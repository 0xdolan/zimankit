#!/usr/bin/env python3
"""Build the website (https://0xdolan.github.io/zimankit/) into _site/.

Each page in site/pages/*.html is the <main> of one page. Its first line is a comment
with the title and description:

    <!-- title: Guide | description: How to install and use zimankit -->

The builder wraps it in the shared head (meta, Open Graph, favicons), header and footer,
copies site/css and site/js, the brand files the pages use, and builds the wheel that
the playground loads into Pyodide.

    python scripts/build_site.py            # then: python -m http.server -d _site
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "site"
OUT = ROOT / "_site"
BRAND = ROOT / "assets" / "brand"
URL = "https://0xdolan.github.io/zimankit/"
REPO = "https://github.com/0xdolan/zimankit"

NAV = [("index.html", "Home"), ("playground.html", "Playground"), ("guide.html", "Guide"),
       ("index.html#install", "Install"), ("story.html", "Story"), ("brand.html", "Brand")]


def version() -> str:
    return re.search(r'__version__ = "(.+?)"', (ROOT / "zimankit" / "__init__.py").read_text()).group(1)


def layout(name: str, title: str, description: str, body: str, ver: str) -> str:
    full = "zimankit · Kurdish language toolkit" if name == "index" else f"{title} · zimankit"
    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#13211C">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{URL}{'' if name == 'index' else name + '.html'}">
<meta property="og:image" content="{URL}brand/social/og-image-1200x630.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/site.css">
<script src="js/site.js"></script>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="index.html"><img class="on-light" src="brand/logo/svg/zimankit-mark-small.svg" alt="" width="30" height="30"><img class="on-dark" src="brand/logo/svg/zimankit-mark-on-dark.svg" alt="" width="30" height="30"><span>zimankit</span></a>
  <button class="menu" aria-expanded="false" aria-label="Menu">Menu</button>
  <nav class="nav">{nav}<a href="{REPO}">GitHub</a><button class="theme" type="button">Theme: system</button></nav>
</div></header>
<main>
{body}
</main>
<div class="band"></div>
<footer><div class="wrap">
  <span>zimankit {ver} · Made with ♥ by <a href="https://github.com/0xdolan">0xdolan</a></span>
  <span class="spacer"></span>
  <a href="{REPO}">Source</a><a href="{REPO}/releases/latest">Releases</a><a href="{REPO}/blob/main/CHANGELOG.md">Changelog</a>
  <a href="{REPO}/blob/main/docs/00-index.md">Docs</a><a href="{REPO}/blob/main/docs/tutorials/README.md">Tutorials</a>
  <a href="https://www.kaggle.com/datasets/zeroxdolan/kurdish-lexicon">Kaggle</a><a href="{REPO}/blob/main/LICENSE">GPL-3.0-or-later</a>
</div></footer>
</body>
</html>
"""


# Arabic-script words joined by single spaces or "+" (segmentations); tabs and double spaces separate columns.
ARABIC_RUN = re.compile(r"[\u0600-\u06FF\u200c]+(?:[ +][\u0600-\u06FF\u200c]+)*")
CODE = re.compile(r"(<(pre|code)\b[^>]*>)(.*?)(</\2>)", re.DOTALL)


def isolate_arabic(html: str) -> str:
    """Wrap Arabic-script runs in code and pre blocks in <bdi>, so they keep their place in LTR lines."""
    def inner(m: re.Match) -> str:
        parts = re.split(r"(<[^>]+>)", m[3])
        parts = [p if p.startswith("<") else ARABIC_RUN.sub(lambda a: f"<bdi>{a[0]}</bdi>", p) for p in parts]
        return m[1] + "".join(parts) + m[4]
    return CODE.sub(inner, html)


def main() -> int:
    ver = version()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for d in ("css", "js"):
        shutil.copytree(SRC / d, OUT / d)
    # Brand files used by the pages and offered for download; the live-text sources stay out.
    shutil.copytree(BRAND, OUT / "brand", ignore=shutil.ignore_patterns("src", "README.md"))
    for f in (BRAND / "icons").iterdir():  # favicons and the manifest at the site root
        shutil.copy(f, OUT / f.name)

    # The wheel for the playground (Pyodide unpacks it in the browser).
    pkg = OUT / "pkg"
    builder = ["uv", "build", "--wheel", "-q", "--out-dir", str(pkg)] if shutil.which("uv") else \
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", str(pkg), str(ROOT)]
    subprocess.run(builder, cwd=ROOT, check=True)
    wheel = next(pkg.glob("zimankit-*.whl")).name
    (pkg / "wheel.json").write_text(json.dumps({"wheel": wheel, "version": ver}) + "\n")

    for page in sorted((SRC / "pages").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        meta = re.match(r"<!--\s*title:\s*(.+?)\s*\|\s*description:\s*(.+?)\s*-->\n", text)
        if not meta:
            raise SystemExit(f"{page}: first line must be <!-- title: … | description: … -->")
        body = isolate_arabic(text[meta.end():].replace("{{version}}", ver))
        (OUT / page.name).write_text(layout(page.stem, meta[1], meta[2], body, ver), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"site built in {OUT.relative_to(ROOT)}/ (zimankit {ver}, {wheel})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
