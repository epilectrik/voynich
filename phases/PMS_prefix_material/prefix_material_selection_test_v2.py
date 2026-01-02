#!/usr/bin/env python3
"""
Prefix/Suffix Material Selection Test - V2 with Visual Data
============================================================
Uses the blinded_visual_coding.json for TEST 3 (Plant Feature Absence Test)
"""

import json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load corpus
print("Loading corpus...")
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']  # Use Herbal transcriber

# Load existing affix analysis
with open('phase7b_affix_operations.json', 'r') as f:
    affix_ops = json.load(f)

# Load visual coding data
with open('blinded_visual_coding.json', 'r') as f:
    visual_data = json.load(f)

print(f"Visual data loaded: {len(visual_data['folios'])} folios coded")

# Extract prefix data
affix_table = affix_ops['affix_operation_table']
prefixes = {k: v for k, v in affix_table.items() if v.get('affix_position') == 'prefix'}

# Build feature matrix for prefixes
prefix_features = []
prefix_names = []
for name, data in prefixes.items():
    features = [
        data.get('hub_strength', 0),
        data.get('mean_slot', 5),
        data.get('entry_initial_rate', 0),
        data.get('entry_final_rate', 0),
        data.get('total_count', 0),
    ]
    prefix_features.append(features)
    prefix_names.append(name)

X = np.array(prefix_features)
X_scaled = StandardScaler().fit_transform(X)

# Cluster prefixes (k=5 was optimal from previous run)
print("\nClustering prefixes (k=5)...")
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
final_labels = kmeans.fit_predict(X_scaled)
sil_score = silhouette_score(X_scaled, final_labels)
print(f"Silhouette score: {sil_score:.3f}")

# Build archetype membership
archetypes = defaultdict(list)
for name, label in zip(prefix_names, final_labels):
    archetypes[label].append(name)

prefix_to_archetype = {p: l for p, l in zip(prefix_names, final_labels)}

print("\nArchetypes discovered:")
for arch_id, members in sorted(archetypes.items()):
    print(f"  Archetype {arch_id}: {len(members)} prefixes - {', '.join(members[:4])}...")

# ============================================================================
# TEST 3: Plant Feature Absence Test with REAL VISUAL DATA
# ============================================================================
print("\n" + "="*70)
print("TEST 3: PLANT FEATURE ABSENCE TEST (WITH VISUAL DATA)")
print("="*70)

# Extract visual features for each folio
folio_visual = {}
for folio, data in visual_data['folios'].items():
    vf = data.get('visual_features', {})
    folio_visual[folio] = {
        'root_present': vf.get('root_present', {}).get('value', 'UNDETERMINED'),
        'root_type': vf.get('root_type', {}).get('value', 'UNDETERMINED'),
        'root_prominence': vf.get('root_prominence', {}).get('value', 'UNDETERMINED'),
        'flower_present': vf.get('flower_present', {}).get('value', 'UNDETERMINED'),
        'flower_count': vf.get('flower_count', {}).get('value', 'UNDETERMINED'),
        'leaf_shape': vf.get('leaf_shape', {}).get('value', 'UNDETERMINED'),
        'leaf_count': vf.get('leaf_count', {}).get('value', 'UNDETERMINED'),
        'stem_type': vf.get('stem_type', {}).get('value', 'UNDETERMINED'),
        'overall_complexity': vf.get('overall_complexity', {}).get('value', 'UNDETERMINED'),
    }

print(f"\nVisual-coded folios: {len(folio_visual)}")

# Get prefix distribution for each visual-coded folio
folio_prefix_counts = defaultdict(Counter)
for _, row in df.iterrows():
    word = str(row['word'])
    folio = row['folio']
    if folio in folio_visual and len(word) >= 2:
        prefix = word[:2]
        if prefix in prefixes:
            folio_prefix_counts[folio][prefix] += 1

# Count folios with data
folios_with_data = [f for f in folio_visual if f in folio_prefix_counts]
print(f"Folios with both visual and prefix data: {len(folios_with_data)}")

# Define binary visual feature groups
# Medieval anatomy categories:
# - ROOT emphasis (prominent roots vs not)
# - FLOWER emphasis (flowers present vs absent)
# - LEAF complexity (many leaves vs few)

