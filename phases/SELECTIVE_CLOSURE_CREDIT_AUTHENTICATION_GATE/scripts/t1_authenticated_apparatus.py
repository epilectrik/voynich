"""
T1: Authenticated Recovery Apparatus
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Two-layer authentication gate:
  Layer 1: Y-credit gating (R2_Y, R4_Y scaled by auth_mult)
  Layer 2: Cleanliness gain modulation (effective_gain raised for low-auth packets)

AuthenticatedRecoveryApparatus overrides update() to track line boundaries via
a pre-computed call-count map, and _apply_close_recovery() to apply both layers.
No forking of the 770-line enhanced event trace needed.
"""

import json
import sys
import os
import math
import time
import copy
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')

# ---------------------------------------------------------------------------
# Imports from apparatus hierarchy
# ---------------------------------------------------------------------------
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
)
from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    STATE_VARS, N_VARS, EQUILIBRIUM, SV_INDEX, Q1,
    K_CLOSE, CTS_WEIGHTED_SVS, PROFILE_CLOSE_MULT,
    R4_X_TO_Y, R4_C_TO_Y,
    R5_CTS_THRESHOLD,
)
from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace, sort_key, compute_infra_scores,
)


# ===========================================================================
# AuthenticatedRecoveryApparatus
# ===========================================================================
class AuthenticatedRecoveryApparatus(FolioSpecificApparatus):
    """FolioSpecificApparatus with two-layer authentication gate.

    Layer 1 (Y-credit gate): R2_Y and R4_Y multiplied by auth_mult.
    Layer 2 (cleanliness gain modulation): effective_gain = 10 + penalty*(1-auth_mult),
        making "clean closure" harder to earn for low-authentication packets.

    R1, R3 (physical SV restoration), and R5 (coherence bonus) are NOT gated.

    Parameters
    ----------
    acs_threshold : float
        ACS value at which auth_mult = 1.0 (linear clamp: auth_mult = ACS/threshold).
    cleanliness_penalty : float
        Additional gain added to clean_close_mult denominator for counterfeit packets.
        When auth_mult=0, effective gain = 10 + penalty.
    acs_lookup : dict
        {line_key: ACS_value} for per-line authentication scores.
    """

    def __init__(self, profile, config_mode, folio, f1, f2, f3, f4_raw, f5,
                 acs_threshold=0.35, cleanliness_penalty=10.0, acs_lookup=None,
                 r1_scale=1.0, k_cts=6.0, k_relief_scale=3.0):
        super().__init__(profile, config_mode, folio, f1, f2, f3, f4_raw, f5,
                         r1_scale=r1_scale, k_cts=k_cts, k_relief_scale=k_relief_scale)
        self._acs_threshold = acs_threshold
        self._cleanliness_penalty = cleanliness_penalty
        self._acs_lookup = acs_lookup or {}
        self._current_line_acs = 0.5  # neutral default
        self._current_line_key = None
        # Line-boundary tracking (set by prepare_for_trace)
        self._call_count = 0
        self._line_boundaries = {}

    def set_line_context(self, line_key):
        """Update authentication context for current line."""
        self._current_line_key = line_key
        self._current_line_acs = self._acs_lookup.get(line_key, 0.5)

    def _compute_auth_mult(self):
        """Compute authentication multiplier from current line ACS."""
        if self._acs_threshold <= 0:
            return 1.0
        return max(0.0, min(1.0, self._current_line_acs / self._acs_threshold))

    def prepare_for_trace(self, sorted_tokens):
        """Pre-compute line boundaries from sorted token list.

        Must be called BEFORE passing this apparatus to run_enhanced_event_trace().
        Maps each call index to the line_key at that call's line boundary.
        """
        self._call_count = 0
        self._line_boundaries = {}
        prev_line = None
        for i, tok in enumerate(sorted_tokens):
            line = tok.get('line', '?')
            if line != prev_line:
                folio = tok['folio']
                self._line_boundaries[i] = f"{folio}|{line}"
                prev_line = line

    def update(self, state, dV, packet_phase='WORK', cts=0.0, permissivity=None):
        """Override update to inject line context at line boundaries.

        Checks pre-computed line boundary map. When a boundary is crossed,
        calls set_line_context() BEFORE the parent update (which calls
        _apply_close_recovery internally).
        """
        if self._call_count in self._line_boundaries:
            self.set_line_context(self._line_boundaries[self._call_count])
        self._call_count += 1
        return super().update(state, dV, packet_phase, cts, permissivity)

    def _apply_close_recovery(self, state, packet_phase, cts, dv_magnitude=0.0):
        """Two-layer gated CLOSE recovery.

        Identical to FolioSpecificApparatus._apply_close_recovery except:
          Layer 1: R2_Y and R4_Y multiplied by auth_mult
          Layer 2: effective_gain = 10 + penalty*(1-auth_mult) in clean_close_mult
          R3 A3-only Y: gated by sqrt(auth_mult) (soft)
          R1, R5: unchanged
        """
        recovery = [0.0] * N_VARS
        details = {'R1': {}, 'R2': {}, 'R3': {}, 'R4': {}, 'R5': {}, 'AUTH': {}}

        if packet_phase != 'CLOSE' or not self.enable_close_recovery:
            return recovery, details

        auth_mult = self._compute_auth_mult()
        details['AUTH'] = {
            'acs': round(self._current_line_acs, 6),
            'threshold': self._acs_threshold,
            'auth_mult': round(auth_mult, 6),
        }

        # R1: Per-SV CLOSE drawdown (UNCHANGED — not gated)
        active_svs = []
        moving_toward_eq = []

        for sv in ['T', 'RC', 'S', 'C', 'TR', 'X']:
            i = SV_INDEX[sv]
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)

            if abs_dev < 1e-10:
                continue

            if sv == 'S' and dev > 0:
                continue

            k = self.k_close.get(sv, 0.0) * self.r1_scale
            profile_mult = PROFILE_CLOSE_MULT[self.profile_name].get(sv, 1.0)

            cts_weight = 1.0
            if sv in CTS_WEIGHTED_SVS:
                cts_weight = 0.5 + 0.5 * max(0.0, min(1.0, cts))

            r1_amount = k * profile_mult * cts_weight * abs_dev
            r1_amount = min(r1_amount, abs_dev)

            sign = 1.0 if dev > 0 else -1.0
            recovery[i] -= r1_amount * sign

            details['R1'][sv] = round(r1_amount, 6)

            if abs_dev > Q1:
                active_svs.append(sv)
                moving_toward_eq.append(sv)

        # LAYER 2: Modulated cleanliness gain
        effective_gain = 10.0 + self._cleanliness_penalty * (1.0 - auth_mult)
        clean_close_mult = 1.0 / (1.0 + effective_gain * dv_magnitude)
        details['AUTH']['effective_gain'] = round(effective_gain, 4)
        details['AUTH']['clean_close_mult'] = round(clean_close_mult, 6)

        # R2: CTS X->Y transfer (Y credit GATED — Layer 1)
        if cts > 0.3:
            x_idx = SV_INDEX['X']
            x_dev = abs(state[x_idx] - EQUILIBRIUM)
            if x_dev > Q1:
                rate = self.k_cts_close * (cts - 0.3) * max(x_dev - Q1, 0.0)
                rate *= self.config.get('cts_discharge_mult', 1.0)
                x_sign = 1.0 if state[x_idx] > EQUILIBRIUM else -1.0
                recovery[x_idx] -= rate * x_sign
                # LAYER 1: Y credit gated by auth_mult
                recovery[SV_INDEX['Y']] += rate * 0.7 * clean_close_mult * auth_mult
                c_idx = SV_INDEX['C']
                c_sign = 1.0 if state[c_idx] > EQUILIBRIUM else -1.0
                recovery[c_idx] -= rate * 0.3 * c_sign
                details['R2'] = {'rate': round(rate, 6), 'cts': round(cts, 4)}

        # R3: Containment-TR relief (Y component SOFT-GATED for A3)
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
                # R3 Y minor: gate softly with sqrt(auth_mult)
                recovery[SV_INDEX['Y']] += rate * 0.15 * clean_close_mult * (auth_mult ** 0.5)
            details['R3'] = {'rate': round(rate, 6)}

        # R4: Quality-conditioned Y accumulation (GATED — Layer 1)
        x_recovery = abs(details['R1'].get('X', 0.0))
        c_recovery = abs(details['R1'].get('C', 0.0))
        r4_y = cts * (R4_X_TO_Y * x_recovery + R4_C_TO_Y * c_recovery) * clean_close_mult * auth_mult
        if r4_y > 0:
            recovery[SV_INDEX['Y']] += r4_y
            details['R4'] = {'y_gain': round(r4_y, 6)}

        # R5: Closure-coherent coordination bonus (UNCHANGED — not gated)
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


