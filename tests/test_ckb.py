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


@pytest.mark.parametrize("stem", ["پیاو", "کتێب", "دەرگا", "ماسی", "خانە", "مامۆستا", "خانوو"])
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


@pytest.mark.parametrize("word", ["سنەییی", "ڕەشایییەکە", "ئەڵڵا"])
def test_normalize_keeps_valid_doubles(word):
    assert normalize_word(word) == word


def test_normalize_zwnj_and_conjunction():
    assert normalize_word("سپی‌یە") == "سپییە"
    assert normalize("من‌و تۆ") == "من و تۆ"


@pytest.mark.parametrize("word", ["ووشە", "چو", "وەکو", "ڵات", "سپی‌یە"])
def test_validate_reports_the_standard_but_builder_check_does_not(word):
    from zimankit.skills_ckb.orthography import structural_problems

    assert validate_word(word)
    assert not structural_problems(word)


@pytest.mark.parametrize("word", ["چوو", "ئاو", "لێو", "شیو", "تۆو", "نییە", "کۆتایی", "تو"])
def test_validate_accepts_standard_spellings(word):
    assert validate_word(word) == []


@pytest.mark.parametrize("word, latin", [
    ("منداڵ", "mindall"), ("کردووە", "kirdûwe"), ("ورمێیی", "wirmêyî"), ("ستران", "stran"), ("چ", "çi"),
    ("بردن", "birdin"), ("کردنەوە", "kirdinewe"),
])
def test_one_unwritten_vowel_per_cluster(word, latin):
    assert to_latin(word) == latin


@pytest.mark.parametrize("form, lemma", [
    ("چووەوە", "چوونەوە"), ("کردبووەوە", "کردنەوە"), ("کردووەتەوە", "کردنەوە"), ("خوێندووەتەوە", "خوێندنەوە"),
    ("چووینەتەوە", "چوونەوە"), ("دۆزییەوە", "دۆزینەوە"), ("هەڵبگرم", "هەڵگرتن"), ("هەڵگرم", "هەڵگرتن"),
    ("دابنیشە", "دانیشتن"), ("ڕامکرد", "ڕاکردن"), ("نووسیی", "نووسین"), ("پرسییان", "پرسین"), ("فڕییت", "فڕین"),
    ("دەخوێنرێت", "خوێندن"), ("دەکڕدرێت", "کڕین"), ("دەنێردرێت", "ناردن"),
])
def test_forms_printed_in_the_grammars(form, lemma):
    assert lemma in {f.lemma for f in verbs.default_index().lookup(form)}


@pytest.mark.parametrize("form", ["چوووە", "کردبوووە", "کردوووە"])
def test_three_waw_forms_are_gone(form):
    assert not verbs.default_index().lookup(form)


def test_ewe_perfect_needs_te():
    assert not [f for f in verbs.default_index().lookup("خوێندووەوە") if f.features.get("tense") == "present_perfect"]


def test_no_passive_for_rakirdin():
    assert not [f for f in verbs.default_index().lookup("ڕاکرا") if f.lemma == "ڕاکردن"]


def test_nouns_in_uu_take_consonant_endings():
    from zimankit.skills_ckb.morphology import decline

    cells = dict(decline("خانوو"))
    assert (cells["def.sg"], cells["def.pl"], cells["ind.sg"], cells["pl"], cells["ezafe"]) == ("خانووەکە", "خانووەکان", "خانووێک", "خانووان", "خانووی")


def test_guessed_vowel_stems_get_no_past_subjunctive():
    guessed = verbs.Verb("کون", "کو", "کە", False, "", "", "guess")
    assert "کوبا" not in {f.form for f in verbs.conjugate(guessed)}
    assert not [f for f in verbs.conjugate(verbs.Verb("یان", "یا", "", True, "", "", "guess")) if f.features.get("voice") == "passive"]


