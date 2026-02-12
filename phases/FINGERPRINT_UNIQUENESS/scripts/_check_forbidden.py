#!/usr/bin/env python3
"""Check depletion ratios for known forbidden pairs."""
import sys
import json
import numpy as np
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

# Load class map
PROJECT_ROOT = __import__('pathlib').Path(__file__).parent.parent.parent.parent
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
t2c = {t: int(c) for t, c in ctm['token_to_class'].items()}
classes = sorted(set(t2c.values()))
n = len(classes)
c2i = {c: i for i, c in enumerate(classes)}
c2r = {int(k): v for k, v in ctm['class_to_role'].items()}
c2r[17] = 'CORE_CONTROL'

# Build transition matrix
tx = Transcript()
lines = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = t2c.get(w)
    if cls is not None:
        lines[(token.folio, token.line)].append(cls)

counts = np.zeros((n, n), dtype=int)
for seq in lines.values():
    for i in range(len(seq) - 1):
        a, b = c2i.get(seq[i]), c2i.get(seq[i + 1])
        if a is not None and b is not None:
            counts[a][b] += 1

row_totals = counts.sum(axis=1).astype(float)
col_totals = counts.sum(axis=0).astype(float)
grand = counts.sum()
expected = np.outer(row_totals, col_totals) / grand

# Known forbidden pairs
KNOWN_FORBIDDEN = [
    (12, 23), (12, 9), (17, 23), (17, 9), (10, 23), (10, 9), (11, 23), (11, 9),
    (10, 12), (10, 17), (11, 12), (11, 17),
    (32, 12), (32, 17), (31, 12), (31, 17),
    (23, 9)
]
known_set = set(KNOWN_FORBIDDEN)

print(f"Total transitions: {int(grand)}")
print(f"\nKnown forbidden pairs depletion (count/expected):")
for (s, t) in KNOWN_FORBIDDEN:
    si, ti = c2i[s], c2i[t]
    obs = counts[si][ti]
    exp = expected[si][ti]
    ratio = obs / exp if exp > 0 else float('inf')
    sr = c2r.get(s, '?')[:2]
    tr = c2r.get(t, '?')[:2]
    print(f"  ({s:2d},{t:2d}) {sr}->{tr}  count={obs:4d}  expected={exp:6.1f}  ratio={ratio:.3f}")

# Overall depletion distribution
dep_ratios = []
for i in range(n):
    for j in range(n):
        if expected[i][j] >= 5.0:
            dep_ratios.append((counts[i][j] / expected[i][j], classes[i], classes[j]))
dep_ratios.sort()

print(f"\nTotal pairs with expected >= 5: {len(dep_ratios)}")
print(f"\n30 most depleted pairs:")
for ratio, s, t in dep_ratios[:30]:
    is_known = '*' if (s, t) in known_set else ' '
    sr = c2r.get(s, '?')[:2]
    tr = c2r.get(t, '?')[:2]
    print(f"  {is_known} ({s:2d},{t:2d}) {sr}->{tr}  ratio={ratio:.3f}")

# One-way kernel check: e->h specifically
# Need to find which classes are k, h, e (kernel operators)
# From C521: class 12=k, class 13=h, class 7=e (typical)
print(f"\n--- Kernel pair check ---")
for (a_cls, b_cls, label) in [(7, 13, 'e->h'), (13, 7, 'h->e'), (7, 12, 'e->k'), (12, 7, 'k->e'), (13, 12, 'h->k'), (12, 13, 'k->h')]:
    if a_cls in c2i and b_cls in c2i:
        ai, bi = c2i[a_cls], c2i[b_cls]
        obs = counts[ai][bi]
        exp = expected[ai][bi]
        ratio = obs / exp if exp > 0 else float('inf')
        print(f"  {label}: count={obs:4d}  expected={exp:6.1f}  ratio={ratio:.3f}")
