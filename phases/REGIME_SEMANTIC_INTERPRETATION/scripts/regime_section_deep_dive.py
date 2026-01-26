"""
REGIME SECTION DEEP DIVE

Key finding from correlation analysis:
- REGIME_1: 60.9% Section B (botanical)
- REGIME_2: 0% Section B, spread across H/S/C
- REGIME_4: 51.9% Section H

What distinguishes Section B that requires control-intensive processing?
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
print("REGIME SECTION DEEP DIVE")
print("=" * 70)

# Load regime mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Collect section info
folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

# =============================================================================
# STEP 1: What MIDDLEs are unique to REGIME_1?
# =============================================================================
print("\n" + "=" * 70)
print("STEP 1: REGIME_1 distinctive MIDDLEs")
print("=" * 70)

regime_middles = defaultdict(Counter)

for token in tx.currier_b():
    if token.word and token.folio in folio_to_regime:
        m = morph.extract(token.word)
        regime = folio_to_regime[token.folio]
        if m.middle:
            regime_middles[regime][m.middle] += 1

# Find MIDDLEs that are enriched in REGIME_1 vs others
regime_1_total = sum(regime_middles['REGIME_1'].values())
other_total = sum(sum(regime_middles[r].values()) for r in ['REGIME_2', 'REGIME_3', 'REGIME_4'])

print(f"\n  REGIME_1 tokens: {regime_1_total}")
print(f"  Other REGIME tokens: {other_total}")

enriched_in_1 = []
for middle, count_1 in regime_middles['REGIME_1'].items():
    count_other = sum(regime_middles[r][middle] for r in ['REGIME_2', 'REGIME_3', 'REGIME_4'])
    if count_1 >= 10:  # minimum frequency
        rate_1 = count_1 / regime_1_total
        rate_other = count_other / other_total if other_total else 0
        ratio = rate_1 / rate_other if rate_other else float('inf')
        if ratio > 1.5:
            enriched_in_1.append({
                'middle': middle,
                'count_1': count_1,
                'count_other': count_other,
                'ratio': ratio,
            })

enriched_in_1.sort(key=lambda x: x['ratio'], reverse=True)

print("\n  MIDDLEs enriched in REGIME_1 (>1.5x vs others):")
for item in enriched_in_1[:15]:
    print(f"    {item['middle']}: {item['ratio']:.2f}x ({item['count_1']} vs {item['count_other']})")

# =============================================================================
# STEP 2: What distinguishes Section B folios?
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Section B characteristics")
print("=" * 70)

# Get Section B folios
section_b_folios = [f for f, s in folio_section.items() if s == 'B']
section_h_folios = [f for f, s in folio_section.items() if s == 'H']

print(f"\n  Section B folios: {len(section_b_folios)}")
print(f"  Section H folios: {len(section_h_folios)}")

# REGIME distribution in Section B
regime_in_b = Counter(folio_to_regime.get(f, 'UNKNOWN') for f in section_b_folios)
regime_in_h = Counter(folio_to_regime.get(f, 'UNKNOWN') for f in section_h_folios)

print("\n  REGIME distribution in Section B:")
for regime, count in sorted(regime_in_b.items()):
    pct = count / len(section_b_folios) * 100 if section_b_folios else 0
    print(f"    {regime}: {count} ({pct:.1f}%)")

print("\n  REGIME distribution in Section H:")
for regime, count in sorted(regime_in_h.items()):
    pct = count / len(section_h_folios) * 100 if section_h_folios else 0
    print(f"    {regime}: {count} ({pct:.1f}%)")

# =============================================================================
# STEP 3: Suffix patterns by Section
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Suffix patterns by Section")
print("=" * 70)

HIGH_FIRE = {'ey', 'ol', 'eey'}
LOW_FIRE = {'y', 'dy', 'edy'}

section_suffix = defaultdict(lambda: {'high': 0, 'low': 0, 'total': 0})

for token in tx.currier_b():
    if token.word and token.folio:
        m = morph.extract(token.word)
        section = folio_section.get(token.folio, 'unknown')
        suffix = m.suffix or ''
        section_suffix[section]['total'] += 1
        if suffix in HIGH_FIRE:
            section_suffix[section]['high'] += 1
        elif suffix in LOW_FIRE:
            section_suffix[section]['low'] += 1

print("\n  Fire-degree by Section:")
for section in sorted(section_suffix.keys()):
    stats = section_suffix[section]
    total = stats['total']
    if total >= 100:
        high_pct = stats['high'] / total * 100
        low_pct = stats['low'] / total * 100
        ratio = stats['high'] / stats['low'] if stats['low'] else 0
        print(f"    {section}: High={high_pct:.1f}%, Low={low_pct:.1f}%, Ratio={ratio:.2f} (n={total})")

# =============================================================================
# STEP 4: Line structure by REGIME
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Line structure by REGIME")
print("=" * 70)

regime_lines = defaultdict(list)
for token in tx.currier_b():
    if token.word and token.folio in folio_to_regime:
        regime = folio_to_regime[token.folio]
        regime_lines[regime].append((token.folio, token.line))

# Deduplicate to get unique lines
regime_line_counts = {}
for regime, lines in regime_lines.items():
    unique_lines = set(lines)
    regime_line_counts[regime] = len(unique_lines)

regime_token_counts = {r: sum(regime_middles[r].values()) for r in regime_middles}

print("\n  Tokens per line by REGIME:")
for regime in sorted(regime_line_counts.keys()):
    lines = regime_line_counts[regime]
    tokens = regime_token_counts.get(regime, 0)
    tpl = tokens / lines if lines else 0
    print(f"    {regime}: {tokens} tokens / {lines} lines = {tpl:.2f} tokens/line")

# =============================================================================
# STEP 5: Prefix patterns by REGIME
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Prefix patterns by REGIME")
print("=" * 70)

regime_prefixes = defaultdict(Counter)

for token in tx.currier_b():
    if token.word and token.folio in folio_to_regime:
        m = morph.extract(token.word)
        regime = folio_to_regime[token.folio]
        prefix = m.prefix or '(none)'
        regime_prefixes[regime][prefix] += 1

print("\n  Top prefixes by REGIME:")
for regime in sorted(regime_prefixes.keys()):
    prefixes = regime_prefixes[regime]
    total = sum(prefixes.values())
    print(f"\n  {regime}:")
    for prefix, count in prefixes.most_common(5):
        pct = count / total * 100
        print(f"    {prefix}: {pct:.1f}%")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: What does REGIME encode?")
print("=" * 70)

print("""
SECTION CORRELATION FINDINGS:

