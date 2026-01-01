#!/usr/bin/env python3
"""
Phase 18, Task 3: Visual-Text Correlation Analysis Framework

Statistical tests for analyzing correlation between visual features (from manual
coding) and text features (from pilot_folio_text_features.json).

This script is READY TO RUN once visual coding data is provided.

Tests included:
- Chi-square tests for categorical associations
- Fisher's exact test for small cell counts
- Cramer's V for effect size
- Cluster analysis with adjusted Rand index
- Null model comparison (permutation tests)

Pre-registered success criteria:
- At least 3 correlations at p < 0.01 (Bonferroni-corrected)
- At least 1 correlation survives null model (>99th percentile)
- Correlations must be interpretable
"""

import json
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
import warnings

warnings.filterwarnings('ignore')

# Optional sklearn - fallback to scipy if not available
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Note: sklearn not available. Using scipy clustering instead.")

# =============================================================================
# DATA LOADING
# =============================================================================

def load_text_features() -> Dict:
    """Load pilot folio text features."""
    with open('pilot_folio_text_features.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def load_visual_features(filepath: str = 'visual_coding_data.json') -> Dict:
    """
    Load visual coding data.

    Expected format:
    {
        "folio_id": {
            "root_present": "YES",
            "root_type": "BULBOUS",
            ...
        }
    }
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"WARNING: Visual coding file '{filepath}' not found.")
        print("This framework is ready to run once visual coding is complete.")
        return None


# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def chi_square_test(visual_values: List[str], text_values: List[str]) -> Dict:
    """
    Perform chi-square test for association between categorical features.

    Returns:
        chi2: Chi-square statistic
        p_value: P-value
        cramers_v: Effect size (Cramer's V)
        dof: Degrees of freedom
        contingency: Contingency table
    """
    # Build contingency table
    visual_cats = sorted(set(visual_values))
    text_cats = sorted(set(text_values))

    contingency = np.zeros((len(visual_cats), len(text_cats)))

    for v, t in zip(visual_values, text_values):
        vi = visual_cats.index(v)
        ti = text_cats.index(t)
        contingency[vi, ti] += 1

    # Check for validity
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return {
            'chi2': np.nan,
            'p_value': 1.0,
            'cramers_v': 0.0,
            'dof': 0,
            'valid': False,
            'reason': 'Insufficient categories'
        }

    # Chi-square test
    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        # Check for small expected counts
        small_expected = np.sum(expected < 5)

        # Cramer's V (effect size)
        n = contingency.sum()
        min_dim = min(contingency.shape) - 1
        if min_dim > 0 and n > 0:
            cramers_v = np.sqrt(chi2 / (n * min_dim))
        else:
            cramers_v = 0.0

        return {
            'chi2': round(chi2, 4),
            'p_value': p_value,
            'cramers_v': round(cramers_v, 4),
            'dof': dof,
            'n': int(n),
            'small_expected_cells': int(small_expected),
            'use_fisher': small_expected > len(expected.flatten()) * 0.2,
            'valid': True,
            'contingency': contingency.tolist(),
            'visual_categories': visual_cats,
            'text_categories': text_cats
        }

    except Exception as e:
        return {
            'chi2': np.nan,
            'p_value': 1.0,
            'cramers_v': 0.0,
            'dof': 0,
            'valid': False,
            'reason': str(e)
        }


def fisher_exact_test(visual_values: List[str], text_values: List[str]) -> Dict:
    """
    Fisher's exact test for 2x2 contingency tables.
    For larger tables, uses chi-square with warning.
    """
    visual_cats = sorted(set(visual_values))
    text_cats = sorted(set(text_values))

    # Build contingency table
    contingency = np.zeros((len(visual_cats), len(text_cats)))
    for v, t in zip(visual_values, text_values):
        vi = visual_cats.index(v)
        ti = text_cats.index(t)
        contingency[vi, ti] += 1

    # Fisher's exact only for 2x2
    if contingency.shape == (2, 2):
        try:
            odds_ratio, p_value = stats.fisher_exact(contingency.astype(int))
            return {
                'odds_ratio': round(odds_ratio, 4),
                'p_value': p_value,
                'valid': True,
                'test': 'fisher_exact'
            }
        except Exception as e:
            return {'valid': False, 'reason': str(e)}
    else:
        # Fall back to chi-square
        result = chi_square_test(visual_values, text_values)
        result['test'] = 'chi_square_fallback'
        return result


def compute_correlation(numeric_visual: List[float], numeric_text: List[float]) -> Dict:
    """Compute Pearson/Spearman correlation for numeric features."""
    if len(numeric_visual) < 3:
        return {'valid': False, 'reason': 'Too few data points'}

    try:
        pearson_r, pearson_p = stats.pearsonr(numeric_visual, numeric_text)
        spearman_r, spearman_p = stats.spearmanr(numeric_visual, numeric_text)

        return {
            'pearson_r': round(pearson_r, 4),
            'pearson_p': pearson_p,
            'spearman_r': round(spearman_r, 4),
            'spearman_p': spearman_p,
            'valid': True
        }
    except Exception as e:
        return {'valid': False, 'reason': str(e)}


# =============================================================================
# CLUSTER ANALYSIS
# =============================================================================

def encode_categorical(data: Dict, features: List[str]) -> np.ndarray:
    """Encode categorical features as numeric for clustering."""
    folios = list(data.keys())
    n_folios = len(folios)

    # Build encoding
    encodings = []
    for feat in features:
        values = [data[f].get(feat, 'UNKNOWN') for f in folios]
        unique_vals = sorted(set(values))
        val_to_idx = {v: i for i, v in enumerate(unique_vals)}
        encoded = [val_to_idx[v] for v in values]
        encodings.append(encoded)

    return np.array(encodings).T  # Shape: (n_folios, n_features)


def cluster_folios(data: Dict, features: List[str], n_clusters: List[int] = [3, 4, 5]) -> Dict:
    """
    Cluster folios by given features.

    Uses sklearn KMeans if available, otherwise scipy hierarchical clustering.
    Returns cluster assignments for each k value.
    """
    X = encode_categorical(data, features)
    folios = list(data.keys())

    results = {}
    for k in n_clusters:
        if k >= len(folios):
            continue

        try:
            if SKLEARN_AVAILABLE:
                # Use KMeans
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(X)
                inertia = round(kmeans.inertia_, 4)
            else:
                # Use scipy hierarchical clustering
                Z = linkage(X, method='ward')
                labels = fcluster(Z, k, criterion='maxclust') - 1  # 0-indexed
                inertia = 0.0  # Not available for hierarchical

            # Compute cluster composition
            clusters = defaultdict(list)
            for i, label in enumerate(labels):
                clusters[int(label)].append(folios[i])

            results[k] = {
                'labels': {folios[i]: int(labels[i]) for i in range(len(folios))},
                'clusters': dict(clusters),
                'inertia': inertia
            }
        except Exception as e:
            results[k] = {'error': str(e)}

    return results


def compute_ari_manual(labels1: List[int], labels2: List[int]) -> float:
    """Compute Adjusted Rand Index manually (no sklearn required)."""
    from scipy.special import comb

    n = len(labels1)
    if n < 2:
        return 0.0

    # Build contingency table
    max_l1 = max(labels1) + 1
    max_l2 = max(labels2) + 1
    contingency = np.zeros((max_l1, max_l2), dtype=int)

    for l1, l2 in zip(labels1, labels2):
        contingency[l1, l2] += 1

    # Sum of combinations
    sum_comb_c = sum(comb(n_ij, 2) for row in contingency for n_ij in row)
    sum_comb_a = sum(comb(contingency[i, :].sum(), 2) for i in range(max_l1))
    sum_comb_b = sum(comb(contingency[:, j].sum(), 2) for j in range(max_l2))

    total_comb = comb(n, 2)

    # ARI formula
    expected = sum_comb_a * sum_comb_b / total_comb if total_comb > 0 else 0
    max_index = (sum_comb_a + sum_comb_b) / 2
    denominator = max_index - expected

    if denominator == 0:
        return 0.0

    ari = (sum_comb_c - expected) / denominator
    return ari


def compare_clusterings(labels1: Dict[str, int], labels2: Dict[str, int]) -> float:
    """
    Compare two clustering solutions using Adjusted Rand Index.

    ARI = 1.0: Perfect agreement
    ARI = 0.0: Random clustering
    ARI < 0: Worse than random
    """
    common_folios = set(labels1.keys()) & set(labels2.keys())
    if len(common_folios) < 3:
        return np.nan

    l1 = [labels1[f] for f in sorted(common_folios)]
    l2 = [labels2[f] for f in sorted(common_folios)]

    if SKLEARN_AVAILABLE:
        return round(adjusted_rand_score(l1, l2), 4)
    else:
        return round(compute_ari_manual(l1, l2), 4)


# =============================================================================
# NULL MODEL COMPARISON
# =============================================================================

def null_model_test(visual_values: List[str], text_values: List[str],
                    test_func, n_shuffles: int = 1000) -> Dict:
    """
    Permutation test to check if observed correlation exceeds null expectation.

    Shuffles visual feature assignments and recomputes test statistic.
    Reports percentile of real correlation in null distribution.
    """
    # Get real test result
    real_result = test_func(visual_values, text_values)

    if not real_result.get('valid', False):
        return {'valid': False, 'reason': 'Real test invalid'}

    # Get test statistic (chi2 or cramers_v)
    if 'chi2' in real_result:
        real_stat = real_result['chi2']
        stat_name = 'chi2'
    elif 'cramers_v' in real_result:
        real_stat = real_result['cramers_v']
        stat_name = 'cramers_v'
    else:
        return {'valid': False, 'reason': 'No suitable statistic'}

    if np.isnan(real_stat):
        return {'valid': False, 'reason': 'Real statistic is NaN'}

    # Generate null distribution
    null_stats = []
    visual_array = np.array(visual_values)

    for _ in range(n_shuffles):
        shuffled = np.random.permutation(visual_array)
        null_result = test_func(shuffled.tolist(), text_values)

        if null_result.get('valid', False) and stat_name in null_result:
            null_stat = null_result[stat_name]
            if not np.isnan(null_stat):
                null_stats.append(null_stat)

    if len(null_stats) < n_shuffles * 0.5:
        return {'valid': False, 'reason': 'Too many null tests failed'}

    # Compute percentile
    null_stats = np.array(null_stats)
    percentile = np.mean(real_stat > null_stats) * 100

    return {
        'real_statistic': round(real_stat, 4),
        'statistic_name': stat_name,
        'null_mean': round(np.mean(null_stats), 4),
        'null_std': round(np.std(null_stats), 4),
        'null_max': round(np.max(null_stats), 4),
        'percentile': round(percentile, 2),
        'exceeds_99th': percentile > 99,
        'exceeds_95th': percentile > 95,
        'n_shuffles': len(null_stats),
        'valid': True
    }


# =============================================================================
# MAIN ANALYSIS FRAMEWORK
# =============================================================================

# Visual features to test
VISUAL_FEATURES = [
    'root_present', 'root_type', 'root_prominence',
    'stem_count', 'stem_type', 'stem_thickness',
    'leaf_present', 'leaf_count_category', 'leaf_shape', 'leaf_arrangement',
    'flower_present', 'flower_count', 'flower_position', 'flower_shape',
    'plant_count', 'container_present', 'plant_symmetry', 'overall_complexity',
    'identifiable_impression', 'drawing_completeness'
]

# Text features to test (categorical)
TEXT_FEATURES_CATEGORICAL = [
    'part1_dominant_prefix', 'part2_dominant_prefix', 'part3_dominant_prefix',
    'heading_prefix', 'heading_suffix',
    'heading_in_b'
]

# Text features to test (numeric - for binning)
TEXT_FEATURES_NUMERIC = [
    'word_count', 'unique_word_count', 'prefix_diversity',
    'part1_word_count', 'part2_word_count', 'part3_word_count',
    'heading_length'
]


def bin_numeric_feature(values: List[float], n_bins: int = 3) -> List[str]:
    """Bin numeric values into categories for chi-square test."""
    arr = np.array(values)
    percentiles = [100 * i / n_bins for i in range(1, n_bins)]
    thresholds = np.percentile(arr, percentiles)

    labels = []
    for v in values:
        label = 'LOW'
        for i, t in enumerate(thresholds):
            if v > t:
                label = ['MEDIUM', 'HIGH'][min(i, 1)]
        labels.append(label)

    return labels


def run_correlation_analysis(visual_data: Dict, text_data: Dict) -> Dict:
    """
    Run full correlation analysis between visual and text features.

    Returns comprehensive results including all tests and summary.
    """
    # Align data - only folios with both visual and text features
    common_folios = sorted(set(visual_data.keys()) & set(text_data['pilot_folios'].keys()))

    if len(common_folios) < 10:
        return {'error': f'Too few common folios: {len(common_folios)}'}

    print(f"Analyzing {len(common_folios)} folios with both visual and text data")

    results = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'n_folios': len(common_folios),
            'visual_features_tested': len(VISUAL_FEATURES),
            'text_features_tested': len(TEXT_FEATURES_CATEGORICAL) + len(TEXT_FEATURES_NUMERIC)
        },
        'folio_list': common_folios,
        'categorical_tests': [],
        'numeric_tests': [],
        'null_model_tests': [],
        'cluster_comparison': {}
    }

    # Extract aligned data
    visual_aligned = {f: visual_data[f] for f in common_folios}
    text_aligned = {f: text_data['pilot_folios'][f] for f in common_folios}

    # 1. Categorical Chi-Square Tests
    print("\n[1/4] Running categorical chi-square tests...")
    n_tests = len(VISUAL_FEATURES) * len(TEXT_FEATURES_CATEGORICAL)
    bonferroni_threshold = 0.01 / n_tests

    for vis_feat in VISUAL_FEATURES:
        vis_values = [visual_aligned[f].get(vis_feat, 'UNKNOWN') for f in common_folios]

        # Skip if no variation
        if len(set(vis_values)) < 2:
            continue

        for text_feat in TEXT_FEATURES_CATEGORICAL:
            text_values = [str(text_aligned[f].get(text_feat, 'UNKNOWN')) for f in common_folios]

            if len(set(text_values)) < 2:
                continue

            test_result = chi_square_test(vis_values, text_values)
            test_result['visual_feature'] = vis_feat
            test_result['text_feature'] = text_feat
            test_result['bonferroni_significant'] = (
                test_result.get('p_value', 1.0) < bonferroni_threshold
            )

            results['categorical_tests'].append(test_result)

    # 2. Numeric Feature Tests (binned)
    print("[2/4] Running numeric feature tests...")
    for vis_feat in VISUAL_FEATURES:
        vis_values = [visual_aligned[f].get(vis_feat, 'UNKNOWN') for f in common_folios]

        if len(set(vis_values)) < 2:
            continue

        for text_feat in TEXT_FEATURES_NUMERIC:
            text_values = [text_aligned[f].get(text_feat, 0) for f in common_folios]

            # Bin numeric values
            text_binned = bin_numeric_feature(text_values)

            test_result = chi_square_test(vis_values, text_binned)
            test_result['visual_feature'] = vis_feat
            test_result['text_feature'] = f"{text_feat}_binned"
            test_result['bonferroni_significant'] = (
                test_result.get('p_value', 1.0) < bonferroni_threshold
            )

            results['numeric_tests'].append(test_result)

    # 3. Null Model Tests for significant results
    print("[3/4] Running null model tests on significant correlations...")
    all_tests = results['categorical_tests'] + results['numeric_tests']
    significant_tests = [t for t in all_tests if t.get('p_value', 1.0) < 0.05]

    for test in significant_tests[:20]:  # Limit to top 20 to save time
        vis_feat = test['visual_feature']
        text_feat = test['text_feature']

        vis_values = [visual_aligned[f].get(vis_feat, 'UNKNOWN') for f in common_folios]

        if text_feat.endswith('_binned'):
            orig_feat = text_feat.replace('_binned', '')
            text_values = bin_numeric_feature(
                [text_aligned[f].get(orig_feat, 0) for f in common_folios]
            )
        else:
            text_values = [str(text_aligned[f].get(text_feat, 'UNKNOWN')) for f in common_folios]

        null_result = null_model_test(vis_values, text_values, chi_square_test)
        null_result['visual_feature'] = vis_feat
        null_result['text_feature'] = text_feat
        null_result['original_p_value'] = test.get('p_value', 1.0)

        results['null_model_tests'].append(null_result)

    # 4. Cluster Analysis
    print("[4/4] Running cluster analysis...")

    # Cluster by visual features
    visual_clusters = cluster_folios(
        visual_aligned,
        [f for f in VISUAL_FEATURES if len(set(visual_aligned[c].get(f, 'UNK') for c in common_folios)) > 1][:10],
        n_clusters=[3, 4, 5]
    )

    # Cluster by text features
    # Convert text data to format suitable for clustering
    text_for_clustering = {
        f: {
            'prefix_div_cat': 'HIGH' if text_aligned[f]['prefix_diversity'] > 25 else 'LOW',
            'word_count_cat': 'LONG' if text_aligned[f]['word_count'] > 100 else 'SHORT',
            'heading_prefix': text_aligned[f]['heading_prefix'],
            'heading_in_b': str(text_aligned[f]['heading_in_b'])
        }
        for f in common_folios
    }

    text_clusters = cluster_folios(
        text_for_clustering,
        ['prefix_div_cat', 'word_count_cat', 'heading_prefix'],
        n_clusters=[3, 4, 5]
    )

    # Compare clusterings
    for k in [3, 4, 5]:
        if k in visual_clusters and k in text_clusters:
            if 'labels' in visual_clusters[k] and 'labels' in text_clusters[k]:
                ari = compare_clusterings(
                    visual_clusters[k]['labels'],
                    text_clusters[k]['labels']
                )
                results['cluster_comparison'][k] = {
                    'adjusted_rand_index': ari,
                    'interpretation': 'Strong alignment' if ari > 0.3 else 'Weak/no alignment'
                }

    results['visual_clusters'] = visual_clusters
    results['text_clusters'] = text_clusters

    # Summary
    print("\nComputing summary statistics...")
    results['summary'] = compute_summary(results, bonferroni_threshold)

    return results


def compute_summary(results: Dict, bonferroni_threshold: float) -> Dict:
    """Compute summary statistics and success criteria evaluation."""

    all_tests = results.get('categorical_tests', []) + results.get('numeric_tests', [])

    # Count significant correlations
    sig_p01 = [t for t in all_tests if t.get('p_value', 1.0) < 0.01]
    sig_bonferroni = [t for t in all_tests if t.get('bonferroni_significant', False)]

    # Count null model survivors
    null_tests = results.get('null_model_tests', [])
    null_survivors_99 = [t for t in null_tests if t.get('exceeds_99th', False)]
    null_survivors_95 = [t for t in null_tests if t.get('exceeds_95th', False)]

    # Best correlations (by effect size)
    valid_tests = [t for t in all_tests if t.get('valid', False) and 'cramers_v' in t]
    best_by_effect = sorted(valid_tests, key=lambda x: x.get('cramers_v', 0), reverse=True)[:10]

    # Cluster alignment
    max_ari = max(
        [v.get('adjusted_rand_index', 0) for v in results.get('cluster_comparison', {}).values()],
        default=0
    )

    # Pre-registered success criteria
    criterion_1 = len(sig_bonferroni) >= 3  # At least 3 Bonferroni-significant
    criterion_2 = len(null_survivors_99) >= 1  # At least 1 survives null model
    criterion_3 = max_ari > 0.2  # Cluster alignment above chance

    success = criterion_1 and criterion_2

    return {
        'total_tests_run': len(all_tests),
        'bonferroni_threshold': bonferroni_threshold,

        'significant_at_p01': len(sig_p01),
        'significant_bonferroni': len(sig_bonferroni),
        'bonferroni_significant_tests': [
            {'visual': t['visual_feature'], 'text': t['text_feature'],
             'p': t['p_value'], 'cramers_v': t.get('cramers_v', 0)}
            for t in sig_bonferroni
        ],

        'null_model_tests_run': len(null_tests),
        'null_model_survivors_99th': len(null_survivors_99),
        'null_model_survivors_95th': len(null_survivors_95),

        'best_correlations_by_effect_size': [
            {'visual': t['visual_feature'], 'text': t['text_feature'],
             'cramers_v': t.get('cramers_v', 0), 'p': t.get('p_value', 1)}
            for t in best_by_effect[:5]
        ],

        'max_cluster_ari': max_ari,

        'pre_registered_criteria': {
            'criterion_1_3_bonferroni_significant': criterion_1,
            'criterion_2_1_survives_null_model': criterion_2,
            'criterion_3_cluster_alignment': criterion_3
        },

        'OVERALL_SUCCESS': success,
        'interpretation': (
            'SUCCESS: Visual-text correlation detected. Semantic probing justified.'
            if success else
            'FAILURE: No robust visual-text correlation. Semantic probing not justified.'
        )
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 18, Task 3: Visual-Text Correlation Framework")
    print("=" * 70)

    # Load text features
    print("\nLoading text features...")
    text_data = load_text_features()
    print(f"  Text features loaded for {len(text_data['pilot_folios'])} folios")

    # Try to load visual features
    print("\nLoading visual features...")
    visual_data = load_visual_features()

    if visual_data is None:
        print("\n" + "=" * 70)
        print("FRAMEWORK READY - AWAITING VISUAL CODING DATA")
        print("=" * 70)
        print("""
To run the analysis:
1. Complete visual coding for 30 pilot folios
2. Save coded data as 'visual_coding_data.json' in this directory
3. Run this script again

Expected format for visual_coding_data.json:
{
    "f38r": {
        "root_present": "YES",
        "root_type": "SINGLE_TAPROOT",
        ...
    },
    "f25r": {...},
    ...
}

Pre-registered success criteria:
- At least 3 correlations at p < 0.01 (Bonferroni-corrected)
- At least 1 correlation survives null model (>99th percentile)
- Correlations must be interpretable
        """)
        return

    # Run analysis
    print("\nRunning correlation analysis...")
    results = run_correlation_analysis(visual_data, text_data)

    # Save results
    output_file = 'visual_text_correlation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    summary = results.get('summary', {})
    print(f"\nTests run: {summary.get('total_tests_run', 0)}")
    print(f"Bonferroni significant: {summary.get('significant_bonferroni', 0)}")
    print(f"Null model survivors (99th): {summary.get('null_model_survivors_99th', 0)}")
    print(f"Max cluster ARI: {summary.get('max_cluster_ari', 0)}")

    print("\nPre-registered criteria:")
    criteria = summary.get('pre_registered_criteria', {})
    for k, v in criteria.items():
        status = "PASS" if v else "FAIL"
        print(f"  {k}: {status}")

    print(f"\n{'*' * 70}")
    print(f"OVERALL: {summary.get('interpretation', 'Unknown')}")
    print(f"{'*' * 70}")

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
