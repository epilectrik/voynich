#!/usr/bin/env python3
"""
Phase 18, Task 4: B->A Reference Graph Construction

Builds a directed graph showing how Currier B entries reference Currier A entries
through shared heading words. Analyzes graph structure, co-citation patterns,
and positional relationships.

Output:
- reference_graph_analysis_report.json
- reference_graph.graphml (for visualization)
- reference_graph_edges.csv (edge list)
"""

import csv
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'pa', 'py', 'ky', 'ty', 'fa', 'fs', 'ks', 'r*'
]

MIN_ENTRY_WORDS = 9

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
    """Load the full corpus."""
    filepath = 'data/transcriptions/interlinear_full_words.txt'
    words = []
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to H (PRIMARY) transcriber only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')
            currier = row.get('language', '').strip().strip('"')
            section = row.get('section', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 2:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num,
                    'currier': currier,
                    'section': section
                })

    return words


def segment_by_folio(corpus: List[Dict], currier: str) -> Dict[str, List[Dict]]:
    """Segment corpus by folio for given Currier language."""
    entries = defaultdict(list)
    for w in corpus:
        if w['currier'] == currier:
            entries[w['folio']].append(w)

    # Filter to valid entries
    return {f: e for f, e in entries.items() if len(e) >= MIN_ENTRY_WORDS}


def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [3, 2]:
        if len(word) >= length and word[:length] in KNOWN_PREFIXES:
            return word[:length]
    return word[:2] if len(word) >= 2 else word


# =============================================================================
# HEADING EXTRACTION
# =============================================================================

def extract_headings(entries: Dict[str, List[Dict]], concentration_threshold: float = 0.7) -> Dict[str, Dict]:
    """
    Extract heading words from Currier A entries.

    Headings are words that appear >70% in Part 1 of entries.
    """
    # Compute part assignments for all words
    word_part_counts = defaultdict(lambda: {'part1': 0, 'part2': 0, 'part3': 0, 'total': 0})

    for folio, entry in entries.items():
        n = len(entry)
        third = n // 3

        for i, w in enumerate(entry):
            word = w['word']
            word_part_counts[word]['total'] += 1

            if i < third:
                word_part_counts[word]['part1'] += 1
            elif i < 2 * third:
                word_part_counts[word]['part2'] += 1
            else:
                word_part_counts[word]['part3'] += 1

    # Find heading candidates
    headings = {}
    for word, counts in word_part_counts.items():
        if counts['total'] >= 2:  # Minimum frequency
            concentration = counts['part1'] / counts['total']
            if concentration >= concentration_threshold:
                headings[word] = {
                    'part1_count': counts['part1'],
                    'total_count': counts['total'],
                    'concentration': round(concentration, 3),
                    'prefix': get_prefix(word)
                }

    return headings


def get_entry_heading(entry: List[Dict]) -> str:
    """Get the first word of an entry (its heading)."""
    if entry:
        return entry[0]['word']
    return ''


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def build_reference_graph(a_entries: Dict[str, List[Dict]],
                          b_entries: Dict[str, List[Dict]],
                          a_headings: Dict[str, Dict]) -> Dict:
    """
    Build directed graph: B entry -> A entry when B contains A's heading word.

    Returns graph structure as dictionary.
    """
    # Build A entry heading lookup
    a_folio_headings = {}
    for folio, entry in a_entries.items():
        heading = get_entry_heading(entry)
        a_folio_headings[folio] = heading

    # Reverse lookup: heading -> A folio
    heading_to_a_folio = defaultdict(list)
    for folio, heading in a_folio_headings.items():
        if heading:
            heading_to_a_folio[heading].append(folio)

    # Build graph
    nodes = {
        'a_nodes': {},
        'b_nodes': {}
    }

    edges = []

    # A nodes
    for folio, entry in a_entries.items():
        heading = get_entry_heading(entry)
        nodes['a_nodes'][folio] = {
            'type': 'A',
            'folio': folio,
            'word_count': len(entry),
            'heading': heading,
            'heading_prefix': get_prefix(heading) if heading else '',
            'section': entry[0].get('section', 'H') if entry else 'H'
        }

    # B nodes
    for folio, entry in b_entries.items():
        nodes['b_nodes'][folio] = {
            'type': 'B',
            'folio': folio,
            'word_count': len(entry),
            'section': entry[0].get('section', '') if entry else ''
        }

    # Build edges: B -> A
    for b_folio, b_entry in b_entries.items():
        b_words = set(w['word'] for w in b_entry)

        # Check each A heading
        for a_folio, a_data in nodes['a_nodes'].items():
            a_heading = a_data['heading']

            if a_heading and a_heading in b_words:
                # Count occurrences
                count = sum(1 for w in b_entry if w['word'] == a_heading)

                edges.append({
                    'source': b_folio,
                    'target': a_folio,
                    'heading_word': a_heading,
                    'count': count,
                    'type': 'B_REFERENCES_A'
                })

    return {
        'nodes': nodes,
        'edges': edges
    }


