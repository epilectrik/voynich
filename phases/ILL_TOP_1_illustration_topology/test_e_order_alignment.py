#!/usr/bin/env python3
"""
ILL-TOP-1 Test E: Order-Preserving Regime Alignment

Question: Do illustrations and Currier A traverse the SAME regime sequence
across the manuscript, possibly at different resolutions?

This tests a DIFFERENT hypothesis than topology correspondence:
- Not: do similar images have similar constraints?
- But: do they traverse the same sequence in the same ORDER?

Example of what this would look like:
  Illustrations (coarse): R1  R2  R3  R4
  Currier A (fine):       R1 R1  R2 R2  R3 R3  R4 R4

Method:
1. Sort folios by manuscript order
2. Extract visual cluster sequence (illustration regimes)
3. Extract constraint-derived regime sequence (A regimes)
4. Test for order-preserving correlation (allowing expansion)
"""

import json
import re
import numpy as np
from pathlib import Path
from scipy import stats
from collections import defaultdict, Counter

OUTPUT_DIR = Path(__file__).parent


def extract_folio_number(folio: str) -> tuple:
    """
    Extract sortable folio number.
    f1r -> (1, 'r'), f10v -> (10, 'v'), etc.
    """
    match = re.match(r'f(\d+)([rv])', folio)
    if match:
        num = int(match.group(1))
        side = match.group(2)
        # recto before verso
        side_order = 0 if side == 'r' else 1
        return (num, side_order)
    return (999, 0)


def assign_hub_regime(hub_density: float) -> int:
    """
    Assign hub density to regime bands.
    Low (0), Medium (1), High (2)
    """
    if hub_density < 0.20:
        return 0  # LOW hub
    elif hub_density < 0.30:
        return 1  # MEDIUM hub
    else:
        return 2  # HIGH hub


def compute_run_length_correlation(seq1, seq2):
    """
    Test if two sequences show order-preserving alignment,
    allowing for expansion/repetition.

    Uses run-length encoding to handle repetition.
    """
    # Run-length encode both sequences
    def run_length_encode(seq):
        if not seq:
            return []
        runs = []
        current = seq[0]
        count = 1
        for item in seq[1:]:
            if item == current:
                count += 1
            else:
                runs.append((current, count))
                current = item
                count = 1
        runs.append((current, count))
        return runs

    rle1 = run_length_encode(seq1)
    rle2 = run_length_encode(seq2)

    # Extract just the regime sequence (without counts)
    regime_seq1 = [r[0] for r in rle1]
    regime_seq2 = [r[0] for r in rle2]

    return regime_seq1, regime_seq2, rle1, rle2


def longest_common_subsequence(seq1, seq2):
    """
    Compute LCS length between two sequences.
    """
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]


def assign_diversity_regime(unique_middles: int) -> int:
    """
    Assign MIDDLE diversity to regime bands.
    Low (0), Medium (1), High (2)
    """
    if unique_middles < 40:
        return 0  # LOW diversity
    elif unique_middles < 55:
        return 1  # MEDIUM diversity
    else:
        return 2  # HIGH diversity


