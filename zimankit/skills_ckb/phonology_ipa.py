"""Central Kurdish grapheme-to-phoneme conversion (Arabic script -> IPA).

The converter works in three passes:

1. **Grapheme parse** - the word is split into graphemes; ``وو`` and ``یی``
   are kept together because they can be one long vowel.
2. **Semivowel resolution** - ``و`` and ``ی`` are each either a consonant
   (/w/, /j/) or a vowel (/u/, /uː/, /iː/).  The decision is purely
   contextual (see ``_resolve``):

   =================  =============================  =========================
   context            و                              ی
   =================  =============================  =========================
   word = "و"         /u/ (conjunction "and")        -
   after a vowel      /w/  ئاو  /ʔaːw/               /j/  چای /tʃaːj/
   before a vowel     /w/  خواردن /xwaːrdɯn/          /j/  پیاو /pjaːw/
   C _ C or C _ #     /u/  کورد /kurd/               /iː/ میر /miːr/
   doubled وو / یی    /uː/ (+ glide before a vowel)  /iː/ (+ /j/ before vowel)
   =================  =============================  =========================

3. **Bizroke repair** - the unwritten short vowel is re-inserted by
   ``shared_utils.phonology_core.break_clusters``; by default it is rendered
   as ``(ɯ)`` so a reader can see that it was inferred, not written.

The same segment list feeds IPA, Kurdish-Latin transliteration and
syllabification, so the three can never disagree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..shared_utils.phonology_core import Segment, break_clusters, syllabify
from .orthography import normalize_word

CONSONANTS: Final[dict[str, str]] = {
    "ئ": "ʔ", "ب": "b", "پ": "p", "ت": "t", "ج": "dʒ", "چ": "tʃ", "ح": "ħ", "خ": "x",
    "د": "d", "ر": "ɾ", "ڕ": "r", "ز": "z", "ژ": "ʒ", "س": "s", "ش": "ʃ", "ع": "ʕ",
    "غ": "ɣ", "ف": "f", "ڤ": "v", "ق": "q", "ک": "k", "گ": "ɡ", "ل": "l", "ڵ": "ɫ",
    "م": "m", "ن": "n", "ه": "h",
}
VOWELS: Final[dict[str, str]] = {"ا": "aː", "ە": "æ", "ێ": "eː", "ۆ": "oː"}

# IPA -> Kurdish Latin (Hawar-compatible) for transliteration
IPA_TO_LATIN: Final[dict[str, str]] = {
    "ʔ": "", "b": "b", "p": "p", "t": "t", "dʒ": "c", "tʃ": "ç", "ħ": "ḧ", "x": "x",
    "d": "d", "ɾ": "r", "r": "rr", "z": "z", "ʒ": "j", "s": "s", "ʃ": "ş", "ʕ": "'",
    "ɣ": "ẍ", "f": "f", "v": "v", "q": "q", "k": "k", "ɡ": "g", "l": "l", "ɫ": "ll",
    "m": "m", "n": "n", "h": "h", "w": "w", "j": "y",
    "aː": "a", "æ": "e", "eː": "ê", "oː": "o", "u": "u", "uː": "û", "iː": "î", "ɯ": "i",
}


@dataclass(frozen=True)
class G2POptions:
    epenthetic: str = "ɯ"  # symbol for the bizroke vowel
    mark_epenthesis: bool = True  # wrap inferred vowels in parentheses
    glottal_onset: bool = True  # render word-initial ئ as ʔ
    hiatus_glides: bool = True  # uː+V -> uːwV, iː+V -> iːjV
    syllable_dots: bool = False


def _graphemes(word: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(word):
        ch = word[i]
        if ch == "‌":
            i += 1
            continue
        if ch in "وی" and i + 1 < len(word) and word[i + 1] == ch:
            out.append(ch * 2)
            i += 2
            continue
        out.append(ch)
        i += 1
    return out


def _is_vowel_letter(g: str | None) -> bool:
    return g is not None and g in VOWELS


def _resolve(graphemes: list[str]) -> list[Segment]:
    """Turn graphemes into phoneme segments, resolving و / ی by context."""
    segs: list[Segment] = []
    n = len(graphemes)
    if graphemes == ["و"]:
        return [("u", "V")]
    for i, g in enumerate(graphemes):
        prev_seg = segs[-1] if segs else None
        prev_is_vowel = prev_seg is not None and prev_seg[1] == "V"
        nxt = graphemes[i + 1] if i + 1 < n else None
        next_is_vowel = _is_vowel_letter(nxt)
        if g in VOWELS:
            segs.append((VOWELS[g], "V"))
        elif g in CONSONANTS:
            sym = CONSONANTS[g]
            if g == "ر" and i == 0:
                sym = "r"
            segs.append((sym, "C"))
        elif g == "وو":
            if prev_is_vowel:
                segs.extend([("w", "C"), ("uː", "V")])
            else:
                segs.append(("uː", "V"))
        elif g == "یی":
            if prev_is_vowel:
                segs.extend([("j", "C"), ("iː", "V")])
            else:
                segs.append(("iː", "V"))
        elif g == "و":
            if i == 0 or prev_is_vowel or next_is_vowel:
                segs.append(("w", "C"))
            else:
                segs.append(("u", "V"))
        elif g == "ی":
            if i == 0:
                segs.append(("j", "C") if (next_is_vowel or nxt in ("و", "وو")) else ("iː", "V"))
            elif prev_is_vowel or next_is_vowel:
                segs.append(("j", "C"))
            else:
                segs.append(("iː", "V"))
        # anything else (digits, foreign letters) is silently skipped
    return segs


def _hiatus(segs: list[Segment]) -> list[Segment]:
    out: list[Segment] = []
    for i, s in enumerate(segs):
        out.append(s)
        if i + 1 < len(segs) and s[1] == "V" and segs[i + 1][1] == "V":
            if s[0] in ("uː", "u"):
                out.append(("w", "C"))
            elif s[0] in ("iː",):
                out.append(("j", "C"))
    return out


def segments(word: str, options: G2POptions | None = None, normalized: bool = False) -> list[Segment]:
    """Phoneme segments for *word*, with epenthetic vowels marked kind 'E'."""
    opt = options or G2POptions()
    w = word if normalized else normalize_word(word)
    graphemes = _graphemes(w)
    # Word-initial ئ + consonant: the hamza itself spells the bizroke (ئنجا).
    lead: list[Segment] = []
    if len(graphemes) > 1 and graphemes[0] == "ئ" and graphemes[1] in CONSONANTS:
        lead = [("ʔ", "C"), (opt.epenthetic, "E")]
        graphemes = graphemes[1:]
    segs = _resolve(graphemes)
    if opt.hiatus_glides:
        segs = _hiatus(segs)
    if lead:
        segs = lead + segs
        repaired = segs[:2] + break_clusters([("", "V")] + segs[2:], opt.epenthetic)[1:]
    else:
        repaired = break_clusters(segs, opt.epenthetic)
    if not opt.glottal_onset and repaired and repaired[0] == ("ʔ", "C"):
        repaired = repaired[1:]
    return repaired


def _render(seg: Segment, opt: G2POptions) -> str:
    sym, kind = seg
    if kind == "E" and opt.mark_epenthesis:
        return f"({sym})"
    return sym


def to_ipa(word: str, options: G2POptions | None = None, slashes: bool = False) -> str:
    """Broad phonemic IPA for a Central Kurdish word."""
    opt = options or G2POptions()
    segs = segments(word, opt)
    if opt.syllable_dots:
        body = ".".join("".join(_render(s, opt) for s in syl) for syl in syllabify(segs))
    else:
        body = "".join(_render(s, opt) for s in segs)
    return f"/{body}/" if slashes else body


def syllables(word: str) -> list[str]:
    """Syllables in IPA (epenthetic vowel unmarked)."""
    opt = G2POptions(mark_epenthesis=False)
    return ["".join(s for s, _ in syl) for syl in syllabify(segments(word, opt))]


LATIN_STYLES: Final[dict[str, dict[str, str]]] = {
    "hawar": {},  # rr / ll, as in the table above
    "accented": {"r": "ř", "ɫ": "ł"},  # single-letter style seen in some Sorani-Latin texts
}


def to_latin(word: str, style: str = "hawar") -> str:
    """Kurdish-Latin transliteration; the bizroke is written as ``i``.

    The word-initial trill is written ``r`` (it is always a trill there),
    hiatus glides are written (``hatuwe``, ``masîyeke``).
    """
    overrides = LATIN_STYLES[style]
    segs = segments(word, G2POptions(mark_epenthesis=False))
    out = []
    for i, (sym, _) in enumerate(segs):
        if sym == "ʔ":
            out.append("" if i == 0 else "'")
        elif sym == "r" and i == 0:
            out.append("r")
        else:
            out.append(overrides.get(sym, IPA_TO_LATIN.get(sym, sym)))
    return "".join(out)


def text_to_ipa(text: str, options: G2POptions | None = None) -> str:
    from ..shared_utils.tokenizer import tokenize

    return " ".join(to_ipa(t.text, options) if t.kind == "word" else t.text for t in tokenize(text))
