/* Service worker: guarda la app para que funcione sin internet.
   OJO: datos.json NO se cachea, para que las actualizaciones siempre lleguen.
   Sube el número de versión si cambias index.html. */
const CACHE = 'precios-v4';
const ARCHIVOS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARCHIVOS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((claves) =>
      Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // Nunca interceptar los datos: siempre van a la red (y la app los guarda aparte)
  if (url.pathname.endsWith('datos.json')) return;
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
