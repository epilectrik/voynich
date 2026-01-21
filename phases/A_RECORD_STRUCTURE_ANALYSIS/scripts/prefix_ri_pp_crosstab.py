#!/usr/bin/env python3
"""
Pre-check: PREFIX family x RI/PP crosstab

Question: Does PREFIX family already explain RI/PP distribution?
If so, DA segment stratification would be automatic (no new discovery).
"""

import json
from collections import Counter, defaultdict

# Load pre-classified token data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    middle_classes = json.load(f)

# Get sets
ri_middles = set(middle_classes['a_exclusive_middles'])

print("=" * 70)
print("PREFIX FAMILY x RI/PP CROSSTAB")
print("=" * 70)
print()

# Count by PREFIX family
prefix_ri_count = Counter()
prefix_pp_count = Counter()
prefix_ri_tokens = Counter()
prefix_pp_tokens = Counter()

# Track MIDDLEs per prefix for deeper analysis
prefix_to_ri_middles = defaultdict(set)
prefix_to_pp_middles = defaultdict(set)

for t in tokens:
    prefix = t['prefix']
    middle = t['middle']
    middle_class = t['middle_class']

    if middle_class == 'exclusive':
        prefix_ri_tokens[prefix] += 1
        prefix_to_ri_middles[prefix].add(middle)
    else:
        prefix_pp_tokens[prefix] += 1
        prefix_to_pp_middles[prefix].add(middle)

# Get unique MIDDLE counts per prefix
for prefix in set(prefix_ri_tokens.keys()) | set(prefix_pp_tokens.keys()):
    prefix_ri_count[prefix] = len(prefix_to_ri_middles[prefix])
    prefix_pp_count[prefix] = len(prefix_to_pp_middles[prefix])

# Calculate totals
all_prefixes = sorted(set(prefix_ri_tokens.keys()) | set(prefix_pp_tokens.keys()),
                      key=lambda p: prefix_ri_tokens[p] + prefix_pp_tokens[p],
                      reverse=True)

print("BY TOKEN COUNT (instances)")
print("-" * 70)
print(f"{'PREFIX':<8} {'RI Tokens':>10} {'PP Tokens':>10} {'Total':>10} {'RI %':>8}")
print("-" * 70)

total_ri = sum(prefix_ri_tokens.values())
total_pp = sum(prefix_pp_tokens.values())

for prefix in all_prefixes[:15]:  # Top 15
    ri = prefix_ri_tokens[prefix]
    pp = prefix_pp_tokens[prefix]
    total = ri + pp
    ri_pct = 100 * ri / total if total > 0 else 0
    print(f"{prefix:<8} {ri:>10} {pp:>10} {total:>10} {ri_pct:>7.1f}%")

print("-" * 70)
print(f"{'TOTAL':<8} {total_ri:>10} {total_pp:>10} {total_ri+total_pp:>10} {100*total_ri/(total_ri+total_pp):>7.1f}%")
print()

print("BY MIDDLE TYPE COUNT (vocabulary)")
print("-" * 70)
print(f"{'PREFIX':<8} {'RI Types':>10} {'PP Types':>10} {'Total':>10} {'RI %':>8}")
print("-" * 70)

total_ri_types = sum(prefix_ri_count.values())
total_pp_types = sum(prefix_pp_count.values())

for prefix in all_prefixes[:15]:
    ri = prefix_ri_count[prefix]
    pp = prefix_pp_count[prefix]
    total = ri + pp
    ri_pct = 100 * ri / total if total > 0 else 0
    print(f"{prefix:<8} {ri:>10} {pp:>10} {total:>10} {ri_pct:>7.1f}%")

print("-" * 70)
print(f"{'TOTAL':<8} {total_ri_types:>10} {total_pp_types:>10} {total_ri_types+total_pp_types:>10}")
print()

# Identify RI-dominant vs PP-dominant prefixes
print("=" * 70)
print("PREFIX CLASSIFICATION BY RI/PP DOMINANCE")
print("=" * 70)
print()

ri_dominant = []
pp_dominant = []
balanced = []

for prefix in all_prefixes:
    ri_tok = prefix_ri_tokens[prefix]
    pp_tok = prefix_pp_tokens[prefix]
    total = ri_tok + pp_tok
    if total < 10:  # Skip rare prefixes
        continue

    ri_pct = ri_tok / total if total > 0 else 0

    if ri_pct > 0.20:  # More than 20% RI = RI-enriched
        ri_dominant.append((prefix, ri_pct, total))
    elif ri_pct < 0.03:  # Less than 3% RI = PP-dominant
        pp_dominant.append((prefix, ri_pct, total))
    else:
        balanced.append((prefix, ri_pct, total))

