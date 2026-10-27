# tools — data readers

* `mdx_extractor.py` — in-process `.mdx` reading via `mdict_utils.base.readmdict.MDX`; entry text, POS markers, equivalent splitting. See [docs/03](../../docs/03-data-ingestion.md).
* `zim_cleaner.py` — ZIM iteration (parallel ranges), HTML sanitisation, prose paragraphs, token XML export.
