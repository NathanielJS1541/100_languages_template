import enum
import re


# Desired name for the desired MarkDown file inside the challenge folder.
README_NAME = "README.md"


class ExportStatus(enum.Enum):
    """ExportStatus An enum containing the status for the MarkDown export operation.

    Args:
        enum (_type_): A status code indicating the success of the MarkDown Export.
    """

    OK = (0,)  # The export was successful.
    ALREADY_EXISTS = (-1,)  # The file already exists.
    OUTPUT_DIR_IS_FILE = (-2,)  # The specified output directory is a file.


# StatusMessages to convert the ExportStatus values to a human-readable string.
StatusMessages = {
    ExportStatus.OK: "OK!",
    ExportStatus.ALREADY_EXISTS: f"{README_NAME} already exists... Skipping!",
    ExportStatus.OUTPUT_DIR_IS_FILE: "Error! The specified output directory is a file.",
}


def generate_padded_number(number: int, total_digits: int) -> str:
    """generate_padded_number Convert a number to a string and pad it to the specified number of digits.

    Args:
        number (int): The number to apply padding to.
        total_digits (int): The number of digits to pad the number to.

    Returns:
        str: The number, padded to total_digits, as a string.
    """

    # Use string.zfill() to pad the number with zeros to the left.
    return str(number).zfill(total_digits)


def generate_folder_name(
    challenge_number: int, challenge_title: str, total_number_digits: int
) -> str:
    """generate_folder_name Generate the folder name for a given challenge.

    Generate a folder name based on the challenge number, title, and a number of padding digits.

    This will pad the number in the name to total_number_digits to ensure they are displayed in order.

    Args:
        challenge_number (int): The challenge number.
        challenge_title (str): The challenge title, which will form the folder name.
        total_number_digits (int): The number of digits to pad the challenge number up to.

    Returns:
        str: A string representing the full folder name.
    """

    # Convert the challenge number to a string, and pad it with the correct number of zeros.
    challenge_number_string = generate_padded_number(
        challenge_number, total_number_digits
    )

    # A character class to match any invalid character:
    # - The character class is defined within the "[]".
    # - "^" negates the character class, meaning it will match any character not in the set.
    # - "A-Za-z0-9 _-" are characters which are defined to be valid for a file path.
    # - "+" means the class will match one or more characters.
    invalid_characters = r"[^A-Za-z0-9 _-]+"

    # Remove all invalid characters in the challenge title.
    folder_title = re.sub(invalid_characters, "", challenge_title)

    # A character class to match any character that I'd rather not include in a path.
    # - The character class is defined within the "[]".
    # - " -" are the characters the character class will match.
    # - "+" means the class will match one or more characters.
    undesirable_characters = r"[ -]+"

    # Replace all spaces and hyphens with underscores for consistency.
    folder_title = re.sub(undesirable_characters, "_", folder_title)

    # Ensure consistent capitalisation across all folders.
    folder_title = folder_title.title()

    # Construct the final folder name from the number string and title.
    return f"{challenge_number_string}_{folder_title}"