# =============================================================================
# GRAPH STATISTICS
# =============================================================================

def compute_graph_statistics(graph: Dict) -> Dict:
    """Compute comprehensive statistics about the reference graph."""

    edges = graph['edges']
    a_nodes = graph['nodes']['a_nodes']
    b_nodes = graph['nodes']['b_nodes']

    # Basic counts
    n_a = len(a_nodes)
    n_b = len(b_nodes)
    n_edges = len(edges)

    # Degree calculations
    a_in_degree = Counter()  # How many B entries reference each A
    b_out_degree = Counter()  # How many A entries each B references
    edge_weights = []

    for edge in edges:
        a_in_degree[edge['target']] += 1
        b_out_degree[edge['source']] += 1
        edge_weights.append(edge['count'])

    # Isolated nodes
    isolated_a = [f for f in a_nodes if a_in_degree[f] == 0]
    isolated_b = [f for f in b_nodes if b_out_degree[f] == 0]

    # Most referenced/referencing
    most_referenced_a = a_in_degree.most_common(10)
    most_referencing_b = b_out_degree.most_common(10)

    # Statistics
    a_in_degrees = [a_in_degree[f] for f in a_nodes]
    b_out_degrees = [b_out_degree[f] for f in b_nodes]

    return {
        'basic_counts': {
            'n_a_nodes': n_a,
            'n_b_nodes': n_b,
            'n_edges': n_edges,
            'density': round(n_edges / (n_a * n_b), 4) if n_a * n_b > 0 else 0
        },

        'a_node_in_degree': {
            'mean': round(np.mean(a_in_degrees), 2),
            'std': round(np.std(a_in_degrees), 2),
            'max': max(a_in_degrees) if a_in_degrees else 0,
            'min': min(a_in_degrees) if a_in_degrees else 0,
            'median': round(np.median(a_in_degrees), 2)
        },

        'b_node_out_degree': {
            'mean': round(np.mean(b_out_degrees), 2),
            'std': round(np.std(b_out_degrees), 2),
            'max': max(b_out_degrees) if b_out_degrees else 0,
            'min': min(b_out_degrees) if b_out_degrees else 0,
            'median': round(np.median(b_out_degrees), 2)
        },

        'edge_weights': {
            'mean': round(np.mean(edge_weights), 2) if edge_weights else 0,
            'max': max(edge_weights) if edge_weights else 0,
            'total': sum(edge_weights)
        },

        'isolated_nodes': {
            'a_isolated_count': len(isolated_a),
            'a_isolated_folios': isolated_a[:20],
            'b_isolated_count': len(isolated_b),
            'b_isolated_folios': isolated_b[:20]
        },

        'most_referenced_a': [
            {'folio': f, 'in_degree': d, 'heading': a_nodes[f]['heading']}
            for f, d in most_referenced_a
        ],

        'most_referencing_b': [
            {'folio': f, 'out_degree': d}
            for f, d in most_referencing_b
        ]
    }


# =============================================================================
# CO-CITATION ANALYSIS
# =============================================================================

