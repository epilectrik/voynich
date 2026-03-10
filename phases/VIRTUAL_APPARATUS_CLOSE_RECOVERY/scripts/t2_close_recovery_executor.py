"""
T2: Close Recovery Executor
Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY

Runs 20 pilot folios through the CloseRecoveryApparatus (from T1)
with a single-channel permissivity buffer for routing.  90 total runs:
  - 60 primary: 20 folios x 3 profiles (each folio uses its assigned config)
  - 30 config ablation: 10 folios x preferred profile x 3 config modes

Single-channel routing (same as 564b/565):
  Single permissivity buffer that shifts effective q2 boundaries.
  Buffer decays by 0.7 per token and resets at line boundaries.

Additional logging beyond 565 T2:
  - CLOSE recovery R1-R5 channel totals
  - Phase-asymmetry (WORK vs CLOSE deviation changes)
  - Y tracking
  - Corridor return latency events
"""

import json
import math
import sys
import time
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Import T1 close recovery apparatus
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
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

# Config ablation folios (first 10 pilot folios)
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
# Excursion detection helpers
# ---------------------------------------------------------------------------

def _is_quiet(state):
    """All process SVs have |dev| < Q1."""
    return all(abs(state[i] - EQUILIBRIUM) < Q1 for i in PROCESS_IDX)


def _is_excursion(state):
    """Any process SV has |dev| >= Q1."""
    return any(abs(state[i] - EQUILIBRIUM) >= Q1 for i in PROCESS_IDX)


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------

