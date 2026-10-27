"""zimankit - Kurdish (Central ckb / Northern kmr) NLP skills.

Quick API::

    from zimankit import analyze, normalize, to_ipa, identify
    analyze("کتێبەکەم")[0].segmentation   # 'کتێب+ەکە+م'
    to_ipa("jinekê")                        # 'ʒɪnɛkeː'
"""

from __future__ import annotations

__version__ = "0.1.0"

from .shared_utils.lid import identify
from .shared_utils.text_helpers import detect_script


def _lang(text: str, lang: str | None) -> str:
    return lang or ("ckb" if detect_script(text) == "arabic" else "kmr")


def normalize(text: str, lang: str | None = None) -> str:
    if _lang(text, lang) == "ckb":
        from .skills_ckb.orthography import normalize as f
    else:
        from .skills_kmr.orthography import normalize as f
    return f(text)


def to_ipa(word: str, lang: str | None = None) -> str:
    if _lang(word, lang) == "ckb":
        from .skills_ckb.phonology_ipa import to_ipa as f
    else:
        from .skills_kmr.phonology_ipa import to_ipa as f
    return f(word)


_ANALYZERS: dict = {}


def analyze(word: str, lang: str | None = None):
    lg = _lang(word, lang)
    if lg not in _ANALYZERS:
        if lg == "ckb":
            from .skills_ckb.morphology import CkbAnalyzer as A
        else:
            from .skills_kmr.morphology import KmrAnalyzer as A
        _ANALYZERS[lg] = A()
    return _ANALYZERS[lg].analyze(word)


__all__ = ["analyze", "normalize", "to_ipa", "identify", "detect_script", "__version__"]
