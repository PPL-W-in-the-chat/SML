# SML Lexeme-to-Token Mapping

This document defines the token contract between the SML lexer and the future
parser. The lexer converts source text into this token stream. The parser will
later decide whether a successful token stream follows the language grammar.

## Phase boundary

- The lexer emits `ERR` only for a character outside the `Character` set
  defined in the language proposal.
- ASCII membership alone is not sufficient. For example, `@` and `\` are
  ASCII characters, but they are outside the defined SML character set.
- If the lexer emits any `ERR` token, parsing must not begin.
- Forms made entirely from valid SML characters are preserved as tokens for
  the parser, even when the resulting sequence will be syntactically invalid.
- The lexer uses maximal munch when more than one token can begin at the same
  position.
- Whitespace is discarded.
- Complete comments are discarded unless comment retention is requested.

## Token data

Each token records:

| Field | Purpose |
| --- | --- |
| `type` | Token name from this contract |
| `lexeme` | Exact source text consumed for the token |
| `line` | One-based starting line |
| `column` | One-based starting column |
| `value` | Optional interpreted value |

To determine whether two tokens were attached, the parser checks that they
begin on the same line and that the second token's column immediately follows
the first token's lexeme. This distinguishes `100m` from `100 m` without an
additional source-offset field.

## Keywords

| Lexeme | Token |
| --- | --- |
| `let` | `KW_LET` |
| `const` | `KW_CONST` |
| `fn` | `KW_FN` |
| `return` | `KW_RETURN` |
| `if` | `KW_IF` |
| `else` | `KW_ELSE` |
| `for` | `KW_FOR` |
| `while` | `KW_WHILE` |
| `break` | `KW_BREAK` |
| `continue` | `KW_CONTINUE` |
| `print` | `KW_PRINT` |
| `input` | `KW_INPUT` |
| `assert` | `KW_ASSERT` |
| `as` | `KW_AS` |
| `import` | `KW_IMPORT` |

`import` is part of this lexer version and must also be added to the keyword
section of the language proposal.

## Reserved words

### Primitive types

| Lexeme | Token |
| --- | --- |
| `int` | `RW_INT` |
| `float` | `RW_FLOAT` |
| `bool` | `RW_BOOL` |
| `text` | `RW_TEXT` |

### Named dimensions

| Lexeme | Token |
| --- | --- |
| `Length` | `RW_LENGTH` |
| `Mass` | `RW_MASS` |
| `Time` | `RW_TIME` |
| `Force` | `RW_FORCE` |

## Boolean literals

| Lexeme | Token | Value |
| --- | --- | --- |
| `true` | `BOL_T` | `True` |
| `false` | `BOL_F` | `False` |

The spellings are reserved, but the token names describe their literal
category.

## Noise words

| Lexeme | Token |
| --- | --- |
| `to` | `NW_TO` |
| `then` | `NW_THEN` |
| `do` | `NW_DO` |

## Identifiers and literals

| Source form | Token | Value |
| --- | --- | --- |
| User-defined name | `ID` | Original name or `None` |
| Consecutive decimal digits | `INT` | Parsed integer |
| Digits, `.`, and one or more following digits | `DEC` | Parsed decimal |
| Closed string literal | `STR` | Contents without quotes |
| Unterminated string literal | `STR_U` | Contents collected after the opening quote |
| Closed comment | `CMT` | Normally discarded |
| Unterminated block comment | `CMT_U` | Contents collected after `/*` |

`STR_U` and `CMT_U` are parser-facing tokens, not lexical errors. They preserve
enough information for the future parser to report missing closing delimiters.

There is no `QTY` token. A quantity is a syntactic structure that the parser
will construct from numeric, identifier, bracket, and operator tokens.

## Assignment operators

| Lexeme | Token |
| --- | --- |
| `=` | `ASG` |
| `+=` | `ASG_ADD` |
| `-=` | `ASG_SUB` |
| `*=` | `ASG_MUL` |
| `/=` | `ASG_DIV` |

## Arithmetic operators

| Lexeme | Token |
| --- | --- |
| `+` | `AR_ADD` |
| `-` | `AR_SUB` |
| `*` | `AR_MUL` |
| `/` | `AR_DIV` |
| `%` | `AR_MOD` |
| `^` | `AR_POW` |

The lexer does not decide whether `+` or `-` is unary or binary. That decision
belongs to the parser.

## Relational operators

| Lexeme | Token |
| --- | --- |
| `==` | `REL_EQ` |
| `!=` | `REL_NE` |
| `<` | `REL_LT` |
| `>` | `REL_GT` |
| `<=` | `REL_LE` |
| `>=` | `REL_GE` |

## Logical operators

| Lexeme | Token |
| --- | --- |
| `&&` | `LOG_AND` |
| `||` | `LOG_OR` |
| `!` | `LOG_NOT` |

## Update operators

| Lexeme | Token |
| --- | --- |
| `++` | `UPD_INC` |
| `--` | `UPD_DEC` |

## Delimiters

### Paired enclosure delimiters

| Subclassification | Lexeme | Token |
| --- | --- | --- |
| Parenthesis, left | `(` | `PAR_L` |
| Parenthesis, right | `)` | `PAR_R` |
| Brace, left | `{` | `BRC_L` |
| Brace, right | `}` | `BRC_R` |
| Bracket, left | `[` | `BRK_L` |
| Bracket, right | `]` | `BRK_R` |

### Separators and terminator

| Subclassification | Lexeme | Token |
| --- | --- | --- |
| Separator | `,` | `COM` |
| Separator | `:` | `COL` |
| Statement terminator | `;` | `SEM` |

Double quotes delimit strings but are absorbed into `STR` or `STR_U`. Complete
comment delimiters are absorbed into `CMT`.

## Standalone symbols

These characters are part of the SML character set. Therefore, they must be
tokenized rather than reported as lexical errors.

| Lexeme | Token | Parser-facing purpose |
| --- | --- | --- |
| `.` | `DOT` | Preserve leading-dot and trailing-dot forms |
| `_` | `UND` | Preserve an underscore at token-start position |
| `&` | `AMP` | Preserve a lone ampersand |
| `|` | `BAR` | Preserve a lone vertical bar |

Maximal munch gives the multi-character logical operators priority:

```text
&&  -> LOG_AND
&   -> AMP
||  -> LOG_OR
|   -> BAR
```

An underscore remains part of an identifier after that identifier begins with
an ASCII letter:

```text
_hidden  -> UND ID("hidden")
foo_bar  -> ID("foo_bar")
foo_     -> ID("foo_")
```

## Control and diagnostic tokens

| Token | Purpose |
| --- | --- |
| `EOF` | Marks the end of the token stream for the parser |
| `ERR` | Represents a character outside the SML character set |

`ERR` is the only token that indicates lexical failure. The parser must run
only when the token stream contains no `ERR` token.

`EOF` is part of the parser-facing token stream. Presentation interfaces such
as `/api/tokenize`, the command-line table, and the website omit it so it does
not appear as an empty source-token row.

## Important tokenization examples

```text
007
-> INT("007")

5.
-> INT("5") DOT

.5
-> DOT INT("5")

5.0
-> DEC("5.0")

100m
-> INT("100") ID("m")

9.8[m/s^2]
-> DEC("9.8") BRK_L ID("m") AR_DIV ID("s") AR_POW INT("2") BRK_R

true & false
-> BOL_T AMP BOL_F

2@kg
-> INT("2") ERR("@") ID("kg")

/* unfinished
-> CMT_U
```

The examples above describe tokenization only. Leading zeros, malformed
decimal forms, invalid identifier positions, incomplete operators, malformed
unit expressions, and missing closing delimiters will be parser concerns.
