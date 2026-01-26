#!/usr/bin/env python3
"""
How does the corrected RI count affect line-level statistics?

Questions:
1. What % of Currier A lines contain RI tokens?
2. How many RI tokens per line?
3. How does this compare to old 349 methodology?
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load our definitive results
with open(PROJECT_ROOT / 'temp_ri_definitive_results.json', 'r') as f:
    results = json.load(f)

ri_middles = set(results['ri_middles'])
pp_middles = set(results['pp_middles'])

print(f"Loaded: {len(ri_middles)} RI MIDDLEs, {len(pp_middles)} PP MIDDLEs")

# Also load old middle_classes.json for comparison
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    old_data = json.load(f)

old_ri = set(old_data['a_exclusive_middles'])
old_pp = set(old_data['a_shared_middles'])

print(f"Old methodology: {len(old_ri)} RI, {len(old_pp)} PP")

# Extraction function (same as definitive test)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token):
    if not token:
        return None
    working = token
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None

def extract_middle_old(token):
    """Old methodology - requires PREFIX, keeps SUFFIX."""
    if not token:
        return None
    for p in PREFIXES:
        if token.startswith(p):
            return token[len(p):]  # Keep suffix attached
    return None  # No prefix = no middle

# Process Currier A lines
lines = defaultdict(list)  # (folio, line) -> list of tokens

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        line = row.get('line_number', '').strip()

        if not word or '*' in word:
            continue

        lines[(folio, line)].append(word)

print(f"\nTotal Currier A lines: {len(lines)}")

# Analyze each line with NEW methodology
new_lines_with_ri = 0
new_ri_per_line = []
new_lines_pure_ri = 0
new_lines_pure_pp = 0
new_lines_mixed = 0

# Analyze each line with OLD methodology
old_lines_with_ri = 0
old_ri_per_line = []

for (folio, line_num), tokens in lines.items():
    # NEW methodology
    middles_new = [extract_middle(t) for t in tokens]
    middles_new = [m for m in middles_new if m]

    ri_count_new = sum(1 for m in middles_new if m in ri_middles)
    pp_count_new = sum(1 for m in middles_new if m in pp_middles)

    if ri_count_new > 0:
        new_lines_with_ri += 1
        new_ri_per_line.append(ri_count_new)

    if ri_count_new > 0 and pp_count_new == 0:
        new_lines_pure_ri += 1
    elif pp_count_new > 0 and ri_count_new == 0:
        new_lines_pure_pp += 1
    elif ri_count_new > 0 and pp_count_new > 0:
        new_lines_mixed += 1

    # OLD methodology
    middles_old = [extract_middle_old(t) for t in tokens]
    middles_old = [m for m in middles_old if m]

    ri_count_old = sum(1 for m in middles_old if m in old_ri)

    if ri_count_old > 0:
        old_lines_with_ri += 1
        old_ri_per_line.append(ri_count_old)

print("\n" + "="*70)
print("LINE-LEVEL RI PRESENCE")
print("="*70)

print(f"\nNEW methodology (667 RI MIDDLEs, PREFIX optional):")
print(f"  Lines with RI: {new_lines_with_ri}/{len(lines)} ({100*new_lines_with_ri/len(lines):.1f}%)")
print(f"  Avg RI tokens per RI-containing line: {sum(new_ri_per_line)/len(new_ri_per_line):.2f}")
print(f"  Max RI tokens in a line: {max(new_ri_per_line)}")

print(f"\nOLD methodology (349 RI MIDDLEs, PREFIX required):")
print(f"  Lines with RI: {old_lines_with_ri}/{len(lines)} ({100*old_lines_with_ri/len(lines):.1f}%)")
if old_ri_per_line:
    print(f"  Avg RI tokens per RI-containing line: {sum(old_ri_per_line)/len(old_ri_per_line):.2f}")
    print(f"  Max RI tokens in a line: {max(old_ri_per_line)}")

print("\n" + "="*70)
print("LINE COMPOSITION (NEW methodology)")
print("="*70)

print(f"\n  Pure RI (only RI tokens): {new_lines_pure_ri} ({100*new_lines_pure_ri/len(lines):.1f}%)")
print(f"  Pure PP (only PP tokens): {new_lines_pure_pp} ({100*new_lines_pure_pp/len(lines):.1f}%)")
print(f"  Mixed (both RI and PP): {new_lines_mixed} ({100*new_lines_mixed/len(lines):.1f}%)")
print(f"  Neither: {len(lines) - new_lines_pure_ri - new_lines_pure_pp - new_lines_mixed}")

# Distribution of RI counts per line
print("\n" + "="*70)
print("RI TOKENS PER LINE DISTRIBUTION (NEW)")
print("="*70)

ri_count_dist = Counter(new_ri_per_line)
for count in sorted(ri_count_dist.keys()):
    n = ri_count_dist[count]
    pct = 100 * n / len(new_ri_per_line)
    bar = '#' * int(pct / 2)
    print(f"  {count} RI tokens: {n:4d} lines ({pct:5.1f}%) {bar}")

# Token-level breakdown
print("\n" + "="*70)
print("TOKEN-LEVEL BREAKDOWN")
print("="*70)

total_tokens = sum(len(tokens) for tokens in lines.values())
total_ri_tokens = sum(new_ri_per_line)
total_pp_tokens = sum(
    sum(1 for m in [extract_middle(t) for t in tokens] if m and m in pp_middles)
    for tokens in lines.values()
)

print(f"\n  Total A tokens: {total_tokens}")
print(f"  RI tokens: {total_ri_tokens} ({100*total_ri_tokens/total_tokens:.1f}%)")
print(f"  PP tokens: {total_pp_tokens} ({100*total_pp_tokens/total_tokens:.1f}%)")
print(f"  Other/unclassified: {total_tokens - total_ri_tokens - total_pp_tokens}")