# ===========================================================================
# Factory
# ===========================================================================
def create_authenticated_apparatus(folio, profile, f_params, acs_threshold,
                                    cleanliness_penalty, acs_lookup):
    """Create an AuthenticatedRecoveryApparatus from F-parameters.

    Parameters
    ----------
    folio : str
    profile : str
    f_params : dict with keys f1, f2, f3, f4_raw, f5, config_mode
    acs_threshold : float
    cleanliness_penalty : float
    acs_lookup : dict {line_key: ACS}

    Returns
    -------
    AuthenticatedRecoveryApparatus
    """
    return AuthenticatedRecoveryApparatus(
        profile=profile,
        config_mode=f_params['config_mode'],
        folio=folio,
        f1=f_params['f1'],
        f2=f_params['f2'],
        f3=f_params['f3'],
        f4_raw=f_params['f4_raw'],
        f5=f_params['f5'],
        acs_threshold=acs_threshold,
        cleanliness_penalty=cleanliness_penalty,
        acs_lookup=acs_lookup,
    )


# ===========================================================================
# Helper: run_authenticated_event_trace
# ===========================================================================
def run_authenticated_event_trace(apparatus, tokens, line_packets, cts_data,
                                   event_map):
    """Run enhanced event trace with line-context-aware authentication gate.

    Call prepare_for_trace on the apparatus, then delegate to the library
    run_enhanced_event_trace. The apparatus's overridden update() will
    automatically set line context at each line boundary.
    """
    sorted_tokens = sorted(tokens, key=sort_key)
    apparatus.prepare_for_trace(sorted_tokens)
    return run_enhanced_event_trace(apparatus, sorted_tokens, line_packets,
                                    cts_data, event_map)


