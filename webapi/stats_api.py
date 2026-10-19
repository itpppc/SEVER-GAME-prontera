#!/usr/bin/env python3
"""Read-only stats API for the website: players online and rankings from the rAthena DB.

Serves GET /status as JSON (cached for 30 s, so traffic never hammers the DB).
Publishes only what players already see in game: character names, jobs, levels,
MVP counts and castle owners. Never account ids, emails, IPs or anything private.
Stdlib only; queries go through the `mysql` client with a SELECT-only DB user.
"""
import json
import os
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MYSQL_CNF = os.environ.get("WEBAPI_MYSQL_CNF", "/etc/sever-webapi/my.cnf")
DB = os.environ.get("WEBAPI_DB", "ragnarok")
LOG_DB = os.environ.get("WEBAPI_LOG_DB", "ragnarok_log")
PORT = int(os.environ.get("WEBAPI_PORT", "8090"))
CACHE_SECONDS = 30
TOP_N = 10
# rAthena default groups: 0 Player, 1 Super Player; 2 and up are staff, hidden from rankings.
MAX_PLAYER_GROUP = 1
GAME_PORTS = (6900, 6121, 5121)  # login, char, map

JOBS = {
    0: "Novice", 1: "Swordman", 2: "Mage", 3: "Archer", 4: "Acolyte", 5: "Merchant", 6: "Thief",
    7: "Knight", 8: "Priest", 9: "Wizard", 10: "Blacksmith", 11: "Hunter", 12: "Assassin",
    14: "Crusader", 15: "Monk", 16: "Sage", 17: "Rogue", 18: "Alchemist", 19: "Bard", 20: "Dancer",
    23: "Super Novice", 24: "Gunslinger", 25: "Ninja",
    4001: "High Novice", 4002: "High Swordman", 4003: "High Mage", 4004: "High Archer",
    4005: "High Acolyte", 4006: "High Merchant", 4007: "High Thief", 4008: "Lord Knight",
    4009: "High Priest", 4010: "High Wizard", 4011: "Whitesmith", 4012: "Sniper",
    4013: "Assassin Cross", 4015: "Paladin", 4016: "Champion", 4017: "Professor",
    4018: "Stalker", 4019: "Creator", 4020: "Clown", 4021: "Gypsy",
    4046: "Taekwon", 4047: "Star Gladiator", 4049: "Soul Linker",
    4054: "Rune Knight", 4055: "Warlock", 4056: "Ranger", 4057: "Arch Bishop", 4058: "Mechanic",
    4059: "Guillotine Cross", 4060: "Rune Knight", 4061: "Warlock", 4062: "Ranger",
    4063: "Arch Bishop", 4064: "Mechanic", 4065: "Guillotine Cross", 4066: "Royal Guard",
    4067: "Sorcerer", 4068: "Minstrel", 4069: "Wanderer", 4070: "Sura", 4071: "Genetic",
    4072: "Shadow Chaser", 4073: "Royal Guard", 4074: "Sorcerer", 4075: "Minstrel",
    4076: "Wanderer", 4077: "Sura", 4078: "Genetic", 4079: "Shadow Chaser",
    4190: "Expanded Super Novice", 4211: "Kagerou", 4212: "Oboro", 4215: "Rebellion",
    4218: "Summoner", 4239: "Star Emperor", 4240: "Soul Reaper",
    4252: "Dragon Knight", 4253: "Meister", 4254: "Shadow Cross", 4255: "Arch Mage",
    4256: "Cardinal", 4257: "Windhawk", 4258: "Imperial Guard", 4259: "Biolo",
    4260: "Abyss Chaser", 4261: "Elemental Master", 4262: "Inquisitor", 4263: "Troubadour",
    4264: "Trouvere", 4302: "Sky Emperor", 4303: "Soul Ascetic", 4304: "Shinkiro",
    4305: "Shiranui", 4306: "Night Watch", 4307: "Hyper Novice", 4308: "Spirit Handler",
}
# castle_id -> name, from rAthena db/re/castle_db.yml
CASTLES = [
    "Neuschwanstein", "Hohenschwangau", "Nuernberg", "Wuerzburg", "Rothenburg",  # Al De Baran
    "Repherion", "Eeyolbriggar", "Yesnelph", "Bergel", "Mersetzdeitz",  # Geffen
    "Bright Arbor", "Scarlet Palace", "Holy Shadow", "Sacred Altar", "Bamboo Grove Hill",  # Payon
    "Kriemhild", "Swanhild", "Fadhgridh", "Skoegul", "Gondul",  # Prontera
    "Earth", "Air", "Water", "Fire",  # Novice guild castles
    "Himinn", "Andlangr", "Viblainn", "Hljod", "Skidbladnir",  # Schwarzwald
    "Mardol", "Cyr", "Horn", "Gefn", "Bandis",  # Arunafeltz
    *[f"Kafragarten {i}" for i in range(1, 6)], *[f"Gloria {i}" for i in range(1, 6)],
]


