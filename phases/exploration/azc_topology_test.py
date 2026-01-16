#!/usr/bin/env python3
"""
TEST 8: AZC Internal Topology Analysis

This test avoids Currier B entirely and examines AZC's internal structure.

Hypothesis:
  If AZC scaffolds mirror circulatory topology, Zodiac AZC should show:
  - Consistent cyclic ordering
  - Minimal branching
  - High self-transition
  - Uniform entry/exit roles

Method:
  - Build directed graph from AZC placement transitions
  - Measure: cycle rank, graph diameter, degree distribution
  - Compare against random graphs and tree structures

Support outcome:
  Zodiac AZC topology closer to single-cycle graphs than trees.
"""

import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
AZC_FOLIO_FEATURES = RESULTS / "azc_folio_features.json"

def load_transcription():
    """Load full transcription with placement codes."""
    rows = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            rows.append(row)
    return rows

def load_azc_features():
    """Load AZC folio features."""
    with open(AZC_FOLIO_FEATURES) as f:
        data = json.load(f)
    return data.get('folios', {}), data.get('metadata', {})

def get_azc_sequences(rows):
    """
    Extract AZC token sequences by folio, preserving order.
    Returns: {folio: [(token, placement), ...]}
    """
    folio_sequences = defaultdict(list)

    for row in rows:
        language = row.get('language', '').strip('"')
        placement = row.get('placement', '').strip('"')
        token = row.get('word', '').strip('"')
        folio = row.get('folio', '').strip('"')

        # AZC is marked as 'NA' in language column
        if language == 'NA' and placement and token:
            # Skip damaged tokens
            if '*' in token:
                continue
            folio_sequences[folio].append((token, placement))

    return dict(folio_sequences)

def classify_folio_type(folio, azc_features):
    """Classify folio as Zodiac, Cosmological, or Other based on section."""
    if folio not in azc_features:
        return 'UNKNOWN'

    section = azc_features[folio].get('section', '')
    if section == 'Z':
        return 'ZODIAC'
    elif section == 'C':
        return 'COSMOLOGICAL'
    elif section == 'A':
        return 'ASTRONOMICAL'
    elif section == 'H':
        return 'HERBAL'
    else:
        return 'OTHER'

def build_transition_graph(sequences, folio_type_filter=None, azc_features=None):
    """
    Build a directed graph of placement transitions.

    Returns:
    - nodes: set of placement types
    - edges: Counter of (from, to) transitions
    - self_loops: Counter of same-placement sequences
    """
    nodes = set()
    edges = Counter()
    self_loops = Counter()

    for folio, seq in sequences.items():
        # Filter by folio type if specified
        if folio_type_filter and azc_features:
            if classify_folio_type(folio, azc_features) != folio_type_filter:
                continue

        placements = [p for _, p in seq]

        for p in placements:
            nodes.add(p)

        # Count transitions
        for i in range(len(placements) - 1):
            p1, p2 = placements[i], placements[i+1]
            if p1 == p2:
                self_loops[p1] += 1
            else:
                edges[(p1, p2)] += 1

    return nodes, edges, self_loops

