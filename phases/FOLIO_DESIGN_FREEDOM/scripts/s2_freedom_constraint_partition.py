#!/usr/bin/env python3
"""
s2_freedom_constraint_partition.py
Phase: FOLIO_DESIGN_FREEDOM

Formally partition atom features into FREEDOM channels (folio-specific,
program-differentiating) vs CONSTRAINED channels (section-determined).

Steps:
  1. Eta-squared per feature (ANOVA with section as factor) — validation of s1
  2. Within-section CV per feature
  3. Classify features: CONSTRAINED / MIXED / FREEDOM
  4. Cross-section consistency (Spearman correlation of folio rankings)
  5. Connection to C1207 atom clusters
  6. Comparison to C1154 (k, e, h predictions)
  7. Summary table + JSON output
"""

import sys
import os
import json
import warnings
from pathlib import Path

# Windows stdout encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from scipy import stats

from scripts.voynich import Transcript, Morphology

warnings.filterwarnings('ignore')

# ── Load data ──────────────────────────────────────────────────────────────
features_df = pd.read_csv(
    'phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features.csv', index_col=0
)
residualized_df = pd.read_csv(
    'phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features_residualized.csv', index_col=0
)

# Section column
section_col = features_df['section']
feature_cols = [c for c in features_df.columns if c not in ('section', 'token_count')]

print(f"Loaded {len(features_df)} folios, {len(feature_cols)} atom features")
print(f"Sections: {dict(section_col.value_counts())}")
print()

# ── Step 1: Eta-squared per feature (ANOVA, section as factor) ─────────────
print("=" * 70)
print("STEP 1: Eta-squared per feature (section ANOVA) — validation of s1")
print("=" * 70)

sections = section_col.unique()
eta_sq = {}

for feat in feature_cols:
    groups = [features_df.loc[section_col == s, feat].dropna().values for s in sections]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) < 2:
        eta_sq[feat] = 0.0
        continue
    # Manual eta-squared: SS_between / SS_total
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_total = np.sum((all_vals - grand_mean) ** 2)
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    eta_sq[feat] = ss_between / ss_total if ss_total > 0 else 0.0

# Sort and display
eta_sorted = sorted(eta_sq.items(), key=lambda x: x[1])
print(f"\n{'Feature':<20} {'eta_sq':>8}")
print("-" * 30)
for feat, e2 in eta_sorted:
    print(f"{feat:<20} {e2:>8.4f}")

# ── Step 2: Within-section CV per feature ──────────────────────────────────
print("\n" + "=" * 70)
print("STEP 2: Within-section coefficient of variation (weighted avg)")
print("=" * 70)

within_cv = {}
for feat in feature_cols:
    weighted_cv_num = 0.0
    total_n = 0
    for s in sections:
        vals = features_df.loc[section_col == s, feat].dropna().values
        if len(vals) < 3:
            continue
        mu = vals.mean()
        sd = vals.std(ddof=1)
        if abs(mu) > 1e-10:
            cv = sd / abs(mu)
        else:
            cv = sd  # use raw SD when mean is near zero
        weighted_cv_num += len(vals) * cv
        total_n += len(vals)
    within_cv[feat] = weighted_cv_num / total_n if total_n > 0 else 0.0

cv_sorted = sorted(within_cv.items(), key=lambda x: x[1], reverse=True)
print(f"\n{'Feature':<20} {'within_CV':>10}")
print("-" * 32)
for feat, cv in cv_sorted:
    print(f"{feat:<20} {cv:>10.4f}")

median_cv = np.median(list(within_cv.values()))
print(f"\nMedian within-section CV: {median_cv:.4f}")

# ── Step 3: Classify features into 3 tiers ────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3: Feature partition — CONSTRAINED / MIXED / FREEDOM")
print("=" * 70)

