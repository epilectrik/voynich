#!/usr/bin/env python3
"""PHASE_770 Arm 0 calibration v2 (controls only; lean-expert v2 check: additive adjustment instead of finer cells).

0a statistic: S3c on y_adj = y - (within-folio additive effect of the preceding token's last two collapsed units,
estimated with cell means and folio fixed effects), standard cells. Sensitivity: the last collapsed unit only.
Calibration, in H (81 folios) and ZL, with plants carrying the background effects:
  - null: within-cell permutation of y_adj from a no-signal plant (1,000) -> the 1% critical value;
  - M1 at the pilot s* (x 0.75, 1, 1.25): distribution of S3c_adj, its power at alpha 0.01, and the ratio
    S3c_adj / S3c (unadjusted, same occurrences);
  - context only (background, no folio setting) at 1x and 3x the within-folio context effect: S3c and S3c_adj.
Pre-registered use (v3 text): C2086 receives the neighbour-context note if S3c_adj < 0.16 (absolute materiality line),
or if S3c_adj has p > 0.01 while this calibrated power is >= 0.9 in both H and ZL; with power < 0.9 that leg is
UNRESOLVED.
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
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def adjust(A, Y, attr='prev'):
    """Column-wise additive within-folio adjustment of the outcome for a context attribute."""
    out = np.empty_like(Y)
    for j in range(Y.shape[1]):
        out[:, j] = Y[:, j] - C.within_folio_effect(A, attr, y=Y[:, j])[0]
    return out


def calibrate(A, label, s_star, rng):
    St, P = C.Stats(A), C.Plants(A)
    res = {}
    # null (no-signal plant, adjusted, permuted within cells)
    y0 = P.draw('NONE', np.zeros(1), rng)
    y0a = adjust(A, y0)[:, 0][St.m]
    null = []
    for _ in range(4):
        Yp = C.B.perm_batch(y0a, St.cell, 250, rng)
        R = (Yp - C.cell_means_batch(Yp.T, St.cell).T).T
        null.append(St.S3c(R))
    null = np.concatenate(null)
    crit = float(np.nanquantile(null, 0.99))
    res['null'] = {'mean': float(np.nanmean(null)), 'sd': float(np.nanstd(null)), 'crit_01': crit}
    for mult in (0.75, 1.0, 1.25):
        Y = P.draw('M1', np.full(200, s_star * mult), rng)
        s_raw = St.S3c(St.residuals(Y))
        s_adj = St.S3c(St.residuals(adjust(A, Y)))
        res[f'M1_x{mult}'] = {'S3c_mean': float(np.nanmean(s_raw)), 'S3c_adj_mean': float(np.nanmean(s_adj)),
                              'ratio_median': float(np.nanmedian(s_adj / s_raw)),
                              'P_S3c_adj_lt_0.16': float(np.nanmean(s_adj < 0.16)),
                              'power_01': float(np.nanmean(s_adj >= crit))}
        log(label, 'M1 x', mult, res[f'M1_x{mult}'])
    # context only, at 1x (the background) and 3x
    ctx = C.within_folio_effect(A, 'prev')[1]
    for mult in (1.0, 3.0):
        extra = ctx * (mult - 1.0)                      # the plant's background already carries 1x context
        Y = P.draw('NONE', np.zeros(200), rng, extra_logit=extra)
        s_raw = St.S3c(St.residuals(Y))
        s_adj = St.S3c(St.residuals(adjust(A, Y)))
        res[f'context_x{mult}'] = {'S3c_mean': float(np.nanmean(s_raw)), 'S3c_adj_mean': float(np.nanmean(s_adj))}
        log(label, 'context x', mult, res[f'context_x{mult}'])
    return res


def main():
    pilot = json.load(open(OUT / 'pilot.json'))
    s_star = pilot['grid_S3c']['M1']['s_star']
    rng = np.random.default_rng(7731)
    out = {'s_star': s_star, 'rule': 'note if S3c_adj < 0.16, or p > 0.01 with power >= 0.9 in H and ZL'}
    out['H81'] = calibrate(C.Analysis('E'), 'H81', s_star, rng)
    json.dump(out, open(OUT / 'cal0.json', 'w'), indent=1)
    out['ZL'] = calibrate(C.Analysis('E', zl=True), 'ZL', s_star, rng)
    out['runtime_s'] = round(time.time() - T0, 1)
    json.dump(out, open(OUT / 'cal0.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
