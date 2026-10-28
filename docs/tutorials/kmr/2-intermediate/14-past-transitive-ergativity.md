<!-- nav:top -->
[← 13. The past tense I: intransitive verbs](13-past-intransitive.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [15. Was doing, used to do: the past progressive →](15-past-progressive.md)
<!-- nav:top -->

# 14. The past tense II: transitive verbs and split ergativity

**Level:** 🟡 Intermediate · lesson 14 of 23

**On this page:** [The big switch](#the-big-switch) · [Paradigms](#paradigms) · [Checking it with zimankit](#checking-it-with-zimankit) · [Practice](#practice) · [Summary](#summary)

## The big switch

Compare the present and the past of *to see*:

<!-- gen:sentences ipa=1
Ez te dibînim. | I see you.
Min tu dîtî. | I saw you.
-->
| # | Kurdish | Arabic script | IPA | English |
|---|---|---|---|---|
| 1 | Ez te dibînim. | ئەز تە دبینم. | /ɛz tɛ dɪbiːnɯm/ | I see you. |
| 2 | Min tu dîtî. | من تو دیتی. | /mɪn tʊ diːtiː/ | I saw you. |
<!-- /gen -->

Everything has swapped:

| | present *I see you* | past *I saw you* |
|---|---|---|
| the doer *I* | **ez** (direct) | **min** (oblique) |
| the object *you* | **te** (oblique) | **tu** (direct) |
| the verb agrees with | the doer: dibîn**im** (1sg) | the **object**: dît**î** (2sg) |

This is **split ergativity**. In the **present**, Kurmanji works like English (*accusative*); in the **past tenses of transitive verbs** it is **ergative**:

1. the **doer** (agent) is **oblique**;
2. the **object** is **direct**;
3. the verb **agrees with the object**.

Intransitive verbs are never ergative: *ez hatim* “I came” (lesson 13).

## Paradigms

In the tables below the person column is the **object**, because that is what the verb agrees with. Any oblique agent can go with any form:

<!-- gen:verb verb=dîtin cells=past,past_neg -->
*dîtin* (دیتن) “to see, to find” — present stem **bîn**, past stem **dît**, transitive

| person | agent (oblique) | object (direct) | Simple past | Past negative |
|---|---|---|---|---|
| 1sg | min | ez | **dîtim**<br><sub>دیتم</sub> | **nedîtim**<br><sub>نەدیتم</sub> |
| 2sg | te | tu | **dîtî**<br><sub>دیتی</sub> | **nedîtî**<br><sub>نەدیتی</sub> |
| 3sg | wî / wê | ew | **dît**<br><sub>دیت</sub> | **nedît**<br><sub>نەدیت</sub> |
| 1pl | me | em | **dîtin**<br><sub>دیتن</sub> | **nedîtin**<br><sub>نەدیتن</sub> |
| 2pl | we | hûn | **dîtin**<br><sub>دیتن</sub> | **nedîtin**<br><sub>نەدیتن</sub> |
| 3pl | wan | ew | **dîtin**<br><sub>دیتن</sub> | **nedîtin**<br><sub>نەدیتن</sub> |

> Past tenses of a transitive verb are **ergative**: the agent is oblique and the verb agrees with the **object** (the *object* column), e.g. *min tu dîtî* “I saw you”.
<!-- /gen -->

So *dîtim* means “(someone) saw **me**”, and *dîtin* means “(someone) saw **them**”.

With a 3rd-person or noun object, which is very common, the verb is simply 3sg or plural:

<!-- gen:sentences ipa=1
Min nan xwar. | I ate bread.
Te nan xwar. | You ate bread.
Wê pirtûk xwend. | She read the book.
Me ew dîtin. | We saw them.
Wan ez dîtim. | They saw me.
Jinê nan çêkir. | The woman made bread.
-->
| # | Kurdish | Arabic script | IPA | English |
|---|---|---|---|---|
| 1 | Min nan xwar. | من نان خوار. | /mɪn naːn xʷaːɾ/ | I ate bread. |
| 2 | Te nan xwar. | تە نان خوار. | /tɛ naːn xʷaːɾ/ | You ate bread. |
| 3 | Wê pirtûk xwend. | وێ پرتووک خوەند. | /weː pɪɾtuːk xʷɛnd/ | She read the book. |
| 4 | Me ew dîtin. | مە ئەو دیتن. | /mɛ ɛw diːtɯn/ | We saw them. |
| 5 | Wan ez dîtim. | وان ئەز دیتم. | /waːn ɛz diːtɯm/ | They saw me. |
| 6 | Jinê nan çêkir. | ژنێ نان چێکر. | /ʒɪneː naːn tʃeːkɯɾ/ | The woman made bread. |
<!-- /gen -->

In *Jinê nan çêkir*, the noun agent *jin* takes the feminine oblique ending **-ê** (lesson 9).

## Checking it with zimankit

zimankit's `detect_alignment()` finds the verb, decides whether the clause is ergative, classifies each argument by case and checks the agreement. This is the core of a Kurmanji grammar checker:

<!-- gen:ergativity
Ez te dibînim. | I see you.
Min tu dîtî. | I saw you.
Min ew dîtin. | I saw them.
Wan ez dîtim. | They saw me.
Min tu dîtim. | (wrong) *I saw you
Ez tu dîtî. | (wrong) *I saw you
-->
| sentence | English | alignment | agent | object | verb agrees with | check |
|---|---|---|---|---|---|---|
| *Ez te dibînim.* | I see you. | accusative | Ez (dir) | te (obl) | subject (1sg) | ✔ |
| *Min tu dîtî.* | I saw you. | ergative | Min (obl) | tu (dir) | object (2sg) | ✔ |
| *Min ew dîtin.* | I saw them. | ergative | Min (obl) | ew (dir) | object (pl) | ✔ |
| *Wan ez dîtim.* | They saw me. | ergative | Wan (obl) | ez (dir) | object (1sg) | ✔ |
| *Min tu dîtim.* | (wrong) *I saw you | ergative | Min (obl) | tu (dir) | object (1sg) | ✘ verb ending marks 1sg but object 'tu' is 2sg |
| *Ez tu dîtî.* | (wrong) *I saw you | ergative | — | Ez (dir) | object (2sg) | ✘ ergative clause without an overt oblique agent (pro-drop); verb ending marks 2sg but object 'Ez' is 1sg |
<!-- /gen -->

The last two are classic learner errors: putting the agreement on the agent (*dîtim* for *min*), and using the direct pronoun for the agent (*ez*). The checker flags both. Its explanation of the second one is not ideal yet: it takes *ez* for the object because it is direct, and then reports a person mismatch. A better message (“the agent of a past transitive verb must be oblique: *min*”) is one of the things a full grammar checker should add. Lesson 22 shows more cases, including where the checker still goes wrong.

## Practice

1. *She saw me.*
2. *I ate the apples* (*sêv*).
3. *You (pl) read the book* (past).

<details><summary>Answers</summary>

1. Wê ez dîtim.
2. Min sêv xwarin. (plural object → plural verb)
3. We pirtûk xwend.

</details>

## Summary

* Present: agent direct, object oblique, verb agrees with the agent.
* Past, transitive: **agent oblique, object direct, verb agrees with the object**.
* Past, intransitive: subject direct, verb agrees with it.

<!-- nav:bottom -->
---
[← 13. The past tense I: intransitive verbs](13-past-intransitive.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [15. Was doing, used to do: the past progressive →](15-past-progressive.md)
<!-- nav:bottom -->
