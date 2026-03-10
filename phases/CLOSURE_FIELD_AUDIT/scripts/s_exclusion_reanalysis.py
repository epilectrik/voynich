#!/usr/bin/env python3
"""
S-Exclusion Reanalysis
======================
Phase 567 supplement - CLOSURE_FIELD_AUDIT

Phase 567 found that S accounts for 90% of all warning+hard_stop contacts
and 84.5% of SAHB. This script re-runs a reduced test battery with S
EXCLUDED from all discrimination metrics (PCV, SAHB, QGY) to test whether
S is masking real discrimination on the other 5 process SVs (T, RC, C, TR, X).

Runs:
  - 20 reference runs (full model, preferred profile, preferred config)
  - N1 x 20 folios x 10 perms = 200 runs (phase-shuffled null)
  - N2 x 20 folios x 10 perms = 200 runs (contribution-shuffled null)
  - N4 x 20 folios x 10 perms = 200 runs (random walk null)
  - B10 x 20 folios = 20 runs (no CLOSE recovery)
  Total: 640 runs

Metrics:
  PCV_noS   - Packet-Coherence Viability over T, RC, C, TR, X only
  SAHB_noS  - Hazard burden over T, RC, C, TR, X only
  QGY_noS   - Quality-gated Y with aggregate dev over T, RC, C, TR, X only
  PCV_withS - Original PCV for comparison (computed alongside)
  SAHB_withS - Original SAHB for comparison

Output:
  phases/CLOSURE_FIELD_AUDIT/results/s_exclusion_reanalysis.json
"""

import json
import math
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# Import apparatus from Phase 566 T1
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY' / 'scripts'))