# ===========================================================================
# Verification
# ===========================================================================
def main():
    t0 = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Load data for verification
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    setup_path = os.path.join(PROJECT_ROOT,
        'phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json')
    with open(setup_path) as f:
        setup = json.load(f)

    folio_params = setup['folio_configs']

    # Load corpus data (same pattern as T2)
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')) as f:
        line_packets = json.load(f)['line_packets']
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't7_closure_cts.json')) as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))
    with open(os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                           'results', 't2b_supervisory_interface_unrouted.json')) as f:
        all_tokens = json.load(f)['token_signals']
    with open(os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                           'results', 't1_event_taxonomy.json')) as f:
        event_map = json.load(f)['event_map']

    all_folios = setup['all_folios']
    folio_infra = compute_infra_scores(all_folios)

    eligible_set = set(setup['eligible_folios'])
    tokens_by_folio = {f: [] for f in eligible_set}
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio[tok['folio']].append(tok)

    # Pick one A2 folio for testing
    a2_folios = [f for f, p in folio_params.items()
                 if 'A2' in p.get('profile', '') and f in eligible_set]
    if not a2_folios:
        print("No A2 folios found")
        return

    test_folio = a2_folios[0]
    fc = folio_params[test_folio]
    profile = fc['profile']
    config_mode = folio_infra.get(test_folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
    print(f"Testing with folio={test_folio}, profile={profile}")

    tokens = tokens_by_folio.get(test_folio, [])
    if not tokens:
        print(f"No tokens for {test_folio}")
        return

    # Build f_params dict (same pattern as T2)
    fp = {
        'config_mode': config_mode,
        'f1': fc['F1'], 'f2': fc['F2'], 'f3': fc['F3'],
        'f4_raw': fc['F4_raw'], 'f5': fc['F5'],
    }

    # Load T0 ACS data
    t0_path = os.path.join(RESULTS_DIR, 't0_acs_assembly.json')
    with open(t0_path) as f:
        t0_data = json.load(f)
    acs_lookup = t0_data['per_line_acs']

    verification = {}

    # ================================================================
    # Test 1: Identity check (threshold=0 → auth_mult=1 always)
    # ================================================================
    print("\n--- Test 1: Identity check (threshold=0) ---")
    # Baseline: regular FolioSpecificApparatus
    baseline_app = FolioSpecificApparatus(
        profile=profile, config_mode=config_mode, folio=test_folio,
        f1=fp['f1'], f2=fp['f2'], f3=fp['f3'], f4_raw=fp['f4_raw'], f5=fp['f5'])

    sorted_tokens = sorted(tokens, key=sort_key)
    baseline_result = run_enhanced_event_trace(
        baseline_app, sorted_tokens, line_packets, cts_data, event_map)
    baseline_y = baseline_result['metrics']['old_y_final']

    # Authenticated with threshold=0 (auth_mult always 1.0, penalty irrelevant)
    auth_app = create_authenticated_apparatus(
        test_folio, profile, fp,
        acs_threshold=0.0,  # auth_mult = max(0, min(1, ACS/0)) = 1.0 always
        cleanliness_penalty=0.0,
        acs_lookup=acs_lookup)

    auth_result = run_authenticated_event_trace(
        auth_app, tokens, line_packets, cts_data, event_map)
    auth_y = auth_result['metrics']['old_y_final']

    y_diff = abs(auth_y - baseline_y)
    identity_pass = y_diff < 1e-6
    print(f"  Baseline Y={baseline_y:.8f}, Auth Y={auth_y:.8f}, diff={y_diff:.2e}")
    print(f"  PASS: {identity_pass}")
    verification['identity_check'] = {
        'folio': test_folio,
        'baseline_y': round(baseline_y, 8),
        'auth_y': round(auth_y, 8),
        'diff': float(f"{y_diff:.2e}"),
        'pass': identity_pass,
    }

    # ================================================================
    # Test 2: Zero-auth check (threshold=999 → auth_mult≈0)
    # ================================================================
    print("\n--- Test 2: Zero-auth check (threshold=999) ---")
    zero_app = create_authenticated_apparatus(
        test_folio, profile, fp,
        acs_threshold=999.0,
        cleanliness_penalty=10.0,
        acs_lookup=acs_lookup)

    zero_result = run_authenticated_event_trace(
        zero_app, tokens, line_packets, cts_data, event_map)
    zero_y = zero_result['metrics']['old_y_final']

    y_reduction = baseline_y - zero_y
    zero_pass = y_reduction > 0
    print(f"  Baseline Y={baseline_y:.8f}, Zero-auth Y={zero_y:.8f}, reduction={y_reduction:.6f}")
    print(f"  PASS: {zero_pass}")
    verification['zero_auth_check'] = {
        'folio': test_folio,
        'baseline_y': round(baseline_y, 8),
        'zero_auth_y': round(zero_y, 8),
        'y_reduction': round(y_reduction, 6),
        'pass': zero_pass,
    }

    # ================================================================
    # Test 3: Layer 1 isolation (penalty=0, threshold active)
    # ================================================================
    print("\n--- Test 3: Layer 1 only (penalty=0, threshold=0.35) ---")
    l1_app = create_authenticated_apparatus(
        test_folio, profile, fp,
        acs_threshold=0.35,
        cleanliness_penalty=0.0,  # Layer 2 disabled
        acs_lookup=acs_lookup)

    l1_result = run_authenticated_event_trace(
        l1_app, tokens, line_packets, cts_data, event_map)
    l1_y = l1_result['metrics']['old_y_final']
    l1_reduction = baseline_y - l1_y
    print(f"  Layer1-only Y={l1_y:.8f}, reduction={l1_reduction:.6f}")
    verification['layer1_only'] = {
        'folio': test_folio,
        'y': round(l1_y, 8),
        'reduction': round(l1_reduction, 6),
    }

    # ================================================================
    # Test 4: Layer 2 isolation (threshold=0 so auth_mult=1, but penalty active)
    # Note: when auth_mult=1, effective_gain = 10 + penalty*(1-1) = 10, so
    # Layer 2 has NO effect when auth_mult=1. This is by design.
    # To test Layer 2 in isolation, use a moderate threshold but set R4/R2
    # coefficients to show the gain change matters.
    # Actually: Layer 2 only activates when auth_mult < 1. So we use the
    # same threshold as Layer 1 but verify the combined effect exceeds Layer 1.
    # ================================================================
    print("\n--- Test 4: Both layers (threshold=0.35, penalty=10) ---")
    both_app = create_authenticated_apparatus(
        test_folio, profile, fp,
        acs_threshold=0.35,
        cleanliness_penalty=10.0,  # Both layers active
        acs_lookup=acs_lookup)

    both_result = run_authenticated_event_trace(
        both_app, tokens, line_packets, cts_data, event_map)
    both_y = both_result['metrics']['old_y_final']
    both_reduction = baseline_y - both_y
    synergy = both_reduction > l1_reduction
    print(f"  Both-layers Y={both_y:.8f}, reduction={both_reduction:.6f}")
    print(f"  Layer1 reduction={l1_reduction:.6f}, Both reduction={both_reduction:.6f}")
    print(f"  Synergy (both > layer1): {synergy}")

    verification['both_layers'] = {
        'folio': test_folio,
        'y': round(both_y, 8),
        'reduction': round(both_reduction, 6),
        'layer1_reduction': round(l1_reduction, 6),
        'synergy': synergy,
    }

    # ================================================================
    # Test 5: High-penalty check (penalty=15)
    # ================================================================
    print("\n--- Test 5: High penalty (threshold=0.35, penalty=15) ---")
    hi_app = create_authenticated_apparatus(
        test_folio, profile, fp,
        acs_threshold=0.35,
        cleanliness_penalty=15.0,
        acs_lookup=acs_lookup)

    hi_result = run_authenticated_event_trace(
        hi_app, tokens, line_packets, cts_data, event_map)
    hi_y = hi_result['metrics']['old_y_final']
    hi_reduction = baseline_y - hi_y
    monotone = hi_reduction >= both_reduction
    print(f"  High-penalty Y={hi_y:.8f}, reduction={hi_reduction:.6f}")
    print(f"  Monotone (hi >= both): {monotone}")

    verification['high_penalty'] = {
        'folio': test_folio,
        'y': round(hi_y, 8),
        'reduction': round(hi_reduction, 6),
        'monotone': monotone,
    }

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '575',
            'script': 't1_authenticated_apparatus.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t0, 2),
            'test_folio': test_folio,
            'test_profile': profile,
        },
        'verification': verification,
        'apparatus_config': {
            'acs_threshold_tested': [0.0, 999.0, 0.35, 0.35, 0.35],
            'cleanliness_penalty_tested': [0.0, 10.0, 0.0, 10.0, 15.0],
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't1_authenticated_apparatus.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == '__main__':
    main()
