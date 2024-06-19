import requests
import bs4
import challenge_fetcher
import challenge_fetcher.scraper
import challenge_fetcher.challenge
import re


# Basic colour keywords as defined by the CSS3 specification (https://www.w3.org/TR/css-color-3/#valuea-def-color).
BASIC_HTML_COLOURS = [
    "black",
    "silver",
    "gray",
    "white",
    "maroon",
    "red",
    "purple",
    "fuchsia",
    "green",
    "lime",
    "olive",
    "yellow",
    "navy",
    "blue",
    "teal",
    "aqua",
]


"""
CHALLENGE_URL_REGEX is a compiled regular expression that matches strings of the form "problem=<number>":
- "^" asserts the start of a line.
- "problem=" matches the literal string "problem=".
- "(?P<number>\d+)" is a named capturing group to capture one or more digits:
  - "(...)" defines the capture group.
  - "?P<number>" names the capture group "number".
  - "\d" is a shorthand character class to capture digits (0-9).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more digits.
"""
CHALLENGE_URL_REGEX = re.compile(r"^problem=(?P<number>\d+)")

"""
RESOURCE_URL_REGEX is a compiled regular expression that matches strings of the form "resources/<optional_path>/<filename>",
"project/resources/<optional_path>/<filename>", "images/<optional_path>/<filename>", and "project/images/<optional_path>/<filename>":
- "^" asserts the start of a line.
- "(project\/)?" is a capture group that matches the optional literal string "project/".
  - "(...)" defines the capture group.
  - "?" makes the capture group optional.
- "(resources|images)" matches either the literal string "resources" or "images".
  - "(...)" defines the capture group.
  - "resources" matches the literal string "resources".
  - "|" is the OR operator.
  - "images" matches the literal string "images".
- "\/" matches the literal string "/".
- "(.+\/)?" is an optional capture group to match any characters followed by a "/":
  - "(...)" defines the capture group.
  - "." matches any character (except for a newline).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more word characters.
  - "\/" matches the literal "/".
  - "?" makes the capture group optional.
- "(?P<filename>.+)" is a named capturing group to match any characters:
  - "(...)" defines the capture group.
  - "?P<filename>" names the capture group "filename".
  - "." matches any character (except for a newline).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more word characters.
"""
RESOURCE_URL_REGEX = re.compile(
    r"^(project\/)?(resources|images)\/(.+\/)?(?P<filename>.+)"
)

"""
ABOUT_URL_REGEX is a compiled regular expression that matches strings of the form "about=<word>":
- "^" asserts the start of a line.
- "about=" matches the literal string "about=".
- "(\w+)" is a capturing group to capture one or more word characters:
  - "(...)" defines the capture group.
  - "\w" is a shorthand character class to capture word characters (a-z, A-Z, 0-9, _).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more word characters.
"""
ABOUT_URL_REGEX = re.compile(r"^about=(\w+)")

"""
FILE_NAME_REGEX is a compiled regular expression which "sanitises" filenames to remove query strings etc.
- "^" asserts the start of a line.
- "(?:.*_)?" is an optional non-capturing group, which removes the unique ID (i.e. "p096_") from the file name.
  - "(...)" defines the capture group.
  - "?:" denotes that it is a non-capturing group.
  - "." matches any character (except for a newline).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more characters.
  - "_" matches the literal string "_" used to separate the unique ID from the file name.
  - "?" makes the capture group optional.
- "(?P<filename>.*\..+)" is a named capturing group to match the name of the file:
  - "(...)" defines the capture group.
  - "?P<filename>" names the capture group "filename".
  - "." matches any character (except for a newline).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more characters.
  - "\." matches the literal string "." which separates the file name and extension.
  - "." matches any character (except for a newline).
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible. This is needed to ensure
    the following optional capture group is used if possible.
- "(?:\?.*)?" is an optional non-capturing group, which removes any query strings (i.e. "?1678992052") from the file name.
  - "(...)" defines the capture group.
  - "?:" denotes that it is a non-capturing group.
  - "\?" matches the literal string "?", which separates the file name from the query string.
  - "." matches any character (except for a newline).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more characters.
  - "?" makes the capture group optional.
- "$" asserts the end of a line.
"""
FILE_NAME_REGEX = re.compile(r"^(?:.+_)?(?P<filename>.+\..+?)(?:\?.*)?$")


