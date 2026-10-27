"""Script-independent text cleaning.

These steps are safe for any Kurdish text (and most other text): they never
change a letter's identity, only the invisible machinery around it.  Dialect
specific letter rules live in ``skills_ckb.orthography`` and
``skills_kmr.orthography``.

Pipeline (all steps are idempotent):

1. Unicode NFC composition.
2. Arabic presentation forms (U+FB50-U+FDFF, U+FE70-U+FEFF) -> base letters.
3. Remove bidi control marks and BOMs.
4. Micro-spaces typed inside words (ZWSP, thin/hair space, soft hyphen ...)
   -> ZWNJ, then redundant ZWNJs are dropped.
5. Wide/no-break spaces -> ASCII space, collapse runs of horizontal space.
6. Optional digit folding and URL / e-mail / mention / emoji stripping.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

from .unicode_tables import (
    ARABIC_INDIC_DIGITS,
    ARABIC_NON_JOINING,
    BIDI_CONTROLS,
    LATIN_DIGITS,
    MICRO_SPACES,
    PERSIAN_DIGITS,
    WIDE_SPACES,
    ZWJ,
    ZWNJ,
)

DigitTarget = Literal["keep", "latin", "arabic-indic"]

URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MENTION_RE = re.compile(r"(?<!\w)[@#][\w‌]+")
EMOJI_RE = re.compile(
    "[\U0001f000-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff️‍⃣]+"
)
HSPACE_RE = re.compile(r"[^\S\r\n]+")
BLANK_LINES_RE = re.compile(r"\n\s*\n+")

_MICRO_TO_ZWNJ = str.maketrans({c: ZWNJ for c in MICRO_SPACES})
_WIDE_TO_SPACE = str.maketrans({c: " " for c in WIDE_SPACES})
_DROP_BIDI = str.maketrans({c: None for c in BIDI_CONTROLS})
_DIGITS = {
    "latin": str.maketrans(ARABIC_INDIC_DIGITS + PERSIAN_DIGITS, LATIN_DIGITS * 2),
    "arabic-indic": str.maketrans(LATIN_DIGITS + PERSIAN_DIGITS, ARABIC_INDIC_DIGITS * 2),
}
_ARABIC_LETTER = r"[ؠ-يٮ-ەۺ-ۿݐ-ݿ]"
# ZWNJ is only meaningful *between* two Arabic-script letters.
_ZWNJ_EDGE_RE = re.compile(rf"(?<!{_ARABIC_LETTER}){ZWNJ}+|{ZWNJ}+(?!{_ARABIC_LETTER})")
_ZWNJ_RUN_RE = re.compile(f"{ZWNJ}{{2,}}")
_ZWNJ_AFTER_NONJOINING_RE = re.compile(f"([{''.join(sorted(ARABIC_NON_JOINING))}]){ZWNJ}")


def _fold_presentation_forms(text: str) -> str:
    """Map Arabic presentation-form code points to their base letters."""
    if not any("ﭐ" <= ch <= "﷿" or "ﹰ" <= ch <= "﻿" for ch in text):
        return text
    return "".join(
        unicodedata.normalize("NFKC", ch)
        if ("ﭐ" <= ch <= "﷿" or "ﹰ" <= ch <= "﻾")
        else ch
        for ch in text
    )


def clean_zwnj(text: str) -> str:
    """Keep a ZWNJ only where it actually prevents two letters from joining."""
    text = text.replace(ZWJ, ZWNJ) if ZWJ in text else text
    text = _ZWNJ_RUN_RE.sub(ZWNJ, text)
    text = _ZWNJ_AFTER_NONJOINING_RE.sub(r"\1", text)
    return _ZWNJ_EDGE_RE.sub("", text)


@dataclass(frozen=True)
class NormalizeOptions:
    digits: DigitTarget = "keep"
    strip_urls: bool = True
    strip_emails: bool = True
    strip_mentions: bool = False
    strip_emoji: bool = True
    collapse_blank_lines: bool = True


def normalize_text(text: str, options: NormalizeOptions | None = None) -> str:
    """Apply the script-independent cleaning steps described in the module doc."""
    opt = options or NormalizeOptions()
    text = unicodedata.normalize("NFC", text)
    text = _fold_presentation_forms(text)
    text = text.translate(_DROP_BIDI)
    text = text.translate(_MICRO_TO_ZWNJ)
    text = clean_zwnj(text)
    if opt.strip_urls:
        text = URL_RE.sub(" ", text)
    if opt.strip_emails:
        text = EMAIL_RE.sub(" ", text)
    if opt.strip_mentions:
        text = MENTION_RE.sub(" ", text)
    if opt.strip_emoji:
        text = EMOJI_RE.sub(" ", text)
    if opt.digits != "keep":
        text = text.translate(_DIGITS[opt.digits])
    text = text.translate(_WIDE_TO_SPACE).replace("\r\n", "\n").replace("\r", "\n")
    text = HSPACE_RE.sub(" ", text)
    if opt.collapse_blank_lines:
        text = BLANK_LINES_RE.sub("\n", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()
