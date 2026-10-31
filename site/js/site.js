// Shared by every page: theme, mobile menu, copy buttons, table of contents.
(function () {
  const root = document.documentElement;
  const order = ["light", "dark", "system"];
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  let theme = "light";
  try { theme = localStorage.getItem("zimankit-theme") || "light"; } catch (e) { /* storage blocked */ }

  function apply() {
    const dark = theme === "dark" || (theme === "system" && media.matches);
    root.setAttribute("data-theme", dark ? "dark" : "light");
    const b = document.querySelector(".theme");
    if (!b) return;
    b.setAttribute("aria-label", "Theme: " + theme + ". Change theme");
    b.title = "Theme: " + theme;
    b.querySelectorAll("[data-t]").forEach((i) => i.toggleAttribute("hidden", i.dataset.t !== theme)); // SVG has no .hidden
  }
  apply();
  media.addEventListener("change", () => { apply(); document.dispatchEvent(new Event("zk-theme")); });

  // The font for Kurdish text in the Arabic-based script.
  const FONTS = ["Sahel", "Estedad", "Vazirmatn"];
  let rtlFont = "Sahel";
  try { rtlFont = localStorage.getItem("zimankit-rtl-font") || "Sahel"; } catch (e) { /* storage blocked */ }
  if (!FONTS.includes(rtlFont)) rtlFont = "Sahel";
  function applyFont() {
    root.style.setProperty("--rtl-font", `"${rtlFont}"`);
    document.querySelectorAll("select.rtl-font").forEach((s) => { s.value = rtlFont; });
  }
  applyFont();

  function theIcon(id) {
    const t = document.getElementById(id);
    return t ? t.innerHTML : "";
  }

  function copyText(pre) {
    // A transcript with $ prompts: copy only the commands.
    if (pre.querySelector(".p")) {
      return pre.textContent.split("\n").filter((l) => l.startsWith("$ ")).map((l) => l.slice(2)).join("\n");
    }
    return pre.textContent;
  }

  function addCopyButtons() {
    document.querySelectorAll("pre:not(.out)").forEach((pre) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "copy";
      b.setAttribute("aria-label", "Copy");
      b.title = "Copy";
      b.innerHTML = theIcon("i-copy");
      b.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(copyText(pre).trim());
          b.innerHTML = theIcon("i-check");
          b.classList.add("done");
          b.setAttribute("aria-label", "Copied");
          setTimeout(() => {
            b.innerHTML = theIcon("i-copy");
            b.classList.remove("done");
            b.setAttribute("aria-label", "Copy");
          }, 1500);
        } catch (e) { b.setAttribute("aria-label", "Could not copy"); }
      });
      pre.classList.add("has-copy");
      pre.append(b);
    });
  }

  function tableOfContents() {
    const toc = document.querySelector("details.toc");
    if (!toc) return;
    const wide = window.matchMedia("(min-width: 901px)");
    const sync = () => { toc.open = wide.matches; };
    sync();
    wide.addEventListener("change", sync);
    const links = [...toc.querySelectorAll("a")];
    links.forEach((a) => a.addEventListener("click", () => { if (!wide.matches) toc.open = false; }));
    if (!("IntersectionObserver" in window)) return;
    const seen = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
      });
    }, { rootMargin: "-15% 0px -75% 0px" });
    links.forEach((a) => {
      const target = document.getElementById(a.getAttribute("href").slice(1));
      if (target) seen.observe(target);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    apply();
    const b = document.querySelector(".theme");
    if (b) b.addEventListener("click", () => {
      theme = order[(order.indexOf(theme) + 1) % order.length];
      apply();
      try { localStorage.setItem("zimankit-theme", theme); } catch (e) { /* storage blocked */ }
      document.dispatchEvent(new Event("zk-theme"));
    });

    applyFont();
    document.querySelectorAll("select.rtl-font").forEach((sel) => sel.addEventListener("change", async () => {
      rtlFont = sel.value;
      try { localStorage.setItem("zimankit-rtl-font", rtlFont); } catch (e) { /* storage blocked */ }
      applyFont();
      if (document.fonts) await Promise.all(["400 16px", "700 16px"].map((f) => document.fonts.load(`${f} "${rtlFont}"`, "ک")));
      document.dispatchEvent(new Event("zk-font"));
    }));

    const m = document.querySelector(".menu");
    const nav = document.querySelector(".nav");
    if (m && nav) {
      const set = (open) => {
        nav.classList.toggle("open", open);
        m.setAttribute("aria-expanded", open ? "true" : "false");
        m.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        m.querySelectorAll("[data-m]").forEach((i) => i.toggleAttribute("hidden", (i.dataset.m === "x") !== open));
      };
      m.addEventListener("click", () => set(!nav.classList.contains("open")));
      nav.addEventListener("click", (e) => { if (e.target.closest("a")) set(false); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("open")) { set(false); m.focus(); } });
      document.addEventListener("click", (e) => { if (!e.target.closest(".top")) set(false); });
    }

    const here = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach((a) => {
      if (a.getAttribute("href") === here) a.setAttribute("aria-current", "page");
    });
    addCopyButtons();
    tableOfContents();
  });
})();
