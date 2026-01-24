#!/usr/bin/env python3
"""
Extend C505 Methodology to WATER_GENTLE

Question: Do WATER_GENTLE (REGIME_2) materials have a distinct PP signature,
identifiable through procedural trace methodology?

Method (C505-style):
1. Identify WATER_GENTLE product type folios (REGIME_2)
2. Find A records that converge to those folios (high survival)
3. Identify RI MIDDLEs exclusive to those records
4. Test for PP signature differentiation vs PRECISION (animals)
"""

import json
import random
from collections import Counter, defaultdict

# Load A record survivors
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

# Load class token map
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

class_to_middles = class_map['class_to_middles']

b_middles_from_classes = set()
for cls, middles in class_to_middles.items():
    b_middles_from_classes.update(middles)

all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

pp_middles = all_a_middles & b_middles_from_classes
ri_middles = all_a_middles - b_middles_from_classes

print("="*70)
print("WATER_GENTLE PP SIGNATURE TEST (C505 Methodology Extension)")
print("="*70)

# ============================================================
# STEP 1: Identify product type folios
# ============================================================
print("\n" + "="*70)
print("STEP 1: IDENTIFY PRODUCT TYPE FOLIOS")
print("="*70)

# Load category discrimination results for product type info
with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/category_discrimination.json') as f:
    cat_disc = json.load(f)

# WATER_GENTLE exclusive MIDDLEs (from category discrimination)
water_gentle_middles = set(cat_disc['exclusive_middles']['WATER_GENTLE'])
oil_resin_middles = set(cat_disc['exclusive_middles']['OIL_RESIN'])

print(f"WATER_GENTLE exclusive MIDDLEs: {water_gentle_middles}")
print(f"OIL_RESIN exclusive MIDDLEs: {oil_resin_middles}")

# These are product-type-specific, not material-class specific
# We need to find A records that show preference for these product types

# ============================================================
# STEP 2: Load REGIME/folio mappings
# ============================================================
print("\n" + "="*70)
print("STEP 2: REGIME FOLIO MAPPINGS")
print("="*70)

# Try to load REGIME folio data
import pandas as pd
import os

# Load transcript for folio info
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Get B folios
df_b = df[df['language'] == 'B']
b_folios = df_b['folio'].unique()
print(f"B folios: {len(b_folios)}")

# Load REGIME mapping if available
try:
    with open('results/regime_folio_mapping.json') as f:
        regime_map = json.load(f)
    print(f"REGIME mapping loaded")
    for regime, folios in regime_map.items():
        print(f"  {regime}: {len(folios)} folios")
except FileNotFoundError:
    regime_map = None
    print("No REGIME mapping found")

# ============================================================
# STEP 3: Alternative approach - use product type MIDDLEs
# ============================================================
print("\n" + "="*70)
print("STEP 3: FIND RECORDS BY PRODUCT TYPE MIDDLES")
print("="*70)

# Find A records containing WATER_GENTLE exclusive MIDDLEs
water_gentle_records = []
oil_resin_records = []

for i, rec in enumerate(records):
    middles = set(rec['a_middles'])

    # Check for WATER_GENTLE MIDDLEs
    wg_overlap = middles & water_gentle_middles
    if wg_overlap:
        water_gentle_records.append({
            'index': i,
            'record': rec['a_record'],
            'wg_middles': wg_overlap,
            'all_middles': middles
        })

    # Check for OIL_RESIN MIDDLEs
    or_overlap = middles & oil_resin_middles
    if or_overlap:
        oil_resin_records.append({
            'index': i,
            'record': rec['a_record'],
            'or_middles': or_overlap,
            'all_middles': middles
        })

print(f"\nRecords with WATER_GENTLE MIDDLEs: {len(water_gentle_records)}")
print(f"Records with OIL_RESIN MIDDLEs: {len(oil_resin_records)}")

# ============================================================
# STEP 4: Get C505 animal records for comparison
# ============================================================
print("\n" + "="*70)
print("STEP 4: C505 ANIMAL RECORDS FOR COMPARISON")
print("="*70)

c505_animal_ri = {'eyd', 'tchyf', 'ofy', 'opcho', 'eoc', 'eso',
                  'olfcho', 'cthso', 'hdaoto', 'teold', 'eoschso'}

animal_records = []
for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    if middles & c505_animal_ri:
        animal_records.append({
            'index': i,
            'record': rec['a_record'],
            'animal_middles': middles & c505_animal_ri,
            'all_middles': middles
        })

print(f"C505 animal records: {len(animal_records)}")

# ============================================================
# STEP 5: Build PP profiles by product type
# ============================================================
print("\n" + "="*70)
print("STEP 5: PP PROFILES BY PRODUCT TYPE")
print("="*70)

# PP matrix
pp_matrix = []
for rec in records:
    middles = set(rec['a_middles'])
    pp_matrix.append(middles & pp_middles)

