"""
F-F9: Section Gradient -- f-initial MIDDLE rate vs category rates across sections.

Tests whether f-initial rate correlates with MARKING (H1/H2/H3 all predict this)
or diverges toward STAGING/OPERATION across sections.

f is MARKING-dominant (85.1%), so the question is whether its section gradient
tracks the MARKING category or shows independence.

Predictions:
  P1: rho(f, MARKING) >= +0.35
  P2: |rho(f, THERMAL)| <= 0.50
  P3: Report which category is the BEST positive tracker for f

Pass: P1 AND P2.

KEY DISCRIMINANT: If MARKING is the best tracker, supports H1 "flag".
                  If STAGING, supports H2 "format".
                  If OPERATION, supports H3 "fill".

Controls: p-initial vs MARKING, d-initial vs MARKING, k-initial vs THERMAL
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# -- Load data ----------------------------------------------------------------
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

# -- Gather tokens by section --------------------------------------------------
section_tokens = defaultdict(list)

for token in tx.currier_b():
    if token.section is None:
        continue
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    section_tokens[token.section].append(m)

print("=" * 72)
print("F-F9: Section Gradient -- f-initial rate vs category rates")
print("=" * 72)
print()

# -- Compute per-section rates -------------------------------------------------
section_data = {}

for sec, morphs in sorted(section_tokens.items()):
    n = len(morphs)
    if n < 20:
        continue

    # f-initial MIDDLE rate
    f_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'f')
    f_rate = f_initial / n

    # Control atoms
    p_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'p')
    d_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'd')
    k_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'k')

    p_rate = p_initial / n
    d_rate = d_initial / n
    k_rate = k_initial / n

    # Category rates
    cat_counts = defaultdict(int)
    cat_total = 0
    for m in morphs:
        cat = cc.classify(m.middle)
        if cat and cat != 'UNK':
            cat_counts[cat] += 1
            cat_total += 1

    cat_rates = {}
    for cat in CATEGORIES:
        cat_rates[cat] = cat_counts[cat] / cat_total if cat_total > 0 else 0.0

    section_data[sec] = {
        'f_rate': f_rate, 'p_rate': p_rate, 'd_rate': d_rate, 'k_rate': k_rate,
        'cat_rates': cat_rates, 'n': n, 'cat_total': cat_total,
        'f_count': f_initial,
    }

# -- Display section profiles --------------------------------------------------
print("Section profiles:")
print(f"  {'Section':<10} {'N':>6} {'f-init':>7} {'f-init%':>8} {'p-init%':>8} {'d-init%':>8} {'k-init%':>8}")
print(f"  {'-'*10} {'-'*6} {'-'*7} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for sec in sorted(section_data.keys()):
    d = section_data[sec]
    print(f"  {sec:<10} {d['n']:>6} {d['f_count']:>7} {d['f_rate']*100:>7.2f}% {d['p_rate']*100:>7.2f}% "
          f"{d['d_rate']*100:>7.2f}% {d['k_rate']*100:>7.2f}%")

print()
print("Category rates by section:")
header = f"  {'Section':<10}"
for cat in CATEGORIES:
    header += f" {cat[:5]:>7}"
print(header)
print(f"  {'-'*10}" + f" {'-'*7}" * len(CATEGORIES))

for sec in sorted(section_data.keys()):
    d = section_data[sec]
    row = f"  {sec:<10}"
    for cat in CATEGORIES:
        row += f" {d['cat_rates'][cat]*100:>6.1f}%"
    print(row)

# -- Spearman rank correlation -------------------------------------------------
def rank_array(arr):
    """Assign ranks to array values (1-based, average ties)."""
    indexed = sorted(enumerate(arr), key=lambda x: x[1])
    ranks = [0.0] * len(arr)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for idx in range(i, j + 1):
            ranks[indexed[idx][0]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(x, y):
    """Compute Spearman rank correlation."""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    rx = rank_array(x)
    ry = rank_array(y)
    n = len(rx)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx) ** 2 for i in range(n)) ** 0.5
    den_y = sum((ry[i] - mean_ry) ** 2 for i in range(n)) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


# -- Compute correlations -----------------------------------------------------
sections = sorted(section_data.keys())
f_rates = [section_data[s]['f_rate'] for s in sections]
p_rates = [section_data[s]['p_rate'] for s in sections]
d_rates = [section_data[s]['d_rate'] for s in sections]
k_rates = [section_data[s]['k_rate'] for s in sections]

print()
print("=" * 72)
print("Spearman correlations: atom-initial rate vs category rate")
print("=" * 72)
print()

# f-initial vs each category
print("f-initial vs categories:")
f_best_cat = None
f_best_rho = -999.0

for cat in CATEGORIES:
    cat_vals = [section_data[s]['cat_rates'][cat] for s in sections]
    rho = spearman_rho(f_rates, cat_vals)
    marker = ""
    if cat == 'MARKING':
        marker = " <-- H1 'flag' target"
    elif cat == 'STAGING':
        marker = " <-- H2 'format' target"
    elif cat == 'OPERATION':
        marker = " <-- H3 'fill' target"
    print(f"  rho(f, {cat:<12}) = {rho:+.3f}{marker}")
    if rho > f_best_rho:
        f_best_rho = rho
        f_best_cat = cat

print(f"\n  BEST positive tracker for f: {f_best_cat} (rho = {f_best_rho:+.3f})")

# Controls
print()
print("Controls:")
for atom_name, atom_rates, expected_cat in [
    ('p-initial', p_rates, 'MARKING'),
    ('d-initial', d_rates, 'MARKING'),
    ('k-initial', k_rates, 'THERMAL'),
]:
    for cat in CATEGORIES:
        cat_vals = [section_data[s]['cat_rates'][cat] for s in sections]
        rho = spearman_rho(atom_rates, cat_vals)
        if cat == expected_cat:
            print(f"  rho({atom_name}, {cat:<12}) = {rho:+.3f}  (expected positive)")

# -- Evaluate predictions -----------------------------------------------------
print()
print("=" * 72)
print("PREDICTION EVALUATION")
print("=" * 72)
print()

# P1: rho(f, MARKING) >= +0.35
marking_vals = [section_data[s]['cat_rates']['MARKING'] for s in sections]
rho_marking = spearman_rho(f_rates, marking_vals)

p1_pass = rho_marking >= 0.35
print(f"P1: rho(f, MARKING) = {rho_marking:+.3f}")
print(f"    Need >= +0.35: {'PASS' if p1_pass else 'FAIL'}")

# P2: |rho(f, THERMAL)| <= 0.50
thermal_vals = [section_data[s]['cat_rates']['THERMAL'] for s in sections]
rho_thermal = spearman_rho(f_rates, thermal_vals)
p2_pass = abs(rho_thermal) <= 0.50
print(f"P2: |rho(f, THERMAL)| = {abs(rho_thermal):.3f}, need <= 0.50: {'PASS' if p2_pass else 'FAIL'}")

# P3: Best tracker
print(f"P3: Best positive tracker = {f_best_cat} (rho = {f_best_rho:+.3f})")

overall = p1_pass and p2_pass
print()
print(f"OVERALL: {'PASS' if overall else 'FAIL'}")

# Hypothesis discrimination
print()
print("HYPOTHESIS DISCRIMINATION:")
if f_best_cat == 'MARKING':
    print("  -> MARKING is best tracker: supports H1 'flag' (Flagge/Fahne)")
elif f_best_cat == 'STAGING':
    print("  -> STAGING is best tracker: supports H2 'format' (Fassung)")
elif f_best_cat == 'OPERATION':
    print("  -> OPERATION is best tracker: supports H3 'fill' (fullen)")
else:
    print(f"  -> {f_best_cat} is best tracker: none of H1/H2/H3 directly supported")
    print(f"     (MARKING rho={rho_marking:+.3f}, STAGING rho="
          f"{spearman_rho(f_rates, [section_data[s]['cat_rates']['STAGING'] for s in sections]):+.3f}, "
          f"OPERATION rho="
          f"{spearman_rho(f_rates, [section_data[s]['cat_rates']['OPERATION'] for s in sections]):+.3f})")
