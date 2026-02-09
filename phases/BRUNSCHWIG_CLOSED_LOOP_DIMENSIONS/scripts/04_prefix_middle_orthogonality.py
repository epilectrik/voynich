#!/usr/bin/env python3
"""
Test 4: PREFIX-MIDDLE Orthogonality

Tests whether PREFIX (material identity) and MIDDLE (procedural core)
encode independent parameters.

Hypothesis: If orthogonal, the same MIDDLEs should appear across
multiple PREFIX contexts, and PREFIX classes should not determine
MIDDLE distribution.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 4: PREFIX-MIDDLE ORTHOGONALITY")
print("="*70)

# Extract PREFIX and MIDDLE for all B tokens
prefix_middle_pairs = []
prefix_counts = Counter()
middle_counts = Counter()
prefix_middles = defaultdict(Counter)  # prefix -> middle distribution

for token in tx.currier_b():
    if '*' in token.word:
        continue

    m = morph.extract(token.word)
    if m.middle:
        prefix = m.prefix if m.prefix else 'NONE'
        middle = m.middle

        prefix_middle_pairs.append((prefix, middle))
        prefix_counts[prefix] += 1
        middle_counts[middle] += 1
        prefix_middles[prefix][middle] += 1

print(f"\nTotal PREFIX-MIDDLE pairs: {len(prefix_middle_pairs)}")
print(f"Unique PREFIXes: {len(prefix_counts)}")
print(f"Unique MIDDLEs: {len(middle_counts)}")

# Filter to significant PREFIXes (>100 occurrences)
MIN_PREFIX_COUNT = 100
significant_prefixes = [p for p, c in prefix_counts.items() if c >= MIN_PREFIX_COUNT]
print(f"\nSignificant PREFIXes (>{MIN_PREFIX_COUNT}): {len(significant_prefixes)}")

for p in sorted(significant_prefixes, key=lambda x: -prefix_counts[x])[:10]:
    print(f"  {p}: {prefix_counts[p]} tokens")

# Test 1: How many MIDDLEs appear in multiple PREFIX contexts?
print(f"\n{'='*70}")
print("MIDDLE CROSS-PREFIX DISTRIBUTION")
print("="*70)

middle_prefix_count = defaultdict(set)  # middle -> set of prefixes it appears with
for prefix, middle_dist in prefix_middles.items():
    if prefix not in significant_prefixes:
        continue
    for middle in middle_dist:
        middle_prefix_count[middle].add(prefix)

# Count MIDDLEs by prefix coverage
single_prefix = sum(1 for m, ps in middle_prefix_count.items() if len(ps) == 1)
multi_prefix = sum(1 for m, ps in middle_prefix_count.items() if len(ps) > 1)
most_prefixes = max(len(ps) for ps in middle_prefix_count.values()) if middle_prefix_count else 0

print(f"\nMIDDLEs appearing in:")
print(f"  Single PREFIX only: {single_prefix}")
print(f"  Multiple PREFIXes: {multi_prefix}")
print(f"  Max PREFIX coverage: {most_prefixes}")

cross_prefix_ratio = multi_prefix / (single_prefix + multi_prefix) if (single_prefix + multi_prefix) > 0 else 0
print(f"\nCross-PREFIX ratio: {cross_prefix_ratio:.1%}")

# Top MIDDLEs appearing in most PREFIX contexts
print(f"\nTop MIDDLEs by PREFIX coverage:")
top_middles = sorted(middle_prefix_count.items(), key=lambda x: -len(x[1]))[:10]
for middle, prefixes in top_middles:
    print(f"  {middle}: {len(prefixes)} prefixes ({', '.join(sorted(prefixes)[:5])}...)")

# Test 2: Chi-square test for independence
print(f"\n{'='*70}")
print("CHI-SQUARE TEST FOR INDEPENDENCE")
print("="*70)

# Build contingency table for top prefixes and top middles
TOP_N = 10
top_prefixes = [p for p, _ in prefix_counts.most_common(TOP_N) if p in significant_prefixes]
top_middles_list = [m for m, _ in middle_counts.most_common(TOP_N)]

contingency = []
for prefix in top_prefixes:
    row = [prefix_middles[prefix].get(m, 0) for m in top_middles_list]
    contingency.append(row)

contingency = np.array(contingency)
print(f"\nContingency table: {len(top_prefixes)} prefixes x {len(top_middles_list)} middles")

if contingency.sum() > 0 and contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
    chi2, p_chi, dof, expected = scipy_stats.chi2_contingency(contingency)
    cramers_v = np.sqrt(chi2 / (contingency.sum() * (min(contingency.shape) - 1)))

    print(f"Chi-square: {chi2:.1f}")
    print(f"p-value: {p_chi:.2e}")
    print(f"Cramer's V: {cramers_v:.3f}")

    # Interpretation of Cramer's V
    if cramers_v < 0.1:
        association = "NEGLIGIBLE"
    elif cramers_v < 0.3:
        association = "WEAK"
    elif cramers_v < 0.5:
        association = "MODERATE"
    else:
        association = "STRONG"

    print(f"Association: {association}")
else:
    chi2, p_chi, cramers_v = None, None, None
    association = "INSUFFICIENT DATA"

# Test 3: Entropy of MIDDLE distribution per PREFIX
print(f"\n{'='*70}")
print("MIDDLE ENTROPY BY PREFIX")
print("="*70)

def entropy(dist):
    total = sum(dist.values())
    if total == 0:
        return 0
    probs = [c/total for c in dist.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

prefix_entropies = {}
for prefix in significant_prefixes:
    h = entropy(prefix_middles[prefix])
    prefix_entropies[prefix] = h

print(f"\nMIDDLE entropy by PREFIX (higher = more diverse):")
for prefix in sorted(prefix_entropies.keys(), key=lambda x: -prefix_entropies[x])[:10]:
    print(f"  {prefix}: H={prefix_entropies[prefix]:.2f} bits ({len(prefix_middles[prefix])} unique MIDDLEs)")

mean_entropy = np.mean(list(prefix_entropies.values()))
print(f"\nMean MIDDLE entropy across PREFIXes: {mean_entropy:.2f} bits")

# Verdict
print(f"\n{'='*70}")
print("VERDICT")
print("="*70)

if cross_prefix_ratio > 0.5 and (cramers_v is None or cramers_v < 0.3):
    verdict = "SUPPORT"
    print(f"\n** PREFIX and MIDDLE are relatively ORTHOGONAL **")
    print(f"  - {cross_prefix_ratio:.0%} of MIDDLEs appear in multiple PREFIX contexts")
    print(f"  - Cramer's V = {cramers_v:.3f} indicates {association} association")
elif cross_prefix_ratio > 0.3:
    verdict = "PARTIAL"
    print(f"\nPartial orthogonality")
else:
    verdict = "NOT SUPPORTED"
    print(f"\nPREFIX and MIDDLE are NOT orthogonal")

# Save results
output = {
    'test': 'PREFIX-MIDDLE Orthogonality',
    'total_pairs': len(prefix_middle_pairs),
    'unique_prefixes': len(prefix_counts),
    'unique_middles': len(middle_counts),
    'significant_prefixes': len(significant_prefixes),
    'cross_prefix_analysis': {
        'single_prefix_middles': single_prefix,
        'multi_prefix_middles': multi_prefix,
        'cross_prefix_ratio': cross_prefix_ratio,
        'max_prefix_coverage': most_prefixes
    },
    'chi_square': {
        'chi2': float(chi2) if chi2 else None,
        'p_value': float(p_chi) if p_chi else None,
        'cramers_v': float(cramers_v) if cramers_v else None,
        'association': association
    },
    'entropy': {
        'mean_entropy': float(mean_entropy),
        'prefix_entropies': {k: float(v) for k, v in prefix_entropies.items()}
    },
    'verdict': verdict
}

output_path = results_dir / 'prefix_middle_orthogonality.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
