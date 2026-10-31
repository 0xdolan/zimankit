import hashlib
import io
import json
import shutil
import subprocess
import tarfile

import pytest

from zimankit.config import Config
from zimankit.lexicon.bundle import bundle_inputs, write_bundle

needs_zstd = pytest.mark.skipif(shutil.which("zstd") is None, reason="needs the zstd command")


def _config(tmp_path):
    cfg = Config(settings={"run": {"output_dir": "output", "cache_dir": "cache"}}, sources=[], deny_tokens=set(),
                 root=tmp_path)
    for name, path in bundle_inputs(cfg, ["ckb", "kmr"]).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"content of {name}".encode())
    # Things that exist beside the inputs and must never be published.
    (tmp_path / "output" / "ckb" / "rejected_ckb.csv").write_text("secret")
    (tmp_path / "output" / "ckb" / "build_report_ckb.json").write_text("secret")
    (tmp_path / "output" / "kaggle" / "kurdish_lexicon.sqlite").write_text("secret")
    return cfg


def _members(path):
    raw = subprocess.run(["zstd", "-dc", str(path)], check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
        return {m.name: (m, tar.extractfile(m).read()) for m in tar.getmembers()}


@needs_zstd
def test_bundle_holds_the_published_files_only(tmp_path):
    members = _members(write_bundle(_config(tmp_path), ["ckb", "kmr"], "9.9.9"))
    assert sorted(name.split("/", 1)[1] for name in members) == sorted([
        "MANIFEST.json", "NOTICE", "README.md",
        "kurdish_words_ckb.parquet", "kurdish_lemmas_ckb.parquet", "kurdish_spelling_variants_ckb.csv",
        "kurdish_words_kmr.parquet", "kurdish_lemmas_kmr.parquet",
        "grammar_rules_ckb.json", "grammar_rules_kmr.json",
    ])
    assert all(name.startswith("zimankit-lexicon-9.9.9/") for name in members)
    assert not any(b"secret" in content for _, content in members.values())


@needs_zstd
def test_manifest_lists_each_file_with_its_checksum(tmp_path):
    members = _members(write_bundle(_config(tmp_path), ["ckb", "kmr"], "9.9.9"))
    manifest = json.loads(members["zimankit-lexicon-9.9.9/MANIFEST.json"][1])
    assert manifest["zimankit_version"] == "9.9.9"
    assert manifest["licence"] == "CC-BY-SA-4.0"
    assert manifest["languages"] == ["ckb", "kmr"]
    assert len(manifest["files"]) == 8
    for name, entry in manifest["files"].items():
        content = members[f"zimankit-lexicon-9.9.9/{name}"][1]
        assert entry == {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}


@needs_zstd
def test_notice_states_the_data_licence(tmp_path):
    members = _members(write_bundle(_config(tmp_path), ["ckb", "kmr"], "9.9.9"))
    notice = members["zimankit-lexicon-9.9.9/NOTICE"][1].decode()
    assert "CC BY-SA 4.0" in notice and "9.9.9" in notice


@needs_zstd
def test_bundle_is_reproducible(tmp_path):
    cfg = _config(tmp_path)
    first = write_bundle(cfg, ["ckb", "kmr"], "9.9.9").read_bytes()
    # A later build, with newer file times, must give the same bytes.
    for path in bundle_inputs(cfg, ["ckb", "kmr"]).values():
        path.touch()
    second_path = write_bundle(cfg, ["ckb", "kmr"], "9.9.9")
    assert second_path.read_bytes() == first
    member, _ = _members(second_path)["zimankit-lexicon-9.9.9/NOTICE"]
    assert (member.mtime, member.uid, member.uname) == (0, 0, "")


@needs_zstd
def test_checksum_file_matches_and_the_tar_is_removed(tmp_path):
    target = write_bundle(_config(tmp_path), ["ckb", "kmr"], "9.9.9")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    assert (target.parent / f"{target.name}.sha256").read_text() == f"{digest}  {target.name}\n"
    assert not list(target.parent.glob("*.tar"))


@needs_zstd
def test_missing_input_is_named(tmp_path):
    cfg = _config(tmp_path)
    (tmp_path / "output" / "kaggle" / "kurdish_words_kmr.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="kurdish_words_kmr.parquet"):
        write_bundle(cfg, ["ckb", "kmr"], "9.9.9")


def test_no_variant_table_without_sorani(tmp_path):
    cfg = Config(settings={"run": {"output_dir": "output", "cache_dir": "cache"}}, sources=[], deny_tokens=set(),
                 root=tmp_path)
    assert "kurdish_spelling_variants_ckb.csv" not in bundle_inputs(cfg, ["kmr"])
