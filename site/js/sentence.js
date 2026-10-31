// Playground, Sentence tab: draw zimankit.parse() as a dependency diagram and explain whatever is clicked.
(function () {
  const EXAMPLES = [
    ["Min pirtûka nû li dibistanê xwend.", "I read the new book at school."],
    ["Jina min nan dixwe.", "My wife eats bread."],
    ["Ez û tu diçin bajêr.", "You and I go to the city."],
    ["Min tu dîtî.", "I saw you. The verb agrees with the object."],
    ["Min tu dîtim.", "A mistake on purpose: the verb should agree with the object “tu”."],
    ["کوڕەکە کتێبێکی نوێی لە قوتابخانە خوێندەوە.", "The boy read a new book at school."],
    ["من دەچمە ماڵەوە.", "I go home."],
    ["ئەو پیاوە باشە.", "That man is good."],
    ["من و تۆ دەچینە بازاڕ.", "You and I go to the market."],
  ];
  const GROUP = {
    root: "root", nsubj: "nsubj", obj: "obj", obl: "obl", case: "case", amod: "mod", nmod: "mod", "nmod:poss": "mod",
    det: "det", nummod: "det", conj: "conj", cc: "conj", advmod: "adv", aux: "fn", cop: "fn", mark: "fn", punct: "fn", dep: "fn",
  };
  const SVG = "http://www.w3.org/2000/svg";
  const $ = (id) => document.getElementById(id);
  let py = null;
  let parsed = null;
  let selected = null; // a word id
  let filter = null; // a relation name
  let timer = null;

  function el(name, attrs, parent, text) {
    const e = document.createElementNS(SVG, name);
    Object.entries(attrs || {}).forEach(([k, v]) => e.setAttribute(k, v));
    if (text !== undefined) e.textContent = text;
    if (parent) parent.append(e);
    return e;
  }
  function html(tag, cls, parent, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) { e.textContent = text; e.dir = "auto"; }
    if (parent) parent.append(e);
    return e;
  }
  const ctx = document.createElement("canvas").getContext("2d");
  function width(text, font) { ctx.font = font; return ctx.measureText(text).width; }
  const groupOf = (w) => "g-" + (GROUP[w.deprel] || "fn");
  const label = (w) => w.relation + (w.kurdish ? " · " + w.kurdish : "");
  const byId = (id) => parsed.tokens[id - 1];
  const dependents = (w) => parsed.tokens.filter((d) => d.head === w.id);

  function draw() {
    const box = $("s-diagram");
    box.replaceChildren();
    const toks = parsed.tokens;
    if (!toks.length) return;
    const rtl = parsed.lang === "ckb";
    const arcs = toks.filter((w) => w.head > 0 && w.upos !== "PUNCT");

    // columns: wide enough for the word, its class and form, and for the label of a one-step arrow
    const cols = toks.map((w) => Math.max(
      width(w.text, "600 20px 'IBM Plex Sans Arabic'"), width(w.pos_name, "500 11.5px 'IBM Plex Sans'"),
      w.segmentation !== w.text ? width(w.segmentation, "12px 'IBM Plex Sans Arabic'") : 0, 34) + 26);
    const centre = [];
    let x = 10;
    cols.forEach((c, i) => { centre.push(x + c / 2); x += c; });
    arcs.filter((a) => Math.abs(a.id - a.head) === 1).forEach((a) => {
      const i = Math.min(a.id, a.head) - 1;
      const need = width(label(a), "600 12.5px 'IBM Plex Sans'") + 22 - (centre[i + 1] - centre[i]);
      if (need > 0) for (let k = i + 1; k < centre.length; k++) centre[k] += need;
      if (need > 0) x += need;
    });
    const total = x + 10;
    const px = (id) => (rtl ? total - centre[id - 1] : centre[id - 1]);

    // levels: an arrow goes above every arrow it overlaps
    const span = (a) => [Math.min(a.id, a.head), Math.max(a.id, a.head)];
    const level = {};
    [...arcs].sort((a, b) => Math.abs(a.id - a.head) - Math.abs(b.id - b.head)).forEach((a) => {
      const [lo, hi] = span(a);
      let l = 1;
      arcs.forEach((b) => {
        if (level[b.id] === undefined || b === a) return;
        const [c, d] = span(b);
        if (c < hi && lo < d) l = Math.max(l, level[b.id] + 1);
      });
      level[a.id] = l;
    });
    const maxLevel = Math.max(0, ...Object.values(level));
    const rise = (l) => 24 + l * 36;
    const y0 = rise(maxLevel) + 44;

    // ports: arrows meeting at a word fan out, the longest nearest the middle
    const port = {};
    toks.forEach((w) => {
      const here = arcs.filter((a) => a.id === w.id || a.head === w.id);
      [-1, 1].forEach((side) => {
        const other = (a) => (a.id === w.id ? px(a.head) : px(a.id));
        here.filter((a) => Math.sign(other(a) - px(w.id)) === side)
          .sort((a, b) => Math.abs(other(a) - px(w.id)) - Math.abs(other(b) - px(w.id))).reverse()
          .forEach((a, i) => { port[a.id + (a.id === w.id ? "d" : "h")] = side * Math.min(4 + i * 7, 22); });
      });
    });

    const svg = el("svg", { width: total, height: y0 + 92, viewBox: `0 0 ${total} ${y0 + 92}`, role: "group" }, box);
    arcs.forEach((a) => {
      const xd = px(a.id) + port[a.id + "d"];
      const xh = px(a.head) + port[a.id + "h"];
      const h = rise(level[a.id]);
      const y = y0 - 2;
      const d = `M${xh} ${y} C${xh} ${y - h * 1.33},${xd} ${y - h * 1.33},${xd} ${y - 7}`;
      const g = el("g", { class: `edge ${groupOf(a)}`, "data-dep": a.id, "data-head": a.head, "data-rel": a.relation }, svg);
      el("path", { class: "arc", d }, g);
      el("path", { class: "tip", d: `M${xd - 5} ${y - 8} L${xd + 5} ${y - 8} L${xd} ${y} Z` }, g);
      el("path", { class: "hit", d }, g);
      const lab = el("g", { class: "lab" }, g);
      const t = label(a);
      const lw = width(t, "600 12.5px 'IBM Plex Sans'") + 10;
      const mid = (xd + xh) / 2;
      el("rect", { x: mid - lw / 2, y: y - h - 9, width: lw, height: 18, rx: 4 }, lab);
      el("text", { x: mid, y: y - h + 4 }, lab, t);
      g.addEventListener("click", (e) => { e.stopPropagation(); choose(a.id); });
    });

    const root = toks.find((w) => w.head === 0);
    if (root) {
      const g = el("g", { class: `edge ${groupOf(root)}`, "data-dep": root.id, "data-head": root.id, "data-rel": root.relation }, svg);
      el("path", { class: "arc", d: `M${px(root.id)} 26 V${y0 - 9}` }, g);
      el("path", { class: "tip", d: `M${px(root.id) - 5} ${y0 - 10} L${px(root.id) + 5} ${y0 - 10} L${px(root.id)} ${y0 - 2} Z` }, g);
      el("path", { class: "hit", d: `M${px(root.id)} 26 V${y0 - 9}` }, g);
      const lab = el("g", { class: "lab" }, g);
      const lw = width(label(root), "600 12.5px 'IBM Plex Sans'") + 10;
      const lx = Math.min(Math.max(px(root.id), lw / 2 + 2), total - lw / 2 - 2);
      el("rect", { x: lx - lw / 2, y: 6, width: lw, height: 18, rx: 4 }, lab);
      el("text", { x: lx, y: 19 }, lab, label(root));
      g.addEventListener("click", (e) => { e.stopPropagation(); choose(root.id); });
    }

    toks.forEach((w, i) => {
      const cx = px(w.id);
      const seg = w.segmentation !== w.text;
      const g = el("g", { class: `w ${groupOf(w)}`, tabindex: 0, role: "button", "data-id": w.id,
        "aria-label": `${w.text}: ${w.relation}, ${w.pos_name}` }, svg);
      el("rect", { x: cx - cols[i] / 2 + 3, y: y0 + 2, width: cols[i] - 6, height: seg ? 78 : 60, rx: 8 }, g);
      el("text", { class: "t", x: cx, y: y0 + 28 }, g, w.text);
      el("text", { class: "p", x: cx, y: y0 + 47 }, g, w.pos_name);
      if (seg) el("text", { class: "s", x: cx, y: y0 + 66 }, g, w.segmentation);
      g.addEventListener("click", (e) => { e.stopPropagation(); choose(w.id); });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(w.id); }
        const step = { ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1 }[e.key];
        if (step) {
          e.preventDefault();
          const next = svg.querySelector(`.w[data-id="${w.id + step}"]`);
          if (next) { next.focus(); choose(w.id + step); }
        }
        if (e.key === "Escape") choose(null);
      });
    });
    svg.addEventListener("click", () => choose(null));
    if (rtl) box.scrollLeft = box.scrollWidth;
    paint();
  }

  // Dim what is not related to the selected word or relation.
  function paint() {
    const svg = $("s-diagram").querySelector("svg");
    if (!svg) return;
    const onWord = new Set();
    const hot = (e) => {
      const dep = +e.dataset.dep;
      const head = +e.dataset.head;
      if (selected !== null) return dep === selected || head === selected;
      if (filter !== null) return e.dataset.rel === filter;
      return true;
    };
    svg.querySelectorAll(".edge").forEach((e) => {
      const on = hot(e);
      e.classList.toggle("dim", !on);
      if (on) { onWord.add(+e.dataset.dep); onWord.add(+e.dataset.head); }
    });
    svg.querySelectorAll(".w").forEach((w) => {
      const id = +w.dataset.id;
      const free = selected === null && filter === null;
      const self = id === selected || (filter !== null && byId(id).relation === filter);
      w.classList.toggle("dim", !(free || self || onWord.has(id)));
      w.classList.toggle("sel", id === selected);
    });
    document.querySelectorAll("#s-legend button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.rel === filter ? "true" : "false"));
  }

  function chipFor(w, rel) {
    const b = html("button", "chip " + groupOf(w));
    b.type = "button";
    html("span", "", b, w.text);
    if (rel) html("small", "", b, rel);
    b.addEventListener("click", () => choose(w.id));
    return b;
  }
  function row(dl, term, build) {
    html("dt", "", dl, term);
    const dd = html("dd", "", dl);
    build(dd);
  }

  function overview() {
    const panel = $("s-panel");
    panel.className = "s-panel";
    panel.replaceChildren();
    html("p", "role", panel, parsed.lang === "ckb" ? "Sorani (Central Kurdish), read from right to left" : "Kurmanji (Northern Kurdish), read from left to right");
    const dl = html("dl", "", panel);
    if (parsed.order) row(dl, "Word order", (d) => { d.textContent = parsed.order; });
    const al = parsed.alignment;
    if (al && al.alignment) {
      row(dl, "Alignment", (d) => {
        d.textContent = al.alignment === "ergative"
          ? "Ergative: the verb is past and transitive, so the agent takes the oblique case and the verb agrees with the object."
          : "Accusative: the subject is in the direct case and the verb agrees with it.";
      });
      if (al.agreement_ok === false) row(dl, "Agreement", (d) => { d.textContent = "Problem: " + al.notes.join("; ") + "."; });
      if (al.agreement_ok === true) row(dl, "Agreement", (d) => { d.textContent = `The verb agrees with the ${al.controller}.`; });
    }
    row(dl, "Next", (d) => { d.textContent = "Click any word, arrow or colour to see what it does in the sentence."; });
    parsed.notes.forEach((n) => row(dl, "Note", (d) => { d.textContent = n; }));
  }

  function explainWord(w) {
    const panel = $("s-panel");
    panel.className = "s-panel " + groupOf(w);
    panel.replaceChildren();
    html("h3", "", panel, w.text);
    const role = html("p", "role", panel);
    role.append(w.relation.charAt(0).toUpperCase() + w.relation.slice(1));
    if (w.kurdish) { role.append(" · "); html("span", "ku", role, w.kurdish); }
    html("p", "", panel, w.meaning.charAt(0).toUpperCase() + w.meaning.slice(1) + ".");
    const dl = html("dl", "", panel);
    row(dl, "Position", (d) => { d.textContent = w.position; });
    row(dl, "Depends on", (d) => {
      if (w.head) d.append(chipFor(byId(w.head), byId(w.head).relation));
      else d.textContent = "Nothing: this is the head of the sentence.";
    });
    const deps = dependents(w);
    if (deps.length) row(dl, "Its dependents", (d) => deps.forEach((x) => d.append(chipFor(x, x.relation))));
    if (w.upos !== "PUNCT") {
      row(dl, "Dictionary form", (d) => { d.textContent = w.lemma; });
      const parts = w.segmentation.split("+");
      const tags = w.gloss.split("+");
      if (parts.length > 1 && parts.length === tags.length) {
        row(dl, "Parts", (d) => parts.forEach((m, i) => {
          const c = html("span", "chip", d);
          html("span", "", c, m);
          html("small", "", c, tags[i]);
        }));
      }
      const feats = Object.entries(w.features).filter(([k]) => !["past_stem", "present_stem"].includes(k));
      if (feats.length) {
        row(dl, "Features", (d) => feats.forEach(([k, v]) => {
          const c = html("span", "chip", d);
          html("small", "", c, k);
          html("span", "", c, v);
        }));
      }
    }
    row(dl, "Explanation", (d) => { d.textContent = w.detail; });
  }

  function explainRelation(name) {
    const words = parsed.tokens.filter((w) => w.relation === name);
    const panel = $("s-panel");
    panel.className = "s-panel " + groupOf(words[0]);
    panel.replaceChildren();
    html("h3", "", panel, name.charAt(0).toUpperCase() + name.slice(1));
    html("p", "", panel, words[0].meaning.charAt(0).toUpperCase() + words[0].meaning.slice(1) + ".");
    const dl = html("dl", "", panel);
    row(dl, "In this sentence", (d) => words.forEach((w) => d.append(chipFor(w, w.head ? "→ " + byId(w.head).text : ""))));
  }

  function choose(id) {
    selected = id;
    filter = null;
    paint();
    if (id === null) overview(); else explainWord(byId(id));
  }

  function legend() {
    const box = $("s-legend");
    box.replaceChildren();
    const seen = new Map();
    parsed.tokens.forEach((w) => { if (w.upos !== "PUNCT" && !seen.has(w.relation)) seen.set(w.relation, w); });
    seen.forEach((w, name) => {
      const b = html("button", groupOf(w), box);
      b.type = "button";
      b.dataset.rel = name;
      html("i", "", b);
      b.append(name);
      b.addEventListener("click", () => {
        const on = filter !== name;
        selected = null;
        filter = on ? name : null;
        paint();
        if (on) explainRelation(name); else overview();
      });
    });
  }

  function render() {
    if (!py) return;
    const text = $("s-input").value.trim();
    py.globals.set("S_TEXT", text);
    py.globals.set("S_LANG", $("s-lang").value);
    parsed = JSON.parse(py.runPython(`
import json, zimankit
json.dumps(zimankit.parse(S_TEXT, S_LANG or None).to_dict(), ensure_ascii=False)
`));
    selected = null;
    filter = null;
    const known = EXAMPLES.find(([s]) => s === text);
    $("s-trans").textContent = known ? known[1] : "";
    draw();
    legend();
    if (parsed.tokens.length) overview(); else $("s-panel").replaceChildren();
    paint();
  }

  window.zkSentence = {
    init() {
      EXAMPLES.forEach(([s, gloss]) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = s;
        b.dir = "auto";
        b.title = gloss;
        b.addEventListener("click", () => { $("s-input").value = s; render(); });
        $("s-examples").append(b);
      });
      $("s-input").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 250); });
      $("s-lang").addEventListener("change", render);
    },
    ready(instance) {
      py = instance;
      render();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (parsed) { draw(); } });
    },
  };
})();
