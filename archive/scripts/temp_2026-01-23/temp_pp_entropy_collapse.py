#!/usr/bin/env python3
"""
PP Entropy Collapse Location Test

Question: Does PP collapse entropy primarily at the AZC stage or at the B stage?

- If AZC: PP = decision legality shapers
- If B: PP = execution survivability carriers
- If split: PP = interface vocabulary

Method:
1. For each A-record, compute PP composition
2. Compute AZC folio compatibility for that PP (which AZC folios share those PP MIDDLEs)
3. Compute B class survival for that PP (already in survivors data)
4. Measure entropy reduction at each stage
"""

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from math import log2

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load A record survivors (has PP composition and B class survival)
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

records = survivors_data['records']

# Load class token map for MIDDLE extraction
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

class_to_middles = class_map['class_to_middles']
token_to_middle = class_map['token_to_middle']

# Collect all B MIDDLEs (from classes)
b_middles_from_classes = set()
for cls, middles in class_to_middles.items():
    b_middles_from_classes.update(middles)

# Get all A MIDDLEs
all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

# PP = shared between A and B
pp_middles = all_a_middles & b_middles_from_classes
ri_middles = all_a_middles - b_middles_from_classes

print("="*70)
print("PP ENTROPY COLLAPSE LOCATION TEST")
print("="*70)
print(f"\nPP MIDDLEs: {len(pp_middles)}")
print(f"RI MIDDLEs: {len(ri_middles)}")
print(f"Total A records: {len(records)}")

# ============================================================
# STEP 1: Build AZC folio -> MIDDLE mapping
# ============================================================
print("\n" + "="*70)
print("STEP 1: BUILD AZC FOLIO MIDDLE PROFILES")
print("="*70)

# Filter to AZC tokens (language == NA in the transcript)
df_azc = df[df['language'].isna()].copy()

