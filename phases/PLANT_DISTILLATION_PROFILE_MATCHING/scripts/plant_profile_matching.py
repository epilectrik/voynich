"""
Phase 436: PLANT_DISTILLATION_PROFILE_MATCHING
================================================
Tests whether the dimensions that separate plant distillation profiles
match the dimensions that separate Voynich folio operational profiles.
Also tests: material-specific vs category-level fit.
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

PLANT_PATH = ROOT / 'phases' / 'PLANT_DISTILLATION_PROFILE_MATCHING' / 'data' / 'plant_profiles.json'
REGIME_PATH = ROOT / 'data' / 'regime_folio_mapping.json'
RESULTS_DIR = ROOT / 'phases' / 'PLANT_DISTILLATION_PROFILE_MATCHING' / 'results'
RESULTS_PATH = RESULTS_DIR / 'plant_matching_results.json'

ATOM_TO_AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
}
AXES = ['ENERGY', 'STABILITY', 'MONITORING', 'ITERATION', 'CLOSURE', 'STRUCTURAL', 'FREE']
MIN_FOLIO_CHARS = 50


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def variance_entropy(explained_ratios):
    ent = 0.0
    for r in explained_ratios:
        if r > 0:
            ent -= r * math.log2(r)
    return ent


def n_for_threshold(explained_ratios, threshold=0.80):
    cum = 0.0
    for i, r in enumerate(explained_ratios):
        cum += r
        if cum >= threshold:
            return i + 1
    return len(explained_ratios)


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def run_pca_generic(matrix, feature_names, label):
    n_samples, n_features = matrix.shape
    n_components = min(n_samples, n_features)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    pca = PCA(n_components=n_components)
    pca.fit(scaled)
    explained = pca.explained_variance_ratio_
    n80 = n_for_threshold(explained, 0.80)
    n90 = n_for_threshold(explained, 0.90)
    entropy = variance_entropy(explained)
    return {
        'label': label,
        'n_samples': n_samples,
        'n_features': n_features,
        'n_for_80': n80,
        'n_for_90': n90,
        'entropy': round(entropy, 3),
        'explained_variance': [round(float(v), 4) for v in explained],
        'cumulative_variance': [round(float(v), 4) for v in np.cumsum(explained)],
        'pc_loadings': {
            f'PC{i+1}': {feature_names[j]: round(float(pca.components_[i][j]), 3)
                         for j in range(n_features)}
            for i in range(min(n80 + 2, len(pca.components_)))
        },
        'components_raw': pca.components_[:min(n80 + 2, len(pca.components_))].tolist(),
    }


# =====================================================================
# STEP 1: BUILD FOLIO AXIS PROFILES
# =====================================================================
print("PLANT DISTILLATION PROFILE MATCHING")
print("=" * 70)
print("\nStep 1: Building per-folio axis profiles from Voynich data...")

tx = Transcript()
morph = Morphology()

# Pre-compute per-folio atom character counts
folio_chars = defaultdict(lambda: Counter())
folio_total = defaultdict(int)
folio_sections = {}

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m.middle:
        for ch in m.middle:
            if ch in ATOM_TO_AXIS:
                folio_chars[t.folio][ATOM_TO_AXIS[ch]] += 1
                folio_total[t.folio] += 1
    if t.folio not in folio_sections:
        folio_sections[t.folio] = t.section if hasattr(t, 'section') else 'UNK'

# Load regime assignments
with open(REGIME_PATH) as f:
    regime_raw = json.load(f)
regime_data = regime_raw.get('regime_assignments', regime_raw)

# Build folio profile matrix
valid_folios = sorted([f for f in folio_total if folio_total[f] >= MIN_FOLIO_CHARS])
print(f"  Folios with {MIN_FOLIO_CHARS}+ mapped chars: {len(valid_folios)}")

folio_profiles = {}
folio_matrix_rows = []
for folio in valid_folios:
    profile = {ax: folio_chars[folio][ax] / folio_total[folio] for ax in AXES}
    regime = regime_data.get(folio, {}).get('regime', 'UNK') if isinstance(regime_data, dict) else 'UNK'
    section = folio_sections.get(folio, 'UNK')
    folio_profiles[folio] = {
        **profile,
        'section': section,
        'regime': regime,
        'n_chars': folio_total[folio],
    }
    folio_matrix_rows.append([profile[ax] for ax in AXES])

folio_matrix = np.array(folio_matrix_rows)
print(f"  Folio matrix: {folio_matrix.shape}")

# Print axis means
print(f"\n  {'Axis':<12} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print(f"  {'----':<12} {'----':>8} {'---':>8} {'---':>8} {'---':>8}")
for j, ax in enumerate(AXES):
    col = folio_matrix[:, j]
    print(f"  {ax:<12} {np.mean(col):>7.1%} {np.std(col):>7.1%} {np.min(col):>7.1%} {np.max(col):>7.1%}")

# =====================================================================
# STEP 2: LOAD AND NORMALIZE PLANT PROFILES
# =====================================================================
print(f"\n{'=' * 70}")
print("Step 2: Loading plant distillation profiles...")

with open(PLANT_PATH) as f:
    plant_data = json.load(f)

plants = plant_data['plants']
print(f"  Plants loaded: {len(plants)}")

# Normalize scores to proportions (same simplex as folio profiles)
plant_profiles = {}
plant_matrix_rows = []
plant_names = []
plant_categories = {}

for p in plants:
    scores = p['scores']
    total = sum(scores[ax] for ax in AXES)
    if total == 0:
        continue
    profile = {ax: scores[ax] / total for ax in AXES}
    plant_profiles[p['name']] = profile
    plant_matrix_rows.append([profile[ax] for ax in AXES])
    plant_names.append(p['name'])
    plant_categories[p['name']] = p['category']

plant_matrix = np.array(plant_matrix_rows)
print(f"  Plant matrix: {plant_matrix.shape}")

# Category summary
categories = sorted(set(plant_categories.values()))
print(f"  Categories: {', '.join(categories)}")
for cat in categories:
    members = [n for n in plant_names if plant_categories[n] == cat]
    print(f"    {cat}: {len(members)} ({', '.join(members)})")

# Print plant axis means
print(f"\n  {'Axis':<12} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
print(f"  {'----':<12} {'----':>8} {'---':>8} {'---':>8} {'---':>8}")
for j, ax in enumerate(AXES):
    col = plant_matrix[:, j]
    print(f"  {ax:<12} {np.mean(col):>7.1%} {np.std(col):>7.1%} {np.min(col):>7.1%} {np.max(col):>7.1%}")

# =====================================================================
# T1: PLANT PCA
# =====================================================================
print(f"\n{'=' * 70}")
print("T1: PLANT PCA — What dimensions separate plants?")
print("=" * 70)

pca_plant = run_pca_generic(plant_matrix, AXES, 'Plants')

print(f"\n  n_for_80%: {pca_plant['n_for_80']}")
print(f"  Entropy: {pca_plant['entropy']} bits")

for pc_name, loadings in pca_plant['pc_loadings'].items():
    pc_idx = int(pc_name[2:]) - 1
    var_pct = pca_plant['explained_variance'][pc_idx] * 100
    print(f"\n  {pc_name} ({var_pct:.1f}% variance):")
    sorted_loads = sorted(loadings.items(), key=lambda x: -abs(x[1]))
    for feat, load in sorted_loads:
        bar = '+' * int(abs(load) * 20) if load > 0 else '-' * int(abs(load) * 20)
        print(f"    {feat:<12} {load:>+7.3f}  {bar}")

# =====================================================================
# T2: FOLIO PCA
# =====================================================================
print(f"\n{'=' * 70}")
print("T2: FOLIO PCA — What dimensions separate folios?")
print("=" * 70)

pca_folio = run_pca_generic(folio_matrix, AXES, 'Folios')

print(f"\n  n_for_80%: {pca_folio['n_for_80']}")
print(f"  Entropy: {pca_folio['entropy']} bits")

for pc_name, loadings in pca_folio['pc_loadings'].items():
    pc_idx = int(pc_name[2:]) - 1
    var_pct = pca_folio['explained_variance'][pc_idx] * 100
    print(f"\n  {pc_name} ({var_pct:.1f}% variance):")
    sorted_loads = sorted(loadings.items(), key=lambda x: -abs(x[1]))
    for feat, load in sorted_loads:
        bar = '+' * int(abs(load) * 20) if load > 0 else '-' * int(abs(load) * 20)
        print(f"    {feat:<12} {load:>+7.3f}  {bar}")

# =====================================================================
# T3: PC ALIGNMENT
# =====================================================================
print(f"\n{'=' * 70}")
print("T3: PC ALIGNMENT — Do plant-separating dimensions match folio-separating?")
print("=" * 70)

n_compare = min(len(pca_plant['components_raw']), len(pca_folio['components_raw']))
plant_comps = np.array(pca_plant['components_raw'][:n_compare])
folio_comps = np.array(pca_folio['components_raw'][:n_compare])

# Best-match alignment: for each plant PC, find most similar folio PC
# Use absolute cosine (PCs can be sign-flipped)
alignment_matrix = np.zeros((n_compare, n_compare))
for i in range(n_compare):
    for j in range(n_compare):
        alignment_matrix[i, j] = abs(cosine_similarity(plant_comps[i], folio_comps[j]))

print(f"\n  Alignment matrix (|cosine| between plant PC_i and folio PC_j):")
print(f"  {'':>10}", end='')
for j in range(n_compare):
    print(f"  Folio_PC{j+1}", end='')
print()
for i in range(n_compare):
    print(f"  Plant_PC{i+1}", end='')
    for j in range(n_compare):
        val = alignment_matrix[i, j]
        marker = ' *' if val == alignment_matrix[i].max() else '  '
        print(f"  {val:>8.3f}{marker}", end='')
    print()

# Greedy best-match alignment
used_folio = set()
aligned_pairs = []
for _ in range(n_compare):
    best_val = -1
    best_i, best_j = -1, -1
    for i in range(n_compare):
        if any(p[0] == i for p in aligned_pairs):
            continue
        for j in range(n_compare):
            if j in used_folio:
                continue
            if alignment_matrix[i, j] > best_val:
                best_val = alignment_matrix[i, j]
                best_i, best_j = i, j
    aligned_pairs.append((best_i, best_j, best_val))
    used_folio.add(best_j)

print(f"\n  Best-match alignment:")
for pi, fi, cos in sorted(aligned_pairs):
    pvar = pca_plant['explained_variance'][pi] * 100
    fvar = pca_folio['explained_variance'][fi] * 100
    print(f"    Plant_PC{pi+1} ({pvar:.1f}%) <-> Folio_PC{fi+1} ({fvar:.1f}%):  |cosine| = {cos:.3f}")

mean_cosine = np.mean([c for _, _, c in aligned_pairs])
print(f"\n  Mean aligned |cosine|: {mean_cosine:.3f}")

# Permutation null test
n_perms = 1000
null_cosines = []
for _ in range(n_perms):
    shuffled = plant_matrix[np.random.permutation(len(plant_matrix))]
    pca_shuf = run_pca_generic(shuffled, AXES, 'shuffle')
    shuf_comps = np.array(pca_shuf['components_raw'][:n_compare])
    # Best-match alignment with folio PCs
    shuf_align = np.zeros((n_compare, n_compare))
    for i in range(n_compare):
        for j in range(n_compare):
            shuf_align[i, j] = abs(cosine_similarity(shuf_comps[i], folio_comps[j]))
    # Greedy alignment
    used = set()
    pairs = []
    for _ in range(n_compare):
        bv, bi, bj = -1, -1, -1
        for i in range(n_compare):
            if any(p[0] == i for p in pairs):
                continue
            for j in range(n_compare):
                if j in used:
                    continue
                if shuf_align[i, j] > bv:
                    bv, bi, bj = shuf_align[i, j], i, j
        pairs.append((bi, bj, bv))
        used.add(bj)
    null_cosines.append(np.mean([c for _, _, c in pairs]))

null_mean = np.mean(null_cosines)
null_std = np.std(null_cosines)
p_value = np.mean([nc >= mean_cosine for nc in null_cosines])

print(f"\n  Permutation null (n={n_perms}):")
print(f"    Null mean |cosine|: {null_mean:.3f} +/- {null_std:.3f}")
print(f"    Observed:           {mean_cosine:.3f}")
print(f"    p-value:            {p_value:.4f}")

if p_value < 0.05:
    print(f"    --> SIGNIFICANT: Plant and folio PCs are aligned beyond chance")
else:
    print(f"    --> NOT SIGNIFICANT: Alignment could arise by chance")

# =====================================================================
# T4: CATEGORY vs MATERIAL FIT
# =====================================================================
print(f"\n{'=' * 70}")
print("T4: CATEGORY vs MATERIAL FIT")
print("=" * 70)

# Category centroids
category_centroids = {}
for cat in categories:
    members = [i for i, n in enumerate(plant_names) if plant_categories[n] == cat]
    category_centroids[cat] = np.mean(plant_matrix[members], axis=0)

# For each folio, compute distances
folio_plant_distances = {}
folio_category_distances = {}
material_dists_all = []
category_dists_all = []

for fi, folio in enumerate(valid_folios):
    fvec = folio_matrix[fi]

    # Distance to each plant
    plant_dists = {}
    for pi, pname in enumerate(plant_names):
        d = np.linalg.norm(fvec - plant_matrix[pi])
        plant_dists[pname] = round(float(d), 4)

    nearest_plant = min(plant_dists, key=plant_dists.get)
    nearest_plant_dist = plant_dists[nearest_plant]

    # Distance to each category centroid
    cat_dists = {}
    for cat, centroid in category_centroids.items():
        d = np.linalg.norm(fvec - centroid)
        cat_dists[cat] = round(float(d), 4)

    nearest_cat = min(cat_dists, key=cat_dists.get)
    nearest_cat_dist = cat_dists[nearest_cat]

    folio_plant_distances[folio] = {
        'nearest_plant': nearest_plant,
        'nearest_plant_category': plant_categories[nearest_plant],
        'nearest_plant_dist': nearest_plant_dist,
        'nearest_category': nearest_cat,
        'nearest_category_dist': nearest_cat_dist,
    }

    material_dists_all.append(nearest_plant_dist)
    category_dists_all.append(nearest_cat_dist)

mean_material_dist = np.mean(material_dists_all)
mean_category_dist = np.mean(category_dists_all)

print(f"\n  Mean distance to nearest plant:    {mean_material_dist:.4f}")
print(f"  Mean distance to nearest category: {mean_category_dist:.4f}")
print(f"  Ratio (category/material):         {mean_category_dist/mean_material_dist:.2f}")

if mean_material_dist < mean_category_dist:
    print(f"  --> Material-specific fit is tighter (expected — more degrees of freedom)")
else:
    print(f"  --> Category-level fit is tighter")

# Category assignment distribution
cat_counts = Counter()
for folio in valid_folios:
    cat_counts[folio_plant_distances[folio]['nearest_category']] += 1

print(f"\n  Folio -> nearest category distribution:")
for cat in sorted(cat_counts, key=cat_counts.get, reverse=True):
    print(f"    {cat:10s}: {cat_counts[cat]:3d} folios ({cat_counts[cat]/len(valid_folios):.0%})")

# Regime × category cross-tabulation
print(f"\n  Regime × nearest-category cross-tabulation:")
regime_cat = defaultdict(Counter)
for folio in valid_folios:
    regime = folio_profiles[folio].get('regime', 'UNK')
    cat = folio_plant_distances[folio]['nearest_category']
    regime_cat[regime][cat] += 1

regimes = sorted(regime_cat.keys())
top_cats = sorted(cat_counts, key=cat_counts.get, reverse=True)[:6]
print(f"  {'':>12}", end='')
for cat in top_cats:
    print(f"  {cat:>8s}", end='')
print()
for reg in regimes:
    print(f"  {reg:>12}", end='')
    for cat in top_cats:
        print(f"  {regime_cat[reg][cat]:>8d}", end='')
    print()

# Section × category cross-tabulation
print(f"\n  Section × nearest-category cross-tabulation:")
section_cat = defaultdict(Counter)
for folio in valid_folios:
    section = folio_profiles[folio].get('section', 'UNK')
    cat = folio_plant_distances[folio]['nearest_category']
    section_cat[section][cat] += 1

sections = sorted(section_cat.keys())
print(f"  {'':>12}", end='')
for cat in top_cats:
    print(f"  {cat:>8s}", end='')
print()
for sec in sections:
    print(f"  {sec:>12}", end='')
    for cat in top_cats:
        print(f"  {section_cat[sec][cat]:>8d}", end='')
    print()

# =====================================================================
# T5: SECTION CONFOUND CONTROL
# =====================================================================
print(f"\n{'=' * 70}")
print("T5: SECTION CONFOUND CONTROL")
print("=" * 70)

# Compute section centroids
section_labels = [folio_profiles[f]['section'] for f in valid_folios]
unique_sections = sorted(set(section_labels))
section_centroids = {}
for sec in unique_sections:
    idxs = [i for i, s in enumerate(section_labels) if s == sec]
    section_centroids[sec] = np.mean(folio_matrix[idxs], axis=0)

# Model A: section centroids predict folio profiles
section_predicted = np.array([section_centroids[section_labels[i]] for i in range(len(valid_folios))])
ss_total = np.sum((folio_matrix - np.mean(folio_matrix, axis=0)) ** 2)
ss_residual_section = np.sum((folio_matrix - section_predicted) ** 2)
r2_section = 1 - ss_residual_section / ss_total

print(f"\n  Sections found: {unique_sections}")
print(f"  Model A (section only): R² = {r2_section:.4f}")

# Model B: section + nearest category centroid
# For each folio, use section centroid + category centroid (averaged)
cat_assignments = [folio_plant_distances[f]['nearest_category'] for f in valid_folios]
unique_cats = sorted(set(cat_assignments))

# Section × category interaction centroids
sec_cat_centroids = {}
for sec in unique_sections:
    for cat in unique_cats:
        idxs = [i for i in range(len(valid_folios))
                if section_labels[i] == sec and cat_assignments[i] == cat]
        if idxs:
            sec_cat_centroids[(sec, cat)] = np.mean(folio_matrix[idxs], axis=0)

# Predict using section×category interaction (if available, else section-only)
seccat_predicted = []
for i in range(len(valid_folios)):
    key = (section_labels[i], cat_assignments[i])
    if key in sec_cat_centroids:
        seccat_predicted.append(sec_cat_centroids[key])
    else:
        seccat_predicted.append(section_centroids[section_labels[i]])
seccat_predicted = np.array(seccat_predicted)

ss_residual_seccat = np.sum((folio_matrix - seccat_predicted) ** 2)
r2_seccat = 1 - ss_residual_seccat / ss_total

partial_r2 = (ss_residual_section - ss_residual_seccat) / ss_residual_section

print(f"  Model B (section + category): R² = {r2_seccat:.4f}")
print(f"  Partial R² (category | section): {partial_r2:.4f}")
print(f"  Category adds {partial_r2:.1%} of remaining variance beyond section")

if partial_r2 > 0.05:
    print(f"  --> Category adds meaningful signal beyond section")
else:
    print(f"  --> Category adds minimal signal beyond section")

# =====================================================================
# OVERALL VERDICT
# =====================================================================
print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

print(f"\n  T1 Plant PCA:         {pca_plant['n_for_80']} PCs for 80%, entropy {pca_plant['entropy']} bits")
print(f"  T2 Folio PCA:         {pca_folio['n_for_80']} PCs for 80%, entropy {pca_folio['entropy']} bits")
print(f"  T3 PC Alignment:      mean |cosine| = {mean_cosine:.3f}, p = {p_value:.4f}")
print(f"  T4 Material/Category: material dist {mean_material_dist:.4f}, category dist {mean_category_dist:.4f}")
print(f"  T5 Section confound:  section R² = {r2_section:.4f}, +category R² = {r2_seccat:.4f}, partial = {partial_r2:.4f}")

# =====================================================================
# SAVE RESULTS
# =====================================================================
results = {
    'folio_profiles': folio_profiles,
    'plant_profiles_normalized': plant_profiles,
    'plant_categories': plant_categories,
    'T1_plant_pca': pca_plant,
    'T2_folio_pca': pca_folio,
    'T3_pc_alignment': {
        'alignment_matrix': alignment_matrix.tolist(),
        'aligned_pairs': [{'plant_pc': pi+1, 'folio_pc': fi+1, 'cosine': round(c, 4)}
                          for pi, fi, c in sorted(aligned_pairs)],
        'mean_cosine': round(mean_cosine, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'p_value': round(p_value, 4),
    },
    'T4_plant_folio_matching': {
        'per_folio': folio_plant_distances,
        'mean_material_dist': round(mean_material_dist, 4),
        'mean_category_dist': round(mean_category_dist, 4),
        'category_distribution': dict(cat_counts),
    },
    'T5_section_confound': {
        'r2_section_only': round(r2_section, 4),
        'r2_section_plus_category': round(r2_seccat, 4),
        'partial_r2_category': round(partial_r2, 4),
    },
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_PATH}")
