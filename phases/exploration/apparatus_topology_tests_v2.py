#!/usr/bin/env python3
"""
APPARATUS-TOPOLOGY Hypothesis Tests v2 (REDESIGNED)

IMPORTANT: This version corrects the test design failures in v1.

Key principle:
  AZC and Currier B occupy DISJOINT folio sets by architectural design.
  Direct folio-level or token-level joins are INVALID.
  All tests must operate at ADJACENCY or QUIRE level.

TEST 1' (K1'): Adjacency-Level AZC Influence
  - Compare B folios NEAR AZC pages vs B folios FAR from AZC pages
  - Tests whether proximity to AZC contexts affects B program characteristics

TEST 7' (K2'): True Negative Control
  - Ensure AZC placement does NOT predict B token identity
  - Uses shuffled alignment to establish null distribution
  - Any signal is a MODEL VIOLATION

Pre-registered kill conditions:
  K1': No p < 0.01 difference in any B metric (near vs far) -> REJECT hypothesis
  K2': AZC placement explains B variance beyond shuffled controls -> MODEL VIOLATION
"""

import json
import csv
import re
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Key data files
CONTROL_SIGNATURES = RESULTS / "control_signatures.json"
AZC_FOLIO_FEATURES = RESULTS / "azc_folio_features.json"

def load_b_metrics():
    """Load B folio control signatures."""
    with open(CONTROL_SIGNATURES) as f:
        data = json.load(f)
    return data.get('signatures', {})

def load_azc_features():
    """Load AZC folio features."""
    with open(AZC_FOLIO_FEATURES) as f:
        data = json.load(f)
    return data.get('folios', {})

def load_transcription():
    """Load full transcription."""
    rows = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            rows.append(row)
    return rows

def parse_folio_number(folio):
    """
    Extract numeric ordering from folio name.
    e.g., 'f26r' -> (26, 0), 'f26v' -> (26, 1), 'f85r1' -> (85, 0.1)
    """
    match = re.match(r'f(\d+)([rv])(\d*)', folio)
    if not match:
        return (999, 0)  # Unknown folios sort to end

    num = int(match.group(1))
    side = 0 if match.group(2) == 'r' else 1
    sub = int(match.group(3)) / 10 if match.group(3) else 0

    return (num, side + sub)

def get_folio_order(folios):
    """Sort folios into manuscript order."""
    return sorted(folios, key=parse_folio_number)

def compute_folio_distances(folio_order):
    """
    Create a distance matrix between folios based on position in manuscript.
    Returns dict: (folio_a, folio_b) -> distance
    """
    position = {f: i for i, f in enumerate(folio_order)}
    distances = {}
    for f1 in folio_order:
        for f2 in folio_order:
            distances[(f1, f2)] = abs(position[f1] - position[f2])
    return distances, position

# ============================================================
# TEST 1': Adjacency-Level AZC Influence
# ============================================================

