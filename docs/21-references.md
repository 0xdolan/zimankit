<!-- nav:top -->
[← Glossary](20-glossary.md) · [⌂ Contents](00-index.md) · [Sentence structure →](22-sentence-structure.md)
<!-- nav:top -->

# References and further reading

Grammars and linguistic descriptions that the rules follow (general scholarship; no data was copied from them):

* W. M. Thackston, *Sorani Kurdish: A Reference Grammar with Selected Readings* (Harvard).
* W. M. Thackston, *Kurmanji Kurdish: A Reference Grammar with Selected Readings* (Harvard).
* E. N. McCarus, *A Kurdish Grammar: Descriptive Analysis of the Kurdish of Sulaimaniya, Iraq* (1958).
* G. Haig, *Alignment Change in Iranian Languages: A Construction Grammar Approach* (2008) — split ergativity.
* G. Haig & E. Öpengin, "Kurmanji Kurdish in Turkey: structure, varieties, and status" (2018).
* E. Öpengin, *The Mukri Variety of Central Kurdish* (2016).
* Unicode Standard, chapter 9 (Middle East-I: Arabic) and the Unicode Arabic-script code charts.
* Universal Dependencies guidelines (UPOS / features / relations) — <https://universaldependencies.org/u/>.
* Kurdish Academy / KRG orthography conventions for Central Kurdish (standard letter inventory, ڕ / ڵ, ە vs ه).

Kurdish-language sources for the Central Kurdish written standard and grammar, as used in [chapter 23](23-ckb-written-standard.md):

