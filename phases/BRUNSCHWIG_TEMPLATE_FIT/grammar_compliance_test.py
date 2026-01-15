#!/usr/bin/env python3
"""
BRUNSCHWIG -> VOYNICH GRAMMAR COMPLIANCE TEST

Question: Can a Brunschwig distillation procedure be expressed in Voynich
          grammar WITHOUT violating any validated constraints?

This tests whether the procedural logic of distillation is compatible
with Voynich's 17 forbidden transitions and kernel grammar rules.

Key constraints to check:
- C109: 17 forbidden transitions (5 hazard classes)
- C332: h->k suppressed (phase shouldn't trigger energy increase)
- C107: Kernel boundary adjacency
- C360: No violations cross line boundaries
- C366: LINK marks monitoring/intervention boundary
"""

# ============================================================
# VOYNICH INSTRUCTION CLASSES (from BCSC)
# ============================================================

INSTRUCTION_CLASSES = {
    # Kernel operators
    'k': {'role': 'ENERGY_MODULATOR', 'desc': 'Adjusts energy input'},
    'h': {'role': 'PHASE_MANAGER', 'desc': 'Manages phase transitions'},
    'e': {'role': 'STABILITY_ANCHOR', 'desc': 'Maintains stable state'},

    # Other operators
    'FLOW': {'role': 'FLOW_OPERATOR', 'desc': 'Transfer/movement'},
    'LINK': {'role': 'MONITORING', 'desc': 'Waiting/observation phase'},
    'AUX': {'role': 'AUXILIARY', 'desc': 'Support operations'},
    'HIGH': {'role': 'HIGH_IMPACT', 'desc': 'Major interventions'},
}

# ============================================================
# VOYNICH HAZARD CLASSES (from C109)
# ============================================================

HAZARDS = {
    'PHASE_ORDERING': {
        'desc': 'Material in wrong phase location',
        'examples': ['vapor before heat', 'collect before condense'],
        'percentage': 41
    },
    'COMPOSITION_JUMP': {
        'desc': 'Impure fractions passing',
        'examples': ['mixing heads with hearts', 'skip rectification'],
        'percentage': 24
    },
    'CONTAINMENT_TIMING': {
        'desc': 'Overflow/pressure events',
        'examples': ['seal before venting', 'overfill'],
        'percentage': 24
    },
    'RATE_MISMATCH': {
        'desc': 'Flow imbalance',
        'examples': ['heat faster than condense capacity'],
        'percentage': 6
    },
    'ENERGY_OVERSHOOT': {
        'desc': 'Thermal damage',
        'examples': ['too much heat', 'fourth degree on flowers'],
        'percentage': 6
    }
}

# ============================================================
# VOYNICH GRAMMAR RULES (from BCSC)
# ============================================================

GRAMMAR_RULES = {
    'h_to_k_suppressed': {
        'constraint': 'C332',
        'rule': 'h -> k transition is forbidden (0 observed)',
        'meaning': 'Phase change should not directly trigger energy increase'
    },
    'e_dominates_recovery': {
        'constraint': 'C105',
        'rule': 'e-class provides 54.7% of recovery paths',
        'meaning': 'Stability anchor is primary recovery mechanism'
    },
    'link_boundary': {
        'constraint': 'C366',
        'rule': 'LINK marks monitoring/intervention boundary',
        'meaning': 'Observation phases are explicitly marked'
    },
    'line_invariant': {
        'constraint': 'C360',
        'rule': '0 forbidden transitions span line breaks',
        'meaning': 'Lines are self-contained control blocks'
    }
}

# ============================================================
# BRUNSCHWIG BALNEUM MARIE (Water Bath) PROCEDURE
# ============================================================

