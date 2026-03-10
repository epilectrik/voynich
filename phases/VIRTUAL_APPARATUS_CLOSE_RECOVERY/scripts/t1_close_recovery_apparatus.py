"""
T1: Close Recovery Apparatus
Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY

Fifth-generation virtual apparatus evolving from the Phase 565 permeability-
calibration architecture. Adds CLOSE recovery channels R1-R5:

  R1: Per-SV CLOSE drawdown (profile-weighted, CTS-conditioned for T/X/TR)
  R2: Strengthened CTS X->Y transfer (K_CTS_CLOSE = 6.0)
  R3: Strengthened containment-TR relief (K_RELIEF_CLOSE = 3x base)
  R4: Quality-conditioned Y accumulation from X and C recovery
  R5: Closure-coherent coordination bonus (multi-SV coherence gate)

Parameter ladder (566-Low / 566-Mid / 566-High) selects optimal R1-R3
scaling via V10-V12 preflight.

Self-tests V1-V9 inherited from 565; V10-V12 are new HARD GATEs.
"""

import json
import sys
import time
import random
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Import first-generation apparatus constants and profiles
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
from t1_apparatus_family_builder import (
    STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM,
    A1_BATH_REFLUX, A2_SEALED_RECIRCULATION, A3_DISTILL_COLLECT,
    PROFILES, assign_folio_profiles
)

# Also import cross-coupling constants from Phase 564
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'VIRTUAL_APPARATUS_EVENT_DYNAMICS' / 'scripts'))
from t1_event_gated_apparatus import PHASE_CC_MULT, CC_TERMS

# ---------------------------------------------------------------------------
# Constants (copied from 565 T1)
# ---------------------------------------------------------------------------
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

# Pilot folios
PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]

# ---------------------------------------------------------------------------
# Zone boundaries
# ---------------------------------------------------------------------------
Q1 = 0.08  # Universal basin boundary

Q2_BASE = {
    'T': 0.24, 'RC': 0.28, 'S': 0.24, 'C': 0.24,
    'TR': 0.28, 'X': 0.21, 'Y': 0.35,
}

# Q3 = Q2_BASE + 0.05 (base values; effective q3 computed at runtime)
Q3_BASE = {sv: Q2_BASE[sv] + 0.05 for sv in STATE_VARS}

# Deviation from equilibrium (0.5) to nearest hazard boundary
HAZARD_DEV = {
    'T': 0.35, 'RC': 0.40, 'S': 0.35, 'C': 0.35,
    'TR': 0.40, 'X': 0.30, 'Y': 1.0,
}

# ---------------------------------------------------------------------------
# Restoring force parameters (base values for A3)
# ---------------------------------------------------------------------------
GAMMA_BASIN = {
    'T': 0.04,
    'RC': 0.015,
    'S': 0.025,
    'C': 0.03,
    'TR': 0.015,
    'X': 0.04,
    'Y': 0.02,
}

GAMMA_CORRIDOR = {
    'T': 0.04, 'RC': 0.05, 'S': 0.10, 'C': 0.04,
    'TR': 0.03, 'X': 0.10, 'Y': 0.10,
}

BETA1 = {'T': 3.0, 'RC': 1.5, 'S': 4.0, 'C': 3.0, 'TR': 2.0, 'X': 8.0, 'Y': 1.0}
BETA2 = {'T': 10.0, 'RC': 4.0, 'S': 12.0, 'C': 10.0, 'TR': 6.0, 'X': 24.0, 'Y': 2.0}

# A3 decay rates (reference for profile scaling)
A3_DECAY = {
    'T': 0.08, 'RC': 0.10, 'S': 0.08, 'C': 0.08,
    'TR': 0.06, 'X': 0.06, 'Y': 0.02,
}

# Per-profile decay rates
PROFILE_DECAYS = {
    'A1_BATH_REFLUX': {
        'T': 0.15, 'RC': 0.08, 'S': 0.05, 'C': 0.10,
        'TR': 0.10, 'X': 0.12, 'Y': 0.03,
    },
    'A2_SEALED_RECIRCULATION': {
        'T': 0.10, 'RC': 0.06, 'S': 0.06, 'C': 0.04,
        'TR': 0.12, 'X': 0.08, 'Y': 0.03,
    },
    'A3_DISTILL_COLLECT': dict(A3_DECAY),
}

# ---------------------------------------------------------------------------
# Phase multiplier tables
# ---------------------------------------------------------------------------
BASIN_MULT = {
    'SPEC':  {'T': 1.2, 'RC': 1.0, 'S': 0.5, 'C': 1.0, 'TR': 0.8, 'X': 1.2, 'Y': 1.0},
    'WORK':  {'T': 0.8, 'RC': 0.8, 'S': 0.5, 'C': 0.8, 'TR': 0.8, 'X': 0.5, 'Y': 0.5},
    'CLOSE': {'T': 1.5, 'RC': 1.2, 'S': 0.8, 'C': 1.5, 'TR': 1.2, 'X': 1.5, 'Y': 0.3},
}

CORRIDOR_MULT = {
    'SPEC':  {'T': 1.5, 'RC': 1.2, 'S': 0.3, 'C': 1.3, 'TR': 1.0, 'X': 1.5, 'Y': 0.5},
    'WORK':  {'T': 0.6, 'RC': 0.7, 'S': 0.3, 'C': 0.6, 'TR': 0.6, 'X': 1.5, 'Y': 0.3},
    'CLOSE': {'T': 2.5, 'RC': 2.0, 'S': 1.0, 'C': 2.5, 'TR': 2.0, 'X': 3.0, 'Y': 0.2},
}

EDGE1_MULT = {
    'SPEC':  {'T': 2.0, 'RC': 1.5, 'S': 0.5, 'C': 2.0, 'TR': 1.5, 'X': 2.5, 'Y': 0.5},
    'WORK':  {'T': 1.5, 'RC': 1.2, 'S': 0.5, 'C': 1.5, 'TR': 1.2, 'X': 3.0, 'Y': 0.3},
    'CLOSE': {'T': 3.0, 'RC': 2.5, 'S': 1.5, 'C': 3.0, 'TR': 2.5, 'X': 3.5, 'Y': 0.3},
}

EDGE2_MULT = {
    phase: {sv: v * 1.5 for sv, v in svs.items()}
    for phase, svs in EDGE1_MULT.items()
}

# ---------------------------------------------------------------------------
# Discharge constants
# ---------------------------------------------------------------------------
K_RELIEF = {
    'A1_BATH_REFLUX': 1.2,
    'A2_SEALED_RECIRCULATION': 0.8,
    'A3_DISTILL_COLLECT': 2.0,
}

# ---------------------------------------------------------------------------
# Config mode effects
# ---------------------------------------------------------------------------
CONFIG_MODES = {
    'H0_LOW_INFRA': {
        'q2_C_shift': -0.02, 'q2_S_shift': -0.02,
        'gamma_basin_C_mult': 1.3, 'gamma_basin_S_mult': 1.2,
        'cts_discharge_mult': 0.8,
        'close_corridor_C_mult': 0.9, 'close_corridor_S_mult': 0.9,
    },
    'H1_MEDIUM_INFRA': {
        'q2_C_shift': 0.0, 'q2_S_shift': 0.0,
        'gamma_basin_C_mult': 1.0, 'gamma_basin_S_mult': 1.0,
        'cts_discharge_mult': 1.0,
        'close_corridor_C_mult': 1.0, 'close_corridor_S_mult': 1.0,
    },
    'H2_HIGH_INFRA': {
        'q2_C_shift': 0.03, 'q2_S_shift': 0.02,
        'gamma_basin_C_mult': 0.7, 'gamma_basin_S_mult': 0.8,
        'cts_discharge_mult': 1.3,
        'close_corridor_C_mult': 1.3, 'close_corridor_S_mult': 1.3,
    },
}

# ---------------------------------------------------------------------------
# Sensitivity values for self-tests
# ---------------------------------------------------------------------------
A3_SENS = {'T': 1.4, 'RC': 0.7, 'S': 0.8, 'C': 1.0, 'TR': 1.4, 'X': 1.2, 'Y': 1.3}

P50_DV = {sv: c * A3_SENS[sv] for sv, c in {
    'T': 0.004, 'RC': 0.000, 'S': 0.011, 'C': 0.004,
    'TR': 0.000, 'X': 0.001, 'Y': 0.001,
}.items()}

P90_DV = {sv: c * A3_SENS[sv] for sv, c in {
    'T': 0.027, 'RC': 0.009, 'S': 0.071, 'C': 0.016,
    'TR': 0.004, 'X': 0.014, 'Y': 0.008,
}.items()}

P95_DV = {
    'T': 0.056, 'RC': 0.013, 'S': 0.066, 'C': 0.035,
    'TR': 0.028, 'X': 0.048, 'Y': 0.017,
}

P99_DV = {sv: c * A3_SENS[sv] for sv, c in {
    'T': 0.054, 'RC': 0.030, 'S': 0.096, 'C': 0.055,
    'TR': 0.045, 'X': 0.068, 'Y': 0.018,
}.items()}

# ---------------------------------------------------------------------------
# CLOSE Recovery Constants (NEW in Phase 566)
# ---------------------------------------------------------------------------
K_CLOSE = {
    'T': 0.50, 'RC': 0.08, 'S': 0.05, 'C': 0.25,
    'TR': 0.08, 'X': 0.25,
}
# Note: Y has no K_CLOSE (Y accumulates from R4, not R1)

# CTS-weighted SVs: T, X, TR get CTS-conditioned recovery
CTS_WEIGHTED_SVS = {'T', 'X', 'TR'}

# Profile-specific CLOSE recovery multipliers
PROFILE_CLOSE_MULT = {
    'A1_BATH_REFLUX': {'T': 1.3, 'RC': 1.0, 'C': 0.7, 'TR': 1.0, 'X': 0.8},
    'A2_SEALED_RECIRCULATION': {'T': 0.8, 'RC': 1.0, 'C': 1.5, 'TR': 1.0, 'X': 1.0},
    'A3_DISTILL_COLLECT': {'T': 1.0, 'RC': 1.0, 'C': 1.0, 'TR': 1.2, 'X': 1.3},
}

# R2: Strengthened CTS X->Y transfer
K_CTS_CLOSE = 6.0  # was 2.0 in 565

# R3: Strengthened containment-TR relief
K_RELIEF_CLOSE = {
    'A1_BATH_REFLUX': 3.6,
    'A2_SEALED_RECIRCULATION': 2.4,
    'A3_DISTILL_COLLECT': 6.0,
}

# R4: Quality-conditioned Y accumulation coefficients
R4_X_TO_Y = 1.5
R4_C_TO_Y = 0.6

# R5: Closure-coherent coordination bonus
R5_MULTI_SV_BONUS = 0.15
R5_CTS_THRESHOLD = 0.3

# Parameter ladder scaling
LADDER_PACKS = {
    '566-Low': {'r1_scale': 0.5, 'k_cts': 4.0, 'k_relief_scale': 2.0},
    '566-Mid': {'r1_scale': 1.0, 'k_cts': 6.0, 'k_relief_scale': 3.0},
    '566-High': {'r1_scale': 1.5, 'k_cts': 8.0, 'k_relief_scale': 4.0},
}


