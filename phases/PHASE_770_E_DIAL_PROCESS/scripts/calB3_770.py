#!/usr/bin/env python3
"""PHASE_770 B3 calibration (controls only): the within-page co-drift statistic B3 with the shift null (block lines,
line-type residualisation), per dial and jointly.
H0 plants (400 replicates each): independent drifting components (joint draw: one e-dial draw for all three pairs),
line-state (an iid latent per line shared by both dials) and line-type (both dials shifted on paragraph-final and first
body lines). Calibrated critical |z|: the 99th percentile of max |z| over the three dials under the worst H0 (the
same construction as B2's). Power: shared drifting component (rho 0.7), 200 replicates per dial.
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
import calB770 as CB  # noqa: E402
import calBj770 as BJ  # noqa: E402

OUT = HERE.parent / 'results/calib'
NPERM = 500
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def b3_z(CD, YE, YY, Pi):
    RE, RY = CD.residuals(YE, YY)
    o, n = CD.B3_stat(RE, RY, Pi)
    z, _, p2 = CB.z_and_p(o, n)
    return z, p2


def main():
    pilot = json.load(open(OUT / 'pilot.json'))
    sE, s6 = pilot['grid_S3c']['M1']['s_star'], pilot['grid_S3c']['M6:0.97']['s_star']
    pairs = {}
    for yd in CB.DIALS_Y:
        AE, AY = CB.build_pair(yd)
        pairs[yd] = (AE, AY, CB.CrossDial(AE, AY, split='block'))
    Pi = pairs['CS'][2].relabellings(NPERM, 7795, mode='shift')
    res = {'n_perm': NPERM, 'null': 'shift', 'H0': {}, 'power': {}}
    # joint independent drift
    rng = np.random.default_rng(zlib.crc32(b'b3/drift'))
    Z = {yd: [] for yd in pairs}
    for _ in range(8):
        draws = BJ.joint_draw(pairs, 'drift', s6, 0.6 * s6 / sE, rng, 50)
        for yd, (AE, AY, CD) in pairs.items():
            Z[yd].append(b3_z(CD, *draws[yd], Pi)[0])
    Z = np.stack([np.concatenate(Z[yd]) for yd in pairs])
    res['H0']['drift'] = {'maxabsz_q99': float(np.nanquantile(np.nanmax(np.abs(Z), 0), 0.99)),
                          'per_dial_absz_q99': {yd: float(np.nanquantile(np.abs(Z[i]), 0.99)) for i, yd in enumerate(pairs)}}
    log('drift', res['H0']['drift'])
    # line-state and line-type (per pair; the e-dial draw is per pair here)
    for kind in ('linestate', 'linetype'):
        Zk = []
        for yd, (AE, AY, CD) in pairs.items():
            PP = CB.PairPlants(AE, AY)
            rng = np.random.default_rng(zlib.crc32(f'b3/{kind}/{yd}'.encode()))
            zz = []
            for _ in range(8):
                YE, YY = PP.draw_line(kind, 0.5, rng, 50)
                zz.append(b3_z(CD, YE, YY, Pi)[0])
            Zk.append(np.concatenate(zz))
        Zk = np.stack(Zk)
        res['H0'][kind] = {'maxabsz_q99': float(np.nanquantile(np.nanmax(np.abs(Zk), 0), 0.99)),
                           'per_dial_absz_q99': {yd: float(np.nanquantile(np.abs(Zk[i]), 0.99))
                                                 for i, yd in enumerate(pairs)}}
        log(kind, res['H0'][kind])
    c3 = max(v['maxabsz_q99'] for v in res['H0'].values())
    res['critical_absz'] = c3
    # power: shared drifting component
    for yd, (AE, AY, CD) in pairs.items():
        PP = CB.PairPlants(AE, AY)
        rng = np.random.default_rng(zlib.crc32(f'b3/power/{yd}'.encode()))
        zz = []
        for _ in range(4):
            YE, YY = PP.draw('drift', s6, 0.6 * s6 / sE * 1.0, 0.7, rng, 50)
            zz.append(b3_z(CD, YE, YY, Pi)[0])
        zz = np.concatenate(zz)
        res['power'][yd] = {'absz_ge_crit': float(np.nanmean(np.abs(zz) >= c3))}
        log('power', yd, res['power'][yd])
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'calB3.json', 'w'), indent=1)
    log('critical |z|', c3, 'done')


if __name__ == '__main__':
    main()
