#!/usr/bin/env python3
"""
PP × HT Interaction Test using proper HT data from ht_folio_features.json
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict
from scipy import stats

# Load proper HT data
with open('results/ht_folio_features.json', encoding='utf-8') as f:
    ht_data = json.load(f)

# Load transcription for PP calculation
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or '_EMPTY_'
            return remainder or '_EMPTY_'
    return None

# Get A and B data
df_a = df[(df['language'] == 'A') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()
df_b = df[(df['language'] == 'B') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

b_middles = set(df_b['middle'].dropna().unique())

print("=" * 70)
print("PP x HT INTERACTION TEST (Proper HT Data)")
print("=" * 70)
print(f"\nHT data: {ht_data['metadata']['n_folios']} folios")
print(f"Global mean HT density: {ht_data['summary']['global_mean_ht_density']*100:.1f}%")

# Build A-record PP data by folio
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna())
}).reset_index()
a_records.columns = ['folio', 'line', 'middles']
a_records['pp_count'] = a_records['middles'].apply(lambda m: len(m & b_middles))

# Aggregate PP by folio
pp_by_folio = a_records.groupby('folio')['pp_count'].agg(['mean', 'sum', 'count', 'std'])
pp_by_folio.columns = ['pp_mean', 'pp_sum', 'a_record_count', 'pp_std']

# Build analysis dataframe
analysis_data = []
for folio, ht_info in ht_data['folios'].items():
    if folio in pp_by_folio.index:
        analysis_data.append({
            'folio': folio,
            'ht_density': ht_info['ht_density'],
            'ht_count': ht_info['n_ht'],
            'total_tokens': ht_info['n_tokens'],
            'ht_unique_types': ht_info['ht_unique_types'],
            'ht_ttr': ht_info['ht_ttr'],
            'pp_mean': pp_by_folio.loc[folio, 'pp_mean'],
            'pp_sum': pp_by_folio.loc[folio, 'pp_sum'],
            'a_records': pp_by_folio.loc[folio, 'a_record_count'],
            'pp_std': pp_by_folio.loc[folio, 'pp_std']
        })

analysis_df = pd.DataFrame(analysis_data)
print(f"\nFolios with both PP and HT data: {len(analysis_df)}")

# =============================================================================
# TEST 1: PP vs HT Correlations
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: PP vs HT Correlations")
print("=" * 70)

# Primary test: PP mean vs HT density
r1, p1 = stats.pearsonr(analysis_df['pp_mean'], analysis_df['ht_density'])
print(f"\nPP mean vs HT density:")
print(f"  Pearson r = {r1:.4f}, p = {p1:.4f}")

rho1, prho1 = stats.spearmanr(analysis_df['pp_mean'], analysis_df['ht_density'])
print(f"  Spearman rho = {rho1:.4f}, p = {prho1:.4f}")

# PP mean vs HT count (controlling for folio size?)
r2, p2 = stats.pearsonr(analysis_df['pp_mean'], analysis_df['ht_count'])
print(f"\nPP mean vs HT count:")
print(f"  r = {r2:.4f}, p = {p2:.4f}")

# PP sum vs HT count
r3, p3 = stats.pearsonr(analysis_df['pp_sum'], analysis_df['ht_count'])
print(f"\nPP sum vs HT count:")
print(f"  r = {r3:.4f}, p = {p3:.4f}")

# PP mean vs HT type-token ratio (morphological complexity)
r4, p4 = stats.pearsonr(analysis_df['pp_mean'], analysis_df['ht_ttr'])
print(f"\nPP mean vs HT TTR (morphological complexity):")
print(f"  r = {r4:.4f}, p = {p4:.4f}")

# =============================================================================
# TEST 2: PP Bins vs HT Density
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: PP Bins vs HT Density")
print("=" * 70)

# Create PP bins
bins = [0, 3, 4, 5, 6, 15]
labels = ['0-3', '3-4', '4-5', '5-6', '6+']
analysis_df['pp_bin'] = pd.cut(analysis_df['pp_mean'], bins=bins, labels=labels)

print("\nHT density by PP bin:")
print("-" * 50)
for pp_bin in labels:
    subset = analysis_df[analysis_df['pp_bin'] == pp_bin]
    if len(subset) > 0:
        mean_ht = subset['ht_density'].mean()
        std_ht = subset['ht_density'].std()
        n = len(subset)
        print(f"  PP {pp_bin}: HT = {mean_ht*100:.2f}% +/- {std_ht*100:.2f}% (n={n})")

# ANOVA across bins
groups = [analysis_df[analysis_df['pp_bin'] == b]['ht_density'].values for b in labels if len(analysis_df[analysis_df['pp_bin'] == b]) > 0]
if len(groups) >= 2 and all(len(g) > 0 for g in groups):
    f_stat, p_anova = stats.f_oneway(*groups)
    print(f"\nANOVA: F = {f_stat:.2f}, p = {p_anova:.4f}")

# =============================================================================
# TEST 3: By Currier System
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: Correlation by Currier System")
print("=" * 70)

# Get system for each folio
folio_system = {}
for _, row in df.iterrows():
    if pd.notna(row['folio']) and pd.notna(row['language']):
        folio_system[row['folio']] = row['language']

analysis_df['system'] = analysis_df['folio'].map(folio_system)

for system in ['A', 'B']:
    subset = analysis_df[analysis_df['system'] == system]
    if len(subset) > 5:
        r, p = stats.pearsonr(subset['pp_mean'], subset['ht_density'])
        print(f"\nCurrier {system} folios (n={len(subset)}):")
        print(f"  PP mean vs HT density: r = {r:.4f}, p = {p:.4f}")

# =============================================================================
# TEST 4: Does A-record count mediate?
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: Controlling for A-record Count")
print("=" * 70)

# Maybe folios with more A records have different properties
r_ar_ht, p_ar_ht = stats.pearsonr(analysis_df['a_records'], analysis_df['ht_density'])
print(f"\nA-record count vs HT density:")
print(f"  r = {r_ar_ht:.4f}, p = {p_ar_ht:.4f}")

r_ar_pp, p_ar_pp = stats.pearsonr(analysis_df['a_records'], analysis_df['pp_mean'])
print(f"\nA-record count vs PP mean:")
print(f"  r = {r_ar_pp:.4f}, p = {p_ar_pp:.4f}")

# Partial correlation: PP vs HT controlling for A-record count
from scipy.stats import linregress

slope1, intercept1, _, _, _ = linregress(analysis_df['a_records'], analysis_df['ht_density'])
ht_resid = analysis_df['ht_density'] - (slope1 * analysis_df['a_records'] + intercept1)

slope2, intercept2, _, _, _ = linregress(analysis_df['a_records'], analysis_df['pp_mean'])
pp_resid = analysis_df['pp_mean'] - (slope2 * analysis_df['a_records'] + intercept2)

r_partial, p_partial = stats.pearsonr(pp_resid, ht_resid)
print(f"\nPP vs HT (controlling for A-record count):")
print(f"  r_partial = {r_partial:.4f}, p = {p_partial:.4f}")

# =============================================================================
# TEST 5: Linear regression
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: Linear Regression (PP -> HT)")
print("=" * 70)

slope, intercept, r_value, p_value, std_err = linregress(analysis_df['pp_mean'], analysis_df['ht_density'])
print(f"\nHT_density = {slope:.4f} * PP_mean + {intercept:.4f}")
print(f"R-squared = {r_value**2:.4f}")
print(f"p = {p_value:.4f}")
print(f"Slope interpretation: +1 PP mean -> {slope*100:.2f}% change in HT density")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: Responsibility Substitution Hypothesis")
print("=" * 70)

if r1 < -0.1 and p1 < 0.05:
    print("\n*** SUPPORTED: Negative correlation between PP and HT ***")
    print(f"    r = {r1:.3f}, p = {p1:.4f}")
    print("    More PP capacity -> Less HT vigilance (substitution)")
elif r1 > 0.1 and p1 < 0.05:
    print("\n*** REJECTED: Positive correlation between PP and HT ***")
    print(f"    r = {r1:.3f}, p = {p1:.4f}")
    print("    More PP capacity -> More HT vigilance (complementary)")
else:
    print("\n*** INCONCLUSIVE: Weak or non-significant correlation ***")
    print(f"    r = {r1:.3f}, p = {p1:.4f}")
    print("    PP and HT may be independent systems")
