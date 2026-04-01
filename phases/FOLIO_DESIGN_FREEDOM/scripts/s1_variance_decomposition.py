#!/usr/bin/env python3
"""
s1_variance_decomposition.py — FOLIO_DESIGN_FREEDOM Phase, Script 1

Establish the atom-level feature space for B folio differentiation.
Build folio-level atom feature matrix, decompose variance into
section-explained vs within-section, and run PCA on section-residualized
features to determine effective dimensionality.

Run from repo root:
    python phases/FOLIO_DESIGN_FREEDOM/scripts/s1_variance_decomposition.py
"""

import sys
import os
import json
import csv
from pathlib import Path
from collections import Counter, defaultdict

# Windows stdout encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure repo root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from scripts.voynich import Transcript, Morphology, HEAD_ATOMS

# ============================================================
# PATHS
# ============================================================
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'FOLIO_DESIGN_FREEDOM' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 0. Load and filter data
# ============================================================
print("=" * 70)
print("FOLIO_DESIGN_FREEDOM — S1: Variance Decomposition")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Build DataFrame from tokens
rows = []
for tok in tx.all(h_only=True):
    rows.append({
        'word': tok.word,
        'folio': tok.folio,
        'line': tok.line,
        'language': tok.language,
        'placement': tok.placement,
        'section': tok.section,
    })

df = pd.DataFrame(rows)

# Standard filters
df = df[~df['placement'].str.startswith('L')]
df = df[df['word'].str.strip() != '']
df = df[~df['word'].str.contains(r'\*', na=False)]
df_b = df[df['language'] == 'B'].copy()

print(f"B tokens after filtering: {len(df_b)}")
print(f"B folios: {df_b['folio'].nunique()}")

# ============================================================
# 1. Build folio-level atom feature matrix
# ============================================================
print("\n--- Building folio-level atom feature matrix ---")

# Define feature names
HEAD_CHARS = ['a', 'e', 'o', 'k', 't']
MOD_CHARS = ['p', 'f', 'i', 'c', 'd', 's']
TERM_CHARS = ['y', 'n', 'l', 'r', 'm', 'h']
PREFIX_CATS = ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'ct', 'bare']

FEATURE_NAMES = (
    [f'head_{c}' for c in HEAD_CHARS] + ['head_headless'] +
    [f'mod_{c}' for c in MOD_CHARS] +
    [f'term_{c}' for c in TERM_CHARS] +
    [f'pfx_{c}' for c in PREFIX_CATS] +
    ['e_depth_mean', 'i_depth_mean', 'mean_atom_length', 'token_count']
)

CORE_PREFIXES_SET = {'ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct'}

# Group tokens by folio
folio_tokens = defaultdict(list)
for _, row in df_b.iterrows():
    folio_tokens[row['folio']].append(row['word'])

