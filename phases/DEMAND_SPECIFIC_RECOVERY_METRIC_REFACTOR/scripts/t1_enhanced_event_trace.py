"""
T1: Enhanced Event Trace Library
Phase 570b - DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR

Fork of 570a T3 run_event_trace() with enhanced per-event state collection.

Enhancements over T3:
  - close_pre_state: state BEFORE first CLOSE token update (T4-style)
  - close_start_state retained (AFTER first CLOSE update) for ERM backward compat
  - CLOSE-phase dV accumulator: line_close_dv_sum, line_close_token_count
  - Enhanced per_event_detail with full state vectors
  - line_states always collected (no flag needed)

This is a LIBRARY MODULE - no main(), just exports.
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Re-exports from shared_metrics (canonical source)
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
# Re-exports from close recovery apparatus
# ---------------------------------------------------------------------------
from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    build_close_recovery_apparatus, build_configured_apparatus,
    build_no_close_recovery_apparatus,
    assign_folio_profiles, compute_infra_scores,
    PILOT_FOLIOS, PROFILES,
)

# ---------------------------------------------------------------------------
# Re-exports from T2 folio apparatus
# ---------------------------------------------------------------------------
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SELECTED_FOLIOS = ['f108v', 'f86v6', 'f111r', 'f84r']

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
        'line_states': [],
    }


def run_enhanced_event_trace(apparatus, tokens, line_packets, cts_data,
                             event_map):
    """
    Run one folio through the apparatus with event detection.

    Parameters
    ----------
    apparatus : CloseRecoveryApparatus or FolioSpecificApparatus
    tokens : list[dict]
    line_packets : dict
    cts_data : dict
    event_map : dict
    Returns
    -------
    dict with:
      - metrics: folio-level metric dict
      - events_by_type: {etype: {count, EIR, mean_ERM, ...}}
      - events_by_demand: {dq: {count, EIR, ...}}
      - per_event_detail: list of per-event dicts
      - line_states: list of per-line state dicts (always collected)
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        result = _empty_folio_result()
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
    close_pre_state = None         # state BEFORE first CLOSE token update (T4-style, NEW)
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

    # ---- Enhanced: CLOSE-phase dV accumulators (NEW) ----
    line_close_dv_sum = 0.0
    line_close_token_count_accum = 0

    # ---- Line state collection (always on) ----
    collected_line_states = []

    def _finalize_line():
        """Finalize metrics for the departing line."""
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_unresolved_warning
        nonlocal last_work_peak_dev, last_work_peak_svs_above_q2
        nonlocal prev_line_work_peak_dev

        if current_line_key is None:
            return

        # ---- Line state collection (always on) ----
        if line_start_state is not None:
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


            # Enhanced: resolve close_pre_state for event detail
            cp_state = close_pre_state if close_pre_state is not None else ls_state

            event_detail = {
                'line_key': current_line_key,
                'packet_types_global': sorted(event_info['packet_types_global']),
                'packet_types_section': sorted(event_info['packet_types_section']),
                'demand_qualifiers': sorted(demand_quals),
                # Enhanced state vectors for 570b metrics
                'close_pre_state': [round(v, 8) for v in cp_state],
                'line_end_state': [round(v, 8) for v in list(state)],
                'line_start_state': [round(v, 8) for v in ls_state],
                'dv_magnitude_sum': round(line_close_dv_sum, 8),
                'n_close_tokens': line_close_token_count_accum,
                'y_gain_event': round(
                    state[Y_IDX] - (cp_state[Y_IDX] if cp_state is not None
                                    else ls_state[Y_IDX]), 8),
                **success  # EIR, ERM, ESQ, EW, CA, YG, CLR unchanged
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
            close_pre_state = None          # Enhanced: reset per line
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

            # Enhanced: reset CLOSE-phase dV accumulators per line
            line_close_dv_sum = 0.0
            line_close_token_count_accum = 0

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

        # ---- Enhanced: capture close_pre_state BEFORE apparatus.update() ----
        if packet_phase == 'CLOSE' and close_pre_state is None:
            close_pre_state = list(state)  # state BEFORE first CLOSE token update

        # ---- Enhanced: accumulate CLOSE-phase dV magnitude ----
        if packet_phase == 'CLOSE':
            line_close_dv_sum += sum(abs(v) for v in dV)
            line_close_token_count_accum += 1

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

        # close_start_state: captured AFTER first CLOSE token update (T3 compat)
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
        'line_states': collected_line_states,
    }
    return result
