<!-- nav:top -->
[← Unicode and shared normalization](04-unicode-normalization.md) · [⌂ Contents](00-index.md) · [Tokenization →](06-tokenization.md)
<!-- nav:top -->

# Language identification

Script is not language. The Arabic-script news data used for training contains **Gurani/Hawrami** sections, the Latin-script data contains whole sections of **Zazaki** — both are closely related varieties, counted by many speakers as part of Kurdish, that share most letters with Sorani and Kurmanji but have their own grammar and vocabulary, and both would silently pollute a wordlist.

## Method (`shared_utils/lid.py`)

For each candidate language a profile holds

* **function words** — high-frequency, *discriminating* words (shared words such as Sorani/Hawrami `و`, `بە`, `کە` or Kurmanji/Zazaki `û`, `de`, `bi` were removed on purpose);
* **diagnostic characters** — e.g. `ۋ` (Hawrami), `ı ğ ö` (Turkish), `ł ř` (Sorani in Latin script), `ة أ إ` (Arabic);
* **regex features** — morphology that only one language has:

| lang | feature | example |
|---|---|---|
| hac | genitive `-و` after a consonant; present `مە…ۆنە` | خەڵکوو، مەکەرۆنە |
| ckb | present verbs `دە…ێت / دە…ات` | دەکات، دەڕوات |
| zza | verbal nouns `-ayîş`, infinitives `-ene` | biyayîş, kerdene |
| kmr | present `di-…im/in/e` | dibînim |

Score = (weighted hits) / tokens. The best language must beat the runner-up by a relative margin (15 %), otherwise the result is `und`. In the corpus counter an `und` block is kept only if the target language still scores highest.

## Measured on the full training corpora (blocks of ~2 kB, `cache/corpus_stats.json`)

| source category | blocks | kept | main rejections |
|---|---|---|---|
| Kurmanji news | 160 862 | 97.6 % | tur 2 846, eng 561 (quoted/boilerplate) |
| Latin-script news that is actually Zazaki | 8 032 | **0.8 %** | zza 7 902 |
| Kurmanji encyclopedia | 22 897 | 98.1 % | zza 186, eng 86, ckb 63 |
| Sorani news (section with Hawrami) | 16 502 | 92.8 % | **hac 1 110** |
| other Sorani news | 267 632 | 86.0 % | Latin-script lines (scraped JavaScript) 37 432 |
| Sorani web corpus | 81 515 | 99.8 % | — |
| Sorani encyclopedia | 54 719 | 99.4 % | — |

Mixed-script blocks are first reduced to the lines in the target script, which removes embedded JavaScript and menus from scraped pages.

```python
from zimankit.shared_utils.lid import identify
identify("Ma yew roje şima ra vat ke ziwanê ma zaf rind o").lang            # 'zza'
identify("Ez ji bajarê Amedê me û niha li Stenbolê dixwînim").lang           # 'kmr'
```

```bash
python -m zimankit lid --json < paragraphs.txt
```

Limitations: rule-based LID is reliable from about eight words up. For single words use the orthographic validators plus corpus attestation (that is what the builder does).

<!-- nav:bottom -->
---
[← Unicode and shared normalization](04-unicode-normalization.md) · [⌂ Contents](00-index.md) · [Tokenization →](06-tokenization.md)
<!-- nav:bottom -->
