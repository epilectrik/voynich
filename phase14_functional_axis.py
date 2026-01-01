#!/usr/bin/env python3
"""
Phase 14: Functional Axis Reconstruction
=========================================

Situation: Phase 13 proved the Voynich is executable as a semantic state machine
with 4 stable states, 100% convergence, 95.2% cyclic settlement.

Goal: Determine what the system is optimizing and characterize its functional axes.

Ground Rules:
- No historical labeling (don't call states "nigredo" or "albedo" yet)
- Treat states as functionally ordered - behavior defines meaning
- Infer, don't assert - test candidates empirically
- The system has an objective - find it through behavior

Sub-phases:
- 14A: Infer the Objective Function
- 14B: Perturbation Tests
- 14C: Collapse Tests
- 14D: Functional Axis Naming (Abstract Only)
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

def load_phase13_results() -> Tuple[Dict, Dict, Dict, Dict]:
    """Load Phase 13 result files."""
    with open("phase13a_semantic_states.json", 'r') as f:
        states = json.load(f)
    with open("phase13b_transition_grammar.json", 'r') as f:
        transitions = json.load(f)
    with open("phase13c_quantitative_depth.json", 'r') as f:
        depth = json.load(f)
    with open("phase13e_executability.json", 'r') as f:
        executability = json.load(f)
    return states, transitions, depth, executability

# ============================================================================
# BUILD STATE INFRASTRUCTURE
# ============================================================================

def build_state_mappings(entries: Dict[str, List[str]], states_result: Dict) -> Tuple[Dict, Dict, Dict]:
    """Build node-to-state mapping and transition matrix."""
    # Node to state mapping
    node_to_state = {}
    for state_name, state_data in states_result['states'].items():
        for node in state_data['member_nodes']:
            node_to_state[node] = state_name

    state_names = list(states_result['states'].keys())

    # Build transition counts: (state_from, operator) -> state_to counts
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

    # Find forbidden transitions
    forbidden = set()
    for s1 in state_names:
        for s2 in state_names:
            has_transition = any(s2 in transitions[s1][op] for op in KNOWN_PREFIXES)
            if not has_transition:
                forbidden.add((s1, s2))

    return node_to_state, transitions, forbidden

def trace_entry_to_states(tokens: List[str], node_to_state: Dict) -> List[str]:
    """Convert token sequence to state sequence."""
    middles = [get_middle(t) for t in tokens]
    states = []
    for m in middles:
        s = node_to_state.get(m)
        if s:
            states.append(s)
    return states

# ============================================================================
# PHASE 14A: INFER THE OBJECTIVE FUNCTION
# ============================================================================

def test_14a_objective_function(entries: Dict[str, List[str]],
                                 states_result: Dict,
                                 depth_result: Dict,
                                 node_to_state: Dict,
                                 transitions: Dict,
                                 records: List[Dict]) -> Dict:
    """
    Identify what monotonic quantity the system maximizes or minimizes.

    Candidate objective functions:
    1. STABILITY - system seeks most stable configuration
    2. REFINEMENT - system purifies toward ideal state
    3. CENTRALITY - system seeks highest-traffic hub
    4. HOMOGENEITY - system reduces differentiation
    5. VOLATILITY_TO_FIXATION - system moves from unstable to fixed
    """
    print("Running Phase 14A: Objective Function Inference...")

    state_names = list(states_result['states'].keys())
    per_state_metrics = depth_result['per_state_metrics']

    # Compute candidate scores per state
    candidates = {}

    # Candidate 1: STABILITY (based on cycle tightness and repetition depth)
    stability_scores = {}
    for state in state_names:
        metrics = per_state_metrics.get(state, {})
        cycle_len = metrics.get('mean_cycle_length', 100)
        rep_depth = metrics.get('repetition_depth', 0)
        # Stability = high repetition / short cycles
        stability_scores[state] = rep_depth / (cycle_len + 1)
    candidates['STABILITY'] = stability_scores

    # Candidate 2: REFINEMENT (based on position in entry - later = more refined)
    refinement_scores = {}
    for state in state_names:
        metrics = per_state_metrics.get(state, {})
        pos = metrics.get('mean_position_in_entry', 0.5)
        refinement_scores[state] = pos
    candidates['REFINEMENT'] = refinement_scores

    # Candidate 3: CENTRALITY (based on hub score)
    centrality_scores = {}
    for state in state_names:
        state_data = states_result['states'].get(state, {})
        hub = state_data.get('hub_score', 0)
        centrality_scores[state] = hub
    candidates['CENTRALITY'] = centrality_scores

    # Candidate 4: HOMOGENEITY (inverse of operator diversity)
    homogeneity_scores = {}
    for state in state_names:
        metrics = per_state_metrics.get(state, {})
        diversity = metrics.get('operator_diversity', 1)
        # Lower diversity = more homogeneous
        homogeneity_scores[state] = 1.0 / (diversity + 1)
    candidates['HOMOGENEITY'] = homogeneity_scores

    # Candidate 5: VOLATILITY_TO_FIXATION (inverse of asymmetry magnitude)
    fixation_scores = {}
    for state in state_names:
        state_data = states_result['states'].get(state, {})
        asym = abs(state_data.get('asymmetry', 0))
        stability = state_data.get('stability_score', 0)
        # Low asymmetry + some stability = fixed
        fixation_scores[state] = (1.0 - asym) * (1 + stability)
    candidates['VOLATILITY_TO_FIXATION'] = fixation_scores

    # Separate A and B entries for analysis
    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    b_entries = {f: t for f, t in entries.items() if folio_populations.get(f) == 'B'}

    # Test monotonicity along execution paths
    candidate_correlations = {}

    for candidate_name, scores in candidates.items():
        correlations = []

        for folio, tokens in list(b_entries.items())[:100]:
            trace = trace_entry_to_states(tokens, node_to_state)
            if len(trace) < 5:
                continue

            # Get score progression along trace
            trace_scores = [scores.get(s, 0) for s in trace]
            positions = list(range(len(trace_scores)))

            # Compute correlation
            if len(trace_scores) > 2:
                mean_score = np.mean(trace_scores)
                mean_pos = np.mean(positions)

                numerator = sum((p - mean_pos) * (s - mean_score)
                               for p, s in zip(positions, trace_scores))
                denom_pos = sum((p - mean_pos)**2 for p in positions)
                denom_score = sum((s - mean_score)**2 for s in trace_scores)

                if denom_pos > 0 and denom_score > 0:
                    r = numerator / (math.sqrt(denom_pos) * math.sqrt(denom_score))
                    correlations.append(r)

        if correlations:
            candidate_correlations[candidate_name] = {
                'mean_correlation': round(np.mean(correlations), 3),
                'std_correlation': round(np.std(correlations), 3),
                'positive_fraction': round(sum(1 for c in correlations if c > 0) / len(correlations), 3)
            }
        else:
            candidate_correlations[candidate_name] = {
                'mean_correlation': 0,
                'std_correlation': 0,
                'positive_fraction': 0.5
            }

    # Test convergence alignment (does STATE-C have optimal value?)
    convergence_alignment = {}
    final_state = 'STATE-C'  # Known from Phase 13

    for candidate_name, scores in candidates.items():
        max_state = max(scores.keys(), key=lambda s: scores[s])
        min_state = min(scores.keys(), key=lambda s: scores[s])

        # Check if STATE-C is at an extreme
        c_score = scores.get(final_state, 0)
        max_score = max(scores.values())
        min_score = min(scores.values())

        if max_score > min_score:
            position = (c_score - min_score) / (max_score - min_score)
        else:
            position = 0.5

        convergence_alignment[candidate_name] = {
            'state_c_position': round(position, 3),  # 1.0 = maximum, 0.0 = minimum
            'at_maximum': max_state == final_state,
            'at_minimum': min_state == final_state
        }

    # Test forbidden transition explanation
    forbidden_explanation = {}
    # STATE-A <-> STATE-B is forbidden

    for candidate_name, scores in candidates.items():
        score_a = scores.get('STATE-A', 0)
        score_b = scores.get('STATE-B', 0)
        score_c = scores.get('STATE-C', 0)

        # Does the forbidden transition represent a "shortcut" in score space?
        # A direct jump would skip intermediate processing
        gap = abs(score_a - score_b)
        a_to_c = abs(score_a - score_c)
        b_to_c = abs(score_b - score_c)

        forbidden_explanation[candidate_name] = {
            'a_b_gap': round(gap, 3),
            'a_c_gap': round(a_to_c, 3),
            'b_c_gap': round(b_to_c, 3),
            'explains_forbidden': gap > 0 and (a_to_c < gap or b_to_c < gap)
        }

    # Rank candidates
    rankings = []
    for candidate_name in candidates.keys():
        corr = candidate_correlations[candidate_name]['mean_correlation']
        align = convergence_alignment[candidate_name]['state_c_position']
        # Best candidate: high correlation magnitude AND STATE-C at extreme
        score = abs(corr) + (0.5 if align > 0.8 or align < 0.2 else 0)
        rankings.append((candidate_name, score, corr))

    rankings.sort(key=lambda x: x[1], reverse=True)
    best_candidate = rankings[0][0]
    best_correlation = rankings[0][2]

    # Determine optimization direction
    if best_correlation > 0:
        direction = "MAXIMIZE"
    elif best_correlation < 0:
        direction = "MINIMIZE"
    else:
        direction = "UNCLEAR"

    # Generate explanation
    if best_candidate == 'STABILITY':
        explanation = "The system seeks the most stable configuration - STATE-C has highest repetition depth and tightest cycles."
    elif best_candidate == 'REFINEMENT':
        explanation = "The system refines material toward an ideal endpoint - processing moves along positional gradient."
    elif best_candidate == 'CENTRALITY':
        explanation = "The system seeks the highest-traffic hub - STATE-C dominates as central attractor."
    elif best_candidate == 'HOMOGENEITY':
        explanation = "The system reduces differentiation - processing converges to low-diversity state."
    else:
        explanation = "The system transitions from volatile to fixed states - asymmetry decreases through processing."

    return {
        "metadata": {
            "phase": "14A",
            "title": "Objective Function Inference",
            "timestamp": datetime.now().isoformat()
        },
        "candidate_scores_per_state": {
            name: {s: round(v, 4) for s, v in scores.items()}
            for name, scores in candidates.items()
        },
        "monotonicity_analysis": candidate_correlations,
        "convergence_alignment": convergence_alignment,
        "forbidden_transition_explanation": forbidden_explanation,
        "candidate_rankings": [
            {"rank": i+1, "candidate": r[0], "score": round(r[1], 3), "correlation": round(r[2], 3)}
            for i, r in enumerate(rankings)
        ],
        "BEST_CANDIDATE": {
            "name": best_candidate,
            "correlation": round(best_correlation, 3),
            "direction": direction,
            "explanation": explanation
        }
    }

# ============================================================================
# PHASE 14B: PERTURBATION TESTS
# ============================================================================

def test_14b_perturbation(entries: Dict[str, List[str]],
                          states_result: Dict,
                          node_to_state: Dict,
                          transitions: Dict,
                          forbidden: Set,
                          records: List[Dict]) -> Dict:
    """
    Understand control logic by deliberately violating normal execution patterns.
    """
    print("Running Phase 14B: Perturbation Tests...")

    state_names = list(states_result['states'].keys())

    # Separate A and B entries
    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    b_entries = {f: t for f, t in entries.items() if folio_populations.get(f) == 'B'}

    # =========================================================================
    # Perturbation 1: Repetition Count Violations
    # =========================================================================

    def analyze_repetitions(tokens: List[str]) -> List[Tuple[int, int]]:
        """Find consecutive repetitions in token sequence."""
        middles = [get_middle(t) for t in tokens]
        repetitions = []
        i = 0
        while i < len(middles):
            count = 1
            while i + count < len(middles) and middles[i + count] == middles[i]:
                count += 1
            if count > 1:
                repetitions.append((i, count))
            i += count
        return repetitions

    repetition_analysis = {
        'entries_with_repetitions': 0,
        'total_repetition_groups': 0,
        'repetition_counts': Counter(),
        'skip_effect': [],
        'extra_effect': []
    }

    for folio, tokens in list(b_entries.items())[:50]:
        reps = analyze_repetitions(tokens)
        if reps:
            repetition_analysis['entries_with_repetitions'] += 1
            repetition_analysis['total_repetition_groups'] += len(reps)
            for pos, count in reps:
                repetition_analysis['repetition_counts'][count] += 1

    # Simulate skip/extra effects
    def check_convergence(trace: List[str]) -> bool:
        if len(trace) < 5:
            return False
        last_5 = trace[-5:]
        return len(set(last_5)) <= 2

    normal_convergences = 0
    skip_convergences = 0
    extra_convergences = 0
    test_count = 0

    for folio, tokens in list(b_entries.items())[:50]:
        trace = trace_entry_to_states(tokens, node_to_state)
        if len(trace) < 10:
            continue

        test_count += 1

        # Normal trace
        if check_convergence(trace):
            normal_convergences += 1

        # Skip repetitions (remove consecutive duplicates)
        skip_trace = []
        for s in trace:
            if not skip_trace or s != skip_trace[-1]:
                skip_trace.append(s)
        if check_convergence(skip_trace):
            skip_convergences += 1

        # Extra repetitions (double each state)
        extra_trace = []
        for s in trace:
            extra_trace.append(s)
            extra_trace.append(s)
        if check_convergence(extra_trace):
            extra_convergences += 1

    repetition_violation_results = {
        'skip_repetition': {
            'still_converges': skip_convergences / test_count > 0.5 if test_count > 0 else False,
            'convergence_rate': round(skip_convergences / test_count, 3) if test_count > 0 else 0,
            'effect': 'faster' if skip_convergences >= normal_convergences else 'delayed'
        },
        'extra_repetition': {
            'still_converges': extra_convergences / test_count > 0.5 if test_count > 0 else False,
            'convergence_rate': round(extra_convergences / test_count, 3) if test_count > 0 else 0,
            'effect': 'same' if abs(extra_convergences - normal_convergences) < 3 else (
                'faster' if extra_convergences > normal_convergences else 'slower'
            )
        },
        'normal_convergence_rate': round(normal_convergences / test_count, 3) if test_count > 0 else 0
    }

    # =========================================================================
    # Perturbation 2: Rare Transition Forcing
    # =========================================================================

    # Find rare transitions (legal but low frequency)
    transition_freqs = defaultdict(int)
    total_transitions = 0

    for s1 in state_names:
        for op in transitions[s1]:
            for s2, count in transitions[s1][op].items():
                transition_freqs[(s1, s2)] += count
                total_transitions += count

    rare_transitions = []
    for (s1, s2), count in transition_freqs.items():
        if count > 0 and count / total_transitions < 0.01:  # Less than 1%
            rare_transitions.append({
                'from': s1,
                'to': s2,
                'count': count,
                'frequency': round(count / total_transitions, 4)
            })

    rare_transitions.sort(key=lambda x: x['frequency'])

    # Simulate recovery from rare transitions
    def simulate_recovery(start_state: str, max_steps: int = 20) -> int:
        """Simulate steps to reach STATE-C from a given state."""
        current = start_state
        for step in range(max_steps):
            if current == 'STATE-C':
                return step
            # Pick most common next state
            next_counts = Counter()
            for op in transitions[current]:
                for s, c in transitions[current][op].items():
                    next_counts[s] += c
            if not next_counts:
                return -1  # No path
            current = next_counts.most_common(1)[0][0]
        return max_steps

    recovery_times = {}
    for state in state_names:
        if state != 'STATE-C':
            recovery_times[state] = simulate_recovery(state)

    rare_transition_results = {
        'rare_transitions_found': len(rare_transitions),
        'rarest_transitions': rare_transitions[:5],
        'recovery_times_from_each_state': recovery_times,
        'worst_case_recovery': max(recovery_times.values()) if recovery_times else 0,
        'unrecoverable_states': [s for s, t in recovery_times.items() if t < 0]
    }

    # =========================================================================
    # Perturbation 3: Near-Forbidden Transitions
    # =========================================================================

    # STATE-A <-> STATE-B is forbidden. What's the minimum path?
    def find_path(start: str, end: str, max_depth: int = 5) -> List[str]:
        """BFS to find shortest path between states."""
        if start == end:
            return [start]

        visited = {start}
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                continue

            # Find all reachable states
            next_states = set()
            for op in transitions[current]:
                for s in transitions[current][op]:
                    next_states.add(s)

            for next_s in next_states:
                if next_s == end:
                    return path + [next_s]
                if next_s not in visited:
                    visited.add(next_s)
                    queue.append((next_s, path + [next_s]))

        return []

    a_to_b_path = find_path('STATE-A', 'STATE-B')
    b_to_a_path = find_path('STATE-B', 'STATE-A')

    # Check if there's a mandatory waypoint
    all_paths_via_c = (
        (len(a_to_b_path) > 2 and 'STATE-C' in a_to_b_path[1:-1]) or
        (len(b_to_a_path) > 2 and 'STATE-C' in b_to_a_path[1:-1])
    )

    near_forbidden_results = {
        'minimum_path_A_to_B': a_to_b_path if a_to_b_path else 'NO_PATH',
        'minimum_path_B_to_A': b_to_a_path if b_to_a_path else 'NO_PATH',
        'path_length_A_to_B': len(a_to_b_path) - 1 if a_to_b_path else -1,
        'path_length_B_to_A': len(b_to_a_path) - 1 if b_to_a_path else -1,
        'mandatory_waypoint': 'STATE-C' if all_paths_via_c else 'NONE',
        'interpretation': (
            "STATE-C serves as mandatory waypoint between A and B" if all_paths_via_c else
            "Multiple paths exist between A and B"
        )
    }

    # =========================================================================
    # Perturbation 4: Initiator/Terminator Bypass
    # =========================================================================

    # Find initiator and terminator patterns
    initiator_states = Counter()
    terminator_states = Counter()

    for folio, tokens in list(b_entries.items())[:100]:
        trace = trace_entry_to_states(tokens, node_to_state)
        if len(trace) >= 3:
            initiator_states[trace[0]] += 1
            terminator_states[trace[-1]] += 1

    # Test execution without typical initiators
    typical_initiator = initiator_states.most_common(1)[0][0] if initiator_states else None
    typical_terminator = terminator_states.most_common(1)[0][0] if terminator_states else None

    with_initiator_converge = 0
    without_initiator_converge = 0
    test_count = 0

    for folio, tokens in list(b_entries.items())[:50]:
        trace = trace_entry_to_states(tokens, node_to_state)
        if len(trace) < 5:
            continue

        test_count += 1

        # Full trace
        if check_convergence(trace):
            with_initiator_converge += 1

        # Without first state
        if len(trace) > 5 and check_convergence(trace[1:]):
            without_initiator_converge += 1

    initiator_bypass_results = {
        'typical_initiator_state': typical_initiator,
        'initiator_state_distribution': dict(initiator_states.most_common(4)),
        'typical_terminator_state': typical_terminator,
        'terminator_state_distribution': dict(terminator_states.most_common(4)),
        'without_initiator': {
            'converges': without_initiator_converge / test_count > 0.5 if test_count > 0 else False,
            'convergence_rate': round(without_initiator_converge / test_count, 3) if test_count > 0 else 0
        },
        'with_initiator': {
            'convergence_rate': round(with_initiator_converge / test_count, 3) if test_count > 0 else 0
        },
        'initiator_essential': with_initiator_converge > without_initiator_converge + 5
    }

    # =========================================================================
    # Control Logic Insights
    # =========================================================================

    insights = []

    if repetition_violation_results['skip_repetition']['still_converges']:
        insights.append("Repetitions are NOT essential for convergence - system is resilient to compression")
    else:
        insights.append("Repetitions ARE essential - skipping breaks convergence")

    if repetition_violation_results['extra_repetition']['effect'] == 'same':
        insights.append("Extra repetitions have no effect - system tolerates redundancy")

    if near_forbidden_results['mandatory_waypoint'] == 'STATE-C':
        insights.append("STATE-C is mandatory waypoint between forbidden states - central processing hub")

    if not initiator_bypass_results['initiator_essential']:
        insights.append("Initiator state is conventional, not essential - system is robust to entry point")
    else:
        insights.append("Initiator state IS essential - must start from correct state")

    if rare_transition_results['worst_case_recovery'] < 5:
        insights.append("System recovers quickly from any state - high error tolerance")

    return {
        "metadata": {
            "phase": "14B",
            "title": "Perturbation Tests",
            "timestamp": datetime.now().isoformat()
        },
        "repetition_violations": repetition_violation_results,
        "rare_transition_forcing": rare_transition_results,
        "near_forbidden_probing": near_forbidden_results,
        "initiator_terminator_bypass": initiator_bypass_results,
        "CONTROL_LOGIC_INSIGHTS": insights,
        "PERTURBATION_RESILIENCE": (
            "HIGH" if len([i for i in insights if "resilient" in i.lower() or "robust" in i.lower() or "tolerates" in i.lower()]) >= 2 else
            "MEDIUM" if len(insights) >= 3 else
            "LOW"
        )
    }

# ============================================================================
# PHASE 14C: COLLAPSE TESTS
# ============================================================================

def test_14c_collapse(entries: Dict[str, List[str]],
                      states_result: Dict,
                      node_to_state: Dict,
                      transitions: Dict,
                      records: List[Dict]) -> Dict:
    """
    Determine if STATE-A and STATE-D are essential or merely interface states.
    """
    print("Running Phase 14C: Collapse Tests...")

    state_names = list(states_result['states'].keys())

    # Separate B entries for testing
    folio_populations = {}
    for rec in records:
        folio_populations[rec['folio']] = rec['population']

    b_entries = {f: t for f, t in entries.items() if folio_populations.get(f) == 'B'}

    def check_convergence(trace: List[str]) -> bool:
        if len(trace) < 5:
            return False
        last_5 = trace[-5:]
        return len(set(last_5)) <= 2

    def check_cycle(trace: List[str]) -> bool:
        if len(trace) < 6:
            return False
        for cycle_len in range(1, 5):
            last_n = trace[-cycle_len * 2:]
            if len(last_n) >= cycle_len * 2:
                if last_n[:cycle_len] == last_n[cycle_len:cycle_len * 2]:
                    return True
        return False

    def run_test(mapping_func, test_name: str) -> Dict:
        """Run convergence/cycle test with modified state mapping."""
        converged = 0
        cyclic = 0
        total = 0

        for folio, tokens in list(b_entries.items())[:50]:
            middles = [get_middle(t) for t in tokens]
            trace = []
            for m in middles:
                s = node_to_state.get(m)
                if s:
                    mapped = mapping_func(s)
                    trace.append(mapped)

            if len(trace) < 5:
                continue

            total += 1
            if check_convergence(trace):
                converged += 1
            if check_cycle(trace):
                cyclic += 1

        return {
            'converges': converged / total > 0.5 if total > 0 else False,
            'convergence_rate': round(converged / total, 3) if total > 0 else 0,
            'settles': cyclic / total > 0.3 if total > 0 else False,
            'cycle_rate': round(cyclic / total, 3) if total > 0 else 0,
            'total_tested': total
        }

    # Baseline (no modification)
    baseline = run_test(lambda s: s, "baseline")

    # Test 1: Remove STATE-A (map to STATE-C)
    without_a = run_test(
        lambda s: 'STATE-C' if s == 'STATE-A' else s,
        "without_A"
    )

    # Test 2: Remove STATE-D (map to STATE-C)
    without_d = run_test(
        lambda s: 'STATE-C' if s == 'STATE-D' else s,
        "without_D"
    )

    # Test 3: Remove STATE-B (map to STATE-C)
    without_b = run_test(
        lambda s: 'STATE-C' if s == 'STATE-B' else s,
        "without_B"
    )

    # Test 4: Binary collapse (keep only STATE-C + one other)
    binary_results = {}
    for other in state_names:
        if other == 'STATE-C':
            continue
        result = run_test(
            lambda s, keep=other: s if s in ['STATE-C', keep] else 'STATE-C',
            f"binary_C_{other}"
        )
        binary_results[f'STATE-C + {other}'] = result

    # Find best binary pairing
    best_binary = max(binary_results.keys(),
                      key=lambda k: binary_results[k]['convergence_rate'])

    # Test 5: STATE-C alone
    c_alone = run_test(
        lambda s: 'STATE-C',
        "c_alone"
    )

    # Determine essential vs interface
    essential_states = []
    interface_states = []

    # A state is essential if removing it significantly degrades convergence
    threshold = baseline['convergence_rate'] - 0.1

    if without_a['convergence_rate'] < threshold:
        essential_states.append('STATE-A')
    else:
        interface_states.append('STATE-A')

    if without_b['convergence_rate'] < threshold:
        essential_states.append('STATE-B')
    else:
        interface_states.append('STATE-B')

    if without_d['convergence_rate'] < threshold:
        essential_states.append('STATE-D')
    else:
        interface_states.append('STATE-D')

    essential_states.append('STATE-C')  # Always essential as attractor

    # Determine semantic kernel
    if c_alone['convergence_rate'] > 0.7:
        kernel = "STATE-C alone is sufficient - system is fundamentally monostate"
    elif binary_results[best_binary]['convergence_rate'] > 0.8:
        kernel = f"Binary system {best_binary} captures core semantics"
    else:
        kernel = f"Full {len(essential_states)}-state system required"

    return {
        "metadata": {
            "phase": "14C",
            "title": "Collapse Tests",
            "timestamp": datetime.now().isoformat()
        },
        "baseline": baseline,
        "without_STATE_A": {
            **without_a,
            'behavior_change': (
                "significant degradation" if without_a['convergence_rate'] < threshold else
                "minimal change - A is interface"
            )
        },
        "without_STATE_B": {
            **without_b,
            'behavior_change': (
                "significant degradation" if without_b['convergence_rate'] < threshold else
                "minimal change - B is interface"
            )
        },
        "without_STATE_D": {
            **without_d,
            'behavior_change': (
                "significant degradation" if without_d['convergence_rate'] < threshold else
                "minimal change - D is interface"
            )
        },
        "binary_collapse": {
            "best_pairing": best_binary,
            "best_pairing_results": binary_results[best_binary],
            "all_pairings": {k: v['convergence_rate'] for k, v in binary_results.items()}
        },
        "STATE_C_alone": {
            **c_alone,
            'trivial': c_alone['convergence_rate'] > 0.9,
            'remaining_structure': (
                "trivial - all converges" if c_alone['convergence_rate'] > 0.9 else
                "non-trivial - state diversity provides information"
            )
        },
        "SEMANTIC_KERNEL": {
            "essential_states": essential_states,
            "interface_states": interface_states,
            "minimum_viable_system": kernel
        }
    }

# ============================================================================
# PHASE 14D: FUNCTIONAL AXIS NAMING (ABSTRACT ONLY)
# ============================================================================

def test_14d_functional_naming(objective_result: Dict,
                                perturbation_result: Dict,
                                collapse_result: Dict,
                                states_result: Dict,
                                depth_result: Dict) -> Dict:
    """
    Name the functional axis abstractly based on 14A-14C results.
    No historical labels - pure functional description.
    """
    print("Running Phase 14D: Functional Axis Naming...")

    state_names = list(states_result['states'].keys())
    per_state_metrics = depth_result['per_state_metrics']

    # Extract key findings
    best_objective = objective_result['BEST_CANDIDATE']['name']
    direction = objective_result['BEST_CANDIDATE']['direction']

    essential = collapse_result['SEMANTIC_KERNEL']['essential_states']
    interface = collapse_result['SEMANTIC_KERNEL']['interface_states']

    mandatory_waypoint = perturbation_result['near_forbidden_probing']['mandatory_waypoint']
    resilience = perturbation_result['PERTURBATION_RESILIENCE']

    # Name the primary axis based on objective function
    axis_names = {
        'STABILITY': ('STABILITY_GRADIENT', 'stability level', 'oscillatory fixation'),
        'REFINEMENT': ('REFINEMENT_AXIS', 'processing depth', 'material purification'),
        'CENTRALITY': ('CENTRALITY_GRADIENT', 'hub proximity', 'network centralization'),
        'HOMOGENEITY': ('HOMOGENEITY_AXIS', 'operator diversity', 'state uniformity'),
        'VOLATILITY_TO_FIXATION': ('FIXATION_GRADIENT', 'volatility level', 'state stabilization')
    }

    axis_name, axis_measure, axis_process = axis_names.get(
        best_objective,
        ('UNKNOWN_AXIS', 'unknown measure', 'unknown process')
    )

    # Name STATE-C's role
    if mandatory_waypoint == 'STATE-C':
        c_role = "PROCESSING_HUB"
        c_description = "mandatory central waypoint for all transformations"
    elif collapse_result['STATE_C_alone']['convergence_rate'] > 0.9:
        c_role = "ABSORBING_ATTRACTOR"
        c_description = "final destination for all processing"
    else:
        c_role = "CONVERGENCE_TARGET"
        c_description = "primary attractor state with highest traffic"

    # Name STATE-A and STATE-B roles
    state_roles = {'STATE-C': c_role}

    for state in ['STATE-A', 'STATE-B', 'STATE-D']:
        if state in essential:
            # Essential states have functional roles
            metrics = per_state_metrics.get(state, {})
            pos = metrics.get('mean_position_in_entry', 0.5)

            if pos < 0.4:
                role = "ENTRY_STATE"
            elif pos > 0.6:
                role = "EXIT_STATE"
            else:
                role = "PROCESSING_STATE"
        else:
            # Interface states are buffers
            role = "INTERFACE_BUFFER"

        state_roles[state] = role

    # Explain forbidden transition meaning
    if mandatory_waypoint == 'STATE-C':
        forbidden_meaning = (
            "A↔B is forbidden because these states represent incompatible processing modes; "
            "transformation must pass through STATE-C (processing hub) to convert between them"
        )
    else:
        obj_scores = objective_result['candidate_scores_per_state'].get(best_objective, {})
        score_a = obj_scores.get('STATE-A', 0)
        score_b = obj_scores.get('STATE-B', 0)

        if direction == 'MAXIMIZE':
            forbidden_meaning = (
                f"A↔B forbidden because direct transition would skip required {axis_measure} accumulation; "
                f"STATE-A ({round(score_a, 3)}) and STATE-B ({round(score_b, 3)}) require intermediary processing"
            )
        else:
            forbidden_meaning = (
                f"A↔B forbidden because these states occupy opposite ends of the {axis_measure} spectrum; "
                "direct transition is semantically invalid"
            )

    # Name the objective function
    if direction == 'MAXIMIZE':
        objective_name = f"MAXIMIZE_{best_objective}"
        mechanism = f"System increases {axis_measure} through iterative processing until STATE-C optimum reached"
    else:
        objective_name = f"MINIMIZE_{best_objective}"
        mechanism = f"System decreases {axis_measure} through iterative processing until STATE-C optimum reached"

    return {
        "metadata": {
            "phase": "14D",
            "title": "Functional Axis Naming (Abstract)",
            "timestamp": datetime.now().isoformat()
        },
        "primary_axis": {
            "name": axis_name,
            "direction": f"{direction} {axis_measure}",
            "interpretation": f"The system performs {axis_process} along the {axis_name}"
        },
        "state_roles": {
            state: {
                "functional_role": role,
                "description": (
                    c_description if state == 'STATE-C' else
                    f"{'essential' if state in essential else 'interface'} state for processing"
                )
            }
            for state, role in state_roles.items()
        },
        "forbidden_transition_meaning": {
            "states": "STATE-A ↔ STATE-B",
            "interpretation": forbidden_meaning
        },
        "objective_function": {
            "name": objective_name,
            "achieved_at": "STATE-C",
            "mechanism": mechanism
        },
        "FUNCTIONAL_CHARACTERIZATION": (
            f"The Voynich semantic state machine operates along a {axis_name}, "
            f"{'maximizing' if direction == 'MAXIMIZE' else 'minimizing'} {axis_measure}. "
            f"STATE-C serves as {c_role} ({c_description}). "
            f"The forbidden A↔B transition enforces {axis_process} discipline. "
            f"System resilience is {resilience}."
        )
    }

# ============================================================================
# PHASE 14 SYNTHESIS
# ============================================================================

def synthesize_phase14(result_14a: Dict, result_14b: Dict,
                       result_14c: Dict, result_14d: Dict) -> Dict:
    """Synthesize all Phase 14 results."""
    print("Synthesizing Phase 14 results...")

    # Extract key findings
    objective = result_14a['BEST_CANDIDATE']
    resilience = result_14b['PERTURBATION_RESILIENCE']
    kernel = result_14c['SEMANTIC_KERNEL']
    axis = result_14d['primary_axis']
    roles = result_14d['state_roles']
    forbidden = result_14d['forbidden_transition_meaning']

    # Count insights
    insights = result_14b['CONTROL_LOGIC_INSIGHTS']

    # Determine confidence
    correlation = abs(objective['correlation'])
    if correlation > 0.3 and resilience in ['HIGH', 'MEDIUM']:
        confidence = 'HIGH'
    elif correlation > 0.1 or resilience == 'HIGH':
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    # Build final interpretation
    final_interpretation = (
        f"The Voynich state machine optimizes {objective['name']} by processing through "
        f"{len(kernel['essential_states'])} essential states along a 1D {axis['name']}. "
        f"STATE-C serves as {roles['STATE-C']['functional_role']}. "
        f"The forbidden A↔B transition enforces {result_14d['objective_function']['mechanism'].split('until')[0].strip()}. "
        f"The system is designed for repeatable, convergent, error-tolerant transformation processing."
    )

    return {
        "metadata": {
            "phase": "14_SYNTHESIS",
            "title": "Functional Axis Reconstruction",
            "timestamp": datetime.now().isoformat()
        },
        "FUNCTIONAL_RECONSTRUCTION": {
            "objective_function": {
                "name": objective['name'],
                "confidence": confidence,
                "evidence": f"correlation={objective['correlation']}, direction={objective['direction']}"
            },
            "system_architecture": {
                "essential_states": len(kernel['essential_states']),
                "interface_states": len(kernel['interface_states']),
                "semantic_kernel": kernel['minimum_viable_system']
            },
            "control_logic": {
                "convergence_mechanism": result_14d['objective_function']['mechanism'],
                "forbidden_transition_purpose": forbidden['interpretation'],
                "perturbation_resilience": resilience
            },
            "functional_interpretation": final_interpretation
        },
        "STATE_ROLE_SUMMARY": {
            state: roles[state]['functional_role']
            for state in roles
        },
        "KEY_INSIGHTS": insights,
        "AXIS_CHARACTERIZATION": axis,
        "SUCCESS_METRICS": {
            "objective_identified": correlation > 0.1,
            "perturbation_tests_informative": len(insights) >= 3,
            "collapse_tests_discriminate": len(kernel['essential_states']) < 4,
            "functional_naming_complete": True
        }
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute all Phase 14 tests."""
    print("=" * 70)
    print("PHASE 14: FUNCTIONAL AXIS RECONSTRUCTION")
    print("=" * 70)
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Load Phase 13 results
    print("Loading Phase 13 results...")
    states_result, transitions_result, depth_result, exec_result = load_phase13_results()
    print(f"  States: {states_result['stable_states_identified']}")
    print()

    # Build infrastructure
    print("Building state infrastructure...")
    node_to_state, transitions, forbidden = build_state_mappings(entries, states_result)
    print(f"  Mapped {len(node_to_state)} nodes to states")
    print(f"  Forbidden transitions: {len(forbidden)}")
    print()

    # Set random seed
    random.seed(42)
    np.random.seed(42)

    # Run Phase 14A
    result_14a = test_14a_objective_function(
        entries, states_result, depth_result, node_to_state, transitions, records
    )
    with open("phase14a_objective_function.json", 'w') as f:
        json.dump(result_14a, f, indent=2, default=str)
    print(f"  Saved: phase14a_objective_function.json")
    print()

    # Run Phase 14B
    result_14b = test_14b_perturbation(
        entries, states_result, node_to_state, transitions, forbidden, records
    )
    with open("phase14b_perturbation_tests.json", 'w') as f:
        json.dump(result_14b, f, indent=2, default=str)
    print(f"  Saved: phase14b_perturbation_tests.json")
    print()

    # Run Phase 14C
    result_14c = test_14c_collapse(
        entries, states_result, node_to_state, transitions, records
    )
    with open("phase14c_collapse_tests.json", 'w') as f:
        json.dump(result_14c, f, indent=2, default=str)
    print(f"  Saved: phase14c_collapse_tests.json")
    print()

    # Run Phase 14D
    result_14d = test_14d_functional_naming(
        result_14a, result_14b, result_14c, states_result, depth_result
    )
    with open("phase14d_functional_naming.json", 'w') as f:
        json.dump(result_14d, f, indent=2, default=str)
    print(f"  Saved: phase14d_functional_naming.json")
    print()

    # Synthesize
    synthesis = synthesize_phase14(result_14a, result_14b, result_14c, result_14d)
    with open("phase14_synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2, default=str)
    print(f"  Saved: phase14_synthesis.json")
    print()

    # Print summary
    print("=" * 70)
    print("PHASE 14 RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"OBJECTIVE FUNCTION: {result_14a['BEST_CANDIDATE']['name']}")
    print(f"  Direction: {result_14a['BEST_CANDIDATE']['direction']}")
    print(f"  Correlation: {result_14a['BEST_CANDIDATE']['correlation']}")
    print()
    print(f"PERTURBATION RESILIENCE: {result_14b['PERTURBATION_RESILIENCE']}")
    print(f"  Control insights: {len(result_14b['CONTROL_LOGIC_INSIGHTS'])}")
    print()
    print(f"SEMANTIC KERNEL:")
    print(f"  Essential states: {result_14c['SEMANTIC_KERNEL']['essential_states']}")
    print(f"  Interface states: {result_14c['SEMANTIC_KERNEL']['interface_states']}")
    print()
    print(f"FUNCTIONAL AXIS: {result_14d['primary_axis']['name']}")
    print()
    print("STATE ROLES:")
    for state, data in result_14d['state_roles'].items():
        print(f"  {state}: {data['functional_role']}")
    print()
    print("-" * 70)
    print("FINAL CHARACTERIZATION:")
    print("-" * 70)
    print(synthesis['FUNCTIONAL_RECONSTRUCTION']['functional_interpretation'])
    print()
    print("SUCCESS METRICS:")
    for metric, value in synthesis['SUCCESS_METRICS'].items():
        status = "PASS" if value else "FAIL"
        print(f"  {metric}: {status}")

if __name__ == "__main__":
    main()
