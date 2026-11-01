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
Kurdish grammars number these the other way: their کۆمەڵەی یەکەم is set 2 here,
and their دووەم and سێیەم are the past and present halves of set 1.

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
# longest first; simple and complex (ناسادە) preverbs
PREVERBS = ("پێدا", "تێدا", "پێڕا", "تێڕا", "لێڕا", "تێوە", "پێوە", "لێوە", "پێک", "تێک", "ڕێک", "وێک", "لێک",
            "هەڵ", "وەر", "دەر", "دا", "ڕا", "ڕۆ", "ڕێ", "تێ", "پێ", "لێ")
# written apart in every tense (تێک دەچم, پێ دەکەنێت); the others only around a clitic (هەڵدەگرم, هەڵم گرت)
SPLIT_PREVERBS = frozenset({"پێ", "تێ", "لێ", "پێک", "تێک", "ڕێک"})
VOWEL_END = "اەۆێیو"
PERFECT_LONG = {"1sg": "مە", "2sg": "یتە", "3sg": "ە", "1pl": "ینە", "2pl": "نە", "3pl": "نە"}
PERFECT_SHORT = {"1sg": "م", "2sg": "یت", "3sg": "ە", "1pl": "ین", "2pl": "ن", "3pl": "ن"}
PAST_SUBJUNCTIVES = (("با", "past_subj"), ("بێت", "perfect_subj"), ("بووبا", "pluperfect_subj"))  # خواردبا, خواردبێت, خواردبووبا
NO_PASSIVE = frozenset({"ڕاکردن"})  # takes the agent clitics (ڕام کرد) but means "run"

# Irregular cells that no rule produces.
IRREGULAR: dict[str, dict[tuple[str, str], str]] = {
    "هاتن": {
        **{("present", p): "د" + f for p, f in zip(PERSONS, ("ێم", "ێیت", "ێت", "ێین", "ێن", "ێن"))},
        **{("present_neg", p): "نا" + f for p, f in zip(PERSONS, ("یەم", "یەیت", "یەت", "یەین", "یەن", "یەن"))},
        **{("subjunctive_neg", p): "نە" + f for p, f in zip(PERSONS, ("یەم", "یەیت", "یەت", "یەین", "یەن", "یەن"))},
        **{("subjunctive", p): "ب" + f for p, f in zip(PERSONS, ("ێم", "ێیت", "ێت", "ێین", "ێن", "ێن"))},
        ("imperative", "2sg"): "وەرە",
        ("imperative", "2pl"): "وەرن",
        ("prohibitive", "2sg"): "مەیە",
        ("prohibitive", "2pl"): "مەیەن",
    },
    "چوون": {("imperative", "2sg"): "بچۆ", ("imperative", "2pl"): "بچن", ("prohibitive", "2sg"): "مەچۆ", ("prohibitive", "2pl"): "مەچن"},
}
# Accepted alongside the cells above, but not the form shown first.
IRREGULAR_VARIANTS: dict[str, dict[tuple[str, str], str]] = {
    "هاتن": {("imperative", "2sg"): "بێ", ("imperative", "2pl"): "بێن", ("prohibitive", "2sg"): "مەیێ", ("prohibitive", "2pl"): "مەیێن"},
    "چوون": {("imperative", "2sg"): "بڕۆ", ("imperative", "2pl"): "بڕۆن"},  # from ڕۆیشتن
}
# Present-stem tenses whose person marker is a set-2 clitic (دەمەوێت "I want", lit. "to-me it is wanted");
# the imperative (بتەوێ) and the passive (ویسترا) are rare.
CLITIC_SUBJECT_PRESENT = {"ویستن": "ەوێت"}
# Passive stems that the rules below do not derive.
PASSIVE_STEM = {"گرتن": "گیر", "گوتن": "گوتر", "وتن": "وتر", "بیستن": "بیستر", "ویستن": "ویستر"}
# Forms that are almost always another word: the particle نا and the noun نان, not "put".
HIDDEN_FORMS = {"نان": frozenset({"نا", "نان"})}


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
    def always_split(self) -> bool:
        """Is the first part written apart even with no clitic?  Noun + light verb and some preverbs are."""
        return bool(self.preverb) and (self.light or self.preverb in SPLIT_PREVERBS or self.preverb not in PREVERBS)

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


