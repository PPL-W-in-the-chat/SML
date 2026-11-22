import unittest

from backend.lexer import CHARACTER, tokenize


class CharacterSetErrorTests(unittest.TestCase):
    def test_every_defined_character_avoids_err(self) -> None:
        for character in sorted(CHARACTER):
            with self.subTest(character=repr(character)):
                errors = [
                    token for token in tokenize(character) if token.type == "ERR"
                ]
                self.assertEqual(errors, [])

    def test_ascii_characters_outside_the_set_emit_err(self) -> None:
        errors = [token for token in tokenize("@\\") if token.type == "ERR"]
        self.assertEqual(
            [(token.lexeme, token.line, token.column) for token in errors],
            [("@", 1, 1), ("\\", 1, 2)],
        )


if __name__ == "__main__":
    unittest.main()