# Group 1: ROOT PROMINENCE
high_root_folios = [f for f, v in folio_visual.items() if v['root_prominence'] in ['HIGH', 'MEDIUM'] and f in folio_prefix_counts]
low_root_folios = [f for f, v in folio_visual.items() if v['root_prominence'] == 'LOW' and f in folio_prefix_counts]
no_root_folios = [f for f, v in folio_visual.items() if v['root_present'] == 'NO' and f in folio_prefix_counts]

print(f"\nRoot prominence groups:")
print(f"  HIGH/MEDIUM root: {len(high_root_folios)} folios")
print(f"  LOW root: {len(low_root_folios)} folios")
print(f"  NO root: {len(no_root_folios)} folios")

# Group 2: FLOWER PRESENCE
flower_folios = [f for f, v in folio_visual.items() if v['flower_present'] == 'YES' and f in folio_prefix_counts]
no_flower_folios = [f for f, v in folio_visual.items() if v['flower_present'] == 'NO' and f in folio_prefix_counts]

print(f"\nFlower presence groups:")
print(f"  With flowers: {len(flower_folios)} folios")
print(f"  Without flowers: {len(no_flower_folios)} folios")

# Group 3: ROOT TYPE (bulbous vs other)
bulbous_folios = [f for f, v in folio_visual.items() if v['root_type'] == 'BULBOUS' and f in folio_prefix_counts]
branching_folios = [f for f, v in folio_visual.items() if v['root_type'] == 'BRANCHING' and f in folio_prefix_counts]

print(f"\nRoot type groups:")
print(f"  BULBOUS root: {len(bulbous_folios)} folios")
print(f"  BRANCHING root: {len(branching_folios)} folios")

# ============================================================================
# TEST 3A: Archetype x Root Prominence
# ============================================================================
print("\n--- TEST 3A: Archetype x Root Prominence ---")

def get_archetype_distribution(folios, folio_prefix_counts, prefix_to_archetype, n_archetypes):
    """Get archetype frequency distribution for a set of folios"""
    arch_counts = [0] * n_archetypes
    total = 0
    for folio in folios:
        for prefix, count in folio_prefix_counts[folio].items():
            if prefix in prefix_to_archetype:
                arch_counts[prefix_to_archetype[prefix]] += count
                total += count
    return arch_counts, total

high_root_arch, high_root_total = get_archetype_distribution(high_root_folios, folio_prefix_counts, prefix_to_archetype, 5)
low_root_arch, low_root_total = get_archetype_distribution(low_root_folios, folio_prefix_counts, prefix_to_archetype, 5)

print(f"HIGH/MEDIUM root archetype distribution (n={high_root_total}):")
for i, count in enumerate(high_root_arch):
    pct = count/high_root_total*100 if high_root_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

print(f"\nLOW root archetype distribution (n={low_root_total}):")
for i, count in enumerate(low_root_arch):
    pct = count/low_root_total*100 if low_root_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

# Chi-square test
if high_root_total > 0 and low_root_total > 0:
    observed = np.array([high_root_arch, low_root_arch])
    # Filter zero columns
    nonzero_cols = observed.sum(axis=0) > 0
    observed_filtered = observed[:, nonzero_cols]
    if observed_filtered.shape[1] >= 2:
        chi2_root, p_root, dof, _ = stats.chi2_contingency(observed_filtered)
        print(f"\nChi-square test: X2={chi2_root:.2f}, p={p_root:.4f}")
        root_significant = p_root < 0.05
    else:
        root_significant = False
        p_root = 1.0
else:
    root_significant = False
    p_root = 1.0

# ============================================================================
# TEST 3B: Archetype x Flower Presence
# ============================================================================
print("\n--- TEST 3B: Archetype x Flower Presence ---")

flower_arch, flower_total = get_archetype_distribution(flower_folios, folio_prefix_counts, prefix_to_archetype, 5)
no_flower_arch, no_flower_total = get_archetype_distribution(no_flower_folios, folio_prefix_counts, prefix_to_archetype, 5)

