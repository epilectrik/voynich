#!/usr/bin/env python3
"""
Phase 10-11: Alchemical Operation & Quantitative Semantics
==========================================================

Phase 10: Alchemical Operation Semantics
- 10A: Operator Behavior Clustering
- 10B: Operator Interaction Graph
- 10C: Canonical Alchemical Signature Detection
- 10D: Operation Class Formalization

Phase 11: Quantitative Semantics Probe
- 11A: Cardinality Fingerprints
- 11B: Repetition as Quantity
- 11C: Cycle Length Analysis
- 11D: A/B Population Split
- 11E: Astrology Section Geometry (Structural Only)

Ground Rules:
- Model remains frozen (no changes to roles, operators, grammar)
- No word naming (don't claim "this means sulfur")
- Behavior defines meaning (let structure speak)
- Alchemy/iatrochemistry frame only (pharmacology eliminated)
"""

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
import random

# ============================================================================
# FROZEN MODEL (from Phase 7 - NO CHANGES)
# ============================================================================

MODEL = {
    "clusters": {
        "FLEXIBLE_CORE": {"size": 35, "mean_a_ratio": 0.40},
        "DEFINITION_CORE": {"size": 25, "mean_a_ratio": 0.755},
        "EXPOSITION_CORE": {"size": 33, "mean_a_ratio": 0.122},
        "RESTRICTED_CORE": {"size": 187, "mean_a_ratio": 0.26}
    },
    "operators": {"POSITION": 6, "SCOPE": 16, "SEMANTIC": 8},
    "grammar": {"slots": 10, "rules": 11, "coverage": 0.951},
    "slot_roles": {
        0: "TOPIC_POSITION",
        1: "PRIMARY_CONTENT",
        2: "PRIMARY_CONTENT",
        3: "SECONDARY_CONTENT",
        4: "SECONDARY_CONTENT",
        5: "SECONDARY_CONTENT",
        6: "MODIFIER_POSITION",
        7: "MODIFIER_POSITION",
        8: "TERMINAL_POSITION",
        9: "TERMINAL_POSITION"
    }
}

# Known prefixes and suffixes from Phase 7
KNOWN_PREFIXES = {'qo', 'da', 'ch', 'sh', 'ok', 'ot', 'sa', 'ct', 'yk', 'yp',
                  'ar', 'ko', 'so', 'ra', 'ta', 'op', 'cf', 'fc', 'pc', 'ts',
                  'al', 'ol', 'or', 'dy', 'od', 'ke', 'am', 'lk', 'ka'}
KNOWN_SUFFIXES = {'aiin', 'ol', 'hy', 'or', 'ar', 'ey', 'edy', 'dy', 'y',
                  'al', 'eey', 'eedy', 'ain', 'in', 'an', 'am', 'o'}

# Hub headings from Phase 19
HUBS = ['tol', 'pol', 'sho', 'tor']

# ============================================================================
# CORPUS LOADING & UTILITIES
# ============================================================================

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

def assign_slot_positions(tokens: List[str]) -> List[Tuple[str, int]]:
    """Assign normalized slot positions (0-9) to tokens in an entry."""
    n = len(tokens)
    if n == 0:
        return []

    result = []
    for i, token in enumerate(tokens):
        slot = min(9, int((i / n) * 10))
        result.append((token, slot))
    return result

def get_hub_for_folio(folio: str, records: List[Dict]) -> str:
    """Get the hub association for a folio based on heading word."""
    # Simple heuristic: check if folio's first word matches a hub pattern
    for rec in records:
        if rec['folio'] == folio:
            word = rec['word'].lower()
            for hub in HUBS:
                if hub in word:
                    return hub
            break
    return "unknown"

# ============================================================================
# PHASE 10A: OPERATOR BEHAVIOR CLUSTERING
# ============================================================================

