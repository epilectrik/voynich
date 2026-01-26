"""
C508 RETEST - Token-Level Discrimination Primacy Under Full Morphology

Original C508 claim (MIDDLE-only filtering):
- Class Jaccard = 0.391 (coarse, universal)
- Token Jaccard = 0.700 (fine, discriminative)
- Class mutual exclusion = 0%
- "A records differ in HOW MANY classes survive, not WHICH classes"

Question: Does this hold under full morphological filtering (PREFIX+MIDDLE+SUFFIX)?
With only ~7 classes surviving, does "which" now matter?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from itertools import combinations

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("C508 RETEST: CLASS-LEVEL DISCRIMINATION UNDER FULL MORPHOLOGY")
print("=" * 70)

# Step 1: Build B token inventory with full morphology
print("\nStep 1: Building B token morphology inventory...")

b_tokens = {}  # word -> (prefix, middle, suffix, class)
for token in tx.currier_b():
    word = token.word
    if word not in b_tokens:
        m = morph.extract(word)
        if m.middle:
            # Assign class based on prefix (simplified, matches class_survival_retest.py)
            if m.prefix:
                cls = f"P_{m.prefix}"
            elif m.suffix:
                cls = f"S_{m.suffix}"
            else:
                cls = "BARE"
            b_tokens[word] = (m.prefix, m.middle, m.suffix, cls)

all_b_classes = set(c for p, m, s, c in b_tokens.values())
print(f"  B token types: {len(b_tokens)}")
print(f"  B classes: {len(all_b_classes)}")

# Step 2: Build A record morphology
print("\nStep 2: Building A record morphology...")

a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

print(f"  A records: {len(record_morphology)}")

# Step 3: Compute class survival under MIDDLE-only vs full morphology
print("\nStep 3: Computing class survival sets...")

b_middles = set(m for p, m, s, c in b_tokens.values())
b_prefixes = set(p for p, m, s, c in b_tokens.values() if p)
b_suffixes = set(s for p, m, s, c in b_tokens.values() if s)

middle_only_classes = {}  # record -> set of surviving classes
full_morph_classes = {}   # record -> set of surviving classes
full_morph_tokens = {}    # record -> set of surviving tokens

for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    # MIDDLE-only filtering
    mid_classes = set()
    for word, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            mid_classes.add(cls)
    middle_only_classes[(folio, line)] = mid_classes

    # Full morphology filtering
    full_classes = set()
    full_tokens = set()
    for word, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                full_classes.add(cls)
                full_tokens.add(word)
    full_morph_classes[(folio, line)] = full_classes
    full_morph_tokens[(folio, line)] = full_tokens

# Step 4: Compute class-level statistics
print("\n" + "=" * 70)
print("CLASS-LEVEL STATISTICS")
print("=" * 70)

def compute_jaccard(set1, set2):
    if len(set1) == 0 and len(set2) == 0:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return 1.0 - (intersection / union) if union > 0 else 0.0

# Sample pairs for Jaccard computation (too many pairs to compute all)
records = list(record_morphology.keys())
np.random.seed(42)
n_samples = min(5000, len(records) * (len(records) - 1) // 2)
sample_pairs = []
for _ in range(n_samples):
    i, j = np.random.choice(len(records), 2, replace=False)
    sample_pairs.append((records[i], records[j]))

# MIDDLE-only class Jaccard
mid_class_jaccards = []
for r1, r2 in sample_pairs:
    j = compute_jaccard(middle_only_classes[r1], middle_only_classes[r2])
    mid_class_jaccards.append(j)

# Full morphology class Jaccard
full_class_jaccards = []
for r1, r2 in sample_pairs:
    j = compute_jaccard(full_morph_classes[r1], full_morph_classes[r2])
    full_class_jaccards.append(j)

# Full morphology token Jaccard
full_token_jaccards = []
for r1, r2 in sample_pairs:
    j = compute_jaccard(full_morph_tokens[r1], full_morph_tokens[r2])
    full_token_jaccards.append(j)

print(f"\nJaccard Distance (higher = more different):")
print(f"  MIDDLE-only class:    {np.mean(mid_class_jaccards):.3f} +/- {np.std(mid_class_jaccards):.3f}")
print(f"  Full morph class:     {np.mean(full_class_jaccards):.3f} +/- {np.std(full_class_jaccards):.3f}")
print(f"  Full morph token:     {np.mean(full_token_jaccards):.3f} +/- {np.std(full_token_jaccards):.3f}")

print(f"\nOriginal C508 (for comparison):")
print(f"  Class Jaccard:  0.391")
print(f"  Token Jaccard:  0.700")

# Step 5: Mutual exclusion analysis
print("\n" + "=" * 70)
print("MUTUAL EXCLUSION ANALYSIS")
print("=" * 70)

# Count class co-occurrence
class_cooccur_mid = defaultdict(int)
class_cooccur_full = defaultdict(int)

for (folio, line) in records:
    for c in middle_only_classes[(folio, line)]:
        class_cooccur_mid[c] += 1
    for c in full_morph_classes[(folio, line)]:
        class_cooccur_full[c] += 1

# Check for mutually exclusive classes
n_records = len(records)

print(f"\nMIDDLE-only class occurrence:")
mid_always = [c for c, cnt in class_cooccur_mid.items() if cnt == n_records]
mid_never = [c for c in all_b_classes if class_cooccur_mid[c] == 0]
mid_partial = [c for c, cnt in class_cooccur_mid.items() if 0 < cnt < n_records]
print(f"  Always present: {len(mid_always)}")
print(f"  Never present:  {len(mid_never)}")
print(f"  Partial:        {len(mid_partial)}")

print(f"\nFull morphology class occurrence:")
full_always = [c for c, cnt in class_cooccur_full.items() if cnt == n_records]
full_never = [c for c in all_b_classes if class_cooccur_full[c] == 0]
full_partial = [c for c, cnt in class_cooccur_full.items() if 0 < cnt < n_records]
print(f"  Always present: {len(full_always)}")
print(f"  Never present:  {len(full_never)}")
print(f"  Partial:        {len(full_partial)}")

# Compute mutual exclusion rate for classes
print("\n" + "=" * 70)
print("CLASS MUTUAL EXCLUSION TEST")
print("=" * 70)

# For each pair of classes, check if they ever co-occur
class_pairs_mid = defaultdict(int)
class_pairs_full = defaultdict(int)

for (folio, line) in records:
    mid_set = middle_only_classes[(folio, line)]
    full_set = full_morph_classes[(folio, line)]

    for c1, c2 in combinations(sorted(mid_set), 2):
        class_pairs_mid[(c1, c2)] += 1

    for c1, c2 in combinations(sorted(full_set), 2):
        class_pairs_full[(c1, c2)] += 1

# Count mutually exclusive pairs (never co-occur but both exist somewhere)
all_mid_classes = set(c for s in middle_only_classes.values() for c in s)
all_full_classes = set(c for s in full_morph_classes.values() for c in s)

mid_possible_pairs = list(combinations(sorted(all_mid_classes), 2))
full_possible_pairs = list(combinations(sorted(all_full_classes), 2))

mid_exclusive = sum(1 for p in mid_possible_pairs if class_pairs_mid[p] == 0)
full_exclusive = sum(1 for p in full_possible_pairs if class_pairs_full[p] == 0)

print(f"\nMIDDLE-only:")
print(f"  Classes present in at least one record: {len(all_mid_classes)}")
print(f"  Possible class pairs: {len(mid_possible_pairs)}")
print(f"  Mutually exclusive pairs: {mid_exclusive} ({100*mid_exclusive/len(mid_possible_pairs) if mid_possible_pairs else 0:.1f}%)")

print(f"\nFull morphology:")
print(f"  Classes present in at least one record: {len(all_full_classes)}")
print(f"  Possible class pairs: {len(full_possible_pairs)}")
print(f"  Mutually exclusive pairs: {full_exclusive} ({100*full_exclusive/len(full_possible_pairs) if full_possible_pairs else 0:.1f}%)")

print(f"\nOriginal C508 class mutual exclusion: 0%")

# Step 6: Within-class token mutual exclusion (for comparison)
print("\n" + "=" * 70)
print("TOKEN-LEVEL MUTUAL EXCLUSION (within same class)")
print("=" * 70)

# Group tokens by class
class_to_tokens = defaultdict(set)
for word, (pref, mid, suf, cls) in b_tokens.items():
    class_to_tokens[cls].add(word)

# For each class, check token co-occurrence
token_cooccur = defaultdict(int)
for (folio, line) in records:
    tokens = full_morph_tokens[(folio, line)]
    for t in tokens:
        token_cooccur[t] += 1

# Check within-class mutual exclusion
within_class_exclusive = 0
within_class_total = 0

for cls, tokens in class_to_tokens.items():
    present_tokens = [t for t in tokens if token_cooccur[t] > 0]
    if len(present_tokens) < 2:
        continue

    # Check pairs within this class
    for t1, t2 in combinations(sorted(present_tokens), 2):
        within_class_total += 1
        # Check if they ever co-occur
        cooccur_count = 0
        for (folio, line) in records:
            if t1 in full_morph_tokens[(folio, line)] and t2 in full_morph_tokens[(folio, line)]:
                cooccur_count += 1
        if cooccur_count == 0:
            within_class_exclusive += 1

print(f"\nWithin-class token pairs: {within_class_total}")
print(f"Mutually exclusive: {within_class_exclusive} ({100*within_class_exclusive/within_class_total if within_class_total else 0:.1f}%)")
print(f"\nOriginal C508 token mutual exclusion: 27.5%")

# Step 7: Summary
print("\n" + "=" * 70)
print("SUMMARY: C508 RETEST RESULTS")
print("=" * 70)

print(f"""
                        | Original C508 | MIDDLE-only | Full Morph |
                        | (MIDDLE-only) | (retest)    | (new)      |
