#!/usr/bin/env python3
"""
T1: Residual Embedding Projection
B_EXCLUSIVE_GEOMETRIC_INTEGRATION phase

Project B-exclusive MIDDLEs into A's 100D residual space using sub-component
overlap. Measure distance to nearest A point, cosine distribution vs shared types.

Outcomes:
- Cluster near origin → non-discriminative elaborations
- Distribute like shared types → unified manifold
- New directional structure → potential second geometry
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from scipy.spatial.distance import cdist

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99


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
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    return all_middles, mid_to_idx


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    res_scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * res_scaling[np.newaxis, :]


def get_b_exclusive_middles(mid_to_idx):
    """Get MIDDLEs that appear in B but NOT in A's 972-MIDDLE space."""
    tx = Transcript()
    morph = Morphology()
    b_middles = set()
    b_mid_counts = Counter()
    b_mid_folios = defaultdict(set)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            b_middles.add(m.middle)
            b_mid_counts[m.middle] += 1
            b_mid_folios[m.middle].add(token.folio)

    shared = b_middles & set(mid_to_idx.keys())
    exclusive = b_middles - set(mid_to_idx.keys())

    return sorted(exclusive), sorted(shared), b_mid_counts, b_mid_folios


def project_via_atoms(exclusive_middles, mid_to_idx, res_emb, a_middles):
    """Project B-exclusive MIDDLEs via sub-component atom overlap."""
    # Build atom set from A-space core MIDDLEs (len >= 2)
    a_atoms = {m for m in a_middles if len(m) >= 2}

    projections = {}
    atom_stats = {}

    for mid in exclusive_middles:
        # Find A-space MIDDLEs contained as substrings
        contained = []
        for atom in a_atoms:
            if atom in mid and atom != mid:
                contained.append(atom)

        if not contained:
            atom_stats[mid] = {'n_atoms': 0, 'atoms': []}
            continue

        # Remove redundant (keep maximal)
        contained.sort(key=len, reverse=True)
        maximal = []
        for atom in contained:
            if not any(atom in longer for longer in maximal):
                maximal.append(atom)

        # Project as centroid of atom embeddings
        atom_indices = [mid_to_idx[a] for a in maximal if a in mid_to_idx]
        if not atom_indices:
            atom_stats[mid] = {'n_atoms': len(maximal), 'atoms': maximal,
                               'note': 'atoms not in idx'}
            continue

        atom_vecs = res_emb[atom_indices]
        centroid = np.mean(atom_vecs, axis=0)
        projections[mid] = centroid
        atom_stats[mid] = {
            'n_atoms': len(maximal),
            'atoms': maximal,
            'n_projected': len(atom_indices),
        }

    return projections, atom_stats


