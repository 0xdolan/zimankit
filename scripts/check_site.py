#!/usr/bin/env python3
"""Check the built website in a real browser, at phone to desktop widths.

Fails on JavaScript errors, failed requests, sideways page scrolling, broken images, and
controls too small to tap on a phone. Exercises the playground and the mobile menu.

    scripts/build_site.sh && uv run --no-project --with playwright python scripts/check_site.py
    uv run --no-project --with playwright python scripts/check_site.py --shots assets/brand/screenshots
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index", "playground", "guide", "story", "brand"]
WIDTHS = [320, 375, 768, 1024, 1440]
TAP = 44  # minimum touch target, CSS px
# Inline links in running text are exempt: WCAG 2.5.8 excludes them.
TAP_SELECTOR = "button:not(.w), .nav a, .brand, .icon-btn, .btn, .dl a, footer nav a, summary, select, textarea, input[type=text]"


def launch(p):
    chrome = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium") if os.path.exists(c)), None)
    return p.chromium.launch(executable_path=chrome, args=["--no-sandbox"]) if chrome else p.chromium.launch()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shots", help="also save the website screenshots into this folder")
    args = ap.parse_args()
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT / "_site"))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/"
    problems: list[str] = []

    with sync_playwright() as p:
        browser = launch(p)

        def new_page(width, height=900, dark=False, mobile=False, scale=1):
            ctx = browser.new_context(viewport={"width": width, "height": height}, is_mobile=mobile, has_touch=mobile,
                                      device_scale_factor=scale)
            if dark:
                ctx.add_init_script("try { localStorage.setItem('zimankit-theme', 'dark') } catch (e) {}")
            page = ctx.new_page()
            where = f"{width}px"
            page.on("pageerror", lambda e: problems.append(f"{where}: JS error: {e}"))
            page.on("response", lambda r: problems.append(f"{where}: {r.status} {r.url}") if r.status >= 400 else None)
            return page

        def ready(page):
            page.goto(base + "playground.html")
            page.wait_for_selector("#s-diagram .w", timeout=180000)
            page.wait_for_timeout(600)

        for width in WIDTHS:
            mobile = width < 800
            page = new_page(width, mobile=mobile)
            for name in PAGES:
                where = f"{name} at {width}px"
                if name == "playground":
                    ready(page)
                else:
                    page.goto(f"{base}{name}.html")
                    page.wait_for_load_state("networkidle")
                over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                if over > 0:
                    wide = page.evaluate("""() => [...document.querySelectorAll('body *')].filter((e) =>
                        e.getBoundingClientRect().right > innerWidth + 1 && !e.closest('pre, table, .table-wrap, .diagram, .tools, .result'))
                        .slice(0, 4).map((e) => e.tagName + '.' + e.className)""")
                    problems.append(f"{where}: page scrolls sideways by {over}px: {wide}")
                page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager' })")
                page.wait_for_timeout(300)
                broken = page.evaluate("[...document.images].filter((i) => i.complete && !i.naturalWidth).map((i) => i.src)")
                if broken:
                    problems.append(f"{where}: broken images {broken}")
                if mobile:
                    small = page.evaluate(f"""() => [...document.querySelectorAll({TAP_SELECTOR!r})]
                        .filter((e) => e.offsetParent !== null && !e.closest('.s-words'))
                        .map((e) => [e.tagName, e.className, (e.textContent || '').trim().slice(0, 18), Math.round(e.getBoundingClientRect().height)])
                        .filter((r) => r[3] < {TAP} - 0.5).slice(0, 5)""")
                    if small:
                        problems.append(f"{where}: small tap targets {small}")
            page.context.close()

        # hostile input must stay text in every view
        page = new_page(1280)
        ready(page)
        page.evaluate("window.__xss = 0")
        attack = '<img src=x onerror="window.__xss=1"><script>window.__xss=1</script>'
        page.fill("#s-input", attack)
        page.wait_for_timeout(400)
        for tool in ("analyze", "ipa", "translit", "conjugate", "ergativity", "lid", "normalize", "validate", "tokenize"):
            page.click(f'.tools button[data-cmd="{tool}"]')
            page.fill("#input", attack)
            page.wait_for_timeout(350)
            if page.locator("#t-result .res").count():
                page.click(".seg button:has-text('JSON')")
                page.wait_for_timeout(100)
                page.click(".seg button:has-text('Result')")
        if page.evaluate("window.__xss") or page.locator("#t-result img, #s-diagram img, #s-panel img").count():
            problems.append("input was treated as HTML")

        # the mobile menu and the one-icon-at-a-time buttons
        page = new_page(375, mobile=True)
        page.goto(base + "index.html")
        for label, sel in (("theme", ".theme svg"), ("menu", ".menu svg")):
            shown = page.locator(sel).evaluate_all("(e) => e.filter((i) => getComputedStyle(i).display !== 'none').length")
            if shown != 1:
                problems.append(f"{label} button shows {shown} icons")
        page.click(".theme")
        if page.get_attribute("html", "data-theme") != "dark":
            problems.append("theme button does not switch to dark")
        page.click(".theme")
        page.click(".theme")
        page.evaluate("try { localStorage.removeItem('zimankit-theme') } catch (e) {}")
        page.click(".menu")
        if not page.is_visible(".nav a[href='guide.html']"):
            problems.append("mobile menu does not open")
        page.keyboard.press("Escape")
        if page.is_visible(".nav a[href='guide.html']"):
            problems.append("mobile menu does not close on Escape")

        # the playground, at phone width
        page = new_page(375, 800, mobile=True)
        ready(page)
        page.tap("#s-words tr[data-id='1']")
        if "Min" not in page.inner_text("#s-panel h3"):
            problems.append("word table does not explain the word")
        page.fill("#s-input", "")
        page.wait_for_timeout(500)
        if "Type a sentence" not in page.inner_text("#s-diagram"):
            problems.append("no empty state")
        page.click("#s-examples .ex-group:nth-child(2) button:first-of-type")
        page.wait_for_timeout(300)
        if page.get_attribute("#s-words tr[data-id='1'] button", "dir") != "auto":
            problems.append("words have no direction")
        for tool in ("analyze", "ipa", "translit", "conjugate", "ergativity", "lid", "normalize", "validate", "tokenize"):
            page.click(f'.tools button[data-cmd="{tool}"]')
            page.wait_for_timeout(250)
            shown = page.inner_text("#t-result .res-body")
            if not shown.strip() or "could not be processed" in shown:
                problems.append(f"tool {tool} gave no result: {shown[:60]!r}")
            if page.locator("#t-learn .learn a").count() == 0:
                problems.append(f"tool {tool} has no learn links")
            bad = page.locator("#t-learn .learn a").evaluate_all("(a) => a.filter((x) => x.textContent.endsWith('.md')).map((x) => x.href)")
            if bad:
                problems.append(f"tool {tool}: learn link without a title: {bad}")
            wide = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if wide > 0:
                problems.append(f"tool {tool} scrolls sideways by {wide}px at phone width")
            page.click(".seg button:has-text('JSON')")
            page.wait_for_timeout(100)
            if not page.inner_text("pre.json").strip().startswith(("[", "{")):
                problems.append(f"tool {tool} has no JSON view")
            page.click(".seg button:has-text('Result')")
        page.click('.tools button[data-cmd="conjugate"]')
        page.wait_for_timeout(250)
        if page.locator(".verb-card").count() < 5:
            problems.append("conjugate does not show its grids")
        page.click('.tools button[data-cmd="sentence"]')
        over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        if over > 0:
            problems.append(f"playground tools scroll sideways by {over}px")

        # fonts: Manrope for Latin, Sahel by default for Arabic script, and the choice sticks
        page = new_page(1280)
        ready(page)
        for family, sample in (("Manrope", "a"), ("Sahel", "ێ")):
            if not page.evaluate("async ([f, t]) => (await document.fonts.load(`700 20px ${f}`, t)).length > 0", [family, sample]):
                problems.append(f"font {family} did not load")
        stack = page.evaluate("getComputedStyle(document.querySelector('#s-diagram .w .t')).fontFamily")
        if "Manrope" not in stack or "Sahel" not in stack:
            problems.append(f"diagram does not use the font stack: {stack}")
        for family in ("Estedad", "Vazirmatn", "Sahel"):
            page.select_option("footer select.rtl-font", family)
            page.wait_for_timeout(300)
            used = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--rtl-font')")
            loaded = page.evaluate("(f) => document.fonts.check(`16px ${f}`, 'ێ')", family)
            if family not in used or not loaded:
                problems.append(f"choosing {family} did not apply: {used}, loaded={loaded}")

        # selecting and resetting, and the lessons for a word
        page.click('.w[data-id="1"]')
        page.wait_for_timeout(150)
        if page.locator(".diagram .dim").count() == 0 or not page.is_visible("#s-reset"):
            problems.append("selecting a word does not dim the rest or offer a reset")
        if page.locator("#s-panel .learn a").count() == 0:
            problems.append("a selected word has no learn links")
        page.click("#s-reset")
        page.wait_for_timeout(150)
        if page.locator(".diagram .dim").count() or page.is_visible("#s-reset"):
            problems.append("the reset button does not bring the colours back")
        page.click('.w[data-id="1"]')
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        if page.locator(".diagram .dim").count():
            problems.append("Escape does not clear the selection")
        page.click('.w[data-id="1"]')
        page.click("#s-panel .back")
        page.wait_for_timeout(100)
        if page.locator(".diagram .dim").count():
            problems.append("the back button does not clear the selection")
        page.click('#s-legend button[data-rel="subject"]')
        page.wait_for_timeout(100)
        page.click("#s-reset")
        page.wait_for_timeout(100)
        if page.locator(".diagram .dim").count():
            problems.append("the reset button does not clear a colour filter")

        # colours: a preset, a custom colour, a reset
        stroke = "getComputedStyle(document.querySelector('.edge.g-nsubj .arc')).stroke"
        before = page.evaluate(stroke)
        page.click("#c-toggle")
        page.click("#c-presets button:has-text('High contrast')")
        page.wait_for_timeout(150)
        if page.evaluate(stroke) == before:
            problems.append("colour preset did not change the diagram")
        page.locator("#c-swatches input[data-group='nsubj']").evaluate(
            "(i) => { i.value = '#ffff00'; i.dispatchEvent(new Event('input', { bubbles: true })) }")
        page.wait_for_timeout(150)
        if page.evaluate(stroke) != "rgb(255, 255, 0)":
            problems.append("custom colour did not change the diagram")
        if "Hard to read" not in page.inner_text("#c-swatches"):
            problems.append("no warning for a colour that is hard to read")
        page.click("#c-presets button:has-text('Default')")
        page.wait_for_timeout(150)
        if page.evaluate(stroke) != before:
            problems.append("reset did not restore the colours")

        # export: each size, at the size it claims
        page.click("#x-open")
        page.wait_for_timeout(500)
        for size, (w, h) in {"1200x630": (2400, 1260), "1080x1080": (2160, 2160), "1080x1350": (2160, 2700), "1080x1920": (2160, 3840)}.items():
            page.select_option("#x-size", size)
            page.wait_for_timeout(400)
            with page.expect_download() as dl:
                page.click("#x-download")
            path = dl.value.path()
            data = Path(path).read_bytes()
            got = (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))
            phys = data.find(b"pHYs")
            ppm = int.from_bytes(data[phys + 4:phys + 8], "big") if phys > 0 else 0
            if got != (w, h) or not 5660 < ppm < 5680:  # 144 dpi = 5669 pixels per metre
                problems.append(f"export {size}: got {got}, {ppm} ppm")
            if args.shots:
                Path(args.shots, f"export-{size}.png").write_bytes(data)
        page.select_option("#x-size", "1200x630")
        for fmt, starts in (("jpg", b"\xff\xd8\xff"), ("pdf", b"%PDF-"), ("svg", b"<svg ")):
            page.select_option("#x-format", fmt)
            page.wait_for_timeout(300)
            with page.expect_download() as dl:
                page.click("#x-download")
            data = Path(dl.value.path()).read_bytes()
            name = dl.value.suggested_filename
            if not data.startswith(starts) or not name.endswith("." + fmt):
                problems.append(f"export {fmt}: {name} starts {data[:8]!r}")
            if fmt == "jpg" and (data[13], int.from_bytes(data[14:16], "big")) != (1, 144):
                problems.append("export jpg: no 144 dpi in the header")
            if fmt == "pdf" and (b"/MediaBox [0 0 1200 630]" not in data or not data.rstrip().endswith(b"%%EOF")):
                problems.append("export pdf: wrong page")
            if fmt == "svg" and (b"@font-face" not in data or b"<text" not in data or b"xwend" not in data):
                problems.append("export svg: no fonts or text inside")
        page.select_option("#x-format", "png")
        page.click("#x-close")

        if args.shots:
            out = Path(args.shots)

            def part(page, name):
                box = page.locator("#sent").bounding_box()
                y = box["y"] + page.evaluate("scrollY")
                page.screenshot(path=str(out / f"{name}.png"), full_page=True,
                                clip={"x": box["x"] - 20, "y": y - 20, "width": box["width"] + 40, "height": box["height"] + 8})

            page = new_page(1180)
            ready(page)
            part(page, "website-sentence")
            page.click('.w[data-id="6"]')
            page.wait_for_timeout(250)
            part(page, "website-sentence-word")
            page.click("#s-examples .ex-group:nth-child(2) button:first-of-type")
            page.wait_for_timeout(300)
            page.click('.w[data-id="2"]')
            page.wait_for_timeout(250)
            part(page, "website-sentence-sorani")
            page = new_page(1180, dark=True)
            ready(page)
            page.click('.w[data-id="1"]')
            page.wait_for_timeout(250)
            part(page, "website-sentence-dark")
            page = new_page(390, 844, mobile=True, scale=2)
            ready(page)
            page.locator("#s-diagram").scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            page.screenshot(path=str(out / "website-sentence-mobile.png"))
            page = new_page(1360, 860)
            ready(page)
            page.click('.tools button[data-cmd="analyze"]')
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / "website-playground.png"))
            for name, kw in (("website-home", {}), ("website-home-dark", {"dark": True})):
                page = new_page(1360, 860, **kw)
                page.goto(base + "index.html")
                page.wait_for_load_state("networkidle")
                page.screenshot(path=str(out / f"{name}.png"))
            page = new_page(390, 844, mobile=True, scale=2)
            page.goto(base + "index.html")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(out / "website-home-mobile.png"))
        browser.close()
    server.shutdown()
    for line in sorted(set(problems)):
        print("PROBLEM", line)
    print(f"checked {len(PAGES)} pages at {WIDTHS}: {len(set(problems))} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
