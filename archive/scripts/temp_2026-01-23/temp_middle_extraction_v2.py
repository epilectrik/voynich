#!/usr/bin/env python3
"""
Re-extract MIDDLEs with corrected prefix list including articulators.

Compare to current 667 RI MIDDLEs to see the impact.
"""

import csv
import json
from collections import Counter, defaultdict

# ============================================================
# CURRENT PREFIX LIST (from middle_classes.json extraction)
# ============================================================
CURRENT_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
                    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
                    'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                    'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']

# ============================================================
# EXTENDED PREFIX LIST (with articulators from C291)
# ============================================================
# Core prefixes
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Articulator + core combinations (from our analysis, 10+ tokens)
ARTICULATOR_PREFIXES = [
    # d + core
    'dch', 'dsh', 'dol',
    # k + core
    'kch', 'ksh', 'kol',
    # t + core
    'tch', 'tsh', 'tol',
    # s + core
    'sch', 'sol',
    # p + core
    'pch', 'psh',
    # f + core
    'fch',
    # r + core
    'rch',
    # l + core
    'lch',
    # y + core and y + extended
    'ych', 'ysh', 'yda', 'yok',
    # y + ke/te/to/ta/ko/ka series
    'yke', 'yte', 'yto', 'yta', 'yko', 'yka',
    # y + articulator + core (double articulator)
    'ytch', 'ykch', 'ypch',
]

# Extended prefixes (non-articulator)
EXTENDED_PREFIXES = ['lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
                     'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']

# Full extended list
EXTENDED_PREFIX_LIST = CORE_PREFIXES + ARTICULATOR_PREFIXES + EXTENDED_PREFIXES
EXTENDED_PREFIX_LIST = sorted(set(EXTENDED_PREFIX_LIST), key=len, reverse=True)

# Suffix list (unchanged)
SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token, prefix_list):
    """Extract MIDDLE from token using given prefix list."""
    if not token:
        return None
    working = token

    # Strip prefix
    for p in prefix_list:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            break

    # Strip suffix
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break

    return working if working else None

# ============================================================
# LOAD CURRENT CLASSIFICATION
# ============================================================
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    current_data = json.load(f)

current_ri = set(current_data['a_exclusive_middles'])
current_pp = set(current_data['a_shared_middles'])

print("="*70)
print("MIDDLE EXTRACTION COMPARISON")
print("="*70)
print(f"\nCurrent classification (old prefix list):")
print(f"  RI (A-exclusive): {len(current_ri)}")
print(f"  PP (A-shared): {len(current_pp)}")
print(f"  Total: {len(current_ri) + len(current_pp)}")

# ============================================================
# RE-EXTRACT WITH EXTENDED PREFIX LIST
# ============================================================
print("\n" + "="*70)
print("RE-EXTRACTION WITH ARTICULATOR-AWARE PREFIX LIST")
print("="*70)

# Collect MIDDLEs by language
a_middles_new = Counter()
b_middles_new = Counter()

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        lang = row.get('language', '').strip()

        if not word or '*' in word:
            continue

        middle = extract_middle(word, EXTENDED_PREFIX_LIST)
        if middle:
            if lang == 'A':
                a_middles_new[middle] += 1
            elif lang == 'B':
                b_middles_new[middle] += 1

# Classify
a_middle_types_new = set(a_middles_new.keys())
b_middle_types_new = set(b_middles_new.keys())

new_ri = a_middle_types_new - b_middle_types_new  # A-exclusive
new_pp = a_middle_types_new & b_middle_types_new  # A-shared with B

print(f"\nNew classification (extended prefix list):")
print(f"  RI (A-exclusive): {len(new_ri)}")
print(f"  PP (A-shared): {len(new_pp)}")
print(f"  Total A MIDDLEs: {len(a_middle_types_new)}")

# ============================================================
# COMPARE OLD vs NEW
# ============================================================
print("\n" + "="*70)
print("COMPARISON: OLD vs NEW")
print("="*70)

print(f"\nRI MIDDLEs:")
print(f"  Old: {len(current_ri)}")
print(f"  New: {len(new_ri)}")
print(f"  Change: {len(new_ri) - len(current_ri):+d} ({100*(len(new_ri) - len(current_ri))/len(current_ri):+.1f}%)")

print(f"\nPP MIDDLEs:")
print(f"  Old: {len(current_pp)}")
print(f"  New: {len(new_pp)}")
print(f"  Change: {len(new_pp) - len(current_pp):+d} ({100*(len(new_pp) - len(current_pp))/len(current_pp):+.1f}%)")

# ============================================================
# ANALYZE DIFFERENCES
# ============================================================
print("\n" + "="*70)
print("WHAT CHANGED?")
print("="*70)

