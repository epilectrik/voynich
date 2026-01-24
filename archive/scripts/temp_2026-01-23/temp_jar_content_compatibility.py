#!/usr/bin/env python3
"""
Test whether jar labels share PP atoms with their contents.

Hypothesis: If jars are category containers, their PP atoms should
predict the PP atoms of their contents (compatibility coherence).
"""

import json
import sys
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent

def extract_middle(token):
    """Extract MIDDLE from token using standard morphology."""
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'oe', 'al']
    suffixes = ['aiin', 'oiin', 'iin', 'ain', 'dy', 'hy', 'ky', 'ly', 'my', 'ny',
                'ry', 'sy', 'ty', 'am', 'an', 'al', 'ar', 'ol', 'or', 'y', 's',
                'g', 'd', 'l', 'r', 'n', 'm']

    middle = str(token).strip()
    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            middle = middle[len(p):]
            break
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            middle = middle[:-len(s)]
            break
    return middle if middle and middle != token else None

def load_pp_middles():
    """Extract PP MIDDLEs from transcript."""
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df = df[~df['placement'].str.startswith('L', na=False)]

    a_tokens = set(df[df['language'] == 'A']['word'].dropna().unique())
    b_tokens = set(df[df['language'] == 'B']['word'].dropna().unique())
    pp_tokens = a_tokens & b_tokens

    pp_middles = set()
    for token in pp_tokens:
        mid = extract_middle(token)
        if mid and len(mid) >= 1:
            pp_middles.add(mid)
    return pp_middles

def find_pp_atoms(token, pp_middles):
    """Find all PP atoms in a token."""
    found = set()
    for pp in pp_middles:
        if pp in token:
            found.add(pp)
    return found

def load_jar_content_pairs():
    """Load jar labels with their associated content labels."""
    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
    pairs = []

    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file) as f:
            data = json.load(f)

        folio = data.get('folio', json_file.stem)

        if 'groups' in data:
            for group in data['groups']:
                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    contents = []
                    for key in ['roots', 'leaves', 'labels']:
                        if key in group:
                            for item in group[key]:
                                if isinstance(item, dict):
                                    token = item.get('token', '')
                                else:
                                    token = item
                                if token and isinstance(token, str) and '*' not in token:
                                    contents.append(token)

                    if contents:
                        pairs.append({
                            'folio': folio,
                            'jar': jar,
                            'contents': contents
                        })

    return pairs

