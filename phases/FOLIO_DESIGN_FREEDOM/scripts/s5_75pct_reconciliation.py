#!/usr/bin/env python3
"""
s5_75pct_reconciliation.py
Phase: FOLIO_DESIGN_FREEDOM

Reconcile the ~75% within-section atom variance with C1169's ~27% AXM design freedom.

Hypothesis: The 75% is genuine but multi-dimensional. AXM measures one dynamical
property (self-transition rate). Atoms measure 30 compositional dimensions. Most
atom variance is AXM-orthogonal.

Steps:
  1. Compute AXM proxy per folio (MIDDLE-class self-transition rate)
  2. Regress each atom feature against AXM proxy within sections -> R² per feature
  3. Aggregate AXM absorption via PCA
  4. ICC-based measurement noise estimation (4-chunk split)
  5. Build reconciliation table
  6. Compare to C1169
"""

import sys
import os
import json
import warnings

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from collections import defaultdict

# Ensure repo root
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('../../..')
sys.path.insert(0, os.getcwd())

from scripts.voynich import Transcript, Morphology

# ─────────────────────────────────────────────
# Load s1 outputs
# ─────────────────────────────────────────────
features_df = pd.read_csv('phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features.csv', index_col=0)
residualized_df = pd.read_csv('phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features_residualized.csv', index_col=0)

with open('phases/FOLIO_DESIGN_FREEDOM/results/s1_variance_decomposition.json') as f:
    s1_results = json.load(f)

anova = s1_results['anova']

# Feature columns (exclude token_count and section)
feat_cols = [c for c in features_df.columns if c not in ('token_count', 'section')]
n_features = len(feat_cols)
print(f"Loaded {len(features_df)} folios, {n_features} atom features")

# ─────────────────────────────────────────────
# Step 1: Compute AXM proxy per folio
# Self-transition rate: fraction of consecutive token pairs
# where MIDDLE class repeats
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 1: AXM PROXY (MIDDLE self-transition rate)")
print("="*60)

tx = Transcript()
morph = Morphology()

# Group B tokens by folio, preserving order
folio_tokens = defaultdict(list)
for t in tx.currier_b():
    if not t.is_label and not t.is_uncertain and t.word.strip():
        folio_tokens[t.folio].append(t.word)

# Compute self-transition rate per folio
axm_proxy = {}
for folio, words in folio_tokens.items():
    if folio not in features_df.index:
        continue
    # Extract MIDDLEs
    middles = []
    for w in words:
        try:
            m = morph.extract(w)
            if m.middle:
                middles.append(m.middle)
        except Exception:
            continue

    if len(middles) < 2:
        continue

    # Count self-transitions (consecutive same MIDDLE)
    transitions = 0
    self_trans = 0
    for i in range(len(middles) - 1):
        transitions += 1
        if middles[i] == middles[i+1]:
            self_trans += 1

    axm_proxy[folio] = self_trans / transitions if transitions > 0 else 0.0

axm_series = pd.Series(axm_proxy)
common_folios = features_df.index.intersection(axm_series.index)
axm_series = axm_series.loc[common_folios]

print(f"AXM proxy computed for {len(axm_series)} folios")
print(f"  Mean self-transition rate: {axm_series.mean():.4f}")
print(f"  Std:  {axm_series.std():.4f}")
print(f"  Range: [{axm_series.min():.4f}, {axm_series.max():.4f}]")

# ─────────────────────────────────────────────
# Step 2: AXM-captured atom variance per feature
# Within each section, regress atom feature ~ AXM proxy
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: AXM-CAPTURED VARIANCE PER FEATURE")
print("="*60)

sections = features_df.loc[common_folios, 'section'] if 'section' in features_df.columns else None
if sections is None:
    # Section should be in features_df
    print("WARNING: section column not found, loading from residualized_df")
    sections = residualized_df.loc[common_folios, 'section']

section_list = sections.unique()

