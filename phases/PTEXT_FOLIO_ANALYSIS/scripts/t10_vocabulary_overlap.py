#!/usr/bin/env python3
"""
Test 10: P-text Vocabulary - Where Does It Appear?

Question: Does P-text vocabulary appear on the diagrams?
- What % of P-text MIDDLEs appear on same-folio diagram?
- What % appear on ANY AZC diagram?
- What % are unique to P-text (not on any diagram)?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

# Collect MIDDLEs by category
ptext_by_folio = defaultdict(list)  # folio -> list of MIDDLEs
diagram_by_folio = defaultdict(list)  # folio -> list of MIDDLEs
currier_a_middles = []
currier_b_middles = []

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
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            m = morph.extract(token)
            if not m.middle:
                continue

            if currier == 'NA':
                if placement == 'P' or placement.startswith('P'):
                    ptext_by_folio[folio].append(m.middle)
                else:
                    diagram_by_folio[folio].append(m.middle)
            elif currier == 'A':
                currier_a_middles.append(m.middle)
            elif currier == 'B':
                currier_b_middles.append(m.middle)

print("=" * 70)
print("TEST 10: P-TEXT VOCABULARY - WHERE DOES IT APPEAR?")
print("=" * 70)
print()

# Get unique MIDDLE sets
all_ptext_middles = set()
for middles in ptext_by_folio.values():
    all_ptext_middles.update(middles)

all_diagram_middles = set()
for middles in diagram_by_folio.values():
    all_diagram_middles.update(middles)

currier_a_set = set(currier_a_middles)
currier_b_set = set(currier_b_middles)

print(f"Unique P-text MIDDLEs: {len(all_ptext_middles)}")
print(f"Unique AZC diagram MIDDLEs: {len(all_diagram_middles)}")
print(f"Unique Currier A MIDDLEs: {len(currier_a_set)}")
print(f"Unique Currier B MIDDLEs: {len(currier_b_set)}")
print()

# 1. P-text MIDDLEs on diagrams
print("1. P-TEXT MIDDLES ON AZC DIAGRAMS")
print("-" * 50)

ptext_on_any_diagram = all_ptext_middles & all_diagram_middles
ptext_not_on_diagram = all_ptext_middles - all_diagram_middles

print(f"P-text MIDDLEs appearing on ANY diagram: {len(ptext_on_any_diagram)} ({len(ptext_on_any_diagram)/len(all_ptext_middles)*100:.1f}%)")
print(f"P-text MIDDLEs NOT on any diagram: {len(ptext_not_on_diagram)} ({len(ptext_not_on_diagram)/len(all_ptext_middles)*100:.1f}%)")
print()

# 2. Same-folio overlap
print("2. SAME-FOLIO DIAGRAM OVERLAP")
print("-" * 50)

for folio in sorted(ptext_by_folio.keys()):
    p_middles = set(ptext_by_folio[folio])
    d_middles = set(diagram_by_folio.get(folio, []))

    overlap = p_middles & d_middles
    p_only = p_middles - d_middles

    print(f"{folio}: P-text has {len(p_middles)} MIDDLEs, diagram has {len(d_middles)}")
    print(f"       Overlap: {len(overlap)} ({len(overlap)/len(p_middles)*100:.1f}% of P-text)")
    if overlap:
        print(f"       Shared: {sorted(overlap)[:10]}{'...' if len(overlap) > 10 else ''}")
    print()

# 3. P-text MIDDLEs in Currier A and B
print("3. P-TEXT MIDDLES IN CURRIER A AND B")
print("-" * 50)

ptext_in_a = all_ptext_middles & currier_a_set
ptext_in_b = all_ptext_middles & currier_b_set
ptext_only = all_ptext_middles - currier_a_set - currier_b_set - all_diagram_middles

print(f"P-text MIDDLEs in Currier A: {len(ptext_in_a)} ({len(ptext_in_a)/len(all_ptext_middles)*100:.1f}%)")
print(f"P-text MIDDLEs in Currier B: {len(ptext_in_b)} ({len(ptext_in_b)/len(all_ptext_middles)*100:.1f}%)")
print(f"P-text MIDDLEs UNIQUE (not in A, B, or diagram): {len(ptext_only)} ({len(ptext_only)/len(all_ptext_middles)*100:.1f}%)")
print()

if ptext_only:
    print(f"Unique P-text MIDDLEs: {sorted(ptext_only)[:20]}")
print()

# 4. Where do P-text MIDDLEs come from?
print("4. P-TEXT MIDDLE SOURCE BREAKDOWN")
print("-" * 50)

# Categorize each P-text MIDDLE
categories = {
    'in_same_folio_diagram': 0,
    'in_other_diagram_only': 0,
    'in_A_not_diagram': 0,
    'in_B_not_A': 0,
    'unique_to_ptext': 0
}

ptext_middle_sources = {}
for folio, middles in ptext_by_folio.items():
    same_folio_diagram = set(diagram_by_folio.get(folio, []))
    other_diagrams = all_diagram_middles - same_folio_diagram

    for m in set(middles):
        if m in same_folio_diagram:
            categories['in_same_folio_diagram'] += 1
            ptext_middle_sources[m] = 'same_folio_diagram'
        elif m in other_diagrams:
            categories['in_other_diagram_only'] += 1
            ptext_middle_sources[m] = 'other_diagram'
        elif m in currier_a_set:
            categories['in_A_not_diagram'] += 1
            ptext_middle_sources[m] = 'currier_a'
        elif m in currier_b_set:
            categories['in_B_not_A'] += 1
            ptext_middle_sources[m] = 'currier_b_only'
        else:
            categories['unique_to_ptext'] += 1
            ptext_middle_sources[m] = 'unique'

total_unique_ptext = len(all_ptext_middles)
print(f"{'Source':<25} {'Count':<8} {'%':<8}")
print("-" * 41)
for cat, count in categories.items():
    print(f"{cat:<25} {count:<8} {count/total_unique_ptext*100:.1f}%")

print()

# 5. The key question
print("=" * 70)
print("KEY FINDING")
print("=" * 70)

same_folio_rate = categories['in_same_folio_diagram'] / total_unique_ptext
any_diagram_rate = (categories['in_same_folio_diagram'] + categories['in_other_diagram_only']) / total_unique_ptext
a_rate = len(ptext_in_a) / total_unique_ptext

print(f"""
P-text MIDDLE vocabulary breakdown:

