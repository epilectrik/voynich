#!/usr/bin/env python3
"""
Test 26: Do Rosettes Circles Have Distinct Vocabulary?

If Brewer-Lewis is right (9 circles = 9 anatomical chambers),
each circle might have specialized vocabulary for its function.

If circles are generic labels, vocabulary should be uniform.

Test:
1. Extract vocabulary per circle (sub-folio)
2. Calculate pairwise Jaccard similarity
3. Check for circle-unique tokens
4. Compare to null expectation (random B folios)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ROSETTES = ['f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']

print("=" * 70)
print("TEST 26: DO ROSETTES CIRCLES HAVE DISTINCT VOCABULARY?")
print("=" * 70)
print()

# 1. Extract vocabulary per circle
print("1. VOCABULARY PER CIRCLE")
print("-" * 50)

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

circle_tokens = defaultdict(list)
circle_middles = defaultdict(set)
circle_prefixes = defaultdict(set)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                circle_tokens[folio].append(token)
                m = morph.extract(token)
                if m:
                    if m.middle:
                        circle_middles[folio].add(m.middle)
                    if m.prefix:
                        circle_prefixes[folio].add(m.prefix)

for folio in ROSETTES:
    n_tokens = len(circle_tokens[folio])
    n_middles = len(circle_middles[folio])
    n_prefixes = len(circle_prefixes[folio])
    print(f"  {folio}: {n_tokens} tokens, {n_middles} unique MIDDLEs, {n_prefixes} unique PREFIXes")

print()

# 2. Pairwise Jaccard similarity (MIDDLEs)
print("2. PAIRWISE JACCARD SIMILARITY (MIDDLEs)")
print("-" * 50)

jaccard_matrix = {}
jaccard_values = []

for f1, f2 in combinations(ROSETTES, 2):
    m1 = circle_middles[f1]
    m2 = circle_middles[f2]

    if m1 or m2:
        intersection = len(m1 & m2)
        union = len(m1 | m2)
        jaccard = intersection / union if union > 0 else 0
    else:
        jaccard = 0

    jaccard_matrix[(f1, f2)] = jaccard
    jaccard_values.append(jaccard)

# Print matrix
print("Jaccard similarity matrix:")
print()
print(f"{'':>10}", end='')
for f in ROSETTES:
    print(f"{f[-4:]:>8}", end='')
print()

for f1 in ROSETTES:
    print(f"{f1[-4:]:>10}", end='')
    for f2 in ROSETTES:
        if f1 == f2:
            print(f"{'1.00':>8}", end='')
        elif (f1, f2) in jaccard_matrix:
            print(f"{jaccard_matrix[(f1, f2)]:>8.2f}", end='')
        elif (f2, f1) in jaccard_matrix:
            print(f"{jaccard_matrix[(f2, f1)]:>8.2f}", end='')
        else:
            print(f"{'?':>8}", end='')
    print()

print()
print(f"Mean Jaccard: {np.mean(jaccard_values):.3f}")
print(f"Std Jaccard: {np.std(jaccard_values):.3f}")
print(f"Min Jaccard: {np.min(jaccard_values):.3f}")
print(f"Max Jaccard: {np.max(jaccard_values):.3f}")

print()

# 3. Circle-unique tokens
print("3. CIRCLE-UNIQUE MIDDLEs")
print("-" * 50)

all_middles = set()
for middles in circle_middles.values():
    all_middles.update(middles)

for folio in ROSETTES:
    other_middles = set()
    for f, middles in circle_middles.items():
        if f != folio:
            other_middles.update(middles)

    unique = circle_middles[folio] - other_middles
    pct = len(unique) / len(circle_middles[folio]) * 100 if circle_middles[folio] else 0

    print(f"  {folio}: {len(unique)} unique MIDDLEs ({pct:.1f}%)")
    if unique and len(unique) <= 10:
        print(f"    Examples: {', '.join(sorted(unique)[:10])}")

print()

# 4. Compare to random B folio pairs
print("4. COMPARISON TO RANDOM B FOLIO PAIRS")
print("-" * 50)

# Get some random B folios for comparison
b_folios = defaultdict(set)
for token in tx.currier_b():
    if token.folio not in ROSETTES:
        m = morph.extract(token.word)
        if m and m.middle:
            b_folios[token.folio].add(m.middle)

# Sample pairwise Jaccard from B folios
b_folio_list = [f for f in b_folios.keys() if len(b_folios[f]) >= 20]
b_jaccards = []

for f1, f2 in list(combinations(b_folio_list, 2))[:100]:  # Sample 100 pairs
    m1 = b_folios[f1]
    m2 = b_folios[f2]
    intersection = len(m1 & m2)
    union = len(m1 | m2)
    jaccard = intersection / union if union > 0 else 0
    b_jaccards.append(jaccard)

print(f"Rosettes circle pairs mean Jaccard: {np.mean(jaccard_values):.3f}")
print(f"Random B folio pairs mean Jaccard: {np.mean(b_jaccards):.3f}")
print()

if np.mean(jaccard_values) > np.mean(b_jaccards) * 1.5:
    print("FINDING: Rosettes circles are MORE similar to each other than random B folios")
    print("-> Circles use SHARED vocabulary, not differentiated")
elif np.mean(jaccard_values) < np.mean(b_jaccards) * 0.7:
    print("FINDING: Rosettes circles are LESS similar to each other than random B folios")
    print("-> Circles have DISTINCT vocabulary, supporting differentiation")
else:
    print("FINDING: Rosettes circles have SIMILAR differentiation to random B folios")
    print("-> No evidence for special differentiation OR homogeneity")

print()

# 5. PREFIX differentiation
print("5. PREFIX DIFFERENTIATION BY CIRCLE")
print("-" * 50)

for folio in ROSETTES:
    prefixes = circle_prefixes[folio]
    tokens = circle_tokens[folio]

    # Count prefix frequencies
    prefix_counts = Counter()
    for token in tokens:
        m = morph.extract(token)
        if m and m.prefix:
            prefix_counts[m.prefix] += 1

    top3 = prefix_counts.most_common(3)
    top3_str = ', '.join(f"{p}({c})" for p, c in top3)
    print(f"  {folio}: {top3_str}")

print()

# 6. Synthesis
print("=" * 70)
print("SYNTHESIS")
print("=" * 70)

mean_jaccard = np.mean(jaccard_values)
mean_b_jaccard = np.mean(b_jaccards)

print(f"""
ROSETTES CIRCLE VOCABULARY ANALYSIS:

