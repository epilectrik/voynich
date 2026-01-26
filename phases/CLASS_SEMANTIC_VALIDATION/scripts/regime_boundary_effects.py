"""
Q12: REGIME Boundary Effects

Do patterns change at REGIME transitions? Are there transition effects
when folios change from one REGIME to another?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Role mapping
ENERGY_CLASSES = {8, 31, 32, 33, 34, 36}

def is_energy(cls):
    return cls in ENERGY_CLASSES

print("=" * 70)
print("Q12: REGIME BOUNDARY EFFECTS")
print("=" * 70)

# Build folio sequence with REGIME info
folio_data = defaultdict(lambda: {'tokens': [], 'energy_count': 0, 'total': 0})

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    cls = token_to_class.get(word)
    if cls is not None:
        folio_data[folio]['tokens'].append(cls)
        folio_data[folio]['total'] += 1
        if is_energy(cls):
            folio_data[folio]['energy_count'] += 1

# Add REGIME info and calculate ENERGY rate
for folio in folio_data:
    folio_data[folio]['regime'] = folio_regime.get(folio, 'UNKNOWN')
    total = folio_data[folio]['total']
    folio_data[folio]['energy_rate'] = folio_data[folio]['energy_count'] / total if total > 0 else 0

# Sort folios by manuscript order
def folio_sort_key(f):
    try:
        num = int(''.join(c for c in f if c.isdigit())[:3])
        suffix = ''.join(c for c in f if c.isalpha())
        return (num, suffix)
    except:
        return (999, f)

sorted_folios = sorted(folio_data.keys(), key=folio_sort_key)

print(f"\nTotal folios: {len(sorted_folios)}")

# 1. IDENTIFY REGIME BOUNDARIES
print("\n" + "-" * 70)
print("1. REGIME BOUNDARIES")
print("-" * 70)

boundaries = []
for i in range(1, len(sorted_folios)):
    prev_folio = sorted_folios[i-1]
    curr_folio = sorted_folios[i]
    prev_regime = folio_data[prev_folio]['regime']
    curr_regime = folio_data[curr_folio]['regime']

    if prev_regime != curr_regime:
        boundaries.append({
            'index': i,
            'prev_folio': prev_folio,
            'curr_folio': curr_folio,
            'from_regime': prev_regime,
            'to_regime': curr_regime
        })

print(f"\nREGIME transitions: {len(boundaries)}")
print("\n| From | To | Prev Folio | Curr Folio |")
print("|------|----|-----------:|:-----------|")
for b in boundaries:
    print(f"| {b['from_regime']} | {b['to_regime']} | {b['prev_folio']:>10} | {b['curr_folio']:<10} |")

# 2. ENERGY RATE AT BOUNDARIES
print("\n" + "-" * 70)
print("2. ENERGY RATE AT BOUNDARIES")
print("-" * 70)

# For each boundary, compare:
# - Last folio of old REGIME
# - First folio of new REGIME
# - Average of old REGIME
# - Average of new REGIME

print("\n| Transition | Last EN% | First EN% | Avg Old | Avg New | Jump |")
print("|------------|----------|-----------|---------|---------|------|")

boundary_jumps = []
for b in boundaries:
    prev_folio = b['prev_folio']
    curr_folio = b['curr_folio']
    from_regime = b['from_regime']
    to_regime = b['to_regime']

    last_en = folio_data[prev_folio]['energy_rate'] * 100
    first_en = folio_data[curr_folio]['energy_rate'] * 100

    # Average for each REGIME
    old_regime_folios = [f for f in sorted_folios if folio_data[f]['regime'] == from_regime]
    new_regime_folios = [f for f in sorted_folios if folio_data[f]['regime'] == to_regime]

    avg_old = np.mean([folio_data[f]['energy_rate'] for f in old_regime_folios]) * 100
    avg_new = np.mean([folio_data[f]['energy_rate'] for f in new_regime_folios]) * 100

    jump = first_en - last_en
    boundary_jumps.append(jump)

    print(f"| {from_regime[-1]}->{to_regime[-1]} | {last_en:7.1f}% | {first_en:8.1f}% | {avg_old:6.1f}% | {avg_new:6.1f}% | {jump:+5.1f} |")

print(f"\nMean absolute boundary jump: {np.mean(np.abs(boundary_jumps)):.1f}%")

# 3. COMPARE TO NON-BOUNDARY TRANSITIONS
print("\n" + "-" * 70)
print("3. BOUNDARY VS NON-BOUNDARY TRANSITIONS")
print("-" * 70)

# Calculate all folio-to-folio ENERGY rate changes
all_jumps = []
non_boundary_jumps = []
boundary_indices = set(b['index'] for b in boundaries)

for i in range(1, len(sorted_folios)):
    prev_folio = sorted_folios[i-1]
    curr_folio = sorted_folios[i]
    jump = (folio_data[curr_folio]['energy_rate'] - folio_data[prev_folio]['energy_rate']) * 100
    all_jumps.append(jump)

    if i not in boundary_indices:
        non_boundary_jumps.append(jump)

print(f"\nAll transitions: {len(all_jumps)}")
print(f"  Mean absolute change: {np.mean(np.abs(all_jumps)):.1f}%")
print(f"  Std: {np.std(all_jumps):.1f}%")

print(f"\nNon-boundary transitions: {len(non_boundary_jumps)}")
print(f"  Mean absolute change: {np.mean(np.abs(non_boundary_jumps)):.1f}%")
print(f"  Std: {np.std(non_boundary_jumps):.1f}%")

print(f"\nBoundary transitions: {len(boundary_jumps)}")
print(f"  Mean absolute change: {np.mean(np.abs(boundary_jumps)):.1f}%")
print(f"  Std: {np.std(boundary_jumps):.1f}%")

# Statistical test
stat, p = stats.mannwhitneyu(
    np.abs(boundary_jumps),
    np.abs(non_boundary_jumps),
    alternative='greater'
)
print(f"\nMann-Whitney (boundary > non-boundary): U={stat:.0f}, p={p:.4f}")

if p < 0.05:
    print("-> SIGNIFICANT: Boundaries show larger ENERGY changes")
else:
    print("-> NOT SIGNIFICANT: Boundaries don't show special ENERGY changes")

# 4. REGIME-SPECIFIC TRANSITION PATTERNS
print("\n" + "-" * 70)
print("4. REGIME-SPECIFIC TRANSITION PATTERNS")
print("-" * 70)

# Group by transition type
transition_types = defaultdict(list)
for i, b in enumerate(boundaries):
    key = f"{b['from_regime']}->{b['to_regime']}"
    transition_types[key].append(boundary_jumps[i])

print("\n| Transition Type | Count | Mean Jump | Direction |")
print("|-----------------|-------|-----------|-----------|")
for key in sorted(transition_types.keys()):
    jumps = transition_types[key]
    mean_jump = np.mean(jumps)
    direction = "UP" if mean_jump > 5 else ("DOWN" if mean_jump < -5 else "FLAT")
    print(f"| {key:16s} | {len(jumps):5d} | {mean_jump:+8.1f}% | {direction:9s} |")

# 5. SMOOTHNESS WITHIN VS ACROSS REGIMES
print("\n" + "-" * 70)
print("5. WITHIN-REGIME SMOOTHNESS")
print("-" * 70)

# Calculate variance of ENERGY rate within each REGIME
regime_variances = {}
for regime in sorted(set(folio_regime.values())):
    regime_folios = [f for f in sorted_folios if folio_data[f]['regime'] == regime]
    if len(regime_folios) > 1:
        rates = [folio_data[f]['energy_rate'] for f in regime_folios]
        regime_variances[regime] = np.var(rates)

print("\n| REGIME | Folios | EN% Variance | Std |")
print("|--------|--------|--------------|-----|")
for regime in sorted(regime_variances.keys()):
    regime_folios = [f for f in sorted_folios if folio_data[f]['regime'] == regime]
    var = regime_variances[regime]
    std = np.sqrt(var) * 100
    print(f"| {regime} | {len(regime_folios):6d} | {var*10000:11.1f} | {std:4.1f}% |")

# Overall variance
all_rates = [folio_data[f]['energy_rate'] for f in sorted_folios]
overall_var = np.var(all_rates)
print(f"| OVERALL  | {len(sorted_folios):6d} | {overall_var*10000:11.1f} | {np.sqrt(overall_var)*100:4.1f}% |")

# 6. FIRST/LAST FOLIO EFFECTS
print("\n" + "-" * 70)
print("6. FIRST/LAST FOLIO EFFECTS")
print("-" * 70)

print("\nDo first/last folios of a REGIME differ from middle folios?")

for regime in sorted(set(folio_regime.values())):
    regime_folios = [f for f in sorted_folios if folio_data[f]['regime'] == regime]
    if len(regime_folios) < 3:
        continue

    first_rate = folio_data[regime_folios[0]]['energy_rate'] * 100
    last_rate = folio_data[regime_folios[-1]]['energy_rate'] * 100
    middle_rates = [folio_data[f]['energy_rate'] * 100 for f in regime_folios[1:-1]]
    middle_mean = np.mean(middle_rates) if middle_rates else 0

    print(f"\n{regime}:")
    print(f"  First folio ({regime_folios[0]}): {first_rate:.1f}%")
    print(f"  Last folio ({regime_folios[-1]}): {last_rate:.1f}%")
    print(f"  Middle folios mean: {middle_mean:.1f}%")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

boundary_larger = np.mean(np.abs(boundary_jumps)) > np.mean(np.abs(non_boundary_jumps))

print(f"""
1. REGIME BOUNDARIES: {len(boundaries)} transitions identified

2. BOUNDARY EFFECTS:
   - Boundary mean absolute jump: {np.mean(np.abs(boundary_jumps)):.1f}%
   - Non-boundary mean absolute jump: {np.mean(np.abs(non_boundary_jumps)):.1f}%
   - Boundaries {'DO' if p < 0.05 else 'do NOT'} show larger changes (p={p:.3f})

3. INTERPRETATION:
   - REGIME transitions {'ARE' if p < 0.05 else 'are NOT'} marked by sharp ENERGY shifts
   - {'Supports' if p < 0.05 else 'Contradicts'} distinct operational modes hypothesis
""")

# Save results
results = {
    'boundaries': boundaries,
    'boundary_jumps': boundary_jumps,
    'non_boundary_stats': {
        'mean_abs': float(np.mean(np.abs(non_boundary_jumps))),
        'std': float(np.std(non_boundary_jumps))
    },
    'boundary_stats': {
        'mean_abs': float(np.mean(np.abs(boundary_jumps))),
        'std': float(np.std(boundary_jumps))
    },
    'mann_whitney_p': float(p),
    'regime_variances': {k: float(v) for k, v in regime_variances.items()}
}

with open(RESULTS / 'regime_boundary_effects.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'regime_boundary_effects.json'}")
