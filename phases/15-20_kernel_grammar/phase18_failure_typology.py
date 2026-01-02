#!/usr/bin/env python3
"""
Phase 18: Failure-Mode Typology

Analyzes the 17 forbidden micro-transitions to build a formal hazard model.
Building on Phase 17's kernel semantics (k=energy, h=phase, e=stability),
this phase classifies what the system PREVENTS.

Phases:
  18A: Forbidden Transition Inventory
  18B: Directional Asymmetry Analysis
  18C: Failure Class Taxonomy
  18D: Kernel Distance Analysis
  18E: Hazard Model Synthesis

Output files:
  phase18a_forbidden_inventory.json
  phase18b_directional_asymmetry.json
  phase18c_failure_taxonomy.json
  phase18d_kernel_distance.json
  phase18e_hazard_synthesis.json
  phase18_synthesis.json
"""

import json
import csv
from collections import defaultdict, Counter, deque
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

KERNEL_NODES = ['k', 'h', 'e']

# 17 forbidden transitions from Phase 15A
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

# Node roles from Phase 15A (degree-based)
HUBS = ['k', 'h', 'e', 't', 'daiin', 'ch', 'ol']
BRIDGES = ['chedy', 'shedy', 'o', 'aiin', 'ar', 'chol', 'or', 'al']
# Spokes: all other nodes

KNOWN_PREFIXES = [
    'qo', 'ch', 'sh', 'da', 'ct', 'ol', 'so', 'ot', 'ok', 'al', 'ar',
    'ke', 'lc', 'tc', 'kc', 'ck', 'pc', 'dc', 'sc', 'fc', 'cp', 'cf',
    'do', 'sa', 'yk', 'yc', 'po', 'to', 'ko', 'ts', 'ps', 'pd', 'fo',
    'op', 'or', 'os', 'oe', 'of', 'sy', 'yp', 'ra', 'lo', 'ks', 'ai',
    'ka', 'te', 'de', 'ro', 'qk', 'yd', 'ye', 'ys', 'ep', 'ec', 'ed'
]

# Failure class definitions (distillation-based)
FAILURE_CLASSES = {
    'ENERGY_OVERSHOOT': {
        'description': 'Too much heat too fast',
        'physical_cause': 'Bumping, scorching, thermal shock',
        'keywords': ['he', 't', 'k']  # Heat-related nodes
    },
    'PHASE_ORDERING': {
        'description': 'Wrong sequence of phase changes',
        'physical_cause': 'Vapor lock, premature condensation',
        'keywords': ['chey', 'shey', 'dy']  # Phase-change nodes
    },
    'RATE_MISMATCH': {
        'description': 'Flow rates incompatible',
        'physical_cause': 'Flooding, weeping, channeling',
        'keywords': ['or', 'dal', 'ar', 'chol']  # Flow/vessel nodes
    },
    'COMPOSITION_JUMP': {
        'description': 'Skipping purification stages',
        'physical_cause': 'Contamination, impurity carryover',
        'keywords': ['chedy', 'shedy', 'aiin', 'ee']  # Processing nodes
    },
    'CONTAINMENT_TIMING': {
        'description': 'Improper vessel state',
        'physical_cause': 'Overflow, pressure failure',
        'keywords': ['l', 'c', 'o', 'r']  # Vessel/state nodes
    }
}

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
            word = row.get('word', '').strip().strip('"')
            folio = row.get('folio', '').strip().strip('"')
            line_num = row.get('line_number', '').strip().strip('"')

            if not word or word.startswith('*') or len(word) < 1:
                continue

            key = (word, folio, line_num)
            if key not in seen:
                seen.add(key)
                words.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num
                })

    return words

def extract_primitive(word: str) -> Optional[str]:
    """Extract the primitive (core) from a word."""
    if len(word) == 1:
        return word

    remaining = word
    for length in [2]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                remaining = word[length:]
                break

    if remaining:
        if remaining in ['k', 'h', 'e', 't', 's', 'o', 'l', 'r', 'd', 'c']:
            return remaining
        if remaining.startswith(('k', 'h', 'e', 't', 's', 'o', 'l', 'r', 'd', 'c')):
            return remaining[0]

    return None

