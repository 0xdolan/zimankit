"""Agreement checks for Central Kurdish clauses.

Warnings, not verdicts: they come from rules over the sentence parser's output, and Kurdish often
leaves out the subject, so they speak only when the words needed to judge are there.

* a past transitive verb with no agent anywhere: من نان خوارد (نانم خوارد);
* an agent clitic on an intransitive past: هاتمان (هاتین);
* a subject pronoun whose person differs from the verb's: من دەچیت;
* a plural verb after a singular definite subject: پیاوەکە دەچن.  This last is common usage, and no
  grammar checked states a rule, so it is worded as a question of usage.
"""

from __future__ import annotations

_AGENT_CLITICS = {"م": "1sg", "ت": "2sg", "ی": "3sg", "مان": "1pl", "تان": "2pl", "یان": "3pl"}
_SET1_PAST = {"1sg": "م", "2sg": "یت", "3sg": "", "1pl": "ین", "2pl": "ن", "3pl": "ن"}


def agreement_warnings(words: list, verbs) -> list[str]:
    """Possible agreement problems in a parsed clause; *words* have ``upos``, ``deprel``, ``head`` and ``features``."""
    out = []
    for w in words:
        if w.upos == "VERB":
            out += _verb_warnings(w, words)
        elif w.upos in ("NOUN", "X"):
            for clitic in ("مان", "تان", "یان", "م", "ت"):
                stem = w.text[: -len(clitic)]
                if w.text.endswith(clitic) and w.deprel == "root" and _intransitive_past(stem, verbs):
                    person = _AGENT_CLITICS[clitic]
                    out.append(f"Possible agreement problem: {stem} is intransitive, so its past takes an ending, not a clitic: {stem + _SET1_PAST[person]}.")
                    break
    return out


def _intransitive_past(stem: str, verbs) -> bool:
    return any(not verbs.verbs[f.lemma].transitive and f.features.get("tense") == "past" and "polarity" not in f.features for f in verbs.lookup(stem))


def _verb_warnings(v, words: list) -> list[str]:
    ft = v.features
    subject = next((w for w in words if w.head == v.id and w.deprel in ("nsubj", "nsubj:pass")), None)
    if ft.get("agent") == "external" and ft.get("transitivity") == "transitive" and ft.get("tense") == "past" and not ft.get("voice"):
        before = [w for w in words if w.id < v.id and w.upos != "PUNCT"]
        if before and not any(w.features.get("enclitic") or w.upos == "PART" or w.text.endswith(tuple(_AGENT_CLITICS)) for w in before):
            return [f"Possible agreement problem: the past of a transitive verb needs an agent clitic on an earlier word or on {v.text}."]
    person = ft.get("person")
    if subject is None or not person:
        return []
    if subject.upos == "PRON" and subject.features.get("person") and subject.features["person"] not in person:
        return [f"Possible agreement problem: the subject {subject.text} is {subject.features['person']}, but {v.text} is {person}."]
    if subject.features.get("number") == "sg" and subject.features.get("definite") == "def" and person == "2pl|3pl":
        return [f"Usage: {subject.text} is singular and {v.text} is plural. This is common, but a singular verb is the plain choice."]
    return []
