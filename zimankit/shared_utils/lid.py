"""Rule-based language identification for Kurdish-adjacent text.

Why not just look at the script?  Because the corpora that look like Central
Kurdish also contain Hawrami (Gorani), Persian and Arabic, and the Latin-script
corpora contain Zazaki, Turkish and English.  Letting those into a wordlist
silently ruins it.

Method
------
Each candidate language has a *profile*: a set of high-frequency function
words (weighted 1.0 per hit) and diagnostic characters / character sequences
(weighted per occurrence).  A text is scored per language, scores are divided
by the number of word tokens, and the best language wins if it beats the
runner-up by ``margin``.  This is transparent, deterministic, needs no
training data and is accurate on paragraph-sized input (> 8 words).  For
single words use the script + orthography validators instead.

Language codes follow ISO 639-3 where one exists:
``ckb`` Central Kurdish, ``kmr`` Northern Kurdish, ``hac`` Gurani/Hawrami,
``sdh`` Southern Kurdish, ``zza`` Zazaki, ``fas`` Persian, ``arb`` Arabic,
``tur`` Turkish, ``eng`` English, ``und`` undetermined.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Final

import re

from .text_helpers import detect_script
from .tokenizer import words

ARABIC_SCRIPT_PROFILES: Final[dict[str, dict]] = {
    "ckb": {
        "words": set(
            "لە بۆ ئەم لەگەڵ دەکات کرد هەیە نییە بوو ئەوە لەسەر بەڵام دوای هەموو زۆر "
            "چونکە ئێمە ئەوان دەبێت دەکرێت لەناو هەروەها ئەمە کردووە ڕایگەیاند لەلایەن "
            "بەپێی کردنی بکات دەڵێت ئێستا ئەمڕۆ خۆی زمان کردبوو دەکەن لەوێ"
            .split()
        ),
        "chars": {"ە": 0.08, "ێ": 0.15, "ڵ": 0.2, "ڕ": 0.2, "ۆ": 0.1},
        "ngrams": {"ەکە": 0.6, "ەکان": 0.8, "دەکە": 0.6, "ەوە": 0.4},
    },
    "hac": {
        "words": set(
            "جە پەی ئینە ئانە مەکەرۆ مەکەرۆنە کەرد کەردەن کەردەی بیەن بیێنە بییەن ئیسە چێگە "
            "یاگێ مەبۆ ئادێ ئینا ئەرە دلێ ۋێش وێش ۋە ژە جەی چەنی فرە ئارۆ کریا کریان دمای "
            "گرد ئانەیە زوانی زیاتەر"
            .split()
        ),
        "strong": 2.0,
        "chars": {"ۋ": 2.0, "ۊ": 2.0},
        "ngrams": {"ۆنە": 0.6, "مێنە": 0.8, "ێنێ ": 0.4},
    },
    "fas": {
        "words": set(
            "از به را است این که با در می شده برای های ها یک آن شد هم بود ای "
            "خود نیز اما پس شود کنند کند دارد هستند"
            .split()
        ),
        "chars": {"آ": 0.5, "ي": 0.05, "ك": 0.05},
        "ngrams": {"ه ": 0.15, "ای ": 0.2, "می ": 0.3},
    },
    "arb": {
        "words": set(
            "في من على إلى أن التي الذي عن هذا كان قد ما لا هذه ذلك بين عام كل مع"
            .split()
        ),
        "chars": {"ة": 0.8, "أ": 0.5, "إ": 0.5, "ى": 0.4, "ث": 0.3, "ذ": 0.3, "ض": 0.3, "ظ": 0.4, "ط": 0.2, "ص": 0.2},
        "ngrams": {" ال": 0.6},
    },
}

LATIN_SCRIPT_PROFILES: Final[dict[str, dict]] = {
    "kmr": {
        "words": set(
            "di ji li ku ev ew jî ên ye hat kir dike wek bo re gelek piştî berî tê dê wê wî "
            "xwe hatiye kirin bû wan dibe em hûn jibo herwiha ligel navbera got dikin kirine "
            "hatin heye anî dibêje"
            .split()
        ),
        "chars": {"ê": 0.05, "î": 0.03, "û": 0.03, "ş": 0.02, "ç": 0.02},
        "ngrams": {"xw": 0.3, "ekê": 0.4, "ên ": 0.2, "dik": 0.2},
    },
    "zza": {
        "words": set(
            "ke yew zî xo ma do yo nê seba kerd ci hetê vat ame înan sey mi ca no ameyî xeylî "
            "amedî ganî wina zaf yeno yena tewrê kerdene la şarê qisey kenê dima bikerê bêro "
            "ziwan ziwanê derheqê kirmanckî kurdkî bîyo kerdo ameyo beno benê dano vato vano esto nîyo"
            .split()
        ),
        "strong": 2.0,
        "chars": {},
        "ngrams": {"ene ": 0.5, "eyî ": 0.6, "ey ": 0.2},
    },
    "tur": {
        "words": set(
            "ve bir bu için ile da de çok olarak olan gibi ama daha en kadar sonra "
            "değil var yok ise şu her ancak"
            .split()
        ),
        "chars": {"ı": 1.0, "ğ": 1.0, "ö": 0.6, "ü": 0.4, "İ": 1.0},
        "ngrams": {"lar": 0.3, "ler": 0.3, "yor": 0.6},
    },
    "eng": {
        "words": set(
            "the and of to in is for on that with as by it was are this from at be or an"
            .split()
        ),
        "chars": {},
        "ngrams": {"th": 0.2, "ing ": 0.4, "tion": 0.4},
    },
    "ckb": {  # Central Kurdish written in Latin script
        "words": set("le be bo legel bełam heye nîye dekat kird kirdin eke ekan deka ewe emane".split()),
        "chars": {"ł": 1.5, "ř": 1.5, "ĺ": 1.5, "ŕ": 1.5},
        "ngrams": {"ekan": 0.6, "ewe ": 0.3},
    },
}


# Pattern features: (regex, weight per match), counted per word token.
REGEX_FEATURES: Final[dict[str, list[tuple[re.Pattern[str], float]]]] = {
    # Gurani/Hawrami genitive -و after a consonant (خەڵکوو، داگیرکەرو), present مە-...ۆ(نە)
    "hac": [(re.compile(r"[^\sاەێۆوی]وو?(?=\s|$)"), 0.6), (re.compile(r"(?:^|\s)مە\S+[ۆێ]نە(?=\s|$)"), 1.0)],
    # Central Kurdish present-tense verbs دە...ێت/ات and the definite plural
    "ckb": [(re.compile(r"(?:^|\s)(?:دە|نا)\S+(?:ێت|ات)(?=\s|$)"), 0.8)],
    # Zazaki verbal nouns -ayîş/-îş and infinitives -ene
    "zza": [(re.compile(r"\w(?:ayîş|yîş|îşê?)(?=\W|$)"), 0.8), (re.compile(r"\w{2}ene(?=\W|$)"), 0.5)],
    # Kurmanji present prefix di- with person endings
    "kmr": [(re.compile(r"(?:^|\s)di\w+(?:im|in|e)(?=\W|$)"), 0.4)],
}


@dataclass
class LidResult:
    lang: str
    script: str
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)


def _score(text: str, tokens: list[str], profiles: dict[str, dict]) -> dict[str, float]:
    n = max(len(tokens), 1)
    padded = f" {text} "
    low_tokens = [t.lower() for t in tokens]
    counts = Counter(low_tokens)
    scores: dict[str, float] = {}
    for lang, prof in profiles.items():
        s = prof.get("strong", 1.0) * sum(c for w, c in counts.items() if w in prof["words"])
        for ch, wt in prof["chars"].items():
            s += padded.count(ch) * wt
        for ng, wt in prof["ngrams"].items():
            s += padded.count(ng) * wt
        for rx, wt in REGEX_FEATURES.get(lang, ()):
            s += len(rx.findall(text)) * wt
        scores[lang] = s / n
    return scores


def identify(text: str, margin: float = 0.15, min_words: int = 3) -> LidResult:
    """Identify the language of a paragraph-sized *text*."""
    script = detect_script(text)
    tokens = list(words(text))
    if script == "arabic":
        profiles = ARABIC_SCRIPT_PROFILES
    elif script == "latin":
        profiles = LATIN_SCRIPT_PROFILES
    else:
        return LidResult("und", script, 0.0)
    if len(tokens) < min_words:
        default = "ckb" if script == "arabic" else "kmr"
        return LidResult(default, script, 0.1)
    scores = _score(text.lower() if script == "latin" else text, tokens, profiles)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    (best, top), (_, second) = ranked[0], ranked[1]
    if top <= 0 or top - second < margin * max(top, 1e-9):
        return LidResult("und", script, 0.0, scores)
    confidence = min(1.0, (top - second) / top) if top else 0.0
    return LidResult(best, script, round(confidence, 3), scores)


def is_lang(text: str, lang: str, min_confidence: float = 0.2) -> bool:
    r = identify(text)
    return r.lang == lang and r.confidence >= min_confidence
