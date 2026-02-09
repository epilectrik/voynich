"""
110_mnemonic_falsification.py

MNEMONIC FALSIFICATION TEST

Test whether Voynich convergence pattern is compatible with mnemonic/indexing systems.

Components:
1. Measure actual Voynich convergence (entropy of endpoints from each starting class)
2. Baseline: Random transition matrices with same sparsity - expected convergence?
3. Functional mnemonic simulation: What convergence does a toy mnemonic system show?

If Voynich convergence >> random baseline AND >> mnemonic ceiling, mnemonic is falsified.
"""

import sys
import random
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("MNEMONIC FALSIFICATION TEST")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Load instruction class mapping
import json
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)

# The structure is {"token_to_class": {word: class_num, ...}}
word_to_class = class_data.get('token_to_class', {})

def get_class(word):
    """Get instruction class for a word."""
    # First try direct lookup
    if word in word_to_class:
        return f"C{word_to_class[word]}"
    # Try via MIDDLE
    try:
        m = morph.extract(word)
        if m.middle and m.middle in word_to_class:
            return f"C{word_to_class[m.middle]}"
    except:
        pass
    return None

# =============================================================
# PART 1: MEASURE VOYNICH CONVERGENCE
# =============================================================
print("\n" + "="*70)
print("PART 1: VOYNICH ACTUAL CONVERGENCE")
print("="*70)

# Build transition matrix from B tokens
transitions = defaultdict(Counter)
b_tokens = [t for t in tx.currier_b() if t.word and '*' not in t.word]

prev_class = None
for t in b_tokens:
    curr_class = get_class(t.word)
    if curr_class and prev_class:
        transitions[prev_class][curr_class] += 1
    prev_class = curr_class

# Get all classes
all_classes = set(transitions.keys())
for targets in transitions.values():
    all_classes.update(targets.keys())
all_classes = sorted(all_classes)
n_classes = len(all_classes)

print(f"Instruction classes found: {n_classes}")

# Convert to probability matrix
trans_prob = {}
for src in all_classes:
    total = sum(transitions[src].values())
    if total > 0:
        trans_prob[src] = {tgt: count/total for tgt, count in transitions[src].items()}
    else:
        trans_prob[src] = {}

