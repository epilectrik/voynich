"""
02_section_middle_matrix.py - Section × MIDDLE vocabulary comparison

Tests whether different sections (HERBAL_B, BIO, PHARMA, OTHER) use
systematically different MIDDLE vocabularies.

Different sections process different materials - if MIDDLEs encode
material-specific operations, they should cluster by section.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
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

# Count MIDDLEs by section
section_middles = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)
middle_totals = defaultdict(int)

for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        section = t.section
        mid = m.middle
        section_middles[section][mid] += 1
        section_totals[section] += 1
        middle_totals[mid] += 1

print(f"\nSection totals:")
for section, count in sorted(section_totals.items()):
    print(f"  {section}: {count}")

total_tokens = sum(section_totals.values())
print(f"  Total: {total_tokens}")

# Find MIDDLEs with enough occurrences
MIN_COUNT = 50
significant_middles = [m for m, c in middle_totals.items() if c >= MIN_COUNT]
print(f"\nMIDDLEs with >= {MIN_COUNT} occurrences: {len(significant_middles)}")

sections = sorted(section_totals.keys())

# Compute enrichment matrix
print("\n" + "="*100)
print("SECTION × MIDDLE ENRICHMENT MATRIX")
print("="*100)
print(f"\n{'MIDDLE':<12}", end="")
for s in sections:
    print(f"{s:>12}", end="")
print(f"{'TOTAL':>10}  INTERPRETATION")
print("-"*100)

results = []

for mid in sorted(significant_middles, key=lambda x: -middle_totals[x]):
    row = {'middle': mid, 'total': middle_totals[mid], 'enrichments': {}}
    print(f"{mid:<12}", end="")

    enrichments = []
    for section in sections:
        observed = section_middles[section][mid]
        expected = (middle_totals[mid] * section_totals[section]) / total_tokens
        ratio = observed / expected if expected > 0 else 0
        row['enrichments'][section] = {'observed': observed, 'expected': expected, 'ratio': ratio}
        enrichments.append((section, ratio))

        # Color coding
        if ratio > 1.3:
            print(f"{'*'+str(round(ratio,2)):>12}", end="")
        elif ratio < 0.7:
            print(f"{'_'+str(round(ratio,2)):>12}", end="")
        else:
            print(f"{ratio:>12.2f}", end="")

    print(f"{middle_totals[mid]:>10}", end="")

    # Interpretation: what section is this MIDDLE most associated with?
    max_section = max(enrichments, key=lambda x: x[1])
    min_section = min(enrichments, key=lambda x: x[1])
    if max_section[1] > 1.3:
        print(f"  --> {max_section[0]} ({max_section[1]:.2f}x)")
    elif min_section[1] < 0.7:
        print(f"  <-- NOT {min_section[0]} ({min_section[1]:.2f}x)")
    else:
        print("  (uniform)")

    results.append(row)

# Chi-square test for overall section-dependence of each MIDDLE
print("\n" + "="*100)
print("CHI-SQUARE TEST: SECTION-DEPENDENCE BY MIDDLE")
print("="*100)

chi_results = []
for mid in significant_middles:
    observed = [section_middles[s][mid] for s in sections]
    expected = [(middle_totals[mid] * section_totals[s]) / total_tokens for s in sections]

    if min(expected) >= 5:
        chi2, p = stats.chisquare(observed, expected)
        chi_results.append({'middle': mid, 'chi2': chi2, 'p': p, 'total': middle_totals[mid]})

chi_results.sort(key=lambda x: x['p'])

print(f"\n{'MIDDLE':<12} {'chi2':>10} {'p-value':>12} {'N':>8}  VERDICT")
print("-"*60)
for r in chi_results[:25]:
    verdict = "SECTION-SPECIFIC" if r['p'] < 0.01 else "uniform"
    print(f"{r['middle']:<12} {r['chi2']:>10.2f} {r['p']:>12.6f} {r['total']:>8}  {verdict}")

# Find the most section-specific MIDDLEs
print("\n" + "="*100)
print("MOST SECTION-SPECIFIC MIDDLEs")
print("="*100)

section_specific = [r for r in chi_results if r['p'] < 0.01]
print(f"\n{len(section_specific)}/{len(chi_results)} MIDDLEs are section-specific (p < 0.01)")

# For each section, find its characteristic MIDDLEs
print("\n--- HERBAL_B characteristic MIDDLEs (>1.3x enriched) ---")
herbal_middles = []
for mid in significant_middles:
    obs = section_middles['HERBAL_B'][mid]
    exp = (middle_totals[mid] * section_totals['HERBAL_B']) / total_tokens
    if exp > 0 and obs/exp > 1.3 and middle_totals[mid] >= 50:
        herbal_middles.append((mid, obs/exp, middle_totals[mid]))
herbal_middles.sort(key=lambda x: -x[1])
for m, ratio, n in herbal_middles[:10]:
    print(f"  {m:<12} {ratio:.2f}x (n={n})")

print("\n--- BIO characteristic MIDDLEs (>1.3x enriched) ---")
bio_middles = []
for mid in significant_middles:
    obs = section_middles['BIO'][mid]
    exp = (middle_totals[mid] * section_totals['BIO']) / total_tokens
    if exp > 0 and obs/exp > 1.3 and middle_totals[mid] >= 50:
        bio_middles.append((mid, obs/exp, middle_totals[mid]))
bio_middles.sort(key=lambda x: -x[1])
for m, ratio, n in bio_middles[:10]:
    print(f"  {m:<12} {ratio:.2f}x (n={n})")

print("\n--- OTHER characteristic MIDDLEs (>1.3x enriched) ---")
other_middles = []
for mid in significant_middles:
    obs = section_middles['OTHER'][mid]
    exp = (middle_totals[mid] * section_totals['OTHER']) / total_tokens
    if exp > 0 and obs/exp > 1.3 and middle_totals[mid] >= 50:
        other_middles.append((mid, obs/exp, middle_totals[mid]))
other_middles.sort(key=lambda x: -x[1])
for m, ratio, n in other_middles[:10]:
    print(f"  {m:<12} {ratio:.2f}x (n={n})")

print("\n--- PHARMA characteristic MIDDLEs (>1.3x enriched) ---")
pharma_middles = []
for mid in significant_middles:
    if 'PHARMA' not in section_totals:
        continue
    obs = section_middles['PHARMA'][mid]
    exp = (middle_totals[mid] * section_totals['PHARMA']) / total_tokens
    if exp > 0 and obs/exp > 1.3 and middle_totals[mid] >= 50:
        pharma_middles.append((mid, obs/exp, middle_totals[mid]))
pharma_middles.sort(key=lambda x: -x[1])
for m, ratio, n in pharma_middles[:10]:
    print(f"  {m:<12} {ratio:.2f}x (n={n})")

# Summary
print("\n" + "="*100)
print("SUMMARY")
print("="*100)
section_specific_pct = 100 * len(section_specific) / len(chi_results)
print(f"Section-specific MIDDLEs: {len(section_specific)}/{len(chi_results)} ({section_specific_pct:.1f}%)")
print(f"HERBAL_B characteristic: {len(herbal_middles)}")
print(f"BIO characteristic: {len(bio_middles)}")
print(f"OTHER characteristic: {len(other_middles)}")
print(f"PHARMA characteristic: {len(pharma_middles)}")

# Save results
output = {
    'parameters': {
        'min_count': MIN_COUNT,
        'total_middles': len(significant_middles)
    },
    'section_totals': dict(section_totals),
    'summary': {
        'section_specific_count': len(section_specific),
        'section_specific_pct': section_specific_pct
    },
    'section_characteristic': {
        'HERBAL_B': [{'middle': m, 'ratio': r, 'n': n} for m, r, n in herbal_middles],
        'BIO': [{'middle': m, 'ratio': r, 'n': n} for m, r, n in bio_middles],
        'OTHER': [{'middle': m, 'ratio': r, 'n': n} for m, r, n in other_middles],
        'PHARMA': [{'middle': m, 'ratio': r, 'n': n} for m, r, n in pharma_middles]
    },
    'chi_results': chi_results,
    'enrichment_matrix': results
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_MAPPING/results/section_middle_matrix.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to section_middle_matrix.json")
