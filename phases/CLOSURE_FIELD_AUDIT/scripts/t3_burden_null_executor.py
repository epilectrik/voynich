"""
T3: Burden Null Executor
========================
Phase 567 - CLOSURE_FIELD_AUDIT

Re-runs the same baseline (B1-B10) and null (N1-N4 x 50 perms) configurations
as Phase 566 T3, but computes 6 NEW metrics alongside the old ones:

  PCV  - Packet-Coherence Viability (phase-aware zone desirability)
  SAHB - S-Asymmetric Hazard Burden (skip S warning/hardstop above EQ)
  REF  - Resolved Excursion Fraction (CLOSE recovery effectiveness)
  QGY  - Quality-Gated Y (Y accumulation only when CLOSE + CTS + net improvement)
  CRE  - Corridor Return Efficiency (strict and soft)
  MPZF - Mean Phase-correct Zone Fraction

Total: 10 baselines x 20 folios + 4 nulls x 20 folios x 50 perms
     = 200 + 4000 = 4,200 runs + 20 reference = 4,220 runs

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t1_close_recovery_apparatus.json         (apparatus spec, folio infra scores)
  - t3_line_packets.json                     (line-level packet_phase)
  - regime_folio_mapping.json                (regime assignments for profile)
  - t2_folio_budgets.json                    (folio budgets for profile assignment)

Output:
  - t3_burden_null_runs.json
"""

import json
import sys
import time
import math
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Import close recovery apparatus (Phase 566 T1)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

# Import from 566 T1
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
T1_566_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY'
               / 'results' / 't1_close_recovery_apparatus.json')
PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                / 'results' / 't3_line_packets.json')
REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
BUDGET_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't2_folio_budgets.json')
OUTPUT_PATH = PHASE_DIR / 'results' / 't3_burden_null_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (same as Phase 566 T3)
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

# Excursion tracking thresholds
QUIET_LO, QUIET_HI = 0.4, 0.6
EXCURSION_LO, EXCURSION_HI = 0.35, 0.65
MAX_CYCLE_DURATION = 50

# Process SVs (those with at least one hazard boundary, excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# Profile rotation for B4
PROFILE_ROTATION = {
    'A1_BATH_REFLUX': 'A2_SEALED_RECIRCULATION',
    'A2_SEALED_RECIRCULATION': 'A3_DISTILL_COLLECT',
    'A3_DISTILL_COLLECT': 'A1_BATH_REFLUX',
}

# S and Y indices
S_IDX = SV_INDEX['S']
Y_IDX = SV_INDEX['Y']

# ---------------------------------------------------------------------------
# PCV desirability tables (frozen)
# ---------------------------------------------------------------------------
# Process SVs (T, RC, C, TR, X) — excludes S and Y which have special rules
PCV_PROCESS_SVS = ['T', 'RC', 'C', 'TR', 'X']

PCV_ZONE_SCORES = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

# S asymmetric (above EQ)
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
# UniformRestoringApparatus for B9 (copied from 566 T3)
# ---------------------------------------------------------------------------
class UniformRestoringApparatus:
    """
    Wraps CloseRecoveryApparatus but replaces the 4-zone piecewise
    restoring force with uniform corridor-level restoring everywhere.
    CLOSE recovery channels (R1-R5) remain intact.
    """

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

            rf[i] = (self.base.gamma_corridor[sv] * dev
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
# Sort key
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
# Zone classification for 4-zone tracking
# ---------------------------------------------------------------------------
def _classify_zone(sv, dev_abs):
    """Classify a deviation into one of the 4 zones."""
    q2 = Q2_BASE[sv]
    q3 = q2 + 0.05
    q3 = min(q3, HAZARD_DEV[sv] - 0.01)

    if dev_abs < Q1:
        return 'BASIN'
    elif dev_abs < q2:
        return 'CORRIDOR'
    elif dev_abs < q3:
        return 'WARNING'
    else:
        return 'HARD_STOP'


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
# PCV computation for a single (state, phase) pair — process SVs
# ---------------------------------------------------------------------------
def _pcv_token_score(state, packet_phase):
    """
    Compute PCV score for one token.
    Process SVs (T, RC, C, TR, X): zone-based desirability table.
    S: asymmetric — if S > EQ, use PCV_S_HIGH_SCORES; else zone table.
    Y: excluded.
    Returns (score_sum, count).
    """
    score_sum = 0.0
    count = 0

    phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])

    for sv in PCV_PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, dev)
        # Check hazard
        if dev >= HAZARD_DEV[sv]:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
        count += 1

    # S: asymmetric handling
    s_val = state[S_IDX]
    s_dev = abs(s_val - EQUILIBRIUM)
    if s_val > EQUILIBRIUM:
        # S above EQ — always desirable
        score_sum += PCV_S_HIGH_SCORES.get(packet_phase, 1.0)
    else:
        # S below EQ — use normal zone scoring
        zone = _classify_zone('S', s_dev)
        if s_dev >= HAZARD_DEV['S']:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
    count += 1

    # Y excluded from PCV
    return score_sum, count


