<!-- nav:top -->
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:top -->

# Central Kurdish: verbs

**On this page:** [Stems](#stems) · [Agreement](#agreement) · [Paradigm of کردن (excerpt, from `python -m zimankit conjugate کردن`)](#paradigm-of-کردن-excerpt-from-python--m-zimankit-conjugate-کردن) · [Tenses and negatives](#tenses-and-negatives) · [Where the agent clitic goes on a verb with a first part](#where-the-agent-clitic-goes-on-a-verb-with-a-first-part) · [Object clitics](#object-clitics)

`skills_ckb/verbs.py` describes a verb with **infinitive, past stem, present stem, transitivity, preverb, -ەوە suffix** and generates every single-word form. The analyzer recognises verbs by looking the token up in the inverted paradigm (`FormIndex`).

## Stems

* past stem = infinitive − `ن`: `کردن → کرد`, `چوون → چوو`, `نووسین → نووسی`, `هێنان → هێنا`.
* present stem is lexical: `کردن → کە`, `بردن → بە`, `گوتن → ڵێ`, `خواردن → خۆ`, `هاتن → ێ`. Reference list: `zimankit/data/ckb_verbs_core.tsv`; verbs from the lexicon use its stem, otherwise `guess_present_stem` applies the regular patterns (`-اند → -ێن`, `-ارد → -ێر`, `-ا/-ی → ∅`).
* preverbs precede the aspect marker. Simple ones are `هەڵ وەر دەر دا ڕا ڕۆ ڕێ تێ پێ لێ`, and complex (ناسادە) ones are `پێدا تێدا پێڕا تێڕا لێڕا تێوە پێوە لێوە پێک تێک ڕێک وێک لێک`: `هەڵدەگرم`. `ب` follows the preverb and may be dropped: `هەڵبگرم` or `هەڵگرم`, `دابنیشە` or `دانیشە`. Both forms are generated, the bare one with `variant=no_b`.
* `ڕاکردن` means "run" but takes the agent clitics (`ڕام کرد`), so it is listed as transitive and has no passive.

## Agreement

* **Set 1** (verbal endings): `م یت ێت(ات) ین ن ن` — subject of present tenses and of intransitive past.
* **Set 2** (enclitics): `م ت ی مان تان یان` — the **agent of transitive past tenses** (ergative alignment): `کردم` "I did", `نەمکرد` "I didn't", `دەمکرد` "I used to do".

## Paradigm of کردن (excerpt, from `python -m zimankit conjugate کردن`)

| cell | 1sg | 3sg | 3pl |
|---|---|---|---|
| present | دەکەم | دەکات | دەکەن |
| negative present | ناکەم | ناکات | ناکەن |
| subjunctive | بکەم | بکات | بکەن |
| simple past (agent clitic) | کردم | کردی | کردیان |
| past progressive | دەمکرد | دەیکرد | دەیانکرد |
| present perfect | کردوومە | کردوویەتی | کردوویانە |
| past perfect | کردبووم | کردبووی | کردبوویان |
| passive present | دەکرێم | دەکرێت | دەکرێن |
| passive past | کرام | کرا | کران |
| imperative | بکە (2sg) · بکەن (2pl) · مەکە (prohibitive) | | |

Intransitive `هاتن`: `هاتم هاتیت هات هاتین هاتن`, perfect `هاتوومە هاتوویتە هاتووە هاتووینە هاتوونە` (the written form; `هاتووم هاتوویت هاتوون` are spoken and generated with `variant=short`), irregular present `دێم دێیت دێت`, negative `نایەم`, imperative `وەرە`.

`-ەوە` verbs attach the suffix after the person ending: `دەکەمەوە`, `دەکاتەوە`, `کردیەوە`. Three `و` never occur: `چوو + ەوە = چووەوە`, `کردبوو + ەوە = کردبووەوە`. A stem in `ی` keeps its 3sg ending: `دۆزی + ی + ەوە = دۆزییەوە`. The perfect adds `ت` before `ەوە` and uses the long endings: `خوێندووەتەوە`, `خوێندوومانەتەوە`, `چووینەتەوە`. The 1sg and 2sg perfects (`کردوومەتەوە`, `هاتوویتەتەوە`) follow the pattern but are not printed in the sources checked.

## Tenses and negatives

Every verb also generates these:

| tense | transitive | intransitive | passive |
|---|---|---|---|
| perfect, negative | `نەمکردووە` | `نەهاتوومە` | `نەکراوە` |
| past perfect, negative | `نەمکردبوو` | `نەهاتبووم` | `نەکرابوو` |
| past subjunctive | `خواردبام` | `هاتبام` | `کرابام` |
| perfect subjunctive | `خواردبێتم` | `هاتبێتم` | `کرابێتم` |
| past perfect subjunctive | `خواردبووبام` | `هاتبووبام` | `کرابووبام` |

The passive also has a subjunctive (`بکرێت`, `نەکرێت`), a negative past (`نەکرا`) and a progressive (`دەکرا`, `نەدەکرا`). Its perfect uses the short endings the sources print: `بینراوم`, `بینراوە`.

A negative past subjunctive with an agent clitic follows the general rule that the clitic comes after `نە` (`نەمخواردبا`). `نەخواردبام` is also accepted, with `variant=clitic_end`. Neither negative is printed in the sources checked, so treat them as unconfirmed.

A verb guessed from the lexicon gets the past subjunctive only if its past stem ends in a consonant. On a vowel-final stem the ending usually belongs to another word (`کوبا` "Cuba", `ڕازی بێت`), so a real form such as `دامەزرابێت` is not read as a verb yet.

## Where the agent clitic goes on a verb with a first part

On a preverb or compound verb the clitic sits directly on the first part, in every tense and in the negative:

| tense | form | written |
|---|---|---|
| past | `هەڵمگرت` | `هەڵم گرت` |
| past negative | `هەڵمنەگرت` | `هەڵم نەگرت` |
| past progressive | `هەڵمدەگرت` | `هەڵم دەگرت` |
| perfect | `هەڵمگرتووە` | `هەڵم گرتووە` |
| past perfect | `هەڵمگرتبوو` | `هەڵم گرتبوو` |

The paradigm index keeps one solid key for each form, and the older shapes (`هەڵنەمگرت`, `هەڵدەمگرت`, `هەڵگرتوومە`, `هەڵگرتم`) stay recognised with `variant=clitic_late`.

`FormIndex.lookup_split(tokens)` reads a verb written over two or three tokens: `هەڵم گرت`, `ڕای گەیاند`, `پێک دێم`, `دەست پێ دەکەم`, `دەستم پێ کرد`. The tokens before the last must be exactly the verb's first part, with or without a clitic, so an ordinary pair of words does not join. The sentence parser uses it, and labels the first parts `compound:prt`.

`Verb.always_split` says whether the first part is written apart even with no clitic: noun or adjective + light verb, and `پێ تێ لێ پێک تێک ڕێک`. The other preverbs split only around a clitic (`هەڵدەگرم`, but `هەڵم گرت`).

## Object clitics

A pronoun object makes six times as many forms, so these are recognised by stripping the object and looking up the rest, rather than listed in the paradigm. A reading needs a transitive verb, and a first or second person object must differ from the subject.

| form | meaning | shape |
|---|---|---|
| `دەتبینم` | I see you | `دە` + clitic + verb |
| `هەڵیدەگرم` | I pick it up | first part + clitic + verb |
| `بمگرە` | catch me! | `ب` + clitic + imperative (not `ت`, `تان`) |
| `بینیمیت` | I saw you | 1st or 2nd person agent, then the object ending |
| `گرتمی`, `بردینیان` | he caught me, they took us | object, then a 3rd person agent |

The result has `object=<person>`.

<!-- nav:bottom -->
---
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:bottom -->
