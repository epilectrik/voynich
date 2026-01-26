#!/usr/bin/env python3
"""
Sanity check: Are we over-stripping with the extended prefix list?

Check for:
1. Single-letter MIDDLEs (suspicious)
2. MIDDLEs that are themselves suffixes
3. MIDDLE length distribution comparison
"""

import csv
import json
from collections import Counter

# Current prefix list
CURRENT_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
                    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
                    'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                    'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
CURRENT_PREFIXES = sorted(set(CURRENT_PREFIXES), key=len, reverse=True)

# Extended prefix list with articulators
EXTENDED_PREFIXES = CURRENT_PREFIXES + [
    'dch', 'dsh', 'dol', 'kch', 'ksh', 'kol', 'tch', 'tsh', 'tol',
    'sch', 'sol', 'pch', 'psh', 'fch', 'rch', 'lch',
    'ych', 'ysh', 'yda', 'yok', 'yke', 'yte', 'yto', 'yta', 'yko', 'yka',
    'ytch', 'ykch', 'ypch'
]
EXTENDED_PREFIXES = sorted(set(EXTENDED_PREFIXES), key=len, reverse=True)

# Suffix list
SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)
SUFFIX_SET = set(SUFFIXES)

def extract_full(token, prefix_list):
    """Extract prefix, middle, suffix from token."""
    if not token:
        return None, None, None

    working = token
    prefix = None
    suffix = None

    # Strip prefix
    for p in prefix_list:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break

    # Strip suffix
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break

    return prefix, working if working else None, suffix

# Collect extractions
old_extractions = []
new_extractions = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        old_p, old_m, old_s = extract_full(word, CURRENT_PREFIXES)
        new_p, new_m, new_s = extract_full(word, EXTENDED_PREFIXES)

        old_extractions.append({'token': word, 'prefix': old_p, 'middle': old_m, 'suffix': old_s})
        new_extractions.append({'token': word, 'prefix': new_p, 'middle': new_m, 'suffix': new_s})

print("="*70)
print("EXTRACTION SANITY CHECK")
print("="*70)

# ============================================================
# 1. MIDDLE LENGTH DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("1. MIDDLE LENGTH DISTRIBUTION")
print("="*70)

old_lengths = Counter(len(e['middle']) for e in old_extractions if e['middle'])
new_lengths = Counter(len(e['middle']) for e in new_extractions if e['middle'])

print("\nOLD extraction MIDDLE lengths:")
for length in sorted(old_lengths.keys()):
    cnt = old_lengths[length]
    pct = 100 * cnt / sum(old_lengths.values())
    bar = '#' * int(pct)
    print(f"  len={length}: {cnt:5d} ({pct:5.1f}%) {bar}")

print("\nNEW extraction MIDDLE lengths:")
for length in sorted(new_lengths.keys()):
    cnt = new_lengths[length]
    pct = 100 * cnt / sum(new_lengths.values())
    bar = '#' * int(pct)
    print(f"  len={length}: {cnt:5d} ({pct:5.1f}%) {bar}")

# ============================================================
# 2. SINGLE-LETTER MIDDLES
# ============================================================
print("\n" + "="*70)
print("2. SINGLE-LETTER MIDDLEs (SUSPICIOUS)")
print("="*70)

old_single = [e for e in old_extractions if e['middle'] and len(e['middle']) == 1]
new_single = [e for e in new_extractions if e['middle'] and len(e['middle']) == 1]

print(f"\nOLD extraction single-letter MIDDLEs: {len(old_single)}")
print(f"NEW extraction single-letter MIDDLEs: {len(new_single)}")

if new_single:
    single_middles = Counter(e['middle'] for e in new_single)
    print(f"\nNew single-letter MIDDLE distribution:")
    for m, cnt in single_middles.most_common():
        print(f"  '{m}': {cnt}")

    print(f"\nExamples of single-letter MIDDLE tokens:")
    for e in new_single[:15]:
        print(f"  {e['token']} -> prefix={e['prefix']}, middle={e['middle']}, suffix={e['suffix']}")

# ============================================================
# 3. MIDDLES THAT ARE THEMSELVES SUFFIXES
# ============================================================
print("\n" + "="*70)
print("3. MIDDLEs THAT ARE ALSO SUFFIXES")
print("="*70)

