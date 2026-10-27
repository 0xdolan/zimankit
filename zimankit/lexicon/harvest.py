"""Pipeline stages 1-3: harvest lexicon entries, dictionary candidates, corpus counts.

All stages write to the cache directory and are restartable: a stage whose
output already exists is skipped unless ``force=True``.
"""

from __future__ import annotations

import json
import os
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from ..config import Config, Source
from ..shared_utils.text_helpers import detect_script
from .corpus import CountResult, Task, plan_text_tasks, read_counts, run_task, write_counts


def _log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------------------
# Stage 1: wiki lexicon
# ---------------------------------------------------------------------------


def _lexicon_worker(args: tuple[str, int, int, str]) -> int:
    path, start, stop, out = args
    from ..tools.zim_cleaner import iter_zim_html
    from .wiki_lexicon import parse_page

    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        for _, title, page in iter_zim_html(path, start, stop):
            if 'class="besazimani" id="ku"' not in page and 'class="besazimani" id="ckb"' not in page:
                continue
            for rec in parse_page(page, title):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
    return n


def harvest_lexicon(cfg: Config, force: bool = False) -> Path:
    out = cfg.cache_dir / "lexicon_wiki.jsonl"
    if out.exists() and not force:
        _log(f"lexicon: cached {out}")
        return out
    from ..tools.zim_cleaner import zim_ranges

    parts_dir = cfg.cache_dir / "lexicon_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for src in cfg.by_kind("wiki_lexicon_zim"):
        for k, (a, b) in enumerate(zim_ranges(src.path, cfg.workers * 8)):
            jobs.append((src.path, a, b, str(parts_dir / f"{src.id}_{k:04d}.jsonl")))
    total = 0
    with ProcessPoolExecutor(cfg.workers) as pool:
        for i, n in enumerate(pool.map(_lexicon_worker, jobs), 1):
            total += n
            if i % 16 == 0:
                _log(f"lexicon: {i}/{len(jobs)} parts, {total} records")
    with open(out, "w", encoding="utf-8") as fh:
        for _, _, _, part in jobs:
            with open(part, encoding="utf-8") as ph:
                fh.write(ph.read())
            os.remove(part)
    _log(f"lexicon: {total} records -> {out}")
    return out


# ---------------------------------------------------------------------------
# Stage 2: dictionaries
# ---------------------------------------------------------------------------


def _dictionary_worker(src: Source) -> list[tuple[str, str, str, str, str]]:
    """Return rows (lang, word, pos, tag, role)."""
    from ..skills_ckb.orthography import normalize_word as ckb_norm
    from ..skills_kmr.orthography import normalize_word as kmr_norm
    from ..tools.mdx_extractor import detect_pos, entry_text, iter_entries, split_equivalents

    sel = tuple(src.options.get("definition_selectors", ()))
    drop = tuple(src.options.get("drop_classes", ()))
    rows: list[tuple[str, str, str, str, str]] = []
    for e in iter_entries(src.path):
        text = entry_text(e.html, sel, drop)
        pos = sorted(detect_pos(text, e.html))
        pos_s = pos[0] if len(pos) == 1 else ""
        if src.kind == "mdx_headwords":
            key = e.key.strip("()[] ")
            if not key or len(key.split()) > 1:
                continue
            rows.append((src.lang, ckb_norm(key) if src.lang == "ckb" else kmr_norm(key), pos_s, src.tag, "headword"))
            continue
        for eq in split_equivalents(text):
            script = detect_script(eq)
            if script == "arabic" and src.lang in ("ckb", "auto"):
                lang, word = "ckb", ckb_norm(eq)
            elif script == "latin" and src.lang in ("kmr", "auto"):
                lang, word = "kmr", kmr_norm(eq)
            else:
                continue
            role = "equivalent" if len(word.split()) == 1 else "expression"
            rows.append((lang, word, pos_s, src.tag, role))
    return rows


def harvest_dictionaries(cfg: Config, force: bool = False) -> Path:
    out = cfg.cache_dir / "dictionary_candidates.tsv"
    if out.exists() and not force:
        _log(f"dictionaries: cached {out}")
        return out
    agg: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    srcs = cfg.by_kind("mdx_headwords", "mdx_equivalents")
    with ProcessPoolExecutor(max(1, min(cfg.workers, len(srcs)))) as pool:
        futs = {pool.submit(_dictionary_worker, s): s for s in srcs}
        for f in as_completed(futs):
            rows = f.result()
            _log(f"dictionaries: {futs[f].id}: {len(rows)} candidates")
            for lang, word, pos, tag, role in rows:
                if word:
                    agg[(lang, word, role)][(pos, tag)] += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for (lang, word, role), c in sorted(agg.items()):
            pos_counts = Counter()
            tags = set()
            for (pos, tag), n in c.items():
                tags.add(tag)
                if pos:
                    pos_counts[pos] += n
            pos = pos_counts.most_common(1)[0][0] if pos_counts else ""
            fh.write(f"{lang}\t{word}\t{pos}\t{','.join(sorted(tags))}\t{role}\t{sum(c.values())}\n")
    _log(f"dictionaries: -> {out}")
    return out


