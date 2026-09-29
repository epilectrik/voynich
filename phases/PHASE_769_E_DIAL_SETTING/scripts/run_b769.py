#!/usr/bin/env python3
"""PHASE_769: is the e-run dial set per folio (or per paragraph) in Currier B? Run only after the lock.

Folio arm (primary): S3c on the H track, alpha 0.01, with the ZL transcription check at ZL_THRESHOLD.
Paragraph arm (co-primary or descriptive, fixed at lock): S3P on the H track, alpha 0.01, with the same ZL check.
Secondary / gate statistics: S3 (unadjusted), S3far, S3-dis, S3-int, S3-cons, S3c-k, S1, S3P-within, i-runs.
Descriptive: frame-controlled folio propensities, leaf correlation (C1977), S3c per stratum (S/3, B/2, other).
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ed769 as E  # noqa: E402
import ed769b as B  # noqa: E402

OUT = E.ROOT / 'phases/PHASE_769_E_DIAL_SETTING/results'
T0 = time.time()
LOCK = None                 # lock commit, filled at lock
ZL_THRESHOLD = 0.05         # fixed at lock: ZL power at sigma 0.35 = 0.91; ZL S3P power at 0.45 = 0.965
PARAGRAPH_ARM = 'co-primary'  # fixed at lock: S3P MDE80 about 0.45 (<= 0.6)
NPERM = 2000


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def arm_verdict(p_h, p_z, present_label):
    if p_h <= 0.01 and p_z <= ZL_THRESHOLD:
        return present_label
    if p_h > 0.05 and p_z > 0.05:
        return 'NO SETTING (bounded)'
    return 'INDETERMINATE'


def propensities(O, recs):
    m = O['informative']
    r = O['y'][m] - E.cell_means(O['y'][m], O['cell'][m])
    f = O['folio'][m]
    s = np.bincount(f, weights=r, minlength=len(O['folio_names']))
    n = np.bincount(f, minlength=len(O['folio_names']))
    meta = {}
    for rec in recs:
        meta.setdefault(rec[1], (rec[7], rec[8]))
    return {name: {'propensity': float(s[i] / n[i]), 'n': int(n[i]), 'section': meta[name][0], 'hand': meta[name][1]}
            for i, name in enumerate(O['folio_names']) if n[i] > 0}


def leaf_correlation(props, min_n=10):
    by = defaultdict(dict)
    for f, v in props.items():
        m = re.match(r'f(\d+)([rv])', f)
        if m and v['n'] >= min_n:
            by[int(m.group(1))].setdefault(m.group(2), []).append(v['propensity'])
    pairs = [(np.mean(d['r']), np.mean(d['v'])) for d in by.values() if 'r' in d and 'v' in d]
    if len(pairs) < 5:
        return {'n_pairs': len(pairs), 'r': None}
    a = np.array(pairs)
    return {'n_pairs': len(pairs), 'r': float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])}


def main():
    assert LOCK and ZL_THRESHOLD and PARAGRAPH_ARM, 'fill the lock constants first'
    res = {'pre_registration': LOCK, 'ZL_threshold': ZL_THRESHOLD, 'paragraph_arm': PARAGRAPH_ARM}
    recs = E.load_b_h()
    amap, leg = B.hf_alignment()
    O = B.add_structure(B.occurrences2(recs, 'e', amap))
    X = B.folio_covariates(recs, O, leg)
    recs_z = E.load_b_zl()
    Oz = B.add_structure(B.occurrences2(recs_z, 'e', None))
    Xz = B.folio_covariates(recs_z, Oz, leg)
    res['informative'] = {'H': int(O['informative'].sum()), 'H_total': len(O['y']), 'ZL': int(Oz['informative'].sum())}
    log('H battery (primary)')
    res['H'] = B.Battery(O, X).evaluate(O['y'], nperm=NPERM, seed=769)
    log('H S3P-within')
    res['H_S3P_within'] = B.Battery(O, X).evaluate(O['y'], nperm=NPERM, seed=770, stats=('S3P',),
                                                  within_folio_para=True)
    log('ZL transcription check')
    res['ZL'] = B.Battery(Oz, Xz).evaluate(Oz['y'], nperm=NPERM, seed=771, stats=('S3c', 'S3P'))
    for name, sub in (('int', ~O['final']), ('cons', O['cons']), ('k', O['after_k'])):
        log(f'subset {name}')
        res[f'H_{name}'] = B.Battery(O, X, subset=sub, paragraph=False).evaluate(O['y'], nperm=NPERM, seed=772,
                                                                                 stats=('S3c',))
    h, z = res['H'], res['ZL']
    res['folio_verdict'] = arm_verdict(h['p_S3c'], z['p_S3c'], 'FOLIO-LEVEL SETTING PRESENT')
    res['paragraph_verdict'] = (arm_verdict(h['p_S3P'], z['p_S3P'], 'PROCEDURE-SCALE SETTING PRESENT')
                                if PARAGRAPH_ARM == 'co-primary' else 'descriptive only')
    res['picture_gate'] = bool(h['p_S3dis'] <= 0.05 and res['H_int']['p_S3c'] <= 0.05 and res['H_cons']['p_S3c'] <= 0.05)
    log(f"FOLIO ARM: S3c {h['S3c']:+.3f} (null {h['S3c_null_mean']:+.3f} sd {h['S3c_null_sd']:.3f}) p {h['p_S3c']:.4f}; "
        f"ZL p {z['p_S3c']:.4f} -> {res['folio_verdict']}")
    log(f"PARAGRAPH ARM: S3P p {h['p_S3P']:.4f}; ZL p {z['p_S3P']:.4f}; within-folio p {res['H_S3P_within']['p_S3P']:.4f} "
        f"-> {res['paragraph_verdict']}")
    log('secondary:', {k: round(v, 4) for k, v in h.items() if k.startswith('p_')},
        {f'{n}_p_S3c': round(res[f'H_{n}']['p_S3c'], 4) for n in ('int', 'cons', 'k')}, 'picture gate', res['picture_gate'])
    # i-runs (interpretation conditional on the minim kappa, reported separately)
    Oi = B.add_structure(B.occurrences2(recs, 'i', amap))
    res['H_i'] = B.Battery(Oi, B.folio_covariates(recs, Oi, leg), paragraph=False).evaluate(
        Oi['y'], nperm=NPERM, seed=773, stats=('S1', 'S3c'))
    # descriptives
    props = propensities(O, recs)
    res['folio_propensity'] = props
    res['leaf_correlation'] = leaf_correlation(props)
    strata = {'S/3': [], 'B/2': [], 'other': []}
    for i, f in enumerate(O['folio_names']):
        sec, hand = props.get(f, {}).get('section'), props.get(f, {}).get('hand')
        strata['S/3' if (sec, hand) == ('S', '3') else ('B/2' if (sec, hand) == ('B', '2') else 'other')].append(i)
    res['stratum_S3c'] = {}
    for sname, idx in strata.items():
        sub = np.isin(O['folio'], idx)
        if (sub & O['informative']).sum() > 200:
            r = B.Battery(O, X, subset=sub, paragraph=False).evaluate(O['y'], nperm=NPERM, seed=774, stats=('S3c',))
            res['stratum_S3c'][sname] = {k: r[k] for k in ('S3c', 'p_S3c', 'n_occ', 'n_folios')}
    log('leaf correlation:', res['leaf_correlation'], '| strata:', res['stratum_S3c'])
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'e_dial_B.json', 'w'), indent=1, default=float)
    log('done')


if __name__ == '__main__':
    main()
