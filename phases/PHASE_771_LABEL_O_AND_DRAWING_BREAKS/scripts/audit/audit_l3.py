#!/usr/bin/env python3
"""PHASE_771 lock audit: separability of the three references after story-specific length matching (text only).
For a label of L glyph units: R_qo from qo-words of L+1 units (unit 3), R_o from o-words of L units (unit 2),
R_init from words of L-1 units (unit 1); lengths capped at 7."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

lines = S.text_lines(Z.load())
cnt = {}
for ln in lines:
    for w in (w for s in ln['segs'] for w in s):
        if not Z.readable(w):
            continue
        u = Z.units(w)
        L = min(len(u), 7)
        for key, ok, idx in (('init', True, 0), ('qo', w.startswith('qo') and len(u) > 2, 2),
                             ('o', u[0] == 'o' and len(u) > 1, 1)):
            if ok:
                cnt.setdefault((key, L), np.zeros(len(S.CATS)))[S.CIDX[S.cat(u[idx])]] += 1
dist = lambda v: (v + 0.5) / (v + 0.5).sum()


def jsd(p, q):
    m = 0.5 * (p + q)
    return 0.5 * float(np.sum(p * np.log2(p / m))) + 0.5 * float(np.sum(q * np.log2(q / m)))


for L in range(2, 8):
    q, o, i = cnt[('qo', min(L + 1, 7))], cnt[('o', L)], cnt[('init', L - 1)]
    pq, po, pi = dist(q), dist(o), dist(i)
    kl = float(np.sum(po * np.log2(po / pq)))
    print(f'label length {L}{"+" if L == 7 else ""}: n qo/o/init {int(q.sum())}/{int(o.sum())}/{int(i.sum())}; '
          f'JSD qo-o {jsd(pq, po):.3f} (KL o||qo {kl:.2f} bits), o-init {jsd(po, pi):.3f}, qo-init {jsd(pq, pi):.3f}')