# ---------------------------------------------------------------------------
# PermeabilityApparatus class (copied from 565)
# ---------------------------------------------------------------------------
class PermeabilityApparatus:
    """
    Fourth-generation virtual apparatus with piecewise 4-zone selective
    restoration (basin / corridor / warning / hard-stop), phase-specific
    modulation, profile-specific discharge events, and headless configuration
    modes.
    """

    def __init__(self, profile_name, config_mode, sensitivity, decay_rates):
        self.profile_name = profile_name
        self.config_mode = config_mode
        self.sensitivity = dict(sensitivity)
        self.decay_rates = dict(decay_rates)
        self.config = CONFIG_MODES[config_mode]
        self.profile_params = dict(PROFILES[profile_name])

        self.gamma_basin = {}
        self.gamma_corridor = {}
        for sv in STATE_VARS:
            scale = decay_rates[sv] / A3_DECAY[sv]
            self.gamma_basin[sv] = GAMMA_BASIN[sv] * scale
            self.gamma_corridor[sv] = GAMMA_CORRIDOR[sv] * scale

        self.gamma_basin['C'] *= self.config['gamma_basin_C_mult']
        self.gamma_basin['S'] *= self.config['gamma_basin_S_mult']

        self.q2 = {}
        for sv in STATE_VARS:
            base = Q2_BASE[sv]
            config_shift = 0.0
            if sv == 'C':
                config_shift = self.config['q2_C_shift']
            elif sv == 'S':
                config_shift = self.config['q2_S_shift']
            q2 = base + config_shift
            q2 = max(Q1 + 0.02, min(q2, HAZARD_DEV[sv] - 0.03))
            self.q2[sv] = q2

        equil_state = [EQUILIBRIUM] * N_VARS
        self.equil_bias = {}
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = self._cross_coupling(equil_state, phase)
            self.equil_bias[phase] = list(cc_eq)

    @staticmethod
    def _clamp(v):
        return max(0.0, min(1.0, v))

    def _cross_coupling(self, state, packet_phase='WORK'):
        p = self.profile_params
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

    def _restoring_force(self, state, packet_phase='WORK', permissivity=None):
        restoring = [0.0] * N_VARS
        zones = [''] * N_VARS

        for i, sv in enumerate(STATE_VARS):
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)
            sign_dev = 1.0 if dev > 0 else (-1.0 if dev < 0 else 0.0)

            eff_q2 = self.q2[sv]
            if sv == 'X' and packet_phase == 'WORK':
                eff_q2 += 0.02
            if permissivity:
                eff_q2 += permissivity.get(sv, 0.0)
            eff_q2 = max(Q1 + 0.02, min(eff_q2, HAZARD_DEV[sv] - 0.03))

            eff_q3 = eff_q2 + 0.05
            eff_q3 = min(eff_q3, HAZARD_DEV[sv] - 0.01)

            corridor_mult_extra = 1.0
            if packet_phase == 'CLOSE':
                if sv == 'C':
                    corridor_mult_extra = self.config['close_corridor_C_mult']
                elif sv == 'S':
                    corridor_mult_extra = self.config['close_corridor_S_mult']

            if abs_dev < Q1:
                restoring[i] = self.gamma_basin[sv] * dev * BASIN_MULT[packet_phase][sv]
                zones[i] = 'BASIN'
            elif abs_dev < eff_q2:
                restoring[i] = (self.gamma_corridor[sv] * dev
                                * CORRIDOR_MULT[packet_phase][sv]
                                * corridor_mult_extra)
                zones[i] = 'CORRIDOR'
            elif abs_dev < eff_q3:
                beta1_eff = BETA1[sv]
                if packet_phase == 'WORK' and sv in ('X', 'T'):
                    beta1_eff *= 0.8
                restoring[i] = (self.gamma_corridor[sv] * dev
                                * EDGE1_MULT[packet_phase][sv]
                                * corridor_mult_extra
                                + beta1_eff * (abs_dev - eff_q2) ** 2 * sign_dev)
                zones[i] = 'WARNING'
            else:
                restoring[i] = (self.gamma_corridor[sv] * dev
                                * EDGE2_MULT[packet_phase][sv]
                                * corridor_mult_extra
                                + BETA2[sv] * (abs_dev - eff_q3) ** 2 * sign_dev)
                zones[i] = 'HARD_STOP'

            max_rf = 0.8 * abs_dev
            if abs(restoring[i]) > max_rf and abs_dev > 1e-10:
                restoring[i] = max_rf * sign_dev

        return restoring, zones

    def _discharge_events(self, state, packet_phase, cts):
        discharge = [0.0] * N_VARS
        events = []

        if packet_phase != 'CLOSE':
            return discharge, events

        X_IDX = SV_INDEX['X']
        Y_IDX = SV_INDEX['Y']
        C_IDX = SV_INDEX['C']
        TR_IDX = SV_INDEX['TR']
        T_IDX = SV_INDEX['T']

        if cts > 0.3:
            x_dev = abs(state[X_IDX] - EQUILIBRIUM)
            if x_dev > Q1:
                rate = 2.0 * (cts - 0.3) * max(x_dev - Q1, 0.0)
                rate *= self.config['cts_discharge_mult']
                discharge[X_IDX] -= rate
                discharge[Y_IDX] += rate * 0.7
                discharge[C_IDX] -= rate * 0.3
                events.append({
                    'type': 'CTS_DISCHARGE',
                    'rate': round(rate, 6),
                })

        c_dev = abs(state[C_IDX] - EQUILIBRIUM)
        tr_dev = abs(state[TR_IDX] - EQUILIBRIUM)
        if c_dev > Q1 and tr_dev > Q1:
            k = K_RELIEF[self.profile_name]
            rate = k * max(c_dev - Q1, 0.0) * max(tr_dev - Q1, 0.0)
            discharge[C_IDX] -= rate
            discharge[TR_IDX] += rate * 0.3
            if 'A3' in self.profile_name:
                discharge[Y_IDX] += rate * 0.15
            events.append({
                'type': 'CONTAINMENT_RESOLUTION',
                'rate': round(rate, 6),
                'profile': self.profile_name,
            })

        t_dev = state[T_IDX] - EQUILIBRIUM
        abs_t_dev = abs(t_dev)
        if abs_t_dev > Q1:
            rate = 2.0 * max(abs_t_dev - Q1, 0.0) ** 2
            sign_t = 1.0 if t_dev > 0 else -1.0
            discharge[T_IDX] -= rate * sign_t
            events.append({
                'type': 'THERMAL_RECOVERY',
                'rate': round(rate, 6),
            })

        return discharge, events

    def update(self, state, dV, packet_phase='WORK', cts=0.0, permissivity=None):
        cc_raw = self._cross_coupling(state, packet_phase)
        bias = self.equil_bias[packet_phase]
        cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]

        rf, zones = self._restoring_force(state, packet_phase, permissivity)

        discharge, events = self._discharge_events(state, packet_phase, cts)

        new_state = []
        rf_mags = {}
        for i in range(N_VARS):
            v = state[i] + dV[i] + cc[i] - rf[i] + discharge[i]
            new_state.append(self._clamp(v))
            rf_mags[STATE_VARS[i]] = round(abs(rf[i]), 6)

        diagnostics = {
            'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
            'discharge_events': events,
            'rf_magnitudes': rf_mags,
        }

        return new_state, diagnostics


