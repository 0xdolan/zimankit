<!-- nav:top -->
[← 21. Irregular and special verbs](21-irregular-verbs.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [23. The written standard and common errors →](23-spelling-and-common-errors.md)
<!-- nav:top -->

# 22. Clitic placement and ergative syntax in depth

**Level:** 🔴 Advanced · lesson 22 of 23

**On this page:** [Five jobs of the clitics](#five-jobs-of-the-clitics) · [The hosting rule](#the-hosting-rule) · [Present tense: the object clitic](#present-tense-the-object-clitic) · [Checking agreement](#checking-agreement) · [Summary](#summary)

The personal clitics (م ت ی مان تان یان) are the heart of Sorani syntax. This lesson collects every rule about where they go and what they mean.

## Five jobs of the clitics

| job | tense | example | meaning |
|---|---|---|---|
| **possessor** | any | کتێبە**کەم** | my book |
| **agent** (doer) | past of transitive verbs | نان**م** خوارد | I ate bread |
| **object** | present of transitive verbs | دە**ی**بینم | I see him/her |
| **object** | past, beside the agent | گرت**م**ی | he caught me |
| **complement** (to, from, with me) | any, on an adposition | بۆ**م** هێنا | he brought it to me |

The set-1 **endings** (present م یت ێت/ات ین ن ن; past م یت – ین ن ن) do the opposite job in each tense. Kurdish school books number these differently: کۆمەڵەی یەکەم is م ت ی مان تان یان, دووەم the past endings, سێیەم the present endings and چوارەم the imperative ە ن.

| tense | agent (doer) marked by | object marked by |
|---|---|---|
| present (دەبینم) | set-1 **ending** | **clitic** |
| past (بینیم) | **clitic** | set-1 **ending** |

This role reversal is Sorani ergativity in a nutshell:

<!-- gen:sentences ipa=1
دەتبینم. | I see you. (ت = you object, م = I subject)
دەمبینیت. | You see me.
بینیمیت. | I saw you. (م = I agent, یت = you object)
بینیتم. | You saw me.
-->
| # | Kurdish | Latin | IPA | English |
|---|---|---|---|---|
| 1 | دەتبینم. | detbînim. | /dætbiːn(ɯ)m/ | I see you. (ت = you object, م = I subject) |
| 2 | دەمبینیت. | dembînît. | /dæmbiːniːt/ | You see me. |
| 3 | بینیمیت. | bînîmît. | /biːniːmiːt/ | I saw you. (م = I agent, یت = you object) |
| 4 | بینیتم. | bînîtim. | /biːniːt(ɯ)m/ | You saw me. |
<!-- /gen -->

## The hosting rule

A clitic attaches to the **first element of the verb phrase** that can host it. In order of priority:

1. the **object**, whatever the verb: **نانم** خوارد;
2. with no object, a **preverb** or the noun part of a compound verb: **هەڵم** گرت, **دەستم** پێ کرد;
3. on a simple verb, the negation **نە**: **نەم**خوارد;
4. on a simple verb, the aspect prefix **دە**: **دەم**خوارد *I was eating*;
5. inside the perfect: خواردوو**مە**;
6. otherwise the end of the verb: **خواردم**.

A clitic on an adposition is the agent only if there is no object and no other clitic: **لێم** پرسی *I asked him*. In **نامەکەی بۆم هێنا**, ی is the agent and م means *to me*, and **بۆمی هێنا** keeps both on بۆ.

With a third person agent, an object clitic comes first: **گرتمی** *he caught me*. With a first or second person agent, the object ending comes last: **بینیمیت** *I saw you*. Up to three clitics can appear together (بۆتی دەنێرم).

Only one agent clitic appears in the verb phrase. A subject pronoun can precede everything for emphasis: **من** نانم خوارد.

## Present tense: the object clitic

In the present, a pronoun object is usually a clitic placed after دە / نا (or the preverb): **دە**ی**بینم** *I see him*, **نا**ت**ناسم** *I don't know you*, **هەڵ**ی**دەگرم** *I pick it up*.

<!-- gen:sentences
کتێبەکە دەخوێنم. | I read the book. (object is a noun → no clitic)
دەیخوێنم. | I read it.
نایناسم. | I don't know him.
هەڵیدەگرم. | I pick it up.
-->
| # | Kurdish | Latin | English |
|---|---|---|---|
| 1 | کتێبەکە دەخوێنم. | kitêbeke dexwênim. | I read the book. (object is a noun → no clitic) |
| 2 | دەیخوێنم. | deyxwênim. | I read it. |
| 3 | نایناسم. | naynasim. | I don't know him. |
| 4 | هەڵیدەگرم. | hellîdegrim. | I pick it up. |
<!-- /gen -->

## Checking agreement

The ergative pattern is where most writing mistakes happen, so it is the first thing a grammar checker for Sorani must verify:

| sentence | correct? | why |
|---|---|---|
| من نانم خوارد. | ✔ | agent clitic on the object |
| \* من نان خواردم. | ✘ (standard) | clitic on the verb although an object precedes it |
| \* ئەوان هاتیان. | ✘ | هاتن is intransitive: هاتن *they came* |
| \* من دەمخوارد نان. | ✘ | the object must precede the verb |

zimankit's sentence parser warns about the first two kinds of mistake in its `notes`: a past transitive verb with no agent, and a clitic on an intransitive verb.

## Summary

* Clitics = possessor, past agent, present object, past object, adposition complement; endings = present subject, past object.
* The clitic goes on the object; failing that, on the first part of the verb, and on a simple verb after نە or دە, inside the perfect, or at the end.
* Intransitive verbs never take an agent clitic.

<!-- nav:bottom -->
---
[← 21. Irregular and special verbs](21-irregular-verbs.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [23. The written standard and common errors →](23-spelling-and-common-errors.md)
<!-- nav:bottom -->
