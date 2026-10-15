/* Interactive effects: 3D tilt character cards, character dialog, hero tilt, scroll reveal. */
(function () {
  "use strict";

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  // Pointer-driven tilt: sets --rx/--ry (and glare --gx/--gy) on el.
  const tilt = (el, max = 14) => {
    if (reduced) return;
    let raf = 0;
    const move = (e) => {
      const r = el.getBoundingClientRect();
      const px = clamp((e.clientX - r.left) / r.width, 0, 1);
      const py = clamp((e.clientY - r.top) / r.height, 0, 1);
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty("--ry", `${(px - 0.5) * 2 * max}deg`);
        el.style.setProperty("--rx", `${(0.5 - py) * 2 * max}deg`);
        el.style.setProperty("--gx", `${px * 100}%`);
        el.style.setProperty("--gy", `${py * 100}%`);
        el.classList.add("is-tilting");
      });
    };
    const reset = () => {
      cancelAnimationFrame(raf);
      el.style.setProperty("--rx", "0deg");
      el.style.setProperty("--ry", "0deg");
      el.classList.remove("is-tilting");
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", reset);
    el.addEventListener("pointercancel", reset);
    el.addEventListener("pointerup", (e) => { if (e.pointerType !== "mouse") reset(); });
  };

  // ---- Character gallery ----
  const chars = Array.isArray(window.RAMAKIEN_CHARS) ? window.RAMAKIEN_CHARS : [];
  const grid = document.querySelector("[data-chars]");
  const dialog = document.querySelector("[data-char-dialog]");
  const SIDE = { rama: "ฝ่ายพระราม", lanka: "ฝ่ายกรุงลงกา" };
  const src = (slug) => `assets/img/chars/${slug}.svg`;

  const openChar = (c, opener) => {
    if (!dialog) return;
    const img = dialog.querySelector("[data-char-img]");
    img.src = src(c.slug);
    img.alt = `${c.name} ตัวละครการ์ตูนจากรามเกียรติ์`;
    dialog.querySelector("[data-char-side]").textContent = SIDE[c.side] || "";
    dialog.querySelector("[data-char-name]").textContent = c.name;
    dialog.querySelector("[data-char-role]").textContent = c.role;
    dialog.querySelector("[data-char-blurb]").textContent = c.blurb;
    dialog._opener = opener;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
  };

  if (grid && chars.length) {
    const frag = document.createDocumentFragment();
    chars.forEach((c, i) => {
      const li = document.createElement("li");
      li.dataset.side = c.side;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "char-card";
      btn.dataset.side = c.side;
      btn.style.setProperty("--d", `${(i % 6) * -0.7}s`);
      btn.setAttribute("aria-label", `${c.name}, ${c.role}. เปิดดูเรื่องราว`);
      const img = document.createElement("img");
      img.src = src(c.slug);
      img.alt = "";
      img.width = 184;
      img.height = 296;
      img.loading = "lazy";
      img.decoding = "async";
      const name = document.createElement("span");
      name.className = "char-name";
      name.textContent = c.name;
      const role = document.createElement("span");
      role.className = "char-role";
      role.textContent = c.role;
      const fig = document.createElement("span");
      fig.className = "char-fig";
      fig.append(img);
      btn.append(fig, name, role);
      btn.addEventListener("click", () => openChar(c, btn));
      tilt(btn);
      li.append(btn);
      frag.append(li);
    });
    grid.append(frag);

    const filters = document.querySelector("[data-char-filters]");
    filters?.addEventListener("click", (e) => {
      const b = e.target.closest("[data-side]");
      if (!b) return;
      const side = b.dataset.side;
      filters.querySelectorAll("[data-side]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      grid.querySelectorAll("li").forEach((li) => { li.hidden = side !== "all" && li.dataset.side !== side; });
    });
  }

  if (dialog) {
    const stage = dialog.querySelector("[data-tilt]");
    if (stage) tilt(stage, 22);
    dialog.querySelector("[data-char-close]")?.addEventListener("click", () => dialog.close());
    // Click on the backdrop closes the dialog.
    dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => dialog._opener?.focus());
  }

  // ---- Hero art follows the pointer ----
  const hero = document.querySelector(".hero");
  const heroArt = document.querySelector(".hero-art");
  if (hero && heroArt && !reduced) {
    hero.addEventListener("pointermove", (e) => {
      if (e.pointerType !== "mouse") return;
      const r = hero.getBoundingClientRect();
      heroArt.style.setProperty("--ry", `${((e.clientX - r.left) / r.width - 0.5) * 12}deg`);
      heroArt.style.setProperty("--rx", `${(0.5 - (e.clientY - r.top) / r.height) * 10}deg`);
    });
    hero.addEventListener("pointerleave", () => {
      heroArt.style.setProperty("--rx", "0deg");
      heroArt.style.setProperty("--ry", "0deg");
    });
  }

  // ---- Reveal sections on scroll ----
  if (!reduced && "IntersectionObserver" in window) {
    const targets = document.querySelectorAll(".section .section-head, .char-grid li, .card, .step, .plan");
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          en.target.classList.add("is-in");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    targets.forEach((t) => {
      const r = t.getBoundingClientRect();
      if (r.top < window.innerHeight) return; // already visible: never hide it
      t.classList.add("reveal");
      io.observe(t);
    });
  }
})();

/* Battle scene: tap a fighter to jump, cheer buttons fire a special move and move the tug bar. */
(function () {
  "use strict";
  const battle = document.querySelector("[data-battle]");
  if (!battle) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tug = battle.querySelector("[data-tug]");
  const score = battle.querySelector("[data-battle-score]");
  const LABEL = { rama: "ฝ่ายพระราม", lanka: "ฝ่ายลงกา" };
  const pts = { rama: 0, lanka: 0 };
  let timer = 0;

  battle.querySelectorAll("[data-fighter]").forEach((f) => {
    f.addEventListener("click", () => {
      if (reduced) return;
      f.classList.remove("is-jumping");
      void f.offsetWidth; // restart the animation on repeated taps
      f.classList.add("is-jumping");
    });
    f.addEventListener("animationend", (e) => { if (e.animationName === "f-jump") f.classList.remove("is-jumping"); });
  });

  battle.querySelectorAll("[data-cheer]").forEach((b) => {
    b.addEventListener("click", () => {
      const side = b.dataset.cheer;
      pts[side] += 1;
      const total = pts.rama + pts.lanka;
      // Keep the bar between 10% and 90% so both sides stay visible.
      const p = Math.min(90, Math.max(10, 50 + ((pts.rama - pts.lanka) / Math.max(total, 1)) * 40));
      tug?.style.setProperty("--p", `${p}%`);
      const diff = Math.abs(pts.rama - pts.lanka);
      const lead = pts.rama === pts.lanka ? null : pts.rama > pts.lanka ? "rama" : "lanka";
      if (score) score.textContent = lead ? `${LABEL[lead]}นำอยู่ ${diff} แต้ม (พระราม ${pts.rama} : ลงกา ${pts.lanka})` : `เสมอกัน ${pts.rama} : ${pts.lanka}`;
      if (reduced) return;
      battle.classList.remove("special-rama", "special-lanka");
      void battle.offsetWidth;
      battle.classList.add(`special-${side}`);
      clearTimeout(timer);
      timer = setTimeout(() => battle.classList.remove("special-rama", "special-lanka"), 1500);
    });
  });
})();
