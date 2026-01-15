#!/usr/bin/env python3
"""
DEGREE-REGIME VIOLATION MATRIX (Test 2)

Tests what is STRUCTURALLY IMPOSSIBLE, not just what fits.
Shows negative space / boundary enforcement.

Key questions:
1. Can Degree 1 ever violate R3? (Expected: YES, insufficient e_ops)
2. Can Degree 4 ever fit R2? (Expected: NO, k exceeds max)
3. Can Degree 3 fit R4? (Expected: NO, HIGH_IMPACT forbidden)
4. Is violation asymmetric? (Expected: YES, not nested)
"""

import json

# ============================================================
# REGIME CONSTRAINTS (from validated analysis)
# ============================================================

REGIME_CONSTRAINTS = {
    'REGIME_2': {
        'name': 'Introductory',
        'max_k': 2,
        'max_h': 1,
        'allows_high_impact': False,
        'min_link_ratio': 0.0,
        'min_e': 0,
    },
    'REGIME_1': {
        'name': 'Standard',
        'max_k': 4,
        'max_h': 2,
        'allows_high_impact': True,
        'min_link_ratio': 0.0,
        'min_e': 0,
    },
    'REGIME_4': {
        'name': 'Precision',
        'max_k': 3,
        'max_h': 2,
        'allows_high_impact': False,
        'min_link_ratio': 0.25,
        'min_e': 0,
    },
    'REGIME_3': {
        'name': 'Advanced',
        'max_k': 6,
        'max_h': 3,
        'allows_high_impact': True,
        'min_link_ratio': 0.0,
        'min_e': 2,
    },
}

# ============================================================
# BRUNSCHWIG DEGREE PROFILES (typical ranges)
# ============================================================

DEGREE_PROFILES = {
    1: {
        'name': 'First (Balneum Marie)',
        'description': 'Gentle water bath',
        'typical_k': (1, 2),
        'typical_h': (1, 1),
        'high_impact': (0, 0),
        'link_ratio': (0.20, 0.25),
        'e_ops': (0, 1),
    },
    2: {
        'name': 'Second (Moderate)',
        'description': 'Moderate sustained heat',
        'typical_k': (3, 4),
        'typical_h': (1, 2),
        'high_impact': (0, 1),
        'link_ratio': (0.15, 0.20),
        'e_ops': (0, 1),
    },
    3: {
        'name': 'Third (Seething)',
        'description': 'Strong intense heat',
        'typical_k': (5, 6),
        'typical_h': (2, 3),
        'high_impact': (2, 3),
        'link_ratio': (0.10, 0.15),
        'e_ops': (1, 2),
    },
    4: {
        'name': 'Fourth (Dry)',
        'description': 'Extreme/destructive distillation',
        'typical_k': (6, 7),
        'typical_h': (2, 3),
        'high_impact': (3, 4),
        'link_ratio': (0.08, 0.12),
        'e_ops': (1, 2),
    },
}

# ============================================================
# VIOLATION CHECKING
# ============================================================

