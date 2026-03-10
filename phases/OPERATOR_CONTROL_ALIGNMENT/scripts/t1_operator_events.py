"""
T1: Operator Event Simulation — Phase 556: OPERATOR_CONTROL_ALIGNMENT
=====================================================================

Two-level extraction from P-controlled thermal reflux simulation:

Level A: Primitive operator actions (mechanical, Voynich-free)
  - dQ_sign, dQ_mag, error_sign, error_mag, stability, phase_activity
  - check_event (endogenous, condition-triggered)
  - hold_duration, cycle_position
  - Compound categories: INCREASE_BELOW, INCREASE_ABOVE, DECREASE_ABOVE,
    DECREASE_BELOW, HOLD_AT, HOLD_OFF, CHECK

Level B: Inferred latent structure (unsupervised, Voynich-free)
  - B1: HMM supervisory meta-states (BIC-selected k=2..6)
  - B2: Behavioral regime clustering (sliding windows)
  - B3: Change-point detection
  - B4: Observation-intervention separation

Cycle segmentation: Full trough-to-trough (symmetric physics;
operator provides asymmetry).

Non-circularity: ZERO Voynich parameters. All from control theory.
"""

import json
import sys
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*not converging.*')

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# PHYSICAL CONSTANTS — same C998 ODE
# ============================================================
DT = 0.02
N_STEPS = 1500
BURN_IN = 300
LAMBDA = 5.0
GAMMA = 0.05
C_EFF = 0.8
K_LOSS = 0.3
Q_MAX = 1.5
T_ENV = 0.0
DELAY = 15          # 15 * 0.02 = 0.30 time units
TARGET_FRAC = 0.05

SIGMA_Q = 0.08
SIGMA_T = 0.01 * np.sqrt(DT / 0.1)
SIGMA_BOIL = 0.02

N_PLANT_PARAMS = 100
N_OPERATOR_PARAMS = 10
N_RUNS_PER = 10
N_QUINTILES = 5
MIN_CYCLE = 8

PLANT_RANGES = {
    'T_boil':    (0.80, 1.20),
    'M':         (0.50, 2.00),
    'alpha':     (1.00, 3.00),
    'beta':      (0.50, 2.00),
    'K_p':       (1.00, 5.00),
    'bias_frac': (0.90, 1.30),
}

# Operator parameter ranges (generic, NOT Voynich-derived)
OPERATOR_RANGES = {
    'dead_zone_frac':      (0.05, 0.30),   # fraction of eq_scale
    'dQ_threshold_frac':   (0.01, 0.10),   # fraction of Q_MAX
    'check_holdoff':       (5, 25),         # steps
    'stability_trigger_frac': (0.3, 0.8),  # fraction of stability range
    'check_error_band_frac':  (0.1, 0.4),  # fraction of eq_scale
    'stability_window':    (3, 10),         # steps (integer)
}

# Compound action type indices
ACT_INCREASE_BELOW = 0
ACT_INCREASE_ABOVE = 1
ACT_DECREASE_ABOVE = 2
ACT_DECREASE_BELOW = 3
ACT_HOLD_AT = 4
ACT_HOLD_OFF = 5
ACT_CHECK = 6
N_ACTION_TYPES = 7
ACTION_NAMES = [
    'INCREASE_BELOW', 'INCREASE_ABOVE', 'DECREASE_ABOVE',
    'DECREASE_BELOW', 'HOLD_AT', 'HOLD_OFF', 'CHECK',
]


# ============================================================
# SIMULATION CORE — reused from Phase 555/C998
# ============================================================

