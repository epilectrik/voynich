#!/usr/bin/env python3
"""
PUFF COMPLEXITY -> B GRAMMAR EXPANSION TEST

Hypothesis: Puff materials are ordered by the B grammar complexity required
to handle them. Material N requires the cumulative capability achieved by
folio N (not folio N specifically).

Tests:
1. Puff Position -> REGIME Correlation
2. Puff Category -> REGIME Distribution
3. Dangerous Flag -> REGIME Association
4. Cumulative Capability Threshold
5. CEI -> Puff Complexity Correlation
+ Negative Control (shuffle test)
"""

import json
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

# ============================================================
# LOAD DATA
# ============================================================

# Load Puff chapters
with open('results/puff_83_chapters.json', 'r', encoding='utf-8') as f:
    puff_data = json.load(f)

# Filter to numeric chapters only (exclude 25a interpolation)
# Keep chapters 1-83 (84 is external source, beyond the 83 match)
puff_chapters = []
for ch in puff_data['chapters']:
    if isinstance(ch['chapter'], int) and ch['chapter'] <= 83:
        puff_chapters.append(ch)

# Sort by chapter number
puff_chapters.sort(key=lambda x: x['chapter'])
print(f"Loaded {len(puff_chapters)} Puff chapters (1-83)")

# Load proposed folio order
folio_order = []
with open('results/proposed_folio_order.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if '|' in line and 'REGIME' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                try:
                    pos = int(parts[0].strip())
                    folio = parts[1].strip()
                    regime = parts[2].strip()
                    section = parts[3].strip()
                    hazard = float(parts[4].strip())
                    cei = float(parts[5].strip()) if len(parts) > 5 else 0.0
                    folio_order.append({
                        'position': pos,
                        'folio': folio,
                        'regime': regime,
                        'section': section,
                        'hazard': hazard,
                        'cei': cei
                    })
                except (ValueError, IndexError):
                    continue

folio_order.sort(key=lambda x: x['position'])
print(f"Loaded {len(folio_order)} Voynich folios in proposed order")
print()

# REGIME ordinal mapping (curriculum order)
REGIME_ORDINAL = {
    'REGIME_2': 1,  # Introductory (lowest complexity)
    'REGIME_1': 2,  # Standard
    'REGIME_4': 3,  # Precision
    'REGIME_3': 4,  # Advanced (highest complexity)
}

# ============================================================
# TEST 1: Puff Position -> REGIME Correlation
# ============================================================

print("=" * 70)
print("TEST 1: Puff Position -> REGIME Correlation")
print("=" * 70)
print()

# Map Puff positions 1-83 to Voynich positions 1-83
# Each Puff chapter N maps to Voynich folio at position N
puff_positions = []
regime_ordinals = []

for i, puff_ch in enumerate(puff_chapters[:83]):
    puff_pos = puff_ch['chapter']
    if i < len(folio_order):
        voynich_folio = folio_order[i]
        regime = voynich_folio['regime']
        regime_ord = REGIME_ORDINAL.get(regime, 0)
        puff_positions.append(puff_pos)
        regime_ordinals.append(regime_ord)

rho1, p1 = stats.spearmanr(puff_positions, regime_ordinals)
print(f"Puff Position vs REGIME Ordinal:")
print(f"  Spearman rho = {rho1:.4f}")
print(f"  p-value = {p1:.2e}")
print()

test1_pass = rho1 > 0.5 and p1 < 0.01
print(f"PASS CRITERION: rho > 0.5, p < 0.01")
print(f"RESULT: {'PASS' if test1_pass else 'FAIL'}")
print()

# ============================================================
# TEST 2: Puff Category -> REGIME Distribution
# ============================================================

print("=" * 70)
print("TEST 2: Puff Category -> REGIME Distribution")
print("=" * 70)
print()

# Map each Puff category to the REGIMEs of matched folios
category_regimes = defaultdict(list)

for i, puff_ch in enumerate(puff_chapters[:83]):
    if i < len(folio_order):
        category = puff_ch['category']
        regime = folio_order[i]['regime']
        category_regimes[category].append(regime)

# Show distribution for major categories
major_categories = ['FLOWER', 'HERB', 'ROOT', 'TREE_FLOWER', 'FUNGUS', 'ANIMAL', 'OIL']
print("Category -> REGIME Distribution:")
print()

category_means = {}
for cat in major_categories:
    if cat in category_regimes:
        regimes = category_regimes[cat]
        regime_counts = Counter(regimes)
        ordinals = [REGIME_ORDINAL.get(r, 0) for r in regimes]
        mean_ord = np.mean(ordinals) if ordinals else 0
        category_means[cat] = mean_ord

        print(f"  {cat} (n={len(regimes)}):")
        print(f"    Distribution: {dict(regime_counts)}")
        print(f"    Mean ordinal: {mean_ord:.2f}")
        print()

# Kruskal-Wallis test across categories with enough samples
cat_groups = []
cat_names = []
for cat in major_categories:
    if cat in category_regimes and len(category_regimes[cat]) >= 3:
        ordinals = [REGIME_ORDINAL.get(r, 0) for r in category_regimes[cat]]
        cat_groups.append(ordinals)
        cat_names.append(cat)

if len(cat_groups) >= 2:
    h_stat, p2 = stats.kruskal(*cat_groups)
    print(f"Kruskal-Wallis test (categories with n>=3):")
    print(f"  H-statistic = {h_stat:.4f}")
    print(f"  p-value = {p2:.4f}")
else:
    p2 = 1.0
    print("Insufficient category groups for Kruskal-Wallis test")

print()
test2_pass = p2 < 0.05
print(f"PASS CRITERION: p < 0.05 (significant category-REGIME association)")
print(f"RESULT: {'PASS' if test2_pass else 'FAIL'}")
print()

# ============================================================
# TEST 3: Dangerous Flag -> REGIME_4 (Precision) Association
# ============================================================

print("=" * 70)
print("TEST 3: Dangerous Flag -> REGIME_4 (Precision) Association")
print("=" * 70)
print()

# Dangerous materials should require PRECISION handling (REGIME_4)
# Not just "higher" regimes - specifically tight-tolerance execution

dangerous_regimes = []
safe_regimes = []

for i, puff_ch in enumerate(puff_chapters[:83]):
    if i < len(folio_order):
        regime = folio_order[i]['regime']

        if puff_ch.get('dangerous', False):
            dangerous_regimes.append(regime)
        else:
            safe_regimes.append(regime)

# Count REGIME_4 proportion in each group
dangerous_r4_count = sum(1 for r in dangerous_regimes if r == 'REGIME_4')
safe_r4_count = sum(1 for r in safe_regimes if r == 'REGIME_4')

dangerous_r4_rate = dangerous_r4_count / len(dangerous_regimes) if dangerous_regimes else 0
safe_r4_rate = safe_r4_count / len(safe_regimes) if safe_regimes else 0

print(f"Dangerous materials (n={len(dangerous_regimes)}):")
print(f"  REGIME distribution: {Counter(dangerous_regimes)}")
print(f"  REGIME_4 rate: {dangerous_r4_rate:.1%} ({dangerous_r4_count}/{len(dangerous_regimes)})")
print()
print(f"Safe materials (n={len(safe_regimes)}):")
print(f"  REGIME_4 rate: {safe_r4_rate:.1%} ({safe_r4_count}/{len(safe_regimes)})")
print()

# Fisher's exact test: Are dangerous materials more likely to be REGIME_4?
# Contingency table: [[dangerous_R4, dangerous_other], [safe_R4, safe_other]]
dangerous_other = len(dangerous_regimes) - dangerous_r4_count
safe_other = len(safe_regimes) - safe_r4_count

contingency = [[dangerous_r4_count, dangerous_other], [safe_r4_count, safe_other]]
odds_ratio, p3 = stats.fisher_exact(contingency, alternative='greater')

print(f"Fisher's exact test (dangerous -> REGIME_4):")
print(f"  Odds ratio = {odds_ratio:.2f}")
print(f"  p-value = {p3:.4f}")
print()

# Also check: what's the enrichment?
baseline_r4_rate = (dangerous_r4_count + safe_r4_count) / 83
enrichment = dangerous_r4_rate / baseline_r4_rate if baseline_r4_rate > 0 else 0
print(f"REGIME_4 baseline rate: {baseline_r4_rate:.1%}")
print(f"Dangerous enrichment: {enrichment:.2f}x")
print()

test3_pass = p3 < 0.10 and dangerous_r4_rate > safe_r4_rate  # Relaxed p for small n
print(f"PASS CRITERION: p < 0.10 (relaxed for n=5), dangerous R4 rate > safe R4 rate")
print(f"RESULT: {'PASS' if test3_pass else 'FAIL'}")
print()

# ============================================================
# TEST 4: Cumulative Capability Threshold
# ============================================================

print("=" * 70)
print("TEST 4: Cumulative Capability Threshold")
print("=" * 70)
print()

# For each REGIME, find which Puff positions map to it
regime_puff_positions = defaultdict(list)

for i, puff_ch in enumerate(puff_chapters[:83]):
    if i < len(folio_order):
        puff_pos = puff_ch['chapter']
        regime = folio_order[i]['regime']
        regime_puff_positions[regime].append(puff_pos)

print("Puff positions handled by each REGIME:")
print()

regime_stats = {}
for regime in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']:
    positions = regime_puff_positions.get(regime, [])
    if positions:
        min_pos = min(positions)
        max_pos = max(positions)
        mean_pos = np.mean(positions)
        regime_stats[regime] = {
            'min': min_pos,
            'max': max_pos,
            'mean': mean_pos,
            'n': len(positions)
        }
        print(f"  {regime} (n={len(positions)}):")
        print(f"    Range: {min_pos} - {max_pos}")
        print(f"    Mean position: {mean_pos:.1f}")
        print()

# Check monotonic relationship: higher REGIME ordinal -> higher max Puff position
regime_order = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
max_positions = [regime_stats.get(r, {}).get('max', 0) for r in regime_order]
mean_positions = [regime_stats.get(r, {}).get('mean', 0) for r in regime_order]

# Test if max positions are monotonically increasing
ordinals = [1, 2, 3, 4]
rho_max, p_max = stats.spearmanr(ordinals, max_positions)
rho_mean, p_mean = stats.spearmanr(ordinals, mean_positions)

print(f"Max position correlation with REGIME ordinal:")
print(f"  rho = {rho_max:.4f}, p = {p_max:.4f}")
print()
print(f"Mean position correlation with REGIME ordinal:")
print(f"  rho = {rho_mean:.4f}, p = {p_mean:.4f}")
print()

test4_pass = rho_mean > 0.5  # Relaxed: just need positive correlation
print(f"PASS CRITERION: Mean position increases with REGIME ordinal (rho > 0.5)")
print(f"RESULT: {'PASS' if test4_pass else 'FAIL'}")
print()

# ============================================================
# TEST 5: CEI -> Puff Position Correlation
# ============================================================

print("=" * 70)
print("TEST 5: CEI -> Puff Position Correlation")
print("=" * 70)
print()

puff_pos_list = []
cei_list = []

for i, puff_ch in enumerate(puff_chapters[:83]):
    if i < len(folio_order):
        puff_pos_list.append(puff_ch['chapter'])
        cei_list.append(folio_order[i]['cei'])

rho5, p5 = stats.spearmanr(puff_pos_list, cei_list)
print(f"Puff Position vs Folio CEI:")
print(f"  Spearman rho = {rho5:.4f}")
print(f"  p-value = {p5:.2e}")
print()

test5_pass = rho5 > 0.6 and p5 < 0.001
print(f"PASS CRITERION: rho > 0.6, p < 0.001")
print(f"RESULT: {'PASS' if test5_pass else 'FAIL'}")
print()

# ============================================================
# NEGATIVE CONTROL: Shuffle Test
# ============================================================

print("=" * 70)
print("NEGATIVE CONTROL: Shuffle Test")
print("=" * 70)
print()

n_permutations = 1000
perm_rho1_values = []
perm_rho5_values = []

np.random.seed(42)

# Get original ordinals and CEI
orig_regime_ordinals = regime_ordinals.copy()
orig_cei = cei_list.copy()

for _ in range(n_permutations):
    # Shuffle the folio order (break Puff-Voynich alignment)
    shuffled_indices = np.random.permutation(len(folio_order))

    # Compute correlation with shuffled data
    shuffled_ordinals = [REGIME_ORDINAL.get(folio_order[i]['regime'], 0) for i in shuffled_indices[:len(puff_positions)]]
    shuffled_cei = [folio_order[i]['cei'] for i in shuffled_indices[:len(puff_pos_list)]]

    perm_rho1, _ = stats.spearmanr(puff_positions, shuffled_ordinals)
    perm_rho5, _ = stats.spearmanr(puff_pos_list, shuffled_cei)

    perm_rho1_values.append(perm_rho1)
    perm_rho5_values.append(perm_rho5)

# Calculate percentile of real correlation in permuted distribution
percentile_rho1 = np.mean([rho1 > p for p in perm_rho1_values]) * 100
percentile_rho5 = np.mean([rho5 > p for p in perm_rho5_values]) * 100

print(f"Test 1 (Position-REGIME):")
print(f"  Real rho = {rho1:.4f}")
print(f"  Permuted mean = {np.mean(perm_rho1_values):.4f}, std = {np.std(perm_rho1_values):.4f}")
print(f"  Percentile of real: {percentile_rho1:.1f}%")
print()

print(f"Test 5 (Position-CEI):")
print(f"  Real rho = {rho5:.4f}")
print(f"  Permuted mean = {np.mean(perm_rho5_values):.4f}, std = {np.std(perm_rho5_values):.4f}")
print(f"  Percentile of real: {percentile_rho5:.1f}%")
print()

control_pass = percentile_rho1 > 95 and percentile_rho5 > 95
print(f"PASS CRITERION: Real correlations exceed 95% of permuted")
print(f"RESULT: {'PASS' if control_pass else 'FAIL'}")
print()

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

tests_passed = sum([test1_pass, test2_pass, test3_pass, test4_pass, test5_pass])
total_tests = 5

print(f"Test Results:")
print(f"  Test 1 (Position-REGIME):      {'PASS' if test1_pass else 'FAIL'}")
print(f"  Test 2 (Category-REGIME):      {'PASS' if test2_pass else 'FAIL'}")
print(f"  Test 3 (Dangerous-Precision):  {'PASS' if test3_pass else 'FAIL'}")
print(f"  Test 4 (Cumulative Threshold): {'PASS' if test4_pass else 'FAIL'}")
print(f"  Test 5 (Position-CEI):         {'PASS' if test5_pass else 'FAIL'}")
print(f"  Negative Control:              {'PASS' if control_pass else 'FAIL'}")
print()
print(f"Total: {tests_passed}/{total_tests} tests passed")
print()

if tests_passed == 5 and control_pass:
    verdict = "STRONG SUPPORT"
    interpretation = "Cumulative threshold model VALIDATED"
elif tests_passed >= 4:
    verdict = "PARTIAL SUPPORT"
    interpretation = "Model needs refinement"
elif tests_passed >= 3:
    verdict = "WEAK SUPPORT"
    interpretation = "Relationship exists but weaker than predicted"
else:
    verdict = "FALSIFIED"
    interpretation = "No systematic complexity relationship"

print(f"VERDICT: {verdict}")
print(f"INTERPRETATION: {interpretation}")
print()

if tests_passed >= 4:
    print("IMPLICATIONS:")
    print("  - Puff chapter order = B grammar expansion requirements")
    print("  - 83 convergence = shared complexity ceiling (mastery horizon)")
    print("  - Material N requires grammar complexity level N (cumulative)")
    print("  - Puff status: CONTEXTUAL -> STRUCTURAL (parallel complexity ladders)")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'hypothesis': 'Puff materials ordered by B grammar complexity requirements',
    'tests': {
        'test1_position_regime': {
            'rho': float(rho1),
            'p_value': float(p1),
            'passed': bool(test1_pass)
        },
        'test2_category_regime': {
            'kruskal_h': float(h_stat) if len(cat_groups) >= 2 else None,
            'p_value': float(p2),
            'passed': bool(test2_pass),
            'category_means': {k: float(v) for k, v in category_means.items()}
        },
        'test3_dangerous_precision': {
            'dangerous_n': len(dangerous_regimes),
            'dangerous_r4_rate': float(dangerous_r4_rate),
            'safe_r4_rate': float(safe_r4_rate),
            'odds_ratio': float(odds_ratio),
            'enrichment': float(enrichment),
            'p_value': float(p3),
            'passed': bool(test3_pass)
        },
        'test4_cumulative_threshold': {
            'regime_stats': {r: {k: int(v) if isinstance(v, (int, np.integer)) else float(v)
                                 for k, v in s.items()}
                           for r, s in regime_stats.items()},
            'mean_position_rho': float(rho_mean),
            'passed': bool(test4_pass)
        },
        'test5_position_cei': {
            'rho': float(rho5),
            'p_value': float(p5),
            'passed': bool(test5_pass)
        }
    },
    'negative_control': {
        'n_permutations': n_permutations,
        'test1_percentile': float(percentile_rho1),
        'test5_percentile': float(percentile_rho5),
        'passed': bool(control_pass)
    },
    'summary': {
        'tests_passed': tests_passed,
        'total_tests': total_tests,
        'control_passed': bool(control_pass),
        'verdict': verdict,
        'interpretation': interpretation
    }
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

with open('results/puff_regime_complexity.json', 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print()
print(f"Results saved to results/puff_regime_complexity.json")
