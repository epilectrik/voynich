#!/usr/bin/env python3
"""
AZC Filtering Mechanisms Follow-up Test

Questions:
1. Do PP MIDDLEs concentrate in specific AZC zones (C, P, R, S)?
2. Does PP interact with escape gradients?
3. Does MIDDLE incompatibility (C475) operate differently on PP vs RI?

This tests whether AZC filtering is ORTHOGONAL to PP (position-based)
or whether PP INTERACTS with AZC's mechanisms.
"""

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from math import log2
from scipy import stats

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class token map
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']
class_to_middles = class_map['class_to_middles']

# Get B MIDDLEs (for PP classification)
b_middles_from_classes = set()
for cls, middles in class_to_middles.items():
    b_middles_from_classes.update(middles)

# Load A record survivors for A MIDDLE inventory
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

all_a_middles = set()
for rec in survivors_data['records']:
    all_a_middles.update(rec['a_middles'])

# PP = shared, RI = A-only
pp_middles = all_a_middles & b_middles_from_classes
ri_middles = all_a_middles - b_middles_from_classes

print("="*70)
print("AZC FILTERING MECHANISMS TEST")
print("="*70)
print(f"\nPP MIDDLEs: {len(pp_middles)}")
print(f"RI MIDDLEs: {len(ri_middles)}")

# ============================================================
# STEP 1: Extract AZC tokens with position info
# ============================================================
print("\n" + "="*70)
print("STEP 1: EXTRACT AZC TOKENS WITH POSITION INFO")
print("="*70)

