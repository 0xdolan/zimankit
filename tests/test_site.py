"""The website's colours stay readable: WCAG AA (4.5:1) for text, in both themes."""

import re
from pathlib import Path

import pytest

CSS = (Path(__file__).resolve().parents[1] / "site" / "css" / "site.css").read_text(encoding="utf-8")


def tokens(block_start: str) -> dict[str, str]:
    block = CSS[CSS.index(block_start):]
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", block[:block.index("\n}")]))


LIGHT = tokens(":root {")
DARK = {**LIGHT, **tokens(':root[data-theme="dark"] {')}


def contrast(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = [(x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4) for x in c]
        return .2126 * r + .7152 * g + .0722 * b
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
def test_text_contrast(theme):
    text = ["foreground", "muted-foreground", "destructive", "ok"] + [k for k in theme if k.startswith("rel-")]
    for fg in text:
        for bg in ("background", "card", "surface", "muted"):
            assert contrast(theme[fg], theme[bg]) >= 4.5, f"{fg} on {bg}: {contrast(theme[fg], theme[bg]):.2f}"
    assert contrast(theme["primary-foreground"], theme["primary"]) >= 4.5


def test_light_is_the_default():
    assert LIGHT["background"] == "#FFFFFF"
    assert 'data-theme="light"' in (Path(__file__).resolve().parents[1] / "scripts" / "build_site.py").read_text(encoding="utf-8")


TOOLS = (Path(__file__).resolve().parents[1] / "site" / "js" / "sentence-tools.js").read_text(encoding="utf-8")
FONTS = Path(__file__).resolve().parents[1] / "site" / "fonts"


@pytest.mark.parametrize("theme, ground", [("light", LIGHT["card"]), ("dark", DARK["card"])])
def test_colour_presets_are_readable(theme, ground):
    presets = re.findall(rf"{theme}: \{{ (root: .*?) \}}", TOOLS)
    assert len(presets) == 2  # the single-colour preset is checked below
    for preset in presets:
        for name, colour in re.findall(r"(\w+): \"(#[0-9A-F]{6})\"", preset):
            assert contrast(colour, ground) >= 4.5, f"{theme} {name} {colour}: {contrast(colour, ground):.2f}"


def test_single_colour_preset_is_readable():
    assert contrast("#171717", LIGHT["card"]) >= 4.5 and contrast("#FAFAFA", DARK["card"]) >= 4.5


def test_fonts_are_hosted_and_licensed():
    for name in ("Manrope-latin", "Manrope-latin-ext", "Sahel", "Sahel-Bold", "Estedad-arabic", "Vazirmatn-arabic"):
        assert (FONTS / f"{name}.woff2").stat().st_size > 1000
        assert f"../fonts/{name}.woff2" in CSS
    for family in ("Manrope", "Sahel", "Estedad", "Vazirmatn"):
        assert "Open Font License" in (FONTS / f"OFL-{family}.txt").read_text(encoding="utf-8")


def test_fonts_contain_the_kurdish_letters():
    tt = pytest.importorskip("fontTools.ttLib")
    pytest.importorskip("brotli")

    def covers(*files):
        out = set()
        for f in files:
            out |= set(tt.TTFont(FONTS / f).getBestCmap())
        return out

    sorani = "ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ"
    for f in ("Sahel.woff2", "Sahel-Bold.woff2", "Estedad-arabic.woff2", "Vazirmatn-arabic.woff2"):
        assert [c for c in sorani if ord(c) not in covers(f)] == [], f
    latin = covers("Manrope-latin.woff2", "Manrope-latin-ext.woff2")
    assert [c for c in "abcçdeêfghiîjklmnopqrsştuûvwxyzÇÊÎŞÛ" if ord(c) not in latin] == []


def _tools():
    import importlib.util

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("playground_tools", root / "site" / "py" / "playground_tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("verb", ["کردن", "چوون", "kirin", "dîtin"])
def test_conjugate_view_keeps_every_form(verb):
    r = _tools().conjugate(verb)
    shown = sum(len(c["affirmative"]) + len(c["negative"]) for g in r["groups"] for c in g["rows"]) + len(r["other"])
    assert shown == r["count"] > 20


def test_verb_page_links_exist():
    root = Path(__file__).resolve().parents[1] / "docs" / "tutorials"
    t = _tools()
    assert (root / "kmr/reference/verbs" / f"{t.conjugate('kirin')['slug']}.md").exists()
    assert (root / "ckb/reference/verbs" / f"{t.conjugate('کردن')['slug']}.md").exists()


def test_tool_results_are_structured():
    t = _tools()
    assert t.ipa("jinekê")[0]["syllables"] == ["ʒɪ", "nɛ", "keː"]
    assert t.normalize(["كوردي"])[0]["changes"][0]["from_code"] == "U+0643"
    assert t.validate("wörld")[0]["problems"]
    assert t.lid(["Îro hewa xweş e"])[0]["name"].startswith("Northern")
    assert t.tokens(["Min."])[0]["tokens"][-1]["kind"] == "punct"
    assert "error" in t.conjugate("hello")


def test_learn_links_point_at_real_pages():
    root = Path(__file__).resolve().parents[1]
    learn = (root / "site" / "js" / "learn.js").read_text(encoding="utf-8")
    paths = re.findall(r'"([\w/.-]+\.md)"', learn)
    assert len(paths) > 40
    assert [p for p in paths if not (root / "docs" / p).exists()] == []
