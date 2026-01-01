#!/usr/bin/env python3
"""
Data Recovery Phase, Task 6: Cluster Analysis (EXPLORATORY ONLY)

Clusters folios by visual and text features separately,
then compares cluster alignment using Adjusted Rand Index.

CRITICAL: Results CANNOT justify enum claims without corroboration
from direct correlations (Tasks 4-5).
"""

import json
import random
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics

# =============================================================================
# CRITICAL WARNING
# =============================================================================

EXPLORATORY_WARNING = """
================================================================================
WARNING: EXPLORATORY ANALYSIS ONLY
================================================================================

Cluster analysis results CANNOT be used to justify enum recovery claims.

Cluster alignment can appear impressive even when driven by:
- Entry length distributions (nuisance structure)
- Frequency effects
- Random chance with small samples

REQUIRED for any claim based on cluster alignment:
1. Direct correlation support from Task 4/5 tests
2. Effect size and null model confirmation
3. Propagation across multiple entries

If cluster alignment is found but NO direct correlation support exists:
Report: "Cluster alignment observed but not corroborated by direct
correlation testing. This may reflect nuisance structure rather than
semantic organization."
================================================================================
"""


# =============================================================================
# CLUSTERING ALGORITHMS
# =============================================================================

def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """Calculate Euclidean distance between two vectors."""
    if len(v1) != len(v2):
        return float('inf')
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def kmeans_cluster(data: List[List[float]], n_clusters: int,
                  max_iterations: int = 100) -> Tuple[List[int], float]:
    """
    K-means clustering implementation.

    Returns cluster assignments and silhouette score.
    """
    if not data or len(data) < n_clusters:
        return [], 0.0

    n_points = len(data)
    n_dims = len(data[0])

    # Initialize centroids randomly
    random.seed(42)  # Reproducibility
    centroid_indices = random.sample(range(n_points), n_clusters)
    centroids = [data[i].copy() for i in centroid_indices]

    assignments = [0] * n_points

    for _ in range(max_iterations):
        # Assign points to nearest centroid
        new_assignments = []
        for point in data:
            distances = [euclidean_distance(point, c) for c in centroids]
            new_assignments.append(distances.index(min(distances)))

        # Check convergence
        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Update centroids
        for k in range(n_clusters):
            cluster_points = [data[i] for i in range(n_points) if assignments[i] == k]
            if cluster_points:
                centroids[k] = [
                    sum(p[d] for p in cluster_points) / len(cluster_points)
                    for d in range(n_dims)
                ]

    # Calculate silhouette score
    silhouette = calculate_silhouette(data, assignments, n_clusters)

    return assignments, silhouette


def calculate_silhouette(data: List[List[float]], assignments: List[int],
                        n_clusters: int) -> float:
    """Calculate silhouette score for clustering quality."""
    n = len(data)
    if n < 2 or n_clusters < 2:
        return 0.0

    silhouettes = []

    for i in range(n):
        cluster_i = assignments[i]

        # a(i): mean distance to same cluster
        same_cluster = [j for j in range(n) if assignments[j] == cluster_i and j != i]
        if not same_cluster:
            a_i = 0
        else:
            a_i = sum(euclidean_distance(data[i], data[j]) for j in same_cluster) / len(same_cluster)

        # b(i): min mean distance to other clusters
        b_i_candidates = []
        for k in range(n_clusters):
            if k == cluster_i:
                continue
            other_cluster = [j for j in range(n) if assignments[j] == k]
            if other_cluster:
                mean_dist = sum(euclidean_distance(data[i], data[j]) for j in other_cluster) / len(other_cluster)
                b_i_candidates.append(mean_dist)

        b_i = min(b_i_candidates) if b_i_candidates else 0

        # Silhouette
        if max(a_i, b_i) > 0:
            s_i = (b_i - a_i) / max(a_i, b_i)
        else:
            s_i = 0

        silhouettes.append(s_i)

    return sum(silhouettes) / len(silhouettes) if silhouettes else 0


# =============================================================================
# ADJUSTED RAND INDEX
# =============================================================================

def adjusted_rand_index(labels1: List[int], labels2: List[int]) -> float:
    """
    Calculate Adjusted Rand Index between two clusterings.

    ARI = 1.0: Perfect agreement
    ARI = 0.0: Random agreement
    ARI < 0: Less than random
    """
    if len(labels1) != len(labels2):
        return 0.0

    n = len(labels1)
    if n < 2:
        return 0.0

    # Build contingency table
    contingency = defaultdict(lambda: defaultdict(int))
    for l1, l2 in zip(labels1, labels2):
        contingency[l1][l2] += 1

    # Calculate sum of combinations
    def comb2(k):
        return k * (k - 1) / 2

    sum_comb = sum(comb2(v) for row in contingency.values() for v in row.values())

    # Row and column sums
    row_sums = {k: sum(v.values()) for k, v in contingency.items()}
    col_sums = defaultdict(int)
    for row in contingency.values():
        for k, v in row.items():
            col_sums[k] += v

    sum_row_comb = sum(comb2(s) for s in row_sums.values())
    sum_col_comb = sum(comb2(s) for s in col_sums.values())

    # Expected and max
    n_comb = comb2(n)
    expected = sum_row_comb * sum_col_comb / n_comb if n_comb > 0 else 0
    max_val = (sum_row_comb + sum_col_comb) / 2

    # ARI
    if max_val - expected == 0:
        return 1.0 if sum_comb == expected else 0.0

    ari = (sum_comb - expected) / (max_val - expected)
    return round(ari, 4)


