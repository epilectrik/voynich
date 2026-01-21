#!/usr/bin/env python3
"""
RI/PP Structure Analysis v2 - Using pre-classified token data

Uses token_data.json from A_INTERNAL_STRATIFICATION which has correct
MIDDLE extraction and classification.
"""

import json
import math
from collections import defaultdict, Counter

def entropy(counts):
    """Compute Shannon entropy from counts."""
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def load_data():
    """Load pre-classified token data."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
        tokens = json.load(f)

    # Group by line
    lines = defaultdict(list)
    for t in tokens:
        line_key = f"{t['folio']}.{t['line']}"
        lines[line_key].append(t)

    return tokens, lines


def main():
    print("=" * 70)
    print("RI/PP STRUCTURE ANALYSIS v2 - Using Pre-Classified Data")
    print("=" * 70)
    print()

    tokens, lines = load_data()

    # Count by class
    exclusive_tokens = [t for t in tokens if t['middle_class'] == 'exclusive']
    shared_tokens = [t for t in tokens if t['middle_class'] == 'shared']

    print(f"Total tokens: {len(tokens)}")
    print(f"  Exclusive (RI): {len(exclusive_tokens)} ({100*len(exclusive_tokens)/len(tokens):.1f}%)")
    print(f"  Shared (PP): {len(shared_tokens)} ({100*len(shared_tokens)/len(tokens):.1f}%)")
    print(f"Total lines: {len(lines)}")
    print()

    # RI per line distribution
    print("=" * 70)
    print("RI TOKENS PER LINE")
    print("=" * 70)
    print()

    ri_per_line = Counter()
    for line_key, line_tokens in lines.items():
        ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
        ri_per_line[ri_count] += 1

    for count in sorted(ri_per_line.keys()):
        n = ri_per_line[count]
        pct = 100 * n / len(lines)
        bar = '#' * int(pct / 2)
        print(f"  {count:2d} RI tokens: {n:4d} lines ({pct:5.1f}%) {bar}")

    print()
    print(f"Lines with 0 RI: {ri_per_line[0]} ({100*ri_per_line[0]/len(lines):.1f}%)")
    print(f"Lines with 1+ RI: {len(lines) - ri_per_line[0]} ({100*(len(lines)-ri_per_line[0])/len(lines):.1f}%)")
    print()

    # Mean RI per line
    total_ri = sum(count * n for count, n in ri_per_line.items())
    mean_ri = total_ri / len(lines)
    print(f"Mean RI per line: {mean_ri:.2f}")
    print()

    # R-1: Record typing
    print("=" * 70)
    print("TEST R-1: Record Typing by RI/PP Composition")
    print("=" * 70)
    print()

    ri_ratios = []
    for line_key, line_tokens in lines.items():
        ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
        total = len(line_tokens)
        ri_ratios.append(ri_count / total if total > 0 else 0)

    mean_ratio = sum(ri_ratios) / len(ri_ratios)
    print(f"Mean RI ratio: {mean_ratio:.3f} ({100*mean_ratio:.1f}%)")

    # Distribution
    ratio_bins = {'0-20%': 0, '20-40%': 0, '40-60%': 0, '60-80%': 0, '80-100%': 0}
    for ratio in ri_ratios:
        if ratio < 0.2:
            ratio_bins['0-20%'] += 1
        elif ratio < 0.4:
            ratio_bins['20-40%'] += 1
        elif ratio < 0.6:
            ratio_bins['40-60%'] += 1
        elif ratio < 0.8:
            ratio_bins['60-80%'] += 1
        else:
            ratio_bins['80-100%'] += 1

    print()
    print("RI Ratio Distribution:")
    for bin_name, count in ratio_bins.items():
        pct = 100 * count / len(ri_ratios)
        bar = '#' * int(pct / 2)
        print(f"  {bin_name}: {count:>4} ({pct:5.1f}%) {bar}")
    print()

    # R-2: Neighbor specificity
    print("=" * 70)
    print("TEST R-2: RI-PP Neighbor Specificity")
    print("=" * 70)
    print()

    # For each RI MIDDLE, collect PP neighbors
    ri_pp_neighbors = defaultdict(Counter)

    for line_key, line_tokens in lines.items():
        for i, t in enumerate(line_tokens):
            if t['middle_class'] == 'exclusive':
                ri_middle = t['middle']
                # Check left neighbor
                if i > 0 and line_tokens[i-1]['middle_class'] == 'shared':
                    ri_pp_neighbors[ri_middle][line_tokens[i-1]['middle']] += 1
                # Check right neighbor
                if i < len(line_tokens) - 1 and line_tokens[i+1]['middle_class'] == 'shared':
                    ri_pp_neighbors[ri_middle][line_tokens[i+1]['middle']] += 1

    # Compute entropy for each RI MIDDLE
    entropies = []
    for ri_middle, pp_counts in ri_pp_neighbors.items():
        if sum(pp_counts.values()) >= 3:
            ent = entropy(pp_counts)
            entropies.append({
                'middle': ri_middle,
                'entropy': ent,
                'n_neighbors': sum(pp_counts.values()),
                'n_unique_pp': len(pp_counts),
            })

    if entropies:
        mean_entropy = sum(e['entropy'] for e in entropies) / len(entropies)

        # Max entropy = log2(n_unique_pp_middles)
        all_pp_middles = set()
        for line_tokens in lines.values():
            for t in line_tokens:
                if t['middle_class'] == 'shared':
                    all_pp_middles.add(t['middle'])

        max_entropy = math.log2(len(all_pp_middles)) if all_pp_middles else 0

        print(f"RI MIDDLEs analyzed: {len(entropies)}")
        print(f"Mean neighbor entropy: {mean_entropy:.3f} bits")
        print(f"Max possible entropy: {max_entropy:.3f} bits")
        print(f"Entropy ratio: {mean_entropy/max_entropy:.3f}")
        print()

        if mean_entropy / max_entropy < 0.5:
            specificity = "HIGH SPECIFICITY"
        elif mean_entropy / max_entropy < 0.75:
            specificity = "MODERATE SPECIFICITY"
        else:
            specificity = "LOW SPECIFICITY"
        print(f"Interpretation: {specificity}")
    else:
        print("Insufficient data for entropy analysis")
        mean_entropy = 0
        max_entropy = 0
        specificity = "UNKNOWN"
    print()

    # R-3: Adjacency coherence
    print("=" * 70)
    print("TEST R-3: Adjacency Coherence by Track")
    print("=" * 70)
    print()

    line_keys = sorted(lines.keys(), key=lambda x: (x.split('.')[0], int(x.split('.')[1]) if x.split('.')[1].isdigit() else 0))

    adjacent_ri_overlap = []
    adjacent_pp_overlap = []
    nonadjacent_ri_overlap = []
    nonadjacent_pp_overlap = []

    for i in range(len(line_keys) - 1):
        key1, key2 = line_keys[i], line_keys[i+1]
        folio1 = key1.split('.')[0]
        folio2 = key2.split('.')[0]
        is_adjacent = (folio1 == folio2)

        # Get MIDDLEs by class
        ri1 = set(t['middle'] for t in lines[key1] if t['middle_class'] == 'exclusive')
        ri2 = set(t['middle'] for t in lines[key2] if t['middle_class'] == 'exclusive')
        pp1 = set(t['middle'] for t in lines[key1] if t['middle_class'] == 'shared')
        pp2 = set(t['middle'] for t in lines[key2] if t['middle_class'] == 'shared')

        ri_overlap = len(ri1 & ri2) / len(ri1 | ri2) if ri1 | ri2 else 0
        pp_overlap = len(pp1 & pp2) / len(pp1 | pp2) if pp1 | pp2 else 0

        if is_adjacent:
            adjacent_ri_overlap.append(ri_overlap)
            adjacent_pp_overlap.append(pp_overlap)
        else:
            nonadjacent_ri_overlap.append(ri_overlap)
            nonadjacent_pp_overlap.append(pp_overlap)

    adj_ri_mean = sum(adjacent_ri_overlap) / len(adjacent_ri_overlap) if adjacent_ri_overlap else 0
    adj_pp_mean = sum(adjacent_pp_overlap) / len(adjacent_pp_overlap) if adjacent_pp_overlap else 0
    nonadj_ri_mean = sum(nonadjacent_ri_overlap) / len(nonadjacent_ri_overlap) if nonadjacent_ri_overlap else 0
    nonadj_pp_mean = sum(nonadjacent_pp_overlap) / len(nonadjacent_pp_overlap) if nonadjacent_pp_overlap else 0

    print(f"Adjacent pairs (same folio): {len(adjacent_ri_overlap)}")
    print(f"Non-adjacent pairs: {len(nonadjacent_ri_overlap)}")
    print()
    print("Mean Jaccard Overlap:")
    print(f"  Adjacent RI:     {adj_ri_mean:.4f}")
    print(f"  Adjacent PP:     {adj_pp_mean:.4f}")
    print(f"  Non-adjacent RI: {nonadj_ri_mean:.4f}")
    print(f"  Non-adjacent PP: {nonadj_pp_mean:.4f}")
    print()

    ri_boost = adj_ri_mean / nonadj_ri_mean if nonadj_ri_mean > 0 else 0
    pp_boost = adj_pp_mean / nonadj_pp_mean if nonadj_pp_mean > 0 else 0

    print(f"Adjacency Boost:")
    print(f"  RI track: {ri_boost:.2f}x")
    print(f"  PP track: {pp_boost:.2f}x")
    print()

    # R-5: Folio exclusivity
    print("=" * 70)
    print("TEST R-5: Folio Exclusivity")
    print("=" * 70)
    print()

    ri_middle_folios = defaultdict(set)
    pp_middle_folios = defaultdict(set)

    for t in tokens:
        if t['middle_class'] == 'exclusive':
            ri_middle_folios[t['middle']].add(t['folio'])
        else:
            pp_middle_folios[t['middle']].add(t['folio'])

    ri_folio_counts = [len(folios) for folios in ri_middle_folios.values()]
    pp_folio_counts = [len(folios) for folios in pp_middle_folios.values()]

    ri_mean = sum(ri_folio_counts) / len(ri_folio_counts) if ri_folio_counts else 0
    pp_mean = sum(pp_folio_counts) / len(pp_folio_counts) if pp_folio_counts else 0

    print(f"RI MIDDLE types: {len(ri_folio_counts)}")
    print(f"  Mean folios per MIDDLE: {ri_mean:.2f}")
    print()
    print(f"PP MIDDLE types: {len(pp_folio_counts)}")
    print(f"  Mean folios per MIDDLE: {pp_mean:.2f}")
    print()

    # Save results
    results = {
        'phase': 'A_RECORD_STRUCTURE_ANALYSIS',
        'version': 'v2_corrected',
        'date': '2026-01-20',
        'data': {
            'n_tokens': len(tokens),
            'n_ri_tokens': len(exclusive_tokens),
            'n_pp_tokens': len(shared_tokens),
            'n_lines': len(lines),
        },
        'ri_per_line': {
            'distribution': {str(k): v for k, v in ri_per_line.items()},
            'lines_with_zero': ri_per_line[0],
            'pct_with_zero': round(100 * ri_per_line[0] / len(lines), 1),
            'mean_ri_per_line': round(mean_ri, 2),
        },
        'R1_record_typing': {
            'mean_ri_ratio': round(mean_ratio, 3),
            'ratio_distribution': ratio_bins,
        },
        'R2_neighbor_specificity': {
            'n_ri_analyzed': len(entropies),
            'mean_entropy': round(mean_entropy, 3),
            'max_entropy': round(max_entropy, 3),
            'entropy_ratio': round(mean_entropy / max_entropy, 3) if max_entropy > 0 else 0,
            'interpretation': specificity,
        },
        'R3_adjacency_coherence': {
            'n_adjacent_pairs': len(adjacent_ri_overlap),
            'n_nonadjacent_pairs': len(nonadjacent_ri_overlap),
            'adjacent_ri_overlap': round(adj_ri_mean, 4),
            'adjacent_pp_overlap': round(adj_pp_mean, 4),
            'nonadjacent_ri_overlap': round(nonadj_ri_mean, 4),
            'nonadjacent_pp_overlap': round(nonadj_pp_mean, 4),
            'ri_adjacency_boost': round(ri_boost, 2),
            'pp_adjacency_boost': round(pp_boost, 2),
        },
        'R5_folio_exclusivity': {
            'ri_middle_types': len(ri_folio_counts),
            'ri_mean_folios': round(ri_mean, 2),
            'pp_middle_types': len(pp_folio_counts),
            'pp_mean_folios': round(pp_mean, 2),
        },
    }

    with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/ri_pp_structure_v2.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print("Results saved to results/ri_pp_structure_v2.json")


if __name__ == '__main__':
    main()
