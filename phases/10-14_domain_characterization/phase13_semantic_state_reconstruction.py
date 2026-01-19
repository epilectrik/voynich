#!/usr/bin/env python3
"""
Phase 13: Semantic State Reconstruction & Execution Tests
=========================================================

Situation: Phase 12 established the Voynich as a private cyclic alchemical algebra
with 94.6% reversibility and 97.7% cyclic collapse. The remaining unknown is
STATE IDENTITY, not vocabulary.

Goal: Infer what distinct semantic STATES this system operates over, and test
whether it can be run as a transformation engine.

Ground Rules:
- No substance naming (states are abstract until behavior defines them)
- No image consultation (pathway remains closed)
- No premature labeling (let the machine speak)
- Treat this as reverse-engineering an executable system

Sub-phases:
- 13A: Semantic State Inference
- 13B: State Transition Grammar
- 13C: Quantitative State Depth
- 13D: Dimensionality Analysis
- 13E: Executability Test
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
# CORPUS LOADING (reuse from Phase 10-11)
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
                    # CRITICAL: Filter to H (PRIMARY) transcriber track only
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
# PHASE 13A: SEMANTIC STATE INFERENCE
# ============================================================================

def test_13a_semantic_states(entries: Dict[str, List[str]]) -> Dict:
    """
    Infer latent semantic states from attractor and transition behavior.

    Clustering approach:
    1. For each attractor/hub node, compute behavioral features
    2. Cluster into semantic state candidates
    3. Assign abstract labels (STATE-A, STATE-B, etc.)
    """
    print("Running Phase 13A: Semantic State Inference...")

    # Build transition graph: middle1 -> middle2 with operator
    edges = defaultdict(lambda: defaultdict(int))  # (m1, m2) -> {prefix: count}
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

    # Get all unique nodes (middles)
    all_nodes = set(node_in_degree.keys()) | set(node_out_degree.keys())
    print(f"  Total nodes (middles): {len(all_nodes)}")

    # Compute behavioral features for each node
    node_features = {}

    for node in all_nodes:
        in_deg = node_in_degree.get(node, 0)
        out_deg = node_out_degree.get(node, 0)
        total_deg = in_deg + out_deg

        if total_deg < 10:  # Skip very rare nodes
            continue

        # Feature 1: Convergence probability (in-degree / total degree)
        convergence = in_deg / total_deg if total_deg > 0 else 0

        # Feature 2: Predecessor diversity (how many different states can reach this)
        pred_count = len(predecessors.get(node, set()))

        # Feature 3: Successor diversity (how many states can this reach)
        succ_count = len(successors.get(node, set()))

        # Feature 4: Stability (self-loop ratio)
        stability = node_self_loops.get(node, 0) / out_deg if out_deg > 0 else 0

        # Feature 5: Asymmetry (difference between in and out flow)
        asymmetry = (in_deg - out_deg) / total_deg if total_deg > 0 else 0

        # Feature 6: Hub score (geometric mean of in and out)
        hub_score = math.sqrt(in_deg * out_deg) if in_deg > 0 and out_deg > 0 else 0

        node_features[node] = {
            'convergence': round(convergence, 3),
            'predecessor_count': pred_count,
            'successor_count': succ_count,
            'stability': round(stability, 3),
            'asymmetry': round(asymmetry, 3),
            'hub_score': round(hub_score, 2),
            'in_degree': in_deg,
            'out_degree': out_deg,
            'total_degree': total_deg
        }

    print(f"  Nodes with sufficient traffic: {len(node_features)}")

    # Cluster nodes by behavioral similarity
    # Use simple k-means-like clustering on normalized features
    feature_vectors = []
    node_list = list(node_features.keys())

    for node in node_list:
        f = node_features[node]
        feature_vectors.append([
            f['convergence'],
            f['predecessor_count'] / 100,  # Normalize
            f['successor_count'] / 100,
            f['stability'],
            f['asymmetry'],
            f['hub_score'] / 100
        ])

    feature_vectors = np.array(feature_vectors)

    # Normalize features
    if len(feature_vectors) > 0:
        means = np.mean(feature_vectors, axis=0)
        stds = np.std(feature_vectors, axis=0) + 1e-6
        feature_vectors_norm = (feature_vectors - means) / stds
    else:
        feature_vectors_norm = feature_vectors

    # Try different cluster counts and find optimal via silhouette-like score
    best_k = 0
    best_score = -1
    best_labels = None

    for k in range(3, 13):  # Test 3-12 clusters (classic alchemical range)
        if len(feature_vectors_norm) < k:
            continue

        labels, centroids = simple_kmeans(feature_vectors_norm, k, max_iter=50)
        score = silhouette_score_simple(feature_vectors_norm, labels)

        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels

    print(f"  Optimal cluster count: {best_k} (silhouette: {best_score:.3f})")

    # Build state definitions
    states = {}
    for i in range(best_k):
        state_name = f"STATE-{chr(65 + i)}"  # STATE-A, STATE-B, etc.
        member_indices = [j for j, l in enumerate(best_labels) if l == i]
        member_nodes = [node_list[j] for j in member_indices]

        if not member_nodes:
            continue

        # Aggregate features
        agg_features = {
            'convergence': np.mean([node_features[n]['convergence'] for n in member_nodes]),
            'predecessor_count': np.mean([node_features[n]['predecessor_count'] for n in member_nodes]),
            'successor_count': np.mean([node_features[n]['successor_count'] for n in member_nodes]),
            'stability': np.mean([node_features[n]['stability'] for n in member_nodes]),
            'asymmetry': np.mean([node_features[n]['asymmetry'] for n in member_nodes]),
            'hub_score': np.mean([node_features[n]['hub_score'] for n in member_nodes])
        }

        states[state_name] = {
            'member_count': len(member_nodes),
            'member_nodes': member_nodes[:20],  # Top 20 examples
            'convergence_probability': round(agg_features['convergence'], 3),
            'operator_reachability': {
                'in': round(agg_features['predecessor_count'], 1),
                'out': round(agg_features['successor_count'], 1)
            },
            'stability_score': round(agg_features['stability'], 3),
            'asymmetry': round(agg_features['asymmetry'], 3),
            'hub_score': round(agg_features['hub_score'], 2)
        }

    # Classify states by behavior
    state_classification = {}
    for state_name, state_data in states.items():
        if state_data['asymmetry'] > 0.2:
            state_classification[state_name] = "ABSORBING"
        elif state_data['asymmetry'] < -0.2:
            state_classification[state_name] = "SOURCE"
        elif state_data['stability_score'] > 0.1:
            state_classification[state_name] = "OSCILLATORY"
        else:
            state_classification[state_name] = "TRANSIENT"

    return {
        "metadata": {
            "phase": "13A",
            "title": "Semantic State Inference",
            "timestamp": datetime.now().isoformat()
        },
        "total_candidates_analyzed": len(all_nodes),
        "nodes_with_sufficient_traffic": len(node_features),
        "stable_states_identified": len(states),
        "clustering_quality": {
            "silhouette_score": round(best_score, 3),
            "optimal_k": best_k
        },
        "states": states,
        "state_classification": state_classification,
        "node_features_sample": {k: node_features[k] for k in list(node_features.keys())[:20]}
    }

def simple_kmeans(X: np.ndarray, k: int, max_iter: int = 50) -> Tuple[List[int], np.ndarray]:
    """Simple k-means clustering."""
    n = len(X)
    if n == 0:
        return [], np.array([])

    # Initialize centroids randomly
    indices = random.sample(range(n), min(k, n))
    centroids = X[indices].copy()

    labels = [0] * n

    for _ in range(max_iter):
        # Assign points to nearest centroid
        new_labels = []
        for i in range(n):
            distances = [np.linalg.norm(X[i] - c) for c in centroids]
            new_labels.append(np.argmin(distances))

        # Check convergence
        if new_labels == labels:
            break
        labels = new_labels

        # Update centroids
        for j in range(k):
            cluster_points = X[[i for i, l in enumerate(labels) if l == j]]
            if len(cluster_points) > 0:
                centroids[j] = np.mean(cluster_points, axis=0)

    return labels, centroids

def silhouette_score_simple(X: np.ndarray, labels: List[int]) -> float:
    """Simplified silhouette score calculation."""
    n = len(X)
    if n < 2:
        return 0

    unique_labels = set(labels)
    if len(unique_labels) < 2:
        return 0

    scores = []
    for i in range(n):
        # a = average distance to same cluster
        same_cluster = [j for j in range(n) if labels[j] == labels[i] and j != i]
        if len(same_cluster) == 0:
            continue
        a = np.mean([np.linalg.norm(X[i] - X[j]) for j in same_cluster])

        # b = minimum average distance to other clusters
        b_values = []
        for label in unique_labels:
            if label != labels[i]:
                other_cluster = [j for j in range(n) if labels[j] == label]
                if len(other_cluster) > 0:
                    b_values.append(np.mean([np.linalg.norm(X[i] - X[j]) for j in other_cluster]))

        if not b_values:
            continue
        b = min(b_values)

        scores.append((b - a) / max(a, b) if max(a, b) > 0 else 0)

    return np.mean(scores) if scores else 0

# ============================================================================
# PHASE 13B: STATE TRANSITION GRAMMAR
# ============================================================================

def test_13b_transition_grammar(entries: Dict[str, List[str]], states_result: Dict) -> Dict:
    """
    Build state-transition matrix and analyze transition structure.
    """
    print("Running Phase 13B: State Transition Grammar...")

    # Get state assignments
    state_to_nodes = {}
    node_to_state = {}

    for state_name, state_data in states_result['states'].items():
        state_to_nodes[state_name] = set(state_data['member_nodes'])
        for node in state_data['member_nodes']:
            node_to_state[node] = state_name

    # Get all operators
    all_operators = set()
    for folio, tokens in entries.items():
        for token in tokens:
            prefix = get_prefix(token)
            if prefix in KNOWN_PREFIXES:
                all_operators.add(prefix)

    operators = list(all_operators)
    state_names = list(states_result['states'].keys())

    print(f"  States: {len(state_names)}, Operators: {len(operators)}")

    # Build transition matrix: (state_from, operator) -> state_to counts
    transitions = defaultdict(lambda: defaultdict(Counter))  # state_from -> operator -> state_to counts

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        prefixes = [get_prefix(t) for t in tokens]

        for i in range(len(middles) - 1):
            m1, m2 = middles[i], middles[i + 1]
            op = prefixes[i + 1]

            s1 = node_to_state.get(m1)
            s2 = node_to_state.get(m2)

            if s1 and s2 and op in KNOWN_PREFIXES:
                transitions[s1][op][s2] += 1

    # Convert to probability matrix
    transition_probs = {}
    for s_from in state_names:
        transition_probs[s_from] = {}
        for op in operators:
            total = sum(transitions[s_from][op].values())
            if total > 0:
                transition_probs[s_from][op] = {
                    s_to: round(count / total, 3)
                    for s_to, count in transitions[s_from][op].items()
                }

    # Find reversible pairs
    reversible_pairs = []
    for s1 in state_names:
        for s2 in state_names:
            if s1 >= s2:
                continue

            # Find operators that go s1 -> s2
            ops_forward = []
            for op in operators:
                if s2 in transitions[s1][op] and transitions[s1][op][s2] > 5:
                    ops_forward.append((op, transitions[s1][op][s2]))

            # Find operators that go s2 -> s1
            ops_backward = []
            for op in operators:
                if s1 in transitions[s2][op] and transitions[s2][op][s1] > 5:
                    ops_backward.append((op, transitions[s2][op][s1]))

            if ops_forward and ops_backward:
                reversible_pairs.append({
                    'states': (s1, s2),
                    'forward_ops': ops_forward[:3],
                    'backward_ops': ops_backward[:3]
                })

    # Find forbidden transitions (state pairs with zero probability)
    forbidden = []
    for s1 in state_names:
        for s2 in state_names:
            has_transition = False
            for op in operators:
                if s2 in transitions[s1][op]:
                    has_transition = True
                    break
            if not has_transition:
                forbidden.append((s1, s2))

    # State classification based on flow
    state_flow = {}
    for state in state_names:
        in_flow = sum(
            sum(transitions[s][op].get(state, 0) for op in operators)
            for s in state_names
        )
        out_flow = sum(
            sum(transitions[state][op].values())
            for op in operators
        )

        if in_flow > 0 and out_flow > 0:
            ratio = in_flow / out_flow
            if ratio > 2:
                state_flow[state] = "absorbing"
            elif ratio < 0.5:
                state_flow[state] = "transient"
            else:
                state_flow[state] = "oscillatory"
        elif in_flow > 0:
            state_flow[state] = "absorbing"
        elif out_flow > 0:
            state_flow[state] = "transient"
        else:
            state_flow[state] = "isolated"

    # Check for purification engine signature
    has_absorbing = "absorbing" in state_flow.values()
    has_oscillatory = "oscillatory" in state_flow.values()
    has_forbidden = len(forbidden) > 0
    purification_signature = has_absorbing and has_oscillatory and has_forbidden

    return {
        "metadata": {
            "phase": "13B",
            "title": "State Transition Grammar",
            "timestamp": datetime.now().isoformat()
        },
        "transition_matrix_summary": {
            "states": len(state_names),
            "operators": len(operators),
            "total_transitions_recorded": sum(
                sum(sum(transitions[s][op].values()) for op in operators)
                for s in state_names
            )
        },
        "reversible_pairs": {
            "count": len(reversible_pairs),
            "examples": reversible_pairs[:10]
        },
        "forbidden_transitions": {
            "count": len(forbidden),
            "examples": forbidden[:20]
        },
        "state_flow_classification": state_flow,
        "state_classification_counts": Counter(state_flow.values()),
        "PURIFICATION_ENGINE_SIGNATURE": "YES" if purification_signature else "NO",
        "signature_components": {
            "has_absorbing_states": has_absorbing,
            "has_oscillatory_core": has_oscillatory,
            "has_forbidden_zones": has_forbidden
        }
    }

# ============================================================================
# PHASE 13C: QUANTITATIVE STATE DEPTH
# ============================================================================

def test_13c_quantitative_depth(entries: Dict[str, List[str]], states_result: Dict) -> Dict:
    """
    Test whether states differ quantitatively (processing depth).
    """
    print("Running Phase 13C: Quantitative State Depth...")

    # Build node_to_state mapping
    node_to_state = {}
    for state_name, state_data in states_result['states'].items():
        for node in state_data['member_nodes']:
            node_to_state[node] = state_name

    state_names = list(states_result['states'].keys())

    # Metrics per state
    state_metrics = {s: {
        'cycle_lengths': [],
        'revisit_counts': [],
        'position_in_entry': [],
        'operator_diversity': set()
    } for s in state_names}

    # Process entries
    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        prefixes = [get_prefix(t) for t in tokens]
        n = len(middles)

        if n < 3:
            continue

        # Track state visitation
        state_visits = defaultdict(list)  # state -> list of positions

        for i, (m, p) in enumerate(zip(middles, prefixes)):
            state = node_to_state.get(m)
            if state:
                state_visits[state].append(i)
                state_metrics[state]['position_in_entry'].append(i / n)
                if p in KNOWN_PREFIXES:
                    state_metrics[state]['operator_diversity'].add(p)

        # Measure cycle lengths (distance between revisits)
        for state, positions in state_visits.items():
            if len(positions) > 1:
                for i in range(len(positions) - 1):
                    cycle_len = positions[i + 1] - positions[i]
                    state_metrics[state]['cycle_lengths'].append(cycle_len)
                state_metrics[state]['revisit_counts'].append(len(positions))

    # Compute aggregated metrics
    per_state_metrics = {}
    for state in state_names:
        metrics = state_metrics[state]

        per_state_metrics[state] = {
            'mean_cycle_length': round(np.mean(metrics['cycle_lengths']), 2) if metrics['cycle_lengths'] else 0,
            'repetition_depth': round(np.mean(metrics['revisit_counts']), 2) if metrics['revisit_counts'] else 0,
            'mean_position_in_entry': round(np.mean(metrics['position_in_entry']), 3) if metrics['position_in_entry'] else 0.5,
            'operator_diversity': len(metrics['operator_diversity']),
            'sample_size': len(metrics['position_in_entry'])
        }

    # Order states by processing depth
    state_ordering_by_position = sorted(
        per_state_metrics.keys(),
        key=lambda s: per_state_metrics[s]['mean_position_in_entry']
    )

    state_ordering_by_refinement = sorted(
        per_state_metrics.keys(),
        key=lambda s: per_state_metrics[s]['mean_cycle_length'],
        reverse=True
    )

    # Measure differentiation strength
    positions = [per_state_metrics[s]['mean_position_in_entry'] for s in state_names if per_state_metrics[s]['sample_size'] > 10]
    if len(positions) > 1:
        position_variance = np.var(positions)
        differentiation = "STRONG" if position_variance > 0.02 else ("MODERATE" if position_variance > 0.005 else "WEAK")
    else:
        differentiation = "INSUFFICIENT_DATA"

    return {
        "metadata": {
            "phase": "13C",
            "title": "Quantitative State Depth",
            "timestamp": datetime.now().isoformat()
        },
        "per_state_metrics": per_state_metrics,
        "state_ordering": {
            "by_processing_depth": state_ordering_by_position,
            "by_refinement_level": state_ordering_by_refinement
        },
        "position_variance": round(np.var(positions), 4) if positions else 0,
        "QUANTITATIVE_DIFFERENTIATION": differentiation,
        "interpretation": {
            "early_states": state_ordering_by_position[:3],
            "late_states": state_ordering_by_position[-3:],
            "high_diversity_states": sorted(
                per_state_metrics.keys(),
                key=lambda s: per_state_metrics[s]['operator_diversity'],
                reverse=True
            )[:3]
        }
    }

# ============================================================================
# PHASE 13D: DIMENSIONALITY ANALYSIS
# ============================================================================

def test_13d_dimensionality(states_result: Dict) -> Dict:
    """
    Determine how many independent semantic axes the state space encodes.
    """
    print("Running Phase 13D: Dimensionality Analysis...")

    states = states_result['states']
    state_names = list(states.keys())

    if len(state_names) < 3:
        return {
            "metadata": {
                "phase": "13D",
                "title": "Dimensionality Analysis",
                "timestamp": datetime.now().isoformat()
            },
            "error": "Insufficient states for dimensionality analysis"
        }

    # Build feature matrix for states
    feature_matrix = []
    for state_name in state_names:
        s = states[state_name]
        feature_matrix.append([
            s['convergence_probability'],
            s['operator_reachability']['in'] / 100,
            s['operator_reachability']['out'] / 100,
            s['stability_score'],
            s['asymmetry'],
            s['hub_score'] / 100
        ])

    X = np.array(feature_matrix)

    # Center the data
    X_centered = X - np.mean(X, axis=0)

    # Compute SVD
    try:
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        # Compute variance explained
        total_variance = np.sum(S ** 2)
        variance_explained = (S ** 2) / total_variance
        cumulative_variance = np.cumsum(variance_explained)

        # Find optimal dimensionality (where cumulative >= 80%)
        optimal_dim = 1
        for i, cv in enumerate(cumulative_variance):
            if cv >= 0.8:
                optimal_dim = i + 1
                break
        else:
            optimal_dim = len(cumulative_variance)

        pca_results = {
            f"{i+1}_component": round(float(cumulative_variance[i]), 3) if i < len(cumulative_variance) else None
            for i in range(min(6, len(cumulative_variance)))
        }

    except Exception as e:
        return {
            "metadata": {
                "phase": "13D",
                "title": "Dimensionality Analysis",
                "timestamp": datetime.now().isoformat()
            },
            "error": str(e)
        }

    # Determine structure type
    if optimal_dim <= 2:
        structure_type = "LINEAR"
    elif optimal_dim == 3:
        structure_type = "ORTHOGONAL_AXES"
    elif optimal_dim == 4:
        structure_type = "ORTHOGONAL_AXES"
    else:
        structure_type = "NETWORK"

    # Test tria prima match (3 axes)
    matches_tria_prima = "YES" if optimal_dim == 3 else ("PARTIAL" if optimal_dim in [2, 4] else "NO")

    # Test elemental match (4 axes)
    matches_elemental = "YES" if optimal_dim == 4 else ("PARTIAL" if optimal_dim in [3, 5] else "NO")

    # Characterize axes (without naming)
    axis_characteristics = []
    for i in range(min(optimal_dim, len(Vt))):
        loadings = Vt[i]
        features = ['convergence', 'in_reach', 'out_reach', 'stability', 'asymmetry', 'hub_score']
        dominant = features[np.argmax(np.abs(loadings))]
        axis_characteristics.append({
            'axis': i + 1,
            'variance_explained': round(float(variance_explained[i]), 3),
            'dominant_feature': dominant,
            'direction': 'positive' if loadings[np.argmax(np.abs(loadings))] > 0 else 'negative'
        })

    return {
        "metadata": {
            "phase": "13D",
            "title": "Dimensionality Analysis",
            "timestamp": datetime.now().isoformat()
        },
        "pca_variance_explained": pca_results,
        "optimal_dimensionality": optimal_dim,
        "structure_type": structure_type,
        "axis_characteristics": axis_characteristics,
        "MATCHES_TRIA_PRIMA": matches_tria_prima,
        "MATCHES_ELEMENTAL": matches_elemental,
        "interpretation": (
            f"State space exhibits {optimal_dim}-dimensional structure. "
            f"{'Consistent with' if optimal_dim in [3,4] else 'Does not match'} classical alchemical ontologies. "
            f"Primary axes: {[a['dominant_feature'] for a in axis_characteristics[:3]]}"
        )
    }

# ============================================================================
# PHASE 13E: EXECUTABILITY TEST
# ============================================================================

def test_13e_executability(entries: Dict[str, List[str]], states_result: Dict,
                           transition_result: Dict, records: List[Dict]) -> Dict:
    """
    Test whether the system can be run as a transformation engine.
    """
    print("Running Phase 13E: Executability Test...")

    # Build mappings
    node_to_state = {}
    for state_name, state_data in states_result['states'].items():
        for node in state_data['member_nodes']:
            node_to_state[node] = state_name

    state_names = list(states_result['states'].keys())

    # Build transition lookup
    transitions = defaultdict(lambda: defaultdict(Counter))

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        prefixes = [get_prefix(t) for t in tokens]

        for i in range(len(middles) - 1):
            m1, m2 = middles[i], middles[i + 1]
            op = prefixes[i + 1]

            s1 = node_to_state.get(m1)
            s2 = node_to_state.get(m2)

            if s1 and s2 and op in KNOWN_PREFIXES:
                transitions[s1][op][s2] += 1

    # Get forbidden transitions
    forbidden = set()
    for s1 in state_names:
        for s2 in state_names:
            has_transition = any(s2 in transitions[s1][op] for op in KNOWN_PREFIXES)
            if not has_transition:
                forbidden.add((s1, s2))

    # Separate A and B entries
    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    a_entries = {f: t for f, t in entries.items() if folio_populations.get(f) == 'A'}
    b_entries = {f: t for f, t in entries.items() if folio_populations.get(f) == 'B'}

    # Simulation: execute entries as state traces
    def trace_entry(tokens):
        """Convert token sequence to state sequence."""
        middles = [get_middle(t) for t in tokens]
        states = []
        for m in middles:
            s = node_to_state.get(m)
            if s:
                states.append(s)
        return states

    def check_trace_validity(state_trace):
        """Check if state trace respects forbidden transitions."""
        violations = 0
        for i in range(len(state_trace) - 1):
            if (state_trace[i], state_trace[i+1]) in forbidden:
                violations += 1
        return violations

    def check_convergence(state_trace):
        """Check if trace converges (settles into stable state or cycle)."""
        if len(state_trace) < 5:
            return False, None

        # Check last 5 states for repetition pattern
        last_states = state_trace[-5:]
        unique_last = set(last_states)

        if len(unique_last) <= 2:
            return True, last_states[-1]
        return False, None

    def check_cycle(state_trace):
        """Check if trace settles into a cycle."""
        if len(state_trace) < 6:
            return False, 0

        # Look for repeating pattern in last portion
        for cycle_len in range(1, 5):
            last_n = state_trace[-cycle_len * 2:]
            if len(last_n) >= cycle_len * 2:
                first_half = last_n[:cycle_len]
                second_half = last_n[cycle_len:cycle_len * 2]
                if first_half == second_half:
                    return True, cycle_len

        return False, 0

    # Run simulations
    results = {
        'a_text': {'valid': 0, 'total': 0, 'violations': []},
        'b_text': {'valid': 0, 'total': 0, 'violations': []},
        'convergence': {'converged': 0, 'total': 0, 'final_states': Counter()},
        'oscillation': {'cyclic': 0, 'total': 0, 'cycle_lengths': Counter()}
    }

    # Process A-text entries
    for folio, tokens in list(a_entries.items())[:100]:
        trace = trace_entry(tokens)
        if len(trace) < 3:
            continue

        results['a_text']['total'] += 1
        violations = check_trace_validity(trace)
        if violations == 0:
            results['a_text']['valid'] += 1
        else:
            results['a_text']['violations'].append((folio, violations))

    # Process B-text entries
    for folio, tokens in list(b_entries.items())[:100]:
        trace = trace_entry(tokens)
        if len(trace) < 3:
            continue

        results['b_text']['total'] += 1
        violations = check_trace_validity(trace)
        if violations == 0:
            results['b_text']['valid'] += 1
        else:
            results['b_text']['violations'].append((folio, violations))

        # Convergence check
        results['convergence']['total'] += 1
        converged, final = check_convergence(trace)
        if converged:
            results['convergence']['converged'] += 1
            if final:
                results['convergence']['final_states'][final] += 1

        # Oscillation check
        results['oscillation']['total'] += 1
        cyclic, cycle_len = check_cycle(trace)
        if cyclic:
            results['oscillation']['cyclic'] += 1
            results['oscillation']['cycle_lengths'][cycle_len] += 1

    # Calculate rates
    a_valid_rate = results['a_text']['valid'] / results['a_text']['total'] if results['a_text']['total'] > 0 else 0
    b_valid_rate = results['b_text']['valid'] / results['b_text']['total'] if results['b_text']['total'] > 0 else 0
    convergence_rate = results['convergence']['converged'] / results['convergence']['total'] if results['convergence']['total'] > 0 else 0
    oscillation_rate = results['oscillation']['cyclic'] / results['oscillation']['total'] if results['oscillation']['total'] > 0 else 0

    # Determine executability
    if a_valid_rate > 0.7 and b_valid_rate > 0.6:
        system_executable = "YES"
        if convergence_rate > 0.3 and oscillation_rate > 0.2:
            execution_type = "PURIFICATION_ENGINE"
        elif oscillation_rate > 0.4:
            execution_type = "CYCLIC_TRANSFORMER"
        else:
            execution_type = "TRANSFORMATION_NETWORK"
    elif a_valid_rate > 0.5 or b_valid_rate > 0.5:
        system_executable = "PARTIAL"
        execution_type = "INCOMPLETE_GRAMMAR"
    else:
        system_executable = "NO"
        execution_type = "NOT_EXECUTABLE"

    return {
        "metadata": {
            "phase": "13E",
            "title": "Executability Test",
            "timestamp": datetime.now().isoformat()
        },
        "simulations_run": results['a_text']['total'] + results['b_text']['total'],
        "convergence": {
            "converged_percent": round(convergence_rate * 100, 1),
            "mean_steps_to_convergence": "N/A",  # Would need additional tracking
            "final_state_distribution": dict(results['convergence']['final_states'].most_common(5))
        },
        "oscillation": {
            "settled_to_cycle_percent": round(oscillation_rate * 100, 1),
            "cycle_length_distribution": dict(results['oscillation']['cycle_lengths'])
        },
        "forbidden_violations": {
            "a_text_violation_count": len(results['a_text']['violations']),
            "b_text_violation_count": len(results['b_text']['violations'])
        },
        "a_text_validity": {
            "valid_starting_states_percent": round(a_valid_rate * 100, 1),
            "total_tested": results['a_text']['total']
        },
        "b_text_validity": {
            "valid_execution_traces_percent": round(b_valid_rate * 100, 1),
            "total_tested": results['b_text']['total']
        },
        "SYSTEM_IS_EXECUTABLE": system_executable,
        "EXECUTION_TYPE": execution_type
    }

# ============================================================================
# SYNTHESIS
# ============================================================================

def synthesize_phase13(result_13a: Dict, result_13b: Dict, result_13c: Dict,
                       result_13d: Dict, result_13e: Dict) -> Dict:
    """Synthesize all Phase 13 results."""
    print("Synthesizing Phase 13 results...")

    # Extract key findings
    state_count = result_13a['stable_states_identified']
    dimensionality = result_13d.get('optimal_dimensionality', 'N/A')
    structure_type = result_13d.get('structure_type', 'N/A')
    reversible_pairs = result_13b['reversible_pairs']['count']
    forbidden_count = result_13b['forbidden_transitions']['count']
    purification_sig = result_13b['PURIFICATION_ENGINE_SIGNATURE']
    differentiation = result_13c['QUANTITATIVE_DIFFERENTIATION']
    executable = result_13e['SYSTEM_IS_EXECUTABLE']
    execution_type = result_13e['EXECUTION_TYPE']

    # Generate final characterization
    final_statement = (
        f"The Voynich operates over {state_count} stable semantic states with "
        f"{dimensionality}-dimensional structure ({structure_type}). "
        f"The transition grammar defines {reversible_pairs} reversible state pairs "
        f"and {forbidden_count} forbidden transitions. "
        f"States differ quantitatively ({differentiation} differentiation). "
        f"System executability: {executable} ({execution_type}). "
    )

    if executable == "YES":
        final_statement += (
            "The system CAN be executed as intended by its author - "
            "a runnable alchemical state machine."
        )
    elif executable == "PARTIAL":
        final_statement += (
            "The system is PARTIALLY executable - some grammar rules are incomplete or ambiguous."
        )
    else:
        final_statement += (
            "The system CANNOT be reliably executed as a state machine with current analysis."
        )

    return {
        "metadata": {
            "phase": "13_SYNTHESIS",
            "title": "Semantic State Machine Characterization",
            "timestamp": datetime.now().isoformat()
        },
        "SEMANTIC_STATE_MACHINE": {
            "state_space": {
                "stable_states": state_count,
                "dimensionality": dimensionality,
                "structure": structure_type,
                "matches_tria_prima": result_13d.get('MATCHES_TRIA_PRIMA', 'N/A'),
                "matches_elemental": result_13d.get('MATCHES_ELEMENTAL', 'N/A')
            },
            "transition_grammar": {
                "reversible_pairs": reversible_pairs,
                "forbidden_transitions": forbidden_count,
                "purification_signature": purification_sig
            },
            "quantitative_depth": {
                "differentiation": differentiation,
                "processing_levels": len(result_13c.get('state_ordering', {}).get('by_processing_depth', []))
            },
            "executability": {
                "system_runs": executable,
                "execution_type": execution_type,
                "convergence_rate": result_13e['convergence']['converged_percent'],
                "oscillation_rate": result_13e['oscillation']['settled_to_cycle_percent']
            }
        },
        "FINAL_CHARACTERIZATION": final_statement,
        "SUCCESS_METRICS": {
            "classic_state_count_5_12": 5 <= state_count <= 12,
            "clear_transition_grammar": reversible_pairs > 5 and forbidden_count > 0,
            "quantitative_differentiation": differentiation in ["STRONG", "MODERATE"],
            "dimensional_structure_3_4": dimensionality in [3, 4] if isinstance(dimensionality, int) else False,
            "system_executable": executable in ["YES", "PARTIAL"]
        }
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute all Phase 13 tests."""
    print("=" * 70)
    print("PHASE 13: SEMANTIC STATE RECONSTRUCTION & EXECUTION TESTS")
    print("=" * 70)
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # Run Phase 13A
    result_13a = test_13a_semantic_states(entries)
    with open("phase13a_semantic_states.json", 'w') as f:
        json.dump(result_13a, f, indent=2, default=str)
    print(f"  Saved: phase13a_semantic_states.json")
    print()

    # Run Phase 13B
    result_13b = test_13b_transition_grammar(entries, result_13a)
    with open("phase13b_transition_grammar.json", 'w') as f:
        json.dump(result_13b, f, indent=2, default=str)
    print(f"  Saved: phase13b_transition_grammar.json")
    print()

    # Run Phase 13C
    result_13c = test_13c_quantitative_depth(entries, result_13a)
    with open("phase13c_quantitative_depth.json", 'w') as f:
        json.dump(result_13c, f, indent=2, default=str)
    print(f"  Saved: phase13c_quantitative_depth.json")
    print()

    # Run Phase 13D
    result_13d = test_13d_dimensionality(result_13a)
    with open("phase13d_dimensionality.json", 'w') as f:
        json.dump(result_13d, f, indent=2, default=str)
    print(f"  Saved: phase13d_dimensionality.json")
    print()

    # Run Phase 13E
    result_13e = test_13e_executability(entries, result_13a, result_13b, records)
    with open("phase13e_executability.json", 'w') as f:
        json.dump(result_13e, f, indent=2, default=str)
    print(f"  Saved: phase13e_executability.json")
    print()

    # Synthesize
    synthesis = synthesize_phase13(result_13a, result_13b, result_13c, result_13d, result_13e)
    with open("phase13_synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2, default=str)
    print(f"  Saved: phase13_synthesis.json")
    print()

    # Print summary
    print("=" * 70)
    print("PHASE 13 RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"STABLE STATES IDENTIFIED: {result_13a['stable_states_identified']}")
    print(f"DIMENSIONALITY: {result_13d.get('optimal_dimensionality', 'N/A')}")
    print(f"STRUCTURE TYPE: {result_13d.get('structure_type', 'N/A')}")
    print()
    print(f"REVERSIBLE PAIRS: {result_13b['reversible_pairs']['count']}")
    print(f"FORBIDDEN TRANSITIONS: {result_13b['forbidden_transitions']['count']}")
    print(f"PURIFICATION SIGNATURE: {result_13b['PURIFICATION_ENGINE_SIGNATURE']}")
    print()
    print(f"QUANTITATIVE DIFFERENTIATION: {result_13c['QUANTITATIVE_DIFFERENTIATION']}")
    print()
    print(f"SYSTEM EXECUTABLE: {result_13e['SYSTEM_IS_EXECUTABLE']}")
    print(f"EXECUTION TYPE: {result_13e['EXECUTION_TYPE']}")
    print()
    print("-" * 70)
    print("FINAL CHARACTERIZATION:")
    print("-" * 70)
    print(synthesis['FINAL_CHARACTERIZATION'])
    print()
    print("SUCCESS METRICS:")
    for metric, value in synthesis['SUCCESS_METRICS'].items():
        status = "PASS" if value else "FAIL"
        print(f"  {metric}: {status}")

if __name__ == "__main__":
    main()
