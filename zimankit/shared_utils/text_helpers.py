"""String distances, script detection and the shared regex library.

The ``PATTERNS`` dictionary is the canonical regex cookbook: the docs
(``docs/17-regex-cookbook.md``) and every cross-language example are generated
from, or tested against, these exact strings.  They use only syntax that is
portable across PCRE2, ECMAScript (``u`` flag), .NET, Rust ``regex`` and Go
RE2: character classes with ``\\u`` escapes are spelled out as literal
characters so no engine-specific escape is needed.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Final, Literal

Script = Literal["arabic", "latin", "cyrillic", "mixed", "none"]

# ---------------------------------------------------------------------------
# Regex cookbook
# ---------------------------------------------------------------------------

CKB_LETTER_CLASS: Final[str] = "ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ"
KMR_LETTER_CLASS: Final[str] = "abcçdeêfghiîjklmnopqrsştuûvwxyzABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZ"

PATTERNS: Final[dict[str, str]] = {
    # --- whole-word validators -------------------------------------------
    "ckb_word": f"^[{CKB_LETTER_CLASS}]+(?:‌[{CKB_LETTER_CLASS}]+)*$",
    "kmr_word": f"^[{KMR_LETTER_CLASS}]+(?:'[{KMR_LETTER_CLASS}]+)?$",
    # --- finding tokens in running text ----------------------------------
    "ckb_token": f"[{CKB_LETTER_CLASS}]+(?:‌[{CKB_LETTER_CLASS}]+)*",
    "kmr_token": f"[{KMR_LETTER_CLASS}]+(?:'[{KMR_LETTER_CLASS}]+)?",
    # --- orthographic problems (Central Kurdish) -------------------------
    "ckb_arabic_kaf_yeh": "[كيى]",
    "ckb_legacy_heh_zwnj": "ه‌",
    "ckb_heh_doachashmee": "ھ",
    "ckb_initial_plain_r": f"(^|[^{CKB_LETTER_CLASS}‌])ر",
    "ckb_double_ae": "ەە+",
    "ckb_arabic_only_letters": "[ثذصضطظةءأإؤ]",
    # --- morphology (Central Kurdish) -------------------------------------
    "ckb_definite_suffix": "(?:ەکە|کە|ەکان|کان)$",
    "ckb_pronominal_enclitic": "(?:مان|تان|یان|م|ت|ی)$",
    "ckb_present_verb": "^(?:نا|نە|مە)?(?:دە|ئە)[^\\s]+(?:م|یت|ێت|ات|ین|ن)$",
    "ckb_infinitive": "(?:دن|تن|ین|ان|وون|اندن)$",
    # --- orthographic problems (Northern Kurdish) -------------------------
    "kmr_turkish_letters": "[ıİğĞöÖüÜ]",
    "kmr_wrong_circumflex": "[éèëēíìïīúùūÉÈËÍÌÏÚÙ]",
    # --- morphology (Northern Kurdish) ------------------------------------
    "kmr_oblique_suffix": "(?:ekê|ekî|yekê|yekî|ê|î|an|yan)$",
    "kmr_ezafe_suffix": "(?:a|ê|ên|ya|yê|yên|eke|ine)$",
    "kmr_present_verb": "^(?:di|na|ni)[a-zçêîşû]+(?:im|î|e|in)$",
    "kmr_infinitive": "(?:in|andin|în|ûn|an|n)$",
    "kmr_oblique_pronoun": "^(?:min|te|wî|wê|me|we|wan|vî|vê|van)$",
    "kmr_direct_pronoun": "^(?:ez|tu|ew|em|hûn|ev)$",
}

COMPILED: Final[dict[str, re.Pattern[str]]] = {name: re.compile(p) for name, p in PATTERNS.items()}

# ---------------------------------------------------------------------------
# Script detection
# ---------------------------------------------------------------------------


@lru_cache(maxsize=4096)
def char_script(ch: str) -> str:
    if ch == "‌":
        return "joiner"
    if not ch.isalpha():
        return "other"
    name = unicodedata.name(ch, "")
    if name.startswith("ARABIC"):
        return "arabic"
    if name.startswith("LATIN"):
        return "latin"
    if name.startswith("CYRILLIC"):
        return "cyrillic"
    return "other"


def detect_script(text: str) -> Script:
    """Return the dominant script of *text* (>= 80 % of its letters)."""
    counts = {"arabic": 0, "latin": 0, "cyrillic": 0}
    total = 0
    for ch in text:
        s = char_script(ch)
        if s in counts:
            counts[s] += 1
            total += 1
    if total == 0:
        return "none"
    best = max(counts, key=counts.__getitem__)
    return best if counts[best] / total >= 0.8 else "mixed"  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Edit distances
# ---------------------------------------------------------------------------


def levenshtein(a: str, b: str) -> int:
    """Classic Levenshtein distance (insert / delete / substitute = 1)."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def damerau_levenshtein(a: str, b: str) -> int:
    """Optimal-string-alignment distance: Levenshtein plus adjacent transposition."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = a[i - 1] != b[j - 1]
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[-1][-1]


# Pairs of letters that Kurdish writers confuse; substituting one for the other
# costs less than an arbitrary substitution.  Used for spelling-variant search.
CONFUSABLE_PAIRS: Final[frozenset[frozenset[str]]] = frozenset(
    frozenset(p)
    for p in (
        ("ر", "ڕ"), ("ل", "ڵ"), ("ی", "ێ"), ("و", "ۆ"), ("ە", "ه"), ("ک", "ك"), ("ی", "ي"),
        ("e", "ê"), ("i", "î"), ("u", "û"), ("s", "ş"), ("c", "ç"),
    )
)


def weighted_distance(a: str, b: str, confusable_cost: float = 0.3) -> float:
    """Levenshtein where confusable letter pairs cost ``confusable_cost``."""
    previous = [float(j) for j in range(len(b) + 1)]
    for i, ca in enumerate(a, 1):
        current = [float(i)]
        for j, cb in enumerate(b, 1):
            if ca == cb:
                sub = 0.0
            elif frozenset((ca, cb)) in CONFUSABLE_PAIRS:
                sub = confusable_cost
            else:
                sub = 1.0
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + sub))
        previous = current
    return previous[-1]
