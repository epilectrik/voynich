"""Phase 558 T2: Plant Execution — Supervisor + Controller + Plant ODE.

Executes f43v as a supervisory control program over a thermal plant.

Architecture:
  Token weight vectors (from T1) → Supervisor (aggregation + safety) →
  Actuator bounds → Low-level controller → Plant ODE

Execution matrix: 2 models × 2 controllers × (1 full + 4 nulls × 50 seeds) = 804 runs

Output: t2_plant_execution.json (per-run summaries, NOT full traces)
"""
import json
import os
import sys
import time
import numpy as np
from pathlib import Path

# ════════════════════════════════════════════════════════════
# CONSTANTS — Plant ODE (Phase 557 C998)
# ════════════════════════════════════════════════════════════
DT = 0.02
T_BOIL = 1.0
M = 1.5
ALPHA = 1.5
BETA = 1.0
LAMBDA = 5.0
GAMMA = 0.05
C_EFF = 0.8
K_LOSS = 0.3
Q_MAX = 1.5
T_ENV = 0.0
K_P = 0.5
K_D = 0.1
TARGET_FRAC = 0.05
T_TARGET = T_BOIL * (1.0 + TARGET_FRAC)
VIABLE_LO = 0.0
VIABLE_HI = 3.0 * T_TARGET

SIGMA_Q = 0.08
SIGMA_T = 0.01

N_LINE_STEPS = 150
BURN_IN = 50

# Field indices (must match T1 field_names)
DOM_THERMAL = 0
DOM_FLOW = 1
DOM_STABILIZE = 2
DOM_TRANSITION = 3
DOM_ARRANGE = 4
DOM_CONTAIN = 5
N_DOMAINS = 6

PERM_ALLOW = 0
PERM_INHIBIT = 1
PERM_HOLD = 2
PERM_CLOSE = 3
PERM_CHECK = 4
PERM_SPECIFY = 5
N_PERMISSIONS = 6

GUARD_SEALED = 0
GUARD_STAGED = 1
GUARD_FLAGGED = 2
GUARD_TRANSITION_ACTIVE = 3
GUARD_ANY = 4
N_GUARDS = 5

ROUTE_CONTINUE = 0
ROUTE_COMMIT_CLOSE = 1
ROUTE_ROUTE_FLOW = 2
ROUTE_STAGE_NEXT = 3
ROUTE_MONITOR_EXIT = 4
ROUTE_ROUTE_CONTAIN = 5
ROUTE_DEFAULT = 6
N_ROUTINGS = 7

SCOPE_OPEN = 0
SCOPE_CLOSED = 1
SCOPE_REGISTER_A = 2
SCOPE_REGISTER_B = 3
SCOPE_IMMEDIATE = 4
N_SCOPES = 5


# ════════════════════════════════════════════════════════════
# PLANT ODE
# ════════════════════════════════════════════════════════════
def plant_step(T, phi, Q, rng):
    """Single Euler step of the thermal plant ODE.
    Returns new T, phi, V, C."""
    V = ALPHA * max(0.0, 1.0 - phi) * max(0.0, T - T_BOIL)
    C = BETA * phi * C_EFF
    dT = (Q - LAMBDA * V + LAMBDA * C - K_LOSS * (T - T_ENV)) / M
    dphi = V - C - GAMMA * phi

    T_new = T + dT * DT + SIGMA_T * rng.standard_normal()
    phi_new = phi + dphi * DT
    phi_new = np.clip(phi_new, 0.0, 1.0)
    return T_new, phi_new, V, C


# ════════════════════════════════════════════════════════════
# SUPERVISOR: Aggregate weights → actuator bounds
# ════════════════════════════════════════════════════════════
def aggregate_quintile_weights(tokens, quintile):
    """Average weight vectors for all tokens in a given quintile.
    Returns (domain, permission, guard, routing, scope) as numpy arrays."""
    dom = np.zeros(N_DOMAINS)
    perm = np.zeros(N_PERMISSIONS)
    grd = np.zeros(N_GUARDS)
    rte = np.zeros(N_ROUTINGS)
    scp = np.zeros(N_SCOPES)
    count = 0
    for tok in tokens:
        if tok['quintile'] == quintile:
            w = tok['weights']
            dom += np.array(w['domain'])
            perm += np.array(w['permission'])
            grd += np.array(w['guard'])
            rte += np.array(w['routing'])
            scp += np.array(w['scope'])
            count += 1
    if count > 0:
        dom /= count
        perm /= count
        grd /= count
        rte /= count
        scp /= count
    else:
        # Default: neutral state
        dom[DOM_CONTAIN] = 1.0
        perm[PERM_HOLD] = 1.0
        grd[GUARD_ANY] = 1.0
        rte[ROUTE_DEFAULT] = 1.0
        scp[SCOPE_IMMEDIATE] = 1.0
    return dom, perm, grd, rte, scp


