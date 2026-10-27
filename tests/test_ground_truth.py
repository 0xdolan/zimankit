"""The verification matrix from the project brief - must always pass."""

import pytest

from zimankit.skills_ckb.morphology import CkbAnalyzer
from zimankit.skills_ckb.phonology_ipa import to_ipa as ckb_ipa
from zimankit.skills_kmr.morphology import KmrAnalyzer
from zimankit.skills_kmr.phonology_ipa import to_ipa as kmr_ipa

CKB = CkbAnalyzer()
KMR = KmrAnalyzer()


@pytest.mark.parametrize(
    "surface, lemma, features, ipa",
    [
        ("پیاوەکە", "پیاو", {"definite": "def", "number": "sg"}, "pjaːwækæ"),
        ("کتێبەکەم", "کتێب", {"definite": "def", "enclitic": "1sg"}, "k(ɯ)teːbækæm"),
    ],
)
def test_ckb(surface, lemma, features, ipa):
    a = CKB.best(surface)
    assert a.lemma == lemma
    for k, v in features.items():
        assert a.features[k] == v
    assert ckb_ipa(surface) == ipa


def test_kmr_jineke():
    a = KMR.best("jinekê")
    assert (a.lemma, a.features["gender"], a.features["case"], a.features["number"]) == ("jin", "f", "obl", "sg")
    assert a.segmentation == "jin+ekê"
    assert kmr_ipa("jinekê") == "ʒɪnɛkeː"


def test_kmr_ditin():
    a = KMR.best("dîtin")
    assert a.pos == "VERB" and a.lemma == "dîtin"
    assert a.features["form"] == "infinitive"
    assert a.features["past_stem"] == "dît" and a.features["transitivity"] == "transitive"
    assert kmr_ipa("dîtin") == "diːtɯn"
