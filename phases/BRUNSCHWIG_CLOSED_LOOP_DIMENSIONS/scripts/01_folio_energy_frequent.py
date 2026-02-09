#!/usr/bin/env python3
"""
Test 1: Folio-Level Verification of C891 (ENERGY-FREQUENT Inverse)

Confirms that the REGIME-level inverse correlation (rho=-0.80) holds
at folio level (n=83), providing stronger statistical confidence.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load class map
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map = json.load(f)

token_to_role = class_map.get('token_to_role', {})

# Load REGIME mapping for comparison
with open(Path(__file__).parent.parent.parent.parent / 'results' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    regime_num = int(regime.replace('REGIME_', ''))
    for folio in folios:
        folio_regime[folio] = regime_num

# Load transcript
tx = Transcript()

print("="*70)
print("TEST 1: FOLIO-LEVEL ENERGY-FREQUENT CORRELATION")
print("="*70)

# Compute role densities per folio
folio_stats = defaultdict(lambda: {'total': 0, 'ENERGY_OPERATOR': 0, 'FREQUENT_OPERATOR': 0})

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio = token.folio
    word = token.word

    folio_stats[folio]['total'] += 1
    role = token_to_role.get(word)
    if role == 'ENERGY_OPERATOR':
        folio_stats[folio]['ENERGY_OPERATOR'] += 1
    elif role == 'FREQUENT_OPERATOR':
        folio_stats[folio]['FREQUENT_OPERATOR'] += 1

# Compute densities and prepare for correlation
folio_data = []
for folio in sorted(folio_stats.keys()):
    s = folio_stats[folio]
    if s['total'] < 50:  # Skip folios with too few tokens
        continue
    energy_rate = s['ENERGY_OPERATOR'] / s['total']
    frequent_rate = s['FREQUENT_OPERATOR'] / s['total']
    regime = folio_regime.get(folio)
    folio_data.append({
        'folio': folio,
        'regime': regime,
        'energy_rate': energy_rate,
        'frequent_rate': frequent_rate,
        'total_tokens': s['total']
    })

print(f"\nFolios analyzed: {len(folio_data)} (with 50+ tokens)")

# Extract arrays for correlation
energy_rates = np.array([d['energy_rate'] for d in folio_data])
frequent_rates = np.array([d['frequent_rate'] for d in folio_data])

# Spearman correlation
rho, p = scipy_stats.spearmanr(energy_rates, frequent_rates)

print(f"\n{'='*70}")
print("FOLIO-LEVEL CORRELATION")
print("="*70)
print(f"\nSpearman rho: {rho:.3f}")
print(f"p-value: {p:.2e}")
print(f"n: {len(folio_data)}")

# Compare to REGIME-level
print(f"\nComparison:")
print(f"  REGIME-level (n=4): rho = -0.80")
print(f"  Folio-level (n={len(folio_data)}): rho = {rho:.3f}")

if rho < -0.3 and p < 0.05:
    verdict = "CONFIRMED"
    print(f"\n** FOLIO-LEVEL CONFIRMS C891 **")
elif rho < 0 and p < 0.1:
    verdict = "PARTIAL"
    print(f"\nPartial confirmation (weaker than REGIME-level)")
else:
    verdict = "NOT CONFIRMED"
    print(f"\nFolio-level does not confirm REGIME pattern")

# Breakdown by REGIME
print(f"\n{'='*70}")
print("BREAKDOWN BY REGIME")
print("="*70)

for regime in sorted(set(d['regime'] for d in folio_data if d['regime'])):
    regime_folios = [d for d in folio_data if d['regime'] == regime]
    mean_energy = np.mean([d['energy_rate'] for d in regime_folios])
    mean_frequent = np.mean([d['frequent_rate'] for d in regime_folios])
    print(f"  R{regime}: n={len(regime_folios)}, mean_ENERGY={mean_energy:.3f}, mean_FREQUENT={mean_frequent:.3f}")

# Within-REGIME correlations
print(f"\n{'='*70}")
print("WITHIN-REGIME CORRELATIONS")
print("="*70)

for regime in sorted(set(d['regime'] for d in folio_data if d['regime'])):
    regime_folios = [d for d in folio_data if d['regime'] == regime]
    if len(regime_folios) >= 5:
        e = [d['energy_rate'] for d in regime_folios]
        f = [d['frequent_rate'] for d in regime_folios]
        r, p_within = scipy_stats.spearmanr(e, f)
        print(f"  R{regime} (n={len(regime_folios)}): rho={r:.3f}, p={p_within:.3f}")
    else:
        print(f"  R{regime}: insufficient data (n={len(regime_folios)})")

# Save results
output = {
    'test': 'Folio-Level ENERGY-FREQUENT Correlation',
    'n_folios': len(folio_data),
    'spearman_rho': float(rho),
    'p_value': float(p),
    'regime_level_rho': -0.80,
    'verdict': verdict,
    'interpretation': {
        'confirmed': verdict == 'CONFIRMED',
        'effect_direction': 'inverse' if rho < 0 else 'positive',
        'statistical_significance': bool(p < 0.05)
    },
    'folio_data': folio_data
}

output_path = results_dir / 'folio_energy_frequent.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
