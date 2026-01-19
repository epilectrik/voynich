#!/usr/bin/env python3
"""
PHASE 2: SENSORY LOAD INDEX (SLI) CALCULATION

Compute SLI for Voynich B folios and test correlation with HT density.

SLI Formula (simplified from expert recommendation):
    SLI = hazard_density / (escape_density + link_density)

Interpretation:
    High SLI → sensory-critical operation (must catch it just in time)
    Low SLI → robust, forgiving process

Tests:
1. Compute SLI per B folio
2. Correlate with HT density (C477: r=0.504, p=0.0045 for tail_pressure)
3. Test if SLI adds predictive power beyond existing metrics
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 2: SENSORY LOAD INDEX (SLI) CALCULATION")
print("=" * 70)
print()

# Load unified folio profiles
with open('results/unified_folio_profiles.json', 'r') as f:
    profiles_data = json.load(f)

profiles = profiles_data['profiles']

# Filter to B folios with complete metrics
b_folios = []
for folio_id, profile in profiles.items():
    if profile.get('system') == 'B' and profile.get('b_metrics'):
        b_metrics = profile['b_metrics']
        if all(k in b_metrics for k in ['hazard_density', 'escape_density', 'link_density']):
            b_folios.append({
                'folio': folio_id,
                'ht_density': profile['ht_density'],
                'hazard_density': b_metrics['hazard_density'],
                'escape_density': b_metrics['escape_density'],
                'link_density': b_metrics['link_density'],
                'regime': b_metrics.get('regime', 'UNKNOWN'),
                'cei': b_metrics.get('cei_total', 0)
            })

print(f"B folios with complete metrics: {len(b_folios)}")
print()

# ============================================================
# COMPUTE SLI
# ============================================================

print("=" * 70)
print("COMPUTING SENSORY LOAD INDEX")
print("=" * 70)
print()

for folio in b_folios:
    denominator = folio['escape_density'] + folio['link_density']
    if denominator > 0:
        folio['sli'] = folio['hazard_density'] / denominator
    else:
        folio['sli'] = float('inf')  # Maximum constraint pressure

# Filter out infinite SLI
valid_folios = [f for f in b_folios if f['sli'] != float('inf')]
print(f"Folios with valid SLI: {len(valid_folios)}")

# Compute statistics
sli_values = [f['sli'] for f in valid_folios]
ht_values = [f['ht_density'] for f in valid_folios]

print()
print("SLI Statistics:")
print(f"  Mean: {np.mean(sli_values):.3f}")
print(f"  Std:  {np.std(sli_values):.3f}")
print(f"  Min:  {np.min(sli_values):.3f}")
print(f"  Max:  {np.max(sli_values):.3f}")
print()
print("HT Density Statistics:")
print(f"  Mean: {np.mean(ht_values):.3f}")
print(f"  Std:  {np.std(ht_values):.3f}")

# ============================================================
# TEST 1: SLI vs HT DENSITY CORRELATION
# ============================================================

print()
print("=" * 70)
print("TEST 1: SLI vs HT DENSITY CORRELATION")
print("=" * 70)
print()

correlation, p_value = stats.pearsonr(sli_values, ht_values)

print(f"Pearson correlation: r = {correlation:.4f}")
print(f"P-value: {p_value:.6f}")
print()

if p_value < 0.01:
    print("RESULT: STRONG correlation (p < 0.01)")
    print("  -> SLI significantly predicts HT density")
elif p_value < 0.05:
    print("RESULT: MODERATE correlation (p < 0.05)")
    print("  -> SLI has predictive power for HT density")
else:
    print("RESULT: No significant correlation")
    print("  -> SLI does not predict HT density")

# Compare to C477 (tail_pressure: r=0.504, p=0.0045)
print()
print("Comparison to C477 (tail_pressure):")
print(f"  C477: r=0.504, p=0.0045")
print(f"  SLI:  r={correlation:.3f}, p={p_value:.4f}")

if abs(correlation) > 0.504:
    print("  -> SLI has STRONGER correlation than tail_pressure")
elif abs(correlation) > 0.3:
    print("  -> SLI has comparable correlation to tail_pressure")
else:
    print("  -> SLI has weaker correlation than tail_pressure")

# ============================================================
# TEST 2: SLI BY REGIME
# ============================================================

print()
print("=" * 70)
print("TEST 2: SLI BY REGIME")
print("=" * 70)
print()

regime_sli = {}
for folio in valid_folios:
    regime = folio['regime']
    if regime not in regime_sli:
        regime_sli[regime] = []
    regime_sli[regime].append(folio['sli'])

print("Mean SLI by REGIME:")
for regime in sorted(regime_sli.keys()):
    values = regime_sli[regime]
    mean = np.mean(values)
    std = np.std(values)
    print(f"  {regime}: {mean:.3f} +/- {std:.3f} (n={len(values)})")

# ANOVA test
regime_groups = [regime_sli[r] for r in sorted(regime_sli.keys()) if len(regime_sli[r]) > 1]
if len(regime_groups) >= 2:
    f_stat, anova_p = stats.f_oneway(*regime_groups)
    print()
    print(f"ANOVA: F={f_stat:.3f}, p={anova_p:.4f}")

    if anova_p < 0.05:
        print("  -> REGIMEs have significantly different SLI")
    else:
        print("  -> No significant difference in SLI across REGIMEs")

# ============================================================
# TEST 3: HIGH SLI vs LOW SLI FOLIOS
# ============================================================

print()
print("=" * 70)
print("TEST 3: HIGH vs LOW SLI FOLIOS")
print("=" * 70)
print()

# Split into quartiles
sorted_folios = sorted(valid_folios, key=lambda x: x['sli'])
n = len(sorted_folios)
q1 = n // 4
q3 = 3 * n // 4

low_sli = sorted_folios[:q1]
high_sli = sorted_folios[q3:]

low_ht = [f['ht_density'] for f in low_sli]
high_ht = [f['ht_density'] for f in high_sli]

print(f"Low SLI quartile (n={len(low_sli)}):")
print(f"  Mean SLI: {np.mean([f['sli'] for f in low_sli]):.3f}")
print(f"  Mean HT:  {np.mean(low_ht):.3f}")
print()
print(f"High SLI quartile (n={len(high_sli)}):")
print(f"  Mean SLI: {np.mean([f['sli'] for f in high_sli]):.3f}")
print(f"  Mean HT:  {np.mean(high_ht):.3f}")

# T-test
t_stat, t_p = stats.ttest_ind(high_ht, low_ht)
print()
print(f"T-test (HT in high vs low SLI): t={t_stat:.3f}, p={t_p:.4f}")

if t_p < 0.05:
    if np.mean(high_ht) > np.mean(low_ht):
        print("  -> High SLI folios have HIGHER HT density")
        print("  -> Supports 'sensory load increases vigilance' hypothesis")
    else:
        print("  -> High SLI folios have LOWER HT density")
        print("  -> Counter to hypothesis")
else:
    print("  -> No significant difference")

# ============================================================
# SAMPLE EXTREME FOLIOS
# ============================================================

print()
print("=" * 70)
print("EXTREME SLI FOLIOS")
print("=" * 70)
print()

print("Highest SLI (most sensory-critical):")
for f in sorted_folios[-5:]:
    print(f"  {f['folio']}: SLI={f['sli']:.3f}, HT={f['ht_density']:.3f}, {f['regime']}")

print()
print("Lowest SLI (most forgiving):")
for f in sorted_folios[:5]:
    print(f"  {f['folio']}: SLI={f['sli']:.3f}, HT={f['ht_density']:.3f}, {f['regime']}")

# ============================================================
# SAVE RESULTS
# ============================================================

print()
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

results = {
    'phase': 'sensory_load_index',
    'n_folios': len(valid_folios),
    'sli_statistics': {
        'mean': float(np.mean(sli_values)),
        'std': float(np.std(sli_values)),
        'min': float(np.min(sli_values)),
        'max': float(np.max(sli_values))
    },
    'ht_correlation': {
        'r': float(correlation),
        'p': float(p_value),
        'significant': bool(p_value < 0.05)
    },
    'comparison_to_c477': {
        'c477_r': 0.504,
        'c477_p': 0.0045,
        'sli_stronger': bool(abs(correlation) > 0.504)
    },
    'regime_analysis': {
        regime: {
            'mean_sli': float(np.mean(values)),
            'std_sli': float(np.std(values)),
            'n': len(values)
        }
        for regime, values in regime_sli.items()
    },
    'quartile_analysis': {
        'high_sli_mean_ht': float(np.mean(high_ht)),
        'low_sli_mean_ht': float(np.mean(low_ht)),
        't_stat': float(t_stat),
        'p_value': float(t_p)
    },
    'folio_sli': {f['folio']: {'sli': f['sli'], 'ht_density': f['ht_density']} for f in valid_folios},
    'conclusion': 'SLI_CORRELATES' if p_value < 0.05 else 'NO_CORRELATION'
}

output_path = Path('results/sensory_load_index.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to {output_path}")

# ============================================================
# CONCLUSION
# ============================================================

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

if p_value < 0.05:
    print("SENSORY LOAD INDEX TEST: PASSED")
    print()
    print(f"SLI correlates with HT density (r={correlation:.3f}, p={p_value:.4f})")
    print()
    print("Interpretation:")
    print("  -> Higher constraint pressure (high SLI) associates with higher HT")
    print("  -> Sensory-critical operations trigger vigilance signals")
    print("  -> Supports 'cost of misjudging' encoding hypothesis")
else:
    print("SENSORY LOAD INDEX TEST: INCONCLUSIVE")
    print()
    print(f"SLI does not significantly correlate with HT (r={correlation:.3f}, p={p_value:.4f})")
    print()
    print("Interpretation:")
    print("  -> Either SLI metric needs refinement")
    print("  -> Or sensory load encoded through different mechanism")

print()
print("Next: Brittleness gradient analysis (P-zone compression)")