def run_test_1_prime(b_metrics, azc_features, window_sizes=[1, 2, 3, 5]):
    """
    TEST 1' (REDESIGNED): Adjacency-Level AZC Influence

    Compare B folios NEAR AZC pages vs B folios FAR from AZC pages.

    Kill condition K1':
    If no metric shows p < 0.01 difference between near and far groups
    -> REJECT apparatus-topology hypothesis
    """
    print("=" * 70)
    print("TEST 1' (REDESIGNED): Adjacency-Level AZC Influence")
    print("=" * 70)
    print("\nPrinciple: AZC and B are architecturally segregated.")
    print("We test whether PROXIMITY to AZC affects B program characteristics.")

    # Get all folios and establish ordering
    all_folios = set(b_metrics.keys()) | set(azc_features.keys())
    folio_order = get_folio_order(all_folios)
    distances, positions = compute_folio_distances(folio_order)

    print(f"\n[1] Folio inventory:")
    print(f"    B folios: {len(b_metrics)}")
    print(f"    AZC folios: {len(azc_features)}")
    print(f"    Total ordered folios: {len(folio_order)}")

    # For each B folio, compute minimum distance to any AZC folio
    b_azc_distances = {}
    azc_set = set(azc_features.keys())

    for b_folio in b_metrics:
        if b_folio not in positions:
            continue
        min_dist = float('inf')
        for azc_folio in azc_set:
            if azc_folio in positions:
                d = distances.get((b_folio, azc_folio), float('inf'))
                min_dist = min(min_dist, d)
        b_azc_distances[b_folio] = min_dist

    print(f"\n[2] B folio distances to nearest AZC:")
    dist_counts = Counter(b_azc_distances.values())
    for d in sorted(dist_counts.keys())[:10]:
        print(f"    Distance {d}: {dist_counts[d]} B folios")

    # Metrics to compare
    test_metrics = ['link_density', 'hazard_density', 'intervention_frequency',
                    'kernel_contact_ratio', 'cycle_regularity', 'mean_cycle_length']

    results = {
        'window_tests': {},
        'any_significant': False
    }

    # Test each window size
    for window in window_sizes:
        print(f"\n[3.{window}] Testing window size = {window} folios:")

        # Partition B folios
        near_azc = [f for f, d in b_azc_distances.items() if d <= window]
        far_azc = [f for f, d in b_azc_distances.items() if d > window]

        print(f"    B-near-AZC (distance <= {window}): {len(near_azc)} folios")
        print(f"    B-far-from-AZC (distance > {window}): {len(far_azc)} folios")

        if len(near_azc) < 3 or len(far_azc) < 3:
            print(f"    -> Insufficient samples, skipping")
            continue

        window_results = {}

        for metric in test_metrics:
            near_values = [b_metrics[f].get(metric) for f in near_azc
                          if metric in b_metrics[f]]
            far_values = [b_metrics[f].get(metric) for f in far_azc
                         if metric in b_metrics[f]]

            near_values = [v for v in near_values if v is not None]
            far_values = [v for v in far_values if v is not None]

            if len(near_values) < 3 or len(far_values) < 3:
                continue

            # Mann-Whitney U test (non-parametric)
            u_stat, p_value = stats.mannwhitneyu(near_values, far_values,
                                                  alternative='two-sided')

            # Effect size (rank-biserial correlation)
            n1, n2 = len(near_values), len(far_values)
            r = 1 - (2 * u_stat) / (n1 * n2)  # Rank-biserial correlation

            window_results[metric] = {
                'near_mean': float(np.mean(near_values)),
                'far_mean': float(np.mean(far_values)),
                'near_n': n1,
                'far_n': n2,
                'U': float(u_stat),
                'p': float(p_value),
                'effect_size_r': float(r)
            }

            sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else ""
            direction = "NEAR > FAR" if np.mean(near_values) > np.mean(far_values) else "FAR > NEAR"
            print(f"    {metric}: near={np.mean(near_values):.3f}, far={np.mean(far_values):.3f}, "
                  f"p={p_value:.4f}, r={r:.3f} [{direction}] {sig}")

            if p_value < 0.01:
                results['any_significant'] = True

        results['window_tests'][f'window_{window}'] = {
            'near_count': len(near_azc),
            'far_count': len(far_azc),
            'metrics': window_results
        }

    # K1' evaluation
    print(f"\n[4] Kill Condition K1' Evaluation:")
    if results['any_significant']:
        print("    RESULT: At least one metric shows p < 0.01 difference")
        print("    -> K1' NOT TRIGGERED, hypothesis survives")
        k1_triggered = False
    else:
        print("    RESULT: No metric shows p < 0.01 difference at any window size")
        print("    -> K1' TRIGGERED, hypothesis REJECTED")
        k1_triggered = True

    results['k1_prime_triggered'] = k1_triggered
    results['b_azc_distances'] = {k: int(v) if v != float('inf') else None
                                   for k, v in b_azc_distances.items()}

    return results


# ============================================================
# TEST 7': True Negative Control
# ============================================================

