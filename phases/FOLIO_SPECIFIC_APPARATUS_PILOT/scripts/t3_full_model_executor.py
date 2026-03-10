"""
T3: Full Model Executor — 4 Models x 4 Folios + D3 Sensitivity
Phase 570a - FOLIO_SPECIFIC_APPARATUS_PILOT

Runs 4 comparison models across 4 selected pilot folios plus D3
single-axis knockout sensitivity analysis (36 total runs).

Models:
  M0  Generic baseline (current config, no F1-F5)
  M1  Folio-specific (F1-F5 applied via FolioSpecificApparatus)
  M2a Generic B10 (no close recovery)
  M2b Folio-specific B10 (F1-F5 applied, close recovery disabled)

D3 Sensitivity: For each folio, run M1 with each F axis neutralized:
  D3_noF1 through D3_noF5 (20 runs total)

Also collects per-line state data from M0 runs for T4 demand matching.
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
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Imports from shared_metrics (canonical source)
# ---------------------------------------------------------------------------
from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import (
    STATE_VARS, N_VARS, EQUILIBRIUM, SV_INDEX, S_IDX, Y_IDX,
    HAZARD_BOUNDARIES, Q1, Q2_BASE, HAZARD_DEV, PROCESS_SVS, PROCESS_IDX,
    classify_zone, is_in_bounds,
    pcv_token_score, sahb_token, wcu_token, wcp_token_quality,
    compute_wcp_line, compute_slr_line, compute_aggregate_dev,
    compute_event_success, classify_closure_demand,
    compute_ueb, compute_ewp, compute_ref, compute_sahb,
    DEFAULT_GLOBAL_THRESHOLDS,
)

# ---------------------------------------------------------------------------
# Imports from close recovery apparatus
# ---------------------------------------------------------------------------
from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    build_close_recovery_apparatus, build_configured_apparatus,
    build_no_close_recovery_apparatus,
    assign_folio_profiles, compute_infra_scores,
    PILOT_FOLIOS as ALL_PILOT_FOLIOS, PROFILES,
)

# ---------------------------------------------------------------------------
# Imports from T2 folio apparatus
# ---------------------------------------------------------------------------
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SELECTED_FOLIOS = ['f108v', 'f86v6', 'f111r', 'f84r']

MODEL_NAMES = ['M0', 'M1', 'M2a', 'M2b']

# Routing permissivity buffer
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
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

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

    print("  Loading T1 pilot selection (F1-F5 values)...")
    pilot_path = os.path.join(phases_dir, 'FOLIO_SPECIFIC_APPARATUS_PILOT',
                              'results', 't1_pilot_selection.json')
    with open(pilot_path, 'r', encoding='utf-8') as f:
        pilot_selection = json.load(f)
    folio_params = pilot_selection['folio_parameters']
    print(f"    Folio parameters: {len(folio_params)}")

    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (line_packets, cts_data, all_tokens, budgets, budget_path,
            event_map, section_thresholds, folio_params, regime_path)


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
# Aggregate event successes
# ---------------------------------------------------------------------------
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
        'per_event_detail': [],
    }


# ---------------------------------------------------------------------------
# Core execution function (reuses Phase 569 T2 pattern)
# ---------------------------------------------------------------------------
def run_event_trace(apparatus, tokens, line_packets, cts_data, event_map,
                    collect_line_states=False):
    """
    Run one folio through the apparatus with event detection.

    Parameters
    ----------
    apparatus : CloseRecoveryApparatus or FolioSpecificApparatus
    tokens : list[dict]
    line_packets : dict
    cts_data : dict
    event_map : dict
    collect_line_states : bool
        If True, collect per-line state data for T4 demand matching.

    Returns
    -------
    dict with:
      - metrics: folio-level metric dict
      - events_by_type: {etype: {count, EIR, mean_ERM, ...}}
      - events_by_demand: {dq: {count, EIR, ...}}
      - per_event_detail: list of per-event dicts
      - line_states: list of per-line state dicts (only if collect_line_states)
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        result = _empty_folio_result()
        if collect_line_states:
            result['line_states'] = []
        return result

    state = [EQUILIBRIUM] * N_VARS
    permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
    prev_line = None

    # ---- Metric accumulators ----
    n_viable = 0
    pcv_score_sum = 0.0
    pcv_pair_count = 0
    sahb_warnings = 0
    sahb_hardstops = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0
    line_work_end_devs = {}
    line_close_end_devs = {}
    qgy_total = 0.0
    prev_aggregate_dev = None
    wcu_score_sum = 0.0
    wcu_pair_count = 0
    slr_values = []
    ueb_close_warnings = 0
    ueb_close_hardstops = 0
    ueb_unresolved_fractions = []
    ueb_line_final_hardstop = 0
    ueb_post_line_residual_above_q2 = 0
    ccy_qualifying_y = 0.0
    last_work_peak_dev = 0.0
    last_work_peak_svs_above_q2 = 0
    wcp_line_scores = []
    ewp_prolonged_hardstop = 0
    ewp_unresolved_warning = 0
    ewp_post_close_residuals = []
    ewp_edge_persistence_numer = 0
    ewp_edge_persistence_denom = 0

    # ---- Event tracking ----
    per_event_details = []
    events_by_type = defaultdict(list)
    events_by_demand = defaultdict(list)

    # ---- Per-line state tracking ----
    current_line_key = None
    current_line_phase = None

    line_start_state = None
    close_start_state = None
    same_line_max_dev = 0.0
    line_work_end_state = None
    line_close_end_state = None
    line_work_peak_dev = 0.0
    line_work_peak_svs_above_q2 = 0

    line_spec_scores = []
    line_work_scores = []
    line_close_scores = []
    line_has_spec = False
    line_has_work = False
    line_has_close = False

    line_work_q2_exceeded = set()
    line_close_q2_returned = set()
    line_work_corridor_tokens = 0
    line_work_total_tokens = 0

    consecutive_work_hardstops = 0
    line_close_warning_svs = set()
    line_close_end_warning_svs = set()
    line_close_tokens_count = 0
    line_cts = 0.0
    prev_line_work_peak_dev = None

    # ---- T4 line state collection ----
    collected_line_states = [] if collect_line_states else None

    def _finalize_line():
        """Finalize metrics for the departing line."""
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_unresolved_warning
        nonlocal last_work_peak_dev, last_work_peak_svs_above_q2
        nonlocal prev_line_work_peak_dev

        if current_line_key is None:
            return

        # ---- T4 line state collection ----
        if collect_line_states and line_start_state is not None:
            agg_dev = compute_aggregate_dev(line_start_state)
            max_sv_dev = 0.0
            n_above_corridor = 0
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and line_start_state[i] > EQUILIBRIUM:
                    continue
                dev = abs(line_start_state[i] - EQUILIBRIUM)
                if dev > max_sv_dev:
                    max_sv_dev = dev
                if dev >= Q2_BASE[sv]:
                    n_above_corridor += 1
            collected_line_states.append({
                'line_key': current_line_key,
                'packet_phase': current_line_phase,
                'line_start_state': [round(v, 8) for v in line_start_state],
                'work_peak_dev': round(line_work_peak_dev, 8),
                'aggregate_dev': round(agg_dev, 8),
                'max_sv_dev': round(max_sv_dev, 8),
                'n_above_corridor': n_above_corridor,
            })

        # REF data
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

        # UEB: line_final_hardstop
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

        # UEB: unresolved fraction
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

        # SLR
        if line_work_end_state is not None:
            work_end_dev = sum(
                abs(line_work_end_state[i] - EQUILIBRIUM)
                for i in range(N_VARS) if i != Y_IDX
            ) / (N_VARS - 1)

            if work_end_dev > Q1:
                close_end_dev = work_end_dev
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

        # WCP
        wcp_val, _ = compute_wcp_line(
            line_spec_scores, line_work_scores, line_close_scores,
            line_has_spec, line_has_work, line_has_close)
        if wcp_val is not None:
            wcp_line_scores.append(wcp_val)

        # EWP: unresolved_warning
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

        # Cross-line WORK peak tracking
        if current_line_phase == 'WORK':
            last_work_peak_dev = line_work_peak_dev
            last_work_peak_svs_above_q2 = line_work_peak_svs_above_q2
            prev_line_work_peak_dev = line_work_peak_dev

        # --- EVENT DETECTION ---
        if current_line_phase == 'CLOSE' and current_line_key in event_map:
            event_info = event_map[current_line_key]

            cs_state = close_start_state if close_start_state is not None else line_start_state
            demand_quals = classify_closure_demand(
                close_start_state=cs_state,
                same_line_max_dev=same_line_max_dev,
                has_work_predecessor=event_info['has_work_predecessor'],
                work_peak_dev=prev_line_work_peak_dev if event_info['has_work_predecessor'] else None
            )

            ls_state = line_start_state if line_start_state is not None else [EQUILIBRIUM] * N_VARS
            wpd = prev_line_work_peak_dev if event_info['has_work_predecessor'] else None
            success = compute_event_success(
                line_start_state=ls_state,
                line_end_state=list(state),
                close_start_state=cs_state if cs_state is not None else ls_state,
                work_peak_dev=wpd
            )

            event_detail = {
                'line_key': current_line_key,
                'packet_types_global': sorted(event_info['packet_types_global']),
                'packet_types_section': sorted(event_info['packet_types_section']),
                'demand_qualifiers': sorted(demand_quals),
                **success
            }
            per_event_details.append(event_detail)

            for etype in event_info['packet_types_global']:
                events_by_type[etype].append(success)

            for dq in demand_quals:
                events_by_demand[dq].append(success)

    # ================================================================
    # Main token loop
    # ================================================================
    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']
        line_key = f"{folio}|{current_line}"

        # ---- Line boundary handling ----
        if current_line != prev_line:
            if prev_line is not None:
                _finalize_line()

            permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
            prev_line = current_line
            current_line_key = line_key

            if line_key in line_packets:
                lp = line_packets[line_key]
                current_line_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
            else:
                current_line_phase = 'WORK'

            line_cts = cts_data.get(line_key, 0.0)

            line_start_state = list(state)
            close_start_state = None
            same_line_max_dev = 0.0
            line_work_end_state = None
            line_close_end_state = None
            line_work_peak_dev = 0.0
            line_work_peak_svs_above_q2 = 0

            line_spec_scores = []
            line_work_scores = []
            line_close_scores = []
            line_has_spec = False
            line_has_work = False
            line_has_close = False

            line_work_q2_exceeded = set()
            line_close_q2_returned = set()
            line_work_corridor_tokens = 0
            line_work_total_tokens = 0

            consecutive_work_hardstops = 0
            line_close_warning_svs = set()
            line_close_end_warning_svs = set()
            line_close_tokens_count = 0

        # ---- Routing ----
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_PERMISSIVITY:
                for sv, shift in ROUTING_PERMISSIVITY[rt].items():
                    permissivity_buffer[sv] += shift

        packet_phase = current_line_phase
        cts = line_cts if line_cts > 0 else tok.get('cts', 0.0)

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

        # Viability
        if is_in_bounds(state):
            n_viable += 1

        # PCV
        pcv_s, pcv_c = pcv_token_score(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_pair_count += pcv_c

        # SAHB
        sw, sh, soc, sme = sahb_token(state, packet_phase)
        sahb_warnings += sw
        sahb_hardstops += sh
        sahb_outside_corridor += soc
        if sme > sahb_max_excursion:
            sahb_max_excursion = sme

        # WCU
        wcu_s, wcu_p = wcu_token(state, packet_phase)
        wcu_score_sum += wcu_s
        wcu_pair_count += wcu_p

        # UEB CLOSE-phase tallies
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

        # QGY
        if packet_phase == 'CLOSE':
            if cts > 0.3 and prev_aggregate_dev is not None:
                if current_agg_dev * (N_VARS - 1) < prev_aggregate_dev:
                    if y_delta > 0:
                        qgy_total += y_delta
            prev_aggregate_dev = current_agg_dev * (N_VARS - 1)
        else:
            prev_aggregate_dev = None

        # CCY
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

        # REF tracking
        if packet_phase == 'WORK':
            line_work_end_state = list(state)
        elif packet_phase == 'CLOSE':
            line_close_end_state = list(state)
            line_close_tokens_count += 1

        # WCP tracking
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

        # EWP tracking
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

            line_close_end_warning_svs = set()
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and s_above_eq:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_end_warning_svs.add(sv)

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

        # Per-line WORK peak tracking
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

            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev >= Q2_BASE[sv]:
                    line_work_q2_exceeded.add(sv)

            all_ok = all(
                abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                for sv in PROCESS_SVS
                if not (sv == 'S' and state[SV_INDEX[sv]] > EQUILIBRIUM)
            )
            if all_ok:
                line_work_corridor_tokens += 1

        elif packet_phase == 'CLOSE':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                if dev < Q2_BASE[sv]:
                    line_close_q2_returned.add(sv)

        # Event tracking: same_line_max_dev and close_start_state
        if packet_phase != 'CLOSE':
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
    pcv = round(pcv_score_sum / pcv_pair_count, 6) if pcv_pair_count > 0 else 1.0
    sahb = compute_sahb(sahb_warnings, sahb_hardstops, sahb_outside_corridor,
                        sahb_max_excursion, n_tokens)
    wcu = round(wcu_score_sum / wcu_pair_count, 6) if wcu_pair_count > 0 else 0.0
    slr_mean = round(sum(slr_values) / len(slr_values), 6) if slr_values else 0.0
    ueb = compute_ueb(ueb_close_warnings, ueb_close_hardstops,
                       ueb_unresolved_fractions,
                       ueb_line_final_hardstop,
                       ueb_post_line_residual_above_q2)
    wcp = round(sum(wcp_line_scores) / len(wcp_line_scores), 6) if wcp_line_scores else 0.0

    edge_persistence = (ewp_edge_persistence_numer / ewp_edge_persistence_denom
                        if ewp_edge_persistence_denom > 0 else 0.0)
    mean_post_close_residual = (sum(ewp_post_close_residuals) / len(ewp_post_close_residuals)
                                if ewp_post_close_residuals else 0.0)
    ewp = compute_ewp(ewp_prolonged_hardstop, ewp_unresolved_warning,
                       mean_post_close_residual, edge_persistence)

    ref_mean, ref_elig_frac = compute_ref(line_work_end_devs, line_close_end_devs)
    ccy = round(ccy_qualifying_y, 6)
    qgy = round(qgy_total, 6)
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

    # Aggregate events
    events_by_type_agg = {}
    for etype, successes in events_by_type.items():
        if successes:
            events_by_type_agg[etype] = _aggregate_successes(successes)

    events_by_demand_agg = {}
    for dq, successes in events_by_demand.items():
        if successes:
            events_by_demand_agg[dq] = _aggregate_successes(successes)

    for detail in per_event_details:
        for k in ('ERM', 'ESQ', 'CA', 'YG', 'CLR'):
            if detail.get(k) is not None:
                detail[k] = round(detail[k], 6)

    result = {
        'metrics': metrics,
        'events_by_type': events_by_type_agg,
        'events_by_demand': events_by_demand_agg,
        'per_event_detail': per_event_details,
    }

    if collect_line_states:
        result['line_states'] = collected_line_states

    return result


# ---------------------------------------------------------------------------
# Apparatus builders for the 4 models
# ---------------------------------------------------------------------------
def build_m0_apparatus(profile, config_mode):
    """M0: Generic baseline (current config, no F1-F5)."""
    return build_configured_apparatus(profile, config_mode)


def build_m1_apparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5):
    """M1: Folio-specific (F1-F5 applied)."""
    return FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5)


