// Playground: load zimankit into Pyodide, run a tool on the input and show the result in a view made for it.
(function () {
  const $ = (id) => document.getElementById(id);
  const PERSON = { "1sg": "I", "2sg": "you", "3sg": "he, she, it", "1pl": "we", "2pl": "you (plural)", "3pl": "they", pl: "we, you, they", external: "no agent ending", "": "–" };
  let py = null;
  let cmd = "analyze";
  let timer = null;
  let last = null; // the data of the latest result
  let view = "table";

  // ---------- small DOM helpers ----------
  function h(tag, cls, parent, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) { e.textContent = text; e.dir = "auto"; }
    if (parent) parent.append(e);
    return e;
  }

  // A table that becomes labelled rows on a phone. Cells: text, a node, or a function that fills the cell.
  function table(parent, headers, rows, opts) {
    const wrap = h("div", "table-wrap", parent);
    const t = h("table", (opts && opts.fixed) ? "" : "rt", wrap);
    const head = h("tr", "", h("thead", "", t));
    headers.forEach((x) => { h("th", "", head, x).scope = "col"; });
    const body = h("tbody", "", t);
    rows.forEach((r) => {
      const tr = h("tr", r.cls || "", body);
      (r.cells || r).forEach((cell, i) => {
        const td = h("td", "", tr);
        td.dataset.label = headers[i];
        // one wrapper per cell: on a phone the cell is a grid of label and value, and text direction stays inside
        const inner = h("div", "cell", td);
        if (typeof cell === "function") cell(inner);
        else if (cell instanceof Node) inner.append(cell);
        else { inner.textContent = cell === undefined || cell === null || cell === "" ? "–" : cell; inner.dir = "auto"; }
      });
    });
    return t;
  }

  function chip(parent, main, small, cls) {
    const c = h("span", "chip" + (cls ? " " + cls : ""), parent);
    h("span", "", c, main);
    if (small) h("small", "", c, small);
    return c;
  }
  function badge(parent, text, kind) { return h("span", "badge" + (kind ? " " + kind : ""), parent, text); }
  const mono = (s, big) => { const e = h("span", big ? "mono big" : "mono", null, s); return e; };
  const features = (f) => (td) => {
    const list = Object.entries(f || {}).filter(([k]) => !["past_stem", "present_stem", "pos"].includes(k));
    if (!list.length) { td.textContent = "–"; return; }
    list.forEach(([k, v]) => chip(td, String(v).replaceAll("|", " / "), k));
  };
  const parts = (a) => (td) => {
    if (a.segments && a.segments.length > 1) a.segments.forEach(([m, g]) => chip(td, m, g));
    else td.append(h("span", "", null, a.segmentation));
  };

  // ---------- the views ----------
  const TOOLS = {
    analyze: {
      title: "Analyze words",
      desc: "Each word's dictionary form, word class, parts and grammatical features.",
      hint: "Words in Sorani or Kurmanji, separated by spaces or lines",
      examples: ["کتێبەکەم", "ماڵەکانمان", "jinekê", "xwendiye", "دەچم"],
      start: "کتێبەکەم\nماڵەکانمان\njinekê\nxwendiye",
      opts: [{ id: "top", label: "Show other readings too" }],
      call: (text, o, lang) => ["analyze", { text, lang, top: o.top ? 3 : 1 }],
      summary: (d) => `${d.length} word${d.length === 1 ? "" : "s"}`,
      render(d, box) {
        const rows = [];
        d.forEach((w) => w.analyses.forEach((a, i) => rows.push({
          cls: i ? "alt" : "",
          cells: [(td) => { h("strong", "word", td, i ? "" : w.word); if (i) td.append(h("span", "muted small", null, `reading ${i + 1}`)); },
            a.lemma, (td) => badge(td, a.pos), parts(a), features(a.features)],
        })));
        table(box, ["Word", "Dictionary form", "Class", "Parts", "Features"], rows);
      },
      csv: (d) => [["word", "lemma", "pos", "segmentation", "gloss", "features"],
        ...d.flatMap((w) => w.analyses.map((a) => [w.word, a.lemma, a.pos, a.segmentation, a.gloss, JSON.stringify(a.features)]))],
      langs: (d) => d.map((w) => w.lang),
    },
    ipa: {
      title: "IPA and syllables",
      desc: "How each word is pronounced, in the International Phonetic Alphabet. Brackets mark the unwritten Sorani vowel.",
      hint: "Words or text",
      examples: ["پیاوەکە", "کتێبەکەم", "jinekê", "dîtin", "Kurdistan"],
      start: "پیاوەکە کتێبەکەم jinekê dîtin",
      opts: [{ id: "narrow", label: "Kurmanji: narrow (aspiration, ŋ)" }, { id: "plain", label: "Sorani: do not mark the inferred vowel" }],
      call: (text, o, lang) => ["ipa", { text, lang, narrow: !!o.narrow, plain: !!o.plain }],
      summary: (d) => `${d.length} word${d.length === 1 ? "" : "s"}`,
      render(d, box) {
        table(box, ["Word", "IPA", "Syllables", "Other script"], d.map((w) => [
          (td) => h("strong", "word", td, w.word), mono(w.ipa, true),
          (td) => w.syllables.forEach((s) => td.append(h("span", "syll mono", null, s))), w.other_script,
        ]));
      },
      csv: (d) => [["word", "ipa", "syllables", "other_script"], ...d.map((w) => [w.word, w.ipa, w.syllables.join("."), w.other_script])],
      langs: (d) => d.map((w) => w.lang),
    },
    translit: {
      title: "Transliterate",
      desc: "Sorani from the Arabic-based script to Latin, and Kurmanji from Hawar Latin to the Arabic-based script.",
      hint: "Text, one sentence per line",
      lines: true,
      examples: ["ئەمڕۆ هەوا خۆشە", "Îro hewa xweş e", "زمانی کوردی", "Zimanê kurdî"],
      start: "ئەمڕۆ هەوا خۆشە\nÎro hewa xweş e",
      call: (lines, o, lang) => ["translit", { lines, lang }],
      summary: (d) => `${d.length} line${d.length === 1 ? "" : "s"}`,
      render(d, box) {
        d.forEach((l) => {
          const card = h("div", "compare", box);
          const a = h("div", "", card); h("p", "compare-label", a, l.lang === "ckb" ? "Arabic-based script" : "Latin (Hawar)"); h("p", "compare-text", a, l.input);
          const b = h("div", "", card); h("p", "compare-label", b, l.lang === "ckb" ? "Latin (Hawar)" : "Arabic-based script"); h("p", "compare-text strong", b, l.output);
        });
        const rows = d.flatMap((l) => l.words.map((w) => [w.from, (td) => h("strong", "word", td, w.to)]));
        if (rows.length) { h("p", "panel-title", box, "Word by word"); table(box, ["Word", "Transliteration"], rows, { fixed: true }); }
      },
      csv: (d) => [["input", "output"], ...d.flatMap((l) => l.words.map((w) => [w.from, w.to]))],
      langs: (d) => d.map((l) => l.lang),
    },
    conjugate: {
      title: "Conjugate a verb",
      desc: "Every form of a verb by tense and person, affirmative and negative.",
      hint: "One infinitive",
      single: true,
      examples: ["کردن", "چوون", "kirin", "dîtin", "xwendin"],
      start: "kirin",
      fields: [{ id: "present", label: "Present stem (for verbs not in the list)" }],
      call: (text, o, lang) => ["conjugate", { infinitive: text.split(/\s+/)[0], lang, present: o.present || null }],
      summary: (d) => (d.error ? "" : `${d.count} forms`),
      render(d, box) {
        if (d.error) { state(box, d.error); return; }
        const top = h("div", "verb-head", box);
        h("span", "verb-title", top, d.infinitive);
        badge(top, d.lang === "ckb" ? "Sorani" : "Kurmanji");
        badge(top, d.listed ? "From the verb list" : "Built by rule: check it", d.listed ? "ok" : "warn");
        if (d.slug && window.zkLearn.verbPage(d.lang, d.slug)) {
          const a = h("a", "btn small", top, "Full verb page");
          a.href = window.zkLearn.verbPage(d.lang, d.slug).url; a.target = "_blank"; a.rel = "noopener";
        }
        const grid = h("div", "verb-grid", box);
        d.groups.forEach((g) => {
          const c = h("div", "verb-card", grid);
          h("h3", "", c, g.title);
          table(c, ["Person", "Affirmative", "Negative"], g.rows.map((r) => [
            (td) => { h("span", "person", td, PERSON[r.person] !== undefined ? PERSON[r.person] : r.person); if (r.person && r.person !== "external") h("small", "muted", td, " " + r.person); },
            (td) => h("strong", "word", td, r.affirmative.join(" / ") || "–"), r.negative.join(" / "),
          ]), { fixed: true });
        });
        if (d.other.length) {
          h("p", "panel-title", box, "Other forms");
          const row = h("div", "chips", box);
          d.other.forEach((f) => chip(row, f.form, f.features.form || Object.values(f.features).join(" ")));
        }
      },
      csv: (d) => (d.error ? [] : [["tense", "person", "affirmative", "negative"],
        ...d.groups.flatMap((g) => g.rows.map((r) => [g.title, r.person, r.affirmative.join(" / "), r.negative.join(" / ")])),
        ...d.other.map((f) => ["other", "", f.form, ""])]),
      langs: (d) => [d.lang],
    },
    ergativity: {
      title: "Check ergativity",
      desc: "Kurmanji past transitive clauses are ergative: the agent takes the oblique case, and the verb agrees with the object. This finds the verb and its arguments and checks the agreement.",
      hint: "Kurmanji sentences, one per line",
      lines: true,
      noLang: true,
      examples: ["Min tu dîtim.", "Min tu dîtî.", "Wî nan xwar.", "Ez diçim malê."],
      start: "Min tu dîtim.\nMin tu dîtî.",
      call: (lines) => ["ergativity", { lines }],
      summary: (d) => `${d.length} sentence${d.length === 1 ? "" : "s"}`,
      render(d, box) {
        d.forEach((r) => {
          const c = h("div", "result-card", box);
          h("h3", "", c, r.sentence);
          const tags = h("div", "chips", c);
          if (r.alignment) badge(tags, r.alignment === "ergative" ? "Ergative" : "Accusative");
          if (r.agreement_ok === true) badge(tags, "Agreement correct", "ok");
          if (r.agreement_ok === false) badge(tags, "Agreement problem", "err");
          if (r.agreement_ok === null && r.verb) badge(tags, "Agreement not checked", "warn");
          if (!r.verb) { h("p", "muted", c, "No finite verb was found."); return; }
          const arg = (x) => (x ? `${x.token} (${x.case === "obl" ? "oblique" : "direct"}${x.person ? ", " + x.person : ""})` : "not written");
          const dl = h("dl", "facts-list", c);
          [["Verb", `${r.verb} (from ${r.lemma})`], ["Tense stem", r.tense_stem], ["Transitive", r.transitive ? "Yes" : "No"],
            ["Agent or subject", arg(r.agent)], ["Object", arg(r.object)], ["Verb ending marks", r.verb_person], ["Verb agrees with", r.controller]]
            .forEach(([k, v]) => { h("dt", "", dl, k); h("dd", "", dl, v || "–"); });
          if (r.notes.length) { const n = h("ul", "notes", c); r.notes.forEach((x) => h("li", "", n, x)); }
        });
      },
      csv: (d) => [["sentence", "verb", "alignment", "agent", "object", "agreement_ok"],
        ...d.map((r) => [r.sentence, r.verb, r.alignment, r.agent && r.agent.token, r.object && r.object.token, r.agreement_ok])],
      langs: () => ["kmr"],
    },
    lid: {
      title: "Identify the language",
      desc: "Tells Sorani, Kurmanji, Zazaki and Gorani apart from each other and from Persian, Arabic, Turkish and English. Longer text gives a surer answer.",
      hint: "Sentences, one per line",
      lines: true,
      noLang: true,
      examples: ["ئەمڕۆ هەوا خۆشە", "Îro hewa xweş e", "Ma yew roje şima ra vat ke ziwanê ma zaf rind o", "امروز هوا خوب است"],
      start: "ئەمڕۆ هەوا خۆشە\nÎro hewa xweş e\nMa yew roje şima ra vat ke ziwanê ma zaf rind o",
      call: (lines) => ["lid", { lines }],
      summary: (d) => `${d.length} text${d.length === 1 ? "" : "s"}`,
      render(d, box) {
        table(box, ["Text", "Language", "Script", "Confidence"], d.map((r) => [
          r.text, (td) => { h("strong", "", td, r.name); h("span", "muted small", td, ` ${r.lang}`); }, r.script,
          (td) => { const m = h("div", "meter", td); const bar = h("span", "", m); bar.style.width = `${Math.round(r.confidence * 100)}%`; h("span", "small", td, `${Math.round(r.confidence * 100)}%`); },
        ]));
      },
      csv: (d) => [["text", "lang", "name", "script", "confidence"], ...d.map((r) => [r.text, r.lang, r.name, r.script, r.confidence])],
      langs: () => [],
    },
    normalize: {
      title: "Normalize text",
      desc: "Replaces look-alike letters and cleans invisible characters, so that the same word is always written the same way.",
      hint: "Text with non-standard letters or spellings, one per line",
      lines: true,
      examples: ["كوردي", "ئەم كتێبە", "Kurdî Zimané"],
      start: "كوردي\nئەم كتێبە",
      call: (lines, o, lang) => ["normalize", { lines, lang }],
      summary: (d) => `${d.filter((l) => l.changed).length} of ${d.length} changed`,
      render(d, box) {
        d.forEach((l) => {
          const card = h("div", "compare", box);
          const a = h("div", "", card); h("p", "compare-label", a, "Before"); h("p", "compare-text", a, l.input);
          const b = h("div", "", card); h("p", "compare-label", b, "After"); h("p", "compare-text strong", b, l.output);
          if (!l.changed) { const n = h("div", "compare-note", card); badge(n, "Already standard", "ok"); return; }
          const n = h("div", "compare-note", card);
          table(n, ["From", "To", "Character"], l.changes.map((c) => [
            (td) => { h("strong", "word", td, c.from || "–"); h("small", "muted code", td, " " + c.from_code); },
            (td) => { h("strong", "word", td, c.to || "(removed)"); h("small", "muted code", td, " " + c.to_code); },
            `${c.from_name || "–"} → ${c.to_name || "removed"}`,
          ]));
        });
      },
      csv: (d) => [["input", "output", "changed"], ...d.map((l) => [l.input, l.output, l.changed])],
      langs: (d) => d.map((l) => l.lang),
    },
    validate: {
      title: "Validate spelling",
      desc: "Normalizes each word and reports what is still wrong with it.",
      hint: "Words, separated by spaces or lines",
      examples: ["كتێب", "kurdî", "ڕۆژ", "wörld"],
      start: "كتێب kurdî ڕۆژ wörld",
      call: (text, o, lang) => ["validate", { text, lang }],
      summary: (d) => `${d.filter((w) => !w.problems.length).length} of ${d.length} valid`,
      render(d, box) {
        table(box, ["Word", "Normalized", "Result"], d.map((w) => ({
          cls: w.problems.length ? "row-err" : "",
          cells: [w.input, (td) => h("strong", "word", td, w.normalized),
            (td) => {
              badge(td, w.problems.length ? "Problem" : w.changed ? "Valid once normalized" : "Valid", w.problems.length ? "err" : w.changed ? "warn" : "ok");
              if (w.problems.length) { const n = h("ul", "notes", td); w.problems.forEach((p) => h("li", "", n, p)); }
            }],
        })));
      },
      csv: (d) => [["input", "normalized", "problems"], ...d.map((w) => [w.input, w.normalized, w.problems.join("; ")])],
      langs: (d) => d.map((w) => w.lang),
    },
    tokenize: {
      title: "Tokenize text",
      desc: "Splits text into words, numbers and punctuation, with each token's position.",
      hint: "Text, one sentence per line",
      lines: true,
      noLang: true,
      examples: ["کتێبەکەم، خوێندەوە.", "Min pirtûk xwend.", "Sala 2026 baş e!"],
      start: "کتێبەکەم، خوێندەوە.",
      call: (lines) => ["tokenize", { lines }],
      summary: (d) => { const n = d.reduce((s, l) => s + l.tokens.length, 0); return `${n} token${n === 1 ? "" : "s"}`; },
      render(d, box) {
        d.forEach((l) => {
          const row = h("div", "chips token-row", box);
          row.dir = "auto";
          l.tokens.forEach((t) => chip(row, t.text, t.kind, "k-" + t.kind));
        });
        table(box, ["Token", "Kind", "Start", "End"], d.flatMap((l) => l.tokens.map((t) => [(td) => h("strong", "word", td, t.text), t.kind, String(t.start), String(t.end)])), { fixed: true });
      },
      csv: (d) => [["token", "kind", "start", "end"], ...d.flatMap((l) => l.tokens.map((t) => [t.text, t.kind, t.start, t.end]))],
      langs: () => [],
    },
  };

  // ---------- pretty JSON ----------
  function jsonView(data) {
    const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const src = esc(JSON.stringify(data, null, 2));
    const out = src.replace(/("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false)\b|\b(null)\b|(-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)/g,
      (m, str, colon, bool, nul, num) => {
        if (str) return colon ? `<span class="j-key">${str}</span>${colon}` : `<span class="j-str">${str}</span>`;
        if (bool) return `<span class="j-bool">${bool}</span>`;
        if (nul) return `<span class="j-null">${nul}</span>`;
        return `<span class="j-num">${num}</span>`;
      });
    const pre = document.createElement("pre");
    pre.className = "json";
    pre.innerHTML = out;
    return pre;
  }

  // ---------- saving ----------
  function save(name, type, text) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type }));
    a.download = name;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }
  const csvText = (rows) => "\ufeff" + rows.map((r) => r.map((v) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }).join(",")).join("\n");

  // ---------- running ----------
  function state(box, text) { h("div", "diagram-state", box, text); }

  function options() {
    const o = {};
    document.querySelectorAll("#t-opts [data-opt]").forEach((i) => { o[i.dataset.opt] = i.type === "checkbox" ? i.checked : i.value.trim(); });
    return o;
  }

  function run() {
    if ($("play").hidden) return;
    const tool = TOOLS[cmd];
    const box = $("t-result");
    const text = $("input").value.trim();
    if (!py) return;
    if (!text) {
      last = null;
      box.replaceChildren();
      state(box, "Type something above, or pick an example.");
      $("t-learn").replaceChildren(window.zkLearn.section(window.zkLearn.forTool(cmd, [])));
      return;
    }
    const lang = $("lang").value || null;
    const input = tool.lines ? text.split(/\n+/).map((s) => s.trim()).filter(Boolean) : text;
    const [name, payload] = tool.call(input, options(), lang);
    try {
      py.globals.set("ZK_TOOL", name);
      py.globals.set("ZK_PAYLOAD", JSON.stringify(payload));
      last = JSON.parse(py.runPython("import json, playground_tools\njson.dumps(playground_tools.run(ZK_TOOL, json.loads(ZK_PAYLOAD)), ensure_ascii=False)"));
    } catch (e) {
      last = null;
      box.replaceChildren();
      state(box, "This input could not be processed. Please try something else, or tell us about it.");
      return;
    }
    show();
  }

  function show() {
    const tool = TOOLS[cmd];
    const box = $("t-result");
    box.replaceChildren();
    const res = h("div", "res", box);
    const bar = h("div", "res-bar", res);
    h("p", "res-count", bar, tool.summary(last));
    const seg = h("div", "seg", bar);
    seg.setAttribute("role", "group");
    seg.setAttribute("aria-label", "View");
    [["table", "Result"], ["json", "JSON"]].forEach(([v, label]) => {
      const b = h("button", "", seg, label);
      b.type = "button";
      b.setAttribute("aria-pressed", v === view ? "true" : "false");
      b.addEventListener("click", () => { view = v; show(); });
    });
    const acts = h("div", "res-actions", bar);
    const copy = h("button", "btn small", acts, "Copy JSON");
    copy.type = "button";
    copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(JSON.stringify(last, null, 2)); copy.textContent = "Copied"; } catch (e) { copy.textContent = "Could not copy"; }
      setTimeout(() => { copy.textContent = "Copy JSON"; }, 1500);
    });
    const dj = h("button", "btn small", acts, "Download JSON");
    dj.type = "button";
    dj.addEventListener("click", () => save(`zimankit-${cmd}.json`, "application/json", JSON.stringify(last, null, 2)));
    const rows = tool.csv(last);
    if (rows.length) {
      const dc = h("button", "btn small", acts, "Download CSV");
      dc.type = "button";
      dc.addEventListener("click", () => save(`zimankit-${cmd}.csv`, "text/csv", csvText(rows)));
    }
    const body = h("div", "res-body", res);
    if (view === "json") body.append(jsonView(last));
    else tool.render(last, body);
    const langs = [...new Set(tool.langs(last))];
    $("t-learn").replaceChildren(window.zkLearn.section(window.zkLearn.forTool(cmd, langs)));
  }

  // ---------- switching tools ----------
  function select(name) {
    document.querySelectorAll(".tools button").forEach((b) => {
      const on = b.dataset.cmd === name;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      if (on) b.scrollIntoView({ block: "nearest", inline: "nearest" });
    });
    $("sent").hidden = name !== "sentence";
    $("play").hidden = name === "sentence";
    if (name === "sentence") return;
    cmd = name;
    view = "table";
    const c = TOOLS[name];
    $("t-title").textContent = c.title;
    $("t-desc").textContent = c.desc;
    $("hint").textContent = c.hint;
    $("input").rows = c.single ? 1 : 3;
    $("input").value = c.start;
    $("t-langbox").hidden = !!c.noLang;
    const opts = $("t-opts");
    opts.replaceChildren();
    (c.opts || []).forEach((o) => {
      const l = h("label", "", opts);
      const i = h("input", "", l);
      i.type = "checkbox";
      i.dataset.opt = o.id;
      l.append(" " + o.label);
      i.addEventListener("change", run);
    });
    (c.fields || []).forEach((f) => {
      const l = h("label", "field-inline", opts);
      l.append(f.label);
      const i = h("input", "", l);
      i.type = "text";
      i.dataset.opt = f.id;
      i.addEventListener("input", later);
    });
    const ex = $("examples");
    ex.replaceChildren();
    c.examples.forEach((e) => {
      const b = h("button", "", ex, e);
      b.type = "button";
      b.addEventListener("click", () => { $("input").value = e; run(); });
    });
    run();
  }

  function later() { clearTimeout(timer); timer = setTimeout(run, 250); }

  function setStatus(text, ok) {
    $("status").innerHTML = `<span class="dot${ok === false ? " err" : ok ? " ok" : ""}"></span><span></span>`;
    $("status").lastChild.textContent = text;
  }

  async function boot() {
    try {
      py = await loadPyodide();
      setStatus("Loading zimankit…");
      const meta = await (await fetch("pkg/wheel.json")).json();
      const wheel = await (await fetch("pkg/" + meta.wheel)).arrayBuffer();
      py.unpackArchive(wheel, "wheel");
      py.FS.writeFile("playground_tools.py", await (await fetch("py/playground_tools.py")).text());
      py.runPython("import zimankit, playground_tools");
      setStatus(`zimankit ${meta.version} is running in your browser`, true);
      window.zkSentence.ready(py);
      run();
    } catch (e) {
      py = null;
      setStatus("Could not start Python here. Check your connection and reload the page. (" + e.message + ")", false);
      window.zkSentence.failed();
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".tools button").forEach((b) => b.addEventListener("click", () => select(b.dataset.cmd)));
    $("input").addEventListener("input", later);
    $("lang").addEventListener("change", run);
    select("sentence");
    window.zkSentence.init();
    boot();
  });
})();