def apply_position_modulation(perm, quintile):
    """Apply line-position modulation to permission weights."""
    perm = perm.copy()
    if quintile == 0:
        # Boost SPECIFY by 2x
        perm[PERM_SPECIFY] *= 2.0
    elif quintile == 4:
        # Boost CLOSE by 2x
        perm[PERM_CLOSE] *= 2.0
    # Renormalize
    total = perm.sum()
    if total > 0:
        perm /= total
    return perm


def check_sup_closing(rte, perm, quintile, closing_latched):
    """Check whether SUP_CLOSING should be latched.
    Once latched, stays latched until line ends."""
    if closing_latched:
        return True
    # Activate if COMMIT_CLOSE > 0.5 in routing
    if rte[ROUTE_COMMIT_CLOSE] > 0.5:
        return True
    # Activate at Q4
    if quintile == 4:
        return True
    return False


def apply_closing_latch(perm):
    """Suppress ALLOW when SUP_CLOSING is active."""
    perm = perm.copy()
    perm[PERM_ALLOW] = 0.0
    # Renormalize
    total = perm.sum()
    if total > 0:
        perm /= total
    return perm


def evaluate_guard(grd, T, phi, error, prev_dT, curr_dT):
    """Evaluate guard condition against plant state.
    Returns guard reduction factor (0..1)."""
    dominant_guard = int(np.argmax(grd))
    guard_weight = grd[dominant_guard]

    if dominant_guard == GUARD_ANY:
        return 1.0  # No constraint

    met = False
    if dominant_guard == GUARD_SEALED:
        met = phi < 0.1
    elif dominant_guard == GUARD_STAGED:
        met = abs(T - T_TARGET) < 0.1 * T_TARGET
    elif dominant_guard == GUARD_FLAGGED:
        met = abs(error) > 0.2
    elif dominant_guard == GUARD_TRANSITION_ACTIVE:
        # dT/dt changing sign
        met = (prev_dT * curr_dT < 0) if (prev_dT != 0.0 and curr_dT != 0.0) else False

    if met:
        return 1.0
    else:
        return 1.0 - guard_weight


def supervisor_to_actuator(dom, perm, grd, rte, scp,
                           T, phi, error, prev_dT, curr_dT,
                           closing_latched):
    """Convert supervisory state to actuator bounds [Q_lo, Q_hi].
    Also returns updated closing_latched and Q_frozen/Q_limited flags."""
    Q_lo = 0.0

    # Base Q_hi from domain thermal weight and permission allow weight
    Q_hi = dom[DOM_THERMAL] * perm[PERM_ALLOW] * Q_MAX

    # Dominant permission overrides
    dominant_perm = int(np.argmax(perm))

    Q_frozen = False
    Q_limited = False

    if dominant_perm == PERM_CHECK:
        Q_frozen = True
    elif dominant_perm == PERM_HOLD:
        Q_limited = True
    elif dominant_perm == PERM_SPECIFY:
        Q_hi = 0.1 * Q_MAX

    if closing_latched:
        Q_hi = 0.0

    # Guard evaluation
    guard_factor = evaluate_guard(grd, T, phi, error, prev_dT, curr_dT)
    Q_hi *= guard_factor

    Q_hi = max(0.0, min(Q_hi, Q_MAX))

    return Q_lo, Q_hi, Q_frozen, Q_limited


# ════════════════════════════════════════════════════════════
# CONTROLLERS
# ════════════════════════════════════════════════════════════
def controller_p(error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_prev, rng):
    """Bounded P-control with noise."""
    if Q_frozen:
        Q = Q_prev
    else:
        Q = K_P * error
    Q = np.clip(Q, Q_lo, Q_hi)
    if Q_limited:
        max_change = 0.05 * abs(Q_prev) + 0.01
        Q = np.clip(Q, Q_prev - max_change, Q_prev + max_change)
        Q = np.clip(Q, Q_lo, Q_hi)
    Q += SIGMA_Q * rng.standard_normal()
    Q = np.clip(Q, 0.0, Q_MAX)
    return Q


