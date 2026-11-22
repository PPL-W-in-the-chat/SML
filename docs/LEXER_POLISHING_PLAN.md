# SML Lexer Polishing Plan

This plan updates the existing lexer so that it follows the token contract in
`LEXEME_TOKEN_MAPPING.md` and produces a clean input stream for the future
parser. It does not add a parser, an AST, or parser-facing API endpoints.

## Current handoff

Last updated: 2026-11-22.

- **Current step:** Steps 1 through 13 are complete. The lexer-polishing roadmap
  is finished and ready for review.
- **Completed work:** Updated `backend/test_words.py` with the categorized
  fixed-word names, `import -> KW_IMPORT`, and `ID` expectations for similar
  spellings and case variants, including `imported`, `important`, and `Import`.
  Updated `backend/test_operators.py` with the `ASG`, `AR`, `REL`, `LOG`, and
  `UPD` token categories and expectations for `DOT`, `UND`, `AMP`, and `BAR`.
  Added recovery and stream-termination expectations for `STR_U`, `CMT_U`, and
  `EOF`, including `EOF` in existing exact token-list tests. Updated the example
  tests to accept only `@` and `\` as character-set errors. In Step 2, renamed
  the fixed-word mappings, identifier fallback, and ordinary literal token
  types, operator mappings, delimiter mappings, diagnostic token, and retained
  comment token to their contract names. Added Step 3 tests for the existing
  token fields and for attached-versus-spaced quantity positions. Step 4 now
  preserves leading underscores as `UND` and scans following identifiers
  normally. Step 5 now preserves leading-zero and dot-adjacent numeric forms
  for the parser while retaining their exact lexemes and parsed values. Step 6
  removes quantity assembly and the lexer-side unit-expression validator;
  quantity components now retain their individual token positions. Step 7 emits
  every valid standalone symbol while retaining maximal munch. Step 8 preserves
  incomplete constructs and positions invalid-character diagnostics precisely.
  Step 9 makes explicit `Character`-set membership the sole source of `ERR`.
  Step 10 appends a positioned `EOF` internally and hides it from presentation
  output. Step 11 aligns the API, API tests, and React UI with `ERR`, `CMT`, and
  hidden `EOF` behavior. Step 12 reconciles the proposal, backend guide, and
  examples guide with the token contract and lexer-parser phase boundary. Step
  13 verifies every listed lexer invariant, adds full invalid-example sequence
  coverage, and locks the boolean literal values required by the contract.
- **Last validation:** The 11 focused Step 1 tests ran. The valid-example test
  passed; the other 10 failed as expected against the unchanged lexer because
  it still emits the old token names, reports incomplete constructs as errors,
  omits `EOF`, and does not emit `ERR`. `git diff --check` passes. The full
  backend suite has not been run for these test-contract changes. After the
  first Step 2 change, all fixed-word and identifier names match the contract;
  the three word tests now fail only because `EOF` is not implemented yet. A
  CLI probe confirmed `5 5.0 "x"` emits `INT`, `DEC`, and `STR` with their
  values preserved and displayed. An operator probe confirmed every renamed
  category and maximal munch; remaining operator-test failures concern `EOF`
  and standalone symbols. A delimiter probe confirmed all nine short names in
  source order. CLI probes confirmed `ERR` is reported with exit status 1,
  ordinary comments are discarded by default, and retained comments emit
  `CMT`. The Step 3 token-data test passes; its quantity-position test is
  intentionally pending quantity splitting and `EOF`. A Step 4 probe confirmed
  `_hidden`, `foo_bar`, `foo_`, and `__x` produce the planned `UND` and `ID`
  sequence at the correct columns; its focused test awaits only `EOF`. A Step 5
  probe confirmed leading-zero integers and decimals retain their lexemes and
  values; dot cases await `DOT` and `EOF`. Step 6 location and quantity probes
  match the complete component sequences and malformed unit syntax produces no
  `ERR`; those focused tests now await only `EOF`. Step 7 standalone-symbol and
  maximal-munch probes match the contract; their tests await only `EOF`. Step 8
  recovery and diagnostic-position tests match the contract; remaining failures
  await only `EOF`. Step 9's exhaustive character-set and example tests pass;
  `_character_error()` is the sole `ERR` constructor. After Step 10, 25 of 27
  backend tests pass; only the two stale Step 11 API expectations fail. CLI
  table and JSON probes confirm `EOF` is hidden. After Step 11, all 27 backend
  tests passed. Step 12's documentation consistency search found no stale lexer
  behavior claims. Step 13 adds exact parser-ready sequence coverage for the
  invalid example and verifies boolean literal values; all 29 backend tests now
  pass. The Vite production build also succeeds, and `git diff --check` passes.
- **Next focused task:** Review the completed lexer-polishing diff before
  committing it. Parser implementation remains a separate future task.
- **Review and Git state:** All changes through Step 13 are awaiting user review
  and are uncommitted.

Check an item only when its stated task is complete. In Step 1, a checked item
means the test expectations are written; it does not mean the lexer passes
those tests. Implementation items require the behavior and relevant passing
checks. Step 13 records final verification of the complete contract.

After each focused change, update the checkboxes and this handoff with the
current step, validation result, and next task. Continue following the
learning-first agreement before the next meaningful edit.

## Goal

The polished lexer must:

- [x] Recognize every token in the agreed token contract.
- [x] Emit `ERR` only for characters outside the proposal's `Character` set.
- [x] Preserve all other source forms as parser-ready tokens.
- [x] Use maximal munch for multi-character operators.
- [x] Preserve exact source positions and original lexemes.
- [x] Produce `EOF` after the final source token.

The future compiler pipeline will be:

```text
source -> lexer -> token list -> parser
                    |
                    +-- stop if any token is ERR
