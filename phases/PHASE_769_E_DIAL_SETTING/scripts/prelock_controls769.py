#!/usr/bin/env python3
"""PHASE_769 pre-lock calibration (CONTROLS ONLY; no statistic is computed on B's real run lengths by folio).

Negative controls laid into B's H-track records (same folios, lines, paragraphs, sections, hands):
  Naibbe GV1 cipher of a real plaintext (spelling variants chosen at random: no setting);
  habit3b, a first-order local-rule generator fitted to B (no folio dependence);
  Timm-Schinner self-citation (copies and mutates earlier words of the folio: word-level reuse, possibly spelling
  inheritance across frames).
Planted controls on B's cell structure: synthetic y ~ Bernoulli(sigmoid(logit(p_cell) + delta)), p_cell = B's cell
rate clipped to [0.01, 0.99] (no folio information), with
  SHARED:  delta = d_folio ~ N(0, sigma^2)            (a folio-level setting shared across words), and
  WORDSPEC: delta = d_(frame, folio) ~ N(0, sigma^2)  (word-specific folio effects, no shared component).
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

OUT = E.ROOT / 'phases/PHASE_769_E_DIAL_SETTING/results'
OUT.mkdir(parents=True, exist_ok=True)
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def control_streams(n):
    import hr768 as HR
    import hr768v2 as V
    sk = HR.b_skeleton()
    flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
    out = {'NAIBBE_P-REC': HR.naibbe_stream('P-REC', 769001, n)[0],
           'HABIT3B': flat(V.habit3b_lines(sk, 769101)),
           'TIMM': flat(HR.timm_lines(sk, 769201))}
    for k, v in out.items():
        assert len(v) == n, (k, len(v), n)
    return out


def planted_y(O, sigma, mode, rng):
    p = np.clip(E.cell_means(O['y'], O['cell']), 0.01, 0.99)
    logit = np.log(p / (1 - p))
    if mode == 'SHARED':
        d = rng.normal(0, sigma, len(O['folio_names']))[O['folio']]
    else:
        key = O['frame'] * 1000 + O['folio']
        _, inv = np.unique(key, return_inverse=True)
        d = rng.normal(0, sigma, inv.max() + 1)[inv.ravel()]
    return (rng.random(len(p)) < 1 / (1 + np.exp(-(logit + d)))).astype(float)


def main():
    recs = E.load_b_h()
    n = len(recs)
    res = {'negative': {}, 'planted': {}}
    for name, stream in control_streams(n).items():
        rc = E.pour_tokens(recs, stream)
        res['negative'][name] = {}
        for kind in ('e', 'i'):
            O = E.occurrences(rc, kind)
            for level in ('folio', 'paragraph'):
                r = E.test(O, level, nperm=2000, seed=769300)
                res['negative'][name][f'{kind}_{level}'] = r
                log(f'{name:13s} {kind}-runs {level:9s}: occ {r["n_occ"]:5d} S1 ratio {r["S1_ratio"]:.3f} p {r["p_S1"]:.3f} '
                    f'| S2 {r["S2"]:+.3f} (null {r["S2_null_mean"]:+.3f} sd {r["S2_null_sd"]:.3f}) p {r["p_S2"]:.3f}')
        json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)
    # planted power / size on B's cell structure (synthetic y only)
    O = E.occurrences(recs, 'e')
    rng = np.random.default_rng(769400)
    for mode in ('SHARED', 'WORDSPEC'):
        for sigma in ((0.0, 0.15, 0.25, 0.35, 0.5) if mode == 'SHARED' else (0.25, 0.5, 1.0)):
            rows = []
            for rep in range(40):
                y = planted_y(O, sigma, mode, rng)
                r = E.test(O, 'folio', nperm=400, seed=769500 + rep, y=y)
                rows.append((r['p_S1'], r['p_S2'], r['S2']))
            a = np.array(rows)
            res['planted'][f'{mode}_{sigma}'] = {'power_S1_05': float((a[:, 0] <= 0.05).mean()),
                                                 'power_S2_05': float((a[:, 1] <= 0.05).mean()),
                                                 'power_S2_01': float((a[:, 1] <= 0.01).mean()),
                                                 'S2_mean': float(a[:, 2].mean())}
            log(f'planted {mode:8s} sigma {sigma:.2f}: S1 power {res["planted"][f"{mode}_{sigma}"]["power_S1_05"]:.2f} '
                f'S2 power(.05) {res["planted"][f"{mode}_{sigma}"]["power_S2_05"]:.2f} '
                f'(.01) {res["planted"][f"{mode}_{sigma}"]["power_S2_01"]:.2f} mean S2 {a[:, 2].mean():+.3f}')
            json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
