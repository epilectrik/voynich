#!/usr/bin/env python3
"""
Test 11: PP Overlap Structure within RI

Question: When RI contains multiple PP atoms, do they overlap (share letters)?

Example: "olsheeos"
- "shee" at positions 2-5
- "eos" at positions 4-6
- They SHARE the 'e' at position 4

This would mean RI is a compressed/overlapping encoding, not concatenation.
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
    """Find all start positions of needle in haystack."""
    positions = []
    start = 0
    while True:
        pos = haystack.find(needle, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def analyze_overlap(ri, pp_list):
    """
    Analyze how PP atoms are arranged within RI.
    Returns coverage map and overlap statistics.
    """
    # Find all positions of each PP in the RI
    pp_positions = {}
    for pp in pp_list:
        if len(pp) > 1:  # Only multi-char PP
            positions = find_all_occurrences(ri, pp)
            if positions:
                pp_positions[pp] = positions

    if not pp_positions:
        return None

    # Build coverage map: which positions are covered by which PP
    coverage = [[] for _ in range(len(ri))]
    for pp, positions in pp_positions.items():
        for start in positions:
            for i in range(start, start + len(pp)):
                if i < len(ri):
                    coverage[i].append(pp)

    # Count overlaps (positions covered by 2+ PP)
    overlap_positions = sum(1 for c in coverage if len(c) > 1)
    covered_positions = sum(1 for c in coverage if len(c) > 0)

    # Calculate total PP character usage
    total_pp_chars = sum(len(pp) * len(positions) for pp, positions in pp_positions.items())

    return {
        'ri': ri,
        'ri_len': len(ri),
        'pp_count': len(pp_positions),
        'covered_positions': covered_positions,
        'overlap_positions': overlap_positions,
        'total_pp_chars': total_pp_chars,
        'coverage_ratio': covered_positions / len(ri) if len(ri) > 0 else 0,
        'overlap_ratio': overlap_positions / len(ri) if len(ri) > 0 else 0,
        'compression_ratio': total_pp_chars / len(ri) if len(ri) > 0 else 0,
        'pp_atoms': list(pp_positions.keys())
    }


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

    pp_list = sorted([pp for pp in pp_middles if len(pp) > 1], key=len, reverse=True)

    print(f"PP MIDDLEs (multi-char): {len(pp_list)}")
    print(f"RI MIDDLEs: {len(ri_middles)}")

    # Analyze each RI
    results = []
    for ri in ri_middles:
        analysis = analyze_overlap(ri, pp_list)
        if analysis:
            results.append(analysis)

    print(f"\nRI with PP coverage: {len(results)}")

    # Summary statistics
    overlap_ratios = [r['overlap_ratio'] for r in results]
    coverage_ratios = [r['coverage_ratio'] for r in results]
    compression_ratios = [r['compression_ratio'] for r in results]

    print(f"\n=== Overlap Analysis ===")
    print(f"Mean overlap ratio: {np.mean(overlap_ratios):.1%}")
    print(f"Mean coverage ratio: {np.mean(coverage_ratios):.1%}")
    print(f"Mean compression ratio: {np.mean(compression_ratios):.2f}x")

    # RI with significant overlap
    high_overlap = [r for r in results if r['overlap_ratio'] > 0.3]
    print(f"\nRI with >30% overlap: {len(high_overlap)} ({100*len(high_overlap)/len(results):.1f}%)")

    # Examples of high overlap
    print(f"\n=== High Overlap Examples ===")
    high_overlap.sort(key=lambda x: x['overlap_ratio'], reverse=True)
    for r in high_overlap[:10]:
        print(f"\n  '{r['ri']}' (len={r['ri_len']})")
        print(f"    PP atoms: {r['pp_atoms'][:5]}...")
        print(f"    Overlap: {r['overlap_ratio']:.0%} ({r['overlap_positions']}/{r['ri_len']} positions)")
        print(f"    Compression: {r['compression_ratio']:.1f}x")

    # Is overlap correlated with RI length?
    print(f"\n=== Overlap vs Length ===")
    from scipy.stats import spearmanr
    lengths = [r['ri_len'] for r in results]
    rho, p = spearmanr(lengths, overlap_ratios)
    print(f"Spearman (length vs overlap): rho={rho:.3f}, p={p:.4f}")

    # Compression analysis
    print(f"\n=== Compression Analysis ===")
    print(f"If PP atoms were concatenated (no overlap):")
    print(f"  Mean total PP chars: {np.mean([r['total_pp_chars'] for r in results]):.1f}")
    print(f"  Mean RI length: {np.mean([r['ri_len'] for r in results]):.1f}")
    print(f"  Compression ratio: {np.mean(compression_ratios):.2f}x")
    print(f"\nThis means PP atoms are 'packed' with {100*(np.mean(compression_ratios)-1):.0f}% character sharing")

    # What letters are most often shared?
    print(f"\n=== Shared Letter Analysis ===")
    shared_letters = Counter()
    for r in results:
        ri = r['ri']
        pp_positions = {}
        for pp in r['pp_atoms']:
            for pos in find_all_occurrences(ri, pp):
                for i in range(pos, pos + len(pp)):
                    if i < len(ri):
                        if i not in pp_positions:
                            pp_positions[i] = []
                        pp_positions[i].append(pp)

        # Count shared positions
        for i, pps in pp_positions.items():
            if len(pps) > 1:
                shared_letters[ri[i]] += 1

    print("Most shared letters:")
    for letter, count in shared_letters.most_common(10):
        print(f"  '{letter}': {count}")

    # Save results
    output = {
        'ri_analyzed': len(results),
        'mean_overlap_ratio': float(np.mean(overlap_ratios)),
        'mean_coverage_ratio': float(np.mean(coverage_ratios)),
        'mean_compression_ratio': float(np.mean(compression_ratios)),
        'high_overlap_count': len(high_overlap),
        'length_overlap_correlation': {'rho': float(rho), 'p': float(p)},
        'most_shared_letters': shared_letters.most_common(10)
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'pp_overlap_structure.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== VERDICT ===")
    if np.mean(overlap_ratios) > 0.1:
        print(f"OVERLAPPING STRUCTURE CONFIRMED: {np.mean(overlap_ratios):.0%} of positions are shared")
        print("RI is a COMPRESSED encoding where PP atoms share letters")
    else:
        print("CONCATENATIVE STRUCTURE: PP atoms don't significantly overlap")
