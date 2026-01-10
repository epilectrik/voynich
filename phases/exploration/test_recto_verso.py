#!/usr/bin/env python
"""Test recto/verso pattern significance."""
from scipy import stats
import json

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

records = data['records']

# Split by recto/verso
recto = [r for r in records if r['folio_id'].endswith('r')]
verso = [r for r in records if r['folio_id'].endswith('v')]

# C+vowel prefixes
c_vowel = {'ko', 'po', 'to', 'fo', 'ka', 'ta', 'pa', 'fa'}

recto_cvowel = sum(1 for r in recto if r['prefix_2char'] in c_vowel)
verso_cvowel = sum(1 for r in verso if r['prefix_2char'] in c_vowel)

recto_other = len(recto) - recto_cvowel
verso_other = len(verso) - verso_cvowel

print('=== Recto vs Verso C+vowel Analysis ===')
print(f'Recto: {recto_cvowel}/{len(recto)} C+vowel = {100*recto_cvowel/len(recto):.1f}%')
print(f'Verso: {verso_cvowel}/{len(verso)} C+vowel = {100*verso_cvowel/len(verso):.1f}%')

contingency = [[recto_cvowel, recto_other], [verso_cvowel, verso_other]]
odds_ratio, p = stats.fisher_exact(contingency)

print(f'Fisher exact: odds_ratio={odds_ratio:.2f}, p={p:.4f}')
if p < 0.05:
    print('--> SIGNIFICANT: C+vowel prefixes prefer verso pages')
else:
    print('--> Not significant')

# Also check ko- specifically
print()
print('=== ko- by page side ===')
ko_recto = sum(1 for r in recto if r['prefix_2char'] == 'ko')
ko_verso = sum(1 for r in verso if r['prefix_2char'] == 'ko')
print(f'ko- on recto: {ko_recto}')
print(f'ko- on verso: {ko_verso}')
