#!/usr/bin/env python3
"""
Phase 19: Identifier Boundary & Non-Executable Token Detection
===============================================================

Situation: Phase 18 completed the hazard model with 17 forbidden transitions
classified into 5 failure classes. The control grammar is complete.

Goal: Determine whether the system contains non-executable identifier tokens
(labels) or is purely operational.

Ground Rules:
- No linguistic interpretation - classify by behavioral role only
- No substance naming - detecting identifiers, not reading them
- Executability is the test - does removing the token change execution?
- Substitution invariance is confirmation - can it be swapped without effect?
- Both outcomes are valid - pure control system OR control + identifiers

Sub-phases:
- 19A: Executability Analysis
- 19B: Substitution Invariance Test
- 19C: Positional Rigidity Analysis
- 19D: Cardinality Constraints
- 19E: Boundary Mapping
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
# CORPUS LOADING (reuse from Phase 18)
# ============================================================================

KNOWN_PREFIXES = {'qo', 'da', 'ch', 'sh', 'ok', 'ot', 'sa', 'ct', 'yk', 'yp',
                  'ar', 'ko', 'so', 'ra', 'ta', 'op', 'cf', 'fc', 'pc', 'ts',
                  'al', 'ol', 'or', 'dy', 'od', 'ke', 'am', 'lk', 'ka'}
KNOWN_SUFFIXES = {'aiin', 'ol', 'hy', 'or', 'ar', 'ey', 'edy', 'dy', 'y',
                  'al', 'eey', 'eedy', 'ain', 'in', 'an', 'am', 'o'}

# From Phase 15/18
KERNEL_NODES = {'k', 'h', 'e'}
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

# Convert to set for fast lookup
FORBIDDEN_SET = set(FORBIDDEN_TRANSITIONS)

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

def group_by_population(records: List[Dict]) -> Dict[str, List[Dict]]:
    """Group records by A/B population."""
    populations = defaultdict(list)
    for rec in records:
        populations[rec['population']].append(rec)
    return dict(populations)

# ============================================================================
# BUILD STATE INFRASTRUCTURE
# ============================================================================

def load_phase13_states() -> Dict:
    """Load Phase 13 state assignments."""
    with open("phase13a_semantic_states.json", 'r') as f:
        return json.load(f)

def build_node_to_state(states_result: Dict) -> Dict[str, str]:
    """Build node-to-state mapping."""
    node_to_state = {}
    for state_name, state_data in states_result['states'].items():
        for node in state_data['member_nodes']:
            node_to_state[node] = state_name
    return node_to_state

def build_transition_graph(entries: Dict[str, List[str]]) -> Dict[str, Dict[str, int]]:
    """Build transition graph from corpus."""
    graph = defaultdict(lambda: defaultdict(int))

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]

        for i in range(len(middles) - 1):
            m1, m2 = middles[i], middles[i + 1]
            if m1 and m2:
                graph[m1][m2] += 1

    return dict(graph)

# ============================================================================
# EXECUTION SIMULATION
# ============================================================================

def simulate_execution(trace: List[str], graph: Dict, max_steps: int = 100) -> Dict:
    """
    Simulate execution of a trace through the graph.
    Returns convergence info and hazard violations.
    """
    if not trace:
        return {'converged': False, 'steps': 0, 'cycle': None, 'violations': 0}

    current = trace[0]
    visited = [current]
    violations = 0

    for i in range(1, min(len(trace), max_steps)):
        next_token = trace[i]

        # Check for forbidden transition
        if (current, next_token) in FORBIDDEN_SET:
            violations += 1

        visited.append(next_token)
        current = next_token

    # Check for cycle at end
    cycle_length = 0
    if len(visited) >= 4:
        for cycle_len in range(1, min(5, len(visited) // 2)):
            if visited[-cycle_len:] == visited[-2*cycle_len:-cycle_len]:
                cycle_length = cycle_len
                break

    converged = cycle_length > 0 or len(set(visited[-5:])) <= 2

    return {
        'converged': converged,
        'steps': len(visited),
        'cycle': cycle_length,
        'violations': violations,
        'final_node': current
    }

def simulate_with_removal(trace: List[str], remove_token: str, graph: Dict) -> Dict:
    """Simulate execution with a specific token removed from trace."""
    filtered = [t for t in trace if get_middle(t) != remove_token]
    if len(filtered) < 2:
        return {'converged': False, 'steps': 0, 'cycle': 0, 'violations': 0}
    return simulate_execution(filtered, graph)

def simulate_with_substitution(trace: List[str], old_token: str, new_token: str, graph: Dict) -> Dict:
    """Simulate execution with one token substituted for another."""
    substituted = []
    for t in trace:
        if get_middle(t) == old_token:
            # Reconstruct token with same affixes but different middle
            prefix = get_prefix(t)
            suffix = get_suffix(t)
            if prefix in KNOWN_PREFIXES or suffix in KNOWN_SUFFIXES:
                substituted.append(prefix + new_token + suffix)
            else:
                substituted.append(new_token)
        else:
            substituted.append(t)
    return simulate_execution(substituted, graph)

# ============================================================================
# PHASE 19A: EXECUTABILITY ANALYSIS
# ============================================================================

def phase19a_executability_analysis(entries: Dict[str, List[str]],
                                     records: List[Dict],
                                     graph: Dict) -> Dict:
    """
    Identify tokens whose removal does NOT alter execution behavior.
    """
    print("Running Phase 19A: Executability Analysis...")

    # Get all unique middles
    all_middles = Counter()
    for folio, tokens in entries.items():
        for t in tokens:
            m = get_middle(t)
            if m:
                all_middles[m] += 1

    # Focus on tokens with sufficient frequency (at least 20 occurrences)
    frequent_tokens = [m for m, count in all_middles.items() if count >= 20]
    print(f"  Testing {len(frequent_tokens)} frequent tokens...")

    # Sample traces for testing
    sample_entries = list(entries.items())[:200]  # Use first 200 entries

    # Baseline execution metrics
    baseline_results = []
    for folio, tokens in sample_entries:
        if len(tokens) >= 5:
            result = simulate_execution([get_middle(t) for t in tokens], graph)
            baseline_results.append(result)

    if not baseline_results:
        return {'error': 'No valid traces for testing'}

    baseline_convergence = sum(1 for r in baseline_results if r['converged']) / len(baseline_results)
    baseline_cycles = sum(r['cycle'] for r in baseline_results) / len(baseline_results)
    baseline_violations = sum(r['violations'] for r in baseline_results)

    print(f"  Baseline: {baseline_convergence:.1%} convergence, {baseline_cycles:.2f} avg cycle, {baseline_violations} violations")

    # Test each token for removal impact
    token_impacts = []

    for token in frequent_tokens:
        removal_results = []

        for folio, tokens in sample_entries:
            if len(tokens) >= 5:
                result = simulate_with_removal(tokens, token, graph)
                removal_results.append(result)

        if removal_results:
            removal_convergence = sum(1 for r in removal_results if r['converged']) / len(removal_results)
            removal_cycles = sum(r['cycle'] for r in removal_results) / len(removal_results)
            removal_violations = sum(r['violations'] for r in removal_results)

            convergence_delta = abs(removal_convergence - baseline_convergence)
            cycle_delta = abs(removal_cycles - baseline_cycles)
            violation_delta = abs(removal_violations - baseline_violations)

            # Classification
            if convergence_delta > 0.05 or violation_delta > 0:
                classification = 'EXECUTABLE'
            elif convergence_delta < 0.02 and violation_delta == 0:
                classification = 'NON_EXECUTABLE'
            else:
                classification = 'AMBIGUOUS'

            token_impacts.append({
                'token': token,
                'frequency': all_middles[token],
                'convergence_delta': round(convergence_delta, 4),
                'cycle_delta': round(cycle_delta, 4),
                'violation_delta': violation_delta,
                'classification': classification
            })

    # Sort by frequency
    token_impacts.sort(key=lambda x: x['frequency'], reverse=True)

    # Count classifications
    classification_counts = Counter(t['classification'] for t in token_impacts)

    # Identify non-executable candidates
    non_executable = [t for t in token_impacts if t['classification'] == 'NON_EXECUTABLE']
    ambiguous = [t for t in token_impacts if t['classification'] == 'AMBIGUOUS']
    executable = [t for t in token_impacts if t['classification'] == 'EXECUTABLE']

    # Determine identifier signal strength
    non_exec_ratio = len(non_executable) / len(token_impacts) if token_impacts else 0
    if non_exec_ratio > 0.15:
        identifier_signal = 'STRONG'
    elif non_exec_ratio > 0.05:
        identifier_signal = 'WEAK'
    else:
        identifier_signal = 'NONE'

    result = {
        'metadata': {
            'phase': '19A',
            'title': 'Executability Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'tokens_tested': len(token_impacts),
        'baseline': {
            'convergence_rate': round(baseline_convergence, 4),
            'mean_cycle_length': round(baseline_cycles, 4),
            'total_violations': baseline_violations
        },
        'classification': {
            'EXECUTABLE': classification_counts.get('EXECUTABLE', 0),
            'NON_EXECUTABLE': classification_counts.get('NON_EXECUTABLE', 0),
            'AMBIGUOUS': classification_counts.get('AMBIGUOUS', 0)
        },
        'non_executable_candidates': non_executable[:30],  # Top 30
        'ambiguous_candidates': ambiguous[:20],
        'sample_executable': executable[:10],
        'IDENTIFIER_SIGNAL': identifier_signal,
        'INTERPRETATION': f"Of {len(token_impacts)} tokens tested, {len(non_executable)} ({non_exec_ratio:.1%}) show non-executable behavior. Identifier signal: {identifier_signal}."
    }

    return result

# ============================================================================
# PHASE 19B: SUBSTITUTION INVARIANCE TEST
# ============================================================================

def phase19b_substitution_invariance(entries: Dict[str, List[str]],
                                      non_executable_candidates: List[Dict],
                                      graph: Dict) -> Dict:
    """
    Confirm identifier candidates by testing substitution invariance.
    """
    print("Running Phase 19B: Substitution Invariance Test...")

    if not non_executable_candidates:
        return {
            'metadata': {'phase': '19B', 'title': 'Substitution Invariance Test',
                        'timestamp': datetime.now().isoformat()},
            'candidates_tested': 0,
            'invariant_pairs': [],
            'IDENTIFIER_CONFIRMATION': 'NO_CANDIDATES'
        }

    # Get candidate tokens
    candidates = [c['token'] for c in non_executable_candidates[:20]]

    # Sample traces
    sample_entries = list(entries.items())[:150]

    # Test pairwise substitution
    invariant_pairs = []
    partial_pairs = []

    for i, token_a in enumerate(candidates):
        for token_b in candidates[i+1:]:
            # Test A -> B substitution
            results_ab = []
            results_ba = []

            for folio, tokens in sample_entries:
                if len(tokens) >= 5:
                    orig_middles = [get_middle(t) for t in tokens]

                    # Only test if tokens appear in trace
                    if token_a in orig_middles or token_b in orig_middles:
                        orig_result = simulate_execution(orig_middles, graph)

                        # A -> B
                        if token_a in orig_middles:
                            sub_result = simulate_with_substitution(tokens, token_a, token_b, graph)
                            results_ab.append({
                                'orig_converged': orig_result['converged'],
                                'sub_converged': sub_result['converged'],
                                'orig_violations': orig_result['violations'],
                                'sub_violations': sub_result['violations']
                            })

                        # B -> A
                        if token_b in orig_middles:
                            sub_result = simulate_with_substitution(tokens, token_b, token_a, graph)
                            results_ba.append({
                                'orig_converged': orig_result['converged'],
                                'sub_converged': sub_result['converged'],
                                'orig_violations': orig_result['violations'],
                                'sub_violations': sub_result['violations']
                            })

            # Evaluate invariance
            if results_ab and results_ba:
                ab_invariant = all(r['orig_converged'] == r['sub_converged'] and
                                  r['orig_violations'] == r['sub_violations']
                                  for r in results_ab)
                ba_invariant = all(r['orig_converged'] == r['sub_converged'] and
                                  r['orig_violations'] == r['sub_violations']
                                  for r in results_ba)

                if ab_invariant and ba_invariant:
                    invariant_pairs.append({
                        'token_a': token_a,
                        'token_b': token_b,
                        'tests_ab': len(results_ab),
                        'tests_ba': len(results_ba),
                        'mutual_invariance': True
                    })
                elif ab_invariant or ba_invariant:
                    partial_pairs.append({
                        'token_a': token_a,
                        'token_b': token_b,
                        'ab_invariant': ab_invariant,
                        'ba_invariant': ba_invariant
                    })

    # Build invariance classes (tokens that are mutually substitutable)
    invariance_classes = []
    used_tokens = set()

    for pair in invariant_pairs:
        a, b = pair['token_a'], pair['token_b']
        added = False
        for cls in invariance_classes:
            if a in cls or b in cls:
                cls.add(a)
                cls.add(b)
                added = True
                break
        if not added:
            invariance_classes.append({a, b})
        used_tokens.add(a)
        used_tokens.add(b)

    # Convert sets to lists for JSON
    invariance_classes = [list(cls) for cls in invariance_classes]

    # Determine confirmation level
    if len(invariant_pairs) >= 5:
        confirmation = 'CONFIRMED'
    elif len(invariant_pairs) > 0 or len(partial_pairs) >= 3:
        confirmation = 'PARTIAL'
    else:
        confirmation = 'REJECTED'

    result = {
        'metadata': {
            'phase': '19B',
            'title': 'Substitution Invariance Test',
            'timestamp': datetime.now().isoformat()
        },
        'candidates_tested': len(candidates),
        'pairs_tested': len(candidates) * (len(candidates) - 1) // 2,
        'invariant_pairs': invariant_pairs,
        'partial_pairs': partial_pairs[:10],
        'invariance_classes': invariance_classes,
        'fully_invariant_tokens': list(used_tokens),
        'IDENTIFIER_CONFIRMATION': confirmation,
        'INTERPRETATION': f"{len(invariant_pairs)} mutually invariant pairs found among {len(candidates)} candidates. {len(invariance_classes)} equivalence classes identified. Confirmation: {confirmation}."
    }

    return result

# ============================================================================
# PHASE 19C: POSITIONAL RIGIDITY ANALYSIS
# ============================================================================

def phase19c_positional_rigidity(entries: Dict[str, List[str]],
                                  candidates: List[str],
                                  kernel_nodes: Set[str]) -> Dict:
    """
    Detect reference-like behavior through positional constraints.
    """
    print("Running Phase 19C: Positional Rigidity Analysis...")

    # Compute positional distributions for each candidate
    positional_data = {}

    for token in candidates:
        positions = []
        predecessors = Counter()
        successors = Counter()
        kernel_distances = []

        for folio, tokens in entries.items():
            middles = [get_middle(t) for t in tokens]

            for i, m in enumerate(middles):
                if m == token:
                    # Record position (normalized by entry length)
                    positions.append(i / len(middles) if middles else 0)

                    # Record neighbors
                    if i > 0:
                        predecessors[middles[i-1]] += 1
                    if i < len(middles) - 1:
                        successors[middles[i+1]] += 1

                    # Compute minimum distance to kernel
                    min_dist = float('inf')
                    for j, m2 in enumerate(middles):
                        if m2 in kernel_nodes:
                            min_dist = min(min_dist, abs(i - j))
                    if min_dist != float('inf'):
                        kernel_distances.append(min_dist)

        if positions:
            # Calculate position entropy
            pos_bins = [0] * 10
            for p in positions:
                bin_idx = min(int(p * 10), 9)
                pos_bins[bin_idx] += 1

            total = sum(pos_bins)
            pos_entropy = 0
            for count in pos_bins:
                if count > 0:
                    p = count / total
                    pos_entropy -= p * math.log2(p)

            # Calculate adjacency entropy
            def calc_entropy(counter):
                total = sum(counter.values())
                if total == 0:
                    return 0
                ent = 0
                for count in counter.values():
                    if count > 0:
                        p = count / total
                        ent -= p * math.log2(p)
                return ent

            pred_entropy = calc_entropy(predecessors)
            succ_entropy = calc_entropy(successors)
            adjacency_entropy = (pred_entropy + succ_entropy) / 2

            # Classification
            # Low entropy = more rigid/fixed = reference-like
            if pos_entropy < 2.5 and adjacency_entropy < 3.0:
                classification = 'REFERENCE_LIKE'
            elif pos_entropy > 3.0 or adjacency_entropy > 4.0:
                classification = 'OPERATIONAL'
            else:
                classification = 'MIXED'

            positional_data[token] = {
                'occurrences': len(positions),
                'positional_entropy': round(pos_entropy, 3),
                'adjacency_entropy': round(adjacency_entropy, 3),
                'kernel_distance_mean': round(np.mean(kernel_distances), 2) if kernel_distances else None,
                'position_mean': round(np.mean(positions), 3),
                'position_std': round(np.std(positions), 3),
                'top_predecessors': dict(predecessors.most_common(3)),
                'top_successors': dict(successors.most_common(3)),
                'classification': classification
            }

    # Separate by classification
    reference_like = {k: v for k, v in positional_data.items() if v['classification'] == 'REFERENCE_LIKE'}
    operational = {k: v for k, v in positional_data.items() if v['classification'] == 'OPERATIONAL'}
    mixed = {k: v for k, v in positional_data.items() if v['classification'] == 'MIXED'}

    # Determine signal strength
    ref_ratio = len(reference_like) / len(positional_data) if positional_data else 0
    if ref_ratio > 0.3:
        signal = 'STRONG'
    elif ref_ratio > 0.1:
        signal = 'WEAK'
    else:
        signal = 'NONE'

    result = {
        'metadata': {
            'phase': '19C',
            'title': 'Positional Rigidity Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'candidates_analyzed': len(positional_data),
        'classification_counts': {
            'REFERENCE_LIKE': len(reference_like),
            'OPERATIONAL': len(operational),
            'MIXED': len(mixed)
        },
        'reference_like_tokens': reference_like,
        'operational_tokens': dict(list(operational.items())[:10]),
        'mixed_tokens': dict(list(mixed.items())[:10]),
        'POSITIONAL_SIGNAL': signal,
        'INTERPRETATION': f"{len(reference_like)} tokens show reference-like positional rigidity out of {len(positional_data)} analyzed ({ref_ratio:.1%}). Signal: {signal}."
    }

    return result

# ============================================================================
# PHASE 19D: CARDINALITY CONSTRAINTS
# ============================================================================

def phase19d_cardinality_constraints(entries: Dict[str, List[str]],
                                      records: List[Dict],
                                      candidates: List[str]) -> Dict:
    """
    Test whether identifier candidates show identifier-typical cardinality patterns.
    """
    print("Running Phase 19D: Cardinality Constraints...")

    # Group by population
    populations = group_by_population(records)
    a_folios = set(r['folio'] for r in populations.get('A', []))
    b_folios = set(r['folio'] for r in populations.get('B', []))

    cardinality_data = {}

    for token in candidates:
        per_trace_counts = []
        a_count = 0
        b_count = 0

        for folio, tokens in entries.items():
            middles = [get_middle(t) for t in tokens]
            token_count = middles.count(token)

            if token_count > 0:
                per_trace_counts.append(token_count)

                if folio in a_folios:
                    a_count += token_count
                elif folio in b_folios:
                    b_count += token_count

        if per_trace_counts:
            max_per_trace = max(per_trace_counts)
            typical_per_trace = np.median(per_trace_counts)
            total_occurrences = sum(per_trace_counts)

            # A-text ratio
            a_ratio = a_count / (a_count + b_count) if (a_count + b_count) > 0 else 0.5

            # Repetition sensitivity proxy:
            # If max >> typical, likely repetition-sensitive (operational)
            # If max ~ typical, likely repetition-insensitive (identifier)
            rep_ratio = max_per_trace / typical_per_trace if typical_per_trace > 0 else 1
            repetition_sensitive = rep_ratio > 3

            # Classification
            # Identifier-like: low max, not repetition-sensitive, A-biased
            if max_per_trace <= 3 and not repetition_sensitive and a_ratio > 0.5:
                classification = 'IDENTIFIER_LIKE'
            elif max_per_trace > 5 or repetition_sensitive:
                classification = 'OPERATIONAL'
            else:
                classification = 'AMBIGUOUS'

            cardinality_data[token] = {
                'total_occurrences': total_occurrences,
                'traces_present': len(per_trace_counts),
                'max_per_trace': max_per_trace,
                'typical_per_trace': round(typical_per_trace, 2),
                'repetition_ratio': round(rep_ratio, 2),
                'repetition_sensitive': repetition_sensitive,
                'a_text_count': a_count,
                'b_text_count': b_count,
                'a_text_ratio': round(a_ratio, 3),
                'classification': classification
            }

    # Count classifications
    identifier_like = {k: v for k, v in cardinality_data.items() if v['classification'] == 'IDENTIFIER_LIKE'}
    operational = {k: v for k, v in cardinality_data.items() if v['classification'] == 'OPERATIONAL'}
    ambiguous = {k: v for k, v in cardinality_data.items() if v['classification'] == 'AMBIGUOUS'}

    # Determine signal strength
    id_ratio = len(identifier_like) / len(cardinality_data) if cardinality_data else 0
    if id_ratio > 0.3:
        signal = 'STRONG'
    elif id_ratio > 0.1:
        signal = 'WEAK'
    else:
        signal = 'NONE'

    result = {
        'metadata': {
            'phase': '19D',
            'title': 'Cardinality Constraints',
            'timestamp': datetime.now().isoformat()
        },
        'candidates_analyzed': len(cardinality_data),
        'classification_counts': {
            'IDENTIFIER_LIKE': len(identifier_like),
            'OPERATIONAL': len(operational),
            'AMBIGUOUS': len(ambiguous)
        },
        'identifier_like_tokens': identifier_like,
        'operational_tokens': dict(list(operational.items())[:10]),
        'ambiguous_tokens': dict(list(ambiguous.items())[:10]),
        'CARDINALITY_SIGNAL': signal,
        'INTERPRETATION': f"{len(identifier_like)} tokens show identifier-like cardinality patterns out of {len(cardinality_data)} analyzed ({id_ratio:.1%}). Signal: {signal}."
    }

    return result

# ============================================================================
# PHASE 19E: BOUNDARY MAPPING
# ============================================================================

def phase19e_boundary_mapping(entries: Dict[str, List[str]],
                               records: List[Dict],
                               identifier_candidates: List[str],
                               operational_tokens: List[str]) -> Dict:
    """
    Overlay identifier candidates onto manuscript structure.
    """
    print("Running Phase 19E: Boundary Mapping...")

    # Group by population
    populations = group_by_population(records)
    a_folios = set(r['folio'] for r in populations.get('A', []))
    b_folios = set(r['folio'] for r in populations.get('B', []))

    # Analyze page distribution for identifier candidates
    page_distribution = {}

    for token in identifier_candidates:
        folios_present = []

        for folio, tokens in entries.items():
            middles = [get_middle(t) for t in tokens]
            if token in middles:
                folios_present.append(folio)

        if folios_present:
            a_count = sum(1 for f in folios_present if f in a_folios)
            b_count = sum(1 for f in folios_present if f in b_folios)

            # Clustering coefficient: how concentrated is the distribution?
            unique_folios = len(set(folios_present))
            total_folios = len(entries)
            spread = unique_folios / total_folios if total_folios > 0 else 0

            page_distribution[token] = {
                'total_folios': unique_folios,
                'a_text_folios': a_count,
                'b_text_folios': b_count,
                'spread': round(spread, 3),
                'clustering_coefficient': round(1 - spread, 3)  # Higher = more clustered
            }

    # Macro-state alignment: where do identifiers appear in entries?
    macro_alignment = {
        'entry_header': [],
        'entry_middle': [],
        'entry_closure': []
    }

    for token in identifier_candidates:
        header_count = 0
        middle_count = 0
        closure_count = 0

        for folio, tokens in entries.items():
            middles = [get_middle(t) for t in tokens]
            n = len(middles)

            for i, m in enumerate(middles):
                if m == token:
                    pos = i / n if n > 0 else 0.5
                    if pos < 0.2:
                        header_count += 1
                    elif pos > 0.8:
                        closure_count += 1
                    else:
                        middle_count += 1

        total = header_count + middle_count + closure_count
        if total > 0:
            if header_count / total > 0.4:
                macro_alignment['entry_header'].append(token)
            elif closure_count / total > 0.4:
                macro_alignment['entry_closure'].append(token)
            else:
                macro_alignment['entry_middle'].append(token)

    # A-text vs B-text dominant
    a_dominant = []
    b_dominant = []

    for token, data in page_distribution.items():
        if data['a_text_folios'] > data['b_text_folios']:
            a_dominant.append(token)
        else:
            b_dominant.append(token)

    # Identify translation-eligible zones
    # Zones where identifier density is high and operational density is low
    zones = []

    for folio, tokens in entries.items():
        middles = [get_middle(t) for t in tokens]

        id_count = sum(1 for m in middles if m in identifier_candidates)
        op_count = sum(1 for m in middles if m in operational_tokens)

        if len(middles) > 0:
            id_density = id_count / len(middles)
            op_density = op_count / len(middles)

            # Translation-eligible: high identifier density, low operational
            if id_density > 0.1 and op_density < 0.3:
                zones.append({
                    'folio': folio,
                    'identifier_density': round(id_density, 3),
                    'operational_density': round(op_density, 3),
                    'population': 'A' if folio in a_folios else 'B',
                    'token_count': len(middles)
                })

    # Sort zones by identifier density
    zones.sort(key=lambda x: x['identifier_density'], reverse=True)

    # Determine translation potential
    if len(zones) > 20:
        potential = 'HIGH'
    elif len(zones) > 5:
        potential = 'MEDIUM'
    elif len(zones) > 0:
        potential = 'LOW'
    else:
        potential = 'NONE'

    # Calculate coverage
    total_entries = len(entries)
    zone_coverage = len(zones) / total_entries if total_entries > 0 else 0

    result = {
        'metadata': {
            'phase': '19E',
            'title': 'Boundary Mapping',
            'timestamp': datetime.now().isoformat()
        },
        'identifier_candidates_mapped': len(identifier_candidates),
        'page_distribution': page_distribution,
        'macro_state_alignment': {
            'entry_header': macro_alignment['entry_header'],
            'entry_middle': macro_alignment['entry_middle'],
            'entry_closure': macro_alignment['entry_closure']
        },
        'population_alignment': {
            'a_text_dominant': a_dominant,
            'b_text_dominant': b_dominant
        },
        'translation_eligible_zones': {
            'count': len(zones),
            'coverage_percent': round(zone_coverage * 100, 1),
            'top_zones': zones[:20]
        },
        'TRANSLATION_POTENTIAL': potential,
        'INTERPRETATION': f"{len(zones)} translation-eligible zones identified ({zone_coverage:.1%} of manuscript). {len(a_dominant)} identifier candidates are A-text dominant. Translation potential: {potential}."
    }

    return result

# ============================================================================
# PHASE 19 SYNTHESIS
# ============================================================================

def phase19_synthesis(results_19a: Dict, results_19b: Dict,
                      results_19c: Dict, results_19d: Dict,
                      results_19e: Dict) -> Dict:
    """
    Combine all sub-phase results into final verdict.
    """
    print("\nGenerating Phase 19 Synthesis...")

    # Extract signals
    exec_signal = results_19a.get('IDENTIFIER_SIGNAL', 'NONE')
    sub_signal = results_19b.get('IDENTIFIER_CONFIRMATION', 'REJECTED')
    pos_signal = results_19c.get('POSITIONAL_SIGNAL', 'NONE')
    card_signal = results_19d.get('CARDINALITY_SIGNAL', 'NONE')
    trans_potential = results_19e.get('TRANSLATION_POTENTIAL', 'NONE')

    # Count strong signals
    strong_signals = sum([
        exec_signal == 'STRONG',
        sub_signal == 'CONFIRMED',
        pos_signal == 'STRONG',
        card_signal == 'STRONG'
    ])

    weak_signals = sum([
        exec_signal == 'WEAK',
        sub_signal == 'PARTIAL',
        pos_signal == 'WEAK',
        card_signal == 'WEAK'
    ])

    # Collect all candidate tokens
    non_exec_candidates = [c['token'] for c in results_19a.get('non_executable_candidates', [])]
    ref_like_tokens = list(results_19c.get('reference_like_tokens', {}).keys())
    id_like_tokens = list(results_19d.get('identifier_like_tokens', {}).keys())

    # Strong candidates appear in multiple tests
    all_candidates = Counter()
    for token in non_exec_candidates:
        all_candidates[token] += 1
    for token in ref_like_tokens:
        all_candidates[token] += 1
    for token in id_like_tokens:
        all_candidates[token] += 1

    strong_candidates = [t for t, count in all_candidates.items() if count >= 2]
    partial_candidates = [t for t, count in all_candidates.items() if count == 1]

    # Determine final verdict
    if strong_signals >= 2:
        verdict = 'IDENTIFIERS_EXIST'
        interpretation = (
            f"The Voynich control grammar DOES contain non-executable identifier tokens. "
            f"{len(strong_candidates)} candidates were identified with HIGH confidence. "
            f"Translation-eligible zones EXIST, covering {results_19e.get('translation_eligible_zones', {}).get('coverage_percent', 0)}% of the manuscript. "
            f"This OPENS the path toward semantic grounding."
        )
    elif strong_signals >= 1 or weak_signals >= 2:
        verdict = 'HYBRID'
        interpretation = (
            f"The Voynich shows MIXED identifier/operational structure. "
            f"{len(strong_candidates)} strong candidates and {len(partial_candidates)} partial candidates identified. "
            f"Some tokens may serve both referential and operational roles. "
            f"Translation potential: {trans_potential}."
        )
    else:
        verdict = 'PURE_OPERATIONAL'
        interpretation = (
            f"The Voynich is a FULLY EXECUTABLE control system with no clear referential layer. "
            f"Every token participates in execution. Translation in the traditional sense is not possible - "
            f"meaning IS the operation, not a label for it."
        )

    # Zone info
    zones_exist = results_19e.get('translation_eligible_zones', {}).get('count', 0) > 0
    zone_count = results_19e.get('translation_eligible_zones', {}).get('count', 0)
    zone_coverage = results_19e.get('translation_eligible_zones', {}).get('coverage_percent', 0)

    result = {
        'metadata': {
            'phase': '19_SYNTHESIS',
            'title': 'Identifier Boundary Detection Complete',
            'timestamp': datetime.now().isoformat()
        },
        'IDENTIFIER_BOUNDARY_DETECTION': {
            'evidence_summary': {
                'executability_signal': exec_signal,
                'substitution_signal': sub_signal,
                'positional_signal': pos_signal,
                'cardinality_signal': card_signal,
                'strong_signals': strong_signals,
                'weak_signals': weak_signals
            },
            'identifier_candidates': {
                'strong_candidates': strong_candidates,
                'partial_candidates': partial_candidates[:20],
                'total_count': len(all_candidates)
            },
            'translation_eligible_zones': {
                'exist': zones_exist,
                'count': zone_count,
                'coverage_percent': zone_coverage
            }
        },
        'FINAL_VERDICT': verdict,
        'INTERPRETATION': interpretation,
        'KEY_FINDINGS': [
            f"Executability signal: {exec_signal}",
            f"Substitution invariance: {sub_signal}",
            f"Positional rigidity signal: {pos_signal}",
            f"Cardinality pattern signal: {card_signal}",
            f"Strong identifier candidates: {len(strong_candidates)}",
            f"Translation-eligible zones: {zone_count} ({zone_coverage}% coverage)",
            f"Final verdict: {verdict}"
        ],
        'IMPLICATIONS': [
            "Strong candidates can be prioritized for semantic grounding" if strong_candidates else "Focus on operational interpretation",
            "A-text dominant tokens likely serve definitional roles",
            "Entry-header tokens may be category/substance labels" if results_19e.get('macro_state_alignment', {}).get('entry_header') else "No clear header pattern",
            f"Translation potential: {trans_potential}"
        ]
    }

    return result

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("PHASE 19: IDENTIFIER BOUNDARY & NON-EXECUTABLE TOKEN DETECTION")
    print("=" * 70)

    # Load corpus
    print("\nLoading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")

    # Build infrastructure
    print("\nBuilding transition graph...")
    graph = build_transition_graph(entries)

    # Load Phase 13 state mappings
    try:
        states = load_phase13_states()
        print(f"  Loaded {len(states['states'])} semantic states from Phase 13")
    except FileNotFoundError:
        print("  Warning: Phase 13 states not found, proceeding without")
        states = None

    # Phase 19A: Executability Analysis
    print("\n" + "-" * 50)
    results_19a = phase19a_executability_analysis(entries, records, graph)

    with open("phase19a_executability_matrix.json", 'w') as f:
        json.dump(results_19a, f, indent=2)
    print(f"  Saved: phase19a_executability_matrix.json")
    print(f"  {results_19a['IDENTIFIER_SIGNAL']} identifier signal")

    # Get candidates for subsequent phases
    non_exec_candidates = results_19a.get('non_executable_candidates', [])
    candidate_tokens = [c['token'] for c in non_exec_candidates]

    # Phase 19B: Substitution Invariance
    print("\n" + "-" * 50)
    results_19b = phase19b_substitution_invariance(entries, non_exec_candidates, graph)

    with open("phase19b_substitution_invariance.json", 'w') as f:
        json.dump(results_19b, f, indent=2)
    print(f"  Saved: phase19b_substitution_invariance.json")
    print(f"  {results_19b['IDENTIFIER_CONFIRMATION']} confirmation")

    # Phase 19C: Positional Rigidity
    print("\n" + "-" * 50)
    results_19c = phase19c_positional_rigidity(entries, candidate_tokens, KERNEL_NODES)

    with open("phase19c_positional_rigidity.json", 'w') as f:
        json.dump(results_19c, f, indent=2)
    print(f"  Saved: phase19c_positional_rigidity.json")
    print(f"  {results_19c['POSITIONAL_SIGNAL']} positional signal")

    # Phase 19D: Cardinality Constraints
    print("\n" + "-" * 50)
    results_19d = phase19d_cardinality_constraints(entries, records, candidate_tokens)

    with open("phase19d_cardinality_constraints.json", 'w') as f:
        json.dump(results_19d, f, indent=2)
    print(f"  Saved: phase19d_cardinality_constraints.json")
    print(f"  {results_19d['CARDINALITY_SIGNAL']} cardinality signal")

    # Get operational tokens for boundary mapping
    exec_tokens = [t['token'] for t in results_19a.get('sample_executable', [])]

    # Phase 19E: Boundary Mapping
    print("\n" + "-" * 50)
    results_19e = phase19e_boundary_mapping(
        entries, records,
        candidate_tokens,
        exec_tokens
    )

    with open("phase19e_boundary_map.json", 'w') as f:
        json.dump(results_19e, f, indent=2)
    print(f"  Saved: phase19e_boundary_map.json")
    print(f"  {results_19e['TRANSLATION_POTENTIAL']} translation potential")

    # Phase 19 Synthesis
    print("\n" + "-" * 50)
    synthesis = phase19_synthesis(results_19a, results_19b, results_19c, results_19d, results_19e)

    with open("phase19_synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2)
    print(f"  Saved: phase19_synthesis.json")

    # Print summary
    print("\n" + "=" * 70)
    print("PHASE 19 COMPLETE")
    print("=" * 70)

    print(f"\nFINAL VERDICT: {synthesis['FINAL_VERDICT']}")
    print(f"\nKEY FINDINGS:")
    for finding in synthesis['KEY_FINDINGS']:
        print(f"  - {finding}")

    print(f"\nINTERPRETATION:")
    print(f"  {synthesis['INTERPRETATION']}")

    return synthesis

if __name__ == "__main__":
    main()
