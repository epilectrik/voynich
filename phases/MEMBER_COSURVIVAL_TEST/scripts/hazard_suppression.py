"""Analysis 3: Hazard Class Suppression.

Track decomposable hazard classes under AZC contexts.
Verify that AZC suppresses paths through hazards by removing members, not classes.

Hazard Class Taxonomy (from MODEL_CONTEXT):
- Atomic: 7, 9, 23 (NOT affected by AZC)
- Decomposable: 8, 11, 30, 31, 33, 41 (context-tunable via MIDDLE availability)

NOTE: CLASS_COSURVIVAL_TEST found class 11's only token 'ol' has MIDDLE=None.
This test will verify whether class 11 should be reclassified as atomic.
"""
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Hazard class taxonomy from MODEL_CONTEXT
ATOMIC_HAZARD_CLASSES = [7, 9, 23]
DECOMPOSABLE_HAZARD_CLASSES = [8, 11, 30, 31, 33, 41]  # Class 11 flagged for verification


def main():
    print("=" * 70)
    print("ANALYSIS 3: HAZARD CLASS SUPPRESSION")
    print("=" * 70)

    # Load member survivor data
    data_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json'
    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data['records']
    total_contexts = len(records)
    print(f"Loaded {total_contexts} A record contexts")

    # Load class info
    map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(map_path, 'r') as f:
        class_map = json.load(f)

    class_to_tokens = class_map['class_to_tokens']
    token_to_middle = class_map['token_to_middle']

    # First verify which hazard classes are truly atomic vs decomposable
    print("\n" + "-" * 70)
    print("HAZARD CLASS ATOMICITY VERIFICATION")
    print("-" * 70)

    verified_atomic = []
    verified_decomposable = []
    misclassified = []

    all_hazard_classes = set(ATOMIC_HAZARD_CLASSES + DECOMPOSABLE_HAZARD_CLASSES)

    for cls_id in sorted(all_hazard_classes):
        tokens = class_to_tokens.get(str(cls_id), [])
        middles = [token_to_middle.get(t) for t in tokens]

        has_atomic = any(m is None for m in middles)
        all_atomic = all(m is None for m in middles)
        listed_as_atomic = cls_id in ATOMIC_HAZARD_CLASSES

        print(f"\nClass {cls_id}:")
        print(f"  Tokens: {tokens}")
        print(f"  MIDDLEs: {middles}")
        print(f"  Has atomic token: {has_atomic}")
        print(f"  All atomic: {all_atomic}")
        print(f"  Listed as atomic in MODEL_CONTEXT: {listed_as_atomic}")

        # Classify based on actual token structure
        if all_atomic:
            verified_atomic.append(cls_id)
            if not listed_as_atomic:
                misclassified.append((cls_id, "DECOMPOSABLE", "ATOMIC"))
        elif has_atomic:
            # Mixed: has both atomic and decomposable tokens
            # Classify as "semi-atomic" - can't be fully suppressed
            verified_atomic.append(cls_id)
            print(f"  -> SEMI-ATOMIC (has atomic backup)")
        else:
            verified_decomposable.append(cls_id)
            if listed_as_atomic:
                misclassified.append((cls_id, "ATOMIC", "DECOMPOSABLE"))

    print("\n" + "-" * 70)
    print("VERIFICATION RESULTS")
    print("-" * 70)
    print(f"Verified ATOMIC hazard classes: {verified_atomic}")
    print(f"Verified DECOMPOSABLE hazard classes: {verified_decomposable}")
    if misclassified:
        print(f"\n*** MISCLASSIFIED in MODEL_CONTEXT: ***")
        for cls_id, listed, actual in misclassified:
            print(f"  Class {cls_id}: listed as {listed}, actually {actual}")

    # Analyze suppression for decomposable hazard classes
    print("\n" + "-" * 70)
    print("SUPPRESSION ANALYSIS (Decomposable Hazard Classes)")
    print("-" * 70)

    results = {}

    for cls_id in verified_decomposable:
        tokens = class_to_tokens.get(str(cls_id), [])
        total_members = len(tokens)

        # Get cardinalities across all contexts
        cardinalities = [r['class_cardinalities'].get(str(cls_id), 0) for r in records]

        zero_contexts = sum(1 for c in cardinalities if c == 0)
        single_contexts = sum(1 for c in cardinalities if c == 1)
        full_contexts = sum(1 for c in cardinalities if c == total_members)

        mean_survivors = statistics.mean(cardinalities) if cardinalities else 0
        suppression_rate = 1 - (mean_survivors / total_members) if total_members > 0 else 0

        results[str(cls_id)] = {
            'total_members': total_members,
            'tokens': tokens,
            'zero_member_contexts': zero_contexts,
            'single_member_contexts': single_contexts,
            'full_member_contexts': full_contexts,
            'mean_survivors': round(mean_survivors, 2),
            'suppression_rate': round(suppression_rate, 4)
        }

        print(f"\nClass {cls_id} ({total_members} members: {tokens}):")
        print(f"  Zero members: {zero_contexts} contexts ({zero_contexts/total_contexts*100:.1f}%)")
        print(f"  Single member: {single_contexts} contexts ({single_contexts/total_contexts*100:.1f}%)")
        print(f"  Full members: {full_contexts} contexts ({full_contexts/total_contexts*100:.1f}%)")
        print(f"  Mean survivors: {mean_survivors:.2f}")
        print(f"  Suppression rate: {suppression_rate*100:.1f}%")

    # Key validation: classes with zero contexts
    print("\n" + "-" * 70)
    print("KEY VALIDATION: AZC SUPPRESSES PATHS, NOT GRAMMAR")
    print("-" * 70)

    classes_with_zero = [cls for cls, stats in results.items() if stats['zero_member_contexts'] > 0]
    if classes_with_zero:
        print(f"Decomposable hazard classes that can reach zero members: {classes_with_zero}")
        print("  -> These classes can be completely suppressed by AZC context")
        print("  -> This validates 'AZC suppresses paths through hazards by removing members'")
    else:
        print("No decomposable hazard classes reach zero members.")
        print("  -> All have at least one atomic backup token")

    # Analyze atomic hazard classes for comparison
    print("\n" + "-" * 70)
    print("ATOMIC HAZARD CLASSES (Control Group)")
    print("-" * 70)

    for cls_id in verified_atomic:
        tokens = class_to_tokens.get(str(cls_id), [])
        total_members = len(tokens)
        cardinalities = [r['class_cardinalities'].get(str(cls_id), 0) for r in records]

        # Atomic classes should NEVER have zero membership
        zero_contexts = sum(1 for c in cardinalities if c == 0)
        min_card = min(cardinalities)
        max_card = max(cardinalities)

        print(f"Class {cls_id} ({total_members} members: {tokens}):")
        print(f"  Min cardinality: {min_card}, Max: {max_card}")
        print(f"  Zero contexts: {zero_contexts}")
        if zero_contexts > 0:
            print(f"  *** WARNING: Atomic class has zero-member contexts! ***")

    # Save results
    output = {
        'metadata': {
            'total_contexts': total_contexts,
            'model_context_atomic': ATOMIC_HAZARD_CLASSES,
            'model_context_decomposable': DECOMPOSABLE_HAZARD_CLASSES
        },
        'verification': {
            'verified_atomic': verified_atomic,
            'verified_decomposable': verified_decomposable,
            'misclassified': [{'class': c, 'listed_as': l, 'actual': a} for c, l, a in misclassified]
        },
        'decomposable_analysis': results
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'hazard_suppression.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
