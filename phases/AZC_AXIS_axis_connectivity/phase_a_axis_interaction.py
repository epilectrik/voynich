#!/usr/bin/env python3
"""
PHASE A: AXIS INTERACTION TESTS

Tests whether POSITION constrains WHAT (token legality).

Test A1: Conditional Grammar Collapse
Test A2: Placement-Conditioned Forbidden Tokens
Test A3: Kernel Sensitivity
Test A4: Cross-Axis Predictability
"""

import os
from collections import defaultdict, Counter
import math
import random

os.chdir('C:/git/voynich')

print("=" * 70)
print("PHASE A: AXIS INTERACTION TESTS")
print("Does WHERE constrain WHAT?")
print("=" * 70)

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip('\"') != 'H':
            continue
        all_tokens.append(row)

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Get vocabularies
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in all_tokens if t.get('language', '') == 'A')
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words

# AZC-only tokens with placement
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

print(f"\nLoaded {len(azc_only_tokens)} AZC-only tokens")

# Group by line for sequence analysis
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# Get placement classes
all_placements = sorted(set(t.get('placement', 'UNK') for t in azc_only_tokens))
all_azc_tokens = sorted(set(t['word'] for t in azc_only_tokens))

print(f"Placement classes: {len(all_placements)}")
print(f"Unique AZC-only tokens: {len(all_azc_tokens)}")

# =========================================================================
# TEST A1: CONDITIONAL GRAMMAR COLLAPSE
# =========================================================================

print("\n" + "=" * 70)
print("TEST A1: CONDITIONAL GRAMMAR COLLAPSE")
print("Does token grammar CHANGE by placement class?")
print("=" * 70)

# Build transition matrices per placement
placement_transitions = defaultdict(lambda: defaultdict(Counter))

for key, tokens in by_line.items():
    for i in range(len(tokens) - 1):
        p = tokens[i].get('placement', 'UNK')
        t1 = tokens[i]['word']
        t2 = tokens[i+1]['word']
        placement_transitions[p][t1][t2] += 1

# Calculate entropy per placement
def transition_entropy(trans_matrix):
    """Calculate average transition entropy for a transition matrix."""
    total_transitions = 0
    weighted_entropy = 0

    for t1, outcomes in trans_matrix.items():
        total = sum(outcomes.values())
        if total == 0:
            continue
        total_transitions += total

        # Entropy for this source token
        h = 0
        for count in outcomes.values():
            if count > 0:
                p = count / total
                h -= p * math.log2(p)
        weighted_entropy += total * h

    return weighted_entropy / total_transitions if total_transitions > 0 else 0

# Overall transition matrix (no placement conditioning)
overall_transitions = defaultdict(Counter)
for p_trans in placement_transitions.values():
    for t1, outcomes in p_trans.items():
        overall_transitions[t1].update(outcomes)

overall_entropy = transition_entropy(overall_transitions)

print(f"\nOverall token transition entropy: {overall_entropy:.3f} bits")
print(f"\nPer-placement transition entropy:")
print(f"{'Placement':<10} {'Transitions':<12} {'Entropy':<10} {'vs Overall':<12}")
print("-" * 50)

placement_entropies = {}
for p in sorted(all_placements):
    if p in placement_transitions:
        trans = placement_transitions[p]
        n_trans = sum(sum(outcomes.values()) for outcomes in trans.values())
        if n_trans >= 20:  # Minimum sample
            h = transition_entropy(trans)
            placement_entropies[p] = h
            diff = h - overall_entropy
            direction = "REDUCED" if diff < -0.1 else "EXPANDED" if diff > 0.1 else "SIMILAR"
            print(f"{p:<10} {n_trans:<12} {h:<10.3f} {diff:>+.3f} ({direction})")

# Summary
reduced = sum(1 for h in placement_entropies.values() if h < overall_entropy - 0.1)
expanded = sum(1 for h in placement_entropies.values() if h > overall_entropy + 0.1)

print(f"\nSummary:")
print(f"  Placements with REDUCED grammar: {reduced}")
print(f"  Placements with EXPANDED grammar: {expanded}")
print(f"  Placements with SIMILAR grammar: {len(placement_entropies) - reduced - expanded}")

if reduced > 0:
    print(f"\n  *** GRAMMAR COLLAPSE DETECTED in {reduced} placements ***")
    print(f"  -> Position constrains action legality")

# =========================================================================
# TEST A2: PLACEMENT-CONDITIONED FORBIDDEN TOKENS
# =========================================================================

print("\n" + "=" * 70)
print("TEST A2: PLACEMENT-CONDITIONED FORBIDDEN TOKENS")
print("Are some tokens ILLEGAL in some placements?")
print("=" * 70)

# Count tokens per placement
placement_token_counts = defaultdict(Counter)
for t in azc_only_tokens:
    p = t.get('placement', 'UNK')
    placement_token_counts[p][t['word']] += 1

# Find tokens that appear frequently overall but NEVER in certain placements
token_totals = Counter(t['word'] for t in azc_only_tokens)
frequent_tokens = {t for t, c in token_totals.items() if c >= 5}

