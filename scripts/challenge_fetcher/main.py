import challenge_fetcher
import challenge_fetcher.arguments
import challenge_fetcher.exporter
import challenge_fetcher.scraper
import challenge_fetcher.parser

# Get the command-line arguments using argparse.
args = challenge_fetcher.arguments.parse_arguments()

# Ensure the arguments are valid before running the script.
if challenge_fetcher.arguments.validate_arguments(args):
    challenge_range = range(args.start_challenge, args.end_challenge + 1)

    # Work out from the largest challenge number how many digits should be created for the folder name.
    folder_num_digits = len(str(args.end_challenge))

    # Loop through all the challenge numbers in the selected range.
    for challenge_number in challenge_range:
        # Get the HTML response from the ProjectEuler page for the challenge number.
        contents = challenge_fetcher.scraper.get_content(challenge_number)

        # Skip this challenge if the scraper couldn't return the contents.
        if contents is None:
            continue

        # Parse the HTML into a "challenge", containing an URL, project number, title, and description.
        challenge = challenge_fetcher.parser.parse_contents(
            challenge_number, contents, args.github_workaround
        )

        # Export the challenge to a README.md file, and get a status code back.
        status = challenge_fetcher.exporter.export_challenge_readme(
            challenge, args.output_dir, folder_num_digits
        )

        # Parse the status into a human-readable string.
        status_string = challenge_fetcher.exporter.StatusMessages.get(status)

        # Print the export status to the terminal.
        print(f"Saving Challenge {challenge_number}: {status_string}")
else:
    print("Input argument validation failed... Exiting.")
