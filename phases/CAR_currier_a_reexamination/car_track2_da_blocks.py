#!/usr/bin/env python
"""
CAR Phase Track 2: DA Block Mechanics

Tests DA-segmented sub-record structure in Currier A.

Tests:
- CAR-2.1: Sub-Record Vocabulary Coherence - Do DA blocks have internal structure?
- CAR-2.2: Block Position Effects - Does position predict vocabulary?
- CAR-2.3: DA Count vs Entry Complexity - Does DA articulation correlate with complexity?

Reference:
- C422: DA articulation (75.1% separation rate)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

from car_data_loader import (
    CARDataLoader, decompose_token, segment_by_da, get_middles_from_tokens,
    jaccard_similarity, MARKER_PREFIXES, is_da_token, PHASE_DIR
)


def test_car_2_1_subrecord_coherence():
    """
    CAR-2.1: Sub-Record Vocabulary Coherence

    Question: Do DA-segmented blocks have higher internal vocabulary overlap than random?

    Method:
    1. Identify all multi-DA entries (43% of A)
    2. Segment into DA-delimited blocks
    3. Calculate within-block Jaccard vs cross-block Jaccard
    4. Compare to shuffled baseline
    """
    print("\n" + "=" * 60)
    print("CAR-2.1: Sub-Record Vocabulary Coherence")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Get entries with multiple DA blocks
    multi_block_entries = []
    single_block_entries = []

    for entry in entries:
        blocks = segment_by_da(entry['tokens'])
        if len(blocks) > 1:
            multi_block_entries.append({
                'entry': entry,
                'blocks': blocks
            })
        else:
            single_block_entries.append(entry)

    print(f"\nTotal entries: {len(entries)}")
    print(f"Multi-block entries: {len(multi_block_entries)} ({100*len(multi_block_entries)/len(entries):.1f}%)")
    print(f"Single-block entries: {len(single_block_entries)}")

    # Calculate within-block vs cross-block MIDDLE similarity
    within_block_jaccards = []
    cross_block_jaccards = []

    for mbe in multi_block_entries:
        blocks = mbe['blocks']

        # Within-block: compare tokens within each block
        for block in blocks:
            if len(block) >= 2:
                middles = get_middles_from_tokens(block)
                # Self-comparison of block gives 1.0, so we need pairs
                for i in range(len(block)):
                    for j in range(i+1, len(block)):
                        m1 = get_middles_from_tokens([block[i]])
                        m2 = get_middles_from_tokens([block[j]])
                        if m1 and m2:
                            within_block_jaccards.append(jaccard_similarity(m1, m2))

        # Cross-block: compare tokens from different blocks
        for i in range(len(blocks)):
            for j in range(i+1, len(blocks)):
                m1 = get_middles_from_tokens(blocks[i])
                m2 = get_middles_from_tokens(blocks[j])
                if m1 and m2:
                    cross_block_jaccards.append(jaccard_similarity(m1, m2))

    mean_within = np.mean(within_block_jaccards) if within_block_jaccards else 0
    mean_cross = np.mean(cross_block_jaccards) if cross_block_jaccards else 0

    print(f"\nWithin-block MIDDLE Jaccard: {mean_within:.4f} (n={len(within_block_jaccards)})")
    print(f"Cross-block MIDDLE Jaccard: {mean_cross:.4f} (n={len(cross_block_jaccards)})")

    if mean_cross > 0:
        ratio = mean_within / mean_cross
        print(f"Ratio (within/cross): {ratio:.2f}x")
    else:
        ratio = 0

    # Statistical test
    if within_block_jaccards and cross_block_jaccards:
        stat, p_val = stats.mannwhitneyu(within_block_jaccards, cross_block_jaccards,
                                         alternative='greater')
        print(f"Mann-Whitney U p-value: {p_val:.6f}")
    else:
        p_val = 1.0

    # Shuffled baseline
    print("\nComputing shuffled baseline...")
    all_tokens = []
    for entry in entries:
        all_tokens.extend([t for t in entry['tokens'] if not is_da_token(t)])

    shuffled_ratios = []
    for _ in range(500):
        shuffled = all_tokens.copy()
        random.shuffle(shuffled)

        # Recreate multi-block entries with shuffled tokens
        idx = 0
        s_within = []
        s_cross = []

        for mbe in multi_block_entries:
            blocks = mbe['blocks']
            s_blocks = []
            for block in blocks:
                n = len(block)
                s_block = shuffled[idx:idx+n] if idx+n <= len(shuffled) else []
                s_blocks.append(s_block)
                idx += n

            # Calculate similarities for shuffled
            for block in s_blocks:
                if len(block) >= 2:
                    for i in range(len(block)):
                        for j in range(i+1, len(block)):
                            m1 = get_middles_from_tokens([block[i]])
                            m2 = get_middles_from_tokens([block[j]])
                            if m1 and m2:
                                s_within.append(jaccard_similarity(m1, m2))

            for i in range(len(s_blocks)):
                for j in range(i+1, len(s_blocks)):
                    m1 = get_middles_from_tokens(s_blocks[i])
                    m2 = get_middles_from_tokens(s_blocks[j])
                    if m1 and m2:
                        s_cross.append(jaccard_similarity(m1, m2))

        if s_within and s_cross:
            shuffled_ratios.append(np.mean(s_within) / np.mean(s_cross))

    baseline_mean = np.mean(shuffled_ratios) if shuffled_ratios else 1.0
    baseline_std = np.std(shuffled_ratios) if shuffled_ratios else 0
    effect_size = (ratio - baseline_mean) / baseline_std if baseline_std > 0 else 0
    perm_p_value = np.mean([r >= ratio for r in shuffled_ratios]) if shuffled_ratios else 1.0

    print(f"\nBaseline ratio: {baseline_mean:.3f} +/- {baseline_std:.3f}")
    print(f"Observed ratio: {ratio:.3f}")
    print(f"Effect size: {effect_size:.2f}")
    print(f"Permutation p-value: {perm_p_value:.4f}")

    result = {
        'test_id': 'CAR-2.1',
        'test_name': 'Sub-Record Vocabulary Coherence',
        'total_entries': len(entries),
        'multi_block_entries': len(multi_block_entries),
        'multi_block_pct': len(multi_block_entries) / len(entries),
        'mean_within_jaccard': mean_within,
        'mean_cross_jaccard': mean_cross,
        'within_cross_ratio': ratio,
        'mann_whitney_p': p_val,
        'baseline_ratio_mean': baseline_mean,
        'baseline_ratio_std': baseline_std,
        'effect_size': effect_size,
        'perm_p_value': perm_p_value,
        'verdict': 'SIGNIFICANT' if p_val < 0.001 and ratio > 1.0 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  DA blocks have higher internal coherence than cross-block")
        print(f"  Within/cross ratio: {ratio:.2f}x")

    return result


def test_car_2_2_block_position():
    """
    CAR-2.2: Block Position Effects

    Question: Does block position (first vs middle vs last) predict vocabulary?

    Method:
    1. Label blocks by position (FIRST, MIDDLE, LAST, ONLY)
    2. Calculate MIDDLE entropy by position
    3. Calculate PREFIX distribution by position
    4. Test for significant differences (chi-square)
    """
    print("\n" + "=" * 60)
    print("CAR-2.2: Block Position Effects")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Collect blocks by position
    position_data = {'FIRST': [], 'MIDDLE': [], 'LAST': [], 'ONLY': []}

    for entry in entries:
        blocks = segment_by_da(entry['tokens'])

        # Filter out empty blocks
        blocks = [b for b in blocks if b]

        if len(blocks) == 0:
            continue
        elif len(blocks) == 1:
            position_data['ONLY'].extend(blocks[0])
        else:
            position_data['FIRST'].extend(blocks[0])
            for block in blocks[1:-1]:
                position_data['MIDDLE'].extend(block)
            position_data['LAST'].extend(blocks[-1])

    print("\nTokens by position:")
    for pos, tokens in position_data.items():
        print(f"  {pos}: {len(tokens)}")

    # Calculate MIDDLE diversity by position
    print("\nMIDDLE diversity by position:")
    position_middles = {}
    position_middle_counts = {}

    for pos, tokens in position_data.items():
        middles = []
        for token in tokens:
            _, m, _ = decompose_token(token)
            if m is not None:
                middles.append(m)
        position_middles[pos] = set(middles)
        position_middle_counts[pos] = Counter(middles)

        if middles:
            unique = len(set(middles))
            entropy = stats.entropy(list(Counter(middles).values()))
            print(f"  {pos}: {unique} unique MIDDLEs, entropy={entropy:.3f}")

    # Calculate PREFIX distribution by position
    print("\nPREFIX distribution by position:")
    position_prefixes = {}

    for pos, tokens in position_data.items():
        prefixes = Counter()
        for token in tokens:
            p, _, _ = decompose_token(token)
            if p in MARKER_PREFIXES:
                prefixes[p] += 1
        position_prefixes[pos] = prefixes

    # Build contingency table for chi-square
    all_prefixes = sorted(MARKER_PREFIXES)
    positions_with_data = [p for p in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']
                          if sum(position_prefixes[p].values()) > 0]

    contingency = []
    for pos in positions_with_data:
        row = [position_prefixes[pos].get(pf, 0) for pf in all_prefixes]
        contingency.append(row)

    contingency = np.array(contingency)

    # Chi-square test
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency + 1)  # +1 to avoid zeros

    print(f"\nChi-square test for PREFIX x Position:")
    print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p_val:.6f}")

    # Show PREFIX distribution per position
    print("\nPREFIX percentages by position:")
    for pos in positions_with_data:
        total = sum(position_prefixes[pos].values())
        top3 = position_prefixes[pos].most_common(3)
        pcts = ', '.join([f"{p}:{100*c/total:.1f}%" for p, c in top3])
        print(f"  {pos}: {pcts}")

    # Compare FIRST vs LAST
    if position_prefixes['FIRST'] and position_prefixes['LAST']:
        first_total = sum(position_prefixes['FIRST'].values())
        last_total = sum(position_prefixes['LAST'].values())

        print("\nFIRST vs LAST comparison:")
        for pf in all_prefixes:
            first_pct = 100 * position_prefixes['FIRST'].get(pf, 0) / first_total
            last_pct = 100 * position_prefixes['LAST'].get(pf, 0) / last_total
            diff = first_pct - last_pct
            if abs(diff) > 2:
                print(f"  {pf}: FIRST={first_pct:.1f}%, LAST={last_pct:.1f}%, diff={diff:+.1f}%")

    result = {
        'test_id': 'CAR-2.2',
        'test_name': 'Block Position Effects',
        'token_counts': {pos: len(tokens) for pos, tokens in position_data.items()},
        'unique_middles': {pos: len(mids) for pos, mids in position_middles.items()},
        'chi2': chi2,
        'p_value': p_val,
        'dof': dof,
        'prefix_distribution': {pos: dict(cnts) for pos, cnts in position_prefixes.items()},
        'verdict': 'SIGNIFICANT' if p_val < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Block position affects vocabulary distribution")
        print(f"  Chi2 = {chi2:.2f}, p = {p_val:.6f}")

    return result


def test_car_2_3_da_complexity():
    """
    CAR-2.3: DA Count vs Entry Complexity

    Question: Does more DA articulation correlate with entry complexity?

    Method:
    1. Count DA occurrences per entry (0 to N)
    2. Calculate entry-level metrics: total tokens, unique MIDDLEs, marker diversity
    3. Correlate DA count with complexity metrics
    4. Test linearity (Spearman correlation)
    """
    print("\n" + "=" * 60)
    print("CAR-2.3: DA Count vs Entry Complexity")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Calculate metrics per entry
    entry_metrics = []

    for entry in entries:
        tokens = entry['tokens']

        # Count DA tokens
        da_count = sum(1 for t in tokens if is_da_token(t))

        # Total tokens (excluding DA)
        non_da_tokens = [t for t in tokens if not is_da_token(t)]
        total_tokens = len(non_da_tokens)

        # Unique MIDDLEs
        middles = get_middles_from_tokens(non_da_tokens)
        unique_middles = len(middles)

        # Marker diversity
        markers = set()
        for token in non_da_tokens:
            p, _, _ = decompose_token(token)
            if p in MARKER_PREFIXES:
                markers.add(p)
        marker_diversity = len(markers)

        entry_metrics.append({
            'da_count': da_count,
            'total_tokens': total_tokens,
            'unique_middles': unique_middles,
            'marker_diversity': marker_diversity
        })

    # Convert to arrays
    da_counts = np.array([e['da_count'] for e in entry_metrics])
    total_tokens = np.array([e['total_tokens'] for e in entry_metrics])
    unique_middles = np.array([e['unique_middles'] for e in entry_metrics])
    marker_diversity = np.array([e['marker_diversity'] for e in entry_metrics])

    # DA count distribution
    print(f"\nDA count distribution:")
    da_dist = Counter(da_counts)
    for da, count in sorted(da_dist.items())[:10]:
        print(f"  {da} DA: {count} entries ({100*count/len(entries):.1f}%)")

    # Correlations
    print("\nCorrelations with DA count:")

    rho_tokens, p_tokens = stats.spearmanr(da_counts, total_tokens)
    print(f"  Total tokens: rho={rho_tokens:.3f}, p={p_tokens:.6f}")

    rho_middles, p_middles = stats.spearmanr(da_counts, unique_middles)
    print(f"  Unique MIDDLEs: rho={rho_middles:.3f}, p={p_middles:.6f}")

    rho_markers, p_markers = stats.spearmanr(da_counts, marker_diversity)
    print(f"  Marker diversity: rho={rho_markers:.3f}, p={p_markers:.6f}")

    # Mean metrics by DA count
    print("\nMean metrics by DA count:")
    for da in range(min(5, max(da_counts) + 1)):
        mask = da_counts == da
        if mask.sum() > 0:
            mean_tokens = total_tokens[mask].mean()
            mean_middles = unique_middles[mask].mean()
            mean_markers = marker_diversity[mask].mean()
            print(f"  {da} DA: {mask.sum()} entries, "
                  f"tokens={mean_tokens:.1f}, middles={mean_middles:.1f}, markers={mean_markers:.1f}")

    result = {
        'test_id': 'CAR-2.3',
        'test_name': 'DA Count vs Entry Complexity',
        'n_entries': len(entries),
        'da_count_distribution': {int(k): int(v) for k, v in da_dist.items()},
        'correlation_tokens': {'rho': rho_tokens, 'p': p_tokens},
        'correlation_middles': {'rho': rho_middles, 'p': p_middles},
        'correlation_markers': {'rho': rho_markers, 'p': p_markers},
        'verdict': 'SIGNIFICANT' if (p_tokens < 0.001 and rho_tokens > 0.1) else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  DA articulation correlates with entry complexity")
        print(f"  More DA = more tokens (rho={rho_tokens:.3f})")
        print(f"  More DA = more unique MIDDLEs (rho={rho_middles:.3f})")

    return result


def run_track2():
    """Run all Track 2 tests."""
    print("\n" + "=" * 70)
    print("TRACK 2: DA BLOCK MECHANICS")
    print("=" * 70)

    results = {
        'track': 2,
        'name': 'DA Block Mechanics',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-2.1'] = test_car_2_1_subrecord_coherence()
    results['tests']['CAR-2.2'] = test_car_2_2_block_position()
    results['tests']['CAR-2.3'] = test_car_2_3_da_complexity()

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 2 SUMMARY")
    print("=" * 70)

    significant = sum(1 for t in results['tests'].values() if t['verdict'] == 'SIGNIFICANT')
    null = sum(1 for t in results['tests'].values() if t['verdict'] == 'NULL')

    print(f"\nTests passed (SIGNIFICANT): {significant}/3")
    print(f"Tests failed (NULL): {null}/3")

    for test_id, test in results['tests'].items():
        print(f"\n{test_id}: {test['test_name']}")
        print(f"  Verdict: {test['verdict']}")

    # Track verdict
    if significant >= 2:
        results['track_verdict'] = 'SUCCESS'
        print("\n-> TRACK 2 VERDICT: SUCCESS")
        print("  DA block mechanics confirmed")
    elif significant >= 1:
        results['track_verdict'] = 'PARTIAL'
        print("\n-> TRACK 2 VERDICT: PARTIAL")
        print("  Some DA block structure exists")
    else:
        results['track_verdict'] = 'NULL'
        print("\n-> TRACK 2 VERDICT: NULL")
        print("  DA blocks do not show internal structure")

    # Save results
    output_file = PHASE_DIR / 'car_track2_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_track2()
