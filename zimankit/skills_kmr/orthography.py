"""Northern Kurdish (Kurmanji) orthography in the Hawar Latin alphabet.

Steps (docs/11-kmr-orthography.md):

1. Shared cleaning (NFC, bidi marks, spaces).  NFC already fuses
   ``e + U+0302`` into ``ê`` and ``s + U+0327`` into ``ş``.
2. Look-alike folding: Turkish ``ı``/``İ``, acute/grave/diaeresis/macron
   vowels typed instead of the circumflex (``é`` -> ``ê``, ``ü`` -> ``û``),
   Romanian ``ș``, Czech ``š``/``č``, every apostrophe variant -> ``'``.
3. Casing: Kurdish-aware lower/upper (``I`` <-> ``i``, ``Î`` <-> ``î``; never
   the Turkish dotted/dotless mapping).
4. Digraphs are kept as written but *recognised* by the phonology:
   ``xw`` (labialised /xʷ/), ``rr`` (trill), ``ll`` (velarised l in some
   writers), ``ḧ``/``ẍ`` and the apostrophe (``'`` = /ʕ/, or after p/t/k/ç
   the unaspirated stop in phonetic spelling).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..shared_utils.normalizer import NormalizeOptions, normalize_text
from ..shared_utils.unicode_tables import KMR_CHAR_MAP, KMR_FOREIGN_LETTERS, KMR_LETTERS

_CHAR_TABLE = str.maketrans(KMR_CHAR_MAP)
_LOWER = str.maketrans({"İ": "i", "I": "i", "Î": "î", "Ê": "ê", "Û": "û", "Ş": "ş", "Ç": "ç"})
_UPPER = str.maketrans({"i": "I", "î": "Î", "ê": "Ê", "û": "Û", "ş": "Ş", "ç": "Ç"})
# An apostrophe survives between letters (HDP'yê) and word-initially before a
# vowel, where it spells /ʕ/ ('erd, 'Ezîz); anything else is a quote mark.
_APOS_EDGE_RE = re.compile(r"(?<![A-Za-zÀ-ɏ])'(?![aeêiîouûAEÊIÎOUÛ])|'(?![A-Za-zÀ-ɏ])")
_VALID_RE = re.compile(r"^[a-zçêîşû]+(?:'[a-zçêîşû]+)?$")
DIGRAPHS = ("xw", "rr", "ll", "ḧ", "ẍ")


def lower(text: str) -> str:
    """Kurdish lowercase (avoids the Turkish İ/ı behaviour of str.lower)."""
    return text.translate(_LOWER).lower()


def upper(text: str) -> str:
    return text.translate(_UPPER).upper()


@dataclass(frozen=True)
class KmrOrthographyOptions:
    lowercase: bool = False
    keep_apostrophe: bool = True  # HDP'yê ; False -> HDPyê


def normalize(text: str, options: KmrOrthographyOptions | None = None) -> str:
    opt = options or KmrOrthographyOptions()
    text = normalize_text(text, NormalizeOptions(digits="latin"))
    text = text.translate(_CHAR_TABLE)
    text = _APOS_EDGE_RE.sub("", text) if "'" in text else text
    if not opt.keep_apostrophe:
        text = text.replace("'", "")
    if opt.lowercase:
        text = lower(text)
    return text


def normalize_word(word: str, lowercase: bool = True) -> str:
    return normalize(word, KmrOrthographyOptions(lowercase=lowercase))


def validate_word(word: str) -> list[str]:
    """Problems with a (lower-cased) Kurmanji word; empty list = valid."""
    problems: list[str] = []
    if not word:
        return ["empty"]
    w = lower(word)
    foreign = sorted({c for c in w if c in KMR_FOREIGN_LETTERS})
    if foreign:
        problems.append("foreign letter(s): " + "".join(foreign))
    if not _VALID_RE.match(w):
        bad = sorted({c for c in w if c not in KMR_LETTERS and c != "'"})
        if bad:
            problems.append("non-Hawar character(s): " + "".join(bad))
    if re.search(r"(.)\1\1", w):
        problems.append("tripled letter")
    if re.search(r"[aeêiîouû]{3,}", w):
        problems.append("three vowels in a row")
    if re.search(r"[bcçdfghjklmnpqrsştvxzw]{4,}", w):
        problems.append("four consonants in a row")
    if not re.search(r"[aeêiîouû]", w) and len(w) > 2:
        problems.append("no vowel")
    if re.search(r"(?:^|[^aeêiîouû])(?:ee|êê|îî|ûû)", w):
        problems.append("doubled vowel")
    return problems
