"""
WHY 83 B FOLIOS?

Exploring what determines the number of distinct procedures.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("WHY 83 B FOLIOS?")
print("=" * 70)

# Count B folios and their properties
b_folios = set()
folio_tokens = defaultdict(int)
folio_middles = defaultdict(set)

for token in tx.currier_b():
    b_folios.add(token.folio)
    folio_tokens[token.folio] += 1
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            folio_middles[token.folio].add(m.middle)

# Unique MIDDLEs
middle_folio_count = Counter()
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

unique_per_folio = {}
for folio in b_folios:
    unique = [m for m in folio_middles[folio] if middle_folio_count[m] == 1]
    unique_per_folio[folio] = len(unique)

total_unique = sum(unique_per_folio.values())
core_middles = [m for m, c in middle_folio_count.items() if c >= len(b_folios) * 0.5]

print(f"\nB FOLIO STATISTICS:")
print(f"  B folios: {len(b_folios)}")
print(f"  Total unique MIDDLEs: {total_unique}")
print(f"  Mean unique per folio: {total_unique/len(b_folios):.1f}")
print(f"  Total distinct MIDDLEs in B: {len(middle_folio_count)}")
print(f"  Core MIDDLEs (>50% folios): {len(core_middles)}")

# A records
a_records = set()
a_folio_records = defaultdict(set)
for token in tx.currier_a():
    record_id = (token.folio, token.line)
    a_records.add(record_id)
    a_folio_records[token.folio].add(record_id)

print(f"\nA REGISTRY STATISTICS:")
print(f"  A records: {len(a_records)}")
print(f"  A folios: {len(a_folio_records)}")
print(f"  A:B folio ratio: {len(a_records)/len(b_folios):.1f}:1")

# Question: How many unique MIDDLEs would we need to distinguish 83 procedures?
# If each procedure needs ~10 unique identifiers, that's 830 unique MIDDLEs
# We have 858 unique MIDDLEs - close match!

print("\n" + "=" * 70)
print("COVERAGE ANALYSIS")
print("=" * 70)

# What if we had fewer folios? Would unique vocabulary collapse?
# Simulate: if we merged adjacent folios, how much unique vocabulary would remain?

folio_list = sorted(b_folios)

def count_unique_if_merged(n_groups):
    """If we merged folios into n_groups, how many unique MIDDLEs?"""
    group_size = len(folio_list) // n_groups
    groups = []
    for i in range(n_groups):
        start = i * group_size
        end = start + group_size if i < n_groups - 1 else len(folio_list)
        group_folios = folio_list[start:end]
        groups.append(group_folios)

    # Merge MIDDLEs within each group
    group_middles = []
    for group in groups:
        merged = set()
        for f in group:
            merged.update(folio_middles[f])
        group_middles.append(merged)

    # Count unique across groups
    middle_group_count = Counter()
    for middles in group_middles:
        for m in middles:
            middle_group_count[m] += 1

    unique = sum(1 for m, c in middle_group_count.items() if c == 1)
    return unique, len(group_middles)

print(f"\nUNIQUE VOCABULARY vs FOLIO COUNT:")
print(f"{'Groups':<10} {'Unique MIDDLEs':<20} {'Per Group':<15}")
print("-" * 45)

for n in [83, 60, 40, 30, 20, 10, 5]:
    if n <= len(folio_list):
        unique, actual_groups = count_unique_if_merged(n)
        per_group = unique / actual_groups if actual_groups > 0 else 0
        print(f"{actual_groups:<10} {unique:<20} {per_group:.1f}")

# Question: Is 83 near some natural break point?
print("\n" + "=" * 70)
print("VOCABULARY OVERLAP STRUCTURE")
print("=" * 70)

# Distribution of MIDDLE frequency
freq_dist = Counter(middle_folio_count.values())
print(f"\nMIDDLE frequency distribution:")
print(f"  Appear in 1 folio: {freq_dist[1]} ({100*freq_dist[1]/len(middle_folio_count):.1f}%)")
print(f"  Appear in 2-5 folios: {sum(freq_dist[i] for i in range(2,6))}")
print(f"  Appear in 6-20 folios: {sum(freq_dist[i] for i in range(6,21))}")
print(f"  Appear in 21-41 folios: {sum(freq_dist[i] for i in range(21,42))}")
print(f"  Appear in >41 folios (core): {sum(freq_dist[i] for i in range(42, max(freq_dist.keys())+1))}")

# Question: Is there a natural clustering that produces 83?
print("\n" + "=" * 70)
print("SECTION DISTRIBUTION")
print("=" * 70)

# Approximate section from folio numbers
import re
def get_section(folio):
    match = re.search(r'f(\d+)', folio)
    if not match:
        return 'unknown'
    num = int(match.group(1))
    if num <= 57:
        return 'herbal_A'
    elif num <= 66:
        return 'astro_cosmo'
    elif num <= 73:
        return 'bio_balneo'
    elif num <= 84:
        return 'herbal_B'
    elif num <= 102:
        return 'pharma'
    else:
        return 'recipe_stars'

section_folios = defaultdict(list)
for f in b_folios:
    section_folios[get_section(f)].append(f)

print(f"\nFolios per section:")
for section in sorted(section_folios.keys()):
    n = len(section_folios[section])
    unique_in_section = sum(unique_per_folio.get(f, 0) for f in section_folios[section])
    print(f"  {section}: {n} folios, {unique_in_section} unique MIDDLEs")

# Question: What determines the number per section?
print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

print(f"""
OBSERVATIONS:

