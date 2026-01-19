#!/usr/bin/env python3
"""
A RECORD-LEVEL PRODUCT PROFILE ANALYSIS

Question: Do entire Currier A records encode compound product specifications
          that predict downstream B REGIME assignment?

Method:
1. Compute profile vector for each A folio (PREFIX distribution + MIDDLE set)
2. Cluster A folios by profile similarity
3. Test if clusters predict B REGIME assignment
4. Map clusters to Brunschwig product categories

Two-level model:
  Level 1 (Entry): Individual tokens encode parameters
  Level 2 (Record): Entire A records encode product profiles
"""

import csv
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

# ============================================================
# KNOWN MORPHOLOGICAL COMPONENTS
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

def decompose_token(token):
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return ('', token, '')

    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return (prefix, token, suffix)

# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load A tokens and B folio REGIME assignments."""

    # Load REGIME assignments
    folio_regime = {}
    with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
        for line in f:
            parts = line.split('|')
            if len(parts) >= 3:
                folio = parts[1].strip()
                regime = parts[2].strip()
                if folio.startswith('f') and regime.startswith('REGIME'):
                    folio_regime[folio] = regime

    # Load A tokens
    a_tokens_by_folio = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            prefix, middle, suffix = decompose_token(word)
            a_tokens_by_folio[folio].append({
                'token': word,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })

    return a_tokens_by_folio, folio_regime

# ============================================================
# PROFILE COMPUTATION
# ============================================================

def compute_folio_profile(tokens):
    """Compute profile vector for a folio's A tokens."""

    if not tokens:
        return None

    # PREFIX distribution
    prefix_counts = Counter(t['prefix'] for t in tokens if t['prefix'])
    total_prefixes = sum(prefix_counts.values())

    prefix_dist = {}
    for p in KNOWN_PREFIXES:
        prefix_dist[p] = prefix_counts.get(p, 0) / total_prefixes if total_prefixes > 0 else 0

    # MIDDLE set and diversity
    middles = [t['middle'] for t in tokens if t['middle']]
    unique_middles = set(middles)
    middle_diversity = len(unique_middles) / len(middles) if middles else 0

    # SUFFIX distribution
    suffix_counts = Counter(t['suffix'] for t in tokens if t['suffix'])
    total_suffixes = sum(suffix_counts.values())

    suffix_dist = {}
    for s in KNOWN_SUFFIXES:
        suffix_dist[s] = suffix_counts.get(s, 0) / total_suffixes if total_suffixes > 0 else 0

    return {
        'prefix_dist': prefix_dist,
        'suffix_dist': suffix_dist,
        'middle_set': unique_middles,
        'middle_diversity': middle_diversity,
        'token_count': len(tokens),
        'unique_middle_count': len(unique_middles)
    }

def profile_distance(p1, p2):
    """Compute distance between two profiles."""

    if p1 is None or p2 is None:
        return 1.0

    # PREFIX distance (L1)
    prefix_dist = 0
    for p in KNOWN_PREFIXES:
        prefix_dist += abs(p1['prefix_dist'].get(p, 0) - p2['prefix_dist'].get(p, 0))
    prefix_dist /= 2  # Normalize to [0, 1]

    # MIDDLE Jaccard distance
    m1 = p1['middle_set']
    m2 = p2['middle_set']
    if m1 or m2:
        jaccard = len(m1 & m2) / len(m1 | m2)
        middle_dist = 1 - jaccard
    else:
        middle_dist = 1.0

    # Combined distance (weighted)
    return 0.5 * prefix_dist + 0.5 * middle_dist

# ============================================================
# CLUSTERING
# ============================================================