# Pre-atomize all tokens per folio
folio_data = {}
for folio, words in folio_tokens.items():
    if len(words) < 50:
        continue

    heads = Counter()
    mods = Counter()
    terms = Counter()
    pfxs = Counter()
    e_depths = []
    i_depths = []
    atom_lengths = []
    n_tokens = len(words)
    headless_count = 0

    for w in words:
        a = morph.atomize(w)

        # HEAD classification
        head_char = a.head
        if head_char and head_char in HEAD_ATOMS:
            heads[head_char] += 1
        if a.is_headless:
            headless_count += 1

        # MOD counts
        for mc in a.mods:
            mods[mc] += 1

        # TERM classification
        t = a.term
        if t:
            terms[t] += 1

        # PREFIX classification
        if a.prefix:
            # Map to core prefix category
            matched = False
            for cp in CORE_PREFIXES_SET:
                if a.prefix == cp or a.prefix.endswith(cp):
                    pfxs[cp] += 1
                    matched = True
                    break
            if not matched:
                pfxs['bare'] += 1
        else:
            pfxs['bare'] += 1

        # Depths
        e_depths.append(a.e_depth)
        if a.i_depth > 0:
            i_depths.append(a.i_depth)

        # Atom length (number of atoms)
        atom_lengths.append(len(a.atoms))

    # Build feature vector
    fv = []
    # HEAD fractions
    for c in HEAD_CHARS:
        fv.append(heads[c] / n_tokens)
    fv.append(headless_count / n_tokens)

    # MOD fractions (per token, not per mod-slot)
    for c in MOD_CHARS:
        fv.append(mods[c] / n_tokens)

    # TERM fractions
    for c in TERM_CHARS:
        fv.append(terms[c] / n_tokens)

    # PREFIX fractions
    for c in PREFIX_CATS:
        fv.append(pfxs[c] / n_tokens)

    # Scalars
    fv.append(np.mean(e_depths) if e_depths else 0.0)
    fv.append(np.mean(i_depths) if i_depths else 0.0)
    fv.append(np.mean(atom_lengths) if atom_lengths else 0.0)
    fv.append(float(n_tokens))

    folio_data[folio] = fv

print(f"Folios with >= 50 tokens: {len(folio_data)}")
print(f"Features per folio: {len(FEATURE_NAMES)}")

# Create DataFrame
folios_sorted = sorted(folio_data.keys())
feature_matrix = pd.DataFrame(
    [folio_data[f] for f in folios_sorted],
    index=folios_sorted,
    columns=FEATURE_NAMES
)
feature_matrix.index.name = 'folio'

# ============================================================
# 2. Section assignment
# ============================================================
print("\n--- Section assignment ---")

# Get majority section per folio
folio_sections_raw = defaultdict(Counter)
for _, row in df_b.iterrows():
    folio_sections_raw[row['folio']][row['section']] += 1

SECTION_MAP = {
    'H': 'Herbal', 'HA': 'Herbal', 'HB': 'Herbal',
    'S': 'Stars',
    'P': 'Pharma',
    'B': 'Bio',
    'C': 'Cosmo',
    'T': 'Text',
}

folio_section = {}
for folio in folios_sorted:
    raw_counts = folio_sections_raw.get(folio, Counter())
    # Map to broad categories
    broad_counts = Counter()
    for s, c in raw_counts.items():
        broad = SECTION_MAP.get(s, s)
        broad_counts[broad] += c
    if broad_counts:
        folio_section[folio] = broad_counts.most_common(1)[0][0]
    else:
        folio_section[folio] = 'Unknown'

feature_matrix['section'] = [folio_section[f] for f in folios_sorted]

section_counts = Counter(folio_section[f] for f in folios_sorted)
for sec, cnt in sorted(section_counts.items()):
    print(f"  {sec}: {cnt} folios")

# ============================================================
# 3. Per-feature ANOVA
# ============================================================
print("\n--- Per-feature ANOVA (section as factor) ---")
print(f"{'Feature':<22} {'eta2':>8} {'within':>8} {'F':>10} {'p':>12}")
print("-" * 62)

anova_results = {}
sections_list = feature_matrix['section'].values
unique_sections = sorted(set(sections_list))

for feat in FEATURE_NAMES:
    vals = feature_matrix[feat].values
    groups = [vals[sections_list == s] for s in unique_sections if np.sum(sections_list == s) > 0]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 2:
        anova_results[feat] = {'eta2': 0.0, 'within': 1.0, 'F': 0.0, 'p': 1.0}
        continue

    f_stat, p_val = stats.f_oneway(*groups)

    # eta-squared
    grand_mean = np.mean(vals)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = np.sum((vals - grand_mean) ** 2)
    eta2 = ss_between / ss_total if ss_total > 0 else 0.0
    within = 1.0 - eta2

    anova_results[feat] = {
        'eta2': float(eta2),
        'within': float(within),
        'F': float(f_stat) if not np.isnan(f_stat) else 0.0,
        'p': float(p_val) if not np.isnan(p_val) else 1.0,
    }

