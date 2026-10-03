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
GALLERY = {'swsh9tg': 'swsh9tg', 'swsh10tg': 'swsh10tg', 'swsh11tg': 'swsh11tg',
           'swsh12tg': 'swsh12tg', 'swsh12pt5gg': 'swsh12.5gg', 'svp': 'svp'}
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

    # never trade a good file for a bad run
    if os.path.exists(out_path):
        try:
            had = sum(len(v) for v in json.load(open(out_path))['sets'].values())
            if priced < had * 0.8:
                sys.exit(f'only {priced} prices against {had} before - leaving the file alone')
        except Exception:
            pass
    if priced < 1000:
        sys.exit(f'only {priced} prices came back - not writing the file')

    json.dump({'updated': stamp[:10], 'cur': 'EUR',
               'src': "Cardmarket price guide via TCGdex", 'sets': out},
              open(out_path, 'w'), separators=(',', ':'))
    print(f'wrote {out_path}: {priced} prices in {len(out)} sets, '
          f'{round(os.path.getsize(out_path)/1024)} KB, dated {stamp[:10]}', flush=True)


if __name__ == '__main__':
    main()
