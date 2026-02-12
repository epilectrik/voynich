"""
T4: Null Model Comparison
==========================
Phase: THERMAL_PLANT_SIMULATION

Runs two null models with the same 100 parameterizations as T1:
  Null A: Batch Still (beta=0, no condensation return / no reflux)
  Null B: Open Heating (alpha=0, no vaporization / no phase transition)

Extracts automata and scores against same 10 Voynich targets.
Tests whether reflux-specific dynamics contribute beyond generic control.

Output: t4_null_models.json
"""

import json
import sys
import numpy as np
from pathlib import Path

# Import T2's analysis pipeline (eliminates 180 lines of duplicated code)
sys.path.insert(0, str(Path(__file__).parent))
from t2_automaton_extraction import analyze_from_vectors

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# Constants (same as T1)
DT = 0.1
N_STEPS = 200
BURN_IN = 50
LAMBDA = 5.0
GAMMA = 0.05
C_EFF = 0.8
K_LOSS = 0.3
Q_MAX = 1.5
T_ENV = 0.0
DELAY = 3
TARGET_FRAC = 0.05
SIGMA_Q = 0.08
SIGMA_T = 0.01
SIGMA_BOIL = 0.02


def load_t1_params():
    """Load parameterizations from T1."""
    with open(RESULTS_DIR / 't1_thermal_simulation.json') as f:
        t1 = json.load(f)
    return [p['params'] for p in t1['parameterizations']]


def simulate_null(params, rng, model_type):
    """Simulate a null model variant.

    model_type: 'batch' (beta=0) or 'open' (alpha=0)
    """
    T_boil = params['T_boil'] + rng.normal(0, SIGMA_BOIL)
    M = params['M']
    alpha = params['alpha'] if model_type != 'open' else 0.0
    beta = params['beta'] if model_type != 'batch' else 0.0
    K_p = params['K_p']
    bias_frac = params['bias_frac']

    T_target = T_boil * (1 + TARGET_FRAC)
    Q_bias = K_LOSS * T_boil * bias_frac

    T = T_boil + rng.normal(0, 0.03)
    phi = rng.uniform(0.0, 0.02)
    T_history = [T] * DELAY

    states = []
    prev_T = T

    for step in range(N_STEPS):
        T_observed = T_history[0]
        error = T_target - T_observed
        Q = np.clip(K_p * error + Q_bias + rng.normal(0, SIGMA_Q), 0, Q_MAX)
        T_history.pop(0)
        T_history.append(T)

        V = alpha * max(0.0, 1.0 - phi) * max(0.0, T - T_boil)
        C = beta * phi * C_EFF

        dT_phys = DT * (Q - LAMBDA * V + LAMBDA * C - K_LOSS * (T - T_ENV)) / M
        T_new = T + dT_phys + rng.normal(0, SIGMA_T)

        dphi = DT * (V - C - GAMMA * phi)
        phi_new = np.clip(phi + dphi, 0.0, 1.0)

        dT_obs = T_new - prev_T
        dphi_obs = phi_new - phi

        states.append([float(T), float(phi), float(dT_obs),
                       float(dphi_obs), float(Q)])

        prev_T = T
        T = T_new
        phi = phi_new

    return np.array(states[BURN_IN:])


def score_targets(result):
    """Score against same 10 targets as T3."""
    if result is None:
        return 0, {}

    tests = {
        'state_count': 5 <= result['optimal_k'] <= 7,
        'hub_mass': 0.60 <= result['hub_mass'] <= 0.70,
        'spectral_gap': result['spectral_gap'] > 0.80,
        'alternation_rate': 0.50 <= result['lanes']['alternation_rate'] <= 0.60,
        'alternation_asymmetry': result['lanes']['heat_to_cool'] > result['lanes']['cool_to_heat'],
        'post_overshoot_cooling': result['lanes']['post_overshoot_cool_rate'] > 0.70,
        'forbidden_count': 10 <= result['n_forbidden'] <= 25,
        'buffer_rate': result['safety_buffers']['buffer_rate'] < 0.01,
        'run_length_median': (result['lanes']['heat_run_median'] == 1.0
                             and result['lanes']['cool_run_median'] == 1.0),
    }
    hits = sum(1 for v in tests.values() if v)
    return hits, {k: bool(v) for k, v in tests.items()}


