#!/usr/bin/env python
"""Check for token and prefix repetition patterns."""
import json
from collections import Counter

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

tokens = [r['token'] for r in data['records']]
folio_token = [(r['folio_id'], r['token']) for r in data['records']]

# Find all repeated tokens
token_counts = Counter(tokens)
repeated = {t: c for t, c in token_counts.items() if c > 1}

print('=== Repeated First Tokens ===')
if repeated:
    for token, count in repeated.items():
        folios = [f for f, t in folio_token if t == token]
        print(f'{token}: {count}x at folios {folios}')
else:
    print('No repeated tokens')

print()
print(f'Total unique: {len(set(tokens))}/{len(tokens)}')
print(f'Uniqueness rate: {100*len(set(tokens))/len(tokens):.1f}%')

# Check if PREFIXES repeat in patterns
print()
print('=== Prefix Repetition by Folio ===')
prefixes = [r['prefix_2char'] for r in data['records']]
prefix_counts = Counter(prefixes)
print('Prefix frequencies:')
for p, c in prefix_counts.most_common():
    folios = [r['folio_id'] for r in data['records'] if r['prefix_2char'] == p]
    print(f'  {p}: {c}x - {folios}')

# Check for suffix repetition
print()
print('=== Suffix Repetition ===')
suffixes = [r['suffix_2char'] for r in data['records']]
suffix_counts = Counter(suffixes)
for s, c in suffix_counts.most_common(5):
    print(f'  -{s}: {c}x')

# Check if any prefix appears on consecutive folios
print()
print('=== Consecutive Folio Same-Prefix ===')
records = data['records']
for i in range(len(records) - 1):
    if records[i]['prefix_2char'] == records[i+1]['prefix_2char']:
        print(f'  {records[i]["folio_id"]}-{records[i+1]["folio_id"]}: {records[i]["prefix_2char"]} ({records[i]["token"]}, {records[i+1]["token"]})')
