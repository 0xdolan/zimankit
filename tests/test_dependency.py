"""Sentence structure: heads and relations for the patterns the rules are meant to cover."""

import pytest

from zimankit.dependency import parse


def rels(sentence: str) -> list[tuple[str, str, int]]:
    return [(w.text, w.deprel, w.head) for w in parse(sentence).tokens]


@pytest.mark.parametrize("sentence, expected", [
    # Sorani: adpositions without a noun, copula after -دا and with a person ending, definite ezafe
    ("پێی وت.", [("پێی", "obl", 2), ("وت", "root", 0), (".", "punct", 2)]),
    ("پارەم پێ نەما.", [("پارەم", "nsubj", 3), ("پێ", "obl", 3), ("نەما", "root", 0), (".", "punct", 3)]),
    ("بۆمی نووسی.", [("بۆمی", "obl", 2), ("نووسی", "root", 0), (".", "punct", 2)]),
    # verbs written over several tokens
    ("هەڵم گرت.", [("هەڵم", "compound:prt", 2), ("گرت", "root", 0), (".", "punct", 2)]),
    ("ڕای گەیاند.", [("ڕای", "compound:prt", 2), ("گەیاند", "root", 0), (".", "punct", 2)]),
    ("دەستم پێ کرد.", [("دەستم", "compound:prt", 3), ("پێ", "compound:prt", 3), ("کرد", "root", 0), (".", "punct", 3)]),
    ("دەستم لێ دا.", [("دەستم", "obj", 3), ("لێ", "compound:prt", 3), ("دا", "root", 0), (".", "punct", 3)]),
    ("من کتێبەکەم هەڵ گرت.", [("من", "nsubj", 4), ("کتێبەکەم", "obj", 4), ("هەڵ", "compound:prt", 4), ("گرت", "root", 0), (".", "punct", 4)]),
    # subordinate clauses: the main verb stays the root
    ("دەچم بۆ سەیران، کە بەهار هات.", [("دەچم", "root", 0), ("بۆ", "case", 3), ("سەیران", "obl", 1), ("،", "punct", 1), ("کە", "mark", 7), ("بەهار", "nsubj", 7), ("هات", "advcl", 1), (".", "punct", 1)]),
    ("پیاوەکەی کە نانی خوارد مێوان بوو.", [("پیاوەکەی", "nsubj", 6), ("کە", "mark", 4), ("نانی", "obj", 4), ("خوارد", "acl:relcl", 1), ("مێوان", "obl", 6), ("بوو", "root", 0), (".", "punct", 6)]),
    # free order, and a passive subject
    ("نان من دەخۆم.", [("نان", "obj", 3), ("من", "nsubj", 3), ("دەخۆم", "root", 0), (".", "punct", 3)]),
    ("نامەکە نێردرا.", [("نامەکە", "nsubj:pass", 2), ("نێردرا", "root", 0), (".", "punct", 2)]),
    # a frame with a demonstrative
    ("لەو شارەدا تۆم بینی.", [("لەو", "case", 2), ("شارەدا", "obl", 4), ("تۆم", "obj", 4), ("بینی", "root", 0), (".", "punct", 4)]),
    # an object clitic on the verb
    ("ئەو دەیبینێت.", [("ئەو", "nsubj", 2), ("دەیبینێت", "root", 0), (".", "punct", 2)]),
    ("پێی لێ هەڵگرت.", [("پێی", "obj", 3), ("لێ", "obl", 3), ("هەڵگرت", "root", 0), (".", "punct", 3)]),
    ("من لە ماڵدام.", [("من", "nsubj", 3), ("لە", "case", 3), ("ماڵدام", "root", 0), (".", "punct", 3)]),
    ("تۆ زیرەکیت.", [("تۆ", "nsubj", 2), ("زیرەکیت", "root", 0), (".", "punct", 2)]),
    ("پیاوە باشەکە هات.", [("پیاوە", "nsubj", 3), ("باشەکە", "amod", 1), ("هات", "root", 0), (".", "punct", 3)]),
    ("دەرگا گەورەکە داخرا.", [("دەرگا", "nsubj:pass", 3), ("گەورەکە", "amod", 1), ("داخرا", "root", 0), (".", "punct", 3)]),
    # … but not a subject before a definite object
    ("مامۆستا کتێبەکە دەخوێنێت.", [("مامۆستا", "nsubj", 3), ("کتێبەکە", "obj", 3), ("دەخوێنێت", "root", 0), (".", "punct", 3)]),
    # Sorani past transitive: the agent clitic sits on the object
    ("نانم خوارد.", [("نانم", "obj", 2), ("خوارد", "root", 0), (".", "punct", 2)]),
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


def test_split_verb_reading_reaches_the_last_word():
    verb = parse("هەڵم نەگرت.").tokens[1]
    assert (verb.lemma, verb.upos, verb.features["agent"], verb.features["polarity"]) == ("هەڵگرتن", "VERB", "1sg", "neg")


def test_split_verb_does_not_join_across_punctuation():
    assert parse("هەڵم، گرت.").tokens[0].upos != "PART"


@pytest.mark.parametrize("sentence, lemma, number", [("ئەو دەرگایە باشە.", "دەرگا", "sg"), ("ئەم پیاوانە هاتن.", "پیاو", "pl"), ("ئەو پیاوەی کە هات.", "پیاو", "sg")])
def test_demonstrative_frame(sentence, lemma, number):
    noun = parse(sentence).tokens[1]
    assert parse(sentence).tokens[0].upos == "DET" and noun.lemma == lemma and noun.features["number"] == number


def test_sorani_grammar_terms():
    assert parse("نامەکە نێردرا.").tokens[0].kurdish == "جێگری بکەر"
    predicate = parse("ئەو پیاوە باشە.").tokens
    assert predicate[1].kurdish == "نیهاد" and predicate[2].kurdish == "تەواوکەری کاری ناتەواو"


@pytest.mark.parametrize("sentence, part", [
    ("من نان خوارد.", "agent clitic"), ("هاتمان.", "هاتین"), ("من دەچیت.", "1sg"), ("پیاوەکە دەچن.", "Usage"),
])
def test_sorani_agreement_warnings(sentence, part):
    assert any(part in n for n in parse(sentence).notes), parse(sentence).notes


@pytest.mark.parametrize("sentence", ["من نانم خوارد.", "ئازاد نانی خوارد.", "هاتین.", "من دەچم.", "پیاوەکە هات.", "نانم خوارد."])
def test_no_agreement_warning(sentence):
    assert not [n for n in parse(sentence).notes if "agreement" in n or "Usage" in n]


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
    assert ckb[2].relation == "predicate" and ckb[2].kurdish == "تەواوکەری کاری ناتەواو" and ckb[1].kurdish == "نیهاد"
    assert parse("").tokens == []


def test_prefers_the_simplest_fitting_reading():
    assert parse("Min li dibistanê xwend.").tokens[2].segmentation == "dibistan+ê"
    assert parse("کتێبێکی نوێ").tokens[0].segmentation == "کتێب+ێک+ی"


def test_function_and_module_do_not_collide():
    import zimankit

    assert zimankit.parse("Ew baş e.").lang == "kmr"
    assert zimankit.parse("Ew baş e.").tokens[1].deprel == "root"
