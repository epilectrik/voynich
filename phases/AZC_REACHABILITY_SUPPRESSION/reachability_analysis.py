"""
AZC->B Instruction-Class Reachability Suppression Analysis

Goal: Demonstrate that AZC legality fields systematically shrink the
reachable subset of the 49 B instruction classes.

Closure statement target:
"AZC does not modify B's grammar; it shortens the reachable language
by forbidding certain class transitions at certain positions once
particular constraint bundles are active."
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Set, List, Tuple, Optional

BASE = Path(r"C:\git\voynich")

# ============================================================================
# STEP 1: Load the 17 forbidden transitions (token-level)
# ============================================================================

FORBIDDEN_TRANSITIONS = [
    # PHASE_ORDERING (7 transitions - 41%)
    ('shey', 'aiin', 'PHASE_ORDERING', 0.9),
    ('shey', 'al', 'PHASE_ORDERING', 0.8),
    ('shey', 'c', 'PHASE_ORDERING', 0.7),
    ('chol', 'r', 'PHASE_ORDERING', 0.8),
    ('chedy', 'ee', 'PHASE_ORDERING', 0.7),
    ('chey', 'chedy', 'PHASE_ORDERING', 0.6),
    ('l', 'chol', 'PHASE_ORDERING', 0.7),

    # COMPOSITION_JUMP (4 transitions - 24%)
    ('dy', 'aiin', 'COMPOSITION_JUMP', 0.8),
    ('dy', 'chey', 'COMPOSITION_JUMP', 0.7),
    ('or', 'dal', 'COMPOSITION_JUMP', 0.8),
    ('ar', 'chol', 'COMPOSITION_JUMP', 0.7),

    # CONTAINMENT_TIMING (4 transitions - 24%)
    ('qo', 'shey', 'CONTAINMENT_TIMING', 0.9),
    ('qo', 'shy', 'CONTAINMENT_TIMING', 0.8),
    ('ok', 'shol', 'CONTAINMENT_TIMING', 0.7),
    ('ol', 'shor', 'CONTAINMENT_TIMING', 0.7),

    # RATE_MISMATCH (1 transition - 6%)
    ('dar', 'qokaiin', 'RATE_MISMATCH', 0.6),

    # ENERGY_OVERSHOOT (1 transition - 6%)
    ('qokaiin', 'qokedy', 'ENERGY_OVERSHOOT', 0.9),
]

# ============================================================================
# STEP 2: Load 49 instruction classes and build token -> class mapping
# ============================================================================

def load_instruction_classes() -> Tuple[Dict[str, int], Dict[int, dict]]:
    """
    Load Phase 20A instruction classes.
    Returns: (token_to_class mapping, class_info dict)
    """
    eq_path = BASE / "phase20a_operator_equivalence.json"
    with open(eq_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_class = {}
    class_info = {}

    for cls in data['classes']:
        class_id = cls['class_id']
        class_info[class_id] = {
            'id': class_id,
            'members': cls['members'],
            'member_count': cls['member_count'],
            'functional_role': cls['functional_role'],
            'representative': cls['representative'],
            'total_frequency': cls['total_frequency'],
        }
        for token in cls['members']:
            token_to_class[token] = class_id

    return token_to_class, class_info

# ============================================================================
# STEP 3: Map token-level forbidden transitions to class-level
# ============================================================================

def map_to_class_transitions(
    token_transitions: List[Tuple],
    token_to_class: Dict[str, int]
) -> Dict[Tuple[int, int], List[dict]]:
    """
    Map token-level forbidden transitions to class-level.

    Returns dict of {(from_class, to_class): [transition_info, ...]}
    Multiple token transitions may map to the same class pair.
    """
    class_transitions = defaultdict(list)
    unmapped = []

    for from_token, to_token, hazard_class, severity in token_transitions:
        from_class = token_to_class.get(from_token)
        to_class = token_to_class.get(to_token)

        if from_class is None or to_class is None:
            unmapped.append((from_token, to_token, from_class, to_class))
            continue

        class_transitions[(from_class, to_class)].append({
            'from_token': from_token,
            'to_token': to_token,
            'hazard_class': hazard_class,
            'severity': severity,
        })

    return class_transitions, unmapped

# ============================================================================
# STEP 4: Build base reachability graph G0
# ============================================================================

def build_base_reachability_graph(
    num_classes: int,
    forbidden_class_pairs: Set[Tuple[int, int]]
) -> Dict[int, Set[int]]:
    """
    Build the base reachability graph G0.

    Nodes: 49 instruction classes
    Edges: All class->class transitions EXCEPT forbidden pairs

    Note: Bidirectional - if (A, B) is forbidden, so is (B, A)
    """
    graph = {i: set() for i in range(1, num_classes + 1)}

    for from_class in range(1, num_classes + 1):
        for to_class in range(1, num_classes + 1):
            if from_class == to_class:
                continue
            # Check both directions for bidirectional forbidden pairs
            if (from_class, to_class) not in forbidden_class_pairs and \
               (to_class, from_class) not in forbidden_class_pairs:
                graph[from_class].add(to_class)

    return graph

def compute_transitive_closure(graph: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
    """
    Compute transitive closure: what can reach what?
    Uses Floyd-Warshall style iteration.
    """
    # Start with direct edges
    reachable = {k: set(v) for k, v in graph.items()}

    # Add self-loops (can reach yourself)
    for node in reachable:
        reachable[node].add(node)

    # Iterate until convergence
    changed = True
    while changed:
        changed = False
        for node in reachable:
            # For each node I can reach, I can also reach what they can reach
            new_reachable = set()
            for intermediate in list(reachable[node]):
                for target in reachable.get(intermediate, set()):
                    if target not in reachable[node]:
                        new_reachable.add(target)
            if new_reachable:
                reachable[node].update(new_reachable)
                changed = True

    return reachable

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 70)
    print("AZC->B INSTRUCTION-CLASS REACHABILITY ANALYSIS")
    print("=" * 70)

    # Load instruction classes
    token_to_class, class_info = load_instruction_classes()
    print(f"\nLoaded {len(class_info)} instruction classes")
    print(f"Loaded {len(token_to_class)} token->class mappings")

    # Map forbidden transitions to class level
    class_transitions, unmapped = map_to_class_transitions(
        FORBIDDEN_TRANSITIONS, token_to_class
    )

    print(f"\n" + "-" * 70)
    print("TOKEN-LEVEL TO CLASS-LEVEL MAPPING")
    print("-" * 70)

    print(f"\n17 forbidden token transitions -> {len(class_transitions)} class pairs")

    if unmapped:
        print(f"\nWARNING: {len(unmapped)} transitions could not be mapped:")
        for from_t, to_t, from_c, to_c in unmapped:
            print(f"  {from_t} (class={from_c}) -> {to_t} (class={to_c})")

    print("\nClass-level forbidden transitions:")
    for (from_class, to_class), transitions in sorted(class_transitions.items()):
        from_role = class_info[from_class]['functional_role']
        to_role = class_info[to_class]['functional_role']
        from_rep = class_info[from_class]['representative']
        to_rep = class_info[to_class]['representative']

        hazard_classes = set(t['hazard_class'] for t in transitions)

        print(f"\n  Class {from_class} ({from_role}, rep={from_rep})")
        print(f"    -> Class {to_class} ({to_role}, rep={to_rep})")
        print(f"    Hazard types: {hazard_classes}")
        print(f"    Token pairs:")
        for t in transitions:
            print(f"      {t['from_token']} -> {t['to_token']} ({t['hazard_class']})")

    # Build base reachability graph
    forbidden_pairs = set(class_transitions.keys())
    graph = build_base_reachability_graph(49, forbidden_pairs)

    print(f"\n" + "-" * 70)
    print("BASE REACHABILITY GRAPH G0")
    print("-" * 70)

    total_edges = sum(len(targets) for targets in graph.values())
    max_edges = 49 * 48  # Full graph without self-loops

    print(f"\nNodes: 49 instruction classes")
    print(f"Edges: {total_edges} (of {max_edges} possible)")
    print(f"Forbidden pairs: {len(forbidden_pairs) * 2} (bidirectional)")
    print(f"Edge density: {total_edges / max_edges * 100:.1f}%")

    # Compute transitive closure
    reachable = compute_transitive_closure(graph)

    print(f"\n" + "-" * 70)
    print("REACHABILITY ANALYSIS")
    print("-" * 70)

    # Find classes with reduced reachability
    full_reachability = 49  # Can reach all classes including self

    print("\nClasses with reduced reachability:")
    reduced = []
    for class_id in sorted(reachable.keys()):
        reach_count = len(reachable[class_id])
        if reach_count < full_reachability:
            role = class_info[class_id]['functional_role']
            rep = class_info[class_id]['representative']
            blocked = full_reachability - reach_count
            reduced.append((class_id, reach_count, blocked, role, rep))

    for class_id, reach, blocked, role, rep in sorted(reduced, key=lambda x: -x[2]):
        print(f"  Class {class_id:2d} ({role:15s}, {rep:12s}): can reach {reach}/49, blocked={blocked}")

    # Identify which classes are affected by forbidden transitions
    print(f"\n" + "-" * 70)
    print("CLASSES INVOLVED IN FORBIDDEN TRANSITIONS")
    print("-" * 70)

    involved_classes = set()
    for (from_class, to_class) in forbidden_pairs:
        involved_classes.add(from_class)
        involved_classes.add(to_class)

    print(f"\n{len(involved_classes)} classes involved in forbidden transitions:")
    for class_id in sorted(involved_classes):
        info = class_info[class_id]
        # Count forbidden outgoing and incoming
        outgoing = sum(1 for (f, t) in forbidden_pairs if f == class_id)
        incoming = sum(1 for (f, t) in forbidden_pairs if t == class_id)
        print(f"  Class {class_id:2d} ({info['functional_role']:15s}, {info['representative']:12s}): "
              f"forbidden_out={outgoing}, forbidden_in={incoming}")

    # Save results
    results = {
        'phase': 'AZC_REACHABILITY_SUPPRESSION',
        'date': '2026-01-17',
        'status': 'PHASE_1_COMPLETE',

        'token_level_forbidden': len(FORBIDDEN_TRANSITIONS),
        'class_level_forbidden_pairs': len(class_transitions),

        'class_transitions': {
            f"{f}_{t}": {
                'from_class': f,
                'to_class': t,
                'token_transitions': trans
            }
            for (f, t), trans in class_transitions.items()
        },

        'unmapped_transitions': unmapped,

        'graph_stats': {
            'nodes': 49,
            'edges': total_edges,
            'max_edges': max_edges,
            'edge_density': total_edges / max_edges,
            'forbidden_pairs': len(forbidden_pairs) * 2,
        },

        'involved_classes': list(involved_classes),
        'reduced_reachability_classes': [
            {'class_id': c, 'reachable': r, 'blocked': b, 'role': role, 'representative': rep}
            for c, r, b, role, rep in reduced
        ],
    }

    output_path = BASE / "phases" / "AZC_REACHABILITY_SUPPRESSION" / "phase1_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_path}")

    return results

# ============================================================================
# STEP 5: Token Morphology Decomposition
# ============================================================================

# Marker families (C240) - prefixes
MARKER_FAMILIES = {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}

# Extended prefixes (C349)
EXTENDED_PREFIX_MAP = {
    'kch': 'ch', 'pch': 'ch', 'tch': 'ch', 'sch': 'sh',
    'dch': 'ch', 'rch': 'ch', 'fch': 'ch', 'lch': 'ch',
}

# Universal suffixes (C269)
KNOWN_SUFFIXES = {
    'ol', 'or', 'y', 'aiin', 'ar', 'chy', 'eeol',
    'ain', 'hy', 'al', 'am', 'an', 'ey', 'dy', 'in',
    'eey', 'edy', 'eedy', 'edy', 'ey', 'r', 'l',
}

def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Decompose a token into (PREFIX, MIDDLE, SUFFIX).
    Returns (None, None, None) if token doesn't follow morphological pattern.
    """
    token_lower = token.lower()

    # Detect prefix
    detected_prefix = None

    # Check extended prefixes first (3-char)
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            detected_prefix = prefix3

    # Check standard 2-char prefixes
    if detected_prefix is None and len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            detected_prefix = prefix2

    if detected_prefix is None:
        # Token doesn't have a recognized prefix
        return (None, None, None)

    remainder = token_lower[len(detected_prefix):]

    if not remainder:
        # Prefix-only token
        return (detected_prefix, '', None)

    # Find suffix (longest match from end)
    detected_suffix = None
    for suffix_len in range(min(4, len(remainder)), 0, -1):
        candidate = remainder[-suffix_len:]
        if candidate in KNOWN_SUFFIXES:
            detected_suffix = candidate
            break

    if detected_suffix is None:
        # No recognized suffix
        return (detected_prefix, remainder, None)

    # Extract middle
    middle_end = len(remainder) - len(detected_suffix)
    detected_middle = remainder[:middle_end] if middle_end > 0 else ''

    return (detected_prefix, detected_middle, detected_suffix)


