#!/usr/bin/env python3
"""
S2: Cluster Currier A folios by atom-level profiles.

Uses hierarchical clustering on per-folio atom distributions (HEAD, MOD, TERM,
e_depth, token length, diagnostic ratios) to find natural groupings among A folios.
Tests whether clusters correspond to Voynich manuscript sections.
"""

import sys
import os
import json
import numpy as np
from collections import defaultdict, Counter

# Windows encoding fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Run from repo root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
os.chdir(repo_root)
sys.path.insert(0, repo_root)

from scripts.voynich import Transcript, Morphology
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.stats import chi2_contingency
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ─── Configuration ────────────────────────────────────────────────
MIN_TOKENS = 20
HEAD_CATS = ['headless', 'o', 'e', 'a', 'k', 't']
MOD_CATS = ['p', 'f', 'i', 'c', 'd', 's']
TERM_CATS = ['y', 'n', 'l', 'r', 'm', 'h']

SECTION_MAP = {
    'H': 'Herbal', 'HA': 'Herbal', 'HB': 'Herbal',
    'P': 'Pharma', 'PA': 'Pharma', 'PB': 'Pharma',
    'T': 'Text', 'TA': 'Text', 'TB': 'Text',
    'S': 'Stars', 'SA': 'Stars', 'SB': 'Stars',
    'C': 'Cosmo', 'Z': 'Zodiac', 'A': 'Astro',
}

# ─── Data collection ──────────────────────────────────────────────
tx = Transcript()
morph = Morphology()

# Per-folio raw data
folio_data = defaultdict(lambda: {
    'head_counts': Counter(),
    'mod_counts': Counter(),
    'term_counts': Counter(),
    'e_depths': [],
    'atom_lengths': [],
    'token_count': 0,
    'section': None,
})

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if token.placement and token.placement.startswith('L'):
        continue

    fol = token.folio
    fd = folio_data[fol]
    if fd['section'] is None:
        sec = token.section if token.section else ''
        fd['section'] = SECTION_MAP.get(sec, sec if sec else 'Unknown')

    a = morph.atomize(w)
    if not a.atoms:
        continue

    fd['token_count'] += 1

    # HEAD
    head_char = a.head
    if head_char is None:
        fd['head_counts']['headless'] += 1
    else:
        fd['head_counts'][head_char] += 1

    # MOD atoms
    for char, role, _ in a.atoms:
        if role == 'MOD':
            fd['mod_counts'][char] += 1

    # TERM
    term_char = a.term
    if term_char:
        fd['term_counts'][term_char] += 1

    fd['e_depths'].append(a.e_depth)
    fd['atom_lengths'].append(len(a.atoms))

# ─── Build feature matrix ────────────────────────────────────────
folios_sorted = sorted([f for f, d in folio_data.items() if d['token_count'] >= MIN_TOKENS])
print(f"Folios with >= {MIN_TOKENS} tokens: {len(folios_sorted)}")
print(f"Excluded: {sorted([f for f, d in folio_data.items() if d['token_count'] < MIN_TOKENS])}\n")

feature_names = []
feature_names += [f'HEAD_{c}' for c in HEAD_CATS]
feature_names += [f'MOD_{c}' for c in MOD_CATS]
feature_names += [f'TERM_{c}' for c in TERM_CATS]
feature_names += ['e_depth_mean', 'atom_len_mean', 'o_oe_ratio', 'l_ly_ratio']

n_features = len(feature_names)
X_raw = np.zeros((len(folios_sorted), n_features))
folio_meta = []  # (folio, section, token_count)

for i, fol in enumerate(folios_sorted):
    fd = folio_data[fol]
    tc = fd['token_count']
    folio_meta.append((fol, fd['section'], tc))

    col = 0
    # HEAD distribution (% of tokens)
    head_total = sum(fd['head_counts'].values())
    for c in HEAD_CATS:
        X_raw[i, col] = (fd['head_counts'].get(c, 0) / head_total * 100) if head_total > 0 else 0
        col += 1

    # MOD distribution (% of canonical MOD total)
    mod_canonical_total = sum(fd['mod_counts'].get(c, 0) for c in MOD_CATS)
    for c in MOD_CATS:
        X_raw[i, col] = (fd['mod_counts'].get(c, 0) / mod_canonical_total * 100) if mod_canonical_total > 0 else 0
        col += 1

    # TERM distribution (% of tokens with a TERM)
    term_total = sum(fd['term_counts'].values())
    for c in TERM_CATS:
        X_raw[i, col] = (fd['term_counts'].get(c, 0) / term_total * 100) if term_total > 0 else 0
        col += 1

    # Continuous features
    X_raw[i, col] = np.mean(fd['e_depths']) if fd['e_depths'] else 0; col += 1
    X_raw[i, col] = np.mean(fd['atom_lengths']) if fd['atom_lengths'] else 0; col += 1

    # o/(o+e) ratio
    o_count = fd['head_counts'].get('o', 0)
    e_count = fd['head_counts'].get('e', 0)
    X_raw[i, col] = o_count / (o_count + e_count) if (o_count + e_count) > 0 else 0.5; col += 1

    # l/(l+y) ratio
    l_count = fd['term_counts'].get('l', 0)
    y_count = fd['term_counts'].get('y', 0)
    X_raw[i, col] = l_count / (l_count + y_count) if (l_count + y_count) > 0 else 0.5; col += 1

