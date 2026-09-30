#!/usr/bin/env python3
"""PHASE_770 Arm B joint certification (controls only), after the 1,000-replicate certification showed the pairing null
anti-conservative under independent drifting components (random relabelling: size 0.026 at alpha 0.01; the spread of X
across H0 replicates exceeds the null's by 16%, or 10% with circular shifts; results/calib/calB_relabel_null.json).

Joint plants: one e-dial draw shared by all three pairs (as in the run), each Y dial with its own independent component
(no sharing). Statistic per replicate: X per dial, the shift null (circular shifts within stratum, one relabelling for all
dials), z per dial and the Westfall-Young adjusted p (max |z| over dials).
  H0 conditions: independent drift (M6 rho 0.97 along chains; E at B's strength, Y at 0.6-scaled strength) and
  independent folio-level components (E at s*, Y at 0.4); 1,000 replicates (drift) and 500 (folio).
  Calibrated threshold alpha*: the largest adjusted-p threshold with P(any dial SHARED) <= 0.01 under the worst H0.
Power at alpha*: pair plants with sharing (rho 0.7) in the tested dial, folio-level (Y 0.35, 0.5) and drifting (Y 0.6),
for both splits (half, block), 200 replicates each; the split is fixed at lock by power under drift.
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

OUT = HERE.parent / 'results/calib'
NPERM = 500
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def joint_draw(pairs, kind, sE, sY, rng, B_):
    """One e-dial draw shared by all pairs; each Y dial independent (no sharing)."""
    yds = list(pairs)
    AE0 = pairs[yds[0]][0]
    PE = C.Plants(AE0)
    if kind == 'folio':
        u = PE.f_page_const(rng, B_)
    else:
        u = PE.f_ar1_chain(rng, B_, 0.97)
    zE = PE._normalise(u[AE0.occ_line])
    lgE = PE.lg[:, None] + zE * sE
    YE = (rng.random(lgE.shape) < 1 / (1 + np.exp(-lgE))).astype(float)
    out = {}
    for yd in yds:
        AE, AY, CD = pairs[yd]
        assert len(AE.O['y']) == len(AE0.O['y'])
        PY = C.Plants(AY)
        v = PY.f_page_const(rng, B_) if kind == 'folio' else PY.f_ar1_chain(rng, B_, 0.97)
        zY = PY._normalise(v[AY.occ_line])
        lgY = PY.lg[:, None] + zY * sY
        YY = (rng.random(lgY.shape) < 1 / (1 + np.exp(-lgY))).astype(float)
        out[yd] = (YE, YY)
    return out


def adjusted_p(pairs, draws, Pi):
    """Per replicate: per-dial two-sided p (shift null) and Westfall-Young adjusted p."""
    zo, zn, p2 = {}, {}, {}
    for yd, (AE, AY, CD) in pairs.items():
        YE, YY = draws[yd]
        RE, RY = CD.residuals(YE, YY)
        o, n = CD.X_stat(RE, RY, Pi)
        z, zn_, pp = CB.z_and_p(o, n)
        zo[yd], zn[yd], p2[yd] = z, zn_, pp
    mx = np.max(np.abs(np.stack([zn[yd] for yd in pairs], axis=0)), axis=0)       # (P, B)
    pwy = {yd: (1 + (mx >= np.abs(zo[yd])[None, :]).sum(0)) / (1 + mx.shape[0]) for yd in pairs}
    return p2, pwy, zo


def main():
    pilot = json.load(open(OUT / 'pilot.json'))
    sE, s6 = pilot['grid_S3c']['M1']['s_star'], pilot['grid_S3c']['M6:0.97']['s_star']
    split_arg = sys.argv[1] if len(sys.argv) > 1 else None
    part = sys.argv[2] if len(sys.argv) > 2 else 'all'          # 'cert', 'power' or 'all'
    splits = (split_arg,) if split_arg else ('half', 'block')
    tag = (f'_{split_arg}' if split_arg else '') + ('' if part == 'all' else f'_{part}')
    res = {'n_perm': NPERM, 'null': 'shift', 'certification': {}, 'power': {}}
    for split in splits:
        pairs = {}
        for yd in CB.DIALS_Y:
            AE, AY = CB.build_pair(yd)
            pairs[yd] = (AE, AY, CB.CrossDial(AE, AY, split=split))
        Pi = pairs['CS'][2].relabellings(NPERM, 7790, mode='shift')
        # ---- H0 certification (joint)
        for kind, n_rep, sY in ((('drift', 1000, 0.6 * s6 / sE), ('folio', 500, 0.4)) if part in ('all', 'cert') else ()):
            rng = np.random.default_rng(zlib.crc32(f'cert/{split}/{kind}'.encode()))
            P2, PWY, ZO = {yd: [] for yd in pairs}, {yd: [] for yd in pairs}, {yd: [] for yd in pairs}
            for _ in range(n_rep // 50):
                draws = joint_draw(pairs, kind, s6 if kind == 'drift' else sE, sY, rng, 50)
                p2, pwy, zo = adjusted_p(pairs, draws, Pi)
                for yd in pairs:
                    P2[yd].append(p2[yd])
                    PWY[yd].append(pwy[yd])
                    ZO[yd].append(zo[yd])
            P2 = {yd: np.concatenate(v) for yd, v in P2.items()}
            PWY = {yd: np.concatenate(v) for yd, v in PWY.items()}
            ZO = {yd: np.concatenate(v) for yd, v in ZO.items()}
            np.savez(OUT / f'calBj_raw_{split}_{kind}.npz', **{f'p2_{yd}': P2[yd] for yd in pairs},
                     **{f'pwy_{yd}': PWY[yd] for yd in pairs}, **{f'z_{yd}': ZO[yd] for yd in pairs})
            maxz = np.nanmax(np.abs(np.stack([ZO[yd] for yd in pairs])), axis=0)
            res.setdefault('maxabsz_quantiles', {})[f'{split}/{kind}'] = {
                str(q): float(np.nanquantile(maxz, q)) for q in (0.95, 0.99, 0.995)}
            minwy = np.min(np.stack([PWY[yd] for yd in pairs]), axis=0)
            thr = {str(a): float((minwy <= a).mean()) for a in (0.01, 0.005, 0.0033, 0.002, 0.001)}
            res['certification'][f'{split}/{kind}'] = {
                'n_rep': int(len(minwy)), 'any_dial_WY_le': thr,
                'per_dial_p2_le_01': {yd: float((P2[yd] <= 0.01).mean()) for yd in pairs},
                'minwy_quantiles': {str(q): float(np.quantile(minwy, q)) for q in (0.005, 0.01, 0.02)}}
            log(split, kind, res['certification'][f'{split}/{kind}'])
            json.dump(res, open(OUT / f'calBj{tag}.json', 'w'), indent=1)
        # ---- power per dial (pair plants with sharing rho 0.7 in the tested dial)
        for yd, (AE, AY, CD) in (pairs.items() if part in ('all', 'power') else ()):
            PP = CB.PairPlants(AE, AY)
            for kind, sY in (('folio', 0.35), ('folio', 0.5), ('drift', 0.6)):
                rng = np.random.default_rng(zlib.crc32(f'power/{split}/{yd}/{kind}/{sY}'.encode()))
                ps, zs = [], []
                for _ in range(4):
                    YE, YY = PP.draw(kind, sE if kind == 'folio' else s6,
                                     sY if kind == 'folio' else sY * s6 / sE, 0.7, rng, 50)
                    RE, RY = CD.residuals(YE, YY)
                    o, n = CD.X_stat(RE, RY, Pi)
                    zz, _, pp = CB.z_and_p(o, n)
                    ps.append(pp)
                    zs.append(zz)
                ps, zs = np.concatenate(ps), np.concatenate(zs)
                np.save(OUT / f'calBj_power_z_{split}_{yd}_{kind}_{sY}.npy', zs)
                res['power'][f'{split}/{yd}/{kind}/{sY}'] = {a: float((ps <= float(a)).mean())
                                                             for a in ('0.01', '0.0033', '0.002', '0.001')}
                res['power'][f'{split}/{yd}/{kind}/{sY}']['absz_ge'] = {str(c): float((np.abs(zs) >= c).mean())
                                                                       for c in (2.8, 3.0, 3.2, 3.4, 3.6)}
                log(split, yd, kind, sY, res['power'][f'{split}/{yd}/{kind}/{sY}'])
                json.dump(res, open(OUT / f'calBj{tag}.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / f'calBj{tag}.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
