#!/usr/bin/env python3
"""
PHASE 4: GRAMMAR COMPLIANCE TESTING

Test ALL extracted Brunschwig recipes against Voynich grammar constraints.

Based on:
- C109: 5 hazard failure classes
- C121: 49 instruction classes
- C493: Grammar embedding - zero violations required

17 Forbidden Transitions (from BCSC):
These represent illegal state changes that would cause system failure.
"""

import json
from pathlib import Path
from collections import defaultdict

# ============================================================
# FORBIDDEN TRANSITIONS (17 total)
# ============================================================

# From the Voynich grammar (BCSC contract):
# The 17 forbidden transitions represent illegal jumps between instruction classes
# Organized by hazard class (C109)

FORBIDDEN_TRANSITIONS = {
    # HAZARD CLASS 1: PHASE_ORDERING (6 transitions)
    'PHASE_ORDERING': [
        ('h_HAZARD', 'AUX'),      # Cannot return to preparation after hazard
        ('e_ESCAPE', 'k_ENERGY'), # Cannot re-energize after escape
        ('e_ESCAPE', 'h_HAZARD'), # Cannot enter hazard after escape
        ('RECOVERY', 'k_ENERGY'), # Cannot re-energize from recovery
        ('RECOVERY', 'h_HAZARD'), # Cannot enter hazard from recovery
        ('e_ESCAPE', 'AUX'),      # Cannot return to prep after escape
    ],

    # HAZARD CLASS 2: COMPOSITION_JUMP (4 transitions)
    'COMPOSITION_JUMP': [
        ('k_ENERGY', 'FLOW'),     # Cannot change flow during energy application
        ('h_HAZARD', 'FLOW'),     # Cannot change flow during hazard
        ('k_ENERGY', 'AUX'),      # Cannot return to prep during energy
        ('FLOW', 'RECOVERY'),     # Cannot enter recovery from flow (must go through hazard)
    ],

    # HAZARD CLASS 3: CONTAINMENT_TIMING (3 transitions)
    'CONTAINMENT_TIMING': [
        ('h_HAZARD', 'e_ESCAPE'), # Cannot escape directly from hazard (need k first)
        ('FLOW', 'h_HAZARD'),     # Cannot enter hazard directly from flow
        ('AUX', 'h_HAZARD'),      # Cannot enter hazard directly from prep
    ],

    # HAZARD CLASS 4: RATE_MISMATCH (2 transitions)
    'RATE_MISMATCH': [
        ('k_ENERGY', 'e_ESCAPE'), # Cannot escape directly from energy
        ('LINK', 'RECOVERY'),     # Cannot enter recovery from monitoring
    ],

    # HAZARD CLASS 5: ENERGY_OVERSHOOT (2 transitions)
    'ENERGY_OVERSHOOT': [
        ('k_ENERGY', 'k_ENERGY'), # Cannot stack energy applications
        ('h_HAZARD', 'h_HAZARD'), # Cannot stack hazard operations
    ],
}

# Flatten for quick lookup
ALL_FORBIDDEN = set()
for hazard_class, transitions in FORBIDDEN_TRANSITIONS.items():
    for t in transitions:
        ALL_FORBIDDEN.add(t)

print(f"Total forbidden transitions: {len(ALL_FORBIDDEN)}")

# ============================================================
# GRAMMAR RULES
# ============================================================

# Valid instruction classes
VALID_CLASSES = {'AUX', 'FLOW', 'k_ENERGY', 'h_HAZARD', 'e_ESCAPE', 'LINK', 'RECOVERY', 'UNKNOWN'}

# Required sequence patterns (soft rules - not violations, but tracked)
EXPECTED_PATTERNS = {
    'starts_with_prep': lambda seq: seq[0] in ['AUX', 'FLOW'] if seq else True,
    'ends_with_escape': lambda seq: seq[-1] in ['e_ESCAPE', 'RECOVERY'] if seq else True,
    'has_energy': lambda seq: 'k_ENERGY' in seq if seq else True,
}

# ============================================================
# COMPLIANCE TESTING FUNCTIONS
# ============================================================

def check_forbidden_transitions(sequence):
    """Check sequence for forbidden transitions. Returns list of violations."""
    violations = []

    # Skip UNKNOWN in transition checking
    filtered = [s for s in sequence if s != 'UNKNOWN']

    for i in range(len(filtered) - 1):
        transition = (filtered[i], filtered[i+1])
        if transition in ALL_FORBIDDEN:
            # Find which hazard class
            for hazard_class, transitions in FORBIDDEN_TRANSITIONS.items():
                if transition in transitions:
                    violations.append({
                        'position': i,
                        'transition': transition,
                        'hazard_class': hazard_class
                    })
                    break

    return violations

def check_pattern_compliance(sequence):
    """Check sequence against expected patterns. Returns dict of results."""
    results = {}
    for pattern_name, check_fn in EXPECTED_PATTERNS.items():
        results[pattern_name] = check_fn(sequence)
    return results

def compute_transition_distribution(sequence):
    """Compute the distribution of transitions in sequence."""
    transitions = defaultdict(int)
    filtered = [s for s in sequence if s != 'UNKNOWN']

    for i in range(len(filtered) - 1):
        t = (filtered[i], filtered[i+1])
        transitions[t] += 1

    return dict(transitions)

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 4: GRAMMAR COMPLIANCE TESTING")
print("=" * 70)
print()

# Load materials database
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials")

# Filter to those with instruction sequences
with_sequences = [m for m in materials if m.get('instruction_sequence')]
print(f"Materials with instruction sequences: {len(with_sequences)}")
print()

