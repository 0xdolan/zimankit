<!-- nav:top -->
[⌂ Contents](00-index.md) · [Getting started →](02-getting-started.md)
<!-- nav:top -->

# Overview and architecture

**On this page:** [Design principles](#design-principles) · [Component map](#component-map) · [Data flow](#data-flow)

zimankit turns raw Kurdish data (compiled dictionaries, offline wiki dumps, plain-text corpora) into **clean, validated wordlists** and a set of **reusable linguistic skills** for the two largest Kurdish varieties:

| code | variety | script | key grammatical traits |
|---|---|---|---|
| `ckb` | Central Kurdish (Sorani) | Arabic-based, 34 letters | no grammatical gender, suffixed definiteness (`-eke`), pronominal enclitics, unwritten short vowel (*bizroke*) |
| `kmr` | Northern Kurdish (Kurmanji) | Hawar Latin, 31 letters | masculine/feminine gender, direct/oblique case, ezafe, split ergativity |

## Design principles

1. **One source of truth per rule.** Alphabets, character maps, suffix inventories and verb paradigms are tables in code. Documentation, `grammar_rules_<lang>.json`, the regex cookbook and the cross-language examples are derived from them.
2. **One phoneme layer per dialect.** IPA, transliteration and syllabification all render the same segment list, so they can never disagree.
3. **Generate, then rank.** Morphological analysis produces every legal segmentation and scores it with lexicon evidence, corpus frequency and affix reliability — never a single greedy regex.
4. **Filter by language, not by script.** Arabic-script corpora contain Gurani/Hawrami, Persian and Arabic; Latin-script corpora contain Zazaki, Turkish and English. Language ID runs on every text block before counting.
5. **Sources stay private.** Raw-data locations live in a git-ignored config file; outputs carry only generic tags (`lexicon`, `dictionary`, `bilingual`, `encyclopedia`, `news`, `web`, `corpus`, `core`).
6. **Everything explains itself.** Every rejected candidate is written to `rejected_<lang>.csv` with its reason, every accepted one carries `morph_meta`.

## Component map

```
zimankit/
├── run_pipeline.py              orchestration: lexicon → dictionaries → corpus → build → rules
├── config/
│   ├── pipeline.toml            thresholds (committed)
│   ├── sources.example.toml     source format (committed)
│   └── sources.local.toml       real paths (git-ignored)
├── zimankit/
│   ├── cli.py                   `python -m zimankit <command>`
│   ├── dependency.py            sentence structure: head and relation of each word
│   ├── rules.py                 grammar_rules_<lang>.json exporter
│   ├── tools/                   mdx_extractor.py, zim_cleaner.py
│   ├── shared_utils/            unicode_tables, normalizer, tokenizer, lid, phonology_core, text_helpers, schema
│   ├── skills_ckb/              orthography, phonology_ipa, morphology, verbs, config.toml
│   ├── skills_kmr/              orthography, phonology_ipa, morphology, verbs, syntax, translit, config.toml
│   ├── lexicon/                 wiki_lexicon, corpus, harvest, builder
│   └── data/                    authored reference tables (core verbs, function words)
├── output/{ckb,kmr}/            generated wordlists, lemma tables, rules, reports
├── docs/                        this documentation
├── examples/                    shell, Python, TypeScript, C#, F#, Rust, Go, Java
├── skills/                      agent skill definitions (SKILL.md)
└── tests/                       pytest suite incl. the ground-truth matrix
```

## Data flow

```
 dictionary wiki (ZIM) ─┐                         ┌─> lemmas + gender + stems + declension forms
 monolingual dict (MDX) ─┼─ stage 1-2 harvest ────┤
 bilingual dicts (MDX) ──┘                         └─> dictionary candidates (+POS hints)
 encyclopedias (ZIM/MDX) ┐
 news / web text ────────┴─ stage 3: blocks → script check → LID → orthography → tokens → counts
                                                   │
                         stage 4 build: gate → lexicon gold → analysis → corpus-only lemma → variants
                                                   │
                     clean_wordlist / lemmas / wordlist.txt / rejected / spelling_variants / report
```

<!-- nav:bottom -->
---
[⌂ Contents](00-index.md) · [Getting started →](02-getting-started.md)
<!-- nav:bottom -->
