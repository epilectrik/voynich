#!/usr/bin/env python3
"""
Trace PP MIDDLE propagation through A → AZC → B pipeline.

Questions:
1. How many PP MIDDLEs reach AZC? Which ones?
2. How do they distribute across AZC folios/zones?
3. How do they propagate to B?
4. Can we cluster them by propagation pattern?
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Morphology parsing (same as prepare_middle_classes.py)
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
ri_middles = set(mc['a_exclusive_middles'])

print("=" * 70)
print("PP MIDDLE PROPAGATION ANALYSIS")
print("=" * 70)
print()
print(f"PP MIDDLEs to trace: {len(pp_middles)}")
print()

# AZC folios
AZC_FOLIOS = ['f67r', 'f67v', 'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
              'f69r', 'f69v1', 'f69v2', 'f70r1', 'f70r2', 'f70v1', 'f70v2',
              'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
              'f73r', 'f73v']

# Simplified AZC folio check
def is_azc_folio(folio):
    f = folio.lower()
    return any(f.startswith(x) for x in ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73'])

# Collect data from transcript
pp_in_a = defaultdict(lambda: {'folios': set(), 'count': 0})
pp_in_azc = defaultdict(lambda: {'folios': set(), 'count': 0})
pp_in_b = defaultdict(lambda: {'folios': set(), 'count': 0})

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

        middle = extract_middle(word)
        if not middle or middle not in pp_middles:
            continue

        if lang == 'A':
            pp_in_a[middle]['folios'].add(folio)
            pp_in_a[middle]['count'] += 1
        elif lang == 'B':
            pp_in_b[middle]['folios'].add(folio)
            pp_in_b[middle]['count'] += 1

        # Check AZC (can overlap with A or be unlabeled)
        if is_azc_folio(folio):
            pp_in_azc[middle]['folios'].add(folio)
            pp_in_azc[middle]['count'] += 1

print("=" * 70)
print("CORPUS PRESENCE")
print("=" * 70)
print()

pp_in_a_set = set(pp_in_a.keys())
pp_in_azc_set = set(pp_in_azc.keys())
pp_in_b_set = set(pp_in_b.keys())

print(f"PP MIDDLEs in A: {len(pp_in_a_set)} ({100*len(pp_in_a_set)/len(pp_middles):.1f}%)")
print(f"PP MIDDLEs in AZC: {len(pp_in_azc_set)} ({100*len(pp_in_azc_set)/len(pp_middles):.1f}%)")
print(f"PP MIDDLEs in B: {len(pp_in_b_set)} ({100*len(pp_in_b_set)/len(pp_middles):.1f}%)")
print()

# Venn diagram logic
only_a = pp_in_a_set - pp_in_azc_set - pp_in_b_set
a_and_azc = pp_in_a_set & pp_in_azc_set - pp_in_b_set
a_and_b = pp_in_a_set & pp_in_b_set - pp_in_azc_set
all_three = pp_in_a_set & pp_in_azc_set & pp_in_b_set
azc_and_b = pp_in_azc_set & pp_in_b_set - pp_in_a_set

print("PROPAGATION PATTERNS:")
print(f"  A only (no AZC, no B): {len(only_a)}")
print(f"  A + AZC (no B): {len(a_and_azc)}")
print(f"  A + B (no AZC): {len(a_and_b)}")
print(f"  A + AZC + B: {len(all_three)}")
print()

# The A+B no AZC is interesting - these bypass AZC?
if a_and_b:
    print("PP MIDDLEs in A+B but NOT in AZC folios:")
    for m in sorted(a_and_b)[:15]:
        print(f"  {m}: A={pp_in_a[m]['count']}, B={pp_in_b[m]['count']}")
    print()

print("=" * 70)
print("AZC FOLIO DISTRIBUTION")
print("=" * 70)
print()

# Classify by AZC spread
azc_spread = {}
for m in pp_middles:
    if m in pp_in_azc:
        azc_spread[m] = len(pp_in_azc[m]['folios'])
    else:
        azc_spread[m] = 0

restricted = [m for m, s in azc_spread.items() if 1 <= s <= 2]
moderate = [m for m, s in azc_spread.items() if 3 <= s <= 10]
universal = [m for m, s in azc_spread.items() if s > 10]
no_azc = [m for m, s in azc_spread.items() if s == 0]

print(f"No AZC presence: {len(no_azc)} ({100*len(no_azc)/len(pp_middles):.1f}%)")
print(f"Restricted (1-2 AZC folios): {len(restricted)} ({100*len(restricted)/len(pp_middles):.1f}%)")
print(f"Moderate (3-10 AZC folios): {len(moderate)} ({100*len(moderate)/len(pp_middles):.1f}%)")
print(f"Universal (10+ AZC folios): {len(universal)} ({100*len(universal)/len(pp_middles):.1f}%)")
print()

# Show universals
if universal:
    print("UNIVERSAL PP MIDDLEs (10+ AZC folios):")
    for m in sorted(universal, key=lambda x: azc_spread[x], reverse=True)[:15]:
        a_count = pp_in_a[m]['count'] if m in pp_in_a else 0
        b_count = pp_in_b[m]['count'] if m in pp_in_b else 0
        print(f"  {m:<10} AZC={azc_spread[m]:>2} folios, A={a_count:>4}, B={b_count:>4}")
    print()

print("=" * 70)
print("B FOLIO DISTRIBUTION BY AZC CATEGORY")
print("=" * 70)
print()

def mean_b_spread(middle_list):
    spreads = [len(pp_in_b[m]['folios']) for m in middle_list if m in pp_in_b]
    return sum(spreads) / len(spreads) if spreads else 0

print(f"Mean B folio spread:")
print(f"  No AZC presence: {mean_b_spread(no_azc):.1f} folios")
print(f"  Restricted (1-2 AZC): {mean_b_spread(restricted):.1f} folios")
print(f"  Moderate (3-10 AZC): {mean_b_spread(moderate):.1f} folios")
print(f"  Universal (10+ AZC): {mean_b_spread(universal):.1f} folios")
print()

print("=" * 70)
print("ROLE CLUSTERING BY PROPAGATION")
print("=" * 70)
print()

# Cluster by (AZC presence, B presence, frequency tier)
def freq_tier(m):
    a_count = pp_in_a[m]['count'] if m in pp_in_a else 0
    if a_count >= 50:
        return 'high'
    elif a_count >= 5:
        return 'mid'
    else:
        return 'low'

clusters = defaultdict(list)
for m in pp_middles:
    has_azc = m in pp_in_azc_set
    has_b = m in pp_in_b_set
    tier = freq_tier(m)
    key = (has_azc, has_b, tier)
    clusters[key].append(m)

print(f"{'AZC':<5} {'B':<5} {'Freq':<6} {'Count':>6} {'Examples'}")
print("-" * 60)
for key in sorted(clusters.keys(), key=lambda x: -len(clusters[x])):
    has_azc, has_b, tier = key
    examples = ', '.join(sorted(clusters[key])[:3])
    print(f"{str(has_azc):<5} {str(has_b):<5} {tier:<6} {len(clusters[key]):>6}   {examples}")
print()

# Save detailed results
results = {
    'summary': {
        'total_pp_middles': len(pp_middles),
        'in_a': len(pp_in_a_set),
        'in_azc': len(pp_in_azc_set),
        'in_b': len(pp_in_b_set),
        'all_three': len(all_three)
    },
    'azc_categories': {
        'no_azc': len(no_azc),
        'restricted': len(restricted),
        'moderate': len(moderate),
        'universal': len(universal)
    },
    'mean_b_spread': {
        'no_azc': mean_b_spread(no_azc),
        'restricted': mean_b_spread(restricted),
        'moderate': mean_b_spread(moderate),
        'universal': mean_b_spread(universal)
    },
    'universal_middles': sorted(universal, key=lambda x: -azc_spread[x]),
    'propagation_patterns': {
        'a_only': len(only_a),
        'a_and_azc': len(a_and_azc),
        'a_and_b_no_azc': len(a_and_b),
        'all_three': len(all_three)
    }
}

with open('phases/A_RECORD_STRUCTURE_ANALYSIS/results/pp_middle_propagation.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Results saved to phases/A_RECORD_STRUCTURE_ANALYSIS/results/pp_middle_propagation.json")
