#!/usr/bin/env python3
"""
T11: Hub-Residual Structure Analysis
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Remove the dominant hub eigenmode (λ₁=82) and analyze the RESIDUAL
discrimination space. The hub masks differential structure — what
remains after its removal reveals whether the constraint space is:
- Block-structured (tight modular clusters → categorical recipe classes)
- Continuous manifold (smooth bands with curvature → thermodynamic affordance)

Expert predictions to test:
1. ~10-15 macro-bands, not clean clusters
2. Section structure sharpens moderately
3. AZC folio separation increases
4. Universal connectors collapse toward origin
5. Rare tail MIDDLEs stretch to extremal ridges
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
K_EMBED = 99  # Eigenvectors 2-100 (skip hub)
N_NULL = 500


def reconstruct_middle_list():
    """Reconstruct the MIDDLE ordering from T1."""
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
    return all_middles, mid_to_idx


def build_hub_residual_embedding(compat_matrix):
    """Build embedding from eigenvectors 2-100 (skip hub eigenmode)."""
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Hub = eigenvector 0; residual = eigenvectors 1 through K_EMBED
    hub_vec = eigenvectors[:, 0]
    hub_val = eigenvalues[0]

    residual_evals = eigenvalues[1:K_EMBED + 1]
    residual_evecs = eigenvectors[:, 1:K_EMBED + 1]

    # Scale by sqrt(eigenvalue)
    pos_evals = np.maximum(residual_evals, 0)
    scaling = np.sqrt(pos_evals)
    residual_embedding = residual_evecs * scaling[np.newaxis, :]

    # Also build full embedding (1-100) for comparison
    full_evals = eigenvalues[:K_EMBED + 1]
    full_evecs = eigenvectors[:, :K_EMBED + 1]
    full_scaling = np.sqrt(np.maximum(full_evals, 0))
    full_embedding = full_evecs * full_scaling[np.newaxis, :]

    return residual_embedding, residual_evals, hub_vec, hub_val, full_embedding, eigenvalues


def cosine_similarity_matrix(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)
    normed = vectors / norms
    return normed @ normed.T


def extract_azc_folio_middles(mid_to_idx):
    tx = Transcript()
    morph = Morphology()
    folio_middles = defaultdict(set)
    for token in tx.azc():
        if hasattr(token, 'placement') and token.placement and \
           token.placement.startswith('P'):
            continue
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            folio_middles[token.folio].add(m.middle)
    return dict(folio_middles)


def get_middle_frequencies(mid_to_idx):
    """Get frequency of each MIDDLE across Currier A lines."""
    tx = Transcript()
    morph = Morphology()
    line_presence = defaultdict(set)  # MIDDLE -> set of (folio, line) keys
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            line_presence[m.middle].add((token.folio, token.line))
    return {m: len(lines) for m, lines in line_presence.items()}


SECTION_MAP = {
    'Z': ['f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
          'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'],
    'A': ['f67r1', 'f67r2', 'f67v1', 'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2'],
    'C': ['f57v', 'f67v2', 'f68v3', 'f69r', 'f69v', 'f70r1', 'f70r2',
          'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'],
}
FOLIO_TO_SECTION = {}
for sec, folios in SECTION_MAP.items():
    for f in folios:
        FOLIO_TO_SECTION[f] = sec


def run():
    print("=" * 70)
    print("T11: Hub-Residual Structure Analysis")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Load data
    print("\n[1/7] Loading and embedding...")
    all_middles, mid_to_idx = reconstruct_middle_list()
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')
    n = len(all_middles)

    residual_emb, residual_evals, hub_vec, hub_val, full_emb, all_evals = \
        build_hub_residual_embedding(M)

    print(f"  {n} MIDDLEs")
    print(f"  Hub eigenvalue: {hub_val:.1f}")
    print(f"  Residual eigenvalue range: {residual_evals[0]:.1f} to {residual_evals[-1]:.1f}")
    print(f"  Residual embedding shape: {residual_emb.shape}")

    # Hub vector analysis
    hub_loadings = hub_vec  # Each MIDDLE's loading on the hub
    print(f"\n  Hub vector loading range: {hub_loadings.min():.4f} to {hub_loadings.max():.4f}")
    print(f"  Hub loading mean: {hub_loadings.mean():.4f}, std: {hub_loadings.std():.4f}")

    # Top hub MIDDLEs (universal connectors)
    hub_order = np.argsort(hub_loadings)[::-1]
    print(f"\n  Top 20 hub-loading MIDDLEs:")
    known_hubs = {'a', 'o', 'e', 'ee', 'eo'}
    for rank, idx in enumerate(hub_order[:20]):
        m = all_middles[idx]
        flag = " *** KNOWN HUB" if m in known_hubs else ""
        print(f"    {rank+1:>3}. {m:<12} loading={hub_loadings[idx]:.4f}{flag}")

    # MIDDLE frequency data
    print("\n[2/7] Analyzing hub vs frequency relationship...")
    mid_freq = get_middle_frequencies(mid_to_idx)
    freqs = np.array([mid_freq.get(m, 0) for m in all_middles])

    # Correlation between hub loading and frequency
    from scipy.stats import spearmanr
    rho, p_rho = spearmanr(hub_loadings, freqs)
    print(f"  Hub loading vs line frequency: Spearman rho={rho:.3f}, p={p_rho:.2e}")

    # Residual norm vs frequency (do rare MIDDLEs stretch to extremes?)
    residual_norms = np.linalg.norm(residual_emb, axis=1)
    rho_res, p_res = spearmanr(residual_norms, freqs)
    print(f"  Residual norm vs frequency: Spearman rho={rho_res:.3f}, p={p_res:.2e}")

    # Frequency quartiles
    freq_quartiles = np.percentile(freqs[freqs > 0], [25, 50, 75])
    print(f"  Frequency quartiles (non-zero): {freq_quartiles}")

    hub_by_freq = {}
    for label, lo, hi in [('rare (1-2 lines)', 0.5, 2.5),
                           ('uncommon (3-10)', 2.5, 10.5),
                           ('common (11-50)', 10.5, 50.5),
                           ('universal (51+)', 50.5, 9999)]:
        mask = (freqs >= lo) & (freqs < hi)
        if mask.sum() > 0:
            hub_by_freq[label] = {
                'count': int(mask.sum()),
                'mean_hub_loading': float(hub_loadings[mask].mean()),
                'mean_residual_norm': float(residual_norms[mask].mean()),
            }
            print(f"    {label}: n={mask.sum()}, hub={hub_loadings[mask].mean():.4f}, "
                  f"residual_norm={residual_norms[mask].mean():.3f}")

    # Step 3: Universal connectors in residual space
    print("\n[3/7] Universal connectors in residual space...")
    connector_middles = ['a', 'o', 'e', 'ee', 'eo', 'ed', 'od', 'oe']
    for cm in connector_middles:
        if cm in mid_to_idx:
            idx = mid_to_idx[cm]
            rnorm = residual_norms[idx]
            hload = hub_loadings[idx]
            freq = freqs[idx]
            print(f"    {cm:<8} hub_load={hload:.4f}  residual_norm={rnorm:.3f}  freq={freq}")

    mean_rnorm = residual_norms.mean()
    connector_rnorms = [residual_norms[mid_to_idx[cm]] for cm in connector_middles if cm in mid_to_idx]
    print(f"\n  Mean residual norm (all): {mean_rnorm:.3f}")
    print(f"  Mean residual norm (connectors): {np.mean(connector_rnorms):.3f}")
    print(f"  Ratio: {np.mean(connector_rnorms)/mean_rnorm:.3f}")

    # Step 4: Clustering analysis on residual space
    print("\n[4/7] Clustering analysis on residual space...")
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score

    cluster_results = {}
    for k in [5, 8, 10, 12, 15, 20, 30]:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(residual_emb)
        sil = silhouette_score(residual_emb, labels, sample_size=min(n, 500), random_state=42)
        sizes = sorted(Counter(labels).values(), reverse=True)
        cluster_results[k] = {
            'silhouette': float(sil),
            'sizes': sizes,
            'max_cluster': sizes[0],
            'min_cluster': sizes[-1],
        }
        print(f"    k={k:>3}: silhouette={sil:.4f}, sizes={sizes[:5]}{'...' if len(sizes) > 5 else ''}")

    # Find best k
    best_k = max(cluster_results.keys(), key=lambda k: cluster_results[k]['silhouette'])
    print(f"  Best k by silhouette: {best_k} (sil={cluster_results[best_k]['silhouette']:.4f})")

    # Step 5: Section structure in residual space
    print("\n[5/7] AZC folio structure in residual space...")
    folio_middles = extract_azc_folio_middles(mid_to_idx)

    folio_indices = {}
    for folio, middles in folio_middles.items():
        indices = sorted([mid_to_idx[m] for m in middles])
        if len(indices) >= 5:
            folio_indices[folio] = np.array(indices)

    # Folio cohesion in residual space
    from scipy.spatial.distance import pdist, squareform

    folio_list = sorted(folio_indices.keys())
    folio_centroids_residual = {}
    folio_cohesion_residual = {}

    rng = np.random.RandomState(42)

    print(f"\n  {'Folio':<10} {'Sec':>3} {'N':>4} {'CosSim':>8} {'NullCos':>8} {'CosZ':>7}")
    print(f"  {'-'*50}")

    n_coherent = 0
    for folio in folio_list:
        indices = folio_indices[folio]
        folio_vecs = residual_emb[indices]
        n_f = len(indices)
        sec = FOLIO_TO_SECTION.get(folio, '?')

        centroid = folio_vecs.mean(axis=0)
        folio_centroids_residual[folio] = centroid

        # Cosine similarity
        cos_mat = cosine_similarity_matrix(folio_vecs)
        triu = np.triu_indices(n_f, k=1)
        mean_cos = float(cos_mat[triu].mean()) if len(triu[0]) > 0 else 0

        # Null
        null_cos_vals = []
        for _ in range(N_NULL):
            rand_idx = rng.choice(n, n_f, replace=False)
            rand_vecs = residual_emb[rand_idx]
            rand_cos = cosine_similarity_matrix(rand_vecs)
            null_cos_vals.append(float(rand_cos[triu].mean()) if len(triu[0]) > 0 else 0)

        null_cos = np.array(null_cos_vals)
        cos_z = (mean_cos - null_cos.mean()) / null_cos.std() if null_cos.std() > 0 else 0

        is_coherent = cos_z > 2.0
        if is_coherent:
            n_coherent += 1

        flag = " ***" if is_coherent else ""
        print(f"  {folio:<10} {sec:>3} {n_f:>4} {mean_cos:>8.4f} {null_cos.mean():>8.4f} {cos_z:>7.2f}{flag}")

        folio_cohesion_residual[folio] = {
            'n_middles': n_f,
            'section': sec,
            'mean_cosine_sim': float(mean_cos),
            'null_cos_mean': float(null_cos.mean()),
            'cos_z': float(cos_z),
        }

    print(f"\n  Coherent folios (cos_z > 2.0): {n_coherent} / {len(folio_list)}")

    # Interfolio separation in residual space
    centroid_mat = np.array([folio_centroids_residual[f] for f in folio_list])
    centroid_cos_residual = cosine_similarity_matrix(centroid_mat)
    triu_f = np.triu_indices(len(folio_list), k=1)
    mean_inter_cos_residual = float(centroid_cos_residual[triu_f].mean())

    centroid_dists_residual = squareform(pdist(centroid_mat, 'euclidean'))
    mean_inter_dist_residual = float(centroid_dists_residual[triu_f].mean())

    print(f"\n  Interfolio centroid cosine (residual): {mean_inter_cos_residual:.4f}")
    print(f"  Interfolio centroid distance (residual): {mean_inter_dist_residual:.3f}")
    print(f"  (Compare T10 full: cosine=0.9475, distance=0.27)")

    # Section structure
    within_dists = []
    between_dists = []
    within_cos = []
    between_cos = []

    for i, fi in enumerate(folio_list):
        for j, fj in enumerate(folio_list):
            if i >= j:
                continue
            sec_i = FOLIO_TO_SECTION.get(fi)
            sec_j = FOLIO_TO_SECTION.get(fj)
            if sec_i and sec_j:
                d = float(centroid_dists_residual[i, j])
                c = float(centroid_cos_residual[i, j])
                if sec_i == sec_j:
                    within_dists.append(d)
                    within_cos.append(c)
                else:
                    between_dists.append(d)
                    between_cos.append(c)

    if within_dists and between_dists:
        from scipy.stats import mannwhitneyu
        mean_within = np.mean(within_dists)
        mean_between = np.mean(between_dists)
        ratio = mean_within / mean_between
        stat, p_val = mannwhitneyu(within_dists, between_dists, alternative='less')

        print(f"\n  Section structure (residual):")
        print(f"    Within-section distance: {mean_within:.3f}")
        print(f"    Between-section distance: {mean_between:.3f}")
        print(f"    Ratio: {ratio:.3f} (T10 full: 0.944)")
        print(f"    Mann-Whitney p: {p_val:.4f} (T10 full: 0.0006)")
        print(f"    Within cosine: {np.mean(within_cos):.4f}")
        print(f"    Between cosine: {np.mean(between_cos):.4f}")

        section_structure = {
            'mean_within_dist': float(mean_within),
            'mean_between_dist': float(mean_between),
            'ratio': float(ratio),
            'mannwhitney_p': float(p_val),
            'mean_within_cos': float(np.mean(within_cos)),
            'mean_between_cos': float(np.mean(between_cos)),
        }
    else:
        section_structure = {}

    # Step 6: Section-MIDDLE clustering alignment
    print("\n[6/7] Cluster-section alignment...")

    # Best-k clustering labels
    km_best = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    best_labels = km_best.fit_predict(residual_emb)

    # Check if cluster labels align with AZC section (for AZC-present MIDDLEs)
    # Build section labels for MIDDLEs that appear in exactly one AZC section
    mid_sections = defaultdict(set)
    for folio, middles in folio_middles.items():
        sec = FOLIO_TO_SECTION.get(folio)
        if sec:
            for m in middles:
                mid_sections[m].add(sec)

    # MIDDLEs unique to one section
    single_section_middles = {m: list(secs)[0] for m, secs in mid_sections.items()
                              if len(secs) == 1 and m in mid_to_idx}

    if len(single_section_middles) >= 20:
        sec_indices = []
        sec_labels_true = []
        sec_labels_cluster = []
        for m, sec in single_section_middles.items():
            idx = mid_to_idx[m]
            sec_indices.append(idx)
            sec_labels_true.append(sec)
            sec_labels_cluster.append(best_labels[idx])

        # ARI and NMI between cluster labels and section labels
        ari = adjusted_rand_score(sec_labels_true, sec_labels_cluster)
        nmi = normalized_mutual_info_score(sec_labels_true, sec_labels_cluster)
        print(f"  Section-unique MIDDLEs: {len(single_section_middles)}")
        print(f"  Cluster-Section ARI: {ari:.4f}")
        print(f"  Cluster-Section NMI: {nmi:.4f}")
    else:
        ari = 0
        nmi = 0
        print(f"  Too few section-unique MIDDLEs for alignment test")

    # Step 7: Block vs manifold diagnostic
    print("\n[7/7] Block vs manifold diagnostic...")

    # If block-structured: silhouette should be high (>0.3), clusters well-separated
    # If manifold: silhouette low (<0.2), continuous spread, no clean separation

    best_sil = cluster_results[best_k]['silhouette']

    # Nearest-neighbor distance distribution
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(residual_emb, residual_emb, 'euclidean')
    np.fill_diagonal(dist_matrix, np.inf)
    nn_dists = dist_matrix.min(axis=1)

    print(f"  Nearest-neighbor distance: mean={nn_dists.mean():.3f}, std={nn_dists.std():.3f}")
    print(f"  NN distance CV: {nn_dists.std()/nn_dists.mean():.3f}")
    print(f"  Best silhouette (k={best_k}): {best_sil:.4f}")

    # Gap statistic approximation: compare cluster inertia to random
    from sklearn.cluster import KMeans as KM
    real_inertia = KM(n_clusters=best_k, random_state=42, n_init=5).fit(residual_emb).inertia_

    null_inertias = []
    for trial in range(20):
        rand_emb = rng.normal(0, residual_emb.std(axis=0), size=residual_emb.shape)
        null_inertia = KM(n_clusters=best_k, random_state=42, n_init=5).fit(rand_emb).inertia_
        null_inertias.append(null_inertia)
    null_inertias = np.array(null_inertias)
    gap = np.log(null_inertias.mean()) - np.log(real_inertia)
    print(f"  Gap statistic (k={best_k}): {gap:.4f}")

    # Verdict
    if best_sil > 0.3:
        structure_type = "BLOCK_STRUCTURED"
        structure_explanation = (f"Silhouette {best_sil:.3f} > 0.3 with k={best_k}. "
                                f"Residual space has discrete macro-clusters.")
    elif best_sil > 0.15:
        structure_type = "MIXED_BANDS"
        structure_explanation = (f"Silhouette {best_sil:.3f} ∈ [0.15, 0.30] with k={best_k}. "
                                f"Residual space has fuzzy bands — not clean blocks, not smooth manifold.")
    else:
        structure_type = "CONTINUOUS_MANIFOLD"
        structure_explanation = (f"Silhouette {best_sil:.3f} < 0.15 with k={best_k}. "
                                f"Residual space is a continuous curved manifold without discrete blocks.")

    print(f"\n  Structure type: {structure_type}")
    print(f"  {structure_explanation}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    cos_z_values = [r['cos_z'] for r in folio_cohesion_residual.values()]
    mean_cos_z = np.mean(cos_z_values)
    pct_coherent = 100 * n_coherent / len(folio_list)

    print(f"\n  Hub removal effect:")
    print(f"    Interfolio cosine: 0.9475 → {mean_inter_cos_residual:.4f} (drop = {0.9475 - mean_inter_cos_residual:.4f})")
    print(f"    Folio cohesion: 27/27 → {n_coherent}/{len(folio_list)}")
    print(f"    Mean cos_z: 13.26 → {mean_cos_z:.2f}")
    if section_structure:
        print(f"    Section ratio: 0.944 → {section_structure['ratio']:.3f}")
        print(f"    Section p-value: 0.0006 → {section_structure['mannwhitney_p']:.4f}")

    print(f"\n  Residual structure:")
    print(f"    Type: {structure_type}")
    print(f"    Best k: {best_k}, silhouette: {best_sil:.4f}")
    print(f"    Gap statistic: {gap:.4f}")
    print(f"    Hub-frequency correlation: rho={rho:.3f}")
    print(f"    Residual norm-frequency: rho={rho_res:.3f}")

    print(f"\n  Expert predictions:")
    print(f"    [1] ~10-15 macro-bands: best k={best_k}, sil={best_sil:.3f} → {'CONFIRMED' if 8 <= best_k <= 20 else 'DIFFERENT'}")
    connector_ratio = np.mean(connector_rnorms) / mean_rnorm
    print(f"    [4] Connectors collapse: ratio={connector_ratio:.3f} → {'CONFIRMED' if connector_ratio < 0.8 else 'NOT CONFIRMED'}")

    # Rare tail analysis
    rare_mask = (freqs >= 1) & (freqs <= 2)
    if rare_mask.sum() > 0:
        rare_rnorm = residual_norms[rare_mask].mean()
        print(f"    [5] Rare tail stretches: rare norm={rare_rnorm:.3f} vs mean={mean_rnorm:.3f}, "
              f"ratio={rare_rnorm/mean_rnorm:.3f} → {'CONFIRMED' if rare_rnorm/mean_rnorm > 1.1 else 'NOT CONFIRMED'}")

    # Save results
    results = {
        'test': 'T11_hub_residual_structure',
        'embedding_dim': K_EMBED,
        'hub_eigenvalue': float(hub_val),
        'residual_eigenvalue_range': [float(residual_evals[0]), float(residual_evals[-1])],
        'hub_frequency_rho': float(rho),
        'hub_frequency_p': float(p_rho),
        'residual_norm_frequency_rho': float(rho_res),
        'connector_residual_ratio': float(connector_ratio),
        'hub_by_frequency': hub_by_freq,
        'clustering': {str(k): v for k, v in cluster_results.items()},
        'best_k': best_k,
        'best_silhouette': float(best_sil),
        'gap_statistic': float(gap),
        'structure_type': structure_type,
        'structure_explanation': structure_explanation,
        'folio_cohesion_residual': folio_cohesion_residual,
        'n_coherent': n_coherent,
        'n_tested': len(folio_list),
        'pct_coherent': float(pct_coherent),
        'mean_cos_z': float(mean_cos_z),
        'interfolio_cos_residual': float(mean_inter_cos_residual),
        'interfolio_dist_residual': float(mean_inter_dist_residual),
        'section_structure': section_structure,
        'cluster_section_ari': float(ari),
        'cluster_section_nmi': float(nmi),
        'nn_dist_mean': float(nn_dists.mean()),
        'nn_dist_cv': float(nn_dists.std() / nn_dists.mean()),
    }

    with open(RESULTS_DIR / 't11_hub_residual_structure.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't11_hub_residual_structure.json'}")


if __name__ == '__main__':
    run()