def compute_graph_metrics(nodes, edges):
    """
    Compute graph topology metrics without networkx.

    Returns dict of metrics.
    """
    if not nodes or not edges:
        return {'error': 'empty_graph'}

    n_nodes = len(nodes)
    n_edges = len(edges)  # unique edges
    total_edge_weight = sum(edges.values())

    # Build adjacency
    out_degree = defaultdict(int)
    in_degree = defaultdict(int)

    for (src, dst), count in edges.items():
        out_degree[src] += count
        in_degree[dst] += count

    # Degree statistics
    out_degrees = [out_degree.get(n, 0) for n in nodes]
    in_degrees = [in_degree.get(n, 0) for n in nodes]
    total_degrees = [out_degree.get(n, 0) + in_degree.get(n, 0) for n in nodes]

    # Cycle rank approximation (for directed graphs)
    # cycle_rank = edges - nodes + connected_components
    # For a single cycle: cycle_rank = 1
    # For a tree: cycle_rank = 0
    cycle_rank = n_edges - n_nodes + 1  # Simplified, assumes connected

    # Graph density
    max_edges = n_nodes * (n_nodes - 1)  # directed
    density = n_edges / max_edges if max_edges > 0 else 0

    # Reciprocity (bidirectional edges)
    reciprocal_count = 0
    for (src, dst) in edges:
        if (dst, src) in edges:
            reciprocal_count += 1
    reciprocity = reciprocal_count / (2 * n_edges) if n_edges > 0 else 0

    # Find strongly connected components (simplified)
    # For cyclic graphs, expect high SCC coverage

    # Transition entropy (how predictable are transitions?)
    # Group by source node
    source_transitions = defaultdict(list)
    for (src, dst), count in edges.items():
        source_transitions[src].append((dst, count))

    # Average entropy per source
    entropies = []
    for src, transitions in source_transitions.items():
        total = sum(c for _, c in transitions)
        if total > 0 and len(transitions) > 1:
            probs = [c/total for _, c in transitions]
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            entropies.append(entropy)

    avg_transition_entropy = np.mean(entropies) if entropies else 0

    # Degree variance (cycles have uniform degree, trees don't)
    degree_variance = np.var(total_degrees) if total_degrees else 0
    degree_cv = np.std(total_degrees) / np.mean(total_degrees) if np.mean(total_degrees) > 0 else 0

    return {
        'n_nodes': n_nodes,
        'n_unique_edges': n_edges,
        'total_transitions': total_edge_weight,
        'cycle_rank': cycle_rank,
        'density': float(density),
        'reciprocity': float(reciprocity),
        'avg_transition_entropy': float(avg_transition_entropy),
        'degree_mean': float(np.mean(total_degrees)),
        'degree_variance': float(degree_variance),
        'degree_cv': float(degree_cv),
        'max_out_degree': max(out_degrees) if out_degrees else 0,
        'max_in_degree': max(in_degrees) if in_degrees else 0
    }

def generate_reference_graphs(n_nodes, n_edges):
    """
    Generate reference graph metrics for comparison.

    Returns metrics for:
    - Pure cycle (n nodes, n edges forming single loop)
    - Random graph (Erdos-Renyi)
    - Tree (n-1 edges, no cycles)
    """
    references = {}

    # Pure cycle: each node has exactly 1 in-edge and 1 out-edge
    references['pure_cycle'] = {
        'n_nodes': n_nodes,
        'n_unique_edges': n_nodes,  # exactly n edges for n-cycle
        'cycle_rank': 1,  # single cycle
        'density': n_nodes / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0,
        'reciprocity': 0,  # directed cycle has no reciprocal edges
        'degree_cv': 0,  # uniform degree
        'description': 'Single directed cycle'
    }

    # Tree: n-1 edges, no cycles
    references['tree'] = {
        'n_nodes': n_nodes,
        'n_unique_edges': n_nodes - 1,
        'cycle_rank': 0,  # no cycles
        'density': (n_nodes - 1) / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0,
        'reciprocity': 0,
        'degree_cv': 0.5,  # varies by structure
        'description': 'Directed tree (no cycles)'
    }

    # Random graph (Erdos-Renyi with same edge count)
    p = n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0
    expected_cycle_rank = n_edges - n_nodes + 1
    references['random'] = {
        'n_nodes': n_nodes,
        'n_unique_edges': n_edges,
        'cycle_rank': max(0, expected_cycle_rank),
        'density': float(p),
        'reciprocity': p,  # Expected reciprocity in random directed graph
        'degree_cv': 1 / np.sqrt(n_nodes * p) if n_nodes * p > 0 else 1,
        'description': f'Random directed graph (p={p:.3f})'
    }

    return references

