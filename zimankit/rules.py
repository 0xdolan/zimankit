"""Export the grammar rules each skill implements as a structured JSON document.

The JSON is generated from the same tables the code uses (alphabets,
G2P maps, suffix slots, verb paradigms), so it can never drift from the
implementation.  It is intended for testing, for porting the rules to other
languages, and as machine-readable documentation.
"""

from __future__ import annotations

import json
from pathlib import Path

from .shared_utils import unicode_tables as U
from .shared_utils.text_helpers import PATTERNS


def _ckb() -> dict:
    from .skills_ckb import morphology as M
    from .skills_ckb import phonology_ipa as P
    from .skills_ckb import verbs as V

    analyzer = M.CkbAnalyzer()
    model = next(v for v in V.default_index().verbs.values() if v.infinitive == "کردن")
    return {
        "language": "ckb",
        "name": "Central Kurdish (Sorani)",
        "script": "Arabic-based Kurdish alphabet (34 letters)",
        "alphabet": [{"letter": l, "codepoints": cp, "name": n} for l, cp, n in U.CKB_ALPHABET],
        "orthography": {
            "char_map": {f"U+{ord(k):04X}": v for k, v in U.CKB_CHAR_MAP.items()},
            "sequence_map": {" ".join(f"U+{ord(c):04X}" for c in k): v for k, v in U.CKB_SEQUENCE_MAP.items()},
            "contextual_rules": [
                {"id": "initial_r", "rule": "word-initial ر -> ڕ", "example": ["رۆژ", "ڕۆژ"]},
                {"id": "initial_hamza", "rule": "word-initial vowel letter gets ئ", "example": ["ەمە", "ئەمە"]},
                {"id": "legacy_ae", "rule": "ه + ZWNJ -> ە; in legacy-encoded text word-final ه -> ە", "example": ["به‌ڕێوه‌به‌ر", "بەڕێوەبەر"]},
                {"id": "zwnj", "rule": "micro-spaces -> ZWNJ; ZWNJ kept only between two joining letters"},
                {"id": "squeeze", "rule": "ەە -> ە, ڕڕ -> ڕ, ڵڵ -> ڵ, ووو -> وو"},
            ],
        },
        "phonology": {
            "consonants": P.CONSONANTS,
            "vowels": {**P.VOWELS, "وو": "uː", "و (C_C)": "u", "ی (C_C)": "iː", "bizroke (unwritten)": "ɯ"},
            "semivowel_resolution": [
                "و / ی after a vowel letter -> /w/ /j/",
                "و / ی before a vowel letter -> /w/ /j/ (onset cluster Cw / Cj)",
                "و between consonants or word-finally -> /u/; ی -> /iː/",
                "وو -> /uː/, یی -> /iː/; a glide is inserted before a following vowel",
            ],
            "phonotactics": {
                "initial_onsets": "C, C+glide, sibilant+stop",
                "medial_onsets": "C, C+glide",
                "final_codas": "falling sonority (rd, nd, st, ʃk)",
                "medial_codas": "fricative+stop, nasal+stop, glide+C",
                "bizroke": "an epenthetic /ɯ/ breaks every other cluster, carved right-to-left",
            },
            "examples": {w: P.to_ipa(w) for w in ("پیاوەکە", "کتێبەکەم", "کوردستان", "بردن", "خواردن", "هاتووە", "ئنجا")},
        },
        "morphology": {
            "nominal_slots": [
                {"slot": name, "affixes": [{"form": a.form, "tag": a.tag, "after": a.after, "features": dict(a.features)} for a in afs]}
                for name, afs in M.SLOTS
            ],
            "proclitics": [{"form": f, "tag": t} for f, t in M.PROCLITICS],
            "examples": {w: (lambda a: {"lemma": a.lemma, "seg": a.segmentation, "gloss": a.gloss, "features": a.features})(analyzer.best(w))
                         for w in ("پیاوەکە", "کتێبەکەم", "دەرگاکە", "دەکەم", "نەمکرد", "کردوومە")},
        },
        "verbs": {
            "agreement_set_1": {"1sg": "م", "2sg": "یت", "3sg": "ێت / ات", "1pl": "ین", "2pl": "ن", "3pl": "ن"},
            "agreement_set_2_enclitics": V.SET2,
            "alignment": "past tenses of transitive verbs are ergative: the agent is cross-referenced by a set-2 enclitic",
            "preverbs": list(V.PREVERBS),
            "model_paradigm": [{"form": f.form, **{k: v for k, v in f.features.items() if k != "pos"}} for f in V.conjugate(model)],
        },
        "regex": {k: v for k, v in PATTERNS.items() if k.startswith("ckb")},
    }


