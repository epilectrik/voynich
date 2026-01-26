#!/usr/bin/env python3
"""
Explore: Could SUFFIX encode product type?

Medieval pharmacy product categories (Brunschwig era):
- Waters (aquae) - distilled waters
- Oils (olea) - essential oils
- Powders (pulveres)
- Syrups (syrupi)
- Spirits/quintessences

Voynich suffixes:
- y, dy, edy, eedy, ey, aiy (the -y family)
- am, an (the -n family)
- ar, al, or, ol (the -l/-r family)
- od, os (other)

Questions:
1. Do certain suffixes co-occur with certain PP profiles?
2. Do suffix distributions vary by folio/section?
3. Is suffix independent of MIDDLE choice?
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load classifications
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

# Group suffixes by family
SUFFIX_FAMILIES = {
    'Y_FAMILY': ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy'],
    'N_FAMILY': ['am', 'an'],
    'L_FAMILY': ['al', 'ol'],
    'R_FAMILY': ['ar', 'or'],
    'OTHER': ['od', 'os']
}

def extract_parts(token):
    if not token:
        return None, None, None
    prefix = None
    suffix = None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break
    return prefix, token if token else None, suffix

def get_suffix_family(suffix):
    if not suffix:
        return 'NONE'
    for family, members in SUFFIX_FAMILIES.items():
        if suffix in members:
            return family
    return 'UNKNOWN'

# Collect data
suffix_counts = Counter()
suffix_family_counts = Counter()
suffix_by_middle_type = {'RI': Counter(), 'PP': Counter()}
suffix_by_prefix = defaultdict(Counter)
middle_suffix_pairs = defaultdict(Counter)  # middle -> suffix counts

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)

        if suffix:
            suffix_counts[suffix] += 1
            suffix_family_counts[get_suffix_family(suffix)] += 1

            if middle:
                if middle in ri_middles:
                    suffix_by_middle_type['RI'][suffix] += 1
                elif middle in pp_middles:
                    suffix_by_middle_type['PP'][suffix] += 1

                middle_suffix_pairs[middle][suffix] += 1

            if prefix:
                suffix_by_prefix[prefix][suffix] += 1

print("="*70)
print("SUFFIX DISTRIBUTION IN CURRIER A")
print("="*70)

print("\nBy individual suffix:")
total = sum(suffix_counts.values())
for suffix, count in suffix_counts.most_common():
    print(f"  -{suffix}: {count} ({100*count/total:.1f}%)")

print("\nBy suffix family:")
for family, count in suffix_family_counts.most_common():
    print(f"  {family}: {count} ({100*count/total:.1f}%)")

print("\n" + "="*70)
print("SUFFIX BY MIDDLE TYPE (RI vs PP)")
print("="*70)

ri_total = sum(suffix_by_middle_type['RI'].values())
pp_total = sum(suffix_by_middle_type['PP'].values())

print(f"\nRI tokens with suffix: {ri_total}")
print(f"PP tokens with suffix: {pp_total}")

print("\nSuffix distribution comparison:")
print(f"{'Suffix':<10} {'RI %':>10} {'PP %':>10} {'Diff':>10}")
print("-"*40)

all_suffixes = set(suffix_by_middle_type['RI'].keys()) | set(suffix_by_middle_type['PP'].keys())
for suffix in sorted(all_suffixes, key=lambda s: -suffix_counts.get(s, 0)):
    ri_pct = 100 * suffix_by_middle_type['RI'].get(suffix, 0) / ri_total if ri_total else 0
    pp_pct = 100 * suffix_by_middle_type['PP'].get(suffix, 0) / pp_total if pp_total else 0
    diff = ri_pct - pp_pct
    if abs(diff) > 5:  # Notable difference
        print(f"  -{suffix:<8} {ri_pct:>9.1f}% {pp_pct:>9.1f}% {diff:>+9.1f}%  ***")
    else:
        print(f"  -{suffix:<8} {ri_pct:>9.1f}% {pp_pct:>9.1f}% {diff:>+9.1f}%")

print("\n" + "="*70)
print("DO SAME MIDDLEs USE MULTIPLE SUFFIXES?")
print("="*70)

# Check if MIDDLEs vary their suffix choice
middles_with_multiple_suffixes = {m: suffixes for m, suffixes in middle_suffix_pairs.items()
                                   if len(suffixes) > 1 and sum(suffixes.values()) >= 3}

print(f"\nMIDDLEs with 3+ tokens and multiple suffixes: {len(middles_with_multiple_suffixes)}")
print(f"Total MIDDLEs with suffix: {len(middle_suffix_pairs)}")

if middles_with_multiple_suffixes:
    print("\nExamples (same MIDDLE, different suffixes):")
    for middle, suffixes in sorted(middles_with_multiple_suffixes.items(),
                                    key=lambda x: -sum(x[1].values()))[:15]:
        suffix_str = ", ".join(f"-{s}:{c}" for s, c in suffixes.most_common())
        middle_type = "RI" if middle in ri_middles else "PP" if middle in pp_middles else "?"
        print(f"  {middle} ({middle_type}): {suffix_str}")

print("\n" + "="*70)
print("SUFFIX-PREFIX CORRELATION")
print("="*70)

# Do certain prefixes prefer certain suffix families?
print("\nSuffix family distribution by prefix:")
print(f"{'PREFIX':<8} {'Y_FAM':>8} {'N_FAM':>8} {'L_FAM':>8} {'R_FAM':>8} {'NONE':>8}")
print("-"*50)

for prefix in ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'd', 'o', 's']:
    if prefix not in suffix_by_prefix:
        continue
    total_pfx = sum(suffix_by_prefix[prefix].values())
    if total_pfx < 20:
        continue

    y_pct = sum(suffix_by_prefix[prefix].get(s, 0) for s in SUFFIX_FAMILIES['Y_FAMILY']) / total_pfx * 100
    n_pct = sum(suffix_by_prefix[prefix].get(s, 0) for s in SUFFIX_FAMILIES['N_FAMILY']) / total_pfx * 100
    l_pct = sum(suffix_by_prefix[prefix].get(s, 0) for s in SUFFIX_FAMILIES['L_FAMILY']) / total_pfx * 100
    r_pct = sum(suffix_by_prefix[prefix].get(s, 0) for s in SUFFIX_FAMILIES['R_FAMILY']) / total_pfx * 100

    # Count tokens without suffix for this prefix
    # (would need separate tracking - skip for now)

    print(f"  {prefix:<6} {y_pct:>7.1f}% {n_pct:>7.1f}% {l_pct:>7.1f}% {r_pct:>7.1f}%")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If SUFFIX = product type:
  - Same MIDDLE + different SUFFIX = different products from same material
  - "rose water" vs "rose oil" = same MIDDLE, different suffix
  - SUFFIX should be partially independent of MIDDLE choice
  - Suffix families might map to: waters, oils, powders, spirits...

Key questions:
  1. Do MIDDLEs vary their suffix? (YES = product variation possible)
  2. Is suffix distribution similar across RI vs PP? (tells us if it's grammar or semantic)
  3. Do suffixes correlate with procedures (PP profile)?
""")
