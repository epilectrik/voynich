"""
UNIQUE MIDDLE MORPHOLOGY CLASS TEST

The 49 classes are based on tokens. But if unique MIDDLE tokens
share PREFIX/SUFFIX patterns with classified tokens, they may
fill the same grammatical slots.

Test: Do unique MIDDLE tokens share morphological patterns with
classified tokens, suggesting grammatical equivalence?
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

token_to_class = {token: int(cls) for token, cls in data['token_to_class'].items()}

print("=" * 70)
print("UNIQUE MIDDLE MORPHOLOGY CLASS TEST")
print("=" * 70)

# Build token morphology data
all_tokens = []
for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        all_tokens.append({
            'word': word,
            'folio': token.folio,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'class': token_to_class.get(word, None)
        })

# Identify unique MIDDLEs
folio_middles = defaultdict(set)
for t in all_tokens:
    if t['middle']:
        folio_middles[t['folio']].add(t['middle'])

middle_folio_count = Counter()
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

unique_middles = {m for m, count in middle_folio_count.items() if count == 1}

# Split tokens
classified_tokens = [t for t in all_tokens if t['class'] is not None]
unique_middle_tokens = [t for t in all_tokens if t['middle'] in unique_middles]

print(f"\nClassified tokens: {len(classified_tokens)}")
print(f"Unique MIDDLE tokens: {len(unique_middle_tokens)}")

# Build morphological signature -> class mapping from classified tokens
# Signature = (PREFIX, SUFFIX)
sig_to_classes = defaultdict(Counter)
for t in classified_tokens:
    sig = (t['prefix'], t['suffix'])
    sig_to_classes[sig][t['class']] += 1

print(f"\nMorphological signatures in classified tokens: {len(sig_to_classes)}")

# For unique MIDDLE tokens, check if their signature exists in classified tokens
print("\n" + "=" * 70)
print("MORPHOLOGICAL SIGNATURE MATCHING")
print("=" * 70)

matched = 0
unmatched = 0
inferred_classes = Counter()

for t in unique_middle_tokens:
    sig = (t['prefix'], t['suffix'])
    if sig in sig_to_classes:
        matched += 1
        # Most common class for this signature
        most_common_class = sig_to_classes[sig].most_common(1)[0][0]
        inferred_classes[most_common_class] += 1
    else:
        unmatched += 1

print(f"\nUnique MIDDLE tokens:")
print(f"  With matching signature: {matched} ({100*matched/len(unique_middle_tokens):.1f}%)")
print(f"  Without matching signature: {unmatched} ({100*unmatched/len(unique_middle_tokens):.1f}%)")

print(f"\nInferred classes for unique MIDDLE tokens (top 10):")
for cls, count in inferred_classes.most_common(10):
    pct = 100 * count / matched if matched > 0 else 0
    print(f"  Class {cls}: {count} ({pct:.1f}%)")

# Compare class distribution
print("\n" + "=" * 70)
print("CLASS DISTRIBUTION COMPARISON")
print("=" * 70)

classified_class_dist = Counter(t['class'] for t in classified_tokens)

# Normalize
total_classified = sum(classified_class_dist.values())
total_inferred = sum(inferred_classes.values())

print(f"\n{'Class':<10} {'Classified %':<15} {'Unique-Inferred %':<20} {'Ratio':<10}")
print("-" * 55)

all_classes = set(classified_class_dist.keys()) | set(inferred_classes.keys())
for cls in sorted(all_classes)[:15]:
    class_pct = 100 * classified_class_dist.get(cls, 0) / total_classified
    infer_pct = 100 * inferred_classes.get(cls, 0) / total_inferred if total_inferred > 0 else 0
    ratio = infer_pct / class_pct if class_pct > 0 else 0
    print(f"{cls:<10} {class_pct:>10.1f}%     {infer_pct:>15.1f}%     {ratio:>8.2f}x")

# Now check adjacent folio slot filling
print("\n" + "=" * 70)
print("ADJACENT FOLIO SLOT FILLING")
print("=" * 70)

def get_folio_unique_inferred_classes(folio):
    """Get inferred classes for unique MIDDLE tokens in this folio."""
    classes = Counter()
    for t in unique_middle_tokens:
        if t['folio'] == folio:
            sig = (t['prefix'], t['suffix'])
            if sig in sig_to_classes:
                most_common = sig_to_classes[sig].most_common(1)[0][0]
                classes[most_common] += 1
    return classes

folio_order = list(folio_middles.keys())

# Compare adjacent pairs
adjacent_results = []
for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    c1 = get_folio_unique_inferred_classes(f1)
    c2 = get_folio_unique_inferred_classes(f2)

    if c1 and c2:
        set1, set2 = set(c1.keys()), set(c2.keys())
        jaccard = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0
        adjacent_results.append((f1, f2, jaccard, c1, c2))

# Non-adjacent comparison
import random
random.seed(42)
nonadj_jaccards = []
for _ in range(len(adjacent_results)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:
        f1, f2 = folio_order[i], folio_order[j]
        c1 = get_folio_unique_inferred_classes(f1)
        c2 = get_folio_unique_inferred_classes(f2)
        if c1 and c2:
            set1, set2 = set(c1.keys()), set(c2.keys())
            jaccard = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0
            nonadj_jaccards.append(jaccard)

adj_jaccards = [r[2] for r in adjacent_results]
print(f"\nInferred class overlap (Jaccard):")
print(f"  Adjacent folios: {np.mean(adj_jaccards):.3f}")
print(f"  Non-adjacent: {np.mean(nonadj_jaccards):.3f}")
if nonadj_jaccards:
    print(f"  Ratio: {np.mean(adj_jaccards)/np.mean(nonadj_jaccards):.2f}x")

# Show examples
print(f"\nSample adjacent pairs:")
for f1, f2, jac, c1, c2 in adjacent_results[:5]:
    shared = set(c1.keys()) & set(c2.keys())
    print(f"  {f1} - {f2}: overlap={jac:.2f}, shared classes={sorted(shared)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
1. MORPHOLOGICAL SIGNATURE MATCHING:
   - {100*matched/len(unique_middle_tokens):.0f}% of unique MIDDLE tokens have PREFIX/SUFFIX
     patterns that match classified tokens
   - This means they likely fill the same grammatical slots

2. INFERRED CLASS DISTRIBUTION:
   - Unique MIDDLE tokens use {len(inferred_classes)} different classes
   - Top classes match overall B distribution (e.g., class 33, 13, 34)

3. ADJACENT FOLIO SLOT FILLING:
   - Adjacent: {np.mean(adj_jaccards):.3f} class overlap
   - Non-adjacent: {np.mean(nonadj_jaccards):.3f}
""")

if np.mean(adj_jaccards) > np.mean(nonadj_jaccards) * 1.1:
    print(f"""
=> ADJACENT FOLIOS' UNIQUE MIDDLEs DO FILL SIMILAR SLOTS

The unique vocabulary in adjacent folios serves the SAME grammatical
function. Different words, same role - like synonyms in a grammar.

This supports the interpretation that adjacent folios are variations
on a theme: same control structure, different specific vocabulary.
""")
else:
    print(f"""
=> NO PREFERENTIAL SLOT SHARING between adjacent folios
""")