@pytest.mark.parametrize("form, lemma, features", [
    ("نەهاتووە", "هاتن", {"tense": "present_perfect", "polarity": "neg"}),
    ("نەهاتبوو", "هاتن", {"tense": "past_perfect", "polarity": "neg"}),
    ("نەکردووە", "کردن", {"tense": "present_perfect", "polarity": "neg"}),
    ("نەکردبوو", "کردن", {"tense": "past_perfect", "polarity": "neg"}),
    ("نەمکردبوو", "کردن", {"tense": "past_perfect", "polarity": "neg", "agent": "1sg"}),
    ("هاتوومە", "هاتن", {"tense": "present_perfect", "person": "1sg"}),
    ("هاتووم", "هاتن", {"tense": "present_perfect", "variant": "short"}),
    ("هێناویە", "هێنان", {"tense": "present_perfect", "variant": "short"}),
    ("خواردبا", "خواردن", {"tense": "past_subj", "agent": "external"}),
    ("خواردبام", "خواردن", {"tense": "past_subj", "agent": "1sg"}),
    ("خواردبێتم", "خواردن", {"tense": "perfect_subj", "agent": "1sg"}),
    ("خواردبووبا", "خواردن", {"tense": "pluperfect_subj"}),
    ("هاتبایت", "هاتن", {"tense": "past_subj", "person": "2sg"}),
    ("هاتبێتیت", "هاتن", {"tense": "perfect_subj", "person": "2sg"}),
    ("دەکرا", "کردن", {"voice": "passive", "aspect": "progressive"}),
    ("نەدەکرا", "کردن", {"voice": "passive", "aspect": "progressive", "polarity": "neg"}),
    ("نەکرا", "کردن", {"voice": "passive", "polarity": "neg"}),
    ("نەکراوە", "کردن", {"voice": "passive", "tense": "present_perfect", "polarity": "neg"}),
    ("کرابوو", "کردن", {"voice": "passive", "tense": "past_perfect"}),
    ("کراوم", "کردن", {"voice": "passive", "tense": "present_perfect", "person": "1sg"}),
    ("بکرێت", "کردن", {"voice": "passive", "mood": "subjunctive"}),
    ("نەکرێت", "کردن", {"voice": "passive", "mood": "subjunctive", "polarity": "neg"}),
    ("کرابا", "کردن", {"voice": "passive", "tense": "past_subj"}),
])
def test_tenses_printed_in_the_grammars(form, lemma, features):
    readings = [f.features for f in verbs.default_index().lookup(form) if f.lemma == lemma]
    assert any(features.items() <= r.items() for r in readings), readings


@pytest.mark.parametrize("word, segmentation", [
    ("کوردە", "کورد+ە"), ("مامۆستایە", "مامۆستا+یە"), ("سپییە", "سپی+یە"), ("ماڵدایە", "ماڵ+دا+یە"), ("ماڵدام", "ماڵ+دا+م"),
    ("چاکترە", "چاک+تر+ە"), ("سنەیی", "سنە+یی"), ("ڕەشایی", "ڕەش+ایی"), ("بێکار", "بێ+کار"), ("هاوکار", "هاو+کار"),
    ("گوڵەگەنم", "گوڵ+ە+گەنم"), ("دەموچاو", "دەم+و+چاو"), ("شارەوشار", "شار+ەو+شار"), ("کوڕێ", "کوڕ+ێ"), ("کوڕەک", "کوڕ+ەک"),
    ("چرایێک", "چرا+یێک"), ("کەسانێک", "کەس+ان+ێک"), ("کوڕگەل", "کوڕ+گەل"), ("تارانێ", "تاران+ێ"),
    ("کتێبەکانیشم", "کتێب+ەکان+یش+م"), ("ماڵەکە", "ماڵ+ەکە"),
])
def test_nominal_segmentation(word, segmentation):
    lex = SimpleLexicon()
    for w in "کورد مامۆستا سپی ماڵ چاک سنە کار گوڵ گەنم دەم چاو شار کوڕ چرا کەس تاران کتێب".split():
        lex.add(w, "NOUN")
    lex.add("ڕەش", "ADJ")
    assert CkbAnalyzer(lex).best(word).segmentation == segmentation


