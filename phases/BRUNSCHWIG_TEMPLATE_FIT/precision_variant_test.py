#!/usr/bin/env python3
"""
PRECISION VARIANT TEST

Hypothesis: REGIME_4 is for PRECISION procedures, not high-intensity ones.
            A "precision first-degree" procedure should fit REGIME_4.

Precision characteristics:
- High monitoring ratio (LINK)
- No aggressive interventions (no HIGH_IMPACT)
- Tight control sequences
- More stability checks (e)

Examples:
- Distilling volatile aromatics (gentle but exact timing)
- Separating close-boiling fractions (narrow temperature window)
- Heat-sensitive materials (must not overshoot even slightly)
"""

from collections import Counter

# ============================================================
# REGIME PROFILES (same as before)
# ============================================================

REGIME_PROFILES = {
    'REGIME_2': {
        'cei': 0.367,
        'hazard': 0.474,
        'escape': 0.101,
        'description': 'Introductory, low intensity',
        'max_k_steps': 2,
        'max_h_steps': 1,
        'requires_link': True,
        'allows_high_impact': False,
        'curriculum_position': 'EARLY'
    },
    'REGIME_1': {
        'cei': 0.510,
        'hazard': 0.608,
        'escape': 0.202,
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
        'allows_high_impact': False,
        'min_link_ratio': 0.25,
        'curriculum_position': 'MIDDLE'
    },
    'REGIME_3': {
        'cei': 0.717,
        'hazard': 0.653,
        'description': 'Advanced, high intensity',
        'max_k_steps': 6,
        'max_h_steps': 3,
        'requires_link': True,
        'allows_high_impact': True,
        'min_e_steps': 2,
        'curriculum_position': 'LATE'
    }
}

# ============================================================
# STANDARD vs PRECISION PROCEDURES
# ============================================================

# Standard First Degree (from before)
STANDARD_FIRST_DEGREE = {
    'name': 'Standard First Degree',
    'description': 'Basic water bath distillation',
    'procedure': [
        ('AUX', 'Prepare material'),
        ('FLOW', 'Load cucurbit'),
        ('AUX', 'Setup apparatus'),
        ('k', 'Apply gentle heat'),
        ('LINK', 'Monitor temperature'),
        ('h', 'Phase transition'),
        ('FLOW', 'Collect distillate'),
        ('LINK', 'Watch completion'),
        ('e', 'Cool system'),
    ]
}

# PRECISION First Degree - volatile aromatics
PRECISION_FIRST_DEGREE = {
    'name': 'Precision First Degree (Volatile Aromatics)',
    'description': 'Gentle heat but exact timing for volatile compounds',
    'procedure': [
        ('AUX', 'Prepare delicate material carefully'),
        ('FLOW', 'Load measured amount'),
        ('AUX', 'Setup with thermometer'),
        ('LINK', 'Verify starting conditions'),
        ('k', 'Apply very gentle heat'),
        ('LINK', 'Monitor temperature precisely'),
        ('LINK', 'Watch for first vapor signs'),
        ('e', 'Check stability'),
        ('h', 'Controlled phase transition'),
        ('LINK', 'Monitor vapor rate'),
        ('FLOW', 'Collect first fraction'),
        ('LINK', 'Verify purity'),
        ('e', 'Stabilize before continuing'),
        ('LINK', 'Check conditions'),
        ('k', 'Slight adjustment if needed'),
        ('LINK', 'Continue monitoring'),
        ('FLOW', 'Collect main fraction'),
        ('LINK', 'Watch for endpoint'),
        ('e', 'Begin controlled cooling'),
        ('LINK', 'Verify completion'),
        ('e', 'Return to ambient'),
    ]
}

# Standard Second Degree
STANDARD_SECOND_DEGREE = {
    'name': 'Standard Second Degree',
    'description': 'Moderate heat for herbs',
    'procedure': [
        ('AUX', 'Chop material'),
        ('FLOW', 'Load cucurbit'),
        ('AUX', 'Seal apparatus'),
        ('k', 'Apply moderate heat'),
        ('LINK', 'Monitor warmth'),
        ('k', 'Maintain heat'),
        ('h', 'Phase transition'),
        ('FLOW', 'Collect fraction'),
        ('LINK', 'Monitor rate'),
        ('h', 'Continue distillation'),
        ('FLOW', 'Collect second fraction'),
        ('k', 'Reduce heat'),
        ('LINK', 'Watch completion'),
        ('e', 'Cool system'),
        ('FLOW', 'Remove product'),
        ('e', 'Return to ambient'),
    ]
}

