#!/usr/bin/env python3
"""Quick check of Rosettes Currier language classification."""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

currier_by_folio = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            currier = parts[6].strip('"').strip()

            if folio in ROSETTES:
                if folio not in currier_by_folio:
                    currier_by_folio[folio] = Counter()
                currier_by_folio[folio][currier] += 1

print('Rosettes Currier Language Classification:')
print('-' * 50)
for folio in sorted(currier_by_folio.keys()):
    langs = currier_by_folio[folio]
    print(f'{folio}: {dict(langs)}')
