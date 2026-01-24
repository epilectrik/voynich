#!/usr/bin/env python3
"""
Test: Do PP profiles predict WHICH B classes survive (not just count)?

Hypothesis: Animal records may have different CLASS COMPOSITION even if
total survival count is similar.
"""

import json
import pandas as pd
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

# Load A records survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json', encoding='utf-8') as f:
    survivors = json.load(f)

# Animal RI MIDDLEs for record identification
animal_ri_middles = {'eyd', 'chald', 'hyd', 'olfcho', 'eoschso', 'hdaoto', 'cthso', 'teold', 'olar', 'hod'}

# Identify animal records from the survivor data
animal_records = []
baseline_records = []

for record_data in survivors['records']:
    record_middles = set(record_data['a_middles'])
    if record_middles & animal_ri_middles:
        animal_records.append(record_data)
    else:
        baseline_records.append(record_data)

print("=" * 70)
print("PP PROFILE -> B CLASS SPECIFICITY TEST")
print("=" * 70)
print(f"\nAnimal records: {len(animal_records)}")
print(f"Baseline records: {len(baseline_records)}")

# Compute class survival rates for each group
def compute_class_rates(records):
    """Compute survival rate for each B class across records."""
    class_counts = Counter()
    for rec in records:
        for cls in rec['surviving_classes']:
            class_counts[cls] += 1
    return {cls: count / len(records) for cls, count in class_counts.items()}

animal_rates = compute_class_rates(animal_records)
baseline_rates = compute_class_rates(baseline_records)

# Get all classes
all_classes = set(animal_rates.keys()) | set(baseline_rates.keys())

print("\n" + "-" * 50)
print("CLASS SURVIVAL RATE COMPARISON")
print("-" * 50)
print(f"{'Class':>6} {'Animal':>10} {'Baseline':>10} {'Diff':>10} {'Enrichment':>12}")
print("-" * 50)

# Compute enrichment for each class
enrichments = []
for cls in sorted(all_classes):
    animal_rate = animal_rates.get(cls, 0)
    baseline_rate = baseline_rates.get(cls, 0)
    diff = animal_rate - baseline_rate
    enrichment = animal_rate / baseline_rate if baseline_rate > 0 else 0

    enrichments.append((cls, animal_rate, baseline_rate, diff, enrichment))

# Sort by absolute difference
enrichments.sort(key=lambda x: -abs(x[3]))

for cls, animal_rate, baseline_rate, diff, enrichment in enrichments[:20]:
    sign = '+' if diff > 0 else ''
    print(f"{cls:>6} {animal_rate*100:>9.1f}% {baseline_rate*100:>9.1f}% {sign}{diff*100:>9.1f}% {enrichment:>11.2f}x")

# Statistical test: Are the class compositions different?
print("\n" + "-" * 50)
print("STATISTICAL TESTS")
print("-" * 50)

# Chi-square test on class survival patterns
print("\nPer-class Chi-square tests (significant at p<0.05):")
significant_classes = []
for cls in sorted(all_classes):
    # 2x2 contingency table: [animal_has_class, animal_lacks_class] vs [baseline_has, baseline_lacks]
    animal_has = sum(1 for r in animal_records if cls in r['surviving_classes'])
    animal_lacks = len(animal_records) - animal_has
    baseline_has = sum(1 for r in baseline_records if cls in r['surviving_classes'])
    baseline_lacks = len(baseline_records) - baseline_has

    # Fisher's exact test (better for small samples)
    _, p_val = stats.fisher_exact([[animal_has, animal_lacks], [baseline_has, baseline_lacks]])

    if p_val < 0.05:
        significant_classes.append((cls, p_val, animal_rates.get(cls, 0), baseline_rates.get(cls, 0)))
        print(f"  Class {cls}: p={p_val:.4f} (Animal: {animal_has}/{len(animal_records)}, Baseline: {baseline_has}/{len(baseline_records)})")

if not significant_classes:
    print("  No individual classes show significant difference")

# Cosine similarity of class vectors
print("\n" + "-" * 50)
print("PROFILE SIMILARITY")
print("-" * 50)

# Build class vectors
animal_vec = np.array([animal_rates.get(cls, 0) for cls in sorted(all_classes)])
baseline_vec = np.array([baseline_rates.get(cls, 0) for cls in sorted(all_classes)])

cosine_sim = np.dot(animal_vec, baseline_vec) / (np.linalg.norm(animal_vec) * np.linalg.norm(baseline_vec))
print(f"Cosine similarity of class profiles: {cosine_sim:.4f}")
print(f"  (1.0 = identical, 0.0 = orthogonal)")

# Jensen-Shannon divergence
def js_divergence(p, q):
    """Compute JS divergence between two distributions."""
    p = np.array(p) / np.sum(p) if np.sum(p) > 0 else np.zeros_like(p)
    q = np.array(q) / np.sum(q) if np.sum(q) > 0 else np.zeros_like(q)
    m = 0.5 * (p + q)
    # Avoid log(0) by adding small epsilon
    eps = 1e-10
    p = p + eps
    q = q + eps
    m = m + eps
    return 0.5 * (stats.entropy(p, m) + stats.entropy(q, m))

js_div = js_divergence(animal_vec, baseline_vec)
print(f"JS divergence: {js_div:.4f}")
print(f"  (0.0 = identical, higher = more different)")

# Mean survival rates
print("\n" + "-" * 50)
print("MEAN CLASS SURVIVAL RATES")
print("-" * 50)
print(f"Animal mean class rate: {np.mean(list(animal_rates.values()))*100:.1f}%")
print(f"Baseline mean class rate: {np.mean(list(baseline_rates.values()))*100:.1f}%")

# Classes that survive more often in animal records
print("\n" + "-" * 50)
print("CLASSES FAVORING ANIMAL RECORDS (rate diff > 10%)")
print("-" * 50)
for cls, animal_rate, baseline_rate, diff, enrichment in enrichments:
    if diff > 0.10:
        print(f"  Class {cls}: +{diff*100:.1f}% ({enrichment:.2f}x)")

print("\n" + "-" * 50)
print("CLASSES FAVORING BASELINE RECORDS (rate diff < -10%)")
print("-" * 50)
for cls, animal_rate, baseline_rate, diff, enrichment in enrichments:
    if diff < -0.10:
        print(f"  Class {cls}: {diff*100:.1f}%")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Animal records: {len(animal_records)}")
print(f"Cosine similarity: {cosine_sim:.4f} (high = similar class profiles)")
print(f"JS divergence: {js_div:.4f} (low = similar distributions)")
print(f"Significant classes: {len(significant_classes)}")
