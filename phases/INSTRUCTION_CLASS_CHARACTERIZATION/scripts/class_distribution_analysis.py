"""
CLASS DISTRIBUTION ANALYSIS

Foundation analysis: How are the 49 instruction classes distributed?
- By folio (universal vs specialized)
- By section (B, H, S, C)
- By REGIME (control vs output intensive)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()

print("=" * 70)
print("INSTRUCTION CLASS DISTRIBUTION ANALYSIS")
print("=" * 70)

# Load class mapping
with open('../CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# Load REGIME mapping
with open('../REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Get section mapping
folio_section = {}
for token in tx.currier_b():
    if token.folio and token.folio not in folio_section:
        folio_section[token.folio] = getattr(token, 'section', 'unknown')

# =============================================================================
# STEP 1: Collect class counts by folio
# =============================================================================
print("\n[Step 1] Collecting class data by folio...")

folio_class_counts = defaultdict(Counter)
total_by_class = Counter()

for token in tx.currier_b():
    if token.word:
        word = token.word
        if word in token_to_class:
            cls = token_to_class[word]
            folio_class_counts[token.folio][cls] += 1
            total_by_class[cls] += 1

print(f"  Processed {sum(total_by_class.values())} classified tokens")
print(f"  Folios: {len(folio_class_counts)}")

# =============================================================================
# STEP 2: Class universality analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Class Universality")
print("=" * 70)

total_folios = len(folio_class_counts)
class_folio_coverage = {}

for cls in range(1, 50):
    folios_with_class = sum(1 for f, counts in folio_class_counts.items() if cls in counts)
    class_folio_coverage[cls] = folios_with_class

# Sort by coverage
sorted_by_coverage = sorted(class_folio_coverage.items(), key=lambda x: x[1], reverse=True)

print(f"\n  Class coverage (out of {total_folios} folios):")
print("\n  UNIVERSAL (80%+ folios):")
universal = []
for cls, count in sorted_by_coverage:
    pct = count / total_folios * 100
    if pct >= 80:
        role = class_to_role.get(str(cls), 'UNKNOWN')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {count} folios ({pct:.0f}%) - {tokens}")
        universal.append(cls)

print("\n  COMMON (50-79% folios):")
common = []
for cls, count in sorted_by_coverage:
    pct = count / total_folios * 100
    if 50 <= pct < 80:
        role = class_to_role.get(str(cls), 'UNKNOWN')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {count} folios ({pct:.0f}%) - {tokens}")
        common.append(cls)

print("\n  RARE (<50% folios):")
rare = []
for cls, count in sorted_by_coverage:
    pct = count / total_folios * 100
    if pct < 50:
        role = class_to_role.get(str(cls), 'UNKNOWN')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {count} folios ({pct:.0f}%) - {tokens}")
        rare.append(cls)

print(f"\n  Summary: {len(universal)} universal, {len(common)} common, {len(rare)} rare")

# =============================================================================
# STEP 3: Section distribution
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Section Distribution")
print("=" * 70)

section_class_counts = defaultdict(Counter)
section_totals = Counter()

for folio, counts in folio_class_counts.items():
    section = folio_section.get(folio, 'unknown')
    for cls, count in counts.items():
        section_class_counts[section][cls] += count
        section_totals[section] += count

# Find section-enriched classes
print("\n  Classes enriched by section (>1.5x vs baseline):")

baseline_rates = {cls: total_by_class[cls] / sum(total_by_class.values()) for cls in total_by_class}

for section in sorted(section_class_counts.keys()):
    if section_totals[section] < 500:
        continue
    print(f"\n  Section {section} (n={section_totals[section]}):")
    enriched = []
    for cls in range(1, 50):
        section_count = section_class_counts[section][cls]
        section_rate = section_count / section_totals[section]
        baseline = baseline_rates.get(cls, 0)
        if baseline > 0:
            enrichment = section_rate / baseline
            if enrichment > 1.5 and section_count >= 10:
                role = class_to_role.get(str(cls), 'UNKNOWN')
                enriched.append((cls, enrichment, section_count, role))

    enriched.sort(key=lambda x: x[1], reverse=True)
    for cls, enr, count, role in enriched[:5]:
        print(f"    Class {cls:2d} ({role[:4]}): {enr:.2f}x (n={count})")

# =============================================================================
# STEP 4: REGIME distribution
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: REGIME Distribution")
print("=" * 70)

regime_class_counts = defaultdict(Counter)
regime_totals = Counter()

for folio, counts in folio_class_counts.items():
    if folio not in folio_to_regime:
        continue
    regime = folio_to_regime[folio]
    for cls, count in counts.items():
        regime_class_counts[regime][cls] += count
        regime_totals[regime] += count

print("\n  Classes enriched by REGIME (>1.5x vs baseline):")

for regime in sorted(regime_class_counts.keys()):
    print(f"\n  {regime} (n={regime_totals[regime]}):")
    enriched = []
    for cls in range(1, 50):
        regime_count = regime_class_counts[regime][cls]
        regime_rate = regime_count / regime_totals[regime]
        baseline = baseline_rates.get(cls, 0)
        if baseline > 0:
            enrichment = regime_rate / baseline
            if enrichment > 1.5 and regime_count >= 10:
                role = class_to_role.get(str(cls), 'UNKNOWN')
                enriched.append((cls, enrichment, regime_count, role))

    enriched.sort(key=lambda x: x[1], reverse=True)
    for cls, enr, count, role in enriched[:5]:
        print(f"    Class {cls:2d} ({role[:4]}): {enr:.2f}x (n={count})")

# =============================================================================
# STEP 5: Role-level REGIME patterns
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Role-Level REGIME Patterns")
print("=" * 70)

role_regime_counts = defaultdict(lambda: defaultdict(int))
role_totals = defaultdict(int)

for regime, counts in regime_class_counts.items():
    for cls, count in counts.items():
        role = class_to_role.get(str(cls), 'UNKNOWN')
        role_regime_counts[role][regime] += count
        role_totals[role] += count

print("\n  Role distribution by REGIME:")
for role in sorted(role_totals.keys()):
    print(f"\n  {role}:")
    for regime in sorted(regime_class_counts.keys()):
        count = role_regime_counts[role][regime]
        total = role_totals[role]
        pct = count / total * 100 if total else 0
        regime_total = regime_totals[regime]
        overall = count / regime_total * 100 if regime_total else 0
        print(f"    {regime}: {pct:.1f}% of role, {overall:.1f}% of regime")

# =============================================================================
# STEP 6: Class frequency ranking
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Class Frequency Ranking")
print("=" * 70)

sorted_by_freq = sorted(total_by_class.items(), key=lambda x: x[1], reverse=True)

print("\n  Top 20 classes by frequency:")
for rank, (cls, count) in enumerate(sorted_by_freq[:20], 1):
    role = class_to_role.get(str(cls), 'UNKNOWN')
    pct = count / sum(total_by_class.values()) * 100
    coverage = class_folio_coverage[cls] / total_folios * 100
    print(f"    {rank:2d}. Class {cls:2d} ({role[:4]}): {count:5d} ({pct:.1f}%), {coverage:.0f}% coverage")

print("\n  Bottom 10 classes by frequency:")
for rank, (cls, count) in enumerate(sorted_by_freq[-10:], 40):
    role = class_to_role.get(str(cls), 'UNKNOWN')
    pct = count / sum(total_by_class.values()) * 100
    coverage = class_folio_coverage[cls] / total_folios * 100
    print(f"    {rank:2d}. Class {cls:2d} ({role[:4]}): {count:5d} ({pct:.2f}%), {coverage:.0f}% coverage")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'class_folio_coverage': class_folio_coverage,
    'total_by_class': dict(total_by_class),
    'universal_classes': universal,
    'common_classes': common,
    'rare_classes': rare,
}

with open('results/class_distribution.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_distribution.json")
print("=" * 70)