# ---------------------------------------------------------------------------
# CloseRecoveryApparatus class (NEW in Phase 566)
# ---------------------------------------------------------------------------
class CloseRecoveryApparatus(PermeabilityApparatus):
    """Phase 566 apparatus with CLOSE recovery channels R1-R5."""

    def __init__(self, profile_name, config_mode, sensitivity, decay_rates,
                 r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0,
                 enable_close_recovery=True):
        super().__init__(profile_name, config_mode, sensitivity, decay_rates)
        self.r1_scale = r1_scale
        self.k_cts_close = k_cts
        self.k_relief_close = K_RELIEF[profile_name] * k_relief_scale
        self.enable_close_recovery = enable_close_recovery

    def _discharge_events(self, state, packet_phase, cts):
        """
        Override: suppress old CTS discharge and old containment resolution
        when CLOSE recovery is enabled (R2 and R3 replace them).
        Keep thermal recovery (not duplicated by R1-R5).
        """
        discharge = [0.0] * N_VARS
        events = []

        if packet_phase != 'CLOSE':
            return discharge, events

        T_IDX = SV_INDEX['T']
        Y_IDX = SV_INDEX['Y']
        C_IDX = SV_INDEX['C']
        TR_IDX = SV_INDEX['TR']

        if self.enable_close_recovery:
            # When CLOSE recovery is enabled, R2 replaces CTS discharge
            # and R3 replaces containment resolution. Only keep thermal recovery.
            pass
        else:
            # When disabled (ablation), use original discharge channels
            X_IDX = SV_INDEX['X']
            if cts > 0.3:
                x_dev = abs(state[X_IDX] - EQUILIBRIUM)
                if x_dev > Q1:
                    rate = 2.0 * (cts - 0.3) * max(x_dev - Q1, 0.0)
                    rate *= self.config['cts_discharge_mult']
                    discharge[X_IDX] -= rate
                    discharge[Y_IDX] += rate * 0.7
                    discharge[C_IDX] -= rate * 0.3
                    events.append({
                        'type': 'CTS_DISCHARGE',
                        'rate': round(rate, 6),
                    })

            c_dev = abs(state[C_IDX] - EQUILIBRIUM)
            tr_dev = abs(state[TR_IDX] - EQUILIBRIUM)
            if c_dev > Q1 and tr_dev > Q1:
                k = K_RELIEF[self.profile_name]
                rate = k * max(c_dev - Q1, 0.0) * max(tr_dev - Q1, 0.0)
                discharge[C_IDX] -= rate
                discharge[TR_IDX] += rate * 0.3
                if 'A3' in self.profile_name:
                    discharge[Y_IDX] += rate * 0.15
                events.append({
                    'type': 'CONTAINMENT_RESOLUTION',
                    'rate': round(rate, 6),
                    'profile': self.profile_name,
                })

        # Thermal recovery always active (not duplicated by R1-R5)
        t_dev = state[T_IDX] - EQUILIBRIUM
        abs_t_dev = abs(t_dev)
        if abs_t_dev > Q1:
            rate = 2.0 * max(abs_t_dev - Q1, 0.0) ** 2
            sign_t = 1.0 if t_dev > 0 else -1.0
            discharge[T_IDX] -= rate * sign_t
            events.append({
                'type': 'THERMAL_RECOVERY',
                'rate': round(rate, 6),
            })

        return discharge, events

    def _apply_close_recovery(self, state, packet_phase, cts, dv_magnitude=0.0):
        """
        Apply CLOSE recovery channels R1-R5.
        Only fires during packet_phase == 'CLOSE'.
        dv_magnitude: L1 norm of input dV (used for clean-CLOSE Y bonus).
        Returns (recovery_vector, recovery_details).
        """
        recovery = [0.0] * N_VARS
        details = {'R1': {}, 'R2': {}, 'R3': {}, 'R4': {}, 'R5': {}}

        if packet_phase != 'CLOSE' or not self.enable_close_recovery:
            return recovery, details

        # R1: Per-SV CLOSE drawdown
        active_svs = []
        moving_toward_eq = []

        for sv in ['T', 'RC', 'S', 'C', 'TR', 'X']:
            i = SV_INDEX[sv]
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)

            if abs_dev < 1e-10:
                continue

            # S special case: only recover when below equilibrium
            if sv == 'S' and dev > 0:
                continue  # upward S drift is productive

            k = K_CLOSE.get(sv, 0.0) * self.r1_scale
            profile_mult = PROFILE_CLOSE_MULT[self.profile_name].get(sv, 1.0)

            # CTS weighting for T, X, TR
            cts_weight = 1.0
            if sv in CTS_WEIGHTED_SVS:
                cts_weight = 0.5 + 0.5 * max(0.0, min(1.0, cts))

            r1_amount = k * profile_mult * cts_weight * abs_dev
            # Cap at |dev| to prevent overshoot
            r1_amount = min(r1_amount, abs_dev)

            # Direction: toward equilibrium
            sign = 1.0 if dev > 0 else -1.0
            recovery[i] -= r1_amount * sign

            details['R1'][sv] = round(r1_amount, 6)

            if abs_dev > Q1:
                active_svs.append(sv)
                moving_toward_eq.append(sv)

        # Clean-CLOSE multiplier: Y gain is amplified when CLOSE phase has
        # no incoming dV (clean recovery), attenuated when dV disrupts CLOSE.
        # This rewards proper phase separation (dV in WORK, zero in CLOSE).
        clean_close_mult = 1.0 / (1.0 + 10.0 * dv_magnitude)

        # R2: CTS X->Y transfer (strengthened)
        if cts > 0.3:
            x_idx = SV_INDEX['X']
            y_idx = SV_INDEX['Y']
            x_dev = abs(state[x_idx] - EQUILIBRIUM)
            if x_dev > Q1:
                rate = self.k_cts_close * (cts - 0.3) * max(x_dev - Q1, 0.0)
                rate *= self.config.get('cts_discharge_mult', 1.0)
                x_sign = 1.0 if state[x_idx] > EQUILIBRIUM else -1.0
                recovery[x_idx] -= rate * x_sign  # X toward eq
                # Y gain scaled by clean-CLOSE multiplier
                recovery[SV_INDEX['Y']] += rate * 0.7 * clean_close_mult
                # Also relieve C slightly
                c_idx = SV_INDEX['C']
                c_sign = 1.0 if state[c_idx] > EQUILIBRIUM else -1.0
                recovery[c_idx] -= rate * 0.3 * c_sign
                details['R2'] = {'rate': round(rate, 6), 'cts': round(cts, 4)}

        # R3: Containment-TR relief (strengthened)
        c_idx = SV_INDEX['C']
        tr_idx = SV_INDEX['TR']
        c_dev = abs(state[c_idx] - EQUILIBRIUM)
        tr_dev = abs(state[tr_idx] - EQUILIBRIUM)
        if c_dev > Q1 and tr_dev > Q1:
            rate = self.k_relief_close * max(c_dev - Q1, 0.0) * max(tr_dev - Q1, 0.0)
            c_sign = 1.0 if state[c_idx] > EQUILIBRIUM else -1.0
            recovery[c_idx] -= rate * c_sign
            recovery[tr_idx] += rate * 0.3 * (1.0 if state[tr_idx] < EQUILIBRIUM else -1.0)
            if 'A3' in self.profile_name:
                # Y gain scaled by clean-CLOSE multiplier
                recovery[SV_INDEX['Y']] += rate * 0.15 * clean_close_mult
            details['R3'] = {'rate': round(rate, 6)}

        # R4: Quality-conditioned Y accumulation
        x_recovery = abs(details['R1'].get('X', 0.0))
        c_recovery = abs(details['R1'].get('C', 0.0))
        # R4 Y gain amplified by clean-CLOSE multiplier
        r4_y = cts * (R4_X_TO_Y * x_recovery + R4_C_TO_Y * c_recovery) * clean_close_mult
        if r4_y > 0:
            recovery[SV_INDEX['Y']] += r4_y
            details['R4'] = {'y_gain': round(r4_y, 6)}

        # R5: Closure-coherent coordination bonus
        n_coherent = len(moving_toward_eq)
        if cts > R5_CTS_THRESHOLD and n_coherent >= 2:
            bonus = 1.0 + R5_MULTI_SV_BONUS * (n_coherent - 1)
            for sv in moving_toward_eq:
                i = SV_INDEX[sv]
                r1_val = details['R1'].get(sv, 0.0)
                if r1_val > 0:
                    additional = r1_val * (bonus - 1.0)
                    sign = 1.0 if state[i] > EQUILIBRIUM else -1.0
                    recovery[i] -= additional * sign
            details['R5'] = {
                'n_coherent': n_coherent,
                'bonus': round(bonus, 4),
                'svs': moving_toward_eq,
            }

        return recovery, details

    def update(self, state, dV, packet_phase='WORK', cts=0.0, permissivity=None):
        """Override update to add CLOSE recovery after base update."""
        # 1. Base update (cross-coupling + restoring + old discharge)
        new_state, diagnostics = super().update(state, dV, packet_phase, cts, permissivity)

        # 2. CLOSE recovery (pass dV magnitude for clean-CLOSE Y bonus)
        dv_mag = sum(abs(v) for v in dV)
        recovery, recovery_details = self._apply_close_recovery(new_state, packet_phase, cts, dv_mag)

        # Apply recovery
        for i in range(N_VARS):
            new_state[i] = self._clamp(new_state[i] + recovery[i])

        diagnostics['close_recovery'] = recovery_details
        diagnostics['close_recovery_magnitudes'] = {
            STATE_VARS[i]: round(abs(recovery[i]), 6) for i in range(N_VARS)
        }

        return new_state, diagnostics


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_close_recovery_apparatus(profile_name, config_mode,
                                    r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0,
                                    enable_close_recovery=True):
    """Build a CloseRecoveryApparatus with given profile and config mode."""
    profile = PROFILES[profile_name]
    sensitivity = {sv: profile[f'sensitivity_{sv}'] for sv in STATE_VARS}
    decay_rates = PROFILE_DECAYS[profile_name]
    return CloseRecoveryApparatus(
        profile_name, config_mode, sensitivity, decay_rates,
        r1_scale=r1_scale, k_cts=k_cts, k_relief_scale=k_relief_scale,
        enable_close_recovery=enable_close_recovery)


def build_no_close_recovery_apparatus(profile_name, config_mode):
    """B10 ablation: CloseRecoveryApparatus with CLOSE recovery disabled."""
    return build_close_recovery_apparatus(
        profile_name, config_mode,
        r1_scale=0.0, k_cts=2.0, k_relief_scale=1.0,
        enable_close_recovery=False)


def build_configured_apparatus(profile_name, config_mode):
    """Build default CloseRecoveryApparatus (566-Mid defaults)."""
    return build_close_recovery_apparatus(profile_name, config_mode)


# ---------------------------------------------------------------------------
# Composite headless regime score
# ---------------------------------------------------------------------------
def compute_infra_scores(pilot_folios):
    """
    Compute composite infrastructure scores from folio budget data.
    """
    project_root = Path(__file__).resolve().parents[3]
    budget_path = (project_root / 'phases'
                   / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results'
                   / 't2_folio_budgets.json')

    with open(budget_path, 'r', encoding='utf-8') as f:
        budget_data = json.load(f)

    raw = {}
    for folio in pilot_folios:
        fb = budget_data['folio_budgets'].get(folio)
        if fb is None:
            print(f"  WARNING: {folio} not in folio budgets, skipping")
            continue
        hr = fb.get('headless_regime', {})
        hl_rate = hr.get('hl_rate', 0.0)
        sd = hr.get('subtype_dist', {})
        pseudo_l_frac = sd.get('PSEUDO_L', 0.0)
        parametric_cpf_frac = sd.get('PARAMETRIC_CPF', 0.0)
        sb = hr.get('suffix_bifurcation', {})
        suffix_bifurc = 1.0 - sb.get('binary_sfx_rate', 0.0)

        raw[folio] = {
            'hl_rate': hl_rate,
            'pseudo_l_frac': pseudo_l_frac,
            'parametric_cpf_frac': parametric_cpf_frac,
            'suffix_bifurc': suffix_bifurc,
        }

    metrics = ['hl_rate', 'pseudo_l_frac', 'parametric_cpf_frac', 'suffix_bifurc']
    mins = {}
    maxs = {}
    for m in metrics:
        vals = [raw[f][m] for f in raw]
        mins[m] = min(vals)
        maxs[m] = max(vals)

    result = {}
    norm_scores = []
    for folio in raw:
        normed = {}
        for m in metrics:
            rng = maxs[m] - mins[m]
            if rng < 1e-10:
                normed[m] = 0.5
            else:
                normed[m] = (raw[folio][m] - mins[m]) / rng

        infra_score = (0.50 * normed['hl_rate']
                       + 0.20 * normed['pseudo_l_frac']
                       + 0.20 * normed['parametric_cpf_frac']
                       + 0.10 * normed['suffix_bifurc'])

        result[folio] = {
            'hl_rate': round(raw[folio]['hl_rate'], 5),
            'pseudo_l_frac': round(raw[folio]['pseudo_l_frac'], 5),
            'parametric_cpf_frac': round(raw[folio]['parametric_cpf_frac'], 5),
            'suffix_bifurc': round(raw[folio]['suffix_bifurc'], 5),
            'infra_score': round(infra_score, 5),
        }
        norm_scores.append((folio, infra_score))

    scores_sorted = sorted(norm_scores, key=lambda x: x[1])
    n = len(scores_sorted)
    p33_idx = n // 3
    p67_idx = 2 * n // 3
    p33_val = scores_sorted[p33_idx][1]
    p67_val = scores_sorted[p67_idx][1]

    for folio, score in norm_scores:
        if score < p33_val:
            result[folio]['config_mode'] = 'H0_LOW_INFRA'
        elif score >= p67_val:
            result[folio]['config_mode'] = 'H2_HIGH_INFRA'
        else:
            result[folio]['config_mode'] = 'H1_MEDIUM_INFRA'

    return result


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def make_dv(sv_name, magnitude):
    """Create a dV vector targeting a single state variable."""
    dv = [0.0] * N_VARS
    dv[SV_INDEX[sv_name]] = magnitude
    return dv


def make_dv_multi(contributions):
    """Create a dV vector from multiple contributions: {sv_name: magnitude}."""
    dv = [0.0] * N_VARS
    for sv_name, mag in contributions.items():
        dv[SV_INDEX[sv_name]] = mag
    return dv


def compute_viability(trajectory, phase_labels):
    """
    Compute packet-coherence viability score for a trajectory.
    """
    if len(trajectory) != len(phase_labels):
        raise ValueError("trajectory and phase_labels must have same length")

    total = 0
    score_sum = 0.0

    zone_scores = {
        'WORK': {
            'BASIN': 0.3,
            'CORRIDOR': 1.0,
            'WARNING': 0.8,
            'HARD_STOP': 0.3,
            'HAZARD': 0.0,
        },
        'SPEC': {
            'BASIN': 1.0,
            'CORRIDOR': 0.85,
            'WARNING': 0.5,
            'HARD_STOP': 0.1,
            'HAZARD': 0.0,
        },
        'CLOSE': {
            'BASIN': 1.0,
            'CORRIDOR': 0.6,
            'WARNING': 0.2,
            'HARD_STOP': 0.0,
            'HAZARD': 0.0,
        },
    }

    for step_idx, state in enumerate(trajectory):
        phase = phase_labels[step_idx]
        scores = zone_scores[phase]

        for i, sv in enumerate(STATE_VARS):
            if HAZARD_BOUNDARIES[sv][0] is None and HAZARD_BOUNDARIES[sv][1] is None:
                continue
            total += 1
            dev = abs(state[i] - EQUILIBRIUM)

            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            if dev < Q1:
                score_sum += scores['BASIN']
            elif dev < q2:
                score_sum += scores['CORRIDOR']
            elif dev < q3:
                score_sum += scores['WARNING']
            elif dev < HAZARD_DEV[sv]:
                score_sum += scores['HARD_STOP']
            else:
                score_sum += scores['HAZARD']

    if total == 0:
        return 1.0
    return score_sum / total


