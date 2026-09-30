#!/usr/bin/env python3
"""PHASE_770 negative-text controls v3 (controls only; lean-expert and expert-advisor v2 checks). neg770.py (v2 panel,
results/calib/neg.json) is kept for provenance.

Controls: Timm-Schinner self-citation output (50 members; it produces folio components by copying and may produce
continuity across page turns) and the habit3b local-rule generator fitted to B (3 members). Naibbe dropped (no page
state; lean-expert v2 check). The generators produce PHASE_769's 80-folio skeleton; for the 81-folio analysis set, f76r's
tokens are filled from a second stream of the same generator (a contiguous segment), inserted at f76r's place.
For each control, every arm on the analysis set:
  Arm 0   S3c on the context-adjusted outcome (additive within-folio adjustment), with its within-cell null
  Arm A   S3c, S3far, the A1 features, the v3 classifier verdict (bank v3_H81_770), A3 p
  Arm B   per dial (CS, KTH, MIN): B1 own S3c and p; B2 X with the pairing null; B3 with the pairing null
  Arm C   K (reading order) with null (b) (per chain) and (a) (per transition), the Q13 / Q20 signs, face K
A control 'fires' a test when p <= 0.01. Output: results/calib/neg_v3.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/scripts'))
import cal770 as C  # noqa: E402
import calB770 as CB  # noqa: E402
import cal0_770 as C0  # noqa: E402

OUT = HERE.parent / 'results/calib'
NPERM = 500
BANK_TAG = 'v3_H81_770'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def perm_p(St, yy, stat, nperm, seed):
    """Observed statistic (on residuals of yy, informative occurrences) and its within-cell permutation p."""
    rng = np.random.default_rng(seed)
    cm = C.E.cell_means(yy, St.cell)
    R0 = (yy - cm)[:, None]
    o = float(stat(R0)[0])
    if not np.isfinite(o):
        return o, 1.0, R0
    null = []
    for _ in range(0, nperm, 250):
        Yp = C.B.perm_batch(yy, St.cell, 250, rng)
        null.append(stat((Yp - cm[None, :]).T))
    null = np.concatenate(null)
    return o, float((1 + (null >= o).sum()) / (1 + nperm)), R0


def stream81(stream80, extra, recs81):
    """Insert f76r's tokens (from a second stream) at f76r's place in manuscript order."""
    i76 = [i for i, r in enumerate(recs81) if r[1] == 'f76r']
    pos, n76 = i76[0], len(i76)
    return list(stream80[:pos]) + list(extra[1000:1000 + n76]) + list(stream80[pos:])


def main():
    import hr768 as HR
    import hr768v2 as V
    import clf770 as K
    OUT.mkdir(parents=True, exist_ok=True)
    base = C.Analysis('E')
    recs81 = base.recs
    amap_leg = (None, base.leg)
    sk = HR.b_skeleton()
    flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
    members = [('TIMM', 770300 + i) for i in range(50)] + [('HABIT3B', 770101 + i) for i in range(3)]
    bank = dict(np.load(OUT / f'bank/bank_{BANK_TAG}.npz'))
    info = json.load(open(OUT / f'bank/bank_{BANK_TAG}.json'))
    clf = K.Classifier(bank, info, 'raw')
    res = {'n_perm': NPERM, 'bank': BANK_TAG, 'controls': {}}
    for kind, seed in members:
        gen = (lambda s: flat(HR.timm_lines(sk, s))) if kind == 'TIMM' else (lambda s: flat(V.habit3b_lines(sk, s)))
        rc = C.E.pour_tokens(recs81, stream81(gen(seed), gen(seed + 1000), recs81))
        A = C.Analysis('E', recs=rc, amap_leg=amap_leg)
        St = C.Stats(A)
        yy = A.O['y'][St.m]
        r = {}
        o3c, p3c, R0 = perm_p(St, yy, St.S3c, NPERM, 7740)
        r.update({'E_informative': int(St.m.sum()), 'S3c': o3c, 'p_S3c': p3c, 'S3far': float(St.S3far(R0)[0])})
        ya = C0.adjust(A, A.O['y'][:, None])[:, 0][St.m]
        r['S3c_adj'], r['p_S3c_adj'], _ = perm_p(St, ya, St.S3c, NPERM, 7741)
        F = St.features(St.quarter_cov(R0))
        Zo = np.column_stack([[o3c], [r['S3far']], F])
        v, sc = clf.verdict(Zo)
        r.update({'A2_verdict': str(v[0]), 'A2_fit_ok': bool(sc['fit_ok'][0]), 'A2_pS': float(sc['pS'][0])})
        D, pD = C.ParaOrder(St, nperm=NPERM).stat_and_p(R0)
        r['A3_p'] = float(pD[0])
        d = St.page_turn_terms(R0)
        Kr = float(d.sum())
        _, pb = St.page_turn_test(R0, nflip=2000, by='chain')
        _, pa = St.page_turn_test(R0, nflip=2000, by='transition')
        q13, q20 = d[St.T_quire == 'M'].sum(), d[St.T_quire == 'T'].sum()
        r.update({'C1_K': Kr, 'C1_p_b': float(pb[0]), 'C1_p_a': float(pa[0]),
                  'C1_same_sign_Q13_Q20': bool(np.sign(q13) == np.sign(q20)),
                  'C1_verdict': bool(pb[0] <= 0.01 and Kr > 0 and np.sign(q13) == np.sign(q20)),
                  'face_K': float(St.page_turn_terms(R0, St.FACES).sum())})
        r['Y'] = {}
        for yd in CB.DIALS_Y:
            AE, AY = CB.build_pair(yd, recs=rc, amap_leg=amap_leg)
            CD = CB.CrossDial(AE, AY)
            StY = C.Stats(AY)
            oy, py, _ = perm_p(StY, AY.O['y'][StY.m], StY.S3c, NPERM, 7742)
            RE, RY = CD.residuals(AE.O['y'][:, None], AY.O['y'][:, None])
            Pi = CD.relabellings(NPERM, 7743)
            xo, xn = CD.X_stat(RE, RY, Pi)
            z, zn, p2 = CB.z_and_p(xo, xn)
            b3o, b3n = CD.B3_stat(RE, RY, Pi)
            pb3 = float((1 + (b3n[:, 0] >= b3o[0]).sum()) / (1 + NPERM)) if np.isfinite(b3o[0]) else 1.0
            r['Y'][yd] = {'B1_S3c': oy, 'B1_p': py, 'X': float(xo[0]), 'X_p2': float(p2[0]), 'B3_p': pb3}
        name = f'{kind}_{seed}'
        res['controls'][name] = r
        log(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != 'Y'},
            {yd: {k: round(v, 3) for k, v in r['Y'][yd].items()} for yd in r['Y']})
        json.dump(res, open(OUT / 'neg_v3.json', 'w'), indent=1)
    T = [r for n, r in res['controls'].items() if n.startswith('TIMM')]
    res['timm_summary'] = {
        'n': len(T),
        'E_S3c_fires': float(np.mean([r['p_S3c'] <= 0.01 for r in T])),
        'A2_position_dependent': float(np.mean([r['A2_verdict'] == 'POSITION-DEPENDENT-DOMINANT' for r in T])),
        'A2_static': float(np.mean([r['A2_verdict'] == 'STATIC-DOMINANT' for r in T])),
        'C1_continuity': float(np.mean([r['C1_verdict'] for r in T])),
        'B2_shared': {yd: float(np.mean([r['Y'][yd]['X_p2'] <= 0.01 / 3 for r in T])) for yd in CB.DIALS_Y},
        'combination_1': float(np.mean([r['A2_verdict'] == 'POSITION-DEPENDENT-DOMINANT' and r['C1_verdict']
                                        and (r['Y']['MIN']['X_p2'] <= 0.01 / 3 or r['Y']['CS']['X_p2'] <= 0.01 / 3)
                                        and r['Y']['KTH']['X_p2'] > 0.05 for r in T]))}
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'neg_v3.json', 'w'), indent=1)
    log('timm summary', res['timm_summary'])
    log('done')


if __name__ == '__main__':
    main()
