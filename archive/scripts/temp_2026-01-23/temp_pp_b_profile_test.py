#!/usr/bin/env python3
"""
Test: Do PP profiles predict B class survival at the record level?

Record = A line (not folio)
Methodology:
1. Identify Animal records via RI MIDDLEs (eyd, chald, hyd, etc.)
2. Compute their PP profile
3. Compute their B class survival pattern (from CLASS_COSURVIVAL_TEST)
4. Compare to baseline records
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

# Get A tokens with MIDDLEs
df_a = df[(df['language'] == 'A') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

# Get B tokens with MIDDLEs
df_b = df[(df['language'] == 'B') & (~df['word'].isna()) & (~df['word'].str.contains(r'\*', na=False))].copy()
df_b['middle'] = df_b['word'].apply(extract_middle)

# Compute shared MIDDLEs (PP)
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles  # These are PP MIDDLEs

print("=" * 70)
print("PP -> B CLASS SURVIVAL TEST (Record Level)")
print("=" * 70)

print(f"\nA MIDDLEs: {len(a_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"Shared (PP): {len(shared_middles)}")

# Build A records (line level)
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': lambda x: list(x)
}).reset_index()
a_records.columns = ['folio', 'line', 'middles', 'words']

# Create record ID
a_records['record_id'] = a_records['folio'] + ':' + a_records['line'].astype(str)

print(f"Total A records (lines): {len(a_records)}")

# RI MIDDLEs for animal records (from identify_animals.py)
animal_ri_middles = {'eyd', 'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'teold', 'olar', 'hod'}

# Identify animal records
animal_records = []
for _, rec in a_records.iterrows():
    if rec['middles'] & animal_ri_middles:
        animal_records.append(rec)

print(f"Animal records (containing animal RI MIDDLEs): {len(animal_records)}")

# Compute PP profile for animal vs baseline records
def compute_pp_profile(records):
    """Compute PP MIDDLE frequencies across records."""
    pp_counts = Counter()
    for rec in records:
        rec_pp = rec['middles'] & shared_middles
        for pp in rec_pp:
            pp_counts[pp] += 1
    return pp_counts

animal_pp = compute_pp_profile(animal_records)
all_pp = compute_pp_profile([rec for _, rec in a_records.iterrows()])

print("\n" + "-" * 50)
print("PP PROFILE: Animal Records vs All Records")
print("-" * 50)

# Compute enrichment for top PPs
print("\nPP MIDDLE enrichment in animal records:")
for pp, _ in all_pp.most_common(20):
    animal_rate = animal_pp[pp] / len(animal_records) if len(animal_records) > 0 else 0
    baseline_rate = all_pp[pp] / len(a_records)
    enrichment = animal_rate / baseline_rate if baseline_rate > 0 else 0
    if animal_pp[pp] > 0:
        print(f"  '{pp}': {animal_pp[pp]}/{len(animal_records)} ({animal_rate*100:.1f}%) vs {baseline_rate*100:.1f}% baseline = {enrichment:.2f}x")

# Test specific signature PPs
print("\n" + "-" * 50)
print("SIGNATURE PP ENRICHMENT (Animal):")
print("-" * 50)

signature_pps = ['te', 'ho', 'ke', 'yt', 'os', 'eo']
for pp in signature_pps:
    animal_rate = animal_pp[pp] / len(animal_records) if len(animal_records) > 0 else 0
    baseline_rate = all_pp[pp] / len(a_records) if all_pp[pp] > 0 else 0
    enrichment = animal_rate / baseline_rate if baseline_rate > 0 else 0
    print(f"  '{pp}': {animal_rate*100:.1f}% (animal) vs {baseline_rate*100:.1f}% (baseline) = {enrichment:.2f}x")

# =============================================================================
# Now test if PP profile predicts B class survival
# =============================================================================

print("\n" + "=" * 70)
print("TEST: Do animal records have different B class survival?")
print("=" * 70)

# Load class survival data
try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json', encoding='utf-8') as f:
        survivors = json.load(f)

    # Get survival counts for animal vs baseline records
    animal_survival = []
    baseline_survival = []

    # Build set of animal record IDs for fast lookup
    animal_record_ids = set(rec['record_id'] for rec in animal_records)

    for record_data in survivors['records']:
        record_id = record_data['a_record']
        survival_count = record_data['surviving_class_count']

        if record_id in animal_record_ids:
            animal_survival.append(survival_count)
        else:
            baseline_survival.append(survival_count)

    print(f"\nAnimal records with survival data: {len(animal_survival)}")
    print(f"Baseline records with survival data: {len(baseline_survival)}")

    if animal_survival and baseline_survival:
        animal_mean = np.mean(animal_survival)
        baseline_mean = np.mean(baseline_survival)

        print(f"\nMean B classes surviving:")
        print(f"  Animal records: {animal_mean:.1f} +/- {np.std(animal_survival):.1f}")
        print(f"  Baseline records: {baseline_mean:.1f} +/- {np.std(baseline_survival):.1f}")

        # Statistical test
        t_stat, p_val = stats.ttest_ind(animal_survival, baseline_survival)
        print(f"\nT-test: t={t_stat:.2f}, p={p_val:.4f}")

        if p_val < 0.05:
            print("  -> Animal PP profile SIGNIFICANTLY predicts different B class survival")
        else:
            print("  -> No significant difference in B class survival")

except FileNotFoundError:
    print("Could not load survival data")

# =============================================================================
# Alternative: Use folio-level matching
# =============================================================================
print("\n" + "=" * 70)
print("ALTERNATIVE: Match by folio (less precise)")
print("=" * 70)

# Get unique folios containing animal records
animal_folios = set(rec['folio'] for rec in animal_records)
print(f"Folios containing animal records: {animal_folios}")

try:
    animal_folio_survival = []
    other_folio_survival = []

    for record_data in survivors['records']:
        record_id = record_data['a_record']
        folio = record_id.split(':')[0]
        survival_count = record_data['surviving_class_count']

        if folio in animal_folios:
            animal_folio_survival.append(survival_count)
        else:
            other_folio_survival.append(survival_count)

    print(f"\nRecords in animal folios: {len(animal_folio_survival)}")
    print(f"Records in other folios: {len(other_folio_survival)}")

    if animal_folio_survival and other_folio_survival:
        print(f"\nMean B classes surviving (by folio):")
        print(f"  Animal folios: {np.mean(animal_folio_survival):.1f} +/- {np.std(animal_folio_survival):.1f}")
        print(f"  Other folios: {np.mean(other_folio_survival):.1f} +/- {np.std(other_folio_survival):.1f}")

        t_stat, p_val = stats.ttest_ind(animal_folio_survival, other_folio_survival)
        print(f"\nT-test: t={t_stat:.2f}, p={p_val:.4f}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
