#!/usr/bin/env python3
"""
Permutation Test: Validate Animal PP Signature Enrichment

Question: Is the 15x enrichment of 'te' in animal records statistically significant?

Method:
1. Take the 13 animal records and 1,566 non-animal records
2. Shuffle the "animal" label randomly 1000x
3. For each shuffle, compute enrichment ratios for key PP MIDDLEs
4. Check how often we get observed enrichment or higher by chance
5. p-value = fraction of permutations >= observed
"""

import json
import numpy as np
from collections import Counter
import random

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

# PP = shared
pp_middles = all_a_middles & b_middles_from_classes

# Animal-associated MIDDLEs (from reverse trace results)
animal_ri_middles = {'eyd', 'tchyf', 'ofy', 'opcho', 'eoc', 'eso',
                     'olfcho', 'cthso', 'hdaoto', 'teold', 'eoschso'}

# Identify animal vs non-animal records
animal_indices = []
non_animal_indices = []

for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    if middles & animal_ri_middles:
        animal_indices.append(i)
    else:
        non_animal_indices.append(i)

n_animal = len(animal_indices)
n_non_animal = len(non_animal_indices)
n_total = len(records)

print("="*70)
print("PERMUTATION TEST: ANIMAL PP SIGNATURE VALIDATION")
print("="*70)
print(f"\nAnimal records: {n_animal}")
print(f"Non-animal records: {n_non_animal}")
print(f"Total records: {n_total}")

# Build PP presence matrix for all records
# pp_matrix[i] = set of PP MIDDLEs in record i
pp_matrix = []
for rec in records:
    middles = set(rec['a_middles'])
    pp_in_record = middles & pp_middles
    pp_matrix.append(pp_in_record)

# Function to compute enrichment for a given set of "animal" indices
def compute_enrichment(animal_idx, non_animal_idx, target_pp):
    """Compute enrichment ratio for target_pp in animal vs non-animal."""
    animal_count = sum(1 for i in animal_idx if target_pp in pp_matrix[i])
    non_animal_count = sum(1 for i in non_animal_idx if target_pp in pp_matrix[i])

    animal_rate = animal_count / len(animal_idx) if animal_idx else 0
    non_animal_rate = non_animal_count / len(non_animal_idx) if non_animal_idx else 0

    if non_animal_rate > 0:
        enrichment = animal_rate / non_animal_rate
    else:
        enrichment = float('inf') if animal_rate > 0 else 1.0

    return enrichment, animal_rate, non_animal_rate

# Key PP MIDDLEs to test (those with high observed enrichment)
test_pp = ['te', 'ho', 'ke', 'eod', 'eo', 'keo']

# Compute observed enrichments
print("\n" + "="*70)
print("OBSERVED ENRICHMENT RATIOS")
print("="*70)

observed_enrichments = {}
for pp in test_pp:
    enrich, animal_rate, non_animal_rate = compute_enrichment(
        animal_indices, non_animal_indices, pp
    )
    observed_enrichments[pp] = enrich
    print(f"\n'{pp}':")
    print(f"  Animal rate: {100*animal_rate:.1f}%")
    print(f"  Non-animal rate: {100*non_animal_rate:.1f}%")
    print(f"  Enrichment: {enrich:.2f}x")

# ============================================================
# PERMUTATION TEST
# ============================================================
print("\n" + "="*70)
print("PERMUTATION TEST (1000 iterations)")
print("="*70)

n_permutations = 1000
random.seed(42)  # For reproducibility

# Store permutation enrichments
perm_enrichments = {pp: [] for pp in test_pp}

all_indices = list(range(n_total))

for perm in range(n_permutations):
    # Shuffle and pick n_animal random "animal" records
    shuffled = all_indices.copy()
    random.shuffle(shuffled)
    perm_animal = shuffled[:n_animal]
    perm_non_animal = shuffled[n_animal:]

    # Compute enrichment for each PP
    for pp in test_pp:
        enrich, _, _ = compute_enrichment(perm_animal, perm_non_animal, pp)
        perm_enrichments[pp].append(enrich)

# Compute p-values
print("\nP-values (fraction of permutations >= observed):")
print("-"*50)

