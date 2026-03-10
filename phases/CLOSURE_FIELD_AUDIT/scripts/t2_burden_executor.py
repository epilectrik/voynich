"""
T2: Burden Executor
Phase 567 - CLOSURE_FIELD_AUDIT

Re-runs the same 90 configurations (60 primary + 30 config ablation) as
Phase 566 T2 through the CloseRecoveryApparatus, but computes 6 NEW metrics
alongside the old ones:

  PCV   - Packet-Coherence Viability (phase-aware zone desirability)
  SAHB  - S-Asymmetric Hazard Burden (skips S above EQ)
  REF   - Resolved Excursion Fraction (line-scoped CLOSE effectiveness)
  QGY   - Quality-Gated Y (Y accumulation gated by quality conditions)
  CRE   - Corridor Return Efficiency (strict and soft variants)
  MPZF  - Mean Phase-correct Zone Fraction (binary desirable-zone check)

The plant law is UNCHANGED -- only the readout/scoring is different.
"""

import json
import math
import sys
import time
from pathlib import Path
from datetime import datetime

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
# Constants (same as 566 T2)
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

# Excursion tracking
MAX_CYCLE_DURATION = 50

# Routing permissivity buffer (same as 566)
ROUTING_PERMISSIVITY = {
    'r': {'X': +0.03, 'S': -0.02, 'C': -0.02},
    'y': {'T': +0.03, 'X': -0.02},
    'h': {'TR': +0.03, 'RC': +0.02, 'X': -0.02, 'T': -0.02},
    'm': {'C': +0.03, 'T': -0.02, 'X': -0.02},
    'n': {'S': +0.02, 'X': -0.01},
    'l': {'TR': +0.02, 'S': +0.02, 'X': -0.01},
}

ROUTING_DECAY = 0.7

# S index constant
S_IDX = SV_INDEX['S']
Y_IDX = SV_INDEX['Y']

# ---------------------------------------------------------------------------
# PCV Desirability Table (FROZEN)
# ---------------------------------------------------------------------------
# Process SVs (T, RC, C, TR, X)
PCV_PROCESS = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

# S asymmetric: high-S (S > 0.5) gets a special score per phase
PCV_S = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0, 'HIGH_S': 0.9},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0, 'HIGH_S': 1.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0, 'HIGH_S': 0.9},
}

