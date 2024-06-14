import requests

# The base Project Euler URL.
URL_BASE = "https://projecteuler.net/"

# The URL base for all challenges. Go to a specific challenge by appending the challenge number.
CHALLENGE_URL_BASE = f"{URL_BASE}problem="


def get_content(challenge_number: int) -> requests.Response | None:
    """get_content Get the content of the webpage of the specified Project Euler challenge.

    Generates the challenge URL based on the challenge number, and then uses the requests library to send a HTTP GET
    request to receive the HTML content for the challenge web page. This will handle any errors by printing an error
    message and returning None.

    Args:
        challenge_number (int): The number of the Project Euler challenge to get the page content for.

    Returns:
        requests.Response | None: The HTTP GET response for the specified Project Euler challenge, or None if an error occured.
    """

    # Send a GET request for the specified challenge URL using the requests library.
    contents = requests.get(get_challenge_url(challenge_number))

    if contents.ok:
        # Return the HTTP GET response if the response code is ok.
        return contents
    else:
        # If an error occured, print the status code and return none.
        print(f"HTTP GET request returned code: {contents.status_code}")
        return None


def get_challenge_url(challenge_number: int) -> str:
    """Get the URL for a specific Project Euler challenge.

    Args:
        challenge_number (int): The number of the challenge to get the URL for.

    Returns:
        str: A string representing the requested challenge URL.
    """
    return f"{CHALLENGE_URL_BASE}{challenge_number}"
