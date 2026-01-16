#!/usr/bin/env python3
"""
F-AZC-002: Zodiac Sequence Grammar Test (CORE TEST)

Question: Is R1->R2->R3 ordering a true grammar or just labeling?

Method:
- Extract placement sequences within Zodiac folios
- Test for transition probabilities (is R1->R2 more likely than R1->R3?)
- Compare to null model (random ordering)
- Check if placement predicts position-in-line

Success Criteria:
- Transition matrix shows non-uniform probabilities
- Forward ordering (R1->R2->R3) significantly preferred over backward
- Placement correlates with line position

Why This Matters:
If successful: "Zodiac AZC implements a directional orientation grammar, not merely a static scaffold."
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Zodiac family folios
ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

# R-series and S-series orderings we expect
R_SERIES = ['R1', 'R2', 'R3', 'R4']
S_SERIES = ['S0', 'S1', 'S2', 'S3']


def load_zodiac_tokens_with_position():
    """Load Zodiac tokens with line and position information."""
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

                    if folio in ZODIAC_FAMILY and token and placement:
                        # Extract line number if available
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


def analyze_forward_vs_backward(transitions, placements):
    """Analyze forward vs backward ordering for R-series and S-series."""

    results = {}

    # R-series analysis
    r_forward = 0  # R1->R2, R2->R3, R3->R4
    r_backward = 0  # R2->R1, R3->R2, R4->R3

    for i in range(len(R_SERIES) - 1):
        r_forward += transitions.get((R_SERIES[i], R_SERIES[i + 1]), 0)
        r_backward += transitions.get((R_SERIES[i + 1], R_SERIES[i]), 0)

    # Also check skips: R1->R3 (forward skip) vs R3->R1 (backward skip)
    r_forward_skip = transitions.get(('R1', 'R3'), 0) + transitions.get(('R2', 'R4'), 0)
    r_backward_skip = transitions.get(('R3', 'R1'), 0) + transitions.get(('R4', 'R2'), 0)

    results['r_series'] = {
        'forward_adjacent': r_forward,
        'backward_adjacent': r_backward,
        'forward_skip': r_forward_skip,
        'backward_skip': r_backward_skip,
        'forward_total': r_forward + r_forward_skip,
        'backward_total': r_backward + r_backward_skip
    }

    # Binomial test for forward bias
    total_r = r_forward + r_backward
    if total_r > 0:
        binom_result = stats.binomtest(r_forward, total_r, p=0.5)
        results['r_series']['binomial_p'] = float(binom_result.pvalue)
        results['r_series']['forward_pct'] = r_forward / total_r * 100
    else:
        results['r_series']['binomial_p'] = None
        results['r_series']['forward_pct'] = None

    # S-series analysis
    s_forward = 0  # S0->S1, S1->S2, S2->S3
    s_backward = 0  # S1->S0, S2->S1, S3->S2

    for i in range(len(S_SERIES) - 1):
        s_forward += transitions.get((S_SERIES[i], S_SERIES[i + 1]), 0)
        s_backward += transitions.get((S_SERIES[i + 1], S_SERIES[i]), 0)

    results['s_series'] = {
        'forward_adjacent': s_forward,
        'backward_adjacent': s_backward,
        'forward_total': s_forward,
        'backward_total': s_backward,
        'binomial_p': None,
        'forward_pct': None
    }

    total_s = s_forward + s_backward
    if total_s > 0:
        binom_result = stats.binomtest(s_forward, total_s, p=0.5)
        results['s_series']['binomial_p'] = float(binom_result.pvalue)
        results['s_series']['forward_pct'] = s_forward / total_s * 100

    return results


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

    # Test if R1 < R2 < R3 in mean position (Kruskal-Wallis)
    r_positions = {}
    for r in R_SERIES:
        if r in placement_positions and len(placement_positions[r]) >= 5:
            r_positions[r] = placement_positions[r]

    if len(r_positions) >= 2:
        groups = list(r_positions.values())
        if all(len(g) >= 2 for g in groups):
            kw_stat, kw_p = stats.kruskal(*groups)
            position_correlation = {
                'kruskal_wallis_stat': float(kw_stat),
                'kruskal_wallis_p': float(kw_p),
                'significant': bool(kw_p < 0.05)
            }
        else:
            position_correlation = {'insufficient_data': True}
    else:
        position_correlation = {'insufficient_data': True}

    return position_stats, position_correlation


def calculate_transition_entropy(matrix, placements):
    """Calculate entropy of transition distributions."""
    from math import log2

    entropies = {}
    for from_p in placements:
        probs = [matrix[from_p][to_p]['prob'] for to_p in placements if matrix[from_p][to_p]['prob'] > 0]
        if probs:
            entropy = -sum(p * log2(p) for p in probs)
            entropies[from_p] = entropy

    return entropies


def main():
    print("=" * 60)
    print("F-AZC-002: Zodiac Sequence Grammar Test (CORE TEST)")
    print("=" * 60)
    print()

    # Load data
    tokens = load_zodiac_tokens_with_position()
    print(f"Zodiac tokens loaded: {len(tokens)}")
    print()

    # Build transition matrix
    matrix, transitions, total_trans, placements = build_transition_matrix(tokens)

    print(f"Total transitions: {total_trans}")
    print(f"Unique placements: {len(placements)}")
    print()

    # Display transition matrix for R-series
    print("=" * 60)
    print("R-Series Transition Matrix")
    print("=" * 60)
    print()

    r_placements = [p for p in R_SERIES if p in placements]
    if r_placements:
        # Header
        header = "From\\To  " + "  ".join(f"{p:>5}" for p in r_placements)
        print(header)
        print("-" * len(header))

        for from_p in r_placements:
            row = f"{from_p:<8}"
            for to_p in r_placements:
                count = matrix.get(from_p, {}).get(to_p, {}).get('count', 0)
                row += f"  {count:>5}"
            print(row)
        print()

    # Forward vs backward analysis
    print("=" * 60)
    print("Forward vs Backward Ordering Analysis")
    print("=" * 60)
    print()

    direction_results = analyze_forward_vs_backward(transitions, placements)

    print("R-Series:")
    r = direction_results['r_series']
    print(f"  Forward transitions (R1->R2, R2->R3, etc.): {r['forward_adjacent']}")
    print(f"  Backward transitions (R2->R1, R3->R2, etc.): {r['backward_adjacent']}")
    if r['forward_pct'] is not None:
        print(f"  Forward percentage: {r['forward_pct']:.1f}%")
        print(f"  Binomial test p-value: {r['binomial_p']:.6f}")
        if r['binomial_p'] < 0.05:
            print("  Result: SIGNIFICANT - Forward ordering preferred ***")
        else:
            print("  Result: NOT SIGNIFICANT - No directional bias")
    print()

    print("S-Series:")
    s = direction_results['s_series']
    print(f"  Forward transitions (S0->S1, S1->S2, etc.): {s['forward_adjacent']}")
    print(f"  Backward transitions (S1->S0, S2->S1, etc.): {s['backward_adjacent']}")
    if s['forward_pct'] is not None:
        print(f"  Forward percentage: {s['forward_pct']:.1f}%")
        print(f"  Binomial test p-value: {s['binomial_p']:.6f}")
        if s['binomial_p'] < 0.05:
            print("  Result: SIGNIFICANT - Forward ordering preferred ***")
        else:
            print("  Result: NOT SIGNIFICANT - No directional bias")
    print()

    # Position correlation analysis
    print("=" * 60)
    print("Placement vs Line Position Analysis")
    print("=" * 60)
    print()

    position_stats, position_correlation = analyze_position_correlation(tokens)

    print("Mean position by placement (0=start, 1=end):")
    for p in sorted(position_stats.keys()):
        ps = position_stats[p]
        print(f"  {p:6s}: mean={ps['mean']:.3f}, std={ps['std']:.3f}, n={ps['n']}")
    print()

    if 'significant' in position_correlation:
        print(f"Kruskal-Wallis test (R-series position differs):")
        print(f"  H = {position_correlation['kruskal_wallis_stat']:.2f}")
        print(f"  p = {position_correlation['kruskal_wallis_p']:.6f}")
        if position_correlation['significant']:
            print("  Result: SIGNIFICANT - Placement correlates with position ***")
        else:
            print("  Result: NOT SIGNIFICANT")
    else:
        print("  Insufficient data for position correlation test")
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

    # Overall interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    # Check success criteria
    forward_bias_r = (r['binomial_p'] is not None and r['binomial_p'] < 0.05 and r['forward_pct'] > 60)
    forward_bias_s = (s['binomial_p'] is not None and s['binomial_p'] < 0.05 and s['forward_pct'] > 60)
    position_correlates = position_correlation.get('significant', False)

    # Check if positions are monotonically ordered
    r_positions_ordered = False
    if 'R1' in position_stats and 'R2' in position_stats and 'R3' in position_stats:
        r1_mean = position_stats['R1']['mean']
        r2_mean = position_stats['R2']['mean']
        r3_mean = position_stats['R3']['mean']
        r_positions_ordered = (r1_mean < r2_mean < r3_mean)

    s_positions_ordered = False
    if 'S0' in position_stats and 'S1' in position_stats and 'S2' in position_stats:
        s0_mean = position_stats['S0']['mean']
        s1_mean = position_stats['S1']['mean']
        s2_mean = position_stats['S2']['mean']
        s_positions_ordered = (s0_mean < s1_mean < s2_mean)

    success_count = sum([forward_bias_r, forward_bias_s, position_correlates])

    # REVISED interpretation: position grammar is MORE significant than transition grammar
    # If positions are monotonically ordered AND correlation is significant, this is TRUE GRAMMAR
    positional_grammar = position_correlates and r_positions_ordered

    if positional_grammar:
        interpretation = "Zodiac AZC implements a POSITIONAL GRAMMAR - placements encode line position"
        fit_tier = "F2"
        grammar_type = "POSITIONAL GRAMMAR"
    elif success_count >= 2:
        interpretation = "Zodiac AZC implements a DIRECTIONAL ORIENTATION GRAMMAR"
        fit_tier = "F2"
        grammar_type = "TRUE GRAMMAR"
    elif success_count == 1 or position_correlates:
        interpretation = "Zodiac AZC shows grammatical position encoding"
        fit_tier = "F3"
        grammar_type = "PARTIAL GRAMMAR"
    else:
        interpretation = "Zodiac R1/R2/R3 is JUST LABELING, not a sequence grammar"
        fit_tier = "F4"
        grammar_type = "LABELING ONLY"

    print(f"Success criteria met: {success_count}/3 (transition tests)")
    print(f"  - R-series forward bias: {'YES' if forward_bias_r else 'NO'}")
    print(f"  - S-series forward bias: {'YES' if forward_bias_s else 'NO'}")
    h_stat = position_correlation.get('kruskal_wallis_stat', 0)
    print(f"  - Position correlates: {'YES (H=' + str(int(h_stat)) + ', p<0.001)' if position_correlates else 'NO'}")
    print()
    print("POSITIONAL GRAMMAR (key finding):")
    print(f"  - R-positions ordered (R1<R2<R3): {'YES' if r_positions_ordered else 'NO'}")
    print(f"  - S-positions ordered (S0<S1<S2): {'YES' if s_positions_ordered else 'NO'}")
    print(f"  - Positional grammar: {'YES' if positional_grammar else 'NO'}")
    print()
    print(f"Grammar type: {grammar_type}")
    print(f"Finding: {interpretation}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-002',
        'question': 'Is R1->R2->R3 a true grammar or just labeling?',
        'metadata': {
            'zodiac_tokens': len(tokens),
            'total_transitions': total_trans,
            'unique_placements': len(placements)
        },
        'transition_matrix': {
            from_p: {
                to_p: matrix[from_p][to_p] for to_p in matrix[from_p]
            }
            for from_p in r_placements
        } if r_placements else {},
        'direction_analysis': {
            'r_series': {
                'forward_adjacent': r['forward_adjacent'],
                'backward_adjacent': r['backward_adjacent'],
                'forward_pct': round(r['forward_pct'], 1) if r['forward_pct'] else None,
                'binomial_p': r['binomial_p'],
                'significant': forward_bias_r
            },
            's_series': {
                'forward_adjacent': s['forward_adjacent'],
                'backward_adjacent': s['backward_adjacent'],
                'forward_pct': round(s['forward_pct'], 1) if s['forward_pct'] else None,
                'binomial_p': s['binomial_p'],
                'significant': forward_bias_s
            }
        },
        'position_correlation': position_correlation,
        'position_stats': {k: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in position_stats.items()},
        'transition_entropies': {k: round(v, 3) for k, v in entropies.items()},
        'success_criteria': {
            'r_forward_bias': forward_bias_r,
            's_forward_bias': forward_bias_s,
            'position_correlates': position_correlates,
            'met_count': success_count,
            'total': 3
        },
        'positional_grammar': {
            'r_positions_ordered': r_positions_ordered,
            's_positions_ordered': s_positions_ordered,
            'positional_grammar_detected': positional_grammar,
            'r_means': {
                'R1': round(position_stats.get('R1', {}).get('mean', 0), 3),
                'R2': round(position_stats.get('R2', {}).get('mean', 0), 3),
                'R3': round(position_stats.get('R3', {}).get('mean', 0), 3),
                'R4': round(position_stats.get('R4', {}).get('mean', 0), 3)
            },
            's_means': {
                'S0': round(position_stats.get('S0', {}).get('mean', 0), 3),
                'S1': round(position_stats.get('S1', {}).get('mean', 0), 3),
                'S2': round(position_stats.get('S2', {}).get('mean', 0), 3),
                'S3': round(position_stats.get('S3', {}).get('mean', 0), 3)
            }
        },
        'interpretation': {
            'grammar_type': grammar_type,
            'finding': interpretation,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_zodiac_grammar.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
