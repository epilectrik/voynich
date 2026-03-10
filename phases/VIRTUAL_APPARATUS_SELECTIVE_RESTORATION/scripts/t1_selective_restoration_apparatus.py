"""
T1: Selective Restoration Apparatus
Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION

Third-generation virtual apparatus replacing the Phase 564 cubic restoring
force (which was too stiff — universal viability=1.0, nothing discriminated)
with a piecewise 3-zone selective restoration architecture calibrated against
actual supervisory signal magnitudes.

Zone architecture:
  Zone 1 (BASIN):    |dev| < q1          — weak linear restoring
  Zone 2 (CORRIDOR): q1 <= |dev| < q2    — moderate linear restoring
  Zone 3 (EDGE):     |dev| >= q2         — corridor + quadratic barrier

Self-tests V1-V8 validate the apparatus; V5, V8b, V8d, V8e are HARD GATEs.
"""

import json
import sys
import time
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
# Constants
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

# Deviation from equilibrium (0.5) to nearest hazard boundary
HAZARD_DEV = {
    'T': 0.35, 'RC': 0.40, 'S': 0.35, 'C': 0.35,
    'TR': 0.40, 'X': 0.30, 'Y': 1.0,
}

# ---------------------------------------------------------------------------
# Restoring force parameters (base values for A3)
# ---------------------------------------------------------------------------
GAMMA_BASIN = {
    'T': 0.10, 'RC': 0.02, 'S': 0.25, 'C': 0.08,
    'TR': 0.02, 'X': 0.18, 'Y': 0.25,
}

GAMMA_CORRIDOR = {
    'T': 0.04, 'RC': 0.05, 'S': 0.10, 'C': 0.04,
    'TR': 0.03, 'X': 0.10, 'Y': 0.10,
}

BETA = {
    'T': 10.0, 'RC': 4.0, 'S': 14.0, 'C': 10.0,
    'TR': 7.0, 'X': 80.0, 'Y': 2.0,
}

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