* دیاکۆ هاشمی, [ڕێنووسی زمانی کوردی](https://diyako.yageyziman.com/%da%95%db%8e%d9%86%d9%88%d9%88%d8%b3/), and its [list of grammar works](https://diyako.yageyziman.com/%da%95%db%8e%d8%b2%d9%85%d8%a7%d9%86/), through which the works below were reached.
* [چاوگی لێکدراو](https://zkurd.org/%da%86%d8%a7%d9%88%da%af%db%8c-%d9%84%db%8e%da%a9%d8%af%d8%b1%d8%a7%d9%88/), zkurd.org.
* ئەکادیمیای کوردی, spelling pamphlets of [2004](http://www.yageyziman.com/pdfekan/Renusi_Kurdi_Akadimyay_Kurdi_2004.pdf) and [2010](http://www.yageyziman.com/pdfekan/Renusi_Kurdi_Akadimyay_Kurdi_2010.pdf).
* [ڕێزمانی وێنەیی](http://www.yageyziman.com/pdfs/Rezimani_Weneyi.pdf), شنە عەزیز حەمە ڕەحیم.
* [ڕێزمانی کوردی, grade 12 handout](http://www.yageyziman.com/rezman-12.pdf), a teacher's handout.
* [ڕێزمانی کوردی](http://www.yageyziman.com/Rezmani_Kurdi_Neriman_Xoshnaw.pdf), نەریمان خۆشناو.
* [ڕێزمانی ئاخاوتنی کوردی](http://www.yageyziman.com/rezman_korri_zanyari.pdf), کۆڕی زانیاریی کورد.
* [ڕستەناسی](http://www.yageyziman.com/pdfs/syntax_Shaswar.pdf), شاسوار هەرشەمی; [جێگری بکەر](http://www.yageyziman.com/Adnan_Cegir_Biker.htm), عەدنان ئەحمەد.
* [بابەتە ڕێزمانییەکان](http://diyako.yageyziman.com/2023/04/08/mamosta-abdullah-abdulqader/), عبدالله عبدالقادر علی.

## Articles used in the literature audit

zimankit uses these papers and repositories for checking rules and as test oracles. No data was copied from them. Where a chapter uses one, the chapter names it.

Morphology and spelling:

* S. Ahmadi (2021). "Hunspell for Sorani Kurdish Spell Checking and Morphological Analysis." arXiv:2109.06374. Its verb template (Table 1) is the basis for the stripped verb elements in [chapter 10](10-ckb-verbs.md#elements-stripped-before-lookup).
* S. Ahmadi (2020). "KLPT – Kurdish Language Processing Toolkit." *Proc. NLP-OSS 2020*, ACL, pp. 72–84. Code and data: <https://github.com/sinaahmadi/klpt> (CC BY-SA 4.0). Its `.aff` rule groups and test cases were used as an oracle ([chapters 4](04-unicode-normalization.md), [10](10-ckb-verbs.md), [13](13-kmr-morphology.md), [14](14-kmr-verbs-ergativity.md)).
* S. Ahmadi & H. Hassani (2020). "Towards Finite-State Morphology of Kurdish." arXiv:2005.10652.
* S. Salavati & S. Ahmadi (2018). "Building a Lemmatizer and a Spell-checker for Sorani Kurdish." arXiv:1809.10763.
* K. O. Aziz, R. A. Teimoor, T. A. Tofiq, D. A. Salih (2023). "Kurdish Sorani dialect Morphological Verb Generation Using a Concatenative Rule-based Strategy." Research Square preprint, doi:10.21203/rs.3.rs-2748581/v1.
* A. Mahmudi, S. Ahmadi, K. Kurniawan, R. Sennrich, E. Hovy, E. Vylomova (2026). "CommonMorph: Participatory Morphological Documentation Platform." arXiv:2604.04515.

Dialects and language identification:

* S. Ahmadi, D. Q. Jaff, M. M. Ibn Alam, A. Anastasopoulos (2024). "Language and Speech Technology for Central Kurdish Varieties." *Proc. LREC-COLING 2024* (arXiv:2403.01983). Data: <https://github.com/sinaahmadi/CORDI>. Used in [chapter 23](23-ckb-written-standard.md#regional-variation) and for `ەوانێ`/`ەو` in [chapter 10](10-ckb-verbs.md).
* H. Hassani & D. Medjedovic (2016). "Automatic Kurdish Dialects Identification." *Computer Science & Information Technology* (CS & IT), pp. 61–78, doi:10.5121/csit.2016.60307.
* KurdishLID, fastText models for `ku`, `ckb`, `sdh`, `hac`, `zza` (MIT), and KurdishLexicography (CC BY-NC-SA 4.0), <https://github.com/sinaahmadi>. Used in [chapter 5](05-language-identification.md#other-kurdish-varieties).

Corpora, text processing and surveys (read for background; no rule changed because of them):

* H. Veisi, M. MohammadAmini, H. Hosseini (2020). "Toward Kurdish language processing: Experiments in collecting and processing the AsoSoft text corpus." *Digital Scholarship in the Humanities* 35(1), pp. 176–193.
* S. Ahmadi, H. Hassani, D. Q. Jaff (2022). "Leveraging Multilingual News Websites for Building a Kurdish Parallel Corpus." *ACM TALLIP* 21(5), article 99, doi:10.1145/3511806.
* S. Ahmadi & M. Masoud (2020). "Towards Machine Translation for the Kurdish Language." *Proc. LoResMT 2020*.
* A. A. Jaf & S. Koç Kayhan (2021). "A Brief Overview of Kurdish Natural Language Processing." *Proc. WIIS 2021*, Chisinau.
* S. Ahmadi (2021). "On the Current State of Kurdish Language Processing." Slides, ICKL-5, Graz.
* H. Hassani (2017). "A Method for Proper Noun Extraction in Kurdish." *SLATE 2017*, OASIcs.
* H. K. Hamarashid, S. M. Saeed, T. A. Rashid (2020). Next-word prediction for Kurdish. *Neural Computing and Applications*, doi:10.1007/s00521-020-05245-3.
* T. A. Tofiq, K. O. Aziz, R. A. Teimoor, D. S. Abdulla, A. M. Maroof, H. Karem (2024). "Common Typing Mistakes in Kurdish Using 'Kurdish Central' Keyboard." *Proc. ICICT 2024*, LNNS 1004, pp. 407–413.
* K. M. Awlla & H. Veisi (2022). "Central Kurdish Sentiment Analysis Using Deep Learning." *JUAPS* 16(2), pp. 119–130.
* H. A. Shekhani & D. Q. Jaff (2023). "Grammatical Metaphor in Political Discourse in the Central Kurdish Language." *JUHD*, pp. 131–141.
* M. Azzat, K. Jacksi, I. Ali (2023). "The Kurdish Language Corpus: State of the Art." *Science Journal of the University of Zakho* 11(1), doi:10.25271/sjuoz.2022.11.1.1123.
* Hatwan Khalid (2022). *Learn LaTeX Kurdish*, V01.

Speech and pronunciation (checked against [chapters 8](08-ckb-phonology-ipa.md) and [12](12-kmr-phonology-ipa.md); none gives a full phoneme or grapheme-to-sound table):

* H. Hassani & R. Kareem (2011). "Kurdish Text-to-Speech (KTTS)." *Proc. IWIPS 2011*, pp. 79–85.
* A. A. Abdullah & H. Veisi (2022). "Central Kurdish Automatic Speech Recognition using Deep Learning." *JUAPS* 16(2), pp. 108–118, doi:10.37652/juaps.2022.176500.
* A. A. Abdullah, S. Tabibian, H. Veisi, A. Mahmudi (2026). "Advancing Low-Resource Speech Recognition: A Comprehensive Study of Fine-Tuning Strategies for Northern Kurdish using Whisper Transformers." Research Square preprint, doi:10.21203/rs.3.rs-9531745/v1.
* M. Mohammadamini, M. Shamsi, M. Tahon (2026). "Central Kurdish Text-to-Speech and Its Application in Speech-to-Text Translation." *Proc. LREC 2026*.
* M. Mohammadamini, D. Q. Jaff, J. Crego, M. Tahon, A. Laurent (2026). "English to Central Kurdish Speech Translation: Corpus Creation, Evaluation, and Orthographic Standardization." arXiv:2604.00613.

## The logo

The logo is a deq sign (the tree-of-life figure) with the sun of the flag of Kurdistan. Its story and its sources on deq, the flag and the word *roj* are in [assets/brand/README.md](../assets/brand/README.md#sources).

<!-- nav:bottom -->
---
[← Glossary](20-glossary.md) · [⌂ Contents](00-index.md) · [Sentence structure →](22-sentence-structure.md)
<!-- nav:bottom -->
