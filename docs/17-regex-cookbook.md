<!-- nav:top -->
[← The wordlist pipeline](16-lexicon-pipeline.md) · [⌂ Contents](00-index.md) · [Examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java →](18-multi-language-examples.md)
<!-- nav:top -->

# Regex cookbook

**On this page:** [`ckb_word`](#ckb_word) · [`kmr_word`](#kmr_word) · [`ckb_token`](#ckb_token) · [`kmr_token`](#kmr_token) · [`ckb_arabic_kaf_yeh`](#ckb_arabic_kaf_yeh) · [`ckb_legacy_heh_zwnj`](#ckb_legacy_heh_zwnj) · [`ckb_heh_doachashmee`](#ckb_heh_doachashmee) · [`ckb_initial_plain_r`](#ckb_initial_plain_r) · [`ckb_double_ae`](#ckb_double_ae) · [`ckb_arabic_only_letters`](#ckb_arabic_only_letters) · [`ckb_definite_suffix`](#ckb_definite_suffix) · [`ckb_pronominal_enclitic`](#ckb_pronominal_enclitic) · [`ckb_present_verb`](#ckb_present_verb) · [`ckb_infinitive`](#ckb_infinitive) · [`kmr_turkish_letters`](#kmr_turkish_letters) · [`kmr_wrong_circumflex`](#kmr_wrong_circumflex) · [`kmr_oblique_suffix`](#kmr_oblique_suffix) · [`kmr_ezafe_suffix`](#kmr_ezafe_suffix) · [`kmr_present_verb`](#kmr_present_verb) · [`kmr_infinitive`](#kmr_infinitive) · [`kmr_oblique_pronoun`](#kmr_oblique_pronoun) · [`kmr_direct_pronoun`](#kmr_direct_pronoun) · [Using the patterns](#using-the-patterns)

Generated from `zimankit/shared_utils/text_helpers.py: PATTERNS` by `scripts/gen_regex_doc.py` — do not edit by hand.

All patterns avoid look-behind and engine-specific escapes, so they work unchanged in PCRE2 (`grep -P`), Python `re`, JavaScript (`u` flag), .NET, Java, Go RE2 and Rust `regex`. `\u200C` below stands for the literal ZWNJ character.

## `ckb_word`

a whole Central Kurdish word (standard letters, ZWNJ only between letters)

```
^[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+(?:\u200C[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+)*$
```

| input | match |
|---|---|
| کتێبەکەم | کتێبەکەم |
| كتاب | — |

## `kmr_word`

a whole Hawar-alphabet word (optional apostrophe suffix: HDP'yê)

```
^[abcçdeêfghiîjklmnopqrsştuûvwxyzABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZ]+(?:'[abcçdeêfghiîjklmnopqrsştuûvwxyzABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZ]+)?$
```

| input | match |
|---|---|
| jinekê | jinekê |
| Erdoğan | — |

## `ckb_token`

find Sorani words in running text

```
[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+(?:\u200C[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+)*
```

| input | match |
|---|---|
| ئەمڕۆ کتێبەکەم کڕی | ئەمڕۆ |

## `kmr_token`

find Kurmanji words in running text

```
[abcçdeêfghiîjklmnopqrsştuûvwxyzABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZ]+(?:'[abcçdeêfghiîjklmnopqrsştuûvwxyzABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZ]+)?
```

| input | match |
|---|---|
| Ez li malê me | Ez |

## `ckb_arabic_kaf_yeh`

Arabic kaf / yeh / alef maksura that must become ک / ی

```
[كيى]
```

| input | match |
|---|---|
| كتێب | ك |
| کتێب | — |

## `ckb_legacy_heh_zwnj`

legacy spelling of ە as heh + ZWNJ

```
ه\u200C
```

| input | match |
|---|---|
| به\u200Cڕێوه\u200Cبه\u200Cر | ه\u200C |

## `ckb_heh_doachashmee`

ھ U+06BE used for h

```
ھ
```

| input | match |
|---|---|
| ھەموو | ھ |

## `ckb_initial_plain_r`

word-initial ر that must be ڕ (group 1 = preceding char)

```
(^|[^ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ\u200C])ر
```

| input | match |
|---|---|
| رۆژ باش | ر |
| ڕۆژ باش | — |

## `ckb_double_ae`

illegal doubled ە

```
ەە+
```

| input | match |
|---|---|
| سەەر | ەە |

## `ckb_arabic_only_letters`

letters of Arabic loans not in the Kurdish alphabet

```
[ثذصضطظةءأإؤ]
```

| input | match |
|---|---|
| صەبر | ص |
| سەبر | — |

## `ckb_definite_suffix`

word ends in a definite suffix

```
(?:ەکە|کە|ەکان|کان)$
```

| input | match |
|---|---|
| پیاوەکە | ەکە |
| پیاو | — |

## `ckb_pronominal_enclitic`

word ends in a pronominal enclitic

```
(?:مان|تان|یان|م|ت|ی)$
```

| input | match |
|---|---|
| کتێبەکەم | م |

## `ckb_present_verb`

shape of a present-tense verb (دە/نا + stem + ending)

```
^(?:نا|نە|مە)?(?:دە|ئە)[^\s]+(?:م|یت|ێت|ات|ین|ن)$
```

| input | match |
|---|---|
| دەکەم | دەکەم |
| نادەم | — |
| کتێب | — |

## `ckb_infinitive`

infinitive ending

```
(?:دن|تن|ین|ان|وون|اندن)$
```

| input | match |
|---|---|
| کردن | دن |
| شکاندن | اندن |

## `kmr_turkish_letters`

Turkish letters (foreign or mistyped)

```
[ıİğĞöÖüÜ]
```

| input | match |
|---|---|
| Erdoğan | ğ |
| Kurdistan | — |

## `kmr_wrong_circumflex`

acute/grave/macron typed for the circumflex

```
[éèëēíìïīúùūÉÈËÍÌÏÚÙ]
```

| input | match |
|---|---|
| şéwe | é |
| şêwe | — |

## `kmr_oblique_suffix`

oblique-case endings

```
(?:ekê|ekî|yekê|yekî|ê|î|an|yan)$
```

| input | match |
|---|---|
| jinekê | ekê |
| jin | — |

## `kmr_ezafe_suffix`

ezafe endings

```
(?:a|ê|ên|ya|yê|yên|eke|ine)$
```

| input | match |
|---|---|
| mala | a |
| malên | ên |

## `kmr_present_verb`

present-tense verb shape (di-/na-/ni- + stem + ending)

```
^(?:di|na|ni)[a-zçêîşû]+(?:im|î|e|in)$
```

| input | match |
|---|---|
| dibînim | dibînim |
| nakim | nakim |
| bibînim | — |

## `kmr_infinitive`

infinitive endings

```
(?:in|andin|în|ûn|an|n)$
```

| input | match |
|---|---|
| dîtin | in |
| çûn | ûn |

## `kmr_oblique_pronoun`

oblique personal pronoun (ergative agent)

```
^(?:min|te|wî|wê|me|we|wan|vî|vê|van)$
```

| input | match |
|---|---|
| min | min |
| ez | — |

## `kmr_direct_pronoun`

direct-case personal pronoun

```
^(?:ez|tu|ew|em|hûn|ev)$
```

| input | match |
|---|---|
| ez | ez |
| min | — |

## Using the patterns

```bash
# shell (ugrep/GNU grep -P): count Arabic kaf/yeh per file
grep -cP '[كيى]' *.txt
# Sorani words ending in a definite suffix
grep -oP '[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ]+(?:ەکە|ەکان)' text.txt | sort | uniq -c | sort -rn | head
# Kurmanji oblique pronouns (possible ergative agents)
grep -owE 'min|te|wî|wê|me|we|wan' text.txt | sort | uniq -c
```

```python
from zimankit.shared_utils.text_helpers import COMPILED
COMPILED["ckb_definite_suffix"].search("پیاوەکە")
```

```typescript
const ckbDefinite = /(?:ەکە|کە|ەکان|کان)$/u;
ckbDefinite.test("پیاوەکە"); // true
```

```csharp
var ckbDefinite = new Regex("(?:ەکە|کە|ەکان|کان)$");
ckbDefinite.IsMatch("پیاوەکە"); // true
```

```rust
let re = regex::Regex::new("(?:ەکە|کە|ەکان|کان)$").unwrap();
assert!(re.is_match("پیاوەکە"));
```

```go
re := regexp.MustCompile(`(?:ەکە|کە|ەکان|کان)$`)
re.MatchString("پیاوەکە") // true
```

<!-- nav:bottom -->
---
[← The wordlist pipeline](16-lexicon-pipeline.md) · [⌂ Contents](00-index.md) · [Examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java →](18-multi-language-examples.md)
<!-- nav:bottom -->
