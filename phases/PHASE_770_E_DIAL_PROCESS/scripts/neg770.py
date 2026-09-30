#!/usr/bin/env python3
"""PHASE_770 negative-text controls (controls only): Timm-Schinner self-citation output (3 seeds), habit3b local-rule
generator fitted to B (3 seeds) and the Naibbe cipher (1 stream), poured into B's skeleton (PHASE_769's 80-folio set,
which the generators were built for). For each control: the E-dial S3c and S3far with the within-cell permutation
null, A1 features, A3, C1 (K with nulls a and b), and for each Y dial B1 (own S3c) and B2 (X with the pairing null)
and B3. A control 'fires' a test when its p <= 0.01.
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

OUT = HERE.parent / 'results/calib'
NPERM = 1000
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def s3_perm_p(St, y, nperm, seed):
    """S3c and S3far with the within-cell permutation null (one-sided)."""
    rng = np.random.default_rng(seed)
    m = St.m
    yy = y[m]
    cm = C.E.cell_means(yy, St.cell)
    R0 = (yy - cm)[:, None]
    o3c, o3f = float(St.S3c(R0)[0]), float(St.S3far(R0)[0])
    n3c, n3f = [], []
    for _ in range(0, nperm, 250):
        Yp = C.B.perm_batch(yy, St.cell, 250, rng)
        R = (Yp - cm[None, :]).T
        n3c.append(St.S3c(R))
        n3f.append(St.S3far(R))
    n3c, n3f = np.concatenate(n3c), np.concatenate(n3f)
    pc = float((1 + (n3c >= o3c).sum()) / (1 + nperm)) if np.isfinite(o3c) else 1.0   # not computable: p = 1
    pf = float((1 + (n3f >= o3f).sum()) / (1 + nperm)) if np.isfinite(o3f) else 1.0
    return o3c, pc, o3f, pf, R0


def main():
    import hr768 as HR
    import hr768v2 as V
    OUT.mkdir(parents=True, exist_ok=True)
    recs80 = C.E.load_b_h()
    base = C.Analysis('E', set81=False, f115r_hand=None)
    amap_leg = (None, base.leg)
    sk = HR.b_skeleton()
    flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
    n = len(recs80)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'panel'
    if mode == 'timm50':                     # 50 Timm-Schinner members (expert-advisor v2 check)
        seeds = [770300 + i for i in range(50)]
        streams = {f'TIMM_{s}': (lambda s=s: flat(HR.timm_lines(sk, s))) for s in seeds}
        out_name, nperm = 'neg_timm50.json', 500
    else:
        streams = {'NAIBBE_P-REC': lambda: HR.naibbe_stream('P-REC', 770001, n)[0]}
        for s in (770201, 770202, 770203):
            streams[f'TIMM_{s}'] = (lambda s=s: flat(HR.timm_lines(sk, s)))
        for s in (770101, 770102, 770103):
            streams[f'HABIT3B_{s}'] = (lambda s=s: flat(V.habit3b_lines(sk, s)))
        out_name, nperm = 'neg.json', NPERM
    clf = None
    bank_tag = 'H81_0.323_0.095_770'
    if (HERE.parent / f'results/calib/bank/bank_{bank_tag}.npz').exists():
        import gate770 as G
        bank = dict(np.load(HERE.parent / f'results/calib/bank/bank_{bank_tag}.npz'))
        info = json.load(open(HERE.parent / f'results/calib/bank/bank_{bank_tag}.json'))
        clf = G.Classifier(bank, info, 'raw')
    res = {'n_perm': nperm, 'controls': {}}
    for name, make in streams.items():
        stream = make()
        rc = C.E.pour_tokens(recs80, stream)
        A = C.Analysis('E', recs=rc, amap_leg=amap_leg)
        St = C.Stats(A)
        y = A.O['y']
        o3c, p3c, o3f, p3f, R0 = s3_perm_p(St, y, nperm, 7720)
        r = {'E_informative': int(A.O['informative'].sum()), 'S3c': o3c, 'p_S3c': p3c, 'S3far': o3f, 'p_S3far': p3f}
        r['A1_features'] = St.features(St.quarter_cov(R0))[0].tolist()
        if clf is not None:
            v, sc = clf.verdict(np.array([r['A1_features']]))
            r['A2_verdict_vs_B_bank'] = str(v[0])
            r['A2_fit_ok'] = bool(sc['fit_ok'][0])
        D, pD = C.ParaOrder(St, nperm=nperm).stat_and_p(R0)
        r['A3_D'], r['A3_p'] = float(D[0]), float(pD[0])
        d = St.page_turn_terms(R0)
        K = float(d.sum())
        rr = np.random.default_rng(7721)
        Sg = rr.choice([-1.0, 1.0], size=(2000, d.shape[0]))
        r['C1_K'] = K
        r['C1_p_a'] = float((1 + ((Sg @ d)[:, 0] >= K).sum()) / 2001)
        r['C1_p_b'] = float(St.page_turn_test(R0, nflip=2000, by='chain')[1][0])
        r['Y'] = {}
        for yd in CB.DIALS_Y:
            AE, AY = CB.build_pair(yd, recs=rc, amap_leg=amap_leg)
            CD = CB.CrossDial(AE, AY)
            StY = C.Stats(AY)
            oy, py, _, _, _ = s3_perm_p(StY, AY.O['y'], nperm, 7722)
            RE, RY = CD.residuals(AE.O['y'][:, None], AY.O['y'][:, None])
            Pi = CD.relabellings(nperm, 7723)
            xo, xn = CD.X_stat(RE, RY, Pi)
            z, zn, p2 = CB.z_and_p(xo, xn)
            b3o, b3n = CD.B3_stat(RE, RY, Pi)
            pb3 = float((1 + (b3n[:, 0] >= b3o[0]).sum()) / (1 + nperm)) if np.isfinite(b3o[0]) else 1.0
            r['Y'][yd] = {'B1_S3c': oy, 'B1_p': py, 'X': float(xo[0]), 'X_p2': float(p2[0]), 'B3': float(b3o[0]),
                          'B3_p': pb3}
        res['controls'][name] = r
        log(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k not in ('A1_features', 'Y')},
            {yd: {k: round(v, 3) for k, v in r['Y'][yd].items()} for yd in r['Y']})
        json.dump(res, open(OUT / out_name, 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / out_name, 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
