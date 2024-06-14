import challenge_fetcher
import challenge_fetcher.arguments

# Get the command-line arguments using argparse.
args = challenge_fetcher.arguments.parse_arguments()

# Ensure the arguments are valid before running the script.
if challenge_fetcher.arguments.validate_arguments(args):
    challenge_range = range(args.start_challenge, args.end_challenge + 1)
else:
    print("Input argument validation failed... Exiting.")
