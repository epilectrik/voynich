"""
T2: Controlled Excursion Null/Ablation Executor
=================================================
Phase 568 - CONTROLLED_EXCURSION_METRICS

Runs baseline (B1-B10) and null (N1-N4 x 50 permutations) models
with the same metrics as T1 (6 new metrics + retained/legacy metrics).

  New metrics:
    WCU  - Work Corridor Utilization
    SLR  - Same-Line Resolution
    UEB  - Unresolved Excursion Burden
    CCY  - Closure-Conditioned Yield
    WCP  - Work-Closure Packet Coherence
    EWP  - Edge Waste Penalty

  Retained/legacy metrics:
    PCV, REF, SAHB, QGY, old_viability, old_y_final

  COF variants:
    CCY_cof1, CCY_cof2, CCY_cof3

Total: 10 baselines x 20 folios + 4 nulls x 20 folios x 50 perms
     = 200 + 4000 = 4,200 runs + 20 reference = 4,220 runs

Baseline runs (B1-B10):
  B1:  sensitivity x 0.5
  B2:  sensitivity x 0 (no apparatus)
  B3:  decay x 0.5
  B4:  decay x 2.0
  B5:  cross-coupling x 0
  B6:  SPEC phase only (force all tokens to SPEC)
  B7:  WORK phase only
  B8:  CLOSE phase only
  B9:  No discharge events (disable in apparatus)
  B10: No CLOSE recovery (enable_close_recovery=False)

Null runs (N1-N4):
  N1: Phase-shuffle     (randomly permute packet_phase labels within folio)
  N2: Contribution-shuffle (randomly permute contribution vectors within folio)
  N3: Line-shuffle       (randomly permute line order within folio)
  N4: MIDDLE-shuffle     (randomly replace each token's contributions with
                          a random token's contributions from same folio)

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t3_line_packets.json                     (line-level packet_phase)
  - t7_closure_cts.json                      (per-line CTS)
  - t2_folio_budgets.json                    (folio budgets for profile assignment)
  - t1_closure_field_audit.json              (COF normalization bounds A6 section)

Output:
  - t2_controlled_excursion_null_runs.json
"""

import json
import sys
import time
import math
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Import close recovery apparatus (Phase 566 T1)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY' / 'scripts'))
from t1_close_recovery_apparatus import (
    CloseRecoveryApparatus, build_close_recovery_apparatus,
    build_no_close_recovery_apparatus, build_configured_apparatus,
    compute_infra_scores, compute_viability,
    STATE_VARS, SV_INDEX, N_VARS, EQUILIBRIUM, Q1, Q2_BASE, Q3_BASE,
    HAZARD_BOUNDARIES, HAZARD_DEV, PILOT_FOLIOS, PROFILES,
    GAMMA_CORRIDOR, assign_folio_profiles,
    CORRIDOR_MULT, BASIN_MULT,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
T2B_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
            / 't2b_supervisory_interface_unrouted.json')
PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                / 'results' / 't3_line_packets.json')
CTS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
            / 'results' / 't7_closure_cts.json')
BUDGET_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't2_folio_budgets.json')
COF_NORMS_PATH = (PROJECT_ROOT / 'phases' / 'CLOSURE_FIELD_AUDIT' / 'results'
                  / 't1_closure_field_audit.json')
REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
OUTPUT_PATH = PHASE_DIR / 'results' / 't2_controlled_excursion_null_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (same as 567 T3)
# ---------------------------------------------------------------------------
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

ROUTING_CONTRIB_GAIN = 0.3
ROUTING_DECAY = 0.7

# Process SVs (those with at least one hazard boundary, excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# S and Y indices
S_IDX = SV_INDEX['S']
Y_IDX = SV_INDEX['Y']

# ---------------------------------------------------------------------------
# Preferred folio profiles (dynamic via assign_folio_profiles, matching T1)
# ---------------------------------------------------------------------------
_PREFERRED_PROFILE_MAP = None  # Lazily initialized


def _init_preferred_profiles():
    """Initialize preferred profile map from assign_folio_profiles (same as T1)."""
    global _PREFERRED_PROFILE_MAP
    if _PREFERRED_PROFILE_MAP is not None:
        return
    _PREFERRED_PROFILE_MAP = {}
    fa = assign_folio_profiles(REGIME_PATH, BUDGET_PATH)
    for folio in PILOT_FOLIOS:
        entry = fa.get(folio, {})
        _PREFERRED_PROFILE_MAP[folio] = entry.get('preferred_profile', 'A1_BATH_REFLUX')


def get_preferred_profile(folio):
    """Return the preferred profile for a folio."""
    _init_preferred_profiles()
    return _PREFERRED_PROFILE_MAP.get(folio, 'A1_BATH_REFLUX')


# ---------------------------------------------------------------------------
# WCU zone scores (per WORK-phase token, per process SV)
# ---------------------------------------------------------------------------
WCU_ZONE_SCORES = {
    'BASIN': 0.3,
    'CORRIDOR': 1.0,
    'WARNING': 0.1,
    'HARD_STOP': -1.0,
    'HAZARD': -2.0,
}
WCU_S_HIGH_SCORE = 1.0  # S above EQ -> +1.0

# ---------------------------------------------------------------------------
# PCV desirability tables (frozen, from 567 T3)
# ---------------------------------------------------------------------------
PCV_PROCESS_SVS = ['T', 'RC', 'C', 'TR', 'X']

PCV_ZONE_SCORES = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

PCV_S_HIGH_SCORES = {
    'SPEC':  0.9,
    'WORK':  1.0,
    'CLOSE': 0.9,
}

# SAHB weights
SAHB_WARNING_WEIGHT = 1.0
SAHB_HARDSTOP_WEIGHT = 3.0
SAHB_OUTSIDE_CORRIDOR_WEIGHT = 0.5
SAHB_MAX_EXCURSION_WEIGHT = 2.0


# ---------------------------------------------------------------------------
# Zone classification (5-zone: BASIN/CORRIDOR/WARNING/HARD_STOP/HAZARD)
# ---------------------------------------------------------------------------
def _classify_zone(sv, dev_abs):
    """Classify a deviation into one of the 5 zones."""
    q2 = Q2_BASE[sv]
    q3 = q2 + 0.05
    q3 = min(q3, HAZARD_DEV[sv] - 0.01)

    if dev_abs < Q1:
        return 'BASIN'
    elif dev_abs < q2:
        return 'CORRIDOR'
    elif dev_abs < q3:
        return 'WARNING'
    elif dev_abs < HAZARD_DEV[sv]:
        return 'HARD_STOP'
    else:
        return 'HAZARD'


# ---------------------------------------------------------------------------
# Hazard check
# ---------------------------------------------------------------------------
def is_in_bounds(state):
    """Check if state is within all hazard boundaries."""
    for i, sv in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[sv]
        if lo is not None and state[i] < lo:
            return False
        if hi is not None and state[i] > hi:
            return False
    return True


# ---------------------------------------------------------------------------
# Sort key for tokens
# ---------------------------------------------------------------------------
def sort_key(tok):
    try:
        ln = int(tok['line'])
    except (ValueError, TypeError):
        ln = 0
    lp = tok.get('line_pos', 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


# ---------------------------------------------------------------------------
# PCV computation (from 567 T3 -- frozen)
# ---------------------------------------------------------------------------
def _pcv_token_score(state, packet_phase):
    """Compute PCV score for one token. Process SVs + S asymmetric. Y excluded."""
    score_sum = 0.0
    count = 0
    phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])

    for sv in PCV_PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, dev)
        if dev >= HAZARD_DEV[sv]:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
        count += 1

    # S: asymmetric handling
    s_val = state[S_IDX]
    s_dev = abs(s_val - EQUILIBRIUM)
    if s_val > EQUILIBRIUM:
        score_sum += PCV_S_HIGH_SCORES.get(packet_phase, 1.0)
    else:
        zone = _classify_zone('S', s_dev)
        if s_dev >= HAZARD_DEV['S']:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
    count += 1

    return score_sum, count


