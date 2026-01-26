"""
Q5: Role Transition Matrix

Analyze full role->role transition probabilities and compare to random.
Identify which transitions are enriched/depleted vs independence expectation.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import random
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

# Role mapping - comprehensive
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

ROLE_NAMES = {
    'CC': 'CORE_CONTROL',
    'EN': 'ENERGY',
    'FL': 'FLOW',
    'FQ': 'FREQUENT',
    'AX': 'AUXILIARY',
    'UN': 'UNCLASSIFIED'
}

def get_role(word):
    cls = token_to_class.get(word)
    if cls is None:
        return 'UN'
    return ROLE_MAP.get(cls, 'AX')

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

print("=" * 70)
print("Q5: ROLE TRANSITION MATRIX")
print("=" * 70)

# Group by line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    line = token.line
    role = get_role(word)
    lines[(folio, line)].append({'word': word, 'role': role, 'folio': folio})

# Count transitions
ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
transition_counts = defaultdict(lambda: defaultdict(int))
role_counts = defaultdict(int)
total_transitions = 0

for (folio, line), word_data in lines.items():
    for i in range(len(word_data) - 1):
        src = word_data[i]['role']
        dst = word_data[i + 1]['role']
        transition_counts[src][dst] += 1
        role_counts[src] += 1
        total_transitions += 1

# Add final position counts
for (folio, line), word_data in lines.items():
    if word_data:
        role_counts[word_data[-1]['role']] += 1

print(f"\nTotal transitions: {total_transitions}")
print(f"Total role occurrences: {sum(role_counts.values())}")

print("\n" + "-" * 70)
print("ROLE FREQUENCY")
print("-" * 70)

total_roles = sum(role_counts.values())
print("\n| Role | Count | Rate |")
print("|------|-------|------|")
for role in ROLES:
    count = role_counts[role]
    rate = count / total_roles if total_roles > 0 else 0
    print(f"| {ROLE_NAMES[role]:15s} | {count:5d} | {rate:.1%} |")

print("\n" + "-" * 70)
print("OBSERVED TRANSITION MATRIX (row -> column)")
print("-" * 70)

# Print header
header = "| From \\ To |"
for role in ROLES:
    header += f" {role:5s} |"
print(header)
print("|-----------|" + "-------|" * len(ROLES))

for src in ROLES:
    row_total = sum(transition_counts[src].values())
    row = f"| {src:9s} |"
    for dst in ROLES:
        count = transition_counts[src][dst]
        rate = count / row_total if row_total > 0 else 0
        row += f" {rate*100:5.1f} |"
    print(row)

print("\n" + "-" * 70)
print("EXPECTED TRANSITION MATRIX (independence model)")
print("-" * 70)

# Expected under independence: P(A->B) = P(B) (destination doesn't depend on source)
dst_probs = {}
for role in ROLES:
    # Probability of being in position i+1 given classified
    dst_probs[role] = role_counts[role] / total_roles if total_roles > 0 else 0

header = "| From \\ To |"
for role in ROLES:
    header += f" {role:5s} |"
print(header)
print("|-----------|" + "-------|" * len(ROLES))

for src in ROLES:
    row = f"| {src:9s} |"
    for dst in ROLES:
        row += f" {dst_probs[dst]*100:5.1f} |"
    print(row)

print("\n" + "-" * 70)
print("ENRICHMENT MATRIX (observed / expected)")
print("-" * 70)

enrichment = defaultdict(lambda: defaultdict(float))
header = "| From \\ To |"
for role in ROLES:
    header += f" {role:5s} |"
print(header)
print("|-----------|" + "-------|" * len(ROLES))

for src in ROLES:
    row_total = sum(transition_counts[src].values())
    row = f"| {src:9s} |"
    for dst in ROLES:
        count = transition_counts[src][dst]
        observed = count / row_total if row_total > 0 else 0
        expected = dst_probs[dst]
        enrich = observed / expected if expected > 0 else 0
        enrichment[src][dst] = enrich
        # Highlight significant enrichment/depletion
        if enrich > 1.3:
            row += f" {enrich:4.2f}+ |"
        elif enrich < 0.7:
            row += f" {enrich:4.2f}- |"
        else:
            row += f" {enrich:5.2f} |"
    print(row)

print("\n" + "-" * 70)
print("SIGNIFICANT TRANSITIONS (chi-square test)")
print("-" * 70)

print("\nTransitions significantly different from independence (p < 0.01):\n")
print("| Transition | Observed | Expected | Enrichment | Chi2 | p-value |")
print("|------------|----------|----------|------------|------|---------|")

significant_transitions = []
for src in ROLES:
    row_total = sum(transition_counts[src].values())
    if row_total < 10:
        continue

    for dst in ROLES:
        observed = transition_counts[src][dst]
        expected = row_total * dst_probs[dst]

        if expected < 5:
            continue

        # Chi-square for this cell
        chi2 = (observed - expected) ** 2 / expected
        p_value = 1 - stats.chi2.cdf(chi2, df=1)

        enrich = observed / expected if expected > 0 else 0

        if p_value < 0.01:
            direction = "+" if enrich > 1 else "-"
            significant_transitions.append({
                'src': src, 'dst': dst,
                'observed': observed, 'expected': expected,
                'enrichment': enrich, 'chi2': chi2, 'p_value': p_value
            })
            print(f"| {src}->{dst:5s} | {observed:8d} | {expected:8.1f} | {enrich:9.2f}x | {chi2:4.1f} | {p_value:.4f} |")

print("\n" + "-" * 70)
print("KEY PATTERNS")
print("-" * 70)

# Identify strongest patterns
print("\nTop 5 ENRICHED transitions:")
enriched = sorted(significant_transitions, key=lambda x: x['enrichment'], reverse=True)[:5]
for t in enriched:
    print(f"  {ROLE_NAMES[t['src']]} -> {ROLE_NAMES[t['dst']]}: {t['enrichment']:.2f}x (p={t['p_value']:.4f})")

print("\nTop 5 DEPLETED transitions:")
depleted = sorted(significant_transitions, key=lambda x: x['enrichment'])[:5]
for t in depleted:
    print(f"  {ROLE_NAMES[t['src']]} -> {ROLE_NAMES[t['dst']]}: {t['enrichment']:.2f}x (p={t['p_value']:.4f})")

# Self-transition analysis
print("\n" + "-" * 70)
print("SELF-TRANSITION (same role -> same role)")
print("-" * 70)

print("\n| Role | Self-Rate | Expected | Enrichment |")
print("|------|-----------|----------|------------|")

for role in ROLES:
    row_total = sum(transition_counts[role].values())
    if row_total < 10:
        continue
    self_count = transition_counts[role][role]
    self_rate = self_count / row_total if row_total > 0 else 0
    expected = dst_probs[role]
    enrich = self_rate / expected if expected > 0 else 0
    print(f"| {ROLE_NAMES[role]:15s} | {self_rate:.1%} | {expected:.1%} | {enrich:.2f}x |")

print("\n" + "-" * 70)
print("REGIME-SPECIFIC PATTERNS")
print("-" * 70)

# Calculate transition enrichment by REGIME
regime_transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
regime_totals = defaultdict(int)

for (folio, line), word_data in lines.items():
    regime = folio_regime.get(folio)
    if not regime:
        continue

    for i in range(len(word_data) - 1):
        src = word_data[i]['role']
        dst = word_data[i + 1]['role']
        regime_transitions[regime][src][dst] += 1
        regime_totals[regime] += 1

# Focus on EN->EN (self-chaining) by regime
print("\nENERGY self-transition by REGIME:")
print("| REGIME | EN->EN | Total EN-> | Rate | vs Baseline |")
print("|--------|-------|-----------|------|-------------|")

baseline_en_self = enrichment['EN']['EN']
for regime in sorted(regime_transitions.keys()):
    en_total = sum(regime_transitions[regime]['EN'].values())
    en_self = regime_transitions[regime]['EN']['EN']
    rate = en_self / en_total if en_total > 0 else 0
    expected = dst_probs['EN']
    vs_base = (rate / expected) / baseline_en_self if baseline_en_self > 0 else 0
    print(f"| {regime} | {en_self:5d} | {en_total:9d} | {rate:.1%} | {vs_base:.2f}x |")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\nKey findings:")
print(f"1. ENERGY self-transition: {enrichment['EN']['EN']:.2f}x enriched")
print(f"2. FLOW self-transition: {enrichment['FL']['FL']:.2f}x enriched")
print(f"3. FREQUENT self-transition: {enrichment['FQ']['FQ']:.2f}x enriched")

# Check for role-role affinities
print("\nRole affinities (>1.3x enrichment):")
for src in ROLES:
    for dst in ROLES:
        if src != dst and enrichment[src][dst] > 1.3:
            print(f"  {ROLE_NAMES[src]} -> {ROLE_NAMES[dst]}: {enrichment[src][dst]:.2f}x")

print("\nRole avoidances (<0.7x enrichment):")
for src in ROLES:
    for dst in ROLES:
        if enrichment[src][dst] < 0.7 and enrichment[src][dst] > 0:
            print(f"  {ROLE_NAMES[src]} -> {ROLE_NAMES[dst]}: {enrichment[src][dst]:.2f}x")

# Save results
results = {
    'role_counts': dict(role_counts),
    'transition_counts': {src: dict(dsts) for src, dsts in transition_counts.items()},
    'enrichment': {src: dict(dsts) for src, dsts in enrichment.items()},
    'significant_transitions': significant_transitions,
    'total_transitions': total_transitions
}

with open(RESULTS / 'role_transition_matrix.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'role_transition_matrix.json'}")