# =============================================================================
# FEATURE ENCODING
# =============================================================================

def encode_visual_features(visual_data: Dict, feature_list: List[str]) -> Dict[str, List[float]]:
    """
    Encode categorical visual features as numeric vectors.

    Uses one-hot encoding for categorical features.
    """
    # Get all possible values for each feature
    value_sets = {f: set() for f in feature_list}
    for folio_data in visual_data.values():
        for f in feature_list:
            val = folio_data.get(f)
            if val and val != 'UNDETERMINED':
                value_sets[f].add(val)

    # Create value-to-index mapping
    value_maps = {}
    for f in feature_list:
        value_maps[f] = {v: i for i, v in enumerate(sorted(value_sets[f]))}

    # Encode each folio
    encoded = {}
    for folio_id, folio_data in visual_data.items():
        vector = []
        for f in feature_list:
            val = folio_data.get(f)
            n_values = len(value_maps[f])
            if n_values == 0:
                continue
            one_hot = [0.0] * n_values
            if val in value_maps[f]:
                one_hot[value_maps[f][val]] = 1.0
            vector.extend(one_hot)
        encoded[folio_id] = vector

    return encoded


def encode_text_features(text_data: Dict, feature_list: List[str]) -> Dict[str, List[float]]:
    """
    Encode text features as numeric vectors.

    Continuous features normalized, categorical one-hot encoded.
    """
    pilot_folios = text_data.get('pilot_folios', {})

    # Get ranges for continuous features
    continuous = ['word_count', 'unique_word_count', 'vocabulary_richness',
                  'prefix_diversity', 'heading_length']

    ranges = {}
    for f in continuous:
        if f in feature_list:
            vals = [pf.get(f, 0) for pf in pilot_folios.values() if pf.get(f) is not None]
            if vals:
                ranges[f] = (min(vals), max(vals))

    # Encode
    encoded = {}
    for folio_id, folio_data in pilot_folios.items():
        vector = []
        for f in feature_list:
            if f in continuous:
                val = folio_data.get(f, 0)
                min_v, max_v = ranges.get(f, (0, 1))
                if max_v > min_v:
                    normalized = (val - min_v) / (max_v - min_v)
                else:
                    normalized = 0.5
                vector.append(normalized)
            else:
                # Categorical - simplified encoding
                val = folio_data.get(f, '')
                vector.append(hash(val) % 1000 / 1000.0)  # Simple hash encoding
        encoded[folio_id] = vector

    return encoded


# =============================================================================
# CLUSTER COMPARISON
# =============================================================================

def cluster_by_visual(visual_data: Dict, n_clusters_list: List[int] = [3, 4, 5]) -> Dict:
    """
    Cluster folios by visual features alone.

    Excludes UNDETERMINED values.
    """
    # Features to use (exclude compound features)
    feature_list = [
        'root_present', 'root_type', 'stem_count', 'stem_type',
        'leaf_present', 'leaf_shape', 'flower_present', 'flower_shape',
        'plant_symmetry'
    ]

    encoded = encode_visual_features(visual_data, feature_list)

    if not encoded:
        return {'error': 'No valid visual data to cluster'}

    folio_ids = list(encoded.keys())
    data = [encoded[f] for f in folio_ids]

    results = {}
    for k in n_clusters_list:
        if k >= len(data):
            continue
        assignments, silhouette = kmeans_cluster(data, k)
        results[f'k={k}'] = {
            'assignments': dict(zip(folio_ids, assignments)),
            'silhouette': round(silhouette, 4)
        }

    return {
        'method': 'visual_clustering',
        'features_used': feature_list,
        'n_folios': len(folio_ids),
        'results': results
    }


def cluster_by_text(text_data: Dict, n_clusters_list: List[int] = [3, 4, 5]) -> Dict:
    """
    Cluster folios by text features alone.
    """
    feature_list = ['word_count', 'vocabulary_richness', 'prefix_diversity']

    encoded = encode_text_features(text_data, feature_list)

    if not encoded:
        return {'error': 'No valid text data to cluster'}

    folio_ids = list(encoded.keys())
    data = [encoded[f] for f in folio_ids]

    results = {}
    for k in n_clusters_list:
        if k >= len(data):
            continue
        assignments, silhouette = kmeans_cluster(data, k)
        results[f'k={k}'] = {
            'assignments': dict(zip(folio_ids, assignments)),
            'silhouette': round(silhouette, 4)
        }

    return {
        'method': 'text_clustering',
        'features_used': feature_list,
        'n_folios': len(folio_ids),
        'results': results
    }


