#!/usr/bin/env python3
"""PHASE_772 lock audit (lean-expert). No R/W/duplicate statistic of the real labels is computed.

1. Clock span of each contiguous label group (page, ring) -- structural.
2. Space types in multi-word labels ('.' definite vs ',' uncertain) -- structural.
3. Edit model: share of copies whose normalised form differs from the base, per lambda and norm, computed
   per form (w vs edits(w) only; no comparison between labels).
4. Inventory-model R floor at N1/N2 for large lambda, with base forms drawn from Currier A running text
   (not from the zodiac labels), sign sizes as in the design.
5. Monte Carlo spread of the 1st percentile of R with 200 simulations.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zod772 as Z  # noqa: E402

rng = np.random.default_rng(11)
labels = Z.load_labels()

# 1. clock spans
groups = defaultdict(list)
for r in labels:
    groups[(r['folio'], r['ring'])].append(r['clock'])
print('group clock spans (hours): n, min, max, largest gap between clock-sorted neighbours (circular)')
for k in sorted(groups):
    c = sorted(groups[k])
    gaps = [c[i + 1] - c[i] for i in range(len(c) - 1)] + [c[0] + 12 - c[-1]]
    print(f'  {k}: n={len(c)} min={c[0]:.2f} max={c[-1]:.2f} maxgap={max(gaps):.2f}')

# 2. space types in multi-word labels
sp = Counter()
cur = None
for raw in open(Z.ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f\w+)>', raw)
    if m and not re.match(r'^<f\w+\.', raw):
        cur = m.group(1) if m.group(1) in Z.SIGN else None
        continue
    if cur is None:
        continue
    m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
    if not m or m.group(1) != cur or not m.group(4).startswith('L'):
        continue
    body = m.group(5)
    if not re.match(r'<!(\d\d):(\d\d)>', body):
        continue
    cb = Z.clean(body)
    form = ''.join(re.split(r'[.,]', cb))
    if not form or not re.fullmatch(r'[a-z]+', form):
        continue
    if '.' in cb.strip('.,') or ',' in cb.strip('.,'):
        sp['definite(.)' if '.' in cb.strip('.,') else 'uncertain(,) only'] += 1
print('multi-word labels by space type:', dict(sp))

# 3. edit-model visibility, per form
forms = [r['form'] for r in labels]
print('share of copies differing from base after normalisation (per-form; 20 draws per form):')
for lam in (0.5, 1.0, 2.0, 3.0, 5.0):
    ch = {k: [] for k in Z.NORMS}
    for w in forms:
        for _ in range(20):
            e = Z.edits(w, rng, lam)
            for k, f in Z.NORMS.items():
                ch[k].append(f(e) != f(w))
    print(f'  lam={lam}: ' + ' '.join(f'{k} {np.mean(v):.3f}' for k, v in ch.items()))

# 4. N2 floor with Currier A base forms
sys.path.insert(0, str(Z.ROOT))
from scripts.voynich import Transcript  # noqa: E402
aw = Counter(t.word for t in Transcript().currier_a() if t.word and re.fullmatch(r'[a-z]+', t.word))
pool = [w for w in aw if 4 <= len(Z.GLYPH_RE.findall(Z.n1(w))) <= 8]
sizes = [28, 30, 30, 29, 28, 29, 30, 27, 30, 29]


def r_stat(fs, ss):
    by = defaultdict(set)
    for f, s in zip(fs, ss):
        by[f].add(s)
    return np.mean([len(by[f] - {s}) > 0 for f, s in zip(fs, ss)])


print(f'Currier A base pool: {len(pool)} types (glyph length 4-8)')
for lam in (1.0, 3.0, 5.0, 8.0, 12.0):
    out = {'N1': [], 'N2': []}
    for _ in range(300):
        base = list(rng.choice(pool, size=30, replace=False))
        fs, ss = [], []
        for si, n in enumerate(sizes):
            for k in range(n):
                fs.append(Z.edits(base[k % 30], rng, lam))
                ss.append(si)
        for k in out:
            out[k].append(r_stat([Z.NORMS[k](w) for w in fs], ss))
    print(f'  A-base inventory lam={lam}: ' + ' '.join(
        f'{k} q01 {np.quantile(v, 0.01):.3f} median {np.median(v):.3f}' for k, v in out.items()))

# 5. Monte Carlo spread of q01 from 200 simulations (A base, lam=3, N2)
big = []
for _ in range(2000):
    base = list(rng.choice(pool, size=30, replace=False))
    fs, ss = [], []
    for si, n in enumerate(sizes):
        for k in range(n):
            fs.append(Z.edits(base[k % 30], rng, 3.0))
            ss.append(si)
    big.append(r_stat([Z.n2(w) for w in fs], ss))
big = np.array(big)
q = [np.quantile(rng.choice(big, 200, replace=True), 0.01) for _ in range(500)]
print(f'q01 (lam=3, N2, A base) from 2000 sims {np.quantile(big, 0.01):.4f}; '
      f'from 200 sims: sd {np.std(q):.4f}, 5-95% {np.quantile(q, 0.05):.4f}-{np.quantile(q, 0.95):.4f}; '
      f'one label = {1/290:.4f}')
