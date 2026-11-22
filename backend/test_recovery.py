import unittest

from backend.lexer import tokenize


class RecoveryTokenTests(unittest.TestCase):
    def test_unterminated_string_is_preserved(self) -> None:
        actual = [
            (token.lexeme, token.type, token.value)
            for token in tokenize('"unfinished')
        ]
        self.assertEqual(
            actual,
            [('"unfinished', "STR_U", "unfinished"), ("", "EOF", None)],
        )

    def test_unterminated_block_comment_is_preserved(self) -> None:
        actual = [
            (token.lexeme, token.type, token.value)
            for token in tokenize("/* unfinished")
        ]
        self.assertEqual(
            actual,
            [("/* unfinished", "CMT_U", " unfinished"), ("", "EOF", None)],
        )

    def test_line_comment_at_eof_is_complete(self) -> None:
        tokens = tokenize("// retained", keep_comments=True)
        self.assertEqual([token.type for token in tokens], ["CMT", "EOF"])

    def test_invalid_string_character_is_positioned_at_the_character(self) -> None:
        tokens = tokenize(r'"ok\bad"')
        self.assertEqual(
            (tokens[0].type, tokens[0].lexeme, tokens[0].line, tokens[0].column),
            ("ERR", "\\", 1, 4),
        )

    def test_invalid_comment_character_is_positioned_at_the_character(self) -> None:
        tokens = tokenize("/* ok @ */")
        self.assertEqual(
            (tokens[0].type, tokens[0].lexeme, tokens[0].line, tokens[0].column),
            ("ERR", "@", 1, 7),
        )

    def test_empty_source_contains_only_eof(self) -> None:
        tokens = tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(
            (tokens[0].type, tokens[0].lexeme, tokens[0].line, tokens[0].column),
            ("EOF", "", 1, 1),
        )

    def test_eof_follows_a_trailing_newline(self) -> None:
        eof = tokenize("x\n")[-1]
        self.assertEqual(
            (eof.type, eof.lexeme, eof.line, eof.column),
            ("EOF", "", 2, 1),
        )


if __name__ == "__main__":
    unittest.main()
