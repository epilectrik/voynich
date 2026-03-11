"""
Phase 579 T4: Constrained Parameter Retuning

Tiered grid search to find passing configurations for each of the 8 stubborn
forgiving folios. Feeds C1666 (DECISIVE).

T4a: F1 x F2 sweep (144 grid points per folio).
T4b: Conditional 3rd-axis extension (F5 or F3) for folios still STRUCTURAL_ENDPOINT.

Per-folio classification:
  PARAMETER_UNDERFIT: passes in T4a with displacement < 0.3
  PARAMETER_ACHIEVABLE: passes in T4a with 0.3 <= displacement < 0.5,
                        OR passes in T4b with any displacement
  STRUCTURAL_ENDPOINT: no passing point found, or all passing points
                       require displacement >= 0.5
"""

import json, sys, os, math, time
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace, sort_key,
    assign_folio_profiles, compute_infra_scores,
    STATE_VARS, N_VARS, EQUILIBRIUM,
)
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
    build_demand_matched_assignments,
    R4_X_TO_Y, R4_C_TO_Y, R5_CTS_THRESHOLD,
    SV_INDEX, CTS_WEIGHTED_SVS, PROFILE_CLOSE_MULT, K_CLOSE,
)
from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import K_RELIEF
from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
    override_line_phases, build_demand_shuffled_phases, build_shuffled_event_map,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

STUBBORN_8 = ['f39v', 'f40r', 'f50v', 'f55v', 'f85r2', 'f86v5', 'f86v6', 'f95r2']
N_NULL_PERMS = 5

# Grid: F1 and F2 each in {0.5, 0.6, ..., 1.5, 1.6}
GRID_VALUES = [round(0.5 + i * 0.1, 1) for i in range(12)]

# Displacement thresholds
UNDERFIT_THRESHOLD = 0.3    # < 0.3 = calibration refinement
ACHIEVABLE_THRESHOLD = 0.5  # < 0.5 = achievable, >= 0.5 = effectively different model


def compute_config_mode(f4):
    if f4 < 0.33:
        return 'H0_LOW_INFRA'
    elif f4 > 0.67:
        return 'H2_HIGH_INFRA'
    else:
        return 'H1_MEDIUM_INFRA'


