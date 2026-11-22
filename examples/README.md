# Demo inputs

These files can be pasted into the website or analyzed directly from the
repository root:

```powershell
python -m backend.lexer examples/valid_units.sml
python -m backend.lexer examples/valid_control_flow.sml
python -m backend.lexer examples/valid_comments.sml --comments
python -m backend.lexer examples/valid_operators.sml
python -m backend.lexer examples/invalid_lexical_errors.sml
```

The four `valid_*.sml` files should finish with exit status `0`. The invalid
file should finish with exit status `1`, but not every unusual form in it is a
lexical error. It contains exactly two characters outside the SML `Character`
set: `@` and `\`. Those characters produce `ERR`. The leading-zero number,
trailing dot, leading underscore, malformed unit expression, lone `&`, and
unterminated block comment are preserved as ordinary or recovery tokens for the
future parser. The file therefore demonstrates both current lexical errors and
syntactically invalid forms intentionally preserved across the lexer-parser
boundary.

Run the automated example check with:

```powershell
python -m unittest backend.test_examples backend.test_operators
```