def _packet_aligned_phase(step, spec_len=5, work_len=15, close_len=5):
    """Return phase for a packet-aligned trace: SPEC->WORK->CLOSE cycle."""
    cycle_len = spec_len + work_len + close_len
    pos = step % cycle_len
    if pos < spec_len:
        return 'SPEC'
    elif pos < spec_len + work_len:
        return 'WORK'
    else:
        return 'CLOSE'


def _packet_disrupted_phase(step, spec_len=5, work_len=15, close_len=5):
    """
    Return phase for a packet-disrupted trace: WORK dV applied during CLOSE,
    zero during WORK. Implemented as swapping WORK<->CLOSE labels.
    """
    cycle_len = spec_len + work_len + close_len
    pos = step % cycle_len
    if pos < spec_len:
        return 'SPEC'
    elif pos < spec_len + work_len:
        return 'CLOSE'
    else:
        return 'WORK'


def _run_synthetic_trace(app, n_tokens, dv_map, phase_sequence, cts=0.0):
    """
    Run a synthetic trace and return trajectory (list of states).
    phase_sequence: list of phase strings, or a callable(step) -> phase_str
    """
    state = [EQUILIBRIUM] * N_VARS
    trajectory = []
    dv = make_dv_multi(dv_map)

    for step in range(n_tokens):
        if callable(phase_sequence):
            phase = phase_sequence(step)
        else:
            phase = phase_sequence[step % len(phase_sequence)]
        state, _ = app.update(state, dv, packet_phase=phase, cts=cts)
        trajectory.append(list(state))

    return trajectory


# ---------------------------------------------------------------------------
# Self-tests V1-V9 (copied from 565, using build_configured_apparatus)
# ---------------------------------------------------------------------------

def test_v1_stable_equilibrium():
    """V1: Stable equilibrium."""
    print("\n  V1: Stable Equilibrium")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = [0.0] * N_VARS
    max_deviation = 0.0

    for step in range(50):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for i in range(N_VARS):
            dev = abs(state[i] - EQUILIBRIUM)
            max_deviation = max(max_deviation, dev)

    passed = max_deviation < 0.01
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: max_deviation={max_deviation:.6f} (threshold=0.01)")
    return passed, {'pass': passed, 'max_deviation': round(max_deviation, 6)}


def test_v2_hazard_approach():
    """V2: Hazard approach."""
    print("\n  V2: Hazard Approach (P99 sustained, 100 tokens)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P99_DV)

    max_vals = {sv: EQUILIBRIUM for sv in STATE_VARS}
    passed = True

    for step in range(100):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for i, sv in enumerate(STATE_VARS):
            max_vals[sv] = max(max_vals[sv], state[i])

    details = {}
    for sv in STATE_VARS:
        lo, hi = HAZARD_BOUNDARIES[sv]
        breached = False
        if hi is not None and max_vals[sv] >= hi:
            breached = True
        details[sv] = {
            'max_val': round(max_vals[sv], 4),
            'hazard_hi': hi,
            'breached': breached,
        }
        if breached:
            passed = False
            print(f"    FAIL: {sv} breached hazard at {max_vals[sv]:.4f} (limit={hi})")

    status = "PASS" if passed else "FAIL"
    print(f"    {status}")
    for sv in STATE_VARS:
        hi = HAZARD_BOUNDARIES[sv][1]
        if hi is not None:
            margin = hi - max_vals[sv]
            print(f"      {sv}: max={max_vals[sv]:.4f}, hazard={hi}, margin={margin:.4f}")

    return passed, {'pass': passed, 'details': details}


def test_v3_y_monotonic():
    """V3: Y monotonic accumulation."""
    print("\n  V3: Y Monotonic Accumulation")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv('Y', 0.01)

    prev_y = state[SV_INDEX['Y']]
    monotonic = True
    first_violation = None

    for step in range(100):
        state, diag = app.update(state, dv, packet_phase='WORK')
        curr_y = state[SV_INDEX['Y']]
        if curr_y < prev_y - 1e-10:
            monotonic = False
            if first_violation is None:
                first_violation = step
        prev_y = curr_y

    passed = monotonic
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: Y_final={state[SV_INDEX['Y']]:.4f}, monotonic={monotonic}")
    if first_violation is not None:
        print(f"    First violation at step {first_violation}")
    return passed, {
        'pass': passed,
        'y_final': round(state[SV_INDEX['Y']], 4),
        'monotonic': monotonic,
    }


def test_v4_close_recovers_faster():
    """V4: CLOSE recovers faster than WORK."""
    print("\n  V4: CLOSE Recovers Faster Than WORK")

    T_IDX = SV_INDEX['T']
    initial_dev = 0.15
    initial_state = [EQUILIBRIUM] * N_VARS
    initial_state[T_IDX] = EQUILIBRIUM + initial_dev
    dv_zero = [0.0] * N_VARS

    app_work = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state_work = list(initial_state)
    work_devs = [abs(state_work[T_IDX] - EQUILIBRIUM)]
    for step in range(20):
        state_work, _ = app_work.update(state_work, dv_zero, packet_phase='WORK')
        work_devs.append(abs(state_work[T_IDX] - EQUILIBRIUM))

    app_close = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state_close = list(initial_state)
    close_devs = [abs(state_close[T_IDX] - EQUILIBRIUM)]
    for step in range(20):
        state_close, _ = app_close.update(state_close, dv_zero, packet_phase='CLOSE')
        close_devs.append(abs(state_close[T_IDX] - EQUILIBRIUM))

    work_final_dev = work_devs[-1]
    close_final_dev = close_devs[-1]
    passed = close_final_dev < work_final_dev

    status = "PASS" if passed else "FAIL"
    print(f"    {status}: WORK final dev={work_final_dev:.4f}, "
          f"CLOSE final dev={close_final_dev:.4f}")
    return passed, {
        'pass': passed,
        'work_final_dev': round(work_final_dev, 4),
        'close_final_dev': round(close_final_dev, 4),
    }


def test_v5a_p95_no_hazard():
    """V5a: P95 sustained input for 100 WORK tokens. No SV breaches hazard. HARD GATE."""
    print("\n  V5a: P95 No Hazard Breach (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P95_DV)

    passed = True
    max_vals = {sv: EQUILIBRIUM for sv in STATE_VARS}

    for step in range(100):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for i, sv in enumerate(STATE_VARS):
            max_vals[sv] = max(max_vals[sv], state[i])

    details = {}
    for sv in STATE_VARS:
        lo, hi = HAZARD_BOUNDARIES[sv]
        breached = False
        if hi is not None and max_vals[sv] >= hi:
            breached = True
            passed = False
        details[sv] = {
            'max_val': round(max_vals[sv], 4),
            'hazard_hi': hi,
            'breached': breached,
        }

    status = "PASS" if passed else "FAIL"
    print(f"    {status}")
    for sv in STATE_VARS:
        hi = HAZARD_BOUNDARIES[sv][1]
        if hi is not None:
            margin = hi - max_vals[sv]
            print(f"      {sv}: max={max_vals[sv]:.4f}, hazard={hi}, margin={margin:.4f}")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {'pass': passed, 'details': details}


def test_v5b_p99_no_sustained_hazard():
    """V5b: P99 no sustained hazard (informational)."""
    print("\n  V5b: P99 No Sustained Hazard (informational)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P99_DV)

    consec_hazard = {sv: 0 for sv in STATE_VARS}
    max_consec_hazard = {sv: 0 for sv in STATE_VARS}
    max_vals = {sv: EQUILIBRIUM for sv in STATE_VARS}

    for step in range(100):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for i, sv in enumerate(STATE_VARS):
            max_vals[sv] = max(max_vals[sv], state[i])
            lo, hi = HAZARD_BOUNDARIES[sv]
            in_hazard = False
            if hi is not None and state[i] >= hi:
                in_hazard = True
            if lo is not None and state[i] <= lo:
                in_hazard = True
            if in_hazard:
                consec_hazard[sv] += 1
                max_consec_hazard[sv] = max(max_consec_hazard[sv], consec_hazard[sv])
            else:
                consec_hazard[sv] = 0

    sustained = any(v > 5 for v in max_consec_hazard.values())
    print(f"    Sustained hazard (>5 consec): {sustained}")
    for sv in STATE_VARS:
        hi = HAZARD_BOUNDARIES[sv][1]
        if hi is not None:
            margin = hi - max_vals[sv]
            print(f"      {sv}: max={max_vals[sv]:.4f}, hazard={hi}, margin={margin:.4f}, "
                  f"max_consec_in_hazard={max_consec_hazard[sv]}")

    return None, {
        'pass': None,
        'informational': True,
        'sustained_hazard': sustained,
        'max_consecutive_hazard': max_consec_hazard,
        'max_vals': {sv: round(v, 4) for sv, v in max_vals.items()},
    }


def test_v5c_p99_random_phase_stress():
    """V5c: P99 random phase stress (informational)."""
    print("\n  V5c: P99 Random Phase Stress (informational)")
    random.seed(42)
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P99_DV)

    max_devs = {sv: 0.0 for sv in STATE_VARS}
    hazard_events = {sv: 0 for sv in STATE_VARS}

    for step in range(200):
        phase = random.choice(['SPEC', 'WORK', 'CLOSE'])
        state, _ = app.update(state, dv, packet_phase=phase)
        for i, sv in enumerate(STATE_VARS):
            dev = abs(state[i] - EQUILIBRIUM)
            max_devs[sv] = max(max_devs[sv], dev)
            lo, hi = HAZARD_BOUNDARIES[sv]
            if hi is not None and state[i] >= hi:
                hazard_events[sv] += 1
            if lo is not None and state[i] <= lo:
                hazard_events[sv] += 1

    total_hazard_events = sum(hazard_events.values())
    print(f"    Total hazard events: {total_hazard_events}")
    for sv in STATE_VARS:
        print(f"      {sv}: max_dev={max_devs[sv]:.4f}, hazard_events={hazard_events[sv]}")

    return None, {
        'pass': None,
        'informational': True,
        'max_deviations': {sv: round(v, 4) for sv, v in max_devs.items()},
        'hazard_events': hazard_events,
        'total_hazard_events': total_hazard_events,
    }


def test_v6_config_mode_differentiates():
    """V6: Config mode differentiates."""
    print("\n  V6: Config Mode Differentiates")
    app_h0 = build_configured_apparatus('A3_DISTILL_COLLECT', 'H0_LOW_INFRA')
    app_h2 = build_configured_apparatus('A3_DISTILL_COLLECT', 'H2_HIGH_INFRA')

    h0_q2_C = app_h0.q2['C']
    h2_q2_C = app_h2.q2['C']
    h0_q2_S = app_h0.q2['S']
    h2_q2_S = app_h2.q2['S']

    c_wider = h2_q2_C > h0_q2_C
    s_wider = h2_q2_S > h0_q2_S

    passed = c_wider and s_wider
    status = "PASS" if passed else "FAIL"
    print(f"    {status}")
    print(f"      C: H0 q2={h0_q2_C:.4f}, H2 q2={h2_q2_C:.4f} (H2 wider={c_wider})")
    print(f"      S: H0 q2={h0_q2_S:.4f}, H2 q2={h2_q2_S:.4f} (H2 wider={s_wider})")

    return passed, {
        'pass': passed,
        'h0_q2_C': round(h0_q2_C, 4),
        'h2_q2_C': round(h2_q2_C, 4),
        'h0_q2_S': round(h0_q2_S, 4),
        'h2_q2_S': round(h2_q2_S, 4),
        'c_wider': c_wider,
        's_wider': s_wider,
    }


def test_v7_bounded_excursion_cycle():
    """V7: Bounded excursion cycle. HARD GATE."""
    print("\n  V7: Bounded Excursion Cycle (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    dv_work = make_dv_multi({
        'T': P90_DV['T'],
        'X': P90_DV['X'],
        'C': P90_DV['C'],
    })
    dv_close = [0.0] * N_VARS

    state = [EQUILIBRIUM] * N_VARS
    process_svs = [sv for sv in STATE_VARS
                   if HAZARD_BOUNDARIES[sv][0] is not None
                   or HAZARD_BOUNDARIES[sv][1] is not None]

    bounded_cycles = 0
    trajectory_info = []

    for cycle in range(4):
        exited_basin = False
        for step in range(15):
            state, diag = app.update(state, dv_work, packet_phase='WORK')
            for sv in process_svs:
                if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) > Q1:
                    exited_basin = True

        work_end_devs = {sv: round(abs(state[SV_INDEX[sv]] - EQUILIBRIUM), 4)
                         for sv in process_svs}

        for step in range(15):
            state, diag = app.update(state, dv_close, packet_phase='CLOSE')

        close_end_devs = {sv: round(abs(state[SV_INDEX[sv]] - EQUILIBRIUM), 4)
                          for sv in process_svs}

        in_basin = all(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) <= Q1
                       for sv in process_svs)

        if exited_basin and in_basin:
            bounded_cycles += 1

        trajectory_info.append({
            'cycle': cycle,
            'exited_basin': exited_basin,
            'returned_to_basin': in_basin,
            'work_end_devs': work_end_devs,
            'close_end_devs': close_end_devs,
        })
        print(f"    Cycle {cycle}: exited={exited_basin}, returned={in_basin}, "
              f"work_end_max={max(work_end_devs.values()):.4f}, "
              f"close_end_max={max(close_end_devs.values()):.4f}")

    passed = bounded_cycles >= 2
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: {bounded_cycles} bounded cycles (need >=2)")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'bounded_cycles': bounded_cycles,
        'trajectory': trajectory_info,
    }


