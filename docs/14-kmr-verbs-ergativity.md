<!-- nav:top -->
[← Northern Kurdish: nominal morphology (gender, case, ezafe)](13-kmr-morphology.md) · [⌂ Contents](00-index.md) · [Transliteration →](15-transliteration.md)
<!-- nav:top -->

# Northern Kurdish: verbs and split ergativity

**On this page:** [Stems and endings](#stems-and-endings) · [Paradigm of dîtin (excerpt, `python -m zimankit conjugate dîtin`)](#paradigm-of-dîtin-excerpt-python--m-zimankit-conjugate-dîtin) · [Split ergativity](#split-ergativity)

## Stems and endings

Past stem = infinitive − `-in` / `-n` (`dîtin → dît`, `çûn → çû`); the present stem is lexical (`dîtin → bîn`, `kirin → k`, `gotin → bêj`, `hatin → ê`). Reference list: `zimankit/data/kmr_verbs_core.tsv`; lexicon verbs bring their own "Rehê dema niha".

| person | after consonant | after vowel |
|---|---|---|
| 1sg | -im `dibînim` | -m `dişom` |
| 2sg | -î `dibînî` | -yî `dişoyî` |
| 3sg | -e present / ∅ past | ∅ |
| pl | -in | -n |

Prefixes: `di-` indicative (`t-` before a vowel-initial stem: `têm`, `tînim`), `bi-` subjunctive/imperative, `na-` negative present (`ni-` for `zanîn`, `karîn`), `ne-` negative past/subjunctive, `nedi-` negative past progressive. Preverbs (`ra- hil- der- ve- lê- çê- …`) come first and suppress `bi-`: `radibim`, `rabim`, `rabe`.

## Paradigm of dîtin (excerpt, `python -m zimankit conjugate dîtin`)

| cell | 1sg | 2sg | 3sg | pl |
|---|---|---|---|---|
| present | dibînim | dibînî | dibîne | dibînin |
| negative | nabînim | nabînî | nabîne | nabînin |
| subjunctive | bibînim | bibînî | bibîne | bibînin |
| simple past | dîtim | dîtî | dît | dîtin |
| past progressive | didîtim | didîtî | didît | didîtin |
| present perfect | dîtime | dîtiyî | dîtiye | dîtine |
| past perfect | dîtibûm | dîtibûyî | dîtibû | dîtibûn |

Irregulars: `hatin` (`têm`, `nayêm`, `bêm`, imperative `were`), `çûn` (imperative `here`).

## Split ergativity

| tense family | agent | object | verb agrees with |
|---|---|---|---|
| present-stem tenses | **direct** (`ez`) | oblique (`te`) | agent/subject |
| past-stem tenses, transitive | **oblique** (`min`) | **direct** (`tu`) | **object** |
| past-stem tenses, intransitive | direct (`ez`) | — | subject |

```
Ez te dibînim.   I.DIR you.OBL see-1SG      accusative, agreement with ez ✔
Min tu dîtî.     I.OBL you.DIR saw-2SG      ergative,  agreement with tu ✔
Min ew dîtin.    I.OBL they.DIR saw-PL      ergative,  ew = 3sg|pl ✔
Min tu dîtim.    *                          ergative,  -im marks 1sg but object tu is 2sg ✘
```

`skills_kmr/syntax.py: detect_alignment(sentence)`:

1. find the last finite verb reading;
2. past stem + transitive → ergative, else accusative;
3. classify preceding tokens by case: pronoun tables (`ez tu ew em hûn ev` direct, `min te wî wê me we wan vî vê van` oblique) and nominal analyses (`-ê -î -an -ekê -ekî` oblique); arguments of prepositions (`di ji bi li …`) are skipped;
4. choose agent/object by alignment and check the verb ending against the controller; notes record pro-drop, marked object-before-agent order and mismatches.

```bash
echo "Min tu dîtim." | python -m zimankit ergativity
# {"alignment": "ergative", "agent": {"token": "Min", "case": "obl", ...}, "object": {"token": "tu", ...},
#  "verb_person": "1sg", "controller": "object", "agreement_ok": false,
#  "notes": ["verb ending marks 1sg but object 'tu' is 2sg"]}
```

Central Kurdish is also ergative in the past, but marks the agent with a **set-2 enclitic** instead of case (see [chapter 10](10-ckb-verbs.md)).

<!-- nav:bottom -->
---
[← Northern Kurdish: nominal morphology (gender, case, ezafe)](13-kmr-morphology.md) · [⌂ Contents](00-index.md) · [Transliteration →](15-transliteration.md)
<!-- nav:bottom -->
