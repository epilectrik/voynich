#!/usr/bin/env python3
"""
Compare morphological profiles of RI vs PP tokens.

Question: Do RI tokens use PREFIX/SUFFIX differently than PP tokens?
"""

import json
import sys
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
    if not token.strip():
        return None, None, None

    prefix = None
    suffix = None
    remainder = token

    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            prefix = p
            remainder = remainder[len(p):]
            break

    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    middle = remainder if remainder else None
    return prefix, middle, suffix

# Load PP MIDDLEs (those appearing in B)
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

# Extract morphology
morphologies = df_a['word'].apply(lambda w: extract_morphology(w))
df_a['prefix'] = morphologies.apply(lambda x: x[0])
df_a['middle'] = morphologies.apply(lambda x: x[1])
df_a['suffix'] = morphologies.apply(lambda x: x[2])

# Classify tokens as RI or PP based on MIDDLE
df_a['token_type'] = df_a['middle'].apply(
    lambda m: 'PP' if m in pp_middles else ('RI' if m and m not in pp_middles else 'NONE')
)

print("="*70)
print("RI vs PP TOKEN MORPHOLOGY COMPARISON")
print("="*70)

# Basic counts
type_counts = df_a['token_type'].value_counts()
print(f"\nToken classification:")
for t, c in type_counts.items():
    print(f"  {t}: {c} ({100*c/len(df_a):.1f}%)")

# Filter to tokens with valid MIDDLE
df_ri = df_a[df_a['token_type'] == 'RI'].copy()
df_pp = df_a[df_a['token_type'] == 'PP'].copy()

print(f"\nRI tokens: {len(df_ri)}")
print(f"PP tokens: {len(df_pp)}")

# PREFIX comparison
print("\n" + "="*70)
print("PREFIX DISTRIBUTION COMPARISON")
print("="*70)

ri_prefix_counts = df_ri['prefix'].value_counts(dropna=False)
pp_prefix_counts = df_pp['prefix'].value_counts(dropna=False)

# Normalize
ri_prefix_pct = ri_prefix_counts / len(df_ri) * 100
pp_prefix_pct = pp_prefix_counts / len(df_pp) * 100

# Calculate rates
ri_has_prefix = (df_ri['prefix'].notna().sum() / len(df_ri)) * 100
pp_has_prefix = (df_pp['prefix'].notna().sum() / len(df_pp)) * 100

print(f"\nPREFIX presence:")
print(f"  RI tokens with PREFIX: {ri_has_prefix:.1f}%")
print(f"  PP tokens with PREFIX: {pp_has_prefix:.1f}%")

# Chi-square test for prefix presence
contingency = [[df_ri['prefix'].notna().sum(), df_ri['prefix'].isna().sum()],
               [df_pp['prefix'].notna().sum(), df_pp['prefix'].isna().sum()]]
chi2, p_prefix = stats.chi2_contingency(contingency)[:2]
print(f"  Chi-square p-value: {p_prefix:.2e}")

# Top prefixes comparison
print(f"\n{'PREFIX':>10} {'RI %':>10} {'PP %':>10} {'Ratio':>10}")
print("-" * 45)

all_prefixes_used = set(ri_prefix_counts.index) | set(pp_prefix_counts.index)
prefix_comparison = []
for p in all_prefixes_used:
    if pd.isna(p):
        continue
    ri_pct = ri_prefix_pct.get(p, 0)
    pp_pct = pp_prefix_pct.get(p, 0)
    ratio = ri_pct / pp_pct if pp_pct > 0 else float('inf')
    prefix_comparison.append((p, ri_pct, pp_pct, ratio))

# Sort by ratio (most RI-enriched first)
prefix_comparison.sort(key=lambda x: -x[3])
for p, ri_pct, pp_pct, ratio in prefix_comparison[:15]:
    ratio_str = f"{ratio:.2f}x" if ratio < 100 else "RI-only"
    print(f"{p:>10} {ri_pct:>9.1f}% {pp_pct:>9.1f}% {ratio_str:>10}")

