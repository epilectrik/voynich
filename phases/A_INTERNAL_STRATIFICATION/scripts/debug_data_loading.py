#!/usr/bin/env python3
"""Debug data loading to find the discrepancy."""

import csv
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

print("=" * 70)
print("DEBUG: Comparing data loading methods")
print("=" * 70)

# Method 1: csv.DictReader (verification script)
print("\n1. Using csv.DictReader...")
dict_reader_lines = defaultdict(list)
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    print(f"   Columns: {reader.fieldnames}")
    for row in reader:
        if row.get('transcriber') != 'H':
            continue
        if row.get('language') != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue
        folio = row.get('folio', '')
        line_num = row.get('line_number', '')
        dict_reader_lines[(folio, line_num)].append(word)

print(f"   Unique (folio, line_number) pairs: {len(dict_reader_lines)}")

# Method 2: Raw line splitting (prep script style)
print("\n2. Using raw line splitting (prep script style)...")

raw_split_lines = defaultdict(list)
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    header = f.readline().strip().split('\t')
    print(f"   Header: {header}")
    print(f"   Index 0: {header[0]}, Index 1: {header[1]}, Index 2: {header[2]}")

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 13:
            continue

        transcriber = parts[12].strip('"').strip()
        if transcriber != 'H':
            continue

        word = parts[0].strip('"').strip().lower()
        folio = parts[1].strip('"').strip()
        line_num = parts[2].strip('"').strip()
        lang = parts[6].strip('"').strip()

        if lang != 'A':
            continue
        if not word or '*' in word:
            continue

        raw_split_lines[(folio, line_num)].append(word)

print(f"   Unique (folio, line_num) pairs: {len(raw_split_lines)}")

# Sample comparison
print("\n3. Sample entries comparison...")
print("\n   First 5 from DictReader:")
for i, ((folio, line), tokens) in enumerate(list(dict_reader_lines.items())[:5]):
    print(f"     ({folio}, {line}): {len(tokens)} tokens - {tokens[:3]}...")

print("\n   First 5 from raw split:")
for i, ((folio, line), tokens) in enumerate(list(raw_split_lines.items())[:5]):
    print(f"     ({folio}, {line}): {len(tokens)} tokens - {tokens[:3]}...")

# Check for key differences
print("\n4. Finding discrepancies...")
dict_keys = set(dict_reader_lines.keys())
raw_keys = set(raw_split_lines.keys())

only_in_dict = dict_keys - raw_keys
only_in_raw = raw_keys - dict_keys

print(f"   Keys only in DictReader: {len(only_in_dict)}")
print(f"   Keys only in raw split: {len(only_in_raw)}")

if only_in_dict:
    print(f"   Examples from DictReader only: {list(only_in_dict)[:5]}")
if only_in_raw:
    print(f"   Examples from raw split only: {list(only_in_raw)[:5]}")

# Check what the prep script is ACTUALLY producing
print("\n5. Checking prep script entry keys...")
import json
RESULTS_DIR = Path(__file__).parent.parent / 'results'
with open(RESULTS_DIR / 'entry_data.json') as f:
    prep_entries = json.load(f)

prep_keys = set((e['folio'], e['line']) for e in prep_entries)
print(f"   Prep script unique (folio, line) keys: {len(prep_keys)}")

# Sample prep keys
print("\n   Sample prep script keys:")
for key in list(prep_keys)[:10]:
    print(f"     {key}")
