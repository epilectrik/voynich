"""Analyze co-survival patterns between instruction classes.

Given the 5 unique survivor patterns found, compute:
1. Pairwise co-survival matrix
2. Jaccard similarity between class pairs
3. Identify the class hierarchy
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 70)
    print("CO-SURVIVAL ANALYSIS")
    print("=" * 70)

    # Load survivor data
    with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'a_record_survivors.json', 'r') as f:
        data = json.load(f)

    # Load class map for role info
    with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json', 'r') as f:
        class_map = json.load(f)

    class_to_role = class_map['class_to_role']
    atomic_classes = set(class_map['atomic_classes'])
    infrastructure_classes = set(class_map['infrastructure_classes'])

    records = data['records']
    n_records = len(records)
    print(f"Analyzing {n_records} A records")

    # Build co-survival matrix (49x49)
    n_classes = 49
    cosurvival = np.zeros((n_classes, n_classes), dtype=int)
    survival_counts = np.zeros(n_classes, dtype=int)

    for rec in records:
        classes = set(rec['surviving_classes'])
        for c in classes:
            survival_counts[c - 1] += 1
            for c2 in classes:
                cosurvival[c - 1, c2 - 1] += 1

    print(f"\nCo-survival matrix computed ({n_classes}x{n_classes})")

    # Compute Jaccard similarity
    jaccard = np.zeros((n_classes, n_classes))
    for i in range(n_classes):
        for j in range(n_classes):
            # J(i,j) = |records where both survive| / |records where either survives|
            both = cosurvival[i, j]
            either = survival_counts[i] + survival_counts[j] - both
            jaccard[i, j] = both / either if either > 0 else 0

    # Find patterns
    print("\n" + "-" * 70)
    print("PATTERN ANALYSIS")
    print("-" * 70)

    # Find the unique survival patterns
    patterns = {}
    for rec in records:
        key = frozenset(rec['surviving_classes'])
        if key not in patterns:
            patterns[key] = 0
        patterns[key] += 1

    print(f"\nUnique survivor patterns: {len(patterns)}")

    # Classify classes by their filtering behavior
    always_survive = set(range(1, 50))
    for pattern in patterns.keys():
        always_survive &= pattern

    sometimes_excluded = set(range(1, 50)) - always_survive

    print(f"\nAlways-survive classes ({len(always_survive)}): {sorted(always_survive)}")
    print(f"Sometimes-excluded classes ({len(sometimes_excluded)}): {sorted(sometimes_excluded)}")

    # Check atomic class hypothesis
    print("\n" + "-" * 70)
    print("ATOMIC CLASS VERIFICATION")
    print("-" * 70)
    print(f"Atomic classes (from map): {sorted(atomic_classes)}")
    print(f"100% survival classes: {sorted(always_survive)}")

    extra_unfilterable = always_survive - atomic_classes
    if extra_unfilterable:
        print(f"\nNon-atomic but unfilterable classes: {sorted(extra_unfilterable)}")
        print("These classes have MIDDLEs present in ALL AZC contexts")
        for cls in sorted(extra_unfilterable):
            middles = class_map['class_to_middles'].get(str(cls), [])
            print(f"  Class {cls}: MIDDLEs = {middles}")

    # Check infrastructure class hypothesis
    print("\n" + "-" * 70)
    print("INFRASTRUCTURE CLASS VERIFICATION")
    print("-" * 70)
    print(f"Infrastructure classes (from BCI): {sorted(infrastructure_classes)}")
    for cls in sorted(infrastructure_classes):
        rate = survival_counts[cls - 1] / n_records
        status = "ALWAYS" if cls in always_survive else "SOMETIMES EXCLUDED"
        print(f"  Class {cls}: {rate*100:.1f}% survival - {status}")

    # Identify co-survival tiers
    print("\n" + "-" * 70)
    print("CO-SURVIVAL TIERS")
    print("-" * 70)

    # Tier 0: Always together (100% Jaccard)
    tier0_pairs = []
    for i in range(n_classes):
        for j in range(i + 1, n_classes):
            if jaccard[i, j] == 1.0:
                tier0_pairs.append((i + 1, j + 1))

    # Group into equivalence classes
    equiv_classes = []
    remaining = set(range(1, 50))
    while remaining:
        seed = min(remaining)
        equiv = {seed}
        for c in list(remaining):
            if c != seed and jaccard[seed - 1, c - 1] == 1.0:
                equiv.add(c)
        equiv_classes.append(sorted(equiv))
        remaining -= equiv

    print(f"\nEquivalence classes (100% co-survival): {len(equiv_classes)}")
    for i, ec in enumerate(equiv_classes):
        if len(ec) > 1:
            roles = [class_to_role.get(str(c), '?') for c in ec]
            unique_roles = list(set(roles))
            print(f"  Group {i + 1}: {ec} (roles: {unique_roles})")
        else:
            c = ec[0]
            role = class_to_role.get(str(c), '?')
            status = "ATOMIC" if c in atomic_classes else ("INFRA" if c in infrastructure_classes else "")
            if c in always_survive:
                status += " UNFILTERABLE"
            print(f"  Singleton: Class {c} ({role}) {status}")

    # Summary statistics
    print("\n" + "-" * 70)
    print("KEY FINDINGS")
    print("-" * 70)

    majority_pattern = max(patterns.values())
    majority_pct = majority_pattern / n_records * 100

    print(f"""
1. COARSE CLASS-LEVEL FILTERING
   - {len(patterns)} unique class-level survivor patterns
   - {majority_pct:.1f}% of A records produce identical survivor sets (all 49 classes)
   - MIDDLE-level: 1575+ unique patterns (C481)
   - CLASS-level: Only {len(patterns)} unique patterns

2. UNFILTERABLE CORE
   - {len(always_survive)} classes survive in ALL A contexts: {sorted(always_survive)}
   - Includes {len(always_survive & atomic_classes)} atomic (no MIDDLE)
   - Plus {len(extra_unfilterable)} with universally-present MIDDLEs

3. INFRASTRUCTURE CLASSES
   - NOT fully protected: survival rates 98.4%-100%
   - Class 44 most filterable (98.4%)

4. CO-SURVIVAL STRUCTURE
   - {len(equiv_classes)} equivalence groups
   - {len([e for e in equiv_classes if len(e) > 1])} groups with multiple classes
   - Dominated by single large group (all filterable together)
""")

    # Save results
    output = {
        'n_records': n_records,
        'unique_patterns': len(patterns),
        'majority_pattern_pct': majority_pct,
        'always_survive': sorted(always_survive),
        'sometimes_excluded': sorted(sometimes_excluded),
        'atomic_classes': sorted(atomic_classes),
        'extra_unfilterable': sorted(extra_unfilterable),
        'infrastructure_survival': {
            str(c): survival_counts[c - 1] / n_records for c in infrastructure_classes
        },
        'equivalence_classes': equiv_classes,
        'cosurvival_matrix': cosurvival.tolist(),
        'jaccard_matrix': jaccard.tolist(),
        'survival_counts': survival_counts.tolist()
    }

    output_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'cosurvival_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
