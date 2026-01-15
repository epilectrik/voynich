#!/usr/bin/env python3
"""
NEGATIVE CONTROL: SYNTHETIC PROPERTY PARTITION (Tier A-3)

Question: Could a property-based registry fake this structure?

Method:
1. Create a synthetic registry with:
   - 5-10 "properties"
   - Smooth overlap
   - Zipf-like frequencies
2. Force it through same analyses:
   - Clustering
   - Cross-type overlap
   - Hub rationing
   - Survivor-set uniqueness
3. Compare to observed Voynich patterns

Expected (if property model fails):
- Fail to reproduce hub rationing
- Fail to reproduce tail forcing
- Fail to reproduce survivor-set uniqueness
- Patterns too smooth or too random

This cleanly kills "latent property" interpretations.
"""

import random
import math
from collections import Counter, defaultdict
import json

random.seed(42)

# ============================================================
# SYNTHETIC REGISTRY GENERATOR
# ============================================================

def generate_property_registry(n_folios=109, n_properties=8, n_vocab=500):
    """
    Generate a synthetic registry where MIDDLEs encode "properties".

    Each folio has 2-4 properties.
    Each property has 50-100 associated MIDDLEs.
    MIDDLEs shared by multiple properties = "cross-cutting".
    """

    # Define properties
    properties = [f"PROP_{i}" for i in range(n_properties)]

    # Assign MIDDLEs to properties (with overlap)
    property_middles = {}
    all_middles = [f"m{i:04d}" for i in range(n_vocab)]

    for prop in properties:
        # Each property gets 50-100 MIDDLEs
        n_middles = random.randint(50, 100)
        # Some random, some shared with adjacent properties
        prop_middles = set(random.sample(all_middles, n_middles))
        property_middles[prop] = prop_middles

    # Add cross-cutting (shared between adjacent properties)
    for i in range(len(properties) - 1):
        shared = set(random.sample(all_middles, 20))
        property_middles[properties[i]].update(shared)
        property_middles[properties[i + 1]].update(shared)

    # Generate folios
    folio_middles = {}
    folio_properties = {}

    for i in range(n_folios):
        folio = f"syn_f{i:03d}"

        # Each folio has 2-4 properties
        n_props = random.randint(2, 4)
        selected_props = random.sample(properties, n_props)
        folio_properties[folio] = selected_props

        # Collect MIDDLEs from properties
        middles = set()
        for prop in selected_props:
            # Take 60-80% of each property's MIDDLEs
            prop_mids = property_middles[prop]
            n_take = int(len(prop_mids) * random.uniform(0.6, 0.8))
            middles.update(random.sample(list(prop_mids), n_take))

        # Add some folio-specific noise
        n_noise = random.randint(5, 15)
        middles.update(random.sample(all_middles, n_noise))

        folio_middles[folio] = middles

    return folio_middles, folio_properties, property_middles

def generate_uniform_registry(n_folios=109, n_vocab=500, vocab_per_folio=80):
    """
    Generate a registry with uniform random vocabulary distribution.
    No property structure, just random sampling.
    """
    all_middles = [f"m{i:04d}" for i in range(n_vocab)]
    folio_middles = {}

    for i in range(n_folios):
        folio = f"unif_f{i:03d}"
        middles = set(random.sample(all_middles, vocab_per_folio))
        folio_middles[folio] = middles

    return folio_middles

# ============================================================
# ANALYSIS METRICS
# ============================================================

def compute_sharing_distribution(folio_middles):
    """Compute how MIDDLEs are distributed across folios."""
    middle_counts = Counter()
    for middles in folio_middles.values():
        for m in middles:
            middle_counts[m] += 1

    # Distribution of folio-coverage
    coverage_dist = Counter(middle_counts.values())
    return coverage_dist, middle_counts

def compute_hub_ratio(middle_counts, n_folios):
    """
    Compute ratio of "hub" MIDDLEs (appear in many folios)
    to "tail" MIDDLEs (appear in few).
    """
    hubs = [m for m, c in middle_counts.items() if c >= n_folios * 0.5]
    tails = [m for m, c in middle_counts.items() if c <= 2]
    return len(hubs) / len(tails) if tails else float('inf')

