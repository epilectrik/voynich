#!/usr/bin/env python3
"""
ILL-TOP-1: Execute All Four Tests

Test A: Visual-MIDDLE cluster correspondence (PRIMARY)
Test B: Section-PREFIX alignment vs null (all folios are H, so this is MOOT)
Test C: Schematic-Hub correlation
Test D: Mismatch as evidence (dissimilar-but-compatible -> hub regions)
"""

import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
from itertools import combinations
import random
from scipy import stats

# Paths
OUTPUT_DIR = Path(__file__).parent

# Hub MIDDLEs (from SSD-PHY-1a)
HUB_MIDDLES = {'a', 'o', 'e', 'ee', 'eo'}


def load_data():
    """Load extracted data."""
    with open(OUTPUT_DIR / 'folio_middle_distributions.json', 'r') as f:
        folio_middles = json.load(f)
    with open(OUTPUT_DIR / 'folio_prefix_distributions.json', 'r') as f:
        folio_prefixes = json.load(f)
    with open(OUTPUT_DIR / 'folio_metadata.json', 'r') as f:
        folio_metadata = json.load(f)
    return folio_middles, folio_prefixes, folio_metadata


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def compute_middle_overlap(middles1: Dict, middles2: Dict) -> float:
    """
    Compute MIDDLE overlap between two folios.
    Uses Jaccard on MIDDLE type sets.
    """
    set1 = set(middles1.keys())
    set2 = set(middles2.keys())
    return jaccard_similarity(set1, set2)


def run_test_a(folio_middles: Dict, folio_metadata: Dict) -> dict:
    """
    Test A: Visual-MIDDLE Cluster Correspondence (PRIMARY)

    Question: When illustrations look visually similar, is the constraint space similar?

    Method:
    - Build visual similarity matrix (same cluster = 1)
    - Build MIDDLE overlap matrix (Jaccard on MIDDLE sets)
    - Compute Mantel-style correlation
    """
    print("\n" + "=" * 60)
    print("TEST A: Visual-MIDDLE Cluster Correspondence")
    print("=" * 60)

    folios = list(folio_middles.keys())
    n = len(folios)

    # Build matrices
    visual_sim = np.zeros((n, n))
    middle_overlap = np.zeros((n, n))

    for i, f1 in enumerate(folios):
        for j, f2 in enumerate(folios):
            if i == j:
                visual_sim[i, j] = 1.0
                middle_overlap[i, j] = 1.0
            else:
                # Visual similarity: same cluster = 1, different = 0
                c1 = folio_metadata[f1]['visual_cluster']
                c2 = folio_metadata[f2]['visual_cluster']
                visual_sim[i, j] = 1.0 if c1 == c2 else 0.0

                # MIDDLE overlap: Jaccard similarity
                middle_overlap[i, j] = compute_middle_overlap(
                    folio_middles[f1], folio_middles[f2]
                )

    # Extract upper triangle (excluding diagonal) for correlation
    upper_idx = np.triu_indices(n, k=1)
    visual_flat = visual_sim[upper_idx]
    middle_flat = middle_overlap[upper_idx]

    # Basic statistics
    same_cluster_pairs = visual_flat == 1.0
    diff_cluster_pairs = visual_flat == 0.0

    same_cluster_overlap = middle_flat[same_cluster_pairs]
    diff_cluster_overlap = middle_flat[diff_cluster_pairs]

    print(f"\nPairwise Statistics:")
    print(f"  Total pairs: {len(visual_flat)}")
    print(f"  Same-cluster pairs: {sum(same_cluster_pairs)}")
    print(f"  Different-cluster pairs: {sum(diff_cluster_pairs)}")

    if len(same_cluster_overlap) > 0:
        print(f"\n  Same-cluster MIDDLE overlap: mean={np.mean(same_cluster_overlap):.4f}, "
              f"std={np.std(same_cluster_overlap):.4f}")
    if len(diff_cluster_overlap) > 0:
        print(f"  Diff-cluster MIDDLE overlap: mean={np.mean(diff_cluster_overlap):.4f}, "
              f"std={np.std(diff_cluster_overlap):.4f}")

    # Statistical test: Mann-Whitney U (are same-cluster overlaps higher?)
    if len(same_cluster_overlap) > 1 and len(diff_cluster_overlap) > 1:
        stat, p_value = stats.mannwhitneyu(
            same_cluster_overlap, diff_cluster_overlap,
            alternative='greater'
        )
        effect_size = np.mean(same_cluster_overlap) - np.mean(diff_cluster_overlap)

        print(f"\nMann-Whitney U test (same > diff):")
        print(f"  U statistic: {stat}")
        print(f"  p-value: {p_value:.6f}")
        print(f"  Effect size (mean diff): {effect_size:.4f}")

        # Also compute Spearman correlation on full matrices
        rho, p_spearman = stats.spearmanr(visual_flat, middle_flat)
        print(f"\nSpearman correlation:")
        print(f"  rho: {rho:.4f}")
        print(f"  p-value: {p_spearman:.6f}")

        # Permutation test for robustness
        n_perms = 10000
        observed_diff = np.mean(same_cluster_overlap) - np.mean(diff_cluster_overlap)
        perm_diffs = []

        all_overlaps = list(same_cluster_overlap) + list(diff_cluster_overlap)
        n_same = len(same_cluster_overlap)

        for _ in range(n_perms):
            random.shuffle(all_overlaps)
            perm_same = all_overlaps[:n_same]
            perm_diff = all_overlaps[n_same:]
            perm_diffs.append(np.mean(perm_same) - np.mean(perm_diff))

        p_perm = sum(1 for d in perm_diffs if d >= observed_diff) / n_perms

        print(f"\nPermutation test (10,000 permutations):")
        print(f"  Observed diff: {observed_diff:.4f}")
        print(f"  p-value: {p_perm:.4f}")

        result = {
            'same_cluster_mean': float(np.mean(same_cluster_overlap)),
            'diff_cluster_mean': float(np.mean(diff_cluster_overlap)),
            'effect_size': float(effect_size),
            'mannwhitney_p': float(p_value),
            'spearman_rho': float(rho),
            'spearman_p': float(p_spearman),
            'permutation_p': float(p_perm),
            'verdict': 'PASS' if p_perm < 0.05 and effect_size > 0 else 'FAIL'
        }
    else:
        result = {
            'error': 'Insufficient data for statistical test',
            'verdict': 'INCONCLUSIVE'
        }

    print(f"\n>>> TEST A VERDICT: {result['verdict']}")
    return result


