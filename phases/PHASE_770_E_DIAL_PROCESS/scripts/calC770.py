#!/usr/bin/env python3
"""PHASE_770 Arm C calibration (controls only): size of the per-transition sign-flip null (a) and the per-chain null
(b) for K under models with no continuity across page turns, and power under continuing processes; the verdict rule
(K p <= 0.01 and the same sign in Q13 and Q20) evaluated on every replicate. Also A3's size and power.

Scales: each model at its pilot s* (mean S3c 0.32 in the pilot), NREP replicates.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cal770 as C  # noqa: E402

OUT = HERE.parent / 'results/calib'
NREP = 400
NFLIP = 2000
T0 = time.time()
SIZE_MODELS = ['M1', 'PAGEAR:0.3', 'PAGEAR:0.6', 'PAGEAR:0.9', 'M2b:2', 'M2b:4', 'M2b:6', 'M3', 'M4:0.97', 'M7',
               'MIX:M3/0.5', 'PARCH', 'QTREND']
POWER_MODELS = ['M6:0.95', 'M6:0.97', 'M6:0.99', 'M8:20', 'M8:40', 'M6M2B:2', 'M6M2B:4', 'MIX:M6:0.97/0.5',
                'M6FACE:0.95', 'M6FACE:0.97']
A3_MODELS = ['M1', 'M2a', 'M2b:4', 'M7', 'M3', 'M5', 'M6:0.97']


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def s_star(pilot, model):
    g = pilot['grid_S3c']
    if model in g and g[model]['s_star']:
        return g[model]['s_star']
    base = {'PAGEAR': 'M1', 'PARCH': 'M1', 'QTREND': 'M1', 'M6M2B': 'M6:0.97', 'M6FACE': 'M6:0.97'}.get(model.split(':')[0])
    return g[base]['s_star'] * (1.2 if model.startswith('M6M2B') else 1.0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pilot = json.load(open(OUT / 'pilot.json'))
    A = C.Analysis('E')
    St = C.Stats(A)
    P = C.Plants(A)
    q13 = St.T_quire == 'M'
    q20 = St.T_quire == 'T'
    log('transitions', len(St.T), 'Q13', int(q13.sum()), 'Q20', int(q20.sum()), 'leaf', int((St.T_kind == 'leaf_turn').sum()),
        'opening', int((St.T_kind == 'opening').sum()))
    res = {'n_rep': NREP, 'n_flip': NFLIP, 'C1': {}, 'A3': {}}
    rng = np.random.default_rng(7703)
    for model in SIZE_MODELS + POWER_MODELS:
        s = s_star(pilot, model)
        Y = P.draw(model, np.full(NREP, s), rng)
        R = St.residuals(Y)
        s3c = St.S3c(R)
        d = St.page_turn_terms(R)
        K = d.sum(0)
        rr = np.random.default_rng(7704)
        Sg = rr.choice([-1.0, 1.0], size=(NFLIP, d.shape[0]))
        pa = (1 + ((Sg @ d) >= K[None, :]).sum(0)) / (1 + NFLIP)
        _, pb = St.page_turn_test(R, nflip=NFLIP, by='chain')
        k13, k20 = d[q13].sum(0), d[q20].sum(0)
        same = np.sign(k13) == np.sign(k20)
        verdict_a = (pa <= 0.01) & same & (K > 0)
        verdict_b = (pb <= 0.01) & same & (K > 0)
        dF = St.page_turn_terms(R, St.FACES)
        KF = dF.sum(0)
        halves = {}
        for qq, qn in (('M', 'Q13'), ('T', 'Q20')):
            for hh in (0, 1):
                sel = (St.T_quire == qq) & (St.T_half == hh)
                halves[f'{qn}_half{hh}'] = d[sel].sum(0)
        r = {'scale': s, 'S3c_mean': float(np.nanmean(s3c)), 'K_mean': float(K.mean()),
             'K_face_mean': float(KF.mean()), 'K_face_pos_rate': float((KF > 0).mean()),
             'Q13_halves_same_sign': float((np.sign(halves['Q13_half0']) == np.sign(halves['Q13_half1'])).mean()),
             'Q20_halves_same_sign': float((np.sign(halves['Q20_half0']) == np.sign(halves['Q20_half1'])).mean()),
             'K_half_means': {k: float(v.mean()) for k, v in halves.items()},
             'p_a_le_01': float((pa <= 0.01).mean()), 'p_a_le_05': float((pa <= 0.05).mean()),
             'p_b_le_01': float((pb <= 0.01).mean()), 'p_b_le_05': float((pb <= 0.05).mean()),
             'verdict_CONTINUITY_a': float(verdict_a.mean()), 'verdict_CONTINUITY_b': float(verdict_b.mean()),
             'leaf_K_mean': float(d[St.T_kind == 'leaf_turn'].sum(0).mean()),
             'opening_K_mean': float(d[St.T_kind == 'opening'].sum(0).mean())}
        res['C1'][model] = r
        log(f'C1 {model:16s} s {s:.2f} S3c {r["S3c_mean"]:+.3f}  (a) p<=.01 {r["p_a_le_01"]:.3f} p<=.05 {r["p_a_le_05"]:.3f}'
            f'  (b) p<=.01 {r["p_b_le_01"]:.3f}  verdict(a) {r["verdict_CONTINUITY_a"]:.3f}')
        json.dump(res, open(OUT / 'calC.json', 'w'), indent=1)
    # M6 MDE80: power of the verdict rule against scale
    res['C1_M6_power_curve'] = {}
    for mult in (1.0, 1.5, 2.0, 3.0):
        s = s_star(pilot, 'M6:0.97') * mult
        Y = P.draw('M6:0.97', np.full(200, s), rng)
        R = St.residuals(Y)
        d = St.page_turn_terms(R)
        K = d.sum(0)
        Sg = np.random.default_rng(7705).choice([-1.0, 1.0], size=(NFLIP, d.shape[0]))
        pa = (1 + ((Sg @ d) >= K[None, :]).sum(0)) / (1 + NFLIP)
        same = np.sign(d[q13].sum(0)) == np.sign(d[q20].sum(0))
        res['C1_M6_power_curve'][str(mult)] = {'scale': s, 'S3c_mean': float(np.nanmean(St.S3c(R))),
                                               'verdict_power': float(((pa <= 0.01) & same & (K > 0)).mean())}
        log('M6:0.97 x', mult, res['C1_M6_power_curve'][str(mult)])
    json.dump(res, open(OUT / 'calC.json', 'w'), indent=1)
    # A3: size and power (200 replicates, 2,000 permutations)
    po = C.ParaOrder(St, nperm=2000)
    for model in A3_MODELS:
        s = s_star(pilot, model)
        Y = P.draw(model, np.full(200, s), rng)
        R = St.residuals(Y)
        D, p = [], []
        for j in range(0, 200, 50):
            d_, p_ = po.stat_and_p(R[:, j:j + 50])
            D.append(d_)
            p.append(p_)
        D, p = np.concatenate(D), np.concatenate(p)
        res['A3'][model] = {'scale': s, 'D_mean': float(D.mean()), 'p_le_01': float((p <= 0.01).mean()),
                            'p_le_05': float((p <= 0.05).mean())}
        log(f'A3 {model:10s} p<=.01 {res["A3"][model]["p_le_01"]:.3f} p<=.05 {res["A3"][model]["p_le_05"]:.3f}')
        json.dump(res, open(OUT / 'calC.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'calC.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
