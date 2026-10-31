<!-- nav:top -->
[← References and further reading](21-references.md) · [⌂ Contents](00-index.md)
<!-- nav:top -->

# Sentence structure

**On this page:** [Command line](#command-line) · [Python](#python) · [Relations](#relations) · [How the rules work](#how-the-rules-work) · [Limits](#limits)

`zimankit parse` shows how the words of a sentence depend on each other. Every word gets a **head**, the word it depends on, and a **relation** to that head. The labels are those of [Universal Dependencies](https://universaldependencies.org/u/dep/).

It is a set of rules over zimankit's morphology, not a trained parser. It is reliable for simple clauses and approximate for complex ones. See [Limits](#limits).

<p align="center"><a href="https://0xdolan.github.io/zimankit/playground.html"><img src="../assets/brand/screenshots/website-sentence-word.png" width="760" alt="a Kurmanji sentence drawn as coloured arrows between its words, with one word selected and explained"></a></p>

The [playground](https://0xdolan.github.io/zimankit/playground.html) draws the result as a diagram. Click a word, an arrow or a colour to see its role, position, form and what depends on it, with links to the lessons that explain it. "Show all", Escape or a click on the empty part of the diagram clears the selection. You can also choose the colours, and export the diagram as PNG, JPG, SVG or PDF in standard social media sizes.

## Command line

```
$ zimankit parse "Min pirtûka nû li dibistanê xwend."
1	Min	min	PRON	6	nsubj
2	pirtûka	pirtûk	NOUN	6	obj
3	nû	nû	NOUN	2	nmod
4	li	li	ADP	5	case
5	dibistanê	dibistan	NOUN	6	obl
6	xwend	xwendin	VERB	0	root
7	.	.	PUNCT	6	punct
```

The columns are position, word, dictionary form, word class, head (0 for the root) and relation. Use `--lang ckb` or `--lang kmr` to override the language, which is otherwise detected from the script. `--json` prints everything below.

## Python

```python
from zimankit import parse

p = parse("Min tu dîtim.")
p.lang                      # 'kmr'
p.order                     # 'subject object verb'
p.alignment["alignment"]    # 'ergative'
p.alignment["agreement_ok"] # False
p.notes                     # what the rules were unsure about

w = p.tokens[0]
w.text, w.lemma, w.upos     # ('Min', 'min', 'PRON')
w.head, w.deprel            # (3, 'nsubj')
w.relation, w.kurdish       # ('subject', 'kirde')
w.segmentation, w.gloss     # the word's parts and their tags
w.features                  # {'person': '1sg', 'case': 'obl'}
w.position, w.detail        # where it stands, and what its form says
w.explanation               # all of it as one text
```

`p.to_dict()` gives the same as plain data. The code is in [`zimankit/dependency.py`](../zimankit/dependency.py).

## Relations

| label | name | meaning | example |
|---|---|---|---|
| `root` | main verb, or predicate | the head of the sentence | **xwend** |
| `nsubj` | subject | who or what does the action, or is described | **Min** pirtûk xwend |
| `obj` | object | what the action is done to | Min **pirtûk** xwend |
| `obl` | oblique | a place, time, goal or other circumstance | li **dibistanê** |
| `case` | adposition | a preposition or postposition that marks its noun | **li** dibistanê |
| `amod` | adjective modifier | a known adjective joined by ezafe | |
| `nmod` | noun modifier | a word joined by ezafe: an attribute or a possessor | pirtûka **nû** |
| `nmod:poss` | possessor | a pronoun joined by ezafe | jina **min** |
| `det` | determiner | a demonstrative or similar word | **ئەو** پیاوە |
| `nummod` | number | a number that counts the noun | |
| `advmod` | adverb | a word that modifies the action | **زۆر** باشە |
| `aux` | auxiliary | a helping verb | |
| `cop` | copula | the verb "to be" | Ew baş **e** |
| `cc` | conjunction | a word that links two parts | Ez **û** tu |
| `conj` | conjunct | a word linked to an earlier word of the same kind | Ez û **tu** |
| `mark` | subordinator | a word that introduces a subordinate clause | |
| `punct` | punctuation | punctuation, attached to the root | |
| `dep` | other | a word the rules could not classify | |

## How the rules work

1. **Choose the reading of each word.** The morphology offers several readings, and context picks one: the oblique after a preposition (*li dibistan+ê*), the ezafe before a modifier (*pirtûk+a nû*). Among fitting readings, those without derivational suffixes come first (*dibistan+ê*, not *dib+istan+ê*).
2. **Sorani endings.** Three endings are read from context: the goal -ە on a verb (دەچم+ە), the -ە that completes a demonstrative (ئەو پیاو+ە), and the copula -ە / -یە on the predicate (باش+ە).
3. **Find the root.** It is the finite verb. With a copula it is the predicate. In coordinated verbs (*xwar û çû*) it is the first verb, and the later ones are its conjuncts.
4. **Attach the small words.** Adpositions attach to their noun, which becomes `obl`. Stacked prepositions (*ji bo te*) both attach to the same noun. Determiners and numbers attach to the noun after them.
5. **Follow the ezafe.** The word after an ezafe-marked noun depends on that noun.
6. **Find the core arguments**, clause by clause, among the nominals still free before the verb:
   - **Kurmanji, past transitive (ergative):** the oblique word is the subject and the direct word is the object. See [chapter 14](14-kmr-verbs-ergativity.md).
   - **Kurmanji, otherwise:** the direct word is the subject, and with a transitive verb the next word is the object.
   - **Sorani:** the first word is the subject, and with a transitive verb the second is the object.
7. **Attach the rest.** Other nominals become `obl`, including those after the verb (*Ez diçim malê*). Adverbs, conjunctions and subordinators attach to their clause's verb.

For Kurmanji, the agreement check is the same as `zimankit ergativity`. A plural verb with coordinated arguments (*Ez û tu diçin*) is not reported as an error.

## Limits

- **Unknown words.** The morphology does not know every word, so an unknown verb can be read as a noun, and adjectives often have the word class `NOUN`. That is why a modifier like *nû* is labelled `nmod` and not `amod`.
- **Several clauses.** Coordinated verbs are handled. Subordinate clauses (*ku*, کە) are attached to a verb without being classified, and `notes` says so.
- **Free word order.** The Sorani rule relies on order, so an object placed before the subject is read wrongly unless other marks decide it.
- **Dropped subjects.** Kurdish often leaves out the subject. The verb ending and the Sorani person clitics show it, but no word is added to the structure.

If a simple sentence gets a wrong structure, please [open an issue](https://github.com/0xdolan/zimankit/issues) with the sentence.

<!-- nav:bottom -->
---
[← References and further reading](21-references.md) · [⌂ Contents](00-index.md)
<!-- nav:bottom -->
