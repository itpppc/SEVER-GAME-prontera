# Website (landing page)

Static Thai landing page for the server: features, rates, how to join, support packages, FAQ and contact.
No build step, no backend, no tracking. Kept separate from the game server files.

## Structure

```
website/
├── index.html          # Page content (Thai)
└── assets/
    ├── config.js       # Server name, address, status, links  ← edit this first
    ├── main.js         # Applies config, copy-address, mobile menu
    └── styles.css      # Theme tokens at the top (:root)
```

## Preview locally

```bash
cd website && python3 -m http.server 8080
# open http://localhost:8080
```

## Before going live

1. `assets/config.js`: set `serverAddress` (from the rAthena setup), `serverStatus`, `openingDate` and every link.
   Links left as `#` render as disabled ("ลิงก์จะเปิดเมื่อเซิร์ฟเวอร์พร้อม"), so nothing points to a dead page.
2. `index.html`: confirm the rates table matches `conf/battle/exp.conf` and `drops.conf`, and that every feature card describes something the server actually does.
3. Replace the placeholder brand name and favicon with your own artwork.

## Deliberately not included (needs owner decision first)

- Online payment, real prices, account registration and any customer data storage.
- Official game client files, publisher artwork, logos or trademarks. The page uses neutral branding and a footer disclaimer.

## Deploy

Any static host works (GitHub Pages, Cloudflare Pages, Vercel, Nginx). Serve the `website/` folder as the site root over HTTPS.
