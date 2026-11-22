#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, List, Optional, Tuple

CAP = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
SM = set("abcdefghijklmnopqrstuvwxyz")
ALPHA = CAP | SM
DIGITS = set("0123456789")
SYMBOLS = set('.+-*/%^<>=!&|(){}[];:,"_')
WHITESPACE = set(" \t\r\n")
CHARACTER = ALPHA | DIGITS | SYMBOLS | WHITESPACE
IDENT_REST = ALPHA | DIGITS | {"_"}

KEYWORD_TOKENS = {
    "let": "KW_LET", "const": "KW_CONST", "fn": "KW_FN",
    "return": "KW_RETURN", "if": "KW_IF", "else": "KW_ELSE",
    "for": "KW_FOR", "while": "KW_WHILE", "break": "KW_BREAK",
    "continue": "KW_CONTINUE", "print": "KW_PRINT", "input": "KW_INPUT",
    "assert": "KW_ASSERT", "as": "KW_AS", "import": "KW_IMPORT",
}
TYPE_TOKENS = {
    "int": "RW_INT", "float": "RW_FLOAT",
    "bool": "RW_BOOL", "text": "RW_TEXT",
}
BOOLEAN_TOKENS = {"true": "BOL_T", "false": "BOL_F"}
BOOLEAN_VALUES = {"true": True, "false": False}
DIMENSION_TOKENS = {
    "Length": "RW_LENGTH", "Mass": "RW_MASS",
    "Time": "RW_TIME", "Force": "RW_FORCE",
}
NOISE_WORD_TOKENS = {"to": "NW_TO", "then": "NW_THEN", "do": "NW_DO"}

WORD_CLASSES = {
    **KEYWORD_TOKENS,
    **TYPE_TOKENS,
    **BOOLEAN_TOKENS,
    **DIMENSION_TOKENS,
    **NOISE_WORD_TOKENS,
}

TWO_CHAR_OPERATORS = {
    "+=": "ASG_ADD", "-=": "ASG_SUB",
    "*=": "ASG_MUL", "/=": "ASG_DIV",
    "==": "REL_EQ", "!=": "REL_NE",
    "<=": "REL_LE", ">=": "REL_GE",
    "&&": "LOG_AND", "||": "LOG_OR",
    "++": "UPD_INC", "--": "UPD_DEC",
}
ONE_CHAR_OPERATORS = {
    "=": "ASG",
    "+": "AR_ADD", "-": "AR_SUB",
    "*": "AR_MUL", "/": "AR_DIV",
    "%": "AR_MOD", "^": "AR_POW",
    "<": "REL_LT", ">": "REL_GT",
    "!": "LOG_NOT",
    "&": "AMP", "|": "BAR",
}
OPERATOR_START = set(ONE_CHAR_OPERATORS)

DELIMITERS = {
    ";": "SEM", "(": "PAR_L", ")": "PAR_R",
    "{": "BRC_L", "}": "BRC_R", "[": "BRK_L", "]": "BRK_R",
    ",": "COM", ":": "COL",
}

@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    line: int
    column: int
    value: Any = None


Mark = Tuple[int, int, int]


class SMLLexer:
    def __init__(self, source: str, keep_comments: bool = False):
        self.src = source
        self.keep_comments = keep_comments
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self, k: int = 0) -> str:
        i = self.pos + k
        return self.src[i] if i < len(self.src) else ""

    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.pos >= len(self.src):
                return
            if self.src[self.pos] == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _mark(self) -> Mark:
        return (self.pos, self.line, self.col)

    def _make(self, ttype: str, mark: Mark, value: Any = None) -> Token:
        return Token(ttype, self.src[mark[0]:self.pos], mark[1], mark[2], value)

    def _character_error(self, mark: Mark) -> Token:
        ch = self.src[mark[0]]
        message = "character %r is not part of the SML character set" % ch
        return Token("ERR", ch, mark[1], mark[2], message)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < len(self.src):
            ch = self._peek()
            if ch in WHITESPACE:
                self._advance()
                continue

            mark = self._mark()
            nxt = self._peek(1)

            if ch == "/" and nxt == "/":
                tok = self._line_comment(mark)
            elif ch == "/" and nxt == "*":
                tok = self._block_comment(mark)
            elif ch in ALPHA:
                tok = self._word(mark)
            elif ch in DIGITS:
                tok = self._number(mark)
            elif ch == '"':
                tok = self._string(mark)
            elif ch == "_":
                self._advance()
                tok = self._make("UND", mark)
            elif ch == ".":
                self._advance()
                tok = self._make("DOT", mark)
            elif ch in DELIMITERS:
                self._advance()
                tok = self._make(DELIMITERS[ch], mark)
            elif ch in OPERATOR_START:
                tok = self._operator(mark)
            else:
                self._advance()
                tok = self._character_error(mark)

            if tok.type == "CMT" and not self.keep_comments:
                continue
            tokens.append(tok)
        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens

    def _line_comment(self, mark: Mark) -> Token:
        bad_mark: Optional[Mark] = None
        while self._peek() not in ("", "\n", "\r"):
            ch = self._peek()
            if ch not in CHARACTER and bad_mark is None:
                bad_mark = self._mark()
            self._advance()
        if bad_mark is not None:
            return self._character_error(bad_mark)
        return self._make("CMT", mark)

    def _block_comment(self, mark: Mark) -> Token:
        bad_mark: Optional[Mark] = None
        self._advance(2)
        content_start = self.pos
        while True:
            if self.pos >= len(self.src):
                if bad_mark is not None:
                    return self._character_error(bad_mark)
                content = self.src[content_start:self.pos]
                return self._make("CMT_U", mark, content)
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance(2)
                if bad_mark is not None:
                    return self._character_error(bad_mark)
                return self._make("CMT", mark)
            ch = self._peek()
            if ch not in CHARACTER and bad_mark is None:
                bad_mark = self._mark()
            self._advance()

    def _word(self, mark: Mark) -> Token:
        while self._peek() in IDENT_REST:
            self._advance()
        text = self.src[mark[0]:self.pos]
        return self._make(
            WORD_CLASSES.get(text, "ID"), mark, BOOLEAN_VALUES.get(text)
        )

    def _number(self, mark: Mark) -> Token:
        while self._peek() in DIGITS:
            self._advance()

        is_decimal = False
        if self._peek() == "." and self._peek(1) in DIGITS:
            self._advance()
            while self._peek() in DIGITS:
                self._advance()
            is_decimal = True
        number_text = self.src[mark[0]:self.pos]
        magnitude = float(number_text) if is_decimal else int(number_text)
        return self._make("DEC" if is_decimal else "INT", mark, magnitude)

    def _string(self, mark: Mark) -> Token:
        self._advance()
        content_start = self.pos
        bad_mark: Optional[Mark] = None
        while True:
            ch = self._peek()
            if ch == "" or ch in ("\n", "\r"):
                if bad_mark is not None:
                    return self._character_error(bad_mark)
                content = self.src[content_start:self.pos]
                return self._make("STR_U", mark, content)
            if ch == '"':
                content = self.src[content_start:self.pos]
                self._advance()
                if bad_mark is not None:
                    return self._character_error(bad_mark)
                return self._make("STR", mark, content)
            if ch not in CHARACTER and bad_mark is None:
                bad_mark = self._mark()
            self._advance()

    def _operator(self, mark: Mark) -> Token:
        c = self._peek()
        two = c + self._peek(1)
        if two in TWO_CHAR_OPERATORS:
            self._advance(2)
            return self._make(TWO_CHAR_OPERATORS[two], mark)
        self._advance()
        return self._make(ONE_CHAR_OPERATORS[c], mark)


