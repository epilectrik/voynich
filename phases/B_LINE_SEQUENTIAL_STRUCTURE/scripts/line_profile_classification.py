#!/usr/bin/env python3
"""
B_LINE_SEQUENTIAL_STRUCTURE - Script 3: Line Profile Classification

Tests whether lines can be classified into functional types and whether
those types sequence predictably.

Tests:
  11. Line Feature Vector Construction (27 dimensions)
  12. Line Clustering (hierarchical + k-means, silhouette sweep)
  13. Line Type Sequencing (transition matrix or cosine similarity)
  14. Positional Prediction (per-feature Spearman, partial R2 vs REGIME+section)
  15. Sequential Prediction (lag-1 Delta-R2 — THE CRITICAL TEST)

Constraint references:
  C664-C669: Class-level proportions stationary within folios
  C171: 94.2% class change line-to-line
  C391: Time-reversal symmetry

Dependencies:
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json
  - phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json
  - scripts/voynich.py (Transcript, Morphology)

Output: results/line_profile_classification.json
"""

import json
import sys
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

EN_QO_CLASSES = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH_CLASSES = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}

HAZARD_CLASSES = {7, 30, 9, 23, 8, 31}

MIN_LINES_PER_FOLIO = 8
PREFIX_FAMILIES = ['ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'other']
SUFFIX_CATS = ['aiin', 'ol', 'y', 'e_family', 'bare', 'other']

SUFFIX_AIIN = {'aiin'}
SUFFIX_OL = {'ol'}
SUFFIX_Y = {'y'}
SUFFIX_E_FAMILY = {'ey', 'eey', 'edy', 'dy'}


def line_sort_key(line_str):
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)


def classify_suffix(suffix):
    if suffix is None:
        return 'bare'
    if suffix in SUFFIX_AIIN:
        return 'aiin'
    if suffix in SUFFIX_OL:
        return 'ol'
    if suffix in SUFFIX_Y:
        return 'y'
    if suffix in SUFFIX_E_FAMILY:
        return 'e_family'
    return 'other'


def classify_prefix(prefix):
    if prefix is None:
        return None
    for family in PREFIX_FAMILIES:
        if family != 'other' and prefix == family:
            return family
    return 'other'


def safe_spearmanr(x, y):
    from scipy.stats import spearmanr
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if len(set(y)) <= 1 or len(x) < 3:
            return 0.0, 1.0
        return spearmanr(x, y)


# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================
print("=" * 70)
print("B_LINE_SEQUENTIAL_STRUCTURE - Script 3: Line Profile Classification")
print("=" * 70)
print("\n--- Section 1: Load & Prepare ---")

# Load class token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)
if 'token_to_class' in ctm_raw:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
else:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw.items()}

# Load regime mapping
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Build morphology cache
morph_engine = Morphology()
morph_cache = {}


def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph_engine.extract(word)
    return morph_cache[word]


# Build per-line data
tx = Transcript()
folio_lines_raw = defaultdict(lambda: defaultdict(list))
total_b_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    total_b_tokens += 1
    folio_lines_raw[token.folio][token.line].append(token.word)

valid_folios = sorted(f for f, lines in folio_lines_raw.items()
                      if len(lines) >= MIN_LINES_PER_FOLIO)
print(f"  Loaded {total_b_tokens} B tokens, {len(valid_folios)} valid folios")

# Pre-compute morphology
for folio in valid_folios:
    for line_id, words in folio_lines_raw[folio].items():
        for w in words:
            get_morph(w)
print(f"  Morphology cache: {len(morph_cache)} words")


# ============================================================
# TEST 11: LINE FEATURE VECTOR CONSTRUCTION
# ============================================================
print("\n" + "=" * 70)
print("TEST 11: Line Feature Vector Construction (27 dimensions)")
print("=" * 70)

