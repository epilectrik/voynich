#!/usr/bin/env python3
"""
C499 Component Analysis: Is classification driven by MIDDLE or SUFFIX?

C499 assigned material class probabilities to "MIDDLEs" but actually stored
PREFIX-stripped tokens (MIDDLE+SUFFIX). This test checks whether the
high-confidence assignments are driven by:
- The true MIDDLE component (lexical identity)
- The SUFFIX component (procedural context)
- Both
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load C499 results
with open(PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json', 'r') as f:
    c499_data = json.load(f)

# Known suffixes (longest first for greedy match)
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_suffix(token):
    """Extract suffix from a token, return (core, suffix) or (token, None)."""
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            return token[:-len(s)], s
    return token, None

# Analyze C499 entries by material class
print("="*70)
print("C499 COMPONENT ANALYSIS")
print("="*70)

# Group by top_class
by_class = defaultdict(list)
for result in c499_data['results']:
    top_class = result.get('top_class')
    top_prob = result.get('top_class_probability', 0)
    middle_plus_suffix = result.get('middle')

    if top_prob >= 0.7:  # High confidence
        core, suffix = extract_suffix(middle_plus_suffix)
        by_class[top_class].append({
            'stored': middle_plus_suffix,
            'core': core,
            'suffix': suffix,
            'prob': top_prob
        })

print(f"\nHigh-confidence assignments (P >= 0.7):")
for cls, items in sorted(by_class.items(), key=lambda x: -len(x[1])):
    print(f"  {cls}: {len(items)} entries")

# For each class, analyze suffix distribution
print("\n" + "="*70)
print("SUFFIX DISTRIBUTION BY MATERIAL CLASS")
print("="*70)

for cls in ['animal', 'herb', 'hot_dry_herb', 'cold_moist_flower']:
    if cls not in by_class:
        continue
    items = by_class[cls]
    suffix_counts = Counter(item['suffix'] for item in items)
    total = len(items)

    print(f"\n{cls.upper()} (n={total}):")
    print(f"  Suffix distribution:")
    for suffix, count in suffix_counts.most_common():
        pct = 100 * count / total
        suffix_label = f"-{suffix}" if suffix else "(no suffix)"
        print(f"    {suffix_label}: {count} ({pct:.1f}%)")

    # Show unique cores
    unique_cores = set(item['core'] for item in items)
    print(f"  Unique MIDDLE cores: {len(unique_cores)}")
    if len(unique_cores) <= 10:
        print(f"    Cores: {sorted(unique_cores)}")

# Check if suffix alone could explain the classification
print("\n" + "="*70)
print("SUFFIX AS CLASSIFIER TEST")
print("="*70)

# For animal class specifically
animal_items = by_class.get('animal', [])
herb_items = by_class.get('herb', [])

if animal_items and herb_items:
    animal_suffixes = Counter(item['suffix'] for item in animal_items)
    herb_suffixes = Counter(item['suffix'] for item in herb_items)

    animal_total = len(animal_items)
    herb_total = len(herb_items)

    print(f"\nAnimal (n={animal_total}) vs Herb (n={herb_total}) suffix comparison:")
    print(f"\n{'Suffix':<12} {'Animal':>10} {'Herb':>10} {'Animal %':>10} {'Herb %':>10}")
    print("-"*55)

    all_suffixes = set(animal_suffixes.keys()) | set(herb_suffixes.keys())
    for suffix in sorted(all_suffixes, key=lambda x: (x is None, x)):
        a_count = animal_suffixes[suffix]
        h_count = herb_suffixes[suffix]
        a_pct = 100 * a_count / animal_total if animal_total else 0
        h_pct = 100 * h_count / herb_total if herb_total else 0
        suffix_label = f"-{suffix}" if suffix else "(none)"
        print(f"  {suffix_label:<10} {a_count:>10} {h_count:>10} {a_pct:>9.1f}% {h_pct:>9.1f}%")

# Check if MIDDLE cores are unique to classes
print("\n" + "="*70)
print("MIDDLE CORE UNIQUENESS TEST")
print("="*70)

animal_cores = set(item['core'] for item in animal_items)
herb_cores = set(item['core'] for item in herb_items)
hot_dry_cores = set(item['core'] for item in by_class.get('hot_dry_herb', []))

overlap_animal_herb = animal_cores & herb_cores
overlap_animal_hotdry = animal_cores & hot_dry_cores

print(f"\nAnimal MIDDLE cores: {len(animal_cores)}")
print(f"Herb MIDDLE cores: {len(herb_cores)}")
print(f"Hot_dry_herb MIDDLE cores: {len(hot_dry_cores)}")

print(f"\nOverlap animal & herb: {len(overlap_animal_herb)}")
if overlap_animal_herb:
    print(f"  Shared cores: {sorted(overlap_animal_herb)}")

print(f"\nOverlap animal & hot_dry_herb: {len(overlap_animal_hotdry)}")
if overlap_animal_hotdry:
    print(f"  Shared cores: {sorted(overlap_animal_hotdry)}")

# Final verdict
print("\n" + "="*70)
print("VERDICT")
print("="*70)

# Check if suffix distribution differs significantly
if animal_items and herb_items:
    # No suffix rate
    animal_no_suffix = sum(1 for item in animal_items if item['suffix'] is None)
    herb_no_suffix = sum(1 for item in herb_items if item['suffix'] is None)

    animal_no_suffix_pct = 100 * animal_no_suffix / animal_total
    herb_no_suffix_pct = 100 * herb_no_suffix / herb_total

    print(f"\nNo-suffix rate:")
    print(f"  Animal: {animal_no_suffix_pct:.1f}%")
    print(f"  Herb: {herb_no_suffix_pct:.1f}%")

    if animal_no_suffix_pct > 80 and herb_no_suffix_pct < 50:
        print("\n=> SUFFIX-DRIVEN: Animal class has mostly suffix-less tokens")
        print("   Classification may be detecting short/simple tokens, not material identity")
    elif len(overlap_animal_herb) == 0:
        print("\n=> MIDDLE-DRIVEN: No MIDDLE core overlap between classes")
        print("   Classification is driven by unique MIDDLE identities")
    else:
        print("\n=> MIXED: Both MIDDLE and SUFFIX contribute to classification")

# Show the actual animal entries for inspection
print("\n" + "="*70)
print("ANIMAL CLASS ENTRIES (P >= 0.9)")
print("="*70)

animal_high = [item for item in animal_items if item['prob'] >= 0.9]
print(f"\n{len(animal_high)} entries with P(animal) >= 0.9:")
for item in sorted(animal_high, key=lambda x: x['stored']):
    suffix_label = f"-{item['suffix']}" if item['suffix'] else "(none)"
    print(f"  {item['stored']:<15} = core '{item['core']}' + suffix {suffix_label}")
