(() => {
  "use strict";

  const cfg = window.SITE_CONFIG;
  if (!cfg) return;

  const STATUS_LABELS = {
    online: "เซิร์ฟเวอร์ออนไลน์",
    offline: "ปิดปรับปรุงชั่วคราว",
    soon: "เปิดให้บริการเร็ว ๆ นี้",
  };

  const PLACEHOLDER_EMAIL = /@example\.(com|org|net)$/i;
  const isPlaceholder = (href) => !href || href === "#" || PLACEHOLDER_EMAIL.test(href);

  // Toast: one shared live region so screen readers announce feedback too.
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");
  document.body.appendChild(toast);
  let toastTimer;
  const showToast = (msg) => {
    toast.textContent = msg;
    toast.dataset.show = "true";
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => (toast.dataset.show = "false"), 3500);
  };
  const PENDING_MSG = {
    clientDownload: "ตัวเกมจะเปิดให้ดาวน์โหลดเมื่อเซิร์ฟเวอร์พร้อม ติดตามประกาศได้เร็ว ๆ นี้",
    setupGuide: "คู่มือการติดตั้งจะเผยแพร่พร้อมไฟล์ตัวเกม",
    register: "ระบบสมัครไอดีจะเปิดเมื่อเซิร์ฟเวอร์พร้อม",
  };
  const DEFAULT_PENDING = "ช่องทางนี้จะเปิดเร็ว ๆ นี้";

  // Text bindings: <span data-config="serverName">
  document.querySelectorAll("[data-config]").forEach((el) => {
    const value = cfg[el.dataset.config];
    if (value !== undefined) el.textContent = String(value);
  });

  // Link bindings: <a data-link="discord">. Contact channels that are not set yet are hidden
  // (no dead buttons); other unset links stay visible but explain themselves on click.
  const CONTACT_KEYS = new Set(["discord", "line", "facebook", "email"]);
  document.querySelectorAll("[data-link]").forEach((el) => {
    const key = el.dataset.link;
    const href = key === "email" ? `mailto:${cfg.links.email}` : cfg.links[key];
    const raw = key === "email" ? cfg.links.email : cfg.links[key];
    if (isPlaceholder(raw) && CONTACT_KEYS.has(key)) {
      (el.closest(".contact-list > li") || el).hidden = true;
      return;
    }
    if (isPlaceholder(raw)) {
      // Keep the element focusable and give feedback instead of a silent dead click.
      el.dataset.pending = "true";
      el.removeAttribute("href");
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");
      const msg = PENDING_MSG[key] || DEFAULT_PENDING;
      const notify = (e) => {
        e.preventDefault();
        showToast(msg);
      };
      el.addEventListener("click", notify);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") notify(e);
      });
      return;
    }
    el.href = href;
    if (/^https?:/i.test(href)) {
      el.target = "_blank";
      el.rel = "noopener noreferrer";
    }
  });

  const emailText = isPlaceholder(cfg.links.email) ? "เร็ว ๆ นี้" : cfg.links.email;
  document.querySelectorAll("[data-email]").forEach((el) => (el.textContent = emailText));

  // If no contact channel is set yet, say so instead of showing an empty list.
  document.querySelectorAll(".contact-list").forEach((list) => {
    const anyShown = [...list.children].some((li) => !li.hidden);
    list.hidden = !anyShown;
    const empty = list.parentElement.querySelector("[data-contact-empty]");
    if (empty) empty.hidden = anyShown;
  });

  // Server status badge (the live stats below may override it once the server is open)
  const configStatus = STATUS_LABELS[cfg.serverStatus] ? cfg.serverStatus : "soon";
  const setStatus = (state) => {
    document.querySelectorAll("[data-status]").forEach((el) => {
      el.dataset.state = state;
      el.querySelector("[data-status-text]").textContent = STATUS_LABELS[state];
    });
  };
  setStatus(configStatus);

  // Copy server address
  const address = `${cfg.serverAddress}:${cfg.serverPort}`;
  document.querySelectorAll("[data-address]").forEach((el) => (el.textContent = address));
  const copyBtn = document.querySelector("[data-copy-address]");
  const copyMsg = document.querySelector("[data-copy-msg]");
  copyBtn?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(address);
      copyMsg.textContent = "คัดลอกแล้ว";
    } catch {
      copyMsg.textContent = `คัดลอกไม่สำเร็จ กรุณาคัดลอกเอง: ${address}`;
    }
    window.clearTimeout(copyBtn._t);
    copyBtn._t = window.setTimeout(() => (copyMsg.textContent = ""), 3000);
  });

  // Mobile navigation
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.getElementById("site-nav");
  const setOpen = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    nav.dataset.open = String(open);
  };
  toggle?.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
  nav?.addEventListener("click", (e) => {
    if (e.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && toggle?.getAttribute("aria-expanded") === "true") {
      setOpen(false);
      toggle.focus();
    }
  });

  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  // Players online: config fallback, replaced by the live count when the stats API answers
  const setOnline = (n) => {
    const text = Number.isFinite(n) ? n.toLocaleString("th-TH") : "—";
    document.querySelectorAll("[data-online]").forEach((el) => (el.textContent = text));
  };
  setOnline(cfg.onlinePlayers);

  // Thai-time clock (game events are announced in Thai time)
  const clockEls = document.querySelectorAll("[data-clock]");
  if (clockEls.length) {
    const fmt = new Intl.DateTimeFormat("th-TH", {
      timeZone: "Asia/Bangkok", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
    });
    const tick = () => {
      const now = new Date();
      clockEls.forEach((el) => {
        el.textContent = fmt.format(now);
        el.dateTime = now.toISOString();
      });
    };
    tick();
    window.setInterval(tick, 1000);
  }

  // News cards from config, filterable by category
  const CATEGORY_LABELS = { event: "อีเวนต์", update: "อัปเดต", promo: "โปรโมชัน" };
  const ART = new Set(["hanuman", "yak", "suphanmatcha"]);
  const newsList = document.querySelector("[data-news]");
  const newsItems = Array.isArray(cfg.news) ? cfg.news.filter((n) => CATEGORY_LABELS[n.category] && n.title) : [];
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const renderNews = (filter) => {
    if (!newsList) return;
    newsList.replaceChildren();
    const shown = newsItems.filter((n) => filter === "all" || n.category === filter);
    if (!shown.length) {
      newsList.appendChild(el("li", "muted", "ยังไม่มีข่าวในหมวดนี้"));
      return;
    }
    shown.forEach((n) => {
      const li = el("li");
      const card = el("article", "news-card");
      const thumb = el("div", "news-thumb");
      thumb.dataset.cat = n.category;
      const img = el("img");
      img.src = `assets/img/mascot-${ART.has(n.art) ? n.art : "hanuman"}.svg`;
      img.alt = "";
      img.width = 120;
      img.height = 120;
      thumb.appendChild(img);
      const body = el("div", "news-body");
      const meta = el("p", "news-meta");
      const tag = el("span", "tag", CATEGORY_LABELS[n.category]);
      tag.dataset.cat = n.category;
      meta.append(tag, el("span", "", n.date || ""));
      body.append(meta, el("h3", "", n.title), el("p", "", n.summary || ""));
      if (n.link) {
        const a = el("a", "link", "อ่านต่อ");
        a.href = n.link;
        a.setAttribute("aria-label", `อ่านต่อ: ${n.title}`);
        body.appendChild(a);
      }
      card.append(thumb, body);
      li.appendChild(card);
      newsList.appendChild(li);
    });
  };
  renderNews("all");
  const filterGroup = document.querySelector("[data-news-filters]");
  filterGroup?.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-filter]");
    if (!btn) return;
    filterGroup.querySelectorAll("[data-filter]").forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    renderNews(btn.dataset.filter);
  });

  // Weekly schedule
  const scheduleBody = document.querySelector("[data-schedule]");
  if (scheduleBody && Array.isArray(cfg.schedule) && cfg.schedule.length) {
    scheduleBody.replaceChildren(
      ...cfg.schedule.map((row) => {
        const tr = el("tr");
        const th = el("th", "", row.name || "");
        th.scope = "row";
        tr.append(th, el("td", "", row.day || "รอประกาศ"), el("td", "", row.time || "รอประกาศ"));
        return tr;
      })
    );
  }

  // Live stats: online count and rankings from the game server (read-only, public data only)
  const RANKINGS = {
    level: {
      panel: "panel-level", ranked: true, caption: "10 อันดับเลเวลสูงสุด",
      head: ["อันดับ", "ชื่อตัวละคร", "อาชีพ", "เลเวล"],
      row: (r, i) => [i + 1, r.name, r.job, `${r.baseLevel} / ${r.jobLevel}`],
    },
    mvp: {
      panel: "panel-mvp", ranked: true, caption: "10 อันดับนักล่า MVP",
      head: ["อันดับ", "ชื่อตัวละคร", "MVP ที่ล่าได้"],
      row: (r, i) => [i + 1, r.name, r.kills.toLocaleString("th-TH")],
    },
    guildCastles: {
      panel: "panel-guild", caption: "กิลด์ที่ครองปราสาท",
      head: ["ปราสาท", "กิลด์", "หัวหน้ากิลด์"],
      row: (r) => [r.castle, r.guild, r.master],
    },
  };
  const timeFmt = new Intl.DateTimeFormat("th-TH", {
    timeZone: "Asia/Bangkok", dateStyle: "medium", timeStyle: "short",
  });
  const renderRanking = (key, rows, updatedAt) => {
    const spec = RANKINGS[key];
    const panel = document.getElementById(spec.panel);
    if (!panel) return;
    // Keep the friendly empty state until there is real data to show.
    let live = panel.querySelector(".rank-live");
    const empty = panel.querySelector(".empty");
    if (!Array.isArray(rows) || !rows.length) {
      live?.remove();
      if (empty) empty.hidden = false;
      return;
    }
    if (!live) {
      live = el("div", "rank-live");
      panel.appendChild(live);
    }
    const table = el("table", spec.ranked ? "rank-table is-ranked" : "rank-table");
    table.appendChild(el("caption", "sr-only", spec.caption));
    const headRow = el("tr");
    spec.head.forEach((h) => {
      const th = el("th", "", h);
      th.scope = "col";
      headRow.appendChild(th);
    });
    table.appendChild(el("thead")).appendChild(headRow);
    const tbody = el("tbody");
    rows.forEach((r, i) => {
      const tr = el("tr");
      spec.row(r, i).forEach((v, c) => {
        const cell = el(c === 1 ? "th" : "td", "", String(v));
        if (c === 1) cell.scope = "row";
        tr.appendChild(cell);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    const when = Date.parse(updatedAt);
    const note = el("p", "rank-note", Number.isNaN(when) ? "" : `อัปเดตล่าสุด ${timeFmt.format(when)} น.`);
    const wrap = el("div", "table-wrap");
    wrap.setAttribute("role", "region");
    wrap.setAttribute("aria-label", spec.caption);
    wrap.tabIndex = 0; // scrollable on small screens, so keyboard users can reach it
    wrap.appendChild(table);
    live.replaceChildren(wrap, note);
    if (empty) empty.hidden = true;
  };

  const loadStats = async () => {
    try {
      const res = await fetch(cfg.statsApi, { headers: { Accept: "application/json" } });
      const data = res.ok ? await res.json() : null;
      if (!data || data.ok !== true) throw new Error("stats unavailable");
      setOnline(data.online);
      // Before launch ("soon") the badge stays as configured; afterwards it follows the real servers.
      if (configStatus !== "soon") setStatus(data.serversUp ? "online" : "offline");
      Object.keys(RANKINGS).forEach((key) => renderRanking(key, data.rankings?.[key], data.updatedAt));
    } catch {
      setOnline(cfg.onlinePlayers); // keep the config fallback; never show stale or made-up numbers
    }
  };
  if (cfg.statsApi) {
    loadStats();
    window.setInterval(() => {
      if (document.visibilityState === "visible") loadStats();
    }, 60000);
  }

  // Accessible tabs (WAI-ARIA tabs pattern, manual activation by click or arrows)
  document.querySelectorAll("[data-tabs]").forEach((root) => {
    const tabs = [...root.querySelectorAll('[role="tab"]')];
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    };
    root.addEventListener("click", (e) => {
      const tab = e.target.closest('[role="tab"]');
      if (tab) select(tab, false);
    });
    root.addEventListener("keydown", (e) => {
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      const next = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (next === undefined) return;
      e.preventDefault();
      select(tabs[(next + tabs.length) % tabs.length], true);
    });
  });
})();