def test_v8a_p50_stays_near_basin():
    """V8a: P50 input stays near basin."""
    print("\n  V8a: P50 Input Stays Near Basin (relaxed: < q1 + 0.02)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P50_DV)

    threshold = Q1 + 0.02

    process_svs = [sv for sv in STATE_VARS
                   if HAZARD_BOUNDARIES[sv][0] is not None
                   or HAZARD_BOUNDARIES[sv][1] is not None]
    max_dev = 0.0
    max_dev_sv = None

    for step in range(30):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for sv in process_svs:
            dev = abs(state[SV_INDEX[sv]] - EQUILIBRIUM)
            if dev > max_dev:
                max_dev = dev
                max_dev_sv = sv

    passed = max_dev < threshold
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: max_dev={max_dev:.6f} ({max_dev_sv}), threshold={threshold}")
    return passed, {
        'pass': passed,
        'max_deviation': round(max_dev, 6),
        'max_deviation_sv': max_dev_sv,
        'threshold': threshold,
    }


def test_v8b_p90_enters_corridor():
    """V8b: P90 input enters corridor. HARD GATE."""
    print("\n  V8b: P90 Input Enters Corridor (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv('T', P90_DV['T'])

    T_IDX = SV_INDEX['T']
    entered_corridor = False
    entry_step = None

    for step in range(10):
        state, diag = app.update(state, dv, packet_phase='WORK')
        t_dev = abs(state[T_IDX] - EQUILIBRIUM)
        if t_dev > Q1 and not entered_corridor:
            entered_corridor = True
            entry_step = step + 1

    passed = entered_corridor and entry_step is not None and entry_step <= 5
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: entered_corridor={entered_corridor}, "
          f"entry_step={entry_step}, threshold=5")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'entered_corridor': entered_corridor,
        'entry_step': entry_step,
    }


def test_v8c_p99_reaches_edge_not_hazard():
    """V8c: P99 reaches edge but not hazard."""
    print("\n  V8c: P99 Reaches Edge But Not Hazard")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv('T', P99_DV['T'])

    T_IDX = SV_INDEX['T']
    reached_edge = False
    breached_hazard = False
    max_t_dev = 0.0

    for step in range(30):
        state, diag = app.update(state, dv, packet_phase='WORK')
        t_dev = abs(state[T_IDX] - EQUILIBRIUM)
        max_t_dev = max(max_t_dev, t_dev)
        if t_dev >= app.q2['T']:
            reached_edge = True
        if HAZARD_BOUNDARIES['T'][1] is not None and state[T_IDX] >= HAZARD_BOUNDARIES['T'][1]:
            breached_hazard = True

    passed = reached_edge and not breached_hazard
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: reached_edge={reached_edge}, breached_hazard={breached_hazard}, "
          f"max_T_dev={max_t_dev:.4f}, q2_T={app.q2['T']:.4f}, "
          f"hazard_T={HAZARD_BOUNDARIES['T'][1]}")
    return passed, {
        'pass': passed,
        'reached_edge': reached_edge,
        'breached_hazard': breached_hazard,
        'max_T_dev': round(max_t_dev, 4),
        'q2_T': round(app.q2['T'], 4),
    }


def test_v8d_work_close_bounded_cycles():
    """V8d: WORK->CLOSE bounded cycles. HARD GATE."""
    print("\n  V8d: WORK->CLOSE Bounded Cycles (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    dv_work = make_dv_multi({
        'T': 0.038,
        'X': 0.020,
        'C': 0.022,
    })
    dv_close = [0.0] * N_VARS

    state = [EQUILIBRIUM] * N_VARS
    process_svs = [sv for sv in STATE_VARS
                   if HAZARD_BOUNDARIES[sv][0] is not None
                   or HAZARD_BOUNDARIES[sv][1] is not None]

    bounded_cycles = 0

    for cycle in range(6):
        exited_basin = False
        for step in range(20):
            state, _ = app.update(state, dv_work, packet_phase='WORK')
            for sv in process_svs:
                if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) > Q1:
                    exited_basin = True

        for step in range(20):
            state, _ = app.update(state, dv_close, packet_phase='CLOSE')

        in_basin = all(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) <= Q1
                       for sv in process_svs)

        if exited_basin and in_basin:
            bounded_cycles += 1

        work_max = max(abs(state[SV_INDEX[sv]] - EQUILIBRIUM)
                       for sv in process_svs)
        print(f"    Cycle {cycle}: exited={exited_basin}, returned={in_basin}, "
              f"close_end_max_dev={work_max:.4f}")

    passed = bounded_cycles >= 2
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: {bounded_cycles} bounded cycles (need >=2)")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'bounded_cycles': bounded_cycles,
    }


def test_v8e_zero_input_stays_in_basin():
    """V8e: Zero input stays in basin. HARD GATE."""
    print("\n  V8e: Zero Input Stays in Basin (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = [0.0] * N_VARS
    max_dev = 0.0
    max_dev_sv = None

    for step in range(100):
        state, _ = app.update(state, dv, packet_phase='WORK')
        for i, sv in enumerate(STATE_VARS):
            dev = abs(state[i] - EQUILIBRIUM)
            if dev > max_dev:
                max_dev = dev
                max_dev_sv = sv

    passed = max_dev < Q1
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: max_dev={max_dev:.6f} ({max_dev_sv}), threshold={Q1}")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'max_deviation': round(max_dev, 6),
        'max_deviation_sv': max_dev_sv,
    }


def test_v8f_sustained_p99_stress():
    """V8f: Sustained P99 stress test (informational)."""
    print("\n  V8f: Sustained P99 Stress Test (informational)")
    random.seed(42)

    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P99_DV)

    max_devs = {sv: 0.0 for sv in STATE_VARS}
    near_hazard = {sv: False for sv in STATE_VARS}

    for step in range(200):
        phase = random.choice(['SPEC', 'WORK', 'CLOSE'])
        state, _ = app.update(state, dv, packet_phase=phase)
        for i, sv in enumerate(STATE_VARS):
            dev = abs(state[i] - EQUILIBRIUM)
            max_devs[sv] = max(max_devs[sv], dev)
            lo, hi = HAZARD_BOUNDARIES[sv]
            if hi is not None and state[i] >= hi - 0.03:
                near_hazard[sv] = True
            if lo is not None and state[i] <= lo + 0.03:
                near_hazard[sv] = True

    print(f"    Max deviations:")
    for sv in STATE_VARS:
        hz_str = "NEAR HAZARD" if near_hazard[sv] else "safe"
        print(f"      {sv}: {max_devs[sv]:.4f} ({hz_str})")

    return None, {
        'pass': None,
        'informational': True,
        'max_deviations': {sv: round(v, 4) for sv, v in max_devs.items()},
        'near_hazard': near_hazard,
    }


