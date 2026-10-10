# Dex's Pokecard Dex

A single-page checklist for Pokémon TCG sets. The front page is a shelf of set tiles, each
showing how far along you are; open one and you get its full card list.

| Tile | Set | Cards | Reverse holos | Master set |
|---|---|---|---|---|
| Pitch Black | Mega Evolution — Pitch Black (`PBL`) | 120 | 74 | 194 |
| Journey Together | Scarlet & Violet — Journey Together (`JTG`) | 190 | 143 | 333 |
| Surging Sparks | Scarlet & Violet — Surging Sparks (`SSP`) | 252 | 165 | 417 |
| Gem Pack Vol. 5 | Simplified Chinese — Gem Pack Vol. 5 (`CBB5C`) | 196 | — | 196 |
| Sun & Moon | Sun & Moon — Base Set (`SUM`) | 173 | 136 | 309 | *(hidden)*
| 30th Celebration | Mega Evolution — 30th Celebration (`30C`) | 215 | — | 215 |
| Lost Origin | Sword & Shield — Lost Origin (`LOR`) | 247 | 149 | 396 |
| Fusion Strike | Sword & Shield — Fusion Strike (`FST`) | 284 | 217 | 501 |
| Paradox Rift | Scarlet & Violet — Paradox Rift (`PAR`) | 266 | 162 | 428 |
| Silver Tempest | Sword & Shield — Silver Tempest (`SIT`) | 245 | 144 | 389 |
| Scarlet & Violet | Scarlet & Violet — Base Set (`SVI`) | 258 | 186 | 444 |
| Chilling Reign | Sword & Shield — Chilling Reign (`CRE`) | 233 | 136 | 369 |
| Brilliant Stars | Sword & Shield — Brilliant Stars (`BRS`) | 216 | 124 | 340 |
| Astral Radiance | Sword & Shield — Astral Radiance (`ASR`) | 246 | 128 | 374 |
| Paldea Evolved | Scarlet & Violet — Paldea Evolved (`PAL`) | 279 | 176 | 455 |
| Temporal Forces | Scarlet & Violet — Temporal Forces (`TEF`) | 218 | 140 | 358 |
| Obsidian Flames | Scarlet & Violet — Obsidian Flames (`OBF`) | 230 | 176 | 406 |
| Crown Zenith | Sword & Shield — Crown Zenith (`CRZ`) | 230 | 113 | 343 |
| 151 | Scarlet & Violet — 151 (`MEW`) | 207 | 153 | 360 |
| Paldean Fates | Scarlet & Violet — Paldean Fates (`PAF`) | 245 | — | 245 |
| Pokémon GO | Sword & Shield — Pokémon GO (`PGO`) | 88 | 58 | 146 |
| Stellar Crown | Scarlet & Violet — Stellar Crown (`SCR`) | 175 | 125 | 300 |
| Mega Evolution | Mega Evolution — Base Set (`MEG`) | 188 | 122 | 310 |
| Battle Styles | Sword & Shield — Battle Styles (`BST`) | 183 | 123 | 306 |
| Chaos Rising | Mega Evolution — Chaos Rising (`CHR`) | 122 | 76 | 198 |
| Phantasmal Flames | Mega Evolution — Phantasmal Flames (`PHF`) | 130 | 84 | 214 |
| Destined Rivals | Scarlet & Violet — Destined Rivals (`DRI`) | 244 | 165 | 409 |
| Evolving Skies | Sword & Shield — Evolving Skies (`EVS`) | 237 | 132 | 369 |
| Twilight Masquerade | Scarlet & Violet — Twilight Masquerade (`TWM`) | 226 | 147 | 373 |
| SVP Promos | Scarlet & Violet — Black Star Promos (`SVP`) | 226 | — | 226 |
| SWSH Promos | Sword & Shield — Black Star Promos (`SWSHP`) | 307 | — | 307 |
| MEP Promos | Mega Evolution — Black Star Promos (`MEP`) | 89 | — | 89 |
| Shrouded Fable | Scarlet & Violet — Shrouded Fable (`SFA`) | 99 | 55 | 154 |
| Perfect Order | Mega Evolution — Perfect Order (`POR`) | 124 | 79 | 203 |
| Ascended Heroes | Mega Evolution — Ascended Heroes (`ASC`) | 295 | 178 | 473 |
| Vivid Voltage | Sword & Shield — Vivid Voltage (`VIV`) | 203 | 142 | 345 |
| Sword & Shield | Sword & Shield — Base Set (`SSH`) | 216 | 164 | 380 |
| Shining Fates | Sword & Shield — Shining Fates (`SHF`) | 195 | 46 | 241 |

11,886 slots on the shelf (12,195 counting the hidden set). Tick the ones you own; the page keeps
count per set, filters down to what's missing, and hands you a link that carries your whole
collection to another device.

## Normal and reverse holo

