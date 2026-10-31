// "Learn more" links from a word or a tool to the tutorials and the documentation.
// Titles come from the pages themselves (js/lessons.js, written by build_site.py, which also fails on a missing page).
(function () {
  const BASE = "https://github.com/0xdolan/zimankit/blob/main/docs/";
  const LESSONS = {
    ckb: {
      alphabet: "tutorials/ckb/1-beginner/02-alphabet.md", vowels: "tutorials/ckb/1-beginner/03-vowels.md",
      consonants: "tutorials/ckb/1-beginner/04-consonants.md", writing: "tutorials/ckb/1-beginner/05-writing-and-reading.md",
      tobe: "tutorials/ckb/1-beginner/06-pronouns-and-to-be.md", nouns: "tutorials/ckb/1-beginner/07-nouns.md",
      demonstratives: "tutorials/ckb/1-beginner/08-this-that-and-questions.md", ezafe: "tutorials/ckb/1-beginner/09-ezafe-and-adjectives.md",
      present: "tutorials/ckb/1-beginner/10-present-tense.md", possessives: "tutorials/ckb/2-intermediate/11-possessives.md",
      subjunctive: "tutorials/ckb/2-intermediate/12-subjunctive-and-imperative.md", pastIntransitive: "tutorials/ckb/2-intermediate/13-past-intransitive.md",
      ergativity: "tutorials/ckb/2-intermediate/14-past-transitive-ergativity.md", progressive: "tutorials/ckb/2-intermediate/15-past-progressive.md",
      adpositions: "tutorials/ckb/2-intermediate/16-prepositions-and-postpositions.md", wordBuilding: "tutorials/ckb/2-intermediate/17-comparison-and-word-building.md",
      perfect: "tutorials/ckb/3-advanced/18-perfect-tenses.md", passive: "tutorials/ckb/3-advanced/19-passive.md",
      compounds: "tutorials/ckb/3-advanced/20-preverbs-and-compound-verbs.md", irregular: "tutorials/ckb/3-advanced/21-irregular-verbs.md",
      clitics: "tutorials/ckb/3-advanced/22-clitic-placement.md", spelling: "tutorials/ckb/3-advanced/23-spelling-and-common-errors.md",
      verbs: "tutorials/ckb/reference/verbs/README.md",
      orthographyDoc: "07-ckb-orthography.md", ipaDoc: "08-ckb-phonology-ipa.md", morphologyDoc: "09-ckb-morphology.md", verbsDoc: "10-ckb-verbs.md",
    },
    kmr: {
      alphabet: "tutorials/kmr/1-beginner/02-alphabet.md", vowels: "tutorials/kmr/1-beginner/03-vowels.md",
      consonants: "tutorials/kmr/1-beginner/04-consonants.md", writing: "tutorials/kmr/1-beginner/05-writing-and-reading.md",
      tobe: "tutorials/kmr/1-beginner/06-pronouns-and-to-be.md", nouns: "tutorials/kmr/1-beginner/07-nouns-gender-and-definiteness.md",
      ezafe: "tutorials/kmr/1-beginner/08-ezafe.md", cases: "tutorials/kmr/1-beginner/09-cases.md",
      present: "tutorials/kmr/1-beginner/10-present-tense.md", demonstratives: "tutorials/kmr/2-intermediate/11-demonstratives-and-questions.md",
      subjunctive: "tutorials/kmr/2-intermediate/12-subjunctive-imperative-future.md", pastIntransitive: "tutorials/kmr/2-intermediate/13-past-intransitive.md",
      ergativity: "tutorials/kmr/2-intermediate/14-past-transitive-ergativity.md", progressive: "tutorials/kmr/2-intermediate/15-past-progressive.md",
      adpositions: "tutorials/kmr/2-intermediate/16-prepositions.md", wordBuilding: "tutorials/kmr/2-intermediate/17-comparison-and-word-building.md",
      perfect: "tutorials/kmr/3-advanced/18-perfect-tenses.md", passive: "tutorials/kmr/3-advanced/19-passive.md",
      compounds: "tutorials/kmr/3-advanced/20-preverbs-and-compound-verbs.md", irregular: "tutorials/kmr/3-advanced/21-irregular-verbs.md",
      agreement: "tutorials/kmr/3-advanced/22-agreement-and-ergativity.md", spelling: "tutorials/kmr/3-advanced/23-spelling-and-common-errors.md",
      verbs: "tutorials/kmr/reference/verbs/README.md",
      orthographyDoc: "11-kmr-orthography.md", ipaDoc: "12-kmr-phonology-ipa.md", morphologyDoc: "13-kmr-morphology.md", verbsDoc: "14-kmr-verbs-ergativity.md",
    },
    any: {
      unicode: "04-unicode-normalization.md", lid: "05-language-identification.md", tokenization: "06-tokenization.md",
      translit: "15-transliteration.md", structure: "22-sentence-structure.md",
    },
  };
  const BY_TOOL = {
    analyze: { keys: ["nouns", "ezafe", "morphologyDoc"], any: [] },
    ipa: { keys: ["vowels", "consonants", "ipaDoc"], any: [] },
    translit: { keys: ["alphabet", "writing"], any: ["translit"] },
    conjugate: { keys: ["present", "ergativity", "irregular", "verbs", "verbsDoc"], any: [] },
    ergativity: { keys: ["ergativity", "agreement", "verbsDoc"], any: ["structure"] },
    lid: { keys: [], any: ["lid"] },
    normalize: { keys: ["alphabet", "spelling", "orthographyDoc"], any: ["unicode"] },
    validate: { keys: ["alphabet", "spelling", "orthographyDoc"], any: [] },
    tokenize: { keys: [], any: ["tokenization"] },
  };

  function page(path) {
    const title = (window.zkLessons && window.zkLessons[path]) || path;
    const kind = path.startsWith("tutorials/ckb") ? "Sorani tutorial" : path.startsWith("tutorials/kmr") ? "Kurmanji tutorial" : "Docs";
    return { title, url: BASE + path, kind };
  }
  const get = (lang, key) => LESSONS[lang] && LESSONS[lang][key];

  function pages(lang, keys, anyKeys) {
    const out = [...keys.map((k) => get(lang, k)).filter(Boolean), ...(anyKeys || []).map((k) => LESSONS.any[k])];
    return [...new Set(out)].map(page);
  }

  function forTool(tool, langs) {
    const t = BY_TOOL[tool];
    if (!t) return [];
    const list = (langs && langs.length ? langs : ["ckb", "kmr"]).filter((l) => LESSONS[l]);
    if (!t.keys.length) return pages("kmr", [], t.any);
    const seen = new Set();
    return list.flatMap((l) => pages(l, t.keys, t.any)).filter((p) => !seen.has(p.url) && seen.add(p.url));
  }

  function verbKeys(w) {
    const f = w.features || {};
    if (f.voice === "passive") return ["passive"];
    if (f.mood === "subjunctive" || f.mood === "imperative") return ["subjunctive"];
    if (f.aspect === "progressive") return ["progressive"];
    if (f.tense === "present_perfect" || f.tense === "past_perfect") return ["perfect", ...(f.alignment === "ergative" ? ["ergativity"] : [])];
    if (f.tense === "past") return f.alignment === "ergative" ? ["ergativity", "agreement", "clitics"] : ["pastIntransitive"];
    return ["present"];
  }

  // The lessons that explain this word's role and form in this sentence.
  function forWord(w, parsed) {
    const f = w.features || {};
    const ergative = parsed.alignment ? parsed.alignment.alignment === "ergative"
      : parsed.tokens.some((x) => x.head === 0 && (x.features || {}).alignment === "ergative");
    let keys = [];
    switch (w.deprel) {
      case "nsubj":
      case "obj":
        keys = ergative ? ["ergativity", "cases"] : ["cases", "present"];
        if (w.upos === "PRON") keys.push("tobe");
        break;
      case "root":
        keys = w.upos === "VERB" ? [...verbKeys(w), "verbsDoc"] : ["tobe"];
        break;
      case "obl":
      case "case":
        keys = ["adpositions", "cases"];
        break;
      case "amod":
      case "nmod":
        keys = ["ezafe"];
        break;
      case "nmod:poss":
        keys = ["ezafe", "possessives"];
        break;
      case "det":
        keys = ["demonstratives"];
        break;
      case "nummod":
        keys = ["nouns"];
        break;
      case "cop":
        keys = ["tobe"];
        break;
      case "aux":
        keys = ["verbsDoc"];
        break;
      default:
        break;
    }
    if (f.ezafe || (f.enclitic || "").includes("ezafe")) keys.push("ezafe");
    if (f.enclitic && !(f.enclitic || "").startsWith("3sg|")) keys.push("possessives");
    if (f.definite) keys.push("nouns");
    if (f.case) keys.push("cases");
    if (f.demonstrative) keys.push("demonstratives");
    if (w.upos !== "VERB" && w.upos !== "PUNCT") keys.push("morphologyDoc");
    return pages(parsed.lang, [...new Set(keys)], ["structure"]).slice(0, 5);
  }

  // A list of links, ready to append.
  function section(links, heading) {
    const box = document.createElement("div");
    box.className = "learn";
    if (!links.length) return box;
    const h = document.createElement("p");
    h.className = "learn-title";
    h.textContent = heading || "Learn more";
    box.append(h);
    const ul = document.createElement("ul");
    links.forEach((l) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = l.url;
      a.target = "_blank";
      a.rel = "noopener";
      const kind = document.createElement("span");
      kind.className = "tag";
      kind.textContent = l.kind;
      const title = document.createElement("span");
      title.textContent = l.title;
      a.append(kind, title);
      li.append(a);
      ul.append(li);
    });
    box.append(ul);
    return box;
  }

  window.zkLearn = { forTool, forWord, section, verbPage: (lang, slug) => {
    const path = `tutorials/${lang}/reference/verbs/${slug}.md`;
    return window.zkLessons && window.zkLessons[path] ? page(path) : null;
  } };
})();