def cluster_profiles(profiles, k=4):
    """Simple k-means-like clustering of profiles."""

    folios = list(profiles.keys())
    n = len(folios)

    if n < k:
        return {f: 0 for f in folios}

    # Initialize centroids by picking spread-out folios
    # Use first folio of each quartile by token count
    sorted_folios = sorted(folios, key=lambda f: profiles[f]['token_count'] if profiles[f] else 0)
    step = n // k
    centroid_folios = [sorted_folios[i * step] for i in range(k)]

    # Iterate assignment
    assignments = {}
    for iteration in range(10):
        # Assign each folio to nearest centroid
        new_assignments = {}
        for f in folios:
            if profiles[f] is None:
                new_assignments[f] = 0
                continue

            min_dist = float('inf')
            best_cluster = 0
            for c_idx, c_folio in enumerate(centroid_folios):
                if profiles[c_folio] is None:
                    continue
                dist = profile_distance(profiles[f], profiles[c_folio])
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = c_idx
            new_assignments[f] = best_cluster

        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Update centroids (pick folio closest to cluster mean)
        for c_idx in range(k):
            cluster_folios = [f for f, c in assignments.items() if c == c_idx and profiles[f]]
            if not cluster_folios:
                continue

            # Find folio with minimum average distance to others in cluster
            min_avg_dist = float('inf')
            best_folio = cluster_folios[0]
            for f1 in cluster_folios[:20]:  # Limit for performance
                avg_dist = sum(profile_distance(profiles[f1], profiles[f2])
                              for f2 in cluster_folios[:20]) / len(cluster_folios[:20])
                if avg_dist < min_avg_dist:
                    min_avg_dist = avg_dist
                    best_folio = f1
            centroid_folios[c_idx] = best_folio

    return assignments

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("A RECORD-LEVEL PRODUCT PROFILE ANALYSIS")
    print("=" * 70)
    print()

    # Load data
    a_tokens_by_folio, folio_regime = load_data()

    print(f"Loaded {len(a_tokens_by_folio)} A folios")
    print(f"Loaded {len(folio_regime)} B folio REGIME assignments")
    print()

    # Compute profiles for each A folio
    profiles = {}
    for folio, tokens in a_tokens_by_folio.items():
        profiles[folio] = compute_folio_profile(tokens)

    valid_profiles = {f: p for f, p in profiles.items() if p is not None}
    print(f"Computed {len(valid_profiles)} valid A folio profiles")
    print()

    # Show profile statistics
    print("=" * 70)
    print("A FOLIO PROFILE STATISTICS")
    print("=" * 70)
    print()

    token_counts = [p['token_count'] for p in valid_profiles.values()]
    middle_counts = [p['unique_middle_count'] for p in valid_profiles.values()]
    diversities = [p['middle_diversity'] for p in valid_profiles.values()]

    print(f"Token count: min={min(token_counts)}, max={max(token_counts)}, "
          f"mean={sum(token_counts)/len(token_counts):.1f}")
    print(f"Unique MIDDLEs: min={min(middle_counts)}, max={max(middle_counts)}, "
          f"mean={sum(middle_counts)/len(middle_counts):.1f}")
    print(f"MIDDLE diversity: min={min(diversities):.2f}, max={max(diversities):.2f}, "
          f"mean={sum(diversities)/len(diversities):.2f}")
    print()

    # Cluster A folios
    print("=" * 70)
    print("CLUSTERING A FOLIOS BY PROFILE")
    print("=" * 70)
    print()

    assignments = cluster_profiles(valid_profiles, k=4)

    # Analyze clusters
    cluster_folios = defaultdict(list)
    for f, c in assignments.items():
        cluster_folios[c].append(f)

    for c_idx in sorted(cluster_folios.keys()):
        folios = cluster_folios[c_idx]
        print(f"CLUSTER {c_idx}: {len(folios)} folios")

        # Aggregate PREFIX distribution
        agg_prefix = Counter()
        total_tokens = 0
        for f in folios:
            if profiles[f]:
                for p, ratio in profiles[f]['prefix_dist'].items():
                    agg_prefix[p] += ratio * profiles[f]['token_count']
                total_tokens += profiles[f]['token_count']

        print("  PREFIX signature:")
        for p in ['qo', 'ch', 'y', 'sh', 'd', 'ok', 'ot', 'ol']:
            pct = 100 * agg_prefix[p] / total_tokens if total_tokens > 0 else 0
            if pct > 1:
                bar = '#' * int(pct / 2)
                print(f"    {p:3s}: {pct:5.1f}% {bar}")
        print()

    # Test: Do A clusters predict B REGIME?
    print("=" * 70)
    print("CLUSTER -> B REGIME PREDICTION TEST")
    print("=" * 70)
    print()

    # For each A folio, find which B folios share vocabulary
    # Then check if A cluster predicts B REGIME

    # Load B tokens to find vocabulary overlap
    b_tokens_by_folio = defaultdict(set)
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language == 'B' and word:
                _, middle, _ = decompose_token(word)
                if middle:
                    b_tokens_by_folio[folio].add(middle)

    # Build A folio MIDDLE sets
    a_folio_middles = {}
    for f, p in valid_profiles.items():
        if p:
            a_folio_middles[f] = p['middle_set']

    # For each A folio, find B folios with highest MIDDLE overlap
    a_to_b_mapping = {}
    for a_folio, a_middles in a_folio_middles.items():
        if not a_middles:
            continue

        best_overlap = 0
        best_b_folio = None
        for b_folio, b_middles in b_tokens_by_folio.items():
            overlap = len(a_middles & b_middles)
            if overlap > best_overlap:
                best_overlap = overlap
                best_b_folio = b_folio

        if best_b_folio:
            a_to_b_mapping[a_folio] = {
                'b_folio': best_b_folio,
                'overlap': best_overlap,
                'regime': folio_regime.get(best_b_folio, 'UNKNOWN')
            }

    # Now test: does A cluster predict B REGIME?
    print("A Cluster -> B REGIME distribution:")
    print()

    cluster_regime_dist = defaultdict(Counter)
    for a_folio, mapping in a_to_b_mapping.items():
        cluster = assignments.get(a_folio, -1)
        regime = mapping['regime']
        cluster_regime_dist[cluster][regime] += 1

    for c_idx in sorted(cluster_regime_dist.keys()):
        regime_counts = cluster_regime_dist[c_idx]
        total = sum(regime_counts.values())
        print(f"CLUSTER {c_idx} (n={total}):")
        for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            count = regime_counts.get(regime, 0)
            pct = 100 * count / total if total > 0 else 0
            bar = '#' * int(pct / 3)
            print(f"  {regime}: {pct:5.1f}% {bar}")

        # Dominant regime
        if regime_counts:
            dominant = max(regime_counts.items(), key=lambda x: x[1])
            print(f"  -> Dominant: {dominant[0]} ({100*dominant[1]/total:.0f}%)")
        print()

    # Compute prediction accuracy
    print("=" * 70)
    print("PREDICTION ACCURACY")
    print("=" * 70)
    print()

    # Assign each cluster a "predicted regime" (its dominant)
    cluster_predicted_regime = {}
    for c_idx, regime_counts in cluster_regime_dist.items():
        if regime_counts:
            cluster_predicted_regime[c_idx] = max(regime_counts.items(), key=lambda x: x[1])[0]

    correct = 0
    total = 0
    for a_folio, mapping in a_to_b_mapping.items():
        cluster = assignments.get(a_folio, -1)
        actual_regime = mapping['regime']
        predicted_regime = cluster_predicted_regime.get(cluster)

        if predicted_regime and actual_regime != 'UNKNOWN':
            total += 1
            if predicted_regime == actual_regime:
                correct += 1

    accuracy = correct / total if total > 0 else 0
    print(f"Cluster-based REGIME prediction accuracy: {correct}/{total} ({100*accuracy:.1f}%)")
    print()

    # Baseline: random assignment
    regime_dist = Counter(m['regime'] for m in a_to_b_mapping.values() if m['regime'] != 'UNKNOWN')
    baseline = max(regime_dist.values()) / sum(regime_dist.values()) if regime_dist else 0
    print(f"Baseline (majority class): {100*baseline:.1f}%")
    print(f"Lift over baseline: {accuracy/baseline:.2f}x" if baseline > 0 else "N/A")
    print()

    # Map clusters to Brunschwig product types
    print("=" * 70)
    print("CLUSTER -> BRUNSCHWIG PRODUCT TYPE MAPPING")
    print("=" * 70)
    print()

    product_regime_map = {
        'REGIME_2': 'AROMATIC_WATER (gentle)',
        'REGIME_1': 'AROMATIC_WATER (standard)',
        'REGIME_3': 'OIL_OR_RESIN (intense)',
        'REGIME_4': 'PRECISION_DISTILLATE'
    }

    for c_idx in sorted(cluster_regime_dist.keys()):
        predicted = cluster_predicted_regime.get(c_idx, 'UNKNOWN')
        product = product_regime_map.get(predicted, 'UNKNOWN')

        # Get PREFIX signature
        folios = cluster_folios[c_idx]
        y_ratio = sum(profiles[f]['prefix_dist'].get('y', 0) for f in folios if profiles.get(f)) / len(folios)
        qo_ratio = sum(profiles[f]['prefix_dist'].get('qo', 0) for f in folios if profiles.get(f)) / len(folios)

        print(f"CLUSTER {c_idx}:")
        print(f"  Predicted REGIME: {predicted}")
        print(f"  Brunschwig product: {product}")
        print(f"  PREFIX signature: y={100*y_ratio:.1f}%, qo={100*qo_ratio:.1f}%")
        print()

    # Conclusion
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    if accuracy > baseline * 1.3:
        print("FINDING: A record profiles PREDICT B REGIME assignment")
        print()
        print("This supports the two-level model:")
        print("  Level 1 (Entry): Individual tokens encode parameters")
        print("  Level 2 (Record): Entire A records encode product profiles")
        print()
        print("Brunschwig product types can be inferred from A record profiles")
        print("before seeing the B execution grammar.")
    else:
        print("FINDING: A record profiles show WEAK REGIME prediction")
        print("         Product type encoding may be more distributed")

    # Save results
    results = {
        'cluster_assignments': {f: int(c) for f, c in assignments.items()},
        'cluster_regime_distribution': {
            str(c): dict(counts) for c, counts in cluster_regime_dist.items()
        },
        'prediction_accuracy': accuracy,
        'baseline_accuracy': baseline,
        'cluster_product_mapping': {
            str(c): product_regime_map.get(cluster_predicted_regime.get(c), 'UNKNOWN')
            for c in cluster_regime_dist.keys()
        }
    }

    with open('results/a_record_product_profiles.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to results/a_record_product_profiles.json")

if __name__ == '__main__':
    main()
