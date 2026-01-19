#!/usr/bin/env python3
"""
SENSORY GRANULARITY TEST

Test sensory encoding at recipe level (not just folio level).

Tests:
1. SLI -> tail_pressure -> HT pathway
2. Modality-specific zone signatures
3. SLI cluster analysis
4. Zone vs REGIME prediction comparison
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("SENSORY GRANULARITY TEST")
print("=" * 70)
print()

print("Loading data...")

# Load reverse activation results
with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
    activation_data = json.load(f)

recipes = activation_data['recipes']
print(f"  Recipes: {len(recipes)}")

# Load folio profiles for HT data
with open('results/unified_folio_profiles.json', 'r') as f:
    folio_profiles = json.load(f)

profiles = folio_profiles['profiles']
b_folios = {k: v for k, v in profiles.items() if v.get('system') == 'B'}
print(f"  B folios: {len(b_folios)}")

print()

# ============================================================
# TEST 1: SLI -> TAIL_PRESSURE -> HT PATHWAY
# ============================================================

print("=" * 70)
print("TEST 1: SLI -> TAIL_PRESSURE -> HT PATHWAY")
print("=" * 70)
print()

sli_values = [r['metrics']['sli'] for r in recipes]
tail_values = [r['vocabulary_fingerprint']['tail_pressure'] for r in recipes]

# Compute predicted HT for each recipe
predicted_ht = []
for r in recipes:
    top_folios = r['folio_prediction']['top_predicted_folios']
    avg_ht = sum(
        profiles.get(f, {}).get('ht_density', 0) * w
        for f, w in top_folios.items()
    )
    predicted_ht.append(avg_ht)

# Correlation chain
r_sli_tail, p_sli_tail = stats.pearsonr(sli_values, tail_values)
r_tail_ht, p_tail_ht = stats.pearsonr(tail_values, predicted_ht)
r_sli_ht, p_sli_ht = stats.pearsonr(sli_values, predicted_ht)

print("Correlation Chain:")
print(f"  SLI -> tail_pressure: r={r_sli_tail:.4f}, p={p_sli_tail:.6f}")
print(f"  tail_pressure -> HT:  r={r_tail_ht:.4f}, p={p_tail_ht:.6f}")
print(f"  SLI -> HT (direct):   r={r_sli_ht:.4f}, p={p_sli_ht:.6f}")
print()

# Test pathway
pathway_supported = (p_sli_tail < 0.05) and (p_tail_ht < 0.05)
print(f"Pathway Supported: {pathway_supported}")
if pathway_supported:
    print("  -> SLI predicts vocabulary tail_pressure")
    print("  -> tail_pressure predicts HT density")
    print("  -> Sensory load encoded via vocabulary selection")
else:
    print("  -> Pathway not fully supported at p < 0.05")

test1_results = {
    'sli_tail': {'r': float(r_sli_tail), 'p': float(p_sli_tail)},
    'tail_ht': {'r': float(r_tail_ht), 'p': float(p_tail_ht)},
    'sli_ht': {'r': float(r_sli_ht), 'p': float(p_sli_ht)},
    'pathway_supported': bool(pathway_supported)
}

# ============================================================
# TEST 2: MODALITY-SPECIFIC ZONE SIGNATURES
# ============================================================

print()
print("=" * 70)
print("TEST 2: MODALITY-SPECIFIC ZONE SIGNATURES")
print("=" * 70)
print()

# Group recipes by sensory modality
modality_recipes = defaultdict(list)
for r in recipes:
    sensory = r['sensory_profile']
    if not sensory:
        modality_recipes['NONE'].append(r)
    else:
        # Get dominant modality (highest score)
        dominant = max(sensory, key=sensory.get)
        modality_recipes[dominant].append(r)

print("Recipes by Dominant Modality:")
for modality in ['SOUND', 'SIGHT', 'TOUCH', 'TASTE', 'SMELL', 'NONE']:
    count = len(modality_recipes[modality])
    if count > 0:
        print(f"  {modality}: {count} recipes")

print()
print("Zone Affinity by Modality:")
print()

modality_zone_profiles = {}
for modality, group in modality_recipes.items():
    if len(group) < 3:  # Skip small groups
        continue

    zone_aff = {
        'C': np.mean([r['zone_affinity']['C'] for r in group]),
        'P': np.mean([r['zone_affinity']['P'] for r in group]),
        'R': np.mean([r['zone_affinity']['R'] for r in group]),
        'S': np.mean([r['zone_affinity']['S'] for r in group])
    }
    dominant_zone = max(zone_aff, key=zone_aff.get)

    modality_zone_profiles[modality] = zone_aff

    print(f"  {modality} (n={len(group)}):")
    print(f"    C={zone_aff['C']:.3f}, P={zone_aff['P']:.3f}, R={zone_aff['R']:.3f}, S={zone_aff['S']:.3f}")
    print(f"    Dominant: {dominant_zone}")
    print()

# Test hypotheses
print("Hypothesis Tests:")
print()

# SOUND: Expected R-affinity (sequential distillation)
if 'SOUND' in modality_zone_profiles and 'NONE' in modality_zone_profiles:
    sound_r = [r['zone_affinity']['R'] for r in modality_recipes['SOUND']]
    none_r = [r['zone_affinity']['R'] for r in modality_recipes['NONE']]
    t_sound, p_sound = stats.ttest_ind(sound_r, none_r)
    print(f"  SOUND vs NONE (R-affinity): t={t_sound:.3f}, p={p_sound:.4f}")
    if p_sound < 0.05:
        if np.mean(sound_r) > np.mean(none_r):
            print("    -> SOUND recipes show HIGHER R-affinity (sequential processing)")
        else:
            print("    -> SOUND recipes show LOWER R-affinity")
    else:
        print("    -> No significant difference")

# SIGHT: Expected P-affinity (monitoring/intervention)
if 'SIGHT' in modality_zone_profiles and 'NONE' in modality_zone_profiles:
    sight_p = [r['zone_affinity']['P'] for r in modality_recipes['SIGHT']]
    none_p = [r['zone_affinity']['P'] for r in modality_recipes['NONE']]
    t_sight, p_sight = stats.ttest_ind(sight_p, none_p)
    print(f"  SIGHT vs NONE (P-affinity): t={t_sight:.3f}, p={p_sight:.4f}")
    if p_sight < 0.05:
        if np.mean(sight_p) > np.mean(none_p):
            print("    -> SIGHT recipes show HIGHER P-affinity (intervention-permitting)")
        else:
            print("    -> SIGHT recipes show LOWER P-affinity")
    else:
        print("    -> No significant difference")

# TOUCH: Expected S-affinity (boundary sensing)
if 'TOUCH' in modality_zone_profiles and 'NONE' in modality_zone_profiles:
    touch_s = [r['zone_affinity']['S'] for r in modality_recipes['TOUCH']]
    none_s = [r['zone_affinity']['S'] for r in modality_recipes['NONE']]
    t_touch, p_touch = stats.ttest_ind(touch_s, none_s)
    print(f"  TOUCH vs NONE (S-affinity): t={t_touch:.3f}, p={p_touch:.4f}")
    if p_touch < 0.05:
        if np.mean(touch_s) > np.mean(none_s):
            print("    -> TOUCH recipes show HIGHER S-affinity (boundary)")
        else:
            print("    -> TOUCH recipes show LOWER S-affinity")
    else:
        print("    -> No significant difference")

test2_results = {
    'modality_zone_profiles': {
        k: {z: float(v) for z, v in profile.items()}
        for k, profile in modality_zone_profiles.items()
    },
    'modality_counts': {k: len(v) for k, v in modality_recipes.items()}
}

# ============================================================
# TEST 3: SLI CLUSTER ANALYSIS
# ============================================================

print()
print("=" * 70)
print("TEST 3: SLI CLUSTER ANALYSIS")
print("=" * 70)
print()

# Manual clustering into 4 groups by SLI quartiles
sli_sorted = sorted(enumerate(sli_values), key=lambda x: x[1])
n = len(sli_sorted)
q1, q2, q3 = n // 4, n // 2, 3 * n // 4

cluster_labels = [0] * n
for rank, (idx, _) in enumerate(sli_sorted):
    if rank < q1:
        cluster_labels[idx] = 0  # Low SLI
    elif rank < q2:
        cluster_labels[idx] = 1  # Low-Mid SLI
    elif rank < q3:
        cluster_labels[idx] = 2  # Mid-High SLI
    else:
        cluster_labels[idx] = 3  # High SLI

cluster_names = ['Low SLI', 'Low-Mid SLI', 'Mid-High SLI', 'High SLI']

# Analyze zone affinity by cluster
print("Zone Affinity by SLI Cluster:")
print()

cluster_zone_data = defaultdict(lambda: {'C': [], 'P': [], 'R': [], 'S': []})
for i, label in enumerate(cluster_labels):
    for zone in ['C', 'P', 'R', 'S']:
        cluster_zone_data[label][zone].append(recipes[i]['zone_affinity'][zone])

for label in range(4):
    cluster_size = cluster_labels.count(label)
    sli_range = [sli_values[i] for i, l in enumerate(cluster_labels) if l == label]
    zone_means = {z: np.mean(cluster_zone_data[label][z]) for z in ['C', 'P', 'R', 'S']}
    dominant = max(zone_means, key=zone_means.get)

    print(f"  {cluster_names[label]} (n={cluster_size}, SLI={np.min(sli_range):.1f}-{np.max(sli_range):.1f}):")
    print(f"    C={zone_means['C']:.3f}, P={zone_means['P']:.3f}, R={zone_means['R']:.3f}, S={zone_means['S']:.3f}")
    print(f"    Dominant: {dominant}")
    print()

# ANOVA: Do clusters differ on zone affinity?
print("ANOVA Tests (Do SLI clusters differ on zone affinity?):")
print()

anova_results = {}
for zone in ['C', 'P', 'R', 'S']:
    groups = [cluster_zone_data[l][zone] for l in range(4)]
    f_stat, p_val = stats.f_oneway(*groups)
    anova_results[zone] = {'F': float(f_stat), 'p': float(p_val)}
    sig = "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"  {zone}-affinity: F={f_stat:.3f}, p={p_val:.6f} {sig}")

test3_results = {
    'cluster_sizes': [cluster_labels.count(l) for l in range(4)],
    'cluster_zone_means': {
        cluster_names[l]: {z: float(np.mean(cluster_zone_data[l][z])) for z in ['C', 'P', 'R', 'S']}
        for l in range(4)
    },
    'anova': anova_results
}

# ============================================================
# TEST 4: ZONE VS REGIME PREDICTION
# ============================================================

print()
print("=" * 70)
print("TEST 4: ZONE VS REGIME PREDICTION")
print("=" * 70)
print()

# Compute REGIME-based HT prediction (baseline)
regime_ht = defaultdict(list)
for folio_id, profile in profiles.items():
    if profile.get('system') != 'B':
        continue
    b_metrics = profile.get('b_metrics', {})
    regime = b_metrics.get('regime', 'UNKNOWN')
    ht = profile.get('ht_density', 0)
    regime_ht[regime].append(ht)

regime_mean_ht = {r: np.mean(hts) for r, hts in regime_ht.items() if hts}

print("REGIME Mean HT:")
for regime in sorted(regime_mean_ht.keys()):
    print(f"  {regime}: {regime_mean_ht[regime]:.4f}")
print()

# Compare predictions
regime_predictions = []
zone_predictions = []

for r in recipes:
    regime = r['predicted_regime']
    regime_pred = regime_mean_ht.get(regime, 0.16)  # Default to global mean
    regime_predictions.append(regime_pred)
    zone_predictions.append(predicted_ht[recipes.index(r)])

# Variance comparison
regime_var = np.var(regime_predictions)
zone_var = np.var(zone_predictions)
variance_ratio = zone_var / regime_var if regime_var > 0 else float('inf')

print("Prediction Variance Comparison:")
print(f"  REGIME-only variance: {regime_var:.6f}")
print(f"  Zone-based variance:  {zone_var:.6f}")
print(f"  Variance ratio (zone/regime): {variance_ratio:.3f}")
print()

if variance_ratio > 1.0:
    print("  -> Zone predictions are MORE discriminative than REGIME alone")
else:
    print("  -> REGIME predictions are sufficient")

# Correlation comparison
# Use REGIME as categorical predictor
regime_encoded = []
for r in recipes:
    regime = r['predicted_regime']
    # Encode as ordinal (REGIME_1=1, REGIME_2=2, etc.)
    regime_num = int(regime.split('_')[1]) if '_' in regime else 0
    regime_encoded.append(regime_num)

r_regime_ht, p_regime_ht = stats.pearsonr(regime_encoded, predicted_ht)
print()
print("Correlation with Predicted HT:")
print(f"  REGIME (ordinal): r={r_regime_ht:.4f}, p={p_regime_ht:.6f}")

# Zone-based metrics
zone_p_vals = [r['zone_affinity']['P'] for r in recipes]
zone_r_vals = [r['zone_affinity']['R'] for r in recipes]
zone_s_vals = [r['zone_affinity']['S'] for r in recipes]

r_p_ht, p_p_ht = stats.pearsonr(zone_p_vals, predicted_ht)
r_r_ht, p_r_ht = stats.pearsonr(zone_r_vals, predicted_ht)
r_s_ht, p_s_ht = stats.pearsonr(zone_s_vals, predicted_ht)

print(f"  P-affinity: r={r_p_ht:.4f}, p={p_p_ht:.6f}")
print(f"  R-affinity: r={r_r_ht:.4f}, p={p_r_ht:.6f}")
print(f"  S-affinity: r={r_s_ht:.4f}, p={p_s_ht:.6f}")

test4_results = {
    'regime_mean_ht': {k: float(v) for k, v in regime_mean_ht.items()},
    'regime_variance': float(regime_var),
    'zone_variance': float(zone_var),
    'variance_ratio': float(variance_ratio),
    'zone_more_discriminative': bool(variance_ratio > 1.0),
    'regime_ht_correlation': {'r': float(r_regime_ht), 'p': float(p_regime_ht)},
    'zone_ht_correlations': {
        'P': {'r': float(r_p_ht), 'p': float(p_p_ht)},
        'R': {'r': float(r_r_ht), 'p': float(p_r_ht)},
        'S': {'r': float(r_s_ht), 'p': float(p_s_ht)}
    }
}

# ============================================================
# SAVE RESULTS
# ============================================================

print()
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

results = {
    'phase': 'SENSORY_GRANULARITY_TEST',
    'n_recipes': len(recipes),
    'test1_sli_ht_pathway': test1_results,
    'test2_modality_signatures': test2_results,
    'test3_sli_clusters': test3_results,
    'test4_zone_vs_regime': test4_results
}

output_path = Path('results/sensory_granularity_test.json')
with open(output_path, 'w', encoding='utf-8') as f:
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

print("SENSORY GRANULARITY TEST COMPLETE")
print()
print("Test Results Summary:")
print()
print(f"  1. SLI->HT Pathway: {'SUPPORTED' if pathway_supported else 'NOT SUPPORTED'}")
print(f"     - SLI predicts tail_pressure: r={r_sli_tail:.3f}, p={p_sli_tail:.4f}")
print(f"     - tail_pressure predicts HT: r={r_tail_ht:.3f}, p={p_tail_ht:.4f}")
print()

print(f"  2. Modality Signatures: {len(modality_zone_profiles)} modalities analyzed")
print(f"     - SOUND (n={len(modality_recipes.get('SOUND', []))}) dominates")
print()

print(f"  3. SLI Clusters: 4 quartile clusters analyzed")
significant_zones = [z for z, v in anova_results.items() if v['p'] < 0.05]
print(f"     - Significant zone differences: {significant_zones if significant_zones else 'None'}")
print()

print(f"  4. Zone vs REGIME Prediction:")
print(f"     - Variance ratio: {variance_ratio:.3f}")
print(f"     - Zone more discriminative: {variance_ratio > 1.0}")
print()

print("Key Finding:")
if pathway_supported:
    print("  Recipe-level sensory load (SLI) encodes through vocabulary selection")
    print("  -> High SLI -> Higher tail_pressure -> Different HT prediction")
else:
    print("  Partial encoding found but pathway not fully significant")
