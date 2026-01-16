#!/usr/bin/env python3
"""
Phase 23: Regime Boundary Analysis

Analyzes outlier folios identified in Phase 22B to determine:
- Whether they represent regime boundary conditions
- Failure recovery / repair operations
- Special operating modes (startup, shutdown, stressed conditions)
- Scribal noise

All analysis remains fully non-semantic and structural.
"""

import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

KERNEL_NODES = {'k', 'h', 'e'}  # Core within core

# Priority outliers from Phase 22B
PRIORITY_OUTLIERS = {
    'f57r': {'priority': 'CRITICAL', 'family': 6, 'key_anomaly': 'Only folio with reset_present=true'},
    'f76r': {'priority': 'HIGH', 'family': 2, 'key_anomaly': 'Largest folio (2222 tokens)'},
    'f85v2': {'priority': 'HIGH', 'family': 4, 'key_anomaly': 'Extreme phase_ordering_rigidity'},
    'f48r': {'priority': 'MEDIUM', 'family': 3, 'key_anomaly': 'High kernel distance'},
    'f83v': {'priority': 'MEDIUM', 'family': 2, 'key_anomaly': 'High hazard density'},
    'f86v4': {'priority': 'MEDIUM', 'family': 8, 'key_anomaly': 'Low cycle regularity'},
    'f33r': {'priority': 'MEDIUM', 'family': 4, 'key_anomaly': 'Low phase_ordering_rigidity'},
    'f94v': {'priority': 'MEDIUM', 'family': 4, 'key_anomaly': 'High intervention frequency'},
    'f95r2': {'priority': 'MEDIUM', 'family': 4, 'key_anomaly': 'Low intervention diversity'},
    'f95v2': {'priority': 'MEDIUM', 'family': 4, 'key_anomaly': 'High intervention frequency'},
    'f105r': {'priority': 'LOW', 'family': 2, 'key_anomaly': 'High link density'},
    'f105v': {'priority': 'LOW', 'family': 3, 'key_anomaly': 'High cycle count'},
    'f111r': {'priority': 'LOW', 'family': 2, 'key_anomaly': 'High near miss count'},
    'f111v': {'priority': 'LOW', 'family': 2, 'key_anomaly': 'High hazard adjacency'},
    'f115v': {'priority': 'LOW', 'family': 2, 'key_anomaly': 'High max consecutive link'},
}

