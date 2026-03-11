"""T2: Family Occupancy in Apparatus Manifold for Phase 580.

How A1/A2/A3 occupy the manifold. Tests A2 elongation and A3 bridge behavior.
Decide C1668.
"""
import json, os, math, random
import numpy as np

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

FAMILIES = ['A1', 'A2', 'A3']


def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def silhouette_score(vectors, labels):
    """Compute mean silhouette score. Pure Python."""
    n = len(vectors)
    if n < 2:
        return 0.0
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        return 0.0
    clusters = {}
    for i, l in enumerate(labels):
        clusters.setdefault(l, []).append(i)
    silhouettes = []
    for i in range(n):
        ci = labels[i]
        same = [j for j in clusters[ci] if j != i]
        if not same:
            silhouettes.append(0.0)
            continue
        a_i = sum(euclidean_dist(vectors[i], vectors[j]) for j in same) / len(same)
        b_i = float('inf')
        for cl, members in clusters.items():
            if cl == ci or not members:
                continue
            mean_d = sum(euclidean_dist(vectors[i], vectors[j]) for j in members) / len(members)
            if mean_d < b_i:
                b_i = mean_d
        if b_i == float('inf'):
            silhouettes.append(0.0)
        else:
            denom = max(a_i, b_i)
            silhouettes.append((b_i - a_i) / denom if denom > 0 else 0.0)
    return sum(silhouettes) / len(silhouettes)


def analyze_space(folios, meta, space_t1, family_labels, family_int):
    """Analyze family occupancy in one PC space."""
    n = len(folios)
    pcs_80 = space_t1['pcs_for_80pct']
    scores = space_t1['folio_scores']
    pc_names = [f'PC{k + 1}' for k in range(pcs_80)]

    X = np.array([[scores[f][pc] for pc in pc_names] for f in folios])

    groups = {fam: [] for fam in FAMILIES}
    for i, f in enumerate(folios):
        groups[meta[f]['family']].append(i)

    # Centroids
    centroids = {}
    for fam in FAMILIES:
        idx = groups[fam]
        centroids[fam] = X[idx].mean(axis=0)

    # Within-family scatter
    scatter = {}
    for fam in FAMILIES:
        idx = groups[fam]
        dists = [float(np.linalg.norm(X[i] - centroids[fam])) for i in idx]
        scatter[fam] = {
            'mean_dist': round(float(np.mean(dists)), 4),
            'std_dist': round(float(np.std(dists)), 4),
            'n': len(idx)
        }

    # Between-family centroid distances
    between = {}
    for i_f, fam1 in enumerate(FAMILIES):
        for fam2 in FAMILIES[i_f + 1:]:
            d = float(np.linalg.norm(centroids[fam1] - centroids[fam2]))
            between[f'{fam1}-{fam2}'] = round(d, 4)

    # Overlap: folios closer to wrong centroid
    wrong_centroid = 0
    for i, f in enumerate(folios):
        true_fam = meta[f]['family']
        dists_to_centroids = {fam: float(np.linalg.norm(X[i] - centroids[fam]))
                              for fam in FAMILIES}
        best_fam = min(dists_to_centroids, key=dists_to_centroids.get)
        if best_fam != true_fam:
            wrong_centroid += 1

    # Silhouette score
    vectors = [X[i].tolist() for i in range(n)]
    sil = silhouette_score(vectors, family_int)

    # LOO classification accuracy
    correct = 0
    for i, f in enumerate(folios):
        true_fam = meta[f]['family']
        loo_centroids = {}
        for fam in FAMILIES:
            idx = [j for j in groups[fam] if j != i]
            loo_centroids[fam] = X[idx].mean(axis=0) if idx else centroids[fam]
        dists_to_loo = {fam: float(np.linalg.norm(X[i] - loo_centroids[fam]))
                        for fam in FAMILIES}
        best_fam = min(dists_to_loo, key=dists_to_loo.get)
        if best_fam == true_fam:
            correct += 1
    loo_accuracy = correct / n

    # Permutation test (1000 perms) on total centroid distance
    obs_total_dist = sum(between.values())
    n_perms = 1000
    perm_exceeds = 0
    for _ in range(n_perms):
        perm_labels = family_labels.copy()
        random.shuffle(perm_labels)
        perm_groups = {fam: [] for fam in FAMILIES}
        for i, fl in enumerate(perm_labels):
            perm_groups[fl].append(i)
        perm_centroids = {}
        for fam in FAMILIES:
            if perm_groups[fam]:
                perm_centroids[fam] = X[perm_groups[fam]].mean(axis=0)
        perm_dist = 0
        for i_f, fam1 in enumerate(FAMILIES):
            for fam2 in FAMILIES[i_f + 1:]:
                if fam1 in perm_centroids and fam2 in perm_centroids:
                    perm_dist += float(np.linalg.norm(
                        perm_centroids[fam1] - perm_centroids[fam2]))
        if perm_dist >= obs_total_dist:
            perm_exceeds += 1
    perm_p = (perm_exceeds + 1) / (n_perms + 1)

    # Family elongation (within-family covariance anisotropy)
    elongation = {}
    for fam in FAMILIES:
        idx = groups[fam]
        if len(idx) < 3 or pcs_80 < 2:
            elongation[fam] = {'ratio': 1.0, 'direction': 'N/A', 'eigenvalues': []}
            continue
        X_fam = X[idx]
        X_centered = X_fam - X_fam.mean(axis=0)
        cov_fam = np.cov(X_centered.T)
        evals_fam = np.linalg.eigvalsh(cov_fam)[::-1]
        evals_fam = np.maximum(evals_fam, 0)
        ratio = float(evals_fam[0] / evals_fam[1]) if evals_fam[1] > 1e-12 else float('inf')

        _, evecs_fam = np.linalg.eigh(cov_fam)
        primary_dir = evecs_fam[:, -1]  # largest eigenvalue
        dir_desc = ', '.join(f'{pc_names[k]}:{primary_dir[k]:.3f}'
                             for k in range(min(3, pcs_80)))
        elongation[fam] = {
            'ratio': round(ratio, 4) if ratio != float('inf') else 999.0,
            'direction': dir_desc,
            'eigenvalues': [round(float(e), 6) for e in evals_fam]
        }

    finite_ratios = {f: elongation[f]['ratio'] for f in FAMILIES
                     if elongation[f]['ratio'] < 999}
    most_elongated = max(finite_ratios, key=finite_ratios.get) if finite_ratios else 'A2'

    # A3 bridge analysis
    a3_idx = groups['A3']
    a3_dist_a1 = [float(np.linalg.norm(X[i] - centroids['A1'])) for i in a3_idx]
    a3_dist_a2 = [float(np.linalg.norm(X[i] - centroids['A2'])) for i in a3_idx]

    a1_a2_dist = between['A1-A2']
    bridge_thresh = a1_a2_dist / 4
    bridge_count = sum(1 for d1, d2 in zip(a3_dist_a1, a3_dist_a2)
                       if abs(d1 - d2) < bridge_thresh)
    bridge_fraction = bridge_count / len(a3_idx) if a3_idx else 0

    max_d1 = max(a3_dist_a1) if a3_dist_a1 else 0
    min_d2 = min(a3_dist_a2) if a3_dist_a2 else 1
    spanning_ratio = max_d1 / min_d2 if min_d2 > 1e-12 else 0

    a3_per_folio = {}
    for k, i in enumerate(a3_idx):
        a3_per_folio[folios[i]] = {
            'dist_A1': round(a3_dist_a1[k], 4),
            'dist_A2': round(a3_dist_a2[k], 4)
        }

    a3_bridge = {
        'n_a3': len(a3_idx),
        'bridge_threshold': round(bridge_thresh, 4),
        'bridge_count': bridge_count,
        'bridge_fraction': round(bridge_fraction, 4),
        'spanning_ratio': round(float(spanning_ratio), 4),
        'mean_dist_to_A1': round(float(np.mean(a3_dist_a1)), 4),
        'mean_dist_to_A2': round(float(np.mean(a3_dist_a2)), 4),
        'per_folio': a3_per_folio
    }

    return {
        'pcs_used': pcs_80,
        'centroids': {fam: [round(float(x), 6) for x in centroids[fam]]
                      for fam in FAMILIES},
        'within_family_scatter': scatter,
        'between_family_distances': between,
        'wrong_centroid_count': wrong_centroid,
        'silhouette': round(sil, 4),
        'loo_accuracy': round(loo_accuracy, 4),
        'permutation_test': {
            'n_perms': n_perms,
            'observed_total_distance': round(obs_total_dist, 4),
            'p_value': round(perm_p, 4)
        },
        'family_elongation': elongation,
        'most_elongated_family': most_elongated,
        'a3_bridge': a3_bridge
    }


