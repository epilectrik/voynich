#!/usr/bin/env python3
"""
ILL-TOP-1 Tests F, G, H: Remaining Order/Geometry Tests

Test F: Quire-Level Regime Articulation
  Do illustration regime shifts align with quire-level boundaries?

Test G: Multi-Folio Perceptual Scaffolding
  Do visual "runs" (consecutive folios in same cluster) show consistent
  within-run constraint patterns vs between-run?

Test H: Negative Geometric Test
  Document absence of fold/overlay/composite geometric signals.
"""

import json
import re
import numpy as np
from pathlib import Path
from scipy import stats
from collections import Counter, defaultdict
from itertools import combinations

OUTPUT_DIR = Path(__file__).parent


def extract_folio_number(folio: str) -> tuple:
    """Extract sortable folio number."""
    match = re.match(r'f(\d+)([rv])', folio)
    if match:
        num = int(match.group(1))
        side = match.group(2)
        side_order = 0 if side == 'r' else 1
        return (num, side_order)
    return (999, 0)


def get_quire_for_folio(folio: str, quire_data: dict) -> str:
    """Determine which quire a folio belongs to."""
    # Extract folio number
    match = re.match(r'f(\d+)([rv])', folio)
    if not match:
        return 'UNKNOWN'

    folio_num = int(match.group(1))

    # Use quire boundaries to determine membership
    # Quire A: f1-f8, B: f9-f16, C: f17-f24, D: f25-f32, etc.
    quire_ranges = {
        'A': (1, 8), 'B': (9, 16), 'C': (17, 24), 'D': (25, 32),
        'E': (33, 40), 'F': (41, 48), 'G': (49, 56), 'H': (57, 66),
    }

    for quire, (start, end) in quire_ranges.items():
        if start <= folio_num <= end:
            return quire

    return 'UNKNOWN'


