#!/usr/bin/env python3
"""
Phase 15: STATE-C Deep Structure Analysis
==========================================

Situation: Phase 14 revealed the Voynich is fundamentally a monostate system.
STATE-C is the only essential state - all others are interface buffers.
All execution paths converge to STATE-C.

Goal: Crack open STATE-C. What's inside the black box?

Sub-phases:
- 15A: Internal Topology (clusters, hubs, spokes, bridges)
- 15B: Length-4 Cycle Analysis (dominant cycle structure)
- 15C: Repetition Analysis (the 130x mystery)
- 15D: Vocabulary Structure (frequency, co-occurrence, operator affinity)
- 15E: Minimal Semantic Units (atomicity, primitives)
"""

import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import numpy as np

# ============================================================================
# CORPUS LOADING (reuse from Phase 13)
# ============================================================================

KNOWN_PREFIXES = {'qo', 'da', 'ch', 'sh', 'ok', 'ot', 'sa', 'ct', 'yk', 'yp',
                  'ar', 'ko', 'so', 'ra', 'ta', 'op', 'cf', 'fc', 'pc', 'ts',
                  'al', 'ol', 'or', 'dy', 'od', 'ke', 'am', 'lk', 'ka'}
KNOWN_SUFFIXES = {'aiin', 'ol', 'hy', 'or', 'ar', 'ey', 'edy', 'dy', 'y',
                  'al', 'eey', 'eedy', 'ain', 'in', 'an', 'am', 'o'}

def load_corpus():
    """Load the interlinear transcription corpus."""
    corpus_path = Path("data/transcriptions/interlinear_full_words.txt")
    records = []

    with open(corpus_path, 'r', encoding='utf-8') as f:
        header = None
        for line in f:
            if line.strip():
                parts = line.strip().split('\t')

                if header is None:
                    header = parts
                    continue

                if len(parts) >= 7:
                    # Filter to H (PRIMARY) transcriber only
                    transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                    if transcriber != 'H':
                        continue

                    word = parts[0].strip('"')
                    folio = parts[2].strip('"')
                    language = parts[6].strip('"')

                    if '*' in word or '?' in word:
                        continue

                    records.append({
                        'folio': folio,
                        'word': word,
                        'population': language
                    })
    return records

def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [2, 1]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return word[:2] if len(word) >= 2 else word

def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    for length in [4, 3, 2, 1]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix
    return word[-2:] if len(word) >= 2 else word

def get_middle(word: str) -> str:
    """Extract middle from word."""
    prefix = get_prefix(word)
    suffix = get_suffix(word)

    if len(word) <= len(prefix) + len(suffix):
        return word

    middle = word[len(prefix):-len(suffix)] if suffix else word[len(prefix):]
    return middle if middle else word

def group_by_entry(records: List[Dict]) -> Dict[str, List[str]]:
    """Group tokens by folio (entry)."""
    entries = defaultdict(list)
    for rec in records:
        entries[rec['folio']].append(rec['word'])
    return dict(entries)

# ============================================================================
# RECONSTRUCT STATE-C MEMBERSHIP
# ============================================================================

def reconstruct_states(entries: Dict[str, List[str]]) -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    """
    Reconstruct state assignments using the same clustering as Phase 13.
    Returns (state_to_nodes, node_to_state) mappings.
    """
    # Build transition graph
    edges = defaultdict(lambda: defaultdict(int))
    node_in_degree = Counter()
    node_out_degree = Counter()
    node_self_loops = Counter()
    predecessors = defaultdict(set)
    successors = defaultdict(set)

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        prefixes = [get_prefix(t) for t in tokens]

        for i in range(len(middles) - 1):
            m1, m2 = middles[i], middles[i + 1]
            op = prefixes[i + 1]

            if m1 and m2:
                edges[(m1, m2)][op] += 1
                node_out_degree[m1] += 1
                node_in_degree[m2] += 1
                predecessors[m2].add(m1)
                successors[m1].add(m2)

                if m1 == m2:
                    node_self_loops[m1] += 1

    # Get all unique nodes
    all_nodes = set(node_in_degree.keys()) | set(node_out_degree.keys())

    # Compute behavioral features for each node
    node_features = {}

    for node in all_nodes:
        in_deg = node_in_degree.get(node, 0)
        out_deg = node_out_degree.get(node, 0)
        total_deg = in_deg + out_deg

        if total_deg < 10:  # Skip very rare nodes
            continue

        convergence = in_deg / total_deg if total_deg > 0 else 0
        pred_count = len(predecessors.get(node, set()))
        succ_count = len(successors.get(node, set()))
        stability = node_self_loops.get(node, 0) / out_deg if out_deg > 0 else 0
        asymmetry = (in_deg - out_deg) / total_deg if total_deg > 0 else 0
        hub_score = math.sqrt(in_deg * out_deg) if in_deg > 0 and out_deg > 0 else 0

        node_features[node] = {
            'convergence': convergence,
            'predecessor_count': pred_count,
            'successor_count': succ_count,
            'stability': stability,
            'asymmetry': asymmetry,
            'hub_score': hub_score,
            'in_degree': in_deg,
            'out_degree': out_deg,
            'total_degree': total_deg
        }

    # Build feature vectors
    feature_vectors = []
    node_list = list(node_features.keys())

    for node in node_list:
        f = node_features[node]
        feature_vectors.append([
            f['convergence'],
            f['predecessor_count'] / 100,
            f['successor_count'] / 100,
            f['stability'],
            f['asymmetry'],
            f['hub_score'] / 100
        ])

    feature_vectors = np.array(feature_vectors)

    # Normalize
    if len(feature_vectors) > 0:
        means = np.mean(feature_vectors, axis=0)
        stds = np.std(feature_vectors, axis=0) + 1e-6
        feature_vectors_norm = (feature_vectors - means) / stds
    else:
        feature_vectors_norm = feature_vectors

    # K-means with k=4 (as found in Phase 13)
    random.seed(42)
    np.random.seed(42)

    labels, _ = simple_kmeans(feature_vectors_norm, 4, max_iter=50)

    # Build state assignments
    state_to_nodes = defaultdict(set)
    node_to_state = {}

    for i, node in enumerate(node_list):
        state_name = f"STATE-{chr(65 + labels[i])}"
        state_to_nodes[state_name].add(node)
        node_to_state[node] = state_name

    # Store node features for later use
    return dict(state_to_nodes), node_to_state, node_features, edges

