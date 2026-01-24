#!/usr/bin/env python3
"""
Test 14: Compatibility Enrichment by System

Prediction from expert:
- RI: Strong enrichment (~4.7x) - CONFIRMED
- PP track: Weak or null
- B: Near baseline (~1x)
- AZC: Near baseline or noisy

If B shows no enrichment, that confirms compatibility-certificate is RI-specific.
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


def find_subcomponents_in_token(token, vocab):
    """Find all vocabulary items contained in token."""
    found = []
    for v in vocab:
        if v in token:
            found.append(v)
    return found


def compute_enrichment(tokens, subcomponent_vocab, record_cooccurrences, all_possible_pairs):
    """
    Compute compatibility enrichment for a population.

    tokens: list of tokens to analyze
    subcomponent_vocab: vocabulary to look for as substrings
    record_cooccurrences: set of (v1, v2) pairs that actually co-occur in records
    all_possible_pairs: total number of possible pairs
    """
    # Get pairs from superstrings
    superstring_pairs = set()
    for token in tokens:
        components = find_subcomponents_in_token(token, subcomponent_vocab)
        if len(components) >= 2:
            for c1, c2 in combinations(components, 2):
                pair = tuple(sorted([c1, c2]))
                superstring_pairs.add(pair)

    if not superstring_pairs:
        return None

    # Calculate rates
    baseline_rate = len(record_cooccurrences) / all_possible_pairs

    superstring_cooccur = superstring_pairs & record_cooccurrences
    superstring_rate = len(superstring_cooccur) / len(superstring_pairs)

    enrichment = superstring_rate / baseline_rate if baseline_rate > 0 else 0

    return {
        'superstring_pairs': len(superstring_pairs),
        'superstring_cooccur': len(superstring_cooccur),
        'superstring_rate': superstring_rate,
        'baseline_rate': baseline_rate,
        'enrichment': enrichment
    }


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    df['middle'] = df['word'].apply(extract_middle)
    df = df[df['middle'].notna() & (df['middle'] != '')]

    # Split populations
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()
    df_azc = df[df['language'].isna()].copy()

    # Get vocabularies
    a_middles = set(df_a['middle'].unique())
    b_middles = set(df_b['middle'].unique())
    azc_middles = set(df_azc['middle'].unique())

    pp_middles = a_middles & b_middles
    ri_middles = a_middles - b_middles
    b_exclusive = b_middles - pp_middles

    # Multi-char only
    pp_list = sorted([p for p in pp_middles if len(p) > 1], key=len, reverse=True)

    print(f"=== Vocabularies ===")
    print(f"PP (multi-char): {len(pp_list)}")
    print(f"RI: {len(ri_middles)}")
    print(f"B-exclusive: {len(b_exclusive)}")
    print(f"AZC: {len(azc_middles)}")

    # Build co-occurrence sets for each system
    # A records
    a_record_middles = defaultdict(set)
    for _, row in df_a.iterrows():
        key = (row['folio'], row['line_number'])
        a_record_middles[key].add(row['middle'])

    a_cooccur = set()
    for key, middles in a_record_middles.items():
        pp_in_record = [m for m in middles if m in pp_list]
        for p1, p2 in combinations(pp_in_record, 2):
            a_cooccur.add(tuple(sorted([p1, p2])))

    # B records
    b_record_middles = defaultdict(set)
    for _, row in df_b.iterrows():
        key = (row['folio'], row['line_number'])
        b_record_middles[key].add(row['middle'])

    b_cooccur = set()
    for key, middles in b_record_middles.items():
        pp_in_record = [m for m in middles if m in pp_list]
        for p1, p2 in combinations(pp_in_record, 2):
            b_cooccur.add(tuple(sorted([p1, p2])))

    # AZC records
    azc_record_middles = defaultdict(set)
    for _, row in df_azc.iterrows():
        key = (row['folio'], row['line_number'])
        azc_record_middles[key].add(row['middle'])

    azc_cooccur = set()
    for key, middles in azc_record_middles.items():
        pp_in_record = [m for m in middles if m in pp_list]
        for p1, p2 in combinations(pp_in_record, 2):
            azc_cooccur.add(tuple(sorted([p1, p2])))

    # Total possible pairs
    total_possible = len(pp_list) * (len(pp_list) - 1) // 2

    print(f"\n=== Co-occurrence Baselines ===")
    print(f"A record co-occurrences: {len(a_cooccur)} ({100*len(a_cooccur)/total_possible:.1f}%)")
    print(f"B record co-occurrences: {len(b_cooccur)} ({100*len(b_cooccur)/total_possible:.1f}%)")
    print(f"AZC record co-occurrences: {len(azc_cooccur)} ({100*len(azc_cooccur)/total_possible:.1f}%)")

    # Compute enrichment for each population
    print(f"\n=== Enrichment Analysis ===\n")

    results = {}

    # RI (using A co-occurrences as ground truth)
    ri_result = compute_enrichment(list(ri_middles), pp_list, a_cooccur, total_possible)
    if ri_result:
        print(f"RI (A-exclusive):")
        print(f"  Superstring pairs: {ri_result['superstring_pairs']}")
        print(f"  Co-occur rate: {ri_result['superstring_rate']:.1%}")
        print(f"  Baseline: {ri_result['baseline_rate']:.1%}")
        print(f"  ENRICHMENT: {ri_result['enrichment']:.1f}x")
        results['RI'] = ri_result

    # B-exclusive (using B co-occurrences as ground truth)
    b_result = compute_enrichment(list(b_exclusive), pp_list, b_cooccur, total_possible)
    if b_result:
        print(f"\nB-exclusive:")
        print(f"  Superstring pairs: {b_result['superstring_pairs']}")
        print(f"  Co-occur rate: {b_result['superstring_rate']:.1%}")
        print(f"  Baseline: {b_result['baseline_rate']:.1%}")
        print(f"  ENRICHMENT: {b_result['enrichment']:.1f}x")
        results['B-exclusive'] = b_result

    # AZC (using AZC co-occurrences as ground truth)
    azc_result = compute_enrichment(list(azc_middles), pp_list, azc_cooccur, total_possible)
    if azc_result:
        print(f"\nAZC:")
        print(f"  Superstring pairs: {azc_result['superstring_pairs']}")
        print(f"  Co-occur rate: {azc_result['superstring_rate']:.1%}")
        print(f"  Baseline: {azc_result['baseline_rate']:.1%}")
        print(f"  ENRICHMENT: {azc_result['enrichment']:.1f}x")
        results['AZC'] = azc_result

    # PP itself (using combined A+B co-occurrences)
    combined_cooccur = a_cooccur | b_cooccur
    pp_result = compute_enrichment(list(pp_middles), pp_list, combined_cooccur, total_possible)
    if pp_result:
        print(f"\nPP (shared vocabulary):")
        print(f"  Superstring pairs: {pp_result['superstring_pairs']}")
        print(f"  Co-occur rate: {pp_result['superstring_rate']:.1%}")
        print(f"  Baseline: {pp_result['baseline_rate']:.1%}")
        print(f"  ENRICHMENT: {pp_result['enrichment']:.1f}x")
        results['PP'] = pp_result

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {k: {kk: float(vv) if isinstance(vv, (np.floating, float)) else vv
                  for kk, vv in v.items()}
              for k, v in results.items()}
    with open(RESULTS_DIR / 'enrichment_by_system.json', 'w') as f:
        json.dump(output, f, indent=2)

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"{'System':<15} {'Enrichment':<12} {'Prediction':<15} {'Match?'}")
    print("-" * 55)

    predictions = {
        'RI': ('~4-5x', lambda x: x > 3.0),
        'B-exclusive': ('~1x', lambda x: x < 2.0),
        'AZC': ('~1x', lambda x: x < 2.0),
        'PP': ('weak/null', lambda x: x < 3.0)
    }

    for system, result in results.items():
        pred, check = predictions.get(system, ('?', lambda x: True))
        enrichment = result['enrichment']
        match = "✓" if check(enrichment) else "✗"
        print(f"{system:<15} {enrichment:<12.1f}x {pred:<15} {match}")

    print(f"\n=== VERDICT ===")
    ri_enrich = results.get('RI', {}).get('enrichment', 0)
    b_enrich = results.get('B-exclusive', {}).get('enrichment', 0)

    if ri_enrich > 3.0 and b_enrich < 2.0:
        print("PREDICTION CONFIRMED: Compatibility enrichment is RI-SPECIFIC")
        print("Superstring compression is global SUBSTRATE")
        print("Compatibility certificate is RI-specific FUNCTION")
    elif b_enrich > 3.0:
        print("WARNING: B shows unexpected enrichment - needs investigation")
    else:
        print("Mixed results - see details above")
