#!/usr/bin/env python3
"""PHASE_769: summarise the pre-lock calibration (results/calib/*.json) into power tables with Wilson intervals,
verdict probabilities for the folio arm (joint H + ZL), the ZL threshold rule, the paragraph-arm MDE, and the
specificity checks (LOCAL, WORDSPEC, DRIFT, COPY, SHARED_K, negative texts, minim kappa). Controls only."""
from __future__ import annotations

import glob
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich/phases/PHASE_769_E_DIAL_SETTING/results')


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def power(ps, a):
    ps = np.asarray(ps, dtype=float)
    k = int((ps <= a).sum())
    return {'power': round(k / len(ps), 3), 'wilson95': wilson(k, len(ps)), 'n': len(ps)}


def main():
    C = {Path(f).stem: json.load(open(f)) for f in glob.glob(str(ROOT / 'calib/*.json'))}
    out = {'conditions': sorted(C)}
    tables = {}
    for name, d in sorted(C.items()):
        if not d.get('reps'):
            continue
        reps = d['reps']
        t = {}
        for s in ('S1', 'S3', 'S3c', 'S3far', 'S3dis', 'S3P'):
            ps = [r['H'][f'p_{s}'] for r in reps if f'p_{s}' in r['H']]
            if ps:
                t[s] = {'a01': power(ps, 0.01), 'a05': power(ps, 0.05),
                        'mean_stat': float(np.nanmean([r['H'][s] for r in reps if s in r['H']]))}
        for sub in ('ZL', 'int', 'cons', 'k'):
            if sub in reps[0]:
                ps = [r[sub]['p_S3c'] for r in reps]
                t[f'S3c_{sub}'] = {'a01': power(ps, 0.01), 'a05': power(ps, 0.05), 'a10': power(ps, 0.10)}
        if 'H_S3P_within' in reps[0]:
            ps = [r['H_S3P_within']['p_S3P'] for r in reps]
            t['S3P_within'] = {'a01': power(ps, 0.01), 'a05': power(ps, 0.05)}
        tables[name] = t
    out['power'] = tables
    # folio-arm verdict probabilities (joint H + ZL) and the ZL threshold rule
    zl035 = C.get('SHARED_0.35')
    if zl035 and zl035.get('reps'):
        pz = np.array([r['ZL']['p_S3c'] for r in zl035['reps']])
        zl_power = float((pz <= 0.05).mean())
        z_thr = 0.05 if zl_power >= 0.80 else 0.10
        out['ZL_rule'] = {'ZL_power_at_sigma_0.35_(0.05)': zl_power, 'wilson95': wilson(int((pz <= 0.05).sum()), len(pz)),
                          'ZL_check_threshold': z_thr, 'zl_informative': zl035.get('zl_informative')}
        vp = {}
        for s in ('SHARED_0', 'SHARED_0.25', 'SHARED_0.35', 'SHARED_0.5'):
            d = C.get(s)
            if not d or not d.get('reps'):
                continue
            ph = np.array([r['H']['p_S3c'] for r in d['reps']])
            pzz = np.array([r['ZL']['p_S3c'] for r in d['reps']])
            pres = (ph <= 0.01) & (pzz <= z_thr)
            no = (ph > 0.05) & (pzz > 0.05)
            gate = np.array([(r['H']['p_S3dis'] <= 0.05) and (r['int']['p_S3c'] <= 0.05) and (r['cons']['p_S3c'] <= 0.05)
                             for r in d['reps']])
            vp[s] = {'P_PRESENT': round(float(pres.mean()), 3), 'P_NO': round(float(no.mean()), 3),
                     'P_INDETERMINATE': round(float(1 - pres.mean() - no.mean()), 3),
                     'P_not_NO': round(float(1 - no.mean()), 3),
                     'P_PRESENT_and_picture_gate': round(float((pres & gate).mean()), 3)}
        out['folio_verdict_probabilities'] = vp
    # paragraph arm MDE (S3P at 0.01 under SHARED_PARA)
    para = {}
    for s in ('SHARED_PARA_0.35', 'SHARED_PARA_0.5', 'SHARED_PARA_0.7'):
        if s in tables and 'S3P' in tables[s]:
            para[s] = {'S3P_a01': tables[s]['S3P']['a01'], 'S3P_within_a01': tables[s].get('S3P_within', {}).get('a01')}
    out['paragraph_arm'] = para
    # drift diagnostic: S3far / S3c mean ratio under SHARED vs DRIFT
    ratio = {}
    for s in ('SHARED_0.35', 'SHARED_0.5', 'DRIFT_0.35'):
        if s in tables and 'S3far' in tables[s]:
            ratio[s] = {'mean_S3c': tables[s]['S3c']['mean_stat'], 'mean_S3far': tables[s]['S3far']['mean_stat']}
    out['drift_diagnostic'] = ratio
    if 'NEG_TEXT' in C:
        out['negative_texts'] = {k: {x: v[x] for x in v if x.startswith('p_') or x in ('S3c', 'n_occ')}
                                 for k, v in C['NEG_TEXT'].get('controls', {}).items()}
    if 'KAPPA_MINIMS' in C:
        out['minim_kappa'] = {k: C['KAPPA_MINIMS'][k] for k in ('kappa', 'n', 'confusion_[H1|H2+][F1|F2+]')
                              if k in C['KAPPA_MINIMS']}
    json.dump(out, open(ROOT / 'prelock_calibration_summary.json', 'w'), indent=1)
    # printed digest
    for name, t in tables.items():
        line = ' | '.join(f"{s} {v['a01']['power']:.2f}/{v['a05']['power']:.2f}" for s, v in t.items()
                          if isinstance(v, dict) and 'a01' in v)
        print(f'{name:18s} power(.01/.05): {line}')
    for k in ('ZL_rule', 'folio_verdict_probabilities', 'paragraph_arm', 'drift_diagnostic', 'negative_texts',
              'minim_kappa'):
        if k in out:
            print(f'== {k}:', json.dumps(out[k], indent=None)[:1500])


if __name__ == '__main__':
    main()
