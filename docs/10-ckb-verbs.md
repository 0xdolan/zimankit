<!-- nav:top -->
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:top -->

# Central Kurdish: verbs

**On this page:** [Stems](#stems) · [Agreement](#agreement) · [Paradigm of کردن (excerpt, from `python -m zimankit conjugate کردن`)](#paradigm-of-کردن-excerpt-from-python--m-zimankit-conjugate-کردن) · [Words built on the verb](#words-built-on-the-verb) · [Tenses and negatives](#tenses-and-negatives) · [Where the agent clitic goes on a verb with a first part](#where-the-agent-clitic-goes-on-a-verb-with-a-first-part) · [Object clitics](#object-clitics)

`skills_ckb/verbs.py` describes a verb with **infinitive, past stem, present stem, transitivity, preverb, -ەوە suffix** and generates every single-word form. The analyzer recognises verbs by looking the token up in the inverted paradigm (`FormIndex`).

## Stems

* past stem = infinitive − `ن`: `کردن → کرد`, `چوون → چوو`, `نووسین → نووسی`, `هێنان → هێنا`.
* present stem is lexical: `کردن → کە`, `بردن → بە`, `گوتن → ڵێ`, `خواردن → خۆ`, `هاتن → ێ`. Reference list: `zimankit/data/ckb_verbs_core.tsv`; verbs from the lexicon use its stem, otherwise `guess_present_stem` applies the regular patterns (`-اند → -ێن`, `-ارد → -ێر`, `-ی → ∅`, `-ا → ∅` if transitive and `-ێ` if intransitive, `-وو` unchanged).
* preverbs precede the aspect marker. Simple ones are `هەڵ وەر دەر دا ڕا ڕۆ ڕێ تێ پێ لێ`, and complex (ناسادە) ones are `پێدا تێدا پێڕا تێڕا لێڕا تێوە پێوە لێوە پێک تێک ڕێک وێک لێک`: `هەڵدەگرم`. `ب` follows the preverb and may be dropped: `هەڵبگرم` or `هەڵگرم`, `دابنیشە` or `دانیشە`. Both forms are generated, the bare one with `variant=no_b`.
* `ڕاکردن` means "run" but takes the agent clitics (`ڕام کرد`), so it is listed as transitive and has no passive.

## Agreement

Kurdish grammars number the person markers differently, so readers of them should map the names:

| zimankit | Kurdish grammars | forms | use |
|---|---|---|---|
| set 2 | کۆمەڵەی یەکەم (ک١) | `م ت ی مان تان یان` | agent of the transitive past |
| set 1, past | کۆمەڵەی دووەم (ک٢) | `م یت – ین ن ن` | subject of the intransitive past, object of the transitive past |
| set 1, present | کۆمەڵەی سێیەم (ک٣) | `م یت ێت/ات ین ن ن` | present |
| imperative | کۆمەڵەی چوارەم (ک٤) | `ە/– ن` | imperative |

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

Other irregular cells: the imperative of `چوون` is `بچۆ`, `بچن`, and `بڕۆ`, `بڕۆن` (from `ڕۆیشتن`) are accepted too. `هاتن` keeps `وەرە`, `وەرن`, `نایەم`, `مەیە` first and also accepts `بێ`, `بێن`, `نایێم`, `مەیێ`. `ویستن` has a rare imperative (`بتەوێ`) and passive (`ویسترا`).

Recognised but never shown first: dropped `ت` in speech and poetry (`دەکا`, `دەڵێ`, `دەمەوێ`, `دەکەی`, `دەبینرێ`, with `variant=short`), `دەژێت` beside `دەژی`, `هاتۆتەوە`, `بکەرەوە` (older or Sulaimani; the current textbook has `بکەوە`), `گرترا` and `بردرا`, and `ئەچم`, `ئەخوارد` with the eastern `ئە-` for core verbs (`variant=dialect_ae`). A variant never hides a function word (`بێ`, the adposition). The forms `نا` and `نان` of the verb "put" are not indexed, because they are almost always the particle and the noun.

`-ەوە` verbs attach the suffix after the person ending: `دەکەمەوە`, `دەکاتەوە`, `کردیەوە`. Three `و` never occur: `چوو + ەوە = چووەوە`, `کردبوو + ەوە = کردبووەوە`. A stem in `ی` keeps its 3sg ending: `دۆزی + ی + ەوە = دۆزییەوە`. The perfect adds `ت` before `ەوە` and uses the long endings: `خوێندووەتەوە`, `خوێندوومانەتەوە`, `چووینەتەوە`. The 1sg and 2sg perfects (`کردوومەتەوە`, `هاتوویتەتەوە`) follow the pattern but are not printed in the sources checked.

## Words built on the verb

Kurdish grammars name these: ناوی بکەر (doer), ناوی بەرکار (thing done), چاوگ (infinitive), ناوی جێگا (place) and ناوی ئامێر (tool). Only the infinitive and the participles are generated, including the negative `نەهاتوو`. Endings such as `ەر`, `گە`, `ەک`, `ۆک` are treated as part of the lexicon, because they do not apply regularly.

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

`standard_spelling(verb, form)` gives the spacing the standard writes, and the tutorial pages show it first with the solid form in small type. `Verb.always_split` says whether the first part is written apart even with no clitic: noun or adjective + light verb, and `پێ تێ لێ پێک تێک ڕێک`. The other preverbs split only around a clitic (`هەڵدەگرم`, but `هەڵم گرت`).

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

## Elements stripped before lookup

The paradigm lists every person, tense and negative, but some elements can be added to almost any cell. Listing them would multiply the paradigm many times, so the analyser removes them and looks up what is left. This only happens when the word has no other verb reading. The inventory follows the verb template in Ahmadi (2021, Table 1) and the rule groups of the KLPT Hunspell file (Ahmadi 2020).

| element | example | what is looked up | feature |
|---|---|---|---|
| `ئە` for `دە` | `ئەچم`, `نەیئەکرد` | `دەچم` | `variant=dialect_ae` |
| particle `ەوە` | `دەیخۆمەوە`, `کڕیومەتەوە`, `بیخۆرەوە` | `دەیخۆم` | `particle=ewe`, lemma `…ەوە` if that verb is listed |
| regional `ەوانێ` / `ەو` | `هاتمەوانێ` (Sulaymaniyah), `گەڕامەو` (Sanandaj) | `هاتمەوە` | `particle_variant=ewanê` / `ew` |
| directional `ە`, `تە` after the perfect | `دەچمە`, `ڕۆیشتووەتە` | `دەچم` | `goal=yes` |
| conditional `ایە` | `بمردایە`, `کردبووایە` | `مرد` | `mood=conditional` |
| `ب` before the past subjunctive | `بهاتبام` | `هاتبام` | |
| additive `یش`/`ش` inside the verb | `نەشیانبینیبووم`, `هەڵیشیدەگرت`, `هاتیشم` | `نەیانبینیبووم` | `additive=yes` |

Up to three elements can be stacked (`ئەچمەو` is `ئە` + `ەو`). The object endings of the perfect and the past perfect are also recognised: `بینیبووم` + `ن`, `کردووم` + `ن`.

Limits, so that real words are not taken for verbs:

* the additive is accepted only right after a first element (`دە`, `نە`, `نا`, `مە`, `ئە`, `ب`, a preverb) or before a personal ending, and the first element must really be one: `بشارینەوە` is not `ب` + `ش` + `بارین`;
* a word whose beginning is in the lexicon keeps that reading: `نەخۆشن` is the adjective `نەخۆش`;
* a shorter form that is a listed noun or function word is not used: `داخەوەش` is `داخەوە` + `ش`;
* the directional `ە` and the additive apply to core verbs only, and an additive reading scores lower than the others.

`نەشیانبینیبووم` is the example Ahmadi (2021, p. 10) gives of a form the Hunspell rules do not reach.

Measured on the built word list (368,810 words), these rules turn 1,614 words (97,495 tokens) from a nominal reading into a verb, and change no verb into something else. A few rare forms are still misread, for example `دەبەشنەوە` (read as `بردن`) and `دەچێشت` (read as `چوون`).

<!-- nav:bottom -->
---
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:bottom -->