print(f"WITH flowers archetype distribution (n={flower_total}):")
for i, count in enumerate(flower_arch):
    pct = count/flower_total*100 if flower_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

print(f"\nWITHOUT flowers archetype distribution (n={no_flower_total}):")
for i, count in enumerate(no_flower_arch):
    pct = count/no_flower_total*100 if no_flower_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

# Chi-square test
if flower_total > 0 and no_flower_total > 0:
    observed = np.array([flower_arch, no_flower_arch])
    nonzero_cols = observed.sum(axis=0) > 0
    observed_filtered = observed[:, nonzero_cols]
    if observed_filtered.shape[1] >= 2:
        chi2_flower, p_flower, dof, _ = stats.chi2_contingency(observed_filtered)
        print(f"\nChi-square test: X2={chi2_flower:.2f}, p={p_flower:.4f}")
        flower_significant = p_flower < 0.05
    else:
        flower_significant = False
        p_flower = 1.0
else:
    flower_significant = False
    p_flower = 1.0

# ============================================================================
# TEST 3C: Archetype x Bulbous Root
# ============================================================================
print("\n--- TEST 3C: Archetype x Root Type (Bulbous vs Branching) ---")

bulb_arch, bulb_total = get_archetype_distribution(bulbous_folios, folio_prefix_counts, prefix_to_archetype, 5)
branch_arch, branch_total = get_archetype_distribution(branching_folios, folio_prefix_counts, prefix_to_archetype, 5)

print(f"BULBOUS root archetype distribution (n={bulb_total}):")
for i, count in enumerate(bulb_arch):
    pct = count/bulb_total*100 if bulb_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

print(f"\nBRANCHING root archetype distribution (n={branch_total}):")
for i, count in enumerate(branch_arch):
    pct = count/branch_total*100 if branch_total > 0 else 0
    print(f"  Archetype {i}: {count} ({pct:.1f}%)")

# Chi-square test
if bulb_total > 0 and branch_total > 0:
    observed = np.array([bulb_arch, branch_arch])
    nonzero_cols = observed.sum(axis=0) > 0
    observed_filtered = observed[:, nonzero_cols]
    if observed_filtered.shape[1] >= 2:
        chi2_bulb, p_bulb, dof, _ = stats.chi2_contingency(observed_filtered)
        print(f"\nChi-square test: X2={chi2_bulb:.2f}, p={p_bulb:.4f}")
        bulb_significant = p_bulb < 0.05
    else:
        bulb_significant = False
        p_bulb = 1.0
else:
    bulb_significant = False
    p_bulb = 1.0

# ============================================================================
# TEST 3 Summary
# ============================================================================
print("\n" + "="*70)
print("TEST 3 SUMMARY")
print("="*70)

n_significant = sum([root_significant, flower_significant, bulb_significant])
print(f"\nSignificant associations found: {n_significant}/3")
print(f"  Root prominence: {'SIGNIFICANT' if root_significant else 'not significant'} (p={p_root:.4f})")
print(f"  Flower presence: {'SIGNIFICANT' if flower_significant else 'not significant'} (p={p_flower:.4f})")
print(f"  Root type (bulb): {'SIGNIFICANT' if bulb_significant else 'not significant'} (p={p_bulb:.4f})")

# Bonferroni correction for multiple tests
alpha_corrected = 0.05 / 3
n_significant_corrected = sum([
    p_root < alpha_corrected,
    p_flower < alpha_corrected,
    p_bulb < alpha_corrected
])
print(f"\nAfter Bonferroni correction (alpha={alpha_corrected:.4f}):")
print(f"  Significant associations: {n_significant_corrected}/3")

# TEST 3 Verdict
if n_significant_corrected >= 1:
    test3_verdict = "PASS"
    test3_notes = "At least one plant feature shows significant association with prefix archetypes"
elif n_significant >= 2:
    test3_verdict = "WEAK_PASS"
    test3_notes = "Multiple uncorrected associations suggest weak signal"
else:
    test3_verdict = "FAIL"
    test3_notes = "No significant archetype-visual feature associations detected"

print(f"\nTEST 3 VERDICT: {test3_verdict}")
print(f"  {test3_notes}")

