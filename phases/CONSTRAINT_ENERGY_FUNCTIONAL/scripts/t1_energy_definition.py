#!/usr/bin/env python3
"""
T1: Energy Functional Definition and Line-Level Distribution
CONSTRAINT_ENERGY_FUNCTIONAL phase

Define E(line) = mean pairwise residual cosine similarity of MIDDLEs on the line.
Residual = eigenvectors 2-100 (hub removed, per C986).

Tests:
1. Distribution shape, quartiles, mean, variance
2. Correlation with line length (expect weak — normalized)
3. Null comparison: random MIDDLE subsets of matching size
4. Coverage: fraction of B lines with >=2 A-space MIDDLEs
5. Compare A-line energy to B-line energy
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99  # Eigenvectors 2-100
N_NULL = 1000


def reconstruct_middle_list():
    """Reconstruct the MIDDLE ordering from T1 (alphabetical, Currier A)."""
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
    """Build residual embedding: eigenvectors 2-100, hub removed."""
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Residual = skip hub (eigenvector 0)
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    res_scaling = np.sqrt(np.maximum(res_evals, 0))
    res_emb = res_evecs * res_scaling[np.newaxis, :]

    print(f"  Hub eigenvalue: {eigenvalues[0]:.2f}")
    print(f"  Residual eigenvalue range: [{res_evals[0]:.2f}, {res_evals[-1]:.2f}]")
    return res_emb, eigenvalues


def compute_line_energy(indices, embedding):
    """Compute E(line) = mean pairwise cosine similarity in residual space.

    Returns E value or None if <2 valid indices.
    """
    if len(indices) < 2:
        return None

    vecs = embedding[indices]
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)

    # Skip zero-norm vectors
    valid = (norms.flatten() > 1e-10)
    if valid.sum() < 2:
        return None

    vecs = vecs[valid]
    norms = norms[valid]
    normed = vecs / norms

    # Pairwise cosine similarity (upper triangle)
    cos_matrix = normed @ normed.T
    n = len(normed)
    triu_idx = np.triu_indices(n, k=1)
    cosines = cos_matrix[triu_idx]

    return float(np.mean(cosines))


def extract_line_middles(token_iter, mid_to_idx):
    """Extract per-line MIDDLE inventories from a token iterator.

    Returns dict: (folio, line) -> list of indices into A-space.
    Also returns total lines and lines with >=2 A-space MIDDLEs.
    """
    morph = Morphology()
    line_middles = defaultdict(set)
    line_all_middles = defaultdict(set)  # Including non-A-space

    for token in token_iter:
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            key = (token.folio, token.line)
            line_all_middles[key].add(m.middle)
            if m.middle in mid_to_idx:
                line_middles[key].add(m.middle)

    # Convert to index lists
    line_indices = {}
    for key, middles in line_middles.items():
        indices = [mid_to_idx[m] for m in middles]
        line_indices[key] = indices

    return line_indices, line_all_middles


def compute_null_energies(embedding, size_counts, n_null=N_NULL, rng=None):
    """Compute null energy distribution for each line size.

    size_counts: dict of size -> count (how many lines of that size)
    Returns: dict of size -> list of null E values
    """
    if rng is None:
        rng = np.random.default_rng(42)

    n_middles = embedding.shape[0]
    null_energies = {}

    for size, count in sorted(size_counts.items()):
        if size < 2:
            continue
        # Sample enough null values: min(n_null, count * 10) for efficiency
        n_samples = min(n_null, max(count * 10, 200))
        energies = []
        for _ in range(n_samples):
            indices = rng.choice(n_middles, size=size, replace=False)
            e = compute_line_energy(indices, embedding)
            if e is not None:
                energies.append(e)
        null_energies[size] = energies

    return null_energies


def main():
    print("=" * 60)
    print("T1: Energy Functional Definition and Line-Level Distribution")
    print("=" * 60)

    # Step 1: Load compatibility matrix and build embedding
    print("\n[1] Loading compatibility matrix and building residual embedding...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles, mid_to_idx = reconstruct_middle_list()
    print(f"  MIDDLEs in A-space: {len(all_middles)}")
    assert compat_matrix.shape[0] == len(all_middles), \
        f"Matrix {compat_matrix.shape[0]} vs middles {len(all_middles)}"

    res_emb, eigenvalues = build_residual_embedding(compat_matrix)

    # Step 2: Extract B-line MIDDLE inventories
    print("\n[2] Extracting B-line MIDDLE inventories...")
    tx = Transcript()
    b_line_indices, b_line_all = extract_line_middles(tx.currier_b(), mid_to_idx)

    total_b_lines = len(b_line_all)
    lines_with_2plus = sum(1 for v in b_line_indices.values() if len(v) >= 2)
    lines_with_0 = total_b_lines - len(b_line_indices)
    lines_with_1 = len(b_line_indices) - lines_with_2plus

    print(f"  Total B lines: {total_b_lines}")
    print(f"  Lines with 0 A-space MIDDLEs: {lines_with_0}")
    print(f"  Lines with 1 A-space MIDDLE: {lines_with_1}")
    print(f"  Lines with >=2 A-space MIDDLEs: {lines_with_2plus}")
    print(f"  Coverage: {lines_with_2plus / total_b_lines:.1%}")

    # Step 3: Compute E(line) for all B lines
    print("\n[3] Computing E(line) for B lines...")
    b_energies = []
    b_sizes = []
    b_keys = []
    for key, indices in b_line_indices.items():
        if len(indices) < 2:
            continue
        e = compute_line_energy(indices, res_emb)
        if e is not None:
            b_energies.append(e)
            b_sizes.append(len(indices))
            b_keys.append(key)

    b_energies = np.array(b_energies)
    b_sizes = np.array(b_sizes)
    print(f"  Lines with valid E: {len(b_energies)}")
    print(f"  E mean: {np.mean(b_energies):.6f}")
    print(f"  E median: {np.median(b_energies):.6f}")
    print(f"  E std: {np.std(b_energies):.6f}")
    print(f"  E range: [{np.min(b_energies):.6f}, {np.max(b_energies):.6f}]")
    print(f"  E quartiles: {np.percentile(b_energies, [25, 50, 75])}")

    # Step 4: Correlation with line size
    print("\n[4] Correlation with line size (number of A-space MIDDLEs)...")
    rho_size, p_size = stats.spearmanr(b_sizes, b_energies)
    print(f"  Spearman rho(size, E): {rho_size:.4f} (p={p_size:.2e})")

    # Size distribution
    from collections import Counter
    size_dist = Counter(b_sizes.tolist())
    print(f"  Size distribution: {dict(sorted(size_dist.items()))}")

    # Step 5: Null model — random MIDDLE subsets
    print("\n[5] Computing null energy distribution...")
    null_energies = compute_null_energies(res_emb, dict(size_dist))

    # Aggregate null: match the observed size distribution
    rng = np.random.default_rng(123)
    null_matched = []
    for size in b_sizes:
        s = int(size)
        if s in null_energies and null_energies[s]:
            null_matched.append(rng.choice(null_energies[s]))

    null_matched = np.array(null_matched)
    print(f"  Null E mean: {np.mean(null_matched):.6f}")
    print(f"  Null E median: {np.median(null_matched):.6f}")
    print(f"  Null E std: {np.std(null_matched):.6f}")

    # Compare distributions
    ks_stat, ks_p = stats.ks_2samp(b_energies, null_matched)
    mw_stat, mw_p = stats.mannwhitneyu(b_energies, null_matched, alternative='two-sided')
    shift = np.mean(b_energies) - np.mean(null_matched)
    print(f"\n  Distribution comparison:")
    print(f"  KS statistic: {ks_stat:.4f} (p={ks_p:.2e})")
    print(f"  Mann-Whitney p: {mw_p:.2e}")
    print(f"  Mean shift (real - null): {shift:.6f}")
    print(f"  Shift direction: {'HIGHER (more compatible)' if shift > 0 else 'LOWER (more tension)'}")

    # Per-size z-scores
    print("\n  Per-size comparison:")
    size_zscores = {}
    for s in sorted(size_dist.keys()):
        if s not in null_energies or not null_energies[s]:
            continue
        real_at_s = b_energies[b_sizes == s]
        null_at_s = np.array(null_energies[s])
        if len(real_at_s) >= 5:
            z = (np.mean(real_at_s) - np.mean(null_at_s)) / (np.std(null_at_s) + 1e-10)
            size_zscores[s] = {
                'n': int(len(real_at_s)),
                'real_mean': float(np.mean(real_at_s)),
                'null_mean': float(np.mean(null_at_s)),
                'z': float(z),
            }
            print(f"    size={s}: n={len(real_at_s)}, "
                  f"real={np.mean(real_at_s):.5f}, "
                  f"null={np.mean(null_at_s):.5f}, z={z:+.2f}")

    # Step 6: A-line energy for comparison
    print("\n[6] Computing A-line energy for comparison...")
    a_line_indices, a_line_all = extract_line_middles(tx.currier_a(), mid_to_idx)

    a_energies = []
    a_sizes_list = []
    for key, indices in a_line_indices.items():
        if len(indices) < 2:
            continue
        e = compute_line_energy(indices, res_emb)
        if e is not None:
            a_energies.append(e)
            a_sizes_list.append(len(indices))

    a_energies = np.array(a_energies)
    a_sizes_arr = np.array(a_sizes_list)
    print(f"  A lines with valid E: {len(a_energies)}")
    print(f"  A E mean: {np.mean(a_energies):.6f}")
    print(f"  A E median: {np.median(a_energies):.6f}")
    print(f"  A E std: {np.std(a_energies):.6f}")
    print(f"  A mean size: {np.mean(a_sizes_arr):.1f}")

    # A vs B comparison
    ab_ks, ab_ks_p = stats.ks_2samp(a_energies, b_energies)
    ab_mw, ab_mw_p = stats.mannwhitneyu(a_energies, b_energies, alternative='two-sided')
    ab_shift = np.mean(b_energies) - np.mean(a_energies)
    print(f"\n  A vs B comparison:")
    print(f"  KS statistic: {ab_ks:.4f} (p={ab_ks_p:.2e})")
    print(f"  Mann-Whitney p: {ab_mw_p:.2e}")
    print(f"  Mean shift (B - A): {ab_shift:.6f}")

    # A vs null comparison (does A also differ from random?)
    a_null_matched = []
    a_rng = np.random.default_rng(456)
    a_size_dist = Counter(a_sizes_arr.tolist())
    a_null_energies = compute_null_energies(res_emb, dict(a_size_dist))
    for size in a_sizes_arr:
        s = int(size)
        if s in a_null_energies and a_null_energies[s]:
            a_null_matched.append(a_rng.choice(a_null_energies[s]))
    a_null_matched = np.array(a_null_matched)
    a_null_shift = np.mean(a_energies) - np.mean(a_null_matched)
    a_ks, a_ks_p = stats.ks_2samp(a_energies, a_null_matched)
    print(f"\n  A vs null:")
    print(f"  KS statistic: {a_ks:.4f} (p={a_ks_p:.2e})")
    print(f"  Mean shift (A - null): {a_null_shift:.6f}")

    # Step 7: Energy percentile distribution
    print("\n[7] Energy distribution shape...")
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    b_pcts = np.percentile(b_energies, percentiles)
    null_pcts = np.percentile(null_matched, percentiles)
    a_pcts = np.percentile(a_energies, percentiles)
    print(f"  {'Pct':>5s} {'B':>10s} {'Null':>10s} {'A':>10s}")
    for p, bv, nv, av in zip(percentiles, b_pcts, null_pcts, a_pcts):
        print(f"  {p:>5d} {bv:>10.5f} {nv:>10.5f} {av:>10.5f}")

    # Skewness and kurtosis
    from scipy.stats import skew, kurtosis
    print(f"\n  Skewness:  B={skew(b_energies):.3f}, null={skew(null_matched):.3f}, A={skew(a_energies):.3f}")
    print(f"  Kurtosis:  B={kurtosis(b_energies):.3f}, null={kurtosis(null_matched):.3f}, A={kurtosis(a_energies):.3f}")

    # Step 8: Verdict
    print("\n" + "=" * 60)
    is_non_degenerate = np.std(b_energies) > 0.001
    is_different_from_null = ks_p < 0.001
    is_shift_positive = shift > 0

    if is_non_degenerate and is_different_from_null:
        verdict = "WELL_DEFINED"
        if is_shift_positive:
            explanation = (
                f"E(line) is non-degenerate (std={np.std(b_energies):.4f}), "
                f"significantly different from random (KS p={ks_p:.2e}), "
                f"and shifted HIGHER than null by {shift:.5f}. "
                f"B lines are more internally compatible than random MIDDLE subsets."
            )
        else:
            explanation = (
                f"E(line) is non-degenerate (std={np.std(b_energies):.4f}), "
                f"significantly different from random (KS p={ks_p:.2e}), "
                f"but shifted LOWER than null by {abs(shift):.5f}. "
                f"B lines have MORE constraint tension than random."
            )
    elif is_non_degenerate:
        verdict = "DEGENERATE_NULL"
        explanation = (
            f"E(line) is non-degenerate but NOT significantly different from random "
            f"(KS p={ks_p:.2e}). Energy is well-defined but not structurally meaningful."
        )
    else:
        verdict = "DEGENERATE"
        explanation = (
            f"E(line) is degenerate (std={np.std(b_energies):.4f}). "
            f"The metric does not differentiate lines."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save results
    results = {
        'test': 'T1_energy_definition',
        'n_a_middles': len(all_middles),
        'hub_eigenvalue': float(eigenvalues[0]),
        'residual_dim': K_RESIDUAL,
        'b_lines': {
            'total': total_b_lines,
            'with_0_a_middles': lines_with_0,
            'with_1_a_middle': lines_with_1,
            'with_2plus': lines_with_2plus,
            'coverage': lines_with_2plus / total_b_lines,
            'valid_energy': len(b_energies),
        },
        'b_energy': {
            'mean': float(np.mean(b_energies)),
            'median': float(np.median(b_energies)),
            'std': float(np.std(b_energies)),
            'min': float(np.min(b_energies)),
            'max': float(np.max(b_energies)),
            'q25': float(np.percentile(b_energies, 25)),
            'q75': float(np.percentile(b_energies, 75)),
            'skewness': float(skew(b_energies)),
            'kurtosis': float(kurtosis(b_energies)),
        },
        'size_correlation': {
            'rho': float(rho_size),
            'p': float(p_size),
        },
        'null_comparison': {
            'null_mean': float(np.mean(null_matched)),
            'null_std': float(np.std(null_matched)),
            'shift': float(shift),
            'ks_stat': float(ks_stat),
            'ks_p': float(ks_p),
            'mannwhitney_p': float(mw_p),
        },
        'per_size_z': size_zscores,
        'a_energy': {
            'n_lines': len(a_energies),
            'mean': float(np.mean(a_energies)),
            'median': float(np.median(a_energies)),
            'std': float(np.std(a_energies)),
            'mean_size': float(np.mean(a_sizes_arr)),
        },
        'a_vs_b': {
            'ks_stat': float(ab_ks),
            'ks_p': float(ab_ks_p),
            'mannwhitney_p': float(ab_mw_p),
            'shift_b_minus_a': float(ab_shift),
        },
        'a_vs_null': {
            'shift_a_minus_null': float(a_null_shift),
            'ks_stat': float(a_ks),
            'ks_p': float(a_ks_p),
        },
        'percentiles': {
            'pcts': percentiles,
            'b': [float(x) for x in b_pcts],
            'null': [float(x) for x in null_pcts],
            'a': [float(x) for x in a_pcts],
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't1_energy_definition.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't1_energy_definition.json'}")


if __name__ == '__main__':
    main()