def guess_present_stem(past: str, transitive: bool | None = None) -> str:
    """Rule-of-thumb present stem for verbs missing from the reference list."""
    if past.endswith("وو"):
        return past  # دروو, سوو, جوو; چوون and بوون are in the list
    if past.endswith("ا") and transitive is False:
        return past[:-1] + "ێ"  # دڕا -> دڕێ, فەوتا -> فەوتێ
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
            if rest in ("وتن", "گوتن") and core[:k] not in PREVERBS:
                continue  # پاڵاوتن is not پاڵا + وتن
            base = known[rest]
            pre = core[:k]
            return Verb(infinitive, base.past, base.present, base.transitive if transitive is None else transitive,
                        pre, suffix, source, light=pre not in PREVERBS)
    past = past_stem_of(core)
    if not past:
        return None
    pres = present or guess_present_stem(past, transitive)
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
    if v.base_infinitive in PASSIVE_STEM:
        return PASSIVE_STEM[v.base_infinitive]
    p = v.present
    if p.endswith(("ر", "ڕ")):
        return p + "در"  # نێر -> نێردرا, کڕ -> کڕدرا
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
    if form.endswith("ا"):
        return form + "یەوە"  # گەڕا + یەوە -> گەڕایەوە (a glide after ا)
    if form.endswith(("ی", "و")):
        return form + "ەوە"  # کردی + ەوە, چوو + ەوە: never three و
    if form and form[-1] in VOWEL_END:
        return form + "وە"
    return form + suffix


