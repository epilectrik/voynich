"""
T2: Folio-Specific Apparatus Library
Phase 570a - FOLIO_SPECIFIC_APPARATUS_PILOT

Implements FolioSpecificApparatus: a CloseRecoveryApparatus subclass that
applies five continuous folio-specific scaling axes (F1-F5) on top of the
generic close-recovery physics.  Also implements demand-matched null
construction for permutation testing.

This is a LIBRARY MODULE — no main(), no output files.

F-axis summary
--------------
  F1  Attractor / Forgiveness   — scales restoring force strength (basin + corridor gamma)
  F2  Closure Exploitability    — scales CLOSE recovery coefficients (K_CLOSE, K_CTS_CLOSE, R5 bonus)
  F3  Thermal Accent            — modulates thermal sensitivity, WORK T tolerance, CLOSE T drawdown
  F4  Continuous Headless Infra — replaces discrete H0/H1/H2 config with continuous interpolation
  F5  Containment Responsiveness— scales containment relief and C/TR/X sensitivity in CLOSE

Identity guarantee: when f1=f2=f3=f5=1.0 and f4_raw matches the original
config mode (H0→0.0, H1→0.5, H2→1.0), the FolioSpecificApparatus produces
IDENTICAL output to a generic CloseRecoveryApparatus with that config mode.
"""

import copy
import math
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Imports from parent apparatus hierarchy
# ---------------------------------------------------------------------------
_project_root = str(Path(__file__).resolve().parents[3])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_close_recovery_dir = str(
    Path(__file__).resolve().parents[2]
    / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY' / 'scripts'
)
if _close_recovery_dir not in sys.path:
    sys.path.insert(0, _close_recovery_dir)

from t1_close_recovery_apparatus import (
    CloseRecoveryApparatus,
    PermeabilityApparatus,
    build_close_recovery_apparatus,
    STATE_VARS, N_VARS, EQUILIBRIUM, SV_INDEX,
    Q1, Q2_BASE, Q3_BASE, HAZARD_DEV,
    GAMMA_BASIN, GAMMA_CORRIDOR,
    BETA1, BETA2,
    BASIN_MULT, CORRIDOR_MULT, EDGE1_MULT, EDGE2_MULT,
    K_CLOSE, CTS_WEIGHTED_SVS, PROFILE_CLOSE_MULT,
    K_CTS_CLOSE as K_CTS_CLOSE_DEFAULT,
    K_RELIEF, K_RELIEF_CLOSE as K_RELIEF_CLOSE_MAP,
    R4_X_TO_Y, R4_C_TO_Y,
    R5_MULTI_SV_BONUS, R5_CTS_THRESHOLD,
    CONFIG_MODES,
    PROFILES, PROFILE_DECAYS, A3_DECAY,
    HAZARD_BOUNDARIES,
    make_dv, make_dv_multi,
)

# Import shared_metrics constants (canonical source of truth)
_eventive_dir = str(
    Path(__file__).resolve().parents[2]
    / 'EVENTIVE_CLOSURE_PACKETS' / 'scripts'
)
if _eventive_dir not in sys.path:
    sys.path.insert(0, _eventive_dir)

from shared_metrics import (
    Q1 as SM_Q1,
    Q2_BASE as SM_Q2_BASE,
    STATE_VARS as SM_STATE_VARS,
    PROCESS_SVS,
    EQUILIBRIUM as SM_EQUILIBRIUM,
)


# ---------------------------------------------------------------------------
# F4 continuous interpolation endpoints
# ---------------------------------------------------------------------------
_CONFIG_H0 = CONFIG_MODES['H0_LOW_INFRA']
_CONFIG_H2 = CONFIG_MODES['H2_HIGH_INFRA']

# Map discrete config modes to their f4_raw equivalents
_CONFIG_MODE_TO_F4 = {
    'H0_LOW_INFRA': 0.0,
    'H1_MEDIUM_INFRA': 0.5,
    'H2_HIGH_INFRA': 1.0,
}