# SUFFIX comparison
print("\n" + "="*70)
print("SUFFIX DISTRIBUTION COMPARISON")
print("="*70)

ri_suffix_counts = df_ri['suffix'].value_counts(dropna=False)
pp_suffix_counts = df_pp['suffix'].value_counts(dropna=False)

ri_suffix_pct = ri_suffix_counts / len(df_ri) * 100
pp_suffix_pct = pp_suffix_counts / len(df_pp) * 100

ri_has_suffix = (df_ri['suffix'].notna().sum() / len(df_ri)) * 100
pp_has_suffix = (df_pp['suffix'].notna().sum() / len(df_pp)) * 100

print(f"\nSUFFIX presence:")
print(f"  RI tokens with SUFFIX: {ri_has_suffix:.1f}%")
print(f"  PP tokens with SUFFIX: {pp_has_suffix:.1f}%")

contingency = [[df_ri['suffix'].notna().sum(), df_ri['suffix'].isna().sum()],
               [df_pp['suffix'].notna().sum(), df_pp['suffix'].isna().sum()]]
chi2, p_suffix = stats.chi2_contingency(contingency)[:2]
print(f"  Chi-square p-value: {p_suffix:.2e}")

print(f"\n{'SUFFIX':>10} {'RI %':>10} {'PP %':>10} {'Ratio':>10}")
print("-" * 45)

all_suffixes_used = set(ri_suffix_counts.index) | set(pp_suffix_counts.index)
suffix_comparison = []
for s in all_suffixes_used:
    if pd.isna(s):
        continue
    ri_pct = ri_suffix_pct.get(s, 0)
    pp_pct = pp_suffix_pct.get(s, 0)
    ratio = ri_pct / pp_pct if pp_pct > 0 else float('inf')
    suffix_comparison.append((s, ri_pct, pp_pct, ratio))

suffix_comparison.sort(key=lambda x: -x[3])
for s, ri_pct, pp_pct, ratio in suffix_comparison[:15]:
    ratio_str = f"{ratio:.2f}x" if ratio < 100 else "RI-only"
    print(f"{s:>10} {ri_pct:>9.1f}% {pp_pct:>9.1f}% {ratio_str:>10}")

# Token length comparison
print("\n" + "="*70)
print("TOKEN LENGTH COMPARISON")
print("="*70)

df_ri['token_len'] = df_ri['word'].apply(lambda w: len(str(w)) if pd.notna(w) else 0)
df_pp['token_len'] = df_pp['word'].apply(lambda w: len(str(w)) if pd.notna(w) else 0)

ri_mean_len = df_ri['token_len'].mean()
pp_mean_len = df_pp['token_len'].mean()

t_stat, p_len = stats.ttest_ind(df_ri['token_len'], df_pp['token_len'])

print(f"\nMean token length:")
print(f"  RI tokens: {ri_mean_len:.2f} characters")
print(f"  PP tokens: {pp_mean_len:.2f} characters")
print(f"  t-test p-value: {p_len:.2e}")

# MIDDLE length comparison
df_ri['middle_len'] = df_ri['middle'].apply(lambda m: len(str(m)) if pd.notna(m) else 0)
df_pp['middle_len'] = df_pp['middle'].apply(lambda m: len(str(m)) if pd.notna(m) else 0)

ri_mid_len = df_ri['middle_len'].mean()
pp_mid_len = df_pp['middle_len'].mean()

print(f"\nMean MIDDLE length:")
print(f"  RI tokens: {ri_mid_len:.2f} characters")
print(f"  PP tokens: {pp_mid_len:.2f} characters")

# Morphological completeness (has all 3 parts?)
print("\n" + "="*70)
print("MORPHOLOGICAL COMPLETENESS")
print("="*70)

