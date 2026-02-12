#!/usr/bin/env python3
"""
T4: Energy Functional Sensitivity
B_EXCLUSIVE_GEOMETRIC_INTEGRATION phase

Compute E(line) with and without B-exclusive tokens.
If no material shift → surface elaboration.
If shift → load-bearing tension contributors.
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
    return sorted(all_middles_set), {m: i for i, m in enumerate(sorted(all_middles_set))}


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    res_scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * res_scaling[np.newaxis, :]


def compute_line_energy(indices, embedding):
    if len(indices) < 2:
        return None
    vecs = embedding[indices]
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    valid = (norms.flatten() > 1e-10)
    if valid.sum() < 2:
        return None
    vecs = vecs[valid]
    norms = norms[valid]
    normed = vecs / norms
    cos_matrix = normed @ normed.T
    n = len(normed)
    triu_idx = np.triu_indices(n, k=1)
    return float(np.mean(cos_matrix[triu_idx]))


def main():
    print("=" * 60)
    print("T4: Energy Functional Sensitivity")
    print("=" * 60)

    # Setup
    print("\n[1] Loading...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    a_middles, mid_to_idx = reconstruct_middle_list()
    a_set = set(a_middles)
    res_emb = build_residual_embedding(compat_matrix)

    # Build per-line data
    print("\n[2] Extracting per-line MIDDLEs...")
    tx = Transcript()
    morph = Morphology()

    line_all_middles = defaultdict(list)  # ALL MIDDLEs on line (with type tag)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            key = (token.folio, token.line)
            is_shared = m.middle in a_set
            line_all_middles[key].append({
                'middle': m.middle,
                'shared': is_shared,
                'mid_idx': mid_to_idx.get(m.middle),
            })

    # Step 3: Compute E with all A-space MIDDLEs (baseline = T1 result)
    print("\n[3] Computing energy: all A-space MIDDLEs (baseline)...")
    baseline_energies = []
    line_keys_valid = []

    for key, tokens in line_all_middles.items():
        a_indices = list(set(t['mid_idx'] for t in tokens if t['mid_idx'] is not None))
        e = compute_line_energy(a_indices, res_emb)
        if e is not None:
            baseline_energies.append(e)
            line_keys_valid.append(key)

    baseline_energies = np.array(baseline_energies)
    print(f"  Valid lines: {len(baseline_energies)}")
    print(f"  Mean E (baseline): {np.mean(baseline_energies):+.6f}")

    # Step 4: Count lines that have exclusive MIDDLEs
    print("\n[4] Counting B-exclusive MIDDLE presence...")
    n_with_exclusive = 0
    n_without_exclusive = 0
    exc_count_per_line = []

    for key in line_keys_valid:
        tokens = line_all_middles[key]
        n_exc = sum(1 for t in tokens if not t['shared'] and t['middle'])
        n_sha = sum(1 for t in tokens if t['shared'])
        exc_count_per_line.append(n_exc)
        if n_exc > 0:
            n_with_exclusive += 1
        else:
            n_without_exclusive += 1

    exc_count_arr = np.array(exc_count_per_line)
    print(f"  Lines with B-exclusive MIDDLEs: {n_with_exclusive} "
          f"({n_with_exclusive/len(line_keys_valid):.1%})")
    print(f"  Lines without: {n_without_exclusive}")
    print(f"  Mean exclusive count per line: {np.mean(exc_count_arr):.2f}")

    # Step 5: Compare E on lines WITH vs WITHOUT exclusive MIDDLEs
    print("\n[5] Energy comparison: lines with vs without exclusives...")
    e_with = baseline_energies[exc_count_arr > 0]
    e_without = baseline_energies[exc_count_arr == 0]

    if len(e_with) > 0 and len(e_without) > 0:
        mw_stat, mw_p = stats.mannwhitneyu(e_with, e_without, alternative='two-sided')
        shift = np.mean(e_with) - np.mean(e_without)
        print(f"  With exclusives: n={len(e_with)}, E={np.mean(e_with):+.6f}")
        print(f"  Without exclusives: n={len(e_without)}, E={np.mean(e_without):+.6f}")
        print(f"  Shift: {shift:+.6f}")
        print(f"  Mann-Whitney p={mw_p:.2e}")
    else:
        mw_p = 1.0
        shift = 0.0

    # Step 6: Correlation between exclusive count and E
    print("\n[6] Correlation: exclusive count vs E...")
    rho_exc, p_exc = stats.spearmanr(exc_count_arr, baseline_energies)
    print(f"  Spearman rho(n_exclusive, E): {rho_exc:+.4f} (p={p_exc:.2e})")

    # Bin analysis
    exc_bins = {'0': [], '1': [], '2': [], '3+': []}
    for ec, e in zip(exc_count_arr, baseline_energies):
        if ec == 0:
            exc_bins['0'].append(e)
        elif ec == 1:
            exc_bins['1'].append(e)
        elif ec == 2:
            exc_bins['2'].append(e)
        else:
            exc_bins['3+'].append(e)

    exc_bin_results = {}
    for b in ['0', '1', '2', '3+']:
        vals = exc_bins[b]
        if vals:
            exc_bin_results[b] = {'n': len(vals), 'mean_E': float(np.mean(vals))}
            print(f"    {b:>3s} exclusives: n={len(vals):>4d}, E={np.mean(vals):+.6f}")

    # Step 7: What fraction of token-level energy comes from shared vs exclusive?
    print("\n[7] Token contribution analysis...")
    # On lines with both shared and exclusive, what's the A-space fraction?
    mixed_lines = []
    for key in line_keys_valid:
        tokens = line_all_middles[key]
        n_total = len(tokens)
        n_sha = sum(1 for t in tokens if t['shared'])
        n_exc = sum(1 for t in tokens if not t['shared'] and t['middle'])
        if n_sha > 0 and n_exc > 0:
            mixed_lines.append({
                'total': n_total,
                'shared': n_sha,
                'exclusive': n_exc,
                'shared_frac': n_sha / n_total,
            })

    if mixed_lines:
        shared_fracs = [m['shared_frac'] for m in mixed_lines]
        print(f"  Lines with both types: {len(mixed_lines)}")
        print(f"  Mean shared fraction: {np.mean(shared_fracs):.3f}")
        print(f"  Mean exclusive count on mixed lines: "
              f"{np.mean([m['exclusive'] for m in mixed_lines]):.1f}")

    # Verdict
    print("\n" + "=" * 60)

    material_shift = abs(shift) > 0.003 and mw_p < 0.01
    material_correlation = abs(rho_exc) > 0.05 and p_exc < 0.01

    if material_shift or material_correlation:
        verdict = "LOAD_BEARING"
        explanation = (
            f"B-exclusive MIDDLEs materially affect line energy: "
            f"shift={shift:+.5f} (p={mw_p:.1e}), "
            f"count correlation rho={rho_exc:+.3f}. "
            f"They contribute to tension structure."
        )
    else:
        verdict = "SURFACE_ELABORATION"
        explanation = (
            f"B-exclusive MIDDLEs do NOT materially affect energy: "
            f"shift={shift:+.5f} (p={mw_p:.1e}), "
            f"count correlation rho={rho_exc:+.3f}. "
            f"They are surface decoration on A-space backbone."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T4_energy_sensitivity',
        'n_valid_lines': len(baseline_energies),
        'baseline_mean_E': float(np.mean(baseline_energies)),
        'exclusive_presence': {
            'lines_with': n_with_exclusive,
            'lines_without': n_without_exclusive,
            'mean_count': float(np.mean(exc_count_arr)),
        },
        'energy_comparison': {
            'with_mean': float(np.mean(e_with)) if len(e_with) > 0 else None,
            'without_mean': float(np.mean(e_without)) if len(e_without) > 0 else None,
            'shift': float(shift),
            'mw_p': float(mw_p),
        },
        'count_correlation': {
            'rho': float(rho_exc),
            'p': float(p_exc),
        },
        'bin_energy': exc_bin_results,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't4_energy_sensitivity.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't4_energy_sensitivity.json'}")


if __name__ == '__main__':
    main()
