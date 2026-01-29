"""
T1: What fraction of B vocabulary is AZC-mediated?

For each B folio, calculate:
- Total unique MIDDLEs
- MIDDLEs that also appear in AZC (AZC-mediated)
- MIDDLEs that are B-only (B-native)
- Fraction AZC-mediated

This establishes the baseline for understanding the constraint relationship.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("T1: B FOLIO AZC-MEDIATED VOCABULARY FRACTION")
print("="*70)

# Collect AZC vocabulary (all MIDDLEs across all AZC folios)
azc_middles = set()
azc_middles_by_folio = defaultdict(set)

for token in tx.azc():
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)
        azc_middles_by_folio[token.folio].add(m.middle)

print(f"\nAZC total unique MIDDLEs: {len(azc_middles)}")
print(f"AZC folios: {len(azc_middles_by_folio)}")

# Collect B vocabulary per folio
b_middles_by_folio = defaultdict(set)

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle:
        b_middles_by_folio[token.folio].add(m.middle)

print(f"\nB folios: {len(b_middles_by_folio)}")

# Calculate AZC-mediated fraction per B folio
results = []

print("\n" + "="*70)
print("PER-FOLIO BREAKDOWN")
print("="*70)
print(f"\n{'Folio':<10} {'Total':<8} {'AZC-Med':<10} {'B-Native':<10} {'% AZC-Med':<10}")
print("-"*50)

for folio in sorted(b_middles_by_folio.keys()):
    b_vocab = b_middles_by_folio[folio]
    azc_mediated = b_vocab & azc_middles
    b_native = b_vocab - azc_middles

    pct_azc = 100 * len(azc_mediated) / len(b_vocab) if b_vocab else 0

    results.append({
        'folio': folio,
        'total_middles': len(b_vocab),
        'azc_mediated': len(azc_mediated),
        'b_native': len(b_native),
        'pct_azc_mediated': round(pct_azc, 1)
    })

    print(f"{folio:<10} {len(b_vocab):<8} {len(azc_mediated):<10} {len(b_native):<10} {pct_azc:.1f}%")

# Summary statistics
pcts = [r['pct_azc_mediated'] for r in results]
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)
print(f"\nMean AZC-mediated %: {np.mean(pcts):.1f}%")
print(f"Std dev: {np.std(pcts):.1f}%")
print(f"Min: {np.min(pcts):.1f}%")
print(f"Max: {np.max(pcts):.1f}%")
print(f"Median: {np.median(pcts):.1f}%")

# Distribution
bins = [0, 20, 40, 60, 80, 100]
hist, _ = np.histogram(pcts, bins=bins)
print(f"\nDistribution:")
for i, count in enumerate(hist):
    print(f"  {bins[i]}-{bins[i+1]}%: {count} folios")

# Check for correlation with vocabulary size
total_middles = [r['total_middles'] for r in results]
correlation = np.corrcoef(total_middles, pcts)[0, 1]
print(f"\nCorrelation (vocab size vs AZC-mediated %): r = {correlation:.3f}")

# Identify extreme folios
sorted_by_pct = sorted(results, key=lambda x: x['pct_azc_mediated'])
print("\n" + "="*70)
print("EXTREME FOLIOS")
print("="*70)
print("\nLowest AZC-mediated %:")
for r in sorted_by_pct[:5]:
    print(f"  {r['folio']}: {r['pct_azc_mediated']:.1f}% ({r['azc_mediated']}/{r['total_middles']})")

print("\nHighest AZC-mediated %:")
for r in sorted_by_pct[-5:]:
    print(f"  {r['folio']}: {r['pct_azc_mediated']:.1f}% ({r['azc_mediated']}/{r['total_middles']})")

# Key question: Is there variance to explain?
print("\n" + "="*70)
print("KEY FINDING")
print("="*70)
if np.std(pcts) < 5:
    print("\nAZC-mediated % is nearly UNIFORM across B folios.")
    print("This suggests AZC is a UNIVERSAL filter, not folio-specific constraint.")
    verdict = "UNIFORM_FILTER"
elif np.std(pcts) > 15:
    print("\nAZC-mediated % varies SUBSTANTIALLY across B folios.")
    print("This suggests AZC provides DIFFERENTIAL constraint by folio.")
    verdict = "DIFFERENTIAL_CONSTRAINT"
else:
    print("\nAZC-mediated % shows MODERATE variation across B folios.")
    verdict = "MODERATE_VARIATION"

# Save results
output = {
    'azc_total_middles': len(azc_middles),
    'b_folios': len(results),
    'per_folio': results,
    'summary': {
        'mean_pct': round(np.mean(pcts), 1),
        'std_pct': round(np.std(pcts), 1),
        'min_pct': round(np.min(pcts), 1),
        'max_pct': round(np.max(pcts), 1),
        'median_pct': round(np.median(pcts), 1),
        'vocab_size_correlation': round(correlation, 3)
    },
    'verdict': verdict
}

output_path = PROJECT_ROOT / 'phases' / 'AZC_B_CONSTRAINT_MECHANISM' / 'results' / 't1_b_azc_overlap.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
