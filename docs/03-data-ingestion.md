<!-- nav:top -->
[← Getting started](02-getting-started.md) · [⌂ Contents](00-index.md) · [Unicode and shared normalization →](04-unicode-normalization.md)
<!-- nav:top -->

# Data ingestion: MDX and ZIM

**On this page:** [MDX (compiled dictionaries)](#mdx-compiled-dictionaries) · [ZIM (offline wiki dumps)](#zim-offline-wiki-dumps) · [Dictionary-wiki pages](#dictionary-wiki-pages) · [Real example from the data](#real-example-from-the-data)

## MDX (compiled dictionaries)

`zimankit/tools/mdx_extractor.py` reads `.mdx` files **in-process** with `mdict_utils.base.readmdict.MDX` — no subprocess, no unpacking to disk.

```python
from zimankit.tools.mdx_extractor import iter_entries, entry_text, detect_pos, split_equivalents

for e in iter_entries("dict.mdx"):                 # @@@LINK= redirects skipped
    text = entry_text(e.html, selectors=("def",), drop_classes=("entry", "abbr"))
    pos = detect_pos(text, e.html)                 # {"VERB"} for "(مص‌م)", {"NOUN"} for "[n.]"
    equivalents = split_equivalents(text)          # "x، y، z" -> ["x", "y", "z"]
```

* **Selectors / drop classes** — dictionaries wrap the definition in an element with a class (`def`, `item`, `meaning`). The extractor keeps those and removes headword echoes, source-language labels and abbreviation tables. They are configured per source, not hard-coded.
* **POS markers** — `POS_MARKERS` maps English (`n`, `v`, `adj`), Central Kurdish (`ناو`, `کار`, `ئاوەڵناو`), Northern Kurdish (`nd`, `lk`, `rd`) and Persian-style (`ا`, `ص`, `ق`, `مص‌ل`, `مص‌م`, `حامص`) abbreviations to Universal POS tags. ZWNJ and dots inside markers are ignored, so `مص‌ل`, `مصل` and `مص.ل` are the same marker.
* **Equivalent splitting** — separators `، , ; ؛ / |`, dashes and newlines; numbering (`1.`, `١-`, `a)`), parenthetical notes and "sense label:" prefixes are removed; pieces longer than three words go to the expression list instead of the wordlist.

### Source roles

| kind | headword | definition |
|---|---|---|
| `mdx_headwords` | Kurdish lemma (trusted) | Kurdish prose → counted as corpus text |
| `mdx_equivalents` | foreign word (ignored) | Kurdish equivalents → candidates; must be attested in the corpus |
| `mdx_articles` | article title | encyclopedic prose → corpus text |

## ZIM (offline wiki dumps)

`zimankit/tools/zim_cleaner.py` iterates HTML items by entry id, which makes it trivially parallel (`zim_ranges(path, parts)`).

* `article_paragraphs(html)` keeps only `<p>` prose of the content region; infoboxes, navboxes, tables, references, `<sup>` markers, math, scripts and styles are removed. This is the cleanest possible text for frequency counts.
* `strip_html(fragment)` is the generic sanitiser used everywhere (comments, scripts, styles, entities, leaked CSS).
* `to_token_xml(...)` serialises analysed sentences as `<doc><s><w lemma="" pos="">…</w></s></doc>` for downstream tools.

## Dictionary-wiki pages

`zimankit/lexicon/wiki_lexicon.py` parses MediaWiki dictionary pages written in Kurdish. Language sections are identified by the language code on the section heading (`ku` → kmr, `ckb` → ckb), parts of speech by the Kurdish heading names:

| heading | UPOS | heading | UPOS |
|---|---|---|---|
| Navdêr | NOUN | Serenav | PROPN |
| Rengdêr | ADJ | Lêker | VERB |
| Hoker | ADV | Cînav | PRON |
| Daçek | ADP | Girêdek | CCONJ |
| Hejmar | NUM | Baneşan | INTJ |
| Formeke navdêrê | inflected noun → lemma | Formeke lêkerê | inflected verb → lemma |

Gender is read from the `<abbr title>` (`mê` = **feminine**, `nêr` = masculine — the bare abbreviation `m` means *mê*, i.e. feminine, a common trap). Transitivity comes from `gerguhêz` / `negerguhêz`, the present stem from "Rehê dema niha", and every cell of a declension table becomes a `(form, lemma, features)` triple such as `jinekê → jin {case: obl, gender: f, number: sg, definite: ind}`.

## Real example from the data

```
page "jin" (Kurmancî / Navdêr):
  headword jin, gender f, 16 declension cells:
  jin (dir) · jina (ezafe) · jinên (ezafe pl) · jinê (obl) · jinan (obl pl) · jinino (voc pl)
  jinek · jineke · jinekê · jinin · jinine · jininan
```

<!-- nav:bottom -->
---
[← Getting started](02-getting-started.md) · [⌂ Contents](00-index.md) · [Unicode and shared normalization →](04-unicode-normalization.md)
<!-- nav:bottom -->