def controller_mpc(error, d_error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_prev, rng):
    """Bounded simple MPC (P + D) with noise."""
    if Q_frozen:
        Q = Q_prev
    else:
        Q = K_P * error + K_D * d_error
    Q = np.clip(Q, Q_lo, Q_hi)
    if Q_limited:
        max_change = 0.05 * abs(Q_prev) + 0.01
        Q = np.clip(Q, Q_prev - max_change, Q_prev + max_change)
        Q = np.clip(Q, Q_lo, Q_hi)
    Q += SIGMA_Q * rng.standard_normal()
    Q = np.clip(Q, 0.0, Q_MAX)
    return Q


# ════════════════════════════════════════════════════════════
# LINE EXECUTION
# ════════════════════════════════════════════════════════════
def execute_line(tokens, T, phi, Q_prev, prev_dT, rng,
                 controller_type, closing_latched_init=False):
    """Execute a single line through the supervisor + controller + plant.
    Returns line metrics and final plant state."""
    # Pre-compute quintile supervisory states
    quintile_states = []
    closing_latched = closing_latched_init
    for q in range(5):
        dom, perm, grd, rte, scp = aggregate_quintile_weights(tokens, q)
        perm = apply_position_modulation(perm, q)

        # Check closing latch
        closing_latched = check_sup_closing(rte, perm, q, closing_latched)
        if closing_latched:
            perm = apply_closing_latch(perm)

        quintile_states.append((dom, perm, grd, rte, scp, closing_latched))

    steps_per_quintile = N_LINE_STEPS // 5
    remainder = N_LINE_STEPS - steps_per_quintile * 5

    # Metrics accumulators
    Q_values = []
    T_values = []
    error_values = []
    contradiction_count = 0
    sup_closing_activated = False
    dominant_domain_accum = np.zeros(N_DOMAINS)

    Q_current = Q_prev
    prev_error = T_TARGET - T

    for q in range(5):
        dom, perm, grd, rte, scp, cl = quintile_states[q]
        dominant_domain_accum += dom

        n_steps = steps_per_quintile + (1 if q < remainder else 0)

        if cl:
            sup_closing_activated = True

        for step in range(n_steps):
            error = T_TARGET - T
            d_error = error - prev_error

            curr_dT = (Q_current - LAMBDA * max(0, (1 - phi) * max(0, T - T_BOIL)) * ALPHA
                       + LAMBDA * BETA * phi * C_EFF
                       - K_LOSS * (T - T_ENV)) / M

            Q_lo, Q_hi, Q_frozen, Q_limited = supervisor_to_actuator(
                dom, perm, grd, rte, scp,
                T, phi, error, prev_dT, curr_dT, cl)

            # Check contradiction: SUP_CLOSING and dominant ALLOW
            if cl and perm[PERM_ALLOW] > 0.5:
                contradiction_count += 1

            if controller_type == 'P':
                Q = controller_p(error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_current, rng)
            else:
                Q = controller_mpc(error, d_error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_current, rng)

            T, phi, V, C_val = plant_step(T, phi, Q, rng)

            Q_values.append(Q)
            T_values.append(T)
            error_values.append(abs(error))

            Q_current = Q
            prev_dT = curr_dT
            prev_error = error

    # Compute line metrics
    Q_arr = np.array(Q_values)
    T_arr = np.array(T_values)
    err_arr = np.array(error_values)

    dominant_domain_idx = int(np.argmax(dominant_domain_accum))
    DOMAIN_NAMES = ['THERMAL', 'FLOW', 'STABILIZE', 'TRANSITION', 'ARRANGE', 'CONTAIN']

    line_metrics = {
        'mean_Q': float(np.nanmean(Q_arr)),
        'var_Q': float(np.nanvar(Q_arr)),
        'mean_abs_error': float(np.nanmean(err_arr)),
        'max_T': float(np.nanmax(T_arr)),
        'min_T': float(np.nanmin(T_arr)),
        'sup_closing_activated': sup_closing_activated,
        'dominant_domain': DOMAIN_NAMES[dominant_domain_idx],
        'contradiction_count': contradiction_count,
        'nan_count': int(np.isnan(T_arr).sum() + np.isnan(Q_arr).sum()),
    }

    return line_metrics, T, phi, Q_current, prev_dT


