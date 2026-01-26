"""
Q10: BIO-REGIME Correlation

C551 shows REGIME_1 has ENERGY enrichment.
C552 shows BIO section has ENERGY enrichment.
Are these the same phenomenon? Does BIO section = REGIME_1?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Section definition
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'

    if num <= 25:
        return 'HERBAL_A'
    elif num <= 56:
        return 'HERBAL_B'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 73:
        return 'ASTRO'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    elif num <= 102:
        return 'RECIPE_A'
    else:
        return 'RECIPE_B'

# Role mapping
ENERGY_CLASSES = {8, 31, 32, 33, 34, 36}

def is_energy(cls):
    return cls in ENERGY_CLASSES

print("=" * 70)
print("Q10: BIO-REGIME CORRELATION")
print("=" * 70)

# Build folio-level data
folio_data = defaultdict(lambda: {'tokens': 0, 'energy': 0})
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    cls = token_to_class.get(word)
    if cls is not None:
        folio_data[folio]['tokens'] += 1
        if is_energy(cls):
            folio_data[folio]['energy'] += 1

# Add section and REGIME info
for folio in folio_data:
    folio_data[folio]['section'] = get_section(folio)
    folio_data[folio]['regime'] = folio_regime.get(folio, 'UNKNOWN')
    folio_data[folio]['energy_rate'] = folio_data[folio]['energy'] / folio_data[folio]['tokens'] if folio_data[folio]['tokens'] > 0 else 0

print("\n" + "-" * 70)
print("1. SECTION-REGIME CROSS-TABULATION")
print("-" * 70)

# Build contingency table
section_regime = defaultdict(lambda: defaultdict(int))
for folio, data in folio_data.items():
    section_regime[data['section']][data['regime']] += 1

regimes = sorted(set(folio_regime.values()))
sections = ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']

print("\n| Section | " + " | ".join(regimes) + " | Total |")
print("|---------|" + "|".join(["------" for _ in regimes]) + "|-------|")

for section in sections:
    row = f"| {section:8s} |"
    total = sum(section_regime[section].values())
    for regime in regimes:
        count = section_regime[section][regime]
        row += f" {count:4d} |"
    row += f" {total:5d} |"
    print(row)

print("\n" + "-" * 70)
print("2. BIO SECTION REGIME BREAKDOWN")
print("-" * 70)

bio_folios = [f for f, d in folio_data.items() if d['section'] == 'BIO']
bio_regimes = defaultdict(int)
for folio in bio_folios:
    bio_regimes[folio_regime.get(folio, 'UNKNOWN')] += 1

print("\nBIO section folios by REGIME:")
print("| REGIME | Folios | % of BIO |")
print("|--------|--------|----------|")
total_bio = len(bio_folios)
for regime in regimes:
    count = bio_regimes[regime]
    pct = count / total_bio * 100 if total_bio > 0 else 0
    print(f"| {regime} | {count:6d} | {pct:6.1f}%  |")

# Is BIO predominantly REGIME_1?
r1_bio_pct = bio_regimes['REGIME_1'] / total_bio * 100 if total_bio > 0 else 0
print(f"\nBIO is {'PREDOMINANTLY' if r1_bio_pct > 50 else 'NOT predominantly'} REGIME_1 ({r1_bio_pct:.1f}%)")

print("\n" + "-" * 70)
print("3. ENERGY RATE COMPARISON")
print("-" * 70)

# Compare ENERGY rates:
# 1. BIO section (all REGIMEs)
# 2. REGIME_1 (all sections)
# 3. BIO AND REGIME_1
# 4. Non-BIO REGIME_1

bio_energy = [d['energy_rate'] for d in folio_data.values() if d['section'] == 'BIO']
r1_energy = [d['energy_rate'] for d in folio_data.values() if d['regime'] == 'REGIME_1']
bio_r1_energy = [d['energy_rate'] for d in folio_data.values() if d['section'] == 'BIO' and d['regime'] == 'REGIME_1']
non_bio_r1_energy = [d['energy_rate'] for d in folio_data.values() if d['section'] != 'BIO' and d['regime'] == 'REGIME_1']
non_bio_non_r1_energy = [d['energy_rate'] for d in folio_data.values() if d['section'] != 'BIO' and d['regime'] != 'REGIME_1']

print("\n| Category | Folios | Mean EN% | Median EN% |")
print("|----------|--------|----------|------------|")
print(f"| BIO (all)          | {len(bio_energy):6d} | {np.mean(bio_energy)*100:7.1f}% | {np.median(bio_energy)*100:9.1f}% |")
print(f"| REGIME_1 (all)     | {len(r1_energy):6d} | {np.mean(r1_energy)*100:7.1f}% | {np.median(r1_energy)*100:9.1f}% |")
print(f"| BIO + REGIME_1     | {len(bio_r1_energy):6d} | {np.mean(bio_r1_energy)*100 if bio_r1_energy else 0:7.1f}% | {np.median(bio_r1_energy)*100 if bio_r1_energy else 0:9.1f}% |")
print(f"| Non-BIO + REGIME_1 | {len(non_bio_r1_energy):6d} | {np.mean(non_bio_r1_energy)*100:7.1f}% | {np.median(non_bio_r1_energy)*100:9.1f}% |")
print(f"| Non-BIO + Non-R1   | {len(non_bio_non_r1_energy):6d} | {np.mean(non_bio_non_r1_energy)*100:7.1f}% | {np.median(non_bio_non_r1_energy)*100:9.1f}% |")

print("\n" + "-" * 70)
print("4. INDEPENDENCE TEST")
print("-" * 70)

# Question: Is ENERGY enrichment due to SECTION or REGIME?
# Use 2-way ANOVA approach: compare means across groups

# Test 1: BIO vs Non-BIO within REGIME_1
if non_bio_r1_energy and bio_r1_energy:
    stat, p = stats.mannwhitneyu(bio_r1_energy, non_bio_r1_energy, alternative='two-sided')
    print(f"\nWithin REGIME_1: BIO vs Non-BIO ENERGY rate")
    print(f"  BIO mean: {np.mean(bio_r1_energy)*100:.1f}%")
    print(f"  Non-BIO mean: {np.mean(non_bio_r1_energy)*100:.1f}%")
    print(f"  Mann-Whitney: U={stat:.0f}, p={p:.4f}")
    print(f"  -> {'SIGNIFICANT' if p < 0.05 else 'Not significant'}: BIO effect {'exists' if p < 0.05 else 'does not exist'} within REGIME_1")

# Test 2: REGIME_1 vs Non-REGIME_1 within BIO
bio_non_r1_energy = [d['energy_rate'] for d in folio_data.values() if d['section'] == 'BIO' and d['regime'] != 'REGIME_1']
if bio_non_r1_energy and bio_r1_energy:
    stat, p = stats.mannwhitneyu(bio_r1_energy, bio_non_r1_energy, alternative='two-sided')
    print(f"\nWithin BIO: REGIME_1 vs Non-REGIME_1 ENERGY rate")
    print(f"  REGIME_1 mean: {np.mean(bio_r1_energy)*100:.1f}%")
    print(f"  Non-REGIME_1 mean: {np.mean(bio_non_r1_energy)*100:.1f}%")
    print(f"  Mann-Whitney: U={stat:.0f}, p={p:.4f}")
    print(f"  -> {'SIGNIFICANT' if p < 0.05 else 'Not significant'}: REGIME effect {'exists' if p < 0.05 else 'does not exist'} within BIO")

# Test 3: Overall independence (non-BIO non-R1 baseline)
print(f"\nBaseline comparison:")
print(f"  Non-BIO Non-R1: {np.mean(non_bio_non_r1_energy)*100:.1f}% ENERGY")
print(f"  Non-BIO REGIME_1: {np.mean(non_bio_r1_energy)*100:.1f}% ENERGY (+{(np.mean(non_bio_r1_energy)-np.mean(non_bio_non_r1_energy))*100:.1f}pp from REGIME)")
print(f"  BIO Non-R1: {np.mean(bio_non_r1_energy)*100 if bio_non_r1_energy else 0:.1f}% ENERGY (+{(np.mean(bio_non_r1_energy)-np.mean(non_bio_non_r1_energy))*100 if bio_non_r1_energy else 0:.1f}pp from SECTION)")

print("\n" + "-" * 70)
print("5. FOLIO-LEVEL DETAIL")
print("-" * 70)

print("\nBIO section folios:")
print("| Folio | REGIME | Tokens | ENERGY | EN% |")
print("|-------|--------|--------|--------|-----|")
for folio in sorted(bio_folios):
    data = folio_data[folio]
    regime = data['regime']
    tokens = data['tokens']
    energy = data['energy']
    en_rate = data['energy_rate'] * 100
    print(f"| {folio:5s} | {regime} | {tokens:6d} | {energy:6d} | {en_rate:3.0f}% |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Determine if effects are independent
baseline = np.mean(non_bio_non_r1_energy) * 100
regime_effect = (np.mean(non_bio_r1_energy) - np.mean(non_bio_non_r1_energy)) * 100
section_effect = (np.mean(bio_non_r1_energy) - np.mean(non_bio_non_r1_energy)) * 100 if bio_non_r1_energy else 0

print(f"""
1. BIO SECTION REGIME COMPOSITION:
   - BIO is {'PRIMARILY' if r1_bio_pct > 50 else 'NOT primarily'} REGIME_1 ({r1_bio_pct:.0f}% of BIO folios)

2. ENERGY EFFECTS (additive model):
   - Baseline (non-BIO, non-R1): {baseline:.1f}%
   - REGIME_1 effect: +{regime_effect:.1f} percentage points
   - BIO section effect: +{section_effect:.1f} percentage points

3. INDEPENDENCE:
   - BIO and REGIME_1 ENERGY enrichments are {'INDEPENDENT' if abs(regime_effect) > 2 and abs(section_effect) > 2 else 'CONFOUNDED'}
   - Both factors contribute to observed ENERGY patterns
""")

# Save results
results = {
    'bio_regime_composition': dict(bio_regimes),
    'energy_rates': {
        'bio_all': float(np.mean(bio_energy)),
        'regime1_all': float(np.mean(r1_energy)),
        'bio_regime1': float(np.mean(bio_r1_energy)) if bio_r1_energy else None,
        'non_bio_regime1': float(np.mean(non_bio_r1_energy)),
        'baseline': float(np.mean(non_bio_non_r1_energy))
    },
    'effects': {
        'regime_effect': float(regime_effect),
        'section_effect': float(section_effect)
    }
}

with open(RESULTS / 'bio_regime_correlation.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'bio_regime_correlation.json'}")
