#!/usr/bin/env python3
"""
Dilution Hypothesis Validation

Question: Are the 40 "animal" records from Bayesian posteriors a diluted version
of C505's 13 high-confidence animal records?

Method:
1. Identify C505's original 13 animal records (using specific animal RI MIDDLEs)
2. Identify the 40 records from Bayesian posteriors
3. Find overlap and difference
4. Compare PP enrichment in:
   - C505's 13 records (should show ~16x for 'te', 'ho', 'ke')
   - The additional records (should show ~1x baseline)
   - All 40 combined (should show diluted ~3x)
"""

import json
import random
from collections import Counter, defaultdict

# Load A record survivors
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

# Load class token map for B MIDDLEs
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
print("DILUTION HYPOTHESIS VALIDATION")
print("="*70)

# ============================================================
# STEP 1: Identify C505's original animal records
# ============================================================
print("\n" + "="*70)
print("STEP 1: C505 ANIMAL RECORDS (Original Methodology)")
print("="*70)

# These are the animal-associated RI MIDDLEs from C505/reverse trace
c505_animal_ri = {'eyd', 'tchyf', 'ofy', 'opcho', 'eoc', 'eso',
                  'olfcho', 'cthso', 'hdaoto', 'teold', 'eoschso'}

# Find records containing any of these
c505_animal_indices = []
for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    if middles & c505_animal_ri:
        c505_animal_indices.append(i)

print(f"C505 animal records: {len(c505_animal_indices)}")

# ============================================================
# STEP 2: Identify Bayesian posterior animal records
# ============================================================
print("\n" + "="*70)
print("STEP 2: BAYESIAN ANIMAL RECORDS (Test Methodology)")
print("="*70)

# Load material class priors
with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json') as f:
    priors_data = json.load(f)

# Map RI MIDDLEs to classes
ri_to_class = {}
for entry in priors_data['results']:
    middle = entry['middle']
    top_class = entry['top_class']
    top_prob = entry['top_class_probability']
    if middle in ri_middles and top_prob >= 0.5:
        ri_to_class[middle] = (top_class, top_prob)

# Find records with dominant class = animal
bayesian_animal_indices = []
for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    ri_in_record = middles & ri_middles

    class_scores = defaultdict(float)
    for m in ri_in_record:
        if m in ri_to_class:
            cls, prob = ri_to_class[m]
            class_scores[cls] += prob

    if class_scores:
        dominant = max(class_scores.items(), key=lambda x: x[1])
        if dominant[0] == 'animal':
            bayesian_animal_indices.append(i)

print(f"Bayesian animal records: {len(bayesian_animal_indices)}")

# ============================================================
# STEP 3: Find overlap and difference
# ============================================================
print("\n" + "="*70)
print("STEP 3: OVERLAP ANALYSIS")
print("="*70)

c505_set = set(c505_animal_indices)
bayesian_set = set(bayesian_animal_indices)

overlap = c505_set & bayesian_set
c505_only = c505_set - bayesian_set
bayesian_only = bayesian_set - c505_set

print(f"\nOverlap (in both): {len(overlap)}")
print(f"C505 only (high-confidence, not in Bayesian): {len(c505_only)}")
print(f"Bayesian only (additional records): {len(bayesian_only)}")

# ============================================================
# STEP 4: Compare PP enrichment across groups
# ============================================================
print("\n" + "="*70)
print("STEP 4: PP ENRICHMENT BY GROUP")
print("="*70)

# Build PP matrix
pp_matrix = []
for rec in records:
    middles = set(rec['a_middles'])
    pp_matrix.append(middles & pp_middles)

# Non-animal baseline (all records not in either animal set)
all_animal = c505_set | bayesian_set
non_animal_indices = [i for i in range(len(records)) if i not in all_animal]

def compute_pp_rate(indices, target_pp):
    if not indices:
        return 0
    count = sum(1 for i in indices if target_pp in pp_matrix[i])
    return count / len(indices)

# Test PP MIDDLEs from C505
test_pp = ['te', 'ho', 'ke', 'eod', 'eo', 'keo']

print(f"\nPP rates by group:")
print(f"{'PP':<8} {'C505 (n='+str(len(c505_animal_indices))+')':<15} {'Overlap (n='+str(len(overlap))+')':<15} {'Bayes-only (n='+str(len(bayesian_only))+')':<20} {'Non-animal':<12}")
print("-"*70)

for pp in test_pp:
    c505_rate = compute_pp_rate(list(c505_set), pp)
    overlap_rate = compute_pp_rate(list(overlap), pp)
    bayesian_only_rate = compute_pp_rate(list(bayesian_only), pp)
    non_animal_rate = compute_pp_rate(non_animal_indices, pp)

    print(f"'{pp}'    {c505_rate*100:>6.1f}%         {overlap_rate*100:>6.1f}%         {bayesian_only_rate*100:>6.1f}%              {non_animal_rate*100:>6.1f}%")

