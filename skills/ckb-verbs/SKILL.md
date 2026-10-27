---
name: ckb-verbs
description: Conjugate and recognise Central Kurdish (Sorani) verbs: present/subjunctive/imperative, ergative past with agent enclitics, progressive, perfect, pluperfect, passive, preverbs (هەڵ، دا، ڕا…) and -ەوە verbs. Use for verb paradigms, verb lemmatization or past-tense agreement questions in Sorani.
---

# ckb-verbs

Conjugate and recognise Central Kurdish (Sorani) verbs: present/subjunctive/imperative, ergative past with agent enclitics, progressive, perfect, pluperfect, passive, preverbs (هەڵ، دا، ڕا…) and -ەوە verbs. Use for verb paradigms, verb lemmatization or past-tense agreement questions in Sorani.

Full explanation: [docs/10-ckb-verbs.md](../../docs/10-ckb-verbs.md)

## Commands

```bash
python -m zimankit conjugate کردن
python -m zimankit conjugate هەڵگرتن | grep present
python -m zimankit analyze نەمکرد کردوومە دەکرێت
```

## Python

```python
from zimankit.skills_ckb.verbs import conjugate, default_index, make_verb
```

## Rules to apply

1. Past stem = infinitive − ن; present stem is lexical (کردن→کە, بردن→بە, گوتن→ڵێ, هاتن→ێ).
2. Set-1 endings (م یت ێت ین ن) mark the subject of present tenses and intransitive pasts.
3. Set-2 enclitics (م ت ی مان تان یان) mark the agent of transitive pasts: کردم, نەمکرد, دەمکرد — ergative alignment.
4. Preverbs precede دە/نا and suppress subjunctive ب: هەڵدەگرم, هەڵگرم.
5. Irregulars: هاتن (دێم, نایەم, وەرە), چوون (imperative بڕۆ).

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
