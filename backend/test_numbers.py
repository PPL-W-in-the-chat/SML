import unittest

from backend.lexer import tokenize


class NumberTokenTests(unittest.TestCase):
    def test_numeric_forms_are_preserved_for_the_parser(self) -> None:
        tokens = tokenize("007 5. .5 5.0 007.5")
        actual = [(token.lexeme, token.type, token.value) for token in tokens]
        self.assertEqual(
            actual,
            [
                ("007", "INT", 7),
                ("5", "INT", 5),
                (".", "DOT", None),
                (".", "DOT", None),
                ("5", "INT", 5),
                ("5.0", "DEC", 5.0),
                ("007.5", "DEC", 7.5),
                ("", "EOF", None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
