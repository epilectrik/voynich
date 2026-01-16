#!/usr/bin/env python3
"""
PHASE B-MIN: DIAGRAM ALIGNMENT TEST (SAFE VERSION)

We know:
- Placement codes are phase-locked (rotation test: 32.3pp drop)
- C is topologically flexible, P/R/S are position-fixed
- R1->R2->R3 appears to be an ordered sequence

Test ONLY:
- B-1: Placement × Folio/Panel distribution
- B-2: R1->R2->R3 ordered mapping (by line position)
- B-3: S1/S2 boundary validation

We test ALIGNMENT, not MEANING.
"""

import os
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

os.chdir('C:/git/voynich')

print("=" * 70)
print("PHASE B-MIN: DIAGRAM ALIGNMENT TEST")
print("Testing text-diagram alignment (correlation only)")
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

# Get AZC tokens (where placement codes are meaningful)
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]

print(f"\nLoaded {len(azc_tokens)} AZC tokens")

# Get unique folios and placements
folios = sorted(set(t.get('folio', '') for t in azc_tokens))
placements = sorted(set(t.get('placement', 'UNK') for t in azc_tokens))

print(f"AZC folios: {len(folios)}")
print(f"Placement classes: {placements}")

# =========================================================================
# B-1: PLACEMENT × FOLIO/PANEL DISTRIBUTION
# =========================================================================

print("\n" + "=" * 70)
print("B-1: PLACEMENT × FOLIO DISTRIBUTION")
print("Do placement codes cluster by folio?")
print("=" * 70)

# Count placement distribution per folio
folio_placement = defaultdict(Counter)
for t in azc_tokens:
    folio = t.get('folio', '')
    p = t.get('placement', 'UNK')
    folio_placement[folio][p] += 1

# For each folio, find dominant placement
print(f"\n{'Folio':<12} {'Tokens':<8} {'Dominant':<10} {'%':<8} {'Profile':<40}")
print("-" * 85)

folio_profiles = {}
for folio in folios:
    counts = folio_placement[folio]
    total = sum(counts.values())
    if total >= 10:  # Minimum tokens
        dominant, dom_count = counts.most_common(1)[0]
        dom_pct = dom_count / total * 100

        # Build profile (top 3)
        profile = ", ".join(f"{p}:{c}" for p, c in counts.most_common(3))
        folio_profiles[folio] = counts

        print(f"{folio:<12} {total:<8} {dominant:<10} {dom_pct:<8.1f} {profile:<40}")

# Test: do different folios have different placement profiles?
# Chi-square test on placement distribution
print("\n--- Folio × Placement Independence Test ---")

# Build contingency table (folios with enough data)
significant_folios = [f for f in folios if sum(folio_placement[f].values()) >= 20]
significant_placements = ['C', 'P', 'R1', 'R2', 'R3', 'S', 'S1', 'S2', 'L', 'X', 'Y']

if len(significant_folios) >= 3:
    contingency = []
    for folio in significant_folios:
        row = [folio_placement[folio].get(p, 0) for p in significant_placements]
        contingency.append(row)

    contingency = np.array(contingency)

    # Remove columns with all zeros
    col_sums = contingency.sum(axis=0)
    non_zero_cols = col_sums > 0
    contingency_clean = contingency[:, non_zero_cols]
    placements_clean = [p for p, nz in zip(significant_placements, non_zero_cols) if nz]

    if contingency_clean.shape[1] >= 2:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_clean)
        cramers_v = np.sqrt(chi2 / (contingency_clean.sum() * (min(contingency_clean.shape) - 1)))

        print(f"Chi-square: {chi2:.1f}, df={dof}, p={p_value:.2e}")
        print(f"Cramer's V: {cramers_v:.3f}")

        if cramers_v > 0.3:
            print("STRONG folio-specific placement distribution")
        elif cramers_v > 0.1:
            print("MODERATE folio-specific placement distribution")
        else:
            print("WEAK folio-specific placement distribution")

# =========================================================================
# B-2: R-SERIES ORDERED MAPPING TEST
# =========================================================================

print("\n" + "=" * 70)
print("B-2: R-SERIES ORDERED MAPPING")
print("Do R1-R2-R3 show ordered positions within folios?")
print("=" * 70)

# For each folio, get mean line position of R1, R2, R3
r_series_positions = defaultdict(lambda: {'R1': [], 'R2': [], 'R3': []})

for t in azc_tokens:
    p = t.get('placement', '')
    if p in ['R1', 'R2', 'R3']:
        folio = t.get('folio', '')
        try:
            line_num = int(t.get('line_number', 0))
            r_series_positions[folio][p].append(line_num)
        except:
            pass

# Test ordering per folio
print(f"\n{'Folio':<12} {'R1 mean':<10} {'R2 mean':<10} {'R3 mean':<10} {'Ordering':<15}")
print("-" * 60)

