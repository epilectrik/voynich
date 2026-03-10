"""
T1: Physical Process with Operator Event Extraction (REDESIGNED)
================================================================
Phase: VOYNICH_CONTROL_ARCHITECTURE_PHYSICAL_ALIGNMENT

Redesign rationale:
  The Voynich grammar describes OPERATOR CONTROL SCHEDULING, not raw physics.
  Phase 555v1 tested raw physical risk against Voynich zones — wrong layer.

  This version extracts OPERATOR ACTIONS from the P-controller trace:
    - PROACTIVE: operator heating toward target (planned, safe)
    - REACTIVE: operator correcting overshoot (unplanned, dangerous)
    - NEUTRAL: operator near setpoint, minimal action (stable work)

  These map to the Voynich hazard classes:
    - PROACTIVE → ZERO (safe/setup)
    - NEUTRAL → IMMUNE (controlled work)
    - REACTIVE → HIGH (containment/correction)

  The Voynich predicts: PROACTIVE concentrates at Q0, NEUTRAL at Q1-Q3,
  REACTIVE at Q4. This is the operator-scheduling prediction, not a
  raw-risk prediction.

Technical fixes from v1:
  - DT=0.02 (was 0.1): 5x finer temporal resolution
  - DELAY=15 (was 3): same physical delay (0.3 time units)
  - N_STEPS=1500: longer runs
  - Stores per-cycle aggregates, not per-timestep (manageable file size)

Non-circularity: ALL labels from control theory. ZERO Voynich-derived values.

Output: t1_physical_process.json
"""

import json
import numpy as np
from pathlib import Path
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# PHYSICAL CONSTANTS — same C998 ODE, adjusted timestep
# ============================================================
DT = 0.02          # 5x finer than C998 (was 0.1)
N_STEPS = 1500     # longer runs
BURN_IN = 300      # discard initial transient
LAMBDA = 5.0
GAMMA = 0.05
C_EFF = 0.8
K_LOSS = 0.3
Q_MAX = 1.5
T_ENV = 0.0
DELAY = 15         # same physical delay: 15 * 0.02 = 0.3 time units (was 3 * 0.1)
TARGET_FRAC = 0.05

# Noise (scaled for smaller DT)
SIGMA_Q = 0.08
SIGMA_T = 0.01 * np.sqrt(DT / 0.1)   # scale thermal noise with sqrt(dt)
SIGMA_BOIL = 0.02

# LHS sweep — same as C998
N_PARAM_SETS = 100
N_RUNS_PER = 10

PARAM_RANGES = {
    'T_boil':    (0.80, 1.20),
    'M':         (0.50, 2.00),
    'alpha':     (1.00, 3.00),
    'beta':      (0.50, 2.00),
    'K_p':       (1.00, 5.00),
    'bias_frac': (0.90, 1.30),
}

N_QUINTILES = 5
N_FINE_BINS = 20

# Operator action thresholds (from control theory, NOT Voynich)
NEUTRAL_ERROR_FRAC = 0.3  # |error| < 30% of eq_scale → NEUTRAL


# ============================================================
# SIMULATION CORE — C998 ODE with finer timestep
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
    """Simulate one run. Returns arrays for efficient computation."""
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

    # Pre-allocate arrays
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

    # Discard burn-in
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
# CYCLE SEGMENTATION
# ============================================================

