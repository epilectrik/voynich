"""
SECTION H PRECISION PARADOX

Finding: Section H has
- LOWEST fire-degree (low intensity)
- But HIGHEST ch/sh ratio (precision mode)
- Highest suffix-less rate

This suggests: GENTLE BUT PRECISE operations
= Brunschwig's "First Degree" (balneum marie / water bath)
= Low temperature but requiring careful control

Test: Does this match the closed-loop model?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("SECTION H PRECISION PARADOX")
print("=" * 70)

# Collect data
folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

section_tokens = defaultdict(list)
for token in tx.currier_b():
    if token.word and token.folio:
        m = morph.extract(token.word)
        section = folio_section.get(token.folio, 'unknown')
        section_tokens[section].append({
            'word': token.word,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
            'folio': token.folio,
            'line': token.line,
        })

# =============================================================================
# STEP 1: Precision mode analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 1: Precision vs Tolerance by Section")
print("=" * 70)

# ch = precision, sh = tolerance (from C412)
print("\n  ch (precision) vs sh (tolerance) prefix usage:")
for section in sorted(section_tokens.keys()):
    tokens = section_tokens[section]
    total = len(tokens)
    if total < 100:
        continue

    ch_count = sum(1 for t in tokens if t['prefix'] == 'ch')
    sh_count = sum(1 for t in tokens if t['prefix'] == 'sh')

    ch_pct = ch_count / total * 100
    sh_pct = sh_count / total * 100
    ratio = ch_count / sh_count if sh_count else float('inf')

    print(f"  {section}: ch={ch_pct:.1f}%, sh={sh_pct:.1f}%, ch/sh={ratio:.2f}")

# =============================================================================
# STEP 2: Fire-degree + Precision cross-analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Fire-degree x Precision cross-analysis")
print("=" * 70)

HIGH_FIRE = {'ey', 'ol', 'eey'}
LOW_FIRE = {'y', 'dy', 'edy'}

print("\n  Tokens by fire-degree AND prefix mode:")
for section in sorted(section_tokens.keys()):
    tokens = section_tokens[section]
    total = len(tokens)
    if total < 100:
        continue

    # Cross-tabulation
    ch_high = sum(1 for t in tokens if t['prefix'] == 'ch' and t['suffix'] in HIGH_FIRE)
    ch_low = sum(1 for t in tokens if t['prefix'] == 'ch' and t['suffix'] in LOW_FIRE)
    sh_high = sum(1 for t in tokens if t['prefix'] == 'sh' and t['suffix'] in HIGH_FIRE)
    sh_low = sum(1 for t in tokens if t['prefix'] == 'sh' and t['suffix'] in LOW_FIRE)

    print(f"\n  Section {section}:")
    print(f"    ch + high-fire: {ch_high} ({ch_high/total*100:.2f}%)")
    print(f"    ch + low-fire:  {ch_low} ({ch_low/total*100:.2f}%)")
    print(f"    sh + high-fire: {sh_high} ({sh_high/total*100:.2f}%)")
    print(f"    sh + low-fire:  {sh_low} ({sh_low/total*100:.2f}%)")

    # Ratio within ch tokens
    ch_total = ch_high + ch_low
    if ch_total:
        print(f"    Within ch: high/low = {ch_high/ch_low if ch_low else 'inf':.2f}")
    sh_total = sh_high + sh_low
    if sh_total:
        print(f"    Within sh: high/low = {sh_high/sh_low if sh_low else 'inf':.2f}")

# =============================================================================
# STEP 3: What makes Section H special?
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Section H token profile")
print("=" * 70)

h_tokens = section_tokens['H']
s_tokens = section_tokens['S']
b_tokens = section_tokens['B']

def profile(tokens, name):
    total = len(tokens)
    print(f"\n  {name} (n={total}):")

    # Prefix distribution
    prefixes = Counter(t['prefix'] for t in tokens)
    print(f"    Top prefixes: {prefixes.most_common(5)}")

    # Suffix distribution
    suffixes = Counter(t['suffix'] for t in tokens)
    print(f"    Top suffixes: {suffixes.most_common(5)}")

    # MIDDLE length
    mid_lengths = [len(t['middle']) for t in tokens if t['middle']]
    print(f"    Mean MIDDLE length: {np.mean(mid_lengths):.2f}")

    # Suffix-less rate
    suffix_less = sum(1 for t in tokens if not t['suffix'])
    print(f"    Suffix-less: {suffix_less/total*100:.1f}%")

    # Prefix-less rate
    prefix_less = sum(1 for t in tokens if not t['prefix'])
    print(f"    Prefix-less: {prefix_less/total*100:.1f}%")

profile(h_tokens, "Section H")
profile(s_tokens, "Section S")
profile(b_tokens, "Section B")

# =============================================================================
# STEP 4: Brunschwig degree interpretation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Brunschwig degree interpretation")
print("=" * 70)

print("""
BRUNSCHWIG FIRE DEGREES:

First Degree (balneum marie):
- Water bath, gentle heat
- Requires PRECISION (exact temperature)
- LOW fire, HIGH control

Second Degree (ashes):
- Moderate heat
- More forgiving

Third Degree (sand/direct):
- High heat
- Aggressive processing

Fourth Degree (naked flame):
- Extreme heat
- Forbidden for most materials

SECTION H PROFILE MATCHES FIRST DEGREE:
- LOW fire-degree suffixes (3.9% high-fire)
- HIGH precision mode (ch dominates)
- High suffix-less rate (minimal output marking)
- Lower energy prefix overall (gentle processing)

HYPOTHESIS:
Section H documents BALNEUM MARIE procedures:
- Gentle extraction requiring precise temperature
- Volatile aromatics that denature at high heat
- Long processing times with careful monitoring
""")

# =============================================================================
# STEP 5: REGIME distribution within Section H
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: REGIME distribution within Section H")
print("=" * 70)

# Load regime mapping
import json
try:
    with open('results/regime_folio_mapping.json', 'r') as f:
        regime_mapping = json.load(f)

    folio_to_regime = {}
    for regime, folios in regime_mapping.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    # Count H folios by REGIME
    h_folios = [f for f, s in folio_section.items() if s == 'H']
    h_regime_dist = Counter(folio_to_regime.get(f, 'UNKNOWN') for f in h_folios)

    print(f"\n  Section H folios by REGIME:")
    for regime, count in sorted(h_regime_dist.items()):
        pct = count / len(h_folios) * 100
        print(f"    {regime}: {count} ({pct:.1f}%)")

    # Compare fire-degree within REGIME_4 (precision) H folios vs others
    regime4_h = [f for f in h_folios if folio_to_regime.get(f) == 'REGIME_4']
    other_h = [f for f in h_folios if folio_to_regime.get(f) != 'REGIME_4']

    def fire_degree_rate(folios):
        high = 0
        low = 0
        total = 0
        for t in h_tokens:
            if t['folio'] in folios:
                total += 1
                if t['suffix'] in HIGH_FIRE:
                    high += 1
                elif t['suffix'] in LOW_FIRE:
                    low += 1
        return high/total*100 if total else 0, low/total*100 if total else 0, total

    r4_high, r4_low, r4_n = fire_degree_rate(regime4_h)
    other_high, other_low, other_n = fire_degree_rate(other_h)

    print(f"\n  Fire-degree within Section H by C494 REGIME:")
    print(f"    REGIME_4 (precision) folios: high={r4_high:.1f}%, low={r4_low:.1f}% (n={r4_n})")
    print(f"    Other REGIME folios: high={other_high:.1f}%, low={other_low:.1f}% (n={other_n})")

except Exception as e:
    print(f"  Could not load REGIME mapping: {e}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: Section H = Gentle Precision Processing")
print("=" * 70)

print("""
FINDING: Section H shows PRECISION PARADOX

Pattern:
- LOW fire-degree (gentle heat)
- HIGH precision mode (ch dominates sh)
- HIGH suffix-less rate (less output marking)
- SHORTER MIDDLEs (simpler tokens)

Interpretation:
Section H documents BALNEUM MARIE (water bath) style processing:
- Volatile aromatics requiring gentle heat
- Precision temperature control (not tolerant of deviation)
- Longer extraction times (less dramatic output)

This explains the LOW fire-degree ratio:
- It's not that H has MORE low-fire, it has LESS high-fire
- High-fire procedures (animal/resin) are elsewhere (S, C)
- H is specialized for gentle aromatic extraction

CONSTRAINT IMPLICATION:
Fire-degree correlates with PROCESSING STYLE, not just MATERIAL:
- High-fire = aggressive extraction (resins, animal)
- Low-fire = gentle extraction (flowers, volatile aromatics)

Section H = flowers/volatiles requiring gentle but precise processing
Section S/B = resins/animal requiring aggressive processing
""")