# PRECISION Second Degree - close-boiling fractions
PRECISION_SECOND_DEGREE = {
    'name': 'Precision Second Degree (Fraction Separation)',
    'description': 'Narrow temperature window for separating similar compounds',
    'procedure': [
        ('AUX', 'Prepare material uniformly'),
        ('FLOW', 'Load exact amount'),
        ('AUX', 'Calibrate apparatus'),
        ('LINK', 'Verify setup'),
        ('k', 'Gentle initial heat'),
        ('LINK', 'Monitor temperature rise'),
        ('LINK', 'Watch approach to target'),
        ('e', 'Stabilize at threshold'),
        ('LINK', 'Verify stable conditions'),
        ('k', 'Fine adjustment'),
        ('h', 'First fraction begins'),
        ('LINK', 'Monitor transition'),
        ('FLOW', 'Collect first cut'),
        ('LINK', 'Check purity'),
        ('e', 'Brief stabilization'),
        ('k', 'Slight increase'),
        ('LINK', 'Monitor second window'),
        ('h', 'Second fraction'),
        ('FLOW', 'Collect second cut'),
        ('LINK', 'Verify separation'),
        ('e', 'Stabilize'),
        ('LINK', 'Check completion'),
        ('k', 'Reduce carefully'),
        ('e', 'Controlled cooling'),
        ('LINK', 'Final verification'),
        ('e', 'Ambient return'),
    ]
}

# PRECISION Third Degree equivalent - controlled intense
PRECISION_INTENSE = {
    'name': 'Precision Intense (Controlled High-Energy)',
    'description': 'Higher energy but with tight monitoring, no aggressive moves',
    'procedure': [
        ('AUX', 'Careful preparation'),
        ('AUX', 'Reinforce containment'),
        ('FLOW', 'Measured loading'),
        ('LINK', 'Pre-heat check'),
        ('k', 'Initial heat'),
        ('LINK', 'Monitor rise'),
        ('e', 'Verify stability'),
        ('LINK', 'Check before increase'),
        ('k', 'Increase gradually'),
        ('LINK', 'Close monitoring'),
        ('LINK', 'Watch for threshold'),
        ('h', 'Phase transition'),
        ('LINK', 'Monitor transition'),
        ('e', 'Stabilize'),
        ('FLOW', 'Collect fraction'),
        ('LINK', 'Purity check'),
        ('k', 'Maintain level'),
        ('LINK', 'Continue monitoring'),
        ('h', 'Secondary extraction'),
        ('LINK', 'Watch endpoint'),
        ('e', 'Begin reduction'),
        ('LINK', 'Verify safe state'),
        ('e', 'Extended cooling'),
        ('LINK', 'Final check'),
        ('e', 'Ambient'),
    ]
}

ALL_PROCEDURES = [
    STANDARD_FIRST_DEGREE,
    PRECISION_FIRST_DEGREE,
    STANDARD_SECOND_DEGREE,
    PRECISION_SECOND_DEGREE,
    PRECISION_INTENSE,
]

# ============================================================
# COMPATIBILITY CHECK (same as before)
# ============================================================

