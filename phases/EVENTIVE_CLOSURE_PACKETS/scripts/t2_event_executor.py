"""
T2: Event Executor — Full Model with Per-Event Success Metrics
Phase 569 - EVENTIVE_CLOSURE_PACKETS

Runs the full model (20 pilot folios x 3 profiles + config ablation = 90 runs)
with event detection and per-event success measurement using the four-metric
stack (EIR, ERM, ESQ, EW) from shared_metrics.

ALL metric computation uses shared_metrics.py (no custom reimplementation).
Loads T1 event map to know which CLOSE lines are events of which types.
At each CLOSE line boundary: records line_start_state, close_start_state,
line_end_state. Tracks same-line max process deviation for Axis B demand
classification. Computes per-event success metrics via shared_metrics.
Aggregates per-folio by event type, by demand qualifier, and by
type+demand combination.

90 runs:
  60 primary: 20 pilot folios x 3 profiles
  30 config ablation: 10 folios x 3 config modes
"""

import json
import sys
import os
import time
import math
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Imports from shared_metrics (single source of truth)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import (
    STATE_VARS, N_VARS, EQUILIBRIUM, SV_INDEX, S_IDX, Y_IDX,
    HAZARD_BOUNDARIES, Q1, Q2_BASE, HAZARD_DEV, PROCESS_SVS, PROCESS_IDX,
    PCV_ZONE_SCORES, PCV_S_HIGH_SCORES, PCV_PROCESS_SVS,
    SAHB_WARNING_WEIGHT, SAHB_HARDSTOP_WEIGHT,
    SAHB_OUTSIDE_CORRIDOR_WEIGHT, SAHB_MAX_EXCURSION_WEIGHT,
    WCU_ZONE_SCORES, WCU_S_HIGH_SCORE, EIR_EPSILON,
    classify_zone, is_in_bounds,
    pcv_token_score, sahb_token, wcu_token, wcp_token_quality,
    compute_wcp_line, compute_slr_line, compute_aggregate_dev,
    compute_event_success, classify_closure_demand,
    compute_ueb, compute_ewp, compute_ref, compute_sahb,
    DEFAULT_GLOBAL_THRESHOLDS,
)

from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    build_close_recovery_apparatus, build_configured_apparatus,
    build_no_close_recovery_apparatus,
    assign_folio_profiles, compute_infra_scores,
    PILOT_FOLIOS as APPARATUS_PILOT_FOLIOS, PROFILES,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]

ALL_PROFILES = ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']

ABLATION_FOLIOS = PILOT_FOLIOS[:10]

CONFIG_ABLATION_MODES = ['no_close_recovery', 'no_hazard_routing', 'no_zone_correction']

