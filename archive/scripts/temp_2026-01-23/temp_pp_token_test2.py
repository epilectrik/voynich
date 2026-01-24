#!/usr/bin/env python3
"""
Test: Does PP composition affect token availability within classes?
"""

import json
import pandas as pd
from collections import defaultdict
from itertools import combinations

# Load class-token mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)

token_to_class = data['token_to_class']
token_to_middle = data['token_to_middle']

# Build class_to_tokens
class_to_tokens = defaultdict(list)
for token, cls in token_to_class.items():
    class_to_tokens[cls].append(token)

# Load survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors = json.load(f)

records = survivors['records']

print("=" * 70)
print("PP COMPOSITION -> TOKEN-LEVEL EFFECT")
print("=" * 70)

# Group by surviving_class_count
by_count = defaultdict(list)
for rec in records:
    by_count[rec['surviving_class_count']].append(rec)

# Find pairs with SAME classes (not just count) but DIFFERENT PP composition
print("\nFinding A records with identical class survival but different PP sets...")

# Convert surviving_classes to frozenset for comparison
by_class_set = defaultdict(list)
for rec in records:
    key = frozenset(rec['surviving_classes'])
    by_class_set[key].append(rec)

# Analyze groups with multiple records (same class survival)
total_comparisons = 0
token_overlaps = []

for class_set, recs in by_class_set.items():
    if len(recs) < 2:
        continue

    # Compare all pairs
    for rec_i, rec_j in combinations(recs, 2):
        pp_i = set(rec_i['a_middles'])
        pp_j = set(rec_j['a_middles'])

        if pp_i == pp_j:
            continue  # Same PP, skip

        # Compute token availability for each
        tokens_i = set()
        tokens_j = set()

        for cls in class_set:
            for tok in class_to_tokens[cls]:
                m = token_to_middle.get(tok)
                if m and m in pp_i:
                    tokens_i.add(tok)
                if m and m in pp_j:
                    tokens_j.add(tok)

        if tokens_i and tokens_j:
            union = tokens_i | tokens_j
            intersection = tokens_i & tokens_j
            jaccard = len(intersection) / len(union)
            token_overlaps.append(jaccard)
            total_comparisons += 1

print(f"\nPairs with same class survival, different PP: {total_comparisons}")

if token_overlaps:
    import statistics
    mean_j = statistics.mean(token_overlaps)
    median_j = statistics.median(token_overlaps)
    min_j = min(token_overlaps)
    max_j = max(token_overlaps)

    print(f"\nToken Jaccard overlap (same classes, different PP):")
    print(f"  Mean:   {mean_j:.3f}")
    print(f"  Median: {median_j:.3f}")
    print(f"  Min:    {min_j:.3f}")
    print(f"  Max:    {max_j:.3f}")

    # Distribution
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    print(f"\nDistribution:")
    for i in range(len(bins)-1):
        count = sum(1 for j in token_overlaps if bins[i] <= j < bins[i+1])
        pct = 100 * count / len(token_overlaps)
        print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}: {count} ({pct:.1f}%)")

    # Perfect overlap count
    perfect = sum(1 for j in token_overlaps if j > 0.99)
    print(f"\n  Perfect overlap (>0.99): {perfect} ({100*perfect/len(token_overlaps):.1f}%)")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
print("""
If mean Jaccard = 1.0:
  -> PP composition doesn't affect token selection
  -> Class survival fully determines token availability

If mean Jaccard < 1.0:
  -> PP composition DOES affect which tokens are available
  -> Same class survival can mean different execution options

If mean Jaccard << 1.0 (e.g., <0.5):
  -> PP composition STRONGLY affects token availability
  -> Class-level analysis misses important variation
""")
