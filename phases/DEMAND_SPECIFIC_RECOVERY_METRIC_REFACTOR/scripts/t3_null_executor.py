"""
T3: Null Executor -- Demand-Matched Null Permutations
Phase 570b - DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR

Runs demand-matched null permutations (M4 generic + M4f folio-specific) across
4 pilot folios with enhanced per-event state collection, including matched-event
tracking.

Total runs: M4f (80) + M4 (80) = 160.  No M3 standard nulls.

For each permutation, saves:
  - per_event_detail[] with enhanced state vectors (from T1)
  - matched_events[] -- only events at demand-matched positions
  - assignment[] -- the (real_close_idx, matched_idx) pairs
  - aggregate metrics and events_by_type/events_by_demand

Input:
  - t2_full_model_runs.json  (m0_line_states per folio)
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t3_line_packets.json     (line-level packet info)
  - t7_closure_cts.json      (per-line CTS)
  - t2_folio_budgets.json    (folio budgets for profile assignment)
  - t1_event_taxonomy.json   (event map, section thresholds)
  - t1_pilot_selection.json  (F1-F5 parameters)
  - regime_folio_mapping.json

Output:
  - t3_null_runs.json
"""

import json
import sys
import os
import copy
import time
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Imports from T1 enhanced event trace (canonical for 570b)
# ---------------------------------------------------------------------------
from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace,
    FolioSpecificApparatus,
    SELECTED_FOLIOS,
    sort_key,
    assign_folio_profiles, compute_infra_scores,
    build_configured_apparatus,
    PILOT_FOLIOS as ALL_PILOT_FOLIOS,
)

# ---------------------------------------------------------------------------
# Import demand-matched assignment builder from 570a T2
# ---------------------------------------------------------------------------
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    build_demand_matched_assignments,
)


# ---------------------------------------------------------------------------
# Helper: Override line phases in line_packets
# ---------------------------------------------------------------------------
def override_line_phases(line_packets, shuffled_phases):
    """Create a copy of line_packets with overridden packet_phase values.

    The run_enhanced_event_trace reads phases from:
        line_packets[line_key]['packet_state']['packet_phase']

    This function creates a shallow-ish copy where only the packet_state
    dict is replaced for lines that have a phase override.
    """
    modified = {}
    for key, lp in line_packets.items():
        if key in shuffled_phases:
            new_lp = dict(lp)
            new_ps = dict(lp.get('packet_state', {}))
            new_ps['packet_phase'] = shuffled_phases[key]
            new_lp['packet_state'] = new_ps
            modified[key] = new_lp
        else:
            modified[key] = lp
    return modified


# ---------------------------------------------------------------------------
# Helper: Build shuffled phases from demand-matched assignment
# ---------------------------------------------------------------------------
def build_demand_shuffled_phases(line_states, assignment):
    """Build a shuffled_phases dict from a demand-matched assignment."""
    shuffled = {}
    for ls in line_states:
        shuffled[ls['line_key']] = ls['packet_phase']

    for real_idx, matched_idx in assignment:
        real_lk = line_states[real_idx]['line_key']
        matched_lk = line_states[matched_idx]['line_key']
        matched_orig_phase = line_states[matched_idx]['packet_phase']

        shuffled[matched_lk] = 'CLOSE'
        shuffled[real_lk] = matched_orig_phase

    return shuffled


