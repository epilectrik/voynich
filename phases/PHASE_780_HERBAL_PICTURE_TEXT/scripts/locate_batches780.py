#!/usr/bin/env python3
"""Write the locator batch lists (no coding): V page images (anonymised codes) and Brunschwig woodcut pages."""
import json
import random
from collections import defaultdict
from pathlib import Path

PH = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT')
CODE_DIR = Path('C:/git/voynich/external/phase780_coding')
rng = random.Random(780_002)

key = json.load(open(PH / 'data/key_v.json', encoding='utf-8'))
codes = sorted(key)
rng.shuffle(codes)
nb = 4
for b in range(nb):
    batch = codes[b::nb]
    json.dump({'images': [str(CODE_DIR / 'v' / f'{c}.jpg') for c in batch], 'out': str(CODE_DIR / f'locate_v_{b + 1}.json')},
              open(CODE_DIR / f'locate_v_batch_{b + 1}.json', 'w', encoding='utf-8'), indent=1)
print('V locator batches:', [len(codes[b::nb]) for b in range(nb)])

E = json.load(open(PH / 'data/entries_br_all.json', encoding='utf-8'))
by = defaultdict(list)
for e in E:
    by[e['woodcut_page']].append(e)
pages = sorted(by)
rng.shuffle(pages)
nb = 3
for b in range(nb):
    items = []
    for p in sorted(pages[b::nb]):
        ents = sorted(by[p], key=lambda e: e['head_line'])
        items.append({'page': p, 'image': f'C:/git/voynich/sources/brunschwig_1500/pages/page_{p:03d}.png',
                      'expected_woodcuts': len(ents),
                      'entries': [{'entry_idx': e['idx'], 'heading': e['heading']} for e in ents]})
    json.dump({'pages': items, 'out': str(CODE_DIR / f'locate_br_{b + 1}.json')},
              open(CODE_DIR / f'locate_br_batch_{b + 1}.json', 'w', encoding='utf-8'), indent=1)
print('BR locator batches (pages):', [len(pages[b::nb]) for b in range(nb)])
