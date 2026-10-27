"""Data structures shared by the analyzers, the lexicon builder and the CLI."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Protocol


@dataclass
class Analysis:
    """One morphological reading of a surface token."""

    surface: str
    lemma: str
    pos: str = "X"  # Universal Dependencies UPOS tag
    features: dict[str, str] = field(default_factory=dict)
    segments: list[tuple[str, str]] = field(default_factory=list)  # (morph, tag)
    score: float = 0.0

    @property
    def segmentation(self) -> str:
        return "+".join(m for m, _ in self.segments) if self.segments else self.surface

    @property
    def gloss(self) -> str:
        return "+".join(t for _, t in self.segments) if self.segments else "STEM"

    def morph_meta(self) -> str:
        meta = {"seg": self.segmentation, "gloss": self.gloss, **self.features}
        return json.dumps(meta, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["segmentation"] = self.segmentation
        d["gloss"] = self.gloss
        return d


class LexiconLike(Protocol):
    """What the analyzers need from a lexicon: membership, POS and frequency."""

    def __contains__(self, word: str) -> bool: ...

    def pos_of(self, word: str) -> set[str]: ...

    def freq(self, word: str) -> int: ...

    def gender_of(self, word: str) -> str | None: ...


class EmptyLexicon:
    def __contains__(self, word: str) -> bool:
        return False

    def pos_of(self, word: str) -> set[str]:
        return set()

    def freq(self, word: str) -> int:
        return 0

    def gender_of(self, word: str) -> str | None:
        return None


class SimpleLexicon:
    """In-memory lexicon: ``{lemma: {"pos": set, "gender": str|None}}`` + frequencies."""

    def __init__(self, entries: dict[str, dict] | None = None, freqs: dict[str, int] | None = None):
        self.entries = entries or {}
        self.freqs = freqs or {}

    def add(self, lemma: str, pos: str | None = None, gender: str | None = None) -> None:
        e = self.entries.setdefault(lemma, {"pos": set(), "gender": None})
        if pos:
            e["pos"].add(pos)
        if gender and not e["gender"]:
            e["gender"] = gender

    def __contains__(self, word: str) -> bool:
        return word in self.entries

    def __len__(self) -> int:
        return len(self.entries)

    def pos_of(self, word: str) -> set[str]:
        e = self.entries.get(word)
        return set(e["pos"]) if e else set()

    def freq(self, word: str) -> int:
        return self.freqs.get(word, 0)

    def gender_of(self, word: str) -> str | None:
        e = self.entries.get(word)
        return e["gender"] if e else None
