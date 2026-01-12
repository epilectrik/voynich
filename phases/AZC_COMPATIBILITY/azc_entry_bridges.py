#!/usr/bin/env python3
"""
AZC Entry Bridge Analysis

Question: From the perspective of Currier A entries, are any AZC folio
combinations "illegal" (never bridged by a single entry)?

Logic:
- Each Currier A entry (token) appears in 1+ AZC folios
- If token X appears in folios {A, B, C}, then X "bridges" those folios
- Using X simultaneously activates A, B, and C
- If NO token bridges folios A and D, they are never directly co-activated

This probe builds an adjacency matrix where:
- Nodes = AZC folios
- Edge (i, j) = number of tokens that appear in BOTH folio i AND folio j
- If edge weight = 0, those folios are NEVER bridged by a single A entry
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "azc_entry_bridges.json"

# AZC Family definitions (from C430)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS


def build_token_azc_profiles() -> Dict[str, Set[str]]:
    """
    Build mapping of token -> set of AZC folios it appears in.
    This is the "bridge profile" for each Currier A entry.
    """
    token_to_folios = defaultdict(set)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Only track tokens in AZC folios
            if folio in ALL_AZC_FOLIOS:
                token_to_folios[word].add(folio)

    return dict(token_to_folios)


def build_bridge_matrix(token_profiles: Dict[str, Set[str]]) -> Dict[Tuple[str, str], int]:
    """
    Build adjacency matrix where edge (i, j) = count of tokens that bridge
    both folio i and folio j.
    """
    bridge_counts = defaultdict(int)
    bridge_tokens = defaultdict(list)  # Track which tokens bridge each pair

    for token, folios in token_profiles.items():
        if len(folios) < 2:
            continue  # Single-folio tokens don't create bridges

        # For each pair of folios this token appears in, increment bridge count
        folio_list = sorted(folios)
        for i, folio_i in enumerate(folio_list):
            for folio_j in folio_list[i+1:]:
                pair = (folio_i, folio_j)
                bridge_counts[pair] += 1
                if len(bridge_tokens[pair]) < 5:  # Keep sample
                    bridge_tokens[pair].append(token)

    return dict(bridge_counts), dict(bridge_tokens)


def find_unbridged_pairs(bridge_counts: Dict[Tuple[str, str], int]) -> List[Tuple[str, str]]:
    """Find all AZC folio pairs that have NO bridging tokens."""
    unbridged = []
    azc_folios = sorted(ALL_AZC_FOLIOS)

    for i, folio_i in enumerate(azc_folios):
        for folio_j in azc_folios[i+1:]:
            pair = (folio_i, folio_j)
            if pair not in bridge_counts:
                unbridged.append(pair)

    return unbridged


def analyze_bridge_distribution(token_profiles: Dict[str, Set[str]]) -> Dict:
    """Analyze distribution of how many folios each token bridges."""
    folio_counts = [len(folios) for folios in token_profiles.values()]

    distribution = Counter(folio_counts)

    return {
        'distribution': dict(sorted(distribution.items())),
        'mean': round(statistics.mean(folio_counts), 2) if folio_counts else 0,
        'max': max(folio_counts) if folio_counts else 0,
        'single_folio_tokens': distribution.get(1, 0),
        'multi_folio_tokens': sum(c for n, c in distribution.items() if n > 1),
        'total_tokens': len(folio_counts)
    }


def check_graph_connectivity(bridge_counts: Dict[Tuple[str, str], int]) -> Dict:
    """
    Check if the AZC folio graph is fully connected.
    Use BFS/DFS to find connected components.
    """
    # Build adjacency list
    adjacency = defaultdict(set)
    for (folio_i, folio_j), count in bridge_counts.items():
        if count > 0:
            adjacency[folio_i].add(folio_j)
            adjacency[folio_j].add(folio_i)

    # Find connected components using BFS
    visited = set()
    components = []

    for start_folio in ALL_AZC_FOLIOS:
        if start_folio in visited:
            continue

        # BFS from this folio
        component = set()
        queue = [start_folio]

        while queue:
            folio = queue.pop(0)
            if folio in visited:
                continue
            visited.add(folio)
            component.add(folio)

            for neighbor in adjacency.get(folio, set()):
                if neighbor not in visited:
                    queue.append(neighbor)

        components.append(component)

    # Analyze components
    if len(components) == 1:
        connectivity = "FULLY_CONNECTED"
    else:
        connectivity = f"DISCONNECTED ({len(components)} components)"

    return {
        'connectivity': connectivity,
        'n_components': len(components),
        'components': [sorted(c) for c in sorted(components, key=len, reverse=True)],
        'largest_component_size': len(components[0]) if components else 0,
        'isolated_folios': [list(c)[0] for c in components if len(c) == 1]
    }


def analyze_family_bridges(bridge_counts: Dict[Tuple[str, str], int]) -> Dict:
    """Analyze bridging patterns within and across families."""
    within_zodiac = []
    within_ac = []
    cross_family = []

    azc_folios = sorted(ALL_AZC_FOLIOS)

    for i, folio_i in enumerate(azc_folios):
        for folio_j in azc_folios[i+1:]:
            pair = (folio_i, folio_j)
            count = bridge_counts.get(pair, 0)

            i_zodiac = folio_i in ZODIAC_FOLIOS
            j_zodiac = folio_j in ZODIAC_FOLIOS

            if i_zodiac and j_zodiac:
                within_zodiac.append(count)
            elif not i_zodiac and not j_zodiac:
                within_ac.append(count)
            else:
                cross_family.append(count)

    def stats(values):
        if not values:
            return {'mean': 0, 'n': 0, 'zero_count': 0}
        return {
            'mean': round(statistics.mean(values), 2),
            'n': len(values),
            'zero_count': sum(1 for v in values if v == 0),
            'zero_pct': round(sum(1 for v in values if v == 0) / len(values) * 100, 1)
        }

    return {
        'within_zodiac': stats(within_zodiac),
        'within_ac': stats(within_ac),
        'cross_family': stats(cross_family)
    }


def main():
    print("=" * 70)
    print("AZC ENTRY BRIDGE ANALYSIS")
    print("=" * 70)
    print("\nQuestion: From Currier A entries, are any AZC combinations illegal?")
    print("(i.e., never bridged by a single A entry)")
    print()

    # Step 1: Build token -> AZC profile
    print("1. Building Currier A entry -> AZC folio profiles...")
    token_profiles = build_token_azc_profiles()
    print(f"   Found {len(token_profiles)} unique tokens in AZC folios")

    # Step 2: Analyze bridge distribution
    print("\n2. Analyzing token bridge distribution...")
    bridge_dist = analyze_bridge_distribution(token_profiles)
    print(f"   Single-folio tokens: {bridge_dist['single_folio_tokens']} ({bridge_dist['single_folio_tokens']/bridge_dist['total_tokens']*100:.1f}%)")
    print(f"   Multi-folio tokens: {bridge_dist['multi_folio_tokens']} ({bridge_dist['multi_folio_tokens']/bridge_dist['total_tokens']*100:.1f}%)")
    print(f"   Mean folios per token: {bridge_dist['mean']}")
    print(f"   Max folios for one token: {bridge_dist['max']}")
    print(f"   Distribution: {bridge_dist['distribution']}")

    # Step 3: Build bridge matrix
    print("\n3. Building AZC folio bridge matrix...")
    bridge_counts, bridge_tokens = build_bridge_matrix(token_profiles)
    print(f"   Found {len(bridge_counts)} bridged folio pairs")

    # Total possible pairs
    n_folios = len(ALL_AZC_FOLIOS)
    total_pairs = n_folios * (n_folios - 1) // 2
    print(f"   Total possible pairs: {total_pairs}")

    # Step 4: Find unbridged pairs
    print("\n4. Finding unbridged (illegal) combinations...")
    unbridged = find_unbridged_pairs(bridge_counts)
    print(f"   UNBRIDGED PAIRS: {len(unbridged)}")

    if unbridged:
        print("\n   These AZC folio pairs are NEVER bridged by a single A entry:")
        for folio_i, folio_j in unbridged[:20]:
            i_family = "Zod" if folio_i in ZODIAC_FOLIOS else "A/C"
            j_family = "Zod" if folio_j in ZODIAC_FOLIOS else "A/C"
            print(f"      {folio_i} ({i_family}) <-> {folio_j} ({j_family})")
        if len(unbridged) > 20:
            print(f"      ... and {len(unbridged) - 20} more")
    else:
        print("   ALL pairs are bridged by at least one token!")

    # Step 5: Check connectivity
    print("\n5. Checking graph connectivity...")
    connectivity = check_graph_connectivity(bridge_counts)
    print(f"   Connectivity: {connectivity['connectivity']}")
    print(f"   Number of components: {connectivity['n_components']}")
    if connectivity['isolated_folios']:
        print(f"   Isolated folios: {connectivity['isolated_folios']}")

    # Step 6: Analyze family patterns
    print("\n6. Analyzing within/cross family bridges...")
    family_analysis = analyze_family_bridges(bridge_counts)
    print(f"   Within-Zodiac: mean={family_analysis['within_zodiac']['mean']} bridges, "
          f"{family_analysis['within_zodiac']['zero_pct']}% unbridged")
    print(f"   Within-A/C: mean={family_analysis['within_ac']['mean']} bridges, "
          f"{family_analysis['within_ac']['zero_pct']}% unbridged")
    print(f"   Cross-family: mean={family_analysis['cross_family']['mean']} bridges, "
          f"{family_analysis['cross_family']['zero_pct']}% unbridged")

    # Step 7: Show strongest bridges
    print("\n" + "=" * 70)
    print("STRONGEST BRIDGES (most tokens spanning both folios)")
    print("=" * 70)

    sorted_bridges = sorted(bridge_counts.items(), key=lambda x: x[1], reverse=True)
    for (folio_i, folio_j), count in sorted_bridges[:15]:
        i_family = "Zod" if folio_i in ZODIAC_FOLIOS else "A/C"
        j_family = "Zod" if folio_j in ZODIAC_FOLIOS else "A/C"
        sample = bridge_tokens.get((folio_i, folio_j), [])[:3]
        print(f"   {folio_i} ({i_family}) <-> {folio_j} ({j_family}): {count} tokens")
        if sample:
            print(f"      Examples: {sample}")

    # Step 8: Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if len(unbridged) == 0:
        verdict = "ALL_COMBINATIONS_LEGAL"
        interpretation = "Every AZC folio pair is bridged by at least one Currier A entry"
    elif len(unbridged) < total_pairs * 0.1:
        verdict = "MOSTLY_LEGAL"
        interpretation = f"Only {len(unbridged)}/{total_pairs} pairs ({len(unbridged)/total_pairs*100:.1f}%) are unbridged"
    elif len(unbridged) < total_pairs * 0.5:
        verdict = "PARTIAL_EXCLUSIVITY"
        interpretation = f"{len(unbridged)}/{total_pairs} pairs ({len(unbridged)/total_pairs*100:.1f}%) are unbridged"
    else:
        verdict = "STRONG_EXCLUSIVITY"
        interpretation = f"Most pairs ({len(unbridged)}/{total_pairs}) are unbridged"

    print(f"\n   >>> {verdict} <<<")
    print(f"   {interpretation}")
    print(f"   Graph is {connectivity['connectivity']}")

    # Save results
    output = {
        'probe_id': 'AZC_ENTRY_BRIDGES',
        'question': 'From Currier A entries, are any AZC combinations illegal?',
        'method': 'Token bridge analysis - count tokens appearing in multiple AZC folios',
        'data': {
            'n_tokens': len(token_profiles),
            'n_azc_folios': len(ALL_AZC_FOLIOS),
            'total_possible_pairs': total_pairs,
            'bridged_pairs': len(bridge_counts),
            'unbridged_pairs': len(unbridged)
        },
        'bridge_distribution': bridge_dist,
        'connectivity': connectivity,
        'family_analysis': family_analysis,
        'unbridged_pairs': [(i, j) for i, j in unbridged],
        'strongest_bridges': [
            {'pair': [i, j], 'count': c, 'examples': bridge_tokens.get((i, j), [])[:3]}
            for (i, j), c in sorted_bridges[:20]
        ],
        'verdict': {
            'overall': verdict,
            'interpretation': interpretation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
