"""
T4: Null Executor
==================
Phase 570a - FOLIO_SPECIFIC_APPARATUS_PILOT

Runs standard null shuffles (M3: N1-N4 x 20 permutations) and demand-matched
null permutations (M4 generic, M4f folio-specific) across 4 pilot folios.

Total runs:
  M3:  4 null types x 4 folios x 20 perms = 320
  M4:  4 folios x 20 perms = 80
  M4f: 4 folios x 20 perms = 80
  Total: 480

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t3_line_packets.json                     (line-level packet_phase)
  - t7_closure_cts.json                      (per-line CTS)
  - t2_folio_budgets.json                    (folio budgets for profile assignment)
  - t1_event_taxonomy.json                   (event map, section thresholds)
  - regime_folio_mapping.json                (regime mapping)
  - t1_pilot_selection.json                  (selected folios, F1-F5 parameters)

Output:
  - t4_null_runs.json
"""

import sys
import json
import math
import time
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import (
    STATE_VARS, N_VARS, EQUILIBRIUM, SV_INDEX, S_IDX, Y_IDX,
    HAZARD_BOUNDARIES, Q1, Q2_BASE, HAZARD_DEV, PROCESS_SVS,
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
    PILOT_FOLIOS, PROFILES,
)

from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
    build_demand_matched_assignments,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = PHASE_DIR.parent  # phases/

T2B_PATH = BASE / 'VIRTUAL_APPARATUS_COUPLING' / 'results' / 't2b_supervisory_interface_unrouted.json'
PACKETS_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't3_line_packets.json'
CTS_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't7_closure_cts.json'
BUDGET_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't2_folio_budgets.json'
EVENT_TAX_PATH = BASE / 'EVENTIVE_CLOSURE_PACKETS' / 'results' / 't1_event_taxonomy.json'
REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
PILOT_SELECTION_PATH = PHASE_DIR / 'results' / 't1_pilot_selection.json'
OUTPUT_PATH = PHASE_DIR / 'results' / 't4_null_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (permissivity model)
# ---------------------------------------------------------------------------
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
# Preferred profile map (lazy init)
# ---------------------------------------------------------------------------
_PREFERRED_PROFILE_MAP = None


def _init_preferred_profiles():
    global _PREFERRED_PROFILE_MAP
    if _PREFERRED_PROFILE_MAP is not None:
        return
    _PREFERRED_PROFILE_MAP = {}
    fa = assign_folio_profiles(REGIME_PATH, BUDGET_PATH)
    for folio in PILOT_FOLIOS:
        entry = fa.get(folio, {})
        _PREFERRED_PROFILE_MAP[folio] = entry.get('preferred_profile', 'A1_BATH_REFLUX')


def get_preferred_profile(folio):
    _init_preferred_profiles()
    return _PREFERRED_PROFILE_MAP.get(folio, 'A1_BATH_REFLUX')


# ---------------------------------------------------------------------------
# Token sort key
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
# WCU zone scores (imported indirectly via shared_metrics)
# ---------------------------------------------------------------------------
try:
    from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import (
        WCU_ZONE_SCORES, WCU_S_HIGH_SCORE,
    )
except ImportError:
    WCU_ZONE_SCORES = {'BASIN': 1.0, 'CORRIDOR': 0.7, 'WARNING': 0.3, 'HARD_STOP': 0.0, 'HAZARD': 0.0}
    WCU_S_HIGH_SCORE = 0.85


