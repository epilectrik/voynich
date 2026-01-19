#!/usr/bin/env python
"""
CAR Phase Track 3: Entry Organization & Lookup

Tests how Currier A entries are organized for human use.

Tests:
- CAR-3.1: Marker Run Analysis - Do same-marker entries cluster spatially?
- CAR-3.2: Folio-Level Marker Concentration - Do folios specialize in certain markers?
- CAR-3.3: Sister Pair Proximity - Do sister pairs (ch-sh, ok-ot) appear near each other?
- CAR-3.4: Index Token Detection - Are there tokens that mark entry boundaries?

Reference:
- C424: Clustered adjacency (31% in runs)
- C408-C412: Sister pair analysis
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

from car_data_loader import (
    CARDataLoader, decompose_token, get_dominant_marker,
    MARKER_PREFIXES, SISTER_PAIRS, PHASE_DIR
)


def test_car_3_1_marker_runs():
    """
    CAR-3.1: Marker Run Analysis

    Question: Do same-marker entries cluster spatially?

    Method:
    1. Tag each A line with dominant marker
    2. Calculate run lengths (consecutive same-marker entries)
    3. Compare to random permutation baseline
    4. Test by section (H, P, T)
    """
    print("\n" + "=" * 60)
    print("CAR-3.1: Marker Run Analysis")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Get dominant marker for each entry
    entry_markers = []
    for entry in entries:
        marker = get_dominant_marker(entry['tokens'])
        entry_markers.append({
            'marker': marker,
            'folio': entry['folio'],
            'section': entry['section']
        })

    # Calculate run lengths
    def get_runs(markers):
        """Calculate run lengths for a sequence of markers."""
        if not markers:
            return []
        runs = []
        current_marker = markers[0]
        current_len = 1
        for m in markers[1:]:
            if m == current_marker and m is not None:
                current_len += 1
            else:
                if current_marker is not None:
                    runs.append(current_len)
                current_marker = m
                current_len = 1
        if current_marker is not None:
            runs.append(current_len)
        return runs

    # Overall runs
    all_markers = [e['marker'] for e in entry_markers]
    observed_runs = get_runs(all_markers)
    mean_run_length = np.mean(observed_runs) if observed_runs else 0
    max_run_length = max(observed_runs) if observed_runs else 0
    runs_gt_1 = sum(1 for r in observed_runs if r > 1)
    pct_in_runs = sum(r for r in observed_runs if r > 1) / len(all_markers) * 100

    print(f"\nEntries with markers: {sum(1 for m in all_markers if m is not None)}/{len(all_markers)}")
    print(f"Total runs: {len(observed_runs)}")
    print(f"Mean run length: {mean_run_length:.2f}")
    print(f"Max run length: {max_run_length}")
    print(f"Runs > 1: {runs_gt_1} ({100*runs_gt_1/len(observed_runs):.1f}%)")
    print(f"Entries in runs >1: {pct_in_runs:.1f}%")

    # Run distribution
    run_dist = Counter(observed_runs)
    print(f"\nRun length distribution:")
    for length in sorted(run_dist.keys())[:10]:
        print(f"  {length}: {run_dist[length]}")

    # Permutation test
    print("\nComputing shuffled baseline (1000 permutations)...")
    shuffled_means = []
    for _ in range(1000):
        shuffled = all_markers.copy()
        random.shuffle(shuffled)
        runs = get_runs(shuffled)
        if runs:
            shuffled_means.append(np.mean(runs))

    baseline_mean = np.mean(shuffled_means)
    baseline_std = np.std(shuffled_means)
    effect_size = (mean_run_length - baseline_mean) / baseline_std if baseline_std > 0 else 0
    p_value = np.mean([m >= mean_run_length for m in shuffled_means])

    print(f"\nBaseline mean run length: {baseline_mean:.3f} +/- {baseline_std:.3f}")
    print(f"Observed mean run length: {mean_run_length:.3f}")
    print(f"Ratio (observed/baseline): {mean_run_length/baseline_mean:.2f}x")
    print(f"Effect size: {effect_size:.2f}")
    print(f"P-value: {p_value:.4f}")

    # By section
    print("\nRuns by section:")
    for section in ['H', 'P', 'T']:
        section_markers = [e['marker'] for e in entry_markers if e['section'] == section]
        section_runs = get_runs(section_markers)
        if section_runs:
            print(f"  {section}: n={len(section_markers)}, mean_run={np.mean(section_runs):.2f}, "
                  f"max_run={max(section_runs)}")

    result = {
        'test_id': 'CAR-3.1',
        'test_name': 'Marker Run Analysis',
        'n_entries': len(all_markers),
        'n_with_markers': sum(1 for m in all_markers if m is not None),
        'n_runs': len(observed_runs),
        'mean_run_length': mean_run_length,
        'max_run_length': max_run_length,
        'pct_in_runs': pct_in_runs,
        'run_distribution': {int(k): int(v) for k, v in run_dist.items()},
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'ratio_to_baseline': mean_run_length / baseline_mean if baseline_mean > 0 else 0,
        'effect_size': effect_size,
        'p_value': p_value,
        'verdict': 'SIGNIFICANT' if p_value < 0.001 and mean_run_length > baseline_mean else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Same-marker entries cluster spatially")
        print(f"  Run length {mean_run_length:.2f} vs {baseline_mean:.2f} expected")

    return result


def test_car_3_2_folio_concentration():
    """
    CAR-3.2: Folio-Level Marker Concentration

    Question: Do folios specialize in certain markers?

    Method:
    1. For each A folio, calculate marker distribution
    2. Calculate entropy (low = specialized, high = mixed)
    3. Compare entropy distribution to random baseline
    4. Identify any single-marker-dominant folios
    """
    print("\n" + "=" * 60)
    print("CAR-3.2: Folio-Level Marker Concentration")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Get markers per folio
    folio_markers = defaultdict(list)
    for entry in entries:
        marker = get_dominant_marker(entry['tokens'])
        if marker:
            folio_markers[entry['folio']].append(marker)

    # Calculate entropy per folio
    folio_entropies = {}
    folio_dominant = {}

    for folio, markers in folio_markers.items():
        if len(markers) >= 5:  # Need minimum entries for meaningful entropy
            counts = Counter(markers)
            probs = [c / len(markers) for c in counts.values()]
            entropy = stats.entropy(probs)
            folio_entropies[folio] = entropy

            # Dominant marker
            dominant, count = counts.most_common(1)[0]
            folio_dominant[folio] = {
                'marker': dominant,
                'pct': count / len(markers),
                'n_entries': len(markers)
            }

    if not folio_entropies:
        print("Not enough folios with sufficient entries")
        return {'test_id': 'CAR-3.2', 'verdict': 'INSUFFICIENT_DATA'}

    mean_entropy = np.mean(list(folio_entropies.values()))
    max_possible_entropy = np.log(len(MARKER_PREFIXES))  # Uniform over 8 markers

    print(f"\nFolios analyzed: {len(folio_entropies)}")
    print(f"Mean entropy: {mean_entropy:.3f} (max possible: {max_possible_entropy:.3f})")
    print(f"Normalized entropy: {mean_entropy/max_possible_entropy:.2f}")

    # Entropy distribution
    entropy_vals = list(folio_entropies.values())
    low_entropy = sum(1 for e in entropy_vals if e < 1.0)
    high_entropy = sum(1 for e in entropy_vals if e > 1.5)

    print(f"\nLow entropy folios (<1.0): {low_entropy} ({100*low_entropy/len(entropy_vals):.1f}%)")
    print(f"High entropy folios (>1.5): {high_entropy} ({100*high_entropy/len(entropy_vals):.1f}%)")

    # Most specialized folios
    print(f"\nMost specialized folios (lowest entropy):")
    sorted_folios = sorted(folio_entropies.items(), key=lambda x: x[1])
    for folio, entropy in sorted_folios[:5]:
        dom = folio_dominant[folio]
        print(f"  {folio}: entropy={entropy:.3f}, dominant={dom['marker']} ({100*dom['pct']:.0f}%), "
              f"n={dom['n_entries']}")

    # Most mixed folios
    print(f"\nMost mixed folios (highest entropy):")
    for folio, entropy in sorted_folios[-5:]:
        dom = folio_dominant[folio]
        print(f"  {folio}: entropy={entropy:.3f}, dominant={dom['marker']} ({100*dom['pct']:.0f}%), "
              f"n={dom['n_entries']}")

    # Single-marker-dominant folios (>80% one marker)
    dominant_folios = [(f, d) for f, d in folio_dominant.items() if d['pct'] > 0.8]
    print(f"\nSingle-marker-dominant folios (>80%): {len(dominant_folios)}")
    for folio, dom in sorted(dominant_folios, key=lambda x: -x[1]['pct'])[:5]:
        print(f"  {folio}: {dom['marker']} ({100*dom['pct']:.0f}%), n={dom['n_entries']}")

    # Shuffled baseline for entropy
    print("\nComputing shuffled baseline...")
    all_markers = []
    folio_sizes = {}
    for folio, markers in folio_markers.items():
        all_markers.extend(markers)
        folio_sizes[folio] = len(markers)

    shuffled_entropies = []
    for _ in range(500):
        shuffled = all_markers.copy()
        random.shuffle(shuffled)

        idx = 0
        s_entropies = []
        for folio, size in folio_sizes.items():
            if size >= 5:
                s_markers = shuffled[idx:idx+size]
                counts = Counter(s_markers)
                probs = [c / len(s_markers) for c in counts.values()]
                s_entropies.append(stats.entropy(probs))
            idx += size

        if s_entropies:
            shuffled_entropies.append(np.mean(s_entropies))

    baseline_mean = np.mean(shuffled_entropies) if shuffled_entropies else 0
    baseline_std = np.std(shuffled_entropies) if shuffled_entropies else 0
    effect_size = (mean_entropy - baseline_mean) / baseline_std if baseline_std > 0 else 0
    # Lower entropy = more specialized, so we test for lower
    p_value = np.mean([m <= mean_entropy for m in shuffled_entropies]) if shuffled_entropies else 1.0

    print(f"\nBaseline entropy: {baseline_mean:.3f} +/- {baseline_std:.3f}")
    print(f"Observed entropy: {mean_entropy:.3f}")
    print(f"Effect size: {effect_size:.2f}")
    print(f"P-value (testing for specialization): {p_value:.4f}")

    result = {
        'test_id': 'CAR-3.2',
        'test_name': 'Folio-Level Marker Concentration',
        'n_folios': len(folio_entropies),
        'mean_entropy': mean_entropy,
        'max_possible_entropy': max_possible_entropy,
        'normalized_entropy': mean_entropy / max_possible_entropy,
        'low_entropy_folios': low_entropy,
        'single_marker_dominant': len(dominant_folios),
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'effect_size': effect_size,
        'p_value': p_value,
        'most_specialized': [(f, e) for f, e in sorted_folios[:5]],
        'verdict': 'SIGNIFICANT' if p_value < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Folios specialize in certain markers")
        print(f"  Entropy {mean_entropy:.3f} below baseline {baseline_mean:.3f}")

    return result


def test_car_3_3_sister_proximity():
    """
    CAR-3.3: Sister Pair Proximity

    Question: Do sister pairs (ch-sh, ok-ot) appear near each other?

    Method:
    1. For each sister pair occurrence, measure distance to nearest sibling
    2. Compare to random baseline
    3. Calculate "switching cost"
    """
    print("\n" + "=" * 60)
    print("CAR-3.3: Sister Pair Proximity")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Get marker sequence
    marker_sequence = []
    for entry in entries:
        marker = get_dominant_marker(entry['tokens'])
        marker_sequence.append(marker)

    print(f"\nEntries: {len(marker_sequence)}")
    print(f"Sister pairs: {SISTER_PAIRS}")

    # For each sister pair, calculate distances to nearest sibling
    results_by_pair = {}

    for m1, m2 in SISTER_PAIRS:
        # Find all positions
        m1_positions = [i for i, m in enumerate(marker_sequence) if m == m1]
        m2_positions = [i for i, m in enumerate(marker_sequence) if m == m2]

        if not m1_positions or not m2_positions:
            continue

        # Calculate distances
        distances = []
        for pos in m1_positions:
            # Find nearest m2
            min_dist = min(abs(pos - p2) for p2 in m2_positions)
            distances.append(min_dist)
        for pos in m2_positions:
            # Find nearest m1
            min_dist = min(abs(pos - p1) for p1 in m1_positions)
            distances.append(min_dist)

        mean_dist = np.mean(distances)
        median_dist = np.median(distances)

        print(f"\n{m1}-{m2} pair:")
        print(f"  {m1} occurrences: {len(m1_positions)}")
        print(f"  {m2} occurrences: {len(m2_positions)}")
        print(f"  Mean distance to sibling: {mean_dist:.2f}")
        print(f"  Median distance: {median_dist:.1f}")

        results_by_pair[(m1, m2)] = {
            'm1_count': len(m1_positions),
            'm2_count': len(m2_positions),
            'mean_distance': mean_dist,
            'median_distance': median_dist,
            'distances': distances
        }

    # Calculate switching cost: when marker changes, what % goes to sibling?
    print("\nSwitching analysis:")
    switches = defaultdict(Counter)

    for i in range(len(marker_sequence) - 1):
        m1, m2 = marker_sequence[i], marker_sequence[i+1]
        if m1 and m2 and m1 != m2:
            switches[m1][m2] += 1

    # Sister vs non-sister switches
    for m1, m2 in SISTER_PAIRS:
        total_from_m1 = sum(switches[m1].values())
        to_sister = switches[m1].get(m2, 0)

        total_from_m2 = sum(switches[m2].values())
        from_sister = switches[m2].get(m1, 0)

        if total_from_m1 > 0:
            pct_to_sister = 100 * to_sister / total_from_m1
            print(f"  {m1} -> {m2}: {to_sister}/{total_from_m1} = {pct_to_sister:.1f}%")
        if total_from_m2 > 0:
            pct_from_sister = 100 * from_sister / total_from_m2
            print(f"  {m2} -> {m1}: {from_sister}/{total_from_m2} = {pct_from_sister:.1f}%")

    # Shuffled baseline
    print("\nComputing shuffled baseline (1000 permutations)...")
    shuffled_distances = {pair: [] for pair in SISTER_PAIRS}

    for _ in range(1000):
        shuffled = marker_sequence.copy()
        random.shuffle(shuffled)

        for m1, m2 in SISTER_PAIRS:
            m1_pos = [i for i, m in enumerate(shuffled) if m == m1]
            m2_pos = [i for i, m in enumerate(shuffled) if m == m2]

            if m1_pos and m2_pos:
                dists = []
                for pos in m1_pos:
                    dists.append(min(abs(pos - p2) for p2 in m2_pos))
                for pos in m2_pos:
                    dists.append(min(abs(pos - p1) for p1 in m1_pos))
                shuffled_distances[(m1, m2)].append(np.mean(dists))

    # Compare to baseline
    print("\nComparison to baseline:")
    all_p_values = []

    for (m1, m2), data in results_by_pair.items():
        baseline = shuffled_distances[(m1, m2)]
        if baseline:
            baseline_mean = np.mean(baseline)
            baseline_std = np.std(baseline)
            effect_size = (data['mean_distance'] - baseline_mean) / baseline_std if baseline_std > 0 else 0
            p_value = np.mean([d <= data['mean_distance'] for d in baseline])
            all_p_values.append(p_value)

            print(f"\n{m1}-{m2}:")
            print(f"  Observed distance: {data['mean_distance']:.2f}")
            print(f"  Baseline distance: {baseline_mean:.2f} +/- {baseline_std:.2f}")
            print(f"  Effect size: {effect_size:.2f}")
            print(f"  P-value (closer than random): {p_value:.4f}")

            data['baseline_mean'] = baseline_mean
            data['baseline_std'] = baseline_std
            data['effect_size'] = effect_size
            data['p_value'] = p_value

    min_p = min(all_p_values) if all_p_values else 1.0

    result = {
        'test_id': 'CAR-3.3',
        'test_name': 'Sister Pair Proximity',
        'n_entries': len(marker_sequence),
        'sister_pairs': [(m1, m2) for m1, m2 in SISTER_PAIRS],
        'pair_results': {f"{m1}-{m2}": {k: v for k, v in data.items() if k != 'distances'}
                        for (m1, m2), data in results_by_pair.items()},
        'min_p_value': min_p,
        'verdict': 'SIGNIFICANT' if min_p < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Sister pairs appear closer than random")

    return result


def test_car_3_4_index_tokens():
    """
    CAR-3.4: Index Token Detection

    Question: Are there tokens that mark entry beginnings or endings?

    Method:
    1. Calculate position distribution for each token type
    2. Identify tokens strongly enriched at line-initial or line-final
    3. Compare to shuffled baseline
    """
    print("\n" + "=" * 60)
    print("CAR-3.4: Index Token Detection")
    print("=" * 60)

    loader = CARDataLoader().load()
    entries = loader.get_a_entries()

    # Count tokens by position
    initial_counts = Counter()
    final_counts = Counter()
    all_counts = Counter()

    for entry in entries:
        tokens = entry['tokens']
        if tokens:
            initial_counts[tokens[0]] += 1
            final_counts[tokens[-1]] += 1
            for t in tokens:
                all_counts[t] += 1

    total_entries = len(entries)

    # Calculate enrichment ratios
    print(f"\nTotal entries: {total_entries}")
    print(f"Unique tokens: {len(all_counts)}")

    # Tokens enriched at initial position
    print("\nTokens enriched at INITIAL position:")
    initial_enriched = []
    for token, count in all_counts.most_common(100):
        init_count = initial_counts.get(token, 0)
        expected = count / (sum(len(e['tokens']) for e in entries) / total_entries)
        if expected > 0:
            ratio = init_count / expected
            if ratio > 2.0 and init_count >= 5:
                initial_enriched.append((token, init_count, expected, ratio))

    for token, init_count, expected, ratio in sorted(initial_enriched, key=lambda x: -x[3])[:10]:
        print(f"  {token}: {init_count} initial vs {expected:.1f} expected ({ratio:.2f}x)")

    # Tokens enriched at final position
    print("\nTokens enriched at FINAL position:")
    final_enriched = []
    for token, count in all_counts.most_common(100):
        final_count = final_counts.get(token, 0)
        expected = count / (sum(len(e['tokens']) for e in entries) / total_entries)
        if expected > 0:
            ratio = final_count / expected
            if ratio > 2.0 and final_count >= 5:
                final_enriched.append((token, final_count, expected, ratio))

    for token, final_count, expected, ratio in sorted(final_enriched, key=lambda x: -x[3])[:10]:
        print(f"  {token}: {final_count} final vs {expected:.1f} expected ({ratio:.2f}x)")

    # Chi-square test for position dependence
    # Build contingency table: top 20 tokens x {initial, internal, final}
    top_tokens = [t for t, _ in all_counts.most_common(20)]
    contingency = []

    for token in top_tokens:
        init = initial_counts.get(token, 0)
        final = final_counts.get(token, 0)
        total = all_counts[token]
        internal = total - init - final

        if internal < 0:
            internal = 0  # Edge case for very short entries

        contingency.append([init, internal, final])

    contingency = np.array(contingency)
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency + 1)

    print(f"\nChi-square test (top 20 tokens x position):")
    print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p_val:.6f}")

    result = {
        'test_id': 'CAR-3.4',
        'test_name': 'Index Token Detection',
        'n_entries': total_entries,
        'n_unique_tokens': len(all_counts),
        'initial_enriched': [(t, int(c), float(r)) for t, c, _, r in initial_enriched[:10]],
        'final_enriched': [(t, int(c), float(r)) for t, c, _, r in final_enriched[:10]],
        'chi2': chi2,
        'p_value': p_val,
        'dof': dof,
        'verdict': 'SIGNIFICANT' if p_val < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  Token position distribution is non-random")
        print(f"  Found {len(initial_enriched)} initial-enriched, {len(final_enriched)} final-enriched tokens")

    return result


def run_track3():
    """Run all Track 3 tests."""
    print("\n" + "=" * 70)
    print("TRACK 3: ENTRY ORGANIZATION & LOOKUP")
    print("=" * 70)

    results = {
        'track': 3,
        'name': 'Entry Organization & Lookup',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-3.1'] = test_car_3_1_marker_runs()
    results['tests']['CAR-3.2'] = test_car_3_2_folio_concentration()
    results['tests']['CAR-3.3'] = test_car_3_3_sister_proximity()
    results['tests']['CAR-3.4'] = test_car_3_4_index_tokens()

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 3 SUMMARY")
    print("=" * 70)

    significant = sum(1 for t in results['tests'].values()
                     if t.get('verdict') == 'SIGNIFICANT')
    null = sum(1 for t in results['tests'].values()
              if t.get('verdict') == 'NULL')

    print(f"\nTests passed (SIGNIFICANT): {significant}/4")
    print(f"Tests failed (NULL): {null}/4")

    for test_id, test in results['tests'].items():
        print(f"\n{test_id}: {test.get('test_name', 'Unknown')}")
        print(f"  Verdict: {test.get('verdict', 'N/A')}")

    # Track verdict
    if significant >= 3:
        results['track_verdict'] = 'SUCCESS'
        print("\n-> TRACK 3 VERDICT: SUCCESS")
        print("  Entry organization patterns confirmed")
    elif significant >= 1:
        results['track_verdict'] = 'PARTIAL'
        print("\n-> TRACK 3 VERDICT: PARTIAL")
        print("  Some organization patterns exist")
    else:
        results['track_verdict'] = 'NULL'
        print("\n-> TRACK 3 VERDICT: NULL")
        print("  No organization patterns detected")

    # Save results
    output_file = PHASE_DIR / 'car_track3_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_track3()
