#!/usr/bin/env python3
"""
PHASE 2: WATER_STANDARD STRUCTURAL CLUSTERING

Question: Within WATER_STANDARD folios, do registry-internal MIDDLEs exhibit
non-random clustering consistent with distinct material input subclasses?

Method:
1. Build co-occurrence graph of registry-internal MIDDLEs in WATER_STANDARD A folios
2. Apply community detection (Louvain-like greedy modularity optimization)
3. Compute modularity and cluster stability via bootstrap
4. AFTER clustering: overlay Brunschwig material subclass labels as DIAGNOSTIC

Key constraints:
- Same REGIME, same product class, same execution affordances
- Any structure must come from Currier A's registry function
- Diagnostic overlay is NOT used in cluster formation
"""

import csv
import json
from collections import defaultdict, Counter
import random
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# WATER_STANDARD material sources (from Brunschwig)
MATERIAL_SOURCES = {
    'herb': 0.863,           # 86.3%
    'hot_flower': 0.055,     # 5.5%
    'moderate_herb': 0.048,  # 4.8%
    'moist_root': 0.022,     # 2.2%
    'leaf': 0.012            # 1.2%
}

# Minimum co-occurrence threshold
MIN_COOCCURRENCE = 2

# Bootstrap iterations
N_BOOTSTRAP = 100

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# ============================================================
# DATA LOADING
# ============================================================

def load_2track_classification():
    """Load registry-internal vs pipeline-participating classification."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles']), set(data['a_shared_middles'])

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load all MIDDLEs per folio from transcript."""
    folio_middles = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue
            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)

    return folio_middles

# ============================================================
# GRAPH BUILDING
# ============================================================

def build_cooccurrence_graph(folios, folio_middles, registry_internal):
    """
    Build co-occurrence graph of registry-internal MIDDLEs.

    Nodes: registry-internal MIDDLEs that appear in WATER_STANDARD folios
    Edges: weighted by co-occurrence count (how many folios have both MIDDLEs)
    """
    # Get registry-internal MIDDLEs per folio
    folio_reg_middles = {}
    for folio in folios:
        middles = folio_middles.get(folio, [])
        reg_middles = set(m for m in middles if m in registry_internal)
        if reg_middles:
            folio_reg_middles[folio] = reg_middles

    # Build co-occurrence counts
    cooccurrence = Counter()
    for folio, reg_middles in folio_reg_middles.items():
        reg_list = list(reg_middles)
        for i in range(len(reg_list)):
            for j in range(i + 1, len(reg_list)):
                m1, m2 = sorted([reg_list[i], reg_list[j]])
                cooccurrence[(m1, m2)] += 1

    # Build adjacency list (only edges with sufficient co-occurrence)
    adjacency = defaultdict(lambda: defaultdict(int))
    for (m1, m2), count in cooccurrence.items():
        if count >= MIN_COOCCURRENCE:
            adjacency[m1][m2] = count
            adjacency[m2][m1] = count

    # Get all nodes (MIDDLEs with at least one edge)
    nodes = set(adjacency.keys())

    # Also track folio-level data for each MIDDLE
    middle_folios = defaultdict(set)
    for folio, reg_middles in folio_reg_middles.items():
        for m in reg_middles:
            middle_folios[m].add(folio)

    return adjacency, nodes, middle_folios, folio_reg_middles

# ============================================================
# COMMUNITY DETECTION (Greedy Modularity Optimization)
# ============================================================

def compute_modularity(adjacency, communities):
    """
    Compute modularity Q of the current partition.
    Q = (1/2m) * sum_ij[(A_ij - k_i*k_j/2m) * delta(c_i, c_j)]
    """
    # Total edge weight
    m = sum(sum(neighbors.values()) for neighbors in adjacency.values()) / 2
    if m == 0:
        return 0

    # Degree of each node
    degrees = {node: sum(neighbors.values()) for node, neighbors in adjacency.items()}

    Q = 0
    for node1 in adjacency:
        c1 = communities.get(node1)
        for node2 in adjacency:
            c2 = communities.get(node2)
            if c1 == c2:  # Same community
                A_ij = adjacency[node1].get(node2, 0)
                k_i = degrees.get(node1, 0)
                k_j = degrees.get(node2, 0)
                Q += A_ij - (k_i * k_j) / (2 * m)

    return Q / (2 * m)

