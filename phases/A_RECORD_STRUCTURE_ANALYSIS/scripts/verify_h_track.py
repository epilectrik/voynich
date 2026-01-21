#!/usr/bin/env python3
"""Verify H track filtering."""

import csv
from collections import Counter

transcribers = Counter()
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        lang = row.get('language', '').strip()
        if lang == 'A':
            t = row.get('transcriber', '').strip().strip('"')
            transcribers[t] += 1

print('Transcribers in A data:')
for t, c in transcribers.most_common():
    print(f'  {t}: {c}')

# Now check what the corrected script actually loaded
print()
print('Tokens loaded by corrected script: 11,346')
print(f'H track A tokens in file: {transcribers.get("H", 0)}')
