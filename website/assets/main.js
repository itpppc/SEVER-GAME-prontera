(() => {
  "use strict";

  const cfg = window.SITE_CONFIG;
  if (!cfg) return;

  const STATUS_LABELS = {
    online: "เซิร์ฟเวอร์ออนไลน์",
    offline: "ปิดปรับปรุงชั่วคราว",
    soon: "เปิดให้บริการเร็ว ๆ นี้",
  };

  const isPlaceholder = (href) => !href || href === "#";

  // Text bindings: <span data-config="serverName">
  document.querySelectorAll("[data-config]").forEach((el) => {
    const value = cfg[el.dataset.config];
    if (value !== undefined) el.textContent = String(value);
  });

  // Link bindings: <a data-link="discord">. Unset links are marked as pending, not dead.
  document.querySelectorAll("[data-link]").forEach((el) => {
    const key = el.dataset.link;
    const href = key === "email" ? `mailto:${cfg.links.email}` : cfg.links[key];
    if (isPlaceholder(href)) {
      el.setAttribute("aria-disabled", "true");
      el.setAttribute("title", "ลิงก์จะเปิดเมื่อเซิร์ฟเวอร์พร้อม");
      el.addEventListener("click", (e) => e.preventDefault());
      return;
    }
    el.href = href;
    if (/^https?:/i.test(href)) {
      el.target = "_blank";
      el.rel = "noopener noreferrer";
    }
  });

  if (cfg.links.email) {
    document.querySelectorAll("[data-email]").forEach((el) => (el.textContent = cfg.links.email));
  }

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
