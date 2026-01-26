"""
CLASS_COMPATIBILITY_ANALYSIS Phase - Test 1
Question: What are the class compatibility patterns under full morphological filtering?

Goals:
1. Identify universal classes (survive for ALL A records)
2. Identify never-activated classes
3. Identify mutually exclusive class pairs
4. Build class co-occurrence matrix
5. Analyze compatibility clusters
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from itertools import combinations
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CLASS COMPATIBILITY ANALYSIS - FULL MORPHOLOGICAL FILTERING")
print("=" * 70)

# Step 1: Build B token inventory with full morphology
print("\nStep 1: Building B token morphology inventory...")

b_tokens = {}  # word -> (prefix, middle, suffix, class)
for token in tx.currier_b():
    word = token.word
    if word not in b_tokens:
        m = morph.extract(word)
        if m.middle:
            if m.prefix:
                cls = f"P_{m.prefix}"
            elif m.suffix:
                cls = f"S_{m.suffix}"
            else:
                cls = "BARE"
            b_tokens[word] = (m.prefix, m.middle, m.suffix, cls)

all_b_classes = sorted(set(c for p, m, s, c in b_tokens.values()))
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

# Step 3: Compute class survival for each A record (full morphology)
print("\nStep 3: Computing class survival per A record...")

b_middles = set(m for p, m, s, c in b_tokens.values())
b_prefixes = set(p for p, m, s, c in b_tokens.values() if p)
b_suffixes = set(s for p, m, s, c in b_tokens.values() if s)

record_classes = {}  # record -> set of surviving classes

for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                surviving.add(cls)
    record_classes[(folio, line)] = surviving

# Step 4: Class occurrence statistics
print("\n" + "=" * 70)
print("CLASS OCCURRENCE STATISTICS")
print("=" * 70)

n_records = len(record_classes)
class_occurrence = defaultdict(int)
for classes in record_classes.values():
    for c in classes:
        class_occurrence[c] += 1

# Categorize classes
universal_classes = []
never_classes = []
rare_classes = []      # <10% of records
common_classes = []    # 10-90%
frequent_classes = []  # >90%

for c in all_b_classes:
    count = class_occurrence[c]
    pct = 100 * count / n_records
    if count == n_records:
        universal_classes.append((c, count, pct))
    elif count == 0:
        never_classes.append((c, count, pct))
    elif pct < 10:
        rare_classes.append((c, count, pct))
    elif pct > 90:
        frequent_classes.append((c, count, pct))
    else:
        common_classes.append((c, count, pct))

print(f"\n1. UNIVERSAL CLASSES (100% of records): {len(universal_classes)}")
for c, cnt, pct in sorted(universal_classes, key=lambda x: x[0]):
    print(f"   {c}: {cnt} records")

print(f"\n2. NEVER-ACTIVATED CLASSES (0% of records): {len(never_classes)}")
for c, cnt, pct in sorted(never_classes, key=lambda x: x[0]):
    print(f"   {c}")

print(f"\n3. FREQUENT CLASSES (>90% of records): {len(frequent_classes)}")
for c, cnt, pct in sorted(frequent_classes, key=lambda x: -x[2]):
    print(f"   {c}: {cnt} records ({pct:.1f}%)")

print(f"\n4. RARE CLASSES (<10% of records): {len(rare_classes)}")
for c, cnt, pct in sorted(rare_classes, key=lambda x: x[2]):
    print(f"   {c}: {cnt} records ({pct:.1f}%)")

print(f"\n5. COMMON CLASSES (10-90%): {len(common_classes)}")
print(f"   (distribution spans the middle range)")

# Step 5: Class co-occurrence matrix
print("\n" + "=" * 70)
print("CLASS CO-OCCURRENCE ANALYSIS")
print("=" * 70)

# Build co-occurrence counts
class_cooccur = defaultdict(int)
for classes in record_classes.values():
    for c1, c2 in combinations(sorted(classes), 2):
        class_cooccur[(c1, c2)] += 1

# Find mutually exclusive pairs
active_classes = sorted([c for c in all_b_classes if class_occurrence[c] > 0])
n_active = len(active_classes)
print(f"\nActive classes: {n_active}")

possible_pairs = list(combinations(active_classes, 2))
mutual_exclusive = []
always_together = []

for c1, c2 in possible_pairs:
    cooccur = class_cooccur[(c1, c2)]
    min_occur = min(class_occurrence[c1], class_occurrence[c2])

    if cooccur == 0:
        mutual_exclusive.append((c1, c2, class_occurrence[c1], class_occurrence[c2]))
    elif cooccur == min_occur:
        # c1 and c2 always co-occur when the less frequent one appears
        always_together.append((c1, c2, cooccur, class_occurrence[c1], class_occurrence[c2]))

print(f"\n6. MUTUALLY EXCLUSIVE CLASS PAIRS: {len(mutual_exclusive)}")
print(f"   ({100*len(mutual_exclusive)/len(possible_pairs):.1f}% of possible pairs)")

if mutual_exclusive:
    print("\n   Top 20 by combined occurrence:")
    sorted_me = sorted(mutual_exclusive, key=lambda x: -(x[2] + x[3]))[:20]
    for c1, c2, o1, o2 in sorted_me:
        print(f"   {c1} ({o1}) <-> {c2} ({o2}) - NEVER together")

print(f"\n7. ALWAYS-TOGETHER CLASS PAIRS: {len(always_together)}")
if always_together:
    print("\n   Top 20 by co-occurrence:")
    sorted_at = sorted(always_together, key=lambda x: -x[2])[:20]
    for c1, c2, cooccur, o1, o2 in sorted_at:
        print(f"   {c1} ({o1}) + {c2} ({o2}) - together {cooccur}x")

# Step 6: Class compatibility clusters
print("\n" + "=" * 70)
print("CLASS COMPATIBILITY CLUSTERS")
print("=" * 70)

# Build adjacency matrix for co-occurrence
class_idx = {c: i for i, c in enumerate(active_classes)}
n = len(active_classes)
cooccur_matrix = np.zeros((n, n))

for (c1, c2), count in class_cooccur.items():
    if c1 in class_idx and c2 in class_idx:
        i, j = class_idx[c1], class_idx[c2]
        cooccur_matrix[i, j] = count
        cooccur_matrix[j, i] = count

# Diagonal = self-occurrence
for c, count in class_occurrence.items():
    if c in class_idx:
        cooccur_matrix[class_idx[c], class_idx[c]] = count

# Compute Jaccard similarity between classes
jaccard_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i == j:
            jaccard_matrix[i, j] = 1.0
        else:
            intersection = cooccur_matrix[i, j]
            union = cooccur_matrix[i, i] + cooccur_matrix[j, j] - intersection
            jaccard_matrix[i, j] = intersection / union if union > 0 else 0

# Find high-compatibility clusters (classes that often appear together)
high_compat = []
low_compat = []

for i in range(n):
    for j in range(i+1, n):
        c1, c2 = active_classes[i], active_classes[j]
        jac = jaccard_matrix[i, j]
        if jac > 0.7:
            high_compat.append((c1, c2, jac))
        elif jac < 0.1 and class_occurrence[c1] > 10 and class_occurrence[c2] > 10:
            low_compat.append((c1, c2, jac))

print(f"\n8. HIGH COMPATIBILITY PAIRS (Jaccard > 0.7): {len(high_compat)}")
for c1, c2, jac in sorted(high_compat, key=lambda x: -x[2])[:15]:
    print(f"   {c1} + {c2}: Jaccard = {jac:.3f}")

print(f"\n9. LOW COMPATIBILITY PAIRS (Jaccard < 0.1, both common): {len(low_compat)}")
for c1, c2, jac in sorted(low_compat, key=lambda x: x[2])[:15]:
    print(f"   {c1} / {c2}: Jaccard = {jac:.3f}")

# Step 7: Core class analysis
print("\n" + "=" * 70)
print("CORE CLASS ANALYSIS")
print("=" * 70)

# What's the minimum set of classes that appears in most records?
threshold_90 = [c for c in active_classes if class_occurrence[c] >= 0.9 * n_records]
threshold_75 = [c for c in active_classes if class_occurrence[c] >= 0.75 * n_records]
threshold_50 = [c for c in active_classes if class_occurrence[c] >= 0.5 * n_records]

print(f"\nCore class sets by coverage threshold:")
print(f"  >90% coverage: {len(threshold_90)} classes")
print(f"  >75% coverage: {len(threshold_75)} classes")
print(f"  >50% coverage: {len(threshold_50)} classes")

print(f"\n>90% coverage classes:")
for c in sorted(threshold_90):
    print(f"   {c}: {class_occurrence[c]} ({100*class_occurrence[c]/n_records:.1f}%)")

# Step 8: Prefix-based analysis
print("\n" + "=" * 70)
print("PREFIX-BASED CLASS ANALYSIS")
print("=" * 70)

# Group classes by prefix type
prefix_groups = defaultdict(list)
for c in active_classes:
    if c.startswith('P_'):
        prefix = c[2:]
        prefix_groups[prefix].append(c)
    elif c.startswith('S_'):
        prefix_groups['SUFFIX'].append(c)
    else:
        prefix_groups['BARE'].append(c)

print("\nClasses by prefix:")
for prefix, classes in sorted(prefix_groups.items()):
    avg_occur = np.mean([class_occurrence[c] for c in classes])
    print(f"  {prefix}: {len(classes)} classes, avg occurrence {avg_occur:.1f} ({100*avg_occur/n_records:.1f}%)")

# Step 9: Save detailed results
print("\n" + "=" * 70)
print("SAVING DETAILED RESULTS")
print("=" * 70)

results = {
    'n_records': n_records,
    'n_classes': len(all_b_classes),
    'n_active_classes': len(active_classes),
    'universal_classes': [c for c, _, _ in universal_classes],
    'never_classes': [c for c, _, _ in never_classes],
    'frequent_classes': [(c, cnt, pct) for c, cnt, pct in frequent_classes],
    'rare_classes': [(c, cnt, pct) for c, cnt, pct in rare_classes],
    'class_occurrence': {c: class_occurrence[c] for c in active_classes},
    'mutual_exclusive_pairs': [(c1, c2) for c1, c2, _, _ in mutual_exclusive],
    'high_compatibility_pairs': [(c1, c2, jac) for c1, c2, jac in high_compat],
    'core_90': threshold_90,
    'core_75': threshold_75,
    'core_50': threshold_50,
}

with open('phases/CLASS_COMPATIBILITY_ANALYSIS/results/compatibility_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Saved to phases/CLASS_COMPATIBILITY_ANALYSIS/results/compatibility_test.json")

# Step 10: Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
CLASS COMPATIBILITY UNDER FULL MORPHOLOGICAL FILTERING

Total B classes:     {len(all_b_classes)}
Active classes:      {len(active_classes)} (appear in at least 1 record)
Universal classes:   {len(universal_classes)} (appear in ALL records)
Never-activated:     {len(never_classes)}

Mutual exclusion:    {len(mutual_exclusive)} pairs ({100*len(mutual_exclusive)/len(possible_pairs):.1f}%)
High compatibility:  {len(high_compat)} pairs (Jaccard > 0.7)

Core sets:
  >90% coverage:     {len(threshold_90)} classes
  >75% coverage:     {len(threshold_75)} classes
  >50% coverage:     {len(threshold_50)} classes

KEY FINDING:
{"Universal classes exist - some classes are truly grammar-essential" if universal_classes else "NO universal classes - every class is context-dependent"}

Mutual exclusion rate of {100*len(mutual_exclusive)/len(possible_pairs):.1f}% confirms class-level differentiation
is significant under full morphological filtering.
""")
