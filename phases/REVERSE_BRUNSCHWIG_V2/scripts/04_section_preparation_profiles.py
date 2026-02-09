"""
Test 4: Section-Specific Preparation Profiles

Question: Do different sections (HERBAL_B, BIO, PHARMA) show different preparation signatures?

Hypothesis: Different material types require different preparation:
- HERBAL_B: Standard herb processing (chop, macerate)
- BIO: Animal material requires different prep (possibly more complex)
- PHARMA: Root processing (different mechanical prep)

Method:
1. Compute EARLY tier (prep) MIDDLE density per section
2. Compute specific prep MIDDLE profiles per section
3. Test if sections differ significantly
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Define tiers
EARLY_MIDDLES = {'ksh', 'lch', 'tch', 'pch', 'te'}
MID_MIDDLES = {'k', 't', 'e'}
LATE_MIDDLES = {'ke', 'kch'}

# Section mapping (from constraint system)
SECTION_MAP = {
    'HERBAL_B': {'f102v', 'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v', 'f106r', 'f106v',
                 'f107r', 'f107v', 'f108r', 'f108v', 'f111r', 'f111v', 'f112r', 'f112v'},
    'BIO': {'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v', 'f79r', 'f79v',
            'f80r', 'f80v', 'f81r', 'f81v', 'f82r', 'f82v', 'f83r', 'f83v', 'f84r', 'f84v'},
    'PHARMA': {'f88r', 'f88v', 'f89r1', 'f89r2', 'f89v1', 'f89v2', 'f90r1', 'f90r2', 'f90v1', 'f90v2',
               'f99r', 'f99v', 'f100r', 'f100v', 'f101r', 'f101v', 'f102r'}
}

def get_section(folio):
    for section, folios in SECTION_MAP.items():
        if folio in folios:
            return section
    return 'OTHER'

# Group by section
section_stats = defaultdict(lambda: {
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

    section = get_section(t.folio)
    section_stats[section]['total'] += 1
    section_stats[section]['folios'].add(t.folio)

    if m.middle in EARLY_MIDDLES:
        section_stats[section]['early'][m.middle] += 1
        section_stats[section]['early_total'] += 1
    elif m.middle in MID_MIDDLES:
        section_stats[section]['mid'][m.middle] += 1
        section_stats[section]['mid_total'] += 1
    elif m.middle in LATE_MIDDLES:
        section_stats[section]['late'][m.middle] += 1
        section_stats[section]['late_total'] += 1

print("=" * 70)
print("TEST 4: SECTION-SPECIFIC PREPARATION PROFILES")
print("=" * 70)
print()
print("Question: Do sections differ in preparation MIDDLE usage?")
print()

print("TIER DENSITY BY SECTION:")
print("-" * 70)
print(f"{'Section':<12} {'Folios':<8} {'N':<8} {'EARLY %':<12} {'MID %':<12} {'LATE %':<12}")
print("-" * 70)

results = []
for section in ['HERBAL_B', 'BIO', 'PHARMA', 'OTHER']:
    data = section_stats[section]
    n = data['total']
    if n == 0:
        continue
    early_pct = data['early_total'] / n * 100
    mid_pct = data['mid_total'] / n * 100
    late_pct = data['late_total'] / n * 100

    print(f"{section:<12} {len(data['folios']):<8} {n:<8} {early_pct:<12.2f} {mid_pct:<12.2f} {late_pct:<12.2f}")
    results.append({
        'section': section,
        'n_folios': len(data['folios']),
        'n_tokens': n,
        'early_pct': early_pct,
        'mid_pct': mid_pct,
        'late_pct': late_pct
    })

print()

# Specific prep MIDDLE profiles
print("SPECIFIC PREPARATION MIDDLEs BY SECTION:")
print("-" * 70)
print(f"{'Section':<12} {'ksh':<8} {'lch':<8} {'tch':<8} {'pch':<8} {'te':<8}")
print("-" * 70)

prep_profiles = []
for section in ['HERBAL_B', 'BIO', 'PHARMA', 'OTHER']:
    data = section_stats[section]
    n = data['total']
    if n == 0:
        continue
    profile = {}
    row = f"{section:<12}"
    for mid in ['ksh', 'lch', 'tch', 'pch', 'te']:
        pct = data['early'][mid] / n * 100 if n > 0 else 0
        row += f" {pct:<7.2f}"
        profile[mid] = pct
    print(row)
    prep_profiles.append({'section': section, 'profile': profile})

print()

# Chi-square test
from scipy import stats
import numpy as np

# Build contingency table for sections x tiers
sections = ['HERBAL_B', 'BIO', 'PHARMA']
observed = []
for section in sections:
    data = section_stats[section]
    if data['total'] > 0:
        observed.append([data['early_total'], data['mid_total'], data['late_total']])

if len(observed) >= 2:
    observed = np.array(observed)
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    print("CHI-SQUARE TEST (Section x Tier):")
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

herbal = next((r for r in results if r['section'] == 'HERBAL_B'), None)
bio = next((r for r in results if r['section'] == 'BIO'), None)
pharma = next((r for r in results if r['section'] == 'PHARMA'), None)

if herbal and bio:
    early_diff = bio['early_pct'] - herbal['early_pct']
    print(f"  BIO vs HERBAL_B (EARLY prep): {early_diff:+.2f}% (BIO {'more' if early_diff > 0 else 'less'} prep)")

if herbal and pharma:
    early_diff = pharma['early_pct'] - herbal['early_pct']
    print(f"  PHARMA vs HERBAL_B (EARLY prep): {early_diff:+.2f}%")

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
    print("\nInterpretation: Sections show significantly different preparation")
    print("MIDDLE profiles, consistent with different material types requiring")
    print("different preparation operations.")

# Output JSON
output = {
    "test": "Section-Specific Preparation Profiles",
    "question": "Do sections differ in preparation MIDDLE usage?",
    "results": results,
    "prep_profiles": prep_profiles,
    "statistics": {
        "chi_square": chi2,
        "p_value": p_value,
        "cramers_v": cramers_v
    },
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/section_preparation_profiles.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/section_preparation_profiles.json")
