"""Stage 6: flatten the build outputs into a Kaggle-ready lexical dataset.

Reads ``output/<lang>/`` (stage 4) and the cached lexicon (stage 1) and writes
``output/kaggle/``:

* ``kurdish_words_<lang>.csv`` / ``.parquet`` - one row per surface form, every
  morphological feature in its own column, lemma-level information repeated
  on each form so a single file is self-contained;
* ``kurdish_lemmas_<lang>.csv`` / ``.parquet`` - one row per lemma;
* ``kurdish_spelling_variants_ckb.csv`` - non-standard spellings -> standard form;
* ``kurdish_lexicon.sqlite`` - all of the above as tables with indexes;
* ``README.md`` (data card), ``dataset-metadata.json`` (Kaggle API: file and column
  descriptions, provenance) and ``dataset-cover-image.png``.

Definitions come from the monolingual lexicon and are therefore written in
Northern Kurdish for both varieties. They are cleaned: placeholders dropped,
"variant of" / "see" cross-references moved to their own columns, quoted
citations, URLs and deny-listed tokens cut off.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import sqlite3
import time
from collections import defaultdict
from pathlib import Path

from ..config import Config
from .builder import SKIP_POS, Dialect

# morph_meta key -> column; anything not listed lands in ``other_features``
FEATURE_COLUMNS = {
    "gender": "gender", "number": "number", "case": "case", "definite": "definiteness",
    "ezafe": "ezafe", "person": "person", "enclitic": "enclitic", "agent": "agent", "agreement": "agreement",
    "tense": "tense", "aspect": "aspect", "mood": "mood", "voice": "voice", "polarity": "polarity",
    "transitivity": "transitivity", "alignment": "alignment", "form": "verb_form",
    "present_stem": "present_stem", "past_stem": "past_stem", "derivation": "derivation", "degree": "degree",
    "postposition": "postposition", "additive": "additive", "demonstrative": "demonstrative",
    "prontype": "pron_type", "numtype": "num_type", "adptype": "adp_type", "deixis": "deixis",
}
BOOL_FEATURES = {"ezafe", "additive", "demonstrative"}
# Kaggle cover (560x280; the thumbnail is the centre 280x280), source: assets/brand/kaggle/kaggle-cover.svg
COVER_IMAGE = Path(__file__).resolve().parents[2] / "assets" / "brand" / "kaggle" / "dataset-cover-image.png"
GOLD_TAGS = {"lexicon", "lexicon-form", "core", "dictionary"}

WORD_COLUMNS = [
    "id", "lang", "word", "lemma", "is_lemma", "upos", "segmentation", "morpheme_count",
    "script_arabic", "script_latin", "ipa", "ipa_reference", "syllables", "syllable_count", "char_length",
    *dict.fromkeys(FEATURE_COLUMNS.values()), "other_features",
    "definition_kmr", "variant_of", "see_also", "nonstandard_spellings",
    "attested", "frequency", "freq_per_million", "zipf", "frequency_rank",
    "lemma_frequency", "lemma_form_count", "source_count", "sources", "quality_tier", "confidence",
]
LEMMA_COLUMNS = [
    "id", "lang", "lemma", "upos", "script_arabic", "script_latin", "ipa", "ipa_reference", "syllables",
    "syllable_count", "gender", "transitivity", "present_stem", "past_stem",
    "definition_kmr", "variant_of", "see_also", "frequency", "zipf", "form_count", "forms_sample", "sources",
]
INT_COLUMNS = {"morpheme_count", "syllable_count", "char_length", "frequency", "frequency_rank",
               "lemma_frequency", "lemma_form_count", "source_count", "form_count"}
FLOAT_COLUMNS = {"freq_per_million", "zipf", "confidence"}
BOOL_COLUMNS = {"is_lemma", "attested", *(FEATURE_COLUMNS[k] for k in BOOL_FEATURES)}


def _log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------------------
# Definitions
# ---------------------------------------------------------------------------

_PLACEHOLDER = "nehatiye nivîsîn"
_VARIANT = re.compile(r"^Guhartoyeke\s+([^.;,:(]+?)\s*(?:[.;,:(]|$)")
_SEE = re.compile(r"^Binêre\s+([^.;,:(]+?)\s*(?:[.;,:(]|$)")
# a lower-case definition followed by a capitalised example sentence
_EXAMPLE = re.compile(r"(?<=[a-zçêîşû,)])\s+(?=[A-ZÇÊÎŞÛ])")
# an Arabic-script sentence of three or more words (ckb usage example)
_ARABIC_EXAMPLE = re.compile(r"\s[\u0600-\u06FF\u200c]+(?:\s+[\u0600-\u06FF\u200c]+){2,}\s*[.!?؟]")
_CITATION = re.compile(r"[“\"«―~]|\b(?:1[5-9]|20)\d\d\b|\bhttps?\b|www\.|\(Tu dikarî tarîxa|\S+\.(?:com|org|net|info|tv|krd|tr)\b", re.I)


def clean_definition(gloss: str, deny: set[str] = frozenset(), headword: str = "", max_len: int = 300) -> tuple[str, str, str]:
    """Return ``(definition, variant_of, see_also)`` for one raw lexicon gloss."""
    g = " ".join((gloss or "").split())
    if not g or _PLACEHOLDER in g:
        return "", "", ""
    if m := _VARIANT.match(g):
        return "", m.group(1), ""
    if m := _SEE.match(g):
        return "", "", m.group(1)
    if m := _CITATION.search(g):
        g = g[: m.start()]
    if m := _ARABIC_EXAMPLE.search(g):
        g = g[: m.start()]
    stem = headword.lower()[: max(3, len(headword) - 2)]
    for m in _EXAMPLE.finditer(g) if stem else ():
        sent = re.match(r"[^.!?]*[.!?]", g[m.end():])
        if sent and len(sent.group().split()) >= 3 and stem in sent.group().lower():
            g = g[: m.start()]
            break
    low = g.lower()
    cut = min((low.find(t) for t in deny if len(t) >= 4 and t in low), default=-1)
    if cut >= 0:
        g = g[:cut]
    g = re.sub(r"\(\s+", "(", g)
    g = re.sub(r"\s+([).,;:!?])", r"\1", g)
    g = g.strip(" ,;:-").rstrip(" ,;:-(")
    while g.count(")") > g.count("("):
        i = g.find(")")
        g = (g[:i] + g[i + 1 :]).strip()
    if len(g) > max_len:
        g = g[:max_len].rsplit(" ", 1)[0] + "…"
    return (g, "", "") if any(c.isalpha() for c in g) else ("", "", "")


def load_lexicon_info(path: Path, d: Dialect, deny: set[str]) -> dict[str, dict]:
    """normalised headword -> definitions, cross-references, reference IPA, verb stems."""
    info: dict[str, dict] = defaultdict(lambda: {"defs": [], "variant_of": [], "see_also": []})
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec["lang"] != d.lang or rec["pos"] in SKIP_POS or rec["pos"].endswith("_FORM"):
                continue
            hw = rec.get("headword") or rec["title"]
            if " " in hw.strip() or not (word := d.norm(hw)):
                continue
            e = info[word]
            definition, variant, see = clean_definition(rec.get("gloss", ""), deny, hw)
            for key, val in (("defs", definition), ("variant_of", variant), ("see_also", see)):
                if val and val not in e[key]:
                    e[key].append(val)
            if rec.get("ipa") and "ipa_reference" not in e:
                e["ipa_reference"] = rec["ipa"][0].strip("/[] ")
            for k in ("present_stem", "past_stem"):
                if rec.get(k) and k not in e:
                    e[k] = rec[k]
    return info


# ---------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------


def _syllabifier(lang: str):
    if lang == "ckb":
        from ..skills_ckb.phonology_ipa import syllables
    else:
        from ..skills_kmr.phonology_ipa import syllables
    return syllables


def _zipf(freq: int, total: int) -> float | None:
    return round(math.log10(freq * 1e9 / total), 3) if freq and total else None


def _tier(sources: set[str], word: str, lemma: str) -> str:
    """gold = attested in a curated lexicon; silver = analysed onto a known lemma or bilingual entry; bronze = corpus only."""
    if sources & GOLD_TAGS:
        return "gold"
    if "corpus" not in sources and (lemma != word or "bilingual" in sources):
        return "silver"
    return "bronze"


def _scripts(lang: str, word: str, translit: str) -> tuple[str, str]:
    return (word, translit) if lang == "ckb" else (translit, word)


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_report(cfg: Config, lang: str) -> dict:
    path = cfg.output_dir / lang / f"build_report_{lang}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_rows(cfg: Config, lang: str) -> tuple[list[dict], list[dict], list[dict]]:
    d = Dialect(lang)
    src = cfg.output_dir / lang
    words = _read_csv(src / f"clean_wordlist_{lang}.csv")
    if not words:
        raise FileNotFoundError(f"{src}/clean_wordlist_{lang}.csv missing - run the build stage first")
    lemmas = _read_csv(src / f"lemmas_{lang}.csv")
    variants = _read_csv(src / f"spelling_variants_{lang}.csv")
    total = build_report(cfg, lang).get("corpus_tokens") or sum(int(r["frequency"]) for r in words)
    info = load_lexicon_info(cfg.cache_dir / "lexicon_wiki.jsonl", d, cfg.deny_tokens)
    syllables = _syllabifier(lang)

    def lex(lemma: str) -> dict:
        return info.get(d.norm(lemma)) or {}

    def syl(w: str) -> list[str]:
        try:
            return syllables(d.norm(w))
        except Exception:  # G2P is total on validated words; stay robust on odd proper nouns
            return []

    by_standard: dict[str, list[str]] = defaultdict(list)
    for v in variants:
        by_standard[v["standard"]].append(v["variant"])
    lemma_stats = {r["lemma"]: r for r in lemmas}

    out_words = []
    for rank, r in enumerate(words, 1):
        meta = json.loads(r["morph_meta"])
        seg = meta.pop("seg", r["grapheme"])
        meta.pop("gloss", None)
        row = {c: None for c in WORD_COLUMNS}
        w, lemma = r["grapheme"], r["lemma"]
        sy = syl(w)
        e = lex(lemma)
        is_lemma = d.norm(w) == d.norm(lemma)
        srcs = set(r["sources"].split(",")) - {""}
        freq = int(r["frequency"])
        row.update(
            id=f"{lang}-w{rank:07d}", lang=lang, word=w, lemma=lemma, is_lemma=is_lemma, upos=r["pos"],
            segmentation=seg, morpheme_count=seg.count("+") + 1, ipa=r["ipa"],
            ipa_reference=e.get("ipa_reference") if is_lemma else None,
            syllables=".".join(sy) or None, syllable_count=len(sy) or None, char_length=len(w),
            definition_kmr=" | ".join(e.get("defs", [])[:3]) or None,
            variant_of=", ".join(e.get("variant_of", [])) or None,
            see_also=", ".join(e.get("see_also", [])) or None,
            nonstandard_spellings=", ".join(by_standard.get(w, [])[:10]) or None,
            attested=freq > 0, frequency=freq, freq_per_million=round(freq * 1e6 / total, 4), zipf=_zipf(freq, total),
            frequency_rank=rank, source_count=len(srcs), sources=",".join(sorted(srcs)),
            quality_tier=_tier(srcs, w, lemma), confidence=float(r["confidence"]),
        )
        row["script_arabic"], row["script_latin"] = _scripts(lang, w, r["translit"])
        if ls := lemma_stats.get(lemma):
            row["lemma_frequency"], row["lemma_form_count"] = int(ls["frequency"]), int(ls["forms"])
        other = []
        for k, v in sorted(meta.items()):
            if k in FEATURE_COLUMNS:
                row[FEATURE_COLUMNS[k]] = (v == "yes") if k in BOOL_FEATURES else v
            else:
                other.append(f"{k}={v}")
        for k in BOOL_FEATURES:
            row[FEATURE_COLUMNS[k]] = bool(row[FEATURE_COLUMNS[k]])
        row["other_features"] = "|".join(other) or None
        out_words.append(row)

    forms_of: dict[str, list[str]] = defaultdict(list)
    for row in out_words:  # already frequency-sorted
        if len(forms_of[row["lemma"]]) < 8:
            forms_of[row["lemma"]].append(row["word"])
    out_lemmas = []
    for i, r in enumerate(lemmas, 1):
        lemma = r["lemma"]
        e = lex(lemma)
        sy = syl(lemma)
        row = {
            "id": f"{lang}-l{i:06d}", "lang": lang, "lemma": lemma, "upos": r["pos"], "ipa": r["ipa"],
            "ipa_reference": e.get("ipa_reference"), "syllables": ".".join(sy) or None,
            "syllable_count": len(sy) or None, "gender": r["gender"] or None, "transitivity": r["transitivity"] or None,
            "present_stem": e.get("present_stem") if r["pos"] == "VERB" else None,
            "past_stem": e.get("past_stem") if r["pos"] == "VERB" else None,
            "definition_kmr": " | ".join(e.get("defs", [])[:5]) or None,
            "variant_of": ", ".join(e.get("variant_of", [])) or None,
            "see_also": ", ".join(e.get("see_also", [])) or None,
            "frequency": int(r["frequency"]), "zipf": _zipf(int(r["frequency"]), total),
            "form_count": int(r["forms"]), "forms_sample": ", ".join(forms_of.get(lemma, [])) or None,
            "sources": r["sources"],
        }
        row["script_arabic"], row["script_latin"] = _scripts(lang, lemma, r["translit"])
        out_lemmas.append({c: row[c] for c in LEMMA_COLUMNS})

    out_variants = [
        {"lang": lang, "variant": v["variant"], "standard": v["standard"],
         "variant_frequency": int(v["variant_frequency"]), "standard_frequency": int(v["standard_frequency"])}
        for v in variants
    ]
    return out_words, out_lemmas, out_variants


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


def _write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: ("true" if v is True else "false" if v is False else v) for k, v in r.items()})


def _arrow_type(col: str):
    import pyarrow as pa

    if col in INT_COLUMNS:
        return pa.int64()
    if col in FLOAT_COLUMNS:
        return pa.float64()
    if col in BOOL_COLUMNS:
        return pa.bool_()
    return pa.string()


def _write_parquet(path: Path, rows: list[dict], cols: list[str]) -> bool:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        return False
    schema = pa.schema([(c, _arrow_type(c)) for c in cols])
    pq.write_table(pa.Table.from_pylist(rows, schema=schema), path, compression="zstd")
    return True


def _sql_type(col: str) -> str:
    return "INTEGER" if col in INT_COLUMNS | BOOL_COLUMNS else "REAL" if col in FLOAT_COLUMNS else "TEXT"


def _write_sqlite(path: Path, tables: dict[str, tuple[list[str], list[dict]]]) -> None:
    path.unlink(missing_ok=True)
    con = sqlite3.connect(path)
    for name, (cols, rows) in tables.items():
        if not rows:
            continue
        pk = " PRIMARY KEY" if cols[0] == "id" else ""
        con.execute(f"CREATE TABLE {name} ({', '.join(f'"{c}" {_sql_type(c)}' + (pk if i == 0 else '') for i, c in enumerate(cols))})")
        con.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})", ([r[c] for c in cols] for r in rows))
    con.executescript(
        """
        CREATE INDEX idx_words_word ON words(word, lang);
        CREATE INDEX idx_words_lemma ON words(lemma, lang);
        CREATE INDEX idx_words_upos ON words(upos, lang);
        CREATE INDEX idx_lemmas_lemma ON lemmas(lemma, lang);
        """
    )
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# Data card
# ---------------------------------------------------------------------------

COLUMN_DOCS = {
    "id": "stable row id within this release (`<lang>-w<rank>` / `<lang>-l<n>`)",
    "lang": "`ckb` Central Kurdish (Sorani) or `kmr` Northern Kurdish (Kurmanji)",
    "word": "surface form in the variety's standard script (Arabic-based for ckb, Hawar Latin for kmr)",
    "lemma": "dictionary form",
    "is_lemma": "the form is its own lemma",
    "upos": "Universal Dependencies part-of-speech tag",
    "segmentation": "morpheme segmentation, morphemes joined by `+`",
    "morpheme_count": "number of morphemes in `segmentation`",
    "script_arabic": "the word in Kurdish Arabic script (original for ckb, transliterated for kmr)",
    "script_latin": "the word in Hawar Latin script (original for kmr, transliterated for ckb)",
    "ipa": "broad IPA transcription generated by the rule-based G2P; `(ɯ)` marks an unwritten epenthetic vowel",
    "ipa_reference": "independent IPA transcription from the lexicon, when it has one (lemma rows only)",
    "syllables": "IPA syllables joined by `.`",
    "syllable_count": "number of syllables",
    "char_length": "length of `word` in Unicode code points",
    "gender": "grammatical gender `f`, `m` or `f|m` (kmr)",
    "number": "`sg` / `pl`",
    "case": "`dir` direct, `obl` oblique, `voc` vocative (kmr)",
    "definiteness": "`def` definite / `ind` indefinite",
    "ezafe": "carries the ezafe (izafe) linker",
    "person": "person/number of verb agreement; syncretic forms list every reading (`2pl|3pl`; kmr `pl` = any plural)",
    "enclitic": "pronominal enclitic attached to the word (ckb), `3sg|ezafe` where ambiguous",
    "agent": "agent marker of a past transitive verb (ckb ergative pattern)",
    "agreement": "whether the verb agrees with the `subject` or `object` (kmr split ergativity)",
    "tense": "`present`, `past`, `present_perfect`, `past_perfect`, `fut`",
    "aspect": "`perfective` / `progressive`",
    "mood": "`indicative`, `subjunctive`, `imperative`, …",
    "voice": "`passive` when marked",
    "polarity": "`neg` for negated forms",
    "transitivity": "`transitive` / `intransitive`",
    "alignment": "`ergative` / `accusative` alignment of the verb form",
    "verb_form": "non-finite form: `infinitive`, `past_participle`, `passive_participle`",
    "present_stem": "present stem of the verb",
    "past_stem": "past stem of the verb",
    "derivation": "derivational suffix type: `abstract`, `agent`, `adverbial`, `place`, …",
    "degree": "`cmp` comparative / `sup` superlative",
    "postposition": "attached postposition/circumposition part (ckb `-da`, `-ewe`, `-ra`)",
    "additive": "carries the additive clitic (ckb `-îş`)",
    "demonstrative": "inflected with a demonstrative (kmr)",
    "pron_type": "pronoun type (`int`, `ind`, `tot`, `neg`, …)",
    "num_type": "`card` cardinal / `ord` ordinal",
    "adp_type": "`prep` / `post`",
    "deixis": "`proximal` / `distal`",
    "other_features": "rare features as `key=value` pairs separated by `|`",
    "definition_kmr": "lemma definition(s) in Northern Kurdish, senses separated by ` | `",
    "variant_of": "the lemma is listed as a spelling variant of this word",
    "see_also": "cross-reference to a related or preferred headword",
    "nonstandard_spellings": "observed non-standard spellings that map to this word (ckb)",
    "attested": "the form occurs in the corpus (false = generated from a lexicon paradigm table only)",
    "frequency": "occurrences in the reference corpus",
    "freq_per_million": "frequency per million corpus tokens",
    "zipf": "Zipf scale frequency, log10(per-billion frequency)",
    "frequency_rank": "1 = most frequent form",
    "lemma_frequency": "sum of the frequencies of all forms of the lemma",
    "lemma_form_count": "number of forms of the lemma in this dataset",
    "form_count": "number of forms of the lemma in the words table",
    "forms_sample": "up to 8 most frequent forms of the lemma",
    "source_count": "number of independent source categories attesting the form",
    "sources": "source categories: `lexicon`, `lexicon-form`, `dictionary`, `bilingual`, `core` (hand-authored tables), `encyclopedia`, `news`, `web`, `corpus` (corpus-only lemma)",
    "quality_tier": "`gold` curated lexicon/dictionary · `silver` analysed onto a known lemma · `bronze` corpus evidence only",
    "confidence": "0–1 score combining lexicon membership, dictionary membership, frequency and source spread",
}


def write_data_card(path: Path, stats: dict[str, dict], links: dict[str, str] | None = None) -> None:
    lines = [
        "# Kurdish Lexicon: Sorani (ckb) & Kurmanji (kmr)",
        "",
        "Word-level lexical database for **Central Kurdish (Sorani)** and **Northern Kurdish (Kurmanji)**: "
        "every row is one validated surface form with its lemma, part of speech, morpheme segmentation, "
        "inflectional features, IPA, syllables, both scripts, definitions and corpus frequency.",
        "",
    ]
    if links:
        lines += ["## Links", "", *(f"- **{name}:** {url}" for name, url in links.items()), ""]
    lines += [
        "## Files",
        "",
        "| file | rows | content |",
        "|---|---|---|",
    ]
    for lang, s in stats.items():
        lines.append(f"| `kurdish_words_{lang}.csv` / `.parquet` | {s['words']:,} | one row per word form |")
        lines.append(f"| `kurdish_lemmas_{lang}.csv` / `.parquet` | {s['lemmas']:,} | one row per lemma |")
        if s["variants"]:
            lines.append(f"| `kurdish_spelling_variants_{lang}.csv` | {s['variants']:,} | non-standard spelling → standard form |")
    lines += [
        "| `kurdish_lexicon.sqlite` | all | tables `words`, `lemmas`, `spelling_variants` with a `lang` column |",
        "",
        "## Quick start",
        "",
        "```python",
        "import pandas as pd",
        'words = pd.read_parquet("kurdish_words_kmr.parquet")',
        'nouns = words[(words.upos == "NOUN") & (words.quality_tier == "gold")]',
        'words[words.lemma == "dîtin"][["word", "tense", "person", "polarity", "ipa"]]',
        "```",
        "",
        "```sql",
        "-- sqlite3 kurdish_lexicon.sqlite",
        "SELECT word, segmentation, ipa FROM words WHERE lang = 'ckb' AND lemma = 'کتێب' ORDER BY frequency DESC;",
        "```",
        "",
        "## How it was built",
        "",
        "1. Word frequencies were counted from encyclopedia, news and web text ("
        + ", ".join(f"{lang}: {s['tokens'] / 1e6:.0f} M tokens" for lang, s in stats.items())
        + ") after Unicode normalisation and per-sentence language identification (Zazaki, Gorani/Hawrami, "
        "Persian, Arabic and Turkish text is filtered out).",
        "2. Candidate forms from a monolingual lexicon, dictionaries and the corpus pass an orthographic validator "
        "for each variety (illegal letters, legacy encodings, broken sequences).",
        "3. A rule-based morphological analyzer segments each form and attaches it to a known lemma; forms that "
        "match no known lemma are kept only if frequent and attested in several independent source categories.",
        "4. IPA, syllables and transliteration are generated by rule-based grapheme-to-phoneme modules "
        "(mean similarity to independent reference transcriptions: "
        + ", ".join(f"{lang} {s['ipa_agreement'] * 100:.1f} %" for lang, s in stats.items() if s.get("ipa_agreement"))
        + ").",
        "",
        "Rejected forms (foreign words, typos, encoding damage, rare unknown stems) are not included.",
        "",
        "## Columns (words table)",
        "",
        "| column | description |",
        "|---|---|",
        *(f"| `{c}` | {COLUMN_DOCS.get(c, '')} |" for c in WORD_COLUMNS),
        "",
        "Lemma table columns that are not in the words table: "
        + ", ".join(f"`{c}` ({COLUMN_DOCS[c]})" for c in LEMMA_COLUMNS if c not in WORD_COLUMNS),
        "",
        "Empty cells mean *not applicable / not marked*, not *unknown value*.",
        "",
        "## Caveats",
        "",
        "- Features come from a rule-based analyzer; the first reading is kept for ambiguous forms. Use "
        "`quality_tier` / `confidence` to trade coverage for precision.",
        "- Definitions are in Northern Kurdish for both varieties and cover mainly Kurmanji lemmas.",
        "- `frequency` reflects written news/encyclopedia/web register.",
        "",
        "## Licence",
        "",
        "CC BY-SA 4.0 — the definitions and part of the lexicon derive from openly licensed share-alike lexical data.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


KAGGLE_TITLE = "Kurdish Lexicon: Sorani & Kurmanji Word Database"  # Kaggle: 6-50 characters
KAGGLE_SUBTITLE = "Sorani & Kurmanji words: morphology, IPA, syllables, definitions, frequency"  # 20-80


VARIANT_COLUMNS = ["lang", "variant", "standard", "variant_frequency", "standard_frequency"]
LEMMA_DOCS = {
    "id": "stable lemma id within this release (`<lang>-l<n>`)",
    "upos": "Universal Dependencies part-of-speech tag of the lemma",
    "ipa": "broad IPA transcription of the lemma generated by the rule-based G2P",
    "ipa_reference": "independent IPA transcription from the lexicon, when it has one",
    "frequency": "sum of the corpus frequencies of all forms of the lemma",
    "zipf": "Zipf scale frequency of the lemma, log10(per-billion frequency)",
    "sources": "source categories attesting any form of the lemma",
}
VARIANT_DOCS = {
    "lang": "`ckb` Central Kurdish (Sorani)",
    "variant": "non-standard spelling observed in the corpus (confusable letters, missing ZWNJ, legacy ه for ە, …)",
    "standard": "standard spelling it maps to; present in the words table",
    "variant_frequency": "corpus frequency of the non-standard spelling",
    "standard_frequency": "corpus frequency of the standard spelling",
}
PROVENANCE = (
    "Sources (generic categories; every row lists the categories that attest it in `sources`):\n"
    "1. lexicon - an openly licensed, community-edited monolingual Kurdish lexicon: headwords, part of speech, "
    "gender, transitivity, verb stems, declension tables, definitions and reference IPA.\n"
    "2. dictionary / bilingual - monolingual dictionary headwords, and Kurdish equivalents from bilingual "
    "dictionaries kept only when attested in the corpus.\n"
    "3. encyclopedia / news / web - a Central and Northern Kurdish text corpus{tokens}, used for frequencies and "
    "attestation.\n"
    "4. core - hand-authored reference tables of function words and core verbs.\n\n"
    "Collection methodology: text was Unicode-normalised (legacy encodings, Arabic vs Kurdish letters, ZWNJ, "
    "diacritics), split into sentences and filtered by language identification (Zazaki, Gorani/Hawrami, Persian, "
    "Arabic, Turkish and English removed). Candidate forms passed an orthographic validator for each variety, were "
    "segmented by a rule-based morphological analyzer and attached to a known lemma; unknown stems were kept only "
    "if frequent and attested in at least two independent source categories. IPA, syllables and transliteration "
    "come from rule-based grapheme-to-phoneme modules; definitions were cleaned of placeholders, citations, URLs "
    "and example sentences. Built with the zimankit pipeline."
)


def _fields(cols: list[str], docs: dict[str, str]) -> list[dict]:
    return [{"name": c, "description": docs.get(c) or COLUMN_DOCS[c]} for c in cols]


def kaggle_resources(stats: dict[str, dict]) -> list[dict]:
    """File descriptions and column descriptors for every published file."""
    name = {"ckb": "Central Kurdish (Sorani, Arabic script)", "kmr": "Northern Kurdish (Kurmanji, Latin script)"}
    res = []
    for lang, s in stats.items():
        words = (f"{name[lang]}: one row per validated word form ({s.get('words', 0):,} rows) with lemma, POS, "
                 "segmentation, inflectional features, IPA, syllables, both scripts, definition and corpus frequency.")
        lemmas = (f"{name[lang]}: one row per lemma ({s.get('lemmas', 0):,} rows) with POS, IPA, gender, "
                  "transitivity, verb stems, definitions, total frequency and its most frequent forms.")
        for ext, fmt in ((".csv", "CSV, UTF-8"), (".parquet", "Parquet, typed columns")):
            res.append({"path": f"kurdish_words_{lang}{ext}", "description": f"{words} {fmt}.",
                        "schema": {"fields": _fields(WORD_COLUMNS, {})}})
            res.append({"path": f"kurdish_lemmas_{lang}{ext}", "description": f"{lemmas} {fmt}.",
                        "schema": {"fields": _fields(LEMMA_COLUMNS, LEMMA_DOCS)}})
        if s.get("variants"):
            res.append({"path": f"kurdish_spelling_variants_{lang}.csv",
                        "description": f"{name[lang]}: {s['variants']:,} non-standard spellings mapped to their standard form.",
                        "schema": {"fields": _fields(VARIANT_COLUMNS, VARIANT_DOCS)}})
    res.append({"path": "kurdish_lexicon.sqlite",
                "description": "SQLite database with every table above for both varieties: `words`, `lemmas` and "
                               "`spelling_variants`, each with a `lang` column and indexes on word, lemma and upos."})
    res.append({"path": "README.md", "description": "Data card: files, build method, column reference, caveats and licence."})
    return res


def write_kaggle_metadata(path: Path, stats: dict[str, dict], dataset_id: str, description: str = "") -> None:
    tokens = [f"{lang}: {s['tokens'] / 1e6:.0f} M tokens" for lang, s in stats.items() if s.get("tokens")]
    meta = {
        "title": KAGGLE_TITLE,
        "id": dataset_id,
        "subtitle": KAGGLE_SUBTITLE,
        "description": description,
        "keywords": ["languages", "linguistics", "nlp", "text"],
        "licenses": [{"name": "CC-BY-SA-4.0"}],
        "userSpecifiedSources": PROVENANCE.format(tokens=f" ({', '.join(tokens)})" if tokens else ""),
        "resources": kaggle_resources(stats),
    }
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage entry point
# ---------------------------------------------------------------------------


def export(cfg: Config, langs: list[str]) -> dict:
    out = cfg.output_dir / "kaggle"
    out.mkdir(parents=True, exist_ok=True)
    all_words, all_lemmas, all_variants, stats = [], [], [], {}
    variant_cols = VARIANT_COLUMNS
    for lang in langs:
        t0 = time.time()
        words, lemmas, variants = build_rows(cfg, lang)
        _write_csv(out / f"kurdish_words_{lang}.csv", words, WORD_COLUMNS)
        _write_csv(out / f"kurdish_lemmas_{lang}.csv", lemmas, LEMMA_COLUMNS)
        if variants:
            _write_csv(out / f"kurdish_spelling_variants_{lang}.csv", variants, variant_cols)
        parquet = _write_parquet(out / f"kurdish_words_{lang}.parquet", words, WORD_COLUMNS)
        _write_parquet(out / f"kurdish_lemmas_{lang}.parquet", lemmas, LEMMA_COLUMNS)
        stats[lang] = {"words": len(words), "lemmas": len(lemmas), "variants": len(variants),
                       "with_definition": sum(1 for r in lemmas if r["definition_kmr"]), "parquet": parquet}
        report = build_report(cfg, lang)
        stats[lang]["tokens"] = report.get("corpus_tokens", 0)
        stats[lang]["ipa_agreement"] = (report.get("ipa_vs_reference") or {}).get("mean_similarity")
        all_words += words
        all_lemmas += lemmas
        all_variants += variants
        _log(f"[{lang}] export: {len(words)} words, {len(lemmas)} lemmas in {time.time() - t0:.1f}s")
    _write_sqlite(out / "kurdish_lexicon.sqlite", {
        "words": (WORD_COLUMNS, all_words), "lemmas": (LEMMA_COLUMNS, all_lemmas),
        "spelling_variants": (variant_cols, all_variants),
    })
    kaggle = cfg.settings.get("kaggle", {})
    dataset_id = kaggle.get("dataset_id", "YOUR-KAGGLE-USERNAME/kurdish-lexicon")
    links = {"Dataset": f"https://www.kaggle.com/datasets/{dataset_id}"}
    if kaggle.get("source_url"):
        links["Source code, tutorials and grammar tools (zimankit)"] = kaggle["source_url"]
    write_data_card(out / "README.md", stats, links)
    if COVER_IMAGE.exists():
        shutil.copyfile(COVER_IMAGE, out / "dataset-cover-image.png")
    write_kaggle_metadata(out / "dataset-metadata.json", stats, dataset_id, (out / "README.md").read_text(encoding="utf-8"))
    if not all(s["parquet"] for s in stats.values()):
        _log("pyarrow not installed: Parquet files skipped (pip install 'zimankit[kaggle]')")
    _log(f"export written to {out}")
    return stats