# Feature names (27 total)
FEATURE_NAMES = (
    ['CC', 'EN', 'FL', 'FQ', 'AX']  # 5: role fractions
    + ['QO_frac']  # 1: EN subfamily
    + ['cc_daiin', 'cc_ol', 'cc_old']  # 3: CC trigger fractions
    + ['link_density']  # 1
    + ['hazard_density']  # 1
    + ['sfx_aiin', 'sfx_ol', 'sfx_y', 'sfx_e_family', 'sfx_bare', 'sfx_other']  # 6
    + ['pfx_ch', 'pfx_sh', 'pfx_qo', 'pfx_da', 'pfx_ol', 'pfx_ok', 'pfx_ot', 'pfx_other']  # 8
    + ['line_length_z']  # 1
    + ['ttr']  # 1
)
N_FEATURES = len(FEATURE_NAMES)
print(f"  Feature dimensions: {N_FEATURES}")

# Build line records
line_data = []  # list of dicts with folio, line, norm_pos, regime, features array

all_line_lengths = []
for folio in valid_folios:
    for line_id in folio_lines_raw[folio]:
        all_line_lengths.append(len(folio_lines_raw[folio][line_id]))
mean_line_len = np.mean(all_line_lengths)
std_line_len = np.std(all_line_lengths) if np.std(all_line_lengths) > 0 else 1.0

for folio in valid_folios:
    sorted_lines = sorted(folio_lines_raw[folio].keys(), key=line_sort_key)
    n_lines = len(sorted_lines)

    for idx, line_id in enumerate(sorted_lines):
        words = folio_lines_raw[folio][line_id]
        n_tok = len(words)
        if n_tok == 0:
            continue

        norm_pos = idx / max(n_lines - 1, 1)

        # Classify each token
        classes = [token_to_class.get(w) for w in words]
        roles = [CLASS_TO_ROLE.get(c, 'UNC') if c is not None else 'UNC' for c in classes]
        role_counts = Counter(roles)

        # Role fractions
        cc_frac = role_counts.get('CC', 0) / n_tok
        en_frac = role_counts.get('EN', 0) / n_tok
        fl_frac = role_counts.get('FL', 0) / n_tok
        fq_frac = role_counts.get('FQ', 0) / n_tok
        ax_frac = role_counts.get('AX', 0) / n_tok

        # QO fraction among EN
        en_tokens_cls = [c for c, r in zip(classes, roles) if r == 'EN' and c is not None]
        qo_count = sum(1 for c in en_tokens_cls if c in EN_QO_CLASSES)
        chsh_count = sum(1 for c in en_tokens_cls if c in EN_CHSH_CLASSES)
        qo_frac = qo_count / (qo_count + chsh_count) if (qo_count + chsh_count) > 0 else 0.5

        # CC trigger fractions
        cc_tokens_cls = [c for c, r in zip(classes, roles) if r == 'CC' and c is not None]
        n_cc = len(cc_tokens_cls) if len(cc_tokens_cls) > 0 else 1
        cc_daiin_frac = sum(1 for c in cc_tokens_cls if c in CC_DAIIN) / n_cc
        cc_ol_frac = sum(1 for c in cc_tokens_cls if c in CC_OL) / n_cc
        cc_old_frac = sum(1 for c in cc_tokens_cls if c in CC_OL_D) / n_cc

        # LINK density (tokens containing 'ol')
        link_count = sum(1 for w in words if 'ol' in w)
        link_density = link_count / n_tok

        # Hazard density
        hazard_count = sum(1 for c in classes if c is not None and c in HAZARD_CLASSES)
        hazard_density = hazard_count / n_tok

        # Suffix profile
        suffix_counts = Counter()
        prefix_counts = Counter()
        for w in words:
            m = morph_cache.get(w)
            if m:
                suffix_counts[classify_suffix(m.suffix)] += 1
                pf = classify_prefix(m.prefix)
                if pf is not None:
                    prefix_counts[pf] += 1
                else:
                    # No prefix; don't count in prefix distribution
                    pass

        sfx_total = sum(suffix_counts.values()) or 1
        pfx_total = sum(prefix_counts.values()) or 1

        sfx_fracs = [suffix_counts.get(s, 0) / sfx_total for s in ['aiin', 'ol', 'y', 'e_family', 'bare', 'other']]
        pfx_fracs = [prefix_counts.get(p, 0) / pfx_total for p in PREFIX_FAMILIES]

        # Line length z-scored
        line_len_z = (n_tok - mean_line_len) / std_line_len

        # Type-token ratio
        ttr = len(set(words)) / n_tok

        # Build feature vector
        features = np.array(
            [cc_frac, en_frac, fl_frac, fq_frac, ax_frac]  # 5
            + [qo_frac]  # 1
            + [cc_daiin_frac, cc_ol_frac, cc_old_frac]  # 3
            + [link_density]  # 1
            + [hazard_density]  # 1
            + sfx_fracs  # 6
            + pfx_fracs  # 8
            + [line_len_z]  # 1
            + [ttr]  # 1
        )
        assert len(features) == N_FEATURES, f"Feature count mismatch: {len(features)} != {N_FEATURES}"

        line_data.append({
            'folio': folio,
            'line': line_id,
            'norm_pos': norm_pos,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
            'features': features,
            'folio_idx': idx,
            'n_lines_in_folio': n_lines,
        })