print(f"\nFrequent tokens (5+ occurrences): {len(frequent_tokens)}")

# For each placement, find frequent tokens that are absent
placement_forbidden = {}
for p in all_placements:
    if sum(placement_token_counts[p].values()) >= 30:  # Significant placement
        present = set(placement_token_counts[p].keys())
        absent = frequent_tokens - present
        if absent:
            placement_forbidden[p] = absent

print(f"\nPlacements with forbidden frequent tokens:")
print(f"{'Placement':<10} {'Forbidden':<10} {'Examples':<50}")
print("-" * 70)

total_forbidden_pairs = 0
for p in sorted(placement_forbidden.keys()):
    absent = placement_forbidden[p]
    total_forbidden_pairs += len(absent)
    examples = list(absent)[:5]
    print(f"{p:<10} {len(absent):<10} {', '.join(examples):<50}")

# Null model: shuffle tokens among placements
print(f"\n--- Null model comparison ---")
random.seed(42)
null_forbidden_counts = []

for _ in range(100):
    # Shuffle placement assignments
    shuffled = azc_only_tokens.copy()
    placements_shuffled = [t.get('placement', 'UNK') for t in shuffled]
    random.shuffle(placements_shuffled)

    # Recount
    null_counts = defaultdict(Counter)
    for i, t in enumerate(shuffled):
        null_counts[placements_shuffled[i]][t['word']] += 1

    # Count forbidden pairs
    null_forbidden = 0
    for p in all_placements:
        if sum(null_counts[p].values()) >= 30:
            present = set(null_counts[p].keys())
            absent = frequent_tokens - present
            null_forbidden += len(absent)
    null_forbidden_counts.append(null_forbidden)

mean_null = sum(null_forbidden_counts) / len(null_forbidden_counts)
std_null = (sum((x - mean_null)**2 for x in null_forbidden_counts) / len(null_forbidden_counts)) ** 0.5

print(f"Observed forbidden pairs: {total_forbidden_pairs}")
print(f"Null model mean: {mean_null:.1f} (+/- {std_null:.1f})")
z_score = (total_forbidden_pairs - mean_null) / std_null if std_null > 0 else 0
print(f"Z-score: {z_score:.2f}")

if z_score > 2:
    print(f"\n  *** SIGNIFICANT: Tokens are placement-forbidden beyond chance ***")
    print(f"  -> WHERE constrains WHAT")
elif z_score < -2:
    print(f"\n  Tokens are LESS forbidden than chance (unexpected)")
else:
    print(f"\n  Forbidden pattern is within null expectation")

# =========================================================================
# TEST A3: KERNEL SENSITIVITY
# =========================================================================

print("\n" + "=" * 70)
print("TEST A3: KERNEL SENSITIVITY")
print("Does placement affect kernel operator usage?")
print("=" * 70)

# In AZC context, we look at shared vocabulary that includes kernel-like patterns
# The B kernels are k, h, e - check for tokens containing these in AZC

# Get shared vocabulary (appears in both AZC and B)
shared_vocab = azc_words.intersection(b_words)

# Load B grammar info if available, otherwise use pattern matching
kernel_patterns = ['ok', 'yk', 'ak', 'ek', 'ch', 'sh', 'oh', 'ah', 'eh']
link_patterns = ['ol', 'al', 'or', 'ar']

# Count kernel-like and link-like tokens per placement in shared vocabulary
shared_tokens_in_azc = [t for t in azc_tokens if t['word'] in shared_vocab]

placement_kernel = defaultdict(lambda: {'kernel': 0, 'link': 0, 'other': 0, 'total': 0})

for t in shared_tokens_in_azc:
    p = t.get('placement', 'UNK')
    word = t['word']
    placement_kernel[p]['total'] += 1

    if any(word.startswith(kp) or word.endswith(kp) for kp in kernel_patterns):
        placement_kernel[p]['kernel'] += 1
    elif any(word.startswith(lp) or word.endswith(lp) for lp in link_patterns):
        placement_kernel[p]['link'] += 1
    else:
        placement_kernel[p]['other'] += 1

print(f"\nKernel/Link density by placement (shared vocabulary only):")
print(f"{'Placement':<10} {'Total':<8} {'Kernel%':<10} {'Link%':<10} {'Pattern':<15}")
print("-" * 55)

for p in sorted(placement_kernel.keys()):
    stats = placement_kernel[p]
    if stats['total'] >= 50:
        kernel_pct = stats['kernel'] / stats['total'] * 100
        link_pct = stats['link'] / stats['total'] * 100

        if kernel_pct > 30:
            pattern = "KERNEL-RICH"
        elif link_pct > 30:
            pattern = "LINK-RICH"
        elif kernel_pct < 10:
            pattern = "KERNEL-SPARSE"
        else:
            pattern = "BALANCED"

        print(f"{p:<10} {stats['total']:<8} {kernel_pct:<10.1f} {link_pct:<10.1f} {pattern:<15}")

# Check boundary vs interior
boundary_placements = {'S1', 'S2', 'X', 'L', 'S'}  # From earlier analysis
interior_placements = {'R1', 'R2', 'R3', 'C', 'P'}

