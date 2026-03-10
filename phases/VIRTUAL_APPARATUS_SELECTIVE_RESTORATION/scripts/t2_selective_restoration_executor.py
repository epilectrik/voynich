"""
T2: Selective Restoration Executor
Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION

Runs 20 pilot folios through the selective restoration apparatus (from T1)
with a single-channel permissivity buffer for routing.  90 total runs:
  - 60 primary: 20 folios x 3 profiles (each folio uses its assigned config)
  - 30 config ablation: 10 folios x preferred profile x 3 config modes

Single-channel routing (key change from 564):
  Instead of dual-channel routing (contribution modulation + threshold shifts),
  564b uses a single permissivity buffer that shifts effective q2 boundaries.
  Buffer decays by 0.7 per token and resets at line boundaries.
"""

import json
import math
import sys
import time
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Import T1 selective restoration apparatus
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t1_selective_restoration_apparatus import (
    SelectiveRestorationApparatus, build_configured_apparatus,
    compute_infra_scores, STATE_VARS, Q1, Q2_BASE, HAZARD_BOUNDARIES,
    N_VARS, EQUILIBRIUM, SV_INDEX, PILOT_FOLIOS, PROFILES,
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
# Zone classification
# ---------------------------------------------------------------------------

def classify_zone(dev_abs, eff_q2):
    """Classify zone for a single SV given |deviation| and effective q2."""
    if dev_abs < Q1:
        return 'BASIN'
    elif dev_abs < eff_q2:
        return 'CORRIDOR'
    else:
        return 'EDGE'


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------

def run_coupled_trace(apparatus, tokens, line_packets):
    """
    Run one folio through the selective restoration apparatus.

    apparatus:    SelectiveRestorationApparatus instance
    tokens:       list of token dicts, pre-sorted by (line, position)
    line_packets: dict mapping "folio|line" -> packet info

    Returns dict with run summary.
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
            'zone_occupancy': {sv: {'basin': 0.0, 'corridor': 0.0, 'edge': 0.0}
                               for sv in STATE_VARS},
            'discharge_events': {
                'cts_discharge': {'count': 0, 'total_magnitude': 0.0},
                'containment_resolution': {'count': 0, 'total_magnitude': 0.0},
                'thermal_recovery': {'count': 0, 'total_magnitude': 0.0},
            },
            'state_trajectory_summary': {sv: {'min': 0.5, 'max': 0.5, 'mean': 0.5, 'std': 0.0}
                                          for sv in STATE_VARS},
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

    # Zone occupancy counters
    zone_counts = {sv: {'BASIN': 0, 'CORRIDOR': 0, 'EDGE': 0} for sv in STATE_VARS}

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

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']

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
        #    Primary source: token itself (supervisory tokens carry packet_phase and cts)
        #    Fallback: line packets file
        packet_phase = tok.get('packet_phase', None)
        cts = tok.get('cts', 0.0)

        if packet_phase is None:
            # Fall back to line packets
            lp_key = f"{folio}|{current_line}"
            if lp_key in line_packets:
                lp = line_packets[lp_key]
                packet_phase = lp.get('packet_state', {}).get('packet_phase', 'WORK')
            else:
                packet_phase = 'WORK'
                lp_mismatches += 1

        # 4. Compute dV: contributions[i] * apparatus.sensitivity[sv]
        #    NO routing dV scaling (permissivity handles routing effects)
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

        # 8. Zone classification per SV
        zones = diagnostics['zones']
        for sv in STATE_VARS:
            zone_counts[sv][zones[sv]] += 1

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
                # Excursion ended
                duration = tok_idx - excursion_start
                if duration <= MAX_CYCLE_DURATION:
                    bounded_excursion_count += 1
                in_excursion = False
                excursion_start = None

    # Compute summary statistics
    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]
    std_state = []
    for i in range(N_VARS):
        variance = (state_sq_sum[i] / n_tokens) - (mean_state[i] ** 2)
        std_state.append(math.sqrt(max(0.0, variance)))

    # Build zone occupancy fractions
    zone_occupancy = {}
    for sv in STATE_VARS:
        total = sum(zone_counts[sv].values())
        if total > 0:
            zone_occupancy[sv] = {
                'basin': round(zone_counts[sv]['BASIN'] / total, 5),
                'corridor': round(zone_counts[sv]['CORRIDOR'] / total, 5),
                'edge': round(zone_counts[sv]['EDGE'] / total, 5),
            }
        else:
            zone_occupancy[sv] = {'basin': 0.0, 'corridor': 0.0, 'edge': 0.0}

    # Build state trajectory summary
    state_trajectory_summary = {}
    for i, sv in enumerate(STATE_VARS):
        state_trajectory_summary[sv] = {
            'min': round(state_min[i], 5),
            'max': round(state_max[i], 5),
            'mean': round(mean_state[i], 5),
            'std': round(std_state[i], 5),
        }

    result = {
        'n_tokens': n_tokens,
        'viability': round(viable_count / n_tokens, 5),
        'n_hazard_events': hazard_count,
        'Y_final': round(state[SV_INDEX['Y']], 5),
        'mean_state': [round(v, 5) for v in mean_state],
        'excursion_count': excursion_count,
        'bounded_excursion_count': bounded_excursion_count,
        'zone_occupancy': zone_occupancy,
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

    output_path = phase_dir / 'results' / 't2_selective_restoration_runs.json'

    # --- Data source paths ---
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    t1_path = phase_dir / 'results' / 't1_selective_restoration_apparatus.json'
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')

    print("=" * 70)
    print("T2: Selective Restoration Executor")
    print("Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION")
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
    # Use assign_folio_profiles from the coupling phase
    print("\n--- Assigning folio profiles ---")
    regime_path = project_root / 'data' / 'regime_folio_mapping.json'
    budget_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                   / 'results' / 't2_folio_budgets.json')

    sys.path.insert(0, str(project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
    from t1_apparatus_family_builder import assign_folio_profiles

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

            run_entry = {
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
                'discharge_events': result['discharge_events'],
                'state_trajectory_summary': result['state_trajectory_summary'],
            }
            if result.get('lp_mismatches'):
                run_entry['lp_mismatches'] = result['lp_mismatches']

            primary_runs.append(run_entry)
            run_count += 1

            is_pref = (profile_name == preferred_profile)
            pref_tag = " *PREFERRED*" if is_pref else ""
            via = result['viability']
            haz = result['n_hazard_events']
            yf = result['Y_final']
            exc = result['excursion_count']
            bnd = result['bounded_excursion_count']
            print(f"  [{run_count:2d}/60] {folio} + {profile_name} [{config_mode}]: "
                  f"viab={via:.4f}, hazards={haz}, Y_final={yf:.4f}, "
                  f"cycles={exc}, bounded={bnd}{pref_tag}")

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

            abl_entry = {
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
                'discharge_events': result['discharge_events'],
                'state_trajectory_summary': result['state_trajectory_summary'],
            }
            if result.get('lp_mismatches'):
                abl_entry['lp_mismatches'] = result['lp_mismatches']

            config_ablation_runs.append(abl_entry)
            ablation_count += 1

            via = result['viability']
            haz = result['n_hazard_events']
            print(f"  [{ablation_count:2d}/30] {folio} + {preferred_profile} + {cm}: "
                  f"viab={via:.4f}, hazards={haz}")

    # --- Build output ---
    print("\n--- Building output ---")

    output = {
        'metadata': {
            'phase': '564b',
            'task': 'T2',
            'timestamp': datetime.now().isoformat(),
            'n_primary': len(primary_runs),
            'n_config_ablation': len(config_ablation_runs),
            'n_total': len(primary_runs) + len(config_ablation_runs),
        },
        'primary_runs': primary_runs,
        'config_ablation_runs': config_ablation_runs,
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
    pref_viabilities = []
    pref_hazards = []
    pref_excursions = []
    pref_bounded = []

    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            pref_viabilities.append(run['viability'])
            pref_hazards.append(run['n_hazard_events'])
            pref_excursions.append(run['excursion_count'])
            pref_bounded.append(run['bounded_excursion_count'])

    if pref_viabilities:
        mean_via = sum(pref_viabilities) / len(pref_viabilities)
        min_via = min(pref_viabilities)
        max_via = max(pref_viabilities)
        total_haz = sum(pref_hazards)
        mean_exc = sum(pref_excursions) / len(pref_excursions)
        mean_bnd = sum(pref_bounded) / len(pref_bounded)
        print(f"  Preferred-profile viability: "
              f"mean={mean_via:.4f}, min={min_via:.4f}, max={max_via:.4f}")
        print(f"  Total hazard events (preferred): {total_haz}")
        print(f"  Mean excursion cycles (preferred): {mean_exc:.1f}")
        print(f"  Mean bounded excursions (preferred): {mean_bnd:.1f}")

    # Zone occupancy summary (preferred runs only)
    print("\n  Zone occupancy (preferred runs, averaged):")
    zone_sums = {sv: {'basin': 0.0, 'corridor': 0.0, 'edge': 0.0} for sv in STATE_VARS}
    zone_n = 0
    for run in primary_runs:
        if run['profile'] == preferred_profile_map.get(run['folio']):
            zone_n += 1
            for sv in STATE_VARS:
                for z in ['basin', 'corridor', 'edge']:
                    zone_sums[sv][z] += run['zone_occupancy'][sv][z]

    if zone_n > 0:
        for sv in STATE_VARS:
            b = zone_sums[sv]['basin'] / zone_n
            c = zone_sums[sv]['corridor'] / zone_n
            e = zone_sums[sv]['edge'] / zone_n
            print(f"    {sv}: basin={b:.3f}, corridor={c:.3f}, edge={e:.3f}")

    print(f"\n  Total runs: {len(primary_runs) + len(config_ablation_runs)}")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
