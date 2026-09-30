#!/usr/bin/env python3
"""PHASE_770 calibration pilot (controls only).

1. Pooled effects used by the CONTEXT and LAYOUT plants (B's outcome pooled over all folios, within cells; no folio,
   position or page-turn information): the preceding glyph unit and the line-fullness tercile.
2. For every plant model: mean S3c at a grid of scales, and the scale s* at which the mean S3c is 0.32 (the PHASE_769
   value), to set the plant bank's strength priors.
3. Arm 0b: the CONTEXT plant at the pooled strength (multiplier 1): distribution of S3c.
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
MODELS = ['M1', 'M2a', 'M2b:2', 'M2b:4', 'M2b:6', 'M2c', 'M7', 'M3', 'M4:0.95', 'M4:0.97', 'M4:0.99', 'M5',
          'M6:0.95', 'M6:0.97', 'M6:0.99', 'M8:10', 'M8:20', 'M8:40', 'M9',
          'MIX:M3/0.25', 'MIX:M3/0.5', 'MIX:M3/0.75', 'MIX:M6:0.97/0.25', 'MIX:M6:0.97/0.5', 'MIX:M6:0.97/0.75']
GRID = [0.2, 0.35, 0.5, 0.7, 1.0, 1.4]
NREP = 100


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    A = C.Analysis('E')
    St = C.Stats(A)
    P = C.Plants(A)
    res = {'n_rep': NREP, 'grid': GRID}
    ctx, ctx_table = C.pooled_effect(A, 'prev')
    lay, lay_table = C.pooled_effect(A, 'full3')
    res['pooled_prev_effect_logit'] = ctx_table
    res['pooled_full3_effect_logit'] = lay_table
    log('pooled prev effect (logit, n>=30):', {k: round(v, 3) for k, v in ctx_table.items() if v != 0})
    log('pooled full3 effect (logit):', {k: round(v, 3) for k, v in lay_table.items()})
    rng = np.random.default_rng(770)
    # Arm 0b: CONTEXT plant at multiplier 1 (no folio latent)
    out0 = []
    for mult in (1.0, 2.0, 3.0):
        Y = P.draw('NONE', np.zeros(200), rng, extra_logit=ctx * mult)
        R = St.residuals(Y)
        s = St.S3c(R)
        out0.append({'multiplier': mult, 'S3c_mean': float(np.nanmean(s)), 'S3c_sd': float(np.nanstd(s)),
                     'S3c_q95': float(np.nanquantile(s, 0.95)), 'S3far_mean': float(np.nanmean(St.S3far(R)))})
        log('CONTEXT x', mult, out0[-1])
    res['context_plant'] = out0
    # LAYOUT at multiplier 1 with no folio latent (how much S3c the fullness effect alone produces)
    Y = P.draw('NONE', np.zeros(200), rng, extra_logit=lay)
    R = St.residuals(Y)
    res['layout_only'] = {'S3c_mean': float(np.nanmean(St.S3c(R))), 'S3far_mean': float(np.nanmean(St.S3far(R)))}
    log('LAYOUT only', res['layout_only'])
    # scale grid per model
    res['grid_S3c'] = {}
    for model in MODELS:
        row = []
        for s in GRID:
            Y = P.draw(model, np.full(NREP, s), rng)
            R = St.residuals(Y)
            row.append([float(np.nanmean(St.S3c(R))), float(np.nanmean(St.S3far(R)))])
        s3 = np.array([r[0] for r in row])
        sstar = float(np.interp(0.32, s3, GRID)) if s3.max() >= 0.32 and np.all(np.diff(s3) > 0) else None
        res['grid_S3c'][model] = {'S3c_S3far': row, 's_star': sstar}
        log(model, 'S3c by scale', np.round(s3, 3), 's*', sstar)
        json.dump(res, open(OUT / 'pilot.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
