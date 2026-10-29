// Playground: load the zimankit wheel into Pyodide and run the CLI commands on the input.
(function () {
  const COMMANDS = {
    analyze: { hint: "Words in Sorani or Kurmanji, one per line or separated by spaces", opts: [["--top", "show 3 analyses per word", "3", false]],
      examples: ["کتێبەکەم", "ماڵەکانمان", "jinekê", "xwendiye", "دەچمە"] },
    ipa: { hint: "Words or text", opts: [["--syllables", "mark syllables"], ["--narrow", "Kurmanji: narrow (aspiration, ŋ)"], ["--plain", "Sorani: do not mark the inferred vowel"]],
      examples: ["پیاوەکە", "کتێبەکەم", "jinekê", "dîtin", "Kurdistan"] },
    translit: { hint: "Sorani text (to Latin) or Kurmanji text (to the Arabic-based script), one per line", opts: [],
      examples: ["ئەمڕۆ هەوا خۆشە", "Îro hewa xweş e", "زمانی کوردی", "Zimanê kurdî"] },
    conjugate: { hint: "One infinitive: a Sorani or Kurmanji verb", opts: [], single: true,
      examples: ["کردن", "چوون", "kirin", "dîtin", "xwendin"] },
    ergativity: { hint: "Kurmanji sentences, one per line", opts: [], lines: true,
      examples: ["Min tu dîtim.", "Min tu dîtî.", "Wî nan xwar.", "Ez diçim malê."] },
    lid: { hint: "Sentences, one per line", opts: [], lines: true,
      examples: ["ئەمڕۆ هەوا خۆشە", "Îro hewa xweş e", "Ma yew roje şima ra vat ke ziwanê ma zaf rind o", "امروز هوا خوب است"] },
    normalize: { hint: "Text with non-standard letters or spellings, one per line", opts: [], lines: true,
      examples: ["كوردي", "ئەم كتێبە"] },
    validate: { hint: "Words, one per line or separated by spaces", opts: [],
      examples: ["كتێب", "kurdî", "ڕۆژ"] },
    tokenize: { hint: "Text, one per line", opts: [], lines: true,
      examples: ["کتێبەکەم، خوێندەوە.", "Min pirtûk xwend."] },
  };
  let cmd = "analyze";
  let py = null;
  const $ = (id) => document.getElementById(id);

  function setStatus(text, ok) {
    $("status").innerHTML = `<span class="dot${ok ? " ok" : ""}"></span><span></span>`;
    $("status").lastChild.textContent = text;
  }

  function select(name) {
    cmd = name;
    const c = COMMANDS[name];
    document.querySelectorAll(".tools button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.cmd === name ? "true" : "false"));
    $("hint").textContent = c.hint;
    $("opts").innerHTML = "";
    c.opts.forEach(([flag, label, value, on]) => {
      const l = document.createElement("label");
      const i = document.createElement("input");
      i.type = "checkbox"; i.dataset.flag = flag; if (value) i.dataset.value = value; i.checked = on === undefined ? !!value : on;
      l.append(i, " " + label);
      $("opts").append(l);
    });
    $("examples").innerHTML = "";
    c.examples.forEach((e) => {
      const b = document.createElement("button");
      b.type = "button"; b.textContent = e; b.dir = "auto";
      b.addEventListener("click", () => {
        const cur = $("input").value.trim();
        $("input").value = c.single || c.lines || !cur ? e : cur + "\n" + e;
        run();
      });
      $("examples").append(b);
    });
    if (c.single) $("input").value = c.examples[0];
    else if (c.lines) $("input").value = c.examples.slice(0, 2).join("\n");
    else $("input").value = c.examples.slice(0, 4).join("\n");
    run();
  }

  function argv() {
    const c = COMMANDS[cmd];
    const args = [cmd];
    const lang = $("lang").value;
    if (lang) args.push("--lang", lang);
    $("opts").querySelectorAll("input:checked").forEach((i) => { args.push(i.dataset.flag); if (i.dataset.value) args.push(i.dataset.value); });
    const text = $("input").value.trim();
    if (!text) return null;
    if (c.single) args.push(text.split(/\s+/)[0]);
    else if (c.lines) args.push(...text.split(/\n+/).map((s) => s.trim()).filter(Boolean));
    else args.push(...text.split(/\s+/).filter(Boolean));
    return args;
  }

  function run() {
    const args = argv();
    $("cmdline").textContent = args ? "$ zimankit " + args.map((a) => (/\s/.test(a) ? JSON.stringify(a) : a)).join(" ") : "";
    if (!py || !args) return;
    const table = ["analyze", "lid"].includes(cmd);
    if (table) args.splice(1, 0, "--json");
    py.globals.set("ARGS", py.toPy(args));
    try {
      const out = py.runPython(`
import io, contextlib, json
from zimankit.cli import main
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        main(list(ARGS))
except SystemExit as e:
    if e.code not in (0, None):
        buf.write(str(e.code))
out = buf.getvalue()
if ARGS[0] == "ergativity":
    out = "\\n\\n".join(json.dumps(json.loads(l), ensure_ascii=False, indent=2) for l in out.splitlines() if l.strip())
out
`);
      if (table && out.trim()) return showTable(out);
      $("term").hidden = false; $("table").hidden = true;
      $("out").textContent = out.trim() || "(no output)";
    } catch (e) {
      $("out").textContent = String(e).split("\n").slice(-3).join("\n");
    }
  }

  function cell(tr, text, cls) {
    const td = document.createElement("td");
    td.textContent = text; td.dir = "auto"; if (cls) td.className = cls;
    tr.append(td);
  }

  // analyze and lid print one JSON object per input; show them as a table.
  function showTable(out) {
    const rows = out.trim().split("\n").map((l) => JSON.parse(l));
    const t = document.createElement("table");
    const head = cmd === "analyze" ? ["word", "lemma", "pos", "segmentation", "gloss", "features"] : ["language", "script", "confidence"];
    const h = document.createElement("tr");
    head.forEach((x) => { const th = document.createElement("th"); th.textContent = x; h.append(th); });
    t.append(h);
    rows.forEach((r) => {
      if (cmd === "lid") {
        const tr = document.createElement("tr");
        cell(tr, r.lang); cell(tr, r.script); cell(tr, String(r.confidence));
        t.append(tr);
        return;
      }
      r.analyses.forEach((a, i) => {
        const tr = document.createElement("tr");
        if (i) tr.className = "alt";
        cell(tr, i ? "" : r.token); cell(tr, a.lemma); cell(tr, a.pos); cell(tr, a.segmentation); cell(tr, a.gloss, "f");
        cell(tr, Object.entries(a.features || {}).map(([k, v]) => k + "=" + v).join(" "), "f");
        t.append(tr);
      });
    });
    $("table").replaceChildren(t);
    $("table").hidden = false; $("term").hidden = true;
  }

  async function boot() {
    try {
      py = await loadPyodide();
      setStatus("Loading zimankit…");
      const meta = await (await fetch("pkg/wheel.json")).json();
      const wheel = await (await fetch("pkg/" + meta.wheel)).arrayBuffer();
      py.unpackArchive(wheel, "wheel");
      py.runPython("import zimankit");
      setStatus(`zimankit ${meta.version} is running in your browser`, true);
      $("run").disabled = false;
      run();
    } catch (e) {
      py = null;
      setStatus("Could not start Python here: " + e.message);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".tools button").forEach((b) => b.addEventListener("click", () => select(b.dataset.cmd)));
    $("run").addEventListener("click", run);
    $("lang").addEventListener("change", run);
    $("opts").addEventListener("change", run);
    $("input").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) run(); });
    select("analyze");
    boot();
  });
})();
