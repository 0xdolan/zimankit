"""What PyPI shows comes from the README and pyproject.toml, so keep them fit for the project page."""

import re
import tomllib
from pathlib import Path

import zimankit

ROOT = Path(__file__).resolve().parents[1]


def test_readme_links_are_absolute():
    # PyPI has no repository to resolve relative links and images against.
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r'(?:src|href)="([^"]+)"', text) + re.findall(r"\]\(([^)\s]+)\)", text)
    assert targets
    assert [t for t in targets if not t.startswith(("http://", "https://", "#"))] == []


def test_readme_images_can_render_on_pypi():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for url in re.findall(r'<img src="https://raw\.githubusercontent\.com/0xdolan/zimankit/main/([^"]+)"', text):
        assert (ROOT / url).exists(), url


def test_version_is_single_sourced():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "version" in project["project"]["dynamic"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", zimankit.__version__)