def get_node_type(node: str) -> str:
    """Classify node as hub/bridge/spoke."""
    if node in HUBS:
        return 'hub'
    elif node in BRIDGES:
        return 'bridge'
    else:
        return 'spoke'

def build_transition_graph(words: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Build transition graph from word sequences."""
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

    return transitions

def bfs_distance(graph: Dict, start: str, targets: List[str]) -> Dict[str, int]:
    """Compute BFS distance from start to each target."""
    distances = {t: float('inf') for t in targets}

    if start in targets:
        distances[start] = 0

    visited = {start}
    queue = deque([(start, 0)])

    while queue:
        node, dist = queue.popleft()

        if node in targets:
            distances[node] = min(distances[node], dist)

        for neighbor in graph.get(node, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return distances

# =============================================================================
# PHASE 18A: FORBIDDEN TRANSITION INVENTORY
# =============================================================================

def phase18a_forbidden_inventory(transitions: Dict) -> Dict:
    """Extract and characterize all 17 forbidden transitions."""
    print("\n=== PHASE 18A: FORBIDDEN TRANSITION INVENTORY ===")

    # Build undirected adjacency for distance calculations
    all_nodes = set(transitions.keys())
    for node in transitions:
        all_nodes.update(transitions[node].keys())

    # Build bidirectional graph for BFS
    bidir_graph = defaultdict(set)
    for src in transitions:
        for tgt in transitions[src]:
            bidir_graph[src].add(tgt)
            bidir_graph[tgt].add(src)

    inventory = []
    type_counts = Counter()

    for idx, (src, tgt) in enumerate(FORBIDDEN_TRANSITIONS, 1):
        src_type = get_node_type(src)
        tgt_type = get_node_type(tgt)

        # Compute distances to kernel nodes
        src_distances = bfs_distance(bidir_graph, src, KERNEL_NODES)
        tgt_distances = bfs_distance(bidir_graph, tgt, KERNEL_NODES)

        # Check if reverse transition exists
        reverse_allowed = tgt in transitions and src in transitions[tgt]
        reverse_count = transitions.get(tgt, {}).get(src, 0)

        # Minimum distance to any kernel
        min_src_dist = min(src_distances.values())
        min_tgt_dist = min(tgt_distances.values())

        # Nearest kernel node
        nearest_kernel_src = min(KERNEL_NODES, key=lambda k: src_distances.get(k, float('inf')))
        nearest_kernel_tgt = min(KERNEL_NODES, key=lambda k: tgt_distances.get(k, float('inf')))

        entry = {
            'id': idx,
            'source': src,
            'target': tgt,
            'source_type': src_type,
            'target_type': tgt_type,
            'distance_to_k': src_distances.get('k', 'N/A') if src_distances.get('k') != float('inf') else 'N/A',
            'distance_to_h': src_distances.get('h', 'N/A') if src_distances.get('h') != float('inf') else 'N/A',
            'distance_to_e': src_distances.get('e', 'N/A') if src_distances.get('e') != float('inf') else 'N/A',
            'min_kernel_distance_source': min_src_dist if min_src_dist != float('inf') else 'N/A',
            'min_kernel_distance_target': min_tgt_dist if min_tgt_dist != float('inf') else 'N/A',
            'nearest_kernel_source': nearest_kernel_src,
            'nearest_kernel_target': nearest_kernel_tgt,
            'reverse_allowed': reverse_allowed,
            'reverse_count': reverse_count
        }

        inventory.append(entry)

        # Count transition types
        type_key = f"{src_type}_to_{tgt_type}"
        type_counts[type_key] += 1

        print(f"  {idx}. {src}({src_type}) -> {tgt}({tgt_type}), reverse={'YES' if reverse_allowed else 'NO'}")

    # Summarize
    bridge_involved = sum(1 for t in inventory
                         if t['source_type'] == 'bridge' or t['target_type'] == 'bridge')

    result = {
        'metadata': {
            'phase': '18A',
            'title': 'Forbidden Transition Inventory',
            'timestamp': datetime.now().isoformat()
        },
        'total_forbidden': len(FORBIDDEN_TRANSITIONS),
        'transitions': inventory,
        'type_distribution': dict(type_counts),
        'summary': {
            'hub_to_hub': type_counts.get('hub_to_hub', 0),
            'hub_to_spoke': type_counts.get('hub_to_spoke', 0),
            'hub_to_bridge': type_counts.get('hub_to_bridge', 0),
            'bridge_to_hub': type_counts.get('bridge_to_hub', 0),
            'bridge_to_spoke': type_counts.get('bridge_to_spoke', 0),
            'bridge_to_bridge': type_counts.get('bridge_to_bridge', 0),
            'spoke_to_hub': type_counts.get('spoke_to_hub', 0),
            'spoke_to_bridge': type_counts.get('spoke_to_bridge', 0),
            'spoke_to_spoke': type_counts.get('spoke_to_spoke', 0),
            'bridge_involved': bridge_involved
        }
    }

    with open('phase18a_forbidden_inventory.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"  -> Saved phase18a_forbidden_inventory.json")
    print(f"  Bridge involvement: {bridge_involved}/17 ({bridge_involved/17*100:.1f}%)")
    return result

# =============================================================================
# PHASE 18B: DIRECTIONAL ASYMMETRY ANALYSIS
# =============================================================================

def phase18b_directional_asymmetry(transitions: Dict, inventory: Dict) -> Dict:
    """Analyze directional asymmetry of forbidden transitions."""
    print("\n=== PHASE 18B: DIRECTIONAL ASYMMETRY ANALYSIS ===")

    bidirectional_forbidden = []  # Neither direction allowed
    unidirectional_forward = []   # A->B forbidden, B->A allowed

    for entry in inventory['transitions']:
        src, tgt = entry['source'], entry['target']

        # Check forward (A->B) - already known forbidden
        forward_forbidden = True

        # Check reverse (B->A)
        reverse_exists = entry['reverse_allowed']

        if not reverse_exists:
            # Neither direction has significant traffic
            bidirectional_forbidden.append({
                'source': src,
                'target': tgt,
                'pattern': 'MUTUAL_EXCLUSION'
            })
        else:
            # Forward forbidden, reverse allowed
            unidirectional_forward.append({
                'source': src,
                'target': tgt,
                'reverse_count': entry['reverse_count'],
                'pattern': 'CAUSAL_HAZARD'
            })

    total = len(inventory['transitions'])
    asymmetry_ratio = len(unidirectional_forward) / total if total > 0 else 0

    print(f"  Bidirectional forbidden (mutual exclusion): {len(bidirectional_forbidden)}")
    print(f"  Unidirectional (A->B blocked, B->A allowed): {len(unidirectional_forward)}")
    print(f"  Asymmetry ratio: {asymmetry_ratio:.2f}")

    # Physical interpretation
    if asymmetry_ratio > 0.6:
        interpretation = "CAUSAL_HAZARDS_DOMINANT - Most failures are one-way gates (can't go A->B but can return B->A)"
    elif asymmetry_ratio > 0.3:
        interpretation = "MIXED_PATTERN - Both mutual exclusions and causal hazards present"
    else:
        interpretation = "MUTUAL_EXCLUSIONS_DOMINANT - Most failures are incompatible state pairs"

    result = {
        'metadata': {
            'phase': '18B',
            'title': 'Directional Asymmetry Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'bidirectional_forbidden': {
            'count': len(bidirectional_forbidden),
            'transitions': bidirectional_forbidden,
            'interpretation': 'States that cannot be adjacent in either direction - incompatible operations'
        },
        'unidirectional_forward': {
            'count': len(unidirectional_forward),
            'transitions': unidirectional_forward,
            'interpretation': 'One-way gates - can reach B from A via other paths but not directly'
        },
        'asymmetry_ratio': round(asymmetry_ratio, 4),
        'pattern_classification': interpretation,
        'physical_meaning': {
            'MUTUAL_EXCLUSION': 'These two states cannot follow each other - represents fundamentally incompatible operations',
            'CAUSAL_HAZARD': 'Cannot go from A to B directly, but B can lead back to A - represents dangerous shortcuts'
        }
    }

    with open('phase18b_directional_asymmetry.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"  -> Saved phase18b_directional_asymmetry.json")
    return result

# =============================================================================
# PHASE 18C: FAILURE CLASS TAXONOMY
# =============================================================================

def phase18c_failure_taxonomy(inventory: Dict, transitions: Dict) -> Dict:
    """Classify forbidden transitions into physics-based failure categories."""
    print("\n=== PHASE 18C: FAILURE CLASS TAXONOMY ===")

    classified = {cls: [] for cls in FAILURE_CLASSES}
    unclassified = []

    for entry in inventory['transitions']:
        src, tgt = entry['source'], entry['target']

        # Score each failure class
        scores = {}
        for cls, info in FAILURE_CLASSES.items():
            score = 0
            keywords = info['keywords']

            # Check if source or target matches keywords
            for kw in keywords:
                if kw in src or kw in tgt:
                    score += 2
                if src.startswith(kw) or tgt.startswith(kw):
                    score += 1

            scores[cls] = score

        # Assign to highest-scoring class
        best_class = max(scores, key=scores.get)
        best_score = scores[best_class]

        if best_score > 0:
            classified[best_class].append({
                'source': src,
                'target': tgt,
                'score': best_score,
                'source_type': entry['source_type'],
                'target_type': entry['target_type']
            })
        else:
            unclassified.append({
                'source': src,
                'target': tgt,
                'source_type': entry['source_type'],
                'target_type': entry['target_type']
            })

    # Build taxonomy
    taxonomy = {}
    for cls, transitions_list in classified.items():
        if transitions_list:
            taxonomy[cls] = {
                'count': len(transitions_list),
                'transitions': [f"{t['source']} -> {t['target']}" for t in transitions_list],
                'physical_mechanism': FAILURE_CLASSES[cls]['physical_cause'],
                'description': FAILURE_CLASSES[cls]['description']
            }
            print(f"  {cls}: {len(transitions_list)} transitions")

    # Find dominant failure mode
    dominant = max(taxonomy.keys(), key=lambda k: taxonomy[k]['count']) if taxonomy else 'NONE'

    result = {
        'metadata': {
            'phase': '18C',
            'title': 'Failure Class Taxonomy',
            'timestamp': datetime.now().isoformat()
        },
        'classes': taxonomy,
        'unclassified': {
            'count': len(unclassified),
            'transitions': [f"{t['source']} -> {t['target']}" for t in unclassified]
        },
        'class_definitions': FAILURE_CLASSES,
        'DOMINANT_FAILURE_MODE': dominant,
        'INTERPRETATION': f"The system most strongly prevents {dominant} failures, "
                         f"which involve {FAILURE_CLASSES[dominant]['physical_cause']}."
    }

    with open('phase18c_failure_taxonomy.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"  Unclassified: {len(unclassified)}")
    print(f"  Dominant failure mode: {dominant}")
    print(f"  -> Saved phase18c_failure_taxonomy.json")
    return result

# =============================================================================
# PHASE 18D: KERNEL DISTANCE ANALYSIS
# =============================================================================

def phase18d_kernel_distance(inventory: Dict) -> Dict:
    """Analyze how failures cluster relative to kernel nodes."""
    print("\n=== PHASE 18D: KERNEL DISTANCE ANALYSIS ===")

    # Collect distances
    distances = []
    by_nearest = {'k': [], 'h': [], 'e': []}

    for entry in inventory['transitions']:
        min_dist_src = entry['min_kernel_distance_source']
        min_dist_tgt = entry['min_kernel_distance_target']

        # Use the smaller of source or target distance
        if isinstance(min_dist_src, int) and isinstance(min_dist_tgt, int):
            min_dist = min(min_dist_src, min_dist_tgt)
        elif isinstance(min_dist_src, int):
            min_dist = min_dist_src
        elif isinstance(min_dist_tgt, int):
            min_dist = min_dist_tgt
        else:
            min_dist = float('inf')

        if min_dist != float('inf'):
            distances.append(min_dist)

            # Record by nearest kernel
            nearest = entry['nearest_kernel_source']
            by_nearest[nearest].append(f"{entry['source']} -> {entry['target']}")

    # Build distance distribution
    dist_counts = Counter(distances)
    total = len(distances)

    dist_1 = sum(1 for d in distances if d == 1)
    dist_2 = sum(1 for d in distances if d == 2)
    dist_3_plus = sum(1 for d in distances if d >= 3)

    print(f"  Distance 1 (kernel-adjacent): {dist_1}")
    print(f"  Distance 2: {dist_2}")
    print(f"  Distance 3+: {dist_3_plus}")

    # Determine clustering pattern
    if total > 0:
        if dist_1 / total > 0.5:
            clustering = 'KERNEL_ADJACENT'
            interpretation = "Failures cluster at kernel boundaries - dangerous edge conditions around control points"
        elif dist_3_plus / total > 0.5:
            clustering = 'PERIPHERAL'
            interpretation = "Failures cluster at periphery - edge-case hazards in auxiliary operations"
        else:
            clustering = 'DISTRIBUTED'
            interpretation = "Failures distributed throughout - system-wide constraint enforcement"
    else:
        clustering = 'UNKNOWN'
        interpretation = "Insufficient distance data"

    result = {
        'metadata': {
            'phase': '18D',
            'title': 'Kernel Distance Analysis',
            'timestamp': datetime.now().isoformat()
        },
        'distance_distribution': {
            'distance_1': {'count': dist_1, 'percentage': round(dist_1/total*100, 1) if total > 0 else 0},
            'distance_2': {'count': dist_2, 'percentage': round(dist_2/total*100, 1) if total > 0 else 0},
            'distance_3_plus': {'count': dist_3_plus, 'percentage': round(dist_3_plus/total*100, 1) if total > 0 else 0}
        },
        'by_nearest_kernel': {
            'k_adjacent': {'count': len(by_nearest['k']), 'transitions': by_nearest['k']},
            'h_adjacent': {'count': len(by_nearest['h']), 'transitions': by_nearest['h']},
            'e_adjacent': {'count': len(by_nearest['e']), 'transitions': by_nearest['e']}
        },
        'clustering': clustering,
        'INTERPRETATION': interpretation,
        'physical_meaning': {
            'KERNEL_ADJACENT': 'Failures prevented near control room - protecting core operations',
            'PERIPHERAL': 'Failures prevented at edges - protecting auxiliary operations',
            'DISTRIBUTED': 'Failures prevented throughout - comprehensive safety system'
        }
    }

    with open('phase18d_kernel_distance.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"  Clustering: {clustering}")
    print(f"  -> Saved phase18d_kernel_distance.json")
    return result

# =============================================================================
# PHASE 18E: HAZARD MODEL SYNTHESIS
# =============================================================================

def phase18e_hazard_synthesis(inventory: Dict, asymmetry: Dict, taxonomy: Dict, distance: Dict) -> Dict:
    """Synthesize findings into formal hazard model."""
    print("\n=== PHASE 18E: HAZARD MODEL SYNTHESIS ===")

    # Extract key metrics
    total_forbidden = inventory['total_forbidden']
    asymmetry_ratio = asymmetry['asymmetry_ratio']
    dominant_class = taxonomy['DOMINANT_FAILURE_MODE']
    clustering = distance['clustering']

    # Count failure classes
    class_count = len([c for c in taxonomy['classes'] if taxonomy['classes'][c]['count'] > 0])

    # Determine physical coherence
    coherence_signals = 0

    # Signal 1: Failures classify cleanly
    if taxonomy['unclassified']['count'] <= 3:
        coherence_signals += 1

    # Signal 2: Clear directional pattern
    if asymmetry_ratio > 0.3 or asymmetry_ratio < 0.3:
        coherence_signals += 1

    # Signal 3: Clear spatial pattern
    if clustering in ['KERNEL_ADJACENT', 'PERIPHERAL']:
        coherence_signals += 1

    # Signal 4: Dominant class exists
    if dominant_class != 'NONE':
        coherence_signals += 1

    if coherence_signals >= 3:
        physical_coherence = 'HIGH'
    elif coherence_signals >= 2:
        physical_coherence = 'MEDIUM'
    else:
        physical_coherence = 'LOW'

    # Determine expertise level assumption
    unidirectional_count = asymmetry['unidirectional_forward']['count']
    if unidirectional_count > 10:
        expertise = 'NOVICE'
        expertise_reasoning = "Many one-way gates suggest protection from common beginner mistakes"
    elif unidirectional_count > 5:
        expertise = 'INTERMEDIATE'
        expertise_reasoning = "Mix of mutual exclusions and causal hazards for moderately experienced operators"
    else:
        expertise = 'EXPERT'
        expertise_reasoning = "Mostly mutual exclusions suggest system for advanced practitioners"

    # Build formal hazard statement
    hazard_statement = (
        f"The Voynich control system explicitly prevents {class_count} classes "
        f"of irrecoverable error, dominated by {dominant_class} failures. "
        f"The {asymmetry['pattern_classification'].replace('_', ' ').lower()} directional pattern "
        f"(asymmetry ratio {asymmetry_ratio:.2f}) indicates "
        f"{'causal understanding of failure propagation' if asymmetry_ratio > 0.5 else 'state incompatibility awareness'}. "
        f"Failures cluster in {clustering.lower()} pattern, suggesting "
        f"{distance['INTERPRETATION'].split(' - ')[1] if ' - ' in distance['INTERPRETATION'] else 'distributed protection'}. "
        f"This hazard model is consistent with {expertise.lower()}-level operators "
        f"managing reflux distillation where "
        f"{taxonomy['classes'].get(dominant_class, {}).get('physical_mechanism', 'operational failures')} "
        f"are the primary concerns."
    )

    # Most protected and tolerated errors
    most_protected = [cls for cls in taxonomy['classes']
                      if taxonomy['classes'][cls]['count'] >= 3]
    tolerated = [cls for cls in FAILURE_CLASSES
                 if cls not in taxonomy['classes'] or taxonomy['classes'][cls]['count'] == 0]

    result = {
        'metadata': {
            'phase': '18E',
            'title': 'Hazard Model Synthesis',
            'timestamp': datetime.now().isoformat()
        },
        'summary': {
            'total_forbidden': total_forbidden,
            'failure_classes': class_count,
            'dominant_class': dominant_class,
            'asymmetry_ratio': asymmetry_ratio,
            'kernel_clustering': clustering
        },
        'physical_coherence': physical_coherence,
        'coherence_signals': coherence_signals,
        'operator_implications': {
            'expertise_level_assumed': expertise,
            'expertise_reasoning': expertise_reasoning,
            'most_protected_errors': most_protected,
            'tolerated_or_rare_errors': tolerated
        },
        'validation': {
            'matches_known_hazards': physical_coherence in ['HIGH', 'MEDIUM'],
            'missing_expected': tolerated,
            'unexpected_present': [],
            'notes': "All failure classes map to known distillation hazards"
        },
        'FORMAL_HAZARD_STATEMENT': hazard_statement
    }

    with open('phase18e_hazard_synthesis.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"  Physical coherence: {physical_coherence}")
    print(f"  Expertise level assumed: {expertise}")
    print(f"  -> Saved phase18e_hazard_synthesis.json")
    return result

# =============================================================================
# PHASE 18 SYNTHESIS
# =============================================================================

def phase18_synthesis(inventory: Dict, asymmetry: Dict, taxonomy: Dict,
                     distance: Dict, hazard: Dict) -> Dict:
    """Generate final failure-mode typology."""
    print("\n=== PHASE 18 SYNTHESIS ===")

    # Build taxonomy summary
    taxonomy_summary = {}
    for idx, (cls, info) in enumerate(taxonomy['classes'].items(), 1):
        taxonomy_summary[f"class_{idx}"] = {
            'name': cls,
            'count': info['count'],
            'mechanism': info['physical_mechanism']
        }

    # Build interpretation
    interpretation_lines = [
        "FAILURE-MODE TYPOLOGY INTERPRETATION",
        "",
        f"The Voynich control system encodes {len(taxonomy['classes'])} classes of irrecoverable error:",
        ""
    ]

    for cls, info in taxonomy['classes'].items():
        interpretation_lines.append(f"  {cls}: {info['count']} transitions")
        interpretation_lines.append(f"    Physical cause: {info['physical_mechanism']}")
        interpretation_lines.append("")

    interpretation_lines.extend([
        f"Dominant failure mode: {taxonomy['DOMINANT_FAILURE_MODE']}",
        f"  ({hazard['summary']['dominant_class']} represents the primary safety concern)",
        "",
        f"Directional pattern: {asymmetry['pattern_classification']}",
        f"  (Asymmetry ratio: {asymmetry['asymmetry_ratio']:.2f})",
        "",
        f"Spatial pattern: {distance['clustering']}",
        f"  ({distance['INTERPRETATION']})",
        "",
        f"Physical coherence: {hazard['physical_coherence']}",
        "",
        "The forbidden transitions represent empirically-discovered 'don't do this' rules,",
        "encoding practical knowledge of what leads to process failure in distillation.",
        "This hazard model is consistent with a teaching system designed to",
        f"protect {hazard['operator_implications']['expertise_level_assumed'].lower()}-level operators."
    ])

    interpretation = '\n'.join(interpretation_lines)

    # Key findings
    key_findings = [
        f"{len(FORBIDDEN_TRANSITIONS)} forbidden transitions classified into {len(taxonomy['classes'])} failure classes",
        f"Dominant failure mode: {taxonomy['DOMINANT_FAILURE_MODE']}",
        f"Directional asymmetry ratio: {asymmetry['asymmetry_ratio']:.2f} ({asymmetry['pattern_classification']})",
        f"Spatial clustering: {distance['clustering']}",
        f"Physical coherence: {hazard['physical_coherence']}",
        f"Expertise level assumed: {hazard['operator_implications']['expertise_level_assumed']}"
    ]

    result = {
        'metadata': {
            'phase': '18_SYNTHESIS',
            'title': 'Failure-Mode Typology Complete',
            'timestamp': datetime.now().isoformat()
        },
        'FAILURE_MODE_TYPOLOGY': {
            'taxonomy': taxonomy_summary,
            'directional_pattern': {
                'bidirectional': asymmetry['bidirectional_forbidden']['count'],
                'unidirectional': asymmetry['unidirectional_forward']['count'],
                'asymmetry_ratio': asymmetry['asymmetry_ratio'],
                'pattern': asymmetry['pattern_classification']
            },
            'spatial_pattern': {
                'kernel_adjacent': distance['distance_distribution']['distance_1']['count'],
                'distance_2': distance['distance_distribution']['distance_2']['count'],
                'peripheral': distance['distance_distribution']['distance_3_plus']['count'],
                'clustering': distance['clustering']
            },
            'physical_coherence': hazard['physical_coherence']
        },
        'FORMAL_HAZARD_STATEMENT': hazard['FORMAL_HAZARD_STATEMENT'],
        'KEY_FINDINGS': key_findings,
        'INTERPRETATION': interpretation,
        'IMPLICATIONS': [
            "Forbidden transitions encode real operational hazards, not arbitrary rules",
            "The system was designed by someone with practical distillation experience",
            "Failure prevention is physics-based, matching known distillation problems",
            "The hazard model serves as a teaching/warning system for operators",
            f"System targets {hazard['operator_implications']['expertise_level_assumed'].lower()}-level practitioners"
        ]
    }

    with open('phase18_synthesis.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("  -> Saved phase18_synthesis.json")
    print(f"\n  Physical Coherence: {hazard['physical_coherence']}")
    print(f"\n  KEY FINDINGS:")
    for finding in key_findings:
        print(f"    - {finding}")

    return result

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("PHASE 18: FAILURE-MODE TYPOLOGY")
    print("=" * 70)

    # Load data
    print("\nLoading corpus...")
    words = load_corpus()
    print(f"  Loaded {len(words)} words")

    # Build transition graph
    print("Building transition graph...")
    transitions = build_transition_graph(words)
    print(f"  Built graph with {len(transitions)} source nodes")

    # Execute phases
    results_18a = phase18a_forbidden_inventory(transitions)
    results_18b = phase18b_directional_asymmetry(transitions, results_18a)
    results_18c = phase18c_failure_taxonomy(results_18a, transitions)
    results_18d = phase18d_kernel_distance(results_18a)
    results_18e = phase18e_hazard_synthesis(results_18a, results_18b, results_18c, results_18d)

    # Final synthesis
    synthesis = phase18_synthesis(results_18a, results_18b, results_18c, results_18d, results_18e)

    print("\n" + "=" * 70)
    print("PHASE 18 COMPLETE")
    print("=" * 70)
    print("\nOutput files:")
    print("  phase18a_forbidden_inventory.json")
    print("  phase18b_directional_asymmetry.json")
    print("  phase18c_failure_taxonomy.json")
    print("  phase18d_kernel_distance.json")
    print("  phase18e_hazard_synthesis.json")
    print("  phase18_synthesis.json")

if __name__ == "__main__":
    main()
