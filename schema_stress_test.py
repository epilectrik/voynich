#!/usr/bin/env python3
"""
Data Recovery Phase, Task 7: Schema Stress Test

Tests whether recovered structure is robust or artifactual.
Permutes prefix assignments and reruns correlation pipeline.

Interpretation:
- Structure collapses under permutation -> findings are REAL
- Structure survives permutation -> findings may be ARTIFACTS
"""

import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
import statistics

# =============================================================================
# CONFIGURATION
# =============================================================================

N_PERMUTATIONS = 100
RANDOM_SEED = 42


# =============================================================================
# PREFIX PERMUTATION
# =============================================================================

def permute_prefix_assignments(text_data: Dict, seed: int = None) -> Dict:
    """
    Randomly permute prefix assignments across entries.

    Each entry's dominant prefixes are shuffled to different entries.
    Text content remains unchanged - only prefix labels are permuted.
    """
    if seed is not None:
        random.seed(seed)

    pilot_folios = text_data.get('pilot_folios', {})
    folio_ids = list(pilot_folios.keys())

    # Collect all prefix assignments
    part1_prefixes = [pilot_folios[f].get('part1_dominant_prefix', '') for f in folio_ids]
    part2_prefixes = [pilot_folios[f].get('part2_dominant_prefix', '') for f in folio_ids]
    part3_prefixes = [pilot_folios[f].get('part3_dominant_prefix', '') for f in folio_ids]
    heading_prefixes = [pilot_folios[f].get('heading_prefix', '') for f in folio_ids]

    # Shuffle each prefix list independently
    random.shuffle(part1_prefixes)
    random.shuffle(part2_prefixes)
    random.shuffle(part3_prefixes)
    random.shuffle(heading_prefixes)

    # Create permuted data
    permuted = {'pilot_folios': {}}
    for i, folio_id in enumerate(folio_ids):
        original = pilot_folios[folio_id].copy()
        original['part1_dominant_prefix'] = part1_prefixes[i]
        original['part2_dominant_prefix'] = part2_prefixes[i]
        original['part3_dominant_prefix'] = part3_prefixes[i]
        original['heading_prefix'] = heading_prefixes[i]
        permuted['pilot_folios'][folio_id] = original

    return permuted


# =============================================================================
# SIMPLE CORRELATION TEST (for stress testing)
# =============================================================================

def simple_chi_square(values1: List, values2: List) -> Tuple[float, float]:
    """
    Simple chi-square test returning chi2 and Cramer's V.

    For stress testing - simplified implementation.
    """
    # Filter pairs
    pairs = [(v1, v2) for v1, v2 in zip(values1, values2)
             if v1 and v2 and v1 != 'UNDETERMINED' and v2 != 'UNDETERMINED']

    if len(pairs) < 5:
        return 0, 0

    # Build contingency table
    contingency = defaultdict(lambda: defaultdict(int))
    for v1, v2 in pairs:
        contingency[v1][v2] += 1

    cats1 = list(contingency.keys())
    cats2 = set()
    for v in contingency.values():
        cats2.update(v.keys())
    cats2 = list(cats2)

    n = len(pairs)
    observed = [[contingency[c1].get(c2, 0) for c2 in cats2] for c1 in cats1]

    # Expected frequencies
    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[i][j] for i in range(len(cats1))) for j in range(len(cats2))]

    # Chi-square
    chi2 = 0
    for i in range(len(cats1)):
        for j in range(len(cats2)):
            expected = (row_sums[i] * col_sums[j]) / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    # Cramer's V
    import math
    k = min(len(cats1), len(cats2))
    cramers_v = math.sqrt(chi2 / (n * (k - 1))) if n > 0 and k > 1 else 0

    return chi2, cramers_v


def count_significant_correlations(visual_data: Dict, text_data: Dict,
                                  threshold: float = 0.2) -> int:
    """
    Count correlations with Cramer's V above threshold.
    """
    visual_features = ['root_type', 'stem_count', 'leaf_shape', 'flower_shape', 'plant_symmetry']
    text_features = ['part1_dominant_prefix', 'heading_prefix']

    pilot_folios = text_data.get('pilot_folios', {})
    common_folios = set(visual_data.keys()) & set(pilot_folios.keys())

    if len(common_folios) < 10:
        return 0

    significant_count = 0

    for v_feat in visual_features:
        for t_feat in text_features:
            v_vals = [visual_data.get(f, {}).get(v_feat) for f in common_folios]
            t_vals = [pilot_folios.get(f, {}).get(t_feat) for f in common_folios]

            _, cramers_v = simple_chi_square(v_vals, t_vals)
            if cramers_v >= threshold:
                significant_count += 1

    return significant_count


