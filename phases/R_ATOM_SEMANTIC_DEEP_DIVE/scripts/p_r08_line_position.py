"""P-R8: ar appears at late line positions, or at medial positions.

If r = "reifen" (ripen/mature):
- ar = readiness assessment, should come AFTER thermal processing
- ar mean line position > 0.65 (final quartile)
- or mean line position 0.45-0.60 (medial)
- ar - or position difference > 0.10
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology


tx = Transcript()
morph = Morphology()

# ============================================================
# Build per-line token data with positions
# ============================================================
print("Building per-line token data...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# P-R8a: ar vs or NORMALIZED LINE POSITION
# ============================================================
print(f"\n{'='*70}")
print("P-R8a: ar vs or NORMALIZED LINE POSITION")
print(f"{'='*70}")
print("Prediction: ar > 0.65, or 0.45-0.60, delta > 0.10\n")

mid_positions = defaultdict(list)

for line_key, words in line_tokens.items():
    n = len(words)
    if n < 4:
        continue

    for i, w in enumerate(words):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2 or mid[-1] != 'r':
            continue
        norm_pos = i / (n - 1) if n > 1 else 0.5
        mid_positions[mid].append(norm_pos)

print(f"  {'MIDDLE':<8s} {'n':>6s} {'mean':>8s} {'median':>8s} {'Q1':>8s} {'Q3':>8s}")
print(f"  {'-'*8} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for mid in sorted(mid_positions.keys()):
    positions = sorted(mid_positions[mid])
    n = len(positions)
    if n < 10:
        continue
    mean = sum(positions) / n
    median = positions[n // 2]
    q1 = positions[n // 4]
    q3 = positions[3 * n // 4]
    print(f"  {mid:<8s} {n:>6d} {mean:>8.4f} {median:>8.4f} {q1:>8.4f} {q3:>8.4f}")

# ============================================================
# P-R8b: ALL terminal atoms -- line position ranking
# ============================================================
print(f"\n{'='*70}")
print("P-R8b: ALL TERMINAL ATOMS -- LINE POSITION RANKING")
print(f"{'='*70}")
print("Where does each terminal atom appear within lines?\n")

term_positions = defaultdict(list)

for line_key, words in line_tokens.items():
    n = len(words)
    if n < 4:
        continue

    for i, w in enumerate(words):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        terminal = mid[-1]
        norm_pos = i / (n - 1) if n > 1 else 0.5
        term_positions[terminal].append(norm_pos)

print(f"  {'Term':<5s} {'n':>8s} {'mean':>8s} {'shape':>10s}")
print(f"  {'-'*5} {'-'*8} {'-'*8} {'-'*10}")

term_means = []
for term in sorted(term_positions.keys()):
    positions = term_positions[term]
    n = len(positions)
    if n < 50:
        continue
    mean = sum(positions) / n
    if mean > 0.55:
        shape = 'LATE'
    elif mean < 0.45:
        shape = 'EARLY'
    else:
        shape = 'MEDIAL'
    term_means.append((term, n, mean, shape))

term_means.sort(key=lambda x: x[2])
for term, n, mean, shape in term_means:
    marker = ' <-- r' if term == 'r' else ' <-- k' if term == 'k' else ' <-- l' if term == 'l' else ''
    print(f"  {term:<5s} {n:>8d} {mean:>8.4f} {shape:>10s}{marker}")

# ============================================================
# P-R8c: ar vs or -- QUARTILE DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("P-R8c: ar vs or QUARTILE DISTRIBUTION")
print(f"{'='*70}")

for mid in ['ar', 'or']:
    positions = mid_positions.get(mid, [])
    if not positions:
        print(f"\n  {mid}: no data")
        continue
    n = len(positions)
    q_counts = [0, 0, 0, 0]
    for p in positions:
        q = min(int(p * 4), 3)
        q_counts[q] += 1

    print(f"\n  {mid} (n={n}):")
    print(f"    Q0 (0-25%): {q_counts[0]:>4d} ({q_counts[0]/n*100:>5.1f}%)")
    print(f"    Q1 (25-50%): {q_counts[1]:>4d} ({q_counts[1]/n*100:>5.1f}%)")
    print(f"    Q2 (50-75%): {q_counts[2]:>4d} ({q_counts[2]/n*100:>5.1f}%)")
    print(f"    Q3 (75-100%): {q_counts[3]:>4d} ({q_counts[3]/n*100:>5.1f}%)")

# ============================================================
# P-R8d: ar vs or position BY MACRO-STATE
# ============================================================
print(f"\n{'='*70}")
print("P-R8d: ar vs or POSITION BY MACRO-STATE")
print(f"{'='*70}")

from scripts.voynich import BFolioDecoder
decoder = BFolioDecoder()

mid_state_positions = defaultdict(lambda: defaultdict(list))

for line_key, words in line_tokens.items():
    n = len(words)
    if n < 4:
        continue

    for i, w in enumerate(words):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2 or mid[-1] != 'r':
            continue
        norm_pos = i / (n - 1) if n > 1 else 0.5
        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if ms:
            mid_state_positions[mid][ms].append(norm_pos)

for mid in ['ar', 'or']:
    print(f"\n  {mid} position by state:")
    print(f"    {'State':<12s} {'n':>6s} {'mean':>8s}")
    print(f"    {'-'*12} {'-'*6} {'-'*8}")
    for state in ['FL_HAZ', 'FL_SAFE', 'AXM', 'AXm', 'FQ', 'CC']:
        positions = mid_state_positions[mid].get(state, [])
        if not positions:
            continue
        mean = sum(positions) / len(positions)
        print(f"    {state:<12s} {len(positions):>6d} {mean:>8.4f}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R8 SUMMARY")
print(f"{'='*70}")

ar_pos = mid_positions.get('ar', [])
or_pos = mid_positions.get('or', [])

if ar_pos and or_pos:
    ar_mean = sum(ar_pos) / len(ar_pos)
    or_mean = sum(or_pos) / len(or_pos)
    delta = ar_mean - or_mean
    print(f"\n  ar mean position: {ar_mean:.4f} (n={len(ar_pos)})")
    print(f"  or mean position: {or_mean:.4f} (n={len(or_pos)})")
    print(f"  Delta: {delta:+.4f}")

    if ar_mean > 0.65:
        print(f"  ar > 0.65: SUPPORTS")
    else:
        print(f"  ar < 0.65: DOES NOT SUPPORT (predicted > 0.65)")

    if delta > 0.10:
        print(f"  Delta > 0.10: SUPPORTS")
    elif delta > 0.05:
        print(f"  Delta > 0.05: PARTIAL SUPPORT")
    else:
        print(f"  Delta < 0.05: DOES NOT SUPPORT")
