#!/usr/bin/env python3
"""
ts_03_judgment_trajectories.py - Final Pressure Test: Judgment Elimination Order

Tests the expert's hypothesis: Which human judgments disappear FIRST vs LAST
as execution proceeds through zones (C->P->R->S)?

This gives us a partial order over the 13 judgments - a "judgment elimination
trajectory" that describes how human agency is progressively withdrawn.

Key insight: The manuscript is a "machine for removing human freedom at exactly
the moments where freedom would be dangerous."
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Zone progression order (execution sequence)
ZONE_ORDER = ['C', 'P', 'R', 'S']

# The 13 judgment types with their zone availability
# (2=REQUIRED, 1=PERMITTED, 0=IMPOSSIBLE)
JUDGMENT_MATRIX = {
    # Watch Closely (6)
    'TEMPERATURE': {'C': 1, 'P': 1, 'R': 2, 'S': 0},
    'PHASE_TRANSITION': {'C': 1, 'P': 2, 'R': 2, 'S': 0},
    'QUALITY_PURITY': {'C': 1, 'P': 2, 'R': 1, 'S': 2},
    'TIMING': {'C': 1, 'P': 2, 'R': 1, 'S': 2},
    'MATERIAL_STATE': {'C': 2, 'P': 2, 'R': 1, 'S': 0},
    'STABILITY': {'C': 1, 'P': 2, 'R': 2, 'S': 0},

    # Forbidden Intervention (3)
    'EQUILIBRIUM_WAIT': {'C': 0, 'P': 0, 'R': 2, 'S': 2},
    'CYCLE_COMPLETION': {'C': 0, 'P': 0, 'R': 2, 'S': 2},
    'PURIFICATION_PATIENCE': {'C': 0, 'P': 0, 'R': 2, 'S': 2},

    # Recovery Decision (4)
    'ABORT_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'CORRECTION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'CONTINUATION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
    'COLLECTION_DECISION': {'C': 1, 'P': 2, 'R': 1, 'S': 0},
}

# Judgment categories
JUDGMENT_CATEGORIES = {
    'WATCH_CLOSELY': ['TEMPERATURE', 'PHASE_TRANSITION', 'QUALITY_PURITY',
                      'TIMING', 'MATERIAL_STATE', 'STABILITY'],
    'FORBIDDEN_INTERVENTION': ['EQUILIBRIUM_WAIT', 'CYCLE_COMPLETION',
                               'PURIFICATION_PATIENCE'],
    'RECOVERY_DECISION': ['ABORT_DECISION', 'CORRECTION_DECISION',
                          'CONTINUATION_DECISION', 'COLLECTION_DECISION'],
}


def compute_elimination_point(judgment_name):
    """
    Compute when a judgment becomes IMPOSSIBLE (eliminated).
    Returns zone index (0=C, 1=P, 2=R, 3=S) or 4 if never eliminated.
    """
    row = JUDGMENT_MATRIX[judgment_name]
    for i, zone in enumerate(ZONE_ORDER):
        if row[zone] == 0:  # IMPOSSIBLE
            return i
    return 4  # Never eliminated


def compute_requirement_peak(judgment_name):
    """
    Compute when a judgment is most REQUIRED.
    Returns zone index where value is highest (2=REQUIRED).
    """
    row = JUDGMENT_MATRIX[judgment_name]
    max_val = -1
    peak_zone = 0
    for i, zone in enumerate(ZONE_ORDER):
        if row[zone] > max_val:
            max_val = row[zone]
            peak_zone = i
    return peak_zone


def compute_availability_trajectory(judgment_name):
    """
    Compute the availability trajectory as a vector [C, P, R, S].
    """
    row = JUDGMENT_MATRIX[judgment_name]
    return [row[zone] for zone in ZONE_ORDER]


def classify_trajectory_shape(trajectory):
    """
    Classify the shape of a judgment trajectory.
    Returns: 'EARLY_PEAK', 'MID_PEAK', 'LATE_PEAK', 'FLAT', 'DECLINING', 'RISING'
    """
    if trajectory == [0, 0, 2, 2]:  # Forbidden interventions
        return 'LATE_ONSET'
    if trajectory[3] == 0 and max(trajectory[:3]) > 0:  # Eliminated at S
        if trajectory[0] == max(trajectory):
            return 'EARLY_PEAK_ELIMINATED'
        elif trajectory[1] == max(trajectory):
            return 'MID_PEAK_ELIMINATED'
        else:
            return 'LATE_PEAK_ELIMINATED'
    if trajectory[3] == 2:  # Required at S
        return 'TERMINAL_REQUIRED'
    return 'OTHER'


def build_elimination_order():
    """
    Build the partial order of judgment elimination.
    Returns judgments sorted by elimination point (early -> late).
    """
    eliminations = []
    for name in JUDGMENT_MATRIX:
        elim_point = compute_elimination_point(name)
        req_peak = compute_requirement_peak(name)
        trajectory = compute_availability_trajectory(name)
        shape = classify_trajectory_shape(trajectory)

        eliminations.append({
            'judgment': name,
            'category': next(cat for cat, members in JUDGMENT_CATEGORIES.items()
                           if name in members),
            'elimination_zone': ZONE_ORDER[elim_point] if elim_point < 4 else 'NEVER',
            'elimination_index': elim_point,
            'requirement_peak': ZONE_ORDER[req_peak],
            'trajectory': trajectory,
            'shape': shape,
        })

    # Sort by elimination point (early first), then by requirement peak
    eliminations.sort(key=lambda x: (x['elimination_index'], x['requirement_peak']))

    return eliminations


def analyze_category_patterns():
    """
    Analyze whether judgment categories have systematic elimination patterns.
    """
    category_patterns = {}

    for category, members in JUDGMENT_CATEGORIES.items():
        elim_points = [compute_elimination_point(m) for m in members]
        req_peaks = [compute_requirement_peak(m) for m in members]

        category_patterns[category] = {
            'members': members,
            'mean_elimination': float(np.mean(elim_points)),
            'elimination_variance': float(np.var(elim_points)),
            'mean_requirement_peak': float(np.mean(req_peaks)),
            'unified_pattern': len(set(elim_points)) == 1,  # All same elimination point
        }

    return category_patterns


def compute_agency_withdrawal_curve():
    """
    Compute the "agency withdrawal curve" - how many judgments remain
    available at each zone.
    """
    curve = {}
    for zone in ZONE_ORDER:
        available = sum(1 for row in JUDGMENT_MATRIX.values() if row[zone] > 0)
        required = sum(1 for row in JUDGMENT_MATRIX.values() if row[zone] == 2)
        impossible = sum(1 for row in JUDGMENT_MATRIX.values() if row[zone] == 0)

        curve[zone] = {
            'available': available,
            'required': required,
            'impossible': impossible,
            'freedom_index': available / 13,  # Fraction of judgments still possible
        }

    return curve


def main():
    print("=" * 70)
    print("TRAJECTORY_SEMANTICS: Judgment Elimination Trajectories")
    print("=" * 70)
    print()
    print("Testing: Which human judgments disappear FIRST vs LAST?")
    print("Hypothesis: The manuscript progressively removes human agency.")
    print()

    # Build elimination order
    print("-" * 70)
    print("JUDGMENT ELIMINATION ORDER (Early -> Late)")
    print("-" * 70)

    elimination_order = build_elimination_order()

    print(f"\n{'Judgment':<25} {'Category':<22} {'Eliminated':<10} {'Peak':<6} {'Shape'}")
    print("-" * 70)

    for item in elimination_order:
        print(f"{item['judgment']:<25} {item['category']:<22} "
              f"{item['elimination_zone']:<10} {item['requirement_peak']:<6} {item['shape']}")

    # Category patterns
    print("\n" + "-" * 70)
    print("CATEGORY-LEVEL PATTERNS")
    print("-" * 70)

    category_patterns = analyze_category_patterns()

    for category, pattern in category_patterns.items():
        print(f"\n{category}:")
        print(f"  Mean elimination zone: {pattern['mean_elimination']:.2f} "
              f"({'early' if pattern['mean_elimination'] < 2 else 'late'})")
        print(f"  Mean requirement peak: {pattern['mean_requirement_peak']:.2f}")
        print(f"  Unified pattern: {pattern['unified_pattern']}")

    # Agency withdrawal curve
    print("\n" + "-" * 70)
    print("AGENCY WITHDRAWAL CURVE")
    print("-" * 70)

    curve = compute_agency_withdrawal_curve()

    print(f"\n{'Zone':<6} {'Available':<12} {'Required':<12} {'Impossible':<12} {'Freedom'}")
    print("-" * 70)

    for zone in ZONE_ORDER:
        c = curve[zone]
        print(f"{zone:<6} {c['available']:<12} {c['required']:<12} "
              f"{c['impossible']:<12} {c['freedom_index']:.1%}")

    # Key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    # 1. Forbidden interventions are LATE ONSET
    fi_pattern = category_patterns['FORBIDDEN_INTERVENTION']
    print(f"\n1. FORBIDDEN INTERVENTIONS are late-onset (appear at zone {fi_pattern['mean_elimination']:.0f})")
    print("   -> 'Do not intervene' rules only apply once the process is running")

    # 2. Watch closely judgments peak at P, eliminated at S
    wc_early = [e for e in elimination_order
                if e['category'] == 'WATCH_CLOSELY' and e['elimination_zone'] == 'S']
    print(f"\n2. WATCH CLOSELY judgments: {len(wc_early)}/6 eliminated at S-zone")
    print("   -> Sensory monitoring becomes impossible when outcome is locked")

    # 3. Recovery decisions eliminated at S
    rd_pattern = [e for e in elimination_order
                  if e['category'] == 'RECOVERY_DECISION']
    print(f"\n3. RECOVERY DECISIONS: All eliminated at S-zone")
    print("   -> You can no longer choose to abort/correct once locked")

    # 4. Freedom collapse
    c_freedom = curve['C']['freedom_index']
    s_freedom = curve['S']['freedom_index']
    print(f"\n4. FREEDOM COLLAPSE: C-zone {c_freedom:.0%} -> S-zone {s_freedom:.0%}")
    print(f"   -> {(c_freedom - s_freedom):.0%} of human agency is withdrawn by S-zone")

    # Compile results
    results = {
        'phase': 'TRAJECTORY_SEMANTICS',
        'test': 'judgment_elimination_trajectories',
        'elimination_order': elimination_order,
        'category_patterns': category_patterns,
        'agency_withdrawal_curve': curve,
        'key_metrics': {
            'c_zone_freedom': curve['C']['freedom_index'],
            's_zone_freedom': curve['S']['freedom_index'],
            'freedom_collapse': curve['C']['freedom_index'] - curve['S']['freedom_index'],
            'forbidden_intervention_onset': fi_pattern['mean_elimination'],
            'watch_closely_eliminated_at_s': len(wc_early),
        },
        'interpretation': {
            'headline': 'The manuscript progressively removes human judgment freedoms phase by phase',
            'mechanism': 'Agency withdrawal curve: C(77%) -> P(77%) -> R(100%) -> S(38%)',
            'key_insight': 'S-zone eliminates 8/13 judgments - the outcome is locked, '
                          'human intervention is no longer possible',
        },
    }

    # The decisive finding
    print("\n" + "=" * 70)
    print("DECISIVE FINDING")
    print("=" * 70)
    print()
    print("The manuscript is a JUDGMENT-GATING SYSTEM.")
    print()
    print("It explicitly engineers when certain kinds of human cognitive")
    print("faculties can no longer be applied:")
    print()
    print("  * C-zone: Flexible setup (10/13 judgments available)")
    print("  * P-zone: Observation required (9/13 judgments REQUIRED)")
    print("  * R-zone: All judgments possible but narrowing")
    print("  * S-zone: 8/13 judgments IMPOSSIBLE (outcome locked)")
    print()
    print("This is META-SEMANTICS OF CONTROL:")
    print()
    print('  "This manuscript is a machine for removing human freedom')
    print('   at exactly the moments where freedom would be dangerous."')

    # Save results
    output_path = RESULTS_DIR / "ts_judgment_trajectories.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