# ---------------------------------------------------------------------------
# Helper: Build shuffled event_map
# ---------------------------------------------------------------------------
def build_shuffled_event_map(original_event_map, shuffled_phases, line_packets):
    """Build event map for shuffled phases.

    All lines with shuffled phase == CLOSE get event entries.
    Original CLOSE lines that got swapped to non-CLOSE are excluded.
    """
    close_phase = 'CLOSE'
    new_map = {}

    for line_key, phase in shuffled_phases.items():
        if phase == close_phase:
            if line_key in original_event_map:
                new_map[line_key] = original_event_map[line_key]
            else:
                lp = line_packets.get(line_key, {})
                section = lp.get('section', 'B')
                new_map[line_key] = {
                    'packet_types_global': ['E_any'],
                    'packet_types_section': ['E_any'],
                    'has_work_predecessor': False,
                    'work_predecessor_key': None,
                    'section': section,
                    'cts': 0.0,
                    'mcb': 0.0,
                    'cob': 0.0,
                    'q4o': 0.0,
                    'armed': False,
                    'is_pilot': True,
                }

    # Recalculate work predecessors based on shuffled phases
    folio_lines = {}
    for lk in shuffled_phases:
        parts = lk.split('|')
        if len(parts) != 2:
            continue
        folio = parts[0]
        line_id = parts[1]
        try:
            line_num = int(line_id)
            line_frac = 0.0
        except ValueError:
            digits = ''
            alpha = ''
            for ch in line_id:
                if ch.isdigit():
                    digits += ch
                else:
                    alpha += ch
            line_num = int(digits) if digits else 9999
            line_frac = 0.1 if alpha else 0.0
        folio_lines.setdefault(folio, []).append((line_num + line_frac, lk))

    for folio, flines in folio_lines.items():
        flines.sort()
        for i, (ln, lk) in enumerate(flines):
            if lk in new_map and shuffled_phases.get(lk) == close_phase:
                if i > 0:
                    prev_lk = flines[i - 1][1]
                    prev_phase = shuffled_phases.get(prev_lk, 'WORK')
                    new_map[lk]['has_work_predecessor'] = (prev_phase == 'WORK')
                    if prev_phase == 'WORK':
                        new_map[lk]['work_predecessor_key'] = prev_lk
                    else:
                        new_map[lk]['work_predecessor_key'] = None
                else:
                    new_map[lk]['has_work_predecessor'] = False
                    new_map[lk]['work_predecessor_key'] = None

    return new_map