# AZC tokens have language=NA and placement codes
df_azc = df[df['language'].isna()].copy()
df_azc['middle'] = df_azc['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

# Extract position zone from placement (first letter: C, P, R, S, L)
def get_zone(placement):
    if pd.isna(placement):
        return 'UNKNOWN'
    p = str(placement)
    if p.startswith('C'):
        return 'C'  # Center
    elif p.startswith('P'):
        return 'P'  # Paragraph/text
    elif p.startswith('R'):
        return 'R'  # Ring
    elif p.startswith('S'):
        return 'S'  # Star/sector
    elif p.startswith('L'):
        return 'L'  # Label
    else:
        return 'OTHER'

df_azc['zone'] = df_azc['placement'].apply(get_zone)

print(f"\nAZC tokens: {len(df_azc)}")
print(f"With MIDDLE: {df_azc['middle'].notna().sum()}")
print(f"\nZone distribution:")
print(df_azc['zone'].value_counts())

# ============================================================
# STEP 2: PP vs RI distribution across AZC zones
# ============================================================
print("\n" + "="*70)
print("STEP 2: PP vs RI DISTRIBUTION ACROSS AZC ZONES")
print("="*70)

# Classify each AZC token's MIDDLE as PP, RI, or neither
def classify_middle(m):
    if pd.isna(m):
        return 'NONE'
    if m in pp_middles:
        return 'PP'
    elif m in ri_middles:
        return 'RI'
    else:
        return 'OTHER'  # In AZC but not in A records

df_azc['middle_type'] = df_azc['middle'].apply(classify_middle)

# Crosstab: zone x middle_type
zone_type_ct = pd.crosstab(df_azc['zone'], df_azc['middle_type'])
print("\nZone x MIDDLE Type crosstab:")
print(zone_type_ct)

# Calculate PP ratio by zone
zone_pp_ratio = {}
for zone in ['C', 'P', 'R', 'S', 'L']:
    if zone in zone_type_ct.index:
        pp_count = zone_type_ct.loc[zone, 'PP'] if 'PP' in zone_type_ct.columns else 0
        ri_count = zone_type_ct.loc[zone, 'RI'] if 'RI' in zone_type_ct.columns else 0
        total = pp_count + ri_count
        if total > 0:
            zone_pp_ratio[zone] = pp_count / total
            print(f"\n{zone} zone: PP={pp_count}, RI={ri_count}, PP ratio={pp_count/total:.3f}")

# Chi-square test: is PP/RI distribution independent of zone?
if 'PP' in zone_type_ct.columns and 'RI' in zone_type_ct.columns:
    contingency = zone_type_ct[['PP', 'RI']].dropna()
    if len(contingency) > 1:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\nChi-square test (PP/RI independence of zone):")
        print(f"  chi2 = {chi2:.2f}, p = {p_value:.2e}, dof = {dof}")
        if p_value < 0.05:
            print("  -> PP/RI distribution DEPENDS on zone (significant)")
        else:
            print("  -> PP/RI distribution is INDEPENDENT of zone")

# ============================================================
# STEP 3: PP vs RI and Escape Rate
# ============================================================
print("\n" + "="*70)
print("STEP 3: PP vs RI AND ESCAPE RATE")
print("="*70)

# Load escape rate data
with open('results/azc_escape_by_position.json') as f:
    escape_data = json.load(f)

# Define escape prefixes (qo is the main escape prefix)
escape_prefixes = ['qo']

def has_escape_prefix(word):
    if pd.isna(word):
        return False
    w = str(word)
    return any(w.startswith(p) for p in escape_prefixes)

df_azc['is_escape'] = df_azc['word'].apply(has_escape_prefix)

# Escape rate by MIDDLE type
for mtype in ['PP', 'RI', 'OTHER']:
    mask = df_azc['middle_type'] == mtype
    n_total = mask.sum()
    n_escape = (df_azc[mask]['is_escape']).sum()
    if n_total > 0:
        rate = 100 * n_escape / n_total
        print(f"{mtype}: {n_escape}/{n_total} escape tokens ({rate:.2f}%)")

# Chi-square: is escape rate independent of PP/RI?
escape_type_ct = pd.crosstab(df_azc['middle_type'], df_azc['is_escape'])
print("\nMIDDLE Type x Escape crosstab:")
print(escape_type_ct)

if True in escape_type_ct.columns and False in escape_type_ct.columns:
    # Filter to PP and RI only
    if 'PP' in escape_type_ct.index and 'RI' in escape_type_ct.index:
        contingency = escape_type_ct.loc[['PP', 'RI']]
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\nChi-square test (escape independence of PP/RI):")
        print(f"  chi2 = {chi2:.2f}, p = {p_value:.2e}, dof = {dof}")
        if p_value < 0.05:
            print("  -> Escape rate DEPENDS on PP/RI (significant)")
        else:
            print("  -> Escape rate is INDEPENDENT of PP/RI")

# ============================================================
# STEP 4: Escape gradient interaction
# ============================================================
print("\n" + "="*70)
print("STEP 4: ESCAPE GRADIENT BY ZONE AND MIDDLE TYPE")
print("="*70)

# For each zone, check escape rate by PP vs RI
for zone in ['C', 'P', 'R', 'S', 'L']:
    zone_mask = df_azc['zone'] == zone
    zone_df = df_azc[zone_mask]

    if len(zone_df) > 10:
        pp_mask = zone_df['middle_type'] == 'PP'
        ri_mask = zone_df['middle_type'] == 'RI'

        pp_escape = zone_df[pp_mask]['is_escape'].sum()
        pp_total = pp_mask.sum()
        ri_escape = zone_df[ri_mask]['is_escape'].sum()
        ri_total = ri_mask.sum()

        pp_rate = 100 * pp_escape / pp_total if pp_total > 0 else 0
        ri_rate = 100 * ri_escape / ri_total if ri_total > 0 else 0

        print(f"\n{zone} zone:")
        print(f"  PP: {pp_escape}/{pp_total} escape ({pp_rate:.1f}%)")
        print(f"  RI: {ri_escape}/{ri_total} escape ({ri_rate:.1f}%)")

# ============================================================
# STEP 5: MIDDLE co-occurrence patterns (incompatibility proxy)
# ============================================================
print("\n" + "="*70)
print("STEP 5: MIDDLE CO-OCCURRENCE (INCOMPATIBILITY ANALYSIS)")
print("="*70)

# Within each AZC folio, which MIDDLEs co-occur?
azc_folio_middles = defaultdict(set)
for _, row in df_azc.iterrows():
    if pd.notna(row['middle']):
        azc_folio_middles[row['folio']].add(row['middle'])

# Count co-occurrences by type
pp_pp_cooccur = 0
pp_ri_cooccur = 0
ri_ri_cooccur = 0

for folio, middles in azc_folio_middles.items():
    pp_in_folio = middles & pp_middles
    ri_in_folio = middles & ri_middles

    # Count pairs
    pp_pp_cooccur += len(pp_in_folio) * (len(pp_in_folio) - 1) // 2
    pp_ri_cooccur += len(pp_in_folio) * len(ri_in_folio)
    ri_ri_cooccur += len(ri_in_folio) * (len(ri_in_folio) - 1) // 2

total_cooccur = pp_pp_cooccur + pp_ri_cooccur + ri_ri_cooccur
print(f"\nMIDDLE co-occurrence counts (within AZC folios):")
print(f"  PP-PP pairs: {pp_pp_cooccur} ({100*pp_pp_cooccur/total_cooccur:.1f}%)")
print(f"  PP-RI pairs: {pp_ri_cooccur} ({100*pp_ri_cooccur/total_cooccur:.1f}%)")
print(f"  RI-RI pairs: {ri_ri_cooccur} ({100*ri_ri_cooccur/total_cooccur:.1f}%)")

# Expected under independence
n_pp = len(pp_middles)
n_ri = len(ri_middles)
total_types = n_pp + n_ri

exp_pp_pp = (n_pp / total_types) ** 2
exp_pp_ri = 2 * (n_pp / total_types) * (n_ri / total_types)
exp_ri_ri = (n_ri / total_types) ** 2

print(f"\nExpected under independence:")
print(f"  PP-PP: {100*exp_pp_pp:.1f}%")
print(f"  PP-RI: {100*exp_pp_ri:.1f}%")
print(f"  RI-RI: {100*exp_ri_ri:.1f}%")

obs_pp_pp = pp_pp_cooccur / total_cooccur
obs_pp_ri = pp_ri_cooccur / total_cooccur
obs_ri_ri = ri_ri_cooccur / total_cooccur

print(f"\nEnrichment ratio (observed/expected):")
print(f"  PP-PP: {obs_pp_pp/exp_pp_pp:.2f}x")
print(f"  PP-RI: {obs_pp_ri/exp_pp_ri:.2f}x")
print(f"  RI-RI: {obs_ri_ri/exp_ri_ri:.2f}x")

# ============================================================
# STEP 6: KEY RESULT - AZC Filtering Mechanism
# ============================================================
print("\n" + "="*70)
print("STEP 6: KEY RESULTS - AZC FILTERING MECHANISMS")
print("="*70)

print("""
QUESTION: Does AZC filter primarily on POSITION or on PP/RI vocabulary?

FINDINGS:
""")

# Summarize zone dependency
if 'chi2' in dir() and p_value < 0.05:
    zone_finding = "PP/RI distribution VARIES by zone -> vocabulary IS position-dependent"
else:
    zone_finding = "PP/RI distribution is UNIFORM across zones -> vocabulary is position-independent"

print(f"1. Zone dependency: {zone_finding}")

# Summarize escape interaction
print("\n2. Escape gradient:")
print("   Position escape rates (from constraint data):")
print("   - P zone: 15.87% (highest)")
print("   - R zone: 9.23%")
print("   - L zone: 3.74%")
print("   - S zone: ~1-2% (lowest)")

# Summary
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("""
If PP/RI is INDEPENDENT of zone:
  -> AZC filters on POSITION (escape gradients, zone legality)
  -> PP filters on B EXECUTION (class survival)
  -> Two ORTHOGONAL filtering mechanisms

If PP/RI VARIES by zone:
  -> AZC and PP filtering are COUPLED
  -> Certain PP MIDDLEs prefer certain positions
  -> This would complicate the clean separation

The B-DOMINANT result from the entropy test combined with these findings
tells us WHERE each filtering mechanism operates:

  A Record -> [RI: identity selection] -> AZC -> [Position filtering] -> B -> [PP: class survival]
              (stays in A)                (zone/escape gradients)       (which operations viable)
""")