def segment_into_cycles(run_data):
    """Segment run into ASCENDING half-cycles (trough → peak).

    Rationale (v3b):
      Full trough-to-trough cycles give symmetric overshoot risk (inverted-U).
      The Voynich predicts monotonically increasing danger (Q0=safe → Q4=dangerous).

      A Voynich "line" maps to the ASCENDING HALF of the oscillation:
        Q0 = T_min (trough: cold, safe, below target)
        Q4 = T_max (peak: hot, dangerous, overshoot)

      Overshoot risk increases monotonically from trough to peak,
      matching the Voynich zone-hazard enrichment pattern.

      The descending half (peak → trough) is a separate control phase,
      potentially mapping to Mode B (passive cooling/monitoring).
    """
    T = run_data['T']
    n = len(T)
    MIN_HALF = 4  # minimum 4 steps per half-cycle

    if n < 20:
        return []

    # Smooth T to avoid noise-induced false extrema
    window = 5
    kernel = np.ones(window) / window
    T_smooth = np.convolve(T, kernel, mode='same')

    # Find local minima (troughs) and maxima (peaks)
    troughs = []
    peaks = []
    for i in range(2, n - 2):
        if (T_smooth[i] <= T_smooth[i-1] and T_smooth[i] <= T_smooth[i-2] and
                T_smooth[i] <= T_smooth[i+1] and T_smooth[i] <= T_smooth[i+2]):
            troughs.append(i)
        if (T_smooth[i] >= T_smooth[i-1] and T_smooth[i] >= T_smooth[i-2] and
                T_smooth[i] >= T_smooth[i+1] and T_smooth[i] >= T_smooth[i+2]):
            peaks.append(i)

    if len(troughs) < 1 or len(peaks) < 1:
        return []

    # Build ascending half-cycles: each trough → next peak
    cycles = []
    peak_idx = 0
    for t in troughs:
        # Advance peak_idx to find next peak after this trough
        while peak_idx < len(peaks) and peaks[peak_idx] <= t:
            peak_idx += 1
        if peak_idx >= len(peaks):
            break
        p = peaks[peak_idx]
        length = p - t
        if length >= MIN_HALF:
            cycles.append((t, p))

    return cycles


# ============================================================
# OPERATOR ACTION CLASSIFICATION
# ============================================================

def classify_operator_actions(run_data):
    """Classify each timestep into operator action types.

    Types (from control variables, NOT Voynich):
      PROACTIVE: error > 0 (T below target, operator heating toward goal)
      REACTIVE:  error < 0 (T above target, operator correcting overshoot)
      NEUTRAL:   |error| < eq_scale * NEUTRAL_ERROR_FRAC (near setpoint)

    Also computes:
      operator_load: |dQ| (intervention intensity)
      operator_stress: |error| * |dQ| (deviation × intervention)
      intervention_type: PLANNED_HEAT / CORRECT_REDUCE / MAINTAIN / PASSIVE
    """
    error = run_data['error']
    dQ = run_data['dQ']
    Q = run_data['Q']
    Q_bias = run_data['Q_bias']
    eq_scale = run_data['eq_scale']
    n = len(error)

    neutral_threshold = eq_scale * NEUTRAL_ERROR_FRAC

    # Primary classification: PROACTIVE / REACTIVE / NEUTRAL
    action_type = np.zeros(n, dtype=int)  # 0=PROACTIVE, 1=NEUTRAL, 2=REACTIVE
    for i in range(n):
        if abs(error[i]) < neutral_threshold:
            action_type[i] = 1  # NEUTRAL
        elif error[i] > 0:
            action_type[i] = 0  # PROACTIVE
        else:
            action_type[i] = 2  # REACTIVE

    # Operator load and stress
    operator_load = np.abs(dQ)
    operator_stress = np.abs(error) * np.abs(dQ)

    # Intervention subtype
    # PLANNED_HEAT: proactive + Q > Q_bias (actively adding heat to reach target)
    # CORRECT_REDUCE: reactive + Q < Q_bias (reducing heat to correct overshoot)
    # MAINTAIN: neutral + |dQ| small (steady state maintenance)
    # ACTIVE_CHECK: neutral + |dQ| large (adjusting near setpoint)
    dQ_abs = np.abs(dQ)
    dQ_p50 = np.percentile(dQ_abs, 50) if n > 5 else 0.01

    intervention_sub = np.zeros(n, dtype=int)
    # 0=PLANNED_HEAT, 1=CORRECT_REDUCE, 2=MAINTAIN, 3=ACTIVE_CHECK
    for i in range(n):
        if action_type[i] == 0:  # PROACTIVE
            intervention_sub[i] = 0  # PLANNED_HEAT
        elif action_type[i] == 2:  # REACTIVE
            intervention_sub[i] = 1  # CORRECT_REDUCE
        elif dQ_abs[i] > dQ_p50:
            intervention_sub[i] = 3  # ACTIVE_CHECK
        else:
            intervention_sub[i] = 2  # MAINTAIN

    return {
        'action_type': action_type,
        'operator_load': operator_load,
        'operator_stress': operator_stress,
        'intervention_sub': intervention_sub,
    }


