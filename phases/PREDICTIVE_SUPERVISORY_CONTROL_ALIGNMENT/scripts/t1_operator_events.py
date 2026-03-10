"""
T1: Operator Event Simulation — Phase 557: PREDICTIVE_SUPERVISORY_CONTROL_ALIGNMENT
====================================================================================

Two-layer controller over thermal reflux plant:

Layer 1 (inner): Model-Predictive Control (MPC)
  - 15 candidate Q values × N_p forward prediction steps
  - Asymmetric safety cost (overshoot penalized more than undershoot)
  - Operates within supervisor-approved Q range [Q_lo, Q_hi]

Layer 2 (outer): Discrete Supervisory Controller (6 states)
  - QUALIFYING:  stability not confirmed → Q restricted
  - TRACKING:    qualified, below target → full Q authority
  - MONITORING:  near target, passive → maintenance Q
  - CHECKING:    endogenous check triggers → Q frozen
  - CORRECTING:  above target → Q = 0 (hard gate)
  - CLOSING:     T declining in correction → reheat latched off

Level A: Same primitive action extraction as Phase 556
Level B: Same unsupervised inference (HMM, clustering)

Non-circularity: ZERO Voynich parameters. All from control theory.
"""

import json
import sys
import warnings
import numpy as np
from pathlib import Path
from collections import deque

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*not converging.*')

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# PHYSICAL CONSTANTS — same C998 ODE as Phase 555/556
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
DELAY = 15
TARGET_FRAC = 0.05

SIGMA_Q = 0.08
SIGMA_T = 0.01 * np.sqrt(DT / 0.1)
SIGMA_BOIL = 0.02

N_PARAM_SETS = 50        # system parameterizations (reduced from 100 for runtime)
N_OPERATOR_PARAMS = 10   # operator parameterizations (Level A classification)
N_RUNS_PER = 10
N_QUINTILES = 5
MIN_CYCLE = 8
N_CANDIDATES = 15        # MPC candidate Q values
HMM_SAMPLE_RATE = 100    # run HMM every Nth run

# Null supervisor sweep (reduced)
N_NULL_PARAM_SETS = 25
N_NULL_RUNS_PER = 5

# ============================================================
# SYSTEM PARAMETER RANGES (plant + MPC + supervisor)
# ============================================================
SYSTEM_RANGES = {
    # Plant (4 dims)
    'T_boil':    (0.80, 1.20),
    'M':         (0.50, 2.00),
    'alpha':     (1.00, 3.00),
    'beta':      (0.50, 2.00),
    # MPC (5 dims)
    'horizon':        (3, 15),
    'error_weight':   (0.5, 5.0),
    'safety_weight':  (1.0, 20.0),
    'effort_weight':  (0.01, 0.5),
    'rate_weight':    (0.0, 1.0),
    # Supervisor (6 dims)
    'qualify_dwell':             (3, 15),
    'stability_qualify_frac':    (0.2, 0.8),
    'monitor_band_frac':         (0.05, 0.30),
    'correction_threshold_frac': (0.05, 0.20),
    'Q_qualify_frac':            (0.05, 0.30),
    'close_dwell':               (3, 10),
}

# Fixed supervisor parameters (not swept)
Q_MONITOR_FRAC = 0.50    # moderate maintenance heating
Q_CORRECT = 0.0          # no heating during correction/closing
CHECK_DWELL = 3           # steps in CHECKING state
MIN_STATE_DWELL = 2       # anti-chatter minimum
PHASE_QUALIFY_FRAC = 0.5  # phase activity threshold
SUP_STABILITY_WINDOW = 8  # rolling window for supervisor stability

# Operator parameter ranges (Level A classification — same as Phase 556)
OPERATOR_RANGES = {
    'dead_zone_frac':          (0.05, 0.30),
    'dQ_threshold_frac':       (0.01, 0.10),
    'check_holdoff':           (5, 25),
    'stability_trigger_frac':  (0.3, 0.8),
    'check_error_band_frac':   (0.1, 0.4),
    'stability_window':        (3, 10),
}

# ============================================================
# COMPOUND ACTION TYPES (same as Phase 556)
# ============================================================
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
# SUPERVISOR STATES (from plant state algebra)
# ============================================================
SUP_QUALIFYING = 0
SUP_TRACKING = 1
SUP_MONITORING = 2
SUP_CHECKING = 3
SUP_CORRECTING = 4
SUP_CLOSING = 5
N_SUP_STATES = 6
SUP_NAMES = [
    'QUALIFYING', 'TRACKING', 'MONITORING', 'CHECKING',
    'CORRECTING', 'CLOSING',
]


# ============================================================
# LATIN HYPERCUBE SAMPLING (reused from Phase 556)
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


# ============================================================
# SIMULATION CORE — MPC + SUPERVISOR
# ============================================================