# Simulate random walks to find terminal distribution
def simulate_walks(trans_prob, classes, n_walks=1000, max_steps=50):
    """Simulate random walks and return terminal state distribution."""
    terminals = Counter()

    for start in classes:
        for _ in range(n_walks // len(classes)):
            state = start
            for _ in range(max_steps):
                if state not in trans_prob or not trans_prob[state]:
                    break
                # Sample next state
                targets = list(trans_prob[state].keys())
                probs = [trans_prob[state][t] for t in targets]
                state = random.choices(targets, weights=probs, k=1)[0]
            terminals[state] += 1

    return terminals

def entropy(counter):
    """Shannon entropy of a distribution."""
    total = sum(counter.values())
    if total == 0:
        return 0
    h = 0
    for count in counter.values():
        if count > 0:
            p = count / total
            h -= p * math.log2(p)
    return h

def convergence_rate(counter, top_k=1):
    """Fraction of walks ending in top-k states."""
    total = sum(counter.values())
    if total == 0:
        return 0
    top_counts = sorted(counter.values(), reverse=True)[:top_k]
    return sum(top_counts) / total

# Voynich terminal distribution
voynich_terminals = simulate_walks(trans_prob, all_classes, n_walks=5000)
voynich_entropy = entropy(voynich_terminals)
voynich_top1 = convergence_rate(voynich_terminals, 1)
voynich_top3 = convergence_rate(voynich_terminals, 3)

print(f"\nVoynich terminal state distribution:")
print(f"  Entropy: {voynich_entropy:.2f} bits (max possible: {math.log2(n_classes):.2f})")
print(f"  Top-1 convergence: {voynich_top1:.1%}")
print(f"  Top-3 convergence: {voynich_top3:.1%}")
print(f"  Distinct terminals: {len(voynich_terminals)}")

# Top terminal states
print(f"\nTop 5 terminal states:")
for state, count in voynich_terminals.most_common(5):
    print(f"  {state}: {count/sum(voynich_terminals.values()):.1%}")

# =============================================================
# PART 2: RANDOM MATRIX BASELINE
# =============================================================
print("\n" + "="*70)
print("PART 2: RANDOM MATRIX BASELINE")
print("="*70)

# Measure sparsity of Voynich transition matrix
total_possible = n_classes * n_classes
actual_transitions = sum(len(t) for t in transitions.values())
sparsity = actual_transitions / total_possible

print(f"Voynich transition matrix sparsity: {sparsity:.1%} ({actual_transitions}/{total_possible})")

# Generate random matrices with same sparsity
def generate_random_matrix(n_classes, sparsity):
    """Generate random transition matrix with given sparsity."""
    classes = [f"C{i}" for i in range(n_classes)]
    trans = {}
    for src in classes:
        # Randomly select targets based on sparsity
        n_targets = max(1, int(n_classes * sparsity * random.uniform(0.5, 1.5)))
        targets = random.sample(classes, min(n_targets, n_classes))
        # Random weights
        weights = [random.random() for _ in targets]
        total = sum(weights)
        trans[src] = {t: w/total for t, w in zip(targets, weights)}
    return trans, classes

random_entropies = []
random_top1s = []
random_top3s = []

print(f"\nGenerating 100 random matrices...")
for i in range(100):
    rand_trans, rand_classes = generate_random_matrix(n_classes, sparsity)
    rand_terminals = simulate_walks(rand_trans, rand_classes, n_walks=2000)
    random_entropies.append(entropy(rand_terminals))
    random_top1s.append(convergence_rate(rand_terminals, 1))
    random_top3s.append(convergence_rate(rand_terminals, 3))

print(f"\nRandom matrix baseline (n=100):")
print(f"  Entropy: {sum(random_entropies)/len(random_entropies):.2f} +/- {(max(random_entropies)-min(random_entropies))/2:.2f}")
print(f"  Top-1 convergence: {sum(random_top1s)/len(random_top1s):.1%} +/- {(max(random_top1s)-min(random_top1s))/2:.1%}")
print(f"  Top-3 convergence: {sum(random_top3s)/len(random_top3s):.1%} +/- {(max(random_top3s)-min(random_top3s))/2:.1%}")

# =============================================================
# PART 3: FUNCTIONAL MNEMONIC SIMULATION
# =============================================================
print("\n" + "="*70)
print("PART 3: FUNCTIONAL MNEMONIC SIMULATION")
print("="*70)

def generate_mnemonic_matrix(n_classes, n_targets=10):
    """
    Generate a mnemonic/indexing system.

    Key property: Multiple retrieval paths to DISTINCT targets.
    Structure: Hierarchical with n_targets terminal states.
    """
    classes = [f"C{i}" for i in range(n_classes)]
    targets = classes[:n_targets]  # First n_targets are terminal "memory items"
    navigators = classes[n_targets:]  # Rest are navigation nodes

    trans = {}

    # Terminal states have no outgoing transitions (you've retrieved the item)
    for t in targets:
        trans[t] = {}

    # Navigation nodes point to either other navigators or targets
    for nav in navigators:
        # Some paths go to targets, some to other navigators
        n_out = random.randint(2, 5)
        dests = random.sample(classes, min(n_out, len(classes)))
        weights = [random.random() for _ in dests]
        total = sum(weights)
        trans[nav] = {d: w/total for d, w in zip(dests, weights)}

    return trans, classes

mnemonic_entropies = []
mnemonic_top1s = []
mnemonic_top3s = []

print(f"Generating 100 mnemonic systems (10 target items each)...")
for i in range(100):
    mnem_trans, mnem_classes = generate_mnemonic_matrix(n_classes, n_targets=10)
    mnem_terminals = simulate_walks(mnem_trans, mnem_classes, n_walks=2000)
    mnemonic_entropies.append(entropy(mnem_terminals))
    mnemonic_top1s.append(convergence_rate(mnem_terminals, 1))
    mnemonic_top3s.append(convergence_rate(mnem_terminals, 3))

print(f"\nMnemonic system baseline (n=100, 10 targets):")
print(f"  Entropy: {sum(mnemonic_entropies)/len(mnemonic_entropies):.2f} +/- {(max(mnemonic_entropies)-min(mnemonic_entropies))/2:.2f}")
print(f"  Top-1 convergence: {sum(mnemonic_top1s)/len(mnemonic_top1s):.1%} +/- {(max(mnemonic_top1s)-min(mnemonic_top1s))/2:.1%}")
print(f"  Top-3 convergence: {sum(mnemonic_top3s)/len(mnemonic_top3s):.1%} +/- {(max(mnemonic_top3s)-min(mnemonic_top3s))/2:.1%}")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY: CONVERGENCE COMPARISON")
print("="*70)

print(f"""
                        Entropy    Top-1      Top-3
                        (bits)     Conv.      Conv.
Voynich actual:         {voynich_entropy:.2f}       {voynich_top1:.1%}      {voynich_top3:.1%}
Random baseline:        {sum(random_entropies)/len(random_entropies):.2f}       {sum(random_top1s)/len(random_top1s):.1%}      {sum(random_top3s)/len(random_top3s):.1%}
Mnemonic system:        {sum(mnemonic_entropies)/len(mnemonic_entropies):.2f}       {sum(mnemonic_top1s)/len(mnemonic_top1s):.1%}      {sum(mnemonic_top3s)/len(mnemonic_top3s):.1%}
Max possible entropy:   {math.log2(n_classes):.2f}

INTERPRETATION:
""")

if voynich_top1 > sum(mnemonic_top1s)/len(mnemonic_top1s) * 1.5:
    print("-> Voynich convergence EXCEEDS mnemonic ceiling")
    print("-> Mnemonic/indexing system is INCONSISTENT with observed structure")
else:
    print("-> Voynich convergence is within mnemonic range")
    print("-> Mnemonic hypothesis cannot be ruled out by convergence alone")

if voynich_top1 > sum(random_top1s)/len(random_top1s) * 1.5:
    print("-> Voynich convergence EXCEEDS random baseline")
    print("-> Convergence is a REAL structural property, not artifact")
else:
    print("-> Voynich convergence is similar to random matrices")
    print("-> Convergence may be artifact of matrix structure")
