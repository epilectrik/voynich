"""
T1: Controlled Excursion Executor
Phase 568 - CONTROLLED_EXCURSION_METRICS

Runs the full model (90 configurations) with 6 new controlled-excursion metrics
plus retained anchors (PCV, REF, SAHB, QGY) and legacy metrics (old_viability,
old_y_final). The plant law (CloseRecoveryApparatus from Phase 566) is
unchanged -- only the readout/scoring differs.

New metrics:
  WCU - Work Corridor Utilization (per-token zone scoring during WORK)
  SLR - Same-Line Resolution (line-scoped resolution + corridor return + work quality)
  UEB - Unresolved Excursion Burden (CLOSE-phase and line-end burden)
  CCY - Closure-Conditioned Yield (quality-gated Y with COF variants and net corridor improvement)
  WCP - Work-Closure Packet Coherence (phase-aware sub-score with presence masking)
  EWP - Edge Waste Penalty (prolonged hard_stop, unresolved warnings, edge persistence)

90 runs:
  60 primary: 20 pilot folios x 3 profiles
  30 config ablation: 10 folios x 3 config modes with A3 profile
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Import T1 close recovery apparatus from Phase 566
# ---------------------------------------------------------------------------
_phase566_scripts = str(Path(__file__).resolve().parents[1].parent
                        / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY' / 'scripts')
sys.path.insert(0, _phase566_scripts)

from t1_close_recovery_apparatus import (
    CloseRecoveryApparatus, build_close_recovery_apparatus, build_configured_apparatus,
    compute_infra_scores, compute_viability,
    STATE_VARS, SV_INDEX, N_VARS, EQUILIBRIUM, Q1, Q2_BASE, Q3_BASE,
    HAZARD_BOUNDARIES, HAZARD_DEV, PILOT_FOLIOS, PROFILES,
    assign_folio_profiles,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROFILE_NAMES = ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']

CONFIG_ABLATION_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r',
    'f40v', 'f43v', 'f34r', 'f31r', 'f39v',
]

CONFIG_MODE_NAMES = ['H0_LOW_INFRA', 'H1_MEDIUM_INFRA', 'H2_HIGH_INFRA']

# Process SVs: those with at least one hazard boundary (excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# S and Y indices
S_IDX = SV_INDEX['S']
Y_IDX = SV_INDEX['Y']

# Routing permissivity buffer (same as 566/567)
ROUTING_PERMISSIVITY = {
    'r': {'X': +0.03, 'S': -0.02, 'C': -0.02},
    'y': {'T': +0.03, 'X': -0.02},
    'h': {'TR': +0.03, 'RC': +0.02, 'X': -0.02, 'T': -0.02},
    'm': {'C': +0.03, 'T': -0.02, 'X': -0.02},
    'n': {'S': +0.02, 'X': -0.01},
    'l': {'TR': +0.02, 'S': +0.02, 'X': -0.01},
}

ROUTING_DECAY = 0.7

# Excursion tracking
MAX_CYCLE_DURATION = 50

# ---------------------------------------------------------------------------
# PCV Desirability Table (FROZEN from 567)
# ---------------------------------------------------------------------------
PCV_PROCESS = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

PCV_S = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0, 'HIGH_S': 0.9},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0, 'HIGH_S': 1.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0, 'HIGH_S': 0.9},
}

# ---------------------------------------------------------------------------
# WCU Zone Score Table (FROZEN)
# ---------------------------------------------------------------------------
WCU_SCORES = {
    'BASIN':     +0.3,
    'CORRIDOR':  +1.0,
    'WARNING':   +0.1,
    'HARD_STOP': -1.0,
    'HAZARD':    -2.0,
}

# S above EQ during WORK gets +1.0
WCU_S_HIGH_WORK = +1.0

# ---------------------------------------------------------------------------
# COF Normalization Bounds (frozen from 567 T1 / A6 section)
# Per-section P90 values from t1_closure_field_audit.json A6_cof_prototype_family
# ---------------------------------------------------------------------------
COF_SECTION_P90 = {
    'B': {
        'q4_opaque_rate': 1.0,
        'm_close_bias': 1.0,
        'close_opacity_bias': 2.25,
        'q4_shift_strength': 1.00995,
    },
    'C': {
        'q4_opaque_rate': 1.0,
        'm_close_bias': 4.1987,
        'close_opacity_bias': 2.6667,
        'q4_shift_strength': 0.99744,
    },
    'H': {
        'q4_opaque_rate': 1.0,
        'm_close_bias': 4.4516,
        'close_opacity_bias': 2.4267,
        'q4_shift_strength': 1.0,
    },
    'S': {
        'q4_opaque_rate': 0.66667,
        'm_close_bias': 6.9431,
        'close_opacity_bias': 2.5,
        'q4_shift_strength': 1.0,
    },
    'T': {
        'q4_opaque_rate': 0.66667,
        'm_close_bias': 6.7368,
        'close_opacity_bias': 3.31669,
        'q4_shift_strength': 0.84711,
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_zone(sv, abs_dev):
    """Classify a state variable's deviation into a 5-zone system."""
    q2 = Q2_BASE[sv]
    q3 = q2 + 0.05
    q3 = min(q3, HAZARD_DEV[sv] - 0.01)

    if abs_dev < Q1:
        return 'BASIN'
    elif abs_dev < q2:
        return 'CORRIDOR'
    elif abs_dev < q3:
        return 'WARNING'
    elif abs_dev < HAZARD_DEV[sv]:
        return 'HARD_STOP'
    else:
        return 'HAZARD'


def _is_quiet(state):
    """All process SVs have |dev| < Q1."""
    return all(abs(state[i] - EQUILIBRIUM) < Q1 for i in PROCESS_IDX)


def _pcv_score_for_token(state, packet_phase):
    """Compute PCV score contribution for one token across process SVs (excl Y)."""
    score = 0.0
    count = 0

    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = state[i] - EQUILIBRIUM
        abs_dev = abs(dev)
        zone = _classify_zone(sv, abs_dev)

        if sv == 'S' and state[i] > EQUILIBRIUM:
            score += PCV_S[packet_phase]['HIGH_S']
        else:
            if sv == 'S':
                score += PCV_S[packet_phase].get(zone, 0.0)
            else:
                score += PCV_PROCESS[packet_phase].get(zone, 0.0)
        count += 1

    return score, count


