#!/usr/bin/env python3
"""
Maybe suffix encodes grammatical ROLE rather than product TYPE?

-dy (RI-preferred) vs -ol/-or (PP-preferred)

Check:
1. Line position preferences
2. Do -dy tokens behave differently (first token? nominative?)
3. Does suffix correlate with the "naming" vs "processing" function?
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

# Collect line data with positions
line_tokens = defaultdict(list)

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

        prefix, middle, suffix = extract_parts(word)
        middle_type = 'RI' if middle in ri_middles else 'PP' if middle in pp_middles else None

        line_tokens[(folio, line)].append({
            'word': word,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'middle_type': middle_type
        })

# Analyze position preferences by suffix
suffix_positions = defaultdict(Counter)  # suffix -> position counts
suffix_first_token = Counter()  # how often suffix appears on first token
suffix_last_token = Counter()
suffix_total = Counter()

for key, tokens in line_tokens.items():
    n = len(tokens)
    for i, tok in enumerate(tokens):
        suffix = tok['suffix']
        if not suffix:
            continue

        suffix_total[suffix] += 1

        # Position categories
        if i == 0:
            suffix_positions[suffix]['FIRST'] += 1
            suffix_first_token[suffix] += 1
        elif i == n - 1:
            suffix_positions[suffix]['LAST'] += 1
            suffix_last_token[suffix] += 1
        else:
            suffix_positions[suffix]['MIDDLE'] += 1

print("="*70)
print("SUFFIX BY LINE POSITION")
print("="*70)

print("\nPosition distribution (FIRST / MIDDLE / LAST):")
print(f"{'Suffix':<8} {'Total':>8} {'FIRST':>10} {'MIDDLE':>10} {'LAST':>10}")
print("-"*50)

for suffix in ['y', 'dy', 'ol', 'or', 'ey', 'ar', 'al', 'am']:
    total = suffix_total[suffix]
    if total < 50:
        continue
    first_pct = 100 * suffix_positions[suffix]['FIRST'] / total
    mid_pct = 100 * suffix_positions[suffix]['MIDDLE'] / total
    last_pct = 100 * suffix_positions[suffix]['LAST'] / total
    print(f"  -{suffix:<6} {total:>7} {first_pct:>9.1f}% {mid_pct:>9.1f}% {last_pct:>9.1f}%")

# Check: when RI token has suffix, what position is it in?
print("\n" + "="*70)
print("RI TOKENS WITH SUFFIX: POSITION ANALYSIS")
print("="*70)

ri_suffix_pos = defaultdict(Counter)
pp_suffix_pos = defaultdict(Counter)

for key, tokens in line_tokens.items():
    n = len(tokens)
    for i, tok in enumerate(tokens):
        suffix = tok['suffix']
        mtype = tok['middle_type']
        if not suffix or not mtype:
            continue

        if i == 0:
            pos = 'FIRST'
        elif i == n - 1:
            pos = 'LAST'
        else:
            pos = 'MIDDLE'

        if mtype == 'RI':
            ri_suffix_pos[suffix][pos] += 1
        else:
            pp_suffix_pos[suffix][pos] += 1

print("\nRI vs PP position distribution for common suffixes:")
for suffix in ['dy', 'y', 'ol', 'or']:
    ri_total = sum(ri_suffix_pos[suffix].values())
    pp_total = sum(pp_suffix_pos[suffix].values())

    if ri_total < 5 or pp_total < 50:
        continue

    print(f"\n  -{suffix}:")
    print(f"    RI (n={ri_total}): ", end="")
    for pos in ['FIRST', 'MIDDLE', 'LAST']:
        pct = 100 * ri_suffix_pos[suffix][pos] / ri_total if ri_total else 0
        print(f"{pos}={pct:.0f}% ", end="")
    print()

    print(f"    PP (n={pp_total}): ", end="")
    for pos in ['FIRST', 'MIDDLE', 'LAST']:
        pct = 100 * pp_suffix_pos[suffix][pos] / pp_total if pp_total else 0
        print(f"{pos}={pct:.0f}% ", end="")
    print()

# Check: does -dy appear more in "naming" contexts (first position)?
print("\n" + "="*70)
print("FIRST-POSITION SUFFIX ENRICHMENT")
print("="*70)

baseline_first = sum(suffix_first_token.values()) / sum(suffix_total.values())
print(f"\nBaseline: {100*baseline_first:.1f}% of all suffixed tokens are first-position")

print("\nEnrichment by suffix:")
for suffix in sorted(suffix_total.keys(), key=lambda s: -suffix_total[s]):
    if suffix_total[suffix] < 50:
        continue
    first_rate = suffix_first_token[suffix] / suffix_total[suffix]
    enrichment = first_rate / baseline_first
    marker = "**" if enrichment > 1.3 or enrichment < 0.7 else ""
    print(f"  -{suffix}: {100*first_rate:.1f}% first-position ({enrichment:.2f}x baseline) {marker}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If -dy = nominative/reference form:
  - Should appear more at line-start (naming the material)
  - RI + -dy = "this is material X"

If -ol/-or = processed forms:
  - Should appear more in middle/end (result of processing)
  - PP + -ol = "resulting in X-water/oil"
""")