# Compute PP profiles
def get_pp_profile(record_list):
    pp_counter = Counter()
    for r in record_list:
        i = r['index']
        for pp in pp_matrix[i]:
            pp_counter[pp] += 1
    return pp_counter

animal_pp = get_pp_profile(animal_records)
water_gentle_pp = get_pp_profile(water_gentle_records)
oil_resin_pp = get_pp_profile(oil_resin_records)

print(f"\nANIMAL (PRECISION) PP profile (n={len(animal_records)}):")
for pp, cnt in animal_pp.most_common(10):
    rate = cnt / len(animal_records) * 100
    print(f"  '{pp}': {rate:.1f}%")

if water_gentle_records:
    print(f"\nWATER_GENTLE PP profile (n={len(water_gentle_records)}):")
    for pp, cnt in water_gentle_pp.most_common(10):
        rate = cnt / len(water_gentle_records) * 100
        print(f"  '{pp}': {rate:.1f}%")

if oil_resin_records:
    print(f"\nOIL_RESIN PP profile (n={len(oil_resin_records)}):")
    for pp, cnt in oil_resin_pp.most_common(10):
        rate = cnt / len(oil_resin_records) * 100
        print(f"  '{pp}': {rate:.1f}%")

# ============================================================
# STEP 6: Compare PP signatures across product types
# ============================================================
print("\n" + "="*70)
print("STEP 6: PP SIGNATURE COMPARISON")
print("="*70)

def compute_pp_rate(record_list, target_pp):
    if not record_list:
        return 0
    indices = [r['index'] for r in record_list]
    count = sum(1 for i in indices if target_pp in pp_matrix[i])
    return count / len(record_list)

# Get baseline (all records not in any product type category)
all_typed_indices = set()
for r in animal_records:
    all_typed_indices.add(r['index'])
for r in water_gentle_records:
    all_typed_indices.add(r['index'])
for r in oil_resin_records:
    all_typed_indices.add(r['index'])

baseline_indices = [i for i in range(len(records)) if i not in all_typed_indices]

# Key PP from C505 (animal signature)
animal_sig_pp = ['te', 'ho', 'ke', 'eod', 's', 'od']

print(f"\nAnimal-signature PP rates:")
print(f"{'PP':<8} {'Animal':<12} {'Water_Gentle':<15} {'Oil_Resin':<12} {'Baseline':<12}")
print("-"*60)

for pp in animal_sig_pp:
    animal_rate = compute_pp_rate(animal_records, pp)
    wg_rate = compute_pp_rate(water_gentle_records, pp)
    or_rate = compute_pp_rate(oil_resin_records, pp)
    baseline_rate = sum(1 for i in baseline_indices if pp in pp_matrix[i]) / len(baseline_indices) if baseline_indices else 0

    print(f"'{pp}'    {animal_rate*100:>6.1f}%      {wg_rate*100:>6.1f}%          {or_rate*100:>6.1f}%       {baseline_rate*100:>6.1f}%")

# ============================================================
# STEP 7: Find product-type-specific PP signatures
# ============================================================
print("\n" + "="*70)
print("STEP 7: PRODUCT-TYPE-SPECIFIC PP SIGNATURES")
print("="*70)

def find_signature_pp(target_records, comparison_records, threshold=2.0):
    """Find PP MIDDLEs enriched in target vs comparison."""
    signatures = []
    for pp in pp_middles:
        target_rate = compute_pp_rate(target_records, pp)
        comparison_rate = compute_pp_rate(comparison_records, pp)

        if target_rate > 0.1:  # At least 10% in target
            if comparison_rate > 0:
                enrich = target_rate / comparison_rate
            else:
                enrich = float('inf')

            if enrich >= threshold:
                signatures.append((pp, target_rate, comparison_rate, enrich))

    return sorted(signatures, key=lambda x: -x[3])

# Animal vs baseline
print("\nANIMAL signature PP (vs baseline, >2x enrichment):")
animal_sigs = find_signature_pp(animal_records, [{'index': i} for i in baseline_indices])
for pp, tr, cr, enrich in animal_sigs[:8]:
    print(f"  '{pp}': {tr*100:.1f}% vs {cr*100:.1f}% ({enrich:.1f}x)")

# Water_Gentle vs baseline
if water_gentle_records:
    print("\nWATER_GENTLE signature PP (vs baseline, >2x enrichment):")
    wg_sigs = find_signature_pp(water_gentle_records, [{'index': i} for i in baseline_indices])
    for pp, tr, cr, enrich in wg_sigs[:8]:
        print(f"  '{pp}': {tr*100:.1f}% vs {cr*100:.1f}% ({enrich:.1f}x)")

