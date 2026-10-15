/**
 * Site configuration — the only file you need to edit for day-to-day changes.
 * Values marked TODO are placeholders until the server goes live.
 * Never put passwords, API keys or payment secrets here: this file is public.
 */
window.SITE_CONFIG = Object.freeze({
  serverName: "Prontera Realm", // TODO: final brand name
  // Public address = PUBLIC_IP in the server .env (login-server port 6900). The installer sets it for players.
  serverAddress: "54.206.105.93",
  serverPort: 6900,
  // "online" | "offline" | "soon" — static for now, no live status check yet
  serverStatus: "soon",
  openingDate: "เร็ว ๆ นี้", // TODO: e.g. "1 ธ.ค. 2569"
  // Players online fallback: a number, or null to show "—". Replaced by the live count from statsApi.
  onlinePlayers: null,
  // Live online count + rankings (Vercel function api/status.js -> game server webapi/). "" turns it off.
  statsApi: "/api/status",

  links: {
    // Accounts are created in the game's login screen (ID + _M/_F), so this points at the guide.
    register: "guide.html#register",
    // The one-click installer (website/downloads/Install-Prontera.bat) and how to use it.
    clientDownload: "guide.html#download",
    setupGuide: "guide.html",
    // Contact channels: "#" hides the button until a real link is set.
    discord: "#", // TODO: Discord invite link, e.g. https://discord.gg/xxxx
    line: "#", // TODO: LINE OA link, e.g. https://lin.ee/xxxx
    facebook: "#", // TODO: Facebook page URL
    email: "contact@example.com", // TODO: real contact email (example.com hides it)
  },

  // News cards. category: "event" | "update" | "promo". Newest first. Only publish what is true.
  // art: "hanuman" | "yak" | "suphanmatcha" (picks the card illustration)
  news: [
    {
      category: "update",
      date: "14 ต.ค. 2569",
      title: "เซิร์ฟเวอร์เริ่มทดสอบระบบแล้ว",
      summary: "ทีมงานเปิดเซิร์ฟเวอร์ทดสอบภายในเรียบร้อย กำลังเตรียมตัวเกมและระบบสมัครไอดีให้พร้อมก่อนเปิดจริง",
      link: "#join",
      art: "hanuman",
    },
    {
      category: "update",
      date: "14 ต.ค. 2569",
      title: "โฉมใหม่ ธีมวรรณคดีรามเกียรติ์",
      summary: "เว็บไซต์และงานภาพชุดใหม่ พบกับพระราม หนุมาน ยักษ์น้อย และนางสุพรรณมัจฉาในสไตล์การ์ตูนไทย",
      link: "#top",
      art: "suphanmatcha",
    },
    {
      category: "event",
      date: "เร็ว ๆ นี้",
      title: "อีเวนต์ฉลองเปิดเซิร์ฟ",
      summary: "รายละเอียดกิจกรรมและของรางวัลจะประกาศพร้อมวันเปิดเซิร์ฟ ติดตามข่าวได้ทาง Discord",
      link: "#contact",
      art: "yak",
    },
    {
      category: "promo",
      date: "เร็ว ๆ นี้",
      title: "เล่นฟรี 100% ไม่มีเก็บเงิน",
      summary: "ไม่มีค่าสมัคร ไม่มีค่ารายเดือน ไม่มีเติมเงิน ดาวน์โหลดและเล่นได้ฟรีทันที",
      link: "#free",
      art: "suphanmatcha",
    },
  ],

  // Weekly activities. Use "รอประกาศ" until the times are set in the server config.
  schedule: [
    { name: "War of Emperium (ชิงปราสาท)", day: "รอประกาศ", time: "รอประกาศ" },
    { name: "ล่าบอส MVP", day: "รอประกาศ", time: "รอประกาศ" },
    { name: "อีเวนต์ GM", day: "รอประกาศ", time: "รอประกาศ" },
  ],
});
