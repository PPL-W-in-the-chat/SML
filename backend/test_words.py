import unittest

from backend.lexer import tokenize


FIXED_WORDS = [
    ("let", "KW_LET"),
    ("const", "KW_CONST"),
    ("fn", "KW_FN"),
    ("return", "KW_RETURN"),
    ("if", "KW_IF"),
    ("else", "KW_ELSE"),
    ("for", "KW_FOR"),
    ("while", "KW_WHILE"),
    ("break", "KW_BREAK"),
    ("continue", "KW_CONTINUE"),
    ("print", "KW_PRINT"),
    ("input", "KW_INPUT"),
    ("assert", "KW_ASSERT"),
    ("as", "KW_AS"),
    ("import", "KW_IMPORT"),
    ("int", "RW_INT"),
    ("float", "RW_FLOAT"),
    ("bool", "RW_BOOL"),
    ("text", "RW_TEXT"),
    ("true", "BOL_T"),
    ("false", "BOL_F"),
    ("Length", "RW_LENGTH"),
    ("Mass", "RW_MASS"),
    ("Time", "RW_TIME"),
    ("Force", "RW_FORCE"),
    ("to", "NW_TO"),
    ("then", "NW_THEN"),
    ("do", "NW_DO"),
]


class FixedWordTokenTests(unittest.TestCase):
    def test_every_fixed_word_has_a_distinct_token_type(self) -> None:
        source = " ".join(lexeme for lexeme, _ in FIXED_WORDS)
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(actual, FIXED_WORDS + [("", "EOF")])

    def test_similar_user_defined_names_remain_identifiers(self) -> None:
        source = "letter integer truthful length mass timing forceful todo imported important"
        tokens = tokenize(source)
        self.assertTrue(tokens)
        self.assertTrue(all(token.type == "ID" for token in tokens[:-1]))
        self.assertEqual(tokens[-1].type, "EOF")

    def test_fixed_words_remain_case_sensitive(self) -> None:
        source = "Let TRUE length Import"
        tokens = tokenize(source)
        self.assertTrue(all(token.type == "ID" for token in tokens[:-1]))
        self.assertEqual(tokens[-1].type, "EOF")

    def test_boolean_literals_preserve_values(self) -> None:
        tokens = tokenize("true false")
        actual = [
            (token.type, token.lexeme, token.value)
            for token in tokens
        ]
        self.assertEqual(
            actual,
            [
                ("BOL_T", "true", True),
                ("BOL_F", "false", False),
                ("EOF", "", None),
            ],
        )

    def test_underscores_preserve_parser_ready_tokens(self) -> None:
        source = "_hidden foo_bar foo_ __x"
        actual = [(token.lexeme, token.type) for token in tokenize(source)]
        self.assertEqual(
            actual,
            [
                ("_", "UND"),
                ("hidden", "ID"),
                ("foo_bar", "ID"),
                ("foo_", "ID"),
                ("_", "UND"),
                ("_", "UND"),
                ("x", "ID"),
                ("", "EOF"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
