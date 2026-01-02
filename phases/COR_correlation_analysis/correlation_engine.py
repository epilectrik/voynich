#!/usr/bin/env python3
"""
Data Recovery Phase, Task 4: Correlation Analysis Engine

Statistical engine for testing visual-text correlations.
Includes chi-square, Fisher's exact, permutation null models,
Bonferroni correction, and interpretability filtering.
"""

import json
import random
import math
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import statistics

# =============================================================================
# CONFIGURATION
# =============================================================================

# Pre-registered thresholds
BONFERRONI_ALPHA = 0.01
NULL_MODEL_PERMUTATIONS = 1000
NULL_MODEL_THRESHOLD_PERCENTILE = 99
UNDETERMINED_RATE_THRESHOLD = 0.30

# Features excluded from correlation tests (compound features)
EXCLUDED_FEATURES = [
    'overall_complexity',
    'identifiable_impression'
]

# =============================================================================
# STATISTICAL TESTS
# =============================================================================

def chi_square_test(visual_values: List, text_values: List) -> Dict:
    """
    Chi-square test for categorical association.

    Returns chi2, p_value, cramers_v, interpretation.
    """
    # Build contingency table
    contingency = {}
    for v, t in zip(visual_values, text_values):
        if v not in contingency:
            contingency[v] = {}
        if t not in contingency[v]:
            contingency[v][t] = 0
        contingency[v][t] += 1

    # Get all categories
    visual_cats = list(contingency.keys())
    text_cats = set()
    for v in visual_cats:
        text_cats.update(contingency[v].keys())
    text_cats = list(text_cats)

    # Build matrix
    n = len(visual_values)
    observed = []
    for v in visual_cats:
        row = [contingency[v].get(t, 0) for t in text_cats]
        observed.append(row)

    # Calculate expected frequencies
    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[i][j] for i in range(len(visual_cats))) for j in range(len(text_cats))]

    expected = []
    for i, row in enumerate(observed):
        exp_row = [(row_sums[i] * col_sums[j]) / n for j in range(len(text_cats))]
        expected.append(exp_row)

    # Chi-square statistic
    chi2 = 0
    for i in range(len(observed)):
        for j in range(len(observed[i])):
            if expected[i][j] > 0:
                chi2 += (observed[i][j] - expected[i][j]) ** 2 / expected[i][j]

    # Degrees of freedom
    df = (len(visual_cats) - 1) * (len(text_cats) - 1)

    # P-value approximation using chi-square distribution
    # Using simple approximation for now
    p_value = chi2_p_value(chi2, df)

    # Cramer's V (effect size)
    k = min(len(visual_cats), len(text_cats))
    cramers_v = math.sqrt(chi2 / (n * (k - 1))) if n > 0 and k > 1 else 0

    # Check for small expected counts
    min_expected = min(min(row) for row in expected) if expected else 0
    small_cells = min_expected < 5

    return {
        'test': 'chi_square',
        'chi2': round(chi2, 4),
        'df': df,
        'p_value': round(p_value, 6),
        'cramers_v': round(cramers_v, 4),
        'n': n,
        'small_cells_warning': small_cells,
        'min_expected': round(min_expected, 2),
        'interpretation': interpret_cramers_v(cramers_v)
    }


def chi2_p_value(chi2: float, df: int) -> float:
    """
    Approximate p-value for chi-square distribution.

    Uses Wilson-Hilferty transformation for approximation.
    """
    if df <= 0 or chi2 <= 0:
        return 1.0

    # Wilson-Hilferty approximation
    z = ((chi2 / df) ** (1/3) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))

    # Standard normal CDF approximation
    p = 0.5 * (1 + math.erf(-z / math.sqrt(2)))

    return max(0, min(1, p))


def interpret_cramers_v(v: float) -> str:
    """Interpret Cramer's V effect size."""
    if v >= 0.3:
        return "STRONG"
    elif v >= 0.2:
        return "MODERATE"
    elif v >= 0.1:
        return "WEAK"
    else:
        return "NEGLIGIBLE"


