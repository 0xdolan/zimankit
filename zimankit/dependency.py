"""Sentence structure: a rule-based dependency analysis for Sorani and Kurmanji.

``parse(sentence)`` returns every token with its morphological analysis, its head
(the word it depends on) and its relation to that head, using Universal
Dependencies labels (``nsubj``, ``obj``, ``obl``, ``case``, ``amod`` …), and a
plain-language explanation of each relation.

The analysis is a set of rules over zimankit's morphology, not a trained parser.
It handles simple clauses well: the verb is the root; core arguments are found by
case (Kurmanji) or by order (Sorani); adpositions attach to the noun they mark;
ezafe joins a noun to the modifier that follows it. Complex sentences get an
approximate structure, and ``notes`` says where the rules were unsure.

    >>> [ (t.text, t.deprel, t.head) for t in parse("Min pirtûk xwend.").tokens ]
    [('Min', 'nsubj', 3), ('pirtûk', 'obj', 3), ('xwend', 'root', 0), ('.', 'punct', 3)]
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .shared_utils.schema import Analysis
from .shared_utils.text_helpers import detect_script
from .shared_utils.tokenizer import tokenize

NOMINAL = {"NOUN", "PROPN", "PRON", "ADJ", "NUM"}
DERIVATION = {"PLACE", "ABST", "ABST|ADJZ", "ADJZ", "POSSR", "AGENT", "DIM", "NISBA", "ADVZ"}

# relation: (English name, what it means) ; Kurdish names only where the term is standard
RELATIONS = {
    "root": ("main verb", "the head of the sentence: every other word depends on it, directly or through other words"),
    "nsubj": ("subject", "who or what does the action, or is described"),
    "obj": ("object", "what the action is done to"),
    "obl": ("oblique", "a place, time, instrument, goal or other circumstance of the action"),
    "case": ("adposition", "a preposition or postposition that marks the role of its noun"),
    "amod": ("adjective modifier", "an adjective that describes the noun before it, joined by ezafe"),
    "nmod": ("noun modifier", "a word joined to the noun before it by ezafe: an attribute or a possessor"),
    "nmod:poss": ("possessor", "the owner of the noun before it, joined by ezafe"),
    "det": ("determiner", "a demonstrative or similar word that points out the noun"),
    "nummod": ("number", "a number that counts the noun"),
    "advmod": ("adverb", "a word that modifies the action: how, when, where or how much"),
    "aux": ("auxiliary", "a helping verb"),
    "cc": ("conjunction", "a word that links two parts (and, or, but)"),
    "conj": ("conjunct", "a word linked by a conjunction to an earlier word of the same kind"),
    "mark": ("subordinator", "a word that introduces a subordinate clause"),
    "cop": ("copula", "the verb “to be” linking the subject to the predicate"),
    "punct": ("punctuation", "punctuation, attached to the root"),
    "dep": ("other", "a word whose relation the rules could not classify; attached to the verb"),
}
KURDISH_TERMS = {  # standard grammar terms: (Kurmanji, Sorani)
    "nsubj": ("kirde", "بکەر"), "obj": ("bireser", "بەرکار"), "case": ("daçek", ""),
    "NOUN": ("navdêr", "ناو"), "PROPN": ("navdêr", "ناو"), "ADJ": ("rengdêr", "ئاوەڵناو"), "PRON": ("cînav", "جێناو"),
    "ADV": ("hoker", "ئاوەڵکار"), "VERB": ("lêker", "کردار"), "NUM": ("hejmar", "ژمارە"),
}
POS_NAMES = {
    "NOUN": "noun", "PROPN": "proper noun", "PRON": "pronoun", "ADJ": "adjective", "VERB": "verb", "AUX": "auxiliary",
    "ADV": "adverb", "ADP": "adposition", "DET": "determiner", "NUM": "number", "CCONJ": "conjunction",
    "SCONJ": "subordinator", "PART": "particle", "INTJ": "interjection", "PUNCT": "punctuation", "X": "other",
}
FEATURE_NAMES = {
    "case": {"dir": "direct case", "obl": "oblique case"}, "number": {"sg": "singular", "pl": "plural"},
    "definite": {"def": "definite", "ind": "indefinite"}, "gender": {"m": "masculine", "f": "feminine"},
    "tense": {"past": "past", "present": "present", "present_perfect": "present perfect", "past_perfect": "past perfect"},
}


@dataclass
class Word:
    id: int  # 1-based position
    text: str
    lemma: str
    upos: str
    segmentation: str
    gloss: str
    features: dict[str, str]
    head: int = 0  # 0 = root
    deprel: str = "dep"
    relation: str = ""  # English name of deprel
    meaning: str = ""  # what the relation means
    pos_name: str = ""  # English name of upos
    position: str = ""  # where the word stands, relative to its head
    detail: str = ""  # what the word's form says
    explanation: str = ""  # relation, meaning, position and detail as one text
    kurdish: str = ""  # standard Kurdish grammar term for the role or word class, when there is one


@dataclass
class Parse:
    sentence: str
    lang: str
    tokens: list[Word]
    order: str = ""  # e.g. "subject object verb"
    alignment: dict | None = None  # Kurmanji: the split-ergativity record
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _analyzer(lang: str):
    if lang == "ckb":
        from .skills_ckb.morphology import CkbAnalyzer

        return CkbAnalyzer()
    from .skills_kmr.morphology import KmrAnalyzer

    return KmrAnalyzer()


_ANALYZERS: dict = {}


def _choose(cands: list[Analysis], nxt: list[Analysis] | None, after_prep: bool, lang: str) -> Analysis:
    """Pick the reading that fits the context: ezafe before a modifier, oblique after a preposition."""
    best = cands[0]
    nxt_pos = {a.pos for a in nxt} if nxt else set()
    if best.pos in ("VERB", "ADP", "PRON", "DET", "CCONJ", "SCONJ", "AUX", "ADV", "NUM", "PART"):
        return best
    def simplest(fits) -> Analysis | None:  # dibistan+ê, not dib+istan+ê; then the analyser's own ranking
        rank = lambda a: (sum(t in DERIVATION for _, t in a.segments), -a.score)
        return min((a for a in cands if fits(a)), key=rank, default=None)

    found = None
    if lang == "kmr":
        if after_prep:
            found = simplest(lambda a: a.features.get("case") == "obl")
        if not found and nxt_pos & NOMINAL:
            found = simplest(lambda a: a.features.get("ezafe"))
    elif nxt_pos & NOMINAL:
        found = simplest(lambda a: "ezafe" in a.features.get("enclitic", ""))
    return found or best


def _sorani_clitics(words: list[Word], an) -> None:
    """Sorani endings the word analyser leaves whole: the goal -ە on verbs, ئەم/ئەو … -ە, the copula -ە."""
    for i, w in enumerate(words):
        if w.upos not in ("VERB", "PUNCT") and w.text.endswith("ە") and len(w.text) > 3:
            stem = an.analyze(w.text[:-1])
            if stem and stem[0].pos == "VERB" and "person" in stem[0].features:
                a = stem[0]
                w.lemma, w.upos, w.features = a.lemma, "VERB", {**a.features, "goal": "yes"}
                w.segmentation, w.gloss = f"{w.text[:-1]}+ە", f"{a.gloss}+GOAL"
        nxt = words[i + 1] if i + 1 < len(words) else None
        if w.text in ("ئەم", "ئەو") and nxt and nxt.upos == "NOUN" and nxt.text.endswith("ە") and len(nxt.text) > 2:
            w.upos = "DET"
            nxt.lemma, nxt.segmentation, nxt.gloss = nxt.text[:-1], f"{nxt.text[:-1]}+ە", "STEM+DEM"
            nxt.features = {**nxt.features, "demonstrative": "yes"}
    if any(w.upos == "VERB" for w in words):
        return
    last = next((w for w in reversed(words) if w.upos != "PUNCT"), None)
    if last and last.upos in ("NOUN", "ADJ", "PRON") and "demonstrative" not in last.features:
        for end in ("یە", "ە"):
            if last.text.endswith(end) and len(last.text) > len(end) + 1:
                stem = last.text[: -len(end)]
                last.lemma, last.segmentation, last.gloss = stem, f"{stem}+{end}", "STEM+COP.3SG"
                last.features = {"copula": "3sg"}
                break


def _explain_position(w: Word, words: list[Word], lang: str) -> str:
    if w.head == 0:
        return f"Word {w.id} of {len(words)}, the root."
    head = words[w.head - 1]
    gap = abs(w.id - w.head)
    side = "before" if w.id < w.head else "after"
    reading = " (reading right to left)" if lang == "ckb" else ""
    return f"Word {w.id} of {len(words)}{reading}; it comes {side} its head “\u2068{head.text}\u2069”, {gap} word{'s' * (gap != 1)} away."


def parse(sentence: str, lang: str | None = None) -> Parse:
    lang = lang or ("ckb" if detect_script(sentence) == "arabic" else "kmr")
    an = _ANALYZERS.setdefault(lang, _analyzer(lang))
    toks = tokenize(sentence)
    cands = [an.analyze(t.text) if t.kind != "punct" else [] for t in toks]
    words: list[Word] = []
    for i, t in enumerate(toks):
        if t.kind == "punct" or not cands[i]:
            words.append(Word(i + 1, t.text, t.text, "PUNCT" if t.kind == "punct" else "X", t.text, "", {}))
            continue
        prev = words[-1] if words else None
        after_prep = bool(prev and prev.upos == "ADP" and prev.features.get("adptype") == "prep")
        nxt = cands[i + 1] if i + 1 < len(toks) else None
        a = _choose(cands[i], nxt, after_prep, lang)
        if t.kind == "number":
            a = Analysis(t.text, t.text, "NUM")
        words.append(Word(i + 1, t.text, a.lemma, a.pos, a.segmentation, a.gloss, dict(a.features)))
    if lang == "ckb":
        _sorani_clitics(words, an)
    p = Parse(sentence, lang, words)
    if not words:
        return p
    _attach(p)
    for w in words:
        w.relation, w.meaning = RELATIONS[w.deprel]
        if w.deprel == "root" and w.upos != "VERB":
            w.relation, w.meaning = "predicate", "the main statement of the sentence: the other words depend on it"
        terms = KURDISH_TERMS.get(w.deprel) or (KURDISH_TERMS.get(w.upos) if w.deprel in ("root", "dep") else None)
        w.kurdish = terms[0 if lang == "kmr" else 1] if terms else ""
        w.pos_name = POS_NAMES.get(w.upos, w.upos.lower())
        w.position = _explain_position(w, words, lang)
        w.detail = _detail(w, p)
        w.explanation = f"{w.relation.capitalize()}: {w.meaning}. {w.position} {w.detail}"
    return p


def _detail(w: Word, p: Parse) -> str:
    feats = [FEATURE_NAMES[k][v] for k, v in w.features.items() if k in FEATURE_NAMES and v in FEATURE_NAMES[k]]
    out = f"It is {'an' if w.pos_name[0] in 'aeiou' else 'a'} {w.pos_name}"
    out += f" ({', '.join(feats)})." if feats else "."
    if w.segmentation != w.text and "+" in w.segmentation:
        out += f" Its parts: {w.segmentation} = {w.gloss}."
    if w.features.get("goal"):
        out += " The ending -ە on the verb marks the goal of the motion (\u2068دەچمە ماڵەوە\u2069: I go home)."
    if w.features.get("demonstrative"):
        out += " With \u2068ئەم\u2069 / \u2068ئەو\u2069 before it, the ending -ە completes the demonstrative: “this / that …”."
    if w.features.get("copula") and w.upos != "AUX":
        out += " The ending is the copula “is”: the word is the predicate of the sentence."
    if p.alignment and p.alignment.get("alignment") == "ergative":
        if w.deprel == "nsubj":
            out += " In this past transitive (ergative) clause the subject, the agent, is in the oblique case."
        elif w.deprel == "obj":
            out += " In this ergative clause the object is in the direct case, and the verb agrees with it."
    if w.features.get("ezafe") or "ezafe" in w.features.get("enclitic", ""):
        out += " It ends in the ezafe, which joins it to the modifier after it."
    if w.deprel == "root" and w.upos == "VERB" and p.alignment:
        al = p.alignment
        if al.get("alignment") == "ergative":
            out += (" The verb is past and transitive, so the clause is ergative: the agent takes the oblique case,"
                    " and the verb agrees with the object.")
        elif al.get("alignment") == "accusative":
            out += " The clause is accusative: the subject is in the direct case and the verb agrees with it."
        if al.get("agreement_ok") is False:
            out += " Agreement problem: " + "; ".join(al.get("notes", [])) + "."
    if w.deprel == "root" and w.upos == "VERB" and p.lang == "ckb" and w.features.get("alignment") == "ergative":
        agent = w.features.get("agent")
        out += " The verb is past and transitive: in Sorani the agent is marked by a person clitic"
        out += f" ({agent})." if agent and agent != "external" else ", which may sit on an earlier word."
    return out


def _case(w: Word) -> str:
    """Kurmanji case of a nominal: oblique, or direct (unmarked)."""
    return "obl" if w.features.get("case") == "obl" else "dir"


def _attach(p: Parse) -> None:
    ws, lang = p.tokens, p.lang
    n = len(ws)
    verbs = [w for w in ws if w.upos == "VERB"]
    finite = [w for w in verbs if "person" in w.features or "agent" in w.features or "tense" in w.features] or verbs
    cop = next((w for w in ws if w.upos == "AUX" and w.features.get("copula")), None) if not verbs else None
    pred = next((w for w in reversed(ws[: cop.id - 1]) if w.upos != "PUNCT"), None) if cop else None
    # "V1 û V2": coordinated verbs; the first is the root and the later ones are its conjuncts
    coordinated = len(finite) > 1 and any(
        w.upos == "CCONJ" and finite[0].id < w.id < finite[-1].id for w in ws)
    if pred is not None:
        root = pred
    elif finite:
        root = finite[0] if coordinated else finite[-1]
    else:
        root = ([w for w in ws if w.upos != "PUNCT"] or ws)[-1]
    root.head, root.deprel = 0, "root"
    attached = {root.id}

    def link(w: Word, head: Word, rel: str) -> None:
        w.head, w.deprel = head.id, rel
        attached.add(w.id)

    if cop is not None and pred is not None:
        link(cop, root, "cop")
    elif root.upos != "VERB" and not root.features.get("copula"):
        p.notes.append("No verb was recognised; the last word is taken as the predicate (often a noun or adjective"
                       " with a copula such as -e / -ە).")
    for v in finite:
        if v is root:
            continue
        cc = next((w for w in reversed(ws[: v.id - 1]) if w.upos == "CCONJ" and w.id > root.id), None)
        if coordinated and cc is not None:
            link(v, root, "conj")
            link(cc, v, "cc")

    def next_nominal(i: int) -> Word | None:
        for w in ws[i:]:
            if w.upos in NOMINAL:
                return w
            if w.upos not in ("DET", "ADP"):  # ji bo te: both adpositions mark "te"
                return None
        return None

    def clause_head(w: Word) -> Word:
        """The verb of the clause a word belongs to: the nearest verb after it, else the root."""
        return next((v for v in finite if v.id > w.id and v.deprel in ("root", "conj")), root)

    for i, w in enumerate(ws):
        if w.id in attached:
            continue
        if w.upos == "PUNCT":
            link(w, root, "punct")
        elif w.upos == "ADP" and w.features.get("adptype") == "prep":
            noun = next_nominal(i + 1)
            if noun is not None and noun is not root:
                link(w, noun, "case")
                if noun.id not in attached:
                    link(noun, clause_head(noun), "obl")
        elif w.upos == "ADP":  # postposition: closes the preceding noun phrase
            prev = next((x for x in reversed(ws[:i]) if x.upos in NOMINAL), None)
            if prev is not None:
                link(w, prev, "case")
                if prev.id not in attached:
                    link(prev, clause_head(prev), "obl")
        elif w.upos in ("DET", "NUM"):
            noun = next_nominal(i + 1)
            if noun is not None:
                link(w, noun, "det" if w.upos == "DET" else "nummod")
    # ezafe: the word after an ezafe-marked noun modifies it (chains: nan-ê germ-ê xweş)
    for i, w in enumerate(ws[:-1]):
        ez = w.features.get("ezafe") or "ezafe" in w.features.get("enclitic", "")
        nxt = ws[i + 1]
        if ez and nxt.upos in NOMINAL and nxt is not root and nxt.id not in attached:
            rel = "amod" if nxt.upos == "ADJ" else "nmod:poss" if nxt.upos == "PRON" else "nmod"
            link(nxt, w, rel)

    # core arguments, clause by clause
    if lang == "kmr" and root.upos == "VERB":
        from .skills_kmr.syntax import detect_alignment

        p.alignment = detect_alignment(p.sentence).to_dict()
    for v in ([x for x in finite if x.deprel in ("root", "conj")] if root.upos == "VERB" else [root]):
        args = [w for w in ws if w.id not in attached and w.upos in NOMINAL and w.id < v.id and clause_head(w) is v]
        transitive = v.features.get("transitivity") == "transitive"
        ergative = lang == "kmr" and transitive and v.features.get("alignment") == "ergative"
        subj = obj = None
        if v.upos != "VERB":
            subj = args[0] if args else None
        elif ergative:  # past transitive: oblique agent, direct object
            subj = next((w for w in args if _case(w) == "obl"), None)
            obj = next((w for w in args if _case(w) == "dir" and w is not subj), None)
        elif lang == "kmr":
            subj = next((w for w in args if _case(w) == "dir"), None) or (args[0] if args else None)
            obj = next((w for w in args if w is not subj), None) if transitive else None
        else:
            subj = args[0] if args else None
            obj = args[1] if transitive and len(args) > 1 else None
        for w in args:
            link(w, v, "nsubj" if w is subj else "obj" if w is obj else "obl")
    for w in ws:
        if w.id in attached:
            continue
        head = clause_head(w)
        if w.upos == "PUNCT":
            link(w, root, "punct")
        elif w.upos in NOMINAL:
            link(w, head, "obl")  # after the verb: typically a goal (Ez diçim malê)
        elif w.upos in ("ADV", "PART"):
            link(w, head, "advmod")
        elif w.upos == "AUX":
            link(w, head, "aux")
        elif w.upos == "CCONJ":
            link(w, head, "cc")
        elif w.upos == "SCONJ":
            link(w, head, "mark")
        else:
            link(w, head, "dep")
    # conjoined nominals: "A û B" -> B is a conjunct of A, û marks B
    for i, w in enumerate(ws):
        if w.upos == "CCONJ" and 0 < i < n - 1 and w.head == root.id:
            left, right = ws[i - 1], ws[i + 1]
            if right is not root and right.deprel != "conj" and right.upos == left.upos and right.upos in NOMINAL:
                w.head, w.deprel = right.id, "cc"
                right.head, right.deprel = left.id, "conj"
    _coordinated_controller(p)
    if any(w.upos == "VERB" and w.deprel == "dep" for w in ws):
        p.notes.append("The sentence has more than one verb; some clauses are attached to the main verb without"
                       " being classified.")
    roles = sorted((w.id, w.deprel) for w in ws if w.deprel in ("nsubj", "obj") and w.head == root.id)
    if root.upos == "VERB":
        names = {"nsubj": "subject", "obj": "object"}
        p.order = " ".join([names[r] for i, r in roles if i < root.id] + ["verb"] + [names[r] for i, r in roles if i > root.id])
    p.notes.append("Rule-based analysis built on zimankit's morphology: reliable for simple clauses, approximate for"
                   " complex ones.")


def _coordinated_controller(p: Parse) -> None:
    """"Ez û tu diçin": a plural verb is right for coordinated arguments, so it is not an agreement error."""
    al = p.alignment
    if not al or al.get("agreement_ok") is not False:
        return
    arg = al.get("agent") if al.get("controller") == "subject" else al.get("object")
    word = next((w for w in p.tokens if arg and w.text == arg["token"]), None)
    if word and any(w.deprel == "conj" and w.head == word.id for w in p.tokens):
        al["agreement_ok"] = None
        al["notes"] = [f"the {al['controller']} is coordinated, so its person is not checked"]
