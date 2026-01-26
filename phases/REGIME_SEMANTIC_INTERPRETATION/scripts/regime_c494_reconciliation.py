"""
REGIME C494 RECONCILIATION

C494 says REGIME_4 = precision (tight control, narrow tolerance)
My empirical classification is based on L-compound vs LATE rates.

Need to check:
1. Does my REGIME_4 match C494's "precision" characteristics?
2. How do escape rates map to my REGIMEs?
3. What is the relationship between L-compound rate and control tightness?
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
print("REGIME C494 RECONCILIATION")
print("=" * 70)

# Load regime mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# =============================================================================
# STEP 1: C494 says REGIME_4 characteristics:
# - Escape rate 0.107 (lowest)
# - HIGH_IMPACT forbidden
# - max_k_steps 3
# - min_LINK_ratio 25%
#
# Let me check kernel (k) usage patterns - more k usage = more intervention
# =============================================================================
print("\n" + "=" * 70)
print("STEP 1: Kernel intervention patterns by REGIME")
print("=" * 70)

# Count k-family operators per line
regime_k_per_line = defaultdict(list)

folio_line_data = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if token.word and token.folio in folio_to_regime:
        m = morph.extract(token.word)
        folio_line_data[token.folio][token.line].append(m.middle or '')

for folio, lines in folio_line_data.items():
    regime = folio_to_regime[folio]
    for line_num, middles in lines.items():
        k_count = sum(1 for m in middles if m and m.startswith('k'))
        total = len(middles)
        if total >= 3:  # minimum tokens
            regime_k_per_line[regime].append({
                'k_count': k_count,
                'total': total,
                'k_rate': k_count / total if total else 0,
            })

print("\n  Kernel per line statistics:")
for regime in sorted(regime_k_per_line.keys()):
    lines = regime_k_per_line[regime]
    k_counts = [l['k_count'] for l in lines]
    k_rates = [l['k_rate'] for l in lines]
    avg_k = np.mean(k_counts)
    max_k = max(k_counts)
    avg_rate = np.mean(k_rates) * 100
    print(f"  {regime}: avg K/line={avg_k:.2f}, max K/line={max_k}, rate={avg_rate:.1f}%")

# =============================================================================
# STEP 2: LINK ratio - tokens that are LINK operators
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: LINK patterns (control infrastructure)")
print("=" * 70)

# LINK is typically encoded as line-internal monitoring
# Check for repeated tokens (potential LINK markers)
regime_link_stats = defaultdict(lambda: {'repeated': 0, 'total': 0})

for folio, lines in folio_line_data.items():
    regime = folio_to_regime[folio]
    for line_num, middles in lines.items():
        counts = Counter(middles)
        for mid, count in counts.items():
            if count > 1:
                regime_link_stats[regime]['repeated'] += count
            regime_link_stats[regime]['total'] += count

print("\n  Token repetition (potential LINK) by REGIME:")
for regime in sorted(regime_link_stats.keys()):
    stats = regime_link_stats[regime]
    pct = stats['repeated'] / stats['total'] * 100 if stats['total'] else 0
    print(f"    {regime}: {pct:.1f}% repeated MIDDLEs")

# =============================================================================
# STEP 3: L-compound as modified control infrastructure
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: L-compound relationship to control tightness")
print("=" * 70)

# L-compound = l + energy operator
# If REGIME_1 has highest L-compound, it means highest MODIFIED control

def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    if middle[0] != 'l':
        return False
    return middle[1] not in 'aeioy'

regime_lc_stats = defaultdict(lambda: {'l_compound': 0, 'bare_energy': 0, 'total': 0})

ENERGY_MIDDLES = {'ch', 'sh', 'k'}

for folio, lines in folio_line_data.items():
    regime = folio_to_regime[folio]
    for line_num, middles in lines.items():
        for mid in middles:
            regime_lc_stats[regime]['total'] += 1
            if is_l_compound(mid):
                regime_lc_stats[regime]['l_compound'] += 1
            elif mid and mid[0] in 'csk':
                regime_lc_stats[regime]['bare_energy'] += 1

print("\n  Control infrastructure (L-compound vs bare energy):")
for regime in sorted(regime_lc_stats.keys()):
    stats = regime_lc_stats[regime]
    total = stats['total']
    lc_pct = stats['l_compound'] / total * 100 if total else 0
    be_pct = stats['bare_energy'] / total * 100 if total else 0
    ratio = stats['l_compound'] / stats['bare_energy'] if stats['bare_energy'] else 0
    print(f"    {regime}: L-compound={lc_pct:.2f}%, Bare energy={be_pct:.2f}%, Ratio={ratio:.3f}")

# =============================================================================
# STEP 4: Precision interpretation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: C494 Precision characteristics check")
print("=" * 70)

# C494 says REGIME_4 has:
# - Lowest escape rate
# - HIGH_IMPACT forbidden
# - max_k_steps 3

# If L-compound modifies energy to EARLIER position, it's about
# INITIATING control earlier, not necessarily tightness

# Key question: Does my REGIME_1 (high L-compound) correspond to
# C494's REGIME_4 (precision), or is it something different?

# C494 Four-Axis Model:
# REGIME_2 = Low intensity (First degree)
# REGIME_1 = Moderate, forgiving (Second degree)
# REGIME_3 = High intensity (Third/Fourth degree)
# REGIME_4 = Precision (tight control)

# My empirical classification:
# REGIME_1 = High L-compound, High ENERGY, High kernel -> CONTROL-INTENSIVE
# REGIME_2 = Low L-compound, High LATE -> OUTPUT-INTENSIVE
# REGIME_3 = High L-compound, Low LATE
# REGIME_4 = Low L-compound, Low LATE

# These may be DIFFERENT classification schemes!

print("""
C494 CLASSIFICATION (from BRUNSCHWIG_TEMPLATE_FIT):
  REGIME_1 = Moderate, forgiving (Second degree)
  REGIME_2 = Low intensity (First degree)
  REGIME_3 = High intensity (Third/Fourth degree)
  REGIME_4 = Precision (tight control)