# Sort by within-section fraction (descending = most freedom first)
sorted_feats = sorted(FEATURE_NAMES, key=lambda f: anova_results[f]['within'], reverse=True)

for feat in sorted_feats:
    r = anova_results[feat]
    print(f"{feat:<22} {r['eta2']:>8.3f} {r['within']:>8.3f} {r['F']:>10.2f} {r['p']:>12.4e}")

# Summary
high_freedom = [f for f in sorted_feats if anova_results[f]['within'] > 0.7]
constrained = [f for f in sorted_feats if anova_results[f]['within'] < 0.3]
print(f"\nHigh freedom channels (within > 0.7): {len(high_freedom)}")
for f in high_freedom:
    print(f"  {f} (within={anova_results[f]['within']:.3f})")
print(f"\nConstrained features (within < 0.3): {len(constrained)}")
for f in constrained:
    print(f"  {f} (within={anova_results[f]['within']:.3f})")

# ============================================================
# 4. Section residualization
# ============================================================
print("\n--- Section residualization ---")

residualized = feature_matrix[FEATURE_NAMES].copy()
section_means = {}
for sec in unique_sections:
    mask = sections_list == sec
    section_means[sec] = {feat: float(np.mean(feature_matrix.loc[mask, feat])) for feat in FEATURE_NAMES}
    for feat in FEATURE_NAMES:
        residualized.loc[mask, feat] = feature_matrix.loc[mask, feat] - section_means[sec][feat]

residualized.index = folios_sorted
residualized.index.name = 'folio'
print(f"Residualized matrix shape: {residualized.shape}")

# ============================================================
# 5. PCA on residualized features
# ============================================================
print("\n--- PCA on residualized (z-scored) features ---")

# Exclude token_count from PCA features (it's a scale variable, not a compositional feature)
pca_features = [f for f in FEATURE_NAMES if f != 'token_count']
X = residualized[pca_features].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA()
pca.fit(X_scaled)

cumvar = np.cumsum(pca.explained_variance_ratio_)
print(f"\n{'PC':<6} {'Var%':>8} {'Cumul%':>8}")
print("-" * 24)
for i, (v, c) in enumerate(zip(pca.explained_variance_ratio_, cumvar)):
    print(f"PC{i+1:<4} {v*100:>7.2f}% {c*100:>7.2f}%")
    if c > 0.99:
        break

# Dimensionality thresholds
for threshold in [0.80, 0.90, 0.95]:
    n_pcs = int(np.searchsorted(cumvar, threshold)) + 1
    print(f"  PCs for {threshold*100:.0f}% variance: {n_pcs}")

# Top 5 PC loadings
print("\n--- Top 5 PC loadings ---")
for pc_idx in range(min(5, len(pca.components_))):
    loadings = pca.components_[pc_idx]
    abs_loadings = np.abs(loadings)
    top_idx = np.argsort(abs_loadings)[::-1][:7]
    print(f"\nPC{pc_idx+1} ({pca.explained_variance_ratio_[pc_idx]*100:.1f}% var):")
    for idx in top_idx:
        print(f"  {pca_features[idx]:<22} {loadings[idx]:>+.3f}")

# ============================================================
# 6. Compare to C1715
# ============================================================
print("\n--- Comparison to C1715 ---")
n_pcs_95 = int(np.searchsorted(cumvar, 0.95)) + 1
print(f"C1715 used 22 aggregate features, found 12 PCs at 95%.")
print(f"This analysis: {len(pca_features)} atom features, {n_pcs_95} PCs at 95%.")
ratio_c1715 = 12 / 22
ratio_ours = n_pcs_95 / len(pca_features)
print(f"Dimensionality ratio: C1715={ratio_c1715:.2f}, ours={ratio_ours:.2f}")