def within_section_r2(feature_values, axm_values, section_labels):
    """Compute pooled within-section R² of feature ~ AXM."""
    ss_res_total = 0.0
    ss_tot_total = 0.0

    for sec in section_labels.unique():
        mask = section_labels == sec
        if mask.sum() < 3:  # Need at least 3 points for meaningful regression
            continue

        x = axm_values[mask].values
        y = feature_values[mask].values

        # Remove NaN
        valid = ~(np.isnan(x) | np.isnan(y))
        if valid.sum() < 3:
            continue
        x, y = x[valid], y[valid]

        # Section-demean (within-section variance)
        y_dm = y - y.mean()
        x_dm = x - x.mean()

        ss_tot = np.sum(y_dm**2)
        if ss_tot < 1e-12:
            continue

        # OLS: y_dm = beta * x_dm + residual
        denom = np.sum(x_dm**2)
        if denom < 1e-12:
            ss_res_total += ss_tot
            ss_tot_total += ss_tot
            continue

        beta = np.sum(x_dm * y_dm) / denom
        y_pred = beta * x_dm
        ss_res = np.sum((y_dm - y_pred)**2)

        ss_res_total += ss_res
        ss_tot_total += ss_tot

    if ss_tot_total < 1e-12:
        return 0.0
    return 1.0 - (ss_res_total / ss_tot_total)

feature_r2 = {}
for feat in feat_cols:
    r2 = within_section_r2(
        features_df.loc[common_folios, feat],
        axm_series,
        sections.loc[common_folios]
    )
    feature_r2[feat] = r2

# Sort by R²
sorted_r2 = sorted(feature_r2.items(), key=lambda x: -x[1])

print(f"\nFeature R² (within-section, regressed on AXM proxy):")
print(f"{'Feature':<22} {'R²':>8} {'AXM-redundant?':>16}")
print("-" * 50)
for feat, r2 in sorted_r2:
    flag = "YES" if r2 > 0.15 else ("partial" if r2 > 0.05 else "no")
    print(f"  {feat:<20} {r2:>8.4f} {flag:>16}")

mean_r2 = np.mean(list(feature_r2.values()))
print(f"\n  Mean R² across features: {mean_r2:.4f}")
print(f"  Features with R² > 0.15: {sum(1 for r in feature_r2.values() if r > 0.15)}")
print(f"  Features with R² > 0.05: {sum(1 for r in feature_r2.values() if r > 0.05)}")

# ─────────────────────────────────────────────
# Step 3: Aggregate AXM absorption via PCA
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3: AGGREGATE AXM ABSORPTION (PCA-based)")
print("="*60)

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Use residualized features (section effect removed)
resid_feats = residualized_df.loc[common_folios, feat_cols].copy()
resid_feats = resid_feats.dropna(axis=1, how='all')
valid_cols = resid_feats.columns.tolist()

# Standardize
scaler = StandardScaler()
X_std = scaler.fit_transform(resid_feats[valid_cols].values)

# PCA
n_comp = min(len(common_folios), len(valid_cols))
pca = PCA(n_components=n_comp)
pcs = pca.fit_transform(X_std)

# Correlate each PC with AXM proxy
axm_aligned = axm_series.loc[resid_feats.index].values
pc_axm_r2 = []
total_axm_absorbed = 0.0

print(f"\n{'PC':<6} {'Var%':>7} {'r²(AXM)':>10} {'Absorbed%':>11}")
print("-" * 38)

for i in range(min(20, n_comp)):
    pc_vals = pcs[:, i]
    # Correlation with AXM
    valid = ~np.isnan(axm_aligned)
    if valid.sum() < 3:
        r = 0.0
    else:
        corr = np.corrcoef(pc_vals[valid], axm_aligned[valid])
        r = corr[0, 1] if not np.isnan(corr[0, 1]) else 0.0

    r2 = r**2
    var_pct = pca.explained_variance_ratio_[i] * 100
    absorbed = var_pct * r2
    total_axm_absorbed += absorbed
    pc_axm_r2.append({'pc': i+1, 'var_pct': var_pct, 'r2_axm': r2, 'absorbed_pct': absorbed})

    if i < 15:
        print(f"  PC{i+1:<3} {var_pct:>6.2f}% {r2:>9.4f} {absorbed:>10.3f}%")

