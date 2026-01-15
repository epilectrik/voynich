#!/usr/bin/env python3
"""
BRUNSCHWIG DEGREE x VOYNICH REGIME COMPATIBILITY MATRIX

Question: Do Brunschwig's 4 distillation degrees map to specific
          Voynich REGIMEs? Can a third-degree procedure fit in a
          REGIME_2 folio, or would it violate constraints?

Brunschwig Degrees:
  1st (balneum marie) - Gentle, flowers, 2-year shelf life
  2nd (moderate) - Leaves/herbs, 3-year shelf life
  3rd (seething) - Roots/barks, intense heat
  4th (forbidden) - Seeds/resins, dry distillation, dangerous

Voynich REGIMEs:
  REGIME_2 - Low CEI (0.37), low hazard (0.47), curriculum: introductory
  REGIME_1 - Moderate CEI (0.51), moderate hazard (0.61), curriculum: core
  REGIME_4 - Higher CEI (0.58), narrow escape (0.11), curriculum: precision
  REGIME_3 - Highest CEI (0.72), highest hazard (0.65), curriculum: advanced

Hypothesis: Degree N should fit REGIME that matches its intensity level.
"""

from collections import Counter

# ============================================================
# REGIME CONSTRAINT PROFILES (from our validated data)
# ============================================================

REGIME_PROFILES = {
    'REGIME_2': {
        'cei': 0.367,
        'hazard': 0.474,
        'escape': 0.101,
        'description': 'Introductory, low intensity',
        'max_k_steps': 2,      # Limited energy operations
        'max_h_steps': 1,      # Minimal phase complexity
        'requires_link': True,  # Must have monitoring
        'allows_high_impact': False,  # No aggressive interventions
        'curriculum_position': 'EARLY'
    },
    'REGIME_1': {
        'cei': 0.510,
        'hazard': 0.608,
        'escape': 0.202,  # Highest escape = most forgiving
        'description': 'Core training, moderate intensity',
        'max_k_steps': 4,
        'max_h_steps': 2,
        'requires_link': True,
        'allows_high_impact': True,
        'curriculum_position': 'MIDDLE'
    },
    'REGIME_4': {
        'cei': 0.584,
        'hazard': 0.551,
        'escape': 0.107,  # Lowest escape = least forgiving
        'description': 'Precision procedures, narrow tolerance',
        'max_k_steps': 3,
        'max_h_steps': 2,
        'requires_link': True,
        'allows_high_impact': False,  # Must be precise, not aggressive
        'min_link_ratio': 0.25,  # High monitoring requirement
        'curriculum_position': 'MIDDLE'
    },
    'REGIME_3': {
        'cei': 0.717,
        'hazard': 0.653,  # Highest hazard
        'escape': 0.169,
        'description': 'Advanced, high intensity',
        'max_k_steps': 6,  # More energy operations allowed
        'max_h_steps': 3,  # More phase complexity
        'requires_link': True,
        'allows_high_impact': True,
        'min_e_steps': 2,  # Must have recovery capacity
        'curriculum_position': 'LATE'
    }
}

# ============================================================
# BRUNSCHWIG DEGREE PROCEDURES
# ============================================================

# First Degree: Balneum Marie (Water Bath) - GENTLE
FIRST_DEGREE = {
    'name': 'First Degree (Balneum Marie)',
    'materials': 'Flowers, delicate herbs',
    'heat': 'Lukewarm water bath',
    'shelf_life': '1-2 years',
    'procedure': [
        ('AUX', 'Prepare delicate material gently'),
        ('FLOW', 'Place in cucurbit'),
        ('AUX', 'Setup water bath vessel'),
        ('k', 'Apply gentle heat'),
        ('LINK', 'Monitor temperature'),
        ('h', 'Vapor rises slowly'),
        ('FLOW', 'Collect distillate'),
        ('LINK', 'Watch for completion'),
        ('e', 'Cool gradually'),
    ]
}