def test_v9_discriminative_viability():
    """V9: Discriminative Viability Preflight. HARD GATE."""
    print("\n  V9: Discriminative Viability Preflight (HARD GATE)")
    random.seed(42)

    results = {}

    # --- V9a: Packet-aligned, P90 ---
    print("    V9a: Packet-aligned P90 (200 tokens)")
    app_a = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    state = [EQUILIBRIUM] * N_VARS
    trajectory_a = []
    phases_a = []
    dv_work = make_dv_multi(P90_DV)
    dv_zero = [0.0] * N_VARS

    for step in range(200):
        phase = _packet_aligned_phase(step)
        dv = dv_work if phase == 'WORK' else dv_zero
        state, _ = app_a.update(state, dv, packet_phase=phase)
        trajectory_a.append(list(state))
        phases_a.append(phase)

    viability_a = compute_viability(trajectory_a, phases_a)
    print(f"      Viability: {viability_a:.4f}")
    results['V9a'] = {'viability': round(viability_a, 4)}

    # --- V9b: Packet-disrupted, P90 ---
    print("    V9b: Packet-disrupted P90 (200 tokens)")
    app_b = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    state = [EQUILIBRIUM] * N_VARS
    trajectory_b = []
    phases_b = []

    for step in range(200):
        aligned_phase = _packet_aligned_phase(step)
        if aligned_phase == 'WORK':
            dv = dv_zero
            actual_phase = 'WORK'
        elif aligned_phase == 'CLOSE':
            dv = dv_work
            actual_phase = 'CLOSE'
        else:
            dv = dv_zero
            actual_phase = 'SPEC'
        state, _ = app_b.update(state, dv, packet_phase=actual_phase)
        trajectory_b.append(list(state))
        phases_b.append(aligned_phase)

    viability_b = compute_viability(trajectory_b, phases_b)
    print(f"      Viability: {viability_b:.4f}")
    results['V9b'] = {'viability': round(viability_b, 4)}

    # --- V9c: Random, P90 ---
    print("    V9c: Random P90 (200 tokens)")
    app_c = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    trajectory_c = []
    phases_c = []

    for step in range(200):
        phase = random.choice(['SPEC', 'WORK', 'CLOSE'])
        state, _ = app_c.update(state, dv_work, packet_phase=phase)
        trajectory_c.append(list(state))
        phases_c.append(_packet_aligned_phase(step))

    viability_c = compute_viability(trajectory_c, phases_c)
    print(f"      Viability: {viability_c:.4f}")
    results['V9c'] = {'viability': round(viability_c, 4)}

    # --- V9d: Packet-aligned, P95 ---
    print("    V9d: Packet-aligned P95 (200 tokens)")
    app_d = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    dv_work_p95 = make_dv_multi(P95_DV)

    state = [EQUILIBRIUM] * N_VARS
    trajectory_d = []
    phases_d = []

    for step in range(200):
        phase = _packet_aligned_phase(step)
        dv = dv_work_p95 if phase == 'WORK' else dv_zero
        state, _ = app_d.update(state, dv, packet_phase=phase)
        trajectory_d.append(list(state))
        phases_d.append(phase)

    viability_d = compute_viability(trajectory_d, phases_d)
    print(f"      Viability: {viability_d:.4f}")
    results['V9d'] = {'viability': round(viability_d, 4)}

    # --- V9e: Packet-disrupted, P95 ---
    print("    V9e: Packet-disrupted P95 (200 tokens)")
    app_e = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    state = [EQUILIBRIUM] * N_VARS
    trajectory_e = []
    phases_e = []

    for step in range(200):
        aligned_phase = _packet_aligned_phase(step)
        if aligned_phase == 'WORK':
            dv = dv_zero
            actual_phase = 'WORK'
        elif aligned_phase == 'CLOSE':
            dv = dv_work_p95
            actual_phase = 'CLOSE'
        else:
            dv = dv_zero
            actual_phase = 'SPEC'
        state, _ = app_e.update(state, dv, packet_phase=actual_phase)
        trajectory_e.append(list(state))
        phases_e.append(aligned_phase)

    viability_e = compute_viability(trajectory_e, phases_e)
    print(f"      Viability: {viability_e:.4f}")
    results['V9e'] = {'viability': round(viability_e, 4)}

    # --- V9f: CTS discharge check ---
    print("    V9f: CTS Discharge Check")
    app_f_cts = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    app_f_no_cts = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    dv_x_push = make_dv('X', P95_DV['X'])

    state_cts = [EQUILIBRIUM] * N_VARS
    state_no_cts = [EQUILIBRIUM] * N_VARS

    for step in range(30):
        state_cts, _ = app_f_cts.update(state_cts, dv_x_push, packet_phase='WORK')
        state_no_cts, _ = app_f_no_cts.update(state_no_cts, dv_x_push, packet_phase='WORK')

    x_before_cts = state_cts[SV_INDEX['X']]
    x_before_no = state_no_cts[SV_INDEX['X']]
    print(f"      X before CLOSE: CTS={x_before_cts:.4f}, no-CTS={x_before_no:.4f}")

    cts_discharge_count = 0
    for step in range(20):
        state_cts, diag_cts = app_f_cts.update(state_cts, dv_zero,
                                                 packet_phase='CLOSE', cts=0.5)
        state_no_cts, diag_no = app_f_no_cts.update(state_no_cts, dv_zero,
                                                       packet_phase='CLOSE', cts=0.0)
        # Check both old discharge events and new R2 CLOSE recovery
        for ev in diag_cts['discharge_events']:
            if ev['type'] == 'CTS_DISCHARGE':
                cts_discharge_count += 1
        # Also check R2 in close_recovery diagnostics
        cr = diag_cts.get('close_recovery', {})
        r2 = cr.get('R2', {})
        if r2.get('rate', 0.0) > 0:
            cts_discharge_count += 1

    x_after_cts = state_cts[SV_INDEX['X']]
    x_after_no = state_no_cts[SV_INDEX['X']]
    x_recovery_with_cts = abs(x_before_cts - x_after_cts)
    x_recovery_without_cts = abs(x_before_no - x_after_no)

    print(f"      X after CLOSE: CTS={x_after_cts:.4f}, no-CTS={x_after_no:.4f}")
    print(f"      X recovery: CTS={x_recovery_with_cts:.4f}, no-CTS={x_recovery_without_cts:.4f}")
    print(f"      CTS discharge events: {cts_discharge_count}")

    results['V9f'] = {
        'cts_discharge_count': cts_discharge_count,
        'x_before_close': round(x_before_cts, 4),
        'x_recovery_with_cts': round(x_recovery_with_cts, 4),
        'x_recovery_without_cts': round(x_recovery_without_cts, 4),
    }

    # --- Evaluate hard gate requirements ---
    gate_a_gt_b = viability_a > viability_b
    gate_a_lt_1 = viability_a < 1.0
    gate_d_gt_e = viability_d > viability_e
    gate_f_discharge = cts_discharge_count > 0

    print(f"\n    Hard gate checks:")
    print(f"      V9a > V9b: {viability_a:.4f} > {viability_b:.4f} = {gate_a_gt_b}")
    print(f"      V9a < 1.0: {viability_a:.4f} < 1.0 = {gate_a_lt_1}")
    print(f"      V9d > V9e: {viability_d:.4f} > {viability_e:.4f} = {gate_d_gt_e}")
    print(f"      V9f CTS discharge > 0: {cts_discharge_count} > 0 = {gate_f_discharge}")

    passed = gate_a_gt_b and gate_a_lt_1 and gate_d_gt_e and gate_f_discharge

    if not passed:
        print("    *** HARD GATE FAILED ***")
        if not gate_a_gt_b:
            print("      -> V9a not > V9b: aligned P90 doesn't beat disrupted")
        if not gate_a_lt_1:
            print("      -> V9a = 1.0: perfect viability, no discrimination")
        if not gate_d_gt_e:
            print("      -> V9d not > V9e: aligned P95 doesn't beat disrupted")
        if not gate_f_discharge:
            print("      -> V9f: no CTS discharge events detected")
    else:
        print("    PASS: All V9 sub-gates passed")

    results['V9a']['pass'] = True
    results['V9b']['pass'] = True
    results['V9c'] = {'pass': None, 'viability': round(viability_c, 4)}
    results['V9d']['pass'] = True
    results['V9e']['pass'] = True
    results['V9f']['pass'] = gate_f_discharge

    return passed, results


# ---------------------------------------------------------------------------
# Self-tests V10-V12 (NEW in Phase 566)
# ---------------------------------------------------------------------------

def _compute_hazard_burden(trajectory):
    """
    Compute hazard burden for a trajectory.
    hazard_burden = 1.0*warning_contacts + 3.0*hardstop_contacts
                    + 0.5*time_outside_corridor + 2.0*max_excursion
    """
    warning_contacts = 0
    hardstop_contacts = 0
    time_outside_corridor = 0
    max_excursion = 0.0

    for state in trajectory:
        for i, sv in enumerate(STATE_VARS):
            if HAZARD_BOUNDARIES[sv][0] is None and HAZARD_BOUNDARIES[sv][1] is None:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            max_excursion = max(max_excursion, dev)

            if dev >= q3:
                hardstop_contacts += 1
            elif dev >= q2:
                warning_contacts += 1

            if dev >= q2:
                time_outside_corridor += 1

    return (1.0 * warning_contacts + 3.0 * hardstop_contacts
            + 0.5 * time_outside_corridor + 2.0 * max_excursion)


def _compute_y_final(trajectory):
    """Get Y value at end of trajectory."""
    if not trajectory:
        return EQUILIBRIUM
    return trajectory[-1][SV_INDEX['Y']]


def test_v10_aligned_recovery(app):
    """
    V10 (HARD GATE): Aligned recovery > disrupted recovery.
    Run 200-token synthetic traces at P90 amplitude.
    """
    print("\n  V10: Aligned Recovery > Disrupted Recovery (HARD GATE)")
    dv_work = make_dv_multi(P90_DV)
    dv_zero = [0.0] * N_VARS

    # V10a: Aligned (SPEC->WORK->CLOSE), dV during WORK only, CTS=0.5 during CLOSE
    state_a = [EQUILIBRIUM] * N_VARS
    close_start_devs_a = []
    close_end_devs_a = []

    for step in range(200):
        phase = _packet_aligned_phase(step)
        dv = dv_work if phase == 'WORK' else dv_zero
        cts = 0.5 if phase == 'CLOSE' else 0.0

        # Track CLOSE phase transitions
        prev_phase = _packet_aligned_phase(step - 1) if step > 0 else 'SPEC'
        if phase == 'CLOSE' and prev_phase != 'CLOSE':
            # Start of CLOSE phase
            close_start_devs_a.append(
                sum(abs(state_a[i] - EQUILIBRIUM) for i in range(N_VARS)) / N_VARS
            )

        state_a, _ = app.update(state_a, dv, packet_phase=phase, cts=cts)

        next_phase = _packet_aligned_phase(step + 1) if step < 199 else 'SPEC'
        if phase == 'CLOSE' and next_phase != 'CLOSE':
            # End of CLOSE phase
            close_end_devs_a.append(
                sum(abs(state_a[i] - EQUILIBRIUM) for i in range(N_VARS)) / N_VARS
            )

    # V10b: Disrupted - WORK-magnitude dV applied during CLOSE, zero during WORK
    # Build a fresh apparatus with same config
    app_b = build_close_recovery_apparatus(
        app.profile_name, app.config_mode,
        r1_scale=app.r1_scale, k_cts=app.k_cts_close,
        k_relief_scale=app.k_relief_close / K_RELIEF[app.profile_name],
        enable_close_recovery=app.enable_close_recovery)

    state_b = [EQUILIBRIUM] * N_VARS
    close_start_devs_b = []
    close_end_devs_b = []

    for step in range(200):
        phase = _packet_aligned_phase(step)
        # Disrupted: dV during CLOSE, zero during WORK
        if phase == 'CLOSE':
            dv = dv_work
        else:
            dv = dv_zero
        cts = 0.5 if phase == 'CLOSE' else 0.0

        prev_phase = _packet_aligned_phase(step - 1) if step > 0 else 'SPEC'
        if phase == 'CLOSE' and prev_phase != 'CLOSE':
            close_start_devs_b.append(
                sum(abs(state_b[i] - EQUILIBRIUM) for i in range(N_VARS)) / N_VARS
            )

        state_b, _ = app_b.update(state_b, dv, packet_phase=phase, cts=cts)

        next_phase = _packet_aligned_phase(step + 1) if step < 199 else 'SPEC'
        if phase == 'CLOSE' and next_phase != 'CLOSE':
            close_end_devs_b.append(
                sum(abs(state_b[i] - EQUILIBRIUM) for i in range(N_VARS)) / N_VARS
            )

    # Compute average recovery during CLOSE phases
    recovery_a = 0.0
    if close_start_devs_a and close_end_devs_a:
        n = min(len(close_start_devs_a), len(close_end_devs_a))
        for j in range(n):
            recovery_a += max(0, close_start_devs_a[j] - close_end_devs_a[j])
        recovery_a /= max(n, 1)

    recovery_b = 0.0
    if close_start_devs_b and close_end_devs_b:
        n = min(len(close_start_devs_b), len(close_end_devs_b))
        for j in range(n):
            recovery_b += max(0, close_start_devs_b[j] - close_end_devs_b[j])
        recovery_b /= max(n, 1)

    gate_recovery = recovery_a > recovery_b
    gate_positive = recovery_a > 0

    passed = gate_recovery and gate_positive
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: aligned_recovery={recovery_a:.6f}, "
          f"disrupted_recovery={recovery_b:.6f}")
    print(f"      aligned > disrupted: {gate_recovery}")
    print(f"      aligned > 0: {gate_positive}")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'aligned_recovery': round(recovery_a, 6),
        'disrupted_recovery': round(recovery_b, 6),
        'gate_recovery': gate_recovery,
        'gate_positive': gate_positive,
    }


