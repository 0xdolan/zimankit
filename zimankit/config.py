"""Configuration loading: ``config/pipeline.toml`` + ``config/sources.local.toml``."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Source:
    id: str
    tag: str
    kind: str
    lang: str
    path: str | None = None
    glob: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    options: dict = field(default_factory=dict)


@dataclass
class Config:
    settings: dict
    sources: list[Source]
    deny_tokens: set[str]
    root: Path

    @property
    def cache_dir(self) -> Path:
        return self.root / self.settings["run"]["cache_dir"]

    @property
    def output_dir(self) -> Path:
        return self.root / self.settings["run"]["output_dir"]

    @property
    def workers(self) -> int:
        return int(os.environ.get("ZIMANKIT_WORKERS", self.settings["run"].get("workers", 4)))

    def by_kind(self, *kinds: str) -> list[Source]:
        return [s for s in self.sources if s.kind in kinds]


def load_config(root: str | Path | None = None, sources_file: str | None = None) -> Config:
    root = Path(root) if root else PROJECT_ROOT
    with open(root / "config" / "pipeline.toml", "rb") as fh:
        settings = tomllib.load(fh)
    src_path = Path(sources_file) if sources_file else root / "config" / "sources.local.toml"
    if not src_path.exists():
        src_path = root / "config" / "sources.example.toml"
    with open(src_path, "rb") as fh:
        raw = tomllib.load(fh)
    sources = []
    known = {"id", "tag", "kind", "lang", "path", "glob", "exclude"}
    for s in raw.get("source", []):
        globs = s.get("glob", [])
        sources.append(
            Source(
                id=s["id"], tag=s["tag"], kind=s["kind"], lang=s.get("lang", "auto"), path=s.get("path"),
                glob=[globs] if isinstance(globs, str) else list(globs), exclude=list(s.get("exclude", [])),
                options={k: v for k, v in s.items() if k not in known},
            )
        )
    deny = {t.lower() for t in raw.get("deny_tokens", [])}
    return Config(settings, sources, deny, root)
