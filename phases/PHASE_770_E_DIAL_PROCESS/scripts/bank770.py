#!/usr/bin/env python3
"""PHASE_770 Arm A plant bank (controls only).

v3 (after the lean-expert v2 check): plants carry the within-folio context and line-fullness background effects; the
scale prior is log-uniform on [0.55 s*, 1.5 s*] (s* from the pilot); replicates are kept when S3c lies in the wide
window [S3C_LO, S3C_HI], so the classifier can condition on B's S3c and S3far at run time (Gaussian conditioning);
N_ACCEPT per model or MAX_DRAWS. D14 (latent position contrast) is computed per model from 200 latent draws. Saves
model, scale, S3c, S3far, 7 raw features and 6 scale-free features (V1-V3, D1-D3 divided by mean(V1-V4)).

Usage: bank770.py SET [SEED]
  SET: H81 (primary), ZL, H80 (PHASE_769 folio set), H81_full3 (fullness tercile in the cell), H81_cons (runs read
       alike by H and F).
Deterministic given SET, target and SEED; the lock fixes code and seeds, and the run script regenerates the bank at
B's values.
"""
from __future__ import annotations

import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cal770 as C  # noqa: E402

OUT = HERE.parent / 'results/calib/bank'
S3C_LO, S3C_HI = 0.25, 0.40
N_ACCEPT = 10000
MAX_DRAWS = 150000
BATCH = 500
MODELS = ['M1', 'M2a', 'M2b:2', 'M2b:4', 'M2b:6', 'M2c', 'M7', 'M3', 'M4:0.95', 'M4:0.97', 'M4:0.99', 'M5',
          'M6:0.95', 'M6:0.97', 'M6:0.99', 'M8:20', 'M8:40',
          'MIX:M3/0.25', 'MIX:M3/0.5', 'MIX:M3/0.75', 'MIX:M6:0.97/0.25', 'MIX:M6:0.97/0.5', 'MIX:M6:0.97/0.75']
D14_STATIC, D14_POS = 0.15, 0.5       # class by latent position contrast (lean-expert v2 check); mixtures: gate only
# excluded after the pilot (cannot reach the PHASE_769 S3c at any scale tried, up to 1.4): M8:10, M9.
# LAYOUT excluded: the pooled line-fullness effect is ~0 (|delta| <= 0.004 logit), so LAYOUT is M1.
# CONTEXT excluded from A2: at multipliers 1-3 its mean S3c is ~0 (Arm 0b).


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def build(set_name):
    if set_name == 'H81':
        return C.Analysis('E')
    if set_name == 'H80':
        return C.Analysis('E', set81=False, f115r_hand=None)
    if set_name == 'H81_full3':
        return C.Analysis('E', cell_extra=('full3',))
    if set_name == 'H81_cons':
        return C.Analysis('E', subset='cons')
    if set_name == 'H81_cons3':                       # runs read alike by H, F and ZL (v3 no-flip check)
        return C.Analysis('E', subset='cons3')
    if set_name == 'ZL':
        return C.Analysis('E', zl=True)
    raise ValueError(set_name)


def generate(A, St, P, tag, models=None, n_accept=N_ACCEPT, max_draws=MAX_DRAWS, with_d14=True):
    """Draw plant replicates of each model (log-uniform scale on [0.55 s*, 1.5 s*]) and keep those with S3c in
    [S3C_LO, S3C_HI]. Deterministic given the tag. Returns (keep dict of lists, counts, d14)."""
    pilot = json.load(open(HERE.parent / 'results/calib/pilot.json'))
    keep = {k: [] for k in ('model', 'scale', 'S3c', 'S3far', 'F_raw', 'F_free')}
    counts, d14 = {}, {}
    for model in (models or MODELS):
        s_star = pilot['grid_S3c'][model]['s_star']
        rng = np.random.default_rng(zlib.crc32(f'{tag}/{model}'.encode()))
        if with_d14:
            d14[model] = C.d14(A, P, model, np.random.default_rng(zlib.crc32(f'{tag}/{model}/d14'.encode())))
        n_draw = n_c = 0
        while n_c < n_accept and n_draw < max_draws:
            scales = np.exp(rng.uniform(np.log(0.55 * s_star), np.log(1.5 * s_star), BATCH))
            Y = P.draw(model, scales, rng)
            R = St.residuals(Y)
            s3c = St.S3c(R)
            s3f = St.S3far(R)
            okc = (s3c >= S3C_LO) & (s3c <= S3C_HI)
            n_draw += BATCH
            n_c += int(okc.sum())
            if okc.any():
                Cq = St.quarter_cov(R[:, okc])
                keep['model'] += [model] * int(okc.sum())
                keep['scale'] += scales[okc].tolist()
                keep['S3c'] += s3c[okc].tolist()
                keep['S3far'] += s3f[okc].tolist()
                keep['F_raw'] += St.features(Cq).tolist()
                keep['F_free'] += St.features(Cq, scale_free=True).tolist()
        counts[model] = {'draws': n_draw, 'S3c_accepted': n_c}
        log(f'{model:18s} D14 {d14.get(model, float("nan")):.3f}  draws {n_draw:6d}  accepted {n_c:6d}')
    return keep, counts, d14


def save(keep, counts, d14, tag, set_name, seed):
    np.savez_compressed(OUT / f'bank_{tag}.npz', model=np.array(keep['model']), scale=np.array(keep['scale']),
                        S3c=np.array(keep['S3c']), S3far=np.array(keep['S3far']), F_raw=np.array(keep['F_raw']),
                        F_free=np.array(keep['F_free']))
    classes = {m: ('X' if m.startswith('MIX') else 'S' if d14[m] <= D14_STATIC else 'P' if d14[m] >= D14_POS else 'I')
               for m in d14}
    json.dump({'set': set_name, 'seed': seed, 'window': [S3C_LO, S3C_HI], 'classes': classes, 'D14': d14,
               'counts': counts, 'runtime_s': round(time.time() - T0, 1)},
              open(OUT / f'bank_{tag}.json', 'w'), indent=1)


def main():
    global T0
    T0 = time.time()
    set_name = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 770
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f'v3_{set_name}_{seed}'
    A = build(set_name)
    St = C.Stats(A)
    P = C.Plants(A)
    log(set_name, 'occ', len(A.O['y']), 'informative', int(A.O['informative'].sum()), 'window', S3C_LO, S3C_HI)
    keep, counts, d14 = generate(A, St, P, tag)
    save(keep, counts, d14, tag, set_name, seed)
    log('saved', tag)


T0 = time.time()

if __name__ == '__main__':
    main()
