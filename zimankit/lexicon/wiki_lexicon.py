"""Parse MediaWiki-rendered *dictionary* pages (as stored in a ZIM archive).

Page anatomy (Kurdish-language dictionary wiki)::

    <h2 id="Kurmancî"><span class="besazimani" id="ku">Kurmancî</span></h2>   language section
      <h3 id="Bilêvkirin">  ... <span class="IPA">/ˈʒɘn/</span>               pronunciation
      <h3 id="Navdêr">                                                       part of speech
        <table class="tewandin-tablo"> ... </table>                          declension table
        <span class="headword-line"><strong class="headword">jin</strong>
              <span class="gender"><abbr title="mê">m</abbr></span>          gender (mê = feminine)
        <ol><li> definition ... </li></ol>
      <h3 id="Formeke_navdêrê">  <i>Rewşa çemandî ya mê ...</i> <b><a>jin</a></b>   inflected form -> lemma

The parser returns plain dicts so results can be streamed to JSONL.
"""

from __future__ import annotations

import html as htmllib
import re
from typing import Iterator

from ..tools.zim_cleaner import strip_html

LANG_IDS = {"ku": "kmr", "kmr": "kmr", "ckb": "ckb"}

POS_HEADINGS: dict[str, str] = {
    "Navdêr": "NOUN", "Navder": "NOUN", "Serenav": "PROPN", "Rengdêr": "ADJ", "Lêker": "VERB",
    "Hoker": "ADV", "Cînav": "PRON", "Daçek": "ADP", "Pêşdaçek": "ADP", "Paşdaçek": "ADP",
    "Bazinedaçek": "ADP", "Girêdek": "CCONJ", "Baneşan": "INTJ", "Hejmar": "NUM",
    "Pirtik": "PART", "Artîkel": "DET", "Pêşgir": "AFFIX", "Paşgir": "AFFIX", "Navgir": "AFFIX",
    "Biwêj": "IDIOM", "Gotineke_pêşiyan": "PROVERB", "Kurtenav": "ABBR", "Tîp": "LETTER",
    "Rehekî_lêkerê": "VERB_STEM", "Reheke_lêkerê": "VERB_STEM",
    "Formeke_navdêrê": "NOUN_FORM", "Formeke_lêkerê": "VERB_FORM",
    "Formeke_rengdêrê": "ADJ_FORM", "Formeke_serenavê": "PROPN_FORM",
}
GENDER_TITLES = {"mê": "f", "nêr": "m", "nêtar": "n"}
GENDER_ABBR = {"m": "f", "n": "m", "nt": "n", "mn": "f|m"}  # abbr text when no title

# Words used in form-of definitions and declension tables -> features
FEATURE_WORDS: dict[str, tuple[str, str]] = {
    "çemandî": ("case", "obl"), "navkî": ("case", "dir"), "bangkirin": ("case", "voc"),
    "îzafe": ("ezafe", "yes"), "yekjimar": ("number", "sg"), "pirjimar": ("number", "pl"),
    "binavkirî": ("definite", "def"), "nebinavkirî": ("definite", "ind"),
    "mê": ("gender", "f"), "nêr": ("gender", "m"),
    "yekem": ("person", "1"), "duyem": ("person", "2"), "sêyem": ("person", "3"),
    "niha": ("tense", "present"), "borî": ("tense", "past"), "fermanî": ("mood", "imperative"),
    "daxwazî": ("mood", "subjunctive"), "neyînî": ("polarity", "neg"), "pêşeroj": ("tense", "future"),
}
ROW_FEATURES: dict[str, dict[str, str]] = {
    "Navkî": {"case": "dir"}, "Îzafe": {"ezafe": "yes"}, "Çemandî": {"case": "obl"},
    "Nîşandera çem.": {"case": "obl", "demonstrative": "yes"}, "Bangkirin": {"case": "voc"},
}

_H2_SPLIT = re.compile(r'<div class="mw-heading mw-heading2">|<h2\b')
_LANG_SPAN = re.compile(r'class="besazimani" id="([^"]+)"')
_H_SPLIT = re.compile(r'<h([34])\s+id="([^"]+)"[^>]*>')
_IPA = re.compile(r'<span class="IPA">([^<]+)</span>')
_HEADWORD = re.compile(r'<strong class="[^"]*headword[^"]*"[^>]*>(.*?)</strong>', re.S)
_TRANSLIT = re.compile(r'class="headword-tr[^"]*"[^>]*>(.*?)</span>', re.S)
_GENDER = re.compile(r'<span class="gender">(.*?)</span>', re.S)
_ABBR = re.compile(r'<abbr(?: title="([^"]*)")?[^>]*>(.*?)</abbr>', re.S)
_TRANS = re.compile(r"\b(negerguhêz|gerguhêz)\b")
_PRES_STEM = re.compile(r"Rehê dema niha(?:</i>)?\s*:\s*(?:</?[a-z][^>]*>\s*)*-?([^\s<>/-]+)-?")
_PAST_STEM = re.compile(r"Rehê dema borî(?:</i>)?\s*:\s*(?:</?[a-z][^>]*>\s*)*-?([^\s<>/-]+)-?")
_DEF_LI = re.compile(r"<ol>\s*<li>(.*?)</li>", re.S)
_FORM_OF = re.compile(r"<i>(.*?)</i>\s*(?:&nbsp;)?\s*<b>(?:<span[^>]*>)?<a[^>]*title=\"([^\"]+)\"", re.S)
_TABLE = re.compile(r'<table[^>]*(?:tewandin-tablo|inflection-table)[^>]*>(.*?)</table>', re.S)
_STUB_NOTE = re.compile(r"Nimûneyekê lê zêde bike\s*\[\s*biguhêre\s*\]")
_ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
_TAG_ONLY = re.compile(r"<[^>]+>")
_CELL = re.compile(r"<(th|td)([^>]*)>(.*?)</\1>", re.S)


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", strip_html(fragment, keep_blocks=False)).strip()