def parse_contents(
    challenge_number: int,
    response: requests.Response,
    github_workaround: bool,
) -> challenge_fetcher.challenge.Challenge | None:
    """parse_contents Parse the contents of the HTTP response.

    Parses the HTML contained in the HTTP response to create a Challenge object. This contains the relevant information
    to generate a README file such as challenge number, challenge URL, challenge title, challenge description, and
    remote content that needs to be downloaded when the README is created.

    Args:
        challenge_number (int): The number of the Project Euler challenge.
        response (requests.Response): The HTTP response from the HTTP GET request.
        github_workaround (bool): If True, a workaround for the GitHub MarkDown renderer not rendering the LaTeX /opcode function will be applied.

    Returns:
        challenge_fetcher.challenge.Challenge | None: A challenge object representing the parsed challenge data, or None if an error was encountered.
    """

    # If the provided HTTP response has an error code, return None.
    if not response.ok:
        return None

    # Parse the HTML response content into a nice soup we can "pythonically" access.
    # html5lib is used as a parser since some of the HTML on https://projecteuler.net/ does not parse properly using
    # Python's html.parser. See #1 (https://github.com/NathanielJS1541/100_languages_template/issues/1) for more info.
    # html5lib seems to generate HTML slower, but much "truer" to what a browser would display.
    soup = bs4.BeautifulSoup(response.content, "html5lib")

    # On all of the pages from https://projecteuler.net/, the actual problem is contained within a div with the id "content".
    # We are not interested in anything else on the page, so grab that.
    page_content = soup.find("div", id="content")

    # If there is no page content, return None.
    if page_content is None:
        print("Page content not found.")
        return None

    # The title is contained within the "content" div, and is contained within h2.
    title = page_content.find("h2").text

    # The description is contained within a div of the "problem_content" class. This is what we need to (somehow)
    # parse into markdown.
    description = page_content.find("div", class_="problem_content")

    # Convert formatting syntax in the HTML to MarkDown syntax. This needs to be done before URLs are converted, to
    # ensure that bold text within a link is maintained. If done after converting the URLs, the fomratting tags will
    # have already been removed.
    convert_text_formatting_to_markdown(description)

    # Convert any URLs embedded in the description to be markdown URLs.
    remote_content = convert_urls_to_markdown(description)

    # Sanitise the description tag content to ensure it can be rendered as MarkDown.
    description_text = sanitise_tag_text(description, github_workaround)

    # Create a new challenge object to return, based on the properties from the page.
    return challenge_fetcher.challenge.Challenge(
        challenge_number,
        response.url,
        title,
        description_text,
        remote_content=remote_content,
    )


def sanitise_file_name(file_name: str) -> str:
    """sanitise_file_name Sanitise the file name of remote content.

    The Project Euler website hosts all resources (such as images and files) in a few central directories, so need
    unique names. When these are downloaded locally, they don't need to have unique names anymore, so this function
    splits off the identifier and keeps the human readable part of the file name. Some file URLs also use a
    query-string, which should be removed from the filename.

    This also strips out any subdirectory names, and takes only the file "stem".

    Args:
        file_name (str): The filename of a remote resource.

    Returns:
        str: The "human readable" part of the filename.
    """

    # Use the compiled regex expression to separate the filename from any additional "fluff".
    filename_match = FILE_NAME_REGEX.search(file_name)

    if not filename_match:
        raise ValueError(
            f"Filename {file_name} could not be parsed using {FILE_NAME_REGEX.pattern}."
        )

    # Return the sanitised filename from the named capture group.
    return filename_match.group("filename")


