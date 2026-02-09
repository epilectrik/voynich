#!/usr/bin/env python3
"""
Test 9: P-text Token Morphology

Question: Are P-text tokens morphologically complete (like Currier A)
or abbreviated/label-like (like AZC diagram)?

Key indicators:
- Token length distribution
- Morphological completeness (has PREFIX, MIDDLE, SUFFIX)
- Bare token rate (MIDDLE only, no affixes)
- TTR (type-token ratio) - labels are more repetitive
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter
import numpy as np
from scripts.voynich import Morphology

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

# Collect tokens by category
ptext_tokens = []
azc_diagram_tokens = []
currier_a_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if currier == 'NA':  # AZC
                if placement == 'P' or placement.startswith('P'):
                    ptext_tokens.append(token)
                else:
                    azc_diagram_tokens.append(token)
            elif currier == 'A':
                currier_a_tokens.append(token)

print("=" * 70)
print("TEST 9: P-TEXT TOKEN MORPHOLOGY")
print("=" * 70)
print()

# 1. Token length distribution
print("1. TOKEN LENGTH DISTRIBUTION")
print("-" * 50)

def length_stats(tokens):
    if not tokens:
        return None
    lengths = [len(t) for t in tokens]
    return {
        'n': len(tokens),
        'mean': np.mean(lengths),
        'median': np.median(lengths),
        'std': np.std(lengths)
    }

ptext_len = length_stats(ptext_tokens)
azc_len = length_stats(azc_diagram_tokens)
a_len = length_stats(currier_a_tokens)

print(f"{'Category':<15} {'N':<8} {'Mean':<8} {'Median':<8} {'Std':<8}")
print("-" * 47)
print(f"{'P-text':<15} {ptext_len['n']:<8} {ptext_len['mean']:<8.2f} {ptext_len['median']:<8.1f} {ptext_len['std']:<8.2f}")
print(f"{'AZC diagram':<15} {azc_len['n']:<8} {azc_len['mean']:<8.2f} {azc_len['median']:<8.1f} {azc_len['std']:<8.2f}")
print(f"{'Currier A':<15} {a_len['n']:<8} {a_len['mean']:<8.2f} {a_len['median']:<8.1f} {a_len['std']:<8.2f}")
print()

# 2. Morphological completeness
print("2. MORPHOLOGICAL COMPLETENESS")
print("-" * 50)

def morph_profile(tokens):
    if not tokens:
        return None

    has_prefix = 0
    has_suffix = 0
    has_articulator = 0
    bare = 0  # MIDDLE only

    for t in tokens:
        m = morph.extract(t)
        if m.prefix:
            has_prefix += 1
        if m.suffix:
            has_suffix += 1
        if m.articulator:
            has_articulator += 1
        if not m.prefix and not m.suffix and not m.articulator:
            bare += 1

    n = len(tokens)
    return {
        'has_prefix': has_prefix / n,
        'has_suffix': has_suffix / n,
        'has_articulator': has_articulator / n,
        'bare_rate': bare / n
    }

ptext_morph = morph_profile(ptext_tokens)
azc_morph = morph_profile(azc_diagram_tokens)
a_morph = morph_profile(currier_a_tokens)

print(f"{'Metric':<20} {'P-text':<12} {'AZC diagram':<12} {'Currier A':<12}")
print("-" * 56)
print(f"{'Has PREFIX':<20} {ptext_morph['has_prefix']*100:<12.1f}% {azc_morph['has_prefix']*100:<12.1f}% {a_morph['has_prefix']*100:<12.1f}%")
print(f"{'Has SUFFIX':<20} {ptext_morph['has_suffix']*100:<12.1f}% {azc_morph['has_suffix']*100:<12.1f}% {a_morph['has_suffix']*100:<12.1f}%")
print(f"{'Has ARTICULATOR':<20} {ptext_morph['has_articulator']*100:<12.1f}% {azc_morph['has_articulator']*100:<12.1f}% {a_morph['has_articulator']*100:<12.1f}%")
print(f"{'Bare (MIDDLE only)':<20} {ptext_morph['bare_rate']*100:<12.1f}% {azc_morph['bare_rate']*100:<12.1f}% {a_morph['bare_rate']*100:<12.1f}%")
print()

# 3. Type-Token Ratio
print("3. TYPE-TOKEN RATIO (VOCABULARY DIVERSITY)")
print("-" * 50)

def ttr(tokens):
    if not tokens:
        return 0
    return len(set(tokens)) / len(tokens)

ptext_ttr = ttr(ptext_tokens)
azc_ttr = ttr(azc_diagram_tokens)
a_ttr = ttr(currier_a_tokens)

print(f"P-text TTR: {ptext_ttr:.3f}")
print(f"AZC diagram TTR: {azc_ttr:.3f}")
print(f"Currier A TTR: {a_ttr:.3f}")
print()
print("(Higher TTR = more diverse vocabulary, less repetition)")
print("(AZC diagram should have highest TTR due to labeling function)")
print()

# 4. PREFIX distribution
print("4. PREFIX DISTRIBUTION")
print("-" * 50)

def prefix_distribution(tokens):
    prefixes = []
    for t in tokens:
        m = morph.extract(t)
        prefixes.append(m.prefix if m.prefix else 'NONE')
    return Counter(prefixes)

ptext_prefixes = prefix_distribution(ptext_tokens)
azc_prefixes = prefix_distribution(azc_diagram_tokens)
a_prefixes = prefix_distribution(currier_a_tokens)

print("Top 10 PREFIXes:")
print(f"{'PREFIX':<10} {'P-text':<12} {'AZC diagram':<12} {'Currier A':<12}")
print("-" * 46)

all_prefixes = set(ptext_prefixes.keys()) | set(azc_prefixes.keys()) | set(a_prefixes.keys())
top_prefixes = sorted(all_prefixes, key=lambda p: ptext_prefixes.get(p, 0), reverse=True)[:10]

for prefix in top_prefixes:
    p_pct = ptext_prefixes.get(prefix, 0) / len(ptext_tokens) * 100 if ptext_tokens else 0
    a_pct = azc_prefixes.get(prefix, 0) / len(azc_diagram_tokens) * 100 if azc_diagram_tokens else 0
    ca_pct = a_prefixes.get(prefix, 0) / len(currier_a_tokens) * 100 if currier_a_tokens else 0
    print(f"{prefix:<10} {p_pct:<12.1f}% {a_pct:<12.1f}% {ca_pct:<12.1f}%")

print()

# 5. Similarity assessment
print("5. MORPHOLOGICAL SIMILARITY")
print("-" * 50)

# Distance metrics
def morph_distance(profile1, profile2):
    keys = ['has_prefix', 'has_suffix', 'has_articulator', 'bare_rate']
    return sum(abs(profile1[k] - profile2[k]) for k in keys) / len(keys)

dist_to_a = morph_distance(ptext_morph, a_morph)
dist_to_azc = morph_distance(ptext_morph, azc_morph)

print(f"P-text morphological distance to Currier A: {dist_to_a:.3f}")
print(f"P-text morphological distance to AZC diagram: {dist_to_azc:.3f}")
print()

# Length distance
len_dist_a = abs(ptext_len['mean'] - a_len['mean'])
len_dist_azc = abs(ptext_len['mean'] - azc_len['mean'])

print(f"P-text length distance to Currier A: {len_dist_a:.2f}")
print(f"P-text length distance to AZC diagram: {len_dist_azc:.2f}")
print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)

morph_verdict = "A-LIKE" if dist_to_a < dist_to_azc else "AZC-LIKE"
len_verdict = "A-LIKE" if len_dist_a < len_dist_azc else "AZC-LIKE"
ttr_verdict = "A-LIKE" if abs(ptext_ttr - a_ttr) < abs(ptext_ttr - azc_ttr) else "AZC-LIKE"

print(f"Morphological profile: {morph_verdict} (distance to A: {dist_to_a:.3f}, to AZC: {dist_to_azc:.3f})")
print(f"Token length: {len_verdict} (distance to A: {len_dist_a:.2f}, to AZC: {len_dist_azc:.2f})")
print(f"TTR (diversity): {ttr_verdict} (P-text: {ptext_ttr:.3f}, A: {a_ttr:.3f}, AZC: {azc_ttr:.3f})")
print()

votes = [morph_verdict, len_verdict, ttr_verdict]
a_votes = votes.count("A-LIKE")
azc_votes = votes.count("AZC-LIKE")

if a_votes > azc_votes:
    final_verdict = "A-LIKE"
    print(f"OVERALL: P-text morphology is A-LIKE ({a_votes}/3 indicators)")
elif azc_votes > a_votes:
    final_verdict = "AZC-LIKE"
    print(f"OVERALL: P-text morphology is AZC-LIKE ({azc_votes}/3 indicators)")
else:
    final_verdict = "INTERMEDIATE"
    print(f"OVERALL: P-text morphology is INTERMEDIATE (split indicators)")
