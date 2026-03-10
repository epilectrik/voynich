"""
T3b: Accumulated Trace Executor with Routing and Headless Modulation
====================================================================
Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION

Runs 20 pilot folios x 3 apparatus profiles = 60 coupled simulations.
Key additions over T3:
  - Routing accumulator: per-state-variable decaying multiplicative bias,
    reset at line boundaries (C1470 compliance)
  - Headless profile modulation per folio (C1574 compliance)
  - Recalibrated apparatus profiles from T1b
  - Expanded pilot folio set (20 folios)

Execution engine matches T4b exactly (same routing logic, same update order).

Input:  t1b_apparatus_recalibrated.json, t2b_supervisory_interface_unrouted.json
Output: t3b_coupled_traces.json
"""

import json
import sys
import time
import math
from pathlib import Path
from collections import defaultdict

# Sibling imports
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from t1_apparatus_family_builder import (
    VirtualApparatus, STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM
)
from t1b_apparatus_recalibration import apply_headless_modulation

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
phase_dir = script_dir.parent
results_dir = phase_dir / "results"
T1B_PATH = results_dir / "t1b_apparatus_recalibrated.json"
T2B_PATH = results_dir / "t2b_supervisory_interface_unrouted.json"
OUTPUT_PATH = results_dir / "t3b_coupled_traces.json"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ROUTING_DECAY = 0.7   # per-token decay factor for routing accumulator
ROUTING_GAIN  = 0.5   # gain applied to routing terminal effects

# Routing effects (C1563) — multiplier dicts, matching T4b exactly
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

# State variable name -> index mapping
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

# 20 Pilot Folios (matching T4b)
PILOT_FOLIOS = [
    "f78r", "f84r", "f79r", "f81v",                    # B
    "f55r", "f40v", "f43v", "f34r",                     # H
    "f31r", "f39v", "f95r1",                            # H
    "f104r", "f111r", "f116r", "f105r", "f108v",        # S
    "f66r", "f85r1",                                    # T
    "f86v5", "f86v6",                                   # C
]

PROFILE_NAMES = ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']


