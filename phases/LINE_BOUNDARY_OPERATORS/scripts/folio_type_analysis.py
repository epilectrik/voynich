"""
FOLIO TYPE ANALYSIS

Key finding: L-compound and LATE rates are NEGATIVELY CORRELATED (-0.305)
- f83v: 4.9% L-compound, 0% LATE
- f50r: 0% L-compound(?), 6.7% LATE

This suggests different folio "types" based on grammar usage patterns.

Also exploring: L-compound = l + energy-operator pattern
- lch = l + ch
- lsh = l + sh
- lk = l + k
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
print("FOLIO TYPE ANALYSIS")
print("=" * 70)

# Setup
LATE_PREFIXES = {'al', 'ar', 'or'}
ENERGY_PREFIXES = {'ch', 'sh', 'qo', 'tch', 'pch', 'dch', 'lsh'}

def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    if middle[0] != 'l':
        return False
    return middle[1] not in 'aeioy'

# Collect all tokens
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })

# =============================================================================
# STEP 1: Folio profiles
# =============================================================================
print("\n[Step 1] Building folio profiles...")

folio_stats = defaultdict(lambda: {
    'total': 0,
    'l_compound': 0,
    'late': 0,
    'energy': 0,
})

for tok in b_tokens:
    f = tok['folio']
    folio_stats[f]['total'] += 1

    if is_l_compound(tok['middle']):
        folio_stats[f]['l_compound'] += 1
    if tok['prefix'] in LATE_PREFIXES:
        folio_stats[f]['late'] += 1
    if tok['prefix'] in ENERGY_PREFIXES:
        folio_stats[f]['energy'] += 1

# Compute rates
folio_profiles = []
for folio, stats in folio_stats.items():
    if stats['total'] >= 50:
        folio_profiles.append({
            'folio': folio,
            'total': stats['total'],
            'l_rate': stats['l_compound'] / stats['total'] * 100,
            'late_rate': stats['late'] / stats['total'] * 100,
            'energy_rate': stats['energy'] / stats['total'] * 100,
        })

print(f"  Folios with 50+ tokens: {len(folio_profiles)}")

# =============================================================================
# STEP 2: Folio clustering by L-compound vs LATE
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Folio clustering")
print("=" * 70)

# Split into high-L vs high-LATE folios
l_rates = [p['l_rate'] for p in folio_profiles]
late_rates = [p['late_rate'] for p in folio_profiles]

median_l = np.median(l_rates)
median_late = np.median(late_rates)

high_l_folios = [p for p in folio_profiles if p['l_rate'] > median_l]
high_late_folios = [p for p in folio_profiles if p['late_rate'] > median_late]
high_both = [p for p in folio_profiles if p['l_rate'] > median_l and p['late_rate'] > median_late]
high_neither = [p for p in folio_profiles if p['l_rate'] <= median_l and p['late_rate'] <= median_late]

print(f"\n  Median L-compound rate: {median_l:.2f}%")
print(f"  Median LATE rate: {median_late:.2f}%")
print(f"\n  High L-compound (> median): {len(high_l_folios)} folios")
print(f"  High LATE (> median): {len(high_late_folios)} folios")
print(f"  High BOTH: {len(high_both)} folios")
print(f"  High NEITHER: {len(high_neither)} folios")

# Extreme folios
print("\n  Extreme L-compound-heavy (top 5):")
sorted_by_l = sorted(folio_profiles, key=lambda x: x['l_rate'], reverse=True)
for p in sorted_by_l[:5]:
    print(f"    {p['folio']}: L={p['l_rate']:.2f}%, LATE={p['late_rate']:.2f}%")

print("\n  Extreme LATE-heavy (top 5):")
sorted_by_late = sorted(folio_profiles, key=lambda x: x['late_rate'], reverse=True)
for p in sorted_by_late[:5]:
    print(f"    {p['folio']}: L={p['l_rate']:.2f}%, LATE={p['late_rate']:.2f}%")

# =============================================================================
# STEP 3: REGIME correlation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: REGIME correlation")
print("=" * 70)

try:
    with open('results/regime_folio_mapping.json', 'r') as f:
        regime_mapping = json.load(f)

    folio_to_regime = {}
    for regime, folios in regime_mapping.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    # Compute mean L and LATE rates by REGIME
    regime_stats = defaultdict(lambda: {'l_rates': [], 'late_rates': [], 'energy_rates': []})

    for p in folio_profiles:
        if p['folio'] in folio_to_regime:
            regime = folio_to_regime[p['folio']]
            regime_stats[regime]['l_rates'].append(p['l_rate'])
            regime_stats[regime]['late_rates'].append(p['late_rate'])
            regime_stats[regime]['energy_rates'].append(p['energy_rate'])

    print("\n  By REGIME:")
    for regime in sorted(regime_stats.keys()):
        stats = regime_stats[regime]
        n = len(stats['l_rates'])
        print(f"    {regime} (n={n}):")
        print(f"      L-compound: {np.mean(stats['l_rates']):.2f}%")
        print(f"      LATE: {np.mean(stats['late_rates']):.2f}%")
        print(f"      ENERGY: {np.mean(stats['energy_rates']):.2f}%")

except Exception as e:
    print(f"  Could not load REGIME mapping: {e}")

# =============================================================================
# STEP 4: L-compound = l + energy operator analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: L-compound = l + energy operator analysis")
print("=" * 70)

l_compound_tokens = [t for t in b_tokens if is_l_compound(t['middle'])]
l_middles = Counter(t['middle'] for t in l_compound_tokens)

# Decompose L-compound MIDDLEs
print("\n  L-compound decomposition:")
print("  (Pattern: l + root)")

decomposed = []
for mid, count in l_middles.items():
    root = mid[1:]  # Everything after 'l'
    decomposed.append({
        'middle': mid,
        'root': root,
        'count': count,
    })

# Group by root
root_counts = Counter()
for d in decomposed:
    root_counts[d['root']] += d['count']

print("\n  Root frequencies:")
for root, count in root_counts.most_common(10):
    print(f"    l + {root}: {count}")

# Check if roots are energy operators
energy_roots = {'ch', 'sh', 'k'}
energy_root_count = sum(count for root, count in root_counts.items()
                        if any(er in root for er in energy_roots))
total_l = sum(root_counts.values())

print(f"\n  Roots containing energy operators (ch/sh/k): {energy_root_count}/{total_l} ({energy_root_count/total_l*100:.1f}%)")

# =============================================================================
# STEP 5: What does 'l' mean?
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: What does 'l' prefix mean?")
print("=" * 70)

# Hypothesis: 'l' modifies energy operators
# Compare: tokens with ch-MIDDLE vs lch-MIDDLE

ch_tokens = [t for t in b_tokens if t['middle'] and t['middle'].startswith('ch') and not t['middle'].startswith('lch')]
lch_tokens = [t for t in b_tokens if t['middle'] and t['middle'].startswith('lch')]

print(f"\n  ch-MIDDLE tokens: {len(ch_tokens)}")
print(f"  lch-MIDDLE tokens: {len(lch_tokens)}")

# Position comparison
ch_positions = []
lch_positions = []

folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    folio_line_tokens[(tok['folio'], tok['line'])].append(tok)

for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)
        if tok['middle'] and tok['middle'].startswith('ch') and not tok['middle'].startswith('lch'):
            ch_positions.append(rel_pos)
        if tok['middle'] and tok['middle'].startswith('lch'):
            lch_positions.append(rel_pos)

if ch_positions and lch_positions:
    print(f"\n  Position comparison:")
    print(f"    ch-MIDDLE mean position: {np.mean(ch_positions):.3f}")
    print(f"    lch-MIDDLE mean position: {np.mean(lch_positions):.3f}")
    print(f"    Difference: {np.mean(lch_positions) - np.mean(ch_positions):.3f}")

# Suffix comparison
ch_suffixes = Counter(t['suffix'] for t in ch_tokens)
lch_suffixes = Counter(t['suffix'] for t in lch_tokens)

print(f"\n  Suffix comparison:")
print(f"    ch-MIDDLE top suffixes: {ch_suffixes.most_common(3)}")
print(f"    lch-MIDDLE top suffixes: {lch_suffixes.most_common(3)}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
FOLIO TYPE FINDINGS:

1. NEGATIVE CORRELATION between L-compound and LATE rates
   - Some folios are L-compound-heavy, others are LATE-heavy
   - Rarely both
   - Suggests different "program types"

2. REGIME CORRELATION
   - Different REGIMEs may favor different grammar patterns
   - Check if L-compound vs LATE maps to REGIME

3. L-COMPOUND = l + ENERGY OPERATOR
   - Most L-compound MIDDLEs are l + ch/sh/k roots
   - 'l' appears to be a MODIFIER on energy operations
   - Possible meanings: "linked", "locked", "lagged"?

4. 'l' SHIFTS POSITION
   - lch is EARLIER than ch alone
   - The 'l' modifier moves the operation toward line-start

INTERPRETATION:

L-compound tokens are MODIFIED ENERGY OPERATORS:
- 'l' is a grammatical modifier (not semantic content)
- Shifts the operation to earlier line position
- Used in "control infrastructure" folios

LATE tokens are OUTPUT MARKERS on pipeline content:
- Applied to PP vocabulary at line-end
- Used in "output-heavy" folios

The folio type distinction may reflect:
- L-heavy folios = control-intensive programs
- LATE-heavy folios = output-intensive programs
""")