def _kmr() -> dict:
    from .skills_kmr import morphology as M
    from .skills_kmr import phonology_ipa as P
    from .skills_kmr import syntax as S
    from .skills_kmr import verbs as V

    analyzer = M.KmrAnalyzer()
    model = next(v for v in V.default_index().verbs.values() if v.infinitive == "dîtin")
    return {
        "language": "kmr",
        "name": "Northern Kurdish (Kurmanji)",
        "script": "Hawar Latin alphabet (31 letters)",
        "alphabet": [{"letter": l, "codepoint": cp, "name": n} for l, cp, n in U.KMR_ALPHABET],
        "orthography": {
            "char_map": U.KMR_CHAR_MAP,
            "casing": "Kurdish-aware: I<->i, Î<->î (never Turkish İ/ı)",
            "digraphs": {"xw": "xʷ", "rr": "r (trill)", "ḧ": "ħ", "ẍ": "ɣ", "'": "ʕ / unaspirated marker"},
        },
        "phonology": {
            "vowels": P.VOWELS,
            "consonants": P.CONSONANTS,
            "rules": [
                "word-initial r and rr -> trill /r/, other r -> tap /ɾ/",
                "xw -> /xʷ/",
                "final closed syllable i in polysyllables -> reduced /ɯ/ (suffix -in)",
                "narrow: p t k ç aspirated unless followed by an apostrophe; n -> ŋ before velars",
            ],
            "examples": {w: P.to_ipa(w) for w in ("jinekê", "dîtin", "xwarin", "rojname", "zivistan")},
        },
        "morphology": {
            "inflections": [{"form": s, "tag": t, "features": f, "after": n} for s, t, f, n in M.INFLECTIONS],
            "derivations": [{"form": s, "tag": t, "pos": p} for s, t, p in M.DERIVATIONS],
            "examples": {w: (lambda a: {"lemma": a.lemma, "seg": a.segmentation, "features": a.features})(analyzer.best(w))
                         for w in ("jinekê", "dîtin", "dibînim", "hatim", "nizanim")},
        },
        "verbs": {
            "endings": {"1sg": "-im / -m", "2sg": "-î / -yî", "3sg": "-e (present) / -ø (past)", "pl": "-in / -n"},
            "preverbs": list(V.PREVERBS),
            "model_paradigm": [{"form": f.form, **{k: v for k, v in f.features.items() if k != "pos"}} for f in V.conjugate(model)],
        },
        "syntax": {
            "split_ergativity": {
                "present_stem_tenses": "nominative-accusative: subject in direct case, verb agrees with subject",
                "past_stem_tenses_transitive": "ergative: agent in oblique case, object in direct case, verb agrees with object",
                "examples": [S.detect_alignment(s).to_dict() for s in ("Ez te dibînim.", "Min tu dîtî.", "Min ew dîtin.", "Ez hatim.")],
            }
        },
        "regex": {k: v for k, v in PATTERNS.items() if k.startswith("kmr")},
    }


def export_rules(path: str | Path, lang: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _ckb() if lang == "ckb" else _kmr()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
