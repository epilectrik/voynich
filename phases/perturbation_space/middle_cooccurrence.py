#!/usr/bin/env python3
"""
MIDDLE Co-occurrence / Repulsion Analysis

Framing: Local recognition bundles (NOT compound meanings)
Question: Which MIDDLEs tend to be noticed together? Which repel each other?

Safe framing:
- "These recognition points cluster" (OK)
- "These form compound meanings" (NOT OK)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from math import log2, sqrt
from itertools import combinations

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token


def load_currier_a_lines():
    """Load Currier A data grouped by line."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    lines = defaultdict(list)
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to H (PRIMARY) transcriber only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    line_num = parts[11].strip('"').strip()
                    if token and folio and line_num:
                        line_key = f"{folio}_{line_num}"
                        lines[line_key].append(token)
    return lines


def get_middle_pairs_in_line(tokens):
    """Extract all MIDDLE pairs from a line of tokens."""
    middles = []
    for token in tokens:
        result = decompose_token(token)
        if result[0]:  # Valid prefix
            _, middle, _ = result
            middles.append(middle)

    # Return unique pairs (order doesn't matter)
    unique_middles = list(set(middles))
    if len(unique_middles) < 2:
        return []

    return list(combinations(sorted(unique_middles), 2))


def calculate_expected_cooccurrence(middle_freq, total_lines):
    """Calculate expected co-occurrence under independence."""
    # P(A and B in same line) under independence
    # = P(A in line) * P(B in line)
    return {}


