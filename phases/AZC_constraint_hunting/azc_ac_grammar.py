#!/usr/bin/env python3
"""
F-AZC-005: A/C Positional Grammar Test (DECISIVE)

Question: Does A/C also show positional grammar like Zodiac?

Method (same as F-AZC-002):
- Extract placement sequences within A/C folios
- Test monotonic ordering of C, P, R, S placements
- Test transition entropy and asymmetry
- Check if placement predicts position-in-line
- Compare forward vs backward likelihood

Success Criteria:
- If A/C shows monotonic position ordering -> AZC = ONE grammar, two parameter regimes
- If A/C does NOT show ordering -> AZC = TWO fundamentally different systems

Why This Matters:
This is the DECISIVE test. It resolves system unity.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np
from math import log2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# A/C family folios
AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

# A/C uses unsubscripted placements - expected order if positional
AC_PLACEMENTS_EXPECTED_ORDER = ['C', 'P', 'R', 'S']


def load_ac_tokens_with_position():
    """Load A/C tokens with line and position information."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if folio in AC_FAMILY and token and placement:
                        line_info = parts[3].strip('"').strip() if len(parts) > 3 else ''
                        word_pos = parts[4].strip('"').strip() if len(parts) > 4 else ''

                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'placement': placement,
                            'line': line_info,
                            'word_pos': word_pos
                        })
    return tokens


def build_transition_matrix(tokens):
    """Build placement transition matrix from token sequences."""

    # Group by folio and line
    sequences = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line'])
        sequences[key].append(t['placement'])

    # Count transitions
    transitions = Counter()
    total_transitions = 0

    for key, seq in sequences.items():
        for i in range(len(seq) - 1):
            from_p = seq[i]
            to_p = seq[i + 1]
            transitions[(from_p, to_p)] += 1
            total_transitions += 1

    # Build matrix
    placements = sorted(set(p for seq in sequences.values() for p in seq))

    matrix = {}
    for from_p in placements:
        matrix[from_p] = {}
        from_total = sum(transitions.get((from_p, to_p), 0) for to_p in placements)
        for to_p in placements:
            count = transitions.get((from_p, to_p), 0)
            prob = count / from_total if from_total > 0 else 0
            matrix[from_p][to_p] = {'count': count, 'prob': prob}

    return matrix, transitions, total_transitions, placements


def analyze_position_correlation(tokens):
    """Analyze correlation between placement and position within line."""

    # Group by folio and line
    sequences = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line'])
        sequences[key].append(t['placement'])

    # For each sequence, record position (normalized 0-1) for each placement
    placement_positions = defaultdict(list)

    for key, seq in sequences.items():
        n = len(seq)
        if n < 2:
            continue
        for i, p in enumerate(seq):
            norm_pos = i / (n - 1)  # Normalize to [0, 1]
            placement_positions[p].append(norm_pos)

    # Calculate mean position for each placement
    position_stats = {}
    for p, positions in placement_positions.items():
        if len(positions) >= 5:
            position_stats[p] = {
                'mean': float(np.mean(positions)),
                'std': float(np.std(positions)),
                'n': len(positions)
            }

    # Test if placements differ in position (Kruskal-Wallis across all placements)
    all_groups = [placement_positions[p] for p in AC_PLACEMENTS_EXPECTED_ORDER if p in placement_positions and len(placement_positions[p]) >= 5]

    if len(all_groups) >= 2 and all(len(g) >= 2 for g in all_groups):
        kw_stat, kw_p = stats.kruskal(*all_groups)
        position_correlation = {
            'kruskal_wallis_stat': float(kw_stat),
            'kruskal_wallis_p': float(kw_p),
            'significant': bool(kw_p < 0.05)
        }
    else:
        position_correlation = {'insufficient_data': True}

    return position_stats, position_correlation, placement_positions


