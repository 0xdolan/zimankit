---
name: ckb-phonology-ipa
description: Convert Central Kurdish (Sorani) Arabic-script words to IPA, syllables and Kurdish-Latin, re-inserting the unwritten bizroke vowel and resolving و/ی as w/u/uː and y/iː. Use for pronunciation, transliteration or phonotactic questions about Sorani.
---

# ckb-phonology-ipa

Convert Central Kurdish (Sorani) Arabic-script words to IPA, syllables and Kurdish-Latin, re-inserting the unwritten bizroke vowel and resolving و/ی as w/u/uː and y/iː. Use for pronunciation, transliteration or phonotactic questions about Sorani.

Full explanation: [docs/08-ckb-phonology-ipa.md](../../docs/08-ckb-phonology-ipa.md)

## Commands

```bash
python -m zimankit ipa پیاوەکە کتێبەکەم    # pjaːwækæ  k(ɯ)teːbækæm
python -m zimankit ipa --syllables کوردستان   # kuɾ.d(ɯ)s.taːn
python -m zimankit translit کوردستان         # kurdistan
```

## Python

```python
from zimankit.skills_ckb.phonology_ipa import to_ipa, to_latin, syllables, G2POptions
```

## Rules to apply

1. و/ی: after or before a vowel letter = glide w/j; between consonants or final = u/iː; وو = uː, یی = iː.
2. Bizroke /ɯ/ is inserted wherever a cluster breaks the rules: initial onsets C, Cw/Cj, s+stop; medial codas fricative+stop, nasal+stop; final codas falling sonority. Carve CɯC from the right.
3. Initial ئ + consonant spells the bizroke itself (ئنجا ʔɯn.dʒaː).
4. ە = æ, ا = aː, ێ = eː, ۆ = oː, ڵ = ɫ, ڕ = r, ر = ɾ (r word-initially).
5. Inferred vowels are shown as (ɯ); pass G2POptions(mark_epenthesis=False) to hide the marks.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
