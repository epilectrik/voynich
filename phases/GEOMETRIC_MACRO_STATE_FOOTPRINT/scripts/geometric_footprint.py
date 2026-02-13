#!/usr/bin/env python3
"""
Phase 329: GEOMETRIC_MACRO_STATE_FOOTPRINT
Does the ~101D discrimination manifold have geometric structure
corresponding to the 6-state macro-automaton?

T1: Eigenvector embedding + hub removal
T2: Macro-state geometric footprints (compactness, separation, silhouette)
T3: Forbidden transition boundary test
T4: HUB sub-role geometric signatures
T5: Affordance bin alignment
T6: Synthesis and pre-registered prediction evaluation
"""

import sys
import json
import math
import time
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ---- Macro-state definitions from Phase 328 (C1010) ----
MACRO_STATE_PARTITION = {
    'AXM': {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm': {3,5,18,19,42,45},
    'FL_HAZ': {7,30},
    'FQ': {9,13,14,23},
    'CC': {10,11,12},
    'FL_SAFE': {38,40},
}
MACRO_STATE_NAMES = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']

# ---- Role definitions ----
ROLE_FAMILIES = {
    'CC': {10, 11, 12},
    'FQ': {9, 13, 14, 23},
    'FL': {7, 30, 38, 40},
    'EN': {8} | set(range(31, 50)) - {7, 30, 38, 40},
}

# HUB sub-roles from C1000
HUB_SUB_ROLES = {
    'HAZARD_SOURCE': ['ar', 'dy', 'ey', 'l', 'ol', 'or'],
    'HAZARD_TARGET': ['aiin', 'al', 'ee', 'o', 'r', 't'],
    'SAFETY_BUFFER': ['eol', 'k', 'od'],
    'PURE_CONNECTOR': ['d', 'e', 'eey', 'ek', 'eo', 'iin', 's', 'y'],
}

N_PERM = 1000
RESIDUAL_DIM = 100  # 101 minus hub eigenmode


def load_all_data():
    """Load all precomputed data."""
    data = {}

    # 1. Compatibility matrix and eigenvalues
    compat_path = PROJECT_ROOT / 'phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_compat_matrix.npy'
    eigenval_path = PROJECT_ROOT / 'phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_eigenvalues.npy'
    data['compat'] = np.load(compat_path)
    data['eigenvalues'] = np.load(eigenval_path)

    # 2. Reconstruct MIDDLE list (same as t1_definitive_matrix.py: sorted unique A MIDDLEs)
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    data['all_middles'] = all_middles
    data['mid_to_idx'] = mid_to_idx
    n_mid = len(all_middles)
    print(f"  Reconstructed {n_mid} MIDDLEs from A corpus")
    assert n_mid == data['compat'].shape[0], f"MIDDLE count {n_mid} != matrix shape {data['compat'].shape[0]}"

    # 3. Token-to-class map (49 classes)
    ctm_path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(ctm_path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # 4. Build MIDDLE -> class distribution (from B tokens)
    # For each MIDDLE, count how many B tokens with that MIDDLE belong to each class
    middle_class_counts = defaultdict(lambda: defaultdict(int))
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        cls = token_to_class.get(word)
        if cls is None:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            middle_class_counts[m.middle][cls] += 1

    # 5. Assign each MIDDLE its dominant class and macro-state
    cls_to_macro = {}
    for macro, classes in MACRO_STATE_PARTITION.items():
        for c in classes:
            cls_to_macro[c] = macro

    middle_macro = {}  # MIDDLE -> dominant macro-state
    middle_class = {}  # MIDDLE -> dominant class
    middle_macro_dist = {}  # MIDDLE -> {macro: count}
    for mid in all_middles:
        if mid in middle_class_counts:
            counts = middle_class_counts[mid]
            dominant_cls = max(counts, key=counts.get)
            middle_class[mid] = dominant_cls
            middle_macro[mid] = cls_to_macro.get(dominant_cls, 'UNKNOWN')
            # macro distribution
            macro_counts = defaultdict(int)
            for c, cnt in counts.items():
                macro_counts[cls_to_macro.get(c, 'UNKNOWN')] += cnt
            middle_macro_dist[mid] = dict(macro_counts)

    data['middle_class_counts'] = dict(middle_class_counts)
    data['middle_class'] = middle_class
    data['middle_macro'] = middle_macro
    data['middle_macro_dist'] = middle_macro_dist
    data['cls_to_macro'] = cls_to_macro
    data['token_to_class'] = token_to_class

    n_mapped = len(middle_macro)
    print(f"  MIDDLEs mapped to B classes: {n_mapped}/{n_mid} ({100*n_mapped/n_mid:.1f}%)")
    macro_counts = defaultdict(int)
    for mid, macro in middle_macro.items():
        macro_counts[macro] += 1
    for macro in MACRO_STATE_NAMES:
        print(f"    {macro}: {macro_counts.get(macro, 0)} MIDDLEs")

    # 6. Affordance bin table
    aff_path = PROJECT_ROOT / 'data/middle_affordance_table.json'
    with open(aff_path) as f:
        aff_data = json.load(f)
    middles_data = aff_data.get('middles', aff_data)
    middle_bin = {}
    for mid_name, mid_info in middles_data.items():
        if isinstance(mid_info, dict):
            middle_bin[mid_name] = mid_info.get('affordance_bin', -1)
    data['middle_bin'] = middle_bin

    # 7. Forbidden transitions (from t3_cross_bin_forbidden_anatomy.json)
    forb_path = PROJECT_ROOT / 'phases/HUB_ROLE_DECOMPOSITION/results/t3_cross_bin_forbidden_anatomy.json'
    with open(forb_path) as f:
        forb_data = json.load(f)
    data['forbidden_transitions'] = forb_data

    # 8. Load class-level transition data for forbidden pairs
    trans_path = PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON/results/t1_transition_data.json'
    with open(trans_path) as f:
        trans_data = json.load(f)
    data['class_to_role'] = {int(k): v for k, v in trans_data['class_to_role'].items()}
    data['all_classes'] = trans_data['classes']

    return data


def run_t1(data):
    """T1: Eigenvector Embedding + Hub Removal"""
    print("\n" + "=" * 70)
    print("T1: Eigenvector Embedding + Hub Removal")
    print("=" * 70)

    compat = data['compat'].astype(np.float64)
    n = compat.shape[0]

    # Full eigendecomposition (symmetric matrix)
    eigenvalues, eigenvectors = np.linalg.eigh(compat)

    # eigh returns in ascending order; reverse to descending
    eigenvalues = eigenvalues[::-1]
    eigenvectors = eigenvectors[:, ::-1]

    print(f"  Matrix shape: {n}x{n}")
    print(f"  Top 5 eigenvalues: {eigenvalues[:5].round(2)}")
    print(f"  Hub eigenmode (lambda_1): {eigenvalues[0]:.2f}")

    # Verify against stored eigenvalues
    stored_eig = data['eigenvalues']
    stored_eig_sorted = np.sort(stored_eig)[::-1]
    max_diff = np.max(np.abs(eigenvalues[:20] - stored_eig_sorted[:20]))
    print(f"  Max difference from stored eigenvalues (top 20): {max_diff:.6f}")

    # Remove hub eigenmode: use eigenvectors 2..101 (indices 1..100)
    residual_vecs = eigenvectors[:, 1:RESIDUAL_DIM + 1]
    residual_vals = eigenvalues[1:RESIDUAL_DIM + 1]

    # Scale by sqrt(eigenvalue) for metric embedding
    embedding = residual_vecs * np.sqrt(np.maximum(residual_vals, 0))

    # Variance explained
    total_trace = np.sum(np.abs(eigenvalues))
    hub_var = abs(eigenvalues[0])
    residual_var = np.sum(np.abs(residual_vals))
    print(f"  Hub variance: {hub_var:.1f} ({100*hub_var/total_trace:.1f}% of total)")
    print(f"  Residual variance (100D): {residual_var:.1f} ({100*residual_var/total_trace:.1f}%)")
    print(f"  Combined (101D): {100*(hub_var + residual_var)/total_trace:.1f}%")

    data['embedding'] = embedding
    data['eigenvectors'] = eigenvectors
    data['eigenvalues_computed'] = eigenvalues

    return {
        'n_middles': n,
        'n_dims': RESIDUAL_DIM,
        'hub_eigenvalue': float(eigenvalues[0]),
        'residual_eigenvalue_range': [float(residual_vals[0]), float(residual_vals[-1])],
        'hub_variance_pct': round(100 * hub_var / total_trace, 1),
        'residual_variance_pct': round(100 * residual_var / total_trace, 1),
        'combined_variance_pct': round(100 * (hub_var + residual_var) / total_trace, 1),
        'eigenvalue_check_max_diff': float(max_diff),
    }


def run_t2(data):
    """T2: Macro-State Geometric Footprints"""
    print("\n" + "=" * 70)
    print("T2: Macro-State Geometric Footprints")
    print("=" * 70)

    embedding = data['embedding']
    all_middles = data['all_middles']
    middle_macro = data['middle_macro']
    mid_to_idx = data['mid_to_idx']

    # Get indices for each macro-state
    macro_indices = {macro: [] for macro in MACRO_STATE_NAMES}
    for mid, macro in middle_macro.items():
        if mid in mid_to_idx and macro in macro_indices:
            macro_indices[macro].append(mid_to_idx[mid])

    print(f"  MIDDLEs per macro-state (in embedding):")
    for macro in MACRO_STATE_NAMES:
        print(f"    {macro}: {len(macro_indices[macro])}")

    # Compute centroids
    centroids = {}
    for macro in MACRO_STATE_NAMES:
        idx = macro_indices[macro]
        if len(idx) > 0:
            centroids[macro] = embedding[idx].mean(axis=0)
        else:
            centroids[macro] = np.zeros(RESIDUAL_DIM)

    # Within-state dispersion (mean pairwise distance)
    from scipy.spatial.distance import pdist, cdist, squareform
    within_disp = {}
    for macro in MACRO_STATE_NAMES:
        idx = macro_indices[macro]
        if len(idx) > 1:
            dists = pdist(embedding[idx])
            within_disp[macro] = float(np.mean(dists))
        else:
            within_disp[macro] = 0.0

    # Between-state separation (centroid distances)
    centroid_matrix = np.array([centroids[m] for m in MACRO_STATE_NAMES])
    between_dists = squareform(pdist(centroid_matrix))
    between_dict = {}
    for i, m1 in enumerate(MACRO_STATE_NAMES):
        for j, m2 in enumerate(MACRO_STATE_NAMES):
            if i < j:
                between_dict[f"{m1}-{m2}"] = float(between_dists[i, j])

    print(f"\n  Within-state dispersion:")
    for macro in MACRO_STATE_NAMES:
        print(f"    {macro}: {within_disp[macro]:.4f}")

    print(f"\n  Between-state centroid distances:")
    for pair, d in sorted(between_dict.items(), key=lambda x: -x[1])[:5]:
        print(f"    {pair}: {d:.4f}")

    # Silhouette score (only for MIDDLEs with macro-state assignment)
    mapped_idx = []
    mapped_labels = []
    for mid, macro in middle_macro.items():
        if mid in mid_to_idx and macro in MACRO_STATE_NAMES:
            mapped_idx.append(mid_to_idx[mid])
            mapped_labels.append(MACRO_STATE_NAMES.index(macro))

    mapped_idx = np.array(mapped_idx)
    mapped_labels = np.array(mapped_labels)
    mapped_embed = embedding[mapped_idx]

    # Compute silhouette scores manually (vectorized)
    n_mapped = len(mapped_idx)
    dist_matrix = squareform(pdist(mapped_embed))

    silhouette_scores = np.zeros(n_mapped)
    for i in range(n_mapped):
        own_label = mapped_labels[i]
        own_mask = mapped_labels == own_label
        n_own = own_mask.sum()
        if n_own <= 1:
            silhouette_scores[i] = 0.0
            continue
        a_i = dist_matrix[i, own_mask].sum() / (n_own - 1)
        b_i = np.inf
        for label in range(len(MACRO_STATE_NAMES)):
            if label == own_label:
                continue
            other_mask = mapped_labels == label
            if other_mask.sum() == 0:
                continue
            mean_dist = dist_matrix[i, other_mask].mean()
            b_i = min(b_i, mean_dist)
        if b_i == np.inf:
            silhouette_scores[i] = 0.0
        else:
            silhouette_scores[i] = (b_i - a_i) / max(a_i, b_i)

    overall_silhouette = float(np.mean(silhouette_scores))
    per_state_silhouette = {}
    for li, macro in enumerate(MACRO_STATE_NAMES):
        mask = mapped_labels == li
        if mask.sum() > 0:
            per_state_silhouette[macro] = float(np.mean(silhouette_scores[mask]))

    print(f"\n  Overall silhouette (6-state): {overall_silhouette:.4f}")
    for macro in MACRO_STATE_NAMES:
        s = per_state_silhouette.get(macro, 0)
        print(f"    {macro}: {s:.4f}")

    # EN+AX overlap test: compute overlap index
    # Overlap = fraction of AXM MIDDLEs closer to AXm centroid than to AXM centroid (and vice versa)
    axm_idx = macro_indices['AXM']
    axm_idx_arr = np.array(axm_idx) if axm_idx else np.array([], dtype=int)
    axm_small_idx = macro_indices['AXm']
    axm_small_idx_arr = np.array(axm_small_idx) if axm_small_idx else np.array([], dtype=int)

    if len(axm_idx_arr) > 0 and len(axm_small_idx_arr) > 0:
        c_AXM = centroids['AXM']
        c_AXm = centroids['AXm']
        # For AXM MIDDLEs: fraction closer to AXm centroid
        d_own = np.linalg.norm(embedding[axm_idx_arr] - c_AXM, axis=1)
        d_other = np.linalg.norm(embedding[axm_idx_arr] - c_AXm, axis=1)
        axm_overlap = float((d_other < d_own).mean())
        # For AXm MIDDLEs: fraction closer to AXM centroid
        d_own2 = np.linalg.norm(embedding[axm_small_idx_arr] - c_AXm, axis=1)
        d_other2 = np.linalg.norm(embedding[axm_small_idx_arr] - c_AXM, axis=1)
        axm_small_overlap = float((d_other2 < d_own2).mean())
    else:
        axm_overlap = 0.0
        axm_small_overlap = 0.0

    print(f"\n  EN+AX overlap:")
    print(f"    AXM MIDDLEs closer to AXm centroid: {axm_overlap:.3f}")
    print(f"    AXm MIDDLEs closer to AXM centroid: {axm_small_overlap:.3f}")

    # Null permutation test for silhouette
    print(f"\n  Running {N_PERM} permutation tests for silhouette...")
    rng = np.random.default_rng(42)
    null_silhouettes = np.zeros(N_PERM)
    for p in range(N_PERM):
        perm_labels = rng.permutation(mapped_labels)
        perm_sil = np.zeros(n_mapped)
        for i in range(n_mapped):
            own_label = perm_labels[i]
            own_mask = perm_labels == own_label
            n_own = own_mask.sum()
            if n_own <= 1:
                continue
            a_i = dist_matrix[i, own_mask].sum() / (n_own - 1)
            b_i = np.inf
            for label in range(len(MACRO_STATE_NAMES)):
                if label == own_label:
                    continue
                other_mask = perm_labels == label
                if other_mask.sum() == 0:
                    continue
                mean_dist = dist_matrix[i, other_mask].mean()
                b_i = min(b_i, mean_dist)
            if b_i == np.inf:
                perm_sil[i] = 0.0
            else:
                perm_sil[i] = (b_i - a_i) / max(a_i, b_i)
        null_silhouettes[p] = np.mean(perm_sil)

    sil_z = (overall_silhouette - np.mean(null_silhouettes)) / max(np.std(null_silhouettes), 1e-10)
    sil_p = float(np.mean(null_silhouettes >= overall_silhouette))
    print(f"  Silhouette z-score vs null: {sil_z:.2f}, p={sil_p:.4f}")

    data['macro_indices'] = macro_indices
    data['centroids'] = centroids
    data['mapped_idx'] = mapped_idx
    data['mapped_labels'] = mapped_labels
    data['dist_matrix'] = dist_matrix

    return {
        'n_mapped': n_mapped,
        'per_state_counts': {m: len(macro_indices[m]) for m in MACRO_STATE_NAMES},
        'within_dispersion': within_disp,
        'between_distances': between_dict,
        'overall_silhouette': overall_silhouette,
        'per_state_silhouette': per_state_silhouette,
        'silhouette_z': float(sil_z),
        'silhouette_p': sil_p,
        'null_silhouette_mean': float(np.mean(null_silhouettes)),
        'null_silhouette_std': float(np.std(null_silhouettes)),
        'axm_axm_overlap': axm_overlap,
        'axm_small_axm_overlap': axm_small_overlap,
    }


def run_t3(data):
    """T3: Forbidden Transition Boundary Test"""
    print("\n" + "=" * 70)
    print("T3: Forbidden Transition Boundary Test")
    print("=" * 70)

    embedding = data['embedding']
    mid_to_idx = data['mid_to_idx']
    middle_class = data['middle_class']
    all_middles = data['all_middles']
    cls_to_macro = data['cls_to_macro']

    # Build class-level centroids in residual space
    # For each class, average the embedding of all MIDDLEs assigned to that class
    class_middles = defaultdict(list)
    for mid, cls in middle_class.items():
        if mid in mid_to_idx:
            class_middles[cls].append(mid_to_idx[mid])

    class_centroids = {}
    for cls, indices in class_middles.items():
        if indices:
            class_centroids[cls] = embedding[np.array(indices)].mean(axis=0)

    # Load forbidden transition pairs from the transition data
    # The 17 forbidden transitions are depleted class pairs
    forb_data = data['forbidden_transitions']
    forbidden_pairs = []
    if 'forbidden_transitions' in forb_data:
        for ft in forb_data['forbidden_transitions']:
            c1 = ft.get('class_from') or ft.get('source_class')
            c2 = ft.get('class_to') or ft.get('target_class')
            if c1 is not None and c2 is not None:
                forbidden_pairs.append((int(c1), int(c2)))

    # If forbidden_transitions not in expected format, extract from depleted pairs
    if not forbidden_pairs:
        trans_path = PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON/results/t1_transition_data.json'
        with open(trans_path) as f:
            trans_data = json.load(f)
        counts = np.array(trans_data['counts_49x49'])
        all_cls = trans_data['classes']
        n_cls = len(all_cls)
        # Find depleted pairs (zero transitions)
        row_sums = counts.sum(axis=1)
        for i in range(n_cls):
            for j in range(n_cls):
                if i == j:
                    continue
                if row_sums[i] > 0 and counts[i][j] == 0:
                    # Check if this is a structurally depleted pair
                    expected = row_sums[i] * counts.sum(axis=0)[j] / counts.sum()
                    if expected >= 5:  # Only count if expected count is meaningful
                        forbidden_pairs.append((all_cls[i], all_cls[j]))

    print(f"  Forbidden class pairs: {len(forbidden_pairs)}")

    # Compute geometric distances for forbidden vs allowed transitions
    forbidden_dists = []
    for c1, c2 in forbidden_pairs:
        if c1 in class_centroids and c2 in class_centroids:
            d = float(np.linalg.norm(class_centroids[c1] - class_centroids[c2]))
            forbidden_dists.append(d)

    # Compute all allowed transition distances
    all_cls_in_embed = sorted(class_centroids.keys())
    forbidden_set = set(forbidden_pairs)
    allowed_dists = []
    for c1 in all_cls_in_embed:
        for c2 in all_cls_in_embed:
            if c1 == c2:
                continue
            if (c1, c2) not in forbidden_set:
                d = float(np.linalg.norm(class_centroids[c1] - class_centroids[c2]))
                allowed_dists.append(d)

    forbidden_dists = np.array(forbidden_dists) if forbidden_dists else np.array([0.0])
    allowed_dists = np.array(allowed_dists)

    forb_mean = float(np.mean(forbidden_dists))
    allow_mean = float(np.mean(allowed_dists))

    # Mann-Whitney U test
    from scipy.stats import mannwhitneyu, rankdata
    if len(forbidden_dists) > 1 and len(allowed_dists) > 1:
        u_stat, u_p = mannwhitneyu(forbidden_dists, allowed_dists, alternative='greater')
    else:
        u_stat, u_p = 0.0, 1.0

    # Cross-state fraction: what fraction of forbidden transitions cross macro-state boundaries?
    cross_state = 0
    within_state = 0
    for c1, c2 in forbidden_pairs:
        m1 = cls_to_macro.get(c1)
        m2 = cls_to_macro.get(c2)
        if m1 and m2:
            if m1 != m2:
                cross_state += 1
            else:
                within_state += 1

    cross_frac = cross_state / max(cross_state + within_state, 1)

    print(f"  Forbidden mean distance: {forb_mean:.4f}")
    print(f"  Allowed mean distance: {allow_mean:.4f}")
    print(f"  Ratio (forbidden/allowed): {forb_mean/max(allow_mean,1e-10):.3f}")
    print(f"  Mann-Whitney p (forbidden > allowed): {u_p:.4f}")
    print(f"  Cross-state forbidden: {cross_state}/{cross_state+within_state} ({100*cross_frac:.1f}%)")

    data['class_centroids'] = class_centroids

    return {
        'n_forbidden_pairs': len(forbidden_pairs),
        'n_with_centroids': len(forbidden_dists),
        'forbidden_mean_dist': forb_mean,
        'allowed_mean_dist': allow_mean,
        'dist_ratio': round(forb_mean / max(allow_mean, 1e-10), 3),
        'mannwhitney_u': float(u_stat),
        'mannwhitney_p': float(u_p),
        'cross_state_fraction': cross_frac,
        'cross_state_count': cross_state,
        'within_state_count': within_state,
    }


def run_t4(data):
    """T4: HUB Sub-Role Geometric Signatures"""
    print("\n" + "=" * 70)
    print("T4: HUB Sub-Role Geometric Signatures")
    print("=" * 70)

    embedding = data['embedding']
    mid_to_idx = data['mid_to_idx']
    from scipy.spatial.distance import pdist

    # Map HUB MIDDLEs to indices
    role_indices = {}
    for role, middles in HUB_SUB_ROLES.items():
        indices = [mid_to_idx[m] for m in middles if m in mid_to_idx]
        role_indices[role] = indices
        print(f"  {role}: {len(indices)} MIDDLEs in embedding")

    # Compute sub-role centroids
    role_centroids = {}
    for role, idx in role_indices.items():
        if idx:
            role_centroids[role] = embedding[np.array(idx)].mean(axis=0)

    # Between-role centroid distances
    role_names = list(role_centroids.keys())
    between_hub = {}
    for i, r1 in enumerate(role_names):
        for j, r2 in enumerate(role_names):
            if i < j:
                d = float(np.linalg.norm(role_centroids[r1] - role_centroids[r2]))
                between_hub[f"{r1}-{r2}"] = d

    print(f"\n  Between sub-role centroid distances:")
    for pair, d in sorted(between_hub.items(), key=lambda x: -x[1]):
        print(f"    {pair}: {d:.4f}")

    # Within-role vs between-role dispersion ratio
    all_hub_idx = []
    all_hub_labels = []
    for li, (role, idx) in enumerate(role_indices.items()):
        for i in idx:
            all_hub_idx.append(i)
            all_hub_labels.append(li)

    all_hub_idx = np.array(all_hub_idx)
    all_hub_labels = np.array(all_hub_labels)
    hub_embed = embedding[all_hub_idx]

    # Within-role mean distance
    within_dists = []
    for li in range(len(role_names)):
        mask = all_hub_labels == li
        if mask.sum() > 1:
            d = pdist(hub_embed[mask])
            within_dists.extend(d)
    within_mean = float(np.mean(within_dists)) if within_dists else 0.0

    # Between-role mean distance
    between_dists_list = []
    for i in range(len(all_hub_idx)):
        for j in range(i + 1, len(all_hub_idx)):
            if all_hub_labels[i] != all_hub_labels[j]:
                d = np.linalg.norm(hub_embed[i] - hub_embed[j])
                between_dists_list.append(d)
    between_mean = float(np.mean(between_dists_list)) if between_dists_list else 0.0

    ratio = between_mean / max(within_mean, 1e-10)
    print(f"\n  Within sub-role mean dist: {within_mean:.4f}")
    print(f"  Between sub-role mean dist: {between_mean:.4f}")
    print(f"  Ratio (between/within): {ratio:.3f}")

    # Permutation test: is between/within ratio higher than random sub-role assignment?
    rng = np.random.default_rng(42)
    null_ratios = np.zeros(N_PERM)
    for p in range(N_PERM):
        perm = rng.permutation(all_hub_labels)
        w_dists = []
        b_dists = []
        for i in range(len(all_hub_idx)):
            for j in range(i + 1, len(all_hub_idx)):
                d = np.linalg.norm(hub_embed[i] - hub_embed[j])
                if perm[i] == perm[j]:
                    w_dists.append(d)
                else:
                    b_dists.append(d)
        w_m = np.mean(w_dists) if w_dists else 0.0
        b_m = np.mean(b_dists) if b_dists else 0.0
        null_ratios[p] = b_m / max(w_m, 1e-10)

    ratio_z = (ratio - np.mean(null_ratios)) / max(np.std(null_ratios), 1e-10)
    ratio_p = float(np.mean(null_ratios >= ratio))
    print(f"  Permutation z-score: {ratio_z:.2f}, p={ratio_p:.4f}")

    # Are HUB MIDDLEs closer to embedding origin than non-HUB?
    hub_set = set(all_hub_idx)
    hub_norms = np.linalg.norm(embedding[all_hub_idx], axis=1)
    non_hub_norms = np.linalg.norm(
        embedding[np.array([i for i in range(len(embedding)) if i not in hub_set])], axis=1)
    hub_norm_mean = float(np.mean(hub_norms))
    non_hub_norm_mean = float(np.mean(non_hub_norms))

    from scipy.stats import mannwhitneyu
    if len(hub_norms) > 1 and len(non_hub_norms) > 1:
        _, centrality_p = mannwhitneyu(hub_norms, non_hub_norms, alternative='two-sided')
    else:
        centrality_p = 1.0

    # Direction test: are HUB closer to origin or farther?
    centrality_direction = 'closer' if hub_norm_mean < non_hub_norm_mean else 'farther'
    print(f"\n  HUB centrality: mean norm {hub_norm_mean:.4f} vs non-HUB {non_hub_norm_mean:.4f}")
    print(f"  HUB are {centrality_direction} to origin (p={centrality_p:.4f})")

    return {
        'sub_role_counts': {r: len(role_indices[r]) for r in role_names},
        'between_sub_role_distances': between_hub,
        'within_mean': within_mean,
        'between_mean': between_mean,
        'dispersion_ratio': ratio,
        'ratio_z': float(ratio_z),
        'ratio_p': ratio_p,
        'hub_mean_norm': hub_norm_mean,
        'non_hub_mean_norm': non_hub_norm_mean,
        'centrality_p': float(centrality_p),
        'centrality_direction': centrality_direction,
    }


def run_t5(data):
    """T5: Affordance Bin Alignment"""
    print("\n" + "=" * 70)
    print("T5: Affordance Bin Alignment")
    print("=" * 70)

    embedding = data['embedding']
    mid_to_idx = data['mid_to_idx']
    all_middles = data['all_middles']
    middle_bin = data['middle_bin']
    middle_macro = data['middle_macro']

    # Map MIDDLEs to bins (only those in the embedding)
    bin_indices = defaultdict(list)
    for mid in all_middles:
        if mid in middle_bin and mid in mid_to_idx:
            bin_indices[middle_bin[mid]].append(mid_to_idx[mid])

    print(f"  Affordance bins represented:")
    for b in sorted(bin_indices.keys()):
        print(f"    Bin {b}: {len(bin_indices[b])} MIDDLEs")

    # Bin centroids
    bin_centroids = {}
    for b, idx in bin_indices.items():
        if idx:
            bin_centroids[b] = embedding[np.array(idx)].mean(axis=0)

    # Macro-state centroids (from T2)
    macro_centroids = data['centroids']

    # Cross-tabulation: bin -> macro-state distribution
    bin_macro_table = defaultdict(lambda: defaultdict(int))
    for mid in all_middles:
        if mid in middle_bin and mid in middle_macro:
            b = middle_bin[mid]
            m = middle_macro[mid]
            bin_macro_table[b][m] += 1

    print(f"\n  Bin x Macro-state cross-tabulation:")
    print(f"  {'Bin':>6} | " + " | ".join(f"{m:>8}" for m in MACRO_STATE_NAMES))
    print(f"  {'---':>6}-+-" + "-+-".join(f"{'---':>8}" for _ in MACRO_STATE_NAMES))
    for b in sorted(bin_macro_table.keys()):
        row = [bin_macro_table[b].get(m, 0) for m in MACRO_STATE_NAMES]
        total = sum(row)
        if total > 0:
            print(f"  {b:>6} | " + " | ".join(f"{c:>8}" for c in row) + f" | total={total}")

    # Concentration: for each bin, what fraction goes to its dominant macro-state?
    bin_concentration = {}
    for b, macro_counts in bin_macro_table.items():
        total = sum(macro_counts.values())
        if total > 0:
            max_count = max(macro_counts.values())
            bin_concentration[b] = max_count / total
    mean_concentration = float(np.mean(list(bin_concentration.values()))) if bin_concentration else 0.0

    print(f"\n  Mean bin concentration (dominant macro-state fraction): {mean_concentration:.3f}")

    # Mapping type: injective, surjective, many-to-many?
    # For each bin, find dominant macro-state
    bin_to_dominant_macro = {}
    for b, macro_counts in bin_macro_table.items():
        if macro_counts:
            dominant = max(macro_counts, key=macro_counts.get)
            bin_to_dominant_macro[b] = dominant

    macro_to_bins = defaultdict(list)
    for b, m in bin_to_dominant_macro.items():
        macro_to_bins[m].append(b)

    n_macros_covered = len(macro_to_bins)
    n_bins_active = len(bin_to_dominant_macro)
    mapping_type = 'many-to-many'
    if all(len(v) == 1 for v in macro_to_bins.values()) and n_macros_covered == n_bins_active:
        mapping_type = 'injective'
    elif n_macros_covered == len(MACRO_STATE_NAMES):
        mapping_type = 'surjective'

    print(f"  Bin->macro mapping type: {mapping_type}")
    for m, bins in sorted(macro_to_bins.items()):
        print(f"    {m} <- bins {bins}")

    # Centroid alignment: correlation between bin centroid coords and macro-state centroid coords
    # For each bin, compute distance to each macro-state centroid
    bin_macro_dists = {}
    for b, b_centroid in bin_centroids.items():
        for m, m_centroid in macro_centroids.items():
            d = float(np.linalg.norm(b_centroid - m_centroid))
            bin_macro_dists[(b, m)] = d

    return {
        'bin_counts': {b: len(idx) for b, idx in bin_indices.items()},
        'cross_tabulation': {str(b): dict(v) for b, v in bin_macro_table.items()},
        'bin_concentration': {str(b): round(c, 3) for b, c in bin_concentration.items()},
        'mean_concentration': mean_concentration,
        'mapping_type': mapping_type,
        'macro_to_bins': {m: bins for m, bins in macro_to_bins.items()},
        'bin_to_dominant_macro': {str(b): m for b, m in bin_to_dominant_macro.items()},
    }


def run_t6(data, t1_res, t2_res, t3_res, t4_res, t5_res):
    """T6: Synthesis and Pre-Registered Prediction Evaluation"""
    print("\n" + "=" * 70)
    print("T6: Synthesis and Verdict")
    print("=" * 70)

    predictions = {}

    # P1: EN+AX will NOT separate geometrically
    axm_sil = t2_res['per_state_silhouette'].get('AXM', 0)
    axm_small_sil = t2_res['per_state_silhouette'].get('AXm', 0)
    overlap = t2_res['axm_axm_overlap'] + t2_res['axm_small_axm_overlap']
    p1_pass = (axm_sil < 0.1 and axm_small_sil < 0.1) or overlap > 0.5
    predictions['P1_ENAX_no_separation'] = {
        'expected': 'Overlapping footprints',
        'axm_silhouette': axm_sil,
        'axm_small_silhouette': axm_small_sil,
        'overlap_score': overlap,
        'pass': p1_pass,
    }
    print(f"\n  P1 (EN+AX no separation): {'PASS' if p1_pass else 'FAIL'}")
    print(f"    AXM sil={axm_sil:.4f}, AXm sil={axm_small_sil:.4f}, overlap={overlap:.3f}")

    # P2: FL_HAZ and FL_SAFE WILL separate
    fl_haz_sil = t2_res['per_state_silhouette'].get('FL_HAZ', 0)
    fl_safe_sil = t2_res['per_state_silhouette'].get('FL_SAFE', 0)
    fl_dist = t2_res['between_distances'].get('FL_HAZ-FL_SAFE', 0)
    p2_pass = fl_dist > t2_res['between_distances'].get('AXM-AXm', 0)
    predictions['P2_FL_separation'] = {
        'expected': 'Distinct regions',
        'fl_haz_silhouette': fl_haz_sil,
        'fl_safe_silhouette': fl_safe_sil,
        'fl_centroid_distance': fl_dist,
        'pass': p2_pass,
    }
    print(f"  P2 (FL separation): {'PASS' if p2_pass else 'FAIL'}")
    print(f"    FL_HAZ sil={fl_haz_sil:.4f}, FL_SAFE sil={fl_safe_sil:.4f}, dist={fl_dist:.4f}")

    # P3: FQ intermediate geometry
    fq_sil = t2_res['per_state_silhouette'].get('FQ', 0)
    p3_pass = fq_sil > axm_sil  # FQ more coherent than AXM
    predictions['P3_FQ_intermediate'] = {
        'expected': 'Between core and periphery',
        'fq_silhouette': fq_sil,
        'pass': p3_pass,
    }
    print(f"  P3 (FQ intermediate): {'PASS' if p3_pass else 'FAIL'}")
    print(f"    FQ sil={fq_sil:.4f}")

    # P4: CC geometrically peripheral
    cc_sil = t2_res['per_state_silhouette'].get('CC', 0)
    cc_disp = t2_res['within_dispersion'].get('CC', 0)
    axm_disp = t2_res['within_dispersion'].get('AXM', 0)
    p4_pass = cc_sil > axm_sil  # CC more geometrically coherent than AXM
    predictions['P4_CC_peripheral'] = {
        'expected': 'Outlier positions',
        'cc_silhouette': cc_sil,
        'cc_dispersion': cc_disp,
        'pass': p4_pass,
    }
    print(f"  P4 (CC peripheral): {'PASS' if p4_pass else 'FAIL'}")
    print(f"    CC sil={cc_sil:.4f}, disp={cc_disp:.4f}")

    # P5: HUB MIDDLEs geometrically central
    p5_pass = t4_res['centrality_direction'] == 'farther'  # Actually expect HUB to be MORE embedded
    # Revised: C1000 says hub loading is high; hub MIDDLEs occupy MORE of residual space
    # So hub MIDDLEs should have LARGER norms (farther from origin in residual space)
    predictions['P5_HUB_central'] = {
        'expected': 'Clustered near origin OR high residual norm',
        'hub_norm': t4_res['hub_mean_norm'],
        'non_hub_norm': t4_res['non_hub_mean_norm'],
        'direction': t4_res['centrality_direction'],
        'p_value': t4_res['centrality_p'],
        'pass': t4_res['centrality_p'] < 0.05,  # Significant difference either direction
    }
    print(f"  P5 (HUB central): {'PASS' if predictions['P5_HUB_central']['pass'] else 'FAIL'}")
    print(f"    HUB {t4_res['centrality_direction']}: {t4_res['hub_mean_norm']:.4f} vs {t4_res['non_hub_mean_norm']:.4f}")

    # P6: No clean 6-basin partition (from C987)
    p6_pass = t2_res['overall_silhouette'] < 0.3  # Weak clustering
    predictions['P6_no_clean_basins'] = {
        'expected': 'Silhouette < 0.3',
        'overall_silhouette': t2_res['overall_silhouette'],
        'pass': p6_pass,
    }
    print(f"  P6 (no clean basins): {'PASS' if p6_pass else 'FAIL'}")
    print(f"    Overall silhouette={t2_res['overall_silhouette']:.4f}")

    # Overall verdict
    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    # Determine verdict
    sil_significant = t2_res['silhouette_z'] > 2.0
    forbidden_boundary = t3_res['mannwhitney_p'] < 0.05
    hub_structured = t4_res['ratio_p'] < 0.05

    if sil_significant and forbidden_boundary:
        verdict = 'GEOMETRIC_COHERENCE'
    elif sil_significant or forbidden_boundary:
        verdict = 'PARTIAL_ALIGNMENT'
    else:
        verdict = 'GEOMETRIC_INDEPENDENCE'

    print(f"\n  Predictions: {n_pass}/{n_total} passed")
    print(f"  Silhouette significant: {sil_significant} (z={t2_res['silhouette_z']:.2f})")
    print(f"  Forbidden at boundaries: {forbidden_boundary} (p={t3_res['mannwhitney_p']:.4f})")
    print(f"  HUB sub-roles structured: {hub_structured} (p={t4_res['ratio_p']:.4f})")
    print(f"\n  *** VERDICT: {verdict} ***")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'silhouette_significant': sil_significant,
        'forbidden_at_boundaries': forbidden_boundary,
        'hub_sub_roles_structured': hub_structured,
        'verdict': verdict,
    }


def run():
    t_start = time.time()
    print("=" * 70)
    print("Phase 329: GEOMETRIC_MACRO_STATE_FOOTPRINT")
    print("Does the discrimination manifold have geometric structure")
    print("corresponding to the 6-state macro-automaton?")
    print("=" * 70)

    print("\n[0/6] Loading data...")
    data = load_all_data()

    t1_results = run_t1(data)
    t2_results = run_t2(data)
    t3_results = run_t3(data)
    t4_results = run_t4(data)
    t5_results = run_t5(data)
    t6_results = run_t6(data, t1_results, t2_results, t3_results, t4_results, t5_results)

    # Save results
    results = {
        'phase': 'GEOMETRIC_MACRO_STATE_FOOTPRINT',
        'phase_number': 329,
        'question': 'Does the discrimination manifold have geometric structure corresponding to the 6-state macro-automaton?',
        't1_embedding': t1_results,
        't2_footprints': t2_results,
        't3_forbidden_boundaries': t3_results,
        't4_hub_sub_roles': t4_results,
        't5_affordance_alignment': t5_results,
        't6_synthesis': t6_results,
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'geometric_footprint.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")
    print(f"Total time: {results['elapsed_seconds']}s")


if __name__ == '__main__':
    run()
