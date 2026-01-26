#!/usr/bin/env python3
"""
Within a folio, are the unique MIDDLEs related?
- Do they share PP atoms?
- Do they share PREFIX/SUFFIX patterns?
- Any structural similarity?
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

def get_pp_atoms(middle):
    """Get PP atoms contained in this MIDDLE (length >= 2)."""
    if not middle:
        return set()
    atoms = set()
    for pp in pp_middles:
        if len(pp) >= 2 and pp in middle:
            atoms.add(pp)
    return atoms

# Collect data by folio
folio_middles = defaultdict(set)
folio_prefixes = defaultdict(list)
folio_suffixes = defaultdict(list)

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
        prefix, middle, suffix = extract_parts(word)
        if middle and middle in ri_middles:
            folio_middles[folio].add(middle)
            folio_prefixes[folio].append(prefix)
            folio_suffixes[folio].append(suffix)

print("="*70)
print("DO MIDDLES ON SAME FOLIO SHARE PP ATOMS?")
print("="*70)

# For each folio, check PP atom overlap between its MIDDLEs
folio_pp_sharing = []

for folio, middles in folio_middles.items():
    if len(middles) < 2:
        continue

    # Get PP atoms for each MIDDLE
    middle_pp = {m: get_pp_atoms(m) for m in middles}

    # Find shared PP atoms (appear in 2+ MIDDLEs)
    all_pp = []
    for pp_set in middle_pp.values():
        all_pp.extend(pp_set)
    pp_counts = Counter(all_pp)
    shared_pp = {pp for pp, count in pp_counts.items() if count >= 2}

    # Calculate sharing ratio
    total_unique_pp = len(set(all_pp))
    sharing_ratio = len(shared_pp) / total_unique_pp if total_unique_pp > 0 else 0

    folio_pp_sharing.append({
        'folio': folio,
        'middles': list(middles),
        'middle_count': len(middles),
        'shared_pp': shared_pp,
        'sharing_ratio': sharing_ratio
    })

# Sort by sharing ratio
folio_pp_sharing.sort(key=lambda x: -x['sharing_ratio'])

print("\nFolios with HIGHEST PP atom sharing between MIDDLEs:")
for item in folio_pp_sharing[:10]:
    print(f"\n  {item['folio']} ({item['middle_count']} MIDDLEs):")
    print(f"    MIDDLEs: {item['middles'][:5]}")
    print(f"    Shared PP atoms: {item['shared_pp']}")
    print(f"    Sharing ratio: {item['sharing_ratio']:.2f}")

print("\nFolios with LOWEST PP atom sharing:")
for item in folio_pp_sharing[-5:]:
    print(f"\n  {item['folio']} ({item['middle_count']} MIDDLEs):")
    print(f"    MIDDLEs: {item['middles'][:5]}")
    print(f"    Shared PP atoms: {item['shared_pp']}")

# Average sharing
avg_sharing = sum(x['sharing_ratio'] for x in folio_pp_sharing) / len(folio_pp_sharing)
print(f"\nAverage PP sharing ratio: {avg_sharing:.2f}")

print("\n" + "="*70)
print("DO MIDDLES ON SAME FOLIO SHARE PREFIX/SUFFIX PATTERNS?")
print("="*70)

# Check if folios have dominant PREFIX or SUFFIX
for folio in list(folio_middles.keys())[:10]:
    prefixes = [p for p in folio_prefixes[folio] if p]
    suffixes = [s for s in folio_suffixes[folio] if s]

    if not prefixes and not suffixes:
        continue

    prefix_dist = Counter(prefixes)
    suffix_dist = Counter(suffixes)

    # Calculate dominance (most common / total)
    if prefixes:
        top_prefix, top_count = prefix_dist.most_common(1)[0]
        prefix_dominance = top_count / len(prefixes)
    else:
        top_prefix, prefix_dominance = None, 0

    if suffixes:
        top_suffix, top_count = suffix_dist.most_common(1)[0]
        suffix_dominance = top_count / len(suffixes)
    else:
        top_suffix, suffix_dominance = None, 0

    print(f"\n  {folio}:")
    print(f"    Top prefix: '{top_prefix}' ({prefix_dominance:.0%} of uses)")
    print(f"    Top suffix: '{top_suffix}' ({suffix_dominance:.0%} of uses)")

print("\n" + "="*70)
print("DETAILED EXAMPLES: FOLIO CLUSTERING")
print("="*70)

# Show a few folios in detail
for folio in ['f88r', 'f58r', 'f99v']:
    if folio not in folio_middles:
        continue

    middles = list(folio_middles[folio])
    print(f"\n{'='*60}")
    print(f"FOLIO {folio}: {len(middles)} unique MIDDLEs")
    print("="*60)

    for m in middles:
        pp_atoms = get_pp_atoms(m)
        print(f"  {m}: PP atoms = {pp_atoms}")

    # Find common PP atoms
    all_pp = []
    for m in middles:
        all_pp.extend(get_pp_atoms(m))
    common = [pp for pp, count in Counter(all_pp).items() if count >= 2]
    print(f"\n  PP atoms shared by 2+ MIDDLEs: {common}")

# Summary
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print(f"""
Average PP sharing ratio: {avg_sharing:.2f}

If high (>0.5): Folios cluster related materials (same PP = same procedures)
If low (<0.2): Folios contain diverse materials

This tells us whether folios are organized by:
- PROCEDURE TYPE (high sharing): "all fire-degree-2 herbs together"
- SPECIFIC THEME (low sharing): "herbs for headaches" (different procedures)
""")
