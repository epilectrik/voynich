#!/usr/bin/env python3
"""
CROSS-TYPE MIDDLE PROPERTY ANALYSIS

Question: Do MIDDLEs encode material PROPERTIES that cross product type boundaries?
          Or are MIDDLEs strictly type-specific?

CAREFUL FRAMING (avoiding semantic drift):
- We do NOT assert MIDDLEs mean "aromatic" or "medicinal"
- We look for STRUCTURAL patterns: shared vs exclusive, clustering
- We let patterns speak, then consider what they might structurally represent

Hypotheses:
H1: MIDDLEs are TYPE-LOCKED
    - Each type has its own MIDDLE vocabulary
    - Cross-type sharing is minimal
    - Interpretation: MIDDLEs encode type-specific procedures

H2: MIDDLEs encode CROSS-CUTTING PROPERTIES
    - Some MIDDLEs appear across types
    - These might encode shared material properties
    - Interpretation: MIDDLEs encode properties independent of product type

H3: MIDDLEs show HIERARCHICAL STRUCTURE
    - Some universal (appear in all types)
    - Some type-specific
    - Some sub-class markers (within-type clustering)
    - Interpretation: Multi-level encoding
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# LOAD DATA
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def load_all_data():
    """Load MIDDLE tokens per folio and classifications."""
    folio_middles = defaultdict(Counter)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio][middle] += 1

    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    classifications = data['a_folio_classifications']

    return folio_middles, classifications

# ============================================================
# ANALYSIS 1: Cross-Type MIDDLE Distribution
# ============================================================

def analyze_cross_type_distribution(folio_middles, classifications):
    """Which MIDDLEs appear in which product types?"""

    # Build type -> set of MIDDLEs
    type_middles = defaultdict(set)
    for folio, ptype in classifications.items():
        if folio in folio_middles:
            type_middles[ptype].update(folio_middles[folio].keys())

    # Count how many types each MIDDLE appears in
    all_middles = set()
    for middles in type_middles.values():
        all_middles.update(middles)

    middle_type_count = {}
    middle_types = {}
    for m in all_middles:
        types_with_m = [t for t, middles in type_middles.items() if m in middles]
        middle_type_count[m] = len(types_with_m)
        middle_types[m] = sorted(types_with_m)

    return type_middles, middle_type_count, middle_types

# ============================================================
# ANALYSIS 2: Within-Type Clustering
# ============================================================

def analyze_within_type_clustering(folio_middles, classifications, ptype):
    """Look for sub-clusters within a product type."""

    type_folios = [f for f, t in classifications.items() if t == ptype and f in folio_middles]

    if len(type_folios) < 2:
        return None

    # Build folio -> MIDDLE set
    folio_middle_sets = {f: set(folio_middles[f].keys()) for f in type_folios}

    # Pairwise Jaccard
    overlaps = []
    for i, f1 in enumerate(type_folios):
        for f2 in type_folios[i+1:]:
            s1 = folio_middle_sets[f1]
            s2 = folio_middle_sets[f2]
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            jaccard = intersection / union if union > 0 else 0
            overlaps.append((f1, f2, jaccard, intersection))

    # Sort by Jaccard
    overlaps.sort(key=lambda x: -x[2])

    # Find clusters (simple greedy)
    clusters = []
    remaining = set(type_folios)

    while remaining and overlaps:
        # Find highest overlap pair from remaining
        best = None
        for f1, f2, jacc, inter in overlaps:
            if f1 in remaining and f2 in remaining:
                best = (f1, f2, jacc, inter)
                break

        if best is None or best[2] < 0.1:  # Minimum threshold
            break

        cluster = {best[0], best[1]}
        remaining.discard(best[0])
        remaining.discard(best[1])
        clusters.append(cluster)

    # Add singletons
    for f in remaining:
        clusters.append({f})

    return {
        'folios': type_folios,
        'overlaps': overlaps[:10],  # Top 10
        'clusters': [sorted(c) for c in clusters],
        'n_clusters': len([c for c in clusters if len(c) > 1])
    }

# ============================================================
# ANALYSIS 3: Property Candidates
# ============================================================

def identify_property_candidates(type_middles, middle_type_count, middle_types):
    """
    Identify MIDDLEs that might encode cross-cutting properties.

    Property candidates: appear in 2+ types (not type-locked)
    Type-specific: appear in exactly 1 type
    Universal: appear in all types
    """

    n_types = len(type_middles)

    universal = [m for m, c in middle_type_count.items() if c == n_types]
    cross_cutting = [m for m, c in middle_type_count.items() if 2 <= c < n_types]
    type_specific = [m for m, c in middle_type_count.items() if c == 1]

    # Which type combinations share MIDDLEs?
    type_pair_sharing = defaultdict(list)
    for m, types in middle_types.items():
        if len(types) == 2:
            pair = tuple(sorted(types))
            type_pair_sharing[pair].append(m)

    return {
        'universal': universal,
        'cross_cutting': cross_cutting,
        'type_specific': type_specific,
        'type_pair_sharing': dict(type_pair_sharing)
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("CROSS-TYPE MIDDLE PROPERTY ANALYSIS")
    print("=" * 70)
    print()
    print("Question: Do MIDDLEs encode cross-cutting material PROPERTIES,")
    print("          or are they strictly type-specific?")
    print()
    print("NOTE: We describe structural PATTERNS, not semantic meanings.")
    print()

    # Load data
    folio_middles, classifications = load_all_data()

    # Count folios per type
    type_counts = Counter(classifications.values())
    print("Product type distribution:")
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {ptype}: {count} A folios")
    print()

    # Analysis 1: Cross-type distribution
    print("=" * 70)
    print("ANALYSIS 1: CROSS-TYPE MIDDLE DISTRIBUTION")
    print("=" * 70)
    print()

    type_middles, middle_type_count, middle_types = analyze_cross_type_distribution(
        folio_middles, classifications
    )

    # Summary
    total_middles = len(middle_type_count)
    by_count = Counter(middle_type_count.values())

    print(f"Total unique MIDDLEs across all types: {total_middles}")
    print()
    print("Distribution by type coverage:")
    for n_types in sorted(by_count.keys()):
        count = by_count[n_types]
        pct = 100 * count / total_middles
        label = {1: "type-specific", 2: "shared by 2", 3: "shared by 3", 4: "universal"}
        print(f"  Appear in {n_types} type(s): {count} ({pct:.1f}%) - {label.get(n_types, '')}")
    print()

    # Analysis 2: Property candidates
    print("=" * 70)
    print("ANALYSIS 2: PROPERTY CANDIDATE IDENTIFICATION")
    print("=" * 70)
    print()

    candidates = identify_property_candidates(type_middles, middle_type_count, middle_types)

    print(f"Universal MIDDLEs (all 4 types): {len(candidates['universal'])}")
    if candidates['universal']:
        print(f"  Examples: {candidates['universal'][:15]}")
    print()

    print(f"Cross-cutting MIDDLEs (2-3 types): {len(candidates['cross_cutting'])}")
    if candidates['cross_cutting']:
        print(f"  Examples: {candidates['cross_cutting'][:15]}")
    print()

    print(f"Type-specific MIDDLEs (1 type only): {len(candidates['type_specific'])}")
    print()

    # Type pair sharing
    print("Type pair MIDDLE sharing:")
    for pair, middles in sorted(candidates['type_pair_sharing'].items(),
                                 key=lambda x: -len(x[1])):
        print(f"  {pair[0]} + {pair[1]}: {len(middles)} shared MIDDLEs")
        if len(middles) <= 5:
            print(f"    {middles}")
    print()

    # Analysis 3: Within-type clustering
    print("=" * 70)
    print("ANALYSIS 3: WITHIN-TYPE CLUSTERING")
    print("=" * 70)
    print()

    clustering_results = {}
    for ptype in sorted(type_middles.keys()):
        result = analyze_within_type_clustering(folio_middles, classifications, ptype)
        clustering_results[ptype] = result

        if result:
            print(f"{ptype}: {len(result['folios'])} folios")
            print(f"  Clusters found: {result['n_clusters']}")

            if result['clusters']:
                for i, cluster in enumerate(result['clusters'][:3]):
                    if len(cluster) > 1:
                        print(f"    Cluster {i+1}: {cluster}")

            if result['overlaps']:
                top = result['overlaps'][0]
                print(f"  Highest Jaccard: {top[0]} + {top[1]} = {top[2]:.2f}")
            print()

    # Analysis 4: Hypothesis testing
    print("=" * 70)
    print("HYPOTHESIS TESTING")
    print("=" * 70)
    print()

    # H1: Type-locked (most MIDDLEs type-specific)
    pct_type_specific = 100 * len(candidates['type_specific']) / total_middles

    # H2: Cross-cutting (significant sharing across types)
    pct_shared = 100 * (len(candidates['universal']) + len(candidates['cross_cutting'])) / total_middles

    # H3: Hierarchical (all three levels present)
    has_universal = len(candidates['universal']) > 10
    has_cross = len(candidates['cross_cutting']) > 50
    has_specific = len(candidates['type_specific']) > 100

    print("H1: TYPE-LOCKED (MIDDLEs specific to product types)")
    print(f"  Type-specific MIDDLEs: {pct_type_specific:.1f}%")
    h1_support = pct_type_specific > 70
    print(f"  Support: {'STRONG' if h1_support else 'WEAK'}")
    print()

    print("H2: CROSS-CUTTING (MIDDLEs encode shared properties)")
    print(f"  Shared MIDDLEs: {pct_shared:.1f}%")
    h2_support = pct_shared > 20
    print(f"  Support: {'STRONG' if h2_support else 'WEAK'}")
    print()

    print("H3: HIERARCHICAL (multi-level structure)")
    print(f"  Has universal layer: {has_universal} ({len(candidates['universal'])})")
    print(f"  Has cross-cutting layer: {has_cross} ({len(candidates['cross_cutting'])})")
    print(f"  Has type-specific layer: {has_specific} ({len(candidates['type_specific'])})")
    h3_support = has_universal and has_cross and has_specific
    print(f"  Support: {'STRONG' if h3_support else 'WEAK'}")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if h3_support:
        verdict = "HIERARCHICAL"
        interpretation = """MIDDLEs show multi-level structure:
  - Universal MIDDLEs: appear in ALL product types (procedural primitives?)
  - Cross-cutting MIDDLEs: shared by 2-3 types (material PROPERTY markers?)
  - Type-specific MIDDLEs: unique to one type (type-locked procedures?)

