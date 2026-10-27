from zimankit.shared_utils.lid import identify
from zimankit.shared_utils.normalizer import normalize_text
from zimankit.shared_utils.phonology_core import break_clusters
from zimankit.shared_utils.text_helpers import COMPILED, damerau_levenshtein, levenshtein, weighted_distance
from zimankit.shared_utils.tokenizer import tokenize


def test_lid():
    assert identify("ئەمڕۆ لە شاری سلێمانی کۆبوونەوەیەک بۆ ئەو پرسە ئەنجام درا و بڕیار درا").lang == "ckb"
    assert identify("Ez ji bajarê Amedê me û niha li Stenbolê dixwînim, ji ber ku zanîngeh li vir e").lang == "kmr"
    assert identify("Ma yew roje şima ra vat ke ziwanê ma zaf rind o, la kes goştarî nêkeno").lang == "zza"
    assert identify("The quick brown fox jumps over the lazy dog and the cat is on the mat").lang == "eng"


def test_tokenize():
    toks = [t.text for t in tokenize("HDP'yê got: «باشە»، 2015.")]
    assert toks == ["HDP'yê", "got", ":", "«", "باشە", "»", "،", "2015", "."]


def test_normalizer_bidi_and_spaces():
    assert normalize_text("a‏b  c") == "ab c"


def test_distances():
    assert levenshtein("kitten", "sitting") == 3
    assert damerau_levenshtein("ab", "ba") == 1
    assert weighted_distance("گول", "گوڵ") < 1


def test_regex_cookbook():
    assert COMPILED["ckb_word"].match("کتێبەکەم")
    assert COMPILED["kmr_word"].match("jinekê")
    assert COMPILED["ckb_definite_suffix"].search("پیاوەکە")
    assert COMPILED["kmr_turkish_letters"].search("Erdoğan")


def test_epenthesis():
    segs = break_clusters([("m", "C"), ("n", "C")])
    assert "".join(s for s, _ in segs) == "mɯn"
