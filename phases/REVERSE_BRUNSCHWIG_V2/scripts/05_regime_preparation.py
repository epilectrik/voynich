"""
Test 5: REGIME x Preparation Vocabulary

Question: Does REGIME affect preparation MIDDLE usage?

Hypothesis:
- REGIME_4 (precision) may use more preparation (careful setup)
- REGIME_3 (intense/oil) may use less preparation (direct extraction)
- REGIME_2 (gentle) may use specific gentle-prep MIDDLEs

Method:
1. Map folios to REGIMEs (from constraint system)
2. Compute EARLY tier density per REGIME
3. Test if REGIMEs differ significantly
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import os

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Define tiers
EARLY_MIDDLES = {'ksh', 'lch', 'tch', 'pch', 'te'}
MID_MIDDLES = {'k', 't', 'e'}
LATE_MIDDLES = {'ke', 'kch'}

# Try to load REGIME mapping
regime_map = {}
regime_file = 'results/regime_folio_mapping.json'
if os.path.exists(regime_file):
    with open(regime_file) as f:
        data = json.load(f)
        if 'folio_regime' in data:
            regime_map = data['folio_regime']
        elif isinstance(data, dict):
            regime_map = data

# If no file, use approximate mapping from C494
if not regime_map:
    # Approximate REGIME mapping based on sections
    # REGIME_1: Standard water (HERBAL_B early)
    # REGIME_2: Gentle (some HERBAL_B)
    # REGIME_3: Intense/oil (BIO sections)
    # REGIME_4: Precision (PHARMA, some BIO)
    REGIME_APPROX = {
        'REGIME_1': {'f102v', 'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v', 'f106r', 'f106v',
                     'f107r', 'f107v', 'f108r', 'f108v'},
        'REGIME_2': {'f111r', 'f111v', 'f112r', 'f112v', 'f113r', 'f113v', 'f114r', 'f114v'},
        'REGIME_3': {'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v', 'f79r', 'f79v'},
        'REGIME_4': {'f88r', 'f88v', 'f89r1', 'f89r2', 'f89v1', 'f89v2', 'f90r1', 'f90r2',
                     'f99r', 'f99v', 'f100r', 'f100v', 'f101r', 'f101v'}
    }
    for regime, folios in REGIME_APPROX.items():
        for f in folios:
            regime_map[f] = regime

def get_regime(folio):
    return regime_map.get(folio, 'UNKNOWN')

# Group by REGIME
regime_stats = defaultdict(lambda: {
    'early': Counter(),
    'mid': Counter(),
    'late': Counter(),
    'total': 0,
    'early_total': 0,
    'mid_total': 0,
    'late_total': 0,
    'folios': set()
})

for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix and m.prefix in HT_PREFIXES:
        continue
    if not m.middle:
        continue

    regime = get_regime(t.folio)
    regime_stats[regime]['total'] += 1
    regime_stats[regime]['folios'].add(t.folio)

    if m.middle in EARLY_MIDDLES:
        regime_stats[regime]['early'][m.middle] += 1
        regime_stats[regime]['early_total'] += 1
    elif m.middle in MID_MIDDLES:
        regime_stats[regime]['mid'][m.middle] += 1
        regime_stats[regime]['mid_total'] += 1
    elif m.middle in LATE_MIDDLES:
        regime_stats[regime]['late'][m.middle] += 1
        regime_stats[regime]['late_total'] += 1

print("=" * 70)
print("TEST 5: REGIME x PREPARATION VOCABULARY")
print("=" * 70)
print()
print("Question: Does REGIME affect preparation MIDDLE usage?")
print()

print("TIER DENSITY BY REGIME:")
print("-" * 70)
print(f"{'REGIME':<12} {'Folios':<8} {'N':<8} {'EARLY %':<12} {'MID %':<12} {'LATE %':<12}")
print("-" * 70)

results = []
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4', 'UNKNOWN']:
    data = regime_stats[regime]
    n = data['total']
    if n == 0:
        continue
    early_pct = data['early_total'] / n * 100
    mid_pct = data['mid_total'] / n * 100
    late_pct = data['late_total'] / n * 100

    print(f"{regime:<12} {len(data['folios']):<8} {n:<8} {early_pct:<12.2f} {mid_pct:<12.2f} {late_pct:<12.2f}")
    results.append({
        'regime': regime,
        'n_folios': len(data['folios']),
        'n_tokens': n,
        'early_pct': early_pct,
        'mid_pct': mid_pct,
        'late_pct': late_pct
    })

print()

# Specific prep MIDDLE profiles
print("SPECIFIC PREPARATION MIDDLEs BY REGIME:")
print("-" * 70)
print(f"{'REGIME':<12} {'ksh':<8} {'lch':<8} {'tch':<8} {'pch':<8} {'te':<8}")
print("-" * 70)

prep_profiles = []
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    data = regime_stats[regime]
    n = data['total']
    if n == 0:
        continue
    profile = {}
    row = f"{regime:<12}"
    for mid in ['ksh', 'lch', 'tch', 'pch', 'te']:
        pct = data['early'][mid] / n * 100 if n > 0 else 0
        row += f" {pct:<7.2f}"
        profile[mid] = pct
    print(row)
    prep_profiles.append({'regime': regime, 'profile': profile})

print()

# Chi-square test
from scipy import stats
import numpy as np

# Build contingency table for regimes x tiers
regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
observed = []
for regime in regimes:
    data = regime_stats[regime]
    if data['total'] > 0:
        observed.append([data['early_total'], data['mid_total'], data['late_total']])

if len(observed) >= 2:
    observed = np.array(observed)
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    print("CHI-SQUARE TEST (REGIME x Tier):")
    print("-" * 50)
    print(f"  Chi-square: {chi2:.2f}")
    print(f"  df: {dof}")
    print(f"  p-value: {p_value:.6f}")

    # Effect size
    n_total = observed.sum()
    min_dim = min(observed.shape) - 1
    cramers_v = np.sqrt(chi2 / (n_total * min_dim))
    print(f"  Cramer's V: {cramers_v:.3f}")
    print()
else:
    chi2, p_value, cramers_v = None, None, None

# Key comparisons
print("KEY COMPARISONS:")
print("-" * 50)

r4 = next((r for r in results if r['regime'] == 'REGIME_4'), None)
r3 = next((r for r in results if r['regime'] == 'REGIME_3'), None)
r1 = next((r for r in results if r['regime'] == 'REGIME_1'), None)

if r4 and r3:
    early_diff = r4['early_pct'] - r3['early_pct']
    print(f"  REGIME_4 vs REGIME_3 (EARLY prep): {early_diff:+.2f}% (R4 {'more' if early_diff > 0 else 'less'} prep)")

if r4 and r1:
    early_diff = r4['early_pct'] - r1['early_pct']
    print(f"  REGIME_4 vs REGIME_1 (EARLY prep): {early_diff:+.2f}%")

print()

# Verdict
if p_value and p_value < 0.05 and cramers_v and cramers_v > 0.05:
    verdict = "CONFIRMED"
elif p_value and p_value < 0.1:
    verdict = "SUPPORT"
else:
    verdict = "NOT SUPPORTED"

print("=" * 70)
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict in ["CONFIRMED", "SUPPORT"]:
    print("\nInterpretation: REGIMEs show different preparation MIDDLE profiles.")
    print("This is consistent with different fire degrees requiring different")
    print("preparation procedures (gentle vs intense extraction).")

# Output JSON
output = {
    "test": "REGIME x Preparation Vocabulary",
    "question": "Does REGIME affect preparation MIDDLE usage?",
    "results": results,
    "prep_profiles": prep_profiles,
    "statistics": {
        "chi_square": chi2,
        "p_value": p_value,
        "cramers_v": cramers_v
    },
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/regime_preparation.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/regime_preparation.json")