------------------------+---------------+-------------+------------|
Class Jaccard           |     0.391     |    {np.mean(mid_class_jaccards):.3f}    |   {np.mean(full_class_jaccards):.3f}    |
Token Jaccard           |     0.700     |      -      |   {np.mean(full_token_jaccards):.3f}    |
Class mutual exclusion  |       0%      |    {100*mid_exclusive/len(mid_possible_pairs) if mid_possible_pairs else 0:.1f}%    |   {100*full_exclusive/len(full_possible_pairs) if full_possible_pairs else 0:.1f}%    |
Token mutual exclusion  |     27.5%     |      -      |   {100*within_class_exclusive/within_class_total if within_class_total else 0:.1f}%    |
""")

# Interpretation
mid_class_j = np.mean(mid_class_jaccards)
full_class_j = np.mean(full_class_jaccards)
full_token_j = np.mean(full_token_jaccards)
full_class_me = 100*full_exclusive/len(full_possible_pairs) if full_possible_pairs else 0

print("INTERPRETATION:")
if full_class_j > 0.5 and full_class_me > 5:
    print("""
  C508's claim "A records differ in HOW MANY, not WHICH" is WEAKENED.

  Under full morphology:
  - Class Jaccard is substantial ({:.3f}) - classes ARE differentiated
  - Class mutual exclusion is non-trivial ({:.1f}%) - some classes DON'T co-occur
  - The "which" DOES matter, not just "how many"

  REVISION NEEDED: C508 should note that under full morphological filtering,
  class-level discrimination becomes significant, not just token-level.
""".format(full_class_j, full_class_me))
elif full_class_j > mid_class_j * 1.2:
    print("""
  C508's claim is PARTIALLY WEAKENED.

  Class Jaccard increased from {:.3f} to {:.3f} under full morphology.
  This suggests more class-level differentiation, though token-level
  still dominates ({:.3f} token vs {:.3f} class Jaccard).

  REVISION SUGGESTED: Note that full morphology increases class-level
  discrimination, though token-level remains primary.
""".format(mid_class_j, full_class_j, full_token_j, full_class_j))
else:
    print("""
  C508's claim HOLDS under full morphology.

  Class-level patterns remain coarse even with severe filtering.
  Token-level discrimination ({:.3f}) still dominates class-level ({:.3f}).

  NO REVISION NEEDED.
""".format(full_token_j, full_class_j))

# Mean class counts
mid_counts = [len(s) for s in middle_only_classes.values()]
full_counts = [len(s) for s in full_morph_classes.values()]
print(f"\nClass survival summary:")
print(f"  MIDDLE-only: {np.mean(mid_counts):.1f} +/- {np.std(mid_counts):.1f} classes")
print(f"  Full morph:  {np.mean(full_counts):.1f} +/- {np.std(full_counts):.1f} classes")
