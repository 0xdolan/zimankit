"""Clause-level alignment detection for Northern Kurdish (split ergativity).

Kurmanji is *nominative-accusative* in present-stem tenses and *ergative* in
past-stem tenses of transitive verbs::

    Ez te dibînim.     I.DIR  you.OBL  see-1SG     verb agrees with the agent
    Min tu dîtî.       I.OBL  you.DIR  saw-2SG     verb agrees with the OBJECT
    Min ew dîtin.      I.OBL  they.DIR saw-PL
    Ez hatim.          I.DIR  came-1SG             intransitive: agrees with subject

``detect_alignment`` finds the finite verb of a clause, decides which
alignment applies, picks the agent / object candidates by case, and checks
whether the verb's person ending agrees with the expected argument.  The
result is a log record, suitable for corpus statistics or grammar checking.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from ..shared_utils.schema import Analysis
from ..shared_utils.tokenizer import words
from .morphology import KmrAnalyzer

PRONOUN_PERSON = {
    "ez": "1sg", "min": "1sg", "tu": "2sg", "te": "2sg", "ew": "3sg|pl", "wî": "3sg", "wê": "3sg",
    "ev": "3sg|pl", "vî": "3sg", "vê": "3sg", "em": "pl", "me": "pl", "hûn": "pl", "we": "pl",
    "wan": "pl", "van": "pl",
}
DIRECT_PRONOUNS = {"ez", "tu", "ew", "em", "hûn", "ev"}
OBLIQUE_PRONOUNS = {"min", "te", "wî", "wê", "me", "we", "wan", "vî", "vê", "van"}


@dataclass
class Argument:
    token: str
    index: int
    case: str
    person: str | None


@dataclass
class AlignmentRecord:
    sentence: str
    verb: str | None = None
    lemma: str | None = None
    tense_stem: str | None = None  # "present" | "past"
    transitive: bool | None = None
    alignment: str | None = None  # "ergative" | "accusative"
    agent: Argument | None = None
    object: Argument | None = None
    verb_person: str | None = None
    controller: str | None = None  # which argument the verb should agree with
    agreement_ok: bool | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _case_of(token: str, a: Analysis | None) -> tuple[str, str | None]:
    t = token.lower()
    if t in DIRECT_PRONOUNS:
        return "dir", PRONOUN_PERSON[t]
    if t in OBLIQUE_PRONOUNS:
        return "obl", PRONOUN_PERSON[t]
    if a is None or a.pos not in ("NOUN", "PROPN", "ADJ"):
        return "none", None
    case = a.features.get("case")
    number = a.features.get("number", "sg")
    person = "pl" if number == "pl" else "3sg"
    if case == "obl":
        return "obl", person
    if a.features.get("ezafe"):
        return "ezafe", person
    return "dir", person


def detect_alignment(sentence: str, analyzer: KmrAnalyzer | None = None) -> AlignmentRecord:
    an = analyzer or KmrAnalyzer()
    toks = list(words(sentence))
    rec = AlignmentRecord(sentence)
    analyses = [an.best(t) for t in toks]
    # finite verb = last token with a finite verbal reading
    verb_i = None
    for i in range(len(toks) - 1, -1, -1):
        for a in an.analyze(toks[i]):
            if a.pos == "VERB" and "person" in a.features and a.features.get("mood") != "imperative":
                verb_i, analyses[i] = i, a
                break
        if verb_i is not None:
            break
    if verb_i is None:
        rec.notes.append("no finite verb found")
        return rec
    va = analyses[verb_i]
    assert va is not None
    rec.verb, rec.lemma = toks[verb_i], va.lemma
    rec.verb_person = va.features.get("person")
    rec.transitive = va.features.get("transitivity") == "transitive"
    past = va.features.get("tense") in ("past", "present_perfect", "past_perfect")
    rec.tense_stem = "past" if past else "present"
    rec.alignment = "ergative" if (past and rec.transitive) else "accusative"

    args = []
    for i in range(verb_i):
        case, person = _case_of(toks[i], analyses[i])
        if case in ("dir", "obl"):
            prev = toks[i - 1].lower() if i else ""
            if prev in {"di", "ji", "bi", "li", "bo", "ber", "ser", "nav", "ligel", "digel"}:
                continue  # object of a preposition, not a core argument
            args.append(Argument(toks[i], i, case, person))
    obl = [a for a in args if a.case == "obl"]
    direct = [a for a in args if a.case == "dir"]
    if rec.alignment == "ergative":
        rec.agent = obl[0] if obl else None
        rec.object = direct[0] if direct else None
        rec.controller = "object"
        target = rec.object
        if rec.agent is None:
            rec.notes.append("ergative clause without an overt oblique agent (pro-drop)")
        if direct and obl and direct[0].index < obl[0].index:
            rec.notes.append("object precedes agent (marked order)")
    else:
        rec.agent = direct[0] if direct else None
        rec.object = obl[0] if (obl and rec.transitive) else None
        rec.controller = "subject"
        target = rec.agent
        if obl and not direct and past is False and rec.transitive:
            rec.notes.append("oblique-case subject with a present-tense verb: check agreement")
    if target is not None and target.person and rec.verb_person:
        rec.agreement_ok = rec.verb_person in target.person.split("|")  # ew = he/she/they
        if not rec.agreement_ok:
            rec.notes.append(f"verb ending marks {rec.verb_person} but {rec.controller} '{target.token}' is {target.person}")
    elif target is None:
        rec.notes.append(f"{rec.controller} not overt; verb ending marks {rec.verb_person}")
    return rec
