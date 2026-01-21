#!/usr/bin/env python3
"""Quick check of PP MIDDLE frequency distribution."""

import json
from collections import Counter

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])

# Count PP MIDDLE frequencies
pp_middle_counts = Counter()
for t in tokens:
    if t['middle'] not in ri_middles:
        pp_middle_counts[t['middle']] += 1

print(f'PP MIDDLEs: {len(pp_middle_counts)}')
print(f'PP tokens: {sum(pp_middle_counts.values())}')
print()

# Frequency distribution
singletons = sum(1 for m, c in pp_middle_counts.items() if c == 1)
low_freq = sum(1 for m, c in pp_middle_counts.items() if c <= 3)
mid_freq = sum(1 for m, c in pp_middle_counts.items() if 4 <= c <= 20)
high_freq = sum(1 for m, c in pp_middle_counts.items() if c >= 50)

print('FREQUENCY DISTRIBUTION:')
print(f'  Singletons (used once): {singletons} ({100*singletons/len(pp_middle_counts):.1f}%)')
print(f'  Low frequency (<=3): {low_freq} ({100*low_freq/len(pp_middle_counts):.1f}%)')
print(f'  Mid frequency (4-20): {mid_freq} ({100*mid_freq/len(pp_middle_counts):.1f}%)')
print(f'  High frequency (>=50): {high_freq} ({100*high_freq/len(pp_middle_counts):.1f}%)')
print()

# Token coverage
singleton_tokens = sum(c for m, c in pp_middle_counts.items() if c == 1)
top10_tokens = sum(c for m, c in pp_middle_counts.most_common(10))
print('TOKEN COVERAGE:')
print(f'  Singleton MIDDLEs cover: {singleton_tokens} tokens ({100*singleton_tokens/sum(pp_middle_counts.values()):.1f}%)')
print(f'  Top 10 MIDDLEs cover: {top10_tokens} tokens ({100*top10_tokens/sum(pp_middle_counts.values()):.1f}%)')
print()

# Top 15 PP MIDDLEs
print('TOP 15 PP MIDDLEs:')
for m, c in pp_middle_counts.most_common(15):
    print(f'  {m}: {c}')
print()

# Example singletons
print('EXAMPLE SINGLETON PP MIDDLEs:')
singletons_list = [m for m, c in pp_middle_counts.items() if c == 1][:15]
for m in singletons_list:
    print(f'  {m}')
