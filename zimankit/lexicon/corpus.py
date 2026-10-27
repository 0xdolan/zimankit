"""Streaming, parallel token-frequency counting with language filtering.

Every text source is cut into *tasks* (byte ranges of plain-text files,
entry-id ranges of ZIM archives, whole MDX files).  A worker reads its task,
groups lines into ~2 kB blocks, runs language identification per block,
normalises accepted blocks with the dialect's orthography skill and counts
word forms.  Returned per task: ``Counter(form -> count)``, a counter of
capitalised non-initial occurrences (proper-noun evidence, Latin only) and
block statistics for the build report.
"""

from __future__ import annotations

import glob
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from ..shared_utils.lid import identify
from ..shared_utils.tokenizer import WORD_RE
from ..shared_utils.text_helpers import detect_script

BLOCK_CHARS = 2000
CHUNK_BYTES = 24 * 1024 * 1024


@dataclass
class Task:
    source_id: str
    tag: str
    kind: str  # text | zim | mdx_articles | mdx_definitions
    path: str
    lang: str
    start: int = 0
    stop: int | None = None
    options: dict = field(default_factory=dict)


@dataclass
class CountResult:
    source_id: str
    tag: str
    lang: str
    counts: Counter
    caps: Counter
    blocks_total: int = 0
    blocks_kept: int = 0
    rejected_langs: Counter = field(default_factory=Counter)


def plan_text_tasks(source_id: str, tag: str, pattern: str, lang: str, exclude: Iterable[str] = ()) -> list[Task]:
    tasks = []
    excl = list(exclude)
    for path in sorted(glob.glob(pattern, recursive=True)):
        if any(x in os.path.basename(path) for x in excl) or not os.path.isfile(path):
            continue
        size = os.path.getsize(path)
        for start in range(0, size, CHUNK_BYTES):
            tasks.append(Task(source_id, tag, "text", path, lang, start, min(size, start + CHUNK_BYTES)))
    return tasks


def _read_text_range(path: str, start: int, stop: int) -> str:
    with open(path, "rb") as fh:
        if start:
            fh.seek(start - 1)
            if fh.read(1) != b"\n":
                fh.readline()  # finish the partial line owned by the previous task
        data = fh.read(max(0, stop - fh.tell()))
        if not data.endswith(b"\n"):
            data += fh.readline()
    return data.decode("utf-8", "replace")


def _blocks(lines: Iterable[str]) -> Iterator[str]:
    buf: list[str] = []
    size = 0
    for line in lines:
        line = line.strip()
        if not line:
            if size >= BLOCK_CHARS // 4 and buf:
                yield "\n".join(buf)
                buf, size = [], 0
            continue
        buf.append(line)
        size += len(line)
        if size >= BLOCK_CHARS:
            yield "\n".join(buf)
            buf, size = [], 0
    if buf:
        yield "\n".join(buf)


def _normalizer(lang: str):
    if lang == "ckb":
        from ..skills_ckb.orthography import normalize

        return normalize
    from ..skills_kmr.orthography import normalize

    return normalize


def _count_blocks(blocks: Iterable[str], lang: str, res: CountResult, require_lid: bool) -> None:
    norm = _normalizer(lang)
    want_script = "arabic" if lang == "ckb" else "latin"
    from ..skills_kmr.orthography import lower

    for block in blocks:
        res.blocks_total += 1
        script = detect_script(block)
        if script == "mixed":
            # drop boilerplate lines (scripts, menus) written in another script
            block = "\n".join(ln for ln in block.split("\n") if detect_script(ln) == want_script)
            script = detect_script(block)
        if script not in (want_script, "mixed"):
            res.rejected_langs[f"script:{script}"] += 1
            continue
        if lang == "ckb":
            block = norm(block)  # legacy encodings must be repaired before LID
        if require_lid:
            r = identify(block)
            # an undecided block is kept only if the target language still scores highest
            tie_ok = r.lang == "und" and bool(r.scores) and r.scores.get(lang, 0) > 0 \
                and r.scores.get(lang, 0) >= max(r.scores.values())
            if r.lang != lang and not tie_ok:
                res.rejected_langs[r.lang] += 1
                continue
        res.blocks_kept += 1
        text = block if lang == "ckb" else norm(block)
        if lang == "ckb":
            for m in WORD_RE.finditer(text):
                w = m.group()
                if "؀" <= w[0] <= "ۿ":
                    res.counts[w] += 1
        else:
            for m in WORD_RE.finditer(text):
                w = m.group()
                c = w[0]
                if not ("a" <= c.lower() <= "z" or c in "çêîşûÇÊÎŞÛ"):
                    continue
                low = lower(w)
                res.counts[low] += 1
                if c.isupper():  # capitalised *inside* a sentence = proper-noun evidence
                    j = m.start() - 1
                    while j >= 0 and text[j] == " ":
                        j -= 1
                    if j >= 0 and text[j] not in ".!?:\n\"«“(-–":
                        res.caps[low] += 1


def run_task(task: Task) -> CountResult:
    res = CountResult(task.source_id, task.tag, task.lang, Counter(), Counter())
    require_lid = task.options.get("lid", True)
    if task.kind == "text":
        text = _read_text_range(task.path, task.start, task.stop or 0)
        _count_blocks(_blocks(text.split("\n")), task.lang, res, require_lid)
    elif task.kind == "zim":
        from ..tools.zim_cleaner import article_paragraphs, iter_zim_html

        def paras():
            for _, _, page in iter_zim_html(task.path, task.start, task.stop):
                yield from article_paragraphs(page)
                yield ""

        _count_blocks(_blocks(paras()), task.lang, res, require_lid)
    elif task.kind == "mdx_articles":
        from ..tools.mdx_extractor import iter_entries
        from ..tools.zim_cleaner import article_paragraphs

        def paras():
            for i, e in enumerate(iter_entries(task.path)):
                if task.stop is not None and i >= task.stop:
                    break
                yield from article_paragraphs(e.html)
                yield ""

        _count_blocks(_blocks(paras()), task.lang, res, require_lid)
    elif task.kind == "mdx_definitions":
        from ..tools.mdx_extractor import entry_text, iter_entries

        sel = tuple(task.options.get("selectors", ()))
        drop = tuple(task.options.get("drop_classes", ()))

        def paras():
            for e in iter_entries(task.path):
                yield entry_text(e.html, sel, drop)
                yield ""

        _count_blocks(_blocks(paras()), task.lang, res, require_lid=False)
    else:
        raise ValueError(task.kind)
    return res


def write_counts(path: str, counts: Counter, caps: Counter | None = None, min_count: int = 1) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for w, c in counts.most_common():
            if c < min_count:
                break
            fh.write(f"{w}\t{c}\t{caps.get(w, 0) if caps else 0}\n")


def read_counts(path: str) -> tuple[Counter, Counter]:
    counts: Counter = Counter()
    caps: Counter = Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                counts[parts[0]] = int(parts[1])
                if len(parts) > 2 and parts[2] != "0":
                    caps[parts[0]] = int(parts[2])
    return counts, caps
