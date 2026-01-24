#!/usr/bin/env python3
"""
Test 9: PREFIX-Based Folio Correlation

Since PP is too universal, check if PREFIX patterns discriminate A→B folios.
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# PREFIX extraction
PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lsh',
            'ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'lk', 'yk',
            'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po',
            'sa', 'ka', 'ta', 'al', 'ar', 'or', 'o', 'd', 's', 'y', 'l', 'r', 'q', 'k', 't', 'p', 'f']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)


def extract_prefix(token):
    if pd.isna(token):
        return None
    token = str(token).strip()
    if not token:
        return None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None


def jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    # Split A and B
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()

    # Extract PREFIXes
    df_a['prefix'] = df_a['word'].apply(extract_prefix)
    df_b['prefix'] = df_b['word'].apply(extract_prefix)

    df_a = df_a[df_a['prefix'].notna()]
    df_b = df_b[df_b['prefix'].notna()]

    # Get PREFIX vocabularies
    a_prefixes = set(df_a['prefix'].unique())
    b_prefixes = set(df_b['prefix'].unique())
    shared_prefixes = a_prefixes & b_prefixes

    print(f"A PREFIXes: {len(a_prefixes)}")
    print(f"B PREFIXes: {len(b_prefixes)}")
    print(f"Shared: {len(shared_prefixes)}")

    # Build per-folio PREFIX profiles (frequency-weighted)
    a_folio_prefix = {}
    for folio, group in df_a.groupby('folio'):
        prefix_counts = Counter(group['prefix'])
        a_folio_prefix[folio] = prefix_counts

    b_folio_prefix = {}
    for folio, group in df_b.groupby('folio'):
        prefix_counts = Counter(group['prefix'])
        b_folio_prefix[folio] = prefix_counts

    print(f"\nA folios: {len(a_folio_prefix)}")
    print(f"B folios: {len(b_folio_prefix)}")

    # Compute similarity using cosine on PREFIX frequency vectors
    all_prefixes = sorted(shared_prefixes)

    def to_vector(counts, vocab):
        return np.array([counts.get(p, 0) for p in vocab], dtype=float)

    def cosine_sim(v1, v2):
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(v1, v2) / (norm1 * norm2)

    a_folios = sorted(a_folio_prefix.keys())
    b_folios = sorted(b_folio_prefix.keys())

    sim_matrix = np.zeros((len(a_folios), len(b_folios)))

    for i, a_fol in enumerate(a_folios):
        a_vec = to_vector(a_folio_prefix[a_fol], all_prefixes)
        for j, b_fol in enumerate(b_folios):
            b_vec = to_vector(b_folio_prefix[b_fol], all_prefixes)
            sim_matrix[i, j] = cosine_sim(a_vec, b_vec)

    print(f"\n=== PREFIX Similarity Statistics ===")
    print(f"Mean A→B cosine: {sim_matrix.mean():.3f}")
    print(f"Max A→B cosine: {sim_matrix.max():.3f}")
    print(f"Std A→B cosine: {sim_matrix.std():.3f}")

    # For each A folio, find best matching B folio
    print(f"\n=== Top A→B Matches ===")
    best_matches = []
    for i, a_fol in enumerate(a_folios):
        row = sim_matrix[i, :]
        best_idx = np.argmax(row)
        best_sim = row[best_idx]
        best_b = b_folios[best_idx]

        # Count distinct best matches (>95% of max)
        near_best = np.sum(row > 0.95 * best_sim) if best_sim > 0 else 0

        best_matches.append({
            'a_folio': a_fol,
            'best_b': best_b,
            'similarity': best_sim,
            'near_best_count': near_best
        })

    best_matches.sort(key=lambda x: x['similarity'], reverse=True)
    print("\nTop 10 A→B matches by cosine:")
    for m in best_matches[:10]:
        print(f"  {m['a_folio']} → {m['best_b']}: {m['similarity']:.3f} ({m['near_best_count']} near-best)")

    # Check match concentration
    print(f"\n=== Match Specificity ===")
    near_best_counts = [m['near_best_count'] for m in best_matches]
    print(f"Mean 'near-best' B folios per A: {np.mean(near_best_counts):.1f}")
    print(f"Min: {np.min(near_best_counts)}, Max: {np.max(near_best_counts)}")

    # Check for dominant PREFIX patterns
    print(f"\n=== Dominant PREFIX Analysis ===")

    # For each A folio, what's the dominant PREFIX?
    a_dominant = {}
    for folio, counts in a_folio_prefix.items():
        if counts:
            dominant = counts.most_common(1)[0][0]
            a_dominant[folio] = dominant

    # Group A folios by dominant PREFIX
    prefix_groups = defaultdict(list)
    for folio, prefix in a_dominant.items():
        prefix_groups[prefix].append(folio)

    print("\nA folios grouped by dominant PREFIX:")
    for prefix, folios in sorted(prefix_groups.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {prefix}: {len(folios)} folios")

    # For each PREFIX group, do they map to similar B folios?
    print(f"\n=== PREFIX Group → B Folio Consistency ===")
    for prefix, a_fols in sorted(prefix_groups.items(), key=lambda x: -len(x[1]))[:5]:
        if len(a_fols) < 3:
            continue

        indices = [a_folios.index(f) for f in a_fols]
        best_bs = []
        for i in indices:
            best_idx = np.argmax(sim_matrix[i, :])
            best_bs.append(b_folios[best_idx])

        b_counts = Counter(best_bs)
        concentration = b_counts.most_common(1)[0][1] / len(best_bs) if best_bs else 0

        print(f"\n  PREFIX '{prefix}' ({len(a_fols)} A folios):")
        print(f"    Top B matches: {b_counts.most_common(3)}")
        print(f"    Concentration: {concentration:.1%}")

    # Permutation test
    print(f"\n=== Permutation Test ===")
    observed_mean_max = np.mean([sim_matrix[i, :].max() for i in range(len(a_folios))])

    n_perms = 1000
    perm_means = []
    b_vectors = [to_vector(b_folio_prefix[b], all_prefixes) for b in b_folios]

    for _ in range(n_perms):
        np.random.shuffle(b_vectors)
        perm_maxes = []
        for i, a_fol in enumerate(a_folios):
            a_vec = to_vector(a_folio_prefix[a_fol], all_prefixes)
            max_sim = max(cosine_sim(a_vec, bv) for bv in b_vectors)
            perm_maxes.append(max_sim)
        perm_means.append(np.mean(perm_maxes))

    perm_mean = np.mean(perm_means)
    perm_std = np.std(perm_means)
    z_score = (observed_mean_max - perm_mean) / perm_std if perm_std > 0 else 0
    p_value = np.mean([p >= observed_mean_max for p in perm_means])

    print(f"Observed mean-max similarity: {observed_mean_max:.3f}")
    print(f"Permutation baseline: {perm_mean:.3f} ± {perm_std:.3f}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P-value: {p_value:.4f}")

    print(f"\n=== VERDICT ===")
    if z_score > 2.0:
        print(f"SIGNAL DETECTED: PREFIX patterns correlate A→B above chance (z={z_score:.2f})")
    else:
        print(f"NO CLEAR SIGNAL: PREFIX patterns don't discriminate A→B (z={z_score:.2f})")
