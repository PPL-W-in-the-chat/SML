import unittest

from backend.lexer import tokenize


OPERATORS = [
    ("=", "ASG"),
    ("+=", "ASG_ADD"),
    ("-=", "ASG_SUB"),
    ("*=", "ASG_MUL"),
    ("/=", "ASG_DIV"),
    ("+", "AR_ADD"),
    ("-", "AR_SUB"),
    ("*", "AR_MUL"),
    ("/", "AR_DIV"),
    ("%", "AR_MOD"),
    ("^", "AR_POW"),
    ("==", "REL_EQ"),
    ("!=", "REL_NE"),
    ("<", "REL_LT"),
    (">", "REL_GT"),
    ("<=", "REL_LE"),
    (">=", "REL_GE"),
    ("&&", "LOG_AND"),
    ("||", "LOG_OR"),
    ("!", "LOG_NOT"),
    ("++", "UPD_INC"),
    ("--", "UPD_DEC"),
]

STANDALONE_SYMBOLS = [
    (".", "DOT"),
    ("_", "UND"),
    ("&", "AMP"),
    ("|", "BAR"),
]


class OperatorTokenTests(unittest.TestCase):
    def test_every_operator_has_a_distinct_token_type(self) -> None:
        for lexeme, expected_type in OPERATORS:
            with self.subTest(lexeme=lexeme):
                tokens = tokenize(lexeme)
                self.assertEqual(len(tokens), 2)
                self.assertEqual(tokens[0].lexeme, lexeme)
                self.assertEqual(tokens[0].type, expected_type)
                self.assertEqual(tokens[1].type, "EOF")

    def test_maximal_munch_across_all_operators(self) -> None:
        source = " ".join(lexeme for lexeme, _ in OPERATORS)
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(actual, OPERATORS + [("", "EOF")])

    def test_valid_standalone_symbols_have_tokens(self) -> None:
        source = " ".join(lexeme for lexeme, _ in STANDALONE_SYMBOLS)
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(actual, STANDALONE_SYMBOLS + [("", "EOF")])


if __name__ == "__main__":
    unittest.main()
