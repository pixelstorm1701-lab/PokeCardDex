// Houdt de pagina in de kast zodat hij ook zonder bereik opengaat.
// Alleen deze map; de rest van de Dex blijft ongemoeid.
const KAST = "30th-japan-v3";
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
  if (res && res.ok && (res.type === "basic" || res.type === "cors")) {
    const kopie = res.clone();
    caches.open(KAST).then(c => c.put(verzoek, kopie));
  }
  return res;
}

// Eerst het net, dan pas de kast. Lukt het net niet, dan alsnog wat er ligt.
function versEerst(verzoek, terugval) {
  return fetch(verzoek)
    .then(res => bewaar(verzoek, res))
    .catch(() => caches.match(verzoek, { ignoreSearch: true })
                       .then(hit => hit || (terugval ? caches.match(terugval) : undefined)));
}

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;

  // De pagina zelf, anders blijf je na een update de oude versie zien.
  if (e.request.mode === "navigate") {
    e.respondWith(versEerst(e.request, "./index.html"));
    return;
  }

  // En de prijzenlijst, om dezelfde reden: die verandert elke dag, dus uit de
  // kast serveren betekent dat je voor altijd de prijzen van die ene dag ziet.
  if (e.request.url.includes("prices.json")) {
    e.respondWith(versEerst(e.request, null));
    return;
  }

  // De rest - plaatjes, het icoon - verandert niet, dus die mag uit de kast.
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit =>
      hit || fetch(e.request).then(res => bewaar(e.request, res))
             .catch(() => caches.match("./index.html"))
    )
  );
});
