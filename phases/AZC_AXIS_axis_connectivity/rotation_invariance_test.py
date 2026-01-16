#!/usr/bin/env python3
"""
ROTATION INVARIANCE TEST

We know:
- 18 restricted operators
- 9 are PLACEMENT-LOCKED (only appear in one placement)
- Some placements are permissive (C, P, S1)

Question: Is the token-placement binding:
- ABSOLUTE (phase-locked to diagram positions)?
- RELATIVE (topological, survives rotation)?
- HYBRID (some fixed, some flowing)?

Test: Rotate sequences within lines and measure:
1. Does placement-token binding break?
2. Do "forbidden" tokens leak into wrong placements?
3. Is legality preserved under cyclic permutation?
"""

import os
from collections import defaultdict, Counter
import random

os.chdir('C:/git/voynich')

print("=" * 70)
print("ROTATION INVARIANCE TEST")
print("Is permission tied to phase or topology?")
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

# Get AZC-only vocabulary
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in all_tokens if t.get('language', '') == 'A')
b_words = set(t['word'] for t in all_tokens if t.get('language', '') == 'B')
azc_only = azc_words - a_words - b_words

# AZC-only tokens
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

# Group by line
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# Get frequent tokens and their placement bindings
token_totals = Counter(t['word'] for t in azc_only_tokens)
frequent_tokens = {t for t, c in token_totals.items() if c >= 5}

# Build ACTUAL placement-token binding
actual_binding = defaultdict(Counter)
for t in azc_only_tokens:
    if t['word'] in frequent_tokens:
        p = t.get('placement', 'UNK')
        actual_binding[t['word']][p] += 1

# Identify placement-locked tokens (>80% in one placement)
placement_locked = {}
for token in frequent_tokens:
    counts = actual_binding[token]
    total = sum(counts.values())
    if total > 0:
        top_placement, top_count = counts.most_common(1)[0]
        if top_count / total >= 0.8:
            placement_locked[token] = top_placement

print(f"\nFound {len(placement_locked)} placement-locked tokens (>80% in one placement)")
print(f"Placement-locked bindings:")
for token, placement in sorted(placement_locked.items(), key=lambda x: x[1]):
    print(f"  {token:<15} -> {placement}")

# =========================================================================
# TEST 1: PLACEMENT SEQUENCE STRUCTURE
# =========================================================================

print("\n" + "=" * 70)
print("TEST 1: PLACEMENT SEQUENCE STRUCTURE")
print("What does the original placement sequence look like?")
print("=" * 70)

# Extract placement sequences per line
placement_sequences = []
for key, tokens in by_line.items():
    if len(tokens) >= 3:  # Need sequences
        seq = [t.get('placement', 'UNK') for t in tokens]
        placement_sequences.append(seq)

print(f"\nLines with 3+ tokens: {len(placement_sequences)}")

# Count placement bigrams
bigram_counts = Counter()
for seq in placement_sequences:
    for i in range(len(seq) - 1):
        bigram_counts[(seq[i], seq[i+1])] += 1

print(f"Unique placement bigrams: {len(bigram_counts)}")
print(f"\nTop 15 placement transitions:")
for (p1, p2), count in bigram_counts.most_common(15):
    print(f"  {p1} -> {p2}: {count}")

# =========================================================================
# TEST 2: ROTATION SIMULATION
# =========================================================================

print("\n" + "=" * 70)
print("TEST 2: ROTATION SIMULATION")
print("What happens to token-placement binding under rotation?")
print("=" * 70)

def rotate_sequence(seq, k):
    """Rotate sequence by k positions."""
    if len(seq) == 0:
        return seq
    k = k % len(seq)
    return seq[k:] + seq[:k]

# For each line, test all possible rotations
# Measure: how often do placement-locked tokens end up in their "home" placement?