n_lines = len(line_data)
print(f"  Lines with feature vectors: {n_lines}")

# Build feature matrix
X = np.array([d['features'] for d in line_data])
print(f"  Feature matrix shape: {X.shape}")

# Z-score normalize
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1.0  # avoid division by zero
X_z = (X - X_mean) / X_std

# Feature statistics
print(f"\n  Feature statistics (raw):")
for i, name in enumerate(FEATURE_NAMES):
    print(f"    {name:>16}: mean={X_mean[i]:.4f}  std={X_std[i]:.4f}  min={X[:, i].min():.4f}  max={X[:, i].max():.4f}")


# ============================================================
# TEST 12: LINE CLUSTERING
# ============================================================
print("\n" + "=" * 70)
print("TEST 12: Line Clustering")
print("=" * 70)

from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

# Silhouette sweep k=2..15 for both methods
max_k = min(15, n_lines - 1)
hier_silhouettes = {}
kmeans_silhouettes = {}

# Hierarchical clustering (UPGMA)
Z = linkage(X_z, method='average', metric='euclidean')

for k in range(2, max_k + 1):
    labels_h = fcluster(Z, t=k, criterion='maxclust')
    if len(set(labels_h)) < 2:
        continue
    sil_h = silhouette_score(X_z, labels_h)
    hier_silhouettes[k] = round(sil_h, 4)

# K-means
for k in range(2, max_k + 1):
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels_km = km.fit_predict(X_z)
    if len(set(labels_km)) < 2:
        continue
    sil_km = silhouette_score(X_z, labels_km)
    kmeans_silhouettes[k] = round(sil_km, 4)

print(f"\n  Silhouette scores:")
print(f"    k  | UPGMA  | KMeans")
print(f"    ---|--------|-------")
for k in range(2, max_k + 1):
    h = hier_silhouettes.get(k, '-')
    km = kmeans_silhouettes.get(k, '-')
    print(f"    {k:>2} | {h if isinstance(h, str) else f'{h:.4f}':>6} | {km if isinstance(km, str) else f'{km:.4f}':>6}")

best_hier_k = max(hier_silhouettes, key=hier_silhouettes.get) if hier_silhouettes else 2
best_km_k = max(kmeans_silhouettes, key=kmeans_silhouettes.get) if kmeans_silhouettes else 2
best_hier_sil = hier_silhouettes.get(best_hier_k, 0)
best_km_sil = kmeans_silhouettes.get(best_km_k, 0)

print(f"\n  Best hierarchical: k={best_hier_k}, sil={best_hier_sil:.4f}")
print(f"  Best KMeans: k={best_km_k}, sil={best_km_sil:.4f}")

best_sil = max(best_hier_sil, best_km_sil)

# Check for degenerate clustering: if the best solution puts <2% in any cluster,
# it's an outlier detection, not meaningful clustering. Fall back to KMeans.
def is_degenerate(labels, threshold=0.02):
    sizes = Counter(labels)
    total = sum(sizes.values())
    return any(v / total < threshold for v in sizes.values())

# Try hierarchical first
if best_hier_sil > 0.15:
    test_labels = fcluster(Z, t=best_hier_k, criterion='maxclust') - 1
    if is_degenerate(test_labels):
        print(f"\n  UPGMA k={best_hier_k} is degenerate (outlier cluster). Falling back to KMeans.")
        best_hier_sil = 0.0  # disqualify

best_sil = max(best_hier_sil, best_km_sil)
discrete_types = best_sil > 0.15

