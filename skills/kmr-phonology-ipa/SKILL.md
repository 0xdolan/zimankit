---
name: kmr-phonology-ipa
description: Convert Northern Kurdish (Kurmanji) words to IPA (broad or narrow with aspiration and ŋ), syllabify, and transliterate to Kurdish Arabic script. Use for Kurmanji pronunciation and script-conversion tasks.
---

# kmr-phonology-ipa

Convert Northern Kurdish (Kurmanji) words to IPA (broad or narrow with aspiration and ŋ), syllabify, and transliterate to Kurdish Arabic script. Use for Kurmanji pronunciation and script-conversion tasks.

Full explanation: [docs/12-kmr-phonology-ipa.md](../../docs/12-kmr-phonology-ipa.md)

## Commands

```bash
python -m zimankit ipa jinekê dîtin      # ʒɪnɛkeː diːtɯn
python -m zimankit ipa --narrow "p'ir bang"
python -m zimankit translit --lang kmr "zimanê kurdî"
```

## Python

```python
from zimankit.skills_kmr.phonology_ipa import to_ipa, KmrG2POptions
from zimankit.skills_kmr.translit import to_arabic
```

## Rules to apply

1. a ê î o û = aː eː iː oː uː; e i u = ɛ ɪ ʊ.
2. Final closed-syllable i in polysyllables → reduced ɯ (dîtin diːtɯn).
3. Initial r and rr = trill r; other r = tap ɾ; xw = xʷ; ḧ ẍ ' = ħ ɣ ʕ.
4. Narrow mode: p t k ç aspirated unless followed by an apostrophe; n → ŋ before velars.
5. To Arabic script: short i unwritten except initially (ئ), every initial vowel gets ئ, rr/initial r → ڕ, v → ڤ.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
