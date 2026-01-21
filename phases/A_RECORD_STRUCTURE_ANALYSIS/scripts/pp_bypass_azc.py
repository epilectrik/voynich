#!/usr/bin/env python3
"""Examine the 114 PP MIDDLEs that bypass AZC (appear in A+B but not AZC)."""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

def extract_middle(token):
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None
    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
    if middle == '':
        middle = '_EMPTY_'
    return middle

# Load middle classes
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

pp_middles = set(mc['a_shared_middles'])

# AZC check
def is_azc_folio(folio):
    f = folio.lower()
    return any(f.startswith(x) for x in ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73'])

# Collect data
pp_data = defaultdict(lambda: {
    'a_count': 0, 'b_count': 0, 'azc_count': 0,
    'a_folios': set(), 'b_folios': set(), 'azc_folios': set(),
    'a_prefixes': Counter(), 'b_prefixes': Counter(),
    'a_suffixes': Counter(), 'b_suffixes': Counter()
})

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '') != 'H':
            continue

        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        lang = row.get('language', '')

        if not word or '*' in word:
            continue

        # Extract components
        prefix = None
        for p in ALL_PREFIXES:
            if word.startswith(p):
                prefix = p
                break
        if not prefix:
            continue

        middle = extract_middle(word)
        if not middle or middle not in pp_middles:
            continue

        remainder = word[len(prefix):]
        suffix = ''
        for s in SUFFIXES:
            if remainder.endswith(s):
                suffix = s
                break

        if lang == 'A':
            pp_data[middle]['a_count'] += 1
            pp_data[middle]['a_folios'].add(folio)
            pp_data[middle]['a_prefixes'][prefix] += 1
            pp_data[middle]['a_suffixes'][suffix] += 1
        elif lang == 'B':
            pp_data[middle]['b_count'] += 1
            pp_data[middle]['b_folios'].add(folio)
            pp_data[middle]['b_prefixes'][prefix] += 1
            pp_data[middle]['b_suffixes'][suffix] += 1

        if is_azc_folio(folio):
            pp_data[middle]['azc_count'] += 1
            pp_data[middle]['azc_folios'].add(folio)

# Find bypass MIDDLEs (in A and B but not AZC)
bypass_middles = []
for m, data in pp_data.items():
    if data['a_count'] > 0 and data['b_count'] > 0 and data['azc_count'] == 0:
        bypass_middles.append((m, data))

print("=" * 70)
print(f"PP MIDDLEs THAT BYPASS AZC: {len(bypass_middles)}")
print("=" * 70)
print()

# Sort by total frequency
bypass_middles.sort(key=lambda x: x[1]['a_count'] + x[1]['b_count'], reverse=True)

print("BY TOTAL FREQUENCY (A+B):")
print()
print(f"{'MIDDLE':<12} {'A':>5} {'B':>5} {'A fol':>6} {'B fol':>6} {'Top A PREFIX':<10} {'Top B PREFIX':<10}")
print("-" * 70)

for m, data in bypass_middles[:40]:
    a_prefix = data['a_prefixes'].most_common(1)[0][0] if data['a_prefixes'] else '-'
    b_prefix = data['b_prefixes'].most_common(1)[0][0] if data['b_prefixes'] else '-'
    print(f"{m:<12} {data['a_count']:>5} {data['b_count']:>5} {len(data['a_folios']):>6} {len(data['b_folios']):>6} {a_prefix:<10} {b_prefix:<10}")

print()

# Analyze patterns
print("=" * 70)
print("PATTERN ANALYSIS")
print("=" * 70)
print()

# Length distribution
lengths = [len(m) for m, _ in bypass_middles]
print(f"MIDDLE length: mean={sum(lengths)/len(lengths):.1f}, range={min(lengths)}-{max(lengths)}")
print()

# Length breakdown
print("By length:")
for l in sorted(set(lengths)):
    count = sum(1 for m, _ in bypass_middles if len(m) == l)
    examples = [m for m, _ in bypass_middles if len(m) == l][:5]
    print(f"  {l} chars: {count} MIDDLEs - {', '.join(examples)}")
print()

# Common substrings/patterns
print("Common patterns:")
patterns = Counter()
for m, _ in bypass_middles:
    if 'ch' in m: patterns['contains ch'] += 1
    if 'ck' in m: patterns['contains ck'] += 1
    if 'ph' in m: patterns['contains ph'] += 1
    if 'th' in m: patterns['contains th'] += 1
    if m.startswith('c'): patterns['starts with c'] += 1
    if m.endswith('o'): patterns['ends with o'] += 1
    if m.endswith('e'): patterns['ends with e'] += 1
    if 'ee' in m: patterns['contains ee'] += 1

for pat, count in patterns.most_common(10):
    print(f"  {pat}: {count} ({100*count/len(bypass_middles):.1f}%)")
print()

# PREFIX distribution in A vs B
print("PREFIX distribution for bypass MIDDLEs:")
a_prefixes_total = Counter()
b_prefixes_total = Counter()
for m, data in bypass_middles:
    a_prefixes_total.update(data['a_prefixes'])
    b_prefixes_total.update(data['b_prefixes'])

print(f"{'PREFIX':<8} {'A tokens':>10} {'B tokens':>10}")
print("-" * 30)
all_prefixes_here = set(a_prefixes_total.keys()) | set(b_prefixes_total.keys())
for p in sorted(all_prefixes_here, key=lambda x: a_prefixes_total[x] + b_prefixes_total[x], reverse=True)[:10]:
    print(f"{p:<8} {a_prefixes_total[p]:>10} {b_prefixes_total[p]:>10}")
print()

# B-heavy vs A-heavy
print("A vs B balance:")
a_heavy = [(m, d) for m, d in bypass_middles if d['a_count'] > d['b_count'] * 2]
b_heavy = [(m, d) for m, d in bypass_middles if d['b_count'] > d['a_count'] * 2]
balanced = [(m, d) for m, d in bypass_middles if m not in [x[0] for x in a_heavy + b_heavy]]

print(f"  A-heavy (A > 2*B): {len(a_heavy)}")
print(f"  B-heavy (B > 2*A): {len(b_heavy)}")
print(f"  Balanced: {len(balanced)}")
print()

if b_heavy:
    print("B-HEAVY bypass MIDDLEs (more common in B than A):")
    for m, d in sorted(b_heavy, key=lambda x: x[1]['b_count'], reverse=True)[:15]:
        print(f"  {m:<12} A={d['a_count']:>3}, B={d['b_count']:>4}")
