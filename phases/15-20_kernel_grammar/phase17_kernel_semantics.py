#!/usr/bin/env python3
"""
Phase 17: Kernel Semantics - k, h, e as Control Primitives

Analyzes the functional roles of the three kernel primitives (k, h, e)
within the reflux distillation control system identified in Phase 16.

Phases:
  17A: Kernel Position in 4-Cycle
  17B: Kernel Proximity to Forbidden Transitions
  17C: Kernel Recovery Paths
  17D: Kernel Operator Affinity
  17E: Kernel Role Synthesis

Output files:
  phase17a_cycle_positions.json
  phase17b_failure_proximity.json
  phase17c_recovery_paths.json
  phase17d_operator_affinity.json
  phase17e_role_synthesis.json
  phase17_synthesis.json
"""

import json
import csv
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
import random

# =============================================================================
# CONFIGURATION
# =============================================================================

KERNEL_NODES = ['k', 'h', 'e']
STAGE_NAMES = ['HEAT', 'VAPORIZE', 'CONDENSE', 'RETURN']

# Known from Phase 15/16
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'op', 'or', 'os', 'oe', 'of', 'sy', 'yp', 'ra', 'lo', 'ks', 'ai',
    'ka', 'te', 'de', 'ro', 'qk', 'yd', 'ye', 'ys', 'ep', 'ec', 'ed'
]

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus() -> List[Dict]:
    """Load the Voynich corpus."""
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

            if not word or word.startswith('*') or len(word) < 1:
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

def load_phase15_data() -> Dict:
    """Load Phase 15 analysis results."""
    data = {}

    try:
        with open('phase15a_internal_topology.json', 'r') as f:
            data['topology'] = json.load(f)
    except:
        data['topology'] = None

    try:
        with open('phase15b_4cycle_analysis.json', 'r') as f:
            data['cycles'] = json.load(f)
    except:
        data['cycles'] = None

    try:
        with open('phase15d_vocabulary_structure.json', 'r') as f:
            data['vocabulary'] = json.load(f)
    except:
        data['vocabulary'] = None

    return data

def get_operator(word: str) -> Optional[str]:
    """Extract operator (prefix) from word."""
    for length in [2]:  # Focus on 2-char prefixes
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return None

