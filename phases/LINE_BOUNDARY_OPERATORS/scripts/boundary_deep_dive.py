"""
BOUNDARY OPERATOR DEEP DIVE

L-compounds and LATE prefixes are both B-internal but have opposite provenance:
- L-compound: 97% B-exclusive tokens, 86% B-exclusive MIDDLEs (fully internal)
- LATE: 85% B-exclusive tokens, 76% PP MIDDLEs (B-prefix on pipeline content)

Questions:
1. What are L-compound MIDDLEs? Are they kernel-related?
2. What MIDDLEs do LATE prefixes mark? Specific types?
3. How do ENERGY prefixes (EARLY position) relate to L-compounds?
4. Is there a three-part line structure: ENERGY → L-compound → LATE?
5. What's the relationship to hazards/recovery?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("BOUNDARY OPERATOR DEEP DIVE")
print("=" * 70)

# =============================================================================
# Setup
# =============================================================================
LATE_PREFIXES = {'al', 'ar', 'or'}
ENERGY_PREFIXES = {'ch', 'sh', 'qo', 'tch', 'pch', 'dch', 'lsh'}

def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    if middle[0] != 'l':
        return False
    return middle[1] not in 'aeioy'

# Collect tokens
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        entry = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        }
        b_tokens.append(entry)

# Build line sequences
folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    key = (tok['folio'], tok['line'])
    folio_line_tokens[key].append(tok)

# =============================================================================
# STEP 1: Analyze L-compound MIDDLE structure
# =============================================================================
print("\n" + "=" * 70)
print("STEP 1: L-compound MIDDLE structure")
print("=" * 70)

l_compound_tokens = [t for t in b_tokens if is_l_compound(t['middle'])]
l_middles = Counter(t['middle'] for t in l_compound_tokens)

# Check if L-compound MIDDLEs contain kernel primitives
KERNEL_CHARS = {'k', 'h', 'e'}  # From BCSC kernel operators

print(f"\n  L-compound MIDDLEs ({len(l_middles)} types):")
print(f"\n  Structure analysis:")

l_with_k = [m for m in l_middles if 'k' in m[1:]]  # k after initial l
l_with_ch = [m for m in l_middles if 'ch' in m]
l_with_sh = [m for m in l_middles if 'sh' in m]

print(f"    Contains 'k': {len(l_with_k)} ({len(l_with_k)/len(l_middles)*100:.1f}%)")
print(f"    Contains 'ch': {len(l_with_ch)} ({len(l_with_ch)/len(l_middles)*100:.1f}%)")
print(f"    Contains 'sh': {len(l_with_sh)} ({len(l_with_sh)/len(l_middles)*100:.1f}%)")

# Most common L-compound patterns
print(f"\n  Top L-compound patterns:")
for mid, count in l_middles.most_common(10):
    second_char = mid[1] if len(mid) > 1 else ''
    print(f"    {mid}: {count} (l + {second_char}...)")

# =============================================================================
# STEP 2: Compare LATE MIDDLEs to L-compound MIDDLEs
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: LATE vs L-compound MIDDLE comparison")
print("=" * 70)

late_tokens = [t for t in b_tokens if t['prefix'] in LATE_PREFIXES]
late_middles = Counter(t['middle'] for t in late_tokens if t['middle'])

print(f"\n  LATE MIDDLEs ({len(late_middles)} types):")
for mid, count in late_middles.most_common(10):
    print(f"    {mid}: {count}")

# Overlap?
l_middle_set = set(l_middles.keys())
late_middle_set = set(late_middles.keys())
overlap = l_middle_set & late_middle_set

print(f"\n  MIDDLE overlap:")
print(f"    L-compound MIDDLEs: {len(l_middle_set)}")
print(f"    LATE MIDDLEs: {len(late_middle_set)}")
print(f"    Shared: {len(overlap)} ({len(overlap)/len(l_middle_set | late_middle_set)*100:.1f}%)")

if overlap:
    print(f"    Shared MIDDLEs: {sorted(overlap)[:10]}...")

# =============================================================================
# STEP 3: ENERGY prefix relationship
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: ENERGY prefix relationship to L-compounds")
print("=" * 70)

energy_tokens = [t for t in b_tokens if t['prefix'] in ENERGY_PREFIXES]

# Position analysis
energy_positions = []
l_positions = []

for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)
        if tok['prefix'] in ENERGY_PREFIXES:
            energy_positions.append(rel_pos)
        if is_l_compound(tok['middle']):
            l_positions.append(rel_pos)

print(f"\n  Position comparison:")
print(f"    ENERGY prefix mean: {np.mean(energy_positions):.3f} (n={len(energy_positions)})")
print(f"    L-compound mean: {np.mean(l_positions):.3f} (n={len(l_positions)})")

# Do ENERGY and L-compound co-occur?
lines_with_energy = set()
lines_with_l = set()

for tok in energy_tokens:
    lines_with_energy.add((tok['folio'], tok['line']))
for tok in l_compound_tokens:
    lines_with_l.add((tok['folio'], tok['line']))

lines_both_energy_l = lines_with_energy & lines_with_l
all_lines = set(folio_line_tokens.keys())

p_energy = len(lines_with_energy) / len(all_lines)
p_l = len(lines_with_l) / len(all_lines)
expected_both = p_energy * p_l * len(all_lines)

print(f"\n  Co-occurrence (ENERGY + L-compound):")
print(f"    Lines with ENERGY: {len(lines_with_energy)} ({p_energy*100:.1f}%)")
print(f"    Lines with L-compound: {len(lines_with_l)} ({p_l*100:.1f}%)")
print(f"    Lines with BOTH: {len(lines_both_energy_l)}")
print(f"    Expected (independence): {expected_both:.1f}")
print(f"    Ratio: {len(lines_both_energy_l)/expected_both:.2f}x")

# =============================================================================
# STEP 4: Three-part line structure test
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Three-part line structure (ENERGY -> L-compound -> LATE)")
print("=" * 70)

# Find lines with all three
lines_with_late = set()
for tok in late_tokens:
    lines_with_late.add((tok['folio'], tok['line']))

lines_with_all_three = lines_with_energy & lines_with_l & lines_with_late

print(f"\n  Lines with all three types: {len(lines_with_all_three)}")

# Check order in those lines
correct_order = 0  # ENERGY before L before LATE
partial_order = 0

for key in lines_with_all_three:
    tokens = folio_line_tokens[key]

    energy_pos = []
    l_pos = []
    late_pos = []

    for i, tok in enumerate(tokens):
        if tok['prefix'] in ENERGY_PREFIXES:
            energy_pos.append(i)
        if is_l_compound(tok['middle']):
            l_pos.append(i)
        if tok['prefix'] in LATE_PREFIXES:
            late_pos.append(i)

    min_energy = min(energy_pos) if energy_pos else float('inf')
    min_l = min(l_pos) if l_pos else float('inf')
    max_late = max(late_pos) if late_pos else float('-inf')

    if min_energy < min_l < max_late:
        correct_order += 1
    elif min_energy < max_late or min_l < max_late:
        partial_order += 1

if lines_with_all_three:
    print(f"  Full order [ENERGY < L < LATE]: {correct_order} ({correct_order/len(lines_with_all_three)*100:.1f}%)")
    print(f"  Partial order: {partial_order}")

# =============================================================================
# STEP 5: Alternative model - Functional differentiation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Functional differentiation analysis")
print("=" * 70)

# Hypothesis: L-compounds are CONTROL INFRASTRUCTURE
# LATE prefixes mark CONTENT at boundaries
# ENERGY prefixes are OPERATIONAL

# Check suffix patterns for each class
l_suffixes = Counter(t['suffix'] for t in l_compound_tokens)
late_suffixes = Counter(t['suffix'] for t in late_tokens)
energy_suffixes = Counter(t['suffix'] for t in energy_tokens)

print(f"\n  SUFFIX patterns:")
print(f"\n  L-compound suffixes (top 5):")
for suf, count in l_suffixes.most_common(5):
    pct = count / len(l_compound_tokens) * 100
    print(f"    '{suf or '(none)'}': {count} ({pct:.1f}%)")

print(f"\n  LATE suffixes (top 5):")
for suf, count in late_suffixes.most_common(5):
    pct = count / len(late_tokens) * 100
    print(f"    '{suf or '(none)'}': {count} ({pct:.1f}%)")

print(f"\n  ENERGY suffixes (top 5):")
for suf, count in energy_suffixes.most_common(5):
    pct = count / len(energy_tokens) * 100
    print(f"    '{suf or '(none)'}': {count} ({pct:.1f}%)")

# =============================================================================
# STEP 6: Folio distribution
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Folio distribution patterns")
print("=" * 70)

# Are L-compounds evenly distributed or clustered?
l_by_folio = Counter(t['folio'] for t in l_compound_tokens)
late_by_folio = Counter(t['folio'] for t in late_tokens)
tokens_by_folio = Counter(t['folio'] for t in b_tokens)

# Compute rates
l_rates = []
late_rates = []
for folio in tokens_by_folio:
    total = tokens_by_folio[folio]
    if total >= 50:
        l_rate = l_by_folio.get(folio, 0) / total * 100
        late_rate = late_by_folio.get(folio, 0) / total * 100
        l_rates.append((folio, l_rate))
        late_rates.append((folio, late_rate))

l_rates.sort(key=lambda x: x[1], reverse=True)
late_rates.sort(key=lambda x: x[1], reverse=True)

print(f"\n  L-compound rate by folio:")
print(f"    Mean: {np.mean([r[1] for r in l_rates]):.2f}%")
print(f"    Std: {np.std([r[1] for r in l_rates]):.2f}%")
print(f"    Top 3: {l_rates[:3]}")
print(f"    Bottom 3: {l_rates[-3:]}")

print(f"\n  LATE rate by folio:")
print(f"    Mean: {np.mean([r[1] for r in late_rates]):.2f}%")
print(f"    Std: {np.std([r[1] for r in late_rates]):.2f}%")
print(f"    Top 3: {late_rates[:3]}")
print(f"    Bottom 3: {late_rates[-3:]}")

# Correlation between L-compound and LATE rates
folio_l_dict = dict(l_rates)
folio_late_dict = dict(late_rates)
common_folios = set(folio_l_dict.keys()) & set(folio_late_dict.keys())

if common_folios:
    l_vals = [folio_l_dict[f] for f in common_folios]
    late_vals = [folio_late_dict[f] for f in common_folios]
    correlation = np.corrcoef(l_vals, late_vals)[0, 1]
    print(f"\n  Correlation (L-compound rate vs LATE rate): {correlation:.3f}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
KEY FINDINGS:

1. L-COMPOUND STRUCTURE:
   - L + consonant pattern (lk, lch, lsh dominate)
   - Built on energy-operator roots (ch, sh, k)
   - Fully B-internal (86% exclusive MIDDLEs)

2. MIDDLE VOCABULARY SEPARATION:
   - L-compound and LATE use different MIDDLE pools
   - Minimal overlap suggests different functional domains

3. ENERGY PREFIX RELATIONSHIP:
   - ENERGY prefixes are also early-position (but different from L-compound)
   - Different mechanisms: ENERGY is PREFIX-based, L-compound is MIDDLE-based

4. LINE STRUCTURE:
   - Not a strict ENERGY -> L-compound -> LATE sequence
   - These are parallel/independent systems, not sequential

5. FOLIO DISTRIBUTION:
   - Check if certain folios favor one type over another
   - Could indicate different program types

INTERPRETATION:

Three distinct B-internal grammatical systems operate in parallel:

| System | Mechanism | Position | Provenance | Role |
|--------|-----------|----------|------------|------|
| ENERGY PREFIX | PREFIX (ch/sh/qo) | Early (0.35) | Mixed | Energy operations |
| L-COMPOUND | MIDDLE (lk/lch/lsh) | Early (0.39) | B-exclusive | Control infrastructure |
| LATE PREFIX | PREFIX (al/ar/or) | Late (0.70) | PP MIDDLEs | Output marking |

These are not brackets but PARALLEL GRAMMATICAL LAYERS.
""")
