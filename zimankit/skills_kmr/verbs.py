"""Northern Kurdish verb lexicon and paradigm generator.

Kurmanji verbs have two stems.  The *past stem* is the infinitive minus
``-in`` / ``-n`` (``dîtin`` -> ``dît``, ``çûn`` -> ``çû``); the *present
stem* is lexical (``dîtin`` -> ``bîn``).  Agreement endings:

=======  =========================  =========================
person   after consonant            after vowel
=======  =========================  =========================
1sg      -im      dibînim           -m      dişom
2sg      -î       dibînî            -yî     dişoyî
3sg      -e (pres) / -ø (past)      -ø      dişo
pl       -in      dibînin           -n      dişon
=======  =========================  =========================

Split ergativity: in every tense built on the **past stem**, a transitive
verb agrees with its *object* (which is in the direct case) while the agent
is in the oblique case: *min tu dîtî* "I saw you" - ``-î`` agrees with *tu*.
Intransitive past verbs and all present-stem tenses agree with the subject.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from importlib import resources
from typing import Iterable, Iterator

PERSONS = ("1sg", "2sg", "3sg", "pl")
VOWELS = "aeêiîouû"
PREVERBS = ("hil", "ra", "der", "ve", "wer", "lê", "pê", "tê", "çê", "da", "rû")
NI_NEGATION = {"zanîn", "karîn"}  # nizanim, nikarim


@dataclass(frozen=True)
class Verb:
    infinitive: str
    past: str
    present: str
    transitive: bool
    preverb: str = ""
    source: str = "core"


@dataclass(frozen=True)
class VerbForm:
    form: str
    lemma: str
    features: dict = field(hash=False, compare=False)


def load_core_verbs() -> list[Verb]:
    text = resources.files("zimankit.data").joinpath("kmr_verbs_core.tsv").read_text("utf-8")
    out = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = (line.split("\t") + [""] * 6)[:6]
        inf, past, pres, tr, pre = (c.strip() for c in cols[:5])
        out.append(Verb(inf, past, pres, tr == "T", pre))
    return out


def past_stem_of(infinitive: str) -> str | None:
    if infinitive.endswith("in") and len(infinitive) > 3 and infinitive[-3] not in VOWELS:
        return infinitive[:-2]
    if infinitive.endswith("n") and len(infinitive) > 2 and infinitive[-2] in "aîûe":
        return infinitive[:-1]
    return None


def guess_present_stem(past: str) -> str:
    """Regular patterns only: -and -> -în (causative), -î -> drop, else = past."""
    if past.endswith("and"):
        return past[:-3] + "în"
    if past.endswith("î") and len(past) > 2:
        return past[:-1]
    if past.endswith("t") and len(past) > 2 and past[-2] in "sş":
        return past[:-1]
    return past


def make_verb(infinitive: str, transitive: bool | None = None, present: str | None = None,
              source: str = "guess", known: dict[str, Verb] | None = None) -> Verb | None:
    known = known or {}
    if infinitive in known:
        return known[infinitive]
    for pre in PREVERBS:
        rest = infinitive[len(pre):]
        if infinitive.startswith(pre) and rest in known:
            b = known[rest]
            return Verb(infinitive, b.past, b.present, b.transitive if transitive is None else transitive, pre, source)
    past = past_stem_of(infinitive)
    if not past:
        return None
    return Verb(infinitive, past, present or guess_present_stem(past), True if transitive is None else transitive, "", source)


def _join(stem: str, suffix: str) -> str:
    """Attach a suffix; a stem-final î shortens to i before y (anî+yî -> aniyî, zanî+ye -> zaniye)."""
    if stem.endswith("î") and suffix.startswith("y"):
        return stem[:-1] + "i" + suffix
    return stem + suffix


def _ending(stem: str, person: str, tense: str) -> str:
    vowel_final = stem[-1] in VOWELS
    if vowel_final:
        return {"1sg": "m", "2sg": "yî", "3sg": "", "pl": "n"}[person]
    if tense == "present":
        return {"1sg": "im", "2sg": "î", "3sg": "e", "pl": "in"}[person]
    return {"1sg": "im", "2sg": "î", "3sg": "", "pl": "in"}[person]


def _present_prefix(v: Verb, kind: str) -> str:
    """Prefix for a present-stem form.

    ê/î-initial stems contract with the prefixes (têm, tînim, nayêm, bêm, neyê);
    a-initial stems keep di- and merge na- (diaxivim, naxivim, baxivim).
    """
    first = v.present[0]
    ei_initial = first in "êî"
    base = v.infinitive[len(v.preverb):]
    if kind == "ind":
        if base == "rûniştin":
            return ""
        return "t" if ei_initial else "di"
    if kind == "neg":
        if base in NI_NEGATION:
            return "ni"
        return "nay" if ei_initial else "n" if first == "a" else "na"
    if kind == "subj":
        if v.preverb:
            return ""
        return "b" if first in VOWELS else "bi"
    if kind == "negsubj":
        return "ney" if ei_initial else "ne"
    raise ValueError(kind)


def conjugate(v: Verb) -> Iterator[VerbForm]:
    pre, lemma, pres, past = v.preverb, v.infinitive, v.present, v.past
    base = lemma[len(pre):]
    align = "ergative" if v.transitive else "accusative"
    agr_past = "object" if v.transitive else "subject"

    def emit(surface: str, **feat):
        yield VerbForm(pre + surface, lemma, {"pos": "VERB", **feat})

    for p in PERSONS:
        e = _ending(pres, p, "present")
        yield from emit(_present_prefix(v, "ind") + pres + e, tense="present", mood="indicative", person=p, agreement="subject")
        yield from emit(_present_prefix(v, "neg") + pres + e, tense="present", mood="indicative", person=p, polarity="neg", agreement="subject")
        yield from emit(_present_prefix(v, "subj") + pres + e, mood="subjunctive", person=p, agreement="subject")
        yield from emit(_present_prefix(v, "negsubj") + pres + e, mood="subjunctive", person=p, polarity="neg", agreement="subject")
        pe = _join(past, _ending(past, p, "past"))
        yield from emit(pe, tense="past", aspect="perfective", person=p, agreement=agr_past, alignment=align)
        yield from emit("ne" + pe, tense="past", aspect="perfective", person=p, polarity="neg", agreement=agr_past, alignment=align)
        yield from emit("di" + pe, tense="past", aspect="progressive", person=p, agreement=agr_past, alignment=align)
        yield from emit("nedi" + pe, tense="past", aspect="progressive", person=p, polarity="neg", agreement=agr_past, alignment=align)
        vowel_final = past[-1] in VOWELS
        perf = {"1sg": "me", "2sg": "yî", "3sg": "ye", "pl": "ne"} if vowel_final else {"1sg": "ime", "2sg": "iyî", "3sg": "iye", "pl": "ine"}
        yield from emit(_join(past, perf[p]), tense="present_perfect", person=p, agreement=agr_past, alignment=align)
        plup = past + ("bû" if vowel_final else "ibû")
        yield from emit(plup + _ending(plup, p, "past"), tense="past_perfect", person=p, agreement=agr_past, alignment=align)
    # imperative
    if base == "hatin":
        imp = {"2sg": "were", "2pl": "werin"}
    elif base == "çûn":
        imp = {"2sg": "here", "2pl": "herin"}
    else:
        stem_v = pres[-1] in VOWELS
        sub = _present_prefix(v, "subj")
        imp = {"2sg": sub + pres + ("" if stem_v else "e"), "2pl": sub + pres + ("n" if stem_v else "in")}
    for p, f in imp.items():
        yield from emit(f, mood="imperative", person=p)
        if pres[-1] in VOWELS:
            end = "" if p == "2sg" else "n"
        else:
            end = "e" if p == "2sg" else "in"
        yield from emit(_present_prefix(v, "negsubj") + pres + end, mood="imperative", person=p, polarity="neg")
    yield VerbForm(lemma, lemma, {"pos": "VERB", "form": "infinitive"})
    yield from emit(past + ("yî" if past[-1] in VOWELS else "î"), form="past_participle")


class FormIndex:
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
            self._index[f.form].append(f)

    def lookup(self, form: str) -> list[VerbForm]:
        return self._index.get(form, [])

    def __len__(self) -> int:
        return len(self._index)


_DEFAULT: FormIndex | None = None


def default_index() -> FormIndex:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = FormIndex(load_core_verbs())
    return _DEFAULT