# ---------------------------------------------------------------------------
# SAHB computation (from 567 T3 -- frozen)
# ---------------------------------------------------------------------------
def _sahb_token(state, packet_phase):
    """Compute SAHB components for one token. Skip S penalty when S > EQ."""
    warnings = 0
    hardstops = 0
    outside_corridor = 0
    max_excursion = 0.0

    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, dev)

        if sv == 'S' and state[S_IDX] > EQUILIBRIUM:
            continue

        if zone == 'WARNING':
            warnings += 1
        elif zone == 'HARD_STOP':
            hardstops += 1

        if zone in ('WARNING', 'HARD_STOP'):
            outside_corridor += 1

        if dev > max_excursion:
            max_excursion = dev

    return warnings, hardstops, outside_corridor, max_excursion


# ---------------------------------------------------------------------------
# COF normalization helper
# ---------------------------------------------------------------------------
def _normalize_cof_component(val, p90):
    """Normalize a COF component value using P90 bound. Clamp to [0, 1]."""
    if p90 <= 0:
        return 0.0
    return min(val / p90, 1.0)


# ---------------------------------------------------------------------------
# Core execution function: run_controlled_excursion_trace
# ---------------------------------------------------------------------------
def run_controlled_excursion_trace(apparatus, tokens, line_packets,
                                    cof_norms, line_cts_map, line_components,
                                    line_section_map,
                                    disable_routing=False, disable_cts=False,
                                    disable_discharge=False, force_phase=None,
                                    override_contributions=None):
    """
    Run one folio through the close recovery apparatus.

    Computes:
      - 6 NEW metrics: WCU, SLR, UEB, CCY, WCP, EWP
      - Retained/legacy: PCV, SAHB, REF, QGY, old_viability, old_y_final
      - COF variants: CCY_cof1, CCY_cof2, CCY_cof3

    Parameters:
      apparatus:            CloseRecoveryApparatus instance
      tokens:               list of token dicts, pre-sorted by (line, position)
      line_packets:         dict mapping "folio|line" -> packet info
      cof_norms:            dict of section -> {comp_name -> P90 value}
      line_cts_map:         dict mapping "folio|line" -> CTS value
      line_components:      dict mapping "folio|line" -> {comp_name -> value}
      line_section_map:     dict mapping "folio|line" -> section string
      disable_routing:      if True, routing buffers are disabled
      disable_cts:          if True, CTS is forced to 0
      disable_discharge:    if True, discharge events are disabled
      force_phase:          if set, override packet_phase for all tokens
      override_contributions: if set, use this contribution vector for all tokens

    Returns dict with all metrics.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return _empty_result()

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    permissivity_buffer = {}
    prev_line = None

    # --- OLD / retained accumulators ---
    n_viable = 0
    hazard_count = 0

    # PCV
    pcv_score_sum = 0.0
    pcv_count = 0

    # SAHB
    sahb_warnings = 0
    sahb_hardstops = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # REF: per-line work_end and close_end deviations
    line_work_end_devs = {}
    line_close_end_devs = {}

    # QGY
    qgy_total = 0.0
    prev_aggregate_dev = None

    # --- NEW metric accumulators ---

    # WCU: Work Corridor Utilization
    wcu_score_sum = 0.0
    wcu_pair_count = 0

    # SLR: Same-Line Resolution (per-line tracking)
    # Accumulated per-line, finalized at line boundaries
    line_slr_data = {}  # line_key -> {work_end_dev, close_end_dev,
                        #               corridor_return, work_quality}

    # UEB: Unresolved Excursion Burden
    ueb_close_warnings = 0
    ueb_close_hardstops = 0
    ueb_unresolved_fractions = []  # per-line unresolved fraction
    ueb_line_final_hardstop = 0
    ueb_post_line_residual_above_q2 = 0

    # CCY: Closure-Conditioned Yield
    # Per-token in CLOSE phase: check 5 conditions
    ccy_qualifying_y = 0.0  # sum of y_delta meeting all 5 conditions
    ccy_total_y = 0.0       # total y_delta across all CLOSE tokens
    ccy_qualifying_count = 0
    ccy_total_close_count = 0
    # COF variants
    ccy_cof1_y = 0.0
    ccy_cof2_y = 0.0
    ccy_cof3_y = 0.0

    # WCP: Work-Closure Packet Coherence (per-line)
    wcp_line_scores = []  # list of per-line WCP scores
    wcp_full_packet_scores = []

    # EWP: Edge Waste Penalty
    ewp_prolonged_hardstop = 0
    ewp_unresolved_warning = 0
    ewp_post_close_residual = 0
    ewp_edge_persistence = 0

    # --- Per-line tracking state ---
    current_line_key = None
    current_line_work_end_state = None
    current_line_close_end_state = None
    current_line_phase = None

    # Per-line zone tracking for WCP
    line_spec_scores = []
    line_work_scores = []
    line_close_scores = []
    line_has_spec = False
    line_has_work = False
    line_has_close = False

    # Per-line WORK-phase peak deviation tracking for SLR + CCY
    line_work_peak_dev = 0.0
    line_work_peak_svs_above_q2 = 0  # SVs above Q2 at peak moment

    # EWP: consecutive hard-stop tracking in WORK
    consecutive_work_hardstops = 0

    # EWP: per-line CLOSE warning tracking
    line_close_warning_svs = set()
    line_close_end_warning_svs = set()

    # EWP: post-close residual tracking
    line_last_close_state = None
    line_had_close = False

    # Per-line Q2 excursion tracking for SLR corridor_return
    line_work_q2_exceeded = set()   # SVs that exceeded Q2 during WORK
    line_close_q2_returned = set()  # SVs that returned below Q2 during CLOSE

    # Per-line WORK quality tracking
    line_work_corridor_tokens = 0
    line_work_total_tokens = 0

    # SLR: accumulation
    slr_values = []
    slr_eligible_count = 0
    slr_work_peak_devs = []

    # CCY: tracking for net corridor improvement
    ccy_work_mean_dev = None   # mean dev at end of most recent WORK phase
    ccy_work_svs_above_q2 = 0  # count of SVs above Q2 at end of WORK

    def _finalize_line():
        """Finalize metrics for the departing line."""
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_post_close_residual, ewp_edge_persistence
        nonlocal ewp_unresolved_warning
        nonlocal ccy_work_mean_dev, ccy_work_svs_above_q2

        if current_line_key is None:
            return

        # Save REF data
        if current_line_work_end_state is not None:
            line_work_end_devs[current_line_key] = [
                abs(current_line_work_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS)
            ]
        if current_line_close_end_state is not None:
            line_close_end_devs[current_line_key] = [
                abs(current_line_close_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS)
            ]

        # UEB: line_final_hardstop — any SV in HARD_STOP at line end
        # (S above EQ excluded)
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            zone = _classify_zone(sv, dev)
            if zone == 'HARD_STOP':
                ueb_line_final_hardstop += 1
                break  # count per line, not per SV

        # UEB: post_line_residual_above_Q2
        residual_count = 0
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            if dev >= Q2_BASE[sv]:
                residual_count += 1
        if residual_count > 0:
            ueb_post_line_residual_above_q2 += residual_count

        # UEB: unresolved fraction per line
        if current_line_work_end_state is not None and current_line_close_end_state is not None:
            work_devs = [abs(current_line_work_end_state[i] - EQUILIBRIUM)
                         for i in range(N_VARS) if i != Y_IDX]
            close_devs = [abs(current_line_close_end_state[i] - EQUILIBRIUM)
                          for i in range(N_VARS) if i != Y_IDX]
            n_unresolved = sum(1 for w, c in zip(work_devs, close_devs)
                               if c >= w and w > Q1)
            n_eligible = sum(1 for w in work_devs if w > Q1)
            if n_eligible > 0:
                ueb_unresolved_fractions.append(n_unresolved / n_eligible)

        # SLR: compute per-line value
        if current_line_work_end_state is not None:
            work_end_dev = sum(
                abs(current_line_work_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS) if i != Y_IDX
            ) / (N_VARS - 1)

            if work_end_dev > Q1:  # eligible
                close_end_dev = work_end_dev  # default if no CLOSE
                if current_line_close_end_state is not None:
                    close_end_dev = sum(
                        abs(current_line_close_end_state[i] - EQUILIBRIUM)
                        for i in range(N_VARS) if i != Y_IDX
                    ) / (N_VARS - 1)

                # corridor_return: fraction of WORK-excursion SVs resolved
                n_exc = len(line_work_q2_exceeded)
                n_ret = len(line_work_q2_exceeded & line_close_q2_returned)
                corridor_return = n_ret / n_exc if n_exc > 0 else 0.0

                # work_quality: fraction of WORK tokens in CORRIDOR
                work_quality = (line_work_corridor_tokens / line_work_total_tokens
                                if line_work_total_tokens > 0 else 0.0)

                slr_val = (0.5 * (1.0 - close_end_dev / work_end_dev
                                  if work_end_dev > 1e-10 else 0.0)
                           + 0.3 * corridor_return
                           + 0.2 * work_quality)
                slr_val = max(-1.0, min(1.0, slr_val))

                slr_values.append(slr_val)
                slr_work_peak_devs.append(line_work_peak_dev)

        # WCP: compute per-line score
        _compute_line_wcp()

        # EWP: unresolved_warning (CLOSE warnings not resolved by line end)
        unresolved_warnings = line_close_warning_svs & line_close_end_warning_svs
        ewp_unresolved_warning += len(unresolved_warnings)

        # EWP: post_close_residual
        if line_had_close and current_line_close_end_state is not None:
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and current_line_close_end_state[i] > EQUILIBRIUM:
                    continue
                dev = abs(current_line_close_end_state[i] - EQUILIBRIUM)
                if dev >= Q2_BASE[sv]:
                    ewp_post_close_residual += 1

        # EWP: edge_persistence (SVs at HARD_STOP for > half the line tokens)
        # We track this at a simplified level: count lines where final state
        # has any SV at HARD_STOP
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            zone = _classify_zone(sv, dev)
            if zone in ('HARD_STOP', 'HAZARD'):
                ewp_edge_persistence += 1
                break

        # CCY: update WORK-peak dev for the next CLOSE phase
        # Use work PEAK dev (not work END dev) per plan spec
        if current_line_work_end_state is not None and line_work_peak_dev > 0:
            ccy_work_mean_dev = line_work_peak_dev
            ccy_work_svs_above_q2 = line_work_peak_svs_above_q2

    def _compute_line_wcp():
        """Compute WCP score for the current line with phase-presence masking."""
        # Base weights: SPEC=0.2, WORK=0.5, CLOSE=0.3
        w_spec, w_work, w_close = 0.2, 0.5, 0.3

        spec_score = sum(line_spec_scores) / len(line_spec_scores) if line_spec_scores else None
        work_score = sum(line_work_scores) / len(line_work_scores) if line_work_scores else None
        close_score = sum(line_close_scores) / len(line_close_scores) if line_close_scores else None

        present = []
        scores = []
        weights = []

        if line_has_spec and spec_score is not None:
            present.append('SPEC')
            scores.append(spec_score)
            weights.append(w_spec)
        if line_has_work and work_score is not None:
            present.append('WORK')
            scores.append(work_score)
            weights.append(w_work)
        if line_has_close and close_score is not None:
            present.append('CLOSE')
            scores.append(close_score)
            weights.append(w_close)

        if not scores:
            return

        total_w = sum(weights)
        wcp_val = sum(s * w for s, w in zip(scores, weights)) / total_w
        wcp_line_scores.append(wcp_val)

        # Full packet mean (only for lines with all 3 phases)
        if len(present) == 3:
            wcp_full_packet_scores.append(wcp_val)

    # =====================================================================
    # MAIN LOOP
    # =====================================================================
    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok.get('folio', '')

        # Save pre-update state
        pre_state = list(state)

        # 1. Line boundary handling
        if current_line != prev_line:
            # Finalize previous line
            if prev_line is not None:
                _finalize_line()

            # Reset line-level tracking
            routing_contrib_buffer = [0.0] * N_VARS
            permissivity_buffer = {}
            prev_line = current_line
            current_line_key = f"{folio}|{current_line}"
            current_line_work_end_state = None
            current_line_close_end_state = None
            current_line_phase = None

            # WCP per-line reset
            line_spec_scores = []
            line_work_scores = []
            line_close_scores = []
            line_has_spec = False
            line_has_work = False
            line_has_close = False

            # SLR per-line reset
            line_work_peak_dev = 0.0
            line_work_peak_svs_above_q2 = 0
            line_work_q2_exceeded = set()
            line_close_q2_returned = set()
            line_work_corridor_tokens = 0
            line_work_total_tokens = 0

            # EWP per-line reset
            consecutive_work_hardstops = 0
            line_close_warning_svs = set()
            line_close_end_warning_svs = set()
            line_last_close_state = None
            line_had_close = False

        # 2. Routing event -> update buffers (unless disabled)
        if not disable_routing:
            if tok.get('routing_active') and tok.get('routing_terminal'):
                rt = tok['routing_terminal']
                if rt in ROUTING_EFFECTS:
                    effects = ROUTING_EFFECTS[rt]
                    for sv, mult in effects.get('boost', {}).items():
                        routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                    for sv, mult in effects.get('suppress', {}).items():
                        routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN

        # 3. Look up packet_phase from line_packets
        if force_phase is not None:
            packet_phase = force_phase
        else:
            line_key = f"{folio}|{current_line}"
            packet = line_packets.get(line_key)
            if packet and 'packet_state' in packet:
                packet_phase = packet['packet_state'].get('packet_phase', 'WORK')
            else:
                packet_phase = tok.get('packet_phase', 'WORK')

        current_line_phase = packet_phase

        # 4. Get CTS from line_cts_map (unless disabled)
        line_key_cts = f"{folio}|{current_line}"
        if disable_cts:
            cts = 0.0
        else:
            cts = line_cts_map.get(line_key_cts, tok.get('cts', 0.0))

        # 5. Compute buffered dV
        if override_contributions is not None:
            contributions = override_contributions
        else:
            contributions = tok['contributions']

        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            base_sens = apparatus.sensitivity[sv]
            dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])

        # 6. Build permissivity for this step
        if not disable_routing and permissivity_buffer:
            perm = {}
            for key, val in permissivity_buffer.items():
                if 'X' in key:
                    perm['X'] = perm.get('X', 0.0) + val * 0.5
                elif 'T' in key:
                    perm['T'] = perm.get('T', 0.0) + val * 0.5
                elif 'C' in key:
                    perm['C'] = perm.get('C', 0.0) + val * 0.5
                elif 'S' in key:
                    perm['S'] = perm.get('S', 0.0) + val * 0.5
            if not perm:
                perm = None
        else:
            perm = None

        # 7. Update state via apparatus
        if disable_discharge:
            if hasattr(apparatus, 'base'):
                cc_raw = apparatus.base._cross_coupling(state, packet_phase)
                bias = apparatus.base.equil_bias[packet_phase]
                cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]
                rf, zones_diag = apparatus._uniform_restoring_force(state, packet_phase)
                new_state = []
                for i in range(N_VARS):
                    v = state[i] + dV[i] + cc[i] - rf[i]
                    new_state.append(max(0.0, min(1.0, v)))
                dv_mag = sum(abs(v) for v in dV)
                recovery, recovery_details = apparatus.base._apply_close_recovery(
                    new_state, packet_phase, cts, dv_mag)
                for i in range(N_VARS):
                    new_state[i] = max(0.0, min(1.0, new_state[i] + recovery[i]))
                state = new_state
                diagnostics = {
                    'zones': {STATE_VARS[i]: zones_diag[i] for i in range(N_VARS)},
                    'discharge_events': [],
                    'close_recovery': recovery_details,
                }
            else:
                cc_raw = apparatus._cross_coupling(state, packet_phase)
                bias = apparatus.equil_bias[packet_phase]
                cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]
                rf, zones_diag = apparatus._restoring_force(state, packet_phase, perm)
                new_state = []
                for i in range(N_VARS):
                    v = state[i] + dV[i] + cc[i] - rf[i]
                    new_state.append(max(0.0, min(1.0, v)))
                dv_mag = sum(abs(v) for v in dV)
                recovery, recovery_details = apparatus._apply_close_recovery(
                    new_state, packet_phase, cts, dv_mag)
                for i in range(N_VARS):
                    new_state[i] = max(0.0, min(1.0, new_state[i] + recovery[i]))
                state = new_state
                diagnostics = {
                    'zones': {STATE_VARS[i]: zones_diag[i] for i in range(N_VARS)},
                    'discharge_events': [],
                    'close_recovery': recovery_details,
                }
        else:
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts, perm)

        # 8. Decay routing buffers
        if not disable_routing:
            routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]
            new_perm = {}
            for k, v in permissivity_buffer.items():
                decayed = v * ROUTING_DECAY
                if abs(decayed) > 1e-10:
                    new_perm[k] = decayed
            permissivity_buffer = new_perm

        # ================================================================
        # RETAINED METRICS
        # ================================================================

        # Viability check
        if is_in_bounds(state):
            n_viable += 1
        else:
            hazard_count += 1

        # PCV
        pcv_s, pcv_c = _pcv_token_score(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_count += pcv_c

        # SAHB
        sw, sh, soc, sme = _sahb_token(state, packet_phase)
        sahb_warnings += sw
        sahb_hardstops += sh
        sahb_outside_corridor += soc
        if sme > sahb_max_excursion:
            sahb_max_excursion = sme

        # REF tracking
        if packet_phase == 'WORK':
            current_line_work_end_state = list(state)
        elif packet_phase == 'CLOSE':
            current_line_close_end_state = list(state)

        # QGY
        if packet_phase == 'CLOSE':
            current_aggregate_dev = sum(abs(state[i] - EQUILIBRIUM)
                                        for i in range(N_VARS) if i != Y_IDX)
            if cts > 0.3 and prev_aggregate_dev is not None:
                if current_aggregate_dev < prev_aggregate_dev:
                    y_increment = state[Y_IDX] - pre_state[Y_IDX]
                    if y_increment > 0:
                        qgy_total += y_increment
            prev_aggregate_dev = current_aggregate_dev
        else:
            prev_aggregate_dev = None

        # ================================================================
        # NEW METRICS
        # ================================================================

        # ---- WCU: Work Corridor Utilization ----
        if packet_phase == 'WORK':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                dev = abs(state[i] - EQUILIBRIUM)

                # S above EQ -> +1.0
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    wcu_score_sum += WCU_S_HIGH_SCORE
                else:
                    zone = _classify_zone(sv, dev)
                    if dev >= HAZARD_DEV[sv]:
                        wcu_score_sum += WCU_ZONE_SCORES['HAZARD']
                    else:
                        wcu_score_sum += WCU_ZONE_SCORES.get(zone, 0.0)
                wcu_pair_count += 1

            # Y excluded from WCU

        # ---- SLR tracking ----
        if packet_phase == 'WORK':
            line_work_total_tokens += 1
            # Track peak deviation for this line's WORK phase
            work_dev = sum(abs(state[i] - EQUILIBRIUM)
                           for i in range(N_VARS) if i != Y_IDX) / (N_VARS - 1)
            if work_dev > line_work_peak_dev:
                line_work_peak_dev = work_dev
                # Count SVs above Q2 at this peak moment
                line_work_peak_svs_above_q2 = sum(
                    1 for sv in PROCESS_SVS
                    if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) >= Q2_BASE[sv]
                    and not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
                )

            # Track Q2 excursions and WORK quality
            any_in_corridor = True
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev >= Q2_BASE[sv]:
                    line_work_q2_exceeded.add(sv)
                    any_in_corridor = False

            # WORK quality: count tokens where all process SVs are in
            # BASIN or CORRIDOR
            all_ok = all(
                abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                for sv in PROCESS_SVS
                if not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
            )
            if all_ok:
                line_work_corridor_tokens += 1

        elif packet_phase == 'CLOSE':
            # Track Q2 returns for SLR corridor_return
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev < Q2_BASE[sv]:
                    line_close_q2_returned.add(sv)

        # ---- UEB tracking ----
        if packet_phase == 'CLOSE':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = _classify_zone(sv, dev)
                if zone == 'WARNING':
                    ueb_close_warnings += 1
                elif zone == 'HARD_STOP':
                    ueb_close_hardstops += 1

        # ---- CCY tracking ----
        if packet_phase == 'CLOSE':
            ccy_total_close_count += 1
            y_delta = state[Y_IDX] - pre_state[Y_IDX]
            if y_delta > 0:
                ccy_total_y += y_delta

            # Current aggregate deviation
            current_agg_dev = sum(
                abs(state[i] - EQUILIBRIUM)
                for i in range(N_VARS) if i != Y_IDX
            ) / (N_VARS - 1)

            # Current SVs above Q2 (excluding S above EQ)
            current_svs_above_q2 = sum(
                1 for sv in PROCESS_SVS
                if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) >= Q2_BASE[sv]
                and not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
            )

            # Check 5 conditions:
            # 1. CLOSE phase (already true)
            # 2. CTS > 0.3
            cond_cts = cts > 0.3
            # 3. Aggregate dev < WORK peak
            cond_dev = (ccy_work_mean_dev is not None
                        and ccy_work_mean_dev > 0
                        and current_agg_dev < ccy_work_mean_dev)
            # 4. Net corridor improvement: mean dev down AND SVs above Q2 decreased
            # When work_peak_svs_above_q2 == 0, second part is vacuously true
            if ccy_work_mean_dev is not None and ccy_work_mean_dev > 0:
                if ccy_work_svs_above_q2 == 0:
                    cond_improvement = current_agg_dev < ccy_work_mean_dev
                else:
                    cond_improvement = (current_agg_dev < ccy_work_mean_dev
                                        and current_svs_above_q2 < ccy_work_svs_above_q2)
            else:
                cond_improvement = False
            # 5. y_delta > 0
            cond_y = y_delta > 0

            if cond_cts and cond_dev and cond_improvement and cond_y:
                ccy_qualifying_y += y_delta
                ccy_qualifying_count += 1

                # COF variants: use per-line COF values
                lk = f"{folio}|{current_line}"
                comp = line_components.get(lk)
                sec = line_section_map.get(lk, 'B')
                section_norms = cof_norms.get(sec, cof_norms.get('B', {}))

                if comp is not None:
                    nq4 = _normalize_cof_component(
                        comp.get('q4_opaque_rate', 0.0),
                        section_norms.get('q4_opaque_rate', 1.0))
                    nmcb = _normalize_cof_component(
                        comp.get('m_close_bias', 0.0),
                        section_norms.get('m_close_bias', 1.0))
                    ncob = _normalize_cof_component(
                        comp.get('close_opacity_bias', 0.0),
                        section_norms.get('close_opacity_bias', 1.0))
                    nq4s = _normalize_cof_component(
                        comp.get('q4_shift_strength', 0.0),
                        section_norms.get('q4_shift_strength', 1.0))

                    cof1 = 0.6 * cts + 0.4 * nq4
                    cof2 = 0.5 * cts + 0.25 * nq4 + 0.25 * nmcb
                    cof3 = 0.3 * cts + 0.2 * nq4s + 0.2 * ncob + 0.3 * nmcb

                    ccy_cof1_y += y_delta * cof1
                    ccy_cof2_y += y_delta * cof2
                    ccy_cof3_y += y_delta * cof3
                else:
                    # Fallback: use raw CTS
                    ccy_cof1_y += y_delta * cts
                    ccy_cof2_y += y_delta * cts
                    ccy_cof3_y += y_delta * cts

        # ---- WCP tracking ----
        # Compute per-token zone quality for the current phase
        token_zone_quality = 0.0
        n_svs_counted = 0
        phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])
        for sv in PCV_PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            zone = _classify_zone(sv, dev)
            if dev >= HAZARD_DEV[sv]:
                token_zone_quality += phase_scores.get('HAZARD', 0.0)
            else:
                token_zone_quality += phase_scores.get(zone, 0.0)
            n_svs_counted += 1
        # S handling
        s_val = state[S_IDX]
        if s_val > EQUILIBRIUM:
            token_zone_quality += PCV_S_HIGH_SCORES.get(packet_phase, 1.0)
        else:
            s_dev = abs(s_val - EQUILIBRIUM)
            zone = _classify_zone('S', s_dev)
            if s_dev >= HAZARD_DEV['S']:
                token_zone_quality += phase_scores.get('HAZARD', 0.0)
            else:
                token_zone_quality += phase_scores.get(zone, 0.0)
        n_svs_counted += 1

        if n_svs_counted > 0:
            quality = token_zone_quality / n_svs_counted
        else:
            quality = 0.0

        if packet_phase == 'SPEC':
            line_spec_scores.append(quality)
            line_has_spec = True
        elif packet_phase == 'WORK':
            line_work_scores.append(quality)
            line_has_work = True
        elif packet_phase == 'CLOSE':
            line_close_scores.append(quality)
            line_has_close = True

        # ---- EWP tracking ----
        if packet_phase == 'WORK':
            # prolonged_hardstop: > 2 consecutive tokens with any SV at HARD_STOP
            any_hardstop = False
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = _classify_zone(sv, dev)
                if zone in ('HARD_STOP', 'HAZARD'):
                    any_hardstop = True
                    break
            if any_hardstop:
                consecutive_work_hardstops += 1
                if consecutive_work_hardstops > 2:
                    ewp_prolonged_hardstop += 1
            else:
                consecutive_work_hardstops = 0

        if packet_phase == 'CLOSE':
            line_had_close = True
            line_last_close_state = list(state)
            # Track CLOSE warnings for unresolved_warning
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = _classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_warning_svs.add(sv)

            # Track end-of-CLOSE warning state
            line_close_end_warning_svs = set()
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = _classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_end_warning_svs.add(sv)

    # Finalize last line
    _finalize_line()

    # ================================================================
    # Compute final metric values
    # ================================================================

    # --- Retained/legacy ---

    # Old viability
    old_viability = round(n_viable / n_tokens, 6) if n_tokens > 0 else 1.0
    old_y_final = round(state[Y_IDX], 6)

    # PCV
    pcv = round(pcv_score_sum / pcv_count, 6) if pcv_count > 0 else 1.0

    # SAHB (normalized by n_tokens)
    sahb_raw = (SAHB_WARNING_WEIGHT * sahb_warnings
                + SAHB_HARDSTOP_WEIGHT * sahb_hardstops
                + SAHB_OUTSIDE_CORRIDOR_WEIGHT * sahb_outside_corridor
                + SAHB_MAX_EXCURSION_WEIGHT * sahb_max_excursion)
    sahb = round(sahb_raw / n_tokens, 6) if n_tokens > 0 else 0.0

    # REF
    ref_eligible = 0
    ref_resolved_sum = 0.0
    ref_worsened = 0
    for lk in line_work_end_devs:
        if lk not in line_close_end_devs:
            continue
        work_devs = line_work_end_devs[lk]
        close_devs = line_close_end_devs[lk]
        for i in range(N_VARS):
            if i == Y_IDX:
                continue
            wed = work_devs[i]
            ced = close_devs[i]
            if wed > Q1:
                ref_eligible += 1
                ref_val = 1.0 - (ced / wed) if wed > 1e-10 else 0.0
                ref_resolved_sum += ref_val
                if ced > wed:
                    ref_worsened += 1

    ref_mean = round(ref_resolved_sum / ref_eligible, 6) if ref_eligible > 0 else 0.0
    total_lines_with_both = sum(1 for lk in line_work_end_devs if lk in line_close_end_devs)
    total_possible_ref = total_lines_with_both * (N_VARS - 1)
    ref_elig_frac = round(ref_eligible / total_possible_ref, 6) if total_possible_ref > 0 else 0.0

    # QGY
    qgy = round(qgy_total, 6)
    qgy_ratio = round(qgy_total / state[Y_IDX], 6) if state[Y_IDX] > 1e-10 else 0.0

    # --- NEW metrics ---

    # WCU
    wcu = round(wcu_score_sum / wcu_pair_count, 6) if wcu_pair_count > 0 else 0.0

    # SLR
    slr_mean = round(sum(slr_values) / len(slr_values), 6) if slr_values else 0.0
    slr_eligible_frac = round(len(slr_values) / max(1, len(line_work_end_devs)), 6)
    slr_eligible_count_val = len(slr_values)
    slr_mean_work_peak_dev = (round(sum(slr_work_peak_devs) / len(slr_work_peak_devs), 6)
                               if slr_work_peak_devs else 0.0)

    # UEB
    mean_uf = (sum(ueb_unresolved_fractions) / len(ueb_unresolved_fractions)
               if ueb_unresolved_fractions else 0.0)
    ueb = round(
        1.0 * ueb_close_warnings
        + 3.0 * ueb_close_hardstops
        + 2.0 * mean_uf
        + 5.0 * ueb_line_final_hardstop
        + 1.5 * ueb_post_line_residual_above_q2,
        6
    )

    # CCY
    ccy = round(ccy_qualifying_y, 6)
    ccy_ratio = round(ccy_qualifying_y / ccy_total_y, 6) if ccy_total_y > 1e-10 else 0.0
    ccy_cof1 = round(ccy_cof1_y, 6)
    ccy_cof2 = round(ccy_cof2_y, 6)
    ccy_cof3 = round(ccy_cof3_y, 6)

    # WCP
    wcp = round(sum(wcp_line_scores) / len(wcp_line_scores), 6) if wcp_line_scores else 0.0
    wcp_full = (round(sum(wcp_full_packet_scores) / len(wcp_full_packet_scores), 6)
                if wcp_full_packet_scores else 0.0)

    # EWP
    ewp = round(
        1.0 * ewp_prolonged_hardstop
        + 2.0 * ewp_unresolved_warning
        + 3.0 * ewp_post_close_residual
        + 5.0 * ewp_edge_persistence,
        6
    )

    return {
        # Retained/legacy
        'old_viability': old_viability,
        'old_y_final': old_y_final,
        'PCV': pcv,
        'SAHB': sahb,
        'REF_mean': ref_mean,
        'REF_eligible_fraction': ref_elig_frac,
        'QGY': qgy,
        'qgy_ratio': qgy_ratio,
        # New metrics
        'WCU': wcu,
        'SLR_mean': slr_mean,
        'SLR_eligible_fraction': slr_eligible_frac,
        'SLR_eligible_count': slr_eligible_count_val,
        'SLR_mean_work_peak_dev': slr_mean_work_peak_dev,
        'UEB': ueb,
        'CCY': ccy,
        'CCY_ratio': ccy_ratio,
        'CCY_cof1': ccy_cof1,
        'CCY_cof2': ccy_cof2,
        'CCY_cof3': ccy_cof3,
        'WCP': wcp,
        'WCP_full_packet_mean': wcp_full,
        'EWP': ewp,
    }


def _empty_result():
    """Return empty result dict for folios with no tokens."""
    return {
        'old_viability': 1.0,
        'old_y_final': 0.5,
        'PCV': 1.0,
        'SAHB': 0.0,
        'REF_mean': 0.0,
        'REF_eligible_fraction': 0.0,
        'QGY': 0.0,
        'qgy_ratio': 0.0,
        'WCU': 0.0,
        'SLR_mean': 0.0,
        'SLR_eligible_fraction': 0.0,
        'SLR_eligible_count': 0,
        'SLR_mean_work_peak_dev': 0.0,
        'UEB': 0.0,
        'CCY': 0.0,
        'CCY_ratio': 0.0,
        'CCY_cof1': 0.0,
        'CCY_cof2': 0.0,
        'CCY_cof3': 0.0,
        'WCP': 0.0,
        'WCP_full_packet_mean': 0.0,
        'EWP': 0.0,
    }


# ---------------------------------------------------------------------------
# Null model generators
# ---------------------------------------------------------------------------

def null_n1_phase_shuffle(tokens, line_packets, rng):
    """N1: Phase-shuffle. Randomly permute packet_phase labels within each folio.

    We shuffle the line_packets dict values' packet_phase labels.
    Returns modified line_packets dict (tokens unchanged).
    """
    folio = tokens[0]['folio'] if tokens else ''
    folio_line_keys = [f"{folio}|{tok['line']}" for tok in tokens]
    unique_keys = list(dict.fromkeys(folio_line_keys))  # preserve order, dedupe

    # Collect existing phases for this folio's lines
    phases = []
    for k in unique_keys:
        pkt = line_packets.get(k)
        if pkt and 'packet_state' in pkt:
            phases.append(pkt['packet_state'].get('packet_phase', 'WORK'))
        else:
            phases.append('WORK')

    # Shuffle phases
    rng.shuffle(phases)

    # Build modified line_packets
    modified_lp = dict(line_packets)
    for k, new_phase in zip(unique_keys, phases):
        if k in modified_lp:
            # Deep copy the packet dict to avoid modifying original
            pkt_copy = dict(modified_lp[k])
            ps_copy = dict(pkt_copy.get('packet_state', {}))
            ps_copy['packet_phase'] = new_phase
            pkt_copy['packet_state'] = ps_copy
            modified_lp[k] = pkt_copy

    return tokens, modified_lp


def null_n2_contribution_shuffle(tokens, rng):
    """N2: Contribution-shuffle. Randomly permute contribution vectors within folio."""
    shuffled = [dict(t) for t in tokens]
    for tok in shuffled:
        contribs = list(tok['contributions'])
        rng.shuffle(contribs)
        tok['contributions'] = contribs
    return shuffled


def null_n3_line_shuffle(tokens, rng):
    """N3: Line-shuffle. Randomly permute line order within folio."""
    # Group tokens by line
    lines = defaultdict(list)
    line_order = []
    for tok in tokens:
        ln = tok['line']
        if ln not in lines:
            line_order.append(ln)
        lines[ln].append(tok)

    # Shuffle line order
    shuffled_order = list(line_order)
    rng.shuffle(shuffled_order)

    # Rebuild token list with shuffled line assignment
    result = []
    for new_line, orig_line in zip(line_order, shuffled_order):
        for tok in lines[orig_line]:
            nt = dict(tok)
            nt['line'] = new_line  # assign to the new position
            result.append(nt)

    return result


def null_n4_middle_shuffle(tokens, rng):
    """N4: MIDDLE-shuffle. Randomly replace each token's contributions
    with a random token's contributions from same folio."""
    n = len(tokens)
    if n == 0:
        return tokens

    shuffled = [dict(t) for t in tokens]
    for i in range(n):
        j = rng.randint(0, n - 1)
        shuffled[i]['contributions'] = list(tokens[j]['contributions'])
        shuffled[i]['cts'] = tokens[j].get('cts', 0.0)

    return shuffled


