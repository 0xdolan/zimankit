<!-- nav:top -->
[← 18. The perfect tenses](18-perfect-tenses.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [20. Preverbs, -ەوە verbs and compound verbs →](20-preverbs-and-compound-verbs.md)
<!-- nav:top -->

# 19. The passive

**Level:** 🔴 Advanced · lesson 19 of 23

**On this page:** [A real passive verb](#a-real-passive-verb) · [Paradigms](#paradigms) · [Participle and perfect](#participle-and-perfect) · [The agent](#the-agent) · [Summary](#summary)

## A real passive verb

English builds the passive with *be* + participle (*is written*). Sorani has a **morphological passive**: a special stem made from the **present stem** + **-ر-**, inflected like an intransitive verb.

| infinitive | present stem | passive stem | present passive | past passive |
|---|---|---|---|---|
| کردن | کە | کر | دەکرێت *is done* | کرا *was done* |
| نووسین | نووس | نووسر | دەنووسرێت | نووسرا |
| خواردن | خۆ | خور | دەخورێت | خورا |
| ناردن | نێر | نێردر | دەنێردرێت | نێردرا |
| گوتن | ڵێ | **گوتر** (irregular) | دەگوترێت | گوترا |
| گرتن | گر | **گیر** (irregular) | دەگیرێت | گیرا |

Rules zimankit applies (`_passive_stem` in `skills_ckb/verbs.py`):

1. a present stem ending in **ە / ێ / ی** drops that vowel: کە → کر;
2. ۆ becomes **و**: خۆ → خور;
3. a stem ending in **ر / ڕ** adds **د**: نێر → نێردر, کڕ → کڕدر;
4. a few verbs are listed as exceptions (گوتن، وتن، گرتن، بیستن); ویستن *to want* has no passive at all.

## Paradigms

<!-- gen:verb verb=کردن cells=passive_present,passive_present_neg,passive_past -->
*کردن* (kirdin) “to do, to make” — present stem **کە**, past stem **کرد**, transitive

| person | pronoun | Passive present | Passive present negative | Passive past |
|---|---|---|---|---|
| 1sg | من | **دەکرێم**<br><sub>dekrêm</sub> | **ناکرێم**<br><sub>nakrêm</sub> | **کرام**<br><sub>kiram</sub> |
| 2sg | تۆ | **دەکرێیت**<br><sub>dekrêyt</sub> | **ناکرێیت**<br><sub>nakrêyt</sub> | **کرایت**<br><sub>kirayt</sub> |
| 3sg | ئەو | **دەکرێت**<br><sub>dekrêt</sub> | **ناکرێت**<br><sub>nakrêt</sub> | **کرا**<br><sub>kira</sub> |
| 1pl | ئێمە | **دەکرێین**<br><sub>dekrêyn</sub> | **ناکرێین**<br><sub>nakrêyn</sub> | **کراین**<br><sub>kirayn</sub> |
| 2pl | ئێوە | **دەکرێن**<br><sub>dekrên</sub> | **ناکرێن**<br><sub>nakrên</sub> | **کران**<br><sub>kiran</sub> |
| 3pl | ئەوان | **دەکرێن**<br><sub>dekrên</sub> | **ناکرێن**<br><sub>nakrên</sub> | **کران**<br><sub>kiran</sub> |
<!-- /gen -->

<!-- gen:verb verb=نووسین cells=passive_present,passive_past -->
*نووسین* (nûsîn) “to write” — present stem **نووس**, past stem **نووسی**, transitive

| person | pronoun | Passive present | Passive past |
|---|---|---|---|
| 1sg | من | **دەنووسرێم**<br><sub>denûsrêm</sub> | **نووسرام**<br><sub>nûsram</sub> |
| 2sg | تۆ | **دەنووسرێیت**<br><sub>denûsrêyt</sub> | **نووسرایت**<br><sub>nûsrayt</sub> |
| 3sg | ئەو | **دەنووسرێت**<br><sub>denûsrêt</sub> | **نووسرا**<br><sub>nûsra</sub> |
| 1pl | ئێمە | **دەنووسرێین**<br><sub>denûsrêyn</sub> | **نووسراین**<br><sub>nûsrayn</sub> |
| 2pl | ئێوە | **دەنووسرێن**<br><sub>denûsrên</sub> | **نووسران**<br><sub>nûsran</sub> |
| 3pl | ئەوان | **دەنووسرێن**<br><sub>denûsrên</sub> | **نووسران**<br><sub>nûsran</sub> |
<!-- /gen -->

<!-- gen:verb verb=ناردن cells=passive_present,passive_past -->
*ناردن* (nardin) “to send” — present stem **نێر**, past stem **نارد**, transitive

| person | pronoun | Passive present | Passive past |
|---|---|---|---|
| 1sg | من | **دەنێردرێم**<br><sub>denêrdirêm</sub> | **نێردرام**<br><sub>nêrdiram</sub> |
| 2sg | تۆ | **دەنێردرێیت**<br><sub>denêrdirêyt</sub> | **نێردرایت**<br><sub>nêrdirayt</sub> |
| 3sg | ئەو | **دەنێردرێت**<br><sub>denêrdirêt</sub> | **نێردرا**<br><sub>nêrdira</sub> |
| 1pl | ئێمە | **دەنێردرێین**<br><sub>denêrdirêyn</sub> | **نێردراین**<br><sub>nêrdirayn</sub> |
| 2pl | ئێوە | **دەنێردرێن**<br><sub>denêrdirên</sub> | **نێردران**<br><sub>nêrdiran</sub> |
| 3pl | ئەوان | **دەنێردرێن**<br><sub>denêrdirên</sub> | **نێردران**<br><sub>nêrdiran</sub> |
<!-- /gen -->

<!-- gen:verb verb=گوتن cells=passive_present,passive_past -->
*گوتن* (gutin) “to say” — present stem **ڵێ**, past stem **گوت**, transitive

| person | pronoun | Passive present | Passive past |
|---|---|---|---|
| 1sg | من | **دەگوترێم**<br><sub>degutrêm</sub> | **گوترام**<br><sub>gutram</sub> |
| 2sg | تۆ | **دەگوترێیت**<br><sub>degutrêyt</sub> | **گوترایت**<br><sub>gutrayt</sub> |
| 3sg | ئەو | **دەگوترێت**<br><sub>degutrêt</sub> | **گوترا**<br><sub>gutra</sub> |
| 1pl | ئێمە | **دەگوترێین**<br><sub>degutrêyn</sub> | **گوتراین**<br><sub>gutrayn</sub> |
| 2pl | ئێوە | **دەگوترێن**<br><sub>degutrên</sub> | **گوتران**<br><sub>gutran</sub> |
| 3pl | ئەوان | **دەگوترێن**<br><sub>degutrên</sub> | **گوتران**<br><sub>gutran</sub> |
<!-- /gen -->

## Participle and perfect

The passive participle is passive stem + **-او**: کراو *done*, نووسراو *written*. Add **-ە** for the perfect: **کراوە** *has been done*, **نووسراوە** *has been written*. The participle is also an adjective: دەرگای داخراو *the closed door*.

## The agent

Usually the passive leaves the doer unsaid. When needed: **لەلایەن … ەوە** *by*:

<!-- gen:sentences ipa=1
ئەم کتێبە بە کوردی نووسراوە. | This book has been written in Kurdish.
نامەکە دوێنێ نێردرا. | The letter was sent yesterday.
ئەمە چۆن دەکرێت؟ | How is this done?
بڕیارەکە لەلایەن حکومەتەوە درا. | The decision was made by the government.
-->
| # | Kurdish | Latin | IPA | English |
|---|---|---|---|---|
| 1 | ئەم کتێبە بە کوردی نووسراوە. | em kitêbe be kurdî nûsrawe. | /ʔæm k(ɯ)teːbæ bæ kuɾdiː nuːsɾaːwæ/ | This book has been written in Kurdish. |
| 2 | نامەکە دوێنێ نێردرا. | nameke dwênê nêrdira. | /naːmækæ dweːneː neːɾd(ɯ)ɾaː/ | The letter was sent yesterday. |
| 3 | ئەمە چۆن دەکرێت؟ | eme çon dekrêt? | /ʔæmæ tʃoːn dækɾeːt/ | How is this done? |
| 4 | بڕیارەکە لەلایەن حکومەتەوە درا. | birryareke lelayen ḧikumetewe dira. | /b(ɯ)rjaːɾækæ lælaːjæn ħ(ɯ)kumætæwæ d(ɯ)ɾaː/ | The decision was made by the government. |
<!-- /gen -->

## Summary

* Passive stem = present stem + **ر** (ر/ڕ-final stems + **در**).
* Present **دەکرێت**, past **کرا**, perfect **کراوە**, participle **کراو**.
* Agent: لەلایەن … ەوە.

<!-- nav:bottom -->
---
[← 18. The perfect tenses](18-perfect-tenses.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [20. Preverbs, -ەوە verbs and compound verbs →](20-preverbs-and-compound-verbs.md)
<!-- nav:bottom -->
