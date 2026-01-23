"""Analysis 1: Intra-Class Pruning Profiles.

For each class, analyze how many members survive per A context.
Identify classes that collapse to single realization.
"""
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def classify_pattern(total, mean, single_count, zero_count, total_contexts):
    """Classify collapse pattern based on survival statistics."""
    survival_rate = (total_contexts - zero_count) / total_contexts
    single_rate = single_count / total_contexts

    if total == 1:
        return "SINGLETON"  # Only 1 member, can't collapse further
    if zero_count == 0 and single_count == 0:
        return "UNFILTERABLE"  # Always full membership
    if single_rate > 0.5:
        return "FORCED_SINGLE"  # Usually collapses to 1
    if mean < total * 0.5:
        return "HEAVILY_PRUNED"
    if mean > total * 0.9:
        return "LIGHTLY_PRUNED"
    return "MODERATELY_PRUNED"


def main():
    print("=" * 70)
    print("ANALYSIS 1: INTRA-CLASS PRUNING PROFILES")
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
    class_to_role = class_map['class_to_role']
    total_classes = len(class_to_tokens)
    print(f"Analyzing {total_classes} classes")

    # Compute per-class statistics
    results = {}

    for cls_id in sorted(class_to_tokens.keys(), key=int):
        total_members = len(class_to_tokens[cls_id])
        role = class_to_role.get(cls_id, 'UNKNOWN')

        # Get cardinalities across all contexts
        cardinalities = [r['class_cardinalities'].get(str(cls_id), 0) for r in records]

        # Compute distribution
        distribution = defaultdict(int)
        for c in cardinalities:
            distribution[c] += 1

        # Statistics
        mean_survivors = statistics.mean(cardinalities)
        median_survivors = statistics.median(cardinalities)
        min_survivors = min(cardinalities)
        max_survivors = max(cardinalities)

        zero_count = distribution.get(0, 0)
        single_count = distribution.get(1, 0)
        full_count = distribution.get(total_members, 0)

        pattern = classify_pattern(total_members, mean_survivors, single_count, zero_count, total_contexts)

        results[cls_id] = {
            'total_members': total_members,
            'role': role,
            'survival_distribution': dict(sorted(distribution.items())),
            'mean_survivors': round(mean_survivors, 2),
            'median_survivors': median_survivors,
            'min_survivors': min_survivors,
            'max_survivors': max_survivors,
            'zero_contexts': zero_count,
            'single_realization_contexts': single_count,
            'full_membership_contexts': full_count,
            'collapse_pattern': pattern
        }

    # Summary by pattern
    print("\n" + "-" * 70)
    print("COLLAPSE PATTERN SUMMARY")
    print("-" * 70)

    pattern_counts = defaultdict(list)
    for cls_id, stats in results.items():
        pattern_counts[stats['collapse_pattern']].append(cls_id)

    for pattern in sorted(pattern_counts.keys()):
        classes = pattern_counts[pattern]
        print(f"\n{pattern} ({len(classes)} classes):")
        for cls_id in classes:
            stats = results[cls_id]
            print(f"  Class {cls_id:>2}: {stats['total_members']:>2} members, "
                  f"mean={stats['mean_survivors']:.1f}, "
                  f"zero={stats['zero_contexts']}, "
                  f"single={stats['single_realization_contexts']}, "
                  f"full={stats['full_membership_contexts']}")

    # Detailed output for interesting classes
    print("\n" + "-" * 70)
    print("CLASSES WITH SINGLE-REALIZATION CONTEXTS")
    print("-" * 70)

    for cls_id in sorted(results.keys(), key=int):
        stats = results[cls_id]
        if stats['single_realization_contexts'] > 0 and stats['total_members'] > 1:
            print(f"\nClass {cls_id} ({stats['role']}):")
            print(f"  Total members: {stats['total_members']}")
            print(f"  Contexts with single realization: {stats['single_realization_contexts']} ({stats['single_realization_contexts']/total_contexts*100:.1f}%)")
            print(f"  Distribution: {stats['survival_distribution']}")

    # Compute effective redundancy exploitation (C411)
    print("\n" + "-" * 70)
    print("C411 REDUNDANCY EXPLOITATION")
    print("-" * 70)

    total_theoretical_capacity = sum(s['total_members'] for s in results.values())
    mean_effective_capacity = sum(s['mean_survivors'] for s in results.values())
    exploitation_ratio = 1 - (mean_effective_capacity / total_theoretical_capacity)

    print(f"Total theoretical capacity: {total_theoretical_capacity} members across {total_classes} classes")
    print(f"Mean effective capacity per context: {mean_effective_capacity:.1f} members")
    print(f"Redundancy exploitation ratio: {exploitation_ratio*100:.1f}%")
    print(f"  (C411 predicts ~40% reducibility)")

    # Save results
    output = {
        'metadata': {
            'total_contexts': total_contexts,
            'total_classes': total_classes,
            'total_theoretical_capacity': total_theoretical_capacity,
            'mean_effective_capacity': round(mean_effective_capacity, 2),
            'redundancy_exploitation_ratio': round(exploitation_ratio, 4),
        },
        'pattern_summary': {pattern: classes for pattern, classes in pattern_counts.items()},
        'class_profiles': results
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'intraclass_pruning.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
