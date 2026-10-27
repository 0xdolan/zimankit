---
name: ckb-orthography
description: Normalize and validate Central Kurdish (Sorani, Arabic script) text: Arabic kaf/yeh, heh variants, legacy heh+ZWNJ for ە, initial ڕ, ZWNJ/micro-space cleanup, digits and punctuation; detect non-standard spellings (ر/ڕ, ل/ڵ, ی/ێ, و/ۆ). Use for any Sorani text cleaning or spell-normalisation task.
---

# ckb-orthography

Normalize and validate Central Kurdish (Sorani, Arabic script) text: Arabic kaf/yeh, heh variants, legacy heh+ZWNJ for ە, initial ڕ, ZWNJ/micro-space cleanup, digits and punctuation; detect non-standard spellings (ر/ڕ, ل/ڵ, ی/ێ, و/ۆ). Use for any Sorani text cleaning or spell-normalisation task.

Full explanation: [docs/07-ckb-orthography.md](../../docs/07-ckb-orthography.md)

## Commands

```bash
python -m zimankit normalize --lang ckb "به‌ڕێوه‌به‌رایه‌تی ئاوی سلێمانی 2015"
python -m zimankit validate --lang ckb صەبر رۆژ کتێب
```

## Python

```python
from zimankit.skills_ckb.orthography import normalize, validate_word, spelling_variants
```

## Rules to apply

1. Canonical letters: ک U+06A9, ی U+06CC, ه U+0647, ە U+06D5, ڕ U+0695, ڵ U+06B5, ێ U+06CE, ۆ U+06C6.
2. ه+ZWNJ always means ە; bare word-final ه means ە only in legacy-encoded chunks (no ە anywhere).
3. Word-initial ر → ڕ; word-initial vowel letter gets ئ.
4. Keep ZWNJ only between two joining letters; convert ZWSP/thin/hair spaces/soft hyphen to ZWNJ first.
5. Never 'fix' ر/ڕ or ل/ڵ inside a word without a lexicon: use spelling_variants() + frequency ratio.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