@pytest.mark.parametrize("word, not_segmentation", [
    ("بووە", "بوو+ە"), ("کۆتایی", "کۆت+ایی"), ("سەرەکی", "سەر+ەک+ی"), ("سەدام", "سە+دا+م"),
])
def test_short_affixes_do_not_overmatch(word, not_segmentation):
    lex = SimpleLexicon()
    for w in "بوو کۆت سەر سەرەک سە دا".split():
        lex.add(w, "NOUN")
    assert CkbAnalyzer(lex).best(word).segmentation != not_segmentation


def test_listed_word_keeps_its_final_e():
    lex = SimpleLexicon()
    lex.add("خان", "NOUN")
    lex.add("خانە", "NOUN")
    assert CkbAnalyzer(lex).best("خانە").segmentation == "خانە"


@pytest.mark.parametrize("word", ["پێ", "لێ", "تێ", "پێم", "لێی", "تێیان", "بۆمان"])
def test_bound_adpositions(word):
    assert CkbAnalyzer().best(word).pos == "ADP"


@pytest.mark.parametrize("form, agent", [
    ("هەڵمگرت", "1sg"), ("هەڵمنەگرت", "1sg"), ("هەڵمدەگرت", "1sg"), ("هەڵمگرتووە", "1sg"), ("هەڵمگرتبوو", "1sg"),
    ("هەڵمگرتبا", "1sg"), ("دامانخست", "1pl"), ("داماننەخست", "1pl"), ("دامانخستووە", "1pl"), ("بەکارمهێنا", "1sg"),
])
def test_clitic_on_the_first_part_in_every_tense(form, agent):
    readings = [f.features for f in verbs.default_index().lookup(form)]
    assert any(r.get("agent") == agent and "variant" not in r for r in readings), readings


@pytest.mark.parametrize("form", ["هەڵنەمگرت", "هەڵدەمگرت", "هەڵگرتوومە", "هەڵگرتم"])
def test_older_clitic_positions_stay_recognised(form):
    readings = verbs.default_index().lookup(form)
    assert readings and all(f.features.get("variant") == "clitic_late" for f in readings if f.features.get("agent"))


@pytest.mark.parametrize("tokens, span, lemma", [
    ("هەڵم گرت", 2, "هەڵگرتن"), ("ڕای گەیاند", 2, "ڕاگەیاندن"), ("هەڵم نەگرت", 2, "هەڵگرتن"), ("هەڵم گرتووە", 2, "هەڵگرتن"),
    ("بەکارم هێنا", 2, "بەکارهێنان"), ("پێک دێم", 2, "پێکهاتن"), ("لێی دا", 2, "لێدان"),
    ("دەست پێ دەکەم", 3, "دەستپێکردن"), ("دەستم پێ کرد", 3, "دەستپێکردن"),
])
def test_lookup_split(tokens, span, lemma):
    n, form = verbs.default_index().lookup_split(tokens.split())
    assert (n, form.lemma) == (span, lemma)


@pytest.mark.parametrize("tokens", ["نان خوارد", "ئەو دەگرم", "کتێب هات", "هەڵمان"])
def test_lookup_split_needs_the_first_part(tokens):
    assert verbs.default_index().lookup_split(tokens.split()) is None


def test_preverb_spacing_classes():
    idx = verbs.default_index().verbs
    assert not idx["هەڵگرتن"].always_split and idx["پێکهاتن"].always_split and idx["بەکارهێنان"].always_split


@pytest.mark.parametrize("word, lemma, features", [
    ("دەتبینم", "بینین", {"person": "1sg", "object": "2sg"}), ("دەیبینم", "بینین", {"person": "1sg", "object": "3sg"}),
    ("دەیبینێت", "بینین", {"person": "3sg", "object": "3sg"}), ("دەمبینیت", "بینین", {"person": "2sg", "object": "1sg"}),
    ("نایناسم", "ناسین", {"person": "1sg", "object": "3sg"}), ("هەڵیدەگرم", "هەڵگرتن", {"person": "1sg", "object": "3sg"}),
    ("بمگرە", "گرتن", {"object": "1sg"}), ("بیگرە", "گرتن", {"object": "3sg"}), ("بینیمیت", "بینین", {"agent": "1sg", "object": "2sg"}),
    ("بینیتم", "بینین", {"agent": "2sg", "object": "1sg"}), ("گرتمی", "گرتن", {"agent": "3sg", "object": "1sg"}),
    ("گرتمانی", "گرتن", {"agent": "3sg", "object": "1pl"}), ("بردینیان", "بردن", {"agent": "3pl", "object": "1pl"}),
])
def test_object_clitics(word, lemma, features):
    a = CkbAnalyzer().best(word)
    assert a.lemma == lemma and features.items() <= a.features.items()


