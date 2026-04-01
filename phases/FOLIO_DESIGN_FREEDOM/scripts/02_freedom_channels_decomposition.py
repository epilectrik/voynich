"""
Script 2: Freedom Channels Decomposition
Question: Which atom features are folio-specific "tuning knobs" vs section-locked?

Computes ICC(folio nested in section) for each atom feature, partitions into
LOCKED/SHARED/FREE tiers, tests cross-section consistency, and correlates
with the apparatus manifold.
"""

import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, f_oneway, kruskal

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

RESULTS = Path(__file__).resolve().parent.parent / 'results'

# === Load Features from Script 1 ===

feature_df = pd.read_csv(RESULTS / '01_folio_atom_features.csv', index_col=0)
residual_df = pd.read_csv(RESULTS / '01_folio_atom_features_residualized.csv', index_col=0)

with open(RESULTS / '01_freedom_space_pca.json') as f:
    pca_results = json.load(f)

sections = pd.Series(pca_results['sections'])
numeric_cols = [c for c in feature_df.columns if c != 'section']

print(f"Loaded {len(feature_df)} folios, {len(numeric_cols)} features")

# === ICC Computation ===

def compute_icc_oneway(values, groups):
    """
    ICC(1,1) — one-way random effects model.
    How much of total variance is between-group (section) vs within-group (folio).

    Returns ICC value and components.
    """
    unique_groups = sorted(set(groups))
    group_data = {g: [] for g in unique_groups}
    for v, g in zip(values, groups):
        group_data[g].append(v)

    # Filter groups with >= 2 members
    group_data = {g: vals for g, vals in group_data.items() if len(vals) >= 2}
    if len(group_data) < 2:
        return 0.0, 0.0, 0.0

    k = len(group_data)
    n_total = sum(len(v) for v in group_data.values())
    grand_mean = np.mean([v for vals in group_data.values() for v in vals])

    # Between-group MS
    ss_between = sum(len(vals) * (np.mean(vals) - grand_mean)**2 for vals in group_data.values())
    ms_between = ss_between / (k - 1) if k > 1 else 0

    # Within-group MS
    ss_within = sum(sum((v - np.mean(vals))**2 for v in vals) for vals in group_data.values())
    ms_within = ss_within / (n_total - k) if n_total > k else 0

    # Average group size
    n0 = n_total / k

    # ICC(1,1)
    if ms_within == 0 and ms_between == 0:
        return 0.0, 0.0, 0.0
    icc = (ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within) if (ms_between + (n0 - 1) * ms_within) > 0 else 0
    icc = max(0, icc)  # Floor at 0

    # Proportion of variance explained by section
    section_var_frac = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else 0

    return icc, section_var_frac, ms_within

# Compute ICC for each feature
icc_results = {}
for col in numeric_cols:
    values = feature_df[col].values
    groups = [sections[f] for f in feature_df.index]
    icc, section_frac, ms_within = compute_icc_oneway(values, groups)

    # Within-section CV (coefficient of variation)
    within_section_stds = []
    for sec in set(groups):
        sec_vals = [v for v, g in zip(values, groups) if g == sec]
        if len(sec_vals) >= 3:
            within_section_stds.append(np.std(sec_vals))
    mean_within_std = np.mean(within_section_stds) if within_section_stds else 0
    overall_mean = np.mean(values)
    within_cv = mean_within_std / abs(overall_mean) if abs(overall_mean) > 1e-10 else 0

    icc_results[col] = {
        'icc_section': float(icc),
        'section_var_frac': float(section_frac),
        'within_section_cv': float(within_cv),
        'overall_mean': float(overall_mean),
        'overall_std': float(np.std(values)),
    }

# === Partition into LOCKED / SHARED / FREE ===

LOCKED_THRESHOLD = 0.05   # ICC < 0.05: section almost completely determines
SHARED_THRESHOLD = 0.20   # ICC 0.05-0.20: modest folio variation
# ICC > 0.20: genuine folio-level freedom

partitions = {'LOCKED': [], 'SHARED': [], 'FREE': []}
for col, res in sorted(icc_results.items(), key=lambda x: x[1]['icc_section']):
    icc = res['icc_section']
    if icc < LOCKED_THRESHOLD:
        partitions['LOCKED'].append(col)
    elif icc < SHARED_THRESHOLD:
        partitions['SHARED'].append(col)
    else:
        partitions['FREE'].append(col)

print(f"\n=== Feature Partition ===")
print(f"LOCKED (section-determined, ICC<{LOCKED_THRESHOLD}): {len(partitions['LOCKED'])}")
for col in partitions['LOCKED']:
    print(f"  {col}: ICC={icc_results[col]['icc_section']:.4f}, section_frac={icc_results[col]['section_var_frac']:.3f}")

