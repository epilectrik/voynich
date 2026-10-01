"""PHASE_778 per-variant banding (surface statistics only; confirmation-pass edit 2).

Configurations are selected per walk group and shared across row arrangements, but a variant's composition can differ
from its group's (with small vertical moves and the line reset, the walk visits only part of the rows, so freq-,
length- and chain-ordered rows place different content in the visited cells; V1 noise edits tokens). Each variant is
therefore banded on its own fresh 10-seed distance, with its own row arrangement and noise level. Bands are reported
under the declared bar (FITTED <= 1.0) and the calibrated bar (FITTED <= the larger positive-control distance, C2).

Output: results/variant_bands778.json.  Usage: python band778.py [workers]
"""
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import run778 as R  # noqa: E402

N_FRESH = 10
SEED_BAND = 778_650_000


def _init():
    R._init()


def one(args):
    vi, name, family, cfg, noise = args
    X, sk = R._W['X'], R._W['sk']
    b = X.load_b(sk)
    inv = R._W['inv'][cfg['parser']]
    fam = {k: family[k] for k in ('order', 'd', 'pos', 'repeat', 'redraw')}
    ss = []
    for m in range(N_FRESH):
        rng = np.random.default_rng(SEED_BAND + 100 * vi + m)
        lines, info = X.generate(sk, inv, {**fam, **cfg}, rng)
        if noise == 'V1':
            lines = X.H757.apply_noise(lines, R._W['noise'], rng)
        ss.append(X.surface(lines, sk['folio'], b, inv['types']))
    mean = {k: float(np.mean([s[k] for s in ss])) for k in ss[0]}
    dev = X.deviations(mean, b)
    dist = X.distance(mean, b)
    return name, {'surface': mean, 'deviations': dev, 'distance': dist, 'band_declared': X.band(dist, 1.0),
                  'band': X.band(dist), 'dominant': max(dev, key=dev.get),
                  'dominant_share': max(dev.values()) / sum(dev.values())}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    t0 = time.time()
    R._init()
    X = R._W['X']
    fit = json.load(open(OUT / 'fit778.json', encoding='utf-8'))
    vs = []
    for fam in R.F.families():
        g = fit['groups'][R.F.group_name(fam)]
        for noise in R.NOISES:
            vs.append((len(vs), f"{R.F.family_name(fam)}/{noise}", fam, g['best']['cfg'], noise))
    out = {}
    with Pool(workers, initializer=_init) as pool:
        for i, (name, r) in enumerate(pool.imap_unordered(one, vs, chunksize=2)):
            out[name] = r
            print(f"[{time.time() - t0:5.0f}s] {name:58s} dist {r['distance']:.3f} {r['band']:8s} (declared {r['band_declared']}) "
                  f"dominant {r['dominant']} {r['dominant_share']:.2f}", flush=True)
    res = {'variants': out, 'N_FRESH': N_FRESH, 'seed': SEED_BAND, 'fitted_bound': X.fitted_bound(),
           'bands_calibrated': {b_: sum(1 for r in out.values() if r['band'] == b_) for b_ in ('FITTED', 'PARTIAL', 'UNFITTED')},
           'bands_declared': {b_: sum(1 for r in out.values() if r['band_declared'] == b_) for b_ in ('FITTED', 'PARTIAL', 'UNFITTED')},
           'runtime_s': time.time() - t0}
    json.dump(res, open(OUT / 'variant_bands778.json', 'w', encoding='utf-8'), indent=1)
    print('done', res['bands_calibrated'], res['bands_declared'], flush=True)


if __name__ == '__main__':
    main()