if discrete_types:
    print(f"\n  DISCRETE TYPES DETECTED (sil={best_sil:.4f} > 0.15)")

    # Use the better method
    if best_km_sil >= best_hier_sil:
        best_k = best_km_k
        km_best = KMeans(n_clusters=best_k, n_init=10, random_state=42)
        best_labels = km_best.fit_predict(X_z)
        method_used = 'KMeans'
    else:
        best_k = best_hier_k
        best_labels = fcluster(Z, t=best_k, criterion='maxclust') - 1
        method_used = 'UPGMA'

    print(f"  Using {method_used} with k={best_k}")

    # Characterize clusters
    cluster_sizes = Counter(int(l) for l in best_labels)
    print(f"\n  Cluster sizes: {dict(sorted(cluster_sizes.items()))}")

    # Per-cluster feature means
    print(f"\n  Cluster feature profiles (z-scored means):")
    print(f"    {'Feature':>16}", end='')
    for c in sorted(cluster_sizes.keys()):
        print(f"  C{c:>2}", end='')
    print()

    cluster_profiles = {}
    for c in sorted(cluster_sizes.keys()):
        mask = np.array([int(l) == c for l in best_labels])
        cluster_profiles[c] = X_z[mask].mean(axis=0).tolist()

    # Find defining features per cluster (|z-mean| > 0.3)
    for i, name in enumerate(FEATURE_NAMES):
        vals = [cluster_profiles[c][i] for c in sorted(cluster_profiles.keys())]
        if max(abs(v) for v in vals) > 0.3:
            print(f"    {name:>16}", end='')
            for v in vals:
                marker = '*' if abs(v) > 0.5 else ''
                print(f" {v:>5.2f}{marker}", end='')
            print()

    # REGIME crosstab
    print(f"\n  Cluster x REGIME crosstab:")
    regimes = sorted(set(d['regime'] for d in line_data))
    print(f"    {'Cluster':>8}", end='')
    for r in regimes:
        print(f" {r:>10}", end='')
    print()
    for c in sorted(cluster_sizes.keys()):
        print(f"    C{c:>7}", end='')
        c_lines = [d for d, lab in zip(line_data, best_labels) if lab == c]
        for r in regimes:
            count = sum(1 for d in c_lines if d['regime'] == r)
            pct = 100 * count / len(c_lines) if c_lines else 0
            print(f" {pct:>9.1f}%", end='')
        print(f"  n={len(c_lines)}")

    # Position distribution per cluster
    print(f"\n  Cluster mean norm_pos:")
    for c in sorted(cluster_sizes.keys()):
        c_positions = [d['norm_pos'] for d, lab in zip(line_data, best_labels) if lab == c]
        print(f"    C{c}: mean={np.mean(c_positions):.3f} std={np.std(c_positions):.3f}")

    # Store labels for later tests
    best_labels_int = [int(l) for l in best_labels]
    for i, d in enumerate(line_data):
        d['cluster'] = best_labels_int[i]

else:
    print(f"\n  NO DISCRETE TYPES (best sil={best_sil:.4f} <= 0.15)")
    print(f"  Lines form a continuous distribution, not discrete clusters.")

    # PCA analysis
    from sklearn.decomposition import PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_z)

    var_explained = pca.explained_variance_ratio_
    cum_var = np.cumsum(var_explained)
    print(f"\n  PCA variance explained:")
    for i in range(min(10, len(var_explained))):
        print(f"    PC{i+1}: {100*var_explained[i]:.1f}% (cumulative: {100*cum_var[i]:.1f}%)")

    # Top PC1/PC2 loadings
    print(f"\n  PC1 top loadings:")
    pc1_loadings = pca.components_[0]
    sorted_idx = np.argsort(np.abs(pc1_loadings))[::-1]
    for j in sorted_idx[:5]:
        print(f"    {FEATURE_NAMES[j]:>16}: {pc1_loadings[j]:+.4f}")

    print(f"\n  PC2 top loadings:")
    pc2_loadings = pca.components_[1]
    sorted_idx2 = np.argsort(np.abs(pc2_loadings))[::-1]
    for j in sorted_idx2[:5]:
        print(f"    {FEATURE_NAMES[j]:>16}: {pc2_loadings[j]:+.4f}")

    best_labels = None
    best_k = None
    method_used = 'PCA'

    for d in line_data:
        d['cluster'] = None

