#!/usr/bin/env python3
"""PHASE_772 lock audit: verdict rules under inventory/palette mixtures, built entirely from Currier A words
(no zodiac label forms are used). Thresholds are the smoke-calibration N2 values."""
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zod772 as Z  # noqa: E402

sys.path.insert(0, str(Z.ROOT))
from scripts.voynich import Transcript  # noqa: E402

rng = np.random.default_rng(5)
aw = Counter(t.word for t in Transcript().currier_a() if t.word and re.fullmatch(r'[a-z]+', t.word))
pool = [w for w in aw if 4 <= len(Z.GLYPH_RE.findall(Z.n1(w))) <= 8]
sizes = [28, 30, 30, 29, 28, 29, 30, 27, 30, 29]
Q01 = {'0.0': 1.0, '0.5': 0.894, '1.0': 0.839, '2.0': 0.8, '3.0': 0.746}
Q05_3 = 0.748
NPERM = 200


def p_low_high(forms, signs):
    st = Z.dup_stats(forms, signs)
    if not np.isfinite(st['W']):
        return st, 1.0, 1.0
    null = Z.perm_W(forms, signs, rng, NPERM)
    return st, (1 + np.sum(null <= st['W'])) / (NPERM + 1), (1 + np.sum(null >= st['W'])) / (NPERM + 1)


def verdict(fs, ss):
    s1, l1, h1 = p_low_high([Z.n1(w) for w in fs], ss)
    s2, l2, h2 = p_low_high([Z.n2(w) for w in fs], ss)
    inv = l1 < .01 and l2 < .01 and s2['R'] >= Q05_3
    lam = None
    for k in Q01:
        if s2['R'] < Q01[k]:
            lam = k
    noinv = lam is not None and not (l1 < .01 and l2 < .01)
    pal = h1 < .01
    calls = [c for c, b in (('INV', inv), (f'NOINV({lam})', noinv), ('PAL', pal)) if b] or ['UNRES']
    return '+'.join(calls), s2['R']


def sim(phi, remainder):
    base = list(rng.choice(pool, size=30, replace=False))
    fs, ss = [], []
    for si, n in enumerate(sizes):
        k_inv = int(round(phi * n))
        pal = list(rng.choice(pool, size=8, replace=False))
        pos = rng.permutation(30)[:k_inv]
        for k in pos:
            fs.append(Z.edits(base[k], rng, 1.0))
            ss.append(si)
        for _ in range(n - k_inv):
            if remainder == 'palette':
                fs.append(Z.edits(pal[rng.integers(8)], rng, 1.0))
            else:
                fs.append(str(rng.choice(pool)))
            ss.append(si)
    return fs, ss


for phi, rem in ((0.5, "palette"), (0.5, "unique"), (0.25, "palette"),
                 ):
    c = Counter()
    rs = []
    for _ in range(20):
        v, r = verdict(*sim(phi, rem))
        c[re.sub(r'\([^)]*\)', '', v)] += 1
        rs.append(r)
    print(f'phi={phi} remainder={rem}: R(N2) median {np.median(rs):.3f}; verdicts {dict(c)}', flush=True)
