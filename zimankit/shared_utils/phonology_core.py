"""Language-neutral phonology helpers: sonority, syllabification, epenthesis.

Both Kurdish varieties share the same phonotactic skeleton:

* syllable = (C)(C) V (C)(C)
* word-initial complex onsets: C + glide (/kw/, /xw/, /pj/) or
  sibilant + stop (/st/, /ʃk/);  word-medial onsets: C or C + glide only;
* word-final codas must *fall* in sonority (/rd/, /nd/, /st/, /ʃk/);
  word-medial codas are limited to fricative+stop (/st/), nasal+stop (/nd/)
  and glide+C (/wt/, /jn/).

Central Kurdish spelling does not write the short high vowel (the *bizroke*,
"hidden vowel"), so the G2P has to re-insert it wherever a consonant cluster
would otherwise violate those rules.  ``break_clusters`` implements that
repair once, for any phoneme inventory.

A *segment* is a tuple ``(symbol, kind)`` where kind is ``"C"`` (consonant,
glides included), ``"V"`` (written vowel) or ``"E"`` (epenthetic vowel).
"""

from __future__ import annotations

from typing import Final, Iterable, Sequence

Segment = tuple[str, str]

STOPS: Final[frozenset[str]] = frozenset("p b t d k ɡ q ʔ tʃ dʒ pʰ tʰ kʰ tʃʰ".split())
FRICATIVES: Final[frozenset[str]] = frozenset("f v s z ʃ ʒ x xʷ ɣ ħ ʕ h".split())
NASALS: Final[frozenset[str]] = frozenset("m n ŋ".split())
LIQUIDS: Final[frozenset[str]] = frozenset("l ɫ ɾ r".split())
GLIDES: Final[frozenset[str]] = frozenset("w j".split())
SIBILANTS: Final[frozenset[str]] = frozenset("s ʃ z".split())


def sonority(symbol: str) -> int:
    """5 glide > 4 liquid > 3 nasal > 2 fricative > 1 stop/affricate."""
    if symbol in GLIDES:
        return 5
    if symbol in LIQUIDS:
        return 4
    if symbol in NASALS:
        return 3
    if symbol in FRICATIVES:
        return 2
    return 1


def legal_onset(cluster: Sequence[str], initial: bool) -> bool:
    """Is *cluster* a permitted onset (word-initially or word-medially)?"""
    n = len(cluster)
    if n <= 1:
        return True
    if n == 2:
        a, b = cluster
        if b in GLIDES and a not in GLIDES:
            return True
        return initial and a in SIBILANTS and b in STOPS
    if n == 3 and initial:
        a, b, c = cluster
        return a in SIBILANTS and b in STOPS and c in GLIDES
    return False


def legal_coda(cluster: Sequence[str], final: bool) -> bool:
    """Is *cluster* a permitted coda (word-finally or word-medially)?"""
    n = len(cluster)
    if n <= 1:
        return True
    if n == 2:
        a, b = cluster
        if a in GLIDES:
            return True
        if final:
            return sonority(a) > sonority(b) or (a in FRICATIVES and b in STOPS)
        return b in STOPS and (a in FRICATIVES or a in NASALS)
    if n == 3 and final:
        return cluster[0] in GLIDES and legal_coda(cluster[1:], True)
    return False


def _closed_syllables(run: list[str], e: str, final: bool) -> list[Segment]:
    """Turn a vowel-less run into C-e-C syllables, carving from the right.

    A single leftover consonant at the left edge becomes an open C-e syllable.
    """
    out: list[Segment] = []
    first = True
    while run:
        if len(run) == 1:
            out[:0] = [(run[0], "C"), (e, "E")]
            break
        if first and final and len(run) >= 3 and legal_coda(run[-2:], True):
            coda, run = run[-2:], run[:-2]
        else:
            coda, run = run[-1:], run[:-1]
        onset, run = run[-1], run[:-1]
        out[:0] = [(onset, "C"), (e, "E")] + [(c, "C") for c in coda]
        first = False
    return out


def _repair_run(run: list[str], left_vowel: bool, right_vowel: bool, e: str) -> list[Segment]:
    """Insert epenthetic vowels into one maximal consonant run."""
    if not run:
        return []
    plain = [(c, "C") for c in run]
    if left_vowel and right_vowel:  # V [coda][onset] V
        for k in (2, 1, 0):
            if k > len(run):
                continue
            onset, coda = run[len(run) - k :], run[: len(run) - k]
            if (k == 0 or legal_onset(onset, False)) and legal_coda(coda, False):
                return plain
        onset_k = 2 if len(run) >= 2 and legal_onset(run[-2:], False) else 1
        onset, rest = run[-onset_k:], run[:-onset_k]
        keep, excess = rest[:1], rest[1:]
        return (
            [(c, "C") for c in keep]
            + _closed_syllables(excess, e, False)
            + [(c, "C") for c in onset]
        )
    if left_vowel:  # V [coda] #
        if legal_coda(run, True):
            return plain
        if len(run) >= 3:
            # first consonant closes the vowel's syllable, the rest is a
            # vowel-less word (allowing a final falling cluster):  næm.kɯɾd
            return [(run[0], "C")] + _closed_syllables(list(run[1:]), e, True)
        rest, out = list(run), []
        while rest and not legal_coda(rest, True):
            c = rest.pop()
            o = rest.pop() if rest else None
            out[:0] = ([(o, "C")] if o else []) + [(e, "E"), (c, "C")]
        return [(c, "C") for c in rest] + out
    if right_vowel:  # # [onset] V
        if legal_onset(run, True):
            return plain
        onset_k = 2 if len(run) >= 2 and legal_onset(run[-2:], True) else 1
        onset, prefix = run[-onset_k:], run[:-onset_k]
        if legal_onset(prefix, True):
            head = [(c, "C") for c in prefix] + [(e, "E")]
        else:
            head = _closed_syllables(prefix[:-1], e, False) + [(prefix[-1], "C"), (e, "E")]
        return head + [(c, "C") for c in onset]
    # no vowel at all:  # C+ #
    if len(run) == 1:
        return plain
    return _closed_syllables(list(run), e, True)


def break_clusters(segments: Iterable[Segment], epenthetic: str = "ɯ") -> list[Segment]:
    """Re-insert unwritten short vowels so every cluster is phonotactically legal."""
    out: list[Segment] = []
    run: list[str] = []
    left_vowel = False
    for sym, kind in segments:
        if kind == "C":
            run.append(sym)
            continue
        out.extend(_repair_run(run, left_vowel, True, epenthetic))
        run = []
        out.append((sym, kind))
        left_vowel = True
    out.extend(_repair_run(run, left_vowel, False, epenthetic))
    return out


def syllabify(segments: Sequence[Segment]) -> list[list[Segment]]:
    """Split a repaired segment list into syllables (maximal legal onset)."""
    nuclei = [i for i, (_, k) in enumerate(segments) if k in ("V", "E")]
    if not nuclei:
        return [list(segments)]
    bounds = [0]
    for a, b in zip(nuclei, nuclei[1:]):
        between = [s for s, _ in segments[a + 1 : b]]
        split = a + 1
        for k in range(len(between), -1, -1):
            if legal_onset(between[len(between) - k :], False):
                split = b - k
                break
        bounds.append(split)
    bounds.append(len(segments))
    return [list(segments[x:y]) for x, y in zip(bounds, bounds[1:]) if y > x]