print(f"RI-ENRICHED PREFIXES (>20% RI tokens):")
for prefix, ri_pct, total in sorted(ri_dominant, key=lambda x: -x[1]):
    print(f"  {prefix}: {100*ri_pct:.1f}% RI ({total} tokens)")
print()

print(f"PP-DOMINANT PREFIXES (<3% RI tokens):")
for prefix, ri_pct, total in sorted(pp_dominant, key=lambda x: x[1]):
    print(f"  {prefix}: {100*ri_pct:.1f}% RI ({total} tokens)")
print()

print(f"BALANCED PREFIXES (3-20% RI tokens):")
for prefix, ri_pct, total in sorted(balanced, key=lambda x: -x[1]):
    print(f"  {prefix}: {100*ri_pct:.1f}% RI ({total} tokens)")
print()

# Key question: Does PREFIX predict RI/PP?
print("=" * 70)
print("KEY QUESTION: DOES PREFIX PREDICT RI/PP?")
print("=" * 70)
print()

# Chi-square test
from scipy import stats
import numpy as np

# Build contingency table for top prefixes
top_prefixes = [p for p in all_prefixes if prefix_ri_tokens[p] + prefix_pp_tokens[p] >= 50]
observed = []
for prefix in top_prefixes:
    observed.append([prefix_ri_tokens[prefix], prefix_pp_tokens[prefix]])

observed = np.array(observed)
chi2, p_value, dof, expected = stats.chi2_contingency(observed)

print(f"Chi-square test (PREFIX x RI/PP):")
print(f"  chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.2e}")
print(f"  degrees of freedom = {dof}")
print()

# Cramér's V for effect size
n = observed.sum()
min_dim = min(observed.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"  Cramer's V = {cramers_v:.3f}")
if cramers_v > 0.3:
    print(f"  -> STRONG association (V > 0.3)")
elif cramers_v > 0.1:
    print(f"  -> MODERATE association (V > 0.1)")
else:
    print(f"  -> WEAK association (V < 0.1)")
print()

# What percentage of RI tokens are in RI-dominant prefixes?
ri_in_ri_dominant = sum(prefix_ri_tokens[p] for p, _, _ in ri_dominant)
print(f"RI tokens in RI-enriched prefixes: {ri_in_ri_dominant}/{total_ri} ({100*ri_in_ri_dominant/total_ri:.1f}%)")

pp_in_pp_dominant = sum(prefix_pp_tokens[p] for p, _, _ in pp_dominant)
print(f"PP tokens in PP-dominant prefixes: {pp_in_pp_dominant}/{total_pp} ({100*pp_in_pp_dominant/total_pp:.1f}%)")
print()

# Implication for DA segmentation
print("=" * 70)
print("IMPLICATION FOR DA SEGMENTATION ANALYSIS")
print("=" * 70)
print()

if cramers_v > 0.2:
    print("PREFIX strongly predicts RI/PP membership.")
    print("Since DA segments are PREFIX-coherent (C422), DA segments")
    print("will automatically show RI/PP stratification.")
    print()
    print("RECOMMENDATION: DA segmentation may just be another view")
    print("of existing PREFIX-based structure. Proceed with caution.")
else:
    print("PREFIX weakly predicts RI/PP membership.")
    print("DA segmentation analysis may reveal NEW structure")
    print("beyond what PREFIX alone explains.")
    print()
    print("RECOMMENDATION: Proceed with Phase 1 (segment-level composition).")

# Save results
results = {
    'token_counts': {
        'by_prefix': {p: {'ri': prefix_ri_tokens[p], 'pp': prefix_pp_tokens[p]}
                      for p in all_prefixes},
        'total_ri': total_ri,
        'total_pp': total_pp
    },
    'type_counts': {
        'by_prefix': {p: {'ri': prefix_ri_count[p], 'pp': prefix_pp_count[p]}
                      for p in all_prefixes},
    },
    'classification': {
        'ri_enriched': [(p, pct, n) for p, pct, n in ri_dominant],
        'pp_dominant': [(p, pct, n) for p, pct, n in pp_dominant],
        'balanced': [(p, pct, n) for p, pct, n in balanced]
    },
    'chi_square': {
        'chi2': chi2,
        'p_value': p_value,
        'dof': dof,
        'cramers_v': cramers_v
    },
    'ri_concentration': {
        'ri_in_ri_enriched_prefixes': ri_in_ri_dominant,
        'ri_in_ri_enriched_pct': ri_in_ri_dominant / total_ri
    }
}

with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/prefix_ri_pp_crosstab.json', 'w') as f:
    json.dump(results, f, indent=2)

print()
print("Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/prefix_ri_pp_crosstab.json")