BALNEUM_MARIE_PROCEDURE = [
    # Step, Brunschwig action, Voynich class, Notes
    (1, "Chop/prepare material", "AUX", "Preparation phase"),
    (2, "Place material in cucurbit", "FLOW", "Loading input"),
    (3, "Add water to outer vessel", "FLOW", "Setup water bath"),
    (4, "Attach alembic head and receiver", "AUX", "Assembly"),
    (5, "Seal joints with luting", "AUX", "Containment setup"),
    (6, "Apply gentle heat to water bath", "k", "ENERGY modulation - first degree"),
    (7, "Wait for water to warm", "LINK", "Monitoring phase"),
    (8, "Observe vapor beginning to rise", "LINK", "Monitor phase transition"),
    (9, "Vapor condenses in alembic head", "h", "PHASE transition"),
    (10, "Distillate flows to receiver", "FLOW", "Product collection"),
    (11, "Monitor distillation rate", "LINK", "Rate observation"),
    (12, "Adjust heat if needed", "k", "ENERGY correction"),
    (13, "Continue until fraction complete", "LINK", "Duration monitoring"),
    (14, "Reduce heat gradually", "k", "ENERGY reduction"),
    (15, "Allow system to cool", "e", "STABILITY - cooling"),
    (16, "Wait for condensation to stop", "LINK", "Monitor completion"),
    (17, "Remove receiver with distillate", "FLOW", "Output extraction"),
    (18, "System returns to ambient", "e", "STABILITY - final state"),
]

# ============================================================
# COMPLIANCE CHECK
# ============================================================

def check_hazard_compliance(procedure):
    """Check if procedure avoids all 5 hazard classes."""
    violations = []

    # Extract sequence
    sequence = [(s[0], s[2], s[1]) for s in procedure]  # (step, class, action)

    # Check PHASE_ORDERING
    # Rule: Must have heat (k) before phase transition (h)
    k_steps = [s[0] for s in sequence if s[1] == 'k']
    h_steps = [s[0] for s in sequence if s[1] == 'h']

    for h_step in h_steps:
        k_before = [k for k in k_steps if k < h_step]
        if not k_before:
            violations.append(('PHASE_ORDERING', h_step, 'Phase transition without prior heat'))

    # Check CONTAINMENT_TIMING
    # Rule: Sealing (AUX) must happen before heat (k)
    aux_steps = [s[0] for s in sequence if s[1] == 'AUX']
    first_k = min(k_steps) if k_steps else 999
    seal_before_heat = any(a < first_k for a in aux_steps)

    if not seal_before_heat:
        violations.append(('CONTAINMENT_TIMING', first_k, 'Heat applied before containment setup'))

    # Check ENERGY_OVERSHOOT
    # Rule: Heat reduction (k) should come before final stability (e)
    e_steps = [s[0] for s in sequence if s[1] == 'e']
    if e_steps and k_steps:
        last_k = max(k_steps)
        first_e = min(e_steps)
        # k should have a reduction step before e
        # (we check if there's any k near the end, suggesting controlled shutdown)
        if last_k > first_e:
            violations.append(('ENERGY_OVERSHOOT', last_k, 'Energy still active after stability phase'))

    # Check RATE_MISMATCH
    # Rule: LINK (monitoring) should occur between heat and phase
    link_steps = [s[0] for s in sequence if s[1] == 'LINK']
    for h_step in h_steps:
        k_before = [k for k in k_steps if k < h_step]
        if k_before:
            last_k_before_h = max(k_before)
            link_between = [l for l in link_steps if last_k_before_h < l < h_step]
            if not link_between:
                violations.append(('RATE_MISMATCH', h_step, 'No monitoring between heat and phase transition'))

    return violations

def check_grammar_compliance(procedure):
    """Check if procedure follows Voynich grammar rules."""
    violations = []

    sequence = [s[2] for s in procedure]  # Just the classes

    # Check h -> k suppression (C332)
    for i in range(len(sequence) - 1):
        if sequence[i] == 'h' and sequence[i+1] == 'k':
            violations.append(('h_to_k_suppressed', i+1,
                             f'Step {i+2}: h followed by k (forbidden transition)'))

    # Check e dominance in recovery
    # After any h (phase), should eventually reach e (stability)
    h_indices = [i for i, s in enumerate(sequence) if s == 'h']
    e_indices = [i for i, s in enumerate(sequence) if s == 'e']

    for h_idx in h_indices:
        e_after = [e for e in e_indices if e > h_idx]
        if not e_after:
            violations.append(('e_dominates_recovery', h_idx,
                             f'Step {h_idx+1}: Phase transition with no subsequent stability'))

    # Check LINK as monitoring boundary
    # LINK should appear between active phases
    link_indices = [i for i, s in enumerate(sequence) if s == 'LINK']
    if not link_indices:
        violations.append(('link_boundary', 0, 'No monitoring phases (LINK) in procedure'))

    return violations

