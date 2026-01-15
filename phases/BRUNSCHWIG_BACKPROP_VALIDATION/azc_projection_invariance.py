#!/usr/bin/env python3
"""
AZC PROJECTION INVARIANCE TEST (Tier A-2)

Question: Does projecting A-registers through AZC legality collapse semantic temptations?

Method:
1. For each A-register, compute its AZC legality footprint (zone survival profile)
2. Cluster registers by ZONE PROFILE, not vocabulary
3. Compare: Do zone-based clusters match vocabulary-based ones?

Expected:
- Partial alignment, not identity
- Demonstrates orthogonality of:
  - discrimination (A)
  - legality (AZC)

Why this matters:
- Reinforces "orthogonal axes" explanation
- Guards against reading property semantics into clusters
- Strengthens C468-C473 integration story
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# LOAD DATA
# ============================================================

def load_folio_zones():
    """Load AZC zone distribution per A folio."""
    folio_zones = defaultdict(Counter)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if language != 'A':
                continue

            # Extract zone from placement
            zone = None
            if placement.startswith('C'):
                zone = 'C'
            elif placement.startswith('P'):
                zone = 'P'
            elif placement.startswith('R'):
                zone = 'R'
            elif placement.startswith('S'):
                zone = 'S'

            if zone:
                folio_zones[folio][zone] += 1

    return folio_zones

def load_folio_middles():
    """Load MIDDLE tokens per folio."""
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

    return folio_middles

def load_classifications():
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

# ============================================================
# CLUSTERING
# ============================================================

def compute_zone_profile(zone_counts):
    """Compute normalized zone distribution."""
    total = sum(zone_counts.values())
    if total == 0:
        return {'C': 0, 'P': 0, 'R': 0, 'S': 0}
    return {z: zone_counts.get(z, 0) / total for z in ['C', 'P', 'R', 'S']}

def zone_distance(p1, p2):
    """Euclidean distance between zone profiles."""
    return math.sqrt(sum((p1.get(z, 0) - p2.get(z, 0))**2 for z in ['C', 'P', 'R', 'S']))

def vocabulary_jaccard(set1, set2):
    """Jaccard similarity for vocabulary sets."""
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

def cluster_by_distance(folios, distance_func, threshold):
    """Generic clustering by distance function."""
    clusters = []
    remaining = set(folios)

    while remaining:
        # Pick arbitrary seed
        seed = min(remaining)
        cluster = {seed}
        remaining.remove(seed)

        # Add all folios within threshold
        changed = True
        while changed:
            changed = False
            for f in list(remaining):
                for c in cluster:
                    if distance_func(f, c) < threshold:
                        cluster.add(f)
                        remaining.discard(f)
                        changed = True
                        break

        clusters.append(cluster)

    return clusters

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("AZC PROJECTION INVARIANCE TEST")
    print("=" * 70)
    print()
    print("Testing if vocabulary-based clusters align with zone-based clusters.")
    print("Partial alignment expected: discrimination (A) orthogonal to legality (AZC).")
    print()

    # Load data
    folio_zones = load_folio_zones()
    folio_middles = load_folio_middles()
    classifications = load_classifications()

    # Get A folios with both zone and vocabulary data
    a_folios = [f for f in classifications.keys()
                if f in folio_zones and f in folio_middles]

    print(f"A folios with zone data: {len([f for f in a_folios if folio_zones[f]])}")
    print(f"A folios with vocabulary data: {len([f for f in a_folios if folio_middles[f]])}")
    print()

    # Check zone data coverage
    folios_with_zones = [f for f in a_folios if sum(folio_zones[f].values()) > 0]
    if len(folios_with_zones) < 10:
        print("WARNING: Limited zone data available.")
        print("Zone data may be in a different format or sparse.")
        print()

    # Compute zone profiles
    zone_profiles = {f: compute_zone_profile(folio_zones[f]) for f in a_folios}

    # Show sample profiles
    print("SAMPLE ZONE PROFILES:")
    print()
    for ptype in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        type_folios = [f for f in a_folios if classifications[f] == ptype][:3]
        if type_folios:
            print(f"  {ptype}:")
            for f in type_folios:
                p = zone_profiles[f]
                counts = folio_zones[f]
                if sum(counts.values()) > 0:
                    print(f"    {f}: C={p['C']:.2f} P={p['P']:.2f} R={p['R']:.2f} S={p['S']:.2f} (n={sum(counts.values())})")
            print()

    # Focus on WATER_GENTLE for detailed comparison
    print("=" * 70)
    print("WATER_GENTLE DETAILED COMPARISON")
    print("=" * 70)
    print()

    gentle_folios = [f for f, t in classifications.items()
                     if t == 'WATER_GENTLE' and f in a_folios]

    print(f"WATER_GENTLE folios: {sorted(gentle_folios)}")
    print()

    # Known vocabulary-based clusters
    vocab_cluster1 = {'f32r', 'f45v'}
    vocab_cluster2 = {'f52v', 'f99v'}

    print("Vocabulary-based clusters (from previous analysis):")
    print(f"  V-Cluster 1: {sorted(vocab_cluster1)}")
    print(f"  V-Cluster 2: {sorted(vocab_cluster2)}")
    print()

    # Compute zone-based distances
    print("Zone profiles and pairwise distances:")
    print()

    for f in sorted(gentle_folios):
        p = zone_profiles[f]
        counts = folio_zones[f]
        print(f"  {f}: C={p['C']:.2f} P={p['P']:.2f} R={p['R']:.2f} S={p['S']:.2f} (n={sum(counts.values())})")
    print()

    # Zone distances between vocabulary clusters
    if all(f in zone_profiles for f in vocab_cluster1) and all(f in zone_profiles for f in vocab_cluster2):
        within_c1 = zone_distance(zone_profiles['f32r'], zone_profiles['f45v'])
        within_c2 = zone_distance(zone_profiles['f52v'], zone_profiles['f99v'])

        # Cross-cluster distances
        cross_distances = []
        for f1 in vocab_cluster1:
            for f2 in vocab_cluster2:
                cross_distances.append(zone_distance(zone_profiles[f1], zone_profiles[f2]))

        avg_cross = sum(cross_distances) / len(cross_distances)

        print("Zone distances:")
        print(f"  Within V-Cluster 1 (f32r, f45v): {within_c1:.3f}")
        print(f"  Within V-Cluster 2 (f52v, f99v): {within_c2:.3f}")
        print(f"  Average cross-cluster: {avg_cross:.3f}")
        print()

        # Interpret
        if within_c1 < avg_cross and within_c2 < avg_cross:
            alignment = "ALIGNED"
            print("Zone distances SUPPORT vocabulary clusters:")
            print("  Within-cluster distances < cross-cluster distances")
        else:
            alignment = "ORTHOGONAL"
            print("Zone distances are ORTHOGONAL to vocabulary clusters:")
            print("  Within-cluster distances ~ cross-cluster distances")
        print()

    # Product type zone profiles
    print("=" * 70)
    print("PRODUCT TYPE ZONE PROFILES")
    print("=" * 70)
    print()

    type_zone_profiles = {}
    for ptype in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        type_folios = [f for f, t in classifications.items()
                       if t == ptype and f in a_folios and sum(folio_zones[f].values()) > 0]

        if type_folios:
            avg_profile = {z: 0 for z in ['C', 'P', 'R', 'S']}
            for f in type_folios:
                for z in ['C', 'P', 'R', 'S']:
                    avg_profile[z] += zone_profiles[f].get(z, 0)
            for z in avg_profile:
                avg_profile[z] /= len(type_folios)

            type_zone_profiles[ptype] = avg_profile
            print(f"{ptype} (n={len(type_folios)}):")
            print(f"  C={avg_profile['C']:.2f} P={avg_profile['P']:.2f} R={avg_profile['R']:.2f} S={avg_profile['S']:.2f}")
    print()

    # Test orthogonality
    print("=" * 70)
    print("ORTHOGONALITY TEST")
    print("=" * 70)
    print()

    # For each folio, compute vocabulary similarity AND zone similarity to type centroids
    # If orthogonal, these should not correlate strongly

    vocab_type_match = []
    zone_type_match = []

    for f in a_folios:
        true_type = classifications[f]

        # Vocabulary match: Jaccard to same-type folios
        same_type_folios = [f2 for f2, t in classifications.items()
                           if t == true_type and f2 != f and f2 in folio_middles]
        if same_type_folios:
            avg_vocab_sim = sum(vocabulary_jaccard(folio_middles[f], folio_middles[f2])
                                for f2 in same_type_folios) / len(same_type_folios)
            vocab_type_match.append(avg_vocab_sim)

            # Zone match: distance to type centroid
            if true_type in type_zone_profiles:
                zone_dist = zone_distance(zone_profiles[f], type_zone_profiles[true_type])
                zone_type_match.append(1 - zone_dist)  # Convert to similarity

    if vocab_type_match and zone_type_match:
        # Compute correlation
        n = min(len(vocab_type_match), len(zone_type_match))
        vocab_type_match = vocab_type_match[:n]
        zone_type_match = zone_type_match[:n]

        mean_v = sum(vocab_type_match) / n
        mean_z = sum(zone_type_match) / n

        num = sum((v - mean_v) * (z - mean_z) for v, z in zip(vocab_type_match, zone_type_match))
        denom_v = math.sqrt(sum((v - mean_v)**2 for v in vocab_type_match))
        denom_z = math.sqrt(sum((z - mean_z)**2 for z in zone_type_match))

        if denom_v > 0 and denom_z > 0:
            correlation = num / (denom_v * denom_z)
        else:
            correlation = 0

        print(f"Vocabulary-Zone correlation: r = {correlation:.3f}")
        print()

        if abs(correlation) < 0.3:
            ortho_status = "CONFIRMED"
            print("ORTHOGONALITY CONFIRMED:")
            print("  Vocabulary discrimination and zone legality are")
            print("  largely independent axes (r < 0.3)")
        elif abs(correlation) < 0.6:
            ortho_status = "PARTIAL"
            print("PARTIAL ORTHOGONALITY:")
            print("  Some correlation exists but axes are distinct")
        else:
            ortho_status = "ALIGNED"
            print("AXES ARE ALIGNED:")
            print("  Vocabulary and zone strongly correlate")
    else:
        correlation = 0
        ortho_status = "INSUFFICIENT_DATA"
        print("Insufficient zone data for correlation analysis")
    print()

    # Final verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if ortho_status == "CONFIRMED":
        verdict = "ORTHOGONAL AXES CONFIRMED"
        interpretation = """
