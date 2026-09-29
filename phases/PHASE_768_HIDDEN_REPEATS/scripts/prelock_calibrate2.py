#!/usr/bin/env python3
"""PHASE_768 pre-lock calibration, part 2 (CONTROLS ONLY): the joint null N5j and stronger negative controls.

First calibration: a class-rule generator (habit) showed TOK 3-gram excess under the glyph null N5g (X3 2.72) that
vanished under the class null N5c. B has both kinds of local rule, so both single-rule nulls could be fooled at once.
Part 2 adds:
  N5j: junction units = (class, edge glyph) jointly, preserving class bigrams, glyph junctions and their interaction;
  habit2: a generator with BOTH rules (next token drawn from B conditioned on the previous token's class and last
          glyph), three seeds; habit (class rules only), two further seeds;
and runs N5j on the Naibbe positives and on Timm. B supplies its skeleton and, for the generators, its local
frequencies; no repeat statistic is computed on B.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    sk = HR.b_skeleton()
    n = HR.n_certain(sk)
    ident = lambda w: w  # noqa: E731
    B3 = {'TOK': ident, 'MID': HR.middle, 'CLS': HR.token_class}
    res = {}
    for j, pid in enumerate(('P-REC', 'P-PHA', 'P-ITA')):
        toks, chunks = HR.naibbe_stream(pid, 768001 + j, n)          # identical streams to part 1
        votes = defaultdict(Counter)
        for t, c in zip(toks, chunks):
            votes[t][c] += 1
        oracle = {t: c.most_common(1)[0][0] for t, c in votes.items()}
        log(f'P3 Naibbe {pid} (joint null)')
        res[f'P3_NAIBBE_{pid}'] = HR.analyse(HR.pour(toks, sk), sk, dict(B3, ORACLE=lambda w: oracle.get(w, w)),
                                             units=('JOINT',), seed=768210 + 10 * j, log=log)
        json.dump(res, open(OUT / 'prelock_calibration2.json', 'w'), indent=1)
    for s in (768302, 768303):
        log(f'N2 habit seed {s}')
        res[f'N2_HABIT_{s}'] = HR.analyse(HR.habit_lines(sk, s), sk, B3, units=('GLYPH', 'CLASS', 'JOINT'),
                                          seed=768310 + (s - 768301) * 10, log=log)
        json.dump(res, open(OUT / 'prelock_calibration2.json', 'w'), indent=1)
    log('N2 habit seed 768301 (joint null only; GLYPH/CLASS in part 1)')
    res['N2_HABIT_768301'] = HR.analyse(HR.habit_lines(sk, 768301), sk, B3, units=('JOINT',), seed=768310, log=log)
    for s in (768501, 768502, 768503):
        log(f'N3 habit2 seed {s}')
        res[f'N3_HABIT2_{s}'] = HR.analyse(HR.habit2_lines(sk, s), sk, B3, units=('GLYPH', 'CLASS', 'JOINT'),
                                           seed=768510 + (s - 768501) * 10, log=log)
        json.dump(res, open(OUT / 'prelock_calibration2.json', 'w'), indent=1)
    log('N1 Timm (joint null)')
    res['N1_TIMM'] = HR.analyse(HR.timm_lines(sk, 767101), sk, B3, units=('JOINT',), seed=768410, log=log)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_calibration2.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
