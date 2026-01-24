#!/usr/bin/env python3
"""
Analyze RI MIDDLEs that REPEAT - where and how?
"""

import json
import sys
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None

# Load PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load A tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

# Identify RI tokens
df_ri = df_a[df_a['middle'].apply(lambda m: m is not None and m not in pp_middles)].copy()

print("="*70)
print("RI MIDDLE REPETITION ANALYSIS")
print("="*70)

# Get RI MIDDLEs that repeat
ri_middle_counts = df_ri['middle'].value_counts()
repeating = ri_middle_counts[ri_middle_counts > 1]

print(f"\nTotal unique RI MIDDLEs: {len(ri_middle_counts)}")
print(f"RI MIDDLEs that repeat (2+): {len(repeating)} ({100*len(repeating)/len(ri_middle_counts):.1f}%)")
print(f"Total tokens from repeating MIDDLEs: {repeating.sum()}")

# For each repeating MIDDLE, check: same folio or different folios?
print("\n" + "="*70)
print("WHERE DO REPEATING RI MIDDLEs APPEAR?")
print("="*70)

same_folio_repeats = 0
cross_folio_repeats = 0
mixed_repeats = 0

repeat_details = []

for middle, count in repeating.items():
    occurrences = df_ri[df_ri['middle'] == middle]
    folios = occurrences['folio'].unique()
    lines = occurrences.apply(lambda r: f"{r['folio']}:{r['line_number']}", axis=1).tolist()

    if len(folios) == 1:
        same_folio_repeats += 1
        location = "SAME_FOLIO"
    elif len(folios) == count:
        cross_folio_repeats += 1
        location = "CROSS_FOLIO"
    else:
        mixed_repeats += 1
        location = "MIXED"

    repeat_details.append({
        'middle': middle,
        'count': count,
        'folios': len(folios),
        'location': location,
        'records': lines
    })

print(f"\nRepetition patterns:")
print(f"  Same folio only: {same_folio_repeats} ({100*same_folio_repeats/len(repeating):.1f}%)")
print(f"  Cross-folio (each in different folio): {cross_folio_repeats} ({100*cross_folio_repeats/len(repeating):.1f}%)")
print(f"  Mixed (some same, some different): {mixed_repeats} ({100*mixed_repeats/len(repeating):.1f}%)")

# Show the most repeated ones
print("\n" + "="*70)
print("MOST FREQUENTLY REPEATING RI MIDDLEs")
print("="*70)

repeat_details.sort(key=lambda x: -x['count'])

print(f"\n{'MIDDLE':>12} {'Count':>6} {'Folios':>7} {'Pattern':>12} Records")
print("-" * 80)

for rd in repeat_details[:30]:
    records_str = ', '.join(rd['records'][:5])
    if len(rd['records']) > 5:
        records_str += f"... (+{len(rd['records'])-5})"
    print(f"{rd['middle']:>12} {rd['count']:>6} {rd['folios']:>7} {rd['location']:>12} {records_str}")

# Deep dive: cross-folio repeats (same RI in different folios)
print("\n" + "="*70)
print("CROSS-FOLIO REPEATS (same RI MIDDLE in different folios)")
print("="*70)

cross_folio = [rd for rd in repeat_details if rd['location'] == 'CROSS_FOLIO']
print(f"\nRI MIDDLEs appearing in multiple folios (1 per folio): {len(cross_folio)}")

if cross_folio:
    print(f"\n{'MIDDLE':>12} {'Folios':>7} Folio list")
    print("-" * 60)
    for rd in cross_folio[:20]:
        folios = list(set(r.split(':')[0] for r in rd['records']))
        print(f"{rd['middle']:>12} {rd['folios']:>7} {', '.join(sorted(folios)[:8])}")

# Check: are cross-folio repeats short (like PP) or long (like typical RI)?
print("\n" + "="*70)
print("LENGTH COMPARISON: REPEATING vs SINGLETON RI")
print("="*70)

singleton_middles = ri_middle_counts[ri_middle_counts == 1].index
repeating_middles = ri_middle_counts[ri_middle_counts > 1].index

singleton_lengths = [len(m) for m in singleton_middles]
repeating_lengths = [len(m) for m in repeating_middles]

print(f"\nSingleton RI MIDDLEs (appear once):")
print(f"  Count: {len(singleton_lengths)}")
print(f"  Mean length: {sum(singleton_lengths)/len(singleton_lengths):.2f} chars")

print(f"\nRepeating RI MIDDLEs (appear 2+):")
print(f"  Count: {len(repeating_lengths)}")
print(f"  Mean length: {sum(repeating_lengths)/len(repeating_lengths):.2f} chars")

# Length distribution of repeaters
print(f"\nRepeating RI by length:")
repeat_by_len = Counter(len(m) for m in repeating_middles)
for length in sorted(repeat_by_len.keys()):
    print(f"  Length {length}: {repeat_by_len[length]} MIDDLEs")

# The very short repeaters - are they actually RI or misclassified?
print("\n" + "="*70)
print("SHORT REPEATING RI (length 1-2) - POSSIBLE BOUNDARY CASES")
print("="*70)

short_repeaters = [rd for rd in repeat_details if len(rd['middle']) <= 2]
print(f"\nShort repeating RI MIDDLEs: {len(short_repeaters)}")

for rd in short_repeaters[:15]:
    folios = list(set(r.split(':')[0] for r in rd['records']))
    print(f"  '{rd['middle']}': {rd['count']}x across {len(folios)} folios - {folios[:5]}")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if cross_folio_repeats > same_folio_repeats:
    print("""
CROSS-FOLIO REPETITION DOMINANT.

The repeating RI MIDDLEs tend to appear across different folios,
suggesting they may be:
- Shared reference points (same material referenced in multiple programs)
- Common categories that span folios
- Possible misclassification (should some be PP?)
""")
else:
    print("""
SAME-FOLIO REPETITION DOMINANT.

The repeating RI MIDDLEs tend to repeat within the same folio,
suggesting:
- Local reuse (same identifier referenced multiple times in one folio)
- Batch-internal repetition (same material used in multiple steps)
- Not cross-references between folios
""")

if sum(repeating_lengths)/len(repeating_lengths) < 3:
    print("""
NOTE: Repeating RI MIDDLEs are SHORTER than singletons.

This could indicate:
- Short MIDDLEs are more likely to be shared/reused
- Possible boundary with PP vocabulary (short = shared)
- Length correlates with specificity (long = unique, short = reusable)
""")
