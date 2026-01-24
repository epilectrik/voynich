#!/usr/bin/env python3
"""
Test 12: Superstring Compatibility Validation

Hypothesis: PP pairs that appear in the same RI superstring should be
compatible (co-occur in records) at elevated rates vs random PP pairs.

If superstring structure embeds compatibility proof, then:
- PP pairs from same superstring → high co-occurrence rate
- Random PP pairs → baseline co-occurrence rate (~4.3% per C475)
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import random

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction
PREFIXES = ['pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch', 'lsh',
            'ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'lk', 'yk',
            'ke', 'te', 'se', 'de', 'pe', 'so', 'ko', 'to', 'do', 'po',
            'sa', 'ka', 'ta', 'al', 'ar', 'or', 'o', 'd', 's', 'y', 'l', 'r', 'q', 'k', 't', 'p', 'f']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token).strip()
    if not token:
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


def find_pp_in_ri(ri, pp_list):
    """Find all PP atoms contained in RI."""
    found = []
    for pp in pp_list:
        if pp in ri:
            found.append(pp)
    return found


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    # Split A and B
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()

    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_b['middle'] = df_b['word'].apply(extract_middle)

    df_a = df_a[df_a['middle'].notna() & (df_a['middle'] != '')]
    df_b = df_b[df_b['middle'].notna() & (df_b['middle'] != '')]

    # Identify PP and RI
    a_middles = set(df_a['middle'].unique())
    b_middles = set(df_b['middle'].unique())
    pp_middles = a_middles & b_middles
    ri_middles = a_middles - b_middles

    # Only multi-char PP
    pp_list = sorted([pp for pp in pp_middles if len(pp) > 1], key=len, reverse=True)

    print(f"PP MIDDLEs (multi-char): {len(pp_list)}")
    print(f"RI MIDDLEs: {len(ri_middles)}")

    # Step 1: Extract PP pairs from superstrings
    superstring_pairs = set()
    for ri in ri_middles:
        pp_atoms = find_pp_in_ri(ri, pp_list)
        if len(pp_atoms) >= 2:
            for p1, p2 in combinations(pp_atoms, 2):
                pair = tuple(sorted([p1, p2]))
                superstring_pairs.add(pair)

    print(f"\nUnique PP pairs from superstrings: {len(superstring_pairs)}")

    # Step 2: Build actual co-occurrence from corpus
    # Check co-occurrence in A records (folio + line)
    record_middles = defaultdict(set)
    for _, row in df_a.iterrows():
        key = (row['folio'], row['line_number'])
        record_middles[key].add(row['middle'])

    # Also check co-occurrence in B (since PP is shared)
    for _, row in df_b.iterrows():
        key = (row['folio'], row['line_number'])
        record_middles[key].add(row['middle'])

    # Count actual co-occurrences
    actual_cooccur = set()
    for key, middles in record_middles.items():
        pp_in_record = [m for m in middles if m in pp_middles and len(m) > 1]
        if len(pp_in_record) >= 2:
            for p1, p2 in combinations(pp_in_record, 2):
                pair = tuple(sorted([p1, p2]))
                actual_cooccur.add(pair)

    print(f"PP pairs that actually co-occur in records: {len(actual_cooccur)}")

    # Step 3: Calculate rates
    # Total possible PP pairs
    total_possible = len(pp_list) * (len(pp_list) - 1) // 2
    print(f"Total possible PP pairs: {total_possible}")

    # Baseline: what fraction of all possible pairs actually co-occur?
    baseline_rate = len(actual_cooccur) / total_possible
    print(f"\nBaseline co-occurrence rate: {baseline_rate:.1%}")

    # Superstring pairs: what fraction actually co-occur?
    superstring_cooccur = superstring_pairs & actual_cooccur
    superstring_rate = len(superstring_cooccur) / len(superstring_pairs) if superstring_pairs else 0
    print(f"Superstring pair co-occurrence rate: {superstring_rate:.1%}")

    # Enrichment
    enrichment = superstring_rate / baseline_rate if baseline_rate > 0 else 0
    print(f"\nEnrichment: {enrichment:.1f}x above baseline")

    # Step 4: Statistical test - permutation
    print(f"\n=== Permutation Test ===")
    n_perms = 1000
    random.seed(42)

    perm_rates = []
    for _ in range(n_perms):
        # Sample same number of random PP pairs
        random_pairs = set()
        while len(random_pairs) < len(superstring_pairs):
            p1, p2 = random.sample(pp_list, 2)
            pair = tuple(sorted([p1, p2]))
            random_pairs.add(pair)

        # Check co-occurrence rate
        random_cooccur = random_pairs & actual_cooccur
        rate = len(random_cooccur) / len(random_pairs)
        perm_rates.append(rate)

    perm_mean = np.mean(perm_rates)
    perm_std = np.std(perm_rates)
    z_score = (superstring_rate - perm_mean) / perm_std if perm_std > 0 else 0
    p_value = np.mean([r >= superstring_rate for r in perm_rates])

    print(f"Observed rate: {superstring_rate:.1%}")
    print(f"Permutation baseline: {perm_mean:.1%} ± {perm_std:.1%}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P-value: {p_value:.4f}")

    # Step 5: Detailed analysis
    print(f"\n=== Detailed Analysis ===")

    # Which superstring pairs don't co-occur?
    non_cooccur = superstring_pairs - actual_cooccur
    print(f"Superstring pairs that DON'T co-occur: {len(non_cooccur)} ({100*len(non_cooccur)/len(superstring_pairs):.1f}%)")

    # Are these trivial overlaps (one contains the other)?
    trivial_pairs = set()
    for p1, p2 in superstring_pairs:
        if p1 in p2 or p2 in p1:
            trivial_pairs.add((p1, p2))

    print(f"Trivial pairs (one contains other): {len(trivial_pairs)}")

    # Non-trivial superstring pairs
    nontrivial_pairs = superstring_pairs - trivial_pairs
    nontrivial_cooccur = nontrivial_pairs & actual_cooccur
    nontrivial_rate = len(nontrivial_cooccur) / len(nontrivial_pairs) if nontrivial_pairs else 0
    print(f"\nNon-trivial superstring pairs: {len(nontrivial_pairs)}")
    print(f"Non-trivial co-occurrence rate: {nontrivial_rate:.1%}")
    print(f"Non-trivial enrichment: {nontrivial_rate / baseline_rate:.1f}x")

    # Save results
    output = {
        'pp_count': len(pp_list),
        'superstring_pairs': len(superstring_pairs),
        'actual_cooccur_pairs': len(actual_cooccur),
        'total_possible_pairs': total_possible,
        'baseline_rate': float(baseline_rate),
        'superstring_rate': float(superstring_rate),
        'enrichment': float(enrichment),
        'z_score': float(z_score),
        'p_value': float(p_value),
        'nontrivial_pairs': len(nontrivial_pairs),
        'nontrivial_rate': float(nontrivial_rate),
        'hypothesis_confirmed': z_score > 2.0 and enrichment > 1.5
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'superstring_compatibility.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== VERDICT ===")
    if z_score > 2.0 and enrichment > 1.5:
        print(f"COMPATIBILITY PROOF CONFIRMED: Superstring pairs co-occur at {enrichment:.1f}x baseline")
        print("PP atoms in the same superstring ARE more compatible than random pairs")
    else:
        print(f"WEAK OR NO SIGNAL: Enrichment {enrichment:.1f}x, z={z_score:.2f}")
