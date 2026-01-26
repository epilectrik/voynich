#!/usr/bin/env python3
"""
Check if distributed RI have different structure from localized RI.

User mentioned "2 categories like long and short" - maybe:
1. RI that are JUST PP atoms (distributed, categorical)
2. RI that are PP + extension (localized, specific)
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

print("="*70)
print("RI STRUCTURE ANALYSIS")
print("="*70)

# Hypothesis: RI = PP_atom + extension
# Check if localized RI have longer extensions than distributed RI

def find_longest_pp_prefix(ri):
    """Find the longest PP atom that the RI starts with."""
    for length in range(len(ri), 0, -1):
        prefix = ri[:length]
        if prefix in pp_middles:
            return prefix, ri[length:]  # pp_atom, extension
    return None, ri

def find_longest_pp_contained(ri):
    """Find the longest PP atom contained in RI."""
    best = None
    best_pos = -1
    for pp in pp_middles:
        if pp in ri and len(pp) >= 2:
            if best is None or len(pp) > len(best):
                best = pp
                best_pos = ri.find(pp)
    if best:
        before = ri[:best_pos]
        after = ri[best_pos + len(best):]
        return before, best, after
    return None, None, ri

print("\nRI decomposition (prefix-based):")
print("-" * 50)

# Check all RI
decompositions = []
for ri in ri_middles:
    pp_prefix, extension = find_longest_pp_prefix(ri)
    decompositions.append({
        'ri': ri,
        'pp_prefix': pp_prefix,
        'extension': extension,
        'has_pp_prefix': pp_prefix is not None,
        'extension_len': len(extension) if extension else 0
    })

# Statistics
has_pp_prefix = sum(1 for d in decompositions if d['has_pp_prefix'])
print(f"RI with PP prefix: {has_pp_prefix}/{len(decompositions)} ({100*has_pp_prefix/len(decompositions):.1f}%)")

# Distribution of extension lengths
ext_lengths = [d['extension_len'] for d in decompositions if d['has_pp_prefix']]
if ext_lengths:
    from collections import Counter
    length_dist = Counter(ext_lengths)
    print(f"\nExtension length distribution (for RI with PP prefix):")
    for length in sorted(length_dist.keys()):
        count = length_dist[length]
        pct = 100 * count / len(ext_lengths)
        print(f"  Length {length}: {count} ({pct:.0f}%)")

# Check if zero-extension RI are more distributed
print("\n" + "="*70)
print("ZERO-EXTENSION RI (just PP atom)")
print("="*70)

zero_ext = [d for d in decompositions if d['has_pp_prefix'] and d['extension_len'] == 0]
print(f"\nRI that are JUST a PP atom (zero extension): {len(zero_ext)}")
for d in sorted(zero_ext, key=lambda x: x['ri'])[:15]:
    print(f"  {d['ri']} = PP '{d['pp_prefix']}' + nothing")

# Check short-extension RI
print("\n" + "="*70)
print("SHORT-EXTENSION RI (PP + 1-2 chars)")
print("="*70)

short_ext = [d for d in decompositions if d['has_pp_prefix'] and 1 <= d['extension_len'] <= 2]
print(f"\nRI with short extension (1-2 chars): {len(short_ext)}")
for d in sorted(short_ext, key=lambda x: x['ri'])[:15]:
    print(f"  {d['ri']} = PP '{d['pp_prefix']}' + '{d['extension']}'")

# Check long-extension RI
print("\n" + "="*70)
print("LONG-EXTENSION RI (PP + 3+ chars)")
print("="*70)

long_ext = [d for d in decompositions if d['has_pp_prefix'] and d['extension_len'] >= 3]
print(f"\nRI with long extension (3+ chars): {len(long_ext)}")
for d in sorted(long_ext, key=lambda x: x['ri'])[:15]:
    print(f"  {d['ri']} = PP '{d['pp_prefix']}' + '{d['extension']}'")

# The key question: Do extension lengths correlate with folio distribution?
print("\n" + "="*70)
print("EXTENSION LENGTH vs FOLIO DISTRIBUTION")
print("="*70)

# Need folio data
import csv

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
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

ri_to_folios = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        folio = row.get('folio', '').strip()
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        middle = extract_middle(word)
        if middle and middle in ri_middles:
            ri_to_folios[middle].add(folio)

# Compute average folio count by extension length
import statistics

for ext_len_group, label in [(0, "Zero ext"), (1, "1 char"), (2, "2 chars"), (3, "3+ chars")]:
    if ext_len_group == 3:
        items = [d for d in decompositions if d['has_pp_prefix'] and d['extension_len'] >= 3]
    else:
        items = [d for d in decompositions if d['has_pp_prefix'] and d['extension_len'] == ext_len_group]

    if items:
        folio_counts = [len(ri_to_folios.get(d['ri'], set())) for d in items]
        valid_counts = [c for c in folio_counts if c > 0]
        if valid_counts:
            avg = statistics.mean(valid_counts)
            med = statistics.median(valid_counts)
            print(f"  {label} extension: {len(items)} RI, avg={avg:.1f} folios, median={med}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
If zero-extension RI (RI = just PP atom) are more distributed,
this suggests:

1. CATEGORICAL RI: Just the PP atom
   - Example: 'ho' = PP 'ho' (if ho is actually a PP)
   - Used across many folios as a category marker

2. SPECIFIC RI: PP + extension
   - Example: 'holdar' = PP 'ho' + 'ldar' (specific material)
   - Used on 1-2 folios where that material is discussed

This would explain:
- Why most RI are localized (they have specific extensions)
- Why a few RI are widespread (they're just PP/category markers)
""")
