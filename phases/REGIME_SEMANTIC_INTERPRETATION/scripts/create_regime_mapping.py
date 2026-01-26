"""
Create REGIME folio mapping based on LINE_BOUNDARY_OPERATORS findings.

From RESULTS.md:
- REGIME_1/3: Higher L-compound, higher ENERGY, lower LATE (control-intensive)
- REGIME_2/4: Lower L-compound, lower ENERGY, higher LATE (output-intensive)

Classification scheme:
- REGIME_1: High L-compound, High ENERGY
- REGIME_2: Low L-compound, Low ENERGY, High LATE
- REGIME_3: High L-compound, Low LATE
- REGIME_4: Low L-compound, High LATE
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import json
import os

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CREATE REGIME FOLIO MAPPING")
print("=" * 70)

# Setup
LATE_PREFIXES = {'al', 'ar', 'or'}
ENERGY_PREFIXES = {'ch', 'sh', 'qo', 'tch', 'pch', 'dch', 'lsh'}

def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    if middle[0] != 'l':
        return False
    return middle[1] not in 'aeioy'

# Collect all B tokens
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'folio': token.folio,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })

print(f"\nTotal B tokens: {len(b_tokens)}")

# Build folio stats
folio_stats = defaultdict(lambda: {
    'total': 0,
    'l_compound': 0,
    'late': 0,
    'energy': 0,
})

for tok in b_tokens:
    f = tok['folio']
    folio_stats[f]['total'] += 1

    if is_l_compound(tok['middle']):
        folio_stats[f]['l_compound'] += 1
    if tok['prefix'] in LATE_PREFIXES:
        folio_stats[f]['late'] += 1
    if tok['prefix'] in ENERGY_PREFIXES:
        folio_stats[f]['energy'] += 1

# Compute rates for folios with sufficient tokens
folio_profiles = []
for folio, stats in folio_stats.items():
    if stats['total'] >= 50:
        folio_profiles.append({
            'folio': folio,
            'total': stats['total'],
            'l_rate': stats['l_compound'] / stats['total'] * 100,
            'late_rate': stats['late'] / stats['total'] * 100,
            'energy_rate': stats['energy'] / stats['total'] * 100,
        })

print(f"Folios with 50+ tokens: {len(folio_profiles)}")

# Compute medians
l_rates = [p['l_rate'] for p in folio_profiles]
late_rates = [p['late_rate'] for p in folio_profiles]
energy_rates = [p['energy_rate'] for p in folio_profiles]

median_l = np.median(l_rates)
median_late = np.median(late_rates)
median_energy = np.median(energy_rates)

print(f"\nMedians:")
print(f"  L-compound: {median_l:.2f}%")
print(f"  LATE: {median_late:.2f}%")
print(f"  ENERGY: {median_energy:.2f}%")

# Classify into 4 REGIMEs based on L-compound and LATE
# REGIME_1: High L, High ENERGY -> control-intensive with active intervention
# REGIME_2: Low L, High LATE -> output-intensive, late marking
# REGIME_3: High L, Low LATE -> control-intensive, less output
# REGIME_4: Low L, Low LATE, but has distinct pattern -> balanced

regime_mapping = {
    'REGIME_1': [],
    'REGIME_2': [],
    'REGIME_3': [],
    'REGIME_4': [],
}

for p in folio_profiles:
    high_l = p['l_rate'] > median_l
    high_late = p['late_rate'] > median_late
    high_energy = p['energy_rate'] > median_energy

    # Classification based on combined patterns
    if high_l and high_energy:
        regime_mapping['REGIME_1'].append(p['folio'])
    elif not high_l and high_late:
        regime_mapping['REGIME_2'].append(p['folio'])
    elif high_l and not high_late:
        regime_mapping['REGIME_3'].append(p['folio'])
    else:  # low L, low LATE
        regime_mapping['REGIME_4'].append(p['folio'])

print("\n" + "=" * 70)
print("REGIME CLASSIFICATION")
print("=" * 70)

for regime, folios in sorted(regime_mapping.items()):
    print(f"\n{regime}: {len(folios)} folios")
    # Compute average stats for this REGIME
    regime_profiles = [p for p in folio_profiles if p['folio'] in folios]
    if regime_profiles:
        avg_l = np.mean([p['l_rate'] for p in regime_profiles])
        avg_late = np.mean([p['late_rate'] for p in regime_profiles])
        avg_energy = np.mean([p['energy_rate'] for p in regime_profiles])
        print(f"  Avg L-compound: {avg_l:.2f}%")
        print(f"  Avg LATE: {avg_late:.2f}%")
        print(f"  Avg ENERGY: {avg_energy:.2f}%")

# Save mapping
os.makedirs('results', exist_ok=True)
with open('results/regime_folio_mapping.json', 'w') as f:
    json.dump(regime_mapping, f, indent=2)

print("\n" + "=" * 70)
print("Saved to results/regime_folio_mapping.json")
print("=" * 70)

# Also save folio profiles for further analysis
folio_profile_dict = {p['folio']: p for p in folio_profiles}
with open('results/folio_profiles.json', 'w') as f:
    json.dump(folio_profile_dict, f, indent=2)

print("Saved folio profiles to results/folio_profiles.json")
