"""
REGIME SEMANTIC INTERPRETATION: Correlation Analysis

From LINE_BOUNDARY_OPERATORS:
- REGIME_1/3: Control-intensive (high L-compound, high ENERGY)
- REGIME_2/4: Output-intensive (high LATE, lower ENERGY)

Questions:
1. Does REGIME correlate with material class (animal vs herb)?
2. Does REGIME correlate with suffix patterns (fire-degree)?
3. What other properties distinguish REGIME groups?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("REGIME SEMANTIC INTERPRETATION: Correlation Analysis")
print("=" * 70)

# =============================================================================
# STEP 1: Load REGIME mapping
# =============================================================================
print("\n[Step 1] Loading REGIME mapping...")

with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"  Loaded {len(folio_to_regime)} folios")
for regime in sorted(regime_mapping.keys()):
    print(f"    {regime}: {len(regime_mapping[regime])} folios")

# =============================================================================
# STEP 2: Collect B token data by folio
# =============================================================================
print("\n[Step 2] Collecting B token data...")

folio_data = defaultdict(lambda: {
    'tokens': [],
    'suffixes': Counter(),
    'prefixes': Counter(),
    'middles': Counter(),
})

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        f = token.folio
        folio_data[f]['tokens'].append({
            'word': token.word,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })
        folio_data[f]['suffixes'][m.suffix or ''] += 1
        folio_data[f]['prefixes'][m.prefix or ''] += 1
        folio_data[f]['middles'][m.middle or ''] += 1

print(f"  Collected data for {len(folio_data)} folios")

# =============================================================================
# STEP 3: Suffix pattern analysis (fire-degree proxy)
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Suffix pattern analysis by REGIME")
print("=" * 70)

# From C527: Animal = -ey/-ol (high fire), Herb = -y/-dy (low fire)
HIGH_FIRE_SUFFIXES = {'ey', 'ol', 'eey'}
LOW_FIRE_SUFFIXES = {'y', 'dy', 'edy'}

regime_suffix_stats = defaultdict(lambda: {
    'high_fire': 0,
    'low_fire': 0,
    'total': 0,
})

for folio, data in folio_data.items():
    if folio not in folio_to_regime:
        continue
    regime = folio_to_regime[folio]

    for suffix, count in data['suffixes'].items():
        regime_suffix_stats[regime]['total'] += count
        if suffix in HIGH_FIRE_SUFFIXES:
            regime_suffix_stats[regime]['high_fire'] += count
        elif suffix in LOW_FIRE_SUFFIXES:
            regime_suffix_stats[regime]['low_fire'] += count

print("\n  Fire-degree suffix distribution by REGIME:")
for regime in sorted(regime_suffix_stats.keys()):
    stats = regime_suffix_stats[regime]
    total = stats['total']
    high_pct = stats['high_fire'] / total * 100 if total else 0
    low_pct = stats['low_fire'] / total * 100 if total else 0
    ratio = stats['high_fire'] / stats['low_fire'] if stats['low_fire'] else float('inf')
    print(f"    {regime}: High={high_pct:.1f}%, Low={low_pct:.1f}%, Ratio={ratio:.2f}")

# =============================================================================
# STEP 4: Check existing material class data
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Material class correlation")
print("=" * 70)

try:
    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json', 'r') as f:
        material_priors = json.load(f)

    print(f"  Loaded material_class_priors.json")

    # Aggregate by REGIME
    regime_material = defaultdict(lambda: Counter())

    for middle, priors in material_priors.items():
        # Find dominant class
        if isinstance(priors, dict):
            dominant = max(priors.items(), key=lambda x: x[1])[0]

            # Find which folios have this MIDDLE
            for folio, data in folio_data.items():
                if folio not in folio_to_regime:
                    continue
                if middle in data['middles']:
                    regime = folio_to_regime[folio]
                    regime_material[regime][dominant] += data['middles'][middle]

    print("\n  Material class distribution by REGIME:")
    for regime in sorted(regime_material.keys()):
        counts = regime_material[regime]
        total = sum(counts.values())
        print(f"\n    {regime} (n={total}):")
        for cls, count in counts.most_common():
            pct = count / total * 100 if total else 0
            print(f"      {cls}: {count} ({pct:.1f}%)")

except Exception as e:
    print(f"  Could not load material class data: {e}")

# =============================================================================
# STEP 5: Kernel usage by REGIME
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Kernel usage by REGIME")
print("=" * 70)

# Kernel operators: k, h, e (from BCSC)
KERNEL_MIDDLES = {'k', 'ke', 'ked', 'key', 'kedy'}  # k-family

regime_kernel = defaultdict(lambda: {'kernel': 0, 'total': 0})

for folio, data in folio_data.items():
    if folio not in folio_to_regime:
        continue
    regime = folio_to_regime[folio]

    for middle, count in data['middles'].items():
        regime_kernel[regime]['total'] += count
        if middle and middle[0] == 'k':
            regime_kernel[regime]['kernel'] += count

print("\n  Kernel (k-family) usage by REGIME:")
for regime in sorted(regime_kernel.keys()):
    stats = regime_kernel[regime]
    pct = stats['kernel'] / stats['total'] * 100 if stats['total'] else 0
    print(f"    {regime}: {pct:.2f}% kernel")

# =============================================================================
# STEP 6: Vocabulary diversity by REGIME
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Vocabulary diversity by REGIME")
print("=" * 70)

regime_diversity = defaultdict(lambda: {'unique_middles': set(), 'total_tokens': 0})

for folio, data in folio_data.items():
    if folio not in folio_to_regime:
        continue
    regime = folio_to_regime[folio]

    regime_diversity[regime]['total_tokens'] += len(data['tokens'])
    regime_diversity[regime]['unique_middles'].update(data['middles'].keys())

print("\n  Vocabulary diversity by REGIME:")
for regime in sorted(regime_diversity.keys()):
    stats = regime_diversity[regime]
    unique = len(stats['unique_middles'])
    total = stats['total_tokens']
    ratio = unique / total * 100 if total else 0
    print(f"    {regime}: {unique} unique MIDDLEs, {total} tokens, ratio={ratio:.2f}%")

# =============================================================================
# STEP 7: REGIME grouping analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: REGIME grouping (1/3 vs 2/4)")
print("=" * 70)

# From LINE_BOUNDARY_OPERATORS: REGIME_1/3 = control-intensive, REGIME_2/4 = output-intensive
group_13 = ['REGIME_1', 'REGIME_3']
group_24 = ['REGIME_2', 'REGIME_4']

def aggregate_groups(data_dict, group_list):
    result = defaultdict(float)
    for regime in group_list:
        if regime in data_dict:
            for key, val in data_dict[regime].items():
                if isinstance(val, (int, float)):
                    result[key] += val
    return dict(result)

# Aggregate suffix stats
suffix_13 = aggregate_groups(regime_suffix_stats, group_13)
suffix_24 = aggregate_groups(regime_suffix_stats, group_24)

print("\n  Suffix patterns (grouped):")
print(f"    REGIME_1/3 (control): High fire {suffix_13.get('high_fire',0)/suffix_13.get('total',1)*100:.1f}%, Low fire {suffix_13.get('low_fire',0)/suffix_13.get('total',1)*100:.1f}%")
print(f"    REGIME_2/4 (output): High fire {suffix_24.get('high_fire',0)/suffix_24.get('total',1)*100:.1f}%, Low fire {suffix_24.get('low_fire',0)/suffix_24.get('total',1)*100:.1f}%")

# Aggregate kernel stats
kernel_13 = aggregate_groups(regime_kernel, group_13)
kernel_24 = aggregate_groups(regime_kernel, group_24)

print(f"\n  Kernel usage (grouped):")
print(f"    REGIME_1/3 (control): {kernel_13.get('kernel',0)/kernel_13.get('total',1)*100:.2f}%")
print(f"    REGIME_2/4 (output): {kernel_24.get('kernel',0)/kernel_24.get('total',1)*100:.2f}%")

# =============================================================================
# STEP 8: Folio illustration types
# =============================================================================
print("\n" + "=" * 70)
print("STEP 8: Folio context (quire, section)")
print("=" * 70)

# Check section distribution by REGIME
folio_sections = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_sections:
        # Get section from first token
        folio_sections[token.folio] = getattr(token, 'section', 'unknown')

regime_sections = defaultdict(Counter)
for folio, section in folio_sections.items():
    if folio in folio_to_regime:
        regime = folio_to_regime[folio]
        regime_sections[regime][section] += 1

print("\n  Section distribution by REGIME:")
for regime in sorted(regime_sections.keys()):
    sections = regime_sections[regime]
    total = sum(sections.values())
    print(f"\n    {regime}:")
    for section, count in sections.most_common():
        pct = count / total * 100 if total else 0
        print(f"      {section}: {count} ({pct:.1f}%)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
REGIME CORRELATION FINDINGS:

1. SUFFIX PATTERNS (Fire-Degree):
   - Check if REGIME_1/3 vs REGIME_2/4 differ in fire-degree suffix usage
   - Higher high-fire ratio might indicate animal/precision processing

2. KERNEL USAGE:
   - Check if control-intensive REGIMEs have different kernel density
   - Kernel (k) is central to intervention

3. VOCABULARY DIVERSITY:
   - Check if output-intensive REGIMEs have different MIDDLE variety
   - More output marking might mean more diverse content

4. SECTION DISTRIBUTION:
   - Check if REGIMEs cluster in certain manuscript sections
   - Could indicate production organization

INTERPRETATION DIRECTIONS:

If REGIME_1/3 (control-intensive) shows:
- Higher kernel usage -> More active intervention needed
- Higher fire-degree -> Processing volatile/animal materials
- Less diverse vocabulary -> Standardized procedures

If REGIME_2/4 (output-intensive) shows:
- Lower kernel usage -> Less intervention needed
- Lower fire-degree -> Processing stable/herb materials
- More diverse vocabulary -> Recording varied outputs
""")
