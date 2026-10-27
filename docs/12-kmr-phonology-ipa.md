<!-- nav:top -->
[← Northern Kurdish: alphabet and orthography](11-kmr-orthography.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: nominal morphology (gender, case, ezafe) →](13-kmr-morphology.md)
<!-- nav:top -->

# Northern Kurdish: phonology and IPA

**On this page:** [Vowels](#vowels) · [Consonants](#consonants) · [Narrow mode: aspiration and the "ejectives"](#narrow-mode-aspiration-and-the-ejectives)

`skills_kmr/phonology_ipa.py`. Hawar spelling is nearly phonemic; the rules are about length, rhotics, digraphs and (in narrow mode) aspiration.

## Vowels

| letter | IPA | example |
|---|---|---|
| a | aː | `mal` /maːl/ |
| e | ɛ | `jinekê` /ʒɪnɛkeː/ |
| ê | eː | `rê` /reː/ |
| i | ɪ (root) / ɯ (reduced, see below) | `jin` /ʒɪn/ |
| î | iː | `dîtin` /diːtɯn/ |
| o | oː | `roj` /roːʒ/ |
| u | ʊ | `kurd` /kʊɾd/ |
| û | uː | `çûn` /tʃuːn/ |

**Reduced suffix vowel.** In the final *closed* syllable of a polysyllabic word, `i` is rendered as the reduced vowel [ɯ] — almost always the infinitive / plural suffix *-in* (`dîtin` /diːtɯn/, `xwarin` /xʷaːɾɯn/). This keeps the transcription parallel to the Sorani bizroke. Disable with `KmrG2POptions(reduced_suffix_i=False)`.

## Consonants

| spelling | IPA | note |
|---|---|---|
| c / ç | dʒ / tʃ | |
| j / ş | ʒ / ʃ | |
| x / xw | x / xʷ | `xwe` /xʷɛ/ |
| r | ɾ | tap |
| rr, initial r | r | trill: `roj` /roːʒ/ |
| ḧ / ẍ / ' | ħ / ɣ / ʕ | `'erd` /ʕɛɾd/ |
| y | j | |
| g | ɡ | |

## Narrow mode: aspiration and the "ejectives"

Kurmanji contrasts aspirated and unaspirated (often described as ejective-like) `p t k ç`, but Hawar does not write it. In narrow mode plain letters are aspirated and an apostrophe after the letter — the convention of phonetic dictionaries — marks the unaspirated member; `n` assimilates to [ŋ] before velars.

```python
from zimankit.skills_kmr.phonology_ipa import to_ipa, KmrG2POptions
to_ipa("jinekê")                                   # 'ʒɪnɛkeː'
to_ipa("jinekê", KmrG2POptions(narrow=True))       # 'ʒɪnɛkʰeː'
to_ipa("p'ir",   KmrG2POptions(narrow=True))       # 'pɪɾ'   (unaspirated)
to_ipa("bang",   KmrG2POptions(narrow=True))       # 'baːŋɡ'
to_ipa("zivistan", KmrG2POptions(syllable_dots=True))
```

<!-- nav:bottom -->
---
[← Northern Kurdish: alphabet and orthography](11-kmr-orthography.md) · [⌂ Contents](00-index.md) · [Northern Kurdish: nominal morphology (gender, case, ezafe) →](13-kmr-morphology.md)
<!-- nav:bottom -->
