#!/usr/bin/env python3
"""
BRUNSCHWIG STRUCTURAL MATCH TEST

Question: Do Voynich folios with Brunschwig-like line counts
have REGIMEs consistent with Brunschwig material categories?

Brunschwig material→degree mapping:
- Cold/moist flowers: First degree (gentle) → REGIME_2?
- Hot/dry herbs: Third degree (strong) → REGIME_3?
- Complex roots: Second/Third degree → REGIME_1/4?

Test: Do folios with 10-20 lines cluster by REGIME?
"""
import csv
import json
from collections import defaultdict

# Load REGIME assignments
with open('results/unified_folio_profiles.json') as f:
    profiles = json.load(f)

# Get folio→REGIME mapping
folio_regime = {}
for folio, profile in profiles['profiles'].items():
    if profile.get('system') == 'B':
        folio_regime[folio] = profile.get('classification', 'UNKNOWN')

# Count lines per B folio
folio_lines = defaultdict(set)
with open('data/transcriptions/interlinear_full_words.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['language'] == 'B':
            folio_lines[row['folio']].add(row['line_number'])

# Group folios by line count range
line_groups = {
    'small (5-9)': [],
    'medium (10-20)': [],  # Brunschwig-like
    'large (21-40)': [],
    'very_large (41+)': []
}

for folio in folio_regime:
    n_lines = len(folio_lines.get(folio, []))
    regime = folio_regime[folio]

    if n_lines <= 9:
        line_groups['small (5-9)'].append((folio, regime))
    elif n_lines <= 20:
        line_groups['medium (10-20)'].append((folio, regime))
    elif n_lines <= 40:
        line_groups['large (21-40)'].append((folio, regime))
    else:
        line_groups['very_large (41+)'].append((folio, regime))

print("=" * 70)
print("BRUNSCHWIG STRUCTURAL MATCH TEST")
print("=" * 70)
print()
print("Question: Do folios with Brunschwig-like structure (10-20 lines)")
print("          cluster by REGIME in a way that matches Brunschwig categories?")
print()

# Analyze each group
for group_name, folios in line_groups.items():
    print(f"{group_name}: {len(folios)} folios")
    regime_counts = defaultdict(int)
    for folio, regime in folios:
        regime_counts[regime] += 1
    for regime in sorted(regime_counts.keys()):
        pct = 100 * regime_counts[regime] / len(folios) if folios else 0
        print(f"    {regime}: {regime_counts[regime]} ({pct:.1f}%)")
    print()

# Focus on medium (Brunschwig-like)
print("-" * 70)
print("MEDIUM LINE COUNT FOLIOS (10-20 lines) - Brunschwig-like structure")
print("-" * 70)
medium = line_groups['medium (10-20)']
for folio, regime in sorted(medium, key=lambda x: x[1]):
    n_lines = len(folio_lines.get(folio, []))
    print(f"  {folio}: {n_lines} lines → {regime}")

# Test: Do medium-sized folios have a distinct REGIME distribution?
print()
print("-" * 70)
print("STRUCTURAL HYPOTHESIS TEST")
print("-" * 70)

# Compare medium vs all
all_regimes = defaultdict(int)
for folio, regime in folio_regime.items():
    all_regimes[regime] += 1

medium_regimes = defaultdict(int)
for folio, regime in medium:
    medium_regimes[regime] += 1

print()
print("REGIME distribution comparison:")
print(f"{'REGIME':<12} {'All Folios':<15} {'Medium (10-20)':<15} {'Difference':<15}")
print("-" * 57)
for regime in sorted(set(all_regimes.keys()) | set(medium_regimes.keys())):
    all_pct = 100 * all_regimes[regime] / sum(all_regimes.values())
    med_pct = 100 * medium_regimes[regime] / len(medium) if medium else 0
    diff = med_pct - all_pct
    print(f"{regime:<12} {all_pct:>6.1f}%        {med_pct:>6.1f}%        {diff:>+6.1f}%")

print()
print("Interpretation:")
print("  If Brunschwig-sized folios (10-20 lines) have a distinct REGIME")
print("  distribution, this suggests structural correlation.")
