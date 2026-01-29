"""
T2: LINK Position Distribution Within Lines

C365 claims LINK is spatially uniform (no positional clustering).
But C802/C803 show HT clusters at boundaries and near LINK.

Test whether LINK has positional preferences within lines.
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript
from scipy import stats
import numpy as np

def is_link(word):
    """LINK = token contains 'ol' substring (C609)"""
    return 'ol' in word.replace('*', '')

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

# Group by folio and line
lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

print(f"Total B tokens: {len(b_tokens)}")
print(f"Total lines: {len(lines)}")

# Analyze LINK positions
link_positions = []  # normalized 0-1
link_abs_positions = []
non_link_positions = []
non_link_abs_positions = []

# First/middle/last analysis
first_link = 0
first_total = 0
middle_link = 0
middle_total = 0
last_link = 0
last_total = 0

for key, tokens in lines.items():
    n = len(tokens)
    if n < 2:
        continue

    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        pos_norm = i / (n - 1) if n > 1 else 0.5
        is_link_token = is_link(word)

        if is_link_token:
            link_positions.append(pos_norm)
            link_abs_positions.append(i + 1)
        else:
            non_link_positions.append(pos_norm)
            non_link_abs_positions.append(i + 1)

        # First/middle/last
        if i == 0:
            first_total += 1
            if is_link_token:
                first_link += 1
        elif i == n - 1:
            last_total += 1
            if is_link_token:
                last_link += 1
        else:
            middle_total += 1
            if is_link_token:
                middle_link += 1

print(f"\n{'='*60}")
print(f"LINK POSITION ANALYSIS")
print(f"{'='*60}")
print(f"LINK tokens: {len(link_positions)}")
print(f"Non-LINK tokens: {len(non_link_positions)}")

# First/middle/last rates
print(f"\n--- FIRST/MIDDLE/LAST TOKEN RATES ---")
first_rate = 100 * first_link / first_total if first_total > 0 else 0
middle_rate = 100 * middle_link / middle_total if middle_total > 0 else 0
last_rate = 100 * last_link / last_total if last_total > 0 else 0
overall_rate = 100 * len(link_positions) / (len(link_positions) + len(non_link_positions))

print(f"First token LINK rate: {first_rate:.1f}% ({first_link}/{first_total})")
print(f"Middle token LINK rate: {middle_rate:.1f}% ({middle_link}/{middle_total})")
print(f"Last token LINK rate: {last_rate:.1f}% ({last_link}/{last_total})")
print(f"Overall LINK rate: {overall_rate:.1f}%")

# Chi-square test for first vs middle
if middle_total > 0:
    chi2_first, p_first = stats.chi2_contingency([
        [first_link, first_total - first_link],
        [middle_link, middle_total - middle_link]
    ])[:2]
    print(f"\nFirst vs Middle: chi2={chi2_first:.1f}, p={p_first:.4f}")

# Chi-square test for last vs middle
if middle_total > 0:
    chi2_last, p_last = stats.chi2_contingency([
        [last_link, last_total - last_link],
        [middle_link, middle_total - middle_link]
    ])[:2]
    print(f"Last vs Middle: chi2={chi2_last:.1f}, p={p_last:.4f}")

# Normalized position distribution
print(f"\n--- NORMALIZED POSITION DISTRIBUTION ---")
print(f"LINK mean position: {np.mean(link_positions):.3f}")
print(f"Non-LINK mean position: {np.mean(non_link_positions):.3f}")

# Mann-Whitney U test
u_stat, p_mw = stats.mannwhitneyu(link_positions, non_link_positions, alternative='two-sided')
print(f"Mann-Whitney U test: p={p_mw:.4f}")

# Bin by quintiles
print(f"\n--- POSITION QUINTILES ---")
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
link_hist, _ = np.histogram(link_positions, bins=bins)
non_link_hist, _ = np.histogram(non_link_positions, bins=bins)

print(f"{'Quintile':<12} {'LINK %':>8} {'Non-LINK %':>10} {'Ratio':>8}")
print(f"{'-'*12} {'-'*8} {'-'*10} {'-'*8}")
for i, (l, nl) in enumerate(zip(link_hist, non_link_hist)):
    l_pct = 100 * l / len(link_positions)
    nl_pct = 100 * nl / len(non_link_positions)
    ratio = l_pct / nl_pct if nl_pct > 0 else 0
    print(f"{bins[i]:.1f}-{bins[i+1]:.1f}      {l_pct:>7.1f}% {nl_pct:>9.1f}% {ratio:>7.2f}x")

# Chi-square test for distribution shape
chi2_shape, p_shape = stats.chisquare(
    link_hist,
    non_link_hist * len(link_positions) / len(non_link_positions)
)
print(f"\nChi-square for shape: chi2={chi2_shape:.1f}, p={p_shape:.4f}")

# Compare to HT patterns (C803 found HT enriched at boundaries)
print(f"\n{'='*60}")
print(f"COMPARISON TO C803 (HT BOUNDARY ENRICHMENT)")
print(f"{'='*60}")
print(f"C803 found: First=45.8% HT, Last=42.9% HT, Middle=25.7% HT")
print(f"\nLINK:       First={first_rate:.1f}%, Last={last_rate:.1f}%, Middle={middle_rate:.1f}%")

if first_rate > middle_rate * 1.2 and last_rate > middle_rate * 1.2:
    print(f"\n=> LINK shows SAME boundary enrichment pattern as HT")
elif first_rate < middle_rate * 0.8 and last_rate < middle_rate * 0.8:
    print(f"\n=> LINK shows OPPOSITE pattern (boundary DEPLETION)")
else:
    print(f"\n=> LINK shows NO clear boundary pattern")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
if p_mw < 0.05:
    print(f"LINK has SIGNIFICANT positional bias (p={p_mw:.4f})")
else:
    print(f"LINK has NO significant positional bias (p={p_mw:.4f}) - CONFIRMS C365")

if p_first < 0.01 or p_last < 0.01:
    print(f"LINK has SIGNIFICANT boundary effects")
else:
    print(f"LINK has NO significant boundary effects")
