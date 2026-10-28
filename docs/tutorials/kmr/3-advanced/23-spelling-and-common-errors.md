<!-- nav:top -->
[← 22. Agreement and ergativity in depth](22-agreement-and-ergativity.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md)
<!-- nav:top -->

# 23. The written standard and common errors

**Level:** 🔴 Advanced · lesson 23 of 23

**On this page:** [1. Turkish and other foreign letters](#1-turkish-and-other-foreign-letters) · [2. What the normaliser fixes](#2-what-the-normaliser-fixes) · [3. What the validator rejects](#3-what-the-validator-rejects) · [4. Real words, wrong place](#4-real-words-wrong-place) · [Summary](#summary)

This last lesson is about writing Kurmanji correctly: the spelling problems that appear in real texts, how zimankit repairs or flags them (`skills_kmr/orthography.py`), and the grammar errors a checker must catch.

## 1. Turkish and other foreign letters

Most Kurmanji writers also type Turkish, and Turkish keyboards produce letters that do not belong to the Hawar alphabet:

| wrong | right | note |
|---|---|---|
| ı (dotless i) | **i** | |
| İ (dotted capital I) | **I** | |
| é, è, ë | **ê** | the circumflex is the only Kurmanji accent |
| í, ï | **î** | |
| ú, ü | **û** | ü is a Turkish letter |
| ș (Romanian) | **ş** | looks identical |
| ğ, ö | — | not Kurmanji: usually a Turkish name |

## 2. What the normaliser fixes

<!-- gen:normalize
Kürdistan | Turkish ü for û
şéwe | acute é for ê
İro baran dibare. | Turkish dotted İ
Ez dıçım malê. | Turkish dotless ı
Ew’ê hat. | curly apostrophe
-->
| typed text | after `normalize()` | problems still found by `validate_word()` | note |
|---|---|---|---|
| Kürdistan | Kûrdistan | — | Turkish ü for û |
| şéwe | şêwe | — | acute é for ê |
| İro baran dibare. | Iro baran dibare. | — | Turkish dotted İ |
| Ez dıçım malê. | Ez diçim malê. | — | Turkish dotless ı |
| Ew’ê hat. | Ew'ê hat. | — | curly apostrophe |
<!-- /gen -->

## 3. What the validator rejects

Some words cannot be standard Kurmanji at all, usually Turkish names or typing errors. The validator reports them; the wordlist pipeline keeps frequent capitalised ones as proper nouns:

<!-- gen:normalize
Erdoğan | ğ is not a Kurmanji letter
Göktürk | ö, ü
kurrrd | three r in a row
-->
| typed text | after `normalize()` | problems still found by `validate_word()` | note |
|---|---|---|---|
| Erdoğan | Erdoğan | Erdoğan: foreign letter(s): ğ; non-Hawar character(s): ğ | ğ is not a Kurmanji letter |
| Göktürk | Göktûrk | Göktûrk: foreign letter(s): ö; non-Hawar character(s): ö | ö, ü |
| kurrrd | kurrrd | kurrrd: tripled letter; four consonants in a row | three r in a row |
<!-- /gen -->

## 4. Real words, wrong place

Some mistakes produce valid words. Only grammar can catch them:

| error | wrong | right | lesson |
|---|---|---|---|
| wrong ezafe gender | \* bava min | bavê min | 8 |
| direct case after a preposition | \* li mal | li malê | 9, 16 |
| direct agent in the past | \* ez nan xwar | min nan xwar | 14 |
| oblique object in the past | \* min wê dît (meaning *her*) | min ew dît | 14 |
| verb agrees with the agent in the past | \* min tu dîtim | min tu dîtî | 14 |
| oblique subject of an intransitive verb | \* min hatim | ez hatim | 13 |
| bi- kept after a preverb | \* birabe | rabe | 20 |
| na- instead of ni- | \* nazanim | nizanim | 21 |

The third, fifth and sixth are checked by zimankit's `detect_alignment` (lessons 14 and 22). The others need the case and gender information the analyzer already provides. Combining them is the plan for a full Kurmanji grammar checker.

## Summary

* Use only Hawar letters: ê î û ş ç, never Turkish ı İ ğ ö ü or accented é í ú.
* zimankit normalises the common confusions and rejects impossible spellings.
* Grammar errors (case, ezafe gender, ergative agreement) need context: the next step is a grammar checker.

**Congratulations, you have finished the Kurmanji course.** The [reference pages](../README.md#reference) have every verb and noun of the course in full.

<!-- nav:bottom -->
---
[← 22. Agreement and ergativity in depth](22-agreement-and-ergativity.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md)
<!-- nav:bottom -->
