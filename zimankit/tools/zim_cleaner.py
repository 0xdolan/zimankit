"""HTML sanitisation, ZIM archive iteration and token-XML export.

* ``strip_html``      - boilerplate-free plain text from any HTML fragment
* ``article_paragraphs`` - prose paragraphs of a MediaWiki-rendered article
                         (infoboxes, navboxes, references, tables removed)
* ``iter_zim_html``   - parallel-safe iteration over the HTML items of a ZIM
* ``to_token_xml``    - analysed tokens as a small XML document
"""

from __future__ import annotations

import html as htmllib
import re
from typing import Callable, Iterable, Iterator
from xml.sax.saxutils import escape, quoteattr

_DROP_BLOCKS = re.compile(
    r"<(script|style|noscript|math|svg|head|figure|figcaption|table|sup|link|meta)\b[^>]*>.*?</\1\s*>|"
    r"<(link|meta|img|hr|input)\b[^>]*/?>",
    re.S | re.I,
)
_COMMENTS = re.compile(r"<!--.*?-->", re.S)
_TAG = re.compile(r"<[^>]+>")
_BLOCK_END = re.compile(r"</(p|div|li|dd|dt|h[1-6]|tr|ol|ul|blockquote)\s*>|<br\s*/?>", re.I)
_SPACES = re.compile(r"[ \t ]+")
_PARA = re.compile(r"<p\b[^>]*>(.*?)</p\s*>", re.S | re.I)
_REF_LIST = re.compile(r'<(ol|div)[^>]*class="[^"]*(references|reflist|navbox|mw-references)[^"]*"[^>]*>.*?</\1>', re.S | re.I)
_CONTENT_START = re.compile(r'id="mw-content-text"|class="[^"]*mw-parser-output')
_CONTENT_END = re.compile(r'class="printfooter"|class="zim-footer"|id="catlinks"|<!--htdig_noindex-->')
_STYLE_ATTR_JUNK = re.compile(r"\{[^{}]*:[^{}]*\}")  # css that leaked into text


def strip_html(fragment: str, keep_blocks: bool = True) -> str:
    """Remove tags, scripts, styles and comments; unescape entities."""
    s = _COMMENTS.sub(" ", fragment)
    s = _DROP_BLOCKS.sub(" ", s)
    if keep_blocks:
        s = _BLOCK_END.sub("\n", s)
    s = _TAG.sub(" ", s)
    s = htmllib.unescape(s)
    s = _STYLE_ATTR_JUNK.sub(" ", s)
    s = _SPACES.sub(" ", s)
    lines = (ln.strip() for ln in s.split("\n"))
    return "\n".join(ln for ln in lines if ln)


def content_region(page_html: str) -> str:
    """The article body of a MediaWiki page (between content start and footer)."""
    m = _CONTENT_START.search(page_html)
    start = m.start() if m else 0
    m2 = _CONTENT_END.search(page_html, start)
    return page_html[start : m2.start() if m2 else len(page_html)]


def article_paragraphs(page_html: str, min_chars: int = 40) -> list[str]:
    """Prose paragraphs only - the cleanest text for frequency counting."""
    body = _REF_LIST.sub(" ", content_region(page_html))
    out = []
    for m in _PARA.finditer(body):
        text = strip_html(m.group(1), keep_blocks=False)
        text = re.sub(r"\[\s*\d+\s*\]", "", text).strip()
        if len(text) >= min_chars:
            out.append(text)
    return out


def iter_zim_html(path: str, start: int = 0, stop: int | None = None) -> Iterator[tuple[str, str, str]]:
    """Yield ``(path, title, html)`` for HTML items with ids in [start, stop)."""
    from libzim.reader import Archive  # imported lazily: optional dependency

    archive = Archive(path)
    stop = archive.entry_count if stop is None else min(stop, archive.entry_count)
    for i in range(start, stop):
        entry = archive._get_entry_by_id(i)
        if entry.is_redirect:
            continue
        item = entry.get_item()
        if not item.mimetype.startswith("text/html"):
            continue
        yield entry.path, entry.title, bytes(item.content).decode("utf-8", "replace")


def zim_entry_count(path: str) -> int:
    from libzim.reader import Archive

    return Archive(path).entry_count


def zim_ranges(path: str, parts: int) -> list[tuple[int, int]]:
    n = zim_entry_count(path)
    step = max(1, -(-n // parts))
    return [(s, min(n, s + step)) for s in range(0, n, step)]


def to_token_xml(sentences: Iterable[list[tuple[str, dict]]], lang: str, doc_id: str = "d1") -> str:
    """Serialise analysed sentences as ``<doc><s><w lemma="" pos="">..</w></s></doc>``."""
    parts = [f"<doc id={quoteattr(doc_id)} lang={quoteattr(lang)}>"]
    for k, sent in enumerate(sentences, 1):
        parts.append(f'  <s n="{k}">')
        for token, attrs in sent:
            attr = " ".join(f"{a}={quoteattr(str(v))}" for a, v in attrs.items() if v not in (None, ""))
            parts.append(f"    <w {attr}>{escape(token)}</w>" if attr else f"    <w>{escape(token)}</w>")
        parts.append("  </s>")
    parts.append("</doc>")
    return "\n".join(parts)


def map_text(paragraphs: Iterable[str], fn: Callable[[str], str]) -> Iterator[str]:
    for p in paragraphs:
        yield fn(p)