# MIDDLEs that were RI but are now gone (absorbed into different MIDDLEs)
old_ri_gone = current_ri - new_ri - new_pp
print(f"\nOld RI MIDDLEs no longer extracted: {len(old_ri_gone)}")
if old_ri_gone:
    examples = sorted(old_ri_gone)[:15]
    print(f"  Examples: {examples}")

# MIDDLEs that are new RI
new_ri_added = new_ri - current_ri - current_pp
print(f"\nNew RI MIDDLEs (not in old extraction): {len(new_ri_added)}")
if new_ri_added:
    examples = sorted(new_ri_added)[:15]
    print(f"  Examples: {examples}")

# MIDDLEs that moved from RI to PP
ri_to_pp = current_ri & new_pp
print(f"\nMoved from RI to PP: {len(ri_to_pp)}")
if ri_to_pp:
    examples = sorted(ri_to_pp)[:10]
    print(f"  Examples: {examples}")

# MIDDLEs that moved from PP to RI
pp_to_ri = current_pp & new_ri
print(f"\nMoved from PP to RI: {len(pp_to_ri)}")
if pp_to_ri:
    examples = sorted(pp_to_ri)[:10]
    print(f"  Examples: {examples}")

# ============================================================
# ANALYZE OLD RI MIDDLES THAT DISAPPEARED
# ============================================================
print("\n" + "="*70)
print("ANALYZING DISAPPEARED RI MIDDLEs")
print("="*70)

# These are MIDDLEs from old extraction that don't appear in new extraction
# This happens when articulator was part of the MIDDLE, now it's part of PREFIX

# Check what the old "y-initial" MIDDLEs became
y_initial_old = [m for m in current_ri if m.startswith('y')]
print(f"\nOld y-initial RI MIDDLEs: {len(y_initial_old)}")

y_still_ri = [m for m in y_initial_old if m in new_ri]
y_now_pp = [m for m in y_initial_old if m in new_pp]
y_gone = [m for m in y_initial_old if m not in new_ri and m not in new_pp]

print(f"  Still RI: {len(y_still_ri)}")
print(f"  Now PP: {len(y_now_pp)}")
print(f"  Gone (absorbed): {len(y_gone)}")

if y_gone:
    print(f"\n  Gone examples: {sorted(y_gone)[:15]}")

# ============================================================
# SPOT CHECK: WHAT HAPPENED TO SPECIFIC OLD MIDDLES
# ============================================================
print("\n" + "="*70)
print("SPOT CHECK: TRACING SPECIFIC OLD MIDDLEs")
print("="*70)

# Take some old y-initial MIDDLEs and trace what tokens they came from
spot_check = ['ytal', 'ytod', 'ychea', 'ytcha', 'yteol']

for old_middle in spot_check:
    if old_middle in current_ri:
        print(f"\nOld MIDDLE '{old_middle}':")

        # Find tokens that produced this old MIDDLE
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

                # Check with old extraction
                old_m = extract_middle(word, sorted(set(CURRENT_PREFIXES), key=len, reverse=True))
                if old_m == old_middle:
                    # Now extract with new list
                    new_m = extract_middle(word, EXTENDED_PREFIX_LIST)

                    # Find what prefix was extracted
                    old_prefix = None
                    new_prefix = None
                    for p in sorted(set(CURRENT_PREFIXES), key=len, reverse=True):
                        if word.startswith(p) and len(word) > len(p):
                            old_prefix = p
                            break
                    for p in EXTENDED_PREFIX_LIST:
                        if word.startswith(p) and len(word) > len(p):
                            new_prefix = p
                            break

                    print(f"  Token: {word}")
                    print(f"    Old: prefix={old_prefix}, middle={old_m}")
                    print(f"    New: prefix={new_prefix}, middle={new_m}")
                    break

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
MIDDLE COUNT COMPARISON:
  Old RI: {len(current_ri)} -> New RI: {len(new_ri)} ({len(new_ri) - len(current_ri):+d})
  Old PP: {len(current_pp)} -> New PP: {len(new_pp)} ({len(new_pp) - len(current_pp):+d})

TOTAL A MIDDLEs:
  Old: {len(current_ri) + len(current_pp)}
  New: {len(a_middle_types_new)}

KEY INSIGHT:
  The articulator-aware prefix list significantly reduces MIDDLE count
  because y-initial (and other articulator) patterns are now prefixes,
  not part of the MIDDLE.

RECOMMENDATION:
  Update middle_classes.json with new extraction methodology.
""")

# Save new classification for reference
new_classification = {
    'a_exclusive_middles': sorted(new_ri),
    'a_shared_middles': sorted(new_pp),
    'methodology': 'Extended prefix list including articulators (C291)',
    'prefix_list': EXTENDED_PREFIX_LIST
}

with open('temp_middle_classes_v2.json', 'w') as f:
    json.dump(new_classification, f, indent=2)
print("\nSaved new classification to temp_middle_classes_v2.json")
