---
name: kmr-morphology
description: Analyse Northern Kurdish (Kurmanji) nouns for gender, number, definiteness, case (direct/oblique/vocative) and ezafe (-a, -ê, -î, -ên, -an, -ek, -ekê, -ekî …), resolving the -ê ambiguity with lexical gender. Use for Kurmanji lemmatization, gender/case tagging or ezafe questions.
---

# kmr-morphology

Analyse Northern Kurdish (Kurmanji) nouns for gender, number, definiteness, case (direct/oblique/vocative) and ezafe (-a, -ê, -î, -ên, -an, -ek, -ekê, -ekî …), resolving the -ê ambiguity with lexical gender. Use for Kurmanji lemmatization, gender/case tagging or ezafe questions.

Full explanation: [docs/13-kmr-morphology.md](../../docs/13-kmr-morphology.md)

## Commands

```bash
python -m zimankit analyze jinekê malê bavê --top 2
```

## Python

```python
from zimankit.skills_kmr.morphology import KmrAnalyzer
from zimankit.shared_utils.schema import SimpleLexicon
```

## Rules to apply

1. -a = feminine ezafe; -ekê = feminine indefinite oblique; -ekî = masculine indefinite oblique.
2. -ê = masculine ezafe OR feminine oblique: decide with the noun's gender (mal f → oblique, bav m → ezafe).
3. After vowel-final stems the suffix takes y: mamosteyê, deriyê.
4. Lexicon gender tag 'm' in Kurdish sources means mê = FEMININE; 'n' = nêr = masculine.
5. Load output/kmr/lemmas_kmr.csv (gender column) into SimpleLexicon for best results.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