results = []
for pp in test_pp:
    observed = observed_enrichments[pp]
    perm_values = perm_enrichments[pp]

    # Handle inf values
    if observed == float('inf'):
        n_exceed = sum(1 for v in perm_values if v == float('inf'))
    else:
        n_exceed = sum(1 for v in perm_values if v >= observed)

    p_value = n_exceed / n_permutations

    # Also compute permutation mean and std
    finite_perms = [v for v in perm_values if v != float('inf')]
    if finite_perms:
        perm_mean = np.mean(finite_perms)
        perm_std = np.std(finite_perms)
    else:
        perm_mean = float('inf')
        perm_std = 0

    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

    results.append({
        'pp': pp,
        'observed': observed,
        'perm_mean': perm_mean,
        'perm_std': perm_std,
        'p_value': p_value,
        'significant': p_value < 0.01
    })

    print(f"\n'{pp}':")
    print(f"  Observed: {observed:.2f}x")
    print(f"  Permutation mean: {perm_mean:.2f}x (±{perm_std:.2f})")
    print(f"  p-value: {p_value:.4f} {significance}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

significant_pp = [r for r in results if r['significant']]
print(f"\nSignificant PP MIDDLEs (p < 0.01): {len(significant_pp)}/{len(test_pp)}")

for r in results:
    status = "SIGNIFICANT" if r['significant'] else "not significant"
    print(f"  '{r['pp']}': {r['observed']:.1f}x enrichment, p={r['p_value']:.4f} -> {status}")

# Verdict
print("\n" + "="*70)
print("VERDICT")
print("="*70)

if len(significant_pp) >= 3:
    print("""
VALIDATED: Animal PP signature is statistically significant.

Multiple PP MIDDLEs show significant enrichment in animal records
that cannot be explained by chance (p < 0.01).

This supports documenting as C505: PP Profile Differentiation by Material Class
""")
elif len(significant_pp) >= 1:
    print("""
PARTIAL: Some PP MIDDLEs show significant enrichment, but not all.

Consider documenting with caveats about which PP are validated.
""")
else:
    print("""
NOT VALIDATED: No PP MIDDLEs show significant enrichment.

The observed enrichment ratios can be explained by chance.
Do NOT document as a constraint.
""")

# Also test the combined signature
print("\n" + "="*70)
print("COMBINED SIGNATURE TEST")
print("="*70)

# Test: do animal records have more of the "animal PP set" overall?
animal_pp_set = {'te', 'ho', 'ke', 'eod', 'eo', 'keo'}

def count_animal_pp(indices):
    """Count total animal-associated PP in given records."""
    total = 0
    for i in indices:
        total += len(pp_matrix[i] & animal_pp_set)
    return total / len(indices) if indices else 0

observed_animal_pp_mean = count_animal_pp(animal_indices)
observed_non_animal_pp_mean = count_animal_pp(non_animal_indices)
observed_diff = observed_animal_pp_mean - observed_non_animal_pp_mean

print(f"\nMean animal-PP count:")
print(f"  Animal records: {observed_animal_pp_mean:.3f}")
print(f"  Non-animal records: {observed_non_animal_pp_mean:.3f}")
print(f"  Difference: {observed_diff:.3f}")

# Permutation test for combined signature
perm_diffs = []
for perm in range(n_permutations):
    shuffled = all_indices.copy()
    random.shuffle(shuffled)
    perm_animal = shuffled[:n_animal]
    perm_non_animal = shuffled[n_animal:]

    perm_animal_mean = count_animal_pp(perm_animal)
    perm_non_animal_mean = count_animal_pp(perm_non_animal)
    perm_diffs.append(perm_animal_mean - perm_non_animal_mean)

n_exceed_combined = sum(1 for d in perm_diffs if d >= observed_diff)
p_combined = n_exceed_combined / n_permutations

print(f"\nPermutation test for combined signature:")
print(f"  Permutation mean diff: {np.mean(perm_diffs):.3f} (±{np.std(perm_diffs):.3f})")
print(f"  p-value: {p_combined:.4f}")

if p_combined < 0.01:
    print("  -> SIGNIFICANT: Animal records have elevated animal-PP signature")
else:
    print("  -> Not significant")