def tokenize(source: str, keep_comments: bool = False) -> List[Token]:
    return SMLLexer(source, keep_comments).tokenize()


def _shorten(text: str, limit: int = 48) -> str:
    text = text.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _value_text(tok: Token) -> str:
    if tok.type in ("INT", "DEC"):
        return str(tok.value)
    if tok.type == "STR":
        return _shorten(tok.value, 30)
    return ""


def render_table(tokens: List[Token]) -> str:
    headers = ("#", "Line:Col", "Token", "Lexeme", "Value")
    visible = [token for token in tokens if token.type != "EOF"]
    rows = [
        (str(i), "%d:%d" % (t.line, t.column), t.type, _shorten(t.lexeme), _value_text(t))
        for i, t in enumerate(visible, 1)
    ]
    widths = [max(len(h), *(len(r[c]) for r in rows)) if rows else len(h)
              for c, h in enumerate(headers)]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"

    def fmt(cells: Tuple[str, ...]) -> str:
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)) + " |"

    out = [line, fmt(headers), line]
    out.extend(fmt(r) for r in rows)
    out.append(line)
    return "\n".join(out)


def render_report(tokens: List[Token]) -> str:
    errors = [t for t in tokens if t.type == "ERR"]
    good = [t for t in tokens if t.type not in ("ERR", "EOF")]
    parts = [render_table(tokens), "", "Token summary:"]
    for ttype, n in sorted(Counter(t.type for t in good).items()):
        parts.append("  %-20s %d" % (ttype, n))
    parts.append("  %-20s %d" % ("TOTAL (valid)", len(good)))
    parts.append("")
    if errors:
        parts.append("Lexical errors (%d):" % len(errors))
        for t in errors:
            parts.append("  line %d, col %d: %s  [lexeme: %s]"
                         % (t.line, t.column, t.value, _shorten(t.lexeme, 40)))
    else:
        parts.append("No lexical errors.")
    return "\n".join(parts)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Lexical analyzer for SML (Standard Measurement Language).")
    ap.add_argument("file", nargs="?", help="path to an SML source file (omit to read stdin)")
    ap.add_argument("-c", "--code", help="analyze this string instead of a file")
    ap.add_argument("--comments", action="store_true", help="include CMT tokens in the output")
    ap.add_argument("--json", action="store_true", help="print tokens and errors as JSON")
    args = ap.parse_args(argv)

    if args.code is not None:
        source = args.code
    elif args.file:
        try:
            with open(args.file, encoding="utf-8", newline="") as fh:
                source = fh.read()
        except OSError as exc:
            print("error: cannot read %s: %s" % (args.file, exc), file=sys.stderr)
            return 2
    elif not sys.stdin.isatty():
        source = sys.stdin.read()
    else:
        ap.print_help()
        return 2

    tokens = tokenize(source, keep_comments=args.comments)
    errors = [t for t in tokens if t.type == "ERR"]

    if args.json:
        print(json.dumps({"tokens": [asdict(t) for t in tokens
                                     if t.type not in ("ERR", "EOF")],
                          "errors": [asdict(t) for t in errors]}, indent=2))
    else:
        print(render_report(tokens))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
