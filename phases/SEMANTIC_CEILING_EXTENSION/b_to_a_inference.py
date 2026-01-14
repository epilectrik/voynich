#!/usr/bin/env python3
"""
Test 1A: B->A Discriminator Back-Inference

Pre-Registered Question:
"Given distinctive B regime behaviors, what MIDDLE zone cluster constraints
must have been active upstream?"

EPISTEMIC SAFEGUARD:
This test remains Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.

Method:
1. Load B folio behavior profiles (brittleness, hazard density, escape reliance)
2. Extract MIDDLEs used in each B folio
3. Map those MIDDLEs to zone cluster assignments (from MIDDLE_ZONE_SURVIVAL)
4. Test if distinctive B behaviors correlate with specific zone distributions
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
B_FEATURES = BASE_PATH / "results" / "b_macro_scaffold_audit.json"
ZONE_RESULTS = BASE_PATH / "results" / "middle_zone_survival.json"
OUTPUT_FILE = BASE_PATH / "results" / "b_to_a_inference.json"

# Prefix/suffix definitions
PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'sa']
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
    """Load MIDDLE zone cluster assignments."""
    # First try the detailed results
    if ZONE_RESULTS.exists():
        with open(ZONE_RESULTS) as f:
            data = json.load(f)

        # Rebuild zone assignments from AZC data
        # The saved results only have examples, so we need to rebuild
        pass

    # Rebuild zone assignments by dominant zone
    middle_zones = defaultdict(Counter)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'NA':  # Only AZC
                continue

            token = row['word'].strip('"').lower()
            placement = row['placement'].strip('"')

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

    # Assign each MIDDLE to dominant zone
    middle_to_zone = {}
    for middle, zones in middle_zones.items():
        total = sum(zones.values())
        if total >= 3:  # Lower threshold for more coverage
            dominant = max(zones, key=lambda z: zones[z])
            if zones[dominant] / total >= 0.35:  # At least 35% in dominant
                middle_to_zone[middle] = dominant

    return middle_to_zone


def load_b_folio_features():
    """Load B folio behavior profiles."""
    with open(B_FEATURES) as f:
        data = json.load(f)
    return data['features']


def extract_b_folio_middles():
    """Extract MIDDLEs used in each B folio."""
    folio_middles = defaultdict(Counter)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'B':  # Only Currier B
                continue

            folio = row['folio'].strip('"')
            token = row['word'].strip('"').lower()

            prefix, middle, suffix = decompose_token(token)
            if middle:
                folio_middles[folio][middle] += 1

    return folio_middles


def compute_zone_distribution(middles_counter, middle_to_zone):
    """Compute zone distribution for a set of MIDDLEs."""
    zone_counts = Counter()
    mapped_count = 0

    for middle, count in middles_counter.items():
        if middle in middle_to_zone:
            zone = middle_to_zone[middle]
            zone_counts[zone] += count
            mapped_count += count

    total = sum(zone_counts.values())
    if total == 0:
        return None, 0

    distribution = {
        'C': zone_counts.get('C', 0) / total,
        'P': zone_counts.get('P', 0) / total,
        'R': zone_counts.get('R', 0) / total,
        'S': zone_counts.get('S', 0) / total
    }

    return distribution, mapped_count


def categorize_b_folios(features):
    """Categorize B folios by distinctive behaviors."""
    categories = {
        'high_brittleness': [],
        'low_brittleness': [],
        'high_hazard': [],
        'low_hazard': [],
        'high_escape': [],
        'low_escape': []
    }

    # Extract metric values
    folios = list(features.keys())
    hazard_densities = [features[f]['hazard_density'] for f in folios]
    qo_densities = [features[f]['qo_density'] for f in folios]
    near_misses = [features[f]['near_miss_count'] for f in folios]

    # Compute thresholds (top/bottom quartile)
    hd_high = np.percentile(hazard_densities, 75)
    hd_low = np.percentile(hazard_densities, 25)
    qo_high = np.percentile(qo_densities, 75)
    qo_low = np.percentile(qo_densities, 25)
    nm_high = np.percentile(near_misses, 75)
    nm_low = np.percentile(near_misses, 25)

    for folio in folios:
        f = features[folio]

        # Brittleness (near-miss count)
        if f['near_miss_count'] >= nm_high:
            categories['high_brittleness'].append(folio)
        elif f['near_miss_count'] <= nm_low:
            categories['low_brittleness'].append(folio)

        # Hazard density
        if f['hazard_density'] >= hd_high:
            categories['high_hazard'].append(folio)
        elif f['hazard_density'] <= hd_low:
            categories['low_hazard'].append(folio)

        # Escape reliance (qo_density)
        if f['qo_density'] >= qo_high:
            categories['high_escape'].append(folio)
        elif f['qo_density'] <= qo_low:
            categories['low_escape'].append(folio)

    return categories


def test_zone_differentiation(folio_zones, categories, contrast_pairs):
    """Test if contrasting B behavior categories have different zone distributions."""
    results = {}

    for pair_name, (cat_high, cat_low) in contrast_pairs.items():
        high_folios = categories[cat_high]
        low_folios = categories[cat_low]

        # Aggregate zone distributions for each group
        high_zones = {'C': [], 'P': [], 'R': [], 'S': []}
        low_zones = {'C': [], 'P': [], 'R': [], 'S': []}

        for folio in high_folios:
            if folio in folio_zones and folio_zones[folio]:
                for zone in ['C', 'P', 'R', 'S']:
                    high_zones[zone].append(folio_zones[folio][zone])

        for folio in low_folios:
            if folio in folio_zones and folio_zones[folio]:
                for zone in ['C', 'P', 'R', 'S']:
                    low_zones[zone].append(folio_zones[folio][zone])

        if not high_zones['C'] or not low_zones['C']:
            results[pair_name] = {'status': 'insufficient_data'}
            continue

        # Test each zone for significant difference
        zone_tests = {}
        significant_zones = []

        for zone in ['C', 'P', 'R', 'S']:
            if len(high_zones[zone]) >= 3 and len(low_zones[zone]) >= 3:
                t_stat, p_value = stats.ttest_ind(high_zones[zone], low_zones[zone])
                effect_size = (np.mean(high_zones[zone]) - np.mean(low_zones[zone])) / np.std(high_zones[zone] + low_zones[zone])

                zone_tests[zone] = {
                    'high_mean': float(np.mean(high_zones[zone])),
                    'low_mean': float(np.mean(low_zones[zone])),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'effect_size': float(effect_size)
                }

                if p_value < 0.05:
                    significant_zones.append(zone)

        results[pair_name] = {
            'status': 'tested',
            'n_high': len(high_folios),
            'n_low': len(low_folios),
            'zone_tests': zone_tests,
            'significant_zones': significant_zones,
            'any_significant': len(significant_zones) > 0
        }

    return results


def main():
    print("=" * 60)
    print("Test 1A: B->A Discriminator Back-Inference")
    print("Tier 3/4 Exploratory")
    print("=" * 60)
    print()

    # Load zone cluster assignments
    print("Loading zone cluster assignments...")
    middle_to_zone = load_zone_clusters()
    print(f"  MIDDLEs with zone assignments: {len(middle_to_zone)}")
    zone_counts = Counter(middle_to_zone.values())
    print(f"  Zone distribution: {dict(zone_counts)}")
    print()

    # Load B folio features
    print("Loading B folio behavior profiles...")
    features = load_b_folio_features()
    print(f"  B folios: {len(features)}")
    print()

    # Extract MIDDLEs from B folios
    print("Extracting MIDDLEs from B folios...")
    folio_middles = extract_b_folio_middles()
    print(f"  B folios with MIDDLEs: {len(folio_middles)}")
    print()

    # Compute zone distribution for each B folio
    print("Computing zone distributions for B folios...")
    folio_zones = {}
    coverage_stats = []

    for folio, middles in folio_middles.items():
        dist, mapped = compute_zone_distribution(middles, middle_to_zone)
        if dist:
            folio_zones[folio] = dist
            coverage_stats.append(mapped / sum(middles.values()))

    print(f"  Folios with zone data: {len(folio_zones)}")
    if coverage_stats:
        print(f"  Mean MIDDLE mapping coverage: {np.mean(coverage_stats):.1%}")
    print()

    # Categorize B folios by behavior
    print("Categorizing B folios by behavior...")
    categories = categorize_b_folios(features)
    for cat, folios in categories.items():
        print(f"  {cat}: {len(folios)} folios")
    print()

    # Test zone differentiation
    print("Testing zone differentiation by B behavior...")
    contrast_pairs = {
        'brittleness': ('high_brittleness', 'low_brittleness'),
        'hazard': ('high_hazard', 'low_hazard'),
        'escape': ('high_escape', 'low_escape')
    }

    diff_results = test_zone_differentiation(folio_zones, categories, contrast_pairs)

    significant_contrasts = []
    for pair_name, result in diff_results.items():
        print(f"\n  {pair_name.upper()}:")
        if result['status'] == 'tested':
            print(f"    High group: {result['n_high']}, Low group: {result['n_low']}")
            for zone, test in result['zone_tests'].items():
                sig = "*" if test['p_value'] < 0.05 else ""
                print(f"    {zone}: high={test['high_mean']:.3f}, low={test['low_mean']:.3f}, p={test['p_value']:.4f}{sig}")
            if result['any_significant']:
                significant_contrasts.append(pair_name)
                print(f"    SIGNIFICANT zones: {result['significant_zones']}")
        else:
            print(f"    {result['status']}")

    print()

    # Verdict
    print("=" * 60)
    if len(significant_contrasts) >= 2:
        verdict = "STRONG_DIFFERENTIATION"
        print("VERDICT: STRONG ZONE DIFFERENTIATION")
        print(f"  {len(significant_contrasts)} behavior contrasts show significant zone differences.")
    elif len(significant_contrasts) == 1:
        verdict = "PARTIAL_DIFFERENTIATION"
        print("VERDICT: PARTIAL ZONE DIFFERENTIATION")
        print(f"  {significant_contrasts[0]} shows significant zone difference.")
    else:
        verdict = "NO_DIFFERENTIATION"
        print("VERDICT: NO ZONE DIFFERENTIATION")
        print("  B behavior profiles do not predict upstream zone constraints.")
    print("=" * 60)

    # Save results
    results = {
        "test": "1A_B_TO_A_INFERENCE",
        "tier": "3-4",
        "question": "Do distinctive B behaviors correlate with MIDDLE zone distributions?",
        "data": {
            "middles_with_zones": len(middle_to_zone),
            "b_folios_analyzed": len(folio_zones),
            "mean_mapping_coverage": float(np.mean(coverage_stats)) if coverage_stats else 0
        },
        "categories": {cat: len(folios) for cat, folios in categories.items()},
        "differentiation_tests": diff_results,
        "significant_contrasts": significant_contrasts,
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