def measure_binding_preservation(sequences, locked_tokens):
    """
    For each rotation, count how many placement-locked tokens
    end up in their designated placement.
    """
    results = []

    for rotation in range(max(len(s) for s in sequences)):
        correct = 0
        total = 0

        for tokens in sequences:
            # Get word and placement sequences
            words = [t['word'] for t in tokens]
            placements = [t.get('placement', 'UNK') for t in tokens]

            # Rotate placements (keeping words fixed)
            rotated_placements = rotate_sequence(placements, rotation)

            # Check binding preservation
            for i, word in enumerate(words):
                if word in locked_tokens:
                    total += 1
                    if rotated_placements[i] == locked_tokens[word]:
                        correct += 1

        if total > 0:
            results.append((rotation, correct, total, correct/total))

    return results

# Get raw token sequences per line
token_sequences = []
for key, tokens in by_line.items():
    if len(tokens) >= 3:
        token_sequences.append(tokens)

# Test rotation
rotation_results = measure_binding_preservation(token_sequences, placement_locked)

print(f"\nRotation effects on placement-locked tokens:")
print(f"{'Rotation':<10} {'Correct':<10} {'Total':<10} {'Preservation%':<15}")
print("-" * 50)

for rotation, correct, total, rate in rotation_results[:10]:
    marker = "*** ORIGINAL ***" if rotation == 0 else ""
    print(f"{rotation:<10} {correct:<10} {total:<10} {rate*100:<15.1f} {marker}")

# =========================================================================
# TEST 3: ROTATION INVARIANCE SCORE
# =========================================================================

print("\n" + "=" * 70)
print("TEST 3: ROTATION INVARIANCE SCORE")
print("=" * 70)

if rotation_results:
    original_rate = rotation_results[0][3]
    other_rates = [r[3] for r in rotation_results[1:] if r[2] > 0]

    if other_rates:
        mean_rotated = sum(other_rates) / len(other_rates)
        max_rotated = max(other_rates)
        min_rotated = min(other_rates)

        print(f"\nOriginal binding preservation: {original_rate*100:.1f}%")
        print(f"Mean under rotation: {mean_rotated*100:.1f}%")
        print(f"Max under rotation: {max_rotated*100:.1f}%")
        print(f"Min under rotation: {min_rotated*100:.1f}%")

        # Invariance score: how much does rotation matter?
        drop = original_rate - mean_rotated

        print(f"\nBinding drop under rotation: {drop*100:.1f} percentage points")

        if drop < 0.05:
            invariance = "ROTATION-INVARIANT"
            meaning = "Binding is TOPOLOGICAL, not positional"
        elif drop < 0.15:
            invariance = "PARTIALLY-INVARIANT"
            meaning = "Some bindings are positional, some topological"
        else:
            invariance = "ROTATION-SENSITIVE"
            meaning = "Binding is PHASE-LOCKED to absolute position"

        print(f"\nVERDICT: {invariance}")
        print(f"Meaning: {meaning}")

# =========================================================================
# TEST 4: WHICH TOKENS ARE INVARIANT?
# =========================================================================

print("\n" + "=" * 70)
print("TEST 4: PER-TOKEN ROTATION SENSITIVITY")
print("=" * 70)

def measure_per_token_invariance(sequences, locked_tokens):
    """Measure rotation sensitivity per token."""
    token_scores = {t: {'original': 0, 'rotated': 0, 'total_orig': 0, 'total_rot': 0}
                   for t in locked_tokens}

    for tokens in sequences:
        words = [t['word'] for t in tokens]
        placements = [t.get('placement', 'UNK') for t in tokens]

        # Original (rotation 0)
        for i, word in enumerate(words):
            if word in locked_tokens:
                token_scores[word]['total_orig'] += 1
                if placements[i] == locked_tokens[word]:
                    token_scores[word]['original'] += 1

        # All other rotations
        for rot in range(1, len(tokens)):
            rotated_placements = rotate_sequence(placements, rot)
            for i, word in enumerate(words):
                if word in locked_tokens:
                    token_scores[word]['total_rot'] += 1
                    if rotated_placements[i] == locked_tokens[word]:
                        token_scores[word]['rotated'] += 1

    return token_scores

token_sensitivity = measure_per_token_invariance(token_sequences, placement_locked)

