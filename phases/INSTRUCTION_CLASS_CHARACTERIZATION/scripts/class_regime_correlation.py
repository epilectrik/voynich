"""
CLASS REGIME CORRELATION ANALYSIS

Research Question Q6: Class REGIME Correlation
- Do control-intensive REGIMEs favor certain classes?
- Are there REGIME-exclusive classes?
- How does class distribution differ by REGIME?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()

print("=" * 70)
print("CLASS REGIME CORRELATION ANALYSIS")
print("=" * 70)

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# Load REGIME mapping
with open('C:/git/voynich/phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"\n[Setup] REGIMEs loaded:")
for regime, folios in regime_mapping.items():
    print(f"  {regime}: {len(folios)} folios")

# =============================================================================
# STEP 1: Collect class counts by REGIME
# =============================================================================
print("\n[Step 1] Collecting class data by REGIME...")

regime_class_counts = defaultdict(Counter)
regime_totals = Counter()
class_totals = Counter()
total_tokens = 0

for token in tx.currier_b():
    if token.word and token.word in token_to_class:
        folio = token.folio
        if folio not in folio_to_regime:
            continue

        regime = folio_to_regime[folio]
        cls = token_to_class[token.word]

        regime_class_counts[regime][cls] += 1
        regime_totals[regime] += 1
        class_totals[cls] += 1
        total_tokens += 1

print(f"  Total classified tokens in REGIME folios: {total_tokens}")
for regime in sorted(regime_class_counts.keys()):
    print(f"    {regime}: {regime_totals[regime]} tokens")

# =============================================================================
# STEP 2: Calculate enrichment by REGIME
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Class Enrichment by REGIME")
print("=" * 70)

# Calculate baseline rates (across all REGIMEs)
baseline_rates = {cls: class_totals[cls] / total_tokens for cls in class_totals}

# Find enriched/depleted classes per REGIME
regime_enrichments = defaultdict(list)  # regime -> [(class, enrichment, count)]

for regime in sorted(regime_class_counts.keys()):
    print(f"\n  {regime} (n={regime_totals[regime]}):")

    enriched = []
    depleted = []

    for cls in range(1, 50):
        count = regime_class_counts[regime][cls]
        if count < 5:
            continue

        rate = count / regime_totals[regime]
        baseline = baseline_rates.get(cls, 0)

        if baseline > 0:
            enrichment = rate / baseline

            if enrichment > 1.5:
                enriched.append((cls, enrichment, count))
            elif enrichment < 0.5:
                depleted.append((cls, enrichment, count))

    enriched.sort(key=lambda x: x[1], reverse=True)
    depleted.sort(key=lambda x: x[1])

    print(f"\n    ENRICHED (>1.5x baseline):")
    for cls, enr, count in enriched[:10]:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"      Class {cls:2d} ({role[:4]}): {enr:.2f}x (n={count}) - {tokens}")
        regime_enrichments[regime].append((cls, enr, 'enriched'))

    print(f"\n    DEPLETED (<0.5x baseline):")
    for cls, enr, count in depleted[:10]:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"      Class {cls:2d} ({role[:4]}): {enr:.2f}x (n={count}) - {tokens}")
        regime_enrichments[regime].append((cls, enr, 'depleted'))

# =============================================================================
# STEP 3: REGIME-exclusive and REGIME-universal classes
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: REGIME Exclusivity Analysis")
print("=" * 70)

# For each class, count how many REGIMEs it appears in
class_regime_presence = defaultdict(set)
class_regime_concentration = {}  # class -> {regime: fraction}

for regime in regime_class_counts:
    for cls, count in regime_class_counts[regime].items():
        if count >= 3:  # Minimum threshold
            class_regime_presence[cls].add(regime)

for cls in range(1, 50):
    if class_totals[cls] < 10:
        continue

    concentrations = {}
    for regime in regime_class_counts:
        count = regime_class_counts[regime][cls]
        concentrations[regime] = count / class_totals[cls] if class_totals[cls] > 0 else 0

    class_regime_concentration[cls] = concentrations

# Find classes with high concentration in single REGIME
print("\n  Classes with >50% concentration in single REGIME:")
concentrated = []
for cls, concentrations in class_regime_concentration.items():
    max_regime = max(concentrations, key=concentrations.get)
    max_conc = concentrations[max_regime]
    if max_conc > 0.5:
        concentrated.append((cls, max_regime, max_conc))

concentrated.sort(key=lambda x: x[2], reverse=True)
for cls, regime, conc in concentrated[:15]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): {conc:.0%} in {regime} - {tokens}")

# Find REGIME-universal classes (spread evenly)
print("\n  REGIME-universal classes (present in all 4, max concentration <40%):")
universal = []
for cls, concentrations in class_regime_concentration.items():
    if len(class_regime_presence[cls]) == 4:
        max_conc = max(concentrations.values())
        if max_conc < 0.40:
            universal.append((cls, max_conc))

universal.sort(key=lambda x: x[1])
for cls, max_conc in universal[:15]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    concs = class_regime_concentration[cls]
    conc_str = ", ".join(f"{r[-1]}:{c:.0%}" for r, c in sorted(concs.items()))
    print(f"    Class {cls:2d} ({role[:4]}): max={max_conc:.0%} [{conc_str}] - {tokens}")

# =============================================================================
# STEP 4: Role-level REGIME patterns
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Role-Level REGIME Patterns")
print("=" * 70)

role_regime_counts = defaultdict(lambda: defaultdict(int))
role_totals = defaultdict(int)

for regime in regime_class_counts:
    for cls, count in regime_class_counts[regime].items():
        role = class_to_role.get(str(cls), 'UNKNOWN')
        role_regime_counts[role][regime] += count
        role_totals[role] += count

print("\n  Role distribution by REGIME:")
for role in sorted(role_totals.keys()):
    print(f"\n  {role}:")
    for regime in sorted(regime_class_counts.keys()):
        count = role_regime_counts[role][regime]
        pct_of_role = count / role_totals[role] * 100 if role_totals[role] else 0
        pct_of_regime = count / regime_totals[regime] * 100 if regime_totals[regime] else 0
        print(f"    {regime}: {count:4d} ({pct_of_role:5.1f}% of role, {pct_of_regime:5.1f}% of regime)")

# Calculate role enrichment by REGIME
print("\n  Role enrichment by REGIME (vs baseline):")
role_baseline = {role: role_totals[role] / total_tokens for role in role_totals}

for regime in sorted(regime_class_counts.keys()):
    print(f"\n  {regime}:")
    enrichments = []
    for role in sorted(role_totals.keys()):
        count = role_regime_counts[role][regime]
        rate = count / regime_totals[regime]
        baseline = role_baseline[role]
        enrichment = rate / baseline if baseline > 0 else 0
        enrichments.append((role, enrichment, count))

    enrichments.sort(key=lambda x: x[1], reverse=True)
    for role, enr, count in enrichments:
        marker = "+" if enr > 1.1 else ("-" if enr < 0.9 else " ")
        print(f"    {marker} {role:20s}: {enr:.2f}x (n={count})")

# =============================================================================
# STEP 5: REGIME class signatures
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: REGIME Class Signatures")
print("=" * 70)

# For each REGIME, identify its "signature" classes (most distinctive)
for regime in sorted(regime_class_counts.keys()):
    print(f"\n  {regime} signature classes (most distinctive):")

    distinctiveness = []
    for cls in range(1, 50):
        count = regime_class_counts[regime][cls]
        if count < 10:
            continue

        # Calculate how much more common this class is here vs other REGIMEs
        other_count = sum(regime_class_counts[r][cls] for r in regime_class_counts if r != regime)
        other_total = sum(regime_totals[r] for r in regime_totals if r != regime)

        here_rate = count / regime_totals[regime]
        other_rate = other_count / other_total if other_total > 0 else 0

        ratio = here_rate / other_rate if other_rate > 0 else float('inf')
        distinctiveness.append((cls, ratio, count))

    distinctiveness.sort(key=lambda x: x[1], reverse=True)
    for cls, ratio, count in distinctiveness[:5]:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        if ratio == float('inf'):
            print(f"    Class {cls:2d} ({role[:4]}): EXCLUSIVE (n={count}) - {tokens}")
        else:
            print(f"    Class {cls:2d} ({role[:4]}): {ratio:.2f}x vs others (n={count}) - {tokens}")

# =============================================================================
# STEP 6: REGIME differentiation summary
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: REGIME Differentiation Summary")
print("=" * 70)

# Create summary table
print("\n  REGIME characterization by enriched classes:")

regime_chars = {
    'REGIME_1': {'control': 'High L-compound', 'section': '70% Section B'},
    'REGIME_2': {'control': 'High LATE', 'section': 'Output-intensive'},
    'REGIME_3': {'control': 'High L-compound, Low LATE', 'section': 'Control without output'},
    'REGIME_4': {'control': 'Low L-compound, Low LATE', 'section': 'Precision mode'},
}

for regime in sorted(regime_class_counts.keys()):
    print(f"\n  {regime}:")
    print(f"    Infrastructure: {regime_chars.get(regime, {}).get('control', 'Unknown')}")
    print(f"    Character: {regime_chars.get(regime, {}).get('section', 'Unknown')}")

    # Top enriched classes
    enriched = [(cls, enr, typ) for cls, enr, typ in regime_enrichments[regime] if typ == 'enriched']
    if enriched:
        top_classes = [f"C{cls}" for cls, _, _ in enriched[:3]]
        print(f"    Enriched classes: {', '.join(top_classes)}")

# =============================================================================
# STEP 7: Cross-REGIME class transitions
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: Classes that Distinguish REGIMEs")
print("=" * 70)

# Find classes with maximum variance across REGIMEs
class_variance = {}
for cls in range(1, 50):
    if class_totals[cls] < 20:
        continue

    rates = []
    for regime in regime_class_counts:
        rate = regime_class_counts[regime][cls] / regime_totals[regime]
        rates.append(rate)

    if rates:
        variance = np.var(rates)
        class_variance[cls] = variance

sorted_by_variance = sorted(class_variance.items(), key=lambda x: x[1], reverse=True)

print("\n  Highest variance classes (best REGIME discriminators):")
for cls, var in sorted_by_variance[:15]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]

    # Show rates per REGIME
    rates = []
    for regime in sorted(regime_class_counts.keys()):
        rate = regime_class_counts[regime][cls] / regime_totals[regime] * 100
        rates.append(f"{regime[-1]}:{rate:.1f}%")

    print(f"    Class {cls:2d} ({role[:4]}): var={var:.6f} [{', '.join(rates)}] - {tokens}")

print("\n  Lowest variance classes (REGIME-independent):")
for cls, var in sorted_by_variance[-10:]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]

    rates = []
    for regime in sorted(regime_class_counts.keys()):
        rate = regime_class_counts[regime][cls] / regime_totals[regime] * 100
        rates.append(f"{regime[-1]}:{rate:.1f}%")

    print(f"    Class {cls:2d} ({role[:4]}): var={var:.6f} [{', '.join(rates)}] - {tokens}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'regime_class_counts': {
        regime: dict(counts) for regime, counts in regime_class_counts.items()
    },
    'regime_totals': dict(regime_totals),
    'class_regime_concentration': {str(k): v for k, v in class_regime_concentration.items()},
    'class_variance': {str(k): v for k, v in class_variance.items()},
    'concentrated_classes': [
        {'class': cls, 'regime': regime, 'concentration': conc}
        for cls, regime, conc in concentrated
    ],
}

with open('results/class_regime_correlation.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_regime_correlation.json")
print("=" * 70)
