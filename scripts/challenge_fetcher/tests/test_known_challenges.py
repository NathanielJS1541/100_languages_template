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
        - Challenge 5: Tests replacement of tooltips.
        - Challenge 7: Tests fixing of inline LaTeX followed immediately by text.
        - Challenge 11: Tests <b> tag and colour replacement in text.
        - Challenge 14: Tests <b> tag detection and replacement.
        - Challenge 39: Test fix for LaTeX containing curly braces {}.
        - Challenge 96: Tests identification of required remote content downloads, and that the references within the
          page have been replaced with MarkDown-style links. Also tests replacement of <i> tags with MarkDown syntax.

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
            # Test replacement of tooltips.
            5: challenge_fetcher.challenge.Challenge(
                5,
                "https://projecteuler.net/problem=5",
                "Smallest Multiple",
                """$2520$ is the smallest number that can be divided by each of the numbers from $1$ to $10$ without any remainder.\n\nWhat is the smallest positive number that is [**evenly divisible**](## "divisible with no remainder") by all of the numbers from $1$ to $20$?""",
                None,
            ),
            # Test inline LaTeX followed immediately by text.
            7: challenge_fetcher.challenge.Challenge(
                7,
                "https://projecteuler.net/problem=7",
                "10001st Prime",
                """By listing the first six prime numbers: $2, 3, 5, 7, 11$, and $13$, we can see that the $6\\text{th}$ prime is $13$.\n\nWhat is the $10\,001\\text{st}$ prime number?""",
                None,
            ),
            # Test <b> tags and colours replacement.
            11: challenge_fetcher.challenge.Challenge(
                11,
                "https://projecteuler.net/problem=11",
                "Largest Product in a Grid",
                """In the $20 \\times 20$ grid below, four numbers along a diagonal line have been marked in red.\n\n08 02 22 97 38 15 00 40 00 75 04 05 07 78 52 12 50 77 91 08  \n49 49 99 40 17 81 18 57 60 87 17 40 98 43 69 48 04 56 62 00  \n81 49 31 73 55 79 14 29 93 71 40 67 53 88 30 03 49 13 36 65  \n52 70 95 23 04 60 11 42 69 24 68 56 01 32 56 71 37 02 36 91  \n22 31 16 71 51 67 63 89 41 92 36 54 22 40 40 28 66 33 13 80  \n24 47 32 60 99 03 45 02 44 75 33 53 78 36 84 20 35 17 12 50  \n32 98 81 28 64 23 67 10 ${\\bf\color{red}26}$ 38 40 67 59 54 70 66 18 38 64 70  \n67 26 20 68 02 62 12 20 95 ${\\bf\color{red}63}$ 94 39 63 08 40 91 66 49 94 21  \n24 55 58 05 66 73 99 26 97 17 ${\\bf\color{red}78}$ 78 96 83 14 88 34 89 63 72  \n21 36 23 09 75 00 76 44 20 45 35 ${\\bf\color{red}14}$ 00 61 33 97 34 31 33 95  \n78 17 53 28 22 75 31 67 15 94 03 80 04 62 16 14 09 53 56 92  \n16 39 05 42 96 35 31 47 55 58 88 24 00 17 54 24 36 29 85 57  \n86 56 00 48 35 71 89 07 05 44 44 37 44 60 21 58 51 54 17 58  \n19 80 81 68 05 94 47 69 28 73 92 13 86 52 17 77 04 89 55 40  \n04 52 08 83 97 35 99 16 07 97 57 32 16 26 26 79 33 27 98 66  \n88 36 68 87 57 62 20 72 03 46 33 67 46 55 12 32 63 93 53 69  \n04 42 16 73 38 25 39 11 24 94 72 18 08 46 29 32 40 62 76 36  \n20 69 36 41 72 30 23 88 34 62 99 69 82 67 59 85 74 04 36 16  \n20 73 35 29 78 31 90 01 74 31 49 71 48 86 81 16 23 57 05 54  \n01 70 54 71 83 51 54 69 16 92 33 48 61 43 52 01 89 19 67 48  \n\nThe product of these numbers is $26 \\times 63 \\times 78 \\times 14 = 1788696$.\n\nWhat is the greatest product of four adjacent numbers in the same direction (up, down, left, right, or diagonally) in the $20 \\times 20$ grid?""",
                None,
            ),
            # Test <b> tag detection and replacement.
            14: challenge_fetcher.challenge.Challenge(
                14,
                "https://projecteuler.net/problem=14",
                "Longest Collatz Sequence",
                """The following iterative sequence is defined for the set of positive integers:\n\n$n \\to n/2$ ($n$ is even)\n\n$n \\to 3n + 1$ ($n$ is odd)\n\nUsing the rule above and starting with $13$, we generate the following sequence:\n\n$$13 \\to 40 \\to 20 \\to 10 \\to 5 \\to 16 \\to 8 \\to 4 \\to 2 \\to 1.$$\n\nIt can be seen that this sequence (starting at $13$ and finishing at $1$) contains $10$ terms. Although it has not been proved yet (Collatz Problem), it is thought that all starting numbers finish at $1$.\n\nWhich starting number, under one million, produces the longest chain?\n\n**NOTE:** Once the chain starts the terms are allowed to go above one million.""",
                None,
            ),
            # Test LaTeX containing curly braces {}.
            39: challenge_fetcher.challenge.Challenge(
                39,
                "https://projecteuler.net/problem=39",
                "Integer Right Triangles",
                """If $p$ is the perimeter of a right angle triangle with integral length sides, $\\\{a, b, c\\\}$, there are exactly three solutions for $p = 120$.\n\n$\\\{20,48,52\\\}$, $\\\{24,45,51\\\}$, $\\\{30,40,50\\\}$\n\nFor which value of $p \le 1000$, is the number of solutions maximised?""",
                None,
            ),
            # Test <img>, <a hrf>, and <i> tag detection and replacement.
            96: challenge_fetcher.challenge.Challenge(
                96,
                "https://projecteuler.net/problem=96",
                "Su Doku",
                """Su Doku (Japanese meaning *number place*) is the name given to a popular puzzle concept. Its origin is unclear, but credit must be attributed to Leonhard Euler who invented a similar, and much more difficult, puzzle idea called Latin Squares. The objective of Su Doku puzzles, however, is to replace the blanks (or zeros) in a 9 by 9 grid in such that each row, column, and 3 by 3 box contains each of the digits 1 to 9. Below is an example of a typical starting puzzle grid and its solution grid.\n\n![1.png](./1.png)     ![2.png](./2.png)\n\nA well constructed Su Doku puzzle has a unique solution and can be solved by logic, although it may be necessary to employ "guess and test" methods in order to eliminate options (there is much contested opinion over this). The complexity of the search determines the difficulty of the puzzle; the example above is considered *easy* because it can be solved by straight forward direct deduction.\n\nThe 6K text file, [sudoku.txt](./sudoku.txt) (right click and 'Save Link/Target As...'), contains fifty different Su Doku puzzles ranging in difficulty, but all with unique solutions (the first puzzle in the file is the example above).\n\nBy solving all fifty puzzles find the sum of the 3-digit numbers found in the top left corner of each solution grid; for example, 483 is the 3-digit number found in the top left corner of the solution grid above.""",
                {
                    "1.png": "https://projecteuler.net/project/images/p096_1.png",
                    "2.png": "https://projecteuler.net/project/images/p096_2.png",
                    "sudoku.txt": "https://projecteuler.net/project/resources/p096_sudoku.txt",
                },
            ),
        }

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
