#!/usr/bin/env python3
"""
Test 11: Rosettes Foldout Exploration

The Rosettes (f85/f86) are a large foldout with 9 diagrams.
What section are they in? How do they compare to other AZC folios?
Do they have P-text?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Collect all folios in AZC (language=NA) by section
section_folios = defaultdict(set)
folio_tokens = defaultdict(list)
folio_placements = defaultdict(Counter)
folio_section = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    columns = header.strip().split('\t')
    print("Columns:", columns)
    print()

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            # Get section if available (column index 3)
            section = parts[3].strip('"').strip() if len(parts) > 3 else 'UNK'

            if not token.strip() or '*' in token:
                continue

            folio_tokens[folio].append(token)
            folio_placements[folio][placement] += 1
            folio_section[folio] = section

            if currier == 'NA':
                section_folios[section].add(folio)

print("=" * 70)
print("TEST 11: ROSETTES FOLDOUT EXPLORATION")
print("=" * 70)
print()

# 1. What sections contain AZC folios?
print("1. AZC FOLIOS BY SECTION")
print("-" * 50)

for section in sorted(section_folios.keys()):
    folios = sorted(section_folios[section])
    print(f"\nSection '{section}': {len(folios)} folios")
    print(f"  Folios: {', '.join(folios[:15])}{'...' if len(folios) > 15 else ''}")

print()

# 2. Look for Rosettes specifically (f85, f86, or similar)
print("2. ROSETTES SEARCH")
print("-" * 50)

rosette_candidates = []
for folio in folio_tokens.keys():
    if '85' in folio or '86' in folio or 'ros' in folio.lower():
        rosette_candidates.append(folio)

if rosette_candidates:
    print(f"Found potential Rosettes folios: {rosette_candidates}")
else:
    print("No folios with '85', '86', or 'ros' in name found")
    print("\nLet me list all folios to find the Rosettes:")
    all_folios = sorted(folio_tokens.keys())
    print(f"Total folios: {len(all_folios)}")
    # Look for large foldouts - these often have multiple sub-pages
    foldout_candidates = [f for f in all_folios if len(folio_tokens[f]) > 200]
    print(f"\nFolios with >200 tokens (potential foldouts): {foldout_candidates}")

print()

# 3. Cosmological section details
print("3. COSMOLOGICAL (C) SECTION DETAILS")
print("-" * 50)

c_folios = section_folios.get('C', set())
if c_folios:
    print(f"Cosmological folios: {sorted(c_folios)}")
    print()

    for folio in sorted(c_folios):
        tokens = folio_tokens[folio]
        placements = folio_placements[folio]
        p_count = sum(v for k, v in placements.items() if k.startswith('P'))

        print(f"{folio}: {len(tokens)} tokens")
        print(f"  Placements: {dict(placements)}")
        print(f"  P-text tokens: {p_count}")
        print()
else:
    print("No folios in section 'C' found")

# 4. Compare to A (Astronomical) and Z (Zodiac)
print("4. ALL AZC SECTIONS COMPARISON")
print("-" * 50)

for section in ['A', 'Z', 'C']:
    folios = section_folios.get(section, set())
    if folios:
        total_tokens = sum(len(folio_tokens[f]) for f in folios)
        total_ptext = 0
        for f in folios:
            total_ptext += sum(v for k, v in folio_placements[f].items() if k.startswith('P'))

        print(f"\nSection {section}:")
        print(f"  Folios: {len(folios)}")
        print(f"  Total tokens: {total_tokens}")
        print(f"  P-text tokens: {total_ptext} ({total_ptext/total_tokens*100:.1f}%)")
        print(f"  Folio list: {sorted(folios)}")

print()

# 5. List ALL folios with their sections and counts
print("5. ALL FOLIOS IN TRANSCRIPT")
print("-" * 50)

print(f"\n{'Folio':<12} {'Section':<8} {'Tokens':<8} {'P-text':<8}")
print("-" * 40)

for folio in sorted(folio_tokens.keys()):
    section = folio_section.get(folio, 'UNK')
    tokens = len(folio_tokens[folio])
    p_count = sum(v for k, v in folio_placements[folio].items() if k.startswith('P'))

    # Only show AZC-like sections or large folios
    if section in ['A', 'Z', 'C'] or tokens > 300:
        print(f"{folio:<12} {section:<8} {tokens:<8} {p_count:<8}")
