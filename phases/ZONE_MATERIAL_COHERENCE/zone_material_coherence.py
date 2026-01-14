#!/usr/bin/env python3
"""
Zone-Material Coherence Test

Tier 3 Exploratory Phase

Pre-Registered Question:
"Do discriminators that require higher intervention affordance also tend to
occur in grammar regions associated with greater phase sensitivity?"

EPISTEMIC SAFEGUARD:
This phase tests coherence between two independent Tier 3 abstractions.
A positive result strengthens interpretive plausibility but does not imply
semantic encoding, referential meaning, or Tier 2 structural necessity.
"""

import csv
import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
ZONE_RESULTS = BASE_PATH / "results" / "middle_zone_survival.json"
OUTPUT_FILE = BASE_PATH / "results" / "zone_material_coherence.json"

# Material class definitions (from PROCESS_ISOMORPHISM)
MATERIAL_CLASSES = {
    'M-A': ['ch', 'qo', 'sh'],  # Phase-sensitive, mobile (ENERGY_OPERATOR)
    'M-B': ['ok', 'ot'],        # Uniform mobile (FREQUENT_OPERATOR)
    'M-C': ['ct'],              # Phase-stable, exclusion-prone (REGISTRY_ONLY)
    'M-D': ['da', 'ol']         # Control-stable (CORE_CONTROL)
}

# Reverse mapping: prefix → material class
PREFIX_TO_CLASS = {}
for mat_class, prefixes in MATERIAL_CLASSES.items():
    for prefix in prefixes:
        PREFIX_TO_CLASS[prefix] = mat_class

# Hypothesis: expected alignment between zone clusters and material classes
HYPOTHESIS = {
    'P': 'M-A',  # High intervention → phase-sensitive
    'S': 'M-D',  # Boundary-surviving → control-stable
    'R': 'M-B',  # Restriction-tolerant → uniform mobile
    'C': 'M-C'   # Entry-preferring → setup-sensitive
}

# Prefix definitions (same as middle_zone_survival.py)
PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'sa']

# Suffix definitions
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token):
    """Extract prefix, middle, suffix from token."""
    if not token or len(token) < 2:
        return None, None, None

    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def load_zone_clusters():
    """Load MIDDLE zone cluster assignments from previous analysis."""
    with open(ZONE_RESULTS, 'r') as f:
        data = json.load(f)

    clusters = data['clustering']['clusters']

    # Map cluster number to dominant zone
    cluster_to_zone = {}
    zone_to_middles = defaultdict(set)

    for cluster_id, info in clusters.items():
        zone = info['dominant_zone']
        cluster_to_zone[int(cluster_id)] = zone
        # We only have example_middles in the saved data
        # Need to reconstruct full membership
        for m in info['example_middles']:
            zone_to_middles[zone].add(m)

    return cluster_to_zone, zone_to_middles, data


def rebuild_cluster_membership():
    """Rebuild full cluster membership by re-running clustering logic."""
    # Load zone results
    with open(ZONE_RESULTS, 'r') as f:
        data = json.load(f)

    # We need to re-extract from original data
    # The saved results only have example_middles
    # Let's use a simpler approach: assign by dominant zone profile

    # Load tokens and build profiles
    middle_zones = defaultdict(Counter)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'NA':  # Only AZC
                continue

            token = row['word'].strip('"').lower()
            placement = row['placement'].strip('"')

            # Map to base zone
            zone_map = {'C': 'C', 'C1': 'C', 'C2': 'C',
                       'P': 'P',
                       'R': 'R', 'R1': 'R', 'R2': 'R', 'R3': 'R', 'R4': 'R',
                       'S': 'S', 'S0': 'S', 'S1': 'S', 'S2': 'S', 'S3': 'S'}

            base_zone = zone_map.get(placement)
            if base_zone not in {'C', 'P', 'R', 'S'}:
                continue

            prefix, middle, suffix = decompose_token(token)
            if not middle:
                continue

            middle_zones[middle][base_zone] += 1

    # Assign each MIDDLE to dominant zone (simplified clustering)
    zone_to_middles = defaultdict(set)
    middle_to_zone = {}

    for middle, zones in middle_zones.items():
        total = sum(zones.values())
        if total < 5:  # Same threshold as original
            continue

        # Find dominant zone
        dominant = max(zones, key=lambda z: zones[z])
        dominant_pct = zones[dominant] / total

        # Require majority dominance
        if dominant_pct >= 0.4:  # At least 40% in dominant zone
            zone_to_middles[dominant].add(middle)
            middle_to_zone[middle] = dominant

    return zone_to_middles, middle_to_zone


