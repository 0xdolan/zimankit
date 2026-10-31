"""Sentence structure: heads and relations for the patterns the rules are meant to cover."""

import pytest

from zimankit.dependency import parse


def rels(sentence: str) -> list[tuple[str, str, int]]:
    return [(w.text, w.deprel, w.head) for w in parse(sentence).tokens]


@pytest.mark.parametrize("sentence, expected", [
    # ergative: oblique agent, direct object
    ("Min pirtûk xwend.", [("Min", "nsubj", 3), ("pirtûk", "obj", 3), ("xwend", "root", 0), (".", "punct", 3)]),
    # ezafe, preposition
    ("Min pirtûka nû li dibistanê xwend.", [("Min", "nsubj", 6), ("pirtûka", "obj", 6), ("nû", "nmod", 2), ("li", "case", 5),
                                            ("dibistanê", "obl", 6), ("xwend", "root", 0), (".", "punct", 6)]),
    # present tense, possessor, object without case marking
    ("Jina min nan dixwe.", [("Jina", "nsubj", 4), ("min", "nmod:poss", 1), ("nan", "obj", 4), ("dixwe", "root", 0), (".", "punct", 4)]),
    # goal after the verb
    ("Ez diçim malê.", [("Ez", "nsubj", 2), ("diçim", "root", 0), ("malê", "obl", 2), (".", "punct", 2)]),
    # copula
    ("Ew baş e.", [("Ew", "nsubj", 2), ("baş", "root", 0), ("e", "cop", 2), (".", "punct", 2)]),
    # coordination of nouns and of verbs, two-word preposition
    ("Ez û tu diçin bajêr.", [("Ez", "nsubj", 4), ("û", "cc", 3), ("tu", "conj", 1), ("diçin", "root", 0), ("bajêr", "obl", 4), (".", "punct", 4)]),
    ("Wî nan xwar û çû.", [("Wî", "nsubj", 3), ("nan", "obj", 3), ("xwar", "root", 0), ("û", "cc", 5), ("çû", "conj", 3), (".", "punct", 3)]),
    ("Ez ji bo te nameyek dinivîsim.", [("Ez", "nsubj", 6), ("ji", "case", 4), ("bo", "case", 4), ("te", "obl", 6), ("nameyek", "obj", 6),
                                        ("dinivîsim", "root", 0), (".", "punct", 6)]),
    # Sorani: subject, object, ezafe, preposition
    ("کوڕەکە کتێبێکی نوێی لە قوتابخانە خوێندەوە.", [("کوڕەکە", "nsubj", 6), ("کتێبێکی", "obj", 6), ("نوێی", "nmod", 2), ("لە", "case", 5),
                                                   ("قوتابخانە", "obl", 6), ("خوێندەوە", "root", 0), (".", "punct", 6)]),
    # Sorani: goal -ە on the verb, demonstrative ئەو … -ە, copula -ە
    ("من دەچمە ماڵەوە.", [("من", "nsubj", 2), ("دەچمە", "root", 0), ("ماڵەوە", "obl", 2), (".", "punct", 2)]),
    ("ئەو پیاوە باشە.", [("ئەو", "det", 2), ("پیاوە", "nsubj", 3), ("باشە", "root", 0), (".", "punct", 3)]),
    ("من و تۆ دەچینە بازاڕ.", [("من", "nsubj", 4), ("و", "cc", 3), ("تۆ", "conj", 1), ("دەچینە", "root", 0), ("بازاڕ", "obl", 4), (".", "punct", 4)]),
])
def test_structure(sentence, expected):
    assert rels(sentence) == expected


def test_every_word_reaches_the_root():
    for s in ("Min pirtûka nû li dibistanê xwend.", "Ez ji bo te nameyek dinivîsim, lê tu nahêyî.", "کوڕەکە کە هات، من چووم."):
        toks = parse(s).tokens
        assert sum(w.head == 0 for w in toks) == 1
        for w in toks:
            seen, h = set(), w
            while h.head:
                assert h.id not in seen
                seen.add(h.id)
                h = toks[h.head - 1]


def test_ergative_explanation_and_agreement():
    p = parse("Min tu dîtim.")
    verb = p.tokens[2]
    assert p.order == "subject object verb" and p.alignment["agreement_ok"] is False
    assert "ergative" in verb.detail and "Agreement problem" in verb.detail
    assert "oblique case" in p.tokens[0].detail
    assert "Agreement problem" not in parse("Min tu dîtî.").tokens[2].detail


def test_coordinated_subject_is_not_an_agreement_error():
    assert "Agreement problem" not in parse("Ez û tu diçin bajêr.").tokens[3].detail


def test_labels_and_kurdish_terms():
    kmr = parse("Min pirtûk xwend.").tokens
    assert (kmr[0].relation, kmr[0].kurdish, kmr[1].kurdish) == ("subject", "kirde", "bireser")
    ckb = parse("ئەو پیاوە باشە.").tokens
    assert ckb[2].relation == "predicate" and ckb[2].kurdish == "ناو" and ckb[1].kurdish == "بکەر"
    assert parse("").tokens == []


def test_prefers_the_simplest_fitting_reading():
    assert parse("Min li dibistanê xwend.").tokens[2].segmentation == "dibistan+ê"
    assert parse("کتێبێکی نوێ").tokens[0].segmentation == "کتێب+ێک+ی"


def test_function_and_module_do_not_collide():
    import zimankit

    assert zimankit.parse("Ew baş e.").lang == "kmr"
    assert zimankit.parse("Ew baş e.").tokens[1].deprel == "root"