def latin_hypercube_sample(n, ranges, rng):
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
    """Simulate one run. Returns raw arrays."""
    T_boil = params['T_boil'] + rng.normal(0, SIGMA_BOIL)
    M = params['M']
    alpha = params['alpha']
    beta = params['beta']
    K_p = params['K_p']
    bias_frac = params['bias_frac']

    T_target = T_boil * (1 + TARGET_FRAC)
    Q_bias = K_LOSS * T_boil * bias_frac
    eq_scale = abs(T_target - T_boil)
    if eq_scale < 1e-6:
        eq_scale = 0.05

    T = T_boil + rng.normal(0, 0.03)
    phi = rng.uniform(0.0, 0.02)
    T_history = [T] * DELAY
    prev_Q = Q_bias

    n_eff = N_STEPS
    T_arr = np.zeros(n_eff)
    phi_arr = np.zeros(n_eff)
    dT_arr = np.zeros(n_eff)
    dphi_arr = np.zeros(n_eff)
    Q_arr = np.zeros(n_eff)
    dQ_arr = np.zeros(n_eff)
    error_arr = np.zeros(n_eff)

    prev_T = T
    for step in range(n_eff):
        T_observed = T_history[0]
        error = T_target - T_observed
        Q = np.clip(K_p * error + Q_bias + rng.normal(0, SIGMA_Q), 0, Q_MAX)

        T_history.pop(0)
        T_history.append(T)

        V = alpha * max(0.0, 1.0 - phi) * max(0.0, T - T_boil)
        C_cond = beta * phi * C_EFF

        dT_phys = DT * (Q - LAMBDA * V + LAMBDA * C_cond
                        - K_LOSS * (T - T_ENV)) / M
        T_new = T + dT_phys + rng.normal(0, SIGMA_T)

        dphi_val = DT * (V - C_cond - GAMMA * phi)
        phi_new = np.clip(phi + dphi_val, 0.0, 1.0)

        T_arr[step] = T
        phi_arr[step] = phi
        dT_arr[step] = T_new - prev_T
        dphi_arr[step] = phi_new - phi
        Q_arr[step] = Q
        dQ_arr[step] = Q - prev_Q
        error_arr[step] = T_target - T

        prev_T = T
        prev_Q = Q
        T = T_new
        phi = phi_new

    sl = slice(BURN_IN, None)
    return {
        'T': T_arr[sl], 'phi': phi_arr[sl],
        'dT': dT_arr[sl], 'dphi': dphi_arr[sl],
        'Q': Q_arr[sl], 'dQ': dQ_arr[sl],
        'error': error_arr[sl],
        'T_target': T_target, 'T_boil': T_boil,
        'Q_bias': Q_bias, 'eq_scale': eq_scale,
    }


# ============================================================
# CYCLE SEGMENTATION — full trough-to-trough
# ============================================================

def segment_full_cycles(T_arr):
    """Segment into full trough-to-trough cycles.

    Physics is symmetric (up then down). Any asymmetry in operator
    action distributions within cycles reflects genuine decision patterns.
    """
    n = len(T_arr)
    if n < 20:
        return []

    window = 5
    kernel = np.ones(window) / window
    T_smooth = np.convolve(T_arr, kernel, mode='same')

    troughs = []
    for i in range(2, n - 2):
        if (T_smooth[i] <= T_smooth[i-1] and T_smooth[i] <= T_smooth[i-2] and
                T_smooth[i] <= T_smooth[i+1] and T_smooth[i] <= T_smooth[i+2]):
            troughs.append(i)

    cycles = []
    for i in range(len(troughs) - 1):
        length = troughs[i+1] - troughs[i]
        if length >= MIN_CYCLE:
            cycles.append((troughs[i], troughs[i+1]))

    return cycles


# ============================================================
# LEVEL A: PRIMITIVE ACTION EXTRACTION
# ============================================================

