#!/usr/bin/env python3
"""
PP × HT Interaction Test: Responsibility Substitution

Hypothesis: Higher PP count (more B execution freedom) correlates with
lower HT density (less required human vigilance).

If the system substitutes grammatical freedom for human attention,
we should see an inverse relationship between PP capacity and HT load.

Tests:
1. PP count vs HT density correlation (record level)
2. PP count vs HT density correlation (folio level)
3. PP count bins vs mean HT density
4. Does PP mediate the relationship between content complexity and HT?
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

# Load transcription
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']  # H track only

# Morphology extraction
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

# Get A and B dataframes
df_a = df[(df['language'] == 'A') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()
df_b = df[(df['language'] == 'B') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)

# Get B MIDDLEs (for PP identification)
b_middles = set(df_b['middle'].dropna().unique())

print("=" * 70)
print("PP x HT INTERACTION TEST: Responsibility Substitution")
print("=" * 70)

# =============================================================================
# Identify HT tokens
# =============================================================================
# HT tokens are single-character tokens in specific placement contexts
# From the constraint system, HT appears in margins and specific positions

# Simple HT identification: single lowercase letters that aren't standard tokens
def is_ht_candidate(token, placement):
    if pd.isna(token) or pd.isna(placement):
        return False
    token = str(token)
    # HT are typically single characters or very short marginal annotations
    # Check placement for margin indicators
    if len(token) <= 2 and placement and ('M' in str(placement) or 'margin' in str(placement).lower()):
        return True
    # Also check for single-char tokens in non-standard placements
    if len(token) == 1 and token.isalpha():
        return True
    return False

# Count HT by folio
ht_by_folio = defaultdict(int)
total_by_folio = defaultdict(int)

for _, row in df.iterrows():
    folio = row['folio']
    token = row['word']
    placement = row.get('placement', '')

    if pd.isna(token):
        continue

    total_by_folio[folio] += 1

    # HT identification (simplified - single chars or margin placements)
    if is_ht_candidate(token, placement):
        ht_by_folio[folio] += 1

# =============================================================================
# Compute PP count by A record (folio:line)
# =============================================================================
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna())
}).reset_index()
a_records.columns = ['folio', 'line', 'middles']

# Compute PP count for each A record
a_records['pp_count'] = a_records['middles'].apply(lambda m: len(m & b_middles))
a_records['record_id'] = a_records['folio'] + ':' + a_records['line'].astype(str)

print(f"\nA records analyzed: {len(a_records)}")
print(f"PP count range: {a_records['pp_count'].min()} - {a_records['pp_count'].max()}")

# Aggregate PP by folio (mean PP count of A records in that folio)
pp_by_folio = a_records.groupby('folio')['pp_count'].agg(['mean', 'sum', 'count'])
pp_by_folio.columns = ['pp_mean', 'pp_sum', 'a_record_count']

# =============================================================================
# TEST 1: Folio-level PP vs HT correlation
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: Folio-Level PP vs HT Correlation")
print("=" * 70)

# Merge PP and HT data by folio
folio_data = []
for folio in pp_by_folio.index:
    if folio in total_by_folio and total_by_folio[folio] > 0:
        ht_density = ht_by_folio[folio] / total_by_folio[folio]
        folio_data.append({
            'folio': folio,
            'pp_mean': pp_by_folio.loc[folio, 'pp_mean'],
            'pp_sum': pp_by_folio.loc[folio, 'pp_sum'],
            'a_records': pp_by_folio.loc[folio, 'a_record_count'],
            'ht_count': ht_by_folio[folio],
            'total_tokens': total_by_folio[folio],
            'ht_density': ht_density
        })

folio_df = pd.DataFrame(folio_data)
print(f"\nFolios with both PP and HT data: {len(folio_df)}")

if len(folio_df) > 10:
    # Correlation: PP mean vs HT density
    r_mean, p_mean = stats.pearsonr(folio_df['pp_mean'], folio_df['ht_density'])
    print(f"\nPP mean vs HT density:")
    print(f"  r = {r_mean:.4f}, p = {p_mean:.4f}")

    # Correlation: PP sum vs HT count
    r_sum, p_sum = stats.pearsonr(folio_df['pp_sum'], folio_df['ht_count'])
    print(f"\nPP sum vs HT count:")
    print(f"  r = {r_sum:.4f}, p = {p_sum:.4f}")

    # Spearman (rank) correlation
    rho, p_rho = stats.spearmanr(folio_df['pp_mean'], folio_df['ht_density'])
    print(f"\nSpearman (PP mean vs HT density):")
    print(f"  rho = {rho:.4f}, p = {p_rho:.4f}")

# =============================================================================
# TEST 2: PP count bins vs HT density
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: PP Count Bins vs Mean HT Density")
print("=" * 70)

# Bin folios by mean PP count
folio_df['pp_bin'] = pd.cut(folio_df['pp_mean'], bins=[0, 2, 4, 6, 8, 20], labels=['0-2', '2-4', '4-6', '6-8', '8+'])

print("\nHT density by PP bin:")
for pp_bin in ['0-2', '2-4', '4-6', '6-8', '8+']:
    subset = folio_df[folio_df['pp_bin'] == pp_bin]
    if len(subset) > 0:
        mean_ht = subset['ht_density'].mean()
        std_ht = subset['ht_density'].std()
        n = len(subset)
        print(f"  PP {pp_bin}: HT density = {mean_ht*100:.2f}% +/- {std_ht*100:.2f}% (n={n})")

# =============================================================================
# TEST 3: Use actual HT data from phases if available
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: Using Structural HT Data (if available)")
print("=" * 70)

try:
    # Try to load HT density data from phases
    import glob
    ht_files = glob.glob('phases/**/ht_*.json', recursive=True) + glob.glob('results/**/ht_*.json', recursive=True)
    print(f"Found {len(ht_files)} potential HT data files")

    # Also check for folio-level metrics
    metrics_files = glob.glob('phases/**/folio_metrics*.json', recursive=True)
    print(f"Found {len(metrics_files)} potential folio metrics files")

except Exception as e:
    print(f"Could not search for HT data files: {e}")

# =============================================================================
# TEST 4: A-record level analysis (PP count vs HT in same folio)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: A-Record PP Count vs Folio HT Density")
print("=" * 70)

# For each A record, get the HT density of its folio
a_records_with_ht = a_records.copy()
a_records_with_ht['folio_ht_density'] = a_records_with_ht['folio'].map(
    lambda f: ht_by_folio[f] / total_by_folio[f] if total_by_folio[f] > 0 else np.nan
)

# Drop records without HT data
a_records_with_ht = a_records_with_ht.dropna(subset=['folio_ht_density'])

print(f"\nA records with HT data: {len(a_records_with_ht)}")

if len(a_records_with_ht) > 100:
    r, p = stats.pearsonr(a_records_with_ht['pp_count'], a_records_with_ht['folio_ht_density'])
    print(f"\nPP count vs folio HT density:")
    print(f"  r = {r:.4f}, p = {p:.4f}")

    # By PP count bucket
    print("\nMean folio HT density by A-record PP count:")
    for pp_low, pp_high in [(0, 2), (3, 5), (6, 8), (9, 12), (13, 20)]:
        subset = a_records_with_ht[(a_records_with_ht['pp_count'] >= pp_low) &
                                    (a_records_with_ht['pp_count'] <= pp_high)]
        if len(subset) > 0:
            mean_ht = subset['folio_ht_density'].mean()
            n = len(subset)
            print(f"  PP {pp_low}-{pp_high}: HT = {mean_ht*100:.2f}% (n={n})")

# =============================================================================
# TEST 5: B-side complexity vs PP interaction
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: Does PP Mediate B Complexity -> HT?")
print("=" * 70)

# Get B token count and vocabulary richness per folio
b_by_folio = df_b.groupby('folio').agg({
    'word': 'count',
    'middle': lambda x: len(set(x.dropna()))
}).reset_index()
b_by_folio.columns = ['folio', 'b_token_count', 'b_middle_diversity']

# Merge with folio_df
if len(folio_df) > 0:
    analysis_df = folio_df.merge(b_by_folio, on='folio', how='inner')

    if len(analysis_df) > 10:
        print(f"\nFolios for mediation analysis: {len(analysis_df)}")

        # Direct: B complexity -> HT
        r_direct, p_direct = stats.pearsonr(analysis_df['b_middle_diversity'], analysis_df['ht_density'])
        print(f"\nB MIDDLE diversity vs HT density (direct):")
        print(f"  r = {r_direct:.4f}, p = {p_direct:.4f}")

        # Does PP count correlate with B complexity?
        r_pp_b, p_pp_b = stats.pearsonr(analysis_df['pp_mean'], analysis_df['b_middle_diversity'])
        print(f"\nPP mean vs B MIDDLE diversity:")
        print(f"  r = {r_pp_b:.4f}, p = {p_pp_b:.4f}")

        # Partial correlation: B complexity -> HT controlling for PP
        # Using simple residualization
        from scipy.stats import linregress

        # Residualize HT on PP
        slope, intercept, _, _, _ = linregress(analysis_df['pp_mean'], analysis_df['ht_density'])
        ht_resid = analysis_df['ht_density'] - (slope * analysis_df['pp_mean'] + intercept)

        # Residualize B diversity on PP
        slope2, intercept2, _, _, _ = linregress(analysis_df['pp_mean'], analysis_df['b_middle_diversity'])
        b_resid = analysis_df['b_middle_diversity'] - (slope2 * analysis_df['pp_mean'] + intercept2)

        r_partial, p_partial = stats.pearsonr(b_resid, ht_resid)
        print(f"\nB diversity vs HT (controlling for PP):")
        print(f"  r_partial = {r_partial:.4f}, p = {p_partial:.4f}")

        if abs(r_direct) > abs(r_partial) + 0.1:
            print("\n  -> PP partially mediates B complexity -> HT relationship")
        else:
            print("\n  -> No evidence of PP mediation")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
Responsibility Substitution Hypothesis:
  If PP provides execution freedom, HT (human vigilance) may decrease.

Key correlations to check:
  - PP vs HT: negative = substitution (more freedom, less vigilance)
  - PP vs HT: positive = complementary (more freedom needs more oversight)
  - PP vs HT: zero = independent systems
""")
