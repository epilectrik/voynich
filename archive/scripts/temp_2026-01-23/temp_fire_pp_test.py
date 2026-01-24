#!/usr/bin/env python3
"""
Test 3: Fire Degree -> PP Correlation

Question: Do different Brunschwig fire degrees correlate with distinct PP signatures?

Note: Fire degree 4 is empty in Brunschwig data, so we test:
- Fire 1 (gentle): flowers, delicate materials
- Fire 2 (standard): most herbs
- Fire 3 (moderate): tougher herbs, roots, some animal products

Method:
1. Use material_class_priors.json to identify RI MIDDLEs associated with each fire degree
2. Find A records by fire degree category
3. Compare PP profiles across fire degrees
4. Test if fire degree predicts PP signature
"""

import json
import numpy as np
import random
from collections import Counter, defaultdict

# Load Brunschwig data to get fire degree -> material class mapping
with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    brunschwig = json.load(f)

recipes = brunschwig['recipes']

# Build material class -> fire degree mapping (most common fire degree per class)
class_fire_map = defaultdict(list)
for r in recipes:
    cls = r.get('material_class')
    fire = r.get('fire_degree')
    if cls and fire:
        class_fire_map[cls].append(fire)

# Assign each class to its most common fire degree
class_to_fire = {}
for cls, fires in class_fire_map.items():
    if fires:
        most_common = Counter(fires).most_common(1)[0][0]
        class_to_fire[cls] = most_common

print("="*70)
print("FIRE DEGREE -> PP CORRELATION TEST")
print("="*70)

print("\nMaterial class to fire degree mapping:")
for fire in [1, 2, 3]:
    classes = [cls for cls, f in class_to_fire.items() if f == fire]
    print(f"  Fire {fire}: {classes}")

# ============================================================
# Load PP/RI data
# ============================================================
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

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

print(f"\nPP MIDDLEs: {len(pp_middles)}")
print(f"RI MIDDLEs: {len(ri_middles)}")

# ============================================================
# STEP 1: Assign RI MIDDLEs to fire degrees via material class
# ============================================================
print("\n" + "="*70)
print("STEP 1: ASSIGN RI MIDDLEs TO FIRE DEGREES")
print("="*70)

# Load material class priors
with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json') as f:
    priors_data = json.load(f)

# Map RI MIDDLEs to fire degrees
ri_to_fire = {}
fire_to_ri = defaultdict(set)

for entry in priors_data['results']:
    middle = entry['middle']
    top_class = entry['top_class']
    top_prob = entry['top_class_probability']

    if middle in ri_middles and top_prob >= 0.5:
        # Get fire degree for this material class
        fire = class_to_fire.get(top_class)
        if fire:
            ri_to_fire[middle] = fire
            fire_to_ri[fire].add(middle)

print("\nRI MIDDLEs by fire degree:")
for fire in [1, 2, 3]:
    print(f"  Fire {fire}: {len(fire_to_ri[fire])} MIDDLEs")

# ============================================================
# STEP 2: Assign A records to fire degree categories
# ============================================================
print("\n" + "="*70)
print("STEP 2: ASSIGN A RECORDS TO FIRE DEGREES")
print("="*70)

# Build PP presence matrix
pp_matrix = []
for rec in records:
    middles = set(rec['a_middles'])
    pp_in_record = middles & pp_middles
    pp_matrix.append(pp_in_record)

# Assign records to fire degrees based on RI content
record_fire = []
for i, rec in enumerate(records):
    middles = set(rec['a_middles'])
    ri_in_record = middles & ri_middles

    # Score record by fire degree
    fire_scores = defaultdict(float)
    for m in ri_in_record:
        if m in ri_to_fire:
            fire_scores[ri_to_fire[m]] += 1

    if fire_scores:
        dominant_fire = max(fire_scores.items(), key=lambda x: x[1])[0]
        record_fire.append({
            'index': i,
            'fire': dominant_fire,
            'scores': dict(fire_scores),
            'pp_middles': pp_matrix[i]
        })
    else:
        record_fire.append({
            'index': i,
            'fire': None,
            'scores': {},
            'pp_middles': pp_matrix[i]
        })