# ---------------------------------------------------------------------------
# Sort key (matching T4b)
# ---------------------------------------------------------------------------
def sort_key(tok):
    try:
        ln = int(tok["line"])
    except (ValueError, TypeError):
        ln = 0
    lp = tok.get("line_pos", 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


# ---------------------------------------------------------------------------
# Hazard check
# ---------------------------------------------------------------------------
def check_hazards_detailed(state, tok, tok_idx):
    """Check state against hazard boundaries, return list of violations with details."""
    violations = []
    for i, sv in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[sv]
        val = state[i]
        if lo is not None and val < lo:
            violations.append({
                'token_idx': tok_idx,
                'word': tok.get('word', ''),
                'line': tok.get('line', '?'),
                'variable': sv,
                'value': round(val, 6),
                'boundary': 'low',
                'threshold': lo,
                'severity': round(lo - val, 6),
            })
        if hi is not None and val > hi:
            violations.append({
                'token_idx': tok_idx,
                'word': tok.get('word', ''),
                'line': tok.get('line', '?'),
                'variable': sv,
                'value': round(val, 6),
                'boundary': 'high',
                'threshold': hi,
                'severity': round(val - hi, 6),
            })
    return violations


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
# Coupled trace execution
# ---------------------------------------------------------------------------
def run_coupled_trace(apparatus, tokens, store_trajectory):
    """
    Run a single folio through the coupled apparatus simulation.

    Routing accumulator logic (identical to T4b):
      1. Line boundary -> reset routing_accum to [0.0]*7
      2. Routing event -> accum[i] += (mult - 1.0) * ROUTING_GAIN
      3. Compute dV: effective_sensitivity = base * (1 + accum[i])
      4. Update state via apparatus.update()
      5. Decay accumulator: accum[i] *= ROUTING_DECAY

    Parameters
    ----------
    apparatus : VirtualApparatus
        The (possibly headless-modulated) apparatus instance.
    tokens : list[dict]
        Token records sorted by (line, line_pos).
    store_trajectory : bool
        If True, store full trajectory; otherwise summary only.

    Returns
    -------
    dict with 'summary' and optionally 'trajectory' and 'hazard_log'.
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'summary': {
                'n_tokens': 0,
                'viability_fraction': 1.0,
                'hazard_count': 0,
                'hazard_rate': 0.0,
                'mean_state': [0.5] * N_VARS,
                'std_state': [0.0] * N_VARS,
                'min_state': [0.5] * N_VARS,
                'max_state': [0.5] * N_VARS,
                'final_state': [0.5] * N_VARS,
                'Y_final': 0.5,
                'max_T': 0.5, 'min_S': 0.5, 'max_C': 0.5, 'max_X': 0.5,
            },
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_accum = [0.0] * N_VARS
    prev_line = None

    trajectory = [] if store_trajectory else None
    hazard_log = [] if store_trajectory else None

    # Accumulators for summary stats
    n_viable = 0
    hazard_count = 0
    state_sum = [0.0] * N_VARS
    state_sq_sum = [0.0] * N_VARS
    min_state = [1.0] * N_VARS
    max_state = [0.0] * N_VARS
    max_T = 0.0
    min_S = 1.0
    max_C = 0.0
    max_X = 0.0

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')

        # 1. Reset routing accumulator at line boundaries (C1470)
        if current_line != prev_line:
            routing_accum = [0.0] * N_VARS
            prev_line = current_line

        # 2. Apply routing terminal effects
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_EFFECTS:
                effects = ROUTING_EFFECTS[rt]
                for sv, mult in effects.get('boost', {}).items():
                    routing_accum[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_GAIN
                for sv, mult in effects.get('suppress', {}).items():
                    routing_accum[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_GAIN

        # 3. Build dV from contributions with routing-modulated sensitivity
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            base_sens = apparatus.sensitivity(sv)
            effective_sens = base_sens * (1.0 + routing_accum[i])
            dV[i] = contributions[i] * effective_sens

        # 4. Update state
        state = apparatus.update(state, dV)

        # 5. Decay routing accumulator
        routing_accum = [a * ROUTING_DECAY for a in routing_accum]

        # --- Check hazards ---
        in_bounds = is_in_bounds(state)
        if in_bounds:
            n_viable += 1
        else:
            hazard_count += 1
            if store_trajectory:
                violations = check_hazards_detailed(state, tok, tok_idx)
                hazard_log.extend(violations)

        # --- Accumulate stats ---
        for i in range(N_VARS):
            v = state[i]
            state_sum[i] += v
            state_sq_sum[i] += v * v
            if v < min_state[i]:
                min_state[i] = v
            if v > max_state[i]:
                max_state[i] = v
        if state[0] > max_T:
            max_T = state[0]
        if state[2] < min_S:
            min_S = state[2]
        if state[3] > max_C:
            max_C = state[3]
        if state[5] > max_X:
            max_X = state[5]

        # --- Record trajectory point (preferred runs only) ---
        if store_trajectory:
            trajectory.append({
                'state': [round(v, 6) for v in state],
                'word': tok.get('word', ''),
                'line': current_line,
                'routing_accum': [round(a, 6) for a in routing_accum],
            })

    # --- Compute summary ---
    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]
    std_state = [
        math.sqrt(max(0.0, state_sq_sum[i] / n_tokens - mean_state[i] ** 2))
        for i in range(N_VARS)
    ]

    summary = {
        'n_tokens': n_tokens,
        'viability_fraction': round(n_viable / n_tokens, 6),
        'hazard_count': hazard_count,
        'hazard_rate': round(hazard_count / n_tokens, 6),
        'mean_state': [round(v, 6) for v in mean_state],
        'std_state': [round(v, 6) for v in std_state],
        'min_state': [round(v, 6) for v in min_state],
        'max_state': [round(v, 6) for v in max_state],
        'final_state': [round(v, 6) for v in state],
        'Y_final': round(state[SV_INDEX['Y']], 6),
        'max_T': round(max_T, 6),
        'min_S': round(min_S, 6),
        'max_C': round(max_C, 6),
        'max_X': round(max_X, 6),
    }

    result = {'summary': summary}
    if store_trajectory:
        result['trajectory'] = trajectory
        result['hazard_log'] = hazard_log
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3b: Accumulated Trace Executor")
    print("Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION")
    print("=" * 70)

    # --- Load inputs ---
    print("\nLoading T1b recalibrated profiles...")
    with open(T1B_PATH) as f:
        t1b_data = json.load(f)

    recalibrated_profiles = t1b_data['profiles']
    folio_assignments = t1b_data['folio_assignments']
    print(f"  Folio assignments: {len(folio_assignments)}")

    print("Loading T2b unrouted token signals...")
    with open(T2B_PATH) as f:
        t2b_data = json.load(f)

    all_tokens = t2b_data['token_signals']
    print(f"  Loaded {len(all_tokens)} tokens")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    # Sort tokens within each folio
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # --- Compute per-folio headless rates ---
    folio_hl_rates = {}
    for folio, toks in tokens_by_folio.items():
        n_total = len(toks)
        n_headless = sum(1 for t in toks if t.get('headless_subtype', 'HEADED') != 'HEADED')
        folio_hl_rates[folio] = n_headless / n_total if n_total > 0 else 0.0

    # --- Run 60 simulations ---
    runs = {}
    cross_profile = defaultdict(dict)  # folio -> {profile: summary}
    n_total_runs = 0
    n_preferred = 0
    n_nonpreferred = 0
    n_skipped = 0

    for folio in PILOT_FOLIOS:
        if folio not in tokens_by_folio:
            print(f"  WARNING: {folio} not found in T2b tokens, skipping")
            n_skipped += 1
            continue

        toks = tokens_by_folio[folio]
        assignment = folio_assignments.get(folio, {})
        preferred = assignment.get('preferred_profile', 'A1_BATH_REFLUX')
        hl_rate = folio_hl_rates.get(folio, 0.25)

        print(f"  {folio}: {len(toks)} tokens, preferred={preferred}, hl_rate={hl_rate:.3f}")

        for profile_name in PROFILE_NAMES:
            is_preferred = (profile_name == preferred)
            run_key = f"{folio}__{profile_name}"

            # Get recalibrated profile params
            profile_params = dict(recalibrated_profiles[profile_name])

            # Apply headless modulation (C1574)
            modulated_params = apply_headless_modulation(profile_params, hl_rate)

            # Build apparatus
            apparatus = VirtualApparatus(modulated_params)

            # Run coupled trace (full trajectory for preferred only)
            result = run_coupled_trace(apparatus, toks, store_trajectory=is_preferred)
            result['folio'] = folio
            result['profile'] = profile_name
            result['is_preferred'] = is_preferred
            result['headless_rate'] = round(hl_rate, 4)
            result['section'] = assignment.get('section', 'unknown')
            result['regime'] = assignment.get('regime', 'unknown')

            runs[run_key] = result
            cross_profile[folio][profile_name] = result['summary']

            n_total_runs += 1
            if is_preferred:
                n_preferred += 1
            else:
                n_nonpreferred += 1

    # --- Build cross-profile summary ---
    cross_profile_summary = {}
    for folio, profiles in cross_profile.items():
        assignment = folio_assignments.get(folio, {})
        preferred = assignment.get('preferred_profile', 'A1_BATH_REFLUX')

        # Viability-based ranking (higher is better)
        best_profile = max(profiles.keys(),
                          key=lambda p: profiles[p]['viability_fraction'])
        worst_profile = min(profiles.keys(),
                           key=lambda p: profiles[p]['viability_fraction'])

        cross_profile_summary[folio] = {
            'section': assignment.get('section', 'unknown'),
            'preferred_profile': preferred,
            'n_tokens': profiles[preferred]['n_tokens'],
            'preferred_viability': profiles[preferred]['viability_fraction'],
            'preferred_hazard_count': profiles[preferred]['hazard_count'],
            'best_profile': best_profile,
            'best_viability': profiles[best_profile]['viability_fraction'],
            'worst_profile': worst_profile,
            'worst_viability': profiles[worst_profile]['viability_fraction'],
            'preferred_is_best': preferred == best_profile,
            'viability': {p: profiles[p]['viability_fraction'] for p in profiles},
            'hazard_counts': {p: profiles[p]['hazard_count'] for p in profiles},
            'Y_final': {p: profiles[p]['Y_final'] for p in profiles},
        }

    elapsed = time.time() - t0

    # --- Assemble output ---
    output = {
        'metadata': {
            'phase': '563b',
            'test': 'T3b',
            'description': 'Accumulated trace executor with routing and headless modulation',
            'n_pilot_folios': len(PILOT_FOLIOS),
            'n_folios_run': len(cross_profile_summary),
            'n_folios_skipped': n_skipped,
            'n_profiles': len(PROFILE_NAMES),
            'n_total_runs': n_total_runs,
            'n_preferred_runs': n_preferred,
            'n_nonpreferred_runs': n_nonpreferred,
            'routing_decay': ROUTING_DECAY,
            'routing_gain': ROUTING_GAIN,
            'state_variables': STATE_VARS,
            'hazard_boundaries': {k: list(v) for k, v in HAZARD_BOUNDARIES.items()},
            'elapsed_seconds': round(elapsed, 2),
        },
        'runs': runs,
        'cross_profile_summary': cross_profile_summary,
    }

    # --- Write output ---
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\nDone in {elapsed:.1f}s")
    print(f"Output: {OUTPUT_PATH} ({file_size_mb:.1f} MB)")
    print(f"Runs: {n_total_runs} ({n_preferred} preferred + {n_nonpreferred} non-preferred)")

    # --- Quick diagnostics ---
    print(f"\n{'=' * 70}")
    print("CROSS-PROFILE SUMMARY")
    print(f"{'=' * 70}")

    n_preferred_is_best = sum(
        1 for v in cross_profile_summary.values() if v['preferred_is_best']
    )
    print(f"Preferred profile is best (highest viability): "
          f"{n_preferred_is_best}/{len(cross_profile_summary)}")

    print(f"\n  {'Folio':<8} {'Sec':>3} {'Preferred':<28} {'Pref Viab':>9} "
          f"{'Best':>28} {'Best Viab':>9}  {'HC':>4}")
    print(f"  {'-'*8} {'-'*3} {'-'*28} {'-'*9} {'-'*28} {'-'*9}  {'-'*4}")

    for folio in PILOT_FOLIOS:
        if folio not in cross_profile_summary:
            continue
        s = cross_profile_summary[folio]
        mark = " *" if s['preferred_is_best'] else ""
        print(f"  {folio:<8} {s['section']:>3} {s['preferred_profile']:<28} "
              f"{s['preferred_viability']:>9.4f} "
              f"{s['best_profile']:>28} {s['best_viability']:>9.4f}  "
              f"{s['preferred_hazard_count']:>4}{mark}")

    # Viability distribution across preferred runs
    pref_viabs = []
    for folio in PILOT_FOLIOS:
        if folio in cross_profile_summary:
            pref_viabs.append(cross_profile_summary[folio]['preferred_viability'])

    if pref_viabs:
        pv_mean = sum(pref_viabs) / len(pref_viabs)
        pv_std = math.sqrt(sum((v - pv_mean)**2 for v in pref_viabs) / len(pref_viabs))
        print(f"\n  Preferred-run viability: "
              f"mean={pv_mean:.4f}, std={pv_std:.4f}, "
              f"min={min(pref_viabs):.4f}, max={max(pref_viabs):.4f}")


if __name__ == '__main__':
    main()