def greedy_modularity_communities(adjacency, nodes):
    """
    Greedy modularity optimization (simplified Louvain-like algorithm).
    Each node starts in its own community, then greedily merge communities
    that increase modularity.
    """
    if not nodes:
        return {}, 0

    # Initialize: each node in its own community
    communities = {node: i for i, node in enumerate(sorted(nodes))}
    n_communities = len(nodes)

    # Compute initial modularity
    best_Q = compute_modularity(adjacency, communities)

    # Greedy optimization
    improved = True
    max_iterations = 100
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for node in sorted(nodes):
            current_comm = communities[node]

            # Try moving to each neighbor's community
            best_move = None
            best_delta = 0

            for neighbor in adjacency.get(node, {}):
                neighbor_comm = communities[neighbor]
                if neighbor_comm != current_comm:
                    # Try this move
                    communities[node] = neighbor_comm
                    new_Q = compute_modularity(adjacency, communities)
                    delta = new_Q - best_Q

                    if delta > best_delta:
                        best_delta = delta
                        best_move = neighbor_comm

                    communities[node] = current_comm  # Revert

            if best_move is not None and best_delta > 0.001:  # Small threshold
                communities[node] = best_move
                best_Q += best_delta
                improved = True

    # Renumber communities to be contiguous
    unique_comms = sorted(set(communities.values()))
    comm_map = {old: new for new, old in enumerate(unique_comms)}
    communities = {node: comm_map[c] for node, c in communities.items()}

    return communities, best_Q

# ============================================================
# BOOTSTRAP STABILITY
# ============================================================

def bootstrap_stability(folios, folio_middles, registry_internal, n_iterations=N_BOOTSTRAP):
    """
    Test cluster stability via bootstrap resampling.
    For each bootstrap sample, re-cluster and measure:
    1. Number of clusters found
    2. Modularity score
    3. Node-pair co-clustering frequency (adjusted Rand index proxy)
    """
    results = []
    pair_cocluster = Counter()  # How often each pair is in the same cluster
    pair_count = Counter()  # How often each pair appears

    for i in range(n_iterations):
        # Bootstrap sample of folios
        sample = random.choices(folios, k=len(folios))

        # Build graph from sample
        adj, nodes, _, _ = build_cooccurrence_graph(sample, folio_middles, registry_internal)

        if len(nodes) < 3:
            continue

        # Cluster
        communities, Q = greedy_modularity_communities(adj, nodes)
        n_clusters = len(set(communities.values()))

        results.append({
            'n_clusters': n_clusters,
            'modularity': Q,
            'n_nodes': len(nodes)
        })

        # Track pair co-clustering
        for n1 in communities:
            for n2 in communities:
                if n1 < n2:
                    pair_count[(n1, n2)] += 1
                    if communities[n1] == communities[n2]:
                        pair_cocluster[(n1, n2)] += 1

    # Compute stability metrics
    if results:
        mean_clusters = sum(r['n_clusters'] for r in results) / len(results)
        std_clusters = (sum((r['n_clusters'] - mean_clusters)**2 for r in results) / len(results)) ** 0.5
        mean_Q = sum(r['modularity'] for r in results) / len(results)
        std_Q = (sum((r['modularity'] - mean_Q)**2 for r in results) / len(results)) ** 0.5

        # Pair stability
        pair_stability = {}
        for pair, count in pair_count.items():
            pair_stability[pair] = pair_cocluster[pair] / count

        mean_pair_stability = sum(pair_stability.values()) / len(pair_stability) if pair_stability else 0
    else:
        mean_clusters = std_clusters = mean_Q = std_Q = mean_pair_stability = 0
        pair_stability = {}

    return {
        'n_iterations': len(results),
        'mean_clusters': mean_clusters,
        'std_clusters': std_clusters,
        'mean_modularity': mean_Q,
        'std_modularity': std_Q,
        'mean_pair_stability': mean_pair_stability,
        'pair_stability': pair_stability
    }

# ============================================================
# DIAGNOSTIC OVERLAY (NOT USED IN CLUSTERING)
# ============================================================