def conjugate(v: Verb) -> Iterator[VerbForm]:
    """Yield every single-word form of *v* with its features."""
    pre, suf, lemma = v.preverb, v.suffix, v.infinitive
    irregular = IRREGULAR.get(v.base_infinitive, {})
    pres, past = v.present, v.past
    clitic_present = CLITIC_SUBJECT_PRESENT.get(v.base_infinitive)
    # on a guessed verb a vowel-final stem + با/بێت is more often another word: کوبا, ڕازی بێت
    past_subjunctives = PAST_SUBJUNCTIVES if v.source == "core" or past[-1:] not in VOWEL_END else ()

    def emit(surface: str, **feat):
        if suf and feat.get("tense") == "present_perfect":  # خوێندووەتەوە, چووینەتەوە
            yield VerbForm(pre + surface + "تەوە", lemma, {"pos": "VERB", **feat})
            if surface.endswith("ووە"):  # هاتۆتەوە, recognised but not shown
                yield VerbForm(pre + surface[:-3] + "ۆتەوە", lemma, {"pos": "VERB", **feat, "variant": "contracted"})
            return
        if suf and past.endswith("ی") and surface.endswith(past):  # دۆزی + ی + ەوە
            surface += "ی"
        yield VerbForm(_with_suffix(pre + surface, suf), lemma, {"pos": "VERB", **feat})
        # speech and poetry drop the ت: دەکا, دەڵێ, دەمەوێ, دەکەی
        if feat.get("tense") == "present" and "variant" not in feat and "goal" not in feat:
            person = feat.get("person")
            if surface.endswith("ت") and (person == "3sg" or clitic_present or (person == "2sg" and surface.endswith("یت"))):
                yield from emit(surface[:-1], variant="short", **feat)

    # the clitic belongs directly on the first part in every tense (RW, the grade 12 handout):
    # هەڵم+نەگرت, هەڵم+دەگرت, هەڵم+گرتووە.  The older solid shapes stay recognised as a variant.
    late = {"variant": "clitic_late"} if pre else {}

    def no_b(surface: str, **feat):
        """ب follows a preverb (هەڵبگرم) and may be dropped (هەڵگرم): the bare form is a variant."""
        if pre and not v.light:
            yield from emit(surface, variant="no_b", **feat)

    for p in PERSONS:
        if clitic_present:
            cl = SET2[p] + clitic_present
            yield from emit("دە" + cl, tense="present", mood="indicative", person=p)
            yield from emit("نا" + cl, tense="present", mood="indicative", person=p, polarity="neg")
            yield from emit("ب" + cl, tense="present", mood="subjunctive", person=p)
            yield from emit("نە" + cl, tense="present", mood="subjunctive", person=p, polarity="neg")
        else:
            # present indicative, negative, subjunctive
            yield from emit(irregular.get(("present", p), "دە" + _set1_present(pres, p)), tense="present", mood="indicative", person=p)
            yield from emit(irregular.get(("present_neg", p), "نا" + _set1_present(pres, p)), tense="present", mood="indicative", person=p, polarity="neg")
            yield from emit(irregular.get(("subjunctive", p), "ب" + _set1_present(pres, p)), tense="present", mood="subjunctive", person=p)
            if ("subjunctive", p) not in irregular:
                yield from no_b(_set1_present(pres, p), tense="present", mood="subjunctive", person=p)
            yield from emit(irregular.get(("subjunctive_neg", p), "نە" + _set1_present(pres, p)), tense="present", mood="subjunctive", person=p, polarity="neg")
        if v.transitive:
            cl = SET2[p]
            yield from emit(past + cl, tense="past", aspect="perfective", agent=p, alignment="ergative", **late)
            yield from emit("نە" + cl + past, tense="past", aspect="perfective", agent=p, polarity="neg", alignment="ergative", **late)
            yield from emit("دە" + cl + past, tense="past", aspect="progressive", agent=p, alignment="ergative", **late)
            yield from emit("نە" + cl + "دە" + past, tense="past", aspect="progressive", agent=p, polarity="neg", alignment="ergative", **late)
            perf_base = _perfect_base(past)
            perf_cl = {"1sg": "مە", "2sg": "تە", "3sg": "یەتی", "1pl": "مانە", "2pl": "تانە", "3pl": "یانە"}[p]
            if suf and p == "3sg":
                perf_cl = "یە"  # کردوویەتەوە
            yield from emit(perf_base + perf_cl, tense="present_perfect", agent=p, alignment="ergative", **late)
            if p == "3sg" and not suf:
                yield from emit(perf_base + "یە", tense="present_perfect", agent=p, alignment="ergative", variant="short")  # هێناویە
            yield from emit("نە" + cl + perf_base + "ە", tense="present_perfect", agent=p, polarity="neg", alignment="ergative", **late)
            yield from emit(past + "بوو" + cl, tense="past_perfect", agent=p, alignment="ergative", **late)
            yield from emit("نە" + cl + past + "بوو", tense="past_perfect", agent=p, polarity="neg", alignment="ergative", **late)
            for mark, tense in past_subjunctives:
                subj = {"tense": tense, "mood": "subjunctive", "agent": p, "alignment": "ergative"}
                yield from emit(past + mark + cl, **subj, **late)
                yield from emit("نە" + cl + past + mark, polarity="neg", **subj, **late)
                yield from emit("نە" + past + mark + cl, polarity="neg", variant="clitic_end", **subj)
            ps = _passive_stem(v)
            if past[-1:] in ("ت", "د") and lemma not in NO_PASSIVE and not clitic_present:  # گرترا, بردرا: recognised, not shown
                yield from emit(_set1_past(past + "را", p), tense="past", voice="passive", person=p, variant="past_stem")
            if (not clitic_present or v.base_infinitive in PASSIVE_STEM) and lemma not in NO_PASSIVE and len(ps) >= 2:  # a lone ر is a guessed stem
                yield from emit("دە" + ps + _set1_present("ێ", p), tense="present", voice="passive", person=p)
                yield from emit("نا" + ps + _set1_present("ێ", p), tense="present", voice="passive", person=p, polarity="neg")
                yield from emit("ب" + ps + _set1_present("ێ", p), tense="present", mood="subjunctive", voice="passive", person=p)
                yield from emit("نە" + ps + _set1_present("ێ", p), tense="present", mood="subjunctive", voice="passive", person=p, polarity="neg")
                pa = ps + "ا"
                passive = {"voice": "passive", "person": p}
                yield from emit(_set1_past(pa, p), tense="past", **passive)
                yield from emit("نە" + _set1_past(pa, p), tense="past", polarity="neg", **passive)
                yield from emit("دە" + _set1_past(pa, p), tense="past", aspect="progressive", **passive)
                yield from emit("نەدە" + _set1_past(pa, p), tense="past", aspect="progressive", polarity="neg", **passive)
                # the sources print the short perfect here (بینراوم); -ەوە needs the long one (نوێکراونەتەوە)
                pf = (PERFECT_LONG if suf else PERFECT_SHORT)[p]
                yield from emit(pa + "و" + pf, tense="present_perfect", **passive)
                yield from emit("نە" + pa + "و" + pf, tense="present_perfect", polarity="neg", **passive)
                yield from emit(_set1_past(pa + "بوو", p), tense="past_perfect", **passive)
                yield from emit("نە" + _set1_past(pa + "بوو", p), tense="past_perfect", polarity="neg", **passive)
                for mark, tense in PAST_SUBJUNCTIVES:
                    yield from emit(_set1_past(pa + mark, p), tense=tense, mood="subjunctive", **passive)
                    yield from emit("نە" + _set1_past(pa + mark, p), tense=tense, mood="subjunctive", polarity="neg", **passive)
        else:
            yield from emit(_set1_past(past, p), tense="past", aspect="perfective", person=p, alignment="accusative")
            if p == "2sg":
                yield from emit(past + "ی", tense="past", aspect="perfective", person=p, variant="short")
            yield from emit("نە" + _set1_past(past, p), tense="past", aspect="perfective", person=p, polarity="neg")
            yield from emit("دە" + _set1_past(past, p), tense="past", aspect="progressive", person=p)
            yield from emit("نەدە" + _set1_past(past, p), tense="past", aspect="progressive", person=p, polarity="neg")
            perf = _perfect_base(past)
            # the long ending is the written form and carries -ەوە (هاتوومە, چووینەتەوە); هاتووم is spoken
            yield from emit(perf + PERFECT_LONG[p], tense="present_perfect", person=p)
            yield from emit("نە" + perf + PERFECT_LONG[p], tense="present_perfect", person=p, polarity="neg")
            if not suf and PERFECT_SHORT[p] != PERFECT_LONG[p]:
                yield from emit(perf + PERFECT_SHORT[p], tense="present_perfect", person=p, variant="short")
                yield from emit("نە" + perf + PERFECT_SHORT[p], tense="present_perfect", person=p, polarity="neg", variant="short")
            yield from emit(_set1_past(past + "بوو", p), tense="past_perfect", person=p)
            yield from emit("نە" + _set1_past(past + "بوو", p), tense="past_perfect", person=p, polarity="neg")
            for mark, tense in past_subjunctives:
                yield from emit(_set1_past(past + mark, p), tense=tense, mood="subjunctive", person=p)
                yield from emit("نە" + _set1_past(past + mark, p), tense=tense, mood="subjunctive", person=p, polarity="neg")
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
        yield from emit("نە" + _perfect_base(past) + "ە", tense="present_perfect", polarity="neg", **ext)
        yield from emit(past + "بوو", tense="past_perfect", **ext)
        yield from emit("نە" + past + "بوو", tense="past_perfect", polarity="neg", **ext)
        for mark, tense in past_subjunctives:
            yield from emit(past + mark, tense=tense, mood="subjunctive", **ext)
            yield from emit("نە" + past + mark, tense=tense, mood="subjunctive", polarity="neg", **ext)
        if pre:
            for p in PERSONS:
                agent = {"agent": p, "alignment": "ergative"}
                for neg, polarity in (("", {}), ("نە", {"polarity": "neg"})):
                    first = SET2[p] + neg
                    yield from emit(first + past, tense="past", aspect="perfective", **agent, **polarity)
                    yield from emit(first + "دە" + past, tense="past", aspect="progressive", **agent, **polarity)
                    yield from emit(first + _perfect_base(past) + "ە", tense="present_perfect", **agent, **polarity)
                    yield from emit(first + past + "بوو", tense="past_perfect", **agent, **polarity)
                    for mark, tense in past_subjunctives:
                        yield from emit(first + past + mark, tense=tense, mood="subjunctive", **agent, **polarity)
    if pres.endswith("ی") and not clitic_present:  # دەژی, also دەژێت
        yield from emit("دە" + pres[:-1] + "ێت", tense="present", mood="indicative", person="3sg", variant="root_i")
    if v.base_infinitive == "هاتن":  # نایەم is the common spelling; نایێم is argued for and recognised
        for p, end in zip(PERSONS, ("ێم", "ێیت", "ێت", "ێین", "ێن", "ێن")):
            yield from emit("نای" + end, tense="present", mood="indicative", person=p, polarity="neg", variant="ye")
            yield from emit("نەی" + end, tense="present", mood="subjunctive", person=p, polarity="neg", variant="ye")
    # imperative / prohibitive
    imp_sg = pres if _vowel_final(pres) else pres + "ە"
    for (cell, p), form in IRREGULAR_VARIANTS.get(v.base_infinitive, {}).items():
        polarity = {"polarity": "neg"} if cell == "prohibitive" else {}
        yield from emit(form, mood="imperative", person=p, variant="other", **polarity)
    if suf and imp_sg.endswith("ە") and not clitic_present:  # بکەرەوە: older or Sulaimani, recognised
        yield VerbForm(pre + "ب" + imp_sg + "رەوە", lemma, {"pos": "VERB", "mood": "imperative", "person": "2sg", "variant": "er"})
    if clitic_present:  # بتەوێ, مەتەوێ: rare
        for p, cl in (("2sg", "ت"), ("2pl", "تان")):
            yield from emit("ب" + cl + "ەوێ", mood="imperative", person=p)
            yield from emit("مە" + cl + "ەوێ", mood="imperative", person=p, polarity="neg")
    if not clitic_present:
        yield from emit(irregular.get(("imperative", "2sg"), "ب" + imp_sg), mood="imperative", person="2sg")
        yield from emit(irregular.get(("imperative", "2pl"), "ب" + pres + "ن"), mood="imperative", person="2pl")
        if ("imperative", "2sg") not in irregular:
            yield from no_b(imp_sg, mood="imperative", person="2sg")
        if ("imperative", "2pl") not in irregular:
            yield from no_b(pres + "ن", mood="imperative", person="2pl")
        yield from emit(irregular.get(("prohibitive", "2sg"), "مە" + imp_sg), mood="imperative", person="2sg", polarity="neg")
        yield from emit(irregular.get(("prohibitive", "2pl"), "مە" + pres + "ن"), mood="imperative", person="2pl", polarity="neg")
    # non-finite
    yield VerbForm(lemma, lemma, {"pos": "VERB", "form": "infinitive"})
    yield from emit(_perfect_base(past), form="past_participle")
    if v.transitive and not clitic_present and lemma not in NO_PASSIVE:
        ps = _passive_stem(v)
        yield from emit(ps + "او", form="passive_participle")


