#!/usr/bin/env python3
"""
Is RI localized (specific plants) or distributed (categories)?

If specific plants: RI appears on 1-2 folios (where that plant is discussed)
If categories: RI appears on many folios (category spans pages)
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
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

# Track which folios each RI appears on
ri_to_folios = defaultdict(set)
pp_to_folios = defaultdict(set)

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
        if middle:
            if middle in ri_middles:
                ri_to_folios[middle].add(folio)
            elif middle in pp_middles:
                pp_to_folios[middle].add(folio)

print("="*70)
print("RI vs PP LOCALIZATION")
print("="*70)

# Distribution of folio counts
ri_folio_counts = [len(folios) for folios in ri_to_folios.values()]
pp_folio_counts = [len(folios) for folios in pp_to_folios.values()]

print(f"\nRI MIDDLEs appearing on exactly 1 folio: {sum(1 for c in ri_folio_counts if c == 1)}")
print(f"RI MIDDLEs appearing on 2-3 folios: {sum(1 for c in ri_folio_counts if 2 <= c <= 3)}")
print(f"RI MIDDLEs appearing on 4+ folios: {sum(1 for c in ri_folio_counts if c >= 4)}")

print(f"\nPP MIDDLEs appearing on exactly 1 folio: {sum(1 for c in pp_folio_counts if c == 1)}")
print(f"PP MIDDLEs appearing on 2-3 folios: {sum(1 for c in pp_folio_counts if 2 <= c <= 3)}")
print(f"PP MIDDLEs appearing on 4+ folios: {sum(1 for c in pp_folio_counts if c >= 4)}")

# Average
import statistics
avg_ri_folios = statistics.mean(ri_folio_counts) if ri_folio_counts else 0
avg_pp_folios = statistics.mean(pp_folio_counts) if pp_folio_counts else 0
median_ri = statistics.median(ri_folio_counts) if ri_folio_counts else 0
median_pp = statistics.median(pp_folio_counts) if pp_folio_counts else 0

print(f"\nAverage folios per RI MIDDLE: {avg_ri_folios:.1f} (median: {median_ri})")
print(f"Average folios per PP MIDDLE: {avg_pp_folios:.1f} (median: {median_pp})")

print("\n" + "="*70)
print("MOST LOCALIZED RI (appearing on fewest folios)")
print("="*70)

# Show most localized RI
localized_ri = [(ri, len(folios)) for ri, folios in ri_to_folios.items() if len(folios) == 1]
print(f"\nRI appearing on exactly 1 folio: {len(localized_ri)}")
print("Examples:")
for ri, _ in sorted(localized_ri, key=lambda x: x[0])[:15]:
    folio = list(ri_to_folios[ri])[0]
    print(f"  {ri}: only on {folio}")

print("\n" + "="*70)
print("MOST DISTRIBUTED RI (appearing on most folios)")
print("="*70)

distributed_ri = sorted(ri_to_folios.items(), key=lambda x: -len(x[1]))[:10]
print("\nRI appearing on most folios:")
for ri, folios in distributed_ri:
    print(f"  {ri}: {len(folios)} folios")

print("\n" + "="*70)
print("COMPARISON: PP DISTRIBUTION")
print("="*70)

distributed_pp = sorted(pp_to_folios.items(), key=lambda x: -len(x[1]))[:10]
print("\nPP appearing on most folios:")
for pp, folios in distributed_pp:
    print(f"  {pp}: {len(folios)} folios")

# Conclusion
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if avg_ri_folios < avg_pp_folios * 0.5:
    print(f"""
RI is SIGNIFICANTLY more localized than PP:
  - RI avg: {avg_ri_folios:.1f} folios
  - PP avg: {avg_pp_folios:.1f} folios

This suggests RI encodes SPECIFIC items:
  - Each RI is tied to a particular material
  - Materials are discussed on specific pages
  - Like a plant being on one or two pages of an herbal

PP encodes CATEGORIES/PROCEDURES:
  - Procedures are referenced across many materials
  - 'e' (standard distillation) appears throughout
""")
elif avg_ri_folios > avg_pp_folios:
    print("""
RI is MORE distributed than PP - unexpected.
May indicate RI = abstract categories that appear throughout.
""")
else:
    print("""
RI and PP have similar distribution.
Both may encode at category level.
""")
