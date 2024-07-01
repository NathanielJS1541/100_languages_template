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
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible. It allows the previous
    character class to capture one or more characters, but will only allow the group to match up to the first underscore.
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
FILE_NAME_REGEX = re.compile(r"^(?:.+?_)?(?P<filename>.+\..+?)(?:\?.*)?$")

"""
LATEX_WORKAROUND_PATTERN is a compiled regular expression which matches inline LaTeX expressions which are immediately
followed by text:
- "(?<!\$)" is a negative lookbehind that asserts what immediately precedes the current position in the string is not a
  dollar sign. This ensures the regex won't match blocks of LaTeX.
- "\$" matches the literal string "$", which is the beginning of a LaTeX expression.
- (?P<expression>[^$]+?) is a named capturing group that captures the contents of the LaTeX expression:
  - "(...)" defines the capture group.
  - "?P<expression>" names the capture group "expression".
  - "[^$]" is a character class that matches any character except the dollar sign:
    - "[...]" defines the character class.
    - "^" is the negation operator, which inverts the following set of characters.
    - "$" is the literal character "$".
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible. This ensures that only the
    contents of the LaTeX expression are captured.
- "\$" matches the literal string "$", which is the end of a LaTeX expression.
- "(?!\$)" is a negative lookahead that asserts what immediately follows the current position in the string is not a
  dollar sign. This ensures the regex won't match blocks of LaTeX.
- "(?P<text>\w+)" is a named capturing group that captures the text following the LaTeX expression:
  - "(...)" defines the capture group.
  - "?P<text>" names the capture group "text".
  - "\w" is a shorthand character class to capture word characters (a-z, A-Z, 0-9, _).
  - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more characters.
"""
LATEX_WORKAROUND_REGEX = re.compile(r"(?<!\$)\$(?P<expression>[^$]+?)\$(?!\$)(?P<text>\w+)?")

"""
MULTILINE_LATEX_REGEX is a compiled regular expression which matches any multi-line LaTeX expression (starting with
\begin{...} and ending with \end{...}) which are not already enclosed in $$..$$.

This is particularly nasty as the re module only supports fixed-length look-behinds. You're welcome...

- "(?<!\$\$)" is a negative look-behind assertion to make sure that the start of the LaTeX expression is not already
  preceded by a "$$":
  - "(?<!...)" is the syntax for a negative lookbehind assertion in regex.
  - "\$\$" matches the literal string "$$".
- "(?<!\$\$\n)" is a negative look-behind assertion to make sure that the start of the LaTeX expression is not already
  preceded by a "$$\n":
  - "(?<!...)" is the syntax for a negative lookbehind assertion in regex.
  - "\$\$" matches the literal string "$$".
  - "\n" matches a newline character.
- "\\begin\{" matches the literal string "\begin{", which is the start of the multi-line LaTeX expression.
- "(\w+?)" is a non-greedy capture group for one or more word characters, to capture the content within the \begin{...}:
  - "\w" is the shorthand character class that matches any word character (equivelant to [a-zA-Z0-9_]).
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible.
- "\}" matches the literal string "}", which closes the "\begin{...}".
- "((?:.|\n)+?)" is a non-greedy capture group for one or more of any character, or newline:
  - "(...)" is the syntax for a capture group.
  - "(?:.|\n)" is a non-capturing group which matches any character (including newlines):
    - "(?:...)" is the syntax for a non-capturing group.
    - "." matches any character (except for a newline).
    - "|" is the OR operator, which allows matching the pattern before or after it.
    - "\n" matches newlines.
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible.
- "\\end\{" matches the literal string "\end{", which is the start of the last tag in the multi-line LaTeX expression.
- "(\w+?)" is a non-greedy capture group for one or more word characters, to capture the content within the \end{...}:
  - "\w" is the shorthand character class that matches any word character (equivelant to [a-zA-Z0-9_]).
  - "+?" is a lazy quantifier that matches one or more times, but as few times as possible.
- "\}" matches the literal string "}", which closes the "\end{...}".
- "(?!\$\$)" is a negative lookahead assertion to make sure the end of the LaTeX expression is not already followed by
  a "$$":
  - "(?!...)" is the syntax for a negative lookahead assertion in regex.
  - "\$\$" matches the literal string "$$".
- "(?!\n\$\$)" is a negative lookahead assertion to make sure the end of the LaTeX expression is not already followed
  by a "\n$$":
  - "(?!...)" is the syntax for a negative lookahead assertion in regex.
  - "\n" matches a newline character.
  - "\$\$" matches the literal string "$$".
"""
MULTILINE_LATEX_REGEX = re.compile(r"(?<!\$\$)(?<!\$\$\n)\\begin\{(\w+?)\}((?:.|\n)+?)\\end\{(\w+?)\}(?!\$\$)(?!\n\$\$)")