def simple_kmeans(X: np.ndarray, k: int, max_iter: int = 50) -> Tuple[List[int], np.ndarray]:
    """Simple k-means clustering."""
    n = len(X)
    if n == 0:
        return [], np.array([])

    indices = random.sample(range(n), min(k, n))
    centroids = X[indices].copy()

    labels = [0] * n

    for _ in range(max_iter):
        new_labels = []
        for i in range(n):
            distances = [np.linalg.norm(X[i] - c) for c in centroids]
            new_labels.append(np.argmin(distances))

        if new_labels == labels:
            break
        labels = new_labels

        for j in range(k):
            cluster_points = X[[i for i, l in enumerate(labels) if l == j]]
            if len(cluster_points) > 0:
                centroids[j] = np.mean(cluster_points, axis=0)

    return labels, centroids

# ============================================================================
# PHASE 15A: INTERNAL TOPOLOGY
# ============================================================================

def test_15a_internal_topology(state_c_nodes: Set[str], edges: Dict,
                                node_features: Dict, entries: Dict) -> Dict:
    """
    Map the internal structure of STATE-C.
    """
    print("Running Phase 15A: Internal Topology...")

    # Build internal transition matrix (only within STATE-C)
    internal_transitions = defaultdict(lambda: defaultdict(int))
    internal_in_degree = Counter()
    internal_out_degree = Counter()

    for (m1, m2), ops in edges.items():
        if m1 in state_c_nodes and m2 in state_c_nodes:
            total_count = sum(ops.values())
            internal_transitions[m1][m2] = total_count
            internal_out_degree[m1] += total_count
            internal_in_degree[m2] += total_count

    # Check connectivity
    nodes_with_internal_edges = set(internal_in_degree.keys()) | set(internal_out_degree.keys())
    active_state_c = state_c_nodes & nodes_with_internal_edges

    print(f"  STATE-C total nodes: {len(state_c_nodes)}")
    print(f"  Nodes with internal edges: {len(active_state_c)}")

    # Build adjacency for connectivity analysis
    adjacency = defaultdict(set)
    for m1, targets in internal_transitions.items():
        for m2 in targets:
            adjacency[m1].add(m2)
            adjacency[m2].add(m1)  # Treat as undirected for connectivity

    # Check if fully connected (BFS from any node)
    if active_state_c:
        start = next(iter(active_state_c))
        visited = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(adjacency[node] - visited)

        fully_connected = len(visited) >= len(active_state_c) * 0.9  # 90% threshold
    else:
        fully_connected = False

    # Node role classification based on internal connectivity
    hub_nodes = []
    spoke_nodes = []
    bridge_nodes = []

    for node in active_state_c:
        in_deg = internal_in_degree.get(node, 0)
        out_deg = internal_out_degree.get(node, 0)
        total_deg = in_deg + out_deg

        # Hubs: high in AND out degree
        if in_deg > np.percentile(list(internal_in_degree.values()), 75) and \
           out_deg > np.percentile(list(internal_out_degree.values()), 75):
            hub_nodes.append((node, total_deg))
        # Spokes: connect primarily to hubs (lower total degree)
        elif total_deg < np.percentile([internal_in_degree.get(n, 0) + internal_out_degree.get(n, 0)
                                        for n in active_state_c], 50):
            spoke_nodes.append((node, total_deg))
        else:
            bridge_nodes.append((node, total_deg))

    hub_nodes.sort(key=lambda x: -x[1])
    spoke_nodes.sort(key=lambda x: -x[1])
    bridge_nodes.sort(key=lambda x: -x[1])

    # Internal forbidden transitions (pairs that never connect)
    internal_forbidden = []
    for n1 in active_state_c:
        for n2 in active_state_c:
            if n1 != n2:
                # Check if n1 -> n2 never occurs
                if n2 not in internal_transitions.get(n1, {}):
                    # Only count if both nodes are active (have some transitions)
                    if internal_out_degree.get(n1, 0) > 10 and internal_in_degree.get(n2, 0) > 10:
                        internal_forbidden.append((n1, n2))

    # Centrality hierarchy
    centrality_scores = {}
    for node in active_state_c:
        in_deg = internal_in_degree.get(node, 0)
        out_deg = internal_out_degree.get(node, 0)
        # Betweenness-like centrality proxy: geometric mean
        centrality_scores[node] = math.sqrt(in_deg * out_deg) if in_deg > 0 and out_deg > 0 else 0

    centrality_ranking = sorted(centrality_scores.items(), key=lambda x: -x[1])

    # Core within core: top centrality nodes
    core_threshold = np.percentile(list(centrality_scores.values()), 90)
    core_within_core = [node for node, score in centrality_ranking if score >= core_threshold]

    # Internal clustering via simple community detection
    # Use label propagation-like approach
    internal_clusters = detect_internal_clusters(active_state_c, internal_transitions)

    return {
        "metadata": {
            "phase": "15A",
            "title": "STATE-C Internal Topology",
            "timestamp": datetime.now().isoformat()
        },
        "total_nodes": len(state_c_nodes),
        "active_internal_nodes": len(active_state_c),
        "internal_connectivity": {
            "fully_connected": fully_connected,
            "total_internal_edges": sum(internal_out_degree.values()),
            "mean_internal_degree": round(np.mean(list(internal_in_degree.values()) + list(internal_out_degree.values())), 2),
            "internal_clusters": len(internal_clusters),
            "cluster_sizes": {f"cluster_{i}": len(c) for i, c in enumerate(internal_clusters)}
        },
        "node_roles": {
            "hubs": [{"node": n, "degree": d} for n, d in hub_nodes[:10]],
            "hubs_count": len(hub_nodes),
            "spokes": [{"node": n, "degree": d} for n, d in spoke_nodes[:10]],
            "spokes_count": len(spoke_nodes),
            "bridges": [{"node": n, "degree": d} for n, d in bridge_nodes[:10]],
            "bridges_count": len(bridge_nodes)
        },
        "internal_forbidden": {
            "count": len(internal_forbidden),
            "examples": internal_forbidden[:20]
        },
        "centrality_hierarchy": [
            {"rank": i+1, "node": n, "score": round(s, 2)}
            for i, (n, s) in enumerate(centrality_ranking[:15])
        ],
        "CORE_WITHIN_CORE": core_within_core[:10],
        "INTERPRETATION": (
            f"STATE-C has {len(internal_clusters)} internal cluster(s). "
            f"{len(hub_nodes)} hub nodes dominate internal traffic. "
            f"Core within core: {core_within_core[:5]}. "
            f"{'Fully connected' if fully_connected else 'Not fully connected'} internal structure."
        )
    }