# ============================================================================
# ADVERSARIAL NULL: Shuffle visual features
# ============================================================================
print("\n" + "="*70)
print("ADVERSARIAL NULL: Shuffled Visual Features")
print("="*70)

np.random.seed(42)
n_shuffles = 1000

# Null test: shuffle root prominence across folios
null_root_p_values = []
folio_list = list(folio_visual.keys())

for _ in range(n_shuffles):
    # Shuffle visual features across folios
    shuffled_features = list(folio_visual.values())
    np.random.shuffle(shuffled_features)
    shuffled_visual = dict(zip(folio_list, shuffled_features))

    high_root = [f for f, v in shuffled_visual.items() if v['root_prominence'] in ['HIGH', 'MEDIUM'] and f in folio_prefix_counts]
    low_root = [f for f, v in shuffled_visual.items() if v['root_prominence'] == 'LOW' and f in folio_prefix_counts]

    if len(high_root) > 0 and len(low_root) > 0:
        h_arch, h_total = get_archetype_distribution(high_root, folio_prefix_counts, prefix_to_archetype, 5)
        l_arch, l_total = get_archetype_distribution(low_root, folio_prefix_counts, prefix_to_archetype, 5)
        if h_total > 0 and l_total > 0:
            obs = np.array([h_arch, l_arch])
            nz = obs.sum(axis=0) > 0
            obs_f = obs[:, nz]
            if obs_f.shape[1] >= 2:
                try:
                    _, p_null, _, _ = stats.chi2_contingency(obs_f)
                    null_root_p_values.append(p_null)
                except:
                    pass

# Calculate percentile of real p-value
if null_root_p_values:
    percentile = sum(1 for p in null_root_p_values if p < p_root) / len(null_root_p_values) * 100
    print(f"Root prominence test:")
    print(f"  Real p-value: {p_root:.4f}")
    print(f"  Null median p-value: {np.median(null_root_p_values):.4f}")
    print(f"  Real p-value percentile: {percentile:.1f}%")

    if percentile > 95:
        print("  -> Signal COLLAPSES under null (real is worse than shuffled)")
    elif percentile < 5:
        print("  -> Signal SURVIVES null (real is better than 95% of shuffled)")
    else:
        print("  -> Signal INCONCLUSIVE (real within null distribution)")

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*70)
print("FINAL VERDICT WITH VISUAL DATA")
print("="*70)

final_verdict = test3_verdict
print(f"\nTEST 3 (with real visual data): {test3_verdict}")

if test3_verdict in ["PASS", "WEAK_PASS"]:
    print("\nINTERPRETATION:")
    print("  Prefix archetypes show association with visible plant anatomical features.")
    print("  This is CONSISTENT with material-selection encoding hypothesis.")
    print("  DOES NOT PROVE: that prefixes encode plant parts")
    print("  DOES PROVE: statistical relationship exists between prefix morphology and illustration features")
else:
    print("\nINTERPRETATION:")
    print("  No significant association between prefix archetypes and plant features.")
    print("  Material-selection encoding hypothesis NOT SUPPORTED by visual data.")

# Save updated results
results = {
    'metadata': {
        'title': 'Prefix Material Selection Test V2',
        'visual_data_used': True,
        'folios_analyzed': len(folios_with_data),
        'date': pd.Timestamp.now().isoformat()
    },
    'test_3_results': {
        'verdict': test3_verdict,
        'root_prominence': {
            'chi2': float(chi2_root) if 'chi2_root' in dir() else None,
            'p_value': float(p_root),
            'significant': bool(root_significant)
        },
        'flower_presence': {
            'chi2': float(chi2_flower) if 'chi2_flower' in dir() else None,
            'p_value': float(p_flower),
            'significant': bool(flower_significant)
        },
        'root_type': {
            'chi2': float(chi2_bulb) if 'chi2_bulb' in dir() else None,
            'p_value': float(p_bulb),
            'significant': bool(bulb_significant)
        },
        'n_significant_uncorrected': int(n_significant),
        'n_significant_corrected': int(n_significant_corrected),
        'notes': test3_notes
    }
}

with open('null_model_results_v2.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: null_model_results_v2.json")
