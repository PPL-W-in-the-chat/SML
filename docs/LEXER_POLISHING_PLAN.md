# SML Lexer Polishing Plan

This plan updates the existing lexer so that it follows the token contract in
`LEXEME_TOKEN_MAPPING.md` and produces a clean input stream for the future
parser. It does not add a parser, an AST, or parser-facing API endpoints.

## Goal

The polished lexer must:

1. Recognize every token in the agreed token contract.
2. Emit `ERR` only for characters outside the proposal's `Character` set.
3. Preserve all other source forms as parser-ready tokens.
4. Use maximal munch for multi-character operators.
5. Preserve exact source positions and original lexemes.
6. Produce `EOF` after the final source token.

The future compiler pipeline will be:

```text
source -> lexer -> token list -> parser
                    |
                    +-- stop if any token is ERR
```

## Step 1: Lock the contract with tests

Update the tests before changing lexer behavior so that failures clearly show
which part of the old contract remains.

- Update every fixed-word expectation to the `KW_`, `RW_`, `BOL_`, and `NW_`
  naming conventions.
- Add `import -> KW_IMPORT`.
- Verify that `imported`, `important`, and `Import` remain `ID` tokens.
- Update operator expectations to the `ASG_`, `AR_`, `REL_`, `LOG_`, and
  `UPD_` categories.
- Add expectations for `DOT`, `UND`, `AMP`, and `BAR`.
- Add expectations for `STR_U`, `CMT_U`, and `EOF`.
- Change the invalid-example test to expect only the character-set errors.

## Step 2: Rename the existing token mappings

Update the fixed-word, operator, and delimiter tables in `backend/lexer.py`.

- Keywords become `KW_*` tokens.
- Primitive types and named dimensions become `RW_*` tokens.
- Boolean literals become `BOL_T` and `BOL_F`.
- Noise words become `NW_*` tokens.
- Identifiers become `ID`.
- Numeric and string literals become `INT`, `DEC`, and `STR`.
- Operators use their subclass prefixes.
- Delimiters use `PAR_*`, `BRC_*`, `BRK_*`, `COM`, `COL`, and `SEM`.
- Rename `ERROR` to `ERR` and `COMMENT` to `CMT`.

Keep the mapping tables centralized near the top of the lexer so the complete
vocabulary remains easy to compare with the contract document.

## Step 3: Preserve source locations

Keep the existing one-based line and column fields and preserve each token's
exact source lexeme.

The future parser can determine whether two quantity components were attached
by checking that they begin on the same line and that the second token's
column immediately follows the first token's lexeme.

Verify locations with attached and spaced examples such as `100m` and `100 m`.

## Step 4: Simplify identifier scanning

- Continue starting an `ID` only with an ASCII letter.
- Continue accepting ASCII letters, digits, and underscores after the first
  character.
- Replace `_bad_underscore()` with single-character `UND` emission.

Expected behavior:

```text
_hidden  -> UND ID("hidden")
foo_bar  -> ID("foo_bar")
foo_     -> ID("foo_")
__x      -> UND UND ID("x")
```

## Step 5: Simplify number scanning

Change number scanning so it recognizes tokens without enforcing the future
parser's numeric restrictions.

1. Consume all consecutive digits.
2. If the next character is `.` and the character after it is a digit,
   consume the fractional part and emit `DEC`.
3. Otherwise, leave the dot for the next lexer iteration and emit `INT`.
4. Do not reject leading zeros.
5. Preserve the original numeric lexeme even when a value is computed.

Expected behavior:

```text
007    -> INT("007")
5.     -> INT("5") DOT
.5     -> DOT INT("5")
5.0    -> DEC("5.0")
007.5  -> DEC("007.5")
```

## Step 6: Stop constructing quantity tokens

Remove simple-quantity and compound-quantity assembly from `_number()`.

- `100m` becomes `INT ID`.
- `9.8[m/s^2]` becomes ordinary numeric, bracket, identifier, and operator
  tokens.
- Do not decide whether a unit name is registered.
- Do not validate the unit-expression grammar.
- Remove `_UnitParser`, `_UnitError`, `_unit_tokens()`, and
  `validate_unit_expression()` from the lexer.