def convert_text_formatting_to_markdown(content: bs4.Tag) -> None:
    """convert_text_formatting_to_markdown Replace formatting tags with MarkDown syntax.

    Currently supported formatting styles:
    - Italic <i> tags.
    - Bold <b> tags.
    - Span <span> tags used to colour text.

    Args:
        content (bs4.Tag): The bs4 content to replace formatting tags in.

    Raises:
        NotImplementedError: A tag type was found that hasn't been implemented.
    """

    # Loop through all formatting tags in the content.
    # Spans must be done first as they MAY need to replace some of the <b> and <i> tags if they are present!
    for tag in content.find_all(["span", "i", "b"]):
        if tag.name == "span":
            # <span> tags are used to colour text. The easiest way (that I know of...) to colour output text in
            # MarkDown is to use LaTeX.

            # IF a span is used to represent a colour, the class stores the colour name.
            # We can assume there is only one class, as the colour name will be checked for validity.
            colour = tag.get("class")[0]

            # Check that the colour is one of the standard HTML colours.
            if colour not in BASIC_HTML_COLOURS:
                # If it's not, it is probably a span used for something else (like a tooltip). Play it safe and leave
                # the span alone in this case!
                continue

            # Generate some LaTeX that will set the text within the tag to the specified colour.
            coloured_latex = f"\\color{{{colour}}}{{{tag.text}}}"

            # Additionally, MarkDown-style bold and italic syntax aren't compatable with this LaTeX. If there is a <b>
            # or <i> tag inside the coloured span, we can add a bit of extra LaTeX to reflect this.
            if tag.findChild("b"):
                # Use \\bf in front of the LaTeX to make it bold and coloured.
                coloured_latex = "\\bf" + coloured_latex
            if tag.findChild("i"):
                # Use \\it in front of the LaTeX to make it italic and coloured.
                coloured_latex = "\\it" + coloured_latex

            # Finally, replace the tag with the complete LaTeX expression so that it can be rendered inline ($..$).
            tag.replace_with(f"${{{coloured_latex}}}$")
        elif tag.name == "i":
            # <i> tags should be replaced with MarkDown italic syntax.
            tag.replace_with(f"*{tag.text}*")
        elif tag.name == "b":
            # <b> tags should be replaced with MarkDown bold syntax.
            tag.replace_with(f"**{tag.text}**")
        else:
            # If a tag type has not been implemented, throw an error.
            # This should never happen, unless content.find_all(["span", "i", "b"]) is updated...
            raise NotImplementedError(f'"{tag.name}" tags have not been implemented.')


def convert_urls_to_markdown(content: bs4.Tag) -> dict[str, str] | None:
    """convert_urls_to_markdown Convert all URLs in the bs4.Tag to MarkDown links.

    This replaces any <a href=""> tags with the equivelant MarkDown syntax, and additionally corrects those URLs
    based on the type of URL:
      - Links to other challenges are corrected to the full URL to the challenge page on the Project Euler website.
      - Links to remote content are corrected to a link to a file locally, and the file URL is recorded for download.
      - Links to the Project Euler about pages (https://projecteuler.net/about) are updated to full URLs.

    Args:
        content (bs4.Tag): The bs4.Tag containing the challenge descrioption.

    Raises:
        KeyError: Multiple resource files with the same name were found on the page.
        NotImplementedError: An undefined resource type was found on the page.
        NotImplementedError: A tag type was found that has not yet been implemented.

    Returns:
        dict[str, str] | None: A dictionary containing resource URLs keyed by file name to download, or None if no remote content is needed.
    """

    # Create an empty dictionary to store remote content filenames and URLs.
    remote_content = {}

    # Loop through all "a" and "img" tags in the content.
    for tag in content.find_all(["a", "img"]):
        # Initialise to False so that only the img tag detection needs to set it to True.
        is_image = False

        # Get the URL from the tag.
        if tag.name == "a":
            # Resources are stored in anchor tags; the URL is stored in the "href" attribute.
            url = tag.get("href")
        elif tag.name == "img":
            # Images are stored in image tags... (duh...); the URL is stored in the "src" attribute.
            url = tag.get("src")

            # Indicate that the resource to download is an image, as the MarkDown tag needs to be altered.
            is_image = True
        else:
            # If a tag type has not been implemented, throw an error as the attribute to retreive the URL from has not
            # been defined.
            # This should never happen, unless content.find_all(["a", "img"]) is updated...
            raise NotImplementedError(f'"{tag.name}" tags have not been implemented.')

        # Replace the tag with a markdown representation of the link.
        # Also update the remote_content dictionary with any content that needs to be downloaded locally.
        # The is_image indication is needed, since images in MarkDown need a "!"  in front to render them.
        replace_tag_with_markdown_url(tag, url, remote_content, is_image)

    if not remote_content:
        # If no remote content was found, return None.
        return None
    else:
        # If there is remote content, return the dictionary storing it.
        return remote_content