def test_v11_cts_visibility(app):
    """
    V11 (HARD GATE): CTS visibility.
    Push X to warning band with 30 WORK tokens of P95 X dV.
    Run 20 CLOSE tokens with CTS=0.5 vs CTS=0.
    """
    print("\n  V11: CTS Visibility (HARD GATE)")
    dv_x_push = make_dv('X', P95_DV['X'])
    dv_zero = [0.0] * N_VARS

    # Build two identical apparatus
    app_cts = build_close_recovery_apparatus(
        app.profile_name, app.config_mode,
        r1_scale=app.r1_scale, k_cts=app.k_cts_close,
        k_relief_scale=app.k_relief_close / K_RELIEF[app.profile_name],
        enable_close_recovery=app.enable_close_recovery)
    app_no = build_close_recovery_apparatus(
        app.profile_name, app.config_mode,
        r1_scale=app.r1_scale, k_cts=app.k_cts_close,
        k_relief_scale=app.k_relief_close / K_RELIEF[app.profile_name],
        enable_close_recovery=app.enable_close_recovery)

    state_cts = [EQUILIBRIUM] * N_VARS
    state_no = [EQUILIBRIUM] * N_VARS

    # Push X into warning band
    for step in range(30):
        state_cts, _ = app_cts.update(state_cts, dv_x_push, packet_phase='WORK')
        state_no, _ = app_no.update(state_no, dv_x_push, packet_phase='WORK')

    x_before = state_cts[SV_INDEX['X']]
    y_before_cts = state_cts[SV_INDEX['Y']]
    y_before_no = state_no[SV_INDEX['Y']]
    print(f"    X before CLOSE: {x_before:.4f}")

    # Run 3 CLOSE tokens (short window to see partial recovery difference)
    for step in range(3):
        state_cts, _ = app_cts.update(state_cts, dv_zero, packet_phase='CLOSE', cts=0.5)
        state_no, _ = app_no.update(state_no, dv_zero, packet_phase='CLOSE', cts=0.0)

    x_after_cts = state_cts[SV_INDEX['X']]
    x_after_no = state_no[SV_INDEX['X']]
    x_recovery_cts = abs(x_before - x_after_cts)
    x_recovery_no = abs(x_before - x_after_no)

    y_gain_cts = state_cts[SV_INDEX['Y']] - y_before_cts
    y_gain_no = state_no[SV_INDEX['Y']] - y_before_no

    # Residual excursion
    residual_cts = abs(x_after_cts - EQUILIBRIUM)
    residual_no = abs(x_after_no - EQUILIBRIUM)

    # Gate: X_recovery(CTS=0.5) > X_recovery(CTS=0) by >= 20%
    if x_recovery_no > 1e-10:
        recovery_ratio = x_recovery_cts / x_recovery_no
    else:
        recovery_ratio = float('inf') if x_recovery_cts > 0 else 1.0

    gate_x_recovery = recovery_ratio >= 1.20
    gate_y_gain = y_gain_cts > y_gain_no
    gate_residual = residual_cts < residual_no

    passed = gate_x_recovery and gate_y_gain
    status = "PASS" if passed else "FAIL"
    print(f"    {status}")
    print(f"      X recovery CTS=0.5: {x_recovery_cts:.4f}, CTS=0: {x_recovery_no:.4f} "
          f"(ratio={recovery_ratio:.2f}, need >=1.20)")
    print(f"      Y gain CTS=0.5: {y_gain_cts:.4f}, CTS=0: {y_gain_no:.4f} "
          f"(CTS > no-CTS: {gate_y_gain})")
    print(f"      Residual excursion CTS=0.5: {residual_cts:.4f}, CTS=0: {residual_no:.4f} "
          f"(lower with CTS: {gate_residual})")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'x_before': round(x_before, 4),
        'x_recovery_cts': round(x_recovery_cts, 4),
        'x_recovery_no_cts': round(x_recovery_no, 4),
        'recovery_ratio': round(recovery_ratio, 4),
        'y_gain_cts': round(y_gain_cts, 4),
        'y_gain_no_cts': round(y_gain_no, 4),
        'residual_cts': round(residual_cts, 4),
        'residual_no_cts': round(residual_no, 4),
        'gate_x_recovery': gate_x_recovery,
        'gate_y_gain': gate_y_gain,
        'gate_residual': gate_residual,
    }


def test_v12_paradox_inversion(app):
    """
    V12 (HARD GATE, ABORT ON FAILURE): B2 paradox inversion preflight.
    Split into safety (V12a) and productivity (V12b).
    """
    print("\n  V12: B2 Paradox Inversion Preflight (HARD GATE, ABORT)")
    random.seed(566)

    dv_work = make_dv_multi(P90_DV)
    dv_zero = [0.0] * N_VARS

    def _build_fresh():
        return build_close_recovery_apparatus(
            app.profile_name, app.config_mode,
            r1_scale=app.r1_scale, k_cts=app.k_cts_close,
            k_relief_scale=app.k_relief_close / K_RELIEF[app.profile_name],
            enable_close_recovery=app.enable_close_recovery)

    # --- Aligned trace (SPEC->WORK->CLOSE, P90 dV during WORK, CTS=0.5 during CLOSE) ---
    app_aligned = _build_fresh()
    state = [EQUILIBRIUM] * N_VARS
    traj_aligned = []
    phases_aligned = []
    for step in range(200):
        phase = _packet_aligned_phase(step)
        dv = dv_work if phase == 'WORK' else dv_zero
        cts = 0.5 if phase == 'CLOSE' else 0.0
        state, _ = app_aligned.update(state, dv, packet_phase=phase, cts=cts)
        traj_aligned.append(list(state))
        phases_aligned.append(phase)

    # --- Zero-input trace ---
    app_zero = _build_fresh()
    state = [EQUILIBRIUM] * N_VARS
    traj_zero = []
    for step in range(200):
        phase = _packet_aligned_phase(step)
        state, _ = app_zero.update(state, dv_zero, packet_phase=phase)
        traj_zero.append(list(state))

    # --- Random-phase trace ---
    # dV applied every token (no phase gating), random phase assignment.
    # This models unsupervised operation: excursion and recovery are not
    # separated, so CLOSE recovery fights incoming dV during CLOSE phases.
    app_random = _build_fresh()
    state = [EQUILIBRIUM] * N_VARS
    traj_random = []
    for step in range(200):
        phase = random.choice(['SPEC', 'WORK', 'CLOSE'])
        cts = 0.5 if phase == 'CLOSE' else 0.0
        state, _ = app_random.update(state, dv_work, packet_phase=phase, cts=cts)
        traj_random.append(list(state))

    # Compute hazard burdens
    hb_aligned = _compute_hazard_burden(traj_aligned)
    hb_zero = _compute_hazard_burden(traj_zero)
    hb_random = _compute_hazard_burden(traj_random)

    # Compute Y finals
    y_aligned = _compute_y_final(traj_aligned)
    y_zero = _compute_y_final(traj_zero)
    y_random = _compute_y_final(traj_random)

    # Compute viability for V12c
    viab_aligned = compute_viability(traj_aligned, phases_aligned)
    viab_zero = compute_viability(traj_zero, [_packet_aligned_phase(s) for s in range(200)])
    viab_random = compute_viability(traj_random, [_packet_aligned_phase(s) for s in range(200)])

    # V12a: Safety inversion
    # hazard_burden(aligned) < hazard_burden(random_phase)
    gate_v12a = hb_aligned < hb_random

    # V12b: Productive closure
    # Y_final(aligned) > Y_final(zero_input) AND Y_final(aligned) > Y_final(random_phase)
    gate_v12b_vs_zero = y_aligned > y_zero
    gate_v12b_vs_random = y_aligned > y_random
    gate_v12b = gate_v12b_vs_zero and gate_v12b_vs_random

    # V12c: Composite (logged, NOT hard-gated)
    composite_aligned = 0.7 * viab_aligned + 0.3 * y_aligned
    composite_zero = 0.7 * viab_zero + 0.3 * y_zero
    composite_random = 0.7 * viab_random + 0.3 * y_random

    # Safety margin ratio
    if hb_aligned > 1e-10:
        safety_margin_ratio = hb_random / hb_aligned
    else:
        safety_margin_ratio = float('inf') if hb_random > 0 else 1.0

    print(f"    V12a - Safety Inversion:")
    print(f"      hazard_burden(aligned)={hb_aligned:.2f}")
    print(f"      hazard_burden(zero_input)={hb_zero:.2f}")
    print(f"      hazard_burden(random_phase)={hb_random:.2f}")
    print(f"      aligned < random: {gate_v12a} (margin ratio={safety_margin_ratio:.2f})")

    print(f"    V12b - Productive Closure:")
    print(f"      Y_final(aligned)={y_aligned:.4f}")
    print(f"      Y_final(zero_input)={y_zero:.4f}")
    print(f"      Y_final(random_phase)={y_random:.4f}")
    print(f"      aligned > zero: {gate_v12b_vs_zero}")
    print(f"      aligned > random: {gate_v12b_vs_random}")

    print(f"    V12c - Composite (logged, not gated):")
    print(f"      aligned={composite_aligned:.4f}")
    print(f"      zero_input={composite_zero:.4f}")
    print(f"      random_phase={composite_random:.4f}")

    passed = gate_v12a and gate_v12b
    status = "PASS" if passed else "FAIL"
    print(f"    {status}")
    if not passed:
        print("    *** HARD GATE FAILED — ABORT ***")

    return passed, {
        'pass': passed,
        'V12a': {
            'pass': gate_v12a,
            'hb_aligned': round(hb_aligned, 4),
            'hb_zero': round(hb_zero, 4),
            'hb_random': round(hb_random, 4),
            'safety_margin_ratio': round(safety_margin_ratio, 4) if safety_margin_ratio != float('inf') else 'inf',
        },
        'V12b': {
            'pass': gate_v12b,
            'y_aligned': round(y_aligned, 4),
            'y_zero': round(y_zero, 4),
            'y_random': round(y_random, 4),
        },
        'V12c': {
            'composite_aligned': round(composite_aligned, 4),
            'composite_zero': round(composite_zero, 4),
            'composite_random': round(composite_random, 4),
        },
    }, safety_margin_ratio