def analyze_cooccurrence():
    """Analyze MIDDLE co-occurrence patterns."""

    lines = load_currier_a_lines()
    total_lines = len(lines)

    # Count MIDDLEs per line
    middle_line_freq = defaultdict(int)  # How many lines contain this MIDDLE
    pair_freq = defaultdict(int)  # How many lines contain this pair

    for line_key, tokens in lines.items():
        # Get unique MIDDLEs in this line
        line_middles = set()
        for token in tokens:
            result = decompose_token(token)
            if result[0]:
                _, middle, _ = result
                line_middles.add(middle)

        # Count line presence
        for middle in line_middles:
            middle_line_freq[middle] += 1

        # Count pair co-occurrence
        pairs = get_middle_pairs_in_line(tokens)
        for pair in pairs:
            pair_freq[pair] += 1

    # Load material class sharing data
    sharing_path = Path(__file__).parent.parent.parent / 'results' / 'middle_class_sharing.json'
    with open(sharing_path, 'r') as f:
        sharing_data = json.load(f)

    # Build universal set
    universal_middles = set()
    universal_details = sharing_data.get('universal_analysis', {}).get('details', [])
    for middle_info in universal_details:
        universal_middles.add(middle_info['middle'])

    # Calculate observed vs expected for each pair
    cooccurrence_stats = []
    for (m1, m2), observed in pair_freq.items():
        if observed < 3:  # Minimum threshold
            continue

        # Expected under independence
        p1 = middle_line_freq[m1] / total_lines
        p2 = middle_line_freq[m2] / total_lines
        expected = p1 * p2 * total_lines

        if expected < 1:  # Skip very rare expectations
            continue

        # Calculate ratio and significance
        ratio = observed / expected
        # Simple chi-squared approximation
        chi_sq = (observed - expected) ** 2 / expected

        # Category of pair
        is_m1_universal = m1 in universal_middles
        is_m2_universal = m2 in universal_middles

        if is_m1_universal and is_m2_universal:
            pair_type = 'universal-universal'
        elif is_m1_universal or is_m2_universal:
            pair_type = 'universal-other'
        else:
            pair_type = 'other-other'

        cooccurrence_stats.append({
            'pair': (m1, m2),
            'observed': observed,
            'expected': round(expected, 2),
            'ratio': round(ratio, 3),
            'chi_sq': round(chi_sq, 2),
            'pair_type': pair_type,
            'attraction': ratio > 1.5,
            'repulsion': ratio < 0.5
        })

    # Sort by ratio for attraction and repulsion
    cooccurrence_stats.sort(key=lambda x: x['ratio'], reverse=True)

    # Identify strong attractions
    attractions = [s for s in cooccurrence_stats if s['attraction'] and s['chi_sq'] > 3.84]
    repulsions = [s for s in cooccurrence_stats if s['repulsion'] and s['chi_sq'] > 3.84]

    # Categorize attractions by type
    attraction_by_type = defaultdict(list)
    for a in attractions:
        attraction_by_type[a['pair_type']].append(a)

    repulsion_by_type = defaultdict(list)
    for r in repulsions:
        repulsion_by_type[r['pair_type']].append(r)

    # Find "hub" MIDDLEs (attract many others)
    hub_counts = defaultdict(int)
    for a in attractions:
        hub_counts[a['pair'][0]] += 1
        hub_counts[a['pair'][1]] += 1

    top_hubs = sorted(hub_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    output = {
        'metadata': {
            'total_lines': total_lines,
            'unique_middles': len(middle_line_freq),
            'pairs_analyzed': len(cooccurrence_stats),
            'framing': 'local recognition bundles'
        },
        'summary': {
            'total_attractions': len(attractions),
            'total_repulsions': len(repulsions),
            'by_pair_type': {
                'universal-universal': {
                    'attractions': len(attraction_by_type.get('universal-universal', [])),
                    'repulsions': len(repulsion_by_type.get('universal-universal', []))
                },
                'universal-other': {
                    'attractions': len(attraction_by_type.get('universal-other', [])),
                    'repulsions': len(repulsion_by_type.get('universal-other', []))
                },
                'other-other': {
                    'attractions': len(attraction_by_type.get('other-other', [])),
                    'repulsions': len(repulsion_by_type.get('other-other', []))
                }
            }
        },
        'top_attractions': [
            {
                'pair': s['pair'],
                'observed': s['observed'],
                'expected': s['expected'],
                'ratio': s['ratio'],
                'pair_type': s['pair_type']
            }
            for s in attractions[:15]
        ],
        'top_repulsions': [
            {
                'pair': s['pair'],
                'observed': s['observed'],
                'expected': s['expected'],
                'ratio': s['ratio'],
                'pair_type': s['pair_type']
            }
            for s in sorted(repulsions, key=lambda x: x['ratio'])[:15]
        ],
        'hub_middles': [
            {
                'middle': m,
                'attraction_count': c,
                'is_universal': m in universal_middles
            }
            for m, c in top_hubs
        ],
        'interpretation': {
            'framing': 'Which recognition points tend to cluster together',
            'finding': None,
            'semantic_ceiling': 'Clustering does NOT imply compound meaning'
        }
    }

    # Generate interpretation
    u_u_attractions = len(attraction_by_type.get('universal-universal', []))
    u_o_attractions = len(attraction_by_type.get('universal-other', []))
    o_o_attractions = len(attraction_by_type.get('other-other', []))

    if u_u_attractions > 0 or u_o_attractions > 0:
        output['interpretation']['finding'] = (
            f"Found {u_u_attractions} universal-universal attractions and {u_o_attractions} universal-other attractions. "
            f"Universal MIDDLEs do participate in recognition bundles with both universal and non-universal recognition points."
        )
    else:
        output['interpretation']['finding'] = (
            "No significant universal MIDDLE attractions found. "
            "Recognition bundles are primarily among non-universal MIDDLEs."
        )

    return output, cooccurrence_stats


def main():
    print("=" * 60)
    print("MIDDLE Co-occurrence / Repulsion Analysis")
    print("Framing: Local recognition bundles (NOT compound meanings)")
    print("=" * 60)
    print()

    output, details = analyze_cooccurrence()

    print(f"Lines analyzed: {output['metadata']['total_lines']}")
    print(f"Unique MIDDLEs: {output['metadata']['unique_middles']}")
    print(f"Pairs analyzed: {output['metadata']['pairs_analyzed']}")
    print()

    print("Summary:")
    print("-" * 40)
    print(f"  Total attractions: {output['summary']['total_attractions']}")
    print(f"  Total repulsions: {output['summary']['total_repulsions']}")
    print()
    print("  By pair type:")
    for ptype, stats in output['summary']['by_pair_type'].items():
        print(f"    {ptype}: {stats['attractions']} attractions, {stats['repulsions']} repulsions")
    print()

    print("Top Attractions (ratio > 1.5, chi-sq > 3.84):")
    print("-" * 40)
    for a in output['top_attractions'][:10]:
        print(f"  {a['pair']}: obs={a['observed']}, exp={a['expected']}, ratio={a['ratio']} [{a['pair_type']}]")
    print()

    print("Top Repulsions (ratio < 0.5, chi-sq > 3.84):")
    print("-" * 40)
    for r in output['top_repulsions'][:10]:
        print(f"  {r['pair']}: obs={r['observed']}, exp={r['expected']}, ratio={r['ratio']} [{r['pair_type']}]")
    print()

    print("Hub MIDDLEs (attract many others):")
    print("-" * 40)
    for h in output['hub_middles']:
        univ = "[UNIVERSAL]" if h['is_universal'] else ""
        print(f"  {h['middle']}: {h['attraction_count']} attractions {univ}")
    print()

    print("Interpretation:")
    print("-" * 40)
    print(f"  {output['interpretation']['finding']}")
    print()
    print(f"  Semantic ceiling: {output['interpretation']['semantic_ceiling']}")

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'middle_cooccurrence.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