def detect_internal_clusters(nodes: Set[str], transitions: Dict) -> List[Set[str]]:
    """Simple clustering based on transition density."""
    if not nodes:
        return []

    # Build undirected adjacency with weights
    adjacency = defaultdict(lambda: defaultdict(int))
    for n1, targets in transitions.items():
        if n1 in nodes:
            for n2, weight in targets.items():
                if n2 in nodes:
                    adjacency[n1][n2] += weight
                    adjacency[n2][n1] += weight

    # Find connected components as baseline clusters
    visited = set()
    clusters = []

    for start in nodes:
        if start not in visited:
            cluster = set()
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    cluster.add(node)
                    queue.extend(set(adjacency[node].keys()) - visited)
            if cluster:
                clusters.append(cluster)

    return clusters

# ============================================================================
# PHASE 15B: LENGTH-4 CYCLE ANALYSIS
# ============================================================================

def test_15b_4cycle_analysis(state_c_nodes: Set[str], edges: Dict,
                              entries: Dict) -> Dict:
    """
    Analyze the dominant 4-cycle structure within STATE-C.
    Optimized version using sampling and early termination.
    """
    print("Running Phase 15B: 4-Cycle Analysis...")

    # Build internal transition graph
    internal_transitions = defaultdict(set)
    internal_weights = defaultdict(lambda: defaultdict(int))

    for (m1, m2), ops in edges.items():
        if m1 in state_c_nodes and m2 in state_c_nodes:
            internal_transitions[m1].add(m2)
            internal_weights[m1][m2] = sum(ops.values())

    # Find cycles using efficient sampling
    four_cycles_set = set()  # Use set for deduplication
    three_cycles_set = set()

    active_nodes = [n for n in state_c_nodes if n in internal_transitions]

    print(f"  Searching for cycles among {len(active_nodes)} active nodes...")

    # Sample top nodes by connectivity for efficiency
    node_connectivity = {n: len(internal_transitions.get(n, set())) for n in active_nodes}
    sorted_nodes = sorted(active_nodes, key=lambda x: -node_connectivity.get(x, 0))
    sample_nodes = sorted_nodes[:30]  # Top 30 most connected

    # Use efficient cycle detection with early termination
    max_cycles = 500  # Cap to prevent explosion

    for n1 in sample_nodes:
        if len(four_cycles_set) >= max_cycles:
            break
        neighbors1 = internal_transitions.get(n1, set())
        for n2 in neighbors1:
            if len(four_cycles_set) >= max_cycles:
                break
            neighbors2 = internal_transitions.get(n2, set())
            for n3 in neighbors2:
                if n3 == n1:
                    continue
                neighbors3 = internal_transitions.get(n3, set())

                # Check for 3-cycle
                if n1 in neighbors3:
                    cycle = tuple(sorted([n1, n2, n3]))
                    three_cycles_set.add(cycle)

                # Check for 4-cycle (limited search)
                if len(four_cycles_set) < max_cycles:
                    for n4 in list(neighbors3)[:20]:  # Limit per node
                        if n4 != n1 and n4 != n2:
                            if n1 in internal_transitions.get(n4, set()):
                                cycle = tuple(sorted([n1, n2, n3, n4]))
                                four_cycles_set.add(cycle)
                                if len(four_cycles_set) >= max_cycles:
                                    break

    four_cycles = [list(c) for c in four_cycles_set]
    three_cycles = [list(c) for c in three_cycles_set]

    print(f"  Found {len(four_cycles)} 4-cycles, {len(three_cycles)} 3-cycles")

    # Node participation in 4-cycles
    node_participation = Counter()
    for cycle in four_cycles:
        for node in cycle:
            node_participation[node] += 1

    # Cycle anchors (nodes in >50% of 4-cycles)
    threshold = len(four_cycles) * 0.5 if four_cycles else 0
    cycle_anchors = [node for node, count in node_participation.items() if count > threshold]

    # Operator patterns in 4-cycles
    operator_sequences = []
    for folio, tokens in list(entries.items())[:200]:  # Sample entries
        middles = [get_middle(t) for t in tokens]
        prefixes = [get_prefix(t) for t in tokens]

        # Look for 4-step sequences within STATE-C
        for i in range(len(middles) - 3):
            if all(m in state_c_nodes for m in middles[i:i+4]):
                ops = prefixes[i+1:i+4]
                operator_sequences.append(tuple(ops))

    op_seq_counts = Counter(operator_sequences)

    # Relationship to quantitative findings
    matches_elemental = len(four_cycles) > 5
    has_3_cycles = len(three_cycles)

    return {
        "metadata": {
            "phase": "15B",
            "title": "Length-4 Cycle Analysis",
            "timestamp": datetime.now().isoformat()
        },
        "total_4_cycles": len(four_cycles),
        "unique_4_cycles": len(set(tuple(sorted(c)) for c in four_cycles)),
        "total_3_cycles": len(three_cycles),
        "node_participation": {
            node: count for node, count in node_participation.most_common(15)
        },
        "cycle_anchors": cycle_anchors[:10],
        "example_4_cycles": four_cycles[:10],
        "example_3_cycles": three_cycles[:10],
        "operator_patterns": {
            "total_sequences_found": len(operator_sequences),
            "most_common_sequences": [
                {"sequence": list(seq), "count": count}
                for seq, count in op_seq_counts.most_common(10)
            ],
            "canonical_sequence": list(op_seq_counts.most_common(1)[0][0]) if op_seq_counts else "NONE"
        },
        "relationship_to_quantitative": {
            "matches_elemental_4": matches_elemental,
            "also_has_3_cycles": has_3_cycles,
            "3_to_4_ratio": round(has_3_cycles / len(four_cycles), 3) if four_cycles else 0
        },
        "INTERPRETATION": (
            f"Found {len(four_cycles)} 4-cycles among STATE-C nodes. "
            f"Cycle anchors: {cycle_anchors[:5]}. "
            f"Also found {len(three_cycles)} 3-cycles (tria prima). "
            f"Most common operator sequence: {list(op_seq_counts.most_common(1)[0][0]) if op_seq_counts else 'N/A'}."
        )
    }