def _cof_norm(val, comp_name, section):
    """Normalize a component value using frozen per-section P90 bounds."""
    p90_dict = COF_SECTION_P90.get(section, COF_SECTION_P90.get('B', {}))
    p90 = p90_dict.get(comp_name, 1.0)
    return min(val / p90, 1.0) if p90 > 0 else 0.0


def _compute_cof_variants(cts, lp, section):
    """Compute COF1, COF2, COF3 for a line from its line packet."""
    ps = lp.get('packet_state', {})
    q4_opaque_rate = lp.get('profile', [0]*15)[14] if len(lp.get('profile', [])) > 14 else 0.0
    m_close_bias = ps.get('m_close_bias', 0.0)
    close_opacity_bias = ps.get('close_opacity_bias', 0.0)
    q4_shift_strength = ps.get('q4_shift_strength', 0.0)

    nq4 = _cof_norm(q4_opaque_rate, 'q4_opaque_rate', section)
    nmcb = _cof_norm(m_close_bias, 'm_close_bias', section)
    ncob = _cof_norm(close_opacity_bias, 'close_opacity_bias', section)
    nq4s = _cof_norm(q4_shift_strength, 'q4_shift_strength', section)

    cof1 = 0.6 * cts + 0.4 * nq4
    cof2 = 0.5 * cts + 0.25 * nq4 + 0.25 * nmcb
    cof3 = 0.3 * cts + 0.2 * nq4s + 0.2 * ncob + 0.3 * nmcb

    return cof1, cof2, cof3


def _compute_ref(ref_pairs):
    """
    Compute REF from (work_end_dev, close_end_dev) pairs.
    Eligibility: work_end_dev > Q1 (0.08).
    REF per eligible pair = 1 - (close_end_dev / work_end_dev).
    """
    if not ref_pairs:
        return 0.0, 0.0

    total_pairs = len(ref_pairs)
    eligible_count = 0
    ref_values = []

    for work_dev, close_dev in ref_pairs:
        if work_dev <= Q1:
            continue
        eligible_count += 1
        ref_val = 1.0 - (close_dev / work_dev)
        ref_values.append(ref_val)

    if eligible_count == 0:
        return 0.0, 0.0

    ref_mean = sum(ref_values) / len(ref_values)
    ref_eligible_frac = eligible_count / total_pairs

    return ref_mean, ref_eligible_frac


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------