# ---------------------------------------------------------------------------
# Stage 3: corpus counts
# ---------------------------------------------------------------------------


def plan_corpus_tasks(cfg: Config) -> list[Task]:
    from ..tools.zim_cleaner import zim_ranges

    tasks: list[Task] = []
    for src in cfg.sources:
        if src.kind == "text":
            for g in src.glob:
                tasks += plan_text_tasks(src.id, src.tag, g, src.lang, src.exclude)
        elif src.kind == "zim_articles":
            for a, b in zim_ranges(src.path, cfg.workers * 4):
                tasks.append(Task(src.id, src.tag, "zim", src.path, src.lang, a, b))
        elif src.kind == "mdx_articles":
            tasks.append(Task(src.id, src.tag, "mdx_articles", src.path, src.lang))
        elif src.kind == "mdx_headwords":
            tasks.append(Task(src.id, src.tag, "mdx_definitions", src.path, src.lang,
                              options={"selectors": src.options.get("definition_selectors", []),
                                       "drop_classes": src.options.get("drop_classes", [])}))
    # biggest first keeps the pool busy
    tasks.sort(key=lambda t: -(t.stop - t.start if t.stop else 10**9))
    return tasks


def harvest_corpus(cfg: Config, force: bool = False) -> dict[str, Path]:
    counts_dir = cfg.cache_dir / "counts"
    outs = {lang: cfg.cache_dir / f"freq_{lang}.tsv" for lang in ("ckb", "kmr")}
    if all(p.exists() for p in outs.values()) and not force:
        _log("corpus: cached")
        return outs
    counts_dir.mkdir(parents=True, exist_ok=True)
    tasks = plan_corpus_tasks(cfg)
    _log(f"corpus: {len(tasks)} tasks")
    per_lang: dict[str, Counter] = {"ckb": Counter(), "kmr": Counter()}
    caps: dict[str, Counter] = {"ckb": Counter(), "kmr": Counter()}
    tags: dict[str, dict[str, set]] = {"ckb": defaultdict(set), "kmr": defaultdict(set)}
    stats: dict[str, dict] = defaultdict(lambda: {"blocks_total": 0, "blocks_kept": 0, "tokens": 0, "rejected": Counter()})
    with ProcessPoolExecutor(cfg.workers) as pool:
        futs = [pool.submit(run_task, t) for t in tasks]
        for i, f in enumerate(as_completed(futs), 1):
            r: CountResult = f.result()
            per_lang[r.lang].update(r.counts)
            caps[r.lang].update(r.caps)
            for w in r.counts:
                tags[r.lang][w].add(r.tag)
            st = stats[r.source_id]
            st["lang"], st["tag"] = r.lang, r.tag
            st["blocks_total"] += r.blocks_total
            st["blocks_kept"] += r.blocks_kept
            st["tokens"] += sum(r.counts.values())
            st["rejected"].update(r.rejected_langs)
            if i % 10 == 0 or i == len(futs):
                _log(f"corpus: {i}/{len(futs)} tasks; types ckb={len(per_lang['ckb'])} kmr={len(per_lang['kmr'])}")
    for lang, out in outs.items():
        with open(out, "w", encoding="utf-8") as fh:
            for w, c in per_lang[lang].most_common():
                fh.write(f"{w}\t{c}\t{caps[lang].get(w, 0)}\t{','.join(sorted(tags[lang][w]))}\n")
    with open(cfg.cache_dir / "corpus_stats.json", "w", encoding="utf-8") as fh:
        json.dump({k: {**v, "rejected": dict(v["rejected"])} for k, v in stats.items()}, fh, ensure_ascii=False, indent=1)
    _log(f"corpus: wrote {outs}")
    return outs


def read_freq(path: Path, min_count: int = 1) -> tuple[dict[str, int], dict[str, int], dict[str, str]]:
    counts: dict[str, int] = {}
    caps: dict[str, int] = {}
    tags: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            w, c, cap, tg = line.rstrip("\n").split("\t")
            c = int(c)
            if c < min_count:
                break  # file is sorted by count
            counts[w] = c
            if cap != "0":
                caps[w] = int(cap)
            tags[w] = tg
    return counts, caps, tags


__all__ = ["harvest_lexicon", "harvest_dictionaries", "harvest_corpus", "read_freq", "read_counts", "write_counts"]
