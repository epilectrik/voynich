#!/usr/bin/env python3
"""PHASE_768 pre-lock calibration, part 4 (CONTROLS ONLY): the strongest local-rule reference under the joint null.

Part 2 showed that a generator with B's class + junction rules (habit2) reaches TOK X3 1.46-1.77 under N5j with no
message. Part 4 adds habit3 (a first-order token model fitted on B, contexts thresholded so rare tokens do not replay
B's sequences), five seeds, and two further habit2 seeds, all under N5j. B supplies its skeleton and local
frequencies; no repeat statistic is computed on B.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    sk = HR.b_skeleton()
    B3 = {'TOK': lambda w: w, 'MID': HR.middle, 'CLS': HR.token_class}
    res = {}
    for s in (768601, 768602, 768603, 768604, 768605):
        log(f'N4 habit3 seed {s}')
        res[f'N4_HABIT3_{s}'] = HR.analyse(HR.habit3_lines(sk, s), sk, B3, units=('JOINT',),
                                           seed=768610 + (s - 768601) * 10, log=log)
        json.dump(res, open(OUT / 'prelock_calibration4.json', 'w'), indent=1)
    for s in (768504, 768505):
        log(f'N3 habit2 seed {s}')
        res[f'N3_HABIT2_{s}'] = HR.analyse(HR.habit2_lines(sk, s), sk, B3, units=('JOINT',),
                                           seed=768510 + (s - 768501) * 10, log=log)
        json.dump(res, open(OUT / 'prelock_calibration4.json', 'w'), indent=1)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_calibration4.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
