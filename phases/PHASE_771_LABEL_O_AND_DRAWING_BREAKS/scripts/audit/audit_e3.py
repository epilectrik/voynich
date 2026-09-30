#!/usr/bin/env python3
"""PHASE_771 lock audit, Arm E: false-call rates at the 1/3 and 2/3 boundaries (corrected edge classes) and
dependence of I on the cross-fitting split seed. Synthetic draws from unbroken lines only (blind)."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_e as AE  # noqa: E402
import stats771 as S  # noqa: E402

rng = np.random.default_rng(4444)
words, breaks, pools, draw = AE.words, AE.breaks, AE.pools, AE.draw
for lang, side in (('A', 'start'), ('A', 'end'), ('B', 'start')):
    W = [w for w in words if w['lang'] == lang]
    flag = 'ps' if side == 'start' else 'pe'
    edge_pos = (lambda w: w['i_start'] == 0) if side == 'start' else (lambda w: w['i_end'] == 0)
    Wc = [w for w in W if not (edge_pos(w) and w[flag])]
    arm = S.EdgeArm(Wc, breaks, lang, side, seed=771)
    P = pools(W, side)
    for pi in (2 / 3, 1 / 3):
        c = Counter()
        for _ in range(60):
            units = [draw(b, side, 'cont_edge' if rng.random() < pi else 'mid', P, rng) for b in arm.breaks]
            c[arm.evaluate(units, B=300, rng=rng)['call']] += 1
        print(f'{lang} {side} corrected, truth pi={pi:.2f}: {dict(c)}', flush=True)
    # split-seed dependence of the point estimate for one fixed synthetic pi=1/2 dataset
    units = [draw(b, side, 'cont_edge' if rng.random() < 0.5 else 'mid', P, rng) for b in arm.breaks]
    Is = [S.EdgeArm(Wc, breaks, lang, side, seed=s).evaluate(units, B=20, rng=rng)['I'] for s in range(771, 781)]
    print(f'{lang} {side} split seeds 771-780, same synthetic words: I range {min(Is):.3f}..{max(Is):.3f}, '
          f'sd {np.std(Is):.3f}', flush=True)
