#!/usr/bin/env python3
"""
Test 10: RI to PP Collapse Analysis

Question: Do ~1,290 RI MIDDLEs collapse to ~90 PP base classes?

Method:
1. For each RI MIDDLE, find which PP MIDDLE(s) it contains
2. Count how many RI variations map to each PP base
3. Check if this produces a tractable number of "material classes"
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

    # Only consider multi-char PP for meaningful matching
    pp_multi = sorted([pp for pp in pp_middles if len(pp) > 1], key=len, reverse=True)

    print(f"PP MIDDLEs (multi-char): {len(pp_multi)}")
    print(f"RI MIDDLEs: {len(ri_middles)}")

    # For each RI, find ALL PP it contains (longest match first)
    ri_to_pp = {}
    ri_to_all_pp = defaultdict(list)

    for ri in ri_middles:
        matches = []
        for pp in pp_multi:
            if pp in ri:
                matches.append(pp)

        ri_to_all_pp[ri] = matches

        # Primary PP = longest match
        if matches:
            ri_to_pp[ri] = max(matches, key=len)
        else:
            ri_to_pp[ri] = None

    # Count RI with PP match
    ri_with_pp = sum(1 for pp in ri_to_pp.values() if pp is not None)
    print(f"\nRI with PP match: {ri_with_pp} ({100*ri_with_pp/len(ri_middles):.1f}%)")
    print(f"RI without PP match: {len(ri_middles) - ri_with_pp}")

    # Count RI per PP base
    pp_to_ri = defaultdict(list)
    for ri, pp in ri_to_pp.items():
        if pp:
            pp_to_ri[pp].append(ri)

    print(f"\n=== PP Base Classes ===")
    print(f"PP bases with RI variations: {len(pp_to_ri)}")

    # Distribution of RI per PP
    ri_counts = [len(ris) for ris in pp_to_ri.values()]
    print(f"\nRI per PP base:")
    print(f"  Mean: {np.mean(ri_counts):.1f}")
    print(f"  Median: {np.median(ri_counts):.1f}")
    print(f"  Max: {np.max(ri_counts)}")
    print(f"  Min: {np.min(ri_counts)}")

    # Top PP bases by RI count
    print(f"\nTop 15 PP bases by RI variation count:")
    sorted_pp = sorted(pp_to_ri.items(), key=lambda x: len(x[1]), reverse=True)
    for pp, ris in sorted_pp[:15]:
        examples = ris[:3]
        print(f"  '{pp}' ({len(ris)} RI): {examples}...")

    # Check for RI with multiple PP matches
    multi_pp_ri = [(ri, pps) for ri, pps in ri_to_all_pp.items() if len(pps) > 1]
    print(f"\n=== RI with Multiple PP Matches ===")
    print(f"RI containing multiple PP: {len(multi_pp_ri)} ({100*len(multi_pp_ri)/len(ri_middles):.1f}%)")

    if multi_pp_ri:
        print("\nExamples:")
        for ri, pps in sorted(multi_pp_ri, key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  '{ri}' contains: {pps}")

    # Analyze the "variation" component (what's left after removing PP)
    print(f"\n=== Variation Analysis ===")

    variation_prefixes = Counter()
    variation_suffixes = Counter()

    for ri, pp in ri_to_pp.items():
        if pp and pp in ri:
            idx = ri.find(pp)
            prefix = ri[:idx]
            suffix = ri[idx + len(pp):]

            if prefix:
                variation_prefixes[prefix] += 1
            if suffix:
                variation_suffixes[suffix] += 1

    print(f"\nTop variation prefixes (what comes BEFORE PP base):")
    for prefix, count in variation_prefixes.most_common(15):
        print(f"  '{prefix}': {count}")

    print(f"\nTop variation suffixes (what comes AFTER PP base):")
    for suffix, count in variation_suffixes.most_common(15):
        print(f"  '{suffix}': {count}")

    # Unique variation components
    print(f"\nUnique variation prefixes: {len(variation_prefixes)}")
    print(f"Unique variation suffixes: {len(variation_suffixes)}")

    # Calculate effective collapse ratio
    print(f"\n=== Collapse Summary ===")
    print(f"RI types: {len(ri_middles)}")
    print(f"PP base classes: {len(pp_to_ri)}")
    print(f"Collapse ratio: {len(ri_middles) / len(pp_to_ri):.1f}x")
    print(f"Variation prefixes: {len(variation_prefixes)}")
    print(f"Variation suffixes: {len(variation_suffixes)}")

    # Theoretical combinations
    theoretical = len(pp_to_ri) * (1 + len(variation_prefixes)) * (1 + len(variation_suffixes))
    print(f"\nTheoretical combinations (PP × prefix × suffix): {theoretical:,}")
    print(f"Actual RI: {len(ri_middles)}")
    print(f"Sparsity: {100 * len(ri_middles) / theoretical:.2f}%")

    # Check if collapse produces meaningful groupings
    # Group RI by PP base and check token frequency correlation
    print(f"\n=== Frequency Coherence Within PP Groups ===")

    ri_freq = df_a.groupby('middle').size().to_dict()

    coherence_scores = []
    for pp, ris in pp_to_ri.items():
        if len(ris) >= 3:
            freqs = [ri_freq.get(ri, 0) for ri in ris]
            if max(freqs) > 0:
                # Coefficient of variation
                cv = np.std(freqs) / np.mean(freqs) if np.mean(freqs) > 0 else 0
                coherence_scores.append((pp, len(ris), cv))

    if coherence_scores:
        mean_cv = np.mean([x[2] for x in coherence_scores])
        print(f"Mean coefficient of variation within PP groups: {mean_cv:.2f}")
        print("(Lower = more coherent frequency patterns within groups)")

    # Save results
    output = {
        'pp_multi_count': len(pp_multi),
        'ri_count': len(ri_middles),
        'ri_with_pp_match': ri_with_pp,
        'ri_with_pp_match_pct': float(100 * ri_with_pp / len(ri_middles)),
        'pp_bases_with_ri': len(pp_to_ri),
        'collapse_ratio': float(len(ri_middles) / len(pp_to_ri)) if pp_to_ri else 0,
        'mean_ri_per_pp': float(np.mean(ri_counts)) if ri_counts else 0,
        'max_ri_per_pp': int(np.max(ri_counts)) if ri_counts else 0,
        'variation_prefixes': len(variation_prefixes),
        'variation_suffixes': len(variation_suffixes),
        'multi_pp_ri_count': len(multi_pp_ri),
        'top_pp_bases': [(pp, len(ris)) for pp, ris in sorted_pp[:20]]
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'ri_to_pp_collapse.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== VERDICT ===")
    if len(pp_to_ri) < 150 and ri_with_pp / len(ri_middles) > 0.7:
        print(f"COLLAPSE SUPPORTED: {len(ri_middles)} RI → {len(pp_to_ri)} PP bases ({len(ri_middles)/len(pp_to_ri):.1f}x reduction)")
        print("RI can be interpreted as variations of PP base materials")
    else:
        print(f"PARTIAL COLLAPSE: {len(pp_to_ri)} PP bases, but {100*(1-ri_with_pp/len(ri_middles)):.1f}% RI unrooted")
