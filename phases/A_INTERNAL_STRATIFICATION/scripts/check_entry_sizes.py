#!/usr/bin/env python3
"""Quick check of entry token counts."""

import json
from collections import Counter
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(RESULTS_DIR / 'entry_data.json') as f:
    entries = json.load(f)

# Count entries by token count
token_counts = Counter(e['n_tokens'] for e in entries)
print('Entry token counts:')
for n, count in sorted(token_counts.items())[:15]:
    print(f'  {n} tokens: {count} entries ({100*count/len(entries):.1f}%)')

# Count entries with 2+ tokens
multi_token = sum(1 for e in entries if e['n_tokens'] >= 2)
print(f'\nEntries with 2+ tokens: {multi_token} ({100*multi_token/len(entries):.1f}%)')

# Check: in multi-token entries, how many have >1 unique MIDDLE?
multi_middle = 0
for e in entries:
    middles = set(t['middle'] for t in e['tokens'])
    if len(middles) >= 2:
        multi_middle += 1

print(f'Entries with 2+ unique MIDDLEs: {multi_middle} ({100*multi_middle/len(entries):.1f}%)')
