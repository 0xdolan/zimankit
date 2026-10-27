"""Read compiled ``.mdx`` dictionaries in-process with ``mdict-utils``.

No external process is spawned: ``mdict_utils.base.readmdict.MDX`` decodes
the key and record blocks directly.  On top of the raw ``(key, html)`` pairs
this module provides:

* ``iter_entries``      - decoded entries, ``@@@LINK=`` redirects resolved or skipped
* ``entry_text``        - the definition as clean text (styles / css / links removed)
* ``detect_pos``        - part-of-speech from the abbreviations dictionaries use
* ``split_equivalents`` - a definition list ("x، y، z") -> individual equivalents
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator

from .zim_cleaner import strip_html

LINK_PREFIX = "@@@LINK="

# Abbreviation -> UPOS.  Keys are matched as whole tokens inside (), [] or
# at the start of a definition.  Covers English, Central Kurdish, Northern
# Kurdish and the Persian-style abbreviations used in bilingual dictionaries.
POS_MARKERS: dict[str, str] = {
    # English
    "n": "NOUN", "noun": "NOUN", "v": "VERB", "vt": "VERB", "vi": "VERB", "verb": "VERB",
    "adj": "ADJ", "a": "ADJ", "adv": "ADV", "prep": "ADP", "conj": "CCONJ", "pron": "PRON",
    "interj": "INTJ", "num": "NUM", "pn": "PROPN",
    # Central Kurdish
    "ناو": "NOUN", "کار": "VERB", "چاوگ": "VERB", "ئاوەڵناو": "ADJ", "هاوەڵناو": "ADJ",
    "ئاوەڵکار": "ADV", "هاوەڵکار": "ADV", "جێناو": "PRON", "ئامراز": "ADP", "ژمارە": "NUM",
    "سەرسوڕمان": "INTJ", "ناوی تایبەت": "PROPN",
    # Northern Kurdish
    "nd": "NOUN", "navdêr": "NOUN", "lk": "VERB", "lêker": "VERB", "rd": "ADJ", "rengdêr": "ADJ",
    "hk": "ADV", "hoker": "ADV", "cn": "PRON", "cînav": "PRON", "dç": "ADP", "daçek": "ADP",
    # Persian-style abbreviations (اسم، صفت، قید، مصدر لازم/متعدی، حاصل مصدر)
    "ا": "NOUN", "اسم": "NOUN", "افا": "NOUN", "امف": "NOUN", "امص": "NOUN", "حامص": "NOUN",
    "ص": "ADJ", "صمر": "ADJ", "صفا": "ADJ", "صمف": "ADJ", "صنسبی": "ADJ", "صفت": "ADJ",
    "ق": "ADV", "قمر": "ADV", "قید": "ADV",
    "مصل": "VERB", "مصم": "VERB", "مص": "VERB", "مصدر": "VERB",
}
_MARKER_GROUP = re.compile(r"[\(\[]\s*([^()\[\]]{1,24}?)\s*[\)\]]")
_NOISE = re.compile(r"[‌‏‎.:،,]")
_EQUIV_SPLIT = re.compile(r"\s*(?:[،,;؛/|]|\s-\s|–|—|\n)\s*")
_NUMBERING = re.compile(r"^\s*(?:\d+|[١-٩][٠-٩]*|[a-z]|[أ-ي])[.)\-]\s*")
_PARENS = re.compile(r"\([^()]*\)|\[[^\[\]]*\]")


@dataclass
class MdxEntry:
    key: str
    html: str
    redirect: str | None = None
    meta: dict = field(default_factory=dict)


def open_mdx(path: str):
    from mdict_utils.base.readmdict import MDX  # lazy: optional dependency

    return MDX(path)


def header(path: str) -> dict[str, str]:
    m = open_mdx(path)
    return {k.decode("utf-8", "replace"): v.decode("utf-8", "replace") for k, v in m.header.items()}


def iter_entries(path: str, follow_links: bool = False) -> Iterator[MdxEntry]:
    """Decode every record; redirects are yielded with ``redirect`` set."""
    mdx = open_mdx(path)
    for k, v in mdx.items():
        key = k.decode("utf-8", "replace").strip()
        val = v.decode("utf-8", "replace").strip("\x00 \r\n")
        if val.startswith(LINK_PREFIX):
            if follow_links:
                yield MdxEntry(key, "", redirect=val[len(LINK_PREFIX) :].strip())
            continue
        yield MdxEntry(key, val)


def entry_text(html: str, selectors: tuple[str, ...] = (), drop_classes: tuple[str, ...] = ()) -> str:
    """Clean text of an entry.

    ``selectors``: class names whose element contents are kept (e.g. ``def``,
    ``item``).  ``drop_classes``: class names removed first (headword echo,
    labels in the source language, abbreviation tables).
    """
    h = html
    for cls in drop_classes:
        h = re.sub(rf'<(\w+)[^>]*class="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*>.*?</\1>', " ", h, flags=re.S)
    if selectors:
        parts = []
        for cls in selectors:
            parts += re.findall(rf'<(\w+)[^>]*class="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*>(.*?)</\1>', h, flags=re.S)
        h = "\n".join(p[1] for p in parts) if parts else h
    return strip_html(h)


def detect_pos(text: str, raw_html: str = "") -> set[str]:
    """Every UPOS whose marker appears in (), [] or a POS-classed element."""
    found: set[str] = set()
    candidates = [m.group(1) for m in _MARKER_GROUP.finditer(text)]
    candidates += re.findall(r'class="(?:nex|pos|gram)"[^>]*>\s*\(?([^<)]{1,24})', raw_html)
    for c in candidates:
        for part in re.split(r"[/\s]+", c):
            key = _NOISE.sub("", part).strip().lower()
            if key in POS_MARKERS:
                found.add(POS_MARKERS[key])
    return found


def split_equivalents(definition: str, max_words: int = 3) -> list[str]:
    """Split a definition into short equivalents, dropping notes and numbering."""
    out: list[str] = []
    for line in definition.split("\n"):
        if ":" in line and len(line.split(":", 1)[0]) < 40:
            line = line.split(":", 1)[1]  # "sense label: eq1، eq2"
        for piece in _EQUIV_SPLIT.split(_PARENS.sub(" ", line)):
            piece = _NUMBERING.sub("", piece).strip(" .-–—*\"'«»“”")
            if piece and len(piece.split()) <= max_words:
                out.append(piece)
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]
