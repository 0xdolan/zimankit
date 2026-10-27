"""Northern Kurdish nominal and verbal morphology.

Nominal inflection fuses gender, number, definiteness and case into one
suffix slot (after an optional derivational suffix)::

    STEM [DERIV] [INFLECTION]
    jin          ekê        -> jinekê   "a woman" (oblique, feminine)

==============  =====================  =================  ===============
suffix          after vowel            meaning            gender evidence
==============  =====================  =================  ===============
-a              -ya                    ezafe sg           feminine
-ê              -yê                    ezafe sg | obl sg  m (ezafe) / f (obl)
-î              -yî                    oblique sg         masculine
-ên             -yên                   ezafe pl           -
-an             -yan                   oblique pl         -
-ek             -yek                   indefinite         -
-ekê            -yekê                  indef. oblique     feminine
-ekî            -yekî                  indef. oblique     masculine
-eke            -yeke                  indef. ezafe       -
-in / -inan     -                      indef. pl / obl    -
-o / -ino       -                      vocative m / pl    masculine / -
==============  =====================  =================  ===============

The suffix ``-ê`` is the classic ambiguity: *mala* "house-EZ.F" vs *malê*
"house-OBL.F", but *bavê* "father-EZ.M".  It is resolved with the lexicon's
gender (dictionary-wiki ``m``/``f`` tags), else both readings are returned.
"""

from __future__ import annotations

import math
from functools import lru_cache
from importlib import resources

from ..shared_utils.schema import Analysis, EmptyLexicon, LexiconLike
from .orthography import lower, normalize_word
from .verbs import FormIndex, default_index

VOWELS = set("aeêiîouû")

# (suffix, tag, features, needs: "C" | "V" | None)
INFLECTIONS: tuple[tuple[str, str, dict[str, str], str | None], ...] = (
    ("ekê", "INDEF.OBL.F", {"definite": "ind", "number": "sg", "case": "obl", "gender": "f"}, "C"),
    ("yekê", "INDEF.OBL.F", {"definite": "ind", "number": "sg", "case": "obl", "gender": "f"}, "V"),
    ("ekî", "INDEF.OBL.M", {"definite": "ind", "number": "sg", "case": "obl", "gender": "m"}, "C"),
    ("yekî", "INDEF.OBL.M", {"definite": "ind", "number": "sg", "case": "obl", "gender": "m"}, "V"),
    ("eke", "INDEF.EZ", {"definite": "ind", "number": "sg", "ezafe": "yes"}, "C"),
    ("yeke", "INDEF.EZ", {"definite": "ind", "number": "sg", "ezafe": "yes"}, "V"),
    ("inan", "INDEF.PL.OBL", {"definite": "ind", "number": "pl", "case": "obl"}, "C"),
    ("ine", "INDEF.PL.EZ", {"definite": "ind", "number": "pl", "ezafe": "yes"}, "C"),
    ("ek", "INDEF", {"definite": "ind", "number": "sg", "case": "dir"}, "C"),
    ("yek", "INDEF", {"definite": "ind", "number": "sg", "case": "dir"}, "V"),
    ("ino", "VOC.PL", {"number": "pl", "case": "voc"}, "C"),
    ("ên", "EZ.PL", {"definite": "def", "number": "pl", "ezafe": "yes"}, "C"),
    ("yên", "EZ.PL", {"definite": "def", "number": "pl", "ezafe": "yes"}, "V"),
    ("an", "OBL.PL", {"definite": "def", "number": "pl", "case": "obl"}, "C"),
    ("yan", "OBL.PL", {"definite": "def", "number": "pl", "case": "obl"}, "V"),
    ("a", "EZ.F", {"definite": "def", "number": "sg", "ezafe": "yes", "gender": "f"}, "C"),
    ("ya", "EZ.F", {"definite": "def", "number": "sg", "ezafe": "yes", "gender": "f"}, "V"),
    ("ê", "EZ.M|OBL.F", {"definite": "def", "number": "sg"}, "C"),
    ("yê", "EZ.M|OBL.F", {"definite": "def", "number": "sg"}, "V"),
    ("î", "OBL.M", {"definite": "def", "number": "sg", "case": "obl", "gender": "m"}, "C"),
    ("yî", "OBL.M", {"definite": "def", "number": "sg", "case": "obl", "gender": "m"}, "V"),
    ("o", "VOC.M", {"number": "sg", "case": "voc", "gender": "m"}, "C"),
    ("in", "INDEF.PL", {"definite": "ind", "number": "pl", "case": "dir"}, "C"),
)
DERIVATIONS: tuple[tuple[str, str, str], ...] = (
    ("ahî", "ABST", "NOUN"), ("tî", "ABST", "NOUN"), ("anî", "ABST", "NOUN"), ("î", "ABST|ADJZ", "NOUN"),
    ("dar", "POSSR", "ADJ"), ("van", "AGENT", "NOUN"), ("kar", "AGENT", "NOUN"), ("ger", "AGENT", "NOUN"),
    ("stan", "PLACE", "NOUN"), ("geh", "PLACE", "NOUN"), ("xane", "PLACE", "NOUN"), ("ane", "ADVZ", "ADV"),
    ("tir", "CMPR", "ADJ"), ("tirîn", "SUPL", "ADJ"), ("ok", "DIM", "NOUN"), ("ik", "DIM", "NOUN"),
)
POS_PRIORITY = ("VERB", "NOUN", "PROPN", "ADJ", "ADV", "PRON", "NUM", "ADP", "CCONJ", "SCONJ", "DET", "AUX", "PART", "INTJ")


