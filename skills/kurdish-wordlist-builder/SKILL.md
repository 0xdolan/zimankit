---
name: kurdish-wordlist-builder
description: Build clean ckb and kmr wordlists (grapheme, lemma, pos, ipa, morph_meta, translit, frequency, sources, confidence) from MDX dictionaries, ZIM wiki dumps and text corpora, with LID filtering, orthographic gates, lexicon-backed analysis and spelling-variant mapping. Use when (re)generating or auditing the wordlists.
---

# kurdish-wordlist-builder

Build clean ckb and kmr wordlists (grapheme, lemma, pos, ipa, morph_meta, translit, frequency, sources, confidence) from MDX dictionaries, ZIM wiki dumps and text corpora, with LID filtering, orthographic gates, lexicon-backed analysis and spelling-variant mapping. Use when (re)generating or auditing the wordlists.

Full explanation: [docs/16-lexicon-pipeline.md](../../docs/16-lexicon-pipeline.md)

## Commands

```bash
cp config/sources.example.toml config/sources.local.toml   # edit paths
python run_pipeline.py
python run_pipeline.py --stages build --langs kmr
```

## Python

```python
from zimankit.config import load_config
from zimankit.lexicon.builder import build
```

## Rules to apply

1. Never write source names or file paths into outputs; use generic tags.
2. Accept a form only if it is a lexicon lemma/form, analyses to a known lemma, or is a frequent multi-source corpus lemma.
3. Every rejection has a reason in rejected_<lang>.csv — audit it after changing thresholds.
4. Sorani misspellings go to spelling_variants_ckb.csv, not the wordlist.
5. Check build_report_<lang>.json (IPA similarity, POS/source distribution) after every rule change.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
