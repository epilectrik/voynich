#!/usr/bin/env python3
"""Quick analysis: How many PREFIX families appear in each B folio?"""

import json
from pathlib import Path
from collections import defaultdict
import csv

# Load Currier B folio list
with open("results/unified_folio_profiles.json") as f:
    profiles = json.load(f)
    b_folios = set(f for f, p in profiles["profiles"].items() if p.get("system") == "B")

print(f"B folios: {len(b_folios)}")

# Define PREFIX families (from BPF phase)
PREFIX_FAMILIES = {
    'ch': 'ENERGY',
    'sh': 'ENERGY',
    'qo': 'ENERGY',
    'ok': 'FREQUENT',
    'ot': 'FREQUENT',
    'da': 'CORE',
    'ol': 'CORE',
    'ct': 'REGISTRY',
    'lk': 'L_COMPOUND',
    'lch': 'L_COMPOUND',
    'yk': 'EXT_CLUSTER',
    'yt': 'EXT_CLUSTER',
    'ke': 'KERNEL',
    'sa': 'A_PREFIX',
    'so': 'A_PREFIX',
    'al': 'OTHER',
    'op': 'OTHER',
    'lo': 'OTHER',
}

# All distinct prefixes to track
ALL_PREFIXES = list(PREFIX_FAMILIES.keys())

# Load interlinear data (TSV format)
folio_tokens = defaultdict(list)
with open("data/transcriptions/interlinear_full_words.txt", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        folio = row['folio']
        word = row['word'].strip('"')
        lang = row['language']
        # Only B language folios
        if lang == 'B' and folio in b_folios:
            folio_tokens[folio].append(word)

print(f"\nB Folios with tokens: {len(folio_tokens)}")
print(f"Total B tokens: {sum(len(t) for t in folio_tokens.values())}")

# Analyze each B folio
results = []
for folio in sorted(folio_tokens.keys()):
    tokens = folio_tokens[folio]

    # Count prefixes
    prefix_counts = defaultdict(int)
    family_counts = defaultdict(int)

    for token in tokens:
        for prefix in sorted(ALL_PREFIXES, key=len, reverse=True):  # Longest first
            if token.startswith(prefix):
                prefix_counts[prefix] += 1
                family_counts[PREFIX_FAMILIES[prefix]] += 1
                break

    n_prefixes = len([p for p, c in prefix_counts.items() if c > 0])
    n_families = len([f for f, c in family_counts.items() if c > 0])

    results.append({
        'folio': folio,
        'n_tokens': len(tokens),
        'n_distinct_prefixes': n_prefixes,
        'n_distinct_families': n_families,
        'prefixes_found': sorted([p for p, c in prefix_counts.items() if c > 0]),
        'families_found': sorted([f for f, c in family_counts.items() if c > 0]),
        'prefix_counts': dict(prefix_counts),
        'family_counts': dict(family_counts),
    })

if not results:
    print("No results found!")
    exit(1)

# Summary statistics
import statistics

n_prefixes_list = [r['n_distinct_prefixes'] for r in results]
n_families_list = [r['n_distinct_families'] for r in results]

print(f"\n=== PREFIX DIVERSITY PER B FOLIO ===")
print(f"Folios analyzed: {len(results)}")
print(f"\nDistinct PREFIXES per folio:")
print(f"  Min: {min(n_prefixes_list)}")
print(f"  Max: {max(n_prefixes_list)}")
print(f"  Mean: {statistics.mean(n_prefixes_list):.1f}")
print(f"  Median: {statistics.median(n_prefixes_list)}")

print(f"\nDistinct PREFIX FAMILIES per folio:")
print(f"  Min: {min(n_families_list)}")
print(f"  Max: {max(n_families_list)}")
print(f"  Mean: {statistics.mean(n_families_list):.1f}")
print(f"  Median: {statistics.median(n_families_list)}")

# Show distribution
from collections import Counter
prefix_dist = Counter(n_prefixes_list)
family_dist = Counter(n_families_list)

print(f"\nPREFIX count distribution:")
for n in sorted(prefix_dist.keys()):
    print(f"  {n} prefixes: {prefix_dist[n]} folios")

print(f"\nFAMILY count distribution:")
for n in sorted(family_dist.keys()):
    print(f"  {n} families: {family_dist[n]} folios")

# Show example folios at different complexity levels
print(f"\n=== SAMPLE FOLIOS ===")
results_sorted = sorted(results, key=lambda x: x['n_distinct_prefixes'])

print(f"\nLowest complexity ({results_sorted[0]['n_distinct_prefixes']} prefixes):")
r = results_sorted[0]
print(f"  {r['folio']}: {r['n_tokens']} tokens, prefixes: {r['prefixes_found']}")
print(f"  families: {r['families_found']}")

mid_idx = len(results_sorted) // 2
print(f"\nMedian complexity ({results_sorted[mid_idx]['n_distinct_prefixes']} prefixes):")
r = results_sorted[mid_idx]
print(f"  {r['folio']}: {r['n_tokens']} tokens, prefixes: {r['prefixes_found']}")
print(f"  families: {r['families_found']}")

print(f"\nHighest complexity ({results_sorted[-1]['n_distinct_prefixes']} prefixes):")
r = results_sorted[-1]
print(f"  {r['folio']}: {r['n_tokens']} tokens, prefixes: {r['prefixes_found']}")
print(f"  families: {r['families_found']}")

# Save results
output = {
    'summary': {
        'n_folios': len(results),
        'prefix_stats': {
            'min': min(n_prefixes_list),
            'max': max(n_prefixes_list),
            'mean': statistics.mean(n_prefixes_list),
            'median': statistics.median(n_prefixes_list),
        },
        'family_stats': {
            'min': min(n_families_list),
            'max': max(n_families_list),
            'mean': statistics.mean(n_families_list),
            'median': statistics.median(n_families_list),
        },
        'prefix_distribution': dict(prefix_dist),
        'family_distribution': dict(family_dist),
    },
    'folios': results
}

with open('results/prefix_per_folio.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to results/prefix_per_folio.json")