def run_null_model(model_type, param_sets, rng):
    """Run a null model across all parameterizations."""
    n_runs = 10
    results = []

    for pi, params in enumerate(param_sets):
        all_vecs = []
        run_lengths = []
        for ri in range(n_runs):
            states = simulate_null(params, rng, model_type)
            all_vecs.append(states)
            run_lengths.append(len(states))

        pooled = np.vstack(all_vecs)

        # Convert run_lengths to run_boundaries for T2's API
        boundaries = []
        idx = 0
        for rl in run_lengths:
            boundaries.append((idx, idx + rl))
            idx += rl

        # Use T2's vectorized analysis pipeline
        automaton = analyze_from_vectors(pooled, boundaries, rng)
        hits, hit_details = score_targets(automaton)

        results.append({
            'param_id': pi,
            'hit_count': hits,
            'hits': hit_details,
            'automaton_summary': {
                'optimal_k': automaton['optimal_k'] if automaton else 0,
                'hub_mass': automaton['hub_mass'] if automaton else 0,
                'spectral_gap': automaton['spectral_gap'] if automaton else 0,
                'alternation_rate': automaton['lanes']['alternation_rate'] if automaton else 0,
            },
        })

        if (pi + 1) % 25 == 0:
            recent = [r['hit_count'] for r in results[-25:]]
            print(f"    {model_type} param {pi+1}/100: "
                  f"mean_hits={np.mean(recent):.1f}")

    return results


def main():
    rng = np.random.default_rng(42)
    param_sets = load_t1_params()

    print("Running Null A: Batch Still (no condensation return)...")
    batch_results = run_null_model('batch', param_sets, rng)

    print("\nRunning Null B: Open Heating (no phase transition)...")
    open_results = run_null_model('open', param_sets, rng)

    # Load reflux scores from T3 for comparison
    with open(RESULTS_DIR / 't3_voynich_comparison.json') as f:
        t3 = json.load(f)
    reflux_hits = [s['hit_count'] for s in t3['per_parameterization']]
    # Add oscillation_variation hit
    if t3['oscillation_variation']['hit']:
        reflux_hits = [h + 1 for h in reflux_hits]

    batch_hits = [r['hit_count'] for r in batch_results]
    open_hits = [r['hit_count'] for r in open_results]

    # Check oscillation variation for null models
    batch_alts = [r['automaton_summary']['alternation_rate'] for r in batch_results]
    open_alts = [r['automaton_summary']['alternation_rate'] for r in open_results]
    batch_ov_hit = (max(batch_alts) - min(batch_alts)) > 0.20
    open_ov_hit = (max(open_alts) - min(open_alts)) > 0.20

    if batch_ov_hit:
        batch_hits = [h + 1 for h in batch_hits]
    if open_ov_hit:
        open_hits = [h + 1 for h in open_hits]

    output = {
        'comparison': {
            'reflux': {
                'median': float(np.median(reflux_hits)),
                'mean': float(np.mean(reflux_hits)),
            },
            'batch_still': {
                'median': float(np.median(batch_hits)),
                'mean': float(np.mean(batch_hits)),
                'oscillation_variation_hit': batch_ov_hit,
            },
            'open_heating': {
                'median': float(np.median(open_hits)),
                'mean': float(np.mean(open_hits)),
                'oscillation_variation_hit': open_ov_hit,
            },
        },
        'discrimination': {
            'reflux_vs_batch': float(np.median(reflux_hits) - np.median(batch_hits)),
            'reflux_vs_open': float(np.median(reflux_hits) - np.median(open_hits)),
            'reflux_advantage': (float(np.median(reflux_hits)) >
                                max(float(np.median(batch_hits)),
                                    float(np.median(open_hits)))),
        },
        'batch_results': batch_results,
        'open_results': open_results,
    }

    out_path = RESULTS_DIR / 't4_null_models.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f"\n{'='*60}")
    print(f"T4 NULL MODEL COMPARISON")
    print(f"{'='*60}")
    print(f"")
    print(f"MODEL COMPARISON (median hits / 10):")
    print(f"  Reflux (T1-T3):   {np.median(reflux_hits):.0f}")
    print(f"  Batch Still:      {np.median(batch_hits):.0f}")
    print(f"  Open Heating:     {np.median(open_hits):.0f}")
    print(f"")
    if output['discrimination']['reflux_advantage']:
        print(f"  Reflux outperforms nulls by "
              f"{output['discrimination']['reflux_vs_batch']:.0f} / "
              f"{output['discrimination']['reflux_vs_open']:.0f} hits")
    else:
        print(f"  No reflux advantage over nulls")
    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