def extract_primitives(run_data, op_params):
    """Extract Level A primitives from simulation trace."""
    T = run_data['T']
    phi = run_data['phi']
    dQ = run_data['dQ']
    Q = run_data['Q']
    error = run_data['error']
    dphi = run_data['dphi']
    eq_scale = run_data['eq_scale']
    n = len(T)

    dead_zone = op_params['dead_zone_frac'] * eq_scale
    dQ_thresh = op_params['dQ_threshold_frac'] * Q_MAX
    stab_win = max(3, int(round(op_params['stability_window'])))
    check_holdoff = int(round(op_params['check_holdoff']))
    check_error_band = op_params['check_error_band_frac'] * eq_scale

    # Raw primitives
    dQ_sign = np.sign(dQ)
    dQ_mag = np.abs(dQ) / max(Q_MAX, 1e-6)
    error_sign = np.zeros(n)
    error_sign[error > dead_zone] = 1.0    # below target
    error_sign[error < -dead_zone] = -1.0  # above target
    error_mag = np.abs(error) / max(eq_scale, 1e-6)

    # Rolling stability (local T volatility)
    stability = np.zeros(n)
    for i in range(stab_win, n):
        stability[i] = np.std(T[i-stab_win:i])

    # Rolling phase activity
    phase_activity = np.zeros(n)
    for i in range(stab_win, n):
        phase_activity[i] = np.mean(np.abs(dphi[i-stab_win:i]))

    # Hold duration (steps since last significant actuator change)
    hold_duration = np.zeros(n)
    last_change = 0
    for i in range(n):
        if np.abs(dQ[i]) > dQ_thresh:
            last_change = i
        hold_duration[i] = i - last_change

    # Endogenous check events
    check_event = np.zeros(n, dtype=bool)
    stab_range = max(stability.max() - stability.min(), 1e-6)
    stab_trigger = op_params['stability_trigger_frac'] * stab_range + stability.min()

    prev_in_band = abs(error[0]) <= check_error_band
    last_check = -check_holdoff  # allow first check immediately

    for i in range(1, n):
        triggered = False

        # Condition 1: enough idle time
        if hold_duration[i] >= check_holdoff and (i - last_check) >= check_holdoff:
            triggered = True

        # Condition 2: stability threshold crossing
        if i > 0 and ((stability[i] > stab_trigger) != (stability[i-1] > stab_trigger)):
            triggered = True

        # Condition 3: error leaving band
        in_band = abs(error[i]) <= check_error_band
        if prev_in_band and not in_band:
            triggered = True
        prev_in_band = in_band

        # Condition 4: phase activity onset
        if i > 0 and phase_activity[i] > 0 and phase_activity[i-1] == 0:
            triggered = True

        if triggered and (i - last_check) >= 2:  # debounce
            check_event[i] = True
            last_check = i

    # Compound action categories
    action_type = np.full(n, ACT_HOLD_AT)
    for i in range(n):
        if check_event[i]:
            action_type[i] = ACT_CHECK
        elif abs(dQ[i]) > dQ_thresh:
            if dQ[i] > 0:
                if error_sign[i] >= 0:    # below or at target
                    action_type[i] = ACT_INCREASE_BELOW
                else:
                    action_type[i] = ACT_INCREASE_ABOVE
            else:
                if error_sign[i] <= 0:    # above or at target
                    action_type[i] = ACT_DECREASE_ABOVE
                else:
                    action_type[i] = ACT_DECREASE_BELOW
        else:
            if abs(error[i]) <= dead_zone:
                action_type[i] = ACT_HOLD_AT
            else:
                action_type[i] = ACT_HOLD_OFF

    return {
        'dQ_sign': dQ_sign, 'dQ_mag': dQ_mag,
        'error_sign': error_sign, 'error_mag': error_mag,
        'stability': stability, 'phase_activity': phase_activity,
        'check_event': check_event, 'hold_duration': hold_duration,
        'action_type': action_type,
    }


# ============================================================
# PER-CYCLE FEATURE EXTRACTION
# ============================================================