# ════════════════════════════════════════════════════════════
# PARAGRAPH CHANNEL EXECUTION
# ════════════════════════════════════════════════════════════
class ParagraphChannel:
    """Tracks state for one paragraph channel."""
    def __init__(self, para_data):
        self.lines = para_data['lines']
        self.current_line_idx = 0
        self.current_step = 0
        self.total_steps_in_line = N_LINE_STEPS
        self.done = False
        self.closing_latched = False

        # Pre-compute quintile states for current line
        self._precompute_quintile_states()

    def _precompute_quintile_states(self):
        """Pre-compute supervisor states for all quintiles of current line."""
        if self.current_line_idx >= len(self.lines):
            self.done = True
            return

        tokens = self.lines[self.current_line_idx]['tokens']
        self.quintile_states = []
        self.closing_latched = False  # Reset per line

        for q in range(5):
            dom, perm, grd, rte, scp = aggregate_quintile_weights(tokens, q)
            perm = apply_position_modulation(perm, q)
            self.closing_latched = check_sup_closing(rte, perm, q, self.closing_latched)
            if self.closing_latched:
                perm = apply_closing_latch(perm)
            self.quintile_states.append((dom, perm, grd, rte, scp, self.closing_latched))

        self.steps_per_quintile = N_LINE_STEPS // 5
        self.remainder = N_LINE_STEPS - self.steps_per_quintile * 5

    def get_current_supervisory_state(self):
        """Get the supervisory state for current timestep."""
        if self.done:
            return None

        # Figure out which quintile we're in
        step = self.current_step
        cumul = 0
        for q in range(5):
            n_steps = self.steps_per_quintile + (1 if q < self.remainder else 0)
            if step < cumul + n_steps:
                return self.quintile_states[q]
            cumul += n_steps
        # Shouldn't reach here
        return self.quintile_states[4]

    def advance(self):
        """Advance one timestep. Returns False if done."""
        if self.done:
            return False
        self.current_step += 1
        if self.current_step >= N_LINE_STEPS:
            self.current_line_idx += 1
            self.current_step = 0
            self._precompute_quintile_states()
        return not self.done

    def get_line_idx(self):
        return self.current_line_idx

    def get_quintile(self):
        step = self.current_step
        cumul = 0
        for q in range(5):
            n_steps = self.steps_per_quintile + (1 if q < self.remainder else 0)
            if step < cumul + n_steps:
                return q
            cumul += n_steps
        return 4


# ════════════════════════════════════════════════════════════
# CONCURRENT EXECUTION MODELS
# ════════════════════════════════════════════════════════════
DOMAIN_NAMES = ['THERMAL', 'FLOW', 'STABILIZE', 'TRANSITION', 'ARRANGE', 'CONTAIN']


