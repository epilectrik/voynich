#!/usr/bin/env python3
"""PHASE_768 pre-lock convergence pilot (CONTROLS ONLY): does N5j reach the E6 gates (R-hat <= 1.05 for RPT_4 and L1,
ESS(RPT_4) >= 100) with longer burn-in and thinning, at beta 2 or 1?
Usage: python prelock_convergence_pilot.py CORPUS SETTING   (CORPUS: codicillus | habit3b; SETTING: s2 | s1)"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402
import hr768v2 as V  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results/convergence_pilot'
OUT.mkdir(parents=True, exist_ok=True)
SETTINGS = {'s2': dict(beta=2.0, burn=6000, anneal=2000, thin=20), 's1': dict(beta=1.0, burn=6000, anneal=2000, thin=20)}


def main(corpus, setting):
    t0 = time.time()
    cfg = SETTINGS[setting]
    HR.BETA = cfg['beta']
    V.BURN, V.ANNEAL, V.THIN = cfg['burn'], cfg['anneal'], cfg['thin']
    sk = HR.b_skeleton()
    n = HR.n_certain(sk)
    if corpus == 'codicillus':
        lines = HR.pour(V.heldout_stream('LAT_codicillus')[:n], sk)
    else:
        lines = V.habit3b_lines(sk, 768799)
    res = V.analyse2(lines, sk, {'TOK': lambda w: w}, units=('JOINT',), seed=769500,
                     log=lambda *a: print(corpus, setting, *a, flush=True))
    res['config'] = cfg
    res['runtime_s'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT / f'{corpus}_{setting}.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