def fisher_exact_2x2(observed: List[List[int]]) -> Dict:
    """
    Fisher's exact test for 2x2 contingency tables.

    For small cell counts (<5).
    """
    a, b = observed[0]
    c, d = observed[1]
    n = a + b + c + d

    # Calculate probability of observed table
    def log_factorial(x):
        if x <= 1:
            return 0
        return sum(math.log(i) for i in range(2, x + 1))

    def table_prob(a, b, c, d):
        row1 = a + b
        row2 = c + d
        col1 = a + c
        col2 = b + d
        n = a + b + c + d

        log_p = (log_factorial(row1) + log_factorial(row2) +
                 log_factorial(col1) + log_factorial(col2) -
                 log_factorial(n) - log_factorial(a) -
                 log_factorial(b) - log_factorial(c) - log_factorial(d))
        return math.exp(log_p)

    # Two-tailed p-value
    observed_prob = table_prob(a, b, c, d)
    row1, row2 = a + b, c + d
    col1 = a + c

    p_value = 0
    for x in range(min(row1, col1) + 1):
        new_a = x
        new_b = row1 - x
        new_c = col1 - x
        new_d = row2 - new_c

        if new_b >= 0 and new_c >= 0 and new_d >= 0:
            prob = table_prob(new_a, new_b, new_c, new_d)
            if prob <= observed_prob + 1e-10:
                p_value += prob

    return {
        'test': 'fisher_exact',
        'p_value': round(min(1.0, p_value), 6),
        'n': n,
        'observed': observed
    }


def test_categorical_association(visual_values: List, text_values: List) -> Dict:
    """
    Test association between categorical visual and text features.

    Uses chi-square or Fisher's exact depending on cell counts.
    """
    # Filter out None values
    pairs = [(v, t) for v, t in zip(visual_values, text_values) if v is not None and t is not None]
    if len(pairs) < 5:
        return {
            'test': 'insufficient_data',
            'n': len(pairs),
            'error': 'Fewer than 5 valid pairs'
        }

    v_vals, t_vals = zip(*pairs)

    # Run chi-square
    result = chi_square_test(list(v_vals), list(t_vals))

    # If small cells, also run Fisher's exact (for 2x2 only)
    if result['small_cells_warning']:
        v_unique = set(v_vals)
        t_unique = set(t_vals)

        if len(v_unique) == 2 and len(t_unique) == 2:
            # Build 2x2 table
            v_list = list(v_unique)
            t_list = list(t_unique)
            table = [[0, 0], [0, 0]]
            for v, t in pairs:
                i = v_list.index(v)
                j = t_list.index(t)
                table[i][j] += 1

            fisher = fisher_exact_2x2(table)
            result['fisher_exact_p'] = fisher['p_value']
            result['use_fisher'] = True
        else:
            result['use_fisher'] = False

    return result


def test_continuous_correlation(values1: List[float], values2: List[float]) -> Dict:
    """
    Test correlation between continuous features.

    Uses Spearman rank correlation (more robust than Pearson).
    """
    # Filter pairs
    pairs = [(v1, v2) for v1, v2 in zip(values1, values2)
             if v1 is not None and v2 is not None]

    if len(pairs) < 5:
        return {
            'test': 'insufficient_data',
            'n': len(pairs),
            'error': 'Fewer than 5 valid pairs'
        }

    x, y = zip(*pairs)
    n = len(x)

    # Spearman rank correlation
    def rank(data):
        sorted_idx = sorted(range(len(data)), key=lambda i: data[i])
        ranks = [0] * len(data)
        for rank_val, idx in enumerate(sorted_idx):
            ranks[idx] = rank_val + 1
        return ranks

    x_ranks = rank(x)
    y_ranks = rank(y)

    # Calculate correlation
    mean_x = sum(x_ranks) / n
    mean_y = sum(y_ranks) / n

    cov = sum((x_ranks[i] - mean_x) * (y_ranks[i] - mean_y) for i in range(n)) / n
    std_x = math.sqrt(sum((r - mean_x) ** 2 for r in x_ranks) / n)
    std_y = math.sqrt(sum((r - mean_y) ** 2 for r in y_ranks) / n)

    if std_x == 0 or std_y == 0:
        rho = 0
    else:
        rho = cov / (std_x * std_y)

    # T-statistic for significance
    if abs(rho) < 1:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
        # Approximate p-value
        p_value = 2 * (1 - t_distribution_cdf(abs(t_stat), n - 2))
    else:
        t_stat = float('inf') if rho > 0 else float('-inf')
        p_value = 0

    return {
        'test': 'spearman',
        'rho': round(rho, 4),
        't_statistic': round(t_stat, 4),
        'p_value': round(p_value, 6),
        'n': n,
        'interpretation': interpret_correlation(rho)
    }