A card that was also printed as a reverse holo gets **two ticks**: green for the normal copy,
foil-blue for the reverse. A row turns green only when every printing it has is ticked, and
half-done rows get a blue tint.

Which cards those are is not guessed from the rarity but listed per set in `rv`, the positions that
have a reverse holo, read off TCGdex's per-card `variants.reverse`. `check_reverse.py` rebuilds
those lists. The rarity rule the dex used before was close but wrong in five sets, worst of all
Paldean Fates, where its 91 numbered cards do have reverse holos even though the shiny vault behind
them does not.

Sun & Moon keeps the old rule: TCGdex reports no reverse holos at all for that set, which is plainly
wrong for a 2017 set, so its own data is not trusted there.

One thing this does not cover: the Poké Ball and Master Ball reverse patterns in 151, and any
set-specific parallel beyond the single reverse holo.

No build step, no dependencies, no backend. `public/index.html` is the whole app.

## Cardmarket prices

Under every card sits its Cardmarket trend price - one figure for the plain print, one in foil blue
for the reverse holo - and each set shows what the boxes you ticked are worth, with a grand total on
the shelf.

The numbers live in `prices.json` next to `index.html`: Cardmarket's own price guide, relayed by
TCGdex. `fetch_prices.py` builds that file. It reads the card list straight out of `index.html`, so
it can never drift from the page, asks TCGdex for every card and keeps two numbers per card
(`trend` and `trend-holo`). About 90 KB for 5,731 cards, loaded once when the page opens.

`.github/workflows/prices.yml` runs it every morning at 05:40 UTC and commits the result; you can
also press **Run workflow** on the Actions tab. A run that comes back with less than 80% of the
prices it had before leaves the old file alone, so a bad day at the API never wipes your figures.

Two sets have no prices at all: Gem Pack Vol. 5, which no price source carries, and 30th
Celebration, which TCGdex has card data for but no Cardmarket listing yet. Their rows simply show
no figures. Without `prices.json` the whole thing is invisible and the dex works as before.

## Cross-device sync

Out of the box the page saves in the browser it's open in. To have every device show the same
numbers, give it a Firestore database — about five minutes of setup, no login for you or anyone
you share it with.

1. **Firebase console → Build → Firestore Database → Create database.** Pick a region, start in
   *production mode* (the rules in `firestore.rules` replace the defaults).
2. **Project settings → Your apps → Web app.** If you have none, add one (the `</>` button); no
   hosting checkbox needed. Copy the `firebaseConfig` object it shows you.
3. Open `public/index.html`, find the `const FIREBASE = {` block near the top of the `<script>`,
   and paste your four values (`apiKey`, `authDomain`, `projectId`, `appId`).
4. Deploy both the page and the rules:

   ```bash
   firebase deploy --only hosting,firestore:rules
   ```

Open the site once. It mints a random sync id, puts it in the address as `#s=…` and stores your
collection under it. **Copy sync link** at the bottom hands you that URL — open it on your phone
and both devices read and write the same document, live: tick a card on one and the other updates
within a second, no refresh.

Notes worth knowing:

- The sync id is the only key to your collection, so treat the link like a password. Anyone who
  has it can edit your ticks; nobody who doesn't can find them.
- Ticks made offline are kept and merged in the first time the device reconnects, so you never
  lose a card by ticking it on the train.
- With no config filled in, the page falls back to `localStorage` plus the old `#c=…` state link.
- Published on claude.ai as an artifact, it uses the artifact's own store instead and syncs
  across your signed-in devices with no setup at all.

## Run it locally

```bash
cd public && python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy to Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase projects:create dex-pokecard-dex     # or use an existing project
```

Put the project ID in `.firebaserc` (replace `REPLACE-WITH-YOUR-FIREBASE-PROJECT-ID`), then:

```bash
firebase deploy --only hosting
```

You get `https://<project-id>.web.app`. Add your own domain under
Hosting → Add custom domain if you want one.

### Deploy on every push

`.github/workflows/firebase-hosting.yml` does it from GitHub Actions. Two things first:

1. Put the same project ID in that file (replace the placeholder).
2. Run `firebase init hosting:github` once — it creates the service account and adds the
   `FIREBASE_SERVICE_ACCOUNT` secret to your repo. (Or create a service-account JSON key in the
   Firebase console and paste it into that repo secret by hand.)

## Deploy to GitHub Pages instead

`.github/workflows/github-pages.yml` publishes the `public/` folder. In your repo, go to
**Settings → Pages → Build and deployment → Source: GitHub Actions**, then push to `main`.
You get `https://<user>.github.io/<repo>/`.

Both workflows can live side by side — delete whichever one you don't want.

## Push it to GitHub

```bash
git init -b main
git add .
git commit -m "Pokecard Dex — Pitch Black checklist"
gh repo create pokecard-dex --public --source=. --push
```

## Adding another set

Everything is driven by the `SETS` array at the top of the `<script>` in `public/index.html`.
Append one more object and the tile, counters, filters and storage appear on their own:

```js
{
  key: "destined-rivals",             // storage id — never change it once used
  tab: "Destined Rivals",             // tile title
  name: "Scarlet & Violet — Destined Rivals",
  code: "DRI",
  released: "30 May 2025",
  accent: "#c0563f",                  // tile colour, also used inside the set view
  rh: ["Common","Uncommon","Rare"],   // rarities that also exist as a reverse holo ([] for none)
  printed: 182,                       // last numbered card; the rest count as secret rares
  total: 244,
  cards: [ [1, "Pikachu", "Common", "Pokémon", "Lightning"], ... ]
}
```

Card rows are `[number, name, rarity, supertype, type]`, with an optional sixth field for the
printed number when it isn't the position in the list — Sun & Moon's `101a` uses it, and the
grouping and search read that label rather than the index. Add new sets at the **end** of the
array — the share link encodes sets in this order, so reordering invalidates old links.

A set can also define its own sections instead of the numbered/secret split, with
`groups: [[title, firstIndex, lastIndex], ...]` over the internal card indexes. 30th Celebration
uses it for its five parts: the numbered set, the secret rares, the 30-card Classic Collection,
the 8 basic energy and the MEP promos. Each section gets its own heading, range and progress chip.
A `note` field replaces the card count in the set's meta line when the plain total would mislead.

To take a set off the shelf without losing anything, give it `hidden: true` rather than deleting
it. The tile and the grand total skip it, its ticks stay in storage, and it keeps its slot in the
share code so existing links still decode. Drop the flag and it reappears exactly as it was.

## Ordering the shelf

Above the tiles sit a search box and an order menu: as added, name A-Z or Z-A, by series, newest or
oldest first, most complete, most still missing, biggest set, or worth the most. **By series** also
draws a heading per series - Sword & Shield, Scarlet & Violet, Mega Evolution, Simplified Chinese -
with the sets inside it oldest first, so the shelf reads as a timeline. The series itself comes from
the part of a set's `name` before the dash, and `rd` holds its release date in sortable form. Your
choice is remembered per browser.

## Card pictures

Every row carries a thumbnail; tap it for the full card. Each set says where its pictures live in an
`img` field: segments of `[firstIndex, lastIndex, host, path, pad]`, with host `t` for TCGdex
(`assets.tcgdex.net/en/<series>/<set>/<number>/low.png`, `/high.png`), `p` for the Pokémon TCG API
(the Trainer and Galarian Gallery subsets, which TCGdex has no art for), `o` for The Pokémon
Company's own gallery CDN (30th Celebration's Classic Collection, published nowhere else) and `l`
for a folder shipped with the page.

Two things exist only as local files, because no online source carries them: Gem Pack Vol. 5 in
`public/img/gem5/001-196.webp` (no card API covers Simplified Chinese sets; photos from
pokipair.com) and 30th Celebration's three RGB Mews in `public/img/30c/159-161.webp` (scans from
their PriceCharting listings). Together about 6 MB.

Pictures load only when a row scrolls into view, and the **Card pictures** switch in the toolbar
turns them off altogether (remembered per browser) for when you are on mobile data. Every card in the dex has a picture.

The three promo sets carry a `tg` field (the TCGdex set they sit in, and how their numbers are
padded). The price script asks for those by id instead of working them out from the picture
segments, which is what lets the MEP promos have prices while having no pictures anywhere.

Most sets come straight from the Pokémon TCG API. Surging Sparks 251 and 252 are
filled in by hand because the API doesn't return them. Gem Pack Vol. 5 is a Simplified
Chinese-exclusive set that the API doesn't cover at all, so it is built from the published set
list, checked against TCG Collector and pokipair.com: 28 Pokémon in order, each with seven variants
(2× Common, 2× Uncommon, Rare, Double Rare, Triple Rare). The cards are not numbered 1-196 on the
card itself — each Pokémon gets its own 01/07 - 07/07 run — so the set is split into 28 sections,
one per Pokémon, and shows those printed numbers. Its energy-type stripes are inferred from each
Pokémon's usual TCG type rather than read off the cards. 30th Celebration now comes from the API
too (`me55` plus `me55c` for the Classic Collection), so its names, numbering and rarities are the
official ones. Its secret rares run 129-158 and are followed by the three RGB Mew cards numbered
R, G and B; the API lists those three as Common, which is plainly wrong, so they carry the rarity
"RGB Mew" here. Classic Collection cards keep their original set numbers (Charizard 4, Misty 18). The MEP promos have their own set code and are not part of the 199; they sit in their own section
numbered MEP 094-109. The last four names - 095 Lucario, 100 Sylveon ex, 106 Ditto and 108 Espeon ex
- were read off the card pictures once Scrydex published them. Pokémon and the card names are trademarks of
Nintendo / Creatures Inc. / GAME FREAK inc.; this is a personal collection tracker.
