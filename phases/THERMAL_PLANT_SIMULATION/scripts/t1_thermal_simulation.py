"""
T1: Minimal Reflux Distillation Thermal Plant Simulation
=========================================================
Phase: THERMAL_PLANT_SIMULATION

Simulates a closed-loop thermal plant (reflux distillation vessel) under
proportional control with operator response delay.

Key physics:
  - Energy balance: heating vs latent heat absorption vs ambient loss
  - Phase transition: vaporization above boiling point, condensation as reflux
  - Control delay: operator reacts to state from d steps ago (fire adjustment lag)
  - This delay + nonlinear phase transition produces natural oscillation

Non-circularity: All parameters from thermodynamics / control theory.
  - T_target derived from T_boil (operator aims slightly above boiling)
  - Q_bias derived from K_LOSS * T_boil * bias_frac (energy-balanced)
  - No Voynich data enters the simulation.

Output: t1_thermal_simulation.json
"""

import json
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# PHYSICAL CONSTANTS (normalized)
# ============================================================
DT = 0.1          # time step (fraction of thermal time constant)
N_STEPS = 200     # steps per run (first 50 = burn-in)
BURN_IN = 50      # discard initial transient
LAMBDA = 5.0      # latent heat ratio (ethanol: 846/(2.44*70))
GAMMA = 0.05      # ambient condensation rate
C_EFF = 0.8       # condenser effectiveness
K_LOSS = 0.3      # ambient heat loss coefficient (moderately insulated vessel)
Q_MAX = 1.5       # maximum heat input
T_ENV = 0.0       # ambient temperature (normalized)
DELAY = 3         # operator response delay (steps)
TARGET_FRAC = 0.05  # operator aims 5% above boiling

# Noise
SIGMA_Q = 0.08    # fire fluctuation (visible variation in wood fire)
SIGMA_T = 0.01    # thermal noise
SIGMA_BOIL = 0.02 # between-run boiling point jitter

# LHS sweep
N_PARAM_SETS = 100
N_RUNS_PER = 10

# Parameter ranges [min, max]
PARAM_RANGES = {
    'T_boil':    (0.80, 1.20),   # boiling point
    'M':         (0.50, 2.00),   # thermal mass
    'alpha':     (1.00, 3.00),   # vaporization rate (volatility)
    'beta':      (0.50, 2.00),   # condenser efficiency
    'K_p':       (1.00, 5.00),   # controller gain (operator aggressiveness)
    'bias_frac': (0.90, 1.30),   # Q_bias = K_LOSS * T_boil * bias_frac
}


def latin_hypercube_sample(n, ranges, rng):
    """Draw n samples via LHS across len(ranges) dimensions."""
    dims = list(ranges.keys())
    d = len(dims)
    samples = []
    for i, key in enumerate(dims):
        lo, hi = ranges[key]
        cuts = np.linspace(0, 1, n + 1)
        points = rng.uniform(cuts[:-1], cuts[1:])
        rng.shuffle(points)
        samples.append(lo + points * (hi - lo))
    return [{dims[i]: samples[i][j] for i in range(d)} for j in range(n)]


def simulate_run(params, rng):
    """Simulate one process run with operator response delay.

    Derived parameters:
      T_target = T_boil * (1 + TARGET_FRAC)
      Q_bias = K_LOSS * T_boil * bias_frac
    """
    T_boil = params['T_boil'] + rng.normal(0, SIGMA_BOIL)
    M = params['M']
    alpha = params['alpha']
    beta = params['beta']
    K_p = params['K_p']
    bias_frac = params['bias_frac']

    # Derived from physics
    T_target = T_boil * (1 + TARGET_FRAC)
    Q_bias = K_LOSS * T_boil * bias_frac

    # Initialize near boiling with small perturbation
    T = T_boil + rng.normal(0, 0.03)
    phi = rng.uniform(0.0, 0.02)

    # History buffer for delayed observation
    T_history = [T] * DELAY

    states = []
    prev_T = T

    for step in range(N_STEPS):
        # P-controller with DELAY
        T_observed = T_history[0]
        error = T_target - T_observed
        Q = np.clip(K_p * error + Q_bias + rng.normal(0, SIGMA_Q), 0, Q_MAX)

        # Update history buffer
        T_history.pop(0)
        T_history.append(T)

        # Vaporization: above boiling point
        V = alpha * max(0.0, 1.0 - phi) * max(0.0, T - T_boil)

        # Condensation: reflux return
        C = beta * phi * C_EFF

        # Temperature update: energy balance
        dT_phys = DT * (Q - LAMBDA * V + LAMBDA * C
                        - K_LOSS * (T - T_ENV)) / M
        T_new = T + dT_phys + rng.normal(0, SIGMA_T)

        # Vapor fraction update
        dphi = DT * (V - C - GAMMA * phi)
        phi_new = np.clip(phi + dphi, 0.0, 1.0)

        # Record state
        dT_obs = T_new - prev_T
        dphi_obs = phi_new - phi

        states.append({
            'T': float(T),
            'phi': float(phi),
            'dT': float(dT_obs),
            'dphi': float(dphi_obs),
            'Q': float(Q),
            'T_boil': float(T_boil),
        })

        prev_T = T
        T = T_new
        phi = phi_new

    # Discard burn-in
    return states[BURN_IN:], T_target, T_boil


