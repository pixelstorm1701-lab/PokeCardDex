// Houdt de pagina in de kast zodat hij ook zonder bereik opengaat.
// Alleen deze map; de rest van de Dex blijft ongemoeid.
const KAST = "30th-japan-v2";
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

function bewaar(verzoek, res) {
  if (res && res.ok && res.type === "basic") {
    const kopie = res.clone();
    caches.open(KAST).then(c => c.put(verzoek, kopie));
  }
  return res;
}

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;

  // De pagina zelf eerst van het net halen, anders blijf je na een update de
  // oude versie zien. Lukt dat niet, dan pakt hij alsnog wat in de kast ligt.
  if (e.request.mode === "navigate") {
    e.respondWith(
      fetch(e.request)
        .then(res => bewaar(e.request, res))
        .catch(() => caches.match("./index.html", { ignoreSearch: true }))
    );
    return;
  }

  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit =>
      hit || fetch(e.request).then(res => bewaar(e.request, res))
             .catch(() => caches.match("./index.html"))
    )
  );
});
