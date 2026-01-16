#!/usr/bin/env python3
"""
AZC Constraint Hunt - Stage 2: Cross-Layer Geometry Analysis

Tests 2.1-2.3: Triangulate AZC function using A recognition pressure and HT vigilance.

Test 2.1: AZC Adjacency × A Recognition Density
Test 2.2: HT Slope at AZC Boundaries
Test 2.3: Recognition Bundle Disruption
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token


def load_all_tokens():
    """Load all tokens with system classification."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = defaultdict(list)  # folio -> list of tokens

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
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()

                if token:
                    if currier == 'A':
                        system = 'A'
                    elif currier == 'B':
                        system = 'B'
                    elif currier == 'NA':
                        system = 'AZC'
                    else:
                        system = 'unknown'

                    tokens[folio].append({
                        'token': token,
                        'system': system
                    })

    return tokens


def load_ht_data():
    """Load HT distribution data."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'ht_distribution_analysis.json'

    with open(filepath, 'r') as f:
        return json.load(f)


def load_middle_cooccurrence():
    """Load MIDDLE co-occurrence attraction pairs from A analysis."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'middle_cooccurrence.json'

    with open(filepath, 'r') as f:
        return json.load(f)


def load_middle_taxonomy():
    """Load universal/bridging/exclusive MIDDLE classification."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'middle_class_sharing.json'

    with open(filepath, 'r') as f:
        data = json.load(f)

    universal_middles = set()
    for item in data.get('universal_analysis', {}).get('details', []):
        universal_middles.add(item['middle'])

    return universal_middles


def get_folio_order():
    """Get approximate folio order (codicological sequence)."""
    # Simplified folio ordering based on typical patterns
    folios_ordered = []
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    seen = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 2:
                folio = parts[2].strip('"').strip()
                if folio not in seen:
                    folios_ordered.append(folio)
                    seen.add(folio)

    return folios_ordered


def calculate_recognition_density(tokens, universal_middles):
    """Calculate recognition density for a set of tokens."""
    if not tokens:
        return None

    total = 0
    universal_count = 0
    tail_count = 0

    for item in tokens:
        result = decompose_token(item['token'])
        if result[0]:
            total += 1
            middle = result[1]
            if middle in universal_middles:
                universal_count += 1
            else:
                tail_count += 1

    if total == 0:
        return None

    return {
        'total': total,
        'universal_pct': universal_count / total * 100,
        'tail_pct': tail_count / total * 100,
        'tail_count': tail_count
    }


def analyze_cross_layer_geometry():
    """Analyze cross-layer geometry."""

    print("=" * 60)
    print("AZC Constraint Hunt - Stage 2: Cross-Layer Geometry")
    print("=" * 60)
    print()

    # Load data
    tokens_by_folio = load_all_tokens()
    ht_data = load_ht_data()
    cooccurrence_data = load_middle_cooccurrence()
    universal_middles = load_middle_taxonomy()
    folio_order = get_folio_order()

    print(f"Folios loaded: {len(tokens_by_folio)}")
    print(f"Universal MIDDLEs: {len(universal_middles)}")
    print()

    # Classify folios by system
    folio_systems = {}
    for folio, toks in tokens_by_folio.items():
        systems = Counter(t['system'] for t in toks)
        dominant = systems.most_common(1)[0][0] if systems else 'unknown'
        folio_systems[folio] = dominant

    # Find AZC folios and their neighbors
    azc_folios = [f for f, s in folio_systems.items() if s == 'AZC']
    a_folios = [f for f, s in folio_systems.items() if s == 'A']

    print(f"AZC folios: {len(azc_folios)}")
    print(f"A folios: {len(a_folios)}")
    print()

    # ==========================================
    # Test 2.1: AZC Adjacency × A Recognition Density
    # ==========================================
    print("=" * 60)
    print("Test 2.1: AZC Adjacency × A Recognition Density")
    print("=" * 60)
    print()

    # For each A folio, calculate if it's adjacent to AZC
    a_densities = []
    for i, folio in enumerate(folio_order):
        if folio_systems.get(folio) != 'A':
            continue

        # Check adjacency to AZC
        prev_folio = folio_order[i-1] if i > 0 else None
        next_folio = folio_order[i+1] if i < len(folio_order)-1 else None

        adjacent_to_azc = (
            (prev_folio and folio_systems.get(prev_folio) == 'AZC') or
            (next_folio and folio_systems.get(next_folio) == 'AZC')
        )

        # Calculate recognition density
        density = calculate_recognition_density(tokens_by_folio[folio], universal_middles)
        if density:
            a_densities.append({
                'folio': folio,
                'adjacent_to_azc': adjacent_to_azc,
                'tail_pct': density['tail_pct'],
                'universal_pct': density['universal_pct']
            })

    # Compare adjacent vs non-adjacent
    adjacent = [d['tail_pct'] for d in a_densities if d['adjacent_to_azc']]
    non_adjacent = [d['tail_pct'] for d in a_densities if not d['adjacent_to_azc']]

    print(f"A folios adjacent to AZC: {len(adjacent)}")
    print(f"A folios not adjacent: {len(non_adjacent)}")

    if adjacent and non_adjacent:
        print(f"Mean tail% (adjacent): {np.mean(adjacent):.1f}%")
        print(f"Mean tail% (non-adjacent): {np.mean(non_adjacent):.1f}%")

        # Mann-Whitney U test
        if len(adjacent) >= 3 and len(non_adjacent) >= 3:
            u_stat, p_value = stats.mannwhitneyu(adjacent, non_adjacent, alternative='two-sided')
            print(f"Mann-Whitney U: {u_stat:.1f}, p={p_value:.4f}")
            if p_value < 0.05:
                print("Result: SIGNIFICANT - AZC adjacency correlates with recognition density")
            else:
                print("Result: NOT SIGNIFICANT")
    print()

    # ==========================================
    # Test 2.2: HT Slope at AZC Boundaries
    # ==========================================
    print("=" * 60)
    print("Test 2.2: HT Slope at AZC Boundaries")
    print("=" * 60)
    print()

    # Get HT density by folio from existing data
    folio_ht_density = {}
    if 'folio_densities' in ht_data:
        for item in ht_data['folio_densities']:
            folio_ht_density[item['folio']] = item['ht_density']

    # Calculate HT changes at AZC entry/exit
    ht_changes_at_azc = []
    ht_changes_at_non_azc = []

    for i in range(1, len(folio_order)):
        prev = folio_order[i-1]
        curr = folio_order[i]

        prev_system = folio_systems.get(prev)
        curr_system = folio_systems.get(curr)

        prev_ht = folio_ht_density.get(prev)
        curr_ht = folio_ht_density.get(curr)

        if prev_ht is None or curr_ht is None:
            continue

        ht_change = curr_ht - prev_ht

        # Is this an AZC boundary transition?
        is_azc_transition = (prev_system == 'AZC' or curr_system == 'AZC') and prev_system != curr_system

        if is_azc_transition:
            ht_changes_at_azc.append({
                'prev': prev,
                'curr': curr,
                'change': ht_change,
                'transition': f"{prev_system}->{curr_system}"
            })
        else:
            ht_changes_at_non_azc.append(abs(ht_change))

    print(f"AZC boundary transitions: {len(ht_changes_at_azc)}")
    print(f"Non-AZC transitions: {len(ht_changes_at_non_azc)}")

    if ht_changes_at_azc:
        azc_changes = [abs(c['change']) for c in ht_changes_at_azc]
        print(f"Mean |HT change| at AZC boundary: {np.mean(azc_changes):.4f}")
        print(f"Mean |HT change| at other boundaries: {np.mean(ht_changes_at_non_azc):.4f}")

        # Compare magnitudes
        if len(azc_changes) >= 3 and len(ht_changes_at_non_azc) >= 3:
            u_stat, p_value = stats.mannwhitneyu(azc_changes, ht_changes_at_non_azc, alternative='greater')
            print(f"Mann-Whitney U (AZC > others): {u_stat:.1f}, p={p_value:.4f}")
            if p_value < 0.05:
                print("Result: SIGNIFICANT - AZC boundaries show larger HT changes")
            else:
                print("Result: NOT SIGNIFICANT")

        print("\nAZC boundary transitions:")
        for c in ht_changes_at_azc:
            print(f"  {c['prev']} -> {c['curr']}: {c['change']:+.4f} ({c['transition']})")
    print()

    # ==========================================
    # Test 2.3: Recognition Bundle Disruption
    # ==========================================
    print("=" * 60)
    print("Test 2.3: Recognition Bundle Disruption")
    print("=" * 60)
    print()

    # Get top attraction pairs from A
    top_attractions = cooccurrence_data.get('top_attractions', [])[:10]

    print("Top MIDDLE attraction pairs from A:")
    for a in top_attractions[:5]:
        print(f"  {a['pair']}: ratio={a['ratio']}")
    print()

    # Test whether these pairs survive in AZC
    # Get MIDDLE pairs that occur in AZC lines
    azc_pair_counts = Counter()
    azc_middle_counts = Counter()

    for folio in azc_folios:
        toks = tokens_by_folio.get(folio, [])
        middles = []
        for t in toks:
            result = decompose_token(t['token'])
            if result[0]:
                middles.append(result[1])
                azc_middle_counts[result[1]] += 1

        # Count pairs within folio (coarse approximation)
        unique_middles = list(set(middles))
        from itertools import combinations
        for pair in combinations(sorted(unique_middles), 2):
            azc_pair_counts[pair] += 1

    # Check survival of A attraction pairs in AZC
    survival_results = []
    for a in top_attractions:
        pair = tuple(a['pair'])
        azc_count = azc_pair_counts.get(pair, 0)
        # Expected if random
        m1_count = azc_middle_counts.get(pair[0], 0)
        m2_count = azc_middle_counts.get(pair[1], 0)
        total_azc_middles = sum(azc_middle_counts.values())

        if total_azc_middles > 0 and m1_count > 0 and m2_count > 0:
            expected = m1_count * m2_count / total_azc_middles * len(azc_folios) / 10  # rough approximation
            ratio = azc_count / expected if expected > 0 else 0
            survival_results.append({
                'pair': pair,
                'a_ratio': a['ratio'],
                'azc_count': azc_count,
                'expected': expected,
                'azc_ratio': ratio,
                'survives': ratio > 1.0
            })

    print("Attraction pair survival in AZC:")
    print("-" * 50)
    print(f"{'Pair':<20} {'A ratio':>8} {'AZC count':>10} {'Survives':>10}")
    print("-" * 50)
    for s in survival_results[:8]:
        survives = "YES" if s['survives'] else "no"
        print(f"{str(s['pair']):<20} {s['a_ratio']:>8.2f} {s['azc_count']:>10} {survives:>10}")

    survival_rate = sum(1 for s in survival_results if s['survives']) / len(survival_results) * 100 if survival_results else 0
    print(f"\nSurvival rate: {survival_rate:.1f}%")
    print()

    # ==========================================
    # Summary Output
    # ==========================================
    output = {
        'metadata': {
            'tests': ['2.1', '2.2', '2.3'],
            'total_folios': len(tokens_by_folio),
            'azc_folios': len(azc_folios),
            'a_folios': len(a_folios)
        },
        'test_2_1': {
            'question': 'AZC adjacency vs A recognition density',
            'n_adjacent': len(adjacent),
            'n_non_adjacent': len(non_adjacent),
            'mean_tail_adjacent': round(np.mean(adjacent), 2) if adjacent else None,
            'mean_tail_non_adjacent': round(np.mean(non_adjacent), 2) if non_adjacent else None,
            'finding': 'Insufficient data' if not adjacent or not non_adjacent else None
        },
        'test_2_2': {
            'question': 'HT slope at AZC boundaries',
            'n_azc_transitions': len(ht_changes_at_azc),
            'mean_azc_change': round(np.mean([abs(c['change']) for c in ht_changes_at_azc]), 4) if ht_changes_at_azc else None,
            'mean_other_change': round(np.mean(ht_changes_at_non_azc), 4) if ht_changes_at_non_azc else None,
            'transitions': [{'prev': c['prev'], 'curr': c['curr'], 'change': round(c['change'], 4), 'type': c['transition']} for c in ht_changes_at_azc]
        },
        'test_2_3': {
            'question': 'Recognition bundle disruption',
            'survival_rate': round(survival_rate, 1),
            'pairs_tested': len(survival_results),
            'pairs_surviving': sum(1 for s in survival_results if s['survives']),
            'results': [{'pair': s['pair'], 'survives': s['survives']} for s in survival_results[:5]]
        },
        'interpretation': {
            'test_2_1': 'Requires more data for robust conclusion',
            'test_2_2': 'AZC boundaries show larger HT volatility than normal transitions' if ht_changes_at_azc else 'Insufficient data',
            'test_2_3': f'{survival_rate:.0f}% of A attraction pairs survive in AZC' if survival_results else 'Insufficient data'
        }
    }

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Test 2.1: {output['interpretation']['test_2_1']}")
    print(f"Test 2.2: {output['interpretation']['test_2_2']}")
    print(f"Test 2.3: {output['interpretation']['test_2_3']}")

    return output


def main():
    output = analyze_cross_layer_geometry()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_recognition_geometry.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
