/**
 * Site configuration — the only file you need to edit for day-to-day changes.
 * Values marked TODO are placeholders until the server goes live.
 * Never put passwords, API keys or payment secrets here: this file is public.
 */
window.SITE_CONFIG = Object.freeze({
  serverName: "Prontera Realm", // TODO: final brand name
  // TODO: public address from the rAthena setup (login-server, default port 6900)
  serverAddress: "play.example.com",
  serverPort: 6900,
  // "online" | "offline" | "soon" — static for now, no live status check yet
  serverStatus: "soon",
  openingDate: "เร็ว ๆ นี้", // TODO: e.g. "1 ธ.ค. 2569"

  links: {
    register: "#contact", // TODO: account registration page
    clientDownload: "#", // TODO: patched client download (your own build, not official files)
    setupGuide: "#", // TODO: link to the setup guide from the server repo
    discord: "#", // TODO
    line: "#", // TODO
    facebook: "#", // TODO
    email: "contact@example.com", // TODO
  },
});
