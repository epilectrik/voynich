#!/usr/bin/env python3
"""PHASE_771 lock audit, Arm E follow-up. Blind as audit_e.py (positions only; synthetic draws from unbroken lines).
(a) E-seg call rate of the design AS WRITTEN when the true break words are continuation-line edges (not paragraph
    openers / closers); (b) mean I of matched mid words drawn from paragraph-first (header) lines vs body lines;
(c) corrected-design power for A end and B end with more simulations.
"""
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_e as AE  # noqa: E402  (re-runs audit_e's quick parts on import; cheap)
import stats771 as S  # noqa: E402

t0 = time.time()
rng = np.random.default_rng(4343)
words, breaks, pools, draw = AE.words, AE.breaks, AE.pools, AE.draw


def hdr_pools(W, side, hdr):
    return pools([w for w in W if w['ps'] == hdr], side)


for lang in ('A', 'B'):
    W = [w for w in words if w['lang'] == lang]
    for side in ('start', 'end'):
        arm = S.EdgeArm(W, breaks, lang, side, seed=771)
        P = pools(W, side)
        calls, Is = Counter(), []
        for _ in range(60):
            r = arm.evaluate([draw(b, side, 'cont_edge', P, rng) for b in arm.breaks], B=300, rng=rng)
            calls[r['call']] += 1
            Is.append(r['I'])
        Ph, Pb = hdr_pools(W, side, True), hdr_pools(W, side, False)
        ih = np.mean([arm.evaluate([draw(b, side, 'mid', Ph, rng) for b in arm.breaks], B=20, rng=rng)['I']
                      for _ in range(10)])
        ib = np.mean([arm.evaluate([draw(b, side, 'mid', Pb, rng) for b in arm.breaks], B=20, rng=rng)['I']
                      for _ in range(10)])
        print(f'(a) {lang} {side} AS WRITTEN, truth = continuation-line edges: calls {dict(calls)}, '
              f'mean I {np.mean(Is):.3f}  |  (b) matched mid from header lines I={ih:.3f}, body lines I={ib:.3f}')
print('elapsed', round(time.time() - t0, 1), 's')

for lang, side in (('A', 'end'), ('B', 'end'), ('A', 'start')):
    W = [w for w in words if w['lang'] == lang]
    flag = 'ps' if side == 'start' else 'pe'
    edge_pos = (lambda w: w['i_start'] == 0) if side == 'start' else (lambda w: w['i_end'] == 0)
    arm = S.EdgeArm([w for w in W if not (edge_pos(w) and w[flag])], breaks, lang, side, seed=771)
    P = pools(W, side)
    out = {}
    for truth, kind, target in (('seg', 'cont_edge', 'E-seg'), ('line', 'mid', 'E-line')):
        c = Counter(arm.evaluate([draw(b, side, kind, P, rng) for b in arm.breaks], B=300, rng=rng)['call']
                    for _ in range(120))
        out[truth] = round(c[target] / 120, 3)
    print(f'(c) {lang} {side} corrected design, 120 sims: correct-call rate {out}')
print('elapsed', round(time.time() - t0, 1), 's')