def load_currier_a_tokens():
    """Load all Currier A tokens with prefix-MIDDLE pairs."""
    pairs = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'A':  # Only Currier A
                continue

            token = row['word'].strip('"').lower()
            prefix, middle, suffix = decompose_token(token)

            if prefix and middle:
                pairs.append((prefix, middle))

    return pairs


def compute_enrichment(zone_to_middles, prefix_middle_pairs):
    """Compute material class enrichment for each zone cluster."""
    # Count prefix co-occurrence with MIDDLEs in each zone
    zone_class_counts = {zone: Counter() for zone in ['C', 'P', 'R', 'S']}
    zone_total_counts = {zone: 0 for zone in ['C', 'P', 'R', 'S']}

    # Build MIDDLE → zone mapping
    middle_to_zone = {}
    for zone, middles in zone_to_middles.items():
        for m in middles:
            middle_to_zone[m] = zone

    # Count prefix occurrences with MIDDLEs from each zone
    for prefix, middle in prefix_middle_pairs:
        if middle not in middle_to_zone:
            continue

        zone = middle_to_zone[middle]
        mat_class = PREFIX_TO_CLASS.get(prefix)

        if mat_class:
            zone_class_counts[zone][mat_class] += 1
            zone_total_counts[zone] += 1

    # Compute proportions
    zone_profiles = {}
    for zone in ['C', 'P', 'R', 'S']:
        total = zone_total_counts[zone]
        if total > 0:
            profile = {
                mat_class: zone_class_counts[zone][mat_class] / total
                for mat_class in ['M-A', 'M-B', 'M-C', 'M-D']
            }
        else:
            profile = {mat_class: 0 for mat_class in ['M-A', 'M-B', 'M-C', 'M-D']}
        zone_profiles[zone] = profile

    return zone_profiles, zone_class_counts, zone_total_counts


def test_hypothesis(zone_profiles, zone_total_counts):
    """Test whether zone-material alignment matches hypothesis."""
    results = {}

    # Global baseline
    all_counts = Counter()
    total_all = 0
    for zone in ['C', 'P', 'R', 'S']:
        total_all += zone_total_counts[zone]

    # For each zone, check if predicted class is enriched
    for zone, predicted_class in HYPOTHESIS.items():
        observed_prop = zone_profiles[zone].get(predicted_class, 0)

        # Compute baseline (all other zones combined)
        other_zones = [z for z in ['C', 'P', 'R', 'S'] if z != zone]
        baseline_sum = sum(
            zone_profiles[z].get(predicted_class, 0) * zone_total_counts[z]
            for z in other_zones
        )
        baseline_total = sum(zone_total_counts[z] for z in other_zones)
        baseline_prop = baseline_sum / baseline_total if baseline_total > 0 else 0

        # Effect size (relative enrichment)
        effect = observed_prop / baseline_prop if baseline_prop > 0 else 0

        # Find actual dominant class
        actual_dominant = max(zone_profiles[zone], key=lambda c: zone_profiles[zone][c])

        results[zone] = {
            'predicted_class': predicted_class,
            'actual_dominant': actual_dominant,
            'predicted_match': predicted_class == actual_dominant,
            'observed_proportion': observed_prop,
            'baseline_proportion': baseline_prop,
            'enrichment_ratio': effect,
            'n': zone_total_counts[zone]
        }

    return results


def permutation_test(zone_to_middles, prefix_middle_pairs, n_permutations=1000):
    """Test significance via permutation."""
    # Observed alignment score
    zone_profiles, zone_class_counts, zone_total_counts = compute_enrichment(
        zone_to_middles, prefix_middle_pairs
    )

    observed_matches = sum(
        1 for zone in HYPOTHESIS
        if zone_profiles[zone].get(HYPOTHESIS[zone], 0) == max(zone_profiles[zone].values())
    )

    # Permutation null
    all_middles = list(set(m for middles in zone_to_middles.values() for m in middles))
    zone_sizes = {zone: len(middles) for zone, middles in zone_to_middles.items()}

    null_matches = []
    for _ in range(n_permutations):
        # Shuffle MIDDLE-zone assignments
        np.random.shuffle(all_middles)

        shuffled_zones = {}
        idx = 0
        for zone in ['C', 'P', 'R', 'S']:
            size = zone_sizes.get(zone, 0)
            shuffled_zones[zone] = set(all_middles[idx:idx+size])
            idx += size

        # Recompute enrichment
        perm_profiles, _, _ = compute_enrichment(shuffled_zones, prefix_middle_pairs)

        perm_matches = sum(
            1 for zone in HYPOTHESIS
            if perm_profiles[zone].get(HYPOTHESIS[zone], 0) == max(perm_profiles[zone].values())
        )
        null_matches.append(perm_matches)

    null_matches = np.array(null_matches)
    p_value = (null_matches >= observed_matches).mean()

    return observed_matches, null_matches.mean(), p_value


