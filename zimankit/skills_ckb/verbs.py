"""Central Kurdish verb lexicon and paradigm generator.

A Sorani verb is fully described by its infinitive, past stem, present stem,
transitivity, optional preverb (هەڵ، دا، ڕا ...) and optional ``ەوە``
suffix.  From these the generator produces every single-word form:

* present indicative / negative / subjunctive         (دەکەم، ناکەم، بکەم)
* imperative / prohibitive                            (بکە، بکەن، مەکە)
* simple past, with agent clitics if transitive       (هاتم / کردم)
* past progressive                                     (دەهاتم / دەمکرد)
* present perfect, past perfect                        (هاتووە، کردبووم)
* passive present / past / perfect                     (دەکرێت، کرا، کراوە)
* infinitive and participles                           (کردن، کردوو، کراو)

Transitive verbs are *ergative* in the past: the person marker is an
enclitic pronoun (set 2: م ت ی مان تان یان) that agrees with the agent,
while intransitive verbs take the verbal endings (set 1: م یت - ین ن ن).

``FormIndex`` inverts the paradigms (surface form -> analyses) and is what
``morphology.analyze`` uses to recognise verbs.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from importlib import resources
from typing import Iterable, Iterator

PERSONS = ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")
SET2 = {"1sg": "م", "2sg": "ت", "3sg": "ی", "1pl": "مان", "2pl": "تان", "3pl": "یان"}
PREVERBS = ("هەڵ", "وەر", "دەر", "دا", "ڕا", "تێ", "پێ", "لێ")
VOWEL_END = "اەۆێیو"

# Irregular cells that no rule produces.
IRREGULAR: dict[str, dict[tuple[str, str], str]] = {
    "هاتن": {
        **{("present", p): "د" + f for p, f in zip(PERSONS, ("ێم", "ێیت", "ێت", "ێین", "ێن", "ێن"))},
        **{("present_neg", p): "نا" + f for p, f in zip(PERSONS, ("یەم", "یەیت", "یەت", "یەین", "یەن", "یەن"))},
        **{("subjunctive_neg", p): "نە" + f for p, f in zip(PERSONS, ("یەم", "یەیت", "یەت", "یەین", "یەن", "یەن"))},
        **{("subjunctive", p): "ب" + f for p, f in zip(PERSONS, ("ێم", "ێیت", "ێت", "ێین", "ێن", "ێن"))},
        ("imperative", "2sg"): "وەرە",
        ("imperative", "2pl"): "وەرن",
    },
    "چوون": {("imperative", "2sg"): "بڕۆ", ("imperative", "2pl"): "بڕۆن"},
}


@dataclass(frozen=True)
class Verb:
    infinitive: str
    past: str
    present: str
    transitive: bool
    preverb: str = ""
    suffix: str = ""  # "ەوە" for verbs like کردنەوە
    source: str = "core"
    light: bool = False  # noun/adjective + light verb (بەکارهێنان): keeps subjunctive ب

    @property
    def base_infinitive(self) -> str:
        inf = self.infinitive
        if self.suffix and inf.endswith(self.suffix):
            inf = inf[: -len(self.suffix)]
        if self.preverb and inf.startswith(self.preverb):
            inf = inf[len(self.preverb) :]
        return inf


@dataclass(frozen=True)
class VerbForm:
    form: str
    lemma: str
    features: dict = field(hash=False, compare=False)


# ---------------------------------------------------------------------------
# Loading and guessing
# ---------------------------------------------------------------------------


def load_core_verbs() -> list[Verb]:
    text = resources.files("zimankit.data").joinpath("ckb_verbs_core.tsv").read_text("utf-8")
    verbs = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = (line.split("\t") + ["", "", "", "", "", ""])[:6]
        inf, past, pres, tr, pre = (c.strip() for c in cols[:5])
        verbs.append(Verb(inf, past, pres, tr == "T", pre, "ەوە" if inf.endswith("ەوە") else ""))
    return verbs


def past_stem_of(infinitive: str) -> str | None:
    """Past stem = infinitive minus the final ن (کردن -> کرد, چوون -> چوو)."""
    inf = infinitive[:-3] if infinitive.endswith("ەوە") else infinitive
    if len(inf) >= 3 and inf.endswith("ن") and inf[-2] in "دتیاو":
        return inf[:-1]
    return None


def guess_present_stem(past: str) -> str:
    """Rule-of-thumb present stem for verbs missing from the reference list."""
    if past.endswith("اند"):
        return past[:-3] + "ێن"  # causative شکاند -> شکێن
    if past.endswith("ارد"):
        return past[:-3] + "ێر"  # نارد -> نێر
    if past.endswith("ا"):
        return past[:-1]  # ترسا -> ترس  (also covers -ێ stems in 3sg)
    if past.endswith("ی"):
        return past[:-1]  # نووسی -> نووس
    if past.endswith(("شت", "ست")):
        return past[:-1]  # فرۆشت -> فرۆش
    if past.endswith(("ت", "د")):
        return past[:-1]  # کەوت -> کەو, مرد -> مر
    if past.endswith("وو"):
        return past[:-2]
    return past


def make_verb(infinitive: str, transitive: bool | None = None, present: str | None = None,
              source: str = "guess", known: dict[str, Verb] | None = None) -> Verb | None:
    """Build a Verb for any infinitive, decomposing preverbs and -ەوە."""
    known = known or {}
    if infinitive in known:
        return known[infinitive]
    suffix = "ەوە" if infinitive.endswith("نەوە") else ""
    core = infinitive[:-3] if suffix else infinitive
    for pre in PREVERBS:
        rest = core[len(pre) :]
        if core.startswith(pre) and rest in known:
            base = known[rest]
            return Verb(infinitive, base.past, base.present, base.transitive if transitive is None else transitive,
                        pre, suffix, source)
    if suffix and core in known:
        base = known[core]
        return Verb(infinitive, base.past, base.present, base.transitive, "", suffix, source)
    # compound written solid: non-verbal element + known verb (دەرکەوتن, بەکارهێنان, دەستپێکردن)
    for k in range(2, len(core) - 2):
        rest = core[k:]
        if rest in known and not known[rest].preverb:
            base = known[rest]
            pre = core[:k]
            return Verb(infinitive, base.past, base.present, base.transitive if transitive is None else transitive,
                        pre, suffix, source, light=pre not in PREVERBS)
    past = past_stem_of(core)
    if not past:
        return None
    pres = present or guess_present_stem(past)
    tr = True if transitive is None else transitive
    return Verb(infinitive, past, pres, tr, "", suffix, source)


# ---------------------------------------------------------------------------
# Paradigm generation
# ---------------------------------------------------------------------------


def _vowel_final(stem: str) -> bool:
    """Phonologically vowel-final? کەو /kæw/ and بزوو /bɯzuː/ differ: final و/ی after a vowel letter is a glide."""
    if not stem:
        return False
    last = stem[-1]
    if last in "اەۆێ":
        return True
    if last in "وی":
        return len(stem) < 2 or stem[-2] == last or stem[-2] not in "اەۆێ"
    return False


def _set1_present(stem: str, person: str) -> str:
    if _vowel_final(stem):
        if person == "3sg":
            last = stem[-1]
            if last == "ە":
                return stem[:-1] + "ات"
            if last == "ۆ":
                return stem[:-1] + "وات"
            if last == "ی":
                return stem
            if last == "ا":
                return stem + "ت"
            return stem + "ت"  # ێ, و
        return stem + {"1sg": "م", "2sg": "یت", "1pl": "ین", "2pl": "ن", "3pl": "ن"}[person]
    return stem + {"1sg": "م", "2sg": "یت", "3sg": "ێت", "1pl": "ین", "2pl": "ن", "3pl": "ن"}[person]


def _set1_past(stem: str, person: str) -> str:
    return stem + {"1sg": "م", "2sg": "یت", "3sg": "", "1pl": "ین", "2pl": "ن", "3pl": "ن"}[person]


def _passive_stem(v: Verb) -> str:
    if v.base_infinitive == "گرتن":
        return "گیر"
    p = v.present
    if p.endswith("ۆ"):
        return p[:-1] + "ور"
    if p.endswith(("ە", "ێ", "ی")):
        return p[:-1] + "ر"
    return p + "ر"


def _perfect_base(past: str) -> str:
    """Stem of the perfect: کرد -> کردوو, دا -> داو, بوو -> بوو (no extra و)."""
    if past.endswith("وو"):
        return past
    return past + ("و" if past[-1] in VOWEL_END else "وو")


def _with_suffix(form: str, suffix: str) -> str:
    if not suffix:
        return form
    if form.endswith("ە"):
        return form + "وە"  # کردە + وە  -> کردەوە
    if form and form[-1] in VOWEL_END:
        return form + "وە"
    return form + suffix


def conjugate(v: Verb) -> Iterator[VerbForm]:
    """Yield every single-word form of *v* with its features."""
    pre, suf, lemma = v.preverb, v.suffix, v.infinitive
    irregular = IRREGULAR.get(v.base_infinitive, {})

    def emit(surface: str, **feat):
        yield VerbForm(_with_suffix(pre + surface, suf), lemma, {"pos": "VERB", **feat})

    pres, past = v.present, v.past
    for p in PERSONS:
        # present indicative, negative, subjunctive
        yield from emit(irregular.get(("present", p), "دە" + _set1_present(pres, p)), tense="present", mood="indicative", person=p)
        yield from emit(irregular.get(("present_neg", p), "نا" + _set1_present(pres, p)), tense="present", mood="indicative", person=p, polarity="neg")
        subj = irregular.get(("subjunctive", p), ("" if pre and not v.light else "ب") + _set1_present(pres, p))
        yield from emit(subj, tense="present", mood="subjunctive", person=p)
        yield from emit(irregular.get(("subjunctive_neg", p), "نە" + _set1_present(pres, p)), tense="present", mood="subjunctive", person=p, polarity="neg")
        if v.transitive:
            cl = SET2[p]
            yield from emit(past + cl, tense="past", aspect="perfective", agent=p, alignment="ergative")
            yield from emit("نە" + cl + past, tense="past", aspect="perfective", agent=p, polarity="neg", alignment="ergative")
            yield from emit("دە" + cl + past, tense="past", aspect="progressive", agent=p, alignment="ergative")
            yield from emit("نە" + cl + "دە" + past, tense="past", aspect="progressive", agent=p, polarity="neg", alignment="ergative")
            perf_base = _perfect_base(past)
            perf_cl = {"1sg": "مە", "2sg": "تە", "3sg": "یەتی", "1pl": "مانە", "2pl": "تانە", "3pl": "یانە"}[p]
            yield from emit(perf_base + perf_cl, tense="present_perfect", agent=p, alignment="ergative")
            yield from emit(past + "بوو" + cl, tense="past_perfect", agent=p, alignment="ergative")
            ps = _passive_stem(v)
            yield from emit("دە" + ps + _set1_present("ێ", p), tense="present", voice="passive", person=p)
            yield from emit("نا" + ps + _set1_present("ێ", p), tense="present", voice="passive", person=p, polarity="neg")
            yield from emit(_set1_past(ps + "ا", p), tense="past", voice="passive", person=p)
        else:
            yield from emit(_set1_past(past, p), tense="past", aspect="perfective", person=p, alignment="accusative")
            if p == "2sg":
                yield from emit(past + "ی", tense="past", aspect="perfective", person=p, variant="short")
            yield from emit("نە" + _set1_past(past, p), tense="past", aspect="perfective", person=p, polarity="neg")
            yield from emit("دە" + _set1_past(past, p), tense="past", aspect="progressive", person=p)
            yield from emit("نەدە" + _set1_past(past, p), tense="past", aspect="progressive", person=p, polarity="neg")
            perf = _perfect_base(past)
            perf_end = {"1sg": "م", "2sg": "یت", "3sg": "ە", "1pl": "ین", "2pl": "ن", "3pl": "ن"}[p]
            yield from emit(perf + perf_end, tense="present_perfect", person=p)
            yield from emit(_set1_past(past + "بوو", p), tense="past_perfect", person=p)
    goal = {"goal": "yes"}
    yield from emit(irregular.get(("present", "3sg"), "دە" + _set1_present(pres, "3sg")) + "ە", tense="present", person="3sg", **goal)
    if not v.transitive and not past.endswith(("ا", "وو", "ی")):
        yield from emit(past + "ە", tense="past", person="3sg", **goal)
    if v.transitive:
        # the agent clitic is often hosted by an earlier word (کارەکەم کرد): bare forms
        ext = {"agent": "external", "alignment": "ergative"}
        yield from emit(past, tense="past", aspect="perfective", **ext)
        yield from emit("نە" + past, tense="past", aspect="perfective", polarity="neg", **ext)
        yield from emit("دە" + past, tense="past", aspect="progressive", **ext)
        yield from emit(_perfect_base(past) + "ە", tense="present_perfect", **ext)
        yield from emit(past + "بوو", tense="past_perfect", **ext)
        if pre:
            # with a preverb the clitic sits right after it: ڕا+ی+گەیاند, هەڵ+م+گرت
            for p in PERSONS:
                yield VerbForm(_with_suffix(pre + SET2[p] + past, suf), lemma,
                               {"pos": "VERB", "tense": "past", "aspect": "perfective", "agent": p, "alignment": "ergative"})
    # imperative / prohibitive
    imp_sg = pres if _vowel_final(pres) else pres + "ە"
    b = "" if pre and not v.light else "ب"
    yield from emit(irregular.get(("imperative", "2sg"), b + imp_sg), mood="imperative", person="2sg")
    yield from emit(irregular.get(("imperative", "2pl"), b + pres + "ن"), mood="imperative", person="2pl")
    yield from emit("مە" + imp_sg, mood="imperative", person="2sg", polarity="neg")
    yield from emit("مە" + pres + "ن", mood="imperative", person="2pl", polarity="neg")
    # non-finite
    yield VerbForm(lemma, lemma, {"pos": "VERB", "form": "infinitive"})
    yield from emit(_perfect_base(past), form="past_participle")
    if v.transitive:
        ps = _passive_stem(v)
        yield from emit(ps + "او", form="passive_participle")
        yield from emit(ps + "اوە", tense="present_perfect", voice="passive", person="3sg")


class FormIndex:
    """Inverted paradigm index: surface form -> list of VerbForm analyses."""

    def __init__(self, verbs: Iterable[Verb]):
        self.verbs: dict[str, Verb] = {}
        self._index: dict[str, list[VerbForm]] = defaultdict(list)
        for v in verbs:
            self.add(v)

    def add(self, v: Verb) -> None:
        if v.infinitive in self.verbs:
            return
        self.verbs[v.infinitive] = v
        for f in conjugate(v):
            self._add_form(f)

    def _add_form(self, f: VerbForm) -> None:
        """Index *f*; persons that share a surface form (2pl/3pl ـن) become one ``2pl|3pl`` reading."""
        same = self._index[f.form]
        person = f.features.get("person")
        if person:
            rest = {k: x for k, x in f.features.items() if k != "person"}
            for i, g in enumerate(same):
                if g.lemma == f.lemma and "person" in g.features and rest == {k: x for k, x in g.features.items() if k != "person"}:
                    persons = g.features["person"].split("|")
                    if person not in persons:
                        merged = "|".join(sorted(persons + [person]))
                        same[i] = VerbForm(g.form, g.lemma, {**g.features, "person": merged})
                    return
        same.append(f)

    def lookup(self, form: str) -> list[VerbForm]:
        return self._index.get(form, [])

    def __len__(self) -> int:
        return len(self._index)


_DEFAULT_INDEX: FormIndex | None = None


def default_index() -> FormIndex:
    global _DEFAULT_INDEX
    if _DEFAULT_INDEX is None:
        core = load_core_verbs()
        known = {v.infinitive: v for v in core if not v.preverb and not v.suffix}
        full = [make_verb(v.infinitive, v.transitive, v.present, "core", known) or v for v in core]
        _DEFAULT_INDEX = FormIndex(full)
    return _DEFAULT_INDEX