# MPZF desirable zones per phase (process SVs, exclude Y)
MPZF_DESIRABLE = {
    'WORK':  {'CORRIDOR', 'WARNING'},
    'CLOSE': {'BASIN', 'CORRIDOR'},
    'SPEC':  {'BASIN'},
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_zone(sv, abs_dev):
    """Classify a state variable's deviation into a 5-zone system (BASIN/CORRIDOR/WARNING/HARD_STOP/HAZARD)."""
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
            # S above EQ: use High-S score
            score += PCV_S[packet_phase]['HIGH_S']
        else:
            if sv == 'S':
                score += PCV_S[packet_phase].get(zone, 0.0)
            else:
                score += PCV_PROCESS[packet_phase].get(zone, 0.0)
        count += 1

    return score, count


def _mpzf_score_for_token(state, packet_phase):
    """Compute MPZF binary score for one token across process SVs (excl Y)."""
    correct = 0
    total = 0
    desirable = MPZF_DESIRABLE.get(packet_phase, {'BASIN'})

    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        abs_dev = abs(state[i] - EQUILIBRIUM)
        zone = _classify_zone(sv, abs_dev)

        # S asymmetric: above-EQ S always counts as correct
        if sv == 'S' and state[i] > EQUILIBRIUM:
            correct += 1
        elif zone in desirable:
            correct += 1
        total += 1

    return correct, total


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------

def run_burden_trace(apparatus, tokens, line_packets):
    """
    Run one folio through the CloseRecoveryApparatus with extended metrics.

    apparatus:    CloseRecoveryApparatus instance
    tokens:       list of token dicts, pre-sorted by (line, position)
    line_packets: dict mapping "folio|line" -> packet info

    Returns dict with old metrics + 6 new metrics.
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

    zone_counts = {sv: {'BASIN': 0, 'CORRIDOR': 0, 'WARNING': 0, 'HARD_STOP': 0}
                   for sv in STATE_VARS}
    warning_contacts = {sv: 0 for sv in STATE_VARS}
    hard_stop_contacts = {sv: 0 for sv in STATE_VARS}

    in_excursion = False
    excursion_start = None
    excursion_count = 0
    bounded_excursion_count = 0

    lp_mismatches = 0

    # ---- NEW metric accumulators ----

    # PCV
    pcv_score_sum = 0.0
    pcv_pair_count = 0

    # SAHB accumulators
    sahb_warning = 0
    sahb_hardstop = 0
    sahb_outside_corridor = 0
    sahb_max_excursion = 0.0

    # REF: per-line tracking
    # We build an ordered list of (line_key, phase, end_dev) tuples
    # Then pair each CLOSE line with its most recent preceding WORK line
    current_line_phase = None
    line_sequence = []  # ordered list of (line_key, phase, end_dev) filled on line transitions
    # last_work_end_dev tracks the most recent WORK line's end_dev for each folio
    last_work_end_dev_per_folio = {}  # folio -> float
    ref_pairs = []  # list of (work_end_dev, close_end_dev) pairs

    # QGY
    quality_y = 0.0
    prev_aggregate_dev = None  # aggregate deviation across process SVs

    # CRE: excursion tracking for strict and soft
    # Track active excursions: when any process SV goes past Q2
    cre_total_excursions = 0
    cre_strict_resolved = 0
    cre_soft_resolved = 0
    # Per-line excursion tracking
    line_had_q2_excursion = False       # any SV past Q2 on current line
    line_excursion_resolved_strict = False  # all SVs returned below Q2 during CLOSE line
    line_excursion_resolved_soft = False    # all SVs returned below Q2 by end of line

    # MPZF
    mpzf_correct = 0
    mpzf_total = 0

    # Track line-level data for REF/CRE
    current_line_key = None
    current_line_tokens_processed = 0

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']
        line_key = f"{folio}|{current_line}"

        # ---- Line boundary handling ----
        if current_line != prev_line:
            # Finalize departing line for REF and CRE
            if prev_line is not None and current_line_key is not None:
                departing_end_dev = sum(
                    abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS
                ) / len(PROCESS_SVS)

                # REF: record departing line's phase and end dev
                departing_folio = current_line_key.split('|')[0]
                if current_line_phase == 'WORK':
                    last_work_end_dev_per_folio[departing_folio] = departing_end_dev
                elif current_line_phase == 'CLOSE':
                    if departing_folio in last_work_end_dev_per_folio:
                        ref_pairs.append((
                            last_work_end_dev_per_folio[departing_folio],
                            departing_end_dev
                        ))

                # CRE: finalize departing line's excursion tracking
                if line_had_q2_excursion:
                    cre_total_excursions += 1
                    # For soft: check if all process SVs below Q2 now (end of line)
                    all_below_q2 = all(
                        abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                        for sv in PROCESS_SVS
                    )
                    if all_below_q2:
                        cre_soft_resolved += 1
                    if line_excursion_resolved_strict:
                        cre_strict_resolved += 1

            # Reset line-level tracking
            permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
            prev_line = current_line
            current_line_key = line_key
            line_had_q2_excursion = False
            line_excursion_resolved_strict = False

            # Determine phase for this line
            lp_key = line_key
            if lp_key in line_packets:
                lp = line_packets[lp_key]
                current_line_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
            else:
                current_line_phase = 'WORK'

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

        # ---- Pre-step aggregate deviation (for QGY) ----
        pre_agg_dev = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # ---- Compute dV ----
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            dV[i] = contributions[i] * apparatus.sensitivity[sv]

        # ---- Pre-step Y (for QGY delta) ----
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

        # ---- Post-step aggregate deviation (for QGY) ----
        post_agg_dev = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # ---- Y delta this step ----
        y_delta = state[Y_IDX] - pre_y

        # ================================================================
        # OLD METRICS
        # ================================================================

        # Zone classification per SV (4-zone from diagnostics)
        zones = diagnostics['zones']
        for sv in STATE_VARS:
            zone = zones[sv]
            zone_counts[sv][zone] += 1
            if zone == 'WARNING':
                warning_contacts[sv] += 1
            elif zone == 'HARD_STOP':
                hard_stop_contacts[sv] += 1

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
        # NEW METRICS
        # ================================================================

        # ---- 1. PCV ----
        pcv_s, pcv_c = _pcv_score_for_token(state, packet_phase)
        pcv_score_sum += pcv_s
        pcv_pair_count += pcv_c

        # ---- 2. SAHB ----
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            if sv == 'S' and state[i] > EQUILIBRIUM:
                # S above EQ: skip warning/hardstop tallies and corridor-exit
                # Also skip max_excursion contribution for S above EQ
                continue

            sahb_max_excursion = max(sahb_max_excursion, dev)

            if dev >= q3:
                sahb_hardstop += 1
            elif dev >= q2:
                sahb_warning += 1

            if dev >= q2:
                sahb_outside_corridor += 1

        # ---- 3. QGY ----
        if prev_aggregate_dev is not None:
            dev_decreased = (post_agg_dev < prev_aggregate_dev)
        else:
            dev_decreased = False

        if packet_phase == 'CLOSE' and cts > 0.3 and dev_decreased and y_delta > 0:
            quality_y += y_delta

        prev_aggregate_dev = post_agg_dev

        # ---- 4. CRE ----
        # Check if any process SV past Q2 on current token
        any_past_q2 = any(
            abs(state[SV_INDEX[sv]] - EQUILIBRIUM) >= Q2_BASE[sv]
            for sv in PROCESS_SVS
        )
        if any_past_q2:
            line_had_q2_excursion = True

        # For CRE_strict: track if during CLOSE line, all SVs returned below Q2
        if packet_phase == 'CLOSE' and line_had_q2_excursion:
            all_below_q2_now = all(
                abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                for sv in PROCESS_SVS
            )
            if all_below_q2_now:
                line_excursion_resolved_strict = True

        # ---- 5. MPZF ----
        mc, mt = _mpzf_score_for_token(state, packet_phase)
        mpzf_correct += mc
        mpzf_total += mt

    # ---- Finalize last line for REF and CRE ----
    if current_line_key is not None:
        departing_end_dev = sum(
            abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS
        ) / len(PROCESS_SVS)

        departing_folio = current_line_key.split('|')[0]
        if current_line_phase == 'WORK':
            last_work_end_dev_per_folio[departing_folio] = departing_end_dev
        elif current_line_phase == 'CLOSE':
            if departing_folio in last_work_end_dev_per_folio:
                ref_pairs.append((
                    last_work_end_dev_per_folio[departing_folio],
                    departing_end_dev
                ))

        if line_had_q2_excursion:
            cre_total_excursions += 1
            all_below_q2 = all(
                abs(state[SV_INDEX[sv]] - EQUILIBRIUM) < Q2_BASE[sv]
                for sv in PROCESS_SVS
            )
            if all_below_q2:
                cre_soft_resolved += 1
            if line_excursion_resolved_strict:
                cre_strict_resolved += 1

    # ================================================================
    # Compute final metric values
    # ================================================================

    # Old viability
    old_viability = viable_count / n_tokens if n_tokens > 0 else 0.0
    old_y_final = state[Y_IDX]

    # Zone occupancy fractions
    zone_occupancy = {}
    for sv in STATE_VARS:
        total = sum(zone_counts[sv].values())
        if total > 0:
            zone_occupancy[sv] = {
                'basin': round(zone_counts[sv]['BASIN'] / total, 5),
                'corridor': round(zone_counts[sv]['CORRIDOR'] / total, 5),
                'warning': round(zone_counts[sv]['WARNING'] / total, 5),
                'hard_stop': round(zone_counts[sv]['HARD_STOP'] / total, 5),
            }
        else:
            zone_occupancy[sv] = {'basin': 0.0, 'corridor': 0.0,
                                   'warning': 0.0, 'hard_stop': 0.0}

    # PCV
    pcv = pcv_score_sum / pcv_pair_count if pcv_pair_count > 0 else 0.0

    # SAHB
    sahb = (1.0 * sahb_warning + 3.0 * sahb_hardstop
            + 0.5 * sahb_outside_corridor + 2.0 * sahb_max_excursion)

    # REF
    ref_mean, ref_eligible_frac, ref_worsened_frac = _compute_ref(ref_pairs)

    # QGY
    qgy_ratio = quality_y / old_y_final if old_y_final > 0 else 0.0

    # CRE
    cre_strict = cre_strict_resolved / cre_total_excursions if cre_total_excursions > 0 else 0.0
    cre_soft = cre_soft_resolved / cre_total_excursions if cre_total_excursions > 0 else 0.0

    # MPZF
    mpzf = mpzf_correct / mpzf_total if mpzf_total > 0 else 0.0

    result = {
        # Old metrics
        'old_viability': round(old_viability, 5),
        'old_y_final': round(old_y_final, 5),
        'excursion_count': excursion_count,
        'bounded_excursion_count': bounded_excursion_count,
        'zone_occupancy': zone_occupancy,
        'warning_contacts': warning_contacts,
        'hard_stop_contacts': hard_stop_contacts,
        'n_tokens': n_tokens,
        'n_hazard_events': hazard_count,
        # New metrics
        'PCV': round(pcv, 5),
        'SAHB': round(sahb, 5),
        'REF_mean': round(ref_mean, 5),
        'REF_eligible_fraction': round(ref_eligible_frac, 5),
        'REF_worsened_fraction': round(ref_worsened_frac, 5),
        'QGY': round(quality_y, 5),
        'qgy_ratio': round(qgy_ratio, 5),
        'CRE_strict': round(cre_strict, 5),
        'CRE_soft': round(cre_soft, 5),
        'MPZF': round(mpzf, 5),
    }

    if lp_mismatches > 0:
        result['lp_mismatches'] = lp_mismatches

    return result


def _compute_ref(ref_pairs):
    """
    Compute REF from (work_end_dev, close_end_dev) pairs.

    Each pair represents a WORK-line -> CLOSE-line transition.
    Eligibility: work_end_dev > Q1 (0.08).
    REF per eligible pair = 1 - (close_end_dev / work_end_dev).

    Returns (REF_mean, REF_eligible_fraction, REF_worsened_fraction).
    """
    if not ref_pairs:
        return 0.0, 0.0, 0.0

    total_pairs = len(ref_pairs)
    eligible_count = 0
    ref_values = []
    worsened_count = 0

    for work_dev, close_dev in ref_pairs:
        if work_dev <= Q1:
            continue

        eligible_count += 1
        ref_val = 1.0 - (close_dev / work_dev)
        ref_values.append(ref_val)

        if close_dev > work_dev:
            worsened_count += 1

    if eligible_count == 0:
        return 0.0, 0.0, 0.0

    ref_mean = sum(ref_values) / len(ref_values)
    ref_eligible_frac = eligible_count / total_pairs
    ref_worsened_frac = worsened_count / eligible_count

    return ref_mean, ref_eligible_frac, ref_worsened_frac


def _empty_result():
    """Return empty result dict for folios with no tokens."""
    return {
        'old_viability': 0.0,
        'old_y_final': 0.5,
        'excursion_count': 0,
        'bounded_excursion_count': 0,
        'zone_occupancy': {sv: {'basin': 0.0, 'corridor': 0.0,
                                 'warning': 0.0, 'hard_stop': 0.0}
                           for sv in STATE_VARS},
        'warning_contacts': {sv: 0 for sv in STATE_VARS},
        'hard_stop_contacts': {sv: 0 for sv in STATE_VARS},
        'n_tokens': 0,
        'n_hazard_events': 0,
        'PCV': 0.0,
        'SAHB': 0.0,
        'REF_mean': 0.0,
        'REF_eligible_fraction': 0.0,
        'REF_worsened_fraction': 0.0,
        'QGY': 0.0,
        'qgy_ratio': 0.0,
        'CRE_strict': 0.0,
        'CRE_soft': 0.0,
        'MPZF': 0.0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    project_root = phase_dir.parent.parent

    output_path = phase_dir / 'results' / 't2_burden_runs.json'

    # --- Data source paths ---
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    t1_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY'
               / 'results' / 't1_close_recovery_apparatus.json')
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')

    print("=" * 70)
    print("T2: Burden Executor")
    print("Phase 567 - CLOSURE_FIELD_AUDIT")
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

    # --- Determine preferred profiles for pilot folios ---
    print("\n--- Assigning folio profiles ---")
    regime_path = project_root / 'data' / 'regime_folio_mapping.json'
    budget_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                   / 'results' / 't2_folio_budgets.json')

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
    primary_results = {}  # folio -> {profile -> result}
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
            result = run_burden_trace(apparatus, toks, line_packets)
            primary_results[folio][profile_name] = result
            run_count += 1

            is_pref = (profile_name == preferred_profile)
            pref_tag = " *PREFERRED*" if is_pref else ""
            short_profile = profile_name.split('_')[0]
            print(f"  [{run_count:2d}/60] {folio} + {short_profile} [{config_mode}]: "
                  f"viab={result['old_viability']:.4f}, "
                  f"PCV={result['PCV']:.4f}, SAHB={result['SAHB']:.1f}, "
                  f"REF={result['REF_mean']:.4f}, QGY={result['QGY']:.4f}, "
                  f"CRE_s={result['CRE_strict']:.4f}, MPZF={result['MPZF']:.4f}"
                  f"{pref_tag}")

    # --- Config ablation runs (30): 10 folios x preferred profile x 3 configs ---
    print("\n--- Config Ablation Runs (30) ---")
    config_ablation_results = {}  # folio -> {config_mode -> result}
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
            result = run_burden_trace(apparatus, toks, line_packets)
            config_ablation_results[folio][cm] = result
            ablation_count += 1

            short_cm = cm.split('_')[0]
            print(f"  [{ablation_count:2d}/30] {folio} + {preferred_profile.split('_')[0]} + {short_cm}: "
                  f"viab={result['old_viability']:.4f}, "
                  f"PCV={result['PCV']:.4f}, SAHB={result['SAHB']:.1f}")

    # --- Build output ---
    print("\n--- Building output ---")

    # Restructure primary_runs to match output spec: folio -> {A1: {...}, A2: {...}, A3: {...}}
    primary_runs_out = {}
    for folio in primary_results:
        primary_runs_out[folio] = {}
        for profile_name in PROFILE_NAMES:
            short_key = profile_name.split('_')[0]  # A1, A2, A3
            if profile_name in primary_results[folio]:
                primary_runs_out[folio][short_key] = primary_results[folio][profile_name]

    # Restructure config_ablation_runs: folio -> {H0: {...}, H1: {...}, H2: {...}}
    config_ablation_out = {}
    for folio in config_ablation_results:
        config_ablation_out[folio] = {}
        for cm in CONFIG_MODE_NAMES:
            short_key = cm.split('_')[0]  # H0, H1, H2
            if cm in config_ablation_results[folio]:
                config_ablation_out[folio][short_key] = config_ablation_results[folio][cm]

    # --- Summary statistics (preferred profile runs) ---
    pref_pcv = []
    pref_sahb = []
    pref_ref = []
    pref_qgy = []
    pref_cre_strict = []
    pref_mpzf = []
    pref_viability = []
    pref_y_final = []
    total_hazard = 0

    for folio in primary_results:
        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        if preferred_profile in primary_results[folio]:
            r = primary_results[folio][preferred_profile]
            pref_pcv.append(r['PCV'])
            pref_sahb.append(r['SAHB'])
            pref_ref.append(r['REF_mean'])
            pref_qgy.append(r['QGY'])
            pref_cre_strict.append(r['CRE_strict'])
            pref_mpzf.append(r['MPZF'])
            pref_viability.append(r['old_viability'])
            pref_y_final.append(r['old_y_final'])
            total_hazard += r['n_hazard_events']

    n_pref = len(pref_pcv)
    mean = lambda lst: sum(lst) / len(lst) if lst else 0.0

    summary = {
        'mean_preferred_PCV': round(mean(pref_pcv), 5),
        'mean_preferred_SAHB': round(mean(pref_sahb), 5),
        'mean_preferred_REF': round(mean(pref_ref), 5),
        'mean_preferred_QGY': round(mean(pref_qgy), 5),
        'mean_preferred_CRE_strict': round(mean(pref_cre_strict), 5),
        'mean_preferred_MPZF': round(mean(pref_mpzf), 5),
        'mean_preferred_old_viability': round(mean(pref_viability), 5),
        'mean_preferred_old_y_final': round(mean(pref_y_final), 5),
        'n_hazard_events': total_hazard,
    }

    output = {
        'metadata': {
            'phase': 567,
            'script': 't2_burden_executor.py',
            'n_runs': run_count + ablation_count,
            'timestamp': datetime.now().isoformat(),
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
    print("\n--- Final Statistics (preferred-profile runs) ---")
    print(f"  n_preferred_runs: {n_pref}")
    print(f"  mean_preferred_old_viability: {mean(pref_viability):.5f}")
    print(f"  mean_preferred_old_y_final:   {mean(pref_y_final):.5f}")
    print(f"  total_hazard_events:          {total_hazard}")
    print(f"  mean_preferred_PCV:           {mean(pref_pcv):.5f}")
    print(f"  mean_preferred_SAHB:          {mean(pref_sahb):.1f}")
    print(f"  mean_preferred_REF:           {mean(pref_ref):.5f}")
    print(f"  mean_preferred_QGY:           {mean(pref_qgy):.5f}")
    print(f"  mean_preferred_CRE_strict:    {mean(pref_cre_strict):.5f}")
    print(f"  mean_preferred_MPZF:          {mean(pref_mpzf):.5f}")

    # Per-folio preferred breakdown
    print("\n  Per-folio preferred breakdown:")
    print(f"  {'Folio':<10s} {'Viab':>7s} {'PCV':>7s} {'SAHB':>8s} {'REF':>7s} {'QGY':>8s} {'CRE_s':>7s} {'MPZF':>7s}")
    for folio in PILOT_FOLIOS:
        pref = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')
        if folio in primary_results and pref in primary_results[folio]:
            r = primary_results[folio][pref]
            print(f"  {folio:<10s} {r['old_viability']:7.4f} {r['PCV']:7.4f} {r['SAHB']:8.1f} "
                  f"{r['REF_mean']:7.4f} {r['QGY']:8.4f} {r['CRE_strict']:7.4f} {r['MPZF']:7.4f}")

    print(f"\n  Total runs: {run_count + ablation_count}")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