# Config parameter keys for interpolation
_CONFIG_INTERP_KEYS = [
    'q2_C_shift', 'q2_S_shift',
    'gamma_basin_C_mult', 'gamma_basin_S_mult',
    'cts_discharge_mult',
    'close_corridor_C_mult', 'close_corridor_S_mult',
]


def _interpolate_config(f4_raw):
    """Linearly interpolate all config parameters between H0 (f4=0) and H2 (f4=1).

    Returns a config dict with the same keys as CONFIG_MODES entries.
    """
    result = {}
    for key in _CONFIG_INTERP_KEYS:
        h0_val = _CONFIG_H0[key]
        h2_val = _CONFIG_H2[key]
        result[key] = h0_val + f4_raw * (h2_val - h0_val)
    return result


# ===========================================================================
# FolioSpecificApparatus
# ===========================================================================
class FolioSpecificApparatus(CloseRecoveryApparatus):
    """CloseRecoveryApparatus with five continuous folio-specific scaling axes.

    The parent's update() method is inherited unchanged.  F1-F5 work by
    modifying the instance variables that the inherited _restoring_force()
    and _apply_close_recovery() already read at runtime.

    Where the parent reads module-level constants (BASIN_MULT, CORRIDOR_MULT,
    K_CLOSE, R5_MULTI_SV_BONUS), this subclass shadows them with instance
    copies so that F-axis scaling is per-instance.

    Parameters
    ----------
    profile : str
        'A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', or 'A3_DISTILL_COLLECT'
    config_mode : str
        Base config mode — used only as the F4 reference.  The parent is
        always initialised with H1_MEDIUM_INFRA (neutral); F4 then applies
        continuous interpolation.
    folio : str
        Folio identifier (for logging / diagnostics).
    f1 : float
        Attractor/forgiveness scaling (typically 0.7–1.4).
    f2 : float
        Closure exploitability scaling.
    f3 : float
        Thermal accent scaling.
    f4_raw : float
        Continuous headless infrastructure position in [0, 1].
        0.0 = H0_LOW_INFRA, 0.5 = H1_MEDIUM_INFRA, 1.0 = H2_HIGH_INFRA.
    f5 : float
        Containment / transition responsiveness scaling.
    r1_scale, k_cts, k_relief_scale : float
        Passed through to CloseRecoveryApparatus.
    """

    def __init__(self, profile, config_mode, folio, f1, f2, f3, f4_raw, f5,
                 r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0):
        # Resolve profile sensitivity and decay for parent constructor
        profile_params = PROFILES[profile]
        sensitivity = {sv: profile_params[f'sensitivity_{sv}'] for sv in STATE_VARS}
        decay_rates = PROFILE_DECAYS[profile]

        # --- Always initialise parent with H1 (neutral) so F4 can apply
        #     continuous interpolation from a clean baseline. ---
        super().__init__(
            profile_name=profile,
            config_mode='H1_MEDIUM_INFRA',
            sensitivity=sensitivity,
            decay_rates=decay_rates,
            r1_scale=r1_scale,
            k_cts=k_cts,
            k_relief_scale=k_relief_scale,
            enable_close_recovery=True,
        )

        self.folio = folio
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4_raw = f4_raw
        self.f5 = f5
        self.original_config_mode = config_mode

        # --- Create instance-level copies of module constants that the
        #     inherited physics methods use.  The overridden _restoring_force
        #     and _apply_close_recovery will read these instead. ---
        self.k_close = {sv: v for sv, v in K_CLOSE.items()}
        self.r5_bonus = R5_MULTI_SV_BONUS
        self.basin_mult = {
            phase: {sv: v for sv, v in svs.items()}
            for phase, svs in BASIN_MULT.items()
        }
        self.corridor_mult = {
            phase: {sv: v for sv, v in svs.items()}
            for phase, svs in CORRIDOR_MULT.items()
        }
        self.sensitivities = dict(sensitivity)

        # --- Apply F-axes in order ---
        self._apply_f1(f1)
        self._apply_f2(f2)
        self._apply_f3(f3)
        self._apply_f4(f4_raw)
        self._apply_f5(f5)

    # -----------------------------------------------------------------
    # F1: Attractor / Forgiveness (response-only, NO topology change)
    # -----------------------------------------------------------------
    def _apply_f1(self, f1):
        """Scale restoring-force gammas.  Does NOT change Q2 boundaries.

        Basin gamma scales linearly with f1; corridor gamma scales with
        sqrt(f1) to preserve the basin/corridor force ratio roughly.
        Y has no restoring force and is skipped.
        """
        for sv in STATE_VARS:
            if sv == 'Y':
                continue  # Y has no restoring force
            self.gamma_basin[sv] *= f1
            self.gamma_corridor[sv] *= math.sqrt(f1)

    # -----------------------------------------------------------------
    # F2: Closure Exploitability (clean separation from F5)
    # -----------------------------------------------------------------
    def _apply_f2(self, f2):
        """Scale closure recovery coefficients.

        Modifies K_CLOSE (R1 per-SV drawdown), K_CTS_CLOSE (R2 CTS
        transfer), and R5 multi-SV coordination bonus.  Does NOT touch
        K_RELIEF_CLOSE (that is F5's domain).
        """
        for sv in self.k_close:
            self.k_close[sv] *= f2
        self.k_cts_close *= f2
        self.r5_bonus *= f2

    # -----------------------------------------------------------------
    # F3: Thermal Accent (work tolerance + close demand)
    # -----------------------------------------------------------------
    def _apply_f3(self, f3):
        """Modulate thermal sensitivity, WORK-phase T tolerance, and
        CLOSE-phase T drawdown.

        Three sub-effects:
          1. self.sensitivities['T'] *= f3  (overall T sensitivity)
          2. BASIN_MULT['WORK']['T'] scaled by (1 + 0.3*(f3-1))
          3. k_close['T'] scaled by (1 + 0.2*(f3-1))
        """
        self.sensitivities['T'] *= f3
        self.basin_mult['WORK']['T'] *= (1 + 0.3 * (f3 - 1.0))
        self.k_close['T'] *= (1 + 0.2 * (f3 - 1.0))

    # -----------------------------------------------------------------
    # F4: Continuous Headless Infrastructure
    # -----------------------------------------------------------------
    def _apply_f4(self, f4_raw):
        """Replace the discrete H0/H1/H2 config with continuous interpolation.

        Since the parent was initialised with H1 (neutral, all multipliers
        = 1.0, all shifts = 0.0), this method applies the continuously
        interpolated config from scratch.

        Affects: q2 boundaries (C, S), gamma_basin (C, S), cts_discharge_mult,
        close_corridor multipliers (C, S).
        """
        cfg = _interpolate_config(f4_raw)

        # Store the interpolated config for runtime use
        self.config = cfg

        # --- Q2 shifts (C and S only) ---
        # Parent with H1 applied zero shift, so current q2 = base values.
        # Apply the continuous shift.
        for sv_key, shift_key in [('C', 'q2_C_shift'), ('S', 'q2_S_shift')]:
            base = Q2_BASE[sv_key]
            q2_new = base + cfg[shift_key]
            q2_new = max(Q1 + 0.02, min(q2_new, HAZARD_DEV[sv_key] - 0.03))
            self.q2[sv_key] = q2_new

        # --- Gamma basin multipliers (C, S) ---
        # Parent with H1 applied mult = 1.0.  We need to apply the continuous
        # multiplier.  The parent computed gamma_basin as:
        #   GAMMA_BASIN[sv] * (decay/A3_DECAY) * config_mult
        # With H1, config_mult was 1.0.  Now apply the continuous config_mult.
        scale_C = self.decay_rates['C'] / A3_DECAY['C']
        scale_S = self.decay_rates['S'] / A3_DECAY['S']
        # Undo H1 mult (1.0 — no-op) and apply continuous mult
        # But F1 already scaled gamma_basin.  We need the pre-F1 base value
        # for C and S, then apply both F1 and F4.
        # Actually, F1 already multiplied gamma_basin by f1.  The H1 mult
        # was 1.0 so nothing to undo.  The continuous config mult should
        # multiply on top of whatever F1 already did.
        # Pre-F1 gamma_basin[C] = GAMMA_BASIN[C] * scale_C * 1.0 (H1)
        # After F1:              = GAMMA_BASIN[C] * scale_C * f1
        # F4 wants:              = GAMMA_BASIN[C] * scale_C * f1 * cfg_mult
        # So multiply current by cfg_mult / 1.0 = cfg_mult
        self.gamma_basin['C'] *= cfg['gamma_basin_C_mult']
        self.gamma_basin['S'] *= cfg['gamma_basin_S_mult']

    # -----------------------------------------------------------------
    # F5: Containment / Transition Responsiveness
    # -----------------------------------------------------------------
    def _apply_f5(self, f5):
        """Scale containment relief and C/TR/X responsiveness in CLOSE.

        Four sub-effects:
          1. k_relief_close *= f5
          2. sensitivities['C'] modulated by f5
          3. sensitivities['TR'] modulated by f5
          4. CORRIDOR_MULT['CLOSE']['C'] and ['X'] scaled by f5
        """
        self.k_relief_close *= f5
        self.sensitivities['C'] *= (1 + 0.3 * (f5 - 1.0))
        self.sensitivities['TR'] *= (1 + 0.2 * (f5 - 1.0))
        self.corridor_mult['CLOSE']['C'] *= f5
        self.corridor_mult['CLOSE']['X'] *= f5

    # -----------------------------------------------------------------
    # Override _restoring_force to use instance-level basin_mult / corridor_mult
    # -----------------------------------------------------------------
    def _restoring_force(self, state, packet_phase='WORK', permissivity=None):
        """Identical to PermeabilityApparatus._restoring_force except it reads
        self.basin_mult and self.corridor_mult (instance copies) instead of
        the module-level BASIN_MULT and CORRIDOR_MULT constants.
        """
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
                restoring[i] = (self.gamma_basin[sv] * dev
                                * self.basin_mult[packet_phase][sv])
                zones[i] = 'BASIN'
            elif abs_dev < eff_q2:
                restoring[i] = (self.gamma_corridor[sv] * dev
                                * self.corridor_mult[packet_phase][sv]
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

    # -----------------------------------------------------------------
    # Override _apply_close_recovery to use instance-level k_close / r5_bonus
    # -----------------------------------------------------------------
    def _apply_close_recovery(self, state, packet_phase, cts, dv_magnitude=0.0):
        """Identical to CloseRecoveryApparatus._apply_close_recovery except
        it reads self.k_close and self.r5_bonus (instance copies) instead of
        the module-level K_CLOSE and R5_MULTI_SV_BONUS constants.
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

            k = self.k_close.get(sv, 0.0) * self.r1_scale
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

        # Clean-CLOSE multiplier
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
                recovery[x_idx] -= rate * x_sign
                recovery[SV_INDEX['Y']] += rate * 0.7 * clean_close_mult
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
                recovery[SV_INDEX['Y']] += rate * 0.15 * clean_close_mult
            details['R3'] = {'rate': round(rate, 6)}

        # R4: Quality-conditioned Y accumulation
        x_recovery = abs(details['R1'].get('X', 0.0))
        c_recovery = abs(details['R1'].get('C', 0.0))
        r4_y = cts * (R4_X_TO_Y * x_recovery + R4_C_TO_Y * c_recovery) * clean_close_mult
        if r4_y > 0:
            recovery[SV_INDEX['Y']] += r4_y
            details['R4'] = {'y_gain': round(r4_y, 6)}

        # R5: Closure-coherent coordination bonus (uses self.r5_bonus)
        n_coherent = len(moving_toward_eq)
        if cts > R5_CTS_THRESHOLD and n_coherent >= 2:
            bonus = 1.0 + self.r5_bonus * (n_coherent - 1)
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

    # -----------------------------------------------------------------
    # Identity verification
    # -----------------------------------------------------------------
    @classmethod
    def verify_identity(cls, profile='A3_DISTILL_COLLECT',
                        config_mode='H1_MEDIUM_INFRA',
                        n_steps=50, verbose=False):
        """Verify that FolioSpecificApparatus with all-neutral F-values
        produces identical output to a generic CloseRecoveryApparatus.

        Parameters
        ----------
        profile : str
            Profile to test.
        config_mode : str
            Config mode to test (H0, H1, or H2).
        n_steps : int
            Number of update steps to compare.
        verbose : bool
            Print per-step comparison.

        Returns
        -------
        bool
            True if all steps match within floating-point tolerance.
        """
        f4_raw = _CONFIG_MODE_TO_F4[config_mode]

        # Build generic apparatus
        generic = build_close_recovery_apparatus(
            profile, config_mode,
            r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0,
            enable_close_recovery=True,
        )

        # Build folio-specific apparatus with all-neutral F-values
        folio_app = cls(
            profile=profile,
            config_mode=config_mode,
            folio='__identity_test__',
            f1=1.0, f2=1.0, f3=1.0, f4_raw=f4_raw, f5=1.0,
            r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0,
        )

        # Run a synthetic trace with perturbation
        state_g = [EQUILIBRIUM] * N_VARS
        state_f = [EQUILIBRIUM] * N_VARS

        # Apply a non-trivial dV pattern to exercise all channels
        dv_pattern = [
            ({'T': 0.03, 'X': 0.02, 'C': 0.01}, 'WORK', 0.0),
            ({'T': 0.02, 'S': -0.01, 'TR': 0.01}, 'WORK', 0.0),
            ({'T': -0.01, 'X': -0.01}, 'CLOSE', 0.6),
            ({}, 'CLOSE', 0.8),
            ({'RC': 0.01}, 'SPEC', 0.0),
        ]

        max_diff = 0.0
        for step in range(n_steps):
            dv_dict, phase, cts = dv_pattern[step % len(dv_pattern)]
            dv = make_dv_multi(dv_dict) if dv_dict else [0.0] * N_VARS

            state_g, diag_g = generic.update(state_g, dv, packet_phase=phase, cts=cts)
            state_f, diag_f = folio_app.update(state_f, dv, packet_phase=phase, cts=cts)

            step_diff = max(abs(g - f) for g, f in zip(state_g, state_f))
            max_diff = max(max_diff, step_diff)

            if verbose and step_diff > 1e-12:
                print(f"  Step {step}: max_diff={step_diff:.2e}")
                for i, sv in enumerate(STATE_VARS):
                    if abs(state_g[i] - state_f[i]) > 1e-12:
                        print(f"    {sv}: generic={state_g[i]:.10f}  "
                              f"folio={state_f[i]:.10f}  "
                              f"diff={state_g[i] - state_f[i]:.2e}")

        passed = max_diff < 1e-10
        if verbose or not passed:
            status = "PASS" if passed else "FAIL"
            print(f"  Identity test ({profile}, {config_mode}): {status}  "
                  f"max_diff={max_diff:.2e}")

        return passed

    @classmethod
    def verify_all_identities(cls, verbose=False):
        """Run identity verification across all profile x config combinations.

        Returns True only if ALL combinations pass.
        """
        all_passed = True
        for profile in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']:
            for config_mode in ['H0_LOW_INFRA', 'H1_MEDIUM_INFRA', 'H2_HIGH_INFRA']:
                passed = cls.verify_identity(
                    profile=profile, config_mode=config_mode,
                    n_steps=50, verbose=verbose,
                )
                if not passed:
                    all_passed = False
        return all_passed


# ===========================================================================
# Demand-Matched Null Construction
# ===========================================================================

def build_demand_matched_assignments(line_states, close_line_indices,
                                     n_permutations=20, k_neighbors=5,
                                     seed=42):
    """Build demand-matched null assignments for a given folio.

    For each real CLOSE line, finds K nearest non-CLOSE lines by
    4D demand signature similarity, then builds permutations by
    randomly selecting matches from the neighbor pools.

    Parameters
    ----------
    line_states : list[dict]
        One dict per line, each with keys:
          - 'line_key': str (e.g. 'f108v|3')
          - 'packet_phase': str ('SPEC', 'WORK', 'CLOSE')
          - 'line_start_state': list[float] (7 SV values at line start)
          - 'work_peak_dev': float (max process SV deviation during non-CLOSE)
          - 'aggregate_dev': float (mean |dev| of process SVs at line start)
          - 'max_sv_dev': float (max |dev| of any process SV at line start)
          - 'n_above_corridor': int (# process SVs above Q2 at line start)
    close_line_indices : list[int]
        Indices into line_states for real CLOSE lines.
    n_permutations : int
        Number of null permutations to generate.
    k_neighbors : int
        Number of nearest neighbors per CLOSE line.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    list[list[tuple[int, int]]]
        List of permutations, each a list of (real_close_idx, matched_non_close_idx)
        pairs.
    """
    if not close_line_indices or len(line_states) < 2:
        return []

    # Identify non-CLOSE line indices
    close_set = set(close_line_indices)
    non_close_indices = [i for i in range(len(line_states))
                         if i not in close_set]

    if not non_close_indices:
        return []

    # --- Step 1: Compute 4D demand signatures ---
    def _demand_signature(ls):
        return [
            ls['aggregate_dev'],
            ls['max_sv_dev'],
            float(ls['n_above_corridor']),
            ls['work_peak_dev'],
        ]

    all_sigs = [_demand_signature(ls) for ls in line_states]

    # --- Step 2: Z-normalize across all lines ---
    n_lines = len(all_sigs)
    n_dims = 4

    # Compute mean and std per dimension
    means = [0.0] * n_dims
    for sig in all_sigs:
        for d in range(n_dims):
            means[d] += sig[d]
    means = [m / n_lines for m in means]

    stds = [0.0] * n_dims
    for sig in all_sigs:
        for d in range(n_dims):
            stds[d] += (sig[d] - means[d]) ** 2
    stds = [math.sqrt(s / n_lines) if n_lines > 1 else 1.0 for s in stds]
    # Avoid division by zero
    stds = [s if s > 1e-10 else 1.0 for s in stds]

    # Normalize
    normed = []
    for sig in all_sigs:
        normed.append([(sig[d] - means[d]) / stds[d] for d in range(n_dims)])

    # --- Step 3: For each CLOSE line, find K nearest non-CLOSE lines ---
    def _euclidean_dist(a, b):
        return math.sqrt(sum((a[d] - b[d]) ** 2 for d in range(n_dims)))

    neighbor_pools = {}  # close_idx -> list of non-close indices (sorted by distance)
    for ci in close_line_indices:
        dists = []
        for ni in non_close_indices:
            d = _euclidean_dist(normed[ci], normed[ni])
            dists.append((d, ni))
        dists.sort(key=lambda x: x[0])
        # Take top K
        k_eff = min(k_neighbors, len(dists))
        neighbor_pools[ci] = [ni for _, ni in dists[:k_eff]]

    # --- Step 4: Build permutations ---
    rng = random.Random(seed)
    permutations = []

    for perm_idx in range(n_permutations):
        assignment = []
        used_in_perm = set()

        # Process CLOSE lines in random order to avoid first-mover bias
        close_order = list(close_line_indices)
        rng.shuffle(close_order)

        for ci in close_order:
            pool = neighbor_pools[ci]
            # Prefer unused matches (without-replacement within permutation)
            available = [ni for ni in pool if ni not in used_in_perm]
            if not available:
                # Allow replacement across CLOSE lines' pools if exhausted
                available = list(pool)
            chosen = rng.choice(available)
            assignment.append((ci, chosen))
            used_in_perm.add(chosen)

        # Sort by close index for deterministic ordering
        assignment.sort(key=lambda x: x[0])
        permutations.append(assignment)

    return permutations