def standard_spelling(v: Verb, f: VerbForm) -> str:
    """How the written standard spaces a form: هەڵم گرت, نان دەکەم, دەستم پێ کرد.

    The index keeps one solid key per form, and solid forms stay accepted input.  A clitic on the first
    part always splits the verb; without one, only ``Verb.always_split`` verbs are written apart.
    """
    pre = v.preverb
    if not pre or not f.form.startswith(pre) or f.features.get("variant"):
        return f.form
    rest = f.form[len(pre) :]
    # دەستپێکردن has two first parts: دەست پێ دەکەم, and the clitic goes on the noun: دەستم پێ کرد
    head, adposition = pre, ""
    if pre not in PREVERBS and pre.endswith(("پێ", "تێ", "لێ")):
        head, adposition = pre[:-2], pre[-2:]
    clitic = SET2.get(f.features.get("agent"))
    if clitic and rest.startswith(clitic):
        return " ".join(x for x in (head + clitic, adposition, rest[len(clitic) :]) if x)
    if v.always_split:
        return " ".join(x for x in (head, adposition, rest) if x)
    return f.form


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
        hidden = HIDDEN_FORMS.get(v.infinitive, ())
        for f in conjugate(v):
            if f.form not in hidden:
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

    def lookup_split(self, tokens: list[str]) -> tuple[int, VerbForm] | None:
        """A verb written over several tokens: ``هەڵم گرت``, ``ڕای گەیاند``, ``دەست پێ دەکەم``, ``دەستم پێ کرد``.

        Returns how many tokens it spans and its reading.  The tokens before the last must be exactly
        the verb's first part, with or without a clitic, so an ordinary pair of words does not join.
        """
        for n in (3, 2):
            if len(tokens) < n:
                continue
            *head, last = tokens[:n]
            keys = [("".join(head), "")]  # دەستم پێ کرد: the clitic is on the noun, the key has it after پێ
            if n == 3:
                keys += [(head[0][: -len(c)] + head[1], c) for c in SET2.values() if head[0].endswith(c)]
            for first, clitic in keys:
                for f in self.lookup(first + clitic + last):
                    pre = self.verbs[f.lemma].preverb
                    if pre and not f.features.get("variant") and first in (pre, *(pre + c for c in SET2.values())):
                        return n, f
        return None

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