def co_citation_analysis(graph: Dict) -> Dict:
    """
    Analyze which A entries are cited together by B entries.

    Co-citation = when multiple A entries are referenced by the same B entry.
    """
    edges = graph['edges']
    a_nodes = graph['nodes']['a_nodes']

    # Build B -> [A entries referenced] mapping
    b_references = defaultdict(set)
    for edge in edges:
        b_references[edge['source']].add(edge['target'])

    # Count co-citations
    co_citation_counts = Counter()
    for b_folio, a_set in b_references.items():
        a_list = sorted(a_set)
        # Count pairs
        for i, a1 in enumerate(a_list):
            for a2 in a_list[i+1:]:
                pair = (a1, a2)
                co_citation_counts[pair] += 1

    # Top co-cited pairs
    top_pairs = co_citation_counts.most_common(20)

    # A entries with most co-citations
    a_co_citation_total = Counter()
    for (a1, a2), count in co_citation_counts.items():
        a_co_citation_total[a1] += count
        a_co_citation_total[a2] += count

    # Cluster A entries by co-citation profile
    # Simple approach: group A entries that share many co-citations
    a_co_citation_vectors = {}
    all_a = list(a_nodes.keys())

    for a in all_a:
        vector = []
        for other_a in all_a:
            if a != other_a:
                pair = tuple(sorted([a, other_a]))
                vector.append(co_citation_counts.get(pair, 0))
        a_co_citation_vectors[a] = vector

    return {
        'n_b_with_multiple_references': sum(1 for refs in b_references.values() if len(refs) > 1),
        'mean_references_per_b': round(np.mean([len(refs) for refs in b_references.values()]), 2),

        'top_co_cited_pairs': [
            {
                'a1': pair[0],
                'a2': pair[1],
                'a1_heading': a_nodes[pair[0]]['heading'],
                'a2_heading': a_nodes[pair[1]]['heading'],
                'co_citation_count': count
            }
            for pair, count in top_pairs
        ],

        'most_co_cited_a': [
            {
                'folio': f,
                'heading': a_nodes[f]['heading'],
                'total_co_citations': count
            }
            for f, count in a_co_citation_total.most_common(10)
        ]
    }


# =============================================================================
# POSITIONAL ANALYSIS
# =============================================================================