def test_monotonic_ordering(position_stats, expected_order):
    """Test if placements follow monotonic ordering in line position."""

    # Get mean positions for expected order placements
    means = []
    for p in expected_order:
        if p in position_stats:
            means.append((p, position_stats[p]['mean']))

    if len(means) < 2:
        return {
            'monotonic': False,
            'insufficient_data': True,
            'pairs_tested': 0
        }

    # Check monotonicity
    monotonic_increasing = True
    monotonic_decreasing = True
    pairs_in_order = 0
    pairs_out_of_order = 0

    for i in range(len(means) - 1):
        if means[i][1] < means[i+1][1]:
            pairs_in_order += 1
            monotonic_decreasing = False
        elif means[i][1] > means[i+1][1]:
            pairs_out_of_order += 1
            monotonic_increasing = False
        # Equal means count as neither

    return {
        'monotonic': monotonic_increasing or monotonic_decreasing,
        'increasing': monotonic_increasing,
        'decreasing': monotonic_decreasing,
        'pairs_in_order': pairs_in_order,
        'pairs_out_of_order': pairs_out_of_order,
        'pairs_tested': len(means) - 1,
        'order_found': [m[0] for m in sorted(means, key=lambda x: x[1])]
    }


def analyze_transition_asymmetry(transitions, placements):
    """Analyze forward vs backward transition bias."""

    # For each pair of placements, compare P(A->B) vs P(B->A)
    forward_total = 0
    backward_total = 0
    asymmetries = []

    for i, p1 in enumerate(AC_PLACEMENTS_EXPECTED_ORDER):
        for j, p2 in enumerate(AC_PLACEMENTS_EXPECTED_ORDER):
            if i < j:  # p1 comes before p2 in expected order
                forward = transitions.get((p1, p2), 0)
                backward = transitions.get((p2, p1), 0)
                forward_total += forward
                backward_total += backward

                if forward + backward > 0:
                    asymmetries.append({
                        'from': p1,
                        'to': p2,
                        'forward': forward,
                        'backward': backward,
                        'forward_pct': forward / (forward + backward) * 100
                    })

    total = forward_total + backward_total
    if total > 0:
        forward_pct = forward_total / total * 100
        binom_result = stats.binomtest(forward_total, total, p=0.5)
        return {
            'forward_total': forward_total,
            'backward_total': backward_total,
            'forward_pct': forward_pct,
            'binomial_p': float(binom_result.pvalue),
            'significant': bool(binom_result.pvalue < 0.05),
            'asymmetries': asymmetries
        }
    else:
        return {
            'forward_total': 0,
            'backward_total': 0,
            'forward_pct': None,
            'binomial_p': None,
            'significant': False,
            'asymmetries': []
        }


def calculate_transition_entropy(matrix, placements):
    """Calculate entropy of transition distributions."""

    entropies = {}
    for from_p in placements:
        if from_p not in matrix:
            continue
        probs = [matrix[from_p][to_p]['prob'] for to_p in placements if to_p in matrix[from_p] and matrix[from_p][to_p]['prob'] > 0]
        if probs:
            entropy = -sum(p * log2(p) for p in probs)
            entropies[from_p] = entropy

    return entropies