EDGE_MULT = {
    'SPEC':  {'T': 2.0, 'RC': 1.5, 'S': 0.5, 'C': 2.0, 'TR': 1.5, 'X': 2.5, 'Y': 0.5},
    'WORK':  {'T': 1.5, 'RC': 1.2, 'S': 0.5, 'C': 1.5, 'TR': 1.2, 'X': 3.0, 'Y': 0.3},
    'CLOSE': {'T': 3.0, 'RC': 2.5, 'S': 1.5, 'C': 3.0, 'TR': 2.5, 'X': 3.5, 'Y': 0.3},
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

P99_DV = {sv: c * A3_SENS[sv] for sv, c in {
    'T': 0.054, 'RC': 0.030, 'S': 0.096, 'C': 0.055,
    'TR': 0.045, 'X': 0.068, 'Y': 0.018,
}.items()}


# ---------------------------------------------------------------------------
# SelectiveRestorationApparatus class
# ---------------------------------------------------------------------------
class SelectiveRestorationApparatus:
    """
    Third-generation virtual apparatus with piecewise 3-zone selective
    restoration, phase-specific modulation, profile-specific discharge
    events, and headless configuration modes.
    """

    def __init__(self, profile_name, config_mode, sensitivity, decay_rates):
        """
        profile_name: e.g. 'A3_DISTILL_COLLECT'
        config_mode:  e.g. 'H1_MEDIUM_INFRA'
        sensitivity:  dict {sv_name: float}
        decay_rates:  dict {sv_name: float}
        """
        self.profile_name = profile_name
        self.config_mode = config_mode
        self.sensitivity = dict(sensitivity)
        self.decay_rates = dict(decay_rates)
        self.config = CONFIG_MODES[config_mode]

        # Get the profile parameters for cross-coupling alphas
        self.profile_params = dict(PROFILES[profile_name])

        # Build scaled gamma_basin and gamma_corridor
        self.gamma_basin = {}
        self.gamma_corridor = {}
        for sv in STATE_VARS:
            scale = decay_rates[sv] / A3_DECAY[sv]
            self.gamma_basin[sv] = GAMMA_BASIN[sv] * scale
            self.gamma_corridor[sv] = GAMMA_CORRIDOR[sv] * scale

        # Apply config mode gamma_basin multipliers for C and S
        self.gamma_basin['C'] *= self.config['gamma_basin_C_mult']
        self.gamma_basin['S'] *= self.config['gamma_basin_S_mult']

        # Build effective q2 per SV
        self.eff_q2 = {}
        for sv in STATE_VARS:
            base = Q2_BASE[sv]
            # Config shifts for C and S
            config_shift = 0.0
            if sv == 'C':
                config_shift = self.config['q2_C_shift']
            elif sv == 'S':
                config_shift = self.config['q2_S_shift']
            # Note: permissivity is applied at update time, not constructor
            q2 = base + config_shift
            # Clamp to valid range
            q2 = max(Q1 + 0.02, min(q2, HAZARD_DEV[sv] - 0.03))
            self.eff_q2[sv] = q2

        # Equilibrium bias correction: compute cross-coupling at [0.5]*7
        # and store as a constant restoring bias, so the apparatus's natural
        # resting state is exactly [0.5]*7 despite asymmetric cc thresholds.
        # This corrects for alpha_FY * max(TR_eq - 0.4, 0) > 0 at equilibrium.
        equil_state = [EQUILIBRIUM] * N_VARS
        self.equil_bias = {}
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = self._cross_coupling(equil_state, phase)
            self.equil_bias[phase] = list(cc_eq)

    @staticmethod
    def _clamp(v):
        return max(0.0, min(1.0, v))

    def _cross_coupling(self, state, packet_phase='WORK'):
        """
        Cross-coupling identical to Phase 564: same alpha terms with
        phase-specific multipliers from PHASE_CC_MULT.
        """
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
        """
        Piecewise 3-zone restoring force.

        Zone 1 (BASIN):    |dev| < Q1       — gamma_basin * dev * basin_mult
        Zone 2 (CORRIDOR): Q1 <= |dev| < q2 — gamma_corridor * dev * corridor_mult
        Zone 3 (EDGE):     |dev| >= q2      — corridor + beta * (|dev|-q2)^2 * sign(dev)
        """
        rf = [0.0] * N_VARS
        zones = [''] * N_VARS

        for i, sv in enumerate(STATE_VARS):
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)
            sign_dev = 1.0 if dev >= 0 else -1.0

            # Compute effective q2 with runtime permissivity and X WORK asymmetry
            eff_q2 = self.eff_q2[sv]
            # X WORK asymmetry: q2_X = 0.23 in WORK, 0.21 in SPEC/CLOSE
            if sv == 'X' and packet_phase == 'WORK':
                eff_q2 += 0.02  # Shift from 0.21 base to 0.23 in WORK
            if permissivity and sv in permissivity:
                eff_q2 += permissivity[sv]
            # Re-clamp after adjustments
            eff_q2 = max(Q1 + 0.02, min(eff_q2, HAZARD_DEV[sv] - 0.03))

            # Apply config mode corridor multipliers for CLOSE phase on C and S
            corridor_mult_extra = 1.0
            if packet_phase == 'CLOSE':
                if sv == 'C':
                    corridor_mult_extra = self.config['close_corridor_C_mult']
                elif sv == 'S':
                    corridor_mult_extra = self.config['close_corridor_S_mult']

            if abs_dev < Q1:
                # Zone 1: Basin
                rf[i] = self.gamma_basin[sv] * dev * BASIN_MULT[packet_phase][sv]
                zones[i] = 'BASIN'
            elif abs_dev < eff_q2:
                # Zone 2: Corridor
                rf[i] = (self.gamma_corridor[sv] * dev
                         * CORRIDOR_MULT[packet_phase][sv]
                         * corridor_mult_extra)
                zones[i] = 'CORRIDOR'
            else:
                # Zone 3: Edge
                rf[i] = (self.gamma_corridor[sv] * dev
                         * EDGE_MULT[packet_phase][sv]
                         * corridor_mult_extra
                         + BETA[sv] * (abs_dev - eff_q2) ** 2 * sign_dev)
                zones[i] = 'EDGE'

            # Stability limiter: prevent restoring force from overshooting
            # equilibrium (rf magnitude capped at 0.8 * deviation to avoid
            # discrete-time oscillation in edge zone)
            if abs_dev > 1e-10:
                max_rf = 0.8 * abs_dev * sign_dev
                if abs(rf[i]) > abs(max_rf):
                    rf[i] = max_rf

        return rf, zones

    def _discharge_events(self, state, packet_phase, cts):
        """
        Discharge events: CLOSE-only, profile-specific.

        1. CTS Discharge (X->Y + C relief)
        2. Containment Resolution (C->TR, profile-specific)
        3. Thermal Recovery (accelerated T return in CLOSE)
        """
        discharge = [0.0] * N_VARS
        events = []

        if packet_phase != 'CLOSE':
            return discharge, events

        X_IDX = SV_INDEX['X']
        Y_IDX = SV_INDEX['Y']
        C_IDX = SV_INDEX['C']
        TR_IDX = SV_INDEX['TR']
        T_IDX = SV_INDEX['T']

        # 1. CTS Discharge (X->Y + C relief)
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

        # 2. Containment Resolution (C->TR, profile-specific)
        c_dev = abs(state[C_IDX] - EQUILIBRIUM)
        tr_dev = abs(state[TR_IDX] - EQUILIBRIUM)
        if c_dev > Q1 and tr_dev > Q1:
            k = K_RELIEF[self.profile_name]
            rate = k * max(c_dev - Q1, 0.0) * max(tr_dev - Q1, 0.0)
            discharge[C_IDX] -= rate
            discharge[TR_IDX] += rate * 0.3
            # A3 also transfers to Y (distillation semantics)
            if 'A3' in self.profile_name:
                discharge[Y_IDX] += rate * 0.15
            events.append({
                'type': 'CONTAINMENT_RESOLUTION',
                'rate': round(rate, 6),
                'profile': self.profile_name,
            })

        # 3. Thermal Recovery (accelerated T return in CLOSE)
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
        """
        Apply one update step.

        state:        list of 7 floats in [0,1]
        dV:           list of 7 floats (external impulse)
        packet_phase: 'SPEC', 'WORK', or 'CLOSE'
        cts:          cumulative thermal stress (scalar)
        permissivity: optional dict {sv: float} shifting effective q2

        Returns: (new_state, diagnostics_dict)
        """
        # 1. Cross-coupling (with equilibrium bias correction)
        cc_raw = self._cross_coupling(state, packet_phase)
        bias = self.equil_bias[packet_phase]
        cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]

        # 2. Restoring force
        rf, zones = self._restoring_force(state, packet_phase, permissivity)

        # 3. Discharge events
        discharge, events = self._discharge_events(state, packet_phase, cts)

        # 4. State update
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
# X WORK asymmetry in q2
# ---------------------------------------------------------------------------
def _get_q2_base_for_phase(sv, packet_phase):
    """X has asymmetric q2: 0.23 in WORK, 0.21 otherwise."""
    if sv == 'X' and packet_phase == 'WORK':
        return 0.23
    return Q2_BASE[sv]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_configured_apparatus(profile_name, config_mode):
    """
    Build a SelectiveRestorationApparatus with given profile and config mode.

    1. Look up profile sensitivity and decay rates
    2. Apply profile scaling to gamma_basin and gamma_corridor
    3. Apply config mode shifts
    4. Return configured instance
    """
    profile = PROFILES[profile_name]
    sensitivity = {sv: profile[f'sensitivity_{sv}'] for sv in STATE_VARS}
    decay_rates = PROFILE_DECAYS[profile_name]
    return SelectiveRestorationApparatus(profile_name, config_mode,
                                         sensitivity, decay_rates)