test12_results = {
    'hier_silhouettes': hier_silhouettes,
    'kmeans_silhouettes': kmeans_silhouettes,
    'best_hier': {'k': best_hier_k, 'sil': best_hier_sil},
    'best_kmeans': {'k': best_km_k, 'sil': best_km_sil},
    'discrete_types': discrete_types,
    'best_sil': round(best_sil, 4),
    'method_used': method_used,
}

if discrete_types:
    test12_results['n_clusters'] = best_k
    test12_results['cluster_sizes'] = {str(k): v for k, v in sorted(cluster_sizes.items())}
    test12_results['cluster_profiles'] = {
        str(c): {FEATURE_NAMES[i]: round(v, 4) for i, v in enumerate(profile)}
        for c, profile in cluster_profiles.items()
    }
else:
    test12_results['pca_variance_explained'] = [round(v, 4) for v in var_explained[:10].tolist()]
    test12_results['pc1_top_loadings'] = {
        FEATURE_NAMES[j]: round(float(pc1_loadings[j]), 4)
        for j in np.argsort(np.abs(pc1_loadings))[::-1][:5]
    }
    test12_results['pc2_top_loadings'] = {
        FEATURE_NAMES[j]: round(float(pc2_loadings[j]), 4)
        for j in np.argsort(np.abs(pc2_loadings))[::-1][:5]
    }


# ============================================================
# TEST 13: LINE TYPE SEQUENCING
# ============================================================
print("\n" + "=" * 70)
print("TEST 13: Line Type Sequencing")
print("=" * 70)

from scipy.spatial.distance import cosine

if discrete_types and best_labels is not None:
    # Transition matrix of line types
    print(f"\n  Building cluster transition matrix...")
    n_clusters = best_k
    trans_matrix = np.zeros((n_clusters, n_clusters), dtype=int)

    for folio in valid_folios:
        folio_data = [(d['folio_idx'], d['cluster']) for d in line_data
                      if d['folio'] == folio and d['cluster'] is not None]
        folio_data.sort()
        for i in range(len(folio_data) - 1):
            src = int(folio_data[i][1])
            tgt = int(folio_data[i + 1][1])
            trans_matrix[src, tgt] += 1

    print(f"  Transition matrix:")
    print(f"    {'':>6}", end='')
    for c in range(n_clusters):
        print(f"   C{c:>2}", end='')
    print()
    for src in range(n_clusters):
        row_sum = trans_matrix[src].sum()
        print(f"    C{src:>4}", end='')
        for tgt in range(n_clusters):
            pct = 100 * trans_matrix[src, tgt] / row_sum if row_sum > 0 else 0
            print(f" {pct:>5.1f}%", end='')
        print(f"  n={row_sum}")

    # Chi-square independence test
    from scipy.stats import chi2_contingency
    try:
        nz_rows = trans_matrix.sum(axis=1) > 0
        nz_cols = trans_matrix.sum(axis=0) > 0
        tm_test = trans_matrix[np.ix_(nz_rows, nz_cols)]
        chi2_tm, p_tm, dof_tm, _ = chi2_contingency(tm_test)
        print(f"\n  Chi-square: chi2={chi2_tm:.2f}, dof={dof_tm}, p={p_tm:.2e}")
        test13_chi2 = {'chi2': round(chi2_tm, 2), 'dof': dof_tm, 'p': float(p_tm)}
    except Exception as e:
        test13_chi2 = {'error': str(e)}

    test13_results = {
        'mode': 'cluster_transitions',
        'transition_matrix': trans_matrix.tolist(),
        'chi_square': test13_chi2,
    }

