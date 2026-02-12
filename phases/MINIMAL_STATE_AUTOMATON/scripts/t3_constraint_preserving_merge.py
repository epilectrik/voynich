#!/usr/bin/env python3
"""
T3: Constraint-Preserving State Merge
MINIMAL_STATE_AUTOMATON phase

Agglomerative merging of 49 classes by transition profile similarity.
At each merge, verify that key constraints are preserved.
Find the minimum state count that maintains all structural properties.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from scipy.spatial.distance import jensenshannon
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
FINGERPRINT_DIR = Path(__file__).parent.parent.parent / 'FINGERPRINT_UNIQUENESS' / 'results'


# ============================================================
# CONSTRAINT DEFINITIONS
# ============================================================

# Known depleted pairs from FINGERPRINT_UNIQUENESS T1
DEPLETED_PAIRS = [
    (11, 36), (13, 40), (9, 33), (24, 30), (14, 46), (9, 27),
    (9, 32), (5, 34), (47, 11), (19, 33), (7, 32), (11, 14),
    (3, 33), (33, 38), (18, 28), (7, 47), (13, 5), (10, 28),
]

# Role boundaries that must not be crossed
CC_CLASSES = {10, 11, 12}
FQ_CLASSES = {9, 13, 14, 23}
FL_CLASSES = {7, 30, 38, 40}
FL_HAZ = {7, 30}
FL_SAFE = {38, 40}
EN_CLASSES = {8} | set(range(31, 50)) - {38, 40}  # Adjusted for FL overlap

# Major role groups (no mixing allowed)
ROLE_GROUPS = {
    'CC': CC_CLASSES,
    'FQ': FQ_CLASSES,
    'FL_HAZ': FL_HAZ,
    'FL_SAFE': FL_SAFE,
}
# EN and AX can merge within themselves but not across major boundaries


def get_role(c, all_classes):
    """Get role for a class."""
    if c in CC_CLASSES: return 'CC'
    if c in FQ_CLASSES: return 'FQ'
    if c in FL_HAZ: return 'FL_HAZ'
    if c in FL_SAFE: return 'FL_SAFE'
    en_set = ({8} | set(range(31, 50))) - {7, 30, 38, 40}
    if c in en_set: return 'EN'
    return 'AX'


def check_role_integrity(partition, all_classes):
    """No merged state should mix protected role groups."""
    for group in partition:
        roles_in_group = set(get_role(c, all_classes) for c in group)
        # CC must not mix with non-CC
        if 'CC' in roles_in_group and len(roles_in_group) > 1:
            return False, "CC mixed with non-CC"
        # FQ must not mix with non-FQ
        if 'FQ' in roles_in_group and len(roles_in_group) > 1:
            return False, "FQ mixed with non-FQ"
        # FL_HAZ must not mix with FL_SAFE
        if 'FL_HAZ' in roles_in_group and 'FL_SAFE' in roles_in_group:
            return False, "FL_HAZ mixed with FL_SAFE"
        # FL must not mix with non-FL (except possibly AX)
        if ('FL_HAZ' in roles_in_group or 'FL_SAFE' in roles_in_group):
            non_fl = roles_in_group - {'FL_HAZ', 'FL_SAFE'}
            if non_fl:
                return False, f"FL mixed with {non_fl}"
    return True, "OK"


def check_depletion_asymmetry(partition, counts, all_classes):
    """Depleted pairs must remain distinguishable and asymmetric in merged space."""
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}

    # Build class-to-partition mapping
    cls_to_part = {}
    for pi, group in enumerate(partition):
        for c in group:
            cls_to_part[c] = pi

    # Check each depleted pair maps to a distinct merged pair
    merged_depleted = set()
    for src, tgt in DEPLETED_PAIRS:
        if src not in cls_to_part or tgt not in cls_to_part:
            continue
        ps, pt = cls_to_part[src], cls_to_part[tgt]
        if ps == pt:
            return False, f"Depleted pair ({src},{tgt}) merged into same state"
        merged_depleted.add((ps, pt))

    # Check asymmetry: for each merged depleted pair, reverse should not be depleted
    n_parts = len(partition)
    merged_counts = np.zeros((n_parts, n_parts), dtype=float)
    for i, gi in enumerate(partition):
        for j, gj in enumerate(partition):
            for ci in gi:
                for cj in gj:
                    merged_counts[i][j] += counts[cls_to_idx[ci]][cls_to_idx[cj]]

    row_sums = merged_counts.sum(axis=1)
    col_sums = merged_counts.sum(axis=0)
    total = merged_counts.sum()

    for ps, pt in merged_depleted:
        expected = row_sums[ps] * col_sums[pt] / total if total > 0 else 0
        if expected < 5:
            continue  # Not enough data to test
        ratio = merged_counts[ps][pt] / expected
        # Check reverse
        rev_expected = row_sums[pt] * col_sums[ps] / total if total > 0 else 0
        if rev_expected >= 5:
            rev_ratio = merged_counts[pt][ps] / rev_expected
            if rev_ratio < 0.2:  # Reverse is ALSO depleted = asymmetry broken
                return False, f"Merged pair ({ps},{pt}) lost asymmetry"

    return True, "OK"


def check_all_constraints(partition, counts, all_classes):
    """Run all constraint checks. Return (ok, messages)."""
    messages = []

    ok1, msg1 = check_role_integrity(partition, all_classes)
    if not ok1:
        messages.append(f"ROLE: {msg1}")

    ok2, msg2 = check_depletion_asymmetry(partition, counts, all_classes)
    if not ok2:
        messages.append(f"DEPLETION: {msg2}")

    return len(messages) == 0, messages


# ============================================================
# MERGING ALGORITHM
# ============================================================

def compute_jsd_matrix(probs, partition, all_classes):
    """Compute pairwise JSD between partition groups using their aggregate transition profiles."""
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    n_parts = len(partition)

    # Aggregate profiles
    profiles = []
    for group in partition:
        # Weighted average of transition profiles
        total_out = 0
        profile = np.zeros(len(all_classes))
        for c in group:
            idx = cls_to_idx[c]
            row_sum = probs[idx].sum()
            profile += probs[idx] * row_sum
            total_out += row_sum
        if total_out > 0:
            profile /= total_out
        else:
            profile = np.ones(len(all_classes)) / len(all_classes)
        profiles.append(profile)

    # Pairwise JSD
    jsd_matrix = np.full((n_parts, n_parts), np.inf)
    for i in range(n_parts):
        for j in range(i + 1, n_parts):
            jsd = jensenshannon(profiles[i], profiles[j])
            if np.isnan(jsd):
                jsd = 1.0
            jsd_matrix[i][j] = jsd
            jsd_matrix[j][i] = jsd

    return jsd_matrix


def run():
    t_start = time.time()
    print("=" * 70)
    print("T3: Constraint-Preserving State Merge")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load
    print("\n[1/3] Loading transition data...")
    with open(RESULTS_DIR / 't1_transition_data.json') as f:
        t1 = json.load(f)

    all_classes = t1['classes']
    counts = np.array(t1['counts_49x49'], dtype=float)
    probs = np.array(t1['probs_49x49'])
    n = len(all_classes)
    print(f"  {n} classes")

    # Initialize: each class in its own partition
    partition = [frozenset([c]) for c in all_classes]

    # Merge history
    merge_log = []
    current_states = n

    print(f"\n[2/3] Agglomerative merging...")
    print(f"  Starting with {current_states} states")

    # Check initial constraints
    partition_sets = [set(p) for p in partition]
    ok, msgs = check_all_constraints(partition_sets, counts, all_classes)
    print(f"  Initial constraint check: {'OK' if ok else 'FAILED'}")

    consecutive_rejects = 0
    max_rejects = 200  # Stop if we can't merge anything

    while current_states > 2 and consecutive_rejects < max_rejects:
        # Compute JSD matrix for current partition
        jsd = compute_jsd_matrix(probs, partition_sets, all_classes)

        # Find closest pair
        n_p = len(partition_sets)
        candidates = []
        for i in range(n_p):
            for j in range(i + 1, n_p):
                candidates.append((jsd[i][j], i, j))
        candidates.sort()

        merged = False
        for dist, i, j in candidates:
            # Propose merge
            new_group = partition_sets[i] | partition_sets[j]
            new_partition = [p for k, p in enumerate(partition_sets) if k != i and k != j]
            new_partition.append(new_group)

            # Check constraints
            ok, msgs = check_all_constraints(new_partition, counts, all_classes)
            if ok:
                merge_log.append({
                    'step': len(merge_log) + 1,
                    'merged': [sorted(partition_sets[i]), sorted(partition_sets[j])],
                    'result_group': sorted(new_group),
                    'jsd': round(float(dist), 6),
                    'states_after': len(new_partition),
                })
                partition_sets = new_partition
                current_states = len(partition_sets)
                consecutive_rejects = 0
                merged = True

                if current_states <= 20 or len(merge_log) % 5 == 0:
                    print(f"    Step {len(merge_log):>3}: {current_states:>2} states "
                          f"(merged JSD={dist:.4f}, "
                          f"group size={len(new_group)})")
                break
            else:
                consecutive_rejects += 1

        if not merged:
            break

    # Final state
    print(f"\n  Final: {current_states} states ({n - current_states} merges)")
    print(f"  Stopped: {'max rejects' if consecutive_rejects >= max_rejects else 'no valid merges'}")

    # Describe final partition
    print(f"\n[3/3] Final automaton states...")
    state_descriptions = []
    for si, group in enumerate(partition_sets):
        roles = set(get_role(c, all_classes) for c in group)
        freq = sum(t1['class_details'][str(c)]['frequency'] for c in group)
        desc = {
            'state_id': si,
            'classes': sorted(group),
            'n_classes': len(group),
            'roles': sorted(roles),
            'total_frequency': freq,
            'frequency_fraction': round(freq / t1['n_tokens'], 4),
        }
        state_descriptions.append(desc)
        if len(group) <= 5:
            cls_str = ", ".join(str(c) for c in sorted(group))
        else:
            cls_str = f"{len(group)} classes"
        print(f"  S{si:>2}: [{cls_str}] "
              f"roles={'/'.join(sorted(roles))} freq={freq} ({desc['frequency_fraction']:.1%})")

    # Compare to role structure
    role_groups_actual = {}
    for si, group in enumerate(partition_sets):
        roles = frozenset(get_role(c, all_classes) for c in group)
        role_key = '/'.join(sorted(roles))
        if role_key not in role_groups_actual:
            role_groups_actual[role_key] = 0
        role_groups_actual[role_key] += 1

    print(f"\n  Role composition of merged states:")
    for role_key, count in sorted(role_groups_actual.items()):
        print(f"    {role_key}: {count} states")

    # Identify binding constraints (which prevented further merging)
    print(f"\n  Testing which constraints bind at current partition...")
    binding_constraints = []
    n_p = len(partition_sets)
    for i in range(n_p):
        for j in range(i + 1, n_p):
            new_group = partition_sets[i] | partition_sets[j]
            new_partition = [p for k, p in enumerate(partition_sets) if k != i and k != j]
            new_partition.append(new_group)
            ok, msgs = check_all_constraints(new_partition, counts, all_classes)
            if not ok:
                for msg in msgs:
                    binding_constraints.append({
                        'states': [sorted(partition_sets[i])[:3], sorted(partition_sets[j])[:3]],
                        'constraint': msg,
                    })

    binding_types = {}
    for bc in binding_constraints:
        ctype = bc['constraint'].split(':')[0]
        binding_types[ctype] = binding_types.get(ctype, 0) + 1

    print(f"  Binding constraint breakdown:")
    for ctype, count in sorted(binding_types.items(), key=lambda x: -x[1]):
        print(f"    {ctype}: {count} blocked merges")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Starting states: {n}")
    print(f"  Final states: {current_states}")
    print(f"  Compression ratio: {n/current_states:.1f}x")
    print(f"  Total valid merges: {len(merge_log)}")

    if current_states <= 8:
        verdict = "COMPRESSIBLE"
    elif current_states <= 15:
        verdict = "MODERATELY_COMPLEX"
    else:
        verdict = "INCOMPRESSIBLE"
    print(f"  Verdict: {verdict}")

    # Save
    results = {
        'test': 'T3_constraint_preserving_merge',
        'n_classes': n,
        'n_final_states': current_states,
        'compression_ratio': round(n / current_states, 2),
        'n_merges': len(merge_log),
        'merge_log': merge_log,
        'final_partition': [sorted(list(g)) for g in partition_sets],
        'state_descriptions': state_descriptions,
        'binding_constraints': binding_constraints[:50],  # Cap for size
        'binding_type_counts': binding_types,
        'verdict': verdict,
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    with open(RESULTS_DIR / 't3_merged_automaton.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't3_merged_automaton.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