def extract_cycle_features(cycle_start, cycle_end, primitives, run_data):
    """Extract Level A features for one cycle."""
    sl = slice(cycle_start, cycle_end)
    n = cycle_end - cycle_start
    if n < MIN_CYCLE:
        return None

    action = primitives['action_type'][sl]
    positions = np.linspace(0, 1, n, endpoint=False)
    quintiles = np.minimum((positions * N_QUINTILES).astype(int), N_QUINTILES - 1)

    # Action type distribution per quintile
    quintile_actions = np.zeros((N_QUINTILES, N_ACTION_TYPES))
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            for a in range(N_ACTION_TYPES):
                quintile_actions[q, a] = np.sum(action[mask] == a) / mask.sum()

    # Mean positions per action type
    mean_positions = {}
    for a in range(N_ACTION_TYPES):
        mask = action == a
        if mask.sum() > 0:
            mean_positions[ACTION_NAMES[a]] = float(np.mean(positions[mask]))
        else:
            mean_positions[ACTION_NAMES[a]] = -1.0

    # CHECK event positions
    check_mask = primitives['check_event'][sl]
    check_positions = positions[check_mask].tolist() if check_mask.any() else []

    # Raw primitive profiles per quintile (for primary scoring)
    dQ_mag = primitives['dQ_mag'][sl]
    error_mag = primitives['error_mag'][sl]
    error_sign = primitives['error_sign'][sl]
    stability = primitives['stability'][sl]
    phase_act = primitives['phase_activity'][sl]

    quintile_raw = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_raw[f'Q{q}'] = {
                'mean_dQ_mag': float(np.mean(dQ_mag[mask])),
                'mean_error_mag': float(np.mean(error_mag[mask])),
                'mean_error_sign': float(np.mean(error_sign[mask])),
                'mean_stability': float(np.mean(stability[mask])),
                'mean_phase_activity': float(np.mean(phase_act[mask])),
                'frac_increasing': float(np.mean(primitives['dQ_sign'][sl][mask] > 0)),
                'frac_decreasing': float(np.mean(primitives['dQ_sign'][sl][mask] < 0)),
            }

    # Observation vs intervention (Level B4 input)
    obs_mask = np.isin(action, [ACT_HOLD_AT, ACT_HOLD_OFF, ACT_CHECK])
    int_mask = ~obs_mask
    passive_mask = np.isin(action, [ACT_HOLD_AT, ACT_HOLD_OFF])
    active_mask = action == ACT_CHECK

    obs_mean_pos = float(np.mean(positions[obs_mask])) if obs_mask.any() else -1.0
    int_mean_pos = float(np.mean(positions[int_mask])) if int_mask.any() else -1.0
    passive_mean_pos = float(np.mean(positions[passive_mask])) if passive_mask.any() else -1.0
    active_mean_pos = float(np.mean(positions[active_mask])) if active_mask.any() else -1.0

    # Transition bigrams
    bigrams = np.zeros((N_ACTION_TYPES, N_ACTION_TYPES))
    for i in range(len(action) - 1):
        bigrams[action[i], action[i+1]] += 1
    total_trans = bigrams.sum()
    if total_trans > 0:
        bigrams_norm = bigrams / total_trans
    else:
        bigrams_norm = bigrams

    # Cycle metadata
    T_sl = run_data['T'][sl]
    error_sl = run_data['error'][sl]

    return {
        'length': n,
        'quintile_actions': quintile_actions.tolist(),
        'mean_positions': mean_positions,
        'check_positions': check_positions,
        'quintile_raw': quintile_raw,
        'obs_mean_pos': obs_mean_pos,
        'int_mean_pos': int_mean_pos,
        'passive_mean_pos': passive_mean_pos,
        'active_mean_pos': active_mean_pos,
        'bigrams': bigrams_norm.tolist(),
        'mean_error': float(np.mean(error_sl)),
        'max_overshoot': float(np.max(-error_sl)) if len(error_sl) > 0 else 0.0,
        'mean_T': float(np.mean(T_sl)),
        'n_checks': int(check_mask.sum()),
        'action_counts': [int(np.sum(action == a)) for a in range(N_ACTION_TYPES)],
    }


# ============================================================
# LEVEL B: INFERRED LATENT STRUCTURE
# ============================================================

def infer_hmm_states(primitives, n_states_range=(2, 7)):
    """Fit Gaussian HMM with BIC model selection."""
    try:
        import logging
        logging.getLogger('hmmlearn').setLevel(logging.ERROR)
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        return None

    features = np.column_stack([
        primitives['dQ_mag'],
        primitives['error_mag'],
        primitives['stability'],
        np.minimum(primitives['hold_duration'] / 25.0, 1.0),
    ])

    n = len(features)
    if n < 50:
        return None

    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    best_bic = np.inf
    best_model = None
    best_k = 2

    for k in range(n_states_range[0], n_states_range[1]):
        try:
            model = GaussianHMM(n_components=k, covariance_type='diag',
                                n_iter=50, random_state=42, verbose=False)
            model.fit(features_scaled)
            ll = model.score(features_scaled)
            n_params = k * (features.shape[1] * 2 + k)
            bic = -2 * ll * n + n_params * np.log(n)
            if bic < best_bic:
                best_bic = bic
                best_model = model
                best_k = k
        except Exception:
            continue

    if best_model is None:
        return None

    labels = best_model.predict(features_scaled)
    centroids = best_model.means_

    return {
        'labels': labels,
        'k': best_k,
        'centroids': centroids.tolist(),
        'transition_matrix': best_model.transmat_.tolist(),
    }


