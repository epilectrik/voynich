#!/usr/bin/env python3
"""Check RI tokens per line distribution."""

import csv
import json
from collections import defaultdict, Counter

# Load RI middles
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# Count RI tokens per line
lines = defaultdict(list)
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        line = row.get('line_number', '').strip()
        language = row.get('language', '').strip()

        if language != 'A' or not word:
            continue
        if word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        line_key = f'{folio}.{line}'
        middle = get_middle(word)
        is_ri = middle in ri_middles
        lines[line_key].append({'middle': middle, 'is_ri': is_ri})

# Count RI per line
ri_counts = Counter()
for line_key, tokens in lines.items():
    ri_count = sum(1 for t in tokens if t['is_ri'])
    ri_counts[ri_count] += 1

print('RI tokens per line distribution:')
print()
for count in sorted(ri_counts.keys()):
    n = ri_counts[count]
    pct = 100 * n / len(lines)
    bar = '#' * int(pct / 2)
    print(f'  {count:2d} RI tokens: {n:4d} lines ({pct:5.1f}%) {bar}')

print()
print(f'Lines with 0 RI: {ri_counts[0]} ({100*ri_counts[0]/len(lines):.1f}%)')
print(f'Lines with 1+ RI: {len(lines) - ri_counts[0]} ({100*(len(lines)-ri_counts[0])/len(lines):.1f}%)')
