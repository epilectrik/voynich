#!/usr/bin/env python3
"""
BRUNSCHWIG STRUCTURAL MATCH TEST v2

Question: Do Voynich folios with Brunschwig-like line counts
have REGIMEs consistent with Brunschwig material categories?
"""
import csv
from collections import defaultdict

# Parse REGIME from proposed_folio_order.txt
folio_regime = {}
with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
    for line in f:
        parts = line.split('|')
        if len(parts) >= 3:
            folio = parts[1].strip()
            regime = parts[2].strip()
            if folio.startswith('f') and regime.startswith('REGIME'):
                folio_regime[folio] = regime

print(f"Loaded {len(folio_regime)} folio REGIME assignments")

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

for folio, regime in folio_regime.items():
    n_lines = len(folio_lines.get(folio, []))

    if n_lines <= 9:
        line_groups['small (5-9)'].append((folio, regime, n_lines))
    elif n_lines <= 20:
        line_groups['medium (10-20)'].append((folio, regime, n_lines))
    elif n_lines <= 40:
        line_groups['large (21-40)'].append((folio, regime, n_lines))
    else:
        line_groups['very_large (41+)'].append((folio, regime, n_lines))

print("=" * 70)
print("BRUNSCHWIG STRUCTURAL MATCH TEST")
print("=" * 70)
print()
print("Question: Do folios with Brunschwig-like structure (10-20 lines)")
print("          cluster by REGIME differently than other folios?")
print()

# Analyze each group
for group_name, folios in line_groups.items():
    print(f"{group_name}: {len(folios)} folios")
    regime_counts = defaultdict(int)
    for folio, regime, n in folios:
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
for folio, regime, n_lines in sorted(medium, key=lambda x: x[1]):
    print(f"  {folio}: {n_lines} lines -> {regime}")

# Test: Do medium-sized folios have a distinct REGIME distribution?
print()
print("-" * 70)
print("STRUCTURAL HYPOTHESIS TEST")
print("-" * 70)

# Compare medium vs all
all_regimes = defaultdict(int)
for regime in folio_regime.values():
    all_regimes[regime] += 1

medium_regimes = defaultdict(int)
for folio, regime, n in medium:
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
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()
print("Brunschwig material categories and expected REGIMEs:")
print("  - Cold/moist flowers (First degree) -> REGIME_2 (gentle)")
print("  - Hot/dry herbs (Third degree) -> REGIME_3 (intense)")
print("  - Complex roots (Second degree) -> REGIME_1 (moderate)")
print()

# Check if REGIME_4 is over/under-represented in medium folios
r4_all = 100 * all_regimes['REGIME_4'] / sum(all_regimes.values())
r4_med = 100 * medium_regimes['REGIME_4'] / len(medium) if medium else 0

if r4_med > r4_all + 10:
    print("FINDING: REGIME_4 is OVER-represented in Brunschwig-sized folios")
    print("         This suggests precision-requiring procedures fit this structure")
elif r4_med < r4_all - 10:
    print("FINDING: REGIME_4 is UNDER-represented in Brunschwig-sized folios")
else:
    print("FINDING: No strong REGIME bias for Brunschwig-sized folios")
    print("         Line count does not predict REGIME")