- Appears on SAME-FOLIO diagram: {categories['in_same_folio_diagram']} ({same_folio_rate*100:.1f}%)
- Appears on ANY diagram: {categories['in_same_folio_diagram'] + categories['in_other_diagram_only']} ({any_diagram_rate*100:.1f}%)
- Appears in Currier A: {len(ptext_in_a)} ({a_rate*100:.1f}%)
- Appears in Currier B: {len(ptext_in_b)} ({len(ptext_in_b)/total_unique_ptext*100:.1f}%)
- UNIQUE to P-text: {categories['unique_to_ptext']} ({categories['unique_to_ptext']/total_unique_ptext*100:.1f}%)
""")

if same_folio_rate > 0.5:
    print("=> P-text vocabulary STRONGLY overlaps with same-folio diagram")
    print("   This suggests P-text ANNOTATES or INDEXES the diagram content")
elif any_diagram_rate > 0.5:
    print("=> P-text vocabulary overlaps with AZC diagrams generally")
    print("   This suggests P-text is part of AZC system, not pure Currier A")
elif a_rate > 0.7:
    print("=> P-text vocabulary is primarily Currier A")
    print("   But it appears in DIFFERENT LOCATIONS than A (on AZC folios)")
else:
    print("=> P-text vocabulary has MIXED sources")
    print("   It may be a bridge between A and AZC systems")