def build_middle_class_index(class_info: Dict[int, dict]) -> Tuple[Dict[str, Set[int]], Dict[int, dict]]:
    """
    For each instruction class, decompose member tokens and collect MIDDLEs.
    Returns: (middle_to_classes mapping, class_morphology_stats)
    """
    middle_to_classes = defaultdict(set)
    class_morphology = {}

    for class_id, info in class_info.items():
        decompositions = []
        middles_found = set()
        prefixes_found = set()

        for token in info['members']:
            prefix, middle, suffix = decompose_token(token)
            decompositions.append({
                'token': token,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
            })

            if middle is not None:
                middles_found.add(middle)
                middle_to_classes[middle].add(class_id)
            if prefix is not None:
                prefixes_found.add(prefix)

        class_morphology[class_id] = {
            'class_id': class_id,
            'member_count': len(info['members']),
            'decomposed_count': sum(1 for d in decompositions if d['prefix'] is not None),
            'middles': list(middles_found),
            'prefixes': list(prefixes_found),
            'decompositions': decompositions,
        }

    return dict(middle_to_classes), class_morphology


def analyze_middle_class_distribution():
    """Analyze how MIDDLEs distribute across instruction classes."""
    print("\n" + "=" * 70)
    print("MIDDLE -> INSTRUCTION CLASS ANALYSIS")
    print("=" * 70)

    # Load classes
    token_to_class, class_info = load_instruction_classes()

    # Build MIDDLE -> class index
    middle_to_classes, class_morphology = build_middle_class_index(class_info)

    print(f"\nTotal unique MIDDLEs found: {len(middle_to_classes)}")

    # Analyze MIDDLE sharing across classes
    exclusive_middles = []  # Appear in only 1 class
    shared_middles = []     # Appear in 2+ classes

    for middle, classes in middle_to_classes.items():
        if len(classes) == 1:
            exclusive_middles.append((middle, classes))
        else:
            shared_middles.append((middle, classes))

    print(f"Exclusive MIDDLEs (1 class): {len(exclusive_middles)}")
    print(f"Shared MIDDLEs (2+ classes): {len(shared_middles)}")

    # Show which classes have the most exclusive MIDDLEs
    print("\n" + "-" * 70)
    print("CLASSES BY EXCLUSIVE MIDDLE COUNT")
    print("-" * 70)

    class_exclusive_count = Counter()
    for middle, classes in exclusive_middles:
        for c in classes:
            class_exclusive_count[c] += 1

    for class_id, count in class_exclusive_count.most_common(15):
        info = class_info[class_id]
        morph = class_morphology[class_id]
        print(f"  Class {class_id:2d} ({info['functional_role']:15s}): "
              f"{count} exclusive MIDDLEs, {morph['decomposed_count']}/{morph['member_count']} decomposed")

    # Show which classes have the most shared MIDDLEs
    print("\n" + "-" * 70)
    print("CLASSES BY SHARED MIDDLE PARTICIPATION")
    print("-" * 70)

    class_shared_count = Counter()
    for middle, classes in shared_middles:
        for c in classes:
            class_shared_count[c] += 1

    for class_id, count in class_shared_count.most_common(15):
        info = class_info[class_id]
        print(f"  Class {class_id:2d} ({info['functional_role']:15s}): {count} shared MIDDLEs")

    # CRITICAL: Check hazard-involved classes
    print("\n" + "-" * 70)
    print("HAZARD-INVOLVED CLASSES: MIDDLE PROFILE")
    print("-" * 70)

    hazard_classes = {7, 8, 9, 11, 23, 30, 31, 33, 41}

    for class_id in sorted(hazard_classes):
        info = class_info[class_id]
        morph = class_morphology[class_id]

        exclusive = class_exclusive_count.get(class_id, 0)
        shared = class_shared_count.get(class_id, 0)

        print(f"\n  Class {class_id} ({info['functional_role']}, rep={info['representative']}):")
        print(f"    Members: {morph['member_count']}, Decomposed: {morph['decomposed_count']}")
        print(f"    MIDDLEs: {len(morph['middles'])} total ({exclusive} exclusive, {shared} shared)")
        print(f"    Prefixes: {morph['prefixes']}")

        # Show actual middles
        if morph['middles']:
            print(f"    MIDDLE values: {morph['middles'][:10]}{'...' if len(morph['middles']) > 10 else ''}")

    # Save results
    results = {
        'total_middles': len(middle_to_classes),
        'exclusive_middles': len(exclusive_middles),
        'shared_middles': len(shared_middles),
        'middle_to_classes': {m: list(c) for m, c in middle_to_classes.items()},
        'class_morphology': {str(k): {
            'class_id': v['class_id'],
            'member_count': v['member_count'],
            'decomposed_count': v['decomposed_count'],
            'middles': v['middles'],
            'prefixes': v['prefixes'],
        } for k, v in class_morphology.items()},
        'hazard_class_profiles': {
            str(c): {
                'exclusive_middles': class_exclusive_count.get(c, 0),
                'shared_middles': class_shared_count.get(c, 0),
            } for c in hazard_classes
        }
    }

    output_path = BASE / "phases" / "AZC_REACHABILITY_SUPPRESSION" / "middle_class_index.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_path}")

    return results


if __name__ == '__main__':
    # Run both analyses
    main()
    print("\n\n" + "=" * 70)
    analyze_middle_class_distribution()