def run_test_b(folio_metadata: Dict) -> dict:
    """
    Test B: Section-PREFIX Alignment

    NOTE: All 29 coded folios are Section H, so this test cannot discriminate.
    This is documented as MOOT.
    """
    print("\n" + "=" * 60)
    print("TEST B: Section-PREFIX Alignment vs Null")
    print("=" * 60)

    sections = [m['section'] for m in folio_metadata.values()]
    unique_sections = set(sections)

    print(f"\nSection distribution: {Counter(sections)}")
    print(f"\nNOTE: All {len(sections)} coded folios are Section H.")
    print("This test cannot discriminate - no section variance exists.")

    result = {
        'sections': dict(Counter(sections)),
        'verdict': 'MOOT',
        'reason': 'All coded folios are Section H. No section variance to test.'
    }

    print(f"\n>>> TEST B VERDICT: {result['verdict']} (no variance)")
    return result


def run_test_c(folio_metadata: Dict) -> dict:
    """
    Test C: Schematic-Hub Correlation

    Question: Do schematic illustrations correlate with hub-MIDDLE usage?
    """
    print("\n" + "=" * 60)
    print("TEST C: Schematic-Hub Correlation")
    print("=" * 60)

    schematic_scores = []
    hub_densities = []

    for folio, meta in folio_metadata.items():
        schematic_scores.append(meta['schematic_score'])
        hub_densities.append(meta['hub_density'])

    print(f"\nSchematic score distribution: {Counter(schematic_scores)}")
    print(f"Hub density range: {min(hub_densities):.3f} - {max(hub_densities):.3f}")

    # Group by schematic score
    by_score = defaultdict(list)
    for s, h in zip(schematic_scores, hub_densities):
        by_score[s].append(h)

    print(f"\nHub density by schematic score:")
    for score in sorted(by_score.keys()):
        densities = by_score[score]
        print(f"  Score {score}: n={len(densities)}, "
              f"mean={np.mean(densities):.3f}, std={np.std(densities):.3f}")

    # Spearman correlation
    rho, p_value = stats.spearmanr(schematic_scores, hub_densities)

    print(f"\nSpearman correlation:")
    print(f"  rho: {rho:.4f}")
    print(f"  p-value: {p_value:.6f}")

    # Interpretation
    if p_value < 0.05 and rho > 0:
        verdict = 'PASS'
        interpretation = 'Significant positive correlation: schematic -> higher hub density'
    elif p_value < 0.05 and rho < 0:
        verdict = 'FAIL'
        interpretation = 'Significant NEGATIVE correlation (opposite of prediction)'
    else:
        verdict = 'FAIL'
        interpretation = 'No significant correlation'

    result = {
        'schematic_distribution': dict(Counter(schematic_scores)),
        'by_score_means': {str(k): float(np.mean(v)) for k, v in by_score.items()},
        'spearman_rho': float(rho),
        'spearman_p': float(p_value),
        'interpretation': interpretation,
        'verdict': verdict
    }

    print(f"\n>>> TEST C VERDICT: {result['verdict']}")
    print(f"    {interpretation}")
    return result


