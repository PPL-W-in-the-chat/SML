import unittest

from backend.lexer import Token, tokenize


class TokenLocationTests(unittest.TestCase):
    def test_tokens_preserve_source_data(self) -> None:
        self.assertEqual(
            tuple(Token.__dataclass_fields__),
            ("type", "lexeme", "line", "column", "value"),
        )

        tokens = tokenize('alpha 5.0\n"x"')
        self.assertEqual(
            tokens[:3],
            [
                Token("ID", "alpha", 1, 1),
                Token("DEC", "5.0", 1, 7, 5.0),
                Token("STR", '"x"', 2, 1, "x"),
            ],
        )

    def test_attached_and_spaced_quantity_parts_have_distinct_positions(self) -> None:
        tokens = tokenize("100m 100 m")
        actual = [
            (token.type, token.lexeme, token.line, token.column)
            for token in tokens
        ]
        self.assertEqual(
            actual,
            [
                ("INT", "100", 1, 1),
                ("ID", "m", 1, 4),
                ("INT", "100", 1, 6),
                ("ID", "m", 1, 10),
                ("EOF", "", 1, 11),
            ],
        )


if __name__ == "__main__":
    unittest.main()
