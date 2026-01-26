"""
Q15: REGIME_3 Homogeneity

From Q12: REGIME_3 has lowest within-REGIME ENERGY variance (4.7% std vs 8-9% for others).
Why is REGIME_3 so internally consistent?
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

# Role mapping
ROLE_MAP = {
    10: 'CC', 11: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

def get_role(cls):
    if cls is None:
        return 'UN'
    return ROLE_MAP.get(cls, 'AX')

# Section definition
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    else:
        return 'RECIPE'

print("=" * 70)
print("Q15: REGIME_3 HOMOGENEITY")
print("=" * 70)

# Build folio-level data
folio_data = defaultdict(lambda: {'tokens': 0, 'classes': defaultdict(int), 'roles': defaultdict(int)})

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    cls = token_to_class.get(word)
    role = get_role(cls)

    folio_data[folio]['tokens'] += 1
    if cls is not None:
        folio_data[folio]['classes'][cls] += 1
    folio_data[folio]['roles'][role] += 1

# Add metadata
for folio in folio_data:
    folio_data[folio]['regime'] = folio_regime.get(folio, 'UNKNOWN')
    folio_data[folio]['section'] = get_section(folio)
    total = folio_data[folio]['tokens']
    folio_data[folio]['energy_rate'] = sum(folio_data[folio]['classes'].get(c, 0) for c in [8,31,32,33,34,36]) / total if total > 0 else 0

# 1. REGIME COMPOSITION
print("\n" + "-" * 70)
print("1. REGIME COMPOSITION")
print("-" * 70)

regime_folios = defaultdict(list)
for folio, data in folio_data.items():
    regime_folios[data['regime']].append(folio)

print("\n| REGIME | Folios | Tokens | Sections |")
print("|--------|--------|--------|----------|")

for regime in sorted(regime_folios.keys()):
    folios = regime_folios[regime]
    tokens_count = sum(folio_data[f]['tokens'] for f in folios)
    sections = set(folio_data[f]['section'] for f in folios)
    print(f"| {regime} | {len(folios):6d} | {tokens_count:6d} | {', '.join(sorted(sections))} |")

# 2. REGIME_3 FOLIOS
print("\n" + "-" * 70)
print("2. REGIME_3 FOLIOS DETAIL")
print("-" * 70)

r3_folios = regime_folios['REGIME_3']
print(f"\nREGIME_3 folios: {sorted(r3_folios)}")

print("\n| Folio | Section | Tokens | EN% | CC% | FL% | FQ% |")
print("|-------|---------|--------|-----|-----|-----|-----|")

for folio in sorted(r3_folios):
    data = folio_data[folio]
    total = data['tokens']
    en = sum(data['classes'].get(c, 0) for c in [8,31,32,33,34,36]) / total * 100
    cc = sum(data['classes'].get(c, 0) for c in [10,11,17]) / total * 100
    fl = sum(data['classes'].get(c, 0) for c in [7,30,38,40]) / total * 100
    fq = sum(data['classes'].get(c, 0) for c in [9,20,21,23]) / total * 100
    print(f"| {folio:5s} | {data['section']:7s} | {total:6d} | {en:3.0f}% | {cc:3.0f}% | {fl:3.0f}% | {fq:3.0f}% |")

# 3. VARIANCE COMPARISON BY ROLE
print("\n" + "-" * 70)
print("3. WITHIN-REGIME VARIANCE BY ROLE")
print("-" * 70)

roles = ['EN', 'CC', 'FL', 'FQ', 'AX']

print("\n| REGIME | Folios | EN std | CC std | FL std | FQ std | AX std |")
print("|--------|--------|--------|--------|--------|--------|--------|")

regime_role_stds = defaultdict(dict)
for regime in sorted(regime_folios.keys()):
    folios = regime_folios[regime]
    if len(folios) < 3:
        continue

    row = f"| {regime} | {len(folios):6d} |"
    for role in roles:
        if role == 'EN':
            role_classes = [8,31,32,33,34,36]
        elif role == 'CC':
            role_classes = [10,11,17]
        elif role == 'FL':
            role_classes = [7,30,38,40]
        elif role == 'FQ':
            role_classes = [9,20,21,23]
        else:
            role_classes = None

        rates = []
        for f in folios:
            total = folio_data[f]['tokens']
            if role_classes:
                count = sum(folio_data[f]['classes'].get(c, 0) for c in role_classes)
            else:
                count = folio_data[f]['roles'].get(role, 0)
            rates.append(count / total if total > 0 else 0)

        std = np.std(rates) * 100
        regime_role_stds[regime][role] = std
        row += f" {std:5.1f}% |"

    print(row)

# 4. WHAT MAKES REGIME_3 CONSISTENT?
print("\n" + "-" * 70)
print("4. REGIME_3 CONSISTENCY ANALYSIS")
print("-" * 70)

# Is it just small sample size?
print(f"\nREGIME_3 has {len(r3_folios)} folios - small sample could explain low variance")

# Check if REGIME_3 has narrower range
print("\n| REGIME | EN min | EN max | EN range |")
print("|--------|--------|--------|----------|")

for regime in sorted(regime_folios.keys()):
    folios = regime_folios[regime]
    en_rates = [folio_data[f]['energy_rate'] * 100 for f in folios]
    if en_rates:
        print(f"| {regime} | {min(en_rates):5.1f}% | {max(en_rates):5.1f}% | {max(en_rates)-min(en_rates):7.1f}% |")

# 5. SECTION HOMOGENEITY IN REGIME_3
print("\n" + "-" * 70)
print("5. REGIME_3 SECTION COMPOSITION")
print("-" * 70)

r3_sections = defaultdict(list)
for f in r3_folios:
    r3_sections[folio_data[f]['section']].append(f)

print("\n| Section | Folios | EN rates |")
print("|---------|--------|----------|")
for section in sorted(r3_sections.keys()):
    folios = r3_sections[section]
    en_rates = [folio_data[f]['energy_rate'] * 100 for f in folios]
    rates_str = ', '.join(f"{r:.0f}%" for r in en_rates)
    print(f"| {section:7s} | {len(folios):6d} | {rates_str} |")

# 6. COMPARE TO OTHER SMALL REGIMES
print("\n" + "-" * 70)
print("6. SIZE-ADJUSTED COMPARISON")
print("-" * 70)

# Bootstrap variance estimation for fair comparison
print("\nBootstrap variance (sampling 8 folios from each REGIME):")

np.random.seed(42)
n_bootstrap = 1000
bootstrap_vars = defaultdict(list)

for regime in sorted(regime_folios.keys()):
    folios = regime_folios[regime]
    if len(folios) < 8:
        continue

    en_rates = [folio_data[f]['energy_rate'] for f in folios]

    for _ in range(n_bootstrap):
        sample = np.random.choice(en_rates, size=8, replace=False)
        bootstrap_vars[regime].append(np.var(sample))

print("\n| REGIME | Orig Folios | Orig Var | Bootstrap Var (n=8) |")
print("|--------|-------------|----------|---------------------|")

for regime in sorted(bootstrap_vars.keys()):
    folios = regime_folios[regime]
    orig_var = np.var([folio_data[f]['energy_rate'] for f in folios]) * 10000
    boot_var = np.mean(bootstrap_vars[regime]) * 10000
    print(f"| {regime} | {len(folios):11d} | {orig_var:8.1f} | {boot_var:19.1f} |")

# Is REGIME_3's low variance just sample size?
if 'REGIME_3' in bootstrap_vars:
    r3_boot = np.mean(bootstrap_vars['REGIME_3'])
    other_boots = [np.mean(bootstrap_vars[r]) for r in bootstrap_vars if r != 'REGIME_3']
    print(f"\nREGIME_3 bootstrap variance: {r3_boot*10000:.1f}")
    print(f"Other REGIMEs mean bootstrap variance: {np.mean(other_boots)*10000:.1f}")

# 7. CLASS DISTRIBUTION IN REGIME_3
print("\n" + "-" * 70)
print("7. REGIME_3 CLASS DISTRIBUTION")
print("-" * 70)

# Which classes are most consistent in REGIME_3?
r3_class_rates = defaultdict(list)
for f in r3_folios:
    total = folio_data[f]['tokens']
    for cls in folio_data[f]['classes']:
        rate = folio_data[f]['classes'][cls] / total
        r3_class_rates[cls].append(rate)

print("\nMost consistent classes in REGIME_3 (lowest CV):")
print("| Class | Role | Mean Rate | Std | CV |")
print("|-------|------|-----------|-----|-----|")

class_cvs = []
for cls, rates in r3_class_rates.items():
    if len(rates) >= 3:
        mean_rate = np.mean(rates)
        std_rate = np.std(rates)
        cv = std_rate / mean_rate if mean_rate > 0 else 999
        class_cvs.append({'class': cls, 'role': get_role(cls), 'mean': mean_rate, 'std': std_rate, 'cv': cv})

class_cvs.sort(key=lambda x: x['cv'])
for c in class_cvs[:10]:
    print(f"| {c['class']:5d} | {c['role']}   | {c['mean']*100:8.1f}% | {c['std']*100:3.1f}% | {c['cv']:.2f} |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

r3_en_std = regime_role_stds['REGIME_3']['EN']
other_en_stds = [regime_role_stds[r]['EN'] for r in regime_role_stds if r != 'REGIME_3']

print(f"""
1. REGIME_3 ENERGY VARIANCE:
   - REGIME_3 std: {r3_en_std:.1f}%
   - Other REGIMEs mean std: {np.mean(other_en_stds):.1f}%
   - Ratio: {np.mean(other_en_stds)/r3_en_std:.1f}x more variable

2. SAMPLE SIZE:
   - REGIME_3 has only {len(r3_folios)} folios (vs 23-27 for others)
   - Small sample partially explains low variance

3. SECTION CONCENTRATION:
   - REGIME_3 spans: {', '.join(sorted(set(folio_data[f]['section'] for f in r3_folios)))}

4. INTERPRETATION:
   - REGIME_3's homogeneity is partly sample-size artifact
   - But may also reflect narrow operational context
""")

# Save results
results = {
    'regime3_folios': sorted(r3_folios),
    'regime_variances': {r: float(regime_role_stds[r]['EN']) for r in regime_role_stds},
    'regime3_sections': dict(r3_sections),
    'bootstrap_comparison': {r: float(np.mean(bootstrap_vars[r])) for r in bootstrap_vars} if bootstrap_vars else {}
}

with open(RESULTS / 'regime3_homogeneity.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'regime3_homogeneity.json'}")
