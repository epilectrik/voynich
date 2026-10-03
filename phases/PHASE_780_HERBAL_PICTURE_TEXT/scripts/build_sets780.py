#!/usr/bin/env python3
"""PHASE_780 data sets (no text statistic is computed here).

  python build_sets780.py pages      Voynich page lists (V-A1, V-B2) with quire, binding position, leaf, token count and
                                     scan file -> data/pages_v.json
  python build_sets780.py vimages    anonymised, downscaled page images for the coders -> CODE_DIR/v/<code>.jpg;
                                     key -> data/key_v.json (never shown to coders)
  python build_sets780.py brentries  Brunschwig 1500 Part 2 entries with a woodcut annotation, the page of the woodcut
                                     and the entry text span -> data/entries_br_all.json

Page metadata only: token counts are the only text-derived values (lengths, used for covariates and truncation)."""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path('C:/git/voynich')
PH = ROOT / 'phases/PHASE_780_HERBAL_PICTURE_TEXT'
DATA = PH / 'data'
CODE_DIR = Path('C:/git/voynich/external/phase780_coding')     # gitignored (external/); images for the coders
SEED = 780_001
EXCLUDE = {'f90r1', 'f90r2', 'f90v1', 'f90v2'}                  # foldout panels without a panel-level scan mapping


def folio_key(f):
    m = re.match(r'f(\d+)([rv])(\d*)', f)
    return int(m.group(1)), m.group(2), int(m.group(3) or 0)


def pages():
    import pandas as pd
    df = pd.read_csv(ROOT / 'data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['section'] == 'H')]
    df = df[df['placement'].fillna('').str.startswith('P')]
    df = df[df['word'].fillna('').str.strip() != '']
    df = df[~df['word'].str.contains(r'\*', regex=True)]
    meta = df.groupby('folio').agg(lang=('language', 'first'), dhand=('d.hand', 'first'), quire=('quire', 'first'),
                                   n=('word', 'size'))
    fm = json.load(open(ROOT / 'sources/voynich_scans/folio_mapping.json', encoding='utf-8'))
    canvas = {}
    for m in fm['mappings']:
        f = m.get('project_folio')
        if f and m.get('mapping_type') == 'SIMPLE' and m.get('in_project_transcript', True) is not False:
            canvas.setdefault(f, m['file'].replace('\\', '/'))
    out = []
    for f, r in meta.iterrows():
        arm = 'V-A1' if (r['lang'] == 'A' and str(r['dhand']) == '1') else ('V-B2' if (r['lang'] == 'B' and str(r['dhand']) == '2') else None)
        if arm is None:
            continue
        num, side, panel = folio_key(f)
        rec = {'folio': f, 'arm': arm, 'quire': r['quire'], 'leaf': num, 'side': side, 'panel': panel,
               'pos': 2 * num + (0 if side == 'r' else 1), 'n_tokens': int(r['n']),
               'scan': canvas.get(f), 'excluded': f in EXCLUDE}
        if rec['scan'] is None and not rec['excluded']:
            rec['excluded'] = True
            rec['exclude_reason'] = 'no single-page scan mapping'
        elif rec['excluded']:
            rec['exclude_reason'] = 'foldout panel without a panel-level scan mapping'
        out.append(rec)
    out.sort(key=lambda d: (d['arm'], d['leaf'], d['side'], d['panel']))
    json.dump(out, open(DATA / 'pages_v.json', 'w', encoding='utf-8'), indent=1)
    for arm in ('V-A1', 'V-B2'):
        inc = [d for d in out if d['arm'] == arm and not d['excluded']]
        exc = [d['folio'] for d in out if d['arm'] == arm and d['excluded']]
        print(arm, 'included', len(inc), 'excluded', exc)


def vimages():
    from PIL import Image
    recs = [d for d in json.load(open(DATA / 'pages_v.json', encoding='utf-8')) if not d['excluded']]
    rng = random.Random(SEED)
    codes = rng.sample(range(1000, 9999), len(recs))
    (CODE_DIR / 'v').mkdir(parents=True, exist_ok=True)
    key = {}
    for d, c in zip(recs, codes):
        code = f'V{c}'
        im = Image.open(ROOT / 'sources/voynich_scans' / d['scan']).convert('RGB')
        s = 2000 / max(im.size)
        if s < 1:
            im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
        im.save(CODE_DIR / 'v' / f'{code}.jpg', quality=90)
        key[code] = {'folio': d['folio'], 'arm': d['arm']}
    json.dump(key, open(DATA / 'key_v.json', 'w', encoding='utf-8'), indent=1)
    print('wrote', len(key), 'images to', CODE_DIR / 'v')


def brentries():
    L = open(ROOT / 'sources/brunschwig_1500/brunschwig_1500_corrected.txt', encoding='utf-8').read().split('\n')
    start = next(i for i, ln in enumerate(L) if re.match(r'^Das\. i\. capitel', ln.strip(), re.I) or 'capitel dis an' in ln) \
        if any('capitel dis an' in ln for ln in L) else 0
    page, chapter = None, None
    heads = []
    for i, ln in enumerate(L):
        m = re.match(r'^--- Page (\d+)', ln)
        if m:
            page = int(m.group(1))
        mc = re.search(r'buchstaben\.?\s*([A-Z])\b', ln)
        if mc:
            chapter = mc.group(1)
        if re.match(r'^Von .{2,80}wasser\.?\s*$', ln.strip()):
            heads.append({'line': i, 'page': page, 'heading': ln.strip(), 'chapter': chapter})
    ents = []
    for k, h in enumerate(heads):
        end = heads[k + 1]['line'] if k + 1 < len(heads) else len(L)
        wc = [(j, L[j]) for j in range(h['line'] + 1, min(end, h['line'] + 6)) if L[j].startswith('[WOODCUT')]
        if not wc:
            continue
        wpage = h['page']
        for j in range(h['line'], wc[0][0]):
            m = re.match(r'^--- Page (\d+)', L[j])
            if m:
                wpage = int(m.group(1))
        ents.append({'idx': len(ents), 'heading': h['heading'], 'chapter': h['chapter'], 'head_line': h['line'],
                     'end_line': end, 'woodcut_line': wc[0][0], 'woodcut_page': wpage,
                     'woodcut_note_for_locator_only': wc[0][1][:160]})
    json.dump(ents, open(DATA / 'entries_br_all.json', 'w', encoding='utf-8'), indent=1)
    print('entries with a woodcut annotation:', len(ents), 'of', len(heads), 'headings; chapters',
          sorted({e['chapter'] for e in ents if e['chapter']}))
    from collections import Counter
    print('woodcuts per page:', Counter(Counter(e['woodcut_page'] for e in ents).values()))


if __name__ == '__main__':
    DATA.mkdir(exist_ok=True)
    {'pages': pages, 'vimages': vimages, 'brentries': brentries}[sys.argv[1]]()
