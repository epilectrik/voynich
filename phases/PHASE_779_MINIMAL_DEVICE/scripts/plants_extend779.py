#!/usr/bin/env python3
"""PHASE_779 PRE-LOCK plant-grid extension (generated members only; no B value is read).

  python plants_extend779.py KEY=lam1,lam2 [KEY2=lam3 ...]

Adds grid points to plants in results/plants779.json: the points the hung stage never ran, weaker points where the
declared grid's weakest point already put >= 80% of plant members outside (so MDE80 was only bounded), and
refining points between the last point under 80% and the first over it. The baseline primary ensemble is
regenerated once from the stage's seed (checked against the stored baseline mean per plant), the new points use the
same member machinery as `run779.py plants` with their own seed block, the file is rewritten after every point
(atomic), and MDE80 is recomputed per plant as the weakest grid point with >= 80% outside. Every extension is
recorded under 'extensions'."""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run779 as R  # noqa: E402

SEED_EXT = R.SEED_PLANT + 500_000


def strength_order(plant, lams):
    return sorted(lams, key=lambda x: -x) if plant == 'P2' else sorted(lams)


def mde80(plant, points):
    for lam in strength_order(plant, [float(x) for x in points]):
        key = next(k for k in points if float(k) == lam)
        if points[key]['frac_outside'] >= 0.8:
            return {'lam': float(lam), 'effect': float(abs(points[key]['mean'] - points[key]['baseline_mean']))}
    return None


def write(res):
    tmp = R.OUT / 'plants779.json.tmp'
    json.dump(res, open(tmp, 'w', encoding='utf-8'), indent=1)
    os.replace(tmp, R.OUT / 'plants779.json')


def main():
    specs = []
    for a in sys.argv[1:]:
        key, lams = a.split('=')
        specs.append((key, [float(x) for x in lams.split(',')]))
    assert specs, 'give KEY=lam1,lam2 ...'
    R.LOGF = open(R.OUT / 'plants_extend_log779.txt', 'a', encoding='utf-8')
    R.log(f"PHASE_779 plants extension {specs}; {time.strftime('%Y-%m-%d %H:%M:%S')}")
    t0 = time.time()
    R._init()
    M = R._W['M']
    kappa = R.kappa_locked()
    res = json.load(open(R.OUT / 'plants779.json', encoding='utf-8'))
    cells_f = json.load(open(R.OUT / 'pair_cells779.json', encoding='utf-8'))
    cells = [tuple(c) for c in cells_f['cells']]
    R._W['pair_expect'] = {tuple(int(x) for x in k.split(',')): e for k, e in cells_f['expect'].items()}
    # baseline primary ensemble, same seed as the plants stage
    tasks = [(R.PRIMARY, m, R.SEED_PLANT, None, 0.0, True) for m in range(R.N_PLANT)]
    base = list(R.pool_map(R.member, tasks, init_kappa=kappa))
    P0 = np.array([r['P'] for r in base])
    zeros0 = []
    for r in base:
        a, b, c = r['pairs']
        present = set(zip(a.tolist(), b.tolist()))
        zeros0.append(sum(1 for k in cells if k not in present))
    R.log(f"baseline regenerated ({time.time() - t0:.0f}s)")
    for key, extra in specs:
        entry = res['plants'][key]
        plant = entry['plant']
        j = M.COUNTED.index(key) if key in M.COUNTED else None
        ref = np.array(zeros0, float) if plant == 'P6' else P0[:, j]
        stored = res.get('baseline', {}).get(key, {}).get('mean')
        if stored is None:
            stored = next(iter(entry['points'].values()))['baseline_mean']
        assert abs(np.nanmean(ref) - stored) < 6e-5, f'{key}: baseline does not reproduce the stored value; not merging'
        kidx = list(M.PLANTS).index(key)
        for lam in extra:
            rng0 = np.random.default_rng(R.SEED_PLANT + 777)
            if plant == 'P6':
                pro = R._prohibit_cells(rng0, int(lam))
                json.dump({a: sorted(b) for a, b in pro.items()}, open(R.OUT / 'prohibit_tmp.json', 'w'))
            tasks = [(R.PRIMARY, m, SEED_EXT + 10_000 * kidx + int(lam * 100), plant, float(lam), plant == 'P6') for m in range(R.N_PLANT)]
            vals = []
            for r in R.pool_map(R.member, tasks, init_kappa=kappa):
                if plant == 'P6':
                    a, b, c = r['pairs']
                    present = set(zip(a.tolist(), b.tolist()))
                    vals.append(sum(1 for k in cells if k not in present))
                else:
                    vals.append(r['P'][j])
            vals = np.array(vals, float)
            frac_out = float(np.mean([R.outside(v, ref, 8, discrete=(plant == 'P6')) for v in vals]))
            lam_key = str(int(lam)) if plant == 'P6' else str(lam)
            entry['points'][lam_key] = {'mean': float(np.nanmean(vals)), 'sd': float(np.nanstd(vals, ddof=1)),
                                        'baseline_mean': float(np.nanmean(ref)), 'frac_outside': frac_out, 'source': 'extension'}
            if lam not in entry['grid'] and (int(lam) if plant == 'P6' else lam) not in entry['grid']:
                entry['grid'].append(int(lam) if plant == 'P6' else lam)
            entry['MDE80'] = mde80(plant, entry['points'])
            res.setdefault('extensions', []).append({'key': key, 'lam': lam, 'seed': SEED_EXT + 10_000 * kidx + int(lam * 100),
                                                     'time': time.strftime('%Y-%m-%d %H:%M:%S')})
            write(res)
            R.log(f"plant {key} lam {lam}: mean {np.nanmean(vals):.4f} (baseline {np.nanmean(ref):.4f}) outside {frac_out:.2f}; MDE80 {entry['MDE80']} ({time.time() - t0:.0f}s)")
            if (R.OUT / 'prohibit_tmp.json').exists():
                (R.OUT / 'prohibit_tmp.json').unlink()
    R.log(f"extensions done ({time.time() - t0:.0f}s)")


if __name__ == '__main__':
    main()