# ============================================================================
# PHASE 15C: REPETITION ANALYSIS
# ============================================================================

def test_15c_repetition_analysis(state_c_nodes: Set[str], node_features: Dict,
                                  entries: Dict, records: List[Dict]) -> Dict:
    """
    Analyze the 130.93x repetition depth mystery.
    """
    print("Running Phase 15C: Repetition Analysis...")

    # Track repetitions per node
    node_repetitions = defaultdict(list)

    # Track by entry type
    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    a_repetitions = []
    b_repetitions = []

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        pop = folio_populations.get(folio, 'U')

        # Count visits to each STATE-C node in this entry
        entry_visits = Counter()
        for m in middles:
            if m in state_c_nodes:
                entry_visits[m] += 1

        # Record repetitions
        for node, count in entry_visits.items():
            if count > 1:  # Only count if repeated
                node_repetitions[node].append(count)
                if pop == 'A':
                    a_repetitions.append(count)
                elif pop == 'B':
                    b_repetitions.append(count)

    # Compute statistics
    all_reps = [c for counts in node_repetitions.values() for c in counts]

    if all_reps:
        mean_rep = np.mean(all_reps)
        median_rep = np.median(all_reps)
        std_rep = np.std(all_reps)
        min_rep = min(all_reps)
        max_rep = max(all_reps)
    else:
        mean_rep = median_rep = std_rep = min_rep = max_rep = 0

    # Distribution shape
    if all_reps:
        # Check for power law vs normal
        log_reps = np.log(np.array(all_reps) + 1)
        skewness = np.mean((log_reps - np.mean(log_reps))**3) / (np.std(log_reps)**3 + 1e-6)

        if abs(skewness) < 0.5:
            dist_shape = "NORMAL"
        elif skewness > 1:
            dist_shape = "RIGHT_SKEWED"
        else:
            dist_shape = "LEFT_SKEWED"

        # Check for bimodality
        hist, edges = np.histogram(all_reps, bins=20)
        local_maxima = sum(1 for i in range(1, len(hist)-1)
                          if hist[i] > hist[i-1] and hist[i] > hist[i+1])
        if local_maxima >= 2:
            dist_shape = "BIMODAL"
    else:
        dist_shape = "INSUFFICIENT_DATA"

    # Repetition by node centrality (using hub_score as proxy)
    hub_reps = []
    spoke_reps = []

    hub_threshold = np.percentile([node_features.get(n, {}).get('hub_score', 0)
                                   for n in state_c_nodes if n in node_features], 75)

    for node in state_c_nodes:
        if node in node_repetitions and node in node_features:
            if node_features[node].get('hub_score', 0) >= hub_threshold:
                hub_reps.extend(node_repetitions[node])
            else:
                spoke_reps.extend(node_repetitions[node])

    # Quantitative interpretation of 130
    # Factorizations of interest
    factorizations = {
        "130 = 2 x 5 x 13": True,
        "130 ~ 128 = 2^7": abs(130.93 - 128) < 5,
        "130 ~ 4 x 32": abs(130.93 - 128) < 5,
        "130 ~ 3 x 43": abs(130.93 - 129) < 3
    }

    # Check if 130 is meaningful or emergent
    meaningful_130 = False
    for desc, matches in factorizations.items():
        if matches and "128" in desc:
            meaningful_130 = True
            break

    # Termination mechanism analysis
    # Check if entries show natural decay patterns
    decay_patterns = []
    for folio, tokens in list(entries.items())[:100]:
        middles = [get_middle(t) for t in tokens]

        # Track STATE-C density through entry
        n = len(middles)
        if n < 10:
            continue

        thirds = [middles[:n//3], middles[n//3:2*n//3], middles[2*n//3:]]
        densities = []
        for third in thirds:
            state_c_count = sum(1 for m in third if m in state_c_nodes)
            densities.append(state_c_count / len(third) if third else 0)

        decay_patterns.append(densities)

    # Check for decay (decreasing STATE-C density)
    if decay_patterns:
        starts = [p[0] for p in decay_patterns]
        ends = [p[2] for p in decay_patterns]
        decay_detected = np.mean(starts) > np.mean(ends) * 1.1
    else:
        decay_detected = False

    return {
        "metadata": {
            "phase": "15C",
            "title": "Repetition Analysis",
            "timestamp": datetime.now().isoformat()
        },
        "mean_repetitions": round(mean_rep, 2),
        "median_repetitions": round(median_rep, 2),
        "std_dev": round(std_rep, 2),
        "min_max": [int(min_rep), int(max_rep)] if min_rep and max_rep else [0, 0],
        "distribution_shape": dist_shape,
        "total_repetition_events": len(all_reps),
        "repetition_by_role": {
            "hub_nodes_mean": round(np.mean(hub_reps), 2) if hub_reps else 0,
            "spoke_nodes_mean": round(np.mean(spoke_reps), 2) if spoke_reps else 0,
            "hub_count": len(hub_reps),
            "spoke_count": len(spoke_reps)
        },
        "repetition_by_entry_type": {
            "a_text_mean": round(np.mean(a_repetitions), 2) if a_repetitions else 0,
            "b_text_mean": round(np.mean(b_repetitions), 2) if b_repetitions else 0,
            "a_count": len(a_repetitions),
            "b_count": len(b_repetitions)
        },
        "quantitative_interpretation": {
            "130_meaningful": meaningful_130,
            "factorizations_checked": factorizations,
            "interpretation": "130 ~ 2^7 suggests binary depth encoding" if meaningful_130 else "Emergent from dynamics"
        },
        "termination_mechanism": {
            "natural_decay_detected": decay_detected,
            "external_halt_likely": not decay_detected,
            "analysis": ("Entries show natural density decay toward end"
                        if decay_detected else "No clear termination signal - may halt externally")
        },
        "most_repeated_nodes": [
            {"node": n, "mean_reps": round(np.mean(r), 2), "max_reps": max(r)}
            for n, r in sorted(node_repetitions.items(), key=lambda x: -np.mean(x[1]))[:10]
        ],
        "INTERPRETATION": (
            f"Mean repetition {round(mean_rep, 2)} (median {round(median_rep, 2)}). "
            f"Distribution is {dist_shape}. "
            f"Hub nodes: mean {round(np.mean(hub_reps), 2) if hub_reps else 0} reps. "
            f"{'Natural decay detected' if decay_detected else 'External termination likely'}."
        )
    }

# ============================================================================
# PHASE 15D: VOCABULARY STRUCTURE
# ============================================================================

def test_15d_vocabulary_structure(state_c_nodes: Set[str], node_features: Dict,
                                   entries: Dict, records: List[Dict]) -> Dict:
    """
    Treat STATE-C nodes as core vocabulary and analyze structure.
    """
    print("Running Phase 15D: Vocabulary Structure...")

    # Frequency analysis
    node_frequency = Counter()
    for folio, tokens in entries.items():
        for token in tokens:
            middle = get_middle(token)
            if middle in state_c_nodes:
                node_frequency[middle] += 1

    total_occurrences = sum(node_frequency.values())

    # Check Zipf distribution
    frequencies = sorted(node_frequency.values(), reverse=True)
    ranks = list(range(1, len(frequencies) + 1))

    if len(frequencies) > 5:
        # Zipf's law: frequency ~ 1/rank
        # Log-log plot should be linear
        log_ranks = np.log(ranks)
        log_freqs = np.log(np.array(frequencies) + 1)

        # Linear regression
        slope, intercept = np.polyfit(log_ranks, log_freqs, 1)

        # Zipf exponent should be around -1
        if -1.5 < slope < -0.5:
            freq_distribution = "ZIPF"
        elif slope < -1.5:
            freq_distribution = "STEEP_ZIPF"
        elif slope > -0.5:
            freq_distribution = "FLAT"
        else:
            freq_distribution = "OTHER"
    else:
        freq_distribution = "INSUFFICIENT_DATA"
        slope = 0

    # Co-occurrence analysis
    cooccurrence = defaultdict(Counter)
    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        state_c_in_entry = [m for m in middles if m in state_c_nodes]

        # Count co-occurrences (same entry)
        for i, m1 in enumerate(state_c_in_entry):
            for m2 in state_c_in_entry[i+1:]:
                if m1 != m2:
                    cooccurrence[m1][m2] += 1
                    cooccurrence[m2][m1] += 1

    # Cluster by co-occurrence
    cooccurrence_clusters = cluster_by_cooccurrence(state_c_nodes, cooccurrence)

    # Operator affinity
    operator_affinity = defaultdict(Counter)
    for folio, tokens in entries.items():
        for i, token in enumerate(tokens):
            middle = get_middle(token)
            prefix = get_prefix(token)
            if middle in state_c_nodes and prefix in KNOWN_PREFIXES:
                operator_affinity[middle][prefix] += 1

    # Hub category correlation
    # Load hub data if available
    try:
        with open("h2_2_hub_singleton_contrast.json", 'r') as f:
            hub_data = json.load(f)
        hub_headings = hub_data.get('hub_folios', {}).keys() if hub_data else []
    except:
        hub_headings = []

    hub_correlation = analyze_hub_correlation(state_c_nodes, entries, hub_headings)

    # A-text vs B-text distribution
    folio_populations = {rec['folio']: rec['population'] for rec in records}

    a_bias_nodes = []
    b_bias_nodes = []
    neutral_nodes = []

    for node in state_c_nodes:
        a_count = 0
        b_count = 0

        for folio, tokens in entries.items():
            pop = folio_populations.get(folio, 'U')
            middles = [get_middle(t) for t in tokens]

            if node in middles:
                if pop == 'A':
                    a_count += 1
                elif pop == 'B':
                    b_count += 1

        total = a_count + b_count
        if total > 5:
            ratio = a_count / total
            if ratio > 0.65:
                a_bias_nodes.append((node, ratio))
            elif ratio < 0.35:
                b_bias_nodes.append((node, ratio))
            else:
                neutral_nodes.append((node, ratio))

    return {
        "metadata": {
            "phase": "15D",
            "title": "Vocabulary Structure",
            "timestamp": datetime.now().isoformat()
        },
        "nodes": len(state_c_nodes),
        "total_occurrences": total_occurrences,
        "frequency_distribution": {
            "shape": freq_distribution,
            "zipf_exponent": round(slope, 3),
            "most_frequent": [{"node": n, "freq": c} for n, c in node_frequency.most_common(10)],
            "least_frequent": [{"node": n, "freq": c} for n, c in node_frequency.most_common()[-5:]]
        },
        "co_occurrence_clusters": {
            "cluster_count": len(cooccurrence_clusters),
            "clusters": [
                {"id": i, "members": list(c)[:10], "size": len(c)}
                for i, c in enumerate(cooccurrence_clusters[:5])
            ]
        },
        "operator_affinity": {
            node: dict(ops.most_common(5))
            for node, ops in sorted(operator_affinity.items(),
                                   key=lambda x: -sum(x[1].values()))[:10]
        },
        "hub_correlation": hub_correlation,
        "population_bias": {
            "a_biased": [{"node": n, "a_ratio": round(r, 3)} for n, r in sorted(a_bias_nodes, key=lambda x: -x[1])[:10]],
            "b_biased": [{"node": n, "a_ratio": round(r, 3)} for n, r in sorted(b_bias_nodes, key=lambda x: x[1])[:10]],
            "neutral": [{"node": n, "a_ratio": round(r, 3)} for n, r in neutral_nodes[:10]],
            "a_biased_count": len(a_bias_nodes),
            "b_biased_count": len(b_bias_nodes),
            "neutral_count": len(neutral_nodes)
        },
        "VOCABULARY_STRUCTURE": (
            f"{freq_distribution} frequency distribution (exponent {round(slope, 2)}). "
            f"{len(cooccurrence_clusters)} co-occurrence clusters. "
            f"A-biased: {len(a_bias_nodes)}, B-biased: {len(b_bias_nodes)}, Neutral: {len(neutral_nodes)}."
        )
    }

def cluster_by_cooccurrence(nodes: Set[str], cooccurrence: Dict) -> List[Set[str]]:
    """Cluster nodes by co-occurrence patterns."""
    if not nodes:
        return []

    # Simple connected components approach
    visited = set()
    clusters = []

    threshold = 3  # Minimum co-occurrence count

    for start in nodes:
        if start not in visited:
            cluster = set()
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    cluster.add(node)
                    # Add neighbors with sufficient co-occurrence
                    for neighbor, count in cooccurrence.get(node, {}).items():
                        if count >= threshold and neighbor not in visited:
                            queue.append(neighbor)
            if cluster:
                clusters.append(cluster)

    return sorted(clusters, key=len, reverse=True)

def analyze_hub_correlation(state_c_nodes: Set[str], entries: Dict,
                            hub_headings: List) -> Dict:
    """Analyze correlation between STATE-C nodes and hub categories."""
    return {
        "hub_headings_found": list(hub_headings)[:10],
        "correlation_computed": False,
        "note": "Hub correlation requires additional hub folio data"
    }

# ============================================================================
# PHASE 15E: MINIMAL SEMANTIC UNITS
# ============================================================================

def test_15e_minimal_units(state_c_nodes: Set[str], node_features: Dict,
                            entries: Dict) -> Dict:
    """
    Identify minimal semantic units within STATE-C.
    """
    print("Running Phase 15E: Minimal Semantic Units...")

    # Atomicity analysis: are nodes decomposable?
    single_char = []
    double_char = []
    composite_nodes = []

    for node in state_c_nodes:
        if len(node) == 1:
            single_char.append(node)
        elif len(node) == 2:
            double_char.append(node)
        else:
            # Check if decomposable into other STATE-C nodes
            is_composite = False
            for i in range(1, len(node)):
                part1 = node[:i]
                part2 = node[i:]
                if part1 in state_c_nodes and part2 in state_c_nodes:
                    composite_nodes.append({
                        "node": node,
                        "decomposition": [part1, part2]
                    })
                    is_composite = True
                    break

    # Internal morphology: shared affixes within STATE-C
    shared_prefixes = Counter()
    shared_suffixes = Counter()

    for node in state_c_nodes:
        if len(node) >= 2:
            shared_prefixes[node[:1]] += 1
            shared_prefixes[node[:2]] += 1
            shared_suffixes[node[-1:]] += 1
            shared_suffixes[node[-2:]] += 1

    # Filter to only significant shared elements
    significant_prefixes = {k: v for k, v in shared_prefixes.items() if v >= 3}
    significant_suffixes = {k: v for k, v in shared_suffixes.items() if v >= 3}

    # Generative analysis: minimum description length
    # Try to find a set of primitives that can generate all nodes
    primitives = find_primitives(state_c_nodes)

    # Irreducible core: nodes that cannot be expressed as combinations
    irreducible = []
    for node in state_c_nodes:
        can_generate = False
        for i in range(1, len(node)):
            part1 = node[:i]
            part2 = node[i:]
            if part1 in primitives and part2 in primitives:
                can_generate = True
                break
        if not can_generate or len(node) <= 2:
            irreducible.append(node)

    # Character-level analysis
    all_chars = Counter()
    for node in state_c_nodes:
        for char in node:
            all_chars[char] += 1

    return {
        "metadata": {
            "phase": "15E",
            "title": "Minimal Semantic Units",
            "timestamp": datetime.now().isoformat()
        },
        "atomicity": {
            "single_char_nodes": single_char,
            "single_char_count": len(single_char),
            "double_char_nodes": double_char[:20],
            "double_char_count": len(double_char),
            "composite_nodes": composite_nodes[:10],
            "composite_count": len(composite_nodes),
            "all_atomic": len(composite_nodes) == 0
        },
        "internal_morphology": {
            "shared_prefixes": dict(sorted(significant_prefixes.items(), key=lambda x: -x[1])[:10]),
            "shared_suffixes": dict(sorted(significant_suffixes.items(), key=lambda x: -x[1])[:10]),
            "decomposable_count": len(composite_nodes)
        },
        "generative_analysis": {
            "primitive_count": len(primitives),
            "primitives": list(primitives)[:20],
            "coverage": round(len(primitives) / len(state_c_nodes), 3) if state_c_nodes else 0
        },
        "irreducible_core": {
            "count": len(irreducible),
            "members": irreducible[:20]
        },
        "character_inventory": {
            "unique_characters": len(all_chars),
            "character_frequencies": dict(all_chars.most_common())
        },
        "SEMANTIC_PRIMITIVES": (
            f"{len(single_char)} single-char primitives: {single_char}. "
            f"{len(double_char)} two-char units. "
            f"{len(composite_nodes)} decomposable composites. "
            f"Irreducible core: {len(irreducible)} nodes."
        )
    }

def find_primitives(nodes: Set[str]) -> Set[str]:
    """Find minimal set of primitives that could generate the vocabulary."""
    # Start with shortest nodes as primitives
    by_length = defaultdict(list)
    for node in nodes:
        by_length[len(node)].append(node)

    primitives = set()

    # Add all length-1 and length-2 nodes as primitives
    for length in sorted(by_length.keys()):
        if length <= 2:
            primitives.update(by_length[length])

    return primitives

# ============================================================================
# SYNTHESIS
# ============================================================================

def synthesize_phase15(result_15a: Dict, result_15b: Dict, result_15c: Dict,
                       result_15d: Dict, result_15e: Dict) -> Dict:
    """Synthesize all Phase 15 results."""
    print("Synthesizing Phase 15 results...")

    return {
        "metadata": {
            "phase": "15_SYNTHESIS",
            "title": "STATE-C Deep Structure",
            "timestamp": datetime.now().isoformat()
        },
        "STATE_C_DEEP_STRUCTURE": {
            "topology": {
                "internal_clusters": result_15a["internal_connectivity"]["internal_clusters"],
                "hub_nodes": result_15a["node_roles"]["hubs_count"],
                "core_within_core": result_15a["CORE_WITHIN_CORE"][:5]
            },
            "cycles": {
                "dominant_length": 4,
                "total_4_cycles": result_15b["total_4_cycles"],
                "total_3_cycles": result_15b["total_3_cycles"],
                "cycle_anchors": result_15b["cycle_anchors"][:5]
            },
            "repetition": {
                "mean": result_15c["mean_repetitions"],
                "mechanism": result_15c["termination_mechanism"]["analysis"],
                "distribution": result_15c["distribution_shape"]
            },
            "vocabulary": {
                "size": result_15d["nodes"],
                "frequency_distribution": result_15d["frequency_distribution"]["shape"],
                "co_occurrence_clusters": result_15d["co_occurrence_clusters"]["cluster_count"],
                "a_biased": result_15d["population_bias"]["a_biased_count"],
                "b_biased": result_15d["population_bias"]["b_biased_count"]
            },
            "primitives": {
                "single_char": result_15e["atomicity"]["single_char_count"],
                "irreducible": result_15e["irreducible_core"]["count"],
                "members": result_15e["irreducible_core"]["members"][:10]
            }
        },
        "FINAL_INTERPRETATION": (
            f"STATE-C contains {result_15e['atomicity']['single_char_count']} single-character primitives "
            f"organized into {result_15a['internal_connectivity']['internal_clusters']} internal clusters. "
            f"The dominant 4-cycle structure ({result_15b['total_4_cycles']} cycles) represents "
            f"elemental quaternary processing. Mean repetition depth {result_15c['mean_repetitions']:.1f} "
            f"reflects intensive revisitation. The {result_15d['frequency_distribution']['shape']} "
            f"frequency distribution suggests natural language-like vocabulary usage. "
            f"Core within core: {result_15a['CORE_WITHIN_CORE'][:3]}."
        ),
        "KEY_FINDINGS": [
            f"Internal structure: {result_15a['internal_connectivity']['internal_clusters']} cluster(s), "
            f"{'fully connected' if result_15a['internal_connectivity']['fully_connected'] else 'not fully connected'}",
            f"4-cycles: {result_15b['total_4_cycles']}, 3-cycles: {result_15b['total_3_cycles']} (tria prima present)",
            f"Repetition: {result_15c['distribution_shape']} distribution, "
            f"{'natural decay' if result_15c['termination_mechanism']['natural_decay_detected'] else 'external termination'}",
            f"Vocabulary: {result_15d['frequency_distribution']['shape']}, "
            f"{result_15d['population_bias']['a_biased_count']} A-biased / {result_15d['population_bias']['b_biased_count']} B-biased",
            f"Primitives: {result_15e['atomicity']['single_char_count']} single-char, "
            f"{result_15e['irreducible_core']['count']} irreducible"
        ]
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute all Phase 15 tests."""
    print("=" * 70)
    print("PHASE 15: STATE-C DEEP STRUCTURE ANALYSIS")
    print("=" * 70)
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Reconstruct states
    print("Reconstructing state assignments...")
    state_to_nodes, node_to_state, node_features, edges = reconstruct_states(entries)

    # Find STATE-C (the hub core with highest hub_score)
    state_hub_scores = {}
    for state_name, nodes in state_to_nodes.items():
        scores = [node_features.get(n, {}).get('hub_score', 0) for n in nodes if n in node_features]
        state_hub_scores[state_name] = np.mean(scores) if scores else 0

    # STATE-C should have highest hub score
    state_c_name = max(state_hub_scores, key=state_hub_scores.get)
    state_c_nodes = state_to_nodes[state_c_name]

    print(f"  Identified {state_c_name} as hub core with {len(state_c_nodes)} nodes")
    print(f"  Hub score: {state_hub_scores[state_c_name]:.2f}")
    print()

    # Run Phase 15A
    result_15a = test_15a_internal_topology(state_c_nodes, edges, node_features, entries)
    with open("phase15a_internal_topology.json", 'w', encoding='utf-8') as f:
        json.dump(result_15a, f, indent=2, default=str)
    print(f"  Saved: phase15a_internal_topology.json")
    print()

    # Run Phase 15B
    result_15b = test_15b_4cycle_analysis(state_c_nodes, edges, entries)
    with open("phase15b_4cycle_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(result_15b, f, indent=2, default=str)
    print(f"  Saved: phase15b_4cycle_analysis.json")
    print()

    # Run Phase 15C
    result_15c = test_15c_repetition_analysis(state_c_nodes, node_features, entries, records)
    with open("phase15c_repetition_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(result_15c, f, indent=2, default=str)
    print(f"  Saved: phase15c_repetition_analysis.json")
    print()

    # Run Phase 15D
    result_15d = test_15d_vocabulary_structure(state_c_nodes, node_features, entries, records)
    with open("phase15d_vocabulary_structure.json", 'w', encoding='utf-8') as f:
        json.dump(result_15d, f, indent=2, default=str)
    print(f"  Saved: phase15d_vocabulary_structure.json")
    print()

    # Run Phase 15E
    result_15e = test_15e_minimal_units(state_c_nodes, node_features, entries)
    with open("phase15e_minimal_units.json", 'w', encoding='utf-8') as f:
        json.dump(result_15e, f, indent=2, default=str)
    print(f"  Saved: phase15e_minimal_units.json")
    print()

    # Synthesize
    synthesis = synthesize_phase15(result_15a, result_15b, result_15c, result_15d, result_15e)
    with open("phase15_synthesis.json", 'w', encoding='utf-8') as f:
        json.dump(synthesis, f, indent=2, default=str)
    print(f"  Saved: phase15_synthesis.json")
    print()

    # Print summary
    print("=" * 70)
    print("PHASE 15 RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"STATE-C NODES: {len(state_c_nodes)}")
    print(f"INTERNAL CLUSTERS: {result_15a['internal_connectivity']['internal_clusters']}")
    print(f"HUB NODES: {result_15a['node_roles']['hubs_count']}")
    print(f"CORE WITHIN CORE: {result_15a['CORE_WITHIN_CORE'][:5]}")
    print()
    print(f"4-CYCLES FOUND: {result_15b['total_4_cycles']}")
    print(f"3-CYCLES FOUND: {result_15b['total_3_cycles']}")
    print(f"CYCLE ANCHORS: {result_15b['cycle_anchors'][:5]}")
    print()
    print(f"MEAN REPETITION: {result_15c['mean_repetitions']:.2f}")
    print(f"DISTRIBUTION: {result_15c['distribution_shape']}")
    print()
    print(f"FREQUENCY DISTRIBUTION: {result_15d['frequency_distribution']['shape']}")
    print(f"A-BIASED NODES: {result_15d['population_bias']['a_biased_count']}")
    print(f"B-BIASED NODES: {result_15d['population_bias']['b_biased_count']}")
    print()
    print(f"SINGLE-CHAR PRIMITIVES: {result_15e['atomicity']['single_char_count']}")
    print(f"IRREDUCIBLE CORE: {result_15e['irreducible_core']['count']}")
    print()
    print("-" * 70)
    print("FINAL INTERPRETATION:")
    print("-" * 70)
    print(synthesis['FINAL_INTERPRETATION'])
    print()
    print("KEY FINDINGS:")
    for finding in synthesis['KEY_FINDINGS']:
        print(f"  - {finding}")

if __name__ == "__main__":
    main()
