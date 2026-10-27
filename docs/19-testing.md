<!-- nav:top -->
[← Examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java](18-multi-language-examples.md) · [⌂ Contents](00-index.md) · [Glossary →](20-glossary.md)
<!-- nav:top -->

# Testing and the verification matrix

**On this page:** [Ground-truth matrix (`tests/test_ground_truth.py`)](#ground-truth-matrix-teststest_ground_truthpy) · [What else is covered](#what-else-is-covered) · [Data-level checks (build report)](#data-level-checks-build-report) · [Known limitations](#known-limitations)

```bash
python -m pytest -q          # 44+ tests
./scripts/check_examples.sh  # cross-language examples vs expected_output.txt
```

## Ground-truth matrix (`tests/test_ground_truth.py`)

| variety | input | lemma | features | IPA |
|---|---|---|---|---|
| ckb | پیاوەکە | پیاو | definite noun (`-eke`) | /pjaːwækæ/ |
| ckb | کتێبەکەم | کتێب | definite + 1sg enclitic `-m` | /k(ɯ)teːbækæm/ |
| kmr | jinekê | jin | feminine sg, oblique, indefinite (`-ekê`) | /ʒɪnɛkeː/ |
| kmr | dîtin | dîtin | infinitive; past stem `dît`, transitive | /diːtɯn/ |

All four pass **without** any lexicon (pure rules), and stay correct with the full lexicon loaded.

## What else is covered

| file | covers |
|---|---|
| test_ckb.py | normalisation (kaf/yeh, heh doachashmee, legacy ZWNJ, initial r, digits, punctuation), validation, IPA + epenthesis, Latin, syllables, paradigms (present, ergative past, preverbs, irregular هاتن), stacked suffixes, enclitic/definite helpers, spelling variants |
| test_kmr.py | look-alike folding, Turkish-safe casing, validation, IPA broad/narrow, paradigms (irregular hatin, ni-negation, preverbs), gender-driven -ê disambiguation, split-ergativity agreement (5 sentences), Arabic-script transliteration |
| test_shared.py | LID (ckb, kmr, zza, eng), tokenizer, bidi/space cleaning, edit distances, regex cookbook, epenthesis core |

## Data-level checks (build report)

`output/<lang>/build_report_<lang>.json` contains, per build: lexicon size, corpus tokens/types, accepted forms and lemmas, rejection reasons, POS and source distributions, number of spelling variants, and the **mean similarity of generated IPA to reference transcriptions** in the lexicon source. Watch these numbers when changing a rule.

## Known limitations

* Bizroke placement is phonotactic; a few morpheme-boundary cases differ from careful pronunciation (`کردبووم` is rendered *kɯɾ.dɯ.buːm*, careful speech *kird.bûm*), because any rule that fixes it breaks `کردنەوە` *kir.di.ne.we*.
* Rule-based LID needs ~8 words; single words are judged by orthography and attestation.
* Present stems of verbs that are neither in the reference list nor in the lexicon are guessed from regular patterns.
* Hawar spelling hides aspiration; narrow IPA marks unaspirated stops only where the input uses the apostrophe convention.

<!-- nav:bottom -->
---
[← Examples in shell, Python, TypeScript, C#, F#/.NET, Rust, Go and Java](18-multi-language-examples.md) · [⌂ Contents](00-index.md) · [Glossary →](20-glossary.md)
<!-- nav:bottom -->
