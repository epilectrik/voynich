"""
T3: PP Count Predicts Cluster Breadth (H3)

Hypothesis: High PP count = narrow viability (more constraints = fewer options)
           Low PP count = broad viability (fewer constraints = more options)

This tests whether the filtering mechanism works as expected.
"""

import sys
import json
from pathlib import Path
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("T3: PP COUNT PREDICTS VIABILITY BREADTH")
print("=" * 70)

# Load data
data_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't1_profile_vectors.json'
with open(data_path) as f:
    data = json.load(f)

profiles = data['profiles']
a_record_pp = data['a_record_pp']
n_b_folios = len(data['b_folios'])

print(f"\nLoaded {len(profiles)} A-record profiles")

# Compute PP count and viability size for each record
pp_counts = []
viability_sizes = []

for key in profiles:
    pp_count = len(a_record_pp[key])
    viability = sum(profiles[key])

    pp_counts.append(pp_count)
    viability_sizes.append(viability)

pp_counts = np.array(pp_counts)
viability_sizes = np.array(viability_sizes)

print(f"\nPP count range: {pp_counts.min()} - {pp_counts.max()}")
print(f"Viability range: {viability_sizes.min()} - {viability_sizes.max()}")

# Correlation analysis
rho, p_val = stats.spearmanr(pp_counts, viability_sizes)
sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "NS"

print("\n" + "=" * 70)
print("CORRELATION ANALYSIS:")
print("=" * 70)
print(f"\nSpearman rho: {rho:.3f}")
print(f"p-value: {p_val:.4e} {sig}")

if rho < -0.3 and p_val < 0.001:
    verdict = "H3 SUPPORTED: High PP = narrow viability (negative correlation)"
elif rho > 0.3 and p_val < 0.001:
    verdict = "H3 INVERTED: High PP = broad viability (unexpected)"
else:
    verdict = "H3 NOT SUPPORTED: Weak or no correlation"

print(f"\n{verdict}")

# Bin analysis
print("\n" + "=" * 70)
print("BIN ANALYSIS:")
print("=" * 70)

bins = [(0, 0), (1, 2), (3, 5), (6, 10), (11, 20), (21, 100)]
bin_labels = ['0 PP', '1-2 PP', '3-5 PP', '6-10 PP', '11-20 PP', '21+ PP']

results = {'bins': {}}

print(f"\n{'Bin':<12} {'Count':>8} {'Mean Viability':>15} {'% of Max':>10}")
print("-" * 50)

for (lo, hi), label in zip(bins, bin_labels):
    mask = (pp_counts >= lo) & (pp_counts <= hi)
    count = mask.sum()

    if count > 0:
        mean_viab = viability_sizes[mask].mean()
        pct_max = (mean_viab / n_b_folios) * 100
    else:
        mean_viab = 0
        pct_max = 0

    results['bins'][label] = {
        'count': int(count),
        'mean_viability': float(mean_viab),
        'pct_of_max': float(pct_max),
    }

    print(f"{label:<12} {count:>8} {mean_viab:>15.1f} {pct_max:>9.1f}%")

# Regression
print("\n" + "=" * 70)
print("LINEAR REGRESSION:")
print("=" * 70)

# Filter out zero PP (universal viability)
mask = pp_counts > 0
if mask.sum() > 10:
    slope, intercept, r_val, p_val_reg, std_err = stats.linregress(
        pp_counts[mask], viability_sizes[mask]
    )
    r_squared = r_val ** 2

    print(f"\nSlope: {slope:.2f} folios per PP MIDDLE")
    print(f"R²: {r_squared:.3f}")
    print(f"p-value: {p_val_reg:.4e}")

    if slope < 0:
        print(f"\nEach additional PP MIDDLE reduces viability by {abs(slope):.1f} B-folios")
    else:
        print(f"\nEach additional PP MIDDLE increases viability by {slope:.1f} B-folios")

    results['regression'] = {
        'slope': float(slope),
        'intercept': float(intercept),
        'r_squared': float(r_squared),
        'p_value': float(p_val_reg),
    }

results['correlation'] = {
    'spearman_rho': float(rho),
    'p_value': float(p_val),
}
results['verdict'] = verdict

# Save
out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't3_pp_breadth.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
