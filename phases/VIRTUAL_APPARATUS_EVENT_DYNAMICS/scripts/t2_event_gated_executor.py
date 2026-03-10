"""
T2: Event-Gated Executor
Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS

Runs 20 pilot folios through the event-gated apparatus with dual-channel
routing buffer. 90 total runs:
  - 60 primary: 20 folios x 3 profiles x 1 inferred config mode
  - 30 config ablation: 10 folios x preferred profile x 3 config modes

Dual-channel routing buffer:
  Channel A: Contribution modulation (scales dV per SV via routing terminal)
  Channel B: Threshold modulation (shifts apparatus threshold levels)
  Both channels decay per-token and reset at line boundaries.
"""

import json
import math
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Import T1 apparatus
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t1_event_gated_apparatus import (
    EventGatedApparatus, STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM,
    SV_INDEX, PROFILES, CONFIG_MODES, PILOT_FOLIOS, assign_config_mode,
    build_configured_apparatus
)

# ---------------------------------------------------------------------------
# Routing Buffer Constants
# ---------------------------------------------------------------------------

# Channel A: Per-routing-terminal contribution modulation effects
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

# Channel A gain: scales how much routing effects feed into contribution buffer
ROUTING_CONTRIB_GAIN = 0.3

# Channel B: Per-routing-terminal threshold shift effects
ROUTING_THRESH_EFFECTS = {
    'r': {'X_collapse_level': +0.04},
    'y': {'T_reversal_level': +0.04},
    'h': {'C_relief_level': -0.04},
    'm': {'C_relief_level': +0.04, 'CTS_discharge_strength': +0.3},
    'n': {'S_erosion_strength': -0.3},
    'l': {'C_relief_level': -0.02},
}

# Decay rate for both routing buffers (per token)
ROUTING_DECAY = 0.7

# Excursion tracking thresholds (process SVs only, Y excluded)
QUIET_LO, QUIET_HI = 0.4, 0.6
EXCURSION_LO, EXCURSION_HI = 0.35, 0.65
MAX_CYCLE_DURATION = 50

# Process SVs: those with at least one hazard boundary (excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# Config ablation folios: 2B, 3H, 3S, 1T, 1C
CONFIG_ABLATION_FOLIOS = [
    'f78r', 'f79r',           # B
    'f55r', 'f40v', 'f43v',   # H
    'f104r', 'f111r', 'f116r', # S
    'f66r',                    # T
    'f86v5',                   # C
]

# All 3 profile names
PROFILE_NAMES = ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']


# ---------------------------------------------------------------------------
# Excursion detection helpers
# ---------------------------------------------------------------------------

def _is_quiet(state):
    """All process SVs in [QUIET_LO, QUIET_HI]."""
    return all(QUIET_LO <= state[i] <= QUIET_HI for i in PROCESS_IDX)


def _is_excursion(state):
    """Any process SV outside [EXCURSION_LO, EXCURSION_HI]."""
    return any(state[i] < EXCURSION_LO or state[i] > EXCURSION_HI
               for i in PROCESS_IDX)


def _excursion_peak(state):
    """Maximum deviation from equilibrium among process SVs."""
    return max(abs(state[i] - EQUILIBRIUM) for i in PROCESS_IDX)


# ---------------------------------------------------------------------------
# Core execution function
# ---------------------------------------------------------------------------

