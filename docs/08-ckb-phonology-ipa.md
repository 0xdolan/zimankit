<!-- nav:top -->
[← Central Kurdish: alphabet and orthography](07-ckb-orthography.md) · [⌂ Contents](00-index.md) · [Central Kurdish: morphology →](09-ckb-morphology.md)
<!-- nav:top -->

# Central Kurdish: phonology and IPA (G2P)

**On this page:** [1. Grapheme parse](#1-grapheme-parse) · [2. Semivowel resolution](#2-semivowel-resolution) · [3. Bizroke repair (epenthesis)](#3-bizroke-repair-epenthesis) · [Consonants](#consonants) · [Options](#options) · [Accuracy check](#accuracy-check)

`skills_ckb/phonology_ipa.py` converts Arabic-script Sorani to broad phonemic IPA in three passes.

## 1. Grapheme parse

The word is split into graphemes; `وو` and `یی` stay together.

## 2. Semivowel resolution

| context | و | ی |
|---|---|---|
| the word `و` ("and") | /u/ | — |
| after a vowel letter | /w/ `ئاو` /ʔaːw/ | /j/ `چای` /tʃaːj/ |
| before a vowel letter | /w/ `خواردن` /xwaːɾdɯn/ | /j/ `پیاو` /pjaːw/ |
| between consonants / final | /u/ `کورد` /kuɾd/ | /iː/ `میر` /miːɾ/ |
| doubled | `وو` /uː/ | `یی` /iː/ |

Before another vowel a hiatus glide is inserted: `هاتووە` /haːtuːwæ/, `ماسییەکە` /maːsiːjækæ/.

## 3. Bizroke repair (epenthesis)

The phonotactic skeleton (shared with Kurmanji, `shared_utils/phonology_core.py`):

| position | allowed clusters |
|---|---|
| word-initial onset | C, C+glide (kw, xw, pj), sibilant+stop (st, ʃk) |
| medial onset | C, C+glide |
| medial coda | fricative+stop (st), nasal+stop (nd), glide+C |
| final coda | falling sonority (rd, nd, st, ʃk, ɾt) |

Sonority: glide 5 > liquid 4 > nasal 3 > fricative 2 > stop 1. Every consonant run that violates these limits is repaired by inserting /ɯ/, carving `C ɯ C` syllables from the right. By default the inferred vowel is shown in parentheses so a reader sees it was not written.

| word | IPA | syllables | Latin |
|---|---|---|---|
| پیاوەکە | pjaːwækæ | pjaː.wæ.kæ | pyaweke |
| کتێبەکەم | k(ɯ)teːbækæm | kɯ.teː.bæ.kæm | kitêbekem |
| کوردستان | kuɾd(ɯ)staːn | kuɾ.dɯs.taːn | kurdistan |
| هەڵبژاردن | hæɫb(ɯ)ʒaːɾd(ɯ)n | hæɫ.bɯ.ʒaːɾ.dɯn | hellbijardin |
| کردنەوە | k(ɯ)ɾd(ɯ)næwæ | kɯɾ.dɯ.næ.wæ | kirdinewe |
| مشک | m(ɯ)ʃk | mɯʃk | mişk |
| بزن | b(ɯ)z(ɯ)n | bɯ.zɯn | bizin |
| ئنجا | ʔ(ɯ)ndʒaː | ʔɯn.dʒaː | inca |

Why right-to-left: Sorani prefers closed `CɯC` syllables built from the end of the word (`bɯɾ.dɯn`, not `bɯ.ɾɯd.n`). Why medial codas are restricted: without that rule `کوردستان` would come out as *kurd.stan* and `هەڵبژاردن` as *hełb.jar.din*.

## Consonants

| letter | IPA | letter | IPA | letter | IPA |
|---|---|---|---|---|---|
| ئ | ʔ | ج | dʒ | چ | tʃ |
| ح | ħ | خ | x | ر | ɾ (initial r) |
| ڕ | r | ژ | ʒ | ش | ʃ |
| ع | ʕ | غ | ɣ | ق | q |
| گ | ɡ | ڵ | ɫ | ه | h |

Vowels: `ا` aː · `ە` æ · `ێ` eː · `ۆ` oː · `وو` uː · `و` u · `ی` iː · bizroke ɯ.

## Options

```python
from zimankit.skills_ckb.phonology_ipa import to_ipa, G2POptions
to_ipa("کتێبەکەم", G2POptions(mark_epenthesis=False))   # 'kɯteːbækæm'
to_ipa("ئاو", G2POptions(glottal_onset=False))           # 'aːw'
to_ipa("کوردستان", G2POptions(syllable_dots=True))       # 'kuɾ.d(ɯ)s.taːn'
```

## Accuracy check

The builder compares the generated IPA of every lemma that also has a reference transcription in the lexicon source (after neutralising notation differences such as stress marks and ɘ/ɪ/ə vs ɯ) and reports the mean similarity in `build_report_ckb.json`.

<!-- nav:bottom -->
---
[← Central Kurdish: alphabet and orthography](07-ckb-orthography.md) · [⌂ Contents](00-index.md) · [Central Kurdish: morphology →](09-ckb-morphology.md)
<!-- nav:bottom -->
