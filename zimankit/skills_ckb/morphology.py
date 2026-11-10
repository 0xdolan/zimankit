"""Central Kurdish morphological analyzer.

Nominal template (left to right)::

    [PREP] STEM [DERIV] [CMP] [NUM/DEF] [ENCLITIC] [ADD] [POSTP] [ە/یە]
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
from .verbs import PREVERBS, VOWEL_END, FormIndex, Verb, VerbForm, _with_suffix, default_index

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
    ("COP", (
        # one word cannot decide among these functions; the next word and any ئەم/ئەو do
        _a("ە", "E", "C", copula="3sg|ezafe.def|dem|voc|def.short"),
        _a("ە", "E", "UU", copula="3sg|ezafe.def|dem|voc|def.short"),
        _a("یە", "E", "V", copula="3sg|dem"),
        # person endings only after -دا (من لە ماڵدام): elsewhere they are the enclitics
        _a("م", "COP.1SG", "DA", copula="1sg"),
        _a("یت", "COP.2SG", "DA", copula="2sg"),
        _a("ین", "COP.1PL", "DA", copula="1pl"),
        _a("ن", "COP.PL", "DA", copula="2pl|3pl"),
    )),
    ("POSTP", (
        _a("ەوە", "POSTP.EWE", "C", postposition="ewe"),
        _a("وە", "POSTP.EWE", "V", postposition="ewe"),
        _a("دا", "POSTP.DA", None, postposition="da"),
        _a("ێ", "POSTP.E", "C", postposition="e|indef"),  # لە تارانێ; also indefinite کوڕێ
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
    ("ADD2", (_a("ش", "ADD", "V", additive="yes"), _a("یش", "ADD", "C", additive="yes"))),
    ("NUMDEF", (
        _a("ەکان", "DEF.PL", "UU", "NOUN", definite="def", number="pl"),
        _a("ەکە", "DEF.SG", "UU", "NOUN", definite="def", number="sg"),
        _a("ێک", "INDEF", "UU", "NOUN", definite="ind", number="sg"),
        _a("ان", "PL", "UU", "NOUN", number="pl"),
        _a("ەکان", "DEF.PL", "C", "NOUN", definite="def", number="pl"),
        _a("یەکان", "DEF.PL", "V", "NOUN", definite="def", number="pl"),
        _a("کان", "DEF.PL", "V", "NOUN", definite="def", number="pl"),
        _a("ەکە", "DEF.SG", "C", "NOUN", definite="def", number="sg"),
        _a("یەکە", "DEF.SG", "V", "NOUN", definite="def", number="sg"),
        _a("کە", "DEF.SG", "V", "NOUN", definite="def", number="sg"),
        _a("ێک", "INDEF", "C", "NOUN", definite="ind", number="sg"),
        _a("یەک", "INDEF", "V", "NOUN", definite="ind", number="sg"),
        _a("یێک", "INDEF", "V", "NOUN", definite="ind", number="sg"),
        _a("ێکە", "DEF.SG", "C", "NOUN", definite="def", number="sg"),  # ماسێکە: the ی of ماسی contracts
        _a("ێکان", "DEF.PL", "C", "NOUN", definite="def", number="pl"),
        _a("ەک", "INDEF", "C", "NOUN", definite="ind", number="sg"),
        _a("ان", "PL", "C", "NOUN", number="pl"),
        _a("یان", "PL", "V", "NOUN", number="pl"),
        _a("گەل", "PL.GEL", None, "NOUN", number="pl"),
    )),
    ("PL0", (_a("ان", "PL", "C", "NOUN", number="pl"),)),  # کەس+ان+ێک
    ("CMP", (
        _a("ترین", "SUPL", None, "ADJ", degree="sup"),
        _a("تر", "CMPR", None, "ADJ", degree="cmp"),
        _a("ین", "ORD", "C", "ADJ", numtype="ord"),  # شەشەم+ین, only after an ordinal
    )),
    ("DERIV", (
        _a("ایەتی", "ABST", None, "NOUN", derivation="abstract"),
        _a("یەتی", "ABST", None, "NOUN", derivation="abstract"),
        _a("ێتی", "ABST", "C", "NOUN", derivation="abstract"),
        _a("انە", "ADVZ", None, "ADV", derivation="adverbial"),
        _a("انە", "PL+E", "C", "NOUN", number="pl", copula="dem"),  # ئەو پیاوانە
        _a("زانی", "SCIENCE", None, "NOUN", derivation="logy"),  # زیندەزانی
        _a("ناسی", "SCIENCE", None, "NOUN", derivation="nomy"),  # ئەستێرەناسی
        _a("خانە", "PLACE", None, "NOUN", derivation="place"),
        _a("گەر", "AGENT", None, "NOUN", derivation="agent"),  # ئاسنگەر
        _a("چی", "AGENT", None, "NOUN", derivation="agent"),  # ڕاوچی
        _a("وان", "AGENT", None, "NOUN", derivation="agent"),  # باخەوان
        _a("ساز", "AGENT", None, "NOUN", derivation="agent"),
        _a("مەند", "POSSR", None, "ADJ", derivation="possessor"),
        _a("ناک", "POSSR", None, "ADJ", derivation="possessor"),
        _a("ۆکە", "DIM", None, "NOUN", derivation="diminutive"),
        _a("ۆڵە", "DIM", None, "NOUN", derivation="diminutive"),
        _a("یلە", "DIM", None, "NOUN", derivation="diminutive"),
        _a("ستان", "PLACE", None, "NOUN", derivation="place"),
        _a("کار", "AGENT", None, "NOUN", derivation="agent"),
        _a("دار", "POSSR", None, "ADJ", derivation="possessor"),
        _a("ی", "NISBA", "C", "ADJ", derivation="nisba|abstract"),
        _a("یی", "NISBA", "V", "ADJ", derivation="nisba"),  # سنە+یی
        _a("ایی", "ABST", None, "NOUN", derivation="abstract"),  # ڕەش+ایی
    )),
)
PROCLITICS = (("لە", "PREP.LE"), ("بە", "PREP.BE"), ("بۆ", "PREP.BO"))
DERIV_PREFIXES = (("بێ", "PRIV"), ("نا", "NEG"), ("هاو", "CO"))  # بێکار, نادیار, هاوکار
INTERFIXES = ("ەو", "او", "بە", "ە", "و", "")  # compound linkers: گوڵ+ە+گەنم, دەم+و+چاو
FULL_SCORE_WORDS = frozenset({"تر", "دیکە", "برا"})  # they inflect like any other word: تریش, دیکەوە, براکەم
DERIVED_TAGS = ("NISBA", "ABST", "ADVZ", "PLACE", "AGENT", "POSSR", "SCIENCE", "DIM")
ADDITIVE_TAILS = frozenset({"", "م", "ت", "ی", "مان", "تان", "یان", "یت", "ین", "ن", "ە", "مە", "یتە", "ینە", "نە"})  # after verb-internal یش
CLITIC_ADPOSITIONS = frozenset({"پێ", "لێ", "تێ", "بۆ"})  # پێم, لێی, بۆمان
ENCLITIC_TAGS = frozenset({"1SG", "2SG", "3SG/EZ", "1PL", "2PL", "3PL"})
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
    uu = stem.endswith("وو")  # وو takes the consonant endings: خانووەکە, خانووێک, خانووان
    v = _ends_with_vowel(stem) and not uu
    glide = v and stem[-1] in "یێ"
    defsg = stem + ("یەکە" if glide else "کە" if v else "ەکە")
    defpl = stem + ("یەکان" if glide else "کان" if v else "ەکان")
    after = (lambda c, _: stem + c) if uu else (lambda c, vv: _after(stem, c, vv))
    return [
        ("bare", stem),
        ("def.sg", defsg),
        ("def.pl", defpl),
        ("ind.sg", after("ێک", "یەک")),
        ("pl", None if stem.endswith("ە") else after("ان", "یان")),
        ("ezafe", stem + "ی"),
        ("dem", after("ە", "یە")),  # ئەم / ئەو … ە
        ("ind.ezafe", after("ێکی", "یەکی")),
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
            if af.after == "UU" and not stem.endswith("وو"):
                continue
            if af.after == "DA" and (not stem.endswith("دا") or len(stem) < 5):
                continue  # ماڵ+دا+م, not سە+دا+م
            if af.after == "C" and _ends_with_vowel(stem):
                continue
            if af.after == "V" and not _ends_with_vowel(stem):
                continue
            stem = stem.rstrip("‌")
            _peel(stem, i + 1, [(af.form, af.tag, af)] + segs, out)


def lemma_seg(word: str, lemma: str, segs: list) -> str:
    """The stem as written in *word*: the lemma may have recovered a letter the surface form lacks."""
    return word[: len(word) - sum(len(f) for f, _, _ in segs)] if segs else lemma


def _verb_head(prefix: str) -> bool:
    """Can *prefix* stand before the marker دە?  Nothing, a preverb, نە and one clitic: نەی+دە, هەڵم+دە."""
    for pre in ("", *PREVERBS):
        if prefix.startswith(pre):
            rest = prefix[len(pre) :]
            if rest in ("", "نە", *CLITICS) or any(rest in ("نە" + c, c + "نە") for c in CLITICS):
                return True
    return False


def _without_b(form: str) -> list[str]:
    """*form* less a leading subjunctive ب; a clitic after it goes back to the end: بمکرد -> کردم."""
    if not form.startswith("ب") or len(form) < 4:
        return []
    out = [form[1:]]
    for c in sorted(CLITICS, key=len, reverse=True):
        if form.startswith(c, 1) and len(form) > len(c) + 3:
            out.append(form[1 + len(c) :] + c)
    return out


class CkbAnalyzer:
    """Rank-ordered morphological analyses for Central Kurdish tokens."""

    def __init__(self, lexicon: LexiconLike | None = None, verbs: FormIndex | None = None):
        self.lexicon = lexicon or EmptyLexicon()
        self.verbs = verbs or default_index()
        self.fw = function_words()

    # -- scoring ----------------------------------------------------------
    def _ordinal(self, stem: str) -> bool:
        """شەش+ەم, سێ+یەم: a cardinal numeral with the ordinal ending."""
        if self.fw.get(stem, ("", {}))[1].get("numtype") == "ord":
            return True
        for suf in ("یەم", "ەم"):
            base = stem[: -len(suf)]
            if stem.endswith(suf) and base and (suf == "ەم" or _ends_with_vowel(base)):
                if self.fw.get(base, ("",))[0] == "NUM" or "NUM" in self.lexicon.pos_of(base):
                    return True
        return False

    def _stem_score(self, stem: str) -> float:
        if self._ordinal(stem):  # above the accidental readings: دەیەم is "tenth" before "my decade"
            return 8.0
        if stem in self.fw and stem not in FULL_SCORE_WORDS:
            return 4.0
        if stem in self.lexicon:
            return 5.0 + math.log1p(self.lexicon.freq(stem)) / 4
        if stem in self.fw:
            return 4.0
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
                if af.tag in ("NISBA", "ABST", "ADVZ", "SCIENCE", "DIM") and stem not in self.lexicon:
                    score -= 1.5
                if af.form in ("گەر", "چی", "وان", "ساز", "مەند", "ناک", "خانە") and stem not in self.lexicon:
                    score -= 3.0  # short and easily accidental
                if af.tag in ("AGENT", "POSSR", "DIM", "SCIENCE") and af.form != "کار" and af.form != "دار" and len(stem) < 3:
                    score -= 12.0  # سە+یلە+م is not a diminutive
                if af.form in ("ێکە", "ێکان") and stem + "ی" not in self.lexicon:
                    score -= 12.0  # پیاوێکە is پیاو+ێک+ە
                if af.tag in DERIVED_TAGS and stem in self.fw:
                    score -= 6.0  # بێ+کار is the prefix, not a preposition with an agent suffix
                inner = stem + "".join(s[0] for s in segs[: segs.index((form, tag, af)) + 1])
                if prev_slot in ("DERIV", "PL0") and inner in self.lexicon:
                    score -= 3.0  # a listed word stays whole: کوردستان+ە, not کورد+ستان+ە
                if inner in self.fw and stem not in self.fw:
                    score -= 3.0  # هەندێک+یش, not هەند+ێک+یش
                if af.form in ("ێ", "ەک"):
                    score -= 1.5 if stem in self.lexicon else 3.5  # short and easily accidental: لە+سێ, not لەس+ێ
                if af.form == "ەک" and af is not segs[-1][2]:
                    score -= 6.0  # final only: سەرەک+ی, not سەر+ەک+ی
                if af.form == "یی" and stem.endswith("ا"):
                    score -= 12.0  # after ا it is ایی or a listed word: کۆتایی; یی follows ە ۆ ێ: سنەیی, شنۆیی
                if af.form == "ایی" and "ADJ" not in self.lexicon.pos_of(stem):
                    score -= 12.0  # ڕەش+ایی, not کۆت+ایی
                if af.tag == "ORD" and not (af is segs[0][2] and self._ordinal(stem)):
                    score -= 12.0  # ین makes the attributive ordinal only: شەشەمین ساڵ
                if af.tag == "PL.GEL" and stem in self.fw:
                    score -= 6.0  # a typo for لەگەڵ, not لە+گەل
                if af.tag == "E" and (word in self.lexicon or word in self.fw):
                    score -= 3.0  # a listed word stays whole
                if (af.tag == "E" or af.tag.startswith("COP")) and (self.verbs.lookup(word) or self.verbs.lookup(word[: -len(form)])):
                    score -= 12.0  # a verb is a verb: بووە, کردە, نیشاندام
                feats.update(dict(af.features))
                pos_hint = pos_hint or af.pos_hint
            # the listed word behind a changed stem: ماس+ێکە is ماسی, پەنجەر+ان is پەنجەرە
            if any(f in ("ێکە", "ێکان") for f, _, _ in segs) and stem + "ی" in self.lexicon:
                stem += "ی"
            elif stem not in self.lexicon and stem + "ە" in self.lexicon and any(t == "PL" for _, t, _ in segs):
                score += self._stem_score(stem + "ە") - self._stem_score(stem)
                stem += "ە"
            pos = self._choose_pos(stem, pos_hint, inflected=bool(segs))
            if self._ordinal(stem):
                pos = "ADJ"
                feats.setdefault("numtype", "ord")
            if stem in self.fw and not segs:
                pos, extra = self.fw[stem]
                feats.update(extra)
            elif stem in CLITIC_ADPOSITIONS and all(t in ENCLITIC_TAGS for _, t, _ in segs):
                pos = "ADP"
                feats["adptype"] = "bare"
                score += 5.0
            seg_list = prefix + [(lemma_seg(word, stem, segs), "STEM")] + [(f, t) for f, t, _ in segs]
            surface = "".join(p for p, _ in prefix) + word
            results.append(Analysis(surface, stem, pos, feats, seg_list, round(score - 0.3 * len(prefix), 3)))
        return results

    def _manner(self, word: str) -> list[Analysis]:
        """بە+خێرا+یی, بە+جوان+ی: the adverbs of manner, when the middle is a known word."""
        out = []
        if word.startswith("بە"):
            for end in ("یی", "ی"):
                stem = word[2 : -len(end)]
                if word.endswith(end) and len(stem) >= 3 and self.lexicon.pos_of(stem) & {"ADJ", "NOUN"}:
                    segs = [("بە", "CONFIX.BE"), (stem, "STEM"), (end, "CONFIX.Y")]
                    out.append(Analysis(word, stem, "ADV", {"derivation": "manner"}, segs, self._stem_score(stem) - 0.3))
        return out

    def _stacked_adposition(self, word: str) -> list[Analysis]:
        """Two clitics on one adposition: بۆ+م+ی (بۆمی نووسی "he wrote to me")."""
        out = []
        for host in CLITIC_ADPOSITIONS:
            rest = word[len(host) :]
            if word.startswith(host):
                for first in CLITICS:
                    if rest.startswith(first) and rest[len(first) :] in CLITICS:
                        second = rest[len(first) :]
                        out.append(Analysis(word, host, "ADP", {"adptype": "bare"}, [(host, "STEM"), (first, "CLITIC"), (second, "CLITIC")], 8.0))
        return out

    def _prefixed(self, word: str) -> list[Analysis]:
        """بێ+کار, ها+و: only when the remainder is a known word."""
        out = []
        for pre, tag in DERIV_PREFIXES:
            rest = word[len(pre) :]
            if word.startswith(pre) and len(rest) >= 2 and rest in self.lexicon:
                out.append(Analysis(word, word, "ADJ", {"derivation": tag.lower()}, [(pre, tag), (rest, "STEM")], self._stem_score(rest) - 0.3))
        return out

    def _compound(self, word: str) -> list[Analysis]:
        """Two known content words, with or without a linker.  Scored below any known or function stem."""
        out = []
        for i in range(2, len(word) - 1):
            left = word[:i]
            if left not in self.lexicon or left in self.fw:
                continue
            for link in INTERFIXES:
                right = word[i + len(link) :]
                if word.startswith(link, i) and len(right) >= 2 and right in self.lexicon and right not in self.fw:
                    segs = [(left, "STEM")] + ([(link, "LINK")] if link else []) + [(right, "STEM")]
                    out.append(Analysis(word, word, "NOUN", {"compound": link or "zero"}, segs, 3.0))
        return out

    def _choose_pos(self, stem: str, hint: str | None, inflected: bool = False) -> str:
        if stem in self.fw and self.fw[stem][0] in ("PRON", "DET", "NUM"):
            return self.fw[stem][0]  # ئەوانە+ی stays a pronoun
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

    def _object_clitic(self, word: str) -> list[tuple[VerbForm, str]]:
        """Forms with a pronoun object: دەتبینم, هەڵیدەگرم, بمگرە, بینیمیت, گرتمی, بردینیان.

        They multiply the paradigm by six, so they are recognised by stripping the object and looking
        the rest up, not listed.  A reading needs a transitive verb, and a first or second person
        object must differ from the subject.
        """
        found: list[tuple[VerbForm, str]] = []

        def transitive(form: str, core_only: bool = False) -> list[VerbForm]:
            verbs = ((f, self.verbs.verbs[f.lemma]) for f in self.verbs.lookup(form))
            return [f for f, v in verbs if v.transitive and (v.source == "core" or not core_only)]

        def add(form: str, obj: str, ok, core_only: bool = False) -> None:
            for f in transitive(form, core_only):
                # "I see me" needs خۆ; only a third person can differ from a subject of the same person
                if ok(f.features) and (obj.startswith("3") or obj not in str(f.features.get("person", f.features.get("agent")))):
                    found.append((f, obj))

        def present(ft: dict, clitic: str) -> bool:
            if ft.get("mood") == "imperative":
                return clitic not in ("ت", "تان")  # no "see yourself" order
            return ft.get("tense") == "present" and "voice" not in ft and "person" in ft

        def past(ft: dict) -> bool:
            return ft.get("tense") == "past" and ft.get("aspect") == "perfective" and "polarity" not in ft and "voice" not in ft

        def fronted_agent(ft: dict) -> bool:
            """The agent clitic stands before the stem, so any agent may be followed by a patient ending."""
            if ft.get("agent") not in PERSONS or "voice" in ft or "mood" in ft:
                return False
            if ft.get("tense") == "past_perfect":
                return ft.get("polarity") == "neg"  # نەیانبینیبوو+م
            return ft.get("tense") == "past" and (ft.get("polarity") == "neg" or ft.get("aspect") == "progressive")

        def final_agent(ft: dict) -> bool:
            return (ft.get("tense") in ("present_perfect", "past_perfect", "past_subj", "pluperfect_subj") and "polarity" not in ft
                    and "voice" not in ft and ft.get("agent") in ("1sg", "2sg", "1pl", "2pl"))

        for cl, obj in zip(CLITICS, PERSONS):
            # دە+ت+بینم, بم+گرە, and on a preverb هەڵ+ی+دەگرم, ڕا+م+بهێنە
            for head in ("دە", "نا", "ب", "نە", "مە", *PREVERBS):
                rest = word[len(head + cl) :]
                if word.startswith(head + cl) and len(rest) >= 2:
                    # a short remainder is too easily another word on a guessed verb: دەیلی
                    add(head + rest, obj, lambda ft, c=cl: present(ft, c), core_only=len(rest) < 4)
        for end, obj in (("یت", "2sg"), ("م", "1sg"), ("ین", "1pl"), ("یان", "3pl"), ("ن", "2pl|3pl")):  # بینیم+یت, ڕامهێنا+یت
            if word.endswith(end) and len(word) > len(end) + 2:
                # core verbs only: on guessed ones these match other words (بریتین, بریتانی, درامی)
                add(word[: -len(end)], obj, lambda ft: past(ft) and ft.get("agent") in ("1sg", "2sg", "1pl", "2pl"), core_only=True)
        # the same endings in the other past tenses (the patient slot of Ahmadi 2021, Table 1)
        for end, obj in (("یت", "2sg"), ("م", "1sg"), ("ین", "1pl"), ("ن", "2pl|3pl")):
            if word.endswith(end) and len(word) > len(end) + 3:
                rest = word[: -len(end)]
                add(rest, obj, fronted_agent, core_only=True)  # نەمدەکرد+ن, دەیانکرد+ین
                add(rest, obj, lambda ft: final_agent(ft) and ft.get("tense") != "present_perfect", core_only=True)  # بینیبووم+ن, کردبام+ن
                add(rest + "ە", obj, lambda ft: final_agent(ft) and ft.get("tense") == "present_perfect", core_only=True)  # کردووم+ن
        for agent, cl3 in (("3sg", "ی"), ("3pl", "یان")):  # گرت+م+ی, برد+ین+یان
            if word.endswith(cl3):
                bare = word[: -len(cl3)]
                for end, obj in (("مان", "1pl"), ("تان", "2pl"), ("م", "1sg"), ("ت", "2sg"), ("ین", "1pl"), ("یت", "2sg")):
                    if bare.endswith(end) and len(bare) > len(end) + 1:
                        for f in transitive(bare[: -len(end)], core_only=True):
                            if past(f.features) and f.features.get("agent") == "external":
                                found.append((VerbForm(f.form, f.lemma, {**f.features, "agent": agent}), obj))
        return found

    def _rewrites(self, word: str) -> list[tuple[str, dict[str, str], object, bool]]:
        """Ways to take one productive element off a verb form: (shorter form, features, test, core verbs only).

        These elements multiply every paradigm cell, so they are stripped and never listed.  The inventory
        is the verb template of Ahmadi (2021, Table 1): the additive یش inside the verb, the directional ە,
        the particle ەوە, the conditional ایە, and the marker ئە for دە (Ahmadi et al. 2024, Table 4).
        """
        out: list[tuple[str, dict[str, str], object, bool]] = []

        def finite(ft: dict, v: Verb) -> bool:
            return "person" in ft or "agent" in ft

        i = word.find("ئە")  # ئەچم, ئەیکەم, نەیئەکرد, هەڵئەگرم
        if i >= 0 and _verb_head(word[:i]):
            out.append((word[:i] + "دە" + word[i + 2 :], {"variant": "dialect_ae"}, finite, True))
        # ەوە on a verb the list has without it: دەیخۆمەوە, خواردیانەوە, کڕیومەتەوە, بیخۆرەوە
        for cut in (2, 3, 4):
            base, tail = word[:-cut], word[-cut:]
            if len(base) < 3 or not tail.endswith("وە"):
                continue
            if _with_suffix(base, "ەوە") == word:
                out.append((base, {"particle": "ewe"}, lambda ft, v: finite(ft, v) and not v.suffix and "goal" not in ft and ft.get("tense") != "present_perfect", False))
            elif tail == "تەوە" and base.endswith("ە"):
                out.append((base, {"particle": "ewe"}, lambda ft, v: not v.suffix and ft.get("tense") == "present_perfect", False))
            elif tail == "رەوە" and base[-1] in "ەۆێ":
                out.append((base, {"particle": "ewe"}, lambda ft, v: not v.suffix and ft.get("mood") == "imperative", False))
        # regional shapes of ەوە (Ahmadi et al. 2024, Table 4): ەوانێ in Sulaymaniyah, ەو in Sanandaj
        if word.endswith("ەوانێ"):
            out.append((word[:-5] + "ەوە", {"particle_variant": "ewanê"}, finite, False))
        elif word.endswith("ەو") and len(word) >= 5:
            out.append((word + "ە", {"particle_variant": "ew"}, finite, False))
        # directional ە: دەچمە, هاتنە, هاتیتە; تە after the perfect: هاتوومەتە
        if word.endswith("ە") and word[-2] not in VOWEL_END:
            out.append((word[:-1], {"goal": "yes"}, lambda ft, v: finite(ft, v) and "goal" not in ft and ft.get("tense") != "present_perfect", True))
        if word.endswith("ەتە"):
            out.append((word[:-2], {"goal": "yes"}, lambda ft, v: ft.get("tense") == "present_perfect", True))
        # conditional ایە on the past: بکردایە, بهاتمایە, بمکردایە, نەهاتایە, کردبووایە
        base = word[:-3] if word.endswith("ایە") else word[:-2] if word.endswith("ایە"[1:]) and word[-3:-2] == "ا" else ""
        if len(base) >= 2:
            def conditional(ft: dict, v: Verb) -> bool:
                return ft.get("tense") in ("past", "past_perfect") and ft.get("aspect") != "progressive" and "mood" not in ft and "goal" not in ft
            for b in (base, *_without_b(base)):
                out.append((b, {"mood": "conditional"}, conditional, False))
        # ب before the past subjunctive: بهاتبام, بمکردبا
        for b in _without_b(word):
            out.append((b, {}, lambda ft, v: ft.get("tense") in ("past_subj", "pluperfect_subj") and "polarity" not in ft, False))
        # additive یش / ش: after the first element (نەشیکرد, هەڵیشیدەگرت) or before the ending (هاتیشم, کردمیش).
        # The first element must then be what it looks like: بشارین is not ب+ش+بارین.
        heads = {len(h): h for h in ("دە", "نە", "نا", "مە", "ئە", "ب", *PREVERBS) if word.startswith(h)}

        def after(head: str | None):
            def test(ft: dict, v: Verb) -> bool:
                if not finite(ft, v) or head in ("دە", "ئە", None):
                    return finite(ft, v)
                if head in PREVERBS:
                    return v.preverb == head
                if head == "ب":
                    return "polarity" not in ft and ft.get("mood") in ("subjunctive", "imperative")
                return ft.get("polarity") == "neg"
            return test

        for k in range(1, len(word)):
            for mark, fits in (("یش", word[k - 1] not in "اەۆێ" and k > 1), ("ش", word[k - 1] in VOWEL_END or k == 1)):
                tail = word[k + len(mark) :]
                if word[: k + len(mark)] in self.lexicon:
                    continue  # نەخۆش+ن is the adjective
                if word.startswith(mark, k) and fits and (k in heads or tail in ADDITIVE_TAILS):
                    out.append((word[:k] + tail, {"additive": "yes"}, after(heads.get(k)), True))
        return [r for r in out if len(r[0]) >= 3]

    def _verb_fallback(self, word: str, depth: int = 0) -> list[tuple[VerbForm, str | None, dict[str, str]]]:
        """Readings of *word* as a listed form plus up to three of the elements in ``_rewrites``."""
        found: list[tuple[VerbForm, str | None, dict[str, str]]] = []
        for shorter, extra, test, core_only in self._rewrites(word):
            def ok(f: VerbForm) -> bool:
                v = self.verbs.verbs[f.lemma]
                return f.lemma not in self.fw and test(f.features, v) and (v.source == "core" or not core_only)
            listed = self.verbs.lookup(shorter)
            if not listed and (shorter in self.lexicon or shorter in self.fw):
                continue  # a known word with a clitic is the nominal analysis: هێشتا+یە, داخەوە+ش
            direct = [(f, None) for f in listed] + self._object_clitic(shorter)
            hits = [(f, obj, extra) for f, obj in direct if ok(f)]
            if not hits and depth < 2:
                hits = [(f, obj, {**more, **extra}) for f, obj, more in self._verb_fallback(shorter, depth + 1) if ok(f) and extra.keys().isdisjoint(more)
                        and not ("particle" in extra and "goal" in more)]  # دەچمەوە is not دەچمە + وە
            found += hits
        return found

    def _verbal(self, word: str) -> list[Analysis]:
        out = []
        if not self.verbs.lookup(word) and word not in self.lexicon and word not in self.fw:
            for vf, obj in self._object_clitic(word):
                feats = {k: str(val) for k, val in vf.features.items() if k != "pos"}
                score = 6.0 if self.verbs.verbs[vf.lemma].source == "core" else 4.5
                out.append(Analysis(word, vf.lemma, "VERB", {**feats, "object": obj, "transitivity": "transitive"}, [(word, "VERB")], score))
        if not out and len(word) >= 4 and not self.verbs.lookup(word) and word not in self.lexicon and word not in self.fw:
            for vf, obj, extra in self._verb_fallback(word):
                v = self.verbs.verbs[vf.lemma]
                lemma = vf.lemma
                if extra.get("particle") == "ewe" and lemma + "ەوە" in self.verbs.verbs:
                    lemma += "ەوە"  # خواردنەوە is its own verb where the list has it
                feats = {k: str(val) for k, val in vf.features.items() if k != "pos"} | extra
                if obj:
                    feats["object"] = obj
                feats["transitivity"] = "transitive" if v.transitive else "intransitive"
                # the one-letter additive is the weakest evidence: a known word with a clitic outranks it (نەخۆش+ن)
                score = 4.3 if "additive" in extra else 6.0 if v.source == "core" else 4.5
                out.append(Analysis(word, lemma, "VERB", feats, [(word, "VERB")], score))
        for vf in self.verbs.lookup(word):
            if vf.lemma in self.fw:
                continue  # a verb guessed from a function word: یان
            v = self.verbs.verbs.get(vf.lemma)
            score = (7.0 if v is None or v.source == "core" else 5.5) + math.log1p(self.lexicon.freq(word)) / 4
            if word in self.fw and (vf.features.get("variant") or self.fw[word][0] == "NOUN"):
                score -= 4.0  # بێ the adposition, برا "brother"
            rivals = {f.lemma for f in self.verbs.lookup(word)} - {vf.lemma}
            if v is not None and v.light and rivals and vf.features.get("agent") not in (None, "external"):
                score -= 0.5  # a listed verb wins: دیاریکرد is دیاریکردن, not دیار+ی+کرد
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
        if word not in self.lexicon and word not in self.fw and not self.verbs.lookup(word):
            results += self._prefixed(word) + self._compound(word) + self._stacked_adposition(word) + self._manner(word)
        best: dict[tuple[str, str], Analysis] = {}
        for a in results:
            key = (a.segmentation, a.gloss, a.pos)
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
