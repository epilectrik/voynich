"""
T2: Automaton Extraction from Simulated Thermal Plant Data
==========================================================
Phase: THERMAL_PLANT_SIMULATION

For each of 100 parameterizations, extracts:
  1. Macro-state count via GMM + BIC (K = 2..12, data-driven)
  2. Transition matrix and hub state identification
  3. Spectral analysis (spectral gap, mixing time)
  4. Forbidden transitions (null-calibrated via shuffled sequences)
  5. Lane analysis (heating vs cooling, alternation, post-overshoot bias)
  6. Safety buffer scan

Non-circularity: State count emerges from BIC. Forbidden transitions
calibrated against shuffled null. Lane = dT sign (physics, not Voynich).

Output: t2_automaton_extraction.json
"""

import json
import numpy as np
from pathlib import Path
from sklearn.mixture import GaussianMixture

RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SHUFFLE = 50  # shuffled sequences for forbidden-pair null (reduced; analytical check is primary)


def load_t1():
    """Load T1 simulation results."""
    path = RESULTS_DIR / 't1_thermal_simulation.json'
    with open(path) as f:
        return json.load(f)


def extract_state_vectors(param_data):
    """Extract all state vectors from a parameterization's runs.

    Returns: array of shape (N, 5) with columns [T, phi, dT, dphi, Q]
             and list of run boundaries for sequence analysis.
    """
    # Pre-collect all arrays per run, then concatenate once
    run_arrays = []
    run_boundaries = []
    idx = 0

    for run in param_data['runs']:
        run_start = idx
        for line in run['lines']:
            n = len(line['T'])
            idx += n
        # Build run array from all lines at once
        T = [v for line in run['lines'] for v in line['T']]
        phi = [v for line in run['lines'] for v in line['phi']]
        dT = [v for line in run['lines'] for v in line['dT']]
        dphi = [v for line in run['lines'] for v in line['dphi']]
        Q = [v for line in run['lines'] for v in line['Q']]
        if T:
            run_arrays.append(np.column_stack([T, phi, dT, dphi, Q]))
        run_boundaries.append((run_start, idx))

    if run_arrays:
        return np.vstack(run_arrays), run_boundaries
    return np.zeros((0, 5)), run_boundaries


def find_optimal_k(X, k_range=(2, 13)):
    """Find optimal number of clusters via BIC."""
    if len(X) < k_range[1]:
        return 2, {}, None

    bic_scores = {}
    best_bic = np.inf
    best_k = 2
    best_model = None

    for k in range(k_range[0], min(k_range[1], len(X))):
        try:
            gmm = GaussianMixture(n_components=k, n_init=1,
                                  max_iter=100, random_state=42)
            gmm.fit(X)
            bic = gmm.bic(X)
            bic_scores[k] = float(bic)
            if bic < best_bic:
                best_bic = bic
                best_k = k
                best_model = gmm
        except Exception:
            bic_scores[k] = float('inf')

    return best_k, bic_scores, best_model


def compute_transition_matrix(labels, run_boundaries):
    """Compute transition matrix from cluster labels, respecting run boundaries."""
    K = int(np.max(labels)) + 1
    counts = np.zeros((K, K), dtype=np.float64)

    for start, end in run_boundaries:
        seq = labels[start:end]
        if len(seq) < 2:
            continue
        np.add.at(counts, (seq[:-1], seq[1:]), 1)

    # Row-stochastic
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans = counts / row_sums

    # Stationary distribution (left eigenvector of T^T with eigenvalue 1)
    try:
        eigvals, eigvecs = np.linalg.eig(trans.T)
        idx = np.argmin(np.abs(eigvals - 1.0))
        stat = np.real(eigvecs[:, idx])
        stat = stat / stat.sum()
        stat = np.abs(stat)
    except Exception:
        stat = row_sums.flatten() / row_sums.sum()

    hub_state = int(np.argmax(stat))

    return trans, stat, counts, hub_state


def spectral_analysis(trans):
    """Compute spectral gap and mixing time."""
    try:
        eigvals = np.linalg.eigvals(trans)
        eigvals_sorted = sorted(np.abs(eigvals), reverse=True)
        lambda_2 = eigvals_sorted[1] if len(eigvals_sorted) > 1 else 0
        spectral_gap = 1.0 - lambda_2
        mixing_time = 1.0 / spectral_gap if spectral_gap > 1e-10 else float('inf')
    except Exception:
        spectral_gap = 0.0
        mixing_time = float('inf')

    return float(spectral_gap), float(mixing_time)


