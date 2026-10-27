"""Stage 4: merge lexicon, dictionaries and corpus counts into clean wordlists.

Decision procedure for every candidate surface form (docs/16-lexicon-pipeline.md):

1. **Deny / orthography gate** - deny-listed tokens, non-alphabet characters,
   illegal sequences, foreign letters -> rejected with a reason.
2. **Lexicon gold** - the form is a lexicon lemma, or a lexicon-listed
   inflected form (declension tables / form-of entries): accepted, the
   lexicon's lemma and features are used.
3. **Analysis** - otherwise the dialect analyzer segments the form; it is
   accepted when the analysed lemma is a known lemma (lexicon, dictionary,
   core verb, function word).
4. **Corpus-only lemma** - an unanalysable form is accepted as a new lemma
   only if it is frequent (``min_count_new_lemma``) and attested in several
   independent source categories.
5. **Variants** (Central Kurdish) - a rejected form whose confusable-letter
   respelling is a much more frequent accepted form is logged as a
   non-standard spelling of it, not added to the wordlist.

Every accepted row gets IPA and transliteration from the phonology skill,
``morph_meta`` from the analysis, and a 0-1 confidence.
"""

from __future__ import annotations

import csv
import json
import math
import multiprocessing as mp
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Config
from ..shared_utils.schema import Analysis, SimpleLexicon
from ..shared_utils.text_helpers import levenshtein
from .harvest import read_freq

SKIP_POS = {"IDIOM", "PROVERB", "LETTER", "AFFIX", "ABBR", "VERB_STEM"}
FORM_POS = {"NOUN_FORM": "NOUN", "VERB_FORM": "VERB", "ADJ_FORM": "ADJ", "PROPN_FORM": "PROPN"}
POS_ORDER = ("NOUN", "VERB", "ADJ", "PROPN", "ADV", "PRON", "NUM", "ADP", "CCONJ", "SCONJ", "DET", "AUX", "PART", "INTJ", "X")


def _log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


@dataclass
class Lemma:
    lemma: str
    pos: set[str] = field(default_factory=set)
    gender: str | None = None
    transitivity: str | None = None
    present_stem: str | None = None
    sources: set[str] = field(default_factory=set)
    ref_ipa: str | None = None
    display: str | None = None  # original casing (proper nouns)


@dataclass
class Row:
    grapheme: str
    lemma: str
    pos: str
    ipa: str
    morph_meta: str
    translit: str
    frequency: int
    sources: str
    confidence: float


# ---------------------------------------------------------------------------
# Dialect plumbing
# ---------------------------------------------------------------------------


class Dialect:
    def __init__(self, lang: str):
        self.lang = lang
        if lang == "ckb":
            from ..skills_ckb import morphology, orthography, phonology_ipa, verbs

            self.norm = orthography.normalize_word
            self.validate = orthography.validate_word
            self.ipa = phonology_ipa.to_ipa
            self.translit = phonology_ipa.to_latin
            self.verbs = verbs
            self.Analyzer = morphology.CkbAnalyzer
            self.fw = morphology.function_words()
        else:
            from ..skills_kmr import morphology, orthography, phonology_ipa, translit, verbs

            self.norm = orthography.normalize_word
            self.validate = orthography.validate_word
            self.ipa = phonology_ipa.to_ipa
            self.translit = translit.to_arabic
            self.verbs = verbs
            self.Analyzer = morphology.KmrAnalyzer
            self.fw = morphology.function_words()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_lexicon(path: Path, d: Dialect) -> tuple[dict[str, Lemma], dict[str, list[tuple[str, str, dict]]]]:
    lemmas: dict[str, Lemma] = {}
    forms: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec["lang"] != d.lang or rec["pos"] in SKIP_POS:
                continue
            hw = rec.get("headword") or rec["title"]
            if " " in hw.strip():
                continue
            word = d.norm(hw)
            if not word:
                continue
            if rec["pos"] in FORM_POS:
                lemma = rec.get("lemma")
                if lemma and " " not in lemma:
                    forms[word].append((d.norm(lemma), FORM_POS[rec["pos"]], rec.get("features", {})))
                continue
            e = lemmas.setdefault(word, Lemma(word))
            e.pos.add(rec["pos"])
            e.sources.add("lexicon")
            if rec["pos"] == "PROPN" and d.lang == "kmr":
                e.display = hw
            if rec.get("gender") and not e.gender:
                e.gender = rec["gender"]
            if rec.get("transitivity") and rec["pos"] == "VERB":
                e.transitivity = rec["transitivity"]
            if rec.get("present_stem") and rec["pos"] == "VERB":
                e.present_stem = d.norm(rec["present_stem"])
            if rec.get("ipa") and not e.ref_ipa:
                e.ref_ipa = rec["ipa"][0]
            for f in rec.get("forms", []):
                fw = d.norm(f["form"])
                if fw and " " not in fw:
                    forms[fw].append((word, rec["pos"], f["features"]))
    return lemmas, forms


