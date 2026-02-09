"""
03_regime_middle_interaction.py - REGIME × MIDDLE clustering

Tests whether precision vs tolerance regimes use different MIDDLEs.
- REGIME_4 = precision axis (C494)
- If MIDDLEs cluster by REGIME, they encode execution mode requirements.

REGIMEs are defined by kernel ratios:
- REGIME_1: k-dominant
- REGIME_2: balanced k/e
- REGIME_3: e-dominant
- REGIME_4: high precision (low variance)
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

# Build folio-level data (REGIME is folio-level)
folio_tokens = defaultdict(list)
for t in b_tokens:
    folio_tokens[t.folio].append(t)

print(f"Total folios: {len(folio_tokens)}")

# Compute REGIME for each folio based on kernel profile
def compute_regime(tokens):
    """
    Compute REGIME based on kernel proportions.
    REGIME_1: k > 0.4
    REGIME_2: 0.25 < k < 0.4, balanced
    REGIME_3: e > 0.55
    REGIME_4: low variance (precision)
    """
    kernels = {'k': 0, 't': 0, 'e': 0, 'h': 0}
    total = 0

    for t in tokens:
        m = morph.extract(t.word)
        if m and m.middle:
            for char in ['k', 't', 'e', 'h']:
                if char in m.middle:
                    kernels[char] += 1
                    total += 1
                    break

    if total < 10:
        return None

    props = {k: v/total for k, v in kernels.items()}

    # Compute variance of proportions
    prop_values = list(props.values())
    variance = np.var(prop_values)

    # Assign REGIME
    if props['k'] > 0.40:
        return 'REGIME_1'  # k-dominant (energy intensive)
    elif props['e'] > 0.55:
        return 'REGIME_3'  # e-dominant (stability focused)
    elif variance < 0.01:
        return 'REGIME_4'  # low variance (precision)
    else:
        return 'REGIME_2'  # balanced

folio_regimes = {}
for folio, tokens in folio_tokens.items():
    regime = compute_regime(tokens)
    if regime:
        folio_regimes[folio] = {'regime': regime, 'tokens': tokens}

# Count regimes
regime_counts = defaultdict(int)
for data in folio_regimes.values():
    regime_counts[data['regime']] += 1

print(f"\nREGIME distribution:")
for regime, count in sorted(regime_counts.items()):
    print(f"  {regime}: {count} folios")

# Compute MIDDLE distribution by REGIME
regime_middles = defaultdict(lambda: defaultdict(int))
regime_totals = defaultdict(int)
middle_totals = defaultdict(int)

for folio, data in folio_regimes.items():
    regime = data['regime']
    for t in data['tokens']:
        m = morph.extract(t.word)
        if m and m.middle:
            mid = m.middle
            regime_middles[regime][mid] += 1
            regime_totals[regime] += 1
            middle_totals[mid] += 1

print(f"\nTokens by REGIME:")
for regime, count in sorted(regime_totals.items()):
    print(f"  {regime}: {count}")

total_tokens = sum(regime_totals.values())

# Find significant MIDDLEs
MIN_COUNT = 50
significant_middles = [m for m, c in middle_totals.items() if c >= MIN_COUNT]
print(f"\nMIDDLEs with >= {MIN_COUNT} occurrences: {len(significant_middles)}")

regimes = sorted(regime_totals.keys())

# Compute enrichment matrix
print("\n" + "="*90)
print("REGIME × MIDDLE ENRICHMENT MATRIX")
print("="*90)
print(f"\n{'MIDDLE':<12}", end="")
for r in regimes:
    print(f"{r:>12}", end="")
print(f"{'TOTAL':>10}  INTERPRETATION")
print("-"*90)

results = []

for mid in sorted(significant_middles, key=lambda x: -middle_totals[x]):
    row = {'middle': mid, 'total': middle_totals[mid], 'enrichments': {}}
    print(f"{mid:<12}", end="")

    enrichments = []
    for regime in regimes:
        observed = regime_middles[regime][mid]
        expected = (middle_totals[mid] * regime_totals[regime]) / total_tokens
        ratio = observed / expected if expected > 0 else 0
        row['enrichments'][regime] = {'observed': observed, 'expected': expected, 'ratio': ratio}
        enrichments.append((regime, ratio))

        # Color coding
        if ratio > 1.3:
            print(f"{'*'+str(round(ratio,2)):>12}", end="")
        elif ratio < 0.7:
            print(f"{'_'+str(round(ratio,2)):>12}", end="")
        else:
            print(f"{ratio:>12.2f}", end="")

    print(f"{middle_totals[mid]:>10}", end="")

    # Interpretation
    max_regime = max(enrichments, key=lambda x: x[1])
    min_regime = min(enrichments, key=lambda x: x[1])
    if max_regime[1] > 1.3:
        print(f"  --> {max_regime[0]} ({max_regime[1]:.2f}x)")
    elif min_regime[1] < 0.7:
        print(f"  <-- NOT {min_regime[0]} ({min_regime[1]:.2f}x)")
    else:
        print("  (uniform)")

    results.append(row)

# Chi-square test for REGIME-dependence
print("\n" + "="*90)
print("CHI-SQUARE TEST: REGIME-DEPENDENCE BY MIDDLE")
print("="*90)

chi_results = []
for mid in significant_middles:
    observed = [regime_middles[r][mid] for r in regimes]
    expected = [(middle_totals[mid] * regime_totals[r]) / total_tokens for r in regimes]

    if min(expected) >= 5:
        chi2, p = stats.chisquare(observed, expected)
        chi_results.append({'middle': mid, 'chi2': chi2, 'p': p, 'total': middle_totals[mid]})

chi_results.sort(key=lambda x: x['p'])

print(f"\n{'MIDDLE':<12} {'chi2':>10} {'p-value':>12} {'N':>8}  VERDICT")
print("-"*60)
for r in chi_results[:25]:
    verdict = "REGIME-SPECIFIC" if r['p'] < 0.01 else "uniform"
    print(f"{r['middle']:<12} {r['chi2']:>10.2f} {r['p']:>12.6f} {r['total']:>8}  {verdict}")

# REGIME-characteristic MIDDLEs
print("\n" + "="*90)
print("REGIME-CHARACTERISTIC MIDDLEs")
print("="*90)

for regime in regimes:
    print(f"\n--- {regime} characteristic MIDDLEs (>1.3x enriched) ---")
    regime_specific = []
    for mid in significant_middles:
        obs = regime_middles[regime][mid]
        exp = (middle_totals[mid] * regime_totals[regime]) / total_tokens
        if exp > 0 and obs/exp > 1.3:
            regime_specific.append((mid, obs/exp, middle_totals[mid]))
    regime_specific.sort(key=lambda x: -x[1])
    for m, ratio, n in regime_specific[:8]:
        print(f"  {m:<12} {ratio:.2f}x (n={n})")

# Summary
regime_specific_count = len([r for r in chi_results if r['p'] < 0.01])
print("\n" + "="*90)
print("SUMMARY")
print("="*90)
print(f"REGIME-specific MIDDLEs: {regime_specific_count}/{len(chi_results)} ({100*regime_specific_count/len(chi_results):.1f}%)")

# Save results
output = {
    'parameters': {
        'min_count': MIN_COUNT,
        'total_folios': len(folio_regimes),
        'total_middles': len(significant_middles)
    },
    'regime_distribution': dict(regime_counts),
    'regime_tokens': dict(regime_totals),
    'summary': {
        'regime_specific_count': regime_specific_count,
        'regime_specific_pct': 100*regime_specific_count/len(chi_results) if chi_results else 0
    },
    'chi_results': chi_results,
    'enrichment_matrix': results
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_MAPPING/results/regime_middle_interaction.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to regime_middle_interaction.json")
