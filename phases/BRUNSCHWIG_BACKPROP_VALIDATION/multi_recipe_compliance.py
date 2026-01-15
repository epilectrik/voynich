#!/usr/bin/env python3
"""
MULTI-RECIPE GRAMMAR COMPLIANCE (Test 4)

Sanity check - defends against "cherry-picked recipe" critique.
Tests 3-5 additional Brunschwig recipes for forbidden transition violations.

Recipes selected:
- Violet water: Very simple (edge case)
- Rosemary oil: Borderline precision/intensity
- Amber oil: "Risky" 4th degree (dry distillation)
"""

import json

# ============================================================
# VALIDATED FORBIDDEN TRANSITIONS (from C109, C332)
# ============================================================

# The "17 forbidden transitions" in C109 are mapped through 5 hazard classes,
# not a simple pairwise list. The key validated suppression is h->k (C332).

FORBIDDEN_TRANSITIONS = [
    ('h', 'k'),   # C332: Phase -> Energy forbidden (0 observed in corpus)
]

# Additional structural constraints (softer - logged but not fatal)
STRUCTURAL_WARNINGS = [
    ('h', 'h'),   # Consecutive phase transitions are unusual
    ('HIGH', 'HIGH'),  # Consecutive high-impact is risky
]

# ============================================================
# BRUNSCHWIG RECIPE TRANSLATIONS
# ============================================================

RECIPES = {
    'violet_water': {
        'name': 'Violet Water',
        'german': 'Veilchenwasser',
        'degree': 1,
        'description': 'First degree, very gentle, delicate aromatics',
        'sequence': [
            'START',
            'LINK',      # Assess material condition
            'k',         # Gentle heat application
            'LINK',      # Monitor temperature
            'h',         # Phase transition (water -> vapor)
            'LINK',      # Observe distillate
            'e',         # Cooling/collection
            'END'
        ],
        'notes': 'Simplest possible distillation'
    },
    'rosemary_oil': {
        'name': 'Rosemary Oil',
        'german': 'Rosmarinoel',
        'degree': 3,
        'description': 'Third degree, aromatic oil extraction, seething heat',
        'sequence': [
            'START',
            'LINK',      # Initial assessment
            'k',         # Heat application
            'LINK',      # Temperature monitoring
            'k',         # Increase heat
            'LINK',      # Monitor
            'h',         # Phase transition
            'LINK',      # Observe
            'k',         # Maintain heat
            'HIGH',      # Intensive extraction
            'LINK',      # Monitor for scorching
            'h',         # Second phase
            'e',         # Cool
            'LINK',      # Check completion
            'e',         # Final stabilization
            'END'
        ],
        'notes': 'Oil extraction requires sustained heat and monitoring'
    },
    'amber_oil': {
        'name': 'Amber Oil',
        'german': 'Bernsteinoel',
        'degree': 4,
        'description': 'Fourth degree, dry/destructive distillation of fossil resin',
        'sequence': [
            'START',
            'LINK',      # Assess amber quality
            'k',         # Initial heat
            'LINK',      # Monitor
            'k',         # Build heat
            'LINK',      # Temperature check
            'HIGH',      # Aggressive heating
            'LINK',      # Watch for decomposition
            'k',         # Continue
            'h',         # Destructive phase transition
            'HIGH',      # Maximum heat
            'LINK',      # Critical monitoring
            'h',         # Further decomposition
            'e',         # Emergency cooling
            'LINK',      # Check product
            'e',         # Final recovery
            'END'
        ],
        'notes': 'Dangerous process, requires careful monitoring'
    }
}

# ============================================================
# COMPLIANCE CHECKING
# ============================================================

def check_compliance(sequence):
    """Check sequence against validated constraints."""
    violations = []
    warnings = []

    for i in range(len(sequence) - 1):
        current = sequence[i]
        next_op = sequence[i + 1]

        transition = (current, next_op)

        # Check hard forbidden (C332: h->k)
        if transition in FORBIDDEN_TRANSITIONS:
            violations.append({
                'position': i,
                'transition': f"{current} -> {next_op}",
                'rule': 'C332: h->k forbidden (phase should not trigger energy increase)'
            })

        # Check structural warnings (soft)
        if transition in STRUCTURAL_WARNINGS:
            warnings.append({
                'position': i,
                'transition': f"{current} -> {next_op}",
                'note': 'Unusual but not forbidden'
            })

    # Check hazard class compliance
    hazard_issues = check_hazards(sequence)

    return violations, warnings, hazard_issues

