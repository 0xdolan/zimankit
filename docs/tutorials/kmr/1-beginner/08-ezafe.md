<!-- nav:top -->
[← 7. Nouns: gender, a / the, and plurals](07-nouns-gender-and-definiteness.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [9. Direct and oblique case →](09-cases.md)
<!-- nav:top -->

# 8. Ezafe: linking nouns to adjectives and owners

**Level:** 🟢 Beginner · lesson 8 of 23

**On this page:** [The linking ending](#the-linking-ending) · [Indefinite ezafe: *a good man*](#indefinite-ezafe-a-good-man) · [Chains](#chains) · [Standalone ezafe: *mine, his*](#standalone-ezafe-mine-his) · [How zimankit reads these](#how-zimankit-reads-these) · [Practice](#practice) · [Summary](#summary)

## The linking ending

When a noun is followed by an adjective, an owner or another noun that describes it, Kurmanji adds a **linking ending**, the **ezafe**, to the noun. Its form depends on **gender** and **number**:

| | after a consonant | after a vowel | example |
|---|---|---|---|
| masculine singular | **-ê** | **-yê** | bav**ê** min *my father* |
| feminine singular | **-a** | **-ya** | mal**a** min *my house* |
| plural (both genders) | **-ên** | **-yên** | heval**ên** min *my friends* |

The owner after the ezafe is in the **oblique** case: *mala **min*** (not *ez*), *bavê **wê*** “her father”.

<!-- gen:noun nouns=bav,mirov,bajar,xanî,jin,mal,pirtûk,çiya cells=def.dir.sg,def.ez.sg,def.ez.pl -->
| noun | meaning | gender | direct sg | ezafe sg | ezafe pl |
|---|---|---|---|---|---|
| **bav** | father | m | **bav**<br><sub>باڤ</sub> | **bavê**<br><sub>باڤێ</sub> | **bavên**<br><sub>باڤێن</sub> |
| **mirov** | person, human, man | m | **mirov**<br><sub>مرۆڤ</sub> | **mirovê**<br><sub>مرۆڤێ</sub> | **mirovên**<br><sub>مرۆڤێن</sub> |
| **bajar** | city | m | **bajar**<br><sub>باژار</sub> | **bajarê**<br><sub>باژارێ</sub> | **bajarên**<br><sub>باژارێن</sub> |
| **xanî** | house (building) | m | **xanî**<br><sub>خانی</sub> | **xaniyê**<br><sub>خانیێ</sub> | **xaniyên**<br><sub>خانیێن</sub> |
| **jin** | woman; wife | f | **jin**<br><sub>ژن</sub> | **jina**<br><sub>ژنا</sub> | **jinên**<br><sub>ژنێن</sub> |
| **mal** | house, home | f | **mal**<br><sub>مال</sub> | **mala**<br><sub>مالا</sub> | **malên**<br><sub>مالێن</sub> |
| **pirtûk** | book | f | **pirtûk**<br><sub>پرتووک</sub> | **pirtûka**<br><sub>پرتووکا</sub> | **pirtûkên**<br><sub>پرتووکێن</sub> |
| **çiya** | mountain | m | **çiya**<br><sub>چیا</sub> | **çiyayê**<br><sub>چیایێ</sub> | **çiyayên**<br><sub>چیایێن</sub> |
<!-- /gen -->

<!-- gen:sentences ipa=1
mala min | my house
bavê te | your father
zimanê kurdî | the Kurdish language
pirtûka nû | the new book
bajarê mezin | the big city
hevalên me | our friends
-->
| # | Kurdish | Arabic script | IPA | English |
|---|---|---|---|---|
| 1 | mala min | مالا من | /maːlaː mɪn/ | my house |
| 2 | bavê te | باڤێ تە | /baːveː tɛ/ | your father |
| 3 | zimanê kurdî | زمانێ کوردی | /zɪmaːneː kʊɾdiː/ | the Kurdish language |
| 4 | pirtûka nû | پرتووکا نوو | /pɪɾtuːkaː nuː/ | the new book |
| 5 | bajarê mezin | باژارێ مەزن | /baːʒaːɾeː mɛzɯn/ | the big city |
| 6 | hevalên me | هەڤالێن مە | /hɛvaːleːn mɛ/ | our friends |
<!-- /gen -->

## Indefinite ezafe: *a good man*

With *a* (-ek), the ezafe is **-ekî** for masculine and **-eke** for feminine nouns:

<!-- gen:noun nouns=mirov,bajar,jin,pirtûk cells=ind.dir.sg,ind.ez.sg -->
| noun | meaning | gender | indef. direct | indef. ezafe |
|---|---|---|---|---|
| **mirov** | person, human, man | m | **mirovek**<br><sub>مرۆڤەک</sub> | **mirovekî**<br><sub>مرۆڤەکی</sub> |
| **bajar** | city | m | **bajarek**<br><sub>باژارەک</sub> | **bajarekî**<br><sub>باژارەکی</sub> |
| **jin** | woman; wife | f | **jinek**<br><sub>ژنەک</sub> | **jineke**<br><sub>ژنەکە</sub> |
| **pirtûk** | book | f | **pirtûkek**<br><sub>پرتووکەک</sub> | **pirtûkeke**<br><sub>پرتووکەکە</sub> |
<!-- /gen -->

*mirovekî baş* “a good man”, *pirtûkeke nû* “a new book”.

## Chains

Ezafes chain from left to right, each noun linking to the next: *mala bavê min* “my father's house” (house-of father-of me), *navê bajarê mezin* “the name of the big city”.

## Standalone ezafe: *mine, his*

Without a noun, the ezafe is a little word **yê** (m), **ya** (f), **yên** (pl): *Ev pirtûk **ya** min e.* “This book is mine.”

## How zimankit reads these

The ending *-ê* is ambiguous (masculine ezafe, or feminine oblique, lesson 9). The analyzer uses the noun's gender from its lexicon to decide:

<!-- gen:analyze words=bavê,mala,hevalên,mirovekî,pirtûkeke -->
| word | segmentation | morpheme tags | lemma | features |
|---|---|---|---|---|
| **bavê** | bav+ê | STEM+EZ.M|OBL.F | bav | definite=def, number=sg, gender=m, ezafe=yes |
| **mala** | mal+a | STEM+EZ.F | mal | definite=def, number=sg, ezafe=yes, gender=f |
| **hevalên** | heval+ên | STEM+EZ.PL | heval | definite=def, number=pl, ezafe=yes, gender=m |
| **mirovekî** | mirov+ekî | STEM+INDEF.OBL.M|INDEF.EZ.M | mirov | definite=ind, number=sg, gender=m, case=obl |
| **pirtûkeke** | pirtûk+eke | STEM+INDEF.EZ.F | pirtûk | definite=ind, number=sg, ezafe=yes, gender=f |
<!-- /gen -->

*mirovekî* gets the oblique reading first; in *mirovekî baş* it is an ezafe. The analyzer keeps both readings and leaves the choice to the context.

## Practice

1. *my sister* (*xwişk f*).
2. *the big village* (*gund m*, *mezin* big).
3. *a beautiful city* (*bajar m*, *xweş* nice).

<details><summary>Answers</summary>

1. xwişka min
2. gundê mezin
3. bajarekî xweş

</details>

## Summary

* Ezafe: **-ê** (m), **-a** (f), **-ên** (pl); after a vowel -yê, -ya, -yên.
* Indefinite: **-ekî** (m), **-eke** (f).
* The word after the ezafe is oblique: mala **min**.

<!-- nav:bottom -->
---
[← 7. Nouns: gender, a / the, and plurals](07-nouns-gender-and-definiteness.md) · [⌂ Northern Kurdish (Kurmanji) course](../README.md) · [9. Direct and oblique case →](09-cases.md)
<!-- nav:bottom -->
