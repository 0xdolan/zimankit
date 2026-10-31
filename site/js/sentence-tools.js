// Playground, Sentence tab: choose the diagram's colours, and export it as an image for social media.
(function () {
  const $ = (id) => document.getElementById(id);
  const SITE = "0xdolan.github.io/zimankit";
  const REPO = "github.com/0xdolan/zimankit";
  const FLAG_SUN = "M450 150l11.24 76.264 33.222-69.563-11.738 76.19 52.249-56.68-33.674 69.344 66.634-38.761-52.616 56.338 75.098-17.399-66.885 38.327 76.89 5.51-75.21 16.909 71.85 27.929-76.852-6.011 60.425 47.867-71.666-28.397 43.632 63.55-60.113-48.259 22.962 73.589-43.217-63.834.25 77.087L450 376.264 427.518 450l.251-77.087-43.217 63.834 22.962-73.589-60.113 48.26 43.632-63.551-71.666 28.397 60.425-47.867-76.852 6.011 71.85-27.93-75.21-16.908 76.89-5.51-66.885-38.327 75.098 17.399-52.616-56.338 66.634 38.76-33.674-69.343 52.249 56.68-11.738-76.19 33.221 69.563z";
  const GROUPS = [
    ["root", "Main verb"], ["nsubj", "Subject"], ["obj", "Object"], ["obl", "Oblique"], ["case", "Adposition"],
    ["mod", "Modifier"], ["det", "Determiner"], ["conj", "Coordination"], ["adv", "Adverb"], ["fn", "Other"],
  ];
  // Each preset: colours for a light ground and for a dark ground, readable at 4.5:1 or better.
  const PRESETS = {
    Default: null,
    "High contrast": {
      light: { root: "#000000", nsubj: "#A5001A", obj: "#7F3700", obl: "#00478F", case: "#5417A8", mod: "#00593C", det: "#00565F", conj: "#8F0F47", adv: "#5F4500", fn: "#404040" },
      dark: { root: "#FFFFFF", nsubj: "#FF9C94", obj: "#FFC285", obl: "#94CCFF", case: "#D2B8FF", mod: "#85E5AB", det: "#7AE5EA", conj: "#FFA8D6", adv: "#F5DC7A", fn: "#D4D4D4" },
    },
    "Colour-blind safe": {
      light: { root: "#000000", nsubj: "#B84E00", obj: "#0072B2", obl: "#007A5E", case: "#A0447A", mod: "#0B6E99", det: "#6B5B00", conj: "#8A2BA8", adv: "#8A5A00", fn: "#5C5C5C" },
      dark: { root: "#FFFFFF", nsubj: "#E69F00", obj: "#56B4E9", obl: "#2BC9A0", case: "#E08FC0", mod: "#8FD3F5", det: "#F0E442", conj: "#D3A6F0", adv: "#F5C26B", fn: "#BDBDBD" },
    },
    "Single colour": {
      light: Object.fromEntries(GROUPS.map(([g]) => [g, "#171717"])),
      dark: Object.fromEntries(GROUPS.map(([g]) => [g, "#FAFAFA"])),
    },
  };

  let preset = "Default";
  let custom = { light: {}, dark: {} }; // changes on top of the preset, per theme
  try {
    const saved = JSON.parse(localStorage.getItem("zimankit-colours") || "null");
    if (saved && saved.custom) { preset = PRESETS[saved.preset] === undefined ? "Default" : saved.preset; custom = saved.custom; }
  } catch (e) { /* storage blocked or corrupt: use the defaults */ }

  function save() {
    try { localStorage.setItem("zimankit-colours", JSON.stringify({ preset, custom })); } catch (e) { /* storage blocked */ }
  }

  // ---------- the design tokens, as written in site.css ----------
  let tokenCache = null;
  function tokens(theme) {
    if (!tokenCache) {
      tokenCache = { light: {}, dark: {} };
      for (const sheet of document.styleSheets) {
        let rules = [];
        try { rules = sheet.cssRules; } catch (e) { continue; }
        for (const rule of rules) {
          const which = { ":root": "light", ':root[data-theme="dark"]': "dark" }[rule.selectorText];
          if (!which) continue;
          for (const name of rule.style) {
            if (name.startsWith("--")) tokenCache[which][name.slice(2)] = rule.style.getPropertyValue(name).trim();
          }
        }
      }
      tokenCache.dark = { ...tokenCache.light, ...tokenCache.dark };
    }
    return tokenCache[theme];
  }
  const siteTheme = () => document.documentElement.getAttribute("data-theme") || "light";

  function colourOf(group, theme) {
    if (custom[theme] && custom[theme][group]) return custom[theme][group];
    if (PRESETS[preset]) return PRESETS[preset][theme][group];
    return tokens(theme)["rel-" + group];
  }

  function contrast(a, b) {
    const lum = (h) => {
      const c = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255).map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
      return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
    };
    const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  }

  // ---------- the colours panel ----------
  function applyColours() {
    const theme = siteTheme();
    const box = $("sent");
    const changed = preset !== "Default" || Object.keys(custom[theme] || {}).length;
    GROUPS.forEach(([g]) => {
      if (changed) box.style.setProperty("--rel-" + g, colourOf(g, theme));
      else box.style.removeProperty("--rel-" + g);
    });
  }

  function buildPanel() {
    const presets = $("c-presets");
    presets.querySelectorAll("button").forEach((b) => b.remove());
    Object.keys(PRESETS).forEach((name) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = name;
      b.setAttribute("aria-pressed", name === preset && !hasCustom() ? "true" : "false");
      b.addEventListener("click", () => {
        preset = name;
        custom = { light: {}, dark: {} };
        save();
        refresh();
      });
      presets.append(b);
    });
    const box = $("c-swatches");
    box.replaceChildren();
    const theme = siteTheme();
    const ground = tokens(theme).card;
    GROUPS.forEach(([g, name]) => {
      const l = document.createElement("label");
      const i = document.createElement("input");
      i.type = "color";
      i.value = colourOf(g, theme).toLowerCase();
      i.dataset.group = g;
      i.setAttribute("aria-label", `Colour for ${name}`);
      const text = document.createElement("span");
      text.textContent = name;
      const warn = document.createElement("small");
      const check = () => {
        const c = contrast(i.value, ground);
        warn.textContent = c < 4.5 ? `Hard to read here (${c.toFixed(1)}:1)` : "";
      };
      check();
      i.addEventListener("input", () => {
        custom[theme] = { ...custom[theme], [g]: i.value };
        check();
        save();
        applyColours();
        $("c-presets").querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
      });
      text.append(warn);
      l.append(i, text);
      box.append(l);
    });
  }
  const hasCustom = () => Object.values(custom).some((c) => Object.keys(c || {}).length);

  function refresh() {
    applyColours();
    buildPanel();
    if ($("x-dialog").open) renderExport();
  }

  // ---------- the image ----------
  const IMG = {};
  function image(src) {
    if (!IMG[src]) {
      IMG[src] = new Promise((ok, no) => {
        const i = new Image();
        i.onload = () => ok(i);
        i.onerror = no;
        i.src = src;
      });
    }
    return IMG[src];
  }

  // Break text into lines no wider than max.
  function lines(c, text, max) {
    const out = [];
    let cur = "";
    text.split(/\s+/).forEach((word) => {
      const next = cur ? cur + " " + word : word;
      if (cur && c.measureText(next).width > max) { out.push(cur); cur = word; } else cur = next;
    });
    if (cur) out.push(cur);
    return out;
  }

  function text(c, s, x, y, font, fill, align) {
    c.font = font;
    c.fillStyle = fill;
    c.textAlign = align || "left";
    c.fillText(s, x, y);
  }

  function drawDiagram(c, g, palette, t) {
    const font = window.zkSentence.fontStack();
    const colour = (w) => palette[window.zkSentence.groupOf(w)];
    c.lineCap = "round";
    const label = (w, x, y) => {
      const s = window.zkSentence.label(w);
      c.font = `700 13px ${font}`;
      const lw = c.measureText(s).width + 10;
      c.fillStyle = t.background;
      c.fillRect(x - lw / 2, y - 9, lw, 18);
      text(c, s, x, y + 4.5, c.font, colour(w), "center");
    };
    g.arcs.forEach((a) => {
      const xd = g.px(a.id) + g.port[a.id + "d"];
      const xh = g.px(a.head) + g.port[a.id + "h"];
      const h = g.rise(g.level[a.id]);
      const y = g.y0 - 2;
      c.strokeStyle = colour(a);
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(xh, y);
      c.bezierCurveTo(xh, y - h * 1.33, xd, y - h * 1.33, xd, y - 7);
      c.stroke();
      c.fillStyle = colour(a);
      c.beginPath();
      c.moveTo(xd - 5, y - 8);
      c.lineTo(xd + 5, y - 8);
      c.lineTo(xd, y);
      c.fill();
    });
    // labels last, so no later arrow crosses them
    g.arcs.forEach((a) => {
      const xd = g.px(a.id) + g.port[a.id + "d"];
      const xh = g.px(a.head) + g.port[a.id + "h"];
      label(a, (xd + xh) / 2, g.y0 - 2 - g.rise(g.level[a.id]));
    });
    if (g.root) {
      const x = g.px(g.root.id);
      c.strokeStyle = colour(g.root);
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(x, 26);
      c.lineTo(x, g.y0 - 9);
      c.stroke();
      c.fillStyle = colour(g.root);
      c.beginPath();
      c.moveTo(x - 5, g.y0 - 10);
      c.lineTo(x + 5, g.y0 - 10);
      c.lineTo(x, g.y0 - 2);
      c.fill();
      label(g.root, Math.min(Math.max(x, 60), g.total - 60), 15);
    }
    g.toks.forEach((w) => {
      const x = g.px(w.id);
      text(c, w.text, x, g.y0 + 28, `700 20px ${font}`, colour(w), "center");
      text(c, w.pos_name, x, g.y0 + 47, `500 12px ${font}`, t["muted-foreground"], "center");
      if (w.segmentation !== w.text) text(c, w.segmentation, x, g.y0 + 66, `12px ${font}`, t["muted-foreground"], "center");
    });
  }

  // Draws the whole card on a canvas, or on the SVG recorder below. Returns the diagram's scale.
  function paintCard(c, W, H, theme, parsed, logo) {
    const t = tokens(theme);
    const font = window.zkSentence.fontStack();
    const palette = Object.fromEntries(GROUPS.map(([g]) => [g, colourOf(g, theme)]));
    c.textBaseline = "alphabetic";
    c.direction = "ltr";
    c.fillStyle = t.background;
    c.fillRect(0, 0, W, H);

    const short = Math.min(W, H);
    const unit = short / 630; // type scale: a 1200×630 card is the reference
    const pad = Math.round(48 * Math.max(unit, 0.9));
    const avail = W - pad * 2;

    // header: logo, name, what this is
    const logoSize = Math.round(58 * unit);
    const headY = pad * 0.75;
    c.drawImage(logo, pad, headY, logoSize, logoSize);
    const nameX = pad + logoSize + 12 * unit;
    text(c, "zimankit", nameX, headY + logoSize * 0.47, `700 ${Math.round(28 * unit)}px ${font}`, t.foreground);
    text(c, "Kurdish language toolkit", nameX, headY + logoSize * 0.88, `500 ${Math.round(15 * unit)}px ${font}`, t["muted-foreground"]);
    if (W > H * 0.9) {
      text(c, parsed.lang === "ckb" ? "Sorani · سۆرانی" : "Kurmanji · Kurmancî", W - pad, headY + logoSize * 0.62,
        `600 ${Math.round(17 * unit)}px ${font}`, t["muted-foreground"], "right");
    }
    const headEnd = headY + logoSize + 16 * unit;
    c.fillStyle = t.border;
    c.fillRect(pad, headEnd, avail, Math.max(1, unit));

    // footer: repository, site, flag band
    const bandH = Math.round(7 * unit);
    const footSize = Math.round(16 * unit);
    const stacked = W <= H; // not enough width for both links on one line in narrow formats
    const footH = (stacked ? footSize * 4.2 : footSize * 2.4); // room for the flag's sun under the centred links
    const footY = H - bandH - footH;
    c.fillStyle = t.border;
    c.fillRect(pad, footY, avail, Math.max(1, unit));
    const footFont = `600 ${footSize}px ${font}`;
    if (stacked) {
      text(c, REPO, W / 2, footY + footSize * 1.45, footFont, t.foreground, "center");
      text(c, SITE, W / 2, footY + footSize * 2.75, `500 ${footSize}px ${font}`, t["muted-foreground"], "center");
    } else {
      text(c, REPO, pad, footY + footSize * 1.55, footFont, t.foreground);
      text(c, SITE, W - pad, footY + footSize * 1.55, `500 ${footSize}px ${font}`, t["muted-foreground"], "right");
    }
    [["#ED2024", 0], [theme === "dark" ? "#FFFFFF" : "#E5E5E5", 1], ["#278E43", 2]].forEach(([col, i]) => {
      c.fillStyle = col;
      c.fillRect(i * W / 3, H - bandH, W / 3 + 1, bandH);
    });
    // the flag's sun, in the middle of the band, standing on the bottom edge
    const sunR = bandH * 1.5;
    const sunScale = sunR / 150;
    c.save();
    c.translate(W / 2 - 450 * sunScale, H - sunR - 300 * sunScale);
    c.scale(sunScale, sunScale);
    c.fillStyle = "#FEBD11";
    if (c instanceof SvgRecorder) c.fillPath(FLAG_SUN);
    else c.fill(new Path2D(FLAG_SUN));
    c.restore();

    // the sentence, then its translation
    let y = headEnd + 34 * unit;
    let size = Math.round(32 * unit);
    c.direction = parsed.lang === "ckb" ? "rtl" : "ltr";
    let parts;
    for (;;) { // shrink until the sentence fits on two lines (three on narrow formats)
      c.font = `700 ${size}px ${font}`;
      parts = lines(c, parsed.sentence, avail);
      if (parts.length <= (W <= H ? 3 : 2) || size <= 16) break;
      size -= 2;
    }
    parts.forEach((line) => {
      y += size * 1.3;
      text(c, line, W / 2, y, c.font, t.foreground, "center");
    });
    c.direction = "ltr";
    const gloss = $("x-trans").checked ? window.zkSentence.translation() : "";
    if (gloss) {
      const gf = `500 ${Math.round(17 * unit)}px ${font}`;
      c.font = gf;
      lines(c, gloss, avail).forEach((line) => {
        y += 17 * unit * 1.45;
        text(c, line, W / 2, y, gf, t["muted-foreground"], "center");
      });
    }

    // the colour key, above the footer
    const used = [];
    parsed.tokens.forEach((w) => {
      if (w.upos !== "PUNCT" && !used.some(([, n]) => n === w.relation)) used.push([window.zkSentence.groupOf(w), w.relation]);
    });
    const keyFont = `500 ${Math.round(14 * unit)}px ${font}`;
    c.font = keyFont;
    const dot = 5 * unit;
    const rows = [[]];
    let rowW = 0;
    used.forEach((u) => {
      const w = dot * 2 + 7 * unit + c.measureText(u[1]).width + 20 * unit;
      if (rowW + w > avail && rows[rows.length - 1].length) { rows.push([]); rowW = 0; }
      rows[rows.length - 1].push([...u, w]);
      rowW += w;
    });
    const rowH = 24 * unit;
    const keyTop = footY - 14 * unit - rows.length * rowH;
    rows.forEach((row, i) => {
      const rw = row.reduce((sum, r) => sum + r[2], 0) - 20 * unit;
      let x = (W - rw) / 2;
      const ry = keyTop + rowH * (i + 0.7);
      row.forEach(([group, name, w]) => {
        c.fillStyle = palette[group];
        c.beginPath();
        c.arc(x + dot, ry - dot * 0.75, dot, 0, Math.PI * 2);
        c.fill();
        text(c, name, x + dot * 2 + 7 * unit, ry, keyFont, t.foreground);
        x += w;
      });
    });

    // the diagram fills what is left, centred
    const top = y + 18 * unit;
    const room = keyTop - 12 * unit - top;
    const narrow = W <= H;
    let g = window.zkSentence.geometry({ gap: narrow ? 10 : 26 });
    let scale = Math.min(avail / g.total, room / g.height, 2.6);
    if (g.maxLevel && room / scale > g.height) { // tall formats: raise the arrows to use the height
      const extra = (room * 0.86 / scale - g.height) / g.maxLevel;
      g = window.zkSentence.geometry({ gap: narrow ? 10 : 26, step: 36 + Math.min(Math.max(extra, 0), 70) });
      scale = Math.min(avail / g.total, room / g.height, 2.6);
    }
    c.save();
    c.translate((W - g.total * scale) / 2, top + (room - g.height * scale) / 2);
    c.scale(scale, scale);
    drawDiagram(c, g, palette, t);
    c.restore();

    return scale;
  }

  const logoPath = (theme) => (theme === "dark" ? "brand/logo/svg/zimankit-mark-on-dark.svg" : "brand/logo/svg/zimankit-mark.svg");
  const pixels = () => $("x-size").value.split("x").map(Number);

  let renderId = 0;
  async function renderExport() {
    const parsed = window.zkSentence.current();
    if (!parsed || !parsed.tokens.length) return;
    const id = ++renderId;
    const [W, H] = pixels();
    const k = +$("x-quality").value;
    const theme = $("x-theme").value;
    const font = window.zkSentence.fontStack();
    const logo = await image(logoPath(theme));
    if (document.fonts) await Promise.all(["400", "500", "600", "700"].map((w) => document.fonts.load(`${w} 20px ${font}`, "کa")));
    if (id !== renderId) return; // a newer render has started

    const canvas = $("x-canvas");
    canvas.width = W * k;
    canvas.height = H * k;
    const c = canvas.getContext("2d");
    c.setTransform(k, 0, 0, k, 0, 0);
    const scale = paintCard(c, W, H, theme, parsed, logo);

    const format = $("x-format").value;
    $("x-quality").disabled = format === "svg";
    $("x-label").textContent = `Download ${format.toUpperCase()}`;
    $("x-trans-row").hidden = !window.zkSentence.translation();
    const size = { svg: "Vector, with its fonts inside.", pdf: `${W * k} × ${H * k} pixel image on one page.` }[format] || `${W * k} × ${H * k} pixels at ${72 * k} dpi.`;
    $("x-note").textContent = (scale < 0.75 ? "This sentence is long for this size, so its text is small. Landscape fits it better. " : "") + size;
  }

  // ---------- SVG: records the same drawing calls as elements ----------
  const xml = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const num = (n) => +n.toFixed(4);

  class SvgRecorder {
    constructor() {
      this.out = [];
      this.stack = [];
      this.m = [1, 1, 0, 0]; // scale x, scale y, translate x, translate y
      this.path = "";
      this.measure = document.createElement("canvas").getContext("2d");
      this.font = "16px sans-serif";
      this.fillStyle = "#000";
      this.strokeStyle = "#000";
      this.lineWidth = 1;
      this.textAlign = "left";
      this.direction = "ltr";
    }
    get transform() {
      const [a, d, e, f] = this.m;
      return a === 1 && d === 1 && e === 0 && f === 0 ? "" : ` transform="matrix(${num(a)} 0 0 ${num(d)} ${num(e)} ${num(f)})"`;
    }
    save() { this.stack.push([...this.m]); }
    restore() { this.m = this.stack.pop(); }
    translate(x, y) { this.m[2] += x * this.m[0]; this.m[3] += y * this.m[1]; }
    scale(x, y) { this.m[0] *= x; this.m[1] *= y; }
    setTransform() {}
    measureText(text) { this.measure.font = this.font; return this.measure.measureText(text); }
    beginPath() { this.path = ""; }
    moveTo(x, y) { this.path += `M${num(x)} ${num(y)}`; }
    lineTo(x, y) { this.path += `L${num(x)} ${num(y)}`; }
    bezierCurveTo(a, b, c, d, e, f) { this.path += `C${num(a)} ${num(b)} ${num(c)} ${num(d)} ${num(e)} ${num(f)}`; }
    arc(x, y, r) { this.path += `M${num(x - r)} ${num(y)}A${num(r)} ${num(r)} 0 1 0 ${num(x + r)} ${num(y)}A${num(r)} ${num(r)} 0 1 0 ${num(x - r)} ${num(y)}Z`; }
    fill() { this.out.push(`<path d="${this.path}Z" fill="${this.fillStyle}"${this.transform}/>`); }
    stroke() { this.out.push(`<path d="${this.path}" fill="none" stroke="${this.strokeStyle}" stroke-width="${this.lineWidth}" stroke-linecap="round"${this.transform}/>`); }
    fillPath(d) { this.out.push(`<path d="${d}" fill="${this.fillStyle}"${this.transform}/>`); }
    fillRect(x, y, w, h) { this.out.push(`<rect x="${num(x)}" y="${num(y)}" width="${num(w)}" height="${num(h)}" fill="${this.fillStyle}"${this.transform}/>`); }
    drawImage(img, x, y, w, h) { this.out.push(`<image href="${img.href}" x="${num(x)}" y="${num(y)}" width="${num(w)}" height="${num(h)}"${this.transform}/>`); }
    fillText(text, x, y) {
      const m = this.font.match(/^(?:(\d+)\s+)?([\d.]+)px\s+(.*)$/);
      const anchor = { left: "start", right: "end", center: "middle" }[this.textAlign];
      this.out.push(`<text x="${num(x)}" y="${num(y)}" font-family='${m[3]}' font-size="${m[2]}" font-weight="${m[1] || 400}" fill="${this.fillStyle}" text-anchor="${anchor}" direction="${this.direction}"${this.transform}>${xml(text)}</text>`);
    }
  }

  async function dataUri(url, type) {
    const bytes = new Uint8Array(await (await fetch(url)).arrayBuffer());
    let bin = "";
    bytes.forEach((b) => { bin += String.fromCharCode(b); });
    return `data:${type};base64,${btoa(bin)}`;
  }

  // Fonts go inside the file, so it looks the same when it is opened elsewhere.
  async function embeddedFonts(rtl) {
    const faces = {
      Sahel: [["Sahel.woff2", 400], ["Sahel-Bold.woff2", 700]],
      Estedad: [["Estedad-arabic.woff2", "100 900"]],
      Vazirmatn: [["Vazirmatn-arabic.woff2", "100 900"]],
    }[rtl] || [];
    const list = [["Manrope", "Manrope-latin.woff2", "200 800"], ["Manrope", "Manrope-latin-ext.woff2", "200 800"], ...faces.map(([f, w]) => [rtl, f, w])];
    const css = await Promise.all(list.map(async ([family, file, weight]) => {
      const uri = await dataUri(`fonts/${file}`, "font/woff2");
      return `@font-face{font-family:"${family}";font-weight:${weight};src:url(${uri}) format("woff2")}`;
    }));
    return css.join("");
  }

  async function svgFile() {
    const [W, H] = pixels();
    const theme = $("x-theme").value;
    const parsed = window.zkSentence.current();
    const rec = new SvgRecorder();
    paintCard(rec, W, H, theme, parsed, { href: await dataUri(logoPath(theme), "image/svg+xml") });
    const rtl = getComputedStyle(document.documentElement).getPropertyValue("--rtl-font").replace(/"/g, "").trim();
    const fonts = await embeddedFonts(rtl);
    const body = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><title>${xml(parsed.sentence)}</title><style>${fonts}</style>${rec.out.join("")}</svg>\n`;
    return new Blob([body], { type: "image/svg+xml" });
  }

  // ---------- saving ----------
  function crc32(bytes) {
    let c = 0xffffffff;
    for (let i = 0; i < bytes.length; i++) {
      c ^= bytes[i];
      for (let k = 0; k < 8; k++) c = c & 1 ? (c >>> 1) ^ 0xedb88320 : c >>> 1;
    }
    return (c ^ 0xffffffff) >>> 0;
  }

  // Canvas PNGs carry no resolution, so add a pHYs chunk after IHDR.
  async function withDpi(blob, dpi) {
    const src = new Uint8Array(await blob.arrayBuffer());
    const ppm = Math.round(dpi / 0.0254);
    const chunk = new Uint8Array(21);
    const v = new DataView(chunk.buffer);
    v.setUint32(0, 9);
    chunk.set([0x70, 0x48, 0x59, 0x73], 4); // "pHYs"
    v.setUint32(8, ppm);
    v.setUint32(12, ppm);
    chunk[16] = 1; // metres
    v.setUint32(17, crc32(chunk.subarray(4, 17)));
    const at = 8 + 25; // signature + IHDR
    const out = new Uint8Array(src.length + chunk.length);
    out.set(src.subarray(0, at), 0);
    out.set(chunk, at);
    out.set(src.subarray(at), at + chunk.length);
    return new Blob([out], { type: "image/png" });
  }

  // JPEG resolution lives in the JFIF header.
  async function jpegWithDpi(blob, dpi) {
    const b = new Uint8Array(await blob.arrayBuffer());
    if (b[6] === 0x4a && b[7] === 0x46) { // "JF"
      b[13] = 1; // dots per inch
      b[14] = dpi >> 8; b[15] = dpi & 255;
      b[16] = dpi >> 8; b[17] = dpi & 255;
    }
    return new Blob([b], { type: "image/jpeg" });
  }

  // A one-page PDF holding the JPEG; 1 px of the size chosen is 1 pt on the page.
  function pdfWithJpeg(jpeg, pxW, pxH, W, H) {
    const enc = new TextEncoder();
    const parts = [];
    const offsets = [];
    let length = 0;
    const push = (p) => { const b = typeof p === "string" ? enc.encode(p) : p; parts.push(b); length += b.length; };
    const object = (n, head, stream) => {
      offsets[n] = length;
      push(`${n} 0 obj\n${head}\n`);
      if (stream) { push(`stream\n`); push(stream); push(`\nendstream\n`); }
      push(`endobj\n`);
    };
    push("%PDF-1.4\n");
    const content = `q ${W} 0 0 ${H} 0 0 cm /Im0 Do Q`;
    object(1, "<< /Type /Catalog /Pages 2 0 R >>");
    object(2, "<< /Type /Pages /Kids [3 0 R] /Count 1 >>");
    object(3, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>`);
    object(4, `<< /Length ${content.length} >>`, enc.encode(content));
    object(5, `<< /Type /XObject /Subtype /Image /Width ${pxW} /Height ${pxH} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>`, jpeg);
    const start = length;
    push(`xref\n0 6\n0000000000 65535 f \n${offsets.slice(1).map((o) => String(o).padStart(10, "0") + " 00000 n \n").join("")}`);
    push(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${start}\n%%EOF\n`);
    return new Blob(parts, { type: "application/pdf" });
  }

  async function makeFile() {
    await renderExport();
    const canvas = $("x-canvas");
    const k = +$("x-quality").value;
    const [W, H] = pixels();
    const format = $("x-format").value;
    const blobOf = (type, q) => new Promise((ok) => canvas.toBlob(ok, type, q));
    let blob;
    if (format === "png") blob = await withDpi(await blobOf("image/png"), 72 * k);
    if (format === "jpg") blob = await jpegWithDpi(await blobOf("image/jpeg", 0.95), 72 * k);
    if (format === "pdf") blob = pdfWithJpeg(new Uint8Array(await (await blobOf("image/jpeg", 0.95)).arrayBuffer()), W * k, H * k, W, H);
    if (format === "svg") blob = await svgFile();
    const suffix = format === "svg" ? "" : `@${k}x`;
    return new File([blob], `zimankit-sentence-${W}x${H}${suffix}.${format}`, { type: blob.type });
  }

  function init() {
    $("c-toggle").addEventListener("click", () => {
      const open = $("c-panel").hidden;
      $("c-panel").hidden = !open;
      $("c-toggle").setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("zk-theme", refresh);
    document.addEventListener("zk-parsed", () => {
      const p = window.zkSentence.current();
      $("x-open").disabled = !(p && p.tokens.length);
    });
    document.addEventListener("zk-font", () => { if ($("x-dialog").open) renderExport(); });
    $("x-open").addEventListener("click", () => {
      $("x-theme").value = siteTheme();
      $("x-dialog").showModal();
      renderExport();
    });
    $("x-close").addEventListener("click", () => $("x-dialog").close());
    $("x-dialog").addEventListener("click", (e) => { if (e.target === $("x-dialog")) $("x-dialog").close(); });
    ["x-format", "x-size", "x-theme", "x-quality", "x-trans"].forEach((id) => $(id).addEventListener("change", renderExport));
    $("x-download").addEventListener("click", async () => {
      const file = await makeFile();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(file);
      a.download = file.name;
      document.body.append(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    });
    const probe = new File([new Blob(["x"], { type: "image/png" })], "x.png", { type: "image/png" });
    if (navigator.canShare && navigator.canShare({ files: [probe] })) {
      $("x-share").hidden = false;
      $("x-share").addEventListener("click", async () => {
        try {
          await navigator.share({ files: [await makeFile()], title: "zimankit", text: `Kurdish sentence structure: https://${SITE}/` });
        } catch (e) { /* the reader closed the share sheet */ }
      });
    }
    refresh();
  }

  window.zkTools = { init };
})();