- Preserve the unit grammar and its limits for reuse when the parser is built.

## Step 7: Tokenize every valid standalone symbol

Add explicit handling for:

- `.` as `DOT`
- `_` as `UND`
- `&` as `AMP`
- `|` as `BAR`

Retain maximal munch so `&&` and `||` become `LOG_AND` and `LOG_OR` before
the lexer considers `AMP` or `BAR`.

No character in the defined SML character set should become `ERR` merely
because it forms an invalid parser sequence.

## Step 8: Adjust string and comment scanning

- A closed string produces `STR`.
- An unterminated string produces `STR_U`, not `ERR`.
- A retained closed comment produces `CMT`.
- An unterminated block comment produces `CMT_U`, even when complete comments
  are normally discarded.
- Line comments continue through the end of their physical line and cannot be
  unterminated in the same sense as block comments.
- A character outside `Character` still produces `ERR`, including when it
  appears inside a string or comment.
- Position an `ERR` at the offending character rather than at the opening
  quote or comment delimiter.

`STR_U` and `CMT_U` preserve incomplete constructs for the future parser;
they do not count as lexical failures.

## Step 9: Restrict lexical errors to the character set

Audit every path that currently creates an error token.

After this change, `ERR` must be created only when the source contains a
character outside `Character`. In particular, remove lexical errors for:

- Leading zeros.
- Leading-dot and trailing-dot numeric forms.
- Leading underscores.
- Invalid unit-expression structure.
- Reserved words used as unit names.
- Lone `&` and `|` characters.
- Unterminated strings and block comments.

Do not use `str.isascii()` as the rule. Characters such as `@` and `\` are
ASCII but still outside the proposal's SML character set.

## Step 10: Emit EOF

Append one `EOF` token after scanning the source.

- Its lexeme is empty.
- Its line and column identify the position immediately after the last source
  character.
- It is included in the parser-facing token stream.
- The command-line output and website hide it because they present source
  tokens rather than parser control tokens.

## Step 11: Update API and UI compatibility

Do not add a parser endpoint.

- Keep `/api/tokenize` as the only analysis endpoint.
- Update checks from `ERROR` to `ERR`.
- Continue separating ordinary tokens from lexical errors in the API response.
- Exclude `EOF` from the `/api/tokenize` response so it does not appear as an
  empty row or increase the visible token count.
- Update the React UI to recognize `ERR` as an error row.
- Display the new token names without otherwise redesigning the interface.

## Step 12: Reconcile documentation and examples

- Add `import` to the proposal's keyword section.
- Add the lexeme-to-token mapping or link to its dedicated document.
- Explain that language restrictions can belong to the future parser even when
  their characters are lexically valid.
- Update `backend/README.md` to remove claims that the lexer validates leading
  zeros, unit expressions, and lone logical-operator characters.
- Update `examples/README.md` to explain that
  `invalid_lexical_errors.sml` contains both current lexical errors and forms
  intentionally preserved for the future parser.

The proposal's language restrictions remain in force. This work changes which
compiler phase will eventually report them, not whether they are valid SML.

## Step 13: Verify the lexer

Run the complete backend test suite and verify these invariants:

1. All existing valid examples produce no `ERR` tokens.
2. `invalid_lexical_errors.sml` produces exactly two `ERR` tokens: `@` and
   `\`.
3. The other forms in that example produce their documented parser-ready
   token sequences.
4. Every fixed word maps to exactly one expected token.
5. Similar spellings remain identifiers.
6. Multi-character operators satisfy maximal munch.
7. `STR_U` and `CMT_U` do not count as lexical errors.
8. Every token has correct line, column, and lexeme data.
9. Exactly one `EOF` token ends every successful or recovered token stream.

## Explicitly out of scope

This lexer-polishing pass does not include:

- A parser or parser errors.
- An abstract syntax tree.
- Semantic or unit registration checks.
- Import-statement grammar beyond recognizing `KW_IMPORT`.
- New parser or combined-analysis API endpoints.
- Security hardening or adversarial-input handling.
- Changes unrelated to the lexer contract.
