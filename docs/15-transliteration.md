<!-- nav:top -->
[← Northern Kurdish: verbs and split ergativity](14-kmr-verbs-ergativity.md) · [⌂ Contents](00-index.md) · [The wordlist pipeline →](16-lexicon-pipeline.md)
<!-- nav:top -->

# Transliteration

## Central Kurdish → Latin (`skills_ckb/phonology_ipa.to_latin`)

Rendered from the same segments as the IPA, so the bizroke appears as `i`:

| Arabic script | Latin | Arabic script | Latin |
|---|---|---|---|
| ا ە ێ ۆ | a e ê o | وو / و (vowel) | û / u |
| ی (vowel) | î | و / ی (glide) | w / y |
| ج چ ژ ش خ | c ç j ş x | ح ع غ | ḧ ' ẍ |
| ڕ ڵ | rr ll (`style="accented"`: ř ł) | initial ئ | ∅ |
| bizroke | i | medial ئ | ' |

`کوردستان → kurdistan`, `هەڵبژاردن → hellbijardin`, `هاتووە → hatûwe`, `ماسییەکە → masîyeke`, `ڕۆژ → roj`.

## Northern Kurdish → Arabic script (`skills_kmr/translit.to_arabic`)

Long vowels to letters (`a ا`, `ê ێ`, `î ی`, `o ۆ`, `û وو`), `e → ە`, `u → و`, short `i` unwritten (bizroke) except word-initially (`ئ`); every word-initial vowel gets `ئ`; `rr`/initial `r → ڕ`, `ll → ڵ`, `v → ڤ`.

`jin → ژن`, `dîtin → دیتن`, `roj → ڕۆژ`, `mirov → مرۆڤ`, `zimanê kurdî → زمانێ کوردی`, `inca → ئنجا`.

```bash
python -m zimankit translit "ڕێبەری زمانی کوردی"
python -m zimankit translit --lang kmr "Ez ji Amedê me"
```

<!-- nav:bottom -->
---
[← Northern Kurdish: verbs and split ergativity](14-kmr-verbs-ergativity.md) · [⌂ Contents](00-index.md) · [The wordlist pipeline →](16-lexicon-pipeline.md)
<!-- nav:bottom -->