# Count records by fire degree
fire_counts = Counter(r['fire'] for r in record_fire if r['fire'])
print("\nRecords by fire degree:")
for fire, cnt in sorted(fire_counts.items()):
    print(f"  Fire {fire}: {cnt} records")

# ============================================================
# STEP 3: PP profiles by fire degree
# ============================================================
print("\n" + "="*70)
print("STEP 3: PP PROFILES BY FIRE DEGREE")
print("="*70)

fire_indices = defaultdict(list)
for r in record_fire:
    if r['fire']:
        fire_indices[r['fire']].append(r['index'])

for fire in [1, 2, 3]:
    if fire in fire_indices:
        indices = fire_indices[fire]
        pp_counter = Counter()
        for i in indices:
            for pp in pp_matrix[i]:
                pp_counter[pp] += 1

        n = len(indices)
        print(f"\nFire {fire} (n={n}):")
        print(f"  Top PP (rate): ", end="")
        top_pp = pp_counter.most_common(8)
        for pp, cnt in top_pp:
            print(f"'{pp}'={cnt/n*100:.0f}% ", end="")
        print()

# ============================================================
# STEP 4: Fire degree discrimination test
# ============================================================
print("\n" + "="*70)
print("STEP 4: FIRE DEGREE DISCRIMINATION")
print("="*70)

def compute_enrichment(group1_indices, group2_indices, target_pp):
    """Compute enrichment of target_pp in group1 vs group2."""
    count1 = sum(1 for i in group1_indices if target_pp in pp_matrix[i])
    count2 = sum(1 for i in group2_indices if target_pp in pp_matrix[i])

    rate1 = count1 / len(group1_indices) if group1_indices else 0
    rate2 = count2 / len(group2_indices) if group2_indices else 0

    if rate2 > 0:
        enrichment = rate1 / rate2
    else:
        enrichment = float('inf') if rate1 > 0 else 1.0

    return enrichment, rate1, rate2

# Test Fire 1 vs Fire 2-3 (gentle vs standard+moderate)
if 1 in fire_indices and (2 in fire_indices or 3 in fire_indices):
    gentle_idx = fire_indices[1]
    standard_idx = fire_indices.get(2, []) + fire_indices.get(3, [])

    print(f"\nFire 1 (gentle) vs Fire 2-3 (standard/moderate):")
    print(f"  Gentle records: {len(gentle_idx)}")
    print(f"  Standard/moderate records: {len(standard_idx)}")

    # Test key PP
    test_pp = list(pp_middles)

    discriminative = []
    for pp in test_pp:
        enrich, gentle_rate, standard_rate = compute_enrichment(gentle_idx, standard_idx, pp)

        if gentle_rate > 0.1 or standard_rate > 0.1:
            if enrich > 2:
                discriminative.append((pp, gentle_rate, standard_rate, enrich, 'gentle'))
            elif enrich > 0 and enrich < 0.5:
                discriminative.append((pp, gentle_rate, standard_rate, 1/enrich, 'standard'))

    # Sort by enrichment
    discriminative.sort(key=lambda x: -x[3])

    print("\nPP enriched in gentle (Fire 1):")
    for pp, gr, sr, enrich, direction in discriminative[:10]:
        if direction == 'gentle':
            print(f"  '{pp}': gentle={gr*100:.1f}%, standard={sr*100:.1f}%, {enrich:.1f}x")

    print("\nPP enriched in standard/moderate (Fire 2-3):")
    for pp, gr, sr, enrich, direction in discriminative:
        if direction == 'standard':
            print(f"  '{pp}': standard={sr*100:.1f}%, gentle={gr*100:.1f}%, {enrich:.1f}x")

# ============================================================
# STEP 5: Permutation test for fire degree
# ============================================================
print("\n" + "="*70)
print("STEP 5: PERMUTATION TEST (Fire 1 vs Fire 2-3)")
print("="*70)

