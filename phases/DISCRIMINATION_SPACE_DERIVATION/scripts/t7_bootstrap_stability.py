#!/usr/bin/env python3
"""
T7: Bootstrap Stability Test
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Test whether the spectral profile is intrinsic to the system or a
sampling artifact from finite data (972 MIDDLEs from 1,559 lines).

Randomly remove 10%, 20%, 30% of MIDDLEs and check if the key
metrics remain stable.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'

REMOVAL_FRACTIONS = [0.10, 0.20, 0.30]
N_TRIALS = 50


def load_matrix():
    """Load compatibility matrix."""
    return np.load(RESULTS_DIR / 't1_compat_matrix.npy')


def compute_metrics(A):
    """Compute key spectral metrics for a compatibility matrix."""
    n = A.shape[0]
    if n < 10:
        return None

    eigs = np.linalg.eigvalsh(A.astype(np.float64))[::-1]

    lambda_1 = float(eigs[0])
    lambda_2 = float(eigs[1]) if len(eigs) > 1 and eigs[1] > 0 else 1e-10
    spectral_gap = lambda_1 / lambda_2

    # n eigenvalues above threshold 12
    n_above_12 = int((eigs > 12.0).sum())

    # Effective rank
    pos_eigs = eigs[eigs > 0]
    if len(pos_eigs) > 0:
        normed = pos_eigs / pos_eigs.sum()
        entropy = -np.sum(normed * np.log(normed))
        eff_rank = float(np.exp(entropy))
    else:
        eff_rank = 0

    # Cumulative variance at K=96
    if len(pos_eigs) >= 96:
        cumvar_96 = float(pos_eigs[:96].sum() / pos_eigs.sum())
    else:
        cumvar_96 = 1.0

    return {
        'lambda_1': lambda_1,
        'spectral_gap': spectral_gap,
        'n_above_12': n_above_12,
        'effective_rank': eff_rank,
        'cumvar_96': cumvar_96,
        'n_nodes': n,
    }


def run():
    print("=" * 70)
    print("T7: Bootstrap Stability Test")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    M = load_matrix()
    n = M.shape[0]
    print(f"  Full matrix: {n}x{n}")

    # Baseline metrics
    baseline = compute_metrics(M)
    print(f"  Baseline λ₁ = {baseline['lambda_1']:.1f}")
    print(f"  Baseline spectral gap = {baseline['spectral_gap']:.2f}")
    print(f"  Baseline eff. rank = {baseline['effective_rank']:.1f}")
    print(f"  Baseline cumvar@96 = {baseline['cumvar_96']:.4f}")

    all_results = {}

    for frac in REMOVAL_FRACTIONS:
        n_remove = int(n * frac)
        print(f"\n  Removal fraction: {frac*100:.0f}% ({n_remove} MIDDLEs)...")
        print(f"  Running {N_TRIALS} trials...")

        trial_metrics = {key: [] for key in ['lambda_1', 'spectral_gap', 'n_above_12',
                                              'effective_rank', 'cumvar_96']}

        np.random.seed(42)
        for trial in range(N_TRIALS):
            # Randomly select MIDDLEs to remove
            remove_idx = np.random.choice(n, n_remove, replace=False)
            keep_idx = np.setdiff1d(np.arange(n), remove_idx)

            # Submatrix
            A_sub = M[np.ix_(keep_idx, keep_idx)]
            m = compute_metrics(A_sub)
            if m is None:
                continue
            for key in trial_metrics:
                trial_metrics[key].append(m[key])

        # Statistics
        frac_key = f"{frac*100:.0f}pct"
        frac_results = {}
        print(f"\n  {'Metric':<20} {'Baseline':>10} {'Mean':>10} {'Std':>10} {'CV':>8}")
        print(f"  {'-'*60}")

        for key in trial_metrics:
            vals = np.array(trial_metrics[key])
            if len(vals) == 0:
                continue
            mean_val = vals.mean()
            std_val = vals.std()
            cv = std_val / mean_val if mean_val > 0 else float('inf')
            base_val = baseline[key]

            print(f"  {key:<20} {base_val:>10.2f} {mean_val:>10.2f} {std_val:>10.3f} {cv:>8.4f}")

            frac_results[key] = {
                'baseline': float(base_val),
                'mean': float(mean_val),
                'std': float(std_val),
                'cv': float(cv),
                'min': float(vals.min()),
                'max': float(vals.max()),
                'ratio_to_baseline': float(mean_val / base_val) if base_val > 0 else 0,
            }

        all_results[frac_key] = frac_results

    # Verdict
    print(f"\n{'='*70}")
    print("STABILITY VERDICT")
    print(f"{'='*70}")

    # Check CV at 20% removal for core metrics
    core_metrics = ['lambda_1', 'spectral_gap', 'effective_rank']
    cvs_at_20 = []
    for key in core_metrics:
        if '20pct' in all_results and key in all_results['20pct']:
            cv = all_results['20pct'][key]['cv']
            cvs_at_20.append(cv)
            print(f"  CV at 20% removal for {key}: {cv:.4f}")

    max_cv = max(cvs_at_20) if cvs_at_20 else 1.0
    if max_cv < 0.10:
        verdict = "STABLE"
        explanation = "All core metrics have CV < 0.10 at 20% removal. Structure is intrinsic."
    elif max_cv < 0.25:
        verdict = "MIXED"
        explanation = "Some metrics show moderate variation. Structure is partially intrinsic."
    else:
        verdict = "FRAGILE"
        explanation = "Core metrics are sensitive to subsampling. Structure may be sampling artifact."

    print(f"\n  Max CV at 20%: {max_cv:.4f}")
    print(f"  Verdict: {verdict}")
    print(f"  {explanation}")

    # Check proportionality: does removal degrade proportionally?
    print(f"\n  Proportionality check (λ₁ ratio to baseline):")
    for frac in REMOVAL_FRACTIONS:
        frac_key = f"{frac*100:.0f}pct"
        if frac_key in all_results and 'lambda_1' in all_results[frac_key]:
            ratio = all_results[frac_key]['lambda_1']['ratio_to_baseline']
            expected = 1.0 - frac  # linear expectation
            print(f"    {frac*100:.0f}% removal: ratio={ratio:.4f} (linear expectation={expected:.2f})")

    results = {
        'test': 'T7_bootstrap_stability',
        'n_nodes': n,
        'n_trials': N_TRIALS,
        'removal_fractions': REMOVAL_FRACTIONS,
        'baseline': baseline,
        'results_by_fraction': all_results,
        'verdict': verdict,
        'explanation': explanation,
        'max_cv_at_20pct': float(max_cv),
    }

    with open(RESULTS_DIR / 't7_bootstrap_stability.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't7_bootstrap_stability.json'}")


if __name__ == '__main__':
    run()