"""
MULTILINE_LATEX_REPLACEMENT_PATTERN is the replacement pattern for use with the MULTILINE_LATEX_REGEX.

This just wraps the original LaTeX expression inside $$...$$, so that it can render in MarkDown.

- "$$\n" is used to wrap the original LaTeX expression in "$$" on the line above for neatness.
- "\\begin{\1}" replaces the first group of the MULTILINE_LATEX_REGEX, which captured the content within the brackets of
  the "\begin{...}".
- "\2" replaces the contents that was captured in the MULTILINE_LATEX_REGEX between the "\begin{...}" and "\end{...}".
- "\\end{\3}" replaces the last group of the MULTILINE_LATEX_REGEX, which captured the content within the brackets of
  the "\end{...}".
- "\n$$" is used to close the LaTeX expression with a "$$" on the line below for neatness.
"""
MULTILINE_LATEX_REPLACEMENT_PATTERN = r"$$\n\\begin{\1}\2\\end{\3}\n$$"

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

    # If there is no page content, raise a ValueError as something has gone terribly wrong...
    if page_content is None:
        raise ValueError(f"Page content <div> was not found.")

    # The title is contained within the "content" div, and is contained within h2.
    title = page_content.find("h2").text

    # The description is contained within a div of the "problem_content" class. This is what we need to (somehow)
    # parse into markdown.
    description = page_content.find("div", class_="problem_content")

    # As above, raise a ValueError in the event that the description tag isn't found. This may indicate that the page
    # layout has changed?
    if description is None:
        raise ValueError(f"Problem description <div> was not found.")

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

        # For challenge links, preserve the original link text.
        link_text = tag.text
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

        # For file and image downloads, ensure the link text or alt text is up to date with the sanitised file name.
        link_text = file_name
    elif about_match:
        # This type of link is a reference to the "about" pages on different topics on the Project Euler website.
        # This content won't be downloaded, and a link to the about page will just be added to the README.

        # The URL from the bs4.Tag will be a relative URL. All we need to do to get a valid URL is add it to the
        # Project Euler base URL.
        url = f"{challenge_fetcher.scraper.URL_BASE}{url}"

        # For "about" links, preserve the original link text.
        link_text = tag.text
    else:
        # Since I don't have the time (or willpower) to download and check every single challenge on the Project
        # Euler website, this error will alert me (or anyone else) to a link type that I haven't come accross yet.
        # If this is raised, inspect the URL and add some more Regex and handling (or open an issue on
        # https://github.com/NathanielJS1541/100_languages_template) :).
        raise NotImplementedError(f"A URL was found to an unknown resource type: {url}")

    # Construct the MarkDown link syntax using the link text and the URL.
    link_text = f"[{link_text}]({url})"

    if is_image:
        # If the link is an image, append an "!" to convert the link syntax to image syntax.
        link_text = "!" + link_text

    # Replace the tag with the MarkDown representation of the new link or image.
    tag.replace_with(link_text)


def latex_regex_repl(match: re.Match[str]) -> str:
    """latex_regex_repl REPL for the GitHub LaTeX workaround re.sub().

    This returns the text that will be used in the substitution based on the capture groups.

    Args:
        match (re.Match[str]): The match from the reegx expression.

    Returns:
        str: The string to replace the matched text.
    """

    # Get the contents of both named capture groups in the LATEX_WORKAROUND_REGEX.
    # Note that the "text" group is optional.
    expression = match.group("expression")
    text = match.group("text")

    # If the optional "text" group was also matched, add it as a text function to the end of the LaTeX expression.
    # Note that all matches of the "expression" group will also call this function. There is no way to avoid returning
    # a replacement string (apart from writing better regex I guess...) so when there is no text group just return the
    # original string.
    if text:
        expression = f"{expression}\\text{{{text}}}"

    # Close the complete expression inside the syntax for a LaTeX inline expression.
    expression = f"${expression}$"

    # Return the expression to use as a replacement.
    return expression


