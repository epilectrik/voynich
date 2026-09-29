#!/usr/bin/env python3
"""PHASE_769 pre-lock (CONTROLS ONLY): power of the paragraph-arm statistic S3P on the ZL transcription structure,
for the paragraph-arm ZL check threshold (E7 rule: >= 0.8 at p <= 0.05 -> 0.05, else 0.10). Synthetic y only."""
from __future__ import annotations

import os

os.environ.setdefault('OMP_NUM_THREADS', '1')

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ed769 as E  # noqa: E402
import ed769b as B  # noqa: E402


def main():
    _, leg = B.hf_alignment()
    recs_z = E.load_b_zl()
    Oz = B.add_structure(B.occurrences2(recs_z, 'e', None))
    bat = B.Battery(Oz, B.folio_covariates(recs_z, Oz, leg))
    rng = np.random.default_rng(769950)
    ps = []
    for rep in range(200):
        y = B.plant(Oz, 'SHARED_PARA', 0.45, rng)
        ps.append(bat.evaluate(y, nperm=1000, seed=775000 + rep, stats=('S3P',))['p_S3P'])
    ps = np.array(ps)
    out = {'sigma': 0.45, 'n_rep': 200, 'power_05': float((ps <= 0.05).mean()), 'power_10': float((ps <= 0.10).mean()),
           'zl_para_threshold': 0.05 if (ps <= 0.05).mean() >= 0.8 else 0.10}
    json.dump(out, open(E.ROOT / 'phases/PHASE_769_E_DIAL_SETTING/results/calib/ZL_PARA_0.45.json', 'w'), indent=1)
    print(out, flush=True)


if __name__ == '__main__':
    main()
