"""Central Kurdish (Sorani) orthography normalization.

Order of operations (each step documented in docs/07-ckb-orthography.md):

1. Shared cleaning (NFC, presentation forms, bidi marks, micro-spaces).
2. Legacy-encoding detection.  Texts typed before the Kurdish keyboard became
   common write the vowel ``ە`` as ``ه`` + ZWNJ (or a bare word-final ``ه``).
   If a text chunk contains *no* real ``ە`` but many ``ه``s at morpheme ends,
   it is treated as legacy and those ``ه``s are converted to ``ە``.
3. Character map: Arabic kaf/yeh -> Kurdish ک/ی, heh doachashmee -> ه,
   legacy small-v sequences -> ڕ ڵ ێ ۆ, teh marbuta -> ە ...
4. Contextual letter rules:
   * word-initial ``ر`` -> ``ڕ`` (Kurdish has no word-initial tap);
   * word-initial bare vowel letter -> ``ئ`` + vowel;
   * word-initial ``أ`` / ``إ`` / ``آ`` -> ``ئە`` / ``ئی`` / ``ئا``;
   * ``ەە`` -> ``ە``, ``ڕڕ`` -> ``ڕ``, ``ڵڵ`` -> ``ڵ``, ``ووو`` -> ``وو``.
5. Remove harakat and tatweel; normalise digits and punctuation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from ..shared_utils.normalizer import NormalizeOptions, clean_zwnj, normalize_text
from ..shared_utils.unicode_tables import (
    ARABIC_DIACRITICS,
    ARABIC_ONLY_LETTERS,
    CKB_CHAR_MAP,
    CKB_LETTERS,
    CKB_SEQUENCE_MAP,
    TATWEEL,
    ZWNJ,
)

_L = "ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ"  # canonical letters
_SEQ_RE = re.compile("|".join(map(re.escape, sorted(CKB_SEQUENCE_MAP, key=len, reverse=True))))
_CHAR_TABLE = str.maketrans(CKB_CHAR_MAP)
_DROP_MARKS = str.maketrans({c: None for c in ARABIC_DIACRITICS + TATWEEL})
_WORD_START = rf"(?<![{_L}‌])"
_INITIAL_R_RE = re.compile(_WORD_START + "ر")
_INITIAL_VOWEL_RE = re.compile(_WORD_START + "([اەێۆ])")
_INITIAL_ALEF_HAMZA = (
    (re.compile(_WORD_START + "آ"), "ئا"),
    (re.compile(_WORD_START + "أ"), "ئە"),
    (re.compile(_WORD_START + "إ"), "ئی"),
)
_SQUEEZE = ((re.compile("ە{2,}"), "ە"), (re.compile("ڕ{2,}|رڕ|ڕر"), "ڕ"), (re.compile("ڵ{2,}|لڵ|ڵل"), "ڵ"), (re.compile("و{3,}"), "وو"), (re.compile("ی{3,}"), "یی"))
_LEGACY_HEH_ZWNJ_RE = re.compile(f"ه{ZWNJ}")
_LEGACY_FINAL_HEH_RE = re.compile(rf"(?<=[{_L}])ه(?![{_L}‌])")
_PUNCT_TABLE = str.maketrans({",": "،", ";": "؛", "?": "؟", "٪": "%"})


def is_legacy_encoded(text: str) -> bool:
    """Heuristic: no U+06D5 at all, but heh+ZWNJ or many word-final hehs."""
    if "ە" in text:
        return text.count(f"ه{ZWNJ}") > text.count("ە")
    finals = len(_LEGACY_FINAL_HEH_RE.findall(text))
    return f"ه{ZWNJ}" in text or finals >= 3


@dataclass(frozen=True)
class CkbOrthographyOptions:
    digits: Literal["keep", "latin", "arabic-indic"] = "arabic-indic"
    kurdish_punctuation: bool = True
    legacy: Literal["auto", "yes", "no"] = "auto"
    fix_initial_r: bool = True
    add_initial_hamza: bool = True


def normalize(text: str, options: CkbOrthographyOptions | None = None) -> str:
    """Return *text* in standard Central Kurdish Unicode orthography."""
    opt = options or CkbOrthographyOptions()
    text = normalize_text(text, NormalizeOptions(digits=opt.digits))
    text = _SEQ_RE.sub(lambda m: CKB_SEQUENCE_MAP[m.group()], text)
    for rx, rep in _INITIAL_ALEF_HAMZA:
        text = rx.sub(rep, text)
    text = text.translate(_CHAR_TABLE)
    legacy = opt.legacy == "yes" or (opt.legacy == "auto" and is_legacy_encoded(text))
    # heh + ZWNJ is the legacy spelling of ae in every text, legacy or not.
    text = _LEGACY_HEH_ZWNJ_RE.sub("ە", text)
    if legacy:
        text = _LEGACY_FINAL_HEH_RE.sub("ە", text)
    text = text.translate(_DROP_MARKS)
    if opt.fix_initial_r:
        text = _INITIAL_R_RE.sub("ڕ", text)
    if opt.add_initial_hamza:
        text = _INITIAL_VOWEL_RE.sub(r"ئ\1", text)
    for rx, rep in _SQUEEZE:
        text = rx.sub(rep, text)
    if opt.kurdish_punctuation:
        text = text.translate(_PUNCT_TABLE)
    return clean_zwnj(text)


def normalize_word(word: str) -> str:
    """Normalize a single token (no punctuation/digit handling, no legacy guess)."""
    return normalize(word, CkbOrthographyOptions(digits="keep", kurdish_punctuation=False, legacy="no"))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_VALID_RE = re.compile(rf"^[{_L}]+(?:‌[{_L}]+)*$")
_ILLEGAL_SEQUENCES = (
    ("ەە", "double ae"),
    ("ئئ", "double hamza"),
    ("اا", "double alef"),
    ("ێێ", "double long e"),
    ("ۆۆ", "double long o"),
)


def validate_word(word: str) -> list[str]:
    """Return a list of problems ('' list = orthographically valid word)."""
    problems: list[str] = []
    if not word:
        return ["empty"]
    if any(ch in ARABIC_ONLY_LETTERS for ch in word):
        problems.append("arabic-only letter")
    if not _VALID_RE.match(word):
        bad = sorted({ch for ch in word if ch not in CKB_LETTERS and ch != ZWNJ})
        problems.append("non-Kurdish character(s): " + " ".join(f"U+{ord(c):04X}" for c in bad))
    for seq, why in _ILLEGAL_SEQUENCES:
        if seq in word:
            problems.append(why)
    if word[0] in "اەێۆ":
        problems.append("initial vowel without ئ")
    if word[0] == "ر":
        problems.append("initial ر should be ڕ")
    if "ئ" in word[1:] and not re.search("[اەێۆوی]ئ|ئ[اەێۆوی]", word):
        problems.append("medial hamza outside a vowel hiatus")
    if len(word) > 1 and word.endswith("ه") and word[-2] in "اەێۆ" and word.count("ە") == 0:
        problems.append("possible legacy heh for ae")
    return problems


# Pairs that unstandardised text confuses; used to propose respellings.
VARIANT_SWAPS: tuple[tuple[str, str], ...] = (
    ("ر", "ڕ"),
    ("ل", "ڵ"),
    ("ی", "ێ"),
    ("و", "ۆ"),
    ("و", "وو"),
    ("ه", "ە"),
)


def spelling_variants(word: str, max_variants: int = 64) -> list[str]:
    """Generate respellings of *word* by toggling confusable letters.

    Used by the lexicon builder: a corpus form that is unattested in the
    lexicon but has a frequent variant (e.g. ``گول`` vs ``گوڵ``) is merged
    into that variant.
    """
    variants = {word}
    for a, b in VARIANT_SWAPS:
        new: set[str] = set()
        for v in variants:
            for i in range(len(v)):
                if v.startswith(a, i) and not (a == "و" and b == "وو" and v.startswith("وو", i)):
                    new.add(v[:i] + b + v[i + len(a):])
                if v.startswith(b, i) and b != "وو":
                    new.add(v[:i] + a + v[i + len(b):])
        variants |= new
        if len(variants) > max_variants:
            break
    if "\u200c" in word:
        variants.add(word.replace("\u200c", ""))  # پێنج‌شەمە -> پێنجشەمە
    for i in range(1, len(word)):  # under-written gemination: شەمە -> شەممە
        if word[i] in "مننلت" and word[i - 1] in "ەاێۆ" and word[i:i + 1] != word[i + 1:i + 2]:
            variants.add(word[: i + 1] + word[i] + word[i + 1 :])
    variants.discard(word)
    return sorted(variants)[:max_variants]
