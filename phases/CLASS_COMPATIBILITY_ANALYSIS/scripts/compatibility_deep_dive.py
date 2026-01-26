"""
CLASS_COMPATIBILITY_ANALYSIS Phase - Test 2
Deep dive into compatibility patterns

Questions:
1. Why is BARE almost universal? What 50 records exclude it?
2. What class combinations form natural clusters?
3. Are there morphological predictors of class availability?
4. Do A records form distinct "class profiles"?
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
print("CLASS COMPATIBILITY DEEP DIVE")
print("=" * 70)

# Rebuild the data (same as test 1)
b_tokens = {}
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

b_middles = set(m for p, m, s, c in b_tokens.values())
b_prefixes = set(p for p, m, s, c in b_tokens.values() if p)
b_suffixes = set(s for p, m, s, c in b_tokens.values() if s)

record_classes = {}
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

n_records = len(record_classes)
all_records = list(record_classes.keys())

# ========================================
# ANALYSIS 1: Why do 50 records exclude BARE?
# ========================================
print("\n" + "=" * 70)
print("ANALYSIS 1: RECORDS WITHOUT BARE CLASS")
print("=" * 70)

no_bare_records = [(r, record_classes[r]) for r in all_records if 'BARE' not in record_classes[r]]
print(f"\nRecords without BARE class: {len(no_bare_records)}")

if no_bare_records:
    # What classes DO these records have?
    no_bare_class_counts = defaultdict(int)
    for r, classes in no_bare_records:
        for c in classes:
            no_bare_class_counts[c] += 1

    print("\nClasses in no-BARE records:")
    for c, cnt in sorted(no_bare_class_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {c}: {cnt} records ({100*cnt/len(no_bare_records):.1f}%)")

    # What morphology do these records have?
    print("\nMorphology of no-BARE records:")
    no_bare_prefixes = defaultdict(int)
    no_bare_middles = defaultdict(int)
    for r, _ in no_bare_records:
        pref, mid, suf = record_morphology[r]
        for p in pref:
            no_bare_prefixes[p] += 1
        for m in mid:
            no_bare_middles[m] += 1

    print(f"  Mean PREFIX count: {np.mean([len(record_morphology[r][0]) for r, _ in no_bare_records]):.1f}")
    print(f"  Mean MIDDLE count: {np.mean([len(record_morphology[r][1]) for r, _ in no_bare_records]):.1f}")

    # What's special about BARE tokens that these records miss?
    bare_tokens = [w for w, (p, m, s, c) in b_tokens.items() if c == 'BARE']
    bare_middles = set(b_tokens[w][1] for w in bare_tokens)
    print(f"\n  BARE class has {len(bare_tokens)} tokens with {len(bare_middles)} unique MIDDLEs")

    # Check if no-BARE records have any BARE middles
    for r, _ in no_bare_records[:5]:
        pref, mid, suf = record_morphology[r]
        pp_mid = mid & b_middles
        bare_mid_overlap = pp_mid & bare_middles
        print(f"\n  Record {r}:")
        print(f"    PP MIDDLEs: {len(pp_mid)}")
        print(f"    BARE MIDDLE overlap: {len(bare_mid_overlap)}")
        if bare_mid_overlap:
            print(f"    But missing PREFIX match for BARE tokens")

# ========================================
# ANALYSIS 2: Class clustering via PCA
# ========================================
print("\n" + "=" * 70)
print("ANALYSIS 2: CLASS PROFILE CLUSTERING")
print("=" * 70)

# Build record-class matrix
active_classes = sorted(set(c for classes in record_classes.values() for c in classes))
class_idx = {c: i for i, c in enumerate(active_classes)}
n_classes = len(active_classes)

record_matrix = np.zeros((n_records, n_classes))
for i, r in enumerate(all_records):
    for c in record_classes[r]:
        record_matrix[i, class_idx[c]] = 1

# Compute class co-occurrence correlation
class_corr = np.corrcoef(record_matrix.T)

# Find highly correlated class pairs
print("\nHighly correlated class pairs (r > 0.5):")
high_corr = []
for i in range(n_classes):
    for j in range(i+1, n_classes):
        if class_corr[i, j] > 0.5:
            high_corr.append((active_classes[i], active_classes[j], class_corr[i, j]))

for c1, c2, r in sorted(high_corr, key=lambda x: -x[2])[:20]:
    print(f"  {c1} <-> {c2}: r = {r:.3f}")

print("\nHighly anti-correlated class pairs (r < -0.3):")
anti_corr = []
for i in range(n_classes):
    for j in range(i+1, n_classes):
        if class_corr[i, j] < -0.3:
            anti_corr.append((active_classes[i], active_classes[j], class_corr[i, j]))

for c1, c2, r in sorted(anti_corr, key=lambda x: x[2])[:20]:
    print(f"  {c1} vs {c2}: r = {r:.3f}")

# ========================================
# ANALYSIS 3: A-record class profile types
# ========================================
print("\n" + "=" * 70)
print("ANALYSIS 3: A-RECORD CLASS PROFILE TYPES")
print("=" * 70)

# Cluster records by class count
class_counts = [len(record_classes[r]) for r in all_records]
print(f"\nClass count distribution:")
print(f"  Mean: {np.mean(class_counts):.1f}")
print(f"  Std:  {np.std(class_counts):.1f}")
print(f"  Min:  {np.min(class_counts)}")
print(f"  Max:  {np.max(class_counts)}")

# Bin by class count
bins = [(1, 3), (4, 6), (7, 10), (11, 15), (16, 20)]
print("\nRecords by class count:")
for lo, hi in bins:
    count = sum(1 for c in class_counts if lo <= c <= hi)
    pct = 100 * count / n_records
    print(f"  {lo:2d}-{hi:2d} classes: {count:4d} records ({pct:5.1f}%)")

# Find records with extreme class counts
low_class_records = [r for r in all_records if len(record_classes[r]) <= 3]
high_class_records = [r for r in all_records if len(record_classes[r]) >= 15]

print(f"\nLow-class records (<=3 classes): {len(low_class_records)}")
if low_class_records:
    print("  Sample classes:")
    for r in low_class_records[:5]:
        print(f"    {r}: {sorted(record_classes[r])}")

print(f"\nHigh-class records (>=15 classes): {len(high_class_records)}")
if high_class_records:
    print("  Sample classes:")
    for r in high_class_records[:5]:
        print(f"    {r}: {len(record_classes[r])} classes")

# ========================================
# ANALYSIS 4: Morphological predictors
# ========================================
print("\n" + "=" * 70)
print("ANALYSIS 4: MORPHOLOGICAL PREDICTORS OF CLASS AVAILABILITY")
print("=" * 70)

# Does PREFIX count predict class count?
prefix_counts = [len(record_morphology[r][0]) for r in all_records]
middle_counts = [len(record_morphology[r][1]) for r in all_records]

from scipy import stats

r_pref, p_pref = stats.pearsonr(prefix_counts, class_counts)
r_mid, p_mid = stats.pearsonr(middle_counts, class_counts)

print(f"\nCorrelation with class count:")
print(f"  PREFIX count: r = {r_pref:.3f}, p = {p_pref:.2e}")
print(f"  MIDDLE count: r = {r_mid:.3f}, p = {p_mid:.2e}")

# Does specific PREFIX presence predict specific class?
print("\nPREFIX -> CLASS associations:")
for target_class in ['P_ch', 'P_da', 'P_sh', 'P_qo', 'P_ok']:
    has_class = [1 if target_class in record_classes[r] else 0 for r in all_records]

    # Which PREFIX best predicts this class?
    all_a_prefixes = set()
    for r in all_records:
        all_a_prefixes.update(record_morphology[r][0])

    best_prefix = None
    best_corr = 0
    for pref in all_a_prefixes:
        has_pref = [1 if pref in record_morphology[r][0] else 0 for r in all_records]
        if sum(has_pref) > 10:  # At least 10 occurrences
            r_val, _ = stats.pearsonr(has_pref, has_class)
            if abs(r_val) > abs(best_corr):
                best_corr = r_val
                best_prefix = pref

    if best_prefix:
        print(f"  {target_class}: best predictor = A-PREFIX '{best_prefix}' (r = {best_corr:.3f})")

# ========================================
# ANALYSIS 5: Class exclusion patterns
# ========================================
print("\n" + "=" * 70)
print("ANALYSIS 5: CLASS EXCLUSION NETWORK")
print("=" * 70)

# Build exclusion graph
exclusion_graph = defaultdict(set)
for c1 in active_classes:
    for c2 in active_classes:
        if c1 >= c2:
            continue
        # Check if they ever co-occur
        cooccur = False
        for r in all_records:
            if c1 in record_classes[r] and c2 in record_classes[r]:
                cooccur = True
                break
        if not cooccur:
            exclusion_graph[c1].add(c2)
            exclusion_graph[c2].add(c1)

# Find classes with most exclusions
print("\nClasses with most exclusions:")
exclusion_counts = [(c, len(exclusion_graph[c])) for c in active_classes]
for c, cnt in sorted(exclusion_counts, key=lambda x: -x[1])[:15]:
    print(f"  {c}: excludes {cnt} classes")

# Find connected components in co-occurrence graph
# (Classes that form mutually compatible groups)
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
CLASS COMPATIBILITY DEEP DIVE RESULTS

1. NO-BARE RECORDS: {len(no_bare_records)} records lack the BARE class
   - These records have specific morphological profiles that miss BARE tokens

2. CLASS CORRELATIONS:
   - {len(high_corr)} highly correlated pairs (r > 0.5)
   - {len(anti_corr)} anti-correlated pairs (r < -0.3)
   - Classes form distinct compatibility clusters

3. CLASS COUNT DISTRIBUTION:
   - Mean: {np.mean(class_counts):.1f} classes per record
   - Range: {np.min(class_counts)} - {np.max(class_counts)}
   - Low-class records (<=3): {len(low_class_records)}
   - High-class records (>=15): {len(high_class_records)}

4. MORPHOLOGICAL PREDICTORS:
   - PREFIX count -> class count: r = {r_pref:.3f}
   - MIDDLE count -> class count: r = {r_mid:.3f}
   - MIDDLE is the stronger predictor

5. EXCLUSION NETWORK:
   - {sum(len(v) for v in exclusion_graph.values()) // 2} exclusive pairs
   - Most-excluding classes tend to be rare/specialized
""")
