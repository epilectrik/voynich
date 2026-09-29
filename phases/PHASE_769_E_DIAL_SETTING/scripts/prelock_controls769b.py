#!/usr/bin/env python3
"""PHASE_769 pre-lock calibration, round 2 (CONTROLS ONLY): the long-range statistic S3.

Round 1 showed that the cross-frame statistic S2 is fooled by local persistence (habit3b, a first-order generator
with no folio dependence: S2 p = 0.029). S3 correlates frame-half A in a folio's top half of lines with frame-half B in
its bottom half, which local persistence cannot produce. Controls (B's own run lengths by folio are not used):
  negatives: Naibbe GV1 (random spelling variants), habit3b x3 seeds, Timm-Schinner;
  planted on B's cell structure (synthetic y): SHARED folio setting (sigma grid, incl. 0 = size), WORDSPEC
  (frame x folio effects, no shared part), LOCAL (strong first-order persistence along the text, no folio setting).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'PHASE_768_HIDDEN_REPEATS/scripts'))
import ed769 as E  # noqa: E402
import prelock_controls769 as P1  # noqa: E402

OUT = E.ROOT / 'phases/PHASE_769_E_DIAL_SETTING/results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def local_y(O, phi, rng):
    """Strong first-order persistence: each occurrence's logit shifts by phi * (previous residual) when the previous
    occurrence is in the same folio; no folio-level component."""
    p = np.clip(E.cell_means(O['y'], O['cell']), 0.01, 0.99)
    lg = np.log(p / (1 - p))
    y = np.zeros(len(p))
    prev_res, prev_f = 0.0, -1
    for t in range(len(p)):
        shift = phi * prev_res if O['folio'][t] == prev_f else 0.0
        q = 1 / (1 + np.exp(-(lg[t] + shift)))
        y[t] = float(rng.random() < q)
        prev_res, prev_f = y[t] - p[t], O['folio'][t]
    return y


def fmt(r):
    return (f"S1 ratio {r['S1_ratio']:.3f} p {r['p_S1']:.3f} | S2 {r['S2']:+.3f} p {r['p_S2']:.3f} | "
            f"S3 {r['S3']:+.3f} (null {r['S3_null_mean']:+.3f} sd {r['S3_null_sd']:.3f}) p {r['p_S3']:.3f}")


def main():
    import hr768 as HR
    import hr768v2 as V
    recs = E.load_b_h()
    n = len(recs)
    sk = HR.b_skeleton()
    flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
    streams = {'NAIBBE_P-REC': HR.naibbe_stream('P-REC', 769001, n)[0], 'TIMM': flat(HR.timm_lines(sk, 769201))}
    for s in (769101, 769102, 769103):
        streams[f'HABIT3B_{s}'] = flat(V.habit3b_lines(sk, s))
    res = {'negative': {}, 'planted': {}}
    for name, stream in streams.items():
        O = E.occurrences(E.pour_tokens(recs, stream), 'e')
        r = E.test3(O, nperm=1000, seed=769600)
        res['negative'][name] = r
        log(f'{name:15s} occ {r["n_occ"]:5d} | {fmt(r)}')
        json.dump(res, open(OUT / 'prelock_controls_b.json', 'w'), indent=1)
    O = E.occurrences(recs, 'e')
    halves_ok = {h: int((O['half'][O['informative']] == h).sum()) for h in (0, 1)}
    log('B cell structure: informative occurrences by folio half', halves_ok)
    rng = np.random.default_rng(769700)
    plans = [('SHARED', s) for s in (0.0, 0.15, 0.25, 0.35, 0.5)] + [('WORDSPEC', 0.5), ('WORDSPEC', 1.0)] + \
            [('LOCAL', 1.5), ('LOCAL', 3.0)]
    for mode, sg in plans:
        rows = []
        for rep in range(40):
            y = local_y(O, sg, rng) if mode == 'LOCAL' else P1.planted_y(O, sg, mode, rng)
            r = E.test3(O, nperm=300, seed=769800 + rep, y=y, k_splits=20)
            rows.append((r['p_S1'], r['p_S2'], r['p_S3'], r['S3']))
        a = np.array(rows)
        res['planted'][f'{mode}_{sg}'] = {f'power_{k}_05': float((a[:, i] <= 0.05).mean())
                                           for i, k in enumerate(('S1', 'S2', 'S3'))}
        res['planted'][f'{mode}_{sg}']['power_S3_01'] = float((a[:, 2] <= 0.01).mean())
        res['planted'][f'{mode}_{sg}']['S3_mean'] = float(a[:, 3].mean())
        log(f'planted {mode:8s} {sg:.2f}: power(.05) S1 {res["planted"][f"{mode}_{sg}"]["power_S1_05"]:.2f} '
            f'S2 {res["planted"][f"{mode}_{sg}"]["power_S2_05"]:.2f} S3 {res["planted"][f"{mode}_{sg}"]["power_S3_05"]:.2f} '
            f'(S3 .01 {res["planted"][f"{mode}_{sg}"]["power_S3_01"]:.2f}) mean S3 {a[:, 3].mean():+.3f}')
        json.dump(res, open(OUT / 'prelock_controls_b.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_controls_b.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
