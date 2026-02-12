#!/usr/bin/env python3
"""
B_FOLIO_TEMPORAL_PROFILE - Script 1: Folio Temporal Metrics

Constructs per-line feature matrix for all B folios and measures
within-folio temporal evolution of role composition, LINK density,
and kernel contact.

Tests:
  1. Role Profile Trajectory (EN/FL/FQ/AX/CC fractions by quartile)
  2. LINK Density Trajectory (LINK token fraction by quartile)
  3. Kernel Contact Trajectory (k/h/e kernel rates by quartile)
  + Trajectory Shape Clustering across folios

Constraint references:
  C556: ENERGY medial concentration (line-level positional grammar)
  C548: Gateway front-loading (rho=-0.368, manuscript-level)
  C557: daiin line-opener function
  C609: LINK density 13.2%
  C121: 49 instruction classes, 100% coverage

Dependencies:
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json
  - phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json
  - scripts/voynich.py (Transcript)

Output: results/folio_temporal_metrics.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

# Role mapping (class -> role) per BCSC v1.2
# C560/C581: class 17 = CC (not AX)
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
# All remaining classes -> AX
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']


def is_link(word):
    """LINK detection: C609 canonical definition."""
    return 'ol' in word if word else False


def get_kernel_class(word):
    """Kernel operator detection (BCSC kernel_roles)."""
    if not word:
        return None
    if word.endswith('k') or word in ('ok', 'yk', 'ak', 'ek'):
        return 'k'
    if word.endswith('h') or word in ('oh', 'yh', 'ah', 'eh'):
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy'):
        return 'e'
    return None


def line_sort_key(line_str):
    """Sort line numbers numerically, handle alphanumeric (e.g., '1a')."""
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)


print("=" * 70)
print("B_FOLIO_TEMPORAL_PROFILE - Script 1: Folio Temporal Metrics")
print("=" * 70)

# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================
print("\n--- Section 1: Load & Prepare ---")

# Load class token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)

if 'token_to_class' in ctm_raw:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
else:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw.items()}

print(f"  Loaded class_token_map: {len(token_to_class)} tokens mapped")

# Load regime mapping (authoritative v2, GMM k=4)
regime_path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

folio_to_regime = {folio: data['regime'] for folio, data in regime_data['regime_assignments'].items()}

print(f"  Loaded regime mapping: {len(folio_to_regime)} folios (v2 authoritative)")

# Build per-folio, per-line token data
tx = Transcript()

folio_lines = defaultdict(lambda: defaultdict(list))
total_b_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    total_b_tokens += 1

    cls = token_to_class.get(token.word)
    role = CLASS_TO_ROLE.get(cls, 'UNCLASSIFIED') if cls is not None else 'UNCLASSIFIED'
    kernel = get_kernel_class(token.word)
    link = is_link(token.word)

    folio_lines[token.folio][token.line].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'kernel': kernel,
        'is_link': link,
    })

n_folios = len(folio_lines)
n_lines_total = sum(len(lines) for lines in folio_lines.values())
print(f"  Total B tokens (filtered): {total_b_tokens}")
print(f"  Folios: {n_folios}")
print(f"  Total lines: {n_lines_total}")

# ============================================================
# SECTION 2: PER-LINE FEATURE MATRIX
# ============================================================
print("\n--- Section 2: Per-Line Feature Matrix ---")

line_features = []  # list of dicts

for folio in sorted(folio_lines.keys()):
    lines_sorted = sorted(folio_lines[folio].keys(), key=line_sort_key)
    n_lines = len(lines_sorted)
    if n_lines == 0:
        continue

    for idx, line_num in enumerate(lines_sorted):
        tokens = folio_lines[folio][line_num]
        n_tok = len(tokens)
        if n_tok == 0:
            continue

        # Normalized position [0, 1]
        norm_pos = idx / max(n_lines - 1, 1)
        quartile = min(int(norm_pos * 4) + 1, 4)

        # Role fractions
        role_counts = Counter(t['role'] for t in tokens)
        role_fracs = {r: role_counts.get(r, 0) / n_tok for r in ROLES + ['UNCLASSIFIED']}

        # LINK density
        link_count = sum(1 for t in tokens if t['is_link'])
        link_density = link_count / n_tok

        # Kernel fractions
        kernel_counts = Counter(t['kernel'] for t in tokens)
        kernel_fracs = {
            'k': kernel_counts.get('k', 0) / n_tok,
            'h': kernel_counts.get('h', 0) / n_tok,
            'e': kernel_counts.get('e', 0) / n_tok,
            'none': kernel_counts.get(None, 0) / n_tok,
        }

        line_features.append({
            'folio': folio,
            'line': line_num,
            'n_tokens': n_tok,
            'norm_pos': norm_pos,
            'quartile': quartile,
            'role_fracs': role_fracs,
            'link_density': link_density,
            'kernel_fracs': kernel_fracs,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
        })

print(f"  Line features computed: {len(line_features)} lines")

# Verify quartile distribution
q_counts = Counter(f['quartile'] for f in line_features)
for q in range(1, 5):
    print(f"    Q{q}: {q_counts.get(q, 0)} lines")

# ============================================================
# SECTION 3: TEST 1 - ROLE PROFILE TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: Role Profile Trajectory")
print("=" * 70)

from scipy.stats import spearmanr, kruskal

# Corpus-wide trajectory
positions = np.array([f['norm_pos'] for f in line_features])

test1_results = {
    'corpus_wide': {
        'spearman': {},
        'kruskal_wallis': {},
        'quartile_means': {f'Q{q}': {} for q in range(1, 5)},
    },
    'regime_stratified': {},
    'regime_kw_on_slope': {},
}

# Aggregate by quartile for each role
quartile_role_data = {q: {r: [] for r in ROLES + ['UNCLASSIFIED']} for q in range(1, 5)}
for f in line_features:
    q = f['quartile']
    for r in ROLES + ['UNCLASSIFIED']:
        quartile_role_data[q][r].append(f['role_fracs'][r])

print("\nCorpus-wide role trajectories:")
print(f"  {'Role':<15} {'Q1':>8} {'Q2':>8} {'Q3':>8} {'Q4':>8} {'rho':>8} {'p':>10} {'KW_H':>8} {'KW_p':>10}")
print("  " + "-" * 85)

for role in ROLES + ['UNCLASSIFIED']:
    # Spearman
    fracs = np.array([f['role_fracs'][role] for f in line_features])
    rho, p_sp = spearmanr(positions, fracs)

    # KW
    groups = [quartile_role_data[q][role] for q in range(1, 5)]
    if all(len(g) > 0 for g in groups):
        kw_h, kw_p = kruskal(*groups)
    else:
        kw_h, kw_p = 0.0, 1.0

    # Quartile means
    q_means = {q: float(np.mean(quartile_role_data[q][role])) for q in range(1, 5)}

    test1_results['corpus_wide']['spearman'][role] = {'rho': round(rho, 4), 'p': float(p_sp)}
    test1_results['corpus_wide']['kruskal_wallis'][role] = {'H': round(kw_h, 2), 'p': float(kw_p)}
    for q in range(1, 5):
        test1_results['corpus_wide']['quartile_means'][f'Q{q}'][role] = round(q_means[q], 4)

    sig = '*' if kw_p < 0.05 else ' '
    print(f"  {role:<15} {q_means[1]:>8.4f} {q_means[2]:>8.4f} {q_means[3]:>8.4f} {q_means[4]:>8.4f} {rho:>8.4f} {p_sp:>10.2e} {kw_h:>8.2f} {kw_p:>10.2e} {sig}")

# Regime stratification
print("\nRegime-stratified trajectories:")
regimes = sorted(set(f['regime'] for f in line_features if f['regime'] != 'UNKNOWN'))

# Per-folio slopes for regime comparison
folio_slopes = defaultdict(dict)  # folio -> {role: Q4-Q1 slope}

for folio in sorted(folio_lines.keys()):
    folio_feats = [f for f in line_features if f['folio'] == folio]
    if not folio_feats:
        continue
    for role in ROLES:
        q1_vals = [f['role_fracs'][role] for f in folio_feats if f['quartile'] == 1]
        q4_vals = [f['role_fracs'][role] for f in folio_feats if f['quartile'] == 4]
        if q1_vals and q4_vals:
            folio_slopes[folio][role] = float(np.mean(q4_vals) - np.mean(q1_vals))

for regime in regimes:
    regime_feats = [f for f in line_features if f['regime'] == regime]
    regime_q_data = {q: {r: [] for r in ROLES} for q in range(1, 5)}
    for f in regime_feats:
        for r in ROLES:
            regime_q_data[f['quartile']][r].append(f['role_fracs'][r])

    test1_results['regime_stratified'][regime] = {
        'n_lines': len(regime_feats),
        'quartile_means': {},
    }
    for q in range(1, 5):
        test1_results['regime_stratified'][regime]['quartile_means'][f'Q{q}'] = {
            r: round(float(np.mean(regime_q_data[q][r])), 4) if regime_q_data[q][r] else 0
            for r in ROLES
        }

    print(f"\n  {regime} (n={len(regime_feats)} lines):")
    for role in ROLES:
        q_vals = [float(np.mean(regime_q_data[q][role])) if regime_q_data[q][role] else 0 for q in range(1, 5)]
        slope = q_vals[3] - q_vals[0]
        print(f"    {role:<10} Q1={q_vals[0]:.4f}  Q4={q_vals[3]:.4f}  slope={slope:+.4f}")

# KW on slopes across regimes
print("\nRegime KW on Q4-Q1 slopes:")
for role in ROLES:
    regime_slope_groups = []
    for regime in regimes:
        regime_folios = [fol for fol in folio_slopes if folio_to_regime.get(fol) == regime]
        slopes = [folio_slopes[fol][role] for fol in regime_folios if role in folio_slopes[fol]]
        regime_slope_groups.append(slopes)

    if all(len(g) >= 2 for g in regime_slope_groups):
        kw_h, kw_p = kruskal(*regime_slope_groups)
        test1_results['regime_kw_on_slope'][role] = {'H': round(kw_h, 2), 'p': float(kw_p)}
        sig = '*' if kw_p < 0.05 else ' '
        print(f"  {role:<10} H={kw_h:.2f}  p={kw_p:.2e} {sig}")
    else:
        test1_results['regime_kw_on_slope'][role] = {'H': 0, 'p': 1.0}
        print(f"  {role:<10} insufficient data")

# ============================================================
# SECTION 4: TEST 2 - LINK DENSITY TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: LINK Density Trajectory")
print("=" * 70)

link_vals = np.array([f['link_density'] for f in line_features])
rho_link, p_link = spearmanr(positions, link_vals)

link_by_q = {q: [] for q in range(1, 5)}
for f in line_features:
    link_by_q[f['quartile']].append(f['link_density'])

link_q_means = {q: float(np.mean(link_by_q[q])) for q in range(1, 5)}
kw_link_h, kw_link_p = kruskal(*[link_by_q[q] for q in range(1, 5)])

test2_results = {
    'spearman': {'rho': round(rho_link, 4), 'p': float(p_link)},
    'kruskal_wallis': {'H': round(kw_link_h, 2), 'p': float(kw_link_p)},
    'quartile_means': {f'Q{q}': round(link_q_means[q], 4) for q in range(1, 5)},
    'regime_stratified': {},
}

sig = '*' if kw_link_p < 0.05 else ''
print(f"\n  Spearman rho = {rho_link:.4f}, p = {p_link:.2e}")
print(f"  KW H = {kw_link_h:.2f}, p = {kw_link_p:.2e} {sig}")
print(f"  Q1={link_q_means[1]:.4f}  Q2={link_q_means[2]:.4f}  Q3={link_q_means[3]:.4f}  Q4={link_q_means[4]:.4f}")
print(f"  Slope (Q4-Q1): {link_q_means[4] - link_q_means[1]:+.4f}")

# Regime stratification
print("\n  Regime stratification:")
for regime in regimes:
    regime_feats = [f for f in line_features if f['regime'] == regime]
    rq = {q: [] for q in range(1, 5)}
    for f in regime_feats:
        rq[f['quartile']].append(f['link_density'])
    rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
    slope = rq_means[4] - rq_means[1]
    test2_results['regime_stratified'][regime] = {
        'quartile_means': {f'Q{q}': round(rq_means[q], 4) for q in range(1, 5)},
        'slope': round(slope, 4),
    }
    print(f"    {regime}: Q1={rq_means[1]:.4f} Q4={rq_means[4]:.4f} slope={slope:+.4f}")

# ============================================================
# SECTION 5: TEST 3 - KERNEL CONTACT TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: Kernel Contact Trajectory")
print("=" * 70)

test3_results = {}

for ktype in ['k', 'h', 'e']:
    kern_vals = np.array([f['kernel_fracs'][ktype] for f in line_features])
    rho_k, p_k = spearmanr(positions, kern_vals)

    kern_by_q = {q: [] for q in range(1, 5)}
    for f in line_features:
        kern_by_q[f['quartile']].append(f['kernel_fracs'][ktype])

    kern_q_means = {q: float(np.mean(kern_by_q[q])) for q in range(1, 5)}
    kw_k_h, kw_k_p = kruskal(*[kern_by_q[q] for q in range(1, 5)])

    test3_results[ktype] = {
        'spearman': {'rho': round(rho_k, 4), 'p': float(p_k)},
        'kruskal_wallis': {'H': round(kw_k_h, 2), 'p': float(kw_k_p)},
        'quartile_means': {f'Q{q}': round(kern_q_means[q], 4) for q in range(1, 5)},
        'regime_stratified': {},
    }

    sig = '*' if kw_k_p < 0.05 else ''
    print(f"\n  Kernel '{ktype}': rho={rho_k:.4f}, p={p_k:.2e}  KW H={kw_k_h:.2f}, p={kw_k_p:.2e} {sig}")
    print(f"    Q1={kern_q_means[1]:.4f}  Q2={kern_q_means[2]:.4f}  Q3={kern_q_means[3]:.4f}  Q4={kern_q_means[4]:.4f}")
    print(f"    Slope: {kern_q_means[4] - kern_q_means[1]:+.4f}")

    # Regime stratification
    for regime in regimes:
        regime_feats = [f for f in line_features if f['regime'] == regime]
        rq = {q: [] for q in range(1, 5)}
        for f in regime_feats:
            rq[f['quartile']].append(f['kernel_fracs'][ktype])
        rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
        slope = rq_means[4] - rq_means[1]
        test3_results[ktype]['regime_stratified'][regime] = {
            'quartile_means': {f'Q{q}': round(rq_means[q], 4) for q in range(1, 5)},
            'slope': round(slope, 4),
        }

# k/e ratio trajectory
print("\n  k/e ratio trajectory:")
ke_by_q = {q: [] for q in range(1, 5)}
for f in line_features:
    k_frac = f['kernel_fracs']['k']
    e_frac = f['kernel_fracs']['e']
    if k_frac + e_frac > 0:
        ke_ratio = k_frac / (k_frac + e_frac)
    else:
        ke_ratio = 0.5  # no kernel contact
    ke_by_q[f['quartile']].append(ke_ratio)

ke_all = []
ke_pos = []
for f in line_features:
    k_frac = f['kernel_fracs']['k']
    e_frac = f['kernel_fracs']['e']
    if k_frac + e_frac > 0:
        ke_all.append(k_frac / (k_frac + e_frac))
        ke_pos.append(f['norm_pos'])

if len(ke_all) > 10:
    rho_ke, p_ke = spearmanr(ke_pos, ke_all)
    ke_q_means = {q: float(np.mean(ke_by_q[q])) for q in range(1, 5)}
    test3_results['ke_ratio'] = {
        'spearman': {'rho': round(rho_ke, 4), 'p': float(p_ke)},
        'quartile_means': {f'Q{q}': round(ke_q_means[q], 4) for q in range(1, 5)},
        'n_lines_with_kernel': len(ke_all),
    }
    print(f"  k/(k+e) ratio: rho={rho_ke:.4f}, p={p_ke:.2e}")
    print(f"    Q1={ke_q_means[1]:.4f}  Q2={ke_q_means[2]:.4f}  Q3={ke_q_means[3]:.4f}  Q4={ke_q_means[4]:.4f}")
    print(f"    Slope: {ke_q_means[4] - ke_q_means[1]:+.4f}")
else:
    test3_results['ke_ratio'] = {'note': 'insufficient data'}
    print("  k/e ratio: insufficient data")

# ============================================================
# SECTION 6: TRAJECTORY SHAPE CLUSTERING
# ============================================================
print("\n" + "=" * 70)
print("TRAJECTORY SHAPE CLUSTERING")
print("=" * 70)

from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# Build per-folio trajectory vectors
folio_traj_data = {}

for folio in sorted(folio_lines.keys()):
    folio_feats = [f for f in line_features if f['folio'] == folio]
    if not folio_feats:
        continue

    # Check: does this folio have lines in all 4 quartiles?
    folio_qs = set(f['quartile'] for f in folio_feats)
    if len(folio_qs) < 4:
        continue

    n_folio_lines = len(folio_feats)
    if n_folio_lines < 8:
        continue

    # Build trajectory: Q1-Q4 means for each metric
    traj = {}
    for q in range(1, 5):
        q_feats = [f for f in folio_feats if f['quartile'] == q]
        if not q_feats:
            break
        for role in ROLES:
            traj[f'{role}_Q{q}'] = float(np.mean([f['role_fracs'][role] for f in q_feats]))
        traj[f'link_Q{q}'] = float(np.mean([f['link_density'] for f in q_feats]))
        for kt in ['k', 'h', 'e']:
            traj[f'kern_{kt}_Q{q}'] = float(np.mean([f['kernel_fracs'][kt] for f in q_feats]))
    else:
        folio_traj_data[folio] = traj

print(f"\n  Folios with full 4-quartile coverage (>=8 lines): {len(folio_traj_data)}")
print(f"  Folios excluded: {n_folios - len(folio_traj_data)}")

clustering_results = {
    'n_folios_clustered': len(folio_traj_data),
    'n_folios_excluded': n_folios - len(folio_traj_data),
}

if len(folio_traj_data) >= 10:
    # Build slope vectors (Q4-Q1 for each metric)
    metric_names = []
    for role in ROLES:
        metric_names.append(f'{role}_slope')
    metric_names.append('link_slope')
    for kt in ['k', 'h', 'e']:
        metric_names.append(f'kern_{kt}_slope')

    folio_list = sorted(folio_traj_data.keys())
    slope_matrix = []
    for folio in folio_list:
        t = folio_traj_data[folio]
        slopes = []
        for role in ROLES:
            slopes.append(t.get(f'{role}_Q4', 0) - t.get(f'{role}_Q1', 0))
        slopes.append(t.get('link_Q4', 0) - t.get('link_Q1', 0))
        for kt in ['k', 'h', 'e']:
            slopes.append(t.get(f'kern_{kt}_Q4', 0) - t.get(f'kern_{kt}_Q1', 0))
        slope_matrix.append(slopes)

    slope_matrix = np.array(slope_matrix)

    # Standardize
    means = slope_matrix.mean(axis=0)
    stds = slope_matrix.std(axis=0)
    stds[stds == 0] = 1  # avoid div-by-zero
    slope_std = (slope_matrix - means) / stds

    # Hierarchical clustering
    dist = pdist(slope_std, metric='euclidean')
    Z = linkage(dist, method='average')

    # Silhouette sweep
    from sklearn.metrics import silhouette_score

    best_k = 2
    best_sil = -1
    sil_scores = {}

    for k in range(2, min(11, len(folio_list))):
        labels = fcluster(Z, t=k, criterion='maxclust')
        if len(set(labels)) < 2:
            continue
        sil = silhouette_score(slope_std, labels)
        sil_scores[k] = round(sil, 4)
        if sil > best_sil:
            best_sil = sil
            best_k = k

    print(f"  Silhouette scores: {sil_scores}")
    print(f"  Best k={best_k}, silhouette={best_sil:.4f}")

    # Get best labels
    best_labels = fcluster(Z, t=best_k, criterion='maxclust')

    # Characterize clusters
    cluster_profiles = {}
    for cl in sorted(set(best_labels)):
        cl_indices = [i for i, l in enumerate(best_labels) if l == cl]
        cl_folios = [folio_list[i] for i in cl_indices]
        cl_slopes = slope_matrix[cl_indices]
        cl_mean_slopes = cl_slopes.mean(axis=0)

        # Regime distribution
        cl_regimes = Counter(folio_to_regime.get(f, 'UNKNOWN') for f in cl_folios)

        profile = {
            'n_folios': len(cl_folios),
            'folios': cl_folios,
            'mean_slopes': {metric_names[i]: round(float(cl_mean_slopes[i]), 4) for i in range(len(metric_names))},
            'regime_distribution': dict(cl_regimes),
        }
        cluster_profiles[f'cluster_{cl}'] = profile
        print(f"\n  Cluster {cl}: {len(cl_folios)} folios")
        print(f"    Regimes: {dict(cl_regimes)}")
        for i, mn in enumerate(metric_names):
            val = cl_mean_slopes[i]
            if abs(val) > 0.01:
                print(f"    {mn}: {val:+.4f}")

    # Regime-cluster cross-tab
    regime_cluster_crosstab = {}
    for regime in regimes:
        regime_cluster_crosstab[regime] = {}
        for cl in sorted(set(best_labels)):
            cl_profile = cluster_profiles[f'cluster_{cl}']
            regime_cluster_crosstab[regime][f'cluster_{cl}'] = cl_profile['regime_distribution'].get(regime, 0)

    clustering_results.update({
        'best_k': best_k,
        'silhouette': round(best_sil, 4),
        'silhouette_scores': sil_scores,
        'metric_names': metric_names,
        'cluster_profiles': cluster_profiles,
        'regime_cluster_crosstab': regime_cluster_crosstab,
    })
else:
    print("  Insufficient folios for clustering (need >= 10)")
    clustering_results['note'] = 'insufficient folios'

# ============================================================
# SECTION 7: SUMMARY & SAVE
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Scorecard
print("\nScorecard:")
for role in ROLES:
    sp = test1_results['corpus_wide']['spearman'][role]
    q1 = test1_results['corpus_wide']['quartile_means']['Q1'][role]
    q4 = test1_results['corpus_wide']['quartile_means']['Q4'][role]
    sig = 'SIG' if sp['p'] < 0.05 else 'ns'
    print(f"  T1 {role:<10} rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

sp = test2_results['spearman']
q1 = test2_results['quartile_means']['Q1']
q4 = test2_results['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T2 LINK       rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

for ktype in ['k', 'h', 'e']:
    sp = test3_results[ktype]['spearman']
    q1 = test3_results[ktype]['quartile_means']['Q1']
    q4 = test3_results[ktype]['quartile_means']['Q4']
    sig = 'SIG' if sp['p'] < 0.05 else 'ns'
    print(f"  T3 kern_{ktype:<5} rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

if 'spearman' in test3_results.get('ke_ratio', {}):
    sp = test3_results['ke_ratio']['spearman']
    q1 = test3_results['ke_ratio']['quartile_means']['Q1']
    q4 = test3_results['ke_ratio']['quartile_means']['Q4']
    sig = 'SIG' if sp['p'] < 0.05 else 'ns'
    print(f"  T3 k/e ratio  rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

if 'best_k' in clustering_results:
    print(f"  Clustering: k={clustering_results['best_k']} sil={clustering_results['silhouette']:.4f} ({clustering_results['n_folios_clustered']} folios)")

# Save results
results = {
    'metadata': {
        'phase': 'B_FOLIO_TEMPORAL_PROFILE',
        'script': 'folio_temporal_metrics',
        'timestamp': datetime.now().isoformat(),
        'total_b_tokens': total_b_tokens,
        'total_folios': n_folios,
        'total_lines': n_lines_total,
        'line_features_count': len(line_features),
    },
    'test1_role_trajectory': test1_results,
    'test2_link_trajectory': test2_results,
    'test3_kernel_trajectory': test3_results,
    'clustering': clustering_results,
}

output_path = RESULTS_DIR / 'folio_temporal_metrics.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("\nDone.")
