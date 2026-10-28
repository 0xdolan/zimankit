#!/usr/bin/env python3
"""Build the language tutorials in docs/tutorials/ from the zimankit skills.

Lessons are hand-written Markdown containing *generator blocks*::

    <!-- gen:verb verb=کردن cells=present,present_neg -->
    ...replaced on every run...
    <!-- /gen -->

Every conjugation, declension, IPA transcription, transliteration and
analysis inside a block is produced by the same code the toolkit uses, so the
tutorials double as a human-readable test of the grammar logic.  The script
also writes the reference pages (one page per verb, noun tables, vocabulary)
and the previous/next navigation of every lesson.

    python scripts/gen_tutorials.py          # (re)write docs/tutorials
    python scripts/gen_tutorials.py --check  # exit 1 if a file is out of date
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from zimankit.shared_utils.schema import SimpleLexicon  # noqa: E402
from zimankit.shared_utils.tokenizer import tokenize  # noqa: E402

TUT = ROOT / "docs" / "tutorials"
LEVELS = {
    "1-beginner": ("beginner", "🟢 Beginner"),
    "2-intermediate": ("intermediate", "🟡 Intermediate"),
    "3-advanced": ("advanced", "🔴 Advanced"),
}
LANG_NAMES = {"ckb": "Central Kurdish (Sorani)", "kmr": "Northern Kurdish (Kurmanji)"}
TOP, BOTTOM = "<!-- nav:top -->", "<!-- nav:bottom -->"
BLOCK = re.compile(r"<!-- gen:(\w+)(.*?)-->.*?<!-- /gen -->", re.S)


class TutorialError(Exception):
    pass


# ---------------------------------------------------------------------------
# Language plumbing
# ---------------------------------------------------------------------------


@dataclass
class Lang:
    code: str
    ipa: Callable[[str], str]
    other: Callable[[str], str]  # the word in the other script
    other_name: str
    syllables: Callable[[str], list[str]]
    verbs: object
    analyzer_cls: type
    decline: Callable
    persons: tuple[tuple[str, str], ...]  # (feature value, label)
    vocab: dict[str, tuple[str, str]] = field(default_factory=dict)  # word -> (meaning, note)
    missing: set[str] = field(default_factory=set)
    _analyzer: object = None
    _verbs: dict = field(default_factory=dict)

    def meaning(self, word: str) -> str:
        if word not in self.vocab:
            self.missing.add(word)
            return "?"
        return self.vocab[word][0]

    def gender(self, word: str) -> str:
        note = self.vocab.get(word, ("", ""))[1]
        if note not in ("f", "m"):
            self.missing.add(f"{word} (gender)")
            return "m"
        return note

    def analyzer(self):
        if self._analyzer is None:
            lex = SimpleLexicon()
            for w, (_, note) in self.vocab.items():
                lex.add(w, "NOUN" if note in ("f", "m", "n") else None, note if note in ("f", "m") else None)
            self._analyzer = self.analyzer_cls(lex)
        return self._analyzer

    def verb(self, infinitive: str):
        if not self._verbs:
            self._verbs = {v.infinitive: v for v in self.verbs.load_core_verbs()}
        if infinitive in self._verbs:
            return self._verbs[infinitive]
        known = {k: v for k, v in self._verbs.items() if not v.preverb}
        v = self.verbs.make_verb(infinitive, None, None, "tutorial", known)
        if v is None:
            raise TutorialError(f"[{self.code}] cannot build verb {infinitive!r}")
        return v

    def text_other(self, text: str) -> str:
        out = []
        for t in tokenize(text):
            if t.kind == "word":
                out.append(self.other(t.text))
            else:
                out.append(t.text.translate(str.maketrans("?,;", "؟،؛")) if self.code == "kmr" else
                           t.text.translate(str.maketrans("؟،؛", "?,;")))
        return _join_tokens(out)

    def text_ipa(self, text: str) -> str:
        return "/" + " ".join(self.ipa(t.text) for t in tokenize(text) if t.kind == "word") + "/"


def _join_tokens(tokens: list[str]) -> str:
    s = " ".join(tokens)
    return re.sub(r" ([.,;:!?،؛؟»)])", r"\1", re.sub(r"([«(]) ", r"\1", s))


def load_langs() -> dict[str, Lang]:
    from zimankit.skills_ckb import morphology as cm, phonology_ipa as cp, verbs as cv
    from zimankit.skills_kmr import morphology as km, phonology_ipa as kp, translit as kt, verbs as kvb

    langs = {
        "ckb": Lang("ckb", cp.to_ipa, cp.to_latin, "Latin", cp.syllables, cv, cm.CkbAnalyzer, cm.decline,
                    (("1sg", "من"), ("2sg", "تۆ"), ("3sg", "ئەو"), ("1pl", "ئێمە"), ("2pl", "ئێوە"), ("3pl", "ئەوان"))),
        "kmr": Lang("kmr", kp.to_ipa, kt.to_arabic, "Arabic script", kp.syllables, kvb, km.KmrAnalyzer, km.decline,
                    (("1sg", "ez"), ("2sg", "tu"), ("3sg", "ew"), ("1pl", "em"), ("2pl", "hûn"), ("3pl", "ew"))),
    }
    for code, lang in langs.items():
        path = TUT / "_data" / f"{code}_vocab.tsv"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                cols = (line.split("\t") + ["", ""])[:3]
                lang.vocab[cols[0].strip()] = (cols[1].strip(), cols[2].strip())
    return langs


# ---------------------------------------------------------------------------
# Verb cells
# ---------------------------------------------------------------------------

# cell -> (column title, feature filter); None in a filter = feature must be absent
CKB_CELLS = {
    "present": ("Present", dict(tense="present", mood="indicative", polarity=None, voice=None, goal=None)),
    "present_neg": ("Present negative", dict(tense="present", mood="indicative", polarity="neg", voice=None)),
    "subj": ("Subjunctive", dict(mood="subjunctive", polarity=None)),
    "subj_neg": ("Subjunctive negative", dict(mood="subjunctive", polarity="neg")),
    "past": ("Simple past", dict(tense="past", aspect="perfective", polarity=None, voice=None, variant=None)),
    "past_neg": ("Past negative", dict(tense="past", aspect="perfective", polarity="neg")),
    "past_prog": ("Past progressive", dict(tense="past", aspect="progressive", polarity=None)),
    "past_prog_neg": ("Past progressive negative", dict(tense="past", aspect="progressive", polarity="neg")),
    "perfect": ("Present perfect", dict(tense="present_perfect", voice=None)),
    "pluperfect": ("Past perfect", dict(tense="past_perfect")),
    "passive_present": ("Passive present", dict(tense="present", voice="passive", polarity=None)),
    "passive_present_neg": ("Passive present negative", dict(tense="present", voice="passive", polarity="neg")),
    "passive_past": ("Passive past", dict(tense="past", voice="passive")),
    "imperative": ("Imperative", dict(mood="imperative", polarity=None)),
    "prohibitive": ("Prohibitive", dict(mood="imperative", polarity="neg")),
}
KMR_CELLS = {
    "present": ("Present", dict(tense="present", mood="indicative", polarity=None)),
    "present_neg": ("Present negative", dict(tense="present", mood="indicative", polarity="neg")),
    "subj": ("Subjunctive", dict(mood="subjunctive", polarity=None)),
    "subj_neg": ("Subjunctive negative", dict(mood="subjunctive", polarity="neg")),
    "past": ("Simple past", dict(tense="past", aspect="perfective", polarity=None)),
    "past_neg": ("Past negative", dict(tense="past", aspect="perfective", polarity="neg")),
    "past_prog": ("Past progressive", dict(tense="past", aspect="progressive", polarity=None)),
    "past_prog_neg": ("Past progressive negative", dict(tense="past", aspect="progressive", polarity="neg")),
    "perfect": ("Present perfect", dict(tense="present_perfect")),
    "pluperfect": ("Past perfect", dict(tense="past_perfect")),
    "imperative": ("Imperative", dict(mood="imperative", polarity=None)),
    "prohibitive": ("Prohibitive", dict(mood="imperative", polarity="neg")),
}
KMR_OBLIQUE = {"1sg": "min", "2sg": "te", "3sg": "wî / wê", "1pl": "me", "2pl": "we", "3pl": "wan"}


def cells_for(lang: Lang) -> dict:
    return CKB_CELLS if lang.code == "ckb" else KMR_CELLS


def verb_cell(lang: Lang, v, cell: str) -> dict[str, str]:
    """person -> form for one paradigm cell (kmr ``pl`` is expanded to 1pl/2pl/3pl)."""
    if cell not in cells_for(lang):
        raise TutorialError(f"[{lang.code}] unknown verb cell {cell!r}")
    filt = cells_for(lang)[cell][1]
    cands: dict[str, list[str]] = {}
    for f in lang.verbs.conjugate(v):
        ft = f.features
        if not all(ft.get(k) == val for k, val in filt.items()):
            continue
        p = ft.get("person") or ft.get("agent")
        if not p or p == "external":
            continue
        for q in (("1pl", "2pl", "3pl") if p == "pl" else p.split("|")):
            cands.setdefault(q, []).append(f.form)
    return {q: _preferred(lang, v, forms) for q, forms in cands.items()}


def _preferred(lang: Lang, v, forms: list[str]) -> str:
    """Several surface forms can fill one cell (the index accepts all of them).  Teach the standard one:
    for a Sorani preverb verb the agent clitic follows the preverb (هەڵمگرت rather than هەڵگرتم)."""
    if lang.code == "ckb" and v.preverb and not v.light and len(forms) > 1:
        for f in forms:
            if not f[len(v.preverb):].startswith(v.past):
                return f
    return forms[0]


def _cellfmt(lang: Lang, form: str | None, show: str) -> str:
    if not form:
        return "—"
    parts = [f"**{form}**"]
    if "translit" in show:
        parts.append(f"<sub>{lang.other(form)}</sub>")
    if "ipa" in show:
        parts.append(f"<sub>/{lang.ipa(form)}/</sub>")
    return "<br>".join(parts)


def _ergative(lang: Lang, v, cell: str) -> bool:
    return v.transitive and cell in ("past", "past_neg", "past_prog", "past_prog_neg", "perfect", "pluperfect")


def render_verb(lang: Lang, args: dict, body: str) -> str:
    v = lang.verb(args["verb"])
    cells = args.get("cells", "present").split(",")
    show = args.get("show", "translit")
    data = {c: verb_cell(lang, v, c) for c in cells}
    persons = [p for p in lang.persons if any(p[0] in d for d in data.values())]
    if all(c in ("imperative", "prohibitive") for c in cells):
        persons = [(p, lab) for p, lab in persons if p in ("2sg", "2pl")]
    erg = any(_ergative(lang, v, c) for c in cells)
    if lang.code == "kmr" and erg:
        head = "| person | agent (oblique) | object (direct) |"
        sep = "|---|---|---|"
    else:
        head, sep = "| person | pronoun |", "|---|---|"
    head += "".join(f" {cells_for(lang)[c][0]} |" for c in cells)
    sep += "---|" * len(cells)
    rows = [head, sep]
    for p, label in persons:
        if lang.code == "kmr" and erg:
            row = f"| {p} | {KMR_OBLIQUE[p]} | {label} |"
        else:
            row = f"| {p} | {label} |"
        row += "".join(f" {_cellfmt(lang, data[c].get(p), show)} |" for c in cells)
        rows.append(row)
    caption = f"*{args['verb']}* ({lang.other(args['verb'])}) “{lang.meaning(args['verb'])}”"
    caption += f" — present stem **{v.present}**, past stem **{v.past}**, {'transitive' if v.transitive else 'intransitive'}"
    if v.preverb:
        caption += f", preverb **{v.preverb}**"
    note = ""
    if erg and lang.code == "kmr":
        note = ("\n\n> Past tenses of a transitive verb are **ergative**: the agent is oblique and the verb agrees "
                "with the **object** (the *object* column), e.g. *min tu dîtî* “I saw you”.")
    elif erg and lang.code == "ckb":
        note = ("\n\n> Past tenses of a transitive verb are **ergative**: the person marker is the set-2 clitic "
                "(م ت ی مان تان یان) of the **agent**, not a verb ending.")
    return caption + "\n\n" + "\n".join(rows) + note


def render_verb_full(lang: Lang, inf: str) -> str:
    """A complete reference page for one verb."""
    v = lang.verb(inf)
    parts = [f"# {inf} — {lang.meaning(inf)}", "",
             "| | |", "|---|---|",
             f"| infinitive | **{inf}** ({lang.other(inf)}) /{lang.ipa(inf)}/ |",
             f"| meaning | {lang.meaning(inf)} |",
             f"| present stem | **{v.present}** |", f"| past stem | **{v.past}** |",
             f"| transitivity | {'transitive — ergative in past tenses' if v.transitive else 'intransitive'} |"]
    if v.preverb:
        parts.append(f"| preverb | **{v.preverb}** |")
    parts.append("")
    groups = [
        ("Present-stem forms", ["present", "present_neg"]), ("Subjunctive", ["subj", "subj_neg"]),
        ("Simple past", ["past", "past_neg"]), ("Past progressive", ["past_prog", "past_prog_neg"]),
        ("Perfect tenses", ["perfect", "pluperfect"]),
    ]
    if lang.code == "ckb" and v.transitive:
        groups.append(("Passive", ["passive_present", "passive_present_neg", "passive_past"]))
    groups.append(("Imperative", ["imperative", "prohibitive"]))
    for title, cells in groups:
        cells = [c for c in cells if verb_cell(lang, v, c)]
        if not cells:
            continue
        parts += [f"## {title}", "", render_verb(lang, {"verb": inf, "cells": ",".join(cells), "show": "translit,ipa"}, ""), ""]
    nonfinite = {}
    for f in lang.verbs.conjugate(v):
        if "form" in f.features:
            nonfinite.setdefault(f.features["form"].replace("_", " "), f.form)
        elif f.features.get("agent") == "external" and f.features.get("polarity") is None:
            key = f"{f.features.get('tense', '').replace('_', ' ')} {f.features.get('aspect', '')}".strip() + ", agent clitic elsewhere"
            nonfinite.setdefault(key, f.form)
    if nonfinite:
        parts += ["## Other forms", "", "| form | Kurdish | " + lang.other_name + " |", "|---|---|---|"]
        parts += [f"| {k} | **{x}** | {lang.other(x)} |" for k, x in nonfinite.items()]
        parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Other blocks
# ---------------------------------------------------------------------------

CKB_NOUN_CELLS = {
    "bare": "bare (generic)", "def.sg": "the … (sg)", "def.pl": "the … (pl)", "ind.sg": "a …", "pl": "… (pl)",
    "ezafe": "ezafe (… of / adj)", "dem": "ئەم / ئەو … ە", "ind.ezafe": "a … + adj", "def.sg.add": "the … too",
    **{f"def.sg+{p}": f"the … + {p}" for p in ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")},
    **{f"bare+{p}": f"… + {p}" for p in ("1sg", "2sg", "3sg", "1pl", "2pl", "3pl")},
}
KMR_NOUN_CELLS = {
    "def.dir.sg": "direct sg", "def.obl.sg": "oblique sg", "def.ez.sg": "ezafe sg",
    "ind.dir.sg": "indef. direct", "ind.obl.sg": "indef. oblique", "ind.ez.sg": "indef. ezafe",
    "def.dir.pl": "direct pl", "def.obl.pl": "oblique pl", "def.ez.pl": "ezafe pl",
    "ind.dir.pl": "indef. pl (rare)", "voc.sg": "vocative sg", "voc.pl": "vocative pl",
}


def noun_forms(lang: Lang, noun: str) -> dict[str, str | None]:
    return dict(lang.decline(noun) if lang.code == "ckb" else lang.decline(noun, lang.gender(noun)))


def render_noun(lang: Lang, args: dict, body: str) -> str:
    nouns = args["nouns"].split(",")
    labels = CKB_NOUN_CELLS if lang.code == "ckb" else KMR_NOUN_CELLS
    cells = args.get("cells", ",".join(labels)).split(",")
    for c in cells:
        if c not in labels:
            raise TutorialError(f"[{lang.code}] unknown noun cell {c!r}")
    gcol = lang.code == "kmr"
    head = "| noun | meaning |" + (" gender |" if gcol else "") + "".join(f" {labels[c]} |" for c in cells)
    sep = "|---|---|" + ("---|" if gcol else "") + "---|" * len(cells)
    rows = [head, sep]
    for n in nouns:
        forms = noun_forms(lang, n)
        row = f"| **{n}** | {lang.meaning(n)} |" + (f" {lang.gender(n)} |" if gcol else "")
        row += "".join(f" {_cellfmt(lang, forms.get(c), args.get('show', 'translit'))} |" for c in cells)
        rows.append(row)
    return "\n".join(rows)


def render_noun_persons(lang: Lang, args: dict, body: str) -> str:
    """ckb: one noun with each personal clitic, bare and definite."""
    n = args["noun"]
    forms = noun_forms(lang, n)
    rows = [f"*{n}* “{lang.meaning(n)}”", "", "| person | pronoun | my/your… + noun | the noun + clitic |", "|---|---|---|---|"]
    for p, label in lang.persons:
        rows.append(f"| {p} | {label} | {_cellfmt(lang, forms[f'bare+{p}'], 'translit')} | "
                    f"{_cellfmt(lang, forms[f'def.sg+{p}'], 'translit')} |")
    return "\n".join(rows)


def render_words(lang: Lang, args: dict, body: str) -> str:
    words = args["words"].split(",")
    rows = [f"| Kurdish | {lang.other_name} | IPA | syllables | meaning |", "|---|---|---|---|---|"]
    for w in words:
        rows.append(f"| **{w}** | {lang.other(w)} | /{lang.ipa(w)}/ | {'.'.join(lang.syllables(w))} | {lang.meaning(w)} |")
    return "\n".join(rows)


def _lines(body: str) -> list[tuple[str, str]]:
    out = []
    for line in body.strip().splitlines():
        if line.strip():
            kurdish, _, english = line.partition("|")
            out.append((kurdish.strip(), english.strip()))
    return out


def render_sentences(lang: Lang, args: dict, body: str) -> str:
    with_ipa = args.get("ipa") == "1"
    head = f"| # | Kurdish | {lang.other_name} |" + (" IPA |" if with_ipa else "") + " English |"
    rows = [head, "|---|---|---|" + ("---|" if with_ipa else "") + "---|"]
    for i, (k, e) in enumerate(_lines(body), 1):
        rows.append(f"| {i} | {k} | {lang.text_other(k)} |" + (f" {lang.text_ipa(k)} |" if with_ipa else "") + f" {e} |")
    return "\n".join(rows)


def render_analyze(lang: Lang, args: dict, body: str) -> str:
    an = lang.analyzer()
    rows = ["| word | segmentation | morpheme tags | lemma | features |", "|---|---|---|---|---|"]
    for w in args["words"].split(","):
        a = an.best(w)
        if a is None:
            raise TutorialError(f"[{lang.code}] no analysis for {w!r}")
        feats = ", ".join(f"{k}={v}" for k, v in a.features.items() if k not in ("past_stem", "present_stem"))
        rows.append(f"| **{w}** | {a.segmentation} | {a.gloss} | {a.lemma} | {feats or '—'} |")
    return "\n".join(rows)


def render_ergativity(lang: Lang, args: dict, body: str) -> str:
    from zimankit.skills_kmr.syntax import detect_alignment

    rows = ["| sentence | English | alignment | agent | object | verb agrees with | check |", "|---|---|---|---|---|---|---|"]
    for k, e in _lines(body):
        r = detect_alignment(k).to_dict()
        ag = r.get("agent") or {}
        ob = r.get("object") or {}
        fmt = lambda x: f"{x['token']} ({x['case']})" if x else "—"
        check = "✔" if r.get("agreement_ok") else "✘ " + "; ".join(r.get("notes") or [])
        rows.append(f"| *{k}* | {e} | {r.get('alignment', '—')} | {fmt(ag)} | {fmt(ob)} | "
                    f"{r.get('controller', '—')} ({r.get('verb_person', '?')}) | {check} |")
    return "\n".join(rows)


def render_normalize(lang: Lang, args: dict, body: str) -> str:
    """Raw text -> normalised text -> the validator's complaints about each remaining word."""
    if lang.code == "ckb":
        from zimankit.skills_ckb.orthography import normalize, validate_word
    else:
        from zimankit.skills_kmr.orthography import normalize, validate_word
    rows = ["| typed text | after `normalize()` | problems still found by `validate_word()` | note |", "|---|---|---|---|"]
    for raw, note in _lines(body):
        fixed = normalize(raw)
        probs = sorted({f"{t.text}: {'; '.join(validate_word(t.text))}" for t in tokenize(fixed)
                        if t.kind == "word" and validate_word(t.text)})
        rows.append(f"| {raw} | {fixed} | {'<br>'.join(probs) or '—'} | {note} |")
    return "\n".join(rows)