# ─── Normalize ────────────────────────────────────────────────────
scaler = StandardScaler()
X = scaler.fit_transform(X_raw)

# ─── Hierarchical clustering ─────────────────────────────────────
Z = linkage(X, method='ward')

print("=" * 70)
print("HIERARCHICAL CLUSTERING RESULTS")
print("=" * 70)

cluster_assignments = {}
for k in [3, 4, 5]:
    labels = fcluster(Z, t=k, criterion='maxclust')
    cluster_assignments[k] = labels
    print(f"\n--- k={k} clusters ---")
    for c in range(1, k + 1):
        members = [folios_sorted[j] for j in range(len(folios_sorted)) if labels[j] == c]
        print(f"  Cluster {c} ({len(members)} folios): {', '.join(members)}")

# ─── Cluster characterization at k=4 ─────────────────────────────
print("\n" + "=" * 70)
print("CLUSTER CHARACTERIZATION (k=4)")
print("=" * 70)

labels_4 = cluster_assignments[4]
cluster_chars = {}

for c in range(1, 5):
    idx = [j for j in range(len(folios_sorted)) if labels_4[j] == c]
    members = [folios_sorted[j] for j in idx]
    sections = [folio_meta[j][1] for j in idx]
    token_counts = [folio_meta[j][2] for j in idx]
    X_sub = X_raw[idx]

    # Mean HEAD profile
    head_profile = {}
    for hi, hc in enumerate(HEAD_CATS):
        head_profile[hc] = float(np.mean(X_sub[:, hi]))

    mean_e_depth = float(np.mean(X_sub[:, len(HEAD_CATS) + len(MOD_CATS) + len(TERM_CATS)]))
    mean_o_oe = float(np.mean(X_sub[:, -2]))
    mean_l_ly = float(np.mean(X_sub[:, -1]))

    sec_dist = Counter(sections)

    char_info = {
        'folios': members,
        'n_folios': len(members),
        'total_tokens': sum(token_counts),
        'mean_head_profile': head_profile,
        'mean_e_depth': round(mean_e_depth, 3),
        'mean_o_oe_ratio': round(mean_o_oe, 3),
        'mean_l_ly_ratio': round(mean_l_ly, 3),
        'section_distribution': dict(sec_dist),
    }
    cluster_chars[c] = char_info

    print(f"\n--- Cluster {c} ---")
    print(f"  Folios ({len(members)}): {', '.join(members)}")
    print(f"  Total tokens: {sum(token_counts)}")
    print(f"  HEAD profile: " + ", ".join(f"{k2}={v:.1f}%" for k2, v in head_profile.items()))
    print(f"  Mean e_depth: {mean_e_depth:.3f}")
    print(f"  Mean o/(o+e): {mean_o_oe:.3f}")
    print(f"  Mean l/(l+y): {mean_l_ly:.3f}")
    print(f"  Sections: {dict(sec_dist)}")

# ─── Section association (chi-squared) ────────────────────────────
print("\n" + "=" * 70)
print("SECTION ASSOCIATION (Chi-squared test)")
print("=" * 70)

sections_list = [folio_meta[j][1] for j in range(len(folios_sorted))]
unique_sections = sorted(set(sections_list))
contingency = np.zeros((4, len(unique_sections)), dtype=int)
for j in range(len(folios_sorted)):
    cl = labels_4[j] - 1
    si = unique_sections.index(folio_meta[j][1])
    contingency[cl, si] += 1

print(f"\nContingency table (clusters x sections):")
print(f"  {'':>10s} " + " ".join(f"{s:>8s}" for s in unique_sections))
for c in range(4):
    print(f"  Cluster {c+1:>2d} " + " ".join(f"{contingency[c,s]:>8d}" for s in range(len(unique_sections))))

# Chi-squared — need to handle sparse table
# Remove columns with all zeros
nonzero_cols = [j for j in range(contingency.shape[1]) if contingency[:, j].sum() > 0]
ct_filtered = contingency[:, nonzero_cols]
secs_filtered = [unique_sections[j] for j in nonzero_cols]

if ct_filtered.shape[1] >= 2:
    chi2, p, dof, expected = chi2_contingency(ct_filtered)
    print(f"\nChi-squared = {chi2:.2f}, dof = {dof}, p = {p:.4e}")
    if p < 0.05:
        print("  => Clusters ARE significantly associated with Voynich sections.")
    else:
        print("  => No significant association between clusters and sections.")
else:
    chi2, p, dof = None, None, None
    print("\n  Not enough section diversity for chi-squared test.")