print(f"\n{'Token':<15} {'Home':<8} {'Orig%':<10} {'Rot%':<10} {'Drop':<10} {'Status':<15}")
print("-" * 75)

for token in sorted(placement_locked.keys()):
    scores = token_sensitivity[token]
    home = placement_locked[token]

    orig_rate = scores['original'] / scores['total_orig'] * 100 if scores['total_orig'] > 0 else 0
    rot_rate = scores['rotated'] / scores['total_rot'] * 100 if scores['total_rot'] > 0 else 0
    drop = orig_rate - rot_rate

    if drop < 5:
        status = "INVARIANT"
    elif drop < 15:
        status = "PARTIAL"
    else:
        status = "PHASE-LOCKED"

    print(f"{token:<15} {home:<8} {orig_rate:<10.1f} {rot_rate:<10.1f} {drop:<10.1f} {status:<15}")

# =========================================================================
# TEST 5: PLACEMENT ROLE UNDER ROTATION
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5: PLACEMENT BEHAVIOR UNDER ROTATION")
print("Do exception placements (C, P, S1) stay exceptional?")
print("=" * 70)

def measure_placement_permissiveness(sequences, locked_tokens):
    """Count how many locked tokens each placement allows under rotation."""
    results = defaultdict(lambda: {'original': set(), 'rotated': set()})

    for tokens in sequences:
        words = [t['word'] for t in tokens]
        placements = [t.get('placement', 'UNK') for t in tokens]

        # Original
        for i, word in enumerate(words):
            if word in locked_tokens:
                results[placements[i]]['original'].add(word)

        # Rotations
        for rot in range(1, len(tokens)):
            rotated_placements = rotate_sequence(placements, rot)
            for i, word in enumerate(words):
                if word in locked_tokens:
                    results[rotated_placements[i]]['rotated'].add(word)

    return results

placement_permissiveness = measure_placement_permissiveness(token_sequences, placement_locked)

print(f"\n{'Placement':<10} {'Orig Tokens':<15} {'Rot Tokens':<15} {'Change':<10}")
print("-" * 55)

for p in sorted(placement_permissiveness.keys()):
    orig = len(placement_permissiveness[p]['original'])
    rot = len(placement_permissiveness[p]['rotated'])
    change = rot - orig
    change_str = f"+{change}" if change > 0 else str(change)
    print(f"{p:<10} {orig:<15} {rot:<15} {change_str:<10}")

# =========================================================================
# VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("ROTATION INVARIANCE VERDICT")
print("=" * 70)

if rotation_results:
    original_rate = rotation_results[0][3]
    other_rates = [r[3] for r in rotation_results[1:] if r[2] > 0]

    if other_rates:
        mean_rotated = sum(other_rates) / len(other_rates)
        drop = original_rate - mean_rotated

        print(f"""
KEY METRICS:
  Original binding preservation: {original_rate*100:.1f}%
  Mean under all rotations: {mean_rotated*100:.1f}%
  Binding drop: {drop*100:.1f} percentage points

INTERPRETATION:
""")

        if drop < 0.05:
            print("""
  ROTATION-INVARIANT

  The token-placement binding is TOPOLOGICAL:
  - Relative position matters, not absolute phase
  - "Start" point is arbitrary
  - The system is phase-free

  This implies:
  - Cyclic/circular organization
  - No fixed entry point
  - Diagram anchoring NOT required
""")
        elif drop < 0.15:
            print("""
  PARTIALLY-INVARIANT

  The token-placement binding is HYBRID:
  - Some bindings are absolute (phase-locked)
  - Some bindings are relative (topological)
  - Mixed architecture

  This implies:
  - Fixed interface points inside cyclic process
  - Some anchoring required, some flexible
  - Nested control structure
""")
        else:
            print("""
  ROTATION-SENSITIVE

  The token-placement binding is PHASE-LOCKED:
  - Absolute position matters
  - Rotation breaks legality
  - Start point is meaningful

  This implies:
  - Diagram-anchored positions
  - Fixed entry point required
  - Visual correlation likely significant
""")

print("=" * 70)
print("ROTATION INVARIANCE TEST COMPLETE")
print("=" * 70)