# ---------------------------------------------------------------------------
# Composite headless regime score
# ---------------------------------------------------------------------------
def compute_infra_scores(pilot_folios):
    """
    Compute composite infrastructure scores from folio budget data.

    Returns dict: {folio: {hl_rate, pseudo_l_frac, parametric_cpf_frac,
                           suffix_bifurc, infra_score, config_mode}}
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

    # Min-max normalize each metric across the pilot folios
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

    # Assign config modes by tertile
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


# ---------------------------------------------------------------------------
# Self-tests V1-V8
# ---------------------------------------------------------------------------

def test_v1_stable_equilibrium():
    """
    V1: Stable equilibrium.
    Start at [0.5]*7. Apply 50 STABILITY tokens (dV near zero).
    All SVs stay within +/-0.01 of 0.5.
    """
    print("\n  V1: Stable Equilibrium")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = [0.0] * N_VARS  # Near-zero input
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
    """
    V2: Hazard approach.
    Apply sustained large dV (P99 level) toward hazard for 100 tokens
    under WORK phase. State approaches but does NOT cross hazard boundary.
    Check each process SV.
    """
    print("\n  V2: Hazard Approach (P99 sustained, 100 tokens)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS

    # Build P99-level dV pushing toward upper hazard for process SVs
    dv = make_dv_multi(P99_DV)

    max_vals = {sv: EQUILIBRIUM for sv in STATE_VARS}
    passed = True

    for step in range(100):
        state, diag = app.update(state, dv, packet_phase='WORK')
        for i, sv in enumerate(STATE_VARS):
            max_vals[sv] = max(max_vals[sv], state[i])

    # Check no hazard breach for process SVs
    details = {}
    for sv in STATE_VARS:
        lo, hi = HAZARD_BOUNDARIES[sv]
        breached = False
        if hi is not None and max_vals[sv] >= hi:
            breached = True
        if lo is not None and (1.0 - max_vals[sv]) <= (1.0 - lo):
            # Check lower bound too (for SVs pushed low)
            pass  # We're pushing positive, so only check upper
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
    """
    V3: Y monotonic accumulation.
    Apply 100 tokens with positive Y dV (0.01). Y must increase monotonically.
    """
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
    """
    V4: CLOSE recovers faster than WORK.
    Push T to corridor (dev ~0.15), then apply zero dV.
    Run 20 tokens under WORK -> record recovery.
    Reset. Run 20 tokens under CLOSE -> record recovery.
    CLOSE must recover faster.
    """
    print("\n  V4: CLOSE Recovers Faster Than WORK")

    T_IDX = SV_INDEX['T']
    initial_dev = 0.15
    initial_state = [EQUILIBRIUM] * N_VARS
    initial_state[T_IDX] = EQUILIBRIUM + initial_dev
    dv_zero = [0.0] * N_VARS

    # WORK recovery
    app_work = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state_work = list(initial_state)
    work_devs = [abs(state_work[T_IDX] - EQUILIBRIUM)]
    for step in range(20):
        state_work, _ = app_work.update(state_work, dv_zero, packet_phase='WORK')
        work_devs.append(abs(state_work[T_IDX] - EQUILIBRIUM))

    # CLOSE recovery
    app_close = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state_close = list(initial_state)
    close_devs = [abs(state_close[T_IDX] - EQUILIBRIUM)]
    for step in range(20):
        state_close, _ = app_close.update(state_close, dv_zero, packet_phase='CLOSE')
        close_devs.append(abs(state_close[T_IDX] - EQUILIBRIUM))

    # Compare: CLOSE final deviation should be smaller
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


def test_v5_edge_barrier():
    """
    V5: Edge barrier prevents hazard violation. HARD GATE.
    Push state to edge zone (dev = q2 + 0.02) for T and X.
    Apply sustained P99 dV toward hazard for 50 tokens.
    State must NOT cross hazard boundary.
    """
    print("\n  V5: Edge Barrier Prevents Hazard (HARD GATE)")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    T_IDX = SV_INDEX['T']
    X_IDX = SV_INDEX['X']

    # Start at edge zone (use WORK-phase q2 for X: 0.23 instead of 0.21)
    state = [EQUILIBRIUM] * N_VARS
    state[T_IDX] = EQUILIBRIUM + app.eff_q2['T'] + 0.02
    x_work_q2 = app.eff_q2['X'] + 0.02  # X WORK asymmetry: +0.02
    state[X_IDX] = EQUILIBRIUM + x_work_q2 + 0.02

    # P99-level dV toward hazard for T and X
    dv = make_dv_multi({
        'T': P99_DV['T'],
        'X': P99_DV['X'],
    })

    passed = True
    max_t = state[T_IDX]
    max_x = state[X_IDX]

    for step in range(50):
        state, diag = app.update(state, dv, packet_phase='WORK')
        max_t = max(max_t, state[T_IDX])
        max_x = max(max_x, state[X_IDX])

        # Check hazard boundaries
        if HAZARD_BOUNDARIES['T'][1] is not None and state[T_IDX] >= HAZARD_BOUNDARIES['T'][1]:
            passed = False
        if HAZARD_BOUNDARIES['X'][1] is not None and state[X_IDX] >= HAZARD_BOUNDARIES['X'][1]:
            passed = False

    status = "PASS" if passed else "FAIL"
    print(f"    {status}: max_T={max_t:.4f} (hazard={HAZARD_BOUNDARIES['T'][1]}), "
          f"max_X={max_x:.4f} (hazard={HAZARD_BOUNDARIES['X'][1]})")
    if not passed:
        print("    *** HARD GATE FAILED ***")

    return passed, {
        'pass': passed,
        'max_T': round(max_t, 4),
        'max_X': round(max_x, 4),
        'T_hazard': HAZARD_BOUNDARIES['T'][1],
        'X_hazard': HAZARD_BOUNDARIES['X'][1],
    }


def test_v6_config_mode_differentiates():
    """
    V6: Config mode differentiates.
    Build H0 and H2 apparatus. Apply same token sequence.
    H2 must have wider effective q2 for C and S than H0.
    """
    print("\n  V6: Config Mode Differentiates")
    app_h0 = build_configured_apparatus('A3_DISTILL_COLLECT', 'H0_LOW_INFRA')
    app_h2 = build_configured_apparatus('A3_DISTILL_COLLECT', 'H2_HIGH_INFRA')

    # Check q2 values
    h0_q2_C = app_h0.eff_q2['C']
    h2_q2_C = app_h2.eff_q2['C']
    h0_q2_S = app_h0.eff_q2['S']
    h2_q2_S = app_h2.eff_q2['S']

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
    """
    V7: Bounded excursion cycle.
    Alternate 15 WORK tokens (with P90-level dV for T,X,C) then 15 CLOSE
    tokens (zero dV). Run 4 cycles (120 tokens).
    Must see at least 2 bounded excursion cycles where state exits basin
    (dev > q1) during WORK and returns to basin during CLOSE.
    """
    print("\n  V7: Bounded Excursion Cycle")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')

    # P90-level dV scaled by sensitivity
    dv_work = make_dv_multi({
        'T': P90_DV['T'],
        'X': P90_DV['X'],
        'C': P90_DV['C'],
    })
    dv_close = [0.0] * N_VARS

    state = [EQUILIBRIUM] * N_VARS
    # Track basin exits and returns
    # Process SVs only (those with hazard boundaries)
    process_svs = [sv for sv in STATE_VARS
                   if HAZARD_BOUNDARIES[sv][0] is not None
                   or HAZARD_BOUNDARIES[sv][1] is not None]

    bounded_cycles = 0
    trajectory_info = []

    for cycle in range(4):
        # WORK phase: 15 tokens
        exited_basin = False
        for step in range(15):
            state, diag = app.update(state, dv_work, packet_phase='WORK')
            for sv in process_svs:
                if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) > Q1:
                    exited_basin = True

        work_end_devs = {sv: round(abs(state[SV_INDEX[sv]] - EQUILIBRIUM), 4)
                         for sv in process_svs}

        # CLOSE phase: 15 tokens
        for step in range(15):
            state, diag = app.update(state, dv_close, packet_phase='CLOSE')

        close_end_devs = {sv: round(abs(state[SV_INDEX[sv]] - EQUILIBRIUM), 4)
                          for sv in process_svs}

        # Check if returned to basin
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

    return passed, {
        'pass': passed,
        'bounded_cycles': bounded_cycles,
        'trajectory': trajectory_info,
    }


def test_v8a_p50_stays_in_basin():
    """
    V8a: P50 input stays in basin.
    Apply 30 WORK tokens with P50-level dV.
    Max deviation for any process SV must stay below q1 (0.08).
    """
    print("\n  V8a: P50 Input Stays in Basin")
    app = build_configured_apparatus('A3_DISTILL_COLLECT', 'H1_MEDIUM_INFRA')
    state = [EQUILIBRIUM] * N_VARS
    dv = make_dv_multi(P50_DV)

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

    passed = max_dev < Q1
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: max_dev={max_dev:.6f} ({max_dev_sv}), threshold={Q1}")
    return passed, {
        'pass': passed,
        'max_deviation': round(max_dev, 6),
        'max_deviation_sv': max_dev_sv,
    }


def test_v8b_p90_enters_corridor():
    """
    V8b: P90 input enters corridor. HARD GATE.
    Apply 10 WORK tokens with P90-level dV for T.
    T deviation must exceed q1 within 5 tokens.
    """
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
            entry_step = step + 1  # 1-indexed

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
    """
    V8c: P99 input reaches edge but not hazard.
    Apply 30 WORK tokens with P99-level dV for T.
    T must reach edge zone (dev >= q2) but not hazard.
    """
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
        if t_dev >= app.eff_q2['T']:
            reached_edge = True
        if HAZARD_BOUNDARIES['T'][1] is not None and state[T_IDX] >= HAZARD_BOUNDARIES['T'][1]:
            breached_hazard = True

    passed = reached_edge and not breached_hazard
    status = "PASS" if passed else "FAIL"
    print(f"    {status}: reached_edge={reached_edge}, breached_hazard={breached_hazard}, "
          f"max_T_dev={max_t_dev:.4f}, q2_T={app.eff_q2['T']:.4f}, "
          f"hazard_T={HAZARD_BOUNDARIES['T'][1]}")
    return passed, {
        'pass': passed,
        'reached_edge': reached_edge,
        'breached_hazard': breached_hazard,
        'max_T_dev': round(max_t_dev, 4),
        'q2_T': round(app.eff_q2['T'], 4),
    }


def test_v8d_work_close_bounded_cycles():
    """
    V8d: WORK->CLOSE bounded cycles with realistic dV. HARD GATE.
    Alternate 20 WORK tokens (P90 dV for T,X,C) and 20 CLOSE tokens (zero dV).
    Run 6 cycles (240 tokens). Must see >=2 bounded excursion cycles.
    """
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
        # WORK phase: 20 tokens
        exited_basin = False
        for step in range(20):
            state, _ = app.update(state, dv_work, packet_phase='WORK')
            for sv in process_svs:
                if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) > Q1:
                    exited_basin = True

        # CLOSE phase: 20 tokens
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
    """
    V8e: Zero input stays in basin. HARD GATE.
    Start at equilibrium. Apply 100 tokens with zero dV.
    Cross-coupling alone must NOT push any SV past q1.
    """
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
    """
    V8f: Sustained P99 stress test (informational).
    Apply 200 WORK tokens with P99-level dV for all process SVs under
    randomized phase sequence. Report max deviation and near-hazard status.
    NOT a hard gate.
    """
    import random
    print("\n  V8f: Sustained P99 Stress Test (informational)")
    random.seed(42)  # Reproducible

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
            # Check if within 0.03 of hazard
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    project_root = phase_dir.parent.parent
    output_path = phase_dir / 'results' / 't1_selective_restoration_apparatus.json'

    print("=" * 70)
    print("T1: Selective Restoration Apparatus")
    print("Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION")
    print("=" * 70)

    # --- Run self-tests ---
    print("\n--- Self-Tests ---")
    test_results = {}
    all_pass = True
    hard_gate_pass = True

    # V1
    v1_pass, v1_detail = test_v1_stable_equilibrium()
    test_results['V1'] = v1_detail
    all_pass = all_pass and v1_pass

    # V2
    v2_pass, v2_detail = test_v2_hazard_approach()
    test_results['V2'] = v2_detail
    all_pass = all_pass and v2_pass

    # V3
    v3_pass, v3_detail = test_v3_y_monotonic()
    test_results['V3'] = v3_detail
    all_pass = all_pass and v3_pass

    # V4
    v4_pass, v4_detail = test_v4_close_recovers_faster()
    test_results['V4'] = v4_detail
    all_pass = all_pass and v4_pass

    # V5 (HARD GATE)
    v5_pass, v5_detail = test_v5_edge_barrier()
    test_results['V5'] = v5_detail
    all_pass = all_pass and v5_pass
    if not v5_pass:
        hard_gate_pass = False

    # V6
    v6_pass, v6_detail = test_v6_config_mode_differentiates()
    test_results['V6'] = v6_detail
    all_pass = all_pass and v6_pass

    # V7
    v7_pass, v7_detail = test_v7_bounded_excursion_cycle()
    test_results['V7'] = v7_detail
    all_pass = all_pass and v7_pass

    # V8a
    v8a_pass, v8a_detail = test_v8a_p50_stays_in_basin()
    test_results['V8a'] = v8a_detail
    all_pass = all_pass and v8a_pass

    # V8b (HARD GATE)
    v8b_pass, v8b_detail = test_v8b_p90_enters_corridor()
    test_results['V8b'] = v8b_detail
    all_pass = all_pass and v8b_pass
    if not v8b_pass:
        hard_gate_pass = False

    # V8c
    v8c_pass, v8c_detail = test_v8c_p99_reaches_edge_not_hazard()
    test_results['V8c'] = v8c_detail
    all_pass = all_pass and v8c_pass

    # V8d (HARD GATE)
    v8d_pass, v8d_detail = test_v8d_work_close_bounded_cycles()
    test_results['V8d'] = v8d_detail
    all_pass = all_pass and v8d_pass
    if not v8d_pass:
        hard_gate_pass = False

    # V8e (HARD GATE)
    v8e_pass, v8e_detail = test_v8e_zero_input_stays_in_basin()
    test_results['V8e'] = v8e_detail
    all_pass = all_pass and v8e_pass
    if not v8e_pass:
        hard_gate_pass = False

    # V8f (informational)
    v8f_pass, v8f_detail = test_v8f_sustained_p99_stress()
    test_results['V8f'] = v8f_detail

    # --- Summary ---
    print("\n--- Self-Test Summary ---")
    hard_gates = {'V5', 'V8b', 'V8d', 'V8e'}
    for name, detail in test_results.items():
        if detail['pass'] is None:
            status = "INFO"
        elif detail['pass']:
            status = "PASS"
        else:
            status = "FAIL"
        gate = " (HARD GATE)" if name in hard_gates else ""
        print(f"  {name}: {status}{gate}")

    if hard_gate_pass:
        print("\n  ALL HARD GATES PASSED")
    else:
        print("\n  *** HARD GATE(S) FAILED — aborting ***")
        sys.exit(1)

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
            'phase': '564b',
            'task': 'T1',
            'timestamp': datetime.now().isoformat(),
        },
        'apparatus_config': {
            'Q1': Q1,
            'Q2_BASE': Q2_BASE,
            'HAZARD_DEV': HAZARD_DEV,
            'GAMMA_BASIN': GAMMA_BASIN,
            'GAMMA_CORRIDOR': GAMMA_CORRIDOR,
            'BETA': BETA,
            'A3_DECAY': A3_DECAY,
            'PROFILE_DECAYS': PROFILE_DECAYS,
            'BASIN_MULT': BASIN_MULT,
            'CORRIDOR_MULT': CORRIDOR_MULT,
            'EDGE_MULT': EDGE_MULT,
            'K_RELIEF': K_RELIEF,
            'CONFIG_MODES': CONFIG_MODES,
            'PHASE_CC_MULT': PHASE_CC_MULT,
        },
        'folio_infra_scores': infra_scores,
        'self_tests': test_results,
        'hard_gate_pass': hard_gate_pass,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {output_path}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")

    return 0 if all_pass else 1


if __name__ == '__main__':
    raise SystemExit(main())