def main():
    print("=" * 60)
    print("T1: Residual Embedding Projection")
    print("=" * 60)

    # Setup
    print("\n[1] Loading...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    a_middles, mid_to_idx = reconstruct_middle_list()
    res_emb = build_residual_embedding(compat_matrix)
    print(f"  A-space: {len(a_middles)} MIDDLEs, {K_RESIDUAL}D residual embedding")

    # Get B-exclusive MIDDLEs
    print("\n[2] Identifying B-exclusive MIDDLEs...")
    exclusive, shared, b_counts, b_folios = get_b_exclusive_middles(mid_to_idx)
    print(f"  B total unique MIDDLEs: {len(exclusive) + len(shared)}")
    print(f"  Shared with A: {len(shared)}")
    print(f"  B-exclusive: {len(exclusive)}")

    # Frequency profile of exclusive vs shared
    exc_counts = [b_counts[m] for m in exclusive]
    sha_counts = [b_counts[m] for m in shared]
    print(f"\n  Frequency profile:")
    print(f"  Exclusive: mean={np.mean(exc_counts):.1f}, median={np.median(exc_counts):.0f}, "
          f"max={max(exc_counts)}")
    print(f"  Shared:    mean={np.mean(sha_counts):.1f}, median={np.median(sha_counts):.0f}, "
          f"max={max(sha_counts)}")

    exc_folio_counts = [len(b_folios[m]) for m in exclusive]
    sha_folio_counts = [len(b_folios[m]) for m in shared]
    print(f"\n  Folio spread:")
    print(f"  Exclusive: mean={np.mean(exc_folio_counts):.1f}, "
          f"median={np.median(exc_folio_counts):.0f}")
    print(f"  Shared:    mean={np.mean(sha_folio_counts):.1f}, "
          f"median={np.median(sha_folio_counts):.0f}")

    # Length profile
    exc_lens = [len(m) for m in exclusive]
    sha_lens = [len(m) for m in shared]
    print(f"\n  Length profile:")
    print(f"  Exclusive: mean={np.mean(exc_lens):.1f}, range=[{min(exc_lens)}, {max(exc_lens)}]")
    print(f"  Shared:    mean={np.mean(sha_lens):.1f}, range=[{min(sha_lens)}, {max(sha_lens)}]")

    # Step 3: Project via sub-component atoms
    print("\n[3] Projecting B-exclusive MIDDLEs via atom overlap...")
    projections, atom_stats = project_via_atoms(exclusive, mid_to_idx, res_emb, a_middles)

    n_projected = len(projections)
    n_no_atoms = sum(1 for s in atom_stats.values() if s['n_atoms'] == 0)
    n_with_atoms = len(exclusive) - n_no_atoms
    print(f"  B-exclusive with A-space atoms: {n_with_atoms}/{len(exclusive)} "
          f"({n_with_atoms/len(exclusive):.1%})")
    print(f"  Successfully projected: {n_projected}/{len(exclusive)} "
          f"({n_projected/len(exclusive):.1%})")
    print(f"  No A-space atoms found: {n_no_atoms}")

    # Atom count distribution
    atom_counts = [s['n_atoms'] for s in atom_stats.values()]
    atom_counter = Counter(atom_counts)
    print(f"  Atom count distribution: {dict(sorted(atom_counter.items()))}")

    if n_projected == 0:
        print("\nNo projections possible. Cannot analyze geometry.")
        results = {
            'test': 'T1_residual_projection',
            'n_exclusive': len(exclusive),
            'n_projected': 0,
            'verdict': 'UNPROJECTABLE',
            'explanation': 'No B-exclusive MIDDLEs could be projected via atom overlap.',
        }
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_DIR / 't1_residual_projection.json', 'w') as f:
            json.dump(results, f, indent=2)
        return

    # Step 4: Analyze projected positions
    print("\n[4] Analyzing projected positions in residual space...")
    proj_vecs = np.array([projections[m] for m in sorted(projections.keys())])
    proj_norms = np.linalg.norm(proj_vecs, axis=1)

    # Compare to A-space norms
    a_norms = np.linalg.norm(res_emb, axis=1)

    # Also compare to shared B MIDDLEs' norms
    shared_indices = [mid_to_idx[m] for m in shared if m in mid_to_idx]
    shared_norms = a_norms[shared_indices]

    print(f"  Projected norm: mean={np.mean(proj_norms):.4f}, "
          f"median={np.median(proj_norms):.4f}")
    print(f"  A-space norm:   mean={np.mean(a_norms):.4f}, "
          f"median={np.median(a_norms):.4f}")
    print(f"  Shared B norm:  mean={np.mean(shared_norms):.4f}, "
          f"median={np.median(shared_norms):.4f}")

    # KS test: projected vs A-space
    ks_proj_a, p_proj_a = stats.ks_2samp(proj_norms, a_norms)
    ks_proj_sh, p_proj_sh = stats.ks_2samp(proj_norms, shared_norms)
    print(f"\n  Projected vs A-space norms: KS={ks_proj_a:.3f}, p={p_proj_a:.2e}")
    print(f"  Projected vs Shared norms: KS={ks_proj_sh:.3f}, p={p_proj_sh:.2e}")

    # Step 5: Distance to nearest A point
    print("\n[5] Distance to nearest A-space point...")
    # For each projected point, find nearest A-space point
    dists = cdist(proj_vecs, res_emb, metric='euclidean')
    min_dists = np.min(dists, axis=1)
    print(f"  Min distance: mean={np.mean(min_dists):.4f}, "
          f"median={np.median(min_dists):.4f}")

    # Compare to within-A distances
    # Random sample of A-to-A nearest neighbor distances
    rng = np.random.default_rng(42)
    a_sample = rng.choice(len(a_middles), size=min(500, len(a_middles)), replace=False)
    a_sample_dists = cdist(res_emb[a_sample], res_emb, metric='euclidean')
    # Set self-distance to inf
    for i, idx in enumerate(a_sample):
        a_sample_dists[i, idx] = np.inf
    a_nn_dists = np.min(a_sample_dists, axis=1)

    print(f"  A-to-A NN distance: mean={np.mean(a_nn_dists):.4f}, "
          f"median={np.median(a_nn_dists):.4f}")
    print(f"  Ratio (projected / A-to-A): {np.mean(min_dists)/np.mean(a_nn_dists):.2f}")

    ks_nn, p_nn = stats.ks_2samp(min_dists, a_nn_dists)
    print(f"  KS test: {ks_nn:.3f}, p={p_nn:.2e}")

    # Step 6: Cosine similarity to A-space
    print("\n[6] Cosine similarity analysis...")
    # Mean cosine between each projected point and all A points
    proj_normed = proj_vecs / (np.linalg.norm(proj_vecs, axis=1, keepdims=True) + 1e-10)
    a_normed = res_emb / (np.linalg.norm(res_emb, axis=1, keepdims=True) + 1e-10)

    cos_to_a = proj_normed @ a_normed.T
    mean_cos_per_proj = np.mean(cos_to_a, axis=1)
    max_cos_per_proj = np.max(cos_to_a, axis=1)

    print(f"  Mean cosine to A-space: {np.mean(mean_cos_per_proj):.4f}")
    print(f"  Max cosine to nearest A: {np.mean(max_cos_per_proj):.4f}")

    # Compare to within-A cosine
    a_cos = a_normed[a_sample] @ a_normed.T
    for i, idx in enumerate(a_sample):
        a_cos[i, idx] = -2  # Exclude self
    a_max_cos = np.max(a_cos, axis=1)
    a_mean_cos = np.mean(a_cos, axis=1)

    print(f"  A-to-A mean cosine: {np.mean(a_mean_cos):.4f}")
    print(f"  A-to-A max cosine: {np.mean(a_max_cos):.4f}")

    # Step 7: Do projections cluster or spread?
    print("\n[7] Directional structure test...")
    # PCA on projected points — do they span new directions?
    if n_projected >= 10:
        proj_centered = proj_vecs - np.mean(proj_vecs, axis=0)
        cov = np.cov(proj_centered.T)
        evals_proj = np.sort(np.linalg.eigvalsh(cov))[::-1]
        var_explained_1 = evals_proj[0] / np.sum(evals_proj)
        var_explained_3 = np.sum(evals_proj[:3]) / np.sum(evals_proj)
        print(f"  PC1 explains: {var_explained_1:.1%} of projected variance")
        print(f"  PC1-3 explain: {var_explained_3:.1%}")

        # Compare to A-space PCA
        a_centered = res_emb - np.mean(res_emb, axis=0)
        cov_a = np.cov(a_centered.T)
        evals_a = np.sort(np.linalg.eigvalsh(cov_a))[::-1]
        a_var_1 = evals_a[0] / np.sum(evals_a)
        a_var_3 = np.sum(evals_a[:3]) / np.sum(evals_a)
        print(f"  A-space PC1: {a_var_1:.1%}, PC1-3: {a_var_3:.1%}")

        # Alignment: do projected PCs align with A PCs?
        _, proj_evecs = np.linalg.eigh(cov)
        _, a_evecs = np.linalg.eigh(cov_a)
        # Top 3 PCs alignment (absolute cosine)
        proj_top3 = proj_evecs[:, -3:]
        a_top3 = a_evecs[:, -3:]
        alignment = np.abs(proj_top3.T @ a_top3)
        max_alignment = np.max(alignment, axis=1)
        print(f"  Top-3 PC alignment with A: {max_alignment}")
        mean_alignment = np.mean(max_alignment)
        print(f"  Mean max alignment: {mean_alignment:.3f}")

    # Verdict
    print("\n" + "=" * 60)

    # Key metrics for verdict
    norm_ratio = np.mean(proj_norms) / np.mean(a_norms)
    dist_ratio = np.mean(min_dists) / np.mean(a_nn_dists)
    atom_coverage = n_with_atoms / len(exclusive)

    if atom_coverage > 0.80 and dist_ratio < 2.0 and norm_ratio > 0.5:
        verdict = "SUBORDINATE"
        explanation = (
            f"B-exclusive MIDDLEs project into A's manifold: "
            f"{atom_coverage:.0%} contain A atoms, "
            f"norm ratio {norm_ratio:.2f}, "
            f"distance ratio {dist_ratio:.2f}. "
            f"They are manifold tail extensions, not a second geometry."
        )
    elif atom_coverage > 0.80 and dist_ratio >= 2.0:
        verdict = "PERIPHERAL"
        explanation = (
            f"{atom_coverage:.0%} contain A atoms but sit far from A-space "
            f"(dist ratio {dist_ratio:.2f}). "
            f"Peripheral extensions with some independence."
        )
    elif atom_coverage <= 0.80:
        verdict = "POTENTIALLY_INDEPENDENT"
        explanation = (
            f"Only {atom_coverage:.0%} contain A atoms. "
            f"Substantial fraction may form independent structure."
        )
    else:
        verdict = "AMBIGUOUS"
        explanation = "Mixed signals — requires further investigation."

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save
    results = {
        'test': 'T1_residual_projection',
        'n_a_middles': len(a_middles),
        'n_b_exclusive': len(exclusive),
        'n_b_shared': len(shared),
        'frequency_profile': {
            'exclusive_mean': float(np.mean(exc_counts)),
            'exclusive_median': float(np.median(exc_counts)),
            'shared_mean': float(np.mean(sha_counts)),
            'shared_median': float(np.median(sha_counts)),
        },
        'length_profile': {
            'exclusive_mean': float(np.mean(exc_lens)),
            'shared_mean': float(np.mean(sha_lens)),
        },
        'folio_spread': {
            'exclusive_mean': float(np.mean(exc_folio_counts)),
            'shared_mean': float(np.mean(sha_folio_counts)),
        },
        'atom_coverage': float(atom_coverage),
        'n_projected': n_projected,
        'n_no_atoms': n_no_atoms,
        'norm_analysis': {
            'projected_mean': float(np.mean(proj_norms)),
            'a_space_mean': float(np.mean(a_norms)),
            'shared_mean': float(np.mean(shared_norms)),
            'norm_ratio': float(norm_ratio),
        },
        'distance_analysis': {
            'projected_to_a_mean': float(np.mean(min_dists)),
            'a_to_a_nn_mean': float(np.mean(a_nn_dists)),
            'dist_ratio': float(dist_ratio),
        },
        'cosine_analysis': {
            'projected_mean_cos': float(np.mean(mean_cos_per_proj)),
            'projected_max_cos': float(np.mean(max_cos_per_proj)),
            'a_mean_cos': float(np.mean(a_mean_cos)),
            'a_max_cos': float(np.mean(a_max_cos)),
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't1_residual_projection.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't1_residual_projection.json'}")


if __name__ == '__main__':
    main()
