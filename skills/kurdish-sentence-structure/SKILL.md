---
name: kurdish-sentence-structure
description: Show how the words of a Central Kurdish (Sorani) or Northern Kurdish (Kurmanji) sentence depend on each other: the head and Universal Dependencies relation of each word, word order, split-ergative alignment and a plain-language explanation of each word. Use for sentence diagrams, grammar explanations, finding subjects and objects, or teaching Kurdish syntax.
---

# kurdish-sentence-structure

Show how the words of a Central Kurdish (Sorani) or Northern Kurdish (Kurmanji) sentence depend on each other: the head and Universal Dependencies relation of each word, word order, split-ergative alignment and a plain-language explanation of each word. Use for sentence diagrams, grammar explanations, finding subjects and objects, or teaching Kurdish syntax.

Full explanation: [docs/22-sentence-structure.md](../../docs/22-sentence-structure.md). Try it as a clickable diagram in the [playground](https://0xdolan.github.io/zimankit/playground.html).

## Commands

```bash
python -m zimankit parse "Min pirtûka nû li dibistanê xwend."      # id, word, lemma, upos, head, relation
python -m zimankit parse --json "ئەو پیاوە باشە."                  # also morphology, explanations, word order, alignment
```

## Python

```python
from zimankit import parse

p = parse("Min pirtûk xwend.")
[(w.text, w.deprel, w.head) for w in p.tokens]  # [('Min', 'nsubj', 3), ('pirtûk', 'obj', 3), ('xwend', 'root', 0), ('.', 'punct', 3)]
p.order                                         # 'subject object verb'
p.alignment["alignment"]                        # 'ergative' (Kurmanji only)
p.tokens[0].explanation                         # the role, position and form in plain language
```

## Rules to apply

1. The finite verb is the root. With a copula (Kurmanji *e*, Sorani -ە / -یە) the predicate is the root. In "V1 û V2" the first verb is the root and the second is its `conj`.
2. Adpositions (`case`) depend on the noun they mark, and that noun is `obl` of the verb.
3. A word after an ezafe-marked noun depends on that noun: `amod` for known adjectives, `nmod:poss` for pronouns, otherwise `nmod`.
4. Kurmanji past transitive: the oblique word is the subject (the agent), the direct word is the object, and the verb agrees with the object. Otherwise the direct word is the subject.
5. Sorani: the first free nominal is the subject and, with a transitive verb, the second is the object.
6. A nominal after the verb is `obl`, typically a goal (*Ez diçim malê*).

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] `notes` read: it says when no verb was recognised or a clause was left unclassified
- [ ] Treated as approximate for complex sentences: the analysis is rule-based, not a trained parser
- [ ] No source names or file paths in anything you output