# Second Degree: Moderate Heat - STANDARD
SECOND_DEGREE = {
    'name': 'Second Degree (Moderate)',
    'materials': 'Leaves, most herbs',
    'heat': 'Warm, sustained',
    'shelf_life': '2-3 years',
    'procedure': [
        ('AUX', 'Chop material'),
        ('FLOW', 'Load cucurbit'),
        ('AUX', 'Seal apparatus'),
        ('k', 'Apply moderate heat'),
        ('LINK', 'Monitor warmth'),
        ('k', 'Maintain heat level'),
        ('h', 'Phase transition'),
        ('FLOW', 'Collect first fraction'),
        ('LINK', 'Monitor rate'),
        ('h', 'Continue distillation'),
        ('FLOW', 'Collect second fraction'),
        ('k', 'Reduce heat'),
        ('LINK', 'Watch for completion'),
        ('e', 'Cool system'),
        ('FLOW', 'Remove product'),
        ('e', 'Return to ambient'),
    ]
}

# Third Degree: Strong/Seething - INTENSE
THIRD_DEGREE = {
    'name': 'Third Degree (Seething)',
    'materials': 'Roots, barks, tough materials',
    'heat': 'Strong, seething',
    'shelf_life': '2-3 years',
    'procedure': [
        ('AUX', 'Grind tough material'),
        ('AUX', 'Soak to soften'),
        ('FLOW', 'Load material'),
        ('AUX', 'Secure apparatus firmly'),
        ('k', 'Apply strong initial heat'),
        ('LINK', 'Monitor pressure'),
        ('k', 'Increase to seething'),
        ('HIGH', 'Maintain high energy'),  # HIGH_IMPACT intervention
        ('h', 'Vigorous phase transition'),
        ('LINK', 'Watch carefully'),
        ('k', 'Sustain heat'),
        ('h', 'Secondary extraction'),
        ('FLOW', 'Collect fraction'),
        ('LINK', 'Monitor exhaustion'),
        ('k', 'Begin reduction'),
        ('k', 'Continue cooling'),
        ('e', 'Stabilize'),
        ('LINK', 'Verify completion'),
        ('FLOW', 'Extract product'),
        ('e', 'Full cooling'),
        ('e', 'Return to safe state'),
    ]
}

# Fourth Degree: Intense/Dry Distillation - DANGEROUS (Brunschwig's "forbidden")
FOURTH_DEGREE = {
    'name': 'Fourth Degree (Intense/Dry)',
    'materials': 'Seeds, resins, animal products',
    'heat': 'Intense, dry distillation',
    'shelf_life': 'Variable',
    'procedure': [
        ('AUX', 'Prepare dense material'),
        ('AUX', 'Special containment setup'),
        ('FLOW', 'Load carefully'),
        ('AUX', 'Reinforce seals'),
        ('k', 'Initial heating'),
        ('LINK', 'Critical monitoring'),
        ('k', 'Increase heat significantly'),
        ('HIGH', 'High energy application'),
        ('LINK', 'Watch for danger signs'),
        ('k', 'Push to decomposition point'),
        ('HIGH', 'Maintain extreme conditions'),
        ('h', 'Destructive phase change'),
        ('LINK', 'Monitor for thermal runaway'),
        ('k', 'Control energy carefully'),
        ('h', 'Secondary decomposition'),
        ('FLOW', 'Capture volatile products'),
        ('HIGH', 'Emergency intervention ready'),
        ('k', 'Begin careful reduction'),
        ('LINK', 'Extended monitoring'),
        ('k', 'Continue reduction'),
        ('e', 'Start stabilization'),
        ('LINK', 'Verify safe state'),
        ('e', 'Extended cooling'),
        ('FLOW', 'Careful extraction'),
        ('e', 'Full return to ambient'),
    ]
}

ALL_DEGREES = [FIRST_DEGREE, SECOND_DEGREE, THIRD_DEGREE, FOURTH_DEGREE]

# ============================================================
# COMPATIBILITY CHECK
# ============================================================

