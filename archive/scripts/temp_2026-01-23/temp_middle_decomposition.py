#!/usr/bin/env python3
"""
Can RI-D MIDDLEs be decomposed into smaller repeating units?
Check for compositional structure within "unique" MIDDLEs.
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter
import re

PROJECT_ROOT = Path('.')

# Morphology
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

# Load PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load A tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

# Get RI-D MIDDLEs (singletons)
ri_tokens = df_a[~df_a['middle'].isin(pp_middles) & df_a['middle'].notna()]
middle_counts = ri_tokens['middle'].value_counts()
singleton_middles = [m for m, c in middle_counts.items() if c == 1]

print("="*70)
print("RI-D MIDDLE INTERNAL STRUCTURE ANALYSIS")
print("="*70)

print(f"\nTotal RI-D MIDDLEs to analyze: {len(singleton_middles)}")

# 1. Length distribution
lengths = [len(m) for m in singleton_middles]
print(f"\nLength distribution:")
for l in sorted(set(lengths)):
    count = lengths.count(l)
    pct = 100 * count / len(lengths)
    print(f"  {l} chars: {count} ({pct:.1f}%)")

# 2. N-gram analysis - what substrings repeat across MIDDLEs?
print(f"\n" + "="*70)
print("N-GRAM ANALYSIS (substrings that repeat across RI-D MIDDLEs)")
print("="*70)

def get_ngrams(s, n):
    return [s[i:i+n] for i in range(len(s)-n+1)]

for n in [2, 3, 4]:
    all_ngrams = []
    for m in singleton_middles:
        if len(m) >= n:
            all_ngrams.extend(get_ngrams(m, n))

    ngram_counts = Counter(all_ngrams)
    top_ngrams = ngram_counts.most_common(15)

    # How many unique ngrams vs total?
    unique_ngrams = len(ngram_counts)
    total_ngrams = len(all_ngrams)

    print(f"\n{n}-grams:")
    print(f"  Total: {total_ngrams}, Unique: {unique_ngrams}, Ratio: {unique_ngrams/total_ngrams:.2%}")
    print(f"  Top 15:")
    for ng, c in top_ngrams:
        print(f"    '{ng}': {c}")

# 3. Check if RI-D MIDDLEs contain PP MIDDLEs as substrings
print(f"\n" + "="*70)
print("DO RI-D MIDDLEs CONTAIN PP MIDDLEs AS SUBSTRINGS?")
print("="*70)

pp_list = sorted(pp_middles, key=len, reverse=True)
rid_contains_pp = []

for rid in singleton_middles:
    contained_pp = [pp for pp in pp_list if pp in rid and len(pp) >= 2]
    if contained_pp:
        rid_contains_pp.append((rid, contained_pp))

print(f"\nRI-D MIDDLEs containing PP MIDDLE as substring: {len(rid_contains_pp)} / {len(singleton_middles)} ({100*len(rid_contains_pp)/len(singleton_middles):.1f}%)")

print(f"\nExamples (first 20):")
for rid, pps in rid_contains_pp[:20]:
    print(f"  '{rid}' contains: {pps}")

# 4. Can we identify common "building blocks"?
print(f"\n" + "="*70)
print("POTENTIAL BUILDING BLOCKS (high-frequency 2-3 grams)")
print("="*70)

# Combine 2-grams and 3-grams
all_2grams = []
all_3grams = []
for m in singleton_middles:
    if len(m) >= 2:
        all_2grams.extend(get_ngrams(m, 2))
    if len(m) >= 3:
        all_3grams.extend(get_ngrams(m, 3))

gram2_counts = Counter(all_2grams)
gram3_counts = Counter(all_3grams)

# Find grams that appear in many different MIDDLEs (not just repeating within one)
def grams_per_middle(middles, n):
    """Count how many different MIDDLEs contain each n-gram"""
    gram_to_middles = {}
    for m in middles:
        if len(m) >= n:
            for ng in set(get_ngrams(m, n)):  # set to count each gram once per middle
                if ng not in gram_to_middles:
                    gram_to_middles[ng] = set()
                gram_to_middles[ng].add(m)
    return {g: len(ms) for g, ms in gram_to_middles.items()}

gram2_coverage = grams_per_middle(singleton_middles, 2)
gram3_coverage = grams_per_middle(singleton_middles, 3)

print(f"\n2-grams appearing in most MIDDLEs:")
for ng, count in sorted(gram2_coverage.items(), key=lambda x: -x[1])[:15]:
    pct = 100 * count / len(singleton_middles)
    print(f"  '{ng}': in {count} MIDDLEs ({pct:.1f}%)")

print(f"\n3-grams appearing in most MIDDLEs:")
for ng, count in sorted(gram3_coverage.items(), key=lambda x: -x[1])[:15]:
    pct = 100 * count / len(singleton_middles)
    print(f"  '{ng}': in {count} MIDDLEs ({pct:.1f}%)")

# 5. Positional patterns - do certain characters cluster at start/middle/end?
print(f"\n" + "="*70)
print("POSITIONAL PATTERNS (what characters appear where?)")
print("="*70)

start_chars = Counter(m[0] for m in singleton_middles if len(m) > 0)
end_chars = Counter(m[-1] for m in singleton_middles if len(m) > 0)

print(f"\nFirst character distribution (top 10):")
for ch, c in start_chars.most_common(10):
    pct = 100 * c / len(singleton_middles)
    print(f"  '{ch}': {c} ({pct:.1f}%)")

print(f"\nLast character distribution (top 10):")
for ch, c in end_chars.most_common(10):
    pct = 100 * c / len(singleton_middles)
    print(f"  '{ch}': {c} ({pct:.1f}%)")

# 6. Check for compound structure: MIDDLE = X + Y where X and Y are both seen elsewhere
print(f"\n" + "="*70)
print("COMPOUND STRUCTURE TEST")
print("="*70)

# Get all MIDDLEs (not just singletons) for potential sub-components
all_a_middles = set(df_a['middle'].dropna())

# For each RI-D MIDDLE, can we split it into two parts that both exist as MIDDLEs?
compound_candidates = []
for rid in singleton_middles:
    if len(rid) >= 4:  # Need at least 2+2 for compound
        for split_point in range(2, len(rid)-1):
            left = rid[:split_point]
            right = rid[split_point:]
            if left in all_a_middles and right in all_a_middles:
                compound_candidates.append((rid, left, right))
                break  # Just find first valid split

print(f"\nRI-D MIDDLEs that could be compounds of other MIDDLEs: {len(compound_candidates)} / {len(singleton_middles)} ({100*len(compound_candidates)/len(singleton_middles):.1f}%)")

if compound_candidates:
    print(f"\nExamples (first 20):")
    for rid, left, right in compound_candidates[:20]:
        print(f"  '{rid}' = '{left}' + '{right}'")

# Summary
print(f"\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
RI-D MIDDLEs show SOME internal structure:

1. Common 2-grams like 'ch', 'sh', 'od', 'ol' appear across many MIDDLEs
   (These are the same patterns as PREFIXes - suggests morphology continues)

2. {100*len(rid_contains_pp)/len(singleton_middles):.1f}% of RI-D MIDDLEs contain PP MIDDLEs as substrings
   (RI-D may be PP + extension, or contain PP-like components)

3. {100*len(compound_candidates)/len(singleton_middles):.1f}% could be analyzed as compounds of other MIDDLEs
   (Some compositional structure exists)

4. Positional patterns exist (certain chars favor start/end positions)
   (Suggests PREFIX-like and SUFFIX-like internal structure)

This suggests RI-D MIDDLEs may have FINER-GRAINED internal morphology
that our current PREFIX/MIDDLE/SUFFIX decomposition doesn't capture.
""")
