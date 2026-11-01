<!-- nav:top -->
[← Sentence structure](22-sentence-structure.md) · [⌂ Contents](00-index.md)
<!-- nav:top -->

# The Central Kurdish written standard

**On this page:** [Letters and sounds](#letters-and-sounds) · [Ezafe and the three ی](#ezafe-and-the-three-ی) · [Verbs: the third person](#verbs-the-third-person) · [Word spacing](#word-spacing) · [Agent clitic placement](#agent-clitic-placement) · [Where the sources disagree](#where-the-sources-disagree) · [Not implemented yet](#not-implemented-yet)

This chapter records the Central Kurdish spelling and grammar rules that zimankit is checked against, how much of each is implemented, and where the authorities disagree. The sources are listed in [References](21-references.md). Coverage of them is uneven: the spelling standard and the verb chapters were read closely, while several school books and handouts were read only in part.

Two ideas run through it:

- **Corpus evidence decides what zimankit recognises, and the standard decides what it recommends.** News text prefers some non-standard forms (`وەکو` over `وەکوو`, `ڕۆژئاوا` over `ڕۆژاوا`), so frequency cannot choose the standard form. Those forms stay in the lexicon, and the validator flags them where it can.
- **Solid compound verbs are not errors.** The standard prefers a space, but the Academy is reported to allow solid forms and they are common. Accept both.

## Letters and sounds

| rule | write | not | zimankit |
|---|---|---|---|
| Kurdish code points | `ک` U+06A9, `ی` U+06CC, `ە` U+06D5 | `ك ي ة` | normalised |
| `ە` and `ه` are different letters | `سەر` | `سهر`, `سه ر` | normalised where safe |
| `ڕ` and `ر` are different letters, and every initial r is `ڕ` | `ڕاست`, `کوڕ` | `راست` | initial `ر` normalised; elsewhere needs the lexicon |
| `ئ` before an initial vowel | `ئاو`, `ئەو` | `او`, `ەو` | normalised |
| `ئ` drops inside compounds | `ڕۆژاوا`, `گوڵاو`, `ماڵاوایی` | `ڕۆژئاوا`, `گوڵئاو` | not flagged; common forms stay recognised |
| `وو` is never initial | `وشە`, `ورچ` | `ووشە`, `وورچ` | `validate_word` |
| final û after a consonant is `وو` | `چوو`, `مێژوو`, `وەکوو` | `چو`, `وەکو` | `validate_word` |
| medial û is `وو` | `کەرکووک`, `حوکوومەت` | `کەرکوک` | not flagged; needs a curated list |
| plain î is one `ی` | `تیر`, `کوردی` | `تییر`, `کوردیی` as the bare word | not flagged; needs the lexicon |
| `یی` for î after a vowel | `کۆتایی`, `سنەیی` | `کۆتای` | generated correctly by the morphology |
| `یە` is written solid | `سپییە`, `چییە`, `نییە`, `مامۆستایە` | `سپی یە`, `سپی‌یە` | ZWNJ form normalised |
| the `ت` stays | `دەستەسڕ`, `ماستاوچی` | `دەسەسڕ` | not flagged |
| Latin values | `wişe`, `mirdin`, `stran`, `mindall` | | `to_latin` |

There are 37 sounds and 34 letters. The bizroke `i` is a real short vowel that the Arabic-based alphabet does not write.

## Ezafe and the three ی

The ezafe `ی` is written even after a word that ends in `ی` or `یی`:

| the word ends in | form | example |
|---|---|---|
| no `ی` | `ی` | `کوردی سنە` "the Kurd of Sanandaj" |
| `ی` | `یی` | `کوردیی سنە` "the Kurdish of Sanandaj", `ڕۆژی جیهانیی ژن` |
| `یی` | `ییی` | `سنەییی دڵسۆز`, `ڕەشاییی چاو` |

`decline` generates these and `normalize` now keeps them. One author reports that most people reject three `ی`, so zimankit does not warn against `یی` here.

## Verbs: the third person

The third person of a transitive past whose stem ends in `ی` needs a second `ی`, and intransitive verbs do not. zimankit generates these correctly:

| verb type | forms |
|---|---|
| transitive | `نووسیم`, `نووسیت`, `نووسیی`, `نووسییان` |
| intransitive | `فڕیم`, `فڕییت`, `فڕی`, `فڕیین` |

The passive adds `د` after a root in `ر` or `ڕ`: `دەخوێنرێت`, but `دەکڕدرێت`, `دەنێردرێت`.

## Word spacing

| rule | write | not | zimankit |
|---|---|---|---|
| compound words are solid | `دڵپاک`, `مارماسی`, `گوڵەگەنم`, `دەموچاو`, `شارەوشار` | `دڵ پاک` | not checked |
| adjective after ە is separate | `کچە جوانەکە`, `شەوە گەرمەکە` | `کچەجوانەکە` | not checked |
| compound infinitives are solid | `نانکردن`, `شەڕکردن`, `پێکهێنان` | `نان کردن` | not checked |
| conjugated compounds split | `نان دەکەم`, `نانم کرد`, `نانم کردووە` | `نانمکرد` (see below) | generated solid |
| preverb, present is solid | `هەڵدەگرم` | `هەڵ دەگرم` | generated |
| preverb, split around a clitic | `هەڵم گرت`, `ڕای گەیاند` | `ڕای‌گەیاند` | generated solid |
| four parts | `پێ لێ هەڵگرتن`, `پێی لێ هەڵگرت` | | not implemented |
| infinitive or finite verb | `ڕێککەوتن` (noun), `ڕێک کەوتن` (verb) | | not checked |
| conjunction `و` is separate | `من و تۆ` | `من‌و تۆ` | ZWNJ form normalised |
| prepositions are separate, postpositions attach | `لە ماڵدا`, `لە کرماشانەوە`, `بە ئاسمانەوە` | `لەماڵدا`, `لە ماڵ دا` | not checked |
| `دا` as a postposition attaches, even before a copula | `من لە ماڵدام`, `لە ماڵدایە` | `لە ماڵ دایە` | analysed |
| `دا` as the verb "gave" is separate | `نامەکەم دا بە سۆران` | | handled |
| `لە` joins in fixed forms | `لەگەڵ`, `لەسەر`, `لەژێر`, `لێرە`, `لەوێ` | `لە گەڵ` | not checked |
| `بێ` attached means "-less", separate means "without" | `بێکار` "unemployed", `بێ کار ژیان` | | analysed |
| comparative attaches, the word "another" is separate | `جوانتر`, `جوانترین`; `شەوێکی تر` | | analysed |
| `پێ تێ لێ` are separate, and attach to a clitic | `پارەم پێ نەما`, `دەستم لێ دا`; `پێم وت`, `لێم سەند` | `پارەم پێنەما` | analysed |
| manner `بە` attaches, preposition `بە` is separate | `بەخێرایی`, `بەهێواشی`; `بە ئۆتۆمبیل` | `بە خێرایی` | not analysed |
| compound numbers are separate | `بیست و یەک`, `دوو سەد`, `سێ میلیۆن` | `بیستویەک` | not checked |
| number + noun as a new word is solid | `دووشەممە`, `یەکشاخ`, `چوارپێ` | | lexicon |
| `ئەم` + time word is solid, unless the noun has an ending | `ئەمڕۆ`, `ئەمساڵ`; `ئەم جارە` | `ئەمجارە` | not checked |

Other preferred spellings: `بەرانبەر` (not `بەرامبەر`), `لێبووردن`, `مشتومڕ`, `کشتوکاڵ`, `ئەلفبێ`, `پێم وایە`, `دەست خۆش`, `تەمەندرێژ`, and `دە-` in preference to `ئە-` (`دەڕۆم`).

## Agent clitic placement

The grade 12 handout and ڕێزمانی وێنەیی agree on this rule:

1. With a stated object, the clitic goes on the object, whatever the verb type: `نانم کرد`.
2. Otherwise it goes on the first part of a compound or preverb verb, in every tense and polarity: `ڕامان خست`, `ڕامان نەخست`, `ڕامان دەخست`, `ڕامان خستووە`.
3. On a simple verb it follows `نە` or `دە`, sits inside the perfect, or ends the verb.

zimankit handles rule 3 and the affirmative simple past of rule 2. It still generates `هەڵنەمگرت`, `هەڵدەمگرت` and `هەڵگرتوومە`.

## Where the sources disagree

These are open, so zimankit should not change them silently. The interim choice is in the last column.

| point | positions | interim |
|---|---|---|
| preverb + clitic | split in the Academy pamphlets; solid allowed according to Hashemi's FAQ, which is the only evidence for that allowance; both printed in school material | accept both, prefer split |
| conjugated compounds, present | split in Hashemi and zkurd.org; solid in the grade 12 handout | as above |
| `تێکچوو` | split in zkurd.org; solid in the 2010 pamphlet | prefer split |
| `ئەمجارە` | `ئەم جارە` in Hashemi; solid in the 2004 pamphlet | do not flag |
| `حەوت سەد`, `ئەلفبێ` | `حەوتسەد` in the 2010 pamphlet; `ئەلفوبێ` in the 2004 pamphlet | prefer Hashemi, warn only |
| clitic after `نە`/`دە` on a simple verb | spaced `نەم هێنا`, `دەمان سڕی` in school material; also solid `دەمانخوێند` | keep solid |
| plural of ە-final nouns | `قوتابخانان`, `پەنجەران`, `دەرگەیان` | not generated |
| definite after a vowel | by syllable count, both `چراکە` and `چرایەکە`, or by final letter | by final letter |
| negative past subjunctive with a clitic | not printed in the sources checked; `نەمخواردبا` follows the clitic rule, `نەخواردبام` is the alternative | generate the first, accept both |
| 3sg pluperfect + ەوە | `دۆزیبووەوە` or `هێنابوویەوە` | the first |
| imperative + ەوە | `بکەرەوە` or `بکەوە` | not changed |
| `هاتن` negative | `نایەم`, `مەیە` or `نایێم`, `مەیێ` | the common forms |
| `چوون` imperative | `بچۆ` in the sources; `بڕۆ` in zimankit | not changed |
| passive after ر | `د` inserted, or `سپێررا`, `برا` regionally | keep `د` |
| `ماسییەکە` or `ماسێکە` | | generate the first |
| vocative | `ە` masculine, `ێ` feminine, `ینە` plural, or `ە` for both | not implemented |
| number + plural noun, `پیاوەکە هاتن` | common usage; no explicit rule found | warn only |
| terminology | `هاوەڵناو`/`ئاوەڵناو`, `جێناو`/`ڕاناو`, `کار`/`کردار` | list both |
| ی after `دوا`, `برا` as `bra`, `مشک` as `mişk` or `mişik` | one example each, or regional | not changed |

## Not implemented yet

In the order they depend on each other:

1. **Split forms:** correct clitic position in every tense, spacing classes for preverbs, then reading `هەڵم گرت`, `ڕای گەیاند` and `دەست پێ دەکەم` as one verb, then object clitics (`دەتبینم`, `بینیمیت`).
2. **Parser:** circumpositions over several words, subordinate clauses, Kurdish labels (`نیهاد`, `جێگری بکەر`), and a Sorani agreement check.
3. **Lexicon overrides:** a curated table so that the standard form is chosen when frequency prefers another (`وەکوو`, `بەرانبەر`, `کەرکووک`).
4. **Generated pages and lessons:** print split forms first and teach them. This comes last on purpose: until step 1 is done, zimankit could not read the spelling its own course would teach.

Some transliterations are also still doubtful and have not been checked against a source, such as `rakridin` for `ڕاکردن` and `hellîgrit` for `هەڵیگرت`.

<!-- nav:bottom -->
---
[← Sentence structure](22-sentence-structure.md) · [⌂ Contents](00-index.md)
<!-- nav:bottom -->