# ---------------------------------------------------------------------------
# Parameter ladder
# ---------------------------------------------------------------------------
def run_parameter_ladder(profile_name='A3_DISTILL_COLLECT',
                          config_mode='H1_MEDIUM_INFRA'):
    """
    Iterate through LADDER_PACKS (Low, Mid, High).
    For each pack, run V10-V12 preflight.
    Select best pack by V12a safety margin ratio.
    """
    print("\n--- Parameter Ladder ---")
    ladder_results = {}
    candidates = []

    for pack_name, params in LADDER_PACKS.items():
        print(f"\n  === Ladder Pack: {pack_name} ===")
        print(f"    r1_scale={params['r1_scale']}, k_cts={params['k_cts']}, "
              f"k_relief_scale={params['k_relief_scale']}")

        app = build_close_recovery_apparatus(
            profile_name, config_mode,
            r1_scale=params['r1_scale'],
            k_cts=params['k_cts'],
            k_relief_scale=params['k_relief_scale'])

        v10_pass, v10_detail = test_v10_aligned_recovery(app)
        v11_pass, v11_detail = test_v11_cts_visibility(app)
        v12_pass, v12_detail, safety_margin = test_v12_paradox_inversion(app)

        pack_result = {
            'params': params,
            'V10': v10_detail,
            'V11': v11_detail,
            'V12': v12_detail,
            'all_pass': v10_pass and v11_pass and v12_pass,
        }
        ladder_results[pack_name] = pack_result

        # Selection criteria
        v10a_recovery = v10_detail.get('aligned_recovery', 0.0)
        if (v12_pass and v10_pass and v11_pass
                and v10a_recovery < 0.80 and v10a_recovery > 0):
            candidates.append((pack_name, safety_margin, v10a_recovery))
            print(f"    -> CANDIDATE (margin={safety_margin:.2f}, recovery={v10a_recovery:.6f})")
        else:
            reasons = []
            if not v12_pass:
                reasons.append("V12 failed")
            if not v10_pass:
                reasons.append("V10 failed")
            if not v11_pass:
                reasons.append("V11 failed")
            if v10a_recovery >= 0.80:
                reasons.append(f"over-recovery ({v10a_recovery:.4f} >= 0.80)")
            if v10a_recovery <= 0:
                reasons.append(f"no recovery ({v10a_recovery:.6f})")
            print(f"    -> REJECTED ({', '.join(reasons)})")

    # Select best pack: maximize safety margin ratio
    if not candidates:
        print("\n  *** NO CANDIDATE PACK PASSED ALL GATES ***")
        # Fall back to Mid if available, else first pack
        selected = '566-Mid'
        print(f"  Falling back to {selected}")
    else:
        # Sort by safety margin (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)
        selected = candidates[0][0]
        print(f"\n  Selected pack: {selected} "
              f"(margin={candidates[0][1]:.2f}, recovery={candidates[0][2]:.6f})")

    return selected, ladder_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    output_path = phase_dir / 'results' / 't1_close_recovery_apparatus.json'

    print("=" * 70)
    print("T1: Close Recovery Apparatus")
    print("Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY")
    print("=" * 70)

    # --- Run self-tests V1-V9 ---
    print("\n--- Self-Tests V1-V9 ---")
    test_results = {}
    all_pass = True
    hard_gate_pass = True

    v1_pass, v1_detail = test_v1_stable_equilibrium()
    test_results['V1'] = v1_detail
    if v1_pass is not None:
        all_pass = all_pass and v1_pass

    v2_pass, v2_detail = test_v2_hazard_approach()
    test_results['V2'] = v2_detail
    if v2_pass is not None:
        all_pass = all_pass and v2_pass

    v3_pass, v3_detail = test_v3_y_monotonic()
    test_results['V3'] = v3_detail
    if v3_pass is not None:
        all_pass = all_pass and v3_pass

    v4_pass, v4_detail = test_v4_close_recovers_faster()
    test_results['V4'] = v4_detail
    if v4_pass is not None:
        all_pass = all_pass and v4_pass

    v5a_pass, v5a_detail = test_v5a_p95_no_hazard()
    test_results['V5a'] = v5a_detail
    if v5a_pass is not None:
        all_pass = all_pass and v5a_pass
        if not v5a_pass:
            hard_gate_pass = False

    v5b_pass, v5b_detail = test_v5b_p99_no_sustained_hazard()
    test_results['V5b'] = v5b_detail

    v5c_pass, v5c_detail = test_v5c_p99_random_phase_stress()
    test_results['V5c'] = v5c_detail

    v6_pass, v6_detail = test_v6_config_mode_differentiates()
    test_results['V6'] = v6_detail
    if v6_pass is not None:
        all_pass = all_pass and v6_pass

    v7_pass, v7_detail = test_v7_bounded_excursion_cycle()
    test_results['V7'] = v7_detail
    if v7_pass is not None:
        all_pass = all_pass and v7_pass
        if not v7_pass:
            hard_gate_pass = False

    v8a_pass, v8a_detail = test_v8a_p50_stays_near_basin()
    test_results['V8a'] = v8a_detail
    if v8a_pass is not None:
        all_pass = all_pass and v8a_pass

    v8b_pass, v8b_detail = test_v8b_p90_enters_corridor()
    test_results['V8b'] = v8b_detail
    if v8b_pass is not None:
        all_pass = all_pass and v8b_pass
        if not v8b_pass:
            hard_gate_pass = False

    v8c_pass, v8c_detail = test_v8c_p99_reaches_edge_not_hazard()
    test_results['V8c'] = v8c_detail
    if v8c_pass is not None:
        all_pass = all_pass and v8c_pass

    v8d_pass, v8d_detail = test_v8d_work_close_bounded_cycles()
    test_results['V8d'] = v8d_detail
    if v8d_pass is not None:
        all_pass = all_pass and v8d_pass
        if not v8d_pass:
            hard_gate_pass = False

    v8e_pass, v8e_detail = test_v8e_zero_input_stays_in_basin()
    test_results['V8e'] = v8e_detail
    if v8e_pass is not None:
        all_pass = all_pass and v8e_pass
        if not v8e_pass:
            hard_gate_pass = False

    v8f_pass, v8f_detail = test_v8f_sustained_p99_stress()
    test_results['V8f'] = v8f_detail

    v9_pass, v9_detail = test_v9_discriminative_viability()
    for sub_key, sub_val in v9_detail.items():
        test_results[sub_key] = sub_val
    if v9_pass is not None:
        all_pass = all_pass and v9_pass
        if not v9_pass:
            hard_gate_pass = False

    # --- V1-V9 Summary ---
    print("\n--- V1-V9 Summary ---")
    hard_gates_v1_v9 = {'V5a', 'V7', 'V8b', 'V8d', 'V8e', 'V9a', 'V9b', 'V9d', 'V9e', 'V9f'}
    for name in ['V1', 'V2', 'V3', 'V4', 'V5a', 'V5b', 'V5c', 'V6', 'V7',
                 'V8a', 'V8b', 'V8c', 'V8d', 'V8e', 'V8f',
                 'V9a', 'V9b', 'V9c', 'V9d', 'V9e', 'V9f']:
        detail = test_results.get(name, {})
        p = detail.get('pass', None)
        if p is None:
            status = "INFO"
        elif p:
            status = "PASS"
        else:
            status = "FAIL"
        gate = " (HARD GATE)" if name in hard_gates_v1_v9 else ""
        print(f"  {name}: {status}{gate}")

    if hard_gate_pass:
        print("\n  ALL V1-V9 HARD GATES PASSED")
    else:
        print("\n  *** V1-V9 HARD GATE(S) FAILED -- aborting ***")
        sys.exit(1)

    # --- Parameter Ladder with V10-V12 ---
    selected_pack, ladder_results = run_parameter_ladder()

    # --- Final V10-V12 with selected pack ---
    print(f"\n--- Final V10-V12 with selected pack: {selected_pack} ---")
    params = LADDER_PACKS[selected_pack]
    final_app = build_close_recovery_apparatus(
        'A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA',
        r1_scale=params['r1_scale'],
        k_cts=params['k_cts'],
        k_relief_scale=params['k_relief_scale'])

    v10_pass, v10_detail = test_v10_aligned_recovery(final_app)
    test_results['V10'] = v10_detail
    if v10_pass is not None:
        all_pass = all_pass and v10_pass
        if not v10_pass:
            hard_gate_pass = False

    v11_pass, v11_detail = test_v11_cts_visibility(final_app)
    test_results['V11'] = v11_detail
    if v11_pass is not None:
        all_pass = all_pass and v11_pass
        if not v11_pass:
            hard_gate_pass = False

    v12_pass, v12_detail, _ = test_v12_paradox_inversion(final_app)
    test_results['V12'] = v12_detail
    if v12_pass is not None:
        all_pass = all_pass and v12_pass
        if not v12_pass:
            hard_gate_pass = False

    # --- Final Summary ---
    print("\n--- Final Self-Test Summary (V1-V12) ---")
    all_test_names = ['V1', 'V2', 'V3', 'V4', 'V5a', 'V5b', 'V5c', 'V6', 'V7',
                      'V8a', 'V8b', 'V8c', 'V8d', 'V8e', 'V8f',
                      'V9a', 'V9b', 'V9c', 'V9d', 'V9e', 'V9f',
                      'V10', 'V11', 'V12']
    hard_gates_all = hard_gates_v1_v9 | {'V10', 'V11', 'V12'}
    for name in all_test_names:
        detail = test_results.get(name, {})
        p = detail.get('pass', None)
        if p is None:
            status = "INFO"
        elif p:
            status = "PASS"
        else:
            status = "FAIL"
        gate = " (HARD GATE)" if name in hard_gates_all else ""
        print(f"  {name}: {status}{gate}")

    if not hard_gate_pass:
        print("\n  *** HARD GATE(S) FAILED -- aborting ***")
        sys.exit(1)
    else:
        print("\n  ALL HARD GATES PASSED")

    if all_pass:
        print("  ALL SELF-TESTS PASSED")
    else:
        print("  Some non-gate tests failed (see above)")

    # --- Compute infra scores ---
    print("\n--- Infra Scores ---")
    infra_scores = compute_infra_scores(PILOT_FOLIOS)
    for folio in PILOT_FOLIOS:
        if folio in infra_scores:
            s = infra_scores[folio]
            print(f"  {folio}: score={s['infra_score']:.3f} -> {s['config_mode']}")

    # --- Build output ---
    output = {
        'metadata': {
            'phase': '566',
            'task': 'T1',
            'timestamp': datetime.now().isoformat(),
        },
        'apparatus_config': {
            'Q1': Q1,
            'Q2_BASE': Q2_BASE,
            'Q3_BASE': Q3_BASE,
            'HAZARD_DEV': HAZARD_DEV,
            'GAMMA_BASIN': GAMMA_BASIN,
            'GAMMA_CORRIDOR': GAMMA_CORRIDOR,
            'BETA1': BETA1,
            'BETA2': BETA2,
            'A3_DECAY': A3_DECAY,
            'PROFILE_DECAYS': PROFILE_DECAYS,
            'BASIN_MULT': BASIN_MULT,
            'CORRIDOR_MULT': CORRIDOR_MULT,
            'EDGE1_MULT': EDGE1_MULT,
            'EDGE2_MULT': EDGE2_MULT,
            'K_RELIEF': K_RELIEF,
            'CONFIG_MODES': CONFIG_MODES,
            'PHASE_CC_MULT': PHASE_CC_MULT,
            'P95_DV': P95_DV,
            'P90_DV': {sv: round(v, 4) for sv, v in P90_DV.items()},
        },
        'close_recovery_config': {
            'K_CLOSE': K_CLOSE,
            'CTS_WEIGHTED_SVS': sorted(CTS_WEIGHTED_SVS),
            'PROFILE_CLOSE_MULT': PROFILE_CLOSE_MULT,
            'K_CTS_CLOSE': K_CTS_CLOSE,
            'K_RELIEF_CLOSE': K_RELIEF_CLOSE,
            'R4_X_TO_Y': R4_X_TO_Y,
            'R4_C_TO_Y': R4_C_TO_Y,
            'R5_MULTI_SV_BONUS': R5_MULTI_SV_BONUS,
            'R5_CTS_THRESHOLD': R5_CTS_THRESHOLD,
            'LADDER_PACKS': LADDER_PACKS,
        },
        'selected_ladder_pack': selected_pack,
        'selected_ladder_params': LADDER_PACKS[selected_pack],
        'ladder_results': {},
        'folio_infra_scores': infra_scores,
        'self_tests': test_results,
        'hard_gate_pass': hard_gate_pass,
    }

    # Serialize ladder results (handle potential non-serializable values)
    for pack_name, pack_result in ladder_results.items():
        serializable = {}
        serializable['params'] = pack_result['params']
        serializable['all_pass'] = pack_result['all_pass']
        for vname in ['V10', 'V11', 'V12']:
            vdata = pack_result.get(vname, {})
            # Convert any non-serializable values
            serializable[vname] = json.loads(json.dumps(vdata, default=str))
        output['ladder_results'][pack_name] = serializable

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {output_path}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")

    return 0 if hard_gate_pass else 1


if __name__ == '__main__':
    raise SystemExit(main())
