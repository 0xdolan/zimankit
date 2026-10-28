# Engineering brief: Kurdish (ckb / kmr) NLP skills and wordlist pipeline

*This is the refined version of the original request, with the gaps filled in. It is the specification zimankit is built against.*

## 1. Role and objective

Act as a senior computational linguist and NLP engineer specialising in Kurdish. Build a standalone, production-quality, modular project that

1. **extracts** raw lexical and textual data from compiled dictionaries (`.mdx`, read in-process with `mdict-utils`), offline wiki dumps (`.zim`, read with `libzim`) and plain-text corpora;
2. **implements reusable linguistic skills** — orthography, phonology/IPA, morphology, verbs, syntax (alignment), language identification, transliteration — separately for
   * **Central Kurdish (Sorani, `ckb`)** — Arabic-based script;
   * **Northern Kurdish (Kurmanji, `kmr`)** — Hawar Latin script;
3. **generates** (not copies) one clean, validated wordlist per variety from that data, using those skills;
4. **documents** every rule with real examples from the data, in an organised, cross-linked documentation set, with examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java.

## 2. Hard constraints

* **Source privacy.** The raw data is training material only. No company names, product names, site names or file names of the sources may appear in code, documentation, skills or outputs. Source locations live in a git-ignored local config; outputs carry only generic tags (`lexicon`, `dictionary`, `bilingual`, `encyclopedia`, `news`, `web`, `corpus`, `core`).
* **Generated, not copied.** Pre-existing wordlists in the workspace are not used as input. Wordlists are produced by the pipeline from dictionaries, dumps and running text.
* **No placeholders.** No `pass`, dummy logic or unfinished regexes. Everything runs.
* **Separate project.** Its own folder, environment, config, tests and docs; the raw-data folders stay untouched and are git-ignored.
* **Language filtering.** Script is not language: Arabic-script data can contain Gurani/Hawrami, Persian and Arabic; Latin-script data can contain Zazaki, Turkish and English. Filter by language before counting.

## 3. Required components

| area | ckb | kmr | shared |
|---|---|---|---|
| orthography | kaf/yeh/heh unification, legacy heh+ZWNJ, ڕ/ڵ/ێ/ۆ sequences, initial ڕ and ئ, ZWNJ policy, validation, spelling variants | look-alike folding (é ü ı İ ș), Kurdish-safe casing, apostrophes, digraphs, validation | NFC, presentation forms, bidi, micro-spaces → ZWNJ, digits |
| phonology | G2P with و/ی resolution, bizroke (unwritten vowel) epenthesis, syllabification, Latin transliteration | Latin → IPA (length, rhotics, xw, ḧ ẍ ʕ), narrow aspiration, Arabic-script transliteration | sonority, legal onsets/codas, epenthesis engine |
| morphology | definiteness, plural, indefinite, enclitic pronouns, additive, postpositions, comparison, derivation, attached prepositions | gender, number, definiteness, case (direct/oblique/vocative), ezafe, derivation; -ê disambiguation by gender | generate-and-rank analysis with lexicon + frequency evidence |
| verbs | stems, full paradigms, ergative agent clitics, preverbs, -ەوە, passive, light verbs | stems, full paradigms, preverbs, irregulars | inverted paradigm index for recognition |
| syntax | ergative past documented | split-ergativity detector with agreement check | |
| LID | ckb vs hac/fas/arb | kmr vs zza/tur/eng | rule-based, explainable |

## 4. Pipeline and outputs

Stages: lexicon harvest → dictionary harvest → LID-filtered corpus counts → build → grammar-rule export, all cached and restartable, parallel where possible.

Per variety (`output/<lang>/`): `clean_wordlist_<lang>.csv` with **`grapheme, lemma, pos, ipa, morph_meta`** (+ `translit, frequency, sources, confidence`), `lemmas_<lang>.csv`, `wordlist_<lang>.txt`, `rejected_<lang>.csv` (with reasons), `spelling_variants_ckb.csv`, `grammar_rules_<lang>.json`, `build_report_<lang>.json`.

## 5. Verification matrix (must pass)

| variety | input | lemma | features | IPA |
|---|---|---|---|---|
| ckb | پیاوەکە | پیاو | definite (`-eke`) | /pjaːwækæ/ |
| ckb | کتێبەکەم | کتێب | definite + 1sg enclitic `-m` | /k(ɯ)teːbækæm/ |
| kmr | jinekê | jin | feminine sg oblique (`-ê`), indefinite | /ʒɪnɛkeː/ |
| kmr | dîtin | dîtin | infinitive; past transitive stem `dît` | /diːtɯn/ |

Plus: unit tests per skill, a data-level build report (including agreement of generated IPA with reference transcriptions found in the data), and cross-language examples verified against one expected output.

## 6. Documentation

Numbered chapters with a table of contents, per-page section links and previous/next navigation, linked from the README: architecture, setup, data ingestion, Unicode, LID, tokenization, each variety's orthography/phonology/morphology/verbs, transliteration, pipeline, generated regex cookbook, multi-language examples, testing, glossary, references. Agent skill definitions (`skills/*/SKILL.md`) for each capability. Short README files next to the code packages.

## 7. Gaps filled beyond the original request

* language identification (Zazaki and Hawrami were found inside the "Kurdish" corpora);
* spelling-variant mapping instead of silently keeping misspellings;
* proper-noun detection from in-sentence capitalisation;
* lexicon gender and transitivity harvesting; gender inference from suffixes;
* ergative agent clitics, preverbs, light verbs and directional -ە in the Sorani verb model;
* a regex cookbook generated from the code so documentation cannot drift;
* grammar rules exported as JSON from the same tables the code uses;
* rejection logs and build reports for auditing.
