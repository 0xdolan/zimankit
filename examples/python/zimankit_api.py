#!/usr/bin/env python3
"""The full library: analysis, IPA, transliteration, verbs, ergativity, LID.

Run from the project root:  python examples/python/zimankit_api.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from zimankit import analyze, identify, normalize, to_ipa  # noqa: E402
from zimankit.skills_ckb.phonology_ipa import syllables, to_latin  # noqa: E402
from zimankit.skills_kmr.syntax import detect_alignment  # noqa: E402
from zimankit.skills_kmr.translit import to_arabic  # noqa: E402
from zimankit.skills_ckb import verbs as ckb_verbs  # noqa: E402

print(normalize("به‌ڕێوه‌به‌رایه‌تی ئاوی سلێمانی 2015"))
for w in ["کتێبەکەم", "پیاوەکە", "دەکەم", "نەمکرد", "jinekê", "dîtin", "dibînim"]:
    a = analyze(w)[0]
    print(f"{w:10} lemma={a.lemma:8} pos={a.pos:5} seg={a.segmentation:14} ipa={to_ipa(w)}")
print(syllables("کوردستان"), to_latin("کوردستان"), to_arabic("zimanê kurdî"))
print([f.form for f in ckb_verbs.conjugate(ckb_verbs.default_index().verbs["کردن"])][:8])
print(json.dumps(detect_alignment("Min tu dîtî.").to_dict(), ensure_ascii=False)[:160])
print(identify("Ma yew roje şima ra vat ke ziwanê ma zaf rind o").lang)
