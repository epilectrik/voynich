#!/usr/bin/env python3
"""
If PREFIX/SUFFIX have global roles, they should behave consistently
across different MIDDLEs.

Check:
1. Do certain prefixes always appear in certain line positions?
2. Do certain suffixes correlate with certain contexts?
3. Is the PREFIX/SUFFIX system independent of MIDDLE choice?
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

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

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

# Collect data with position info
prefix_by_position = defaultdict(Counter)  # position -> prefix counts
suffix_by_position = defaultdict(Counter)
prefix_by_middle = defaultdict(Counter)    # middle -> prefix counts
suffix_by_middle = defaultdict(Counter)
prefix_overall = Counter()
suffix_overall = Counter()

# Track word position in line
line_words = defaultdict(list)  # (folio, line) -> list of words

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        line = row.get('line', '').strip()

        if not word or '*' in word:
            continue

        line_words[(folio, line)].append(word)

# Now process with position info
for (folio, line), words in line_words.items():
    for pos, word in enumerate(words):
        prefix, middle, suffix = extract_parts(word)

        if middle and middle in ri_middles:
            # Normalize position: first, middle, last
            if pos == 0:
                pos_cat = 'first'
            elif pos == len(words) - 1:
                pos_cat = 'last'
            else:
                pos_cat = 'middle'

            if prefix:
                prefix_by_position[pos_cat][prefix] += 1
                prefix_by_middle[middle][prefix] += 1
                prefix_overall[prefix] += 1

            if suffix:
                suffix_by_position[pos_cat][suffix] += 1
                suffix_by_middle[middle][suffix] += 1
                suffix_overall[suffix] += 1

print("="*70)
print("PREFIX DISTRIBUTION BY LINE POSITION")
print("="*70)

for pos in ['first', 'middle', 'last']:
    total = sum(prefix_by_position[pos].values())
    if total == 0:
        continue
    print(f"\n{pos.upper()} position ({total} RI tokens with prefix):")
    for prefix, count in prefix_by_position[pos].most_common(10):
        pct = 100 * count / total
        overall_pct = 100 * prefix_overall[prefix] / sum(prefix_overall.values())
        diff = pct - overall_pct
        print(f"  {prefix}: {pct:.1f}% (overall: {overall_pct:.1f}%, diff: {diff:+.1f}%)")

print("\n" + "="*70)
print("SUFFIX DISTRIBUTION BY LINE POSITION")
print("="*70)

for pos in ['first', 'middle', 'last']:
    total = sum(suffix_by_position[pos].values())
    if total == 0:
        continue
    print(f"\n{pos.upper()} position ({total} RI tokens with suffix):")
    for suffix, count in suffix_by_position[pos].most_common(10):
        pct = 100 * count / total
        overall_pct = 100 * suffix_overall[suffix] / sum(suffix_overall.values())
        diff = pct - overall_pct
        print(f"  {suffix}: {pct:.1f}% (overall: {overall_pct:.1f}%, diff: {diff:+.1f}%)")

print("\n" + "="*70)
print("DO DIFFERENT MIDDLES USE SAME PREFIX/SUFFIX PATTERNS?")
print("="*70)

# Check if prefix distribution is similar across MIDDLEs
# Pick a few common MIDDLEs and compare their prefix distributions
common_middles = [m for m, prefixes in prefix_by_middle.items()
                  if sum(prefixes.values()) >= 5]

print(f"\nMIDDLEs with 5+ prefixed tokens: {len(common_middles)}")

if common_middles:
    print("\nPrefix distribution for common MIDDLEs:")
    for middle in sorted(common_middles)[:10]:
        total = sum(prefix_by_middle[middle].values())
        top_prefixes = prefix_by_middle[middle].most_common(3)
        prefix_str = ", ".join(f"{p}:{100*c/total:.0f}%" for p, c in top_prefixes)
        print(f"  {middle}: {prefix_str}")

# Check if same prefix appears with many different MIDDLEs
print("\n" + "="*70)
print("PREFIX VERSATILITY (how many MIDDLEs use each prefix)")
print("="*70)

prefix_middles = defaultdict(set)
for middle, prefixes in prefix_by_middle.items():
    for prefix in prefixes:
        prefix_middles[prefix].add(middle)

for prefix in sorted(prefix_middles.keys(), key=lambda x: -len(prefix_middles[x])):
    count = len(prefix_middles[prefix])
    print(f"  {prefix}: used with {count} different MIDDLEs")

print("\n" + "="*70)
print("SUFFIX VERSATILITY")
print("="*70)

suffix_middles = defaultdict(set)
for middle, suffixes in suffix_by_middle.items():
    for suffix in suffixes:
        suffix_middles[suffix].add(middle)

for suffix in sorted(suffix_middles.keys(), key=lambda x: -len(suffix_middles[x])):
    count = len(suffix_middles[suffix])
    print(f"  {suffix}: used with {count} different MIDDLEs")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If PREFIX/SUFFIX have global grammatical roles:
  - Same prefix should appear with MANY different MIDDLEs
  - Prefix distribution should be similar regardless of MIDDLE
  - Position in line might influence prefix choice

If PREFIX/SUFFIX are MIDDLE-specific:
  - Each MIDDLE would have its own preferred prefixes
  - Little overlap in prefix usage across MIDDLEs
""")