# Sum remaining PCs
remaining_absorbed = 0.0
for i in range(20, n_comp):
    pc_vals = pcs[:, i]
    valid = ~np.isnan(axm_aligned)
    if valid.sum() >= 3:
        corr = np.corrcoef(pc_vals[valid], axm_aligned[valid])
        r = corr[0, 1] if not np.isnan(corr[0, 1]) else 0.0
        r2 = r**2
        remaining_absorbed += pca.explained_variance_ratio_[i] * 100 * r2
total_axm_absorbed += remaining_absorbed

print(f"\n  Total AXM-absorbed variance: {total_axm_absorbed:.2f}% of within-section variance")

# Convert to fraction of total variance
# Within-section variance is ~75% of total
mean_eta2 = np.mean([v['eta2'] for v in anova.values() if v.get('eta2') is not None])
within_section_frac = 1.0 - mean_eta2
axm_absorbed_of_total = total_axm_absorbed / 100.0 * within_section_frac

print(f"  Within-section fraction of total: {within_section_frac:.4f}")
print(f"  AXM-absorbed as fraction of total: {axm_absorbed_of_total:.4f} ({axm_absorbed_of_total*100:.2f}%)")

# ─────────────────────────────────────────────
# Step 4: Measurement noise (ICC via 4-chunk split)
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 4: MEASUREMENT NOISE (ICC, 4-chunk split)")
print("="*60)

def compute_atom_features_for_chunk(words, morph_obj):
    """Compute the same atom features used in s1, but for a subset of words."""
    if len(words) < 10:
        return None

    heads = defaultdict(int)
    mods = defaultdict(int)
    terms = defaultdict(int)
    prefixes = defaultdict(int)
    e_depths = []
    i_depths = []
    atom_lengths = []
    n_atomized = 0

    for w in words:
        try:
            a = morph_obj.atomize(w)
        except Exception:
            continue

        n_atomized += 1

        # Head
        head_found = False
        for atom_name, role, _ in a.atoms:
            if role == 'HEAD':
                heads[atom_name] += 1
                head_found = True
                break
        if not head_found:
            heads['headless'] += 1

        # Modifiers
        for atom_name, role, _ in a.atoms:
            if role == 'MOD':
                mods[atom_name] += 1

        # Terminal
        for atom_name, role, _ in a.atoms:
            if role == 'TERM':
                terms[atom_name] += 1
                break  # first terminal only

        # Prefix
        pfx = a.prefix if a.prefix else 'bare'
        prefixes[pfx] += 1

        e_depths.append(a.e_depth)

        # i_depth: count 'i' MODs
        i_count = sum(1 for an, r, _ in a.atoms if r == 'MOD' and an == 'i')
        i_depths.append(i_count)

        atom_lengths.append(len(a.atoms))

    if n_atomized < 10:
        return None

    features = {}
    # Head fractions
    for h in ['a', 'e', 'o', 'k', 't', 'headless']:
        features[f'head_{h}'] = heads.get(h, 0) / n_atomized

    # Mod fractions (per token, not per mod)
    for m in ['p', 'f', 'i', 'c', 'd', 's']:
        features[f'mod_{m}'] = mods.get(m, 0) / n_atomized

    # Term fractions
    for t in ['y', 'n', 'l', 'r', 'm', 'h']:
        features[f'term_{t}'] = terms.get(t, 0) / n_atomized

    # Prefix fractions
    for p in ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'ct', 'bare']:
        features[f'pfx_{p}'] = prefixes.get(p, 0) / n_atomized

    features['e_depth_mean'] = np.mean(e_depths) if e_depths else 0.0
    features['i_depth_mean'] = np.mean(i_depths) if i_depths else 0.0
    features['mean_atom_length'] = np.mean(atom_lengths) if atom_lengths else 0.0

    return features

# Split each folio into 4 chunks, compute features per chunk
icc_results = {}
folio_chunk_data = {}  # folio -> list of feature dicts