# ─── PCA ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PCA ANALYSIS")
print("=" * 70)

pca = PCA(n_components=min(5, X.shape[1]))
X_pca = pca.fit_transform(X)

print(f"\nVariance explained: " + ", ".join(f"PC{i+1}={v:.1%}" for i, v in enumerate(pca.explained_variance_ratio_[:5])))
print(f"Cumulative: " + ", ".join(f"{sum(pca.explained_variance_ratio_[:i+1]):.1%}" for i in range(min(5, len(pca.explained_variance_ratio_)))))

# PC1/PC2 loadings
print(f"\nPC1 loadings (top 8):")
pc1_load = list(zip(feature_names, pca.components_[0]))
pc1_load.sort(key=lambda x: abs(x[1]), reverse=True)
for name, val in pc1_load[:8]:
    print(f"  {name:>20s}: {val:+.3f}")

print(f"\nPC2 loadings (top 8):")
pc2_load = list(zip(feature_names, pca.components_[1]))
pc2_load.sort(key=lambda x: abs(x[1]), reverse=True)
for name, val in pc2_load[:8]:
    print(f"  {name:>20s}: {val:+.3f}")

print(f"\nFolio positions (PC1, PC2) with cluster assignment (k=4):")
print(f"  {'Folio':>8s} {'PC1':>8s} {'PC2':>8s} {'Cl':>3s} {'Section':>10s}")
for i, fol in enumerate(folios_sorted):
    print(f"  {fol:>8s} {X_pca[i,0]:>8.3f} {X_pca[i,1]:>8.3f} {labels_4[i]:>3d} {folio_meta[i][1]:>10s}")

# ─── Key discriminating features ─────────────────────────────────
print("\n" + "=" * 70)
print("TOP DISCRIMINATING FEATURES (between-cluster variance)")
print("=" * 70)

# Between-cluster variance for each feature (on z-scored data)
between_var = []
overall_mean = X.mean(axis=0)
for fi in range(n_features):
    bv = 0
    for c in range(1, 5):
        idx = [j for j in range(len(folios_sorted)) if labels_4[j] == c]
        cluster_mean = X[idx, fi].mean()
        bv += len(idx) * (cluster_mean - overall_mean[fi]) ** 2
    bv /= len(folios_sorted)
    between_var.append((feature_names[fi], bv))

between_var.sort(key=lambda x: x[1], reverse=True)
print("\nTop 10 features by between-cluster variance:")
for name, bv in between_var[:10]:
    print(f"  {name:>20s}: {bv:.4f}")

# ─── Save JSON ────────────────────────────────────────────────────
output = {
    'description': 'Currier A folio clustering by atom-level profiles',
    'min_tokens': MIN_TOKENS,
    'n_folios': len(folios_sorted),
    'n_features': n_features,
    'feature_names': feature_names,
    'folios': folios_sorted,
    'folio_sections': {fol: folio_meta[i][1] for i, fol in enumerate(folios_sorted)},
    'folio_token_counts': {fol: folio_meta[i][2] for i, fol in enumerate(folios_sorted)},
    'cluster_assignments': {
        str(k): {folios_sorted[j]: int(labels[j]) for j in range(len(folios_sorted))}
        for k, labels in cluster_assignments.items()
    },
    'cluster_characterization_k4': {
        str(c): {
            'folios': info['folios'],
            'n_folios': info['n_folios'],
            'total_tokens': info['total_tokens'],
            'mean_head_profile': {k2: round(v, 2) for k2, v in info['mean_head_profile'].items()},
            'mean_e_depth': info['mean_e_depth'],
            'mean_o_oe_ratio': info['mean_o_oe_ratio'],
            'mean_l_ly_ratio': info['mean_l_ly_ratio'],
            'section_distribution': info['section_distribution'],
        }
        for c, info in cluster_chars.items()
    },
    'chi_squared': {
        'chi2': round(chi2, 2) if chi2 is not None else None,
        'p_value': float(p) if p is not None else None,
        'dof': int(dof) if dof is not None else None,
        'significant': bool(p < 0.05) if p is not None else None,
    },
    'pca': {
        'variance_explained': [round(float(v), 4) for v in pca.explained_variance_ratio_[:5]],
        'pc1_top_loadings': {name: round(float(val), 4) for name, val in pc1_load[:8]},
        'pc2_top_loadings': {name: round(float(val), 4) for name, val in pc2_load[:8]},
        'folio_positions': {
            fol: {'PC1': round(float(X_pca[i, 0]), 3), 'PC2': round(float(X_pca[i, 1]), 3)}
            for i, fol in enumerate(folios_sorted)
        },
    },
    'top_discriminating_features': [
        {'feature': name, 'between_cluster_variance': round(bv, 4)}
        for name, bv in between_var[:10]
    ],
}

out_path = 'phases/CURRIER_A_ATOMS/results/s2_a_folio_clustering.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to {out_path}")
print("Done.")