def run_single_config(profile, config_mode, folio, f1, f2, f3, f4, f5,
                      tokens, line_packets, cts_data, event_map,
                      line_states, assignments):
    """Run M1 + M4f for a single F-param configuration. Returns (m1_dye, m4f_dye, n_runs)."""
    app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

    # M1
    m1_result = run_enhanced_event_trace(app, tokens, line_packets, cts_data, event_map)
    m1_ev = select_events(m1_result.get('per_event_detail', []))
    m1_dye = compute_event_dye(m1_ev)
    n_runs = 1

    # M4f
    m4f_dyes = []
    for assignment in assignments[:N_NULL_PERMS]:
        shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
        new_lp = override_line_phases(line_packets, shuffled_phases)
        new_em = build_shuffled_event_map(event_map, shuffled_phases, line_packets)

        null_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)
        null_result = run_enhanced_event_trace(null_app, tokens, new_lp, cts_data, new_em)
        null_ev = select_events(null_result.get('per_event_detail', []))
        m4f_dyes.append(compute_event_dye(null_ev))
        n_runs += 1

    m4f_dye = sum(m4f_dyes) / len(m4f_dyes) if m4f_dyes else 0.0
    return m1_dye, m4f_dye, n_runs


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("T4: Constrained Parameter Retuning")
    print("Phase 579 - FORGIVING_POLE_RESIDUAL_AUDIT")

    # -- Load data --
    print("\n--- Loading data ---")
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        t1_setup = json.load(f)
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)

    print("  Loading line packets...")
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')) as f:
        line_packets = json.load(f)['line_packets']

    print("  Loading CTS data...")
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't7_closure_cts.json')) as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))

    print("  Loading supervisory tokens...")
    with open(os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                           'results', 't2b_supervisory_interface_unrouted.json')) as f:
        all_tokens = json.load(f)['token_signals']

    print("  Loading event taxonomy...")
    with open(os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                           'results', 't1_event_taxonomy.json')) as f:
        event_map = json.load(f)['event_map']

    print("  Loading T2 channel results...")
    with open(os.path.join(RESULTS_DIR, 't2_channel_decomposition.json')) as f:
        t2_channel = json.load(f)

    folio_configs = t1_setup['folio_configs']
    m0_line_states = t2_runs['m0_line_states']

    # Build tokens by folio
    tokens_by_folio = {f: [] for f in STUBBORN_8}
    for tok in all_tokens:
        if tok['folio'] in tokens_by_folio:
            tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # Build assignments per folio
    folio_assignments = {}
    for folio in STUBBORN_8:
        line_states = m0_line_states.get(folio, [])
        close_indices = [i for i, ls in enumerate(line_states)
                         if ls.get('packet_phase') == 'CLOSE']
        assignments = build_demand_matched_assignments(
            line_states, close_indices,
            n_permutations=N_NULL_PERMS, k_neighbors=5, seed=42
        )
        folio_assignments[folio] = (line_states, assignments)

    print("  Data loaded.")

    # ================================================================
    # T4a: F1 x F2 sweep
    # ================================================================
    print(f"\n--- T4a: F1 x F2 sweep ({len(GRID_VALUES)}x{len(GRID_VALUES)} = {len(GRID_VALUES)**2} per folio) ---")

    total_runs = 0
    t4a_results = {}

    for folio in STUBBORN_8:
        fc = folio_configs[folio]
        profile = fc['profile']
        orig_f1, orig_f2 = fc['F1'], fc['F2']
        f3, f4, f5 = fc['F3'], fc['F4_raw'], fc['F5']
        config_mode = compute_config_mode(f4)

        tokens = tokens_by_folio[folio]
        line_states, assignments = folio_assignments[folio]

        landscape = {}
        best_adv = -999
        best_f1, best_f2 = orig_f1, orig_f2
        passing_points = 0

        for g_f1 in GRID_VALUES:
            for g_f2 in GRID_VALUES:
                m1_dye, m4f_dye, n = run_single_config(
                    profile, config_mode, folio,
                    g_f1, g_f2, f3, f4, f5,
                    tokens, line_packets, cts_data, event_map,
                    line_states, assignments
                )
                total_runs += n

                adv = m1_dye - m4f_dye  # DYE_advantage (positive = grammar wins)
                passes = adv > 0

                landscape[f"{g_f1},{g_f2}"] = {
                    'm1_dye': round(m1_dye, 6),
                    'm4f_dye': round(m4f_dye, 6),
                    'dye_advantage': round(adv, 6),
                    'passes': passes,
                }

                if passes:
                    passing_points += 1

                if adv > best_adv:
                    best_adv = adv
                    best_f1 = g_f1
                    best_f2 = g_f2

        displacement = math.sqrt((best_f1 - orig_f1)**2 + (best_f2 - orig_f2)**2)
        passes_at_best = best_adv > 0

        # Classification
        if passes_at_best and displacement < UNDERFIT_THRESHOLD:
            classification = 'PARAMETER_UNDERFIT'
        elif passes_at_best and displacement < ACHIEVABLE_THRESHOLD:
            classification = 'PARAMETER_ACHIEVABLE'
        else:
            classification = 'STRUCTURAL_ENDPOINT'

        t4a_results[folio] = {
            'orig_f1': round(orig_f1, 4),
            'orig_f2': round(orig_f2, 4),
            'best_f1': round(best_f1, 4),
            'best_f2': round(best_f2, 4),
            'best_dye_advantage': round(best_adv, 6),
            'passes_at_best': passes_at_best,
            'displacement': round(displacement, 4),
            'passing_points': passing_points,
            'passing_fraction': round(passing_points / len(GRID_VALUES)**2, 4),
            't4a_classification': classification,
            'landscape': landscape,
        }

        status = 'PASS' if passes_at_best else 'FAIL'
        print(f"  {folio}: best=({best_f1},{best_f2}) adv={best_adv:+.4f} "
              f"disp={displacement:.3f} {status} [{classification}] "
              f"({passing_points}/{len(GRID_VALUES)**2} passing)")

    print(f"\n  T4a total runs: {total_runs}")

    # ================================================================
    # T4b: Conditional 3rd-axis extension
    # ================================================================
    print("\n--- T4b: Conditional 3rd-axis extension ---")

    # Determine which folios need T4b
    endpoint_folios = [f for f in STUBBORN_8
                       if t4a_results[f]['t4a_classification'] == 'STRUCTURAL_ENDPOINT']

    t4b_results = {}
    if not endpoint_folios:
        print("  No folios remain STRUCTURAL_ENDPOINT after T4a. Skipping T4b.")
    else:
        # Determine 3rd axis from T2 channel results
        dom_channels = t2_channel.get('dominant_channels', {})
        for folio in endpoint_folios:
            dom = dom_channels.get(folio, {}).get('post_gate_dominant', 'NO_R1')
            # R4 = containment-coupled -> try F5
            # R1/R2/R5 = close recovery -> try F3 (thermal accent)
            if 'R4' in dom:
                third_axis = 'F5'
            else:
                third_axis = 'F3'

            fc = folio_configs[folio]
            profile = fc['profile']
            f3_orig, f4, f5_orig = fc['F3'], fc['F4_raw'], fc['F5']
            config_mode = compute_config_mode(f4)
            tokens = tokens_by_folio[folio]
            line_states, assignments = folio_assignments[folio]

            # Use best F1/F2 from T4a (or original if no passing)
            best_f1 = t4a_results[folio]['best_f1']
            best_f2 = t4a_results[folio]['best_f2']

            t4b_best_adv = -999
            t4b_best_val = fc[third_axis] if third_axis == 'F3' else fc[third_axis]
            orig_3rd = fc['F3'] if third_axis == 'F3' else fc['F5']

            for g_val in GRID_VALUES:
                if third_axis == 'F3':
                    use_f3, use_f5 = g_val, f5_orig
                else:
                    use_f3, use_f5 = f3_orig, g_val

                m1_dye, m4f_dye, n = run_single_config(
                    profile, config_mode, folio,
                    best_f1, best_f2, use_f3, f4, use_f5,
                    tokens, line_packets, cts_data, event_map,
                    line_states, assignments
                )
                total_runs += n

                adv = m1_dye - m4f_dye
                if adv > t4b_best_adv:
                    t4b_best_adv = adv
                    t4b_best_val = g_val

            t4b_passes = t4b_best_adv > 0
            # Extended displacement: F1, F2, and 3rd axis
            orig_f1, orig_f2 = fc['F1'], fc['F2']
            ext_disp = math.sqrt(
                (best_f1 - orig_f1)**2 +
                (best_f2 - orig_f2)**2 +
                (t4b_best_val - orig_3rd)**2
            )

            # Reclassify
            if t4b_passes:
                final_class = 'PARAMETER_ACHIEVABLE'
            else:
                final_class = 'STRUCTURAL_ENDPOINT'

            t4b_results[folio] = {
                'third_axis': third_axis,
                'orig_3rd_value': round(orig_3rd, 4),
                'best_3rd_value': round(t4b_best_val, 4),
                'best_f1': round(best_f1, 4),
                'best_f2': round(best_f2, 4),
                'best_dye_advantage': round(t4b_best_adv, 6),
                'passes': t4b_passes,
                'extended_displacement': round(ext_disp, 4),
                't4b_classification': final_class,
            }

            status = 'PASS' if t4b_passes else 'FAIL'
            print(f"  {folio}: {third_axis}={t4b_best_val} adv={t4b_best_adv:+.4f} "
                  f"ext_disp={ext_disp:.3f} {status} [{final_class}]")

    print(f"\n  T4b total runs: {total_runs - sum(1 for _ in [])}")

    # ================================================================
    # Final classification
    # ================================================================
    print("\n--- Final per-folio classification ---")

    final_classifications = {}
    for folio in STUBBORN_8:
        t4a_class = t4a_results[folio]['t4a_classification']
        if t4a_class != 'STRUCTURAL_ENDPOINT':
            final_class = t4a_class
        elif folio in t4b_results:
            final_class = t4b_results[folio]['t4b_classification']
        else:
            final_class = 'STRUCTURAL_ENDPOINT'

        final_classifications[folio] = final_class
        print(f"  {folio}: {final_class}")

    # Aggregate C1666
    class_counts = {}
    for cls in final_classifications.values():
        class_counts[cls] = class_counts.get(cls, 0) + 1

    n_endpoint = class_counts.get('STRUCTURAL_ENDPOINT', 0)
    n_underfit = class_counts.get('PARAMETER_UNDERFIT', 0)

    if n_endpoint >= 6:
        c1666_verdict = 'STRUCTURAL_ENDPOINT_CONFIRMED'
    elif n_underfit >= 6:
        c1666_verdict = 'PARAMETER_UNDERFIT_CONFIRMED'
    else:
        c1666_verdict = 'MIXED_BOUNDARY_STRATUM'

    print(f"\n  Classification counts: {class_counts}")
    print(f"  -> C1666 verdict: {c1666_verdict}")

    # -- Save results --
    results = {
        'metadata': {
            'phase': 579,
            'script': 't4_constrained_retuning',
            'grid_values': GRID_VALUES,
            'n_grid_points': len(GRID_VALUES)**2,
            'n_folios': 8,
            'n_null_perms': N_NULL_PERMS,
            'total_runs': total_runs,
            'runtime_s': round(time.time() - t_start, 2),
        },
        't4a_results': {f: {k: v for k, v in r.items() if k != 'landscape'}
                        for f, r in t4a_results.items()},
        't4a_landscapes': {f: r['landscape'] for f, r in t4a_results.items()},
        't4b_results': t4b_results,
        'final_classifications': final_classifications,
        'c1666_inputs': {
            'classification_counts': class_counts,
            'n_endpoint': n_endpoint,
            'n_underfit': n_underfit,
            'n_achievable': class_counts.get('PARAMETER_ACHIEVABLE', 0),
            'c1666_verdict': c1666_verdict,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't4_constrained_retuning.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\nT4 complete in {elapsed:.1f}s. Saved to {out_path}")


if __name__ == '__main__':
    main()
