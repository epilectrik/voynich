#!/usr/bin/env python3
"""
T10: AZC Folio Submanifold Projection
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Test whether AZC folios correspond to coherent subregions of the
~100D MIDDLE discrimination space.

Hypothesis: Each AZC folio is a "local coordinate chart" — a coherent
slice through the constraint manifold. If true:
- Within-folio MIDDLEs cluster tightly in the latent embedding
- Between-folio overlaps reflect manifold adjacency
- Zone progression (C→R→S) tracks constraint intensity gradients
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
K_EMBED = 100  # Embedding dimensionality
N_NULL = 1000  # Null trials for cohesion test
MIN_MIDDLES = 5  # Minimum MIDDLEs per folio to include

# AZC section assignments (from architecture docs)
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


def reconstruct_middle_list():
    """Reconstruct the MIDDLE ordering from T1 (sorted alphabetical)."""
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


def build_embedding(compat_matrix, n_components=K_EMBED):
    """Build spectral embedding: top eigenvectors scaled by sqrt(eigenvalue)."""
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))

    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Take top K components
    evals = eigenvalues[:n_components]
    evecs = eigenvectors[:, :n_components]

    # Scale by sqrt(eigenvalue) — high-variance axes get more weight
    pos_evals = np.maximum(evals, 0)  # Clip negatives
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]

    return embedding, evals


def extract_azc_folio_middles(mid_to_idx):
    """Extract per-AZC-folio MIDDLE inventories (diagram tokens only)."""
    tx = Transcript()
    morph = Morphology()

    folio_middles = defaultdict(set)

    for token in tx.azc():
        # Exclude P-placement (Currier A text on AZC folios)
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


def cosine_similarity_matrix(vectors):
    """Compute pairwise cosine similarity for a set of vectors."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)  # Avoid division by zero
    normed = vectors / norms
    return normed @ normed.T


def compute_folio_cohesion(embedding, folio_indices, n_null=N_NULL):
    """Compute intrafolio cohesion and compare to null."""
    n_total = embedding.shape[0]
    folio_vecs = embedding[folio_indices]
    n_folio = len(folio_indices)

    if n_folio < 2:
        return None

    # Centroid
    centroid = folio_vecs.mean(axis=0)

    # Mean pairwise cosine similarity
    cos_sim = cosine_similarity_matrix(folio_vecs)
    triu_idx = np.triu_indices(n_folio, k=1)
    mean_cos = float(cos_sim[triu_idx].mean()) if len(triu_idx[0]) > 0 else 0

    # Mean distance to centroid
    dists = np.linalg.norm(folio_vecs - centroid, axis=1)
    mean_radius = float(dists.mean())

    # Null distribution: random subsets of same size
    null_cos = []
    null_radius = []
    rng = np.random.RandomState(42)

    for _ in range(n_null):
        rand_idx = rng.choice(n_total, n_folio, replace=False)
        rand_vecs = embedding[rand_idx]

        # Cosine
        rand_cos_mat = cosine_similarity_matrix(rand_vecs)
        rand_triu = np.triu_indices(n_folio, k=1)
        null_cos.append(float(rand_cos_mat[rand_triu].mean()) if len(rand_triu[0]) > 0 else 0)

        # Radius
        rand_centroid = rand_vecs.mean(axis=0)
        rand_dists = np.linalg.norm(rand_vecs - rand_centroid, axis=1)
        null_radius.append(float(rand_dists.mean()))

    null_cos = np.array(null_cos)
    null_radius = np.array(null_radius)

    # Z-scores (positive z for cosine = tighter than random; negative z for radius = tighter)
    cos_z = (mean_cos - null_cos.mean()) / null_cos.std() if null_cos.std() > 0 else 0
    radius_z = (mean_radius - null_radius.mean()) / null_radius.std() if null_radius.std() > 0 else 0

    return {
        'n_middles': n_folio,
        'mean_cosine_sim': float(mean_cos),
        'mean_radius': float(mean_radius),
        'null_cos_mean': float(null_cos.mean()),
        'null_cos_std': float(null_cos.std()),
        'cos_z': float(cos_z),
        'null_radius_mean': float(null_radius.mean()),
        'null_radius_std': float(null_radius.std()),
        'radius_z': float(radius_z),
        'centroid': centroid,
    }


