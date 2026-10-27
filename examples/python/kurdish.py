#!/usr/bin/env python3
"""Portable core of the zimankit rules (no dependencies). Run: python3 kurdish.py"""
import re
import unicodedata

CKB_MAP = str.maketrans({"ك": "ک", "ي": "ی", "ى": "ی", "ھ": "ه", "ة": "ە"})
KMR_MAP = str.maketrans({"é": "ê", "è": "ê", "ë": "ê", "í": "î", "ì": "î", "ï": "î",
                         "ú": "û", "ù": "û", "ü": "û", "ı": "i", "ș": "ş"})
CKB_SPLIT = re.compile(r"^(.+?)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$")
KMR_SPLIT = re.compile(r"^(.+?)(ekê|ekî|eke|ek|ên|an|a|ê|î)$")
KMR_FEATS = {"ekê": "indef.obl.f", "ekî": "indef.obl.m", "eke": "indef.ezafe", "ek": "indef",
             "ên": "ezafe.pl", "an": "obl.pl", "a": "ezafe.f", "ê": "ezafe.m|obl.f", "î": "obl.m"}


def normalize_ckb(s: str) -> str:
    s = unicodedata.normalize("NFC", s).translate(CKB_MAP).replace("ه‌", "ە")
    return re.sub(r"(^|\s)ر", r"\1ڕ", s)


def normalize_kmr(s: str) -> str:
    return unicodedata.normalize("NFC", s).translate(KMR_MAP)


def is_arabic(s: str) -> bool:
    return any("؀" <= c <= "ۿ" for c in s)


for line in open(__file__.rsplit("/", 2)[0] + "/inputs.txt", encoding="utf-8"):
    w = line.strip()
    if not w:
        continue
    if is_arabic(w):
        n = normalize_ckb(w)
        m = CKB_SPLIT.match(n)
        seg = f"stem={m[1]} def={m[2]} clitic={m[3] or '-'}" if m else f"stem={n}"
        print(f"ckb {w} -> {n} | {seg}")
    else:
        n = normalize_kmr(w)
        m = KMR_SPLIT.match(n.lower())
        seg = f"stem={m[1]} suffix={m[2]} {KMR_FEATS[m[2]]}" if m else f"stem={n.lower()}"
        print(f"kmr {w} -> {n} | {seg}")