else:
    # Continuous: cosine similarity of adjacent vs random line pairs
    print(f"\n  Computing cosine similarity (continuous mode)...")
    adjacent_sims = []
    random_sims = []

    for folio in valid_folios:
        folio_data = [(d['folio_idx'], d['features']) for d in line_data if d['folio'] == folio]
        folio_data.sort()

        if len(folio_data) < 2:
            continue

        # Adjacent pairs
        for i in range(len(folio_data) - 1):
            sim = 1.0 - cosine(folio_data[i][1], folio_data[i + 1][1])
            adjacent_sims.append(sim)

        # Random pairs (sample same number)
        n_adj = len(folio_data) - 1
        indices = list(range(len(folio_data)))
        for _ in range(n_adj):
            i, j = np.random.choice(indices, 2, replace=False)
            sim = 1.0 - cosine(folio_data[i][1], folio_data[j][1])
            random_sims.append(sim)

    mean_adj = np.mean(adjacent_sims)
    mean_rnd = np.mean(random_sims)

    print(f"  Adjacent pairs: n={len(adjacent_sims)}, mean cosine sim={mean_adj:.4f}")
    print(f"  Random pairs:   n={len(random_sims)}, mean cosine sim={mean_rnd:.4f}")
    print(f"  Difference: {mean_adj - mean_rnd:+.4f}")

    # Permutation test
    N_PERM = 1000
    perm_diffs = []
    for _ in range(N_PERM):
        perm_adj = []
        for folio in valid_folios:
            folio_data = [(d['folio_idx'], d['features']) for d in line_data if d['folio'] == folio]
            if len(folio_data) < 2:
                continue
            # Shuffle feature vectors within folio
            features_shuffled = [d[1] for d in folio_data]
            np.random.shuffle(features_shuffled)
            for i in range(len(features_shuffled) - 1):
                sim = 1.0 - cosine(features_shuffled[i], features_shuffled[i + 1])
                perm_adj.append(sim)
        perm_diffs.append(np.mean(perm_adj))

    p_adj = np.mean([1 if p >= mean_adj else 0 for p in perm_diffs])
    print(f"\n  Permutation test (adjacent > shuffled):")
    print(f"    Observed mean: {mean_adj:.4f}")
    print(f"    Permuted mean: {np.mean(perm_diffs):.4f}")
    print(f"    p-value: {p_adj:.4f}")

    test13_results = {
        'mode': 'cosine_similarity',
        'n_adjacent_pairs': len(adjacent_sims),
        'mean_adjacent_sim': round(mean_adj, 4),
        'mean_random_sim': round(mean_rnd, 4),
        'difference': round(mean_adj - mean_rnd, 4),
        'permutation_p': round(float(p_adj), 4),
        'permuted_mean': round(float(np.mean(perm_diffs)), 4),
    }


# ============================================================
# TEST 14: POSITIONAL PREDICTION
# ============================================================
print("\n" + "=" * 70)
print("TEST 14: Positional Feature Prediction")
print("=" * 70)

# Spearman rho of each feature vs norm_pos
positions = np.array([d['norm_pos'] for d in line_data])

test14_results = {}
print(f"\n  Per-feature Spearman rho vs norm_pos:")
sig_features = 0
for i, name in enumerate(FEATURE_NAMES):
    vals = X[:, i]
    rho, p = safe_spearmanr(positions, vals)
    sig = '*' if p < 0.05 else ''
    if p < 0.05:
        sig_features += 1
    print(f"    {name:>16}: rho={rho:+.4f} p={p:.2e} {sig}")
    test14_results[name] = {'rho': round(rho, 4), 'p': float(p)}

print(f"\n  Significant features: {sig_features}/{N_FEATURES}")

# Partial R2: position adds beyond REGIME + section
# Use OLS: feature ~ REGIME_dummies + norm_pos
# Compare R2 with and without norm_pos
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

# Encode REGIME as dummies
regime_labels = np.array([d['regime'] for d in line_data]).reshape(-1, 1)
enc = OneHotEncoder(sparse_output=False, drop='first')
regime_dummies = enc.fit_transform(regime_labels)

# Model: REGIME only vs REGIME + position
X_regime = regime_dummies
X_regime_pos = np.column_stack([regime_dummies, positions])