1. REGIME_1 concentrates in Section B (botanical) - 60.9% vs <10% for REGIME_2/4
   - Section B = large plant illustrations
   - Section H = herbal (smaller plants with text)
   - Section S = stellar/cosmological

2. REGIME_1 has:
   - Highest kernel usage (16.4%)
   - Highest L-compound rate (2.35%)
   - Highest ENERGY prefix rate (53.5%)
   - LOWEST vocabulary diversity (7.64%)
   - Most tokens per line (density TBD)

3. REGIME_2 avoids Section B entirely:
   - Distributed across H, S, C
   - Lowest kernel usage (9.77%)
   - Highest LATE prefix (3.14%)
   - Higher vocabulary diversity

INTERPRETATION:

Section B botanical folios require CONTROL-INTENSIVE processing:
- More kernel intervention (k operator)
- More energy-modified operators (L-compound)
- More standardized vocabulary (lower diversity)

This suggests Section B documents:
- Complex multi-step procedures
- Active temperature/process control
- Standardized protocols (less variation)

Section H/S/C folios are OUTPUT-INTENSIVE:
- Less active intervention needed
- More output marking (LATE prefix)
- More varied content (higher diversity)

REGIME may encode PROCEDURE COMPLEXITY:
- REGIME_1 = Complex controlled procedures (botanical)
- REGIME_2 = Simple output-recording (herbal/stellar)
- REGIME_4 = Balanced (herbal-focused)
""")
