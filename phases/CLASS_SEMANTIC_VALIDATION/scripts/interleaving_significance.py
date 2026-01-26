"""
Q4: Interleaving Significance Test

Test whether the 61-75% qo/ch-sh interleaving rate is significantly
different from random expectation.

Null hypothesis: If qo and ch/sh tokens are distributed randomly,
what interleaving rate would we expect?
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

# qo and ch/sh families
QO_CLASSES = {32, 33, 36}
CHSH_CLASSES = {8, 31, 34}

qo_tokens = set()
for cls in QO_CLASSES:
    qo_tokens.update(class_map.get(str(cls), []))

chsh_tokens = set()
for cls in CHSH_CLASSES:
    chsh_tokens.update(class_map.get(str(cls), []))

print("=" * 60)
print("Q4: INTERLEAVING SIGNIFICANCE TEST")
print("=" * 60)

# Group by line
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    lines[(token.folio, token.line)].append(word)

# Extract energy-family sequences from each line
# Mark each token as Q (qo), C (ch/sh), or X (other)
def get_energy_sequence(words):
    """Extract sequence of Q/C tokens from a line."""
    seq = []
    for w in words:
        if w in qo_tokens:
            seq.append('Q')
        elif w in chsh_tokens:
            seq.append('C')
    return seq

def count_transitions(seq):
    """Count interleaving vs same-family transitions."""
    interleave = 0
    same = 0
    for i in range(len(seq) - 1):
        if seq[i] != seq[i+1]:
            interleave += 1
        else:
            same += 1
    return interleave, same

# Observed interleaving
all_sequences = []
total_interleave = 0
total_same = 0

for (folio, line), words in lines.items():
    seq = get_energy_sequence(words)
    if len(seq) >= 2:
        all_sequences.append(seq)
        inter, same = count_transitions(seq)
        total_interleave += inter
        total_same += same

total_transitions = total_interleave + total_same
observed_rate = total_interleave / total_transitions if total_transitions > 0 else 0

print(f"\nObserved transitions: {total_transitions}")
print(f"Interleaving: {total_interleave} ({observed_rate:.1%})")
print(f"Same-family: {total_same} ({1-observed_rate:.1%})")

print("\n" + "-" * 40)
print("NULL MODEL: RANDOM SHUFFLE")
print("-" * 40)

# Monte Carlo: shuffle each sequence and measure interleaving
N_SIMULATIONS = 10000
random.seed(42)

shuffled_rates = []
for _ in range(N_SIMULATIONS):
    sim_interleave = 0
    sim_total = 0

    for seq in all_sequences:
        shuffled = list(seq)
        random.shuffle(shuffled)
        inter, same = count_transitions(shuffled)
        sim_interleave += inter
        sim_total += inter + same

    if sim_total > 0:
        shuffled_rates.append(sim_interleave / sim_total)

mean_null = np.mean(shuffled_rates)
std_null = np.std(shuffled_rates)

print(f"\nNull distribution (N={N_SIMULATIONS} simulations):")
print(f"  Mean: {mean_null:.1%}")
print(f"  Std: {std_null:.3%}")
print(f"  95% CI: [{np.percentile(shuffled_rates, 2.5):.1%}, {np.percentile(shuffled_rates, 97.5):.1%}]")

# Z-score and p-value
z_score = (observed_rate - mean_null) / std_null if std_null > 0 else 0
p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed

print(f"\nObserved rate: {observed_rate:.1%}")
print(f"Z-score: {z_score:.2f}")
print(f"p-value: {p_value:.6f}")

print("\n" + "-" * 40)
print("THEORETICAL EXPECTATION")
print("-" * 40)

# Theoretical: if p(Q) and p(C) are known, expected interleaving is 2*p(Q)*p(C)
total_q = sum(seq.count('Q') for seq in all_sequences)
total_c = sum(seq.count('C') for seq in all_sequences)
total_qc = total_q + total_c

p_q = total_q / total_qc if total_qc > 0 else 0.5
p_c = total_c / total_qc if total_qc > 0 else 0.5

expected_interleave = 2 * p_q * p_c

print(f"\np(Q) = {p_q:.3f}, p(C) = {p_c:.3f}")
print(f"Theoretical expected interleaving: {expected_interleave:.1%}")
print(f"Observed interleaving: {observed_rate:.1%}")
print(f"Observed / Expected: {observed_rate / expected_interleave:.2f}x" if expected_interleave > 0 else "")

print("\n" + "-" * 40)
print("BY-REGIME ANALYSIS")
print("-" * 40)

# Load REGIME
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

regime_stats = defaultdict(lambda: {'interleave': 0, 'same': 0})

for (folio, line), words in lines.items():
    regime = folio_regime.get(folio)
    if not regime:
        continue

    seq = get_energy_sequence(words)
    if len(seq) >= 2:
        inter, same = count_transitions(seq)
        regime_stats[regime]['interleave'] += inter
        regime_stats[regime]['same'] += same

print("\n| REGIME | Interleave | Same | Rate | vs Expected |")
print("|--------|------------|------|------|-------------|")

for regime in sorted(regime_stats.keys()):
    data = regime_stats[regime]
    total = data['interleave'] + data['same']
    rate = data['interleave'] / total if total > 0 else 0
    vs_exp = rate / expected_interleave if expected_interleave > 0 else 0
    print(f"| {regime} | {data['interleave']:5d} | {data['same']:4d} | {rate:.1%} | {vs_exp:.2f}x |")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if p_value < 0.001:
    sig = "HIGHLY SIGNIFICANT (p < 0.001)"
elif p_value < 0.01:
    sig = "SIGNIFICANT (p < 0.01)"
elif p_value < 0.05:
    sig = "SIGNIFICANT (p < 0.05)"
else:
    sig = "NOT SIGNIFICANT"

print(f"\nInterleaving rate: {observed_rate:.1%}")
print(f"Expected (null): {mean_null:.1%}")
print(f"Z-score: {z_score:.2f}")
print(f"Status: {sig}")

if observed_rate > mean_null and p_value < 0.01:
    print("\n=> SUPPORTED: qo/ch-sh interleaving is ABOVE random expectation")
    print(f"   Excess interleaving: {(observed_rate - mean_null)*100:.1f} percentage points")
elif observed_rate < mean_null and p_value < 0.01:
    print("\n=> OPPOSITE: qo/ch-sh interleaving is BELOW random expectation")
    print("   Same-family sequences are preferred")
else:
    print("\n=> NULL: Interleaving rate matches random expectation")

# Save results
results = {
    'observed_rate': observed_rate,
    'null_mean': mean_null,
    'null_std': std_null,
    'z_score': z_score,
    'p_value': p_value,
    'theoretical_expected': expected_interleave,
    'total_transitions': total_transitions,
    'total_interleave': total_interleave,
    'total_same': total_same,
    'regime_rates': {r: regime_stats[r]['interleave'] / (regime_stats[r]['interleave'] + regime_stats[r]['same'])
                     if (regime_stats[r]['interleave'] + regime_stats[r]['same']) > 0 else 0
                     for r in regime_stats}
}

with open(RESULTS / 'interleaving_significance.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'interleaving_significance.json'}")