# =============================================================================
# STRESS TEST
# =============================================================================

def run_stress_test(visual_data: Dict, text_data: Dict,
                   n_permutations: int = N_PERMUTATIONS) -> Dict:
    """
    Run prefix permutation stress test.

    1. Count significant correlations with original data
    2. Permute prefix assignments N times
    3. Count significant correlations each time
    4. Compare original to permuted distribution
    """
    print(f"\n  Running {n_permutations} permutations...")

    # Original correlation count
    original_count = count_significant_correlations(visual_data, text_data)
    print(f"  Original significant correlations: {original_count}")

    # Permuted distribution
    permuted_counts = []
    for i in range(n_permutations):
        permuted_text = permute_prefix_assignments(text_data, seed=RANDOM_SEED + i)
        count = count_significant_correlations(visual_data, permuted_text)
        permuted_counts.append(count)

        if (i + 1) % 20 == 0:
            print(f"    Completed {i + 1}/{n_permutations} permutations...")

    # Statistics
    mean_permuted = statistics.mean(permuted_counts)
    std_permuted = statistics.stdev(permuted_counts) if len(permuted_counts) > 1 else 0

    # Percentile of original in permuted distribution
    count_below = sum(1 for c in permuted_counts if c < original_count)
    percentile = 100 * count_below / n_permutations

    # Z-score
    z_score = (original_count - mean_permuted) / std_permuted if std_permuted > 0 else 0

    # Interpretation
    if percentile >= 95:
        interpretation = "ROBUST"
        explanation = "Original structure significantly exceeds permuted baseline. Findings are REAL."
    elif percentile >= 80:
        interpretation = "MARGINALLY_ROBUST"
        explanation = "Original structure somewhat exceeds baseline. Findings may be real but weaker than expected."
    else:
        interpretation = "POTENTIALLY_ARTIFACTUAL"
        explanation = "Original structure does not exceed permuted baseline. Findings may be frequency artifacts."

    return {
        'original_significant_correlations': original_count,
        'permuted_statistics': {
            'mean': round(mean_permuted, 2),
            'std': round(std_permuted, 2),
            'min': min(permuted_counts),
            'max': max(permuted_counts),
            'distribution': dict(Counter(permuted_counts))
        },
        'comparison': {
            'original_percentile': round(percentile, 1),
            'z_score': round(z_score, 2)
        },
        'interpretation': interpretation,
        'explanation': explanation,
        'n_permutations': n_permutations
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Data Recovery Phase, Task 7: Schema Stress Test")
    print("=" * 70)

    print("\nSchema stress test framework ready.")
    print("Awaiting visual data to run permutation tests.")

    print("\nMethodology:")
    print(f"  1. Count significant correlations (Cramer's V >= 0.2)")
    print(f"  2. Permute prefix assignments {N_PERMUTATIONS} times")
    print(f"  3. Count correlations each permutation")
    print(f"  4. Compare original to permuted distribution")

    print("\nInterpretation:")
    print("  - Original > 95th percentile: ROBUST (real findings)")
    print("  - Original 80-95th percentile: MARGINALLY_ROBUST")
    print("  - Original < 80th percentile: POTENTIALLY_ARTIFACTUAL")

    # Save configuration
    config = {
        'metadata': {
            'title': 'Schema Stress Test Configuration',
            'phase': 'Data Recovery Phase, Task 7',
            'date': datetime.now().isoformat()
        },
        'parameters': {
            'n_permutations': N_PERMUTATIONS,
            'significance_threshold': 0.2,
            'random_seed': RANDOM_SEED
        },
        'interpretation_thresholds': {
            'robust': 95,
            'marginally_robust': 80,
            'potentially_artifactual': 0
        },
        'status': 'READY - awaiting visual data'
    }

    with open('schema_stress_test_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print(f"\nSaved configuration to: schema_stress_test_config.json")


if __name__ == '__main__':
    main()