from t1_close_recovery_apparatus import (
    CloseRecoveryApparatus, build_close_recovery_apparatus,
    build_no_close_recovery_apparatus, build_configured_apparatus,
    STATE_VARS, SV_INDEX, N_VARS, EQUILIBRIUM, Q1, Q2_BASE, Q3_BASE,
    HAZARD_BOUNDARIES, HAZARD_DEV, PILOT_FOLIOS, PROFILES,
    GAMMA_CORRIDOR, assign_folio_profiles,
    CORRIDOR_MULT, BASIN_MULT,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
S_IDX = SV_INDEX['S']
Y_IDX = SV_INDEX['Y']

# Process SVs (all with hazard boundaries, excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]

# S-excluded process SVs: T, RC, C, TR, X
PROCESS_SVS_NO_S = [sv for sv in PROCESS_SVS if sv != 'S']

# Routing constants (from T3)
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

N_PERMS = 10  # Reduced from 50 for speed

# ---------------------------------------------------------------------------
# PCV desirability tables (FROZEN)
# ---------------------------------------------------------------------------
# Process SVs (T, RC, C, TR, X) -- used for both withS and noS
PCV_ZONE_SCORES = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

# S asymmetric (above EQ) — for withS PCV only
PCV_S_HIGH_SCORES = {
    'SPEC':  0.9,
    'WORK':  1.0,
    'CLOSE': 0.9,
}


# ---------------------------------------------------------------------------
# Zone classification
# ---------------------------------------------------------------------------
def _classify_zone(sv, abs_dev):
    """Classify a state variable's deviation into 5-zone system."""
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
# Core execution: computes BOTH withS and noS metrics in one pass
# ---------------------------------------------------------------------------
def run_dual_trace(apparatus, tokens, line_packets):
    """
    Run one folio through the CloseRecoveryApparatus.
    Computes both with-S and without-S metrics in a single pass.

    Returns dict with PCV_noS, SAHB_noS, QGY_noS, PCV_withS, SAHB_withS, QGY_withS,
    and diagnostic counters.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'PCV_noS': 1.0, 'SAHB_noS': 0.0, 'QGY_noS': 0.0,
            'PCV_withS': 1.0, 'SAHB_withS': 0.0, 'QGY_withS': 0.0,
            'n_tokens': 0,
            'warning_contacts_noS': 0, 'hardstop_contacts_noS': 0,
            'warning_contacts_withS': 0, 'hardstop_contacts_withS': 0,
            'warning_contacts_S_only': 0, 'hardstop_contacts_S_only': 0,
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    prev_line = None

    # --- PCV accumulators ---
    pcv_noS_sum = 0.0
    pcv_noS_count = 0
    pcv_withS_sum = 0.0
    pcv_withS_count = 0

    # --- SAHB accumulators (noS) ---
    sahb_noS_warnings = 0
    sahb_noS_hardstops = 0
    sahb_noS_outside_corridor = 0
    sahb_noS_max_excursion = 0.0

    # --- SAHB accumulators (withS) ---
    sahb_withS_warnings = 0
    sahb_withS_hardstops = 0
    sahb_withS_outside_corridor = 0
    sahb_withS_max_excursion = 0.0

    # --- QGY accumulators ---
    qgy_noS_total = 0.0
    qgy_withS_total = 0.0
    prev_agg_dev_noS = None
    prev_agg_dev_withS = None

    # --- Contact counters ---
    warn_noS = 0
    hs_noS = 0
    warn_withS = 0
    hs_withS = 0
    warn_S_only = 0
    hs_S_only = 0

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok.get('folio', '')

        # Save pre-update state for Y delta
        pre_state = list(state)

        # Line boundary: reset routing buffer
        if current_line != prev_line:
            routing_contrib_buffer = [0.0] * N_VARS
            prev_line = current_line

        # Routing event
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_EFFECTS:
                effects = ROUTING_EFFECTS[rt]
                for sv, mult in effects.get('boost', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                for sv, mult in effects.get('suppress', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN

        # Packet phase
        line_key = f"{folio}|{current_line}"
        packet = line_packets.get(line_key)
        if packet and 'packet_state' in packet:
            packet_phase = packet['packet_state'].get('packet_phase', 'WORK')
        else:
            packet_phase = tok.get('packet_phase', 'WORK')

        # CTS
        cts = tok.get('cts', 0.0)

        # Compute dV
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            base_sens = apparatus.sensitivity[sv]
            dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])

        # Pre-step aggregate deviations
        pre_agg_noS = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS_NO_S)
        pre_agg_withS = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # Apparatus update
        state, diagnostics = apparatus.update(state, dV, packet_phase, cts, None)

        # Decay routing buffer
        routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]

        # Post-step aggregate deviations
        post_agg_noS = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS_NO_S)
        post_agg_withS = sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS)

        # Y delta
        y_delta = state[Y_IDX] - pre_state[Y_IDX]

        phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])

        # ================================================================
        # PCV_noS: only T, RC, C, TR, X
        # ================================================================
        for sv in PROCESS_SVS_NO_S:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            zone = _classify_zone(sv, dev)
            if dev >= HAZARD_DEV[sv]:
                pcv_noS_sum += phase_scores.get('HAZARD', 0.0)
            else:
                pcv_noS_sum += phase_scores.get(zone, 0.0)
            pcv_noS_count += 1

        # ================================================================
        # PCV_withS: T, RC, C, TR, X + S (asymmetric)
        # ================================================================
        for sv in PROCESS_SVS_NO_S:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            zone = _classify_zone(sv, dev)
            if dev >= HAZARD_DEV[sv]:
                pcv_withS_sum += phase_scores.get('HAZARD', 0.0)
            else:
                pcv_withS_sum += phase_scores.get(zone, 0.0)
            pcv_withS_count += 1

        # S contribution to PCV_withS
        s_val = state[S_IDX]
        s_dev = abs(s_val - EQUILIBRIUM)
        if s_val > EQUILIBRIUM:
            pcv_withS_sum += PCV_S_HIGH_SCORES.get(packet_phase, 1.0)
        else:
            zone = _classify_zone('S', s_dev)
            if s_dev >= HAZARD_DEV['S']:
                pcv_withS_sum += phase_scores.get('HAZARD', 0.0)
            else:
                pcv_withS_sum += phase_scores.get(zone, 0.0)
        pcv_withS_count += 1

        # ================================================================
        # SAHB_noS: T, RC, C, TR, X only
        # ================================================================
        for sv in PROCESS_SVS_NO_S:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            sahb_noS_max_excursion = max(sahb_noS_max_excursion, dev)

            if dev >= q3:
                sahb_noS_hardstops += 1
                hs_noS += 1
            elif dev >= q2:
                sahb_noS_warnings += 1
                warn_noS += 1

            if dev >= q2:
                sahb_noS_outside_corridor += 1

        # ================================================================
        # SAHB_withS: all process SVs, S-asymmetric (skip high-S)
        # ================================================================
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            dev = abs(state[i] - EQUILIBRIUM)
            q2 = Q2_BASE[sv]
            q3 = q2 + 0.05
            q3 = min(q3, HAZARD_DEV[sv] - 0.01)

            # S asymmetric: skip penalty when S > EQ
            if sv == 'S' and state[S_IDX] > EQUILIBRIUM:
                continue

            sahb_withS_max_excursion = max(sahb_withS_max_excursion, dev)

            if dev >= q3:
                sahb_withS_hardstops += 1
                hs_withS += 1
            elif dev >= q2:
                sahb_withS_warnings += 1
                warn_withS += 1

            if dev >= q2:
                sahb_withS_outside_corridor += 1

        # S-only contacts (for diagnostic)
        s_dev_now = abs(state[S_IDX] - EQUILIBRIUM)
        s_q2 = Q2_BASE['S']
        s_q3 = s_q2 + 0.05
        s_q3 = min(s_q3, HAZARD_DEV['S'] - 0.01)
        if s_dev_now >= s_q3:
            hs_S_only += 1
        elif s_dev_now >= s_q2:
            warn_S_only += 1

        # ================================================================
        # QGY_noS and QGY_withS
        # ================================================================
        if packet_phase == 'CLOSE':
            # QGY_noS: aggregate dev check over non-S process SVs only
            if cts > 0.3 and prev_agg_dev_noS is not None:
                if post_agg_noS < prev_agg_dev_noS:
                    if y_delta > 0:
                        qgy_noS_total += y_delta

            # QGY_withS: aggregate dev check over all process SVs
            if cts > 0.3 and prev_agg_dev_withS is not None:
                if post_agg_withS < prev_agg_dev_withS:
                    if y_delta > 0:
                        qgy_withS_total += y_delta

            prev_agg_dev_noS = post_agg_noS
            prev_agg_dev_withS = post_agg_withS
        else:
            prev_agg_dev_noS = None
            prev_agg_dev_withS = None

    # ================================================================
    # Final metric computation
    # ================================================================
    pcv_noS = round(pcv_noS_sum / pcv_noS_count, 6) if pcv_noS_count > 0 else 1.0
    pcv_withS = round(pcv_withS_sum / pcv_withS_count, 6) if pcv_withS_count > 0 else 1.0

    sahb_noS = (1.0 * sahb_noS_warnings + 3.0 * sahb_noS_hardstops
                + 0.5 * sahb_noS_outside_corridor + 2.0 * sahb_noS_max_excursion)
    sahb_noS_norm = round(sahb_noS / n_tokens, 6) if n_tokens > 0 else 0.0

    sahb_withS = (1.0 * sahb_withS_warnings + 3.0 * sahb_withS_hardstops
                  + 0.5 * sahb_withS_outside_corridor + 2.0 * sahb_withS_max_excursion)
    sahb_withS_norm = round(sahb_withS / n_tokens, 6) if n_tokens > 0 else 0.0

    qgy_noS = round(qgy_noS_total, 6)
    qgy_withS = round(qgy_withS_total, 6)

    return {
        'PCV_noS': pcv_noS,
        'SAHB_noS': sahb_noS_norm,
        'QGY_noS': qgy_noS,
        'PCV_withS': pcv_withS,
        'SAHB_withS': sahb_withS_norm,
        'QGY_withS': qgy_withS,
        'n_tokens': n_tokens,
        'warning_contacts_noS': warn_noS,
        'hardstop_contacts_noS': hs_noS,
        'warning_contacts_withS': warn_withS,
        'hardstop_contacts_withS': hs_withS,
        'warning_contacts_S_only': warn_S_only,
        'hardstop_contacts_S_only': hs_S_only,
    }


# ---------------------------------------------------------------------------
# Null model generators (from T3)
# ---------------------------------------------------------------------------

def null_n1_phase_shuffle(tokens, rng):
    """N1: Phase-shuffled. Random ordering, same positions."""
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


def null_n4_random_walk(tokens, rng):
    """N4: Random walk. Random dV magnitudes from same distribution."""
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
    print("S-EXCLUSION REANALYSIS")
    print("Phase 567 supplement - CLOSURE_FIELD_AUDIT")
    print("=" * 70)
    print(f"\nSVs included in noS metrics: {PROCESS_SVS_NO_S}")
    print(f"SVs excluded: S, Y")
    print(f"Permutations per null: {N_PERMS}")

    # --- Paths ---
    T2B_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
                / 't2b_supervisory_interface_unrouted.json')
    T1_566_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY'
                   / 'results' / 't1_close_recovery_apparatus.json')
    PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                    / 'results' / 't3_line_packets.json')
    REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    BUDGET_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                   / 'results' / 't2_folio_budgets.json')
    OUTPUT_PATH = PHASE_DIR / 'results' / 's_exclusion_reanalysis.json'

    # Also load T4 results for comparison values
    T4_PATH = PHASE_DIR / 'results' / 't4_burden_validation.json'

    # --- Load data ---
    print("\n--- Loading data sources ---")

    print(f"  Loading T2b supervisory tokens...")
    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"    Total tokens: {len(all_tokens)}")

    print(f"  Loading T1 apparatus config...")
    with open(T1_566_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    infra_scores = t1_data['folio_infra_scores']

    print(f"  Loading line packets...")
    with open(PACKETS_PATH, 'r', encoding='utf-8') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    # Load T4 for comparison
    t4_comparison = {}
    if T4_PATH.exists():
        print(f"  Loading T4 validation results for comparison...")
        with open(T4_PATH, 'r', encoding='utf-8') as f:
            t4_comparison = json.load(f)

    # --- Folio profile assignments ---
    print("\n--- Assigning folio profiles ---")
    folio_assignments = assign_folio_profiles(REGIME_PATH, BUDGET_PATH)

    folio_profile = {}
    folio_config_mode = {}
    for folio in PILOT_FOLIOS:
        assignment = folio_assignments.get(folio, {})
        folio_profile[folio] = assignment.get('preferred_profile', 'A2_SEALED_RECIRCULATION')
        infra = infra_scores.get(folio, {})
        folio_config_mode[folio] = infra.get('config_mode', 'H1_MEDIUM_INFRA')

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    pilot_folio_list = sorted(PILOT_FOLIOS)
    for folio in pilot_folio_list:
        n = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: {n} tokens, profile={folio_profile[folio]}, "
              f"config={folio_config_mode[folio]}")

    run_count = 0

    # =====================================================================
    # REFERENCE RUNS (20 folios, full model)
    # =====================================================================
    print("\n" + "=" * 70)
    print("REFERENCE RUNS (full model, 20 folios)")
    print("=" * 70)

    reference = {}
    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            print(f"  WARNING: {folio} has no tokens, skipping")
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        apparatus = build_configured_apparatus(profile, config_mode)

        result = run_dual_trace(apparatus, toks, line_packets)
        reference[folio] = result
        run_count += 1

        print(f"  {folio}: PCV_noS={result['PCV_noS']:.4f} "
              f"PCV_withS={result['PCV_withS']:.4f}  "
              f"SAHB_noS={result['SAHB_noS']:.4f} "
              f"SAHB_withS={result['SAHB_withS']:.4f}  "
              f"QGY_noS={result['QGY_noS']:.4f} "
              f"QGY_withS={result['QGY_withS']:.4f}")

    # =====================================================================
    # B10 BASELINE (no CLOSE recovery, 20 folios)
    # =====================================================================
    print("\n" + "=" * 70)
    print("B10 BASELINE (no CLOSE recovery, 20 folios)")
    print("=" * 70)

    b10_results = {}
    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        apparatus = build_no_close_recovery_apparatus(profile, config_mode)

        result = run_dual_trace(apparatus, toks, line_packets)
        b10_results[folio] = result
        run_count += 1

        print(f"  {folio}: PCV_noS={result['PCV_noS']:.4f} "
              f"SAHB_noS={result['SAHB_noS']:.4f} "
              f"QGY_noS={result['QGY_noS']:.4f}")

    elapsed = time.time() - t0
    print(f"\n  Reference + B10: {run_count} runs in {elapsed:.1f}s")

    # =====================================================================
    # NULL MODELS (N1, N2, N4 x 20 folios x 10 perms = 600 runs)
    # =====================================================================
    print("\n" + "=" * 70)
    print(f"NULL MODELS (N1, N2, N4 x 20 folios x {N_PERMS} perms = "
          f"{3 * 20 * N_PERMS} runs)")
    print("=" * 70)

    METRIC_KEYS = ['PCV_noS', 'SAHB_noS', 'QGY_noS',
                   'PCV_withS', 'SAHB_withS', 'QGY_withS']

    null_runs = {
        'N1': {},
        'N2': {},
        'N4': {},
    }

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]

        for null_name in null_runs:
            null_runs[null_name][folio] = {mk: [] for mk in METRIC_KEYS}

        for perm_idx in range(N_PERMS):
            # N1: phase-shuffled
            rng1 = random.Random(42 + perm_idx)
            n1_toks = null_n1_phase_shuffle(toks, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_dual_trace(apparatus, n1_toks, line_packets)
            for mk in METRIC_KEYS:
                null_runs['N1'][folio][mk].append(r1[mk])
            run_count += 1

            # N2: contribution-shuffled
            rng2 = random.Random(42 + perm_idx)
            n2_toks = null_n2_contribution_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_dual_trace(apparatus, n2_toks, line_packets)
            for mk in METRIC_KEYS:
                null_runs['N2'][folio][mk].append(r2[mk])
            run_count += 1

            # N4: random walk
            rng4 = random.Random(42 + perm_idx)
            n4_toks = null_n4_random_walk(toks, rng4)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_dual_trace(apparatus, n4_toks, line_packets)
            for mk in METRIC_KEYS:
                null_runs['N4'][folio][mk].append(r4[mk])
            run_count += 1

        elapsed = time.time() - t0
        print(f"  {folio} nulls done ({run_count} runs, {elapsed:.1f}s)")

    # =====================================================================
    # Compute null summaries (mean across permutations)
    # =====================================================================
    null_summaries = {}
    for null_name in null_runs:
        null_summaries[null_name] = {}
        for folio in null_runs[null_name]:
            entry = null_runs[null_name][folio]
            summary = {}
            for mk in METRIC_KEYS:
                vals = entry[mk]
                if vals:
                    summary[f'mean_{mk}'] = round(sum(vals) / len(vals), 6)
                    # Also store std
                    mean_v = sum(vals) / len(vals)
                    var_v = sum((v - mean_v) ** 2 for v in vals) / len(vals)
                    summary[f'std_{mk}'] = round(math.sqrt(var_v), 6)
                else:
                    summary[f'mean_{mk}'] = 0.0
                    summary[f'std_{mk}'] = 0.0
            null_summaries[null_name][folio] = summary

    # =====================================================================
    # NP TESTS (S-excluded)
    # =====================================================================
    print("\n" + "=" * 70)
    print("NP TESTS")
    print("=" * 70)

    def mean(lst):
        return sum(lst) / len(lst) if lst else 0.0

    # --- NP1_noS: Full PCV_noS > N1 mean PCV_noS ---
    np1_noS_pass_count = 0
    np1_noS_details = []
    np1_withS_pass_count = 0

    for folio in pilot_folio_list:
        if folio not in reference or folio not in null_summaries['N1']:
            continue
        full_noS = reference[folio]['PCV_noS']
        n1_noS = null_summaries['N1'][folio]['mean_PCV_noS']
        passed = full_noS > n1_noS
        if passed:
            np1_noS_pass_count += 1
        np1_noS_details.append({
            'folio': folio, 'full_PCV_noS': full_noS,
            'N1_mean_PCV_noS': n1_noS, 'pass': passed
        })

        # WithS comparison
        full_withS = reference[folio]['PCV_withS']
        n1_withS = null_summaries['N1'][folio]['mean_PCV_withS']
        if full_withS > n1_withS:
            np1_withS_pass_count += 1

    np1_noS_result = 'PASS' if np1_noS_pass_count >= 14 else 'FAIL'
    np1_withS_result = 'PASS' if np1_withS_pass_count >= 14 else 'FAIL'

    print(f"\n  NP1 (PCV > N1 mean): noS={np1_noS_pass_count}/20 [{np1_noS_result}]  "
          f"withS={np1_withS_pass_count}/20 [{np1_withS_result}]")

    # --- NP2_noS: Full SAHB_noS < N1 mean SAHB_noS ---
    np2_noS_pass_count = 0
    np2_noS_details = []
    np2_withS_pass_count = 0

    for folio in pilot_folio_list:
        if folio not in reference or folio not in null_summaries['N1']:
            continue
        full_noS = reference[folio]['SAHB_noS']
        n1_noS = null_summaries['N1'][folio]['mean_SAHB_noS']
        passed = full_noS < n1_noS
        if passed:
            np2_noS_pass_count += 1
        np2_noS_details.append({
            'folio': folio, 'full_SAHB_noS': full_noS,
            'N1_mean_SAHB_noS': n1_noS, 'pass': passed
        })

        full_withS = reference[folio]['SAHB_withS']
        n1_withS = null_summaries['N1'][folio]['mean_SAHB_withS']
        if full_withS < n1_withS:
            np2_withS_pass_count += 1

    np2_noS_result = 'PASS' if np2_noS_pass_count >= 14 else 'FAIL'
    np2_withS_result = 'PASS' if np2_withS_pass_count >= 14 else 'FAIL'

    print(f"  NP2 (SAHB < N1 mean): noS={np2_noS_pass_count}/20 [{np2_noS_result}]  "
          f"withS={np2_withS_pass_count}/20 [{np2_withS_result}]")

    # --- NP3_noS: Full QGY_noS > N2 mean QGY_noS ---
    np3_noS_pass_count = 0
    np3_noS_details = []
    np3_withS_pass_count = 0

    for folio in pilot_folio_list:
        if folio not in reference or folio not in null_summaries['N2']:
            continue
        full_noS = reference[folio]['QGY_noS']
        n2_noS = null_summaries['N2'][folio]['mean_QGY_noS']
        passed = full_noS > n2_noS
        if passed:
            np3_noS_pass_count += 1
        np3_noS_details.append({
            'folio': folio, 'full_QGY_noS': full_noS,
            'N2_mean_QGY_noS': n2_noS, 'pass': passed
        })

        full_withS = reference[folio]['QGY_withS']
        n2_withS = null_summaries['N2'][folio]['mean_QGY_withS']
        if full_withS > n2_withS:
            np3_withS_pass_count += 1

    np3_noS_result = 'PASS' if np3_noS_pass_count >= 14 else 'FAIL'
    np3_withS_result = 'PASS' if np3_withS_pass_count >= 14 else 'FAIL'

    print(f"  NP3 (QGY > N2 mean): noS={np3_noS_pass_count}/20 [{np3_noS_result}]  "
          f"withS={np3_withS_pass_count}/20 [{np3_withS_result}]")

    # --- NP4_noS: Full QGY_noS > N4 mean QGY_noS ---
    np4_noS_pass_count = 0
    np4_noS_details = []
    np4_withS_pass_count = 0

    for folio in pilot_folio_list:
        if folio not in reference or folio not in null_summaries['N4']:
            continue
        full_noS = reference[folio]['QGY_noS']
        n4_noS = null_summaries['N4'][folio]['mean_QGY_noS']
        passed = full_noS > n4_noS
        if passed:
            np4_noS_pass_count += 1
        np4_noS_details.append({
            'folio': folio, 'full_QGY_noS': full_noS,
            'N4_mean_QGY_noS': n4_noS, 'pass': passed
        })

        full_withS = reference[folio]['QGY_withS']
        n4_withS = null_summaries['N4'][folio]['mean_QGY_withS']
        if full_withS > n4_withS:
            np4_withS_pass_count += 1

    np4_noS_result = 'PASS' if np4_noS_pass_count >= 14 else 'FAIL'
    np4_withS_result = 'PASS' if np4_withS_pass_count >= 14 else 'FAIL'

    print(f"  NP4 (QGY > N4 mean): noS={np4_noS_pass_count}/20 [{np4_noS_result}]  "
          f"withS={np4_withS_pass_count}/20 [{np4_withS_result}]")

    # --- NP6_noS: PCV delta (full - B10) ---
    full_pcv_noS_list = [reference[f]['PCV_noS'] for f in pilot_folio_list if f in reference]
    b10_pcv_noS_list = [b10_results[f]['PCV_noS'] for f in pilot_folio_list if f in b10_results]
    full_pcv_withS_list = [reference[f]['PCV_withS'] for f in pilot_folio_list if f in reference]
    b10_pcv_withS_list = [b10_results[f]['PCV_withS'] for f in pilot_folio_list if f in b10_results]

    mean_full_noS = mean(full_pcv_noS_list)
    mean_b10_noS = mean(b10_pcv_noS_list)
    abs_delta_noS = abs(mean_full_noS - mean_b10_noS)

    # Dynamic range for relative delta
    all_pcv_noS = full_pcv_noS_list + b10_pcv_noS_list
    pcv_noS_range = max(all_pcv_noS) - min(all_pcv_noS) if all_pcv_noS else 1.0
    rel_delta_noS = (abs_delta_noS / pcv_noS_range * 100) if pcv_noS_range > 0 else 0.0

    # Cohen's d
    if len(full_pcv_noS_list) > 1 and len(b10_pcv_noS_list) > 1:
        var_full = sum((v - mean_full_noS) ** 2 for v in full_pcv_noS_list) / (len(full_pcv_noS_list) - 1)
        var_b10 = sum((v - mean_b10_noS) ** 2 for v in b10_pcv_noS_list) / (len(b10_pcv_noS_list) - 1)
        pooled_std = math.sqrt((var_full + var_b10) / 2)
        cohens_d_noS = abs_delta_noS / pooled_std if pooled_std > 0 else 0.0
    else:
        cohens_d_noS = 0.0

    np6_noS_pass = (abs_delta_noS > 0.01) or (rel_delta_noS > 2.0) or (cohens_d_noS > 0.3)
    np6_noS_result = 'PASS' if np6_noS_pass else 'FAIL'

    # WithS version
    mean_full_withS = mean(full_pcv_withS_list)
    mean_b10_withS = mean(b10_pcv_withS_list)
    abs_delta_withS = abs(mean_full_withS - mean_b10_withS)
    all_pcv_withS = full_pcv_withS_list + b10_pcv_withS_list
    pcv_withS_range = max(all_pcv_withS) - min(all_pcv_withS) if all_pcv_withS else 1.0
    rel_delta_withS = (abs_delta_withS / pcv_withS_range * 100) if pcv_withS_range > 0 else 0.0

    if len(full_pcv_withS_list) > 1 and len(b10_pcv_withS_list) > 1:
        var_f = sum((v - mean_full_withS) ** 2 for v in full_pcv_withS_list) / (len(full_pcv_withS_list) - 1)
        var_b = sum((v - mean_b10_withS) ** 2 for v in b10_pcv_withS_list) / (len(b10_pcv_withS_list) - 1)
        ps = math.sqrt((var_f + var_b) / 2)
        cohens_d_withS = abs_delta_withS / ps if ps > 0 else 0.0
    else:
        cohens_d_withS = 0.0

    np6_withS_pass = (abs_delta_withS > 0.01) or (rel_delta_withS > 2.0) or (cohens_d_withS > 0.3)
    np6_withS_result = 'PASS' if np6_withS_pass else 'FAIL'

    print(f"\n  NP6 (PCV delta full-B10):")
    print(f"    noS:   abs={abs_delta_noS:.5f}, rel={rel_delta_noS:.2f}%, "
          f"d={cohens_d_noS:.4f} [{np6_noS_result}]")
    print(f"    withS: abs={abs_delta_withS:.5f}, rel={rel_delta_withS:.2f}%, "
          f"d={cohens_d_withS:.4f} [{np6_withS_result}]")

    # =====================================================================
    # DIAGNOSTICS
    # =====================================================================
    print("\n" + "=" * 70)
    print("DIAGNOSTICS")
    print("=" * 70)

    # Non-S edge contacts
    total_warn_noS = sum(reference[f]['warning_contacts_noS'] for f in reference)
    total_hs_noS = sum(reference[f]['hardstop_contacts_noS'] for f in reference)
    total_warn_withS = sum(reference[f]['warning_contacts_withS'] for f in reference)
    total_hs_withS = sum(reference[f]['hardstop_contacts_withS'] for f in reference)
    total_warn_S = sum(reference[f]['warning_contacts_S_only'] for f in reference)
    total_hs_S = sum(reference[f]['hardstop_contacts_S_only'] for f in reference)

    total_edge_noS = total_warn_noS + total_hs_noS
    total_edge_withS = total_warn_withS + total_hs_withS
    total_edge_S = total_warn_S + total_hs_S

    # Note: withS doesn't include S above EQ. S_only counts all S edge contacts.
    # The "all edge contacts" is non-S + S
    total_all_edge = total_edge_noS + total_edge_S

    s_share_of_all = (total_edge_S / total_all_edge * 100) if total_all_edge > 0 else 0.0

    print(f"\n  Edge contact breakdown:")
    print(f"    Non-S warning contacts:  {total_warn_noS}")
    print(f"    Non-S hardstop contacts: {total_hs_noS}")
    print(f"    Non-S total edge:        {total_edge_noS}")
    print(f"    S-only warning contacts: {total_warn_S}")
    print(f"    S-only hardstop contacts:{total_hs_S}")
    print(f"    S-only total edge:       {total_edge_S}")
    print(f"    S share of all edge:     {s_share_of_all:.1f}%")

    # PCV correlation (noS vs withS)
    pcv_noS_vals = [reference[f]['PCV_noS'] for f in pilot_folio_list if f in reference]
    pcv_withS_vals = [reference[f]['PCV_withS'] for f in pilot_folio_list if f in reference]

    if len(pcv_noS_vals) > 2:
        n = len(pcv_noS_vals)
        mean_noS = mean(pcv_noS_vals)
        mean_withS_v = mean(pcv_withS_vals)
        cov = sum((pcv_noS_vals[i] - mean_noS) * (pcv_withS_vals[i] - mean_withS_v)
                   for i in range(n)) / (n - 1)
        std_noS = math.sqrt(sum((v - mean_noS) ** 2 for v in pcv_noS_vals) / (n - 1))
        std_withS_v = math.sqrt(sum((v - mean_withS_v) ** 2 for v in pcv_withS_vals) / (n - 1))
        pcv_correlation = cov / (std_noS * std_withS_v) if (std_noS * std_withS_v) > 0 else 0.0
    else:
        pcv_correlation = 0.0

    print(f"\n  PCV_noS vs PCV_withS correlation: r={pcv_correlation:.4f}")

    # SAHB ranges
    sahb_noS_vals = [reference[f]['SAHB_noS'] for f in pilot_folio_list if f in reference]
    sahb_withS_vals = [reference[f]['SAHB_withS'] for f in pilot_folio_list if f in reference]
    sahb_n1_noS_vals = [null_summaries['N1'][f]['mean_SAHB_noS']
                         for f in pilot_folio_list if f in null_summaries['N1']]

    print(f"\n  SAHB_noS range:  [{min(sahb_noS_vals):.4f}, {max(sahb_noS_vals):.4f}], "
          f"mean={mean(sahb_noS_vals):.4f}")
    print(f"  SAHB_withS range:[{min(sahb_withS_vals):.4f}, {max(sahb_withS_vals):.4f}], "
          f"mean={mean(sahb_withS_vals):.4f}")
    print(f"  SAHB_noS N1 mean: {mean(sahb_n1_noS_vals):.4f}")

    # =====================================================================
    # SIDE-BY-SIDE SUMMARY
    # =====================================================================
    print("\n" + "=" * 70)
    print("SIDE-BY-SIDE: NP RESULTS WITH S vs WITHOUT S")
    print("=" * 70)

    comparisons = [
        ('NP1', 'PCV > N1 mean', np1_withS_pass_count, np1_withS_result,
         np1_noS_pass_count, np1_noS_result),
        ('NP2', 'SAHB < N1 mean', np2_withS_pass_count, np2_withS_result,
         np2_noS_pass_count, np2_noS_result),
        ('NP3', 'QGY > N2 mean', np3_withS_pass_count, np3_withS_result,
         np3_noS_pass_count, np3_noS_result),
        ('NP4', 'QGY > N4 mean', np4_withS_pass_count, np4_withS_result,
         np4_noS_pass_count, np4_noS_result),
    ]

    print(f"\n  {'Test':<6} {'Description':<20} {'With S':>12} {'Without S':>12} {'Flipped?':>10}")
    print(f"  {'-'*6} {'-'*20} {'-'*12} {'-'*12} {'-'*10}")

    flipped_count = 0
    for test, desc, ws_count, ws_result, noS_count, noS_result in comparisons:
        flipped = ws_result != noS_result
        if flipped:
            flipped_count += 1
        flip_marker = "<-- YES" if flipped else ""
        print(f"  {test:<6} {desc:<20} {ws_count:>3}/20 {ws_result:>5} "
              f"{noS_count:>3}/20 {noS_result:>5} {flip_marker}")

    print(f"\n  NP6:")
    print(f"    With S:    abs={abs_delta_withS:.5f}, d={cohens_d_withS:.4f} [{np6_withS_result}]")
    print(f"    Without S: abs={abs_delta_noS:.5f}, d={cohens_d_noS:.4f} [{np6_noS_result}]")
    np6_flipped = np6_withS_result != np6_noS_result
    if np6_flipped:
        flipped_count += 1
        print(f"    <-- FLIPPED")

    # Compare with T4 results
    print(f"\n  Comparison with T4 validation (50 perms):")
    if t4_comparison and 'primary_tests' in t4_comparison:
        t4_tests = t4_comparison['primary_tests']
        for test_name in ['NP1', 'NP2', 'NP3', 'NP4', 'NP6']:
            if test_name in t4_tests:
                t4_result = t4_tests[test_name]['result']
                t4_n = t4_tests[test_name].get('n_folios_passing', '-')
                print(f"    {test_name} T4(50perm): {t4_result} ({t4_n}/20)")

    # =====================================================================
    # Per-folio detail table
    # =====================================================================
    print("\n" + "=" * 70)
    print("PER-FOLIO DETAIL")
    print("=" * 70)

    print(f"\n  {'Folio':<8} {'PCV_noS':>8} {'PCV_wS':>8} {'SAHB_noS':>9} "
          f"{'SAHB_wS':>9} {'QGY_noS':>8} {'QGY_wS':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*9} {'-'*9} {'-'*8} {'-'*8}")

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        r = reference[folio]
        print(f"  {folio:<8} {r['PCV_noS']:>8.4f} {r['PCV_withS']:>8.4f} "
              f"{r['SAHB_noS']:>9.4f} {r['SAHB_withS']:>9.4f} "
              f"{r['QGY_noS']:>8.4f} {r['QGY_withS']:>8.4f}")

    # =====================================================================
    # SUMMARY
    # =====================================================================
    total_elapsed = time.time() - t0
    print(f"\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    total_tests = 5  # NP1, NP2, NP3, NP4, NP6
    noS_passes = sum(1 for r in [np1_noS_result, np2_noS_result, np3_noS_result,
                                   np4_noS_result, np6_noS_result] if r == 'PASS')
    withS_passes = sum(1 for r in [np1_withS_result, np2_withS_result, np3_withS_result,
                                     np4_withS_result, np6_withS_result] if r == 'PASS')

    print(f"\n  Tests passed with S:    {withS_passes}/{total_tests}")
    print(f"  Tests passed without S: {noS_passes}/{total_tests}")
    print(f"  Tests flipped:          {flipped_count}/{total_tests}")
    print(f"  Total runs:             {run_count}")
    print(f"  Elapsed:                {total_elapsed:.1f}s")

    key_finding = ""
    if noS_passes > withS_passes:
        key_finding = "S exclusion IMPROVES discrimination (more tests pass)"
    elif noS_passes < withS_passes:
        key_finding = "S exclusion HURTS discrimination (fewer tests pass)"
    else:
        key_finding = "S exclusion has NO NET EFFECT on discrimination (same pass count)"
    print(f"\n  KEY FINDING: {key_finding}")

    # =====================================================================
    # Build output JSON
    # =====================================================================
    reference_out = {}
    for f in reference:
        reference_out[f] = {k: round(v, 6) if isinstance(v, float) else v
                             for k, v in reference[f].items()}

    nulls_out = {}
    for nn in null_summaries:
        nulls_out[nn] = {}
        for f in null_summaries[nn]:
            nulls_out[nn][f] = null_summaries[nn][f]

    baselines_out = {}
    for f in b10_results:
        baselines_out[f] = {k: round(v, 6) if isinstance(v, float) else v
                             for k, v in b10_results[f].items()}

    output = {
        'metadata': {
            'purpose': 'S-exclusion reanalysis of Phase 567 data',
            'n_reference_runs': len(reference),
            'n_null_perms': N_PERMS,
            'svs_included': ['T', 'RC', 'C', 'TR', 'X'],
            'svs_excluded': ['S', 'Y'],
            'total_runs': run_count,
            'elapsed_seconds': round(total_elapsed, 2),
            'timestamp': datetime.now().isoformat(),
        },
        'reference': reference_out,
        'nulls': {
            'N1': nulls_out.get('N1', {}),
            'N2': nulls_out.get('N2', {}),
            'N4': nulls_out.get('N4', {}),
        },
        'baselines': {
            'B10': baselines_out,
        },
        'tests': {
            'NP1_noS': {
                'result': np1_noS_result,
                'n_folios': np1_noS_pass_count,
                'threshold': 14,
                'details': np1_noS_details,
            },
            'NP2_noS': {
                'result': np2_noS_result,
                'n_folios': np2_noS_pass_count,
                'threshold': 14,
                'details': np2_noS_details,
            },
            'NP3_noS': {
                'result': np3_noS_result,
                'n_folios': np3_noS_pass_count,
                'threshold': 14,
                'details': np3_noS_details,
            },
            'NP4_noS': {
                'result': np4_noS_result,
                'n_folios': np4_noS_pass_count,
                'threshold': 14,
                'details': np4_noS_details,
            },
            'NP6_noS': {
                'result': np6_noS_result,
                'abs_delta': round(abs_delta_noS, 6),
                'rel_delta_pct': round(rel_delta_noS, 4),
                'cohens_d': round(cohens_d_noS, 6),
                'mean_full_PCV_noS': round(mean_full_noS, 6),
                'mean_B10_PCV_noS': round(mean_b10_noS, 6),
            },
        },
        'comparison': {
            'NP1_withS': {'result': np1_withS_result, 'n_folios': np1_withS_pass_count},
            'NP1_noS': {'result': np1_noS_result, 'n_folios': np1_noS_pass_count},
            'NP2_withS': {'result': np2_withS_result, 'n_folios': np2_withS_pass_count},
            'NP2_noS': {'result': np2_noS_result, 'n_folios': np2_noS_pass_count},
            'NP3_withS': {'result': np3_withS_result, 'n_folios': np3_withS_pass_count},
            'NP3_noS': {'result': np3_noS_result, 'n_folios': np3_noS_pass_count},
            'NP4_withS': {'result': np4_withS_result, 'n_folios': np4_withS_pass_count},
            'NP4_noS': {'result': np4_noS_result, 'n_folios': np4_noS_pass_count},
            'NP6_withS': {
                'result': np6_withS_result,
                'abs_delta': round(abs_delta_withS, 6),
                'cohens_d': round(cohens_d_withS, 6),
            },
            'NP6_noS': {
                'result': np6_noS_result,
                'abs_delta': round(abs_delta_noS, 6),
                'cohens_d': round(cohens_d_noS, 6),
            },
        },
        'diagnostics': {
            'non_s_edge_contacts_total': total_edge_noS,
            'non_s_warning_contacts': total_warn_noS,
            'non_s_hardstop_contacts': total_hs_noS,
            's_only_edge_contacts_total': total_edge_S,
            's_share_of_all_edge_pct': round(s_share_of_all, 2),
            'pcv_noS_vs_pcv_withS_correlation': round(pcv_correlation, 6),
            'sahb_noS_range': [round(min(sahb_noS_vals), 6), round(max(sahb_noS_vals), 6)],
            'sahb_noS_mean_full': round(mean(sahb_noS_vals), 6),
            'sahb_noS_mean_n1': round(mean(sahb_n1_noS_vals), 6),
            'sahb_withS_range': [round(min(sahb_withS_vals), 6), round(max(sahb_withS_vals), 6)],
            'sahb_withS_mean_full': round(mean(sahb_withS_vals), 6),
            'key_finding': key_finding,
            'tests_flipped': flipped_count,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = OUTPUT_PATH.stat().st_size
    print(f"\n  Output: {OUTPUT_PATH}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print("\n  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
