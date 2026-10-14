/**
 * Site configuration — the only file you need to edit for day-to-day changes.
 * Values marked TODO are placeholders until the server goes live.
 * Never put passwords, API keys or payment secrets here: this file is public.
 */
window.SITE_CONFIG = Object.freeze({
  serverName: "Prontera Realm", // TODO: final brand name
  // TODO: public address = PUBLIC_IP in the server .env (no VPS yet); login-server port 6900
  serverAddress: "play.example.com",
  serverPort: 6900,
  // "online" | "offline" | "soon" — static for now, no live status check yet
  serverStatus: "soon",
  openingDate: "เร็ว ๆ นี้", // TODO: e.g. "1 ธ.ค. 2569"

  links: {
    register: "#contact", // TODO: account registration page
    clientDownload: "#", // TODO: patched client download (your own build, not official files)
    // TODO: host the player guide on this site; the repo is private so a GitHub link would 404 for players
    setupGuide: "#",
    discord: "#", // TODO
    line: "#", // TODO
    facebook: "#", // TODO
    email: "contact@example.com", // TODO
  },
});