def main():
    random.seed(42)
    np.random.seed(42)

    with open(os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_manifold_embedding.json')) as f:
        t1 = json.load(f)

    folios = t0['folios']
    meta = t0['folio_metadata']
    n = len(folios)

    family_labels = [meta[f]['family'] for f in folios]
    family_int = [FAMILIES.index(fl) for fl in family_labels]

    result_A = analyze_space(folios, meta, t1['space_A'], family_labels, family_int)
    result_B = analyze_space(folios, meta, t1['space_B'], family_labels, family_int)

    # C1668 decision (Space A)
    loo = result_A['loo_accuracy']
    sil = result_A['silhouette']
    if loo > 0.70 and sil > 0.20:
        verdict = 'FAMILY_SEPARABLE'
    elif loo < 0.55:
        verdict = 'FAMILY_OVERLAPPING'
    else:
        verdict = 'FAMILY_GRADIENT'

    output = {
        'metadata': {
            'phase': '580',
            'script': 't2_family_occupancy.py',
            'n_folios': n,
            'family_counts': {fam: sum(1 for fl in family_labels if fl == fam)
                              for fam in FAMILIES}
        },
        'space_A': result_A,
        'space_B': result_B,
        'C1668': {
            'verdict': verdict,
            'loo_accuracy': result_A['loo_accuracy'],
            'silhouette': result_A['silhouette'],
            'rationale': f"LOO accuracy = {loo:.2f}, silhouette = {sil:.2f}"
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't2_family_occupancy.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T2: Family occupancy analysis complete")
    print(f"  Space A: LOO={loo:.2f}, silhouette={sil:.4f}, "
          f"perm_p={result_A['permutation_test']['p_value']:.4f}")
    print(f"  Space B: LOO={result_B['loo_accuracy']:.2f}, "
          f"silhouette={result_B['silhouette']:.4f}")
    for fam in FAMILIES:
        e = result_A['family_elongation'][fam]
        print(f"  {fam} elongation: {e['ratio']:.2f} ({e['direction']})")
    print(f"  Most elongated: {result_A['most_elongated_family']}")
    b = result_A['a3_bridge']
    print(f"  A3 bridge: {b['bridge_count']}/{b['n_a3']} "
          f"({b['bridge_fraction']:.2f}), spanning={b['spanning_ratio']:.2f}")
    print(f"  C1668: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