def _features_from_words(text: str) -> dict[str, str]:
    feats: dict[str, str] = {}
    low = text.lower()
    for word in re.findall(r"[a-zçêîşû]+", low):
        if word in FEATURE_WORDS:
            k, v = FEATURE_WORDS[word]
            feats.setdefault(k, v)
    if "dema niha" in low:
        feats["tense"] = "present"
    if "dema borî" in low or "boriya" in low:
        feats["tense"] = "past"
    return feats


def _declension(table_html: str, lemma: str) -> list[dict]:
    """Rows of a declension table -> [{form, features}]."""
    forms: list[dict] = []
    block: dict[str, str] = {}
    for row in _ROW.findall(table_html):
        cells = _CELL.findall(row)
        if not cells:
            continue
        if len(cells) == 1 and cells[0][0] == "th":
            label = _text(cells[0][2])
            if label.startswith("Zayend"):
                block = _features_from_words(label)
            continue
        head = _text(cells[0][2]) if cells[0][0] == "th" else ""
        if head not in ROW_FEATURES:
            continue
        values = [c for c in cells[1:] if c[0] == "td"]
        for number, cell in zip(("sg", "pl"), values):
            # inline tags (jin<b>a</b>) must not become spaces
            surface = re.sub(r"\s+", " ", htmllib.unescape(_TAG_ONLY.sub("", cell[2]))).strip()
            if not surface or surface == "-":
                continue
            surface = surface.split()[-1]  # drop demonstrative wê/wan
            forms.append({"form": surface, "lemma": lemma, "features": {**block, **ROW_FEATURES[head], "number": number}})
    return forms


def parse_page(page_html: str, title: str) -> Iterator[dict]:
    """Yield one record per (language, part-of-speech) section of *page_html*."""
    for section in _H2_SPLIT.split(page_html)[1:]:
        m = _LANG_SPAN.search(section[:600])
        if not m or m.group(1) not in LANG_IDS:
            continue
        lang = LANG_IDS[m.group(1)]
        ipa = [htmllib.unescape(x).strip() for x in _IPA.findall(section)]
        parts = _H_SPLIT.split(section)
        # parts = [pre, level, id, body, level, id, body, ...]
        rec: dict | None = None
        for k in range(1, len(parts) - 2, 3):
            heading = re.sub(r"_\d+$", "", parts[k + 1])
            body = parts[k + 2]
            pos = POS_HEADINGS.get(heading)
            if pos is None:
                # sub-sections (Tewandin = inflection, ...) enrich the current record
                if rec is not None and not rec["pos"].endswith("_FORM"):
                    _enrich(rec, body, lang)
                continue
            if rec is not None:
                yield rec
            rec = {"lang": lang, "title": title, "pos": pos, "ipa": ipa[:1]}
            hw = _HEADWORD.search(body)
            rec["headword"] = _text(hw.group(1)) if hw else title
            tr = _TRANSLIT.search(body)
            if tr:
                rec["translit"] = _text(tr.group(1))
            g = _GENDER.search(body)
            if g:
                genders = set()
                for gtitle, abbr in _ABBR.findall(g.group(1)):
                    gtitle = htmllib.unescape(gtitle or "").strip()
                    if gtitle in GENDER_TITLES:
                        genders.add(GENDER_TITLES[gtitle])
                    elif _text(abbr) in GENDER_ABBR:
                        genders.update(GENDER_ABBR[_text(abbr)].split("|"))
                if genders:
                    rec["gender"] = "|".join(sorted(genders))
            t = _TRANS.search(body[:6000])
            if t:
                rec["transitivity"] = "intransitive" if t.group(1) == "negerguhêz" else "transitive"
            if pos.endswith("_FORM"):
                fo = _FORM_OF.search(body)
                if fo:
                    rec["lemma"] = htmllib.unescape(fo.group(2)).replace("_", " ")
                    rec["features"] = _features_from_words(_text(fo.group(1)))
            else:
                d = _DEF_LI.search(body)
                if d:
                    rec["gloss"] = _STUB_NOTE.sub("", _text(d.group(1))).strip()[:200]
                _enrich(rec, body, lang)
        if rec is not None:
            yield rec


def _enrich(rec: dict, body: str, lang: str) -> None:
    """Stems and inflection tables found in *body* are attached to *rec*."""
    if "present_stem" not in rec:
        ps = _PRES_STEM.search(body)
        if ps:
            rec["present_stem"] = htmllib.unescape(ps.group(1))
    if "past_stem" not in rec:
        pa = _PAST_STEM.search(body)
        if pa:
            rec["past_stem"] = htmllib.unescape(pa.group(1))
    for table in _TABLE.findall(body):
        forms = _declension(table, rec["headword"])
        if forms:
            rec.setdefault("forms", []).extend(forms)
    if lang == "ckb" and rec["pos"] == "VERB" and "present_stem" not in rec:
        rec.update(_ckb_verb_table(body))


_CKB_PRESENT_1SG = re.compile(r"(?<!rehê )dema niha\s*</th>.*?<td[^>]*>\s*(?:<[^>]+>)*\s*([؀-ۿ]+)", re.S)


def _ckb_verb_table(body: str) -> dict:
    """Present stem of a Central Kurdish verb from its 1sg present cell (دەکەم -> کە)."""
    m = _CKB_PRESENT_1SG.search(body)
    if not m:
        return {}
    form = m.group(1)
    if form.startswith(("دە", "ئە")) and form.endswith("م") and len(form) > 3:
        return {"present_stem": form[2:-1]}
    return {}
