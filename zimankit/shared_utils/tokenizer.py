"""Word / sentence tokenization for Arabic-script and Latin-script Kurdish.

Design rules
------------
* A ZWNJ is *inside* a word (it separates morphemes of one orthographic word),
  so it never splits a token.
* In Latin text an apostrophe between letters is kept ("HDP'yî"); quotes at
  the edges of a word are punctuation.
* Hyphenated compounds are split by default (``keep_hyphen=False``) because
  both dialects write most compounds solid or spaced, and a hyphen is usually
  a dash or a line-break artefact.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, Literal

TokenKind = Literal["word", "number", "punct"]

_AR = "ؠ-يٮ-ۓەۺ-ۿݐ-ݿ"
_LAT = "A-Za-zÀ-ɏḀ-ỿ"
_CYR = "Ѐ-ӿ"
_DIG = "0-9٠-٩۰-۹"

WORD_RE = re.compile(
    rf"[{_AR}]+(?:‌[{_AR}]+)*"  # Arabic-script word, ZWNJ allowed inside
    rf"|[{_LAT}]+(?:'[{_LAT}]+)*"  # Latin word with internal apostrophes
    rf"|[{_CYR}]+"
)
NUMBER_RE = re.compile(rf"[{_DIG}]+(?:[.,٫٬][{_DIG}]+)*")
TOKEN_RE = re.compile(
    rf"(?P<word>{WORD_RE.pattern})"
    rf"|(?P<number>{NUMBER_RE.pattern})"
    r"|(?P<punct>[^\s])"
)
HYPHEN_WORD_RE = re.compile(rf"(?:{WORD_RE.pattern})(?:-(?:{WORD_RE.pattern}))+")
SENTENCE_END_RE = re.compile(r"(?<=[.!?؟۔])\s+|\n+")


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    kind: TokenKind
    start: int
    end: int


def tokenize(text: str, keep_hyphen: bool = False) -> list[Token]:
    """Split *text* into word, number and punctuation tokens with offsets."""
    tokens: list[Token] = []
    pos = 0
    if keep_hyphen:
        hyphen_spans = {m.start(): m for m in HYPHEN_WORD_RE.finditer(text)}
    else:
        hyphen_spans = {}
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
            continue
        if pos in hyphen_spans:
            m = hyphen_spans[pos]
            tokens.append(Token(m.group(), "word", m.start(), m.end()))
            pos = m.end()
            continue
        m = TOKEN_RE.match(text, pos)
        if m is None:  # pragma: no cover - TOKEN_RE matches any non-space
            pos += 1
            continue
        kind = m.lastgroup or "punct"
        tokens.append(Token(m.group(), kind, m.start(), m.end()))  # type: ignore[arg-type]
        pos = m.end()
    return tokens


def words(text: str) -> Iterator[str]:
    """Yield only the word tokens of *text* (fast path, no offsets)."""
    for m in WORD_RE.finditer(text):
        yield m.group()


def sentences(text: str) -> list[str]:
    """Rough sentence split on terminal punctuation and newlines."""
    return [s.strip() for s in SENTENCE_END_RE.split(text) if s and s.strip()]
