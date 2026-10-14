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

  // Link bindings: <a data-link="discord">. Unset links are marked as pending, not dead.
  document.querySelectorAll("[data-link]").forEach((el) => {
    const key = el.dataset.link;
    const href = key === "email" ? `mailto:${cfg.links.email}` : cfg.links[key];
    const raw = key === "email" ? cfg.links.email : cfg.links[key];
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

  // Server status badge
  const status = STATUS_LABELS[cfg.serverStatus] ? cfg.serverStatus : "soon";
  document.querySelectorAll("[data-status]").forEach((el) => {
    el.dataset.state = status;
    el.querySelector("[data-status-text]").textContent = STATUS_LABELS[status];
  });

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
})();
