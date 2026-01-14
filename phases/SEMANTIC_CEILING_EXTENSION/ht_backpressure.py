#!/usr/bin/env python3
"""
Test 1B: HT->A Back-Pressure Test

Pre-Registered Question:
"Does HT morphology correspond to apparatus vs material pressure dominance?"

EPISTEMIC SAFEGUARD:
This test remains Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.
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
HT_FEATURES = BASE_PATH / "results" / "ht_folio_features.json"
OUTPUT_FILE = BASE_PATH / "results" / "ht_backpressure.json"

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
    """Load MIDDLE zone cluster assignments (from AZC data)."""
    middle_zones = defaultdict(Counter)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'NA':
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

    middle_to_zone = {}
    for middle, zones in middle_zones.items():
        total = sum(zones.values())
        if total >= 3:
            dominant = max(zones, key=lambda z: zones[z])
            if zones[dominant] / total >= 0.35:
                middle_to_zone[middle] = dominant

    return middle_to_zone


def load_ht_features():
    """Load HT features per folio."""
    with open(HT_FEATURES) as f:
        data = json.load(f)
    return data['folios']


def extract_folio_middles():
    """Extract MIDDLEs used in each folio (A and B)."""
    folio_middles = defaultdict(Counter)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang not in ['A', 'B']:
                continue

            folio = row['folio'].strip('"')
            token = row['word'].strip('"').lower()

            prefix, middle, suffix = decompose_token(token)
            if middle:
                folio_middles[folio][middle] += 1

    return folio_middles


def compute_zone_diversity(middles_counter, middle_to_zone):
    """Compute zone diversity (entropy) for a set of MIDDLEs."""
    zone_counts = Counter()

    for middle, count in middles_counter.items():
        if middle in middle_to_zone:
            zone = middle_to_zone[middle]
            zone_counts[zone] += count

    total = sum(zone_counts.values())
    if total == 0:
        return None, 0

    # Shannon entropy
    entropy = 0
    for zone in ['C', 'P', 'R', 'S']:
        p = zone_counts.get(zone, 0) / total
        if p > 0:
            entropy -= p * np.log2(p)

    return entropy, total


def main():
    print("=" * 60)
    print("Test 1B: HT->A Back-Pressure")
    print("Tier 3/4 Exploratory")
    print("=" * 60)
    print()

    # Load zone clusters
    print("Loading zone cluster assignments...")
    middle_to_zone = load_zone_clusters()
    print(f"  MIDDLEs with zones: {len(middle_to_zone)}")
    print()

    # Load HT features
    print("Loading HT features...")
    ht_features = load_ht_features()
    print(f"  Folios with HT data: {len(ht_features)}")
    print()

    # Extract MIDDLEs per folio
    print("Extracting MIDDLEs per folio...")
    folio_middles = extract_folio_middles()
    print(f"  Folios with MIDDLEs: {len(folio_middles)}")
    print()

    # Compute zone diversity for each folio
    print("Computing zone diversity...")
    folio_diversity = {}
    for folio, middles in folio_middles.items():
        entropy, n = compute_zone_diversity(middles, middle_to_zone)
        if entropy is not None and n >= 10:
            folio_diversity[folio] = entropy

    print(f"  Folios with valid diversity: {len(folio_diversity)}")
    print()

    # Match HT density with zone diversity
    matched_data = []
    for folio in folio_diversity:
        if folio in ht_features:
            matched_data.append({
                'folio': folio,
                'ht_density': ht_features[folio]['ht_density'],
                'ht_ttr': ht_features[folio].get('ht_ttr', 0),
                'zone_diversity': folio_diversity[folio]
            })

    print(f"  Matched folios (HT + diversity): {len(matched_data)}")
    print()

    if len(matched_data) < 10:
        print("  ERROR: Insufficient matched data")
        return

    # Extract arrays
    ht_densities = np.array([d['ht_density'] for d in matched_data])
    ht_ttrs = np.array([d['ht_ttr'] for d in matched_data])
    zone_divs = np.array([d['zone_diversity'] for d in matched_data])

    # Test correlations
    print("Testing correlations...")

    # HT density vs zone diversity
    r_density, p_density = stats.pearsonr(ht_densities, zone_divs)
    print(f"  HT density vs zone diversity: r={r_density:.4f}, p={p_density:.4f}")

    # HT TTR vs zone diversity
    r_ttr, p_ttr = stats.pearsonr(ht_ttrs, zone_divs)
    print(f"  HT TTR vs zone diversity: r={r_ttr:.4f}, p={p_ttr:.4f}")

    # Group comparison: high vs low HT
    ht_median = np.median(ht_densities)
    high_ht = [d['zone_diversity'] for d in matched_data if d['ht_density'] >= ht_median]
    low_ht = [d['zone_diversity'] for d in matched_data if d['ht_density'] < ht_median]

    t_stat, p_group = stats.ttest_ind(high_ht, low_ht)
    print()
    print(f"  High-HT folios (n={len(high_ht)}): mean diversity={np.mean(high_ht):.4f}")
    print(f"  Low-HT folios (n={len(low_ht)}): mean diversity={np.mean(low_ht):.4f}")
    print(f"  Group difference: t={t_stat:.4f}, p={p_group:.4f}")
    print()

    # Verdict
    print("=" * 60)
    if p_density < 0.05 or p_group < 0.05:
        verdict = "HT_ZONE_CORRELATED"
        print("VERDICT: HT CORRELATES WITH ZONE DIVERSITY")
        if r_density > 0:
            print("  Higher HT density -> more zone diversity (material pressure)")
        else:
            print("  Higher HT density -> less zone diversity (apparatus focus)")
    else:
        verdict = "HT_ZONE_INDEPENDENT"
        print("VERDICT: HT AND ZONE DIVERSITY ARE INDEPENDENT")
        print("  HT tracks something orthogonal to zone discrimination.")
    print("=" * 60)

    # Save results
    results = {
        "test": "1B_HT_BACKPRESSURE",
        "tier": "3-4",
        "question": "Does HT morphology correspond to zone diversity?",
        "data": {
            "matched_folios": len(matched_data),
            "ht_range": [float(min(ht_densities)), float(max(ht_densities))],
            "diversity_range": [float(min(zone_divs)), float(max(zone_divs))]
        },
        "correlations": {
            "ht_density_vs_diversity": {
                "r": float(r_density),
                "p": float(p_density)
            },
            "ht_ttr_vs_diversity": {
                "r": float(r_ttr),
                "p": float(p_ttr)
            }
        },
        "group_comparison": {
            "high_ht_mean": float(np.mean(high_ht)),
            "low_ht_mean": float(np.mean(low_ht)),
            "t_statistic": float(t_stat),
            "p_value": float(p_group)
        },
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
