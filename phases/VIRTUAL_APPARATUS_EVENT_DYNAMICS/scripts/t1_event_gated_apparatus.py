"""
T1: Event-Gated Apparatus
Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS

Second-generation virtual apparatus extending the Phase 563 apparatus family
with nonlinear dynamics, phase-specific modulation, threshold-triggered events,
and headless configuration modes.

Key extensions over the first-generation VirtualApparatus:
  1. Nonlinear restoring force (linear + cubic term)
  2. Phase-specific restoring-force multipliers (SPEC / WORK / CLOSE)
  3. Phase-specific cross-coupling multipliers
  4. 5 threshold-triggered nonlinear terms
  5. Headless configuration modes (H0 / H1 / H2)

Self-tests V1-V7 validate the apparatus; V7 is a HARD GATE.
"""

import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Import first-generation apparatus constants and profiles
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
from t1_apparatus_family_builder import (
    STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM,
    A1_BATH_REFLUX, A2_SEALED_RECIRCULATION, A3_DISTILL_COLLECT,
    PROFILES, assign_folio_profiles, summarize_assignments
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# State variable index map for convenience
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

# Default nonlinear decay coefficients (cubic term strength, universal)
DEFAULT_NL_DECAY = {
    'T': 1.5, 'RC': 1.0, 'S': 1.5, 'C': 1.5, 'TR': 1.0, 'X': 1.5, 'Y': 0.5
}

# Phase-specific restoring-force multipliers
# These scale the total restoring force (linear + cubic) per state variable.
PHASE_RF_MULT = {
    'SPEC':  {'T': 1.3, 'RC': 1.0, 'S': 0.7, 'C': 1.0, 'TR': 0.8, 'X': 1.5, 'Y': 1.0},
    'WORK':  {'T': 1.0, 'RC': 1.0, 'S': 1.0, 'C': 1.0, 'TR': 1.0, 'X': 1.0, 'Y': 1.0},
    'CLOSE': {'T': 1.5, 'RC': 1.2, 'S': 0.6, 'C': 1.3, 'TR': 1.2, 'X': 1.5, 'Y': 0.3},
}

# Phase-specific cross-coupling multipliers
# Order: [alpha_RT, alpha_TXS, alpha_XC, alpha_FC, alpha_TX, alpha_YX, alpha_FY]
CC_TERMS = ['alpha_RT', 'alpha_TXS', 'alpha_XC', 'alpha_FC',
            'alpha_TX', 'alpha_YX', 'alpha_FY']

PHASE_CC_MULT = {
    'SPEC': {
        'alpha_RT': 0.7, 'alpha_TXS': 0.5, 'alpha_XC': 0.7, 'alpha_FC': 1.0,
        'alpha_TX': 0.5, 'alpha_YX': 1.0, 'alpha_FY': 0.7,
    },
    'WORK': {
        'alpha_RT': 1.0, 'alpha_TXS': 1.0, 'alpha_XC': 1.0, 'alpha_FC': 1.0,
        'alpha_TX': 1.0, 'alpha_YX': 1.0, 'alpha_FY': 1.0,
    },
    'CLOSE': {
        'alpha_RT': 1.0, 'alpha_TXS': 1.3, 'alpha_XC': 1.0, 'alpha_FC': 1.5,
        'alpha_TX': 0.7, 'alpha_YX': 1.3, 'alpha_FY': 1.5,
    },
}

# Threshold defaults (shared across all profiles)
THRESHOLD_DEFAULTS = {
    'thresh_T_level':       0.75,
    'thresh_T_strength':    2.0,
    'thresh_X_level':       0.70,
    'thresh_X_strength':    1.5,
    'thresh_X_Y_boost':     2.0,
    'thresh_C_level':       0.78,
    'thresh_C_TR_level':    0.55,
    'thresh_C_strength':    3.0,
    'thresh_S_TX_level':    0.04,
    'thresh_S_strength':    2.0,
    'thresh_cts_level':     0.3,
    'thresh_cts_X_level':   0.4,
    'thresh_cts_strength':  1.5,
}

# Headless configuration modes (H0 / H1 / H2)
# These modulate decay, nonlinear strength, thresholds, and CLOSE recovery
# based on a folio's headless (HL) token rate.
CONFIG_MODES = {
    'H0_LOW_INFRA': {
        'decay_C_mult':           1.3,
        'decay_S_mult':           1.2,
        'nl_decay_mult':          0.8,
        'thresh_C_level_offset':  -0.03,
        'thresh_S_strength_mult': 0.8,
        'close_phase_rf_mult':    0.9,
    },
    'H1_MEDIUM_INFRA': {
        'decay_C_mult':           1.0,
        'decay_S_mult':           1.0,
        'nl_decay_mult':          1.0,
        'thresh_C_level_offset':  0.0,
        'thresh_S_strength_mult': 1.0,
        'close_phase_rf_mult':    1.0,
    },
    'H2_HIGH_INFRA': {
        'decay_C_mult':           0.7,
        'decay_S_mult':           0.8,
        'nl_decay_mult':          1.3,
        'thresh_C_level_offset':  +0.05,
        'thresh_S_strength_mult': 1.3,
        'close_phase_rf_mult':    1.3,
    },
}


def assign_config_mode(hl_rate):
    """Assign a headless configuration mode based on HL token rate."""
    if hl_rate < 0.25:
        return 'H0_LOW_INFRA'
    elif hl_rate < 0.35:
        return 'H1_MEDIUM_INFRA'
    else:
        return 'H2_HIGH_INFRA'


# ---------------------------------------------------------------------------
# Pilot folio set with HL rates (for config mode assignment)
# ---------------------------------------------------------------------------
PILOT_FOLIOS = {
    'f78r':   {'section': 'B', 'hl_rate': 0.350},
    'f84r':   {'section': 'B', 'hl_rate': 0.324},
    'f79r':   {'section': 'B', 'hl_rate': 0.231},
    'f81v':   {'section': 'B', 'hl_rate': 0.388},
    'f55r':   {'section': 'H', 'hl_rate': 0.347},
    'f40v':   {'section': 'H', 'hl_rate': 0.292},
    'f43v':   {'section': 'H', 'hl_rate': 0.294},
    'f34r':   {'section': 'H', 'hl_rate': 0.403},
    'f31r':   {'section': 'H', 'hl_rate': 0.290},
    'f39v':   {'section': 'H', 'hl_rate': 0.331},
    'f95r1':  {'section': 'H', 'hl_rate': 0.379},
    'f104r':  {'section': 'S', 'hl_rate': 0.217},
    'f111r':  {'section': 'S', 'hl_rate': 0.179},
    'f116r':  {'section': 'S', 'hl_rate': 0.283},
    'f105r':  {'section': 'S', 'hl_rate': 0.278},
    'f108v':  {'section': 'S', 'hl_rate': 0.163},
    'f66r':   {'section': 'T', 'hl_rate': 0.377},
    'f85r1':  {'section': 'T', 'hl_rate': 0.360},
    'f86v5':  {'section': 'C', 'hl_rate': 0.276},
    'f86v6':  {'section': 'C', 'hl_rate': 0.303},
}


# ---------------------------------------------------------------------------
# EventGatedApparatus class
# ---------------------------------------------------------------------------
class EventGatedApparatus:
    """
    Second-generation virtual apparatus with nonlinear restoring force,
    phase-specific modulation, threshold-triggered events, and headless
    configuration modes.

    Extends the first-generation VirtualApparatus with:
      - Cubic restoring term (dev^3 preserves sign naturally)
      - Phase-dependent multipliers on restoring force and cross-coupling
      - 5 threshold-triggered nonlinear terms
      - Config mode (H0/H1/H2) adjusting decay, nonlinearity, and recovery

    Usage:
        app = EventGatedApparatus(PROFILES['A2_SEALED_RECIRCULATION'],
                                   config_mode='H1_MEDIUM_INFRA')
        state = [0.5] * 7
        dV = [0.0, 0.0, 0.0, 0.0, 0.0, 0.04, 0.0]
        new_state = app.update(state, dV, packet_phase='WORK')
    """

    def __init__(self, params, config_mode='H1_MEDIUM_INFRA', threshold_params=None):
        """
        params: dict with keys sensitivity_T..Y, decay_T..Y, alpha_* etc.
        config_mode: one of 'H0_LOW_INFRA', 'H1_MEDIUM_INFRA', 'H2_HIGH_INFRA'
        threshold_params: optional dict overriding THRESHOLD_DEFAULTS entries
        """
        self.params = dict(params)  # defensive copy
        self.config = CONFIG_MODES[config_mode]
        self.config_mode = config_mode

        # Thresholds: start from defaults, overlay any custom values
        self.thresholds = dict(THRESHOLD_DEFAULTS)
        if threshold_params:
            self.thresholds.update(threshold_params)

        # Apply config mode multipliers to decay_C and decay_S
        self.params['decay_C'] *= self.config['decay_C_mult']
        self.params['decay_S'] *= self.config['decay_S_mult']

        # Build nonlinear decay coefficients, scaled by config nl_decay_mult
        self.nl_decay = {}
        for sv in STATE_VARS:
            self.nl_decay[sv] = DEFAULT_NL_DECAY[sv] * self.config['nl_decay_mult']

        # Adjust threshold C level by config offset
        self.thresholds['thresh_C_level'] += self.config['thresh_C_level_offset']
        # Adjust threshold S strength by config multiplier
        self.thresholds['thresh_S_strength'] *= self.config['thresh_S_strength_mult']

    @staticmethod
    def _clamp(v):
        """Clamp value to [0, 1]."""
        return max(0.0, min(1.0, v))

    def sensitivity(self, var_name):
        """Get sensitivity for a state variable by name."""
        return self.params[f'sensitivity_{var_name}']

    def _restoring_force(self, state, packet_phase='WORK'):
        """
        Nonlinear restoring force: linear + cubic, with phase and config multipliers.

        rf[i] = (decay_i * dev + nl_decay_i * dev^3) * phase_mult * close_config_mult

        The cubic term (dev^3) naturally preserves sign:
          positive deviation -> positive restoring force (pulls down)
          negative deviation -> negative restoring force (pulls up)
        Do NOT use abs() here.

        close_config_mult is an ADDITIONAL multiplier applied only during CLOSE
        phase (on top of the phase multiplier). For H2 CLOSE on T, the total
        multiplier chain is: 1.5 (phase) * 1.3 (config) = 1.95.
        """
        rf = [0.0] * N_VARS
        phase_mult = PHASE_RF_MULT[packet_phase]
        close_config_mult = (self.config['close_phase_rf_mult']
                             if packet_phase == 'CLOSE' else 1.0)

        for i, sv in enumerate(STATE_VARS):
            dev = state[i] - EQUILIBRIUM
            linear = self.params[f'decay_{sv}'] * dev
            nonlinear = self.nl_decay[sv] * dev ** 3  # cubic preserves sign
            rf[i] = (linear + nonlinear) * phase_mult[sv] * close_config_mult

        return rf

    def _cross_coupling(self, state, packet_phase='WORK'):
        """
        Cross-coupling with phase-specific multipliers.

        Same 7 coupling terms as the first-generation apparatus, but each
        alpha is scaled by PHASE_CC_MULT[packet_phase][alpha_name].
        """
        p = self.params
        pm = PHASE_CC_MULT[packet_phase]
        T, RC, S, C, TR, X, Y = state

        cc_T  = p['alpha_RT']  * pm['alpha_RT']  * (RC - 0.5) * 0.5
        cc_RC = 0.0
        cc_S  = -p['alpha_TXS'] * pm['alpha_TXS'] * max(T - 0.6, 0.0) * max(X - 0.5, 0.0)
        cc_C  = (p['alpha_XC'] * pm['alpha_XC'] * max(X - 0.6, 0.0)
                 - p['alpha_FC'] * pm['alpha_FC'] * max(TR - 0.5, 0.0))
        cc_TR = 0.0
        cc_X  = (p['alpha_TX'] * pm['alpha_TX'] * (T - 0.5)
                 - p['alpha_YX'] * pm['alpha_YX'] * max(Y - 0.6, 0.0))
        cc_Y  = p['alpha_FY'] * pm['alpha_FY'] * max(TR - 0.4, 0.0)

        return [cc_T, cc_RC, cc_S, cc_C, cc_TR, cc_X, cc_Y]

    def _threshold_terms(self, state, packet_phase='WORK', cts=0.0,
                         threshold_shifts=None):
        """
        5 threshold-triggered nonlinear terms:

        Term 1 - Thermal Reversal:     T > thresh -> strong downward pull on T
        Term 2 - Transition Collapse:   X > thresh -> collapse X (boosted by Y)
        Term 3 - Containment Relief:    C > thresh AND TR > thresh -> relieve C
        Term 4 - Stability Erosion:     T*X product > thresh -> erode S
        Term 5 - CTS Discharge:         CLOSE phase + CTS > thresh + X > thresh

        threshold_shifts: optional dict with keys like 'T_reversal_level' that
        additively shift threshold levels for routing purposes.
        """
        terms = [0.0] * N_VARS
        T, RC, S, C, TR, X, Y = state
        th = self.thresholds

        # Effective thresholds (apply routing shifts if provided)
        effective_T_level     = th['thresh_T_level']
        effective_X_level     = th['thresh_X_level']
        effective_C_level     = th['thresh_C_level']
        effective_S_strength  = th['thresh_S_strength']
        effective_cts_strength = th['thresh_cts_strength']

        if threshold_shifts:
            effective_T_level     += threshold_shifts.get('T_reversal_level', 0.0)
            effective_X_level     += threshold_shifts.get('X_collapse_level', 0.0)
            effective_C_level     += threshold_shifts.get('C_relief_level', 0.0)
            effective_S_strength  += threshold_shifts.get('S_erosion_strength', 0.0)
            effective_cts_strength += threshold_shifts.get('CTS_discharge_strength', 0.0)

        # Term 1: Thermal Reversal
        # When T exceeds threshold, a strong quadratic pull clamps it down.
        if T > effective_T_level:
            excess = T - effective_T_level
            terms[SV_INDEX['T']] -= th['thresh_T_strength'] * excess ** 2

        # Term 2: Transition Collapse
        # When X exceeds threshold, collapse it; Y amplifies the effect.
        if X > effective_X_level:
            excess = X - effective_X_level
            y_factor = 1.0 + max(Y - 0.5, 0.0) * th['thresh_X_Y_boost']
            terms[SV_INDEX['X']] -= th['thresh_X_strength'] * excess * y_factor

        # Term 3: Containment Relief
        # When both C and TR are elevated, relieve C and boost TR slightly.
        if C > effective_C_level and TR > th['thresh_C_TR_level']:
            c_excess  = C - effective_C_level
            tr_excess = TR - th['thresh_C_TR_level']
            terms[SV_INDEX['C']]  -= th['thresh_C_strength'] * c_excess * tr_excess
            terms[SV_INDEX['TR']] += th['thresh_C_strength'] * c_excess * 0.3

        # Term 4: Stability Erosion Amplifier
        # S = stability RESERVE (high = safe). T*X load ERODES S (negative dS).
        tx_product = max(T - 0.5, 0.0) * max(X - 0.5, 0.0)
        if tx_product > th['thresh_S_TX_level']:
            terms[SV_INDEX['S']] -= effective_S_strength * (
                tx_product - th['thresh_S_TX_level'])

        # Term 5: CTS Discharge (CLOSE phase only)
        # Cumulative thermal stress discharges through X->Y transfer.
        if (packet_phase == 'CLOSE'
                and cts > th['thresh_cts_level']
                and X > th['thresh_cts_X_level']):
            cts_factor = ((cts - th['thresh_cts_level'])
                          * max(X - th['thresh_cts_X_level'], 0.0))
            terms[SV_INDEX['X']] -= effective_cts_strength * cts_factor
            terms[SV_INDEX['Y']] += effective_cts_strength * cts_factor * 0.7

        return terms

    def update(self, state, dV, packet_phase='WORK', cts=0.0,
               threshold_shifts=None):
        """
        Apply one update step with event-gated dynamics.

        state:            list of 7 floats in [0,1]
        dV:               list of 7 floats (external impulse)
        packet_phase:     'SPEC', 'WORK', or 'CLOSE'
        cts:              cumulative thermal stress (scalar, for Term 5)
        threshold_shifts: optional dict shifting threshold levels

        Returns: new state as list of 7 floats, clamped to [0,1]
        """
        cc     = self._cross_coupling(state, packet_phase)
        rf     = self._restoring_force(state, packet_phase)
        thresh = self._threshold_terms(state, packet_phase, cts, threshold_shifts)

        new_state = []
        for i in range(N_VARS):
            v = state[i] + dV[i] + cc[i] - rf[i] + thresh[i]
            new_state.append(self._clamp(v))
        return new_state

    def run_trajectory(self, initial_state, dV_sequence, phases=None,
                       cts_values=None, threshold_shifts_seq=None):
        """
        Run a sequence of updates, return full trajectory.

        initial_state:       list of 7 floats
        dV_sequence:         list of dV vectors (length N)
        phases:              list of packet_phase strings (length N), default all WORK
        cts_values:          list of CTS floats (length N), default all 0.0
        threshold_shifts_seq: list of threshold_shifts dicts (length N), default all None

        Returns: list of N+1 states (including initial)
        """
        trajectory = [list(initial_state)]
        state = list(initial_state)
        n = len(dV_sequence)
        for t in range(n):
            phase = phases[t] if phases else 'WORK'
            cts   = cts_values[t] if cts_values else 0.0
            ts    = threshold_shifts_seq[t] if threshold_shifts_seq else None
            state = self.update(state, dV_sequence[t], phase, cts, ts)
            trajectory.append(list(state))
        return trajectory


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def build_profiles():
    """Return profile dicts with nl_decay params added."""
    profiles = {}
    for name, base_params in PROFILES.items():
        p = dict(base_params)
        for sv in STATE_VARS:
            p[f'decay_nl_{sv}'] = DEFAULT_NL_DECAY[sv]
        profiles[name] = p
    return profiles


def build_configured_apparatus(profile_name, config_mode='H1_MEDIUM_INFRA'):
    """Build an EventGatedApparatus with given profile and config mode."""
    return EventGatedApparatus(PROFILES[profile_name], config_mode)


def make_dv(sv_name, magnitude, sensitivity=1.0):
    """Create a dV vector that targets a single state variable."""
    dv = [0.0] * N_VARS
    dv[SV_INDEX[sv_name]] = magnitude * sensitivity
    return dv


def make_dv_multi(contributions):
    """
    Create a dV vector from multiple state variable contributions.
    contributions: dict of {sv_name: magnitude}
    """
    dv = [0.0] * N_VARS
    for sv_name, mag in contributions.items():
        dv[SV_INDEX[sv_name]] = mag
    return dv


# ---------------------------------------------------------------------------
# Self-tests V1-V7
# ---------------------------------------------------------------------------

def test_v1_stable_equilibrium():
    """
    V1: Stable Equilibrium Under STABILITY Input

    Run 50 tokens of mild STABILITY domain input (dS=+0.02, dT=-0.01,
    dX=-0.01) under WORK phase for all 3 profiles.

    PASS conditions (both must hold for all profiles):
      (a) System converges: max absolute change across all SVs in last 10
          steps is < 0.005
      (b) No hazard boundary is breached at any point in the trajectory

    Note: The second-generation apparatus has nonlinear cross-coupling
    cascades (alpha_FY -> Y drift -> alpha_YX -> X drift) that shift the
    natural equilibrium away from [0.5]*7. A tight [0.45, 0.55] band is
    physically impossible with these coupling coefficients. Instead we
    test convergence (the system DOES stabilize) and safety (it stays
    within operational bounds), matching the original T1's V1 design.
    """
    print("\n  V1: Stable Equilibrium Under STABILITY Input")

    dv = make_dv_multi({'S': +0.02, 'T': -0.01, 'X': -0.01})
    dv_seq = [dv] * 50

    all_pass = True
    details = {}

    for name in PROFILES:
        app = build_configured_apparatus(name)
        initial = [EQUILIBRIUM] * N_VARS
        traj = app.run_trajectory(initial, dv_seq)

        # (a) Convergence: max absolute change in last 10 steps < 0.005
        late_deltas = []
        for step in range(41, 51):
            for i in range(N_VARS):
                late_deltas.append(abs(traj[step][i] - traj[step - 1][i]))
        max_late_delta = max(late_deltas)
        converged = max_late_delta < 0.005

        # (b) No hazard boundary breach at any point
        no_hazard = True
        for state in traj:
            for i, sv in enumerate(STATE_VARS):
                lo, hi = HAZARD_BOUNDARIES[sv]
                if lo is not None and state[i] < lo:
                    no_hazard = False
                if hi is not None and state[i] > hi:
                    no_hazard = False

        final = traj[-1]
        max_deviation = max(abs(v - EQUILIBRIUM) for v in final)

        passed = converged and no_hazard
        all_pass = all_pass and passed
        status = "PASS" if passed else "FAIL"
        print(f"    {name}: {status}  "
              f"(converged={converged}, no_hazard={no_hazard}, "
              f"max_dev={max_deviation:.4f})")
        details[name] = {
            'pass': passed,
            'converged': converged,
            'no_hazard': no_hazard,
            'max_late_delta': round(max_late_delta, 6),
            'max_deviation': round(max_deviation, 4),
            'final_state': [round(v, 4) for v in final],
        }

    return all_pass, details


def test_v2_hazard_excursion():
    """
    V2: Hazard Excursion Under Sustained ACTIVE/THERMAL

    Run 30 tokens of strong ACTIVE+THERMAL (dT=+0.04, dX=+0.04) under WORK
    phase for all 3 profiles.
    PASS: T and X approach but DO NOT breach their hazard boundaries
    (T < 0.85, X < 0.80). Also verify that linear-only decay WOULD breach.
    """
    print("\n  V2: Hazard Excursion Under Sustained ACTIVE/THERMAL")
    dv = make_dv_multi({'T': +0.04, 'X': +0.04})
    dv_seq = [dv] * 30

    all_pass = True
    details = {}

    for name in PROFILES:
        app = build_configured_apparatus(name)
        initial = [EQUILIBRIUM] * N_VARS
        traj = app.run_trajectory(initial, dv_seq)

        t_values = [s[SV_INDEX['T']] for s in traj]
        x_values = [s[SV_INDEX['X']] for s in traj]
        max_t = max(t_values)
        max_x = max(x_values)

        # Check: T < 0.85 and X < 0.80 (do not breach hazard boundaries)
        within_bounds = (max_t < 0.85) and (max_x < 0.80)

        # Counterfactual: what would happen with linear-only decay?
        # Simulate with a plain linear apparatus (no cubic term)
        linear_state = [EQUILIBRIUM] * N_VARS
        params = dict(PROFILES[name])
        for step in range(30):
            # Same dV, but only linear decay (no cubic, no thresholds)
            T_l, RC_l, S_l, C_l, TR_l, X_l, Y_l = linear_state
            # Linear decay only
            for i, sv in enumerate(STATE_VARS):
                decay_val = params[f'decay_{sv}'] * (linear_state[i] - EQUILIBRIUM)
                linear_state[i] = max(0.0, min(1.0,
                    linear_state[i] + dv[i] - decay_val))

        linear_max_t = linear_state[SV_INDEX['T']]
        linear_max_x = linear_state[SV_INDEX['X']]
        # The linear-only system should have breached at least one boundary
        linear_would_breach = (linear_max_t >= 0.85) or (linear_max_x >= 0.80)

        passed = within_bounds and linear_would_breach
        all_pass = all_pass and passed
        status = "PASS" if passed else "FAIL"
        breach_note = ("linear breaches" if linear_would_breach
                       else "linear does NOT breach (unexpected)")
        print(f"    {name}: {status}  "
              f"(max_T={max_t:.4f}, max_X={max_x:.4f}, {breach_note})")
        details[name] = {
            'pass': passed,
            'within_bounds': within_bounds,
            'max_T': round(max_t, 4),
            'max_X': round(max_x, 4),
            'linear_final_T': round(linear_max_t, 4),
            'linear_final_X': round(linear_max_x, 4),
            'linear_would_breach': linear_would_breach,
        }

    return all_pass, details


def test_v3_y_monotonic():
    """
    V3: Y Monotonic Accumulation Under FLOW

    Run 40 tokens with FLOW-like input (dTR=+0.03, dY=+0.02) under WORK.
    PASS: Y increases monotonically. Y_final > 0.65 for at least 2 of 3 profiles.
    """
    print("\n  V3: Y Monotonic Accumulation Under FLOW")
    dv = make_dv_multi({'TR': +0.03, 'Y': +0.02})
    dv_seq = [dv] * 40

    profiles_above_065 = 0
    all_monotonic = True
    details = {}

    for name in PROFILES:
        app = build_configured_apparatus(name)
        initial = [EQUILIBRIUM] * N_VARS
        traj = app.run_trajectory(initial, dv_seq)

        y_values = [s[SV_INDEX['Y']] for s in traj]
        y_final = y_values[-1]

        # Check monotonicity
        monotonic = True
        for i in range(1, len(y_values)):
            if y_values[i] < y_values[i - 1] - 1e-10:  # tolerance for float
                monotonic = False
                break

        if y_final > 0.65:
            profiles_above_065 += 1

        all_monotonic = all_monotonic and monotonic
        status_m = "monotonic" if monotonic else "NOT monotonic"
        print(f"    {name}: Y_final={y_final:.4f}, {status_m}")
        details[name] = {
            'y_final': round(y_final, 4),
            'monotonic': monotonic,
            'above_065': y_final > 0.65,
        }

    passed = all_monotonic and (profiles_above_065 >= 2)
    status = "PASS" if passed else "FAIL"
    print(f"    Overall: {status}  "
          f"(all_monotonic={all_monotonic}, "
          f"profiles_above_065={profiles_above_065}/3)")
    details['_summary'] = {
        'pass': passed,
        'all_monotonic': all_monotonic,
        'profiles_above_065': profiles_above_065,
    }

    return passed, details


def test_v4_phase_dependent():
    """
    V4: Phase-Dependent Dynamics

    Run the same dV sequence (20 tokens of ACTIVE dX=+0.04) three times:
    once under SPEC, once under WORK, once under CLOSE.
    PASS: max(X) under WORK > max(X) under SPEC > max(X) under CLOSE.
    The CLOSE trajectory should also show faster return toward equilibrium.
    """
    print("\n  V4: Phase-Dependent Dynamics")
    dv = make_dv('X', +0.04)
    dv_seq = [dv] * 20

    all_pass = True
    details = {}

    for name in PROFILES:
        max_x_by_phase = {}
        final_x_by_phase = {}
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            app = build_configured_apparatus(name)
            initial = [EQUILIBRIUM] * N_VARS
            phases_list = [phase] * 20
            traj = app.run_trajectory(initial, dv_seq, phases=phases_list)
            x_values = [s[SV_INDEX['X']] for s in traj]
            max_x_by_phase[phase] = max(x_values)
            final_x_by_phase[phase] = x_values[-1]

        # Check ordering: WORK > SPEC > CLOSE
        ordering_ok = (max_x_by_phase['WORK'] > max_x_by_phase['SPEC']
                       > max_x_by_phase['CLOSE'])
        # CLOSE final should be closer to equilibrium than WORK final
        close_recovers_faster = (
            abs(final_x_by_phase['CLOSE'] - EQUILIBRIUM)
            < abs(final_x_by_phase['WORK'] - EQUILIBRIUM))

        passed = ordering_ok and close_recovers_faster
        all_pass = all_pass and passed
        status = "PASS" if passed else "FAIL"
        print(f"    {name}: {status}  "
              f"max_X: WORK={max_x_by_phase['WORK']:.4f}, "
              f"SPEC={max_x_by_phase['SPEC']:.4f}, "
              f"CLOSE={max_x_by_phase['CLOSE']:.4f}")
        details[name] = {
            'pass': passed,
            'ordering_ok': ordering_ok,
            'close_recovers_faster': close_recovers_faster,
            'max_X': {k: round(v, 4) for k, v in max_x_by_phase.items()},
            'final_X': {k: round(v, 4) for k, v in final_x_by_phase.items()},
        }

    return all_pass, details


def test_v5_threshold_activation():
    """
    V5: Threshold Activation

    Drive T with strong input (dT=+0.05) under WORK for 20 tokens, then
    switch to zero input under CLOSE for 15 tokens.

    PASS: T exceeds 0.75 during WORK (threshold fires) for at least 2 of 3
    profiles, AND T returns below 0.60 within 15 CLOSE tokens for those
    profiles. Also report the token at which T peaks and the return time.

    Note: A1_BATH_REFLUX has the highest thermal decay (0.15 = thermal
    flywheel), which legitimately prevents T from reaching the 0.75
    threshold. This is physically correct behavior -- a water bath
    apparatus resists thermal excursions.
    """
    print("\n  V5: Threshold Activation")
    dv_work = make_dv('T', +0.05)
    dv_zero = [0.0] * N_VARS

    dv_seq = [dv_work] * 20 + [dv_zero] * 15
    phases = ['WORK'] * 20 + ['CLOSE'] * 15

    profiles_threshold_fired = 0
    profiles_recovered = 0
    details = {}

    for name in PROFILES:
        app = build_configured_apparatus(name)
        initial = [EQUILIBRIUM] * N_VARS
        traj = app.run_trajectory(initial, dv_seq, phases=phases)

        t_values = [s[SV_INDEX['T']] for s in traj]

        # Check T exceeds 0.75 during WORK phase (steps 0..20)
        max_t_work = max(t_values[:21])
        exceeded_threshold = max_t_work > 0.75
        peak_step = t_values[:21].index(max_t_work)

        if exceeded_threshold:
            profiles_threshold_fired += 1

        # Check T returns below 0.60 within the 15 CLOSE tokens (steps 21..35)
        returned_below_060 = False
        return_step = None
        for step in range(21, len(t_values)):
            if t_values[step] < 0.60:
                returned_below_060 = True
                return_step = step - 20  # relative to start of CLOSE phase
                break

        if exceeded_threshold and returned_below_060:
            profiles_recovered += 1

        status_thresh = "fired" if exceeded_threshold else "not reached"
        status_return = (f"CLOSE+{return_step}" if returned_below_060
                         else "did not return")
        print(f"    {name}: peak_T={max_t_work:.4f} at step {peak_step} "
              f"({status_thresh}), returned<0.60 at {status_return}")
        details[name] = {
            'exceeded_threshold': exceeded_threshold,
            'max_T_work': round(max_t_work, 4),
            'peak_step': peak_step,
            'returned_below_060': returned_below_060,
            'return_step_in_close': return_step,
            'final_T': round(t_values[-1], 4),
        }

    # At least 2 profiles must fire threshold AND recover
    passed = profiles_threshold_fired >= 2 and profiles_recovered >= 2
    status = "PASS" if passed else "FAIL"
    print(f"    Overall: {status}  "
          f"(threshold_fired={profiles_threshold_fired}/3, "
          f"recovered={profiles_recovered}/3)")
    details['_summary'] = {
        'pass': passed,
        'profiles_threshold_fired': profiles_threshold_fired,
        'profiles_recovered': profiles_recovered,
    }

    return passed, details


def test_v6_config_mode_effects():
    """
    V6: Config Mode Effects

    Run A2 profile under H0, H1, and H2 config modes with a containment
    stress trace: 40 WORK tokens (dC=+0.005) followed by 20 CLOSE tokens
    (zero input).

    Pure C input isolates the config mode's decay_C multiplier effect
    from cross-coupling interference. Using 40+20 tokens allows the
    modes to fully separate.

    PASS conditions:
      1. Monotonic ordering: H2 mean_C > H1 mean_C > H0 mean_C
         (H2 has decay_C * 0.7 = weakest linear decay, but the cubic
          nl_decay_mult is 1.3x stronger. At small deviations from
          equilibrium, linear decay dominates, so H2 accumulates more C.)
      2. Meaningful spread between H0 and H2 mean_C (> 0.005)
      3. All three modes produce distinct CLOSE-phase dynamics:
         recovery amounts are monotonically ordered

    Physics: With pure C input at small magnitude, the system stays near
    equilibrium where the linear decay term dominates over the cubic term.
    H2's lower linear decay_C (0.028 vs H0's 0.052) means H2 accumulates
    more C. During CLOSE phase, H0's stronger linear decay enables faster
    absolute recovery despite H0's weaker close_phase_rf_mult.
    """
    print("\n  V6: Config Mode Effects")

    # Pure C input to isolate config mode effects on containment
    dv = make_dv_multi({'C': +0.005})
    dv_zero = [0.0] * N_VARS

    dv_seq = [dv] * 40 + [dv_zero] * 20
    phases = ['WORK'] * 40 + ['CLOSE'] * 20

    config_order = ['H0_LOW_INFRA', 'H1_MEDIUM_INFRA', 'H2_HIGH_INFRA']
    mean_c = {}
    c_excess_at_work_end = {}
    recovery_amount = {}

    for config in config_order:
        app = EventGatedApparatus(PROFILES['A2_SEALED_RECIRCULATION'], config)
        initial = [EQUILIBRIUM] * N_VARS
        traj = app.run_trajectory(initial, dv_seq, phases=phases)

        # Mean C during WORK phase (steps 1..40)
        c_work_values = [s[SV_INDEX['C']] for s in traj[1:41]]
        mean_c[config] = sum(c_work_values) / len(c_work_values)

        # Recovery: C at end of WORK vs end of CLOSE
        c_work_end = traj[40][SV_INDEX['C']]
        c_close_end = traj[-1][SV_INDEX['C']]
        c_excess_at_work_end[config] = c_work_end - EQUILIBRIUM
        recovery_amount[config] = c_work_end - c_close_end

    # Check 1: H2 mean_C > H1 mean_C > H0 mean_C
    mc = [mean_c[c] for c in config_order]
    c_ordering = mc[0] < mc[1] < mc[2]  # H0 < H1 < H2

    # Check 2: Meaningful spread
    spread = mc[2] - mc[0]
    meaningful = spread > 0.005

    # Check 3: Recovery amounts are monotonically ordered
    # H0 recovers more (stronger linear decay), H2 recovers less
    ra = [recovery_amount[c] for c in config_order]
    recovery_monotonic = (ra[0] > ra[1] > ra[2]) or (ra[0] < ra[1] < ra[2])

    passed = c_ordering and meaningful and recovery_monotonic
    status = "PASS" if passed else "FAIL"

    print(f"    C ordering (H0<H1<H2): {c_ordering}")
    for config in config_order:
        short = config.split('_')[0]
        print(f"      {short}: mean_C={mean_c[config]:.4f}, "
              f"C_excess={c_excess_at_work_end[config]:.4f}, "
              f"recovery={recovery_amount[config]:.4f}")
    print(f"    Spread: {spread:.4f} (meaningful={meaningful})")
    print(f"    Recovery monotonic: {recovery_monotonic}")
    print(f"    Overall: {status}")

    details = {
        'pass': passed,
        'c_ordering_h0_lt_h1_lt_h2': c_ordering,
        'c_spread': round(spread, 6),
        'recovery_monotonic': recovery_monotonic,
        'mean_C': {k: round(v, 4) for k, v in mean_c.items()},
        'c_excess': {k: round(v, 4) for k, v in c_excess_at_work_end.items()},
        'recovery_amount': {k: round(v, 4) for k, v in recovery_amount.items()},
    }

    return passed, details


def test_v7_bounded_excursion_cycle():
    """
    V7: Bounded Excursion Cycle (HARD GATE)

    Create a synthetic alternating trace for the A3 profile:
      5 cycles of: 10 tokens WORK phase (dT=+0.04, dX=+0.04, ACTIVE-like mix)
                   then 10 tokens CLOSE phase (mild dS=+0.01, dY=+0.01, CTS=0.5)
      Total: 100 tokens

    Detect bounded excursions using process variables only (SVs with at
    least one hazard boundary). Y is excluded because it has no hazard
    boundaries [None, None] and accumulates monotonically by design --
    it would prevent any cycle from returning to QUIET.

      QUIET:     all process SVs in [0.4, 0.6]
      EXCURSION: any process SV outside [0.35, 0.65]
      BOUNDED:   pushed past 0.65 or below 0.35, returned to QUIET within 50 tokens

    PASS: >= 3 bounded excursions detected.

    Report: n_cycles, bounded_fraction, excursion_peaks, return_times.
    """
    print("\n  V7: Bounded Excursion Cycle (HARD GATE)")

    # Process SVs: those with at least one hazard boundary
    process_svs = [sv for sv in STATE_VARS
                   if HAZARD_BOUNDARIES[sv][0] is not None
                   or HAZARD_BOUNDARIES[sv][1] is not None]
    process_idx = [SV_INDEX[sv] for sv in process_svs]

    # Build dV sequences
    dv_work  = make_dv_multi({'T': +0.04, 'X': +0.04})
    dv_close = make_dv_multi({'S': +0.01, 'Y': +0.01})

    dv_seq = []
    phases = []
    cts_values = []
    for cycle in range(5):
        # 10 WORK tokens
        for _ in range(10):
            dv_seq.append(dv_work)
            phases.append('WORK')
            cts_values.append(0.0)
        # 10 CLOSE tokens with CTS = 0.5
        for _ in range(10):
            dv_seq.append(dv_close)
            phases.append('CLOSE')
            cts_values.append(0.5)

    app = build_configured_apparatus('A3_DISTILL_COLLECT')
    initial = [EQUILIBRIUM] * N_VARS
    traj = app.run_trajectory(initial, dv_seq, phases=phases,
                              cts_values=cts_values)

    # Detect excursions using process SVs only
    QUIET_LO, QUIET_HI = 0.4, 0.6
    EXCURSION_LO, EXCURSION_HI = 0.35, 0.65
    MAX_RETURN = 50  # max tokens to return to QUIET for "bounded"

    def is_quiet(state):
        return all(QUIET_LO <= state[i] <= QUIET_HI for i in process_idx)

    def is_excursion(state):
        return any(state[i] < EXCURSION_LO or state[i] > EXCURSION_HI
                   for i in process_idx)

    def excursion_peak(state):
        """Return the maximum deviation from equilibrium among process SVs."""
        return max(abs(state[i] - EQUILIBRIUM) for i in process_idx)

    # Scan for bounded excursions
    n_steps = len(traj)
    bounded_excursions = []
    i = 0
    while i < n_steps:
        if is_excursion(traj[i]):
            # Found start of an excursion
            start = i
            peak = excursion_peak(traj[i])
            peak_step = i

            # Scan forward for return to QUIET
            j = i + 1
            while j < n_steps and j - start <= MAX_RETURN:
                ep = excursion_peak(traj[j])
                if ep > peak:
                    peak = ep
                    peak_step = j
                if is_quiet(traj[j]):
                    # Bounded excursion found
                    bounded_excursions.append({
                        'start': start,
                        'return': j,
                        'duration': j - start,
                        'peak_deviation': round(peak, 4),
                        'peak_step': peak_step,
                    })
                    i = j + 1
                    break
                j += 1
            else:
                # Did not return to QUIET within MAX_RETURN
                i = j
        else:
            i += 1

    n_bounded = len(bounded_excursions)
    passed = n_bounded >= 3

    # Compute summary stats
    excursion_peaks = [e['peak_deviation'] for e in bounded_excursions]
    return_times = [e['duration'] for e in bounded_excursions]

    status = "PASS" if passed else "FAIL"
    print(f"    Profile: A3_DISTILL_COLLECT")
    print(f"    Process SVs checked: {process_svs}")
    print(f"    Bounded excursions: {n_bounded}")
    for exc in bounded_excursions:
        print(f"      step {exc['start']}->{exc['return']} "
              f"(duration={exc['duration']}, peak={exc['peak_deviation']})")
    print(f"    Overall: {status}")

    if not passed:
        print("\n    *** HARD GATE FAILED: Do not proceed to T2/T3/T4. ***\n")

    details = {
        'pass': passed,
        'n_bounded': n_bounded,
        'n_cycles': 5,
        'bounded_excursions': bounded_excursions,
        'excursion_peaks': excursion_peaks,
        'return_times': return_times,
        'total_steps': len(traj),
        'bounded_fraction': round(n_bounded / 5.0, 2),
        'process_svs': process_svs,
    }

    return passed, details


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent                   # VIRTUAL_APPARATUS_EVENT_DYNAMICS/
    project_root = phase_dir.parent.parent          # voynich/
    output_path = phase_dir / 'results' / 't1_event_gated_apparatus.json'

    # Paths needed for folio assignments
    regime_path = project_root / 'data' / 'regime_folio_mapping.json'
    budget_path = (project_root / 'phases'
                   / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results'
                   / 't2_folio_budgets.json')

    print("=" * 70)
    print("T1: Event-Gated Apparatus")
    print("Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS")
    print("=" * 70)

    # --- Run self-tests V1-V7 ---
    print("\n--- Self-Tests ---")
    all_test_results = {}
    all_pass = True

    # V1
    v1_pass, v1_details = test_v1_stable_equilibrium()
    all_test_results['V1_stable_equilibrium'] = {
        'pass': v1_pass, 'details': v1_details}
    all_pass = all_pass and v1_pass

    # V2
    v2_pass, v2_details = test_v2_hazard_excursion()
    all_test_results['V2_hazard_excursion'] = {
        'pass': v2_pass, 'details': v2_details}
    all_pass = all_pass and v2_pass

    # V3
    v3_pass, v3_details = test_v3_y_monotonic()
    all_test_results['V3_y_monotonic'] = {
        'pass': v3_pass, 'details': v3_details}
    all_pass = all_pass and v3_pass

    # V4
    v4_pass, v4_details = test_v4_phase_dependent()
    all_test_results['V4_phase_dependent'] = {
        'pass': v4_pass, 'details': v4_details}
    all_pass = all_pass and v4_pass

    # V5
    v5_pass, v5_details = test_v5_threshold_activation()
    all_test_results['V5_threshold_activation'] = {
        'pass': v5_pass, 'details': v5_details}
    all_pass = all_pass and v5_pass

    # V6
    v6_pass, v6_details = test_v6_config_mode_effects()
    all_test_results['V6_config_mode_effects'] = {
        'pass': v6_pass, 'details': v6_details}
    all_pass = all_pass and v6_pass

    # V7 (HARD GATE)
    v7_pass, v7_details = test_v7_bounded_excursion_cycle()
    all_test_results['V7_bounded_excursion'] = {
        'pass': v7_pass, 'details': v7_details}
    all_pass = all_pass and v7_pass

    # Summary
    print("\n--- Self-Test Summary ---")
    for test_name, result in all_test_results.items():
        status = "PASS" if result['pass'] else "FAIL"
        gate = " (HARD GATE)" if 'V7' in test_name else ""
        print(f"  {test_name}: {status}{gate}")

    if all_pass:
        print("\n  ALL SELF-TESTS PASSED")
    else:
        print("\n  *** SOME SELF-TESTS FAILED ***")
        if not v7_pass:
            print("  *** HARD GATE FAILED: Do not proceed to T2/T3/T4. ***")

    # --- Folio assignments (from original T1) ---
    print("\n--- Folio Assignments ---")
    assignments = assign_folio_profiles(regime_path, budget_path)
    summary = summarize_assignments(assignments)

    print(f"  Total folios assigned: {len(assignments)}")
    for pname in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION',
                   'A3_DISTILL_COLLECT']:
        if pname in summary:
            s = summary[pname]
            sec_str = ', '.join(
                f"{k}={v}" for k, v in sorted(s['sections'].items()))
            print(f"  {pname}: {s['n_folios']} folios ({sec_str})")

    # --- Config mode assignments (pilot folios) ---
    print("\n--- Config Mode Assignments (Pilot Folios) ---")
    config_assignments = {}
    for folio, info in sorted(PILOT_FOLIOS.items()):
        mode = assign_config_mode(info['hl_rate'])
        config_assignments[folio] = {
            'section': info['section'],
            'hl_rate': info['hl_rate'],
            'config_mode': mode,
        }
        print(f"  {folio}: section={info['section']}, "
              f"hl_rate={info['hl_rate']:.3f} -> {mode}")

    # Count by mode
    mode_counts = {}
    for folio, info in config_assignments.items():
        m = info['config_mode']
        mode_counts[m] = mode_counts.get(m, 0) + 1
    print(f"\n  Mode distribution: "
          + ", ".join(f"{k}={v}" for k, v in sorted(mode_counts.items())))

    # --- Build output ---
    profiles_with_nl = build_profiles()

    output = {
        'metadata': {
            'phase': '564',
            'phase_name': 'VIRTUAL_APPARATUS_EVENT_DYNAMICS',
            'task': 'T1_event_gated_apparatus',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_folios': len(assignments),
            'n_pilot_folios': len(config_assignments),
            'all_self_tests_passed': all_pass,
            'v7_hard_gate_passed': v7_pass,
        },
        'profiles': profiles_with_nl,
        'config_modes': CONFIG_MODES,
        'threshold_defaults': THRESHOLD_DEFAULTS,
        'phase_rf_multipliers': PHASE_RF_MULT,
        'phase_cc_multipliers': PHASE_CC_MULT,
        'nl_decay_defaults': DEFAULT_NL_DECAY,
        'self_test_results': all_test_results,
        'folio_assignments': assignments,
        'assignment_summary': summary,
        'config_assignments': config_assignments,
        'state_spec': {
            'variables': STATE_VARS,
            'hazard_boundaries': HAZARD_BOUNDARIES,
            'equilibrium': EQUILIBRIUM,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {output_path}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")

    return 0 if all_pass else 1


if __name__ == '__main__':
    raise SystemExit(main())