# ---------------------------------------------------------------------------
# SAHB computation for a single (state, phase) pair
# ---------------------------------------------------------------------------
def _sahb_token(state, packet_phase):
    """
    Compute SAHB (S-Asymmetric Hazard Burden) components for one token.
    Skip S warning/hardstop when S > EQ.
    Returns (warnings, hardstops, outside_corridor, max_excursion).
    """
    warnings = 0
    hardstops = 0
    outside_corridor = 0
    max_excursion = 0.0

    for sv in PROCESS_SVS:  # Excludes Y
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, dev)

        # S asymmetric: skip penalty when S > EQ
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
# MPZF computation for a single (state, phase) pair
# ---------------------------------------------------------------------------
def _mpzf_token(state, packet_phase):
    """
    Compute MPZF contribution for one token.
    Fraction of (token, SV) pairs in desirable zone for phase.
    S above EQ always correct.
    Returns (correct_count, total_count).
    """
    correct = 0
    total = 0

    phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])

    for sv in PCV_PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, dev)

        # "Desirable" = zone score >= 0.8
        if dev >= HAZARD_DEV[sv]:
            score = phase_scores.get('HAZARD', 0.0)
        else:
            score = phase_scores.get(zone, 0.0)
        if score >= 0.8:
            correct += 1
        total += 1

    # S
    s_val = state[S_IDX]
    if s_val > EQUILIBRIUM:
        correct += 1  # S above EQ always correct
    else:
        s_dev = abs(s_val - EQUILIBRIUM)
        zone = _classify_zone('S', s_dev)
        if s_dev >= HAZARD_DEV['S']:
            score = phase_scores.get('HAZARD', 0.0)
        else:
            score = phase_scores.get(zone, 0.0)
        if score >= 0.8:
            correct += 1
    total += 1

    return correct, total


