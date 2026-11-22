import unittest

from backend.lexer import tokenize


class QuantityComponentTokenTests(unittest.TestCase):
    def test_simple_quantity_is_not_assembled_by_the_lexer(self) -> None:
        actual = [
            (token.lexeme, token.type, token.line, token.column)
            for token in tokenize("100m")
        ]
        self.assertEqual(
            actual,
            [
                ("100", "INT", 1, 1),
                ("m", "ID", 1, 4),
                ("", "EOF", 1, 5),
            ],
        )

    def test_compound_quantity_is_an_ordinary_token_sequence(self) -> None:
        actual = [token.type for token in tokenize("9.8[m/s^2]")]
        self.assertEqual(
            actual,
            ["DEC", "BRK_L", "ID", "AR_DIV", "ID", "AR_POW", "INT", "BRK_R", "EOF"],
        )

    def test_malformed_unit_syntax_is_preserved_for_the_parser(self) -> None:
        tokens = tokenize("1[kg/m/s^2]")
        self.assertEqual(
            [token.type for token in tokens],
            [
                "INT", "BRK_L", "ID", "AR_DIV", "ID", "AR_DIV",
                "ID", "AR_POW", "INT", "BRK_R", "EOF",
            ],
        )
        self.assertFalse(any(token.type == "ERR" for token in tokens))


if __name__ == "__main__":
    unittest.main()