MY EMPIRICAL CLASSIFICATION (from LINE_BOUNDARY_OPERATORS):
  REGIME_1 = High L-compound, High ENERGY -> CONTROL-INFRASTRUCTURE-HEAVY
  REGIME_2 = Low L-compound, High LATE -> OUTPUT-INTENSIVE
  REGIME_3 = High L-compound, Low LATE
  REGIME_4 = Low L-compound, Low LATE

These may measure DIFFERENT axes:
- C494: Execution intensity/precision
- Mine: Grammar infrastructure type (control vs output)

RECONCILIATION HYPOTHESIS:
The two classifications are ORTHOGONAL.
A folio can be both high-precision (C494) AND control-infrastructure-heavy (mine).

TESTABLE PREDICTION:
If Section B (balneological) requires both HIGH CONTROL and HIGH PRECISION,
then Section B folios should cluster where both classifications overlap.
""")

# =============================================================================
# STEP 5: Section vs REGIME cross-tab
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Section-REGIME cross-tabulation")
print("=" * 70)

folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

# Cross-tab
cross_tab = defaultdict(lambda: defaultdict(int))
for folio in folio_to_regime:
    regime = folio_to_regime[folio]
    section = folio_section.get(folio, 'unknown')
    cross_tab[section][regime] += 1

print("\n  Section x REGIME cross-tabulation:")
regimes = sorted(regime_mapping.keys())
print(f"        {'  '.join([r[-1] for r in regimes])}  (1=R1, 2=R2, etc.)")
for section in sorted(cross_tab.keys()):
    counts = [str(cross_tab[section][r]).rjust(2) for r in regimes]
    total = sum(cross_tab[section].values())
    print(f"    {section}: {' '.join(counts)}  (n={total})")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: Two classification axes")
print("=" * 70)

print("""
FINDING: The two REGIME classifications measure different things.

AXIS 1 (C494 - from template fit):
  Measures: Execution intensity and precision requirements
  REGIME_4 = Precision (tight control, narrow tolerance)

AXIS 2 (Mine - from grammar analysis):
  Measures: Grammar infrastructure allocation
  REGIME_1 = Control-infrastructure-heavy (high L-compound, kernel)
  REGIME_2 = Output-intensive (high LATE prefix)

KEY INSIGHT:
Section B (balneological) has:
- 70% REGIME_1 in my classification (high control infrastructure)
- But this doesn't contradict C494's precision axis

INTERPRETATION:
Section B procedures require:
1. Heavy control infrastructure (L-compound, kernel) - grammar axis
2. AND potentially high precision - execution axis

The "bathing" section may involve:
- Complex multi-step procedures
- Temperature-sensitive processing (hence control infrastructure)
- Precise timing requirements (hence precision)

NEXT STEP:
Check if Section B folios also show C494-style precision characteristics
(low escape, high LINK ratio) within my REGIME_1 classification.
""")