def build_m2a_apparatus(profile, config_mode):
    """M2a: Generic B10 (no close recovery)."""
    return build_no_close_recovery_apparatus(profile, config_mode)


def build_m2b_apparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5):
    """M2b: Folio-specific B10 (F1-F5 applied, close recovery disabled)."""
    app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5)
    app.enable_close_recovery = False
    return app


# ---------------------------------------------------------------------------
# D3 sensitivity builders
# ---------------------------------------------------------------------------
def build_d3_apparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5,
                       knockout_axis):
    """Build M1-like apparatus with one F-axis set to neutral.

    knockout_axis: 'F1', 'F2', 'F3', 'F4', or 'F5'
    """
    d3_f1, d3_f2, d3_f3, d3_f4, d3_f5 = f1, f2, f3, f4_raw, f5
    if knockout_axis == 'F1':
        d3_f1 = 1.0
    elif knockout_axis == 'F2':
        d3_f2 = 1.0
    elif knockout_axis == 'F3':
        d3_f3 = 1.0
    elif knockout_axis == 'F4':
        d3_f4 = 0.5  # H1 neutral
    elif knockout_axis == 'F5':
        d3_f5 = 1.0
    return FolioSpecificApparatus(profile, config_mode, folio,
                                  d3_f1, d3_f2, d3_f3, d3_f4, d3_f5)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: Full Model Executor - 4 Models x 4 Folios + D3 Sensitivity")
    print("Phase 570a - FOLIO_SPECIFIC_APPARATUS_PILOT")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data sources ---")
    (line_packets, cts_data, all_tokens, budgets, budget_path,
     event_map, section_thresholds, folio_params, regime_path) = load_data()

    # ---- Assign folio profiles and config modes ----
    print("\n--- Resolving folio profiles and config modes ---")
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(ALL_PILOT_FOLIOS)

    # Build profile/config map for selected folios
    folio_config = {}
    for folio in SELECTED_FOLIOS:
        fp = folio_params[folio]
        profile = fp['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        f_vals = {
            'f1': fp['F1'],
            'f2': fp['F2'],
            'f3': fp['F3'],
            'f4_raw': fp['F4_raw'],
            'f5': fp['F5'],
        }
        folio_config[folio] = {
            'profile': profile,
            'config_mode': config_mode,
            'section': fp['section'],
            **f_vals,
        }
        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"F1={f_vals['f1']:.4f} F2={f_vals['f2']:.4f} "
              f"F3={f_vals['f3']:.4f} F4={f_vals['f4_raw']:.4f} "
              f"F5={f_vals['f5']:.4f}")

    # ---- Group and sort tokens ----
    print("\n--- Extracting selected folio tokens ---")
    selected_set = set(SELECTED_FOLIOS)
    tokens_by_folio = {f: [] for f in selected_set}
    for tok in all_tokens:
        if tok['folio'] in selected_set:
            tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    for folio in SELECTED_FOLIOS:
        n = len(tokens_by_folio[folio])
        print(f"  {folio}: {n} tokens")

    # ================================================================
    # PRIMARY RUNS (16): 4 folios x 4 models
    # ================================================================
    print("\n--- Primary Runs (16) ---")
    primary_results = {}
    m0_line_states = {}
    run_count = 0

    for folio in SELECTED_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        fc = folio_config[folio]
        profile = fc['profile']
        config_mode = fc['config_mode']
        f1, f2, f3, f4_raw, f5 = (
            fc['f1'], fc['f2'], fc['f3'], fc['f4_raw'], fc['f5']
        )

        folio_results = {}

        # M0: Generic baseline (also collect line states for T4)
        app_m0 = build_m0_apparatus(profile, config_mode)
        result_m0 = run_event_trace(app_m0, toks, line_packets, cts_data,
                                    event_map, collect_line_states=True)
        m0_line_states[folio] = result_m0.pop('line_states', [])
        folio_results['M0'] = result_m0
        run_count += 1
        m = result_m0['metrics']
        n_ev = len(result_m0['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M0:  PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M1: Folio-specific
        app_m1 = build_m1_apparatus(profile, config_mode, folio,
                                    f1, f2, f3, f4_raw, f5)
        result_m1 = run_event_trace(app_m1, toks, line_packets, cts_data, event_map)
        folio_results['M1'] = result_m1
        run_count += 1
        m = result_m1['metrics']
        n_ev = len(result_m1['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M1:  PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M2a: Generic B10
        app_m2a = build_m2a_apparatus(profile, config_mode)
        result_m2a = run_event_trace(app_m2a, toks, line_packets, cts_data, event_map)
        folio_results['M2a'] = result_m2a
        run_count += 1
        m = result_m2a['metrics']
        n_ev = len(result_m2a['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M2a: PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M2b: Folio-specific B10
        app_m2b = build_m2b_apparatus(profile, config_mode, folio,
                                      f1, f2, f3, f4_raw, f5)
        result_m2b = run_event_trace(app_m2b, toks, line_packets, cts_data, event_map)
        folio_results['M2b'] = result_m2b
        run_count += 1
        m = result_m2b['metrics']
        n_ev = len(result_m2b['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M2b: PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        primary_results[folio] = folio_results

    t_primary = time.time()
    print(f"\n  Primary runs completed: {run_count} in {t_primary - t0:.1f}s")

    # ================================================================
    # D3 SENSITIVITY RUNS (20): 4 folios x 5 axis knockouts
    # ================================================================
    print("\n--- D3 Sensitivity Runs (20) ---")
    d3_results = {}
    d3_count = 0
    d3_axes = ['F1', 'F2', 'F3', 'F4', 'F5']

    for folio in SELECTED_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            continue

        fc = folio_config[folio]
        profile = fc['profile']
        config_mode = fc['config_mode']
        f1, f2, f3, f4_raw, f5 = (
            fc['f1'], fc['f2'], fc['f3'], fc['f4_raw'], fc['f5']
        )

        folio_d3 = {}
        for axis in d3_axes:
            d3_key = f"D3_no{axis}"
            app = build_d3_apparatus(profile, config_mode, folio,
                                     f1, f2, f3, f4_raw, f5, axis)
            result = run_event_trace(app, toks, line_packets, cts_data, event_map)
            folio_d3[d3_key] = result
            d3_count += 1

            m = result['metrics']
            n_ev = len(result['per_event_detail'])
            if d3_count % 5 == 0 or d3_count <= 2:
                print(f"  [{d3_count:2d}/20] {folio} {d3_key}: "
                      f"PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
                      f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f}")

        d3_results[folio] = folio_d3

    t_d3 = time.time()
    print(f"\n  D3 sensitivity runs completed: {d3_count} in {t_d3 - t_primary:.1f}s")

    # ================================================================
    # Build output
    # ================================================================
    print("\n--- Writing output ---")

    output = {
        'metadata': {
            'phase': '570a',
            'script': 't3_full_model_executor.py',
            'n_primary_runs': run_count,
            'n_d3_runs': d3_count,
            'total_runs': run_count + d3_count,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'selected_folios': SELECTED_FOLIOS,
            'models': MODEL_NAMES,
            'd3_axes': d3_axes,
        },
        'primary_runs': primary_results,
        'd3_sensitivity': d3_results,
        'm0_line_states': m0_line_states,
    }

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 't3_full_model_runs.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = os.path.getsize(out_path)
    print(f"  Output: {out_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # ================================================================
    # Final comparison table
    # ================================================================
    t_final = time.time()
    print(f"\n{'=' * 70}")
    print("COMPARISON: M0 (generic) vs M1 (folio-specific)")
    print(f"{'=' * 70}")

    key_metrics = ['PCV', 'WCU', 'SAHB', 'UEB', 'CCY', 'QGY', 'WCP', 'EWP',
                   'REF_mean', 'SLR_mean', 'old_viability', 'old_y_final']

    print(f"\n  {'Folio':<8s} {'Metric':<16s} {'M0':>10s} {'M1':>10s} {'M2a':>10s} "
          f"{'M2b':>10s} {'M1-M0':>10s}")
    print(f"  {'-'*8} {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for folio in SELECTED_FOLIOS:
        if folio not in primary_results:
            continue
        fr = primary_results[folio]
        for mk in key_metrics:
            m0_val = fr['M0']['metrics'].get(mk, 0.0)
            m1_val = fr['M1']['metrics'].get(mk, 0.0)
            m2a_val = fr['M2a']['metrics'].get(mk, 0.0)
            m2b_val = fr['M2b']['metrics'].get(mk, 0.0)
            delta = m1_val - m0_val
            print(f"  {folio:<8s} {mk:<16s} {m0_val:10.4f} {m1_val:10.4f} "
                  f"{m2a_val:10.4f} {m2b_val:10.4f} {delta:+10.4f}")
        print()

    # ---- D3 sensitivity summary ----
    print(f"\n{'=' * 70}")
    print("D3 SENSITIVITY: Impact of each F-axis knockout (M1 baseline)")
    print(f"{'=' * 70}")

    d3_summary_metrics = ['PCV', 'WCU', 'UEB', 'CCY', 'old_y_final']
    print(f"\n  {'Folio':<8s} {'Knockout':<10s}", end='')
    for mk in d3_summary_metrics:
        print(f" {mk:>10s}", end='')
    print(f" {'vs M1':>10s}")

    for folio in SELECTED_FOLIOS:
        if folio not in primary_results or folio not in d3_results:
            continue
        m1_pcv = primary_results[folio]['M1']['metrics']['PCV']
        for axis in d3_axes:
            d3_key = f"D3_no{axis}"
            d3m = d3_results[folio][d3_key]['metrics']
            print(f"  {folio:<8s} {d3_key:<10s}", end='')
            for mk in d3_summary_metrics:
                print(f" {d3m.get(mk, 0.0):10.4f}", end='')
            # Delta PCV vs M1
            delta_pcv = d3m['PCV'] - m1_pcv
            print(f" {delta_pcv:+10.4f}")
        print()

    # ---- Event summary ----
    print(f"\n{'=' * 70}")
    print("EVENT SUMMARY: Per-folio event counts and EIR by model")
    print(f"{'=' * 70}")

    print(f"\n  {'Folio':<8s} {'Model':<6s} {'events':>7s} {'EIR':>7s} {'mean_ERM':>10s} "
          f"{'mean_ESQ':>10s} {'demanded':>8s}")
    for folio in SELECTED_FOLIOS:
        if folio not in primary_results:
            continue
        for model in MODEL_NAMES:
            fr = primary_results[folio][model]
            n_ev = len(fr['per_event_detail'])
            ebt = fr['events_by_type']
            e_any = ebt.get('E_any', {})
            eir = e_any.get('EIR', 0.0)
            erm = e_any.get('mean_ERM', 0.0)
            esq = e_any.get('mean_ESQ', 0.0)

            ebd = fr['events_by_demand']
            n_demanded = ebd.get('demanded', {}).get('count', 0)

            print(f"  {folio:<8s} {model:<6s} {n_ev:7d} {eir:7.4f} {erm:10.4f} "
                  f"{esq:10.4f} {n_demanded:8d}")
        print()

    # ---- M0 line states summary ----
    print(f"\n{'=' * 70}")
    print("M0 LINE STATES (for T4 demand matching)")
    print(f"{'=' * 70}")
    for folio in SELECTED_FOLIOS:
        lines = m0_line_states.get(folio, [])
        n_close = sum(1 for ls in lines if ls['packet_phase'] == 'CLOSE')
        n_work = sum(1 for ls in lines if ls['packet_phase'] == 'WORK')
        print(f"  {folio}: {len(lines)} lines total, {n_work} WORK, {n_close} CLOSE")

    print(f"\n  Total time: {t_final - t0:.1f}s")
    print(f"  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