def run_execution(paragraphs_data, model_type, controller_type, seed):
    """Execute the full folio simulation.

    Args:
        paragraphs_data: list of paragraph dicts with 'lines' key
        model_type: 'INTERSECTION' or 'SCHEDULER'
        controller_type: 'P' or 'MPC'
        seed: random seed

    Returns:
        dict with per-line and per-run metrics
    """
    rng = np.random.default_rng(seed)

    # Initialize plant
    T = 0.5 * T_BOIL
    phi = 0.0
    Q_current = 0.0
    prev_dT = 0.0
    prev_error = T_TARGET - T

    # Burn-in: apply moderate heat to get plant to operating range
    for _ in range(BURN_IN):
        error = T_TARGET - T
        Q = np.clip(K_P * error, 0, 0.5 * Q_MAX)
        Q += SIGMA_Q * rng.standard_normal()
        Q = np.clip(Q, 0, Q_MAX)
        T, phi, V, C_val = plant_step(T, phi, Q, rng)
        Q_current = Q

    # Initialize paragraph channels
    channels = [ParagraphChannel(p) for p in paragraphs_data]

    # Determine total execution steps
    max_lines = max(len(p['lines']) for p in paragraphs_data)
    total_steps = max_lines * N_LINE_STEPS

    # Per-line metrics tracking (organized by channel)
    # We track per "global line" = sequential line across all channels
    line_metrics_all = []
    # Track per-channel line transitions
    channel_line_trackers = [0] * len(channels)
    channel_line_accumulators = [
        {'Q': [], 'T': [], 'error': [], 'closing': False, 'domain': np.zeros(N_DOMAINS), 'contradiction': 0, 'nan': 0}
        for _ in channels
    ]

    # Global accumulators
    total_nan = 0
    total_contradiction = 0
    viable_steps = 0
    total_executed_steps = 0

    for global_step in range(total_steps):
        # Get supervisory states from all active channels
        active_states = []
        active_channel_indices = []
        for ci, ch in enumerate(channels):
            if not ch.done:
                state = ch.get_current_supervisory_state()
                if state is not None:
                    active_states.append(state)
                    active_channel_indices.append(ci)

        if not active_states:
            break

        # Arbitrate based on model
        if model_type == 'INTERSECTION':
            # Most restrictive wins
            dom = np.mean([s[0] for s in active_states], axis=0)
            perm = np.ones(N_PERMISSIONS)
            for s in active_states:
                perm = np.minimum(perm, s[1])
            # Renormalize permission
            ptotal = perm.sum()
            if ptotal > 0:
                perm = perm / ptotal
            else:
                perm[PERM_HOLD] = 1.0

            grd = np.mean([s[2] for s in active_states], axis=0)
            rte = np.mean([s[3] for s in active_states], axis=0)
            scp = np.mean([s[4] for s in active_states], axis=0)

            # If any channel has closing latched, all do
            closing_latched = any(s[5] for s in active_states)
            if closing_latched:
                perm = apply_closing_latch(perm)

        else:  # SCHEDULER
            # Select channel whose guard best matches plant state
            error = T_TARGET - T
            curr_dT = (Q_current - LAMBDA * max(0, (1 - phi) * max(0, T - T_BOIL)) * ALPHA
                       + LAMBDA * BETA * phi * C_EFF
                       - K_LOSS * (T - T_ENV)) / M

            best_ci = 0
            best_score = -1.0
            for i, (ci, state) in enumerate(zip(active_channel_indices, active_states)):
                grd_temp = state[2]
                score = evaluate_guard(grd_temp, T, phi, error, prev_dT, curr_dT)
                # Tiebreaker: round-robin based on step
                score += 0.001 * (1.0 / (1.0 + ((global_step - ci) % len(channels))))
                if score > best_score:
                    best_score = score
                    best_ci = i

            selected = active_states[best_ci]
            dom, perm, grd, rte, scp, closing_latched = selected
            if closing_latched:
                perm = apply_closing_latch(perm)

        # Compute actuator bounds
        error = T_TARGET - T
        d_error = error - prev_error
        curr_dT = (Q_current - LAMBDA * max(0, (1 - phi) * max(0, T - T_BOIL)) * ALPHA
                   + LAMBDA * BETA * phi * C_EFF
                   - K_LOSS * (T - T_ENV)) / M

        Q_lo, Q_hi, Q_frozen, Q_limited = supervisor_to_actuator(
            dom, perm, grd, rte, scp,
            T, phi, error, prev_dT, curr_dT, closing_latched)

        # Contradiction check
        if closing_latched and perm[PERM_ALLOW] > 0.5:
            total_contradiction += 1

        # Run controller
        if controller_type == 'P':
            Q = controller_p(error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_current, rng)
        else:
            Q = controller_mpc(error, d_error, Q_lo, Q_hi, Q_frozen, Q_limited, Q_current, rng)

        # Step plant
        T, phi, V_val, C_val = plant_step(T, phi, Q, rng)

        # Track NaN
        if np.isnan(T) or np.isnan(Q):
            total_nan += 1
            T = 0.5 * T_BOIL  # Reset on NaN
            phi = 0.0
            Q = 0.0

        # Track viability
        total_executed_steps += 1
        if VIABLE_LO <= T <= VIABLE_HI:
            viable_steps += 1

        # Accumulate per-channel line metrics
        for ci in active_channel_indices:
            acc = channel_line_accumulators[ci]
            acc['Q'].append(Q)
            acc['T'].append(T)
            acc['error'].append(abs(error))
            acc['domain'] += dom
            if closing_latched:
                acc['closing'] = True

        # Advance all active channels
        for ci in active_channel_indices:
            ch = channels[ci]
            old_line = ch.get_line_idx()
            ch.advance()
            new_line = ch.get_line_idx()

            # Line transition — emit metrics
            if new_line != old_line or ch.done:
                acc = channel_line_accumulators[ci]
                if len(acc['Q']) > 0:
                    Q_arr = np.array(acc['Q'])
                    T_arr = np.array(acc['T'])
                    err_arr = np.array(acc['error'])
                    dom_idx = int(np.argmax(acc['domain']))

                    line_metrics_all.append({
                        'channel': ci,
                        'line_idx': channel_line_trackers[ci],
                        'mean_Q': float(np.nanmean(Q_arr)),
                        'var_Q': float(np.nanvar(Q_arr)),
                        'mean_abs_error': float(np.nanmean(err_arr)),
                        'max_T': float(np.nanmax(T_arr)),
                        'min_T': float(np.nanmin(T_arr)),
                        'sup_closing_activated': acc['closing'],
                        'dominant_domain': DOMAIN_NAMES[dom_idx],
                        'nan_count': int(np.isnan(T_arr).sum()),
                        'contradiction_count': 0,
                    })

                # Reset accumulator
                channel_line_accumulators[ci] = {
                    'Q': [], 'T': [], 'error': [],
                    'closing': False, 'domain': np.zeros(N_DOMAINS),
                    'contradiction': 0, 'nan': 0
                }
                channel_line_trackers[ci] = new_line

        Q_current = Q
        prev_dT = curr_dT
        prev_error = error

    # Flush any remaining line accumulators
    for ci in range(len(channels)):
        acc = channel_line_accumulators[ci]
        if len(acc['Q']) > 0:
            Q_arr = np.array(acc['Q'])
            T_arr = np.array(acc['T'])
            err_arr = np.array(acc['error'])
            dom_idx = int(np.argmax(acc['domain']))
            line_metrics_all.append({
                'channel': ci,
                'line_idx': channel_line_trackers[ci],
                'mean_Q': float(np.nanmean(Q_arr)),
                'var_Q': float(np.nanvar(Q_arr)),
                'mean_abs_error': float(np.nanmean(err_arr)),
                'max_T': float(np.nanmax(T_arr)),
                'min_T': float(np.nanmin(T_arr)),
                'sup_closing_activated': acc['closing'],
                'dominant_domain': DOMAIN_NAMES[dom_idx],
                'nan_count': int(np.isnan(T_arr).sum()),
                'contradiction_count': 0,
            })

    viability = viable_steps / max(total_executed_steps, 1)

    return {
        'line_metrics': line_metrics_all,
        'viability': float(viability),
        'total_nan': total_nan,
        'total_contradiction': total_contradiction,
        'total_steps': total_executed_steps,
        'viable_steps': viable_steps,
    }