def t_distribution_cdf(t: float, df: int) -> float:
    """Approximate CDF of t-distribution."""
    if df <= 0:
        return 0.5

    x = df / (df + t * t)

    # Beta function approximation
    a = df / 2
    b = 0.5

    # Incomplete beta function approximation
    if t >= 0:
        return 1 - 0.5 * incomplete_beta(x, a, b)
    else:
        return 0.5 * incomplete_beta(x, a, b)


def incomplete_beta(x: float, a: float, b: float) -> float:
    """Simple approximation of incomplete beta function."""
    # Using continued fraction approximation
    if x <= 0:
        return 0
    if x >= 1:
        return 1

    # Simple numerical integration
    steps = 100
    total = 0
    for i in range(steps):
        t = (i + 0.5) / steps * x
        total += (t ** (a - 1)) * ((1 - t) ** (b - 1))
    return total * x / steps


def interpret_correlation(rho: float) -> str:
    """Interpret correlation coefficient."""
    abs_rho = abs(rho)
    if abs_rho >= 0.7:
        return "STRONG"
    elif abs_rho >= 0.4:
        return "MODERATE"
    elif abs_rho >= 0.2:
        return "WEAK"
    else:
        return "NEGLIGIBLE"


# =============================================================================
# NULL MODEL
# =============================================================================