if 1 in fire_indices and (2 in fire_indices or 3 in fire_indices):
    gentle_idx = fire_indices[1]
    standard_idx = fire_indices.get(2, []) + fire_indices.get(3, [])

    # Take top discriminative PP for testing
    top_test_pp = [d[0] for d in discriminative[:10]]

    n_permutations = 1000
    random.seed(42)

    combined = gentle_idx + standard_idx
    n_gentle = len(gentle_idx)

    print(f"\nTesting {len(top_test_pp)} discriminative PP MIDDLEs:")

    results = []
    for pp in top_test_pp:
        obs_enrich, obs_gentle, obs_standard = compute_enrichment(gentle_idx, standard_idx, pp)

        perm_enrichments = []
        for _ in range(n_permutations):
            shuffled = combined.copy()
            random.shuffle(shuffled)
            perm_gentle = shuffled[:n_gentle]
            perm_standard = shuffled[n_gentle:]
            enrich, _, _ = compute_enrichment(perm_gentle, perm_standard, pp)
            perm_enrichments.append(enrich)

        if obs_enrich >= 1:
            if obs_enrich == float('inf'):
                n_exceed = sum(1 for v in perm_enrichments if v == float('inf'))
            else:
                n_exceed = sum(1 for v in perm_enrichments if v >= obs_enrich)
            p_value = n_exceed / n_permutations
        else:
            n_below = sum(1 for v in perm_enrichments if v <= obs_enrich)
            p_value = n_below / n_permutations

        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

        results.append({
            'pp': pp,
            'enrichment': obs_enrich,
            'p_value': p_value,
            'significant': p_value < 0.05
        })

        print(f"  '{pp}': enrich={obs_enrich:.2f}x, p={p_value:.4f} {sig}")

    sig_count = sum(1 for r in results if r['significant'])
    print(f"\n  Significant (p<0.05): {sig_count}/{len(results)}")

# ============================================================
# STEP 6: Cross-check with animal PP signature
# ============================================================
print("\n" + "="*70)
print("STEP 6: CROSS-CHECK WITH ANIMAL PP SIGNATURE (C505)")
print("="*70)

# The animal-enriched PP from C505 were 'te', 'ho', 'ke'
# Animals in Brunschwig are typically Fire 1 (gentle for eggs/honey) or Fire 3 (for processing)
animal_pp = ['te', 'ho', 'ke', 'eod', 'eo', 'keo']

print("\nAnimal-signature PP ('te', 'ho', 'ke') by fire degree:")
for fire in [1, 2, 3]:
    if fire in fire_indices:
        indices = fire_indices[fire]
        n = len(indices)
        for pp in animal_pp[:3]:  # Just the top 3
            count = sum(1 for i in indices if pp in pp_matrix[i])
            rate = count / n * 100
            print(f"  Fire {fire}: '{pp}' = {rate:.1f}%")

# ============================================================
# STEP 7: Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Fire Degree -> PP Correlation Test Results:

FIRE DEGREE DISTRIBUTION:
  Fire 1 (gentle): {len(fire_indices.get(1, []))} records - flowers, delicate materials
  Fire 2 (standard): {len(fire_indices.get(2, []))} records - most herbs
  Fire 3 (moderate): {len(fire_indices.get(3, []))} records - roots, tougher materials

KEY FINDING:
""")

if results:
    sig_pp = [r['pp'] for r in results if r['significant']]
    if sig_pp:
        print(f"  {len(sig_pp)} PP MIDDLEs show significant fire degree discrimination")
        print(f"  Discriminative PP: {sig_pp[:5]}")
        print("""
INTERPRETATION:
  If PP correlates with fire degree, it suggests PP encodes thermal requirements.
  Combined with C505 (animal PP signature), this would mean:
  - PP encodes processing parameters (fire, handling, etc.)
  - Different material types need different PP profiles
  - PP is an operational affordance carrier
""")
    else:
        print("  No PP MIDDLEs show significant fire degree discrimination")
        print("""
INTERPRETATION:
  Fire degree may not be the primary axis of PP variation.
  Material class (animal vs herb) may be more relevant than thermal regime.
""")
