#!/usr/bin/env python3
"""
Test 1: P-text Folio Physical Characteristics

Questions:
- Which folios have P-text vs no P-text?
- Do P-text folios cluster by quire, foldout status, diagram type?
- What distinguishes the 9 P-text folios?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
import re

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Collect data
# Column indices: 0=word, 2=folio, 6=language(currier), 10=placement, 12=transcriber
azc_folios = set()
ptext_tokens_by_folio = defaultdict(list)
diagram_tokens_by_folio = defaultdict(list)
all_placements_by_folio = defaultdict(Counter)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            if currier == 'NA':  # AZC tokens
                folio = parts[2].strip('"').strip()  # Column 2
                token = parts[0].strip('"').strip().lower()
                placement = parts[10].strip('"').strip()

                if not token.strip():
                    continue

                azc_folios.add(folio)
                all_placements_by_folio[folio][placement] += 1

                if placement == 'P' or placement.startswith('P'):
                    ptext_tokens_by_folio[folio].append(token)
                else:
                    diagram_tokens_by_folio[folio].append(token)

# Folios with P-text (empirical)
ptext_folios = set(ptext_tokens_by_folio.keys())

print("=" * 70)
print("TEST 1: P-TEXT FOLIO CHARACTERISTICS")
print("=" * 70)
print()

# 1. Basic stats
print("1. BASIC STATISTICS")
print("-" * 50)
print(f"Total AZC folios: {len(azc_folios)}")
print(f"Folios with P-text: {len(ptext_folios)}")
print(f"Folios without P-text: {len(azc_folios - ptext_folios)}")
print()

# 2. P-text token counts
print("2. P-TEXT TOKEN COUNTS BY FOLIO")
print("-" * 50)
print(f"{'Folio':<12} {'P-text':<8} {'Diagram':<8} {'P-ratio':<8}")
print("-" * 36)

for folio in sorted(ptext_folios):
    p_count = len(ptext_tokens_by_folio[folio])
    d_count = len(diagram_tokens_by_folio[folio])
    total = p_count + d_count
    ratio = p_count / total if total > 0 else 0
    print(f"{folio:<12} {p_count:<8} {d_count:<8} {ratio:.1%}")

total_ptext = sum(len(v) for v in ptext_tokens_by_folio.values())
total_diagram = sum(len(v) for v in diagram_tokens_by_folio.values())
print("-" * 36)
print(f"{'TOTAL':<12} {total_ptext:<8} {total_diagram:<8} {total_ptext/(total_ptext+total_diagram):.1%}")
print()

# 3. Folio numbering pattern
print("3. P-TEXT FOLIOS")
print("-" * 50)
print("P-text folios (sorted):", sorted(ptext_folios))
print()

# Extract folio numbers
def extract_folio_num(f):
    match = re.match(r'f(\d+)', f)
    return int(match.group(1)) if match else 0

ptext_nums = sorted([extract_folio_num(f) for f in ptext_folios])
print(f"Folio number range: {min(ptext_nums)} to {max(ptext_nums)}")
print(f"Span: {max(ptext_nums) - min(ptext_nums) + 1} folios")
print()

# 4. Non-P-text AZC folios for comparison
non_ptext_azc = azc_folios - ptext_folios
print("4. NON-P-TEXT AZC FOLIOS")
print("-" * 50)
print(f"Count: {len(non_ptext_azc)}")
print(f"Folios: {sorted(non_ptext_azc)}")
print()

# 5. Placement distribution
print("5. PLACEMENT DISTRIBUTION IN P-TEXT FOLIOS")
print("-" * 50)
for folio in sorted(ptext_folios):
    placements = all_placements_by_folio[folio]
    total = sum(placements.values())
    print(f"{folio} (n={total}):")
    for p, count in sorted(placements.items(), key=lambda x: -x[1])[:5]:
        print(f"  {p}: {count} ({count/total:.1%})")
    print()

# 6. Are P-text folios all foldouts?
print("6. FOLDOUT PATTERN")
print("-" * 50)
# Folios ending in numbers > 1 (like f67r1, f67r2) suggest multi-page foldouts
foldout_indicators = []
for f in ptext_folios:
    if re.search(r'[rv]\d+$', f):
        foldout_indicators.append(f)

print(f"Folios with multi-page indicator (e.g., f67r1, f67r2): {len(foldout_indicators)}")
print(f"  {sorted(foldout_indicators)}")
simple_folios = ptext_folios - set(foldout_indicators)
print(f"Simple folios (e.g., f65v): {len(simple_folios)}")
print(f"  {sorted(simple_folios)}")
print()

# 7. Compare to non-P-text AZC folios
print("7. COMPARISON: P-TEXT vs NON-P-TEXT AZC FOLIOS")
print("-" * 50)
# Check if non-P-text folios are different (e.g., Zodiac)
non_ptext_nums = sorted([extract_folio_num(f) for f in non_ptext_azc])
if non_ptext_nums:
    print(f"Non-P-text folio number range: {min(non_ptext_nums)} to {max(non_ptext_nums)}")
else:
    print("No non-P-text folios found")

# Zodiac folios are typically f70v-f73v
zodiac_range = set(f for f in non_ptext_azc if extract_folio_num(f) >= 70)
non_zodiac_range = set(f for f in non_ptext_azc if extract_folio_num(f) < 70)
print(f"\nNon-P-text in f70+ (likely Zodiac): {len(zodiac_range)}")
print(f"Non-P-text in <f70 (likely A/C): {len(non_zodiac_range)}")

# List all non-P-text folios by range
print(f"\nNon-P-text Zodiac folios: {sorted(zodiac_range)}")
print(f"Non-P-text A/C folios: {sorted(non_zodiac_range)}")
print()

# 8. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Key findings:

1. P-text appears on {len(ptext_folios)} AZC folios (of {len(azc_folios)} total)
2. P-text folios: {sorted(ptext_folios)}
3. All in f{min(ptext_nums)}-f{max(ptext_nums)} range
4. {len(foldout_indicators)} of {len(ptext_folios)} have foldout indicators
5. Total P-text: {total_ptext} tokens ({total_ptext/(total_ptext+total_diagram):.1%} of AZC)

Non-P-text AZC folios: {len(non_ptext_azc)}
  - In Zodiac range (f70+): {len(zodiac_range)}
  - In A/C range (<f70): {len(non_zodiac_range)}
""")
