<!-- nav:top -->
[← Data ingestion: MDX and ZIM](03-data-ingestion.md) · [⌂ Contents](00-index.md) · [Language identification →](05-language-identification.md)
<!-- nav:top -->

# Unicode and shared normalization

`zimankit/shared_utils/normalizer.py` performs the steps that are safe for **any** text; they never change which letter is written, only the invisible machinery around letters.

| step | what | why |
|---|---|---|
| NFC | compose `e + U+0302` → `ê`, `s + U+0327` → `ş` | Kurmanji keyboards often emit combining marks |
| presentation forms | U+FB50–FDFF, U+FE70–FEFF → base letters (NFKC on those ranges only) | text copied from PDFs |
| bidi controls | drop LRM, RLM, LRE…PDF, isolates, ALM, BOM | invisible, break string equality |
| micro-spaces → ZWNJ | ZWSP U+200B, thin U+2009, hair U+200A, narrow NBSP U+202F, soft hyphen U+00AD, word joiner U+2060 | people use them to stop letters joining; ZWNJ is the standard |
| ZWNJ cleanup | ZWJ → ZWNJ, runs collapsed, removed after non-joining letters (ا د ر ڕ ز ژ و ۆ ە ئ) and at word edges | a ZWNJ is meaningful only between two joining letters |
| spaces | NBSP and wide spaces → space, collapse | |
| optional | digits (`latin` / `arabic-indic`), URLs, e-mails, mentions, emoji | |

## Code points that matter

| letter | code point | common wrong input |
|---|---|---|
| ک keheh | U+06A9 | ك U+0643 Arabic kaf |
| ی farsi yeh | U+06CC | ي U+064A, ى U+0649 |
| ه heh | U+0647 | ھ U+06BE (doachashmee), ہ U+06C1 |
| ە ae | U+06D5 | ه + ZWNJ (legacy), ة U+0629 |
| ڕ trilled r | U+0695 | ر + small-v mark, ڒ U+0692 |
| ڵ velar l | U+06B5 | ل + small-v mark, ڶ/ڷ |
| ێ long e | U+06CE | ې U+06D0, ی + small-v |
| ۆ long o | U+06C6 | ۇ U+06C7, ۅ U+06C5, و + small-v |
| ڤ veh | U+06A4 | ڨ U+06A8 |

The full tables are `CKB_CHAR_MAP`, `CKB_SEQUENCE_MAP` and `KMR_CHAR_MAP` in `unicode_tables.py`, and are exported in `grammar_rules_<lang>.json`.

```python
from zimankit.shared_utils.normalizer import normalize_text, NormalizeOptions
normalize_text("a‏b  c")                          # 'ab c'
normalize_text("ساڵی ۲۰۱۵", NormalizeOptions(digits="latin"))     # 'ساڵی 2015'
```

```bash
# find every Arabic kaf / yeh in a file
grep -nP '[\x{0643}\x{064A}\x{0649}]' corpus.txt | head
# find bidi control characters
grep -nP '[\x{200E}\x{200F}\x{202A}-\x{202E}\x{2066}-\x{2069}]' corpus.txt
```

<!-- nav:bottom -->
---
[← Data ingestion: MDX and ZIM](03-data-ingestion.md) · [⌂ Contents](00-index.md) · [Language identification →](05-language-identification.md)
<!-- nav:bottom -->
