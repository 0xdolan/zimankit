"""Stage 7: pack the published lexicon into one reproducible release asset.

Reads ``output/kaggle/`` (stage 6) and ``output/<lang>/grammar_rules_<lang>.json``
(stage 5) and writes ``output/bundle/zimankit-lexicon-<version>.tar.zst`` with a
``.sha256`` file beside it, for tools such as Zimanyar that build on the lexicon and
cannot run this pipeline themselves.

The bundle holds only what the Kaggle dataset publishes, as Parquet: never the raw
sources, the cache, the build reports or the rejected forms. The same inputs always
give the same bytes, so its checksum can be pinned.
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

from .. import __version__
from ..config import Config

SCHEMA_VERSION = 1
NOTICE = """\
Kurdish Lexicon, built with zimankit {version}
https://github.com/0xdolan/zimankit

The data in this bundle is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0):
https://creativecommons.org/licenses/by-sa/4.0/legalcode

The definitions and part of the lexicon derive from openly licensed share-alike
lexical data. If you share this data or an adaptation of it, credit the Kurdish
Lexicon and zimankit, link the licence, say whether you changed the data, and share
adaptations under the same licence.

The zimankit code is separate and is licensed under GPL-3.0-or-later.
"""


def bundle_inputs(cfg: Config, langs: list[str]) -> dict[str, Path]:
    """Map each file name in the bundle to its source file."""
    out = cfg.output_dir
    files = {"README.md": out / "kaggle" / "README.md"}
    for lang in langs:
        for table in ("words", "lemmas"):
            name = f"kurdish_{table}_{lang}.parquet"
            files[name] = out / "kaggle" / name
        files[f"grammar_rules_{lang}.json"] = out / lang / f"grammar_rules_{lang}.json"
    # Only Sorani has a spelling variant table.
    variants = out / "kaggle" / "kurdish_spelling_variants_ckb.csv"
    if "ckb" in langs:
        files[variants.name] = variants
    return files


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _add(tar: tarfile.TarFile, name: str, size: int, fh) -> None:
    # Fixed metadata: the archive must not depend on when or by whom it was built.
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = 0o644
    info.mtime = 0
    tar.addfile(info, fh)


def write_bundle(cfg: Config, langs: list[str], version: str = __version__) -> Path:
    if shutil.which("zstd") is None:
        raise RuntimeError("the bundle stage needs the zstd command")
    files = bundle_inputs(cfg, langs)
    missing = sorted(str(path) for path in files.values() if not path.exists())
    if missing:
        raise FileNotFoundError(
            "run the rules and export stages first (Parquet needs pip install 'zimankit[kaggle]'); missing: "
            + ", ".join(missing)
        )

    target_dir = cfg.output_dir / "bundle"
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = f"zimankit-lexicon-{version}"
    target = target_dir / f"{stem}.tar.zst"
    tar_path = target_dir / f"{stem}.tar"

    notice = NOTICE.format(version=version).encode("utf-8")
    manifest = {
        "schema": SCHEMA_VERSION,
        "zimankit_version": version,
        "languages": sorted(langs),
        "licence": "CC-BY-SA-4.0",
        "files": {
            name: {"size": files[name].stat().st_size, "sha256": _sha256(files[name])} for name in sorted(files)
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")

    with tarfile.open(tar_path, "w", format=tarfile.PAX_FORMAT) as tar:
        _add(tar, f"{stem}/MANIFEST.json", len(manifest_bytes), io.BytesIO(manifest_bytes))
        _add(tar, f"{stem}/NOTICE", len(notice), io.BytesIO(notice))
        for name in sorted(files):
            with open(files[name], "rb") as fh:
                _add(tar, f"{stem}/{name}", files[name].stat().st_size, fh)

    subprocess.run(["zstd", "-19", "-T0", "-q", "-f", "--rm", str(tar_path), "-o", str(target)], check=True)
    (target_dir / f"{target.name}.sha256").write_text(f"{_sha256(target)}  {target.name}\n", encoding="utf-8")
    return target
