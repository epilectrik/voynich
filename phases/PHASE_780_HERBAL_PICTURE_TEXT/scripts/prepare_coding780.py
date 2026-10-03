#!/usr/bin/env python3
"""PHASE_780 coding images and batches (after the locators; no coding, no text statistic).

  python prepare_coding780.py

- V: masked images (grey outside the locator polygon and over its text boxes), cropped to the polygon's bounding box
  plus a margin; drawing height = polygon height / page height. Pages flagged main_plant = no are excluded.
- BR: woodcut crops from the locator boxes; duplicate blocks by difference hash (Hamming distance <= HASH_MAX on a
  9x8 dHash of the crop) keep one entry per block (seeded); entries under 41 cleaned words excluded.
- Fresh random codes for every image; coding batches for sets A and B drawn independently; keys and geometry saved.
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PH = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT')
DATA = PH / 'data'
CODE_DIR = Path('C:/git/voynich/external/phase780_coding')
sys.path.insert(0, str(PH / 'scripts'))
import core780 as K  # noqa: E402

SEED = 780_003
HASH_MAX = 6
MARGIN = 20
GREY = (128, 128, 128)
N_BATCH_V, N_BATCH_BR = 4, 4


def dhash(im, size=8):
    g = np.asarray(im.convert('L').resize((size + 1, size), Image.LANCZOS), dtype=float)
    return (g[:, 1:] > g[:, :-1]).flatten()


def main():
    rng = random.Random(SEED)
    key_v = json.load(open(DATA / 'key_v.json', encoding='utf-8'))
    loc_v = {}
    for p in sorted(CODE_DIR.glob('locate_v_[0-9].json')):
        loc_v.update(json.load(open(p, encoding='utf-8')))
    missing = [c for c in key_v if c not in loc_v]
    assert not missing, f'locator output missing for {missing}'
    (CODE_DIR / 'code').mkdir(exist_ok=True)
    geometry, items = {}, []
    excluded_noplant = []
    for c, info in sorted(key_v.items()):
        L = loc_v[c]
        if str(L.get('main_plant', 'yes')).lower() != 'yes':
            excluded_noplant.append(info['folio'])
            continue
        im = Image.open(CODE_DIR / 'v' / f'{c}.jpg').convert('RGB')
        w, h = im.size
        poly = [tuple(map(float, pt)) for pt in L['polygon']]
        mask = Image.new('L', (w, h), 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        for b in L.get('text_boxes', []) or []:
            ImageDraw.Draw(mask).rectangle(b, fill=0)
        out = Image.composite(im, Image.new('RGB', (w, h), GREY), mask)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        box = (max(0, int(min(xs)) - MARGIN), max(0, int(min(ys)) - MARGIN), min(w, int(max(xs)) + MARGIN), min(h, int(max(ys)) + MARGIN))
        items.append(('V', info['folio'], info['arm'], out.crop(box)))
        geometry[info['folio']] = {'drawing_height': (max(ys) - min(ys)) / h, 'n_plants_locator': L.get('n_plants'),
                                   'locator_notes': L.get('notes', '')}
    # BR
    E = {e['idx']: e for e in json.load(open(DATA / 'entries_br_all.json', encoding='utf-8'))}
    texts = dict(zip(E, K.br_texts([E[i] for i in E])))
    loc_br = {}
    for p in sorted(CODE_DIR.glob('locate_br_[0-9].json')):
        loc_br.update(json.load(open(p, encoding='utf-8')))
    crops, notes = {}, {}
    for page, L in loc_br.items():
        im = Image.open(f'C:/git/voynich/sources/brunschwig_1500/pages/page_{int(page):03d}.png').convert('RGB')
        for wc in L.get('woodcuts', []):
            i = int(wc['entry_idx'])
            if i in crops:
                notes[i] = 'two boxes for one entry; first kept'
                continue
            x0, y0, x1, y1 = map(int, wc['box'])
            crops[i] = (im.crop((x0, y0, x1, y1)), (y1 - y0) / im.size[1], wc.get('contains_text', 'no'))
    elig = [i for i in sorted(crops) if len(texts[i]) >= 41]
    short = [i for i in sorted(crops) if len(texts[i]) < 41]
    dup = json.load(open(DATA / 'br_duplicates.json', encoding='utf-8'))['confirmed_same_block']
    groups, used = [], set()
    for pair in dup:                                   # visually confirmed reused blocks (data/br_duplicates.json)
        g = [j for j in pair if j in elig]
        if g:
            groups.append(g)
            used.update(g)
    groups += [[i] for i in elig if i not in used]
    keep = sorted(rng.choice(g) for g in groups)
    dup_dropped = sorted(set(elig) - set(keep))
    entries_br = [dict(E[i], n_words=len(texts[i]), woodcut_height=crops[i][1], locator_text_flag=crops[i][2]) for i in keep]
    json.dump(entries_br, open(DATA / 'entries_br.json', 'w', encoding='utf-8'), indent=1)
    for i in keep:
        items.append(('BR', i, 'BR', crops[i][0]))
        geometry[f'BR{i}'] = {'drawing_height': crops[i][1]}
    # codes and batches
    codes = rng.sample(range(10000, 99999), len(items))
    key = {}
    for (corp, ident, arm, img), c in zip(items, codes):
        code = f'P{c}'
        img.save(CODE_DIR / 'code' / f'{code}.jpg', quality=92)
        key[code] = {'corpus': corp, 'id': ident, 'arm': arm}
    json.dump(key, open(DATA / 'key_code.json', 'w', encoding='utf-8'), indent=1)
    json.dump(geometry, open(DATA / 'geometry.json', 'w', encoding='utf-8'), indent=1)
    for cset in ('A', 'B'):
        r = random.Random(SEED + (1 if cset == 'A' else 2))
        for corp, nb in (('V', N_BATCH_V), ('BR', N_BATCH_BR)):
            cs = [c for c, k in key.items() if k['corpus'] == corp]
            r.shuffle(cs)
            for b in range(nb):
                json.dump({'codebook': str(CODE_DIR / f'codebook_{cset}.md'),
                           'images': [str(CODE_DIR / 'code' / f'{c}.jpg') for c in cs[b::nb]],
                           'out': str(CODE_DIR / f'codes_{cset}_{corp}_{b + 1}.json')},
                          open(CODE_DIR / f'batch_{cset}_{corp}_{b + 1}.json', 'w', encoding='utf-8'), indent=1)
    summary = {'V_coded': sum(1 for k in key.values() if k['corpus'] == 'V'),
               'V_excluded_no_main_plant': excluded_noplant,
               'BR_located': len(crops), 'BR_short_under_41': short, 'BR_duplicate_blocks_dropped': dup_dropped,
               'BR_eligible': len(keep), 'BR_notes': {str(k): v for k, v in notes.items()},
               'BR_entries_without_crop': sorted(set(E) - set(crops))}
    json.dump(summary, open(DATA / 'prepare_summary.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(summary, indent=1)[:2000])


if __name__ == '__main__':
    main()