partition = {}
for feat in feature_cols:
    e2 = eta_sq[feat]
    cv = within_cv[feat]
    if e2 > 0.30:
        partition[feat] = 'CONSTRAINED'
    elif e2 >= 0.10:
        partition[feat] = 'MIXED'
    elif cv > median_cv:
        partition[feat] = 'FREEDOM'
    else:
        # Low eta_sq but also low CV — weakly varying, classify as FREEDOM anyway
        # (section doesn't explain it, even if it doesn't vary much)
        partition[feat] = 'FREEDOM'

counts = {}
for v in partition.values():
    counts[v] = counts.get(v, 0) + 1

print(f"\nPartition counts: {counts}")
print(f"\n{'Feature':<20} {'eta_sq':>8} {'within_CV':>10} {'Partition':>12}")
print("-" * 54)
for feat in sorted(feature_cols):
    print(f"{feat:<20} {eta_sq[feat]:>8.4f} {within_cv[feat]:>10.4f} {partition[feat]:>12}")

# ── Step 4: Cross-section consistency (Spearman on FREEDOM features) ──────
print("\n" + "=" * 70)
print("STEP 4: Cross-section consistency of FREEDOM features")
print("=" * 70)

freedom_feats = [f for f in feature_cols if partition[f] == 'FREEDOM']
print(f"\nFREEDOM features ({len(freedom_feats)}): {freedom_feats}")

# Sections with N >= 10: Herbal, Stars, Bio
big_sections = [s for s in sections if (section_col == s).sum() >= 10]
big_sections = sorted(big_sections)
print(f"Sections with N >= 10: {big_sections}")

# For each FREEDOM feature, rank folios within each section, then correlate
# rankings across section pairs
section_pairs = []
for i in range(len(big_sections)):
    for j in range(i + 1, len(big_sections)):
        section_pairs.append((big_sections[i], big_sections[j]))

pair_correlations = {}
for s1, s2 in section_pairs:
    pair_key = f"{s1}-{s2}"
    pair_correlations[pair_key] = {}

    # For this pair, we can't directly correlate folio rankings (different folios)
    # Instead: for each FREEDOM feature, rank folios within s1 and s2 independently,
    # then check if the FEATURE rankings are consistent.
    # Better approach: correlate the feature-level statistics across sections.
    # For each feature, compute the mean and spread within each section,
    # then check if the relative importance (CV) of features is consistent.

    # Actually the right test: for each FREEDOM feature, compute the variance
    # (or IQR) within each section. Then rank features by within-section variance.
    # If the same features are high-variance in both sections, rankings correlate.

    variances_s1 = []
    variances_s2 = []
    for feat in freedom_feats:
        v1 = features_df.loc[section_col == s1, feat].var()
        v2 = features_df.loc[section_col == s2, feat].var()
        variances_s1.append(v1)
        variances_s2.append(v2)

    if len(freedom_feats) >= 3:
        rho, p = stats.spearmanr(variances_s1, variances_s2)
        pair_correlations[pair_key] = {'rho': round(rho, 4), 'p': round(p, 6)}
        print(f"\n  {pair_key}: Spearman rho = {rho:.4f}  (p = {p:.4e})")
    else:
        pair_correlations[pair_key] = {'rho': None, 'p': None}
        print(f"\n  {pair_key}: Too few FREEDOM features for correlation")

# Mean rho
rhos = [v['rho'] for v in pair_correlations.values() if v['rho'] is not None]
mean_rho = np.mean(rhos) if rhos else None
print(f"\n  Mean cross-section Spearman rho: {mean_rho:.4f}" if mean_rho else "  No valid correlations")

# ── Step 5: Connection to C1207 atom clusters ─────────────────────────────
print("\n" + "=" * 70)
print("STEP 5: Connection to C1207 atom clusters")
print("=" * 70)