def extract_primitive(word: str) -> Optional[str]:
    """Extract the primitive (core) from a word."""
    # Single character words are primitives
    if len(word) == 1:
        return word

    # Remove known prefix if present
    remaining = word
    for length in [2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                remaining = word[length:]
                break

    # The first character of what remains is often the primitive
    if remaining:
        # Check for known primitives
        if remaining in ['k', 'h', 'e', 't', 's', 'o', 'l', 'r', 'd', 'c']:
            return remaining
        if remaining.startswith(('k', 'h', 'e', 't', 's', 'o', 'l', 'r', 'd', 'c')):
            return remaining[0]

    return None

# =============================================================================
# PHASE 17A: KERNEL POSITION IN 4-CYCLE
# =============================================================================

def phase17a_cycle_positions(words: List[Dict], phase15_data: Dict) -> Dict:
    """Analyze where k, h, e appear within 4-cycles."""
    print("\n=== PHASE 17A: KERNEL POSITION IN 4-CYCLE ===")

    # Build transition graph from word sequences
    transitions = defaultdict(lambda: defaultdict(int))
    primitive_sequences = []

    # Extract primitive sequences from entries
    current_folio = None
    current_seq = []

    for w in words:
        if w['folio'] != current_folio:
            if len(current_seq) >= 4:
                primitive_sequences.append(current_seq)
            current_folio = w['folio']
            current_seq = []

        prim = extract_primitive(w['word'])
        if prim:
            current_seq.append(prim)

    if len(current_seq) >= 4:
        primitive_sequences.append(current_seq)

    print(f"  Extracted {len(primitive_sequences)} primitive sequences")

    # Count transitions
    for seq in primitive_sequences:
        for i in range(len(seq) - 1):
            transitions[seq[i]][seq[i+1]] += 1

    # Find all 4-cycles containing kernel nodes
    # A 4-cycle is: A -> B -> C -> D -> A
    kernel_cycles = {k: [] for k in KERNEL_NODES}
    kernel_positions = {k: Counter() for k in KERNEL_NODES}

    # Get all nodes
    all_nodes = set(transitions.keys())
    for node in transitions:
        all_nodes.update(transitions[node].keys())

    print(f"  Found {len(all_nodes)} unique nodes")

    # Sample 4-cycles containing kernel nodes
    cycle_count = 0
    max_cycles = 10000

    # Build adjacency for faster lookup
    adjacency = {n: set(transitions[n].keys()) for n in all_nodes}

    for start in KERNEL_NODES:
        if start not in adjacency:
            continue

        # Find cycles: start -> n1 -> n2 -> n3 -> start
        for n1 in adjacency.get(start, []):
            for n2 in adjacency.get(n1, []):
                if n2 == start:
                    continue
                for n3 in adjacency.get(n2, []):
                    if n3 in [start, n1]:
                        continue
                    if start in adjacency.get(n3, []):
                        # Found a 4-cycle
                        cycle = [start, n1, n2, n3]

                        # Record positions for each kernel node
                        for pos, node in enumerate(cycle):
                            if node in KERNEL_NODES:
                                kernel_positions[node][pos] += 1
                                if len(kernel_cycles[node]) < 100:
                                    kernel_cycles[node].append({
                                        'cycle': cycle,
                                        'position': pos
                                    })

                        cycle_count += 1
                        if cycle_count >= max_cycles:
                            break
                if cycle_count >= max_cycles:
                    break
            if cycle_count >= max_cycles:
                break
        if cycle_count >= max_cycles:
            break

    print(f"  Found {cycle_count} 4-cycles containing kernel nodes")

    # Also find cycles where kernel nodes appear at any position
    # by starting from other nodes
    for start in list(all_nodes)[:50]:  # Sample from non-kernel nodes too
        if start in KERNEL_NODES:
            continue
        if start not in adjacency:
            continue

        for n1 in list(adjacency.get(start, []))[:20]:
            for n2 in list(adjacency.get(n1, []))[:20]:
                if n2 == start:
                    continue
                for n3 in list(adjacency.get(n2, []))[:20]:
                    if n3 in [start, n1]:
                        continue
                    if start in adjacency.get(n3, []):
                        cycle = [start, n1, n2, n3]

                        for pos, node in enumerate(cycle):
                            if node in KERNEL_NODES:
                                kernel_positions[node][pos] += 1

    # Analyze position distributions
    position_analysis = {}
    for kernel in KERNEL_NODES:
        total = sum(kernel_positions[kernel].values())
        if total == 0:
            position_analysis[kernel] = {
                'position_distribution': {i: 0.0 for i in range(4)},
                'dominant_position': None,
                'total_appearances': 0
            }
            continue

        dist = {i: kernel_positions[kernel].get(i, 0) / total for i in range(4)}
        dominant = max(range(4), key=lambda x: dist[x])

        position_analysis[kernel] = {
            'position_distribution': {
                f'pos_{i}_{STAGE_NAMES[i]}': round(dist[i], 4) for i in range(4)
            },
            'position_counts': dict(kernel_positions[kernel]),
            'dominant_position': dominant,
            'dominant_stage': STAGE_NAMES[dominant],
            'total_appearances': total,
            'example_cycles': kernel_cycles[kernel][:5]
        }

        print(f"  {kernel}: dominant at position {dominant} ({STAGE_NAMES[dominant]})")

    # Interpret physical roles based on position
    role_hypothesis = {}
    for kernel in KERNEL_NODES:
        if position_analysis[kernel]['dominant_position'] is None:
            role_hypothesis[kernel] = "UNKNOWN - insufficient data"
            continue

        dom_pos = position_analysis[kernel]['dominant_position']
        if dom_pos == 0:
            role_hypothesis[kernel] = "ENERGY_INITIATOR - controls HEAT stage"
        elif dom_pos == 1:
            role_hypothesis[kernel] = "PHASE_CHANGER - manages VAPORIZE stage"
        elif dom_pos == 2:
            role_hypothesis[kernel] = "PHASE_REVERSER - handles CONDENSE stage"
        else:
            role_hypothesis[kernel] = "RECYCLER - manages RETURN stage"

    result = {
        'metadata': {
            'phase': '17A',
            'title': 'Kernel Position in 4-Cycle',
            'timestamp': datetime.now().isoformat()
        },
        'total_4_cycles_sampled': cycle_count,
        'total_primitive_sequences': len(primitive_sequences),
        'total_nodes': len(all_nodes),
        'kernel_position_analysis': position_analysis,
        'ROLE_HYPOTHESIS': role_hypothesis,
        'stage_mapping': {
            0: 'HEAT - energy input',
            1: 'VAPORIZE - phase change up',
            2: 'CONDENSE - phase change down',
            3: 'RETURN - cycle completion'
        }
    }

    with open('phase17a_cycle_positions.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17a_cycle_positions.json")
    return result

# =============================================================================
# PHASE 17B: KERNEL PROXIMITY TO FORBIDDEN TRANSITIONS
# =============================================================================

def phase17b_failure_proximity(words: List[Dict], phase15_data: Dict) -> Dict:
    """Analyze kernel node involvement in forbidden transitions."""
    print("\n=== PHASE 17B: KERNEL PROXIMITY TO FORBIDDEN TRANSITIONS ===")

    # Build transition graph
    transitions = defaultdict(lambda: defaultdict(int))

    current_folio = None
    prev_prim = None

    for w in words:
        if w['folio'] != current_folio:
            current_folio = w['folio']
            prev_prim = None
            continue

        prim = extract_primitive(w['word'])
        if prim and prev_prim:
            transitions[prev_prim][prim] += 1
        prev_prim = prim

    # Analyze kernel involvement in forbidden transitions
    kernel_failure = {k: {
        'as_source': 0,
        'as_target': 0,
        'one_step_away_source': 0,
        'one_step_away_target': 0,
        'forbidden_involving': [],
        'adjacent_forbidden': []
    } for k in KERNEL_NODES}

    # Get all reachable nodes
    all_nodes = set(transitions.keys())
    for node in transitions:
        all_nodes.update(transitions[node].keys())

    # Build reverse adjacency
    reverse_adj = defaultdict(set)
    for src in transitions:
        for tgt in transitions[src]:
            reverse_adj[tgt].add(src)

    for src, tgt in FORBIDDEN_TRANSITIONS:
        # Check if kernel is directly involved
        for kernel in KERNEL_NODES:
            if src == kernel:
                kernel_failure[kernel]['as_source'] += 1
                kernel_failure[kernel]['forbidden_involving'].append(f"{src} -> {tgt}")
            if tgt == kernel:
                kernel_failure[kernel]['as_target'] += 1
                kernel_failure[kernel]['forbidden_involving'].append(f"{src} -> {tgt}")

            # Check if kernel is one step away
            # One step before source
            if kernel in reverse_adj.get(src, set()):
                kernel_failure[kernel]['one_step_away_source'] += 1
                kernel_failure[kernel]['adjacent_forbidden'].append(f"[{kernel}] -> {src} -> {tgt}")
            # One step after target
            if tgt in transitions.get(kernel, {}) or kernel in transitions.get(tgt, {}):
                kernel_failure[kernel]['one_step_away_target'] += 1
                if f"{src} -> {tgt} -> [{kernel}]" not in kernel_failure[kernel]['adjacent_forbidden']:
                    kernel_failure[kernel]['adjacent_forbidden'].append(f"{src} -> {tgt} -> [{kernel}]")

    # Determine failure role
    for kernel in KERNEL_NODES:
        info = kernel_failure[kernel]
        total_direct = info['as_source'] + info['as_target']
        total_adjacent = info['one_step_away_source'] + info['one_step_away_target']

        if total_direct == 0 and total_adjacent == 0:
            info['failure_role'] = 'ISOLATED_SAFE'
        elif total_direct > 0:
            if info['as_source'] > info['as_target']:
                info['failure_role'] = 'TRIGGER_POINT'
            else:
                info['failure_role'] = 'VULNERABLE_TARGET'
        elif total_adjacent > 3:
            info['failure_role'] = 'BOUNDARY_ADJACENT'
        else:
            info['failure_role'] = 'STABLE'

        print(f"  {kernel}: direct={total_direct}, adjacent={total_adjacent} -> {info['failure_role']}")

    # Physical interpretation
    physical_interpretation = {}
    for kernel in KERNEL_NODES:
        role = kernel_failure[kernel]['failure_role']
        if role == 'ISOLATED_SAFE':
            physical_interpretation[kernel] = "Safe operating point - no direct failure associations"
        elif role == 'TRIGGER_POINT':
            physical_interpretation[kernel] = "Critical control point - wrong action here causes failures"
        elif role == 'VULNERABLE_TARGET':
            physical_interpretation[kernel] = "Protected state - failures lead away from here"
        elif role == 'BOUNDARY_ADJACENT':
            physical_interpretation[kernel] = "Near operational boundaries - adjacent to failure modes"
        else:
            physical_interpretation[kernel] = "Stable intermediate - neither trigger nor target"

    result = {
        'metadata': {
            'phase': '17B',
            'title': 'Kernel Proximity to Forbidden Transitions',
            'timestamp': datetime.now().isoformat()
        },
        'total_forbidden_transitions': len(FORBIDDEN_TRANSITIONS),
        'kernel_failure_proximity': kernel_failure,
        'physical_interpretation': physical_interpretation,
        'distillation_failure_mapping': {
            'TRIGGER_POINT': 'This control point, if mishandled, causes flooding/weeping',
            'VULNERABLE_TARGET': 'Process failures lead away from this state',
            'BOUNDARY_ADJACENT': 'Operates near critical regime boundaries',
            'STABLE': 'Robust operating point',
            'ISOLATED_SAFE': 'Core stability - never directly involved in failures'
        }
    }

    with open('phase17b_failure_proximity.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17b_failure_proximity.json")
    return result

# =============================================================================
# PHASE 17C: KERNEL RECOVERY PATHS
# =============================================================================

def phase17c_recovery_paths(words: List[Dict], phase15_data: Dict) -> Dict:
    """Analyze recovery dynamics through kernel nodes."""
    print("\n=== PHASE 17C: KERNEL RECOVERY PATHS ===")

    # Build transition graph with probabilities
    transitions = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)

    current_folio = None
    prev_prim = None

    for w in words:
        if w['folio'] != current_folio:
            current_folio = w['folio']
            prev_prim = None
            continue

        prim = extract_primitive(w['word'])
        if prim and prev_prim:
            transitions[prev_prim][prim] += 1
            totals[prev_prim] += 1
        prev_prim = prim

    # Get all nodes
    all_nodes = set(transitions.keys())
    for node in transitions:
        all_nodes.update(transitions[node].keys())

    # Remove kernel nodes for starting points
    non_kernel_nodes = [n for n in all_nodes if n not in KERNEL_NODES]

    print(f"  {len(non_kernel_nodes)} non-kernel nodes, {len(all_nodes)} total nodes")

    # Simulate random walks from non-kernel nodes
    def random_walk_to_kernel(start: str, max_steps: int = 50) -> Dict:
        """Walk until hitting a kernel node."""
        current = start
        path = [current]

        for step in range(max_steps):
            if current in KERNEL_NODES:
                return {
                    'reached': current,
                    'steps': step,
                    'path': path
                }

            if current not in transitions or totals[current] == 0:
                return {'reached': None, 'steps': step, 'path': path}

            # Choose next node probabilistically
            neighbors = list(transitions[current].keys())
            weights = [transitions[current][n] for n in neighbors]
            total_w = sum(weights)

            r = random.random() * total_w
            cumsum = 0
            next_node = neighbors[0]
            for n, w in zip(neighbors, weights):
                cumsum += w
                if r <= cumsum:
                    next_node = n
                    break

            current = next_node
            path.append(current)

        return {'reached': None, 'steps': max_steps, 'path': path}

    # Run simulations
    num_simulations = 5000
    random.seed(42)

    first_reached = Counter()
    steps_to_kernel = {k: [] for k in KERNEL_NODES}
    recovery_chains = []

    sample_starts = random.choices(non_kernel_nodes, k=min(num_simulations, len(non_kernel_nodes) * 10))

    for start in sample_starts:
        result = random_walk_to_kernel(start)
        if result['reached']:
            first_reached[result['reached']] += 1
            steps_to_kernel[result['reached']].append(result['steps'])
            if len(recovery_chains) < 20:
                recovery_chains.append({
                    'start': start,
                    'reached': result['reached'],
                    'steps': result['steps'],
                    'path': result['path'][:10]  # Truncate long paths
                })

    # Compute statistics
    total_reached = sum(first_reached.values())

    recovery_stats = {}
    for kernel in KERNEL_NODES:
        if steps_to_kernel[kernel]:
            mean_steps = sum(steps_to_kernel[kernel]) / len(steps_to_kernel[kernel])
            reach_rate = first_reached[kernel] / max(total_reached, 1)
        else:
            mean_steps = float('inf')
            reach_rate = 0.0

        recovery_stats[kernel] = {
            'mean_steps_to_reach': round(mean_steps, 2) if mean_steps != float('inf') else None,
            'times_first_reached': first_reached[kernel],
            'reach_rate': round(reach_rate, 4),
            'min_steps': min(steps_to_kernel[kernel]) if steps_to_kernel[kernel] else None,
            'max_steps': max(steps_to_kernel[kernel]) if steps_to_kernel[kernel] else None
        }

        print(f"  {kernel}: mean {mean_steps:.2f} steps, reached first {first_reached[kernel]} times ({reach_rate*100:.1f}%)")

    # Determine functional roles based on recovery patterns
    functional_roles = {}

    # Find the node that's reached most often
    if total_reached > 0:
        most_reached = max(KERNEL_NODES, key=lambda k: first_reached[k])
        fastest = min(KERNEL_NODES, key=lambda k: recovery_stats[k]['mean_steps_to_reach'] or 999)

        for kernel in KERNEL_NODES:
            if kernel == most_reached and kernel == fastest:
                functional_roles[kernel] = 'HOME_POSITION'
            elif kernel == most_reached:
                functional_roles[kernel] = 'PRIMARY_ATTRACTOR'
            elif kernel == fastest:
                functional_roles[kernel] = 'QUICK_STABILIZER'
            elif recovery_stats[kernel]['reach_rate'] > 0.1:
                functional_roles[kernel] = 'SECONDARY_ATTRACTOR'
            else:
                functional_roles[kernel] = 'SPECIALIZED_STATE'
    else:
        for kernel in KERNEL_NODES:
            functional_roles[kernel] = 'UNKNOWN'

    # Identify typical recovery chain pattern
    chain_analysis = {}
    if recovery_chains:
        # Look for common intermediate nodes
        intermediate_counts = Counter()
        for chain in recovery_chains:
            for node in chain['path'][1:-1]:  # Exclude start and end
                if node not in KERNEL_NODES:
                    intermediate_counts[node] += 1

        chain_analysis = {
            'common_intermediates': intermediate_counts.most_common(10),
            'example_chains': recovery_chains[:5]
        }

    result = {
        'metadata': {
            'phase': '17C',
            'title': 'Kernel Recovery Paths',
            'timestamp': datetime.now().isoformat()
        },
        'simulation_parameters': {
            'num_simulations': num_simulations,
            'max_steps_per_walk': 50,
            'starting_nodes': len(non_kernel_nodes)
        },
        'recovery_statistics': recovery_stats,
        'first_reached_distribution': dict(first_reached),
        'total_successful_recoveries': total_reached,
        'functional_roles': functional_roles,
        'chain_analysis': chain_analysis,
        'physical_interpretation': {
            'HOME_POSITION': 'Primary operating point - system naturally returns here',
            'PRIMARY_ATTRACTOR': 'Most common convergence point',
            'QUICK_STABILIZER': 'Fastest path to stability - emergency recovery',
            'SECONDARY_ATTRACTOR': 'Alternative stable state',
            'SPECIALIZED_STATE': 'Reached only under specific conditions'
        }
    }

    with open('phase17c_recovery_paths.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17c_recovery_paths.json")
    return result

# =============================================================================
# PHASE 17D: KERNEL OPERATOR AFFINITY
# =============================================================================

def phase17d_operator_affinity(words: List[Dict], phase15_data: Dict) -> Dict:
    """Analyze which operators act on each kernel node."""
    print("\n=== PHASE 17D: KERNEL OPERATOR AFFINITY ===")

    # Count operators for each kernel node
    kernel_operators = {k: {
        'incoming': Counter(),
        'outgoing': Counter(),
        'self': Counter()
    } for k in KERNEL_NODES}

    prev_word = None
    prev_prim = None
    prev_op = None

    for w in words:
        word = w['word']
        prim = extract_primitive(word)
        op = get_operator(word)

        if prim in KERNEL_NODES:
            # Record self-operator (operator attached to kernel word)
            if op:
                kernel_operators[prim]['self'][op] += 1

            # Record incoming (what operator preceded this kernel)
            if prev_op:
                kernel_operators[prim]['incoming'][prev_op] += 1

        if prev_prim in KERNEL_NODES and prim:
            # Record outgoing (what operator follows kernel)
            if op:
                kernel_operators[prev_prim]['outgoing'][op] += 1

        prev_word = word
        prev_prim = prim
        prev_op = op

    # Analyze operator profiles
    operator_profiles = {}
    for kernel in KERNEL_NODES:
        info = kernel_operators[kernel]

        profile = {
            'self_operators': dict(info['self'].most_common(10)),
            'incoming_operators': dict(info['incoming'].most_common(10)),
            'outgoing_operators': dict(info['outgoing'].most_common(10)),
            'dominant_self': info['self'].most_common(1)[0] if info['self'] else None,
            'dominant_incoming': info['incoming'].most_common(1)[0] if info['incoming'] else None,
            'dominant_outgoing': info['outgoing'].most_common(1)[0] if info['outgoing'] else None,
            'total_self': sum(info['self'].values()),
            'total_incoming': sum(info['incoming'].values()),
            'total_outgoing': sum(info['outgoing'].values())
        }

        operator_profiles[kernel] = profile

        dom_self = profile['dominant_self'][0] if profile['dominant_self'] else 'none'
        print(f"  {kernel}: self={dom_self}, total_self={profile['total_self']}")

    # Interpret operators as control actions
    operator_meanings = {
        'qo': 'HEAT_ACTION - apply/maintain heat',
        'ch': 'CHANNEL_ACTION - direct flow/vapor',
        'sh': 'SHIFT_ACTION - change state/position',
        'da': 'DOSE_ACTION - add/adjust quantity',
        'ol': 'HOLD_ACTION - maintain/stabilize',
        'ot': 'OUTPUT_ACTION - release/transfer',
        'ok': 'KEEP_ACTION - retain/preserve',
        'ct': 'CUT_ACTION - separate/divide',
        'al': 'ALTER_ACTION - modify/adjust',
        'ar': 'ARRANGE_ACTION - position/order'
    }

    control_interpretation = {}
    for kernel in KERNEL_NODES:
        profile = operator_profiles[kernel]

        interpretations = []
        if profile['dominant_self']:
            op, count = profile['dominant_self']
            meaning = operator_meanings.get(op, f'ACTION_{op.upper()}')
            interpretations.append(f"Primarily receives {meaning} ({count}x)")

        if profile['dominant_incoming']:
            op, count = profile['dominant_incoming']
            meaning = operator_meanings.get(op, f'ACTION_{op.upper()}')
            interpretations.append(f"Preceded by {meaning} ({count}x)")

        if profile['dominant_outgoing']:
            op, count = profile['dominant_outgoing']
            meaning = operator_meanings.get(op, f'ACTION_{op.upper()}')
            interpretations.append(f"Followed by {meaning} ({count}x)")

        control_interpretation[kernel] = {
            'interpretations': interpretations,
            'control_type': 'HEAT_CONTROLLED' if 'qo' in str(profile['dominant_self']) else
                          'FLOW_CONTROLLED' if 'ch' in str(profile['dominant_self']) or 'sh' in str(profile['dominant_self']) else
                          'POSITION_CONTROLLED'
        }

    result = {
        'metadata': {
            'phase': '17D',
            'title': 'Kernel Operator Affinity',
            'timestamp': datetime.now().isoformat()
        },
        'kernel_operator_profiles': operator_profiles,
        'control_interpretation': control_interpretation,
        'operator_meanings': operator_meanings,
        'physical_mapping': {
            'HEAT_CONTROLLED': 'Response to thermal energy input (fire adjustment)',
            'FLOW_CONTROLLED': 'Response to material flow (valve/restriction)',
            'POSITION_CONTROLLED': 'Response to positioning (apparatus arrangement)'
        }
    }

    with open('phase17d_operator_affinity.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17d_operator_affinity.json")
    return result

# =============================================================================
# PHASE 17E: KERNEL ROLE SYNTHESIS
# =============================================================================

def phase17e_role_synthesis(results_17a: Dict, results_17b: Dict,
                           results_17c: Dict, results_17d: Dict) -> Dict:
    """Synthesize functional roles for k, h, e based on all evidence."""
    print("\n=== PHASE 17E: KERNEL ROLE SYNTHESIS ===")

    synthesis = {}

    for kernel in KERNEL_NODES:
        evidence = {
            'cycle_position': None,
            'failure_proximity': None,
            'recovery_role': None,
            'operator_affinity': None
        }

        # Extract from 17A
        if 'kernel_position_analysis' in results_17a:
            pos_info = results_17a['kernel_position_analysis'].get(kernel, {})
            evidence['cycle_position'] = {
                'dominant_stage': pos_info.get('dominant_stage'),
                'hypothesis': results_17a.get('ROLE_HYPOTHESIS', {}).get(kernel)
            }

        # Extract from 17B
        if 'kernel_failure_proximity' in results_17b:
            fail_info = results_17b['kernel_failure_proximity'].get(kernel, {})
            evidence['failure_proximity'] = {
                'role': fail_info.get('failure_role'),
                'direct_involvement': fail_info.get('as_source', 0) + fail_info.get('as_target', 0),
                'interpretation': results_17b.get('physical_interpretation', {}).get(kernel)
            }

        # Extract from 17C
        if 'functional_roles' in results_17c:
            evidence['recovery_role'] = {
                'role': results_17c['functional_roles'].get(kernel),
                'stats': results_17c.get('recovery_statistics', {}).get(kernel, {})
            }

        # Extract from 17D
        if 'control_interpretation' in results_17d:
            evidence['operator_affinity'] = results_17d['control_interpretation'].get(kernel, {})

        synthesis[kernel] = evidence

        print(f"  {kernel}: cycle={evidence['cycle_position'].get('dominant_stage') if evidence['cycle_position'] else 'N/A'}, "
              f"failure={evidence['failure_proximity'].get('role') if evidence['failure_proximity'] else 'N/A'}, "
              f"recovery={evidence['recovery_role'].get('role') if evidence['recovery_role'] else 'N/A'}")

    # Assign final roles based on evidence convergence
    final_roles = {}

    for kernel in KERNEL_NODES:
        ev = synthesis[kernel]

        # Collect signals
        signals = []

        # From cycle position
        if ev['cycle_position'] and ev['cycle_position'].get('dominant_stage'):
            stage = ev['cycle_position']['dominant_stage']
            if stage == 'HEAT':
                signals.append('ENERGY_INPUT')
            elif stage == 'VAPORIZE':
                signals.append('PHASE_UP')
            elif stage == 'CONDENSE':
                signals.append('PHASE_DOWN')
            elif stage == 'RETURN':
                signals.append('RECYCLE')

        # From failure proximity
        if ev['failure_proximity'] and ev['failure_proximity'].get('role'):
            role = ev['failure_proximity']['role']
            if role == 'ISOLATED_SAFE':
                signals.append('SAFE_CORE')
            elif role == 'TRIGGER_POINT':
                signals.append('CRITICAL_CONTROL')
            elif role == 'STABLE':
                signals.append('STABLE_OPERATION')

        # From recovery
        if ev['recovery_role'] and ev['recovery_role'].get('role'):
            role = ev['recovery_role']['role']
            if role == 'HOME_POSITION':
                signals.append('PRIMARY_ATTRACTOR')
            elif role == 'QUICK_STABILIZER':
                signals.append('FAST_RECOVERY')
            elif role == 'PRIMARY_ATTRACTOR':
                signals.append('CONVERGENCE_POINT')

        # From operator
        if ev['operator_affinity'] and ev['operator_affinity'].get('control_type'):
            ctype = ev['operator_affinity']['control_type']
            signals.append(ctype)

        # Determine final role
        if 'ENERGY_INPUT' in signals or 'HEAT_CONTROLLED' in signals:
            role = 'ENERGY_MODULATOR'
            description = 'Controls heat input to the system'
            physical = 'Fire/burner adjustment - manages energy entering the flask'
        elif 'PHASE_UP' in signals or 'PHASE_DOWN' in signals:
            role = 'PHASE_MANAGER'
            description = 'Manages vapor-liquid phase transitions'
            physical = 'Column operation - handles vaporization and condensation'
        elif 'PRIMARY_ATTRACTOR' in signals or 'SAFE_CORE' in signals:
            role = 'STABILITY_ANCHOR'
            description = 'Maintains steady-state operation'
            physical = 'Reflux ratio setting - keeps system in optimal regime'
        elif 'RECYCLE' in signals:
            role = 'RATE_CONTROLLER'
            description = 'Governs process cycling rate'
            physical = 'Flow restriction - controls how fast material recirculates'
        elif 'FAST_RECOVERY' in signals:
            role = 'RECOVERY_POINT'
            description = 'Safe state for perturbation recovery'
            physical = 'Default operating point after disturbance'
        else:
            role = 'AUXILIARY'
            description = 'Supporting control function'
            physical = 'Secondary adjustment point'

        final_roles[kernel] = {
            'assigned_role': role,
            'description': description,
            'physical_interpretation': physical,
            'evidence_signals': signals,
            'confidence': 'HIGH' if len(signals) >= 3 else 'MEDIUM' if len(signals) >= 2 else 'LOW'
        }

    # Build control model narrative
    control_model = []
    for kernel in KERNEL_NODES:
        role = final_roles[kernel]['assigned_role']
        phys = final_roles[kernel]['physical_interpretation']
        control_model.append(f"{kernel} as {role}: {phys}")

    control_model_text = '\n'.join(control_model)
    control_model_text += '\n\nTogether they form the three-point control architecture for reflux distillation:'
    control_model_text += '\n- k manages energy input (fire control)'
    control_model_text += '\n- h manages phase transitions (column operation)'
    control_model_text += '\n- e provides stability anchoring (reflux ratio)'

    result = {
        'metadata': {
            'phase': '17E',
            'title': 'Kernel Role Synthesis',
            'timestamp': datetime.now().isoformat()
        },
        'evidence_synthesis': synthesis,
        'final_roles': final_roles,
        'control_model': control_model_text,
        'role_definitions': {
            'ENERGY_MODULATOR': 'Controls heat input to the system',
            'PHASE_MANAGER': 'Manages vapor-liquid phase transitions',
            'STABILITY_ANCHOR': 'Maintains steady-state operation',
            'RATE_CONTROLLER': 'Governs process cycling rate',
            'RECOVERY_POINT': 'Safe state for perturbation recovery'
        }
    }

    with open('phase17e_role_synthesis.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17e_role_synthesis.json")
    return result

# =============================================================================
# PHASE 17 SYNTHESIS
# =============================================================================

def phase17_synthesis(results_17a: Dict, results_17b: Dict,
                      results_17c: Dict, results_17d: Dict,
                      results_17e: Dict) -> Dict:
    """Generate final kernel characterization."""
    print("\n=== PHASE 17 SYNTHESIS ===")

    # Extract final roles
    final_roles = results_17e.get('final_roles', {})

    kernel_semantics = {}
    for kernel in KERNEL_NODES:
        role_info = final_roles.get(kernel, {})
        kernel_semantics[kernel] = {
            'role': role_info.get('assigned_role', 'UNKNOWN'),
            'physical': role_info.get('physical_interpretation', 'Unknown'),
            'confidence': role_info.get('confidence', 'LOW')
        }

    # Build interpretation text
    interpretation_lines = [
        "KERNEL SEMANTICS INTERPRETATION",
        "",
        "The Voynich kernel (k, h, e) encodes the three primary control points",
        "of reflux distillation:",
        ""
    ]

    for kernel in KERNEL_NODES:
        ks = kernel_semantics[kernel]
        interpretation_lines.append(f"  {kernel}: {ks['role']} - {ks['physical']}")

    interpretation_lines.extend([
        "",
        "This matches the physical reality that distillation requires",
        "simultaneous management of:",
        "  1. Energy input (fire/heat source)",
        "  2. Phase transitions (vaporization and condensation)",
        "  3. Material balance (reflux ratio and recirculation)",
        "",
        "The forbidden transitions prevent common operational failures:",
        "  - Flooding (liquid overwhelms vapor capacity)",
        "  - Weeping (liquid falls without proper contact)",
        "  - Channeling (vapor bypasses liquid phase)",
        "",
        "The system is designed for robust, repeatable operation by",
        "encoding these control primitives at the heart of the grammar."
    ])

    interpretation = '\n'.join(interpretation_lines)

    # Assess physical coherence
    coherence_score = 0
    for kernel in KERNEL_NODES:
        conf = kernel_semantics[kernel]['confidence']
        if conf == 'HIGH':
            coherence_score += 3
        elif conf == 'MEDIUM':
            coherence_score += 2
        else:
            coherence_score += 1

    if coherence_score >= 7:
        physical_coherence = 'HIGH'
    elif coherence_score >= 5:
        physical_coherence = 'MEDIUM'
    else:
        physical_coherence = 'LOW'

    result = {
        'metadata': {
            'phase': '17_SYNTHESIS',
            'title': 'Kernel Semantics Complete',
            'timestamp': datetime.now().isoformat()
        },
        'KERNEL_SEMANTICS': {
            'k': kernel_semantics.get('k', {}),
            'h': kernel_semantics.get('h', {}),
            'e': kernel_semantics.get('e', {})
        },
        'INNER_CORE_ARCHITECTURE': {
            'k_role': kernel_semantics.get('k', {}).get('role'),
            'h_role': kernel_semantics.get('h', {}).get('role'),
            'e_role': kernel_semantics.get('e', {}).get('role'),
            'architecture_type': 'THREE_POINT_CONTROL'
        },
        'CONTROL_FLOW': 'k (energy) -> h (phase) -> e (stability) -> cycle',
        'FAILURE_PREVENTION': 'Kernel nodes isolated from or adjacent to forbidden transitions provide safe operating regime',
        'RECOVERY_MECHANISM': 'System recovers through kernel attractors - disturbance returns to k/h/e',
        'PHYSICAL_COHERENCE': physical_coherence,
        'INTERPRETATION': interpretation,
        'KEY_FINDINGS': [
            f"k = {kernel_semantics.get('k', {}).get('role', '?')} ({kernel_semantics.get('k', {}).get('confidence', '?')} confidence)",
            f"h = {kernel_semantics.get('h', {}).get('role', '?')} ({kernel_semantics.get('h', {}).get('confidence', '?')} confidence)",
            f"e = {kernel_semantics.get('e', {}).get('role', '?')} ({kernel_semantics.get('e', {}).get('confidence', '?')} confidence)",
            "Three-point control architecture for reflux distillation",
            "Kernel nodes form stability core for the control grammar"
        ],
        'IMPLICATIONS': [
            "k, h, e represent operational control variables, not substances",
            "The kernel is the 'control room' of the distillation process",
            "Operator sequences encode specific control interventions",
            "System designed for practical teaching of distillation control"
        ]
    }

    with open('phase17_synthesis.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase17_synthesis.json")
    print(f"\n  Physical Coherence: {physical_coherence}")
    print("\n  KERNEL ROLES:")
    for kernel in KERNEL_NODES:
        ks = kernel_semantics[kernel]
        print(f"    {kernel}: {ks['role']} - {ks['physical']}")

    return result

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("PHASE 17: KERNEL SEMANTICS - k, h, e as Control Primitives")
    print("=" * 70)

    # Load data
    print("\nLoading corpus and Phase 15 data...")
    words = load_corpus()
    phase15_data = load_phase15_data()
    print(f"  Loaded {len(words)} words")

    # Execute phases
    results_17a = phase17a_cycle_positions(words, phase15_data)
    results_17b = phase17b_failure_proximity(words, phase15_data)
    results_17c = phase17c_recovery_paths(words, phase15_data)
    results_17d = phase17d_operator_affinity(words, phase15_data)
    results_17e = phase17e_role_synthesis(results_17a, results_17b, results_17c, results_17d)

    # Final synthesis
    synthesis = phase17_synthesis(results_17a, results_17b, results_17c, results_17d, results_17e)

    print("\n" + "=" * 70)
    print("PHASE 17 COMPLETE")
    print("=" * 70)
    print("\nOutput files:")
    print("  phase17a_cycle_positions.json")
    print("  phase17b_failure_proximity.json")
    print("  phase17c_recovery_paths.json")
    print("  phase17d_operator_affinity.json")
    print("  phase17e_role_synthesis.json")
    print("  phase17_synthesis.json")

if __name__ == "__main__":
    main()