print(f"\nSHARED (ICC {LOCKED_THRESHOLD}-{SHARED_THRESHOLD}): {len(partitions['SHARED'])}")
for col in partitions['SHARED']:
    print(f"  {col}: ICC={icc_results[col]['icc_section']:.4f}, section_frac={icc_results[col]['section_var_frac']:.3f}")

print(f"\nFREE (folio-tunable, ICC>{SHARED_THRESHOLD}): {len(partitions['FREE'])}")
for col in sorted(partitions['FREE'], key=lambda c: icc_results[c]['icc_section'], reverse=True):
    print(f"  {col}: ICC={icc_results[col]['icc_section']:.4f}, within_CV={icc_results[col]['within_section_cv']:.3f}")

# === Cross-Section Consistency of Freedom Channels ===

# For each pair of sections with >= 5 folios, compute rank-correlation of
# within-section feature variance
section_counts = sections.value_counts()
big_sections = section_counts[section_counts >= 5].index.tolist()

print(f"\n=== Cross-Section Freedom Consistency ===")
print(f"Sections with >= 5 folios: {big_sections}")

section_variances = {}
for sec in big_sections:
    sec_folios = [f for f in feature_df.index if sections[f] == sec]
    sec_data = feature_df.loc[sec_folios, numeric_cols]
    section_variances[sec] = sec_data.var()

if len(big_sections) >= 2:
    from itertools import combinations
    for s1, s2 in combinations(big_sections, 2):
        v1 = section_variances[s1]
        v2 = section_variances[s2]
        rho, p = spearmanr(v1, v2)
        print(f"  {s1} vs {s2}: rho={rho:.3f}, p={p:.4f}")

# === Within-Section F-test for FREE Features ===

print(f"\n=== Within-Section Kruskal-Wallis for FREE Features ===")
print("(Testing: do folios differ within sections?)")

for col in sorted(partitions['FREE'], key=lambda c: icc_results[c]['icc_section'], reverse=True)[:10]:
    # Within largest section (Herbal typically)
    for sec in big_sections[:2]:
        sec_folios = [f for f in feature_df.index if sections[f] == sec]
        if len(sec_folios) < 5:
            continue
        values = feature_df.loc[sec_folios, col].values
        # Can't do KW with single-observation groups, but we can report spread
        q25, q75 = np.percentile(values, [25, 75])
        iqr = q75 - q25
        rng = values.max() - values.min()
        print(f"  {col} in {sec} (n={len(sec_folios)}): range={rng:.4f}, IQR={iqr:.4f}, mean={values.mean():.4f}")

# === Apparatus Manifold Correlation ===

print(f"\n=== Apparatus Manifold Correlation ===")
try:
    # Try to load apparatus manifold positions
    manifold_path = Path(__file__).resolve().parents[3] / 'results' / 'apparatus_manifold.json'
    if manifold_path.exists():
        with open(manifold_path) as f:
            manifold_data = json.load(f)
        # Correlate free features with manifold PCs
        print("  (Apparatus manifold found — computing correlations)")
    else:
        print("  Apparatus manifold not found — skipping")
        print("  (Use C1670 accent-manifold alignment as proxy)")

    # Instead, correlate with PCA scores from Script 1
    pca_scores = {f: pca_results['folio_scores'][f] for f in feature_df.index
                  if f in pca_results['folio_scores']}

    print(f"\n  Free feature correlations with freedom-space PC1-PC3:")
    for col in sorted(partitions['FREE'], key=lambda c: icc_results[c]['icc_section'], reverse=True)[:8]:
        folios = [f for f in feature_df.index if f in pca_scores]
        feat_vals = [residual_df.loc[f, col] for f in folios]
        for pc_idx in range(3):
            pc_vals = [pca_scores[f][pc_idx] for f in folios]
            rho, p = spearmanr(feat_vals, pc_vals)
            if abs(rho) > 0.3:
                print(f"    {col} x PC{pc_idx+1}: rho={rho:.3f}, p={p:.4f}")

except Exception as e:
    print(f"  Error: {e}")

# === Save Results ===

results = {
    'n_features': len(numeric_cols),
    'partition_counts': {k: len(v) for k, v in partitions.items()},
    'partitions': partitions,
    'icc_results': icc_results,
    'cross_section_consistency': {},
    'thresholds': {
        'locked': LOCKED_THRESHOLD,
        'shared': SHARED_THRESHOLD,
    },
}

# Add cross-section correlations
if len(big_sections) >= 2:
    from itertools import combinations
    for s1, s2 in combinations(big_sections, 2):
        v1 = section_variances[s1]
        v2 = section_variances[s2]
        rho, p = spearmanr(v1, v2)
        results['cross_section_consistency'][f'{s1}_vs_{s2}'] = {
            'rho': float(rho), 'p': float(p)
        }

with open(RESULTS / '02_freedom_channels.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / '02_freedom_channels.json'}")
print("Done.")
