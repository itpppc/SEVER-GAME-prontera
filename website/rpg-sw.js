/* Offline cache for the ศึกลงกา game (/rpg). Lives at the site root so its scope can cover "/rpg" without a trailing slash. */
const CACHE = 'lanka-rpg-v1';
const CORE = [
  '/rpg',
  '/rpg/engine.js',
  '/rpg/game.js',
  '/rpg/game.css',
  '/rpg/manifest.webmanifest',
  '/rpg/icons/icon-192.png',
  '/assets/img/favicon.svg',
  ...['hanuman', 'rama', 'phiphek', 'nonthok', 'benjakai', 'kumpakan'].map((c) => '/assets/img/chars/' + c + '.svg'),
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith('lanka-rpg-') && k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Pages: network first so updates show up, cache when offline. Everything else: cache first, refreshed in the background.
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  const isFont = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!sameOrigin && !isFont) return;

  if (req.mode === 'navigate') {
    e.respondWith(fetch(req)
      .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put('/rpg', copy)); return res; })
      .catch(() => caches.match('/rpg')));
    return;
  }
  e.respondWith(caches.match(req).then((hit) => {
    const net = fetch(req).then((res) => {
      if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => hit);
    return hit || net;
  }));
});