# ---------------------------------------------------------------------------
# Build sensitivity-scaled apparatus for B1/B2
# ---------------------------------------------------------------------------
def build_sensitivity_scaled_apparatus(profile_name, config_mode, scale):
    """Build apparatus with sensitivity scaled by given factor."""
    app = build_configured_apparatus(profile_name, config_mode)
    for sv in STATE_VARS:
        app.sensitivity[sv] *= scale
    return app


# ---------------------------------------------------------------------------
# Build decay-scaled apparatus for B3/B4
# ---------------------------------------------------------------------------
def build_decay_scaled_apparatus(profile_name, config_mode, scale):
    """Build apparatus with decay rates scaled by given factor."""
    app = build_configured_apparatus(profile_name, config_mode)
    for sv in STATE_VARS:
        app.decay_rates[sv] *= scale
    return app


# ---------------------------------------------------------------------------
# Build zero-cross-coupling apparatus for B5
# ---------------------------------------------------------------------------
def build_zero_cc_apparatus(profile_name, config_mode):
    """Build apparatus with all cross-coupling zeroed out."""
    app = build_configured_apparatus(profile_name, config_mode)
    for key in list(app.profile_params.keys()):
        if key.startswith('alpha_'):
            app.profile_params[key] = 0.0
    # Recompute equilibrium bias with zero CC
    equil_state = [EQUILIBRIUM] * N_VARS
    app.equil_bias = {}
    for phase in ['SPEC', 'WORK', 'CLOSE']:
        cc_eq = app._cross_coupling(equil_state, phase)
        app.equil_bias[phase] = list(cc_eq)
    return app


