#!/usr/bin/env python3
"""
MIDDLE-Level Incompatibility Graph Probe

Question: Which MIDDLEs cannot co-exist with which other MIDDLEs?

This is the ATOMIC incompatibility graph - the fundamental layer below
folio-level compatibility (discovered in azc_entry_bridges.py).

Configuration (Expert-Validated):
- Specification context: LINE (C233, C235, C473: line-atomic bundles)
- Data scope: AZC folios only (C442: compatibility filtering enforced here)
- Null model: Frequency-matched shuffle (protect against rare-MIDDLE artifacts)
- Sensitivity check: 2-line sliding window

Hypotheses:
- H1: PREFIX family clustering (within-PREFIX > cross-PREFIX compatibility)
- H2: f116v isolation is MIDDLE-driven (folio isolation = symptom)
"""

import csv
import json
import random
import statistics
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "middle_incompatibility.json"

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

# PREFIX definitions (for H1 stratification)
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# SUFFIX definitions (for parsing)
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Decompose token into PREFIX, MIDDLE, SUFFIX.
    Returns (prefix, middle, suffix) - any can be None.
    """
    if not token or len(token) < 2:
        return None, None, None

    # Skip invalid tokens
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    # Find prefix (longest match first)
    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    # Find suffix (longest match first)
    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    # Middle must be non-empty
    if not middle:
        middle = None

    return prefix, middle, suffix


def build_line_middle_sets(use_2line_window: bool = False) -> Tuple[Dict, Dict, Set]:
    """
    Build mapping: (folio, line) → set of MIDDLEs.
    Also tracks prefix for each MIDDLE for stratification.

    Args:
        use_2line_window: If True, merge adjacent lines into single context

    Returns:
        line_middles: {(folio, line_key) → set of MIDDLEs}
        middle_to_prefix: {middle → set of prefixes it appears with}
        all_middles: set of all observed MIDDLEs
    """
    # First pass: collect raw line data
    raw_line_data = defaultdict(list)  # (folio, line) → [(middle, prefix), ...]
    middle_to_prefix = defaultdict(set)
    all_middles = set()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('"transcriber"', row.get('transcriber', '')).strip().strip('"')
            if transcriber != 'H':
                continue

            # Handle quoted column names
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            line = row.get('"line_number"', row.get('line_number', '')).strip().strip('"')

            # Only AZC folios
            if folio not in ALL_AZC_FOLIOS:
                continue

            prefix, middle, suffix = decompose_token(word)

            if middle:
                raw_line_data[(folio, line)].append((middle, prefix))
                if prefix:
                    middle_to_prefix[middle].add(prefix)
                all_middles.add(middle)

    # Second pass: build line-level MIDDLE sets
    if use_2line_window:
        # Group by folio, sort lines, merge adjacent pairs
        folio_lines = defaultdict(list)
        for (folio, line), middles_prefixes in raw_line_data.items():
            folio_lines[folio].append((line, middles_prefixes))

        line_middles = {}
        for folio, lines in folio_lines.items():
            # Sort lines (attempt numeric sort if possible)
            try:
                sorted_lines = sorted(lines, key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
            except:
                sorted_lines = sorted(lines, key=lambda x: x[0])

            # Create 2-line windows
            for i in range(len(sorted_lines)):
                window_middles = set()
                # Current line
                for middle, prefix in sorted_lines[i][1]:
                    window_middles.add(middle)
                # Next line (if exists)
                if i + 1 < len(sorted_lines):
                    for middle, prefix in sorted_lines[i + 1][1]:
                        window_middles.add(middle)

                key = (folio, f"window_{i}")
                line_middles[key] = window_middles
    else:
        # Simple: each line is its own context
        line_middles = {}
        for (folio, line), middles_prefixes in raw_line_data.items():
            line_middles[(folio, line)] = {m for m, p in middles_prefixes}

    return line_middles, dict(middle_to_prefix), all_middles


def build_cooccurrence_matrix(line_middles: Dict) -> Dict[Tuple[str, str], int]:
    """
    Build sparse co-occurrence matrix.
    For each pair of MIDDLEs, count lines where both appear.
    """
    cooccurrence = defaultdict(int)

    for line_key, middles in line_middles.items():
        middle_list = sorted(middles)
        for i, m1 in enumerate(middle_list):
            for m2 in middle_list[i + 1:]:
                pair = (m1, m2)
                cooccurrence[pair] += 1

    return dict(cooccurrence)


def compute_null_expectation(line_middles: Dict, n_permutations: int = 1000) -> Dict[Tuple[str, str], float]:
    """
    Compute null model expectation via frequency-matched shuffle.

    Shuffles MIDDLEs across lines preserving:
    - Line length distribution
    - Per-MIDDLE frequency
    """
    print(f"   Computing null model ({n_permutations} permutations)...")

    # Build pool and line structure
    middle_pool = []
    line_lengths = []
    for middles in line_middles.values():
        middle_list = list(middles)
        middle_pool.extend(middle_list)
        line_lengths.append(len(middle_list))

    # Run permutations
    null_cooccurrence = defaultdict(list)

    for perm in range(n_permutations):
        if perm % 100 == 0:
            print(f"      Permutation {perm}/{n_permutations}...")

        # Shuffle pool
        shuffled_pool = middle_pool.copy()
        random.shuffle(shuffled_pool)

        # Reconstruct lines with same lengths
        idx = 0
        perm_cooccur = defaultdict(int)

        for length in line_lengths:
            if length < 2:
                idx += length
                continue

            line_middles_set = shuffled_pool[idx:idx + length]
            idx += length

            # Count co-occurrences in this shuffled line
            line_middles_sorted = sorted(set(line_middles_set))
            for i, m1 in enumerate(line_middles_sorted):
                for m2 in line_middles_sorted[i + 1:]:
                    pair = (m1, m2)
                    perm_cooccur[pair] += 1

        # Record this permutation's counts
        for pair, count in perm_cooccur.items():
            null_cooccurrence[pair].append(count)

    # Compute mean expectation for each pair
    expected = {}
    for pair, counts in null_cooccurrence.items():
        expected[pair] = statistics.mean(counts)

    return expected


def find_illegal_pairs(
    all_middles: Set[str],
    observed: Dict[Tuple[str, str], int],
    expected: Dict[Tuple[str, str], float],
    threshold: float = 0.5
) -> Tuple[List, List]:
    """
    Find MIDDLE pairs that are STATISTICALLY ILLEGAL:
    - Observed = 0
    - Expected > threshold (not just rare)
    """
    illegal = []
    trivially_absent = []

    all_middles_sorted = sorted(all_middles)

    for i, m1 in enumerate(all_middles_sorted):
        for m2 in all_middles_sorted[i + 1:]:
            pair = (m1, m2)
            obs = observed.get(pair, 0)
            exp = expected.get(pair, 0)

            if obs == 0:
                if exp > threshold:
                    illegal.append((pair, exp))
                else:
                    trivially_absent.append(pair)

    return illegal, trivially_absent


def analyze_graph(
    all_middles: Set[str],
    observed: Dict[Tuple[str, str], int]
) -> Dict:
    """
    Graph analysis: components, hubs, isolates.
    """
    # Build adjacency list
    adjacency = defaultdict(set)
    for (m1, m2), count in observed.items():
        if count > 0:
            adjacency[m1].add(m2)
            adjacency[m2].add(m1)

    # Find connected components via BFS
    visited = set()
    components = []

    for start_middle in all_middles:
        if start_middle in visited:
            continue

        component = set()
        queue = [start_middle]

        while queue:
            middle = queue.pop(0)
            if middle in visited:
                continue
            visited.add(middle)
            component.add(middle)

            for neighbor in adjacency.get(middle, set()):
                if neighbor not in visited:
                    queue.append(neighbor)

        components.append(component)

    # Sort by size
    components.sort(key=len, reverse=True)

    # Compute degree for each MIDDLE
    degree = {m: len(adjacency.get(m, set())) for m in all_middles}

    # Identify hubs (top 10% by degree) and isolates (degree 0)
    sorted_by_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)
    hub_threshold = len(all_middles) // 10
    hub_middles = [m for m, d in sorted_by_degree[:hub_threshold] if d > 0]
    isolated_middles = [m for m, d in degree.items() if d == 0]

    return {
        'n_components': len(components),
        'component_sizes': [len(c) for c in components],
        'components': [sorted(c) for c in components[:5]],  # Top 5 only
        'hub_middles': hub_middles[:20],  # Top 20 hubs
        'isolated_middles': isolated_middles,
        'degree_distribution': dict(Counter(degree.values()))
    }


def test_h1_prefix_clustering(
    all_middles: Set[str],
    observed: Dict[Tuple[str, str], int],
    middle_to_prefix: Dict[str, Set[str]]
) -> Dict:
    """
    H1: MIDDLEs within same PREFIX family are more compatible than cross-PREFIX.
    """
    within_prefix_legal = 0
    within_prefix_total = 0
    cross_prefix_legal = 0
    cross_prefix_total = 0

    all_middles_sorted = sorted(all_middles)

    for i, m1 in enumerate(all_middles_sorted):
        for m2 in all_middles_sorted[i + 1:]:
            pair = (m1, m2)
            is_legal = observed.get(pair, 0) > 0

            # Get prefixes for each middle
            p1 = middle_to_prefix.get(m1, set())
            p2 = middle_to_prefix.get(m2, set())

            # Check if any prefix overlap
            if p1 & p2:  # Shared prefix
                within_prefix_total += 1
                if is_legal:
                    within_prefix_legal += 1
            elif p1 and p2:  # Different prefixes
                cross_prefix_total += 1
                if is_legal:
                    cross_prefix_legal += 1

    within_pct = (within_prefix_legal / within_prefix_total * 100) if within_prefix_total > 0 else 0
    cross_pct = (cross_prefix_legal / cross_prefix_total * 100) if cross_prefix_total > 0 else 0

    verdict = "SUPPORTED" if within_pct > cross_pct else "REJECTED"

    return {
        'within_prefix_legal': within_prefix_legal,
        'within_prefix_total': within_prefix_total,
        'within_prefix_legal_pct': round(within_pct, 2),
        'cross_prefix_legal': cross_prefix_legal,
        'cross_prefix_total': cross_prefix_total,
        'cross_prefix_legal_pct': round(cross_pct, 2),
        'verdict': verdict
    }


def test_h2_f116v_isolation(
    line_middles: Dict,
    all_middles: Set[str],
    observed: Dict[Tuple[str, str], int]
) -> Dict:
    """
    H2: f116v isolation correlates with MIDDLE-level incompatibility.
    """
    # Extract MIDDLEs that appear in f116v
    f116v_middles = set()
    for (folio, line), middles in line_middles.items():
        if folio == 'f116v':
            f116v_middles.update(middles)

    # Extract MIDDLEs from all other folios
    other_middles = set()
    for (folio, line), middles in line_middles.items():
        if folio != 'f116v':
            other_middles.update(middles)

    # Check compatibility between f116v MIDDLEs and other MIDDLEs
    compatible_with_other = 0
    total_pairs = 0

    for m1 in f116v_middles:
        for m2 in other_middles:
            if m1 == m2:
                continue
            pair = tuple(sorted([m1, m2]))
            total_pairs += 1
            if observed.get(pair, 0) > 0:
                compatible_with_other += 1

    compatibility_pct = (compatible_with_other / total_pairs * 100) if total_pairs > 0 else 0

    # Compare to average compatibility for other folios
    other_folio_middles = defaultdict(set)
    for (folio, line), middles in line_middles.items():
        if folio != 'f116v':
            other_folio_middles[folio].update(middles)

    other_compatibility_rates = []
    for folio, folio_mids in other_folio_middles.items():
        other_mids = other_middles - folio_mids
        compatible = 0
        total = 0
        for m1 in folio_mids:
            for m2 in other_mids:
                if m1 == m2:
                    continue
                pair = tuple(sorted([m1, m2]))
                total += 1
                if observed.get(pair, 0) > 0:
                    compatible += 1
        if total > 0:
            other_compatibility_rates.append(compatible / total * 100)

    avg_other_compatibility = statistics.mean(other_compatibility_rates) if other_compatibility_rates else 0

    # f116v is isolated if its compatibility is much lower than average
    is_isolated = compatibility_pct < avg_other_compatibility * 0.8  # 20% lower threshold

    verdict = "SUPPORTED" if is_isolated else "REJECTED"

    return {
        'f116v_middles_count': len(f116v_middles),
        'f116v_middles_sample': sorted(f116v_middles)[:10],
        'f116v_compatibility_pct': round(compatibility_pct, 2),
        'other_folios_avg_compatibility_pct': round(avg_other_compatibility, 2),
        'is_isolated': is_isolated,
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("MIDDLE-LEVEL INCOMPATIBILITY GRAPH PROBE")
    print("=" * 70)
    print("\nQuestion: Which MIDDLEs cannot co-exist with which other MIDDLEs?")
    print()

    # Step 1: Build line-level MIDDLE sets (primary analysis)
    print("1. Building line-level MIDDLE sets (single-line context)...")
    line_middles_1line, middle_to_prefix, all_middles = build_line_middle_sets(use_2line_window=False)
    print(f"   Found {len(all_middles)} unique MIDDLEs in {len(line_middles_1line)} lines")

    # Step 2: Build co-occurrence matrix
    print("\n2. Building co-occurrence matrix...")
    observed_1line = build_cooccurrence_matrix(line_middles_1line)
    print(f"   Found {len(observed_1line)} MIDDLE pairs with >=1 co-occurrence")

    # Total possible pairs
    n_middles = len(all_middles)
    total_pairs = n_middles * (n_middles - 1) // 2
    print(f"   Total possible pairs: {total_pairs}")

    # Step 3: Compute null model
    print("\n3. Computing frequency-matched null model...")
    expected_1line = compute_null_expectation(line_middles_1line, n_permutations=1000)

    # Step 4: Find illegal pairs
    print("\n4. Finding illegal MIDDLE pairs...")
    illegal_1line, trivial_1line = find_illegal_pairs(all_middles, observed_1line, expected_1line, threshold=0.5)
    print(f"   STATISTICALLY ILLEGAL pairs: {len(illegal_1line)}")
    print(f"   Trivially absent (rare MIDDLEs): {len(trivial_1line)}")

    legal_pairs = total_pairs - len(illegal_1line) - len(trivial_1line)
    print(f"   Legal pairs: {legal_pairs}")

    # Show top illegal pairs
    if illegal_1line:
        print("\n   Top 10 illegal pairs (by expected co-occurrence):")
        sorted_illegal = sorted(illegal_1line, key=lambda x: x[1], reverse=True)
        for (m1, m2), exp in sorted_illegal[:10]:
            print(f"      {m1} <-> {m2}: expected {exp:.2f}, observed 0")

    # Step 5: Graph analysis
    print("\n5. Analyzing graph structure...")
    graph_analysis = analyze_graph(all_middles, observed_1line)
    print(f"   Connected components: {graph_analysis['n_components']}")
    print(f"   Largest component size: {graph_analysis['component_sizes'][0] if graph_analysis['component_sizes'] else 0}")
    print(f"   Isolated MIDDLEs: {len(graph_analysis['isolated_middles'])}")

    if graph_analysis['hub_middles']:
        print(f"   Top hub MIDDLEs: {graph_analysis['hub_middles'][:5]}")

    # Step 6: Test H1 (PREFIX clustering)
    print("\n6. Testing H1: PREFIX family clustering...")
    h1_result = test_h1_prefix_clustering(all_middles, observed_1line, middle_to_prefix)
    print(f"   Within-PREFIX legal: {h1_result['within_prefix_legal_pct']}%")
    print(f"   Cross-PREFIX legal: {h1_result['cross_prefix_legal_pct']}%")
    print(f"   Verdict: {h1_result['verdict']}")

    # Step 7: Test H2 (f116v isolation)
    print("\n7. Testing H2: f116v isolation...")
    h2_result = test_h2_f116v_isolation(line_middles_1line, all_middles, observed_1line)
    print(f"   f116v MIDDLEs: {h2_result['f116v_middles_count']}")
    print(f"   f116v compatibility: {h2_result['f116v_compatibility_pct']}%")
    print(f"   Other folios average: {h2_result['other_folios_avg_compatibility_pct']}%")
    print(f"   Verdict: {h2_result['verdict']}")

    # Step 8: 2-line sensitivity check
    print("\n8. Running 2-line sensitivity check...")
    line_middles_2line, _, _ = build_line_middle_sets(use_2line_window=True)
    observed_2line = build_cooccurrence_matrix(line_middles_2line)
    expected_2line = compute_null_expectation(line_middles_2line, n_permutations=500)  # Fewer perms for speed
    illegal_2line, trivial_2line = find_illegal_pairs(all_middles, observed_2line, expected_2line, threshold=0.5)

    # Compare
    illegal_pairs_1line_set = {pair for pair, exp in illegal_1line}
    illegal_pairs_2line_set = {pair for pair, exp in illegal_2line}
    overlap = illegal_pairs_1line_set & illegal_pairs_2line_set
    overlap_pct = len(overlap) / len(illegal_pairs_1line_set) * 100 if illegal_pairs_1line_set else 0

    print(f"   1-line illegal pairs: {len(illegal_1line)}")
    print(f"   2-line illegal pairs: {len(illegal_2line)}")
    print(f"   Overlap (robust): {len(overlap)} ({overlap_pct:.1f}%)")

    sensitivity_check = {
        'method': '2-line sliding window',
        'illegal_pairs_1line': len(illegal_1line),
        'illegal_pairs_2line': len(illegal_2line),
        'overlap': len(overlap),
        'overlap_pct': round(overlap_pct, 2)
    }

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    sparsity = (len(illegal_1line) + len(trivial_1line)) / total_pairs if total_pairs > 0 else 0

    if sparsity > 0.5:
        structure_verdict = "SPARSE_GRAPH"
        interpretation = "MIDDLE vocabulary is partitioned into discrimination regimes"
    elif len(illegal_1line) > 0:
        structure_verdict = "PARTIAL_STRUCTURE"
        interpretation = f"{len(illegal_1line)} illegal pairs found - some discrimination regimes exist"
    else:
        structure_verdict = "DENSE_GRAPH"
        interpretation = "Most MIDDLEs can work with most others"

    print(f"\n   >>> {structure_verdict} <<<")
    print(f"   {interpretation}")
    print(f"   H1 (PREFIX clustering): {h1_result['verdict']}")
    print(f"   H2 (f116v isolation): {h2_result['verdict']}")
    print(f"   Robustness (2-line overlap): {overlap_pct:.1f}%")

    # Save results
    output = {
        'probe_id': 'MIDDLE_INCOMPATIBILITY',
        'question': 'Which MIDDLEs cannot co-exist with which other MIDDLEs?',
        'configuration': {
            'context': 'line (C233, C235, C473)',
            'scope': 'AZC folios only',
            'null_model': 'frequency-matched shuffle (1000 permutations)',
            'threshold': 0.5
        },
        'summary': {
            'total_middles': len(all_middles),
            'total_possible_pairs': total_pairs,
            'legal_pairs': legal_pairs,
            'illegal_pairs': len(illegal_1line),
            'trivially_absent': len(trivial_1line),
            'sparsity': round(sparsity, 4)
        },
        'null_model': {
            'n_permutations': 1000,
            'threshold': 0.5,
            'pairs_exceeding_threshold': len([p for p in expected_1line.values() if p > 0.5])
        },
        'graph_analysis': graph_analysis,
        'hypotheses': {
            'H1_prefix_clustering': h1_result,
            'H2_f116v_isolation': h2_result
        },
        'sensitivity_check': sensitivity_check,
        'illegal_pairs': [(list(pair), round(exp, 3)) for pair, exp in sorted(illegal_1line, key=lambda x: x[1], reverse=True)[:100]],
        'strongest_bridges': [
            (list(pair), count) for pair, count in sorted(observed_1line.items(), key=lambda x: x[1], reverse=True)[:50]
        ],
        'verdict': {
            'structure': structure_verdict,
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
