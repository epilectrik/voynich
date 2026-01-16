#!/usr/bin/env python3
"""Quick stats for tokens per line in B folios."""
import csv
from collections import defaultdict

line_tokens = defaultdict(int)
with open('data/transcriptions/interlinear_full_words.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['language'] == 'B':
            key = (row['folio'], row['line_number'])
            line_tokens[key] += 1

counts = list(line_tokens.values())
print(f'Total B lines: {len(counts)}')
print(f'Tokens per line: min={min(counts)}, max={max(counts)}, mean={sum(counts)/len(counts):.1f}')

# Distribution
from collections import Counter
dist = Counter(counts)
print('\nDistribution:')
for n in sorted(dist.keys())[:15]:
    print(f'  {n} tokens: {dist[n]} lines')
