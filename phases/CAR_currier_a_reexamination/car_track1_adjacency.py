#!/usr/bin/env python
"""
CAR Phase Track 1: Adjacency Pattern Recovery

Tests adjacency structure in clean (H-only) Currier A data.

Tests:
- CAR-1.1: Bigram Distribution - What is the actual bigram reuse rate?
- CAR-1.2: MIDDLE Adjacency Coherence - Do adjacent entries share MIDDLEs?
- CAR-1.3: Transition Matrix - Are there forbidden/enriched adjacency patterns?

Reference:
- C346: Sequential coherence (1.31x overlap)
- C267: Previous bigram reuse (70.7% - INFLATED by bug)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

from car_data_loader import (
    CARDataLoader, decompose_token, get_middles_from_tokens,
    jaccard_similarity, MARKER_PREFIXES, PHASE_DIR, RESULTS_DIR
)


def test_car_1_1_bigram_distribution():
    """
    CAR-1.1: Bigram Distribution (Clean)

    Question: What is the actual bigram reuse rate with H-only data?

    Method:
    1. Extract all adjacent token pairs (within lines)
    2. Count unique bigrams vs total pairs
    3. Compare to shuffled baseline
    4. Compare to previous inflated value (70.7% -> expected ~14%)
    """
    print("\n" + "=" * 60)
    print("CAR-1.1: Bigram Distribution (Clean)")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Extract all bigrams from Currier A
    bigrams = []
    for entry in entries:
        tokens = entry['tokens']
        for i in range(len(tokens) - 1):
            bigrams.append((tokens[i], tokens[i+1]))

    total_bigrams = len(bigrams)
    unique_bigrams = len(set(bigrams))

    # Bigram reuse rate = 1 - (unique / total)
    # High reuse = many repeated bigrams
    reuse_rate = 1 - (unique_bigrams / total_bigrams) if total_bigrams > 0 else 0

    print(f"\nTotal bigrams: {total_bigrams:,}")
    print(f"Unique bigrams: {unique_bigrams:,}")
    print(f"Bigram reuse rate: {100*reuse_rate:.1f}%")

    # Bigram frequency distribution
    bigram_counts = Counter(bigrams)
    top_bigrams = bigram_counts.most_common(20)

    print(f"\nTop 10 bigrams:")
    for (b1, b2), count in top_bigrams[:10]:
        print(f"  {b1} -> {b2}: {count}")

    # Shuffled baseline
    print("\nComparing to shuffled baseline (1000 permutations)...")
    all_tokens = []
    for entry in entries:
        all_tokens.extend(entry['tokens'])

    shuffled_reuse_rates = []
    for _ in range(1000):
        shuffled = all_tokens.copy()
        random.shuffle(shuffled)

        # Recreate entries with shuffled tokens
        shuffled_bigrams = []
        idx = 0
        for entry in entries:
            n = len(entry['tokens'])
            for i in range(n - 1):
                if idx + i + 1 < len(shuffled):
                    shuffled_bigrams.append((shuffled[idx+i], shuffled[idx+i+1]))
            idx += n

        if shuffled_bigrams:
            s_unique = len(set(shuffled_bigrams))
            s_reuse = 1 - (s_unique / len(shuffled_bigrams))
            shuffled_reuse_rates.append(s_reuse)

    baseline_mean = np.mean(shuffled_reuse_rates)
    baseline_std = np.std(shuffled_reuse_rates)
    effect_size = (reuse_rate - baseline_mean) / baseline_std if baseline_std > 0 else 0
    p_value = np.mean([r >= reuse_rate for r in shuffled_reuse_rates])

    print(f"\nBaseline reuse rate: {100*baseline_mean:.1f}% ± {100*baseline_std:.1f}%")
    print(f"Observed reuse rate: {100*reuse_rate:.1f}%")
    print(f"Effect size (z-score): {effect_size:.2f}")
    print(f"P-value (one-tailed): {p_value:.4f}")

    # Compare to inflated value
    inflated_value = 0.707
    print(f"\nPrevious (inflated) value: {100*inflated_value:.1f}%")
    print(f"Current (H-only) value: {100*reuse_rate:.1f}%")
    print(f"Reduction: {100*(inflated_value - reuse_rate):.1f} percentage points")

    result = {
        'test_id': 'CAR-1.1',
        'test_name': 'Bigram Distribution (Clean)',
        'total_bigrams': total_bigrams,
        'unique_bigrams': unique_bigrams,
        'reuse_rate': reuse_rate,
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'effect_size': effect_size,
        'p_value': p_value,
        'previous_inflated_value': inflated_value,
        'top_bigrams': [(b1, b2, c) for (b1, b2), c in top_bigrams[:20]],
        'verdict': 'SIGNIFICANT' if p_value < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Bigram reuse rate {100*reuse_rate:.1f}% is significantly above baseline")
        print(f"  This confirms adjacency structure exists in clean data")

    return result


def test_car_1_2_middle_adjacency():
    """
    CAR-1.2: MIDDLE Adjacency Coherence

    Question: Do adjacent entries share MIDDLEs more than expected?

    Method:
    1. Extract MIDDLE component from all A tokens
    2. For each adjacent entry pair, calculate Jaccard(MIDDLEs)
    3. Compare to random permutation baseline
    4. Decompose by: same-marker vs cross-marker pairs
    """
    print("\n" + "=" * 60)
    print("CAR-1.2: MIDDLE Adjacency Coherence")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Get dominant marker and MIDDLE set for each entry
    entry_data = []
    for entry in entries:
        middles = get_middles_from_tokens(entry['tokens'])

        # Get dominant marker
        marker_counts = Counter()
        for token in entry['tokens']:
            prefix, _, _ = decompose_token(token)
            if prefix in MARKER_PREFIXES:
                marker_counts[prefix] += 1

        dominant_marker = marker_counts.most_common(1)[0][0] if marker_counts else None

        entry_data.append({
            'middles': middles,
            'marker': dominant_marker,
            'folio': entry['folio']
        })

    # Calculate adjacent Jaccard similarities
    adjacent_jaccards = []
    same_marker_jaccards = []
    cross_marker_jaccards = []
    same_folio_jaccards = []

    for i in range(len(entry_data) - 1):
        e1, e2 = entry_data[i], entry_data[i+1]

        if e1['middles'] and e2['middles']:
            j = jaccard_similarity(e1['middles'], e2['middles'])
            adjacent_jaccards.append(j)

            if e1['marker'] == e2['marker'] and e1['marker'] is not None:
                same_marker_jaccards.append(j)
            elif e1['marker'] != e2['marker']:
                cross_marker_jaccards.append(j)

            if e1['folio'] == e2['folio']:
                same_folio_jaccards.append(j)

    mean_adjacent = np.mean(adjacent_jaccards) if adjacent_jaccards else 0
    mean_same_marker = np.mean(same_marker_jaccards) if same_marker_jaccards else 0
    mean_cross_marker = np.mean(cross_marker_jaccards) if cross_marker_jaccards else 0
    mean_same_folio = np.mean(same_folio_jaccards) if same_folio_jaccards else 0

    print(f"\nAdjacent entry MIDDLE Jaccard similarity:")
    print(f"  Overall: {mean_adjacent:.4f} (n={len(adjacent_jaccards)})")
    print(f"  Same marker: {mean_same_marker:.4f} (n={len(same_marker_jaccards)})")
    print(f"  Cross marker: {mean_cross_marker:.4f} (n={len(cross_marker_jaccards)})")
    print(f"  Same folio: {mean_same_folio:.4f} (n={len(same_folio_jaccards)})")

    # Random baseline (shuffle entry order)
    print("\nComputing shuffled baseline (1000 permutations)...")
    shuffled_means = []
    for _ in range(1000):
        shuffled = entry_data.copy()
        random.shuffle(shuffled)

        jaccards = []
        for i in range(len(shuffled) - 1):
            e1, e2 = shuffled[i], shuffled[i+1]
            if e1['middles'] and e2['middles']:
                jaccards.append(jaccard_similarity(e1['middles'], e2['middles']))

        if jaccards:
            shuffled_means.append(np.mean(jaccards))

    baseline_mean = np.mean(shuffled_means)
    baseline_std = np.std(shuffled_means)
    effect_size = (mean_adjacent - baseline_mean) / baseline_std if baseline_std > 0 else 0
    p_value = np.mean([m >= mean_adjacent for m in shuffled_means])

    print(f"\nBaseline Jaccard: {baseline_mean:.4f} ± {baseline_std:.4f}")
    print(f"Observed Jaccard: {mean_adjacent:.4f}")
    print(f"Ratio (observed/baseline): {mean_adjacent/baseline_mean:.2f}x")
    print(f"Effect size (z-score): {effect_size:.2f}")
    print(f"P-value (one-tailed): {p_value:.4f}")

    # Compare same-marker vs cross-marker
    if same_marker_jaccards and cross_marker_jaccards:
        t_stat, t_pval = stats.mannwhitneyu(same_marker_jaccards, cross_marker_jaccards,
                                            alternative='greater')
        print(f"\nSame vs cross-marker comparison:")
        print(f"  Same marker mean: {mean_same_marker:.4f}")
        print(f"  Cross marker mean: {mean_cross_marker:.4f}")
        print(f"  Ratio: {mean_same_marker/mean_cross_marker:.2f}x")
        print(f"  Mann-Whitney p-value: {t_pval:.4f}")
    else:
        t_pval = 1.0

    result = {
        'test_id': 'CAR-1.2',
        'test_name': 'MIDDLE Adjacency Coherence',
        'mean_adjacent_jaccard': mean_adjacent,
        'mean_same_marker': mean_same_marker,
        'mean_cross_marker': mean_cross_marker,
        'mean_same_folio': mean_same_folio,
        'n_adjacent_pairs': len(adjacent_jaccards),
        'n_same_marker': len(same_marker_jaccards),
        'n_cross_marker': len(cross_marker_jaccards),
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'ratio_to_baseline': mean_adjacent / baseline_mean if baseline_mean > 0 else 0,
        'effect_size': effect_size,
        'p_value': p_value,
        'same_vs_cross_pvalue': t_pval,
        'verdict': 'SIGNIFICANT' if p_value < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Adjacent entries share MIDDLEs {result['ratio_to_baseline']:.2f}x above baseline")
        if t_pval < 0.001:
            print(f"  Same-marker pairs have higher coherence than cross-marker pairs")

    return result


def test_car_1_3_transition_matrix():
    """
    CAR-1.3: Transition Matrix (Clean)

    Question: Are there forbidden or enriched adjacency patterns?

    Method:
    1. Build PREFIX×PREFIX transition matrix
    2. Build MIDDLE×MIDDLE transition matrix (top 50 MIDDLEs)
    3. Chi-square test for independence
    4. Identify any forbidden (0-count) or enriched (>3x expected) pairs
    """
    print("\n" + "=" * 60)
    print("CAR-1.3: Transition Matrix (Clean)")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Extract all adjacent token pairs with decomposition
    prefix_transitions = []
    middle_transitions = []
    all_middles = Counter()

    for entry in entries:
        tokens = entry['tokens']
        for i in range(len(tokens) - 1):
            p1, m1, _ = decompose_token(tokens[i])
            p2, m2, _ = decompose_token(tokens[i+1])

            if p1 and p2:
                prefix_transitions.append((p1, p2))

            if m1 is not None and m2 is not None:
                middle_transitions.append((m1, m2))
                all_middles[m1] += 1
                all_middles[m2] += 1

    # === PREFIX TRANSITION MATRIX ===
    print("\n--- PREFIX Transition Analysis ---")
    prefixes = sorted(MARKER_PREFIXES)
    prefix_matrix = np.zeros((len(prefixes), len(prefixes)), dtype=int)
    prefix_idx = {p: i for i, p in enumerate(prefixes)}

    for p1, p2 in prefix_transitions:
        if p1 in prefix_idx and p2 in prefix_idx:
            prefix_matrix[prefix_idx[p1], prefix_idx[p2]] += 1

    # Chi-square test for independence
    chi2, p_val, dof, expected = stats.chi2_contingency(prefix_matrix + 1)  # +1 to avoid zeros

    print(f"\nPrefix transitions: {len(prefix_transitions):,}")
    print(f"Chi-square: {chi2:.1f}, df={dof}, p={p_val:.4f}")

    # Find enriched/depleted pairs
    print("\nPrefix transition enrichment (observed/expected):")
    enriched_pairs = []
    depleted_pairs = []

    for i, p1 in enumerate(prefixes):
        for j, p2 in enumerate(prefixes):
            obs = prefix_matrix[i, j]
            exp = expected[i, j]
            ratio = obs / exp if exp > 0 else 0

            if ratio > 2.0:
                enriched_pairs.append((p1, p2, obs, exp, ratio))
            elif ratio < 0.5 and obs < exp - 5:
                depleted_pairs.append((p1, p2, obs, exp, ratio))

    print(f"\nEnriched pairs (>2x expected): {len(enriched_pairs)}")
    for p1, p2, obs, exp, ratio in sorted(enriched_pairs, key=lambda x: -x[4])[:10]:
        print(f"  {p1} -> {p2}: {obs} vs {exp:.1f} expected ({ratio:.2f}x)")

    print(f"\nDepleted pairs (<0.5x expected): {len(depleted_pairs)}")
    for p1, p2, obs, exp, ratio in sorted(depleted_pairs, key=lambda x: x[4])[:10]:
        print(f"  {p1} -> {p2}: {obs} vs {exp:.1f} expected ({ratio:.2f}x)")

    # === MIDDLE TRANSITION MATRIX (Top 50) ===
    print("\n--- MIDDLE Transition Analysis (Top 50) ---")
    top_middles = [m for m, _ in all_middles.most_common(50)]
    middle_idx = {m: i for i, m in enumerate(top_middles)}

    middle_matrix = np.zeros((50, 50), dtype=int)
    for m1, m2 in middle_transitions:
        if m1 in middle_idx and m2 in middle_idx:
            middle_matrix[middle_idx[m1], middle_idx[m2]] += 1

    # Add pseudocount for chi-square
    middle_chi2, middle_p, middle_dof, middle_expected = stats.chi2_contingency(
        middle_matrix + 1
    )

    print(f"\nMIDDLE transitions (top 50): {middle_matrix.sum():,}")
    print(f"Chi-square: {middle_chi2:.1f}, df={middle_dof}, p={middle_p:.6f}")

    # Find enriched/depleted MIDDLE pairs
    middle_enriched = []
    middle_depleted = []
    zero_count_pairs = 0

    for i, m1 in enumerate(top_middles):
        for j, m2 in enumerate(top_middles):
            obs = middle_matrix[i, j]
            exp = middle_expected[i, j]
            ratio = obs / exp if exp > 1 else 0

            if obs == 0 and exp > 3:
                zero_count_pairs += 1
            if ratio > 3.0 and obs > 5:
                middle_enriched.append((m1, m2, obs, exp, ratio))
            elif ratio < 0.33 and exp > 5:
                middle_depleted.append((m1, m2, obs, exp, ratio))

    print(f"\nZero-count pairs (where >3 expected): {zero_count_pairs}")
    print(f"Enriched pairs (>3x expected): {len(middle_enriched)}")
    for m1, m2, obs, exp, ratio in sorted(middle_enriched, key=lambda x: -x[4])[:5]:
        print(f"  '{m1}' -> '{m2}': {obs} vs {exp:.1f} expected ({ratio:.2f}x)")

    print(f"\nDepleted pairs (<0.33x expected): {len(middle_depleted)}")
    for m1, m2, obs, exp, ratio in sorted(middle_depleted, key=lambda x: x[4])[:5]:
        print(f"  '{m1}' -> '{m2}': {obs} vs {exp:.1f} expected ({ratio:.2f}x)")

    result = {
        'test_id': 'CAR-1.3',
        'test_name': 'Transition Matrix (Clean)',
        'prefix_transitions': len(prefix_transitions),
        'prefix_chi2': chi2,
        'prefix_p_value': p_val,
        'prefix_enriched_count': len(enriched_pairs),
        'prefix_depleted_count': len(depleted_pairs),
        'prefix_enriched_pairs': [(p1, p2, int(obs), float(ratio))
                                   for p1, p2, obs, _, ratio in enriched_pairs[:10]],
        'prefix_depleted_pairs': [(p1, p2, int(obs), float(ratio))
                                   for p1, p2, obs, _, ratio in depleted_pairs[:10]],
        'middle_transitions_top50': int(middle_matrix.sum()),
        'middle_chi2': middle_chi2,
        'middle_p_value': middle_p,
        'middle_enriched_count': len(middle_enriched),
        'middle_depleted_count': len(middle_depleted),
        'middle_zero_count_pairs': zero_count_pairs,
        'verdict': 'SIGNIFICANT' if p_val < 0.001 or middle_p < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print("  Adjacency patterns are non-random:")
        print(f"  - PREFIX transitions: chi2={chi2:.1f}, p={p_val:.6f}")
        print(f"  - MIDDLE transitions: chi2={middle_chi2:.1f}, p={middle_p:.6f}")
        if len(enriched_pairs) > 0:
            print(f"  - Found {len(enriched_pairs)} enriched PREFIX pairs")
        if zero_count_pairs > 0:
            print(f"  - Found {zero_count_pairs} zero-count MIDDLE pairs (potential forbidden transitions)")

    return result


def run_track1():
    """Run all Track 1 tests."""
    print("\n" + "=" * 70)
    print("TRACK 1: ADJACENCY PATTERN RECOVERY")
    print("=" * 70)

    results = {
        'track': 1,
        'name': 'Adjacency Pattern Recovery',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-1.1'] = test_car_1_1_bigram_distribution()
    results['tests']['CAR-1.2'] = test_car_1_2_middle_adjacency()
    results['tests']['CAR-1.3'] = test_car_1_3_transition_matrix()

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 1 SUMMARY")
    print("=" * 70)

    significant = sum(1 for t in results['tests'].values() if t['verdict'] == 'SIGNIFICANT')
    null = sum(1 for t in results['tests'].values() if t['verdict'] == 'NULL')

    print(f"\nTests passed (SIGNIFICANT): {significant}/3")
    print(f"Tests failed (NULL): {null}/3")

    for test_id, test in results['tests'].items():
        print(f"\n{test_id}: {test['test_name']}")
        print(f"  Verdict: {test['verdict']}")

    # Track verdict
    if significant == 0:
        results['track_verdict'] = 'HARD_STOP'
        print("\n-> TRACK 1 VERDICT: HARD_STOP")
        print("  All tests returned null - adjacency structure doesn't exist")
    elif significant >= 2:
        results['track_verdict'] = 'SUCCESS'
        print("\n-> TRACK 1 VERDICT: SUCCESS")
        print("  Adjacency structure confirmed in clean data")
    else:
        results['track_verdict'] = 'PARTIAL'
        print("\n-> TRACK 1 VERDICT: PARTIAL")
        print("  Some adjacency structure exists")

    # Save results
    output_file = PHASE_DIR / 'car_track1_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_track1()
