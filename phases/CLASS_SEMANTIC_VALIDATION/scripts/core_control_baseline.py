"""
Q3b: CORE_CONTROL Baseline Comparison

Establish baseline for what % of tokens are followed by ENERGY_OPERATOR
to evaluate whether CORE_CONTROL's 40.6% is significant.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

class_map = defaultdict(list)
for tok, cls in token_to_class.items():
    class_map[str(cls)].append(tok)

# Role mapping
ENERGY_CLASSES = {8, 31, 32, 33, 34, 36}
CORE_CONTROL_CLASSES = {10, 11, 17}
FLOW_CLASSES = {7, 30, 38, 40}
FREQUENT_CLASSES = {9, 20, 21, 23}

def get_role(cls):
    if cls in ENERGY_CLASSES:
        return 'ENERGY_OPERATOR'
    elif cls in CORE_CONTROL_CLASSES:
        return 'CORE_CONTROL'
    elif cls in FLOW_CLASSES:
        return 'FLOW_OPERATOR'
    elif cls in FREQUENT_CLASSES:
        return 'FREQUENT_OPERATOR'
    else:
        return 'OTHER'

# Get token sets
cc_tokens = set()
for cls in CORE_CONTROL_CLASSES:
    cc_tokens.update(class_map.get(str(cls), []))

energy_tokens = set()
for cls in ENERGY_CLASSES:
    energy_tokens.update(class_map.get(str(cls), []))

print("=" * 60)
print("Q3b: CORE_CONTROL BASELINE COMPARISON")
print("=" * 60)

# Group by folio/line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    lines[(token.folio, token.line)].append(word)

# Count follow-on patterns for ALL tokens vs CORE_CONTROL
all_followon = defaultdict(int)
cc_followon = defaultdict(int)
role_followon = defaultdict(lambda: defaultdict(int))

total_followable = 0  # Tokens that have a next token
cc_followable = 0

for (folio, line), words in lines.items():
    n = len(words)
    for i in range(n - 1):
        curr = words[i]
        next_word = words[i + 1]

        curr_class = token_to_class.get(curr)
        next_class = token_to_class.get(next_word)

        if next_class:
            next_role = get_role(next_class)
            all_followon[next_role] += 1
            total_followable += 1

            if curr_class:
                curr_role = get_role(curr_class)
                role_followon[curr_role][next_role] += 1

            if curr in cc_tokens:
                cc_followon[next_role] += 1
                cc_followable += 1

print("\n" + "-" * 40)
print("BASELINE: ALL TOKENS")
print("-" * 40)

print(f"\nTotal followable tokens: {total_followable}")
print("\nFollow-on distribution (any token -> X):")
for role in ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'OTHER']:
    count = all_followon[role]
    rate = count / total_followable if total_followable > 0 else 0
    print(f"  {role}: {count} ({rate:.1%})")

baseline_energy = all_followon['ENERGY_OPERATOR'] / total_followable if total_followable > 0 else 0

print("\n" + "-" * 40)
print("CORE_CONTROL FOLLOW-ON")
print("-" * 40)

print(f"\nCORE_CONTROL followable tokens: {cc_followable}")
print("\nFollow-on distribution (CORE_CONTROL -> X):")
for role in ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'OTHER']:
    count = cc_followon[role]
    rate = count / cc_followable if cc_followable > 0 else 0
    print(f"  {role}: {count} ({rate:.1%})")

cc_energy = cc_followon['ENERGY_OPERATOR'] / cc_followable if cc_followable > 0 else 0

print("\n" + "-" * 40)
print("COMPARISON")
print("-" * 40)

enrichment = cc_energy / baseline_energy if baseline_energy > 0 else 0
print(f"\nBaseline ENERGY follow-on rate: {baseline_energy:.1%}")
print(f"CORE_CONTROL ENERGY follow-on rate: {cc_energy:.1%}")
print(f"Enrichment: {enrichment:.2f}x")

# Chi-square test
observed = cc_followon['ENERGY_OPERATOR']
expected = cc_followable * baseline_energy
other_observed = cc_followable - observed
other_expected = cc_followable * (1 - baseline_energy)

if expected >= 5 and other_expected >= 5:
    chi2 = ((observed - expected)**2 / expected) + ((other_observed - other_expected)**2 / other_expected)
    p_value = 1 - stats.chi2.cdf(chi2, df=1)
    print(f"\nChi-square test: chi2={chi2:.2f}, p={p_value:.4f}")
    if p_value < 0.01:
        print("=> SIGNIFICANT (p < 0.01)")
    elif p_value < 0.05:
        print("=> SIGNIFICANT (p < 0.05)")
    else:
        print("=> NOT SIGNIFICANT")

print("\n" + "-" * 40)
print("ALL ROLES COMPARISON")
print("-" * 40)

print("\n| Source Role | -> ENERGY | -> CC | -> FLOW | -> FREQ | -> OTHER |")
print("|-------------|-----------|-------|---------|---------|----------|")

for src_role in ['CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'OTHER']:
    total = sum(role_followon[src_role].values())
    if total > 0:
        rates = []
        for dst_role in ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'OTHER']:
            rate = role_followon[src_role][dst_role] / total
            rates.append(f"{rate:.1%}")
        print(f"| {src_role:11s} | {rates[0]:9s} | {rates[1]:5s} | {rates[2]:7s} | {rates[3]:7s} | {rates[4]:8s} |")

# Baseline row
rates = []
for dst_role in ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR', 'OTHER']:
    rate = all_followon[dst_role] / total_followable if total_followable > 0 else 0
    rates.append(f"{rate:.1%}")
print(f"| {'BASELINE':11s} | {rates[0]:9s} | {rates[1]:5s} | {rates[2]:7s} | {rates[3]:7s} | {rates[4]:8s} |")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"\nCORE_CONTROL -> ENERGY enrichment: {enrichment:.2f}x over baseline")

if enrichment > 1.3 and p_value < 0.01:
    print("\n=> SUPPORTED: CORE_CONTROL significantly enriched for ENERGY follow-on")
elif enrichment > 1.1:
    print("\n=> WEAK SUPPORT: CORE_CONTROL slightly enriched for ENERGY follow-on")
else:
    print("\n=> NOT SUPPORTED: CORE_CONTROL ENERGY follow-on is baseline-level")

# Save results
results = {
    'baseline_energy_rate': baseline_energy,
    'cc_energy_rate': cc_energy,
    'enrichment': enrichment,
    'chi2': chi2 if 'chi2' in dir() else None,
    'p_value': p_value if 'p_value' in dir() else None,
    'role_followon_matrix': {k: dict(v) for k, v in role_followon.items()}
}

with open(RESULTS / 'core_control_baseline.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'core_control_baseline.json'}")