def run_test_d(folio_middles: Dict, folio_metadata: Dict) -> dict:
    """
    Test D: Mismatch as Evidence

    Question: If visually dissimilar plants map to similar constraint regimes,
    does this support regime-level interpretation?

    Method:
    - Find pairs that are visually DISSIMILAR but have HIGH MIDDLE overlap
    - Check if these pairs concentrate in hub-dense regions
    """
    print("\n" + "=" * 60)
    print("TEST D: Mismatch as Evidence (Dissimilar-but-Compatible)")
    print("=" * 60)

    folios = list(folio_middles.keys())

    # Compute all pairwise data
    pairs_data = []
    for f1, f2 in combinations(folios, 2):
        c1 = folio_metadata[f1]['visual_cluster']
        c2 = folio_metadata[f2]['visual_cluster']
        visual_dissimilar = c1 != c2

        overlap = compute_middle_overlap(folio_middles[f1], folio_middles[f2])

        # Combined hub density of the pair
        hub_pair = (folio_metadata[f1]['hub_density'] + folio_metadata[f2]['hub_density']) / 2

        pairs_data.append({
            'f1': f1, 'f2': f2,
            'visual_dissimilar': visual_dissimilar,
            'middle_overlap': overlap,
            'hub_density': hub_pair
        })

    # Define thresholds
    # "High overlap" = above median
    overlaps = [p['middle_overlap'] for p in pairs_data]
    overlap_median = np.median(overlaps)
    overlap_75 = np.percentile(overlaps, 75)

    print(f"\nMIDDLE overlap distribution:")
    print(f"  Min: {min(overlaps):.4f}")
    print(f"  Median: {overlap_median:.4f}")
    print(f"  75th percentile: {overlap_75:.4f}")
    print(f"  Max: {max(overlaps):.4f}")

    # Categorize pairs
    similar_compatible = []  # visual similar, high overlap
    similar_incompatible = []  # visual similar, low overlap
    dissimilar_compatible = []  # visual dissimilar, high overlap (KEY)
    dissimilar_incompatible = []  # visual dissimilar, low overlap

    for p in pairs_data:
        high_overlap = p['middle_overlap'] >= overlap_median

        if not p['visual_dissimilar'] and high_overlap:
            similar_compatible.append(p)
        elif not p['visual_dissimilar'] and not high_overlap:
            similar_incompatible.append(p)
        elif p['visual_dissimilar'] and high_overlap:
            dissimilar_compatible.append(p)  # KEY GROUP
        else:
            dissimilar_incompatible.append(p)

    print(f"\nPair categorization (overlap threshold = median):")
    print(f"  Similar & Compatible: {len(similar_compatible)}")
    print(f"  Similar & Incompatible: {len(similar_incompatible)}")
    print(f"  Dissimilar & Compatible: {len(dissimilar_compatible)} [KEY]")
    print(f"  Dissimilar & Incompatible: {len(dissimilar_incompatible)}")

    # KEY TEST: Do dissimilar-compatible pairs have higher hub density?
    if len(dissimilar_compatible) > 0:
        dc_hub = [p['hub_density'] for p in dissimilar_compatible]
        other_hub = [p['hub_density'] for p in dissimilar_incompatible + similar_incompatible]

        print(f"\nHub density comparison:")
        print(f"  Dissimilar-Compatible: mean={np.mean(dc_hub):.4f}, n={len(dc_hub)}")
        print(f"  Other pairs: mean={np.mean(other_hub):.4f}, n={len(other_hub)}")

        if len(dc_hub) > 1 and len(other_hub) > 1:
            stat, p_value = stats.mannwhitneyu(dc_hub, other_hub, alternative='greater')
            print(f"\n  Mann-Whitney U (DC > others): U={stat}, p={p_value:.6f}")

            # Effect size
            effect = np.mean(dc_hub) - np.mean(other_hub)
            print(f"  Effect size: {effect:.4f}")

            # Interpretation per pre-registered prediction:
            # Dissimilar-but-compatible pairs existing supports REGIME model
            # If they concentrate in hub regions, STRONGLY supports REGIME
            dc_exists = len(dissimilar_compatible) > 0
            dc_hub_concentrated = effect > 0 and p_value < 0.1  # more lenient

            if dc_exists and dc_hub_concentrated:
                verdict = 'PASS'
                interpretation = 'Dissimilar-compatible pairs exist AND concentrate in hub regions'
            elif dc_exists:
                verdict = 'PARTIAL'
                interpretation = 'Dissimilar-compatible pairs exist but no hub concentration'
            else:
                verdict = 'FAIL'
                interpretation = 'No dissimilar-compatible pairs found'

            result = {
                'dissimilar_compatible_count': len(dissimilar_compatible),
                'dc_hub_mean': float(np.mean(dc_hub)),
                'other_hub_mean': float(np.mean(other_hub)),
                'effect_size': float(effect),
                'mannwhitney_p': float(p_value),
                'interpretation': interpretation,
                'verdict': verdict
            }
        else:
            result = {
                'dissimilar_compatible_count': len(dissimilar_compatible),
                'verdict': 'INCONCLUSIVE',
                'reason': 'Insufficient data for statistical test'
            }
    else:
        result = {
            'dissimilar_compatible_count': 0,
            'verdict': 'FAIL',
            'interpretation': 'No dissimilar-compatible pairs found'
        }

    print(f"\n>>> TEST D VERDICT: {result['verdict']}")
    if 'interpretation' in result:
        print(f"    {result['interpretation']}")

    return result


