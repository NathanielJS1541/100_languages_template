import re


"""
CHALLENGE_URL_REGEX is a compiled regular expression that matches strings of the form "problem=<number>":
  - "^" asserts the start of a line.
  - "problem=" matches the literal string problem=.
  - "(?P<number>\d+)" is a named capturing group to capture one or more digits:
    - "(...)" defines the capture group.
    - "?P<number>" names the capture group "number".
    - "\d" is a shorthand character class to capture digits (0-9).
    - "+" is a greedy quantifier that matches one or more times, and allows the previous character class to capture one or more digits.
"""
CHALLENGE_URL_REGEX = re.compile(r"^problem=(?P<number>\d+)")

"""
RESOURCE_URL_REGEX is a compiled regular expression that matches strings of the form "resources/<filename>" and "project/resources/<filename>:
  - "^" asserts the start of a line.
  - "(project\/)?" is a capture group that matches the optional literal string "project/".
    - "(...)" defines the capture group.
    - "?" makes the capture group optional.
  - "resources\/" matches the literal string "resources/".
  - "(.+\/)?" is an optional capture group to match any characters followed by a "/":
    - "(...)" defines the capture group.
    - "." matches any character (except for a newline).
    - "+" is a greedy quantifier that matches one or more times, and allows the "." to capture one or more digits.
    - "\/" matches the literal "/".
    - "?" makes the capture group optional.
  - "(?P<filename>.+)" is a named capturing group to match any characters:
    - "(...)" defines the capture group.
    - "?P<filename>" names the capture group "filename".
    - "." matches any character (except for a newline).
    - "+" is a greedy quantifier that matches one or more times, and allows the "." to capture one or more digits.
"""
RESOURCE_URL_REGEX = re.compile(r"^(project\/)?resources\/(.+\/)?(?P<filename>.+)")

