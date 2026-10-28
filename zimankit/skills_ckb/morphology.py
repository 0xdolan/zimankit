"""Central Kurdish morphological analyzer.

Nominal template (left to right)::

    [PREP] STEM [DERIV] [CMP] [NUM/DEF] [ENCLITIC] [ADD] [POSTP]
            کتێب          ەکە        م
       لە   ماڵ           ەکان       مان       یش     دا   ->  لەماڵەکانمانیشدا

Each slot has allomorphs whose choice depends on whether the preceding
letter is a vowel letter (V) or a consonant letter (C):

=========  ============================  ===============================
slot       after C                       after V
=========  ============================  ===============================
DEF.SG     ەکە   پیاوەکە                 کە / یەکە  دەرگاکە، دێیەکە
DEF.PL     ەکان  پیاوەکان                کان / یەکان
INDEF      ێک    پیاوێک                  یەک  دەرگایەک
PL         ان    پیاوان                  یان  دەرگایان
ENCLITIC   م ت ی مان تان یان             same
ADD        یش                            ش
POSTP      ەوە، دا                        وە، دا
=========  ============================  ===============================

Analysis is *generate-and-rank*: every way of peeling suffixes off the right
edge (respecting slot order and allomorph conditions) is produced, then each
candidate is scored.  A stem found in the lexicon dominates; corpus
frequency of the bare stem is the tie-breaker; every peeled affix costs a
little, and a one-letter affix costs more unless the stem is known.  Verbs
are recognised by lookup in the paradigm index built by ``verbs.py``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Iterable

from ..shared_utils.schema import Analysis, EmptyLexicon, LexiconLike
from .orthography import normalize_word
from .verbs import FormIndex, default_index

VOWEL_LETTERS = set("اەۆێیو")


@dataclass(frozen=True)
class Affix:
    form: str
    tag: str
    features: tuple[tuple[str, str], ...]
    after: str | None = None  # "C", "V" or None (any)
    pos_hint: str | None = None


def _a(form: str, tag: str, after: str | None = None, pos: str | None = None, **feat: str) -> Affix:
    return Affix(form, tag, tuple(sorted(feat.items())), after, pos)


# Slots ordered from the OUTERMOST (rightmost) to the innermost.
SLOTS: tuple[tuple[str, tuple[Affix, ...]], ...] = (
    ("POSTP", (
        _a("ەوە", "POSTP.EWE", "C", postposition="ewe"),
        _a("وە", "POSTP.EWE", "V", postposition="ewe"),
        _a("دا", "POSTP.DA", None, postposition="da"),
        _a("ڕا", "POSTP.RA", None, postposition="ra"),
    )),
    ("ADD", (_a("یش", "ADD", "C", additive="yes"), _a("ش", "ADD", "V", additive="yes"))),
    ("ENCLITIC", (
        _a("مان", "1PL", None, enclitic="1pl"),
        _a("تان", "2PL", None, enclitic="2pl"),
        _a("یان", "3PL", None, enclitic="3pl"),
        _a("م", "1SG", None, enclitic="1sg"),
        _a("ت", "2SG", None, enclitic="2sg"),
        _a("ی", "3SG/EZ", None, enclitic="3sg|ezafe"),
    )),
    ("ADD2", (_a("ش", "ADD", "V", additive="yes"),)),
    ("NUMDEF", (
        _a("ەکان", "DEF.PL", "C", "NOUN", definite="def", number="pl"),
        _a("یەکان", "DEF.PL", "V", "NOUN", definite="def", number="pl"),
        _a("کان", "DEF.PL", "V", "NOUN", definite="def", number="pl"),
        _a("ەکە", "DEF.SG", "C", "NOUN", definite="def", number="sg"),
        _a("یەکە", "DEF.SG", "V", "NOUN", definite="def", number="sg"),
        _a("کە", "DEF.SG", "V", "NOUN", definite="def", number="sg"),
        _a("ێک", "INDEF", "C", "NOUN", definite="ind", number="sg"),
        _a("یەک", "INDEF", "V", "NOUN", definite="ind", number="sg"),
        _a("ان", "PL", "C", "NOUN", number="pl"),
        _a("یان", "PL", "V", "NOUN", number="pl"),
    )),
    ("CMP", (
        _a("ترین", "SUPL", None, "ADJ", degree="sup"),
        _a("تر", "CMPR", None, "ADJ", degree="cmp"),
    )),
    ("DERIV", (
        _a("ایەتی", "ABST", None, "NOUN", derivation="abstract"),
        _a("یەتی", "ABST", None, "NOUN", derivation="abstract"),
        _a("ێتی", "ABST", "C", "NOUN", derivation="abstract"),
        _a("انە", "ADVZ", None, "ADV", derivation="adverbial"),
        _a("ستان", "PLACE", None, "NOUN", derivation="place"),
        _a("کار", "AGENT", None, "NOUN", derivation="agent"),
        _a("دار", "POSSR", None, "ADJ", derivation="possessor"),
        _a("ی", "NISBA", "C", "ADJ", derivation="nisba|abstract"),
    )),
)
PROCLITICS = (("لە", "PREP.LE"), ("بە", "PREP.BE"), ("بۆ", "PREP.BO"))
POS_PRIORITY = ("VERB", "NOUN", "PROPN", "ADJ", "ADV", "PRON", "NUM", "ADP", "CCONJ", "SCONJ", "DET", "PART", "INTJ")


@lru_cache(maxsize=1)
def function_words() -> dict[str, tuple[str, dict[str, str]]]:
    text = resources.files("zimankit.data").joinpath("ckb_function_words.tsv").read_text("utf-8")
    out: dict[str, tuple[str, dict[str, str]]] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = (line.split("\t") + ["", ""])[:3]
        feats = dict(kv.split("=", 1) for kv in cols[2].split("|") if "=" in kv)
        out.setdefault(cols[0], (cols[1], feats))
    return out


def _ends_with_vowel(stem: str) -> bool:
    """Phonological, not orthographic: final و/ی after a vowel letter is a glide.

    پیاو /pjaːw/ and چای /tʃaːj/ end in consonants (-> پیاوەکە، چایەکە), while
    کوردی /kurdiː/ and دوو /duː/ end in vowels (-> کوردییەکە، دووەکە).
    """
    if not stem:
        return False
    last = stem[-1]
    if last in "اەۆێ":
        return True
    if last in "وی":
        if len(stem) >= 2 and stem[-2] == last:
            return True
        return not (len(stem) >= 2 and stem[-2] in "اەۆێ")
    return False


CLITICS = ("م", "ت", "ی", "مان", "تان", "یان")  # set 2: 1sg 2sg 3sg 1pl 2pl 3pl
PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")


def _after(stem: str, after_c: str, after_v: str) -> str:
    return stem + (after_v if _ends_with_vowel(stem) else after_c)


def decline(stem: str) -> list[tuple[str, str | None]]:
    """Generate the nominal forms of a Central Kurdish noun: ``[(cell, form), ...]``.

    The allomorphs are the ones the analyzer peels (SLOTS); after a vowel the
    definite suffix is کە, except after ی / ێ where a glide is written (ماسییەکە).
    """
    v = _ends_with_vowel(stem)
    glide = v and stem[-1] in "یێ"
    defsg = stem + ("یەکە" if glide else "کە" if v else "ەکە")
    defpl = stem + ("یەکان" if glide else "کان" if v else "ەکان")
    return [
        ("bare", stem),
        ("def.sg", defsg),
        ("def.pl", defpl),
        ("ind.sg", _after(stem, "ێک", "یەک")),
        ("pl", None if stem.endswith("ە") else _after(stem, "ان", "یان")),
        ("ezafe", stem + "ی"),
        ("dem", _after(stem, "ە", "یە")),  # ئەم / ئەو … ە
        ("ind.ezafe", _after(stem, "ێکی", "یەکی")),
        ("def.sg.add", defsg + "ش"),
        *((f"def.sg+{p}", defsg + c) for p, c in zip(PERSONS, CLITICS)),
        *((f"bare+{p}", stem + c) for p, c in zip(PERSONS, CLITICS)),
    ]


def _peel(word: str, slot: int, segs: list[tuple[str, str, Affix]], out: list) -> None:
    out.append((word, list(segs)))
    if len(out) > 400:
        return
    for i in range(slot, len(SLOTS)):
        name, affixes = SLOTS[i]
        if name == "ADD2" and any(a.tag == "ADD" for _, _, a in segs):
            continue
        for af in affixes:
            if not word.endswith(af.form):
                continue
            stem = word[: -len(af.form)]
            if len(stem.replace("‌", "")) < 2:
                continue
            if af.after == "C" and _ends_with_vowel(stem):
                continue
            if af.after == "V" and not _ends_with_vowel(stem):
                continue
            stem = stem.rstrip("‌")
            _peel(stem, i + 1, [(af.form, af.tag, af)] + segs, out)


class CkbAnalyzer:
    """Rank-ordered morphological analyses for Central Kurdish tokens."""

    def __init__(self, lexicon: LexiconLike | None = None, verbs: FormIndex | None = None):
        self.lexicon = lexicon or EmptyLexicon()
        self.verbs = verbs or default_index()
        self.fw = function_words()

    # -- scoring ----------------------------------------------------------
    def _stem_score(self, stem: str) -> float:
        if stem in self.fw:
            return 4.0
        if stem in self.lexicon:
            return 5.0 + math.log1p(self.lexicon.freq(stem)) / 4
        f = self.lexicon.freq(stem)
        return -3.0 + (math.log1p(f) / 3 if f else 0.0)

    def _nominal(self, word: str, prefix: list[tuple[str, str]]) -> list[Analysis]:
        cands: list = []
        _peel(word, 0, [], cands)
        results = []
        for stem, segs in cands:
            score = self._stem_score(stem)
            feats: dict[str, str] = {}
            pos_hint = None
            prev_slot = None
            for form, tag, af in segs:
                score -= 0.4 + (0.5 if len(form) == 1 and stem not in self.lexicon else 0.0)
                # Long affixes are rarely accidental string matches.
                score += 0.9 if len(form) >= 3 else 0.4 if len(form) == 2 else 0.0
                if len(form) == 1 and prev_slot == "NUMDEF":
                    score += 0.6  # ەکە+م, ەکان+ی: enclitic after a definite suffix
                prev_slot = next(n for n, afs in SLOTS if af in afs)
                if af.tag in ("NISBA", "ABST", "ADVZ") and stem not in self.lexicon:
                    score -= 1.5
                feats.update(dict(af.features))
                pos_hint = pos_hint or af.pos_hint
            pos = self._choose_pos(stem, pos_hint, inflected=bool(segs))
            if stem in self.fw and not segs:
                pos, extra = self.fw[stem]
                feats.update(extra)
            seg_list = prefix + [(stem, "STEM")] + [(f, t) for f, t, _ in segs]
            surface = "".join(p for p, _ in prefix) + word
            results.append(Analysis(surface, stem, pos, feats, seg_list, round(score - 0.3 * len(prefix), 3)))
        return results

    def _choose_pos(self, stem: str, hint: str | None, inflected: bool = False) -> str:
        known = self.lexicon.pos_of(stem)
        if inflected:
            known = known - {"VERB"}  # an infinitive with nominal suffixes is a verbal noun
        if stem in self.fw:
            known = known | {self.fw[stem][0]}
        if hint and (hint in known or not known):
            return hint
        for p in POS_PRIORITY:
            if p in known:
                return p
        return hint or "NOUN"

    def _verbal(self, word: str) -> list[Analysis]:
        out = []
        for vf in self.verbs.lookup(word):
            v = self.verbs.verbs.get(vf.lemma)
            score = (7.0 if v is None or v.source == "core" else 5.5) + math.log1p(self.lexicon.freq(word)) / 4
            feats = {k: str(val) for k, val in vf.features.items() if k != "pos"}
            if feats.get("form") == "infinitive":
                score += 0.2
            if v is not None:
                feats["transitivity"] = "transitive" if v.transitive else "intransitive"
            out.append(Analysis(word, vf.lemma, "VERB", feats, [(word, "VERB")], score))
        return out

    # -- public API -------------------------------------------------------
    def analyze(self, token: str, normalized: bool = False) -> list[Analysis]:
        word = token if normalized else normalize_word(token)
        if not word:
            return []
        results = self._verbal(word) + self._nominal(word, [])
        for pre, tag in PROCLITICS:
            rest = word[len(pre) :].lstrip("‌")
            if word.startswith(pre) and len(rest) >= 2 and word not in self.lexicon and word not in self.fw:
                results += [a for a in self._nominal(rest, [(pre, tag)]) if a.lemma in self.lexicon]
        best: dict[tuple[str, str], Analysis] = {}
        for a in results:
            key = (a.segmentation, a.pos)
            if key not in best or a.score > best[key].score:
                best[key] = a
        return sorted(best.values(), key=lambda a: a.score, reverse=True)

    def best(self, token: str) -> Analysis | None:
        res = self.analyze(token)
        return res[0] if res else None

    def lemmatize(self, token: str) -> str:
        a = self.best(token)
        return a.lemma if a else token

    def analyze_text(self, words: Iterable[str]) -> list[Analysis | None]:
        return [self.best(w) for w in words]


def split_enclitic(word: str) -> tuple[str, str | None]:
    """Detach a final pronominal enclitic (م ت ی مان تان یان), longest first."""
    for cl in ("مان", "تان", "یان", "م", "ت", "ی"):
        if word.endswith(cl) and len(word) - len(cl) >= 2:
            return word[: -len(cl)], cl
    return word, None


def split_definite(word: str) -> tuple[str, str | None]:
    """Detach a definiteness suffix (ەکان کان ەکە کە)."""
    for suf in ("ەکان", "یەکان", "کان", "ەکە", "یەکە", "کە"):
        if word.endswith(suf) and len(word) - len(suf) >= 2:
            stem = word[: -len(suf)]
            if suf.startswith("ە") or _ends_with_vowel(stem):
                return stem, suf
    return word, None
