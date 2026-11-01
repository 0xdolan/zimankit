# Changelog

All notable changes to zimankit are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-11-01

Central Kurdish is corrected against the written standard and the grammar sources. Spelling, transliteration, IPA, lemmas and word classes all change for some Central Kurdish words, so results will differ from 0.2.0: rebuild anything that stores them. Kurmanji is not affected.

### Fixed

Central Kurdish, checked against the written-standard and grammar sources in [chapter 23](docs/23-ckb-written-standard.md):

- **Normaliser**: keeps `ییی` (`سنەییی`) and `ڵڵ` (`ئەڵڵا`), and no longer merges `ر` with `ڕ` or `ل` with `ڵ`. It removes the ZWNJ in `سپی‌یە` and splits a ZWNJ-attached `و`.
- **Transliteration and IPA**: no second unwritten vowel in words like `منداڵ` (`mindall`, was `minidall`) and `کردووە` (`kirdûwe`); `ستران` is `stran`; a lone `چ` is `çi`. This also changes the `ipa` and `translit` columns of the lexicon when it is rebuilt.
- **`-ەوە` verbs**: no three-`و` forms (`چووەوە`, was `چوووە`); the perfect has `ت` (`خوێندووەتەوە`); `دۆزییەوە`.
- **Missing tenses**: negative perfects (`نەکردووە`, `نەهاتبوو`), the written long perfect (`هاتوومە`, with `هاتووم` as a variant), the past subjunctive (`خواردبا`, `خواردبێت`, `خواردبووبا`) and the full passive (`بکرێت`, `نەکرا`, `دەکرا`, `کرابوو`, `کرابا`). Reference pages show them, and the lexicon now reads very common forms such as `بکرێت` and `نەبووە` as verbs.
- **Nouns and function words**: final ە/یە (`مامۆستایە`, `ماڵدایە`), `ماڵدام`, indefinite `چرایێک`, `کەسانێک`, `کوڕێ`, plural `-گەل`, `سنەیی`, `ڕەشایی`, prefixes `بێ` `نا` `هاو`, compounds (`گوڵ+ە+گەنم`), and `پێ` `لێ` `تێ` as adpositions rather than nouns.
- **Documentation**: 37 sounds and the bizroke as a real vowel, the ezafe after ی and یی, vocatives, collective nouns, and Kurdish grammar terms in the glossary and in chapter 9.
- **Small forms**: the negative participle `نەهاتوو`, and `masîy` for `ماسیی`.
- **Spacing on tutorial pages and in lessons**: `standard_spelling` gives the split form (`هەڵم گرت`, `دەست پێ دەکەم`, `دەستم پێ کرد`), shown first with the solid form in small type. The course teaches the spacing standard and the clitic rules, including five jobs of the clitics, compound numbers and a write/not table.
- **Sorani clauses**: a verb after a subordinator is no longer the main verb, with the new relations `advcl`, `ccomp` and `acl:relcl`. Also `nsubj:pass`, a subject pronoun found by its person (`نان من دەخۆم`), `ئەو دەرگایە` with lemma `دەرگا`, and the terms `نیهاد` and `جێگری بکەر`.
- **Sorani agreement warnings** in the parser's `notes`: `من نان خوارد`, `هاتمان`, `من دەچیت`, and a usage note for `پیاوەکە دەچن`.
- **Verb list and guesser**: more core verbs (`خواستن`, `گواستن`, `سەندن`, `دڕان`, `دانان` and others), no false `وتن` splits (`پاڵاوتن`), and intransitive `ا` → `ێ` (`دەدڕێت`).
- **Imperatives**: `بچۆ` with `بڕۆ` also accepted, `بێ`, `نایێم`, and `ویستن` has a rare imperative and passive.
- **Recognised, never shown first**: `دەکا`, `دەڵێ`, `دەمەوێ`, `دەژێت`, `هاتۆتەوە`, `بکەرەوە`, `گرترا`, `ئەچم`, `بینیووە`, `گەڕاونەوە`, `دۆزیەوە`.
- **Nouns**: `ماسێکە`, `پەنجەران`, adverbs of manner (`بەخێرایی`), more suffixes (`-گەر`, `-زانی`), and `برا` reads as "brother". `مامۆستایان` returns both its readings.
- **Spelling variants**: `STANDARD_OVERRIDES` for spellings where frequency prefers the non-standard form (`وەکو`, `بەرامبەر`, `نیە`).
- **Agent clitic position**: on a preverb or compound verb it sits on the first part in every tense (`هەڵمنەگرت`, `هەڵمدەگرت`, `هەڵمگرتووە`). The older shapes stay recognised as a variant.
- **Split verbs**: `FormIndex.lookup_split` and the sentence parser read `هەڵم گرت`, `ڕای گەیاند` and `دەستم پێ کرد` as one verb. New relation `compound:prt`.
- **Object clitics**: `دەتبینم`, `هەڵیدەگرم`, `بمگرە`, `بینیمیت`, `گرتمی`, and `بۆمی` with two clitics.
- **Preverbs**: the full list of simple and complex preverbs.
- **Lexicon builder**: a core verb reading now beats a dictionary entry with no word class, so `کردووە`, `هاتووە` and `داوە` are verbs rather than nouns with broken lemmas. A word with a known remainder after `بێ`, `نا` or `هاو` is accepted.
- **Sentence structure**: bare adpositions (`پێی وت`), `من لە ماڵدام`, `تۆ زیرەکیت`, and definite adjective phrases (`پیاوە باشەکە هات`).
- **Preverb verbs**: `ب` is generated after the preverb (`هەڵبگرم`, `دابنیشە`), with the bare form as a variant. `ڕاکردن` takes the agent clitics.
- **Nouns in `وو`**: `خانووەکە`, `خانووێک`, `خانووان`.
- **Sentence structure**: in `نانم خوارد` the clitic host is the object, not the subject.
- **Sentences and tokens**: one-letter abbreviations do not end a sentence, closing quotes stay with their sentence, and a lone `ـ` is punctuation.