# Routing permissivity buffer (same as 568 T1)
ROUTING_PERMISSIVITY = {
    'r': {'X': +0.03, 'S': -0.02, 'C': -0.02},
    'y': {'T': +0.03, 'X': -0.02},
    'h': {'TR': +0.03, 'RC': +0.02, 'X': -0.02, 'T': -0.02},
    'm': {'C': +0.03, 'T': -0.02, 'X': -0.02},
    'n': {'S': +0.02, 'X': -0.01},
    'l': {'TR': +0.02, 'S': +0.02, 'X': -0.01},
}
ROUTING_DECAY = 0.7


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data():
    """Load all data sources."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
    phases_dir = os.path.join(base, 'phases')

    print("  Loading line packets...")
    lp_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')
    with open(lp_path, 'r', encoding='utf-8') as f:
        lp_raw = json.load(f)
    line_packets = lp_raw['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    print("  Loading CTS data...")
    cts_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path, 'r', encoding='utf-8') as f:
        cts_raw = json.load(f)
    # Build CTS lookup: "folio|line" -> cts float
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

    print("  Loading supervisory tokens...")
    sup_path = os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                            'results', 't2b_supervisory_interface_unrouted.json')
    with open(sup_path, 'r', encoding='utf-8') as f:
        sup_raw = json.load(f)
    all_tokens = sup_raw['token_signals']
    print(f"    Total tokens: {len(all_tokens)}")

    print("  Loading folio budgets...")
    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    with open(budget_path, 'r', encoding='utf-8') as f:
        budgets = json.load(f)

    print("  Loading T1 event taxonomy...")
    event_path = os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                              'results', 't1_event_taxonomy.json')
    with open(event_path, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']
    section_thresholds = event_taxonomy['section_thresholds']
    print(f"    Event map entries: {len(event_map)}")

    # Determine regime and budget paths for assign_folio_profiles
    regime_path = os.path.join(base, 'data', 'regime_folio_mapping.json')

    return (line_packets, cts_data, all_tokens, budgets, budget_path,
            event_map, section_thresholds, regime_path)


# ---------------------------------------------------------------------------
# Token sorting
# ---------------------------------------------------------------------------
def sort_key(tok):
    """Sort tokens by (line_number, line_position)."""
    try:
        ln = int(tok['line'])
    except (ValueError, TypeError):
        ln = 99999
    lp = tok.get('line_pos', 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------
def run_event_trace(apparatus, tokens, line_packets, cts_data, event_map):
    """
    Run one folio through the CloseRecoveryApparatus with event detection.

    Returns dict with:
      - metrics: folio-level metric dict
      - events_by_type: {etype: {count, EIR, mean_ERM, ...}}
      - events_by_demand: {dq: {count, EIR, ...}}
      - events_by_type_demand: {combo: {count, EIR, ...}}
      - per_event_detail: list of per-event dicts
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return _empty_folio_result()

    state = [EQUILIBRIUM] * N_VARS
    permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
    prev_line = None

    # ---- Old metric accumulators ----
    n_viable = 0

    # ---- PCV accumulators ----
    pcv_score_sum = 0.0
    pcv_pair_count = 0

    # ---- SAHB accumulators ----
    sahb_warnings = 0
    sahb_hardstops = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # ---- REF tracking ----
    line_work_end_devs = {}   # line_key -> [dev per SV]
    line_close_end_devs = {}  # line_key -> [dev per SV]

    # ---- QGY accumulators ----
    qgy_total = 0.0
    prev_aggregate_dev = None

    # ---- WCU accumulators ----
    wcu_score_sum = 0.0
    wcu_pair_count = 0

    # ---- SLR per-line tracking ----
    slr_values = []

    # ---- UEB accumulators ----
    ueb_close_warnings = 0
    ueb_close_hardstops = 0
    ueb_unresolved_fractions = []
    ueb_line_final_hardstop = 0
    ueb_post_line_residual_above_q2 = 0

    # ---- CCY accumulators ----
    ccy_qualifying_y = 0.0
    # Cross-line WORK peak tracking
    last_work_peak_dev = 0.0
    last_work_peak_svs_above_q2 = 0

    # ---- WCP per-line tracking ----
    wcp_line_scores = []

    # ---- EWP accumulators ----
    ewp_prolonged_hardstop = 0
    ewp_unresolved_warning = 0
    ewp_post_close_residuals = []
    ewp_edge_persistence_numer = 0
    ewp_edge_persistence_denom = 0

    # ---- Event tracking ----
    per_event_details = []
    events_by_type = defaultdict(list)
    events_by_demand = defaultdict(list)
    events_by_type_demand = defaultdict(list)

    # ---- Per-line state tracking ----
    current_line_key = None
    current_line_phase = None
    current_line_section = 'B'

    # Per-line accumulators (reset on line boundary)
    line_start_state = None
    close_start_state = None
    same_line_max_dev = 0.0  # max agg dev during non-CLOSE portion
    line_work_end_state = None
    line_close_end_state = None
    line_work_peak_dev = 0.0
    line_work_peak_svs_above_q2 = 0
    line_work_end_dev_mean = 0.0  # mean |dev| across process SVs at work end

    # WCP per-line phase score lists
    line_spec_scores = []
    line_work_scores = []
    line_close_scores = []
    line_has_spec = False
    line_has_work = False
    line_has_close = False

    # SLR per-line
    line_work_q2_exceeded = set()
    line_close_q2_returned = set()
    line_work_corridor_tokens = 0
    line_work_total_tokens = 0

    # EWP per-line
    consecutive_work_hardstops = 0
    line_close_warning_svs = set()
    line_close_end_warning_svs = set()

    # UEB per-line
    line_close_tokens_count = 0

    # CTS for this line
    line_cts = 0.0

    # Prev line work peak dev (for cross-line event demand)
    prev_line_work_peak_dev = None

    def _finalize_line():
        """Finalize metrics for the departing line. Called on line transitions."""
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_unresolved_warning
        nonlocal last_work_peak_dev, last_work_peak_svs_above_q2
        nonlocal prev_line_work_peak_dev

        if current_line_key is None:
            return

        # Save REF data
        if line_work_end_state is not None:
            line_work_end_devs[current_line_key] = [
                abs(line_work_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS)
            ]
        if line_close_end_state is not None:
            line_close_end_devs[current_line_key] = [
                abs(line_close_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS)
            ]

        # UEB: line_final_hardstop (any SV at HARD_STOP/HAZARD at line end)
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            zone = classify_zone(sv, dev)
            if zone in ('HARD_STOP', 'HAZARD'):
                ueb_line_final_hardstop += 1
                break

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
        if line_work_end_state is not None and line_close_end_state is not None:
            work_devs = [abs(line_work_end_state[i] - EQUILIBRIUM)
                         for i in range(N_VARS) if i != Y_IDX]
            close_devs = [abs(line_close_end_state[i] - EQUILIBRIUM)
                          for i in range(N_VARS) if i != Y_IDX]
            n_unresolved = sum(1 for w, c in zip(work_devs, close_devs)
                               if c >= w and w > Q1)
            n_eligible = sum(1 for w in work_devs if w > Q1)
            if n_eligible > 0:
                ueb_unresolved_fractions.append(n_unresolved / n_eligible)

        # SLR: compute per-line value
        if line_work_end_state is not None:
            work_end_dev = sum(
                abs(line_work_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS) if i != Y_IDX
            ) / (N_VARS - 1)

            if work_end_dev > Q1:
                close_end_dev = work_end_dev  # default if no CLOSE
                if line_close_end_state is not None:
                    close_end_dev = sum(
                        abs(line_close_end_state[i] - EQUILIBRIUM)
                        for i in range(N_VARS) if i != Y_IDX
                    ) / (N_VARS - 1)

                n_exc = len(line_work_q2_exceeded)
                n_ret = len(line_work_q2_exceeded & line_close_q2_returned)
                corridor_return = n_ret / n_exc if n_exc > 0 else 0.0

                work_quality = (line_work_corridor_tokens / line_work_total_tokens
                                if line_work_total_tokens > 0 else 0.0)

                slr_val = compute_slr_line(work_end_dev, close_end_dev,
                                           corridor_return, work_quality)
                if slr_val is not None:
                    slr_values.append(slr_val)

        # WCP: compute per-line score
        wcp_val, _ = compute_wcp_line(
            line_spec_scores, line_work_scores, line_close_scores,
            line_has_spec, line_has_work, line_has_close)
        if wcp_val is not None:
            wcp_line_scores.append(wcp_val)

        # EWP: unresolved_warning (CLOSE warnings not resolved by line end)
        unresolved = line_close_warning_svs & line_close_end_warning_svs
        ewp_unresolved_warning += len(unresolved)

        # EWP: post_close_residual
        if line_close_end_state is not None and line_close_tokens_count > 0:
            residuals = []
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and line_close_end_state[i] > EQUILIBRIUM:
                    continue
                dev = abs(line_close_end_state[i] - EQUILIBRIUM)
                residuals.append(max(dev - Q1, 0.0))
            if residuals:
                ewp_post_close_residuals.append(sum(residuals) / len(residuals))

        # Cross-line WORK peak tracking for CCY
        if current_line_phase == 'WORK':
            last_work_peak_dev = line_work_peak_dev
            last_work_peak_svs_above_q2 = line_work_peak_svs_above_q2
            prev_line_work_peak_dev = line_work_peak_dev

        # --- EVENT DETECTION ---
        # Check if this line is a CLOSE line in the event_map
        if current_line_phase == 'CLOSE' and current_line_key in event_map:
            event_info = event_map[current_line_key]

            # Compute Axis B demand qualifiers
            cs_state = close_start_state if close_start_state is not None else line_start_state
            demand_quals = classify_closure_demand(
                close_start_state=cs_state,
                same_line_max_dev=same_line_max_dev,
                has_work_predecessor=event_info['has_work_predecessor'],
                work_peak_dev=prev_line_work_peak_dev if event_info['has_work_predecessor'] else None
            )

            # Compute event success metrics
            ls_state = line_start_state if line_start_state is not None else [EQUILIBRIUM] * N_VARS
            wpd = prev_line_work_peak_dev if event_info['has_work_predecessor'] else None
            success = compute_event_success(
                line_start_state=ls_state,
                line_end_state=list(state),
                close_start_state=cs_state if cs_state is not None else ls_state,
                work_peak_dev=wpd
            )

            # Record per-event detail
            event_detail = {
                'line_key': current_line_key,
                'packet_types_global': sorted(event_info['packet_types_global']),
                'packet_types_section': sorted(event_info['packet_types_section']),
                'demand_qualifiers': sorted(demand_quals),
                **success
            }
            per_event_details.append(event_detail)

            # Aggregate by event type (global regime)
            for etype in event_info['packet_types_global']:
                events_by_type[etype].append(success)

            # Aggregate by demand qualifier
            for dq in demand_quals:
                events_by_demand[dq].append(success)

            # Aggregate by type+demand combination
            for etype in event_info['packet_types_global']:
                for dq in demand_quals:
                    combo = f"{etype}__{dq}"
                    events_by_type_demand[combo].append(success)

        # Update cross-line tracking for next CLOSE line
        if current_line_phase != 'WORK':
            # Only reset prev_line_work_peak_dev if we're leaving a non-WORK line
            # (CLOSE lines consume the previous WORK peak but don't reset it)
            pass

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

            # Determine phase for this line
            if line_key in line_packets:
                lp = line_packets[line_key]
                current_line_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
                current_line_section = lp.get('section', 'B')
            else:
                current_line_phase = 'WORK'
                current_line_section = 'B'

            # Get CTS for this line
            line_cts = cts_data.get(line_key, 0.0)

            # Reset per-line state
            line_start_state = list(state)
            close_start_state = None
            same_line_max_dev = 0.0
            line_work_end_state = None
            line_close_end_state = None
            line_work_peak_dev = 0.0
            line_work_peak_svs_above_q2 = 0
            line_work_end_dev_mean = 0.0

            # WCP per-line reset
            line_spec_scores = []
            line_work_scores = []
            line_close_scores = []
            line_has_spec = False
            line_has_work = False
            line_has_close = False

            # SLR per-line reset
            line_work_q2_exceeded = set()
            line_close_q2_returned = set()
            line_work_corridor_tokens = 0
            line_work_total_tokens = 0

            # EWP per-line reset
            consecutive_work_hardstops = 0
            line_close_warning_svs = set()
            line_close_end_warning_svs = set()

            # UEB
            line_close_tokens_count = 0

        # ---- Routing ----
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_PERMISSIVITY:
                for sv, shift in ROUTING_PERMISSIVITY[rt].items():
                    permissivity_buffer[sv] += shift

        # ---- Packet phase from line_packets (override token-level) ----
        packet_phase = current_line_phase

        # ---- CTS: use line-level, fallback to token-level ----
        cts = line_cts if line_cts > 0 else tok.get('cts', 0.0)

        # ---- Pre-step state ----
        pre_state = list(state)
        pre_y = state[Y_IDX]

        # ---- Compute dV ----
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            dV[i] = contributions[i] * apparatus.sensitivity[sv]

        # ---- Apparatus update ----
        perm_dict = {sv: v for sv, v in permissivity_buffer.items() if abs(v) > 1e-8}
        state, diagnostics = apparatus.update(
            state, dV, packet_phase, cts,
            permissivity=perm_dict if perm_dict else None
        )

        # ---- Decay permissivity buffer ----
        for sv in STATE_VARS:
            permissivity_buffer[sv] *= ROUTING_DECAY

        # ---- Post-step ----
        y_delta = state[Y_IDX] - pre_y
        current_agg_dev = compute_aggregate_dev(state)

        # ================================================================
        # VIABILITY
        # ================================================================
        if is_in_bounds(state):
            n_viable += 1

        # ================================================================
        # PCV (via shared_metrics)
        # ================================================================
        pcv_s, pcv_c = pcv_token_score(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_pair_count += pcv_c

        # ================================================================
        # SAHB (via shared_metrics)
        # ================================================================
        sw, sh, soc, sme = sahb_token(state, packet_phase)
        sahb_warnings += sw
        sahb_hardstops += sh
        sahb_outside_corridor += soc
        if sme > sahb_max_excursion:
            sahb_max_excursion = sme

        # ================================================================
        # WCU (via shared_metrics)
        # ================================================================
        wcu_s, wcu_p = wcu_token(state, packet_phase)
        wcu_score_sum += wcu_s
        wcu_pair_count += wcu_p

        # ================================================================
        # UEB CLOSE-phase tallies
        # ================================================================
        if packet_phase == 'CLOSE':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    ueb_close_warnings += 1
                elif zone in ('HARD_STOP', 'HAZARD'):
                    ueb_close_hardstops += 1

        # ================================================================
        # QGY
        # ================================================================
        if packet_phase == 'CLOSE':
            if cts > 0.3 and prev_aggregate_dev is not None:
                if current_agg_dev * (N_VARS - 1) < prev_aggregate_dev:
                    if y_delta > 0:
                        qgy_total += y_delta
            prev_aggregate_dev = current_agg_dev * (N_VARS - 1)
        else:
            prev_aggregate_dev = None

        # ================================================================
        # CCY
        # ================================================================
        if packet_phase == 'CLOSE' and y_delta > 0:
            current_mean_dev = current_agg_dev
            ref_work_peak_dev = last_work_peak_dev
            ref_work_peak_svs_above_q2 = last_work_peak_svs_above_q2

            s_above_eq = state[S_IDX] > EQUILIBRIUM

            agg_dev_decreased = (ref_work_peak_dev > 0
                                 and current_mean_dev < ref_work_peak_dev)

            current_svs_above_q2 = sum(
                1 for sv in PROCESS_SVS
                if not (sv == 'S' and s_above_eq)
                and abs(state[SV_INDEX[sv]] - EQUILIBRIUM) > Q2_BASE[sv]
            )

            if ref_work_peak_svs_above_q2 == 0:
                net_corridor_improvement = (current_mean_dev < ref_work_peak_dev
                                            if ref_work_peak_dev > 0 else False)
            else:
                net_corridor_improvement = (
                    current_mean_dev < ref_work_peak_dev
                    and current_svs_above_q2 < ref_work_peak_svs_above_q2
                )

            if agg_dev_decreased and net_corridor_improvement and cts > 0.3:
                ccy_qualifying_y += y_delta

        # ================================================================
        # REF tracking
        # ================================================================
        if packet_phase == 'WORK':
            line_work_end_state = list(state)
        elif packet_phase == 'CLOSE':
            line_close_end_state = list(state)
            line_close_tokens_count += 1

        # ================================================================
        # WCP tracking (via shared_metrics per-token quality)
        # ================================================================
        quality = wcp_token_quality(state, packet_phase)
        if packet_phase == 'SPEC':
            line_spec_scores.append(quality)
            line_has_spec = True
        elif packet_phase == 'WORK':
            line_work_scores.append(quality)
            line_has_work = True
        elif packet_phase == 'CLOSE':
            line_close_scores.append(quality)
            line_has_close = True

        # ================================================================
        # EWP tracking
        # ================================================================
        s_above_eq = state[S_IDX] > EQUILIBRIUM

        if packet_phase == 'WORK':
            any_hardstop = False
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and s_above_eq:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
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
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and s_above_eq:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_warning_svs.add(sv)

            # Update end-of-CLOSE warning state
            line_close_end_warning_svs = set()
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and s_above_eq:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_end_warning_svs.add(sv)

            # Edge persistence per-CLOSE-token
            any_edge = False
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and s_above_eq:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone in ('HARD_STOP', 'HAZARD'):
                    any_edge = True
                    break
            ewp_edge_persistence_denom += 1
            if any_edge:
                ewp_edge_persistence_numer += 1

        # ================================================================
        # Per-line WORK peak tracking (SLR + CCY)
        # ================================================================
        if packet_phase == 'WORK':
            line_work_total_tokens += 1
            work_dev = current_agg_dev
            if work_dev > line_work_peak_dev:
                line_work_peak_dev = work_dev
                line_work_peak_svs_above_q2 = sum(
                    1 for sv in PROCESS_SVS
                    if abs(state[SV_INDEX[sv]] - EQUILIBRIUM) >= Q2_BASE[sv]
                    and not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
                )

            # SLR: Q2 excursion tracking
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev >= Q2_BASE[sv]:
                    line_work_q2_exceeded.add(sv)

            # SLR: work quality (tokens where all SVs below Q2)
            all_ok = all(
                abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                for sv in PROCESS_SVS
                if not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
            )
            if all_ok:
                line_work_corridor_tokens += 1

        elif packet_phase == 'CLOSE':
            # SLR: Q2 return tracking
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev < Q2_BASE[sv]:
                    line_close_q2_returned.add(sv)

        # ================================================================
        # Event tracking: same_line_max_dev and close_start_state
        # ================================================================
        if packet_phase != 'CLOSE':
            # Track max aggregate dev during non-CLOSE portion
            if current_agg_dev > same_line_max_dev:
                same_line_max_dev = current_agg_dev

        if packet_phase == 'CLOSE' and close_start_state is None:
            close_start_state = list(state)

    # ---- Finalize last line ----
    if current_line_key is not None:
        _finalize_line()

    # ================================================================
    # Compute final folio-level metrics
    # ================================================================

    # PCV
    pcv = round(pcv_score_sum / pcv_pair_count, 6) if pcv_pair_count > 0 else 1.0

    # SAHB (via shared_metrics, normalized by tokens)
    sahb = compute_sahb(sahb_warnings, sahb_hardstops, sahb_outside_corridor,
                        sahb_max_excursion, n_tokens)

    # WCU
    wcu = round(wcu_score_sum / wcu_pair_count, 6) if wcu_pair_count > 0 else 0.0

    # SLR
    slr_mean = round(sum(slr_values) / len(slr_values), 6) if slr_values else 0.0

    # UEB
    ueb = compute_ueb(ueb_close_warnings, ueb_close_hardstops,
                       ueb_unresolved_fractions,
                       ueb_line_final_hardstop,
                       ueb_post_line_residual_above_q2)

    # WCP
    wcp = round(sum(wcp_line_scores) / len(wcp_line_scores), 6) if wcp_line_scores else 0.0

    # EWP
    edge_persistence = (ewp_edge_persistence_numer / ewp_edge_persistence_denom
                        if ewp_edge_persistence_denom > 0 else 0.0)
    mean_post_close_residual = (sum(ewp_post_close_residuals) / len(ewp_post_close_residuals)
                                if ewp_post_close_residuals else 0.0)
    ewp = compute_ewp(ewp_prolonged_hardstop, ewp_unresolved_warning,
                       mean_post_close_residual, edge_persistence)

    # REF (via shared_metrics)
    ref_mean, ref_elig_frac = compute_ref(line_work_end_devs, line_close_end_devs)

    # CCY
    ccy = round(ccy_qualifying_y, 6)

    # QGY
    qgy = round(qgy_total, 6)

    # Old metrics
    old_viability = round(n_viable / n_tokens, 6) if n_tokens > 0 else 1.0
    old_y_final = round(state[Y_IDX], 6)

    metrics = {
        'PCV': pcv,
        'SAHB': sahb,
        'WCU': wcu,
        'SLR_mean': slr_mean,
        'UEB': ueb,
        'WCP': wcp,
        'EWP': ewp,
        'REF_mean': ref_mean,
        'REF_eligible_fraction': ref_elig_frac,
        'CCY': ccy,
        'QGY': qgy,
        'old_viability': old_viability,
        'old_y_final': old_y_final,
        'n_tokens': n_tokens,
    }

    # ================================================================
    # Aggregate events
    # ================================================================
    events_by_type_agg = {}
    for etype, successes in events_by_type.items():
        if successes:
            events_by_type_agg[etype] = _aggregate_successes(successes)

    events_by_demand_agg = {}
    for dq, successes in events_by_demand.items():
        if successes:
            events_by_demand_agg[dq] = _aggregate_successes(successes)

    events_by_type_demand_agg = {}
    for combo, successes in events_by_type_demand.items():
        if successes:
            events_by_type_demand_agg[combo] = _aggregate_successes(successes)

    # Round per-event detail floats
    for detail in per_event_details:
        for k in ('ERM', 'ESQ', 'CA', 'YG', 'CLR'):
            if detail.get(k) is not None:
                detail[k] = round(detail[k], 6)

    return {
        'metrics': metrics,
        'events_by_type': events_by_type_agg,
        'events_by_demand': events_by_demand_agg,
        'events_by_type_demand': events_by_type_demand_agg,
        'per_event_detail': per_event_details,
    }


def _aggregate_successes(successes):
    """Aggregate a list of event success dicts into summary stats."""
    n = len(successes)
    return {
        'count': n,
        'EIR': round(sum(s['EIR'] for s in successes) / n, 6),
        'mean_ERM': round(sum(s['ERM'] for s in successes) / n, 6),
        'mean_ESQ': round(sum(s['ESQ'] for s in successes) / n, 6),
        'mean_EW': round(sum(s['EW'] for s in successes) / n, 6),
        'mean_CA': round(sum(s['CA'] for s in successes) / n, 6),
        'mean_YG': round(sum(s['YG'] for s in successes) / n, 6),
    }


def _empty_folio_result():
    """Return empty result for folios with no tokens."""
    return {
        'metrics': {
            'PCV': 1.0, 'SAHB': 0.0, 'WCU': 0.0, 'SLR_mean': 0.0,
            'UEB': 0.0, 'WCP': 0.0, 'EWP': 0.0,
            'REF_mean': 0.0, 'REF_eligible_fraction': 0.0,
            'CCY': 0.0, 'QGY': 0.0,
            'old_viability': 1.0, 'old_y_final': 0.5, 'n_tokens': 0,
        },
        'events_by_type': {},
        'events_by_demand': {},
        'events_by_type_demand': {},
        'per_event_detail': [],
    }


# ---------------------------------------------------------------------------
# Ablation apparatus builders
# ---------------------------------------------------------------------------
def build_ablation_apparatus(profile_name, config_mode, ablation_mode):
    """Build apparatus with specific ablation applied."""
    if ablation_mode == 'no_close_recovery':
        return build_no_close_recovery_apparatus(profile_name, config_mode)
    elif ablation_mode == 'no_hazard_routing':
        # Build normal apparatus but zero out hazard routing sensitivity
        app = build_configured_apparatus(profile_name, config_mode)
        # Disable routing by zeroing sensitivity for routing-affected SVs
        for sv in STATE_VARS:
            app.sensitivity[sv] *= 0.5
        return app
    elif ablation_mode == 'no_zone_correction':
        # Build apparatus with reduced zone correction
        app = build_configured_apparatus(profile_name, config_mode)
        # Scale down close recovery
        return build_close_recovery_apparatus(
            profile_name, config_mode,
            r1_scale=0.0, k_cts=2.0, k_relief_scale=1.0,
            enable_close_recovery=False)
    else:
        return build_configured_apparatus(profile_name, config_mode)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T2: Event Executor — Full Model with Per-Event Success Metrics")
    print("Phase 569 - EVENTIVE_CLOSURE_PACKETS")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data sources ---")
    (line_packets, cts_data, all_tokens, budgets, budget_path,
     event_map, section_thresholds, regime_path) = load_data()

    # ---- Assign folio profiles ----
    print("\n--- Assigning folio profiles ---")
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    preferred_profile_map = {}
    for folio in PILOT_FOLIOS:
        fa = folio_assignments.get(folio, {})
        preferred_profile_map[folio] = fa.get('preferred_profile', 'A1_BATH_REFLUX')

    # Determine config modes
    folio_infra = compute_infra_scores(PILOT_FOLIOS)

    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, '?')
        cfg = folio_infra.get(folio, {}).get('config_mode', '?')
        print(f"  {folio}: preferred={pref}, config={cfg}")

    # ---- Group and sort tokens by folio ----
    print("\n--- Extracting pilot folio tokens ---")
    pilot_set = set(PILOT_FOLIOS)
    tokens_by_folio = {f: [] for f in pilot_set}
    for tok in all_tokens:
        if tok['folio'] in pilot_set:
            tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    for folio in PILOT_FOLIOS:
        n = len(tokens_by_folio[folio])
        print(f"  {folio}: {n} tokens")

    # ================================================================
    # PRIMARY RUNS (60): 20 folios x 3 profiles
    # ================================================================
    print("\n--- Primary Runs (60) ---")
    primary_results = {}
    run_count = 0

    for folio in PILOT_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

        for profile_name in ALL_PROFILES:
            apparatus = build_configured_apparatus(profile_name, config_mode)
            result = run_event_trace(apparatus, toks, line_packets, cts_data, event_map)

            run_key = f"{folio}|{profile_name}"
            primary_results[run_key] = result
            run_count += 1

            m = result['metrics']
            n_events = len(result['per_event_detail'])
            is_pref = (profile_name == preferred_profile_map.get(folio, ''))
            pref_tag = " *PREF*" if is_pref else ""

            if run_count % 10 == 0 or run_count <= 3:
                print(f"  [{run_count:2d}/60] {folio}|{profile_name.split('_')[0]}: "
                      f"PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
                      f"UEB={m['UEB']:.1f} CCY={m['CCY']:.4f} "
                      f"events={n_events}{pref_tag}")

    t_primary = time.time()
    print(f"\n  Primary runs completed: {run_count} in {t_primary - t0:.1f}s")

    # ================================================================
    # CONFIG ABLATION RUNS (30): 10 folios x 3 config modes
    # ================================================================
    print("\n--- Config Ablation Runs (30) ---")
    ablation_results = {}
    ablation_count = 0

    for folio in ABLATION_FOLIOS:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        preferred = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

        for abl_mode in CONFIG_ABLATION_MODES:
            apparatus = build_ablation_apparatus(preferred, config_mode, abl_mode)
            result = run_event_trace(apparatus, toks, line_packets, cts_data, event_map)

            abl_key = f"{folio}|{abl_mode}"
            ablation_results[abl_key] = result
            ablation_count += 1

            m = result['metrics']
            n_events = len(result['per_event_detail'])

            if ablation_count % 10 == 0 or ablation_count <= 3:
                print(f"  [{ablation_count:2d}/30] {folio}|{abl_mode}: "
                      f"PCV={m['PCV']:.4f} events={n_events}")

    t_ablation = time.time()
    print(f"\n  Ablation runs completed: {ablation_count} in {t_ablation - t_primary:.1f}s")

    # ================================================================
    # Build summary
    # ================================================================
    print("\n--- Building summary ---")

    # Mean metrics across preferred-profile primary runs
    pref_metrics = []
    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        key = f"{folio}|{pref}"
        if key in primary_results:
            pref_metrics.append(primary_results[key]['metrics'])

    mean_metrics = {}
    if pref_metrics:
        metric_keys = list(pref_metrics[0].keys())
        for mk in metric_keys:
            if mk == 'n_tokens':
                mean_metrics[mk] = sum(m[mk] for m in pref_metrics)
            else:
                vals = [m[mk] for m in pref_metrics]
                mean_metrics[mk] = round(sum(vals) / len(vals), 6)

    # Event type means across preferred-profile runs (global regime)
    all_events_by_type = defaultdict(list)
    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        key = f"{folio}|{pref}"
        if key in primary_results:
            for detail in primary_results[key]['per_event_detail']:
                for etype in detail['packet_types_global']:
                    all_events_by_type[etype].append({
                        'EIR': detail['EIR'],
                        'ERM': detail['ERM'],
                        'ESQ': detail['ESQ'],
                        'EW': detail['EW'],
                        'CA': detail['CA'],
                        'YG': detail['YG'],
                    })

    event_type_means_global = {}
    for etype, successes in all_events_by_type.items():
        if successes:
            event_type_means_global[etype] = _aggregate_successes(successes)

    summary = {
        'mean_metrics': mean_metrics,
        'event_type_means_global': event_type_means_global,
    }

    # ================================================================
    # Build output
    # ================================================================
    print("\n--- Writing output ---")

    output = {
        'metadata': {
            'phase': 569,
            'script': 't2_event_executor.py',
            'n_primary_runs': run_count,
            'n_ablation_runs': ablation_count,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pilot_folios': PILOT_FOLIOS,
            'profiles': ALL_PROFILES,
            'ablation_modes': CONFIG_ABLATION_MODES,
            'preferred_profiles': preferred_profile_map,
        },
        'primary_runs': {},
        'ablation_runs': {},
        'summary': summary,
    }

    # Primary runs
    for run_key, result in primary_results.items():
        output['primary_runs'][run_key] = result

    # Ablation runs
    for abl_key, result in ablation_results.items():
        output['ablation_runs'][abl_key] = result

    # Write
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 't2_event_runs.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = os.path.getsize(out_path)
    print(f"  Output: {out_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # ================================================================
    # Final statistics
    # ================================================================
    t_final = time.time()
    print(f"\n{'=' * 70}")
    print("FINAL STATISTICS (preferred-profile runs)")
    print(f"{'=' * 70}")

    print(f"\n  Total runs: {run_count + ablation_count}")
    print(f"  Total time: {t_final - t0:.1f}s")

    if mean_metrics:
        print(f"\n  Mean metrics across {len(pref_metrics)} preferred-profile runs:")
        for mk in ['PCV', 'SAHB', 'WCU', 'SLR_mean', 'UEB', 'WCP', 'EWP',
                    'REF_mean', 'CCY', 'QGY', 'old_viability', 'old_y_final']:
            if mk in mean_metrics:
                print(f"    {mk:<22s}: {mean_metrics[mk]:>10.6f}")

    if event_type_means_global:
        print(f"\n  Event type means (global regime, preferred profile):")
        print(f"  {'Type':<22s} {'count':>6s} {'EIR':>7s} {'ERM':>7s} "
              f"{'ESQ':>7s} {'EW':>7s} {'CA':>7s} {'YG':>7s}")
        for etype in sorted(event_type_means_global.keys()):
            agg = event_type_means_global[etype]
            print(f"  {etype:<22s} {agg['count']:6d} {agg['EIR']:7.4f} "
                  f"{agg['mean_ERM']:7.4f} {agg['mean_ESQ']:7.4f} "
                  f"{agg['mean_EW']:7.4f} {agg['mean_CA']:7.4f} "
                  f"{agg['mean_YG']:7.4f}")

    # Per-folio preferred breakdown
    print(f"\n  Per-folio preferred breakdown:")
    print(f"  {'Folio':<10s} {'PCV':>7s} {'WCU':>7s} {'UEB':>8s} {'CCY':>8s} "
          f"{'WCP':>7s} {'EWP':>8s} {'viab':>7s} {'events':>6s}")
    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        key = f"{folio}|{pref}"
        if key in primary_results:
            m = primary_results[key]['metrics']
            n_ev = len(primary_results[key]['per_event_detail'])
            print(f"  {folio:<10s} {m['PCV']:7.4f} {m['WCU']:7.4f} {m['UEB']:8.1f} "
                  f"{m['CCY']:8.4f} {m['WCP']:7.4f} {m['EWP']:8.1f} "
                  f"{m['old_viability']:7.4f} {n_ev:6d}")

    print(f"\n  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
