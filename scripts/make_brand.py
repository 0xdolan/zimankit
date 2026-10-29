#!/usr/bin/env python3
"""Generate the zimankit brand kit (logo, icons, wordmarks, social, ads, print, story image) into assets/brand/.

The logo is a **deq** sign, the figure of the tree of life (a dot, two branches, a trunk
through a circle, two roots, a dot), with **Roj**, the 21-rayed sun of the flag of Kurdistan,
at its heart. The sun is drawn with the path of the flag's official SVG (Wikimedia Commons,
public domain). See assets/brand/README.md for the story and the sources.

    uv run python scripts/make_brand.py          # SVGs + PNG/ICO/PDF (needs inkscape and ImageMagick)
    uv run python scripts/make_brand.py --svg    # SVG sources only

Every SVG with text is written twice: with live text under assets/brand/src/ and with the
text converted to paths at its final place, so it renders without the fonts installed
(IBM Plex Sans and IBM Plex Sans Arabic).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "brand"
REPO = "github.com/0xdolan/zimankit"

# Sun of the flag of Kurdistan (Flag_of_Kurdistan.svg): centre (450, 300), outer radius 150.
FLAG_SUN = (
    "M450 150l11.24 76.264 33.222-69.563-11.738 76.19 52.249-56.68-33.674 69.344 66.634-38.761-52.616 "
    "56.338 75.098-17.399-66.885 38.327 76.89 5.51-75.21 16.909 71.85 27.929-76.852-6.011 60.425 47.867"
    "-71.666-28.397 43.632 63.55-60.113-48.259 22.962 73.589-43.217-63.834.25 77.087L450 376.264 427.518 "
    "450l.251-77.087-43.217 63.834 22.962-73.589-60.113 48.26 43.632-63.551-71.666 28.397 60.425-47.867"
    "-76.852 6.011 71.85-27.93-75.21-16.908 76.89-5.51-66.885-38.327 75.098 17.399-52.616-56.338 66.634 "
    "38.76-33.674-69.343 52.249 56.68-11.738-76.19 33.221 69.563z"
)

C = {
    "sun": "#FEBD11",  # the flag's sun
    "ink": "#22332A",  # deq ink: green-black
    "sand": "#F4EDE0",  # warm ground, like skin and undyed wool
    "rim": "#3A3A34",
    "night": "#13211C",  # dark ground
    "pale": "#F3EEE2",  # ink on the dark ground
    "muted": "#5B5F58",
    "muted-dark": "#BDB7A8",
    "red": "#ED2024", "white": "#FFFFFF", "green": "#278E43",  # the flag's band
}
THEMES = {
    "light": {"bg": C["sand"], "ink": C["ink"], "fg": "#151A17", "sub": C["muted"], "accent": "#9A6B00"},
    "dark": {"bg": C["night"], "ink": C["pale"], "fg": C["pale"], "sub": C["muted-dark"], "accent": C["sun"]},
}

LATIN, ARABIC = "IBM Plex Sans", "IBM Plex Sans Arabic"
NAME, NAME_CKB = "zimankit", "زمانکیت"
TAGLINE = "Kurdish language toolkit · Sorani · Kurmanji"
# Advance widths per 1 px of font size, measured with Inkscape.
EM = {"name": 3.95, "name_ckb": 3.04, "tagline": 19.2, "url": 13.5}

# ---------------------------------------------------------------- the mark

# On a 1024 box: the sun at (512, 512) r 230; the figure from the top dot (y 96) to the bottom dot (y 934).
STROKE = 36
FIGURE = [
    "M430 190 L512 268 L594 190",  # the two branches (Sorani and Kurmanji)
    "M512 268 V756",  # the trunk
    "M430 840 L512 756 L594 840",  # the roots
]
RING, DOTS = (512, 512, 112), ((512, 122, 26), (512, 908, 26))
MARK_BOX = 64  # the mark alone fits the square 64..960, with room for the bold dots


def sun(cx: float, cy: float, r: float, fill: str = C["sun"], extra: str = "") -> str:
    s = r / 150
    return (f'<path fill="{fill}"{extra} transform="translate({cx - 450 * s:.2f} {cy - 300 * s:.2f}) '
            f'scale({s:.4f})" d="{FLAG_SUN}"/>')


def figure(ink: str, width: float = STROKE, dot_grow: float = 0) -> str:
    paths = "".join(f'<path d="{d}"/>' for d in FIGURE)
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r + dot_grow}"/>' for x, y, r in DOTS)
    return (f'<g fill="none" stroke="{ink}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'{paths}<circle cx="{RING[0]}" cy="{RING[1]}" r="{RING[2]}"/></g><g fill="{ink}">{dots}</g>')


def mark(ink: str, sun_fill: str = C["sun"], mono: bool = False, bold: bool = False, uid: str = "k") -> str:
    """The mark on the 1024 box. mono: one colour, the figure cut out of the sun by a gap."""
    width = 60 if bold else STROKE
    grow = 14 if bold else 0
    if not mono:
        return sun(512, 512, 230, sun_fill) + figure(ink, width, grow)
    knock = figure("#000", width + 44, grow + 22)
    return (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">'
            f'<rect width="1024" height="1024" fill="#fff"/>{knock}</mask>'
            + f'<g mask="url(#{uid})">{sun(512, 512, 230, ink)}</g>' + figure(ink, width, grow))


def place(body: str, x: float, y: float, size: float, box: float = MARK_BOX) -> str:
    """Put a 1024-box drawing so that its square box..1024-box lands at (x, y) with the given size."""
    s = size / (1024 - 2 * box)
    return f'<g transform="translate({x - box * s:.2f} {y - box * s:.2f}) scale({s:.5f})">{body}</g>'


def disc_logo(theme: str, rim: bool = True, **kw) -> str:
    t = THEMES[theme]
    stroke = f' stroke="{C["rim"]}" stroke-width="4"' if rim and theme == "light" else ""
    return f'<circle cx="512" cy="512" r="490" fill="{t["bg"]}"{stroke}/>' + mark(t["ink"], **kw)


# ---------------------------------------------------------------- SVG helpers


def svg(body: str, w: float, h: float, view: str | None = None, title: str = "zimankit", unit: str = "") -> str:
    view = view or f"0 0 {w} {h}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}{unit}" height="{h}{unit}" viewBox="{view}">\n'
            f"  <title>{title}</title>\n  {body}\n</svg>\n")


def text(x: float, y: float, size: float, s: str, fill: str, weight: int = 400, anchor: str = "start",
         font: str = LATIN, spacing: float = 0, opacity: float = 1) -> str:
    extra = f' letter-spacing="{spacing:.2f}"' if spacing else ""
    extra += f' opacity="{opacity}"' if opacity != 1 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-weight="{weight}" font-size="{size:.1f}" '
            f'fill="{fill}" text-anchor="{anchor}"{extra}>{s}</text>')


def flag_band(w: float, h: float, thick: float) -> str:
    return "".join(f'<rect y="{h - (3 - i) * thick:.1f}" width="{w}" height="{thick + 0.5:.1f}" fill="{c}"/>'
                   for i, c in enumerate((C["red"], C["white"], C["green"])))


# ---------------------------------------------------------------- compositions


def wordmark(theme: str, layout: str) -> tuple[str, int, int]:
    t = THEMES[theme]
    logo = disc_logo(theme, uid=f"wm{theme}")
    if layout == "horizontal":
        w, h = 1640, 512
        body = (f'<g transform="translate(24 24) scale(0.453)">{logo}</g>'
                + text(540, 236, 186, NAME, t["fg"], 600)
                + text(548, 356, 100, NAME_CKB, t["fg"], 600, font=ARABIC)
                + text(548, 450, 50, TAGLINE, t["sub"]))
    else:
        w, h = 1024, 1280
        body = (f'<g transform="translate(232 64) scale(0.547)">{logo}</g>'
                + text(512, 846, 190, NAME, t["fg"], 600, "middle")
                + text(512, 994, 110, NAME_CKB, t["fg"], 600, "middle", ARABIC)
                + text(512, 1110, 46, TAGLINE, t["sub"], anchor="middle"))
    ground = f'<rect width="{w}" height="{h}" rx="40" fill="{t["bg"]}"/>' if theme == "dark" else ""
    return svg(ground + body, w, h), w, h


def card(w: int, h: int, theme: str = "dark", url: bool = True, band: bool = True, tagline: str = TAGLINE) -> str:
    """A social or ad card: the layout follows the aspect ratio."""
    t = THEMES[theme]
    r = w / h
    out = [f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>']
    if theme == "dark":
        out.append(f'<defs><radialGradient id="glow"><stop offset="0" stop-color="{C["sun"]}" stop-opacity="0.16"/>'
                   f'<stop offset="1" stop-color="{C["sun"]}" stop-opacity="0"/></radialGradient></defs>')
    logo = mark(t["ink"], uid=f"c{w}x{h}")
    bandh = max(2, round(min(w, h) * 0.012)) if band else 0
    inner_h = h - 3 * bandh
    if r >= 1.5:  # mark on the left, text on the right
        pad = inner_h * (0.16 if r < 5 else 0.12)
        size = inner_h - 2 * pad
        x0 = pad * (1.4 if r < 5 else 1.0)
        if theme == "dark":
            out.append(f'<circle cx="{x0 + size / 2:.1f}" cy="{pad + size / 2:.1f}" r="{size * 0.62:.1f}" fill="url(#glow)"/>')
        out.append(place(logo, x0, pad, size))
        tx = x0 + size + pad * (0.9 if r < 5 else 0.7)
        avail = w - tx - pad * 1.2
        compact = r >= 5  # leaderboard-like strips: one line of text
        if compact:
            s = min(inner_h * 0.42, avail / (EM["name"] + EM["name_ckb"] + 1.2) if not url else avail / (EM["name"] + EM["name_ckb"] + 1.2 + 0.4 * EM["url"] + 1.5))
            base = inner_h / 2 + s * 0.36
            out.append(text(tx, base, s, NAME, t["fg"], 600))
            out.append(text(tx + s * (EM["name"] + 0.6), base, s * 0.92, NAME_CKB, t["fg"], 600, font=ARABIC))
            if url:
                out.append(text(w - pad * 1.2, base, s * 0.4, REPO, t["accent"], 500, "end"))
        else:
            s = min(inner_h * 0.2, avail / EM["name"])
            sub = min(s * 0.24, avail / EM["tagline"])
            lines = s * 1.0 + s * 0.6 * 1.25 + sub * 2.2 + (sub * 2.4 if url else 0)
            y = inner_h / 2 - lines / 2 + s * 0.78
            out.append(text(tx, y, s, NAME, t["fg"], 600))
            y += s * 0.75
            out.append(text(tx, y, s * 0.55, NAME_CKB, t["accent"] if theme == "dark" else t["fg"], 600, font=ARABIC))
            y += sub * 2.6
            if sub >= 8:  # too small to read on narrow banners
                out.append(text(tx, y, sub, tagline, t["sub"]))
            if url:
                y += sub * 2.2
                out.append(text(tx, y, sub * 0.92, REPO, t["accent"], 500))
    else:  # stacked: mark above, text below
        pad = min(w, inner_h) * 0.1
        s = min((w - 2 * pad) / EM["name"], inner_h * 0.11)
        sub = min(s * 0.24, (w - 1.6 * pad) / EM["tagline"])
        text_h = s * 0.8 + s * 0.62 * 1.3 + sub * 2.6 + (sub * 2.4 if url else 0)
        size = min(w - 2 * pad, inner_h - 2 * pad - text_h - pad * 0.5)
        total = size + pad * 0.6 + text_h
        y0 = (inner_h - total) / 2
        if theme == "dark":
            out.append(f'<circle cx="{w / 2:.1f}" cy="{y0 + size / 2:.1f}" r="{size * 0.62:.1f}" fill="url(#glow)"/>')
        out.append(place(logo, (w - size) / 2, y0, size))
        y = y0 + size + pad * 0.6 + s * 0.8
        out.append(text(w / 2, y, s, NAME, t["fg"], 600, "middle"))
        y += s * 0.82
        out.append(text(w / 2, y, s * 0.62, NAME_CKB, t["accent"] if theme == "dark" else t["fg"], 600, "middle", ARABIC))
        y += sub * 2.6
        if sub * 1.15 < 8:  # too small to read: no tagline
            pass
        elif sub * EM["tagline"] > w - 1.6 * pad or sub < 9:  # too narrow: two short lines
            out.append(text(w / 2, y, sub * 1.15, "Kurdish language toolkit", t["sub"], anchor="middle"))
            y += sub * 1.6
            out.append(text(w / 2, y, sub * 1.15, "Sorani · Kurmanji", t["sub"], anchor="middle"))
        else:
            out.append(text(w / 2, y, sub, tagline, t["sub"], anchor="middle"))
        if url:
            y += sub * 2.4
            out.append(text(w / 2, y, min(sub * 1.05, (w - pad) / EM["url"]), REPO, t["accent"], 500, "middle"))
    if band:
        out.append(flag_band(w, h, bandh))
    return svg("\n  ".join(out), w, h)


def app_icon(size: int, theme: str = "light", safe: float = 0.86, rounded: bool = False) -> str:
    """Full-bleed square: stores and launchers crop the corners themselves."""
    t = THEMES[theme]
    rx = f' rx="{size * 0.2:.1f}"' if rounded else ""
    inner = size * safe
    return svg(f'<rect width="{size}" height="{size}"{rx} fill="{t["bg"]}"/>'
               + place(mark(t["ink"], uid="app"), (size - inner) / 2, (size - inner) / 2, inner), size, size)


# ---------------------------------------------------------------- story images


def deq_figure_lineart(ink: str) -> str:
    """The deq sign as it is tattooed: thin lines, an upright oval, no sun."""
    return (f'<g fill="none" stroke="{ink}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M440 200 L512 268 L584 200"/><path d="M512 268 V756"/>'
            f'<ellipse cx="512" cy="512" rx="110" ry="150"/><path d="M440 830 L512 756 L584 830"/></g>'
            f'<g fill="{ink}"><circle cx="512" cy="130" r="20"/><circle cx="512" cy="900" r="20"/></g>')


def story_construction() -> str:
    t = THEMES["light"]
    w, h = 1800, 760
    cols = (300, 900, 1500)
    out = [f'<rect width="{w}" height="{h}" rx="24" fill="{t["bg"]}"/>',
           place(deq_figure_lineart(t["ink"]), cols[0] - 230, 80, 460),
           place(sun(512, 512, 230), cols[1] - 230, 80, 460),
           place(mark(t["ink"]), cols[2] - 230, 80, 460),
           text((cols[0] + cols[1]) / 2, 330, 110, "+", t["sub"], 300, "middle"),
           text((cols[1] + cols[2]) / 2, 330, 110, "=", t["sub"], 300, "middle")]
    labels = (("Deq", "the tree-of-life figure,", "a hand-poked Kurdish tattoo"),
              ("Roj", "the 21-rayed sun of", "the flag of Kurdistan"),
              ("zimankit", "the sun at the heart", "of the tree of life"))
    for x, (a, b, c) in zip(cols, labels):
        out += [text(x, 610, 46, a, t["fg"], 600, "middle", spacing=0.5),
                text(x, 664, 30, b, t["sub"], anchor="middle"), text(x, 702, 30, c, t["sub"], anchor="middle")]
    return svg("\n  ".join(out), w, h, title="zimankit logo: deq + Roj")


# ---------------------------------------------------------------- the kit

SOCIAL = {  # name: (w, h)
    "github-social-preview": (1280, 640),
    "og-image": (1200, 630),
    "x-post": (1200, 675),
    "x-header": (1500, 500),
    "linkedin-banner": (1584, 396),
    "facebook-cover": (1640, 624),
    "youtube-banner": (2560, 1440),
    "instagram-post": (1080, 1080),
    "instagram-story": (1080, 1920),
}
ADS = {  # IAB standard units
    "leaderboard": (728, 90),
    "mobile-banner": (320, 50),
    "large-mobile-banner": (320, 100),
    "billboard": (970, 250),
    "medium-rectangle": (300, 250),
    "large-rectangle": (336, 280),
    "half-page": (300, 600),
    "wide-skyscraper": (160, 600),
}


def build() -> dict[str, str]:
    """{path under assets/brand/: SVG}; paths under src/ keep live text."""
    f: dict[str, str] = {}
    full = "0 0 1024 1024"
    crop = f"{MARK_BOX} {MARK_BOX} {1024 - 2 * MARK_BOX} {1024 - 2 * MARK_BOX}"
    f["logo/svg/zimankit-logo.svg"] = svg(disc_logo("light"), 1024, 1024, full)
    f["logo/svg/zimankit-logo-small.svg"] = svg(disc_logo("light", bold=True), 1024, 1024, full)
    f["logo/svg/zimankit-logo-dark.svg"] = svg(disc_logo("dark"), 1024, 1024, full)
    f["logo/svg/zimankit-mark.svg"] = svg(mark(C["ink"]), 1024, 1024, crop)
    f["logo/svg/zimankit-mark-on-dark.svg"] = svg(mark(C["pale"]), 1024, 1024, crop)
    f["logo/svg/zimankit-mark-mono-black.svg"] = svg(mark("#000000", mono=True), 1024, 1024, crop)
    f["logo/svg/zimankit-mark-mono-white.svg"] = svg(mark("#FFFFFF", mono=True), 1024, 1024, crop)
    f["logo/svg/zimankit-mark-small.svg"] = svg(mark(C["ink"], bold=True), 1024, 1024, crop)
    # The browser-tab icon follows the system theme: pale ink in dark mode.
    f["icons/favicon.svg"] = svg('<style>@media (prefers-color-scheme:dark){.f g[stroke]{stroke:#F3EEE2}'
                                 '.f g[fill]{fill:#F3EEE2}}</style>'
                                 + sun(512, 512, 230) + f'<g class="f">{figure(C["ink"], 60, 14)}</g>', 1024, 1024, crop)
    f["icons/safari-pinned-tab.svg"] = svg(mark("#000000", mono=True, bold=True), 1024, 1024, crop)
    for theme in ("light", "dark"):
        for layout in ("horizontal", "stacked"):
            body, _, _ = wordmark(theme, layout)
            f[f"src/wordmark/zimankit-wordmark-{layout}-{theme}.svg"] = body
    for name, (w, h) in SOCIAL.items():
        f[f"src/social/{name}-{w}x{h}.svg"] = card(w, h, "dark")
    f["src/social/og-image-light-1200x630.svg"] = card(1200, 630, "light")
    for name, (w, h) in ADS.items():
        for theme in ("dark", "light"):
            f[f"src/ads/{name}-{w}x{h}-{theme}.svg"] = card(w, h, theme, band=w * h > 20000 and min(w, h) >= 90)
    # Print, in millimetres (rendered at 300 dpi): an A4 poster and a round 75 mm sticker.
    poster = card(2480, 3508, "light").replace('width="2480" height="3508"', 'width="210mm" height="297mm"', 1)
    f["src/print/poster-a4.svg"] = poster
    f["print/sticker-75mm.svg"] = svg(disc_logo("light", rim=False), 75, 75, full, unit="mm")
    f["src/story/zimankit-logo-construction.svg"] = story_construction()
    return f


# ---------------------------------------------------------------- rendering


def run(*args: str) -> None:
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def png(src: Path, dst: Path, w: int, h: int | None = None, dpi: int | None = None) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    args = ["inkscape", str(src), "-o", str(dst), "-w", str(w), "-h", str(h or w)]
    if dpi:  # sets the PNG's pHYs density, for print
        args = ["inkscape", str(src), "-o", str(dst), "-d", str(dpi)]
    run(*args)


def flatten(src: Path, dst: Path) -> None:
    """Text to paths, so the result renders without the fonts."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    run("inkscape", str(src), "--export-text-to-path", "--export-plain-svg", "-o", str(dst))


