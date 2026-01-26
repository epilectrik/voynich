#!/usr/bin/env python3
"""
Do different suffixes correlate with different PP profiles (procedures)?

If suffix = product type:
  - Waters need gentle heat (low fire degree)
  - Oils need more aggressive processing
  - Different suffix families should show different PP co-occurrence
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load classifications
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

SUFFIX_FAMILIES = {
    'Y_SIMPLE': ['y'],
    'Y_EXTENDED': ['dy', 'edy', 'eedy', 'ey', 'aiy'],
    'L_FAMILY': ['al', 'ol'],
    'R_FAMILY': ['ar', 'or'],
    'N_FAMILY': ['am', 'an'],
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

# Collect: for each line, what suffix family appears with what PP atoms?
line_data = defaultdict(lambda: {'suffixes': set(), 'pp_atoms': set()})

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
        key = (folio, line)

        if suffix:
            line_data[key]['suffixes'].add(suffix)

        if middle and middle in pp_middles:
            line_data[key]['pp_atoms'].add(middle)

# For each suffix, what PP atoms co-occur most?
suffix_pp_cooccurrence = defaultdict(Counter)

for key, data in line_data.items():
    for suffix in data['suffixes']:
        for pp in data['pp_atoms']:
            suffix_pp_cooccurrence[suffix][pp] += 1

print("="*70)
print("PP ATOMS THAT CO-OCCUR WITH EACH SUFFIX")
print("="*70)

# Focus on main suffixes
for suffix in ['y', 'dy', 'ol', 'or', 'al', 'ar', 'am', 'ey']:
    if suffix not in suffix_pp_cooccurrence:
        continue
    total = sum(suffix_pp_cooccurrence[suffix].values())
    print(f"\n-{suffix} (n={total}):")
    top_pp = suffix_pp_cooccurrence[suffix].most_common(10)
    for pp, count in top_pp:
        pct = 100 * count / total
        print(f"    {pp}: {pct:.1f}%")

# Now compare: do -ol and -y have different PP profiles?
print("\n" + "="*70)
print("SUFFIX FAMILY PP PROFILE COMPARISON")
print("="*70)

family_pp = defaultdict(Counter)
for suffix, pp_counts in suffix_pp_cooccurrence.items():
    family = get_suffix_family(suffix)
    for pp, count in pp_counts.items():
        family_pp[family][pp] += count

# Compare Y_SIMPLE vs L_FAMILY
print("\nComparing -y vs -ol/-al (waters vs oils?):")
y_total = sum(family_pp['Y_SIMPLE'].values())
l_total = sum(family_pp['L_FAMILY'].values())

if y_total and l_total:
    all_pp = set(family_pp['Y_SIMPLE'].keys()) | set(family_pp['L_FAMILY'].keys())

    print(f"\n{'PP atom':<15} {'Y_SIMPLE %':>12} {'L_FAMILY %':>12} {'Diff':>10}")
    print("-"*50)

    diffs = []
    for pp in all_pp:
        y_pct = 100 * family_pp['Y_SIMPLE'].get(pp, 0) / y_total
        l_pct = 100 * family_pp['L_FAMILY'].get(pp, 0) / l_total
        diff = l_pct - y_pct
        diffs.append((pp, y_pct, l_pct, diff))

    # Sort by absolute difference
    for pp, y_pct, l_pct, diff in sorted(diffs, key=lambda x: -abs(x[3]))[:15]:
        marker = "***" if abs(diff) > 3 else ""
        print(f"  {pp:<13} {y_pct:>11.1f}% {l_pct:>11.1f}% {diff:>+9.1f}% {marker}")

# Check: does -dy (RI-preferred) have a distinct profile?
print("\n" + "="*70)
print("-dy PROFILE (RI-PREFERRED SUFFIX)")
print("="*70)

dy_pp = suffix_pp_cooccurrence.get('dy', Counter())
y_pp = suffix_pp_cooccurrence.get('y', Counter())
dy_total = sum(dy_pp.values())
y_total = sum(y_pp.values())

if dy_total and y_total:
    print(f"\n-dy occurs with {dy_total} PP instances")
    print(f"-y occurs with {y_total} PP instances")

    print(f"\n{'PP atom':<15} {'-dy %':>12} {'-y %':>12} {'Diff':>10}")
    print("-"*50)

    all_pp = set(dy_pp.keys()) | set(y_pp.keys())
    diffs = []
    for pp in all_pp:
        dy_pct = 100 * dy_pp.get(pp, 0) / dy_total if dy_total else 0
        y_pct = 100 * y_pp.get(pp, 0) / y_total if y_total else 0
        diffs.append((pp, dy_pct, y_pct, dy_pct - y_pct))

    for pp, dy_pct, y_pct, diff in sorted(diffs, key=lambda x: -abs(x[3]))[:10]:
        marker = "***" if abs(diff) > 5 else ""
        print(f"  {pp:<13} {dy_pct:>11.1f}% {y_pct:>11.1f}% {diff:>+9.1f}% {marker}")

print("\n" + "="*70)
print("SPECULATION")
print("="*70)
print("""
Medieval product categories (Brunschwig):
  - Aquae (waters) - gentle distillation
  - Olea (oils) - separation from waters, sometimes higher heat
  - Spiritus - alcoholic, requires careful heat control
  - Pulveres (powders) - dried, ground

Possible Voynich mapping:
  -y  → Simple water? (most common, 32%)
  -ol → Oil? (Latin: oleum)
  -or → Tincture/spirit?
  -dy → Raw/unprocessed reference? (RI prefers this)
  -am/-an → Special preparations? (rarest)

The key test: Do these correlate with fire degree or processing intensity?
""")
