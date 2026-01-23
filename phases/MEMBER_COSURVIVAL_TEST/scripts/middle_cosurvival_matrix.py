"""Analysis 2: MIDDLE-MIDDLE Co-Survival Matrix.

Construct matrix where M[i,j] = count of A records where MIDDLE_i and MIDDLE_j are both legal.
Identify co-survival clusters and hard exclusions.
"""
import json
from pathlib import Path
from collections import defaultdict
import itertools

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 70)
    print("ANALYSIS 2: MIDDLE-MIDDLE CO-SURVIVAL MATRIX")
    print("=" * 70)

    # Load member survivor data
    data_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json'
    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data['records']
    total_contexts = len(records)
    print(f"Loaded {total_contexts} A record contexts")

    # Collect all unique legal MIDDLEs
    all_middles = set()
    for r in records:
        all_middles.update(r['legal_middles'])

    all_middles = sorted(all_middles)
    print(f"Unique MIDDLEs across all contexts: {len(all_middles)}")

    # Build co-survival counts
    print("\nBuilding co-survival matrix...")
    middle_to_contexts = defaultdict(set)
    for i, r in enumerate(records):
        for m in r['legal_middles']:
            middle_to_contexts[m].add(i)

    # Count co-occurrences (optimize by iterating over pairs once)
    cosurvival = defaultdict(int)
    for m, contexts in middle_to_contexts.items():
        cosurvival[(m, m)] = len(contexts)  # Self-survival

    # For pair co-survival, use context intersection
    print("Computing pair co-survival...")
    middles_list = list(all_middles)
    n_middles = len(middles_list)
    total_pairs = n_middles * (n_middles - 1) // 2
    print(f"Total MIDDLE pairs to check: {total_pairs}")

    nonzero_pairs = 0
    zero_pairs = 0

    for idx, (m1, m2) in enumerate(itertools.combinations(middles_list, 2)):
        contexts1 = middle_to_contexts[m1]
        contexts2 = middle_to_contexts[m2]
        overlap = len(contexts1 & contexts2)
        if overlap > 0:
            cosurvival[(m1, m2)] = overlap
            cosurvival[(m2, m1)] = overlap  # Symmetric
            nonzero_pairs += 1
        else:
            zero_pairs += 1

        if (idx + 1) % 100000 == 0:
            print(f"  Processed {idx + 1}/{total_pairs} pairs...")

    print(f"\nNon-zero pairs: {nonzero_pairs}")
    print(f"Zero (exclusive) pairs: {zero_pairs}")
    matrix_density = nonzero_pairs / total_pairs if total_pairs > 0 else 0
    print(f"Matrix density: {matrix_density*100:.2f}%")

    # Find always-together MIDDLEs (same context set)
    print("\n" + "-" * 70)
    print("CO-SURVIVAL CLUSTERS (MIDDLEs with identical context sets)")
    print("-" * 70)

    context_to_middles = defaultdict(list)
    for m, contexts in middle_to_contexts.items():
        key = frozenset(contexts)
        context_to_middles[key].append(m)

    clusters = []
    for contexts, middles in context_to_middles.items():
        if len(middles) > 1:
            clusters.append({
                'middles': sorted(middles),
                'context_count': len(contexts),
                'context_coverage': round(len(contexts) / total_contexts * 100, 2)
            })

    clusters.sort(key=lambda x: (-len(x['middles']), -x['context_count']))
    print(f"Found {len(clusters)} co-survival clusters (MIDDLEs that always appear together)")

    for i, c in enumerate(clusters[:10]):
        print(f"  Cluster {i+1}: {len(c['middles'])} MIDDLEs, {c['context_count']} contexts ({c['context_coverage']}%)")
        if len(c['middles']) <= 10:
            print(f"    MIDDLEs: {c['middles']}")

    # Find MIDDLEs that appear in ALL contexts (universal)
    universal_middles = [m for m, contexts in middle_to_contexts.items() if len(contexts) == total_contexts]
    print(f"\nUniversal MIDDLEs (appear in all {total_contexts} contexts): {len(universal_middles)}")
    if universal_middles:
        print(f"  {sorted(universal_middles)}")

    # Find MIDDLEs with highest exclusivity (appear in fewest contexts)
    print("\n" + "-" * 70)
    print("MOST EXCLUSIVE MIDDLEs (appear in fewest contexts)")
    print("-" * 70)

    sorted_by_rarity = sorted(middle_to_contexts.items(), key=lambda x: len(x[1]))
    for m, contexts in sorted_by_rarity[:15]:
        print(f"  {m}: {len(contexts)} contexts ({len(contexts)/total_contexts*100:.1f}%)")

    # Sample some hard exclusions
    print("\n" + "-" * 70)
    print("SAMPLE HARD EXCLUSIONS (zero co-occurrence)")
    print("-" * 70)

    hard_exclusions = []
    for m1, m2 in itertools.combinations(middles_list[:50], 2):  # Sample first 50
        if cosurvival.get((m1, m2), 0) == 0:
            hard_exclusions.append((m1, m2))

    for m1, m2 in hard_exclusions[:20]:
        c1 = len(middle_to_contexts[m1])
        c2 = len(middle_to_contexts[m2])
        print(f"  {m1} ({c1} ctx) vs {m2} ({c2} ctx) = 0 co-occurrence")

    # Load class map to project onto classes
    map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(map_path, 'r') as f:
        class_map = json.load(f)

    token_to_middle = class_map['token_to_middle']
    token_to_class = class_map['token_to_class']

    # Map MIDDLEs to classes
    middle_to_classes = defaultdict(set)
    for token, middle in token_to_middle.items():
        if middle and token in token_to_class:
            cls = token_to_class[token]
            middle_to_classes[middle].add(cls)

    # Project clusters onto classes
    print("\n" + "-" * 70)
    print("CLUSTER-TO-CLASS PROJECTION")
    print("-" * 70)

    cluster_to_classes = []
    for i, c in enumerate(clusters[:10]):
        classes = set()
        for m in c['middles']:
            classes.update(middle_to_classes.get(m, set()))
        cluster_to_classes.append({
            'cluster_id': i,
            'middle_count': len(c['middles']),
            'classes': sorted(classes),
            'context_count': c['context_count']
        })
        print(f"  Cluster {i}: {len(c['middles'])} MIDDLEs -> classes {sorted(classes)}")

    # Save results
    # Don't save full matrix (too large), save summary
    output = {
        'metadata': {
            'total_contexts': total_contexts,
            'unique_middles': len(all_middles),
            'nonzero_pairs': nonzero_pairs,
            'zero_pairs': zero_pairs,
            'matrix_density': round(matrix_density, 4),
            'cluster_count': len(clusters)
        },
        'universal_middles': sorted(universal_middles) if universal_middles else [],
        'cosurvival_clusters': clusters[:50],  # Top 50 clusters
        'cluster_to_classes': cluster_to_classes,
        'middle_context_counts': {m: len(c) for m, c in middle_to_contexts.items()},
        'sample_hard_exclusions': [{'middle_a': m1, 'middle_b': m2} for m1, m2 in hard_exclusions[:100]]
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'middle_cosurvival.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