```

## Step 1: Lock the contract with tests

Update the tests before changing lexer behavior so that failures clearly show
which part of the old contract remains.

- [x] Update every fixed-word expectation to the `KW_`, `RW_`, `BOL_`, and `NW_`
  naming conventions.
- [x] Add `import -> KW_IMPORT`.
- [x] Add test expectations that `imported`, `important`, and `Import` remain
  `ID` tokens.
- [x] Update operator expectations to the `ASG_`, `AR_`, `REL_`, `LOG_`, and
  `UPD_` categories.
- [x] Add expectations for `DOT`, `UND`, `AMP`, and `BAR`.
- [x] Add expectations for `STR_U`, `CMT_U`, and `EOF`.
- [x] Change the invalid-example test to expect only the character-set errors.

## Step 2: Rename the existing token mappings

Update the fixed-word, operator, and delimiter tables in `backend/lexer.py`.

- [x] Keywords become `KW_*` tokens.
- [x] Primitive types and named dimensions become `RW_*` tokens.
- [x] Boolean literals become `BOL_T` and `BOL_F`.
- [x] Noise words become `NW_*` tokens.
- [x] Identifiers become `ID`.
- [x] Numeric and string literals become `INT`, `DEC`, and `STR`.
- [x] Operators use their subclass prefixes.
- [x] Delimiters use `PAR_*`, `BRC_*`, `BRK_*`, `COM`, `COL`, and `SEM`.
- [x] Rename `ERROR` to `ERR` and `COMMENT` to `CMT`.

Keep the mapping tables centralized near the top of the lexer so the complete
vocabulary remains easy to compare with the contract document.

## Step 3: Preserve source locations

- [x] Keep the existing one-based line and column fields and preserve each
  token's exact source lexeme. Retain the `value` field without adding an
  absolute offset.

The future parser can determine whether two quantity components were attached
by checking that they begin on the same line and that the second token's
column immediately follows the first token's lexeme.

- [x] Verify locations with attached and spaced examples such as `100m` and
  `100 m`.

## Step 4: Simplify identifier scanning

- [x] Continue starting an `ID` only with an ASCII letter.
- [x] Continue accepting ASCII letters, digits, and underscores after the first
  character.
- [x] Replace `_bad_underscore()` with single-character `UND` emission.

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

- [x] Consume all consecutive digits.
- [x] If the next character is `.` and the character after it is a digit,
   consume the fractional part and emit `DEC`.
- [x] Otherwise, leave the dot for the next lexer iteration and emit `INT`.
- [x] Do not reject leading zeros.
- [x] Preserve the original numeric lexeme even when a value is computed.

Expected behavior:

```text
007    -> INT("007")
5.     -> INT("5") DOT
.5     -> DOT INT("5")
5.0    -> DEC("5.0")
007.5  -> DEC("007.5")
```

## Step 6: Stop constructing quantity tokens

- [x] Remove simple-quantity and compound-quantity assembly from `_number()`.

- [x] `100m` becomes `INT ID`.
- [x] `9.8[m/s^2]` becomes ordinary numeric, bracket, identifier, and operator
  tokens.
- [x] Do not decide whether a unit name is registered.
- [x] Do not validate the unit-expression grammar.
- [x] Remove `_UnitParser`, `_UnitError`, `_unit_tokens()`, and
  `validate_unit_expression()` from the lexer.
- [x] Preserve the unit grammar and its limits for reuse when the parser is built.

## Step 7: Tokenize every valid standalone symbol

Add explicit handling for:

- [x] `.` as `DOT`
- [x] `_` as `UND`
- [x] `&` as `AMP`
- [x] `|` as `BAR`

- [x] Retain maximal munch so `&&` and `||` become `LOG_AND` and `LOG_OR`
  before the lexer considers `AMP` or `BAR`.

No character in the defined SML character set should become `ERR` merely
because it forms an invalid parser sequence.

## Step 8: Adjust string and comment scanning

- [x] A closed string produces `STR`.
- [x] An unterminated string produces `STR_U`, not `ERR`.
- [x] A retained closed comment produces `CMT`.
- [x] An unterminated block comment produces `CMT_U`, even when complete comments
  are normally discarded.
- [x] Line comments continue through the end of their physical line and cannot be
  unterminated in the same sense as block comments.
- [x] A character outside `Character` still produces `ERR`, including when it
  appears inside a string or comment.
- [x] Position an `ERR` at the offending character rather than at the opening
  quote or comment delimiter.

`STR_U` and `CMT_U` preserve incomplete constructs for the future parser;
they do not count as lexical failures.

## Step 9: Restrict lexical errors to the character set

- [x] Audit every path that currently creates an error token.

After this change, `ERR` must be created only when the source contains a
character outside `Character`. In particular, remove lexical errors for:

- [x] Leading zeros.
- [x] Leading-dot and trailing-dot numeric forms.
- [x] Leading underscores.
- [x] Invalid unit-expression structure.
- [x] Reserved words used as unit names.
- [x] Lone `&` and `|` characters.
- [x] Unterminated strings and block comments.

Do not use `str.isascii()` as the rule. Characters such as `@` and `\` are
ASCII but still outside the proposal's SML character set.

## Step 10: Emit EOF

- [x] Append one `EOF` token after scanning the source.

- [x] Its lexeme is empty.
- [x] Its line and column identify the position immediately after the last source
  character.
- [x] It is included in the parser-facing token stream.
- [x] The command-line output and website hide it because they present source
  tokens rather than parser control tokens.

## Step 11: Update API and UI compatibility

Do not add a parser endpoint.

- [x] Keep `/api/tokenize` as the only analysis endpoint.
- [x] Update checks from `ERROR` to `ERR`.
- [x] Continue separating ordinary tokens from lexical errors in the API response.
- [x] Exclude `EOF` from the `/api/tokenize` response so it does not appear as an
  empty row or increase the visible token count.
- [x] Update the React UI to recognize `ERR` as an error row.
- [x] Display the new token names without otherwise redesigning the interface.

## Step 12: Reconcile documentation and examples

- [x] Add `import` to the proposal's keyword section.
- [x] Add the lexeme-to-token mapping or link to its dedicated document.
- [x] Explain that language restrictions can belong to the future parser even when
  their characters are lexically valid.
- [x] Update `backend/README.md` to remove claims that the lexer validates leading
  zeros, unit expressions, and lone logical-operator characters.
- [x] Update `examples/README.md` to explain that
  `invalid_lexical_errors.sml` contains both current lexical errors and forms
  intentionally preserved for the future parser.

The proposal's language restrictions remain in force. This work changes which
compiler phase will eventually report them, not whether they are valid SML.

## Step 13: Verify the lexer

- [x] Run the complete backend test suite.

Verify these invariants:

- [x] All existing valid examples produce no `ERR` tokens.
- [x] `invalid_lexical_errors.sml` produces exactly two `ERR` tokens: `@` and
   `\`.
- [x] The other forms in that example produce their documented parser-ready
   token sequences.
- [x] Every fixed word maps to exactly one expected token.
- [x] Similar spellings remain identifiers.
- [x] Multi-character operators satisfy maximal munch.
- [x] `STR_U` and `CMT_U` do not count as lexical errors.
- [x] Every token has correct line, column, and lexeme data.
- [x] Exactly one `EOF` token ends every successful or recovered token stream.

## Explicitly out of scope

This lexer-polishing pass does not include:

- A parser or parser errors.
- An abstract syntax tree.
- Semantic or unit registration checks.
- Import-statement grammar beyond recognizing `KW_IMPORT`.
- New parser or combined-analysis API endpoints.
- Security hardening or adversarial-input handling.
- Changes unrelated to the lexer contract.
