#!/usr/bin/env python3
"""PHASE_768 pre-lock probe (CONTROLS ONLY): X3 / X4 of the held-out word-written texts under the single-chain N5j
protocol of calibration parts 1-4, to see whether the NT-based threshold (T4 = 11.49) carries over to other texts.
Usage: python prelock_heldout_probe.py NAME  (one held-out text per process)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402
import hr768v2 as V  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results/heldout_probe'
OUT.mkdir(parents=True, exist_ok=True)


def main(name):
    t0 = time.time()
    sk = HR.b_skeleton()
    n = HR.n_certain(sk)
    words = V.heldout_stream(name)[:n]
    res = HR.analyse(HR.pour(words, sk), sk, {'TOK': lambda w: w}, units=('JOINT',), seed=769000 + V.HELDOUT.index(name),
                     log=lambda *a: print(name, *a, flush=True))
    res['runtime_s'] = round(time.time() - t0, 1)
    res['first_words'] = words[:40]
    json.dump(res, open(OUT / f'{name}.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
