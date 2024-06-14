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
RESOURCE_URL_REGEX = re.compile(r"^(project\/)?(resources|images)\/(.+\/)?(?P<filename>.+)")

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


