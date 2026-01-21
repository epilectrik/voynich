#!/usr/bin/env python3
"""
A_SECTION_T_CHARACTERIZATION - Test B & Vocabulary Overlap

Test B: Permutation test - is 0/83 B presence statistically anomalous?
Vocabulary Overlap: Do Section T MIDDLEs have ANY overlap with B vocabulary?

OPTIMIZED: Pre-compute all MIDDLE sets before permutation loop.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
import random

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
RESULTS_PATH = PROJECT_ROOT / 'phases' / 'A_SECTION_T_CHARACTERIZATION' / 'results'

SECTION_T_A_FOLIOS = ['f1r', 'f58r', 'f58v']

AZC_FOLIOS = ['f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
              'f68v1', 'f68v2', 'f68v3', 'f69r1', 'f69r2', 'f69v1', 'f69v2',
              'f70r1', 'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1',
              'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]


def extract_middle(token):
    """Extract MIDDLE from token."""
    if pd.isna(token):
        return None
    token = str(token)

    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None

    remainder = token[len(prefix):]

    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder

    if middle == '':
        middle = '_EMPTY_'

    return middle


def main():
    print("=" * 70)
    print("TEST B: PERMUTATION TEST & VOCABULARY OVERLAP")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H'].copy()
    df['middle'] = df['word'].apply(extract_middle)

    # Get corpora
    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']
    df_azc = df[df['folio'].isin(AZC_FOLIOS)]
    df_t = df_a[df_a['folio'].isin(SECTION_T_A_FOLIOS)]

    # Get MIDDLE sets
    t_middles = set(df_t['middle'].dropna().unique())
    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    azc_middles = set(df_azc['middle'].dropna().unique())

    print(f"Section T unique MIDDLEs: {len(t_middles)}")
    print(f"All A unique MIDDLEs: {len(a_middles)}")
    print(f"All B unique MIDDLEs: {len(b_middles)}")
    print()

    # PRE-COMPUTE: MIDDLE sets for each B folio (O(n) instead of O(n*m))
    print("Pre-computing B folio MIDDLE sets...")
    b_folios = df_b['folio'].unique()
    b_folio_middles = {}
    for folio in b_folios:
        b_folio_middles[folio] = set(df_b[df_b['folio'] == folio]['middle'].dropna().unique())
    print(f"Pre-computed {len(b_folio_middles)} B folio MIDDLE sets")
    print()

    # =========================================================================
    # VOCABULARY OVERLAP CHECK
    # =========================================================================
    print("=" * 70)
    print("VOCABULARY OVERLAP CHECK")
    print("=" * 70)
    print()

    # Do T MIDDLEs overlap with B?
    t_in_b = t_middles & b_middles
    t_not_in_b = t_middles - b_middles

    print(f"Section T MIDDLEs that ALSO appear in B: {len(t_in_b)} / {len(t_middles)} ({len(t_in_b)/len(t_middles)*100:.1f}%)")
    print(f"Section T MIDDLEs EXCLUSIVE to A: {len(t_not_in_b)} / {len(t_middles)} ({len(t_not_in_b)/len(t_middles)*100:.1f}%)")
    print()

    if t_in_b:
        print("Section T MIDDLEs that appear in BOTH A and B:")
        for mid in sorted(t_in_b)[:20]:
            b_folios_count = sum(1 for fm in b_folio_middles.values() if mid in fm)
            b_tokens = len(df_b[df_b['middle'] == mid])
            t_tokens = len(df_t[df_t['middle'] == mid])
            print(f"  {mid}: T={t_tokens}, B={b_tokens} tokens across {b_folios_count} B folios")
        if len(t_in_b) > 20:
            print(f"  ... and {len(t_in_b) - 20} more")
        print()

    # Compare to baseline
    a_in_b = a_middles & b_middles
    baseline_overlap = len(a_in_b) / len(a_middles) * 100
    t_overlap = len(t_in_b) / len(t_middles) * 100

    print(f"Baseline (all A MIDDLEs in B): {len(a_in_b)} / {len(a_middles)} ({baseline_overlap:.1f}%)")
    print(f"Section T MIDDLEs in B: {len(t_in_b)} / {len(t_middles)} ({t_overlap:.1f}%)")
    print()

    # =========================================================================
    # B FOLIO PRESENCE CHECK
    # =========================================================================
    print("=" * 70)
    print("B FOLIO PRESENCE CHECK")
    print("=" * 70)
    print()

    # Count B folios containing at least one T MIDDLE
    b_folios_with_t = [f for f, mids in b_folio_middles.items() if mids & t_middles]

    print(f"B folios containing ANY Section T MIDDLE: {len(b_folios_with_t)} / {len(b_folios)}")

    if b_folios_with_t:
        print("B folios with Section T MIDDLEs:")
        for folio in sorted(b_folios_with_t)[:10]:
            overlap = b_folio_middles[folio] & t_middles
            print(f"  {folio}: {sorted(overlap)[:5]}")
    else:
        print("CONFIRMED: Zero B folios contain any Section T MIDDLE")
    print()

    # =========================================================================
    # PERMUTATION TEST (OPTIMIZED)
    # =========================================================================
    print("=" * 70)
    print("PERMUTATION TEST")
    print("=" * 70)
    print()

    n_permutations = 10000
    n_sample = len(t_middles)

    # Pool of A MIDDLEs to sample from
    non_t_a_middles = list(a_middles - t_middles)
    print(f"Sampling {n_sample} MIDDLEs from {len(non_t_a_middles)} non-T A MIDDLEs")
    print(f"Running {n_permutations:,} permutations...")

    zero_b_count = 0
    b_folio_counts = []

    random.seed(42)
    for i in range(n_permutations):
        sample = set(random.sample(non_t_a_middles, min(n_sample, len(non_t_a_middles))))

        # Count B folios containing any sample MIDDLE (using pre-computed sets)
        count = sum(1 for mids in b_folio_middles.values() if mids & sample)

        b_folio_counts.append(count)
        if count == 0:
            zero_b_count += 1

        if (i + 1) % 2000 == 0:
            print(f"  {i+1:,} / {n_permutations:,} done...")

    b_folio_counts = np.array(b_folio_counts)

    print()
    print(f"Permutation results:")
    print(f"  Mean B folios: {np.mean(b_folio_counts):.1f}")
    print(f"  Median B folios: {np.median(b_folio_counts):.0f}")
    print(f"  Min B folios: {np.min(b_folio_counts)}")
    print(f"  Max B folios: {np.max(b_folio_counts)}")
    print()

    print(f"  Permutations with 0 B folios: {zero_b_count} / {n_permutations}")

    p_value = zero_b_count / n_permutations
    if zero_b_count == 0:
        print(f"  P-VALUE: < {1/n_permutations:.4f} (none observed in {n_permutations:,} trials)")
    else:
        print(f"  P-VALUE: {p_value:.4f}")
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    print(f"Section T MIDDLEs overlapping with B vocabulary: {len(t_in_b)} ({t_overlap:.1f}%)")
    print(f"B folios with any T MIDDLE: {len(b_folios_with_t)} / {len(b_folios)}")
    print(f"Permutation p-value: {'< 0.0001' if zero_b_count == 0 else f'{p_value:.4f}'}")
    print()

    if len(b_folios_with_t) == 0 and zero_b_count == 0:
        conclusion = "HIGHLY_ANOMALOUS"
        explanation = "Section T's 0% B folio presence NEVER occurred in 10,000 random samples. This is statistically extraordinary."
    elif len(b_folios_with_t) == 0 and p_value < 0.01:
        conclusion = "STATISTICALLY_ANOMALOUS"
        explanation = f"Section T's 0% B presence occurred only {zero_b_count} times in 10,000 trials (p={p_value:.4f})."
    else:
        conclusion = "WITHIN_EXPECTATIONS"
        explanation = "Section T's B presence is within random expectations."

    print(f"CONCLUSION: {conclusion}")
    print(f"  {explanation}")

    # Save results
    results = {
        'vocabulary_overlap': {
            't_in_b_count': len(t_in_b),
            't_in_b_list': sorted(list(t_in_b)),
            't_in_b_pct': t_overlap,
            'baseline_overlap_pct': baseline_overlap,
        },
        'b_folio_presence': {
            'b_folios_with_t': len(b_folios_with_t),
            'total_b_folios': len(b_folios),
        },
        'permutation_test': {
            'n_permutations': n_permutations,
            'mean_b_folios': float(np.mean(b_folio_counts)),
            'median_b_folios': float(np.median(b_folio_counts)),
            'min_b_folios': int(np.min(b_folio_counts)),
            'zero_count': zero_b_count,
            'p_value': p_value if zero_b_count > 0 else 0.0001,
        },
        'conclusion': conclusion,
        'explanation': explanation,
    }

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH / 'permutation_and_overlap.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_PATH / 'permutation_and_overlap.json'}")


if __name__ == '__main__':
    main()