@lru_cache(maxsize=1)
def function_words() -> dict[str, tuple[str, dict[str, str]]]:
    text = resources.files("zimankit.data").joinpath("kmr_function_words.tsv").read_text("utf-8")
    out: dict[str, tuple[str, dict[str, str]]] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = (line.split("\t") + ["", ""])[:3]
        feats = dict(kv.split("=", 1) for kv in cols[2].split("|") if "=" in kv)
        out.setdefault(cols[0], (cols[1], feats))
    return out


def _cond(stem: str, need: str | None) -> bool:
    if need is None or not stem:
        return bool(stem)
    v = stem[-1] in VOWELS
    return v if need == "V" else not v


class KmrAnalyzer:
    def __init__(self, lexicon: LexiconLike | None = None, verbs: FormIndex | None = None):
        self.lexicon = lexicon or EmptyLexicon()
        self.verbs = verbs or default_index()
        self.fw = function_words()

    def _stem_score(self, stem: str) -> float:
        if stem in self.fw:
            return 4.0
        if stem in self.lexicon:
            return 5.0 + math.log1p(self.lexicon.freq(stem)) / 4
        f = self.lexicon.freq(stem)
        return -3.0 + (math.log1p(f) / 3 if f else 0.0)

    @staticmethod
    def _affix_cost(form: str) -> float:
        return -0.4 + (0.9 if len(form) >= 3 else 0.4 if len(form) == 2 else -0.5)

    def _candidates(self, word: str) -> list[tuple[str, list[tuple[str, str]], dict[str, str], str | None]]:
        out = [(word, [], {}, None)]
        for suf, tag, feats, need in INFLECTIONS:
            if word.endswith(suf) and len(word) - len(suf) >= 2:
                stem = word[: -len(suf)]
                if _cond(stem, need):
                    out.append((stem, [(suf, tag)], dict(feats), "NOUN"))
                    for dsuf, dtag, dpos in DERIVATIONS:
                        if stem.endswith(dsuf) and len(stem) - len(dsuf) >= 2:
                            out.append((stem[: -len(dsuf)], [(dsuf, dtag), (suf, tag)], dict(feats), dpos))
        for dsuf, dtag, dpos in DERIVATIONS:
            if word.endswith(dsuf) and len(word) - len(dsuf) >= 2:
                out.append((word[: -len(dsuf)], [(dsuf, dtag)], {}, dpos))
        return out

    def _resolve_gender(self, stem: str, tag: str, feats: dict[str, str]) -> list[dict[str, str]]:
        """Split the -ê ambiguity using lexical gender."""
        g = self.lexicon.gender_of(stem)
        if g and "gender" not in feats:
            feats["gender"] = g
        if tag != "EZ.M|OBL.F":
            return [feats]
        if g == "f":
            return [{**feats, "case": "obl"}]
        if g == "m":
            return [{**feats, "ezafe": "yes"}]
        return [{**feats, "case": "obl", "gender": "f"}, {**feats, "ezafe": "yes", "gender": "m"}]

    def analyze(self, token: str, normalized: bool = False) -> list[Analysis]:
        word = lower(token) if normalized else normalize_word(token)
        if not word:
            return []
        results: list[Analysis] = []
        for vf in self.verbs.lookup(word):
            v = self.verbs.verbs.get(vf.lemma)
            feats = {k: str(x) for k, x in vf.features.items() if k != "pos"}
            if v is not None:
                feats["transitivity"] = "transitive" if v.transitive else "intransitive"
                feats["past_stem"] = v.past
                feats["present_stem"] = v.present
            score = (7.0 if v is None or v.source == "core" else 5.5) + math.log1p(self.lexicon.freq(word)) / 4
            if feats.get("form") == "infinitive":
                score += 0.2  # citation form beats the homographic 3pl past
            results.append(Analysis(word, vf.lemma, "VERB", feats, [(word, "VERB")], score))
        for stem, segs, feats, pos_hint in self._candidates(word):
            score = self._stem_score(stem) + sum(self._affix_cost(f) for f, _ in segs)
            known = self.lexicon.pos_of(stem) | ({self.fw[stem][0]} if stem in self.fw else set())
            if segs:
                known = known - {"VERB"}  # infinitive + case suffix = verbal noun (dîtina)
            g = self.lexicon.gender_of(stem)
            tag = segs[-1][1] if segs else ""
            if g and feats.get("gender") and feats["gender"] != g:
                score -= 2.0  # e.g. -a (feminine ezafe) on a masculine noun
            if pos_hint == "NOUN" and known and "NOUN" not in known and "PROPN" not in known and "ADJ" not in known:
                score -= 1.0
            pos = pos_hint if pos_hint and (not known or pos_hint in known) else next((p for p in POS_PRIORITY if p in known), pos_hint or "NOUN")
            if not segs and stem in self.fw:
                pos, extra = self.fw[stem]
                feats = {**feats, **extra}
            for fs in self._resolve_gender(stem, tag, feats):
                results.append(Analysis(word, stem, pos, fs, [(stem, "STEM")] + segs, round(score, 3)))
        best: dict[tuple, Analysis] = {}
        for a in results:
            key = (a.segmentation, a.pos, tuple(sorted(a.features.items())))
            if key not in best or a.score > best[key].score:
                best[key] = a
        return sorted(best.values(), key=lambda a: a.score, reverse=True)

    def best(self, token: str) -> Analysis | None:
        r = self.analyze(token)
        return r[0] if r else None

    def lemmatize(self, token: str) -> str:
        a = self.best(token)
        return a.lemma if a else token
