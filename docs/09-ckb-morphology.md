<!-- nav:top -->
[← Central Kurdish: phonology and IPA (G2P)](08-ckb-phonology-ipa.md) · [⌂ Contents](00-index.md) · [Central Kurdish: verbs →](10-ckb-verbs.md)
<!-- nav:top -->

# Central Kurdish: morphology

**On this page:** [Nominal template](#nominal-template) · [Scoring](#scoring) · [Ambiguities kept on purpose](#ambiguities-kept-on-purpose)

`skills_ckb/morphology.py` — a generate-and-rank analyzer.

## Nominal template

```
[PREP] STEM [DERIV] [CMP] [NUM/DEF] [ENCLITIC] [ADD] [POSTP] [ە/یە]
 لە    ماڵ                ەکان       مان        یش    دا     -> لەماڵەکانمانیشدا "in our houses too"
```

| slot | after consonant | after vowel | meaning |
|---|---|---|---|
| DEF.SG | ەکە پیاوەکە | کە / یەکە دەرگاکە، ماسییەکە | the |
| DEF.PL | ەکان | کان / یەکان | the (pl) |
| INDEF | ێک پیاوێک | یەک دەرگایەک | a |
| PL | ان پیاوان | یان | plural |
| ENCLITIC | م ت ی مان تان یان | same | my, your … / agent of past transitive |
| ADD | یش | ش | too, also |
| POSTP | ەوە، دا، ڕا | وە، دا | circumposition halves (لە … دا "in") |

Nouns in وو take the after-consonant endings: خانووەکە, خانووێک, خانووان.

Also recognised:

* **Final ە/یە** (`کوردە`, `مامۆستایە`, `ماڵدایە`, `چاکترە`). One word cannot show which job it does: copula, definite ezafe, demonstrative, vocative or short definite. So it gets the tag `E` and the feature `copula=3sg|ezafe.def|dem|voc|def.short`, and the next word and any ئەم/ئەو decide. A word listed in the lexicon stays whole.
* **Person copula after -دا**: `ماڵ+دا+م` "I am at home" (`copula=1sg`). Elsewhere the same endings are the enclitics, so `باشم` is "my good" here. The sentence parser reads `تۆ زیرەکیت` as a copula when the subject pronoun's person matches.
* **Other indefinites**: `چرایێک`, `کەسانێک`, and with a known stem `کوڕێ`, `کوڕەک`. `ێ` also marks a place (`لە تارانێ`); it is the same segment, so it is tagged `POSTP.E` with `postposition=e|indef`.
* **Plural -گەل**: `کوڕگەل`.
* **Derivation**: `سنە+یی`, `ڕەش+ایی`, and with a known remainder the prefixes `بێ+کار`, `نا+دیار`, `هاو+کار`.
* **Compounds** of two known words, with the linkers ەو او بە ە و or none: `گوڵ+ە+گەنم`, `دەم+و+چاو`, `شار+ەو+شار`. They score below any known stem, and inflected compounds (`گوڵەگەنمەکە`) are not split.
* **پێ, لێ, تێ, بۆ + clitic** are adpositions: `پێ+م`, `لێ+ی`, `بۆ+مان`.
| CMP | تر، ترین | | comparative, superlative |
| DERIV | ایەتی، ێتی، ی، یی، ایی، انە، ستان، کار، دار | | abstract, nisba, adverbial, place, agent, possessor |

**Vowel- vs consonant-final is phonological**, not orthographic: `پیاو` ends in the consonant /w/ (→ `پیاوەکە`), `کوردی` in the vowel /iː/ (→ `کوردییەکە`). `_ends_with_vowel` treats final `و`/`ی` after a vowel letter as glides.

## Scoring

| evidence | score |
|---|---|
| stem is a lexicon lemma | +5 + log(freq)/4 |
| stem is a function word | +4 |
| unknown stem | −3 + log(freq)/3 |
| each affix | −0.4; +0.9 if ≥ 3 letters, +0.4 if 2 letters |
| one-letter affix on an unknown stem | −0.5 |
| one-letter enclitic right after DEF/PL | +0.6 |
| derivational suffix on an unknown stem | −1.5 |
| verb paradigm hit (reference verb) | 7.0 (lexicon-derived verb 5.5) |

So `کتێبەکەم` → `کتێب+ەکە+م` even with an empty lexicon (long `ەکە` is reliable), while `کوردی` stays a lemma when it is in the lexicon instead of becoming `کورد+ی`.

```python
from zimankit.skills_ckb.morphology import CkbAnalyzer
an = CkbAnalyzer()                       # pass SimpleLexicon(...) for best results
a = an.best("کتێبەکەم")
a.segmentation, a.gloss, a.features
# ('کتێب+ەکە+م', 'STEM+DEF.SG+1SG', {'definite': 'def', 'number': 'sg', 'enclitic': '1sg'})
```

## Ambiguities kept on purpose

* final `ی`: ezafe *or* 3sg enclitic (`ماڵی باوکم` vs `ماڵی`) → feature `enclitic=3sg|ezafe`.
* `یان`: plural after a vowel *or* 3pl enclitic — both readings are returned, ranked.
* final `ە`/`یە`: copula, definite ezafe, demonstrative, vocative or short definite → feature `copula=3sg|ezafe.def|dem|voc|def.short`.
* use `analyze()` (all readings) rather than `best()` for disambiguation in context.

<!-- nav:bottom -->
---
[← Central Kurdish: phonology and IPA (G2P)](08-ckb-phonology-ipa.md) · [⌂ Contents](00-index.md) · [Central Kurdish: verbs →](10-ckb-verbs.md)
<!-- nav:bottom -->