# ============================================================
# STEP 5: Compute enrichment ratios
# ============================================================
print("\n" + "="*70)
print("STEP 5: ENRICHMENT RATIOS vs NON-ANIMAL BASELINE")
print("="*70)

print(f"\n{'PP':<8} {'C505 enrich':<15} {'Bayes-only enrich':<20} {'All Bayes enrich':<18}")
print("-"*65)

for pp in test_pp:
    non_animal_rate = compute_pp_rate(non_animal_indices, pp)

    c505_rate = compute_pp_rate(list(c505_set), pp)
    bayesian_only_rate = compute_pp_rate(list(bayesian_only), pp)
    all_bayesian_rate = compute_pp_rate(bayesian_animal_indices, pp)

    if non_animal_rate > 0:
        c505_enrich = c505_rate / non_animal_rate
        bayesian_only_enrich = bayesian_only_rate / non_animal_rate
        all_bayesian_enrich = all_bayesian_rate / non_animal_rate
    else:
        c505_enrich = float('inf') if c505_rate > 0 else 1.0
        bayesian_only_enrich = float('inf') if bayesian_only_rate > 0 else 1.0
        all_bayesian_enrich = float('inf') if all_bayesian_rate > 0 else 1.0

    print(f"'{pp}'    {c505_enrich:>6.1f}x          {bayesian_only_enrich:>6.1f}x               {all_bayesian_enrich:>6.1f}x")

# ============================================================
# STEP 6: Verdict
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

# Check if Bayesian-only records have baseline-like rates
c505_te = compute_pp_rate(list(c505_set), 'te')
c505_ho = compute_pp_rate(list(c505_set), 'ho')
c505_ke = compute_pp_rate(list(c505_set), 'ke')

bayesian_only_te = compute_pp_rate(list(bayesian_only), 'te')
bayesian_only_ho = compute_pp_rate(list(bayesian_only), 'ho')
bayesian_only_ke = compute_pp_rate(list(bayesian_only), 'ke')

non_te = compute_pp_rate(non_animal_indices, 'te')
non_ho = compute_pp_rate(non_animal_indices, 'ho')
non_ke = compute_pp_rate(non_animal_indices, 'ke')

# Bayesian-only enrichment should be near 1x if dilution hypothesis is correct
bayesian_only_mean_enrich = 0
count = 0
for pp in ['te', 'ho', 'ke']:
    non_rate = compute_pp_rate(non_animal_indices, pp)
    bo_rate = compute_pp_rate(list(bayesian_only), pp)
    if non_rate > 0:
        bayesian_only_mean_enrich += bo_rate / non_rate
        count += 1

if count > 0:
    bayesian_only_mean_enrich /= count

if bayesian_only_mean_enrich < 2:
    print(f"""
DILUTION HYPOTHESIS CONFIRMED

The Bayesian-only records (n={len(bayesian_only)}) show mean enrichment of {bayesian_only_mean_enrich:.1f}x,
which is near baseline (1.0x).

C505's records (n={len(c505_animal_indices)}) contain the TRUE animal signal.
The additional Bayesian records are procedurally ambiguous and dilute the PP signature.

This confirms:
1. PP discrimination requires procedural grounding (reverse trace methodology)
2. Taxonomic classification (Bayesian posteriors) identifies a noisy superset
3. C505's methodology captures handling complexity, not taxonomic category
""")
else:
    print(f"""
DILUTION HYPOTHESIS NOT CONFIRMED

The Bayesian-only records (n={len(bayesian_only)}) show mean enrichment of {bayesian_only_mean_enrich:.1f}x,
which suggests they also contain some animal signal.

This may indicate:
1. The Bayesian method captures a broader but still valid signal
2. There are more animal records than C505 identified
3. Further investigation needed
""")

# List what the Bayesian-only records are
print("\n" + "="*70)
print("BAYESIAN-ONLY RECORDS (for inspection)")
print("="*70)
print(f"\n{len(bayesian_only)} records classified as 'animal' by Bayesian but NOT by C505 RI MIDDLEs:")
for i in list(bayesian_only)[:10]:
    rec = records[i]
    middles = set(rec['a_middles'])
    ri_in_rec = middles & ri_middles
    # Find which RI led to animal classification
    animal_ri = [m for m in ri_in_rec if m in ri_to_class and ri_to_class[m][0] == 'animal']
    print(f"  {rec['a_record']}: animal RI = {animal_ri[:3]}")
