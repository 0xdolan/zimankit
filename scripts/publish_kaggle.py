#!/usr/bin/env python3
"""Upload output/kaggle as a new version of the Kaggle dataset, with progress bars and resume.

    python scripts/publish_kaggle.py           # upload
    python scripts/publish_kaggle.py --check   # show what would be uploaded, upload nothing

If the upload stops for any reason (Ctrl-C, lost network, reboot), run the same command again:
it continues each file from the last byte Kaggle received. Rebuilding the export changes the
files, and those start again. Unfinished uploads expire after about six days.

Needs the kaggle package: pip install 'zimankit[kaggle]'
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zimankit import __version__  # noqa: E402

FOLDER = ROOT / "output" / "kaggle"
METADATA = "dataset-metadata.json"
COVER = "dataset-cover-image.png"
# Kaggle keeps its resume state under the temp directory, and /tmp can be emptied by a reboot.
STATE_DIR = Path(os.environ.get("XDG_CACHE_HOME") or "~/.cache").expanduser() / "zimankit" / "kaggle-upload"
RETRIES = 20
RETRY_WAIT = 30  # seconds


def upload_files(folder: Path) -> list[Path]:
    """The files Kaggle will upload: everything but the metadata and the cover image."""
    return sorted(p for p in folder.iterdir() if p.is_file() and p.name not in (METADATA, COVER))


def size_text(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return ""


def make_api(total: int):
    """A KaggleApi that draws one bar for the whole upload and one for the current file."""
    from kaggle.api import kaggle_api_extended as kae
    from tqdm import tqdm

    if not (hasattr(kae.KaggleApi, "_upload_file") and hasattr(kae, "TqdmBufferedReader") and hasattr(kae, "Retry")):
        sys.exit("This kaggle package is not supported: pip install 'zimankit[kaggle]' --upgrade")

    bar_options = {"unit": "B", "unit_scale": True, "unit_divisor": 1024, "dynamic_ncols": True}

    class ProgressApi(kae.KaggleApi):
        done = 0  # bytes in the files already finished
        overall = None
        current = None

        def _upload_file(self, file_name, full_path, blob_type, upload_context, quiet, resources, content_type=None):
            size = os.path.getsize(full_path)
            self.current = tqdm(total=size, desc=file_name, position=1, leave=False, **bar_options)
            try:
                # quiet turns off Kaggle's own bar, and the reader below draws these instead
                result = super()._upload_file(file_name, full_path, blob_type, upload_context, True, resources, content_type)
            finally:
                self.current.close()
            self.done += size
            jump(self.overall, self.done)
            self.overall.write(f"done  {file_name} ({size_text(size)})")
            return result

    def jump(bar, position: int) -> None:
        """Move a bar without counting the distance as transfer speed, so a resume keeps the ETA honest."""
        bar.n = bar.last_print_n = position
        bar.refresh()

    class ProgressReader(kae.TqdmBufferedReader):
        def __init__(self, raw, progress_bar):
            super().__init__(raw, progress_bar)
            start = raw.tell()  # past zero when Kaggle resumes this file
            jump(api.current, start)
            jump(api.overall, api.done + start)

        def increment(self, length):
            api.current.update(length)
            api.overall.update(length)

    kae.TqdmBufferedReader = ProgressReader
    # Kaggle's HTTP retry sends a broken file again from byte 0; with none, it goes to its resume path instead
    retry = kae.Retry
    kae.Retry = lambda **_: retry(total=0)
    api = ProgressApi()
    api.overall = tqdm(total=total, desc="all files", position=0, **bar_options)
    return api


def publish(folder: Path, notes: str, retries: int = RETRIES, wait: int = RETRY_WAIT):
    """Upload *folder* as a new dataset version; returns Kaggle's response."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(STATE_DIR)
    total = sum(p.stat().st_size for p in upload_files(folder))
    api = make_api(total)
    api.authenticate()
    try:
        for attempt in range(retries + 1):
            api.done = 0
            try:
                return api.dataset_create_version(str(folder), notes, quiet=True)
            except Exception as error:
                # bad metadata will not fix itself; everything else may be the network
                if isinstance(error, ValueError) and not str(error).startswith("Upload unsuccessful"):
                    raise
                if attempt == retries:
                    raise
                api.overall.write(f"{error}\nTrying again in {wait} s ({attempt + 1} of {retries}).")
                time.sleep(wait)
    finally:
        api.overall.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload output/kaggle as a new version of the Kaggle dataset.")
    ap.add_argument("--check", action="store_true", help="show what would be uploaded and upload nothing")
    ap.add_argument("-m", "--message", default=f"zimankit {__version__}", help="version notes")
    ap.add_argument("--path", type=Path, default=FOLDER, help="the export folder")
    args = ap.parse_args()

    meta_path = args.path / METADATA
    if not meta_path.exists():
        print(f"{meta_path} not found. Build it first: python run_pipeline.py --stages build,rules,export", file=sys.stderr)
        return 1
    meta = json.loads(meta_path.read_text("utf-8"))
    files = upload_files(args.path)
    missing = [r["path"] for r in meta.get("resources", []) if not (args.path / r["path"]).exists()]
    if missing:
        print("listed in the metadata but missing: " + ", ".join(missing), file=sys.stderr)
        return 1

    print(f"Dataset: https://www.kaggle.com/datasets/{meta['id']}")
    print(f"Version notes: {args.message}")
    for p in files:
        print(f"  {size_text(p.stat().st_size):>10}  {p.name}")
    print(f"  {size_text(sum(p.stat().st_size for p in files)):>10}  total")
    if args.check:
        from kaggle import api

        print("Kaggle says the dataset is:", api.dataset_status(meta["id"]))
        return 0

    try:
        response = publish(args.path, args.message)
    except KeyboardInterrupt:
        print("\nStopped. Run the same command again to continue from here.", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"\n{error}\nRun the same command again to continue from here.", file=sys.stderr)
        return 1
    if response is None or (getattr(response, "error", "") or "") or (getattr(response, "status", "") or "ok").lower() != "ok":
        print(f"\nKaggle refused the new version: {getattr(response, 'error', response)}", file=sys.stderr)
        return 1
    print(f"\nUploaded. Kaggle is now processing it: {getattr(response, 'url', '') or meta['id']}")
    print(f"Check it with: kaggle datasets status {meta['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
