<!-- nav:top -->
[← 2. The alphabet](02-alphabet.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [4. Consonants and pronunciation →](04-consonants.md)
<!-- nav:top -->

# 3. Vowels and the hidden i

**Level:** 🟢 Beginner · lesson 3 of 23

**On this page:** [The vowel letters](#the-vowel-letters) · [و and ی have two jobs](#و-and-ی-have-two-jobs) · [The bizroke: the vowel you do not write](#the-bizroke-the-vowel-you-do-not-write) · [Long and short](#long-and-short) · [Practice](#practice) · [Summary](#summary)

## The vowel letters

Sorani has eight vowels. Six are written with their own letters, one is written with a double letter, and one is not written at all:

| letter | Latin | IPA | sounds like | example |
|---|---|---|---|---|
| **ا** | a | aː | *a* in *father*, long | باران *rain* |
| **ە** | e | æ | *a* in *cat* | ئەسپ *horse* |
| **ێ** | ê | eː | *ay* in *say*, without the glide | سێو *apple* |
| **ۆ** | o | oː | *o* in *more* | ڕۆژ *day* |
| **وو** | û | uː | *oo* in *food* | بوون *to be* |
| **و** | u | u / ʊ | *u* in *put* (between consonants) | کورد *Kurd* |
| **ی** | î | iː | *ee* in *see* (between consonants) | شیر *milk* |
| — | i | ɯ | a short, central *i* (the **bizroke**) | not written: من *min* “I” |

<!-- gen:words words=باران,ئەسپ,سێو,ڕۆژ,بوون,کورد,شیر -->
| Kurdish | Latin | IPA | syllables | meaning |
|---|---|---|---|---|
| **باران** | baran | /baːɾaːn/ | baː.ɾaːn | rain |
| **ئەسپ** | esp | /ʔæsp/ | ʔæsp | horse |
| **سێو** | sêw | /seːw/ | seːw | apple |
| **ڕۆژ** | roj | /roːʒ/ | roːʒ | day; sun |
| **بوون** | bûn | /buːn/ | buːn | to be, to become |
| **کورد** | kurd | /kuɾd/ | kuɾd | Kurd |
| **شیر** | şîr | /ʃiːɾ/ | ʃiːɾ | milk; lion |
<!-- /gen -->

## و and ی have two jobs

**و** and **ی** are vowels *or* consonants, depending on what is around them:

| position | و | ی |
|---|---|---|
| next to a vowel letter | consonant **w** — ئاو *aw* “water” | consonant **y** — پیاو *pyaw* “man” |
| between consonants or at the end after a consonant | vowel **u** — کورد *kurd* | vowel **î** — شیر *şîr* |
| doubled | long **û** — وو in بوون *bûn* | **î + y** where a vowel meets a glide — ماسییەکە *masîyeke* “the fish” |

zimankit's pronunciation engine applies exactly these rules (`skills_ckb/phonology_ipa.py`), so you can check any word:

<!-- gen:words words=ئاو,پیاو,چاو,خواردن,چای,ماسی,کوردی -->
| Kurdish | Latin | IPA | syllables | meaning |
|---|---|---|---|---|
| **ئاو** | aw | /ʔaːw/ | ʔaːw | water |
| **پیاو** | pyaw | /pjaːw/ | pjaːw | man |
| **چاو** | çaw | /tʃaːw/ | tʃaːw | eye |
| **خواردن** | xwardin | /xwaːɾd(ɯ)n/ | xwaːɾ.dɯn | to eat |
| **چای** | çay | /tʃaːj/ | tʃaːj | tea |
| **ماسی** | masî | /maːsiː/ | maː.siː | fish |
| **کوردی** | kurdî | /kuɾdiː/ | kuɾ.diː | Kurdish (language) |
<!-- /gen -->

Notice چای *tea* (*çay*): the final ی comes right after the vowel ا, so it is the consonant *y*. In ماسی *fish* (*masî*) it follows the consonant س, so it is the vowel *î*.

## The bizroke: the vowel you do not write

Sorani has a short vowel *i* (IPA ɯ) that is **never written**. Readers insert it automatically wherever two or three consonants would otherwise be hard to pronounce together:

| written | consonants | said | meaning |
|---|---|---|---|
| من | m-n | **min** | I |
| کتێب | k-t-ê-b | **kitêb** | book |
| بزن | b-z-n | **bizin** | goat |
| کردن | k-r-d-n | **kirdin** | to do |

The rule zimankit uses (and that native readers follow without thinking) is:

1. A syllable may start with **one consonant**, or a consonant + *w*/*y* (خوا *xwa*, پیا *pya*), and at the start of a word also *s/ş* + consonant (ستێرە *stêre*).
2. A syllable may end with one consonant, or a falling cluster such as *rd*, *nd*, *st*, *şk*.
3. Wherever this is impossible, insert *i*, building syllables from the **end** of the word.

In the IPA column the inserted vowel appears as `(ɯ)`, so you can see where it goes:

<!-- gen:words words=من,کتێب,بزن,کردن,مشک,کوردستان,هەڵبژاردن -->
| Kurdish | Latin | IPA | syllables | meaning |
|---|---|---|---|---|
| **من** | min | /m(ɯ)n/ | mɯn | I |
| **کتێب** | kitêb | /k(ɯ)teːb/ | kɯ.teːb | book |
| **بزن** | bizin | /b(ɯ)z(ɯ)n/ | bɯ.zɯn | goat |
| **کردن** | kirdin | /k(ɯ)ɾd(ɯ)n/ | kɯɾ.dɯn | to do, to make |
| **مشک** | mişk | /m(ɯ)ʃk/ | mɯʃk | mouse |
| **کوردستان** | kurdistan | /kuɾd(ɯ)staːn/ | kuɾ.dɯs.taːn | Kurdistan |
| **هەڵبژاردن** | hellbijardin | /hæɫb(ɯ)ʒaːɾd(ɯ)n/ | hæɫ.bɯ.ʒaːɾ.dɯn | to elect, to choose; election |
<!-- /gen -->

## Long and short

Vowel length changes meaning, so hold the long vowels (ا ێ ۆ وو ی) a little longer than ە, و (u) and the hidden *i*:

<!-- gen:words words=کەر,کار,شیر,شەر -->
| Kurdish | Latin | IPA | syllables | meaning |
|---|---|---|---|---|
| **کەر** | ker | /kæɾ/ | kæɾ | donkey |
| **کار** | kar | /kaːɾ/ | kaːɾ | work, job |
| **شیر** | şîr | /ʃiːɾ/ | ʃiːɾ | milk; lion |
| **شەر** | şer | /ʃæɾ/ | ʃæɾ | war, fight |
<!-- /gen -->

## Practice

1. Is the ی in **پیاو** a vowel or a consonant? And in **شیر**?
2. Where does the hidden *i* go in **بزن** and **کردن**?
3. Pronounce: ئاو، سێو، ڕۆژ، بوون، کورد.

<details><summary>Answers</summary>

1. پیاو: consonant *y* (before the vowel ا) → *pyaw*. شیر: vowel *î* (between ش and ر) → *şîr*.
2. *bizin* (b-i-z-i-n), *kirdin* (k-i-r-d-i-n).
3. *aw, sêw, roj, bûn, kurd*.

</details>

## Summary

* Written vowels: ا ە ێ ۆ وو, plus و (u) and ی (î) between consonants.
* و and ی are *w* and *y* next to a vowel letter.
* The short *i* (bizroke) is never written; insert it to break up impossible consonant clusters, working from the end of the word.

<!-- nav:bottom -->
---
[← 2. The alphabet](02-alphabet.md) · [⌂ Central Kurdish (Sorani) course](../README.md) · [4. Consonants and pronunciation →](04-consonants.md)
<!-- nav:bottom -->