def run_test_7_prime(b_metrics, azc_features, n_permutations=1000):
    """
    TEST 7' (REDESIGNED): True Negative Control

    AZC placement must NOT predict Currier B token characteristics.
    Uses shuffled alignment to establish null distribution.

    Kill condition K2':
    If observed correlation exceeds 95th percentile of shuffled controls
    -> MODEL VIOLATION (investigate leakage)
    """
    print("\n" + "=" * 70)
    print("TEST 7' (REDESIGNED): True Negative Control")
    print("=" * 70)
    print("\nPrinciple: AZC placement must NOT predict B characteristics.")
    print("Any signal beyond chance is a MODEL VIOLATION.")

    # Get AZC placement distributions per folio
    azc_placement_vectors = {}
    for folio, features in azc_features.items():
        pv = features.get('placement_vector', {})
        if pv:
            # Normalize to sum to 1
            total = sum(pv.values())
            if total > 0:
                azc_placement_vectors[folio] = {k: v/total for k, v in pv.items()}

    # Get B metrics
    b_metric_values = {}
    test_metrics = ['link_density', 'hazard_density', 'intervention_frequency']

    for folio, metrics in b_metrics.items():
        b_metric_values[folio] = {m: metrics.get(m, 0) for m in test_metrics}

    print(f"\n[1] Data inventory:")
    print(f"    AZC folios with placement vectors: {len(azc_placement_vectors)}")
    print(f"    B folios with metrics: {len(b_metric_values)}")

    # Since AZC and B are on different folios, we create arbitrary alignments
    # The null hypothesis is that ANY alignment should show no correlation

    azc_folios = list(azc_placement_vectors.keys())
    b_folios = list(b_metric_values.keys())

    if len(azc_folios) == 0 or len(b_folios) == 0:
        print("\n    ERROR: Insufficient data for test")
        return {'error': 'insufficient_data', 'k2_prime_triggered': False}

    # For each AZC placement dimension, test correlation with B metrics
    # under random alignment

    placement_dims = list(next(iter(azc_placement_vectors.values())).keys())

    print(f"    AZC placement dimensions: {len(placement_dims)}")
    print(f"\n[2] Running {n_permutations} permutation tests...")

    # Observed "correlations" under various random alignments
    # Since they're on different folios, we pair them by position in sorted order
    # Then shuffle to get null distribution

    min_n = min(len(azc_folios), len(b_folios))

    # Create baseline alignment (sorted order)
    azc_sorted = sorted(azc_folios, key=parse_folio_number)[:min_n]
    b_sorted = sorted(b_folios, key=parse_folio_number)[:min_n]

    def compute_alignment_correlation(azc_order, b_order, placement_dim, b_metric):
        """Compute correlation between AZC placement and B metric under given alignment."""
        azc_vals = [azc_placement_vectors[f].get(placement_dim, 0) for f in azc_order]
        b_vals = [b_metric_values[f].get(b_metric, 0) for f in b_order]

        if len(set(azc_vals)) < 2 or len(set(b_vals)) < 2:
            return 0.0

        rho, _ = stats.spearmanr(azc_vals, b_vals)
        return rho if not np.isnan(rho) else 0.0

    # Test each combination
    results = {
        'tests': {},
        'any_violation': False
    }

    for b_metric in test_metrics:
        print(f"\n    Testing B metric: {b_metric}")

        for placement_dim in ['R1', 'R2', 'R3', 'S1', 'S2', 'C']:  # Key placements
            if placement_dim not in placement_dims:
                continue

            # Observed correlation (arbitrary but consistent alignment)
            observed_rho = compute_alignment_correlation(
                azc_sorted, b_sorted, placement_dim, b_metric
            )

            # Null distribution via permutation
            null_rhos = []
            for _ in range(n_permutations):
                shuffled_b = list(b_sorted)
                np.random.shuffle(shuffled_b)
                null_rho = compute_alignment_correlation(
                    azc_sorted, shuffled_b, placement_dim, b_metric
                )
                null_rhos.append(null_rho)

            null_rhos = np.array(null_rhos)

            # P-value: proportion of null that exceeds observed
            p_value = np.mean(np.abs(null_rhos) >= np.abs(observed_rho))

            # 95th percentile of null
            threshold_95 = np.percentile(np.abs(null_rhos), 95)

            violation = np.abs(observed_rho) > threshold_95

            test_key = f"{placement_dim}_vs_{b_metric}"
            results['tests'][test_key] = {
                'observed_rho': float(observed_rho),
                'null_mean': float(np.mean(null_rhos)),
                'null_std': float(np.std(null_rhos)),
                'threshold_95': float(threshold_95),
                'p_value': float(p_value),
                'violation': bool(violation)
            }

            status = "VIOLATION!" if violation else "OK"
            print(f"      {placement_dim}: rho={observed_rho:.3f}, "
                  f"null_95={threshold_95:.3f}, p={p_value:.3f} [{status}]")

            if violation:
                results['any_violation'] = True

    # K2' evaluation
    print(f"\n[3] Kill Condition K2' Evaluation:")
    if results['any_violation']:
        print("    WARNING: Observed correlation exceeds null distribution")
        print("    -> K2' TRIGGERED, MODEL VIOLATION - investigate leakage")
        k2_triggered = True
    else:
        print("    RESULT: No correlation exceeds shuffled controls")
        print("    -> K2' NOT TRIGGERED, negative control PASSED")
        k2_triggered = False

    results['k2_prime_triggered'] = k2_triggered

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("APPARATUS-TOPOLOGY HYPOTHESIS: Redesigned Critical Tests (v2)")
    print("=" * 70)
    print("\nIMPORTANT: This version corrects the test design from v1.")
    print("AZC and B are architecturally segregated - tests operate at")
    print("ADJACENCY level, not folio level.")
    print("\nPre-registered kill conditions:")
    print("  K1': No p < 0.01 difference (near vs far AZC) -> REJECT hypothesis")
    print("  K2': AZC predicts B beyond shuffled null -> MODEL VIOLATION")
    print("=" * 70)

    # Load data
    print("\n[Loading data...]")
    b_metrics = load_b_metrics()
    print(f"  B folio metrics: {len(b_metrics)} folios")

    azc_features = load_azc_features()
    print(f"  AZC folio features: {len(azc_features)} folios")

    # Run redesigned tests
    test1_result = run_test_1_prime(b_metrics, azc_features)
    test7_result = run_test_7_prime(b_metrics, azc_features, n_permutations=1000)

    # Final verdict
    print("\n" + "=" * 70)
    print("DECISION GATE (v2)")
    print("=" * 70)

    k1_triggered = test1_result.get('k1_prime_triggered', True)
    k2_triggered = test7_result.get('k2_prime_triggered', False)

    if k1_triggered and not k2_triggered:
        print("\nK1' TRIGGERED: No significant adjacency effect found")
        print("K2' NOT TRIGGERED: Negative control passed")
        print("-> HYPOTHESIS REJECTED (no evidence of AZC influence on B)")
        verdict = "REJECTED"
    elif k2_triggered:
        print("\nK2' TRIGGERED: Model integrity violation detected")
        print("-> STOP AND AUDIT MODEL")
        verdict = "MODEL_VIOLATION"
    elif not k1_triggered and not k2_triggered:
        print("\nBoth tests passed:")
        print("  - K1': Adjacency effect detected (hypothesis survives)")
        print("  - K2': Negative control passed (model intact)")
        print("-> PROCEED to secondary tests")
        verdict = "PROCEED"
    else:
        print("\nUnexpected state - review results manually")
        verdict = "REVIEW"

    # Save results
    output = {
        'metadata': {
            'analysis': 'APPARATUS-TOPOLOGY Critical Tests v2 (REDESIGNED)',
            'tests_run': ['TEST 1 prime', 'TEST 7 prime'],
            'design_note': 'Tests operate at adjacency level, not folio level'
        },
        'test_1_prime': {k: v for k, v in test1_result.items()
                        if k != 'b_azc_distances'},  # Exclude large dict
        'test_7_prime': test7_result,
        'verdict': verdict,
        'kill_conditions': {
            'k1_prime_triggered': k1_triggered,
            'k2_prime_triggered': k2_triggered
        }
    }

    output_path = RESULTS / "apparatus_topology_critical_tests_v2.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    return output

if __name__ == "__main__":
    main()
