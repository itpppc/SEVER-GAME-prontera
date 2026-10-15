# Website (landing page)

Static Thai landing page for the server: features, rates, how to join, free-to-play info, FAQ and contact.
No build step, no backend, no tracking. Kept separate from the game server files.

## Structure

```
website/
├── index.html          # Page content (Thai)
└── assets/
    ├── config.js       # Server name, address, status, links  ← edit this first
    ├── main.js         # Applies config, copy-address, mobile menu
    ├── styles.css      # Theme tokens at the top (:root)
    └── img/            # Original Ramakien-themed SVG illustrations (hero scene, mascots), ~1-10 KB each
```

## Preview locally

```bash
cd website && python3 -m http.server 8080
# open http://localhost:8080
```

## Before going live

1. `assets/config.js`: set `serverAddress` (from the rAthena setup), `serverStatus`, `openingDate` and every link.
   News cards (`news`), the weekly schedule (`schedule`) and the online count (`onlinePlayers`) are also edited there; only publish what is true.
   Links left as `#` (or an `@example.com` email) show a "coming soon" toast when clicked, so nothing points to a dead page.
2. `index.html`: confirm the rates table matches `conf/battle/exp.conf` and `drops.conf`, and that every feature card describes something the server actually does.
3. Replace the placeholder brand name and favicon with your own artwork.

## Deliberately not included (needs owner decision first)

- Online payment, real prices, account registration and any customer data storage.
- Live data: `statsApi` in config.js points at the Vercel function `api/status.js`, which reads the game server's read-only stats service (`webapi/`, see its README). It fills the online count and the level, MVP and castle rankings. If the game server does not answer, the page shows "—" and the empty ranking states. PvP rankings and registration are not built.
- Official game client files, publisher artwork, logos or trademarks. The page uses neutral branding and a footer disclaimer.

## Deploy

Vercel: the repo-root `vercel.json` serves `website/` with no build step, so the project works with the default Root Directory. (If Root Directory is set to `website`, that also works; Vercel then ignores the root `vercel.json`.)

Any other static host works too (GitHub Pages, Cloudflare Pages, Nginx). Serve the `website/` folder as the site root over HTTPS.

## Player guide and installer

- `guide.html`: player guide (download, install, create an account with `_M`/`_F` at the game's login screen, first login, troubleshooting). The menu links for download, guide and register point here.
- `downloads/Install-Prontera.bat`: copy of the one-click installer from the server thread (`installer/Install-Prontera.bat` on branch `claude/project-thread-wzqygb`). Copy it again whenever the installer changes, and keep CRLF line endings (`downloads/.gitattributes`). It contains no game files; it downloads them from the original sources on the player's PC.
- Contact buttons (Discord, LINE, Facebook, email) stay hidden until a real link is set in `config.js`.