def compute_jaccard(set1: set, set2: set) -> float:
    """Compute Jaccard similarity."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def run_test_f(folio_metadata: dict, folios_sorted: list):
    """
    Test F: Quire-Level Regime Articulation

    Do illustration regime shifts align with quire-level regime transitions?
    """
    print("=" * 60)
    print("TEST F: Quire-Level Regime Articulation")
    print("=" * 60)

    # Assign quires
    folio_quires = {}
    for folio in folios_sorted:
        folio_quires[folio] = get_quire_for_folio(folio, None)

    print(f"\nFolio-Quire assignments:")
    quire_dist = Counter(folio_quires.values())
    print(f"  Distribution: {dict(quire_dist)}")

    # Build sequences
    visual_seq = [folio_metadata[f]['visual_cluster'] for f in folios_sorted]
    quire_seq = [folio_quires[f] for f in folios_sorted]

    print(f"\nVisual cluster sequence: {visual_seq}")
    print(f"Quire sequence: {quire_seq}")

    # Identify visual transitions and quire boundaries
    visual_transitions = []
    quire_boundaries = []

    for i in range(len(folios_sorted) - 1):
        is_visual_trans = visual_seq[i] != visual_seq[i+1]
        is_quire_bound = quire_seq[i] != quire_seq[i+1]
        visual_transitions.append(1 if is_visual_trans else 0)
        quire_boundaries.append(1 if is_quire_bound else 0)

    print(f"\nVisual transitions (0/1): {visual_transitions}")
    print(f"Quire boundaries (0/1):   {quire_boundaries}")

    # Count co-occurrences
    n_both = sum(1 for v, q in zip(visual_transitions, quire_boundaries) if v == 1 and q == 1)
    n_visual_only = sum(1 for v, q in zip(visual_transitions, quire_boundaries) if v == 1 and q == 0)
    n_quire_only = sum(1 for v, q in zip(visual_transitions, quire_boundaries) if v == 0 and q == 1)
    n_neither = sum(1 for v, q in zip(visual_transitions, quire_boundaries) if v == 0 and q == 0)

    print(f"\nContingency table:")
    print(f"  Visual trans & Quire bound: {n_both}")
    print(f"  Visual trans only: {n_visual_only}")
    print(f"  Quire bound only: {n_quire_only}")
    print(f"  Neither: {n_neither}")

    # Fisher's exact test
    from scipy.stats import fisher_exact
    contingency = [[n_both, n_visual_only], [n_quire_only, n_neither]]
    odds_ratio, p_fisher = fisher_exact(contingency)

    print(f"\nFisher's exact test:")
    print(f"  Odds ratio: {odds_ratio:.4f}")
    print(f"  p-value: {p_fisher:.4f}")

    # Correlation test
    if sum(quire_boundaries) > 0:  # Only if there are quire boundaries
        rho, p_rho = stats.spearmanr(visual_transitions, quire_boundaries)
        print(f"\nSpearman correlation:")
        print(f"  rho: {rho:.4f}")
        print(f"  p-value: {p_rho:.4f}")
    else:
        rho, p_rho = 0.0, 1.0
        print(f"\nNo quire boundaries in data subset.")

    # Verdict
    if p_fisher < 0.05 and odds_ratio > 1:
        verdict = 'PASS'
        interpretation = 'Visual regime shifts align with quire boundaries'
    else:
        verdict = 'FAIL'
        interpretation = 'No alignment between visual shifts and quire boundaries'

    print(f"\n>>> TEST F VERDICT: {verdict}")
    print(f"    {interpretation}")

    return {
        'n_both': n_both,
        'n_visual_only': n_visual_only,
        'n_quire_only': n_quire_only,
        'n_neither': n_neither,
        'odds_ratio': float(odds_ratio),
        'fisher_p': float(p_fisher),
        'spearman_rho': float(rho),
        'spearman_p': float(p_rho),
        'verdict': verdict,
        'interpretation': interpretation
    }


def run_test_g(folio_metadata: dict, folio_middles: dict, folios_sorted: list):
    """
    Test G: Multi-Folio Perceptual Scaffolding

    Do visual "runs" (consecutive folios in same cluster) show consistent
    within-run constraint patterns vs between-run?

    Hypothesis: Images establish visual regime that persists, with text
    providing discrimination WITHIN that regime.
    """
    print("\n" + "=" * 60)
    print("TEST G: Multi-Folio Perceptual Scaffolding")
    print("=" * 60)

    # Build visual cluster sequence
    visual_seq = [folio_metadata[f]['visual_cluster'] for f in folios_sorted]

    # Identify runs (consecutive folios with same visual cluster)
    runs = []
    current_run_start = 0
    current_cluster = visual_seq[0]

    for i in range(1, len(visual_seq)):
        if visual_seq[i] != current_cluster:
            runs.append({
                'cluster': current_cluster,
                'folios': folios_sorted[current_run_start:i],
                'start': current_run_start,
                'end': i - 1,
                'length': i - current_run_start
            })
            current_run_start = i
            current_cluster = visual_seq[i]

    # Don't forget the last run
    runs.append({
        'cluster': current_cluster,
        'folios': folios_sorted[current_run_start:],
        'start': current_run_start,
        'end': len(visual_seq) - 1,
        'length': len(visual_seq) - current_run_start
    })

    print(f"\nIdentified {len(runs)} visual runs:")
    multi_folio_runs = [r for r in runs if r['length'] > 1]
    print(f"  Multi-folio runs (length > 1): {len(multi_folio_runs)}")

    for run in runs:
        print(f"  Cluster {run['cluster']}: {run['folios']} (length {run['length']})")

    # Compute within-run MIDDLE similarity
    within_run_similarities = []
    for run in multi_folio_runs:
        run_folios = run['folios']
        for f1, f2 in combinations(run_folios, 2):
            m1 = set(folio_middles.get(f1, {}).keys())
            m2 = set(folio_middles.get(f2, {}).keys())
            sim = compute_jaccard(m1, m2)
            within_run_similarities.append(sim)

    # Compute between-run MIDDLE similarity (adjacent runs only)
    between_run_similarities = []
    for i in range(len(runs) - 1):
        run1_folios = runs[i]['folios']
        run2_folios = runs[i+1]['folios']

        # Compare last folio of run1 with first folio of run2
        f1 = run1_folios[-1]
        f2 = run2_folios[0]
        m1 = set(folio_middles.get(f1, {}).keys())
        m2 = set(folio_middles.get(f2, {}).keys())
        sim = compute_jaccard(m1, m2)
        between_run_similarities.append(sim)

    print(f"\nWithin-run pairs: {len(within_run_similarities)}")
    print(f"Between-run pairs: {len(between_run_similarities)}")

    if within_run_similarities:
        print(f"\nWithin-run MIDDLE similarity:")
        print(f"  Mean: {np.mean(within_run_similarities):.4f}")
        print(f"  Std: {np.std(within_run_similarities):.4f}")

    if between_run_similarities:
        print(f"\nBetween-run MIDDLE similarity:")
        print(f"  Mean: {np.mean(between_run_similarities):.4f}")
        print(f"  Std: {np.std(between_run_similarities):.4f}")

    # Test: Is within-run similarity > between-run similarity?
    if within_run_similarities and between_run_similarities:
        u_stat, p_mann = stats.mannwhitneyu(
            within_run_similarities, between_run_similarities,
            alternative='greater'
        )

        effect_size = np.mean(within_run_similarities) - np.mean(between_run_similarities)

        print(f"\nMann-Whitney U test (within > between):")
        print(f"  U statistic: {u_stat}")
        print(f"  p-value: {p_mann:.4f}")
        print(f"  Effect size: {effect_size:.4f}")

        if p_mann < 0.05 and effect_size > 0:
            verdict = 'PASS'
            interpretation = 'Within-run constraint similarity exceeds between-run'
        else:
            verdict = 'FAIL'
            interpretation = 'No scaffolding effect detected'
    else:
        u_stat, p_mann = 0, 1.0
        effect_size = 0
        verdict = 'INSUFFICIENT_DATA'
        interpretation = 'Not enough data for comparison'

    print(f"\n>>> TEST G VERDICT: {verdict}")
    print(f"    {interpretation}")

    return {
        'n_runs': len(runs),
        'n_multi_folio_runs': len(multi_folio_runs),
        'within_run_pairs': len(within_run_similarities),
        'between_run_pairs': len(between_run_similarities),
        'within_run_mean': float(np.mean(within_run_similarities)) if within_run_similarities else 0,
        'between_run_mean': float(np.mean(between_run_similarities)) if between_run_similarities else 0,
        'mann_whitney_u': float(u_stat),
        'mann_whitney_p': float(p_mann),
        'effect_size': float(effect_size),
        'verdict': verdict,
        'interpretation': interpretation
    }


def run_test_h(folio_metadata: dict, folios_sorted: list):
    """
    Test H: Negative Geometric Test

    Explicitly document absence of fold/overlay/composite signals.
    Pre-empts fringe interpretations.
    """
    print("\n" + "=" * 60)
    print("TEST H: Negative Geometric Test")
    print("=" * 60)

    results = {}

    # H1: Fold Symmetry Test
    # If pages were meant to be folded, first half should mirror second half
    print("\n--- H1: Fold Symmetry Test ---")
    n = len(folios_sorted)
    mid = n // 2

    first_half_clusters = [folio_metadata[f]['visual_cluster'] for f in folios_sorted[:mid]]
    second_half_clusters = [folio_metadata[f]['visual_cluster'] for f in folios_sorted[mid:]]
    second_half_reversed = second_half_clusters[::-1]

    # Truncate to same length
    min_len = min(len(first_half_clusters), len(second_half_reversed))
    first_half_clusters = first_half_clusters[:min_len]
    second_half_reversed = second_half_reversed[:min_len]

    # Count matches
    fold_matches = sum(1 for a, b in zip(first_half_clusters, second_half_reversed) if a == b)
    fold_expected = min_len / len(set(first_half_clusters + second_half_reversed))  # Expected by chance

    print(f"  Comparing first {min_len} folios with reversed last {min_len}")
    print(f"  Fold matches: {fold_matches}/{min_len}")
    print(f"  Expected by chance: {fold_expected:.1f}")

    # Permutation test
    n_perms = 10000
    perm_matches = []
    for _ in range(n_perms):
        shuffled = list(second_half_reversed)
        np.random.shuffle(shuffled)
        matches = sum(1 for a, b in zip(first_half_clusters, shuffled) if a == b)
        perm_matches.append(matches)

    p_fold = sum(1 for m in perm_matches if m >= fold_matches) / n_perms

    print(f"  Permutation p-value: {p_fold:.4f}")
    print(f"  Interpretation: {'FOLD SIGNAL' if p_fold < 0.05 else 'NO FOLD SIGNAL'}")

    results['fold_symmetry'] = {
        'matches': fold_matches,
        'total': min_len,
        'expected': float(fold_expected),
        'p_value': float(p_fold),
        'signal': bool(p_fold < 0.05)
    }

    # H2: Overlay/Superposition Test
    # If pages were meant to be overlaid, adjacent pages should have complementary patterns
    print("\n--- H2: Overlay/Superposition Test ---")

    # Test if recto-verso pairs have systematically different or complementary patterns
    recto_clusters = []
    verso_clusters = []

    for folio in folios_sorted:
        cluster = folio_metadata[folio]['visual_cluster']
        if folio.endswith('r'):
            recto_clusters.append(cluster)
        else:
            verso_clusters.append(cluster)

    # Test if recto and verso have different distributions
    if recto_clusters and verso_clusters:
        u_stat, p_recto_verso = stats.mannwhitneyu(recto_clusters, verso_clusters, alternative='two-sided')

        print(f"  Recto mean cluster: {np.mean(recto_clusters):.2f}")
        print(f"  Verso mean cluster: {np.mean(verso_clusters):.2f}")
        print(f"  Mann-Whitney p-value: {p_recto_verso:.4f}")
        print(f"  Interpretation: {'RECTO/VERSO DIFFERENCE' if p_recto_verso < 0.05 else 'NO SYSTEMATIC DIFFERENCE'}")

        results['recto_verso'] = {
            'recto_mean': float(np.mean(recto_clusters)),
            'verso_mean': float(np.mean(verso_clusters)),
            'p_value': float(p_recto_verso),
            'signal': bool(p_recto_verso < 0.05)
        }
    else:
        print("  Insufficient recto/verso data")
        results['recto_verso'] = {'signal': False}

    # H3: Composite/Assembly Test
    # If pages were meant to be assembled, specific page positions should show patterns
    print("\n--- H3: Composite/Assembly Test ---")

    # Test if page position (ordinal) correlates with visual cluster
    positions = list(range(len(folios_sorted)))
    clusters = [folio_metadata[f]['visual_cluster'] for f in folios_sorted]

    rho_pos, p_pos = stats.spearmanr(positions, clusters)

    print(f"  Position-Cluster Spearman rho: {rho_pos:.4f}")
    print(f"  p-value: {p_pos:.4f}")
    print(f"  Interpretation: {'POSITIONAL PATTERN' if p_pos < 0.05 else 'NO POSITIONAL PATTERN'}")

    results['position_cluster'] = {
        'spearman_rho': float(rho_pos),
        'p_value': float(p_pos),
        'signal': bool(p_pos < 0.05)
    }

    # H4: Modular/Periodic Test
    # If pages were meant to be viewed in groups, visual clusters would show periodicity
    print("\n--- H4: Modular/Periodic Test ---")

    # Test for periodicity at common periods (2, 3, 4, 5)
    periodic_signals = {}
    for period in [2, 3, 4, 5]:
        groups = [[] for _ in range(period)]
        for i, cluster in enumerate(clusters):
            groups[i % period].append(cluster)

        # ANOVA-like test: do groups differ?
        if all(len(g) > 1 for g in groups):
            h_stat, p_kruskal = stats.kruskal(*groups)
            periodic_signals[period] = {
                'h_stat': float(h_stat),
                'p_value': float(p_kruskal),
                'signal': bool(p_kruskal < 0.05)
            }
            print(f"  Period {period}: H={h_stat:.2f}, p={p_kruskal:.4f} {'*SIGNAL*' if p_kruskal < 0.05 else ''}")

    results['periodicity'] = periodic_signals

    # Apply Bonferroni correction for periodicity tests (4 tests)
    bonferroni_threshold = 0.05 / 4  # = 0.0125
    any_periodic_signal_corrected = any(
        v.get('p_value', 1.0) < bonferroni_threshold for v in periodic_signals.values()
    )

    print(f"\n  Bonferroni-corrected threshold: {bonferroni_threshold:.4f}")
    print(f"  Any signal survives correction: {any_periodic_signal_corrected}")

    # Summary
    print("\n--- SUMMARY ---")
    any_geometric_signal = (
        results['fold_symmetry']['signal'] or
        results.get('recto_verso', {}).get('signal', False) or
        results['position_cluster']['signal'] or
        any_periodic_signal_corrected  # Use corrected version
    )

    if any_geometric_signal:
        verdict = 'SIGNAL_DETECTED'
        interpretation = 'Unexpected geometric pattern detected - requires investigation'
    else:
        verdict = 'NO_SIGNAL'
        interpretation = 'No fold/overlay/composite/periodic geometric signals detected'

    print(f"\n>>> TEST H VERDICT: {verdict}")
    print(f"    {interpretation}")

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    return results


def main():
    """Run all remaining tests."""
    print("ILL-TOP-1 Tests F, G, H: Remaining Order/Geometry Tests")
    print("=" * 60)

    # Load data
    with open(OUTPUT_DIR / 'folio_metadata.json', 'r') as f:
        folio_metadata = json.load(f)

    with open(OUTPUT_DIR / 'folio_middle_distributions.json', 'r') as f:
        folio_middles = json.load(f)

    # Sort folios
    folios_sorted = sorted(folio_metadata.keys(), key=extract_folio_number)

    print(f"\nAnalyzing {len(folios_sorted)} folios")
    print(f"First: {folios_sorted[0]}, Last: {folios_sorted[-1]}")

    # Run tests
    results = {}

    results['test_f'] = run_test_f(folio_metadata, folios_sorted)
    results['test_g'] = run_test_g(folio_metadata, folio_middles, folios_sorted)
    results['test_h'] = run_test_h(folio_metadata, folios_sorted)

    # Overall summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    print(f"\nTest F (Quire-level regime articulation): {results['test_f']['verdict']}")
    print(f"Test G (Multi-folio perceptual scaffolding): {results['test_g']['verdict']}")
    print(f"Test H (Negative geometric test): {results['test_h']['verdict']}")

    # Save results
    with open(OUTPUT_DIR / 'test_f_g_h_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to test_f_g_h_results.json")

    return results


if __name__ == '__main__':
    main()
