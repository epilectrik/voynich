#!/usr/bin/env python3
"""Analyze closer RI MIDDLE frequency distribution."""

import json
from collections import Counter, defaultdict

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

# Group by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

# Get closer MIDDLEs and their counts
closer_counts = Counter()
for line_key, line_tokens in lines.items():
    if len(line_tokens) > 0:
        last = line_tokens[-1]
        if last['middle_class'] == 'exclusive':
            closer_counts[last['middle']] += 1

print('CLOSER RI MIDDLE FREQUENCY')
print('=' * 50)
print(f'Total closer tokens: {sum(closer_counts.values())}')
print(f'Distinct closer MIDDLEs: {len(closer_counts)}')
print(f'Average uses per MIDDLE: {sum(closer_counts.values())/len(closer_counts):.2f}')
print()

# Distribution
usage_dist = Counter(closer_counts.values())
print('Usage frequency distribution:')
for uses, count in sorted(usage_dist.items()):
    pct = 100 * count / len(closer_counts)
    print(f'  Used {uses}x: {count} MIDDLEs ({pct:.1f}%)')
print()

# Top closers
print('Top 15 most frequent closer MIDDLEs:')
for middle, count in closer_counts.most_common(15):
    print(f'  {middle}: {count}')
print()

# Singletons
singletons = [m for m, c in closer_counts.items() if c == 1]
print(f'Singleton closers (used exactly once): {len(singletons)} ({100*len(singletons)/len(closer_counts):.1f}%)')
print()

# Check morphology of top closers
print('Morphological patterns in top closers:')
top_closers = [m for m, c in closer_counts.most_common(20)]
ending_o = [m for m in top_closers if m.endswith('o')]
ending_od = [m for m in top_closers if m.endswith('od')]
ending_ol = [m for m in top_closers if m.endswith('ol')]
print(f'  Ending in -o: {ending_o}')
print(f'  Ending in -od: {ending_od}')
print(f'  Ending in -ol: {ending_ol}')
