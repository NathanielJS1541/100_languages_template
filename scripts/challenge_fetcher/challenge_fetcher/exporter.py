import pathlib
import challenge_fetcher.challenge
import enum
import re
import requests


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


def export_challenge_readme(
    challenge: challenge_fetcher.challenge.Challenge,
    output_path: pathlib.Path,
    folder_num_digits: int,
) -> ExportStatus:
    """export_challenge_readme Export the README.md file for the given challenge.

    Create a folder for the current challenge, and export the README.md file for the challenge along with any
    required resources to the folder.

    Args:
        challenge (challenge_fetcher.challenge.Challenge): The Challenge object to export.
        output_path (pathlib.Path): The output path for the export. This should be the same for all challenges.
        folder_num_digits (int): The number of digits to pad the challenge number in the folder name to.

    Returns:
        ExportStatus: The status for the export operation.
    """

    # Ensure the specified output directory is not a file path.
    if output_path.is_file():
        return ExportStatus.OUTPUT_DIR_IS_FILE

    # Ensure the output path is completely resolved.
    output_path = output_path.resolve()

    # Create the output directory. This will raise an error if the output directory does not have existing parents. If
    # the file already exists, no error is raised. This will raise an error if it is not a directory (which should
    # never happen as this is checked above).
    output_path.mkdir(exist_ok=True)

    # Get the path to the output folder for the current challenge.
    folder_path = generate_folder_path(challenge, folder_num_digits, output_path)

    # Create the folder for the current challenge, ignoring errors if it already exists.
    folder_path.mkdir(exist_ok=True)

    # Generate the full path for the README file.
    readme_path = folder_path.joinpath(README_NAME)

    if readme_path.exists():
        # If the README file already exists, skip it and report a warning.
        status = ExportStatus.ALREADY_EXISTS
    else:
        # If the README does not exist, create it and write the challenge description to it.
        status = ExportStatus.OK

        # Open the file for writing.
        with open(readme_path, "w") as readme:
            # Write the title to the file.
            readme.write(
                f"# Problem {generate_padded_number(challenge.number, folder_num_digits)}: {challenge.title}\n"
            )

            # Write the entire description to the README.
            readme.write(f"{challenge.description}\n")

            # At the end of the README, add the link to the original challenge page.
            readme.write(
                f"*For the original page, see [{challenge.url}]({challenge.url}).*\n"
            )

        # Download additional remote content that should already be linked in the README.
        # TODO: Error reporting for external content downloads.
        download_remote_content(folder_path, challenge.remote_content)

    # Return the export status.
    return status


def download_remote_content(
    output_dir: pathlib.Path, remote_content: dict[str, str] | None
) -> None:
    """download_remote_content Download the remote content for a challenge to the specified directory.

    Args:
        output_dir (pathlib.Path): The output directory that the content will be saved under.
        remote_content (dict[str, str] | None): A dict containing the remote content to download, or None.
    """

    # If there is no content to download, return.
    if remote_content is None:
        return

    # Loop through every item in the dictionary.
    for file_name, remote_url in remote_content.items():
        # Create the output path from the output directory and the file name.
        output_path = output_dir.joinpath(file_name)

        # Skip re-downloading files.
        if output_path.exists():
            # TODO: Hash check to ensure the file content is the same?
            # TODO: Error reporting?
            continue

        # Get the response from the download URL.
        response = requests.get(remote_url)

        # TODO: error handling.
        # Write to the output file if the request was successful.
        if response.ok:
            # Write the response content as binary to the output file.
            with open(output_path, "wb") as local_content:
                local_content.write(response.content)


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


def generate_folder_path(
    challenge: challenge_fetcher.challenge.Challenge,
    total_number_digits: int,
    output_path: pathlib.Path,
) -> pathlib.Path:
    """generate_folder_path Generate a folder path from a challenge, number of digits, and output path.

    The folder path will be a child of the specified output_path. It will be named based on the challenge number
    (padded to the number of digits specified by total_number_digits) and the challenge title.

    Args:
        challenge (challenge_fetcher.challenge.Challenge): The Challenge to generate a folder for.
        total_number_digits (int): The number of digits to pad the challenge number in the folder name to.
        output_path (pathlib.Path): The path that the folder will be created in.

    Returns:
        pathlib.Path: A path to a folder named for the specified Challenge.
    """

    # Create a new path based on the output path, challenge number, and challenge title.
    return output_path.joinpath(
        generate_folder_name(challenge.number, challenge.title, total_number_digits)
    )
