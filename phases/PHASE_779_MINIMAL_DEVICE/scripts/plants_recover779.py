#!/usr/bin/env python3
"""PHASE_779 PRE-LOCK recovery of results/plants779.json from the plants-stage log.

The plants stage (run779.py plants) hung at the P12 lam 1.0 grid point (its pool's workers were all replaced at
18:20 on 2026-10-02 and the in-flight tasks were lost; cause not determined) and it writes its JSON only at the end.
This script (1) parses every completed grid point from results/plants_log779.txt (mean, baseline mean, fraction
outside; the per-point sd is not in the log and is stored as null), (2) regenerates the baseline primary ensemble
from the stage's own seed and checks that every logged baseline mean is reproduced to the log's 4 decimals, (3)
stores the baseline summaries (mean, sd, min, max) and the pair-zero baseline, and (4) writes plants779.json with
MDE80 per plant (the weakest grid point with >= 80% of plant members outside). Generated members only; no B value
is read. Missing and refining grid points are then added with plants_extend779.py."""
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run779 as R  # noqa: E402

LINE = re.compile(r'^plant (\S+) lam (\S+): mean (\S+) \(baseline (\S+)\) outside (\S+)')


def summ0(vals):
    v = np.asarray(vals, float)
    v = v[~np.isnan(v)]
    return {'mean': float(v.mean()), 'sd': float(v.std(ddof=1)), 'min': float(v.min()), 'max': float(v.max()), 'n': int(len(v))}


def strength_order(plant, lams):
    return sorted(lams, key=lambda x: -x) if plant == 'P2' else sorted(lams)


def mde80(plant, points):
    for lam in strength_order(plant, [float(x) for x in points]):
        key = next(k for k in points if float(k) == lam)
        if points[key]['frac_outside'] >= 0.8:
            return {'lam': float(lam), 'effect': float(abs(points[key]['mean'] - points[key]['baseline_mean']))}
    return None


def main():
    R.LOGF = open(R.OUT / 'plants_recover_log779.txt', 'a', encoding='utf-8')
    R.log(f"PHASE_779 plants recovery from log; {time.strftime('%Y-%m-%d %H:%M:%S')}")
    t0 = time.time()
    R._init()
    M = R._W['M']
    kappa = R.kappa_locked()
    # 1. parse the log
    logged = {}
    for ln in open(R.OUT / 'plants_log779.txt', encoding='utf-8'):
        m = LINE.match(ln)
        if m:
            key, lam, mean, base, frac = m.groups()
            logged.setdefault(key, {})[lam] = {'mean': float(mean), 'sd': None, 'baseline_mean': float(base),
                                               'frac_outside': float(frac), 'source': 'log'}
    R.log('parsed: ' + ', '.join(f'{k.split("_")[0]} {len(v)}' for k, v in logged.items()))
    # 2. regenerate the baseline (same seed as the stage)
    cells_f = json.load(open(R.OUT / 'pair_cells779.json', encoding='utf-8'))
    cells = [tuple(c) for c in cells_f['cells']]
    tasks = [(R.PRIMARY, m, R.SEED_PLANT, None, 0.0, True) for m in range(R.N_PLANT)]
    base = list(R.pool_map(R.member, tasks, init_kappa=kappa))
    P0 = np.array([r['P'] for r in base])
    zeros0 = []
    for r in base:
        a, b, c = r['pairs']
        present = set(zip(a.tolist(), b.tolist()))
        zeros0.append(sum(1 for k in cells if k not in present))
    R.log(f"baseline regenerated ({time.time() - t0:.0f}s)")
    # 3. verify every logged baseline mean
    ok = True
    baseline = {}
    for key, (plant, grid) in M.PLANTS.items():
        if plant == 'P6':
            vals = np.array(zeros0, float)
        else:
            vals = P0[:, M.COUNTED.index(key)]
        baseline[key] = summ0(vals)
        lb = next(iter(logged.get(key, {}).values()), None)
        if lb is None:
            R.log(f"  {key}: no logged points")
            continue
        diff = abs(baseline[key]['mean'] - lb['baseline_mean'])
        R.log(f"  {key}: regenerated baseline {baseline[key]['mean']:.6f} vs logged {lb['baseline_mean']:.4f} (diff {diff:.2e}) sd {baseline[key]['sd']:.5f}")
        ok &= diff < 6e-5
    assert ok, 'a logged baseline mean is not reproduced; not writing'
    # 4. write
    res = {'kappa': kappa, 'N': R.N_PLANT, 'cells_expect_ge3': len(cells), 'baseline_zeros': summ0(zeros0),
           'baseline': baseline, 'plants': {}, 'recovered': {
               'from': 'results/plants_log779.txt',
               'reason': 'the plants stage hung at the P12 lam 1.0 point (pool workers replaced, in-flight tasks lost) and writes its JSON only at the end',
               'per_point_sd': 'not in the log; null for stage points',
               'baseline_check': 'regenerated from the stage seed; every logged baseline mean reproduced to 4 decimals',
               'time': time.strftime('%Y-%m-%d %H:%M:%S')}}
    for key, (plant, grid) in M.PLANTS.items():
        pts = logged.get(key, {})
        res['plants'][key] = {'plant': plant, 'grid': list(grid), 'points': pts, 'MDE80': mde80(plant, pts) if pts else None,
                              'missing_from_stage': [g for g in grid if str(g) not in pts]}
        R.log(f"  {key}: {len(pts)} points, missing {res['plants'][key]['missing_from_stage']}, MDE80 {res['plants'][key]['MDE80']}")
    tmp = R.OUT / 'plants779.json.tmp'
    json.dump(res, open(tmp, 'w', encoding='utf-8'), indent=1)
    os.replace(tmp, R.OUT / 'plants779.json')
    R.log(f"plants779.json written from the log ({time.time() - t0:.0f}s)")


if __name__ == '__main__':
    main()