def get_next_sibling_element(element: bs4.PageElement, reverse: bool) -> bs4.PageElement | None:
    """get_next_sibling_element Get the next sibling element of the specified element.

    If the specified element has a sibling in the specified direction, it is returned. Otherwise None is returned.

    Siblings are ignored if they consist of only newlines.

    Args:
        element (bs4.PageElement): The element to look for siblings of.
        reverse (bool): False to look for the NEXT sibling element. True to look for the PREVIOUS sibling element.

    Returns:
        bs4.PageElement | None: The next sibling element in the specified direction, or None.
    """

    # Get the siblings to iterate through based on the specified direction.
    if reverse:
        # In reverse mode, look through the previous siblings of the element.
        siblings = element.previous_siblings
    else:
        # In normal mode, look through the next siblings of the element.
        siblings = element.next_siblings

    # Loop through the list of siblings.
    for sibling in siblings:
        # TODO: Can this strip all whitespace, not just newlines?
        if sibling.text.strip("\n") is not None:
            # If the sibling is not empty after removing newlines, return it.
            return sibling


def format_tag_as_markdown_paragraph(tag: bs4.Tag, markdown: str) -> str:
    """format_tag_as_markdown_paragraph Add the correct spacing around the MarkDown string based on the tag type.

    Different "paragraph" style tags should be handled differently. The formatting is handled here to ensure it is
    consistent.

    Currently this will handle the following tags:
      - <p>
      - <div>
      - <blockquote>
      - <br>

    Args:
        tag (bs4.Tag): The paragraph tag to format the MarkDown string based on.
        markdown (str): The current MarkDown representation of the contents of the tag.

    Returns:
        str: A string with the correct paragraph spacing for the tag type when rendered in MarkDown.
    """

    # TODO: Maybe if this is given the text for the previous element, it can be simplified a lot?

    # Get the next and previous sibling element to the current tag.
    previous_sibling = get_next_sibling_element(tag, reverse=True)
    next_sibling = get_next_sibling_element(tag, reverse=False)

    # This list denotes the "paragraph" style tags, that should ensure there is spacing between this tag and
    # surrounding tags.
    paragraph_tags = ["p", "div", "blockquote"]

    # The prefix and will store the newlines to place efore and after the "markdown" text.
    prefix = ""
    suffix = ""

    # If the tag is a "paragraph" style tag, ensure there are two newlines between it and the next element.
    if tag.name in paragraph_tags:
        # TODO: Maybe this can be simplified if it just checks in one direction?
        if isinstance(previous_sibling, bs4.Tag):
            # If the previous element is a bs4.Tag, it may have added newlines before the current paragraph.
            if previous_sibling.name in paragraph_tags:
                # "Paragraph" style tags will have appended a single newline after them, so add a single newline before
                # this "paragraph".
                prefix = "\n"
            elif previous_sibling.name == "ul":
                # TODO: Can this just be an else?
                # Lists will not have newlines added after them but require spacing, so add it here.
                prefix = "\n\n"
        elif isinstance(previous_sibling, bs4.NavigableString):
            # A NavigableString will not have had newlines added after it, so add two as a prefix.
            prefix = "\n\n"

        if isinstance(next_sibling, bs4.Tag):
            # If the next element is a bs4.Tag, it may add newlines after the current paragraph.
            if next_sibling.name in paragraph_tags:
                # As above, "paragraph" style strings will add a single newline before themselves, so add a single
                # newline after the paragraph.
                suffix = "\n"
            elif next_sibling.name == "ul":
                # TODO: Can this just be an else?
                # Lists will not have newlines added before them but require spacing, so add it here.
                suffix = "\n\n"
        elif isinstance(next_sibling, bs4.NavigableString):
            # A NavigableString will not have had newlines added before it, so add two as a suffix.
            suffix = "\n\n"
    elif tag.name == "br":
        # If the tag is a <br> tag, it should only be able to effect the formatting of any sibling tags, but not tags
        # outside of its parent tag. To ensure this, check whether the next sibling exists.
        if next_sibling is not None:
            # If there is a sibling tag after the <br>, add a newline. Otherwise the <br> is ignored.
            markdown = "\n"

    # Return the original MarkDown text with the newlines in the prefix and suffix applied.
    return f"{prefix}{markdown}{suffix}"


