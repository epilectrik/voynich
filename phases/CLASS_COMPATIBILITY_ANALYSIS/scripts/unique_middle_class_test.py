"""
UNIQUE MIDDLE CLASS TEST

1. Do unique MIDDLEs belong to the 49 instruction classes?
2. Do unique MIDDLEs in adjacent folios fill the same grammatical slots?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    data = json.load(f)

# Get token -> class mapping directly
token_to_class = {token: int(cls) for token, cls in data['token_to_class'].items()}

print("=" * 70)
print("UNIQUE MIDDLE CLASS ANALYSIS")
print("=" * 70)

# Build per-folio token data
folio_tokens = defaultdict(list)
folio_middles = defaultdict(set)

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        folio_tokens[token.folio].append({
            'word': word,
            'middle': m.middle,
            'class': token_to_class.get(word, None)
        })
        if m.middle:
            folio_middles[token.folio].add(m.middle)

folio_order = list(folio_middles.keys())

# Identify unique MIDDLEs
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

unique_middles = {m for m, count in middle_folio_count.items() if count == 1}
print(f"\nUnique MIDDLEs: {len(unique_middles)}")

# Question 1: Do unique MIDDLEs belong to 49 classes?
print("\n" + "=" * 70)
print("Q1: DO UNIQUE MIDDLEs BELONG TO THE 49 CLASSES?")
print("=" * 70)

# For each token with unique MIDDLE, check if it has a class
unique_middle_tokens = []
for folio, tokens in folio_tokens.items():
    for t in tokens:
        if t['middle'] in unique_middles:
            unique_middle_tokens.append(t)

tokens_with_class = [t for t in unique_middle_tokens if t['class'] is not None]
tokens_without_class = [t for t in unique_middle_tokens if t['class'] is None]

print(f"\nTokens with unique MIDDLEs: {len(unique_middle_tokens)}")
print(f"  With class assignment: {len(tokens_with_class)} ({100*len(tokens_with_class)/len(unique_middle_tokens):.1f}%)")
print(f"  Without class: {len(tokens_without_class)} ({100*len(tokens_without_class)/len(unique_middle_tokens):.1f}%)")

# Class distribution of unique MIDDLE tokens
unique_class_dist = Counter(t['class'] for t in tokens_with_class)
print(f"\nClasses used by unique MIDDLE tokens: {len(unique_class_dist)}")
print(f"\nTop 10 classes for unique MIDDLE tokens:")
for cls, count in unique_class_dist.most_common(10):
    pct = 100 * count / len(tokens_with_class)
    print(f"  Class {cls}: {count} ({pct:.1f}%)")

# Compare to overall B class distribution
all_class_dist = Counter(t['class'] for t in sum(folio_tokens.values(), []) if t['class'] is not None)
print(f"\nTop 10 classes overall in B:")
for cls, count in all_class_dist.most_common(10):
    pct = 100 * count / sum(all_class_dist.values())
    print(f"  Class {cls}: {count} ({pct:.1f}%)")

# Question 2: Do adjacent folios' unique MIDDLEs fill the same slots?
print("\n" + "=" * 70)
print("Q2: DO ADJACENT FOLIOS' UNIQUE MIDDLEs FILL THE SAME SLOTS?")
print("=" * 70)

def get_unique_middle_classes(folio):
    """Get class distribution of tokens with unique MIDDLEs in this folio."""
    classes = Counter()
    for t in folio_tokens[folio]:
        if t['middle'] in unique_middles and t['class'] is not None:
            classes[t['class']] += 1
    return classes

def class_overlap(dist1, dist2):
    """Jaccard overlap of class sets."""
    set1 = set(dist1.keys())
    set2 = set(dist2.keys())
    if not set1 and not set2:
        return 1.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0

# Compare adjacent pairs
adjacent_overlaps = []
for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    dist1 = get_unique_middle_classes(f1)
    dist2 = get_unique_middle_classes(f2)
    if dist1 and dist2:
        overlap = class_overlap(dist1, dist2)
        adjacent_overlaps.append((f1, f2, overlap, dist1, dist2))

# Compare non-adjacent pairs (sample)
import random
random.seed(42)
nonadjacent_overlaps = []
for _ in range(len(adjacent_overlaps)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        dist1 = get_unique_middle_classes(f1)
        dist2 = get_unique_middle_classes(f2)
        if dist1 and dist2:
            nonadjacent_overlaps.append(class_overlap(dist1, dist2))

adj_mean = np.mean([o[2] for o in adjacent_overlaps])
nonadj_mean = np.mean(nonadjacent_overlaps)

print(f"\nClass overlap (Jaccard) for unique MIDDLE tokens:")
print(f"  Adjacent folios: {adj_mean:.3f}")
print(f"  Non-adjacent folios: {nonadj_mean:.3f}")
print(f"  Ratio: {adj_mean/nonadj_mean:.2f}x")

# Show some examples
print(f"\nSample adjacent pairs (class overlap):")
for f1, f2, overlap, dist1, dist2 in adjacent_overlaps[:5]:
    classes1 = sorted(dist1.keys())
    classes2 = sorted(dist2.keys())
    shared = set(classes1) & set(classes2)
    print(f"  {f1} - {f2}: overlap={overlap:.2f}")
    print(f"    {f1} classes: {classes1}")
    print(f"    {f2} classes: {classes2}")
    print(f"    Shared: {sorted(shared)}")

# Check if unique MIDDLEs use ALL 49 classes or a subset
print("\n" + "=" * 70)
print("CLASS COVERAGE")
print("=" * 70)

all_unique_classes = set(unique_class_dist.keys())
print(f"\nTotal classes in 49-class system: 49")
print(f"Classes used by unique MIDDLE tokens: {len(all_unique_classes)}")
print(f"Classes NOT used: {49 - len(all_unique_classes)}")

unused = set(range(1, 50)) - all_unique_classes
if unused:
    print(f"\nUnused classes: {sorted(unused)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
Q1: Do unique MIDDLEs belong to the 49 classes?
  - {100*len(tokens_with_class)/len(unique_middle_tokens):.1f}% of unique MIDDLE tokens have class assignments
  - They use {len(all_unique_classes)} of 49 classes
  - Top classes: {[c for c, _ in unique_class_dist.most_common(5)]}

Q2: Do adjacent folios' unique MIDDLEs fill same slots?
  - Adjacent class overlap: {adj_mean:.3f}
  - Non-adjacent overlap: {nonadj_mean:.3f}
  - Ratio: {adj_mean/nonadj_mean:.2f}x

INTERPRETATION:
""")

if adj_mean > nonadj_mean * 1.1:
    print("""
Adjacent folios' unique MIDDLEs DO fill similar grammatical slots.
This suggests unique MIDDLEs are grammatically interchangeable -
different "words" serving the same grammatical function.

Like different ingredients in the same recipe step:
  "add [herb X]" vs "add [herb Y]" - same slot, different content.
""")
else:
    print("""
Adjacent folios' unique MIDDLEs do NOT preferentially fill same slots.
Class usage is similar to random pairs.
""")
