"""
S-S9: Section Gradient — s-initial MIDDLE rate vs category rates across sections.

Tests whether s-initial rate correlates with STAGING (H1) or MONITORING (H2)
rate across sections, discriminating between the three s-atom hypotheses.

Predictions:
  P1: rho(s, STAGING) >= +0.35 OR rho(s, MONITORING) >= +0.35
  P2: |rho(s, THERMAL)| <= 0.50
  P3: Report which category is the BEST positive tracker for s

Pass: P1 AND P2.

KEY DISCRIMINANT: If STAGING is the best tracker, supports H1 "sequence".
                  If MONITORING, supports H2 "sift/inspect".
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# ── Load data ──────────────────────────────────────────────────────────────
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

# ── Gather tokens by section ───────────────────────────────────────────────
# Include both Currier B and AZC tokens for section coverage
section_tokens = defaultdict(list)

for token in tx.currier_b():
    if token.section is None:
        continue
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    section_tokens[token.section].append(m)

print("=" * 72)
print("S-S9: Section Gradient -- s-initial rate vs category rates")
print("=" * 72)
print()

# ── Compute per-section rates ──────────────────────────────────────────────
section_data = {}

for sec, morphs in sorted(section_tokens.items()):
    n = len(morphs)
    if n < 20:
        continue

    # s-initial MIDDLE rate
    s_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 's')
    s_rate = s_initial / n

    # Control atoms
    k_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'k')
    c_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'c')
    o_initial = sum(1 for m in morphs if m.middle and m.middle[0] == 'o')

    k_rate = k_initial / n
    c_rate = c_initial / n
    o_rate = o_initial / n

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
        's_rate': s_rate, 'k_rate': k_rate, 'c_rate': c_rate, 'o_rate': o_rate,
        'cat_rates': cat_rates, 'n': n, 'cat_total': cat_total
    }

# ── Display section profiles ───────────────────────────────────────────────
print("Section profiles:")
print(f"  {'Section':<10} {'N':>6} {'s-init%':>8} {'k-init%':>8} {'c-init%':>8} {'o-init%':>8}")
print(f"  {'-'*10} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for sec in sorted(section_data.keys()):
    d = section_data[sec]
    print(f"  {sec:<10} {d['n']:>6} {d['s_rate']*100:>7.2f}% {d['k_rate']*100:>7.2f}% "
          f"{d['c_rate']*100:>7.2f}% {d['o_rate']*100:>7.2f}%")

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

# ── Spearman rank correlation ──────────────────────────────────────────────
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


# ── Compute correlations ──────────────────────────────────────────────────
sections = sorted(section_data.keys())
s_rates = [section_data[s]['s_rate'] for s in sections]
k_rates = [section_data[s]['k_rate'] for s in sections]
c_rates = [section_data[s]['c_rate'] for s in sections]
o_rates = [section_data[s]['o_rate'] for s in sections]

print()
print("=" * 72)
print("Spearman correlations: atom-initial rate vs category rate")
print("=" * 72)
print()

# s-initial vs each category
print("s-initial vs categories:")
s_best_cat = None
s_best_rho = -999.0

for cat in CATEGORIES:
    cat_vals = [section_data[s]['cat_rates'][cat] for s in sections]
    rho = spearman_rho(s_rates, cat_vals)
    marker = ""
    if cat in ('STAGING', 'MONITORING'):
        marker = " <-- hypothesis target"
    print(f"  rho(s, {cat:<12}) = {rho:+.3f}{marker}")
    if rho > s_best_rho:
        s_best_rho = rho
        s_best_cat = cat

print(f"\n  BEST positive tracker for s: {s_best_cat} (rho = {s_best_rho:+.3f})")

# Control: k-initial vs THERMAL
print()
print("Controls:")
for atom_name, atom_rates, expected_cat in [
    ('k-initial', k_rates, 'THERMAL'),
    ('c-initial', c_rates, 'MONITORING'),
    ('o-initial', o_rates, 'STAGING'),
]:
    for cat in CATEGORIES:
        cat_vals = [section_data[s]['cat_rates'][cat] for s in sections]
        rho = spearman_rho(atom_rates, cat_vals)
        if cat == expected_cat:
            print(f"  rho({atom_name}, {cat:<12}) = {rho:+.3f}  (expected positive)")

# ── Evaluate predictions ──────────────────────────────────────────────────
print()
print("=" * 72)
print("PREDICTION EVALUATION")
print("=" * 72)
print()

# P1: rho(s, STAGING) >= +0.35 OR rho(s, MONITORING) >= +0.35
staging_vals = [section_data[s]['cat_rates']['STAGING'] for s in sections]
monitoring_vals = [section_data[s]['cat_rates']['MONITORING'] for s in sections]
rho_staging = spearman_rho(s_rates, staging_vals)
rho_monitoring = spearman_rho(s_rates, monitoring_vals)

p1_pass = rho_staging >= 0.35 or rho_monitoring >= 0.35
print(f"P1: rho(s, STAGING)={rho_staging:+.3f}, rho(s, MONITORING)={rho_monitoring:+.3f}")
print(f"    Need >= +0.35 for either: {'PASS' if p1_pass else 'FAIL'}")

# P2: |rho(s, THERMAL)| <= 0.50
thermal_vals = [section_data[s]['cat_rates']['THERMAL'] for s in sections]
rho_thermal = spearman_rho(s_rates, thermal_vals)
p2_pass = abs(rho_thermal) <= 0.50
print(f"P2: |rho(s, THERMAL)|={abs(rho_thermal):.3f}, need <= 0.50: {'PASS' if p2_pass else 'FAIL'}")

# P3: Best tracker
print(f"P3: Best positive tracker = {s_best_cat} (rho = {s_best_rho:+.3f})")

overall = p1_pass and p2_pass
print()
print(f"OVERALL: {'PASS' if overall else 'FAIL'}")

# Hypothesis discrimination
print()
print("HYPOTHESIS DISCRIMINATION:")
if s_best_cat == 'STAGING':
    print("  -> STAGING is best tracker: supports H1 'sequence' (sequenzieren)")
elif s_best_cat == 'MONITORING':
    print("  -> MONITORING is best tracker: supports H2 'sift/inspect' (sichten)")
elif s_best_cat == 'OPERATION':
    print("  -> OPERATION is best tracker: supports H3 'step' (Schritt)")
else:
    print(f"  -> {s_best_cat} is best tracker: none of H1/H2/H3 directly supported")
    print(f"     (STAGING rho={rho_staging:+.3f}, MONITORING rho={rho_monitoring:+.3f})")