def load_dictionary(path: Path, d: Dialect) -> dict[str, tuple[str, set[str], str]]:
    """word -> (pos, tags, role)"""
    out: dict[str, tuple[str, set[str], str]] = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            lang, word, pos, tags, role, _ = line.rstrip("\n").split("\t")
            if lang != d.lang or role == "expression":
                continue
            prev = out.get(word)
            if prev:
                out[word] = (prev[0] or pos, prev[1] | set(tags.split(",")), prev[2] if prev[2] == "headword" else role)
            else:
                out[word] = (pos, set(tags.split(",")), role)
    return out


# ---------------------------------------------------------------------------
# Parallel analysis
# ---------------------------------------------------------------------------

_G: dict = {}


def _analyze_chunk(words: list[str]) -> list[tuple[str, list[Analysis] | None, list[str]]]:
    an = _G["analyzer"]
    d: Dialect = _G["dialect"]
    out = []
    for w in words:
        problems = d.validate(w)
        if problems:
            out.append((w, None, problems))
            continue
        res = an.analyze(w, normalized=True)
        out.append((w, res[:4], []))
    return out


def _confidence(in_lex: bool, in_dict: bool, freq: int, n_tags: int, analysed: bool) -> float:
    c = 0.45 * in_lex + 0.15 * in_dict + 0.3 * min(1.0, math.log10(freq + 1) / 4) + 0.05 * min(n_tags, 2)
    if analysed:
        c += 0.05
    return round(min(1.0, c), 3)


def _ipa_similarity(ours: str, ref: str, lang: str = "kmr") -> float:
    """Similarity after neutralising notation differences between transcription traditions."""

    def simp(s: str) -> str:
        s = s.split("→")[-1].strip().strip("/[]")
        s = re.sub(r"[ˈˌ.()ʔ]", "", s)
        for a, b in (("ʤ", "dʒ"), ("ʧ", "tʃ"), ("o̞", "o"), ("e̞", "e"), ("ɑ", "a"), ("ɡ", "g"), ("ɡʷ", "gw"),
                     ("kʰ", "k"), ("tʰ", "t"), ("pʰ", "p"), ("tʃʰ", "tʃ"), ("u̯", "w"), ("i̯", "j"), ("ɘ", "ɯ"), ("ɨ", "ɯ")):
            s = s.replace(a, b)
        if lang == "ckb":
            # the reference writes ە as short a / ɛ and the bizroke as ə
            s = s.replace("ə", "ɯ").replace("ɛ", "æ")
            s = re.sub(r"a(?!ː)", "æ", s)
            s = s.replace("ɾ", "r")
        else:
            s = s.replace("ə", "ɯ").replace("ɪ", "ɯ").replace("ɾ", "r")
        return s


    a, b = simp(ours), simp(ref)
    if not a or not b:
        return 0.0
    return 1 - levenshtein(a, b) / max(len(a), len(b))


def _denied(w: str, deny: set[str]) -> bool:
    """Deny-listed as a whole word, before an apostrophe suffix, or as a long substring."""
    low = w.lower()
    if low in deny or low.split("'", 1)[0] in deny:
        return True
    return any(len(t) >= 6 and t in low for t in deny)