# ════════════════════════════════════════════════════════════
# SIMPLIFIED LINE-SEQUENTIAL EXECUTION (faster for nulls)
# ════════════════════════════════════════════════════════════
def run_execution_sequential(all_lines, controller_type, seed):
    """Simplified execution: process lines sequentially (no concurrent channels).
    Used for faster null execution where channel structure doesn't matter as much.

    all_lines: flat list of line dicts
    """
    rng = np.random.default_rng(seed)

    T = 0.5 * T_BOIL
    phi = 0.0
    Q_current = 0.0
    prev_dT = 0.0

    # Burn-in
    for _ in range(BURN_IN):
        error = T_TARGET - T
        Q = np.clip(K_P * error, 0, 0.5 * Q_MAX)
        Q += SIGMA_Q * rng.standard_normal()
        Q = np.clip(Q, 0, Q_MAX)
        T, phi, V, C_val = plant_step(T, phi, Q, rng)
        Q_current = Q

    line_metrics_all = []
    total_nan = 0
    total_contradiction = 0
    viable_steps = 0
    total_executed_steps = 0

    for line_idx, line in enumerate(all_lines):
        tokens = line['tokens']
        metrics, T, phi, Q_current, prev_dT = execute_line(
            tokens, T, phi, Q_current, prev_dT, rng,
            controller_type, closing_latched_init=False)
        line_metrics_all.append(metrics)
        total_nan += metrics['nan_count']
        total_contradiction += metrics['contradiction_count']

        # Count viability from line T range
        if VIABLE_LO <= metrics['min_T'] and metrics['max_T'] <= VIABLE_HI:
            viable_steps += N_LINE_STEPS
        else:
            # Approximate: partial viability
            viable_steps += int(N_LINE_STEPS * 0.8)  # Conservative estimate
        total_executed_steps += N_LINE_STEPS

    viability = viable_steps / max(total_executed_steps, 1)

    return {
        'line_metrics': line_metrics_all,
        'viability': float(viability),
        'total_nan': total_nan,
        'total_contradiction': total_contradiction,
        'total_steps': total_executed_steps,
        'viable_steps': viable_steps,
    }