def castle_label(castle_id):
    return CASTLES[castle_id] if 0 <= castle_id < len(CASTLES) else f"Castle {castle_id}"


def _unescape(field):
    # mysql --batch escapes \\, \t, \n and \0 in values
    return field.replace("\\t", "\t").replace("\\n", "\n").replace("\\0", "").replace("\\\\", "\\")


def run_query(sql):
    """Run one SELECT and return rows as lists of strings ([] on any failure)."""
    try:
        out = subprocess.run(
            ["mysql", f"--defaults-extra-file={MYSQL_CNF}", "--batch", "--skip-column-names", "-e", sql],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [[_unescape(f) for f in line.split("\t")] for line in out.splitlines() if line]


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def collect(query=run_query, ports_up=None):
    players = f"JOIN `{DB}`.`login` l ON l.account_id = c.account_id AND l.group_id <= {MAX_PLAYER_GROUP}"
    online_rows = query(f"SELECT COUNT(c.char_id) FROM `{DB}`.`char` c {players} WHERE c.online = 1")
    level_rows = query(
        f"SELECT c.name, c.class, c.base_level, c.job_level FROM `{DB}`.`char` c {players} "
        f"ORDER BY c.base_level DESC, c.base_exp DESC, c.job_level DESC LIMIT {TOP_N}"
    )
    mvp_rows = query(
        f"SELECT c.name, COUNT(m.kill_char_id) AS kills FROM `{LOG_DB}`.`mvplog` m "
        f"JOIN `{DB}`.`char` c ON c.char_id = m.kill_char_id {players} "
        f"GROUP BY m.kill_char_id, c.name ORDER BY kills DESC LIMIT {TOP_N}"
    )
    castle_rows = query(
        f"SELECT gc.castle_id, g.name, g.master FROM `{DB}`.`guild_castle` gc "
        f"JOIN `{DB}`.`guild` g ON g.guild_id = gc.guild_id WHERE gc.guild_id > 0 ORDER BY gc.castle_id"
    )

    def as_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    up = ports_up if ports_up is not None else all(port_open(p) for p in GAME_PORTS)
    return {
        "online": as_int(online_rows[0][0]) if online_rows else None,
        "serversUp": up,
        "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rankings": {
            "level": [
                {"name": r[0], "job": JOBS.get(as_int(r[1]), f"Job {as_int(r[1])}"),
                 "baseLevel": as_int(r[2]), "jobLevel": as_int(r[3])}
                for r in level_rows if len(r) >= 4
            ],
            "mvp": [{"name": r[0], "kills": as_int(r[1])} for r in mvp_rows if len(r) >= 2],
            "guildCastles": [
                {"castle": castle_label(as_int(r[0])), "guild": r[1], "master": r[2]}
                for r in castle_rows if len(r) >= 3
            ],
        },
    }


class Cache:
    def __init__(self, ttl, producer):
        self.ttl, self.producer = ttl, producer
        self.lock = threading.Lock()
        self.body, self.at = b"", 0.0

    def get(self):
        with self.lock:
            if time.monotonic() - self.at >= self.ttl or not self.body:
                self.body = json.dumps(self.producer(), ensure_ascii=False).encode("utf-8")
                self.at = time.monotonic()
            return self.body


CACHE = Cache(CACHE_SECONDS, collect)


class Handler(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "sever-webapi"
    sys_version = ""

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            return self._send(200, b'{"ok":true}')
        if path != "/status":
            return self._send(404, b'{"error":"not found"}')
        self._send(200, CACHE.get())

    def do_HEAD(self):
        self._send(405, b"")

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", f"public, max-age={CACHE_SECONDS}")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # keep the journal quiet: errors only
        pass


if __name__ == "__main__":
    ThreadingHTTPServer.daemon_threads = True
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
