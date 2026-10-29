// Theme (system / light / dark) and the mobile menu. Shared by every page.
(function () {
  const root = document.documentElement;
  const order = ["system", "light", "dark"];
  let theme = "system";
  try { theme = localStorage.getItem("zimankit-theme") || "system"; } catch (e) { /* storage blocked */ }

  function apply(t) {
    theme = t;
    if (t === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", t);
    const b = document.querySelector(".theme");
    if (b) b.textContent = "Theme: " + t;
  }
  apply(theme);

  document.addEventListener("DOMContentLoaded", function () {
    apply(theme);
    const b = document.querySelector(".theme");
    if (b) b.addEventListener("click", function () {
      const next = order[(order.indexOf(theme) + 1) % order.length];
      apply(next);
      try { localStorage.setItem("zimankit-theme", next); } catch (e) { /* storage blocked */ }
    });
    const m = document.querySelector(".menu");
    const nav = document.querySelector(".nav");
    if (m && nav) m.addEventListener("click", function () {
      const open = nav.classList.toggle("open");
      m.setAttribute("aria-expanded", open ? "true" : "false");
    });
    const here = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach(function (a) {
      if (a.getAttribute("href") === here) a.setAttribute("aria-current", "page");
    });
  });
})();
