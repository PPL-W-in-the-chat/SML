# SML lexical analyzer

`lexer.py` implements the lexical analyzer defined by the SML programming
language proposal for COSC-303. It requires Python 3.8 or newer and uses only
the Python standard library.

## Command-line usage

Run these commands from the repository root:

```powershell
python -m backend.lexer examples/valid_operators.sml
python -m backend.lexer -c "let x = 5m;"
python -m backend.lexer examples/valid_comments.sml --comments
python -m backend.lexer examples/valid_units.sml --json
Get-Content examples/valid_units.sml | python -m backend.lexer
```

The process exits with status `0` when no lexical errors are found and `1`
when the input contains lexical errors.

## Token categories

The complete parser-facing token vocabulary is defined in
[`docs/LEXEME_TOKEN_MAPPING.md`](../docs/LEXEME_TOKEN_MAPPING.md). Its short
categorized names include `KW_IMPORT`, `ID`, `INT`, `DEC`, `STR`, `CMT`, and
the operator and delimiter families. `ERR` is reserved for a character outside
the proposal's `Character` set. `EOF` ends the internal token stream but is
hidden from command-line and JSON presentation.

Each `Token` stores its category, original lexeme, one-based line and column,
and an optional value. Internally, a lexer mark is the tuple
`(absolute position, line, column)` where a lexeme begins; the absolute
position is not part of the emitted token data.

## Lexical rules

- The lexer uses maximal munch, so the longest valid lexeme wins. For example,
  `+=` is one operator rather than `+` followed by `=`.
- Each operator symbol has a distinct token type. `AR_ADD` and `AR_SUB` identify
  the symbols themselves; deciding whether they are unary or binary belongs to
  a future parser.
- Every fixed language word has a distinct token type. Variable user-defined
  names remain `ID` tokens.
- The lexer does not construct quantity tokens. For example, `100m` becomes
  `INT("100") ID("m")`, and compound quantities become ordinary numeric,
  bracket, identifier, and operator tokens. The future parser checks attachment
  from token locations and validates unit-expression syntax.
- Leading `+` and `-` characters are operators, not part of numeric literals.
- Whitespace and comments are discarded unless `--comments` is supplied.
- An identifier starts with an ASCII letter. A leading underscore is preserved
  as `UND`, followed by an `ID` when applicable.
- Leading-zero and dot-adjacent numeric forms are preserved for the parser. For
  example, `007` becomes `INT`, `5.` becomes `INT DOT`, and `.5` becomes
  `DOT INT`.
- String escape sequences are not supported.
- A lone `&` or `|` becomes `AMP` or `BAR`; maximal munch still makes `&&` and
  `||` become `LOG_AND` and `LOG_OR`.
- Unterminated strings and block comments become `STR_U` and `CMT_U`. They are
  parser-facing recovery tokens rather than lexical errors.

Forms made only from valid `Character` members can still be invalid SML. The
lexer preserves those forms so the future parser can report the relevant
syntax restriction. Only an outside-set character produces `ERR`.

## Unit-expression grammar

```text
UnitPower       = UnitSymbol [ "^" SignedInteger ]
UnitProduct     = UnitPower { "*" UnitPower }
UnitDenominator = UnitPower | "(" UnitProduct ")"
UnitExpression  = UnitProduct [ "/" UnitDenominator ]
```

The future parser will enforce the grammar and limits above. The text inside
one unit annotation is limited to 128 ASCII characters, eight written
unit-factor occurrences, and exponents from `-16` through `16`.

## Implementation map

The source is organized in this order:

1. Character sets and identifier characters
2. Keywords, primitive types, dimensions, literals, and noise words
3. Operators and delimiters
4. The immutable `Token` data class
5. The stateful `SMLLexer`
6. Table, report, JSON, and command-line output

Within `SMLLexer`, scanning proceeds through low-level cursor helpers, the main
dispatch loop, comments, words, numbers, strings, and operators. Number scanning
reads consecutive digits and consumes a fractional part only when a dot is
followed by a digit. Block comments consume their opening `/*` before searching
for the closing `*/`; strings similarly consume their opening quote before
collecting their contents.

The full language specification is in
`docs/SML_Programming_Language_Proposal.md`.
