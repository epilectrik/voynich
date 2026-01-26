"""
GALLOWS_B_COMPATIBILITY Phase - Test 2
Question: Are most A records so PP-limited that B programs are effectively crippled?

We know:
- C504: PP count correlates with B class survival (r=0.715)
- C506 gradient: PP 0-2 -> 19 classes, PP 12-15 -> 44 classes

This tests whether the A->B pipeline at RECORD level creates severe restrictions.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology, RecordAnalyzer
from collections import defaultdict
import numpy as np
from scipy import stats

# Load data
tx = Transcript()
morph = Morphology()

print("=" * 70)
print("RECORD-LEVEL PP ANALYSIS")
print("=" * 70)

# Step 1: Get all B MIDDLEs (this defines PP vocabulary)
print("\nStep 1: Building B vocabulary (defines PP)...")
b_middles = set()
b_folio_middles = defaultdict(set)

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle:
        b_middles.add(m.middle)
        b_folio_middles[token.folio].add(m.middle)

print(f"  B vocabulary: {len(b_middles)} unique MIDDLEs")
print(f"  B folios: {len(b_folio_middles)}")

# Step 2: Analyze A records
print("\nStep 2: Analyzing A records...")

# Group A tokens by record (folio + line)
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

print(f"  A records: {len(a_records)}")

# For each record, compute PP count (MIDDLEs shared with B)
record_pp_counts = []
record_pp_sets = {}

for (folio, line), tokens in a_records.items():
    middles = set()
    for token in tokens:
        m = morph.extract(token.word)
        if m.middle:
            middles.add(m.middle)

    pp_middles = middles & b_middles
    record_pp_counts.append(len(pp_middles))
    record_pp_sets[(folio, line)] = pp_middles

print(f"  Records analyzed: {len(record_pp_counts)}")

# Step 3: PP count distribution at record level
print("\n" + "=" * 70)
print("PP COUNT DISTRIBUTION (per A record)")
print("=" * 70)

pp_arr = np.array(record_pp_counts)
print(f"\n  Mean PP count: {np.mean(pp_arr):.2f}")
print(f"  Median: {np.median(pp_arr):.1f}")
print(f"  Std: {np.std(pp_arr):.2f}")
print(f"  Min: {np.min(pp_arr)}")
print(f"  Max: {np.max(pp_arr)}")

# Distribution bins (matching C506 gradient)
bins = [(0, 0), (1, 2), (3, 5), (6, 8), (9, 11), (12, 100)]
expected_classes = [0, 19, 31, 37, 41, 44]  # From C506 gradient (0 is my addition for PP=0)

print("\n  PP count bins:")
for i, (lo, hi) in enumerate(bins):
    count = sum(1 for p in pp_arr if lo <= p <= hi)
    pct = 100 * count / len(pp_arr)
    classes = expected_classes[i]
    print(f"    PP {lo}-{hi}: {count:4d} records ({pct:5.1f}%) -> ~{classes} B classes")

# Step 4: "Crippled" threshold analysis
print("\n" + "=" * 70)
print("CRIPPLING ANALYSIS")
print("=" * 70)

# Define thresholds
print("\nRecords by PP threshold:")
thresholds = [0, 1, 2, 3, 5]
for thresh in thresholds:
    count = sum(1 for p in pp_arr if p <= thresh)
    pct = 100 * count / len(pp_arr)
    print(f"  PP <= {thresh}: {count:4d} records ({pct:5.1f}%)")

# Zero-PP records
zero_pp = sum(1 for p in pp_arr if p == 0)
zero_pct = 100 * zero_pp / len(pp_arr)
print(f"\n  ZERO PP (completely isolated): {zero_pp} records ({zero_pct:.1f}%)")

# Step 5: What does a "crippled" record look like?
print("\n" + "=" * 70)
print("SAMPLE LOW-PP RECORDS")
print("=" * 70)

# Find records with PP=0
zero_pp_records = [(k, v) for k, v in a_records.items()
                   if len(record_pp_sets[k]) == 0]

print(f"\nRecords with PP=0 (no B vocabulary): {len(zero_pp_records)}")
if zero_pp_records:
    print("  Sample (first 5):")
    for (folio, line), tokens in zero_pp_records[:5]:
        words = [t.word for t in tokens]
        middles = []
        for t in tokens:
            m = morph.extract(t.word)
            if m.middle:
                middles.append(m.middle)
        print(f"    {folio}.{line}: {words}")
        print(f"      MIDDLEs: {middles} (all RI)")

# Find records with PP=1
one_pp_records = [(k, v) for k, v in a_records.items()
                  if len(record_pp_sets[k]) == 1]

print(f"\nRecords with PP=1: {len(one_pp_records)}")
if one_pp_records:
    print("  Sample (first 5):")
    for (folio, line), tokens in one_pp_records[:5]:
        words = [t.word for t in tokens]
        pp = record_pp_sets[(folio, line)]
        print(f"    {folio}.{line}: {words}")
        print(f"      PP MIDDLEs: {pp}")

# Step 6: B folio accessibility per record
print("\n" + "=" * 70)
print("B FOLIO ACCESSIBILITY PER RECORD")
print("=" * 70)

# For each A record, count how many B folios it can reach
record_b_access = []
for (folio, line), pp_set in record_pp_sets.items():
    if not pp_set:
        record_b_access.append(0)
    else:
        # Count B folios that contain any of these PP MIDDLEs
        accessible = sum(1 for bf, bm in b_folio_middles.items()
                        if pp_set & bm)
        record_b_access.append(accessible)

b_arr = np.array(record_b_access)
print(f"\n  Mean B folios accessible: {np.mean(b_arr):.1f}")
print(f"  Median: {np.median(b_arr):.1f}")
print(f"  Min: {np.min(b_arr)}")
print(f"  Max: {np.max(b_arr)}")

# Distribution
print("\n  B folio accessibility distribution:")
access_bins = [(0, 0), (1, 10), (11, 40), (41, 70), (71, 82)]
for lo, hi in access_bins:
    count = sum(1 for b in b_arr if lo <= b <= hi)
    pct = 100 * count / len(b_arr)
    print(f"    {lo}-{hi} B folios: {count:4d} records ({pct:5.1f}%)")

# Step 7: Gallows domain effect on PP count
print("\n" + "=" * 70)
print("GALLOWS DOMAIN EFFECT ON PP COUNT")
print("=" * 70)

GALLOWS = {'k', 't', 'p', 'f'}

def extract_gallows(middle):
    return set(c for c in middle if c in GALLOWS)

def get_dominant_gallows(middles):
    counts = defaultdict(int)
    for m in middles:
        for g in extract_gallows(m):
            counts[g] += 1
    if not counts:
        return None
    return max(counts.keys(), key=lambda g: counts[g])

# Classify records by gallows domain
record_gallows = {}
for (folio, line), tokens in a_records.items():
    middles = []
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle:
            middles.append(m.middle)
    record_gallows[(folio, line)] = get_dominant_gallows(middles)

# PP count by gallows domain
gallows_pp = defaultdict(list)
for key, pp_set in record_pp_sets.items():
    dom = record_gallows.get(key)
    if dom:
        gallows_pp[dom].append(len(pp_set))

print("\nMean PP count by gallows domain:")
for g in ['k', 't', 'p', 'f']:
    if gallows_pp[g]:
        arr = gallows_pp[g]
        print(f"  {g}-dominant: mean={np.mean(arr):.2f}, n={len(arr)}")

# Step 8: Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

crippled_pct = 100 * sum(1 for p in pp_arr if p <= 2) / len(pp_arr)
isolated_pct = 100 * sum(1 for p in pp_arr if p == 0) / len(pp_arr)
broad_pct = 100 * sum(1 for p in pp_arr if p >= 6) / len(pp_arr)

print(f"""
A RECORD PP DISTRIBUTION:
  - Isolated (PP=0, no B access): {isolated_pct:.1f}%
  - Crippled (PP<=2, ~19 classes): {crippled_pct:.1f}%
  - Broad (PP>=6, ~37+ classes): {broad_pct:.1f}%

INTERPRETATION:
""")

if crippled_pct > 30:
    print(f"""  YES - Many records ({crippled_pct:.1f}%) are severely PP-limited.
  These records can technically "reach" B folios but with so few
  PP MIDDLEs that the resulting execution would be heavily constrained.

  This supports the idea that A records CREATE meaningful B restrictions,
  not through exclusion but through severe vocabulary limitation.
""")
else:
    print(f"""  NO - Most records ({100-crippled_pct:.1f}%) have sufficient PP.
  While some records are PP-limited, the majority have enough
  PP vocabulary to access B programs with reasonable flexibility.
""")