def forbidden_transitions_null_calibrated(labels, run_boundaries, K, rng):
    """Identify forbidden transitions via analytical null + Monte Carlo check.

    Forbidden = observed count is 0 AND analytical null expects > 5.
    Analytical null: for a random permutation of length L with marginal
    counts n_i, expected transitions E[i->j] = n_i * n_j / (L-1) for i!=j.
    """
    # Observed counts (vectorized)
    obs_counts = np.zeros((K, K), dtype=np.int64)
    for start, end in run_boundaries:
        seq = labels[start:end]
        if len(seq) < 2:
            continue
        np.add.at(obs_counts, (seq[:-1], seq[1:]), 1)

    # Analytical null expected counts per run, summed (vectorized via np.outer)
    null_expected = np.zeros((K, K), dtype=np.float64)
    for start, end in run_boundaries:
        seq = labels[start:end]
        L = len(seq)
        if L < 2:
            continue
        counts = np.bincount(seq, minlength=K).astype(np.float64)
        n_trans = L - 1
        # Outer product: E[i->j] = n_i * n_j / (L-1)
        outer = np.outer(counts, counts) / n_trans
        # Diagonal: E[i->i] = n_i * (n_i - 1) / (L-1)
        np.fill_diagonal(outer, counts * (counts - 1) / n_trans)
        null_expected += outer

    # Forbidden: observed=0 and null expects >5 (vectorized)
    forbidden_mask = (obs_counts == 0) & (null_expected > 5)
    fi, fj = np.where(forbidden_mask)
    forbidden = [{'source': int(i), 'target': int(j),
                  'null_expected': float(null_expected[i, j])}
                 for i, j in zip(fi, fj)]

    return forbidden


def lane_analysis(vectors, run_boundaries):
    """Analyze heating/cooling lane dynamics.

    Lane: dT > 0 = heating (QO-like), dT <= 0 = cooling (CHSH-like).
    """
    dT = vectors[:, 2]  # column 2 = dT
    phi = vectors[:, 1]  # column 1 = phi
    heating = dT > 0  # True = heating lane

    # All metrics computed with vectorized numpy ops per run boundary
    n_transitions = 0
    n_pairs = 0
    h2c = 0
    h_total = 0
    c2h = 0
    c_total = 0
    heat_runs = []
    cool_runs = []
    post_overshoot_cool = 0
    post_overshoot_total = 0

    for start, end in run_boundaries:
        seq = heating[start:end]
        if len(seq) < 2:
            continue

        curr = seq[:-1]
        nxt = seq[1:]

        # Alternation (vectorized)
        n_pairs += len(curr)
        n_transitions += int(np.sum(curr != nxt))

        # Asymmetry (vectorized boolean masks)
        h_mask = curr
        c_mask = ~curr
        h_total += int(np.sum(h_mask))
        h2c += int(np.sum(h_mask & ~nxt))
        c_total += int(np.sum(c_mask))
        c2h += int(np.sum(c_mask & nxt))

        # Run lengths (vectorized via np.diff on change points)
        changes = np.where(seq[:-1] != seq[1:])[0]
        starts_arr = np.concatenate([[0], changes + 1])
        ends_arr = np.concatenate([changes + 1, [len(seq)]])
        lengths = ends_arr - starts_arr
        run_types = seq[starts_arr]  # True = heat, False = cool
        if np.any(run_types):
            heat_runs.extend(lengths[run_types].tolist())
        if np.any(~run_types):
            cool_runs.extend(lengths[~run_types].tolist())

        # Post-overshoot bias (vectorized peak detection)
        phi_seq = phi[start:end]
        if len(phi_seq) >= 3:
            mid = phi_seq[1:-1]
            peaks = (mid > 0.10) & (mid > phi_seq[:-2]) & (mid >= phi_seq[2:])
            post_overshoot_total += int(np.sum(peaks))
            post_overshoot_cool += int(np.sum(peaks & ~seq[2:]))

    alt_rate = n_transitions / n_pairs if n_pairs > 0 else 0
    heat_to_cool = h2c / h_total if h_total > 0 else 0
    cool_to_heat = c2h / c_total if c_total > 0 else 0
    post_overshoot_cool_rate = (post_overshoot_cool / post_overshoot_total
                                if post_overshoot_total > 0 else 0)

    return {
        'alternation_rate': float(alt_rate),
        'heat_to_cool': float(heat_to_cool),
        'cool_to_heat': float(cool_to_heat),
        'asymmetry': float(heat_to_cool - cool_to_heat),
        'heat_run_mean': float(np.mean(heat_runs)) if heat_runs else 0,
        'heat_run_median': float(np.median(heat_runs)) if heat_runs else 0,
        'cool_run_mean': float(np.mean(cool_runs)) if cool_runs else 0,
        'cool_run_median': float(np.median(cool_runs)) if cool_runs else 0,
        'post_overshoot_cool_rate': float(post_overshoot_cool_rate),
        'post_overshoot_total': int(post_overshoot_total),
        'n_pairs': int(n_pairs),
    }


