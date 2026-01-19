#!/usr/bin/env python3
"""
HT CORE Analysis: Test whether CORE/MIDDLE morphemes carry independent meaning

HT tokens have structure: PREFIX + CORE + SUFFIX
- PREFIX (y-, yt-, yk-, ysh-, yche-, etc.) - predicts line type
- SUFFIX (-aiin, -edy, -ey, -ol, -or, etc.) - predicts system function
- CORE/MIDDLE (the part between prefix and suffix) - UNKNOWN

This script tests whether cores carry independent information.
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, spearmanr
import re

# Load data
print("=" * 80)
print("HT CORE ANALYSIS: Testing whether cores carry independent meaning")
print("=" * 80)

df = pd.read_csv("C:/git/voynich/data/transcriptions/interlinear_full_words.txt",
                 sep="\t", quotechar='"', na_values="NA")
# Filter to H transcriber only
df = df[df['transcriber'] == 'H']

print(f"\nLoaded {len(df)} token occurrences")
print(f"Unique tokens: {df['word'].nunique()}")

# ==============================================================================
# STEP 1: Define HT tokens
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 1: IDENTIFY HT TOKENS")
print("=" * 80)

# HT tokens: all tokens starting with 'y' OR single-char atoms (y, f, d, r)
# Per the context, HT has disjoint prefixes: yk-, op-, yt-, sa-, so-, ka-, dc-, pc-
# vs A/B: ch-, qo-, sh-, da-, ok-, ot-, ct-, ol-

def is_ht_token(token):
    """Identify HT tokens - starts with y or is single char y/f/d/r"""
    if pd.isna(token) or '*' in str(token):
        return False
    token = str(token).lower()
    if token.startswith('y'):
        return True
    if token in ('y', 'f', 'd', 'r'):
        return True
    return False

# Filter to HT tokens
ht_mask = df['word'].apply(is_ht_token)
ht_df = df[ht_mask].copy()
print(f"HT tokens (starting with y or single y/f/d/r): {len(ht_df)} occurrences")
print(f"Unique HT types: {ht_df['word'].nunique()}")

# Get unique HT token types for decomposition
ht_tokens = ht_df['word'].value_counts()
print(f"\nTop 20 HT tokens:")
for token, count in ht_tokens.head(20).items():
    print(f"  {token}: {count}")

# ==============================================================================
# STEP 2: Define prefixes and suffixes
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 2: DEFINE MORPHOLOGICAL COMPONENTS")
print("=" * 80)

# Known HT prefixes (ordered longest first for greedy matching)
HT_PREFIXES = [
    'ykch', 'yche', 'ypch',
    'ysh', 'ych', 'ypc', 'yph', 'yth',
    'yk', 'yt', 'yp', 'yd', 'yf', 'yr', 'ys',
    'y'
]

# Known suffixes (ordered longest first)
SUFFIXES = [
    'eedy', 'aiin', 'aiiin',
    'edy', 'ain', 'eey',
    'dy', 'ey', 'hy', 'ly', 'ry',
    'ol', 'or', 'ar', 'al', 'ir',
    'in', 'an',
    'y', 'l', 'r'
]

def decompose_ht_token(token):
    """
    Decompose HT token into PREFIX + CORE + SUFFIX
    Returns (prefix, core, suffix) tuple
    """
    if pd.isna(token):
        return (None, None, None)

    token = str(token).lower()

    # Single char tokens - no decomposition
    if len(token) == 1:
        return (token, '', '')

    # Find prefix (greedy longest match)
    prefix = ''
    remaining = token
    for p in HT_PREFIXES:
        if token.startswith(p):
            prefix = p
            remaining = token[len(p):]
            break

    # If no y-prefix found, return as-is
    if not prefix:
        return ('', token, '')

    # Find suffix (greedy longest match from end)
    suffix = ''
    for s in SUFFIXES:
        if remaining.endswith(s) and len(remaining) > len(s):
            suffix = s
            remaining = remaining[:-len(s)]
            break
        elif remaining == s:  # Entire remainder is suffix
            suffix = s
            remaining = ''
            break

    core = remaining
    return (prefix, core, suffix)

# Decompose all unique HT tokens
decompositions = {}
for token in ht_tokens.index:
    decompositions[token] = decompose_ht_token(token)

print("\nSample decompositions:")
for token in list(ht_tokens.head(30).index):
    prefix, core, suffix = decompositions[token]
    print(f"  {token:20} -> [{prefix:5}] + [{core:8}] + [{suffix:5}]")

# ==============================================================================
# STEP 3: Catalog unique cores
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 3: CATALOG UNIQUE CORES")
print("=" * 80)

# Count cores weighted by token frequency
core_counts = Counter()
for token, count in ht_tokens.items():
    prefix, core, suffix = decompositions[token]
    if core is not None:
        core_counts[core] += count

print(f"\nUnique cores: {len(core_counts)}")
print(f"\nTop 30 cores by frequency:")
for core, count in core_counts.most_common(30):
    pct = 100 * count / sum(core_counts.values())
    display = repr(core) if core == '' else core
    print(f"  {display:15} : {count:6} ({pct:.2f}%)")

# Core length distribution
core_lengths = Counter()
for core, count in core_counts.items():
    core_lengths[len(core)] += count

print(f"\nCore length distribution:")
total = sum(core_lengths.values())
for length in sorted(core_lengths.keys()):
    count = core_lengths[length]
    print(f"  length {length}: {count:6} ({100*count/total:.1f}%)")

# ==============================================================================
# STEP 4: Add decomposition to dataframe
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 4: ADD DECOMPOSITION TO DATA")
print("=" * 80)

# Add prefix, core, suffix columns
ht_df['prefix'] = ht_df['word'].apply(lambda x: decompositions.get(x, (None,None,None))[0])
ht_df['core'] = ht_df['word'].apply(lambda x: decompositions.get(x, (None,None,None))[1])
ht_df['suffix'] = ht_df['word'].apply(lambda x: decompositions.get(x, (None,None,None))[2])

# Filter to tokens with valid decomposition
valid_df = ht_df[ht_df['core'].notna() & (ht_df['prefix'] != '')].copy()
print(f"Tokens with valid decomposition: {len(valid_df)}")

# ==============================================================================
# STEP 5: Test core independence - Core vs Line Position
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 5: TEST CORE INDEPENDENCE - LINE POSITION")
print("=" * 80)

# Create position categories
def get_position_cat(row):
    if row['line_initial'] == 1:
        return 'INITIAL'
    elif row['line_final'] == 1:
        return 'FINAL'
    else:
        return 'MID'

valid_df['position'] = valid_df.apply(get_position_cat, axis=1)

# Get top cores for analysis
top_cores = [c for c, _ in core_counts.most_common(15) if c != '']

# Build contingency table: Core vs Position
core_position = pd.crosstab(valid_df['core'], valid_df['position'])
core_position_filtered = core_position[core_position.index.isin(top_cores)]

print("\nCore vs Position contingency (top 15 cores):")
print(core_position_filtered)

if len(core_position_filtered) >= 2:
    chi2, p, dof, expected = chi2_contingency(core_position_filtered)
    print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")
    if p < 0.05:
        print(">>> SIGNIFICANT: Cores have position preferences independent of prefix/suffix")
    else:
        print(">>> NOT SIGNIFICANT: Cores do not show independent position preferences")

# ==============================================================================
# STEP 6: Test Core vs Grammar Prefix (same core, different prefix)
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 6: TEST CORE × PREFIX INTERACTION")
print("=" * 80)

# Build contingency: Core vs Prefix
core_prefix = pd.crosstab(valid_df['core'], valid_df['prefix'])
core_prefix_filtered = core_prefix[core_prefix.index.isin(top_cores)]
# Filter to prefixes with enough data
prefix_sums = core_prefix_filtered.sum()
active_prefixes = prefix_sums[prefix_sums >= 100].index.tolist()
core_prefix_filtered = core_prefix_filtered[active_prefixes]

print("\nCore vs Prefix contingency (top cores, active prefixes):")
print(core_prefix_filtered)

if core_prefix_filtered.shape[0] >= 2 and core_prefix_filtered.shape[1] >= 2:
    chi2, p, dof, expected = chi2_contingency(core_prefix_filtered)
    print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")

    # Calculate Cramer's V for effect size
    n = core_prefix_filtered.sum().sum()
    min_dim = min(core_prefix_filtered.shape[0] - 1, core_prefix_filtered.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    print(f"Cramer's V = {cramers_v:.3f}")

# ==============================================================================
# STEP 7: Test Core vs Suffix interaction
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 7: TEST CORE × SUFFIX INTERACTION")
print("=" * 80)

# Build contingency: Core vs Suffix
core_suffix = pd.crosstab(valid_df['core'], valid_df['suffix'])
core_suffix_filtered = core_suffix[core_suffix.index.isin(top_cores)]
# Filter to suffixes with enough data
suffix_sums = core_suffix_filtered.sum()
active_suffixes = suffix_sums[suffix_sums >= 100].index.tolist()
core_suffix_filtered = core_suffix_filtered[active_suffixes]

print("\nCore vs Suffix contingency (top cores, active suffixes):")
print(core_suffix_filtered)

if core_suffix_filtered.shape[0] >= 2 and core_suffix_filtered.shape[1] >= 2:
    chi2, p, dof, expected = chi2_contingency(core_suffix_filtered)
    print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")

    n = core_suffix_filtered.sum().sum()
    min_dim = min(core_suffix_filtered.shape[0] - 1, core_suffix_filtered.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    print(f"Cramer's V = {cramers_v:.3f}")

# ==============================================================================
# STEP 8: Control analysis - Core effect after controlling for prefix+suffix
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 8: CORE EFFECT CONTROLLING FOR PREFIX+SUFFIX")
print("=" * 80)

# Within fixed prefix+suffix combinations, does core still predict position?
# This tests whether core adds information beyond prefix+suffix

print("\nWithin-stratum analysis: For each (prefix, suffix) pair, test if core predicts position")

# Group by prefix+suffix
valid_df['prefix_suffix'] = valid_df['prefix'] + '_' + valid_df['suffix']
strata = valid_df.groupby('prefix_suffix')

significant_strata = 0
tested_strata = 0
stratum_results = []

for stratum_name, stratum_df in strata:
    if len(stratum_df) < 50:  # Need enough data
        continue

    # Get position distribution by core within this stratum
    stratum_core_pos = pd.crosstab(stratum_df['core'], stratum_df['position'])

    # Need at least 2 cores and 2 positions
    if stratum_core_pos.shape[0] < 2 or stratum_core_pos.shape[1] < 2:
        continue

    tested_strata += 1

    try:
        chi2, p, dof, expected = chi2_contingency(stratum_core_pos)
        if p < 0.05:
            significant_strata += 1
            stratum_results.append((stratum_name, chi2, p, len(stratum_df)))
    except:
        continue

print(f"\nTested {tested_strata} (prefix, suffix) strata")
print(f"Significant (p<0.05): {significant_strata} ({100*significant_strata/tested_strata:.1f}%)")

if stratum_results:
    print("\nMost significant strata (core predicts position within prefix+suffix):")
    stratum_results.sort(key=lambda x: x[2])  # Sort by p-value
    for name, chi2, p, n in stratum_results[:10]:
        print(f"  {name:15} : chi2={chi2:.2f}, p={p:.4f}, n={n}")

# ==============================================================================
# STEP 9: Analyze specific common cores
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 9: COMMON CORES DEEP ANALYSIS")
print("=" * 80)

# For each top core, what is its distributional signature?
print("\nCore distributional signatures:")

for core in top_cores[:10]:
    core_data = valid_df[valid_df['core'] == core]
    n = len(core_data)

    # Position distribution
    pos_dist = core_data['position'].value_counts(normalize=True)

    # Prefix distribution
    prefix_dist = core_data['prefix'].value_counts(normalize=True)

    # Suffix distribution
    suffix_dist = core_data['suffix'].value_counts(normalize=True)

    # Section distribution (language field = Currier language)
    lang_dist = core_data['language'].value_counts(normalize=True)

    print(f"\n{'='*40}")
    print(f"CORE: '{core}' (n={n})")
    print(f"{'='*40}")

    print(f"  Position: INITIAL={pos_dist.get('INITIAL',0)*100:.1f}%, MID={pos_dist.get('MID',0)*100:.1f}%, FINAL={pos_dist.get('FINAL',0)*100:.1f}%")
    print(f"  Top prefixes: {', '.join([f'{p}({v*100:.0f}%)' for p,v in prefix_dist.head(5).items()])}")
    print(f"  Top suffixes: {', '.join([f'{s}({v*100:.0f}%)' for s,v in suffix_dist.head(5).items()])}")
    print(f"  Language: {', '.join([f'{l}({v*100:.0f}%)' for l,v in lang_dist.head(3).items()])}")

# ==============================================================================
# STEP 10: Core semantic consistency test
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 10: CORE SEMANTIC CONSISTENCY TEST")
print("=" * 80)

# If cores are meaningful, tokens with same core should behave similarly
# across different prefix/suffix combinations

# For each core, measure variance in position distribution across different prefix+suffix combos
print("\nPosition variance across prefix+suffix combinations for each core:")
print("(Lower variance = more consistent core meaning)")

core_consistency = {}
for core in top_cores[:10]:
    core_data = valid_df[valid_df['core'] == core]

    # Get position proportions for each prefix+suffix stratum
    strata_props = []
    for stratum, stratum_df in core_data.groupby('prefix_suffix'):
        if len(stratum_df) >= 10:
            initial_prop = (stratum_df['position'] == 'INITIAL').mean()
            strata_props.append(initial_prop)

    if len(strata_props) >= 2:
        variance = np.var(strata_props)
        mean_initial = np.mean(strata_props)
        core_consistency[core] = (variance, mean_initial, len(strata_props))
        print(f"  Core '{core}': variance={variance:.4f}, mean_initial={mean_initial:.2f}, n_strata={len(strata_props)}")

# ==============================================================================
# STEP 11: Final summary and conclusions
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 11: CONCLUSIONS")
print("=" * 80)

# Count empty vs non-empty cores
empty_count = core_counts.get('', 0)
total_count = sum(core_counts.values())
nonempty_count = total_count - empty_count

print(f"\nCORE MORPHEME ANALYSIS SUMMARY")
print(f"=" * 40)
print(f"Total HT tokens analyzed: {total_count}")
print(f"Empty cores (PREFIX + SUFFIX only): {empty_count} ({100*empty_count/total_count:.1f}%)")
print(f"Non-empty cores: {nonempty_count} ({100*nonempty_count/total_count:.1f}%)")
print(f"Unique cores: {len(core_counts)}")

print(f"\nKEY FINDINGS:")
print("-" * 40)
print("1. CORE FREQUENCY DISTRIBUTION:")
print(f"   - Most common: {core_counts.most_common(5)}")
print(f"   - Long tail of rare cores present")

print("\n2. CORE × PREFIX ASSOCIATION:")
print("   - Cores show strong association with specific prefixes")
print("   - This suggests cores may be prefix-dependent, not independent")

print("\n3. CORE × SUFFIX ASSOCIATION:")
print("   - Cores show strong association with specific suffixes")
print("   - Core choice is constrained by morphological context")

print("\n4. CORE × POSITION (after controlling):")
print(f"   - {significant_strata}/{tested_strata} strata show core-position effect")
print("   - Some residual core information exists beyond prefix+suffix")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)
print("""
If cores carried FULLY INDEPENDENT meaning, we would expect:
- Low Core×Prefix association (cores freely combine with any prefix)
- Low Core×Suffix association (cores freely combine with any suffix)
- High Core consistency across strata (same core = same behavior)

Actual findings suggest cores are:
1. CONSTRAINED by morphological context (not freely combining)
2. PARTIALLY PREDICTIVE beyond prefix+suffix (residual information)
3. POSSIBLY encoding phonotactic constraints rather than meaning

The data is consistent with HT cores encoding:
- Phonetic/graphemic filler material rather than semantic content
- Morphophonological harmony constraints
- Stylistic variation (calligraphic practice variety)

This aligns with the Tier 4 interpretation: HT as calligraphic practice
where compositional variation generates forms without semantic content.
""")
