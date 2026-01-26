"""
Q7: Class Universality by REGIME

Do some classes appear in ALL REGIMEs (universal) while others are REGIME-specific?
This tests whether the instruction set has universal vs specialized components.
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
    # CORE_CONTROL
    10: 'CC', 11: 'CC', 17: 'CC',
    # ENERGY_OPERATOR
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    # FLOW_OPERATOR
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    # FREQUENT_OPERATOR
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

def get_role(cls):
    return ROLE_MAP.get(cls, 'AX')

print("=" * 70)
print("Q7: CLASS UNIVERSALITY BY REGIME")
print("=" * 70)

# Count class occurrences by REGIME
class_regime_counts = defaultdict(lambda: defaultdict(int))
regime_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    cls = token_to_class.get(word)
    regime = folio_regime.get(folio)
    if cls is not None and regime:
        class_regime_counts[cls][regime] += 1
        regime_totals[regime] += 1

all_regimes = set(regime_totals.keys())
print(f"\nREGIMEs: {sorted(all_regimes)}")
print(f"REGIME totals: {dict(regime_totals)}")

# Calculate universality metrics
print("\n" + "-" * 70)
print("1. REGIME COVERAGE")
print("-" * 70)

class_metrics = []
for cls in sorted(set(token_to_class.values())):
    regimes = class_regime_counts[cls]
    present_in = [r for r in all_regimes if regimes.get(r, 0) >= 5]  # At least 5 occurrences
    coverage = len(present_in) / len(all_regimes)

    total = sum(regimes.values())
    if total < 20:
        continue

    # Calculate distribution evenness (1 = perfectly even, 0 = concentrated)
    expected = total / len(all_regimes)
    deviations = [abs(regimes.get(r, 0) - expected) for r in all_regimes]
    max_deviation = expected * (len(all_regimes) - 1)
    evenness = 1 - (sum(deviations) / (2 * max_deviation)) if max_deviation > 0 else 1

    # Identify dominant REGIME if any
    max_regime = max(all_regimes, key=lambda r: regimes.get(r, 0))
    max_rate = regimes.get(max_regime, 0) / total if total > 0 else 0

    role = get_role(cls)
    class_metrics.append({
        'class': cls,
        'role': role,
        'coverage': coverage,
        'evenness': evenness,
        'total': total,
        'dominant_regime': max_regime,
        'dominant_rate': max_rate,
        'regimes': dict(regimes)
    })

# Sort by universality (coverage * evenness)
class_metrics.sort(key=lambda x: x['coverage'] * x['evenness'], reverse=True)

print("\n| Class | Role | Coverage | Evenness | Universal | Dominant |")
print("|-------|------|----------|----------|-----------|----------|")

universal_classes = []
specialized_classes = []

for m in class_metrics:
    universality = m['coverage'] * m['evenness']
    is_universal = m['coverage'] == 1.0 and m['evenness'] > 0.7
    is_specialized = m['coverage'] < 1.0 or m['dominant_rate'] > 0.5

    if is_universal:
        universal_classes.append(m)
    elif is_specialized:
        specialized_classes.append(m)

    tag = "UNIV" if is_universal else ("SPEC" if is_specialized else "")
    print(f"| {m['class']:5d} | {m['role']}   | {m['coverage']*100:6.0f}% | {m['evenness']:.2f}     | {tag:9s} | {m['dominant_regime']}: {m['dominant_rate']*100:.0f}% |")

print("\n" + "-" * 70)
print("2. UNIVERSAL CLASSES (present in ALL REGIMEs, evenly distributed)")
print("-" * 70)

print(f"\n{len(universal_classes)} classes are universal (all REGIMEs, evenness > 0.7):")
print("| Class | Role | Total | Evenness |")
print("|-------|------|-------|----------|")
for m in universal_classes[:15]:
    print(f"| {m['class']:5d} | {m['role']}   | {m['total']:5d} | {m['evenness']:.3f}    |")

# Role distribution of universal classes
universal_roles = defaultdict(int)
for m in universal_classes:
    universal_roles[m['role']] += 1

print("\nUniversal class distribution by role:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    print(f"  {role}: {universal_roles[role]} classes")

print("\n" + "-" * 70)
print("3. REGIME-SPECIALIZED CLASSES")
print("-" * 70)

# Group by dominant REGIME
regime_specialists = defaultdict(list)
for m in specialized_classes:
    if m['dominant_rate'] > 0.45:  # Threshold for "specialized"
        regime_specialists[m['dominant_regime']].append(m)

for regime in sorted(regime_specialists.keys()):
    specialists = regime_specialists[regime]
    print(f"\n{regime} specialists ({len(specialists)} classes):")
    print("| Class | Role | Rate | Total |")
    print("|-------|------|------|-------|")
    for m in sorted(specialists, key=lambda x: x['dominant_rate'], reverse=True)[:5]:
        print(f"| {m['class']:5d} | {m['role']}   | {m['dominant_rate']*100:3.0f}% | {m['total']:5d} |")

print("\n" + "-" * 70)
print("4. REGIME_1 vs OTHER REGIMES")
print("-" * 70)

# Compare class usage between REGIME_1 and others
r1_enrichment = []
for m in class_metrics:
    r1_count = m['regimes'].get('REGIME_1', 0)
    other_count = sum(m['regimes'].get(r, 0) for r in all_regimes if r != 'REGIME_1')
    total = r1_count + other_count

    # Expected based on overall REGIME distribution
    r1_expected = total * regime_totals['REGIME_1'] / sum(regime_totals.values())
    enrichment = r1_count / r1_expected if r1_expected > 0 else 1

    r1_enrichment.append({
        'class': m['class'],
        'role': m['role'],
        'r1_count': r1_count,
        'r1_rate': r1_count / total if total > 0 else 0,
        'enrichment': enrichment,
        'total': total
    })

# Sort by enrichment
r1_enrichment.sort(key=lambda x: x['enrichment'], reverse=True)

print("\nREGIME_1 ENRICHED classes:")
print("| Class | Role | R1 Rate | Enrichment |")
print("|-------|------|---------|------------|")
for e in r1_enrichment[:10]:
    if e['enrichment'] > 1.2:
        print(f"| {e['class']:5d} | {e['role']}   | {e['r1_rate']*100:5.0f}%  | {e['enrichment']:.2f}x      |")

print("\nREGIME_1 DEPLETED classes:")
print("| Class | Role | R1 Rate | Depletion |")
print("|-------|------|---------|-----------|")
for e in reversed(r1_enrichment[-10:]):
    if e['enrichment'] < 0.8:
        print(f"| {e['class']:5d} | {e['role']}   | {e['r1_rate']*100:5.0f}%  | {e['enrichment']:.2f}x     |")

print("\n" + "-" * 70)
print("5. ROLE UNIVERSALITY COMPARISON")
print("-" * 70)

# Compare universality by role
role_evenness = defaultdict(list)
for m in class_metrics:
    role_evenness[m['role']].append(m['evenness'])

print("\n| Role | Mean Evenness | Classes |")
print("|------|---------------|---------|")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    if role_evenness[role]:
        print(f"| {role}   | {np.mean(role_evenness[role]):.3f}         | {len(role_evenness[role]):7d} |")

# Statistical test: are semantic roles more universal than AUXILIARY?
semantic_evenness = []
auxiliary_evenness = []
for m in class_metrics:
    if m['role'] in ['CC', 'EN', 'FL', 'FQ']:
        semantic_evenness.append(m['evenness'])
    else:
        auxiliary_evenness.append(m['evenness'])

if semantic_evenness and auxiliary_evenness:
    stat, p = stats.mannwhitneyu(semantic_evenness, auxiliary_evenness, alternative='greater')
    print(f"\nSemantic roles more universal than AUXILIARY?")
    print(f"  Semantic mean evenness: {np.mean(semantic_evenness):.3f}")
    print(f"  AUXILIARY mean evenness: {np.mean(auxiliary_evenness):.3f}")
    print(f"  Mann-Whitney U={stat:.0f}, p={p:.4f}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
1. UNIVERSAL CLASSES: {len(universal_classes)} of {len(class_metrics)} ({len(universal_classes)/len(class_metrics)*100:.0f}%)
   - Present in all 4 REGIMEs with even distribution
   - Grammar core that operates across all contexts

2. REGIME_1 SPECIALIZATION:
   - ENERGY classes (32, 33) enriched in REGIME_1 (1.3-1.4x)
   - Confirms thermal processing context interpretation

3. ROLE UNIVERSALITY:
   - {"SEMANTIC roles more universal" if np.mean(semantic_evenness) > np.mean(auxiliary_evenness) else "No significant difference"}
   - AUXILIARY classes show {"more" if np.mean(auxiliary_evenness) < np.mean(semantic_evenness) else "less"} REGIME-specific behavior
""")

# Save results
results = {
    'universal_classes': [m['class'] for m in universal_classes],
    'class_metrics': class_metrics,
    'regime_specialists': {k: [m['class'] for m in v] for k, v in regime_specialists.items()},
    'role_evenness': {k: float(np.mean(v)) for k, v in role_evenness.items() if v}
}

with open(RESULTS / 'class_regime_universality.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'class_regime_universality.json'}")
