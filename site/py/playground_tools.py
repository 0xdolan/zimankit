"""Structured results for the website's playground tools, as JSON-ready data.

The zimankit command prints text for the terminal; these functions return the same analyses
as data, so the page can show tables and grids. They run in the browser, in Pyodide.
"""

from __future__ import annotations

import difflib
import re
import unicodedata

from zimankit.shared_utils.lid import identify
from zimankit.shared_utils.text_helpers import detect_script
from zimankit.shared_utils.tokenizer import tokenize, words

LANGUAGES = {"ckb": "Central Kurdish (Sorani)", "kmr": "Northern Kurdish (Kurmanji)", "zza": "Zazaki", "hac": "Gorani / Hawrami",
             "fas": "Persian", "arb": "Arabic", "tur": "Turkish", "eng": "English"}
PERSONS = ["1sg", "2sg", "3sg", "1pl", "2pl", "3pl", "pl", "external", ""]
GROUPS = [  # (title, tense, mood, aspect, voice)
    ("Present", "present", "indicative", None, None),
    ("Subjunctive", "present", "subjunctive", None, None),
    ("Subjunctive", None, "subjunctive", None, None),
    ("Imperative", None, "imperative", None, None),
    ("Past", "past", None, "perfective", None),
    ("Past progressive", "past", None, "progressive", None),
    ("Present perfect", "present_perfect", None, None, None),
    ("Past perfect", "past_perfect", None, None, None),
    ("Passive present", "present", None, None, "passive"),
    ("Passive past", "past", None, None, "passive"),
    ("Passive present perfect", "present_perfect", None, None, "passive"),
]


def _lang(text: str, lang: str | None) -> str:
    return lang or ("ckb" if detect_script(text) == "arabic" else "kmr")


def _analyzer(lang: str):
    if lang == "ckb":
        from zimankit.skills_ckb.morphology import CkbAnalyzer as A
    else:
        from zimankit.skills_kmr.morphology import KmrAnalyzer as A
    return _CACHE.setdefault(lang, A())


_CACHE: dict = {}


def analyze(text: str, lang: str | None = None, top: int = 1) -> list[dict]:
    out = []
    for w in words(text):
        lg = _lang(w, lang)
        out.append({"word": w, "lang": lg, "analyses": [a.to_dict() for a in _analyzer(lg).analyze(w)[:top]]})
    return out


def ipa(text: str, lang: str | None = None, narrow: bool = False, plain: bool = False) -> list[dict]:
    out = []
    for w in words(text):
        lg = _lang(w, lang)
        if lg == "ckb":
            from zimankit.skills_ckb.phonology_ipa import G2POptions, syllables, to_ipa, to_latin

            row = {"ipa": to_ipa(w, G2POptions(mark_epenthesis=not plain)), "other_script": to_latin(w)}
        else:
            from zimankit.skills_kmr.phonology_ipa import KmrG2POptions, syllables, to_ipa
            from zimankit.skills_kmr.translit import to_arabic

            row = {"ipa": to_ipa(w, KmrG2POptions(narrow=narrow)), "other_script": to_arabic(w)}
        out.append({"word": w, "lang": lg, "syllables": syllables(w), **row})
    return out


def translit(lines: list[str], lang: str | None = None) -> list[dict]:
    out = []
    for line in lines:
        lg = _lang(line, lang)
        if lg == "ckb":
            from zimankit.skills_ckb.phonology_ipa import to_latin as conv
        else:
            from zimankit.skills_kmr.translit import to_arabic as conv
        toks = tokenize(line)
        result = " ".join(conv(t.text) if t.kind == "word" else t.text for t in toks)
        pairs = [{"from": t.text, "to": conv(t.text)} for t in toks if t.kind == "word"]
        out.append({"input": line, "output": result, "lang": lg, "words": pairs})
    return out


