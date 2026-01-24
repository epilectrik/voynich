#!/usr/bin/env python3
"""
Test 8: PP-Based Folio Correlation

Question: Can PP vocabulary in A folios predict which B folios to consult?

Method:
1. Extract PP vocabulary per A folio
2. Extract PP vocabulary per B folio
3. Compute Jaccard similarity between each A folio and each B folio
4. Check for clustering/correlation patterns
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict
from scipy.stats import spearmanr
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]  # Exclude labels

    # Split A and B
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()

    # Extract MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_b['middle'] = df_b['word'].apply(extract_middle)

    df_a = df_a[df_a['middle'].notna() & (df_a['middle'] != '')]
    df_b = df_b[df_b['middle'].notna() & (df_b['middle'] != '')]

    # Identify PP (shared vocabulary)
    a_middles = set(df_a['middle'].unique())
    b_middles = set(df_b['middle'].unique())
    pp_middles = a_middles & b_middles

    print(f"A MIDDLEs: {len(a_middles)}")
    print(f"B MIDDLEs: {len(b_middles)}")
    print(f"PP (shared): {len(pp_middles)}")

    # Build per-folio PP profiles
    a_folio_pp = {}
    for folio, group in df_a.groupby('folio'):
        middles = set(group['middle'].unique())
        a_folio_pp[folio] = middles & pp_middles

    b_folio_pp = {}
    for folio, group in df_b.groupby('folio'):
        middles = set(group['middle'].unique())
        b_folio_pp[folio] = middles & pp_middles

    print(f"\nA folios with PP: {len(a_folio_pp)}")
    print(f"B folios with PP: {len(b_folio_pp)}")

    # Compute A→B similarity matrix
    a_folios = sorted(a_folio_pp.keys())
    b_folios = sorted(b_folio_pp.keys())

    sim_matrix = np.zeros((len(a_folios), len(b_folios)))

    for i, a_fol in enumerate(a_folios):
        for j, b_fol in enumerate(b_folios):
            sim_matrix[i, j] = jaccard(a_folio_pp[a_fol], b_folio_pp[b_fol])

    # Basic statistics
    print(f"\n=== Similarity Statistics ===")
    print(f"Mean A→B Jaccard: {sim_matrix.mean():.3f}")
    print(f"Max A→B Jaccard: {sim_matrix.max():.3f}")
    print(f"Std A→B Jaccard: {sim_matrix.std():.3f}")

    # For each A folio, find best matching B folio(s)
    print(f"\n=== Top A→B Matches ===")
    best_matches = []
    for i, a_fol in enumerate(a_folios):
        row = sim_matrix[i, :]
        best_idx = np.argmax(row)
        best_sim = row[best_idx]
        best_b = b_folios[best_idx]

        # Count how many B folios have >50% of max similarity
        high_matches = np.sum(row > 0.5 * best_sim) if best_sim > 0 else 0

        best_matches.append({
            'a_folio': a_fol,
            'best_b': best_b,
            'similarity': best_sim,
            'a_pp_count': len(a_folio_pp[a_fol]),
            'high_match_count': high_matches
        })

    # Show top 10 by similarity
    best_matches.sort(key=lambda x: x['similarity'], reverse=True)
    print("\nTop 10 A→B matches by Jaccard:")
    for m in best_matches[:10]:
        print(f"  {m['a_folio']} → {m['best_b']}: {m['similarity']:.3f} (A has {m['a_pp_count']} PP, {m['high_match_count']} B folios >50% match)")

    # Check if matches are concentrated or dispersed
    print(f"\n=== Match Concentration ===")

    # For each A folio, how many B folios share ANY PP?
    any_overlap = []
    for i, a_fol in enumerate(a_folios):
        row = sim_matrix[i, :]
        count = np.sum(row > 0)
        any_overlap.append(count)

    print(f"Mean B folios with any PP overlap: {np.mean(any_overlap):.1f}")
    print(f"Min: {np.min(any_overlap)}, Max: {np.max(any_overlap)}")

    # Check if certain B folios are "hubs"
    print(f"\n=== B Folio Hub Analysis ===")
    b_hub_scores = []
    for j, b_fol in enumerate(b_folios):
        col = sim_matrix[:, j]
        mean_sim = col.mean()
        a_connections = np.sum(col > 0)
        b_hub_scores.append({
            'b_folio': b_fol,
            'mean_similarity': mean_sim,
            'a_connections': a_connections,
            'pp_count': len(b_folio_pp[b_fol])
        })

    b_hub_scores.sort(key=lambda x: x['mean_similarity'], reverse=True)
    print("\nTop 10 B 'hub' folios (highest mean similarity to A):")
    for h in b_hub_scores[:10]:
        print(f"  {h['b_folio']}: mean_sim={h['mean_similarity']:.3f}, connects to {h['a_connections']} A folios, has {h['pp_count']} PP")

    # Check for A-section → B-folio patterns
    print(f"\n=== Section Patterns ===")

    # Get A folio sections
    a_sections = {}
    for folio in a_folios:
        subset = df_a[df_a['folio'] == folio]
        if len(subset) > 0:
            a_sections[folio] = subset['section'].iloc[0]

    for section in ['H', 'P', 'T']:
        section_folios = [f for f in a_folios if a_sections.get(f) == section]
        if not section_folios:
            continue

        section_indices = [a_folios.index(f) for f in section_folios]
        section_sims = sim_matrix[section_indices, :]

        # Find most common best-match B folios for this section
        best_b_for_section = []
        for i in section_indices:
            best_idx = np.argmax(sim_matrix[i, :])
            best_b_for_section.append(b_folios[best_idx])

        from collections import Counter
        b_counts = Counter(best_b_for_section)
        top_b = b_counts.most_common(3)

        print(f"\nSection {section} ({len(section_folios)} folios):")
        print(f"  Mean similarity to B: {section_sims.mean():.3f}")
        print(f"  Top B matches: {top_b}")

    # Test: Is there signal above random?
    print(f"\n=== Permutation Test ===")

    # Observed: mean of max similarities per A folio
    observed_mean_max = np.mean([sim_matrix[i, :].max() for i in range(len(a_folios))])

    # Permutation baseline
    n_perms = 1000
    perm_means = []
    for _ in range(n_perms):
        # Shuffle B folio PP assignments
        shuffled_b_pp = list(b_folio_pp.values())
        np.random.shuffle(shuffled_b_pp)

        perm_sims = []
        for i, a_fol in enumerate(a_folios):
            a_pp = a_folio_pp[a_fol]
            max_sim = max(jaccard(a_pp, b_pp) for b_pp in shuffled_b_pp)
            perm_sims.append(max_sim)
        perm_means.append(np.mean(perm_sims))

    perm_mean = np.mean(perm_means)
    perm_std = np.std(perm_means)
    z_score = (observed_mean_max - perm_mean) / perm_std if perm_std > 0 else 0
    p_value = np.mean([p >= observed_mean_max for p in perm_means])

    print(f"Observed mean-max similarity: {observed_mean_max:.3f}")
    print(f"Permutation baseline: {perm_mean:.3f} ± {perm_std:.3f}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P-value: {p_value:.4f}")

    # Save results
    output = {
        'a_folios': len(a_folios),
        'b_folios': len(b_folios),
        'pp_vocabulary': len(pp_middles),
        'mean_similarity': float(sim_matrix.mean()),
        'max_similarity': float(sim_matrix.max()),
        'observed_mean_max': float(observed_mean_max),
        'permutation_baseline': float(perm_mean),
        'z_score': float(z_score),
        'p_value': float(p_value),
        'signal_detected': z_score > 2.0
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'pp_folio_correlation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== VERDICT ===")
    if z_score > 2.0:
        print(f"SIGNAL DETECTED: A→B PP correlation is above chance (z={z_score:.2f})")
        print("PP vocabulary may serve as a weak linkage key, but not 1:1 mapping")
    else:
        print(f"NO CLEAR SIGNAL: A→B PP correlation is at chance level (z={z_score:.2f})")
        print("PP alone doesn't determine B folio - need additional mechanism")
