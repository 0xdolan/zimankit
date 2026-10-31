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
  const fontStack = () => `Manrope, ${getComputedStyle(document.documentElement).getPropertyValue("--rtl-font").trim() || "Sahel"}, sans-serif`;
  const ctx = document.createElement("canvas").getContext("2d");
  function width(text, font) { ctx.font = font; return ctx.measureText(text).width; }
  const groupOf = (w) => "g-" + (GROUP[w.deprel] || "fn");
  const label = (w) => w.relation + (w.kurdish ? " · " + w.kurdish : "");
  const byId = (id) => parsed.tokens[id - 1];
  const dependents = (w) => parsed.tokens.filter((d) => d.head === w.id);

  // Word and arrow positions, in diagram units. The page and the image export both draw from this.
  function geometry(opts) {
    const { gap = 26, step = 36 } = opts || {}; // the export tightens the columns and raises the arrows to fit its format
    const toks = parsed.tokens;
    const rtl = parsed.lang === "ckb";
    const arcs = toks.filter((w) => w.head > 0 && w.upos !== "PUNCT");
    const font = fontStack();

    // columns: wide enough for the word, its class and form, and for the label of a one-step arrow
    const cols = toks.map((w) => Math.max(
      width(w.text, `700 20px ${font}`), width(w.pos_name, `500 12px ${font}`),
      w.segmentation !== w.text ? width(w.segmentation, `12px ${font}`) : 0, 34) + gap);
    const centre = [];
    let x = 10;
    cols.forEach((c) => { centre.push(x + c / 2); x += c; });
    arcs.filter((a) => Math.abs(a.id - a.head) === 1).forEach((a) => {
      const i = Math.min(a.id, a.head) - 1;
      const need = width(label(a), `700 13px ${font}`) + gap - 4 - (centre[i + 1] - centre[i]);
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
    const rise = (l) => 24 + l * step;
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
    return { toks, rtl, arcs, cols, total, px, level, rise, y0, port, maxLevel, height: y0 + 92, root: toks.find((w) => w.head === 0) };
  }

  function draw() {
    const box = $("s-diagram");
    box.replaceChildren();
    const toks = parsed.tokens;
    if (!toks.length) return;
    const { rtl, arcs, cols, total, px, level, rise, y0, port } = geometry();

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
      const lw = width(t, `700 13px ${fontStack()}`) + 10;
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
      const lw = width(label(root), `700 13px ${fontStack()}`) + 10;
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
      g.addEventListener("click", (e) => { e.stopPropagation(); choose(w.id); revealPanel(); });
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
    $("s-hint").hidden = box.scrollWidth <= box.clientWidth + 2;
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
    $("s-reset").hidden = selected === null && filter === null;
    document.querySelectorAll("#s-words tr[data-id]").forEach((r) => r.classList.toggle("sel", +r.dataset.id === selected));
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
    panel.append(window.zkLearn.section(window.zkLearn.forWord(parsed.tokens.find((w) => w.head === 0), parsed), "Learn more about this sentence"));
  }

  function backButton(panel) {
    const b = html("button", "btn small back", panel, "Back to the whole sentence");
    b.type = "button";
    b.addEventListener("click", () => choose(null));
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
          html("span", "", c, String(v).replaceAll("|", " / "));
        }));
      }
    }
    row(dl, "Explanation", (d) => { d.textContent = w.detail; });
    panel.append(window.zkLearn.section(window.zkLearn.forWord(w, parsed), "Learn more about this"));
    backButton(panel);
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
    panel.append(window.zkLearn.section(window.zkLearn.forWord(words[0], parsed), "Learn more about this"));
    backButton(panel);
  }

  function wordTable() {
    const box = $("s-words");
    box.replaceChildren();
    const wrap = html("div", "table-wrap", box);
    const t = html("table", "", wrap);
    const head = html("tr", "", t);
    ["Word", "Role", "Depends on"].forEach((x) => { html("th", "", head, x).scope = "col"; });
    parsed.tokens.filter((w) => w.upos !== "PUNCT").forEach((w) => {
      const tr = html("tr", groupOf(w), t);
      tr.dataset.id = w.id;
      const first = html("td", "", tr);
      const b = html("button", "w-text", first, w.text);
      b.type = "button";
      b.setAttribute("aria-label", `${w.text}: ${w.relation}`);
      const rel = html("span", "w-rel", html("td", "", tr));
      html("i", "", rel);
      rel.append(w.relation);
      html("td", "w-head", tr, w.head ? byId(w.head).text : "–");
      tr.addEventListener("click", () => { choose(w.id); revealPanel(); });
    });
  }

  // On a narrow screen the explanation sits above the table, so bring it into view.
  function revealPanel() {
    if (!window.matchMedia("(max-width: 900px)").matches) return;
    const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    $("s-panel").scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "nearest" });
  }

  function state(iconSvg, text) {
    const box = $("s-diagram");
    box.innerHTML = '<div class="diagram-state"></div>';
    const st = box.firstChild;
    if (iconSvg) st.innerHTML = iconSvg;
    html("span", "", st, text);
    $("s-hint").hidden = true;
  }

  function clearDetails() {
    $("s-legend").replaceChildren();
    $("s-words").replaceChildren();
    $("s-panel").replaceChildren();
    $("s-panel").className = "s-panel";
    $("s-panel").hidden = true;
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
    selected = null;
    filter = null;
    const known = EXAMPLES.find(([x]) => x === text);
    $("s-trans").textContent = known ? known[1] : "";
    if (!text) {
      parsed = null;
      clearDetails();
      state("", "Type a sentence above, or pick an example.");
      document.dispatchEvent(new Event("zk-parsed"));
      return;
    }
    try {
      py.globals.set("S_TEXT", text);
      py.globals.set("S_LANG", $("s-lang").value);
      parsed = JSON.parse(py.runPython(`
import json, zimankit
json.dumps(zimankit.parse(S_TEXT, S_LANG or None).to_dict(), ensure_ascii=False)
`));
    } catch (e) {
      parsed = null;
      clearDetails();
      state("", "This sentence could not be analysed. Please try another one, or tell us about it.");
      document.dispatchEvent(new Event("zk-parsed"));
      return;
    }
    $("s-panel").hidden = false;
    draw();
    legend();
    wordTable();
    overview();
    paint();
    document.dispatchEvent(new Event("zk-parsed"));
  }

  window.zkSentence = {
    current: () => parsed,
    geometry,
    fontStack,
    label,
    groupOf: (w) => GROUP[w.deprel] || "fn",
    translation: () => { const k = parsed && EXAMPLES.find(([x]) => x === $("s-input").value.trim()); return k ? k[1] : ""; },
    init() {
      document.addEventListener("zk-font", () => { if (parsed) { draw(); legend(); wordTable(); paint(); } });
      [["Kurmanji", EXAMPLES.slice(0, 5)], ["Sorani", EXAMPLES.slice(5)]].forEach(([name, list]) => {
        const group = html("div", "ex-group", $("s-examples"));
        html("span", "", group, name);
        list.forEach(([s, gloss]) => {
          const b = html("button", "", group, s);
          b.type = "button";
          b.title = gloss;
          b.addEventListener("click", () => { $("s-input").value = s; render(); });
        });
      });
      $("s-reset").addEventListener("click", () => { selected = null; choose(null); });
      // a click on the empty part of the diagram, or Escape, also clears the selection
      $("s-diagram").addEventListener("click", (e) => { if (parsed && !e.target.closest(".w, .edge")) choose(null); });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && parsed && !$("sent").hidden && !document.querySelector("dialog[open]") && (selected !== null || filter !== null)) choose(null);
      });
      $("s-input").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(render, 250); });
      $("s-lang").addEventListener("change", render);
    },
    failed() { clearDetails(); state("", "The analyser could not start. Check your connection and reload the page."); },
    ready(instance) {
      py = instance;
      window.zkTools.init();
      render();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (parsed) { draw(); wordTable(); } });
    },
  };
})();
