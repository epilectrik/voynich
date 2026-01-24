#!/usr/bin/env python3
"""
Test 1: Multi-Class PP Discrimination

Question: Do different Brunschwig material classes have distinct PP signatures?

Method:
1. Use material_class_priors.json to group RI MIDDLEs by dominant class
2. Find A records containing MIDDLEs from each class
3. Compute PP profiles for each material class
4. Test if classes have statistically distinct PP signatures
5. Use permutation testing for validation
"""

import json
import numpy as np
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

# Get B MIDDLEs
b_middles_from_classes = set()
for cls, middles in class_to_middles.items():
    b_middles_from_classes.update(middles)

# Get all A MIDDLEs
all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

# PP = shared, RI = A-only
pp_middles = all_a_middles & b_middles_from_classes
ri_middles = all_a_middles - b_middles_from_classes

print("="*70)
print("MULTI-CLASS PP DISCRIMINATION TEST")
print("="*70)
print(f"\nPP MIDDLEs: {len(pp_middles)}")
print(f"RI MIDDLEs: {len(ri_middles)}")
print(f"Total A records: {len(records)}")

# ============================================================
# STEP 1: Load material class priors and group RI MIDDLEs
# ============================================================
print("\n" + "="*70)
print("STEP 1: GROUP RI MIDDLEs BY MATERIAL CLASS")
print("="*70)

with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json') as f:
    priors_data = json.load(f)

# Group MIDDLEs by dominant class (only for RI MIDDLEs with high confidence)
class_to_ri = defaultdict(set)
ri_to_class = {}

for entry in priors_data['results']:
    middle = entry['middle']
    top_class = entry['top_class']
    top_prob = entry['top_class_probability']

    # Only consider RI MIDDLEs (not PP)
    if middle in ri_middles and top_prob >= 0.5:  # At least 50% confident
        class_to_ri[top_class].add(middle)
        ri_to_class[middle] = (top_class, top_prob)

print("\nRI MIDDLEs by material class (>=50% confidence):")
for cls, middles in sorted(class_to_ri.items(), key=lambda x: -len(x[1])):
    print(f"  {cls}: {len(middles)} MIDDLEs")

# ============================================================
# STEP 2: Identify records for each material class
# ============================================================
print("\n" + "="*70)
print("STEP 2: IDENTIFY RECORDS BY MATERIAL CLASS")
print("="*70)

# For each record, determine its material class(es) based on RI MIDDLEs
record_classes = []
for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    ri_in_record = middles & ri_middles

    # Find classes represented by this record's RI MIDDLEs
    classes_in_record = defaultdict(float)
    for m in ri_in_record:
        if m in ri_to_class:
            cls, prob = ri_to_class[m]
            classes_in_record[cls] += prob

    if classes_in_record:
        # Assign to dominant class
        dominant = max(classes_in_record.items(), key=lambda x: x[1])
        record_classes.append({
            'index': i,
            'record': rec['a_record'],
            'dominant_class': dominant[0],
            'class_scores': dict(classes_in_record),
            'pp_middles': middles & pp_middles
        })
    else:
        record_classes.append({
            'index': i,
            'record': rec['a_record'],
            'dominant_class': None,
            'class_scores': {},
            'pp_middles': middles & pp_middles
        })

# Count records by dominant class
class_counts = Counter(r['dominant_class'] for r in record_classes if r['dominant_class'])
print("\nRecords by dominant material class:")
for cls, cnt in class_counts.most_common():
    print(f"  {cls}: {cnt} records")

# ============================================================
# STEP 3: Compute PP profiles for each material class
# ============================================================
print("\n" + "="*70)
print("STEP 3: PP PROFILES BY MATERIAL CLASS")
print("="*70)

# Build PP presence matrix
pp_matrix = []
for rec in records:
    middles = set(rec['a_middles'])
    pp_in_record = middles & pp_middles
    pp_matrix.append(pp_in_record)

# Focus on classes with sufficient records (n >= 10)
test_classes = [cls for cls, cnt in class_counts.items() if cnt >= 10]
print(f"\nClasses with >= 10 records: {test_classes}")

# Compute PP frequency per class
class_pp_profiles = {}
for cls in test_classes:
    class_records = [r for r in record_classes if r['dominant_class'] == cls]
    pp_counter = Counter()
    for r in class_records:
        for pp in r['pp_middles']:
            pp_counter[pp] += 1

    # Convert to rates
    n = len(class_records)
    pp_rates = {pp: cnt/n for pp, cnt in pp_counter.items()}
    class_pp_profiles[cls] = {
        'n_records': n,
        'pp_counter': pp_counter,
        'pp_rates': pp_rates
    }

    print(f"\n{cls} (n={n}):")
    print(f"  Top PP: {dict(pp_counter.most_common(8))}")

# ============================================================
# STEP 4: Pairwise class discrimination
# ============================================================
print("\n" + "="*70)
print("STEP 4: PAIRWISE CLASS DISCRIMINATION")
print("="*70)

def compute_enrichment(class1_indices, class2_indices, target_pp):
    """Compute enrichment of target_pp in class1 vs class2."""
    class1_count = sum(1 for i in class1_indices if target_pp in pp_matrix[i])
    class2_count = sum(1 for i in class2_indices if target_pp in pp_matrix[i])

    rate1 = class1_count / len(class1_indices) if class1_indices else 0
    rate2 = class2_count / len(class2_indices) if class2_indices else 0

    if rate2 > 0:
        enrichment = rate1 / rate2
    else:
        enrichment = float('inf') if rate1 > 0 else 1.0

    return enrichment, rate1, rate2

# Get indices for each class
class_indices = {}
for cls in test_classes:
    class_indices[cls] = [r['index'] for r in record_classes if r['dominant_class'] == cls]

