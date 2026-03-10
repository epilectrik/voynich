"""
T3: Event Null Executor
========================
Phase 569 - EVENTIVE_CLOSURE_PACKETS

Runs baselines (B1-B10), reference, and null (N1-N4 x 50 permutations)
models with DUAL event scoring (phase-native + structure-native) and the
four-metric success stack (EIR, ERM, ESQ, EW).

Total: 20 reference + 10 baselines x 20 folios + 4 nulls x 20 folios x 50 perms
     = 20 + 200 + 4000 = 4,220 runs

Baseline runs (B1-B10):
  B1:  No apparatus (state unchanged by contributions)
  B2:  Random walk (small random dV each token)
  B3:  Equilibrium pull (weak constant pull toward 0.5)
  B4:  No close recovery apparatus (build_no_close_recovery_apparatus)
  B5:  Halved gains (apparatus with 0.5x sensitivity)
  B6:  Doubled gains (apparatus with 2.0x sensitivity)
  B7:  Inverted CTS (1 - cts)
  B8:  Zero CTS (cts=0 always)
  B9:  Shuffled dV (randomly permute dV components within each token)
  B10: No close recovery (same as B4, tracked separately)

Null runs (N1-N4):
  N1: Phase-shuffle     (randomly permute packet_phase labels within folio)
  N2: Token-shuffle     (shuffle all tokens within folio, keep original phases)
  N3: Cross-folio       (run tokens from a different folio's supervisory data)
  N4: dV permutation    (permute the 7 components of each dV vector)

Key feature: For null runs, event success is computed under BOTH scoring
regimes (phase-native and structure-native).

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t3_line_packets.json                     (line-level packet_phase)
  - t7_closure_cts.json                      (per-line CTS)
  - t2_folio_budgets.json                    (folio budgets for profile assignment)
  - t1_closure_field_audit.json              (COF normalization bounds)
  - t1_event_taxonomy.json                   (event map, section thresholds)

Output:
  - t3_event_null_runs.json
"""

import sys
import os
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
    HAZARD_BOUNDARIES, Q1, Q2_BASE, HAZARD_DEV, PROCESS_SVS, PROCESS_IDX,
    PCV_ZONE_SCORES, PCV_S_HIGH_SCORES, PCV_PROCESS_SVS,
    SAHB_WARNING_WEIGHT, SAHB_HARDSTOP_WEIGHT, SAHB_OUTSIDE_CORRIDOR_WEIGHT, SAHB_MAX_EXCURSION_WEIGHT,
    WCU_ZONE_SCORES, WCU_S_HIGH_SCORE, EIR_EPSILON,
    classify_zone, is_in_bounds,
    pcv_token_score, sahb_token, wcu_token, wcp_token_quality,
    compute_wcp_line, compute_slr_line, compute_aggregate_dev,
    compute_event_success, classify_closure_demand,
    compute_ueb, compute_ewp, compute_ref, compute_sahb,
    DEFAULT_GLOBAL_THRESHOLDS
)

from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    build_close_recovery_apparatus, build_no_close_recovery_apparatus,
    build_configured_apparatus, assign_folio_profiles, compute_infra_scores,
    PILOT_FOLIOS, PROFILES,
    CloseRecoveryApparatus, GAMMA_CORRIDOR,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = PHASE_DIR.parent  # phases/

T2B_PATH = BASE / 'VIRTUAL_APPARATUS_COUPLING' / 'results' / 't2b_supervisory_interface_unrouted.json'
PACKETS_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't3_line_packets.json'
CTS_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't7_closure_cts.json'
BUDGET_PATH = BASE / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results' / 't2_folio_budgets.json'
COF_PATH = BASE / 'CLOSURE_FIELD_AUDIT' / 'results' / 't1_closure_field_audit.json'
EVENT_TAX_PATH = PHASE_DIR / 'results' / 't1_event_taxonomy.json'
REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
OUTPUT_PATH = PHASE_DIR / 'results' / 't3_event_null_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (from 567/568 T3)
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

# ---------------------------------------------------------------------------
# Preferred profile map (lazy init)
# ---------------------------------------------------------------------------
_PREFERRED_PROFILE_MAP = None