def convert_span_tag_to_markdown(span: bs4.Tag, contents_string: str) -> str:
    """convert_span_tag_to_markdown convert_span_tag_to_markdown Generate the MarkDown-equivelant text for the given span tag.

    Some of the formatting for <span> tags is a little long-winded, so is currently in its own method.

    <span> tags are mostly being used to colour text. The easiest way (that I know of...) to colour output text in
    MarkDown is to use LaTeX.

    Args:
        span (bs4.Tag): The span tag to get the formatted text for.
        contents_string (str): The string representation of the contents of the tag.

    Raises:
        ValueError: If the provided tag is not a span tag, a ValueError is raised.
        NotImplementedError: If the span class is not yet implemented, a NotImplementedError is raised.

    Returns:
        str: The string representation of the span tag and its contents.
    """

    if span.name is not "span":
        # If the provided tag is not a <span> tag, it cannot be processed here so raise an error.
        raise ValueError(f"Span tag was expected but got a {span.name} tag.")

    # IF a span is used to represent a colour, the class stores the colour name.
    # We can assume there is only one class, as the colour name will be checked for validity.

    # Get the classes for the span tag, as it is used to select the behaviour.
    span_classes = span.get("class")

    # If the <span> tag is used to colour text, assume that the first class that is returned will be a colour tag.
    # Check the first class against the standard HTML colours to see if this is the case.
    if span_classes[0] in BASIC_HTML_COLOURS:
        # Generate some LaTeX that will set the text within the tag to the specified colour.
        latex_string = f"\\color{{{span_classes[0]}}}{{{span.text}}}"

        # Additionally, MarkDown-style bold and italic syntax aren't compatable with this LaTeX. If there is a <b>,
        # <strong>, <i>, or <em> tag inside the coloured span, we can add a bit of extra LaTeX to reflect this.
        if span.findChild("b") or span.findChild("strong"):
            # Use \\bf in front of the LaTeX to make it bold and coloured.
            latex_string = "\\bf" + latex_string
        if span.findChild("i") or span.findChild("em"):
            # Use \\it in front of the LaTeX to make it italic and coloured.
            latex_string = "\\it" + latex_string

        # Finally, replace the tag with the complete LaTeX expression so that it can be rendered inline ($..$).
        span_string = f"${{{latex_string}}}$"
    # TODO: tooltip tags are currently processed in get_string_for_tag_type(). Maybe tooltip and tooltiptext tags
    # should both be processed in the same place?
    # elif "tooltip" in span_class:
    #     span_string = f"[{contents_string}]"
    elif "tooltiptext" in span_classes:
        # Format the tooltiptext as a MarkDown link, which uses "##" to ensure the page won't scroll when the tooltip
        # is clicked (whereas a single "#" would navigate to the top of the page).
        span_string = f"(## \"{contents_string}\")"
    else:
        # Create a string list of all the classes.
        classes_list = ", ".join(span_classes)

        # If the tag class is not recognised, raise an error so it can be identified and implemented.
        raise NotImplementedError(f"Unknown usage of a <span> tag. Tag classes: {classes_list}.")

    # Return the MarkDown string representing the <span> tag.
    return span_string


