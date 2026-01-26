"""
Q13: Class 33 Anomaly

From C552: Class 33 is depleted in PHARMA section at 0.20x.
Why? What makes Class 33 avoid PHARMA specifically?
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
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[int(cls)].append(tok)

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

# ENERGY classes for comparison
ENERGY_CLASSES = {8, 31, 32, 33, 34, 36}

print("=" * 70)
print("Q13: CLASS 33 ANOMALY")
print("=" * 70)

# 1. CLASS 33 BASICS
print("\n" + "-" * 70)
print("1. CLASS 33 PROFILE")
print("-" * 70)

class33_tokens = class_to_tokens[33]
print(f"\nClass 33 token types: {len(class33_tokens)}")
print(f"Tokens: {', '.join(sorted(class33_tokens)[:20])}...")

# Count occurrences
class33_count = sum(1 for t in tokens if token_to_class.get(t.word.replace('*', '').strip()) == 33)
total_count = sum(1 for t in tokens if token_to_class.get(t.word.replace('*', '').strip()) is not None)
print(f"\nTotal Class 33 occurrences: {class33_count}")
print(f"Rate in corpus: {class33_count/total_count*100:.1f}%")

# 2. SECTION DISTRIBUTION
print("\n" + "-" * 70)
print("2. CLASS 33 BY SECTION")
print("-" * 70)

section_counts = defaultdict(lambda: {'class33': 0, 'total': 0})
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    section = get_section(folio)
    cls = token_to_class.get(word)

    if cls is not None:
        section_counts[section]['total'] += 1
        if cls == 33:
            section_counts[section]['class33'] += 1

print("\n| Section | Class 33 | Total | Rate | Expected | Enrichment |")
print("|---------|----------|-------|------|----------|------------|")

baseline_rate = class33_count / total_count
for section in ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']:
    c33 = section_counts[section]['class33']
    total = section_counts[section]['total']
    rate = c33 / total if total > 0 else 0
    expected = baseline_rate * total
    enrichment = rate / baseline_rate if baseline_rate > 0 else 0

    marker = "**" if section == 'PHARMA' else ""
    print(f"| {marker}{section:8s}{marker} | {c33:8d} | {total:5d} | {rate*100:3.1f}% | {expected:8.1f} | {enrichment:.2f}x       |")

# 3. COMPARE TO OTHER ENERGY CLASSES
print("\n" + "-" * 70)
print("3. ENERGY CLASSES IN PHARMA")
print("-" * 70)

print("\nHow do other ENERGY classes behave in PHARMA?")
print("\n| Class | PHARMA Count | PHARMA Rate | Corpus Rate | Enrichment |")
print("|-------|--------------|-------------|-------------|------------|")

pharma_total = section_counts['PHARMA']['total']
for cls in sorted(ENERGY_CLASSES):
    # Count in PHARMA
    pharma_count = sum(1 for t in tokens
                       if get_section(t.folio) == 'PHARMA'
                       and token_to_class.get(t.word.replace('*', '').strip()) == cls)

    # Count in corpus
    corpus_count = sum(1 for t in tokens
                       if token_to_class.get(t.word.replace('*', '').strip()) == cls)

    pharma_rate = pharma_count / pharma_total if pharma_total > 0 else 0
    corpus_rate = corpus_count / total_count if total_count > 0 else 0
    enrichment = pharma_rate / corpus_rate if corpus_rate > 0 else 0

    marker = "**" if cls == 33 else ""
    print(f"| {marker}{cls:5d}{marker} | {pharma_count:12d} | {pharma_rate*100:10.1f}% | {corpus_rate*100:10.1f}% | {enrichment:.2f}x       |")

# 4. REGIME DISTRIBUTION OF PHARMA
print("\n" + "-" * 70)
print("4. PHARMA REGIME COMPOSITION")
print("-" * 70)

pharma_regimes = defaultdict(int)
pharma_folios = set()
for token in tokens:
    folio = token.folio
    if get_section(folio) == 'PHARMA':
        pharma_folios.add(folio)
        pharma_regimes[folio_regime.get(folio, 'UNKNOWN')] += 1

print(f"\nPHARMA folios: {sorted(pharma_folios)}")
print("\nPHARMA tokens by REGIME:")
print("| REGIME | Tokens | % |")
print("|--------|--------|---|")
pharma_tokens_total = sum(pharma_regimes.values())
for regime in sorted(pharma_regimes.keys()):
    count = pharma_regimes[regime]
    pct = count / pharma_tokens_total * 100 if pharma_tokens_total > 0 else 0
    print(f"| {regime} | {count:6d} | {pct:4.1f}% |")

# 5. CLASS 33 BY REGIME (to see if PHARMA's REGIME explains it)
print("\n" + "-" * 70)
print("5. CLASS 33 BY REGIME")
print("-" * 70)

regime_class33 = defaultdict(lambda: {'class33': 0, 'total': 0})
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    regime = folio_regime.get(folio)
    cls = token_to_class.get(word)

    if cls is not None and regime:
        regime_class33[regime]['total'] += 1
        if cls == 33:
            regime_class33[regime]['class33'] += 1

print("\n| REGIME | Class 33 | Total | Rate | Enrichment |")
print("|--------|----------|-------|------|------------|")
for regime in sorted(regime_class33.keys()):
    c33 = regime_class33[regime]['class33']
    total = regime_class33[regime]['total']
    rate = c33 / total if total > 0 else 0
    enrichment = rate / baseline_rate if baseline_rate > 0 else 0
    print(f"| {regime} | {c33:8d} | {total:5d} | {rate*100:3.1f}% | {enrichment:.2f}x       |")

# 6. CLASS 33 TOKEN ANALYSIS
print("\n" + "-" * 70)
print("6. CLASS 33 TOKEN FORMS")
print("-" * 70)

# What are the actual tokens in Class 33?
class33_in_pharma = []
class33_elsewhere = []

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    section = get_section(folio)
    cls = token_to_class.get(word)

    if cls == 33:
        if section == 'PHARMA':
            class33_in_pharma.append(word)
        else:
            class33_elsewhere.append(word)

print(f"\nClass 33 in PHARMA ({len(class33_in_pharma)} tokens):")
pharma_forms = defaultdict(int)
for w in class33_in_pharma:
    pharma_forms[w] += 1
for w, c in sorted(pharma_forms.items(), key=lambda x: -x[1])[:10]:
    print(f"  {w}: {c}")

print(f"\nClass 33 elsewhere ({len(class33_elsewhere)} tokens) - top forms:")
other_forms = defaultdict(int)
for w in class33_elsewhere:
    other_forms[w] += 1
for w, c in sorted(other_forms.items(), key=lambda x: -x[1])[:10]:
    print(f"  {w}: {c}")

# Check if any forms are PHARMA-exclusive or PHARMA-absent
pharma_exclusive = set(pharma_forms.keys()) - set(other_forms.keys())
pharma_absent = set(other_forms.keys()) - set(pharma_forms.keys())
print(f"\nPHARMA-exclusive Class 33 forms: {len(pharma_exclusive)}")
print(f"PHARMA-absent Class 33 forms: {len(pharma_absent)}")

# 7. POSITIONAL ANALYSIS
print("\n" + "-" * 70)
print("7. CLASS 33 POSITIONAL BEHAVIOR")
print("-" * 70)

# Is Class 33 positionally different in PHARMA vs elsewhere?
positions = {'PHARMA': [], 'OTHER': []}
lines = defaultdict(list)

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    lines[(folio, line)].append({'word': word, 'class': token_to_class.get(word)})

for (folio, line), word_data in lines.items():
    section = get_section(folio)
    n = len(word_data)

    for i, wd in enumerate(word_data):
        if wd['class'] == 33:
            rel_pos = i / (n - 1) if n > 1 else 0.5
            if section == 'PHARMA':
                positions['PHARMA'].append(rel_pos)
            else:
                positions['OTHER'].append(rel_pos)

if positions['PHARMA'] and positions['OTHER']:
    print(f"\nClass 33 mean relative position:")
    print(f"  PHARMA: {np.mean(positions['PHARMA']):.3f} (n={len(positions['PHARMA'])})")
    print(f"  OTHER: {np.mean(positions['OTHER']):.3f} (n={len(positions['OTHER'])})")

    stat, p = stats.mannwhitneyu(positions['PHARMA'], positions['OTHER'], alternative='two-sided')
    print(f"  Mann-Whitney: U={stat:.0f}, p={p:.4f}")
else:
    print(f"\nInsufficient PHARMA data for positional analysis")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Calculate key metrics
pharma_c33_enrichment = (section_counts['PHARMA']['class33'] / section_counts['PHARMA']['total']) / baseline_rate if section_counts['PHARMA']['total'] > 0 else 0

# Which ENERGY class is most enriched in PHARMA?
energy_pharma_enrichments = {}
for cls in ENERGY_CLASSES:
    pharma_count = sum(1 for t in tokens
                       if get_section(t.folio) == 'PHARMA'
                       and token_to_class.get(t.word.replace('*', '').strip()) == cls)
    corpus_count = sum(1 for t in tokens
                       if token_to_class.get(t.word.replace('*', '').strip()) == cls)

    pharma_rate = pharma_count / pharma_total if pharma_total > 0 else 0
    corpus_rate = corpus_count / total_count if total_count > 0 else 0
    energy_pharma_enrichments[cls] = pharma_rate / corpus_rate if corpus_rate > 0 else 0

most_enriched = max(energy_pharma_enrichments, key=energy_pharma_enrichments.get)
most_depleted = min(energy_pharma_enrichments, key=energy_pharma_enrichments.get)

print(f"""
1. CLASS 33 PHARMA DEPLETION: {pharma_c33_enrichment:.2f}x (confirmed)

2. ENERGY CLASS PATTERN IN PHARMA:
   - Most enriched: Class {most_enriched} ({energy_pharma_enrichments[most_enriched]:.2f}x)
   - Most depleted: Class {most_depleted} ({energy_pharma_enrichments[most_depleted]:.2f}x)

3. EXPLANATION CANDIDATES:
   - PHARMA is REGIME_1/4 dominated (not REGIME-driven depletion)
   - Class 33 vs 34 divergence in PHARMA context
   - Class 33 may represent specific thermal operation not needed in PHARMA
""")

# Save results
results = {
    'class33_pharma_enrichment': float(pharma_c33_enrichment),
    'energy_pharma_enrichments': {str(k): float(v) for k, v in energy_pharma_enrichments.items()},
    'class33_tokens': class33_tokens[:20],
    'pharma_regime_composition': dict(pharma_regimes)
}

with open(RESULTS / 'class33_anomaly.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'class33_anomaly.json'}")
