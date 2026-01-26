"""
FQ_ANATOMY Script 1: Structural Anatomy

Determine the organizing principle of FQ's 4-class structure.
Tests morphological vs positional partitions, PCA, clustering, 13-14 deep dive.

Reuses sr_features.json and sr_internal_structure.json from SMALL_ROLE_ANATOMY.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
SR_FEATURES = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_features.json'
SR_INTERNAL = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_internal_structure.json'
RESULTS = BASE / 'phases/FQ_ANATOMY/results'

FQ_CLASSES = {9, 13, 14, 23}
FQ_BARE = {9, 23}
FQ_PREFIXED = {13, 14}
FQ_MEDIAL = {9, 13}
FQ_FINAL = {14, 23}

# Hazard classes per C109
HAZARD_CLASSES = {7, 8, 9, 23, 30}
FQ_HAZARD = FQ_CLASSES & HAZARD_CLASSES    # {9, 23}
FQ_SAFE = FQ_CLASSES - HAZARD_CLASSES      # {13, 14}

# Load data
print("=" * 70)
print("FQ STRUCTURAL ANATOMY")
print("=" * 70)

tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

with open(MIDDLE_CLASSES) as f:
    middle_classes = json.load(f)

with open(SR_FEATURES) as f:
    sr_features = json.load(f)

with open(SR_INTERNAL) as f:
    sr_internal = json.load(f)

# Build per-token data
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'word': word, 'class': cls, 'folio': token.folio
    })

# Per-class position samples
class_positions = defaultdict(list)
for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n == 0:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls in FQ_CLASSES:
            pos = i / (n - 1) if n > 1 else 0.5
            class_positions[cls].append(pos)

results = {}

# ============================================================
# SECTION 1: MORPHOLOGICAL PARTITION TEST
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: MORPHOLOGICAL PARTITION (BARE vs PREFIXED)")
print("=" * 70)

bare_positions = []
prefixed_positions = []
for cls in FQ_BARE:
    bare_positions.extend(class_positions[cls])
for cls in FQ_PREFIXED:
    prefixed_positions.extend(class_positions[cls])

bare_arr = np.array(bare_positions)
pref_arr = np.array(prefixed_positions)

# Mann-Whitney on position
U_morph, p_morph = stats.mannwhitneyu(bare_arr, pref_arr, alternative='two-sided')
# Rank-biserial effect size: r = 1 - (2U)/(n1*n2)
n1, n2 = len(bare_arr), len(pref_arr)
r_morph = 1 - (2 * U_morph) / (n1 * n2)

print(f"\nBARE ({sorted(FQ_BARE)}): n={n1}, mean_pos={bare_arr.mean():.4f}")
print(f"PREFIXED ({sorted(FQ_PREFIXED)}): n={n2}, mean_pos={pref_arr.mean():.4f}")
print(f"Mann-Whitney U={U_morph:.0f}, p={p_morph:.2e}")
print(f"Rank-biserial r={r_morph:.4f}")

# Build per-token feature vectors for more tests
# Initial rate
bare_init = []
pref_init = []
bare_final = []
pref_final = []
bare_lengths = []
pref_lengths = []

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n == 0:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls in FQ_BARE:
            bare_init.append(1.0 if i == 0 else 0.0)
            bare_final.append(1.0 if i == n - 1 else 0.0)
            bare_lengths.append(len(tok['word']))
        elif cls in FQ_PREFIXED:
            pref_init.append(1.0 if i == 0 else 0.0)
            pref_final.append(1.0 if i == n - 1 else 0.0)
            pref_lengths.append(len(tok['word']))

morph_tests = {}
for name, bare_v, pref_v in [
    ('position', bare_arr, pref_arr),
    ('initial_rate', np.array(bare_init), np.array(pref_init)),
    ('final_rate', np.array(bare_final), np.array(pref_final)),
    ('token_length', np.array(bare_lengths), np.array(pref_lengths)),
]:
    U, p = stats.mannwhitneyu(bare_v, pref_v, alternative='two-sided')
    r = 1 - (2 * U) / (len(bare_v) * len(pref_v))
    morph_tests[name] = {
        'U': float(U), 'p': float(p), 'r': round(r, 4),
        'bare_mean': round(float(bare_v.mean()), 4),
        'pref_mean': round(float(pref_v.mean()), 4),
        'significant': p < 0.001
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    print(f"  {name:15s}: bare={bare_v.mean():.4f} pref={pref_v.mean():.4f} r={r:.4f} {sig}")

# Cross-tabulate morphology x hazard
print(f"\nMorphology x Hazard cross-tabulation:")
print(f"  BARE  = {sorted(FQ_BARE)}  -> HAZARD = {sorted(FQ_HAZARD)}")
print(f"  PREF  = {sorted(FQ_PREFIXED)} -> SAFE   = {sorted(FQ_SAFE)}")
morph_hazard_overlap = FQ_BARE == FQ_HAZARD and FQ_PREFIXED == FQ_SAFE
print(f"  PERFECT OVERLAP: {morph_hazard_overlap}")

results['morphological_partition'] = {
    'bare_classes': sorted(FQ_BARE),
    'prefixed_classes': sorted(FQ_PREFIXED),
    'bare_n': n1,
    'prefixed_n': n2,
    'tests': morph_tests,
    'hazard_overlap': morph_hazard_overlap,
}

# ============================================================
# SECTION 2: POSITIONAL PARTITION TEST
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: POSITIONAL PARTITION (MEDIAL vs FINAL)")
print("=" * 70)

med_positions = []
fin_positions = []
for cls in FQ_MEDIAL:
    med_positions.extend(class_positions[cls])
for cls in FQ_FINAL:
    fin_positions.extend(class_positions[cls])

med_arr = np.array(med_positions)
fin_arr = np.array(fin_positions)

U_pos, p_pos = stats.mannwhitneyu(med_arr, fin_arr, alternative='two-sided')
n1p, n2p = len(med_arr), len(fin_arr)
r_pos = 1 - (2 * U_pos) / (n1p * n2p)

print(f"\nMEDIAL ({sorted(FQ_MEDIAL)}): n={n1p}, mean_pos={med_arr.mean():.4f}")
print(f"FINAL ({sorted(FQ_FINAL)}): n={n2p}, mean_pos={fin_arr.mean():.4f}")
print(f"Mann-Whitney U={U_pos:.0f}, p={p_pos:.2e}")
print(f"Rank-biserial r={r_pos:.4f}")

# Build per-token features for positional partition
med_init = []
fin_init_vals = []
med_final_vals = []
fin_final_vals = []
med_lengths = []
fin_lengths = []

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n == 0:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls in FQ_MEDIAL:
            med_init.append(1.0 if i == 0 else 0.0)
            med_final_vals.append(1.0 if i == n - 1 else 0.0)
            med_lengths.append(len(tok['word']))
        elif cls in FQ_FINAL:
            fin_init_vals.append(1.0 if i == 0 else 0.0)
            fin_final_vals.append(1.0 if i == n - 1 else 0.0)
            fin_lengths.append(len(tok['word']))

pos_tests = {}
for name, med_v, fin_v in [
    ('position', med_arr, fin_arr),
    ('initial_rate', np.array(med_init), np.array(fin_init_vals)),
    ('final_rate', np.array(med_final_vals), np.array(fin_final_vals)),
    ('token_length', np.array(med_lengths), np.array(fin_lengths)),
]:
    U, p = stats.mannwhitneyu(med_v, fin_v, alternative='two-sided')
    r = 1 - (2 * U) / (len(med_v) * len(fin_v))
    pos_tests[name] = {
        'U': float(U), 'p': float(p), 'r': round(r, 4),
        'med_mean': round(float(med_v.mean()), 4),
        'fin_mean': round(float(fin_v.mean()), 4),
        'significant': p < 0.001
    }
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    print(f"  {name:15s}: med={med_v.mean():.4f} fin={fin_v.mean():.4f} r={r:.4f} {sig}")

results['positional_partition'] = {
    'medial_classes': sorted(FQ_MEDIAL),
    'final_classes': sorted(FQ_FINAL),
    'medial_n': n1p,
    'final_n': n2p,
    'tests': pos_tests,
}

# Compare partition strengths
print(f"\n--- PARTITION COMPARISON ---")
morph_r_sum = sum(abs(morph_tests[k]['r']) for k in morph_tests)
pos_r_sum = sum(abs(pos_tests[k]['r']) for k in pos_tests)
print(f"  Morphological partition: sum|r| = {morph_r_sum:.4f}")
print(f"  Positional partition:    sum|r| = {pos_r_sum:.4f}")
primary = 'MORPHOLOGICAL' if morph_r_sum > pos_r_sum else 'POSITIONAL'
print(f"  PRIMARY PARTITION: {primary}")

results['partition_comparison'] = {
    'morph_sum_r': round(morph_r_sum, 4),
    'pos_sum_r': round(pos_r_sum, 4),
    'primary': primary,
}

# ============================================================
# SECTION 3: PCA
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: PCA")
print("=" * 70)

# Build feature matrix from sr_features.json
feature_names = [
    'mean_position', 'initial_rate', 'final_rate',
    'regime_entropy', 'prefix_rate', 'suffix_rate',
    'mean_token_length', 'self_chain_rate',
]

# Add regime shares
regime_keys = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
# Add section shares
section_keys = ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']

all_feature_names = feature_names + [f'regime_{k}' for k in regime_keys] + [f'section_{k}' for k in section_keys]

fq_classes_sorted = sorted(FQ_CLASSES)
X = np.zeros((4, len(all_feature_names)))

for i, cls in enumerate(fq_classes_sorted):
    feat = sr_features[str(cls)]
    for j, fn in enumerate(feature_names):
        X[i, j] = feat[fn]
    for j, rk in enumerate(regime_keys):
        X[i, len(feature_names) + j] = feat['regime_shares'][rk]
    for j, sk in enumerate(section_keys):
        X[i, len(feature_names) + len(regime_keys) + j] = feat['section_shares'].get(sk, 0.0)

# Z-score normalize
means = X.mean(axis=0)
stds = X.std(axis=0)
stds[stds < 1e-10] = 1.0  # avoid division by zero
Z = (X - means) / stds

# PCA via covariance eigendecomposition
cov = np.cov(Z.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
# Sort descending
idx = eigenvalues.argsort()[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Variance explained
total_var = eigenvalues.sum()
var_explained = eigenvalues / total_var if total_var > 0 else eigenvalues
cumulative = np.cumsum(var_explained)

print(f"\nFeature matrix: {X.shape[0]} classes x {X.shape[1]} features")
print(f"\nVariance explained:")
for k in range(min(3, len(eigenvalues))):
    print(f"  PC{k+1}: {var_explained[k]*100:.1f}% (cumulative: {cumulative[k]*100:.1f}%)")

# PC1 loadings
print(f"\nPC1 loadings (top 5 by magnitude):")
pc1 = eigenvectors[:, 0]
loading_idx = np.argsort(np.abs(pc1))[::-1]
pc1_loadings = {}
for k in range(min(5, len(all_feature_names))):
    fi = loading_idx[k]
    print(f"  {all_feature_names[fi]:25s}: {pc1[fi]:+.4f}")
    pc1_loadings[all_feature_names[fi]] = round(float(pc1[fi]), 4)

# PC2 loadings
print(f"\nPC2 loadings (top 5 by magnitude):")
pc2 = eigenvectors[:, 1]
loading_idx2 = np.argsort(np.abs(pc2))[::-1]
pc2_loadings = {}
for k in range(min(5, len(all_feature_names))):
    fi = loading_idx2[k]
    print(f"  {all_feature_names[fi]:25s}: {pc2[fi]:+.4f}")
    pc2_loadings[all_feature_names[fi]] = round(float(pc2[fi]), 4)

# Project classes onto PC1/PC2
projections = Z @ eigenvectors[:, :2]
print(f"\nClass projections:")
for i, cls in enumerate(fq_classes_sorted):
    label = 'BARE' if cls in FQ_BARE else 'PREF'
    print(f"  Class {cls:2d} ({label}): PC1={projections[i,0]:+.3f}  PC2={projections[i,1]:+.3f}")

# Determine PC1 alignment
# Check if PC1 separates bare vs prefixed
bare_pc1 = [projections[i, 0] for i, c in enumerate(fq_classes_sorted) if c in FQ_BARE]
pref_pc1 = [projections[i, 0] for i, c in enumerate(fq_classes_sorted) if c in FQ_PREFIXED]
pc1_sep = abs(np.mean(bare_pc1) - np.mean(pref_pc1))

# Check if PC1 separates medial vs final
med_pc1 = [projections[i, 0] for i, c in enumerate(fq_classes_sorted) if c in FQ_MEDIAL]
fin_pc1 = [projections[i, 0] for i, c in enumerate(fq_classes_sorted) if c in FQ_FINAL]
pc1_pos_sep = abs(np.mean(med_pc1) - np.mean(fin_pc1))

pc1_aligns_with = 'MORPHOLOGY' if pc1_sep > pc1_pos_sep else 'POSITION'
print(f"\nPC1 alignment: {pc1_aligns_with} (morph_sep={pc1_sep:.3f}, pos_sep={pc1_pos_sep:.3f})")

results['pca'] = {
    'n_features': len(all_feature_names),
    'variance_explained': [round(float(v), 4) for v in var_explained[:3]],
    'cumulative': [round(float(c), 4) for c in cumulative[:3]],
    'pc1_loadings': pc1_loadings,
    'pc2_loadings': pc2_loadings,
    'projections': {str(cls): [round(float(projections[i, 0]), 4), round(float(projections[i, 1]), 4)]
                    for i, cls in enumerate(fq_classes_sorted)},
    'pc1_aligns_with': pc1_aligns_with,
    'morph_separation': round(float(pc1_sep), 4),
    'pos_separation': round(float(pc1_pos_sep), 4),
}

# ============================================================
# SECTION 4: WARD CLUSTERING
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: WARD CLUSTERING")
print("=" * 70)

# Distance matrix
dist_matrix = pdist(Z, metric='euclidean')
linkage_matrix = linkage(dist_matrix, method='ward')

# k=2
labels_k2 = fcluster(linkage_matrix, t=2, criterion='maxclust')
print(f"\nk=2 clustering:")
for i, cls in enumerate(fq_classes_sorted):
    print(f"  Class {cls}: cluster {labels_k2[i]}")

# Identify what k=2 recovers
cluster1 = {fq_classes_sorted[i] for i in range(4) if labels_k2[i] == 1}
cluster2 = {fq_classes_sorted[i] for i in range(4) if labels_k2[i] == 2}
k2_recovers_morph = (cluster1 == FQ_BARE and cluster2 == FQ_PREFIXED) or \
                    (cluster1 == FQ_PREFIXED and cluster2 == FQ_BARE)
k2_recovers_pos = (cluster1 == FQ_MEDIAL and cluster2 == FQ_FINAL) or \
                  (cluster1 == FQ_FINAL and cluster2 == FQ_MEDIAL)

print(f"  Cluster 1: {sorted(cluster1)}")
print(f"  Cluster 2: {sorted(cluster2)}")
print(f"  Recovers morphological split: {k2_recovers_morph}")
print(f"  Recovers positional split: {k2_recovers_pos}")

# Silhouette for k=2 (manual computation)
dist_sq = squareform(dist_matrix)
silhouettes_k2 = []
for i in range(4):
    my_cluster = labels_k2[i]
    same = [dist_sq[i, j] for j in range(4) if labels_k2[j] == my_cluster and j != i]
    diff = [dist_sq[i, j] for j in range(4) if labels_k2[j] != my_cluster]
    a = np.mean(same) if same else 0
    b = np.mean(diff) if diff else 0
    s = (b - a) / max(a, b) if max(a, b) > 0 else 0
    silhouettes_k2.append(s)
sil_k2 = np.mean(silhouettes_k2)
print(f"  Silhouette k=2: {sil_k2:.4f}")

# k=3
labels_k3 = fcluster(linkage_matrix, t=3, criterion='maxclust')
print(f"\nk=3 clustering:")
clusters_k3 = defaultdict(set)
for i, cls in enumerate(fq_classes_sorted):
    clusters_k3[labels_k3[i]].add(cls)
    print(f"  Class {cls}: cluster {labels_k3[i]}")

k3_recovers_trio = any(
    len(clusters_k3) == 3 and
    {9} in [clusters_k3[k] for k in clusters_k3] and
    {13, 14} in [clusters_k3[k] for k in clusters_k3] and
    {23} in [clusters_k3[k] for k in clusters_k3]
    for _ in [None]
)
print(f"  Recovers {{9}},{{13,14}},{{23}}: {k3_recovers_trio}")

# Silhouette for k=3
silhouettes_k3 = []
for i in range(4):
    my_cluster = labels_k3[i]
    same = [dist_sq[i, j] for j in range(4) if labels_k3[j] == my_cluster and j != i]
    diff = [dist_sq[i, j] for j in range(4) if labels_k3[j] != my_cluster]
    a = np.mean(same) if same else 0
    b = np.mean(diff) if diff else 0
    s = (b - a) / max(a, b) if max(a, b) > 0 else 0
    silhouettes_k3.append(s)
sil_k3 = np.mean(silhouettes_k3)
print(f"  Silhouette k=3: {sil_k3:.4f}")

results['clustering'] = {
    'k2': {
        'cluster_1': sorted(cluster1),
        'cluster_2': sorted(cluster2),
        'recovers_morph': k2_recovers_morph,
        'recovers_pos': k2_recovers_pos,
        'silhouette': round(float(sil_k2), 4),
    },
    'k3': {
        'clusters': {str(k): sorted(v) for k, v in clusters_k3.items()},
        'recovers_trio': k3_recovers_trio,
        'silhouette': round(float(sil_k3), 4),
    },
}

# ============================================================
# SECTION 5: 13-14 DEEP COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: 13-14 DEEP COMPARISON")
print("=" * 70)

# MIDDLE vocabulary comparison
class_middles = defaultdict(set)
class_tokens_by_class = defaultdict(list)

for (folio, line_id), line_tokens in lines.items():
    for tok in line_tokens:
        cls = tok['class']
        if cls in FQ_CLASSES:
            m = morph.extract(tok['word'])
            if m.middle:
                class_middles[cls].add(m.middle)
            class_tokens_by_class[cls].append(tok['word'])

m13 = class_middles[13]
m14 = class_middles[14]
shared = m13 & m14
jaccard_13_14 = len(shared) / len(m13 | m14) if (m13 | m14) else 0

print(f"\nClass 13 MIDDLEs ({len(m13)}): {sorted(m13)}")
print(f"Class 14 MIDDLEs ({len(m14)}): {sorted(m14)}")
print(f"Shared: {sorted(shared)}")
print(f"Jaccard(13,14) = {jaccard_13_14:.4f}")

# All FQ MIDDLEs
all_fq_middles = set()
for cls in FQ_CLASSES:
    all_fq_middles |= class_middles[cls]
print(f"\nAll FQ MIDDLEs ({len(all_fq_middles)}): {sorted(all_fq_middles)}")

# Per-class exclusive MIDDLEs
for cls in sorted(FQ_CLASSES):
    others = set()
    for c2 in FQ_CLASSES:
        if c2 != cls:
            others |= class_middles[c2]
    exclusive = class_middles[cls] - others
    print(f"  Class {cls} exclusive: {sorted(exclusive)} ({len(exclusive)})")

# Suffix comparison
f13 = sr_features['13']
f14 = sr_features['14']
print(f"\nSuffix comparison:")
print(f"  Class 13: suffix_rate={f13['suffix_rate']:.4f} (n={f13['n_tokens']})")
print(f"  Class 14: suffix_rate={f14['suffix_rate']:.4f} (n={f14['n_tokens']})")
# Chi-squared on suffix presence
# Class 13: 18.18% suffixed = ~216 suffixed, ~975 bare
# Class 14: 0% suffixed = 0 suffixed, 707 bare
n13_suf = round(f13['suffix_rate'] * f13['n_tokens'])
n13_bare = f13['n_tokens'] - n13_suf
n14_suf = round(f14['suffix_rate'] * f14['n_tokens'])
n14_bare = f14['n_tokens'] - n14_suf

contingency = np.array([[n13_suf, n13_bare], [n14_suf, n14_bare]])
if n13_suf > 0 and n14_suf == 0:
    # Fisher's exact since one cell is 0
    odds, p_suffix = stats.fisher_exact(contingency)
    test_type = 'fisher_exact'
else:
    chi2, p_suffix, dof, expected = stats.chi2_contingency(contingency)
    test_type = 'chi2'
print(f"  {test_type}: p={p_suffix:.2e}")
print(f"  Contingency: 13=[{n13_suf} suf, {n13_bare} bare], 14=[{n14_suf} suf, {n14_bare} bare]")

# Context profile comparison
print(f"\nContext profile comparison:")
ctx_keys = ['left_EN', 'right_EN', 'left_AX', 'right_AX', 'left_CC', 'right_CC',
            'left_FL', 'right_FL', 'left_FQ', 'right_FQ', 'left_UN', 'right_UN']

# JS divergence on context
ctx13 = np.array([f13['context_shares'].get(k, 0) for k in ctx_keys])
ctx14 = np.array([f14['context_shares'].get(k, 0) for k in ctx_keys])
ctx13_n = ctx13 / ctx13.sum() if ctx13.sum() > 0 else ctx13
ctx14_n = ctx14 / ctx14.sum() if ctx14.sum() > 0 else ctx14

# Manual JS divergence
m = (ctx13_n + ctx14_n) / 2
def kl(p, q):
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log2(p[mask] / q[mask]))
js_ctx = 0.5 * kl(ctx13_n, m) + 0.5 * kl(ctx14_n, m)

print(f"  JS divergence (context): {js_ctx:.6f}")

# Key context differences
print(f"  Key differences:")
for k in ctx_keys:
    v13 = f13['context_shares'].get(k, 0)
    v14 = f14['context_shares'].get(k, 0)
    diff = abs(v13 - v14)
    if diff > 0.03:
        print(f"    {k:10s}: 13={v13:.4f}  14={v14:.4f}  diff={diff:.4f}")

# Positional effect size (already from sr_internal)
pos_result = sr_internal['FQ']['role_specific']['class13_vs_14']
print(f"\nPositional separation (from sr_internal):")
print(f"  U={pos_result['U']:.0f}, p={pos_result['p']:.2e}")
print(f"  Mean 13={pos_result['mean_13']:.4f}, Mean 14={pos_result['mean_14']:.4f}")

# Regime/section divergence (from sr_internal)
js_13_14 = sr_internal['FQ']['js_divergence']['13-14']
print(f"\nDistributional divergence (from sr_internal):")
print(f"  JS regime: {js_13_14['regime']}")
print(f"  JS section: {js_13_14['section']}")

# Prefix distribution within 13 and 14
print(f"\nPrefix distribution:")
prefix_counts = defaultdict(lambda: Counter())
for (folio, line_id), line_tokens in lines.items():
    for tok in line_tokens:
        cls = tok['class']
        if cls in {13, 14}:
            m_result = morph.extract(tok['word'])
            prefix_counts[cls][m_result.prefix or 'NONE'] += 1

for cls in [13, 14]:
    total = sum(prefix_counts[cls].values())
    print(f"  Class {cls}:")
    for pfx, cnt in prefix_counts[cls].most_common():
        print(f"    {pfx}: {cnt} ({cnt/total*100:.1f}%)")

results['comparison_13_14'] = {
    'middle_jaccard': round(jaccard_13_14, 4),
    'middles_13': sorted(m13),
    'middles_14': sorted(m14),
    'middles_shared': sorted(shared),
    'suffix_test': test_type,
    'suffix_p': float(p_suffix),
    'suffix_13': round(f13['suffix_rate'], 4),
    'suffix_14': round(f14['suffix_rate'], 4),
    'context_js': round(float(js_ctx), 6),
    'positional_p': pos_result['p'],
    'mean_13': pos_result['mean_13'],
    'mean_14': pos_result['mean_14'],
    'js_regime': js_13_14['regime'],
    'js_section': js_13_14['section'],
    'prefix_dist_13': dict(prefix_counts[13]),
    'prefix_dist_14': dict(prefix_counts[14]),
}

# ============================================================
# SECTION 6: SUB-GROUP VERDICT
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: SUB-GROUP VERDICT")
print("=" * 70)

# Score candidates
candidates = {}

# 2-group morphological
morph_sig = sum(1 for v in morph_tests.values() if v['significant'])
candidates['2G_MORPHOLOGICAL'] = {
    'groups': [sorted(FQ_BARE), sorted(FQ_PREFIXED)],
    'labels': ['BARE', 'PREFIXED'],
    'sig_features': morph_sig,
    'sum_r': morph_r_sum,
    'hazard_aligned': morph_hazard_overlap,
    'cluster_aligned': k2_recovers_morph,
}

# 2-group positional
pos_sig = sum(1 for v in pos_tests.values() if v['significant'])
candidates['2G_POSITIONAL'] = {
    'groups': [sorted(FQ_MEDIAL), sorted(FQ_FINAL)],
    'labels': ['MEDIAL', 'FINAL'],
    'sig_features': pos_sig,
    'sum_r': pos_r_sum,
    'hazard_aligned': False,
    'cluster_aligned': k2_recovers_pos,
}

# 3-group
candidates['3G_TRIO'] = {
    'groups': [[9], [13, 14], [23]],
    'labels': ['CONNECTOR', 'PREFIXED_PAIR', 'CLOSER'],
    'cluster_aligned': k3_recovers_trio,
    'silhouette': sil_k3,
}

# Determine winner
print(f"\nCandidate scores:")
for name, c in candidates.items():
    sr = c.get('sum_r')
    sr_str = f"{sr:.4f}" if sr is not None else 'N/A'
    print(f"  {name}: sig={c.get('sig_features','?')}, sum_r={sr_str}, "
          f"hazard={c.get('hazard_aligned','?')}, cluster={c.get('cluster_aligned','?')}")

# Decision: prefer morphological if it has hazard alignment and cluster support
if candidates['2G_MORPHOLOGICAL']['hazard_aligned'] and candidates['2G_MORPHOLOGICAL']['cluster_aligned']:
    verdict = '2G_MORPHOLOGICAL'
    verdict_desc = 'BARE/PREFIXED with perfect hazard alignment'
elif candidates['2G_MORPHOLOGICAL']['sum_r'] > candidates['2G_POSITIONAL']['sum_r']:
    verdict = '2G_MORPHOLOGICAL'
    verdict_desc = 'BARE/PREFIXED (stronger feature separation)'
elif candidates['2G_POSITIONAL']['sum_r'] > candidates['2G_MORPHOLOGICAL']['sum_r']:
    verdict = '2G_POSITIONAL'
    verdict_desc = 'MEDIAL/FINAL (stronger feature separation)'
else:
    verdict = '3G_TRIO'
    verdict_desc = 'Three-way split'

# Check if 3-group is better than both 2-groups
if sil_k3 > sil_k2 and k3_recovers_trio:
    verdict = '3G_TRIO'
    verdict_desc = 'Three-way split (better silhouette and interpretive coherence)'

print(f"\n  VERDICT: {verdict}")
print(f"  Description: {verdict_desc}")
print(f"  Primary dimension: {primary}")
print(f"  Secondary dimension: {'POSITION' if primary == 'MORPHOLOGICAL' else 'MORPHOLOGY'}")

results['verdict'] = {
    'winner': verdict,
    'description': verdict_desc,
    'primary_dimension': primary,
    'candidates': candidates,
    'silhouette_k2': round(float(sil_k2), 4),
    'silhouette_k3': round(float(sil_k3), 4),
}

# Save results
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'fq_structural_anatomy.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'fq_structural_anatomy.json'}")