# ============================================================
# PER-CYCLE FEATURE EXTRACTION
# ============================================================

def extract_cycle_features(run_data, ops, cycle_bounds):
    """Extract per-cycle aggregate features."""
    start, end = cycle_bounds
    n = end - start

    # Slices
    T = run_data['T'][start:end]
    Q = run_data['Q'][start:end]
    dT = run_data['dT'][start:end]
    dphi = run_data['dphi'][start:end]
    phi = run_data['phi'][start:end]
    dQ = run_data['dQ'][start:end]
    error = run_data['error'][start:end]
    T_target = run_data['T_target']
    action = ops['action_type'][start:end]
    load = ops['operator_load'][start:end]
    stress = ops['operator_stress'][start:end]
    interv = ops['intervention_sub'][start:end]

    # Quintile assignment
    quintiles = np.array([min(int((i / n) * N_QUINTILES), N_QUINTILES - 1) for i in range(n)])
    fine_bins = np.array([min(int((i / n) * N_FINE_BINS), N_FINE_BINS - 1) for i in range(n)])

    # --- Quintile profiles ---

    # Operator action type distribution per quintile
    # action_type: 0=PROACTIVE, 1=NEUTRAL, 2=REACTIVE
    action_names = ['PROACTIVE', 'NEUTRAL', 'REACTIVE']
    quintile_action_dist = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        n_q = mask.sum()
        if n_q > 0:
            dist = {}
            for ai, aname in enumerate(action_names):
                dist[aname] = float((action[mask] == ai).sum() / n_q)
            quintile_action_dist[f'Q{q}'] = dist
        else:
            quintile_action_dist[f'Q{q}'] = {a: 0.333 for a in action_names}

    # Operator load per quintile
    quintile_load = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_load[f'Q{q}'] = float(np.mean(load[mask]))
        else:
            quintile_load[f'Q{q}'] = 0.0

    # Operator stress per quintile
    quintile_stress = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_stress[f'Q{q}'] = float(np.mean(stress[mask]))
        else:
            quintile_stress[f'Q{q}'] = 0.0

    # Risk per quintile (physical risk: |dT| + |dphi| + |error|, normalized)
    dT_abs = np.abs(dT)
    dphi_abs = np.abs(dphi)
    err_abs = np.abs(error)

    def norm01(arr):
        mn, mx = arr.min(), arr.max()
        return (arr - mn) / (mx - mn) if mx - mn > 1e-12 else np.zeros_like(arr)

    risk = (norm01(dT_abs) + norm01(dphi_abs) + norm01(err_abs)) / 3.0

    quintile_risk = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_risk[f'Q{q}'] = float(np.mean(risk[mask]))
        else:
            quintile_risk[f'Q{q}'] = 0.0

    # Asymmetric risk: overshoot danger (physically correct for distillation)
    # Overheating is dangerous (thermal runaway, uncontrolled vaporization)
    # Underheating is safe (just slow)
    overshoot = np.maximum(0, T - T_target)

    quintile_overshoot = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_overshoot[f'Q{q}'] = float(np.mean(overshoot[mask]))
        else:
            quintile_overshoot[f'Q{q}'] = 0.0

    # Cumulative overshoot: running integral of thermal excess within cycle
    cum_overshoot = np.cumsum(overshoot)
    quintile_cum_overshoot = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        if mask.sum() > 0:
            quintile_cum_overshoot[f'Q{q}'] = float(np.mean(cum_overshoot[mask]))
        else:
            quintile_cum_overshoot[f'Q{q}'] = 0.0

    # Fine-bin profiles
    fine_action_dist = {}
    fine_load = {}
    fine_risk = {}
    for b in range(N_FINE_BINS):
        mask = fine_bins == b
        if mask.sum() > 0:
            dist = {}
            for ai, aname in enumerate(action_names):
                dist[aname] = float((action[mask] == ai).sum() / mask.sum())
            fine_action_dist[f'B{b}'] = dist
            fine_load[f'B{b}'] = float(np.mean(load[mask]))
            fine_risk[f'B{b}'] = float(np.mean(risk[mask]))

    # --- Operator behavior features (for H2 mode decomposition) ---
    dQ_abs = np.abs(dQ)
    dQ_p75 = np.percentile(dQ_abs, 75) if n > 3 else 0.01
    dT_med = np.median(dT_abs) if n > 3 else 0.01
    dQ_med = np.median(dQ_abs) if n > 3 else 0.01

    intervention_density = float(np.mean(dQ_abs > dQ_p75))
    passive_frac = float(np.mean((dT_abs < dT_med) & (dQ_abs < dQ_med)))
    active_frac = float(np.mean(dQ_abs > dQ_p75))
    proactive_frac = float(np.mean(action == 0))
    reactive_frac = float(np.mean(action == 2))
    neutral_frac = float(np.mean(action == 1))

    # Passive vs active mean positions (for H3)
    passive_positions = []
    active_positions = []
    for i in range(n):
        pos = i / n
        if dQ_abs[i] < dQ_med and dT_abs[i] < dT_med:
            passive_positions.append(pos)
        if dQ_abs[i] > dQ_p75:
            active_positions.append(pos)

    mean_passive_pos = float(np.mean(passive_positions)) if passive_positions else 0.5
    mean_active_pos = float(np.mean(active_positions)) if active_positions else 0.5

    # Thermal state (for H4)
    is_hot = T > run_data['T_boil']
    is_stable = dT_abs < np.median(dT_abs) if n > 3 else np.ones(n, dtype=bool)
    hot_stable_frac = float(np.mean(is_hot & is_stable))
    hot_unstable_frac = float(np.mean(is_hot & ~is_stable))
    cool_safe_frac = float(np.mean(~is_hot))

    # Thermal state per quintile (for H4 quintile alignment)
    quintile_thermal = {}
    for q in range(N_QUINTILES):
        mask = quintiles == q
        n_q = mask.sum()
        if n_q > 0:
            quintile_thermal[f'Q{q}'] = {
                'HOT_STABLE': float(np.mean((is_hot & is_stable)[mask])),
                'HOT_UNSTABLE': float(np.mean((is_hot & ~is_stable)[mask])),
                'COOL_SAFE': float(np.mean((~is_hot)[mask])),
            }

    return {
        'length': n,
        'quintile_action_dist': quintile_action_dist,
        'quintile_load': quintile_load,
        'quintile_stress': quintile_stress,
        'quintile_risk': quintile_risk,
        'quintile_overshoot': quintile_overshoot,
        'quintile_cum_overshoot': quintile_cum_overshoot,
        'quintile_thermal': quintile_thermal,
        'fine_action_dist': fine_action_dist,
        'fine_load': fine_load,
        'fine_risk': fine_risk,
        # H2 features
        'intervention_density': intervention_density,
        'passive_frac': passive_frac,
        'active_frac': active_frac,
        'proactive_frac': proactive_frac,
        'reactive_frac': reactive_frac,
        'neutral_frac': neutral_frac,
        'Q_var': float(np.var(Q)),
        'dQ_var': float(np.var(dQ)),
        'phi_accum': float(phi[-1] - phi[0]) if n > 1 else 0.0,
        'T_mean': float(np.mean(T)),
        'T_std': float(np.std(T)),
        'boundary_frac': float(np.mean(dT_abs > np.percentile(dT_abs, 67))) if n > 3 else 0.0,
        # H3 features
        'mean_passive_pos': mean_passive_pos,
        'mean_active_pos': mean_active_pos,
        'n_passive': len(passive_positions),
        'n_active': len(active_positions),
        # H4 features
        'hot_stable_frac': hot_stable_frac,
        'hot_unstable_frac': hot_unstable_frac,
        'cool_safe_frac': cool_safe_frac,
        # Mean risk
        'mean_risk': float(np.mean(risk)),
        'mean_load': float(np.mean(load)),
        'mean_stress': float(np.mean(stress)),
    }


