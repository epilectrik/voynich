"""
SECTION H FIRE-DEGREE ANOMALY

Finding: Section H has the LOWEST high-fire ratio (0.22)
- Section H = "herbal" (botanical illustrations)
- Section C = cosmological has HIGHEST (0.48)
- Section B = balneological is middle (0.39)

This is counterintuitive: if Section H is "herbal/botanical",
shouldn't it have MORE fire-intensive processing for volatile aromatics?

Questions:
1. What suffixes dominate in Section H?
2. What MIDDLEs are Section H exclusive?
3. Does Section H have different PREFIX distribution?
4. Is Section H more "registry-like" (lower processing intensity)?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("SECTION H FIRE-DEGREE ANOMALY INVESTIGATION")
print("=" * 70)

# Fire-degree suffixes (from C527)
HIGH_FIRE = {'ey', 'ol', 'eey'}  # Animal/high-fire
LOW_FIRE = {'y', 'dy', 'edy'}    # Herb/low-fire

# Collect data by section
section_data = defaultdict(lambda: {
    'tokens': [],
    'suffixes': Counter(),
    'prefixes': Counter(),
    'middles': Counter(),
})

folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

for token in tx.currier_b():
    if token.word and token.folio:
        m = morph.extract(token.word)
        section = folio_section.get(token.folio, 'unknown')
        section_data[section]['tokens'].append({
            'word': token.word,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })
        section_data[section]['suffixes'][m.suffix or ''] += 1
        section_data[section]['prefixes'][m.prefix or ''] += 1
        section_data[section]['middles'][m.middle or ''] += 1

# =============================================================================
# STEP 1: Suffix distribution by section
# =============================================================================
print("\n" + "=" * 70)
print("STEP 1: Suffix distribution by section")
print("=" * 70)

print("\n  Fire-degree suffixes:")
for section in sorted(section_data.keys()):
    suffixes = section_data[section]['suffixes']
    total = sum(suffixes.values())
    if total < 100:
        continue

    high = sum(suffixes[s] for s in HIGH_FIRE)
    low = sum(suffixes[s] for s in LOW_FIRE)
    high_pct = high / total * 100
    low_pct = low / total * 100
    ratio = high / low if low else 0

    print(f"\n  Section {section} (n={total}):")
    print(f"    High-fire (ey/ol/eey): {high} ({high_pct:.1f}%)")
    print(f"    Low-fire (y/dy/edy): {low} ({low_pct:.1f}%)")
    print(f"    Ratio: {ratio:.2f}")

# =============================================================================
# STEP 2: Top suffixes by section
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Top suffixes by section")
print("=" * 70)

for section in sorted(section_data.keys()):
    suffixes = section_data[section]['suffixes']
    total = sum(suffixes.values())
    if total < 100:
        continue

    print(f"\n  Section {section}:")
    for suffix, count in suffixes.most_common(8):
        pct = count / total * 100
        marker = ""
        if suffix in HIGH_FIRE:
            marker = " [HIGH-FIRE]"
        elif suffix in LOW_FIRE:
            marker = " [LOW-FIRE]"
        print(f"    {suffix or '(none)'}: {pct:.1f}%{marker}")

# =============================================================================
# STEP 3: PREFIX distribution by section
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: PREFIX distribution by section")
print("=" * 70)

ENERGY_PREFIXES = {'ch', 'sh', 'qo', 'tch', 'pch', 'dch'}
LATE_PREFIXES = {'al', 'ar', 'or'}

for section in sorted(section_data.keys()):
    prefixes = section_data[section]['prefixes']
    total = sum(prefixes.values())
    if total < 100:
        continue

    energy = sum(prefixes[p] for p in ENERGY_PREFIXES)
    late = sum(prefixes[p] for p in LATE_PREFIXES)
    none = prefixes['']

    print(f"\n  Section {section}:")
    print(f"    ENERGY (ch/sh/qo): {energy/total*100:.1f}%")
    print(f"    LATE (al/ar/or): {late/total*100:.1f}%")
    print(f"    No prefix: {none/total*100:.1f}%")

# =============================================================================
# STEP 4: Section-exclusive MIDDLEs
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Section-exclusive MIDDLEs")
print("=" * 70)

# Find MIDDLEs that appear predominantly in one section
all_middles = set()
for section, data in section_data.items():
    all_middles.update(data['middles'].keys())

section_exclusive = defaultdict(list)
for middle in all_middles:
    if not middle:
        continue

    counts = {s: section_data[s]['middles'][middle] for s in section_data}
    total = sum(counts.values())
    if total < 10:
        continue

    for section, count in counts.items():
        if count / total >= 0.7:  # 70%+ in one section
            section_exclusive[section].append({
                'middle': middle,
                'count': count,
                'total': total,
                'pct': count / total * 100,
            })

print("\n  Section-concentrated MIDDLEs (70%+ in one section):")
for section in sorted(section_exclusive.keys()):
    items = sorted(section_exclusive[section], key=lambda x: x['count'], reverse=True)
    print(f"\n  Section {section}: {len(items)} MIDDLEs")
    for item in items[:10]:
        print(f"    {item['middle']}: {item['pct']:.0f}% ({item['count']}/{item['total']})")

# =============================================================================
# STEP 5: Section H deep dive
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Section H deep dive")
print("=" * 70)

h_data = section_data['H']
h_total = len(h_data['tokens'])

# What makes H different?
print(f"\n  Section H has {h_total} tokens")

# Suffix-less rate
suffix_less = sum(1 for t in h_data['tokens'] if not t['suffix'])
print(f"  Suffix-less rate: {suffix_less/h_total*100:.1f}%")

# Compare to other sections
for section in ['B', 'S', 'C']:
    if section in section_data:
        data = section_data[section]
        total = len(data['tokens'])
        sl = sum(1 for t in data['tokens'] if not t['suffix'])
        print(f"  Section {section} suffix-less: {sl/total*100:.1f}%")

# Most common H middles vs others
print("\n  Section H most common MIDDLEs:")
for mid, count in h_data['middles'].most_common(10):
    pct = count / h_total * 100
    # Check if this is H-enriched
    h_rate = count / h_total
    other_count = sum(section_data[s]['middles'][mid] for s in section_data if s != 'H')
    other_total = sum(len(section_data[s]['tokens']) for s in section_data if s != 'H')
    other_rate = other_count / other_total if other_total else 0
    enrichment = h_rate / other_rate if other_rate else float('inf')
    print(f"    {mid or '(none)'}: {pct:.1f}% (H enrichment: {enrichment:.2f}x)")

# =============================================================================
# STEP 6: Hypothesis testing
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Why does Section H have lowest fire-degree?")
print("=" * 70)

print("""
HYPOTHESES TO TEST:

H1: Section H is more "registry-like" (labeling, not processing)
    -> Test: Higher suffix-less rate? More ct-type MIDDLEs?

H2: Section H processes STABLE materials (low volatility)
    -> Test: Higher M-D (stable/homogeneous) prefixes?

H3: Section H uses TOLERANCE mode (sh > ch)
    -> Test: Higher sh/ch ratio?

H4: Section H documents OUTPUT, not PROCESS
    -> Test: Higher LATE prefixes? More terminal forms?

H5: Fire-degree correlates with material CLASS, not section
    -> Test: Do H folios with animal materials have higher fire-degree?
""")

# Test H1: Registry-like
print("\n  H1: Registry-like (suffix-less rate):")
for section in sorted(section_data.keys()):
    data = section_data[section]
    total = len(data['tokens'])
    if total < 100:
        continue
    sl = sum(1 for t in data['tokens'] if not t['suffix'])
    print(f"    {section}: {sl/total*100:.1f}%")

# Test H3: Tolerance mode (sh/ch ratio)
print("\n  H3: Tolerance mode (sh vs ch prefix):")
for section in sorted(section_data.keys()):
    prefixes = section_data[section]['prefixes']
    total = sum(prefixes.values())
    if total < 100:
        continue
    sh = prefixes['sh']
    ch = prefixes['ch']
    ratio = sh / ch if ch else float('inf')
    print(f"    {section}: sh/ch = {ratio:.2f} (sh={sh/total*100:.1f}%, ch={ch/total*100:.1f}%)")

# Test H4: Output documentation (LATE prefixes)
print("\n  H4: Output documentation (LATE prefix rate):")
for section in sorted(section_data.keys()):
    prefixes = section_data[section]['prefixes']
    total = sum(prefixes.values())
    if total < 100:
        continue
    late = sum(prefixes[p] for p in LATE_PREFIXES)
    print(f"    {section}: {late/total*100:.2f}%")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
KEY OBSERVATIONS:

1. Section H has LOWEST high-fire suffix ratio (0.22)
   - But similar LOW-fire rate to others (17.8%)
   - The difference is in HIGH-fire depletion, not LOW-fire enrichment

2. Check which hypothesis best explains the pattern...
""")
