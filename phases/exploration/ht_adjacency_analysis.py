#!/usr/bin/env python3
"""
HT-THREAD Phase 5: Folio Adjacency Patterns

Tests if HT types cluster in adjacent folios like Currier A vocabulary (C424).

Key question: Do adjacent folios share more HT vocabulary than non-adjacent?
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import re

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# HT prefixes
HT_PREFIXES = {
    'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc',
    'do', 'ta', 'ke', 'al', 'po', 'ko', 'yd', 'ysh',
    'ych', 'kch', 'ks'
}

def is_ht_token(token):
    """Check if token is HT."""
    if not token or len(token) < 2:
        return False
    for prefix in sorted(HT_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            return True
    return False

def get_folio_order():
    """Get folios in manuscript order."""
    def folio_sort_key(f):
        match = re.match(r'f(\d+)([rv])(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)
    return folio_sort_key

def load_ht_types_per_folio():
    """Load actual HT types (not just prefixes) per folio."""
    import csv

    folio_ht_types = defaultdict(set)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')

        for row in reader:
            folio = row.get('folio', '').strip('"')
            token = row.get('word', '').strip('"')

            if not folio or not token:
                continue

            # Skip damaged tokens
            if '*' in token:
                continue

            if is_ht_token(token):
                folio_ht_types[folio].add(token)

    return folio_ht_types

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def compute_adjacency_similarity(folio_ht_types):
    """
    Compute HT vocabulary similarity between adjacent vs non-adjacent folios.
    """
    sort_key = get_folio_order()
    ordered_folios = sorted(folio_ht_types.keys(), key=sort_key)

    # Adjacent pairs
    adjacent_sims = []
    for i in range(len(ordered_folios) - 1):
        f1 = ordered_folios[i]
        f2 = ordered_folios[i + 1]

        # Only compute if both have HT tokens
        if folio_ht_types[f1] and folio_ht_types[f2]:
            sim = jaccard_similarity(folio_ht_types[f1], folio_ht_types[f2])
            adjacent_sims.append(sim)

    # Non-adjacent pairs (sample to keep computation manageable)
    non_adjacent_sims = []
    n = len(ordered_folios)
    np.random.seed(42)

    # Sample 500 non-adjacent pairs
    for _ in range(500):
        i = np.random.randint(0, n)
        j = np.random.randint(0, n)

        # Ensure not adjacent
        if abs(i - j) <= 1:
            continue

        f1 = ordered_folios[i]
        f2 = ordered_folios[j]

        if folio_ht_types[f1] and folio_ht_types[f2]:
            sim = jaccard_similarity(folio_ht_types[f1], folio_ht_types[f2])
            non_adjacent_sims.append(sim)

    return adjacent_sims, non_adjacent_sims, ordered_folios

def permutation_test(adjacent_sims, non_adjacent_sims, n_perms=1000):
    """Permutation test for adjacency enrichment."""
    observed_diff = np.mean(adjacent_sims) - np.mean(non_adjacent_sims)

    # Combine all similarities
    all_sims = adjacent_sims + non_adjacent_sims
    n_adjacent = len(adjacent_sims)

    # Permutation
    null_diffs = []
    np.random.seed(42)

    for _ in range(n_perms):
        np.random.shuffle(all_sims)
        perm_adjacent = all_sims[:n_adjacent]
        perm_non_adjacent = all_sims[n_adjacent:]
        null_diffs.append(np.mean(perm_adjacent) - np.mean(perm_non_adjacent))

    # P-value (one-tailed: adjacent > non-adjacent)
    p_value = np.mean([d >= observed_diff for d in null_diffs])

    return {
        'observed_diff': float(observed_diff),
        'p_value': float(p_value),
        'enrichment_ratio': (
            float(np.mean(adjacent_sims) / np.mean(non_adjacent_sims))
            if np.mean(non_adjacent_sims) > 0 else float('inf')
        )
    }

def main():
    print("=" * 70)
    print("HT-THREAD Phase 5: Folio Adjacency Analysis")
    print("=" * 70)

    # Load HT types per folio
    print("\n[1] Loading HT vocabulary per folio...")
    folio_ht_types = load_ht_types_per_folio()
    print(f"    Loaded HT types for {len(folio_ht_types)} folios")

    # Compute stats
    type_counts = [len(types) for types in folio_ht_types.values() if types]
    print(f"    Mean HT types per folio: {np.mean(type_counts):.1f}")
    print(f"    Median HT types per folio: {np.median(type_counts):.1f}")

    # Compute adjacency similarity
    print("\n[2] Computing adjacency similarity...")
    adjacent_sims, non_adjacent_sims, ordered_folios = compute_adjacency_similarity(folio_ht_types)

    print(f"    Adjacent pairs: {len(adjacent_sims)}")
    print(f"    Non-adjacent pairs: {len(non_adjacent_sims)}")
    print(f"    Mean adjacent similarity: {np.mean(adjacent_sims):.4f}")
    print(f"    Mean non-adjacent similarity: {np.mean(non_adjacent_sims):.4f}")

    # Permutation test
    print("\n[3] Running permutation test...")
    perm_result = permutation_test(adjacent_sims, non_adjacent_sims)

    enrichment = perm_result['enrichment_ratio']
    p_value = perm_result['p_value']

    print(f"    Enrichment ratio: {enrichment:.3f}x")
    print(f"    P-value: {p_value:.4f}")

    if p_value < 0.05 and enrichment > 1.0:
        verdict = 'SIGNIFICANT_ADJACENCY_CLUSTERING'
        interpretation = f'HT vocabulary shows {enrichment:.2f}x enrichment in adjacent folios (p={p_value:.4f})'
    elif enrichment > 1.0:
        verdict = 'WEAK_ADJACENCY_EFFECT'
        interpretation = f'HT vocabulary shows weak adjacency enrichment ({enrichment:.2f}x) but not significant (p={p_value:.4f})'
    else:
        verdict = 'NO_ADJACENCY_EFFECT'
        interpretation = f'HT vocabulary does not cluster in adjacent folios (enrichment={enrichment:.2f}x, p={p_value:.4f})'

    print(f"\n    Verdict: {verdict}")
    print(f"    {interpretation}")

    # Compare to C424 (Currier A adjacency)
    print("\n[4] Comparison to C424 (Currier A adjacency)...")
    print("    C424: Currier A shows 1.31x adjacency enrichment")
    print(f"    HT: {enrichment:.2f}x adjacency enrichment")

    if enrichment > 1.31:
        comparison = 'HT shows STRONGER adjacency clustering than Currier A'
    elif enrichment > 1.0:
        comparison = 'HT shows SIMILAR or WEAKER adjacency clustering than Currier A'
    else:
        comparison = 'HT shows NO adjacency clustering (unlike Currier A)'

    print(f"    {comparison}")

    # Save results
    output = {
        'metadata': {
            'analysis': 'HT-THREAD Phase 5',
            'description': 'HT folio adjacency analysis',
            'n_folios': len(folio_ht_types)
        },
        'statistics': {
            'mean_adjacent_similarity': float(np.mean(adjacent_sims)),
            'std_adjacent_similarity': float(np.std(adjacent_sims)),
            'mean_non_adjacent_similarity': float(np.mean(non_adjacent_sims)),
            'std_non_adjacent_similarity': float(np.std(non_adjacent_sims)),
            'n_adjacent_pairs': len(adjacent_sims),
            'n_non_adjacent_pairs': len(non_adjacent_sims)
        },
        'permutation_test': perm_result,
        'verdict': verdict,
        'interpretation': interpretation,
        'c424_comparison': {
            'c424_enrichment': 1.31,
            'ht_enrichment': float(enrichment),
            'comparison': comparison
        }
    }

    output_path = RESULTS / "ht_adjacency_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 5 SUMMARY")
    print("=" * 70)
    print(f"\nVerdict: {verdict}")
    print(f"Enrichment: {enrichment:.2f}x (C424 reference: 1.31x)")
    print(f"P-value: {p_value:.4f}")
    print("\n" + "=" * 70)

    return output

if __name__ == "__main__":
    main()