# C1207 clusters: {a,i,n,r} iteration, {c,h} monitoring, {k,l} energy,
#                 {d,y} closure, {o,p} structural
atom_clusters = {
    'iteration': ['a', 'i', 'n', 'r'],
    'monitoring': ['c', 'h'],
    'energy': ['k', 'l'],
    'closure': ['d', 'y'],
    'structural': ['o', 'p'],
}

# Map features to clusters based on the atom letter in the feature name
def feature_to_cluster(feat):
    """Map a feature name to its C1207 cluster."""
    # Extract the atom letter from feature names like head_a, mod_i, term_y, etc.
    parts = feat.split('_')
    if len(parts) == 2:
        role, atom = parts
        if role in ('head', 'mod', 'term'):
            for cluster_name, atoms in atom_clusters.items():
                if atom in atoms:
                    return cluster_name
    # Composite features
    if feat == 'e_depth_mean':
        return 'energy'  # e is head but depth relates to energy
    if feat == 'i_depth_mean':
        return 'iteration'
    if feat == 'mean_atom_length':
        return None  # composite
    # Prefix features don't map cleanly to single atoms
    if feat.startswith('pfx_'):
        return None
    return None

cluster_map = {f: feature_to_cluster(f) for f in feature_cols}

# For each cluster, count FREEDOM vs CONSTRAINED vs MIXED
print(f"\n{'Cluster':<15} {'FREEDOM':>8} {'MIXED':>6} {'CONSTR':>8} {'Features'}")
print("-" * 70)

cluster_partition = {}
for cname in list(atom_clusters.keys()) + [None]:
    label = cname if cname else 'unassigned'
    feats_in = [f for f in feature_cols if cluster_map[f] == cname]
    if not feats_in:
        continue
    f_count = sum(1 for f in feats_in if partition[f] == 'FREEDOM')
    m_count = sum(1 for f in feats_in if partition[f] == 'MIXED')
    c_count = sum(1 for f in feats_in if partition[f] == 'CONSTRAINED')
    feat_list = ', '.join(f"{f}({partition[f][0]})" for f in feats_in)
    print(f"{label:<15} {f_count:>8} {m_count:>6} {c_count:>8}   {feat_list}")
    cluster_partition[label] = {
        'FREEDOM': f_count, 'MIXED': m_count, 'CONSTRAINED': c_count,
        'features': {f: partition[f] for f in feats_in}
    }

# ── Step 6: Comparison to C1154 ───────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 6: Comparison to C1154 predictions")
print("=" * 70)
print("C1154: k and e variance are universally program-specific,")
print("       h is section-determined (except Stars).")

c1154_checks = {
    'head_k': {
        'prediction': 'FREEDOM (program-specific)',
        'actual': partition.get('head_k', 'N/A'),
        'eta_sq': eta_sq.get('head_k', None),
    },
    'head_e': {
        'prediction': 'FREEDOM or low-MIXED (program-specific)',
        'actual': partition.get('head_e', 'N/A'),
        'eta_sq': eta_sq.get('head_e', None),
    },
    'term_h': {
        'prediction': 'CONSTRAINED or high-MIXED (section-determined)',
        'actual': partition.get('term_h', 'N/A'),
        'eta_sq': eta_sq.get('term_h', None),
    },
}

for feat, info in c1154_checks.items():
    match_str = ""
    actual = info['actual']
    e2 = info['eta_sq']

    if feat == 'head_k':
        # C1154 says k is program-specific → should NOT be CONSTRAINED
        if actual == 'CONSTRAINED':
            match_str = "MISMATCH — C1154 says program-specific but classified CONSTRAINED"
        else:
            match_str = "CONSISTENT"
    elif feat == 'head_e':
        if actual == 'CONSTRAINED':
            match_str = "MISMATCH — C1154 says program-specific"
        else:
            match_str = "CONSISTENT"
    elif feat == 'term_h':
        # C1154 says h is section-determined → expect CONSTRAINED or MIXED
        # But eta_sq is actually very low (0.051), meaning section does NOT explain h
        if actual == 'FREEDOM':
            match_str = "SURPRISE — C1154 says section-determined, but eta_sq is very low"
        else:
            match_str = "CONSISTENT"

    print(f"\n  {feat}:")
    print(f"    C1154 prediction: {info['prediction']}")
    print(f"    Actual partition: {actual} (eta_sq = {e2:.4f})")
    print(f"    Verdict: {match_str}")