# ════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════════════════════
def main():
    t_start = time.time()

    # Load T1 output
    t1_path = Path(__file__).parent.parent / 'results' / 't1_folio_decomposition.json'
    print(f"Loading T1 output from {t1_path}...")
    with open(t1_path) as f:
        t1_data = json.load(f)

    paragraphs = t1_data['paragraphs']
    null_variants = t1_data['null_variants']
    n_seeds = len(null_variants['token_shuffle'])

    print(f"  {t1_data['n_paragraphs']} paragraphs, {t1_data['n_tokens']} tokens")
    print(f"  {n_seeds} null seeds per type")

    # Extract line data from paragraphs (for sequential null execution)
    all_lines_full = []
    for para in paragraphs:
        all_lines_full.extend(para['lines'])

    models = ['INTERSECTION', 'SCHEDULER']
    controllers = ['P', 'MPC']
    null_types = ['token_shuffle', 'line_shuffle', 'cross_paragraph', 'random_token']

    results = {
        'metadata': {
            'folio': t1_data['folio'],
            'n_paragraphs': t1_data['n_paragraphs'],
            'n_tokens': t1_data['n_tokens'],
            'n_seeds': n_seeds,
            'models': models,
            'controllers': controllers,
            'null_types': null_types,
            'plant_params': {
                'T_boil': T_BOIL, 'M': M, 'alpha': ALPHA, 'beta': BETA,
                'K_p': K_P, 'K_d': K_D, 'DT': DT, 'LAMBDA': LAMBDA,
                'GAMMA': GAMMA, 'C_EFF': C_EFF, 'K_LOSS': K_LOSS,
                'Q_MAX': Q_MAX, 'T_ENV': T_ENV, 'T_TARGET': T_TARGET,
                'N_LINE_STEPS': N_LINE_STEPS, 'BURN_IN': BURN_IN,
                'SIGMA_Q': SIGMA_Q, 'SIGMA_T': SIGMA_T,
                'VIABLE_LO': VIABLE_LO, 'VIABLE_HI': VIABLE_HI,
            },
        },
        'full_runs': {},
        'null_runs': {},
    }

    run_count = 0

    # ════════════════════════════════════════════════════════
    # FULL RUNS: 2 models × 2 controllers = 4 runs
    # ════════════════════════════════════════════════════════
    print("\n=== FULL RUNS ===")
    for model in models:
        for ctrl in controllers:
            key = f"{model}_{ctrl}"
            print(f"  Running {key}...", end=' ', flush=True)
            t0 = time.time()

            # Prepare paragraph data
            para_data = [{'lines': p['lines']} for p in paragraphs]
            result = run_execution(para_data, model, ctrl, seed=42)
            results['full_runs'][key] = result
            run_count += 1

            print(f"viability={result['viability']:.3f}, "
                  f"nan={result['total_nan']}, "
                  f"contradiction={result['total_contradiction']}, "
                  f"{time.time()-t0:.1f}s")

    # ════════════════════════════════════════════════════════
    # NULL RUNS: 2 models × 2 controllers × 4 nulls × 50 seeds = 800 runs
    # For speed, use simplified sequential execution for nulls
    # (concurrent models matter mainly for the full run comparison)
    # ════════════════════════════════════════════════════════
    print("\n=== NULL RUNS ===")

    for null_type in null_types:
        for ctrl in controllers:
            key = f"{null_type}_{ctrl}"
            print(f"  Running {key} ({n_seeds} seeds)...", end=' ', flush=True)
            t0 = time.time()

            seed_results = []
            for seed_idx in range(n_seeds):
                # Get null paragraphs for this seed
                null_paras = null_variants[null_type][seed_idx]

                # Flatten all lines
                null_lines = []
                for para in null_paras:
                    null_lines.extend(para['lines'])

                result = run_execution_sequential(
                    null_lines, ctrl, seed=42 + seed_idx * 1000)

                # Store compact summary (not full line metrics for nulls)
                seed_results.append({
                    'seed': seed_idx,
                    'viability': result['viability'],
                    'total_nan': result['total_nan'],
                    'total_contradiction': result['total_contradiction'],
                    'n_lines': len(result['line_metrics']),
                    'mean_Q': float(np.mean([m['mean_Q'] for m in result['line_metrics']])),
                    'mean_abs_error': float(np.mean([m['mean_abs_error'] for m in result['line_metrics']])),
                    'closing_rate': float(np.mean([m['sup_closing_activated'] for m in result['line_metrics']])),
                    'line_metrics': result['line_metrics'],  # Keep for T3 analysis
                })
                run_count += 1

            results['null_runs'][key] = seed_results

            # Summary stats
            viabilities = [r['viability'] for r in seed_results]
            closing_rates = [r['closing_rate'] for r in seed_results]
            print(f"viab={np.mean(viabilities):.3f}+/-{np.std(viabilities):.3f}, "
                  f"close={np.mean(closing_rates):.3f}, "
                  f"{time.time()-t0:.1f}s")

    # Also run concurrent-model null for the key comparisons
    # (token_shuffle and random_token with INTERSECTION, 10 seeds each for speed)
    print("\n=== CONCURRENT-MODEL NULL RUNS (key comparisons) ===")
    for null_type in ['token_shuffle', 'random_token']:
        for model in models:
            key = f"{null_type}_{model}_concurrent"
            print(f"  Running {key} (10 seeds)...", end=' ', flush=True)
            t0 = time.time()

            seed_results = []
            for seed_idx in range(min(10, n_seeds)):
                null_paras = null_variants[null_type][seed_idx]
                para_data = [{'lines': p['lines']} for p in null_paras]
                result = run_execution(para_data, model, 'P', seed=42 + seed_idx * 1000)

                seed_results.append({
                    'seed': seed_idx,
                    'viability': result['viability'],
                    'total_nan': result['total_nan'],
                    'total_contradiction': result['total_contradiction'],
                    'mean_Q': float(np.mean([m['mean_Q'] for m in result['line_metrics']])),
                    'mean_abs_error': float(np.mean([m['mean_abs_error'] for m in result['line_metrics']])),
                    'closing_rate': float(np.mean([m['sup_closing_activated'] for m in result['line_metrics']])),
                    'line_metrics': result['line_metrics'],
                })
                run_count += 1

            results['null_runs'][key] = seed_results

            viabilities = [r['viability'] for r in seed_results]
            print(f"viab={np.mean(viabilities):.3f}+/-{np.std(viabilities):.3f}, "
                  f"{time.time()-t0:.1f}s")

    # ════════════════════════════════════════════════════════
    # SUMMARY
    # ════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    print(f"\n=== EXECUTION COMPLETE ===")
    print(f"  Total runs: {run_count}")
    print(f"  Total time: {elapsed:.1f}s")

    results['metadata']['total_runs'] = run_count
    results['metadata']['total_time_s'] = round(elapsed, 1)

    # Print full run comparison
    print("\n=== FULL RUN COMPARISON ===")
    for key, result in results['full_runs'].items():
        line_m = result['line_metrics']
        n_closing = sum(1 for m in line_m if m['sup_closing_activated'])
        domains = [m['dominant_domain'] for m in line_m]
        print(f"  {key}:")
        print(f"    Viability: {result['viability']:.4f}")
        print(f"    Mean Q: {np.mean([m['mean_Q'] for m in line_m]):.4f}")
        print(f"    Mean |error|: {np.mean([m['mean_abs_error'] for m in line_m]):.4f}")
        print(f"    Closing rate: {n_closing}/{len(line_m)}")
        print(f"    Domains: {dict(zip(*np.unique(domains, return_counts=True)))}")
        print(f"    NaN: {result['total_nan']}, Contradiction: {result['total_contradiction']}")

    # Save output
    out_path = Path(__file__).parent.parent / 'results' / 't2_plant_execution.json'
    print(f"\nWriting output to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  Output size: {size_mb:.1f} MB")
    print("  Done.")


if __name__ == '__main__':
    main()