def simulate_run(sys_params, op_params, rng, null_mode=False):
    """Simulate one run with MPC inner loop + supervisor gate.

    null_mode=True: same states but degraded constraints
      - QUALIFYING allows full Q range (no gate)
      - MONITORING/CHECKING merged behavior
      - CORRECTING allows moderate Q (no hard gate)
      - CLOSING can return to TRACKING (no commitment latch)
    """
    T_boil = sys_params['T_boil'] + rng.normal(0, SIGMA_BOIL)
    M = sys_params['M']
    alpha = sys_params['alpha']
    beta = sys_params['beta']

    T_target = T_boil * (1 + TARGET_FRAC)
    eq_scale = abs(T_target - T_boil)
    if eq_scale < 1e-6:
        eq_scale = 0.05

    # MPC parameters
    horizon = max(3, int(round(sys_params['horizon'])))
    error_weight = sys_params['error_weight']
    safety_weight = sys_params['safety_weight']
    effort_weight = sys_params['effort_weight']
    rate_weight = sys_params['rate_weight']

    # Supervisor parameters
    qualify_dwell = max(3, int(round(sys_params['qualify_dwell'])))
    close_dwell_param = max(3, int(round(sys_params['close_dwell'])))
    monitor_band = sys_params['monitor_band_frac'] * eq_scale
    correction_threshold = sys_params['correction_threshold_frac'] * eq_scale
    Q_qualify_max = sys_params['Q_qualify_frac'] * Q_MAX
    Q_monitor_max = Q_MONITOR_FRAC * Q_MAX
    stability_qualify_threshold = sys_params['stability_qualify_frac'] * eq_scale

    # Operator parameters (for supervisor check triggers)
    check_holdoff = int(round(op_params['check_holdoff']))
    check_error_band = op_params['check_error_band_frac'] * eq_scale

    # Phase activity threshold for qualification
    phase_qualify_threshold = PHASE_QUALIFY_FRAC * eq_scale

    # Plant state
    T = T_boil + rng.normal(0, 0.03)
    phi = rng.uniform(0.0, 0.02)
    T_history = [T] * DELAY
    prev_Q = 0.0
    prev_T = T

    # Supervisor state
    sup_state = SUP_QUALIFYING
    sup_dwell = 0
    stab_confirm = 0       # consecutive stable steps
    dT_neg_count = 0       # consecutive dT < 0 steps
    check_remaining = 0    # steps left in CHECK

    # Supervisor rolling windows
    T_recent = deque([T] * SUP_STABILITY_WINDOW, maxlen=SUP_STABILITY_WINDOW)
    dphi_recent = deque([0.0] * SUP_STABILITY_WINDOW, maxlen=SUP_STABILITY_WINDOW)

    # Supervisor check trigger state
    sup_hold_duration = 0
    prev_sup_stab_above = False
    prev_sup_in_band = True
    prev_sup_phase_active = False

    # MPC working arrays (preallocated to avoid per-step allocation)
    _mpc_Q = np.empty(N_CANDIDATES)
    _mpc_T = np.empty(N_CANDIDATES)
    _mpc_phi = np.empty(N_CANDIDATES)
    _mpc_cost = np.empty(N_CANDIDATES)

    # Output arrays
    T_arr = np.zeros(N_STEPS)
    phi_arr = np.zeros(N_STEPS)
    dT_arr = np.zeros(N_STEPS)
    dphi_arr = np.zeros(N_STEPS)
    Q_arr = np.zeros(N_STEPS)
    dQ_arr = np.zeros(N_STEPS)
    error_arr = np.zeros(N_STEPS)
    sup_state_arr = np.zeros(N_STEPS, dtype=np.int8)

    prev_dphi = 0.0

    for step in range(N_STEPS):
        T_observed = T_history[0]
        error = T_target - T_observed

        # Update rolling supervisor statistics
        T_recent.append(T)
        dphi_recent.append(abs(prev_dphi))
        if step >= SUP_STABILITY_WINDOW:
            sup_stability = float(np.std(list(T_recent)))
            sup_phase_activity = float(np.mean(list(dphi_recent)))
        else:
            sup_stability = 0.0
            sup_phase_activity = 0.0

        # Update supervisor hold duration
        if step > 0 and abs(Q_arr[step-1] - (prev_Q if step <= 1 else Q_arr[step-2])) > 0.01 * Q_MAX:
            sup_hold_duration = 0
        else:
            sup_hold_duration += 1

        # dT tracking for CLOSING
        dT_current = T - prev_T

        # ---- SUPERVISOR STATE MACHINE ----
        sup_dwell += 1
        new_state = sup_state

        if sup_state == SUP_QUALIFYING:
            # Check stability confirmation
            if sup_stability < stability_qualify_threshold and sup_phase_activity < phase_qualify_threshold:
                stab_confirm += 1
            else:
                stab_confirm = 0

            if stab_confirm >= qualify_dwell and error > 0:
                new_state = SUP_TRACKING
                stab_confirm = 0

            # Q constraints
            if null_mode:
                Q_lo, Q_hi = 0.0, Q_MAX  # null: no gate
            else:
                Q_lo, Q_hi = 0.0, Q_qualify_max

        elif sup_state == SUP_TRACKING:
            if error < -correction_threshold:
                new_state = SUP_CORRECTING
                dT_neg_count = 0
            elif abs(error) < monitor_band and sup_dwell >= MIN_STATE_DWELL:
                new_state = SUP_MONITORING
            Q_lo, Q_hi = 0.0, Q_MAX

        elif sup_state == SUP_MONITORING:
            # Check triggers for MONITORING → CHECKING
            check_triggered = False
            # Trigger 1: idle holdoff
            if sup_hold_duration >= check_holdoff:
                check_triggered = True
            # Trigger 2: stability crossing
            stab_above = sup_stability > stability_qualify_threshold
            if stab_above != prev_sup_stab_above and step > SUP_STABILITY_WINDOW:
                check_triggered = True
            prev_sup_stab_above = stab_above
            # Trigger 3: error leaving band
            in_band = abs(error) <= check_error_band
            if prev_sup_in_band and not in_band:
                check_triggered = True
            prev_sup_in_band = in_band
            # Trigger 4: phase activity onset
            phase_active = sup_phase_activity > phase_qualify_threshold * 0.5
            if phase_active and not prev_sup_phase_active:
                check_triggered = True
            prev_sup_phase_active = phase_active

            if error < -correction_threshold:
                new_state = SUP_CORRECTING
                dT_neg_count = 0
            elif abs(error) > monitor_band and sup_dwell >= MIN_STATE_DWELL:
                new_state = SUP_TRACKING
            elif check_triggered and sup_dwell >= MIN_STATE_DWELL:
                if null_mode:
                    pass  # null: no separate CHECKING state
                else:
                    new_state = SUP_CHECKING
                    check_remaining = CHECK_DWELL

            if null_mode:
                Q_lo, Q_hi = 0.0, Q_monitor_max
            else:
                Q_lo, Q_hi = 0.0, Q_monitor_max

        elif sup_state == SUP_CHECKING:
            check_remaining -= 1
            if error < -correction_threshold:
                new_state = SUP_CORRECTING
                dT_neg_count = 0
            elif check_remaining <= 0:
                if abs(error) < monitor_band:
                    new_state = SUP_MONITORING
                else:
                    new_state = SUP_TRACKING

            # Q frozen at prev_Q during check
            Q_lo, Q_hi = max(0.0, prev_Q - 0.001), min(Q_MAX, prev_Q + 0.001)

        elif sup_state == SUP_CORRECTING:
            # Track dT sign for CLOSING transition
            if dT_current < 0:
                dT_neg_count += 1
            else:
                dT_neg_count = 0

            if dT_neg_count >= close_dwell_param and sup_dwell >= MIN_STATE_DWELL:
                new_state = SUP_CLOSING
            elif error > 0 and sup_dwell >= MIN_STATE_DWELL:
                # Brief zero-crossing, not real cycle end
                new_state = SUP_TRACKING if not null_mode else SUP_QUALIFYING

            if null_mode:
                Q_lo, Q_hi = 0.0, Q_monitor_max  # null: moderate Q allowed
            else:
                Q_lo, Q_hi = 0.0, Q_CORRECT  # hard gate: no heating

        elif sup_state == SUP_CLOSING:
            if error > 0 and sup_dwell >= MIN_STATE_DWELL:
                new_state = SUP_QUALIFYING
                stab_confirm = 0
            elif null_mode and error > 0:
                # null: can return to TRACKING (no commitment latch)
                new_state = SUP_TRACKING

            Q_lo, Q_hi = 0.0, Q_CORRECT  # no heating in closing

        # State transition
        if new_state != sup_state:
            sup_state = new_state
            sup_dwell = 0

        # ---- MPC INNER LOOP (vectorized over candidates) ----
        if Q_hi <= Q_lo + 1e-6:
            # Constrained to single value (CHECKING or Q_CORRECT=0)
            Q = max(0.0, min(Q_MAX, Q_lo + rng.normal(0, SIGMA_Q * 0.1)))
        else:
            # Vectorized: evaluate all candidates simultaneously
            step_q = (Q_hi - Q_lo) / max(N_CANDIDATES - 1, 1)
            for ci in range(N_CANDIDATES):
                _mpc_Q[ci] = Q_lo + ci * step_q
            _mpc_T[:] = T_observed
            _mpc_phi[:] = phi
            _mpc_cost[:] = 0.0
            Q_candidates = _mpc_Q
            T_pred = _mpc_T
            phi_pred = _mpc_phi
            total_cost = _mpc_cost

            for k in range(horizon):
                V_p = alpha * np.maximum(0.0, 1.0 - phi_pred) * np.maximum(0.0, T_pred - T_boil)
                C_p = beta * phi_pred * C_EFF
                dT_p = DT * (Q_candidates - LAMBDA * V_p + LAMBDA * C_p
                             - K_LOSS * (T_pred - T_ENV)) / M
                T_pred += dT_p
                dphi_p = DT * (V_p - C_p - GAMMA * phi_pred)
                phi_pred = np.clip(phi_pred + dphi_p, 0.0, 1.0)

                err = T_target - T_pred
                total_cost += error_weight * err * err
                overshoot = np.maximum(0.0, T_pred - T_target)
                total_cost += safety_weight * overshoot * overshoot

            total_cost += effort_weight * Q_candidates * Q_candidates
            total_cost += rate_weight * (Q_candidates - prev_Q) ** 2

            best_Q = Q_candidates[np.argmin(total_cost)]
            Q = max(0.0, min(Q_MAX, best_Q + rng.normal(0, SIGMA_Q)))

        # ---- PLANT ODE ----
        T_history.pop(0)
        T_history.append(T)

        V = alpha * max(0.0, 1.0 - phi) * max(0.0, T - T_boil)
        C_cond = beta * phi * C_EFF

        dT_phys = DT * (Q - LAMBDA * V + LAMBDA * C_cond
                        - K_LOSS * (T - T_ENV)) / M
        T_new = T + dT_phys + rng.normal(0, SIGMA_T)

        dphi_val = DT * (V - C_cond - GAMMA * phi)
        phi_new = max(0.0, min(1.0, phi + dphi_val))

        # Store
        T_arr[step] = T
        phi_arr[step] = phi
        dT_arr[step] = T_new - prev_T
        dphi_arr[step] = phi_new - phi
        Q_arr[step] = Q
        dQ_arr[step] = Q - prev_Q
        error_arr[step] = T_target - T
        sup_state_arr[step] = sup_state

        prev_dphi = dphi_val
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
        'eq_scale': eq_scale,
        'sup_state': sup_state_arr[sl],
    }