def get_string_for_tag_type(tag: bs4.Tag, contents_strings: list[str]) -> str:
    """get_string_for_tag_type Get a string that represents the tag and its contents, formatted to be MarkDown-compatible.

    Parses the contents_strings for the specified tag and formats them so they are MarkDown-compatible, and render
    similarly to the original content when rendered as MarkDown.

    Args:
        tag (bs4.Tag): The tag to base the formatting on. All contents will be placed within the relevant formatting.
        contents_strings (list[str]): A list of strings representing the elements within the tag.

    Raises:
        NotImplementedError: The HTML tag has not been implemented.

    Returns:
        str: A MarkDown-formatted string which represents the tag and its contents.
    """

    # Get the classes ascosiated with the tag. This is used in multiple places so just get it once.
    tag_classes = tag.get("class")

    # Workaround to get tooltips to render properly.
    # TODO: I hate this, but it works for now.
    if tag_classes and "tooltip" in tag_classes:
        # For tooltip tags, get only the first element to display as the tooltip. The rest will (probably...) be the
        # tooltip text to display on hover.
        contents_string = contents_strings[0]
    else:
        # Some tags just need the complete contents string, so generate that once here.
        contents_string = "".join(contents_strings)

    # Format the contents_strings or contents_string based on tag type.
    if tag.name == "p" or tag.name == "br" or tag.name == "blockquote":
        # For paragraph / break / blockquote tags, ensure there are the correct number of newlines between adjacent
        # elements.
        tag_string = format_tag_as_markdown_paragraph(tag, contents_string)
    elif tag.name == "div":
        # <div> tags should be handled the same as <p> and <blockquote> tags, except in the case
        # where it is the topmost tag containing all the problem content. In this case no newlines
        # should be added.
        if tag_classes and "problem_content" in tag_classes:
            # This is the main tag that contains problem content.
            # No surrounding newlines are needed 
            tag_string = contents_string
        else:
            # For normal <div> tags, ensure the correct number of newlines are placed bewteen adjacent elements.
            tag_string = format_tag_as_markdown_paragraph(tag, contents_string)
    elif tag.name == "i" or tag.name == "em":
        # <i> and <em> tags should be replaced with MarkDown italic syntax.
        tag_string = f"*{contents_string}*"
    elif tag.name == "b" or tag.name == "strong":
        # <b> and <strong> tags should be replaced with MarkDown bold syntax.
        tag_string = f"**{contents_string}**"
    elif tag.name == "sup":
        # <sup> tags preceded by LaTeX can be joined into the LaTeX equation.
        # TODO: This is a horrible bodge.
        # TODO: Everything will go wrong if LaTeX isn't there!
        tag_string = f"^{{{contents_string}}}$"
    elif tag.name == "span":
        # Span tags can be used for either coloured and formatted text, or tooltip text.
        # The handling is a bit long-winded so is in its own function... For now...
        tag_string = convert_span_tag_to_markdown(tag, contents_string)
    elif tag.name == "ul":
        # Remove newlines surrounding unordered lists so the surrounding formatting isn't affected.
        # This ensures the trailing "\n" from the last <li> element is removed.
        tag_string = contents_string.strip("\n")
    elif tag.name == "li":
        # List elements should be separated by a single newline.
        # This will leave a trailing "\n" on the last <li> element in a <ul>.
        tag_string = f"{contents_string}\n"
    else:
        # If a HTML tag type has not been implemented, raise an error so it can be identified and fixed.
        raise NotImplementedError(
            f"{tag.name} tags with nested contents have not been implemented."
        )
    
    # Workaround to get tooltips to render properly.
    # TODO: I hate this, but it works for now.
    if tag_classes and "tooltip" in tag_classes:
        # Join all but the first contents string to form the tooltip text.
        tooltip_text = "".join(contents_strings[1::])
        # Format the tooltip text into MarkDown syntax.
        tag_string = f"[{tag_string}]{tooltip_text}"

    # Return the string that represents the tag and its contents.
    return tag_string


def get_element_as_markdown(element: bs4.PageElement) -> str:
    """get_element_as_markdown Get the specified element and all of its contents as MarkDown-compatible text.

    Recursively traverses the parse tree (ooooh recursive function.... scary!) in order to parse each element that is
    a child of the specified element, and reconstruct the parse tree into MarkDown-compatible text. This includes
    replacing HTML syntax with the equivelant in MarkDown where applicable.

    Args:
        element (bs4.PageElement): The page element to construct the MarkDown text from.

    Raises:
        NotImplementedError: Raised when a HTML element type has not been implemented.

    Returns:
        str: The MarkDown-compatible string representing the element and its children.
    """

    # The action performed on a specified element depends on its instance type.
    if isinstance(element, bs4.NavigableString):
        # If the tag is a NavigableString, it holds no useful formatting information. Simply remove all newlines from
        # the start and end of the text, as the MarkDown formatting will be derived from the tag types of subsequent
        # tags.
        # NavigableStrings can't have any children, so can be parsed directly as text.
        tag_string = element.text.strip("\n")

        # Workaround for enclosing <sup> tags inside adjacent LaTeX.
        # TODO: This is horrible.... Move this into get_tag_and_contents_as_markdown_text()? Maybe
        # that method needs the previous element to be passed in aswell?
        if tag_string.endswith("$"):
            # Get the element next to the current element.
            next_element = get_next_sibling_element(element, False)

            # If the tag is a <sup> tag and the current NavigableString ends with a "$", remove the
            # closing "$" as it will be added when the <sup> tag is parsed.
            # TODO: I really, really hate this...
            if isinstance(next_element, bs4.Tag) and next_element.name == "sup":
                tag_string = tag_string[:-1]
    elif isinstance(element, bs4.Tag):
        # If the element is a tag, it can have children which need to be individually parsed to retain their formatting
        # style.

        # Create a blank list to store the formatted text from the child elements.
        contents_strings = []

        # Get an Iterable for the children of the current tag.
        child_elements = element.children

        # If there are PageElements contained within the current element, they must be processed individually.
        if child_elements is not None:
            # Loop through each of the child elements of the current element.
            for child in child_elements:
                # Append the formatted output from each of the child elements to the list.
                contents_strings.append(get_element_as_markdown(child))

        # Format the string of the child elements, based on the tag type of the current element.
        tag_string = get_string_for_tag_type(element, contents_strings)
    else:
        # If the element is an unknown type, raise an error so it can be identified implemented.
        raise NotImplementedError(
            f"Handling for bs4.{type(element).__name__}s has not been implemented."
        )

    # Return the string that represents the element and its contents.
    return tag_string