def check_compatibility(procedure_data, regime_name):
    """Check if a procedure fits within a REGIME's constraints."""
    regime = REGIME_PROFILES[regime_name]
    procedure = procedure_data['procedure']

    violations = []
    warnings = []

    # Count instruction types
    sequence = [step[0] for step in procedure]
    counts = Counter(sequence)

    k_count = counts.get('k', 0)
    h_count = counts.get('h', 0)
    e_count = counts.get('e', 0)
    link_count = counts.get('LINK', 0)
    high_count = counts.get('HIGH', 0)
    total = len(sequence)

    # Check k (energy) limit
    max_k = regime.get('max_k_steps', 10)
    if k_count > max_k:
        violations.append(f"Too many energy ops: {k_count} > {max_k} allowed")

    # Check h (phase) limit
    max_h = regime.get('max_h_steps', 10)
    if h_count > max_h:
        violations.append(f"Too many phase transitions: {h_count} > {max_h} allowed")

    # Check LINK requirement
    if regime.get('requires_link', False) and link_count == 0:
        violations.append("Missing required LINK (monitoring) phases")

    # Check LINK ratio for precision regimes
    min_link_ratio = regime.get('min_link_ratio', 0)
    if min_link_ratio > 0:
        actual_ratio = link_count / total if total > 0 else 0
        if actual_ratio < min_link_ratio:
            violations.append(f"Insufficient monitoring: {actual_ratio:.2f} < {min_link_ratio} required")

    # Check HIGH_IMPACT allowance
    if high_count > 0 and not regime.get('allows_high_impact', True):
        violations.append(f"HIGH_IMPACT operations not allowed: {high_count} found")

    # Check minimum e (stability) for intense regimes
    min_e = regime.get('min_e_steps', 0)
    if e_count < min_e:
        violations.append(f"Insufficient recovery capacity: {e_count} < {min_e} required")

    # Check h -> k forbidden transition
    for i in range(len(sequence) - 1):
        if sequence[i] == 'h' and sequence[i+1] == 'k':
            violations.append(f"Forbidden h->k transition at step {i+1}")

    # Calculate intensity metrics
    intensity = (k_count * 2 + h_count * 3 + high_count * 4) / total if total > 0 else 0

    # Check if intensity matches regime
    regime_cei = regime['cei']
    if intensity > regime_cei + 0.3:
        warnings.append(f"Procedure intensity ({intensity:.2f}) may exceed regime capacity ({regime_cei})")
    elif intensity < regime_cei - 0.3:
        warnings.append(f"Procedure intensity ({intensity:.2f}) underutilizes regime capacity ({regime_cei})")

    return {
        'fits': len(violations) == 0,
        'violations': violations,
        'warnings': warnings,
        'stats': {
            'k': k_count,
            'h': h_count,
            'e': e_count,
            'LINK': link_count,
            'HIGH': high_count,
            'total': total,
            'intensity': intensity
        }
    }