def check_fit(degree, regime_key, use_min=False, use_max=True):
    """
    Check if a degree can fit a regime.

    use_min: Use minimum values from degree profile (best case)
    use_max: Use maximum values from degree profile (worst case)

    Returns tuple: (can_fit, violations)
    """
    profile = DEGREE_PROFILES[degree]
    regime = REGIME_CONSTRAINTS[regime_key]

    violations = []

    # Select values based on min/max
    if use_max:
        k_val = profile['typical_k'][1]
        h_val = profile['typical_h'][1]
        high_val = profile['high_impact'][1]
        link_val = profile['link_ratio'][0]  # Lower bound is worst for link
        e_val = profile['e_ops'][0]  # Lower bound is worst for e
    else:
        k_val = profile['typical_k'][0]
        h_val = profile['typical_h'][0]
        high_val = profile['high_impact'][0]
        link_val = profile['link_ratio'][1]  # Upper bound is best for link
        e_val = profile['e_ops'][1]  # Upper bound is best for e

    # Check k constraint
    if k_val > regime['max_k']:
        violations.append(f"k={k_val} > max_k={regime['max_k']}")

    # Check h constraint
    if h_val > regime['max_h']:
        violations.append(f"h={h_val} > max_h={regime['max_h']}")

    # Check HIGH_IMPACT
    if high_val > 0 and not regime['allows_high_impact']:
        violations.append(f"HIGH_IMPACT={high_val}, regime forbids HIGH_IMPACT")

    # Check min_link_ratio
    if link_val < regime['min_link_ratio']:
        violations.append(f"LINK={link_val:.0%} < min_link={regime['min_link_ratio']:.0%}")

    # Check min_e
    if e_val < regime['min_e']:
        violations.append(f"e={e_val} < min_e={regime['min_e']}")

    can_fit = len(violations) == 0
    return can_fit, violations

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 75)
    print("DEGREE-REGIME VIOLATION MATRIX (Test 2)")
    print("=" * 75)
    print()
    print("Tests what is STRUCTURALLY IMPOSSIBLE, not just what fits.")
    print()

    # Show constraints
    print("REGIME CONSTRAINTS:")
    print("-" * 75)
    print(f"{'REGIME':<12} {'max_k':>6} {'max_h':>6} {'HIGH':>8} {'min_LINK':>10} {'min_e':>6}")
    print("-" * 75)

    for regime_key, regime in REGIME_CONSTRAINTS.items():
        high_str = "ALLOWED" if regime['allows_high_impact'] else "FORBID"
        link_str = f"{regime['min_link_ratio']:.0%}" if regime['min_link_ratio'] > 0 else "-"
        e_str = str(regime['min_e']) if regime['min_e'] > 0 else "-"
        print(f"{regime_key:<12} {regime['max_k']:>6} {regime['max_h']:>6} {high_str:>8} {link_str:>10} {e_str:>6}")
    print()

    # Show degree profiles
    print("BRUNSCHWIG DEGREE PROFILES (typical ranges):")
    print("-" * 75)
    print(f"{'Degree':<25} {'k':>10} {'h':>10} {'HIGH':>10} {'LINK':>12} {'e':>8}")
    print("-" * 75)

    for degree, profile in DEGREE_PROFILES.items():
        k_range = f"{profile['typical_k'][0]}-{profile['typical_k'][1]}"
        h_range = f"{profile['typical_h'][0]}-{profile['typical_h'][1]}"
        high_range = f"{profile['high_impact'][0]}-{profile['high_impact'][1]}"
        link_range = f"{profile['link_ratio'][0]:.0%}-{profile['link_ratio'][1]:.0%}"
        e_range = f"{profile['e_ops'][0]}-{profile['e_ops'][1]}"
        print(f"{profile['name']:<25} {k_range:>10} {h_range:>10} {high_range:>10} {link_range:>12} {e_range:>8}")
    print()

    # Build violation matrix
    print("=" * 75)
    print("VIOLATION MATRIX (worst case - can degree NEVER fit regime?)")
    print("=" * 75)
    print()

    regimes = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
    degrees = [1, 2, 3, 4]

    # Header
    print(f"{'Degree':<25}", end="")
    for r in regimes:
        print(f" {r:>10}", end="")
    print()
    print("-" * 75)

    matrix = {}

    for degree in degrees:
        profile = DEGREE_PROFILES[degree]
        print(f"{profile['name']:<25}", end="")

        matrix[degree] = {}

        for regime_key in regimes:
            can_fit, violations = check_fit(degree, regime_key, use_max=True)

            matrix[degree][regime_key] = {
                'can_fit': can_fit,
                'violations': violations
            }

            if can_fit:
                print(f" {'CAN FIT':>10}", end="")
            else:
                print(f" {'VIOLATES':>10}", end="")
        print()
    print()

    # Detailed violations
    print("=" * 75)
    print("DETAILED VIOLATIONS")
    print("=" * 75)
    print()

    for degree in degrees:
        profile = DEGREE_PROFILES[degree]
        print(f"{profile['name']}:")

        for regime_key in regimes:
            result = matrix[degree][regime_key]
            if not result['can_fit']:
                violations_str = "; ".join(result['violations'])
                print(f"  {regime_key}: {violations_str}")

        if all(matrix[degree][r]['can_fit'] for r in regimes):
            print(f"  (fits all regimes)")
        print()

    # Best case matrix (minimum values)
    print("=" * 75)
    print("COMPATIBILITY MATRIX (best case - can degree EVER fit regime?)")
    print("=" * 75)
    print()

    print(f"{'Degree':<25}", end="")
    for r in regimes:
        print(f" {r:>10}", end="")
    print()
    print("-" * 75)

    best_matrix = {}

    for degree in degrees:
        profile = DEGREE_PROFILES[degree]
        print(f"{profile['name']:<25}", end="")

        best_matrix[degree] = {}

        for regime_key in regimes:
            can_fit, violations = check_fit(degree, regime_key, use_max=False)

            best_matrix[degree][regime_key] = {
                'can_fit': can_fit,
                'violations': violations
            }

            if can_fit:
                print(f" {'POSSIBLE':>10}", end="")
            else:
                print(f" {'NEVER':>10}", end="")
        print()
    print()

    # Specific questions from plan
    print("=" * 75)
    print("SPECIFIC QUESTIONS")
    print("=" * 75)
    print()

    questions = [
        ("Can Degree 1 violate R3?", 1, 'REGIME_3', True, "YES, insufficient e_ops"),
        ("Can Degree 4 fit R2?", 4, 'REGIME_2', False, "NO, k exceeds max"),
        ("Can Degree 3 fit R4?", 3, 'REGIME_4', False, "NO, HIGH_IMPACT forbidden"),
    ]

    for question, degree, regime, expected_violate, expected_reason in questions:
        can_fit_worst, viol_worst = check_fit(degree, regime, use_max=True)
        can_fit_best, viol_best = check_fit(degree, regime, use_max=False)

        print(f"Q: {question}")
        print(f"   Expected: {expected_reason}")

        if expected_violate:
            # We expect violation
            if not can_fit_worst:
                result = "CONFIRMED"
                actual = f"Violations: {'; '.join(viol_worst)}"
            else:
                result = "UNEXPECTED - no violation found"
                actual = "Degree fits regime"
        else:
            # We expect no fit possible
            if not can_fit_best:
                result = "CONFIRMED"
                actual = f"Violations: {'; '.join(viol_best)}"
            else:
                result = "UNEXPECTED - fit is possible"
                actual = "Degree can fit regime"

        print(f"   Result: {result}")
        print(f"   Actual: {actual}")
        print()

    # Asymmetry check
    print("=" * 75)
    print("ASYMMETRY CHECK")
    print("=" * 75)
    print()

    # Count violations per degree and per regime
    degree_violations = {d: sum(1 for r in regimes if not best_matrix[d][r]['can_fit']) for d in degrees}
    regime_violations = {r: sum(1 for d in degrees if not best_matrix[d][r]['can_fit']) for r in regimes}

    print("Violations by degree (best case):")
    for d in degrees:
        print(f"  Degree {d}: {degree_violations[d]}/4 regimes impossible")

    print()
    print("Violations by regime (best case):")
    for r in regimes:
        print(f"  {r}: {regime_violations[r]}/4 degrees impossible")

    # Check if nested
    is_nested = all(degree_violations[i] <= degree_violations[j] for i, j in [(1,2), (2,3), (3,4)])
    print()
    print(f"Is structure fully nested? {is_nested}")

    # Count asymmetric cells
    asymmetric_cells = 0
    for d in degrees:
        for r in regimes:
            # Check if this cell differs from what simple nesting would predict
            worst = not matrix[d][r]['can_fit']
            best = not best_matrix[d][r]['can_fit']
            if worst != best:
                asymmetric_cells += 1

    print(f"Cells with range-dependent outcome: {asymmetric_cells}/16")

    # Verdict
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    # Count violation cells and compatibility cells
    violation_cells = sum(1 for d in degrees for r in regimes if not best_matrix[d][r]['can_fit'])
    compatibility_cells = sum(1 for d in degrees for r in regimes if best_matrix[d][r]['can_fit'])

    # Check pass criteria
    high_degree_violations = sum(1 for d in [3, 4] for r in ['REGIME_2', 'REGIME_4']
                                  if not best_matrix[d][r]['can_fit'])
    low_degree_compat = sum(1 for d in [1, 2] for r in ['REGIME_1', 'REGIME_2']
                            if best_matrix[d][r]['can_fit'])

    print(f"Violation cells (best case): {violation_cells}/16")
    print(f"Compatibility cells (best case): {compatibility_cells}/16")
    print(f"High degree (3-4) violations in R2/R4: {high_degree_violations}/4 (need >= 4)")
    print(f"Low degree (1-2) compatibility with R1/R2: {low_degree_compat}/4 (need >= 2)")
    print()

    if high_degree_violations >= 4 and low_degree_compat >= 2 and not is_nested:
        verdict = "PASS"
        interpretation = "Degree-REGIME violations are asymmetric (boundary enforcement confirmed)"
    elif high_degree_violations >= 3 and low_degree_compat >= 2:
        verdict = "PARTIAL"
        interpretation = "Some boundary enforcement, structure not fully asymmetric"
    else:
        verdict = "FAIL"
        interpretation = "Boundary enforcement not demonstrated"

    print(f"Verdict: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    if verdict == "PASS":
        print("C496 CANDIDATE: Degree-REGIME violations are asymmetric (boundary enforcement)")

    # Save results
    output = {
        'test': 'DEGREE_REGIME_VIOLATIONS',
        'regime_constraints': REGIME_CONSTRAINTS,
        'degree_profiles': {str(k): v for k, v in DEGREE_PROFILES.items()},
        'worst_case_matrix': {str(d): {r: {'can_fit': m['can_fit'], 'violations': m['violations']}
                                        for r, m in row.items()}
                              for d, row in matrix.items()},
        'best_case_matrix': {str(d): {r: {'can_fit': m['can_fit'], 'violations': m['violations']}
                                       for r, m in row.items()}
                             for d, row in best_matrix.items()},
        'summary': {
            'violation_cells': violation_cells,
            'compatibility_cells': compatibility_cells,
            'is_nested': is_nested,
            'verdict': verdict,
            'interpretation': interpretation
        }
    }

    with open('results/degree_regime_violations.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/degree_regime_violations.json")

if __name__ == '__main__':
    main()
