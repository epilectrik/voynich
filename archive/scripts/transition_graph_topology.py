"""
TRANSITION GRAPH TOPOLOGY ANALYSIS

Global structural analysis of the grammar as a directed graph.

Questions:
- What's the diameter (max distance between any two states)?
- Are there strongly connected components (zones you can't leave)?
- Are there articulation points / bottlenecks (must-pass nodes)?
- What's the clustering coefficient?
- Are there hub nodes?

This reveals the SHAPE of the allowed state space.
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("WARNING: networkx not installed. Some analyses will be skipped.")

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR_FILE = BASE / "results" / "canonical_grammar.json"

def load_grammar_classes():
    """Load the 49 grammar classes."""
    with open(GRAMMAR_FILE, 'r', encoding='utf-8') as f:
        grammar = json.load(f)

    # Format: {"terminals": {"count": N, "list": [{"id": X, "symbol": "...", "role": "..."}]}}
    token_to_class = {}
    class_names = set()

    terminals = grammar.get('terminals', {}).get('list', [])
    for term in terminals:
        symbol = term.get('symbol')
        role = term.get('role')
        if symbol and role:
            token_to_class[symbol] = role
            class_names.add(role)

    return token_to_class, list(class_names)

def load_transitions():
    """Load class-level transitions from corpus."""
    token_to_class, class_names = load_grammar_classes()

    transitions = Counter()

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        prev_token = None
        prev_folio = None

        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']

            # Don't count cross-folio transitions
            if folio == prev_folio and prev_token:
                prev_cls = token_to_class.get(prev_token)
                curr_cls = token_to_class.get(token)
                if prev_cls and curr_cls:
                    transitions[(prev_cls, curr_cls)] += 1

            prev_token = token
            prev_folio = folio

    return transitions, class_names

def build_graph(transitions, class_names):
    """Build directed graph from transitions."""
    if not HAS_NETWORKX:
        return None

    G = nx.DiGraph()
    G.add_nodes_from(class_names)

    for (c1, c2), weight in transitions.items():
        G.add_edge(c1, c2, weight=weight)

    return G

def analyze_topology(G, transitions, class_names):
    """Analyze graph topology."""
    print("="*70)
    print("TRANSITION GRAPH TOPOLOGY ANALYSIS")
    print("="*70)

    if not HAS_NETWORKX:
        print("\nnetworkx not available. Manual analysis only.")
        return

    print(f"\nGraph statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.4f}")

    # Strongly connected components
    print("\n" + "-"*70)
    print("STRONGLY CONNECTED COMPONENTS")
    print("-"*70)

    sccs = list(nx.strongly_connected_components(G))
    print(f"\nNumber of SCCs: {len(sccs)}")

    scc_sizes = sorted([len(scc) for scc in sccs], reverse=True)
    print(f"SCC sizes: {scc_sizes[:10]}{'...' if len(scc_sizes) > 10 else ''}")

    largest_scc = max(sccs, key=len)
    print(f"\nLargest SCC: {len(largest_scc)} nodes ({100*len(largest_scc)/len(class_names):.1f}%)")

    if len(largest_scc) < len(class_names):
        isolated = set(class_names) - largest_scc
        print(f"Nodes outside largest SCC: {len(isolated)}")
        for node in list(isolated)[:10]:
            print(f"  {node}")

    # Weakly connected components
    wccs = list(nx.weakly_connected_components(G))
    print(f"\nWeakly connected components: {len(wccs)}")
    if len(wccs) > 1:
        print("  -> Graph is NOT fully connected!")

    # Diameter (on largest SCC)
    print("\n" + "-"*70)
    print("GRAPH DIAMETER AND DISTANCES")
    print("-"*70)

    subgraph = G.subgraph(largest_scc)
    if nx.is_strongly_connected(subgraph):
        diameter = nx.diameter(subgraph)
        avg_path = nx.average_shortest_path_length(subgraph)
        print(f"\nDiameter of largest SCC: {diameter}")
        print(f"Average path length: {avg_path:.2f}")
    else:
        print("\nLargest SCC is not strongly connected (shouldn't happen)")

    # Hub analysis (in-degree and out-degree)
    print("\n" + "-"*70)
    print("HUB ANALYSIS")
    print("-"*70)

    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())

    print(f"\nTop nodes by IN-DEGREE (many transitions TO this node):")
    for node, deg in sorted(in_deg.items(), key=lambda x: -x[1])[:10]:
        print(f"  {node}: {deg}")

    print(f"\nTop nodes by OUT-DEGREE (many transitions FROM this node):")
    for node, deg in sorted(out_deg.items(), key=lambda x: -x[1])[:10]:
        print(f"  {node}: {deg}")

    # Betweenness centrality (bottlenecks)
    print("\n" + "-"*70)
    print("BOTTLENECK ANALYSIS (Betweenness Centrality)")
    print("-"*70)

    betweenness = nx.betweenness_centrality(G)
    print(f"\nTop nodes by betweenness (paths pass through them):")
    for node, bc in sorted(betweenness.items(), key=lambda x: -x[1])[:10]:
        print(f"  {node}: {bc:.4f}")

    # PageRank
    print("\n" + "-"*70)
    print("PAGERANK ANALYSIS")
    print("-"*70)

    pagerank = nx.pagerank(G)
    print(f"\nTop nodes by PageRank:")
    for node, pr in sorted(pagerank.items(), key=lambda x: -x[1])[:10]:
        print(f"  {node}: {pr:.4f}")

    # Clustering coefficient
    print("\n" + "-"*70)
    print("CLUSTERING ANALYSIS")
    print("-"*70)

    # For directed graphs, use transitivity
    transitivity = nx.transitivity(G)
    print(f"\nGraph transitivity: {transitivity:.4f}")

    # Reciprocity
    reciprocity = nx.reciprocity(G)
    print(f"Reciprocity (A->B implies B->A): {reciprocity:.4f}")

    # Self-loops
    self_loops = list(nx.selfloop_edges(G))
    print(f"Self-loops: {len(self_loops)}")

    # Check for articulation points (in undirected version)
    print("\n" + "-"*70)
    print("ARTICULATION POINTS (must-pass nodes)")
    print("-"*70)

    G_undirected = G.to_undirected()
    articulation = list(nx.articulation_points(G_undirected))
    print(f"\nArticulation points: {len(articulation)}")
    if articulation:
        for node in articulation[:10]:
            print(f"  {node}")

    # Community detection (for structure)
    print("\n" + "-"*70)
    print("COMMUNITY STRUCTURE")
    print("-"*70)

    try:
        communities = list(nx.community.greedy_modularity_communities(G_undirected))
        print(f"\nDetected communities: {len(communities)}")
        for i, comm in enumerate(communities[:5]):
            print(f"  Community {i+1}: {len(comm)} nodes")
            print(f"    Members: {list(comm)[:5]}{'...' if len(comm) > 5 else ''}")
    except Exception as e:
        print(f"Community detection failed: {e}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\nGraph structure:")
    print(f"  - {len(sccs)} strongly connected components")
    print(f"  - Largest SCC contains {100*len(largest_scc)/len(class_names):.1f}% of nodes")
    print(f"  - Diameter: {diameter if 'diameter' in dir() else 'N/A'}")
    print(f"  - Transitivity: {transitivity:.4f}")
    print(f"  - Reciprocity: {reciprocity:.4f}")

    print(f"\nKey nodes:")
    top_betweenness = sorted(betweenness.items(), key=lambda x: -x[1])[:3]
    print(f"  - Bottlenecks: {', '.join([n for n, _ in top_betweenness])}")
    top_in = sorted(in_deg.items(), key=lambda x: -x[1])[:3]
    print(f"  - In-hubs: {', '.join([n for n, _ in top_in])}")
    top_out = sorted(out_deg.items(), key=lambda x: -x[1])[:3]
    print(f"  - Out-hubs: {', '.join([n for n, _ in top_out])}")

def main():
    transitions, class_names = load_transitions()
    print(f"Loaded {len(transitions)} unique transitions across {len(class_names)} classes")

    G = build_graph(transitions, class_names)
    if G:
        analyze_topology(G, transitions, class_names)
    else:
        print("Cannot perform graph analysis without networkx")
        print("Install with: pip install networkx")

if __name__ == '__main__':
    main()