# ============================================================
# 7. Folio positions on PC1 vs PC2
# ============================================================
print("\n--- Folio positions on PC1 vs PC2 ---")

X_pca = pca.transform(X_scaled)

print(f"{'Folio':<10} {'Section':<10} {'PC1':>8} {'PC2':>8}")
print("-" * 38)
for i, folio in enumerate(folios_sorted):
    sec = folio_section[folio]
    print(f"{folio:<10} {sec:<10} {X_pca[i, 0]:>8.3f} {X_pca[i, 1]:>8.3f}")

# Within-section spread analysis
print("\n--- Within-section spread (std of PC1, PC2) ---")
print(f"{'Section':<10} {'N':>4} {'PC1_std':>10} {'PC2_std':>10} {'PC1_range':>10} {'PC2_range':>10}")
print("-" * 56)
for sec in sorted(unique_sections):
    mask = np.array([folio_section[f] == sec for f in folios_sorted])
    if mask.sum() < 2:
        continue
    pc1 = X_pca[mask, 0]
    pc2 = X_pca[mask, 1]
    print(f"{sec:<10} {mask.sum():>4} {np.std(pc1):>10.3f} {np.std(pc2):>10.3f} "
          f"{np.ptp(pc1):>10.3f} {np.ptp(pc2):>10.3f}")

# ============================================================
# 8. Save outputs
# ============================================================
print("\n--- Saving outputs ---")

# CSV: folio feature matrix
csv_path = RESULTS_DIR / 's1_folio_atom_features.csv'
feature_matrix.to_csv(csv_path)
print(f"Saved: {csv_path}")

# CSV: residualized matrix (add section column for reference)
resid_out = residualized.copy()
resid_out['section'] = [folio_section[f] for f in folios_sorted]
csv_resid_path = RESULTS_DIR / 's1_folio_atom_features_residualized.csv'
resid_out.to_csv(csv_resid_path)
print(f"Saved: {csv_resid_path}")

# JSON results
results = {
    'n_folios': len(folios_sorted),
    'n_features': len(FEATURE_NAMES),
    'n_pca_features': len(pca_features),
    'min_tokens_threshold': 50,
    'section_counts': dict(section_counts),
    'anova': {feat: anova_results[feat] for feat in sorted_feats},
    'high_freedom_features': high_freedom,
    'constrained_features': constrained,
    'pca': {
        'n_components': len(pca.explained_variance_ratio_),
        'variance_explained': [float(v) for v in pca.explained_variance_ratio_],
        'cumulative_variance': [float(c) for c in cumvar],
        'pcs_for_80pct': int(np.searchsorted(cumvar, 0.80)) + 1,
        'pcs_for_90pct': int(np.searchsorted(cumvar, 0.90)) + 1,
        'pcs_for_95pct': n_pcs_95,
        'top5_loadings': {},
    },
    'c1715_comparison': {
        'c1715_features': 22,
        'c1715_pcs_95': 12,
        'our_features': len(pca_features),
        'our_pcs_95': n_pcs_95,
    },
    'folio_pc_positions': {
        folio: {
            'section': folio_section[folio],
            'PC1': float(X_pca[i, 0]),
            'PC2': float(X_pca[i, 1]),
        }
        for i, folio in enumerate(folios_sorted)
    },
}

# Add top 5 PC loadings to JSON
for pc_idx in range(min(5, len(pca.components_))):
    loadings = pca.components_[pc_idx]
    abs_loadings = np.abs(loadings)
    top_idx = np.argsort(abs_loadings)[::-1][:7]
    results['pca']['top5_loadings'][f'PC{pc_idx+1}'] = {
        'variance_pct': float(pca.explained_variance_ratio_[pc_idx] * 100),
        'top_features': {pca_features[idx]: float(loadings[idx]) for idx in top_idx},
    }

json_path = RESULTS_DIR / 's1_variance_decomposition.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print(f"Saved: {json_path}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