def replace_tag_with_markdown_url(
    tag: bs4.Tag, url: str, remote_content: dict[str, str], is_image: bool
) -> None:
    """replace_tag_with_markdown_url Replace a bs4.Tag with the equivelant MarkDown representation.

    Depending on the URL type, the remote_content dictionary may be updated to include content that needs to be
    downloaded to the specified filename (key) in order for the MarkDown link to work.

    Args:
        tag (bs4.Tag): The tag to replace with MarkDown.
        url (str): The string URL contained within the tag.
        remote_content (dict[str, str]): A dictionary containing the desired filename and URL to the remote content that needs to be downloaded.
        is_image (bool): Indicates that the resource is an image, so the appropriate MarkDown syntax is used.

    Raises:
        KeyError: Multiple resource files with the same name were found on the page.
        NotImplementedError: An undefined resource type was found on the page.
    """

    # Run compiled Regex expressions against the url to determine the type of content.
    # Links to another challenge.
    challenge_match = CHALLENGE_URL_REGEX.search(url)
    # Links to resources such as images and files.
    resource_match = RESOURCE_URL_REGEX.search(url)
    # Links to the Project Euler "about" pages (https://projecteuler.net/about).
    about_match = ABOUT_URL_REGEX.search(url)

    if challenge_match:
        # This type of link is a reference to another challenge.

        # TODO: If problem is going to be downloaded, link it locally.

        # Get the linked challenge number from the named capture group.
        challenge_number = challenge_match.group("number")

        # Construct a URL to the remote challenge page.
        url = f"{challenge_fetcher.scraper.CHALLENGE_URL_BASE}{challenge_number}"
    elif resource_match:
        # This type of link is a reference to a resource such as an image or file. We will download these
        # locally so they can committed to the repo and linked locally in the README.

        # Get the linked file name from the Regex expression's named capture group.
        file_name = sanitise_file_name(resource_match.group("filename"))

        # Construct a URL for the remote content based on the base URL, and the complete URL that the Regex
        # matched.
        remote_url = challenge_fetcher.scraper.URL_BASE + url

        # Swap the "URL" to a local reference to the file_name, so the README will link to the local file once it
        # has been downloaded.
        url = f"./{file_name}"

        # For now, I'm assuming that each page will contain all uniquely named files. This will raise an error
        # if this assumption is incorrect, so I can fix it later :).
        if file_name in remote_content:
            raise KeyError(f"Multiple resources found with the name {file_name}")

        # Add the remote URL to the remote_content dictionary, keyed by the file_name that the resource needs to be
        # downloaded to.
        remote_content[file_name] = remote_url
    elif about_match:
        # This type of link is a reference to the "about" pages on different topics on the Project Euler website.
        # This content won't be downloaded, and a link to the about page will just be added to the README.

        # The URL from the bs4.Tag will be a relative URL. All we need to do to get a valid URL is add it to the
        # Project Euler base URL.
        url = f"{challenge_fetcher.scraper.URL_BASE}{url}"
    else:
        # Since I don't have the time (or willpower) to download and check every single challenge on the Project
        # Euler website, this error will alert me (or anyone else) to a link type that I haven't come accross yet.
        # If this is raised, inspect the URL and add some more Regex and handling (or open an issue on
        # https://github.com/NathanielJS1541/100_languages_template) :).
        raise NotImplementedError(f"A URL was found to an unknown resource type: {url}")

    # Construct the MarkDown link syntax using the filename as the link text (or alt text for images), and the URL.
    link_text = f"[{file_name}]({url})"

    if is_image:
        # If the link is an image, append an "!" to convert the link syntax to image syntax.
        link_text = "!" + link_text

    # Replace the tag with the MarkDown representation of the new link or image.
    tag.replace_with(link_text)


