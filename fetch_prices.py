#!/usr/bin/env python3
"""Write prices.json: Cardmarket's trend prices for every card in the dex.

The card list is read straight out of index.html, so this never drifts from the
page. A set with a `tg` field sits whole inside one TCGdex set and is asked for
by that id; the others are matched segment by segment through their pictures. Prices come from TCGdex, which relays Cardmarket's own price guide: two
numbers per card, the plain print and the reverse holo. Cards no source prices yet -
Gem Pack Vol. 5, which nothing carries, and 30th Celebration, where TCGdex has
the fields but no figures in them - are simply left out, and appear by
themselves on the first run after the figures land.

Run it from the repository root:  python fetch_prices.py
"""
import json, os, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

API = 'https://api.tcgdex.net/v2/en/cards/'
GUIDE = 'https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json'
GALLERY = {'swsh9tg': 'swsh9tg', 'swsh10tg': 'swsh10tg', 'swsh11tg': 'swsh11tg',
           'swsh12tg': 'swsh12tg', 'swsh12pt5gg': 'swsh12.5gg', 'svp': 'svp',
           'swsh45sv': 'swsh4.5sv'}
WORKERS = 8


def find_page():
    for p in ('index.html', 'public/index.html'):
        if os.path.exists(p):
            return p
    sys.exit('index.html not found - run this from the repository root')


def read_sets(page):
    for line in open(page, encoding='utf-8'):
        if line.startswith('const SETS = '):
            return json.loads(line[len('const SETS = '):].rstrip().rstrip(';'))
    sys.exit('no SETS array in ' + page)


def tcgdex_id(seg, label, ix):
    a, b, host, path, pad = seg
    if host == 't':
        sid = path.split('/')[-1]
        return f"{sid}-{label.zfill(pad) if pad and label.isdigit() else label}"
    if host == 'p' and path in GALLERY:
        return f'{GALLERY[path]}-{label}'
    if host == 'o':                      # 30th Celebration's Classic Collection
        return f'30th-c-{str(ix - pad).zfill(3)}'
    return None


def fetch(cid):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(API + cid, timeout=45) as r:
                return (json.load(r).get('pricing') or {}).get('cardmarket')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
        time.sleep(1 + attempt * 2)
    return None


def main():
    page = find_page()
    sets = read_sets(page)
    out_path = os.path.join(os.path.dirname(page), 'prices.json')

    jobs = []
    for s in sets:
        tg = s.get('tg')
        if tg:                      # the whole set sits in one TCGdex set
            sid, pad = tg
            for ix, c in enumerate(s['cards'], 1):
                lbl = str(c[5]) if len(c) > 5 else str(c[0])
                jobs.append((s['key'], ix,
                             f"{sid}-{lbl.zfill(pad) if pad and lbl.isdigit() else lbl}"))
            continue
        for seg in s.get('img', []):
            for ix in range(seg[0], seg[1] + 1):
                c = s['cards'][ix - 1]
                lbl = str(c[5]) if len(c) > 5 else str(c[0])
                cid = tcgdex_id(seg, lbl, ix)
                if cid:
                    jobs.append((s['key'], ix, cid))
    print(f'{len(jobs)} cards to price', flush=True)

    done = [0]
    def one(job):
        key, ix, cid = job
        cm = fetch(cid)
        done[0] += 1
        if done[0] % 500 == 0:
            print(f'  {done[0]}/{len(jobs)}', flush=True)
        return key, ix, cm

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        rows = list(ex.map(one, jobs))

    out, stamp = {}, ''
    for key, ix, cm in rows:
        if not cm:
            continue
        stamp = max(stamp, cm.get('updated') or '')
        e = [cm.get('trend'), cm.get('trend-holo')]
        e = [round(v, 2) if isinstance(v, (int, float)) and v else None for v in e]
        while e and e[-1] is None:
            e.pop()
        if e and e[0] is not None:
            out.setdefault(key, {})[str(ix)] = e
    priced = sum(len(v) for v in out.values())

    # A set no relay carries yet is filled straight from Cardmarket's own
    # daily price guide. They publish it as one file per game - Pokémon is 6 -
    # and it is keyed on idProduct, so cardmarket-ids.json holds which product
    # belongs to which slot. Gaps only: the moment a relay starts answering for
    # a card, that figure wins and the guide is ignored for it. If the download
    # fails, prices-manual.json is the fallback so a set never silently empties.
    here = os.path.dirname(page)
    manual = {}

    def vul(rows, key, datum, tag):
        mine = out.setdefault(key, {})
        used = 0
        for ix, e in rows.items():
            if ix not in mine:
                mine[ix] = e
                used += 1
        if used:
            manual[key] = {'n': used, 'date': datum, 'tag': tag}
        return used

    kaart = {}
    kp = os.path.join(here, 'cardmarket-ids.json')
    if os.path.exists(kp):
        try:
            kaart = json.load(open(kp)).get('sets', {})
        except Exception as e:
            print('cardmarket-ids.json could not be read:', e, flush=True)

    gelukt = set()
    if kaart:
        try:
            req = urllib.request.Request(GUIDE, headers={'User-Agent': 'pokecard-dex'})
            with urllib.request.urlopen(req, timeout=180) as r:
                gids = json.load(r)
            prijs = {g['idProduct']: g for g in gids.get('priceGuides', [])}
            datum = (gids.get('createdAt') or '')[:10]
            print(f'Cardmarket price guide: {len(prijs)} rows, {datum}', flush=True)
            for key, slots in kaart.items():
                rows = {}
                for ix, idp in slots.items():
                    g = prijs.get(int(idp))
                    if not g:
                        continue
                    e = [g.get('trend'), g.get('trend-holo')]
                    e = [round(v, 2) if isinstance(v, (int, float)) and v else None for v in e]
                    while e and e[-1] is None:
                        e.pop()
                    if e and e[0] is not None:
                        rows[str(ix)] = e
                if rows and vul(rows, key, datum, 'Cardmarket'):
                    gelukt.add(key)
        except Exception as e:
            print('Cardmarket price guide unreachable:', e, flush=True)

    mp = os.path.join(here, 'prices-manual.json')
    if os.path.exists(mp):
        try:
            hand = json.load(open(mp))
            for key, rows in hand.get('sets', {}).items():
                if key not in gelukt:
                    vul(rows, key, hand.get('updated', ''), 'handmatig')
        except Exception as e:
            print('prices-manual.json could not be read:', e, flush=True)

    if manual:
        print('filled outside the relay: '
              + ', '.join(f'{k} {v["n"]} ({v["tag"]})' for k, v in manual.items()), flush=True)

    priced = sum(len(v) for v in out.values())

    # never trade a good file for a bad run
    if os.path.exists(out_path):
        try:
            was = json.load(open(out_path))
            had = sum(len(v) for v in was['sets'].values())
            had -= sum(m.get('n', 0) for m in (was.get('manual') or {}).values())
            if priced - sum(m['n'] for m in manual.values()) < had * 0.8:
                sys.exit(f'only {priced} prices against {had} before - leaving the file alone')
        except Exception:
            pass
    if priced < 1000:
        sys.exit(f'only {priced} prices came back - not writing the file')

    json.dump({'updated': stamp[:10], 'cur': 'EUR',
               'src': "Cardmarket price guide via TCGdex",
               'manual': manual, 'sets': out},
              open(out_path, 'w'), separators=(',', ':'))
    print(f'wrote {out_path}: {priced} prices in {len(out)} sets, '
          f'{round(os.path.getsize(out_path)/1024)} KB, dated {stamp[:10]}', flush=True)


if __name__ == '__main__':
    main()
