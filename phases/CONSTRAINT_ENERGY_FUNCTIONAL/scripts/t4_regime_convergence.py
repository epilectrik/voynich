#!/usr/bin/env python3
"""
T4: REGIME and Program Structure
CONSTRAINT_ENERGY_FUNCTIONAL phase

Test whether:
1. REGIME modulates E variance (not mean) — C979
2. E trajectories track convergence — C074
3. First-line (HT) energy differs from body energy
4. Late-folio energy variance tightens (convergence signature)
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
REGIME_FILE = Path(__file__).resolve().parents[3] / 'results' / 'regime_folio_mapping.json'
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


def load_regime_mapping():
    with open(REGIME_FILE) as f:
        raw = json.load(f)
    folio_to_regime = {}
    for regime, folios in raw.items():
        for folio in folios:
            folio_to_regime[folio] = regime
    return folio_to_regime


def main():
    print("=" * 60)
    print("T4: REGIME and Program Structure")
    print("=" * 60)

    # Setup
    print("\n[1] Loading...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles, mid_to_idx = reconstruct_middle_list()
    res_emb = build_residual_embedding(compat_matrix)
    folio_to_regime = load_regime_mapping()

    # Extract per-line data with folio structure
    print("\n[2] Extracting per-line data with folio structure...")
    tx = Transcript()
    morph = Morphology()

    # Collect tokens per line and per folio
    line_tokens = defaultdict(set)  # (folio, line) -> set of mid_idx
    folio_lines = defaultdict(set)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            key = (token.folio, token.line)
            line_tokens[key].add(mid_to_idx[m.middle])
            folio_lines[token.folio].add(token.line)

    # Order lines within each folio
    folio_ordered_lines = {}
    for folio, lines in folio_lines.items():
        folio_ordered_lines[folio] = sorted(lines)

    # Compute energy for each line
    line_energy = {}
    for key, indices in line_tokens.items():
        e = compute_line_energy(list(indices), res_emb)
        if e is not None:
            line_energy[key] = e

    print(f"  Lines with energy: {len(line_energy)}")
    print(f"  Folios: {len(folio_ordered_lines)}")

    # Step 3: First-line vs body-line energy
    print("\n[3] First-line (HT) vs body-line energy...")
    first_line_e = []
    body_line_e = []
    for folio, ordered in folio_ordered_lines.items():
        if not ordered:
            continue
        first = ordered[0]
        key_first = (folio, first)
        if key_first in line_energy:
            first_line_e.append(line_energy[key_first])
        for line in ordered[1:]:
            key = (folio, line)
            if key in line_energy:
                body_line_e.append(line_energy[key])

    if first_line_e and body_line_e:
        mw_fb, p_fb = stats.mannwhitneyu(first_line_e, body_line_e, alternative='two-sided')
        print(f"  First lines: n={len(first_line_e)}, E={np.mean(first_line_e):+.5f} ± {np.std(first_line_e):.5f}")
        print(f"  Body lines:  n={len(body_line_e)}, E={np.mean(body_line_e):+.5f} ± {np.std(body_line_e):.5f}")
        print(f"  Shift (first - body): {np.mean(first_line_e) - np.mean(body_line_e):+.5f}")
        print(f"  Mann-Whitney p={p_fb:.2e}")
    else:
        p_fb = 1.0

    # Step 4: Energy trajectory within folios (quintile analysis)
    print("\n[4] Energy trajectory within folios...")
    # Assign each line a normalized position within its folio
    quintile_data = {q: [] for q in range(5)}
    for folio, ordered in folio_ordered_lines.items():
        n = len(ordered)
        if n < 5:
            continue
        for i, line in enumerate(ordered):
            key = (folio, line)
            if key in line_energy:
                q = min(int(i / n * 5), 4)
                quintile_data[q].append(line_energy[key])

    quintile_results = {}
    q_labels = ['Q1 (start)', 'Q2', 'Q3', 'Q4', 'Q5 (end)']
    for q in range(5):
        vals = quintile_data[q]
        if vals:
            quintile_results[q_labels[q]] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
                'var_E': float(np.var(vals)),
            }
            print(f"  {q_labels[q]:>12s}: n={len(vals):>4d}, "
                  f"E={np.mean(vals):+.5f} ± {np.std(vals):.5f}, "
                  f"var={np.var(vals):.6f}")

    # Trend test: Jonckheere-Terpstra-like (Spearman across quintile assignments)
    all_q_pos = []
    all_q_e = []
    for q in range(5):
        for e in quintile_data[q]:
            all_q_pos.append(q)
            all_q_e.append(e)
    if all_q_pos:
        rho_q, p_q = stats.spearmanr(all_q_pos, all_q_e)
        print(f"\n  Position-energy trend: rho={rho_q:.4f} (p={p_q:.2e})")

    # Step 5: Variance trajectory (does variance tighten toward end?)
    print("\n[5] Variance trajectory within folios...")
    var_early = np.var(quintile_data[0]) if quintile_data[0] else 0
    var_late = np.var(quintile_data[4]) if quintile_data[4] else 0
    var_ratio = var_late / var_early if var_early > 0 else 0
    print(f"  Q1 variance: {var_early:.6f}")
    print(f"  Q5 variance: {var_late:.6f}")
    print(f"  Ratio (Q5/Q1): {var_ratio:.3f}")
    print(f"  {'TIGHTENING' if var_ratio < 0.85 else 'LOOSENING' if var_ratio > 1.15 else 'STABLE'}")

    # Per-quintile variance using Levene's test
    q_groups = [quintile_data[q] for q in range(5) if quintile_data[q]]
    if len(q_groups) >= 2:
        levene_stat, levene_p = stats.levene(*q_groups)
        print(f"  Levene's test for equal variance: F={levene_stat:.2f}, p={levene_p:.2e}")

    # Step 6: REGIME × energy variance (extending T2)
    print("\n[6] REGIME energy variance analysis...")
    regime_energies = defaultdict(list)
    for folio, ordered in folio_ordered_lines.items():
        regime = folio_to_regime.get(folio)
        if not regime:
            continue
        for line in ordered:
            key = (folio, line)
            if key in line_energy:
                regime_energies[regime].append(line_energy[key])

    regime_var_results = {}
    for regime in sorted(regime_energies.keys()):
        vals = regime_energies[regime]
        regime_var_results[regime] = {
            'n': len(vals),
            'mean_E': float(np.mean(vals)),
            'var_E': float(np.var(vals)),
            'iqr': float(np.percentile(vals, 75) - np.percentile(vals, 25)),
            'p10': float(np.percentile(vals, 10)),
            'p90': float(np.percentile(vals, 90)),
            'range_80': float(np.percentile(vals, 90) - np.percentile(vals, 10)),
        }
        print(f"  {regime}: mean={np.mean(vals):+.5f}, var={np.var(vals):.6f}, "
              f"80% range={np.percentile(vals, 90) - np.percentile(vals, 10):.5f}")

    # Levene's test across REGIMEs
    r_groups = [regime_energies[r] for r in sorted(regime_energies.keys())]
    if len(r_groups) >= 2:
        r_levene, r_levene_p = stats.levene(*r_groups)
        print(f"\n  Levene's test (REGIME variance): F={r_levene:.2f}, p={r_levene_p:.2e}")

    # Step 7: Per-REGIME trajectory (does convergence pattern differ?)
    print("\n[7] Per-REGIME energy trajectory...")
    regime_traj_results = {}
    for regime in sorted(regime_energies.keys()):
        regime_quintiles = {q: [] for q in range(5)}
        regime_folios = [f for f in folio_ordered_lines
                         if folio_to_regime.get(f) == regime]
        for folio in regime_folios:
            ordered = folio_ordered_lines[folio]
            n = len(ordered)
            if n < 5:
                continue
            for i, line in enumerate(ordered):
                key = (folio, line)
                if key in line_energy:
                    q = min(int(i / n * 5), 4)
                    regime_quintiles[q].append(line_energy[key])

        q_means = []
        q_valid = True
        for q in range(5):
            if regime_quintiles[q]:
                q_means.append(np.mean(regime_quintiles[q]))
            else:
                q_valid = False
                break

        if q_valid and len(q_means) == 5:
            # Trend
            rho_rt, p_rt = stats.spearmanr(range(5), q_means)
            var_q1 = np.var(regime_quintiles[0]) if regime_quintiles[0] else 0
            var_q5 = np.var(regime_quintiles[4]) if regime_quintiles[4] else 0

            regime_traj_results[regime] = {
                'q_means': [float(x) for x in q_means],
                'trend_rho': float(rho_rt),
                'trend_p': float(p_rt),
                'var_q1': float(var_q1),
                'var_q5': float(var_q5),
                'var_ratio': float(var_q5 / var_q1) if var_q1 > 0 else None,
            }
            print(f"  {regime}: trend rho={rho_rt:+.3f} (p={p_rt:.2e}), "
                  f"var Q1={var_q1:.6f}, Q5={var_q5:.6f}, "
                  f"ratio={var_q5 / var_q1:.3f}" if var_q1 > 0 else "")

    # Step 8: Per-folio energy signature (is E consistent within folios?)
    print("\n[8] Per-folio energy consistency...")
    folio_mean_energies = {}
    folio_std_energies = {}
    for folio, ordered in folio_ordered_lines.items():
        folio_e = [line_energy[(folio, line)] for line in ordered
                   if (folio, line) in line_energy]
        if len(folio_e) >= 5:
            folio_mean_energies[folio] = np.mean(folio_e)
            folio_std_energies[folio] = np.std(folio_e)

    if folio_mean_energies:
        mean_vals = list(folio_mean_energies.values())
        std_vals = list(folio_std_energies.values())
        print(f"  Folios with >=5 lines: {len(folio_mean_energies)}")
        print(f"  Cross-folio mean E: {np.mean(mean_vals):+.5f} ± {np.std(mean_vals):.5f}")
        print(f"  Mean within-folio std: {np.mean(std_vals):.5f}")
        print(f"  Ratio (within/between): {np.mean(std_vals) / np.std(mean_vals):.2f}")

        # ICC-like: how much variance is between-folio vs within-folio?
        between_var = np.var(mean_vals)
        within_var = np.mean([s**2 for s in std_vals])
        icc_like = between_var / (between_var + within_var) if (between_var + within_var) > 0 else 0
        print(f"  ICC-like (between / total): {icc_like:.3f}")

    # Step 9: Verdict
    print("\n" + "=" * 60)

    has_ht_body_diff = p_fb < 0.01
    has_trajectory = abs(rho_q) > 0.03 and p_q < 0.05 if all_q_pos else False
    has_variance_trend = abs(var_ratio - 1.0) > 0.15 if var_early > 0 else False
    has_regime_variance = r_levene_p < 0.01 if len(r_groups) >= 2 else False

    n_effects = sum([has_ht_body_diff, has_trajectory, has_variance_trend, has_regime_variance])

    if n_effects >= 3:
        verdict = "STRONG_PROGRAM_STRUCTURE"
    elif n_effects >= 1:
        verdict = "PARTIAL_PROGRAM_STRUCTURE"
    else:
        verdict = "NO_PROGRAM_STRUCTURE"

    effects = []
    if has_ht_body_diff:
        effects.append("HT/body difference")
    if has_trajectory:
        effects.append(f"position trend (rho={rho_q:.3f})")
    if has_variance_trend:
        effects.append(f"variance {'tightening' if var_ratio < 1 else 'loosening'} ({var_ratio:.2f})")
    if has_regime_variance:
        effects.append(f"REGIME variance (Levene p={r_levene_p:.1e})")

    explanation = (
        f"{n_effects}/4 program structure effects. "
        + ("; ".join(effects) if effects else "None significant.")
    )
    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save
    results = {
        'test': 'T4_regime_convergence',
        'n_lines': len(line_energy),
        'n_folios': len(folio_ordered_lines),
        'first_vs_body': {
            'first_n': len(first_line_e),
            'first_mean': float(np.mean(first_line_e)) if first_line_e else None,
            'body_n': len(body_line_e),
            'body_mean': float(np.mean(body_line_e)) if body_line_e else None,
            'shift': float(np.mean(first_line_e) - np.mean(body_line_e)) if first_line_e and body_line_e else None,
            'p': float(p_fb),
        },
        'position_trajectory': {
            'quintile_energy': quintile_results,
            'trend_rho': float(rho_q) if all_q_pos else None,
            'trend_p': float(p_q) if all_q_pos else None,
        },
        'variance_trajectory': {
            'var_q1': float(var_early),
            'var_q5': float(var_late),
            'var_ratio': float(var_ratio),
            'levene_p': float(levene_p) if len(q_groups) >= 2 else None,
        },
        'regime_variance': {
            'per_regime': regime_var_results,
            'levene_p': float(r_levene_p) if len(r_groups) >= 2 else None,
        },
        'regime_trajectory': regime_traj_results,
        'folio_consistency': {
            'n_folios': len(folio_mean_energies),
            'cross_folio_mean': float(np.mean(mean_vals)) if folio_mean_energies else None,
            'cross_folio_std': float(np.std(mean_vals)) if folio_mean_energies else None,
            'mean_within_std': float(np.mean(std_vals)) if folio_mean_energies else None,
            'icc_like': float(icc_like) if folio_mean_energies else None,
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't4_regime_convergence.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't4_regime_convergence.json'}")


if __name__ == '__main__':
    main()
