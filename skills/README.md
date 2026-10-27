# Agent skills

Each folder is a self-contained skill (`SKILL.md` with YAML front-matter) that an agent can load to work with Kurdish. All of them call the `zimankit` package in this repository.

| skill | dialect | purpose |
|---|---|---|
| [ckb-orthography](ckb-orthography/SKILL.md) | ckb | Normalize and validate Central Kurdish (Sorani, Arabic script) text: Arabic kaf/yeh, heh variants, legacy heh+ZWNJ for ە, initial ڕ, ZWNJ/micro-space cleanup, digits and punctuation; detect non-standard spellings (ر/ڕ, ل/ڵ, ی/ێ, و/ۆ) |
| [ckb-phonology-ipa](ckb-phonology-ipa/SKILL.md) | ckb | Convert Central Kurdish (Sorani) Arabic-script words to IPA, syllables and Kurdish-Latin, re-inserting the unwritten bizroke vowel and resolving و/ی as w/u/uː and y/iː |
| [ckb-morphology](ckb-morphology/SKILL.md) | ckb | Segment and lemmatize Central Kurdish (Sorani) words: definiteness (-ەکە, -کە, -ەکان), indefinite -ێک, plural -ان, pronominal enclitics (م ت ی مان تان یان), additive -یش, postpositions -دا/-ەوە, comparatives, derivation and attached prepositions لە/بە/بۆ |
| [ckb-verbs](ckb-verbs/SKILL.md) | ckb | Conjugate and recognise Central Kurdish (Sorani) verbs: present/subjunctive/imperative, ergative past with agent enclitics, progressive, perfect, pluperfect, passive, preverbs (هەڵ، دا، ڕا…) and -ەوە verbs |
| [kmr-orthography](kmr-orthography/SKILL.md) | kmr | Normalize and validate Northern Kurdish (Kurmanji, Hawar Latin) text: fold é/ü/ı/İ/ș look-alikes to ê/û/i/I/ş, Kurdish-safe casing, apostrophe handling, digraphs xw/rr, foreign-letter detection |
| [kmr-phonology-ipa](kmr-phonology-ipa/SKILL.md) | kmr | Convert Northern Kurdish (Kurmanji) words to IPA (broad or narrow with aspiration and ŋ), syllabify, and transliterate to Kurdish Arabic script |
| [kmr-morphology](kmr-morphology/SKILL.md) | kmr | Analyse Northern Kurdish (Kurmanji) nouns for gender, number, definiteness, case (direct/oblique/vocative) and ezafe (-a, -ê, -î, -ên, -an, -ek, -ekê, -ekî …), resolving the -ê ambiguity with lexical gender |
| [kmr-verbs-ergativity](kmr-verbs-ergativity/SKILL.md) | kmr | Conjugate Northern Kurdish (Kurmanji) verbs and check clause alignment: present (nominative-accusative) vs past transitive (ergative: oblique agent, direct object, verb agrees with object) |
| [kurdish-language-id](kurdish-language-id/SKILL.md) | both | Identify whether text is Central Kurdish, Northern Kurdish, Gurani/Hawrami, Zazaki, Persian, Arabic, Turkish or English using function words, diagnostic letters and morphological regex features |
| [kurdish-wordlist-builder](kurdish-wordlist-builder/SKILL.md) | both | Build clean ckb and kmr wordlists (grapheme, lemma, pos, ipa, morph_meta, translit, frequency, sources, confidence) from MDX dictionaries, ZIM wiki dumps and text corpora, with LID filtering, orthographic gates, lexicon-backed analysis and spelling-variant mapping |
