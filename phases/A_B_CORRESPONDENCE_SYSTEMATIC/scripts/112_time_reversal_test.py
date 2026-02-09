"""
112_time_reversal_test.py

TIME-REVERSAL SYMMETRY TEST

Test whether Voynich grammar is symmetric under time reversal.

Sharp metrics:
1. KL divergence between forward and reversed transition matrices
2. Difference in hazard incidence rates
3. Difference in convergence rates

Comparisons:
- Known procedural text (we'll use assembly-like patterns)
- Known narrative text (we'll use story-like patterns)
- Shuffled Voynich (random order)

If Voynich clusters with procedural and away from narrative, time-symmetry is meaningful.
"""

import sys
import math
import random
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("TIME-REVERSAL SYMMETRY TEST")
print("="*70)

tx = Transcript()
morph = Morphology()

# Load instruction class mapping
import json
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)

word_to_class = class_data.get('token_to_class', {})

def get_class(word):
    if word in word_to_class:
        return f"C{word_to_class[word]}"
    try:
        m = morph.extract(word)
        if m.middle and m.middle in word_to_class:
            return f"C{word_to_class[m.middle]}"
    except:
        pass
    return None

# =============================================================
# METRIC FUNCTIONS
# =============================================================

def build_transition_matrix(sequence):
    """Build transition probability matrix from sequence."""
    transitions = defaultdict(Counter)
    for i in range(len(sequence) - 1):
        transitions[sequence[i]][sequence[i+1]] += 1

    # Normalize
    trans_prob = {}
    for src, targets in transitions.items():
        total = sum(targets.values())
        trans_prob[src] = {tgt: count/total for tgt, count in targets.items()}

    return trans_prob, transitions

def kl_divergence(p_matrix, q_matrix, all_classes):
    """
    KL divergence between two transition matrices.
    KL(P || Q) = sum_i sum_j P(i->j) * log(P(i->j) / Q(i->j))
    """
    eps = 1e-10
    kl = 0
    count = 0

    for src in all_classes:
        if src not in p_matrix:
            continue
        p_dist = p_matrix[src]
        q_dist = q_matrix.get(src, {})

        for tgt in p_dist:
            p_val = p_dist[tgt]
            q_val = q_dist.get(tgt, eps)
            if p_val > 0:
                kl += p_val * math.log(p_val / q_val)
                count += 1

    return kl, count

def symmetric_kl(p_matrix, q_matrix, all_classes):
    """Symmetric KL divergence (Jensen-Shannon style average)."""
    kl_pq, c1 = kl_divergence(p_matrix, q_matrix, all_classes)
    kl_qp, c2 = kl_divergence(q_matrix, p_matrix, all_classes)
    return (kl_pq + kl_qp) / 2

def transition_correlation(forward_trans, reverse_trans, all_classes):
    """
    Correlation between forward P(A->B) and reverse P(B->A).
    High correlation = time-symmetric grammar.
    """
    forward_probs = []
    reverse_probs = []

    for src in all_classes:
        if src not in forward_trans:
            continue
        for tgt in forward_trans[src]:
            p_forward = forward_trans[src][tgt]
            p_reverse = reverse_trans.get(tgt, {}).get(src, 0)
            forward_probs.append(p_forward)
            reverse_probs.append(p_reverse)

    if len(forward_probs) < 2:
        return 0

    # Pearson correlation
    n = len(forward_probs)
    mean_f = sum(forward_probs) / n
    mean_r = sum(reverse_probs) / n

    num = sum((f - mean_f) * (r - mean_r) for f, r in zip(forward_probs, reverse_probs))
    den_f = sum((f - mean_f)**2 for f in forward_probs) ** 0.5
    den_r = sum((r - mean_r)**2 for r in reverse_probs) ** 0.5

    if den_f * den_r == 0:
        return 0
    return num / (den_f * den_r)