def main():
    print("=" * 60)
    print("F-AZC-005: A/C Positional Grammar Test (DECISIVE)")
    print("=" * 60)
    print()

    # Load data
    tokens = load_ac_tokens_with_position()
    print(f"A/C tokens loaded: {len(tokens)}")
    print()

    # Build transition matrix
    matrix, transitions, total_trans, placements = build_transition_matrix(tokens)

    print(f"Total transitions: {total_trans}")
    print(f"Unique placements: {len(placements)}")
    print(f"Placements found: {sorted(placements)}")
    print()

    # Display transition matrix for key A/C placements
    print("=" * 60)
    print("A/C Transition Matrix (C, P, R, S)")
    print("=" * 60)
    print()

    ac_placements = [p for p in AC_PLACEMENTS_EXPECTED_ORDER if p in placements]
    if ac_placements:
        header = "From\\To  " + "  ".join(f"{p:>6}" for p in ac_placements)
        print(header)
        print("-" * len(header))

        for from_p in ac_placements:
            row = f"{from_p:<8}"
            for to_p in ac_placements:
                count = matrix.get(from_p, {}).get(to_p, {}).get('count', 0)
                row += f"  {count:>6}"
            print(row)
        print()

    # Position correlation analysis
    print("=" * 60)
    print("Placement vs Line Position Analysis")
    print("=" * 60)
    print()

    position_stats, position_correlation, placement_positions = analyze_position_correlation(tokens)

    print("Mean position by placement (0=start, 1=end):")
    for p in sorted(position_stats.keys()):
        ps = position_stats[p]
        print(f"  {p:6s}: mean={ps['mean']:.3f}, std={ps['std']:.3f}, n={ps['n']}")
    print()

    if 'significant' in position_correlation:
        print(f"Kruskal-Wallis test (placement positions differ):")
        print(f"  H = {position_correlation['kruskal_wallis_stat']:.2f}")
        print(f"  p = {position_correlation['kruskal_wallis_p']:.6f}")
        if position_correlation['significant']:
            print("  Result: SIGNIFICANT - Placement correlates with position ***")
        else:
            print("  Result: NOT SIGNIFICANT")
    else:
        print("  Insufficient data for position correlation test")
    print()

    # Monotonicity test
    print("=" * 60)
    print("Monotonic Ordering Test")
    print("=" * 60)
    print()

    monotonicity = test_monotonic_ordering(position_stats, AC_PLACEMENTS_EXPECTED_ORDER)

    if monotonicity.get('insufficient_data'):
        print("Insufficient data for monotonicity test")
    else:
        print(f"Pairs tested: {monotonicity['pairs_tested']}")
        print(f"Pairs in expected order: {monotonicity['pairs_in_order']}")
        print(f"Pairs out of order: {monotonicity['pairs_out_of_order']}")
        print(f"Monotonic: {'YES' if monotonicity['monotonic'] else 'NO'}")
        print(f"Actual order found: {' < '.join(monotonicity['order_found'])}")
    print()

    # Transition asymmetry
    print("=" * 60)
    print("Transition Asymmetry Analysis")
    print("=" * 60)
    print()

    asymmetry = analyze_transition_asymmetry(transitions, placements)

    print(f"Forward transitions (expected order): {asymmetry['forward_total']}")
    print(f"Backward transitions (reverse order): {asymmetry['backward_total']}")
    if asymmetry['forward_pct'] is not None:
        print(f"Forward percentage: {asymmetry['forward_pct']:.1f}%")
        print(f"Binomial p-value: {asymmetry['binomial_p']:.6f}")
        if asymmetry['significant']:
            print("Result: SIGNIFICANT - Transition asymmetry detected ***")
        else:
            print("Result: NOT SIGNIFICANT - No strong asymmetry")
    print()

    if asymmetry['asymmetries']:
        print("Detailed asymmetries:")
        for a in asymmetry['asymmetries']:
            print(f"  {a['from']}->{a['to']}: {a['forward']} forward, {a['backward']} backward ({a['forward_pct']:.1f}% forward)")
    print()

    # Transition entropy
    print("=" * 60)
    print("Transition Entropy")
    print("=" * 60)
    print()

    entropies = calculate_transition_entropy(matrix, placements)
    for p in sorted(entropies.keys()):
        print(f"  {p:6s}: {entropies[p]:.2f} bits")
    print()

    # DECISIVE INTERPRETATION
    print("=" * 60)
    print("DECISIVE INTERPRETATION")
    print("=" * 60)
    print()

    # Criteria for positional grammar:
    # 1. Position correlation significant
    # 2. Monotonic ordering present
    # 3. Transition asymmetry (optional, strengthens conclusion)

    position_significant = position_correlation.get('significant', False)
    has_monotonic = monotonicity.get('monotonic', False) and not monotonicity.get('insufficient_data', False)
    has_asymmetry = asymmetry.get('significant', False)

    evidence_count = sum([position_significant, has_monotonic, has_asymmetry])

    print(f"Evidence for positional grammar: {evidence_count}/3")
    print(f"  - Position correlation: {'YES' if position_significant else 'NO'}")
    print(f"  - Monotonic ordering: {'YES' if has_monotonic else 'NO'}")
    print(f"  - Transition asymmetry: {'YES' if has_asymmetry else 'NO'}")
    print()

    # DECISIVE CONCLUSION
    if evidence_count >= 2:
        conclusion = "A/C HAS POSITIONAL GRAMMAR"
        system_unity = "AZC = ONE UNIFIED SYSTEM with two parameter regimes"
        fit_tier = "F2"
    elif evidence_count == 1:
        conclusion = "A/C shows WEAK positional structure"
        system_unity = "AZC = PARTIALLY UNIFIED (some shared grammar)"
        fit_tier = "F3"
    else:
        conclusion = "A/C LACKS POSITIONAL GRAMMAR"
        system_unity = "AZC = TWO DISTINCT SYSTEMS (bifurcated by design)"
        fit_tier = "F2"  # Still F2 because it's a decisive answer

    print(f"CONCLUSION: {conclusion}")
    print(f"SYSTEM UNITY: {system_unity}")
    print(f"Fit tier: {fit_tier}")
    print()

    # Compare to Zodiac
    print("=" * 60)
    print("COMPARISON TO ZODIAC (F-AZC-002)")
    print("=" * 60)
    print()
    print("Zodiac results (from F-AZC-002):")
    print("  - Position correlation: H=927.48, p<0.000001 (SIGNIFICANT)")
    print("  - R-series monotonic: R1<R2<R3<R4 (YES)")
    print("  - S-series monotonic: S0<S1<S2<S3 (YES)")
    print()
    print(f"A/C results (this test):")
    if 'kruskal_wallis_stat' in position_correlation:
        print(f"  - Position correlation: H={position_correlation['kruskal_wallis_stat']:.2f}, p={position_correlation['kruskal_wallis_p']:.6f} ({'SIGNIFICANT' if position_significant else 'NOT SIGNIFICANT'})")
    print(f"  - Monotonic: {'YES - ' + ' < '.join(monotonicity.get('order_found', [])) if has_monotonic else 'NO'}")
    print()

    # Prepare output
    output = {
        'fit_id': 'F-AZC-005',
        'question': 'Does A/C show positional grammar like Zodiac?',
        'decisive': True,
        'metadata': {
            'ac_tokens': len(tokens),
            'total_transitions': total_trans,
            'unique_placements': len(placements),
            'placements_found': sorted(placements)
        },
        'position_correlation': position_correlation,
        'position_stats': {k: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in position_stats.items()},
        'monotonicity': {
            'monotonic': monotonicity.get('monotonic', False),
            'pairs_tested': monotonicity.get('pairs_tested', 0),
            'pairs_in_order': monotonicity.get('pairs_in_order', 0),
            'pairs_out_of_order': monotonicity.get('pairs_out_of_order', 0),
            'order_found': monotonicity.get('order_found', [])
        },
        'transition_asymmetry': {
            'forward_total': asymmetry['forward_total'],
            'backward_total': asymmetry['backward_total'],
            'forward_pct': round(asymmetry['forward_pct'], 1) if asymmetry['forward_pct'] else None,
            'binomial_p': asymmetry['binomial_p'],
            'significant': asymmetry['significant']
        },
        'transition_entropies': {k: round(v, 3) for k, v in entropies.items()},
        'evidence': {
            'position_significant': position_significant,
            'has_monotonic': has_monotonic,
            'has_asymmetry': has_asymmetry,
            'evidence_count': evidence_count
        },
        'interpretation': {
            'conclusion': conclusion,
            'system_unity': system_unity,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_ac_grammar.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