for folio in common_folios:
    words = folio_tokens.get(folio, [])
    if len(words) < 40:  # Need at least 10 per chunk
        continue

    chunk_size = len(words) // 4
    chunks = []
    for c in range(4):
        start = c * chunk_size
        end = start + chunk_size if c < 3 else len(words)
        chunk_words = words[start:end]
        feats = compute_atom_features_for_chunk(chunk_words, morph)
        if feats is not None:
            chunks.append(feats)

    if len(chunks) >= 3:  # Need at least 3 chunks
        folio_chunk_data[folio] = chunks

print(f"Folios with valid chunk data: {len(folio_chunk_data)}")

# Compute ICC per feature
# ICC(1,1) = (MS_between - MS_within) / (MS_between + (k-1)*MS_within)
for feat in feat_cols:
    folio_vals = []  # list of lists: each inner list = chunk values for one folio
    for folio, chunks in folio_chunk_data.items():
        vals = [ch.get(feat, 0.0) for ch in chunks]
        if len(vals) >= 3:
            folio_vals.append(vals)

    if len(folio_vals) < 10:
        icc_results[feat] = {'icc': np.nan, 'reliable': False, 'n_folios': len(folio_vals)}
        continue

    # Pad to equal length (4 chunks each)
    k = 4  # target chunks
    n = len(folio_vals)

    # Build matrix: n_folios x k
    # Some folios may have 3 chunks, pad with NaN and use available
    all_vals = []
    for fv in folio_vals:
        row = fv[:k]
        while len(row) < k:
            row.append(np.nan)
        all_vals.append(row)

    mat = np.array(all_vals)  # n x k

    # Remove rows with any NaN
    valid_rows = ~np.any(np.isnan(mat), axis=1)
    mat = mat[valid_rows]
    n = mat.shape[0]

    if n < 5:
        icc_results[feat] = {'icc': np.nan, 'reliable': False, 'n_folios': n}
        continue

    # Grand mean
    grand_mean = mat.mean()

    # Row means (folio means)
    row_means = mat.mean(axis=1)

    # MS_between: k * variance of row means
    MS_between = k * np.sum((row_means - grand_mean)**2) / (n - 1)

    # MS_within: mean of within-folio variances
    within_ss = np.sum((mat - row_means[:, np.newaxis])**2)
    MS_within = within_ss / (n * (k - 1))

    if (MS_between + (k - 1) * MS_within) < 1e-15:
        icc_val = 0.0
    else:
        icc_val = (MS_between - MS_within) / (MS_between + (k - 1) * MS_within)

    icc_results[feat] = {
        'icc': float(icc_val),
        'reliable': icc_val >= 0.10,
        'n_folios': n
    }

# Report
sorted_icc = sorted(icc_results.items(), key=lambda x: x[1].get('icc', -1) if not np.isnan(x[1].get('icc', -1)) else -1)
print(f"\n{'Feature':<22} {'ICC':>8} {'Reliable':>10}")
print("-" * 44)
unreliable_count = 0
for feat, info in sorted_icc:
    icc = info['icc']
    if np.isnan(icc):
        print(f"  {feat:<20} {'N/A':>8} {'N/A':>10}")
        unreliable_count += 1
    else:
        flag = "YES" if info['reliable'] else "NO"
        print(f"  {feat:<20} {icc:>8.4f} {flag:>10}")
        if not info['reliable']:
            unreliable_count += 1

reliable_features = [f for f, info in icc_results.items() if info.get('reliable', False)]
unreliable_features = [f for f, info in icc_results.items() if not info.get('reliable', False)]
print(f"\n  Reliable features (ICC >= 0.10): {len(reliable_features)}/{n_features}")
print(f"  Unreliable features (ICC < 0.10 or N/A): {len(unreliable_features)}/{n_features}")

# ─────────────────────────────────────────────
# Step 5: Build reconciliation table
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5: RECONCILIATION TABLE")
print("="*60)