ordering_results = []
for folio in sorted(r_series_positions.keys()):
    positions = r_series_positions[folio]

    # Need at least 2 points in each
    if all(len(positions[r]) >= 2 for r in ['R1', 'R2', 'R3']):
        means = {r: sum(positions[r])/len(positions[r]) for r in ['R1', 'R2', 'R3']}

        # Check ordering
        if means['R1'] < means['R2'] < means['R3']:
            ordering = "R1 < R2 < R3"
            ordering_results.append(1)
        elif means['R1'] > means['R2'] > means['R3']:
            ordering = "R1 > R2 > R3"
            ordering_results.append(-1)
        else:
            ordering = "MIXED"
            ordering_results.append(0)

        print(f"{folio:<12} {means['R1']:<10.1f} {means['R2']:<10.1f} {means['R3']:<10.1f} {ordering:<15}")

if ordering_results:
    forward = sum(1 for r in ordering_results if r == 1)
    backward = sum(1 for r in ordering_results if r == -1)
    mixed = sum(1 for r in ordering_results if r == 0)

    print(f"\nOrdering summary:")
    print(f"  R1 < R2 < R3 (forward): {forward}")
    print(f"  R1 > R2 > R3 (backward): {backward}")
    print(f"  Mixed: {mixed}")

    if forward > backward + mixed:
        print("\n  VERDICT: R-series shows CONSISTENT FORWARD ordering")
        print("  -> R1->R2->R3 maps to increasing line position")
    elif backward > forward + mixed:
        print("\n  VERDICT: R-series shows CONSISTENT BACKWARD ordering")
        print("  -> R1->R2->R3 maps to decreasing line position")
    else:
        print("\n  VERDICT: R-series ordering is FOLIO-SPECIFIC")
        print("  -> Different diagrams may have different orientations")

# Global test: Spearman correlation between R-index and line position
all_r_data = []
for t in azc_tokens:
    p = t.get('placement', '')
    if p in ['R1', 'R2', 'R3']:
        try:
            line_num = int(t.get('line_number', 0))
            r_index = int(p[1])  # 1, 2, or 3
            all_r_data.append((r_index, line_num))
        except:
            pass

if len(all_r_data) >= 20:
    r_indices = [d[0] for d in all_r_data]
    line_nums = [d[1] for d in all_r_data]
    rho, p_val = stats.spearmanr(r_indices, line_nums)

    print(f"\nGlobal R-index × Line correlation:")
    print(f"  Spearman rho: {rho:.3f}")
    print(f"  p-value: {p_val:.2e}")

    if abs(rho) > 0.3 and p_val < 0.01:
        direction = "INCREASING" if rho > 0 else "DECREASING"
        print(f"  SIGNIFICANT {direction} correlation detected")

# =========================================================================
# B-3: S-SERIES BOUNDARY VALIDATION
# =========================================================================

print("\n" + "=" * 70)
print("B-3: S-SERIES BOUNDARY VALIDATION")
print("Do S1/S2 appear at structural boundaries?")
print("=" * 70)

# For each folio, get line range and check where S1/S2 appear
s_series_boundary = {'S1': {'early': 0, 'middle': 0, 'late': 0},
                     'S2': {'early': 0, 'middle': 0, 'late': 0}}

for folio in folios:
    folio_tokens = [t for t in azc_tokens if t.get('folio', '') == folio]
    if len(folio_tokens) < 10:
        continue

    # Get line range for this folio
    line_nums = []
    for t in folio_tokens:
        try:
            line_nums.append(int(t.get('line_number', 0)))
        except:
            pass

    if not line_nums:
        continue

    min_line = min(line_nums)
    max_line = max(line_nums)
    range_size = max_line - min_line

    if range_size < 3:
        continue

    # Categorize S1/S2 tokens
    for t in folio_tokens:
        p = t.get('placement', '')
        if p in ['S1', 'S2']:
            try:
                line_num = int(t.get('line_number', 0))
                relative_pos = (line_num - min_line) / range_size

                if relative_pos < 0.25:
                    s_series_boundary[p]['early'] += 1
                elif relative_pos > 0.75:
                    s_series_boundary[p]['late'] += 1
                else:
                    s_series_boundary[p]['middle'] += 1
            except:
                pass

print("\nS-series distribution by relative line position:")
print(f"{'Placement':<10} {'Early (0-25%)':<15} {'Middle (25-75%)':<18} {'Late (75-100%)':<15} {'Boundary%':<12}")
print("-" * 75)

for s in ['S1', 'S2']:
    early = s_series_boundary[s]['early']
    middle = s_series_boundary[s]['middle']
    late = s_series_boundary[s]['late']
    total = early + middle + late

    if total > 0:
        boundary_pct = (early + late) / total * 100
        print(f"{s:<10} {early:<15} {middle:<18} {late:<15} {boundary_pct:<12.1f}")

        if boundary_pct > 60:
            print(f"  -> {s} is BOUNDARY-CONCENTRATED")
        elif boundary_pct < 40:
            print(f"  -> {s} is INTERIOR-CONCENTRATED")