def infer_regime_clustering(primitives, window=10):
    """Sliding window regime clustering."""
    action = primitives['action_type']
    n = len(action)
    if n < window * 3:
        return None

    windows = []
    positions = []
    for i in range(0, n - window, window // 2):
        win = action[i:i+window]
        dist = np.zeros(N_ACTION_TYPES)
        for a in range(N_ACTION_TYPES):
            dist[a] = np.sum(win == a) / window
        windows.append(dist)
        positions.append((i + window / 2) / n)

    X = np.array(windows)
    if len(X) < 6:
        return None

    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    best_k = 2
    best_sil = -1
    best_labels = None
    best_centroids = None

    for k in range(2, min(7, len(X))):
        try:
            km = KMeans(n_clusters=k, n_init=5, random_state=42)
            labs = km.fit_predict(X)
            if len(set(labs)) < 2:
                continue
            sil = silhouette_score(X, labs)
            if sil > best_sil:
                best_sil = sil
                best_k = k
                best_labels = labs
                best_centroids = km.cluster_centers_.tolist()
        except Exception:
            continue

    if best_labels is None:
        return None

    return {
        'labels': best_labels.tolist(),
        'positions': positions,
        'k': best_k,
        'centroids': best_centroids,
        'silhouette': float(best_sil),
    }


def detect_change_points(primitives):
    """Detect behavioral change points."""
    try:
        import ruptures as rpt
    except ImportError:
        return None

    features = np.column_stack([
        primitives['dQ_mag'],
        primitives['error_mag'],
        primitives['stability'],
    ])

    n = len(features)
    if n < 30:
        return None

    try:
        algo = rpt.Pelt(model='rbf', min_size=5).fit(features)
        change_points = algo.predict(pen=3)
        # Normalize to [0,1]
        cp_frac = [cp / n for cp in change_points if cp < n]
        return cp_frac
    except Exception:
        return None


# ============================================================
# LEVEL B PER-CYCLE FEATURES
# ============================================================

def extract_hmm_cycle_features(hmm_result, cycle_start, cycle_end, n_total):
    """Extract HMM features for one cycle."""
    if hmm_result is None:
        return None

    labels = hmm_result['labels'][cycle_start:cycle_end]
    k = hmm_result['k']
    n = len(labels)
    if n < MIN_CYCLE:
        return None

    positions = np.linspace(0, 1, n, endpoint=False)
    quintiles = np.minimum((positions * N_QUINTILES).astype(int), N_QUINTILES - 1)

    # Meta-state distribution per quintile
    quintile_states = np.zeros((N_QUINTILES, k))
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            for s in range(k):
                quintile_states[q, s] = np.sum(labels[mask] == s) / mask.sum()

    # Persistence and interleaving
    same_count = sum(1 for i in range(len(labels)-1) if labels[i] == labels[i+1])
    persistence = same_count / max(len(labels) - 1, 1)
    interleaving = 1.0 - persistence

    # Non-contiguous: are different states interspersed?
    runs = []
    cur = labels[0]
    for l in labels[1:]:
        if l != cur:
            runs.append(cur)
            cur = l
    runs.append(cur)
    non_contiguous = len(runs) >= 3  # at least 3 runs = interleaved

    return {
        'quintile_states': quintile_states.tolist(),
        'persistence': float(persistence),
        'interleaving': float(interleaving),
        'non_contiguous': bool(non_contiguous),
        'n_switches': int(len(runs) - 1),
        'k': k,
    }


# ============================================================
# APPARATUS FAMILY CLASSIFICATION
# ============================================================

def classify_apparatus_families(run_summaries):
    """Classify plant parameterizations into 3 apparatus families."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    features = []
    for s in run_summaries:
        features.append([
            s.get('mean_overshoot', 0),
            s.get('mean_cycle_length', 15),
            s.get('correction_rate', 0),
            s.get('stability_variance', 0),
        ])

    X = np.array(features)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=3, n_init=10, random_state=42)
    labels = km.fit_predict(X_scaled)

    # Name families by centroid characteristics
    centroids = km.cluster_centers_
    # Sort by mean_overshoot (column 0)
    order = np.argsort(centroids[:, 0])
    label_map = {old: new for new, old in enumerate(order)}
    labels = np.array([label_map[l] for l in labels])
    family_names = ['SLOW_SUSTAINED', 'MODERATE', 'FAST_AGGRESSIVE']

    return labels, family_names


# ============================================================
# MAIN
# ============================================================

def main():
    rng = np.random.default_rng(42)

    print("Generating LHS samples...")
    plant_params = latin_hypercube_sample(N_PLANT_PARAMS, PLANT_RANGES, rng)
    operator_params = latin_hypercube_sample(N_OPERATOR_PARAMS, OPERATOR_RANGES, rng)

    all_cycles = []
    run_summaries = []
    total_cycles = 0
    hmm_bic_ks = []

    # HMM is expensive — only run on sampled runs (every HMM_SAMPLE_RATE'th)
    HMM_SAMPLE_RATE = 100

    n_total_runs = N_PLANT_PARAMS * N_OPERATOR_PARAMS * N_RUNS_PER
    run_count = 0

    for pi, pp in enumerate(plant_params):
        for oi, op in enumerate(operator_params):
            for ri in range(N_RUNS_PER):
                run_count += 1
                if run_count % 1000 == 0:
                    print(f"  Run {run_count}/{n_total_runs}: "
                          f"cycles_so_far={total_cycles}", flush=True)

                run_data = simulate_run(pp, rng)
                primitives = extract_primitives(run_data, op)
                cycles = segment_full_cycles(run_data['T'])

                # Level B inference (sampled — HMM is expensive)
                hmm_result = None
                if run_count % HMM_SAMPLE_RATE == 0:
                    hmm_result = infer_hmm_states(primitives)
                    if hmm_result is not None:
                        hmm_bic_ks.append(hmm_result['k'])

                # Per-run summary for apparatus classification
                run_corr_rate = 0
                run_overshoots = []
                run_cycle_lengths = []

                for cs, ce in cycles:
                    cf = extract_cycle_features(cs, ce, primitives, run_data)
                    if cf is None:
                        continue

                    # Add HMM features
                    hmm_cf = extract_hmm_cycle_features(
                        hmm_result, cs, ce, len(run_data['T']))

                    cycle_record = {
                        'plant_param_idx': pi,
                        'operator_param_idx': oi,
                        'run_idx': ri,
                        **cf,
                    }
                    if hmm_cf is not None:
                        cycle_record['hmm'] = hmm_cf

                    all_cycles.append(cycle_record)
                    total_cycles += 1

                    run_overshoots.append(cf['max_overshoot'])
                    run_cycle_lengths.append(cf['length'])
                    corr_count = cf['action_counts'][ACT_DECREASE_ABOVE]
                    run_corr_rate += corr_count / max(cf['length'], 1)

                if run_cycle_lengths:
                    run_summaries.append({
                        'plant_param_idx': pi,
                        'mean_overshoot': float(np.mean(run_overshoots)),
                        'mean_cycle_length': float(np.mean(run_cycle_lengths)),
                        'correction_rate': float(run_corr_rate / len(run_cycle_lengths)),
                        'stability_variance': float(np.var(run_overshoots))
                            if len(run_overshoots) > 1 else 0.0,
                    })

    print(f"\nTotal cycles: {total_cycles}")
    print(f"Total runs: {run_count}")

    # Apparatus classification
    # Aggregate run summaries by plant param
    plant_summaries = []
    for pi in range(N_PLANT_PARAMS):
        runs = [s for s in run_summaries if s['plant_param_idx'] == pi]
        if runs:
            plant_summaries.append({
                'mean_overshoot': float(np.mean([s['mean_overshoot'] for s in runs])),
                'mean_cycle_length': float(np.mean([s['mean_cycle_length'] for s in runs])),
                'correction_rate': float(np.mean([s['correction_rate'] for s in runs])),
                'stability_variance': float(np.mean([s['stability_variance'] for s in runs])),
            })
        else:
            plant_summaries.append({
                'mean_overshoot': 0, 'mean_cycle_length': 15,
                'correction_rate': 0, 'stability_variance': 0,
            })

    family_labels, family_names = classify_apparatus_families(plant_summaries)

    # Aggregate statistics
    agg_quintile_actions = np.zeros((N_QUINTILES, N_ACTION_TYPES))
    agg_count = 0
    cycle_lengths = []
    action_totals = np.zeros(N_ACTION_TYPES)

    for c in all_cycles:
        qa = np.array(c['quintile_actions'])
        agg_quintile_actions += qa
        agg_count += 1
        cycle_lengths.append(c['length'])
        for a in range(N_ACTION_TYPES):
            action_totals[a] += c['action_counts'][a]

    if agg_count > 0:
        agg_quintile_actions /= agg_count

    # HMM BIC distribution
    hmm_k_counts = {}
    for k in hmm_bic_ks:
        hmm_k_counts[k] = hmm_k_counts.get(k, 0) + 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"T1 OPERATOR EVENTS COMPLETE")
    print(f"{'='*60}")
    print(f"Plant parameterizations: {N_PLANT_PARAMS}")
    print(f"Operator parameterizations: {N_OPERATOR_PARAMS}")
    print(f"Runs per combo: {N_RUNS_PER}")
    print(f"Total runs: {run_count}")
    print(f"Total cycles: {total_cycles}")
    if cycle_lengths:
        print(f"Cycle length: mean={np.mean(cycle_lengths):.1f}  "
              f"median={np.median(cycle_lengths):.0f}  "
              f"range=[{min(cycle_lengths)}, {max(cycle_lengths)}]")

    print(f"\nACTION TYPE TOTALS:")
    total_actions = action_totals.sum()
    for a in range(N_ACTION_TYPES):
        pct = 100 * action_totals[a] / max(total_actions, 1)
        print(f"  {ACTION_NAMES[a]:<20s} {action_totals[a]:>10.0f}  ({pct:.1f}%)")

    print(f"\nAGGREGATE QUINTILE ACTION PROFILE:")
    print(f"  {'Q':<4}", end='')
    for name in ACTION_NAMES:
        print(f"  {name[:8]:>8}", end='')
    print()
    for q in range(N_QUINTILES):
        print(f"  Q{q:<3}", end='')
        for a in range(N_ACTION_TYPES):
            print(f"  {agg_quintile_actions[q, a]:>8.3f}", end='')
        print()

    print(f"\nHMM BIC-SELECTED STATE COUNTS:")
    for k in sorted(hmm_k_counts.keys()):
        print(f"  k={k}: {hmm_k_counts[k]} runs ({100*hmm_k_counts[k]/max(len(hmm_bic_ks),1):.1f}%)")

    print(f"\nAPPARATUS FAMILIES:")
    for fi, fname in enumerate(family_names):
        count = sum(1 for l in family_labels if l == fi)
        print(f"  {fname}: {count} parameterizations")

    # Build compact output — numpy arrays for per-cycle data
    # This avoids 2GB+ JSON files
    summary = {
        'n_plant_params': N_PLANT_PARAMS,
        'n_operator_params': N_OPERATOR_PARAMS,
        'n_runs_per': N_RUNS_PER,
        'total_runs': run_count,
        'total_cycles': total_cycles,
        'cycle_length_mean': float(np.mean(cycle_lengths)) if cycle_lengths else 0,
        'cycle_length_median': float(np.median(cycle_lengths)) if cycle_lengths else 0,
        'action_totals': {ACTION_NAMES[a]: int(action_totals[a])
                          for a in range(N_ACTION_TYPES)},
        'aggregate_quintile_actions': agg_quintile_actions.tolist(),
        'hmm_bic_k_distribution': hmm_k_counts,
        'apparatus_families': {
            'names': family_names,
            'plant_assignments': family_labels.tolist(),
        },
        'non_circularity': {
            'voynich_input': 'NONE — zero Voynich-derived values in T1',
            'event_types': 'From controller state algebra (dQ × error sign)',
            'check_triggers': 'Endogenous: hold_duration, stability, error_band, phase_activity',
            'hmm': 'Unsupervised: BIC-selected state count on raw primitives',
        },
        'design_note': (
            'Full trough-to-trough cycles. Physics is symmetric. '
            'Operator asymmetry is genuine. Compound categories are '
            'secondary; raw primitives are primary scoring inputs.'
        ),
    }

    # Write summary JSON (small)
    summary_path = RESULTS_DIR / 't1_operator_events.json'
    print(f"\nWriting summary to {summary_path}...")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary size: {summary_path.stat().st_size / 1e3:.1f} KB")

    # Write per-cycle data as compressed numpy arrays
    n_cyc = len(all_cycles)
    print(f"Packing {n_cyc} cycles into numpy arrays...")

    # Core arrays T3 needs
    qa_arr = np.zeros((n_cyc, N_QUINTILES, N_ACTION_TYPES), dtype=np.float32)
    bigrams_arr = np.zeros((n_cyc, N_ACTION_TYPES, N_ACTION_TYPES), dtype=np.float32)
    positions_arr = np.zeros((n_cyc, N_ACTION_TYPES), dtype=np.float32)
    counts_arr = np.zeros((n_cyc, N_ACTION_TYPES), dtype=np.int32)
    meta_arr = np.zeros((n_cyc, 6), dtype=np.float32)  # length, max_overshoot, obs/int/passive/active pos
    param_arr = np.zeros((n_cyc, 3), dtype=np.int32)   # plant_idx, operator_idx, run_idx

    # quintile_raw arrays for H6 stability context
    qr_stability = np.zeros((n_cyc, N_QUINTILES), dtype=np.float32)
    qr_phase_activity = np.zeros((n_cyc, N_QUINTILES), dtype=np.float32)

    # HMM features (sparse — only for sampled runs)
    hmm_interleaving = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_persistence = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_non_contiguous = np.zeros(n_cyc, dtype=np.int8)
    hmm_k = np.zeros(n_cyc, dtype=np.int8)

    for i, c in enumerate(all_cycles):
        qa_arr[i] = np.array(c['quintile_actions'], dtype=np.float32)
        bigrams_arr[i] = np.array(c['bigrams'], dtype=np.float32)
        for a in range(N_ACTION_TYPES):
            positions_arr[i, a] = c['mean_positions'][ACTION_NAMES[a]]
        counts_arr[i] = np.array(c['action_counts'], dtype=np.int32)
        meta_arr[i] = [c['length'], c['max_overshoot'],
                        c['obs_mean_pos'], c['int_mean_pos'],
                        c['passive_mean_pos'], c['active_mean_pos']]
        param_arr[i] = [c['plant_param_idx'], c['operator_param_idx'], c['run_idx']]

        qr = c.get('quintile_raw', {})
        for q in range(N_QUINTILES):
            qk = f'Q{q}'
            if qk in qr:
                qr_stability[i, q] = qr[qk]['mean_stability']
                qr_phase_activity[i, q] = qr[qk]['mean_phase_activity']

        if 'hmm' in c and c['hmm'] is not None:
            hmm_interleaving[i] = c['hmm']['interleaving']
            hmm_persistence[i] = c['hmm']['persistence']
            hmm_non_contiguous[i] = 1 if c['hmm']['non_contiguous'] else 0
            hmm_k[i] = c['hmm']['k']

    npz_path = RESULTS_DIR / 't1_cycles.npz'
    np.savez_compressed(npz_path,
                        quintile_actions=qa_arr,
                        bigrams=bigrams_arr,
                        mean_positions=positions_arr,
                        action_counts=counts_arr,
                        meta=meta_arr,
                        params=param_arr,
                        qr_stability=qr_stability,
                        qr_phase_activity=qr_phase_activity,
                        hmm_interleaving=hmm_interleaving,
                        hmm_persistence=hmm_persistence,
                        hmm_non_contiguous=hmm_non_contiguous,
                        hmm_k=hmm_k)
    print(f"Cycles NPZ: {npz_path} ({npz_path.stat().st_size / 1e6:.1f} MB)")
    print(f"\nDone.")


if __name__ == '__main__':
    main()