@pytest.mark.parametrize("word", ["دەمبینم", "بتگرە", "بیرم", "مەمک"])
def test_no_object_reading(word):
    assert "object" not in CkbAnalyzer().best(word).features


def test_listed_verb_beats_a_clitic_on_a_noun_part():
    known = {v.infinitive: v for v in verbs.load_core_verbs() if not v.preverb and not v.suffix}
    make = lambda inf: verbs.make_verb(inf, True, None, "lexicon", known)
    index = verbs.FormIndex([make("دیاریکردن"), make("دیارکردن")])
    assert CkbAnalyzer(verbs=index).best("دیاریکرد").lemma == "دیاریکردن"
    index = verbs.FormIndex([make("ڕوودان")])
    assert CkbAnalyzer(verbs=index).best("ڕوویدا").lemma == "ڕوودان"


@pytest.mark.parametrize("form, lemma", [
    ("دەکا", "کردن"), ("دەڵێ", "گوتن"), ("دەخوا", "خواردن"), ("دەمەوێ", "ویستن"), ("دەکەی", "کردن"), ("دەبینرێ", "بینین"), ("دەژێت", "ژیان"),
    ("بچۆ", "چوون"), ("بڕۆ", "چوون"), ("مەچۆ", "چوون"), ("نایێم", "هاتن"), ("ویسترا", "ویستن"), ("گرترا", "گرتن"), ("بردرا", "بردن"),
    ("بکەرەوە", "کردنەوە"), ("هاتۆتەوە", "هاتنەوە"), ("ئەچم", "چوون"), ("ئەخوارد", "خواردن"), ("دادەنێم", "دانان"), ("دەخوازم", "خواستن"),
    ("نووسیووە", "نووسین"), ("بینیووە", "بینین"), ("نەبینیووە", "بینین"), ("گەڕاونەوە", "گەڕانەوە"), ("ماونەوە", "مانەوە"), ("کردووتەوە", "کردنەوە"),
])
def test_variants_and_regional_forms(form, lemma):
    assert CkbAnalyzer().best(form).lemma == lemma


@pytest.mark.parametrize("word, pos", [("بێ", "ADP"), ("نا", "PART"), ("نان", "NOUN"), ("برا", "NOUN"), ("با", "NOUN")])
def test_new_verb_forms_do_not_hide_common_words(word, pos):
    assert CkbAnalyzer().best(word).pos == pos


def test_guessing_present_stems():
    known = {v.infinitive: v for v in verbs.load_core_verbs() if not v.preverb and not v.suffix}
    assert verbs.guess_present_stem("دڕا", False) == "دڕێ" and verbs.guess_present_stem("شکا", True) == "شک"
    assert verbs.guess_present_stem("دروو") == "دروو"
    assert verbs.make_verb("پاڵاوتن", None, None, "guess", known).preverb == ""
    for word in ("ترازان", "لەرزان"):
        assert verbs.make_verb(word, None, None, "guess", known).preverb == ""


def test_guessed_verb_in_yan_does_not_take_forms_of_the_real_verb():
    known = {v.infinitive: v for v in verbs.load_core_verbs() if not v.preverb and not v.suffix}
    index = verbs.FormIndex([verbs.make_verb(w, None, None, "lexicon", known) for w in ("دزیان", "دزین")])
    assert [f.lemma for f in index.lookup("دەدزێت")] == ["دزین"]


