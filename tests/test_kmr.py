import pytest

from zimankit.skills_kmr import verbs
from zimankit.skills_kmr.morphology import KmrAnalyzer
from zimankit.shared_utils.schema import SimpleLexicon
from zimankit.skills_kmr.orthography import lower, normalize, validate_word
from zimankit.skills_kmr.phonology_ipa import KmrG2POptions, to_ipa
from zimankit.skills_kmr.syntax import detect_alignment
from zimankit.skills_kmr.translit import to_arabic


def test_normalize():
    assert normalize("Kürdistan") == "Kûrdistan"
    assert normalize("şéwe") == "şêwe"
    assert lower("ÎRO") == "îro" and lower("İro") == "iro"


def test_validate():
    assert validate_word("jinekê") == []
    assert validate_word("Erdoğan")


@pytest.mark.parametrize("w, ipa", [("xwarin", "xʷaːɾɯn"), ("rojname", "roːʒnaːmɛ"), ("'erd", "ʕɛɾd")])
def test_ipa(w, ipa):
    assert to_ipa(w) == ipa


def test_narrow():
    assert to_ipa("p'ir", KmrG2POptions(narrow=True)) == "pɪɾ"
    assert to_ipa("HDP'ê") == "hdpeː"
    assert to_ipa("bang", KmrG2POptions(narrow=True)) == "baːŋɡ"


def test_paradigm():
    idx = verbs.default_index()
    assert {f.lemma for f in idx.lookup("dibînim")} == {"dîtin"}
    assert idx.lookup("tê")[0].lemma == "hatin"
    assert idx.lookup("nizanim")[0].features["polarity"] == "neg"
    assert idx.lookup("radibim")[0].lemma == "rabûn"


def test_gender_from_lexicon():
    lex = SimpleLexicon()
    lex.add("mal", "NOUN", "f")
    lex.add("bav", "NOUN", "m")
    an = KmrAnalyzer(lex)
    assert an.best("malê").features["case"] == "obl"
    assert an.best("bavê").features["ezafe"] == "yes"


@pytest.mark.parametrize("sentence, alignment, ok", [
    ("Ez te dibînim.", "accusative", True),
    ("Min tu dîtî.", "ergative", True),
    ("Min ew dîtin.", "ergative", True),
    ("Min tu dîtim.", "ergative", False),
    ("Ez hatim.", "accusative", True),
])
def test_ergativity(sentence, alignment, ok):
    r = detect_alignment(sentence)
    assert r.alignment == alignment and r.agreement_ok is ok


def test_translit():
    assert to_arabic("roj") == "ڕۆژ"
    assert to_arabic("mirov") == "مرۆڤ"
    assert to_arabic("inca") == "ئنجا"


@pytest.mark.parametrize("stem, gender", [("jin", "f"), ("mal", "f"), ("bav", "m"), ("mirov", "m"), ("xanî", "m"), ("çiya", "m")])
def test_decline_round_trip(stem, gender):
    """Every generated case form is analysed back to its stem with the cell's features."""
    from zimankit.skills_kmr.morphology import decline

    lex = SimpleLexicon()
    lex.add(stem, "NOUN", gender)
    an = KmrAnalyzer(lex)
    expect = {"obl": ("case", "obl"), "ez": ("ezafe", "yes")}
    for cell, form in decline(stem, gender):
        if form is None or form == stem or cell.startswith("voc"):
            continue
        readings = [a for a in an.analyze(form) if a.lemma == stem]
        assert readings, (cell, form)
        kind = cell.split(".")[1]
        if kind in expect:
            k, v = expect[kind]
            assert any(a.features.get(k) == v for a in readings), (cell, form)


def test_decline_forms():
    from zimankit.skills_kmr.morphology import decline

    assert dict(decline("xanî", "m"))["def.ez.sg"] == "xaniyê"
    assert dict(decline("jin", "f"))["ind.ez.sg"] == "jineke"
    assert dict(decline("mirov", "m"))["ind.ez.sg"] == "mirovekî"


@pytest.mark.parametrize("inf, cell, form", [
    ("hatin", ("imperative", "neg", "2sg"), "neyê"),
    ("axaftin", ("present", None, "1sg"), "diaxivim"),
    ("axaftin", ("present", "neg", "1sg"), "naxivim"),
    ("anîn", ("past", None, "2sg"), "aniyî"),
    ("şûştin", ("imperative", "neg", "pl"), "neşon"),
])
def test_verb_regressions(inf, cell, form):
    v = next(v for v in verbs.load_core_verbs() if v.infinitive == inf)
    kind, pol, person = cell
    forms = [f.form for f in verbs.conjugate(v)
             if (f.features.get("tense") == kind or f.features.get("mood") == kind)
             and f.features.get("polarity") == pol and f.features.get("person", "").replace("2pl", "pl") == person
             and f.features.get("aspect") in (None, "perfective")]
    assert form in forms


def test_istan_derivation():
    lex = SimpleLexicon()
    lex.add("kurd", "NOUN", "m")
    assert KmrAnalyzer(lex).best("Kurdistan").segmentation == "kurd+istan"