def _propn_display(w: str, lemmas: dict[str, Lemma]) -> str:
    """Capitalised display form; acronyms before an apostrophe are upper-cased (HDP'ê)."""
    if w in lemmas and lemmas[w].display:
        return lemmas[w].display
    if "'" in w:
        stem, suf = w.split("'", 1)
        if not any(c in "aeêiîouû" for c in stem):
            return stem.upper() + "'" + suf
    return w[:1].upper() + w[1:]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(cfg: Config, lang: str) -> dict:
    t0 = time.time()
    d = Dialect(lang)
    s_corpus = cfg.settings["corpus"]
    out_dir = cfg.output_dir / lang
    out_dir.mkdir(parents=True, exist_ok=True)

    lemmas, lex_forms = load_lexicon(cfg.cache_dir / "lexicon_wiki.jsonl", d)
    _log(f"[{lang}] lexicon lemmas={len(lemmas)} forms={len(lex_forms)}")
    dict_cands = load_dictionary(cfg.cache_dir / "dictionary_candidates.tsv", d)
    counts, caps, tags = read_freq(cfg.cache_dir / f"freq_{lang}.tsv", 1)
    _log(f"[{lang}] dictionary candidates={len(dict_cands)} corpus types={len(counts)}")

    # function words and core verbs are always lemmas
    for w, (pos, _) in d.fw.items():
        lemmas.setdefault(w, Lemma(w)).pos.add(pos)
        lemmas[w].sources.add("core")
    core = d.verbs.load_core_verbs()
    for v in core:
        e = lemmas.setdefault(v.infinitive, Lemma(v.infinitive))
        e.pos.add("VERB")
        e.sources.add("core")

    # dictionary words become lemmas when attested (headwords of a monolingual
    # dictionary are trusted without attestation)
    min_dict = cfg.settings["dictionary"]["min_corpus_count"]
    for w, (pos, dtags, role) in dict_cands.items():
        if d.validate(w) or _denied(w, cfg.deny_tokens):
            continue
        if role == "headword" or counts.get(w, 0) >= min_dict:
            e = lemmas.setdefault(w, Lemma(w))
            # dictionary POS hints are noisy: keep open classes only, verbs only for infinitive shapes
            if pos in ("NOUN", "ADJ", "ADV") or (pos == "VERB" and d.verbs.past_stem_of(w)):
                e.pos.add(pos)
            e.sources |= dtags

    # verb index: core verbs + every verb lemma we know
    known = {v.infinitive: v for v in core if not v.preverb}
    verbs = list(core)
    for w, e in lemmas.items():
        if "VERB" in e.pos and w not in known:
            tr = None if e.transitivity is None else e.transitivity == "transitive"
            v = d.verbs.make_verb(w, tr, e.present_stem, "lexicon", known)
            if v is not None:
                verbs.append(v)
    index = d.verbs.FormIndex(verbs)
    _log(f"[{lang}] verbs={len(index.verbs)} verb forms={len(index)}")

    lex = SimpleLexicon(freqs=counts)
    for w, e in lemmas.items():
        for p in e.pos or {"X"}:
            g = e.gender if e.gender in ("f", "m") else None
            lex.add(w, p, g)
    analyzer = d.Analyzer(lex, index)

    # candidate surface forms
    min_count = s_corpus["min_count"]
    cands = set(lemmas) | set(lex_forms) | {w for w, c in counts.items() if c >= min_count}
    cands = sorted(c for c in cands if c)
    _log(f"[{lang}] analysing {len(cands)} candidate forms")
    _G.update(analyzer=analyzer, dialect=d)
    chunks = [cands[i : i + 5000] for i in range(0, len(cands), 5000)]
    results: list[tuple[str, list[Analysis] | None, list[str]]] = []
    ctx = mp.get_context("fork")
    with ctx.Pool(cfg.workers) as pool:
        for part in pool.imap(_analyze_chunk, chunks, chunksize=1):
            results.extend(part)
    _log(f"[{lang}] analysis done")

    rows: list[Row] = []
    rejected: list[tuple[str, int, str]] = []
    pending_variants: list[str] = []
    accepted: dict[str, Row] = {}
    min_new = s_corpus["min_count_new_lemma"]
    min_tags = s_corpus["min_source_tags_new_lemma"]
    propn_ratio = cfg.settings["kmr"]["propn_ratio"]
    lemma_set = set(lemmas)

    for w, alist, problems in results:
        a = alist[0] if alist else None
        freq = counts.get(w, 0)
        wtags = set(tags.get(w, "").split(",")) - {""}
        if _denied(w, cfg.deny_tokens):
            rejected.append((w, freq, "deny-listed token"))
            continue
        if problems:
            rejected.append((w, freq, "; ".join(problems)))
            continue
        if len(w) == 1 and w not in d.fw:
            rejected.append((w, freq, "single letter"))
            continue
        srcs = set(wtags)
        in_dict = w in dict_cands
        feats: dict = {}
        lemma, pos, seg = w, "X", w
        analysed = False
        core_verb_reading = (
            a is not None and a.pos == "VERB" and a.lemma != w and w not in d.fw
            and getattr(index.verbs.get(a.lemma), "source", "") == "core"
        )
        # a POS-less dictionary word that analyses into a known lemma is an inflected form
        posless_inflected = None
        if w in lemmas and not lemmas[w].pos and w not in d.fw:
            def plausible(x: Analysis) -> bool:
                if x.lemma == w or x.lemma not in lemma_set or not lemmas[x.lemma].pos or x.score <= 0:
                    return False
                last = x.segments[-1][0] if len(x.segments) > 1 else ""
                # a one-letter enclitic (م ت ش) is only believable on a stem at least as frequent
                return len(last) >= 2 or last == "ی" or counts.get(x.lemma, 0) >= freq

            posless_inflected = next((x for x in alist or [] if plausible(x)), None)
        if posless_inflected is not None:
            a = posless_inflected
            srcs |= lemmas[w].sources
            lemma, pos, feats, seg = a.lemma, a.pos, dict(a.features), a.segmentation
            analysed = True
        elif w in lemmas and not core_verb_reading:
            e = lemmas[w]
            srcs |= e.sources
            lemma = w
            if w in d.fw:  # closed-class words: the reference table wins over homographs
                pos, fw_feats = d.fw[w]
                feats = dict(fw_feats)
            else:
                pos = "VERB" if ("VERB" in e.pos and w in index.verbs) else next((p for p in POS_ORDER if p in e.pos), "X")
                if a is not None and a.lemma == w:
                    feats = dict(a.features)
                if e.gender and pos in ("NOUN", "PROPN"):
                    feats["gender"] = e.gender
                if e.transitivity and pos == "VERB":
                    feats["transitivity"] = e.transitivity
        elif core_verb_reading:
            lemma, pos, feats, seg = a.lemma, "VERB", dict(a.features), a.segmentation
            srcs |= {"core"}
            analysed = True
        elif w in lex_forms:
            lemma, pos, feats = lex_forms[w][0]
            feats = dict(feats)
            srcs.add("lexicon-form")
            if a is not None and a.lemma == lemma:
                seg = a.segmentation
        elif a is not None and (a.lemma in lemma_set or a.pos == "VERB") and a.score > 0:
            lemma, pos, feats, seg = a.lemma, a.pos, dict(a.features), a.segmentation
            analysed = True
        else:
            n_tags = len(wtags)
            if lang == "kmr" and freq and caps.get(w, 0) / freq >= propn_ratio:
                if freq >= min_new:
                    lemma, pos = w, "PROPN"
                    srcs.add("corpus")
                else:
                    rejected.append((w, freq, "rare proper noun"))
                    continue
            elif freq >= min_new and n_tags >= min_tags:
                lemma = a.lemma if a is not None else w
                pos = a.pos if a is not None else "X"
                feats = dict(a.features) if a is not None else {}
                seg = a.segmentation if a is not None else w
                srcs.add("corpus")
                analysed = a is not None and a.lemma != w
            else:
                pending_variants.append(w)
                continue
        if lang == "kmr" and pos == "PROPN":
            grapheme = _propn_display(w, lemmas)
            lemma = _propn_display(lemma, lemmas)
        else:
            grapheme = w
        meta = {"seg": seg, **{k: v for k, v in feats.items() if v not in (None, "")}}
        row = Row(
            grapheme=grapheme, lemma=lemma, pos=pos, ipa=d.ipa(w),
            morph_meta=json.dumps(meta, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
            translit=d.translit(w), frequency=freq, sources=",".join(sorted(srcs)),
            confidence=_confidence("lexicon" in srcs or "lexicon-form" in srcs or "core" in srcs, in_dict,
                                   freq, len(wtags), analysed),
        )
        accepted[w] = row

    # Central Kurdish spelling variants of accepted forms
    variants: list[tuple[str, str, int, int]] = []
    if lang == "ckb":
        from ..skills_ckb.orthography import spelling_variants

        ratio = cfg.settings["ckb"]["variant_ratio"]
        for w in pending_variants:
            f = counts.get(w, 0)
            best = None
            for v in spelling_variants(w, 32):
                if v in accepted and accepted[v].frequency >= ratio * max(f, 1):
                    if best is None or accepted[v].frequency > accepted[best].frequency:
                        best = v
            if best:
                variants.append((w, best, f, accepted[best].frequency))
            else:
                rejected.append((w, f, "unknown stem (not in lexicon, too rare for a new lemma)"))
    else:
        rejected += [(w, counts.get(w, 0), "unknown stem (not in lexicon, too rare for a new lemma)") for w in pending_variants]

    rows = sorted(accepted.values(), key=lambda r: (-r.frequency, r.grapheme))
    cols = cfg.settings["output"]["csv_columns"]
    with open(out_dir / f"clean_wordlist_{lang}.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(cols)
        for r in rows:
            wr.writerow([getattr(r, c) for c in cols])
    with open(out_dir / f"wordlist_{lang}.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(r.grapheme for r in rows) + "\n")

    # lemma table
    agg: dict[str, dict] = {}
    for r in rows:
        g = agg.setdefault(r.lemma, {"freq": 0, "forms": 0, "pos": Counter(), "sources": set()})
        g["freq"] += r.frequency
        g["forms"] += 1
        g["pos"][r.pos] += 1
        g["sources"] |= set(r.sources.split(","))
    ipa_scores = []
    with open(out_dir / f"lemmas_{lang}.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["lemma", "pos", "ipa", "translit", "gender", "transitivity", "frequency", "forms", "sources"])
        for lemma, g in sorted(agg.items(), key=lambda kv: -kv[1]["freq"]):
            e = lemmas.get(lemma)
            if lemma in d.fw:
                pos = d.fw[lemma][0]
            elif e and "VERB" in e.pos and lemma in index.verbs:
                pos = "VERB"
            else:
                pos = next((p for p in POS_ORDER if e and p in e.pos), g["pos"].most_common(1)[0][0])
            ours = d.ipa(lemma)
            if e and e.ref_ipa and not d.validate(lemma):
                ipa_scores.append(_ipa_similarity(ours, e.ref_ipa, lang))
            gender = (e.gender or "") if e and pos in ("NOUN", "PROPN") else ""
            wr.writerow([lemma, pos, ours, d.translit(lemma), gender,
                         (e.transitivity if e else "") or "", g["freq"], g["forms"], ",".join(sorted(g["sources"] - {""}))])
    with open(out_dir / f"rejected_{lang}.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["grapheme", "frequency", "reason"])
        for r in sorted(rejected, key=lambda x: -x[1])[: cfg.settings["output"]["max_rejected_rows"]]:
            wr.writerow(r)
    if variants:
        with open(out_dir / f"spelling_variants_{lang}.csv", "w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh)
            wr.writerow(["variant", "standard", "variant_frequency", "standard_frequency"])
            wr.writerows(sorted(variants, key=lambda x: -x[2]))
    # small committed samples
    with open(out_dir / f"sample_clean_wordlist_{lang}.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(cols)
        for r in rows[:300]:
            wr.writerow([getattr(r, c) for c in cols])

    reasons = Counter(r[2].split(":")[0].split(";")[0] for r in rejected)
    report = {
        "lang": lang,
        "seconds": round(time.time() - t0, 1),
        "lexicon_lemmas": len(lemmas),
        "lexicon_forms": len(lex_forms),
        "dictionary_candidates": len(dict_cands),
        "corpus_types": len(counts),
        "corpus_tokens": sum(counts.values()),
        "candidates_analysed": len(cands),
        "accepted_forms": len(rows),
        "accepted_lemmas": len(agg),
        "rejected": len(rejected),
        "spelling_variants": len(variants),
        "rejection_reasons": dict(reasons.most_common(15)),
        "pos_distribution": dict(Counter(r.pos for r in rows).most_common()),
        "source_distribution": dict(Counter(s for r in rows for s in r.sources.split(",")).most_common()),
        "ipa_vs_reference": {"n": len(ipa_scores), "mean_similarity": round(sum(ipa_scores) / len(ipa_scores), 3) if ipa_scores else None},
        "verbs_in_index": len(index.verbs),
    }
    with open(out_dir / f"build_report_{lang}.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    _log(f"[{lang}] {len(rows)} forms / {len(agg)} lemmas accepted, {len(rejected)} rejected in {report['seconds']}s")
    return report
