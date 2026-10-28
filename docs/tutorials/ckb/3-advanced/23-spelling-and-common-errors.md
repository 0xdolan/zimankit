<!-- nav:top -->
[← 22. Clitic placement and ergative syntax in depth](22-clitic-placement.md) · [⌂ Central Kurdish (Sorani) course](../README.md)
<!-- nav:top -->

# 23. The written standard and common errors

**Level:** 🔴 Advanced · lesson 23 of 23

**On this page:** [1. Use Kurdish letters, not Arabic or Persian ones](#1-use-kurdish-letters-not-arabic-or-persian-ones) · [2. Don't drop the marks](#2-dont-drop-the-marks) · [3. Initial vowels need ئ](#3-initial-vowels-need-ئ) · [4. Old encodings](#4-old-encodings) · [5. Words the validator rejects](#5-words-the-validator-rejects) · [6. Real words in the wrong spelling](#6-real-words-in-the-wrong-spelling) · [7. Grammar errors to watch](#7-grammar-errors-to-watch) · [Summary](#summary)

You can now read and write Sorani grammatically. This lesson covers what separates a correct text from a merely understandable one: the spelling standard, and the mistakes that native writers and machines make most. Every rule here is implemented in zimankit (`skills_ckb/orthography.py`), so this lesson is also the specification of a future grammar checker.

## 1. Use Kurdish letters, not Arabic or Persian ones

Keyboards often produce look-alike characters from other languages. They look the same but break searching, sorting and spell-checking:

| wrong (Arabic/Persian code point) | right (Kurdish) |
|---|---|
| ك | **ک** |
| ي ى | **ی** |
| ة | **ە** |
| ه used as a vowel | **ە** |
| ھ | **ه** |

## 2. Don't drop the marks

ڕ ڵ ێ ۆ are distinct letters. Writing ر ل ی و instead changes the word: گول is not گوڵ *flower*, بەلام is not بەڵام *but*.

## 3. Initial vowels need ئ

A word never starts with a bare vowel: ئاو, ئێمە, ئەو, never او or ێمە.

## 4. Old encodings

Older websites and documents typed ە as ه + ZWNJ and used Arabic digits and punctuation. The normaliser converts all of this:

<!-- gen:normalize
به‌ڕێوه‌به‌ر | legacy ه + ZWNJ for ە
كتێبەكە | Arabic kāf
ئەو رۆژە | initial ر should be ڕ
ساڵی 2015 | Latin digits
گول | missing ڵ: a possible word shape, so not flagged here (see section 6)
-->
| typed text | after `normalize()` | problems still found by `validate_word()` | note |
|---|---|---|---|
| به‌ڕێوه‌به‌ر | بەڕێوەبەر | — | legacy ه + ZWNJ for ە |
| كتێبەكە | کتێبەکە | — | Arabic kāf |
| ئەو رۆژە | ئەو ڕۆژە | — | initial ر should be ڕ |
| ساڵی 2015 | ساڵی ٢٠١٥ | — | Latin digits |
| گول | گول | — | missing ڵ: a possible word shape, so not flagged here (see section 6) |
<!-- /gen -->

## 5. Words the validator rejects

`validate_word()` reports spellings that cannot be standard Sorani:

<!-- gen:normalize
ثەورە | Arabic-only letter ث
اسپ | initial vowel without ئ
ذکر | Arabic-only letter ذ
-->
| typed text | after `normalize()` | problems still found by `validate_word()` | note |
|---|---|---|---|
| ثەورە | ثەورە | ثەورە: arabic-only letter; non-Kurdish character(s): U+062B | Arabic-only letter ث |
| اسپ | ئاسپ | — | initial vowel without ئ |
| ذکر | ذکر | ذکر: arabic-only letter; non-Kurdish character(s): U+0630 | Arabic-only letter ذ |
<!-- /gen -->

## 6. Real words in the wrong spelling

Some errors produce a string that *could* be a word. گول is a possible letter sequence, so a validator cannot reject it; only a **lexicon** can tell you that گوڵ *flower* is the word meant. zimankit generates the confusable variants of a word (`spelling_variants`: ر/ڕ ل/ڵ ی/ێ و/ۆ و/وو ه/ە, ZWNJ), and the wordlist pipeline maps a rare spelling to a variant that is at least five times more frequent in the corpus. 24 924 such pairs were learned from real text. The most frequent:

| non-standard | standard | seen | standard seen |
|---|---|---|---|
| وێستگه | وێستگە *station* | 6 748 | 55 860 |
| سێشەممه | سێشەممە *Tuesday* | 1 409 | 7 681 |
| ڕای‌گەیاند | ڕایگەیاند *he announced* | 295 | 79 327 |
| دیناره | دینارە *it is a dinar* | 234 | 13 721 |
| نێردراوه | نێردراوە *has been sent* | 209 | 3 322 |

Most are the legacy ه-for-ە problem of section 4 on words the normaliser could not safely fix on its own. ڕای‌گەیاند shows a ZWNJ inserted after the preverb clitic (lesson 20).

## 7. Grammar errors to watch

These need context, not just spelling. They are the targets of the planned grammar checker:

| error | example | correct | lesson |
|---|---|---|---|
| agent clitic missing in the past | \* من نان خوارد | من نانم خوارد | 14 |
| agent clitic on an intransitive verb | \* هاتمان | هاتین | 13 |
| wrong allomorph after a vowel | \* دەرگاەکە | دەرگاکە | 7 |
| plural noun after a number | \* سێ پیاوان | سێ پیاو | 7 |
| ezafe missing between noun and adjective | \* پیاو باش | پیاوی باش | 9 |
| definite + adjective order | \* پیاوەکە باش (as a phrase) | پیاوە باشەکە | 9 |

## Summary

* Use Kurdish code points; keep the marks on ڕ ڵ ێ ۆ; start vowels with ئ.
* zimankit normalises legacy text and flags impossible spellings.
* Lexicon-based variant mapping catches real-word misspellings.
* Agreement and ezafe errors need context and are the next step: a grammar checker.

**Congratulations, you have finished the Sorani course.** The [reference pages](../README.md#reference) have every verb and noun of the course in full.

<!-- nav:bottom -->
---
[← 22. Clitic placement and ergative syntax in depth](22-clitic-placement.md) · [⌂ Central Kurdish (Sorani) course](../README.md)
<!-- nav:bottom -->