def positional_analysis(graph: Dict, a_entries: Dict, b_entries: Dict) -> Dict:
    """
    Analyze positional/sequential patterns in references.

    Questions:
    - Do early B entries reference early A entries?
    - Is there sequential structure in referencing?
    """
    edges = graph['edges']

    # Sort folios by their numeric part
    def folio_sort_key(f):
        # Extract numeric part: f1r -> 1, f10v -> 10
        import re
        match = re.search(r'(\d+)', f)
        return int(match.group(1)) if match else 0

    a_folios_sorted = sorted(a_entries.keys(), key=folio_sort_key)
    b_folios_sorted = sorted(b_entries.keys(), key=folio_sort_key)

    # Assign positions
    a_positions = {f: i for i, f in enumerate(a_folios_sorted)}
    b_positions = {f: i for i, f in enumerate(b_folios_sorted)}

    # Compute position correlation
    b_pos = []
    a_pos = []
    for edge in edges:
        if edge['source'] in b_positions and edge['target'] in a_positions:
            b_pos.append(b_positions[edge['source']])
            a_pos.append(a_positions[edge['target']])

    if len(b_pos) > 10:
        from scipy.stats import spearmanr
        correlation, p_value = spearmanr(b_pos, a_pos)
    else:
        correlation, p_value = 0.0, 1.0

    # Analyze by B thirds
    n_b = len(b_folios_sorted)
    third = n_b // 3
    early_b = set(b_folios_sorted[:third])
    middle_b = set(b_folios_sorted[third:2*third])
    late_b = set(b_folios_sorted[2*third:])

    n_a = len(a_folios_sorted)
    a_third = n_a // 3
    early_a = set(a_folios_sorted[:a_third])
    middle_a = set(a_folios_sorted[a_third:2*a_third])
    late_a = set(a_folios_sorted[2*a_third:])

    # Count references by position
    ref_matrix = {
        'early_b_to_early_a': 0,
        'early_b_to_middle_a': 0,
        'early_b_to_late_a': 0,
        'middle_b_to_early_a': 0,
        'middle_b_to_middle_a': 0,
        'middle_b_to_late_a': 0,
        'late_b_to_early_a': 0,
        'late_b_to_middle_a': 0,
        'late_b_to_late_a': 0,
    }

    for edge in edges:
        b = edge['source']
        a = edge['target']

        b_pos_cat = 'early' if b in early_b else ('middle' if b in middle_b else 'late')
        a_pos_cat = 'early' if a in early_a else ('middle' if a in middle_a else 'late')

        key = f'{b_pos_cat}_b_to_{a_pos_cat}_a'
        ref_matrix[key] += 1

    return {
        'position_correlation': {
            'spearman_r': round(correlation, 4),
            'p_value': p_value,
            'interpretation': 'Sequential pattern' if p_value < 0.05 else 'No sequential pattern'
        },

        'reference_by_position': ref_matrix,

        'interpretation': (
            'SEQUENTIAL' if p_value < 0.05 and correlation > 0.3 else
            'REVERSE_SEQUENTIAL' if p_value < 0.05 and correlation < -0.3 else
            'DISTRIBUTED'
        )
    }


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_graphml(graph: Dict, filepath: str):
    """Export graph in GraphML format for visualization tools."""

    root = ET.Element('graphml')
    root.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')

    # Define attributes
    for key, attr_for, attr_name, attr_type in [
        ('type', 'node', 'type', 'string'),
        ('word_count', 'node', 'word_count', 'int'),
        ('heading', 'node', 'heading', 'string'),
        ('section', 'node', 'section', 'string'),
        ('count', 'edge', 'count', 'int'),
        ('heading_word', 'edge', 'heading_word', 'string'),
    ]:
        key_elem = ET.SubElement(root, 'key')
        key_elem.set('id', key)
        key_elem.set('for', attr_for)
        key_elem.set('attr.name', attr_name)
        key_elem.set('attr.type', attr_type)

    # Create graph element
    graph_elem = ET.SubElement(root, 'graph')
    graph_elem.set('id', 'reference_graph')
    graph_elem.set('edgedefault', 'directed')

    # Add A nodes
    for folio, data in graph['nodes']['a_nodes'].items():
        node = ET.SubElement(graph_elem, 'node')
        node.set('id', f'A_{folio}')

        for key, value in [
            ('type', 'A'),
            ('word_count', str(data['word_count'])),
            ('heading', data['heading']),
            ('section', data.get('section', 'H'))
        ]:
            data_elem = ET.SubElement(node, 'data')
            data_elem.set('key', key)
            data_elem.text = value

    # Add B nodes
    for folio, data in graph['nodes']['b_nodes'].items():
        node = ET.SubElement(graph_elem, 'node')
        node.set('id', f'B_{folio}')

        for key, value in [
            ('type', 'B'),
            ('word_count', str(data['word_count'])),
            ('section', data.get('section', ''))
        ]:
            data_elem = ET.SubElement(node, 'data')
            data_elem.set('key', key)
            data_elem.text = value

    # Add edges
    for i, edge in enumerate(graph['edges']):
        edge_elem = ET.SubElement(graph_elem, 'edge')
        edge_elem.set('id', f'e{i}')
        edge_elem.set('source', f'B_{edge["source"]}')
        edge_elem.set('target', f'A_{edge["target"]}')

        for key, value in [
            ('count', str(edge['count'])),
            ('heading_word', edge['heading_word'])
        ]:
            data_elem = ET.SubElement(edge_elem, 'data')
            data_elem.set('key', key)
            data_elem.text = value

    # Write file
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)