def diagnostic_overlay(communities, middle_folios, folio_classifications, folios):
    """
    AFTER clustering is complete, overlay Brunschwig material source
    distributions as a DIAGNOSTIC check.

    This does NOT influence clustering - it's purely for interpretation.
    """
    # For each cluster, count how many folios each MIDDLE appears in
    # Then weight by the material source distribution for WATER_STANDARD

    cluster_stats = defaultdict(lambda: {
        'n_middles': 0,
        'total_folio_appearances': 0,
        'middles': []
    })

    for middle, cluster in communities.items():
        folios_with = middle_folios.get(middle, set())
        # Filter to WATER_STANDARD folios
        ws_folios = [f for f in folios_with if folio_classifications.get(f) == 'WATER_STANDARD']

        cluster_stats[cluster]['n_middles'] += 1
        cluster_stats[cluster]['total_folio_appearances'] += len(ws_folios)
        cluster_stats[cluster]['middles'].append({
            'middle': middle,
            'n_folios': len(ws_folios)
        })

    # Sort MIDDLEs within each cluster by folio count
    for cluster in cluster_stats:
        cluster_stats[cluster]['middles'].sort(key=lambda x: -x['n_folios'])

    return dict(cluster_stats)

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PHASE 2: WATER_STANDARD STRUCTURAL CLUSTERING")
    print("=" * 70)
    print()
    print("Question: Do registry-internal MIDDLEs exhibit non-random clustering")
    print("          within WATER_STANDARD folios?")
    print()
    print("Method: Co-occurrence graph + greedy modularity optimization")
    print()

    # Load data
    print("Loading data...")
    registry_internal, pipeline = load_2track_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    # Filter to WATER_STANDARD folios
    ws_folios = [f for f, ptype in folio_classifications.items() if ptype == 'WATER_STANDARD']

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print(f"  WATER_STANDARD folios: {len(ws_folios)}")
    print()

    # Build co-occurrence graph
    print("=" * 70)
    print("BUILDING CO-OCCURRENCE GRAPH")
    print("=" * 70)
    print()

    adjacency, nodes, middle_folios, folio_reg_middles = build_cooccurrence_graph(
        ws_folios, folio_middles, registry_internal
    )

    # Graph statistics
    n_edges = sum(len(neighbors) for neighbors in adjacency.values()) // 2
    total_weight = sum(sum(neighbors.values()) for neighbors in adjacency.values()) // 2

    print(f"  Nodes (MIDDLEs with edges): {len(nodes)}")
    print(f"  Edges (co-occurrence >= {MIN_COOCCURRENCE}): {n_edges}")
    print(f"  Total edge weight: {total_weight}")
    print()

    # How many folios have registry-internal MIDDLEs?
    n_folios_with_reg = len(folio_reg_middles)
    print(f"  Folios with registry-internal MIDDLEs: {n_folios_with_reg}")
    print()

    if len(nodes) < 5:
        print("INSUFFICIENT DATA: Not enough connected registry-internal MIDDLEs")
        print("for meaningful clustering analysis.")
        return

    # Community detection
    print("=" * 70)
    print("COMMUNITY DETECTION")
    print("=" * 70)
    print()

    communities, modularity = greedy_modularity_communities(adjacency, nodes)
    n_clusters = len(set(communities.values()))

    print(f"  Clusters found: {n_clusters}")
    print(f"  Modularity Q: {modularity:.3f}")
    print()

    # Interpret modularity
    if modularity < 0.1:
        mod_interpretation = "WEAK (near-random structure)"
    elif modularity < 0.3:
        mod_interpretation = "MODERATE (some structure)"
    elif modularity < 0.5:
        mod_interpretation = "GOOD (clear community structure)"
    else:
        mod_interpretation = "STRONG (highly modular)"

    print(f"  Interpretation: {mod_interpretation}")
    print()

    # Show clusters
    print("=" * 70)
    print("CLUSTER COMPOSITION")
    print("=" * 70)
    print()

    cluster_members = defaultdict(list)
    for middle, cluster in communities.items():
        n_folios = len(middle_folios.get(middle, set()))
        cluster_members[cluster].append((middle, n_folios))

    for cluster in sorted(cluster_members.keys()):
        members = cluster_members[cluster]
        members.sort(key=lambda x: -x[1])
        print(f"Cluster {cluster} (n={len(members)} MIDDLEs):")
        for m, n in members[:10]:
            print(f"    {m}: {n} folios")
        if len(members) > 10:
            print(f"    ... and {len(members) - 10} more")
        print()

    # Bootstrap stability
    print("=" * 70)
    print("BOOTSTRAP STABILITY ANALYSIS")
    print("=" * 70)
    print()

    print(f"Running {N_BOOTSTRAP} bootstrap iterations...")
    stability = bootstrap_stability(ws_folios, folio_middles, registry_internal)

    print(f"  Mean clusters: {stability['mean_clusters']:.1f} (+/- {stability['std_clusters']:.1f})")
    print(f"  Mean modularity: {stability['mean_modularity']:.3f} (+/- {stability['std_modularity']:.3f})")
    print(f"  Mean pair stability: {stability['mean_pair_stability']:.3f}")
    print()

    # Stability interpretation
    if stability['mean_pair_stability'] > 0.8:
        stab_interpretation = "HIGH (clusters are reproducible)"
    elif stability['mean_pair_stability'] > 0.6:
        stab_interpretation = "MODERATE (clusters partially stable)"
    elif stability['mean_pair_stability'] > 0.4:
        stab_interpretation = "LOW (clusters unstable)"
    else:
        stab_interpretation = "VERY LOW (near-random clustering)"

    print(f"  Stability interpretation: {stab_interpretation}")
    print()

    # Diagnostic overlay (AFTER clustering)
    print("=" * 70)
    print("DIAGNOSTIC OVERLAY (NOT USED IN CLUSTERING)")
    print("=" * 70)
    print()

    cluster_stats = diagnostic_overlay(communities, middle_folios, folio_classifications, ws_folios)

    print("Cluster statistics:")
    for cluster in sorted(cluster_stats.keys()):
        stats = cluster_stats[cluster]
        print(f"  Cluster {cluster}: {stats['n_middles']} MIDDLEs, {stats['total_folio_appearances']} total appearances")
    print()

    print("NOTE: Brunschwig WATER_STANDARD material distribution:")
    for source, pct in sorted(MATERIAL_SOURCES.items(), key=lambda x: -x[1]):
        print(f"  {source}: {pct:.1%}")
    print()
    print("Without folio-level material labels, we cannot compute alignment.")
    print("Clusters represent co-occurrence structure, not confirmed material categories.")
    print()

    # Save results
    output = {
        'phase': 'WATER_STANDARD_CLUSTERING',
        'date': '2026-01-20',
        'graph': {
            'n_nodes': len(nodes),
            'n_edges': n_edges,
            'total_weight': total_weight,
            'min_cooccurrence': MIN_COOCCURRENCE
        },
        'clustering': {
            'n_clusters': n_clusters,
            'modularity': modularity,
            'modularity_interpretation': mod_interpretation,
            'communities': {m: int(c) for m, c in communities.items()}
        },
        'stability': {
            'n_bootstrap': stability['n_iterations'],
            'mean_clusters': stability['mean_clusters'],
            'std_clusters': stability['std_clusters'],
            'mean_modularity': stability['mean_modularity'],
            'std_modularity': stability['std_modularity'],
            'mean_pair_stability': stability['mean_pair_stability'],
            'interpretation': stab_interpretation
        },
        'cluster_stats': {
            str(c): {
                'n_middles': stats['n_middles'],
                'total_appearances': stats['total_folio_appearances'],
                'top_middles': [m['middle'] for m in stats['middles'][:5]]
            }
            for c, stats in cluster_stats.items()
        }
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/water_standard_clustering.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Final interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if modularity >= 0.3 and stability['mean_pair_stability'] >= 0.6:
        print("POSITIVE: Registry-internal MIDDLEs show stable clustering structure")
        print("within WATER_STANDARD.")
        print()
        print("This suggests non-random organization of registry-internal vocabulary,")
        print("consistent with (but not proving) material subclass distinctions.")
    elif modularity >= 0.1 and stability['mean_pair_stability'] >= 0.4:
        print("WEAK POSITIVE: Some clustering structure exists but is not highly stable.")
        print()
        print("Registry-internal vocabulary shows partial organization that may reflect")
        print("material distinctions, but evidence is not strong.")
    else:
        print("NULL: No stable clustering structure found.")
        print()
        print("Registry-internal vocabulary does not cluster by co-occurrence within")
        print("WATER_STANDARD. This suggests distinctions are either:")
        print("  - Atomic (per-entry, not categorical)")
        print("  - Orthogonal to material taxonomy")
        print("  - Below the resolution of this test")

    print()
    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/water_standard_clustering.json")

if __name__ == '__main__':
    main()
