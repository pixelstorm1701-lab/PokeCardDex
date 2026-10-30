// Houdt de pagina in de kast zodat hij ook zonder bereik opengaat.
// Alleen deze map; de rest van de Dex blijft ongemoeid.
const KAST = "30th-japan-v1";
const SPUL = ["./", "./index.html", "./icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(KAST).then(c => c.addAll(SPUL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(namen => Promise.all(namen.filter(n => n !== KAST).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit =>
      hit || fetch(e.request).then(res => {
        // nieuwe versie meteen bewaren, dan klopt de kast na een update
        if (res.ok && res.type === "basic") {
          const kopie = res.clone();
          caches.open(KAST).then(c => c.put(e.request, kopie));
        }
        return res;
      }).catch(() => caches.match("./index.html"))
    )
  );
});