def convergence_rate(sequence, top_k=3):
    """Measure convergence to dominant ending states."""
    # Look at last token of each "run" (every 20 tokens)
    endings = []
    for i in range(19, len(sequence), 20):
        endings.append(sequence[i])

    counter = Counter(endings)
    total = len(endings)
    if total == 0:
        return 0
    top_counts = sorted(counter.values(), reverse=True)[:top_k]
    return sum(top_counts) / total

def analyze_time_reversal(sequence, name=""):
    """Full time-reversal analysis of a sequence."""
    reversed_seq = sequence[::-1]

    # Get all classes
    all_classes = sorted(set(sequence))

    # Build matrices
    forward_prob, forward_raw = build_transition_matrix(sequence)
    reverse_prob, reverse_raw = build_transition_matrix(reversed_seq)

    # Metrics
    kl = symmetric_kl(forward_prob, reverse_prob, all_classes)
    corr = transition_correlation(forward_prob, reverse_prob, all_classes)
    conv_forward = convergence_rate(sequence)
    conv_reverse = convergence_rate(reversed_seq)
    conv_diff = abs(conv_forward - conv_reverse)

    return {
        'name': name,
        'kl_divergence': kl,
        'transition_correlation': corr,
        'convergence_forward': conv_forward,
        'convergence_reverse': conv_reverse,
        'convergence_diff': conv_diff,
        'n_classes': len(all_classes),
        'n_tokens': len(sequence)
    }

# =============================================================
# BUILD VOYNICH SEQUENCE
# =============================================================
print("\nBuilding Voynich class sequence...")

b_class_sequence = []
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        cls = get_class(t.word)
        if cls:
            b_class_sequence.append(cls)

print(f"Voynich B tokens: {len(b_class_sequence)}")

# =============================================================
# GENERATE COMPARISON SEQUENCES
# =============================================================
print("\nGenerating comparison sequences...")

def generate_procedural_sequence(n_tokens, n_classes=49):
    """
    Procedural/recipe-like sequence:
    - Loops (A->B->C->A)
    - State transitions both directions equally likely
    - Time-symmetric by design
    """
    classes = [f"C{i}" for i in range(1, n_classes+1)]
    seq = []

    # Define some loops
    loops = [
        classes[0:5],   # Loop 1
        classes[5:10],  # Loop 2
        classes[10:15], # Loop 3
    ]

    state = random.choice(classes)
    for _ in range(n_tokens):
        seq.append(state)
        # 30% chance: follow a loop
        # 70% chance: random transition
        if random.random() < 0.3:
            for loop in loops:
                if state in loop:
                    idx = loop.index(state)
                    # Go forward OR backward in loop (symmetric)
                    if random.random() < 0.5:
                        state = loop[(idx + 1) % len(loop)]
                    else:
                        state = loop[(idx - 1) % len(loop)]
                    break
        else:
            state = random.choice(classes)

    return seq