def run_excursion_trace(apparatus, tokens, line_packets, cts_data):
    """
    Run one folio through the CloseRecoveryApparatus with controlled-excursion metrics.

    apparatus:     CloseRecoveryApparatus instance
    tokens:        list of token dicts, pre-sorted by (line, position)
    line_packets:  dict mapping "folio|line" -> packet info
    cts_data:      dict mapping "folio|line" -> CTS value

    Returns dict with old metrics + retained anchors + 6 new metrics.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return _empty_result()

    state = [EQUILIBRIUM] * N_VARS
    permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
    prev_line = None

    # ---- Old metric accumulators ----
    viable_count = 0
    hazard_count = 0
    in_excursion = False
    excursion_start = None
    excursion_count = 0
    bounded_excursion_count = 0

    # ---- PCV accumulators (retained anchor) ----
    pcv_score_sum = 0.0
    pcv_pair_count = 0

    # ---- SAHB accumulators (retained anchor) ----
    sahb_warning = 0
    sahb_hardstop = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # ---- REF: per-line tracking (retained anchor) ----
    last_work_end_dev_per_folio = {}
    ref_pairs = []

    # ---- QGY accumulators (retained anchor) ----
    quality_y = 0.0
    prev_aggregate_dev = None

    # ---- M1: WCU accumulators ----
    wcu_score_sum = 0.0
    wcu_pair_count = 0

    # ---- M2: SLR per-line tracking ----
    # We collect per-line data and compute SLR at the end
    line_data = []  # list of per-line dicts, finalized on line transitions

    # ---- M3: UEB accumulators ----
    ueb_close_warnings = 0
    ueb_close_hardstops = 0
    ueb_unresolved_fractions = []  # per eligible line
    ueb_line_final_hardstop_count = 0
    ueb_post_line_residual_above_q2 = 0

    # ---- M4: CCY accumulators ----
    ccy_total = 0.0
    ccy_cof1_total = 0.0
    ccy_cof2_total = 0.0
    ccy_cof3_total = 0.0
    ccy_n_svs_below_q2_events = []
    # Cross-line WORK peak tracking (packet_phase is line-level, so CLOSE lines
    # need the WORK peak from the preceding WORK line, like REF does with work_end_dev)
    last_work_peak_dev_per_folio = {}
    last_work_peak_svs_above_q2_per_folio = {}

    # ---- M5: WCP per-line tracking ----
    # Tracked per-line and aggregated at the end

    # ---- M6: EWP accumulators ----
    ewp_prolonged_hardstop = 0
    ewp_unresolved_warning_count = 0
    ewp_post_close_residuals = []  # per CLOSE line
    ewp_edge_persistence_numer = 0
    ewp_edge_persistence_denom = 0

    # ---- Per-line state tracking ----
    current_line_key = None
    current_line_phase = None
    lp_mismatches = 0

    # Per-line accumulators (reset on line boundary)
    line_work_tokens = 0
    line_close_tokens = 0
    line_spec_tokens = 0
    line_work_peak_dev = 0.0  # max mean |dev| across process SVs during WORK
    line_work_end_dev = 0.0
    line_close_end_dev = 0.0
    line_work_peak_svs_above_q2 = 0  # count at the WORK peak moment
    line_work_corridor_count = 0  # WORK tokens where >= 1 process SV in CORRIDOR
    line_close_dev_decreasing_count = 0  # CLOSE tokens where mean |dev| decreased
    line_spec_all_basin_count = 0  # SPEC tokens where ALL process SVs in BASIN
    line_work_any_corridor_or_warning_count = 0  # WORK tokens where >= 1 in CORRIDOR/WARNING
    line_prev_close_mean_dev = None  # for WCP close_score tracking

    # EWP per-line
    line_consecutive_hardstop_during_work = 0  # consecutive tokens in hard_stop during WORK
    line_warning_svs_during_close = set()  # SVs that had warning during CLOSE
    line_close_end_sv_devs = {}  # {sv: abs_dev} at line end for CLOSE lines

    # Per-line: track per-phase zone occupancy for process SVs
    # Used for multiple metrics

    # COF data for current line
    line_cts = 0.0
    line_cof1 = 0.0
    line_cof2 = 0.0
    line_cof3 = 0.0
    line_section = 'B'

    def _finalize_line():
        """Finalize metrics for the departing line. Called on line transitions."""
        nonlocal ueb_line_final_hardstop_count, ueb_post_line_residual_above_q2
        nonlocal ewp_unresolved_warning_count

        if current_line_key is None:
            return

        # Compute end-of-line deviations
        end_dev_per_sv = {}
        any_hardstop_or_hazard = False
        mean_q2_at_end = 0.0
        n_above_q2_at_end = 0
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            end_dev_per_sv[sv] = dev
            zone = _classify_zone(sv, dev)
            # S above EQ exclusion for UEB/EWP
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            if zone in ('HARD_STOP', 'HAZARD'):
                any_hardstop_or_hazard = True
            if dev > Q2_BASE[sv]:
                n_above_q2_at_end += 1
            mean_q2_at_end += Q2_BASE[sv]

        n_process = len([sv for sv in PROCESS_SVS if not (sv == 'S' and state[S_IDX] > EQUILIBRIUM)])
        mean_end_dev = sum(
            end_dev_per_sv[sv] for sv in PROCESS_SVS
            if not (sv == 'S' and state[S_IDX] > EQUILIBRIUM)
        ) / max(n_process, 1)
        mean_q2 = mean_q2_at_end / len(PROCESS_SVS)

        # UEB: line_final_hardstop
        if any_hardstop_or_hazard:
            ueb_line_final_hardstop_count += 1

        # UEB: post_line_residual_above_Q2
        if mean_end_dev > mean_q2:
            ueb_post_line_residual_above_q2 += 1

        # UEB: unresolved_fraction (eligible lines: work_end_dev > Q1)
        if line_work_end_dev > Q1:
            if line_close_tokens > 0:
                uf = line_close_end_dev / line_work_end_dev if line_work_end_dev > 0 else 1.0
            else:
                uf = 1.0  # no CLOSE phase means nothing resolved
            ueb_unresolved_fractions.append(uf)

        # EWP: unresolved_warning -- warnings during CLOSE that don't resolve below Q2 by line end
        if line_close_tokens > 0:
            for sv in line_warning_svs_during_close:
                if sv == 'S' and state[S_IDX] > EQUILIBRIUM:
                    continue
                dev_at_end = end_dev_per_sv.get(sv, 0.0)
                if dev_at_end >= Q2_BASE[sv]:
                    ewp_unresolved_warning_count += 1

        # EWP: post_close_residual
        if line_close_tokens > 0:
            residuals = []
            for sv in PROCESS_SVS:
                if sv == 'S' and state[S_IDX] > EQUILIBRIUM:
                    continue
                dev_at_end = end_dev_per_sv.get(sv, 0.0)
                residuals.append(max(dev_at_end - Q1, 0.0))
            if residuals:
                ewp_post_close_residuals.append(sum(residuals) / len(residuals))

        # Compute work_end_dev and close_end_dev for SLR/REF
        departing_folio = current_line_key.split('|')[0]

        if current_line_phase == 'WORK':
            last_work_end_dev_per_folio[departing_folio] = line_work_end_dev
            # Cross-line WORK peak tracking for CCY (CLOSE lines need preceding WORK peak)
            last_work_peak_dev_per_folio[departing_folio] = line_work_peak_dev
            last_work_peak_svs_above_q2_per_folio[departing_folio] = line_work_peak_svs_above_q2
        elif current_line_phase == 'CLOSE':
            if departing_folio in last_work_end_dev_per_folio:
                ref_pairs.append((
                    last_work_end_dev_per_folio[departing_folio],
                    line_close_end_dev
                ))

        # SLR: build per-line record
        slr_record = {
            'work_end_dev': line_work_end_dev,
            'close_end_dev': line_close_end_dev,
            'work_peak_dev': line_work_peak_dev,
            'work_peak_svs_above_q2': line_work_peak_svs_above_q2,
            'work_tokens': line_work_tokens,
            'close_tokens': line_close_tokens,
            'spec_tokens': line_spec_tokens,
            'work_corridor_count': line_work_corridor_count,
            'all_below_q2_at_end': n_above_q2_at_end == 0,
            'close_dev_decreasing_count': line_close_dev_decreasing_count,
            'spec_all_basin_count': line_spec_all_basin_count,
            'work_any_corridor_or_warning_count': line_work_any_corridor_or_warning_count,
        }
        line_data.append(slr_record)

    # ================================================================
    # Main token loop
    # ================================================================
    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']
        line_key = f"{folio}|{current_line}"

        # ---- Line boundary handling ----
        if current_line != prev_line:
            # Finalize departing line
            if prev_line is not None:
                _finalize_line()

            # Reset line-level tracking
            permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
            prev_line = current_line
            current_line_key = line_key

            line_work_tokens = 0
            line_close_tokens = 0
            line_spec_tokens = 0
            line_work_peak_dev = 0.0
            line_work_end_dev = 0.0
            line_close_end_dev = 0.0
            line_work_peak_svs_above_q2 = 0
            line_work_corridor_count = 0
            line_close_dev_decreasing_count = 0
            line_spec_all_basin_count = 0
            line_work_any_corridor_or_warning_count = 0
            line_prev_close_mean_dev = None
            line_consecutive_hardstop_during_work = 0
            line_warning_svs_during_close = set()
            line_close_end_sv_devs = {}

            # Determine phase for this line
            lp_key = line_key
            if lp_key in line_packets:
                lp = line_packets[lp_key]
                current_line_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
                line_section = lp.get('section', 'B')
            else:
                current_line_phase = 'WORK'
                line_section = 'B'

            # Get CTS for this line
            if line_key in cts_data:
                line_cts = cts_data[line_key]
            elif line_key in line_packets:
                # Fallback: use token-level cts if available
                line_cts = 0.0
            else:
                line_cts = 0.0

            # Compute COF variants for this line
            if line_key in line_packets:
                line_cof1, line_cof2, line_cof3 = _compute_cof_variants(
                    line_cts, line_packets[line_key], line_section)
            else:
                line_cof1, line_cof2, line_cof3 = 0.0, 0.0, 0.0

        # ---- Routing ----
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_PERMISSIVITY:
                for sv, shift in ROUTING_PERMISSIVITY[rt].items():
                    permissivity_buffer[sv] += shift

        # ---- Packet phase and CTS ----
        packet_phase = tok.get('packet_phase', None)
        cts = tok.get('cts', 0.0)

        if packet_phase is None:
            if line_key in line_packets:
                lp = line_packets[line_key]
                packet_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
            else:
                packet_phase = 'WORK'
                lp_mismatches += 1

        # Use line-level CTS if token doesn't have it
        if cts == 0.0 and line_cts > 0.0:
            cts = line_cts

        # ---- Pre-step aggregate deviation (for QGY/CCY) ----
        pre_agg_dev = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # ---- Compute dV ----
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            dV[i] = contributions[i] * apparatus.sensitivity[sv]

        # ---- Pre-step Y (for delta) ----
        pre_y = state[Y_IDX]

        # ---- Apparatus update ----
        perm_dict = {sv: v for sv, v in permissivity_buffer.items() if abs(v) > 1e-8}
        state, diagnostics = apparatus.update(
            state, dV, packet_phase, cts,
            permissivity=perm_dict if perm_dict else None
        )

        # ---- Decay permissivity buffer ----
        for sv in STATE_VARS:
            permissivity_buffer[sv] *= ROUTING_DECAY

        # ---- Post-step aggregate deviation ----
        post_agg_dev = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # ---- Y delta this step ----
        y_delta = state[Y_IDX] - pre_y

        # ---- Zone classification per SV ----
        per_sv_zones = {}
        per_sv_abs_dev = {}
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            per_sv_abs_dev[sv] = dev
            per_sv_zones[sv] = _classify_zone(sv, dev)

        # Mean |dev| across process SVs (for line tracking)
        current_mean_dev = sum(per_sv_abs_dev[sv] for sv in PROCESS_SVS) / len(PROCESS_SVS)

        # S above EQ flag
        s_above_eq = state[S_IDX] > EQUILIBRIUM

        # ================================================================
        # OLD METRICS
        # ================================================================

        # Viability check (binary: not in hazard)
        is_viable = True
        for i, sv in enumerate(STATE_VARS):
            lo, hi = HAZARD_BOUNDARIES[sv]
            if lo is not None and state[i] < lo:
                is_viable = False
            if hi is not None and state[i] > hi:
                is_viable = False
        if is_viable:
            viable_count += 1
        else:
            hazard_count += 1

        # Excursion tracking
        quiet_now = _is_quiet(state)
        if not in_excursion:
            if not quiet_now:
                in_excursion = True
                excursion_start = tok_idx
                excursion_count += 1
        else:
            if quiet_now:
                duration = tok_idx - excursion_start
                if duration <= MAX_CYCLE_DURATION:
                    bounded_excursion_count += 1
                in_excursion = False
                excursion_start = None

        # ================================================================
        # RETAINED ANCHOR: PCV
        # ================================================================
        pcv_s, pcv_c = _pcv_score_for_token(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_pair_count += pcv_c

        # ================================================================
        # RETAINED ANCHOR: SAHB
        # ================================================================
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue

            sahb_max_excursion = max(sahb_max_excursion, dev)

            if dev >= q3:
                sahb_hardstop += 1
            elif dev >= q2:
                sahb_warning += 1

            if dev >= q2:
                sahb_outside_corridor += 1

        # ================================================================
        # RETAINED ANCHOR: QGY
        # ================================================================
        if prev_aggregate_dev is not None:
            dev_decreased = (post_agg_dev < prev_aggregate_dev)
        else:
            dev_decreased = False

        if packet_phase == 'CLOSE' and cts > 0.3 and dev_decreased and y_delta > 0:
            quality_y += y_delta

        prev_aggregate_dev = post_agg_dev

        # ================================================================
        # M1: WCU (Work Corridor Utilization)
        # ================================================================
        if packet_phase == 'WORK':
            for sv in PROCESS_SVS:
                if sv == 'S' and s_above_eq:
                    wcu_score_sum += WCU_S_HIGH_WORK
                    wcu_pair_count += 1
                elif sv == 'Y':
                    continue  # Y excluded
                else:
                    zone = per_sv_zones[sv]
                    wcu_score_sum += WCU_SCORES.get(zone, 0.0)
                    wcu_pair_count += 1

        # ================================================================
        # M3: UEB (Unresolved Excursion Burden) -- CLOSE-phase tallies
        # ================================================================
        if packet_phase == 'CLOSE':
            for sv in PROCESS_SVS:
                if sv == 'S' and s_above_eq:
                    continue  # S above EQ excluded
                zone = per_sv_zones[sv]
                if zone == 'WARNING':
                    ueb_close_warnings += 1
                elif zone in ('HARD_STOP', 'HAZARD'):
                    ueb_close_hardstops += 1

        # ================================================================
        # M4: CCY (Closure-Conditioned Yield)
        # ================================================================
        if packet_phase == 'CLOSE' and y_delta > 0:
            # Condition 2: cts > 0.3 (primary)
            # Condition 3: aggregate deviation decreased from WORK-phase peak
            # NOTE: packet_phase is line-level, so CLOSE lines have no WORK tokens.
            # Use cross-line tracking: the WORK peak from the preceding WORK line.
            ref_work_peak_dev = last_work_peak_dev_per_folio.get(folio, 0.0)
            ref_work_peak_svs_above_q2 = last_work_peak_svs_above_q2_per_folio.get(folio, 0)
            agg_dev_decreased_from_work_peak = (current_mean_dev < ref_work_peak_dev) if ref_work_peak_dev > 0 else False

            # Condition 4: NET CORRIDOR IMPROVEMENT
            # mean |dev| < WORK peak mean |dev|
            # AND count of SVs with |dev| > Q2 decreased from WORK peak
            # Note: if work_peak_svs_above_q2 == 0, the second part is vacuously
            # true (no excursions above Q2 to resolve), so only mean dev decrease needed.
            current_svs_above_q2 = sum(
                1 for sv in PROCESS_SVS
                if not (sv == 'S' and s_above_eq)
                and per_sv_abs_dev[sv] > Q2_BASE[sv]
            )
            if ref_work_peak_svs_above_q2 == 0:
                # No SVs exceeded Q2 during WORK — vacuously satisfied
                net_corridor_improvement = current_mean_dev < ref_work_peak_dev if ref_work_peak_dev > 0 else False
            else:
                net_corridor_improvement = (
                    current_mean_dev < ref_work_peak_dev
                    and current_svs_above_q2 < ref_work_peak_svs_above_q2
                )

            if agg_dev_decreased_from_work_peak and net_corridor_improvement:
                # Count SVs below Q2 for logging
                n_below_q2 = sum(
                    1 for sv in PROCESS_SVS
                    if not (sv == 'S' and s_above_eq)
                    and per_sv_abs_dev[sv] < Q2_BASE[sv]
                )

                # Primary: cts > 0.3
                if cts > 0.3:
                    ccy_total += y_delta
                    ccy_n_svs_below_q2_events.append(n_below_q2)

                # COF variants
                if line_cof1 > 0.3:
                    ccy_cof1_total += y_delta
                if line_cof2 > 0.3:
                    ccy_cof2_total += y_delta
                if line_cof3 > 0.3:
                    ccy_cof3_total += y_delta

        # ================================================================
        # M6: EWP -- per-token tracking
        # ================================================================
        if packet_phase == 'WORK':
            # Check for prolonged hard_stop (> 2 consecutive tokens)
            any_hardstop_this_token = False
            for sv in PROCESS_SVS:
                if sv == 'S' and s_above_eq:
                    continue
                if per_sv_zones[sv] in ('HARD_STOP', 'HAZARD'):
                    any_hardstop_this_token = True
                    break

            if any_hardstop_this_token:
                line_consecutive_hardstop_during_work += 1
                if line_consecutive_hardstop_during_work > 2:
                    ewp_prolonged_hardstop += 1
            else:
                line_consecutive_hardstop_during_work = 0

        if packet_phase == 'CLOSE':
            # Track warning SVs during CLOSE (for unresolved_warning)
            for sv in PROCESS_SVS:
                if sv == 'S' and s_above_eq:
                    continue
                if per_sv_zones[sv] == 'WARNING':
                    line_warning_svs_during_close.add(sv)

            # Edge persistence: CLOSE tokens where any process SV in hard_stop/hazard
            any_edge = False
            for sv in PROCESS_SVS:
                if sv == 'S' and s_above_eq:
                    continue
                if per_sv_zones[sv] in ('HARD_STOP', 'HAZARD'):
                    any_edge = True
                    break
            ewp_edge_persistence_denom += 1
            if any_edge:
                ewp_edge_persistence_numer += 1

        # ================================================================
        # Per-line phase tracking
        # ================================================================
        if packet_phase == 'WORK':
            line_work_tokens += 1
            # Track work peak dev
            if current_mean_dev > line_work_peak_dev:
                line_work_peak_dev = current_mean_dev
                # Count SVs above Q2 at this peak moment
                line_work_peak_svs_above_q2 = sum(
                    1 for sv in PROCESS_SVS
                    if not (sv == 'S' and s_above_eq)
                    and per_sv_abs_dev[sv] > Q2_BASE[sv]
                )
            line_work_end_dev = current_mean_dev

            # WCP: work_score -- >= 1 process SV in CORRIDOR or WARNING
            any_corridor_or_warning = any(
                per_sv_zones[sv] in ('CORRIDOR', 'WARNING')
                for sv in PROCESS_SVS
            )
            if any_corridor_or_warning:
                line_work_any_corridor_or_warning_count += 1

            # SLR: work_quality -- >= 1 process SV in CORRIDOR
            any_corridor = any(
                per_sv_zones[sv] == 'CORRIDOR'
                for sv in PROCESS_SVS
            )
            if any_corridor:
                line_work_corridor_count += 1

        elif packet_phase == 'CLOSE':
            line_close_tokens += 1
            line_close_end_dev = current_mean_dev

            # WCP: close_score -- mean |dev| decreased from previous token
            if line_prev_close_mean_dev is not None:
                if current_mean_dev < line_prev_close_mean_dev:
                    line_close_dev_decreasing_count += 1
            line_prev_close_mean_dev = current_mean_dev

        elif packet_phase == 'SPEC':
            line_spec_tokens += 1

            # WCP: spec_score -- ALL process SVs in BASIN
            all_basin = all(
                per_sv_zones[sv] == 'BASIN'
                for sv in PROCESS_SVS
            )
            if all_basin:
                line_spec_all_basin_count += 1

    # ---- Finalize last line ----
    if current_line_key is not None:
        _finalize_line()

    # ================================================================
    # Compute final metric values
    # ================================================================

    # Old viability
    old_viability = viable_count / n_tokens if n_tokens > 0 else 0.0
    old_y_final = state[Y_IDX]

    # PCV
    pcv = pcv_score_sum / pcv_pair_count if pcv_pair_count > 0 else 0.0

    # SAHB
    sahb = (1.0 * sahb_warning + 3.0 * sahb_hardstop
            + 0.5 * sahb_outside_corridor + 2.0 * sahb_max_excursion)

    # REF
    ref_mean, ref_eligible_frac = _compute_ref(ref_pairs)

    # QGY
    qgy_ratio = quality_y / old_y_final if old_y_final > 0 else 0.0

    # ---- M1: WCU ----
    wcu = wcu_score_sum / wcu_pair_count if wcu_pair_count > 0 else 0.0

    # ---- M2: SLR ----
    slr_values = []
    slr_eligible_count = 0
    work_peak_devs = []

    for ld in line_data:
        wed = ld['work_end_dev']
        work_peak_devs.append(ld['work_peak_dev'])

        if wed <= Q1:
            continue  # Not eligible

        slr_eligible_count += 1
        ced = ld['close_end_dev']

        # resolution_score = 1.0 - (close_end_dev / work_end_dev) [= REF]
        resolution_score = 1.0 - (ced / wed) if wed > 0 else 0.0

        # corridor_return: 1.0 if all process SVs below Q2 at line end
        corridor_return = 1.0 if ld['all_below_q2_at_end'] else 0.0

        # work_quality: fraction of WORK-phase tokens where >= 1 process SV in CORRIDOR
        if ld['work_tokens'] > 0:
            work_quality = ld['work_corridor_count'] / ld['work_tokens']
        else:
            work_quality = 0.0

        slr = 0.5 * resolution_score + 0.3 * corridor_return + 0.2 * work_quality
        slr = max(-1.0, min(1.0, slr))
        slr_values.append(slr)

    slr_mean = sum(slr_values) / len(slr_values) if slr_values else 0.0
    slr_eligible_fraction = slr_eligible_count / len(line_data) if line_data else 0.0
    mean_work_peak_dev = sum(work_peak_devs) / len(work_peak_devs) if work_peak_devs else 0.0

    # ---- M3: UEB ----
    mean_unresolved = (sum(ueb_unresolved_fractions) / len(ueb_unresolved_fractions)
                       if ueb_unresolved_fractions else 0.0)
    ueb = (1.0 * ueb_close_warnings
           + 3.0 * ueb_close_hardstops
           + 2.0 * mean_unresolved
           + 5.0 * ueb_line_final_hardstop_count
           + 1.5 * ueb_post_line_residual_above_q2)

    # ---- M4: CCY ----
    ccy_ratio = ccy_total / old_y_final if old_y_final > 0 else 0.0

    # ---- M5: WCP ----
    wcp_all_lines = []
    wcp_full_packet_lines = []

    for ld in line_data:
        has_spec = ld['spec_tokens'] > 0
        has_work = ld['work_tokens'] > 0
        has_close = ld['close_tokens'] > 0

        # Compute sub-scores
        spec_score = None
        work_score = None
        close_score = None

        if has_spec:
            spec_score = ld['spec_all_basin_count'] / ld['spec_tokens']

        if has_work:
            work_score = ld['work_any_corridor_or_warning_count'] / ld['work_tokens']

        if has_close:
            # fraction where mean |dev| decreased from previous token
            # First CLOSE token has no previous, so denominator is close_tokens - 1 or close_tokens
            if ld['close_tokens'] > 1:
                close_score = ld['close_dev_decreasing_count'] / (ld['close_tokens'] - 1)
            elif ld['close_tokens'] == 1:
                close_score = 0.0  # single token, no comparison possible

        # Phase-presence masking
        present = []
        weights = {}
        if spec_score is not None:
            present.append(('spec', spec_score))
        if work_score is not None:
            present.append(('work', work_score))
        if close_score is not None:
            present.append(('close', close_score))

        if len(present) == 0:
            continue

        # Determine weights based on which phases are present
        if len(present) == 3:
            # All three: 0.2*spec + 0.4*work + 0.4*close
            wcp_val = 0.2 * spec_score + 0.4 * work_score + 0.4 * close_score
            wcp_full_packet_lines.append(wcp_val)
        elif len(present) == 2:
            phase_names = {p[0] for p in present}
            if phase_names == {'work', 'close'}:
                wcp_val = 0.5 * work_score + 0.5 * close_score
            elif phase_names == {'spec', 'work'}:
                wcp_val = 0.33 * spec_score + 0.67 * work_score
            elif phase_names == {'spec', 'close'}:
                wcp_val = 0.33 * spec_score + 0.67 * close_score
            else:
                wcp_val = sum(s for _, s in present) / len(present)
        else:
            # Single phase
            wcp_val = present[0][1]

        wcp_all_lines.append(wcp_val)

    wcp_mean = sum(wcp_all_lines) / len(wcp_all_lines) if wcp_all_lines else 0.0
    wcp_full_packet_mean = (sum(wcp_full_packet_lines) / len(wcp_full_packet_lines)
                            if wcp_full_packet_lines else 0.0)

    # ---- M6: EWP ----
    edge_persistence = (ewp_edge_persistence_numer / ewp_edge_persistence_denom
                        if ewp_edge_persistence_denom > 0 else 0.0)
    mean_post_close_residual = (sum(ewp_post_close_residuals) / len(ewp_post_close_residuals)
                                if ewp_post_close_residuals else 0.0)

    ewp = (1.0 * ewp_prolonged_hardstop
           + 2.0 * ewp_unresolved_warning_count
           + 3.0 * mean_post_close_residual
           + 5.0 * edge_persistence)

    # ================================================================
    # Build result
    # ================================================================
    result = {
        # New metrics (M1-M6)
        'WCU': round(wcu, 5),
        'SLR_mean': round(slr_mean, 5),
        'SLR_eligible_fraction': round(slr_eligible_fraction, 5),
        'SLR_eligible_count': slr_eligible_count,
        'mean_work_peak_dev': round(mean_work_peak_dev, 5),
        'UEB': round(ueb, 5),
        'UEB_components': {
            'close_warnings': ueb_close_warnings,
            'close_hardstops': ueb_close_hardstops,
            'mean_unresolved_fraction': round(mean_unresolved, 5),
            'line_final_hardstop_count': ueb_line_final_hardstop_count,
            'post_line_residual_above_q2': ueb_post_line_residual_above_q2,
        },
        'CCY': round(ccy_total, 5),
        'CCY_ratio': round(ccy_ratio, 5),
        'CCY_cof1': round(ccy_cof1_total, 5),
        'CCY_cof2': round(ccy_cof2_total, 5),
        'CCY_cof3': round(ccy_cof3_total, 5),
        'WCP_mean': round(wcp_mean, 5),
        'WCP_full_packet_mean': round(wcp_full_packet_mean, 5),
        'EWP': round(ewp, 5),
        'EWP_components': {
            'prolonged_hardstop': ewp_prolonged_hardstop,
            'unresolved_warning': ewp_unresolved_warning_count,
            'post_close_residual': round(mean_post_close_residual, 5),
            'edge_persistence': round(edge_persistence, 5),
        },
        # Retained anchors
        'PCV': round(pcv, 5),
        'REF_mean': round(ref_mean, 5),
        'REF_eligible_fraction': round(ref_eligible_frac, 5),
        'SAHB': round(sahb, 5),
        'QGY': round(quality_y, 5),
        'qgy_ratio': round(qgy_ratio, 5),
        # Legacy metrics
        'old_viability': round(old_viability, 5),
        'old_y_final': round(old_y_final, 5),
        'n_tokens': n_tokens,
        'n_hazard_events': hazard_count,
    }

    if lp_mismatches > 0:
        result['lp_mismatches'] = lp_mismatches

    return result


def _empty_result():
    """Return empty result dict for folios with no tokens."""
    return {
        'WCU': 0.0,
        'SLR_mean': 0.0,
        'SLR_eligible_fraction': 0.0,
        'SLR_eligible_count': 0,
        'mean_work_peak_dev': 0.0,
        'UEB': 0.0,
        'UEB_components': {
            'close_warnings': 0,
            'close_hardstops': 0,
            'mean_unresolved_fraction': 0.0,
            'line_final_hardstop_count': 0,
            'post_line_residual_above_q2': 0,
        },
        'CCY': 0.0,
        'CCY_ratio': 0.0,
        'CCY_cof1': 0.0,
        'CCY_cof2': 0.0,
        'CCY_cof3': 0.0,
        'WCP_mean': 0.0,
        'WCP_full_packet_mean': 0.0,
        'EWP': 0.0,
        'EWP_components': {
            'prolonged_hardstop': 0,
            'unresolved_warning': 0,
            'post_close_residual': 0.0,
            'edge_persistence': 0.0,
        },
        'PCV': 0.0,
        'REF_mean': 0.0,
        'REF_eligible_fraction': 0.0,
        'SAHB': 0.0,
        'QGY': 0.0,
        'qgy_ratio': 0.0,
        'old_viability': 0.0,
        'old_y_final': 0.5,
        'n_tokens': 0,
        'n_hazard_events': 0,
        'structurally_ineligible': True,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()

    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    project_root = phase_dir.parent.parent

    output_path = phase_dir / 'results' / 't1_controlled_excursion_runs.json'

    # --- Data source paths ---
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    t1_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY'
               / 'results' / 't1_close_recovery_apparatus.json')
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')
    cts_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                / 'results' / 't7_closure_cts.json')
    budget_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                   / 'results' / 't2_folio_budgets.json')

    print("=" * 70)
    print("T1: Controlled Excursion Executor")
    print("Phase 568 - CONTROLLED_EXCURSION_METRICS")
    print("=" * 70)

    # --- Load data sources ---
    print("\n--- Loading data sources ---")

    print(f"  Loading T2b supervisory tokens: {t2b_path}")
    with open(t2b_path, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"    Total tokens: {len(all_tokens)}")

    print(f"  Loading T1 apparatus config: {t1_path}")
    with open(t1_path, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    folio_infra_scores = t1_data['folio_infra_scores']
    print(f"    Folio infra scores: {len(folio_infra_scores)} folios")

    print(f"  Loading line packets: {lp_path}")
    with open(lp_path, 'r', encoding='utf-8') as f:
        lp_data = json.load(f)
    line_packets = lp_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    print(f"  Loading CTS data: {cts_path}")
    with open(cts_path, 'r', encoding='utf-8') as f:
        cts_raw = json.load(f)
    # Build CTS lookup: "folio|line" -> cts value
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            if isinstance(val, dict):
                cts_data[key] = val.get('cts', 0.0)
            else:
                cts_data[key] = float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            if isinstance(val, dict):
                cts_data[key] = val.get('cts', val.get('score', 0.0))
            else:
                cts_data[key] = float(val)
    print(f"    CTS entries: {len(cts_data)}")

    # --- Determine preferred profiles for pilot folios ---
    print("\n--- Assigning folio profiles ---")
    regime_path = project_root / 'data' / 'regime_folio_mapping.json'

    folio_assignments = assign_folio_profiles(regime_path, budget_path)

    preferred_profile_map = {}
    for folio in PILOT_FOLIOS:
        fa = folio_assignments.get(folio, {})
        preferred_profile_map[folio] = fa.get('preferred_profile', 'A1_BATH_REFLUX')

    print(f"    Preferred profiles assigned for {len(preferred_profile_map)} pilot folios")

    # --- Extract tokens per pilot folio ---
    print("\n--- Extracting pilot folio tokens ---")
    pilot_folio_set = set(PILOT_FOLIOS)
    tokens_by_folio = {f: [] for f in pilot_folio_set}
    for tok in all_tokens:
        if tok['folio'] in pilot_folio_set:
            tokens_by_folio[tok['folio']].append(tok)

    def sort_key(tok):
        line = tok.get('line', '0')
        try:
            line_num = int(line)
        except (ValueError, TypeError):
            line_num = 99999
        return (line_num, tok.get('line_pos', 0.0))

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    for folio in PILOT_FOLIOS:
        n = len(tokens_by_folio[folio])
        cfg = folio_infra_scores.get(folio, {}).get('config_mode', '?')
        pref = preferred_profile_map.get(folio, '?')
        print(f"  {folio}: {n} tokens, config={cfg}, preferred={pref}")

    # --- Primary runs (60): 20 folios x 3 profiles ---
    print("\n--- Primary Runs (60) ---")
    primary_results = {}
    run_count = 0

    for folio in PILOT_FOLIOS:
        toks = tokens_by_folio[folio]
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        infra = folio_infra_scores.get(folio, {})
        config_mode = infra.get('config_mode', 'H1_MEDIUM_INFRA')
        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')

        if folio not in primary_results:
            primary_results[folio] = {}

        for profile_name in PROFILE_NAMES:
            apparatus = build_configured_apparatus(profile_name, config_mode)
            result = run_excursion_trace(apparatus, toks, line_packets, cts_data)
            primary_results[folio][profile_name] = result
            run_count += 1

            is_pref = (profile_name == preferred_profile)
            pref_tag = " *PREFERRED*" if is_pref else ""
            short_profile = profile_name.split('_')[0]
            print(f"  [{run_count:2d}/60] {folio} + {short_profile} [{config_mode}]: "
                  f"WCU={result['WCU']:.4f}, SLR={result['SLR_mean']:.4f}, "
                  f"UEB={result['UEB']:.1f}, CCY={result['CCY']:.4f}, "
                  f"WCP={result['WCP_mean']:.4f}, EWP={result['EWP']:.1f}, "
                  f"PCV={result['PCV']:.4f}, viab={result['old_viability']:.4f}"
                  f"{pref_tag}")

    t_primary = time.time()
    print(f"\n  Primary runs completed in {t_primary - t0:.1f}s")

    # --- Config ablation runs (30): 10 folios x preferred profile x 3 configs ---
    print("\n--- Config Ablation Runs (30) ---")
    config_ablation_results = {}
    ablation_count = 0

    for folio in CONFIG_ABLATION_FOLIOS:
        toks = tokens_by_folio.get(folio, [])
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        if folio not in config_ablation_results:
            config_ablation_results[folio] = {}

        for cm in CONFIG_MODE_NAMES:
            apparatus = build_configured_apparatus(preferred_profile, cm)
            result = run_excursion_trace(apparatus, toks, line_packets, cts_data)
            config_ablation_results[folio][cm] = result
            ablation_count += 1

            short_cm = cm.split('_')[0]
            print(f"  [{ablation_count:2d}/30] {folio} + {preferred_profile.split('_')[0]} + {short_cm}: "
                  f"WCU={result['WCU']:.4f}, SLR={result['SLR_mean']:.4f}, "
                  f"UEB={result['UEB']:.1f}, CCY={result['CCY']:.4f}")

    t_ablation = time.time()
    print(f"\n  Ablation runs completed in {t_ablation - t_primary:.1f}s")

    # --- Build output ---
    print("\n--- Building output ---")

    # Restructure primary_runs: folio -> {profile_name: {...}}
    primary_runs_out = {}
    for folio in primary_results:
        primary_runs_out[folio] = {}
        for profile_name in PROFILE_NAMES:
            if profile_name in primary_results[folio]:
                primary_runs_out[folio][profile_name] = primary_results[folio][profile_name]

    # Restructure config_ablation_runs: folio -> {config_mode: {...}}
    config_ablation_out = {}
    for folio in config_ablation_results:
        config_ablation_out[folio] = {}
        for cm in CONFIG_MODE_NAMES:
            if cm in config_ablation_results[folio]:
                config_ablation_out[folio][cm] = config_ablation_results[folio][cm]

    # --- Summary statistics (preferred profile runs) ---
    pref_wcu = []
    pref_slr = []
    pref_ueb = []
    pref_ccy = []
    pref_wcp = []
    pref_ewp = []
    pref_pcv = []
    pref_ref = []
    pref_sahb = []
    pref_qgy = []
    pref_viability = []
    pref_y_final = []
    total_hazard = 0

    for folio in primary_results:
        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        if preferred_profile in primary_results[folio]:
            r = primary_results[folio][preferred_profile]
            pref_wcu.append(r['WCU'])
            pref_slr.append(r['SLR_mean'])
            pref_ueb.append(r['UEB'])
            pref_ccy.append(r['CCY'])
            pref_wcp.append(r['WCP_mean'])
            pref_ewp.append(r['EWP'])
            pref_pcv.append(r['PCV'])
            pref_ref.append(r['REF_mean'])
            pref_sahb.append(r['SAHB'])
            pref_qgy.append(r['QGY'])
            pref_viability.append(r['old_viability'])
            pref_y_final.append(r['old_y_final'])
            total_hazard += r['n_hazard_events']

    n_pref = len(pref_wcu)
    mean = lambda lst: sum(lst) / len(lst) if lst else 0.0

    summary = {
        'mean_WCU': round(mean(pref_wcu), 5),
        'mean_SLR': round(mean(pref_slr), 5),
        'mean_UEB': round(mean(pref_ueb), 5),
        'mean_CCY': round(mean(pref_ccy), 5),
        'mean_WCP': round(mean(pref_wcp), 5),
        'mean_EWP': round(mean(pref_ewp), 5),
        'mean_PCV': round(mean(pref_pcv), 5),
        'mean_REF': round(mean(pref_ref), 5),
        'mean_SAHB': round(mean(pref_sahb), 5),
        'mean_QGY': round(mean(pref_qgy), 5),
        'mean_old_viability': round(mean(pref_viability), 5),
        'mean_old_y_final': round(mean(pref_y_final), 5),
        'n_hazard_events': total_hazard,
        'n_preferred_runs': n_pref,
    }

    output = {
        'metadata': {
            'phase': 568,
            'script': 't1_controlled_excursion_executor.py',
            'n_runs': run_count + ablation_count,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cof_normalization': 'frozen_section_p90_from_567_T1_A6',
        },
        'primary_runs': primary_runs_out,
        'config_ablation_runs': config_ablation_out,
        'summary': summary,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = output_path.stat().st_size
    print(f"\n  Output: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # --- Final Statistics ---
    t_final = time.time()
    print("\n--- Final Statistics (preferred-profile runs) ---")
    print(f"  n_preferred_runs: {n_pref}")
    print(f"  total_runs:       {run_count + ablation_count}")
    print(f"  total_time:       {t_final - t0:.1f}s")
    print()
    print(f"  New Metrics:")
    print(f"    mean_WCU:  {mean(pref_wcu):.5f}")
    print(f"    mean_SLR:  {mean(pref_slr):.5f}")
    print(f"    mean_UEB:  {mean(pref_ueb):.1f}")
    print(f"    mean_CCY:  {mean(pref_ccy):.5f}")
    print(f"    mean_WCP:  {mean(pref_wcp):.5f}")
    print(f"    mean_EWP:  {mean(pref_ewp):.1f}")
    print()
    print(f"  Retained Anchors:")
    print(f"    mean_PCV:           {mean(pref_pcv):.5f}")
    print(f"    mean_REF:           {mean(pref_ref):.5f}")
    print(f"    mean_SAHB:          {mean(pref_sahb):.1f}")
    print(f"    mean_QGY:           {mean(pref_qgy):.5f}")
    print()
    print(f"  Legacy:")
    print(f"    mean_old_viability: {mean(pref_viability):.5f}")
    print(f"    mean_old_y_final:   {mean(pref_y_final):.5f}")
    print(f"    total_hazard:       {total_hazard}")

    # Per-folio preferred breakdown
    print(f"\n  Per-folio preferred breakdown:")
    print(f"  {'Folio':<10s} {'WCU':>7s} {'SLR':>7s} {'UEB':>8s} {'CCY':>8s} "
          f"{'WCP':>7s} {'EWP':>8s} {'PCV':>7s} {'viab':>7s}")
    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        if folio in primary_results and pref in primary_results[folio]:
            r = primary_results[folio][pref]
            print(f"  {folio:<10s} {r['WCU']:7.4f} {r['SLR_mean']:7.4f} {r['UEB']:8.1f} "
                  f"{r['CCY']:8.4f} {r['WCP_mean']:7.4f} {r['EWP']:8.1f} "
                  f"{r['PCV']:7.4f} {r['old_viability']:7.4f}")

    print(f"\n  Total runs: {run_count + ablation_count}")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
