# lexicon — wordlist pipeline

* `wiki_lexicon.py` — parse dictionary-wiki pages (POS, gender, transitivity, stems, declension tables, form-of entries)
* `corpus.py` — parallel LID-filtered frequency counting
* `harvest.py` — stages 1–3 (lexicon, dictionaries, corpus), cached in `cache/`
* `builder.py` — stage 4: gates, analysis, variants, outputs ([docs/16](../../docs/16-lexicon-pipeline.md))
