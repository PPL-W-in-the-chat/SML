import unittest
from pathlib import Path

from backend.lexer import tokenize


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPOSITORY_ROOT / "examples"


class DemoExampleTests(unittest.TestCase):
    def test_valid_examples_have_no_lexical_errors(self) -> None:
        for example in sorted(EXAMPLES.glob("valid_*.sml")):
            with self.subTest(example=example.name):
                source = example.read_text(encoding="utf-8")
                errors = [token for token in tokenize(source) if token.type == "ERR"]
                self.assertEqual(errors, [])

    def test_invalid_example_has_only_character_set_errors(self) -> None:
        source = (EXAMPLES / "invalid_lexical_errors.sml").read_text(
            encoding="utf-8"
        )
        errors = [token for token in tokenize(source) if token.type == "ERR"]
        self.assertEqual([token.lexeme for token in errors], ["@", "\\"])

    def test_invalid_example_preserves_parser_ready_sequence(self) -> None:
        source = (EXAMPLES / "invalid_lexical_errors.sml").read_text(
            encoding="utf-8"
        )
        unterminated_comment = source[source.index("/*"):]
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(
            actual,
            [
                ("let", "KW_LET"),
                ("leadingZero", "ID"),
                ("=", "ASG"),
                ("007", "INT"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("trailingDot", "ID"),
                ("=", "ASG"),
                ("5", "INT"),
                (".", "DOT"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("_", "UND"),
                ("hidden", "ID"),
                ("=", "ASG"),
                ("1", "INT"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("badUnit", "ID"),
                ("=", "ASG"),
                ("1", "INT"),
                ("[", "BRK_L"),
                ("kg", "ID"),
                ("/", "AR_DIV"),
                ("m", "ID"),
                ("/", "AR_DIV"),
                ("s", "ID"),
                ("^", "AR_POW"),
                ("2", "INT"),
                ("]", "BRK_R"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("loneAnd", "ID"),
                ("=", "ASG"),
                ("true", "BOL_T"),
                ("&", "AMP"),
                ("false", "BOL_F"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("unknownCharacter", "ID"),
                ("=", "ASG"),
                ("2", "INT"),
                ("@", "ERR"),
                ("kg", "ID"),
                (";", "SEM"),
                ("let", "KW_LET"),
                ("escapedString", "ID"),
                ("=", "ASG"),
                ("\\", "ERR"),
                (";", "SEM"),
                (unterminated_comment, "CMT_U"),
                ("", "EOF"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
