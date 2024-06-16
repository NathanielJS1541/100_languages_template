import pytest
import challenge_fetcher
import challenge_fetcher.challenge
import challenge_fetcher.parser
import challenge_fetcher.scraper


class TestKnownChallenges:
    """A class for testing challenge_fetcher against known / desired outputs."""

    @pytest.fixture
    def known_challenges(self) -> dict[int, challenge_fetcher.challenge.Challenge]:
        """known_challenges Return a dictionary of known Challenge objects, keyed by challenge number.

        The returned challenges are hand-written, and demonstrate the "desired" output of the challenge objects.

        The following Challenges are used:
        - Challenge 1: Sanity check!

        Returns:
            dict[int, challenge_fetcher.challenge.Challenge]: A dictionary of desired Challenge object outputs.
        """

        return {
            # Sanity check...
            1: challenge_fetcher.challenge.Challenge(
                1,
                "https://projecteuler.net/problem=1",
                "Multiples of 3 or 5",
                """If we list all the natural numbers below $10$ that are multiples of $3$ or $5$, we get $3, 5, 6$ and $9$. The sum of these multiples is $23$.\n\nFind the sum of all the multiples of $3$ or $5$ below $1000$.""",
                None,
            ),

    def test_known_challenges(
        self, known_challenges: dict[int, challenge_fetcher.challenge.Challenge]
    ):
        """test_known_challenges Test the challenge_fetcher Challenge output against a list of known Challenge objects.

        For details of which challenges are used and why, see the known_challenges fixture.

        Args:
            known_challenges (dict[int, challenge_fetcher.challenge.Challenge]): The array of known challenge outputs from the known_challenges fixture.
        """

        # Loop through each known challenge to run the challenge_fetcher against it.
        for key, test_data in known_challenges.items():
            # Get the page content from the scraper.
            response = challenge_fetcher.scraper.get_content(key)

            # Ensure a response was returned by the get_content() function.
            assert response is not None

            # Ensure the response was returned successfully.
            assert response.ok is True

            # Parse the contents into a challenge object. Assume the GitHub workaround is being used.
            challenge = challenge_fetcher.parser.parse_contents(key, response, True)

            # Ensure the challenge was generated successfully.
            assert challenge is not None

            # Ensure that the challenge data was returned as expected, explicitly to make debugging easier.
            assert challenge.number == test_data.number
            assert challenge.url == test_data.url
            assert challenge.title == test_data.title
            assert challenge.description == test_data.description
            assert challenge.remote_content == test_data.remote_content

            # Catch-all, just incase new properties are added to the Challenge class.
            assert challenge == test_data
