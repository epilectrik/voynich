#!/usr/bin/env python3
"""
Check: Are certain PREFIX+SUFFIX combinations enriched or depleted?

If SUFFIX = product type and PREFIX = processing stage:
  - Certain stage+product combinations might be preferred
  - e.g., "gentle heat (ch) + water (-y)" vs "strong heat + oil (-ol)"
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path
import math

PROJECT_ROOT = Path('.')

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_parts(token):
    if not token:
        return None, None, None
    prefix = None
    suffix = None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break
    return prefix, token if token else None, suffix

# Collect PREFIX+SUFFIX co-occurrence
prefix_suffix_counts = defaultdict(Counter)
prefix_total = Counter()
suffix_total = Counter()
total_with_both = 0

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)

        if prefix and suffix:
            prefix_suffix_counts[prefix][suffix] += 1
            prefix_total[prefix] += 1
            suffix_total[suffix] += 1
            total_with_both += 1

# Calculate enrichment matrix
print("="*70)
print("PREFIX x SUFFIX CO-OCCURRENCE MATRIX")
print("="*70)

main_prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'd', 'o', 's']
main_suffixes = ['y', 'dy', 'ol', 'or', 'ey', 'ar', 'al', 'am']

print(f"\nRaw counts (tokens with both prefix and suffix):")
print(f"Total: {total_with_both}")

# Header
header = "PREFIX  " + "".join(f"{s:>7}" for s in main_suffixes)
print(f"\n{header}")
print("-" * len(header))

for prefix in main_prefixes:
    row = f"  {prefix:<6}"
    for suffix in main_suffixes:
        count = prefix_suffix_counts[prefix][suffix]
        row += f"{count:>7}"
    print(row)

# Calculate expected counts and enrichment
print("\n" + "="*70)
print("ENRICHMENT RATIOS (observed/expected)")
print("="*70)
print("Values > 1.3 are enriched (**), < 0.7 are depleted (--))")

print(f"\n{header}")
print("-" * len(header))

enrichments = {}
for prefix in main_prefixes:
    row = f"  {prefix:<6}"
    for suffix in main_suffixes:
        observed = prefix_suffix_counts[prefix][suffix]
        # Expected under independence
        expected = (prefix_total[prefix] * suffix_total[suffix]) / total_with_both if total_with_both else 0

        if expected > 5:  # Only for sufficient data
            ratio = observed / expected
            enrichments[(prefix, suffix)] = ratio
            if ratio > 1.3:
                row += f" {ratio:>5.2f}**"
            elif ratio < 0.7:
                row += f" {ratio:>5.2f}--"
            else:
                row += f" {ratio:>5.2f}  "
        else:
            row += "      -"
    print(row)

# Find the most extreme combinations
print("\n" + "="*70)
print("MOST ENRICHED/DEPLETED COMBINATIONS")
print("="*70)

sorted_enrich = sorted(enrichments.items(), key=lambda x: x[1], reverse=True)

print("\nMost ENRICHED (process stage -> product type?):")
for (prefix, suffix), ratio in sorted_enrich[:10]:
    count = prefix_suffix_counts[prefix][suffix]
    print(f"  {prefix} + {suffix}: {ratio:.2f}x (n={count})")

print("\nMost DEPLETED (incompatible combinations?):")
for (prefix, suffix), ratio in sorted_enrich[-10:]:
    count = prefix_suffix_counts[prefix][suffix]
    print(f"  {prefix} + {suffix}: {ratio:.2f}x (n={count})")

# Check suffix-suffix patterns on same line
print("\n" + "="*70)
print("DO MULTIPLE SUFFIXES APPEAR ON SAME LINE?")
print("="*70)

line_suffixes = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        line = row.get('line', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if suffix:
            line_suffixes[(folio, line)].add(suffix)

# Count lines with mixed suffixes
single_suffix_lines = sum(1 for s in line_suffixes.values() if len(s) == 1)
multi_suffix_lines = sum(1 for s in line_suffixes.values() if len(s) > 1)
total_lines = len(line_suffixes)

print(f"\nLines with single suffix type: {single_suffix_lines} ({100*single_suffix_lines/total_lines:.1f}%)")
print(f"Lines with multiple suffix types: {multi_suffix_lines} ({100*multi_suffix_lines/total_lines:.1f}%)")

# What suffix combinations appear together?
suffix_pair_counts = Counter()
for suffixes in line_suffixes.values():
    if len(suffixes) >= 2:
        for s1 in suffixes:
            for s2 in suffixes:
                if s1 < s2:  # Avoid double counting
                    suffix_pair_counts[(s1, s2)] += 1

print("\nMost common suffix pairs on same line:")
for (s1, s2), count in suffix_pair_counts.most_common(10):
    print(f"  -{s1} + -{s2}: {count} lines")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If suffix = product type:
  - Different products from same batch might appear on same line
  - High multi-suffix lines = multiple outputs specified
  - Enriched PREFIX+SUFFIX = preferred process->product mappings
""")