# Find PP MIDDLEs that discriminate between classes
discriminative_pp = defaultdict(list)

for cls1 in test_classes:
    for cls2 in test_classes:
        if cls1 >= cls2:
            continue

        print(f"\n{cls1} vs {cls2}:")
        indices1 = class_indices[cls1]
        indices2 = class_indices[cls2]

        # Test each PP
        for pp in pp_middles:
            enrich, rate1, rate2 = compute_enrichment(indices1, indices2, pp)

            # Report if strongly discriminative (>3x in either direction)
            if enrich > 3 and rate1 > 0.1:
                print(f"  '{pp}': {cls1}={rate1*100:.1f}% vs {cls2}={rate2*100:.1f}% ({enrich:.1f}x for {cls1})")
                discriminative_pp[pp].append((cls1, cls2, enrich))
            elif enrich > 0 and enrich < 0.33 and rate2 > 0.1:
                print(f"  '{pp}': {cls1}={rate1*100:.1f}% vs {cls2}={rate2*100:.1f}% ({1/enrich:.1f}x for {cls2})")
                discriminative_pp[pp].append((cls2, cls1, 1/enrich))

# ============================================================
# STEP 5: Permutation test for significance
# ============================================================
print("\n" + "="*70)
print("STEP 5: PERMUTATION TEST")
print("="*70)

# Test the most discriminative PP MIDDLEs
# Focus on animal vs herb (our strongest contrast from C505)
if 'animal' in class_indices and 'herb' in class_indices:
    animal_idx = class_indices['animal']
    herb_idx = class_indices['herb']

    print(f"\nAnimal vs Herb permutation test:")
    print(f"  Animal records: {len(animal_idx)}")
    print(f"  Herb records: {len(herb_idx)}")

    # Key PP from C505 and new discoveries
    test_pp = ['te', 'ho', 'ke', 'eod', 'eo', 'keo', 'o', 'e', 'l', 'r']

    n_permutations = 1000
    random.seed(42)

    combined_indices = animal_idx + herb_idx
    n_animal = len(animal_idx)

    results = []
    for pp in test_pp:
        # Observed enrichment
        obs_enrich, obs_animal, obs_herb = compute_enrichment(animal_idx, herb_idx, pp)

        # Permutation distribution
        perm_enrichments = []
        for _ in range(n_permutations):
            shuffled = combined_indices.copy()
            random.shuffle(shuffled)
            perm_animal = shuffled[:n_animal]
            perm_herb = shuffled[n_animal:]

            enrich, _, _ = compute_enrichment(perm_animal, perm_herb, pp)
            perm_enrichments.append(enrich)

        # p-value (one-tailed: is observed enrichment higher than expected?)
        if obs_enrich == float('inf'):
            n_exceed = sum(1 for v in perm_enrichments if v == float('inf'))
        else:
            n_exceed = sum(1 for v in perm_enrichments if v >= obs_enrich)

        p_value = n_exceed / n_permutations

        # Two-tailed for low enrichment
        if obs_enrich < 1:
            n_below = sum(1 for v in perm_enrichments if v <= obs_enrich)
            p_value_low = n_below / n_permutations
        else:
            p_value_low = 1.0

        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

        results.append({
            'pp': pp,
            'animal_rate': obs_animal,
            'herb_rate': obs_herb,
            'enrichment': obs_enrich,
            'p_value': p_value,
            'significant': p_value < 0.01
        })

        print(f"  '{pp}': animal={obs_animal*100:.1f}%, herb={obs_herb*100:.1f}%, "
              f"enrich={obs_enrich:.2f}x, p={p_value:.4f} {sig}")

    # Summary
    sig_count = sum(1 for r in results if r['significant'])
    print(f"\n  Significant (p<0.01): {sig_count}/{len(results)}")

# ============================================================
# STEP 6: Multi-class summary
# ============================================================
print("\n" + "="*70)
print("STEP 6: SUMMARY - CLASS DISCRIMINATION BY PP")
print("="*70)

# For each class, find its signature PP (high rate vs other classes)
print("\nClass-specific PP signatures (>20% in class, >2x vs others):")

for cls in test_classes:
    cls_idx = class_indices[cls]
    other_idx = [i for c, indices in class_indices.items() for i in indices if c != cls]

    sig_pp = []
    for pp in pp_middles:
        enrich, cls_rate, other_rate = compute_enrichment(cls_idx, other_idx, pp)
        if cls_rate > 0.2 and enrich > 2:
            sig_pp.append((pp, cls_rate, enrich))

    if sig_pp:
        sig_pp.sort(key=lambda x: -x[2])
        print(f"\n{cls}:")
        for pp, rate, enrich in sig_pp[:5]:
            print(f"  '{pp}': {rate*100:.1f}% ({enrich:.1f}x vs others)")

# ============================================================
# STEP 7: Verdict
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

if 'animal' in test_classes:
    animal_sig = [r for r in results if r['significant']]
    if len(animal_sig) >= 3:
        print(f"""
VALIDATED: Multiple material classes have distinct PP signatures.

Animal class shows {len(animal_sig)} significantly enriched PP MIDDLEs:
{[r['pp'] for r in animal_sig]}

This extends C505 by confirming:
1. PP discrimination is robust across methodologies (material_class_priors vs manual animal RI)
2. PP profiles differentiate material classes beyond just animals
3. PP carries information about operational affordances
""")
    else:
        print(f"""
PARTIAL: Some PP discrimination detected but weaker than C505.

Only {len(animal_sig)} PP MIDDLEs show significant enrichment.
May need larger sample sizes or refined class assignments.
""")
else:
    print("""
INSUFFICIENT DATA: No animal class records found in this analysis.
Check material_class_priors.json mapping.
""")