# ============================================================
# CYCLE SEGMENTATION — full trough-to-trough (same as Phase 556)
# ============================================================

def segment_full_cycles(T_arr):
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
# LEVEL A: PRIMITIVE ACTION EXTRACTION (same as Phase 556)
# ============================================================

def extract_primitives(run_data, op_params):
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

    dQ_sign = np.sign(dQ)
    dQ_mag = np.abs(dQ) / max(Q_MAX, 1e-6)
    error_sign = np.zeros(n)
    error_sign[error > dead_zone] = 1.0
    error_sign[error < -dead_zone] = -1.0
    error_mag = np.abs(error) / max(eq_scale, 1e-6)

    stability = np.zeros(n)
    for i in range(stab_win, n):
        stability[i] = np.std(T[i-stab_win:i])

    phase_activity = np.zeros(n)
    for i in range(stab_win, n):
        phase_activity[i] = np.mean(np.abs(dphi[i-stab_win:i]))

    hold_duration = np.zeros(n)
    last_change = 0
    for i in range(n):
        if np.abs(dQ[i]) > dQ_thresh:
            last_change = i
        hold_duration[i] = i - last_change

    check_event = np.zeros(n, dtype=bool)
    stab_range = max(stability.max() - stability.min(), 1e-6)
    stab_trigger = op_params['stability_trigger_frac'] * stab_range + stability.min()

    prev_in_band = abs(error[0]) <= check_error_band
    last_check = -check_holdoff

    for i in range(1, n):
        triggered = False
        if hold_duration[i] >= check_holdoff and (i - last_check) >= check_holdoff:
            triggered = True
        if i > 0 and ((stability[i] > stab_trigger) != (stability[i-1] > stab_trigger)):
            triggered = True
        in_band = abs(error[i]) <= check_error_band
        if prev_in_band and not in_band:
            triggered = True
        prev_in_band = in_band
        if i > 0 and phase_activity[i] > 0 and phase_activity[i-1] == 0:
            triggered = True
        if triggered and (i - last_check) >= 2:
            check_event[i] = True
            last_check = i

    action_type = np.full(n, ACT_HOLD_AT)
    for i in range(n):
        if check_event[i]:
            action_type[i] = ACT_CHECK
        elif abs(dQ[i]) > dQ_thresh:
            if dQ[i] > 0:
                if error_sign[i] >= 0:
                    action_type[i] = ACT_INCREASE_BELOW
                else:
                    action_type[i] = ACT_INCREASE_ABOVE
            else:
                if error_sign[i] <= 0:
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

    # Raw primitive profiles per quintile
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

    # Observation vs intervention
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
    bigrams_norm = bigrams / total_trans if total_trans > 0 else bigrams

    # Supervisor state distribution per quintile
    sup_state = run_data['sup_state'][sl]
    sup_quintile_dist = np.zeros((N_QUINTILES, N_SUP_STATES))
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            for s in range(N_SUP_STATES):
                sup_quintile_dist[q, s] = np.sum(sup_state[mask] == s) / mask.sum()

    # Check event log (for H3): find CHECKING episodes from supervisor state
    check_events_log = []
    in_check = False
    check_start_pos = 0
    for i in range(n):
        if sup_state[i] == SUP_CHECKING and not in_check:
            in_check = True
            check_start_pos = i
        elif sup_state[i] != SUP_CHECKING and in_check:
            in_check = False
            duration = i - check_start_pos
            position = (check_start_pos + i) / 2 / n
            post_state = int(sup_state[i])
            check_events_log.append((position, duration, post_state))

    # First TRACKING onset (for sanity diagnostic)
    first_tracking_pos = -1.0
    for i in range(n):
        if sup_state[i] == SUP_TRACKING:
            first_tracking_pos = positions[i]
            break

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
        # NEW for Phase 557
        'sup_quintile_dist': sup_quintile_dist.tolist(),
        'check_events_log': check_events_log,
        'first_tracking_pos': first_tracking_pos,
        'n_sup_checks': len(check_events_log),
        'post_check_states': [e[2] for e in check_events_log],
    }


