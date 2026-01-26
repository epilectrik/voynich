#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path('.')

with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token:
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

ri_used = set()
ri_to_folios = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue
        middle = extract_middle(word)
        if middle and middle in ri_middles:
            ri_used.add(middle)
            ri_to_folios[middle].add(folio)

# Count localized RI (1-2 folios)
local_ri = [ri for ri, folios in ri_to_folios.items() if len(folios) <= 2]
single_folio_ri = [ri for ri, folios in ri_to_folios.items() if len(folios) == 1]

print(f'Total RI MIDDLEs defined: {len(ri_middles)}')
print(f'Unique RI MIDDLEs used in Currier A: {len(ri_used)}')
print(f'Local RI (1-2 folios only): {len(local_ri)}')
print(f'Strictly local (1 folio only): {len(single_folio_ri)}')

# How many Currier A folios?
a_folios = set()
with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() == 'A':
            a_folios.add(row.get('folio', '').strip())

print(f'\nCurrier A folios: {len(a_folios)}')
print(f'Currier B folios: 83')
