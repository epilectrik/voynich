#!/usr/bin/env python
"""Check Q3 pattern."""
import json

with open('C:/git/voynich/phases/exploration/first_token_data.json') as f:
    data = json.load(f)

# Get Q3 folios (17-24)
q3 = [r for r in data['records'] if 17 <= int(r['folio_id'][:-1]) <= 24]

print('Q3 first tokens:')
for r in q3:
    marker = '***' if r['token'] == 'pchor' else '   '
    print(f"  {marker} {r['folio_id']}: {r['token']}")

print()
# Check if any OTHER prefix repeats at 2-folio intervals
from collections import defaultdict
prefix_positions = defaultdict(list)
for i, r in enumerate(data['records']):
    prefix_positions[r['prefix_2char']].append((i, r['folio_id']))

print('Prefixes appearing 2+ times with their positions:')
for prefix, positions in sorted(prefix_positions.items()):
    if len(positions) >= 2:
        folios = [p[1] for p in positions]
        # Check spacing
        indices = [p[0] for p in positions]
        spacings = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
        print(f'  {prefix}: {folios} (spacings: {spacings})')
