<!-- nav:top -->
[← Language identification](05-language-identification.md) · [⌂ Contents](00-index.md) · [Central Kurdish: alphabet and orthography →](07-ckb-orthography.md)
<!-- nav:top -->

# Tokenization

`shared_utils/tokenizer.py`

* A **ZWNJ is part of a word** — it separates morphemes inside one orthographic word (`پێ‌نەبوون`), so it never splits a token.
* **Apostrophes** between letters are kept (`HDP'yê`); quotes at word edges are punctuation.
* **Hyphens** split by default; `tokenize(text, keep_hyphen=True)` keeps `pêşî-hatin`.
* Numbers in Latin, Arabic-Indic (U+0660…) and Persian (U+06F0…) digits, with `.` `,` `٫` `٬` separators, are single tokens.

```python
from zimankit.shared_utils.tokenizer import tokenize, words, sentences
[t.text for t in tokenize("HDP'yê got: «باشە»، 2015.")]
# ["HDP'yê", 'got', ':', '«', 'باشە', '»', '،', '2015', '.']
```

Word pattern (portable):

```
Arabic-script word : [ؠ-يٮ-ۓەۺ-ۿݐ-ݿ]+(?:‌[same]+)*
Latin word         : [A-Za-zÀ-ɏḀ-ỿ]+(?:'[same]+)*
```

## Proclitic prepositions

Unstandardised Sorani writes `لە`, `بە`, `بۆ` attached (`لەماڵەوە`). The tokenizer does **not** split them (that would break lexicalised words such as `لەگەڵ`, `بەڵام`); the analyzer peels them as a `PREP` segment only when the remainder is a known lemma: `لەماڵەکانمانیشدا → لە+ماڵ+ەکان+مان+یش+دا`.

<!-- nav:bottom -->
---
[← Language identification](05-language-identification.md) · [⌂ Contents](00-index.md) · [Central Kurdish: alphabet and orthography →](07-ckb-orthography.md)
<!-- nav:bottom -->