def segment_into_lines(states, T_target):
    """Segment a run into lines via cycle detection.

    Cycle boundary: T crosses T_target from above (downward zero-crossing).
    """
    lines = []
    current_line = []
    prev_above = states[0]['T'] > T_target if states else False

    for s in states:
        above = s['T'] > T_target
        current_line.append(s)

        if prev_above and not above and len(current_line) >= 3:
            lines.append(current_line)
            current_line = []

        prev_above = above

    if len(current_line) >= 3:
        lines.append(current_line)

    return lines


def compute_run_diagnostics(states, lines, T_target, T_boil):
    """Compute per-run diagnostics."""
    T_vals = np.array([s['T'] for s in states])
    phi_vals = np.array([s['phi'] for s in states])
    Q_vals = np.array([s['Q'] for s in states])
    dT_vals = np.array([s['dT'] for s in states])

    # Hazard proxy: phi > 0.15 (emergent, not hard-coded threshold)
    hazard_count = int(np.sum(phi_vals > 0.15))

    # Lane: Q above vs below Q_mean (operator heating vs stabilizing)
    Q_mean = float(np.mean(Q_vals))
    heating = Q_vals > Q_mean
    n_alt = int(np.sum(heating[1:] != heating[:-1]))
    alt_rate = n_alt / (len(heating) - 1) if len(heating) > 1 else 0

    # Also compute dT-based alternation
    rising = dT_vals > 0
    n_alt_dT = int(np.sum(rising[1:] != rising[:-1]))
    alt_rate_dT = n_alt_dT / (len(rising) - 1) if len(rising) > 1 else 0

    # Oscillation amplitude
    T_above_boil = T_vals[T_vals > T_boil]
    T_below_boil = T_vals[T_vals <= T_boil]

    return {
        'T_mean': float(np.mean(T_vals)),
        'T_std': float(np.std(T_vals)),
        'T_min': float(np.min(T_vals)),
        'T_max': float(np.max(T_vals)),
        'T_target': float(T_target),
        'T_boil': float(T_boil),
        'phi_mean': float(np.mean(phi_vals)),
        'phi_max': float(np.max(phi_vals)),
        'Q_mean': float(Q_mean),
        'hazard_rate': float(hazard_count / len(states)),
        'alt_rate_Q': float(alt_rate),
        'alt_rate_dT': float(alt_rate_dT),
        'frac_above_boil': float(len(T_above_boil) / len(T_vals)),
        'n_lines': len(lines),
        'mean_line_length': float(np.mean([len(l) for l in lines])) if lines else 0,
        'line_lengths': [len(l) for l in lines],
    }