ri_complete = ((df_ri['prefix'].notna()) & (df_ri['suffix'].notna())).sum() / len(df_ri) * 100
pp_complete = ((df_pp['prefix'].notna()) & (df_pp['suffix'].notna())).sum() / len(df_pp) * 100

ri_naked = ((df_ri['prefix'].isna()) & (df_ri['suffix'].isna())).sum() / len(df_ri) * 100
pp_naked = ((df_pp['prefix'].isna()) & (df_pp['suffix'].isna())).sum() / len(df_pp) * 100

ri_prefix_only = ((df_ri['prefix'].notna()) & (df_ri['suffix'].isna())).sum() / len(df_ri) * 100
pp_prefix_only = ((df_pp['prefix'].notna()) & (df_pp['suffix'].isna())).sum() / len(df_pp) * 100

ri_suffix_only = ((df_ri['prefix'].isna()) & (df_ri['suffix'].notna())).sum() / len(df_ri) * 100
pp_suffix_only = ((df_pp['prefix'].isna()) & (df_pp['suffix'].notna())).sum() / len(df_pp) * 100

print(f"\n{'Structure':>20} {'RI %':>10} {'PP %':>10}")
print("-" * 45)
print(f"{'PREFIX+SUFFIX':>20} {ri_complete:>9.1f}% {pp_complete:>9.1f}%")
print(f"{'PREFIX only':>20} {ri_prefix_only:>9.1f}% {pp_prefix_only:>9.1f}%")
print(f"{'SUFFIX only':>20} {ri_suffix_only:>9.1f}% {pp_suffix_only:>9.1f}%")
print(f"{'NAKED (middle only)':>20} {ri_naked:>9.1f}% {pp_naked:>9.1f}%")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Key differences between RI and PP tokens:

PREFIX:
  - RI: {ri_has_prefix:.1f}% have PREFIX
  - PP: {pp_has_prefix:.1f}% have PREFIX
  - Difference: {abs(ri_has_prefix - pp_has_prefix):.1f}pp (p={p_prefix:.2e})

SUFFIX:
  - RI: {ri_has_suffix:.1f}% have SUFFIX
  - PP: {pp_has_suffix:.1f}% have SUFFIX
  - Difference: {abs(ri_has_suffix - pp_has_suffix):.1f}pp (p={p_suffix:.2e})

TOKEN LENGTH:
  - RI: {ri_mean_len:.2f} chars
  - PP: {pp_mean_len:.2f} chars
  - Difference: {abs(ri_mean_len - pp_mean_len):.2f} chars (p={p_len:.2e})

COMPLETENESS:
  - RI fully structured (P+S): {ri_complete:.1f}%
  - PP fully structured (P+S): {pp_complete:.1f}%
  - RI naked (M only): {ri_naked:.1f}%
  - PP naked (M only): {pp_naked:.1f}%
""")

# Interpretation
print("="*70)
print("INTERPRETATION")
print("="*70)

if abs(ri_has_prefix - pp_has_prefix) > 10 or abs(ri_has_suffix - pp_has_suffix) > 10:
    print("""
SIGNIFICANT MORPHOLOGICAL DIVERGENCE DETECTED.

RI tokens and PP tokens have different morphological profiles.
This suggests PREFIX/SUFFIX serve different roles in each system:

- PP tokens: PREFIX/SUFFIX have operational meaning (articulation, closure)
- RI tokens: PREFIX/SUFFIX may serve different purposes:
  * Mnemonic scaffolding (human-readable structure)
  * Organizational indexing (cross-reference markers)
  * Phonetic completion (structural padding)

The morphological apparatus is REPURPOSED between the two token classes.
""")
else:
    print("""
NO SIGNIFICANT MORPHOLOGICAL DIVERGENCE.

RI and PP tokens have similar morphological profiles.
PREFIX/SUFFIX appear to serve similar structural roles in both systems.
The difference between RI and PP is purely at the MIDDLE level.
""")
