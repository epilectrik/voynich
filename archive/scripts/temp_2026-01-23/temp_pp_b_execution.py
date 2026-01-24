#!/usr/bin/env python3
"""
Test: Do PP profiles predict B-side execution behavior?

If PP MIDDLEs function as compatibility carriers (C504), then A records with
different PP profiles should produce different B vocabulary patterns when
filtered through the same AZC constraints.

Test approach:
1. Group A records by their PP profile (Animal-signature vs Water-signature vs Other)
2. For each group, compute the B classes that survive strict filtering
3. Check if different PP profiles yield different B execution profiles
"""

import json
import pandas as pd
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

# Load transcription
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']  # H track only

# Load token -> class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8') as f:
    class_map = json.load(f)
token_to_class = class_map['token_to_class']

# Get B tokens by folio
b_df = df[(df['language'] == 'B') & (~df['word'].isna()) & (~df['word'].str.contains('\*', na=False))]
b_tokens = set(b_df['word'].unique())

# Get A tokens and their folios
a_df = df[(df['language'] == 'A') & (~df['word'].isna()) & (~df['word'].str.contains('\*', na=False))]

# Define PP MIDDLEs (from C504 analysis)
pp_middles = {'a', 'o', 'y', 'e', 'i', 'l', 'r', 'ar', 'or', 'ol', 'al', 'an',
              'am', 'ain', 'air', 'aiin', 'dy', 'ey', 'ky', 'ty', 'od', 'ed',
              'te', 'ho', 'ke', 'yt', 'os', 'eo', 'ai', 'oi', 'ee', 'ii'}

# Define signature PPs
animal_signature = {'te', 'ho', 'ke'}
water_signature = {'te', 'yt', 'os', 'eo'}

def extract_middle(token):
    """Extract MIDDLE from token (simplified heuristic)."""
    if not token or len(token) < 2:
        return None
    # Remove common prefixes
    prefixes = ['qo', 'ch', 'sh', 'da', 'ol', 'ok', 'ot', 'ct', 'sa', 'so']
    t = token
    for p in prefixes:
        if t.startswith(p):
            t = t[len(p):]
            break
    # Remove common suffixes
    suffixes = ['dy', 'y', 'n', 'l', 'm', 'g', 'd', 's', 'r']
    for s in sorted(suffixes, key=len, reverse=True):
        if t.endswith(s) and len(t) > len(s):
            t = t[:-len(s)]
            break
    return t if t else None

# Group A records by folio (approximation of "record")
a_records = defaultdict(set)  # folio -> set of tokens
for _, row in a_df.iterrows():
    folio = row['folio']
    token = row['word']
    a_records[folio].add(token)

# Compute PP profile for each A "record" (folio)
record_profiles = {}
for folio, tokens in a_records.items():
    middles = set()
    for t in tokens:
        m = extract_middle(t)
        if m and m in pp_middles:
            middles.add(m)

    # Classify profile
    has_animal = len(middles & animal_signature) >= 2
    has_water = len(middles & water_signature) >= 2

    if has_animal and not has_water:
        profile = 'ANIMAL'
    elif has_water and not has_animal:
        profile = 'WATER'
    elif has_animal and has_water:
        profile = 'OVERLAP'
    else:
        profile = 'OTHER'

    record_profiles[folio] = {
        'profile': profile,
        'pp_count': len(middles),
        'pp_middles': middles,
        'token_count': len(tokens)
    }

# Count profile distribution
profile_counts = Counter(r['profile'] for r in record_profiles.values())
print("=" * 70)
print("A RECORD PP PROFILE DISTRIBUTION")
print("=" * 70)
for profile, cnt in profile_counts.most_common():
    print(f"  {profile}: {cnt} records")

# Now compute B class survival for each profile group
print("\n" + "=" * 70)
print("B CLASS SURVIVAL BY PP PROFILE")
print("=" * 70)

# Get all B classes used
b_classes = set()
for token in b_tokens:
    if token in token_to_class:
        b_classes.add(token_to_class[token])

print(f"\nTotal B classes in use: {len(b_classes)}")

# For each profile group, compute which B classes would survive
# (This is simplified - full implementation would use AZC filtering)

# Instead, let's look at PP MIDDLE correlation with specific B vocabulary
# Get B tokens that co-occur with each PP profile

def get_b_vocabulary_for_profile(profile_type):
    """Get B tokens from folios where A records have this profile."""
    # This is a simplification - in reality we'd trace through AZC
    # For now, look at H-section folios that have A records with this profile
    profile_folios = [f for f, r in record_profiles.items() if r['profile'] == profile_type]

    # Get B tokens from same section (approximation)
    b_vocab = Counter()
    for folio in profile_folios:
        # Get B tokens from nearby folios (same quire or section)
        folio_b = b_df[b_df['folio'].str.startswith(folio[:2])]
        for t in folio_b['word']:
            if t in token_to_class:
                b_vocab[t] += 1
    return b_vocab

# This approach is too indirect. Let me try a different angle:
# Look at PP MIDDLE presence in A and correlate with B class usage

print("\n" + "=" * 70)
print("PP MIDDLE -> B CLASS CORRELATION (Direct Test)")
print("=" * 70)

