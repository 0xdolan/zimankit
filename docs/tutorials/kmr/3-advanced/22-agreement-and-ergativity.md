<!-- nav:top -->
[← 21. Irregular and special verbs](21-irregular-verbs.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [23. The written standard and common errors →](23-spelling-and-common-errors.md)
<!-- nav:top -->

# 22. Agreement and ergativity in depth

**Level:** 🔴 Advanced · lesson 22 of 23

**On this page:** [The complete rule](#the-complete-rule) · [Agreement with plural objects](#agreement-with-plural-objects) · [Pro-drop](#pro-drop) · [The checker on correct and wrong sentences](#the-checker-on-correct-and-wrong-sentences) · [Ezafe agreement](#ezafe-agreement) · [Summary](#summary)

Split ergativity is the hardest part of Kurmanji, for learners and for software alike. This lesson collects all the rules and tests them against zimankit's ergativity checker.

## The complete rule

| clause | agent / subject | object | verb agrees with |
|---|---|---|---|
| present-stem tense (present, subjunctive, future, imperative), any verb | **direct** | **oblique** | agent / subject |
| past-stem tense, **intransitive** verb | **direct** | — | subject |
| past-stem tense, **transitive** verb | **oblique** | **direct** | **object** |
| passive (hatin + infinitive) | — | direct (as subject) | that subject |

Past-stem tenses are the simple past, past progressive, present perfect and past perfect.

## Agreement with plural objects

Because the verb agrees with the object in ergative clauses, a plural object needs a plural verb, even though a direct plural noun has **no plural ending**:

<!-- gen:sentences
Min sêv xwar. | I ate the apple.
Min sêv xwarin. | I ate the apples.
Wî heval dîtin. | He saw the friends.
-->
| # | Kurdish | Arabic script | English |
|---|---|---|---|
| 1 | Min sêv xwar. | من سێڤ خوار. | I ate the apple. |
| 2 | Min sêv xwarin. | من سێڤ خوارن. | I ate the apples. |
| 3 | Wî heval dîtin. | وی هەڤال دیتن. | He saw the friends. |
<!-- /gen -->

Only the verb tells you whether *sêv* is one apple or several.

## Pro-drop

The agent is often left out when it is clear from context: *Te çi kir?* “What did you do?” → *Min tiştek nekir.* “I didn't do anything.” → *Nekir.* “(I) didn't.” A checker must accept clauses without an overt agent.

## The checker on correct and wrong sentences

<!-- gen:ergativity
Ez nan dixwim. | I eat bread.
Min nan xwar. | I ate bread.
Te ez dîtim. | You saw me.
Wan em dîtin. | They saw us.
Ez hatim. | I came.
Ez nan xwar. | (wrong) direct agent
Min tu dîtim. | (wrong) agreement with the agent
Min hatim. | (wrong) oblique subject of an intransitive verb
Min sêv xwarin. | I ate the apples. (correct)
Jinê nan çêkir. | The woman made bread. (correct)
-->
| sentence | English | alignment | agent | object | verb agrees with | check |
|---|---|---|---|---|---|---|
| *Ez nan dixwim.* | I eat bread. | accusative | Ez (dir) | — | subject (1sg) | ✔ |
| *Min nan xwar.* | I ate bread. | ergative | Min (obl) | nan (dir) | object (3sg) | ✔ |
| *Te ez dîtim.* | You saw me. | ergative | Te (obl) | ez (dir) | object (1sg) | ✔ |
| *Wan em dîtin.* | They saw us. | ergative | Wan (obl) | em (dir) | object (pl) | ✔ |
| *Ez hatim.* | I came. | accusative | Ez (dir) | — | subject (1sg) | ✔ |
| *Ez nan xwar.* | (wrong) direct agent | ergative | — | Ez (dir) | object (3sg) | ✘ ergative clause without an overt oblique agent (pro-drop); verb ending marks 3sg but object 'Ez' is 1sg |
| *Min tu dîtim.* | (wrong) agreement with the agent | ergative | Min (obl) | tu (dir) | object (1sg) | ✘ verb ending marks 1sg but object 'tu' is 2sg |
| *Min hatim.* | (wrong) oblique subject of an intransitive verb | accusative | — | — | subject (1sg) | ✘ subject not overt; verb ending marks 1sg |
| *Min sêv xwarin.* | I ate the apples. (correct) | ergative | Min (obl) | sêv (dir) | object (pl) | ✘ verb ending marks pl but object 'sêv' is 3sg |
| *Jinê nan çêkir.* | The woman made bread. (correct) | ergative | — | Jinê (dir) | object (3sg) | ✔ |
<!-- /gen -->

Read the last rows critically, because they show where the current checker is still weak:

* **Min hatim** is rightly flagged, but only because no subject is found; the message should say “the subject of an intransitive verb is direct: *ez hatim*”.
* **Min sêv xwarin** is correct (*apples*, plural), but a bare noun looks singular, so the checker reports a false mismatch. A real grammar checker must treat a bare direct noun as *singular or plural*.
* **Jinê nan çêkir** gets a ✔ for the wrong reason. Without a lexicon the checker cannot know that *jin* is feminine, so it takes *jinê* as a direct object and assumes the agent was dropped. With the gender lexicon from the wordlist pipeline, *jinê* would be read correctly as the oblique agent.

All three are concrete tasks for the grammar-checker project.

## Ezafe agreement

The ezafe must match the gender and number of the noun it follows:

| wrong | right | why |
|---|---|---|
| \* malê bavê min | mala bavê min | *mal* is feminine → -a |
| \* bava min | bavê min | *bav* is masculine → -ê |
| \* hevala min (for several friends) | hevalên min | plural → -ên |

## Summary

* Present: accusative. Past transitive: ergative (oblique agent, direct object, agreement with the object). Past intransitive and passive: subject agreement.
* Bare direct nouns can be plural; the verb shows it.
* Ezafe agrees in gender and number.

<!-- nav:bottom -->
---
[← 21. Irregular and special verbs](21-irregular-verbs.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [23. The written standard and common errors →](23-spelling-and-common-errors.md)
<!-- nav:bottom -->
