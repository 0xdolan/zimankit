---
name: ckb-morphology
description: Segment and lemmatize Central Kurdish (Sorani) words: definiteness (-ەکە, -کە, -ەکان), indefinite -ێک, plural -ان, pronominal enclitics (م ت ی مان تان یان), additive -یش, postpositions -دا/-ەوە, comparatives, derivation and attached prepositions لە/بە/بۆ. Use for stemming, lemmatization or morphological glossing of Sorani.
---

# ckb-morphology

Segment and lemmatize Central Kurdish (Sorani) words: definiteness (-ەکە, -کە, -ەکان), indefinite -ێک, plural -ان, pronominal enclitics (م ت ی مان تان یان), additive -یش, postpositions -دا/-ەوە, comparatives, derivation and attached prepositions لە/بە/بۆ. Use for stemming, lemmatization or morphological glossing of Sorani.

Full explanation: [docs/09-ckb-morphology.md](../../docs/09-ckb-morphology.md)

## Commands

```bash
python -m zimankit analyze کتێبەکەم لەماڵەکانمانیشدا --top 2
python -m zimankit analyze --json پیاوەکە
```

## Python

```python
from zimankit.skills_ckb.morphology import CkbAnalyzer
```

## Rules to apply

1. Template: [PREP] STEM [DERIV] [CMP] [NUM/DEF] [ENCLITIC] [ADD] [POSTP].
2. Allomorph choice depends on whether the stem ends in a vowel *sound*: پیاو ends in /w/ → پیاوەکە; دەرگا ends in a vowel → دەرگاکە.
3. Generate all segmentations, rank by lexicon membership, corpus frequency and affix reliability; do not trust the first regex match.
4. Final ی is ambiguous (ezafe vs 3sg enclitic) — keep both readings.
5. Pass a SimpleLexicon built from output/ckb/lemmas_ckb.csv for production accuracy.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