def generate_narrative_sequence(n_tokens, n_classes=49):
    """
    Narrative/story-like sequence:
    - Beginning, middle, end structure
    - Time-asymmetric: early states != late states
    - Forward progression, rare return to earlier states
    """
    classes = [f"C{i}" for i in range(1, n_classes+1)]
    seq = []

    # Divide classes into early/middle/late
    early = classes[:15]
    middle = classes[15:35]
    late = classes[35:]

    phase_boundaries = [n_tokens // 3, 2 * n_tokens // 3]

    state = random.choice(early)
    for i in range(n_tokens):
        seq.append(state)

        # Determine current phase
        if i < phase_boundaries[0]:
            # Early: mostly stay in early, small chance of middle
            if random.random() < 0.8:
                state = random.choice(early)
            else:
                state = random.choice(middle)
        elif i < phase_boundaries[1]:
            # Middle: stay in middle
            if random.random() < 0.1:
                state = random.choice(early)  # Rare flashback
            elif random.random() < 0.8:
                state = random.choice(middle)
            else:
                state = random.choice(late)
        else:
            # Late: stay in late, progress toward end
            if random.random() < 0.05:
                state = random.choice(early)  # Very rare return
            elif random.random() < 0.3:
                state = random.choice(middle)
            else:
                state = random.choice(late)

    return seq

# Generate sequences
n_tokens = len(b_class_sequence)
procedural_seq = generate_procedural_sequence(n_tokens)
narrative_seq = generate_narrative_sequence(n_tokens)
shuffled_seq = b_class_sequence.copy()
random.shuffle(shuffled_seq)

# =============================================================
# RUN ANALYSIS
# =============================================================
print("\nRunning time-reversal analysis...")

results = []
results.append(analyze_time_reversal(b_class_sequence, "Voynich B"))
results.append(analyze_time_reversal(procedural_seq, "Procedural (synthetic)"))
results.append(analyze_time_reversal(narrative_seq, "Narrative (synthetic)"))
results.append(analyze_time_reversal(shuffled_seq, "Shuffled Voynich"))

# =============================================================
# RESULTS
# =============================================================
print("\n" + "="*70)
print("RESULTS: TIME-REVERSAL METRICS")
print("="*70)

print(f"\n{'System':<25} {'KL Div':>10} {'Trans Corr':>12} {'Conv Diff':>10}")
print("-" * 60)
for r in results:
    print(f"{r['name']:<25} {r['kl_divergence']:>10.4f} {r['transition_correlation']:>12.3f} {r['convergence_diff']:>10.3f}")

print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

voynich = results[0]
procedural = results[1]
narrative = results[2]
shuffled = results[3]

print(f"""
KL DIVERGENCE (lower = more time-symmetric):
  Voynich:    {voynich['kl_divergence']:.4f}
  Procedural: {procedural['kl_divergence']:.4f}
  Narrative:  {narrative['kl_divergence']:.4f}
  Shuffled:   {shuffled['kl_divergence']:.4f}

TRANSITION CORRELATION P(A->B) vs P(B->A) (higher = more symmetric):
  Voynich:    {voynich['transition_correlation']:.3f}
  Procedural: {procedural['transition_correlation']:.3f}
  Narrative:  {narrative['transition_correlation']:.3f}
  Shuffled:   {shuffled['transition_correlation']:.3f}

CONVERGENCE DIFFERENCE |forward - reverse| (lower = more symmetric):
  Voynich:    {voynich['convergence_diff']:.3f}
  Procedural: {procedural['convergence_diff']:.3f}
  Narrative:  {narrative['convergence_diff']:.3f}
  Shuffled:   {shuffled['convergence_diff']:.3f}
""")

# Determine where Voynich clusters
print("CLUSTERING:")
procedural_dist = abs(voynich['kl_divergence'] - procedural['kl_divergence'])
narrative_dist = abs(voynich['kl_divergence'] - narrative['kl_divergence'])

if procedural_dist < narrative_dist:
    print(f"  Voynich is CLOSER to procedural (dist={procedural_dist:.4f}) than narrative (dist={narrative_dist:.4f})")
    print("  -> TIME-SYMMETRY finding SUPPORTED")
else:
    print(f"  Voynich is CLOSER to narrative (dist={narrative_dist:.4f}) than procedural (dist={procedural_dist:.4f})")
    print("  -> TIME-SYMMETRY finding NOT SUPPORTED")

# Overall verdict
print(f"\n" + "="*70)
print("VERDICT")
print("="*70)

symmetry_score = 0
if voynich['kl_divergence'] < narrative['kl_divergence']:
    print("+ KL divergence lower than narrative: TIME-SYMMETRIC")
    symmetry_score += 1
if voynich['transition_correlation'] > narrative['transition_correlation']:
    print("+ Transition correlation higher than narrative: TIME-SYMMETRIC")
    symmetry_score += 1
if voynich['convergence_diff'] < narrative['convergence_diff']:
    print("+ Convergence difference lower than narrative: TIME-SYMMETRIC")
    symmetry_score += 1

print(f"\nTIME-SYMMETRY SCORE: {symmetry_score}/3 (vs narrative baseline)")

if symmetry_score >= 2:
    print("-> Voynich grammar IS time-symmetric, inconsistent with narrative/language")
else:
    print("-> Time-symmetry claim NOT strongly supported")