# ---------------------------------------------------------------------------
# UniformRestoringApparatus for B9 (copied from 567 T3)
# ---------------------------------------------------------------------------
class UniformRestoringApparatus:
    """Wraps CloseRecoveryApparatus but replaces the 4-zone piecewise
    restoring force with uniform corridor-level restoring everywhere.
    CLOSE recovery channels (R1-R5) remain intact."""

    def __init__(self, base_apparatus):
        self.base = base_apparatus
        self.sensitivity = base_apparatus.sensitivity
        self.profile_name = base_apparatus.profile_name
        self.config_mode = base_apparatus.config_mode

    def _uniform_restoring_force(self, state, packet_phase='WORK'):
        rf = [0.0] * N_VARS
        zones = ['CORRIDOR'] * N_VARS

        for i, sv in enumerate(STATE_VARS):
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)
            sign_dev = 1.0 if dev >= 0 else -1.0

            corridor_mult_extra = 1.0
            if packet_phase == 'CLOSE':
                if sv == 'C':
                    corridor_mult_extra = self.base.config['close_corridor_C_mult']
                elif sv == 'S':
                    corridor_mult_extra = self.base.config['close_corridor_S_mult']

            rf[i] = (GAMMA_CORRIDOR[sv] * dev
                     * CORRIDOR_MULT[packet_phase][sv]
                     * corridor_mult_extra)

            if abs_dev > 1e-10:
                max_rf = 0.8 * abs_dev * sign_dev
                if abs(rf[i]) > abs(max_rf):
                    rf[i] = max_rf

        return rf, zones

    def update(self, state, dV, packet_phase='WORK', cts=0.0, permissivity=None):
        cc_raw = self.base._cross_coupling(state, packet_phase)
        bias = self.base.equil_bias[packet_phase]
        cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]

        rf, zones = self._uniform_restoring_force(state, packet_phase)

        discharge, events = self.base._discharge_events(state, packet_phase, cts)

        new_state = []
        for i in range(N_VARS):
            v = state[i] + dV[i] + cc[i] - rf[i] + discharge[i]
            new_state.append(max(0.0, min(1.0, v)))

        dv_mag = sum(abs(v) for v in dV)
        recovery, recovery_details = self.base._apply_close_recovery(
            new_state, packet_phase, cts, dv_mag)

        for i in range(N_VARS):
            new_state[i] = max(0.0, min(1.0, new_state[i] + recovery[i]))

        diagnostics = {
            'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
            'discharge_events': events,
            'close_recovery': recovery_details,
        }

        return new_state, diagnostics


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T2: Controlled Excursion Null/Ablation Executor")
    print("Phase 568 - CONTROLLED_EXCURSION_METRICS")
    print("=" * 70)

    # --- Load inputs ---
    print("\nLoading inputs...")

    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"  T2b tokens: {len(all_tokens)}")

    with open(PACKETS_PATH, 'r', encoding='utf-8') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    with open(CTS_PATH, 'r', encoding='utf-8') as f:
        cts_data = json.load(f)
    line_cts_raw = cts_data['line_cts']
    line_cts_map = {k: v['cts'] for k, v in line_cts_raw.items()}
    print(f"  Line CTS entries: {len(line_cts_map)}")

    with open(COF_NORMS_PATH, 'r', encoding='utf-8') as f:
        cof_audit_data = json.load(f)
    cof_norms = cof_audit_data['A6_cof_prototype_family']['section_p90_normalization']
    print(f"  COF normalization sections: {list(cof_norms.keys())}")

    # Build per-line COF component lookup
    line_components = {}
    line_section_map = {}
    for k, lp in line_packets.items():
        ps = lp.get('packet_state', {})
        prof = lp.get('profile', [])
        line_components[k] = {
            'q4_shift_strength': ps.get('q4_shift_strength', 0.0),
            'close_opacity_bias': ps.get('close_opacity_bias', 0.0),
            'm_close_bias': ps.get('m_close_bias', 0.0),
            'q4_opaque_rate': prof[14] if len(prof) > 14 else 0.0,
        }
        line_section_map[k] = lp.get('section', 'B')

    print(f"  Line components built: {len(line_components)}")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    print(f"  Unique folios in T2b: {len(tokens_by_folio)}")

    # --- Determine pilot folio list ---
    pilot_folio_list = sorted(PILOT_FOLIOS)
    print(f"\nPilot folios: {len(pilot_folio_list)}")

    # --- Determine preferred profile and config mode ---
    folio_infra = compute_infra_scores(PILOT_FOLIOS)
    for folio in pilot_folio_list:
        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        n_toks = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: profile={profile}, config={config_mode}, n_tokens={n_toks}")

    # =====================================================================
    # REFERENCE RUNS (full model, 20 folios)
    # =====================================================================
    print("\n" + "=" * 70)
    print("REFERENCE RUNS (full model, 20 folios)")
    print("=" * 70)

    reference = {}
    run_count = 0

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            print(f"  WARNING: {folio} has no tokens, skipping")
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        apparatus = build_configured_apparatus(profile, config_mode)

        result = run_controlled_excursion_trace(
            apparatus, toks, line_packets,
            cof_norms, line_cts_map, line_components, line_section_map)
        reference[folio] = result
        run_count += 1

        print(f"  {folio}: WCU={result['WCU']:.4f}, SLR={result['SLR_mean']:.4f}, "
              f"UEB={result['UEB']:.1f}, CCY={result['CCY']:.4f}, "
              f"WCP={result['WCP']:.4f}, EWP={result['EWP']:.1f}, "
              f"PCV={result['PCV']:.4f}")

    # =====================================================================
    # BASELINES (10 types x 20 folios = 200 runs)
    # =====================================================================
    print("\n" + "=" * 70)
    print("BASELINES (10 types x 20 folios = 200 runs)")
    print("=" * 70)

    baseline_runs = {f'B{i}': [] for i in range(1, 11)}

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

        trace_kwargs = dict(
            line_packets=line_packets,
            cof_norms=cof_norms,
            line_cts_map=line_cts_map,
            line_components=line_components,
            line_section_map=line_section_map,
        )

        # --- B1: sensitivity x 0.5 ---
        apparatus = build_sensitivity_scaled_apparatus(profile, config_mode, 0.5)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B1'].append(r)
        run_count += 1

        # --- B2: sensitivity x 0 (no apparatus) ---
        apparatus = build_sensitivity_scaled_apparatus(profile, config_mode, 0.0)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B2'].append(r)
        run_count += 1

        # --- B3: decay x 0.5 ---
        apparatus = build_decay_scaled_apparatus(profile, config_mode, 0.5)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B3'].append(r)
        run_count += 1

        # --- B4: decay x 2.0 ---
        apparatus = build_decay_scaled_apparatus(profile, config_mode, 2.0)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B4'].append(r)
        run_count += 1

        # --- B5: cross-coupling x 0 ---
        apparatus = build_zero_cc_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B5'].append(r)
        run_count += 1

        # --- B6: SPEC phase only ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks, force_phase='SPEC',
                                            **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B6'].append(r)
        run_count += 1

        # --- B7: WORK phase only ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks, force_phase='WORK',
                                            **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B7'].append(r)
        run_count += 1

        # --- B8: CLOSE phase only ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks, force_phase='CLOSE',
                                            **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B8'].append(r)
        run_count += 1

        # --- B9: No discharge events ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks,
                                            disable_discharge=True,
                                            **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B9'].append(r)
        run_count += 1

        # --- B10: No CLOSE recovery (enable_close_recovery=False) ---
        apparatus = build_no_close_recovery_apparatus(profile, config_mode)
        r = run_controlled_excursion_trace(apparatus, toks, **trace_kwargs)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B10'].append(r)
        run_count += 1

        elapsed = time.time() - t0
        print(f"  Baselines {folio} done ({run_count} runs, {elapsed:.1f}s)")

    # Print baseline summary
    print("\n  Baseline summary:")
    for bname in sorted(baseline_runs.keys(), key=lambda x: int(x[1:])):
        bdata = baseline_runs[bname]
        if bdata:
            wcu_vals = [r['WCU'] for r in bdata]
            pcv_vals = [r['PCV'] for r in bdata]
            mean_wcu = sum(wcu_vals) / len(wcu_vals)
            mean_pcv = sum(pcv_vals) / len(pcv_vals)
            print(f"    {bname}: mean_WCU={mean_wcu:.4f}, mean_PCV={mean_pcv:.4f}, "
                  f"n_folios={len(bdata)}")

    # =====================================================================
    # NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)
    # =====================================================================
    print("\n" + "=" * 70)
    print("NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)")
    print("=" * 70)

    N_PERMS = 50
    null_runs = {
        'N1': {},
        'N2': {},
        'N3': {},
        'N4': {},
    }

    # Metric keys to accumulate for nulls
    NULL_METRIC_KEYS = [
        'old_viability', 'old_y_final',
        'PCV', 'SAHB', 'REF_mean', 'REF_eligible_fraction',
        'QGY', 'qgy_ratio',
        'WCU', 'SLR_mean', 'SLR_eligible_fraction',
        'UEB', 'CCY', 'CCY_ratio', 'CCY_cof1', 'CCY_cof2', 'CCY_cof3',
        'WCP', 'WCP_full_packet_mean', 'EWP',
    ]

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

        trace_kwargs = dict(
            cof_norms=cof_norms,
            line_cts_map=line_cts_map,
            line_components=line_components,
            line_section_map=line_section_map,
        )

        # Initialize null result containers
        for null_name in null_runs:
            null_runs[null_name][folio] = {mk: [] for mk in NULL_METRIC_KEYS}

        for perm_idx in range(N_PERMS):
            # --- N1: Phase-shuffle ---
            rng1 = random.Random(42 + perm_idx)
            n1_toks, n1_lp = null_n1_phase_shuffle(toks, line_packets, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_controlled_excursion_trace(
                apparatus, n1_toks, line_packets=n1_lp, **trace_kwargs)
            for mk in NULL_METRIC_KEYS:
                null_runs['N1'][folio][mk].append(r1[mk])
            run_count += 1

            # --- N2: Contribution-shuffle ---
            rng2 = random.Random(42 + perm_idx)
            n2_toks = null_n2_contribution_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_controlled_excursion_trace(
                apparatus, n2_toks, line_packets=line_packets, **trace_kwargs)
            for mk in NULL_METRIC_KEYS:
                null_runs['N2'][folio][mk].append(r2[mk])
            run_count += 1

            # --- N3: Line-shuffle ---
            rng3 = random.Random(42 + perm_idx)
            n3_toks = null_n3_line_shuffle(toks, rng3)
            apparatus = build_configured_apparatus(profile, config_mode)
            r3 = run_controlled_excursion_trace(
                apparatus, n3_toks, line_packets=line_packets, **trace_kwargs)
            for mk in NULL_METRIC_KEYS:
                null_runs['N3'][folio][mk].append(r3[mk])
            run_count += 1

            # --- N4: MIDDLE-shuffle ---
            rng4 = random.Random(42 + perm_idx)
            n4_toks = null_n4_middle_shuffle(toks, rng4)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_controlled_excursion_trace(
                apparatus, n4_toks, line_packets=line_packets, **trace_kwargs)
            for mk in NULL_METRIC_KEYS:
                null_runs['N4'][folio][mk].append(r4[mk])
            run_count += 1

            if run_count % 100 == 0:
                elapsed = time.time() - t0
                print(f"  Progress: {run_count} runs, {elapsed:.1f}s "
                      f"(folio={folio}, perm={perm_idx+1}/{N_PERMS})")

        elapsed = time.time() - t0
        print(f"  N1-N4 {folio} done ({run_count} total runs, {elapsed:.1f}s)")

    # Compute null summaries (mean across permutations)
    null_output = {}
    for null_name in null_runs:
        null_output[null_name] = {}
        for folio in null_runs[null_name]:
            entry = null_runs[null_name][folio]
            n_p = len(entry.get('old_viability', []))
            if n_p == 0:
                continue

            summary = {'n_perms': n_p}
            for mk in NULL_METRIC_KEYS:
                vals = entry[mk]
                mean_val = sum(vals) / n_p
                summary[f'mean_{mk}'] = round(mean_val, 6)

                # Also compute std for key metrics
                if mk in ('WCU', 'PCV', 'old_viability', 'SLR_mean', 'CCY', 'WCP', 'EWP', 'UEB'):
                    std_val = math.sqrt(
                        sum((v - mean_val) ** 2 for v in vals) / n_p)
                    summary[f'std_{mk}'] = round(std_val, 6)

            null_output[null_name][folio] = summary

    # Print null summary
    print("\n  Null summary:")
    for null_name in sorted(null_output.keys()):
        folio_data = null_output[null_name]
        if not folio_data:
            continue
        wcu_means = [folio_data[f]['mean_WCU']
                     for f in folio_data if 'mean_WCU' in folio_data[f]]
        pcv_means = [folio_data[f]['mean_PCV']
                     for f in folio_data if 'mean_PCV' in folio_data[f]]
        if wcu_means:
            overall_mean_wcu = sum(wcu_means) / len(wcu_means)
            overall_mean_pcv = sum(pcv_means) / len(pcv_means) if pcv_means else 0.0
            print(f"    {null_name}: mean_WCU={overall_mean_wcu:.4f}, "
                  f"mean_PCV={overall_mean_pcv:.4f}, n_folios={len(wcu_means)}")

    # === Assemble output ===
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': 568,
            'script': 't2_controlled_excursion_null_executor.py',
            'total_runs': run_count,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_baselines': sum(len(v) for v in baseline_runs.values()),
            'n_nulls': N_PERMS * len(null_runs) * len(pilot_folio_list),
            'n_perms': N_PERMS,
            'n_pilot_folios': len(pilot_folio_list),
            'elapsed_seconds': round(elapsed, 2),
            'metrics': NULL_METRIC_KEYS,
            'baseline_descriptions': {
                'B1': 'sensitivity x 0.5',
                'B2': 'sensitivity x 0 (no apparatus)',
                'B3': 'decay x 0.5',
                'B4': 'decay x 2.0',
                'B5': 'cross-coupling x 0',
                'B6': 'SPEC phase only',
                'B7': 'WORK phase only',
                'B8': 'CLOSE phase only',
                'B9': 'No discharge events',
                'B10': 'No CLOSE recovery',
            },
            'null_descriptions': {
                'N1': 'Phase-shuffle (permute packet_phase labels within folio)',
                'N2': 'Contribution-shuffle (permute SV contribution vectors)',
                'N3': 'Line-shuffle (permute line order within folio)',
                'N4': 'MIDDLE-shuffle (random token contributions from same folio)',
            },
            'preferred_profiles': {
                f: get_preferred_profile(f) for f in pilot_folio_list
            },
        },
        'reference': reference,
        'baseline_runs': baseline_runs,
        'null_runs': null_output,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Size: {file_size_mb:.1f} MB")

    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")

    # Build per-folio baseline lookup for comparison
    baseline_by_folio = {f'B{i}': {} for i in range(1, 11)}
    for bname, blist in baseline_runs.items():
        for entry in blist:
            baseline_by_folio[bname][entry['folio']] = entry

    bnames = [f'B{i}' for i in range(1, 11)]
    nnames = ['N1', 'N2', 'N3', 'N4']

    # --- WCU table ---
    print(f"\n  WCU (Work Corridor Utilization):")
    header_b = ' '.join(f'{b:>7}' for b in bnames)
    header_n = ' '.join(f'{n:>7}' for n in nnames)
    print(f"  {'Folio':<8} {'Ref':>7} | {header_b} | {header_n}")
    divider_b = ' '.join('-' * 7 for _ in bnames)
    divider_n = ' '.join('-' * 7 for _ in nnames)
    print(f"  {'-' * 8} {'-' * 7} | {divider_b} | {divider_n}")

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['WCU']
        b_vals = []
        for bn in bnames:
            entry = baseline_by_folio[bn].get(folio, {})
            v = entry.get('WCU', 0.0) if entry else 0.0
            b_vals.append(f"{v:>7.4f}")
        n_vals = []
        for nn in nnames:
            v = null_output[nn].get(folio, {}).get('mean_WCU', 0.0)
            n_vals.append(f"{v:>7.4f}")
        print(f"  {folio:<8} {ref_v:>7.4f} | {' '.join(b_vals)} | "
              f"{' '.join(n_vals)}")

    # --- PCV table ---
    print(f"\n  PCV (Packet-Coherence Viability):")
    print(f"  {'Folio':<8} {'Ref':>7} | {header_b} | {header_n}")
    print(f"  {'-' * 8} {'-' * 7} | {divider_b} | {divider_n}")

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['PCV']
        b_vals = []
        for bn in bnames:
            entry = baseline_by_folio[bn].get(folio, {})
            v = entry.get('PCV', 0.0) if entry else 0.0
            b_vals.append(f"{v:>7.4f}")
        n_vals = []
        for nn in nnames:
            v = null_output[nn].get(folio, {}).get('mean_PCV', 0.0)
            n_vals.append(f"{v:>7.4f}")
        print(f"  {folio:<8} {ref_v:>7.4f} | {' '.join(b_vals)} | "
              f"{' '.join(n_vals)}")

    # --- New metrics: Reference vs Null ---
    print(f"\n  New Metrics: Reference vs Null Means:")
    new_metrics = ['WCU', 'SLR_mean', 'UEB', 'CCY', 'WCP', 'EWP',
                   'PCV', 'SAHB', 'REF_mean', 'QGY']
    for mk in new_metrics:
        ref_vals = [reference[f][mk] for f in pilot_folio_list if f in reference]
        if not ref_vals:
            continue
        ref_mean = sum(ref_vals) / len(ref_vals)
        null_means = {}
        for nn in nnames:
            nm_key = f'mean_{mk}'
            vals = [null_output[nn].get(f, {}).get(nm_key, 0.0)
                    for f in pilot_folio_list if f in reference]
            null_means[nn] = sum(vals) / len(vals) if vals else 0.0

        n_strs = ' '.join(f'{nn}={null_means[nn]:>8.4f}' for nn in nnames)
        print(f"    {mk:<22} ref={ref_mean:>8.4f}  {n_strs}")

    # --- B10 Delta Analysis (CLOSE recovery ablation) ---
    print(f"\n  B10 Deltas (Reference - B10, CLOSE recovery ablation):")
    b10_metrics = ['WCU', 'SLR_mean', 'UEB', 'CCY', 'WCP', 'EWP', 'PCV']
    print(f"  {'Folio':<8}", end='')
    for mk in b10_metrics:
        print(f" {'d'+mk:>8}", end='')
    print()
    print(f"  {'-' * 8}", end='')
    for _ in b10_metrics:
        print(f" {'-' * 8}", end='')
    print()

    b10_deltas = {mk: [] for mk in b10_metrics}
    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref = reference[folio]
        b10 = baseline_by_folio['B10'].get(folio, {})
        if not b10:
            continue
        print(f"  {folio:<8}", end='')
        for mk in b10_metrics:
            d = ref.get(mk, 0.0) - b10.get(mk, 0.0)
            b10_deltas[mk].append(d)
            # For UEB and EWP, lower is better, so invert sign
            if mk in ('UEB', 'EWP'):
                print(f" {-d:>+8.4f}", end='')
            else:
                print(f" {d:>+8.4f}", end='')
        print()

    if b10_deltas.get('WCU'):
        print(f"  {'MEAN':<8}", end='')
        for mk in b10_metrics:
            vals = b10_deltas[mk]
            mean_d = sum(vals) / len(vals)
            if mk in ('UEB', 'EWP'):
                mean_d = -mean_d
            print(f" {mean_d:>+8.4f}", end='')
        print()

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