def analyze_placement_ordering(sequences, folio_type_filter=None, azc_features=None):
    """
    Analyze whether placements follow consistent ordering (R1->R2->R3 etc).

    Cyclic structures should show:
    - Consistent forward progression
    - Return to start (R3->R1 or similar)
    """
    # Track R-series progressions
    r_forward = 0  # R1->R2, R2->R3
    r_backward = 0  # R2->R1, R3->R2
    r_wrap = 0  # R3->R1 (cycle completion)

    # Track S-series
    s_forward = 0
    s_backward = 0

    for folio, seq in sequences.items():
        if folio_type_filter and azc_features:
            if classify_folio_type(folio, azc_features) != folio_type_filter:
                continue

        placements = [p for _, p in seq]

        for i in range(len(placements) - 1):
            p1, p2 = placements[i], placements[i+1]

            # R-series analysis
            if p1.startswith('R') and p2.startswith('R'):
                try:
                    n1 = int(p1[1:]) if len(p1) > 1 else 0
                    n2 = int(p2[1:]) if len(p2) > 1 else 0

                    if n2 == n1 + 1:
                        r_forward += 1
                    elif n2 == n1 - 1:
                        r_backward += 1
                    elif n1 == 3 and n2 == 1:  # Wrap-around
                        r_wrap += 1
                except ValueError:
                    pass

            # S-series analysis
            if p1.startswith('S') and p2.startswith('S'):
                try:
                    n1 = int(p1[1:]) if len(p1) > 1 else 0
                    n2 = int(p2[1:]) if len(p2) > 1 else 0

                    if n2 == n1 + 1:
                        s_forward += 1
                    elif n2 == n1 - 1:
                        s_backward += 1
                except ValueError:
                    pass

    r_total = r_forward + r_backward + r_wrap
    s_total = s_forward + s_backward

    return {
        'r_series': {
            'forward': r_forward,
            'backward': r_backward,
            'wrap_around': r_wrap,
            'total': r_total,
            'forward_ratio': r_forward / r_total if r_total > 0 else 0,
            'cyclic_signature': (r_forward + r_wrap) / r_total if r_total > 0 else 0
        },
        's_series': {
            'forward': s_forward,
            'backward': s_backward,
            'total': s_total,
            'forward_ratio': s_forward / s_total if s_total > 0 else 0
        }
    }

