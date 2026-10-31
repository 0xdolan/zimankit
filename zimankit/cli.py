"""Command-line interface: ``python -m zimankit <command> ...`` or ``zimankit ...``.

Every command reads its words/text from arguments, or from stdin when none
are given, so it composes with shell pipelines.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import asdict


def _inputs(args: list[str]) -> Iterable[str]:
    if args:
        yield from args
    else:
        for line in sys.stdin:
            line = line.rstrip("\n")
            if line:
                yield line


def _lang_of(text: str, forced: str | None) -> str:
    if forced:
        return forced
    from .shared_utils.text_helpers import detect_script

    return "ckb" if detect_script(text) == "arabic" else "kmr"


def cmd_normalize(a) -> None:
    for t in _inputs(a.text):
        lang = _lang_of(t, a.lang)
        if lang == "ckb":
            from .skills_ckb.orthography import normalize
        else:
            from .skills_kmr.orthography import normalize
        print(normalize(t))


def cmd_tokenize(a) -> None:
    from .shared_utils.tokenizer import tokenize

    for t in _inputs(a.text):
        print(" ".join(tok.text for tok in tokenize(t)) if not a.json else json.dumps([asdict(tok) for tok in tokenize(t)], ensure_ascii=False))


def cmd_lid(a) -> None:
    from .shared_utils.lid import identify

    for t in _inputs(a.text):
        r = identify(t)
        print(json.dumps({"lang": r.lang, "script": r.script, "confidence": r.confidence}, ensure_ascii=False) if a.json else f"{r.lang}\t{r.confidence}\t{t[:60]}")


def cmd_ipa(a) -> None:
    for t in _inputs(a.text):
        lang = _lang_of(t, a.lang)
        if lang == "ckb":
            from .skills_ckb.phonology_ipa import G2POptions, text_to_ipa

            print(text_to_ipa(t, G2POptions(mark_epenthesis=not a.plain, syllable_dots=a.syllables)))
        else:
            from .skills_kmr.phonology_ipa import KmrG2POptions, text_to_ipa

            print(text_to_ipa(t, KmrG2POptions(narrow=a.narrow, syllable_dots=a.syllables)))


def cmd_translit(a) -> None:
    from .shared_utils.tokenizer import tokenize

    for t in _inputs(a.text):
        lang = _lang_of(t, a.lang)
        if lang == "ckb":
            from .skills_ckb.phonology_ipa import to_latin as conv
        else:
            from .skills_kmr.translit import to_arabic as conv
        print(" ".join(conv(tok.text) if tok.kind == "word" else tok.text for tok in tokenize(t)))


def _analyzer(lang: str):
    if lang == "ckb":
        from .skills_ckb.morphology import CkbAnalyzer

        return CkbAnalyzer()
    from .skills_kmr.morphology import KmrAnalyzer

    return KmrAnalyzer()


def cmd_analyze(a) -> None:
    from .shared_utils.tokenizer import words

    cache: dict[str, object] = {}
    for t in _inputs(a.text):
        lang = _lang_of(t, a.lang)
        an = cache.setdefault(lang, _analyzer(lang))
        for w in words(t):
            res = an.analyze(w)[: a.top]  # type: ignore[attr-defined]
            if a.json:
                print(json.dumps({"token": w, "analyses": [r.to_dict() for r in res]}, ensure_ascii=False))
            else:
                for r in res:
                    print(f"{w}\t{r.lemma}\t{r.pos}\t{r.segmentation}\t{r.gloss}\t{json.dumps(r.features, ensure_ascii=False)}\t{r.score}")


def cmd_conjugate(a) -> None:
    lang = _lang_of(a.infinitive, a.lang)
    if lang == "ckb":
        from .skills_ckb import verbs as V
    else:
        from .skills_kmr import verbs as V
    idx = V.default_index()
    v = idx.verbs.get(a.infinitive)
    if v is None:
        known = {x.infinitive: x for x in idx.verbs.values() if not x.preverb}
        v = V.make_verb(a.infinitive, None if a.transitive is None else a.transitive == "yes", a.present, "guess", known)
    if v is None:
        sys.exit(f"cannot build a paradigm for {a.infinitive!r}")
    for f in V.conjugate(v):
        feats = ",".join(f"{k}={x}" for k, x in f.features.items() if k != "pos")
        print(f"{f.form}\t{feats}")


def cmd_ergativity(a) -> None:
    from .skills_kmr.syntax import detect_alignment

    for t in _inputs(a.text):
        print(json.dumps(detect_alignment(t).to_dict(), ensure_ascii=False))


def cmd_parse(a) -> None:
    from .dependency import parse

    for t in _inputs(a.text):
        p = parse(t, a.lang)
        if a.json:
            print(json.dumps(p.to_dict(), ensure_ascii=False))
            continue
        for w in p.tokens:
            print(f"{w.id}\t{w.text}\t{w.lemma}\t{w.upos}\t{w.head}\t{w.deprel}")
        print()


def cmd_validate(a) -> None:
    for t in _inputs(a.text):
        lang = _lang_of(t, a.lang)
        if lang == "ckb":
            from .skills_ckb.orthography import normalize_word, validate_word
        else:
            from .skills_kmr.orthography import normalize_word, validate_word
        w = normalize_word(t)
        p = validate_word(w)
        print(f"{t}\t{w}\t{'OK' if not p else '; '.join(p)}")


def cmd_rules(a) -> None:
    from .rules import export_rules

    print(export_rules(a.out or f"output/{a.lang}/grammar_rules_{a.lang}.json", a.lang))


def main(argv: list[str] | None = None) -> int:
    from . import __version__

    ap = argparse.ArgumentParser(prog="zimankit", description="Kurdish (ckb / kmr) NLP skills")
    ap.add_argument("--version", action="version", version=f"zimankit {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_, text=True):
        p = sub.add_parser(name, help=help_)
        if text:
            p.add_argument("text", nargs="*")
        p.add_argument("--lang", choices=["ckb", "kmr"])
        p.set_defaults(fn=fn)
        return p

    add("normalize", cmd_normalize, "orthographic normalisation")
    add("tokenize", cmd_tokenize, "word tokenisation").add_argument("--json", action="store_true")
    add("lid", cmd_lid, "language identification").add_argument("--json", action="store_true")
    p = add("ipa", cmd_ipa, "grapheme-to-phoneme (IPA)")
    p.add_argument("--narrow", action="store_true", help="kmr: aspiration, ŋ")
    p.add_argument("--plain", action="store_true", help="ckb: do not mark the inferred bizroke")
    p.add_argument("--syllables", action="store_true")
    add("translit", cmd_translit, "ckb Arabic->Latin, kmr Latin->Arabic")
    p = add("analyze", cmd_analyze, "morphological analysis")
    p.add_argument("--top", type=int, default=1)
    p.add_argument("--json", action="store_true")
    p = add("conjugate", cmd_conjugate, "full verb paradigm", text=False)
    p.add_argument("infinitive")
    p.add_argument("--present", help="present stem for verbs not in the reference list")
    p.add_argument("--transitive", choices=["yes", "no"])
    add("ergativity", cmd_ergativity, "kmr clause alignment / agreement check")
    add("validate", cmd_validate, "orthographic validation of words")
    add("parse", cmd_parse, "sentence structure: head and relation of each word").add_argument("--json", action="store_true")
    p = add("rules", cmd_rules, "export grammar_rules_<lang>.json", text=False)
    p.add_argument("--out")
    a = ap.parse_args(argv)
    if a.cmd == "rules" and not a.lang:
        ap.error("rules needs --lang")
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