# For each PP MIDDLE, check if A records containing it
# correlate with specific B class distributions

# First, compute which B classes each A folio "activates"
# (uses strict filtering from C502)

# Load the strict survival data if available
try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/cosurvival_analysis.json', encoding='utf-8') as f:
        cosurvival = json.load(f)

    print("\nUsing CLASS_COSURVIVAL_TEST data for strict survival patterns")

    # Get PP distribution across survival patterns
    survival_patterns = cosurvival.get('unique_patterns', 0)
    print(f"Unique survival patterns: {survival_patterns}")

except FileNotFoundError:
    print("\nCould not load cosurvival data")

# Alternative: Direct PP -> class count correlation
print("\n" + "=" * 70)
print("PP MIDDLES IN A RECORDS: DETAILED ANALYSIS")
print("=" * 70)

# Compute PP MIDDLE frequency across all A records
all_pp_middles = Counter()
records_with_pp = defaultdict(list)  # pp_middle -> list of folios

for folio, record in record_profiles.items():
    for pp in record['pp_middles']:
        all_pp_middles[pp] += 1
        records_with_pp[pp].append(folio)

print("\nPP MIDDLE frequency in A records:")
for pp, cnt in all_pp_middles.most_common(20):
    pct = 100 * cnt / len(record_profiles)
    print(f"  '{pp}': {cnt} records ({pct:.1f}%)")

# Check Animal signature co-occurrence
print("\n" + "-" * 50)
print("ANIMAL SIGNATURE CO-OCCURRENCE:")
te_records = set(records_with_pp.get('te', []))
ho_records = set(records_with_pp.get('ho', []))
ke_records = set(records_with_pp.get('ke', []))

print(f"  'te' records: {len(te_records)}")
print(f"  'ho' records: {len(ho_records)}")
print(f"  'ke' records: {len(ke_records)}")
print(f"  'te' AND 'ho': {len(te_records & ho_records)}")
print(f"  'te' AND 'ke': {len(te_records & ke_records)}")
print(f"  'ho' AND 'ke': {len(ho_records & ke_records)}")
print(f"  ALL THREE: {len(te_records & ho_records & ke_records)}")

# Check Water signature co-occurrence
print("\n" + "-" * 50)
print("WATER SIGNATURE CO-OCCURRENCE:")
yt_records = set(records_with_pp.get('yt', []))
os_records = set(records_with_pp.get('os', []))
eo_records = set(records_with_pp.get('eo', []))

print(f"  'yt' records: {len(yt_records)}")
print(f"  'os' records: {len(os_records)}")
print(f"  'eo' records: {len(eo_records)}")
print(f"  'te' AND 'yt': {len(te_records & yt_records)}")
print(f"  'te' AND 'os': {len(te_records & os_records)}")

# Profile overlap analysis
print("\n" + "-" * 50)
print("ANIMAL vs WATER OVERLAP:")
animal_all = te_records | ho_records | ke_records
water_all = yt_records | os_records | eo_records
print(f"  Records with ANY animal PP: {len(animal_all)}")
print(f"  Records with ANY water PP: {len(water_all)}")
print(f"  Records with BOTH: {len(animal_all & water_all)}")
print(f"  Animal-only: {len(animal_all - water_all)}")
print(f"  Water-only: {len(water_all - animal_all)}")

# Test if these profiles predict different B class usage
print("\n" + "=" * 70)
print("PP PROFILE -> B CLASS SURVIVAL (Chi-Square Test)")
print("=" * 70)

# For the Chi-square test, we need to check if PP profile is independent of B class survival
# Using the cosurvival data

try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json', encoding='utf-8') as f:
        survivors = json.load(f)

    # Map A records to their class survival count
    record_survival = {}
    for record_id, data in survivors['records'].items():
        record_survival[record_id] = len(data['surviving_classes'])

    # Now correlate with PP profile
    print("\nMean B classes surviving by PP profile:")
    profile_survival = defaultdict(list)

    # Match by section/folio (approximation)
    for folio, profile_data in record_profiles.items():
        # Find matching record
        for record_id, survival_count in record_survival.items():
            if folio in record_id or record_id in folio:
                profile_survival[profile_data['profile']].append(survival_count)
                break

    for profile in ['ANIMAL', 'WATER', 'OVERLAP', 'OTHER']:
        if profile_survival[profile]:
            mean_survival = np.mean(profile_survival[profile])
            std_survival = np.std(profile_survival[profile])
            n = len(profile_survival[profile])
            print(f"  {profile}: {mean_survival:.1f} +/- {std_survival:.1f} classes (n={n})")

    # ANOVA test
    groups = [profile_survival[p] for p in ['ANIMAL', 'WATER', 'OVERLAP', 'OTHER'] if profile_survival[p]]
    if len(groups) >= 2:
        f_stat, p_val = stats.f_oneway(*groups)
        print(f"\nANOVA: F={f_stat:.2f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  -> PP profile SIGNIFICANTLY predicts B class survival")
        else:
            print("  -> PP profile does NOT significantly predict B class survival")

except Exception as e:
    print(f"Could not perform survival analysis: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
