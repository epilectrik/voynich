"""
Script 4: AX Byproduct Test

Test whether AX class count is a predictable byproduct of total pipeline
vocabulary size, or whether AX is over/under-represented relative to expectations.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path('C:/git/voynich')
SURVIVORS = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json'
RESULTS = BASE / 'phases/AX_FUNCTIONAL_ANATOMY/results'

# Load data
with open(SURVIVORS) as f:
    surv_data = json.load(f)

# AX class definitions
AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 14, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}

ALL_49_CLASSES = set(range(1, 50))  # 1-49

# Per-record analysis
records = surv_data['records']
total_counts = []
ax_counts = []
ax_init_counts = []
ax_med_counts = []
ax_final_counts = []
ax_fractions = []

for rec in records:
    surviving = set(rec['surviving_classes'])
    total = len(surviving)
    ax = len(surviving & AX_CLASSES)
    ax_init = len(surviving & AX_INIT)
    ax_med = len(surviving & AX_MED)
    ax_final = len(surviving & AX_FINAL)

    total_counts.append(total)
    ax_counts.append(ax)
    ax_init_counts.append(ax_init)
    ax_med_counts.append(ax_med)
    ax_final_counts.append(ax_final)
    ax_fractions.append(ax / total if total > 0 else 0)

n = len(records)

# Basic statistics
mean_total = sum(total_counts) / n
mean_ax = sum(ax_counts) / n
mean_frac = sum(ax_fractions) / n

# Expected AX fraction if uniform survival
expected_uniform = len(AX_CLASSES) / len(ALL_49_CLASSES)  # 20/49

# Weighted expected: sum of individual AX class survival rates / sum of all survival rates
survival_rates = surv_data['class_survival_rates']
sum_ax_rates = sum(survival_rates.get(str(c), 0) for c in AX_CLASSES)
sum_all_rates = sum(survival_rates.get(str(c), 0) for c in ALL_49_CLASSES if str(c) in survival_rates)
expected_weighted = sum_ax_rates / sum_all_rates if sum_all_rates > 0 else 0

# Linear regression: ax_count = slope * total_count + intercept
mean_x = sum(total_counts) / n
mean_y = sum(ax_counts) / n
ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(total_counts, ax_counts))
ss_xx = sum((x - mean_x) ** 2 for x in total_counts)
ss_yy = sum((y - mean_y) ** 2 for y in ax_counts)

slope = ss_xy / ss_xx if ss_xx > 0 else 0
intercept = mean_y - slope * mean_x
r = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_xx > 0 and ss_yy > 0 else 0
r_squared = r ** 2

# Residual analysis
residuals = [ax - (slope * total + intercept) for total, ax in zip(total_counts, ax_counts)]
mean_residual = sum(residuals) / n
max_pos_residual = max(residuals)
max_neg_residual = min(residuals)
overrep = sum(1 for r in residuals if r > 0.5)
underrep = sum(1 for r in residuals if r < -0.5)

# Subgroup regressions
def linear_regression(x_vals, y_vals):
    n_local = len(x_vals)
    mx = sum(x_vals) / n_local
    my = sum(y_vals) / n_local
    sxy = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals))
    sxx = sum((x - mx) ** 2 for x in x_vals)
    syy = sum((y - my) ** 2 for y in y_vals)
    sl = sxy / sxx if sxx > 0 else 0
    it = my - sl * mx
    r_val = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0
    return {'slope': round(sl, 4), 'intercept': round(it, 4),
            'r_squared': round(r_val ** 2, 4), 'mean': round(my, 2)}

subgroup_regressions = {
    'AX_INIT': linear_regression(total_counts, ax_init_counts),
    'AX_MED': linear_regression(total_counts, ax_med_counts),
    'AX_FINAL': linear_regression(total_counts, ax_final_counts),
}

# Print results
print("=== AX BYPRODUCT TEST ===")
print(f"\nTotal A records: {n}")
print(f"Mean total surviving classes: {mean_total:.1f}")
print(f"Mean AX surviving classes: {mean_ax:.1f}")
print(f"Mean AX fraction: {mean_frac:.4f}")
print(f"Expected uniform (20/49): {expected_uniform:.4f}")
print(f"Expected weighted (by survival rates): {expected_weighted:.4f}")
print(f"Deviation from uniform: {mean_frac - expected_uniform:+.4f}")
print(f"Deviation from weighted: {mean_frac - expected_weighted:+.4f}")

print(f"\n=== LINEAR MODEL: AX = {slope:.4f} * total + {intercept:.4f} ===")
print(f"Pearson r: {r:.4f}")
print(f"R-squared: {r_squared:.4f}")
print(f"Interpretation: AX count is {'highly' if r_squared > 0.9 else 'moderately' if r_squared > 0.7 else 'weakly'} predictable from total count")

print(f"\n=== RESIDUAL ANALYSIS ===")
print(f"Mean residual: {mean_residual:.4f}")
print(f"Max positive residual: {max_pos_residual:.2f}")
print(f"Max negative residual: {max_neg_residual:.2f}")
print(f"Records AX over-represented (res > 0.5): {overrep}")
print(f"Records AX under-represented (res < -0.5): {underrep}")

print(f"\n=== SUBGROUP SCALING ===")
for sg, reg in subgroup_regressions.items():
    n_classes = len(AX_INIT if sg == 'AX_INIT' else AX_MED if sg == 'AX_MED' else AX_FINAL)
    expected_slope = n_classes / len(ALL_49_CLASSES)
    print(f"  {sg:10s}: slope={reg['slope']:.4f} (expected {expected_slope:.4f}), "
          f"R2={reg['r_squared']:.4f}, mean={reg['mean']:.2f}/{n_classes}")

# Byproduct verdict
is_byproduct = r_squared > 0.9 and abs(mean_frac - expected_weighted) < 0.02
print(f"\n=== VERDICT ===")
print(f"Is AX a pipeline byproduct? {'YES (R2>{0.9} and fraction matches expected)' if is_byproduct else 'NO (independent structure detected)'}")
if not is_byproduct:
    if r_squared <= 0.9:
        print(f"  -> R2={r_squared:.4f} indicates non-linear relationship")
    if abs(mean_frac - expected_weighted) >= 0.02:
        print(f"  -> AX fraction deviates from expected by {abs(mean_frac - expected_weighted):.4f}")

# Save results
results = {
    'per_record_stats': {
        'total_records': n,
        'mean_total_classes': round(mean_total, 2),
        'mean_ax_classes': round(mean_ax, 2),
        'mean_ax_fraction': round(mean_frac, 4),
        'expected_ax_fraction_uniform': round(expected_uniform, 4),
        'expected_ax_fraction_weighted': round(expected_weighted, 4),
    },
    'linear_model': {
        'slope': round(slope, 6),
        'intercept': round(intercept, 4),
        'r_squared': round(r_squared, 4),
        'pearson_r': round(r, 4),
    },
    'byproduct_test': {
        'actual_mean_ax_fraction': round(mean_frac, 4),
        'expected_mean_ax_fraction_weighted': round(expected_weighted, 4),
        'deviation_from_weighted': round(mean_frac - expected_weighted, 4),
        'deviation_from_uniform': round(mean_frac - expected_uniform, 4),
        'is_byproduct_consistent': is_byproduct,
    },
    'subgroup_scaling': subgroup_regressions,
    'residual_analysis': {
        'mean_residual': round(mean_residual, 4),
        'max_positive_residual': round(max_pos_residual, 2),
        'max_negative_residual': round(max_neg_residual, 2),
        'records_ax_overrepresented': overrep,
        'records_ax_underrepresented': underrep,
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'ax_byproduct_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_byproduct_test.json'}")