boundary_kernel = sum(placement_kernel[p]['kernel'] for p in boundary_placements)
boundary_total = sum(placement_kernel[p]['total'] for p in boundary_placements)
interior_kernel = sum(placement_kernel[p]['kernel'] for p in interior_placements)
interior_total = sum(placement_kernel[p]['total'] for p in interior_placements)

if boundary_total > 0 and interior_total > 0:
    boundary_rate = boundary_kernel / boundary_total * 100
    interior_rate = interior_kernel / interior_total * 100

    print(f"\nBoundary vs Interior kernel density:")
    print(f"  Boundary placements (S1,S2,X,L,S): {boundary_rate:.1f}%")
    print(f"  Interior placements (R1,R2,R3,C,P): {interior_rate:.1f}%")

    if abs(boundary_rate - interior_rate) > 10:
        print(f"\n  *** KERNEL SENSITIVITY DETECTED ***")
        if boundary_rate < interior_rate:
            print(f"  -> Kernel SUPPRESSED at boundaries")
        else:
            print(f"  -> Kernel CONCENTRATED at boundaries")

# =========================================================================
# TEST A4: CROSS-AXIS PREDICTABILITY
# =========================================================================

print("\n" + "=" * 70)
print("TEST A4: CROSS-AXIS PREDICTABILITY")
print("H(next_token | token, placement) vs H(next_token | token)")
print("=" * 70)

# Already have overall transition entropy
# Now calculate H(next_token | token, placement)

def conditional_joint_entropy(trans_by_placement):
    """Calculate H(next_token | token, placement)."""
    total = 0
    weighted_h = 0

    for p, trans in trans_by_placement.items():
        for t1, outcomes in trans.items():
            n = sum(outcomes.values())
            if n == 0:
                continue
            total += n

            h = 0
            for count in outcomes.values():
                if count > 0:
                    prob = count / n
                    h -= prob * math.log2(prob)
            weighted_h += n * h

    return weighted_h / total if total > 0 else 0

h_token_given_token = overall_entropy
h_token_given_token_and_placement = conditional_joint_entropy(placement_transitions)

print(f"\nEntropy comparison:")
print(f"  H(next_token | token):              {h_token_given_token:.3f} bits")
print(f"  H(next_token | token, placement):   {h_token_given_token_and_placement:.3f} bits")

reduction = h_token_given_token - h_token_given_token_and_placement
reduction_pct = reduction / h_token_given_token * 100 if h_token_given_token > 0 else 0

print(f"\n  Information gain from placement: {reduction:.3f} bits ({reduction_pct:.1f}%)")

if reduction > 0.1:
    print(f"\n  *** PLACEMENT IS A CONDITIONING VARIABLE ***")
    print(f"  -> Knowing WHERE reduces uncertainty about WHAT comes next")
    print(f"  -> Position defines local affordances")
else:
    print(f"\n  Placement provides minimal additional predictive power")

# =========================================================================
# PHASE A VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("PHASE A VERDICT: AXIS INTERACTION")
print("=" * 70)

evidence_count = 0

print("\nTest Results Summary:")

# A1
if reduced > 0:
    evidence_count += 1
    print(f"  A1 Grammar Collapse:     YES ({reduced} placements show reduced grammar)")
else:
    print(f"  A1 Grammar Collapse:     NO")

# A2
if z_score > 2:
    evidence_count += 1
    print(f"  A2 Forbidden Tokens:     YES (z={z_score:.1f}, beyond chance)")
else:
    print(f"  A2 Forbidden Tokens:     NO (z={z_score:.1f})")

# A3
if boundary_total > 0 and interior_total > 0 and abs(boundary_rate - interior_rate) > 10:
    evidence_count += 1
    print(f"  A3 Kernel Sensitivity:   YES ({abs(boundary_rate - interior_rate):.1f}% difference)")
else:
    print(f"  A3 Kernel Sensitivity:   NO")

# A4
if reduction > 0.1:
    evidence_count += 1
    print(f"  A4 Cross-Axis Predict:   YES ({reduction:.2f} bits gain)")
else:
    print(f"  A4 Cross-Axis Predict:   NO ({reduction:.2f} bits)")

print(f"\n  Evidence score: {evidence_count}/4")

if evidence_count >= 3:
    print(f"""
  STRONG AXIS INTERACTION CONFIRMED.

  Position (WHERE) constrains Token (WHAT):
  - Grammar changes by placement
  - Some tokens forbidden in some positions
  - Placement conditions execution

  This is the signature of:
  > POSITION DEFINES LOCAL AFFORDANCES

  The axes are NOT independent - they interact.
""")
elif evidence_count >= 2:
    print(f"""
  MODERATE AXIS INTERACTION detected.

  Some evidence that position constrains tokens,
  but not overwhelming.
""")
else:
    print(f"""
  WEAK/NO AXIS INTERACTION.

  Position and token appear largely independent.
  The axes operate in parallel without strong coupling.
""")

print("=" * 70)
print("PHASE A COMPLETE")
print("=" * 70)