def check_compatibility(procedure_data, regime_name):
    """Check if a procedure fits within a REGIME's constraints."""
    regime = REGIME_PROFILES[regime_name]
    procedure = procedure_data['procedure']

    violations = []
    warnings = []

    sequence = [step[0] for step in procedure]
    counts = Counter(sequence)

    k_count = counts.get('k', 0)
    h_count = counts.get('h', 0)
    e_count = counts.get('e', 0)
    link_count = counts.get('LINK', 0)
    high_count = counts.get('HIGH', 0)
    total = len(sequence)

    # Check limits
    max_k = regime.get('max_k_steps', 10)
    if k_count > max_k:
        violations.append(f"Too many k ops: {k_count} > {max_k}")

    max_h = regime.get('max_h_steps', 10)
    if h_count > max_h:
        violations.append(f"Too many h ops: {h_count} > {max_h}")

    if regime.get('requires_link', False) and link_count == 0:
        violations.append("Missing LINK phases")

    min_link_ratio = regime.get('min_link_ratio', 0)
    if min_link_ratio > 0:
        actual_ratio = link_count / total if total > 0 else 0
        if actual_ratio < min_link_ratio:
            violations.append(f"Insufficient monitoring: {actual_ratio:.2f} < {min_link_ratio}")

    if high_count > 0 and not regime.get('allows_high_impact', True):
        violations.append(f"HIGH_IMPACT not allowed: {high_count} found")

    min_e = regime.get('min_e_steps', 0)
    if e_count < min_e:
        violations.append(f"Insufficient e ops: {e_count} < {min_e}")

    # Check h -> k forbidden
    for i in range(len(sequence) - 1):
        if sequence[i] == 'h' and sequence[i+1] == 'k':
            violations.append(f"Forbidden h->k at step {i+1}")

    return {
        'fits': len(violations) == 0,
        'violations': violations,
        'warnings': warnings,
        'stats': {
            'k': k_count, 'h': h_count, 'e': e_count,
            'LINK': link_count, 'HIGH': high_count,
            'total': total,
            'link_ratio': link_count / total if total > 0 else 0
        }
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*75)
    print("PRECISION VARIANT TEST")
    print("="*75)
    print()
    print("Hypothesis: REGIME_4 is for PRECISION procedures, not intensity.")
    print("            Precision variants of any degree should fit REGIME_4.")
    print()

    # Test each procedure
    results = {}
    for proc in ALL_PROCEDURES:
        results[proc['name']] = {}
        for regime in REGIME_PROFILES:
            results[proc['name']][regime] = check_compatibility(proc, regime)

    # Print comparison table
    print("STANDARD vs PRECISION COMPARISON:")
    print("-"*75)
    print(f"{'Procedure':<45} {'REGIME_4 Fit?':<15} {'Link Ratio'}")
    print("-"*75)

    for proc in ALL_PROCEDURES:
        name = proc['name']
        r4_result = results[name]['REGIME_4']
        status = "YES" if r4_result['fits'] else "NO"
        link_ratio = r4_result['stats']['link_ratio']

        # Highlight precision variants
        marker = "***" if "Precision" in name and r4_result['fits'] else ""
        print(f"{name:<45} {status:<15} {link_ratio:.2f} {marker}")

    # Detailed REGIME_4 analysis
    print()
    print("="*75)
    print("REGIME_4 DETAILED ANALYSIS")
    print("="*75)
    print()
    print("REGIME_4 requirements:")
    print("  - max_k_steps: 3")
    print("  - max_h_steps: 2")
    print("  - min_link_ratio: 0.25 (25% monitoring)")
    print("  - allows_high_impact: NO")
    print()

    for proc in ALL_PROCEDURES:
        name = proc['name']
        r4 = results[name]['REGIME_4']
        stats = r4['stats']

        print(f"{name}:")
        print(f"  Stats: k={stats['k']}, h={stats['h']}, e={stats['e']}, "
              f"LINK={stats['LINK']}, HIGH={stats['HIGH']}")
        print(f"  Link ratio: {stats['link_ratio']:.2f}")
        print(f"  REGIME_4: {'FITS' if r4['fits'] else 'VIOLATES'}")
        if r4['violations']:
            for v in r4['violations']:
                print(f"    X {v}")
        print()

    # Full matrix for precision variants
    print("="*75)
    print("FULL COMPATIBILITY MATRIX (Precision Variants)")
    print("="*75)
    print()
    print(f"{'Procedure':<45} R2   R1   R4   R3")
    print("-"*75)

    for proc in ALL_PROCEDURES:
        name = proc['name'][:44]
        row = f"{name:<45}"
        for regime in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']:
            fits = results[proc['name']][regime]['fits']
            row += f" {'+':<4}" if fits else f" {'-':<4}"
        print(row)

    # Conclusion
    print()
    print("="*75)
    print("CONCLUSION")
    print("="*75)
    print()

    # Check if precision variants fit REGIME_4
    precision_procs = [p for p in ALL_PROCEDURES if 'Precision' in p['name']]
    precision_fit_r4 = sum(1 for p in precision_procs
                          if results[p['name']]['REGIME_4']['fits'])

    standard_procs = [p for p in ALL_PROCEDURES if 'Standard' in p['name']]
    standard_fit_r4 = sum(1 for p in standard_procs
                         if results[p['name']]['REGIME_4']['fits'])

    print(f"Standard procedures that fit REGIME_4: {standard_fit_r4}/{len(standard_procs)}")
    print(f"Precision procedures that fit REGIME_4: {precision_fit_r4}/{len(precision_procs)}")
    print()

    if precision_fit_r4 > standard_fit_r4:
        print("*** HYPOTHESIS CONFIRMED ***")
        print()
        print("REGIME_4 is the PRECISION regime - it accepts procedures with:")
        print("  - High monitoring ratio (25%+ LINK operations)")
        print("  - No aggressive interventions (no HIGH_IMPACT)")
        print("  - Controlled energy operations (max 3 k-steps)")
        print()
        print("This is NOT about intensity level - it's about CONTROL TIGHTNESS.")
        print("A gentle procedure requiring precision fits REGIME_4.")
        print("A violent procedure without precision does NOT fit REGIME_4.")
    else:
        print("Hypothesis not confirmed - need to adjust model")

    return results

if __name__ == '__main__':
    main()