# ============================================================
# LABEL SET B: UNSUPERVISED
# ============================================================

def compute_label_set_b(run_data, ops):
    """Unsupervised labels on operator features."""
    T = run_data['T']
    Q = run_data['Q']
    error = run_data['error']
    load = ops['operator_load']
    n = len(T)

    if n < 20:
        return {'gmm_k': 1, 'kmeans_k': 1}

    features = np.column_stack([T, Q, error, load])
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # GMM with BIC
    best_bic = np.inf
    best_k = 2
    for k in range(2, 7):
        try:
            gmm = GaussianMixture(n_components=k, n_init=3, max_iter=200, random_state=42)
            gmm.fit(X)
            bic = gmm.bic(X)
            if bic < best_bic:
                best_bic = bic
                best_k = k
        except Exception:
            continue

    # KMeans with silhouette
    best_sil = -1
    best_km_k = 2
    for k in range(2, 7):
        try:
            km = KMeans(n_clusters=k, n_init=10, random_state=42)
            lab = km.fit_predict(X)
            sc = silhouette_score(X, lab)
            if sc > best_sil:
                best_sil = sc
                best_km_k = k
        except Exception:
            continue

    return {
        'gmm_k': best_k,
        'gmm_bic': float(best_bic),
        'kmeans_k': best_km_k,
        'kmeans_sil': float(best_sil),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    rng = np.random.default_rng(42)
    param_sets = latin_hypercube_sample(N_PARAM_SETS, PARAM_RANGES, rng)

    all_results = []
    total_cycles = 0
    all_cycle_lengths = []

    # Aggregate quintile profiles across ALL cycles
    agg_action = {f'Q{q}': {'PROACTIVE': [], 'NEUTRAL': [], 'REACTIVE': []}
                  for q in range(N_QUINTILES)}
    agg_load = {f'Q{q}': [] for q in range(N_QUINTILES)}
    agg_stress = {f'Q{q}': [] for q in range(N_QUINTILES)}
    agg_risk = {f'Q{q}': [] for q in range(N_QUINTILES)}
    agg_overshoot = {f'Q{q}': [] for q in range(N_QUINTILES)}
    agg_thermal = {f'Q{q}': {'HOT_STABLE': [], 'HOT_UNSTABLE': [], 'COOL_SAFE': []}
                   for q in range(N_QUINTILES)}

    for pi, params in enumerate(param_sets):
        runs = []
        for ri in range(N_RUNS_PER):
            run_data = simulate_run(params, rng)
            ops = classify_operator_actions(run_data)
            label_b = compute_label_set_b(run_data, ops)

            cycle_bounds = segment_into_cycles(run_data)
            total_cycles += len(cycle_bounds)

            cycle_data = []
            for ci, bounds in enumerate(cycle_bounds):
                feats = extract_cycle_features(run_data, ops, bounds)
                all_cycle_lengths.append(feats['length'])

                # Aggregate
                for q in range(N_QUINTILES):
                    key = f'Q{q}'
                    if key in feats['quintile_action_dist']:
                        for atype in ['PROACTIVE', 'NEUTRAL', 'REACTIVE']:
                            agg_action[key][atype].append(
                                feats['quintile_action_dist'][key][atype])
                    if key in feats['quintile_load']:
                        agg_load[key].append(feats['quintile_load'][key])
                    if key in feats['quintile_stress']:
                        agg_stress[key].append(feats['quintile_stress'][key])
                    if key in feats['quintile_risk']:
                        agg_risk[key].append(feats['quintile_risk'][key])
                    if key in feats.get('quintile_overshoot', {}):
                        agg_overshoot[key].append(feats['quintile_overshoot'][key])
                    if key in feats['quintile_thermal']:
                        for ts in ['HOT_STABLE', 'HOT_UNSTABLE', 'COOL_SAFE']:
                            agg_thermal[key][ts].append(
                                feats['quintile_thermal'][key][ts])

                cycle_data.append({
                    'cycle_id': ci,
                    'length': feats['length'],
                    'quintile_action_dist': feats['quintile_action_dist'],
                    'quintile_load': feats['quintile_load'],
                    'quintile_stress': feats['quintile_stress'],
                    'quintile_risk': feats['quintile_risk'],
                    'quintile_overshoot': feats['quintile_overshoot'],
                    'quintile_cum_overshoot': feats['quintile_cum_overshoot'],
                    'quintile_thermal': feats['quintile_thermal'],
                    'features': {
                        'intervention_density': feats['intervention_density'],
                        'passive_frac': feats['passive_frac'],
                        'active_frac': feats['active_frac'],
                        'proactive_frac': feats['proactive_frac'],
                        'reactive_frac': feats['reactive_frac'],
                        'neutral_frac': feats['neutral_frac'],
                        'Q_var': feats['Q_var'],
                        'dQ_var': feats['dQ_var'],
                        'phi_accum': feats['phi_accum'],
                        'T_mean': feats['T_mean'],
                        'T_std': feats['T_std'],
                        'boundary_frac': feats['boundary_frac'],
                        'mean_passive_pos': feats['mean_passive_pos'],
                        'mean_active_pos': feats['mean_active_pos'],
                        'n_passive': feats['n_passive'],
                        'n_active': feats['n_active'],
                        'hot_stable_frac': feats['hot_stable_frac'],
                        'hot_unstable_frac': feats['hot_unstable_frac'],
                        'cool_safe_frac': feats['cool_safe_frac'],
                        'mean_risk': feats['mean_risk'],
                        'mean_load': feats['mean_load'],
                        'mean_stress': feats['mean_stress'],
                    },
                })

            runs.append({
                'run_id': ri,
                'T_target': float(run_data['T_target']),
                'T_boil': float(run_data['T_boil']),
                'Q_bias': float(run_data['Q_bias']),
                'n_cycles': len(cycle_bounds),
                'label_b_meta': label_b,
                'cycles': cycle_data,
            })

        all_results.append({
            'param_id': pi,
            'params': {k: float(v) for k, v in params.items()},
            'runs': runs,
        })

        if (pi + 1) % 10 == 0:
            print(f"  Param {pi+1}/{N_PARAM_SETS}: "
                  f"cycles_so_far={total_cycles}, "
                  f"mean_len={np.mean(all_cycle_lengths):.1f}")

    # ============================================================
    # SUMMARY
    # ============================================================

    # Aggregate operator action profiles
    quintile_action_summary = {}
    for q in range(N_QUINTILES):
        key = f'Q{q}'
        quintile_action_summary[key] = {
            atype: {
                'mean': float(np.mean(agg_action[key][atype])),
                'std': float(np.std(agg_action[key][atype])),
                'n': len(agg_action[key][atype]),
            }
            for atype in ['PROACTIVE', 'NEUTRAL', 'REACTIVE']
        }

    quintile_load_summary = {
        f'Q{q}': {
            'mean': float(np.mean(agg_load[f'Q{q}'])),
            'std': float(np.std(agg_load[f'Q{q}'])),
        }
        for q in range(N_QUINTILES) if agg_load[f'Q{q}']
    }

    quintile_stress_summary = {
        f'Q{q}': {
            'mean': float(np.mean(agg_stress[f'Q{q}'])),
            'std': float(np.std(agg_stress[f'Q{q}'])),
        }
        for q in range(N_QUINTILES) if agg_stress[f'Q{q}']
    }

    quintile_risk_summary = {
        f'Q{q}': {
            'mean': float(np.mean(agg_risk[f'Q{q}'])),
            'std': float(np.std(agg_risk[f'Q{q}'])),
        }
        for q in range(N_QUINTILES) if agg_risk[f'Q{q}']
    }

    quintile_overshoot_summary = {
        f'Q{q}': {
            'mean': float(np.mean(agg_overshoot[f'Q{q}'])),
            'std': float(np.std(agg_overshoot[f'Q{q}'])),
        }
        for q in range(N_QUINTILES) if agg_overshoot[f'Q{q}']
    }

    quintile_thermal_summary = {}
    for q in range(N_QUINTILES):
        key = f'Q{q}'
        quintile_thermal_summary[key] = {
            ts: {
                'mean': float(np.mean(agg_thermal[key][ts])),
                'std': float(np.std(agg_thermal[key][ts])),
            }
            for ts in ['HOT_STABLE', 'HOT_UNSTABLE', 'COOL_SAFE']
            if agg_thermal[key][ts]
        }

    summary = {
        'n_parameterizations': N_PARAM_SETS,
        'n_runs_per': N_RUNS_PER,
        'total_runs': N_PARAM_SETS * N_RUNS_PER,
        'total_cycles': total_cycles,
        'dt': DT,
        'delay': DELAY,
        'delay_physical': DT * DELAY,
        'effective_steps': N_STEPS - BURN_IN,
        'cycle_length_stats': {
            'mean': float(np.mean(all_cycle_lengths)),
            'median': float(np.median(all_cycle_lengths)),
            'std': float(np.std(all_cycle_lengths)),
            'min': int(np.min(all_cycle_lengths)),
            'max': int(np.max(all_cycle_lengths)),
        },
        'quintile_operator_action_profile': quintile_action_summary,
        'quintile_load_profile': quintile_load_summary,
        'quintile_stress_profile': quintile_stress_summary,
        'quintile_risk_profile': quintile_risk_summary,
        'quintile_overshoot_profile': quintile_overshoot_summary,
        'quintile_thermal_profile': quintile_thermal_summary,
        'non_circularity': {
            'voynich_input': 'NONE — zero Voynich-derived values in T1',
            'operator_labels': 'PROACTIVE/NEUTRAL/REACTIVE from control error sign',
            'overshoot_risk': 'max(0, T - T_target) — asymmetric, from thermodynamics',
            'threshold': f'NEUTRAL_ERROR_FRAC={NEUTRAL_ERROR_FRAC} (30% of eq_scale)',
            'risk_components': ['|dT|', '|dphi|', '|error|', 'max(0, T-T_target)'],
        },
        'design_note': (
            'v3b: Ascending half-cycle segmentation (trough → peak). '
            'Full trough-to-trough cycles give symmetric overshoot risk (inverted-U). '
            'The Voynich predicts monotonically increasing danger (Q0=safe, Q4=dangerous). '
            'The ascending half (trough→peak) matches: overshoot risk increases '
            'monotonically from zero (trough) to maximum (peak). '
            'Primary test variable: overshoot risk = max(0, T - T_target).'
        ),
    }

    output = {
        'summary': summary,
        'parameterizations': all_results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't1_physical_process.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    # Print report
    print(f"\n{'='*60}")
    print(f"T1 PHYSICAL PROCESS (REDESIGNED) COMPLETE")
    print(f"{'='*60}")
    print(f"DT={DT}, DELAY={DELAY} ({DT*DELAY:.2f} time units)")
    print(f"Parameterizations: {N_PARAM_SETS}")
    print(f"Total runs:        {N_PARAM_SETS * N_RUNS_PER}")
    print(f"Total cycles:      {total_cycles}")
    cl = all_cycle_lengths
    print(f"Cycle length:      mean={np.mean(cl):.1f}  "
          f"median={np.median(cl):.0f}  "
          f"range=[{np.min(cl)}, {np.max(cl)}]")
    print()
    print("OPERATOR ACTION PROFILE (quintile means):")
    print(f"  {'Q':<4} {'PROACTIVE':>10} {'NEUTRAL':>10} {'REACTIVE':>10} {'LOAD':>10}")
    for q in range(N_QUINTILES):
        key = f'Q{q}'
        qa = quintile_action_summary[key]
        ql = quintile_load_summary.get(key, {'mean': 0})
        print(f"  {key:<4} {qa['PROACTIVE']['mean']:>10.3f} "
              f"{qa['NEUTRAL']['mean']:>10.3f} "
              f"{qa['REACTIVE']['mean']:>10.3f} "
              f"{ql['mean']:>10.4f}")
    print()
    print("THERMAL STATE PROFILE:")
    print(f"  {'Q':<4} {'HOT_STABLE':>12} {'HOT_UNSTABLE':>14} {'COOL_SAFE':>10}")
    for q in range(N_QUINTILES):
        key = f'Q{q}'
        qt = quintile_thermal_summary.get(key, {})
        hs = qt.get('HOT_STABLE', {'mean': 0})['mean']
        hu = qt.get('HOT_UNSTABLE', {'mean': 0})['mean']
        cs = qt.get('COOL_SAFE', {'mean': 0})['mean']
        print(f"  {key:<4} {hs:>12.3f} {hu:>14.3f} {cs:>10.3f}")
    print()
    print("OVERSHOOT RISK PROFILE (asymmetric: max(0, T-T_target)):")
    print(f"  {'Q':<4} {'OVERSHOOT':>12}")
    for q in range(N_QUINTILES):
        key = f'Q{q}'
        ov = quintile_overshoot_summary.get(key, {'mean': 0})['mean']
        print(f"  {key:<4} {ov:>12.6f}")
    print()
    print(f"Output: {out_path}")
    sz = out_path.stat().st_size / 1024 / 1024
    print(f"Size: {sz:.1f} MB")


if __name__ == '__main__':
    main()
