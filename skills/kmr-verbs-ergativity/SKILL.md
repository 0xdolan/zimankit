---
name: kmr-verbs-ergativity
description: Conjugate Northern Kurdish (Kurmanji) verbs and check clause alignment: present (nominative-accusative) vs past transitive (ergative: oblique agent, direct object, verb agrees with object). Use for Kurmanji verb paradigms, agreement checking or grammar correction of past-tense transitive sentences.
---

# kmr-verbs-ergativity

Conjugate Northern Kurdish (Kurmanji) verbs and check clause alignment: present (nominative-accusative) vs past transitive (ergative: oblique agent, direct object, verb agrees with object). Use for Kurmanji verb paradigms, agreement checking or grammar correction of past-tense transitive sentences.

Full explanation: [docs/14-kmr-verbs-ergativity.md](../../docs/14-kmr-verbs-ergativity.md)

## Commands

```bash
python -m zimankit conjugate dîtin
echo "Min tu dîtim." | python -m zimankit ergativity   # agreement_ok: false
```

## Python

```python
from zimankit.skills_kmr.verbs import conjugate, default_index
from zimankit.skills_kmr.syntax import detect_alignment
```

## Rules to apply

1. Past stem = infinitive − in/n; present stem lexical (dîtin→bîn, kirin→k, hatin→ê).
2. Endings -im -î -e/-ø -in (after vowels -m -yî -ø -n); prefixes di-/t-, bi-, na-/ni-, ne-, nedi-.
3. Past transitive: agent oblique (min, te, wî, wê, me, we, wan), object direct (ez, tu, ew, em, hûn), verb agrees with the object.
4. ew/ev are 3sg or plural — accept either agreement.
5. Skip arguments of prepositions (di, ji, bi, li, ser …) when looking for agent/object.

## Checklist

- [ ] Input normalised with the dialect's orthography skill first
- [ ] Results checked against `tests/` expectations when rules are changed
- [ ] No source names or file paths in anything you output