Vocabulary-based discrimination (A register content) and
zone-based legality (AZC position constraints) operate on
DIFFERENT AXES. This means:

1. Sub-class clusters based on vocabulary do NOT simply
   reflect zone legality differences.

2. The two systems (A discrimination, AZC legality) are
   structurally independent, joined at the interface.

3. Semantic property readings are LESS supported because
   vocabulary clusters don't collapse to legality categories.

This strengthens C468-C473 (A/AZC orthogonality).
"""
    elif ortho_status == "PARTIAL":
        verdict = "PARTIAL ORTHOGONALITY"
        interpretation = """
Some independence between vocabulary and zone axes, but
not fully orthogonal. The systems share some structure.
"""
    else:
        verdict = "INSUFFICIENT DATA"
        interpretation = """
Zone data insufficient for robust orthogonality testing.
Further data collection needed.
"""

    print(f"Verdict: {verdict}")
    print()
    print(f"Interpretation: {interpretation.strip()}")

    # Save results
    output = {
        'test': 'AZC_PROJECTION_INVARIANCE',
        'n_folios_tested': len(a_folios),
        'folios_with_zone_data': len(folios_with_zones),
        'type_zone_profiles': type_zone_profiles,
        'vocabulary_zone_correlation': float(correlation) if 'correlation' in dir() else None,
        'orthogonality_status': ortho_status,
        'verdict': verdict,
        'interpretation': interpretation.strip()
    }

    with open('results/azc_projection_invariance.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to results/azc_projection_invariance.json")

if __name__ == '__main__':
    main()
