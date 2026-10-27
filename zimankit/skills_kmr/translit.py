"""Kurmanji Latin -> Kurdish Arabic script (the Sorani-style orthography).

Rules: long vowels map to letters (a ا, ê ێ, î ی, o ۆ, û وو), short ``e`` to
``ە``, short ``u`` to ``و``; the short ``i`` is not written (bizroke) except
word-initially, where the hamza seat ``ئ`` carries it.  Every word-initial
vowel gets ``ئ``.  ``rr`` and word-initial ``r`` become ``ڕ``; ``ll`` becomes
``ڵ``.
"""

from __future__ import annotations

from .orthography import lower

MAP = {
    "a": "ا", "b": "ب", "c": "ج", "ç": "چ", "d": "د", "e": "ە", "ê": "ێ", "f": "ف", "g": "گ",
    "h": "ه", "i": "", "î": "ی", "j": "ژ", "k": "ک", "l": "ل", "m": "م", "n": "ن", "o": "ۆ",
    "p": "پ", "q": "ق", "r": "ر", "s": "س", "ş": "ش", "t": "ت", "u": "و", "û": "وو", "v": "ڤ",
    "w": "و", "x": "خ", "y": "ی", "z": "ز", "ḧ": "ح", "ẍ": "غ", "'": "ع",
}
VOWELS = set("aeêiîouû")


def to_arabic(word: str) -> str:
    w = lower(word)
    if w == "û":
        return "و"  # the conjunction "and"
    w = w[0] + w[1:].replace("'", "") if w else w  # inner apostrophe = suffix boundary
    out = []
    i = 0
    while i < len(w):
        ch = w[i]
        if i == 0 and ch in VOWELS:
            out.append("ئ" + ("" if ch == "i" else MAP[ch]))
            i += 1
            continue
        if ch == "r" and (i == 0 or w[i + 1 : i + 2] == "r"):
            out.append("ڕ")
            i += 2 if w[i + 1 : i + 2] == "r" else 1
            continue
        if ch == "l" and w[i + 1 : i + 2] == "l":
            out.append("ڵ")
            i += 2
            continue
        if ch in VOWELS and i > 0 and w[i - 1] in VOWELS and ch != "i":
            out.append("ئ" + MAP[ch])  # vowel hiatus is written with ئ
            i += 1
            continue
        out.append(MAP.get(ch, ch))
        i += 1
    s = "".join(out)
    return s.replace("ەە", "ە")


def text_to_arabic(text: str) -> str:
    from ..shared_utils.tokenizer import tokenize

    return " ".join(to_arabic(t.text) if t.kind == "word" else t.text for t in tokenize(text))