This suggests MIDDLEs encode BOTH:
  1. Common procedural vocabulary (universal)
  2. Shared material properties (cross-cutting)
  3. Type-specific configurations (unique)"""
    elif h1_support:
        verdict = "TYPE-LOCKED"
        interpretation = """MIDDLEs are primarily type-specific.
Each product type has its own procedural vocabulary.
Little cross-cutting property encoding."""
    elif h2_support:
        verdict = "PROPERTY-BASED"
        interpretation = """MIDDLEs primarily encode cross-cutting properties.
Material properties matter more than product type.
Type differences are secondary."""
    else:
        verdict = "MIXED"
        interpretation = "No clear pattern. MIDDLEs show mixed behavior."

    print(f"Verdict: {verdict}")
    print()
    print(f"Interpretation:")
    print(interpretation)
    print()

    # Structural implications
    print("=" * 70)
    print("STRUCTURAL IMPLICATIONS (no semantic labels)")
    print("=" * 70)
    print()

    print("What the patterns suggest about A register specification:")
    print()

    if verdict == "HIERARCHICAL":
        print("1. A registers use a SHARED CORE vocabulary (universal MIDDLEs)")
        print("   - These may encode fundamental procedural operations")
        print("   - Same primitives reused across all product types")
        print()
        print("2. A registers use PROPERTY MARKERS (cross-cutting MIDDLEs)")
        print("   - These may encode material characteristics")
        print("   - E.g., a property shared by rose water AND rosemary oil")
        print("   - Not 'aromatic' but 'requires X treatment'")
        print()
        print("3. A registers use TYPE-SPECIFIC vocabulary (unique MIDDLEs)")
        print("   - These may encode type-locked procedures")
        print("   - E.g., oil extraction steps not used for waters")

    print()

    # Save results
    output = {
        'test': 'CROSS_TYPE_MIDDLE_ANALYSIS',
        'total_middles': total_middles,
        'distribution': {
            'universal': len(candidates['universal']),
            'cross_cutting': len(candidates['cross_cutting']),
            'type_specific': len(candidates['type_specific']),
        },
        'percentages': {
            'type_specific': pct_type_specific,
            'shared': pct_shared,
        },
        'hypothesis_support': {
            'H1_type_locked': h1_support,
            'H2_cross_cutting': h2_support,
            'H3_hierarchical': h3_support,
        },
        'type_pair_sharing': {
            f"{p[0]}+{p[1]}": len(m) for p, m in candidates['type_pair_sharing'].items()
        },
        'clustering': {
            ptype: result['n_clusters'] if result else 0
            for ptype, result in clustering_results.items()
        },
        'verdict': verdict,
        'interpretation': interpretation.replace('\n', ' ').strip()
    }

    with open('results/cross_type_middle_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/cross_type_middle_analysis.json")

if __name__ == '__main__':
    main()
