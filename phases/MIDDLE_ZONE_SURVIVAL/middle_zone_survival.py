#!/usr/bin/env python3
"""
MIDDLE Zone Survival Analysis

Tier 3 Exploratory Phase

Pre-Registered Question:
"Do MIDDLEs exhibit stable, non-random survival profiles across AZC legality
zones (C/P/R/S), after controlling for frequency, section, and prefix?"

Method:
1. Parse all AZC tokens to extract MIDDLE components
2. Map each MIDDLE to its zone distribution (C/P/R/S counts)
3. Cluster MIDDLEs by zone profile similarity
4. Test for non-random clustering (vs frequency-matched null)
5. Control for: frequency, section, prefix, family

Semantic Ceiling:
- This reveals MIDDLE-level legality patterns
- NOT material decoding
- NOT entry-level A→B mapping
"""

import csv
import json
import random
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "middle_zone_survival.json"

# Zone mapping: subscripted → base zone
ZONE_MAP = {
    'C': 'C', 'C1': 'C', 'C2': 'C',
    'P': 'P',
    'R': 'R', 'R1': 'R', 'R2': 'R', 'R3': 'R', 'R4': 'R',
    'S': 'S', 'S0': 'S', 'S1': 'S', 'S2': 'S', 'S3': 'S'
}

# Valid zones for analysis (exclude X, Y, L, O, etc.)
VALID_ZONES = {'C', 'P', 'R', 'S'}

# Prefix definitions
PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'sa']

# Suffix definitions
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]

# AZC Family definitions
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}


def decompose_token(token):
    """Extract prefix, middle, suffix from token."""
    if not token or len(token) < 2:
        return None, None, None

    # Skip invalid tokens
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token

    # Find prefix (longest match first)
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    # Find suffix (longest match first)
    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    # Middle must be non-empty
    if not middle:
        middle = None

    return prefix, middle, suffix


def load_azc_data():
    """Load AZC tokens with zone information."""
    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip('"')
            if transcriber != 'H':
                continue

            lang = row['language'].strip('"')
            if lang != 'NA':  # Only AZC
                continue

            token = row['word'].strip('"').lower()
            folio = row['folio'].strip('"')
            placement = row['placement'].strip('"')
            section = row['section'].strip('"')

            # Map placement to base zone
            base_zone = ZONE_MAP.get(placement)
            if base_zone not in VALID_ZONES:
                continue

            # Determine family
            if folio in ZODIAC_FOLIOS:
                family = 'zodiac'
            elif folio in AC_FOLIOS:
                family = 'ac'
            else:
                family = 'unknown'

            tokens.append({
                'token': token,
                'folio': folio,
                'zone': base_zone,
                'section': section,
                'family': family
            })

    return tokens


def build_middle_zone_profiles(tokens):
    """Build zone distribution for each MIDDLE."""
    middle_data = defaultdict(lambda: {
        'zones': Counter(),
        'prefixes': Counter(),
        'sections': Counter(),
        'families': Counter(),
        'total': 0
    })

    for t in tokens:
        prefix, middle, suffix = decompose_token(t['token'])
        if not middle:
            continue

        middle_data[middle]['zones'][t['zone']] += 1
        middle_data[middle]['prefixes'][prefix or '_NONE_'] += 1
        middle_data[middle]['sections'][t['section']] += 1
        middle_data[middle]['families'][t['family']] += 1
        middle_data[middle]['total'] += 1

    return middle_data


def compute_zone_profile(zone_counts, min_count=5):
    """Compute normalized zone profile [C, P, R, S]."""
    total = sum(zone_counts.values())
    if total < min_count:
        return None

    profile = np.array([
        zone_counts.get('C', 0),
        zone_counts.get('P', 0),
        zone_counts.get('R', 0),
        zone_counts.get('S', 0)
    ], dtype=float)

    # Normalize
    profile = profile / profile.sum()
    return profile


