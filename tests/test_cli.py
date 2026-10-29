"""The zimankit command: every subcommand runs and prints what the guide shows."""

import json

import pytest

from zimankit import __version__
from zimankit.cli import main


def run(capsys, *argv: str) -> str:
    main(list(argv))
    return capsys.readouterr().out


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert capsys.readouterr().out.strip() == f"zimankit {__version__}"


def test_tokenize_json(capsys):
    toks = json.loads(run(capsys, "tokenize", "--json", "Min pirtûk xwend."))
    assert [t["text"] for t in toks] == ["Min", "pirtûk", "xwend", "."]
    assert toks[-1] == {"text": ".", "kind": "punct", "start": 16, "end": 17}


@pytest.mark.parametrize("argv, expected", [
    (["normalize", "كوردي"], "کوردی"),
    (["ipa", "--syllables", "jinekê"], "ʒɪ.nɛ.keː"),
    (["translit", "Îro hewa xweş e"], "ئیرۆ هەوا خوەش ئە"),
    (["lid", "Îro hewa xweş e"], "kmr\t1.0\tÎro hewa xweş e"),
    (["validate", "كتێب"], "كتێب\tکتێب\tOK"),
])
def test_commands(capsys, argv, expected):
    assert run(capsys, *argv).strip() == expected


def test_conjugate_and_ergativity(capsys):
    assert run(capsys, "conjugate", "kirin").splitlines()[0] == "dikim\ttense=present,mood=indicative,person=1sg,agreement=subject"
    out = json.loads(run(capsys, "ergativity", "Min tu dîtim."))
    assert out["alignment"] == "ergative" and out["agreement_ok"] is False
