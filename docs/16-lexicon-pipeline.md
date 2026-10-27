<!-- nav:top -->
[← Transliteration](15-transliteration.md) · [⌂ Contents](00-index.md) · [Regex cookbook →](17-regex-cookbook.md)
<!-- nav:top -->

# The wordlist pipeline

**On this page:** [Stages](#stages) · [Stage 4: decision procedure for every candidate form](#stage-4-decision-procedure-for-every-candidate-form) · [Output files (`output/<lang>/`)](#output-files-outputlang) · [Results of the current build](#results-of-the-current-build) · [Real rows](#real-rows) · [Kaggle dataset (`output/kaggle/`)](#kaggle-dataset-outputkaggle) · [Tuning](#tuning)

```bash
python run_pipeline.py                         # lexicon → dictionaries → corpus → build → rules → export
python run_pipeline.py --stages build,rules    # reuse cached harvests
python run_pipeline.py --langs kmr --force     # recompute everything for one variety
```

## Stages

| # | stage | input kinds | output (cache/) | time* |
|---|---|---|---|---|
| 1 | lexicon | `wiki_lexicon_zim` | `lexicon_wiki.jsonl` — 445 044 (language, POS) records | ~4 min |
| 2 | dictionaries | `mdx_headwords`, `mdx_equivalents` | `dictionary_candidates.tsv` | ~2 min |
| 3 | corpus | `text`, `zim_articles`, `mdx_articles`, monolingual definitions | `freq_ckb.tsv`, `freq_kmr.tsv`, `corpus_stats.json` | ~6 min |
| 4 | build | all of the above + core tables | `output/<lang>/…` | ~1.5 min / variety |
| 5 | rules | code tables | `output/<lang>/grammar_rules_<lang>.json` | seconds |
| 6 | export | stage 4 outputs + `lexicon_wiki.jsonl` | `output/kaggle/…` | ~2.5 min |

\* 8 workers, ~1.8 GB of text.

## Stage 4: decision procedure for every candidate form

1. **Gate** — deny list (also before an apostrophe suffix), orthographic validator of the variety, single letters.
2. **Lexicon gold** — a lexicon lemma, or a form from a declension table / form-of entry → accepted with the lexicon's lemma and features. Closed-class words take their POS from the reference table; reference-verb readings beat rare noun homographs (`kir` = past of *kirin*).
3. **Analysis** — the analyzer's best reading with a known lemma (lexicon, dictionary, core verb, function word). A POS-less dictionary word that analyses into a known lemma is treated as an inflected form (`وەزارەتی → وەزارەت+ی`), but a one-letter enclitic is believed only if the stem is at least as frequent.
4. **Corpus-only lemma** — ≥ 40 occurrences in ≥ 2 independent source categories; Kurmanji forms capitalised inside sentences ≥ 80 % of the time become `PROPN`.
5. **Variants (ckb)** — an otherwise rejected form whose confusable-letter respelling (ر/ڕ ل/ڵ ی/ێ و/ۆ و/وو ه/ە, ZWNJ, gemination) is ≥ 5× more frequent goes to `spelling_variants_ckb.csv`.
6. Everything else → `rejected_<lang>.csv` with its reason.

## Output files (`output/<lang>/`)

| file | content |
|---|---|
| `clean_wordlist_<lang>.csv` | every accepted surface form |
| `lemmas_<lang>.csv` | lemma, pos, ipa, translit, gender, transitivity, aggregated frequency, number of forms, sources |
| `wordlist_<lang>.txt` | one grapheme per line (spell-checkers, keyboards) |
| `spelling_variants_ckb.csv` | non-standard → standard spelling with frequencies |
| `rejected_<lang>.csv` | top 50 000 rejected candidates with reasons |
| `grammar_rules_<lang>.json` | the rules implemented by the skills |
| `build_report_<lang>.json` | statistics of the build |
| `sample_clean_wordlist_<lang>.csv` | first 300 rows (committed to git) |

### CSV schema

| column | meaning |
|---|---|
| `grapheme` | normalised surface form (Kurmanji lower-case; proper nouns capitalised) |
| `lemma` | citation form (infinitive for verbs) |
| `pos` | UPOS (`X` = unknown) |
| `ipa` | broad IPA from the phonology skill (Sorani inferred vowels in parentheses) |
| `morph_meta` | JSON: `seg` (segmentation) + features (`definite`, `number`, `case`, `gender`, `enclitic`, `tense`, `person`, `agent`, `alignment`, …) |
| `translit` | ckb → Latin, kmr → Arabic script |
| `frequency` | corpus count after normalisation |
| `sources` | generic tags: lexicon, lexicon-form, dictionary, bilingual, encyclopedia, news, web, corpus, core |
| `confidence` | 0–1: lexicon evidence, dictionary evidence, log frequency, number of source categories |

## Results of the current build

| | Central Kurdish (ckb) | Northern Kurdish (kmr) |
|---|---|---|
| corpus tokens after LID | 98.9 M | 43.4 M |
| corpus types | 2.12 M | 0.57 M |
| lexicon / dictionary lemmas | 76 902 | 122 729 |
| lexicon declension forms | — | 387 582 |
| verbs in the paradigm index | 7 041 | 6 317 |
| **accepted forms** | **328 881** | **503 606** |
| **accepted lemmas** | **≈ 101 000** | **≈ 122 600** |
| spelling variants mapped | 24 922 | — |
| IPA vs. reference transcriptions | 0.965 (n = 178) | 0.978 (n = 18 472) |

Largest rejection reasons — ckb: unknown rare stems (342 k), Arabic-only letters (4.9 k); kmr: unknown rare stems (62 k), rare proper nouns (33 k), non-Hawar characters (9.4 k, mostly scraped JavaScript and English).

## Real rows

```
grapheme,lemma,pos,ipa,morph_meta,translit,frequency,sources,confidence
پیاوەکە,پیاو,NOUN,pjaːwækæ,"{""definite"":""def"",""number"":""sg"",""seg"":""پیاو+ەکە""}",pyaweke,1483,"encyclopedia,news,web",0.388
کتێبەکەم,کتێب,NOUN,k(ɯ)teːbækæm,"{""definite"":""def"",""enclitic"":""1sg"",""number"":""sg"",""seg"":""کتێب+ەکە+م""}",kitêbekem,137,"encyclopedia,news,web",0.31
نەمکرد,کردن,VERB,næmk(ɯ)ɾd,"{""agent"":""1sg"",""alignment"":""ergative"",""polarity"":""neg"",""tense"":""past"",...}",nemkird,20,"core,news,web",0.699
jinekê,jin,NOUN,ʒɪnɛkeː,"{""case"":""obl"",""definite"":""ind"",""gender"":""f"",""number"":""sg"",""seg"":""jin+ekê""}",ژنەکێ,530,"encyclopedia,lexicon-form,news",0.754
dîtin,dîtin,VERB,diːtɯn,"{""form"":""infinitive"",""past_stem"":""dît"",""present_stem"":""bîn"",""transitivity"":""transitive""}",دیتن,22729,...,1.0
malê,mal,NOUN,maːleː,"{""case"":""obl"",""gender"":""f"",""seg"":""mal+ê""}",مالێ,6064,...
bavê,bav,NOUN,baːveː,"{""ezafe"":""yes"",""gender"":""m"",""seg"":""bav+ê""}",باڤێ,8682,...
```

Spelling variants learnt from the data: `وێستگه → وێستگە` (legacy final heh), `ڕای‌گەیاند → ڕایگەیاند` (stray ZWNJ), `بالادەستی → باڵادەستی` (ل/ڵ), `گولله → گوللە`.

## Kaggle dataset (`output/kaggle/`)

```bash
uv pip install --python .venv/bin/python pyarrow   # optional: Parquet files
python run_pipeline.py --stages export             # reuses the build outputs, ~2.5 min
```

Stage 6 flattens the build into a self-contained dataset with a data card (`README.md`) and Kaggle API metadata (`dataset-metadata.json`):

| file | content |
|---|---|
| `kurdish_words_<lang>.csv` / `.parquet` | one row per form, 59 columns: every `morph_meta` feature as its own column (`gender`, `case`, `definiteness`, `ezafe`, `tense`, `person`, `enclitic`, `agent`, …), `segmentation`, `morpheme_count`, `script_arabic` + `script_latin`, `ipa`, `syllables`, the lemma's cleaned definition, `attested`, `freq_per_million`, `zipf`, `quality_tier` |
| `kurdish_lemmas_<lang>.csv` / `.parquet` | one row per lemma with definitions, verb stems, `forms_sample` |
| `kurdish_spelling_variants_ckb.csv` | non-standard → standard spelling |
| `kurdish_lexicon.sqlite` | `words`, `lemmas`, `spelling_variants` tables for both varieties, indexed on word / lemma / upos |

Definitions are cleaned in `clean_definition()`: placeholders dropped, "variant of X" / "see X" moved to `variant_of` / `see_also`, quoted citations, years, URLs, glued example sentences and deny-listed tokens cut off. `quality_tier`: `gold` = curated lexicon/dictionary, `silver` = analysed onto a known lemma, `bronze` = corpus evidence only. About 80 % of Kurmanji rows are paradigm forms from declension tables with `attested = false`; filter on it for a corpus-attested list.

Publish with the Kaggle CLI (the dataset id comes from `[kaggle] dataset_id` in `config/pipeline.toml`): `kaggle datasets create -p output/kaggle`.

## Tuning

All thresholds are in `config/pipeline.toml` (`min_count`, `min_count_new_lemma`, `min_source_tags_new_lemma`, `variant_ratio`, `propn_ratio`). After changing a rule, rerun `--stages build` and compare `build_report_<lang>.json` and the top of `rejected_<lang>.csv`.

<!-- nav:bottom -->
---
[← Transliteration](15-transliteration.md) · [⌂ Contents](00-index.md) · [Regex cookbook →](17-regex-cookbook.md)
<!-- nav:bottom -->