reconciliation = {}
for feat in feat_cols:
    eta2 = anova.get(feat, {}).get('eta2', 0.0)
    within = 1.0 - eta2
    r2_axm = feature_r2.get(feat, 0.0)
    axm_within = r2_axm * within  # AXM-captured portion of within-section
    icc = icc_results.get(feat, {}).get('icc', np.nan)
    reliable = icc_results.get(feat, {}).get('reliable', True)  # default to reliable if unknown

    # Noise estimate: for unreliable features, assume a fraction is noise
    # ICC < 0.10 means most between-folio variance is measurement noise
    if not reliable and not np.isnan(icc):
        noise_frac = within * (1.0 - max(icc, 0.0))  # unreliable within-section portion
    else:
        noise_frac = 0.0

    genuine = within - axm_within - noise_frac
    genuine = max(genuine, 0.0)

    reconciliation[feat] = {
        'section_eta2': eta2,
        'within_section': within,
        'axm_r2': r2_axm,
        'axm_captured_within': axm_within,
        'icc': float(icc) if not np.isnan(icc) else None,
        'reliable': reliable,
        'noise_frac': noise_frac,
        'genuine_freedom': genuine
    }

print(f"\n{'Feature':<22} {'Sect%':>7} {'Within%':>8} {'AXM%':>7} {'Noise%':>8} {'Free%':>7} {'ICC':>7}")
print("-" * 72)
for feat in sorted(reconciliation.keys(), key=lambda f: -reconciliation[f]['genuine_freedom']):
    r = reconciliation[feat]
    icc_str = f"{r['icc']:.3f}" if r['icc'] is not None else "N/A"
    print(f"  {feat:<20} {r['section_eta2']*100:>6.1f} {r['within_section']*100:>7.1f} "
          f"{r['axm_captured_within']*100:>6.2f} {r['noise_frac']*100:>7.2f} "
          f"{r['genuine_freedom']*100:>6.1f} {icc_str:>7}")

# ─────────────────────────────────────────────
# Step 6: Aggregate reconciliation
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 6: AGGREGATE RECONCILIATION")
print("="*60)

# Average across all features (equal weight)
avg_section = np.mean([r['section_eta2'] for r in reconciliation.values()])
avg_axm_within = np.mean([r['axm_captured_within'] for r in reconciliation.values()])
avg_noise = np.mean([r['noise_frac'] for r in reconciliation.values()])
avg_genuine = np.mean([r['genuine_freedom'] for r in reconciliation.values()])

# Also compute for reliable features only
if reliable_features:
    rel_section = np.mean([reconciliation[f]['section_eta2'] for f in reliable_features])
    rel_axm = np.mean([reconciliation[f]['axm_captured_within'] for f in reliable_features])
    rel_noise = np.mean([reconciliation[f]['noise_frac'] for f in reliable_features])
    rel_genuine = np.mean([reconciliation[f]['genuine_freedom'] for f in reliable_features])
else:
    rel_section = rel_axm = rel_noise = rel_genuine = 0.0

print(f"\n{'Source':<35} {'All Features':>14} {'Reliable Only':>15}")
print("-" * 68)
print(f"  {'Section-determined':<33} {avg_section*100:>12.1f}% {rel_section*100:>13.1f}%")
print(f"  {'AXM-captured within-section':<33} {avg_axm_within*100:>12.2f}% {rel_axm*100:>13.2f}%")
print(f"  {'Measurement noise (low ICC)':<33} {avg_noise*100:>12.2f}% {rel_noise*100:>13.2f}%")
print(f"  {'Genuine atom freedom':<33} {avg_genuine*100:>12.1f}% {rel_genuine*100:>13.1f}%")
total_check = avg_section + avg_axm_within + avg_noise + avg_genuine
print(f"  {'TOTAL':<33} {total_check*100:>12.1f}%")

# ─────────────────────────────────────────────
# Step 7: Compare to C1169
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 7: COMPARISON TO C1169 (~27% AXM DESIGN FREEDOM)")
print("="*60)

c1169_freedom = 0.27  # ~27% AXM design freedom

print(f"\n  C1169 AXM design freedom:           ~{c1169_freedom*100:.0f}%")
print(f"  Atom genuine freedom (all):          {avg_genuine*100:.1f}%")
print(f"  Atom genuine freedom (reliable):     {rel_genuine*100:.1f}%")

ratio_all = avg_genuine / c1169_freedom if c1169_freedom > 0 else float('inf')
ratio_rel = rel_genuine / c1169_freedom if c1169_freedom > 0 else float('inf')