def compare_clusterings(visual_clusters: Dict, text_clusters: Dict) -> Dict:
    """
    Compare visual and text clusterings using Adjusted Rand Index.

    HIGH ARI suggests visual similarity predicts text similarity.
    """
    comparisons = []

    v_results = visual_clusters.get('results', {})
    t_results = text_clusters.get('results', {})

    for v_key, v_data in v_results.items():
        for t_key, t_data in t_results.items():
            v_assign = v_data.get('assignments', {})
            t_assign = t_data.get('assignments', {})

            # Get common folios
            common = set(v_assign.keys()) & set(t_assign.keys())
            if len(common) < 5:
                continue

            common_list = sorted(common)
            v_labels = [v_assign[f] for f in common_list]
            t_labels = [t_assign[f] for f in common_list]

            ari = adjusted_rand_index(v_labels, t_labels)

            comparisons.append({
                'visual_k': v_key,
                'text_k': t_key,
                'n_common': len(common),
                'ari': ari,
                'interpretation': interpret_ari(ari)
            })

    return {
        'comparisons': comparisons,
        'best_alignment': max(comparisons, key=lambda x: x['ari']) if comparisons else None
    }


def interpret_ari(ari: float) -> str:
    """Interpret Adjusted Rand Index."""
    if ari >= 0.8:
        return "STRONG_ALIGNMENT"
    elif ari >= 0.5:
        return "MODERATE_ALIGNMENT"
    elif ari >= 0.2:
        return "WEAK_ALIGNMENT"
    elif ari >= 0:
        return "RANDOM_LEVEL"
    else:
        return "NEGATIVE_ALIGNMENT"


# =============================================================================
# INTERPRETATION GUARDRAIL
# =============================================================================

def interpret_clusters(alignment_results: Dict, correlation_results: Optional[Dict] = None) -> Dict:
    """
    Interpret cluster analysis with strict guardrails.

    Cluster interpretation is ONLY valid if:
    1. Direct correlations from Task 4/5 support the pattern
    2. Alignment is not driven by entry length or frequency alone
    """
    best = alignment_results.get('best_alignment')
    if not best:
        return {
            'interpretation': 'No valid cluster comparison possible',
            'corroborated': False
        }

    ari = best.get('ari', 0)

    # Check if we have correlation support
    has_correlation_support = False
    if correlation_results:
        significant = correlation_results.get('significant_results', {})
        bonferroni_sig = significant.get('bonferroni_significant', [])
        has_correlation_support = len(bonferroni_sig) >= 1

    # Generate interpretation
    if ari >= 0.5 and has_correlation_support:
        interpretation = (
            f"Cluster alignment observed (ARI={ari:.2f}) AND corroborated by "
            "direct correlation testing. Visual and text features show consistent structure."
        )
        status = "CORROBORATED"
    elif ari >= 0.5 and not has_correlation_support:
        interpretation = (
            f"Cluster alignment observed (ARI={ari:.2f}) but NOT corroborated by "
            "direct correlation testing. This may reflect nuisance structure "
            "(e.g., entry length distribution) rather than semantic organization."
        )
        status = "NOT_CORROBORATED"
    elif ari >= 0.2:
        interpretation = (
            f"Weak cluster alignment observed (ARI={ari:.2f}). "
            "Insufficient evidence for structural claims."
        )
        status = "WEAK"
    else:
        interpretation = (
            f"No meaningful cluster alignment (ARI={ari:.2f}). "
            "Visual and text features do not cluster similarly."
        )
        status = "NO_ALIGNMENT"

    return {
        'best_ari': round(ari, 4),
        'correlation_support': has_correlation_support,
        'status': status,
        'interpretation': interpretation,
        'exploratory_warning': "This is exploratory analysis. Do not use to justify enum claims."
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print(EXPLORATORY_WARNING)

    print("=" * 70)
    print("Data Recovery Phase, Task 6: Cluster Analysis")
    print("=" * 70)

    print("\nCluster analysis framework ready.")
    print("Awaiting visual data to run clustering.")

    print("\nCapabilities:")
    print("  - K-means clustering on visual features")
    print("  - K-means clustering on text features")
    print("  - Adjusted Rand Index comparison")
    print("  - Interpretation with correlation guardrail")

    # Save configuration
    config = {
        'metadata': {
            'title': 'Cluster Analysis Configuration',
            'phase': 'Data Recovery Phase, Task 6',
            'date': datetime.now().isoformat()
        },
        'warning': 'EXPLORATORY ONLY - cannot justify enum claims without direct correlation support',
        'n_clusters_to_test': [3, 4, 5],
        'visual_features_used': [
            'root_present', 'root_type', 'stem_count', 'stem_type',
            'leaf_present', 'leaf_shape', 'flower_present', 'flower_shape',
            'plant_symmetry'
        ],
        'text_features_used': ['word_count', 'vocabulary_richness', 'prefix_diversity'],
        'ari_thresholds': {
            'strong': 0.8,
            'moderate': 0.5,
            'weak': 0.2
        },
        'status': 'READY - awaiting visual data'
    }

    with open('cluster_analysis_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved configuration to: cluster_analysis_config.json")


if __name__ == '__main__':
    main()