def run_coupled_trace(apparatus, tokens, line_packets):
    """
    Run one folio through the CloseRecoveryApparatus.

    apparatus:    CloseRecoveryApparatus instance
    tokens:       list of token dicts, pre-sorted by (line, position)
    line_packets: dict mapping "folio|line" -> packet info

    Returns dict with run summary including CLOSE recovery logging.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'n_tokens': 0,
            'viability': 0.0,
            'n_hazard_events': 0,
            'Y_final': 0.5,
            'mean_state': [0.5] * N_VARS,
            'excursion_count': 0,
            'bounded_excursion_count': 0,
            'zone_occupancy': {sv: {'basin': 0.0, 'corridor': 0.0,
                                     'warning': 0.0, 'hard_stop': 0.0}
                               for sv in STATE_VARS},
            'warning_contacts': {sv: 0 for sv in STATE_VARS},
            'hard_stop_contacts': {sv: 0 for sv in STATE_VARS},
            'edge_by_phase': {phase: {sv: 0 for sv in STATE_VARS}
                              for phase in ['SPEC', 'WORK', 'CLOSE']},
            'discharge_events': {
                'cts_discharge': {'count': 0, 'total_magnitude': 0.0},
                'containment_resolution': {'count': 0, 'total_magnitude': 0.0},
                'thermal_recovery': {'count': 0, 'total_magnitude': 0.0},
            },
            'state_trajectory_summary': {sv: {'min': 0.5, 'max': 0.5, 'mean': 0.5, 'std': 0.0}
                                          for sv in STATE_VARS},
            'close_recovery_R1': {sv: 0.0 for sv in STATE_VARS if sv != 'Y'},
            'close_recovery_R2': 0.0,
            'close_recovery_R3': 0.0,
            'close_recovery_R4': 0.0,
            'close_recovery_R5': 0.0,
            'close_recovery_total': 0.0,
            'work_deviation_change': {sv: 0.0 for sv in STATE_VARS},
            'close_deviation_change': {sv: 0.0 for sv in STATE_VARS},
            'y_final': 0.5,
            'corridor_return_events': [],
        }

    state = [EQUILIBRIUM] * N_VARS
    permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
    prev_line = None

    # Accumulators
    viable_count = 0
    hazard_count = 0
    state_sum = [0.0] * N_VARS
    state_sq_sum = [0.0] * N_VARS
    state_min = [1.0] * N_VARS
    state_max = [0.0] * N_VARS

    # Zone occupancy counters (4-zone)
    zone_counts = {sv: {'BASIN': 0, 'CORRIDOR': 0, 'WARNING': 0, 'HARD_STOP': 0}
                   for sv in STATE_VARS}

    # Per-SV warning and hard_stop contact counters
    warning_contacts = {sv: 0 for sv in STATE_VARS}
    hard_stop_contacts = {sv: 0 for sv in STATE_VARS}

    # Edge (warning + hard_stop) contacts broken down by packet_phase
    edge_by_phase = {phase: {sv: 0 for sv in STATE_VARS}
                     for phase in ['SPEC', 'WORK', 'CLOSE']}

    # Discharge event accumulators
    cts_discharge_count = 0
    cts_discharge_mag = 0.0
    containment_res_count = 0
    containment_res_mag = 0.0
    thermal_rec_count = 0
    thermal_rec_mag = 0.0

    # Excursion cycle tracking
    in_excursion = False
    excursion_start = None
    excursion_count = 0
    bounded_excursion_count = 0

    # Line packet mismatch counter
    lp_mismatches = 0

    # --- CLOSE recovery accumulators (NEW in 566 T2) ---
    close_recovery_R1 = {sv: 0.0 for sv in STATE_VARS if sv != 'Y'}
    close_recovery_R2 = 0.0
    close_recovery_R3 = 0.0
    close_recovery_R4 = 0.0
    close_recovery_R5 = 0.0

    # --- Phase-asymmetry tracking ---
    # Track per-SV deviation changes during WORK and CLOSE tokens
    work_dev_change_sum = {sv: 0.0 for sv in STATE_VARS}
    work_dev_change_count = 0
    close_dev_change_sum = {sv: 0.0 for sv in STATE_VARS}
    close_dev_change_count = 0

    # --- Corridor return latency tracking ---
    # Track excursions past Q1 for each SV and how many tokens to return below Q2_BASE
    corridor_return_events = []
    # Per-SV: whether we are tracking an excursion (past Q1) waiting for return below Q2_BASE
    sv_excursion_active = {sv: False for sv in PROCESS_SVS}
    sv_excursion_start_idx = {sv: 0 for sv in PROCESS_SVS}
    sv_excursion_peak_dev = {sv: 0.0 for sv in PROCESS_SVS}

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']

        # Record pre-update deviations for phase-asymmetry tracking
        pre_devs = {sv: abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in STATE_VARS}

        # 1. Line boundary check: reset permissivity buffer
        if current_line != prev_line:
            permissivity_buffer = {sv: 0.0 for sv in STATE_VARS}
            prev_line = current_line

        # 2. Routing: accumulate permissivity shifts
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_PERMISSIVITY:
                for sv, shift in ROUTING_PERMISSIVITY[rt].items():
                    permissivity_buffer[sv] += shift

        # 3. Packet phase and CTS lookup
        packet_phase = tok.get('packet_phase', None)
        cts = tok.get('cts', 0.0)

        if packet_phase is None:
            lp_key = f"{folio}|{current_line}"
            if lp_key in line_packets:
                lp = line_packets[lp_key]
                packet_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
            else:
                packet_phase = 'WORK'
                lp_mismatches += 1

        # 4. Compute dV
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            dV[i] = contributions[i] * apparatus.sensitivity[sv]

        # 5. Call apparatus.update with permissivity buffer
        perm_dict = {sv: v for sv, v in permissivity_buffer.items() if abs(v) > 1e-8}
        state, diagnostics = apparatus.update(
            state, dV, packet_phase, cts,
            permissivity=perm_dict if perm_dict else None
        )

        # 6. Decay permissivity buffer
        for sv in STATE_VARS:
            permissivity_buffer[sv] *= ROUTING_DECAY

        # 7. Record state statistics
        for i in range(N_VARS):
            state_sum[i] += state[i]
            state_sq_sum[i] += state[i] ** 2
            if state[i] < state_min[i]:
                state_min[i] = state[i]
            if state[i] > state_max[i]:
                state_max[i] = state[i]

        # 8. Zone classification per SV (4-zone)
        zones = diagnostics['zones']
        for sv in STATE_VARS:
            zone = zones[sv]
            zone_counts[sv][zone] += 1

            if zone == 'WARNING':
                warning_contacts[sv] += 1
                edge_by_phase[packet_phase][sv] += 1
            elif zone == 'HARD_STOP':
                hard_stop_contacts[sv] += 1
                edge_by_phase[packet_phase][sv] += 1

        # 9. Discharge event logging
        for evt in diagnostics.get('discharge_events', []):
            evt_type = evt['type']
            rate = evt['rate']
            if evt_type == 'CTS_DISCHARGE':
                cts_discharge_count += 1
                cts_discharge_mag += abs(rate)
            elif evt_type == 'CONTAINMENT_RESOLUTION':
                containment_res_count += 1
                containment_res_mag += abs(rate)
            elif evt_type == 'THERMAL_RECOVERY':
                thermal_rec_count += 1
                thermal_rec_mag += abs(rate)

        # 10. Viability check
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

        # 11. Excursion tracking
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

        # --- 12. CLOSE recovery accumulation (NEW) ---
        cr = diagnostics.get('close_recovery', {})

        # R1: per-SV recovery
        r1_data = cr.get('R1', {})
        for sv, val in r1_data.items():
            if sv in close_recovery_R1:
                close_recovery_R1[sv] += val

        # R2: CTS X->Y transfer
        r2_data = cr.get('R2', {})
        if r2_data:
            close_recovery_R2 += r2_data.get('rate', 0.0)

        # R3: containment-TR relief
        r3_data = cr.get('R3', {})
        if r3_data:
            close_recovery_R3 += r3_data.get('rate', 0.0)

        # R4: Y accumulation
        r4_data = cr.get('R4', {})
        if r4_data:
            close_recovery_R4 += r4_data.get('y_gain', 0.0)

        # R5: coordination bonus
        r5_data = cr.get('R5', {})
        if r5_data:
            # Sum up the additional bonus applied to each SV
            bonus = r5_data.get('bonus', 1.0)
            n_coherent = r5_data.get('n_coherent', 0)
            svs = r5_data.get('svs', [])
            # R5 bonus magnitude: sum of additional recovery from R5
            r5_additional = 0.0
            for sv in svs:
                r1_val = r1_data.get(sv, 0.0)
                if r1_val > 0:
                    r5_additional += r1_val * (bonus - 1.0)
            close_recovery_R5 += r5_additional

        # --- 13. Phase-asymmetry tracking (NEW) ---
        post_devs = {sv: abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in STATE_VARS}
        if packet_phase == 'WORK':
            work_dev_change_count += 1
            for sv in STATE_VARS:
                work_dev_change_sum[sv] += (post_devs[sv] - pre_devs[sv])
        elif packet_phase == 'CLOSE':
            close_dev_change_count += 1
            for sv in STATE_VARS:
                close_dev_change_sum[sv] += (post_devs[sv] - pre_devs[sv])

        # --- 14. Corridor return latency tracking (NEW) ---
        for sv in PROCESS_SVS:
            i = SV_INDEX[sv]
            abs_dev = abs(state[i] - EQUILIBRIUM)

            if not sv_excursion_active[sv]:
                # Check if WORK-phase excursion pushes |dev| past Q1
                if packet_phase == 'WORK' and abs_dev >= Q1:
                    sv_excursion_active[sv] = True
                    sv_excursion_start_idx[sv] = tok_idx
                    sv_excursion_peak_dev[sv] = abs_dev
            else:
                # Track peak
                if abs_dev > sv_excursion_peak_dev[sv]:
                    sv_excursion_peak_dev[sv] = abs_dev

                # Check if returned below Q2_BASE
                if abs_dev < Q2_BASE[sv]:
                    corridor_return_events.append({
                        'sv': sv,
                        'excursion_token_idx': sv_excursion_start_idx[sv],
                        'return_token_idx': tok_idx,
                        'latency': tok_idx - sv_excursion_start_idx[sv],
                        'peak_dev': round(sv_excursion_peak_dev[sv], 5),
                    })
                    sv_excursion_active[sv] = False

    # Compute summary statistics
    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]
    std_state = []
    for i in range(N_VARS):
        variance = (state_sq_sum[i] / n_tokens) - (mean_state[i] ** 2)
        std_state.append(math.sqrt(max(0.0, variance)))

    # Build zone occupancy fractions (4-zone)
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

    # Build state trajectory summary
    state_trajectory_summary = {}
    for i, sv in enumerate(STATE_VARS):
        state_trajectory_summary[sv] = {
            'min': round(state_min[i], 5),
            'max': round(state_max[i], 5),
            'mean': round(mean_state[i], 5),
            'std': round(std_state[i], 5),
        }

    # Compute close recovery total
    close_recovery_total = (
        sum(close_recovery_R1.values())
        + close_recovery_R2
        + close_recovery_R3
        + close_recovery_R4
        + close_recovery_R5
    )

    # Compute phase-asymmetry means
    work_deviation_change = {}
    close_deviation_change = {}
    for sv in STATE_VARS:
        if work_dev_change_count > 0:
            work_deviation_change[sv] = round(work_dev_change_sum[sv] / work_dev_change_count, 6)
        else:
            work_deviation_change[sv] = 0.0
        if close_dev_change_count > 0:
            close_deviation_change[sv] = round(close_dev_change_sum[sv] / close_dev_change_count, 6)
        else:
            close_deviation_change[sv] = 0.0

    result = {
        'n_tokens': n_tokens,
        'viability': round(viable_count / n_tokens, 5),
        'n_hazard_events': hazard_count,
        'Y_final': round(state[SV_INDEX['Y']], 5),
        'mean_state': [round(v, 5) for v in mean_state],
        'excursion_count': excursion_count,
        'bounded_excursion_count': bounded_excursion_count,
        'zone_occupancy': zone_occupancy,
        'warning_contacts': warning_contacts,
        'hard_stop_contacts': hard_stop_contacts,
        'edge_by_phase': edge_by_phase,
        'discharge_events': {
            'cts_discharge': {
                'count': cts_discharge_count,
                'total_magnitude': round(cts_discharge_mag, 5),
            },
            'containment_resolution': {
                'count': containment_res_count,
                'total_magnitude': round(containment_res_mag, 5),
            },
            'thermal_recovery': {
                'count': thermal_rec_count,
                'total_magnitude': round(thermal_rec_mag, 5),
            },
        },
        'state_trajectory_summary': state_trajectory_summary,
        # --- CLOSE recovery logging (NEW) ---
        'close_recovery_R1': {sv: round(v, 5) for sv, v in close_recovery_R1.items()},
        'close_recovery_R2': round(close_recovery_R2, 5),
        'close_recovery_R3': round(close_recovery_R3, 5),
        'close_recovery_R4': round(close_recovery_R4, 5),
        'close_recovery_R5': round(close_recovery_R5, 5),
        'close_recovery_total': round(close_recovery_total, 5),
        # --- Phase-asymmetry logging (NEW) ---
        'work_deviation_change': work_deviation_change,
        'close_deviation_change': close_deviation_change,
        # --- Y tracking (NEW) ---
        'y_final': round(state[SV_INDEX['Y']], 5),
        # --- Corridor return latency (NEW) ---
        'corridor_return_events': corridor_return_events,
    }

    if lp_mismatches > 0:
        result['lp_mismatches'] = lp_mismatches

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    project_root = phase_dir.parent.parent

    output_path = phase_dir / 'results' / 't2_close_recovery_runs.json'

    # --- Data source paths ---
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    t1_path = phase_dir / 'results' / 't1_close_recovery_apparatus.json'
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')

    print("=" * 70)
    print("T2: Close Recovery Executor")
    print("Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY")
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

    # Build preferred profile map for pilot folios
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

    # Sort each folio's tokens by (line, line_pos)
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
    primary_runs = []
    run_count = 0

    for folio in PILOT_FOLIOS:
        toks = tokens_by_folio[folio]
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        infra = folio_infra_scores.get(folio, {})
        config_mode = infra.get('config_mode', 'H1_MEDIUM_INFRA')
        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')

        for profile_name in PROFILE_NAMES:
            # Build apparatus with this profile and the folio's config mode
            apparatus = build_configured_apparatus(profile_name, config_mode)

            result = run_coupled_trace(apparatus, toks, line_packets)

            run_key = f"{folio}_{profile_name}_{config_mode}"
            run_entry = {
                'run_key': run_key,
                'folio': folio,
                'profile': profile_name,
                'config_mode': config_mode,
                'n_tokens': result['n_tokens'],
                'viability': result['viability'],
                'n_hazard_events': result['n_hazard_events'],
                'Y_final': result['Y_final'],
                'mean_state': result['mean_state'],
                'excursion_count': result['excursion_count'],
                'bounded_excursion_count': result['bounded_excursion_count'],
                'zone_occupancy': result['zone_occupancy'],
                'warning_contacts': result['warning_contacts'],
                'hard_stop_contacts': result['hard_stop_contacts'],
                'edge_by_phase': result['edge_by_phase'],
                'discharge_events': result['discharge_events'],
                'state_trajectory_summary': result['state_trajectory_summary'],
                # CLOSE recovery logging
                'close_recovery_R1': result['close_recovery_R1'],
                'close_recovery_R2': result['close_recovery_R2'],
                'close_recovery_R3': result['close_recovery_R3'],
                'close_recovery_R4': result['close_recovery_R4'],
                'close_recovery_R5': result['close_recovery_R5'],
                'close_recovery_total': result['close_recovery_total'],
                # Phase-asymmetry
                'work_deviation_change': result['work_deviation_change'],
                'close_deviation_change': result['close_deviation_change'],
                # Y tracking
                'y_final': result['y_final'],
                # Corridor return latency
                'corridor_return_events': result['corridor_return_events'],
            }
            if result.get('lp_mismatches'):
                run_entry['lp_mismatches'] = result['lp_mismatches']

            primary_runs.append(run_entry)
            run_count += 1

            is_pref = (profile_name == preferred_profile)
            pref_tag = " *PREFERRED*" if is_pref else ""
            via = result['viability']
            haz = result['n_hazard_events']
            yf = result['y_final']
            exc = result['excursion_count']
            bnd = result['bounded_excursion_count']
            warn_total = sum(result['warning_contacts'].values())
            hs_total = sum(result['hard_stop_contacts'].values())
            cr_total = result['close_recovery_total']
            print(f"  [{run_count:2d}/60] {folio} + {profile_name} [{config_mode}]: "
                  f"viab={via:.4f}, hazards={haz}, Y_final={yf:.4f}, "
                  f"cycles={exc}, bounded={bnd}, warn={warn_total}, hs={hs_total}, "
                  f"CR_total={cr_total:.4f}{pref_tag}")

    # --- Config ablation runs (30): 10 folios x preferred profile x 3 config modes ---
    print("\n--- Config Ablation Runs (30) ---")
    config_ablation_runs = []
    ablation_count = 0

    for folio in CONFIG_ABLATION_FOLIOS:
        toks = tokens_by_folio.get(folio, [])
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        preferred_profile = preferred_profile_map.get(folio, 'A1_BATH_REFLUX')

        for cm in CONFIG_MODE_NAMES:
            apparatus = build_configured_apparatus(preferred_profile, cm)
            result = run_coupled_trace(apparatus, toks, line_packets)

            run_key = f"ABL_{folio}_{preferred_profile}_{cm}"
            abl_entry = {
                'run_key': run_key,
                'folio': folio,
                'profile': preferred_profile,
                'config_mode': cm,
                'n_tokens': result['n_tokens'],
                'viability': result['viability'],
                'n_hazard_events': result['n_hazard_events'],
                'Y_final': result['Y_final'],
                'mean_state': result['mean_state'],
                'excursion_count': result['excursion_count'],
                'bounded_excursion_count': result['bounded_excursion_count'],
                'zone_occupancy': result['zone_occupancy'],
                'warning_contacts': result['warning_contacts'],
                'hard_stop_contacts': result['hard_stop_contacts'],
                'edge_by_phase': result['edge_by_phase'],
                'discharge_events': result['discharge_events'],
                'state_trajectory_summary': result['state_trajectory_summary'],
                # CLOSE recovery logging
                'close_recovery_R1': result['close_recovery_R1'],
                'close_recovery_R2': result['close_recovery_R2'],
                'close_recovery_R3': result['close_recovery_R3'],
                'close_recovery_R4': result['close_recovery_R4'],
                'close_recovery_R5': result['close_recovery_R5'],
                'close_recovery_total': result['close_recovery_total'],
                # Phase-asymmetry
                'work_deviation_change': result['work_deviation_change'],
                'close_deviation_change': result['close_deviation_change'],
                # Y tracking
                'y_final': result['y_final'],
                # Corridor return latency
                'corridor_return_events': result['corridor_return_events'],
            }
            if result.get('lp_mismatches'):
                abl_entry['lp_mismatches'] = result['lp_mismatches']

            config_ablation_runs.append(abl_entry)
            ablation_count += 1

            via = result['viability']
            haz = result['n_hazard_events']
            cr_total = result['close_recovery_total']
            print(f"  [{ablation_count:2d}/30] {folio} + {preferred_profile} + {cm}: "
                  f"viab={via:.4f}, hazards={haz}, CR_total={cr_total:.4f}")

    # --- Build summary ---
    print("\n--- Building output ---")

    # Compute summary statistics from preferred-profile runs
    pref_viabilities = []
    pref_hazards = []
    pref_y_finals = []
    pref_cr_totals = []
    total_warning = 0
    total_hardstop = 0

    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            pref_viabilities.append(run['viability'])
            pref_hazards.append(run['n_hazard_events'])
            pref_y_finals.append(run['y_final'])
            pref_cr_totals.append(run['close_recovery_total'])
            total_warning += sum(run['warning_contacts'].values())
            total_hardstop += sum(run['hard_stop_contacts'].values())

    n_pref = len(pref_viabilities)
    mean_pref_viability = sum(pref_viabilities) / n_pref if n_pref > 0 else 0.0
    mean_y_final = sum(pref_y_finals) / n_pref if n_pref > 0 else 0.5
    mean_cr_total = sum(pref_cr_totals) / n_pref if n_pref > 0 else 0.0

    # Build keyed runs dict
    runs_dict = {}
    for run in primary_runs:
        runs_dict[run['run_key']] = run
    for run in config_ablation_runs:
        runs_dict[run['run_key']] = run

    output = {
        'metadata': {
            'phase': '566',
            'task': 'T2',
            'phase_name': 'VIRTUAL_APPARATUS_CLOSE_RECOVERY',
            'timestamp': datetime.now().isoformat(),
            'n_primary': len(primary_runs),
            'n_config_ablation': len(config_ablation_runs),
            'n_total': len(primary_runs) + len(config_ablation_runs),
        },
        'summary': {
            'n_runs': len(primary_runs) + len(config_ablation_runs),
            'mean_preferred_viability': round(mean_pref_viability, 5),
            'total_hazard_events': sum(pref_hazards),
            'total_warning_contacts': total_warning,
            'total_hard_stop_contacts': total_hardstop,
            'mean_y_final': round(mean_y_final, 5),
            'mean_close_recovery_total': round(mean_cr_total, 5),
        },
        'runs': runs_dict,
        'preferred_profile_map': preferred_profile_map,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = output_path.stat().st_size
    print(f"\n  Output: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # --- Final statistics ---
    print("\n--- Final Statistics ---")

    # Primary run stats (preferred profile only)
    pref_excursions = []
    pref_bounded = []
    pref_warning_totals = []
    pref_hardstop_totals = []

    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            pref_excursions.append(run['excursion_count'])
            pref_bounded.append(run['bounded_excursion_count'])
            pref_warning_totals.append(sum(run['warning_contacts'].values()))
            pref_hardstop_totals.append(sum(run['hard_stop_contacts'].values()))

    if pref_viabilities:
        min_via = min(pref_viabilities)
        max_via = max(pref_viabilities)
        mean_exc = sum(pref_excursions) / len(pref_excursions)
        mean_bnd = sum(pref_bounded) / len(pref_bounded)
        print(f"  Preferred-profile viability: "
              f"mean={mean_pref_viability:.4f}, min={min_via:.4f}, max={max_via:.4f}")
        print(f"  Total hazard events (preferred): {sum(pref_hazards)}")
        print(f"  Mean excursion cycles (preferred): {mean_exc:.1f}")
        print(f"  Mean bounded excursions (preferred): {mean_bnd:.1f}")
        print(f"  Total warning contacts (preferred): {sum(pref_warning_totals)}")
        print(f"  Total hard_stop contacts (preferred): {sum(pref_hardstop_totals)}")
        print(f"  Mean Y final (preferred): {mean_y_final:.4f}")
        print(f"  Mean CLOSE recovery total (preferred): {mean_cr_total:.4f}")

    # CLOSE recovery channel breakdown (preferred runs)
    print("\n  CLOSE recovery channel breakdown (preferred runs, totals):")
    r1_sums = {sv: 0.0 for sv in STATE_VARS if sv != 'Y'}
    r2_sum = 0.0
    r3_sum = 0.0
    r4_sum = 0.0
    r5_sum = 0.0
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            for sv, val in run['close_recovery_R1'].items():
                r1_sums[sv] += val
            r2_sum += run['close_recovery_R2']
            r3_sum += run['close_recovery_R3']
            r4_sum += run['close_recovery_R4']
            r5_sum += run['close_recovery_R5']

    r1_total = sum(r1_sums.values())
    print(f"    R1 (per-SV drawdown): {r1_total:.4f}")
    for sv in sorted(r1_sums.keys()):
        if r1_sums[sv] > 0:
            print(f"      {sv}: {r1_sums[sv]:.4f}")
    print(f"    R2 (CTS X->Y transfer): {r2_sum:.4f}")
    print(f"    R3 (containment-TR relief): {r3_sum:.4f}")
    print(f"    R4 (Y accumulation): {r4_sum:.4f}")
    print(f"    R5 (coordination bonus): {r5_sum:.4f}")

    # Phase-asymmetry summary (preferred runs)
    print("\n  Phase-asymmetry (preferred runs, mean per-SV deviation change):")
    work_dc_avg = {sv: 0.0 for sv in STATE_VARS}
    close_dc_avg = {sv: 0.0 for sv in STATE_VARS}
    n_pa = 0
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            n_pa += 1
            for sv in STATE_VARS:
                work_dc_avg[sv] += run['work_deviation_change'][sv]
                close_dc_avg[sv] += run['close_deviation_change'][sv]

    if n_pa > 0:
        for sv in STATE_VARS:
            work_dc_avg[sv] /= n_pa
            close_dc_avg[sv] /= n_pa
        print(f"    {'SV':>4s}  {'WORK':>10s}  {'CLOSE':>10s}")
        for sv in STATE_VARS:
            print(f"    {sv:>4s}  {work_dc_avg[sv]:>+10.6f}  {close_dc_avg[sv]:>+10.6f}")

    # Corridor return latency summary (preferred runs)
    print("\n  Corridor return latency (preferred runs):")
    all_latencies = []
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            all_latencies.extend(run['corridor_return_events'])

    if all_latencies:
        lats = [e['latency'] for e in all_latencies]
        mean_lat = sum(lats) / len(lats)
        min_lat = min(lats)
        max_lat = max(lats)
        peaks = [e['peak_dev'] for e in all_latencies]
        mean_peak = sum(peaks) / len(peaks)
        print(f"    Total events: {len(all_latencies)}")
        print(f"    Latency: mean={mean_lat:.1f}, min={min_lat}, max={max_lat}")
        print(f"    Peak deviation: mean={mean_peak:.4f}")

        # Breakdown by SV
        sv_lats = {}
        for e in all_latencies:
            sv = e['sv']
            if sv not in sv_lats:
                sv_lats[sv] = []
            sv_lats[sv].append(e['latency'])
        for sv in sorted(sv_lats.keys()):
            sl = sv_lats[sv]
            print(f"    {sv}: n={len(sl)}, mean_latency={sum(sl)/len(sl):.1f}")
    else:
        print("    No corridor return events recorded")

    # Zone occupancy summary (preferred runs, 4-zone)
    print("\n  Zone occupancy (preferred runs, averaged):")
    zone_sums = {sv: {'basin': 0.0, 'corridor': 0.0, 'warning': 0.0, 'hard_stop': 0.0}
                 for sv in STATE_VARS}
    zone_n = 0
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            zone_n += 1
            for sv in STATE_VARS:
                for z in ['basin', 'corridor', 'warning', 'hard_stop']:
                    zone_sums[sv][z] += run['zone_occupancy'][sv][z]

    if zone_n > 0:
        for sv in STATE_VARS:
            b = zone_sums[sv]['basin'] / zone_n
            c = zone_sums[sv]['corridor'] / zone_n
            w = zone_sums[sv]['warning'] / zone_n
            h = zone_sums[sv]['hard_stop'] / zone_n
            print(f"    {sv}: basin={b:.3f}, corridor={c:.3f}, warning={w:.3f}, hard_stop={h:.3f}")

    # Edge-by-phase summary (preferred runs only)
    print("\n  Edge contacts by phase (preferred runs, totals):")
    phase_edge_sums = {phase: {sv: 0 for sv in STATE_VARS}
                       for phase in ['SPEC', 'WORK', 'CLOSE']}
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            for phase in ['SPEC', 'WORK', 'CLOSE']:
                for sv in STATE_VARS:
                    phase_edge_sums[phase][sv] += run['edge_by_phase'][phase][sv]

    for phase in ['SPEC', 'WORK', 'CLOSE']:
        total_phase = sum(phase_edge_sums[phase].values())
        sv_details = ', '.join(f"{sv}={phase_edge_sums[phase][sv]}"
                               for sv in STATE_VARS
                               if phase_edge_sums[phase][sv] > 0)
        print(f"    {phase}: total={total_phase}" + (f" ({sv_details})" if sv_details else ""))

    print(f"\n  Total runs: {len(primary_runs) + len(config_ablation_runs)}")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
