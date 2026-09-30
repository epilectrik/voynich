#!/usr/bin/env python3
"""PHASE_770 Arm A threshold calibration (controls only): the gate at grid points near B's likely values under
alternative verdict thresholds (class posterior, new-part Bayes factor), with two mixture rules:
  literal : 25% mixtures must reach POSITION-DEPENDENT in <= 15%, 75% mixtures STATIC in <= 15% (lean-expert v2)
  by_d14  : a mixture is gated by its own D14 class (S: POSITION-DEPENDENT <= 15%; P: STATIC <= 15%; I: not gated)
Pure models: own class >= 70%, wrong class <= 5% (n >= 30 evaluation replicates within +-0.03 of the point).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clf770 as K  # noqa: E402

BANK = HERE.parent / 'results/calib/bank'
POINTS = [(c, f) for c in (0.30, 0.32, 0.34) for f in (0.06, 0.09, 0.12)]
THRESH = [(0.8, 3), (0.9, 3), (0.9, 10), (0.95, 10), (0.95, 30), (0.98, 30)]


def main():
    tag = sys.argv[1]
    bank = dict(np.load(BANK / f'bank_{tag}.npz'))
    info = json.load(open(BANK / f'bank_{tag}.json'))
    d14 = info['D14']
    out = {}
    for version in ('raw', 'free'):
        clf = K.Classifier(bank, info, version)
        # scores for every model's evaluation replicates near each point
        scored = {}
        for m, cls in clf.classes.items():
            ev = clf.split[m][2]
            Zev = clf.Z[ev]
            s = clf.score(Zev)
            scored[m] = (Zev, s)
        for pthr, bthr in THRESH:
            for rule in ('literal', 'by_d14'):
                res_pts = {}
                for c3, cf in POINTS:
                    ok, fails = True, []
                    for m, cls in clf.classes.items():
                        Zev, s = scored[m]
                        sel = (np.abs(Zev[:, 0] - c3) <= 0.03) & (np.abs(Zev[:, 1] - cf) <= 0.03)
                        if sel.sum() < 30:
                            continue
                        pS, lbf, fit = s['pS'][sel], s['log_bf_new'][sel], s['fit_ok'][sel]
                        vS = (pS >= pthr) & (lbf >= np.log(bthr)) & fit
                        vP = (pS <= 1 - pthr) & (lbf <= -np.log(bthr)) & fit
                        fS, fP = vS.mean(), vP.mean()
                        eff = cls
                        if cls == 'X':
                            if rule == 'literal':
                                eff = 'XS' if m.endswith('/0.25') else ('XP' if m.endswith('/0.75') else None)
                            else:
                                eff = 'XS' if d14[m] <= 0.15 else ('XP' if d14[m] >= 0.5 else None)
                        if eff == 'S' and not (fS >= 0.70 and fP <= 0.05):
                            ok = False; fails.append(f'{m}({fS:.2f}/{fP:.2f})')
                        elif eff == 'P' and not (fP >= 0.70 and fS <= 0.05):
                            ok = False; fails.append(f'{m}({fS:.2f}/{fP:.2f})')
                        elif eff == 'XS' and fP > 0.15:
                            ok = False; fails.append(f'{m}({fS:.2f}/{fP:.2f})')
                        elif eff == 'XP' and fS > 0.15:
                            ok = False; fails.append(f'{m}({fS:.2f}/{fP:.2f})')
                    res_pts[f'{c3:.2f}/{cf:.2f}'] = {'pass': ok, 'fails': fails}
                key = f'{version} post>={pthr} BF>={bthr} {rule}'
                out[key] = res_pts
                npass = sum(v['pass'] for v in res_pts.values())
                print(f'{key:40s} passes {npass}/{len(POINTS)}  ' +
                      '; '.join(f"{p}: {','.join(v['fails'][:3])}" for p, v in res_pts.items() if not v['pass'])[:260])
    json.dump(out, open(BANK / f'thr_{tag}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