1. UNIQUE VOCABULARY BUDGET:
   - 858 unique MIDDLEs distributed across 83 folios
   - Mean ~10.3 unique MIDDLEs per folio
   - This is the "identity budget" - what makes each procedure distinct

2. COVERAGE EFFICIENCY:
   - With 83 folios: 858 unique MIDDLEs
   - If merged to 40 groups: unique vocabulary would collapse significantly
   - 83 appears to be near the granularity that preserves procedural distinctiveness

3. A:B RATIO:
   - {len(a_records)} A records : 83 B folios = {len(a_records)/83:.0f}:1
   - Each procedure serves ~{len(a_records)/83:.0f} different material contexts on average

4. VOCABULARY STRUCTURE:
   - Core (>50% folios): {len(core_middles)} MIDDLEs = shared control vocabulary
   - Unique (1 folio): {freq_dist[1]} MIDDLEs = procedure identity
   - Ratio: {freq_dist[1]/len(core_middles):.1f}:1 unique to core

POSSIBLE ANSWERS TO "WHY 83?":

A) MASTERY HORIZON (current speculation):
   83 = number of distinct procedures an expert needs to master
   Matches Puff's 84 substances (curriculum scope)

B) COVERAGE MINIMUM:
   83 = minimum granularity that preserves unique procedure identity
   Fewer folios would collapse procedural distinctiveness

C) MATERIAL-PROCEDURE MATRIX:
   ~1559 materials × ~4 REGIMEs / ~{len(a_records)/(83*4):.0f} overlap = ~83 procedures
   Each REGIME tier needs enough procedures to cover the material space

D) PRACTICAL CONSTRAINT:
   83 = what fits in a portable codex with adequate procedural detail
   Physical book size may have driven the count
""")

# Additional analysis: REGIME distribution
print("\n" + "=" * 70)
print("REGIME DISTRIBUTION (from prior analysis)")
print("=" * 70)

print("""
From curriculum_realignment analysis:
- REGIME_2: ~11-27 folios (introductory, low CEI)
- REGIME_1: ~? folios (standard execution)
- REGIME_4: ~25 folios (precision, narrow tolerance)
- REGIME_3: ~16 folios (advanced, high CEI)

If REGIMEs represent completeness tiers, then:
- Simple procedures (REGIME_2): fewer needed, more overlap
- Complex procedures (REGIME_3): more needed, less overlap
- Precision procedures (REGIME_4): moderate count, specialized

The 83 total may emerge from covering each REGIME adequately.
""")