# Hazard classes from Phase 18
HAZARD_CLASSES = {
    'PHASE_ORDERING': {
        'transitions': [('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
                        ('dy', 'aiin'), ('dy', 'chey'), ('chey', 'chedy'), ('chey', 'shedy')],
        'keywords': {'chey', 'shey', 'dy'}
    },
    'COMPOSITION_JUMP': {
        'transitions': [('chedy', 'ee'), ('c', 'ee'), ('shedy', 'aiin'), ('shedy', 'o')],
        'keywords': {'chedy', 'shedy', 'aiin', 'ee'}
    },
    'CONTAINMENT_TIMING': {
        'transitions': [('chol', 'r'), ('l', 'chol'), ('or', 'dal'), ('he', 'or')],
        'keywords': {'l', 'c', 'o', 'r'}
    },
    'ENERGY_OVERSHOOT': {
        'transitions': [('he', 't')],
        'keywords': {'he', 't', 'k'}
    },
    'RATE_MISMATCH': {
        'transitions': [('ar', 'dal')],
        'keywords': {'or', 'dal', 'ar', 'chol'}
    }
}

# Build forbidden transitions set
FORBIDDEN_TRANSITIONS = set()
for hc, data in HAZARD_CLASSES.items():
    for t in data['transitions']:
        FORBIDDEN_TRANSITIONS.add(t)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_transcription_data() -> Dict[str, List[str]]:
    """Load tokens for each folio from transcription file (PRIMARY transcriber H only)."""
    folio_tokens = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header
    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= 13:
            # Filter to PRIMARY transcriber (H) only - column 12
            transcriber = parts[12].strip('"')
            if transcriber != 'H':
                continue

            word = parts[0].strip('"')
            folio = parts[2].strip('"')
            # Clean word - remove asterisks and special chars
            clean_word = re.sub(r'\*', '', word)
            if clean_word and folio:
                folio_tokens[folio].append(clean_word)

    return dict(folio_tokens)

def load_control_signatures() -> Dict:
    """Load control signatures from Phase 22B."""
    with open('control_signatures.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_operator_equivalence() -> Dict:
    """Load operator equivalence classes from Phase 20A."""
    with open('phase20a_operator_equivalence.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_internal_topology() -> Dict:
    """Load internal topology from Phase 15A."""
    with open('phase15a_internal_topology.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_token_to_class_map(equivalence_data: Dict) -> Dict[str, int]:
    """Build mapping from token to class ID."""
    token_to_class = {}
    for cls in equivalence_data.get('classes', []):
        class_id = cls['class_id']
        for member in cls.get('members', []):
            if member:  # Skip empty strings
                token_to_class[member] = class_id
    return token_to_class

def get_node_types(topology_data: Dict) -> Dict[str, str]:
    """Build mapping from node to type (hub/bridge/spoke)."""
    node_types = {}

    for hub in topology_data.get('node_roles', {}).get('hubs', []):
        node_types[hub['node']] = 'hub'
    for bridge in topology_data.get('node_roles', {}).get('bridges', []):
        node_types[bridge['node']] = 'bridge'
    for spoke in topology_data.get('node_roles', {}).get('spokes', []):
        node_types[spoke['node']] = 'spoke'

    return node_types

# ============================================================================
# KERNEL DISTANCE COMPUTATION
# ============================================================================

def compute_kernel_distance(token: str, kernel_nodes: Set[str]) -> int:
    """
    Compute distance to nearest kernel node.
    Distance 1 = token contains kernel character
    Distance 2 = token adjacent to kernel in grammar
    Distance 3+ = further
    """
    # Check if token IS a kernel node
    if token in kernel_nodes:
        return 0

    # Check if token contains kernel character
    for k in kernel_nodes:
        if k in token:
            return 1

    # Check for proximity patterns
    # Tokens with 'ch', 'sh' are typically distance 2 from h
    if 'ch' in token or 'sh' in token:
        return 2

    # Tokens with 'ol', 'al', 'ar' are bridge-type
    if any(x in token for x in ['ol', 'al', 'ar', 'or']):
        return 2

    # Default distance
    return 3

def compute_kernel_distances_per_node(token: str) -> Dict[str, int]:
    """Compute distance to each kernel node individually."""
    distances = {}
    for k in KERNEL_NODES:
        if token == k:
            distances[k] = 0
        elif k in token:
            distances[k] = 1
        elif k == 'h' and ('ch' in token or 'sh' in token):
            distances[k] = 1
        elif k == 'k' and 'k' in token:
            distances[k] = 1
        elif k == 'e' and 'e' in token:
            distances[k] = 1
        else:
            distances[k] = 3
    return distances

# ============================================================================
# HAZARD DETECTION
# ============================================================================

def is_hazard_adjacent(prev_token: str, curr_token: str) -> Tuple[bool, Optional[str]]:
    """Check if transition is hazard-adjacent or forbidden."""
    if (prev_token, curr_token) in FORBIDDEN_TRANSITIONS:
        # Find which hazard class
        for hc_name, hc_data in HAZARD_CLASSES.items():
            if (prev_token, curr_token) in hc_data['transitions']:
                return True, hc_name

    # Check keyword adjacency
    for hc_name, hc_data in HAZARD_CLASSES.items():
        keywords = hc_data['keywords']
        if prev_token in keywords or curr_token in keywords:
            return True, hc_name

    return False, None

def get_hazard_classes_for_token(token: str) -> List[str]:
    """Get all hazard classes this token is associated with."""
    classes = []
    for hc_name, hc_data in HAZARD_CLASSES.items():
        if token in hc_data['keywords']:
            classes.append(hc_name)
    return classes

# ============================================================================
# CYCLE DETECTION
# ============================================================================

def detect_2_cycles(tokens: List[str]) -> List[Tuple[int, int, str]]:
    """Detect 2-cycles in token sequence. Returns (position, cycle_num, position_in_cycle)."""
    cycles = []
    cycle_num = 1
    pos_in_cycle = 1

    for i, token in enumerate(tokens):
        cycles.append((i, cycle_num, f"{cycle_num}.{pos_in_cycle}"))
        pos_in_cycle += 1
        if pos_in_cycle > 2:
            pos_in_cycle = 1
            cycle_num += 1

    return cycles

# ============================================================================
# TASK A: LINE-BY-LINE CONTROL TRACE
# ============================================================================

def generate_control_trace(folio: str, tokens: List[str], token_to_class: Dict[str, int]) -> str:
    """Generate detailed control trace for a folio."""
    lines = []
    lines.append(f"# Control Trace: {folio}")
    lines.append(f"# Generated: {datetime.now().isoformat()}")
    lines.append(f"# Total Tokens: {len(tokens)}")
    lines.append("")
    lines.append("| Position | Token | Class | K_Dist | H_Dist | E_Dist | Min_Dist | Hazard_Adj | Hazard_Class | Cycle | Notes |")
    lines.append("|----------|-------|-------|--------|--------|--------|----------|------------|--------------|-------|-------|")

    cycles = detect_2_cycles(tokens)
    prev_token = None
    hazard_sequences = []
    current_hazard_seq = []

    for i, token in enumerate(tokens):
        # Get class ID
        class_id = token_to_class.get(token, 0)
        class_str = f"CLASS_{class_id:02d}" if class_id > 0 else "UNKNOWN"

        # Compute kernel distances
        distances = compute_kernel_distances_per_node(token)
        min_dist = min(distances.values())

        # Check hazard adjacency
        is_hazard, hazard_class = False, None
        if prev_token:
            is_hazard, hazard_class = is_hazard_adjacent(prev_token, token)

        # Track hazard sequences
        if is_hazard:
            current_hazard_seq.append(i)
        else:
            if len(current_hazard_seq) >= 3:
                hazard_sequences.append(current_hazard_seq.copy())
            current_hazard_seq = []

        # Get cycle info
        _, _, cycle_pos = cycles[i]

        # Determine notes
        notes = []
        if token in KERNEL_NODES:
            notes.append("KERNEL")
        if min_dist <= 1:
            notes.append("KERNEL_ADJACENT")
        if is_hazard:
            notes.append("HAZARD")

        hazard_adj_str = "Y" if is_hazard else "N"
        hazard_class_str = hazard_class if hazard_class else "-"
        notes_str = ", ".join(notes) if notes else ""

        lines.append(f"| {i+1:04d} | {token[:10]:10s} | {class_str:8s} | {distances['k']} | {distances['h']} | {distances['e']} | {min_dist} | {hazard_adj_str} | {hazard_class_str:15s} | {cycle_pos:5s} | {notes_str} |")

        prev_token = token

    # Add summary section
    lines.append("")
    lines.append("---")
    lines.append("## Summary Statistics")
    lines.append("")

    # Kernel contact count
    kernel_contacts = sum(1 for t in tokens if compute_kernel_distance(t, KERNEL_NODES) <= 1)
    lines.append(f"- **Kernel contacts (dist <= 1):** {kernel_contacts} ({100*kernel_contacts/len(tokens):.1f}%)")

    # Hazard adjacency count
    hazard_count = 0
    for i in range(1, len(tokens)):
        is_h, _ = is_hazard_adjacent(tokens[i-1], tokens[i])
        if is_h:
            hazard_count += 1
    lines.append(f"- **Hazard-adjacent transitions:** {hazard_count}")

    # Navigation sequences
    if hazard_sequences:
        lines.append(f"- **Navigation sequences (3+ consecutive hazard-adjacent):** {len(hazard_sequences)}")
        for seq in hazard_sequences[:5]:
            lines.append(f"  - Positions {seq[0]+1}-{seq[-1]+1}")
    else:
        lines.append("- **Navigation sequences:** None")

    return "\n".join(lines)

# ============================================================================
# TASK B: KERNEL-DISTANCE TRAJECTORY ANALYSIS
# ============================================================================

def compute_kernel_trajectory(tokens: List[str]) -> Dict:
    """Compute kernel distance trajectory for a folio."""
    trajectory = []
    trajectory_k = []
    trajectory_h = []
    trajectory_e = []

    for token in tokens:
        distances = compute_kernel_distances_per_node(token)
        min_dist = min(distances.values())
        trajectory.append(min_dist)
        trajectory_k.append(distances['k'])
        trajectory_h.append(distances['h'])
        trajectory_e.append(distances['e'])

    # Compute statistics
    mean_dist = sum(trajectory) / len(trajectory) if trajectory else 0
    variance = sum((d - mean_dist)**2 for d in trajectory) / len(trajectory) if trajectory else 0

    # Kernel contact events (distance = 0 or 1)
    kernel_contacts = sum(1 for d in trajectory if d <= 1)

    # Longest excursion from kernel
    max_excursion = 0
    current_excursion = 0
    for d in trajectory:
        if d > 1:
            current_excursion += 1
            max_excursion = max(max_excursion, current_excursion)
        else:
            current_excursion = 0

    # Pattern detection
    oscillations = 0
    for i in range(1, len(trajectory)):
        if (trajectory[i] > 1 and trajectory[i-1] <= 1) or (trajectory[i] <= 1 and trajectory[i-1] > 1):
            oscillations += 1

    pattern = "stable"
    if variance > 1.0:
        if oscillations > len(trajectory) * 0.3:
            pattern = "oscillating"
        else:
            pattern = "erratic"
    elif max_excursion > len(trajectory) * 0.1:
        pattern = "drifting"

    return {
        'trajectory': trajectory,
        'trajectory_k': trajectory_k,
        'trajectory_h': trajectory_h,
        'trajectory_e': trajectory_e,
        'mean_distance': mean_dist,
        'variance': variance,
        'kernel_contact_count': kernel_contacts,
        'kernel_contact_ratio': kernel_contacts / len(trajectory) if trajectory else 0,
        'longest_excursion': max_excursion,
        'oscillation_count': oscillations,
        'pattern': pattern
    }

def generate_trajectory_comparison(outlier_data: Dict, sibling_data: Dict,
                                    outlier_folio: str, sibling_folio: str) -> str:
    """Generate comparison between outlier and sibling trajectories."""
    lines = []
    lines.append(f"## Trajectory Comparison: {outlier_folio} vs {sibling_folio}")
    lines.append("")
    lines.append("| Metric | Outlier | Sibling | Delta |")
    lines.append("|--------|---------|---------|-------|")

    metrics = [
        ('mean_distance', 'Mean Distance'),
        ('variance', 'Variance'),
        ('kernel_contact_ratio', 'Kernel Contact Ratio'),
        ('longest_excursion', 'Longest Excursion'),
        ('oscillation_count', 'Oscillation Count'),
    ]

    for key, label in metrics:
        o_val = outlier_data.get(key, 0)
        s_val = sibling_data.get(key, 0)
        delta = o_val - s_val
        lines.append(f"| {label} | {o_val:.3f} | {s_val:.3f} | {delta:+.3f} |")

    lines.append(f"| Pattern | {outlier_data.get('pattern', 'unknown')} | {sibling_data.get('pattern', 'unknown')} | - |")

    # Interpretation
    lines.append("")
    lines.append("### Interpretation")

    if outlier_data['mean_distance'] > sibling_data['mean_distance']:
        lines.append("- Outlier maintains **greater distance** from kernel nodes")
    else:
        lines.append("- Outlier maintains **closer proximity** to kernel nodes")

    if outlier_data['longest_excursion'] > sibling_data['longest_excursion']:
        lines.append(f"- Outlier has **longer excursions** from kernel ({outlier_data['longest_excursion']} vs {sibling_data['longest_excursion']} tokens)")

    if outlier_data['pattern'] != sibling_data['pattern']:
        lines.append(f"- **Pattern mismatch**: outlier is {outlier_data['pattern']}, sibling is {sibling_data['pattern']}")

    return "\n".join(lines)

# ============================================================================
# TASK C: HAZARD-EDGE INTERACTION MAPS
# ============================================================================

def generate_hazard_map(folio: str, tokens: List[str]) -> Dict:
    """Generate hazard interaction map for a folio."""
    hazard_contacts = defaultdict(list)
    navigation_sequences = []
    current_nav_seq = []

    for i in range(1, len(tokens)):
        prev_token = tokens[i-1]
        curr_token = tokens[i]
        is_hazard, hazard_class = is_hazard_adjacent(prev_token, curr_token)

        if is_hazard and hazard_class:
            hazard_contacts[hazard_class].append(i)
            current_nav_seq.append(i)
        else:
            if len(current_nav_seq) >= 3:
                navigation_sequences.append({
                    'positions': current_nav_seq.copy(),
                    'length': len(current_nav_seq)
                })
            current_nav_seq = []

    # Check final sequence
    if len(current_nav_seq) >= 3:
        navigation_sequences.append({
            'positions': current_nav_seq.copy(),
            'length': len(current_nav_seq)
        })

    # Compute positional distribution (quartiles)
    total_len = len(tokens)
    q1_end = total_len // 4
    q2_end = total_len // 2
    q3_end = 3 * total_len // 4

    distribution = {hc: {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0} for hc in HAZARD_CLASSES}

    for hc, positions in hazard_contacts.items():
        for pos in positions:
            if pos <= q1_end:
                distribution[hc]['Q1'] += 1
            elif pos <= q2_end:
                distribution[hc]['Q2'] += 1
            elif pos <= q3_end:
                distribution[hc]['Q3'] += 1
            else:
                distribution[hc]['Q4'] += 1

    return {
        'folio': folio,
        'total_tokens': len(tokens),
        'hazard_contacts': dict(hazard_contacts),
        'navigation_sequences': navigation_sequences,
        'positional_distribution': distribution,
        'dominant_hazard': max(hazard_contacts.keys(), key=lambda k: len(hazard_contacts[k])) if hazard_contacts else None
    }

def generate_hazard_analysis_md(hazard_maps: List[Dict]) -> str:
    """Generate hazard interaction analysis markdown."""
    lines = []
    lines.append("# Hazard Interaction Analysis")
    lines.append(f"\n*Generated: {datetime.now().isoformat()}*\n")

    lines.append("## Summary by Hazard Class")
    lines.append("")

    # Aggregate by hazard class
    class_totals = defaultdict(lambda: {'total': 0, 'folios': []})

    for hmap in hazard_maps:
        for hc, positions in hmap['hazard_contacts'].items():
            class_totals[hc]['total'] += len(positions)
            class_totals[hc]['folios'].append((hmap['folio'], len(positions)))

    for hc in HAZARD_CLASSES:
        data = class_totals[hc]
        lines.append(f"### {hc}")
        lines.append(f"- **Total contacts:** {data['total']}")
        if data['folios']:
            top_folios = sorted(data['folios'], key=lambda x: -x[1])[:5]
            lines.append(f"- **Top folios:** {', '.join(f'{f[0]}({f[1]})' for f in top_folios)}")
        lines.append("")

    lines.append("## Navigation Sequences")
    lines.append("")
    lines.append("*Sequences of 3+ consecutive hazard-adjacent tokens*")
    lines.append("")

    for hmap in hazard_maps:
        if hmap['navigation_sequences']:
            lines.append(f"### {hmap['folio']}")
            for seq in hmap['navigation_sequences']:
                positions = seq['positions']
                lines.append(f"- Positions {positions[0]}-{positions[-1]} (length: {seq['length']})")
            lines.append("")

    lines.append("## Positional Distribution")
    lines.append("")
    lines.append("*Where hazard contacts occur: Q1=early, Q2=mid-early, Q3=mid-late, Q4=late*")
    lines.append("")

    for hmap in hazard_maps:
        lines.append(f"### {hmap['folio']}")
        dist = hmap['positional_distribution']
        lines.append("| Hazard Class | Q1 | Q2 | Q3 | Q4 |")
        lines.append("|--------------|----|----|----|----|")
        for hc in HAZARD_CLASSES:
            d = dist[hc]
            lines.append(f"| {hc} | {d['Q1']} | {d['Q2']} | {d['Q3']} | {d['Q4']} |")
        lines.append("")

    return "\n".join(lines)

# ============================================================================
# TASK D: RESET ANALYSIS (f57r CRITICAL)
# ============================================================================

def analyze_reset_folio(tokens: List[str], token_to_class: Dict[str, int]) -> Dict:
    """Perform deep reset analysis for f57r."""
    n = len(tokens)

    # Detect potential reset points
    # A reset is where the state returns to initial - look for patterns
    # that suggest reinitialization

    reset_candidates = []

    # Method 1: Look for repeated initial sequence
    if n > 10:
        initial_seq = tokens[:10]
        for i in range(10, n-10):
            if tokens[i:i+5] == tokens[:5]:
                reset_candidates.append({
                    'position': i,
                    'method': 'sequence_repeat',
                    'confidence': 'HIGH'
                })

    # Method 2: Look for kernel clustering after gap
    kernel_positions = [i for i, t in enumerate(tokens) if t in KERNEL_NODES or
                        compute_kernel_distance(t, KERNEL_NODES) == 1]

    if kernel_positions:
        # Find largest gap
        gaps = []
        for i in range(1, len(kernel_positions)):
            gap = kernel_positions[i] - kernel_positions[i-1]
            if gap > 10:
                gaps.append((kernel_positions[i], gap))

        for pos, gap in gaps:
            reset_candidates.append({
                'position': pos,
                'method': 'kernel_gap',
                'gap_size': gap,
                'confidence': 'MEDIUM'
            })

    # Method 3: Look for pattern break in 2-cycle structure
    # (change in token type distribution)
    window = 20
    type_changes = []
    for i in range(window, n-window, window//2):
        pre_types = Counter(token_to_class.get(t, 0) for t in tokens[i-window:i])
        post_types = Counter(token_to_class.get(t, 0) for t in tokens[i:i+window])

        # Compute distribution difference
        all_types = set(pre_types.keys()) | set(post_types.keys())
        diff = sum(abs(pre_types.get(t, 0) - post_types.get(t, 0)) for t in all_types)

        if diff > window * 0.5:
            type_changes.append({
                'position': i,
                'method': 'type_distribution_shift',
                'diff_score': diff,
                'confidence': 'LOW'
            })

    # Determine best reset point
    best_reset = None
    if reset_candidates:
        # Prioritize by confidence and method
        for rc in sorted(reset_candidates, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x['confidence'], 3)):
            best_reset = rc
            break
    elif type_changes:
        # Use strongest type change
        best_reset = max(type_changes, key=lambda x: x['diff_score'])

    # Segment analysis if reset found
    segments = {}
    if best_reset:
        reset_pos = best_reset['position']
        pre_reset = tokens[:reset_pos]
        post_reset = tokens[reset_pos:]

        # Compute separate signatures for each segment
        pre_trajectory = compute_kernel_trajectory(pre_reset)
        post_trajectory = compute_kernel_trajectory(post_reset)

        segments = {
            'pre_reset': {
                'length': len(pre_reset),
                'kernel_contact_ratio': pre_trajectory['kernel_contact_ratio'],
                'pattern': pre_trajectory['pattern'],
                'mean_distance': pre_trajectory['mean_distance']
            },
            'post_reset': {
                'length': len(post_reset),
                'kernel_contact_ratio': post_trajectory['kernel_contact_ratio'],
                'pattern': post_trajectory['pattern'],
                'mean_distance': post_trajectory['mean_distance']
            },
            'structural_similarity': abs(
                pre_trajectory['mean_distance'] - post_trajectory['mean_distance']
            ) < 0.5
        }

    # Hypothesis testing
    hypotheses = []

    if best_reset:
        # Repair maneuver: pre-reset shows degradation
        if segments.get('pre_reset', {}).get('mean_distance', 0) > segments.get('post_reset', {}).get('mean_distance', 0):
            hypotheses.append({
                'hypothesis': 'REPAIR_MANEUVER',
                'evidence': 'Pre-reset distance > post-reset distance (recovery from deviation)',
                'confidence': 'MEDIUM'
            })

        # Restart protocol: structurally similar before and after
        if segments.get('structural_similarity', False):
            hypotheses.append({
                'hypothesis': 'RESTART_PROTOCOL',
                'evidence': 'Structurally similar before and after reset',
                'confidence': 'HIGH'
            })
        else:
            hypotheses.append({
                'hypothesis': 'BOUNDARY_MARKER',
                'evidence': 'Structurally different before and after (regime change)',
                'confidence': 'HIGH'
            })

    return {
        'folio': 'f57r',
        'total_tokens': n,
        'reset_candidates': reset_candidates,
        'type_changes': type_changes,
        'best_reset': best_reset,
        'segments': segments,
        'hypotheses': hypotheses
    }

def generate_reset_analysis_md(reset_data: Dict, tokens: List[str]) -> str:
    """Generate reset analysis markdown for f57r."""
    lines = []
    lines.append("# Reset Analysis: f57r (CRITICAL)")
    lines.append(f"\n*Generated: {datetime.now().isoformat()}*\n")
    lines.append("---\n")

    lines.append("## Overview")
    lines.append("")
    lines.append("f57r is the **only folio** in the manuscript with `reset_present = true`.")
    lines.append("This demands focused analysis to understand how the system handles boundary conditions.")
    lines.append("")
    lines.append(f"- **Total tokens:** {reset_data['total_tokens']}")
    lines.append(f"- **Reset candidates identified:** {len(reset_data['reset_candidates'])}")
    lines.append(f"- **Type distribution shifts:** {len(reset_data['type_changes'])}")
    lines.append("")

    lines.append("## Reset Point Detection")
    lines.append("")

    if reset_data['best_reset']:
        br = reset_data['best_reset']
        lines.append(f"### Best Reset Point")
        lines.append(f"- **Position:** Token {br['position']}")
        lines.append(f"- **Detection method:** {br['method']}")
        lines.append(f"- **Confidence:** {br['confidence']}")
        if 'gap_size' in br:
            lines.append(f"- **Kernel gap size:** {br['gap_size']} tokens")
        lines.append("")
    else:
        lines.append("*No clear reset point identified via automated detection.*")
        lines.append("")

    lines.append("### All Candidates")
    lines.append("")
    for rc in reset_data['reset_candidates']:
        lines.append(f"- Position {rc['position']}: {rc['method']} (confidence: {rc['confidence']})")
    lines.append("")

    lines.append("## Segment Analysis")
    lines.append("")

    if reset_data['segments']:
        seg = reset_data['segments']
        lines.append("| Metric | Pre-Reset | Post-Reset |")
        lines.append("|--------|-----------|------------|")
        lines.append(f"| Length | {seg['pre_reset']['length']} | {seg['post_reset']['length']} |")
        lines.append(f"| Kernel Contact Ratio | {seg['pre_reset']['kernel_contact_ratio']:.3f} | {seg['post_reset']['kernel_contact_ratio']:.3f} |")
        lines.append(f"| Mean Distance | {seg['pre_reset']['mean_distance']:.3f} | {seg['post_reset']['mean_distance']:.3f} |")
        lines.append(f"| Pattern | {seg['pre_reset']['pattern']} | {seg['post_reset']['pattern']} |")
        lines.append("")
        lines.append(f"**Structural Similarity:** {'YES' if seg['structural_similarity'] else 'NO'}")
        lines.append("")
    else:
        lines.append("*No segments to analyze (no reset point identified).*")
        lines.append("")

    lines.append("## Hypothesis Testing")
    lines.append("")

    if reset_data['hypotheses']:
        for h in reset_data['hypotheses']:
            lines.append(f"### {h['hypothesis']}")
            lines.append(f"- **Evidence:** {h['evidence']}")
            lines.append(f"- **Confidence:** {h['confidence']}")
            lines.append("")
    else:
        lines.append("*No hypotheses generated (insufficient evidence).*")
        lines.append("")

    lines.append("## Token Context Around Reset")
    lines.append("")

    if reset_data['best_reset']:
        pos = reset_data['best_reset']['position']
        start = max(0, pos - 10)
        end = min(len(tokens), pos + 10)

        lines.append("```")
        for i in range(start, end):
            marker = " <-- RESET" if i == pos else ""
            lines.append(f"{i:04d}: {tokens[i]}{marker}")
        lines.append("```")
        lines.append("")

    lines.append("## Conclusion")
    lines.append("")

    if reset_data['hypotheses']:
        top_hypothesis = max(reset_data['hypotheses'],
                            key=lambda x: {'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}.get(x['confidence'], 0))
        lines.append(f"**Most likely interpretation:** {top_hypothesis['hypothesis']}")
        lines.append("")

        if top_hypothesis['hypothesis'] == 'RESTART_PROTOCOL':
            lines.append("This folio appears to encode a **deliberate restart protocol** - the control program")
            lines.append("reinitializes itself after completing one operational cycle. This suggests the folio")
            lines.append("may describe a procedure that can be repeated multiple times.")
        elif top_hypothesis['hypothesis'] == 'BOUNDARY_MARKER':
            lines.append("This folio marks a **regime boundary** - the control program transitions from one")
            lines.append("operating mode to another. This may represent a handoff between different phases")
            lines.append("of a larger process.")
        elif top_hypothesis['hypothesis'] == 'REPAIR_MANEUVER':
            lines.append("This folio contains a **repair maneuver** - the control program recovers from")
            lines.append("a deviation by resetting to a known good state. This demonstrates the system's")
            lines.append("error correction capability.")
    else:
        lines.append("Unable to determine reset function with high confidence.")

    return "\n".join(lines)

# ============================================================================
# TASK E: OUTLIER CLASSIFICATION
# ============================================================================

def classify_outlier(folio: str, tokens: List[str], signature: Dict,
                     trajectory: Dict, hazard_map: Dict,
                     baseline: Dict, reset_data: Optional[Dict] = None) -> Dict:
    """Classify an outlier folio."""
    classification = {
        'folio': folio,
        'classification': 'UNKNOWN',
        'confidence': 'LOW',
        'supporting_evidence': [],
        'alternative_interpretations': []
    }

    # Check for BOUNDARY_CONDITION indicators
    boundary_indicators = 0
    if folio == 'f57r' and reset_data:
        classification['classification'] = 'BOUNDARY_CONDITION'
        classification['confidence'] = 'HIGH'
        classification['supporting_evidence'].append('Only folio with reset_present=true')
        classification['supporting_evidence'].append('Contains restart/regime change point')
        return classification

    # Check terminal state
    term_state = signature.get('terminal_state', '')
    if term_state == 'initial':
        boundary_indicators += 2
        classification['supporting_evidence'].append(f'Terminal state is initial (reset behavior)')

    # Check for EXTENDED_RUN
    if signature.get('total_length', 0) > baseline.get('mean_length', 500) * 1.5:
        classification['classification'] = 'EXTENDED_RUN'
        classification['confidence'] = 'MEDIUM'
        classification['supporting_evidence'].append(f"Length {signature.get('total_length')} exceeds baseline by >50%")
        classification['alternative_interpretations'].append('Could be STRESSED_REGIME if hazard density high')

    # Check for STRESSED_REGIME
    if signature.get('hazard_density', 0) > baseline.get('mean_hazard_density', 0.5) * 1.3:
        if classification['classification'] != 'EXTENDED_RUN':
            classification['classification'] = 'STRESSED_REGIME'
            classification['confidence'] = 'MEDIUM'
        classification['supporting_evidence'].append(f"Hazard density {signature.get('hazard_density', 0):.3f} exceeds baseline")

    # Check trajectory pattern for RECOVERY_OPERATION
    if trajectory.get('pattern') == 'oscillating':
        if signature.get('recovery_ops_count', 0) > baseline.get('mean_recovery_ops', 10) * 1.5:
            classification['classification'] = 'RECOVERY_OPERATION'
            classification['confidence'] = 'MEDIUM'
            classification['supporting_evidence'].append('Oscillating trajectory pattern')
            classification['supporting_evidence'].append('High recovery operations count')

    # Check for SCRIBAL_ANOMALY
    if trajectory.get('pattern') == 'erratic' and signature.get('cycle_regularity', 5) < 1.0:
        classification['classification'] = 'SCRIBAL_ANOMALY'
        classification['confidence'] = 'LOW'
        classification['supporting_evidence'].append('Erratic trajectory pattern')
        classification['supporting_evidence'].append('Very low cycle regularity')
        classification['alternative_interpretations'].append('Could be BOUNDARY_CONDITION if deliberate')

    # If still UNKNOWN, provide best guess
    if classification['classification'] == 'UNKNOWN':
        # Use trajectory pattern as hint
        pattern = trajectory.get('pattern', 'unknown')
        if pattern == 'stable':
            classification['alternative_interpretations'].append('Possibly normal with measurement noise')
        elif pattern == 'drifting':
            classification['alternative_interpretations'].append('Possibly STRESSED_REGIME with gradual degradation')

    return classification

# ============================================================================
# TASK F: BASELINE PROFILE
# ============================================================================

def compute_baseline_profile(all_signatures: Dict, all_trajectories: Dict,
                             outlier_folios: Set[str]) -> Dict:
    """Compute baseline profile from non-outlier folios."""
    non_outlier_sigs = {f: s for f, s in all_signatures.items() if f not in outlier_folios}

    if not non_outlier_sigs:
        return {}

    # Compute mean values
    metrics = ['total_length', 'cycle_count', 'cycle_regularity', 'link_density',
               'kernel_distance_mean', 'kernel_contact_ratio', 'hazard_density',
               'near_miss_count', 'recovery_ops_count', 'phase_ordering_rigidity']

    baseline = {}
    for metric in metrics:
        values = [s.get(metric, 0) for s in non_outlier_sigs.values() if metric in s]
        if values:
            baseline[f'mean_{metric}'] = sum(values) / len(values)
            baseline[f'std_{metric}'] = (sum((v - baseline[f'mean_{metric}'])**2 for v in values) / len(values)) ** 0.5

    # Trajectory patterns
    patterns = [t.get('pattern', 'unknown') for f, t in all_trajectories.items() if f not in outlier_folios]
    if patterns:
        baseline['typical_pattern'] = max(set(patterns), key=patterns.count)
        baseline['pattern_distribution'] = dict(Counter(patterns))

    # Terminal states
    term_states = [s.get('terminal_state', 'unknown') for s in non_outlier_sigs.values()]
    if term_states:
        baseline['typical_terminal_state'] = max(set(term_states), key=term_states.count)
        baseline['terminal_state_distribution'] = dict(Counter(term_states))

    baseline['sample_size'] = len(non_outlier_sigs)

    return baseline

def generate_baseline_profile_md(baseline: Dict, sample_folios: List[str]) -> str:
    """Generate baseline profile markdown."""
    lines = []
    lines.append("# Baseline Control Profile")
    lines.append(f"\n*Generated: {datetime.now().isoformat()}*\n")
    lines.append("---\n")

    lines.append("## Overview")
    lines.append("")
    lines.append(f"This profile is computed from **{baseline.get('sample_size', 0)} non-outlier folios**.")
    lines.append("It establishes what 'normal' control behavior looks like in the Voynich manuscript.")
    lines.append("")

    lines.append("## Sample Folios")
    lines.append("")
    for f in sample_folios[:5]:
        lines.append(f"- {f}")
    lines.append("")

    lines.append("## Signature Statistics")
    lines.append("")
    lines.append("| Metric | Mean | Std Dev |")
    lines.append("|--------|------|---------|")

    metrics = ['total_length', 'cycle_count', 'cycle_regularity', 'link_density',
               'kernel_distance_mean', 'kernel_contact_ratio', 'hazard_density',
               'near_miss_count', 'recovery_ops_count', 'phase_ordering_rigidity']

    for m in metrics:
        mean = baseline.get(f'mean_{m}', 0)
        std = baseline.get(f'std_{m}', 0)
        lines.append(f"| {m} | {mean:.3f} | {std:.3f} |")
    lines.append("")

    lines.append("## Typical Patterns")
    lines.append("")
    lines.append(f"- **Typical trajectory pattern:** {baseline.get('typical_pattern', 'unknown')}")

    if 'pattern_distribution' in baseline:
        lines.append("- **Pattern distribution:**")
        for p, c in baseline['pattern_distribution'].items():
            lines.append(f"  - {p}: {c}")
    lines.append("")

    lines.append(f"- **Typical terminal state:** {baseline.get('typical_terminal_state', 'unknown')}")

    if 'terminal_state_distribution' in baseline:
        lines.append("- **Terminal state distribution:**")
        for s, c in baseline['terminal_state_distribution'].items():
            lines.append(f"  - {s}: {c}")
    lines.append("")

    lines.append("## Canonical Control Profile")
    lines.append("")
    lines.append("A 'normal' Voynich folio exhibits:")
    lines.append("")
    lines.append(f"1. **Length:** ~{baseline.get('mean_total_length', 0):.0f} tokens")
    lines.append(f"2. **Cycle count:** ~{baseline.get('mean_cycle_count', 0):.0f} cycles")
    lines.append(f"3. **Kernel contact ratio:** ~{baseline.get('mean_kernel_contact_ratio', 0):.2f}")
    lines.append(f"4. **Hazard density:** ~{baseline.get('mean_hazard_density', 0):.2f}")
    lines.append(f"5. **Trajectory pattern:** {baseline.get('typical_pattern', 'unknown')}")
    lines.append(f"6. **Terminal state:** {baseline.get('typical_terminal_state', 'unknown')}")

    return "\n".join(lines)

# ============================================================================
# FIND NEAREST SIBLING
# ============================================================================

def find_nearest_sibling(outlier_folio: str, family: int, all_signatures: Dict,
                          outlier_folios: Set[str]) -> Optional[str]:
    """Find the nearest non-outlier folio in the same family."""
    outlier_sig = all_signatures.get(outlier_folio, {})
    if not outlier_sig:
        return None

    best_sibling = None
    best_distance = float('inf')

    # Key signature dimensions for comparison
    dims = ['cycle_count', 'link_density', 'kernel_distance_mean',
            'hazard_density', 'phase_ordering_rigidity']

    for folio, sig in all_signatures.items():
        if folio in outlier_folios:
            continue

        # Check family match
        # We'll approximate family by recipe characteristics
        # For now, use signature similarity

        distance = sum(abs(outlier_sig.get(d, 0) - sig.get(d, 0)) for d in dims)

        if distance < best_distance:
            best_distance = distance
            best_sibling = folio

    return best_sibling

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("PHASE 23: REGIME BOUNDARY ANALYSIS")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Create output directories
    os.makedirs('outlier_traces', exist_ok=True)
    os.makedirs('kernel_trajectories', exist_ok=True)
    os.makedirs('hazard_maps', exist_ok=True)

    # Load data
    print("Loading data...")
    folio_tokens = load_transcription_data()
    print(f"  Loaded tokens for {len(folio_tokens)} folios")

    control_signatures = load_control_signatures()
    signatures = control_signatures.get('signatures', {})
    print(f"  Loaded signatures for {len(signatures)} folios")

    equivalence = load_operator_equivalence()
    token_to_class = build_token_to_class_map(equivalence)
    print(f"  Built token-to-class map with {len(token_to_class)} entries")

    topology = load_internal_topology()
    node_types = get_node_types(topology)
    print(f"  Loaded topology with {len(node_types)} node types")

    outlier_folios = set(PRIORITY_OUTLIERS.keys())

    # Storage for results
    all_trajectories = {}
    all_hazard_maps = []
    all_classifications = []

    print()
    print("=" * 70)
    print("TASK A & B: Control Traces and Kernel Trajectories")
    print("=" * 70)

    # Process all folios for trajectories (needed for baseline)
    for folio in signatures.keys():
        tokens = folio_tokens.get(folio, [])
        if tokens:
            traj = compute_kernel_trajectory(tokens)
            all_trajectories[folio] = traj

    # Process priority outliers
    for folio, info in PRIORITY_OUTLIERS.items():
        print(f"\nProcessing {folio} (Priority: {info['priority']})...")

        tokens = folio_tokens.get(folio, [])
        if not tokens:
            print(f"  WARNING: No tokens found for {folio}")
            continue

        # Task A: Control Trace
        trace = generate_control_trace(folio, tokens, token_to_class)
        trace_path = f"outlier_traces/{folio}_control_trace.md"
        with open(trace_path, 'w', encoding='utf-8') as f:
            f.write(trace)
        print(f"  Generated control trace: {trace_path}")

        # Task B: Kernel Trajectory
        trajectory = all_trajectories.get(folio, compute_kernel_trajectory(tokens))
        traj_path = f"kernel_trajectories/{folio}_trajectory.json"

        # Save trajectory data
        traj_data = {
            'folio': folio,
            'metadata': {
                'total_tokens': len(tokens),
                'family': info['family'],
                'priority': info['priority']
            },
            'statistics': {
                'mean_distance': trajectory['mean_distance'],
                'variance': trajectory['variance'],
                'kernel_contact_count': trajectory['kernel_contact_count'],
                'kernel_contact_ratio': trajectory['kernel_contact_ratio'],
                'longest_excursion': trajectory['longest_excursion'],
                'oscillation_count': trajectory['oscillation_count'],
                'pattern': trajectory['pattern']
            },
            'trajectory': trajectory['trajectory'][:100]  # First 100 for preview
        }
        with open(traj_path, 'w', encoding='utf-8') as f:
            json.dump(traj_data, f, indent=2)
        print(f"  Generated trajectory: {traj_path}")

        # Task C: Hazard Map
        hazard_map = generate_hazard_map(folio, tokens)
        all_hazard_maps.append(hazard_map)

        hmap_path = f"hazard_maps/{folio}_hazard_map.json"
        with open(hmap_path, 'w', encoding='utf-8') as f:
            json.dump(hazard_map, f, indent=2)
        print(f"  Generated hazard map: {hmap_path}")

    print()
    print("=" * 70)
    print("TASK D: Reset Analysis (f57r CRITICAL)")
    print("=" * 70)

    f57r_tokens = folio_tokens.get('f57r', [])
    if f57r_tokens:
        reset_analysis = analyze_reset_folio(f57r_tokens, token_to_class)

        reset_md = generate_reset_analysis_md(reset_analysis, f57r_tokens)
        with open('reset_analysis_f57r.md', 'w', encoding='utf-8') as f:
            f.write(reset_md)
        print("Generated: reset_analysis_f57r.md")

        # Save raw analysis
        with open('reset_analysis_f57r.json', 'w', encoding='utf-8') as f:
            # Convert to serializable
            serializable = {
                'folio': reset_analysis['folio'],
                'total_tokens': reset_analysis['total_tokens'],
                'reset_candidates': reset_analysis['reset_candidates'],
                'best_reset': reset_analysis['best_reset'],
                'segments': reset_analysis['segments'],
                'hypotheses': reset_analysis['hypotheses']
            }
            json.dump(serializable, f, indent=2)
        print("Generated: reset_analysis_f57r.json")
    else:
        print("WARNING: No tokens found for f57r")
        reset_analysis = None

    print()
    print("=" * 70)
    print("TASK F: Baseline Profile")
    print("=" * 70)

    baseline = compute_baseline_profile(signatures, all_trajectories, outlier_folios)

    # Get sample non-outlier folios
    sample_folios = [f for f in signatures.keys() if f not in outlier_folios][:10]

    baseline_md = generate_baseline_profile_md(baseline, sample_folios)
    with open('baseline_profile.md', 'w', encoding='utf-8') as f:
        f.write(baseline_md)
    print("Generated: baseline_profile.md")

    print()
    print("=" * 70)
    print("TASK E: Outlier Classification")
    print("=" * 70)

    for folio, info in PRIORITY_OUTLIERS.items():
        tokens = folio_tokens.get(folio, [])
        sig = signatures.get(folio, {})
        traj = all_trajectories.get(folio, {})
        hmap = next((h for h in all_hazard_maps if h['folio'] == folio), {})

        reset_data = reset_analysis if folio == 'f57r' else None

        classification = classify_outlier(folio, tokens, sig, traj, hmap, baseline, reset_data)
        all_classifications.append(classification)
        print(f"  {folio}: {classification['classification']} ({classification['confidence']})")

    # Generate classification report
    lines = []
    lines.append("# Outlier Classification Report")
    lines.append(f"\n*Generated: {datetime.now().isoformat()}*\n")
    lines.append("---\n")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Folio | Classification | Confidence |")
    lines.append("|-------|----------------|------------|")
    for c in all_classifications:
        lines.append(f"| {c['folio']} | {c['classification']} | {c['confidence']} |")
    lines.append("")

    lines.append("## Classification Legend")
    lines.append("")
    lines.append("| Classification | Definition |")
    lines.append("|----------------|------------|")
    lines.append("| BOUNDARY_CONDITION | Represents startup, shutdown, or regime edge |")
    lines.append("| RECOVERY_OPERATION | Contains repair/reset sequences for deviation correction |")
    lines.append("| STRESSED_REGIME | Normal operation under extreme parameters |")
    lines.append("| EXTENDED_RUN | Same control logic, just longer duration |")
    lines.append("| SCRIBAL_ANOMALY | Structural irregularities suggesting copying error |")
    lines.append("| UNKNOWN | Cannot classify with available evidence |")
    lines.append("")

    lines.append("## Detailed Classifications")
    lines.append("")

    for c in all_classifications:
        lines.append(f"### {c['folio']}")
        lines.append(f"**Classification:** {c['classification']}")
        lines.append(f"**Confidence:** {c['confidence']}")
        lines.append("")

        if c['supporting_evidence']:
            lines.append("**Supporting Evidence:**")
            for e in c['supporting_evidence']:
                lines.append(f"- {e}")
            lines.append("")

        if c['alternative_interpretations']:
            lines.append("**Alternative Interpretations:**")
            for a in c['alternative_interpretations']:
                lines.append(f"- {a}")
            lines.append("")

        lines.append("---")
        lines.append("")

    with open('outlier_classification.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print("\nGenerated: outlier_classification.md")

    # Generate hazard analysis
    hazard_analysis_md = generate_hazard_analysis_md(all_hazard_maps)
    with open('hazard_interaction_analysis.md', 'w', encoding='utf-8') as f:
        f.write(hazard_analysis_md)
    print("Generated: hazard_interaction_analysis.md")

    # Generate trajectory comparison
    print()
    print("Generating trajectory comparisons...")

    comparison_lines = []
    comparison_lines.append("# Kernel Trajectory Comparison")
    comparison_lines.append(f"\n*Generated: {datetime.now().isoformat()}*\n")
    comparison_lines.append("---\n")

    for folio, info in PRIORITY_OUTLIERS.items():
        sibling = find_nearest_sibling(folio, info['family'], signatures, outlier_folios)

        if sibling and folio in all_trajectories and sibling in all_trajectories:
            comparison = generate_trajectory_comparison(
                all_trajectories[folio],
                all_trajectories[sibling],
                folio,
                sibling
            )
            comparison_lines.append(comparison)
            comparison_lines.append("\n---\n")

    with open('kernel_trajectory_comparison.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(comparison_lines))
    print("Generated: kernel_trajectory_comparison.md")

    print()
    print("=" * 70)
    print("PHASE 23 COMPLETE")
    print("=" * 70)
    print()
    print("Deliverables generated:")
    print("  - outlier_traces/[folio]_control_trace.md (per outlier)")
    print("  - kernel_trajectories/[folio]_trajectory.json (per outlier)")
    print("  - hazard_maps/[folio]_hazard_map.json (per outlier)")
    print("  - kernel_trajectory_comparison.md")
    print("  - hazard_interaction_analysis.md")
    print("  - reset_analysis_f57r.md (CRITICAL)")
    print("  - reset_analysis_f57r.json")
    print("  - outlier_classification.md")
    print("  - baseline_profile.md")
    print()
    print(f"Completed: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
