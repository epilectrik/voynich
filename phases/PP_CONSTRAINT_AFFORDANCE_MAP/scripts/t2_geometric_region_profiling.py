#!/usr/bin/env python3
"""
T2: Geometric Region Profiling
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

Extract natural geometric regions from the residual manifold and profile
each region by its property composition. T1 showed the space is OPAQUE
to simple property correlations — regions may reveal structure that
individual axes do not.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

QO_INITIALS = set('ktp')
CHSH_INITIALS = set('eo')


def reconstruct_middle_list():
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
    return sorted(all_middles_set)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    hub_vec = eigenvectors[:, 0]
    return res_evecs * scaling[np.newaxis, :], hub_vec, eigenvalues


def build_properties(all_middles, mid_to_idx, hub_vec, embedding):
    """Build property vectors for profiling."""
    tx = Transcript()
    morph = Morphology()

    props = {m: {} for m in all_middles}

    # Morphological
    for m in all_middles:
        props[m]['length'] = len(m)
        props[m]['contains_k'] = 1 if 'k' in m else 0
        props[m]['contains_e'] = 1 if 'e' in m else 0
        props[m]['contains_h'] = 1 if 'h' in m else 0
        props[m]['kernel_count'] = sum(1 for c in m if c in 'keh')
        if m[0] in QO_INITIALS:
            props[m]['lane'] = 'QO'
        elif m[0] in CHSH_INITIALS:
            props[m]['lane'] = 'CHSH'
        else:
            props[m]['lane'] = 'OTHER'

    # Frequency
    a_counts = Counter()
    a_folio_sets = defaultdict(set)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m_result = morph.extract(word)
        if m_result.middle and m_result.middle in mid_to_idx:
            a_counts[m_result.middle] += 1
            a_folio_sets[m_result.middle].add(token.folio)

    b_counts = Counter()
    b_section_counts = defaultdict(lambda: Counter())
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m_result = morph.extract(word)
        if m_result.middle and m_result.middle in mid_to_idx:
            b_counts[m_result.middle] += 1
            b_section_counts[m_result.middle][token.section] += 1

    for m in all_middles:
        props[m]['a_count'] = a_counts.get(m, 0)
        props[m]['a_folios'] = len(a_folio_sets.get(m, set()))
        props[m]['b_count'] = b_counts.get(m, 0)
        props[m]['in_b'] = 1 if b_counts.get(m, 0) > 0 else 0
        props[m]['log_freq'] = float(np.log1p(a_counts.get(m, 0)))
        if m in b_section_counts and b_section_counts[m]:
            props[m]['b_dom_section'] = b_section_counts[m].most_common(1)[0][0]
        else:
            props[m]['b_dom_section'] = 'NONE'

    # Compound
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')
    for m in all_middles:
        props[m]['is_compound'] = 1 if mid_analyzer.is_compound(m) else 0

    # Geometric
    for i, m in enumerate(all_middles):
        props[m]['hub_loading'] = float(hub_vec[i])
        props[m]['residual_norm'] = float(np.linalg.norm(embedding[i]))

    return props


def profile_cluster(cluster_middles, props, all_middles):
    """Build profile for a cluster of MIDDLEs."""
    n = len(cluster_middles)
    if n == 0:
        return {}

    profile = {'n': n}

    # Numeric means
    for key in ['length', 'contains_k', 'contains_e', 'contains_h',
                'kernel_count', 'a_count', 'a_folios', 'b_count', 'in_b',
                'is_compound', 'hub_loading', 'residual_norm', 'log_freq']:
        vals = [props[m][key] for m in cluster_middles]
        profile[f'mean_{key}'] = float(np.mean(vals))

    # Categorical distributions
    lane_counts = Counter(props[m]['lane'] for m in cluster_middles)
    profile['lane_dist'] = {k: v / n for k, v in lane_counts.items()}
    profile['dominant_lane'] = lane_counts.most_common(1)[0][0]

    sec_counts = Counter(props[m]['b_dom_section'] for m in cluster_middles)
    profile['section_dist'] = {k: v / n for k, v in sec_counts.most_common(5)}
    profile['dominant_section'] = sec_counts.most_common(1)[0][0]

    # Initial character distribution
    init_counts = Counter(m[0] for m in cluster_middles)
    profile['top_initials'] = {k: v / n for k, v in init_counts.most_common(5)}

    return profile


def main():
    print("=" * 60)
    print("T2: Geometric Region Profiling")
    print("=" * 60)

    # Load data
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    embedding, hub_vec, eigenvalues = build_residual_embedding(compat_matrix)
    print(f"  {len(all_middles)} MIDDLEs, embedding shape {embedding.shape}")

    props = build_properties(all_middles, mid_to_idx, hub_vec, embedding)

    # GMM with BIC selection
    print("\n[2] GMM clustering with BIC selection (k=3..20)...")
    bic_scores = {}
    gmm_models = {}
    for k in range(3, 21):
        gmm = GaussianMixture(n_components=k, random_state=42, n_init=3,
                               covariance_type='diag', max_iter=300)
        gmm.fit(embedding)
        bic = gmm.bic(embedding)
        bic_scores[k] = float(bic)
        gmm_models[k] = gmm
        if k <= 10 or k % 5 == 0:
            print(f"    k={k:2d}: BIC={bic:.1f}")

    best_k = min(bic_scores, key=bic_scores.get)
    print(f"\n  Best k by BIC: {best_k} (BIC={bic_scores[best_k]:.1f})")

    # Also compute silhouette for reference
    best_gmm = gmm_models[best_k]
    gmm_labels = best_gmm.predict(embedding)
    sil = silhouette_score(embedding, gmm_labels)
    print(f"  Silhouette at k={best_k}: {sil:.3f}")

    # KMeans comparison at same k
    print(f"\n[3] KMeans at k={best_k} for comparison...")
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    km_labels = km.fit_predict(embedding)
    km_sil = silhouette_score(embedding, km_labels)
    print(f"  KMeans silhouette: {km_sil:.3f}")

    # Use GMM labels (soft clustering is more appropriate for MIXED_BANDS)
    labels = gmm_labels

    # Profile each cluster
    print(f"\n[4] Profiling {best_k} clusters...")
    cluster_profiles = {}
    for c in range(best_k):
        cluster_mids = [all_middles[i] for i in range(len(all_middles)) if labels[i] == c]
        profile = profile_cluster(cluster_mids, props, all_middles)
        cluster_profiles[str(c)] = profile

        # Print identity card
        print(f"\n  Cluster {c} (n={profile['n']}):")
        print(f"    Lane: {profile['dominant_lane']} "
              f"(QO={profile['lane_dist'].get('QO', 0):.0%}, "
              f"CHSH={profile['lane_dist'].get('CHSH', 0):.0%}, "
              f"OTHER={profile['lane_dist'].get('OTHER', 0):.0%})")
        print(f"    Kernel: k={profile['mean_contains_k']:.2f}, "
              f"e={profile['mean_contains_e']:.2f}, h={profile['mean_contains_h']:.2f}")
        print(f"    Freq: mean_a={profile['mean_a_count']:.1f}, "
              f"folios={profile['mean_a_folios']:.1f}, "
              f"in_b={profile['mean_in_b']:.0%}")
        print(f"    Length: {profile['mean_length']:.1f}, "
              f"compound={profile['mean_is_compound']:.0%}")
        print(f"    Geometry: hub={profile['mean_hub_loading']:.4f}, "
              f"depth={profile['mean_residual_norm']:.4f}")
        print(f"    Section: {profile['dominant_section']} "
              f"({profile['section_dist']})")
        top_init = ', '.join(f"{k}={v:.0%}" for k, v in
                             sorted(profile['top_initials'].items(),
                                    key=lambda x: x[1], reverse=True)[:5])
        print(f"    Initials: {top_init}")

    # Inter-cluster property contrasts
    print(f"\n[5] Key inter-cluster contrasts...")
    numeric_keys = ['mean_contains_k', 'mean_contains_e', 'mean_contains_h',
                    'mean_length', 'mean_a_count', 'mean_residual_norm',
                    'mean_hub_loading', 'mean_is_compound', 'mean_in_b']

    # Find the most discriminating property for each cluster pair
    contrasts = []
    for ci in range(best_k):
        for cj in range(ci + 1, best_k):
            mids_i = [all_middles[idx] for idx in range(len(all_middles)) if labels[idx] == ci]
            mids_j = [all_middles[idx] for idx in range(len(all_middles)) if labels[idx] == cj]

            best_disc = None
            best_diff = 0
            for key in numeric_keys:
                vi = profile_cluster(mids_i, props, all_middles).get(key, 0)
                vj = profile_cluster(mids_j, props, all_middles).get(key, 0)
                diff = abs(vi - vj)
                # Normalize by overall range
                all_vals = [cluster_profiles[str(c)].get(key, 0) for c in range(best_k)]
                rng = max(all_vals) - min(all_vals) if len(all_vals) > 1 else 1
                if rng > 0:
                    norm_diff = diff / rng
                    if norm_diff > best_diff:
                        best_diff = norm_diff
                        best_disc = key

            contrasts.append({
                'pair': f"{ci}-{cj}",
                'discriminator': best_disc,
                'normalized_diff': float(best_diff),
            })

    contrasts.sort(key=lambda x: x['normalized_diff'], reverse=True)
    print(f"  Top 10 most contrasting cluster pairs:")
    for c in contrasts[:10]:
        print(f"    {c['pair']:>5s}: {c['discriminator']:>25s} (norm_diff={c['normalized_diff']:.3f})")

    # Count discriminating properties per cluster
    print(f"\n[6] Per-cluster discriminating property count...")
    for c in range(best_k):
        profile = cluster_profiles[str(c)]
        n_discrim = 0
        for key in numeric_keys:
            # Compare this cluster to overall mean
            all_vals = [cluster_profiles[str(cc)].get(key, 0) for cc in range(best_k)]
            overall_mean = np.mean(all_vals)
            overall_std = np.std(all_vals)
            if overall_std > 0:
                z = abs(profile.get(key, 0) - overall_mean) / overall_std
                if z > 1.0:
                    n_discrim += 1
        print(f"    Cluster {c}: {n_discrim} discriminating properties (z>1)")

    # Verdict
    print("\n" + "=" * 60)

    # Count clusters with ≥3 discriminating properties
    n_structured = 0
    for c in range(best_k):
        profile = cluster_profiles[str(c)]
        n_discrim = 0
        for key in numeric_keys:
            all_vals = [cluster_profiles[str(cc)].get(key, 0) for cc in range(best_k)]
            overall_mean = np.mean(all_vals)
            overall_std = np.std(all_vals)
            if overall_std > 0:
                z = abs(profile.get(key, 0) - overall_mean) / overall_std
                if z > 1.0:
                    n_discrim += 1
        if n_discrim >= 3:
            n_structured += 1

    if n_structured >= best_k * 0.6:
        verdict = "STRUCTURED_REGIONS"
        explanation = (
            f"{n_structured}/{best_k} clusters have ≥3 discriminating properties. "
            f"The manifold has multi-property-structured regions."
        )
    elif n_structured >= 2:
        verdict = "PARTIALLY_STRUCTURED"
        explanation = (
            f"{n_structured}/{best_k} clusters have ≥3 discriminating properties. "
            f"Some regions are property-coherent, others are generic."
        )
    elif all(abs(cluster_profiles[str(c)].get('mean_log_freq', 0) -
                 np.mean([cluster_profiles[str(cc)].get('mean_log_freq', 0)
                          for cc in range(best_k)])) > 0.5
             for c in range(best_k)):
        verdict = "FREQUENCY_ONLY"
        explanation = "Clusters differ primarily on frequency, not structural properties."
    else:
        verdict = "UNSTRUCTURED"
        explanation = "No stable multi-property cluster structure found."

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T2_geometric_region_profiling',
        'n_middles': len(all_middles),
        'bic_selection': {
            'best_k': best_k,
            'bic_scores': {str(k): v for k, v in bic_scores.items()},
            'gmm_silhouette': float(sil),
            'kmeans_silhouette': float(km_sil),
        },
        'cluster_profiles': cluster_profiles,
        'top_contrasts': contrasts[:15],
        'n_structured_clusters': n_structured,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't2_geometric_region_profiling.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't2_geometric_region_profiling.json'}")


if __name__ == '__main__':
    main()
