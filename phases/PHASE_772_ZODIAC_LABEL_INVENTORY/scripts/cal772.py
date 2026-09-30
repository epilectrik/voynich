#!/usr/bin/env python3
"""PHASE_772 calibration (v2 after the lean-expert lock audit). Base forms come from Currier A paragraph words of 4-8
glyph units (ZL), not from the real labels; only the real sign sizes are used. Nothing here computes a statistic of
the real labels.

  R thresholds: pure inventory model, 2,000 simulations per lam (R only), unrounded q01 / q05 at N0/N1/N2; the share
                of inventory copies visibly changed at N2 per lam.
  W power:      pure inventory model, 100 simulations per lam, 1,000 permutations each (INVENTORY rule rates).
  Mixtures:     inventory share phi in {0.25, 0.5, 0.75} x remainder {palette, unique}, lam = 1, 40 simulations each,
                verdict distribution under the full pre-registered logic.
  Pure palette and pure unique-form sets: verdict distributions (200 and 100 simulations).
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zod772 as Z  # noqa: E402

OUT = Z.ROOT / 'phases/PHASE_772_ZODIAC_LABEL_INVENTORY/results'
SEED = 7721
NSIM_R, NSIM_W, NPERM, NSIM_MIX, NSIM_PAL, NSIM_UNI = 2000, 100, 1000, 40, 200, 100
SMOKE = '--smoke' in sys.argv
if SMOKE:
    NSIM_R, NSIM_W, NPERM, NSIM_MIX, NSIM_PAL, NSIM_UNI = 50, 3, 100, 3, 3, 3


def log(*a):
    print(*a, flush=True)


def verdict_rates(sizes, pool, rng, thr, nsim, lam, phi, remainder):
    calls = Counter()
    for _ in range(nsim):
        forms, signs, _ = Z.simulate(sizes, pool, rng, lam, phi, remainder)
        s1 = Z.w_test([Z.n1(w) for w in forms], signs, rng, NPERM)
        f2 = [Z.n2(w) for w in forms]
        s2 = Z.w_test(f2, signs, rng, NPERM)
        v, _ = Z.verdict(s1, s2, s2['R'], s2['R'], thr)
        calls[v.split(' (')[0] if v.startswith('NO INVENTORY') and '+' not in v else v] += 1
    return {k: round(c / nsim, 3) for k, c in calls.items()}


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    pool = Z.currier_a_words()
    sizes = Counter(r['sign'] for r in Z.load_labels())
    res = {'pool_size': len(pool), 'sizes': dict(sizes)}
    log('pool', len(pool), 'sizes', dict(sizes))
    thr, vis_share = {}, {}
    for lam in Z.LAM_GRID:
        R = {k: [] for k in Z.NORMS}
        vis = []
        for _ in range(NSIM_R):
            forms, signs, v = Z.simulate(sizes, pool, rng, lam)
            vis.extend(v)
            for k, f in Z.NORMS.items():
                R[k].append(Z.dup_stats([f(w) for w in forms], signs)['R'])
        thr[str(lam)] = {k: {'q01': float(np.quantile(v, 0.01)), 'q05': float(np.quantile(v, 0.05))}
                         for k, v in R.items()}
        vis_share[str(lam)] = float(np.mean(vis))
        log(f'lam {lam}: R(N2) q01 {thr[str(lam)]["N2"]["q01"]:.4f} q05 {thr[str(lam)]["N2"]["q05"]:.4f} | '
            f'visibly changed at N2 {vis_share[str(lam)]:.3f}')
    res['R_thresholds'] = thr
    res['visible_change_share_N2'] = vis_share
    thr2 = {lam: thr[lam]['N2'] for lam in thr}
    res['inventory_rule_rates'] = {}
    for lam in Z.LAM_GRID:
        res['inventory_rule_rates'][str(lam)] = verdict_rates(sizes, pool, rng, thr2, NSIM_W, lam, 1.0, 'unique')
        log(f'pure inventory lam {lam}: {res["inventory_rule_rates"][str(lam)]}')
    res['mixtures_lam1'] = {}
    for phi in (0.25, 0.5, 0.75):
        for rem in ('palette', 'unique'):
            key = f'phi{phi}_{rem}'
            res['mixtures_lam1'][key] = verdict_rates(sizes, pool, rng, thr2, NSIM_MIX, 1.0, phi, rem)
            log(f'mixture {key}: {res["mixtures_lam1"][key]}')
    res['pure_palette_lam1'] = verdict_rates(sizes, pool, rng, thr2, NSIM_PAL, 1.0, 0.0, 'palette')
    log('pure palette:', res['pure_palette_lam1'])
    res['pure_unique'] = verdict_rates(sizes, pool, rng, thr2, NSIM_UNI, 0.0, 0.0, 'unique')
    log('pure unique forms:', res['pure_unique'])
    res['runtime_s'] = round(time.time() - t0, 1)
    (OUT / ('cal772_smoke.json' if SMOKE else 'cal772.json')).write_text(json.dumps(res, indent=1))
    log('done', res['runtime_s'], 's')


if __name__ == '__main__':
    main()