### Changed

- **`validate_word`** also reports the spelling standard (`ووشە`, `چو`, `ڵات`). The new `structural_problems` is what the wordlist builder rejects on, so common non-standard forms stay recognised.

### Added

- **Documentation**: [chapter 23, the Central Kurdish written standard](docs/23-ckb-written-standard.md): the rules, what zimankit implements of them, where the authorities disagree and what is still open.
- **Lexicon bundle**: `run_pipeline.py --stages bundle` packs the published lexicon into one reproducible file, `zimankit-lexicon-<version>.tar.zst`, for tools that build on it. It holds the words and lemmas as Parquet, the spelling variants, the grammar rules, the data card and the licence notice, and is attached to the GitHub release.

## [0.2.0] - 2026-10-31

### Added

- **Sentence structure**: `zimankit parse` and `zimankit.parse()` give the head and relation of each word (Universal Dependencies labels) with a plain-language explanation, using rules over the morphology. They cover subject and object by case and alignment (Kurmanji) or order (Sorani), adpositions, ezafe, determiners, coordination and the copula. Complex sentences get an approximate structure.
- **Sentence diagram in the playground**: coloured arrows between the words of a Sorani or Kurmanji sentence. Click a word, an arrow or a colour to see its role, position, form and what depends on it.
- **Documentation**: [chapter 22, Sentence structure](docs/22-sentence-structure.md), new glossary entries, the `kurdish-sentence-structure` agent skill, and the guide's `parse` section.
- **Diagram colours and export**: choose a colour for each relation or a preset (high contrast, colour-blind safe, single colour), with a warning for colours that are hard to read. Export the diagram as PNG, JPG, SVG or PDF in standard social media sizes at up to 3× resolution, with a header, footer and colour key, in light or dark.
- **Playground tools**: a view made for each tool, with result tables, verb grids by tense and person, before-and-after comparisons, readable JSON, and copy and download as JSON or CSV. Each tool and each word in the diagram links to the matching tutorial and documentation chapter.
- **Fonts**: Manrope for Latin text and Sahel for Kurdish in the Arabic-based script, with Estedad and Vazirmatn as choices for the reader. All are hosted with the site and contain every Kurdish letter.
- **PyPI**: `pip install zimankit`. Each version tag publishes the wheel and sdist through Trusted Publishing, and CI checks the package metadata on every push.
- **Website**: a full redesign. A clean white look with shadcn/ui-style tokens and Lucide icons, in light by default with an optional dark theme. Every page works from phone to desktop, with a mobile menu, collapsible contents, copy buttons, and a word table beside the sentence diagram. The sentence diagram is on the home page, with new screenshots in `assets/brand/screenshots/`.

### Changed

- **Brand kit**: the logo files, wordmarks, icons, social cards, ads, print files and the Kaggle cover are regenerated in the new design: white and black grounds, Manrope and Sahel, and the flag band with the flag's sun in its middle.
- **Install**: `pip install zimankit` is now the main way to install.

### Fixed

- A package classifier that PyPI does not accept is removed, and the README's links and images now work on the PyPI page.

## [0.1.0] - 2026-10-29

The first release.

### Added

- **Skills for Central Kurdish (Sorani, `ckb`) and Northern Kurdish (Kurmanji, `kmr`)**: orthographic normalisation and validation, tokenisation, language identification (with Zazaki, Gorani and the neighbouring languages), IPA / grapheme-to-phoneme with syllabification, transliteration (Sorani Arabic → Latin, Kurmanji Latin → Arabic), morphological analysis, full verb paradigms and split-ergativity checking for Kurmanji.
- **Python API** (`from zimankit import analyze, normalize, to_ipa, identify`) and the **`zimankit` command** (`normalize`, `tokenize`, `lid`, `ipa`, `translit`, `analyze`, `conjugate`, `ergativity`, `validate`, `rules`, `--version`). The skills need only the standard library.
- **Wordlist pipeline** (`run_pipeline.py`): reads `.mdx` dictionaries, `.zim` wiki dumps and plain-text corpora, and builds clean wordlists, lemma tables, variant maps and grammar-rule JSON.
- **Kaggle export**: one row per word with 59 flat columns, as CSV, Parquet and SQLite, with a data card and cover.
- **Documentation**: 21 developer chapters and two complete tutorials, Sorani and Kurmanji, with 23 lessons each. Their tables are generated by zimankit and checked by the tests.
- **Brand**: the logo, a deq tree-of-life sign with the sun of the flag of Kurdistan, and its story. A generated kit of logo, icon, wordmark, social, ad and print files is in `assets/brand/`.
- **Releases**: wheel, sdist, a Debian package and source archives, built by `scripts/build_release.sh` and published by GitHub Actions when a version tag is pushed. Continuous integration runs the tests on Python 3.11 to 3.13.
- **Website**: <https://0xdolan.github.io/zimankit/> has the guide, the story of the logo, the brand kit and a live playground that runs zimankit in the browser.

[Unreleased]: https://github.com/0xdolan/zimankit/compare/v0.3.0...develop
[0.3.0]: https://github.com/0xdolan/zimankit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/0xdolan/zimankit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/0xdolan/zimankit/releases/tag/v0.1.0