def test_one_ye_before_ewe_is_a_variant():
    known = {v.infinitive: v for v in verbs.load_core_verbs() if not v.preverb and not v.suffix}
    index = verbs.FormIndex([verbs.make_verb("دۆزینەوە", True, "دۆز", "guess", known)])
    assert all("variant" not in f.features for f in index.lookup("دۆزییەوە"))
    assert all(f.features.get("variant") == "one_ye" for f in index.lookup("دۆزیەوە"))


@pytest.mark.parametrize("word, lemma, segmentation", [
    ("ماسێکە", "ماسی", "ماس+ێکە"), ("پەنجەران", "پەنجەرە", "پەنجەر+ان"), ("بەخێرایی", "خێرا", "بە+خێرا+یی"), ("ئاسنگەر", "ئاسن", "ئاسن+گەر"),
])
def test_recovered_lemmas_and_new_suffixes(word, lemma, segmentation):
    lex = SimpleLexicon()
    for w in ("ماسی", "پەنجەرە", "ئاسن"):
        lex.add(w, "NOUN")
    lex.add("خێرا", "ADJ")
    a = CkbAnalyzer(lex).best(word)
    assert (a.lemma, a.segmentation) == (lemma, segmentation)


def test_both_readings_of_yan_are_returned():
    lex = SimpleLexicon()
    lex.add("مامۆستا", "NOUN")
    glosses = {a.gloss for a in CkbAnalyzer(lex).analyze("مامۆستایان")}
    assert {"STEM+3PL", "STEM+PL"} <= glosses


@pytest.mark.parametrize("word, standard", [("وەکو", "وەکوو"), ("بەرامبەر", "بەرانبەر"), ("نیە", "نییە"), ("ڕۆژئاوا", "ڕۆژاوا")])
def test_validator_names_the_standard_spelling(word, standard):
    assert any(standard in p for p in validate_word(word))


@pytest.mark.parametrize("solid, lemma, written", [
    ("هەڵمگرت", "هەڵگرتن", "هەڵم گرت"), ("هەڵمنەگرت", "هەڵگرتن", "هەڵم نەگرت"), ("هەڵیگرتووە", "هەڵگرتن", "هەڵی گرتووە"),
    ("هەڵدەگرم", "هەڵگرتن", "هەڵدەگرم"), ("هەڵمەگرە", "هەڵگرتن", "هەڵمەگرە"), ("پێکدێم", "پێکهاتن", "پێک دێم"), ("لێمدا", "لێدان", "لێم دا"),
    ("بەکارمهێنا", "بەکارهێنان", "بەکارم هێنا"), ("بەکاردەهێنم", "بەکارهێنان", "بەکار دەهێنم"),
    ("دەستپێدەکەم", "دەستپێکردن", "دەست پێ دەکەم"), ("دەستپێمکرد", "دەستپێکردن", "دەستم پێ کرد"), ("دەکەم", "کردن", "دەکەم"),
])
def test_standard_spelling(solid, lemma, written):
    idx = verbs.default_index()
    forms = [f for f in idx.lookup(solid) if f.lemma == lemma and not f.features.get("variant") and f.features.get("agent") != "external"]
    assert verbs.standard_spelling(idx.verbs[lemma], forms[0]) == written


@pytest.mark.parametrize("written", ["هەڵم گرت", "هەڵم نەگرت", "پێک دێم", "بەکارم هێنا", "دەست پێ دەکەم", "دەستم پێ کرد", "لێم دا"])
def test_the_spelling_we_teach_can_be_read_back(written):
    assert verbs.default_index().lookup_split(written.split()) is not None


@pytest.mark.parametrize("word, latin", [("ماسیی", "masîy"), ("کوردیی", "kurdîy"), ("ماسی", "masî"), ("کۆتایی", "kotayî"), ("سنەیی", "sineyî")])
def test_ezafe_after_a_final_i_is_written_in_latin(word, latin):
    assert to_latin(word) == latin


def test_negative_participle():
    assert any(f.features.get("form") == "past_participle" for f in verbs.default_index().lookup("نەهاتوو"))


def test_brother_is_bira():
    assert to_latin("برا") == "bira" and to_latin("برایەک") == "birayek"