def conjugate(infinitive: str, lang: str | None = None, present: str | None = None, transitive: bool | None = None) -> dict:
    lg = _lang(infinitive, lang)
    if lg == "ckb":
        from zimankit.skills_ckb import verbs as V
    else:
        from zimankit.skills_kmr import verbs as V
    idx = V.default_index()
    verb = idx.verbs.get(infinitive)
    listed = verb is not None
    if verb is None:
        known = {x.infinitive: x for x in idx.verbs.values() if not x.preverb}
        verb = V.make_verb(infinitive, transitive, present or None, "guess", known)
    if verb is None:
        return {"infinitive": infinitive, "lang": lg, "error": "A paradigm could not be built for this word. Is it an infinitive?"}
    forms = list(V.conjugate(verb))
    groups: dict[str, dict] = {}
    other = []
    for f in forms:
        ft = f.features
        key = (ft.get("tense"), ft.get("mood"), ft.get("aspect"), ft.get("voice"))
        title = next((g[0] for g in GROUPS if g[1:] == key), None)
        if title is None:
            other.append({"form": f.form, "features": {k: v for k, v in ft.items() if k != "pos"}})
            continue
        person = ft.get("person") or ft.get("agent") or ""
        rows = groups.setdefault(title, {"title": title, "rows": {}})["rows"]
        cell = rows.setdefault(person, {"person": person, "affirmative": [], "negative": []})
        cell["negative" if ft.get("polarity") == "neg" else "affirmative"].append(f.form)
    ordered = []
    for title in dict.fromkeys(g[0] for g in GROUPS):
        if title in groups:
            rows = sorted(groups[title]["rows"].values(), key=lambda r: PERSONS.index(r["person"]) if r["person"] in PERSONS else 99)
            ordered.append({"title": title, "rows": rows})
    return {"infinitive": infinitive, "lang": lg, "listed": listed, "slug": _verb_slug(infinitive, lg), "count": len(forms),
            "groups": ordered, "other": other}


def _verb_slug(infinitive: str, lang: str) -> str:
    """The name of the verb's page in the tutorials, as scripts/gen_tutorials.py makes it."""
    latin = infinitive
    if lang == "ckb":
        from zimankit.skills_ckb.phonology_ipa import to_latin

        latin = to_latin(infinitive)
    return re.sub(r"[^a-z0-9]+", "-", latin.lower().translate(str.maketrans("çêîşûéáíú", "ceisueaiu"))).strip("-")


def ergativity(lines: list[str]) -> list[dict]:
    from zimankit.skills_kmr.syntax import detect_alignment

    return [detect_alignment(line).to_dict() for line in lines]


def lid(lines: list[str]) -> list[dict]:
    out = []
    for line in lines:
        r = identify(line)
        out.append({"text": line, "lang": r.lang, "name": LANGUAGES.get(r.lang, r.lang), "script": r.script, "confidence": r.confidence})
    return out


def _codepoint(s: str) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in s)


def _name(s: str) -> str:
    return ", ".join(unicodedata.name(c, "unnamed").title() for c in s)


def normalize(lines: list[str], lang: str | None = None) -> list[dict]:
    out = []
    for line in lines:
        lg = _lang(line, lang)
        if lg == "ckb":
            from zimankit.skills_ckb.orthography import normalize as f
        else:
            from zimankit.skills_kmr.orthography import normalize as f
        result = f(line)
        changes = []
        for op, a, b, c, d in difflib.SequenceMatcher(None, line, result, autojunk=False).get_opcodes():
            if op != "equal":
                changes.append({"from": line[a:b], "to": result[c:d], "from_code": _codepoint(line[a:b]), "to_code": _codepoint(result[c:d]),
                                "from_name": _name(line[a:b]), "to_name": _name(result[c:d])})
        out.append({"input": line, "output": result, "lang": lg, "changed": result != line, "changes": changes})
    return out


def validate(text: str, lang: str | None = None) -> list[dict]:
    out = []
    for w in text.split():
        lg = _lang(w, lang)
        if lg == "ckb":
            from zimankit.skills_ckb.orthography import normalize_word, validate_word
        else:
            from zimankit.skills_kmr.orthography import normalize_word, validate_word
        fixed = normalize_word(w)
        out.append({"input": w, "normalized": fixed, "lang": lg, "changed": fixed != w, "problems": list(validate_word(fixed))})
    return out


def tokens(lines: list[str]) -> list[dict]:
    return [{"text": line, "tokens": [{"text": t.text, "kind": t.kind, "start": t.start, "end": t.end} for t in tokenize(line)]} for line in lines]


def run(tool: str, payload: dict):
    return {"analyze": analyze, "ipa": ipa, "translit": translit, "conjugate": conjugate, "ergativity": ergativity, "lid": lid,
            "normalize": normalize, "validate": validate, "tokenize": tokens}[tool](**payload)
