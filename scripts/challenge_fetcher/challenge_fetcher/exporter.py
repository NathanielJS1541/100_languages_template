import enum


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