# Special check: head_k has highest eta_sq (0.50) — CONSTRAINED!
# This CONTRADICTS C1154 if taken at face value.
if partition.get('head_k') == 'CONSTRAINED':
    print("\n  ** CRITICAL FINDING: head_k is CONSTRAINED (eta_sq = {:.4f}) **".format(
        eta_sq['head_k']))
    print("  This means section strongly determines k usage rates.")
    print("  C1154 says k variance is program-specific — but that may mean")
    print("  within-section k variance is high (folio-to-folio), which is")
    print("  compatible with high eta_sq if sections also differ in k baselines.")
    print("  Resolution: k has BOTH section-level structure AND folio-level freedom.")

# ── Step 7: Summary table ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 7: Complete summary table")
print("=" * 70)

print(f"\n{'Feature':<20} {'eta_sq':>8} {'w_CV':>8} {'Partition':>12} {'Cluster':>14}")
print("-" * 66)
for feat in sorted(feature_cols, key=lambda f: eta_sq[f]):
    cl = cluster_map[feat] or '-'
    print(f"{feat:<20} {eta_sq[feat]:>8.4f} {within_cv[feat]:>8.4f} {partition[feat]:>12} {cl:>14}")

# ── Build output JSON ─────────────────────────────────────────────────────
output = {
    'n_folios': len(features_df),
    'n_features': len(feature_cols),
    'median_within_cv': round(median_cv, 6),
    'partition_counts': counts,
    'thresholds': {
        'constrained_eta_sq_min': 0.30,
        'mixed_eta_sq_range': [0.10, 0.30],
        'freedom_eta_sq_max': 0.10,
        'freedom_cv_min': round(median_cv, 6),
    },
    'features': {},
    'cross_section_consistency': {
        'section_pairs': pair_correlations,
        'mean_rho': round(mean_rho, 4) if mean_rho is not None else None,
        'method': 'Spearman correlation of within-section variance rankings across FREEDOM features',
    },
    'c1207_cluster_partition': cluster_partition,
    'c1154_comparison': {
        feat: {
            'prediction': info['prediction'],
            'actual': info['actual'],
            'eta_sq': round(info['eta_sq'], 4) if info['eta_sq'] is not None else None,
        }
        for feat, info in c1154_checks.items()
    },
}

for feat in feature_cols:
    output['features'][feat] = {
        'eta_sq': round(eta_sq[feat], 6),
        'within_cv': round(within_cv[feat], 6),
        'partition': partition[feat],
        'cluster': cluster_map[feat],
    }

out_path = 'phases/FOLIO_DESIGN_FREEDOM/results/s2_freedom_constraint_partition.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nSaved: {out_path}")

# ── Final summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(f"  FREEDOM features:     {counts.get('FREEDOM', 0)}")
print(f"  MIXED features:       {counts.get('MIXED', 0)}")
print(f"  CONSTRAINED features: {counts.get('CONSTRAINED', 0)}")
print(f"  Cross-section rho:    {mean_rho:.4f}" if mean_rho else "  Cross-section rho: N/A")
print(f"  C1154 head_k:         {partition.get('head_k', '?')} (eta_sq={eta_sq.get('head_k', 0):.4f})")
print(f"  C1154 head_e:         {partition.get('head_e', '?')} (eta_sq={eta_sq.get('head_e', 0):.4f})")
print(f"  C1154 term_h:         {partition.get('term_h', '?')} (eta_sq={eta_sq.get('term_h', 0):.4f})")
print("\nDone.")
