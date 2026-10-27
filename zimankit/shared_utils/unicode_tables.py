"""Code-point tables shared by every Kurdish skill.

Everything here is data, not logic: canonical letters, their code points, and
the confusable characters that real-world text uses instead of them.  Keeping
the tables in one module means the Python skills, the regex cookbook and the
cross-language examples can all be checked against a single source of truth.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Central Kurdish (Arabic-based script) - the 34-letter standard alphabet.
# Order follows the standard Kurdish alphabetical order.
# ---------------------------------------------------------------------------

CKB_ALPHABET: Final[tuple[tuple[str, str, str], ...]] = (
    # (letter, code point(s), name)
    ("ئ", "U+0626", "hamza carrier (glottal onset)"),
    ("ا", "U+0627", "alef - long a"),
    ("ب", "U+0628", "beh"),
    ("پ", "U+067E", "peh"),
    ("ت", "U+062A", "teh"),
    ("ج", "U+062C", "jeem"),
    ("چ", "U+0686", "tcheh"),
    ("ح", "U+062D", "hah - pharyngeal fricative"),
    ("خ", "U+062E", "khah"),
    ("د", "U+062F", "dal"),
    ("ر", "U+0631", "reh - tap r"),
    ("ڕ", "U+0695", "reh with small v below - trilled r"),
    ("ز", "U+0632", "zain"),
    ("ژ", "U+0698", "jeh"),
    ("س", "U+0633", "seen"),
    ("ش", "U+0634", "sheen"),
    ("ع", "U+0639", "ain - voiced pharyngeal"),
    ("غ", "U+063A", "ghain"),
    ("ف", "U+0641", "feh"),
    ("ڤ", "U+06A4", "veh"),
    ("ق", "U+0642", "qaf"),
    ("ک", "U+06A9", "keheh - Kurdish/Persian kaf"),
    ("گ", "U+06AF", "gaf"),
    ("ل", "U+0644", "lam - clear l"),
    ("ڵ", "U+06B5", "lam with small v - velarized l"),
    ("م", "U+0645", "meem"),
    ("ن", "U+0646", "noon"),
    ("ه", "U+0647", "heh - consonant h"),
    ("ە", "U+06D5", "ae - short vowel e/a"),
    ("و", "U+0648", "waw - w / u"),
    ("وو", "U+0648 U+0648", "double waw - long u"),
    ("ۆ", "U+06C6", "oe - long o"),
    ("ی", "U+06CC", "farsi yeh - y / long i"),
    ("ێ", "U+06CE", "yeh with small v - long e"),
)

CKB_LETTERS: Final[frozenset[str]] = frozenset(
    ch for letter, _, _ in CKB_ALPHABET for ch in letter
)
CKB_VOWEL_LETTERS: Final[frozenset[str]] = frozenset("اەۆێ")
CKB_SEMIVOWELS: Final[frozenset[str]] = frozenset("وی")
CKB_CONSONANT_LETTERS: Final[frozenset[str]] = CKB_LETTERS - CKB_VOWEL_LETTERS - CKB_SEMIVOWELS

# Letters that never join to the following letter.  A ZWNJ after any of them
# is redundant and is removed by the normalizer.
ARABIC_NON_JOINING: Final[frozenset[str]] = frozenset("ئادذرڕزژوۆەۊۋؤأإآة")
# Letters that do NOT occur in native Kurdish orthography (Arabic-only).
ARABIC_ONLY_LETTERS: Final[frozenset[str]] = frozenset("ثذصضطظةءأإؤى")

# Confusables -> canonical Central Kurdish letter.  Applied character by
# character after NFC, before any contextual rule.
CKB_CHAR_MAP: Final[dict[str, str]] = {
    "ي": "ی",  # ARABIC LETTER YEH
    "ى": "ی",  # ARABIC LETTER ALEF MAKSURA
    "ې": "ێ",  # ARABIC LETTER E (Pashto/Uyghur)
    "ك": "ک",  # ARABIC LETTER KAF
    "ڪ": "ک",  # ARABIC LETTER SWASH KAF
    "ھ": "ه",  # ARABIC LETTER HEH DOACHASHMEE
    "ہ": "ه",  # ARABIC LETTER HEH GOAL
    "ۀ": "ەی",  # HEH WITH YEH ABOVE (Persian ezafe ligature)
    "ة": "ە",  # TEH MARBUTA in loans -> ae
    "ڒ": "ڕ",  # REH WITH SMALL V (legacy fonts)
    "ڶ": "ڵ",  # LAM WITH SMALL V (variant)
    "ڷ": "ڵ",  # LAM WITH THREE DOTS ABOVE (legacy fonts)
    "ڨ": "ڤ",  # QAF WITH THREE DOTS ABOVE (legacy veh)
    "ۇ": "ۆ",  # ARABIC LETTER U - used for o by some keyboards
    "ۅ": "ۆ",  # KIRGHIZ OE
    "ٶ": "ئو",  # HIGH HAMZA WAW
    "ؤ": "ئو",  # WAW WITH HAMZA ABOVE
    "أ": "ئ",  # ALEF WITH HAMZA ABOVE (contextual rule may add a vowel)
    "إ": "ئ",  # ALEF WITH HAMZA BELOW
    "ء": "ئ",  # standalone HAMZA
}

# Base letter + combining mark sequences produced by old keyboard layouts.
CKB_SEQUENCE_MAP: Final[dict[str, str]] = {
    "یٔ": "ئ",
    "ئ": "ئ",
    "یٚ": "ێ",
    "ی̆": "ێ",
    "ی̂": "ێ",
    "وٚ": "ۆ",
    "و̆": "ۆ",
    "و̂": "ۆ",
    "رٚ": "ڕ",
    "ر̆": "ڕ",
    "ر̂": "ڕ",
    "لٚ": "ڵ",
    "ل̆": "ڵ",
    "ل̂": "ڵ",
}

# Harakat and other Arabic diacritics: never part of standard Kurdish spelling.
ARABIC_DIACRITICS: Final[str] = (
    "ًٌٍَُِّْٕٓٔ"
    "ٰٖٜٟٗ٘ٙٚٛٝٞ"
)
TATWEEL: Final[str] = "ـ"

# ---------------------------------------------------------------------------
# Spacing / control characters
# ---------------------------------------------------------------------------

ZWNJ: Final[str] = "‌"
ZWJ: Final[str] = "‍"
# "Micro spaces" that people type (or copy) inside words instead of ZWNJ.
MICRO_SPACES: Final[str] = "​     ­⁠﻿"
BIDI_CONTROLS: Final[str] = "‎‏‪‫‬‭‮⁦⁧⁨⁩؜"
WIDE_SPACES: Final[str] = "         　"

# ---------------------------------------------------------------------------
# Digits
# ---------------------------------------------------------------------------

LATIN_DIGITS: Final[str] = "0123456789"
ARABIC_INDIC_DIGITS: Final[str] = "٠١٢٣٤٥٦٧٨٩"  # U+0660..U+0669, standard for ckb
PERSIAN_DIGITS: Final[str] = "۰۱۲۳۴۵۶۷۸۹"  # U+06F0..U+06F9

# ---------------------------------------------------------------------------
# Northern Kurdish (Hawar Latin alphabet) - 31 letters.
# ---------------------------------------------------------------------------

KMR_ALPHABET: Final[tuple[tuple[str, str, str], ...]] = (
    ("a", "U+0061", "long open a"),
    ("b", "U+0062", "b"),
    ("c", "U+0063", "voiced affricate dʒ"),
    ("ç", "U+00E7", "voiceless affricate tʃ"),
    ("d", "U+0064", "d"),
    ("e", "U+0065", "short e ɛ"),
    ("ê", "U+00EA", "long e eː"),
    ("f", "U+0066", "f"),
    ("g", "U+0067", "g"),
    ("h", "U+0068", "h"),
    ("i", "U+0069", "short central i ɪ/ɨ"),
    ("î", "U+00EE", "long i iː"),
    ("j", "U+006A", "ʒ"),
    ("k", "U+006B", "k"),
    ("l", "U+006C", "l"),
    ("m", "U+006D", "m"),
    ("n", "U+006E", "n"),
    ("o", "U+006F", "long o oː"),
    ("p", "U+0070", "p"),
    ("q", "U+0071", "uvular q"),
    ("r", "U+0072", "tap r (rr = trill)"),
    ("s", "U+0073", "s"),
    ("ş", "U+015F", "ʃ"),
    ("t", "U+0074", "t"),
    ("u", "U+0075", "short u ʊ"),
    ("û", "U+00FB", "long u uː"),
    ("v", "U+0076", "v"),
    ("w", "U+0077", "w"),
    ("x", "U+0078", "velar fricative x"),
    ("y", "U+0079", "glide j"),
    ("z", "U+007A", "z"),
)
KMR_LETTERS: Final[frozenset[str]] = frozenset(letter for letter, _, _ in KMR_ALPHABET)
KMR_VOWELS: Final[frozenset[str]] = frozenset("aeêiîouû")
# Optional letters some writers add for Arabic sounds (not part of Hawar).
KMR_EXTENDED_LETTERS: Final[frozenset[str]] = frozenset("ḧẍ'")

# Look-alikes -> canonical Hawar letter.  Most come from Turkish, French or
# phone keyboards that lack the circumflex letters.
KMR_CHAR_MAP: Final[dict[str, str]] = {
    "ı": "i",  # Turkish dotless i
    "İ": "I",  # Turkish dotted capital I
    "é": "ê", "è": "ê", "ë": "ê", "ē": "ê", "ě": "ê",
    "É": "Ê", "È": "Ê", "Ë": "Ê", "Ē": "Ê",
    "í": "î", "ì": "î", "ï": "î", "ī": "î",
    "Í": "Î", "Ì": "Î", "Ï": "Î", "Ī": "Î",
    "ú": "û", "ù": "û", "ü": "û", "ū": "û",
    "Ú": "Û", "Ù": "Û", "Ü": "Û", "Ū": "Û",
    "ș": "ş", "Ș": "Ş", "š": "ş", "Š": "Ş",
    "č": "ç", "Č": "Ç",
    "ḥ": "ḧ", "Ḥ": "Ḧ",
    "ʼ": "'", "’": "'", "‘": "'", "`": "'", "´": "'", "ʻ": "'", "ʿ": "'", "ʾ": "'",
}
# Letters that indicate a non-Kurmanji (usually Turkish, German, etc.) token.
KMR_FOREIGN_LETTERS: Final[frozenset[str]] = frozenset("öÖäÄßñÑåÅøØæÆãõâÂôÔğĞ")
