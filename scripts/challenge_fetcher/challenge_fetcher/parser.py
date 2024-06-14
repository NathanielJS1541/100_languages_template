import re


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

    # Get the text contained in the BeautifulSoup tag.
    description_text = description.text

    # For markdown, a newline is not only represented by a /n, but two spaces followed by a /n. This is to get the same visual effect as a
    # new paragraph in the HTML.
    description_text = description_text.replace("\n", "  \n")

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
