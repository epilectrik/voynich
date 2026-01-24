#!/usr/bin/env python3
"""
Test 7: Local vs Global RI Composition by Length

Hypothesis: Locally-derived RI (contains PP from same record) is shorter than
globally-composed RI (uses PP from outside the record).

Per C498.d, length predicts complexity. If local derivation is "intra-category
refinement" and global composition is "inter-category discrimination", we'd
expect:
- Short RI: enriched for local derivation
- Long RI: enriched for global composition
"""

import pandas as pd
import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction (from test1)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE from token."""
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


def get_section(folio):
    """Get section from folio."""
    if pd.isna(folio):
        return 'H'
    folio = str(folio)
    if folio.startswith(('f99', 'f100', 'f101', 'f102', 'f103')):
        return 'P'
    if folio.startswith(('f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84')):
        return 'T'
    return 'H'


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Filter to Currier A
    df_a = df[df['language'] == 'A'].copy()
    df_a = df_a[~df_a['placement'].str.startswith('L', na=False)]
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_a = df_a[df_a['middle'].notna() & (df_a['middle'] != '')]

    # Get B tokens
    df_b = df[df['language'] == 'B'].copy()
    df_b = df_b[~df_b['placement'].str.startswith('L', na=False)]
    df_b['middle'] = df_b['word'].apply(extract_middle)
    df_b = df_b[df_b['middle'].notna() & (df_b['middle'] != '')]

    # PP = A ∩ B, RI = A-only
    a_middles = set(df_a['middle'].unique())
    b_middles = set(df_b['middle'].unique())
    pp_middles = a_middles & b_middles
    ri_middles = a_middles - b_middles

    # Only consider multi-char PP for meaningful matches
    pp_multi = {pp for pp in pp_middles if len(pp) > 1}

    print(f"PP MIDDLEs: {len(pp_middles)} ({len(pp_multi)} multi-char)")
    print(f"RI MIDDLEs: {len(ri_middles)}")

    # Build record structure: folio -> line -> set of MIDDLEs
    records = defaultdict(lambda: defaultdict(set))
    for _, row in df_a.iterrows():
        folio = row['folio']
        line = row['line_number']
        middle = row['middle']
        records[folio][line].add(middle)

    # For each RI token occurrence, check if it contains any PP from the same record
    results = []

    for _, row in df_a.iterrows():
        middle = row['middle']
        if middle not in ri_middles:
            continue  # Only analyze RI

        folio = row['folio']
        line = row['line_number']
        section = row.get('section', 'H')

        # Get PP MIDDLEs in the same record (folio + line)
        record_middles = records[folio][line]
        record_pp = record_middles & pp_multi

        # Check if RI contains any PP from the same record
        is_local = False
        matching_pp = None
        for pp in record_pp:
            if pp in middle:  # Substring match
                is_local = True
                matching_pp = pp
                break

        results.append({
            'middle': middle,
            'length': len(middle),
            'folio': folio,
            'line': line,
            'section': section,
            'is_local': is_local,
            'matching_pp': matching_pp
        })

    results_df = pd.DataFrame(results)

    print(f"\nTotal RI occurrences analyzed: {len(results_df)}")
    print(f"Locally-derived: {results_df['is_local'].sum()} ({100*results_df['is_local'].mean():.1f}%)")
    print(f"Globally-composed: {(~results_df['is_local']).sum()} ({100*(~results_df['is_local']).mean():.1f}%)")

    # Compare lengths
    local_df = results_df[results_df['is_local']]
    global_df = results_df[~results_df['is_local']]

    print(f"\n=== Length Comparison ===")
    print(f"Locally-derived mean length: {local_df['length'].mean():.2f}")
    print(f"Globally-composed mean length: {global_df['length'].mean():.2f}")
    print(f"Difference: {global_df['length'].mean() - local_df['length'].mean():.2f}")

    # Statistical test
    from scipy.stats import mannwhitneyu
    stat, pval = mannwhitneyu(local_df['length'], global_df['length'], alternative='less')
    print(f"\nMann-Whitney U (local < global): U={stat:.0f}, p={pval:.4f}")

    # Enrichment by length bin
    print("\n=== Local Derivation Rate by Length ===")
    for length in sorted(results_df['length'].unique()):
        subset = results_df[results_df['length'] == length]
        if len(subset) >= 10:  # Only show meaningful bins
            local_rate = subset['is_local'].mean()
            print(f"Length {length}: {100*local_rate:.1f}% local ({len(subset)} tokens)")

    # Section breakdown
    print("\n=== By Section ===")
    for section in ['H', 'P', 'T']:
        subset = results_df[results_df['section'] == section]
        if len(subset) > 0:
            local_rate = subset['is_local'].mean()
            local_len = subset[subset['is_local']]['length'].mean() if subset['is_local'].any() else 0
            global_len = subset[~subset['is_local']]['length'].mean() if (~subset['is_local']).any() else 0
            print(f"{section}: {100*local_rate:.1f}% local | local_len={local_len:.2f}, global_len={global_len:.2f}")

    # Check correlation: length vs local rate by unique RI type (not occurrence)
    print("\n=== By Unique RI Type ===")
    ri_types = results_df.groupby('middle').agg({
        'length': 'first',
        'is_local': ['mean', 'sum', 'count']
    }).reset_index()
    ri_types.columns = ['middle', 'length', 'local_rate', 'local_count', 'total_count']

    # Correlation
    from scipy.stats import spearmanr
    rho, p_corr = spearmanr(ri_types['length'], ri_types['local_rate'])
    print(f"Spearman correlation (length vs local_rate): rho={rho:.3f}, p={p_corr:.4f}")

    # Save results
    output = {
        'total_ri_occurrences': int(len(results_df)),
        'locally_derived': {
            'count': int(local_df.shape[0]),
            'percentage': float(100 * local_df.shape[0] / len(results_df)),
            'mean_length': float(local_df['length'].mean())
        },
        'globally_composed': {
            'count': int(global_df.shape[0]),
            'percentage': float(100 * global_df.shape[0] / len(results_df)),
            'mean_length': float(global_df['length'].mean())
        },
        'length_difference': float(global_df['length'].mean() - local_df['length'].mean()),
        'mann_whitney_p': float(pval),
        'spearman_rho': float(rho),
        'spearman_p': float(p_corr),
        'hypothesis_confirmed': bool(pval < 0.05 and local_df['length'].mean() < global_df['length'].mean())
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'local_vs_global_length.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== VERDICT ===")
    if output['hypothesis_confirmed']:
        print("CONFIRMED: Locally-derived RI is significantly shorter than globally-composed RI")
    else:
        if local_df['length'].mean() < global_df['length'].mean():
            print("TREND: Locally-derived RI is shorter, but NOT significant (p > 0.05)")
        else:
            print("NOT CONFIRMED: No length difference in expected direction")
