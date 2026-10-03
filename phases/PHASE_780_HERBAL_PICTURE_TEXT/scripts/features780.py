#!/usr/bin/env python3
"""PHASE_780 page features (text only; no picture is read): length, layout and spelling-dial shares per V page, used as
pair covariates. Drawing breaks are counted on the ZL transliteration with PHASE_771's loader; everything else on the
H track (P placement, certain tokens).  -> data/page_features_v.json"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path('C:/git/voynich')
PH = ROOT / 'phases/PHASE_780_HERBAL_PICTURE_TEXT'
sys.path.insert(0, str(ROOT / 'phases/PHASE_771_LABEL_O_AND_DRAWING_BREAKS/scripts'))
import zl771 as Z  # noqa: E402

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')


def main():
    pages = [d for d in json.load(open(PH / 'data/pages_v.json', encoding='utf-8')) if not d['excluded']]
    folios = [d['folio'] for d in pages]
    df = pd.read_csv(ROOT / 'data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['folio'].isin(folios))]
    df = df[df['placement'].fillna('').str.startswith('P')]
    df = df[df['word'].fillna('').str.strip() != '']
    df = df[~df['word'].str.contains(r'\*', regex=True)]
    brk = Counter()
    for r in Z.load():
        if r['folio'] in folios and r['kind'].startswith('P'):
            brk[r['folio']] += max(len(r['segments']) - 1, 0)
    out = {}
    for f in folios:
        g = df[df['folio'] == f]
        words = list(g['word'])
        n = len(words)
        nl = g['line_number'].nunique()
        starts = int((g['line_initial'].astype(int) == 1).sum())
        ends = int((g['line_final'].astype(int) == 1).sum())
        npar = int((g['par_initial'].astype(int) == 1).sum())
        e_any = sum(1 for w in words if 'e' in w)
        e2 = sum(1 for w in words if 'ee' in w)
        units = Counter(u for w in words for u in GLYPH_RE.findall(w))
        minim_any = sum(1 for w in words if re.search(r'i+[nrlm]|i', w))
        minim2 = sum(1 for w in words if 'ii' in w)
        k = units['k'] + units['ckh']
        t = units['t'] + units['cth']
        ch, sh = units['ch'], units['sh']
        out[f] = {'n_tokens': n, 'n_lines': int(nl), 'tokens_per_line': n / max(nl, 1),
                  'line_edge_share': (starts + ends + 2 * brk[f]) / max(n, 1), 'n_breaks_zl': int(brk[f]),
                  'n_paragraphs': npar,
                  'e2_share': e2 / e_any if e_any else float('nan'),
                  'minim2_share': minim2 / minim_any if minim_any else float('nan'),
                  'k_share': k / (k + t) if (k + t) else float('nan'),
                  'ch_share': ch / (ch + sh) if (ch + sh) else float('nan')}
    json.dump(out, open(PH / 'data/page_features_v.json', 'w', encoding='utf-8'), indent=1)
    vals = pd.DataFrame(out).T
    print(vals.describe().T[['count', 'mean', 'min', 'max']].round(3).to_string())


if __name__ == '__main__':
    main()