def run_test_e():
    """
    Test E: Order-Preserving Regime Alignment
    """
    print("=" * 60)
    print("TEST E: Order-Preserving Regime Alignment")
    print("=" * 60)

    # Load data
    with open(OUTPUT_DIR / 'folio_metadata.json', 'r') as f:
        folio_metadata = json.load(f)

    with open(OUTPUT_DIR / 'folio_prefix_distributions.json', 'r') as f:
        folio_prefixes = json.load(f)

    # Sort folios by manuscript order
    folios_sorted = sorted(folio_metadata.keys(), key=extract_folio_number)

    print(f"\nFolios in manuscript order ({len(folios_sorted)} total):")
    print(f"  First: {folios_sorted[0]}, Last: {folios_sorted[-1]}")

    # Extract sequences
    visual_cluster_seq = []
    hub_regime_seq = []
    diversity_regime_seq = []
    dominant_prefix_seq = []

    for folio in folios_sorted:
        meta = folio_metadata[folio]

        # Visual cluster (illustration regime)
        visual_cluster_seq.append(meta['visual_cluster'])

        # Hub density regime (A-derived)
        hub_regime = assign_hub_regime(meta['hub_density'])
        hub_regime_seq.append(hub_regime)

        # MIDDLE diversity regime (A-derived - alternative)
        diversity_regime = assign_diversity_regime(meta['unique_middles'])
        diversity_regime_seq.append(diversity_regime)

        # Dominant PREFIX (A-derived)
        if folio in folio_prefixes and folio_prefixes[folio]:
            dom_prefix = max(folio_prefixes[folio], key=folio_prefixes[folio].get)
            dominant_prefix_seq.append(dom_prefix)
        else:
            dominant_prefix_seq.append('none')

    print(f"\n--- VISUAL CLUSTER SEQUENCE (Illustration Regimes) ---")
    print(f"  {visual_cluster_seq}")
    print(f"  Unique values: {sorted(set(visual_cluster_seq))}")

    print(f"\n--- HUB REGIME SEQUENCE (A-derived: 0=Low, 1=Med, 2=High) ---")
    print(f"  {hub_regime_seq}")
    print(f"  Distribution: {dict(Counter(hub_regime_seq))}")

    print(f"\n--- DOMINANT PREFIX SEQUENCE (A-derived) ---")
    print(f"  {dominant_prefix_seq}")
    print(f"  Distribution: {dict(Counter(dominant_prefix_seq))}")

    # Test 1: Raw Spearman correlation on visual vs hub regime
    rho_raw, p_raw = stats.spearmanr(visual_cluster_seq, hub_regime_seq)
    print(f"\n--- TEST 1: Raw Spearman (Visual Cluster vs Hub Regime) ---")
    print(f"  rho: {rho_raw:.4f}")
    print(f"  p-value: {p_raw:.4f}")

    # Test 2: Run-length encoded correlation
    visual_rle_seq, hub_rle_seq, visual_rle, hub_rle = compute_run_length_correlation(
        visual_cluster_seq, hub_regime_seq
    )

    print(f"\n--- TEST 2: Run-Length Encoded Sequences ---")
    print(f"  Visual RLE: {len(visual_rle)} runs from {len(visual_cluster_seq)} items")
    print(f"  Hub RLE: {len(hub_rle)} runs from {len(hub_regime_seq)} items")

    # Test 3: LCS as fraction of shorter sequence
    lcs_len = longest_common_subsequence(visual_rle_seq, hub_rle_seq)
    min_len = min(len(visual_rle_seq), len(hub_rle_seq))
    lcs_ratio = lcs_len / min_len if min_len > 0 else 0

    print(f"\n--- TEST 3: Longest Common Subsequence ---")
    print(f"  LCS length: {lcs_len}")
    print(f"  Shorter sequence length: {min_len}")
    print(f"  LCS ratio: {lcs_ratio:.4f}")

    # Test 4: Permutation test for LCS
    n_perms = 10000
    perm_lcs_ratios = []

    for _ in range(n_perms):
        shuffled_hub = list(hub_rle_seq)
        np.random.shuffle(shuffled_hub)
        perm_lcs = longest_common_subsequence(visual_rle_seq, shuffled_hub)
        perm_lcs_ratios.append(perm_lcs / min_len if min_len > 0 else 0)

    p_lcs = sum(1 for r in perm_lcs_ratios if r >= lcs_ratio) / n_perms

    print(f"\n--- TEST 4: LCS Permutation Test ({n_perms} permutations) ---")
    print(f"  Observed LCS ratio: {lcs_ratio:.4f}")
    print(f"  Mean random LCS ratio: {np.mean(perm_lcs_ratios):.4f}")
    print(f"  p-value: {p_lcs:.4f}")

    # Test 5: Adjacent folio correlation
    # Do adjacent folios tend to have same visual cluster AND same hub regime?
    adjacent_visual_same = sum(1 for i in range(len(visual_cluster_seq)-1)
                               if visual_cluster_seq[i] == visual_cluster_seq[i+1])
    adjacent_hub_same = sum(1 for i in range(len(hub_regime_seq)-1)
                           if hub_regime_seq[i] == hub_regime_seq[i+1])

    # Do transitions in visual cluster correlate with transitions in hub regime?
    visual_transitions = [1 if visual_cluster_seq[i] != visual_cluster_seq[i+1] else 0
                         for i in range(len(visual_cluster_seq)-1)]
    hub_transitions = [1 if hub_regime_seq[i] != hub_regime_seq[i+1] else 0
                      for i in range(len(hub_regime_seq)-1)]

    rho_transitions, p_transitions = stats.spearmanr(visual_transitions, hub_transitions)

    print(f"\n--- TEST 5: Transition Correlation ---")
    print(f"  Adjacent same visual cluster: {adjacent_visual_same}/{len(visual_cluster_seq)-1}")
    print(f"  Adjacent same hub regime: {adjacent_hub_same}/{len(hub_regime_seq)-1}")
    print(f"  Transition correlation (rho): {rho_transitions:.4f}")
    print(f"  Transition correlation (p): {p_transitions:.4f}")

    # Summary verdict
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Criteria for order-preserving alignment:
    # - LCS ratio significantly above chance OR
    # - Transition correlation significant

    order_preserved = (p_lcs < 0.05 and lcs_ratio > np.mean(perm_lcs_ratios) + 0.1) or \
                     (p_transitions < 0.05 and rho_transitions > 0.3)

    if order_preserved:
        verdict = 'PASS'
        interpretation = 'Order-preserving alignment detected'
    else:
        verdict = 'FAIL'
        interpretation = 'No order-preserving alignment detected'

    result = {
        'raw_spearman_rho': float(rho_raw),
        'raw_spearman_p': float(p_raw),
        'lcs_length': lcs_len,
        'lcs_ratio': float(lcs_ratio),
        'lcs_permutation_p': float(p_lcs),
        'mean_random_lcs_ratio': float(np.mean(perm_lcs_ratios)),
        'transition_correlation_rho': float(rho_transitions),
        'transition_correlation_p': float(p_transitions),
        'verdict': verdict,
        'interpretation': interpretation
    }

    print(f"\n>>> TEST E VERDICT: {verdict}")
    print(f"    {interpretation}")

    # ================================================================
    # PART 2: DIVERSITY REGIME (Alternative A-side definition)
    # ================================================================
    print("\n" + "=" * 60)
    print("ALTERNATIVE A-SIDE: MIDDLE DIVERSITY REGIME")
    print("=" * 60)

    print(f"\n--- DIVERSITY REGIME SEQUENCE (0=Low<40, 1=Med<55, 2=High) ---")
    print(f"  {diversity_regime_seq}")
    print(f"  Distribution: {dict(Counter(diversity_regime_seq))}")

    # Test 6: Raw Spearman on visual vs diversity regime
    rho_div, p_div = stats.spearmanr(visual_cluster_seq, diversity_regime_seq)
    print(f"\n--- TEST 6: Raw Spearman (Visual Cluster vs Diversity Regime) ---")
    print(f"  rho: {rho_div:.4f}")
    print(f"  p-value: {p_div:.4f}")

    # Test 7: RLE + LCS for diversity regime
    visual_rle_seq2, div_rle_seq, visual_rle2, div_rle = compute_run_length_correlation(
        visual_cluster_seq, diversity_regime_seq
    )

    print(f"\n--- TEST 7: Run-Length Encoded (Diversity) ---")
    print(f"  Visual RLE: {len(visual_rle2)} runs")
    print(f"  Diversity RLE: {len(div_rle)} runs")

    lcs_len_div = longest_common_subsequence(visual_rle_seq2, div_rle_seq)
    min_len_div = min(len(visual_rle_seq2), len(div_rle_seq))
    lcs_ratio_div = lcs_len_div / min_len_div if min_len_div > 0 else 0

    print(f"  LCS length: {lcs_len_div}")
    print(f"  LCS ratio: {lcs_ratio_div:.4f}")

    # Permutation test for diversity LCS
    perm_lcs_div = []
    for _ in range(n_perms):
        shuffled_div = list(div_rle_seq)
        np.random.shuffle(shuffled_div)
        perm_lcs = longest_common_subsequence(visual_rle_seq2, shuffled_div)
        perm_lcs_div.append(perm_lcs / min_len_div if min_len_div > 0 else 0)

    p_lcs_div = sum(1 for r in perm_lcs_div if r >= lcs_ratio_div) / n_perms

    print(f"\n--- TEST 8: Diversity LCS Permutation Test ---")
    print(f"  Observed LCS ratio: {lcs_ratio_div:.4f}")
    print(f"  Mean random LCS ratio: {np.mean(perm_lcs_div):.4f}")
    print(f"  p-value: {p_lcs_div:.4f}")

    # Test 9: Transition correlation for diversity
    div_transitions = [1 if diversity_regime_seq[i] != diversity_regime_seq[i+1] else 0
                      for i in range(len(diversity_regime_seq)-1)]

    rho_div_trans, p_div_trans = stats.spearmanr(visual_transitions, div_transitions)

    print(f"\n--- TEST 9: Diversity Transition Correlation ---")
    print(f"  Transition correlation (rho): {rho_div_trans:.4f}")
    print(f"  Transition correlation (p): {p_div_trans:.4f}")

    # ================================================================
    # OVERALL SUMMARY
    # ================================================================
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    # Check if either regime shows order-preserving alignment
    hub_order_preserved = (p_lcs < 0.05 and lcs_ratio > np.mean(perm_lcs_ratios) + 0.1) or \
                         (p_transitions < 0.05 and rho_transitions > 0.3)

    div_order_preserved = (p_lcs_div < 0.05 and lcs_ratio_div > np.mean(perm_lcs_div) + 0.1) or \
                         (p_div_trans < 0.05 and rho_div_trans > 0.3)

    print(f"\nHUB REGIME: {'PASS' if hub_order_preserved else 'FAIL'}")
    print(f"  LCS ratio: {lcs_ratio:.4f} (random: {np.mean(perm_lcs_ratios):.4f}, p={p_lcs:.4f})")
    print(f"  Transition rho: {rho_transitions:.4f} (p={p_transitions:.4f})")

    print(f"\nDIVERSITY REGIME: {'PASS' if div_order_preserved else 'FAIL'}")
    print(f"  LCS ratio: {lcs_ratio_div:.4f} (random: {np.mean(perm_lcs_div):.4f}, p={p_lcs_div:.4f})")
    print(f"  Transition rho: {rho_div_trans:.4f} (p={p_div_trans:.4f})")

    if hub_order_preserved or div_order_preserved:
        overall_verdict = 'PASS'
        overall_interp = 'Order-preserving alignment detected with at least one regime definition'
    else:
        overall_verdict = 'FAIL'
        overall_interp = 'No order-preserving alignment detected with either regime definition'

    # Update result dict
    result['diversity_spearman_rho'] = float(rho_div)
    result['diversity_spearman_p'] = float(p_div)
    result['diversity_lcs_ratio'] = float(lcs_ratio_div)
    result['diversity_lcs_p'] = float(p_lcs_div)
    result['diversity_transition_rho'] = float(rho_div_trans)
    result['diversity_transition_p'] = float(p_div_trans)
    result['hub_order_preserved'] = bool(hub_order_preserved)
    result['diversity_order_preserved'] = bool(div_order_preserved)
    result['overall_verdict'] = overall_verdict
    result['overall_interpretation'] = overall_interp

    print(f"\n>>> TEST E OVERALL VERDICT: {overall_verdict}")
    print(f"    {overall_interp}")

    # Additional analysis: Show the actual sequences visually
    print("\n--- VISUAL ALIGNMENT CHECK ---")
    print("Folio\tVisClust\tHubReg\tDivReg")
    print("-" * 50)
    for i, folio in enumerate(folios_sorted):
        print(f"{folio}\t{visual_cluster_seq[i]}\t\t{hub_regime_seq[i]}\t{diversity_regime_seq[i]}")

    # Save results
    with open(OUTPUT_DIR / 'test_e_results.json', 'w') as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == '__main__':
    run_test_e()
