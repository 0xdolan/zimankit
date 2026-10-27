---
name: kurdish-language-id
description: Identify whether text is Central Kurdish, Northern Kurdish, Gurani/Hawrami, Zazaki, Persian, Arabic, Turkish or English using function words, diagnostic letters and morphological regex features. Use before counting or training on mixed Kurdish corpora.
---

# kurdish-language-id

Identify whether text is Central Kurdish, Northern Kurdish, Gurani/Hawrami, Zazaki, Persian, Arabic, Turkish or English using function words, diagnostic letters and morphological regex features. Use before counting or training on mixed Kurdish corpora.

Full explanation: [docs/05-language-identification.md](../../docs/05-language-identification.md)

## Commands

```bash
python -m zimankit lid "Ma yew roje şima ra vat ke ziwanê ma zaf rind o"   # zza
python -m zimankit lid --json < paragraphs.txt
```

## Python

```python
from zimankit.shared_utils.lid import identify
```

## Rules to apply

1. Script is not language: Arabic-script Kurdish corpora hide Hawrami/Persian, Latin ones hide Zazaki/Turkish.
2. Use paragraph-sized input (≥ 8 words); for single words rely on orthography validation + corpus attestation.
3. Normalise Sorani legacy encodings before LID (ە is a key feature).
4. Drop lines in the wrong script (scraped JavaScript) before deciding a block.
5. Treat 'und' as accept only if the target language still scores highest.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