Mean within-Rosettes Jaccard: {mean_jaccard:.3f}
Mean random B folio Jaccard: {mean_b_jaccard:.3f}
Ratio: {mean_jaccard / mean_b_jaccard:.2f}x

INTERPRETATION:
""")

if mean_jaccard > 0.4:
    print("""
HIGH SIMILARITY (Jaccard > 0.4):
Circles share most of their vocabulary.
This suggests GENERIC LABELING, not chamber-specific content.

The text on each circle may be:
- Generic procedural vocabulary repeated
- Labels that don't encode chamber-specific information
- A shared vocabulary pool applied uniformly

This WEAKENS the Brewer-Lewis hypothesis (from text perspective).
The circles may be anatomically distinct in the IMAGES,
but the TEXT doesn't differentiate them.
""")
elif mean_jaccard < 0.2:
    print("""
LOW SIMILARITY (Jaccard < 0.2):
Circles have distinct vocabulary.
This suggests CHAMBER-SPECIFIC content.

Each circle may encode:
- Different treatments for different anatomical regions
- Specialized vocabulary for each chamber's function

This SUPPORTS differentiation hypothesis.
""")
else:
    print("""
MODERATE SIMILARITY (0.2 < Jaccard < 0.4):
Circles have some shared and some distinct vocabulary.
Partial differentiation - some generic, some specific.
""")