def main():
    print("=" * 60)
    print("ILL-TOP-1: EXECUTE ALL TESTS")
    print("=" * 60)

    # Load data
    folio_middles, folio_prefixes, folio_metadata = load_data()
    print(f"\nLoaded data for {len(folio_middles)} folios")

    # Run all tests
    results = {}

    results['test_a'] = run_test_a(folio_middles, folio_metadata)
    results['test_b'] = run_test_b(folio_metadata)
    results['test_c'] = run_test_c(folio_metadata)
    results['test_d'] = run_test_d(folio_middles, folio_metadata)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = {
        'A': results['test_a']['verdict'],
        'B': results['test_b']['verdict'],
        'C': results['test_c']['verdict'],
        'D': results['test_d']['verdict'],
    }

    print(f"\nTest Verdicts:")
    for test, verdict in verdicts.items():
        print(f"  Test {test}: {verdict}")

    # Overall interpretation per matrix
    # CRITICAL: If Test A fails, overall is MISMATCH
    if verdicts['A'] == 'FAIL':
        overall = 'MISMATCH'
        reason = 'Primary test (A) failed - parallel indexing falsified'
    elif verdicts['A'] == 'PASS':
        # Count other passes (excluding MOOT)
        other_passes = sum(1 for t in ['C', 'D'] if verdicts[t] == 'PASS')
        if other_passes == 2:
            overall = 'STRONG_MATCH'
            reason = 'All applicable tests pass'
        elif other_passes == 1:
            overall = 'PARTIAL'
            reason = 'Primary passes, one secondary passes'
        else:
            overall = 'WEAK'
            reason = 'Only primary test passes'
    else:
        overall = 'INCONCLUSIVE'
        reason = 'Primary test inconclusive'

    print(f"\n>>> OVERALL VERDICT: {overall}")
    print(f"    {reason}")

    results['overall'] = {
        'verdict': overall,
        'reason': reason,
        'verdicts': verdicts
    }

    # Save results
    with open(OUTPUT_DIR / 'test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to test_results.json")

    return results


if __name__ == '__main__':
    main()
