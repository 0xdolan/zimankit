<!-- nav:top -->
[← Overview and architecture](01-overview.md) · [⌂ Contents](00-index.md) · [Data ingestion: MDX and ZIM →](03-data-ingestion.md)
<!-- nav:top -->

# Getting started

**On this page:** [Install](#install) · [Try the skills](#try-the-skills) · [Build the wordlists](#build-the-wordlists) · [Run the tests](#run-the-tests)

## Install

```bash
cd zimankit
uv venv --python 3.13 .venv            # or: python3 -m venv .venv
uv pip install --python .venv/bin/python mdict-utils libzim pytest
source .venv/bin/activate
```

The linguistic skills need **only the standard library**. `mdict-utils` and `libzim` are needed only for reading `.mdx` / `.zim` data.

## Try the skills

```bash
python -m zimankit analyze کتێبەکەم jinekê
# کتێبەکەم  کتێب  NOUN  کتێب+ەکە+م  STEM+DEF.SG+1SG  {"definite":"def","number":"sg","enclitic":"1sg"}
# jinekê    jin   NOUN  jin+ekê     STEM+INDEF.OBL.F {"definite":"ind","number":"sg","case":"obl","gender":"f"}

python -m zimankit ipa پیاوەکە کتێبەکەم jinekê dîtin
# pjaːwækæ / k(ɯ)teːbækæm / ʒɪnɛkeː / diːtɯn

python -m zimankit ipa --syllables کوردستان          # kuɾ.d(ɯ)s.taːn
python -m zimankit translit کوردستان                  # kurdistan
python -m zimankit translit "zimanê kurdî"            # زمانێ کوردی
python -m zimankit normalize "به‌ڕێوه‌به‌رایه‌تی ئاوی سلێمانی 2015"
python -m zimankit conjugate کردن | head
python -m zimankit conjugate dîtin | grep past
echo "Min tu dîtim." | python -m zimankit ergativity   # agreement_ok: false

python -m zimankit parse "Min pirtûka nû li dibistanê xwend."   # head and relation of each word, see chapter 22
python -m zimankit lid "Ma yew roje şima ra vat ke ziwanê ma zaf rind o"   # zza
python -m zimankit validate صەبر رۆژ کتێب
```

## Build the wordlists

```bash
cp config/sources.example.toml config/sources.local.toml   # then edit the paths
python run_pipeline.py                   # all stages (cached stages are reused)
python run_pipeline.py --stages build    # re-run only the merge step after tuning thresholds
./scripts/build_wordlists.sh             # same, with logging
```

Outputs land in `output/ckb/` and `output/kmr/` (see [Lexicon pipeline](16-lexicon-pipeline.md)).

## Run the tests

```bash
python -m pytest -q
```

<!-- nav:bottom -->
---
[← Overview and architecture](01-overview.md) · [⌂ Contents](00-index.md) · [Data ingestion: MDX and ZIM →](03-data-ingestion.md)
<!-- nav:bottom -->