# ============================================================
# LEVEL B: INFERRED LATENT STRUCTURE (same as Phase 556)
# ============================================================

def infer_hmm_states(primitives, n_states_range=(2, 7)):
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


def extract_hmm_cycle_features(hmm_result, cycle_start, cycle_end, n_total):
    if hmm_result is None:
        return None

    labels = hmm_result['labels'][cycle_start:cycle_end]
    k = hmm_result['k']
    n = len(labels)
    if n < MIN_CYCLE:
        return None

    positions = np.linspace(0, 1, n, endpoint=False)
    quintiles = np.minimum((positions * N_QUINTILES).astype(int), N_QUINTILES - 1)

    quintile_states = np.zeros((N_QUINTILES, k))
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            for s in range(k):
                quintile_states[q, s] = np.sum(labels[mask] == s) / mask.sum()

    same_count = sum(1 for i in range(len(labels)-1) if labels[i] == labels[i+1])
    persistence = same_count / max(len(labels) - 1, 1)
    interleaving = 1.0 - persistence

    runs = []
    cur = labels[0]
    for l in labels[1:]:
        if l != cur:
            runs.append(cur)
            cur = l
    runs.append(cur)
    non_contiguous = len(runs) >= 3

    # Hierarchical macro-bundle (for H2: collapse k states into 2 macro-bundles)
    if k > 2:
        try:
            from scipy.cluster.hierarchy import linkage, fcluster
            centroids = np.array(hmm_result['centroids'])
            Z = linkage(centroids, method='ward')
            bundle_labels = fcluster(Z, t=2, criterion='maxclust') - 1
            macro_labels = np.array([bundle_labels[l] for l in labels])

            macro_same = sum(1 for i in range(len(macro_labels)-1)
                            if macro_labels[i] == macro_labels[i+1])
            macro_persistence = macro_same / max(len(macro_labels) - 1, 1)
            macro_interleaving = 1.0 - macro_persistence

            macro_runs = []
            mcur = macro_labels[0]
            for ml in macro_labels[1:]:
                if ml != mcur:
                    macro_runs.append(mcur)
                    mcur = ml
            macro_runs.append(mcur)
            macro_non_contiguous = len(macro_runs) >= 3
        except Exception:
            macro_persistence = persistence
            macro_interleaving = interleaving
            macro_non_contiguous = non_contiguous
    else:
        macro_persistence = persistence
        macro_interleaving = interleaving
        macro_non_contiguous = non_contiguous

    return {
        'quintile_states': quintile_states.tolist(),
        'persistence': float(persistence),
        'interleaving': float(interleaving),
        'non_contiguous': bool(non_contiguous),
        'n_switches': int(len(runs) - 1),
        'k': k,
        'macro_persistence': float(macro_persistence),
        'macro_interleaving': float(macro_interleaving),
        'macro_non_contiguous': bool(macro_non_contiguous),
    }