# Extract MIDDLEs for AZC tokens
df_azc['middle'] = df_azc['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

# Build AZC folio -> set of MIDDLEs
azc_folio_middles = defaultdict(set)
for _, row in df_azc.iterrows():
    if pd.notna(row['middle']):
        azc_folio_middles[row['folio']].add(row['middle'])

azc_folios = list(azc_folio_middles.keys())
print(f"AZC folios: {len(azc_folios)}")

# Which MIDDLEs are PP and appear in AZC?
azc_pp_middles = set()
for folio, middles in azc_folio_middles.items():
    azc_pp_middles.update(middles & pp_middles)

print(f"PP MIDDLEs that appear in AZC: {len(azc_pp_middles)}")

# ============================================================
# STEP 2: Build B folio -> MIDDLE mapping
# ============================================================
print("\n" + "="*70)
print("STEP 2: BUILD B FOLIO MIDDLE PROFILES")
print("="*70)

df_b = df[df['language'] == 'B'].copy()
df_b['middle'] = df_b['word'].apply(lambda x: token_to_middle.get(x) if pd.notna(x) else None)

b_folio_middles = defaultdict(set)
for _, row in df_b.iterrows():
    if pd.notna(row['middle']):
        b_folio_middles[row['folio']].add(row['middle'])

b_folios = list(b_folio_middles.keys())
print(f"B folios: {len(b_folios)}")

# ============================================================
# STEP 3: Compute entropy metrics
# ============================================================
print("\n" + "="*70)
print("STEP 3: COMPUTE ENTROPY METRICS")
print("="*70)

def entropy(counts):
    """Shannon entropy from count dict or list."""
    if isinstance(counts, dict):
        counts = list(counts.values())
    total = sum(counts)
    if total == 0:
        return 0
    probs = [c/total for c in counts if c > 0]
    return -sum(p * log2(p) for p in probs)

# Baseline entropies (unconditional)
# H(AZC) = entropy over AZC folios (assuming uniform prior)
h_azc_baseline = log2(len(azc_folios)) if azc_folios else 0
print(f"\nBaseline H(AZC folios) = {h_azc_baseline:.3f} bits (uniform over {len(azc_folios)} folios)")

# H(B classes) = entropy over 49 classes (uniform prior)
h_b_class_baseline = log2(49)
print(f"Baseline H(B classes) = {h_b_class_baseline:.3f} bits (uniform over 49 classes)")

# H(B folios) = entropy over B folios (uniform prior)
h_b_folio_baseline = log2(len(b_folios)) if b_folios else 0
print(f"Baseline H(B folios) = {h_b_folio_baseline:.3f} bits (uniform over {len(b_folios)} folios)")

# ============================================================
# STEP 4: For each A record, compute conditional entropies
# ============================================================
print("\n" + "="*70)
print("STEP 4: COMPUTE CONDITIONAL ENTROPIES PER A RECORD")
print("="*70)

azc_entropies = []
b_class_entropies = []
b_folio_entropies = []
pp_counts = []

for rec in records:
    a_middles = set(rec['a_middles'])
    pp_in_record = a_middles & pp_middles
    pp_counts.append(len(pp_in_record))

    # --- AZC Stage Entropy ---
    # Which AZC folios are compatible with this PP composition?
    # Compatible = AZC folio contains ALL the PP MIDDLEs in the A record
    # (strict interpretation: A record MIDDLEs must be legal in AZC)

    # Actually, let's use a softer measure: Jaccard overlap
    # Count how many PP MIDDLEs from the A record appear in each AZC folio
    azc_overlap_counts = {}
    for azc_folio in azc_folios:
        overlap = len(pp_in_record & azc_folio_middles[azc_folio])
        azc_overlap_counts[azc_folio] = overlap

    # Weight AZC folios by overlap (more overlap = more compatible)
    # Entropy of this weighted distribution
    if sum(azc_overlap_counts.values()) > 0:
        h_azc = entropy(azc_overlap_counts)
    else:
        h_azc = h_azc_baseline
    azc_entropies.append(h_azc)

    # --- B Class Entropy ---
    # Use surviving classes from the survivors data
    surviving_classes = rec['surviving_classes']
    n_surviving = len(surviving_classes)
    # Entropy assuming uniform distribution over surviving classes
    h_b_class = log2(n_surviving) if n_surviving > 1 else 0
    b_class_entropies.append(h_b_class)

    # --- B Folio Entropy ---
    # Which B folios are compatible with this PP composition?
    b_overlap_counts = {}
    for b_folio in b_folios:
        overlap = len(pp_in_record & b_folio_middles[b_folio])
        b_overlap_counts[b_folio] = overlap

    if sum(b_overlap_counts.values()) > 0:
        h_b_folio = entropy(b_overlap_counts)
    else:
        h_b_folio = h_b_folio_baseline
    b_folio_entropies.append(h_b_folio)

# Convert to arrays
azc_entropies = np.array(azc_entropies)
b_class_entropies = np.array(b_class_entropies)
b_folio_entropies = np.array(b_folio_entropies)
pp_counts = np.array(pp_counts)

# ============================================================
# STEP 5: Compute entropy reduction metrics
# ============================================================
print("\n" + "="*70)
print("STEP 5: ENTROPY REDUCTION ANALYSIS")
print("="*70)

# Mean conditional entropies
mean_h_azc = np.mean(azc_entropies)
mean_h_b_class = np.mean(b_class_entropies)
mean_h_b_folio = np.mean(b_folio_entropies)

print(f"\nMean conditional entropies:")
print(f"  H(AZC | PP composition) = {mean_h_azc:.3f} bits")
print(f"  H(B classes | PP composition) = {mean_h_b_class:.3f} bits")
print(f"  H(B folios | PP composition) = {mean_h_b_folio:.3f} bits")

# Entropy reduction (information gained from PP)
azc_reduction = h_azc_baseline - mean_h_azc
b_class_reduction = h_b_class_baseline - mean_h_b_class
b_folio_reduction = h_b_folio_baseline - mean_h_b_folio

print(f"\nEntropy reduction (bits gained from PP conditioning):")
print(f"  AZC stage reduction: {azc_reduction:.3f} bits ({100*azc_reduction/h_azc_baseline:.1f}% of baseline)")
print(f"  B class reduction: {b_class_reduction:.3f} bits ({100*b_class_reduction/h_b_class_baseline:.1f}% of baseline)")
print(f"  B folio reduction: {b_folio_reduction:.3f} bits ({100*b_folio_reduction/h_b_folio_baseline:.1f}% of baseline)")

# ============================================================
# STEP 6: Correlation with PP count
# ============================================================
print("\n" + "="*70)
print("STEP 6: CORRELATION WITH PP COUNT")
print("="*70)

# Does more PP lead to more entropy reduction?
corr_azc = np.corrcoef(pp_counts, azc_entropies)[0,1]
corr_b_class = np.corrcoef(pp_counts, b_class_entropies)[0,1]
corr_b_folio = np.corrcoef(pp_counts, b_folio_entropies)[0,1]

print(f"\nCorrelation of PP count with conditional entropy:")
print(f"  PP count vs H(AZC): r = {corr_azc:.3f}")
print(f"  PP count vs H(B classes): r = {corr_b_class:.3f}")
print(f"  PP count vs H(B folios): r = {corr_b_folio:.3f}")

print("""
Interpretation:
  - Negative correlation = more PP reduces entropy (concentrates options)
  - Strong negative at AZC = PP shapes decision legality
  - Strong negative at B = PP shapes execution survivability
""")

# ============================================================
# STEP 7: Stratified analysis by PP count
# ============================================================
print("\n" + "="*70)
print("STEP 7: STRATIFIED ANALYSIS BY PP COUNT")
print("="*70)

# Group records by PP count
pp_bins = [(0, 2), (3, 5), (6, 10), (11, 20)]
for low, high in pp_bins:
    mask = (pp_counts >= low) & (pp_counts <= high)
    n = np.sum(mask)
    if n > 0:
        mean_azc = np.mean(azc_entropies[mask])
        mean_b_class = np.mean(b_class_entropies[mask])
        mean_b_folio = np.mean(b_folio_entropies[mask])
        print(f"\nPP count {low}-{high} (n={n}):")
        print(f"  Mean H(AZC): {mean_azc:.3f} bits")
        print(f"  Mean H(B classes): {mean_b_class:.3f} bits")
        print(f"  Mean H(B folios): {mean_b_folio:.3f} bits")

# ============================================================
# STEP 8: Key test - Where does PP do more work?
# ============================================================
print("\n" + "="*70)
print("STEP 8: KEY RESULT - WHERE DOES PP COLLAPSE ENTROPY?")
print("="*70)

# Normalize reductions to percentage of baseline
azc_pct = 100 * azc_reduction / h_azc_baseline if h_azc_baseline > 0 else 0
b_class_pct = 100 * b_class_reduction / h_b_class_baseline if h_b_class_baseline > 0 else 0
b_folio_pct = 100 * b_folio_reduction / h_b_folio_baseline if h_b_folio_baseline > 0 else 0

print(f"\nEntropy reduction as % of baseline:")
print(f"  AZC stage: {azc_pct:.1f}%")
print(f"  B class stage: {b_class_pct:.1f}%")
print(f"  B folio stage: {b_folio_pct:.1f}%")

# Determine dominant stage
if azc_pct > b_class_pct * 1.5:
    verdict = "AZC-DOMINANT"
    interpretation = "PP primarily shapes DECISION LEGALITY (which AZC contexts are valid)"
elif b_class_pct > azc_pct * 1.5:
    verdict = "B-DOMINANT"
    interpretation = "PP primarily shapes EXECUTION SURVIVABILITY (which B classes survive)"
else:
    verdict = "SPLIT / INTERFACE"
    interpretation = "PP functions as INTERFACE VOCABULARY bridging both stages"

print(f"\n{'='*70}")
print(f"VERDICT: {verdict}")
print(f"{'='*70}")
print(f"\n{interpretation}")

# Absolute comparison
print(f"\nAbsolute entropy reduction:")
print(f"  AZC: {azc_reduction:.3f} bits")
print(f"  B classes: {b_class_reduction:.3f} bits")
print(f"  B folios: {b_folio_reduction:.3f} bits")

# Ratio
if b_class_reduction > 0:
    ratio = azc_reduction / b_class_reduction
    print(f"\nAZC/B-class reduction ratio: {ratio:.2f}")

    if ratio > 2:
        print("  -> PP does most of its work at the AZC stage")
    elif ratio < 0.5:
        print("  -> PP does most of its work at the B stage")
    else:
        print("  -> PP work is distributed across both stages")

# ============================================================
# STEP 9: Summary statistics
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
PP Entropy Collapse Location Test Results:

BASELINES:
  H(AZC folios): {h_azc_baseline:.3f} bits ({len(azc_folios)} folios)
  H(B classes): {h_b_class_baseline:.3f} bits (49 classes)
  H(B folios): {h_b_folio_baseline:.3f} bits ({len(b_folios)} folios)

MEAN CONDITIONAL ENTROPIES (given PP composition):
  H(AZC | PP): {mean_h_azc:.3f} bits
  H(B classes | PP): {mean_h_b_class:.3f} bits
  H(B folios | PP): {mean_h_b_folio:.3f} bits

ENTROPY REDUCTION:
  AZC stage: {azc_reduction:.3f} bits ({azc_pct:.1f}% reduction)
  B class stage: {b_class_reduction:.3f} bits ({b_class_pct:.1f}% reduction)
  B folio stage: {b_folio_reduction:.3f} bits ({b_folio_pct:.1f}% reduction)

CORRELATIONS (PP count vs conditional entropy):
  AZC: r = {corr_azc:.3f}
  B classes: r = {corr_b_class:.3f}
  B folios: r = {corr_b_folio:.3f}

VERDICT: {verdict}
{interpretation}
""")