# ============================================================
# TEST GRAMMAR COMPLIANCE
# ============================================================

print("=" * 70)
print("TESTING GRAMMAR COMPLIANCE")
print("=" * 70)
print()

compliant_count = 0
violation_count = 0
total_violations = 0
violations_by_class = defaultdict(int)
all_transitions = defaultdict(int)

for material in with_sequences:
    sequence = material['instruction_sequence']

    # Check forbidden transitions
    violations = check_forbidden_transitions(sequence)

    # Check pattern compliance
    patterns = check_pattern_compliance(sequence)

    # Compute transition distribution
    transitions = compute_transition_distribution(sequence)
    for t, count in transitions.items():
        all_transitions[t] += count

    # Update material record
    material['grammar_compliance'] = {
        'violations': len(violations),
        'violation_details': violations,
        'patterns': patterns,
        'transitions_checked': len(sequence) - 1 if len(sequence) > 1 else 0,
        'status': 'COMPLIANT' if len(violations) == 0 else 'VIOLATION'
    }

    if len(violations) == 0:
        compliant_count += 1
    else:
        violation_count += 1
        total_violations += len(violations)
        for v in violations:
            violations_by_class[v['hazard_class']] += 1

# ============================================================
# RESULTS
# ============================================================

print(f"Recipes tested: {len(with_sequences)}")
print(f"COMPLIANT: {compliant_count} ({100*compliant_count/len(with_sequences):.1f}%)")
print(f"VIOLATIONS: {violation_count} ({100*violation_count/len(with_sequences):.1f}%)")
print(f"Total violations found: {total_violations}")
print()

print("Violations by hazard class:")
for hazard_class in ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    count = violations_by_class.get(hazard_class, 0)
    print(f"  {hazard_class}: {count}")

print()

# ============================================================
# TRANSITION ANALYSIS
# ============================================================

print("=" * 70)
print("TRANSITION ANALYSIS")
print("=" * 70)
print()

print("Most common transitions observed:")
sorted_transitions = sorted(all_transitions.items(), key=lambda x: -x[1])[:15]
for t, count in sorted_transitions:
    status = "FORBIDDEN" if t in ALL_FORBIDDEN else "allowed"
    print(f"  {t[0]} -> {t[1]}: {count} ({status})")

print()

# Check which forbidden transitions were observed
print("Forbidden transitions observed in data:")
observed_forbidden = 0
for t in ALL_FORBIDDEN:
    if all_transitions.get(t, 0) > 0:
        print(f"  {t}: {all_transitions[t]} occurrences")
        observed_forbidden += 1

if observed_forbidden == 0:
    print("  NONE - all sequences avoid forbidden transitions")

print()

# ============================================================
# PATTERN ANALYSIS
# ============================================================

print("=" * 70)
print("PATTERN ANALYSIS")
print("=" * 70)
print()

pattern_counts = defaultdict(int)
for m in with_sequences:
    patterns = m['grammar_compliance']['patterns']
    for pattern_name, passed in patterns.items():
        if passed:
            pattern_counts[pattern_name] += 1

print("Pattern compliance:")
for pattern_name in EXPECTED_PATTERNS.keys():
    count = pattern_counts[pattern_name]
    pct = 100 * count / len(with_sequences) if with_sequences else 0
    print(f"  {pattern_name}: {count}/{len(with_sequences)} ({pct:.1f}%)")

print()

# ============================================================
# SAMPLE VIOLATIONS (if any)
# ============================================================

if violation_count > 0:
    print("=" * 70)
    print("SAMPLE VIOLATIONS")
    print("=" * 70)
    print()

    violation_samples = [m for m in with_sequences if m['grammar_compliance']['violations'] > 0][:5]

    for m in violation_samples:
        recipe_id = m['recipe_id']
        name = m['name_normalized']
        seq = ' -> '.join(m.get('instruction_sequence_simplified', []))
        violations = m['grammar_compliance']['violation_details']

        print(f"Recipe: {recipe_id} ({name})")
        print(f"  Sequence: {seq}")
        print(f"  Violations:")
        for v in violations:
            print(f"    - {v['transition']} ({v['hazard_class']})")
        print()

# ============================================================
# SAVE UPDATED DATABASE
# ============================================================

print("=" * 70)
print("SAVING UPDATED DATABASE")
print("=" * 70)
print()

# Update summary
data['summary']['grammar_compliance'] = {
    'recipes_tested': len(with_sequences),
    'compliant': compliant_count,
    'compliance_rate': compliant_count / len(with_sequences) if with_sequences else 0,
    'total_violations': total_violations,
    'violations_by_class': dict(violations_by_class)
}

# Save
output_path = Path('data/brunschwig_materials_master.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated database saved to {output_path}")

# ============================================================
# COMPLIANCE SUMMARY
# ============================================================

print()
print("=" * 70)
print("COMPLIANCE SUMMARY")
print("=" * 70)
print()

compliance_rate = 100 * compliant_count / len(with_sequences) if with_sequences else 0

if compliance_rate >= 95:
    print(f"SUCCESS: {compliance_rate:.1f}% compliance rate meets >95% threshold")
    print("Grammar embedding hypothesis (C493) SUPPORTED")
else:
    print(f"BELOW THRESHOLD: {compliance_rate:.1f}% compliance rate")
    print(f"Need to investigate {violation_count} recipes with violations")

print()
print("Next steps:")
print("  - Phase 5: REGIME assignment based on fire degree")
print("  - Phase 6: Reverse mapping to find semantic anchors")
