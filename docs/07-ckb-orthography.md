<!-- nav:top -->
[← Tokenization](06-tokenization.md) · [⌂ Contents](00-index.md) · [Central Kurdish: phonology and IPA (G2P) →](08-ckb-phonology-ipa.md)
<!-- nav:top -->

# Central Kurdish: alphabet and orthography

**On this page:** [Alphabet (34 letters)](#alphabet-34-letters) · [Normalisation (`skills_ckb/orthography.py`)](#normalisation-skills_ckborthographypy) · [Validation](#validation) · [Spelling variants](#spelling-variants)

## Alphabet (34 letters)

`ئ ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن ه ە و وو ۆ ی ێ`

* **Vowel letters:** `ا ە ێ ۆ` always vowels; `و ی` are *semivowels* (w/u, y/î); `وو` is long û.
* **The bizroke** — the short high vowel /ɯ/ (Latin `i`) is **not written** (`من` min, `بردن` birdin). See [phonology](08-ckb-phonology-ipa.md).
* **ئ** is a seat for the glottal onset of every vowel-initial word (`ئاو`, `ئێمە`); word-initially before a consonant it spells the bizroke itself (`ئنجا` inca).
* **ڕ vs ر**: trill vs tap. Word-initially only the trill exists, so standard spelling writes `ڕ` there.
* **ڵ vs ل**: velarised vs clear l; `ڵ` never starts a word.
* **ه vs ە**: consonant /h/ vs vowel /æ/; never interchangeable.

## Normalisation (`skills_ckb/orthography.py`)

1. Shared cleaning ([chapter 4](04-unicode-normalization.md)).
2. Old keyboard sequences: `ی + ٔ → ئ`, `ر + ٚ → ڕ`, `ل + ٚ → ڵ`, `ی + ٚ → ێ`, `و + ٚ → ۆ`.
3. Word-initial `آ أ إ` → `ئا ئە ئی`.
4. Character map: `ك → ک`, `ي ى → ی`, `ھ ہ → ه`, `ة → ە`, `ۀ → ەی`, `ې → ێ` …
5. **Legacy encoding**: `ه + ZWNJ → ە` always; when a chunk has no `ە` at all but many word-final `ه`, those become `ە` as well (`is_legacy_encoded`).
6. Harakat and tatweel removed.
7. Contextual: initial `ر → ڕ`, initial bare vowel → `ئ` + vowel, `ەە → ە`, `ڕڕ → ڕ`, `ڵڵ → ڵ`, `ووو → وو`.
8. Punctuation `, ; ? → ، ؛ ؟`, digits → Arabic-Indic (configurable).

Real input from the news corpus and its normalised form:

```
in : به‌ڕێوه‌به‌رایه‌تی ئاوی سلێمانی له‌ماوه‌ی مانگی ئابی 2015 دا كرد رۆژ
out: بەڕێوەبەرایەتی ئاوی سلێمانی لەماوەی مانگی ئابی ٢٠١٥ دا کرد ڕۆژ
```

## Validation

`validate_word(w)` returns a list of problems: Arabic-only letters (`ث ذ ص ض ط ظ ة ء أ إ ؤ`), non-Kurdish characters (reported by code point), doubled vowels, initial vowel without `ئ`, initial `ر`, medial hamza outside a hiatus, legacy final heh.

## Spelling variants

Unstandardised text confuses `ر/ڕ`, `ل/ڵ`, `ی/ێ`, `و/ۆ`, `و/وو`, `ه/ە`. `spelling_variants(word)` toggles these; the builder maps a rare unknown form to a **much more frequent accepted variant** (ratio ≥ 5) and writes the pair to `spelling_variants_ckb.csv` (e.g. `بەلام → بەڵام`, `گول → گوڵ`) instead of putting the misspelling in the wordlist.

<!-- nav:bottom -->
---
[← Tokenization](06-tokenization.md) · [⌂ Contents](00-index.md) · [Central Kurdish: phonology and IPA (G2P) →](08-ckb-phonology-ipa.md)
<!-- nav:bottom -->