# ---------------------------------------------------------------------------
# Core execution function with new metrics
# ---------------------------------------------------------------------------
def run_burden_trace(apparatus, tokens, line_packets,
                     disable_routing=False, disable_cts=False,
                     disable_discharge=False, force_phase=None,
                     override_contributions=None,
                     override_permissivity=None):
    """
    Run one folio through the close recovery apparatus with routing buffer.
    Computes OLD metrics (viability, Y_final, zone_occupancy, contacts)
    plus 6 NEW metrics (PCV, SAHB, REF, QGY, CRE, MPZF).

    Returns dict with all metrics.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'old_viability': 1.0,
            'old_y_final': 0.5,
            'n_hazard_events': 0,
            'warning_contacts': 0,
            'hard_stop_contacts': 0,
            'PCV': 1.0,
            'SAHB': 0.0,
            'REF_mean': 0.0,
            'REF_eligible_fraction': 0.0,
            'REF_worsened_fraction': 0.0,
            'QGY': 0.0,
            'qgy_ratio': 0.0,
            'CRE_strict': 0.0,
            'CRE_soft': 0.0,
            'MPZF': 1.0,
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    permissivity_buffer = {}
    prev_line = None

    # OLD accumulators
    n_viable = 0
    hazard_count = 0
    warning_contacts = 0
    hard_stop_contacts = 0

    # Zone occupancy tracking (4-zone, per SV)
    zone_counts = {sv: {'BASIN': 0, 'CORRIDOR': 0, 'WARNING': 0, 'HARD_STOP': 0}
                   for sv in STATE_VARS}

    # --- NEW metric accumulators ---

    # PCV
    pcv_score_sum = 0.0
    pcv_count = 0

    # SAHB
    sahb_warnings = 0
    sahb_hardstops = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # REF: track per-line work_end and close_end deviations
    # We need to know when WORK phase ends and CLOSE phase ends per line
    # Track state at end of WORK and end of CLOSE for each line
    line_work_end_devs = {}   # line -> [dev per SV]
    line_close_end_devs = {}  # line -> [dev per SV]
    line_phases = defaultdict(list)  # line -> list of (tok_idx, phase)

    # QGY
    qgy_total = 0.0
    qgy_count = 0  # total CLOSE tokens
    prev_aggregate_dev = None  # Track net aggregate deviation

    # CRE: per-SV excursion tracking for corridor return
    # When dev exceeds Q2 during WORK, track if it returns below Q2 during CLOSE
    cre_excursions = []  # list of {sv, work_peak, returned_strict, returned_soft}
    sv_cre_state = {sv: {'active': False, 'peak_dev': 0.0, 'close_started': False,
                         'returned_strict': False, 'returned_soft': False}
                    for sv in PROCESS_SVS}

    # MPZF
    mpzf_correct = 0
    mpzf_total = 0

    # Per-line tracking for REF
    current_line_work_end_state = None
    current_line_close_end_state = None
    current_line_key = None

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok.get('folio', '')

        # Save pre-update state
        pre_state = list(state)

        # 1. Reset routing buffers at line boundaries
        if current_line != prev_line:
            # Save REF data for previous line if it exists
            if prev_line is not None and current_line_key is not None:
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

            routing_contrib_buffer = [0.0] * N_VARS
            permissivity_buffer = {}
            prev_line = current_line
            current_line_key = f"{folio}|{current_line}"
            current_line_work_end_state = None
            current_line_close_end_state = None

            # Reset CRE close_started flags for new line
            for sv in PROCESS_SVS:
                if sv_cre_state[sv]['active']:
                    sv_cre_state[sv]['close_started'] = False

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

        # 4. Get CTS from token (unless disabled)
        cts = 0.0 if disable_cts else tok.get('cts', 0.0)

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
        if override_permissivity == 'zero':
            perm = None
        elif not disable_routing and permissivity_buffer:
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
                rf, zones = apparatus._uniform_restoring_force(state, packet_phase)
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
                    'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
                    'discharge_events': [],
                    'close_recovery': recovery_details,
                }
            else:
                cc_raw = apparatus._cross_coupling(state, packet_phase)
                bias = apparatus.equil_bias[packet_phase]
                cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]
                rf, zones = apparatus._restoring_force(state, packet_phase, perm)
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
                    'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
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

        # ---- OLD METRICS ----

        # 9. Zone occupancy tracking (4-zone)
        zones = diagnostics.get('zones', {})
        token_has_warning = False
        token_has_hard_stop = False
        for sv in STATE_VARS:
            z = zones.get(sv, 'CORRIDOR')
            if z in zone_counts[sv]:
                zone_counts[sv][z] += 1
            if z == 'WARNING':
                token_has_warning = True
            elif z == 'HARD_STOP':
                token_has_hard_stop = True

        if token_has_warning:
            warning_contacts += 1
        if token_has_hard_stop:
            hard_stop_contacts += 1

        # 10. Hazard check (old viability)
        if is_in_bounds(state):
            n_viable += 1
        else:
            hazard_count += 1

        # ---- NEW METRICS ----

        # 11. PCV (Packet-Coherence Viability)
        pcv_s, pcv_c = _pcv_token_score(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_count += pcv_c

        # 12. SAHB (S-Asymmetric Hazard Burden)
        sw, sh, soc, sme = _sahb_token(state, packet_phase)
        sahb_warnings += sw
        sahb_hardstops += sh
        sahb_outside_corridor += soc
        if sme > sahb_max_excursion:
            sahb_max_excursion = sme

        # 13. MPZF
        mc, mt = _mpzf_token(state, packet_phase)
        mpzf_correct += mc
        mpzf_total += mt

        # 14. REF tracking: save state at end of each phase per line
        if packet_phase == 'WORK':
            current_line_work_end_state = list(state)
        elif packet_phase == 'CLOSE':
            current_line_close_end_state = list(state)

        # 15. QGY (Quality-Gated Y)
        if packet_phase == 'CLOSE':
            qgy_count += 1
            # Compute current aggregate deviation
            current_aggregate_dev = sum(abs(state[i] - EQUILIBRIUM)
                                        for i in range(N_VARS) if i != Y_IDX)
            if cts > 0.3 and prev_aggregate_dev is not None:
                if current_aggregate_dev < prev_aggregate_dev:
                    # Net improvement — count Y increment
                    y_increment = state[Y_IDX] - pre_state[Y_IDX]
                    if y_increment > 0:
                        qgy_total += y_increment
            prev_aggregate_dev = current_aggregate_dev
        else:
            # Reset aggregate tracking when leaving CLOSE
            prev_aggregate_dev = None

        # 16. CRE tracking
        for sv in PROCESS_SVS:
            si = SV_INDEX[sv]
            dev_abs = abs(state[si] - EQUILIBRIUM)
            q2_sv = Q2_BASE[sv]

            if not sv_cre_state[sv]['active']:
                # Enter excursion when WORK phase and dev exceeds Q2
                if packet_phase == 'WORK' and dev_abs > q2_sv:
                    sv_cre_state[sv]['active'] = True
                    sv_cre_state[sv]['peak_dev'] = dev_abs
                    sv_cre_state[sv]['close_started'] = False
                    sv_cre_state[sv]['returned_strict'] = False
                    sv_cre_state[sv]['returned_soft'] = False
            else:
                # Track peak
                if dev_abs > sv_cre_state[sv]['peak_dev']:
                    sv_cre_state[sv]['peak_dev'] = dev_abs

                if packet_phase == 'CLOSE':
                    sv_cre_state[sv]['close_started'] = True
                    # CRE_strict: return below Q2 within CLOSE window
                    if dev_abs < q2_sv:
                        sv_cre_state[sv]['returned_strict'] = True

                # CRE_soft: return below Q2 by line end (any phase after excursion)
                if dev_abs < q2_sv:
                    sv_cre_state[sv]['returned_soft'] = True

                # If we've entered a new WORK phase after CLOSE, finalize this excursion
                if packet_phase == 'WORK' and sv_cre_state[sv]['close_started']:
                    cre_excursions.append({
                        'sv': sv,
                        'peak_dev': sv_cre_state[sv]['peak_dev'],
                        'returned_strict': sv_cre_state[sv]['returned_strict'],
                        'returned_soft': sv_cre_state[sv]['returned_soft'],
                    })
                    sv_cre_state[sv]['active'] = False

    # Finalize last line REF data
    if current_line_key is not None:
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

    # Finalize any still-active CRE excursions
    for sv in PROCESS_SVS:
        if sv_cre_state[sv]['active']:
            cre_excursions.append({
                'sv': sv,
                'peak_dev': sv_cre_state[sv]['peak_dev'],
                'returned_strict': sv_cre_state[sv]['returned_strict'],
                'returned_soft': sv_cre_state[sv]['returned_soft'],
            })

    # === Compute final metrics ===

    # Old viability
    old_viability = round(n_viable / n_tokens, 6) if n_tokens > 0 else 1.0

    # Old Y_final
    old_y_final = round(state[Y_IDX], 6)

    # PCV
    pcv = round(pcv_score_sum / pcv_count, 6) if pcv_count > 0 else 1.0

    # SAHB: 1.0*warnings + 3.0*hardstops + 0.5*outside_corridor + 2.0*max_excursion
    sahb = round(
        SAHB_WARNING_WEIGHT * sahb_warnings
        + SAHB_HARDSTOP_WEIGHT * sahb_hardstops
        + SAHB_OUTSIDE_CORRIDOR_WEIGHT * sahb_outside_corridor
        + SAHB_MAX_EXCURSION_WEIGHT * sahb_max_excursion,
        6
    )
    # Normalize by n_tokens so it's comparable across folios of different lengths
    sahb_norm = round(sahb / n_tokens, 6) if n_tokens > 0 else 0.0

    # REF: Resolved Excursion Fraction
    ref_eligible = 0
    ref_resolved_sum = 0.0
    ref_worsened = 0
    for line_key in line_work_end_devs:
        if line_key not in line_close_end_devs:
            continue
        work_devs = line_work_end_devs[line_key]
        close_devs = line_close_end_devs[line_key]
        for i in range(N_VARS):
            if i == Y_IDX:
                continue  # Skip Y
            work_end_dev = work_devs[i]
            close_end_dev = close_devs[i]
            if work_end_dev > Q1:
                ref_eligible += 1
                ref_val = 1.0 - (close_end_dev / work_end_dev) if work_end_dev > 1e-10 else 0.0
                ref_resolved_sum += ref_val
                if close_end_dev > work_end_dev:
                    ref_worsened += 1

    ref_mean = round(ref_resolved_sum / ref_eligible, 6) if ref_eligible > 0 else 0.0
    total_lines_with_both = sum(1 for lk in line_work_end_devs if lk in line_close_end_devs)
    total_possible_ref = total_lines_with_both * (N_VARS - 1)  # Exclude Y
    ref_eligible_fraction = round(ref_eligible / total_possible_ref, 6) if total_possible_ref > 0 else 0.0
    ref_worsened_fraction = round(ref_worsened / ref_eligible, 6) if ref_eligible > 0 else 0.0

    # QGY
    qgy = round(qgy_total, 6)
    qgy_ratio = round(qgy_total / state[Y_IDX], 6) if state[Y_IDX] > 1e-10 else 0.0

    # CRE
    n_cre = len(cre_excursions)
    if n_cre > 0:
        cre_strict = round(sum(1 for e in cre_excursions if e['returned_strict']) / n_cre, 6)
        cre_soft = round(sum(1 for e in cre_excursions if e['returned_soft']) / n_cre, 6)
    else:
        cre_strict = 0.0
        cre_soft = 0.0

    # MPZF
    mpzf = round(mpzf_correct / mpzf_total, 6) if mpzf_total > 0 else 1.0

    return {
        'old_viability': old_viability,
        'old_y_final': old_y_final,
        'n_hazard_events': hazard_count,
        'warning_contacts': warning_contacts,
        'hard_stop_contacts': hard_stop_contacts,
        'PCV': pcv,
        'SAHB': sahb_norm,
        'REF_mean': ref_mean,
        'REF_eligible_fraction': ref_eligible_fraction,
        'REF_worsened_fraction': ref_worsened_fraction,
        'QGY': qgy,
        'qgy_ratio': qgy_ratio,
        'CRE_strict': cre_strict,
        'CRE_soft': cre_soft,
        'MPZF': mpzf,
    }


# ---------------------------------------------------------------------------
# Null model generators (same as 566 T3)
# ---------------------------------------------------------------------------

def null_n1_phase_shuffle(tokens, rng):
    """N1: Phase-shuffled. Random phase assignment, same dV magnitudes."""
    shuffled = list(tokens)
    rng.shuffle(shuffled)
    for i, orig in enumerate(tokens):
        shuffled[i] = dict(shuffled[i])
        shuffled[i]['line'] = orig['line']
        shuffled[i]['line_pos'] = orig['line_pos']
        shuffled[i]['folio'] = orig['folio']
    return shuffled


def null_n2_contribution_shuffle(tokens, rng):
    """N2: Contribution-shuffled. Random SV assignment for each contribution."""
    shuffled = [dict(t) for t in tokens]
    for tok in shuffled:
        contribs = list(tok['contributions'])
        rng.shuffle(contribs)
        tok['contributions'] = contribs
    return shuffled


def null_n3_cross_folio(tokens, all_tokens_by_folio, rng, target_folio):
    """N3: Cross-folio. Apply a different folio's contributions."""
    available_folios = [f for f in all_tokens_by_folio
                        if f != target_folio and len(all_tokens_by_folio[f]) > 0]
    if not available_folios:
        return tokens

    source_folio = rng.choice(available_folios)
    source_toks = all_tokens_by_folio[source_folio]

    n_source = len(source_toks)
    result = []
    for i, orig_tok in enumerate(tokens):
        nt = dict(orig_tok)
        src_idx = i % n_source
        nt['contributions'] = list(source_toks[src_idx]['contributions'])
        nt['cts'] = source_toks[src_idx].get('cts', 0.0)
        nt['routing_active'] = source_toks[src_idx].get('routing_active', False)
        nt['routing_terminal'] = source_toks[src_idx].get('routing_terminal', None)
        result.append(nt)

    return result


