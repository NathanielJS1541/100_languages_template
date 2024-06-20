import argparse
import pathlib

# The challenge numbers on Project Euler start at 1.
LOWERST_CHALLENGE_NUMBER = 1


def parse_arguments() -> argparse.Namespace:
    """parse_arguments: Parse the command-line arguments using argparse.

    Parses the arguments from the command line using argparse, populating any arguments that were not specified with
    the default value if applicable.

    Returns:
        argparse.Namespace: The arguments that were parsed from the command line.
    """

    # Define an argparse ArgumentParser with the expected arguments for the program.
    parser = argparse.ArgumentParser(
        description="A small script to scrape https://projecteuler.net/, and add the selected challenges to this repo as markdown files."
    )

    parser.add_argument(
        "-s",
        "--start",
        dest="start_challenge",
        help="The number of the first challenge to scrape.",
        default=1,
        type=int,
    )
    parser.add_argument(
        "-e",
        "--end",
        dest="end_challenge",
        help="The number of the last challenge to scrape.",
        default=100,
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="The directory in which all output files and folders will be generated.",
        default="../../src/",
        type=pathlib.Path,
    )
    parser.add_argument(
        "-g",
        "--github-workaround",
        dest="github_workaround",
        help="The GitHub MarkDown renderer currently does not display the LaTeX operator \\operatorname or inline LaTeX immediately followed by text correctly. Enabling this flag adds a workaround to allow them to be rendered correctly. See https://github.com/github/markup/issues/1688.",
        action="store_true",
    )

    # Parse the arguments accoring to the parser defined above.
    args = parser.parse_args()

    # Return the argument values from the parser.
    return args


def validate_arguments(args: argparse.Namespace) -> bool:
    """validate_arguments: Validate the arguments from parse_arguments().

    Validates each command-line argument from argparse to ensure that it is valid according to what the program
    expects. It will also print an error message explaining any errors that were found.

    Args:
        args (argparse.Namespace): the argparse.Namespace returned from the parse_arguments() function.

    Returns:
        bool: True if the arguments are valid. False if one or more arguments were invalid.
    """
    arguments_valid = True

    # Resolve the absolute path to the specified output directory.
    args.output_dir = args.output_dir.resolve()

    # Mark the arguments as invalid if the output_dir is a file path, or has a non-existent parent.
    if args.output_dir.is_file():
        arguments_valid &= False
        print(f"Specified output path {args.output_dir} is a file path.")
    elif not args.output_dir.parent.exists():
        arguments_valid &= False
        print(
            f"Specified output path parent directory {args.output_dir.parent} does not exist."
        )

    # Ensure the range is valid (start is less than end), and that start_challenge is greater than 1.
    if args.start_challenge > args.end_challenge:
        arguments_valid &= False
        print(
            f"start_challenge ({args.start_challenge}) must be smaller than end_challenge ({args.end_challenge})!"
        )
    elif args.start_challenge < LOWERST_CHALLENGE_NUMBER:
        arguments_valid &= False
        print(
            f"start_challenge ({args.start_challenge}) cannot be less than {LOWERST_CHALLENGE_NUMBER}!"
        )

    return arguments_valid
