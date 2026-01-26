#!/usr/bin/env python3
"""
What distinguishes high-sharing folios from low-sharing folios?
- Folio position/section?
- Number of MIDDLEs?
- Distributed vs localized RI?
- Token counts?
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
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token:
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

def get_pp_atoms(middle):
    if not middle:
        return set()
    atoms = set()
    for pp in pp_middles:
        if len(pp) >= 2 and pp in middle:
            atoms.add(pp)
    return atoms

# Distributed RI (10+ folios)
distributed_ri = {'odaiin', 'ho', 'ols', 'eom', 'chol'}

# Collect folio data
folio_middles = defaultdict(set)
folio_tokens = defaultdict(int)
ri_to_folios = defaultdict(set)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue

        folio_tokens[folio] += 1
        middle = extract_middle(word)
        if middle and middle in ri_middles:
            folio_middles[folio].add(middle)
            ri_to_folios[middle].add(folio)

# Calculate PP sharing ratio for each folio
folio_stats = []

for folio, middles in folio_middles.items():
    if len(middles) < 2:
        continue

    # Get PP atoms for each MIDDLE
    all_pp = []
    for m in middles:
        all_pp.extend(get_pp_atoms(m))
    pp_counts = Counter(all_pp)
    shared_pp = {pp for pp, count in pp_counts.items() if count >= 2}
    total_unique_pp = len(set(all_pp))
    sharing_ratio = len(shared_pp) / total_unique_pp if total_unique_pp > 0 else 0

    # Count distributed vs localized RI
    dist_count = len([m for m in middles if m in distributed_ri])
    local_count = len([m for m in middles if len(ri_to_folios[m]) <= 2])

    # Extract folio number for position analysis
    folio_num = ''.join(c for c in folio if c.isdigit())
    folio_num = int(folio_num) if folio_num else 0

    folio_stats.append({
        'folio': folio,
        'folio_num': folio_num,
        'sharing_ratio': sharing_ratio,
        'middle_count': len(middles),
        'token_count': folio_tokens[folio],
        'distributed_ri': dist_count,
        'local_ri': local_count,
        'local_pct': 100 * local_count / len(middles) if middles else 0,
        'shared_pp': shared_pp
    })

# Split into high and low sharing
high_sharing = [f for f in folio_stats if f['sharing_ratio'] >= 0.20]
low_sharing = [f for f in folio_stats if f['sharing_ratio'] == 0]
medium_sharing = [f for f in folio_stats if 0 < f['sharing_ratio'] < 0.20]

print("="*70)
print("HIGH vs LOW SHARING FOLIO COMPARISON")
print("="*70)

print(f"\nHigh sharing (ratio >= 0.20): {len(high_sharing)} folios")
print(f"Medium sharing (0 < ratio < 0.20): {len(medium_sharing)} folios")
print(f"Low sharing (ratio = 0): {len(low_sharing)} folios")

# Compare features
def avg(lst):
    return sum(lst) / len(lst) if lst else 0

print("\n" + "-"*70)
print("FEATURE COMPARISON")
print("-"*70)

print(f"\n{'Feature':<30} {'High Share':>12} {'Medium':>12} {'Low Share':>12}")
print("-"*70)

# MIDDLE count
high_mid = avg([f['middle_count'] for f in high_sharing])
med_mid = avg([f['middle_count'] for f in medium_sharing])
low_mid = avg([f['middle_count'] for f in low_sharing])
print(f"{'Avg MIDDLEs per folio':<30} {high_mid:>12.1f} {med_mid:>12.1f} {low_mid:>12.1f}")

# Token count
high_tok = avg([f['token_count'] for f in high_sharing])
med_tok = avg([f['token_count'] for f in medium_sharing])
low_tok = avg([f['token_count'] for f in low_sharing])
print(f"{'Avg tokens per folio':<30} {high_tok:>12.1f} {med_tok:>12.1f} {low_tok:>12.1f}")

# Distributed RI count
high_dist = avg([f['distributed_ri'] for f in high_sharing])
med_dist = avg([f['distributed_ri'] for f in medium_sharing])
low_dist = avg([f['distributed_ri'] for f in low_sharing])
print(f"{'Avg distributed RI count':<30} {high_dist:>12.1f} {med_dist:>12.1f} {low_dist:>12.1f}")

# Local RI percentage
high_local = avg([f['local_pct'] for f in high_sharing])
med_local = avg([f['local_pct'] for f in medium_sharing])
low_local = avg([f['local_pct'] for f in low_sharing])
print(f"{'Avg % local RI':<30} {high_local:>11.0f}% {med_local:>11.0f}% {low_local:>11.0f}%")

# Folio position
high_pos = avg([f['folio_num'] for f in high_sharing])
med_pos = avg([f['folio_num'] for f in medium_sharing])
low_pos = avg([f['folio_num'] for f in low_sharing])
print(f"{'Avg folio number':<30} {high_pos:>12.1f} {med_pos:>12.1f} {low_pos:>12.1f}")

# List the folios
print("\n" + "="*70)
print("HIGH SHARING FOLIOS (ratio >= 0.20)")
print("="*70)
for f in sorted(high_sharing, key=lambda x: -x['sharing_ratio']):
    print(f"  {f['folio']}: ratio={f['sharing_ratio']:.2f}, {f['middle_count']} MIDDLEs, shared PP: {f['shared_pp']}")

print("\n" + "="*70)
print("LOW SHARING FOLIOS (ratio = 0)")
print("="*70)
for f in sorted(low_sharing, key=lambda x: x['folio']):
    print(f"  {f['folio']}: {f['middle_count']} MIDDLEs, {f['distributed_ri']} distributed RI")

# Check if distributed RI explains low sharing
print("\n" + "="*70)
print("ANALYSIS: DOES DISTRIBUTED RI EXPLAIN LOW SHARING?")
print("="*70)

# For low sharing folios, check their MIDDLEs
for f in low_sharing[:5]:
    middles = folio_middles[f['folio']]
    print(f"\n  {f['folio']}:")
    for m in middles:
        is_dist = "DISTRIBUTED" if m in distributed_ri else "local"
        pp = get_pp_atoms(m)
        print(f"    {m}: {is_dist}, PP atoms: {pp}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