def sanitise_tag_text(description: bs4.Tag, github_workarounds: bool) -> str:
    """sanitise_tag_text Sanitise the content of a bs4.Tag, and return it as a string.

    The text content of a bs4.Tag is "sanitised" to ensure that it is compatable with MarkDown. This includes an
    optional workaround for the GitHub MarkDown renderer. The sanitised content is then returned as a string.

    Args:
        description (bs4.Tag): The bs4.Tag containing the challenge description.
        github_workaround (bool): If True, a workaround for the GitHub MarkDown renderer not rendering the LaTeX
        /opcode function will be applied, as well as a workaround for inline LaTeX followed immediately by text not
        rendering correctly on GitHub.

    Returns:
        str: A string that is MarkDown-compatible, which contains the description for the Project Euler challenge.
    """

    # Get the text representation of the description tag. This tag is a <div> with the class "problem_content".
    # The get_tag_and_contents_as_markdown_text() method will recursively parse all tags that are descendents of the
    # "description" tag into MarkDown-compatible text, and return the resulting string.
    description_text = get_element_as_markdown(description)

    # Strip leading and trailing whitespaces to ensure consistent spacing from the title and footnote when it is added
    # to the MarkDown file.
    description_text = description_text.strip()

    # Some LaTeX expressions do not render correctly as the curly braces \{ and \} do not end up with a backslash. It
    # seems like the backslash is interpreted as an escape character. In order to escape the backslash it must be
    # preceeded with another backslash. To ensure this only alters LaTeX syntax, search for specifically the
    # combination "\{" and "\}", and replace them with "\\{" and "\\}" respectively. Including the escape characters
    # for this ends up looking a bit silly; "\\\\{" and "\\\\}".
    # For more information, see the comment on issue #4:
    # https://github.com/NathanielJS1541/100_languages_template/issues/4#issuecomment-2179358966
    description_text = description_text.replace("\\{", "\\\\{").replace("\\}", "\\\\}")

    # Ensure that multi-line LaTeX expressions (between \begin{...} and \end{...}) are being enclosed in $$..$$ tags.
    # This allows them to correctly render when exported to MarkDown.
    description_text = re.sub(MULTILINE_LATEX_REGEX, MULTILINE_LATEX_REPLACEMENT_PATTERN, description_text)

    # If requested, do the GitHub-specific workarounds.
    if github_workarounds:
        # Workaround for GitHub not supporting \operatorname anymore (see https://github.com/github/markup/issues/1688).
        if "\\operatorname" in description_text:
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
            # - "\2" is a backreference to the second capture group in the pattern. This corresponds to the text
            #   captured by "(.+?)" between the "}" and "=" in the original string.
            # - "=" is the literal string =, which ends the replacement.
            replacement = r"\\mathop{\\text{\1}}\2="

            # Use the RegEx pattern and replacement strings to replace \operatorname{...} with \mathop{\text{...}} in
            # the description text.
            description_text = re.sub(pattern, replacement, description_text)
        
        # Workaround for GitHub not properly rendering LaTeX immediately followed by text.
        # See #2 (https://github.com/NathanielJS1541/100_languages_template/issues/2).
        # This just adds any text immediately next to an inline LaTeX expression into the LaTeX.
        description_text = re.sub(LATEX_WORKAROUND_REGEX, latex_regex_repl, description_text)

    return description_text
