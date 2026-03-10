"""
T3: Two-Layer Apparatus Family Clustering
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

Two separate clusterings to distinguish behavioral families from
parameterization families:

  T3a: Response-only clustering (how closure behaves)
       Features: DYE_M1, CCS1, DVA, YGA, CRR, NRI, ablation shares

  T3b: Response-surface clustering (what physics the folio presumes)
       Features: F1-F5, ablation shares, CRR_M1, CRR_M4f

  T3c: Supervised sanity check (F-only vs response-only vs combined)

Cluster stability via bootstrap resampling.
"""

import json
import sys
import os
import time
import random
import math
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P573_RESULTS = RESULTS_DIR
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

ABLATION_NAMES = [
    'NO_CROSS_COUPLING',
    'NO_CLOSE_RECOVERY',
    'NO_CONTAINMENT',
    'NO_TR_TO_Y',
    'NO_Y_SENSITIVITY',
]


# ---------------------------------------------------------------------------
# Numpy-free clustering utilities
# ---------------------------------------------------------------------------
def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def z_normalize(vectors):
    """Z-score normalize columns. Returns (normalized, means, stds)."""
    if not vectors:
        return [], [], []
    n = len(vectors)
    d = len(vectors[0])
    means = [sum(v[j] for v in vectors) / n for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((v[j] - means[j]) ** 2 for v in vectors) / n
        stds.append(math.sqrt(var) if var > 1e-10 else 1.0)
    normed = [[(v[j] - means[j]) / stds[j] for j in range(d)] for v in vectors]
    return normed, means, stds


def ward_linkage(vectors):
    """Ward's minimum variance hierarchical clustering.
    Returns list of (i, j, distance, size) merge steps.
    """
    n = len(vectors)
    # Active cluster tracking
    cluster_members = {i: [i] for i in range(n)}
    cluster_centroids = {i: list(vectors[i]) for i in range(n)}
    cluster_sizes = {i: 1 for i in range(n)}
    active = set(range(n))
    merges = []
    next_id = n

    for _ in range(n - 1):
        if len(active) < 2:
            break

        # Find minimum-cost merge (Ward criterion)
        best_cost = float('inf')
        best_pair = None
        active_list = sorted(active)

        for idx_i in range(len(active_list)):
            ci = active_list[idx_i]
            for idx_j in range(idx_i + 1, len(active_list)):
                cj = active_list[idx_j]
                ni, nj = cluster_sizes[ci], cluster_sizes[cj]
                # Ward distance = (ni*nj)/(ni+nj) * ||ci - cj||^2
                d2 = sum((cluster_centroids[ci][k] - cluster_centroids[cj][k]) ** 2
                         for k in range(len(vectors[0])))
                cost = (ni * nj) / (ni + nj) * d2
                if cost < best_cost:
                    best_cost = cost
                    best_pair = (ci, cj)

        ci, cj = best_pair
        ni, nj = cluster_sizes[ci], cluster_sizes[cj]
        n_new = ni + nj

        # New centroid
        new_centroid = [(ni * cluster_centroids[ci][k] + nj * cluster_centroids[cj][k]) / n_new
                        for k in range(len(vectors[0]))]

        merges.append((ci, cj, math.sqrt(best_cost), n_new))

        cluster_members[next_id] = cluster_members[ci] + cluster_members[cj]
        cluster_centroids[next_id] = new_centroid
        cluster_sizes[next_id] = n_new

        active.discard(ci)
        active.discard(cj)
        active.add(next_id)
        next_id += 1

    return merges


def cut_dendrogram(merges, n_items, k):
    """Cut dendrogram at k clusters. Returns list of cluster labels."""
    if k >= n_items:
        return list(range(n_items))

    # Replay merges, stop when we have k clusters
    parent = {}
    cluster_id = {i: i for i in range(n_items)}
    next_id = n_items

    n_merges_needed = n_items - k
    for step, (ci, cj, dist, size) in enumerate(merges):
        if step >= n_merges_needed:
            break
        parent[ci] = next_id
        parent[cj] = next_id
        next_id += 1

    # Assign labels
    def find_root(node):
        while node in parent:
            node = parent[node]
        return node

    roots = set()
    labels = []
    for i in range(n_items):
        r = find_root(i)
        roots.add(r)
        labels.append(r)

    # Renumber to 0..k-1
    root_to_label = {r: idx for idx, r in enumerate(sorted(roots))}
    return [root_to_label[find_root(i)] for i in range(n_items)]


def silhouette_score(vectors, labels):
    """Compute mean silhouette score."""
    n = len(vectors)
    if n < 2:
        return 0.0
    k = max(labels) + 1
    if k < 2:
        return 0.0

    # Group by cluster
    clusters = {}
    for i, l in enumerate(labels):
        clusters.setdefault(l, []).append(i)

    silhouettes = []
    for i in range(n):
        ci = labels[i]
        # a(i) = mean distance to same cluster
        same = [j for j in clusters[ci] if j != i]
        if not same:
            silhouettes.append(0.0)
            continue
        a_i = sum(euclidean_dist(vectors[i], vectors[j]) for j in same) / len(same)

        # b(i) = min mean distance to other clusters
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


def adjusted_rand_index(labels_a, labels_b):
    """Compute Adjusted Rand Index between two label vectors."""
    n = len(labels_a)
    if n < 2:
        return 0.0

    # Build contingency table
    pairs_a = {}
    pairs_b = {}
    for i in range(n):
        pairs_a.setdefault(labels_a[i], set()).add(i)
        pairs_b.setdefault(labels_b[i], set()).add(i)

    # Compute nij, ai, bj
    sum_nij_choose2 = 0
    for ca in pairs_a.values():
        for cb in pairs_b.values():
            nij = len(ca & cb)
            sum_nij_choose2 += nij * (nij - 1) // 2

    sum_ai_choose2 = sum(len(c) * (len(c) - 1) // 2 for c in pairs_a.values())
    sum_bj_choose2 = sum(len(c) * (len(c) - 1) // 2 for c in pairs_b.values())
    n_choose2 = n * (n - 1) // 2

    expected = sum_ai_choose2 * sum_bj_choose2 / n_choose2 if n_choose2 > 0 else 0
    max_index = 0.5 * (sum_ai_choose2 + sum_bj_choose2)
    denom = max_index - expected

    if abs(denom) < 1e-10:
        return 0.0 if sum_nij_choose2 != expected else 1.0
    return (sum_nij_choose2 - expected) / denom


def nearest_centroid_classify(train_vecs, train_labels, test_vecs):
    """Simple nearest-centroid classifier."""
    labels_set = sorted(set(train_labels))
    centroids = {}
    for l in labels_set:
        members = [train_vecs[i] for i in range(len(train_vecs)) if train_labels[i] == l]
        d = len(train_vecs[0])
        centroids[l] = [sum(m[j] for m in members) / len(members) for j in range(d)]

    predictions = []
    for v in test_vecs:
        best_l = None
        best_d = float('inf')
        for l, c in centroids.items():
            d = euclidean_dist(v, c)
            if d < best_d:
                best_d = d
                best_l = l
        predictions.append(best_l)
    return predictions


def bootstrap_stability(vectors, k, n_bootstrap=100, seed=42):
    """Compute bootstrap cluster assignment stability."""
    rng = random.Random(seed)
    n = len(vectors)

    # Reference clustering
    merges = ward_linkage(vectors)
    ref_labels = cut_dendrogram(merges, n, k)

    agreement_counts = [0] * n
    sample_counts = [0] * n

    for _ in range(n_bootstrap):
        # Bootstrap sample (with replacement)
        indices = [rng.randint(0, n - 1) for _ in range(n)]
        boot_vecs = [vectors[i] for i in indices]

        boot_merges = ward_linkage(boot_vecs)
        boot_labels = cut_dendrogram(boot_merges, n, k)

        # Map boot labels to ref labels (best matching)
        # For each original point that appears in bootstrap, check agreement
        for boot_idx, orig_idx in enumerate(indices):
            sample_counts[orig_idx] += 1
            # Check if same-cluster pairs are preserved
            # Simplified: track if boot label matches ref label
            # (use majority mapping)
            pass

    # Simplified stability: fraction of bootstrap runs where each point
    # stays in the same relative cluster (via ARI between ref and boot)
    ari_scores = []
    for _ in range(n_bootstrap):
        indices = sorted(set(rng.randint(0, n - 1) for _ in range(n)))
        if len(indices) < k + 1:
            continue
        sub_vecs = [vectors[i] for i in indices]
        sub_ref = [ref_labels[i] for i in indices]

        sub_merges = ward_linkage(sub_vecs)
        sub_labels = cut_dendrogram(sub_merges, len(sub_vecs), k)
        ari_scores.append(adjusted_rand_index(sub_ref, sub_labels))

    return sum(ari_scores) / len(ari_scores) if ari_scores else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data():
    """Load Phase 572 data + T1 ablation results."""
    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1_setup = json.load(f)

    print("  Loading T1 mechanism ablation results...")
    with open(os.path.join(P573_RESULTS, 't1_mechanism_ablation.json'), 'r', encoding='utf-8') as f:
        t1_ablation = json.load(f)

    print("  Loading T2 grammar strength results...")
    t2_path = os.path.join(P573_RESULTS, 't2_grammar_strength_forgivingness.json')
    t2_grammar = None
    if os.path.exists(t2_path):
        with open(t2_path, 'r', encoding='utf-8') as f:
            t2_grammar = json.load(f)

    return t1_setup, t1_ablation, t2_grammar


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T3: Two-Layer Apparatus Family Clustering")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    print("\n--- Loading data ---")
    t1_setup, t1_ablation, t2_grammar = load_data()

    eligible_folios = t1_setup['eligible_folios']
    folio_configs = t1_setup['folio_configs']
    per_folio_abl = t1_ablation['per_folio']

    # ================================================================
    # Build feature vectors
    # ================================================================
    print("\n--- Building feature vectors ---")

    folio_list = []
    profile_labels = []
    section_labels = []

    # T3a: Response-only features
    response_features = []
    # T3b: Response-surface features
    surface_features = []
    # Combined
    combined_features = []
    # F-params only
    fparam_features = []

    for folio in eligible_folios:
        fc = folio_configs[folio]
        abl = per_folio_abl.get(folio)
        if abl is None:
            continue

        folio_list.append(folio)
        profile_labels.append(fc['profile'])
        section_labels.append(fc['section'])

        # Response-only: behavioral outcomes
        m1_dye = abl['baseline_m1_dye']
        ccs1 = abl['baseline_m4f_dye']
        dye_adv = m1_dye - ccs1
        crr_m1 = abl['crr_m1']
        crr_m4f = abl['crr_m4f']
        nri_m1 = abl['nri_m1']
        nri_m4f = abl['nri_m4f']

        # Ablation shares (mechanism channel weights)
        abl_shares = []
        for abl_name in ABLATION_NAMES:
            abl_data = abl['ablations'][abl_name]
            abl_shares.append(abl_data['delta_m4f_dye'])

        resp_vec = [m1_dye, ccs1, dye_adv, crr_m4f, nri_m4f] + abl_shares
        response_features.append(resp_vec)

        # Response-surface: apparatus parameters + channel diagnostics
        f1 = fc.get('F1', 1.0) or 1.0
        f2 = fc.get('F2', 1.0) or 1.0
        f3 = fc.get('F3', 1.0) or 1.0
        f4 = fc.get('F4_raw', 0.5) or 0.5
        f5 = fc.get('F5', 1.0) or 1.0

        surf_vec = [f1, f2, f3, f4, f5, crr_m1, crr_m4f] + abl_shares
        surface_features.append(surf_vec)

        combined_features.append(resp_vec + surf_vec)
        fparam_features.append([f1, f2, f3, f4, f5])

    n_folios = len(folio_list)
    print(f"  {n_folios} folios with complete features")

    # Normalize
    resp_norm, _, _ = z_normalize(response_features)
    surf_norm, _, _ = z_normalize(surface_features)
    comb_norm, _, _ = z_normalize(combined_features)
    fparam_norm, _, _ = z_normalize(fparam_features)

    # Encode labels as integers for ARI
    profile_set = sorted(set(profile_labels))
    section_set = sorted(set(section_labels))
    prof_int = [profile_set.index(p) for p in profile_labels]
    sect_int = [section_set.index(s) for s in section_labels]

    # Two-family label: A2 vs non-A2
    two_family_labels = [1 if 'A2' in p else 0 for p in profile_labels]

    # ================================================================
    # T3a: Response-only clustering
    # ================================================================
    print("\n--- T3a: Response-only clustering ---")
    resp_merges = ward_linkage(resp_norm)

    t3a_results = {}
    for k in [2, 3, 4]:
        labels = cut_dendrogram(resp_merges, n_folios, k)
        sil = silhouette_score(resp_norm, labels)
        ari_prof = adjusted_rand_index(labels, prof_int)
        ari_sect = adjusted_rand_index(labels, sect_int)
        ari_2fam = adjusted_rand_index(labels, two_family_labels)

        # Cluster composition
        cluster_comp = {}
        for i, l in enumerate(labels):
            cluster_comp.setdefault(l, []).append(profile_labels[i])

        comp_summary = {}
        for cl, profiles in cluster_comp.items():
            counts = {}
            for p in profiles:
                counts[p] = counts.get(p, 0) + 1
            comp_summary[str(cl)] = counts

        t3a_results[str(k)] = {
            'silhouette': round(sil, 4),
            'ari_vs_profile': round(ari_prof, 4),
            'ari_vs_section': round(ari_sect, 4),
            'ari_vs_2family': round(ari_2fam, 4),
            'cluster_composition': comp_summary,
        }

        print(f"  k={k}: silhouette={sil:.4f}  ARI(profile)={ari_prof:.4f}  "
              f"ARI(section)={ari_sect:.4f}  ARI(2-fam)={ari_2fam:.4f}")
        for cl in sorted(comp_summary):
            print(f"    cluster {cl}: {comp_summary[cl]}")

    # Best k for response-only
    best_k_resp = max(t3a_results.keys(),
                      key=lambda k: t3a_results[k]['silhouette'])

    # Bootstrap stability for best k
    print(f"\n  Bootstrap stability for best k={best_k_resp}...")
    resp_stability = bootstrap_stability(resp_norm, int(best_k_resp), n_bootstrap=50, seed=42)
    print(f"  Bootstrap ARI stability: {resp_stability:.4f}")
    t3a_results['best_k'] = best_k_resp
    t3a_results['bootstrap_stability'] = round(resp_stability, 4)

    # ================================================================
    # T3b: Response-surface clustering
    # ================================================================
    print("\n--- T3b: Response-surface clustering ---")
    surf_merges = ward_linkage(surf_norm)

    t3b_results = {}
    for k in [2, 3, 4]:
        labels = cut_dendrogram(surf_merges, n_folios, k)
        sil = silhouette_score(surf_norm, labels)
        ari_prof = adjusted_rand_index(labels, prof_int)
        ari_sect = adjusted_rand_index(labels, sect_int)
        ari_2fam = adjusted_rand_index(labels, two_family_labels)

        cluster_comp = {}
        for i, l in enumerate(labels):
            cluster_comp.setdefault(l, []).append(profile_labels[i])
        comp_summary = {}
        for cl, profiles in cluster_comp.items():
            counts = {}
            for p in profiles:
                counts[p] = counts.get(p, 0) + 1
            comp_summary[str(cl)] = counts

        t3b_results[str(k)] = {
            'silhouette': round(sil, 4),
            'ari_vs_profile': round(ari_prof, 4),
            'ari_vs_section': round(ari_sect, 4),
            'ari_vs_2family': round(ari_2fam, 4),
            'cluster_composition': comp_summary,
        }

        print(f"  k={k}: silhouette={sil:.4f}  ARI(profile)={ari_prof:.4f}  "
              f"ARI(section)={ari_sect:.4f}  ARI(2-fam)={ari_2fam:.4f}")
        for cl in sorted(comp_summary):
            print(f"    cluster {cl}: {comp_summary[cl]}")

    best_k_surf = max(t3b_results.keys(),
                      key=lambda k: t3b_results[k]['silhouette'])
    print(f"\n  Bootstrap stability for best k={best_k_surf}...")
    surf_stability = bootstrap_stability(surf_norm, int(best_k_surf), n_bootstrap=50, seed=42)
    print(f"  Bootstrap ARI stability: {surf_stability:.4f}")
    t3b_results['best_k'] = best_k_surf
    t3b_results['bootstrap_stability'] = round(surf_stability, 4)

    # ================================================================
    # T3c: Supervised sanity check
    # ================================================================
    print("\n--- T3c: Supervised sanity check ---")

    # Use best-k response-only labels as target
    best_resp_labels = cut_dendrogram(resp_merges, n_folios, int(best_k_resp))

    # Leave-one-out nearest centroid classification
    def loo_accuracy(features, target_labels):
        correct = 0
        for i in range(len(features)):
            train_vecs = features[:i] + features[i+1:]
            train_labs = target_labels[:i] + target_labels[i+1:]
            pred = nearest_centroid_classify(train_vecs, train_labs, [features[i]])
            if pred[0] == target_labels[i]:
                correct += 1
        return correct / len(features)

    # F-params only
    fparam_acc = loo_accuracy(fparam_norm, best_resp_labels)
    # Response-only
    resp_acc = loo_accuracy(resp_norm, best_resp_labels)
    # Combined
    comb_acc = loo_accuracy(comb_norm, best_resp_labels)

    t3c_results = {
        'target': f'response_k{best_k_resp}_labels',
        'fparam_only_accuracy': round(fparam_acc, 4),
        'response_only_accuracy': round(resp_acc, 4),
        'combined_accuracy': round(comb_acc, 4),
    }

    print(f"  Predicting response-only k={best_k_resp} labels:")
    print(f"    F-params only:   {fparam_acc:.1%}")
    print(f"    Response only:   {resp_acc:.1%}")
    print(f"    Combined:        {comb_acc:.1%}")

    # Also predict profile labels
    fparam_prof_acc = loo_accuracy(fparam_norm, prof_int)
    resp_prof_acc = loo_accuracy(resp_norm, prof_int)
    comb_prof_acc = loo_accuracy(comb_norm, prof_int)

    t3c_results['profile_prediction'] = {
        'fparam_only_accuracy': round(fparam_prof_acc, 4),
        'response_only_accuracy': round(resp_prof_acc, 4),
        'combined_accuracy': round(comb_prof_acc, 4),
    }

    print(f"\n  Predicting profile labels:")
    print(f"    F-params only:   {fparam_prof_acc:.1%}")
    print(f"    Response only:   {resp_prof_acc:.1%}")
    print(f"    Combined:        {comb_prof_acc:.1%}")

    # ================================================================
    # Centroid interpretability
    # ================================================================
    print(f"\n--- Centroid interpretability (response k={best_k_resp}) ---")
    best_labels = cut_dendrogram(resp_merges, n_folios, int(best_k_resp))

    resp_feature_names = (['DYE_M1', 'CCS1', 'DYE_adv', 'CRR_M4f', 'NRI_M4f'] +
                          [f'abl_{a}' for a in ABLATION_NAMES])

    centroids = {}
    for cl in sorted(set(best_labels)):
        members = [i for i in range(n_folios) if best_labels[i] == cl]
        centroid_raw = [sum(response_features[i][j] for i in members) / len(members)
                        for j in range(len(response_features[0]))]
        centroid_desc = {}
        for j, fname in enumerate(resp_feature_names):
            centroid_desc[fname] = round(centroid_raw[j], 4)
        centroids[str(cl)] = {
            'n_members': len(members),
            'centroid': centroid_desc,
            'profiles': {},
        }
        for i in members:
            p = profile_labels[i]
            centroids[str(cl)]['profiles'][p] = centroids[str(cl)]['profiles'].get(p, 0) + 1

        print(f"\n  Cluster {cl} (n={len(members)}):")
        print(f"    Profiles: {centroids[str(cl)]['profiles']}")
        for fname, val in centroid_desc.items():
            print(f"    {fname:<20s} = {val:+.4f}")

    # ================================================================
    # Write output
    # ================================================================
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '573',
            'script': 't3_two_layer_clustering.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': n_folios,
            'response_feature_names': resp_feature_names,
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        't3a_response_only': t3a_results,
        't3b_response_surface': t3b_results,
        't3c_supervised': t3c_results,
        'centroids': centroids,
        'folio_cluster_assignments': {
            folio_list[i]: {
                'response_k_best': best_labels[i],
                'profile': profile_labels[i],
                'section': section_labels[i],
            }
            for i in range(n_folios)
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't3_response_families.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\n  Total time: {time.time() - t_start:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
