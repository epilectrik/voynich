"""
T1: Categorical Discretization Scoring
=======================================
Phase: CATEGORICAL_DISCRETIZATION_TEST

Applies 6 discretization strategies to continuous thermal plant data (from
THERMAL_PLANT_SIMULATION T1), extracts automaton metrics, and scores each
strategy using direction-of-movement vs continuous baseline.

Expert adjustments incorporated:
  A. Direction-of-movement scoring (not pass/fail thresholds)
  B. Let K emerge via BIC for data-driven strategy (no forced K=6)
  C. Legality imposition layer (physically-motivated forbidden transitions)

O-Complexity: ALL per-token operations are vectorized numpy. Zero Python
for-loops over token-level arrays.

Output: t1_discretization_scoring.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans

# Import vectorized T2 functions
THERMAL_SCRIPTS = Path(__file__).parent.parent.parent / 'THERMAL_PLANT_SIMULATION' / 'scripts'
sys.path.insert(0, str(THERMAL_SCRIPTS))
from t2_automaton_extraction import (
    extract_state_vectors,
    compute_transition_matrix,
    spectral_analysis,
    forbidden_transitions_null_calibrated,
    safety_buffer_scan,
)

THERMAL_RESULTS = Path(__file__).parent.parent.parent / 'THERMAL_PLANT_SIMULATION' / 'results'
RESULTS_DIR = Path(__file__).parent.parent / 'results'


# ============================================================
# DATA LOADING
# ============================================================

def load_t1():
    with open(THERMAL_RESULTS / 't1_thermal_simulation.json') as f:
        return json.load(f)


def extract_with_tboil(param_data):
    """Extract state vectors + per-step T_boil vector."""
    vectors, run_boundaries = extract_state_vectors(param_data)
    t_boil_vec = np.zeros(len(vectors))
    for run, (start, end) in zip(param_data['runs'], run_boundaries):
        t_boil_vec[start:end] = run['diagnostics']['T_boil']
    return vectors, run_boundaries, t_boil_vec


# ============================================================
# DISCRETIZATION STRATEGIES (all vectorized numpy)
# ============================================================

def strategy_lane_temp(vectors, t_boil_vec, delta=0.05):
    """Lane x Temperature Phase: 2 lanes x 3 temp zones = 6 states.

    States: {0: cool_below, 1: cool_near, 2: cool_above,
             3: heat_below, 4: heat_near, 5: heat_above}
    """
    T, dT = vectors[:, 0], vectors[:, 2]
    lane = (dT > 0).astype(np.int32)  # 0=cooling, 1=heating
    # Temperature zones relative to T_boil
    zone = np.ones(len(T), dtype=np.int32)  # default: near boil
    zone[T < t_boil_vec * (1 - delta)] = 0  # below
    zone[T > t_boil_vec * (1 + delta)] = 2  # above
    return lane * 3 + zone


def strategy_operational(vectors, t_boil_vec, delta=0.05,
                         dT_small=0.005, phi_thresh=0.05):
    """Operational Regime: 6 hand-defined distiller states.

    States: {0: cold_start, 1: stabilize, 2: active_boil,
             3: overshoot, 4: recovery, 5: condensing}
    Cascading priority: later overrides earlier.
    """
    T, phi, dT, dphi = vectors[:, 0], vectors[:, 1], vectors[:, 2], vectors[:, 3]
    near = np.abs(T - t_boil_vec) < t_boil_vec * delta
    above = T > t_boil_vec
    well_above = T > t_boil_vec * (1 + 2 * delta)

    labels = np.zeros(len(T), dtype=np.int32)  # cold_start default
    labels[near & (np.abs(dT) < dT_small)] = 1  # stabilize
    labels[above & (dphi > 0)] = 2  # active_boil
    labels[well_above & (phi > phi_thresh)] = 3  # overshoot
    labels[(dT < 0) & (phi > 0.01) & (dphi < 0)] = 4  # recovery
    labels[near & (phi < 0.02) & (np.abs(dT) < dT_small)] = 5  # condensing
    return labels


def strategy_gmm_bic(vectors):
    """GMM+BIC: let K emerge from data (no forcing).

    Same as THERMAL_PLANT_SIMULATION T2 but as explicit comparison.
    """
    means = vectors.mean(axis=0)
    stds = vectors.std(axis=0)
    stds[stds < 1e-10] = 1.0
    X_norm = (vectors - means) / stds

    best_bic = np.inf
    best_k = 2
    best_model = None
    for k in range(2, min(13, len(X_norm))):
        try:
            gmm = GaussianMixture(n_components=k, n_init=1,
                                  max_iter=100, random_state=42)
            gmm.fit(X_norm)
            bic = gmm.bic(X_norm)
            if bic < best_bic:
                best_bic = bic
                best_k = k
                best_model = gmm
        except Exception:
            pass

    labels = best_model.predict(X_norm) if best_model else np.zeros(len(X_norm), dtype=int)
    return labels, best_k


def strategy_t_bins(vectors, K=6):
    """Uniform T-only bins: equal-width bins on temperature."""
    T = vectors[:, 0]
    t_min, t_max = T.min(), T.max()
    if t_max - t_min < 1e-10:
        return np.zeros(len(T), dtype=np.int32), 1
    edges = np.linspace(t_min, t_max + 1e-10, K + 1)
    return np.digitize(T, edges[1:-1]).astype(np.int32), K


def strategy_q_phase(vectors, phi_thresh=0.02):
    """Q-action x Phase: 3 Q levels x 2 phase states = 6 states."""
    Q, phi = vectors[:, 4], vectors[:, 1]
    q_tertiles = np.percentile(Q, [33.3, 66.7])
    q_level = np.digitize(Q, q_tertiles).astype(np.int32)  # 0, 1, 2
    vapor = (phi > phi_thresh).astype(np.int32)  # 0, 1
    return q_level * 2 + vapor


def strategy_random(vectors, K=6, rng=None):
    """Random assignment: null control."""
    return rng.integers(0, K, size=len(vectors)).astype(np.int32)


# ============================================================
# LANE ANALYSIS (vectorized — clones T2 pattern)
# ============================================================

def assign_lanes(labels, vectors, K):
    """Assign each discrete state to a lane based on mean dT."""
    dT = vectors[:, 2]
    state_mean_dT = np.zeros(K)
    for k in range(K):
        mask = labels == k
        if np.any(mask):
            state_mean_dT[k] = dT[mask].mean()
    state_is_heating = state_mean_dT > 0  # True = heating (QO-like)
    return state_is_heating[labels], state_mean_dT


def lane_analysis_discrete(lane_labels, run_boundaries):
    """Compute lane metrics from binary lane assignment (vectorized)."""
    n_transitions = 0
    n_pairs = 0
    h2c = 0
    h_total = 0
    c2h = 0
    c_total = 0
    heat_runs = []
    cool_runs = []

    for start, end in run_boundaries:
        seq = lane_labels[start:end]
        if len(seq) < 2:
            continue
        curr = seq[:-1]
        nxt = seq[1:]

        # Alternation (vectorized)
        n_pairs += len(curr)
        n_transitions += int(np.sum(curr != nxt))

        # Asymmetry (vectorized boolean masks)
        h_mask = curr   # True = heating
        c_mask = ~curr  # True = cooling
        h_total += int(np.sum(h_mask))
        h2c += int(np.sum(h_mask & ~nxt))
        c_total += int(np.sum(c_mask))
        c2h += int(np.sum(c_mask & nxt))

        # Run lengths (vectorized via change points)
        changes = np.where(seq[:-1] != seq[1:])[0]
        starts_arr = np.concatenate([[0], changes + 1])
        ends_arr = np.concatenate([changes + 1, [len(seq)]])
        lengths = ends_arr - starts_arr
        run_types = seq[starts_arr]
        if np.any(run_types):
            heat_runs.extend(lengths[run_types].tolist())
        if np.any(~run_types):
            cool_runs.extend(lengths[~run_types].tolist())

    alt_rate = n_transitions / n_pairs if n_pairs > 0 else 0
    heat_to_cool = h2c / h_total if h_total > 0 else 0
    cool_to_heat = c2h / c_total if c_total > 0 else 0

    return {
        'alternation_rate': float(alt_rate),
        'heat_to_cool': float(heat_to_cool),
        'cool_to_heat': float(cool_to_heat),
        'asymmetry': float(heat_to_cool - cool_to_heat),
        'heat_run_median': float(np.median(heat_runs)) if heat_runs else 0,
        'cool_run_median': float(np.median(cool_runs)) if cool_runs else 0,
        'n_pairs': int(n_pairs),
    }


def post_overshoot_discrete(labels, lane_labels, run_boundaries,
                            overshoot_states):
    """Post-overshoot cooling rate from discrete states (vectorized)."""
    if not overshoot_states:
        return 0.0, 0

    # Pre-build overshoot mask for the full label array
    ov_mask = np.zeros(len(labels), dtype=bool)
    for s in overshoot_states:
        ov_mask |= (labels == s)

    total = 0
    cool_count = 0
    for start, end in run_boundaries:
        ov_seq = ov_mask[start:end]
        lane_seq = lane_labels[start:end]
        if len(ov_seq) < 2:
            continue
        # Transitions OUT of overshoot states (vectorized)
        leaving_ov = ov_seq[:-1]
        next_cool = ~lane_seq[1:]
        total += int(np.sum(leaving_ov))
        cool_count += int(np.sum(leaving_ov & next_cool))

    rate = cool_count / total if total > 0 else 0
    return float(rate), int(total)


# ============================================================
# LEGALITY IMPOSITION LAYER
# ============================================================

def build_legality_matrix_lane_temp(K=6):
    """Physically-motivated forbidden transitions for Lane x Temp strategy.

    States: {0: cool_below, 1: cool_near, 2: cool_above,
             3: heat_below, 4: heat_near, 5: heat_above}

    Forbidden: transitions spanning 2+ temp zones in one step
    AND simultaneous lane reversal across distant zones.
    """
    forbidden = np.zeros((K, K), dtype=bool)
    # Can't jump from below to above (or vice versa) in one step
    # regardless of lane:
    #   cool_below(0) -> cool_above(2), cool_above(2) -> cool_below(0)
    #   heat_below(3) -> heat_above(5), heat_above(5) -> heat_below(3)
    #   cool_below(0) -> heat_above(5), heat_above(5) -> cool_below(0)
    #   heat_below(3) -> cool_above(2), cool_above(2) -> heat_below(3)
    pairs = [(0, 2), (2, 0), (3, 5), (5, 3),
             (0, 5), (5, 0), (3, 2), (2, 3)]
    for i, j in pairs:
        forbidden[i, j] = True
    return forbidden


def build_legality_matrix_operational(K=6):
    """Physically-motivated forbidden transitions for Operational Regime.

    States: {0: cold_start, 1: stabilize, 2: active_boil,
             3: overshoot, 4: recovery, 5: condensing}

    Forbidden: physically impossible single-step transitions.
    """
    forbidden = np.zeros((K, K), dtype=bool)
    pairs = [
        (0, 3),  # cold_start -> overshoot (can't jump to overheat)
        (5, 3),  # condensing -> overshoot (stable state can't overheat)
        (3, 0),  # overshoot -> cold_start (can't cool that fast)
        (4, 0),  # recovery -> cold_start (still above boil during recovery)
        (0, 4),  # cold_start -> recovery (not above boil yet)
        (5, 2),  # condensing -> active_boil (vapor already settled)
    ]
    for i, j in pairs:
        if i < K and j < K:
            forbidden[i, j] = True
    return forbidden


def build_legality_matrix_q_phase(K=6):
    """Physically-motivated forbidden transitions for Q-action x Phase.

    States: Q_level(0,1,2) x phase(0=no_vapor, 1=vapor)
    State = q_level * 2 + vapor: {0: low_dry, 1: low_wet, 2: mid_dry,
                                    3: mid_wet, 4: high_dry, 5: high_wet}

    Forbidden: jumping 2 Q levels in one step (fire can't change that fast).
    """
    forbidden = np.zeros((K, K), dtype=bool)
    for i in range(K):
        for j in range(K):
            q_i, q_j = i // 2, j // 2
            if abs(q_i - q_j) >= 2:
                forbidden[i, j] = True
    return forbidden


def check_legality(labels, run_boundaries, forbidden_matrix):
    """Check observed data against legality rules (vectorized).

    Returns: n_defined_forbidden, n_observed_violations, violation_rate.
    """
    K = forbidden_matrix.shape[0]
    n_defined = int(np.sum(forbidden_matrix))

    obs_counts = np.zeros((K, K), dtype=np.int64)
    total_transitions = 0
    for start, end in run_boundaries:
        seq = labels[start:end]
        if len(seq) < 2:
            continue
        np.add.at(obs_counts, (seq[:-1], seq[1:]), 1)
        total_transitions += len(seq) - 1

    violations = int(np.sum(obs_counts[forbidden_matrix]))
    rate = violations / total_transitions if total_transitions > 0 else 0

    # Which defined-forbidden transitions are actually observed=0?
    truly_absent = int(np.sum(forbidden_matrix & (obs_counts == 0)))

    return {
        'n_defined_forbidden': n_defined,
        'n_truly_absent': truly_absent,
        'n_violations': violations,
        'violation_rate': float(rate),
        'total_transitions': total_transitions,
    }


# ============================================================
# SCORING (direction-of-movement, not pass/fail)
# ============================================================

def score_strategy(labels, vectors, run_boundaries, K, rng,
                   legality_matrix=None):
    """Full metric extraction for one strategy on one parameterization."""
    # Effective K (states with observations)
    present = np.unique(labels)
    effective_k = len(present)

    # Transition matrix + hub
    trans, stat, counts, hub_state = compute_transition_matrix(
        labels, run_boundaries)
    hub_mass = float(stat[hub_state])

    # Spectral
    spectral_gap, mixing_time = spectral_analysis(trans)

    # Forbidden (null-calibrated)
    forbidden = forbidden_transitions_null_calibrated(
        labels, run_boundaries, K, rng)

    # Lane assignment + metrics
    lane_labels, state_mean_dT = assign_lanes(labels, vectors, K)
    lanes = lane_analysis_discrete(lane_labels, run_boundaries)

    # Post-overshoot: states with mean phi > 0.10 are overshoot candidates
    phi = vectors[:, 1]
    state_mean_phi = np.zeros(K)
    for k in range(K):
        mask = labels == k
        if np.any(mask):
            state_mean_phi[k] = phi[mask].mean()
    overshoot_states = set(np.where(state_mean_phi > 0.05)[0])
    post_ov_rate, post_ov_total = post_overshoot_discrete(
        labels, lane_labels, run_boundaries, overshoot_states)

    # Safety buffers
    buffers = safety_buffer_scan(labels, run_boundaries, forbidden)

    # Legality
    legality = None
    if legality_matrix is not None:
        legality = check_legality(labels, run_boundaries, legality_matrix)

    return {
        'effective_k': int(effective_k),
        'hub_mass': float(hub_mass),
        'spectral_gap': float(spectral_gap),
        'mixing_time': float(mixing_time),
        'n_forbidden': len(forbidden),
        'lanes': lanes,
        'post_overshoot_cool_rate': float(post_ov_rate),
        'post_overshoot_total': int(post_ov_total),
        'buffer_rate': float(buffers['buffer_rate']),
        'legality': legality,
        'state_populations': {
            int(k): int(np.sum(labels == k)) for k in range(K)
        },
    }


# ============================================================
# MAIN
# ============================================================

STRATEGIES = {
    'lane_temp': {'K': 6, 'has_legality': True},
    'operational': {'K': 6, 'has_legality': True},
    'gmm_bic': {'K': None, 'has_legality': False},
    't_bins': {'K': 6, 'has_legality': False},
    'q_phase': {'K': 6, 'has_legality': True},
    'random': {'K': 6, 'has_legality': False},
}


def main():
    rng = np.random.default_rng(42)
    t1_data = load_t1()
    params_list = t1_data['parameterizations']

    # Pre-build legality matrices
    legality_matrices = {
        'lane_temp': build_legality_matrix_lane_temp(6),
        'operational': build_legality_matrix_operational(6),
        'q_phase': build_legality_matrix_q_phase(6),
    }

    all_results = {name: [] for name in STRATEGIES}

    for pi, param_data in enumerate(params_list):
        vectors, run_boundaries, t_boil_vec = extract_with_tboil(param_data)
        if len(vectors) < 20:
            continue

        # Apply each strategy
        for name in STRATEGIES:
            if name == 'lane_temp':
                labels = strategy_lane_temp(vectors, t_boil_vec)
                K = 6
            elif name == 'operational':
                labels = strategy_operational(vectors, t_boil_vec)
                K = 6
            elif name == 'gmm_bic':
                labels, K = strategy_gmm_bic(vectors)
            elif name == 't_bins':
                labels, K = strategy_t_bins(vectors, K=6)
            elif name == 'q_phase':
                labels = strategy_q_phase(vectors)
                K = 6
            elif name == 'random':
                labels = strategy_random(vectors, K=6, rng=rng)
                K = 6

            leg_matrix = legality_matrices.get(name)
            result = score_strategy(labels, vectors, run_boundaries, K,
                                    rng, leg_matrix)
            result['param_id'] = param_data['param_id']
            result['nominal_k'] = K
            all_results[name].append(result)

        if (pi + 1) % 25 == 0:
            # Progress: show lane_temp spectral gap as representative
            lt = all_results['lane_temp'][-1]
            print(f"  Param {pi+1}/100: "
                  f"lane_temp gap={lt['spectral_gap']:.3f} "
                  f"forb={lt['n_forbidden']} "
                  f"hub={lt['hub_mass']:.3f} "
                  f"alt={lt['lanes']['alternation_rate']:.3f}")

    # Summary per strategy
    output = {'strategies': {}}
    for name, results in all_results.items():
        gaps = [r['spectral_gap'] for r in results]
        hubs = [r['hub_mass'] for r in results]
        forbs = [r['n_forbidden'] for r in results]
        alts = [r['lanes']['alternation_rate'] for r in results]
        asym = [r['lanes']['asymmetry'] for r in results]
        h_run = [r['lanes']['heat_run_median'] for r in results]
        c_run = [r['lanes']['cool_run_median'] for r in results]
        post_ov = [r['post_overshoot_cool_rate'] for r in results]
        buf = [r['buffer_rate'] for r in results]
        eff_k = [r['effective_k'] for r in results]

        summary = {
            'n_params': len(results),
            'effective_k': {
                'median': float(np.median(eff_k)),
                'mean': float(np.mean(eff_k)),
            },
            'spectral_gap': {
                'median': float(np.median(gaps)),
                'mean': float(np.mean(gaps)),
            },
            'hub_mass': {
                'median': float(np.median(hubs)),
                'mean': float(np.mean(hubs)),
            },
            'n_forbidden': {
                'median': float(np.median(forbs)),
                'mean': float(np.mean(forbs)),
            },
            'alternation_rate': {
                'median': float(np.median(alts)),
                'mean': float(np.mean(alts)),
            },
            'asymmetry': {
                'median': float(np.median(asym)),
                'mean': float(np.mean(asym)),
            },
            'heat_run_median': {
                'median': float(np.median(h_run)),
                'mean': float(np.mean(h_run)),
            },
            'cool_run_median': {
                'median': float(np.median(c_run)),
                'mean': float(np.mean(c_run)),
            },
            'post_overshoot_cool_rate': {
                'median': float(np.median(post_ov)),
                'mean': float(np.mean(post_ov)),
            },
            'buffer_rate': {
                'median': float(np.median(buf)),
                'mean': float(np.mean(buf)),
            },
            'oscillation_variation': float(max(alts) - min(alts)) if alts else 0,
        }

        # Legality summary
        if STRATEGIES[name]['has_legality']:
            leg_defined = [r['legality']['n_defined_forbidden']
                          for r in results if r['legality']]
            leg_absent = [r['legality']['n_truly_absent']
                         for r in results if r['legality']]
            leg_violations = [r['legality']['violation_rate']
                            for r in results if r['legality']]
            summary['legality'] = {
                'n_defined_forbidden': int(leg_defined[0]) if leg_defined else 0,
                'median_truly_absent': float(np.median(leg_absent)) if leg_absent else 0,
                'median_violation_rate': float(np.median(leg_violations)) if leg_violations else 0,
            }

        output['strategies'][name] = {
            'summary': summary,
            'per_parameterization': results,
        }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't1_discretization_scoring.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    # Print summary
    print(f"\n{'='*70}")
    print(f"T1 CATEGORICAL DISCRETIZATION SCORING")
    print(f"{'='*70}")
    print(f"")
    print(f"{'Strategy':<16s} {'K':>5s} {'Gap':>7s} {'Hub':>7s} "
          f"{'Forb':>6s} {'Alt':>7s} {'Asym':>7s} {'PostOv':>7s} "
          f"{'RunH':>5s} {'RunC':>5s}")
    print(f"{'-'*16} {'-'*5} {'-'*7} {'-'*7} {'-'*6} {'-'*7} "
          f"{'-'*7} {'-'*7} {'-'*5} {'-'*5}")

    # Voynich targets for reference
    print(f"{'VOYNICH':.<16s} {'5-7':>5s} {'>0.80':>7s} {'0.60':>7s} "
          f"{'10-25':>6s} {'0.549':>7s} {'+0.04':>7s} {'>0.70':>7s} "
          f"{'1.0':>5s} {'1.0':>5s}")
    print(f"{'CONTINUOUS':.<16s} {'10':>5s} {'0.000':>7s} {'0.558':>7s} "
          f"{'0':>6s} {'0.462':>7s} {'-0.00':>7s} {'0.215':>7s} "
          f"{'2.0':>5s} {'2.0':>5s}")

    for name in ['lane_temp', 'operational', 'gmm_bic', 't_bins',
                  'q_phase', 'random']:
        s = output['strategies'][name]['summary']
        k_str = f"{s['effective_k']['median']:.0f}"
        print(f"{name:<16s} {k_str:>5s} "
              f"{s['spectral_gap']['median']:>7.3f} "
              f"{s['hub_mass']['median']:>7.3f} "
              f"{s['n_forbidden']['median']:>6.0f} "
              f"{s['alternation_rate']['median']:>7.3f} "
              f"{s['asymmetry']['median']:>7.3f} "
              f"{s['post_overshoot_cool_rate']['median']:>7.3f} "
              f"{s['heat_run_median']['median']:>5.1f} "
              f"{s['cool_run_median']['median']:>5.1f}")

    print(f"")

    # Legality summary
    print(f"LEGALITY IMPOSITION LAYER:")
    for name in ['lane_temp', 'operational', 'q_phase']:
        leg = output['strategies'][name]['summary'].get('legality', {})
        print(f"  {name}: {leg.get('n_defined_forbidden', 0)} rules, "
              f"{leg.get('median_truly_absent', 0):.0f} truly absent, "
              f"violation rate {leg.get('median_violation_rate', 0):.4f}")

    print(f"")
    print(f"Output: {out_path}")


if __name__ == '__main__':
    main()