def null_n4_random_walk(tokens, rng):
    """N4: Random walk. Random dV magnitudes with same distribution."""
    all_values = []
    for tok in tokens:
        for v in tok['contributions']:
            all_values.append(v)

    shuffled = [dict(t) for t in tokens]
    rng.shuffle(all_values)

    idx = 0
    for tok in shuffled:
        new_contribs = []
        for _ in range(N_VARS):
            new_contribs.append(all_values[idx % len(all_values)])
            idx += 1
        tok['contributions'] = new_contribs

    return shuffled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: Burden Null Executor")
    print("Phase 567 - CLOSURE_FIELD_AUDIT")
    print("=" * 70)

    # --- Load inputs ---
    print("\nLoading inputs...")

    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"  T2b tokens: {len(all_tokens)}")

    with open(T1_566_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    infra_scores = t1_data['folio_infra_scores']
    print(f"  566 infra scores: {len(infra_scores)} folios")

    with open(PACKETS_PATH, 'r', encoding='utf-8') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    # --- Load folio profile assignments ---
    print("\n  Loading folio profile assignments...")
    folio_assignments = assign_folio_profiles(REGIME_PATH, BUDGET_PATH)
    print(f"  Folio assignments: {len(folio_assignments)}")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    print(f"  Unique folios in T2b: {len(tokens_by_folio)}")

    # --- Pre-compute folio mean contributions ---
    print("\nPre-computing folio means...")
    folio_contrib_sums = defaultdict(lambda: [0.0] * N_VARS)
    folio_contrib_counts = defaultdict(int)
    for tok in all_tokens:
        fid = tok['folio']
        contribs = tok['contributions']
        for i in range(N_VARS):
            folio_contrib_sums[fid][i] += contribs[i]
        folio_contrib_counts[fid] += 1

    folio_mean_contribs = {}
    for fid in folio_contrib_sums:
        n = folio_contrib_counts[fid]
        folio_mean_contribs[fid] = [folio_contrib_sums[fid][i] / n for i in range(N_VARS)]
    print(f"  Folio mean contribs: {len(folio_mean_contribs)} folios")

    # --- Determine preferred profile and config mode for each pilot folio ---
    pilot_folio_list = sorted(PILOT_FOLIOS)
    print(f"\nPilot folios: {len(pilot_folio_list)}")

    folio_profile = {}
    folio_config_mode = {}
    for folio in pilot_folio_list:
        assignment = folio_assignments.get(folio, {})
        profile = assignment.get('preferred_profile', 'A2_SEALED_RECIRCULATION')
        folio_profile[folio] = profile

        infra = infra_scores.get(folio, {})
        config_mode = infra.get('config_mode', 'H1_MEDIUM_INFRA')
        folio_config_mode[folio] = config_mode

        n_toks = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"n_tokens={n_toks}")

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

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        apparatus = build_configured_apparatus(profile, config_mode)

        result = run_burden_trace(apparatus, toks, line_packets)
        reference[folio] = result
        run_count += 1

        print(f"  {folio}: old_viab={result['old_viability']:.4f}, "
              f"PCV={result['PCV']:.4f}, SAHB={result['SAHB']:.4f}, "
              f"REF={result['REF_mean']:.4f}, QGY={result['QGY']:.4f}, "
              f"CRE_s={result['CRE_strict']:.4f}, MPZF={result['MPZF']:.4f}")

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

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        folio_mean = folio_mean_contribs.get(folio, [0.0] * N_VARS)

        # --- B1: Flat uniform profile (folio-mean contributions) ---
        b1_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = list(folio_mean)
            b1_toks.append(nt)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, b1_toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B1'].append(r)
        run_count += 1

        # --- B2: Zero contributions ---
        b2_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = [0.0] * N_VARS
            b2_toks.append(nt)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, b2_toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B2'].append(r)
        run_count += 1

        # --- B3: No CTS (CTS forced to 0) ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets, disable_cts=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B3'].append(r)
        run_count += 1

        # --- B4: No routing (wrong profile) ---
        wrong_profile = PROFILE_ROTATION.get(profile, 'A2_SEALED_RECIRCULATION')
        apparatus = build_configured_apparatus(wrong_profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = wrong_profile
        r['original_profile'] = profile
        baseline_runs['B4'].append(r)
        run_count += 1

        # --- B5: No routing permissivity ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets,
                             disable_routing=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B5'].append(r)
        run_count += 1

        # --- B6: Reversed phase sequence (force WORK everywhere) ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets,
                             force_phase='WORK')
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B6'].append(r)
        run_count += 1

        # --- B7: No cross-coupling ---
        apparatus = build_configured_apparatus(profile, config_mode)
        for key in list(apparatus.profile_params.keys()):
            if key.startswith('alpha_'):
                apparatus.profile_params[key] = 0.0
        equil_state = [EQUILIBRIUM] * N_VARS
        apparatus.equil_bias = {}
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = apparatus._cross_coupling(equil_state, phase)
            apparatus.equil_bias[phase] = list(cc_eq)
        r = run_burden_trace(apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B7'].append(r)
        run_count += 1

        # --- B8: No discharge events ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets,
                             disable_discharge=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B8'].append(r)
        run_count += 1

        # --- B9: Uniform restoring (CLOSE recovery intact) ---
        base_apparatus = build_configured_apparatus(profile, config_mode)
        uniform_apparatus = UniformRestoringApparatus(base_apparatus)
        r = run_burden_trace(uniform_apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B9'].append(r)
        run_count += 1

        # --- B10: No CLOSE recovery (R1-R5 disabled) ---
        apparatus = build_no_close_recovery_apparatus(profile, config_mode)
        r = run_burden_trace(apparatus, toks, line_packets)
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
            viabs = [r['old_viability'] for r in bdata]
            pcvs = [r['PCV'] for r in bdata]
            mean_v = sum(viabs) / len(viabs)
            mean_pcv = sum(pcvs) / len(pcvs)
            print(f"    {bname}: mean_viab={mean_v:.4f}, mean_PCV={mean_pcv:.4f}, "
                  f"n_folios={len(viabs)}")

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
        'old_viability', 'PCV', 'SAHB', 'REF_mean', 'REF_eligible_fraction',
        'REF_worsened_fraction', 'QGY', 'qgy_ratio', 'CRE_strict', 'CRE_soft',
        'MPZF', 'old_y_final',
    ]

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]

        # Initialize null result containers
        for null_name in null_runs:
            null_runs[null_name][folio] = {mk: [] for mk in NULL_METRIC_KEYS}

        for perm_idx in range(N_PERMS):
            # --- N1: Phase-shuffled ---
            rng1 = random.Random(42 + perm_idx)
            n1_toks = null_n1_phase_shuffle(toks, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_burden_trace(apparatus, n1_toks, line_packets)
            for mk in NULL_METRIC_KEYS:
                null_runs['N1'][folio][mk].append(r1[mk])
            run_count += 1

            # --- N2: Contribution-shuffled ---
            rng2 = random.Random(42 + perm_idx)
            n2_toks = null_n2_contribution_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_burden_trace(apparatus, n2_toks, line_packets)
            for mk in NULL_METRIC_KEYS:
                null_runs['N2'][folio][mk].append(r2[mk])
            run_count += 1

            # --- N3: Cross-folio ---
            rng3 = random.Random(42 + perm_idx)
            n3_toks = null_n3_cross_folio(toks, tokens_by_folio, rng3, folio)
            apparatus = build_configured_apparatus(profile, config_mode)
            r3 = run_burden_trace(apparatus, n3_toks, line_packets)
            for mk in NULL_METRIC_KEYS:
                null_runs['N3'][folio][mk].append(r3[mk])
            run_count += 1

            # --- N4: Random walk ---
            rng4 = random.Random(42 + perm_idx)
            n4_toks = null_n4_random_walk(toks, rng4)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_burden_trace(apparatus, n4_toks, line_packets)
            for mk in NULL_METRIC_KEYS:
                null_runs['N4'][folio][mk].append(r4[mk])
            run_count += 1

            if perm_idx % 10 == 9:
                elapsed = time.time() - t0
                print(f"  N1-N4 {folio} perm {perm_idx + 1}/50... "
                      f"({run_count} total runs, {elapsed:.1f}s)")

    # Compute null summaries (mean across permutations)
    null_output = {}
    for null_name in null_runs:
        null_output[null_name] = {}
        for folio in null_runs[null_name]:
            entry = null_runs[null_name][folio]
            n_p = len(entry.get('old_viability', []))
            if n_p == 0:
                continue

            summary = {}
            for mk in NULL_METRIC_KEYS:
                vals = entry[mk]
                mean_val = sum(vals) / n_p
                summary[f'mean_{mk}'] = round(mean_val, 6)

            # Also compute std for old_viability
            viabs = entry['old_viability']
            viab_mean = summary['mean_old_viability']
            viab_std = math.sqrt(
                sum((v - viab_mean) ** 2 for v in viabs) / n_p)
            summary['std_old_viability'] = round(viab_std, 6)

            null_output[null_name][folio] = summary

    # Print null summary
    print("\n  Null summary:")
    for null_name in sorted(null_output.keys()):
        folio_data = null_output[null_name]
        if not folio_data:
            continue
        viab_means = [folio_data[f]['mean_old_viability']
                      for f in folio_data if 'mean_old_viability' in folio_data[f]]
        pcv_means = [folio_data[f]['mean_PCV']
                     for f in folio_data if 'mean_PCV' in folio_data[f]]
        if viab_means:
            overall_mean_viab = sum(viab_means) / len(viab_means)
            overall_mean_pcv = sum(pcv_means) / len(pcv_means) if pcv_means else 0.0
            print(f"    {null_name}: mean_viab={overall_mean_viab:.4f}, "
                  f"mean_PCV={overall_mean_pcv:.4f}, n_folios={len(viab_means)}")

    # === Assemble output ===
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': 567,
            'script': 't3_burden_null_executor.py',
            'total_runs': run_count,
            'timestamp': datetime.now().isoformat(),
            'n_baselines': sum(len(v) for v in baseline_runs.values()),
            'n_nulls': N_PERMS * len(null_runs) * len(pilot_folio_list),
            'n_perms': N_PERMS,
            'n_pilot_folios': len(pilot_folio_list),
            'elapsed_seconds': round(elapsed, 2),
            'metrics': ['old_viability', 'PCV', 'SAHB', 'REF_mean',
                        'REF_eligible_fraction', 'REF_worsened_fraction',
                        'QGY', 'qgy_ratio', 'CRE_strict', 'CRE_soft',
                        'MPZF', 'old_y_final'],
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

    # Reference vs baseline comparison (old_viability + PCV)
    bnames = [f'B{i}' for i in range(1, 11)]
    nnames = ['N1', 'N2', 'N3', 'N4']

    print(f"\n  OLD VIABILITY:")
    header_b = ' '.join(f'{b:>7}' for b in bnames)
    header_n = ' '.join(f'{n:>7}' for n in nnames)
    print(f"  {'Folio':<8} {'Ref':>7} | {header_b} | {header_n}")
    divider_b = ' '.join('-' * 7 for _ in bnames)
    divider_n = ' '.join('-' * 7 for _ in nnames)
    print(f"  {'-' * 8} {'-' * 7} | {divider_b} | {divider_n}")

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['old_viability']
        b_vals = []
        for bn in bnames:
            entry = baseline_by_folio[bn].get(folio, {})
            v = entry.get('old_viability', 0.0) if entry else 0.0
            b_vals.append(f"{v:>7.4f}")
        n_vals = []
        for nn in nnames:
            v = null_output[nn].get(folio, {}).get('mean_old_viability', 0.0)
            n_vals.append(f"{v:>7.4f}")
        print(f"  {folio:<8} {ref_v:>7.4f} | {' '.join(b_vals)} | "
              f"{' '.join(n_vals)}")

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

    # --- B10 Delta Analysis (CLOSE recovery ablation, new metrics) ---
    print(f"\n  B10 Deltas (Reference - B10, CLOSE recovery ablation):")
    print(f"  {'Folio':<8} {'dViab':>7} {'dPCV':>7} {'dSAHB':>7} "
          f"{'dREF':>7} {'dQGY':>7} {'dCRE_s':>7} {'dMPZF':>7}")
    print(f"  {'-' * 8} {'-' * 7} {'-' * 7} {'-' * 7} "
          f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7}")

    b10_deltas = {mk: [] for mk in ['old_viability', 'PCV', 'SAHB', 'REF_mean',
                                      'QGY', 'CRE_strict', 'MPZF']}
    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref = reference[folio]
        b10 = baseline_by_folio['B10'].get(folio, {})
        if not b10:
            continue

        deltas = {}
        for mk in b10_deltas:
            d = ref.get(mk, 0.0) - b10.get(mk, 0.0)
            deltas[mk] = d
            b10_deltas[mk].append(d)

        # For SAHB, lower is better, so invert sign for display
        print(f"  {folio:<8} {deltas['old_viability']:>+7.4f} "
              f"{deltas['PCV']:>+7.4f} {-deltas['SAHB']:>+7.4f} "
              f"{deltas['REF_mean']:>+7.4f} {deltas['QGY']:>+7.4f} "
              f"{deltas['CRE_strict']:>+7.4f} {deltas['MPZF']:>+7.4f}")

    if b10_deltas['old_viability']:
        print(f"  {'MEAN':<8}", end='')
        for mk in ['old_viability', 'PCV', 'SAHB', 'REF_mean', 'QGY',
                    'CRE_strict', 'MPZF']:
            vals = b10_deltas[mk]
            mean_d = sum(vals) / len(vals)
            if mk == 'SAHB':
                mean_d = -mean_d  # Invert for display
            print(f" {mean_d:>+7.4f}", end='')
        print()

    # --- B2 Analysis (zero input — shows PCV sensitivity to phase alignment) ---
    print(f"\n  B2 Analysis (zero-input, old_viab always 1.0 but PCV varies):")
    print(f"  {'Folio':<8} {'old_v':>7} {'PCV':>7} {'SAHB':>7} {'MPZF':>7}")
    for folio in pilot_folio_list:
        b2 = baseline_by_folio['B2'].get(folio, {})
        if not b2:
            continue
        print(f"  {folio:<8} {b2['old_viability']:>7.4f} "
              f"{b2['PCV']:>7.4f} {b2['SAHB']:>7.4f} {b2['MPZF']:>7.4f}")

    # --- New metric comparison: Ref vs Null means ---
    print(f"\n  New Metrics: Reference vs Null Means:")
    for mk in ['PCV', 'SAHB', 'REF_mean', 'QGY', 'CRE_strict', 'MPZF']:
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

        n_strs = ' '.join(f'{nn}={null_means[nn]:>7.4f}' for nn in nnames)
        print(f"    {mk:<22} ref={ref_mean:>7.4f}  {n_strs}")

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