def null_model_test(visual_values: List, text_values: List,
                   n_permutations: int = NULL_MODEL_PERMUTATIONS) -> Dict:
    """
    Test if observed correlation exceeds null expectation.

    Shuffles visual assignments, recalculates correlation 1000x.
    Returns percentile of real correlation in null distribution.
    """
    # Filter out None values
    pairs = [(v, t) for v, t in zip(visual_values, text_values)
             if v is not None and t is not None]

    if len(pairs) < 5:
        return {
            'test': 'null_model',
            'error': 'Insufficient data',
            'n': len(pairs)
        }

    v_vals, t_vals = zip(*pairs)
    v_list = list(v_vals)
    t_list = list(t_vals)

    # Get observed statistic (Cramer's V)
    observed_result = chi_square_test(v_list, t_list)
    observed_v = observed_result['cramers_v']

    # Generate null distribution
    null_distribution = []
    for _ in range(n_permutations):
        shuffled_v = v_list.copy()
        random.shuffle(shuffled_v)
        null_result = chi_square_test(shuffled_v, t_list)
        null_distribution.append(null_result['cramers_v'])

    # Calculate percentile
    count_below = sum(1 for nv in null_distribution if nv < observed_v)
    percentile = 100 * count_below / n_permutations

    # Statistics
    null_mean = statistics.mean(null_distribution)
    null_std = statistics.stdev(null_distribution) if len(null_distribution) > 1 else 0

    return {
        'test': 'null_model',
        'observed': round(observed_v, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'percentile': round(percentile, 1),
        'n_permutations': n_permutations,
        'significant_at_99': percentile >= 99,
        'significant_at_95': percentile >= 95,
        'z_score': round((observed_v - null_mean) / null_std, 2) if null_std > 0 else 0
    }


# =============================================================================
# MULTIPLE COMPARISON CORRECTION
# =============================================================================

def apply_bonferroni(results: List[Dict], alpha: float = BONFERRONI_ALPHA) -> List[Dict]:
    """
    Apply Bonferroni correction for multiple comparisons.

    Adjusts alpha by dividing by number of tests.
    """
    n_tests = len(results)
    adjusted_alpha = alpha / n_tests

    for result in results:
        p = result.get('p_value', 1.0)
        result['bonferroni_alpha'] = round(adjusted_alpha, 6)
        result['significant_bonferroni'] = p < adjusted_alpha
        result['n_tests'] = n_tests

    return results


# =============================================================================
# INTERPRETABILITY FILTER
# =============================================================================

def filter_interpretable(results: List[Dict], undetermined_rates: Dict) -> Dict:
    """
    Filter correlations to those involving single visual dimensions.

    REJECTS:
    - Correlations involving 'complexity' or 'overall_complexity'
    - Compound features (multiple visual properties)
    - Features with >30% UNDETERMINED rate

    RANKS surviving correlations by:
    1. Simplicity (single-feature > multi-feature)
    2. Effect size (Cramer's V)
    3. Null model percentile
    """
    rejected = []
    accepted = []

    for result in results:
        visual_feature = result.get('visual_feature', '')
        rejection_reasons = []

        # Check excluded features
        if visual_feature in EXCLUDED_FEATURES:
            rejection_reasons.append(f"Compound feature: {visual_feature}")

        # Check for complexity in name
        if 'complexity' in visual_feature.lower():
            rejection_reasons.append("Contains 'complexity'")

        # Check UNDETERMINED rate
        undet_rate = undetermined_rates.get(visual_feature, 0)
        if undet_rate > UNDETERMINED_RATE_THRESHOLD:
            rejection_reasons.append(f"High UNDETERMINED rate: {undet_rate:.1%}")

        if rejection_reasons:
            result['rejected'] = True
            result['rejection_reasons'] = rejection_reasons
            rejected.append(result)
        else:
            result['rejected'] = False
            accepted.append(result)

    # Rank accepted results
    # Priority: effect_size > null_percentile > p_value
    def sort_key(r):
        cramers_v = r.get('cramers_v', 0)
        percentile = r.get('null_percentile', 0)
        p_val = r.get('p_value', 1)
        return (-cramers_v, -percentile, p_val)

    accepted_sorted = sorted(accepted, key=sort_key)

    for i, r in enumerate(accepted_sorted):
        r['rank'] = i + 1

    return {
        'accepted': accepted_sorted,
        'rejected': rejected,
        'n_accepted': len(accepted_sorted),
        'n_rejected': len(rejected)
    }


# =============================================================================
# FULL ANALYSIS PIPELINE
# =============================================================================

def run_full_correlation_analysis(merged_data: Dict, undetermined_rates: Dict) -> Dict:
    """
    Run all tests, apply corrections, filter for interpretability.

    Returns structured report with explicit pass/fail against pre-registered criteria.
    """
    from visual_data_join import VISUAL_FEATURE_SCHEMA, EXCLUDED_FROM_CORRELATION

    # Get all valid visual features
    visual_features = [
        f for f in VISUAL_FEATURE_SCHEMA.keys()
        if f not in EXCLUDED_FROM_CORRELATION
        and undetermined_rates.get(f, 0) <= UNDETERMINED_RATE_THRESHOLD
    ]

    # Text features to test
    text_features_categorical = [
        'part1_dominant_prefix', 'part2_dominant_prefix', 'part3_dominant_prefix',
        'heading_prefix'
    ]
    text_features_continuous = [
        'word_count', 'unique_word_count', 'vocabulary_richness',
        'prefix_diversity', 'heading_length'
    ]

    all_results = []

    # Test categorical associations
    for v_feat in visual_features:
        for t_feat in text_features_categorical:
            v_vals = [merged_data[f]['visual_features'].get(v_feat) for f in merged_data]
            t_vals = [merged_data[f]['text_features'].get(t_feat) for f in merged_data]

            result = test_categorical_association(v_vals, t_vals)
            result['visual_feature'] = v_feat
            result['text_feature'] = t_feat
            result['feature_pair'] = f"{v_feat} × {t_feat}"

            # Run null model
            null_result = null_model_test(v_vals, t_vals)
            result['null_percentile'] = null_result.get('percentile', 0)
            result['null_significant_99'] = null_result.get('significant_at_99', False)

            all_results.append(result)

    # Test continuous correlations
    for v_feat in visual_features:
        # Convert categorical visual to ordinal if possible
        for t_feat in text_features_continuous:
            v_vals = [merged_data[f]['visual_features'].get(v_feat) for f in merged_data]
            t_vals = [merged_data[f]['text_features'].get(t_feat) for f in merged_data]

            # Skip if visual is categorical
            if not all(isinstance(v, (int, float)) for v in v_vals if v is not None):
                continue

            result = test_continuous_correlation(v_vals, t_vals)
            result['visual_feature'] = v_feat
            result['text_feature'] = t_feat
            result['feature_pair'] = f"{v_feat} × {t_feat}"

            all_results.append(result)

    # Apply Bonferroni correction
    all_results = apply_bonferroni(all_results)

    # Filter for interpretability
    filtered = filter_interpretable(all_results, undetermined_rates)

    # Count significant results
    significant_bonferroni = [r for r in filtered['accepted'] if r.get('significant_bonferroni', False)]
    significant_null_99 = [r for r in filtered['accepted'] if r.get('null_significant_99', False)]

    # Evaluate against pre-registered criteria
    criteria_met = {
        'at_least_3_significant': len(significant_bonferroni) >= 3,
        'at_least_1_null_survives': len(significant_null_99) >= 1,
        'single_dimension_only': len(filtered['rejected']) < len(all_results)
    }
    overall_success = all(criteria_met.values())

    return {
        'metadata': {
            'date': datetime.now().isoformat(),
            'n_tests': len(all_results),
            'n_accepted': filtered['n_accepted'],
            'n_rejected': filtered['n_rejected'],
            'bonferroni_alpha': round(BONFERRONI_ALPHA / len(all_results), 6)
        },
        'pre_registered_criteria': {
            'criterion_1': {
                'description': '>=3 correlations at p < 0.01 (Bonferroni-corrected)',
                'met': criteria_met['at_least_3_significant'],
                'count': len(significant_bonferroni)
            },
            'criterion_2': {
                'description': '>=1 correlation surviving null model (>99th percentile)',
                'met': criteria_met['at_least_1_null_survives'],
                'count': len(significant_null_99)
            },
            'criterion_3': {
                'description': 'Single-dimension correlations only (no compound features)',
                'met': criteria_met['single_dimension_only'],
                'rejected_count': filtered['n_rejected']
            },
            'overall_success': overall_success
        },
        'significant_results': {
            'bonferroni_significant': [
                {
                    'visual': r['visual_feature'],
                    'text': r['text_feature'],
                    'cramers_v': r.get('cramers_v'),
                    'p_value': r.get('p_value'),
                    'null_percentile': r.get('null_percentile')
                }
                for r in significant_bonferroni
            ],
            'null_model_significant': [
                {
                    'visual': r['visual_feature'],
                    'text': r['text_feature'],
                    'cramers_v': r.get('cramers_v'),
                    'null_percentile': r.get('null_percentile')
                }
                for r in significant_null_99
            ]
        },
        'all_accepted_results': filtered['accepted'],
        'rejected_results': filtered['rejected']
    }


# =============================================================================
# MAIN (for testing)
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 4: Correlation Engine")
    print("=" * 70)

    print("\nCorrelation engine ready.")
    print("Awaiting visual coding data to run analysis.")
    print("\nCapabilities:")
    print("  - Chi-square test with Cramer's V")
    print("  - Fisher's exact test for small cells")
    print("  - Spearman correlation for continuous")
    print("  - Permutation null model (1000 shuffles)")
    print("  - Bonferroni correction")
    print("  - Interpretability filter")
    print(f"\nPre-registered thresholds:")
    print(f"  - Bonferroni alpha: {BONFERRONI_ALPHA}")
    print(f"  - Null model permutations: {NULL_MODEL_PERMUTATIONS}")
    print(f"  - Null model threshold: {NULL_MODEL_THRESHOLD_PERCENTILE}th percentile")
    print(f"  - Max UNDETERMINED rate: {UNDETERMINED_RATE_THRESHOLD:.0%}")

    # Save engine configuration
    config = {
        'metadata': {
            'title': 'Correlation Engine Configuration',
            'phase': 'Data Recovery Phase, Task 4',
            'date': datetime.now().isoformat()
        },
        'thresholds': {
            'bonferroni_alpha': BONFERRONI_ALPHA,
            'null_model_permutations': NULL_MODEL_PERMUTATIONS,
            'null_model_threshold_percentile': NULL_MODEL_THRESHOLD_PERCENTILE,
            'undetermined_rate_threshold': UNDETERMINED_RATE_THRESHOLD
        },
        'excluded_features': EXCLUDED_FEATURES,
        'tests_available': [
            'chi_square_test',
            'fisher_exact_2x2',
            'test_categorical_association',
            'test_continuous_correlation',
            'null_model_test'
        ],
        'status': 'READY - awaiting visual data'
    }

    with open('correlation_engine_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved configuration to: correlation_engine_config.json")


if __name__ == '__main__':
    main()
