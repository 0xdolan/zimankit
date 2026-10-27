"""Northern Kurdish (Kurmanji) Latin -> IPA.

Hawar spelling is close to phonemic, so the work is mostly in the details:

* **Vowel length**: ``a ê î o û`` are long (/aː eː iː oː uː/), ``e i u`` short
  (/ɛ ɪ ʊ/).  The short high vowel ``i`` is rendered [ɪ] in roots and as the
  reduced vowel [ɯ] in the final closed syllable of a polysyllabic word
  (mostly the suffix *-in*: ``dîtin`` /diːtɯn/), matching the convention used
  for the Central Kurdish bizroke.  Configure with ``reduced_suffix_i``.
* **Rhotics**: word-initial ``r`` and written ``rr`` are the trill /r/,
  any other ``r`` is the tap /ɾ/.
* **xw**: the labialised fricative /xʷ/ (``xwe``, ``xwarin``).
* **Aspiration**: Hawar does not write the aspirated/unaspirated contrast of
  p t k ç.  In *narrow* mode plain letters are aspirated ([pʰ]) and a
  following apostrophe marks the unaspirated (ejective-like) member, the
  convention of phonetic dictionaries: ``p'ir`` -> [pɪɾ].
* **Extended letters**: ``ḧ`` /ħ/, ``ẍ`` /ɣ/, word-initial or post-vowel
  apostrophe /ʕ/ (``'erd`` -> /ʕɛɾd/).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..shared_utils.phonology_core import Segment, syllabify
from .orthography import lower, normalize_word

VOWELS: Final[dict[str, str]] = {
    "a": "aː", "e": "ɛ", "ê": "eː", "i": "ɪ", "î": "iː", "o": "oː", "u": "ʊ", "û": "uː",
}
CONSONANTS: Final[dict[str, str]] = {
    "b": "b", "c": "dʒ", "ç": "tʃ", "d": "d", "f": "f", "g": "ɡ", "h": "h", "j": "ʒ",
    "k": "k", "l": "l", "m": "m", "n": "n", "p": "p", "q": "q", "r": "ɾ", "s": "s",
    "ş": "ʃ", "t": "t", "v": "v", "w": "w", "x": "x", "y": "j", "z": "z",
    "ḧ": "ħ", "ẍ": "ɣ",
}
ASPIRABLE: Final[frozenset[str]] = frozenset("ptkç")


@dataclass(frozen=True)
class KmrG2POptions:
    narrow: bool = False  # aspiration, ŋ before velars, ɫ for ll
    reduced_suffix_i: bool = True
    reduced_symbol: str = "ɯ"
    syllable_dots: bool = False


def segments(word: str, options: KmrG2POptions | None = None, normalized: bool = False) -> list[Segment]:
    opt = options or KmrG2POptions()
    w = lower(word) if normalized else normalize_word(word)
    segs: list[Segment] = []
    i = 0
    while i < len(w):
        ch = w[i]
        nxt = w[i + 1] if i + 1 < len(w) else ""
        if ch == "x" and nxt == "w":
            segs.append(("xʷ", "C"))
            i += 2
            continue
        if ch == "r" and nxt == "r":
            segs.append(("r", "C"))
            i += 2
            continue
        if ch == "l" and nxt == "l" and opt.narrow:
            segs.append(("ɫ", "C"))
            i += 2
            continue
        if ch == "'":
            if i == 0:
                segs.append(("ʕ", "C"))  # 'erd
            elif opt.narrow and w[i - 1] in ASPIRABLE:
                segs[-1] = (segs[-1][0], "C*")  # p' t' k' ç' = unaspirated
            # otherwise a morpheme boundary (HDP'ê) - not pronounced
            i += 1
            continue
        if ch in VOWELS:
            segs.append((VOWELS[ch], "V"))
        elif ch in CONSONANTS:
            sym = CONSONANTS[ch]
            if ch == "r" and i == 0:
                sym = "r"
            segs.append((sym, "C"))
        i += 1
    # reduced suffix vowel: last vowel is short i, in a closed final syllable
    vowel_idx = [k for k, (_, kind) in enumerate(segs) if kind == "V"]
    if opt.reduced_suffix_i and len(vowel_idx) >= 2:
        last = vowel_idx[-1]
        if segs[last][0] == "ɪ" and last < len(segs) - 1 and all(k != "V" for _, k in segs[last + 1 :]):
            segs[last] = (opt.reduced_symbol, "V")
    if opt.narrow:
        out: list[Segment] = []
        for k, (sym, kind) in enumerate(segs):
            if kind == "C" and sym in ("p", "t", "k", "tʃ"):
                sym = sym + "ʰ"
            if sym == "n" and k + 1 < len(segs) and segs[k + 1][0] in ("k", "kʰ", "ɡ", "q"):
                sym = "ŋ"
            out.append((sym, "C" if kind == "C*" else kind))
        segs = out
    else:
        segs = [(s, "C" if k == "C*" else k) for s, k in segs]
    return segs


def to_ipa(word: str, options: KmrG2POptions | None = None, slashes: bool = False) -> str:
    opt = options or KmrG2POptions()
    segs = segments(word, opt)
    if opt.syllable_dots:
        body = ".".join("".join(s for s, _ in syl) for syl in syllabify(segs))
    else:
        body = "".join(s for s, _ in segs)
    if opt.narrow:
        return f"[{body}]" if slashes else body
    return f"/{body}/" if slashes else body


def syllables(word: str) -> list[str]:
    return ["".join(s for s, _ in syl) for syl in syllabify(segments(word))]


def text_to_ipa(text: str, options: KmrG2POptions | None = None) -> str:
    from ..shared_utils.tokenizer import tokenize

    return " ".join(to_ipa(t.text, options) if t.kind == "word" else t.text for t in tokenize(text))