print(f"\n  Partial R2 (position beyond REGIME):")
partial_r2 = {}
sig_partial = 0
for i, name in enumerate(FEATURE_NAMES):
    y = X[:, i]

    # R2 with REGIME only
    reg1 = LinearRegression().fit(X_regime, y)
    r2_regime = reg1.score(X_regime, y)

    # R2 with REGIME + position
    reg2 = LinearRegression().fit(X_regime_pos, y)
    r2_full = reg2.score(X_regime_pos, y)

    delta_r2 = r2_full - r2_regime
    # F-test for the added variable
    n = len(y)
    p_vars = X_regime_pos.shape[1]
    if r2_full < 1.0:
        f_stat = (delta_r2 / 1) / ((1 - r2_full) / (n - p_vars))
        from scipy.stats import f as f_dist
        p_f = 1 - f_dist.cdf(f_stat, 1, n - p_vars)
    else:
        f_stat = np.inf
        p_f = 0.0

    sig = '*' if p_f < 0.05 else ''
    if p_f < 0.05:
        sig_partial += 1
    if delta_r2 > 0.005 or p_f < 0.05:
        print(f"    {name:>16}: R2_regime={r2_regime:.4f} R2_full={r2_full:.4f} dR2={delta_r2:+.4f} F={f_stat:.2f} p={p_f:.2e} {sig}")

    partial_r2[name] = {
        'r2_regime': round(r2_regime, 4),
        'r2_full': round(r2_full, 4),
        'delta_r2': round(delta_r2, 4),
        'f_stat': round(f_stat, 2),
        'p_f': float(p_f),
    }

print(f"\n  Features where position adds beyond REGIME: {sig_partial}/{N_FEATURES}")

test14_full = {
    'spearman': test14_results,
    'partial_r2': partial_r2,
    'sig_spearman_count': sig_features,
    'sig_partial_r2_count': sig_partial,
}


# ============================================================
# TEST 15: SEQUENTIAL PREDICTION (THE CRITICAL TEST)
# ============================================================
print("\n" + "=" * 70)
print("TEST 15: Sequential Prediction (lag-1 Delta-R2)")
print("=" * 70)

# For each feature: compare
# Model A (position-only): feature_N+1 ~ norm_pos_N+1
# Model B (combined):      feature_N+1 ~ feature_N + norm_pos_N+1
# Delta-R2 = R2(B) - R2(A)

# Build adjacent pairs within folios
adj_pairs = []  # (folio, feature_N, feature_N+1, norm_pos_N+1)

for folio in valid_folios:
    folio_data = sorted(
        [(d['folio_idx'], d['features'], d['norm_pos']) for d in line_data if d['folio'] == folio],
        key=lambda x: x[0]
    )
    for i in range(len(folio_data) - 1):
        # Only strictly consecutive lines
        if folio_data[i + 1][0] - folio_data[i][0] == 1:
            adj_pairs.append((
                folio,
                folio_data[i][1],    # features_N
                folio_data[i + 1][1], # features_N+1
                folio_data[i + 1][2], # norm_pos_N+1
            ))

n_pairs = len(adj_pairs)
print(f"\n  Strictly consecutive line pairs: {n_pairs}")

# Extract arrays
feat_prev = np.array([p[1] for p in adj_pairs])  # (n_pairs, N_FEATURES)
feat_next = np.array([p[2] for p in adj_pairs])   # (n_pairs, N_FEATURES)
pos_next = np.array([p[3] for p in adj_pairs]).reshape(-1, 1)

test15_results = {}
features_with_lag = 0
print(f"\n  Per-feature lag-1 Delta-R2:")
print(f"    {'Feature':>16}  R2_pos  R2_comb  dR2     F       p")
print(f"    {'-'*16}  ------  -------  ------  ------  ------")

for i, name in enumerate(FEATURE_NAMES):
    y = feat_next[:, i]

    # Model A: position-only
    reg_a = LinearRegression().fit(pos_next, y)
    r2_pos = max(reg_a.score(pos_next, y), 0)

    # Model B: position + lag-1 feature
    X_comb = np.column_stack([pos_next, feat_prev[:, i].reshape(-1, 1)])
    reg_b = LinearRegression().fit(X_comb, y)
    r2_comb = max(reg_b.score(X_comb, y), 0)

    delta_r2 = r2_comb - r2_pos
    # F-test
    n = len(y)
    p_vars = 2
    if r2_comb < 1.0 and n > p_vars + 1:
        f_stat = (delta_r2 / 1) / ((1 - r2_comb) / (n - p_vars - 1))
        from scipy.stats import f as f_dist
        p_f = 1 - f_dist.cdf(f_stat, 1, n - p_vars - 1)
    else:
        f_stat = 0.0
        p_f = 1.0

    sig = '*' if p_f < 0.05 else ''
    if p_f < 0.05:
        features_with_lag += 1

    # Only print notable results
    if delta_r2 > 0.005 or p_f < 0.05:
        print(f"    {name:>16}  {r2_pos:.4f}  {r2_comb:.4f}  {delta_r2:+.4f}  {f_stat:>6.1f}  {p_f:.2e} {sig}")

    test15_results[name] = {
        'r2_position': round(r2_pos, 4),
        'r2_combined': round(r2_comb, 4),
        'delta_r2': round(delta_r2, 4),
        'f_stat': round(f_stat, 2),
        'p_f': float(p_f),
    }

