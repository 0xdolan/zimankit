---
name: kmr-orthography
description: Normalize and validate Northern Kurdish (Kurmanji, Hawar Latin) text: fold é/ü/ı/İ/ș look-alikes to ê/û/i/I/ş, Kurdish-safe casing, apostrophe handling, digraphs xw/rr, foreign-letter detection. Use for any Kurmanji text cleaning or spelling validation.
---

# kmr-orthography

Normalize and validate Northern Kurdish (Kurmanji, Hawar Latin) text: fold é/ü/ı/İ/ș look-alikes to ê/û/i/I/ş, Kurdish-safe casing, apostrophe handling, digraphs xw/rr, foreign-letter detection. Use for any Kurmanji text cleaning or spelling validation.

Full explanation: [docs/11-kmr-orthography.md](../../docs/11-kmr-orthography.md)

## Commands

```bash
python -m zimankit normalize --lang kmr "Kürdistan şéwe"
python -m zimankit validate --lang kmr jinekê Erdoğan
```

## Python

```python
from zimankit.skills_kmr.orthography import normalize, lower, validate_word
```

## Rules to apply

1. Hawar: 31 letters; long a ê î o û, short e i u.
2. Map acute/grave/diaeresis/macron vowels to the circumflex; Turkish ı→i, İ→I.
3. Lowercase with skills_kmr.orthography.lower(), never a Turkish locale.
4. Keep an apostrophe inside a word (HDP'yê) and word-initially before a vowel ('erd = /ʕ/).
5. Words with ö ä ğ ß ñ … are foreign; frequent capitalised ones are proper nouns.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
