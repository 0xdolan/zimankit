<!-- nav:top -->
[← Central Kurdish: verbs](10-ckb-verbs.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: phonology and IPA →](12-kmr-phonology-ipa.md)
<!-- nav:top -->

# Northern Kurdish: alphabet and orthography

**On this page:** [Hawar alphabet (31 letters)](#hawar-alphabet-31-letters) · [Normalisation (`skills_kmr/orthography.py`)](#normalisation-skills_kmrorthographypy) · [Validation rules](#validation-rules) · [Proper nouns](#proper-nouns)

## Hawar alphabet (31 letters)

`a b c ç d e ê f g h i î j k l m n o p q r s ş t u û v w x y z`

* long vowels `a ê î o û`, short vowels `e i u`;
* `c` = /dʒ/, `ç` = /tʃ/, `j` = /ʒ/, `ş` = /ʃ/, `x` = /x/, `q` = /q/, `y` = /j/;
* extended letters some writers add for Arabic sounds: `ḧ` /ħ/, `ẍ` /ɣ/, apostrophe /ʕ/ (`'erd`, `'Ezîz`);
* conventional **digraphs** recognised by the phonology: `xw` /xʷ/ (`xwe`, `xwarin`), `rr` trill (`kurr`), `ll` (velarised l in some writers).

## Normalisation (`skills_kmr/orthography.py`)

| problem | fix |
|---|---|
| Turkish `ı`, `İ` | `i`, `I` |
| acute / grave / diaeresis / macron vowels typed for the circumflex (`é è ë ē`, `í ì ï ī`, `ú ù ü ū`) | `ê`, `î`, `û` |
| Romanian `ș`, Czech `š č` | `ş`, `ç` |
| `e + U+0302`, `s + U+0327` (combining marks) | NFC → `ê`, `ş` |
| apostrophe variants `’ ‘ ʼ ´ ` ʻ` | `'`; kept only inside a word or word-initially before a vowel |
| casing | Kurdish-aware `lower()` / `upper()`: `I↔i`, `Î↔î` — never Python's Turkish-unsafe behaviour for `İ` |

```python
from zimankit.skills_kmr.orthography import normalize, lower, validate_word
normalize("Kürdistan")      # 'Kûrdistan'
normalize("şéwe")           # 'şêwe'
lower("İro")                # 'iro'
validate_word("Erdoğan")    # ['foreign letter(s): ğ']
```

## Validation rules

Foreign letters (`ö ä ß ğ ñ å ø æ â ô …`), non-Hawar characters, tripled letters, three vowels in a row, four consonants in a row, vowel-less words longer than two letters, doubled long vowels. Turkish personal and place names are therefore excluded from the common wordlist automatically; frequent capitalised forms become `PROPN` entries.

## Proper nouns

The corpus counter records how often a form is **capitalised inside a sentence** (not after `. ! ? : « "`). A form not in the lexicon whose capitalised ratio is ≥ 0.8 and that is frequent enough is kept as `PROPN` with its capitalised spelling.

<!-- nav:bottom -->
---
[← Central Kurdish: verbs](10-ckb-verbs.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: phonology and IPA →](12-kmr-phonology-ipa.md)
<!-- nav:bottom -->
