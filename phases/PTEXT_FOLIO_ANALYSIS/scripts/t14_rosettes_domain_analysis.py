#!/usr/bin/env python3
"""
Test 14: Rosettes Domain Analysis

Do Rosettes' MIDDLEs appear in botanical B folios or pharmaceutical B folios?
What domain do these procedures operate in?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect data by section
rosettes_tokens = []
b_by_section = defaultdict(list)
b_folios_by_section = defaultdict(set)
folio_sections = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()

            if not token.strip() or '*' in token:
                continue

            folio_sections[folio] = section

            if folio in ROSETTES:
                rosettes_tokens.append(token)
            elif currier == 'B':
                b_by_section[section].append(token)
                b_folios_by_section[section].add(folio)

print("=" * 70)
print("TEST 14: ROSETTES DOMAIN ANALYSIS")
print("=" * 70)
print()

# 1. Show B folios by section
print("1. CURRIER B FOLIOS BY SECTION")
print("-" * 50)

for section in sorted(b_by_section.keys()):
    folios = sorted(b_folios_by_section[section])
    tokens = len(b_by_section[section])
    print(f"\nSection '{section}': {len(folios)} folios, {tokens} tokens")
    print(f"  Folios: {', '.join(folios[:10])}{'...' if len(folios) > 10 else ''}")

print()

# 2. Rosettes section info
print("2. ROSETTES SECTIONS")
print("-" * 50)
for folio in sorted(ROSETTES):
    print(f"{folio}: Section '{folio_sections.get(folio, 'UNK')}'")
print()

# 3. MIDDLE vocabulary by section
print("3. MIDDLE VOCABULARY BY B SECTION")
print("-" * 50)

def get_middles(tokens):
    middles = set()
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.add(m.middle)
    return middles

rosettes_middles = get_middles(rosettes_tokens)
section_middles = {s: get_middles(tokens) for s, tokens in b_by_section.items()}

print(f"\nRosettes unique MIDDLEs: {len(rosettes_middles)}")
print()

print(f"{'Section':<10} {'Folios':<8} {'MIDDLEs':<10} {'Overlap w/ Ros':<15} {'%':<8}")
print("-" * 51)

overlaps = []
for section in sorted(section_middles.keys()):
    middles = section_middles[section]
    overlap = rosettes_middles & middles
    n_folios = len(b_folios_by_section[section])
    pct = len(overlap) / len(rosettes_middles) * 100 if rosettes_middles else 0
    overlaps.append((section, len(overlap), pct, n_folios))
    print(f"{section:<10} {n_folios:<8} {len(middles):<10} {len(overlap):<15} {pct:.1f}%")

print()

# 4. Which sections have highest overlap?
print("4. SECTIONS RANKED BY ROSETTES OVERLAP")
print("-" * 50)

overlaps.sort(key=lambda x: -x[2])
print(f"{'Rank':<6} {'Section':<10} {'Overlap %':<12} {'Shared MIDDLEs':<15}")
print("-" * 43)
for i, (section, count, pct, n_folios) in enumerate(overlaps[:10], 1):
    print(f"{i:<6} {section:<10} {pct:<12.1f}% {count:<15}")

print()

# 5. Rosettes-unique MIDDLEs - where do they NOT appear?
print("5. ROSETTES-UNIQUE MIDDLES ANALYSIS")
print("-" * 50)

all_b_middles = set()
for middles in section_middles.values():
    all_b_middles.update(middles)

ros_unique = rosettes_middles - all_b_middles
ros_shared = rosettes_middles & all_b_middles

print(f"Rosettes MIDDLEs shared with ANY B section: {len(ros_shared)} ({len(ros_shared)/len(rosettes_middles)*100:.1f}%)")
print(f"Rosettes MIDDLEs unique (not in any B): {len(ros_unique)} ({len(ros_unique)/len(rosettes_middles)*100:.1f}%)")
print()

if ros_unique:
    print(f"Unique MIDDLEs: {sorted(ros_unique)[:25]}{'...' if len(ros_unique) > 25 else ''}")
print()

# 6. Check if Rosettes MIDDLEs appear in Currier A
print("6. ROSETTES MIDDLES IN CURRIER A")
print("-" * 50)

# Reload to get A tokens
a_tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue
            currier = parts[6].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            if currier == 'A' and token.strip() and '*' not in token:
                a_tokens.append(token)

a_middles = get_middles(a_tokens)

ros_in_a = rosettes_middles & a_middles
ros_in_a_not_b = ros_in_a - all_b_middles

print(f"Rosettes MIDDLEs in Currier A: {len(ros_in_a)} ({len(ros_in_a)/len(rosettes_middles)*100:.1f}%)")
print(f"Rosettes MIDDLEs in A but NOT in any B: {len(ros_in_a_not_b)} ({len(ros_in_a_not_b)/len(rosettes_middles)*100:.1f}%)")
print()

if ros_in_a_not_b:
    print(f"A-only MIDDLEs used by Rosettes: {sorted(ros_in_a_not_b)[:20]}")
print()

# 7. Domain interpretation
print("=" * 70)
print("DOMAIN INTERPRETATION")
print("=" * 70)

# Find top overlapping sections
top_sections = overlaps[:3]

print(f"""
Rosettes MIDDLE vocabulary analysis:

1. Total unique MIDDLEs: {len(rosettes_middles)}
2. Shared with B sections: {len(ros_shared)} ({len(ros_shared)/len(rosettes_middles)*100:.1f}%)
3. Unique to Rosettes: {len(ros_unique)} ({len(ros_unique)/len(rosettes_middles)*100:.1f}%)

Top overlapping B sections:
""")

for section, count, pct, n_folios in top_sections:
    print(f"  - Section '{section}': {pct:.1f}% overlap ({count} shared MIDDLEs, {n_folios} folios)")

# Determine domain
if top_sections:
    top_section = top_sections[0][0]
    top_pct = top_sections[0][2]

    section_meanings = {
        'H': 'Herbal/Botanical',
        'B': 'Balneological/Bathing',
        'S': 'Stars/Pharmaceutical',
        'T': 'Text/Pharmaceutical',
        'A': 'Astronomical',
        'C': 'Cosmological',
        'Z': 'Zodiac'
    }

    domain = section_meanings.get(top_section, top_section)

    print(f"""
CONCLUSION:
Rosettes procedures primarily share vocabulary with Section '{top_section}' ({domain}).
Overlap rate: {top_pct:.1f}%

This suggests Rosettes encode {domain.lower()} procedures, operating on
similar materials/states as other {top_section}-section B folios.
""")