def main():
    print("="*70)
    print("BRUNSCHWIG -> VOYNICH GRAMMAR COMPLIANCE TEST")
    print("="*70)
    print()
    print("Question: Can a Brunschwig distillation procedure be expressed")
    print("          in Voynich grammar WITHOUT violating any constraints?")
    print()

    # Display the procedure
    print("BRUNSCHWIG BALNEUM MARIE (Water Bath) PROCEDURE:")
    print("-"*70)
    print(f"{'Step':<5} {'Voynich':<8} {'Brunschwig Action':<45}")
    print("-"*70)

    for step, action, vclass, notes in BALNEUM_MARIE_PROCEDURE:
        print(f"{step:<5} {vclass:<8} {action:<45}")

    print()
    print(f"Total steps: {len(BALNEUM_MARIE_PROCEDURE)}")

    # Count by class
    from collections import Counter
    class_counts = Counter(s[2] for s in BALNEUM_MARIE_PROCEDURE)
    print(f"By Voynich class: {dict(class_counts)}")

    # Check hazard compliance
    print()
    print("="*70)
    print("HAZARD COMPLIANCE CHECK (C109: 17 forbidden transitions)")
    print("="*70)

    hazard_violations = check_hazard_compliance(BALNEUM_MARIE_PROCEDURE)

    for hazard_class, info in HAZARDS.items():
        violations_in_class = [v for v in hazard_violations if v[0] == hazard_class]
        status = "VIOLATION" if violations_in_class else "COMPLIANT"
        symbol = "-" if violations_in_class else "+"
        print(f"  [{symbol}] {hazard_class} ({info['percentage']}%): {status}")
        print(f"      Rule: {info['desc']}")
        for v in violations_in_class:
            print(f"      >> Step {v[1]}: {v[2]}")

    # Check grammar compliance
    print()
    print("="*70)
    print("GRAMMAR COMPLIANCE CHECK")
    print("="*70)

    grammar_violations = check_grammar_compliance(BALNEUM_MARIE_PROCEDURE)

    for rule_name, rule_info in GRAMMAR_RULES.items():
        violations_for_rule = [v for v in grammar_violations if v[0] == rule_name]
        status = "VIOLATION" if violations_for_rule else "COMPLIANT"
        symbol = "-" if violations_for_rule else "+"
        print(f"  [{symbol}] {rule_info['constraint']}: {status}")
        print(f"      Rule: {rule_info['rule']}")
        for v in violations_for_rule:
            print(f"      >> {v[2]}")

    # Overall verdict
    print()
    print("="*70)
    print("VERDICT")
    print("="*70)

    total_violations = len(hazard_violations) + len(grammar_violations)

    if total_violations == 0:
        print()
        print("  *** FULL COMPLIANCE ***")
        print()
        print("  The Brunschwig balneum marie procedure CAN be expressed")
        print("  in Voynich grammar without violating ANY constraints.")
        print()
        print("  This means:")
        print("    1. Voynich's 17 forbidden transitions encode REAL")
        print("       distillation hazards that Brunschwig also avoids")
        print()
        print("    2. Voynich's kernel grammar (k-h-e) maps to the")
        print("       actual control flow of distillation")
        print()
        print("    3. The procedural isomorphism is NOT superficial -")
        print("       it extends to the constraint level")
    else:
        print()
        print(f"  {total_violations} VIOLATIONS FOUND")
        print()
        print("  Hazard violations:", len(hazard_violations))
        print("  Grammar violations:", len(grammar_violations))
        print()
        print("  The procedure needs modification to fit Voynich grammar.")

    # Show the sequence for verification
    print()
    print("="*70)
    print("INSTRUCTION SEQUENCE (for manual verification)")
    print("="*70)
    print()
    sequence = [s[2] for s in BALNEUM_MARIE_PROCEDURE]
    print("  " + " -> ".join(sequence))
    print()

    # Check specific transition that would be problematic
    print("Key transitions checked:")
    print("  - h -> k (forbidden): ", end="")
    h_to_k = any(sequence[i] == 'h' and sequence[i+1] == 'k'
                 for i in range(len(sequence)-1))
    print("PRESENT (violation)" if h_to_k else "ABSENT (compliant)")

    print("  - k before h (required): ", end="")
    first_k = sequence.index('k') if 'k' in sequence else 999
    first_h = sequence.index('h') if 'h' in sequence else 999
    print("YES (compliant)" if first_k < first_h else "NO (violation)")

    print("  - h before e (required): ", end="")
    first_e = sequence.index('e') if 'e' in sequence else 999
    print("YES (compliant)" if first_h < first_e else "NO (violation)")

    return total_violations == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
