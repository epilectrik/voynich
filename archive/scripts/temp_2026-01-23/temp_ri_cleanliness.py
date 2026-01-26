#!/usr/bin/env python3
"""
How clean is the RI-to-folio mapping?
- Do folios have distinct, non-overlapping RI?
- Or is there messy overlap?
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

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

# Build RI-to-folio and folio-to-RI mappings
ri_to_folios = defaultdict(set)
folio_to_ri = defaultdict(set)

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
            folio_to_ri[folio].add(middle)

print("="*70)
print("RI-TO-FOLIO MAPPING CLEANLINESS")
print("="*70)

# Distribution of folio counts per RI
folio_counts = [len(folios) for folios in ri_to_folios.values()]
count_dist = Counter(folio_counts)

print(f"\nRI by number of folios they appear on:")
total_ri = len(ri_to_folios)
cumulative = 0
for n in sorted(count_dist.keys()):
    count = count_dist[n]
    cumulative += count
    pct = 100 * count / total_ri
    cum_pct = 100 * cumulative / total_ri
    bar = '*' * min(count, 50)
    print(f"  {n:2d} folio(s): {count:3d} RI ({pct:4.1f}%) [cumulative: {cum_pct:5.1f}%] {bar}")

# How many RI are truly "local" (1-2 folios)?
local_ri = [ri for ri, folios in ri_to_folios.items() if len(folios) <= 2]
print(f"\n'Local' RI (1-2 folios): {len(local_ri)} / {total_ri} ({100*len(local_ri)/total_ri:.1f}%)")

print("\n" + "="*70)
print("FOLIO DISTINCTIVENESS")
print("="*70)

# For each folio, what % of its RI are unique to that folio?
folio_stats = []

for folio, ri_set in folio_to_ri.items():
    if not ri_set:
        continue

    unique_ri = [ri for ri in ri_set if len(ri_to_folios[ri]) == 1]
    shared_ri = [ri for ri in ri_set if len(ri_to_folios[ri]) > 1]

    folio_stats.append({
        'folio': folio,
        'total_ri': len(ri_set),
        'unique_ri': len(unique_ri),
        'shared_ri': len(shared_ri),
        'unique_pct': 100 * len(unique_ri) / len(ri_set) if ri_set else 0
    })

# Sort by unique %
folio_stats.sort(key=lambda x: -x['unique_pct'])

print(f"\nFolios with HIGHEST RI uniqueness (most distinct themes):")
for stat in folio_stats[:15]:
    print(f"  {stat['folio']}: {stat['unique_ri']}/{stat['total_ri']} unique ({stat['unique_pct']:.0f}%)")

print(f"\nFolios with LOWEST RI uniqueness (most shared themes):")
for stat in sorted(folio_stats, key=lambda x: x['unique_pct'])[:15]:
    print(f"  {stat['folio']}: {stat['unique_ri']}/{stat['total_ri']} unique ({stat['unique_pct']:.0f}%)")

# Overall stats
avg_unique_pct = sum(s['unique_pct'] for s in folio_stats) / len(folio_stats) if folio_stats else 0
print(f"\nAverage folio RI uniqueness: {avg_unique_pct:.1f}%")

print("\n" + "="*70)
print("FOLIO OVERLAP ANALYSIS")
print("="*70)

# For folios that share RI, how much overlap is there?
folio_list = list(folio_to_ri.keys())
overlap_counts = []

for i, f1 in enumerate(folio_list):
    for f2 in folio_list[i+1:]:
        shared = folio_to_ri[f1] & folio_to_ri[f2]
        if shared:
            overlap_counts.append({
                'f1': f1,
                'f2': f2,
                'shared': len(shared),
                'shared_ri': list(shared)[:5]
            })

overlap_counts.sort(key=lambda x: -x['shared'])

print(f"\nFolio pairs with MOST RI overlap:")
for ov in overlap_counts[:15]:
    print(f"  {ov['f1']} + {ov['f2']}: {ov['shared']} shared RI")
    print(f"    Examples: {ov['shared_ri']}")

# How many folio pairs have ANY overlap?
pairs_with_overlap = len(overlap_counts)
total_pairs = len(folio_list) * (len(folio_list) - 1) // 2
print(f"\nFolio pairs with RI overlap: {pairs_with_overlap} / {total_pairs} ({100*pairs_with_overlap/total_pairs:.1f}%)")

# Summary
print("\n" + "="*70)
print("SUMMARY: IS IT CLEAN?")
print("="*70)

clean_threshold = 80  # % of RI that are local
is_clean = (100 * len(local_ri) / total_ri) >= clean_threshold

print(f"""
Local RI (1-2 folios): {100*len(local_ri)/total_ri:.1f}%
Average folio uniqueness: {avg_unique_pct:.1f}%
Folio pairs with overlap: {100*pairs_with_overlap/total_pairs:.1f}%

VERDICT: {"CLEAN - clear delineation" if is_clean else "MESSY - significant overlap"}

The pattern is {"clean" if is_clean else "messy"} because:
- {100*len(local_ri)/total_ri:.0f}% of RI appear on only 1-2 folios
- Most folios have unique RI signatures
- Overlap between folios is {"minimal" if pairs_with_overlap/total_pairs < 0.1 else "moderate" if pairs_with_overlap/total_pairs < 0.3 else "significant"}
""")
