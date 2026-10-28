<!-- nav:top -->
[← 8. Ezafe: linking nouns to adjectives and owners](08-ezafe.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [10. The present tense →](10-present-tense.md)
<!-- nav:top -->

# 9. Direct and oblique case

**Level:** 🟢 Beginner · lesson 9 of 23

**On this page:** [Two cases](#two-cases) · [Oblique endings](#oblique-endings) · [Full declension](#full-declension) · [In sentences](#in-sentences) · [Practice](#practice) · [Summary](#summary)

## Two cases

Kurmanji nouns have two main **cases**:

* **direct**: the plain form, for the subject of most sentences and for the object of past transitive verbs;
* **oblique**: a form with an ending, for everything else:
  1. after **prepositions**: *li **malê*** “at home”;
  2. the **object** of a present-tense verb: *Ez **pirtûkê** dixwînim* “I read the book”;
  3. the **owner** after an ezafe: *mala **bavî*** “the father's house”;
  4. the **doer** of a past transitive verb (lesson 14): ***Jinê*** nan xwar “the woman ate bread”.

## Oblique endings

| | after a consonant | after a vowel |
|---|---|---|
| feminine singular | **-ê** | **-yê** |
| masculine singular | **-î** (often dropped) | nothing |
| plural | **-an** | **-yan** |
| indefinite f / m | **-ekê / -ekî** | -yekê / -yekî |

The masculine *-î* is optional in most dialects (*ji bavî* or *ji bav* “from the father”), but it regularly appears after a demonstrative: *vî bajarî* “this city” (lesson 11). The feminine *-ê* is never dropped.

## Full declension

Here is everything zimankit's `decline()` generates for seven consonant-final nouns. Vocative forms (*keçê!* “girl!”, *kuro!* “boy!”) are used to address someone:

<!-- gen:noun nouns=jin,mal,keç,pirtûk,bav,mirov,bajar cells=def.dir.sg,def.obl.sg,def.ez.sg,ind.dir.sg,ind.obl.sg,def.obl.pl,def.ez.pl,voc.sg -->
| noun | meaning | gender | direct sg | oblique sg | ezafe sg | indef. direct | indef. oblique | oblique pl | ezafe pl | vocative sg |
|---|---|---|---|---|---|---|---|---|---|---|
| **jin** | woman; wife | f | **jin**<br><sub>ژن</sub> | **jinê**<br><sub>ژنێ</sub> | **jina**<br><sub>ژنا</sub> | **jinek**<br><sub>ژنەک</sub> | **jinekê**<br><sub>ژنەکێ</sub> | **jinan**<br><sub>ژنان</sub> | **jinên**<br><sub>ژنێن</sub> | **jinê**<br><sub>ژنێ</sub> |
| **mal** | house, home | f | **mal**<br><sub>مال</sub> | **malê**<br><sub>مالێ</sub> | **mala**<br><sub>مالا</sub> | **malek**<br><sub>مالەک</sub> | **malekê**<br><sub>مالەکێ</sub> | **malan**<br><sub>مالان</sub> | **malên**<br><sub>مالێن</sub> | **malê**<br><sub>مالێ</sub> |
| **keç** | girl; daughter | f | **keç**<br><sub>کەچ</sub> | **keçê**<br><sub>کەچێ</sub> | **keça**<br><sub>کەچا</sub> | **keçek**<br><sub>کەچەک</sub> | **keçekê**<br><sub>کەچەکێ</sub> | **keçan**<br><sub>کەچان</sub> | **keçên**<br><sub>کەچێن</sub> | **keçê**<br><sub>کەچێ</sub> |
| **pirtûk** | book | f | **pirtûk**<br><sub>پرتووک</sub> | **pirtûkê**<br><sub>پرتووکێ</sub> | **pirtûka**<br><sub>پرتووکا</sub> | **pirtûkek**<br><sub>پرتووکەک</sub> | **pirtûkekê**<br><sub>پرتووکەکێ</sub> | **pirtûkan**<br><sub>پرتووکان</sub> | **pirtûkên**<br><sub>پرتووکێن</sub> | **pirtûkê**<br><sub>پرتووکێ</sub> |
| **bav** | father | m | **bav**<br><sub>باڤ</sub> | **bavî**<br><sub>باڤی</sub> | **bavê**<br><sub>باڤێ</sub> | **bavek**<br><sub>باڤەک</sub> | **bavekî**<br><sub>باڤەکی</sub> | **bavan**<br><sub>باڤان</sub> | **bavên**<br><sub>باڤێن</sub> | **bavo**<br><sub>باڤۆ</sub> |
| **mirov** | person, human, man | m | **mirov**<br><sub>مرۆڤ</sub> | **mirovî**<br><sub>مرۆڤی</sub> | **mirovê**<br><sub>مرۆڤێ</sub> | **mirovek**<br><sub>مرۆڤەک</sub> | **mirovekî**<br><sub>مرۆڤەکی</sub> | **mirovan**<br><sub>مرۆڤان</sub> | **mirovên**<br><sub>مرۆڤێن</sub> | **mirovo**<br><sub>مرۆڤۆ</sub> |
| **bajar** | city | m | **bajar**<br><sub>باژار</sub> | **bajarî**<br><sub>باژاری</sub> | **bajarê**<br><sub>باژارێ</sub> | **bajarek**<br><sub>باژارەک</sub> | **bajarekî**<br><sub>باژارەکی</sub> | **bajaran**<br><sub>باژاران</sub> | **bajarên**<br><sub>باژارێن</sub> | **bajaro**<br><sub>باژارۆ</sub> |
<!-- /gen -->

Vowel-final nouns:

<!-- gen:noun nouns=xanî,çiya cells=def.dir.sg,def.obl.sg,def.ez.sg,ind.dir.sg,ind.obl.sg,def.obl.pl,def.ez.pl -->
| noun | meaning | gender | direct sg | oblique sg | ezafe sg | indef. direct | indef. oblique | oblique pl | ezafe pl |
|---|---|---|---|---|---|---|---|---|---|
| **xanî** | house (building) | m | **xanî**<br><sub>خانی</sub> | **xanî**<br><sub>خانی</sub> | **xaniyê**<br><sub>خانیێ</sub> | **xaniyek**<br><sub>خانیەک</sub> | **xaniyekî**<br><sub>خانیەکی</sub> | **xaniyan**<br><sub>خانیان</sub> | **xaniyên**<br><sub>خانیێن</sub> |
| **çiya** | mountain | m | **çiya**<br><sub>چیا</sub> | **çiya**<br><sub>چیا</sub> | **çiyayê**<br><sub>چیایێ</sub> | **çiyayek**<br><sub>چیایەک</sub> | **çiyayekî**<br><sub>چیایەکی</sub> | **çiyayan**<br><sub>چیایان</sub> | **çiyayên**<br><sub>چیایێن</sub> |
<!-- /gen -->

## In sentences

<!-- gen:sentences ipa=1
Ez diçim malê. | I am going home.
Ez pirtûkê dixwînim. | I am reading the book.
Em li bajêr in. | We are in the city.
Ez bi keçan re diaxivim. | I am talking with the girls.
Wî jinek dît. | He saw a woman. (past: the doer wî is oblique, the object jinek direct)
-->
| # | Kurdish | Arabic script | IPA | English |
|---|---|---|---|---|
| 1 | Ez diçim malê. | ئەز دچم مالێ. | /ɛz dɪtʃɯm maːleː/ | I am going home. |
| 2 | Ez pirtûkê dixwînim. | ئەز پرتووکێ دخوینم. | /ɛz pɪɾtuːkeː dɪxʷiːnɯm/ | I am reading the book. |
| 3 | Em li bajêr in. | ئەم ل باژێر ئن. | /ɛm lɪ baːʒeːɾ ɪn/ | We are in the city. |
| 4 | Ez bi keçan re diaxivim. | ئەز ب کەچان ڕە دئاخڤم. | /ɛz bɪ kɛtʃaːn rɛ dɪaːxɪvɯm/ | I am talking with the girls. |
| 5 | Wî jinek dît. | وی ژنەک دیت. | /wiː ʒɪnɛk diːt/ | He saw a woman. (past: the doer wî is oblique, the object jinek direct) |
<!-- /gen -->

**bajêr**: a few masculine nouns change the **a** of their last syllable to **ê** in the oblique: *bajar → bajêr*. This vowel change is not generated by zimankit, which gives the regular *bajarî*; learn it with those nouns.

## Practice

1. *I see the woman* (present: *dibînim*).
2. *in the house* (*li … *).
3. *with the friends* (*bi … re*, *heval*).

<details><summary>Answers</summary>

1. Ez jinê dibînim.
2. li malê
3. bi hevalan re

</details>

## Summary

* Oblique after prepositions, for present-tense objects, for owners and for past agents.
* f **-ê**, m **-î** (optional), pl **-an**; indefinite **-ekê / -ekî**.
* Some masculine nouns change a → ê in the oblique (bajêr).

<!-- nav:bottom -->
---
[← 8. Ezafe: linking nouns to adjectives and owners](08-ezafe.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [10. The present tense →](10-present-tense.md)
<!-- nav:bottom -->