def main():
    rng = np.random.default_rng(42)

    param_sets = latin_hypercube_sample(N_PARAM_SETS, PARAM_RANGES, rng)

    all_results = []

    for pi, params in enumerate(param_sets):
        runs = []
        for ri in range(N_RUNS_PER):
            states, T_target, T_boil = simulate_run(params, rng)
            lines = segment_into_lines(states, T_target)
            diag = compute_run_diagnostics(states, lines, T_target, T_boil)

            line_data = []
            for line in lines:
                line_data.append({
                    'T': [s['T'] for s in line],
                    'phi': [s['phi'] for s in line],
                    'dT': [s['dT'] for s in line],
                    'dphi': [s['dphi'] for s in line],
                    'Q': [s['Q'] for s in line],
                })
            runs.append({
                'run_id': ri,
                'diagnostics': diag,
                'lines': line_data,
            })

        all_diags = [r['diagnostics'] for r in runs]
        agg = {
            'mean_line_length': float(np.mean([d['mean_line_length'] for d in all_diags])),
            'mean_hazard_rate': float(np.mean([d['hazard_rate'] for d in all_diags])),
            'mean_alt_rate_Q': float(np.mean([d['alt_rate_Q'] for d in all_diags])),
            'mean_alt_rate_dT': float(np.mean([d['alt_rate_dT'] for d in all_diags])),
            'mean_T_std': float(np.mean([d['T_std'] for d in all_diags])),
            'mean_phi_max': float(np.mean([d['phi_max'] for d in all_diags])),
            'mean_frac_above_boil': float(np.mean([d['frac_above_boil'] for d in all_diags])),
            'total_lines': sum(d['n_lines'] for d in all_diags),
        }

        all_results.append({
            'param_id': pi,
            'params': {k: float(v) for k, v in params.items()},
            'derived': {
                'T_target': float(params['T_boil'] * (1 + TARGET_FRAC)),
                'Q_bias': float(K_LOSS * params['T_boil'] * params['bias_frac']),
            },
            'aggregate': agg,
            'runs': runs,
        })

        if (pi + 1) % 20 == 0:
            print(f"  Param {pi+1}/{N_PARAM_SETS}: "
                  f"lines={agg['total_lines']}, "
                  f"line_len={agg['mean_line_length']:.1f}, "
                  f"haz={agg['mean_hazard_rate']:.3f}, "
                  f"alt_Q={agg['mean_alt_rate_Q']:.3f}, "
                  f"alt_dT={agg['mean_alt_rate_dT']:.3f}, "
                  f"above_boil={agg['mean_frac_above_boil']:.2f}")

    # Summary
    line_lengths = [r['aggregate']['mean_line_length'] for r in all_results]
    hazard_rates = [r['aggregate']['mean_hazard_rate'] for r in all_results]
    alt_Q = [r['aggregate']['mean_alt_rate_Q'] for r in all_results]
    alt_dT = [r['aggregate']['mean_alt_rate_dT'] for r in all_results]
    above_boil = [r['aggregate']['mean_frac_above_boil'] for r in all_results]

    summary = {
        'n_parameterizations': N_PARAM_SETS,
        'n_runs_per': N_RUNS_PER,
        'n_steps_per_run': N_STEPS,
        'burn_in': BURN_IN,
        'effective_steps': N_STEPS - BURN_IN,
        'dt': DT,
        'operator_delay': DELAY,
        'line_length_stats': {
            'mean': float(np.mean(line_lengths)),
            'median': float(np.median(line_lengths)),
            'std': float(np.std(line_lengths)),
            'min': float(np.min(line_lengths)),
            'max': float(np.max(line_lengths)),
        },
        'hazard_rate_stats': {
            'mean': float(np.mean(hazard_rates)),
            'median': float(np.median(hazard_rates)),
        },
        'alternation_Q_stats': {
            'mean': float(np.mean(alt_Q)),
            'median': float(np.median(alt_Q)),
        },
        'alternation_dT_stats': {
            'mean': float(np.mean(alt_dT)),
            'median': float(np.median(alt_dT)),
        },
        'frac_above_boil_stats': {
            'mean': float(np.mean(above_boil)),
            'median': float(np.median(above_boil)),
        },
        'param_ranges': {k: list(v) for k, v in PARAM_RANGES.items()},
        'fixed_params': {
            'LAMBDA': LAMBDA, 'GAMMA': GAMMA, 'C_EFF': C_EFF,
            'K_LOSS': K_LOSS, 'Q_MAX': Q_MAX,
            'TARGET_FRAC': TARGET_FRAC, 'DELAY': DELAY,
            'SIGMA_Q': SIGMA_Q, 'SIGMA_T': SIGMA_T, 'SIGMA_BOIL': SIGMA_BOIL,
        },
    }

    output = {
        'summary': summary,
        'parameterizations': all_results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't1_thermal_simulation.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f"\n{'='*60}")
    print(f"T1 THERMAL SIMULATION COMPLETE")
    print(f"{'='*60}")
    print(f"Parameterizations: {N_PARAM_SETS}")
    print(f"Total runs:        {N_PARAM_SETS * N_RUNS_PER}")
    print(f"Steps per run:     {N_STEPS - BURN_IN} (after burn-in)")
    print(f"Operator delay:    {DELAY} steps")
    print(f"")
    print(f"LINE LENGTH:  mean={summary['line_length_stats']['mean']:.1f}  "
          f"median={summary['line_length_stats']['median']:.1f}")
    print(f"HAZARD RATE:  mean={summary['hazard_rate_stats']['mean']:.3f}  "
          f"median={summary['hazard_rate_stats']['median']:.3f}")
    print(f"ALT RATE (Q): mean={summary['alternation_Q_stats']['mean']:.3f}  "
          f"median={summary['alternation_Q_stats']['median']:.3f}")
    print(f"ALT RATE (dT):mean={summary['alternation_dT_stats']['mean']:.3f}  "
          f"median={summary['alternation_dT_stats']['median']:.3f}")
    print(f"ABOVE BOIL:   mean={summary['frac_above_boil_stats']['mean']:.3f}  "
          f"median={summary['frac_above_boil_stats']['median']:.3f}")
    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