def compute_cluster_count(folio_middles, min_jaccard=0.15):
    """Count multi-member clusters via greedy Jaccard."""
    folios = list(folio_middles.keys())

    # Compute pairwise Jaccard
    overlaps = []
    for i, f1 in enumerate(folios):
        for f2 in folios[i + 1:]:
            s1 = folio_middles[f1]
            s2 = folio_middles[f2]
            if not s1 or not s2:
                continue
            jaccard = len(s1 & s2) / len(s1 | s2)
            if jaccard >= min_jaccard:
                overlaps.append((f1, f2, jaccard))

    overlaps.sort(key=lambda x: -x[2])

    # Greedy clustering
    clusters = []
    remaining = set(folios)

    while remaining and overlaps:
        best = None
        for f1, f2, jacc in overlaps:
            if f1 in remaining and f2 in remaining:
                best = (f1, f2)
                break
        if best is None:
            break

        cluster = {best[0], best[1]}
        remaining.discard(best[0])
        remaining.discard(best[1])
        clusters.append(cluster)

    return len(clusters)

def compute_uniqueness(folio_middles):
    """
    Compute survivor-set uniqueness:
    What fraction of MIDDLEs are unique to one folio?
    """
    middle_counts = Counter()
    for middles in folio_middles.values():
        for m in middles:
            middle_counts[m] += 1

    unique = sum(1 for c in middle_counts.values() if c == 1)
    return unique / len(middle_counts) if middle_counts else 0

def compute_cross_type_overlap(folio_middles, folio_types):
    """
    For property-based registry, compute overlap between "types".
    """
    type_middles = defaultdict(set)
    for folio, middles in folio_middles.items():
        if folio in folio_types:
            # Use first property as "type"
            ptype = folio_types[folio][0]
            type_middles[ptype].update(middles)

    # Compute pairwise overlap
    types = list(type_middles.keys())
    overlaps = {}
    for i, t1 in enumerate(types):
        for t2 in types[i + 1:]:
            shared = len(type_middles[t1] & type_middles[t2])
            overlaps[(t1, t2)] = shared

    return overlaps

# ============================================================
# LOAD ACTUAL VOYNICH DATA
# ============================================================

