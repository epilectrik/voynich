#!/usr/bin/env python3
"""
RI/PP Structure Analysis - Currier A Record Structure with Two-Track Lens

Tests:
- R-1: Record typing by RI/PP composition
- R-2: RI-PP neighbor specificity (entropy analysis)
- R-3: Adjacency coherence by track
- R-4: RI token spacing pattern
- R-5: Folio exclusivity comparison
"""

import csv
import json
import math
from collections import defaultdict, Counter

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def entropy(counts):
    """Compute Shannon entropy from counts."""
    total = sum(counts.values())
    if total == 0:
        return 0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_a_data():
    """Load Currier A tokens, grouped by line."""
    lines = defaultdict(list)
    all_tokens = []

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            line = row.get('line_number', '').strip()  # Column is line_number, not line
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            line_key = f"{folio}.{line}"
            middle = get_middle(word)

            token_data = {
                'word': word,
                'folio': folio,
                'line': line,
                'line_key': line_key,
                'middle': middle
            }
            lines[line_key].append(token_data)
            all_tokens.append(token_data)

    return lines, all_tokens

# ============================================================
# TEST R-5: Folio Exclusivity Comparison
# ============================================================

def test_r5_folio_exclusivity(all_tokens, registry_internal):
    """Compare folio spread of RI vs PP tokens."""
    print("=" * 70)
    print("TEST R-5: Folio Exclusivity Comparison")
    print("=" * 70)
    print()

    # Count folios per MIDDLE
    middle_folios = defaultdict(set)
    for t in all_tokens:
        middle_folios[t['middle']].add(t['folio'])

    ri_folio_counts = []
    pp_folio_counts = []

    for middle, folios in middle_folios.items():
        if middle in registry_internal:
            ri_folio_counts.append(len(folios))
        else:
            pp_folio_counts.append(len(folios))

    ri_mean = sum(ri_folio_counts) / len(ri_folio_counts) if ri_folio_counts else 0
    pp_mean = sum(pp_folio_counts) / len(pp_folio_counts) if pp_folio_counts else 0

    ri_median = sorted(ri_folio_counts)[len(ri_folio_counts)//2] if ri_folio_counts else 0
    pp_median = sorted(pp_folio_counts)[len(pp_folio_counts)//2] if pp_folio_counts else 0

    # Singleton rate (appear in only 1 folio)
    ri_singleton = sum(1 for c in ri_folio_counts if c == 1)
    pp_singleton = sum(1 for c in pp_folio_counts if c == 1)

    print(f"Registry-Internal MIDDLEs: {len(ri_folio_counts)}")
    print(f"  Mean folios: {ri_mean:.2f}")
    print(f"  Median folios: {ri_median}")
    print(f"  Singletons (1 folio): {ri_singleton} ({100*ri_singleton/len(ri_folio_counts):.1f}%)")
    print()
    print(f"Pipeline-Participating MIDDLEs: {len(pp_folio_counts)}")
    print(f"  Mean folios: {pp_mean:.2f}")
    print(f"  Median folios: {pp_median}")
    print(f"  Singletons (1 folio): {pp_singleton} ({100*pp_singleton/len(pp_folio_counts):.1f}%)")
    print()
    print(f"Ratio (PP/RI mean): {pp_mean/ri_mean:.2f}x")
    print()

    return {
        'ri_count': len(ri_folio_counts),
        'ri_mean_folios': round(ri_mean, 2),
        'ri_median_folios': ri_median,
        'ri_singleton_rate': round(ri_singleton / len(ri_folio_counts), 3),
        'pp_count': len(pp_folio_counts),
        'pp_mean_folios': round(pp_mean, 2),
        'pp_median_folios': pp_median,
        'pp_singleton_rate': round(pp_singleton / len(pp_folio_counts), 3),
        'ratio_pp_ri': round(pp_mean / ri_mean, 2)
    }

# ============================================================
# TEST R-1: Record Typing by RI/PP Composition
# ============================================================

def test_r1_record_typing(lines, registry_internal):
    """Type records by RI/PP composition."""
    print("=" * 70)
    print("TEST R-1: Record Typing by RI/PP Composition")
    print("=" * 70)
    print()

    records = []
    for line_key, tokens in lines.items():
        ri_count = sum(1 for t in tokens if t['middle'] in registry_internal)
        pp_count = len(tokens) - ri_count
        total = len(tokens)
        ri_ratio = ri_count / total if total > 0 else 0

        folio = tokens[0]['folio'] if tokens else ''

        records.append({
            'line_key': line_key,
            'folio': folio,
            'total': total,
            'ri_count': ri_count,
            'pp_count': pp_count,
            'ri_ratio': ri_ratio
        })

    # Summary statistics
    ri_ratios = [r['ri_ratio'] for r in records]
    mean_ratio = sum(ri_ratios) / len(ri_ratios)

    # Distribution of RI ratios
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

    print(f"Total A records (lines): {len(records)}")
    print(f"Mean RI ratio: {mean_ratio:.3f}")
    print()
    print("RI Ratio Distribution:")
    for bin_name, count in ratio_bins.items():
        pct = 100 * count / len(records)
        bar = '#' * int(pct / 2)
        print(f"  {bin_name}: {count:>3} ({pct:>5.1f}%) {bar}")
    print()

    # Correlation with record length
    lengths = [r['total'] for r in records]
    ri_counts = [r['ri_count'] for r in records]

    mean_len = sum(lengths) / len(lengths)
    mean_ri = sum(ri_counts) / len(ri_counts)

    cov = sum((l - mean_len) * (r - mean_ri) for l, r in zip(lengths, ri_counts)) / len(lengths)
    std_len = (sum((l - mean_len)**2 for l in lengths) / len(lengths))**0.5
    std_ri = (sum((r - mean_ri)**2 for r in ri_counts) / len(ri_counts))**0.5

    corr = cov / (std_len * std_ri) if std_len > 0 and std_ri > 0 else 0

    print(f"Correlation (record length vs RI count): r = {corr:.3f}")
    print()

    return {
        'n_records': len(records),
        'mean_ri_ratio': round(mean_ratio, 3),
        'ratio_distribution': {k: v for k, v in ratio_bins.items()},
        'length_ri_correlation': round(corr, 3)
    }

# ============================================================
# TEST R-4: RI Token Spacing Pattern
# ============================================================

def test_r4_spacing_pattern(lines, registry_internal):
    """Analyze spacing between RI tokens within records."""
    print("=" * 70)
    print("TEST R-4: RI Token Spacing Pattern")
    print("=" * 70)
    print()

    all_gaps = []
    all_normalized_gaps = []

    for line_key, tokens in lines.items():
        ri_positions = [i for i, t in enumerate(tokens) if t['middle'] in registry_internal]

        if len(ri_positions) >= 2:
            for i in range(1, len(ri_positions)):
                gap = ri_positions[i] - ri_positions[i-1]
                all_gaps.append(gap)
                # Normalize by line length
                norm_gap = gap / len(tokens)
                all_normalized_gaps.append(norm_gap)

    if not all_gaps:
        print("No RI token pairs found")
        return {'status': 'no_data'}

    mean_gap = sum(all_gaps) / len(all_gaps)
    median_gap = sorted(all_gaps)[len(all_gaps)//2]

    # Gap distribution
    gap_dist = Counter(all_gaps)

    print(f"Total RI-to-RI gaps: {len(all_gaps)}")
    print(f"Mean gap: {mean_gap:.2f} tokens")
    print(f"Median gap: {median_gap}")
    print()

    print("Gap Distribution (top 10):")
    for gap, count in gap_dist.most_common(10):
        pct = 100 * count / len(all_gaps)
        print(f"  Gap {gap}: {count} ({pct:.1f}%)")
    print()

    # Test for regularity vs randomness
    # Coefficient of variation (CV) - lower = more regular
    std_gap = (sum((g - mean_gap)**2 for g in all_gaps) / len(all_gaps))**0.5
    cv = std_gap / mean_gap if mean_gap > 0 else 0

    print(f"Coefficient of Variation: {cv:.3f}")
    if cv < 0.5:
        pattern = "REGULAR (low CV)"
    elif cv < 1.0:
        pattern = "MODERATE"
    else:
        pattern = "IRREGULAR/RANDOM (high CV)"
    print(f"Pattern interpretation: {pattern}")
    print()

    # Adjacent gaps (gap=1 means consecutive RI tokens)
    adjacent_ri = gap_dist.get(1, 0)
    print(f"Adjacent RI tokens (gap=1): {adjacent_ri} ({100*adjacent_ri/len(all_gaps):.1f}%)")
    print()

    return {
        'n_gaps': len(all_gaps),
        'mean_gap': round(mean_gap, 2),
        'median_gap': median_gap,
        'cv': round(cv, 3),
        'pattern': pattern,
        'adjacent_rate': round(adjacent_ri / len(all_gaps), 3) if all_gaps else 0,
        'gap_distribution': {str(k): v for k, v in gap_dist.most_common(10)}
    }

# ============================================================
# TEST R-2: RI-PP Neighbor Specificity
# ============================================================

def test_r2_neighbor_specificity(lines, registry_internal):
    """Test if specific RI MIDDLEs have preferred PP neighbors."""
    print("=" * 70)
    print("TEST R-2: RI-PP Neighbor Specificity")
    print("=" * 70)
    print()

    # For each RI MIDDLE, collect its PP neighbors
    ri_pp_neighbors = defaultdict(Counter)

    for line_key, tokens in lines.items():
        for i, t in enumerate(tokens):
            if t['middle'] in registry_internal:
                # Get PP neighbors
                if i > 0 and tokens[i-1]['middle'] not in registry_internal:
                    ri_pp_neighbors[t['middle']][tokens[i-1]['middle']] += 1
                if i < len(tokens) - 1 and tokens[i+1]['middle'] not in registry_internal:
                    ri_pp_neighbors[t['middle']][tokens[i+1]['middle']] += 1

    # Compute entropy for each RI MIDDLE
    entropies = []
    ri_with_neighbors = 0

    for ri_middle, pp_counts in ri_pp_neighbors.items():
        if sum(pp_counts.values()) >= 3:  # Need at least 3 observations
            ent = entropy(pp_counts)
            entropies.append({
                'ri_middle': ri_middle,
                'entropy': ent,
                'n_neighbors': sum(pp_counts.values()),
                'n_unique_pp': len(pp_counts),
                'top_pp': pp_counts.most_common(3)
            })
            ri_with_neighbors += 1

    if not entropies:
        print("Insufficient data for entropy analysis")
        return {'status': 'insufficient_data'}

    mean_entropy = sum(e['entropy'] for e in entropies) / len(entropies)

    # Compute null model entropy (random pairing)
    # If neighbors were random, entropy would be log2(n_unique_pp_middles)
    all_pp_middles = set()
    for line_key, tokens in lines.items():
        for t in tokens:
            if t['middle'] not in registry_internal:
                all_pp_middles.add(t['middle'])

    max_entropy = math.log2(len(all_pp_middles)) if all_pp_middles else 0

    print(f"RI MIDDLEs with sufficient neighbors: {len(entropies)}")
    print(f"Mean neighbor entropy: {mean_entropy:.3f} bits")
    print(f"Max possible entropy (random): {max_entropy:.3f} bits")
    print(f"Entropy ratio (observed/max): {mean_entropy/max_entropy:.3f}")
    print()

    # Low entropy = specific neighbors, high entropy = random
    if mean_entropy / max_entropy < 0.5:
        specificity = "HIGH SPECIFICITY (low entropy ratio)"
    elif mean_entropy / max_entropy < 0.75:
        specificity = "MODERATE SPECIFICITY"
    else:
        specificity = "LOW SPECIFICITY (near-random)"

    print(f"Interpretation: {specificity}")
    print()

    # Show examples of low-entropy (specific) RI MIDDLEs
    sorted_by_entropy = sorted(entropies, key=lambda x: x['entropy'])
    print("Most specific RI MIDDLEs (lowest entropy):")
    for e in sorted_by_entropy[:5]:
        top_neighbors = ', '.join(f"{pp}({c})" for pp, c in e['top_pp'])
        print(f"  {e['ri_middle']}: H={e['entropy']:.2f}, n={e['n_neighbors']}, top: {top_neighbors}")
    print()

    # Show examples of high-entropy (dispersed) RI MIDDLEs
    print("Most dispersed RI MIDDLEs (highest entropy):")
    for e in sorted_by_entropy[-5:]:
        print(f"  {e['ri_middle']}: H={e['entropy']:.2f}, n={e['n_neighbors']}, unique_pp={e['n_unique_pp']}")
    print()

    return {
        'n_ri_analyzed': len(entropies),
        'mean_entropy': round(mean_entropy, 3),
        'max_entropy': round(max_entropy, 3),
        'entropy_ratio': round(mean_entropy / max_entropy, 3) if max_entropy > 0 else 0,
        'interpretation': specificity,
        'lowest_entropy': [{'middle': e['ri_middle'], 'entropy': round(e['entropy'], 3)}
                          for e in sorted_by_entropy[:5]],
        'highest_entropy': [{'middle': e['ri_middle'], 'entropy': round(e['entropy'], 3)}
                           for e in sorted_by_entropy[-5:]]
    }

# ============================================================
# TEST R-3: Adjacency Coherence by Track
# ============================================================

def test_r3_adjacency_coherence(lines, registry_internal):
    """Test if C346 adjacency coherence is driven by RI or PP vocabulary."""
    print("=" * 70)
    print("TEST R-3: Adjacency Coherence by Track")
    print("=" * 70)
    print()

    # Get ordered list of lines (by folio.line)
    line_keys = sorted(lines.keys(), key=lambda x: (x.split('.')[0], int(x.split('.')[1]) if x.split('.')[1].isdigit() else 0))

    # For adjacent pairs, compute overlap
    adjacent_ri_overlap = []
    adjacent_pp_overlap = []
    nonadjacent_ri_overlap = []
    nonadjacent_pp_overlap = []

    for i in range(len(line_keys) - 1):
        key1, key2 = line_keys[i], line_keys[i+1]

        # Check if same folio (adjacent)
        folio1 = key1.split('.')[0]
        folio2 = key2.split('.')[0]
        is_adjacent = (folio1 == folio2)

        # Get MIDDLEs for each line, split by track
        middles1 = set(t['middle'] for t in lines[key1])
        middles2 = set(t['middle'] for t in lines[key2])

        ri1 = middles1 & registry_internal
        ri2 = middles2 & registry_internal
        pp1 = middles1 - registry_internal
        pp2 = middles2 - registry_internal

        # Jaccard overlap
        ri_overlap = len(ri1 & ri2) / len(ri1 | ri2) if ri1 | ri2 else 0
        pp_overlap = len(pp1 & pp2) / len(pp1 | pp2) if pp1 | pp2 else 0

        if is_adjacent:
            adjacent_ri_overlap.append(ri_overlap)
            adjacent_pp_overlap.append(pp_overlap)
        else:
            nonadjacent_ri_overlap.append(ri_overlap)
            nonadjacent_pp_overlap.append(pp_overlap)

    # Means
    adj_ri_mean = sum(adjacent_ri_overlap) / len(adjacent_ri_overlap) if adjacent_ri_overlap else 0
    adj_pp_mean = sum(adjacent_pp_overlap) / len(adjacent_pp_overlap) if adjacent_pp_overlap else 0
    nonadj_ri_mean = sum(nonadjacent_ri_overlap) / len(nonadjacent_ri_overlap) if nonadjacent_ri_overlap else 0
    nonadj_pp_mean = sum(nonadjacent_pp_overlap) / len(nonadjacent_pp_overlap) if nonadjacent_pp_overlap else 0

    print(f"Adjacent line pairs (same folio): {len(adjacent_ri_overlap)}")
    print(f"Non-adjacent line pairs: {len(nonadjacent_ri_overlap)}")
    print()

    print("Mean Jaccard Overlap:")
    print(f"  Adjacent RI:     {adj_ri_mean:.4f}")
    print(f"  Adjacent PP:     {adj_pp_mean:.4f}")
    print(f"  Non-adjacent RI: {nonadj_ri_mean:.4f}")
    print(f"  Non-adjacent PP: {nonadj_pp_mean:.4f}")
    print()

    # Adjacency boost
    ri_boost = adj_ri_mean / nonadj_ri_mean if nonadj_ri_mean > 0 else 0
    pp_boost = adj_pp_mean / nonadj_pp_mean if nonadj_pp_mean > 0 else 0

    print(f"Adjacency Boost (adjacent/non-adjacent):")
    print(f"  RI track: {ri_boost:.2f}x")
    print(f"  PP track: {pp_boost:.2f}x")
    print()

    if ri_boost > pp_boost * 1.5:
        driver = "RI-DRIVEN (batch/instance continuity)"
    elif pp_boost > ri_boost * 1.5:
        driver = "PP-DRIVEN (operational continuity)"
    else:
        driver = "MIXED (both tracks contribute)"

    print(f"Coherence driver: {driver}")
    print()

    return {
        'n_adjacent_pairs': len(adjacent_ri_overlap),
        'n_nonadjacent_pairs': len(nonadjacent_ri_overlap),
        'adjacent_ri_overlap': round(adj_ri_mean, 4),
        'adjacent_pp_overlap': round(adj_pp_mean, 4),
        'nonadjacent_ri_overlap': round(nonadj_ri_mean, 4),
        'nonadjacent_pp_overlap': round(nonadj_pp_mean, 4),
        'ri_adjacency_boost': round(ri_boost, 2),
        'pp_adjacency_boost': round(pp_boost, 2),
        'coherence_driver': driver
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("RI/PP STRUCTURE ANALYSIS - Currier A Records")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    lines, all_tokens = load_a_data()
    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print(f"  Total A lines: {len(lines)}")
    print(f"  Total A tokens: {len(all_tokens)}")
    print()

    results = {
        'phase': 'A_RECORD_STRUCTURE_ANALYSIS',
        'date': '2026-01-20',
        'data': {
            'n_ri_middles': len(registry_internal),
            'n_lines': len(lines),
            'n_tokens': len(all_tokens)
        }
    }

    # Run tests
    results['R5_folio_exclusivity'] = test_r5_folio_exclusivity(all_tokens, registry_internal)
    results['R1_record_typing'] = test_r1_record_typing(lines, registry_internal)
    results['R4_spacing_pattern'] = test_r4_spacing_pattern(lines, registry_internal)
    results['R2_neighbor_specificity'] = test_r2_neighbor_specificity(lines, registry_internal)
    results['R3_adjacency_coherence'] = test_r3_adjacency_coherence(lines, registry_internal)

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"R-5 (Folio Exclusivity): RI={results['R5_folio_exclusivity']['ri_mean_folios']:.1f} vs PP={results['R5_folio_exclusivity']['pp_mean_folios']:.1f} folios")
    print(f"R-1 (Record Typing): Mean RI ratio = {results['R1_record_typing']['mean_ri_ratio']:.3f}")
    print(f"R-4 (Spacing): CV = {results['R4_spacing_pattern']['cv']:.3f} ({results['R4_spacing_pattern']['pattern']})")
    print(f"R-2 (Neighbor Specificity): {results['R2_neighbor_specificity']['interpretation']}")
    print(f"R-3 (Adjacency Coherence): {results['R3_adjacency_coherence']['coherence_driver']}")
    print()

    # Save results
    with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/ri_pp_structure.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/ri_pp_structure.json")

if __name__ == '__main__':
    main()