def run_test_8():
    """
    TEST 8: AZC Internal Topology vs Circulatory Archetype

    Tests whether AZC (especially Zodiac) shows cyclic rather than tree-like topology.
    """
    print("=" * 70)
    print("TEST 8: AZC Internal Topology Analysis")
    print("=" * 70)
    print("\nHypothesis: If AZC mirrors circulatory topology, it should show:")
    print("  - Consistent cyclic ordering")
    print("  - Low degree variance (uniform connectivity)")
    print("  - High cycle rank relative to trees")
    print("=" * 70)

    # Load data
    print("\n[Loading data...]")
    rows = load_transcription()
    azc_features, metadata = load_azc_features()
    sequences = get_azc_sequences(rows)

    print(f"  AZC folios: {len(sequences)}")
    print(f"  Total AZC tokens: {sum(len(s) for s in sequences.values())}")

    results = {
        'by_type': {},
        'ordering_analysis': {},
        'topology_verdict': {}
    }

    # Analyze by folio type
    for folio_type in ['ZODIAC', 'COSMOLOGICAL', 'ALL']:
        print(f"\n{'='*70}")
        print(f"Analyzing: {folio_type}")
        print("=" * 70)

        if folio_type == 'ALL':
            nodes, edges, self_loops = build_transition_graph(sequences)
        else:
            nodes, edges, self_loops = build_transition_graph(
                sequences, folio_type_filter=folio_type, azc_features=azc_features
            )

        if not nodes:
            print(f"  No data for {folio_type}")
            continue

        print(f"\n[1] Graph Structure:")
        print(f"    Nodes (placement types): {len(nodes)}")
        print(f"    Unique edges: {len(edges)}")
        print(f"    Self-loop placements: {len(self_loops)}")

        # Show top transitions
        print(f"\n[2] Top transitions:")
        for (src, dst), count in edges.most_common(10):
            print(f"    {src} -> {dst}: {count}")

        # Compute metrics
        metrics = compute_graph_metrics(nodes, edges)

        print(f"\n[3] Graph Metrics:")
        print(f"    Cycle rank: {metrics.get('cycle_rank', 'N/A')}")
        print(f"    Density: {metrics.get('density', 0):.4f}")
        print(f"    Reciprocity: {metrics.get('reciprocity', 0):.4f}")
        print(f"    Transition entropy: {metrics.get('avg_transition_entropy', 0):.3f}")
        print(f"    Degree CV: {metrics.get('degree_cv', 0):.3f}")

        # Generate reference comparisons
        refs = generate_reference_graphs(len(nodes), len(edges))

        print(f"\n[4] Comparison to Reference Graphs:")
        print(f"    Pure cycle would have:")
        print(f"      - Cycle rank: 1")
        print(f"      - Degree CV: 0 (uniform)")
        print(f"    Tree would have:")
        print(f"      - Cycle rank: 0")
        print(f"    Random graph would have:")
        print(f"      - Cycle rank: ~{refs['random']['cycle_rank']}")

        # Ordering analysis
        if folio_type == 'ALL':
            ordering = analyze_placement_ordering(sequences)
        else:
            ordering = analyze_placement_ordering(
                sequences, folio_type_filter=folio_type, azc_features=azc_features
            )

        print(f"\n[5] Placement Ordering Analysis:")
        print(f"    R-series transitions:")
        print(f"      Forward (R1->R2->R3): {ordering['r_series']['forward']}")
        print(f"      Backward: {ordering['r_series']['backward']}")
        print(f"      Wrap-around (R3->R1): {ordering['r_series']['wrap_around']}")
        print(f"      Forward ratio: {ordering['r_series']['forward_ratio']:.3f}")
        print(f"      Cyclic signature: {ordering['r_series']['cyclic_signature']:.3f}")

        print(f"    S-series transitions:")
        print(f"      Forward: {ordering['s_series']['forward']}")
        print(f"      Backward: {ordering['s_series']['backward']}")
        print(f"      Forward ratio: {ordering['s_series']['forward_ratio']:.3f}")

        # Verdict for this type
        cyclic_evidence = []
        tree_evidence = []

        # Check cycle rank
        if metrics.get('cycle_rank', 0) > 0:
            cyclic_evidence.append(f"cycle_rank={metrics['cycle_rank']} > 0")
        else:
            tree_evidence.append("cycle_rank=0 (tree-like)")

        # Check degree uniformity
        if metrics.get('degree_cv', 1) < 0.5:
            cyclic_evidence.append(f"low degree_cv={metrics['degree_cv']:.3f} (uniform)")
        else:
            tree_evidence.append(f"high degree_cv={metrics['degree_cv']:.3f} (non-uniform)")

        # Check R-series ordering
        if ordering['r_series']['cyclic_signature'] > 0.7:
            cyclic_evidence.append(f"strong cyclic ordering ({ordering['r_series']['cyclic_signature']:.2f})")
        elif ordering['r_series']['forward_ratio'] > 0.6:
            cyclic_evidence.append(f"consistent forward progression ({ordering['r_series']['forward_ratio']:.2f})")

        print(f"\n[6] Topology Verdict for {folio_type}:")
        print(f"    Evidence for CYCLIC structure: {len(cyclic_evidence)}")
        for e in cyclic_evidence:
            print(f"      + {e}")
        print(f"    Evidence for TREE structure: {len(tree_evidence)}")
        for e in tree_evidence:
            print(f"      - {e}")

        if len(cyclic_evidence) > len(tree_evidence):
            verdict = "CYCLIC"
            print(f"    -> {folio_type} shows CYCLIC topology")
        elif len(tree_evidence) > len(cyclic_evidence):
            verdict = "TREE-LIKE"
            print(f"    -> {folio_type} shows TREE-LIKE topology")
        else:
            verdict = "MIXED"
            print(f"    -> {folio_type} shows MIXED topology")

        results['by_type'][folio_type] = {
            'metrics': metrics,
            'ordering': ordering,
            'references': refs,
            'verdict': verdict,
            'cyclic_evidence': cyclic_evidence,
            'tree_evidence': tree_evidence
        }

    # Final summary
    print("\n" + "=" * 70)
    print("TEST 8 SUMMARY")
    print("=" * 70)

    zodiac = results['by_type'].get('ZODIAC', {})
    cosmo = results['by_type'].get('COSMOLOGICAL', {})

    print("\nTopology verdicts:")
    for ftype, data in results['by_type'].items():
        print(f"  {ftype}: {data.get('verdict', 'N/A')}")

    # Overall interpretation
    print("\n[INTERPRETATION]")
    if zodiac.get('verdict') == 'CYCLIC':
        print("  Zodiac AZC shows CYCLIC topology - consistent with circulatory archetype")
        print("  This supports (but does not prove) the cognitive-map interpretation")
        results['supports_circulatory'] = True
    else:
        print("  Zodiac AZC does NOT show clear cyclic topology")
        print("  The circulatory archetype is not strongly supported")
        results['supports_circulatory'] = False

    # Save results
    output_path = RESULTS / "azc_topology_analysis.json"

    # Convert Counter objects to dicts for JSON
    output = {
        'metadata': {
            'test': 'TEST 8 - AZC Internal Topology',
            'hypothesis': 'AZC shows cyclic rather than tree-like structure'
        },
        'results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n[SAVED] {output_path}")

    return results

if __name__ == "__main__":
    run_test_8()
