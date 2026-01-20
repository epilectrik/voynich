#!/usr/bin/env python3
"""
Re-test position finding controlling for single-token entries.

The original finding: A-exclusive tokens are 98.8% openers.
But if 84% of entries are single-token, this is confounded.

Key question: Are A-exclusive tokens more likely to be in SINGLE-token entries?
"""

import json
from collections import Counter
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(RESULTS_DIR / 'middle_classes.json') as f:
    middle_classes = json.load(f)

with open(RESULTS_DIR / 'entry_data.json') as f:
    entries = json.load(f)

a_exclusive = set(middle_classes['a_exclusive_middles'])
a_shared = set(middle_classes['a_shared_middles'])

print("=" * 70)
print("POSITION RE-TEST: Controlling for entry size")
print("=" * 70)

# Classify entries by MIDDLE class AND token count
single_exclusive = 0
single_shared = 0
multi_exclusive = 0
multi_shared = 0

for e in entries:
    # Get the MIDDLE (all tokens have same MIDDLE in multi-token entries)
    middle = e['tokens'][0]['middle']
    n_tokens = e['n_tokens']

    is_exclusive = middle in a_exclusive

    if n_tokens == 1:
        if is_exclusive:
            single_exclusive += 1
        else:
            single_shared += 1
    else:
        if is_exclusive:
            multi_exclusive += 1
        else:
            multi_shared += 1

print("\nEntry distribution by class and size:")
print()
print(f"  Single-token entries:")
print(f"    A-exclusive: {single_exclusive}")
print(f"    A/B-shared:  {single_shared}")
print()
print(f"  Multi-token entries:")
print(f"    A-exclusive: {multi_exclusive}")
print(f"    A/B-shared:  {multi_shared}")

# Calculate rates
total_exclusive = single_exclusive + multi_exclusive
total_shared = single_shared + multi_shared

excl_single_rate = single_exclusive / total_exclusive if total_exclusive > 0 else 0
shared_single_rate = single_shared / total_shared if total_shared > 0 else 0

print()
print(f"  Single-token rate:")
print(f"    A-exclusive: {100*excl_single_rate:.1f}%")
print(f"    A/B-shared:  {100*shared_single_rate:.1f}%")

# Statistical test
from scipy import stats

table = [
    [single_exclusive, multi_exclusive],
    [single_shared, multi_shared]
]

chi2, p_value, dof, expected = stats.chi2_contingency(table)

print()
print(f"  Chi-square test for single-token rate difference:")
print(f"    chi2 = {chi2:.2f}, p = {p_value:.6f}")

# Now look at token COUNT distribution
print()
print("=" * 70)
print("TOKEN COUNT DISTRIBUTION BY CLASS")
print("=" * 70)

excl_counts = []
shared_counts = []

for e in entries:
    middle = e['tokens'][0]['middle']
    if middle in a_exclusive:
        excl_counts.append(e['n_tokens'])
    else:
        shared_counts.append(e['n_tokens'])

import numpy as np

print()
print(f"  A-exclusive entries:")
print(f"    Mean tokens: {np.mean(excl_counts):.2f}")
print(f"    Median: {np.median(excl_counts):.1f}")
print(f"    Max: {max(excl_counts)}")

print()
print(f"  A/B-shared entries:")
print(f"    Mean tokens: {np.mean(shared_counts):.2f}")
print(f"    Median: {np.median(shared_counts):.1f}")
print(f"    Max: {max(shared_counts)}")

# Mann-Whitney test
u_stat, p_val = stats.mannwhitneyu(excl_counts, shared_counts, alternative='two-sided')
print()
print(f"  Mann-Whitney U test: U={u_stat:.0f}, p={p_val:.6f}")

# CRITICAL FINDING
print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)

if excl_single_rate > shared_single_rate + 0.05:
    print("""
A-exclusive entries are MORE LIKELY to be single-token than shared entries.

This explains the 98.8% opener rate: A-exclusive MIDDLEs appear in shorter entries.
The "opener concentration" finding is CONFOUNDED by entry size.

However, this itself is a finding: A-exclusive vocabulary correlates with
single-token entries, while shared vocabulary appears in longer entries.
""")
elif abs(excl_single_rate - shared_single_rate) < 0.05:
    print("""
A-exclusive and shared entries have SIMILAR single-token rates.

The entry size is not significantly different between classes.
The original position finding needs re-interpretation.
""")
else:
    print("""
A-exclusive entries are LESS LIKELY to be single-token.

This contradicts the simple confound explanation.
The position finding may reflect real positional preference within multi-token entries.
""")