# ---------------------------------------------------------------------------
# Data loading (reused from T2)
# ---------------------------------------------------------------------------
def load_data():
    """Load all data sources."""
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    print("  Loading line packets...")
    lp_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')
    with open(lp_path, 'r', encoding='utf-8') as f:
        lp_raw = json.load(f)
    line_packets = lp_raw['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    print("  Loading CTS data...")
    cts_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path, 'r', encoding='utf-8') as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            if isinstance(val, dict):
                cts_data[key] = val.get('cts', 0.0)
            else:
                cts_data[key] = float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            if isinstance(val, dict):
                cts_data[key] = val.get('cts', val.get('score', 0.0))
            else:
                cts_data[key] = float(val)
    print(f"    CTS entries: {len(cts_data)}")

    print("  Loading supervisory tokens...")
    sup_path = os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                            'results', 't2b_supervisory_interface_unrouted.json')
    with open(sup_path, 'r', encoding='utf-8') as f:
        sup_raw = json.load(f)
    all_tokens = sup_raw['token_signals']
    print(f"    Total tokens: {len(all_tokens)}")

    print("  Loading folio budgets...")
    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    with open(budget_path, 'r', encoding='utf-8') as f:
        budgets = json.load(f)

    print("  Loading T1 event taxonomy...")
    event_path = os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                              'results', 't1_event_taxonomy.json')
    with open(event_path, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']
    print(f"    Event map entries: {len(event_map)}")

    print("  Loading T1 pilot selection (F1-F5 values)...")
    pilot_path = os.path.join(phases_dir, 'FOLIO_SPECIFIC_APPARATUS_PILOT',
                              'results', 't1_pilot_selection.json')
    with open(pilot_path, 'r', encoding='utf-8') as f:
        pilot_selection = json.load(f)
    folio_params = pilot_selection['folio_parameters']
    print(f"    Folio parameters: {len(folio_params)}")

    print("  Loading T2 output (m0_line_states)...")
    t2_path = os.path.join(phases_dir, 'DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR',
                           'results', 't2_full_model_runs.json')
    with open(t2_path, 'r', encoding='utf-8') as f:
        t2_output = json.load(f)
    m0_line_states = t2_output['m0_line_states']
    print(f"    M0 line_states folios: {list(m0_line_states.keys())}")

    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (line_packets, cts_data, all_tokens, budgets, budget_path,
            event_map, folio_params, m0_line_states, regime_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: Null Executor - Demand-Matched (M4 + M4f)")
    print("Phase 570b - DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data sources ---")
    (line_packets, cts_data, all_tokens, budgets, budget_path,
     event_map, folio_params, m0_line_states, regime_path) = load_data()

    # ---- Assign folio profiles and config modes ----
    print("\n--- Resolving folio profiles and config modes ---")
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(ALL_PILOT_FOLIOS)

    folio_config = {}
    for folio in SELECTED_FOLIOS:
        fp = folio_params[folio]
        profile = fp['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        f_vals = {
            'f1': fp['F1'],
            'f2': fp['F2'],
            'f3': fp['F3'],
            'f4_raw': fp['F4_raw'],
            'f5': fp['F5'],
        }
        folio_config[folio] = {
            'profile': profile,
            'config_mode': config_mode,
            'section': fp['section'],
            **f_vals,
        }
        print(f"  {folio}: profile={profile}, config={config_mode}")

    # ---- Group and sort tokens ----
    print("\n--- Extracting selected folio tokens ---")
    selected_set = set(SELECTED_FOLIOS)
    tokens_by_folio = {f: [] for f in selected_set}
    for tok in all_tokens:
        if tok['folio'] in selected_set:
            tokens_by_folio[tok['folio']].append(tok)

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    for folio in SELECTED_FOLIOS:
        n = len(tokens_by_folio[folio])
        print(f"  {folio}: {n} tokens")

    # ---- Build demand-matched assignments per folio ----
    print("\n--- Building demand-matched assignments ---")
    n_perms = 20
    assignments_by_folio = {}

    for folio in SELECTED_FOLIOS:
        line_states = m0_line_states[folio]
        close_indices = [i for i, ls in enumerate(line_states)
                         if ls['packet_phase'] == 'CLOSE']
        assignments = build_demand_matched_assignments(
            line_states, close_indices,
            n_permutations=n_perms, k_neighbors=5, seed=42
        )
        assignments_by_folio[folio] = assignments
        n_close = len(close_indices)
        print(f"  {folio}: {n_close} CLOSE lines, {len(assignments)} permutations, "
              f"{len(assignments[0]) if assignments else 0} swaps/perm")

    # ================================================================
    # M4f: Demand-matched with folio-specific apparatus (80 runs)
    # ================================================================
    print("\n--- M4f: Demand-matched (folio-specific) ---")
    m4f_results = {}
    run_count = 0
    total_runs = n_perms * len(SELECTED_FOLIOS) * 2  # M4f + M4

    for folio in SELECTED_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        fc = folio_config[folio]
        line_states = m0_line_states[folio]
        assignments = assignments_by_folio[folio]

        folio_perms = []
        for perm_idx, assignment in enumerate(assignments):
            shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
            modified_lps = override_line_phases(line_packets, shuffled_phases)
            shuffled_event_map = build_shuffled_event_map(
                event_map, shuffled_phases, line_packets
            )

            app = FolioSpecificApparatus(
                profile=fc['profile'],
                config_mode=fc['config_mode'],
                folio=folio,
                f1=fc['f1'], f2=fc['f2'], f3=fc['f3'],
                f4_raw=fc['f4_raw'], f5=fc['f5'],
            )

            result = run_enhanced_event_trace(
                app, toks, modified_lps, cts_data, shuffled_event_map
            )

            matched_line_keys = set()
            for real_idx, matched_idx in assignment:
                matched_lk = line_states[matched_idx]['line_key']
                matched_line_keys.add(matched_lk)

            per_event_detail = result['per_event_detail']
            matched_events = [e for e in per_event_detail
                              if e['line_key'] in matched_line_keys]

            result.pop('line_states', None)

            perm_result = {
                'metrics': result['metrics'],
                'events_by_type': result['events_by_type'],
                'events_by_demand': result['events_by_demand'],
                'per_event_detail': per_event_detail,
                'matched_events': matched_events,
                'assignment': assignment,
            }
            folio_perms.append(perm_result)

            run_count += 1
            if (perm_idx + 1) % 5 == 0 or perm_idx == 0:
                m = result['metrics']
                n_ev = len(per_event_detail)
                n_matched = len(matched_events)
                print(f"  [{run_count:3d}/{total_runs}] {folio} M4f perm {perm_idx+1:2d}/{n_perms}: "
                      f"events={n_ev} matched={n_matched} "
                      f"PCV={m['PCV']:.4f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f}")

        m4f_results[folio] = {'all_perms': folio_perms}

    t_m4f = time.time()
    print(f"\n  M4f completed: {run_count} runs in {t_m4f - t0:.1f}s")

    # ================================================================
    # M4: Demand-matched with generic apparatus (80 runs)
    # ================================================================
    print("\n--- M4: Demand-matched (generic) ---")
    m4_results = {}
    m4_start = run_count

    for folio in SELECTED_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        fc = folio_config[folio]
        line_states = m0_line_states[folio]
        assignments = assignments_by_folio[folio]

        app_template_profile = fc['profile']
        app_template_config = fc['config_mode']

        folio_perms = []
        for perm_idx, assignment in enumerate(assignments):
            shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
            modified_lps = override_line_phases(line_packets, shuffled_phases)
            shuffled_event_map = build_shuffled_event_map(
                event_map, shuffled_phases, line_packets
            )

            app = build_configured_apparatus(app_template_profile, app_template_config)

            result = run_enhanced_event_trace(
                app, toks, modified_lps, cts_data, shuffled_event_map
            )

            matched_line_keys = set()
            for real_idx, matched_idx in assignment:
                matched_lk = line_states[matched_idx]['line_key']
                matched_line_keys.add(matched_lk)

            per_event_detail = result['per_event_detail']
            matched_events = [e for e in per_event_detail
                              if e['line_key'] in matched_line_keys]

            result.pop('line_states', None)

            perm_result = {
                'metrics': result['metrics'],
                'events_by_type': result['events_by_type'],
                'events_by_demand': result['events_by_demand'],
                'per_event_detail': per_event_detail,
                'matched_events': matched_events,
                'assignment': assignment,
            }
            folio_perms.append(perm_result)

            run_count += 1
            if (perm_idx + 1) % 5 == 0 or perm_idx == 0:
                m = result['metrics']
                n_ev = len(per_event_detail)
                n_matched = len(matched_events)
                print(f"  [{run_count:3d}/{total_runs}] {folio} M4 perm {perm_idx+1:2d}/{n_perms}: "
                      f"events={n_ev} matched={n_matched} "
                      f"PCV={m['PCV']:.4f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f}")

        m4_results[folio] = {'all_perms': folio_perms}

    t_m4 = time.time()
    print(f"\n  M4 completed: {run_count - m4_start} runs in {t_m4 - t_m4f:.1f}s")

    # ================================================================
    # Summary
    # ================================================================
    print(f"\n{'=' * 70}")
    print("NULL SUMMARY")
    print(f"{'=' * 70}")

    for model_name, model_results in [('M4f', m4f_results), ('M4', m4_results)]:
        print(f"\n  --- {model_name} ---")
        for folio in SELECTED_FOLIOS:
            if folio not in model_results:
                continue
            perms = model_results[folio]['all_perms']
            n_perms_actual = len(perms)

            pcv_vals = [p['metrics']['PCV'] for p in perms]
            ccy_vals = [p['metrics']['CCY'] for p in perms]
            ueb_vals = [p['metrics']['UEB'] for p in perms]
            yf_vals = [p['metrics']['old_y_final'] for p in perms]
            n_events = [len(p['per_event_detail']) for p in perms]
            n_matched = [len(p['matched_events']) for p in perms]

            mean_pcv = sum(pcv_vals) / n_perms_actual
            mean_ccy = sum(ccy_vals) / n_perms_actual
            mean_ueb = sum(ueb_vals) / n_perms_actual
            mean_yf = sum(yf_vals) / n_perms_actual
            mean_events = sum(n_events) / n_perms_actual
            mean_matched = sum(n_matched) / n_perms_actual

            print(f"  {folio}: {n_perms_actual} perms, "
                  f"mean_events={mean_events:.1f} mean_matched={mean_matched:.1f}")
            print(f"    PCV={mean_pcv:.4f} CCY={mean_ccy:.4f} "
                  f"UEB={mean_ueb:.1f} Yf={mean_yf:.4f}")

    # ================================================================
    # Build output
    # ================================================================
    print(f"\n--- Writing output ---")

    output = {
        'metadata': {
            'phase': '570b',
            'script': 't3_null_executor.py',
            'total_runs': run_count,
            'n_permutations': n_perms,
            'models': ['M4f', 'M4'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'selected_folios': SELECTED_FOLIOS,
            'seed': 42,
        },
        'm4f_demand_matched': m4f_results,
        'm4_demand_matched': m4_results,
    }

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 't3_null_runs.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = os.path.getsize(out_path)
    print(f"  Output: {out_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    t_final = time.time()
    print(f"\n  Total time: {t_final - t0:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