def run():
    print("=" * 70)
    print("T10: AZC Folio Submanifold Projection")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Step 1: Reconstruct MIDDLE list and load matrix
    print("\n[1/6] Loading discrimination space...")
    all_middles, mid_to_idx = reconstruct_middle_list()
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')
    n = len(all_middles)
    print(f"  {n} MIDDLEs, matrix shape {M.shape}")
    assert M.shape == (n, n), f"Matrix shape {M.shape} != ({n}, {n})"

    # Step 2: Build 100D embedding
    print(f"\n[2/6] Building {K_EMBED}D spectral embedding...")
    embedding, eigenvalues = build_embedding(M, K_EMBED)
    print(f"  Embedding shape: {embedding.shape}")
    print(f"  Top 5 eigenvalues: {eigenvalues[:5]}")
    print(f"  Eigenvalue range: {eigenvalues[0]:.1f} to {eigenvalues[-1]:.1f}")
    variance_captured = eigenvalues[eigenvalues > 0].sum() / np.load(RESULTS_DIR / 't1_eigenvalues.npy')[np.load(RESULTS_DIR / 't1_eigenvalues.npy') > 0].sum()
    print(f"  Variance captured (top {K_EMBED}): {variance_captured:.1%}")

    # Step 3: Extract AZC folio MIDDLEs
    print(f"\n[3/6] Extracting AZC folio MIDDLE inventories...")
    folio_middles = extract_azc_folio_middles(mid_to_idx)

    # Convert to indices
    folio_indices = {}
    for folio, middles in folio_middles.items():
        indices = sorted([mid_to_idx[m] for m in middles])
        if len(indices) >= MIN_MIDDLES:
            folio_indices[folio] = np.array(indices)

    total_azc_middles = set()
    for middles in folio_middles.values():
        total_azc_middles.update(middles)

    print(f"  AZC folios found: {len(folio_middles)}")
    print(f"  Folios with >= {MIN_MIDDLES} MIDDLEs: {len(folio_indices)}")
    print(f"  Total unique AZC MIDDLEs in space: {len(total_azc_middles)} / {n} ({100*len(total_azc_middles)/n:.1f}%)")

    for folio in sorted(folio_indices.keys()):
        sec = FOLIO_TO_SECTION.get(folio, '?')
        print(f"    {folio} ({sec}): {len(folio_indices[folio])} MIDDLEs")

    # Step 4: Intrafolio cohesion
    print(f"\n[4/6] Computing intrafolio cohesion ({N_NULL} null trials each)...")
    cohesion_results = {}
    n_coherent = 0
    n_tested = 0

    print(f"\n  {'Folio':<10} {'Sec':>3} {'N':>4} {'CosSim':>8} {'NullCos':>8} {'CosZ':>7} {'Radius':>8} {'NullRad':>8} {'RadZ':>7}")
    print(f"  {'-'*75}")

    for folio in sorted(folio_indices.keys()):
        sec = FOLIO_TO_SECTION.get(folio, '?')
        result = compute_folio_cohesion(embedding, folio_indices[folio])
        if result is None:
            continue

        n_tested += 1
        centroid = result.pop('centroid')  # Remove for JSON serialization
        cohesion_results[folio] = result
        cohesion_results[folio]['section'] = sec

        is_coherent = result['cos_z'] > 2.0
        if is_coherent:
            n_coherent += 1

        flag = " ***" if is_coherent else ""
        print(f"  {folio:<10} {sec:>3} {result['n_middles']:>4} {result['mean_cosine_sim']:>8.4f} "
              f"{result['null_cos_mean']:>8.4f} {result['cos_z']:>7.2f} "
              f"{result['mean_radius']:>8.2f} {result['null_radius_mean']:>8.2f} {result['radius_z']:>7.2f}{flag}")

    print(f"\n  Coherent folios (cos_z > 2.0): {n_coherent} / {n_tested}")

    # Step 5: Interfolio separation
    print(f"\n[5/6] Computing interfolio separation...")

    # Compute centroids
    folio_centroids = {}
    for folio, indices in folio_indices.items():
        folio_centroids[folio] = embedding[indices].mean(axis=0)

    folio_list = sorted(folio_centroids.keys())
    n_folios = len(folio_list)
    centroid_matrix = np.array([folio_centroids[f] for f in folio_list])

    # Pairwise centroid cosine similarity
    centroid_cos = cosine_similarity_matrix(centroid_matrix)
    triu = np.triu_indices(n_folios, k=1)
    mean_interfolio_cos = float(centroid_cos[triu].mean())

    # Pairwise centroid Euclidean distance
    from scipy.spatial.distance import pdist, squareform
    centroid_dists = squareform(pdist(centroid_matrix, 'euclidean'))
    mean_interfolio_dist = float(centroid_dists[triu].mean())

    print(f"  Mean interfolio centroid cosine similarity: {mean_interfolio_cos:.4f}")
    print(f"  Mean interfolio centroid Euclidean distance: {mean_interfolio_dist:.2f}")

    # Null: random subset centroids
    rng = np.random.RandomState(123)
    null_inter_cos = []
    null_inter_dist = []
    sizes = [len(folio_indices[f]) for f in folio_list]

    for _ in range(500):
        rand_centroids = []
        for size in sizes:
            rand_idx = rng.choice(n, size, replace=False)
            rand_centroids.append(embedding[rand_idx].mean(axis=0))
        rand_centroids = np.array(rand_centroids)

        rand_cos = cosine_similarity_matrix(rand_centroids)
        null_inter_cos.append(float(rand_cos[triu].mean()))

        rand_dists = squareform(pdist(rand_centroids, 'euclidean'))
        null_inter_dist.append(float(rand_dists[triu].mean()))

    null_inter_cos = np.array(null_inter_cos)
    null_inter_dist = np.array(null_inter_dist)

    inter_cos_z = (mean_interfolio_cos - null_inter_cos.mean()) / null_inter_cos.std() if null_inter_cos.std() > 0 else 0
    inter_dist_z = (mean_interfolio_dist - null_inter_dist.mean()) / null_inter_dist.std() if null_inter_dist.std() > 0 else 0

    print(f"  Null mean interfolio cosine: {null_inter_cos.mean():.4f} ± {null_inter_cos.std():.4f}")
    print(f"  Interfolio cosine z-score: {inter_cos_z:.2f}")
    print(f"  Null mean interfolio distance: {null_inter_dist.mean():.2f} ± {null_inter_dist.std():.2f}")
    print(f"  Interfolio distance z-score: {inter_dist_z:.2f}")

    separation_results = {
        'mean_interfolio_cos': float(mean_interfolio_cos),
        'null_inter_cos_mean': float(null_inter_cos.mean()),
        'null_inter_cos_std': float(null_inter_cos.std()),
        'inter_cos_z': float(inter_cos_z),
        'mean_interfolio_dist': float(mean_interfolio_dist),
        'null_inter_dist_mean': float(null_inter_dist.mean()),
        'null_inter_dist_std': float(null_inter_dist.std()),
        'inter_dist_z': float(inter_dist_z),
    }

    # Step 6: Section-level structure
    print(f"\n[6/6] Section-level structure...")

    section_centroids = {}
    for sec in ['Z', 'A', 'C']:
        sec_folios = [f for f in folio_list if FOLIO_TO_SECTION.get(f) == sec]
        if not sec_folios:
            continue
        sec_indices = []
        for f in sec_folios:
            sec_indices.extend(folio_indices[f].tolist())
        sec_indices = list(set(sec_indices))  # Unique MIDDLEs across section
        if sec_indices:
            section_centroids[sec] = embedding[sec_indices].mean(axis=0)
            print(f"  Section {sec}: {len(sec_folios)} folios, {len(sec_indices)} unique MIDDLEs")

    # Within-section vs between-section folio centroid distances
    within_dists = []
    between_dists = []

    for i, fi in enumerate(folio_list):
        for j, fj in enumerate(folio_list):
            if i >= j:
                continue
            sec_i = FOLIO_TO_SECTION.get(fi)
            sec_j = FOLIO_TO_SECTION.get(fj)
            d = float(centroid_dists[i, j])
            if sec_i and sec_j:
                if sec_i == sec_j:
                    within_dists.append(d)
                else:
                    between_dists.append(d)

    if within_dists and between_dists:
        mean_within = np.mean(within_dists)
        mean_between = np.mean(between_dists)
        ratio = mean_within / mean_between if mean_between > 0 else float('inf')
        print(f"\n  Within-section mean distance: {mean_within:.2f} ({len(within_dists)} pairs)")
        print(f"  Between-section mean distance: {mean_between:.2f} ({len(between_dists)} pairs)")
        print(f"  Within/Between ratio: {ratio:.3f}")

        # Mann-Whitney U test
        from scipy.stats import mannwhitneyu
        stat, p_val = mannwhitneyu(within_dists, between_dists, alternative='less')
        print(f"  Mann-Whitney U (within < between): U={stat:.0f}, p={p_val:.4f}")

        section_structure = {
            'mean_within_dist': float(mean_within),
            'mean_between_dist': float(mean_between),
            'within_between_ratio': float(ratio),
            'n_within_pairs': len(within_dists),
            'n_between_pairs': len(between_dists),
            'mannwhitney_U': float(stat),
            'mannwhitney_p': float(p_val),
        }
    else:
        section_structure = {'error': 'insufficient data'}
        print("  Insufficient data for section analysis")

    # Within-section cosine similarity vs between
    within_cos = []
    between_cos = []
    for i, fi in enumerate(folio_list):
        for j, fj in enumerate(folio_list):
            if i >= j:
                continue
            sec_i = FOLIO_TO_SECTION.get(fi)
            sec_j = FOLIO_TO_SECTION.get(fj)
            c = float(centroid_cos[i, j])
            if sec_i and sec_j:
                if sec_i == sec_j:
                    within_cos.append(c)
                else:
                    between_cos.append(c)

    if within_cos and between_cos:
        mean_within_cos = np.mean(within_cos)
        mean_between_cos = np.mean(between_cos)
        print(f"\n  Within-section mean cosine: {mean_within_cos:.4f}")
        print(f"  Between-section mean cosine: {mean_between_cos:.4f}")
        section_structure['mean_within_cos'] = float(mean_within_cos)
        section_structure['mean_between_cos'] = float(mean_between_cos)

    # Zone-ordered trajectory analysis
    print(f"\n  Zone-ordered trajectory analysis...")
    tx = Transcript()
    morph = Morphology()

    # Collect per-folio per-zone MIDDLEs
    folio_zone_middles = defaultdict(lambda: defaultdict(set))
    for token in tx.azc():
        if hasattr(token, 'placement') and token.placement and \
           token.placement.startswith('P'):
            continue
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx and hasattr(token, 'placement'):
            placement = token.placement if token.placement else ''
            # Extract zone type: C, R1, R2, R3, S1, S2
            zone = None
            if placement.startswith('C'):
                zone = 'C'
            elif placement.startswith('R'):
                # Try to extract R1, R2, R3
                if len(placement) >= 2 and placement[1].isdigit():
                    zone = placement[:2]
                else:
                    zone = 'R'
            elif placement.startswith('S'):
                if len(placement) >= 2 and placement[1].isdigit():
                    zone = placement[:2]
                else:
                    zone = 'S'
            if zone:
                folio_zone_middles[token.folio][zone].add(m.middle)

    # For folios with multiple zones, compute zone centroids
    zone_order = ['C', 'R1', 'R2', 'R3', 'S1', 'S2']
    zone_trajectories = {}
    n_trajectory_folios = 0

    for folio in sorted(folio_zone_middles.keys()):
        zones_present = [z for z in zone_order if z in folio_zone_middles[folio]
                        and len(folio_zone_middles[folio][z]) >= 3]
        if len(zones_present) >= 2:
            zone_cents = {}
            for z in zones_present:
                z_indices = [mid_to_idx[m] for m in folio_zone_middles[folio][z]
                           if m in mid_to_idx]
                if z_indices:
                    zone_cents[z] = embedding[z_indices].mean(axis=0)

            if len(zone_cents) >= 2:
                n_trajectory_folios += 1
                ordered_zones = [z for z in zone_order if z in zone_cents]
                # Compute sequential distances
                seq_dists = []
                for i in range(len(ordered_zones) - 1):
                    d = np.linalg.norm(zone_cents[ordered_zones[i]] - zone_cents[ordered_zones[i+1]])
                    seq_dists.append(float(d))

                zone_trajectories[folio] = {
                    'zones': ordered_zones,
                    'zone_sizes': {z: len(folio_zone_middles[folio][z]) for z in ordered_zones},
                    'sequential_distances': seq_dists,
                    'total_trajectory_length': sum(seq_dists),
                }

    print(f"  Folios with zone trajectories: {n_trajectory_folios}")
    for folio, traj in sorted(zone_trajectories.items()):
        sec = FOLIO_TO_SECTION.get(folio, '?')
        zones_str = '→'.join(traj['zones'])
        sizes_str = ','.join(str(traj['zone_sizes'][z]) for z in traj['zones'])
        print(f"    {folio} ({sec}): {zones_str} sizes=[{sizes_str}] dists={[f'{d:.2f}' for d in traj['sequential_distances']]}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    # Cohesion summary
    cos_z_values = [r['cos_z'] for r in cohesion_results.values()]
    mean_cos_z = np.mean(cos_z_values) if cos_z_values else 0
    pct_coherent = 100 * n_coherent / n_tested if n_tested > 0 else 0

    print(f"\n  Intrafolio cohesion:")
    print(f"    Folios tested: {n_tested}")
    print(f"    Coherent (cos_z > 2.0): {n_coherent} ({pct_coherent:.0f}%)")
    print(f"    Mean cos_z: {mean_cos_z:.2f}")

    print(f"\n  Interfolio separation:")
    print(f"    Centroid cosine z: {inter_cos_z:.2f}")
    print(f"    Centroid distance z: {inter_dist_z:.2f}")

    if 'within_between_ratio' in section_structure:
        print(f"\n  Section structure:")
        print(f"    Within/Between distance ratio: {section_structure['within_between_ratio']:.3f}")
        print(f"    Mann-Whitney p: {section_structure['mannwhitney_p']:.4f}")

    # Verdict
    if pct_coherent >= 50 and section_structure.get('mannwhitney_p', 1.0) < 0.05:
        verdict = "COHERENT_SUBMANIFOLDS"
        explanation = (f"{n_coherent}/{n_tested} AZC folios show significantly tighter "
                      f"MIDDLE clustering than random subsets (mean cos_z={mean_cos_z:.2f}). "
                      f"Section structure is significant (p={section_structure['mannwhitney_p']:.4f}). "
                      f"AZC folios correspond to coherent subregions of the discrimination space.")
    elif pct_coherent >= 25 or mean_cos_z > 1.5:
        verdict = "PARTIAL_COHERENCE"
        explanation = (f"{n_coherent}/{n_tested} folios coherent, mean cos_z={mean_cos_z:.2f}. "
                      f"Some AZC folios are coherent submanifolds but the pattern is not systematic.")
    else:
        verdict = "NO_STRUCTURE"
        explanation = (f"Only {n_coherent}/{n_tested} folios coherent, mean cos_z={mean_cos_z:.2f}. "
                      f"AZC folio projections are indistinguishable from random subsets.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save results
    results = {
        'test': 'T10_azc_submanifold_projection',
        'embedding_dim': K_EMBED,
        'n_middles_total': n,
        'n_azc_middles_in_space': len(total_azc_middles),
        'azc_coverage_pct': float(100 * len(total_azc_middles) / n),
        'n_folios_tested': n_tested,
        'n_coherent': n_coherent,
        'pct_coherent': float(pct_coherent),
        'mean_cos_z': float(mean_cos_z),
        'cohesion_by_folio': cohesion_results,
        'separation': separation_results,
        'section_structure': section_structure,
        'zone_trajectories': {k: v for k, v in zone_trajectories.items()},
        'verdict': verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't10_azc_submanifold_projection.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't10_azc_submanifold_projection.json'}")


if __name__ == '__main__':
    run()