def test_10a_operator_clustering(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Cluster operators by behavioral properties:
    - Reversibility rate
    - Commutativity partners
    - Hub-switch effect
    - Cycle participation
    - Position bias
    """
    print("Running Phase 10A: Operator Behavior Clustering...")

    # Get unique operators (prefixes only for simplicity)
    all_prefixes = set()
    for folio, tokens in entries.items():
        for token in tokens:
            prefix = get_prefix(token)
            if prefix in KNOWN_PREFIXES:
                all_prefixes.add(prefix)

    operators = list(all_prefixes)
    print(f"  Analyzing {len(operators)} operators...")

    # Compute behavior metrics for each operator
    operator_features = {}

    # 1. Build transition data
    transitions = defaultdict(Counter)  # prefix -> next prefix counts
    reverse_transitions = defaultdict(Counter)  # prefix -> prev prefix counts

    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            p1 = get_prefix(tokens[i])
            p2 = get_prefix(tokens[i + 1])
            if p1 in KNOWN_PREFIXES and p2 in KNOWN_PREFIXES:
                transitions[p1][p2] += 1
                reverse_transitions[p2][p1] += 1

    # 2. Build operator pairs for commutativity
    operator_pairs = defaultdict(lambda: {'forward': 0, 'backward': 0})
    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            p1 = get_prefix(tokens[i])
            p2 = get_prefix(tokens[i + 1])
            if p1 in KNOWN_PREFIXES and p2 in KNOWN_PREFIXES and p1 != p2:
                pair = tuple(sorted([p1, p2]))
                if p1 < p2:
                    operator_pairs[pair]['forward'] += 1
                else:
                    operator_pairs[pair]['backward'] += 1

    # 3. Hub association tracking
    folio_hubs = {}
    for rec in records:
        if rec['folio'] not in folio_hubs:
            folio_hubs[rec['folio']] = get_hub_for_folio(rec['folio'], records)

    operator_hub_counts = defaultdict(Counter)  # operator -> hub counts
    for folio, tokens in entries.items():
        hub = folio_hubs.get(folio, "unknown")
        for token in tokens:
            prefix = get_prefix(token)
            if prefix in KNOWN_PREFIXES:
                operator_hub_counts[prefix][hub] += 1

    # 4. Position distribution
    operator_positions = defaultdict(list)
    for folio, tokens in entries.items():
        slot_tokens = assign_slot_positions(tokens)
        for token, slot in slot_tokens:
            prefix = get_prefix(token)
            if prefix in KNOWN_PREFIXES:
                operator_positions[prefix].append(slot)

    # 5. Cycle detection (A->B->A patterns)
    two_step_cycles = defaultdict(int)  # (A, B) -> count of A->B->A
    for folio, tokens in entries.items():
        for i in range(len(tokens) - 2):
            p1 = get_prefix(tokens[i])
            p2 = get_prefix(tokens[i + 1])
            p3 = get_prefix(tokens[i + 2])
            if p1 in KNOWN_PREFIXES and p2 in KNOWN_PREFIXES and p3 in KNOWN_PREFIXES:
                if p1 == p3 and p1 != p2:
                    two_step_cycles[(p1, p2)] += 1

    # Now compute features for each operator
    for op in operators:
        features = {}

        # Reversibility: how often does reverse sequence (B->A) occur when A->B occurs?
        forward_total = sum(transitions[op].values())
        reverse_total = 0
        for next_op, count in transitions[op].items():
            reverse_total += reverse_transitions[op].get(next_op, 0)
        features['reversibility'] = round(reverse_total / forward_total, 3) if forward_total > 0 else 0

        # Commutativity: count of partner operators with bidirectional flow
        commutative_partners = 0
        total_partners = 0
        for pair, counts in operator_pairs.items():
            if op in pair:
                total_partners += 1
                ratio = min(counts['forward'], counts['backward']) / max(counts['forward'], counts['backward']) if max(counts['forward'], counts['backward']) > 0 else 0
                if ratio > 0.3:
                    commutative_partners += 1
        features['commutativity_rate'] = round(commutative_partners / total_partners, 3) if total_partners > 0 else 0

        # Hub association
        hub_counts = operator_hub_counts[op]
        total_hub = sum(hub_counts.values())
        dominant_hub = hub_counts.most_common(1)[0][0] if hub_counts else "unknown"
        dominant_hub_rate = hub_counts.most_common(1)[0][1] / total_hub if total_hub > 0 and hub_counts else 0
        features['dominant_hub'] = dominant_hub
        features['hub_concentration'] = round(dominant_hub_rate, 3)

        # Hub-switch: does this operator tend to appear when hub changes?
        hub_switch_count = 0
        same_hub_count = 0
        for folio, tokens in list(entries.items())[:100]:  # Sample
            hub = folio_hubs.get(folio, "unknown")
            for token in tokens:
                if get_prefix(token) == op:
                    # Check if previous token had different hub association
                    same_hub_count += 1  # Simplified - count occurrences
        features['occurrence_count'] = same_hub_count

        # Position bias
        positions = operator_positions[op]
        if positions:
            mean_pos = sum(positions) / len(positions)
            features['mean_position'] = round(mean_pos, 2)
            features['position_bias'] = "initial" if mean_pos < 3.5 else ("terminal" if mean_pos > 6.5 else "middle")

            # Entry-initial rate (slot 0)
            initial_count = sum(1 for p in positions if p == 0)
            features['entry_initial_rate'] = round(initial_count / len(positions), 3)

            # Entry-terminal rate (slots 8-9)
            terminal_count = sum(1 for p in positions if p >= 8)
            features['entry_terminal_rate'] = round(terminal_count / len(positions), 3)
        else:
            features['mean_position'] = 5.0
            features['position_bias'] = "unknown"
            features['entry_initial_rate'] = 0
            features['entry_terminal_rate'] = 0

        # Cycle participation
        cycle_count = sum(count for (a, b), count in two_step_cycles.items() if a == op or b == op)
        features['cycle_participation'] = cycle_count

        operator_features[op] = features

    # Cluster operators by behavior
    clusters = cluster_operators_by_behavior(operator_features)

    return {
        "metadata": {
            "phase": "10A",
            "title": "Operator Behavior Clustering",
            "timestamp": datetime.now().isoformat()
        },
        "operators_analyzed": len(operators),
        "operator_features": operator_features,
        "behavior_clusters": clusters,
        "summary": {
            "cluster_count": len(clusters),
            "cluster_sizes": {name: len(members) for name, members in clusters.items()},
            "high_reversibility_operators": [op for op, f in operator_features.items() if f['reversibility'] > 0.5],
            "high_commutativity_operators": [op for op, f in operator_features.items() if f['commutativity_rate'] > 0.5],
            "position_markers": [op for op, f in operator_features.items() if f['entry_initial_rate'] > 0.15]
        }
    }

def cluster_operators_by_behavior(features: Dict) -> Dict:
    """
    Simple clustering based on behavioral features.
    Uses manual thresholds to identify natural groupings.
    """
    clusters = {
        "CYCLIC_BIDIRECTIONAL": [],  # High reversibility + high commutativity
        "DIRECTIONAL_INITIATORS": [],  # High entry-initial, low reversibility
        "DIRECTIONAL_TERMINATORS": [],  # High entry-terminal
        "HUB_SHIFTERS": [],  # Strong hub concentration
        "NEUTRAL_TRANSFORMERS": [],  # Middle position, moderate everything
        "HIGH_FREQUENCY_CORES": []  # High occurrence, moderate position
    }

    for op, f in features.items():
        # Classification logic
        if f['reversibility'] > 0.4 and f['commutativity_rate'] > 0.4:
            clusters["CYCLIC_BIDIRECTIONAL"].append(op)
        elif f['entry_initial_rate'] > 0.15:
            clusters["DIRECTIONAL_INITIATORS"].append(op)
        elif f['entry_terminal_rate'] > 0.12:
            clusters["DIRECTIONAL_TERMINATORS"].append(op)
        elif f['hub_concentration'] > 0.4:
            clusters["HUB_SHIFTERS"].append(op)
        elif f['occurrence_count'] > 500:
            clusters["HIGH_FREQUENCY_CORES"].append(op)
        else:
            clusters["NEUTRAL_TRANSFORMERS"].append(op)

    # Remove empty clusters
    return {k: v for k, v in clusters.items() if v}

# ============================================================================
# PHASE 10B: OPERATOR INTERACTION GRAPH
# ============================================================================

def test_10b_operator_graph(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Build a graph of how operators transform semantic states.
    Nodes: Semantic core states (middles)
    Edges: Operator applications (directed, labeled by operator)
    """
    print("Running Phase 10B: Operator Interaction Graph...")

    # Build transition graph: middle1 --prefix--> middle2
    edges = defaultdict(lambda: defaultdict(int))  # (m1, m2) -> {prefix: count}
    node_counts = Counter()

    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            m1 = get_middle(tokens[i])
            m2 = get_middle(tokens[i + 1])
            prefix = get_prefix(tokens[i + 1])  # Operator applied to get m2

            if m1 and m2 and len(m1) > 0 and len(m2) > 0:
                edges[(m1, m2)][prefix] += 1
                node_counts[m1] += 1
                node_counts[m2] += 1

    # Compute node degrees
    out_degree = Counter()
    in_degree = Counter()

    for (m1, m2), ops in edges.items():
        total_weight = sum(ops.values())
        out_degree[m1] += total_weight
        in_degree[m2] += total_weight

    # Identify hub nodes (high traffic)
    total_nodes = len(node_counts)
    hub_threshold = sum(out_degree.values()) / total_nodes * 3 if total_nodes > 0 else 0
    hub_nodes = [n for n in node_counts if out_degree[n] + in_degree[n] > hub_threshold]

    # Identify source nodes (high out, low in)
    source_nodes = []
    for n in node_counts:
        if out_degree[n] > 0:
            ratio = out_degree[n] / (in_degree[n] + 1)
            if ratio > 2.0 and out_degree[n] > 10:
                source_nodes.append((n, round(ratio, 2)))
    source_nodes.sort(key=lambda x: -x[1])

    # Identify sink nodes (low out, high in)
    sink_nodes = []
    for n in node_counts:
        if in_degree[n] > 0:
            ratio = in_degree[n] / (out_degree[n] + 1)
            if ratio > 2.0 and in_degree[n] > 10:
                sink_nodes.append((n, round(ratio, 2)))
    sink_nodes.sort(key=lambda x: -x[1])

    # Identify attractor states (nodes that cycles collapse into)
    # These are nodes with high in-degree from diverse sources
    attractor_candidates = []
    for n in node_counts:
        if in_degree[n] > 20:
            # Count unique sources
            sources = set()
            for (m1, m2), ops in edges.items():
                if m2 == n:
                    sources.add(m1)
            if len(sources) > 5:
                attractor_candidates.append((n, len(sources), in_degree[n]))
    attractor_candidates.sort(key=lambda x: (-x[1], -x[2]))

    # Edge statistics
    total_edges = len(edges)
    total_weight = sum(sum(ops.values()) for ops in edges.values())

    return {
        "metadata": {
            "phase": "10B",
            "title": "Operator Interaction Graph",
            "timestamp": datetime.now().isoformat()
        },
        "graph_statistics": {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "total_edge_weight": total_weight,
            "mean_out_degree": round(sum(out_degree.values()) / len(out_degree), 2) if out_degree else 0,
            "mean_in_degree": round(sum(in_degree.values()) / len(in_degree), 2) if in_degree else 0
        },
        "hub_nodes": {
            "count": len(hub_nodes),
            "examples": hub_nodes[:20]
        },
        "source_nodes": {
            "count": len(source_nodes),
            "top_10": source_nodes[:10]
        },
        "sink_nodes": {
            "count": len(sink_nodes),
            "top_10": sink_nodes[:10]
        },
        "attractor_states": {
            "count": len(attractor_candidates),
            "top_10": [(n, sources, indeg) for n, sources, indeg in attractor_candidates[:10]]
        },
        "top_transitions": get_top_transitions(edges, 20)
    }

def get_top_transitions(edges: Dict, n: int = 20) -> List:
    """Get top N most frequent transitions."""
    all_transitions = []
    for (m1, m2), ops in edges.items():
        total = sum(ops.values())
        dominant_op = max(ops.items(), key=lambda x: x[1])[0] if ops else "?"
        all_transitions.append({
            "from": m1,
            "to": m2,
            "weight": total,
            "dominant_operator": dominant_op
        })

    all_transitions.sort(key=lambda x: -x['weight'])
    return all_transitions[:n]

# ============================================================================
# PHASE 10C: ALCHEMICAL SIGNATURE DETECTION
# ============================================================================

def test_10c_alchemical_signatures(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Search for specific patterns that characterize alchemical transformation grammars.
    """
    print("Running Phase 10C: Alchemical Signature Detection...")

    # Pattern 1: Short Cycles (A -> B -> A)
    short_cycles = find_short_cycles(entries)

    # Pattern 2: Ladders Collapsing to Cycles
    ladder_cycles = find_ladder_to_cycle_patterns(entries)

    # Pattern 3: Hub Attractor States
    attractors = find_attractor_states(entries)

    # Pattern 4: Reversible Pairs
    reversible_pairs = find_reversible_pairs(entries)

    # Calculate signature match strength
    signature_scores = {
        "short_cycles": 1.0 if short_cycles['count'] > 100 else (0.5 if short_cycles['count'] > 20 else 0.0),
        "ladder_to_cycle": 1.0 if ladder_cycles['count'] > 50 else (0.5 if ladder_cycles['count'] > 10 else 0.0),
        "attractor_states": 1.0 if attractors['convergence_rate'] > 0.3 else (0.5 if attractors['convergence_rate'] > 0.1 else 0.0),
        "reversible_pairs": 1.0 if reversible_pairs['rate'] > 0.4 else (0.5 if reversible_pairs['rate'] > 0.2 else 0.0)
    }

    total_score = sum(signature_scores.values()) / 4
    signature_match = "STRONG" if total_score > 0.7 else ("MODERATE" if total_score > 0.4 else "WEAK")

    return {
        "metadata": {
            "phase": "10C",
            "title": "Alchemical Signature Detection",
            "timestamp": datetime.now().isoformat()
        },
        "patterns": {
            "short_cycles": short_cycles,
            "ladder_to_cycle": ladder_cycles,
            "attractor_states": attractors,
            "reversible_pairs": reversible_pairs
        },
        "signature_scores": signature_scores,
        "signature_match": signature_match,
        "total_score": round(total_score, 3),
        "interpretation": get_signature_interpretation(signature_match, signature_scores)
    }

def find_short_cycles(entries: Dict[str, List[str]]) -> Dict:
    """Find all 2-step cycles (A -> B -> A) in middle sequences."""
    cycles = Counter()

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        for i in range(len(middles) - 2):
            m1, m2, m3 = middles[i], middles[i+1], middles[i+2]
            if m1 == m3 and m1 != m2:
                cycles[(m1, m2)] += 1

    return {
        "count": len(cycles),
        "total_occurrences": sum(cycles.values()),
        "top_10": cycles.most_common(10),
        "interpretation": "oscillatory_behavior" if len(cycles) > 50 else "limited_oscillation"
    }

def find_ladder_to_cycle_patterns(entries: Dict[str, List[str]]) -> Dict:
    """Find linear chains (A->B->C->D) that eventually loop back."""
    ladder_ends = Counter()  # Track where ladders end up
    cycle_returns = 0
    total_ladders = 0

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]

        # Look for chains of 4+ unique middles
        for start in range(len(middles) - 4):
            chain = middles[start:start+4]
            if len(set(chain)) == 4:  # All unique
                total_ladders += 1
                # Check if the sequence eventually returns to an earlier state
                for j in range(start + 4, len(middles)):
                    if middles[j] in chain:
                        cycle_returns += 1
                        break

    return {
        "total_ladders": total_ladders,
        "count": cycle_returns,
        "cycle_return_rate": round(cycle_returns / total_ladders, 3) if total_ladders > 0 else 0,
        "interpretation": "ladders_collapse_to_cycles" if cycle_returns / total_ladders > 0.3 else "linear_progression"
    }

def find_attractor_states(entries: Dict[str, List[str]]) -> Dict:
    """Find nodes that multiple transformation paths converge on."""
    # Count how many unique predecessors each middle has
    predecessors = defaultdict(set)
    total_transitions = 0

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]
        for i in range(len(middles) - 1):
            predecessors[middles[i + 1]].add(middles[i])
            total_transitions += 1

    # Find middles with high convergence (many predecessors)
    convergent_nodes = []
    for middle, preds in predecessors.items():
        if len(preds) > 10:
            convergent_nodes.append((middle, len(preds)))

    convergent_nodes.sort(key=lambda x: -x[1])

    # Convergence rate: what fraction of transitions go to high-convergence nodes?
    high_convergence_middles = set(n for n, _ in convergent_nodes[:20])
    convergent_transitions = sum(1 for folio, tokens in entries.items()
                                  for i in range(len(tokens) - 1)
                                  if get_middle(tokens[i + 1]) in high_convergence_middles)

    convergence_rate = convergent_transitions / total_transitions if total_transitions > 0 else 0

    return {
        "count": len(convergent_nodes),
        "top_attractors": convergent_nodes[:10],
        "convergence_rate": round(convergence_rate, 3),
        "interpretation": "strong_attractors" if convergence_rate > 0.2 else "distributed_flow"
    }

def find_reversible_pairs(entries: Dict[str, List[str]]) -> Dict:
    """Identify operator pairs that consistently reverse each other."""
    # Count A->B and B->A for prefix pairs
    pair_directions = defaultdict(lambda: {'forward': 0, 'backward': 0})

    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            p1 = get_prefix(tokens[i])
            p2 = get_prefix(tokens[i + 1])
            if p1 in KNOWN_PREFIXES and p2 in KNOWN_PREFIXES and p1 != p2:
                pair = tuple(sorted([p1, p2]))
                if p1 < p2:
                    pair_directions[pair]['forward'] += 1
                else:
                    pair_directions[pair]['backward'] += 1

    # Find reversible pairs (both directions appear with similar frequency)
    reversible = []
    total_pairs = 0

    for pair, counts in pair_directions.items():
        if counts['forward'] > 5 and counts['backward'] > 5:
            total_pairs += 1
            ratio = min(counts['forward'], counts['backward']) / max(counts['forward'], counts['backward'])
            if ratio > 0.3:
                reversible.append((pair, round(ratio, 2), counts['forward'], counts['backward']))

    reversible.sort(key=lambda x: -x[1])

    return {
        "total_pairs_tested": total_pairs,
        "reversible_count": len(reversible),
        "rate": round(len(reversible) / total_pairs, 3) if total_pairs > 0 else 0,
        "top_reversible": reversible[:10],
        "interpretation": "paired_operations" if len(reversible) / total_pairs > 0.3 else "directional_operations"
    }

def get_signature_interpretation(match: str, scores: Dict) -> str:
    """Interpret the alchemical signature match."""
    if match == "STRONG":
        return ("System exhibits strong alchemical transformation signatures: "
                "cyclical processes, ladder-to-cycle collapse, attractor states, and reversible pairs. "
                "Consistent with medieval alchemical operation grammar.")
    elif match == "MODERATE":
        return ("System shows partial alchemical signatures. "
                "Some cyclic behavior and reversibility present, but not dominant. "
                "May indicate hybrid system or specific alchemical sub-tradition.")
    else:
        return ("Weak alchemical signatures. Pattern detection does not strongly support "
                "cyclical transformation grammar. May require different analytical frame.")

# ============================================================================
# PHASE 10D: OPERATION CLASS FORMALIZATION
# ============================================================================

def test_10d_operation_classes(result_10a: Dict, result_10c: Dict) -> Dict:
    """
    Formalize operation classes based on clustering and signature results.
    """
    print("Running Phase 10D: Operation Class Formalization...")

    clusters = result_10a['behavior_clusters']
    features = result_10a['operator_features']

    operation_classes = {}

    for cluster_name, members in clusters.items():
        if not members:
            continue

        # Aggregate features for cluster
        cluster_features = {
            'reversibility': [],
            'commutativity_rate': [],
            'mean_position': [],
            'entry_initial_rate': [],
            'entry_terminal_rate': [],
            'cycle_participation': []
        }

        hub_counts = Counter()

        for op in members:
            if op in features:
                f = features[op]
                for key in cluster_features:
                    if key in f:
                        cluster_features[key].append(f[key])
                if 'dominant_hub' in f:
                    hub_counts[f['dominant_hub']] += 1

        # Compute cluster statistics
        stats = {}
        for key, values in cluster_features.items():
            if values:
                stats[f'mean_{key}'] = round(sum(values) / len(values), 3)

        # Determine behavior type
        behavior_type = determine_behavior_type(cluster_name, stats)
        hub_effect = "shifting" if hub_counts and max(hub_counts.values()) / len(members) > 0.5 else "stable"
        typical_position = determine_typical_position(stats)
        reversibility_level = "high" if stats.get('mean_reversibility', 0) > 0.4 else (
            "medium" if stats.get('mean_reversibility', 0) > 0.2 else "low")

        # Determine cycle role
        cycle_role = determine_cycle_role(cluster_name, stats)

        operation_classes[cluster_name] = {
            "member_operators": members,
            "member_count": len(members),
            "statistics": stats,
            "behavior_type": behavior_type,
            "hub_effect": hub_effect,
            "dominant_hub": hub_counts.most_common(1)[0][0] if hub_counts else "mixed",
            "typical_position": typical_position,
            "reversibility": reversibility_level,
            "cycle_role": cycle_role,
            "structural_meaning": generate_structural_meaning(cluster_name, behavior_type, cycle_role)
        }

    # Count classes (matches alchemical operations?)
    class_count = len(operation_classes)
    classical_match = "YES" if 6 <= class_count <= 12 else "PARTIAL"

    return {
        "metadata": {
            "phase": "10D",
            "title": "Operation Class Formalization",
            "timestamp": datetime.now().isoformat()
        },
        "operation_classes": operation_classes,
        "class_count": class_count,
        "classical_operation_match": classical_match,
        "classical_interpretation": (
            f"Detected {class_count} operation classes. "
            f"{'Matches' if classical_match == 'YES' else 'Partially matches'} "
            "classical alchemical operation count (typically 7-12 operations)."
        )
    }

def determine_behavior_type(cluster_name: str, stats: Dict) -> str:
    """Determine the behavior type for a cluster."""
    if 'CYCLIC' in cluster_name or stats.get('mean_reversibility', 0) > 0.35:
        return "cyclic"
    elif 'INITIATOR' in cluster_name or 'TERMINATOR' in cluster_name:
        return "directional"
    else:
        return "neutral"

def determine_typical_position(stats: Dict) -> str:
    """Determine typical position based on statistics."""
    mean_pos = stats.get('mean_mean_position', 5.0)
    initial_rate = stats.get('mean_entry_initial_rate', 0)
    terminal_rate = stats.get('mean_entry_terminal_rate', 0)

    if initial_rate > 0.12 or mean_pos < 4.0:
        return "initial"
    elif terminal_rate > 0.10 or mean_pos > 6.0:
        return "terminal"
    else:
        return "middle"

def determine_cycle_role(cluster_name: str, stats: Dict) -> str:
    """Determine the role in transformation cycles."""
    if 'INITIATOR' in cluster_name:
        return "initiator"
    elif 'TERMINATOR' in cluster_name:
        return "terminator"
    elif 'CYCLIC' in cluster_name:
        return "oscillator"
    elif stats.get('mean_cycle_participation', 0) > 50:
        return "transformer"
    else:
        return "neutral"

def generate_structural_meaning(cluster_name: str, behavior_type: str, cycle_role: str) -> str:
    """Generate structural meaning description (without word guessing)."""
    meanings = {
        "CYCLIC_BIDIRECTIONAL": "Marks reversible transformation states - operations that can be undone or repeated",
        "DIRECTIONAL_INITIATORS": "Begins transformation sequences - marks entry into process",
        "DIRECTIONAL_TERMINATORS": "Completes transformation sequences - marks process conclusion",
        "HUB_SHIFTERS": "Shifts category/state association - transitions between major domains",
        "NEUTRAL_TRANSFORMERS": "General transformation markers - intermediate process steps",
        "HIGH_FREQUENCY_CORES": "Common transformational operations - fundamental process elements"
    }
    return meanings.get(cluster_name, f"Unknown cluster role ({behavior_type}, {cycle_role})")

# ============================================================================
# PHASE 11A: CARDINALITY FINGERPRINTS
# ============================================================================

def test_11a_cardinality_fingerprints(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Measure distributions and test for stable peaks at meaningful integers.
    """
    print("Running Phase 11A: Cardinality Fingerprints...")

    # Compute distributions
    slot_counts = []  # tokens per entry
    operator_counts = []  # unique operators per entry
    middle_counts = []  # unique middles per entry

    for folio, tokens in entries.items():
        if len(tokens) < 5:
            continue

        slot_counts.append(len(tokens))

        operators = set()
        middles = set()
        for t in tokens:
            operators.add(get_prefix(t))
            operators.add(get_suffix(t))
            middles.add(get_middle(t))

        operator_counts.append(len(operators))
        middle_counts.append(len(middles))

    # Test for peaks at meaningful integers
    test_integers = [2, 3, 4, 7, 8, 12, 28, 30, 40]

    def find_peaks(distribution: List[int], targets: List[int]) -> Dict:
        """Find if distribution peaks at target integers."""
        counter = Counter(distribution)
        total = len(distribution)
        mean = sum(distribution) / total if total > 0 else 0
        std = (sum((x - mean) ** 2 for x in distribution) / total) ** 0.5 if total > 0 else 1

        peaks = {}
        for target in targets:
            # Count values within range of target
            window = max(1, int(std * 0.5))
            count_at_target = sum(counter[v] for v in range(target - window, target + window + 1))
            expected = total / (max(distribution) - min(distribution) + 1) if distribution else 0
            ratio = count_at_target / expected if expected > 0 else 0

            if ratio > 1.5:  # Significantly above expected
                peaks[target] = round(ratio, 2)

        return peaks

    slot_peaks = find_peaks(slot_counts, test_integers)
    operator_peaks = find_peaks(operator_counts, test_integers)
    middle_peaks = find_peaks(middle_counts, test_integers)

    # Significant cardinalities (appearing in multiple distributions)
    all_peaks = set(slot_peaks.keys()) | set(operator_peaks.keys()) | set(middle_peaks.keys())
    significant = [p for p in all_peaks if sum([
        1 if p in slot_peaks else 0,
        1 if p in operator_peaks else 0,
        1 if p in middle_peaks else 0
    ]) >= 2]

    return {
        "metadata": {
            "phase": "11A",
            "title": "Cardinality Fingerprints",
            "timestamp": datetime.now().isoformat()
        },
        "distributions": {
            "slot_count": {
                "mean": round(sum(slot_counts) / len(slot_counts), 2) if slot_counts else 0,
                "std": round((sum((x - sum(slot_counts)/len(slot_counts))**2 for x in slot_counts)/len(slot_counts))**0.5, 2) if slot_counts else 0,
                "min": min(slot_counts) if slot_counts else 0,
                "max": max(slot_counts) if slot_counts else 0,
                "peaks": slot_peaks
            },
            "operator_count": {
                "mean": round(sum(operator_counts) / len(operator_counts), 2) if operator_counts else 0,
                "peaks": operator_peaks
            },
            "middle_count": {
                "mean": round(sum(middle_counts) / len(middle_counts), 2) if middle_counts else 0,
                "peaks": middle_peaks
            }
        },
        "significant_cardinalities": significant,
        "interpretation": interpret_cardinalities(significant)
    }

def interpret_cardinalities(significant: List[int]) -> str:
    """Interpret significant cardinalities."""
    meanings = {
        3: "tria prima (salt, sulfur, mercury)",
        4: "four elements/seasons",
        7: "planetary week/metals",
        8: "known hub count",
        12: "zodiacal year"
    }

    found = [f"{n} ({meanings.get(n, 'unknown')})" for n in significant if n in meanings]

    if found:
        return f"Significant peaks at: {', '.join(found)}. Suggests numerical encoding of alchemical concepts."
    else:
        return "No clear alignment with classical alchemical numbers detected."

# ============================================================================
# PHASE 11B: REPETITION AS QUANTITY
# ============================================================================

def test_11b_repetition_patterns(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Detect repetition of identical operator sequences as quantity encoding.
    """
    print("Running Phase 11B: Repetition as Quantity...")

    # Look for repeated operator sequences within entries
    doubled = []  # ABC-ABC patterns
    tripled = []
    n_fold = Counter()  # count by repetition factor

    for folio, tokens in entries.items():
        if len(tokens) < 6:
            continue

        # Get operator sequence (prefixes)
        ops = [get_prefix(t) for t in tokens]

        # Look for repeated subsequences of length 2-5
        for length in [2, 3, 4, 5]:
            for start in range(len(ops) - length * 2 + 1):
                seq1 = tuple(ops[start:start + length])
                seq2 = tuple(ops[start + length:start + length * 2])

                if seq1 == seq2:
                    doubled.append((folio, seq1))
                    n_fold[2] += 1

                    # Check for triple
                    if start + length * 3 <= len(ops):
                        seq3 = tuple(ops[start + length * 2:start + length * 3])
                        if seq1 == seq3:
                            tripled.append((folio, seq1))
                            n_fold[3] += 1

    # Compare A-text vs B-text
    a_doubled = 0
    b_doubled = 0

    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    for folio, _ in doubled:
        if folio_populations.get(folio) == 'A':
            a_doubled += 1
        else:
            b_doubled += 1

    return {
        "metadata": {
            "phase": "11B",
            "title": "Repetition as Quantity",
            "timestamp": datetime.now().isoformat()
        },
        "patterns": {
            "doubled_sequences": {
                "count": len(doubled),
                "examples": [(f, list(s)) for f, s in doubled[:5]]
            },
            "tripled_sequences": {
                "count": len(tripled),
                "examples": [(f, list(s)) for f, s in tripled[:5]]
            },
            "n_fold_distribution": dict(n_fold)
        },
        "population_distribution": {
            "a_text_doubled": a_doubled,
            "b_text_doubled": b_doubled,
            "ratio": round(a_doubled / b_doubled, 2) if b_doubled > 0 else "inf"
        },
        "non_random_repetition": len(doubled) > 50,
        "preferred_counts": [n for n, c in n_fold.most_common(3)],
        "interpretation": interpret_repetition(doubled, tripled, n_fold)
    }

def interpret_repetition(doubled: List, tripled: List, n_fold: Counter) -> str:
    """Interpret repetition patterns."""
    if len(doubled) > 100:
        return ("Strong repetition patterns detected. Doubled sequences are common, "
                "suggesting quantity encoding through repetition (e.g., 'do this twice').")
    elif len(doubled) > 30:
        return ("Moderate repetition patterns. Some doubled sequences found, "
                "may indicate partial quantity encoding or emphasis markers.")
    else:
        return "Limited repetition patterns. Quantity encoding through repetition is unlikely."

# ============================================================================
# PHASE 11C: CYCLE LENGTH ANALYSIS
# ============================================================================

def test_11c_cycle_lengths(entries: Dict[str, List[str]]) -> Dict:
    """
    Analyze the operator graph for preferred cycle lengths.
    """
    print("Running Phase 11C: Cycle Length Analysis...")

    # Find cycles in middle sequences
    cycle_lengths = Counter()

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]

        # For each position, find how many steps until we see a repeat
        for start in range(len(middles)):
            seen = {middles[start]: 0}
            for step in range(1, min(20, len(middles) - start)):
                m = middles[start + step]
                if m in seen:
                    cycle_len = step - seen[m]
                    if cycle_len > 0:
                        cycle_lengths[cycle_len] += 1
                    break
                seen[m] = step

    # Test alignment with known cycles
    alignments = {
        "tria_prima_3": cycle_lengths.get(3, 0),
        "elemental_4": cycle_lengths.get(4, 0),
        "planetary_7": cycle_lengths.get(7, 0),
        "zodiacal_12": cycle_lengths.get(12, 0)
    }

    total_cycles = sum(cycle_lengths.values())

    # Calculate alignment scores
    expected_per_length = total_cycles / 20 if total_cycles > 0 else 0
    alignment_scores = {}
    for name, count in alignments.items():
        score = count / expected_per_length if expected_per_length > 0 else 0
        alignment_scores[name] = round(score, 2)

    return {
        "metadata": {
            "phase": "11C",
            "title": "Cycle Length Analysis",
            "timestamp": datetime.now().isoformat()
        },
        "cycle_length_distribution": dict(cycle_lengths.most_common(15)),
        "preferred_lengths": [l for l, c in cycle_lengths.most_common(5)],
        "alignment_with_known": alignments,
        "alignment_scores": alignment_scores,
        "interpretation": interpret_cycle_alignment(alignment_scores)
    }

def interpret_cycle_alignment(scores: Dict) -> str:
    """Interpret cycle alignment scores."""
    strong = [name for name, score in scores.items() if score > 1.5]
    if strong:
        return f"Strong alignment with: {', '.join(strong)}. Cycle structure matches alchemical patterns."
    else:
        return "No strong alignment with classical alchemical cycle lengths."

# ============================================================================
# PHASE 11D: A/B POPULATION SPLIT
# ============================================================================

def test_11d_population_split(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Compare quantitative patterns between A-text and B-text.
    """
    print("Running Phase 11D: A/B Population Split...")

    # Separate by population
    a_entries = defaultdict(list)
    b_entries = defaultdict(list)

    for rec in records:
        if rec['population'] == 'A':
            a_entries[rec['folio']].append(rec['word'])
        else:
            b_entries[rec['folio']].append(rec['word'])

    def compute_stats(entry_dict: Dict) -> Dict:
        slot_counts = []
        operator_counts = []
        cycle_participation = []

        for folio, tokens in entry_dict.items():
            if len(tokens) < 5:
                continue

            slot_counts.append(len(tokens))

            operators = set()
            for t in tokens:
                operators.add(get_prefix(t))
            operator_counts.append(len(operators))

            # Count internal cycles (simplified)
            middles = [get_middle(t) for t in tokens]
            repeats = len(middles) - len(set(middles))
            cycle_participation.append(repeats)

        def mean_var(lst):
            if not lst:
                return 0, 0
            m = sum(lst) / len(lst)
            v = sum((x - m) ** 2 for x in lst) / len(lst)
            return round(m, 2), round(v, 2)

        sm, sv = mean_var(slot_counts)
        om, ov = mean_var(operator_counts)
        cm, cv = mean_var(cycle_participation)

        # Find preferred integers (modes)
        slot_mode = Counter(slot_counts).most_common(3)

        return {
            "entry_count": len(slot_counts),
            "slot_count": {"mean": sm, "variance": sv},
            "operator_count": {"mean": om, "variance": ov},
            "cycle_participation": {"mean": cm, "variance": cv},
            "preferred_integers": [s for s, _ in slot_mode]
        }

    a_stats = compute_stats(dict(a_entries))
    b_stats = compute_stats(dict(b_entries))

    # Compare variances
    a_var_total = a_stats['slot_count']['variance'] + a_stats['operator_count']['variance']
    b_var_total = b_stats['slot_count']['variance'] + b_stats['operator_count']['variance']

    a_more_fixed = a_var_total < b_var_total
    effect_size = abs(a_var_total - b_var_total) / max(a_var_total, b_var_total) if max(a_var_total, b_var_total) > 0 else 0

    return {
        "metadata": {
            "phase": "11D",
            "title": "A/B Population Quantitative Split",
            "timestamp": datetime.now().isoformat()
        },
        "a_text": a_stats,
        "b_text": b_stats,
        "comparison": {
            "a_variance_total": round(a_var_total, 2),
            "b_variance_total": round(b_var_total, 2),
            "a_more_fixed": a_more_fixed,
            "effect_size": round(effect_size, 3)
        },
        "interpretation": (
            "A-text shows lower variance (more fixed cardinalities) consistent with definitions. "
            "B-text shows higher variance consistent with procedural operations."
            if a_more_fixed else
            "B-text shows lower variance than expected. May indicate constrained procedures."
        )
    }

# ============================================================================
# PHASE 11E: ASTROLOGY SECTION GEOMETRY (Structural Only)
# ============================================================================

def test_11e_astro_geometry(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Extract quantitative structure from astrological pages - geometry only.
    (No label reading or visual interpretation)
    """
    print("Running Phase 11E: Astrology Section Geometry...")

    # Identify likely astrological folios by naming convention (f70-f73, f85-f86)
    astro_folios = []
    for folio in entries.keys():
        # Simple heuristic for astro pages
        if any(x in folio.lower() for x in ['f70', 'f71', 'f72', 'f73', 'f85', 'f86']):
            astro_folios.append(folio)

    if not astro_folios:
        # Try alternate detection based on entry structure
        for folio, tokens in entries.items():
            # Astro pages often have shorter, more structured entries
            if 20 < len(tokens) < 100:
                astro_folios.append(folio)
        astro_folios = astro_folios[:12]  # Limit sample

    # Analyze structural patterns in astro entries
    division_counts = []
    segment_patterns = []

    for folio in astro_folios:
        tokens = entries.get(folio, [])
        if not tokens:
            continue

        # Count "divisions" - sections separated by repeated tokens or pattern breaks
        middles = [get_middle(t) for t in tokens]
        unique_middles = len(set(middles))

        # Estimate divisions based on repeated patterns
        pattern_breaks = 0
        for i in range(len(middles) - 1):
            if middles[i] == middles[i + 1]:
                pattern_breaks += 1

        # Division count estimate
        divisions = max(1, pattern_breaks // 2 + 1)
        division_counts.append(divisions)

        # Segment count (unique vocabulary sections)
        segments = unique_middles // 5 if unique_middles > 5 else 1
        segment_patterns.append(segments)

    # Find common division counts
    div_counter = Counter(division_counts)
    common_divisions = [d for d, _ in div_counter.most_common(3)]

    # Alignment with semantic cycles (from 11C)
    alignment_score = sum(1 for d in common_divisions if d in [3, 4, 7, 12]) / len(common_divisions) if common_divisions else 0

    return {
        "metadata": {
            "phase": "11E",
            "title": "Astrology Section Geometry (Structural Only)",
            "timestamp": datetime.now().isoformat()
        },
        "folios_analyzed": len(astro_folios),
        "folio_list": astro_folios[:10],
        "division_counts": division_counts,
        "common_divisions": common_divisions,
        "segment_patterns": segment_patterns,
        "alignment_with_semantic_cycles": round(alignment_score, 2),
        "interpretation": (
            f"Structural analysis of {len(astro_folios)} candidate astro folios. "
            f"Common divisions: {common_divisions}. "
            f"{'Strong' if alignment_score > 0.5 else 'Weak'} alignment with semantic cycle lengths."
        )
    }

# ============================================================================
# SYNTHESIS
# ============================================================================

def synthesize_phase10(result_10a: Dict, result_10b: Dict, result_10c: Dict, result_10d: Dict) -> Dict:
    """Synthesize Phase 10 results."""
    print("Synthesizing Phase 10 results...")

    return {
        "metadata": {
            "phase": "10_SYNTHESIS",
            "title": "Alchemical Operation Semantics Synthesis",
            "timestamp": datetime.now().isoformat()
        },
        "operator_clustering": {
            "clusters_found": result_10a['summary']['cluster_count'],
            "classical_match": result_10d['classical_operation_match'],
            "high_reversibility_count": len(result_10a['summary']['high_reversibility_operators']),
            "position_markers_count": len(result_10a['summary']['position_markers'])
        },
        "graph_structure": {
            "hub_nodes": result_10b['hub_nodes']['count'],
            "attractor_states": result_10b['attractor_states']['count'],
            "source_sink_asymmetry": abs(result_10b['source_nodes']['count'] - result_10b['sink_nodes']['count'])
        },
        "alchemical_signatures": {
            "signature_match": result_10c['signature_match'],
            "total_score": result_10c['total_score'],
            "key_patterns": [k for k, v in result_10c['signature_scores'].items() if v > 0.5]
        },
        "operation_classes": {
            "count": result_10d['class_count'],
            "classical_interpretation": result_10d['classical_interpretation']
        },
        "verdict": get_phase10_verdict(result_10c['signature_match'], result_10d['class_count'])
    }

def get_phase10_verdict(signature_match: str, class_count: int) -> Dict:
    """Generate Phase 10 verdict."""
    if signature_match == "STRONG" and 6 <= class_count <= 12:
        verdict = "STRONG_ALCHEMICAL"
        confidence = "HIGH"
        interpretation = ("System exhibits strong alchemical transformation grammar: "
                         f"{class_count} operation classes with cyclical/reversible signatures.")
    elif signature_match == "MODERATE" or 5 <= class_count <= 14:
        verdict = "MODERATE_ALCHEMICAL"
        confidence = "MEDIUM"
        interpretation = ("System shows moderate alchemical characteristics. "
                         "Some patterns consistent with transformation grammar.")
    else:
        verdict = "WEAK_ALCHEMICAL"
        confidence = "LOW"
        interpretation = "Weak alchemical signatures. May require alternative analytical frame."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "interpretation": interpretation
    }

def synthesize_phase11(result_11a: Dict, result_11b: Dict, result_11c: Dict,
                       result_11d: Dict, result_11e: Dict) -> Dict:
    """Synthesize Phase 11 results."""
    print("Synthesizing Phase 11 results...")

    return {
        "metadata": {
            "phase": "11_SYNTHESIS",
            "title": "Quantitative Semantics Probe Synthesis",
            "timestamp": datetime.now().isoformat()
        },
        "cardinality_findings": {
            "significant_cardinalities": result_11a['significant_cardinalities'],
            "interpretation": result_11a['interpretation']
        },
        "repetition_findings": {
            "non_random": result_11b['non_random_repetition'],
            "preferred_counts": result_11b['preferred_counts']
        },
        "cycle_findings": {
            "preferred_lengths": result_11c['preferred_lengths'],
            "alignment_scores": result_11c['alignment_scores']
        },
        "population_split": {
            "a_more_fixed": result_11d['comparison']['a_more_fixed'],
            "effect_size": result_11d['comparison']['effect_size']
        },
        "astro_geometry": {
            "common_divisions": result_11e['common_divisions'],
            "semantic_alignment": result_11e['alignment_with_semantic_cycles']
        },
        "verdict": get_phase11_verdict(result_11a, result_11b, result_11c, result_11d)
    }

def get_phase11_verdict(r11a: Dict, r11b: Dict, r11c: Dict, r11d: Dict) -> Dict:
    """Generate Phase 11 verdict."""
    # Count strong signals
    signals = 0

    if r11a['significant_cardinalities']:
        signals += 1
    if r11b['non_random_repetition']:
        signals += 1
    if any(v > 1.5 for v in r11c['alignment_scores'].values()):
        signals += 1
    if r11d['comparison']['effect_size'] > 0.2:
        signals += 1

    if signals >= 3:
        verdict = "QUANTITATIVE_ENCODING_CONFIRMED"
        confidence = "HIGH"
    elif signals >= 2:
        verdict = "QUANTITATIVE_ENCODING_LIKELY"
        confidence = "MEDIUM"
    else:
        verdict = "QUANTITATIVE_ENCODING_WEAK"
        confidence = "LOW"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "signal_count": signals,
        "interpretation": (
            f"Detected {signals}/4 strong quantitative encoding signals. "
            f"{'Numbers are encoded behaviorally through repetition and cycle length.' if signals >= 2 else 'Limited quantitative encoding evidence.'}"
        )
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_phase10():
    """Execute all Phase 10 tests."""
    print("=" * 60)
    print("PHASE 10: ALCHEMICAL OPERATION SEMANTICS")
    print("=" * 60)
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Run tests
    result_10a = test_10a_operator_clustering(entries, records)
    print()
    result_10b = test_10b_operator_graph(entries, records)
    print()
    result_10c = test_10c_alchemical_signatures(entries, records)
    print()
    result_10d = test_10d_operation_classes(result_10a, result_10c)
    print()

    # Synthesize
    synthesis_10 = synthesize_phase10(result_10a, result_10b, result_10c, result_10d)

    # Save results
    for name, result in [
        ("phase10a_operator_clusters.json", result_10a),
        ("phase10b_operator_graph.json", result_10b),
        ("phase10c_alchemical_signatures.json", result_10c),
        ("phase10d_operation_classes.json", result_10d),
        ("phase10_synthesis.json", synthesis_10)
    ]:
        with open(name, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved: {name}")

    return result_10a, result_10b, result_10c, result_10d, synthesis_10, entries, records

def run_phase11(entries: Dict[str, List[str]], records: List[Dict]):
    """Execute all Phase 11 tests."""
    print()
    print("=" * 60)
    print("PHASE 11: QUANTITATIVE SEMANTICS PROBE")
    print("=" * 60)
    print()

    # Run tests
    result_11a = test_11a_cardinality_fingerprints(entries, records)
    print()
    result_11b = test_11b_repetition_patterns(entries, records)
    print()
    result_11c = test_11c_cycle_lengths(entries)
    print()
    result_11d = test_11d_population_split(entries, records)
    print()
    result_11e = test_11e_astro_geometry(entries, records)
    print()

    # Synthesize
    synthesis_11 = synthesize_phase11(result_11a, result_11b, result_11c, result_11d, result_11e)

    # Save results
    for name, result in [
        ("phase11a_cardinality_fingerprints.json", result_11a),
        ("phase11b_repetition_patterns.json", result_11b),
        ("phase11c_cycle_lengths.json", result_11c),
        ("phase11d_population_split.json", result_11d),
        ("phase11e_astro_geometry.json", result_11e),
        ("phase11_synthesis.json", synthesis_11)
    ]:
        with open(name, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved: {name}")

    return result_11a, result_11b, result_11c, result_11d, result_11e, synthesis_11

def print_summary(synthesis_10: Dict, synthesis_11: Dict):
    """Print final summary."""
    print()
    print("=" * 60)
    print("PHASE 10-11 COMBINED RESULTS")
    print("=" * 60)
    print()

    print("PHASE 10: ALCHEMICAL OPERATION SEMANTICS")
    print("-" * 40)
    print(f"  Operation clusters found: {synthesis_10['operator_clustering']['clusters_found']}")
    print(f"  Classical operation match: {synthesis_10['operator_clustering']['classical_match']}")
    print(f"  Alchemical signature match: {synthesis_10['alchemical_signatures']['signature_match']}")
    print(f"  Signature score: {synthesis_10['alchemical_signatures']['total_score']}")
    print()
    print(f"  VERDICT: {synthesis_10['verdict']['verdict']}")
    print(f"  Confidence: {synthesis_10['verdict']['confidence']}")
    print(f"  {synthesis_10['verdict']['interpretation']}")
    print()

    print("PHASE 11: QUANTITATIVE SEMANTICS")
    print("-" * 40)
    print(f"  Significant cardinalities: {synthesis_11['cardinality_findings']['significant_cardinalities']}")
    print(f"  Non-random repetition: {synthesis_11['repetition_findings']['non_random']}")
    print(f"  Preferred cycle lengths: {synthesis_11['cycle_findings']['preferred_lengths']}")
    print(f"  A-text more fixed: {synthesis_11['population_split']['a_more_fixed']}")
    print()
    print(f"  VERDICT: {synthesis_11['verdict']['verdict']}")
    print(f"  Confidence: {synthesis_11['verdict']['confidence']}")
    print(f"  {synthesis_11['verdict']['interpretation']}")
    print()

    print("COMBINED INTERPRETATION")
    print("-" * 40)
    if (synthesis_10['verdict']['verdict'] == "STRONG_ALCHEMICAL" and
        synthesis_11['verdict']['verdict'] == "QUANTITATIVE_ENCODING_CONFIRMED"):
        print("  The system encodes a closed algebra of material transformations")
        print("  with operation classes exhibiting strong reversibility and cyclic behavior.")
        print("  Quantitative semantics are encoded via repetition and cycle length.")
        print("  Properties uniquely match late medieval alchemical/iatrochemical grammars.")
    elif "ALCHEMICAL" in synthesis_10['verdict']['verdict']:
        print("  Partial alchemical structure detected with operation classes.")
        print("  Quantitative encoding shows mixed signals.")
        print("  May represent specific alchemical sub-tradition or hybrid system.")
    else:
        print("  Limited alchemical signatures detected.")
        print("  May require alternative analytical framework.")

def main():
    """Main entry point."""
    # Run Phase 10
    result_10a, result_10b, result_10c, result_10d, synthesis_10, entries, records = run_phase10()

    # Run Phase 11
    result_11a, result_11b, result_11c, result_11d, result_11e, synthesis_11 = run_phase11(entries, records)

    # Print combined summary
    print_summary(synthesis_10, synthesis_11)

if __name__ == "__main__":
    main()