def _init_preferred_profiles():
    """Initialize preferred profile map from assign_folio_profiles."""
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
# Core execution function
# ---------------------------------------------------------------------------
def run_event_trace(apparatus, tokens, line_packets, line_cts_map,
                    event_map, section_thresholds,
                    disable_cts=False, force_phase=None,
                    shuffled_phases=None, invert_cts=False,
                    random_walk_rng=None, equil_pull=False,
                    shuffle_dv_rng=None):
    """
    Run one folio through the apparatus and compute:
      - Standard metrics (PCV, SAHB, REF, UEB, WCU, SLR, WCP, EWP, etc.)
      - Per-event success metrics (EIR, ERM, ESQ, EW) for CLOSE lines
      - Under both phase-native and structure-native event scoring

    Parameters:
      apparatus:         CloseRecoveryApparatus or None (B1: no apparatus)
      tokens:            list of token dicts, pre-sorted by (line, position)
      line_packets:      dict mapping "folio|line" -> packet info
      line_cts_map:      dict mapping "folio|line" -> CTS value
      event_map:         dict mapping line_key -> event taxonomy entry (from T1)
      section_thresholds: dict of section -> threshold values
      disable_cts:       if True, CTS is forced to 0
      force_phase:       if set, override packet_phase for all tokens
      shuffled_phases:   dict {line_key: new_phase} for N1 phase shuffle
      invert_cts:        if True, use (1 - cts) instead of cts
      random_walk_rng:   if set, use random walk dV instead of contributions
      equil_pull:        if True, apply weak equilibrium pull instead of apparatus
      shuffle_dv_rng:    if set, randomly permute dV components per token

    Returns dict with metrics and event results.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return _empty_result()

    folio = tokens[0]['folio']
    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
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

    # CCY tracking
    ccy_work_mean_dev = None
    ccy_work_svs_above_q2 = 0

    # Same-line max dev for closure demand classification
    same_line_max_dev = 0.0

    # --- Event tracking ---
    # Structure-native: events at lines in the ORIGINAL event_map
    # Phase-native: events at lines labeled CLOSE under current (possibly shuffled) phases
    structure_native_events = []
    phase_native_events = []

    # Pre-compute: which line_keys are CLOSE in the original event_map (structure-native)
    structure_close_keys = set(event_map.keys())

    # Pre-compute: which line_keys are CLOSE under current phases (phase-native)
    # This depends on shuffled_phases or line_packets
    phase_native_close_keys = set()
    if shuffled_phases is not None:
        phase_native_close_keys = {lk for lk, p in shuffled_phases.items() if p == 'CLOSE'}
    elif force_phase == 'CLOSE':
        # All lines are CLOSE
        for tok in tokens:
            phase_native_close_keys.add(f"{tok['folio']}|{tok['line']}")
    else:
        # Use line_packets
        for lk, pkt in line_packets.items():
            if pkt.get('packet_state', {}).get('packet_phase') == 'CLOSE':
                phase_native_close_keys.add(lk)

    # Per-line: track whether the previous line was WORK (for closure demand)
    prev_line_key = None
    prev_line_phase = None
    prev_line_work_peak_dev = None

    def _get_packet_phase(line_key):
        """Get packet phase for a line, considering overrides."""
        if force_phase is not None:
            return force_phase
        if shuffled_phases is not None:
            return shuffled_phases.get(line_key, 'WORK')
        pkt = line_packets.get(line_key)
        if pkt and 'packet_state' in pkt:
            return pkt['packet_state'].get('packet_phase', 'WORK')
        return 'WORK'

    def _classify_event_types_for_line(line_key):
        """Classify event types for a line using its original closure features.

        For phase-native scoring of shuffled nulls: the line that received the
        CLOSE label may not be in the original event_map (it was originally
        SPEC or WORK). In that case, look up the line's original closure
        features from line_packets/cts_data and classify.
        """
        # Check if already in event_map
        if line_key in event_map:
            entry = event_map[line_key]
            return set(entry['packet_types_global'])

        # Not in event_map: look up original features
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
        # Handle mcb P75 edge case
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
        """Finalize metrics for the departing line."""
        nonlocal ueb_line_final_hardstop, ueb_post_line_residual_above_q2
        nonlocal ewp_post_close_residual, ewp_edge_persistence
        nonlocal ewp_unresolved_warning
        nonlocal ccy_work_mean_dev, ccy_work_svs_above_q2
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

        # CCY: update WORK-peak dev
        if current_line_work_end_state is not None and line_work_peak_dev > 0:
            ccy_work_mean_dev = line_work_peak_dev
            ccy_work_svs_above_q2 = line_work_peak_svs_above_q2

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

        # Pre-update state
        pre_state = list(state)

        # 1. Line boundary handling
        if current_line != prev_line:
            if prev_line is not None:
                _finalize_line()

            # Reset line-level tracking
            routing_contrib_buffer = [0.0] * N_VARS
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

        # 2. Routing event
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_EFFECTS:
                effects = ROUTING_EFFECTS[rt]
                for sv, mult in effects.get('boost', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                for sv, mult in effects.get('suppress', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN

        # 3. Look up packet_phase
        line_key = f"{tok_folio}|{current_line}"
        packet_phase = _get_packet_phase(line_key)
        current_line_phase = packet_phase

        # Track close_start_state for event success
        if packet_phase == 'CLOSE' and close_start_state is None:
            close_start_state = list(state)

        # 4. Get CTS
        if disable_cts:
            cts = 0.0
        else:
            cts = line_cts_map.get(line_key, tok.get('cts', 0.0))
            if invert_cts:
                cts = 1.0 - cts

        # 5. Compute dV
        contributions = tok['contributions']

        if apparatus is None:
            # B1: no apparatus, state unchanged
            pass
        elif random_walk_rng is not None:
            # B2: random walk
            dV = [random_walk_rng.gauss(0, 0.005) for _ in range(N_VARS)]
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)
        elif equil_pull:
            # B3: weak equilibrium pull
            dV = [(EQUILIBRIUM - state[i]) * 0.02 for i in range(N_VARS)]
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)
        elif shuffle_dv_rng is not None:
            # B9/N4: permute dV components
            dV = [0.0] * N_VARS
            for i, sv in enumerate(STATE_VARS):
                base_sens = apparatus.sensitivity[sv]
                dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])
            shuffle_dv_rng.shuffle(dV)
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)
        else:
            # Normal execution
            dV = [0.0] * N_VARS
            for i, sv in enumerate(STATE_VARS):
                base_sens = apparatus.sensitivity[sv]
                dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts)

        # 6. Decay routing buffers
        routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]

        # Track same-line max dev for closure demand
        current_agg_dev = compute_aggregate_dev(state)
        if current_agg_dev > same_line_max_dev:
            same_line_max_dev = current_agg_dev

        # ================================================================
        # RETAINED METRICS
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

        # ================================================================
        # NEW METRICS
        # ================================================================

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
                        wcu_score_sum += WCU_ZONE_SCORES['HAZARD']
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
        """Aggregate event list into per-type and per-demand summaries."""
        by_type = defaultdict(lambda: {'count': 0, 'EIR_sum': 0, 'ERM_sum': 0.0,
                                        'ESQ_sum': 0.0, 'EW_sum': 0})
        by_demand = defaultdict(lambda: {'count': 0, 'EIR_sum': 0, 'ERM_sum': 0.0,
                                          'ESQ_sum': 0.0, 'EW_sum': 0})
        by_type_demand = defaultdict(lambda: {'count': 0, 'EIR_sum': 0, 'ERM_sum': 0.0,
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

            # Type x Demand cross
            for etype in ev['event_types']:
                for dq in ev['demand']:
                    k = f"{etype}|{dq}"
                    btd = by_type_demand[k]
                    btd['count'] += 1
                    btd['EIR_sum'] += s['EIR']
                    btd['ERM_sum'] += s['ERM']
                    btd['ESQ_sum'] += s['ESQ']
                    btd['EW_sum'] += s['EW']

        # Compute means
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
            'events_by_type_demand': _finalize(by_type_demand),
        }

    sn_agg = _aggregate_events(structure_native_events)
    pn_agg = _aggregate_events(phase_native_events)

    return {
        'metrics': metrics,
        'events_by_type': pn_agg['events_by_type'],
        'events_by_demand': pn_agg['events_by_demand'],
        'events_by_type_demand': pn_agg['events_by_type_demand'],
        'events_by_type_structure_native': sn_agg['events_by_type'],
        'events_by_demand_structure_native': sn_agg['events_by_demand'],
        'per_event_detail': phase_native_events,  # full detail (reference only)
        'per_event_detail_structure_native': structure_native_events,
    }


def _empty_result():
    """Return empty result dict for folios with no tokens."""
    return {
        'metrics': {
            'old_viability': 1.0, 'old_y_final': 0.5, 'PCV': 1.0, 'SAHB': 0.0,
            'REF_mean': 0.0, 'REF_eligible_fraction': 0.0, 'QGY': 0.0, 'qgy_ratio': 0.0,
            'WCU': 0.0, 'SLR_mean': 0.0, 'SLR_eligible_fraction': 0.0,
            'UEB': 0.0, 'WCP': 0.0, 'WCP_full_packet_mean': 0.0, 'EWP': 0.0,
        },
        'events_by_type': {},
        'events_by_demand': {},
        'events_by_type_demand': {},
        'events_by_type_structure_native': {},
        'events_by_demand_structure_native': {},
        'per_event_detail': [],
        'per_event_detail_structure_native': [],
    }


# ---------------------------------------------------------------------------
# Null model generators
# ---------------------------------------------------------------------------

def null_n1_phase_shuffle(tokens, line_packets, rng):
    """N1: Phase-shuffle. Randomly permute packet_phase labels within folio.
    Returns (tokens, shuffled_phases dict {line_key: new_phase})."""
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
    """N2: Token-shuffle. Shuffle all tokens within folio, keep original line/phase structure."""
    # Collect all contributions
    all_contribs = [list(tok['contributions']) for tok in tokens]
    rng.shuffle(all_contribs)

    shuffled = []
    for i, tok in enumerate(tokens):
        nt = dict(tok)
        nt['contributions'] = all_contribs[i]
        shuffled.append(nt)
    return shuffled


def null_n3_cross_folio(tokens, folio, other_folio_tokens):
    """N3: Cross-folio. Use supervisory tokens from a different folio.
    Returns list of tokens with contributions from other_folio."""
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
# Build helpers for baselines
# ---------------------------------------------------------------------------

def build_sensitivity_scaled_apparatus(profile_name, config_mode, scale):
    """Build apparatus with sensitivity scaled by given factor."""
    app = build_configured_apparatus(profile_name, config_mode)
    for sv in STATE_VARS:
        app.sensitivity[sv] *= scale
    return app


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: Event Null Executor")
    print("Phase 569 - EVENTIVE_CLOSURE_PACKETS")
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

    with open(COF_PATH, 'r', encoding='utf-8') as f:
        cof_data = json.load(f)

    with open(EVENT_TAX_PATH, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']
    section_thresholds = event_taxonomy['section_thresholds']
    print(f"  Event map entries: {len(event_map)}")
    print(f"  Section thresholds: {list(section_thresholds.keys())}")

    # Budget data (for profile assignment)
    with open(BUDGET_PATH, 'r', encoding='utf-8') as f:
        budgets = json.load(f)

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    print(f"  Unique folios in T2b: {len(tokens_by_folio)}")

    # --- Pilot folios ---
    pilot_folio_list = sorted(PILOT_FOLIOS)
    print(f"\nPilot folios: {len(pilot_folio_list)}")

    # --- Preferred profiles and config modes ---
    folio_infra = compute_infra_scores(PILOT_FOLIOS)
    for folio in pilot_folio_list:
        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        n_toks = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: profile={profile}, config={config_mode}, n_tokens={n_toks}")

    # Common trace kwargs
    def make_trace_kwargs():
        return dict(
            line_packets=line_packets,
            line_cts_map=line_cts_map,
            event_map=event_map,
            section_thresholds=section_thresholds,
        )

    # =====================================================================
    # REFERENCE RUNS (20 folios, preferred profile)
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

        result = run_event_trace(apparatus, toks, **make_trace_kwargs())

        reference[folio] = {
            'profile': profile,
            'metrics': result['metrics'],
            'events_by_type': result['events_by_type'],
            'events_by_demand': result['events_by_demand'],
            'events_by_type_demand': result['events_by_type_demand'],
            'per_event_detail': result['per_event_detail'],
        }
        run_count += 1

        m = result['metrics']
        n_events = sum(e['count'] for e in result['events_by_type'].values()
                       if e.get('count', 0) > 0)
        eir_any = result['events_by_type'].get('E_any', {}).get('EIR', 0.0)
        print(f"  {folio}: PCV={m['PCV']:.4f}, WCU={m['WCU']:.4f}, "
              f"events={n_events}, EIR_any={eir_any:.3f}")

    # =====================================================================
    # BASELINES (10 types x 20 folios = 200 runs)
    # =====================================================================
    print("\n" + "=" * 70)
    print("BASELINES (10 types x 20 folios = 200 runs)")
    print("=" * 70)

    baselines = {f'B{i}': {} for i in range(1, 11)}

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tk = make_trace_kwargs()

        # B1: No apparatus (state unchanged)
        r = run_event_trace(None, toks, **tk)
        baselines['B1'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B2: Random walk (small random dV)
        rw_rng = random.Random(42)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, random_walk_rng=rw_rng, **tk)
        baselines['B2'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B3: Equilibrium pull (weak pull toward 0.5)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, equil_pull=True, **tk)
        baselines['B3'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B4: No close recovery apparatus
        apparatus = build_no_close_recovery_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, **tk)
        baselines['B4'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B5: Halved gains (sensitivity x 0.5)
        apparatus = build_sensitivity_scaled_apparatus(profile, config_mode, 0.5)
        r = run_event_trace(apparatus, toks, **tk)
        baselines['B5'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B6: Doubled gains (sensitivity x 2.0)
        apparatus = build_sensitivity_scaled_apparatus(profile, config_mode, 2.0)
        r = run_event_trace(apparatus, toks, **tk)
        baselines['B6'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B7: Inverted CTS (1 - cts)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, invert_cts=True, **tk)
        baselines['B7'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B8: Zero CTS (cts=0 always)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, disable_cts=True, **tk)
        baselines['B8'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B9: Shuffled dV (randomly permute dV components within each token)
        sdv_rng = random.Random(42)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, shuffle_dv_rng=sdv_rng, **tk)
        baselines['B9'][folio] = {'metrics': r['metrics'],
                                   'events_by_type': r['events_by_type'],
                                   'events_by_demand': r['events_by_demand']}
        run_count += 1

        # B10: No close recovery (same as B4 but tracked separately)
        apparatus = build_no_close_recovery_apparatus(profile, config_mode)
        r = run_event_trace(apparatus, toks, **tk)
        baselines['B10'][folio] = {'metrics': r['metrics'],
                                    'events_by_type': r['events_by_type'],
                                    'events_by_demand': r['events_by_demand']}
        run_count += 1

        elapsed = time.time() - t0
        print(f"  Baselines {folio} done ({run_count} runs, {elapsed:.1f}s)")

    # Print baseline summary
    print("\n  Baseline summary:")
    for bname in sorted(baselines.keys(), key=lambda x: int(x[1:])):
        bdata = baselines[bname]
        if bdata:
            pcv_vals = [bdata[f]['metrics']['PCV'] for f in bdata]
            mean_pcv = sum(pcv_vals) / len(pcv_vals)
            eir_vals = [bdata[f]['events_by_type'].get('E_any', {}).get('EIR', 0.0)
                        for f in bdata]
            mean_eir = sum(eir_vals) / len(eir_vals) if eir_vals else 0.0
            print(f"    {bname}: mean_PCV={mean_pcv:.4f}, mean_EIR_any={mean_eir:.3f}, "
                  f"n_folios={len(bdata)}")

    # =====================================================================
    # NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)
    # =====================================================================
    print("\n" + "=" * 70)
    print("NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)")
    print("=" * 70)

    N_PERMS = 50

    # Metric keys to accumulate
    METRIC_KEYS = [
        'old_viability', 'old_y_final', 'PCV', 'SAHB', 'REF_mean',
        'REF_eligible_fraction', 'QGY', 'qgy_ratio', 'WCU', 'SLR_mean',
        'SLR_eligible_fraction', 'UEB', 'WCP', 'WCP_full_packet_mean', 'EWP',
    ]

    # Event type keys
    EVENT_TYPES = ['E_any', 'E_armed', 'E_compound', 'E_cts50',
                   'E_decisive', 'E_mcb', 'E_opaque', 'E_opaque_decisive']
    EVENT_METRICS = ['EIR', 'mean_ERM', 'mean_ESQ', 'mean_EW']

    null_runs = {
        'N1': {'all_perms': {}, 'mean': {}},
        'N2': {'all_perms': {}, 'mean': {}},
        'N3': {'all_perms': {}, 'mean': {}},
        'N4': {'all_perms': {}, 'mean': {}},
    }

    # Build cross-folio lookup for N3
    other_folio_cycle = {}
    for i, folio in enumerate(pilot_folio_list):
        # Use next folio in cyclic order (excluding self)
        others = [f for f in pilot_folio_list if f != folio]
        other_folio_cycle[folio] = others

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = get_preferred_profile(folio)
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tk = make_trace_kwargs()

        # Initialize per-folio storage for all null types
        for nn in null_runs:
            null_runs[nn]['all_perms'][folio] = []

        for perm_idx in range(N_PERMS):
            seed = 42 + perm_idx

            # --- N1: Phase shuffle ---
            rng1 = random.Random(seed)
            n1_toks, shuffled_phases = null_n1_phase_shuffle(toks, line_packets, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_event_trace(apparatus, n1_toks, shuffled_phases=shuffled_phases, **tk)
            null_runs['N1']['all_perms'][folio].append({
                'metrics': r1['metrics'],
                'events_by_type_phase_native': r1['events_by_type'],
                'events_by_type_structure_native': r1['events_by_type_structure_native'],
            })
            run_count += 1

            # --- N2: Token shuffle ---
            rng2 = random.Random(seed)
            n2_toks = null_n2_token_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_event_trace(apparatus, n2_toks, **tk)
            null_runs['N2']['all_perms'][folio].append({
                'metrics': r2['metrics'],
                'events_by_type_phase_native': r2['events_by_type'],
                'events_by_type_structure_native': r2['events_by_type_structure_native'],
            })
            run_count += 1

            # --- N3: Cross-folio ---
            rng3 = random.Random(seed)
            others = other_folio_cycle[folio]
            other_folio = others[perm_idx % len(others)]
            other_toks = tokens_by_folio.get(other_folio, [])
            n3_toks = null_n3_cross_folio(toks, folio, other_toks)
            apparatus = build_configured_apparatus(profile, config_mode)
            r3 = run_event_trace(apparatus, n3_toks, **tk)
            null_runs['N3']['all_perms'][folio].append({
                'metrics': r3['metrics'],
                'events_by_type_phase_native': r3['events_by_type'],
                'events_by_type_structure_native': r3['events_by_type_structure_native'],
            })
            run_count += 1

            # --- N4: dV permutation ---
            rng4 = random.Random(seed)
            n4_toks = null_n4_dv_permutation(toks, rng4)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_event_trace(apparatus, n4_toks, **tk)
            null_runs['N4']['all_perms'][folio].append({
                'metrics': r4['metrics'],
                'events_by_type_phase_native': r4['events_by_type'],
                'events_by_type_structure_native': r4['events_by_type_structure_native'],
            })
            run_count += 1

            if run_count % 100 == 0:
                elapsed = time.time() - t0
                print(f"  Progress: {run_count} runs, {elapsed:.1f}s "
                      f"(folio={folio}, perm={perm_idx + 1}/{N_PERMS})")

        elapsed = time.time() - t0
        print(f"  N1-N4 {folio} done ({run_count} total runs, {elapsed:.1f}s)")

    # --- Compute null means ---
    print("\nComputing null means...")
    for nn in null_runs:
        for folio in null_runs[nn]['all_perms']:
            perms = null_runs[nn]['all_perms'][folio]
            n_p = len(perms)
            if n_p == 0:
                continue

            # Average metrics
            mean_metrics = {}
            for mk in METRIC_KEYS:
                vals = [p['metrics'][mk] for p in perms]
                mean_metrics[mk] = round(sum(vals) / n_p, 6)

            # Average event metrics (phase-native)
            mean_events_pn = {}
            for etype in EVENT_TYPES:
                counts = [p['events_by_type_phase_native'].get(etype, {}).get('count', 0)
                          for p in perms]
                eirs = [p['events_by_type_phase_native'].get(etype, {}).get('EIR', 0.0)
                        for p in perms if etype in p['events_by_type_phase_native']]
                erms = [p['events_by_type_phase_native'].get(etype, {}).get('mean_ERM', 0.0)
                        for p in perms if etype in p['events_by_type_phase_native']]
                esqs = [p['events_by_type_phase_native'].get(etype, {}).get('mean_ESQ', 0.0)
                        for p in perms if etype in p['events_by_type_phase_native']]
                ews = [p['events_by_type_phase_native'].get(etype, {}).get('mean_EW', 0.0)
                       for p in perms if etype in p['events_by_type_phase_native']]

                mean_count = round(sum(counts) / n_p, 6)
                if len(eirs) > 0:
                    mean_events_pn[etype] = {
                        'count': mean_count,
                        'EIR': round(sum(eirs) / len(eirs), 6),
                        'mean_ERM': round(sum(erms) / len(erms), 6),
                        'mean_ESQ': round(sum(esqs) / len(esqs), 6),
                        'mean_EW': round(sum(ews) / len(ews), 6),
                    }

            # Average event metrics (structure-native)
            mean_events_sn = {}
            for etype in EVENT_TYPES:
                counts = [p['events_by_type_structure_native'].get(etype, {}).get('count', 0)
                          for p in perms]
                eirs = [p['events_by_type_structure_native'].get(etype, {}).get('EIR', 0.0)
                        for p in perms if etype in p['events_by_type_structure_native']]
                erms = [p['events_by_type_structure_native'].get(etype, {}).get('mean_ERM', 0.0)
                        for p in perms if etype in p['events_by_type_structure_native']]
                esqs = [p['events_by_type_structure_native'].get(etype, {}).get('mean_ESQ', 0.0)
                        for p in perms if etype in p['events_by_type_structure_native']]
                ews = [p['events_by_type_structure_native'].get(etype, {}).get('mean_EW', 0.0)
                       for p in perms if etype in p['events_by_type_structure_native']]

                mean_count = round(sum(counts) / n_p, 6)
                if len(eirs) > 0:
                    mean_events_sn[etype] = {
                        'count': mean_count,
                        'EIR': round(sum(eirs) / len(eirs), 6),
                        'mean_ERM': round(sum(erms) / len(erms), 6),
                        'mean_ESQ': round(sum(esqs) / len(esqs), 6),
                        'mean_EW': round(sum(ews) / len(ews), 6),
                    }

            null_runs[nn]['mean'][folio] = {
                'metrics': mean_metrics,
                'events_by_type_phase_native': mean_events_pn,
                'events_by_type_structure_native': mean_events_sn,
            }

    # Print null summary
    print("\n  Null summary:")
    for nn in sorted(null_runs.keys()):
        mean_data = null_runs[nn]['mean']
        if not mean_data:
            continue
        pcv_means = [mean_data[f]['metrics']['PCV'] for f in mean_data]
        eir_means = [mean_data[f]['events_by_type_phase_native'].get('E_any', {}).get('EIR', 0.0)
                     for f in mean_data]
        if pcv_means:
            overall_pcv = sum(pcv_means) / len(pcv_means)
            overall_eir = sum(eir_means) / len(eir_means) if eir_means else 0.0
            print(f"    {nn}: mean_PCV={overall_pcv:.4f}, "
                  f"mean_EIR_any={overall_eir:.3f}, n_folios={len(pcv_means)}")

    # =====================================================================
    # Assemble output
    # =====================================================================
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': 569,
            'script': 't3_event_null_executor.py',
            'n_reference_runs': len(reference),
            'n_baseline_runs': sum(len(v) for v in baselines.values()),
            'n_null_runs': N_PERMS * 4 * len(pilot_folio_list),
            'total_runs': run_count,
            'n_perms': N_PERMS,
            'n_pilot_folios': len(pilot_folio_list),
            'elapsed_seconds': round(elapsed, 2),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'baseline_descriptions': {
                'B1': 'No apparatus (state unchanged)',
                'B2': 'Random walk (small random dV)',
                'B3': 'Equilibrium pull (weak pull toward 0.5)',
                'B4': 'No close recovery apparatus',
                'B5': 'Halved gains (sensitivity x 0.5)',
                'B6': 'Doubled gains (sensitivity x 2.0)',
                'B7': 'Inverted CTS (1 - cts)',
                'B8': 'Zero CTS (cts=0 always)',
                'B9': 'Shuffled dV (permute dV components per token)',
                'B10': 'No close recovery (tracked separately)',
            },
            'null_descriptions': {
                'N1': 'Phase-shuffle (permute packet_phase labels within folio)',
                'N2': 'Token-shuffle (shuffle token contributions within folio)',
                'N3': 'Cross-folio (use contributions from different folio)',
                'N4': 'dV permutation (permute 7 components of each dV vector)',
            },
            'preferred_profiles': {f: get_preferred_profile(f) for f in pilot_folio_list},
        },
        'reference': reference,
        'baselines': baselines,
        'nulls': {
            nn: {
                'mean': null_runs[nn]['mean'],
                'all_perms': null_runs[nn]['all_perms'],
            }
            for nn in sorted(null_runs.keys())
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

    # --- Reference vs Null comparison ---
    nnames = ['N1', 'N2', 'N3', 'N4']
    bnames = [f'B{i}' for i in range(1, 11)]

    print(f"\n  Key Metrics: Reference vs Nulls (mean across folios):")
    key_metrics = ['PCV', 'WCU', 'SLR_mean', 'UEB', 'WCP', 'EWP']
    header = f"  {'Metric':<22} {'Ref':>8}"
    for nn in nnames:
        header += f" {nn:>8}"
    print(header)
    print(f"  {'-' * 22} {'-' * 8}" + (' ' + '-' * 8) * 4)

    for mk in key_metrics:
        ref_vals = [reference[f]['metrics'][mk] for f in pilot_folio_list if f in reference]
        if not ref_vals:
            continue
        ref_mean = sum(ref_vals) / len(ref_vals)
        row = f"  {mk:<22} {ref_mean:>8.4f}"
        for nn in nnames:
            null_vals = [null_runs[nn]['mean'].get(f, {}).get('metrics', {}).get(mk, 0.0)
                         for f in pilot_folio_list if f in reference]
            null_mean = sum(null_vals) / len(null_vals) if null_vals else 0.0
            row += f" {null_mean:>8.4f}"
        print(row)

    # --- Event success: Reference vs Null ---
    print(f"\n  Event Success (EIR) by Type: Reference vs Nulls:")
    for etype in EVENT_TYPES:
        ref_eirs = [reference[f]['events_by_type'].get(etype, {}).get('EIR', None)
                    for f in pilot_folio_list if f in reference]
        ref_eirs = [v for v in ref_eirs if v is not None]
        if not ref_eirs:
            continue
        ref_mean_eir = sum(ref_eirs) / len(ref_eirs)
        row = f"    {etype:<22} ref={ref_mean_eir:>6.3f}"
        for nn in nnames:
            null_eirs = [null_runs[nn]['mean'].get(f, {}).get(
                'events_by_type_phase_native', {}).get(etype, {}).get('EIR', None)
                for f in pilot_folio_list if f in reference]
            null_eirs = [v for v in null_eirs if v is not None]
            null_mean_eir = sum(null_eirs) / len(null_eirs) if null_eirs else 0.0
            row += f"  {nn}={null_mean_eir:>6.3f}"
        print(row)

    # --- B4/B10 delta (close recovery ablation) ---
    print(f"\n  B4/B10 Event Impact (Ref - B4 EIR by type):")
    for etype in EVENT_TYPES:
        ref_eirs = [reference[f]['events_by_type'].get(etype, {}).get('EIR', None)
                    for f in pilot_folio_list if f in reference]
        b4_eirs = [baselines['B4'].get(f, {}).get('events_by_type', {}).get(
                   etype, {}).get('EIR', None)
                   for f in pilot_folio_list if f in reference]
        pairs = [(r, b) for r, b in zip(ref_eirs, b4_eirs) if r is not None and b is not None]
        if pairs:
            mean_delta = sum(r - b for r, b in pairs) / len(pairs)
            print(f"    {etype:<22} delta_EIR={mean_delta:>+6.3f} (n={len(pairs)})")

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