# Oil_Resin vs baseline
if oil_resin_records:
    print("\nOIL_RESIN signature PP (vs baseline, >2x enrichment):")
    or_sigs = find_signature_pp(oil_resin_records, [{'index': i} for i in baseline_indices])
    for pp, tr, cr, enrich in or_sigs[:8]:
        print(f"  '{pp}': {tr*100:.1f}% vs {cr*100:.1f}% ({enrich:.1f}x)")

# ============================================================
# STEP 8: Permutation test for product type discrimination
# ============================================================
print("\n" + "="*70)
print("STEP 8: PERMUTATION TEST - ANIMAL vs WATER_GENTLE")
print("="*70)

if water_gentle_records and len(water_gentle_records) >= 5:
    animal_idx = [r['index'] for r in animal_records]
    wg_idx = [r['index'] for r in water_gentle_records]

    print(f"\nAnimal: {len(animal_idx)} records")
    print(f"Water_Gentle: {len(wg_idx)} records")

    # Test animal-signature PP
    test_pp = ['te', 'ho', 'ke', 's', 'od']

    n_permutations = 1000
    random.seed(42)

    combined = animal_idx + wg_idx
    n_animal = len(animal_idx)

    print(f"\nPermutation test (n={n_permutations}):")
    results = []

    for pp in test_pp:
        # Observed
        animal_count = sum(1 for i in animal_idx if pp in pp_matrix[i])
        wg_count = sum(1 for i in wg_idx if pp in pp_matrix[i])

        animal_rate = animal_count / len(animal_idx)
        wg_rate = wg_count / len(wg_idx) if wg_idx else 0

        if wg_rate > 0:
            obs_enrich = animal_rate / wg_rate
        else:
            obs_enrich = float('inf') if animal_rate > 0 else 1.0

        # Permutation
        perm_enrichments = []
        for _ in range(n_permutations):
            shuffled = combined.copy()
            random.shuffle(shuffled)
            perm_animal = shuffled[:n_animal]
            perm_wg = shuffled[n_animal:]

            pa_rate = sum(1 for i in perm_animal if pp in pp_matrix[i]) / len(perm_animal)
            pw_rate = sum(1 for i in perm_wg if pp in pp_matrix[i]) / len(perm_wg) if perm_wg else 0

            if pw_rate > 0:
                perm_enrichments.append(pa_rate / pw_rate)
            elif pa_rate > 0:
                perm_enrichments.append(float('inf'))
            else:
                perm_enrichments.append(1.0)

        # p-value
        if obs_enrich == float('inf'):
            n_exceed = sum(1 for v in perm_enrichments if v == float('inf'))
        else:
            n_exceed = sum(1 for v in perm_enrichments if v >= obs_enrich)

        p_value = n_exceed / n_permutations
        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

        results.append({
            'pp': pp,
            'animal_rate': animal_rate,
            'wg_rate': wg_rate,
            'enrichment': obs_enrich,
            'p_value': p_value
        })

        print(f"  '{pp}': animal={animal_rate*100:.1f}%, WG={wg_rate*100:.1f}%, "
              f"enrich={obs_enrich:.2f}x, p={p_value:.4f} {sig}")

    sig_count = sum(1 for r in results if r['p_value'] < 0.05)
    print(f"\n  Significant (p<0.05): {sig_count}/{len(results)}")
else:
    print("\nInsufficient WATER_GENTLE records for permutation test")

# ============================================================
# STEP 9: Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Product Type PP Signature Analysis:

SAMPLE SIZES:
  Animal (PRECISION): {len(animal_records)} records
  Water_Gentle: {len(water_gentle_records)} records
  Oil_Resin: {len(oil_resin_records)} records
  Baseline: {len(baseline_indices)} records

METHODOLOGY:
  Used C505-style procedural trace - identify records by product-type-exclusive MIDDLEs,
  then compare PP profiles.

KEY FINDINGS:
""")

if water_gentle_records and len(water_gentle_records) >= 5:
    # Check if profiles differ
    animal_top = set([pp for pp, cnt in animal_pp.most_common(5)])
    wg_top = set([pp for pp, cnt in water_gentle_pp.most_common(5)])

    if animal_top != wg_top:
        print(f"  - Animal and Water_Gentle have DIFFERENT top PP profiles")
        print(f"    Animal top: {animal_top}")
        print(f"    Water_Gentle top: {wg_top}")
    else:
        print(f"  - Animal and Water_Gentle have SIMILAR top PP profiles")
else:
    print(f"  - Insufficient WATER_GENTLE records ({len(water_gentle_records)}) for comparison")

if oil_resin_records and len(oil_resin_records) >= 5:
    or_top = set([pp for pp, cnt in oil_resin_pp.most_common(5)])
    if animal_top != or_top:
        print(f"  - Animal and Oil_Resin have DIFFERENT top PP profiles")
        print(f"    Animal top: {animal_top}")
        print(f"    Oil_Resin top: {or_top}")