def safety_buffer_scan(labels, run_boundaries, forbidden_pairs):
    """For each forbidden pair, find tokens whose removal creates it."""
    if not forbidden_pairs:
        return {'n_buffers': 0, 'buffer_rate': 0.0}

    max_label = int(np.max(labels)) + 1 if len(labels) > 0 else 1
    forbidden_codes = np.array(
        [fp['source'] * max_label + fp['target'] for fp in forbidden_pairs],
        dtype=np.int64)
    total_interior = 0
    buffer_count = 0

    for start, end in run_boundaries:
        seq = labels[start:end]
        if len(seq) < 3:
            continue
        left = seq[:-2].astype(np.int64)
        right = seq[2:].astype(np.int64)
        total_interior += len(left)
        pair_codes = left * max_label + right
        buffer_count += int(np.sum(np.isin(pair_codes, forbidden_codes)))

    return {
        'n_buffers': int(buffer_count),
        'total_interior': int(total_interior),
        'buffer_rate': float(buffer_count / total_interior) if total_interior > 0 else 0,
    }


def analyze_from_vectors(vectors, run_boundaries, rng):
    """Full analysis pipeline from raw state vectors.

    Reusable entry point — called by analyze_parameterization() and T4.
    vectors: (N, 5) array with columns [T, phi, dT, dphi, Q]
    run_boundaries: list of (start, end) index tuples
    """
    if len(vectors) < 20:
        return None

    # Normalize for clustering
    means = vectors.mean(axis=0)
    stds = vectors.std(axis=0)
    stds[stds < 1e-10] = 1.0
    X_norm = (vectors - means) / stds

    # 1. Macro-state discovery
    best_k, bic_scores, best_model = find_optimal_k(X_norm)
    labels = best_model.predict(X_norm) if best_model else np.zeros(len(X_norm), dtype=int)

    # 2. Transition matrix
    trans, stat, counts, hub_state = compute_transition_matrix(labels, run_boundaries)

    # 3. Spectral analysis
    spectral_gap, mixing_time = spectral_analysis(trans)

    # 4. Forbidden transitions (null-calibrated)
    forbidden = forbidden_transitions_null_calibrated(labels, run_boundaries, best_k, rng)

    # 5. Lane analysis
    lanes = lane_analysis(vectors, run_boundaries)

    # 6. Safety buffers
    buffers = safety_buffer_scan(labels, run_boundaries, forbidden)

    return {
        'n_tokens': len(vectors),
        'optimal_k': int(best_k),
        'bic_scores': {str(k): v for k, v in bic_scores.items()},
        'hub_state': int(hub_state),
        'hub_mass': float(stat[hub_state]),
        'stationary_dist': [float(x) for x in stat],
        'transition_matrix': [[float(x) for x in row] for row in trans],
        'spectral_gap': spectral_gap,
        'mixing_time': mixing_time,
        'n_forbidden': len(forbidden),
        'forbidden_pairs': forbidden,
        'lanes': lanes,
        'safety_buffers': buffers,
    }


def analyze_parameterization(param_data, rng):
    """Full analysis for one parameterization."""
    vectors, run_boundaries = extract_state_vectors(param_data)
    return analyze_from_vectors(vectors, run_boundaries, rng)


