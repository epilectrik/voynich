"""
BF-PFX-Omega: Brute-Force Exhaustive Annotation-Agnostic Robustness Test

PURPOSE: Determine if prefix-visual correlation is genuinely anchored to visual
morphology OR can be reproduced by any sufficiently coarse partition.

PRE-REGISTERED DECISION RULES:
- SUPPORT survives ONLY IF <10% of partitions show significance AND significant
  partitions cluster on structurally similar visual distinctions
- SUPPORT FAILS if significance appears uniformly or survives random groupings
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict, Counter
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# LOAD DATA
# ============================================================================
print("="*70)
print("BF-PFX-OMEGA: Exhaustive Partition Robustness Test")
print("="*70)

# Load visual coding
with open('blinded_visual_coding.json', 'r') as f:
    visual_data = json.load(f)

# Load corpus
corpus_data = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    header = next(f)  # Skip header
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            # Remove quotes from values
            token = parts[0].strip('"')
            folio = parts[2].strip('"')
            corpus_data.append({
                'folio': folio,
                'token': token
            })

# Extract visual features per folio
folio_features = {}
for folio_id, folio_data in visual_data['folios'].items():
    features = {}
    for feat_name, feat_data in folio_data['visual_features'].items():
        val = feat_data.get('value', 'UNDETERMINED')
        if val and val != 'UNDETERMINED':
            features[feat_name] = val
    folio_features[folio_id] = features

print(f"Visual-coded folios: {len(folio_features)}")

# ============================================================================
# BUILD PREFIX ARCHETYPE MAP (frozen from previous analysis)
# ============================================================================
# Using frozen archetypes from TEST 1
archetype_members = {
    0: ['yk', 'ar', 'sh', 'qe', 'ch', 'or', 'ot', 'ok', 'ol', 'al'],
    1: ['cha', 'dai', 'sho', 'cho'],
    2: ['ts', 'cp', 'cf', 'po', 'fc', 'op', 'of'],
    3: ['sha', 'ota', 'oko', 'oke', 'ara', 'ote'],
    4: ['she', 'qok', 'che']
}

prefix_to_archetype = {}
for arch, members in archetype_members.items():
    for prefix in members:
        prefix_to_archetype[prefix] = arch

# Build folio -> prefix counts
folio_prefix_counts = defaultdict(lambda: defaultdict(int))
for record in corpus_data:
    folio = record['folio']
    token = record['token']
    if folio in folio_features and token:
        # Extract prefix (first 2-3 chars that match known prefixes)
        for prefix in prefix_to_archetype:
            if token.startswith(prefix):
                folio_prefix_counts[folio][prefix] += 1
                break

# Get folios with both visual and prefix data
valid_folios = [f for f in folio_features if f in folio_prefix_counts]
print(f"Folios with both data types: {len(valid_folios)}")

# ============================================================================
# STEP 1: GENERATE ALL PARSIMONIOUS PARTITIONS
# ============================================================================
print("\n" + "="*70)
print("STEP 1: GENERATING PARTITIONS")
print("="*70)

MIN_GROUP_SIZE = 4

def get_feature_values(feature_name):
    """Get all values for a feature across valid folios"""
    values = {}
    for folio in valid_folios:
        if feature_name in folio_features[folio]:
            values[folio] = folio_features[folio][feature_name]
    return values

# Identify categorical features with sufficient variation
all_features = set()
for folio in valid_folios:
    all_features.update(folio_features[folio].keys())

feature_value_counts = {}
for feat in all_features:
    values = get_feature_values(feat)
    if values:
        counts = Counter(values.values())
        # Only keep features with at least 2 values, each with MIN_GROUP_SIZE
        viable_values = [v for v, c in counts.items() if c >= MIN_GROUP_SIZE]
        if len(viable_values) >= 2:
            feature_value_counts[feat] = counts

print(f"Features with viable variation: {len(feature_value_counts)}")

# Generate binary partitions
binary_partitions = []

for feat, counts in feature_value_counts.items():
    values = list(counts.keys())
    # Single value vs rest
    for val in values:
        group_a = [f for f in valid_folios if folio_features[f].get(feat) == val]
        group_b = [f for f in valid_folios if folio_features[f].get(feat) != val and feat in folio_features[f]]
        if len(group_a) >= MIN_GROUP_SIZE and len(group_b) >= MIN_GROUP_SIZE:
            binary_partitions.append({
                'type': 'binary',
                'feature': feat,
                'description': f"{feat}={val} vs rest",
                'groups': [group_a, group_b],
                'group_labels': [f"{val}", "OTHER"]
            })

    # Pairs vs rest (for features with 3+ values)
    if len(values) >= 3:
        for pair in combinations(values, 2):
            group_a = [f for f in valid_folios if folio_features[f].get(feat) in pair]
            group_b = [f for f in valid_folios if folio_features[f].get(feat) not in pair and feat in folio_features[f]]
            if len(group_a) >= MIN_GROUP_SIZE and len(group_b) >= MIN_GROUP_SIZE:
                binary_partitions.append({
                    'type': 'binary',
                    'feature': feat,
                    'description': f"{feat} in {pair} vs rest",
                    'groups': [group_a, group_b],
                    'group_labels': [f"{pair}", "OTHER"]
                })

# Generate ternary partitions
ternary_partitions = []

for feat, counts in feature_value_counts.items():
    values = list(counts.keys())
    if len(values) >= 3:
        for triple in combinations(values, 3):
            groups = []
            labels = []
            valid = True
            for val in triple:
                grp = [f for f in valid_folios if folio_features[f].get(feat) == val]
                if len(grp) < MIN_GROUP_SIZE:
                    valid = False
                    break
                groups.append(grp)
                labels.append(val)
            if valid:
                ternary_partitions.append({
                    'type': 'ternary',
                    'feature': feat,
                    'description': f"{feat} in {triple}",
                    'groups': groups,
                    'group_labels': labels
                })

# Cross-feature binary partitions (feature combinations)
cross_partitions = []
feature_list = list(feature_value_counts.keys())

for i, feat1 in enumerate(feature_list):
    for feat2 in feature_list[i+1:]:
        vals1 = list(feature_value_counts[feat1].keys())
        vals2 = list(feature_value_counts[feat2].keys())

        # Only test one cross per pair (first value of each)
        if len(vals1) >= 2 and len(vals2) >= 2:
            v1, v2 = vals1[0], vals2[0]
            # Intersection vs union complement
            group_a = [f for f in valid_folios
                      if folio_features[f].get(feat1) == v1 and folio_features[f].get(feat2) == v2]
            group_b = [f for f in valid_folios
                      if not (folio_features[f].get(feat1) == v1 and folio_features[f].get(feat2) == v2)
                      and feat1 in folio_features[f] and feat2 in folio_features[f]]
            if len(group_a) >= MIN_GROUP_SIZE and len(group_b) >= MIN_GROUP_SIZE:
                cross_partitions.append({
                    'type': 'cross',
                    'feature': f"{feat1}+{feat2}",
                    'description': f"{feat1}={v1} AND {feat2}={v2} vs rest",
                    'groups': [group_a, group_b],
                    'group_labels': ["MATCH", "OTHER"]
                })

all_partitions = binary_partitions + ternary_partitions + cross_partitions

print(f"Binary partitions: {len(binary_partitions)}")
print(f"Ternary partitions: {len(ternary_partitions)}")
print(f"Cross-feature partitions: {len(cross_partitions)}")
print(f"TOTAL PARTITIONS: {len(all_partitions)}")

# ============================================================================
# STEP 2: EXHAUSTIVE PREFIX TESTING
# ============================================================================
print("\n" + "="*70)
print("STEP 2: EXHAUSTIVE CHI-SQUARE TESTING")
print("="*70)

def get_archetype_distribution(folio_list, arch_count=5):
    """Get archetype token counts for a list of folios"""
    dist = [0] * arch_count
    for folio in folio_list:
        for prefix, count in folio_prefix_counts[folio].items():
            if prefix in prefix_to_archetype:
                arch = prefix_to_archetype[prefix]
                dist[arch] += count
    return dist

def test_partition(partition):
    """Run chi-square test on a partition"""
    groups = partition['groups']

    # Get archetype distributions per group
    distributions = []
    for group in groups:
        dist = get_archetype_distribution(group)
        distributions.append(dist)

    # Build contingency table
    observed = np.array(distributions)

    # Filter zero columns
    col_sums = observed.sum(axis=0)
    nonzero_cols = col_sums > 0
    observed_filtered = observed[:, nonzero_cols]

    # Filter zero rows
    row_sums = observed_filtered.sum(axis=1)
    nonzero_rows = row_sums > 0
    observed_filtered = observed_filtered[nonzero_rows, :]

    if observed_filtered.shape[0] < 2 or observed_filtered.shape[1] < 2:
        return None, 1.0, 0.0

    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed_filtered)
        # Effect size (Cramer's V)
        n = observed_filtered.sum()
        min_dim = min(observed_filtered.shape) - 1
        if min_dim > 0 and n > 0:
            cramers_v = np.sqrt(chi2 / (n * min_dim))
        else:
            cramers_v = 0.0
        return chi2, p_value, cramers_v
    except:
        return None, 1.0, 0.0

# Test all partitions
results = []
for partition in all_partitions:
    chi2, p_val, effect = test_partition(partition)
    results.append({
        'partition': partition,
        'chi2': chi2,
        'p_value': p_val,
        'effect_size': effect,
        'significant_005': p_val < 0.05,
        'significant_001': p_val < 0.01
    })

# Sort by p-value
results.sort(key=lambda x: x['p_value'])

# Count significant
n_sig_005 = sum(1 for r in results if r['significant_005'])
n_sig_001 = sum(1 for r in results if r['significant_001'])
pct_sig_005 = n_sig_005 / len(results) * 100 if results else 0
pct_sig_001 = n_sig_001 / len(results) * 100 if results else 0

print(f"\nTotal partitions tested: {len(results)}")
print(f"Significant at p<0.05: {n_sig_005} ({pct_sig_005:.1f}%)")
print(f"Significant at p<0.01: {n_sig_001} ({pct_sig_001:.1f}%)")

# Show top 10 most significant
print("\nTop 10 most significant partitions:")
for i, r in enumerate(results[:10]):
    p = r['partition']
    print(f"  {i+1}. {p['description']}: p={r['p_value']:.4f}, V={r['effect_size']:.3f}")

# ============================================================================
# STEP 3: NULL CONTROLS
# ============================================================================
print("\n" + "="*70)
print("STEP 3: NULL CONTROLS")
print("="*70)

np.random.seed(42)
N_PERMUTATIONS = 500

# NULL 1: Prefix shuffle - shuffle archetype assignments across folios
print("\nNULL 1: Prefix Shuffle")
null1_sig_counts = []

for perm in range(N_PERMUTATIONS):
    # Shuffle prefix-to-archetype mapping
    shuffled_mapping = dict(zip(
        prefix_to_archetype.keys(),
        np.random.permutation(list(prefix_to_archetype.values()))
    ))

    # Count significant partitions under shuffled prefixes
    sig_count = 0
    for partition in all_partitions[:100]:  # Sample for speed
        groups = partition['groups']
        distributions = []
        for group in groups:
            dist = [0] * 5
            for folio in group:
                for prefix, count in folio_prefix_counts[folio].items():
                    if prefix in shuffled_mapping:
                        arch = shuffled_mapping[prefix]
                        dist[arch] += count
            distributions.append(dist)

        observed = np.array(distributions)
        col_sums = observed.sum(axis=0)
        nonzero_cols = col_sums > 0
        observed_filtered = observed[:, nonzero_cols]
        row_sums = observed_filtered.sum(axis=1)
        nonzero_rows = row_sums > 0
        observed_filtered = observed_filtered[nonzero_rows, :]

        if observed_filtered.shape[0] >= 2 and observed_filtered.shape[1] >= 2:
            try:
                _, p_val, _, _ = stats.chi2_contingency(observed_filtered)
                if p_val < 0.05:
                    sig_count += 1
            except:
                pass

    null1_sig_counts.append(sig_count)

# Real count on same subset
real_sig_count_subset = sum(1 for r in results[:100] if r['significant_005'])
null1_mean = np.mean(null1_sig_counts)
null1_std = np.std(null1_sig_counts)
null1_percentile = np.mean([real_sig_count_subset > x for x in null1_sig_counts]) * 100

print(f"  Real significant (subset): {real_sig_count_subset}")
print(f"  Null mean: {null1_mean:.1f} (+/- {null1_std:.1f})")
print(f"  Percentile: {null1_percentile:.1f}%")
null1_survives = null1_percentile > 95

# NULL 2: Visual feature scramble
print("\nNULL 2: Visual Feature Scramble")
null2_sig_counts = []

for perm in range(N_PERMUTATIONS):
    # Shuffle visual features across folios
    shuffled_features = dict(zip(
        valid_folios,
        np.random.permutation([folio_features[f] for f in valid_folios])
    ))

    sig_count = 0
    for partition in all_partitions[:100]:
        # Rebuild groups with shuffled features
        feat = partition['feature'].split('+')[0]  # Handle cross-features
        if '=' in partition['description']:
            # Binary partition
            target_val = partition['description'].split('=')[1].split(' ')[0]
            group_a = [f for f in valid_folios if shuffled_features[f].get(feat) == target_val]
            group_b = [f for f in valid_folios if shuffled_features[f].get(feat) != target_val and feat in shuffled_features[f]]
        else:
            continue

        if len(group_a) >= MIN_GROUP_SIZE and len(group_b) >= MIN_GROUP_SIZE:
            distributions = [get_archetype_distribution(group_a), get_archetype_distribution(group_b)]
            observed = np.array(distributions)
            col_sums = observed.sum(axis=0)
            nonzero_cols = col_sums > 0
            observed_filtered = observed[:, nonzero_cols]
            row_sums = observed_filtered.sum(axis=1)
            nonzero_rows = row_sums > 0
            observed_filtered = observed_filtered[nonzero_rows, :]

            if observed_filtered.shape[0] >= 2 and observed_filtered.shape[1] >= 2:
                try:
                    _, p_val, _, _ = stats.chi2_contingency(observed_filtered)
                    if p_val < 0.05:
                        sig_count += 1
                except:
                    pass

    null2_sig_counts.append(sig_count)

null2_mean = np.mean(null2_sig_counts)
null2_std = np.std(null2_sig_counts)
null2_percentile = np.mean([real_sig_count_subset > x for x in null2_sig_counts]) * 100

print(f"  Real significant (subset): {real_sig_count_subset}")
print(f"  Null mean: {null2_mean:.1f} (+/- {null2_std:.1f})")
print(f"  Percentile: {null2_percentile:.1f}%")
null2_survives = null2_percentile > 95

# NULL 3: Synthetic random partitions
print("\nNULL 3: Synthetic Random Partitions")
null3_sig_counts = []

for perm in range(N_PERMUTATIONS):
    sig_count = 0
    # Generate random binary partitions matching real sizes
    for partition in all_partitions[:100]:
        if partition['type'] != 'binary':
            continue
        size_a = len(partition['groups'][0])
        size_b = len(partition['groups'][1])

        # Random split
        shuffled = np.random.permutation(valid_folios)
        group_a = list(shuffled[:size_a])
        group_b = list(shuffled[size_a:size_a+size_b])

        if len(group_a) >= MIN_GROUP_SIZE and len(group_b) >= MIN_GROUP_SIZE:
            distributions = [get_archetype_distribution(group_a), get_archetype_distribution(group_b)]
            observed = np.array(distributions)
            col_sums = observed.sum(axis=0)
            nonzero_cols = col_sums > 0
            observed_filtered = observed[:, nonzero_cols]
            row_sums = observed_filtered.sum(axis=1)
            nonzero_rows = row_sums > 0
            observed_filtered = observed_filtered[nonzero_rows, :]

            if observed_filtered.shape[0] >= 2 and observed_filtered.shape[1] >= 2:
                try:
                    _, p_val, _, _ = stats.chi2_contingency(observed_filtered)
                    if p_val < 0.05:
                        sig_count += 1
                except:
                    pass

    null3_sig_counts.append(sig_count)

null3_mean = np.mean(null3_sig_counts)
null3_std = np.std(null3_sig_counts)
null3_percentile = np.mean([real_sig_count_subset > x for x in null3_sig_counts]) * 100

print(f"  Real significant (subset): {real_sig_count_subset}")
print(f"  Null mean: {null3_mean:.1f} (+/- {null3_std:.1f})")
print(f"  Percentile: {null3_percentile:.1f}%")
null3_survives = null3_percentile > 95

# ============================================================================
# STEP 4: CLUSTER ANALYSIS OF SIGNIFICANT PARTITIONS
# ============================================================================
print("\n" + "="*70)
print("STEP 4: SIGNIFICANT PARTITION CLUSTERING")
print("="*70)

sig_partitions = [r for r in results if r['significant_005']]
if sig_partitions:
    # Group by feature
    feature_groups = defaultdict(list)
    for r in sig_partitions:
        feat = r['partition']['feature'].split('+')[0]
        feature_groups[feat].append(r)

    print(f"\nSignificant partitions by feature:")
    for feat, items in sorted(feature_groups.items(), key=lambda x: -len(x[1])):
        print(f"  {feat}: {len(items)} partitions")

    # Check clustering
    n_features_with_sig = len(feature_groups)
    total_features = len(feature_value_counts)
    clustering_ratio = n_features_with_sig / total_features if total_features > 0 else 1.0

    print(f"\nClustering analysis:")
    print(f"  Features with significant partitions: {n_features_with_sig}/{total_features}")
    print(f"  Clustering ratio: {clustering_ratio:.2f}")
    print(f"  Clustered = ratio < 0.3 (significance confined to few features)")

    # Root-salience clustering check
    root_features = ['root_prominence', 'root_type', 'root_present', 'root_color_distinct']
    root_sig_count = sum(1 for f in feature_groups if any(rf in f for rf in root_features))
    root_clustering = root_sig_count / n_features_with_sig if n_features_with_sig > 0 else 0

    print(f"\nRoot-related clustering:")
    print(f"  Root-related features in significant set: {root_sig_count}/{n_features_with_sig}")
    print(f"  Root clustering ratio: {root_clustering:.2f}")
else:
    print("No significant partitions found")
    clustering_ratio = 1.0
    root_clustering = 0.0

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n" + "="*70)
print("FINAL VERDICT (PRE-REGISTERED RULES)")
print("="*70)

# Decision rule 1: <10% of partitions significant
rule1_pass = pct_sig_005 < 10
print(f"\nRULE 1: <10% partitions significant")
print(f"  Result: {pct_sig_005:.1f}% significant")
print(f"  PASS: {rule1_pass}")

# Decision rule 2: Significant partitions cluster on similar features
rule2_pass = clustering_ratio < 0.3
print(f"\nRULE 2: Significant partitions cluster (ratio < 0.3)")
print(f"  Result: {clustering_ratio:.2f}")
print(f"  PASS: {rule2_pass}")

# Decision rule 3: Signal destroyed by nulls
nulls_destroyed = not (null1_survives and null2_survives and null3_survives)
nulls_survive_count = sum([null1_survives, null2_survives, null3_survives])
print(f"\nRULE 3: Signal survives all null controls")
print(f"  Null 1 (prefix shuffle): {'SURVIVES' if null1_survives else 'COLLAPSES'}")
print(f"  Null 2 (visual scramble): {'SURVIVES' if null2_survives else 'COLLAPSES'}")
print(f"  Null 3 (random partition): {'SURVIVES' if null3_survives else 'COLLAPSES'}")
print(f"  Nulls survived: {nulls_survive_count}/3")

# Final verdict
print("\n" + "="*70)
if rule1_pass and rule2_pass and nulls_survive_count >= 2:
    verdict = "SUPPORT_SURVIVES"
    interpretation = "Prefix-visual correlation is genuinely anchored to specific visual dimensions"
elif pct_sig_005 > 20 or (not rule2_pass and nulls_survive_count < 2):
    verdict = "SUPPORT_FAILS"
    interpretation = "Prefix-visual correlation is a general low-level indexing artifact"
else:
    verdict = "INCONCLUSIVE"
    interpretation = "Mixed evidence - partial anchoring possible"

print(f"VERDICT: {verdict}")
print(f"INTERPRETATION: {interpretation}")
print("="*70)

# ============================================================================
# SAVE RESULTS
# ============================================================================
output = {
    'metadata': {
        'test': 'BF-PFX-OMEGA',
        'purpose': 'Exhaustive annotation-agnostic robustness test',
        'total_partitions': len(all_partitions),
        'valid_folios': len(valid_folios)
    },
    'partition_counts': {
        'binary': len(binary_partitions),
        'ternary': len(ternary_partitions),
        'cross_feature': len(cross_partitions)
    },
    'significance_rates': {
        'p_005': float(pct_sig_005),
        'p_001': float(pct_sig_001),
        'n_significant_005': n_sig_005,
        'n_significant_001': n_sig_001
    },
    'null_controls': {
        'null1_prefix_shuffle': {
            'real_count': int(real_sig_count_subset),
            'null_mean': float(null1_mean),
            'null_std': float(null1_std),
            'percentile': float(null1_percentile),
            'survives': bool(null1_survives)
        },
        'null2_visual_scramble': {
            'real_count': int(real_sig_count_subset),
            'null_mean': float(null2_mean),
            'null_std': float(null2_std),
            'percentile': float(null2_percentile),
            'survives': bool(null2_survives)
        },
        'null3_random_partition': {
            'real_count': int(real_sig_count_subset),
            'null_mean': float(null3_mean),
            'null_std': float(null3_std),
            'percentile': float(null3_percentile),
            'survives': bool(null3_survives)
        }
    },
    'clustering': {
        'features_with_significance': int(len(feature_groups)) if sig_partitions else 0,
        'total_features': len(feature_value_counts),
        'clustering_ratio': float(clustering_ratio),
        'root_clustering_ratio': float(root_clustering) if sig_partitions else 0.0
    },
    'decision_rules': {
        'rule1_lt_10pct': bool(rule1_pass),
        'rule2_clustered': bool(rule2_pass),
        'rule3_nulls_survived': int(nulls_survive_count)
    },
    'verdict': verdict,
    'interpretation': interpretation,
    'top_10_partitions': [
        {
            'description': r['partition']['description'],
            'p_value': float(r['p_value']) if r['p_value'] else None,
            'effect_size': float(r['effect_size']) if r['effect_size'] else None
        }
        for r in results[:10]
    ]
}

with open('bf_pfx_omega_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to: bf_pfx_omega_results.json")