# ---------------------------------------------------------------------------
# Core execution function (adapted from Phase 569 t3_event_null_executor)
# ---------------------------------------------------------------------------
def run_event_trace(apparatus, tokens, line_packets, line_cts_map,
                    event_map, section_thresholds,
                    shuffled_phases=None, shuffle_dv_rng=None):
    """
    Run one folio through the apparatus and compute:
      - Standard metrics (PCV, SAHB, REF, UEB, WCU, SLR, WCP, EWP, etc.)
      - Per-event success metrics (EIR, ERM, ESQ, EW) for CLOSE lines
      - Under both phase-native and structure-native event scoring

    Also tracks per-line state data needed for demand-matched null construction.

    Parameters:
      apparatus:         CloseRecoveryApparatus or FolioSpecificApparatus
      tokens:            list of token dicts, pre-sorted by (line, position)
      line_packets:      dict mapping "folio|line" -> packet info
      line_cts_map:      dict mapping "folio|line" -> CTS value
      event_map:         dict mapping line_key -> event taxonomy entry
      section_thresholds: dict of section -> threshold values
      shuffled_phases:   dict {line_key: new_phase} for phase shuffle nulls
      shuffle_dv_rng:    if set, randomly permute dV components per token

    Returns dict with metrics, event results, and per-line state data.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return _empty_result()

    folio = tokens[0]['folio']
    state = [EQUILIBRIUM] * N_VARS
    permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
    prev_line = None

    # --- Accumulators ---
    n_viable = 0

    # PCV
    pcv_score_sum = 0.0
    pcv_count = 0

    # SAHB
    sahb_warnings = 0
    sahb_hardstops = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # REF
    line_work_end_devs = {}
    line_close_end_devs = {}

    # QGY
    qgy_total = 0.0
    prev_aggregate_dev = None

    # WCU
    wcu_score_sum = 0.0
    wcu_pair_count = 0

    # SLR
    slr_values = []
    slr_work_peak_devs = []

    # UEB
    ueb_close_warnings = 0
    ueb_close_hardstops = 0
    ueb_unresolved_fractions = []
    ueb_line_final_hardstop = 0
    ueb_post_line_residual_above_q2 = 0

    # WCP
    wcp_line_scores = []
    wcp_full_packet_scores = []

    # EWP
    ewp_prolonged_hardstop = 0
    ewp_unresolved_warning = 0
    ewp_post_close_residual = 0
    ewp_edge_persistence = 0

    # --- Per-line tracking ---
    current_line_key = None
    current_line_work_end_state = None
    current_line_close_end_state = None
    current_line_phase = None
    line_start_state = None
    close_start_state = None

    # WCP per-line
    line_spec_scores = []
    line_work_scores = []
    line_close_scores = []
    line_has_spec = False
    line_has_work = False
    line_has_close = False

    # SLR per-line
    line_work_peak_dev = 0.0
    line_work_peak_svs_above_q2 = 0
    line_work_q2_exceeded = set()
    line_close_q2_returned = set()
    line_work_corridor_tokens = 0
    line_work_total_tokens = 0

    # EWP per-line
    consecutive_work_hardstops = 0
    line_close_warning_svs = set()
    line_close_end_warning_svs = set()
    line_had_close = False

    # Same-line max dev for closure demand classification
    same_line_max_dev = 0.0

    # --- Per-line state data for demand-matched null construction ---
    line_states_data = []
    line_keys_ordered = []

    # --- Event tracking ---
    structure_native_events = []
    phase_native_events = []

    structure_close_keys = set(event_map.keys())

    phase_native_close_keys = set()
    if shuffled_phases is not None:
        phase_native_close_keys = {lk for lk, p in shuffled_phases.items() if p == 'CLOSE'}
    else:
        for lk, pkt in line_packets.items():
            if pkt.get('packet_state', {}).get('packet_phase') == 'CLOSE':
                phase_native_close_keys.add(lk)

    prev_line_key = None
    prev_line_phase = None
    prev_line_work_peak_dev = None

    def _get_packet_phase(line_key):
        if shuffled_phases is not None:
            return shuffled_phases.get(line_key, 'WORK')
        pkt = line_packets.get(line_key)
        if pkt and 'packet_state' in pkt:
            return pkt['packet_state'].get('packet_phase', 'WORK')
        return 'WORK'

    def _classify_event_types_for_line(line_key):
        if line_key in event_map:
            entry = event_map[line_key]
            return set(entry['packet_types_global'])

        pkt = line_packets.get(line_key)
        if pkt is None:
            return {'E_any'}

        ps = pkt.get('packet_state', {})
        sec = pkt.get('section', 'B')
        cts_val = line_cts_map.get(line_key, 0.0)
        mcb = ps.get('m_close_bias', 0.0)
        cob = ps.get('close_opacity_bias', 0.0)
        prof = pkt.get('profile', [])
        q4o = prof[14] if len(prof) > 14 else 0.0
        armed = ps.get('closure_armed', False)

        sec_th = section_thresholds.get(sec, {})
        effective_sec_th = dict(sec_th)
        if effective_sec_th.get('mcb_p75', 0.0) == 0.0:
            if effective_sec_th.get('mcb_p90', 0.0) > 0.0:
                effective_sec_th['mcb_p75'] = effective_sec_th['mcb_p90']

        from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import classify_packet_identity
        identity = classify_packet_identity(
            cts=cts_val, mcb=mcb, cob=cob, q4o=q4o, armed=armed,
            global_thresholds=DEFAULT_GLOBAL_THRESHOLDS,
            section_thresholds=effective_sec_th,
            section=sec
        )
        return identity['global']

    def _finalize_line():
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_post_close_residual, ewp_edge_persistence
        nonlocal ewp_unresolved_warning
        nonlocal prev_line_key, prev_line_phase, prev_line_work_peak_dev

        if current_line_key is None:
            return

        effective_phase = _get_packet_phase(current_line_key)

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

        # UEB: line_final_hardstop
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            zone = classify_zone(sv, dev)
            if zone == 'HARD_STOP':
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

            if work_end_dev > Q1:
                close_end_dev = work_end_dev
                if current_line_close_end_state is not None:
                    close_end_dev = sum(
                        abs(current_line_close_end_state[i] - EQUILIBRIUM)
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
                    slr_work_peak_devs.append(line_work_peak_dev)

        # WCP: compute per-line score
        wcp_val, is_full = compute_wcp_line(
            line_spec_scores, line_work_scores, line_close_scores,
            line_has_spec, line_has_work, line_has_close)
        if wcp_val is not None:
            wcp_line_scores.append(wcp_val)
            if is_full:
                wcp_full_packet_scores.append(wcp_val)

        # EWP: unresolved_warning
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

        # EWP: edge_persistence
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and state[i] > EQUILIBRIUM:
                continue
            dev = abs(state[i] - EQUILIBRIUM)
            zone = classify_zone(sv, dev)
            if zone in ('HARD_STOP', 'HAZARD'):
                ewp_edge_persistence += 1
                break

        # --- Record per-line state data ---
        n_above = 0
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            if sv == 'S' and line_start_state[i] > EQUILIBRIUM:
                continue
            dev = abs(line_start_state[i] - EQUILIBRIUM)
            if dev >= Q2_BASE[sv]:
                n_above += 1

        agg_dev = sum(abs(line_start_state[i] - EQUILIBRIUM) for i in range(N_VARS)
                       if i != Y_IDX) / (N_VARS - 1)
        max_sv = max(
            abs(line_start_state[SV_INDEX[sv]] - EQUILIBRIUM)
            for sv in PROCESS_SVS
        )

        line_states_data.append({
            'line_key': current_line_key,
            'packet_phase': effective_phase,
            'line_start_state': list(line_start_state),
            'work_peak_dev': line_work_peak_dev,
            'aggregate_dev': agg_dev,
            'max_sv_dev': max_sv,
            'n_above_corridor': n_above,
        })
        line_keys_ordered.append(current_line_key)

        # --- EVENT SUCCESS COMPUTATION ---

        # Structure-native: compute event success at original CLOSE lines
        if current_line_key in structure_close_keys:
            if close_start_state is not None and line_start_state is not None:
                event_entry = event_map[current_line_key]
                event_types = set(event_entry['packet_types_global'])

                has_wp = event_entry.get('has_work_predecessor', False)
                wp_dev = prev_line_work_peak_dev if (prev_line_phase == 'WORK' or has_wp) else None

                demand = classify_closure_demand(
                    close_start_state, same_line_max_dev,
                    has_work_predecessor=has_wp,
                    work_peak_dev=wp_dev
                )

                success = compute_event_success(
                    line_start_state, list(state), close_start_state,
                    work_peak_dev=wp_dev
                )

                structure_native_events.append({
                    'line_key': current_line_key,
                    'event_types': sorted(event_types),
                    'demand': sorted(demand),
                    'success': success,
                })

        # Phase-native: compute event success at lines labeled CLOSE under current phases
        if current_line_key in phase_native_close_keys:
            if close_start_state is not None and line_start_state is not None:
                event_types = _classify_event_types_for_line(current_line_key)

                has_wp = prev_line_phase == 'WORK'
                wp_dev = prev_line_work_peak_dev if has_wp else None

                demand = classify_closure_demand(
                    close_start_state, same_line_max_dev,
                    has_work_predecessor=has_wp,
                    work_peak_dev=wp_dev
                )

                success = compute_event_success(
                    line_start_state, list(state), close_start_state,
                    work_peak_dev=wp_dev
                )

                phase_native_events.append({
                    'line_key': current_line_key,
                    'event_types': sorted(event_types),
                    'demand': sorted(demand),
                    'success': success,
                })

        # Update prev_line tracking
        prev_line_key = current_line_key
        prev_line_phase = effective_phase
        prev_line_work_peak_dev = line_work_peak_dev if effective_phase == 'WORK' else None

    # =====================================================================
    # MAIN LOOP
    # =====================================================================
    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        tok_folio = tok.get('folio', folio)

        # 1. Line boundary handling
        if current_line != prev_line:
            if prev_line is not None:
                _finalize_line()

            # Reset line-level tracking
            permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
            prev_line = current_line
            current_line_key = f"{tok_folio}|{current_line}"
            current_line_work_end_state = None
            current_line_close_end_state = None
            current_line_phase = None
            line_start_state = list(state)
            close_start_state = None
            same_line_max_dev = 0.0

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
            line_had_close = False

        # 2. Routing event (permissivity model)
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_PERMISSIVITY:
                for sv, shift in ROUTING_PERMISSIVITY[rt].items():
                    permissivity_buffer[sv] += shift

        # 3. Look up packet_phase
        line_key = f"{tok_folio}|{current_line}"
        packet_phase = _get_packet_phase(line_key)
        current_line_phase = packet_phase

        # Track close_start_state for event success
        if packet_phase == 'CLOSE' and close_start_state is None:
            close_start_state = list(state)

        # 4. Get CTS
        cts = line_cts_map.get(line_key, tok.get('cts', 0.0))

        # 5. Compute dV and update state
        contributions = tok['contributions']
        pre_state = list(state)

        if shuffle_dv_rng is not None:
            # N4: permute dV components
            dV = [0.0] * N_VARS
            for i, sv in enumerate(STATE_VARS):
                base_sens = apparatus.sensitivity[sv]
                dV[i] = contributions[i] * base_sens * (1.0 + permissivity_buffer.get(sv, 0.0))
            shuffle_dv_rng.shuffle(dV)
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)
        else:
            # Normal execution
            dV = [0.0] * N_VARS
            for i, sv in enumerate(STATE_VARS):
                base_sens = apparatus.sensitivity[sv]
                dV[i] = contributions[i] * base_sens * (1.0 + permissivity_buffer.get(sv, 0.0))
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)

        # 6. Decay routing buffers
        for sv in STATE_VARS:
            permissivity_buffer[sv] *= ROUTING_DECAY

        # Track same-line max dev for closure demand
        current_agg_dev = compute_aggregate_dev(state)
        if current_agg_dev > same_line_max_dev:
            same_line_max_dev = current_agg_dev

        # ================================================================
        # METRICS
        # ================================================================

        # Viability
        if is_in_bounds(state):
            n_viable += 1

        # PCV
        pcv_s, pcv_c = pcv_token_score(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_count += pcv_c

        # SAHB
        sw, sh, soc, sme = sahb_token(state, packet_phase)
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
            c_agg_dev = sum(abs(state[i] - EQUILIBRIUM)
                            for i in range(N_VARS) if i != Y_IDX)
            if cts > 0.3 and prev_aggregate_dev is not None:
                if c_agg_dev < prev_aggregate_dev:
                    y_increment = state[Y_IDX] - pre_state[Y_IDX]
                    if y_increment > 0:
                        qgy_total += y_increment
            prev_aggregate_dev = c_agg_dev
        else:
            prev_aggregate_dev = None

        # WCU
        if packet_phase == 'WORK':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                dev = abs(state[i] - EQUILIBRIUM)
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    wcu_score_sum += WCU_S_HIGH_SCORE
                else:
                    zone = classify_zone(sv, dev)
                    if dev >= HAZARD_DEV[sv]:
                        wcu_score_sum += WCU_ZONE_SCORES.get('HAZARD', 0.0)
                    else:
                        wcu_score_sum += WCU_ZONE_SCORES.get(zone, 0.0)
                wcu_pair_count += 1

        # SLR tracking
        if packet_phase == 'WORK':
            line_work_total_tokens += 1
            work_dev = sum(abs(state[i] - EQUILIBRIUM)
                           for i in range(N_VARS) if i != Y_IDX) / (N_VARS - 1)
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

        # UEB tracking
        if packet_phase == 'CLOSE':
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    ueb_close_warnings += 1
                elif zone == 'HARD_STOP':
                    ueb_close_hardstops += 1

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
        if packet_phase == 'WORK':
            any_hardstop = False
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
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
            line_had_close = True
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_warning_svs.add(sv)

            line_close_end_warning_svs = set()
            for sv in PROCESS_SVS:
                i = SV_INDEX[sv]
                if sv == 'S' and state[i] > EQUILIBRIUM:
                    continue
                dev = abs(state[i] - EQUILIBRIUM)
                zone = classify_zone(sv, dev)
                if zone == 'WARNING':
                    line_close_end_warning_svs.add(sv)

    # Finalize last line
    _finalize_line()

    # ================================================================
    # Compute final metric values
    # ================================================================
    old_viability = round(n_viable / n_tokens, 6) if n_tokens > 0 else 1.0
    old_y_final = round(state[Y_IDX], 6)

    pcv = round(pcv_score_sum / pcv_count, 6) if pcv_count > 0 else 1.0

    sahb = compute_sahb(sahb_warnings, sahb_hardstops, sahb_outside_corridor,
                        sahb_max_excursion, n_tokens)

    ref_mean, ref_elig_frac = compute_ref(line_work_end_devs, line_close_end_devs)

    qgy = round(qgy_total, 6)
    qgy_ratio = round(qgy_total / state[Y_IDX], 6) if state[Y_IDX] > 1e-10 else 0.0

    wcu = round(wcu_score_sum / wcu_pair_count, 6) if wcu_pair_count > 0 else 0.0

    slr_mean = round(sum(slr_values) / len(slr_values), 6) if slr_values else 0.0
    slr_elig_frac = round(len(slr_values) / max(1, len(line_work_end_devs)), 6)

    ueb = compute_ueb(ueb_close_warnings, ueb_close_hardstops,
                       ueb_unresolved_fractions, ueb_line_final_hardstop,
                       ueb_post_line_residual_above_q2)

    wcp = round(sum(wcp_line_scores) / len(wcp_line_scores), 6) if wcp_line_scores else 0.0
    wcp_full = (round(sum(wcp_full_packet_scores) / len(wcp_full_packet_scores), 6)
                if wcp_full_packet_scores else 0.0)

    ewp = compute_ewp(ewp_prolonged_hardstop, ewp_unresolved_warning,
                       ewp_post_close_residual, ewp_edge_persistence)

    metrics = {
        'old_viability': old_viability,
        'old_y_final': old_y_final,
        'PCV': pcv,
        'SAHB': sahb,
        'REF_mean': ref_mean,
        'REF_eligible_fraction': ref_elig_frac,
        'QGY': qgy,
        'qgy_ratio': qgy_ratio,
        'WCU': wcu,
        'SLR_mean': slr_mean,
        'SLR_eligible_fraction': slr_elig_frac,
        'UEB': ueb,
        'WCP': wcp,
        'WCP_full_packet_mean': wcp_full,
        'EWP': ewp,
    }

    # --- Aggregate event results ---
    def _aggregate_events(events_list):
        by_type = defaultdict(lambda: {'count': 0, 'EIR_sum': 0, 'ERM_sum': 0.0,
                                        'ESQ_sum': 0.0, 'EW_sum': 0})
        by_demand = defaultdict(lambda: {'count': 0, 'EIR_sum': 0, 'ERM_sum': 0.0,
                                          'ESQ_sum': 0.0, 'EW_sum': 0})

        for ev in events_list:
            s = ev['success']
            for etype in ev['event_types']:
                bt = by_type[etype]
                bt['count'] += 1
                bt['EIR_sum'] += s['EIR']
                bt['ERM_sum'] += s['ERM']
                bt['ESQ_sum'] += s['ESQ']
                bt['EW_sum'] += s['EW']

            for dq in ev['demand']:
                bd = by_demand[dq]
                bd['count'] += 1
                bd['EIR_sum'] += s['EIR']
                bd['ERM_sum'] += s['ERM']
                bd['ESQ_sum'] += s['ESQ']
                bd['EW_sum'] += s['EW']

        def _finalize(d):
            result = {}
            for k, v in d.items():
                n = v['count']
                result[k] = {
                    'count': n,
                    'EIR': round(v['EIR_sum'] / n, 6) if n > 0 else 0.0,
                    'mean_ERM': round(v['ERM_sum'] / n, 6) if n > 0 else 0.0,
                    'mean_ESQ': round(v['ESQ_sum'] / n, 6) if n > 0 else 0.0,
                    'mean_EW': round(v['EW_sum'] / n, 6) if n > 0 else 0.0,
                }
            return result

        return {
            'events_by_type': _finalize(by_type),
            'events_by_demand': _finalize(by_demand),
        }

    sn_agg = _aggregate_events(structure_native_events)
    pn_agg = _aggregate_events(phase_native_events)

    return {
        'metrics': metrics,
        'events_by_type': pn_agg['events_by_type'],
        'events_by_demand': pn_agg['events_by_demand'],
        'events_by_type_structure_native': sn_agg['events_by_type'],
        'events_by_demand_structure_native': sn_agg['events_by_demand'],
        'line_states': line_states_data,
    }


def _empty_result():
    return {
        'metrics': {
            'old_viability': 1.0, 'old_y_final': 0.5, 'PCV': 1.0, 'SAHB': 0.0,
            'REF_mean': 0.0, 'REF_eligible_fraction': 0.0, 'QGY': 0.0, 'qgy_ratio': 0.0,
            'WCU': 0.0, 'SLR_mean': 0.0, 'SLR_eligible_fraction': 0.0,
            'UEB': 0.0, 'WCP': 0.0, 'WCP_full_packet_mean': 0.0, 'EWP': 0.0,
        },
        'events_by_type': {},
        'events_by_demand': {},
        'events_by_type_structure_native': {},
        'events_by_demand_structure_native': {},
        'line_states': [],
    }


# ---------------------------------------------------------------------------
# Null model generators
# ---------------------------------------------------------------------------

def null_n1_phase_shuffle(tokens, line_packets, rng):
    """N1: Phase-shuffle. Randomly permute packet_phase labels within folio."""
    folio = tokens[0]['folio'] if tokens else ''
    folio_line_keys = [f"{folio}|{tok['line']}" for tok in tokens]
    unique_keys = list(dict.fromkeys(folio_line_keys))

    phases = []
    for k in unique_keys:
        pkt = line_packets.get(k)
        if pkt and 'packet_state' in pkt:
            phases.append(pkt['packet_state'].get('packet_phase', 'WORK'))
        else:
            phases.append('WORK')

    rng.shuffle(phases)
    shuffled_phases = {k: p for k, p in zip(unique_keys, phases)}
    return tokens, shuffled_phases


def null_n2_token_shuffle(tokens, rng):
    """N2: Token-shuffle. Shuffle all token contributions within folio."""
    all_contribs = [list(tok['contributions']) for tok in tokens]
    rng.shuffle(all_contribs)

    shuffled = []
    for i, tok in enumerate(tokens):
        nt = dict(tok)
        nt['contributions'] = all_contribs[i]
        shuffled.append(nt)
    return shuffled


def null_n3_cross_folio(tokens, folio, other_folio_tokens):
    """N3: Cross-folio. Use supervisory tokens from a different folio."""
    result = []
    n_other = len(other_folio_tokens)
    if n_other == 0:
        return tokens

    for i, tok in enumerate(tokens):
        nt = dict(tok)
        src_idx = i % n_other
        nt['contributions'] = list(other_folio_tokens[src_idx]['contributions'])
        result.append(nt)
    return result


def null_n4_dv_permutation(tokens, rng):
    """N4: dV permutation. Permute the 7 components of each token's contributions."""
    shuffled = []
    for tok in tokens:
        nt = dict(tok)
        contribs = list(tok['contributions'])
        rng.shuffle(contribs)
        nt['contributions'] = contribs
        shuffled.append(nt)
    return shuffled


