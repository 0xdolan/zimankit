<!-- nav:top -->
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:top -->

# Central Kurdish: verbs

**On this page:** [Stems](#stems) · [Agreement](#agreement) · [Paradigm of کردن (excerpt, from `python -m zimankit conjugate کردن`)](#paradigm-of-کردن-excerpt-from-python--m-zimankit-conjugate-کردن)

`skills_ckb/verbs.py` describes a verb with **infinitive, past stem, present stem, transitivity, preverb, -ەوە suffix** and generates every single-word form. The analyzer recognises verbs by looking the token up in the inverted paradigm (`FormIndex`).

## Stems

* past stem = infinitive − `ن`: `کردن → کرد`, `چوون → چوو`, `نووسین → نووسی`, `هێنان → هێنا`.
* present stem is lexical: `کردن → کە`, `بردن → بە`, `گوتن → ڵێ`, `خواردن → خۆ`, `هاتن → ێ`. Reference list: `zimankit/data/ckb_verbs_core.tsv`; verbs from the lexicon use its stem, otherwise `guess_present_stem` applies the regular patterns (`-اند → -ێن`, `-ارد → -ێر`, `-ا/-ی → ∅`).
* preverbs `هەڵ وەر دەر دا ڕا تێ پێ لێ` precede the aspect marker: `هەڵدەگرم`. `ب` follows the preverb and may be dropped: `هەڵبگرم` or `هەڵگرم`, `دابنیشە` or `دانیشە`. Both forms are generated, the bare one with `variant=no_b`.
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

Intransitive `هاتن`: `هاتم هاتیت هات هاتین هاتن`, perfect `هاتووم … هاتووە`, irregular present `دێم دێیت دێت`, negative `نایەم`, imperative `وەرە`.

`-ەوە` verbs attach the suffix after the person ending: `دەکەمەوە`, `دەکاتەوە`, `کردیەوە`. Three `و` never occur: `چوو + ەوە = چووەوە`, `کردبوو + ەوە = کردبووەوە`. A stem in `ی` keeps its 3sg ending: `دۆزی + ی + ەوە = دۆزییەوە`. The perfect adds `ت` before `ەوە` and uses the long endings: `خوێندووەتەوە`, `خوێندوومانەتەوە`, `چووینەتەوە`. The 1sg and 2sg perfects (`کردوومەتەوە`, `هاتوویتەتەوە`) follow the pattern but are not printed in the sources checked.

<!-- nav:bottom -->
---
[← Central Kurdish: morphology](09-ckb-morphology.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: alphabet and orthography →](11-kmr-orthography.md)
<!-- nav:bottom -->
