#!/usr/bin/env python
"""Check for sequential patterns in first tokens."""
import json
from collections import Counter

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

print('=== First Token Sequence Across Folios ===')
print()

for r in data['records']:
    status = 'PASS' if r['is_pass'] else 'FAIL'
    print(f"{r['folio_id']:8} {r['token']:15} {r['prefix_2char']:6} {status}")

print()
print('=== Looking for Patterns ===')

prefixes = [r['prefix_2char'] for r in data['records']]
tokens = [r['token'] for r in data['records']]
print('Prefix sequence:', ' '.join(prefixes))

# Check for runs of same prefix
runs = []
current_run = [prefixes[0]]
for i in range(1, len(prefixes)):
    if prefixes[i] == prefixes[i-1]:
        current_run.append(prefixes[i])
    else:
        if len(current_run) > 1:
            runs.append((current_run[0], len(current_run)))
        current_run = [prefixes[i]]
if len(current_run) > 1:
    runs.append((current_run[0], len(current_run)))

print('Runs of same prefix:', runs if runs else 'NONE')

# Check transitions
transitions = Counter()
for i in range(len(prefixes)-1):
    transitions[(prefixes[i], prefixes[i+1])] += 1

print()
print('Top transitions:')
for (p1, p2), count in transitions.most_common(10):
    print(f'  {p1} -> {p2}: {count}')

# Check for token repetition
print()
print('=== Token Repetition ===')
token_counts = Counter(tokens)
repeated = [(t, c) for t, c in token_counts.items() if c > 1]
if repeated:
    print('Repeated first tokens:')
    for t, c in repeated:
        print(f'  {t}: {c}x')
else:
    print('No repeated first tokens (all unique)')

# Check for suffix patterns
print()
print('=== Suffix Sequence ===')
suffixes = [r['suffix_2char'] for r in data['records']]
print('Suffix sequence:', ' '.join(suffixes))

# Check for any numeric-like progression in remainders
print()
print('=== Remainder Patterns ===')
remainders = [r['hyp_remainder'] for r in data['records']]
print('Remainders:', remainders[:20], '...')

# Check if ko- tokens show any ordering
print()
print('=== ko- Token Positions ===')
ko_positions = [(i, r['folio_id'], r['token']) for i, r in enumerate(data['records']) if r['prefix_2char'] == 'ko']
print('ko- appears at positions:', ko_positions)

# Check spacing between ko- occurrences
if len(ko_positions) > 1:
    spacings = [ko_positions[i+1][0] - ko_positions[i][0] for i in range(len(ko_positions)-1)]
    print('Spacing between ko- tokens:', spacings)

# Check if ko- suffixes show pattern
print()
print('=== ko- suffix endings ===')
ko_suffixes = [r['suffix_2char'] for r in data['records'] if r['prefix_2char'] == 'ko']
print(f'ko- suffixes: {ko_suffixes}')

# Check if po- tokens show any ordering
print()
print('=== po- Token Positions ===')
po_tokens = [(i, r['folio_id'], r['token']) for i, r in enumerate(data['records']) if r['prefix_2char'] == 'po']
for pos, folio, token in po_tokens:
    print(f'  {folio}: {token}')

# Check if there's any pattern in how prefixes distribute across recto/verso
print()
print('=== Recto vs Verso ===')
recto = [r for r in data['records'] if r['folio_id'].endswith('r')]
verso = [r for r in data['records'] if r['folio_id'].endswith('v')]

from collections import Counter
recto_prefixes = Counter(r['prefix_2char'] for r in recto)
verso_prefixes = Counter(r['prefix_2char'] for r in verso)

print('Recto top prefixes:', dict(recto_prefixes.most_common(5)))
print('Verso top prefixes:', dict(verso_prefixes.most_common(5)))

# Check if there's any alphabetic/numeric ordering in remainders
print()
print('=== Remainder Analysis ===')
remainders = [(r['folio_id'], r['hyp_remainder']) for r in data['records'] if r['prefix_2char'] == 'ko']
print('ko- remainders:', remainders)