def main():
    print("=" * 60)
    print("Zone-Material Coherence Test")
    print("Tier 3 Exploratory Phase")
    print("=" * 60)
    print()
    print("EPISTEMIC SAFEGUARD:")
    print("This tests coherence between two independent Tier 3 abstractions.")
    print("Positive result does NOT imply semantic encoding or Tier 2 necessity.")
    print()

    # Load/rebuild cluster membership
    print("Rebuilding cluster membership...")
    zone_to_middles, middle_to_zone = rebuild_cluster_membership()

    for zone in ['C', 'P', 'R', 'S']:
        print(f"  {zone}-cluster: {len(zone_to_middles[zone])} MIDDLEs")
    print()

    # Load Currier A tokens
    print("Loading Currier A prefix-MIDDLE pairs...")
    pairs = load_currier_a_tokens()
    print(f"  Total pairs: {len(pairs)}")
    print()

    # Compute enrichment
    print("Computing material class enrichment by zone...")
    zone_profiles, zone_class_counts, zone_total_counts = compute_enrichment(
        zone_to_middles, pairs
    )

    for zone in ['C', 'P', 'R', 'S']:
        print(f"  {zone}: n={zone_total_counts[zone]}")
        for mat_class in ['M-A', 'M-B', 'M-C', 'M-D']:
            pct = zone_profiles[zone][mat_class] * 100
            print(f"    {mat_class}: {pct:.1f}%")
    print()

    # Test hypothesis
    print("Testing hypothesis alignment...")
    hypothesis_results = test_hypothesis(zone_profiles, zone_total_counts)

    matches = 0
    for zone in ['C', 'P', 'R', 'S']:
        r = hypothesis_results[zone]
        match_str = "MATCH" if r['predicted_match'] else "MISMATCH"
        print(f"  {zone}: predicted={r['predicted_class']}, actual={r['actual_dominant']} [{match_str}]")
        print(f"      enrichment ratio: {r['enrichment_ratio']:.2f}")
        if r['predicted_match']:
            matches += 1

    print(f"\n  Hypothesis matches: {matches}/4")
    print()

    # Permutation test
    print("Running permutation test (1000 iterations)...")
    obs_matches, null_mean, p_value = permutation_test(zone_to_middles, pairs)
    print(f"  Observed matches: {obs_matches}")
    print(f"  Null mean matches: {null_mean:.2f}")
    print(f"  P-value: {p_value:.4f}")
    print()

    # Verdict
    print("=" * 60)
    if p_value < 0.05 and matches >= 2:
        verdict = "ALIGNED"
        print("VERDICT: ALIGNED")
        print("  Two independent abstractions show statistically significant alignment.")
    elif p_value < 0.1:
        verdict = "WEAK_SIGNAL"
        print("VERDICT: WEAK SIGNAL")
        print("  Some evidence of alignment, not robust.")
    else:
        verdict = "ORTHOGONAL"
        print("VERDICT: ORTHOGONAL")
        print("  Material behavior and zone survival are independent axes.")
    print("=" * 60)

    # Save results
    results = {
        "phase": "ZONE_MATERIAL_COHERENCE",
        "tier": 3,
        "question": "Do zone survival clusters align with material behavior classes?",
        "epistemic_safeguard": "Positive result does not imply semantic encoding or Tier 2 necessity",
        "data": {
            "zone_cluster_sizes": {z: len(m) for z, m in zone_to_middles.items()},
            "currier_a_pairs": len(pairs),
            "zone_sample_sizes": zone_total_counts
        },
        "zone_profiles": zone_profiles,
        "hypothesis_test": hypothesis_results,
        "permutation_test": {
            "observed_matches": int(obs_matches),
            "null_mean_matches": float(null_mean),
            "p_value": float(p_value)
        },
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
