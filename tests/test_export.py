import csv
import json
import sqlite3

import pytest

from zimankit.config import Config
from zimankit.lexicon.export import KAGGLE_SUBTITLE, KAGGLE_TITLE, LEMMA_COLUMNS, kaggle_resources, WORD_COLUMNS, clean_definition, export


@pytest.mark.parametrize("gloss, head, expected", [
    ("Maneya vê madeyê hê nehatiye nivîsîn. Heke hûn maneya wê bizanin, kerem bikin binivîsin.", "x", ("", "", "")),
    ("Guhartoyeke wê . Forma nêr: ewî . 2018 , Navek , “Sernav”, li ser example.com : ...", "ewê", ("", "wê", "")),
    ("Binêre Evdile .", "Evdile", ("", "", "Evdile")),
    ("( reng ) zer", "zerd", ("(reng) zer", "", "")),
    ("zever, şiyan, ked Divê em kurd bi xîret bin daku welatê xwe rizgar bikin.", "xîret", ("zever, şiyan, ked", "", "")),
    ("( ziman ) zimanek e ku li giravê Nîwe yê Nû Zelendayê tê peyivîn", "nîwî",
     ("(ziman) zimanek e ku li giravê Nîwe yê Nû Zelendayê tê peyivîn", "", "")),
    ("bêhna xweş 2007 , Navek , li ser www.example.org", "bîn", ("bêhna xweş", "", "")),
    ("û من و تۆ دەچین بۆ ماڵەوە. Min u to deçîn bo malewe.", "و", ("û", "", "")),
    ("pêçî, tilî Hevmane: قامک ( qamk )", "پەنجە", ("pêçî, tilî Hevmane: قامک (qamk)", "", "")),
    ("kelpîç, tuxle (Tu dikarî tarîxa vê jêgirtinê binivîsî?), https ://example", "brîket", ("kelpîç, tuxle", "", "")),
])
def test_clean_definition(gloss, head, expected):
    assert clean_definition(gloss, set(), head) == expected


def test_clean_definition_deny_tokens():
    assert clean_definition("nûçe, agahî ji malperasite re", {"malperasite"}, "nûçe") == ("nûçe, agahî ji", "", "")


def _write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(header)
        wr.writerows(rows)


def test_export_end_to_end(tmp_path):
    out = tmp_path / "output" / "kmr"
    out.mkdir(parents=True)
    (tmp_path / "cache").mkdir()
    _write_csv(out / "clean_wordlist_kmr.csv",
               ["grapheme", "lemma", "pos", "ipa", "morph_meta", "translit", "frequency", "sources", "confidence"], [
                   ["jin", "jin", "NOUN", "ʒɪn", '{"gender":"f","seg":"jin"}', "ژن", 100, "lexicon,news", 0.9],
                   ["jinekê", "jin", "NOUN", "ʒɪnɛkeː",
                    '{"case":"obl","definite":"ind","ezafe":"yes","gender":"f","number":"sg","seg":"jin+ekê","title":"yes"}',
                    "ژنەکێ", 0, "lexicon-form", 0.45],
               ])
    _write_csv(out / "lemmas_kmr.csv",
               ["lemma", "pos", "ipa", "translit", "gender", "transitivity", "frequency", "forms", "sources"],
               [["jin", "NOUN", "ʒɪn", "ژن", "f", "", 100, 2, "lexicon,lexicon-form,news"]])
    (out / "build_report_kmr.json").write_text(json.dumps({"corpus_tokens": 1_000_000}))
    (tmp_path / "cache" / "lexicon_wiki.jsonl").write_text(json.dumps(
        {"lang": "kmr", "title": "jin", "headword": "jin", "pos": "NOUN", "ipa": ["/ʒɪn/"], "gender": "f",
         "gloss": "mirovê mê , pîrek"}, ensure_ascii=False) + "\n", encoding="utf-8")
    settings = {"run": {"cache_dir": "cache", "output_dir": "output"}}
    stats = export(Config(settings, [], set(), tmp_path), ["kmr"])
    assert stats["kmr"]["words"] == 2 and stats["kmr"]["with_definition"] == 1

    k = tmp_path / "output" / "kaggle"
    with open(k / "kurdish_words_kmr.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0]) == WORD_COLUMNS
    jin, jineke = rows
    assert jin["is_lemma"] == "true" and jin["ipa_reference"] == "ʒɪn" and jin["zipf"] == "5.0"
    assert jin["script_latin"] == "jin" and jin["script_arabic"] == "ژن"
    assert jin["definition_kmr"] == "mirovê mê, pîrek" and jin["quality_tier"] == "gold"
    assert jineke["case"] == "obl" and jineke["definiteness"] == "ind" and jineke["ezafe"] == "true"
    assert jineke["segmentation"] == "jin+ekê" and jineke["morpheme_count"] == "2"
    assert jineke["other_features"] == "title=yes" and jineke["attested"] == "false" and jineke["zipf"] == ""
    assert jineke["definition_kmr"] == "mirovê mê, pîrek" and jineke["syllable_count"] == "3"

    with open(k / "kurdish_lemmas_kmr.csv", encoding="utf-8") as fh:
        lemma = next(csv.DictReader(fh))
    assert list(lemma) == LEMMA_COLUMNS and lemma["forms_sample"] == "jin, jinekê"

    con = sqlite3.connect(k / "kurdish_lexicon.sqlite")
    assert con.execute("SELECT word, \"case\" FROM words WHERE lemma = 'jin' AND ezafe = 1").fetchall() == [("jinekê", "obl")]
    assert (k / "README.md").exists() and json.loads((k / "dataset-metadata.json").read_text())["licenses"]


def test_kaggle_metadata_limits():
    assert 6 <= len(KAGGLE_TITLE) <= 50 and 20 <= len(KAGGLE_SUBTITLE) <= 80


def test_kaggle_resources_describe_every_file_and_column():
    res = kaggle_resources({"ckb": {"words": 1, "lemmas": 1, "variants": 1}, "kmr": {"words": 1, "lemmas": 1, "variants": 0}})
    paths = {r["path"] for r in res}
    assert {"kurdish_words_kmr.parquet", "kurdish_spelling_variants_ckb.csv", "kurdish_lexicon.sqlite"} <= paths
    assert "kurdish_spelling_variants_kmr.csv" not in paths
    assert all(r["description"] for r in res)
    assert all(f["description"] for r in res for f in r.get("schema", {}).get("fields", []))