def main():
    print("="*75)
    print("BRUNSCHWIG DEGREE x VOYNICH REGIME COMPATIBILITY MATRIX")
    print("="*75)
    print()
    print("Testing whether each Brunschwig degree fits each Voynich REGIME...")
    print()

    # Build the matrix
    results = {}

    for degree in ALL_DEGREES:
        degree_name = degree['name']
        results[degree_name] = {}

        for regime_name in REGIME_PROFILES:
            result = check_compatibility(degree, regime_name)
            results[degree_name][regime_name] = result

    # Print matrix header
    print("COMPATIBILITY MATRIX:")
    print("-"*75)
    header = f"{'Brunschwig Degree':<35}"
    for regime in REGIME_PROFILES:
        header += f" {regime:<10}"
    print(header)
    print("-"*75)

    # Print each row
    for degree in ALL_DEGREES:
        degree_name = degree['name']
        row = f"{degree_name:<35}"

        for regime_name in REGIME_PROFILES:
            result = results[degree_name][regime_name]
            if result['fits']:
                if result['warnings']:
                    symbol = "~"  # Fits with warnings
                else:
                    symbol = "+"  # Clean fit
            else:
                symbol = "-"  # Violation
            row += f" {symbol:^10}"

        print(row)

    print("-"*75)
    print("Legend: + = fits, ~ = fits with warnings, - = violates constraints")

    # Detailed analysis
    print()
    print("="*75)
    print("DETAILED ANALYSIS")
    print("="*75)

    for degree in ALL_DEGREES:
        degree_name = degree['name']
        print(f"\n{degree_name}")
        print("-"*50)
        print(f"Materials: {degree['materials']}")
        print(f"Heat level: {degree['heat']}")
        print(f"Steps: {len(degree['procedure'])}")

        # Show stats
        sequence = [s[0] for s in degree['procedure']]
        counts = Counter(sequence)
        print(f"Composition: k={counts.get('k',0)}, h={counts.get('h',0)}, "
              f"e={counts.get('e',0)}, LINK={counts.get('LINK',0)}, HIGH={counts.get('HIGH',0)}")

        print()
        for regime_name, profile in REGIME_PROFILES.items():
            result = results[degree_name][regime_name]
            status = "FITS" if result['fits'] else "VIOLATES"
            print(f"  vs {regime_name} ({profile['description'][:30]}): {status}")

            if result['violations']:
                for v in result['violations']:
                    print(f"      X {v}")
            if result['warnings']:
                for w in result['warnings']:
                    print(f"      ! {w}")

    # Expected mappings
    print()
    print("="*75)
    print("EXPECTED vs ACTUAL MAPPINGS")
    print("="*75)
    print()

    expected = {
        'First Degree (Balneum Marie)': 'REGIME_2',
        'Second Degree (Moderate)': 'REGIME_1',
        'Third Degree (Seething)': 'REGIME_3',
        'Fourth Degree (Intense/Dry)': 'REGIME_4'  # Precision/narrow tolerance
    }

    print(f"{'Brunschwig Degree':<35} {'Expected':<12} {'Best Fit':<12} {'Match?'}")
    print("-"*75)

    matches = 0
    for degree in ALL_DEGREES:
        degree_name = degree['name']
        expected_regime = expected.get(degree_name, '?')

        # Find best fit (fewest violations, then fewest warnings)
        best_fit = None
        best_score = (-999, 999)  # (negative violations, warnings)

        for regime_name in REGIME_PROFILES:
            result = results[degree_name][regime_name]
            score = (-len(result['violations']), len(result['warnings']))
            if score > best_score:
                best_score = score
                best_fit = regime_name

        match = "YES" if best_fit == expected_regime else "NO"
        if match == "YES":
            matches += 1

        print(f"{degree_name:<35} {expected_regime:<12} {best_fit:<12} {match}")

    print("-"*75)
    print(f"Mapping accuracy: {matches}/{len(ALL_DEGREES)} ({100*matches/len(ALL_DEGREES):.0f}%)")

    # Summary
    print()
    print("="*75)
    print("CONCLUSION")
    print("="*75)

    # Count clean fits per regime
    regime_fit_counts = {r: 0 for r in REGIME_PROFILES}
    for degree in ALL_DEGREES:
        degree_name = degree['name']
        for regime_name in REGIME_PROFILES:
            if results[degree_name][regime_name]['fits']:
                regime_fit_counts[regime_name] += 1

    print()
    print("Procedures that fit each REGIME:")
    for regime, count in regime_fit_counts.items():
        print(f"  {regime}: {count}/4 degrees can fit")

    # Key finding
    print()
    if matches >= 3:
        print("KEY FINDING: Brunschwig degrees map to specific Voynich REGIMEs")
        print("             The mapping is NOT arbitrary - intensity levels correspond")
    else:
        print("KEY FINDING: Mapping is weaker than expected")
        print("             Degrees may fit multiple REGIMEs")

    return results

if __name__ == '__main__':
    main()