def export_edge_list(graph: Dict, filepath: str):
    """Export edge list as CSV."""
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['source_b', 'target_a', 'heading_word', 'count'])

        for edge in graph['edges']:
            writer.writerow([
                edge['source'],
                edge['target'],
                edge['heading_word'],
                edge['count']
            ])


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Phase 18, Task 4: B->A Reference Graph Analysis")
    print("=" * 70)

    # Load corpus
    print("\n[1/7] Loading corpus...")
    corpus = load_corpus()
    print(f"  Loaded {len(corpus)} word tokens")

    # Segment by Currier
    print("\n[2/7] Segmenting by Currier...")
    a_entries = segment_by_folio(corpus, 'A')
    b_entries = segment_by_folio(corpus, 'B')
    print(f"  Currier A: {len(a_entries)} entries")
    print(f"  Currier B: {len(b_entries)} entries")

    # Extract headings
    print("\n[3/7] Extracting A headings...")
    a_headings = extract_headings(a_entries)
    print(f"  Found {len(a_headings)} heading candidates")

    # Build graph
    print("\n[4/7] Building reference graph...")
    graph = build_reference_graph(a_entries, b_entries, a_headings)
    print(f"  Nodes: {len(graph['nodes']['a_nodes'])} A + {len(graph['nodes']['b_nodes'])} B")
    print(f"  Edges: {len(graph['edges'])}")

    # Compute statistics
    print("\n[5/7] Computing graph statistics...")
    stats = compute_graph_statistics(graph)

    # Co-citation analysis
    print("\n[6/7] Running co-citation analysis...")
    co_citation = co_citation_analysis(graph)

    # Positional analysis
    print("\n[7/7] Running positional analysis...")
    positional = positional_analysis(graph, a_entries, b_entries)

    # Compile results
    results = {
        'metadata': {
            'title': 'B->A Reference Graph Analysis',
            'phase': 'Phase 18, Task 4',
            'date': datetime.now().isoformat(),
            'purpose': 'Analyze semantic dependency between Currier B and A entries'
        },

        'graph_statistics': stats,
        'co_citation_analysis': co_citation,
        'positional_analysis': positional,

        'key_findings': {
            'total_edges': len(graph['edges']),
            'a_entries_referenced': len(graph['nodes']['a_nodes']) - stats['isolated_nodes']['a_isolated_count'],
            'a_entries_isolated': stats['isolated_nodes']['a_isolated_count'],
            'b_entries_referencing': len(graph['nodes']['b_nodes']) - stats['isolated_nodes']['b_isolated_count'],
            'mean_a_in_degree': stats['a_node_in_degree']['mean'],
            'mean_b_out_degree': stats['b_node_out_degree']['mean'],
            'positional_pattern': positional['interpretation']
        }
    }

    # Save JSON report
    with open('reference_graph_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Export GraphML
    print("\nExporting graph files...")
    export_graphml(graph, 'reference_graph.graphml')
    export_edge_list(graph, 'reference_graph_edges.csv')

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nGraph Structure:")
    print(f"  A nodes: {stats['basic_counts']['n_a_nodes']}")
    print(f"  B nodes: {stats['basic_counts']['n_b_nodes']}")
    print(f"  Edges (B->A references): {stats['basic_counts']['n_edges']}")
    print(f"  Density: {stats['basic_counts']['density']}")

    print(f"\nA Entry In-Degree (times referenced by B):")
    print(f"  Mean: {stats['a_node_in_degree']['mean']}")
    print(f"  Max: {stats['a_node_in_degree']['max']}")
    print(f"  Isolated: {stats['isolated_nodes']['a_isolated_count']}")

    print(f"\nB Entry Out-Degree (A entries referenced):")
    print(f"  Mean: {stats['b_node_out_degree']['mean']}")
    print(f"  Max: {stats['b_node_out_degree']['max']}")
    print(f"  Isolated: {stats['isolated_nodes']['b_isolated_count']}")

    print(f"\nMost Referenced A Entries:")
    for item in stats['most_referenced_a'][:5]:
        print(f"  {item['folio']}: {item['in_degree']} refs (heading: {item['heading']})")

    print(f"\nCo-Citation Analysis:")
    print(f"  B entries with multiple references: {co_citation['n_b_with_multiple_references']}")
    print(f"  Mean refs per B: {co_citation['mean_references_per_b']}")

    print(f"\nPositional Analysis:")
    print(f"  Pattern: {positional['interpretation']}")
    print(f"  Spearman r: {positional['position_correlation']['spearman_r']}")

    print(f"\nFiles saved:")
    print(f"  - reference_graph_analysis_report.json")
    print(f"  - reference_graph.graphml")
    print(f"  - reference_graph_edges.csv")

    return results


if __name__ == '__main__':
    main()