# ============================================================
# APPARATUS FAMILY CLASSIFICATION (same as Phase 556)
# ============================================================

def classify_apparatus_families(run_summaries):
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

    centroids = km.cluster_centers_
    order = np.argsort(centroids[:, 0])
    label_map = {old: new for new, old in enumerate(order)}
    labels = np.array([label_map[l] for l in labels])
    family_names = ['SLOW_SUSTAINED', 'MODERATE', 'FAST_AGGRESSIVE']

    return labels, family_names


# ============================================================
# RUN SWEEP — shared by full and null supervisor
# ============================================================

def run_sweep(system_params, operator_params, rng, null_mode,
              n_runs_per, hmm_sample_rate, label):
    """Run a full parameter sweep. Returns (all_cycles, run_summaries, hmm_bic_ks)."""
    all_cycles = []
    run_summaries = []
    hmm_bic_ks = []
    total_cycles = 0

    n_sys = len(system_params)
    n_op = len(operator_params)
    n_total_runs = n_sys * n_op * n_runs_per
    run_count = 0

    # Track first TRACKING onset quintiles for sanity diagnostic
    first_tracking_quintiles = []

    for si, sp in enumerate(system_params):
        for oi, op in enumerate(operator_params):
            for ri in range(n_runs_per):
                run_count += 1
                if run_count % 500 == 0:
                    print(f"  [{label}] Run {run_count}/{n_total_runs}: "
                          f"cycles={total_cycles}", flush=True)

                run_data = simulate_run(sp, op, rng, null_mode=null_mode)
                primitives = extract_primitives(run_data, op)
                cycles = segment_full_cycles(run_data['T'])

                # Level B inference (sampled)
                hmm_result = None
                if run_count % hmm_sample_rate == 0:
                    hmm_result = infer_hmm_states(primitives)
                    if hmm_result is not None:
                        hmm_bic_ks.append(hmm_result['k'])

                # Per-run summary
                run_corr_rate = 0
                run_overshoots = []
                run_cycle_lengths = []

                for cs, ce in cycles:
                    cf = extract_cycle_features(cs, ce, primitives, run_data)
                    if cf is None:
                        continue

                    hmm_cf = extract_hmm_cycle_features(
                        hmm_result, cs, ce, len(run_data['T']))

                    cycle_record = {
                        'sys_param_idx': si,
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

                    if cf['first_tracking_pos'] >= 0:
                        ftp_q = min(int(cf['first_tracking_pos'] * N_QUINTILES),
                                    N_QUINTILES - 1)
                        first_tracking_quintiles.append(ftp_q)

                if run_cycle_lengths:
                    run_summaries.append({
                        'sys_param_idx': si,
                        'mean_overshoot': float(np.mean(run_overshoots)),
                        'mean_cycle_length': float(np.mean(run_cycle_lengths)),
                        'correction_rate': float(run_corr_rate / len(run_cycle_lengths)),
                        'stability_variance': float(np.var(run_overshoots))
                            if len(run_overshoots) > 1 else 0.0,
                    })

    print(f"  [{label}] Complete: {total_cycles} cycles from {run_count} runs",
          flush=True)

    # First TRACKING onset diagnostic
    ft_dist = [0] * N_QUINTILES
    for q in first_tracking_quintiles:
        ft_dist[q] += 1
    total_ft = sum(ft_dist)
    if total_ft > 0:
        ft_dist_frac = [c / total_ft for c in ft_dist]
    else:
        ft_dist_frac = [0.0] * N_QUINTILES

    return all_cycles, run_summaries, hmm_bic_ks, ft_dist_frac


def pack_cycles_npz(all_cycles, path, n_sys_params):
    """Pack cycle records into compressed numpy arrays."""
    n_cyc = len(all_cycles)
    print(f"Packing {n_cyc} cycles into numpy arrays...")

    qa_arr = np.zeros((n_cyc, N_QUINTILES, N_ACTION_TYPES), dtype=np.float32)
    bigrams_arr = np.zeros((n_cyc, N_ACTION_TYPES, N_ACTION_TYPES), dtype=np.float32)
    positions_arr = np.zeros((n_cyc, N_ACTION_TYPES), dtype=np.float32)
    counts_arr = np.zeros((n_cyc, N_ACTION_TYPES), dtype=np.int32)
    meta_arr = np.zeros((n_cyc, 6), dtype=np.float32)
    param_arr = np.zeros((n_cyc, 3), dtype=np.int32)
    qr_stability = np.zeros((n_cyc, N_QUINTILES), dtype=np.float32)
    qr_phase_activity = np.zeros((n_cyc, N_QUINTILES), dtype=np.float32)

    # HMM features (sparse)
    hmm_interleaving = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_persistence = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_non_contiguous = np.zeros(n_cyc, dtype=np.int8)
    hmm_k = np.zeros(n_cyc, dtype=np.int8)
    hmm_macro_interleaving = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_macro_persistence = np.full(n_cyc, -1.0, dtype=np.float32)
    hmm_macro_non_contiguous = np.zeros(n_cyc, dtype=np.int8)

    # NEW: Supervisor state quintile distribution
    sup_quintile_arr = np.zeros((n_cyc, N_QUINTILES, N_SUP_STATES), dtype=np.float32)

    # NEW: Check event summary (n_checks, mean_pos, mean_dur, n_post_states)
    check_summary = np.zeros((n_cyc, 4), dtype=np.float32)

    for i, c in enumerate(all_cycles):
        qa_arr[i] = np.array(c['quintile_actions'], dtype=np.float32)
        bigrams_arr[i] = np.array(c['bigrams'], dtype=np.float32)
        for a in range(N_ACTION_TYPES):
            positions_arr[i, a] = c['mean_positions'][ACTION_NAMES[a]]
        counts_arr[i] = np.array(c['action_counts'], dtype=np.int32)
        meta_arr[i] = [c['length'], c['max_overshoot'],
                       c['obs_mean_pos'], c['int_mean_pos'],
                       c['passive_mean_pos'], c['active_mean_pos']]
        param_arr[i] = [c['sys_param_idx'], c['operator_param_idx'], c['run_idx']]

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
            hmm_macro_interleaving[i] = c['hmm']['macro_interleaving']
            hmm_macro_persistence[i] = c['hmm']['macro_persistence']
            hmm_macro_non_contiguous[i] = 1 if c['hmm']['macro_non_contiguous'] else 0

        if 'sup_quintile_dist' in c:
            sup_quintile_arr[i] = np.array(c['sup_quintile_dist'], dtype=np.float32)

        check_log = c.get('check_events_log', [])
        if check_log:
            check_summary[i, 0] = len(check_log)
            check_summary[i, 1] = float(np.mean([e[0] for e in check_log]))
            check_summary[i, 2] = float(np.mean([e[1] for e in check_log]))
            check_summary[i, 3] = len(set(e[2] for e in check_log))

    np.savez_compressed(path,
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
                        hmm_k=hmm_k,
                        hmm_macro_interleaving=hmm_macro_interleaving,
                        hmm_macro_persistence=hmm_macro_persistence,
                        hmm_macro_non_contiguous=hmm_macro_non_contiguous,
                        supervisor_states=sup_quintile_arr,
                        check_summary=check_summary)
    print(f"NPZ: {path} ({path.stat().st_size / 1e6:.1f} MB)")


# ============================================================
# MAIN
# ============================================================

def main():
    rng = np.random.default_rng(42)

    print("=" * 70)
    print("Phase 557: PREDICTIVE_SUPERVISORY_CONTROL_ALIGNMENT")
    print("MPC inner loop + 6-state supervisor + null baseline")
    print("=" * 70)

    # Generate LHS samples
    print("\nGenerating LHS samples...")
    system_params = latin_hypercube_sample(N_PARAM_SETS, SYSTEM_RANGES, rng)
    operator_params = latin_hypercube_sample(N_OPERATOR_PARAMS, OPERATOR_RANGES, rng)

    # ---- FULL SUPERVISOR RUN ----
    print(f"\n{'='*50}")
    print(f"FULL SUPERVISOR: {N_PARAM_SETS} system × {N_OPERATOR_PARAMS} op × {N_RUNS_PER} runs")
    print(f"{'='*50}")

    full_cycles, full_run_summaries, full_hmm_ks, ft_dist = run_sweep(
        system_params, operator_params, rng,
        null_mode=False, n_runs_per=N_RUNS_PER,
        hmm_sample_rate=HMM_SAMPLE_RATE, label="FULL")

    # Apparatus classification (on full runs)
    n_sys = len(system_params)
    plant_summaries = []
    for si in range(n_sys):
        runs = [s for s in full_run_summaries if s['sys_param_idx'] == si]
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

    # Print full supervisor summary
    total_cycles = len(full_cycles)
    cycle_lengths = [c['length'] for c in full_cycles]
    action_totals = np.zeros(N_ACTION_TYPES)
    for c in full_cycles:
        for a in range(N_ACTION_TYPES):
            action_totals[a] += c['action_counts'][a]

    # Supervisor state totals
    sup_totals = np.zeros(N_SUP_STATES)
    for c in full_cycles:
        sd = np.array(c['sup_quintile_dist'])
        for s in range(N_SUP_STATES):
            sup_totals[s] += sd[:, s].mean()

    hmm_k_counts = {}
    for k in full_hmm_ks:
        hmm_k_counts[k] = hmm_k_counts.get(k, 0) + 1

    print(f"\n{'='*60}")
    print(f"FULL SUPERVISOR RESULTS")
    print(f"{'='*60}")
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

    print(f"\nSUPERVISOR STATE FRACTIONS (mean across cycles):")
    sup_total = sup_totals.sum()
    for s in range(N_SUP_STATES):
        pct = 100 * sup_totals[s] / max(sup_total, 1)
        print(f"  {SUP_NAMES[s]:<20s} {pct:.1f}%")

    print(f"\nFIRST TRACKING ONSET BY QUINTILE (sanity diagnostic):")
    for q in range(N_QUINTILES):
        print(f"  Q{q}: {ft_dist[q]*100:.1f}%")

    print(f"\nHMM BIC-SELECTED STATE COUNTS:")
    for k in sorted(hmm_k_counts.keys()):
        print(f"  k={k}: {hmm_k_counts[k]} runs")

    print(f"\nAPPARATUS FAMILIES:")
    for fi, fname in enumerate(family_names):
        count = sum(1 for l in family_labels if l == fi)
        print(f"  {fname}: {count} parameterizations")

    # Save full supervisor NPZ
    pack_cycles_npz(full_cycles,
                    RESULTS_DIR / 't1_cycles.npz', n_sys)

    # ---- NULL SUPERVISOR RUN ----
    print(f"\n{'='*50}")
    print(f"NULL SUPERVISOR: {N_NULL_PARAM_SETS} system × {N_OPERATOR_PARAMS} op × {N_NULL_RUNS_PER} runs")
    print(f"{'='*50}")

    null_system_params = latin_hypercube_sample(N_NULL_PARAM_SETS, SYSTEM_RANGES, rng)

    null_cycles, null_run_summaries, null_hmm_ks, null_ft_dist = run_sweep(
        null_system_params, operator_params, rng,
        null_mode=True, n_runs_per=N_NULL_RUNS_PER,
        hmm_sample_rate=HMM_SAMPLE_RATE, label="NULL")

    null_total = len(null_cycles)
    print(f"\nNull supervisor cycles: {null_total}")

    # Save null supervisor NPZ
    pack_cycles_npz(null_cycles,
                    RESULTS_DIR / 't1_null_cycles.npz', N_NULL_PARAM_SETS)

    # ---- SUMMARY JSON ----
    agg_quintile_actions = np.zeros((N_QUINTILES, N_ACTION_TYPES))
    for c in full_cycles:
        agg_quintile_actions += np.array(c['quintile_actions'])
    if total_cycles > 0:
        agg_quintile_actions /= total_cycles

    summary = {
        'phase': 'Phase 557: PREDICTIVE_SUPERVISORY_CONTROL_ALIGNMENT',
        'controller': 'MPC (15 candidates, asymmetric safety) + 6-state supervisor',
        'n_system_params': N_PARAM_SETS,
        'n_operator_params': N_OPERATOR_PARAMS,
        'n_runs_per': N_RUNS_PER,
        'total_runs': N_PARAM_SETS * N_OPERATOR_PARAMS * N_RUNS_PER,
        'total_cycles': total_cycles,
        'cycle_length_mean': float(np.mean(cycle_lengths)) if cycle_lengths else 0,
        'cycle_length_median': float(np.median(cycle_lengths)) if cycle_lengths else 0,
        'action_totals': {ACTION_NAMES[a]: int(action_totals[a])
                          for a in range(N_ACTION_TYPES)},
        'aggregate_quintile_actions': agg_quintile_actions.tolist(),
        'supervisor_state_fractions': {
            SUP_NAMES[s]: float(sup_totals[s] / max(sup_total, 1))
            for s in range(N_SUP_STATES)
        },
        'first_tracking_onset_quintile_dist': ft_dist,
        'hmm_bic_k_distribution': hmm_k_counts,
        'apparatus_families': {
            'names': family_names,
            'plant_assignments': family_labels.tolist(),
        },
        'null_supervisor': {
            'n_system_params': N_NULL_PARAM_SETS,
            'n_runs_per': N_NULL_RUNS_PER,
            'total_cycles': null_total,
            'first_tracking_onset_quintile_dist': null_ft_dist,
        },
        'non_circularity': {
            'voynich_input': 'NONE — zero Voynich-derived values in T1',
            'controller': 'MPC from standard optimal control theory',
            'supervisor': '6-state FSM from plant state algebra '
                          '(error regime × stability × check trigger × correction phase)',
            'null_supervisor': 'Same states, degraded constraints (standard ablation)',
            'event_types': 'From controller state algebra (dQ × error sign)',
            'check_triggers': 'Endogenous: hold_duration, stability, error_band, phase_activity',
            'hmm': 'Unsupervised: BIC-selected state count on raw primitives',
        },
        'design_note': (
            'Two-layer controller: MPC (inner, continuous optimization) + '
            'supervisor (outer, discrete state gating). Full trough-to-trough '
            'cycles. Physics is symmetric. Operator asymmetry is genuine. '
            'Null supervisor tests structural necessity of gates.'
        ),
    }

    summary_path = RESULTS_DIR / 't1_operator_events.json'
    print(f"\nWriting summary to {summary_path}...")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary size: {summary_path.stat().st_size / 1e3:.1f} KB")

    print(f"\nDone.")


if __name__ == '__main__':
    main()