def render_alphabet(lang: Lang, args: dict, body: str) -> str:
    zwj = "‍"
    if lang.code == "ckb":
        rows = ["| letter | isolated | initial | medial | final | Latin | IPA | joins left? | example | meaning |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for letter, latin, ipa, example in CKB_ALPHABET:
            joins = letter[-1] not in CKB_NON_JOINING
            ini = letter + zwj if joins else letter
            med = zwj + letter + zwj if joins else zwj + letter
            rows.append(f"| **{letter}** | {letter} | {ini} | {med} | {zwj}{letter} | {latin} | /{ipa}/ | "
                        f"{'yes' if joins else '**no**'} | {example} ({lang.other(example)}) | {lang.meaning(example)} |")
    else:
        rows = ["| letter | Arabic-script equivalent | IPA | example | example (Arabic script) | meaning |",
                "|---|---|---|---|---|---|"]
        for letter, arabic, ipa, example in KMR_ALPHABET:
            rows.append(f"| **{letter.upper()} {letter}** | {arabic} | /{ipa}/ | {example} | {lang.other(example)} | {lang.meaning(example)} |")
    return "\n".join(rows)


CKB_NON_JOINING = set("ادرڕزژوۆە")
# letter, Latin (Hawar-style), IPA, example word
CKB_ALPHABET = (
    ("ئ", "—", "ʔ", "ئاو"), ("ا", "a", "aː", "باران"), ("ب", "b", "b", "باوک"), ("پ", "p", "p", "پیاو"),
    ("ت", "t", "t", "تۆ"), ("ج", "c", "dʒ", "جوان"), ("چ", "ç", "tʃ", "چاو"), ("ح", "ḧ", "ħ", "حەوت"),
    ("خ", "x", "x", "خەو"), ("د", "d", "d", "دار"), ("ر", "r", "ɾ", "بەرد"), ("ڕ", "rr", "r", "ڕۆژ"),
    ("ز", "z", "z", "زمان"), ("ژ", "j", "ʒ", "ژن"), ("س", "s", "s", "سەر"), ("ش", "ş", "ʃ", "شار"),
    ("ع", "'", "ʕ", "عەقڵ"), ("غ", "ẍ", "ɣ", "غەریب"), ("ف", "f", "f", "فڕین"), ("ڤ", "v", "v", "ڤیدیۆ"),
    ("ق", "q", "q", "قەڵەم"), ("ک", "k", "k", "کتێب"), ("گ", "g", "ɡ", "گوڵ"), ("ل", "l", "l", "لاو"),
    ("ڵ", "ll", "ɫ", "ماڵ"), ("م", "m", "m", "مانگ"), ("ن", "n", "n", "نان"), ("ه", "h", "h", "هەوا"),
    ("ە", "e", "æ", "ئەسپ"), ("و", "w / u", "w, u", "وڵات"), ("وو", "û", "uː", "بوون"), ("ۆ", "o", "oː", "ڕۆژ"),
    ("ی", "y / î", "j, iː", "شیر"), ("ێ", "ê", "eː", "سێو"),
)
KMR_ALPHABET = (
    ("a", "ا", "aː", "av"), ("b", "ب", "b", "bav"), ("c", "ج", "dʒ", "ciwan"), ("ç", "چ", "tʃ", "çav"),
    ("d", "د", "d", "dar"), ("e", "ە", "ɛ", "dest"), ("ê", "ێ", "eː", "êvar"), ("f", "ف", "f", "firîn"),
    ("g", "گ", "ɡ", "gul"), ("h", "ه", "h", "hesp"), ("i", "(unwritten)", "ɪ", "jin"), ("î", "ی", "iː", "şîr"),
    ("j", "ژ", "ʒ", "jin"), ("k", "ک", "k", "kitêb"), ("l", "ل", "l", "ling"), ("m", "م", "m", "mal"),
    ("n", "ن", "n", "nan"), ("o", "ۆ", "oː", "roj"), ("p", "پ", "p", "pirtûk"), ("q", "ق", "q", "qelem"),
    ("r", "ر / ڕ", "ɾ, r", "bira"), ("s", "س", "s", "sêv"), ("ş", "ش", "ʃ", "şev"), ("t", "ت", "t", "tu"),
    ("u", "و", "ʊ", "kurd"), ("û", "وو", "uː", "çûn"), ("v", "ڤ", "v", "av"), ("w", "و", "w", "welat"),
    ("x", "خ", "x", "xew"), ("y", "ی", "j", "yek"), ("z", "ز", "z", "ziman"),
)


# ---------------------------------------------------------------------------
# Lessons, navigation and reference pages
# ---------------------------------------------------------------------------


@dataclass
class Lesson:
    path: Path
    lang: str
    level: str
    number: int
    title: str


def lessons_of(lang: str) -> list[Lesson]:
    out = []
    for folder, (level, _) in LEVELS.items():
        for p in sorted((TUT / lang / folder).glob("[0-9][0-9]-*.md")):
            m = re.search(r"^# (.+)$", p.read_text(encoding="utf-8"), re.M)
            if not m:
                raise TutorialError(f"{p} has no title")
            out.append(Lesson(p, lang, level, int(p.name[:2]), m.group(1)))
    return sorted(out, key=lambda l: l.number)


def rel(src: Path, dst: Path) -> str:
    import os

    return os.path.relpath(dst, src.parent).replace(os.sep, "/")


def render_lessons(lang: Lang, args: dict, body: str, here: Path) -> str:
    codes = [lang.code] if lang else list(LANG_NAMES)
    out = []
    for code in codes:
        if not lang:
            out += [f"### {LANG_NAMES[code]}", ""]
        for folder, (level, badge) in LEVELS.items():
            ls = [l for l in lessons_of(code) if l.level == level]
            out += [f"**{badge}**", ""]
            out += [f"* [{l.title}]({rel(here, l.path)})" for l in ls] or ["*(coming soon)*"]
            out.append("")
    return "\n".join(out).rstrip()


def render_verb_index(lang: Lang, args: dict, body: str, here: Path) -> str:
    rows = [f"| verb | {lang.other_name} | meaning | type | present | past (3sg) |", "|---|---|---|---|---|---|"]
    for inf in reference_verbs(lang):
        v = lang.verb(inf)
        pres = verb_cell(lang, v, "present").get("1sg", "—")
        past = verb_cell(lang, v, "past").get("3sg", "—")
        page = TUT / lang.code / "reference" / "verbs" / f"{verb_slug(lang, inf)}.md"
        rows.append(f"| [**{inf}**]({rel(here, page)}) | {lang.other(inf)} | {lang.meaning(inf)} | "
                    f"{'transitive' if v.transitive else 'intransitive'} | {pres} | {past} |")
    return "\n".join(rows)


def verb_slug(lang: Lang, inf: str) -> str:
    latin = lang.other(inf) if lang.code == "ckb" else inf
    return re.sub(r"[^a-z0-9]+", "-", latin.lower().translate(str.maketrans("çêîşûéáíú", "ceisueaiu"))).strip("-")


def reference_verbs(lang: Lang) -> list[str]:
    core = [v.infinitive for v in lang.verbs.load_core_verbs()]
    extra = {"ckb": ["هەڵگرتن", "ڕاگەیاندن", "دەستپێکردن", "کردنەوە", "گەڕانەوە"],
             "kmr": ["rabûn", "hilgirtin", "vekirin", "derketin", "rûniştin"]}[lang.code]
    return list(dict.fromkeys(core + extra))


RENDERERS = {
    "verb": render_verb, "noun": render_noun, "noun_persons": render_noun_persons, "words": render_words,
    "sentences": render_sentences, "analyze": render_analyze, "ergativity": render_ergativity,
    "alphabet": render_alphabet, "normalize": render_normalize,
}
PAGE_RENDERERS = {"lessons": render_lessons, "verb_index": render_verb_index}


def fill_blocks(text: str, lang: Lang | None, here: Path) -> str:
    def sub(m: re.Match) -> str:
        name, rest = m.group(1), m.group(2)
        first, _, body = rest.partition("\n")
        args = dict(re.findall(r"(\w+)=(\S+)", first))
        if name in PAGE_RENDERERS:
            out = PAGE_RENDERERS[name](lang, args, body, here)
        elif name in RENDERERS:
            if lang is None:
                raise TutorialError(f"{here}: block {name} needs a language folder")
            out = RENDERERS[name](lang, args, body)
        else:
            raise TutorialError(f"{here}: unknown block {name!r}")
        return f"<!-- gen:{name}{rest}-->\n{out}\n<!-- /gen -->"

    return BLOCK.sub(sub, text)


def strip_nav(text: str) -> str:
    text = re.sub(rf"{TOP}.*?{TOP}\n*", "", text, flags=re.S)
    text = re.sub(r"\n\*\*(?:On this page|Level):\*\*[^\n]*\n", "\n", text)
    text = re.sub(r"^(# .+\n)\n+", r"\1\n", text, count=1, flags=re.M)
    return re.sub(rf"\n*{BOTTOM}.*?{BOTTOM}\n?", "\n", text, flags=re.S).rstrip() + "\n"


def slug(h: str) -> str:
    h = re.sub(r"<[^>]+>", "", h).lower()
    return re.sub(r"[^\w\- ]", "", h).strip().replace(" ", "-")


def add_nav(text: str, lesson: Lesson, prev_: Lesson | None, next_: Lesson | None, total: int) -> str:
    here = lesson.path
    home = TUT / lesson.lang / "README.md"
    links = [f"[⌂ {LANG_NAMES[lesson.lang]} course]({rel(here, home)})"]
    if prev_:
        links.insert(0, f"[← {prev_.number}. {prev_.title.split('. ', 1)[-1]}]({rel(here, prev_.path)})")
    if next_:
        links.append(f"[{next_.number}. {next_.title.split('. ', 1)[-1]} →]({rel(here, next_.path)})")
    bar = " · ".join(links)
    badge = dict(LEVELS.values())[lesson.level]
    body = strip_nav(text)
    heads = re.findall(r"^## (.+)$", body, re.M)
    toc = f"\n**Level:** {badge} · lesson {lesson.number} of {total}\n"
    if len(heads) >= 3:
        toc += "\n**On this page:** " + " · ".join(f"[{h}](#{slug(h)})" for h in heads) + "\n"
    body = re.sub(r"^(# .+\n)", lambda m: m.group(1) + toc, body, count=1, flags=re.M)
    return f"{TOP}\n{bar}\n{TOP}\n\n{body}\n{BOTTOM}\n---\n{bar}\n{BOTTOM}\n"


def reference_pages(lang: Lang) -> dict[Path, str]:
    base = TUT / lang.code / "reference"
    pages: dict[Path, str] = {}
    back = f"[⌂ {LANG_NAMES[lang.code]} course](../../README.md) · [all verbs](README.md)"
    for inf in reference_verbs(lang):
        path = base / "verbs" / f"{verb_slug(lang, inf)}.md"
        pages[path] = f"{back}\n\n{render_verb_full(lang, inf)}\n---\n{back}\n"
    # vocabulary
    rows = [f"| Kurdish | {lang.other_name} | IPA | meaning |" + (" gender |" if lang.code == "kmr" else ""),
            "|---|---|---|---|" + ("---|" if lang.code == "kmr" else "")]
    for w in sorted(lang.vocab, key=lambda x: x.lower()):
        meaning, note = lang.vocab[w]
        rows.append(f"| **{w}** | {lang.other(w)} | /{lang.ipa(w)}/ | {meaning} |" + (f" {note} |" if lang.code == "kmr" else ""))
    pages[base / "vocabulary.md"] = (
        f"[⌂ {LANG_NAMES[lang.code]} course](../README.md)\n\n# Vocabulary\n\n"
        f"Every word used in the {LANG_NAMES[lang.code]} lessons ({len(lang.vocab)} entries). IPA and "
        f"{lang.other_name} spelling are generated by zimankit.\n\n" + "\n".join(rows) + "\n"
    )
    # nouns
    nouns = [w for w, (_, note) in lang.vocab.items() if note in ("f", "m", "n")]
    labels = CKB_NOUN_CELLS if lang.code == "ckb" else KMR_NOUN_CELLS
    blocks = []
    for n in nouns:
        forms = noun_forms(lang, n)
        blocks += [f"## {n} — {lang.meaning(n)}" + (f" ({lang.gender(n)})" if lang.code == "kmr" else ""), "",
                   f"| form | Kurdish | {lang.other_name} |", "|---|---|---|"]
        blocks += [f"| {labels[c]} | **{f}** | {lang.other(f)} |" for c, f in forms.items() if f]
        blocks.append("")
    pages[base / "nouns.md"] = (
        f"[⌂ {LANG_NAMES[lang.code]} course](../README.md)\n\n# Noun declension tables\n\n"
        f"Generated by `decline()` in `zimankit/skills_{lang.code}/morphology.py` — the same suffix rules the "
        f"analyzer uses.\n\n" + "\n".join(blocks)
    )
    return pages


def build() -> dict[Path, str]:
    langs = load_langs()
    out: dict[Path, str] = {}
    for code, lang in langs.items():
        ls = lessons_of(code)
        for i, l in enumerate(ls):
            text = fill_blocks(l.path.read_text(encoding="utf-8"), lang, l.path)
            out[l.path] = add_nav(text, l, ls[i - 1] if i else None, ls[i + 1] if i + 1 < len(ls) else None, len(ls))
        for p in (TUT / code).rglob("*.md"):
            if p not in out and "verbs" not in p.parts[-2:-1] and p.name not in ("vocabulary.md", "nouns.md"):
                out[p] = fill_blocks(p.read_text(encoding="utf-8"), lang, p)
        out.update(reference_pages(lang))
        idx = TUT / code / "reference" / "verbs" / "README.md"
        out[idx] = fill_blocks(idx.read_text(encoding="utf-8"), lang, idx)
    hub = TUT / "README.md"
    out[hub] = fill_blocks(hub.read_text(encoding="utf-8"), None, hub)
    for code, lang in langs.items():
        if lang.missing:
            raise TutorialError(f"[{code}] add to docs/tutorials/_data/{code}_vocab.tsv: " + ", ".join(sorted(lang.missing)))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if any file is out of date")
    args = ap.parse_args(argv)
    try:
        pages = build()
    except TutorialError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    stale = [p for p, text in pages.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        return 1 if stale else 0
    for p in stale:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(pages[p], encoding="utf-8")
    print(f"{len(pages)} pages, {len(stale)} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