if __name__ == '__main__':
    print("=" * 70)
    print("JAR-CONTENT PP COMPATIBILITY ANALYSIS")
    print("=" * 70)

    pp_middles = load_pp_middles()
    print(f"\nLoaded {len(pp_middles)} PP MIDDLEs")

    pairs = load_jar_content_pairs()
    print(f"Loaded {len(pairs)} jar-content groups")

    # For each jar, compute PP overlap with its contents
    print("\n" + "=" * 70)
    print("JAR-TO-CONTENT PP SHARING")
    print("=" * 70)

    all_overlaps = []
    random_overlaps = []
    all_content_pp = []  # Collect all content PP for random baseline

    for pair in pairs:
        jar = pair['jar']
        contents = pair['contents']

        jar_pp = find_pp_atoms(jar, pp_middles)

        # Content PP atoms (union across all contents)
        content_pp = set()
        for content in contents:
            content_pp.update(find_pp_atoms(content, pp_middles))

        all_content_pp.append(content_pp)

        # Compute overlap
        if jar_pp and content_pp:
            overlap = len(jar_pp & content_pp)
            jaccard = len(jar_pp & content_pp) / len(jar_pp | content_pp) if (jar_pp | content_pp) else 0
            coverage = overlap / len(jar_pp) if jar_pp else 0  # What % of jar PP appears in contents

            all_overlaps.append({
                'folio': pair['folio'],
                'jar': jar,
                'jar_pp_count': len(jar_pp),
                'content_pp_count': len(content_pp),
                'overlap': overlap,
                'jaccard': jaccard,
                'jar_coverage': coverage,
                'n_contents': len(contents)
            })

    # Display results
    print(f"\n{'Folio':<10} {'Jar':<15} {'Jar PP':<8} {'Content PP':<12} {'Overlap':<8} {'Jaccard':<8} {'Coverage':<10}")
    print("-" * 80)

    for r in sorted(all_overlaps, key=lambda x: x['jaccard'], reverse=True):
        print(f"{r['folio']:<10} {r['jar']:<15} {r['jar_pp_count']:<8} {r['content_pp_count']:<12} {r['overlap']:<8} {r['jaccard']:.3f}    {r['jar_coverage']:.1%}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    jaccards = [r['jaccard'] for r in all_overlaps]
    coverages = [r['jar_coverage'] for r in all_overlaps]

    print(f"\nMean Jaccard similarity: {np.mean(jaccards):.3f}")
    print(f"Std Jaccard similarity: {np.std(jaccards):.3f}")
    print(f"Mean jar coverage in contents: {np.mean(coverages):.1%}")

    # Random baseline: shuffle jars to random content groups
    print("\n" + "=" * 70)
    print("RANDOM BASELINE (1000 shuffles)")
    print("=" * 70)

    import random
    n_shuffles = 1000
    random_jaccards = []

    jars_list = [p['jar'] for p in pairs]

    for _ in range(n_shuffles):
        shuffled_jars = jars_list.copy()
        random.shuffle(shuffled_jars)

        for jar, content_pp in zip(shuffled_jars, all_content_pp):
            jar_pp = find_pp_atoms(jar, pp_middles)
            if jar_pp and content_pp:
                jaccard = len(jar_pp & content_pp) / len(jar_pp | content_pp)
                random_jaccards.append(jaccard)

    mean_random = np.mean(random_jaccards)
    std_random = np.std(random_jaccards)

    print(f"Random baseline Jaccard: {mean_random:.3f} ± {std_random:.3f}")
    print(f"Observed Jaccard: {np.mean(jaccards):.3f}")
    print(f"Ratio (observed/random): {np.mean(jaccards)/mean_random:.2f}x")

    # Z-score
    z = (np.mean(jaccards) - mean_random) / (std_random / np.sqrt(len(jaccards)))
    print(f"Z-score: {z:.2f}")

    # Check if specific PPs are shared
    print("\n" + "=" * 70)
    print("PP ATOMS CONSISTENTLY SHARED (jar → content)")
    print("=" * 70)

    shared_counts = Counter()
    total_jars = 0

    for pair in pairs:
        jar = pair['jar']
        contents = pair['contents']

        jar_pp = find_pp_atoms(jar, pp_middles)
        content_pp = set()
        for content in contents:
            content_pp.update(find_pp_atoms(content, pp_middles))

        if jar_pp:
            total_jars += 1
            for pp in jar_pp:
                if pp in content_pp:
                    shared_counts[pp] += 1

    print(f"\nPP atoms most consistently shared (jar has it AND contents have it):")
    print(f"{'PP Atom':<10} {'Shared Count':<15} {'Share Rate':<10}")
    print("-" * 40)
    for pp, count in shared_counts.most_common(20):
        rate = count / total_jars if total_jars else 0
        print(f"'{pp}':<10 {count:<15} {rate:.1%}")

    # Look at specific folios
    print("\n" + "=" * 70)
    print("F88V DETAILED ANALYSIS")
    print("=" * 70)

    for r in all_overlaps:
        if r['folio'] == 'f88v':
            jar = r['jar']
            jar_pp = find_pp_atoms(jar, pp_middles)

            print(f"\nJar: {jar}")
            print(f"Jar PP atoms: {sorted(jar_pp)}")

            # Find which contents share which PPs
            for pair in pairs:
                if pair['folio'] == 'f88v' and pair['jar'] == jar:
                    print(f"\nContents ({len(pair['contents'])} items):")
                    for content in pair['contents']:
                        content_pp = find_pp_atoms(content, pp_middles)
                        shared = jar_pp & content_pp
                        print(f"  {content}: shares {sorted(shared)}")