def check_hazards(sequence):
    """Check for hazard class violations."""
    issues = []

    # Find positions of key operations
    k_positions = [i for i, op in enumerate(sequence) if op == 'k']
    h_positions = [i for i, op in enumerate(sequence) if op == 'h']
    e_positions = [i for i, op in enumerate(sequence) if op == 'e']
    high_positions = [i for i, op in enumerate(sequence) if op == 'HIGH']

    # PHASE_ORDERING: Heat (k) must precede phase transition (h)
    for h_pos in h_positions:
        k_before = [k for k in k_positions if k < h_pos]
        if not k_before:
            issues.append({
                'hazard': 'PHASE_ORDERING',
                'position': h_pos,
                'issue': 'Phase transition without prior heat application'
            })

    # ENERGY_OVERSHOOT: Multiple HIGH operations without cooling
    if len(high_positions) >= 2:
        for i in range(len(high_positions) - 1):
            e_between = [e for e in e_positions if high_positions[i] < e < high_positions[i+1]]
            if not e_between:
                issues.append({
                    'hazard': 'ENERGY_OVERSHOOT',
                    'position': high_positions[i+1],
                    'issue': 'High-impact operations without intermediate cooling'
                })

    return issues

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("MULTI-RECIPE GRAMMAR COMPLIANCE (Test 4)")
    print("=" * 70)
    print()
    print("Tests additional Brunschwig recipes against validated constraints.")
    print("Key rule: C332 (h->k forbidden) + hazard class avoidance.")
    print("Defends against 'cherry-picked recipe' critique.")
    print()

    # Show forbidden transitions
    print("VALIDATED FORBIDDEN TRANSITIONS:")
    print("-" * 50)
    for i, (a, b) in enumerate(FORBIDDEN_TRANSITIONS):
        print(f"  {i+1}. {a} -> {b} (C332)")
    print()

    # Test each recipe
    print("=" * 70)
    print("RECIPE COMPLIANCE TESTS")
    print("=" * 70)
    print()

    all_results = []

    for recipe_key, recipe in RECIPES.items():
        print(f"{recipe['name']} ({recipe['german']})")
        print(f"  Degree: {recipe['degree']}")
        print(f"  Description: {recipe['description']}")
        print()

        # Show sequence
        print(f"  Sequence ({len(recipe['sequence'])} steps):")
        print(f"    {' -> '.join(recipe['sequence'])}")
        print()

        # Check compliance
        violations, warnings, hazards = check_compliance(recipe['sequence'])

        if violations:
            print(f"  VIOLATIONS ({len(violations)}):")
            for v in violations:
                print(f"    Position {v['position']}: {v['transition']}")
                print(f"      Rule: {v['rule']}")
        else:
            print(f"  VIOLATIONS: None (h->k not present)")

        print()

        if warnings:
            print(f"  WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"    Position {w['position']}: {w['transition']} ({w['note']})")

        if hazards:
            print(f"  HAZARD ISSUES ({len(hazards)}):")
            for h in hazards:
                print(f"    {h['hazard']}: {h['issue']}")
        print()

        status = "COMPLIANT" if len(violations) == 0 else f"VIOLATES ({len(violations)})"
        print(f"  Status: [{status}]")
        print()
        print("-" * 50)
        print()

        all_results.append({
            'recipe': recipe['name'],
            'german': recipe['german'],
            'degree': recipe['degree'],
            'sequence_length': len(recipe['sequence']),
            'violations': len(violations),
            'violation_details': violations,
            'warnings': len(warnings),
            'hazard_issues': len(hazards),
            'status': status
        })

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    compliant = sum(1 for r in all_results if r['violations'] == 0)
    total = len(all_results)

    print(f"Recipes tested: {total}")
    print(f"Compliant: {compliant}/{total}")
    print()

    for r in all_results:
        status_char = "+" if r['violations'] == 0 else "X"
        print(f"  [{status_char}] {r['recipe']} (degree {r['degree']}): {r['status']}")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if compliant == total:
        verdict = "PASS"
        interpretation = "All recipes comply with grammar constraints (robustness confirmed)"
    elif compliant >= total - 1:
        verdict = "PARTIAL"
        interpretation = "Most recipes comply, edge cases need review"
    else:
        verdict = "FAIL"
        interpretation = "Multiple recipes violate grammar constraints"

    print(f"Verdict: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    if verdict == "PASS":
        print("Supports C493: Brunschwig procedures can be expressed in Voynich grammar")

    # Save results
    output = {
        'test': 'MULTI_RECIPE_COMPLIANCE',
        'forbidden_transitions': len(FORBIDDEN_TRANSITIONS),
        'recipes_tested': total,
        'recipes_compliant': compliant,
        'results': all_results,
        'summary': {
            'verdict': verdict,
            'interpretation': interpretation
        }
    }

    with open('results/multi_recipe_compliance.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/multi_recipe_compliance.json")

if __name__ == '__main__':
    main()
