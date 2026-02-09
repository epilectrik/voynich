"""
03_prefix_middle_interaction.py - PREFIX × MIDDLE combination analysis

PREFIX encodes handling mode, MIDDLE encodes operation type.
- Are certain PREFIX+MIDDLE combinations forbidden?
- Do prefixes select for specific MIDDLE families?
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()

# Get Currier B tokens
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# Count PREFIX × MIDDLE combinations
prefix_middle = defaultdict(lambda: defaultdict(int))
prefix_totals = defaultdict(int)
middle_totals = defaultdict(int)
total = 0

for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        prefix = m.prefix or '(none)'
        middle = m.middle
        prefix_middle[prefix][middle] += 1
        prefix_totals[prefix] += 1
        middle_totals[middle] += 1
        total += 1

print(f"Total tokens with MIDDLE: {total}")
print(f"Unique prefixes: {len(prefix_totals)}")
print(f"Unique MIDDLEs: {len(middle_totals)}")

# Filter to common prefixes and MIDDLEs
MIN_PREFIX = 100
MIN_MIDDLE = 50
common_prefixes = [p for p, c in prefix_totals.items() if c >= MIN_PREFIX]
common_middles = [m for m, c in middle_totals.items() if c >= MIN_MIDDLE]

print(f"\nPrefixes with >= {MIN_PREFIX} tokens: {len(common_prefixes)}")
print(f"MIDDLEs with >= {MIN_MIDDLE} tokens: {len(common_middles)}")

# Compute enrichment/depletion matrix
print("\n" + "="*100)
print("PREFIX × MIDDLE ENRICHMENT MATRIX")
print("="*100)

# Header
print(f"\n{'PREFIX':<10}", end="")
for mid in sorted(common_middles, key=lambda x: -middle_totals[x])[:15]:
    print(f"{mid:>8}", end="")
print()
print("-"*140)

forbidden_pairs = []
enriched_pairs = []

for prefix in sorted(common_prefixes, key=lambda x: -prefix_totals[x])[:20]:
    print(f"{prefix:<10}", end="")
    for mid in sorted(common_middles, key=lambda x: -middle_totals[x])[:15]:
        observed = prefix_middle[prefix][mid]
        expected = (prefix_totals[prefix] * middle_totals[mid]) / total
        ratio = observed / expected if expected > 0 else 0

        if expected >= 5:
            if ratio == 0:
                print(f"{'---':>8}", end="")
                forbidden_pairs.append((prefix, mid, prefix_totals[prefix], middle_totals[mid]))
            elif ratio > 2.0:
                print(f"{'*'+str(round(ratio,1)):>8}", end="")
                enriched_pairs.append((prefix, mid, ratio, observed))
            elif ratio < 0.3:
                print(f"{'_'+str(round(ratio,2)):>8}", end="")
            else:
                print(f"{ratio:>8.2f}", end="")
        else:
            print(f"{'~':>8}", end="")
    print(f"  (n={prefix_totals[prefix]})")

# Chi-square test for each prefix - does it select specific MIDDLEs?
print("\n" + "="*100)
print("PREFIX SELECTIVITY (Chi-square test)")
print("="*100)

selectivity_results = []

for prefix in common_prefixes:
    observed = np.array([prefix_middle[prefix][m] for m in common_middles])
    expected = np.array([(prefix_totals[prefix] * middle_totals[m]) / total for m in common_middles])

    # Normalize expected to match observed sum (avoids rounding error)
    expected = expected * (observed.sum() / expected.sum())

    if min(expected) >= 1:
        chi2, p = stats.chisquare(observed, expected)
        selectivity_results.append({
            'prefix': prefix,
            'chi2': float(chi2),
            'p': float(p),
            'n': prefix_totals[prefix]
        })

selectivity_results.sort(key=lambda x: x['chi2'], reverse=True)

print(f"\n{'PREFIX':<10} {'chi2':>12} {'p-value':>15} {'N':>8}  VERDICT")
print("-"*60)
for r in selectivity_results[:20]:
    verdict = "HIGHLY SELECTIVE" if r['chi2'] > 500 else "SELECTIVE" if r['chi2'] > 100 else "moderate"
    print(f"{r['prefix']:<10} {r['chi2']:>12.1f} {r['p']:>15.2e} {r['n']:>8}  {verdict}")

# Find which MIDDLEs each major prefix selects
print("\n" + "="*100)
print("PREFIX-SPECIFIC MIDDLE VOCABULARIES")
print("="*100)

major_prefixes = ['ch', 'sh', 'qo', 'ok', 'da', 'ol', 'ot', 'so', 'sa', 'ct']

for prefix in major_prefixes:
    if prefix not in prefix_totals:
        continue
    print(f"\n--- {prefix} (n={prefix_totals[prefix]}) ---")

    # Find enriched MIDDLEs
    enriched = []
    for mid in common_middles:
        observed = prefix_middle[prefix][mid]
        expected = (prefix_totals[prefix] * middle_totals[mid]) / total
        if expected >= 5:
            ratio = observed / expected
            if ratio > 1.5:
                enriched.append((mid, ratio, observed))

    enriched.sort(key=lambda x: -x[1])
    for mid, ratio, obs in enriched[:8]:
        print(f"  {mid:<10} {ratio:.2f}x (n={obs})")

# Forbidden combinations analysis
print("\n" + "="*100)
print("FORBIDDEN/RARE COMBINATIONS (expected >= 5, observed = 0)")
print("="*100)

if forbidden_pairs:
    print(f"\n{'PREFIX':<10} {'MIDDLE':<10} {'PREFIX_N':>10} {'MIDDLE_N':>10} {'Expected':>10}")
    print("-"*60)
    for prefix, mid, pn, mn in forbidden_pairs[:20]:
        exp = (pn * mn) / total
        print(f"{prefix:<10} {mid:<10} {pn:>10} {mn:>10} {exp:>10.1f}")
else:
    print("\nNo forbidden combinations found!")

# MIDDLE family affinity by prefix class
print("\n" + "="*100)
print("PREFIX CLASS × MIDDLE FAMILY AFFINITY")
print("="*100)

# Define prefix classes
prefix_classes = {
    'ch/sh': ['ch', 'sh'],
    'qo/ok': ['qo', 'ok'],
    'da/sa': ['da', 'sa'],
    'ot/ol': ['ot', 'ol'],
    'ct': ['ct']
}

middle_families = {
    'k-family': ['k', 'ke', 'ck', 'ek', 'kch'],
    'e-family': ['e', 'ed', 'eed', 'eo', 'eey'],
    'h-family': ['ch', 'sh', 'd'],
    'infra': ['iin', 'aiin', 'in', 'ain']
}

print(f"\n{'PREFIX_CLASS':<12}", end="")
for fam in middle_families:
    print(f"{fam:>12}", end="")
print()
print("-"*70)

for pc_name, prefixes in prefix_classes.items():
    print(f"{pc_name:<12}", end="")
    pc_total = sum(prefix_totals.get(p, 0) for p in prefixes)

    for fam_name, middles in middle_families.items():
        fam_count = 0
        fam_expected = 0
        for p in prefixes:
            for m in middles:
                fam_count += prefix_middle[p][m]
                fam_expected += (prefix_totals.get(p, 0) * middle_totals.get(m, 0)) / total

        ratio = fam_count / fam_expected if fam_expected > 0 else 0
        if ratio > 1.3:
            print(f"{'*'+str(round(ratio,2)):>12}", end="")
        elif ratio < 0.7:
            print(f"{'_'+str(round(ratio,2)):>12}", end="")
        else:
            print(f"{ratio:>12.2f}", end="")
    print()

# Summary
print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print(f"Most selective prefix: {selectivity_results[0]['prefix']} (chi2={selectivity_results[0]['chi2']:.0f})")
print(f"Forbidden combinations: {len(forbidden_pairs)}")
print(f"Highly enriched pairs (>2x): {len(enriched_pairs)}")

# Save results
output = {
    'parameters': {
        'min_prefix': MIN_PREFIX,
        'min_middle': MIN_MIDDLE,
        'total_tokens': total
    },
    'selectivity': selectivity_results,
    'forbidden_pairs': [{'prefix': p, 'middle': m, 'prefix_n': pn, 'middle_n': mn}
                        for p, m, pn, mn in forbidden_pairs],
    'enriched_pairs': [{'prefix': p, 'middle': m, 'ratio': r, 'observed': o}
                       for p, m, r, o in enriched_pairs]
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_DEEPENING/results/prefix_middle_interaction.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to prefix_middle_interaction.json")
