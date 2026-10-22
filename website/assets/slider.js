/* Home banner slideshow: autoplay with pause/play, prev/next, dots, arrow keys, swipe.
   Without JS the first slide is simply shown. Slides only cross-fade (nothing moves), so it also
   auto-advances for visitors who prefer reduced motion, a bit slower; the pause button stops it. */
(() => {
  const root = document.querySelector("[data-slider]");
  if (!root) return;
  const slides = [...root.querySelectorAll(".slide")];
  if (slides.length < 2) return;

  const controls = root.querySelector("[data-controls]");
  const dotsBox = root.querySelector("[data-dots]");
  const toggleBtn = root.querySelector("[data-toggle]");
  const live = root.querySelector("[data-slides]");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const interval = () => (reduce.matches ? 8000 : 6000);

  let index = 0;
  let timer = null;
  let userPaused = false;
  let hovering = false;
  let focusing = false;

  // Load the later slides only after the page has loaded, so the first image stays fast.
  const loadLater = () => {
    root.querySelectorAll("[data-src],[data-srcset]").forEach((el) => {
      if (el.dataset.srcset) el.srcset = el.dataset.srcset;
      if (el.dataset.src) el.src = el.dataset.src;
    });
  };
  if (document.readyState === "complete") loadLater();
  else window.addEventListener("load", loadLater, { once: true });

  const dots = slides.map((_, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "slider-dot";
    b.setAttribute("aria-label", `ไปที่ภาพที่ ${i + 1}`);
    b.addEventListener("click", () => go(i, true));
    dotsBox.appendChild(b);
    return b;
  });

  function go(i, reschedule) {
    index = (i + slides.length) % slides.length;
    slides.forEach((s, n) => {
      const on = n === index;
      s.classList.toggle("is-active", on);
      s.setAttribute("aria-hidden", on ? "false" : "true");
      s.inert = !on;
    });
    dots.forEach((d, n) => {
      if (n === index) d.setAttribute("aria-current", "true");
      else d.removeAttribute("aria-current");
    });
    if (reschedule) restart(); // re-arms the autoplay timer (used by buttons, keys and the timer itself)
  }

  const playing = () => !userPaused && !hovering && !focusing && !document.hidden;
  function restart() {
    clearTimeout(timer);
    if (playing()) timer = setTimeout(() => go(index + 1, true), interval());
    live.setAttribute("aria-live", playing() ? "off" : "polite");
  }

  function setPaused(p) {
    userPaused = p;
    root.classList.toggle("is-paused", p);
    toggleBtn.setAttribute("aria-label", p ? "เริ่มเลื่อนอัตโนมัติ" : "หยุดเลื่อนอัตโนมัติ");
    restart();
  }

  root.querySelector("[data-prev]").addEventListener("click", () => go(index - 1, true));
  root.querySelector("[data-next]").addEventListener("click", () => go(index + 1, true));
  toggleBtn.addEventListener("click", () => setPaused(!userPaused));

  root.addEventListener("mouseenter", () => { hovering = true; restart(); });
  root.addEventListener("mouseleave", () => { hovering = false; restart(); });
  root.addEventListener("focusin", () => { focusing = true; restart(); });
  root.addEventListener("focusout", (e) => {
    if (!root.contains(e.relatedTarget)) { focusing = false; restart(); }
  });
  document.addEventListener("visibilitychange", restart);

  root.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") { go(index - 1, true); e.preventDefault(); }
    else if (e.key === "ArrowRight") { go(index + 1, true); e.preventDefault(); }
  });

  // Swipe (touch / pen): horizontal move of 40px+ that is clearly more horizontal than vertical.
  let sx = 0, sy = 0, tracking = false;
  live.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse") return;
    tracking = true; sx = e.clientX; sy = e.clientY;
  });
  live.addEventListener("pointerup", (e) => {
    if (!tracking) return;
    tracking = false;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.5) go(index + (dx < 0 ? 1 : -1), true);
  });
  live.addEventListener("pointercancel", () => { tracking = false; });

  controls.hidden = false;
  root.classList.add("js-ready");
  root.classList.toggle("is-paused", userPaused);
  toggleBtn.setAttribute("aria-label", userPaused ? "เริ่มเลื่อนอัตโนมัติ" : "หยุดเลื่อนอัตโนมัติ");
  go(0);
  restart();
})();