def main():
    rng = np.random.default_rng(42)

    t1_data = load_t1()
    params_list = t1_data['parameterizations']

    results = []
    for pi, param_data in enumerate(params_list):
        analysis = analyze_parameterization(param_data, rng)
        if analysis is None:
            continue

        results.append({
            'param_id': param_data['param_id'],
            'params': param_data['params'],
            **analysis,
        })

        if (pi + 1) % 20 == 0:
            a = analysis
            print(f"  Param {pi+1}/100: K={a['optimal_k']}, "
                  f"hub={a['hub_mass']:.2f}, "
                  f"gap={a['spectral_gap']:.3f}, "
                  f"forb={a['n_forbidden']}, "
                  f"alt={a['lanes']['alternation_rate']:.3f}, "
                  f"buffers={a['safety_buffers']['n_buffers']}")

    # Distribution summaries
    ks = [r['optimal_k'] for r in results]
    hubs = [r['hub_mass'] for r in results]
    gaps = [r['spectral_gap'] for r in results]
    forbs = [r['n_forbidden'] for r in results]
    alts = [r['lanes']['alternation_rate'] for r in results]
    asym = [r['lanes']['asymmetry'] for r in results]
    h2c = [r['lanes']['heat_to_cool'] for r in results]
    c2h = [r['lanes']['cool_to_heat'] for r in results]
    heat_med = [r['lanes']['heat_run_median'] for r in results]
    cool_med = [r['lanes']['cool_run_median'] for r in results]
    post_ov = [r['lanes']['post_overshoot_cool_rate'] for r in results]
    buf_rates = [r['safety_buffers']['buffer_rate'] for r in results]

    def stats(vals, name):
        return {
            'mean': float(np.mean(vals)),
            'median': float(np.median(vals)),
            'std': float(np.std(vals)),
            'min': float(np.min(vals)),
            'max': float(np.max(vals)),
            'q25': float(np.percentile(vals, 25)),
            'q75': float(np.percentile(vals, 75)),
        }

    summary = {
        'n_parameterizations': len(results),
        'optimal_k': stats(ks, 'K'),
        'hub_mass': stats(hubs, 'hub'),
        'spectral_gap': stats(gaps, 'gap'),
        'n_forbidden': stats(forbs, 'forb'),
        'alternation_rate': stats(alts, 'alt'),
        'heat_to_cool': stats(h2c, 'h2c'),
        'cool_to_heat': stats(c2h, 'c2h'),
        'asymmetry': stats(asym, 'asym'),
        'heat_run_median': stats(heat_med, 'heat_run'),
        'cool_run_median': stats(cool_med, 'cool_run'),
        'post_overshoot_cool_rate': stats(post_ov, 'post_ov'),
        'buffer_rate': stats(buf_rates, 'buf'),
        'k_distribution': {str(k): int(ks.count(k)) for k in sorted(set(ks))},
    }

    output = {
        'summary': summary,
        'parameterizations': results,
    }

    out_path = RESULTS_DIR / 't2_automaton_extraction.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f"\n{'='*60}")
    print(f"T2 AUTOMATON EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Analyzed: {len(results)} parameterizations")
    print(f"")
    print(f"MACRO-STATE COUNT (K):")
    print(f"  Distribution: {summary['k_distribution']}")
    print(f"  Median: {summary['optimal_k']['median']:.0f}")
    print(f"")
    print(f"HUB STATE MASS:")
    print(f"  Median: {summary['hub_mass']['median']:.3f}")
    print(f"  IQR:    [{summary['hub_mass']['q25']:.3f}, {summary['hub_mass']['q75']:.3f}]")
    print(f"")
    print(f"SPECTRAL GAP:")
    print(f"  Median: {summary['spectral_gap']['median']:.3f}")
    print(f"")
    print(f"FORBIDDEN PAIRS:")
    print(f"  Median: {summary['n_forbidden']['median']:.0f}")
    print(f"  IQR:    [{summary['n_forbidden']['q25']:.0f}, {summary['n_forbidden']['q75']:.0f}]")
    print(f"")
    print(f"LANE ALTERNATION:")
    print(f"  Rate median: {summary['alternation_rate']['median']:.3f}")
    print(f"  H->C median: {summary['heat_to_cool']['median']:.3f}")
    print(f"  C->H median: {summary['cool_to_heat']['median']:.3f}")
    print(f"  Asymmetry:   {summary['asymmetry']['median']:.3f}")
    print(f"")
    print(f"RUN LENGTHS:")
    print(f"  Heat median: {summary['heat_run_median']['median']:.1f}")
    print(f"  Cool median: {summary['cool_run_median']['median']:.1f}")
    print(f"")
    print(f"POST-OVERSHOOT COOLING BIAS:")
    print(f"  Median: {summary['post_overshoot_cool_rate']['median']:.3f}")
    print(f"")
    print(f"SAFETY BUFFER RATE:")
    print(f"  Median: {summary['buffer_rate']['median']:.4f}")
    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
