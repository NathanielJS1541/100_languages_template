import pytest
import challenge_fetcher
import challenge_fetcher.parser


class TestFileNameSanitiser:
    """A class to test the filename sanitisation logic."""

    @pytest.fixture
    def known_file_names(self) -> dict[str, str]:
        """known_file_names Return the known filename sanitisations as a dictionary.

        The dictionary contains the raw filename as the key, and the sanitised filename as the value.

        Returns:
            dict[str, str]: A dictionary of known filenames, with the keys as the raw filename and the value as the
                            desired "sanitised" filename.
        """

        return {
            # From Challenge 15 (https://projecteuler.net/problem=15).
            "0015.png?1678992052": "0015.png",
            # From Challenge 22 (https://projecteuler.net/problem=22).
            "0022_names.txt": "names.txt",
            # From Challenge 42 (https://projecteuler.net/problem=42).
            "0042_words.txt": "words.txt",
            # From Challenge 68 (https://projecteuler.net/problem=68).
            "0068_1.png?1678992052": "1.png",
            "0068_2.png?1678992052": "2.png",
            # From Challenge 84 (https://projecteuler.net/problem=84).
            "0084_monopoly_board.png?1678992052": "monopoly_board.png",
            # From Challenge 96 (https://projecteuler.net/problem=96).
            "p096_1.png": "1.png",
            "p096_2.png": "2.png",
            "p096_sudoku.txt": "sudoku.txt",
            # From Challenge 99 (https://projecteuler.net/problem=99).
            "0099_base_exp.txt": "base_exp.txt",
        }

    def test_known_file_names(self, known_file_names: dict[str, str]) -> None:
        """test_known_file_names Test the sanitise_file_name() method of the challenge_fetcher.parser.

        Args:
            known_file_names (dict[str, str]): A dictionary of file names. The key is the raw filename and the value is
                                               the desired "sanitised" filename.
        """

        # Loop through each entry in the dictionary.
        for raw_name, sanitised_name in known_file_names.items():
            # Compare the output of sanitise_file_name() with the desired output.
            assert (
                challenge_fetcher.parser.sanitise_file_name(raw_name) == sanitised_name
            )