def no_alpha(path: Path, bg: str) -> None:
    run("magick", str(path), "-background", bg, "-alpha", "remove", "-alpha", "off", str(path))


def render() -> int:
    for tool in ("inkscape", "magick"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is required to render PNGs (use --svg to skip)")
    for d in ("logo/png", "icons", "wordmark", "social", "ads", "print", "story", "kaggle"):
        for p in (OUT / d).rglob("*.png"):
            p.unlink()
    lg = OUT / "logo"

    # Logo: every size from favicon to print; small sizes use the bold mark.
    for s in (16, 24, 32, 48, 64, 96, 128, 192, 256, 512, 1024, 2048):
        png(lg / "svg" / ("zimankit-logo-small.svg" if s <= 48 else "zimankit-logo.svg"), lg / "png" / f"zimankit-logo-{s}.png", s)
    for s in (256, 512, 1024):
        png(lg / "svg" / "zimankit-logo-dark.svg", lg / "png" / f"zimankit-logo-dark-{s}.png", s)
    for name in ("mark", "mark-on-dark", "mark-mono-black", "mark-mono-white"):
        for s in (64, 128, 256, 512, 1024):
            src = "zimankit-mark-small.svg" if name == "mark" and s <= 64 else f"zimankit-{name}.svg"
            png(lg / "svg" / src, lg / "png" / f"zimankit-{name}-{s}.png", s)

    # Icons: favicons, PWA, Apple, Windows, stores.
    ic = OUT / "icons"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        small = []
        for s in (16, 32, 48):
            p = ic / f"favicon-{s}x{s}.png"
            png(lg / "svg" / ("zimankit-mark-small.svg" if s <= 32 else "zimankit-logo-small.svg"), p, s)
            small.append(str(p))
        run("magick", *small, str(ic / "favicon.ico"))
        for name, size, kw in (
            ("apple-touch-icon", 180, {}),
            ("android-chrome-192x192", 192, {"rounded": True}),
            ("android-chrome-512x512", 512, {"rounded": True}),
            ("maskable-icon-512x512", 512, {"safe": 0.66}),
            ("mstile-150x150", 150, {"safe": 0.7}),
            ("app-store-1024x1024", 1024, {}),
            ("play-store-512x512", 512, {}),
        ):
            src = tmpd / f"{name}.svg"
            src.write_text(app_icon(size, **kw), encoding="utf-8")
            png(src, ic / f"{name}.png", size)
            if name in ("apple-touch-icon", "app-store-1024x1024", "play-store-512x512"):
                no_alpha(ic / f"{name}.png", C["sand"])  # the stores reject transparency
    (ic / "site.webmanifest").write_text(json.dumps({
        "name": "zimankit", "short_name": "zimankit",
        "description": "Kurdish language toolkit for Sorani and Kurmanji",
        "icons": [{"src": "android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "maskable-icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
        "theme_color": C["night"], "background_color": C["sand"], "display": "standalone",
    }, indent=2) + "\n", encoding="utf-8")

    # Everything with text: flatten, then PNG at 1x and 2x (wordmarks also 3x).
    for src in sorted((OUT / "src").rglob("*.svg")):
        rel = src.relative_to(OUT / "src")
        flat = OUT / rel.parent / "svg" / rel.name if rel.parts[0] == "wordmark" else OUT / rel
        flatten(src, flat)
        if rel.parts[0] == "print":
            png(flat, flat.with_suffix(".png"), 0, dpi=300)
            run("inkscape", str(flat), "-o", str(flat.with_suffix(".pdf")))
            continue
        w, h = (int(float(v)) for v in src.read_text().split('viewBox="')[1].split('"')[0].split()[2:])
        scales = (1, 2, 3) if rel.parts[0] == "wordmark" else (1, 2) if rel.parts[0] in ("ads", "story") else (1,)
        for k in scales:
            stem = flat.stem if k == 1 else f"{flat.stem}@{k}x"
            outdir = OUT / rel.parent / "png" if rel.parts[0] == "wordmark" else flat.parent
            png(flat, outdir / f"{stem}.png", w * k, h * k)
    sticker = OUT / "print" / "sticker-75mm.svg"
    png(sticker, sticker.with_suffix(".png"), 0, dpi=300)
    run("inkscape", str(sticker), "-o", str(sticker.with_suffix(".pdf")))

    # Kaggle cover: the hand-made layout in kaggle/kaggle-cover.svg with the mark at its centre.
    kc = OUT / "kaggle" / "kaggle-cover.svg"
    if kc.exists():
        png(kc, OUT / "kaggle" / "dataset-cover-image.png", 560, 280)

    return sum(1 for p in OUT.rglob("*") if p.suffix in (".png", ".ico", ".pdf"))


def write_kaggle_mark() -> None:
    """Refresh the mark inside the Kaggle cover between its <!-- mark --> comments."""
    kc = OUT / "kaggle" / "kaggle-cover.svg"
    if not kc.exists():
        return
    src = kc.read_text(encoding="utf-8")
    a, b = "<!-- mark -->", "<!-- /mark -->"
    if a in src and b in src:
        new = place(mark(C["pale"], uid="kg"), 228, 40, 104)
        head, rest = src.split(a, 1)
        kc.write_text(f"{head}{a}{new}{b}{rest.split(b, 1)[1]}", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--svg", action="store_true", help="write the SVG sources only")
    args = ap.parse_args()
    files = build()
    for name, content in files.items():
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    write_kaggle_mark()
    print(f"wrote {len(files)} SVG sources to assets/brand/")
    if not args.svg:
        print(f"rendered {render()} PNG/ICO/PDF files to assets/brand/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
