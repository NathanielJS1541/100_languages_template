import challenge_fetcher
import challenge_fetcher.arguments
import challenge_fetcher.scraper

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
else:
    print("Input argument validation failed... Exiting.")
