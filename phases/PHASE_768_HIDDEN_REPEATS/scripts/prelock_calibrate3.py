#!/usr/bin/env python3
"""PHASE_768 pre-lock calibration, part 3 (CONTROLS ONLY): the joint null N5j on the five word-written NTs, with the
same text windows and the same position-attached spelling markers as part 1 (seeds 768100 + i)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    sk = HR.b_skeleton()
    n = HR.n_certain(sk)
    res = {}
    for i, lang in enumerate(('la', 'it', 'es', 'de', 'en')):
        lines = HR.pour(HR.natural_stream(lang)[:n], sk)
        npos = sum(len(ln) for ln in lines)
        rng = np.random.default_rng(768100 + i)
        extras = {'TOK_k4': ('TOK', rng.integers(0, 4, npos)), 'TOK_k16': ('TOK', rng.integers(0, 16, npos))}
        log(f'P1 WORD_{lang} (joint null)')
        res[f'P1_WORD_{lang}'] = HR.analyse(lines, sk, {'TOK': lambda w: w}, units=('JOINT',),
                                            seed=768110 + 10 * i, extras=extras, log=log)
        json.dump(res, open(OUT / 'prelock_calibration3.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_calibration3.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
