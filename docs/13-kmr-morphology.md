<!-- nav:top -->
[← Northern Kurdish: phonology and IPA](12-kmr-phonology-ipa.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: verbs and split ergativity →](14-kmr-verbs-ergativity.md)
<!-- nav:top -->

# Northern Kurdish: nominal morphology (gender, case, ezafe)

**On this page:** [The inflection table (`skills_kmr/morphology.py: INFLECTIONS`)](#the-inflection-table-skills_kmrmorphologypy-inflections) · [The -ê ambiguity](#the--ê-ambiguity) · [Gender inferred from the data](#gender-inferred-from-the-data)

Kurmanji fuses gender, number, definiteness and case into **one suffix slot** after an optional derivational suffix.

```
STEM [DERIV] [INFLECTION]
jin           ekê     -> jinekê  "a woman" (indefinite, oblique, feminine)
```

## The inflection table (`skills_kmr/morphology.py: INFLECTIONS`)

| suffix (after C / V) | meaning | gender evidence |
|---|---|---|
| -a / -ya | ezafe sg (definite construct) | **feminine** |
| -ê / -yê | ezafe sg **or** oblique sg | m (ezafe) / f (oblique) |
| -î / -yî | oblique sg | masculine |
| -ên / -yên | ezafe pl | — |
| -an / -yan | oblique pl | — |
| -ek / -yek | indefinite | — |
| -ekê / -yekê | indefinite oblique | **feminine** |
| -ekî / -yekî | indefinite oblique | **masculine** |
| -eke / -yeke | indefinite ezafe | — |
| -in, -inan, -ine | indefinite plural (dir / obl / ezafe) | — |
| -o, -ino | vocative m / pl | |

Derivational suffixes: `-ahî -tî -anî -î` (abstract), `-dar` (possessor), `-van -kar -ger` (agent), `-stan -geh -xane` (place), `-ane` (adverb), `-tir -tirîn` (comparison), `-ok -ik` (diminutive).

## The -ê ambiguity

`malê` can be *the house (oblique)* — `mal` is feminine — while `bavê` is *father-of (ezafe)* — `bav` is masculine. The analyzer resolves it with the lexical gender harvested from the dictionary wiki (`mal f`, `bav m`); with no gender it returns both readings. A feminine-only suffix (`-a`, `-ekê`) on a masculine noun is penalised.

```python
from zimankit.skills_kmr.morphology import KmrAnalyzer
from zimankit.shared_utils.schema import SimpleLexicon
lex = SimpleLexicon(); lex.add("mal", "NOUN", "f"); lex.add("bav", "NOUN", "m")
an = KmrAnalyzer(lex)
an.best("malê").features   # {'definite': 'def', 'number': 'sg', 'gender': 'f', 'case': 'obl'}
an.best("bavê").features   # {'definite': 'def', 'number': 'sg', 'gender': 'm', 'ezafe': 'yes'}
an.best("jinekê").features # {'definite': 'ind', 'number': 'sg', 'case': 'obl', 'gender': 'f'}
```

## Gender inferred from the data

Even without a lexicon tag, the suffix itself is evidence: `-ekê` and `-a` occur only with feminine nouns, `-ekî` only with masculine ones. The builder writes the analysis features into `morph_meta`, so gender is visible per form in `clean_wordlist_kmr.csv`.

<!-- nav:bottom -->
---
[← Northern Kurdish: phonology and IPA](12-kmr-phonology-ipa.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: verbs and split ergativity →](14-kmr-verbs-ergativity.md)
<!-- nav:bottom -->