def run_coupled_trace(apparatus, tokens, line_packets, store_trajectory=False):
    """
    Run one folio through the event-gated apparatus.

    apparatus:        EventGatedApparatus instance
    tokens:           list of token dicts, pre-sorted by (line, line_pos)
    line_packets:     dict mapping "folio|line" -> packet info
    store_trajectory: if True, record per-token state

    Returns dict with 'summary', and optionally 'trajectory', 'hazard_log',
    'excursion_events'.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'summary': {
                'n_tokens': 0,
                'viability_fraction': 0.0,
                'hazard_count': 0,
                'hazard_rate': 0.0,
            }
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    routing_thresh_buffer = {}
    prev_line = None

    # Accumulators
    viable_count = 0
    hazard_count = 0
    state_sum = [0.0] * N_VARS
    state_sq_sum = [0.0] * N_VARS
    state_min = [1.0] * N_VARS
    state_max = [0.0] * N_VARS
    max_T = 0.0
    min_S = 1.0
    max_C = 0.0
    max_X = 0.0

    trajectory = [] if store_trajectory else None
    hazard_log = [] if store_trajectory else None
    all_states_for_excursion = [] if store_trajectory else None

    # Excursion cycle tracking (always computed for summary)
    excursion_events = []
    in_excursion = False
    excursion_start = None
    excursion_peak_dev = 0.0
    excursion_packet_phase_start = None

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok['folio']

        # 1. Reset routing buffers at line boundary
        if current_line != prev_line:
            routing_contrib_buffer = [0.0] * N_VARS
            routing_thresh_buffer = {}
            prev_line = current_line

        # 2. Routing event -> update BOTH buffers
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_EFFECTS:
                # Channel A: contribution modulation
                for sv, mult in ROUTING_EFFECTS[rt].get('boost', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                for sv, mult in ROUTING_EFFECTS[rt].get('suppress', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
            if rt in ROUTING_THRESH_EFFECTS:
                # Channel B: threshold modulation
                for key, shift in ROUTING_THRESH_EFFECTS[rt].items():
                    routing_thresh_buffer[key] = routing_thresh_buffer.get(key, 0.0) + shift

        # 3. Look up packet_phase from line_packets
        lp_key = f"{folio}|{current_line}"
        if lp_key in line_packets:
            packet_phase = line_packets[lp_key].get('packet_state', {}).get('packet_phase', 'WORK')
        else:
            packet_phase = 'WORK'  # fallback

        # 4. Get CTS from token
        cts = tok.get('cts', 0.0)

        # 5. Compute buffered dV: contributions * sensitivity * (1 + contrib_buffer)
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            effective_sens = apparatus.sensitivity(sv) * (1.0 + routing_contrib_buffer[i])
            dV[i] = tok['contributions'][i] * effective_sens

        # 6. Update state
        state = apparatus.update(
            state, dV, packet_phase, cts,
            routing_thresh_buffer if routing_thresh_buffer else None
        )

        # 7. Decay both buffers
        routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]
        new_thresh = {}
        for k, v in routing_thresh_buffer.items():
            nv = v * ROUTING_DECAY
            if abs(nv) > 0.001:  # prune negligible
                new_thresh[k] = nv
        routing_thresh_buffer = new_thresh

        # 8. Record state, check hazard, track excursions
        # Update running statistics
        for i in range(N_VARS):
            state_sum[i] += state[i]
            state_sq_sum[i] += state[i] ** 2
            if state[i] < state_min[i]:
                state_min[i] = state[i]
            if state[i] > state_max[i]:
                state_max[i] = state[i]

        # Track specific extremes
        t_val = state[SV_INDEX['T']]
        s_val = state[SV_INDEX['S']]
        c_val = state[SV_INDEX['C']]
        x_val = state[SV_INDEX['X']]
        if t_val > max_T:
            max_T = t_val
        if s_val < min_S:
            min_S = s_val
        if c_val > max_C:
            max_C = c_val
        if x_val > max_X:
            max_X = x_val

        # Hazard check
        is_hazardous = False
        for i, sv in enumerate(STATE_VARS):
            lo, hi = HAZARD_BOUNDARIES[sv]
            if lo is not None and state[i] < lo:
                is_hazardous = True
            if hi is not None and state[i] > hi:
                is_hazardous = True

        if is_hazardous:
            hazard_count += 1
            if hazard_log is not None:
                hazard_log.append({
                    'tok_idx': tok_idx,
                    'word': tok.get('word', ''),
                    'state': [round(v, 5) for v in state],
                })
        else:
            viable_count += 1

        # Store trajectory if requested
        if trajectory is not None:
            trajectory.append([round(v, 5) for v in state])

        # Excursion cycle tracking
        quiet_now = _is_quiet(state)
        excursion_now = _is_excursion(state)
        peak_dev = _excursion_peak(state)

        if not in_excursion:
            if not quiet_now:
                # Entering excursion
                in_excursion = True
                excursion_start = tok_idx
                excursion_peak_dev = peak_dev
                excursion_packet_phase_start = packet_phase
        else:
            # Already in excursion
            if peak_dev > excursion_peak_dev:
                excursion_peak_dev = peak_dev
            if quiet_now:
                # Returned to quiet: cycle complete
                duration = tok_idx - excursion_start
                bounded = (excursion_peak_dev > (EQUILIBRIUM - EXCURSION_LO)
                           and duration <= MAX_CYCLE_DURATION)
                excursion_events.append({
                    'start_idx': excursion_start,
                    'end_idx': tok_idx,
                    'duration': duration,
                    'peak_deviation': round(excursion_peak_dev, 5),
                    'packet_phase_at_start': excursion_packet_phase_start,
                    'bounded': bounded,
                })
                in_excursion = False
                excursion_start = None
                excursion_peak_dev = 0.0

    # Compute summary statistics
    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]
    std_state = []
    for i in range(N_VARS):
        variance = (state_sq_sum[i] / n_tokens) - (mean_state[i] ** 2)
        std_state.append(math.sqrt(max(0.0, variance)))

    n_excursion_cycles = len(excursion_events)
    n_bounded_cycles = sum(1 for e in excursion_events if e['bounded'])

    summary = {
        'n_tokens': n_tokens,
        'viability_fraction': round(viable_count / n_tokens, 5),
        'hazard_count': hazard_count,
        'hazard_rate': round(hazard_count / n_tokens, 5),
        'mean_state': [round(v, 5) for v in mean_state],
        'std_state': [round(v, 5) for v in std_state],
        'min_state': [round(v, 5) for v in state_min],
        'max_state': [round(v, 5) for v in state_max],
        'final_state': [round(v, 5) for v in state],
        'Y_final': round(state[SV_INDEX['Y']], 5),
        'max_T': round(max_T, 5),
        'min_S': round(min_S, 5),
        'max_C': round(max_C, 5),
        'max_X': round(max_X, 5),
        'n_excursion_cycles': n_excursion_cycles,
        'n_bounded_cycles': n_bounded_cycles,
        'bounded_fraction': round(
            n_bounded_cycles / max(n_excursion_cycles, 1), 4),
        'mean_return_time': round(
            (sum(e['duration'] for e in excursion_events if e['bounded'])
             / max(n_bounded_cycles, 1)),
            2),
    }

    result = {'summary': summary}
    if store_trajectory:
        result['trajectory'] = trajectory
        result['hazard_log'] = hazard_log
        result['excursion_events'] = excursion_events
    else:
        result['trajectory'] = None
        result['hazard_log'] = None
        result['excursion_events'] = None

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent
    project_root = phase_dir.parent.parent

    output_path = phase_dir / 'results' / 't2_event_gated_runs.json'

    # --- Data source paths ---
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    t1_path = phase_dir / 'results' / 't1_event_gated_apparatus.json'
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')

    print("=" * 70)
    print("T2: Event-Gated Executor")
    print("Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS")
    print("=" * 70)

    # --- Load data sources ---
    print("\n--- Loading data sources ---")

    print(f"  Loading T2b supervisory tokens: {t2b_path}")
    with open(t2b_path, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"    Total tokens: {len(all_tokens)}")

    print(f"  Loading T1 apparatus: {t1_path}")
    with open(t1_path, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    folio_assignments = t1_data['folio_assignments']
    config_assignments = t1_data['config_assignments']
    print(f"    Folio assignments: {len(folio_assignments)}")
    print(f"    Config assignments: {len(config_assignments)}")

    print(f"  Loading line packets: {lp_path}")
    with open(lp_path, 'r', encoding='utf-8') as f:
        lp_data = json.load(f)
    line_packets = lp_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    # --- Extract tokens per pilot folio ---
    print("\n--- Extracting pilot folio tokens ---")
    pilot_folio_set = set(PILOT_FOLIOS.keys())
    tokens_by_folio = {f: [] for f in pilot_folio_set}
    for tok in all_tokens:
        if tok['folio'] in pilot_folio_set:
            tokens_by_folio[tok['folio']].append(tok)

    # Sort each folio's tokens by (line, line_pos)
    def sort_key(tok):
        # Line may be numeric string or contain letters; sort as string
        # but try numeric first for natural ordering
        line = tok.get('line', '0')
        try:
            line_num = int(line)
        except (ValueError, TypeError):
            line_num = 99999
        return (line_num, tok.get('line_pos', 0.0))

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # Compute hl_rate from actual tokens
    hl_rates = {}
    for folio, toks in tokens_by_folio.items():
        n_total = len(toks)
        if n_total == 0:
            hl_rates[folio] = 0.0
            continue
        n_headless = sum(1 for t in toks if t.get('headless_subtype', 'HEADED') != 'HEADED')
        hl_rates[folio] = n_headless / n_total

    # Print summary
    for folio in sorted(pilot_folio_set):
        n = len(tokens_by_folio[folio])
        section = PILOT_FOLIOS[folio]['section']
        pref = folio_assignments.get(folio, {}).get('preferred_profile', '?')
        cfg = config_assignments.get(folio, {}).get('config_mode', '?')
        print(f"  {folio}: {n} tokens, section={section}, "
              f"preferred={pref}, config={cfg}, hl_rate={hl_rates[folio]:.3f}")

    # --- Primary runs (60): 20 folios x 3 profiles ---
    print("\n--- Primary Runs (60) ---")
    runs = {}
    run_count = 0

    for folio in sorted(pilot_folio_set):
        toks = tokens_by_folio[folio]
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        fa = folio_assignments.get(folio, {})
        ca = config_assignments.get(folio, {})
        preferred_profile = fa.get('preferred_profile', 'A1_BATH_REFLUX')
        config_mode = ca.get('config_mode', 'H1_MEDIUM_INFRA')
        section = PILOT_FOLIOS[folio]['section']
        hl_rate = ca.get('hl_rate', hl_rates[folio])

        for profile_name in PROFILE_NAMES:
            is_preferred = (profile_name == preferred_profile)
            store_traj = is_preferred

            # Build apparatus with this profile and the folio's config mode
            apparatus = build_configured_apparatus(profile_name, config_mode)

            result = run_coupled_trace(apparatus, toks, line_packets,
                                       store_trajectory=store_traj)

            run_key = f"{folio}__{profile_name}"
            runs[run_key] = {
                'summary': result['summary'],
                'trajectory': result.get('trajectory'),
                'hazard_log': result.get('hazard_log'),
                'excursion_events': result.get('excursion_events'),
                'folio': folio,
                'profile': profile_name,
                'is_preferred': is_preferred,
                'config_mode': config_mode,
                'headless_rate': round(hl_rate, 4),
                'section': section,
            }

            run_count += 1
            pref_tag = " *PREFERRED*" if is_preferred else ""
            via = result['summary']['viability_fraction']
            haz = result['summary']['hazard_count']
            yf = result['summary']['Y_final']
            nc = result['summary']['n_excursion_cycles']
            nb = result['summary']['n_bounded_cycles']
            print(f"  [{run_count:2d}/60] {folio} + {profile_name}: "
                  f"viability={via:.4f}, hazards={haz}, Y_final={yf:.4f}, "
                  f"cycles={nc}, bounded={nb}{pref_tag}")

    # --- Config ablation runs (30): 10 folios x preferred profile x 3 config modes ---
    print("\n--- Config Ablation Runs (30) ---")
    config_ablation_runs = {}
    ablation_count = 0

    config_mode_names = list(CONFIG_MODES.keys())

    for folio in CONFIG_ABLATION_FOLIOS:
        toks = tokens_by_folio.get(folio, [])
        if len(toks) == 0:
            print(f"  SKIP {folio}: no tokens")
            continue

        fa = folio_assignments.get(folio, {})
        preferred_profile = fa.get('preferred_profile', 'A1_BATH_REFLUX')

        for cm in config_mode_names:
            apparatus = build_configured_apparatus(preferred_profile, cm)
            result = run_coupled_trace(apparatus, toks, line_packets,
                                       store_trajectory=False)

            abl_key = f"{folio}__{cm}"
            config_ablation_runs[abl_key] = {
                'summary': result['summary'],
                'folio': folio,
                'profile': preferred_profile,
                'config_mode': cm,
            }

            ablation_count += 1
            via = result['summary']['viability_fraction']
            haz = result['summary']['hazard_count']
            print(f"  [{ablation_count:2d}/30] {folio} + {preferred_profile} + {cm}: "
                  f"viability={via:.4f}, hazards={haz}")

    # --- Cross-profile summary ---
    print("\n--- Cross-Profile Summary ---")
    cross_profile_summary = {}

    for folio in sorted(pilot_folio_set):
        fa = folio_assignments.get(folio, {})
        ca = config_assignments.get(folio, {})
        preferred_profile = fa.get('preferred_profile', 'A1_BATH_REFLUX')
        config_mode = ca.get('config_mode', 'H1_MEDIUM_INFRA')
        section = PILOT_FOLIOS[folio]['section']
        n_toks = len(tokens_by_folio[folio])

        viability = {}
        hazard_counts = {}
        y_finals = {}

        for profile_name in PROFILE_NAMES:
            run_key = f"{folio}__{profile_name}"
            if run_key in runs:
                s = runs[run_key]['summary']
                viability[profile_name] = s['viability_fraction']
                hazard_counts[profile_name] = s['hazard_count']
                y_finals[profile_name] = s['Y_final']

        # Get excursion info from preferred run
        pref_key = f"{folio}__{preferred_profile}"
        pref_summary = runs.get(pref_key, {}).get('summary', {})

        preferred_viability = viability.get(preferred_profile, 0.0)
        best_profile = max(viability, key=viability.get) if viability else None
        preferred_is_best = (best_profile == preferred_profile)

        cps = {
            'section': section,
            'preferred_profile': preferred_profile,
            'config_mode': config_mode,
            'n_tokens': n_toks,
            'preferred_viability': preferred_viability,
            'preferred_is_best': preferred_is_best,
            'viability': viability,
            'hazard_counts': hazard_counts,
            'Y_final': y_finals,
            'n_excursion_cycles': pref_summary.get('n_excursion_cycles', 0),
            'n_bounded_cycles': pref_summary.get('n_bounded_cycles', 0),
            'bounded_fraction': pref_summary.get('bounded_fraction', 0.0),
        }
        cross_profile_summary[folio] = cps

        best_tag = "BEST" if preferred_is_best else f"BEST={best_profile}"
        print(f"  {folio}: preferred={preferred_profile} "
              f"via={preferred_viability:.4f} [{best_tag}] "
              f"cycles={cps['n_excursion_cycles']}/{cps['n_bounded_cycles']} bounded")

    # --- Build output ---
    output = {
        'metadata': {
            'phase': '564',
            'task': 'T2_event_gated_executor',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_pilot_folios': len(pilot_folio_set),
            'n_primary_runs': run_count,
            'n_config_ablation_runs': ablation_count,
            'n_total_runs': run_count + ablation_count,
            'routing_contrib_gain': ROUTING_CONTRIB_GAIN,
            'routing_decay': ROUTING_DECAY,
            'quiet_band': [QUIET_LO, QUIET_HI],
            'excursion_band': [EXCURSION_LO, EXCURSION_HI],
            'max_cycle_duration': MAX_CYCLE_DURATION,
            'process_svs': PROCESS_SVS,
        },
        'runs': runs,
        'config_ablation_runs': config_ablation_runs,
        'cross_profile_summary': cross_profile_summary,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = output_path.stat().st_size
    print(f"\n  Output: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # --- Final stats ---
    print("\n--- Final Statistics ---")
    all_viabilities = []
    all_hazards = []
    pref_best_count = 0
    for folio, cps in cross_profile_summary.items():
        all_viabilities.append(cps['preferred_viability'])
        all_hazards.append(cps['hazard_counts'].get(cps['preferred_profile'], 0))
        if cps['preferred_is_best']:
            pref_best_count += 1

    if all_viabilities:
        mean_via = sum(all_viabilities) / len(all_viabilities)
        min_via = min(all_viabilities)
        max_via = max(all_viabilities)
        total_hazards = sum(all_hazards)
        print(f"  Preferred-profile viability: "
              f"mean={mean_via:.4f}, min={min_via:.4f}, max={max_via:.4f}")
        print(f"  Total hazard tokens (preferred): {total_hazards}")
        print(f"  Preferred is best: {pref_best_count}/{len(cross_profile_summary)}")

    # Bounded cycle stats
    all_bounded_frac = [cps['bounded_fraction']
                        for cps in cross_profile_summary.values()
                        if cps['n_excursion_cycles'] > 0]
    if all_bounded_frac:
        mean_bf = sum(all_bounded_frac) / len(all_bounded_frac)
        print(f"  Mean bounded fraction (folios with cycles): {mean_bf:.4f}")

    print(f"\n  Total runs: {run_count + ablation_count}")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
