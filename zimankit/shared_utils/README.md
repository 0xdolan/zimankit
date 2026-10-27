# shared_utils — script-independent building blocks

* `unicode_tables.py` — alphabets, code points, confusable maps ([docs/04](../../docs/04-unicode-normalization.md))
* `normalizer.py` — NFC, presentation forms, bidi, micro-spaces → ZWNJ, spaces, digits
* `tokenizer.py` — words/numbers/punctuation with offsets ([docs/06](../../docs/06-tokenization.md))
* `lid.py` — rule-based language identification ([docs/05](../../docs/05-language-identification.md))
* `phonology_core.py` — sonority, legal onsets/codas, epenthesis, syllabification
* `text_helpers.py` — regex cookbook `PATTERNS`, script detection, Levenshtein variants ([docs/17](../../docs/17-regex-cookbook.md))
* `schema.py` — `Analysis`, lexicon protocol, `SimpleLexicon`
