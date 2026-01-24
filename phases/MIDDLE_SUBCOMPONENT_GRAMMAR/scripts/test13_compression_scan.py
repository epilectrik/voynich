#!/usr/bin/env python3
"""
Test 13: Compression Pattern Scan

Question: Does the superstring compression pattern exist elsewhere?
- Currier A (RI) - already confirmed
- Currier B MIDDLEs
- AZC tokens

Method: Check overlap ratio within each population using their own
sub-component vocabulary.
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


def find_all_occurrences(haystack, needle):
    positions = []
    start = 0
    while True:
        pos = haystack.find(needle, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def analyze_overlap_for_population(tokens, subcomponent_vocab):
    """
    Analyze overlap structure for a population of tokens
    using a given sub-component vocabulary.
    """
    results = []

    # Sort vocab by length (longest first) for matching
    vocab = sorted([v for v in subcomponent_vocab if len(v) > 1], key=len, reverse=True)

    for token in tokens:
        if len(token) < 2:
            continue

        # Find all sub-components in this token
        coverage = [0] * len(token)  # Count how many sub-components cover each position

        for v in vocab:
            for pos in find_all_occurrences(token, v):
                for i in range(pos, min(pos + len(v), len(token))):
                    coverage[i] += 1

        covered = sum(1 for c in coverage if c > 0)
        overlapped = sum(1 for c in coverage if c > 1)
        total_matches = sum(coverage)

        if covered > 0:
            results.append({
                'token': token,
                'length': len(token),
                'covered': covered,
                'overlapped': overlapped,
                'coverage_ratio': covered / len(token),
                'overlap_ratio': overlapped / len(token),
                'compression_ratio': total_matches / len(token) if len(token) > 0 else 0
            })

    return results


if __name__ == '__main__':
    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    # Split populations
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()
    df_azc = df[df['language'].isna()].copy()  # AZC has NA language

    # Extract MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_b['middle'] = df_b['word'].apply(extract_middle)
    df_azc['middle'] = df_azc['word'].apply(extract_middle)

    # Get unique MIDDLEs
    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())
    azc_middles = set(df_azc['middle'].dropna().unique())

    # Define sub-component vocabularies
    pp_middles = a_middles & b_middles  # Shared vocabulary
    ri_middles = a_middles - b_middles  # A-exclusive

    print(f"=== Population Sizes ===")
    print(f"A MIDDLEs: {len(a_middles)} (PP: {len(pp_middles)}, RI: {len(ri_middles)})")
    print(f"B MIDDLEs: {len(b_middles)}")
    print(f"AZC MIDDLEs: {len(azc_middles)}")

    # For each population, analyze overlap using PP vocabulary
    print(f"\n=== Overlap Analysis (using PP vocabulary as sub-components) ===\n")

    populations = {
        'RI (A-exclusive)': list(ri_middles),
        'PP (A∩B shared)': list(pp_middles),
        'B-exclusive': list(b_middles - pp_middles),
        'AZC': list(azc_middles)
    }

    results_summary = {}

    for name, tokens in populations.items():
        if not tokens:
            print(f"{name}: No tokens")
            continue

        # Use PP as the sub-component vocabulary for all populations
        results = analyze_overlap_for_population(tokens, pp_middles)

        if not results:
            print(f"{name}: No analyzable tokens")
            continue

        overlap_ratios = [r['overlap_ratio'] for r in results]
        coverage_ratios = [r['coverage_ratio'] for r in results]
        compression_ratios = [r['compression_ratio'] for r in results]

        mean_overlap = np.mean(overlap_ratios)
        mean_coverage = np.mean(coverage_ratios)
        mean_compression = np.mean(compression_ratios)
        high_overlap = sum(1 for r in overlap_ratios if r > 0.3)

        print(f"{name}:")
        print(f"  Tokens analyzed: {len(results)}")
        print(f"  Mean coverage (by PP): {mean_coverage:.1%}")
        print(f"  Mean overlap ratio: {mean_overlap:.1%}")
        print(f"  Mean compression: {mean_compression:.2f}x")
        print(f"  High overlap (>30%): {high_overlap} ({100*high_overlap/len(results):.1f}%)")
        print()

        results_summary[name] = {
            'count': len(results),
            'mean_coverage': float(mean_coverage),
            'mean_overlap': float(mean_overlap),
            'mean_compression': float(mean_compression),
            'high_overlap_pct': float(100 * high_overlap / len(results))
        }

    # Now analyze B using B's own internal vocabulary
    print(f"=== B-Internal Analysis (using B vocabulary as sub-components) ===\n")

    # Build B sub-component vocabulary from frequent substrings
    b_tokens = list(b_middles)
    b_bigrams = Counter()
    b_trigrams = Counter()
    for t in b_tokens:
        for i in range(len(t) - 1):
            b_bigrams[t[i:i+2]] += 1
        for i in range(len(t) - 2):
            b_trigrams[t[i:i+3]] += 1

    # Take frequent ones as sub-components
    b_subcomponents = set()
    for bg, count in b_bigrams.items():
        if count >= 20:
            b_subcomponents.add(bg)
    for tg, count in b_trigrams.items():
        if count >= 10:
            b_subcomponents.add(tg)

    print(f"B sub-components (freq>=20 bigrams, >=10 trigrams): {len(b_subcomponents)}")

    b_results = analyze_overlap_for_population(b_tokens, b_subcomponents)
    if b_results:
        b_overlap = [r['overlap_ratio'] for r in b_results]
        b_coverage = [r['coverage_ratio'] for r in b_results]
        b_compression = [r['compression_ratio'] for r in b_results]

        print(f"B (self-analysis):")
        print(f"  Tokens analyzed: {len(b_results)}")
        print(f"  Mean coverage: {np.mean(b_coverage):.1%}")
        print(f"  Mean overlap: {np.mean(b_overlap):.1%}")
        print(f"  Mean compression: {np.mean(b_compression):.2f}x")
        print(f"  High overlap (>30%): {sum(1 for r in b_overlap if r > 0.3)} ({100*sum(1 for r in b_overlap if r > 0.3)/len(b_results):.1f}%)")

        results_summary['B-self'] = {
            'count': len(b_results),
            'mean_coverage': float(np.mean(b_coverage)),
            'mean_overlap': float(np.mean(b_overlap)),
            'mean_compression': float(np.mean(b_compression)),
            'high_overlap_pct': float(100 * sum(1 for r in b_overlap if r > 0.3) / len(b_results))
        }

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'compression_scan.json', 'w') as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n=== COMPARISON ===")
    print(f"{'Population':<20} {'Coverage':<12} {'Overlap':<12} {'Compression':<12}")
    print("-" * 56)
    for name, stats in results_summary.items():
        print(f"{name:<20} {stats['mean_coverage']:.1%}        {stats['mean_overlap']:.1%}        {stats['mean_compression']:.2f}x")

    print(f"\n=== VERDICT ===")
    ri_overlap = results_summary.get('RI (A-exclusive)', {}).get('mean_overlap', 0)
    b_overlap = results_summary.get('B-exclusive', {}).get('mean_overlap', 0)
    azc_overlap = results_summary.get('AZC', {}).get('mean_overlap', 0)

    if ri_overlap > 0.5 and b_overlap < 0.3:
        print("SUPERSTRING COMPRESSION IS RI-SPECIFIC")
        print(f"  RI: {ri_overlap:.0%} overlap")
        print(f"  B: {b_overlap:.0%} overlap")
        print("The compression pattern is unique to the A registry layer")
    elif b_overlap > 0.3:
        print("COMPRESSION PATTERN ALSO EXISTS IN B")
        print("Further investigation needed")
    else:
        print("Mixed results - see details above")