# ---------------------------------------------------------------------------
# Demand-matched null helpers
# ---------------------------------------------------------------------------

def build_demand_shuffled_phases(line_states, assignment, line_packets):
    """Build shuffled_phases dict from demand-matched assignment.

    Parameters
    ----------
    line_states : list[dict]
        Per-line state data from M0 reference trace.
    assignment : list[tuple[int, int]]
        List of (real_close_idx, matched_non_close_idx) pairs.
    line_packets : dict
        Original line_packets for phase lookup.

    Returns
    -------
    dict
        Mapping line_key -> new phase.
    """
    # Start with original phases for all lines
    shuffled = {}
    for ls in line_states:
        lk = ls['line_key']
        shuffled[lk] = ls['packet_phase']

    # Swap: matched non-CLOSE lines get CLOSE, real CLOSE lines get matched line's phase
    for real_close_idx, matched_idx in assignment:
        real_lk = line_states[real_close_idx]['line_key']
        matched_lk = line_states[matched_idx]['line_key']

        matched_original_phase = line_states[matched_idx]['packet_phase']

        shuffled[matched_lk] = 'CLOSE'
        shuffled[real_lk] = matched_original_phase

    return shuffled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T4: Null Executor")
    print("Phase 570a - FOLIO_SPECIFIC_APPARATUS_PILOT")
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
        cts_raw = json.load(f)
    line_cts_raw = cts_raw['line_cts']
    line_cts_map = {k: v['cts'] for k, v in line_cts_raw.items()}
    print(f"  Line CTS entries: {len(line_cts_map)}")

    with open(EVENT_TAX_PATH, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']
    section_thresholds = event_taxonomy['section_thresholds']
    print(f"  Event map entries: {len(event_map)}")

    with open(PILOT_SELECTION_PATH, 'r', encoding='utf-8') as f:
        pilot_selection = json.load(f)
    selected_folios = pilot_selection['selected_folios']
    folio_parameters = pilot_selection['folio_parameters']
    print(f"  Selected folios: {selected_folios}")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # --- Preferred profiles and config modes ---
    folio_infra = compute_infra_scores(PILOT_FOLIOS)

    for folio in selected_folios:
        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        fp = folio_parameters[folio]
        n_toks = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"F1={fp['F1']}, F2={fp['F2']}, F3={fp['F3']}, "
              f"F4_raw={fp['F4_raw']}, F5={fp['F5']}, n_tokens={n_toks}")

    N_PERMS = 20

    # Common trace kwargs
    def make_trace_kwargs():
        return dict(
            line_packets=line_packets,
            line_cts_map=line_cts_map,
            event_map=event_map,
            section_thresholds=section_thresholds,
        )

    # Metric keys to accumulate
    METRIC_KEYS = [
        'old_viability', 'old_y_final', 'PCV', 'SAHB', 'REF_mean',
        'REF_eligible_fraction', 'QGY', 'qgy_ratio', 'WCU', 'SLR_mean',
        'SLR_eligible_fraction', 'UEB', 'WCP', 'WCP_full_packet_mean', 'EWP',
    ]

    EVENT_TYPES = ['E_any', 'E_armed', 'E_compound', 'E_cts50',
                   'E_decisive', 'E_mcb', 'E_opaque', 'E_opaque_decisive']

    run_count = 0

    # =====================================================================
    # STEP 1: Run M0 reference traces for each folio to get line_states
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 1: M0 reference traces (4 folios)")
    print("=" * 70)

    m0_line_states = {}  # folio -> list of line_state dicts
    m0_close_indices = {}  # folio -> list of close line indices

    for folio in selected_folios:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            print(f"  WARNING: {folio} has no tokens, skipping")
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        apparatus = build_configured_apparatus(profile, config_mode)

        result = run_event_trace(apparatus, toks, **make_trace_kwargs())
        run_count += 1

        line_states = result['line_states']
        m0_line_states[folio] = line_states

        # Identify CLOSE line indices
        close_indices = []
        for idx, ls in enumerate(line_states):
            if ls['line_key'] in event_map:
                close_indices.append(idx)
        m0_close_indices[folio] = close_indices

        m = result['metrics']
        n_events = sum(e['count'] for e in result['events_by_type'].values())
        print(f"  {folio}: PCV={m['PCV']:.4f}, WCU={m['WCU']:.4f}, "
              f"n_lines={len(line_states)}, n_close={len(close_indices)}, "
              f"n_events={n_events}")

    # =====================================================================
    # STEP 2: Build demand-matched assignments
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Build demand-matched assignments")
    print("=" * 70)

    dm_assignments = {}  # folio -> list of permutations

    for folio in selected_folios:
        line_states = m0_line_states.get(folio, [])
        close_indices = m0_close_indices.get(folio, [])

        if not close_indices:
            print(f"  {folio}: no CLOSE lines, skipping demand-matched nulls")
            dm_assignments[folio] = []
            continue

        assignments = build_demand_matched_assignments(
            line_states, close_indices,
            n_permutations=N_PERMS, k_neighbors=5, seed=42
        )
        dm_assignments[folio] = assignments
        print(f"  {folio}: {len(assignments)} permutations, "
              f"{len(close_indices)} CLOSE lines, "
              f"{len(line_states) - len(close_indices)} non-CLOSE lines")

    # =====================================================================
    # STEP 3: M3 Standard Null Runs (N1-N4 x 4 folios x 20 perms = 320)
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 3: M3 Standard Nulls (4 types x 4 folios x 20 perms = 320)")
    print("=" * 70)

    m3_nulls = {
        'N1': {},
        'N2': {},
        'N3': {},
        'N4': {},
    }

    # Build cross-folio lookup for N3 (cycle through other 3 selected folios)
    other_folio_cycle = {}
    for folio in selected_folios:
        others = [f for f in selected_folios if f != folio]
        other_folio_cycle[folio] = others

    for folio in selected_folios:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tk = make_trace_kwargs()

        for nn in m3_nulls:
            m3_nulls[nn][folio] = []

        for perm_idx in range(N_PERMS):
            seed = 42 + perm_idx

            # --- N1: Phase shuffle ---
            rng1 = random.Random(seed)
            n1_toks, shuffled_phases = null_n1_phase_shuffle(toks, line_packets, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_event_trace(apparatus, n1_toks, shuffled_phases=shuffled_phases, **tk)
            m3_nulls['N1'][folio].append({
                'metrics': r1['metrics'],
                'events_by_type': r1['events_by_type'],
            })
            run_count += 1

            # --- N2: Token shuffle ---
            rng2 = random.Random(seed)
            n2_toks = null_n2_token_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_event_trace(apparatus, n2_toks, **tk)
            m3_nulls['N2'][folio].append({
                'metrics': r2['metrics'],
                'events_by_type': r2['events_by_type'],
            })
            run_count += 1

            # --- N3: Cross-folio ---
            others = other_folio_cycle[folio]
            other_folio = others[perm_idx % len(others)]
            other_toks = tokens_by_folio.get(other_folio, [])
            n3_toks = null_n3_cross_folio(toks, folio, other_toks)
            apparatus = build_configured_apparatus(profile, config_mode)
            r3 = run_event_trace(apparatus, n3_toks, **tk)
            m3_nulls['N3'][folio].append({
                'metrics': r3['metrics'],
                'events_by_type': r3['events_by_type'],
            })
            run_count += 1

            # --- N4: dV permutation ---
            rng4 = random.Random(seed)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_event_trace(apparatus, toks, shuffle_dv_rng=rng4, **tk)
            m3_nulls['N4'][folio].append({
                'metrics': r4['metrics'],
                'events_by_type': r4['events_by_type'],
            })
            run_count += 1

        if run_count % 40 == 0 or True:
            elapsed = time.time() - t0
            print(f"  M3 {folio} done ({run_count} total runs, {elapsed:.1f}s)")

    # =====================================================================
    # STEP 4: M4 Demand-Matched Nulls, Generic Apparatus (4 folios x 20 perms = 80)
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 4: M4 Demand-Matched Nulls, Generic (4 folios x 20 perms = 80)")
    print("=" * 70)

    m4_demand_matched = {}

    for folio in selected_folios:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tk = make_trace_kwargs()

        line_states = m0_line_states.get(folio, [])
        assignments = dm_assignments.get(folio, [])

        m4_demand_matched[folio] = []

        if not assignments:
            print(f"  {folio}: no demand-matched assignments, skipping")
            continue

        for perm_idx, assignment in enumerate(assignments):
            shuffled_phases = build_demand_shuffled_phases(line_states, assignment, line_packets)
            apparatus = build_configured_apparatus(profile, config_mode)
            r = run_event_trace(apparatus, toks, shuffled_phases=shuffled_phases, **tk)

            m4_demand_matched[folio].append({
                'metrics': r['metrics'],
                'events_by_type': r['events_by_type'],
                'events_by_demand': r['events_by_demand'],
            })
            run_count += 1

        elapsed = time.time() - t0
        print(f"  M4 {folio} done ({run_count} total runs, {elapsed:.1f}s)")

    # =====================================================================
    # STEP 5: M4f Demand-Matched Nulls, Folio-Specific Apparatus (4 x 20 = 80)
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 5: M4f Demand-Matched Nulls, Folio-Specific (4 folios x 20 perms = 80)")
    print("=" * 70)

    m4f_demand_matched = {}

    for folio in selected_folios:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tk = make_trace_kwargs()

        fp = folio_parameters[folio]
        line_states = m0_line_states.get(folio, [])
        assignments = dm_assignments.get(folio, [])

        m4f_demand_matched[folio] = []

        if not assignments:
            print(f"  {folio}: no demand-matched assignments, skipping")
            continue

        for perm_idx, assignment in enumerate(assignments):
            shuffled_phases = build_demand_shuffled_phases(line_states, assignment, line_packets)

            # Build folio-specific apparatus
            fsa = FolioSpecificApparatus(
                profile=profile,
                config_mode=config_mode,
                folio=folio,
                f1=fp['F1'],
                f2=fp['F2'],
                f3=fp['F3'],
                f4_raw=fp['F4_raw'],
                f5=fp['F5'],
            )

            r = run_event_trace(fsa, toks, shuffled_phases=shuffled_phases, **tk)

            m4f_demand_matched[folio].append({
                'metrics': r['metrics'],
                'events_by_type': r['events_by_type'],
                'events_by_demand': r['events_by_demand'],
            })
            run_count += 1

        elapsed = time.time() - t0
        print(f"  M4f {folio} done ({run_count} total runs, {elapsed:.1f}s)")

    # =====================================================================
    # Compute means
    # =====================================================================
    print("\nComputing means...")

    def _compute_mean_metrics(perms_list):
        """Average metrics across permutations."""
        n_p = len(perms_list)
        if n_p == 0:
            return {}
        mean_metrics = {}
        for mk in METRIC_KEYS:
            vals = [p['metrics'].get(mk, 0.0) for p in perms_list]
            mean_metrics[mk] = round(sum(vals) / n_p, 6)
        return mean_metrics

    def _compute_mean_events(perms_list, key='events_by_type'):
        """Average event metrics across permutations."""
        n_p = len(perms_list)
        if n_p == 0:
            return {}
        mean_events = {}
        for etype in EVENT_TYPES:
            counts = [p.get(key, {}).get(etype, {}).get('count', 0) for p in perms_list]
            eirs = [p.get(key, {}).get(etype, {}).get('EIR', 0.0)
                    for p in perms_list if etype in p.get(key, {})]
            erms = [p.get(key, {}).get(etype, {}).get('mean_ERM', 0.0)
                    for p in perms_list if etype in p.get(key, {})]
            esqs = [p.get(key, {}).get(etype, {}).get('mean_ESQ', 0.0)
                    for p in perms_list if etype in p.get(key, {})]
            ews = [p.get(key, {}).get(etype, {}).get('mean_EW', 0.0)
                   for p in perms_list if etype in p.get(key, {})]

            mean_count = round(sum(counts) / n_p, 6)
            if eirs:
                mean_events[etype] = {
                    'count': mean_count,
                    'EIR': round(sum(eirs) / len(eirs), 6),
                    'mean_ERM': round(sum(erms) / len(erms), 6),
                    'mean_ESQ': round(sum(esqs) / len(esqs), 6),
                    'mean_EW': round(sum(ews) / len(ews), 6),
                }
        return mean_events

    def _compute_mean_demand_events(perms_list):
        """Average events_by_demand across permutations."""
        n_p = len(perms_list)
        if n_p == 0:
            return {}
        # Collect all demand categories seen
        all_demand_keys = set()
        for p in perms_list:
            all_demand_keys.update(p.get('events_by_demand', {}).keys())

        mean_demand = {}
        for dk in all_demand_keys:
            counts = [p.get('events_by_demand', {}).get(dk, {}).get('count', 0) for p in perms_list]
            eirs = [p.get('events_by_demand', {}).get(dk, {}).get('EIR', 0.0)
                    for p in perms_list if dk in p.get('events_by_demand', {})]

            mean_count = round(sum(counts) / n_p, 6)
            if eirs:
                mean_demand[dk] = {
                    'count': mean_count,
                    'EIR': round(sum(eirs) / len(eirs), 6),
                }
        return mean_demand

    # M3 means
    m3_means = {}
    for nn in m3_nulls:
        m3_means[nn] = {}
        for folio in m3_nulls[nn]:
            perms = m3_nulls[nn][folio]
            m3_means[nn][folio] = {
                'mean': {
                    'metrics': _compute_mean_metrics(perms),
                    'events_by_type': _compute_mean_events(perms),
                },
                'all_perms': perms,
            }

    # M4 means
    m4_means = {}
    for folio in m4_demand_matched:
        perms = m4_demand_matched[folio]
        m4_means[folio] = {
            'mean': {
                'metrics': _compute_mean_metrics(perms),
                'events_by_type': _compute_mean_events(perms),
                'events_by_demand': _compute_mean_demand_events(perms),
            },
            'all_perms': perms,
        }

    # M4f means
    m4f_means = {}
    for folio in m4f_demand_matched:
        perms = m4f_demand_matched[folio]
        m4f_means[folio] = {
            'mean': {
                'metrics': _compute_mean_metrics(perms),
                'events_by_type': _compute_mean_events(perms),
                'events_by_demand': _compute_mean_demand_events(perms),
            },
            'all_perms': perms,
        }

    # =====================================================================
    # Assemble output
    # =====================================================================
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': '570a',
            'script': 't4_null_executor.py',
            'n_m3_runs': sum(len(m3_nulls[nn].get(f, []))
                             for nn in m3_nulls for f in selected_folios),
            'n_m4_runs': sum(len(m4_demand_matched.get(f, [])) for f in selected_folios),
            'n_m4f_runs': sum(len(m4f_demand_matched.get(f, [])) for f in selected_folios),
            'total_runs': run_count,
            'n_perms': N_PERMS,
            'selected_folios': selected_folios,
            'folio_parameters': folio_parameters,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'null_descriptions': {
                'N1': 'Phase-shuffle (permute packet_phase labels within folio)',
                'N2': 'Token-shuffle (shuffle token contributions within folio)',
                'N3': 'Cross-folio (use contributions from different folio)',
                'N4': 'dV permutation (permute 7 components of each dV vector)',
                'M4': 'Demand-matched null, generic apparatus',
                'M4f': 'Demand-matched null, folio-specific apparatus',
            },
        },
        'm3_nulls': {
            nn: {
                folio: m3_means[nn][folio]
                for folio in selected_folios
                if folio in m3_means[nn]
            }
            for nn in sorted(m3_means.keys())
        },
        'm4_demand_matched': {
            folio: m4_means[folio]
            for folio in selected_folios
            if folio in m4_means
        },
        'm4f_demand_matched_folio_specific': {
            folio: m4f_means[folio]
            for folio in selected_folios
            if folio in m4f_means
        },
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

    # --- M3 null summary ---
    print(f"\n  M3 Standard Nulls (mean across folios):")
    key_metrics = ['PCV', 'WCU', 'SLR_mean', 'UEB', 'WCP', 'EWP']
    header = f"  {'Metric':<22}"
    for nn in ['N1', 'N2', 'N3', 'N4']:
        header += f" {nn:>8}"
    print(header)
    print(f"  {'-' * 22}" + (' ' + '-' * 8) * 4)

    for mk in key_metrics:
        row = f"  {mk:<22}"
        for nn in ['N1', 'N2', 'N3', 'N4']:
            vals = [m3_means[nn].get(f, {}).get('mean', {}).get('metrics', {}).get(mk, 0.0)
                    for f in selected_folios]
            mean_val = sum(vals) / len(vals) if vals else 0.0
            row += f" {mean_val:>8.4f}"
        print(row)

    # --- M3 EIR summary ---
    print(f"\n  M3 Event Success (EIR E_any):")
    for nn in ['N1', 'N2', 'N3', 'N4']:
        eirs = []
        for f in selected_folios:
            eir = m3_means[nn].get(f, {}).get('mean', {}).get(
                'events_by_type', {}).get('E_any', {}).get('EIR', None)
            if eir is not None:
                eirs.append(eir)
        if eirs:
            print(f"    {nn}: mean_EIR_any={sum(eirs)/len(eirs):.4f}")

    # --- M4 vs M4f comparison ---
    print(f"\n  M4 vs M4f Demand-Matched Nulls (per folio):")
    print(f"  {'Folio':<10} {'M4 PCV':>8} {'M4f PCV':>8} {'M4 EIR':>8} {'M4f EIR':>8}")
    print(f"  {'-' * 10} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8}")

    for folio in selected_folios:
        m4_pcv = m4_means.get(folio, {}).get('mean', {}).get('metrics', {}).get('PCV', 0.0)
        m4f_pcv = m4f_means.get(folio, {}).get('mean', {}).get('metrics', {}).get('PCV', 0.0)
        m4_eir = m4_means.get(folio, {}).get('mean', {}).get(
            'events_by_type', {}).get('E_any', {}).get('EIR', 0.0)
        m4f_eir = m4f_means.get(folio, {}).get('mean', {}).get(
            'events_by_type', {}).get('E_any', {}).get('EIR', 0.0)
        print(f"  {folio:<10} {m4_pcv:>8.4f} {m4f_pcv:>8.4f} {m4_eir:>8.4f} {m4f_eir:>8.4f}")

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
