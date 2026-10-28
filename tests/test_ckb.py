import pytest

from zimankit.shared_utils.schema import SimpleLexicon
from zimankit.skills_ckb import verbs
from zimankit.skills_ckb.morphology import CkbAnalyzer, split_definite, split_enclitic
from zimankit.skills_ckb.orthography import normalize, normalize_word, spelling_variants, validate_word
from zimankit.skills_ckb.phonology_ipa import syllables, to_ipa, to_latin


@pytest.mark.parametrize("raw, expected", [
    ("كتێب", "کتێب"),                       # Arabic kaf
    ("ھەموو", "هەموو"),                     # heh doachashmee
    ("به‌ڕێوه‌به‌ر", "بەڕێوەبەر"),          # legacy heh+ZWNJ
    ("رۆژ", "ڕۆژ"),                          # initial r
    ("سەەر", "سەر"),                         # doubled ae
    ("کتێب​ەکە", "کتێبەکە"),           # zero-width space after non-joining? ب joins -> ZWNJ kept? see below
])
def test_normalize_word(raw, expected):
    got = normalize_word(raw)
    assert got.replace("‌", "") == expected


def test_digits_and_punctuation():
    assert normalize("ساڵی 2015, باشە?") == "ساڵی ٢٠١٥، باشە؟"


def test_validate():
    assert validate_word("کتێب") == []
    assert "arabic-only letter" in validate_word("صەبر")
    assert any("initial" in p for p in validate_word("رۆژ"))


@pytest.mark.parametrize("word, ipa", [
    ("کوردستان", "kuɾd(ɯ)staːn"), ("بردن", "b(ɯ)ɾd(ɯ)n"), ("خواردن", "xwaːɾd(ɯ)n"),
    ("هاتووە", "haːtuːwæ"), ("ئنجا", "ʔ(ɯ)ndʒaː"), ("ڕۆژ", "roːʒ"), ("چای", "tʃaːj"), ("و", "u"),
])
def test_ipa(word, ipa):
    assert to_ipa(word) == ipa


def test_latin_and_syllables():
    assert to_latin("کوردستان") == "kurdistan"
    assert to_latin("هەڵبژاردن") == "hellbijardin"
    assert syllables("کتێبەکەم") == ["kɯ", "teː", "bæ", "kæm"]


def test_verbs_paradigm():
    idx = verbs.default_index()
    assert idx.lookup("دەکەم")[0].lemma == "کردن"
    assert any(f.features.get("alignment") == "ergative" for f in idx.lookup("کردم"))
    assert idx.lookup("هەڵدەگرم")[0].lemma == "هەڵگرتن"
    assert idx.lookup("دێت")[0].lemma == "هاتن"


def test_analyzer_with_lexicon():
    lex = SimpleLexicon()
    for w in ("ماڵ", "ماسی", "دەرگا"):
        lex.add(w, "NOUN")
    an = CkbAnalyzer(lex)
    a = an.best("لەماڵەکانمانیشدا")
    assert a.segmentation == "لە+ماڵ+ەکان+مان+یش+دا"
    assert an.best("ماسییەکە").lemma == "ماسی"
    assert an.best("دەرگاکە").segmentation == "دەرگا+کە"


def test_helpers():
    assert split_enclitic("کتێبەکەم") == ("کتێبەکە", "م")
    assert split_definite("پیاوەکە") == ("پیاو", "ەکە")
    assert "گوڵ" in spelling_variants("گول")


@pytest.mark.parametrize("form, lemma, feature", [
    ("کردووە", "کردن", ("agent", "external")),        # agent clitic on an earlier word
    ("بووە", "بوون", ("tense", "present_perfect")),   # no extra و after a وو stem
    ("ڕایگەیاند", "ڕاگەیاندن", ("agent", "3sg")),     # clitic after the preverb
    ("دەردەکەوێت", "دەرکەوتن", ("person", "3sg")),    # کەو ends in a glide, not a vowel
    ("بەکاربهێنێت", "بەکارهێنان", ("mood", "subjunctive")),  # light verb keeps ب
    ("دەبێتە", "بوون", ("goal", "yes")),               # directional -ە
    ("نەیەم", "هاتن", ("polarity", "neg")),            # irregular negative subjunctive
])
def test_verb_regressions(form, lemma, feature):
    from zimankit.skills_ckb.morphology import CkbAnalyzer

    a = CkbAnalyzer().best(form)
    assert a.lemma == lemma and a.features.get(feature[0]) == feature[1]


def test_verbal_noun_is_noun():
    lex = SimpleLexicon()
    lex.add("نووسین", "VERB")
    a = CkbAnalyzer(lex).best("نووسینەکە")
    assert a.lemma == "نووسین" and a.pos == "NOUN"


def test_final_cluster_repair():
    assert to_ipa("نەمکرد") == "næmk(ɯ)ɾd"


def test_plural_person_syncretism():
    """2pl and 3pl share ـن in set 1: one reading listing both persons, not an arbitrary pick."""
    idx = verbs.default_index()
    readings = [f.features for f in idx.lookup("دەکەن") if f.lemma == "کردن"]
    assert [r["person"] for r in readings] == ["2pl|3pl"]
    assert {f.features.get("person") for f in idx.lookup("دەکەین")} == {"1pl"}


@pytest.mark.parametrize("stem", ["پیاو", "کتێب", "دەرگا", "ماسی", "خانە", "مامۆستا"])
def test_decline_round_trip(stem):
    """Every generated nominal form is analysed back to its stem."""
    from zimankit.skills_ckb.morphology import decline

    lex = SimpleLexicon()
    lex.add(stem, "NOUN")
    an = CkbAnalyzer(lex)
    for cell, form in decline(stem):
        if form is None or cell in ("bare", "dem"):
            continue
        assert any(a.lemma == stem for a in an.analyze(form)[:3]), (cell, form)


@pytest.mark.parametrize("inf, form, feature", [
    ("هاتن", "مەیە", ("polarity", "neg")),
    ("ویستن", "دەمەوێت", ("person", "1sg")),
    ("گوتن", "گوترا", ("voice", "passive")),
    ("ناردن", "نێردرا", ("voice", "passive")),
])
def test_verb_fixes(inf, form, feature):
    idx = verbs.default_index()
    assert any(f.lemma == inf and f.features.get(feature[0]) == feature[1] for f in idx.lookup(form))
    assert not idx.lookup("دەوێم") and not idx.lookup("ڵرا")


def test_normalize_word_start_after_foreign_letter():
    """A non-Kurdish letter inside a word is not a word boundary (no ئ inserted after ث)."""
    assert normalize("ثەورە") == "ثەورە"
    assert normalize("اسپ") == "ئاسپ"
    assert normalize("ئەو رۆژە") == "ئەو ڕۆژە"
