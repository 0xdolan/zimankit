"""The tutorials are generated from the skills: any change to a rule must be reflected in the docs."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _gen():
    spec = importlib.util.spec_from_file_location("gen_tutorials", ROOT / "scripts" / "gen_tutorials.py")
    mod = sys.modules.get("gen_tutorials") or importlib.util.module_from_spec(spec)
    sys.modules["gen_tutorials"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_tutorials_up_to_date():
    """Fails if a lesson table no longer matches the code: run `python scripts/gen_tutorials.py`."""
    assert _gen().main(["--check"]) == 0


def test_every_lesson_has_level_and_navigation():
    gen = _gen()
    for lang in ("ckb", "kmr"):
        lessons = gen.lessons_of(lang)
        assert [l.number for l in lessons] == list(range(1, len(lessons) + 1))
        for l in lessons:
            text = l.path.read_text(encoding="utf-8")
            assert "**Level:**" in text and text.startswith("<!-- nav:top -->"), l.path