print(f"\n  Ratio (atom freedom / AXM freedom):")
print(f"    All features:       {ratio_all:.2f}x")
print(f"    Reliable features:  {ratio_rel:.2f}x")

# Interpretation
print(f"\n  INTERPRETATION:")
if rel_genuine > 0.50:
    print(f"  Atoms capture dramatically MORE design freedom ({rel_genuine*100:.0f}%) than AXM alone (27%).")
    print(f"  The 75% within-section variance is genuine: atoms measure compositional")
    print(f"  dimensions orthogonal to AXM's single dynamical property.")
    print(f"  AXM absorbs only {rel_axm*100:.1f}% of within-section variance.")
    verdict = "ATOMS_ORTHOGONAL_TO_AXM"
elif rel_genuine > 0.30:
    print(f"  Atoms capture moderately more freedom ({rel_genuine*100:.0f}%) than AXM (27%).")
    print(f"  Most atom dimensions are AXM-orthogonal, but AXM captures a meaningful share.")
    verdict = "PARTIALLY_INDEPENDENT"
elif rel_genuine > 0.20:
    print(f"  Atom freedom ({rel_genuine*100:.0f}%) is close to AXM freedom (27%).")
    print(f"  Atoms may be a fine-grained readout of the same freedom AXM measures.")
    verdict = "CONVERGENT_WITH_AXM"
else:
    print(f"  Atom freedom ({rel_genuine*100:.0f}%) is LESS than AXM (27%).")
    print(f"  Much of the 75% within-section variance may be noise or AXM-redundant.")
    verdict = "NOISE_DOMINATED"

print(f"\n  AXM-absorption diagnostic:")
print(f"    AXM captures {total_axm_absorbed:.1f}% of within-section PCA variance")
print(f"    This means {100 - total_axm_absorbed:.1f}% of atom variance is AXM-orthogonal")

# ─────────────────────────────────────────────
# Save results
# ─────────────────────────────────────────────
output = {
    'n_folios': len(common_folios),
    'n_features': n_features,
    'n_reliable_features': len(reliable_features),
    'n_unreliable_features': len(unreliable_features),

    'axm_proxy': {
        'method': 'MIDDLE_self_transition_rate',
        'mean': float(axm_series.mean()),
        'std': float(axm_series.std()),
        'min': float(axm_series.min()),
        'max': float(axm_series.max()),
        'per_folio': {f: float(v) for f, v in axm_series.items()}
    },

    'feature_axm_r2': {f: float(r2) for f, r2 in feature_r2.items()},
    'mean_feature_axm_r2': float(mean_r2),

    'pca_axm_absorption': {
        'total_axm_absorbed_pct': float(total_axm_absorbed),
        'pcs': pc_axm_r2[:15]
    },

    'icc': {f: {
        'icc': float(info['icc']) if not np.isnan(info.get('icc', float('nan'))) else None,
        'reliable': info.get('reliable', False)
    } for f, info in icc_results.items()},

    'reconciliation_per_feature': {f: {
        k: (float(v) if isinstance(v, (float, np.floating)) and not np.isnan(v) else v)
        for k, v in r.items()
    } for f, r in reconciliation.items()},

    'aggregate_reconciliation': {
        'all_features': {
            'section_determined': float(avg_section),
            'axm_captured_within': float(avg_axm_within),
            'measurement_noise': float(avg_noise),
            'genuine_freedom': float(avg_genuine)
        },
        'reliable_features_only': {
            'section_determined': float(rel_section),
            'axm_captured_within': float(rel_axm),
            'measurement_noise': float(rel_noise),
            'genuine_freedom': float(rel_genuine)
        }
    },

    'c1169_comparison': {
        'c1169_axm_freedom': c1169_freedom,
        'atom_genuine_freedom_all': float(avg_genuine),
        'atom_genuine_freedom_reliable': float(rel_genuine),
        'ratio_all': float(ratio_all),
        'ratio_reliable': float(ratio_rel),
        'verdict': verdict
    }
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bool):
            return bool(obj)
        return super().default(obj)

out_path = 'phases/FOLIO_DESIGN_FREEDOM/results/s5_75pct_reconciliation.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {out_path}")
print("\nDone.")