print(f"\n  Features where lag-1 adds prediction: {features_with_lag}/{N_FEATURES}")

# VERDICT
if features_with_lag >= 10:
    verdict = 'SEQUENTIALLY_COUPLED'
elif features_with_lag <= 2:
    verdict = 'POSITION_CONDITIONED_INDEPENDENT'
else:
    verdict = 'PARTIAL_COUPLING'

print(f"\n  === VERDICT: {verdict} ===")
print(f"  {features_with_lag} features benefit from lag-1 prediction")

if verdict == 'SEQUENTIALLY_COUPLED':
    print(f"  Lines carry substantial state memory beyond position.")
elif verdict == 'POSITION_CONDITIONED_INDEPENDENT':
    print(f"  Lines are independent draws conditioned on position. No sequential memory.")
else:
    print(f"  Partial coupling: some features carry forward state, most don't.")

# Identify which features carry memory
lag_features = [(name, test15_results[name]) for name in FEATURE_NAMES
                if test15_results[name]['p_f'] < 0.05]
lag_features.sort(key=lambda x: x[1]['delta_r2'], reverse=True)

if lag_features:
    print(f"\n  Features with significant lag-1 contribution (sorted by dR2):")
    for name, res in lag_features:
        print(f"    {name:>16}: dR2={res['delta_r2']:+.4f} F={res['f_stat']:.1f} p={res['p_f']:.2e}")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n  T11: {N_FEATURES} features constructed per line")

print(f"\n  T12: {'DISCRETE TYPES' if discrete_types else 'CONTINUOUS'} (best sil={best_sil:.4f})")
if discrete_types:
    print(f"    {best_k} clusters via {method_used}")

print(f"\n  T13: ", end='')
if test13_results['mode'] == 'cosine_similarity':
    print(f"Adjacent sim={test13_results['mean_adjacent_sim']:.4f} vs random={test13_results['mean_random_sim']:.4f}")
    print(f"         Permutation p={test13_results['permutation_p']:.4f}")
else:
    print(f"Cluster transitions: chi2={test13_results['chi_square'].get('chi2', 'N/A')}")

print(f"\n  T14: {sig_features}/{N_FEATURES} features correlated with position")
print(f"       {sig_partial}/{N_FEATURES} features where position adds beyond REGIME")

print(f"\n  T15: VERDICT = {verdict}")
print(f"       {features_with_lag}/{N_FEATURES} features with lag-1 prediction")


# ============================================================
# SAVE
# ============================================================
results = {
    'metadata': {
        'phase': 'B_LINE_SEQUENTIAL_STRUCTURE',
        'script': 'line_profile_classification',
        'timestamp': datetime.now().isoformat(),
        'total_lines': n_lines,
        'n_features': N_FEATURES,
        'feature_names': FEATURE_NAMES,
        'n_consecutive_pairs': n_pairs,
    },
    'test11_feature_stats': {
        name: {'mean': round(float(X_mean[i]), 4), 'std': round(float(X_std[i]), 4)}
        for i, name in enumerate(FEATURE_NAMES)
    },
    'test12_clustering': test12_results,
    'test13_sequencing': test13_results,
    'test14_positional_prediction': test14_full,
    'test15_sequential_prediction': {
        'per_feature': test15_results,
        'n_pairs': n_pairs,
        'features_with_lag': features_with_lag,
        'verdict': verdict,
        'lag_features': [
            {'name': name, 'delta_r2': res['delta_r2'], 'p': res['p_f']}
            for name, res in lag_features
        ] if lag_features else [],
    },
}

output_path = RESULTS_DIR / 'line_profile_classification.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("\nDone.")
