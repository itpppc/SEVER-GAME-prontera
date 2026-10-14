// Vercel serverless proxy: GET /api/status -> game server stats API (HTTP, server to server).
// The browser only ever talks HTTPS to this site, so there is no mixed-content problem,
// and the edge cache means the game server sees about one request per 30 s however busy the site is.
// Set GAME_STATS_URL in Vercel project settings if the server IP changes (no redeploy of code needed).
"use strict";

const UPSTREAM = process.env.GAME_STATS_URL || "http://54.206.105.93:8090/status";
const TOP_N = 10;

const str = (v, max = 24) => (typeof v === "string" ? v.slice(0, max) : "");
const int = (v) => (Number.isInteger(v) && v >= 0 ? v : 0);
const list = (v, map) => (Array.isArray(v) ? v.slice(0, TOP_N).map(map) : []);

// Pass on only known fields with known types, so a broken or compromised upstream
// can never push arbitrary content to visitors.
function sanitize(data) {
  const r = (data && data.rankings) || {};
  return {
    ok: true,
    online: Number.isInteger(data.online) && data.online >= 0 ? data.online : null,
    serversUp: data.serversUp === true,
    updatedAt: str(data.updatedAt, 32),
    rankings: {
      level: list(r.level, (x) => ({
        name: str(x?.name), job: str(x?.job, 32), baseLevel: int(x?.baseLevel), jobLevel: int(x?.jobLevel),
      })),
      mvp: list(r.mvp, (x) => ({ name: str(x?.name), kills: int(x?.kills) })),
      guildCastles: list(r.guildCastles, (x) => ({
        castle: str(x?.castle, 32), guild: str(x?.guild), master: str(x?.master),
      })),
    },
  };
}

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("X-Content-Type-Options", "nosniff");
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    res.statusCode = 405;
    return res.end(JSON.stringify({ ok: false, reason: "method" }));
  }
  try {
    const upstream = await fetch(UPSTREAM, { signal: AbortSignal.timeout(4000) });
    if (!upstream.ok) throw new Error(`upstream ${upstream.status}`);
    const body = sanitize(await upstream.json());
    res.setHeader("Cache-Control", "public, max-age=0, s-maxage=30, stale-while-revalidate=60");
    res.statusCode = 200;
    res.end(JSON.stringify(body));
  } catch {
    // Game server unreachable: tell the page so it can show "offline" instead of stale numbers.
    res.setHeader("Cache-Control", "public, max-age=0, s-maxage=10");
    res.statusCode = 200;
    res.end(JSON.stringify({ ok: false, reason: "unreachable" }));
  }
};
