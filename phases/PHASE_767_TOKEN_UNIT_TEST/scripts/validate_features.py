#!/usr/bin/env python3
"""PHASE_767 pre-lock feature validation from CONTROL corpora only (results/calibration_controls.json).

Syllable index per feature: s_f(x) = (x - m_W) / (m_S - m_W), m_W / m_S = medians of the five word-written / syllable-
written training texts. A feature is valid if (a) SYL - WORD has the same sign in all five language pairs, (b) both
native syllable-written texts have s_f > 0.5, (c) at least 12 of the 15 held-out word-written texts have s_f < 0.5.
Also runs the leave-one-pair-out check on the valid set. Currier B is not read.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tu767 as T  # noqa: E402

OUT = T.ROOT / 'phases/PHASE_767_TOKEN_UNIT_TEST/results'
LANGS = list(T.EU)


def axes(cal, feats, langs):
    ax = {}
    for f in feats:
        mW = float(np.median([cal[f'WORD_{l}']['features'][f] for l in langs]))
        mS = float(np.median([cal[f'SYL_{l}']['features'][f] for l in langs]))
        ax[f] = (mW, mS)
    return ax


def s_index(x, ax_f):
    mW, mS = ax_f
    return (x - mW) / (mS - mW)


def validate(cal, natives=('NAT_pinyin_tones', 'NAT_vietnamese'), min_heldout=12):
    feats = T.FEATURES
    ax = axes(cal, feats, LANGS)
    how = [k for k in cal if k.startswith('HOW_')]
    table = {}
    for f in feats:
        sgn = np.sign(ax[f][1] - ax[f][0])
        pairs_ok = all(np.sign(cal[f'SYL_{l}']['features'][f] - cal[f'WORD_{l}']['features'][f]) == sgn
                       for l in LANGS)
        nat = {n: s_index(cal[n]['features'][f], ax[f]) for n in natives}
        ho = {n: s_index(cal[n]['features'][f], ax[f]) for n in how}
        n_ok = sum(v < 0.5 for v in ho.values())
        valid = bool(pairs_ok and all(v > 0.5 for v in nat.values()) and n_ok >= min_heldout)
        table[f] = {'m_W': ax[f][0], 'm_S': ax[f][1], 'pairs_same_sign': pairs_ok,
                    'natives': {k: round(v, 3) for k, v in nat.items()},
                    'heldout_word_side': f'{n_ok}/{len(ho)}',
                    'heldout_failures': {k: round(v, 3) for k, v in ho.items() if v >= 0.5}, 'valid': valid}
    return table


def lopo(cal, fstar):
    """Leave-one-pair-out: axes from four pairs; classify the held-out pair's WORD and SYL by mean clipped index."""
    out = {}
    for l in LANGS:
        ax = axes(cal, fstar, [x for x in LANGS if x != l])
        for kind in ('WORD', 'SYL'):
            s = np.mean([np.clip(s_index(cal[f'{kind}_{l}']['features'][f], ax[f]), -1, 2) for f in fstar])
            out[f'{kind}_{l}'] = {'S': round(float(s), 3), 'correct': bool((s > 0.5) == (kind == 'SYL'))}
    return out


def main():
    cal = json.load(open(OUT / 'calibration_controls.json'))
    table = validate(cal)
    fstar = [f for f, v in table.items() if v['valid']]
    lo = lopo(cal, fstar) if fstar else {}
    ax = axes(cal, fstar, LANGS)
    mean_idx = {k: round(float(np.mean([np.clip(s_index(v['features'][f], ax[f]), -1, 2) for f in fstar])), 3)
                for k, v in cal.items() if v['features']}
    res = {'validation': table, 'F_star': fstar, 'leave_one_pair_out': lo,
           'lopo_correct': sum(v['correct'] for v in lo.values()), 'mean_index_controls': mean_idx}
    # variant V3: Pinyin without tones as the native
    t3 = validate(cal, natives=('NAT_pinyin_notones', 'NAT_vietnamese'))
    res['V3_validation_F_star'] = [f for f, v in t3.items() if v['valid']]
    json.dump(res, open(OUT / 'feature_validation.json', 'w'), indent=1)
    for f, v in table.items():
        print(f, 'VALID' if v['valid'] else 'invalid', '| pairs', v['pairs_same_sign'], '| natives', v['natives'],
              '| held-out word-side', v['heldout_word_side'], v['heldout_failures'])
    print('F* =', fstar, '| LOPO correct', res['lopo_correct'], '/ 10', '| V3 F* =', res['V3_validation_F_star'])
    for k, v in sorted(mean_idx.items(), key=lambda kv: kv[1]):
        print(f'  {k:28s} {v:+.3f}')


if __name__ == '__main__':
    main()