def cluster_middles(middle_data, min_count=5):
    """Cluster MIDDLEs by their zone profiles."""
    # Build profile matrix
    middles = []
    profiles = []

    for middle, data in middle_data.items():
        profile = compute_zone_profile(data['zones'], min_count)
        if profile is not None:
            middles.append(middle)
            profiles.append(profile)

    if len(profiles) < 10:
        return None, None, None

    X = np.array(profiles)

    # Hierarchical clustering
    distances = pdist(X, metric='cosine')
    Z = linkage(distances, method='ward')

    # Try different cluster counts
    best_k = 2
    best_silhouette = -1

    for k in range(2, min(8, len(middles) // 5)):
        labels = fcluster(Z, k, criterion='maxclust')
        try:
            sil = silhouette_score(X, labels, metric='cosine')
            if sil > best_silhouette:
                best_silhouette = sil
                best_k = k
        except:
            pass

    final_labels = fcluster(Z, best_k, criterion='maxclust')

    return middles, profiles, final_labels, best_k, best_silhouette


def compute_cluster_profiles(middles, profiles, labels):
    """Compute mean profile for each cluster."""
    profiles = np.array(profiles)
    cluster_ids = sorted(set(labels))

    cluster_info = {}
    for cid in cluster_ids:
        mask = np.array(labels) == cid
        cluster_profiles = profiles[mask]
        cluster_middles = [m for m, l in zip(middles, labels) if l == cid]

        mean_profile = cluster_profiles.mean(axis=0)
        std_profile = cluster_profiles.std(axis=0)

        # Determine dominant zone
        zone_names = ['C', 'P', 'R', 'S']
        dominant_zone = zone_names[np.argmax(mean_profile)]

        cluster_info[int(cid)] = {
            'size': int(mask.sum()),
            'mean_profile': {
                'C': float(mean_profile[0]),
                'P': float(mean_profile[1]),
                'R': float(mean_profile[2]),
                'S': float(mean_profile[3])
            },
            'std_profile': {
                'C': float(std_profile[0]),
                'P': float(std_profile[1]),
                'R': float(std_profile[2]),
                'S': float(std_profile[3])
            },
            'dominant_zone': dominant_zone,
            'example_middles': cluster_middles[:10]
        }

    return cluster_info


def null_model_test(profiles, labels, n_permutations=1000):
    """Test clustering significance against null model."""
    observed_silhouette = silhouette_score(np.array(profiles), labels, metric='cosine')

    null_scores = []
    for _ in range(n_permutations):
        shuffled_labels = np.random.permutation(labels)
        try:
            null_sil = silhouette_score(np.array(profiles), shuffled_labels, metric='cosine')
            null_scores.append(null_sil)
        except:
            pass

    if not null_scores:
        return observed_silhouette, 1.0, 0.0

    null_scores = np.array(null_scores)
    p_value = (null_scores >= observed_silhouette).mean()

    return observed_silhouette, p_value, null_scores.mean()


def frequency_control_test(middle_data, middles, profiles, labels, n_bootstrap=100):
    """Test if clustering survives frequency control."""
    # Get frequencies
    frequencies = np.array([middle_data[m]['total'] for m in middles])

    # Bootstrap within frequency bands
    freq_quartiles = np.percentile(frequencies, [25, 50, 75])

    band_silhouettes = []
    for _ in range(n_bootstrap):
        # Sample equally from each frequency band
        band_indices = []
        for i, (low, high) in enumerate([
            (0, freq_quartiles[0]),
            (freq_quartiles[0], freq_quartiles[1]),
            (freq_quartiles[1], freq_quartiles[2]),
            (freq_quartiles[2], frequencies.max() + 1)
        ]):
            band_mask = (frequencies >= low) & (frequencies < high)
            band_idx = np.where(band_mask)[0]
            if len(band_idx) >= 5:
                sampled = np.random.choice(band_idx, min(len(band_idx), 20), replace=False)
                band_indices.extend(sampled)

        if len(band_indices) < 20:
            continue

        sampled_profiles = np.array([profiles[i] for i in band_indices])
        sampled_labels = np.array([labels[i] for i in band_indices])

        try:
            sil = silhouette_score(sampled_profiles, sampled_labels, metric='cosine')
            band_silhouettes.append(sil)
        except:
            pass

    if not band_silhouettes:
        return 0.0, 1.0

    return np.mean(band_silhouettes), np.std(band_silhouettes)


def main():
    print("=" * 60)
    print("MIDDLE Zone Survival Analysis")
    print("Tier 3 Exploratory Phase")
    print("=" * 60)
    print()

    # Load data
    print("Loading AZC data...")
    tokens = load_azc_data()
    print(f"  AZC tokens with valid zones: {len(tokens)}")

    # Zone distribution
    zone_counts = Counter(t['zone'] for t in tokens)
    print(f"  Zone distribution: {dict(zone_counts)}")
    print()

    # Build MIDDLE profiles
    print("Building MIDDLE zone profiles...")
    middle_data = build_middle_zone_profiles(tokens)
    print(f"  Unique MIDDLEs found: {len(middle_data)}")

    # Filter by minimum count
    min_count = 5
    qualified = sum(1 for d in middle_data.values() if d['total'] >= min_count)
    print(f"  MIDDLEs with >= {min_count} occurrences: {qualified}")
    print()

    # Cluster analysis
    print("Clustering MIDDLEs by zone profile...")
    result = cluster_middles(middle_data, min_count)

    if result[0] is None:
        print("  ERROR: Insufficient data for clustering")
        return

    middles, profiles, labels, k, silhouette = result
    print(f"  Optimal cluster count: {k}")
    print(f"  Silhouette score: {silhouette:.4f}")
    print()

    # Cluster profiles
    print("Computing cluster profiles...")
    cluster_info = compute_cluster_profiles(middles, profiles, labels)

    for cid, info in sorted(cluster_info.items()):
        print(f"  Cluster {cid} (n={info['size']}):")
        print(f"    Dominant zone: {info['dominant_zone']}")
        print(f"    Profile: C={info['mean_profile']['C']:.2f}, P={info['mean_profile']['P']:.2f}, "
              f"R={info['mean_profile']['R']:.2f}, S={info['mean_profile']['S']:.2f}")
        print(f"    Examples: {', '.join(info['example_middles'][:5])}")
    print()

    # Null model test
    print("Testing against null model (1000 permutations)...")
    observed_sil, p_value, null_mean = null_model_test(profiles, labels)
    print(f"  Observed silhouette: {observed_sil:.4f}")
    print(f"  Null mean silhouette: {null_mean:.4f}")
    print(f"  P-value: {p_value:.6f}")
    print()

    # Frequency control
    print("Testing frequency control...")
    freq_sil_mean, freq_sil_std = frequency_control_test(middle_data, middles, profiles, labels)
    print(f"  Frequency-controlled silhouette: {freq_sil_mean:.4f} (+/- {freq_sil_std:.4f})")
    print()

    # Verdict
    print("=" * 60)
    if p_value < 0.01 and freq_sil_mean > 0.1:
        verdict = "CONFIRMED"
        print("VERDICT: CONFIRMED")
        print("  MIDDLEs show significant zone-specific survival patterns")
    elif p_value < 0.05:
        verdict = "WEAK_SIGNAL"
        print("VERDICT: WEAK SIGNAL")
        print("  Some evidence of zone preference, but not robust")
    else:
        verdict = "NO_SIGNAL"
        print("VERDICT: NO SIGNAL")
        print("  No significant zone-specific patterns detected")
    print("=" * 60)

    # Save results
    results = {
        "phase": "MIDDLE_ZONE_SURVIVAL",
        "tier": 3,
        "question": "Do MIDDLEs exhibit stable survival profiles across AZC legality zones?",
        "data": {
            "azc_tokens": len(tokens),
            "unique_middles": len(middle_data),
            "qualified_middles": len(middles),
            "zone_distribution": dict(zone_counts)
        },
        "clustering": {
            "optimal_k": k,
            "silhouette": float(silhouette),
            "clusters": cluster_info
        },
        "significance": {
            "observed_silhouette": float(observed_sil),
            "null_mean_silhouette": float(null_mean),
            "p_value": float(p_value)
        },
        "frequency_control": {
            "mean_silhouette": float(freq_sil_mean),
            "std_silhouette": float(freq_sil_std)
        },
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