def sanitise_tag_text(description: bs4.Tag, github_workaround: bool) -> str:
    """sanitise_tag_text Sanitise the content of a bs4.Tag, and return it as a string.

    The text content of a bs4.Tag is "sanitised" to ensure that it is compatable with MarkDown. This includes an
    optional workaround for the GitHub MarkDown renderer. The sanitised content is then returned as a string.

    Args:
        description (bs4.Tag): The bs4.Tag containing the challenge description.
        github_workaround (bool): If True, a workaround for the GitHub MarkDown renderer not rendering the LaTeX /opcode function will be applied.

    Returns:
        str: A string that is MarkDown-compatible, which contains the description for the Project Euler challenge.
    """

    # Start with a blank string. This will be used to construct the string.
    description_text = ""

    # For markdown, a newline does not add spacing between paragraphs. For this, two newlines are required instead.
    # Loop through each type of element that may represent a "paragraph".
    for element in description.find_all(["p", "div", "ul"]):
        # Add the text for the current element:
        # - separator="" is used as elements are to be concatonated directly together.
        # - strip=False as it would also remove spaces which we don't want.
        # - .strip("\n") so we can strip newlines out without altering other whitespace characters.
        description_text += element.get_text(separator="", strip=False).strip("\n")

        # At the end of each "paragraph", add the two newlines required to add spacing in the MarkDown output.
        description_text += "\n\n"

    # Strip leading and trailing whitespaces (in this case, newlines added after the last element).
    description_text = description_text.strip()

    # Replace any non-breaking spaces from the text with normal spaces. In MarkDown, the non-breaking spaces render
    # weirdly so should be removed.
    description_text = description_text.replace("\xa0", " ")

    # Some LaTeX expressions do not render correctly as the curly braces \{ and \} do not end up with a backslash. It
    # seems like the backslash is interpreted as an escape character. In order to escape the backslash it must be
    # preceeded with another backslash. To ensure this only alters LaTeX syntax, search for specifically the
    # combination "\{" and "\}", and replace them with "\\{" and "\\}" respectively. Including the escape characters
    # for this ends up looking a bit silly; "\\\\{" and "\\\\}".
    # For more information, see the comment on issue #4:
    # https://github.com/NathanielJS1541/100_languages_template/issues/4#issuecomment-2179358966
    description_text = description_text.replace("\\{", "\\\\{").replace("\\}", "\\\\}")

    # Workaround for GitHub not supporting \operatorname anymore (see https://github.com/github/markup/issues/1688).
    if github_workaround and "\\operatorname" in description_text:
        # RegEx pattern to replace the occurrances of \operatorname in the description:
        # - "\\operatorname\{" matches the literal string \operatorname{ (with escape character for the \ and {).
        # - "(.+?)" creates a capture group which matches the following:
        #   - "." matches any character.
        #   - "+" quantifier meaning that the previous "." can match one or more times.
        #   - "?" makes the "+" quantifier lazy. It will try and match as few characters as possible while still
        #     matching the next "}".
        # - "\}" matches the literal string }.
        # - "(.+?)" creates another capture group, as above.
        # - "=" matches the literal string = at the end of the expression.
        pattern = r"\\operatorname\{(.+?)\}(.+?)="

        # Replacement expression to define how the capture groups are included in the replaced text:
        # - "\\mathop{\\text{" is the literal string that will replace \operatorname{ with \mathop{\text{.
        # - "\1" is a backreference to the first capture group in the pattern. This corresponds to text captured by
        #   "(.+?)" inside the \\operatorname{...} in the original string.
        # - "}}" is the literal string which will close the \text{} and \mathop{} LaTeX commands.
        # - "\2" is a backreference to the second capture group in the pattern. This corresponds to the text captured
        #   by "(.+?)" between the "}" and "=" in the original string.
        # - "=" is the literal string =, which ends the replacement.
        replacement = r"\\mathop{\\text{\1}}\2="

        # Use the RegEx pattern and replacement strings to replace \operatorname{...} with \mathop{\text{...}} in the
        # description text.
        description_text = re.sub(pattern, replacement, description_text)

    return description_text