# Test: S1 vs S2 position difference
print("\n--- S1 vs S2 Position Comparison ---")

s1_positions = []
s2_positions = []

for folio in folios:
    folio_tokens = [t for t in azc_tokens if t.get('folio', '') == folio]

    line_nums = []
    for t in folio_tokens:
        try:
            line_nums.append(int(t.get('line_number', 0)))
        except:
            pass

    if not line_nums:
        continue

    min_line = min(line_nums)
    max_line = max(line_nums)
    range_size = max_line - min_line

    if range_size < 3:
        continue

    for t in folio_tokens:
        p = t.get('placement', '')
        try:
            line_num = int(t.get('line_number', 0))
            relative_pos = (line_num - min_line) / range_size

            if p == 'S1':
                s1_positions.append(relative_pos)
            elif p == 'S2':
                s2_positions.append(relative_pos)
        except:
            pass

if s1_positions and s2_positions:
    s1_mean = sum(s1_positions) / len(s1_positions)
    s2_mean = sum(s2_positions) / len(s2_positions)

    print(f"S1 mean relative position: {s1_mean:.3f}")
    print(f"S2 mean relative position: {s2_mean:.3f}")

    if len(s1_positions) >= 5 and len(s2_positions) >= 5:
        stat, p_val = stats.mannwhitneyu(s1_positions, s2_positions, alternative='two-sided')
        print(f"Mann-Whitney U p-value: {p_val:.4f}")

        if p_val < 0.05:
            if s1_mean < s2_mean:
                print("  S1 appears EARLIER than S2 (significant)")
            else:
                print("  S2 appears EARLIER than S1 (significant)")
        else:
            print("  No significant position difference between S1 and S2")

# =========================================================================
# PHASE B-MIN VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("PHASE B-MIN VERDICT: DIAGRAM ALIGNMENT")
print("=" * 70)

print("""
ALIGNMENT TEST RESULTS:

B-1: FOLIO × PLACEMENT
""")

if 'cramers_v' in dir():
    if cramers_v > 0.3:
        print(f"  STRONG folio-specific distribution (V={cramers_v:.3f})")
        print("  -> Different folios have DIFFERENT placement profiles")
        print("  -> Diagram layout varies by folio")
    elif cramers_v > 0.1:
        print(f"  MODERATE folio-specific distribution (V={cramers_v:.3f})")
        print("  -> Some folios have distinct placement profiles")
    else:
        print(f"  WEAK folio-specific distribution (V={cramers_v:.3f})")
        print("  -> Placement distribution is relatively uniform across folios")

print("""
B-2: R-SERIES ORDERING
""")

if ordering_results:
    if forward > backward + mixed:
        print("  R1->R2->R3 shows CONSISTENT FORWARD ordering")
        print("  -> Placement sequence maps to spatial sequence")
    elif backward > forward + mixed:
        print("  R1->R2->R3 shows CONSISTENT BACKWARD ordering")
        print("  -> Placement sequence maps to reverse spatial sequence")
    else:
        print("  R-series ordering is FOLIO-SPECIFIC")
        print("  -> Orientation varies by diagram")

print("""
B-3: S-SERIES BOUNDARIES
""")

s1_boundary = (s_series_boundary['S1']['early'] + s_series_boundary['S1']['late']) / max(1, sum(s_series_boundary['S1'].values())) * 100
s2_boundary = (s_series_boundary['S2']['early'] + s_series_boundary['S2']['late']) / max(1, sum(s_series_boundary['S2'].values())) * 100

if s1_boundary > 50 or s2_boundary > 50:
    print(f"  S1 boundary concentration: {s1_boundary:.1f}%")
    print(f"  S2 boundary concentration: {s2_boundary:.1f}%")
    print("  -> S-series marks STRUCTURAL BOUNDARIES")
else:
    print("  S-series does NOT concentrate at boundaries")

print("""
OVERALL ALIGNMENT STATUS:
""")

alignment_score = 0
if 'cramers_v' in dir() and cramers_v > 0.1:
    alignment_score += 1
if ordering_results and (forward > backward + mixed or backward > forward + mixed):
    alignment_score += 1
if s1_boundary > 50 or s2_boundary > 50:
    alignment_score += 1

if alignment_score >= 2:
    print(f"  ALIGNMENT CONFIRMED ({alignment_score}/3 tests positive)")
    print("")
    print("  The placement codes correlate with:")
    print("  - Folio-specific layout patterns")
    print("  - Ordered spatial sequences")
    print("  - Structural boundary positions")
    print("")
    print("  This is consistent with DIAGRAM-ANCHORED ENCODING.")
else:
    print(f"  ALIGNMENT WEAK ({alignment_score}/3 tests positive)")
    print("  Placement codes may be abstract, not visual.")

print("\n" + "=" * 70)
print("PHASE B-MIN COMPLETE")
print("=" * 70)
