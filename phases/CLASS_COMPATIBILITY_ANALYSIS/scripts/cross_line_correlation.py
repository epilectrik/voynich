"""
Test: Do adjacent A lines have correlated class survival patterns?

If A records span multiple lines, we'd expect:
- Adjacent lines to have similar/correlated class budgets
- Morphological "completion" across line boundaries

If A records are line-atomic, we'd expect:
- No correlation between adjacent line class budgets
- Each line is independent
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CROSS-LINE CORRELATION TEST")
print("Are adjacent A lines independent or correlated?")
print("=" * 70)

# Build B token data
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        }

b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

# Build A records by folio and line
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

# Extract morphology per record
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

# Compute surviving classes per record
def get_surviving_classes(prefixes, middles, suffixes):
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, info in b_tokens.items():
        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            # Use PREFIX-based classification
            if info['prefix']:
                surviving.add(f"P_{info['prefix']}")
            elif info['suffix']:
                surviving.add(f"S_{info['suffix']}")
            else:
                surviving.add("BARE")

    return surviving

record_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    record_classes[(folio, line)] = get_surviving_classes(prefixes, middles, suffixes)

print(f"\nA records: {len(record_classes)}")

# Group by folio and sort by line
folio_lines = defaultdict(list)
for (folio, line) in record_classes.keys():
    folio_lines[folio].append(line)

for folio in folio_lines:
    folio_lines[folio].sort()

print(f"Folios: {len(folio_lines)}")

# Compute Jaccard similarity between adjacent lines
def jaccard(set1, set2):
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

adjacent_jaccards = []
non_adjacent_jaccards = []

for folio, lines in folio_lines.items():
    if len(lines) < 2:
        continue

    # Adjacent pairs
    for i in range(len(lines) - 1):
        line1, line2 = lines[i], lines[i+1]
        classes1 = record_classes.get((folio, line1), set())
        classes2 = record_classes.get((folio, line2), set())
        if classes1 and classes2:  # Only if both have classes
            j = jaccard(classes1, classes2)
            adjacent_jaccards.append(j)

    # Non-adjacent pairs (same folio, skip 1 line)
    for i in range(len(lines) - 2):
        line1, line3 = lines[i], lines[i+2]
        classes1 = record_classes.get((folio, line1), set())
        classes3 = record_classes.get((folio, line3), set())
        if classes1 and classes3:
            j = jaccard(classes1, classes3)
            non_adjacent_jaccards.append(j)

print(f"\n--- Class Jaccard Similarity ---")
print(f"Adjacent line pairs: {len(adjacent_jaccards)}")
print(f"  Mean Jaccard: {np.mean(adjacent_jaccards):.3f}")
print(f"  Std: {np.std(adjacent_jaccards):.3f}")

print(f"\nNon-adjacent pairs (skip 1): {len(non_adjacent_jaccards)}")
print(f"  Mean Jaccard: {np.mean(non_adjacent_jaccards):.3f}")
print(f"  Std: {np.std(non_adjacent_jaccards):.3f}")

# Statistical test: are adjacent more similar than non-adjacent?
if adjacent_jaccards and non_adjacent_jaccards:
    t_stat, p_value = stats.ttest_ind(adjacent_jaccards, non_adjacent_jaccards)
    print(f"\nT-test (adjacent vs non-adjacent):")
    print(f"  t = {t_stat:.3f}, p = {p_value:.4f}")

    if p_value < 0.05 and np.mean(adjacent_jaccards) > np.mean(non_adjacent_jaccards):
        print("  -> Adjacent lines ARE more similar (suggests multi-line records)")
    else:
        print("  -> No significant difference (supports line atomicity)")

# Also check: random pairs from different folios
cross_folio_jaccards = []
folio_list = list(folio_lines.keys())
import random
random.seed(42)

for _ in range(min(1000, len(adjacent_jaccards))):
    f1, f2 = random.sample(folio_list, 2)
    l1 = random.choice(folio_lines[f1])
    l2 = random.choice(folio_lines[f2])
    classes1 = record_classes.get((f1, l1), set())
    classes2 = record_classes.get((f2, l2), set())
    if classes1 and classes2:
        j = jaccard(classes1, classes2)
        cross_folio_jaccards.append(j)

print(f"\nCross-folio random pairs: {len(cross_folio_jaccards)}")
print(f"  Mean Jaccard: {np.mean(cross_folio_jaccards):.3f}")

# Compare adjacent to cross-folio
if adjacent_jaccards and cross_folio_jaccards:
    t_stat, p_value = stats.ttest_ind(adjacent_jaccards, cross_folio_jaccards)
    print(f"\nT-test (adjacent vs cross-folio):")
    print(f"  t = {t_stat:.3f}, p = {p_value:.4f}")

# Check morphological overlap between adjacent lines
print("\n" + "=" * 70)
print("MORPHOLOGICAL OVERLAP BETWEEN ADJACENT LINES")
print("=" * 70)

adj_middle_overlap = []
adj_prefix_overlap = []
adj_suffix_overlap = []

for folio, lines in folio_lines.items():
    for i in range(len(lines) - 1):
        line1, line2 = lines[i], lines[i+1]
        if (folio, line1) in record_morphology and (folio, line2) in record_morphology:
            pref1, mid1, suf1 = record_morphology[(folio, line1)]
            pref2, mid2, suf2 = record_morphology[(folio, line2)]

            if mid1 and mid2:
                adj_middle_overlap.append(jaccard(mid1, mid2))
            if pref1 and pref2:
                adj_prefix_overlap.append(jaccard(pref1, pref2))
            if suf1 and suf2:
                adj_suffix_overlap.append(jaccard(suf1, suf2))

print(f"\nAdjacent line morphological Jaccard:")
print(f"  MIDDLE overlap: {np.mean(adj_middle_overlap):.3f} (n={len(adj_middle_overlap)})")
print(f"  PREFIX overlap: {np.mean(adj_prefix_overlap):.3f} (n={len(adj_prefix_overlap)})")
print(f"  SUFFIX overlap: {np.mean(adj_suffix_overlap):.3f} (n={len(adj_suffix_overlap)})")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

adj_mean = np.mean(adjacent_jaccards)
non_adj_mean = np.mean(non_adjacent_jaccards) if non_adjacent_jaccards else 0
cross_mean = np.mean(cross_folio_jaccards) if cross_folio_jaccards else 0

print(f"""
CLASS SURVIVAL JACCARD:
  Adjacent lines: {adj_mean:.3f}
  Non-adjacent (skip 1): {non_adj_mean:.3f}
  Cross-folio random: {cross_mean:.3f}

INTERPRETATION:
""")

if abs(adj_mean - non_adj_mean) < 0.05 and abs(adj_mean - cross_mean) < 0.1:
    print("Adjacent lines are NOT significantly more similar than random.")
    print("This SUPPORTS LINE ATOMICITY - each line is an independent record.")
elif adj_mean > non_adj_mean + 0.1:
    print("Adjacent lines ARE more similar than non-adjacent.")
    print("This might suggest some multi-line record structure.")
else:
    print("Results are ambiguous - moderate correlation exists.")
    print("Line atomicity is neither strongly confirmed nor refuted.")
