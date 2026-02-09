#!/usr/bin/env python3
"""
Test 10: Role Composition Orthogonality

Tests whether different role compositions vary independently across REGIMEs,
particularly the ENERGY_OPERATOR vs FREQUENT_OPERATOR inverse correlation.

Findings:
- C891: ENERGY-FREQUENT inverse correlation (rho = -0.80)
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

token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}
token_to_role = class_map.get('token_to_role', {})

# Build role token sets
role_tokens = defaultdict(set)
for token, role in token_to_role.items():
    role_tokens[role].add(token)

# Load REGIME mapping
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
print("TEST 10: ROLE COMPOSITION ORTHOGONALITY")
print("="*70)

# Compute role densities per REGIME
roles = ['CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'AUXILIARY']

regime_stats = defaultdict(lambda: {r: 0 for r in roles + ['total']})

for token in tx.currier_b():
    if '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if regime is None:
        continue

    word = token.word
    regime_stats[regime]['total'] += 1

    role = token_to_role.get(word)
    if role and role in regime_stats[regime]:
        regime_stats[regime][role] += 1

# Compute profiles
regime_profiles = {}
for regime in sorted(regime_stats.keys()):
    s = regime_stats[regime]
    total = s['total']
    profile = {}
    for role in roles:
        profile[role] = 100 * s[role] / total if total > 0 else 0
    regime_profiles[regime] = profile

# Print results
print("\nRole Composition by REGIME (%):")
print("-"*80)
header = "REGIME   " + "  ".join([r[:10] for r in roles])
print(header)
print("-"*80)

for regime in sorted(regime_profiles.keys()):
    p = regime_profiles[regime]
    values = "  ".join([f"{p[r]:6.1f}" for r in roles])
    print(f"  R{regime}      {values}")

# Compute pairwise correlations
print("\n" + "="*70)
print("PAIRWISE CORRELATIONS")
print("="*70)

def compare_roles(r1, r2):
    vals1 = [regime_profiles[r][r1] for r in sorted(regime_profiles.keys())]
    vals2 = [regime_profiles[r][r2] for r in sorted(regime_profiles.keys())]
    if np.std(vals1) > 0 and np.std(vals2) > 0:
        rho, p = scipy_stats.spearmanr(vals1, vals2)
        return float(rho), float(p)
    return None, None

correlations = {}
print("\nRole Pair                      rho      Interpretation")
print("-"*60)

key_pairs = [
    ('ENERGY_OPERATOR', 'FREQUENT_OPERATOR'),
    ('ENERGY_OPERATOR', 'FLOW_OPERATOR'),
    ('CORE_CONTROL', 'FREQUENT_OPERATOR'),
    ('CORE_CONTROL', 'ENERGY_OPERATOR'),
]

for r1, r2 in key_pairs:
    rho, p = compare_roles(r1, r2)
    if rho is not None:
        if abs(rho) < 0.3:
            interp = "orthogonal"
        elif rho > 0.3:
            interp = "aligned"
        else:
            interp = "INVERSE"
        correlations[f"{r1}_vs_{r2}"] = {'rho': rho, 'p': p, 'interpretation': interp}
        print(f"  {r1[:12]:12s} vs {r2[:12]:12s}   {rho:+.2f}    {interp}")

# Key finding: ENERGY vs FREQUENT
energy_freq_rho = correlations.get('ENERGY_OPERATOR_vs_FREQUENT_OPERATOR', {}).get('rho', 0)
strong_inverse = energy_freq_rho < -0.5

print("\n" + "="*70)
print("KEY FINDING: C891")
print("="*70)
print(f"\nENERGY_OPERATOR vs FREQUENT_OPERATOR correlation: rho = {energy_freq_rho:.2f}")
if strong_inverse:
    print("** STRONG INVERSE CONFIRMED **")
    print("\nInterpretation:")
    print("  High energy processing (R3) -> low escape operators")
    print("  Precision processing (R4) -> high escape operators")
    print("  These are orthogonal control dimensions")
else:
    print("Inverse relationship weaker than expected")

# Rankings
print("\n" + "="*70)
print("REGIME RANKINGS BY ROLE")
print("="*70)

rankings = {}
for role in roles:
    sorted_regimes = sorted(regime_profiles.keys(),
                           key=lambda r: regime_profiles[r][role],
                           reverse=True)
    rankings[role] = [f'R{r}' for r in sorted_regimes]
    print(f"  {role}: {' > '.join(rankings[role])}")

# Save results
output = {
    'test': 'Role Composition Orthogonality',
    'findings': {
        'C891_energy_frequent_inverse': {
            'rho': energy_freq_rho,
            'strong_inverse': strong_inverse,
            'interpretation': 'High energy = low escape; low energy = high escape'
        }
    },
    'correlations': correlations,
    'regime_profiles': {str(k): v for k, v in regime_profiles.items()},
    'rankings': rankings,
    'verdict': 'SUPPORT' if strong_inverse else 'PARTIAL',
    'note': 'n=4 REGIMEs; folio-level confirmation recommended for confidence intervals'
}

output_path = results_dir / 'role_orthogonality.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {output['verdict']}")