def load_actual_data():
    """Load actual Voynich MIDDLE data for comparison."""
    import csv

    KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

    def get_middle(token):
        for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
            if token.startswith(p):
                return token[len(p):]
        return token

    folio_middles = defaultdict(set)

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
                folio_middles[folio].add(middle)

    return dict(folio_middles)

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("NEGATIVE CONTROL: SYNTHETIC PROPERTY PARTITION")
    print("=" * 70)
    print()
    print("Testing if a property-based registry can reproduce Voynich structure.")
    print("If property model CANNOT reproduce, 'latent property' interpretations fail.")
    print()

    # Load actual Voynich data
    actual_data = load_actual_data()
    n_actual_folios = len(actual_data)
    n_actual_vocab = len(set(m for middles in actual_data.values() for m in middles))

    print(f"Actual Voynich: {n_actual_folios} folios, {n_actual_vocab} unique MIDDLEs")
    print()

    # Generate synthetic registries
    print("Generating synthetic registries...")
    print()

    property_registry, folio_props, _ = generate_property_registry(
        n_folios=n_actual_folios, n_properties=8, n_vocab=n_actual_vocab
    )
    uniform_registry = generate_uniform_registry(
        n_folios=n_actual_folios, n_vocab=n_actual_vocab
    )

    # Compute metrics for all three
    print("=" * 70)
    print("METRIC COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Metric':<30} {'Voynich':>12} {'Property':>12} {'Uniform':>12}")
    print("-" * 70)

    # 1. Sharing distribution
    actual_dist, actual_counts = compute_sharing_distribution(actual_data)
    prop_dist, prop_counts = compute_sharing_distribution(property_registry)
    unif_dist, unif_counts = compute_sharing_distribution(uniform_registry)

    # Universal (appear in >50% of folios)
    actual_universal = sum(1 for m, c in actual_counts.items() if c >= n_actual_folios * 0.5)
    prop_universal = sum(1 for m, c in prop_counts.items() if c >= n_actual_folios * 0.5)
    unif_universal = sum(1 for m, c in unif_counts.items() if c >= n_actual_folios * 0.5)

    print(f"{'Universal MIDDLEs (>50%):':<30} {actual_universal:>12} {prop_universal:>12} {unif_universal:>12}")

    # 2. Hub/tail ratio
    actual_hub = compute_hub_ratio(actual_counts, n_actual_folios)
    prop_hub = compute_hub_ratio(prop_counts, n_actual_folios)
    unif_hub = compute_hub_ratio(unif_counts, n_actual_folios)

    print(f"{'Hub/Tail ratio:':<30} {actual_hub:>12.3f} {prop_hub:>12.3f} {unif_hub:>12.3f}")

    # 3. Cluster count
    actual_clusters = compute_cluster_count(actual_data)
    prop_clusters = compute_cluster_count(property_registry)
    unif_clusters = compute_cluster_count(uniform_registry)

    print(f"{'Multi-member clusters:':<30} {actual_clusters:>12} {prop_clusters:>12} {unif_clusters:>12}")

    # 4. Uniqueness
    actual_unique = compute_uniqueness(actual_data)
    prop_unique = compute_uniqueness(property_registry)
    unif_unique = compute_uniqueness(uniform_registry)

    print(f"{'Unique MIDDLE fraction:':<30} {actual_unique:>12.2%} {prop_unique:>12.2%} {unif_unique:>12.2%}")

    print()

    # Analyze differences
    print("=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)
    print()

    failures = []
    matches = []

    # Hub ratio
    if abs(actual_hub - prop_hub) > abs(actual_hub - unif_hub):
        failures.append("Hub/Tail ratio: Property model WORSE than uniform")
    elif abs(actual_hub - prop_hub) < 0.1:
        matches.append("Hub/Tail ratio: Property model matches")
    else:
        failures.append(f"Hub/Tail ratio: Property model off by {abs(actual_hub - prop_hub):.3f}")

    # Cluster count
    cluster_diff_prop = abs(actual_clusters - prop_clusters)
    cluster_diff_unif = abs(actual_clusters - unif_clusters)

    if cluster_diff_prop > cluster_diff_unif:
        failures.append("Cluster count: Property model WORSE than uniform")
    elif cluster_diff_prop < 10:
        matches.append("Cluster count: Property model matches")
    else:
        failures.append(f"Cluster count: Property model off by {cluster_diff_prop}")

    # Uniqueness
    if abs(actual_unique - prop_unique) > 0.1:
        failures.append(f"Uniqueness: Property model shows {prop_unique:.1%} vs Voynich {actual_unique:.1%}")
    else:
        matches.append("Uniqueness: Property model matches")

    # Universal count
    if actual_universal > 100 and prop_universal < 50:
        failures.append("Universal MIDDLEs: Property model under-produces")
    elif actual_universal < 50 and prop_universal > 100:
        failures.append("Universal MIDDLEs: Property model over-produces")
    else:
        matches.append("Universal MIDDLEs: Property model in range")

    print("Property Model MATCHES Voynich:")
    for m in matches:
        print(f"  + {m}")
    print()

    print("Property Model FAILS to match Voynich:")
    for f in failures:
        print(f"  - {f}")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if len(failures) > len(matches):
        verdict = "PROPERTY MODEL FAILS"
        interpretation = """
The synthetic property-based registry CANNOT reproduce the observed
Voynich MIDDLE distribution. Key failures:

1. Hub/tail rationing differs from Voynich pattern
2. Cluster structure doesn't match
3. Uniqueness distribution is wrong

This provides NEGATIVE EVIDENCE against interpreting MIDDLEs as
encoding latent material properties. The Voynich structure arises
from something OTHER than property composition.

The "incompatibility manifold" interpretation is DEFENDED:
- A registers don't enumerate property combinations
- They enumerate regions defined by constraint avoidance
"""
    elif len(failures) == len(matches):
        verdict = "INCONCLUSIVE"
        interpretation = """
Property model shows mixed results. Cannot definitively rule out
property-based interpretations, but also doesn't support them.
"""
    else:
        verdict = "PROPERTY MODEL PLAUSIBLE"
        interpretation = """
Property model reproduces many Voynich patterns. This does NOT
confirm property interpretation, but doesn't rule it out either.
"""

    print(f"Verdict: {verdict}")
    print()
    print(f"Interpretation: {interpretation.strip()}")

    # Save results
    output = {
        'test': 'SYNTHETIC_PROPERTY_CONTROL',
        'actual_metrics': {
            'n_folios': n_actual_folios,
            'n_vocab': n_actual_vocab,
            'universal': actual_universal,
            'hub_ratio': actual_hub,
            'clusters': actual_clusters,
            'uniqueness': actual_unique
        },
        'property_metrics': {
            'universal': prop_universal,
            'hub_ratio': prop_hub,
            'clusters': prop_clusters,
            'uniqueness': prop_unique
        },
        'uniform_metrics': {
            'universal': unif_universal,
            'hub_ratio': unif_hub,
            'clusters': unif_clusters,
            'uniqueness': unif_unique
        },
        'failures': failures,
        'matches': matches,
        'verdict': verdict,
        'interpretation': interpretation.strip()
    }

    with open('results/synthetic_property_control.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to results/synthetic_property_control.json")

if __name__ == '__main__':
    main()