old_suffix_middles = [e for e in old_extractions if e['middle'] and e['middle'] in SUFFIX_SET]
new_suffix_middles = [e for e in new_extractions if e['middle'] and e['middle'] in SUFFIX_SET]

print(f"\nOLD extraction MIDDLEs that are suffixes: {len(old_suffix_middles)}")
print(f"NEW extraction MIDDLEs that are suffixes: {len(new_suffix_middles)}")

if new_suffix_middles:
    suffix_as_middle = Counter(e['middle'] for e in new_suffix_middles)
    print(f"\nNew suffix-as-MIDDLE distribution:")
    for m, cnt in suffix_as_middle.most_common(10):
        print(f"  '{m}': {cnt}")

    print(f"\nExamples:")
    for e in new_suffix_middles[:10]:
        print(f"  {e['token']} -> prefix={e['prefix']}, middle={e['middle']}, suffix={e['suffix']}")

# ============================================================
# 4. CHECK SPECIFIC PROBLEMATIC CASES
# ============================================================
print("\n" + "="*70)
print("4. PROBLEMATIC CASE ANALYSIS")
print("="*70)

# The tokens from our spot check
problem_tokens = ['ytalar', 'ytod', 'ycheas', 'ytchas', 'yteoldy']

for token in problem_tokens:
    old_p, old_m, old_s = extract_full(token, CURRENT_PREFIXES)
    new_p, new_m, new_s = extract_full(token, EXTENDED_PREFIXES)

    print(f"\n{token}:")
    print(f"  OLD: prefix={old_p}, middle={old_m}, suffix={old_s}")
    print(f"  NEW: prefix={new_p}, middle={new_m}, suffix={new_s}")

    # Is the new MIDDLE a suffix?
    if new_m and new_m in SUFFIX_SET:
        print(f"  WARNING: New MIDDLE '{new_m}' is itself a suffix!")

# ============================================================
# 5. ARE THESE REALLY PREFIX+MIDDLE OR JUST LONG PREFIXES?
# ============================================================
print("\n" + "="*70)
print("5. ALTERNATIVE INTERPRETATION")
print("="*70)

print("""
If 'ytalar' becomes prefix=yta, middle=l, suffix=ar...
And 'l' is suspicious as a MIDDLE...

Maybe 'ytal' is a UNIT (prefix+middle fused) rather than:
  - yta (prefix) + l (middle) + ar (suffix)

The original extraction treated 'ytal' as the MIDDLE, which may be correct.
The articulator 'y-' might not be separable from the rest.
""")

# Check: do the "articulator prefixes" ever appear with normal-length middles?
print("\nChecking articulator prefix usage patterns:")

articulator_prefixes = ['ych', 'ysh', 'yda', 'yok', 'yke', 'yte', 'yto', 'yta', 'yko', 'yka', 'ytch', 'ykch', 'ypch']

for ap in articulator_prefixes[:5]:
    tokens_with_ap = [e for e in new_extractions if e['prefix'] == ap]
    if tokens_with_ap:
        middle_lengths = [len(e['middle']) for e in tokens_with_ap if e['middle']]
        avg_len = sum(middle_lengths) / len(middle_lengths) if middle_lengths else 0
        print(f"\n  {ap}: {len(tokens_with_ap)} tokens, avg MIDDLE length: {avg_len:.1f}")

        # Show length distribution
        len_dist = Counter(middle_lengths)
        for length, cnt in sorted(len_dist.items()):
            print(f"    len={length}: {cnt}")

        # Examples
        examples = [e for e in tokens_with_ap if e['middle']][:3]
        for e in examples:
            print(f"    e.g., {e['token']} -> middle={e['middle']}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
SANITY CHECK RESULTS:

Single-letter MIDDLEs:
  OLD: {len(old_single)}
  NEW: {len(new_single)}

MIDDLEs that are suffixes:
  OLD: {len(old_suffix_middles)}
  NEW: {len(new_suffix_middles)}

CONCLUSION:
""")

if len(new_single) > len(old_single) * 2:
    print("  WARNING: Extended prefix list creates many more single-letter MIDDLEs")
    print("  This suggests we may be OVER-PARSING with articulator prefixes")
    print("  The original extraction may be more correct")
else:
    print("  Single-letter MIDDLE count is reasonable")

if len(new_suffix_middles) > len(old_suffix_middles) * 1.5:
    print("  WARNING: Extended prefix list creates MIDDLEs that are just suffixes")
    print("  This is a sign of incorrect parsing")
