"""
Phase 579 T2: Channel Decomposition

Per-folio R1-R5 sub-ablation restricted to the 8 stubborn forgiving folios.
Compares pre-gate (Phase 574 existing data) vs post-gate (new simulation
under AMB_PESSIMISTIC regime admission) channel profiles.

Feeds C1664.

New simulation: 8 folios x 7 sub-ablations x (1 M1 + 5 M4f) = 336 traces.
"""

import json, sys, os, copy, time
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
from phases.COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP.scripts.t1_recovery_gate_decomposition import (
    R4AblatedApparatus, create_sub_ablated_apparatus,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

SUB_ABLATION_NAMES = ['NO_R1', 'NO_R2', 'NO_R3', 'NO_R4', 'NO_R5', 'NO_R1_C_ONLY', 'NO_R4_C_ONLY']
N_NULL_PERMS = 5
STUBBORN_8 = ['f39v', 'f40r', 'f50v', 'f55v', 'f85r2', 'f86v5', 'f86v6', 'f95r2']


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("T2: Channel Decomposition (8 stubborn folios)")
    print("Phase 579 - FORGIVING_POLE_RESIDUAL_AUDIT")

    # -- Load data --
    print("\n--- Loading data ---")
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    print("  Loading Phase 572 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        t1_setup = json.load(f)

    print("  Loading Phase 572 M1 runs...")
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)

    print("  Loading Phase 572 M4f nulls...")
    with open(os.path.join(P572_RESULTS, 't3_null_runs.json')) as f:
        t3_nulls = json.load(f)

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

    print("  Loading Phase 574 sub-ablation (pre-gate baseline)...")
    with open(os.path.join(phases_dir,
        'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP', 'results',
        't1_recovery_gate_decomposition.json')) as f:
        p574_sub = json.load(f)
    pre_gate_sub = p574_sub['per_folio_sub_ablation']

    print("  Loading T0 census...")
    with open(os.path.join(RESULTS_DIR, 't0_pole_census.json')) as f:
        t0 = json.load(f)

    folio_configs = t1_setup['folio_configs']
    all_folios = t1_setup['all_folios']
    m0_line_states = t2_runs['m0_line_states']
    null_data = t3_nulls['m4f_demand_matched']

    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(all_folios)

    # Build tokens by folio
    tokens_by_folio = {f: [] for f in STUBBORN_8}
    for tok in all_tokens:
        if tok['folio'] in tokens_by_folio:
            tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # -- Step 1: Compute baseline (ungated) DYE for the 8 --
    print("\n--- Step 1: Baseline DYE ---")
    baseline = {}
    for folio in STUBBORN_8:
        m1_events = t2_runs['primary_runs'][folio]['M1']['per_event_detail']
        m1_dye = compute_event_dye(select_events(m1_events))

        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            sel = select_events(perm.get('matched_events', []))
            perm_dyes.append(compute_event_dye(sel))
        m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        baseline[folio] = {'m1_dye': m1_dye, 'm4f_dye': m4f_dye}
        print(f"  {folio}: M1={m1_dye:.4f}, M4f={m4f_dye:.4f}")

    # -- Step 2: Run sub-ablation for each folio --
    print("\n--- Step 2: Sub-ablation (8 folios x 7 conditions) ---")

    run_count = 0
    post_gate_results = {}

    for folio in STUBBORN_8:
        fc = folio_configs[folio]
        profile = fc['profile']
        f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

        # Determine config_mode from F4
        if f4 < 0.33:
            config_mode = 'H0_LOW_INFRA'
        elif f4 > 0.67:
            config_mode = 'H2_HIGH_INFRA'
        else:
            config_mode = 'H1_MEDIUM_INFRA'

        tokens = tokens_by_folio[folio]

        # Build demand-matched assignments from m0_line_states (same as Phase 574)
        line_states = m0_line_states.get(folio, [])
        close_indices = [i for i, ls in enumerate(line_states)
                         if ls.get('packet_phase') == 'CLOSE']
        assignments = build_demand_matched_assignments(
            line_states, close_indices,
            n_permutations=N_NULL_PERMS, k_neighbors=5, seed=42
        )

        folio_results = {}
        for sub_name in SUB_ABLATION_NAMES:
            # Build base apparatus
            base_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

            # Create sub-ablated version
            abl_app = create_sub_ablated_apparatus(base_app, sub_name)

            # Run M1
            m1_result = run_enhanced_event_trace(abl_app, tokens, line_packets, cts_data, event_map)
            m1_ev = select_events(m1_result.get('per_event_detail', []))
            abl_m1_dye = compute_event_dye(m1_ev)
            run_count += 1

            # Run M4f (N_NULL_PERMS)
            m4f_dyes = []
            for assignment in assignments[:N_NULL_PERMS]:
                shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
                new_lp = override_line_phases(line_packets, shuffled_phases)
                new_em = build_shuffled_event_map(event_map, shuffled_phases, line_packets)

                null_app = create_sub_ablated_apparatus(
                    FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5),
                    sub_name)
                null_result = run_enhanced_event_trace(null_app, tokens, new_lp, cts_data, new_em)
                null_ev = select_events(null_result.get('per_event_detail', []))
                m4f_dyes.append(compute_event_dye(null_ev))
                run_count += 1

            abl_m4f_dye = sum(m4f_dyes) / len(m4f_dyes) if m4f_dyes else 0.0

            base_m1 = baseline[folio]['m1_dye']
            base_m4f = baseline[folio]['m4f_dye']

            folio_results[sub_name] = {
                'abl_m1_dye': round(abl_m1_dye, 6),
                'abl_m4f_dye': round(abl_m4f_dye, 6),
                'delta_m1_dye': round(base_m1 - abl_m1_dye, 6),
                'delta_m4f_dye': round(base_m4f - abl_m4f_dye, 6),
                'delta_dye_advantage': round((base_m1 - abl_m1_dye) - (base_m4f - abl_m4f_dye), 6),
            }

        post_gate_results[folio] = folio_results
        print(f"  {folio}: 7 sub-ablations complete")

    print(f"\n  Total runs: {run_count}")

    # -- Step 3: Pre-gate vs post-gate comparison --
    print("\n--- Step 3: Pre-gate vs post-gate comparison ---")

    comparison = {}
    for folio in STUBBORN_8:
        pre = pre_gate_sub.get(folio, {}).get('sub_ablations', {})
        post = post_gate_results[folio]
        base_m4f = baseline[folio]['m4f_dye']

        folio_comp = {}
        for sub_name in SUB_ABLATION_NAMES:
            pre_delta = pre.get(sub_name, {}).get('delta_m4f_dye', 0)
            post_delta = post[sub_name]['delta_m4f_dye']

            pre_share = pre_delta / base_m4f if base_m4f != 0 else 0
            post_share = post_delta / base_m4f if base_m4f != 0 else 0

            folio_comp[sub_name] = {
                'pre_gate_delta': round(pre_delta, 6),
                'post_gate_delta': round(post_delta, 6),
                'pre_gate_share': round(pre_share, 4),
                'post_gate_share': round(post_share, 4),
                'share_shift': round(post_share - pre_share, 4),
            }
        comparison[folio] = folio_comp

    # -- Step 4: Dominant channel analysis --
    print("\n--- Step 4: Dominant channel identification ---")

    dominant_channels = {}
    for folio in STUBBORN_8:
        comp = comparison[folio]
        # Find dominant sub-channel by pre-gate delta_m4f_dye (contribution to CCS1)
        best_pre = max(SUB_ABLATION_NAMES, key=lambda s: comp[s]['pre_gate_delta'])
        best_post = max(SUB_ABLATION_NAMES, key=lambda s: comp[s]['post_gate_delta'])

        pre_share = comp[best_pre]['pre_gate_share']
        post_share = comp[best_post]['post_gate_share']

        dominant_channels[folio] = {
            'pre_gate_dominant': best_pre,
            'pre_gate_dominant_share': round(pre_share, 4),
            'post_gate_dominant': best_post,
            'post_gate_dominant_share': round(post_share, 4),
            'dominant_changed': best_pre != best_post,
        }
        changed = ' ** CHANGED' if best_pre != best_post else ''
        print(f"  {folio}: pre={best_pre}({pre_share:.2f}) -> post={best_post}({post_share:.2f}){changed}")

    # Count consensus
    pre_counts = {}
    post_counts = {}
    for folio in STUBBORN_8:
        pre = dominant_channels[folio]['pre_gate_dominant']
        post = dominant_channels[folio]['post_gate_dominant']
        pre_counts[pre] = pre_counts.get(pre, 0) + 1
        post_counts[post] = post_counts.get(post, 0) + 1

    print(f"\n  Pre-gate dominant counts: {pre_counts}")
    print(f"  Post-gate dominant counts: {post_counts}")

    # Check concentration: single channel >60% share in >=6/8
    concentrated_count = 0
    for folio in STUBBORN_8:
        max_share = max(comparison[folio][s]['post_gate_share'] for s in SUB_ABLATION_NAMES)
        if max_share > 0.60:
            concentrated_count += 1

    # C1664 assessment
    most_common_post = max(post_counts, key=post_counts.get)
    most_common_count = post_counts[most_common_post]

    if concentrated_count >= 6 and most_common_count >= 6:
        channel_verdict = 'CHANNEL_CONCENTRATED'
    elif most_common_count < 4:
        channel_verdict = 'CHANNEL_HETEROGENEOUS'
    else:
        channel_verdict = 'CHANNEL_DIFFUSE'

    print(f"\n  Concentrated (>60% share) count: {concentrated_count}/8")
    print(f"  Most common post-gate dominant: {most_common_post} ({most_common_count}/8)")
    print(f"  -> C1664 verdict: {channel_verdict}")

    # -- Save results --
    results = {
        'metadata': {
            'phase': 579,
            'script': 't2_channel_decomposition',
            'n_folios': 8,
            'n_sub_ablations': 7,
            'n_null_perms': N_NULL_PERMS,
            'total_runs': run_count,
            'runtime_s': round(time.time() - t_start, 2),
        },
        'baseline': {f: {k: round(v, 6) for k, v in baseline[f].items()} for f in STUBBORN_8},
        'post_gate_sub_ablation': post_gate_results,
        'pre_vs_post_comparison': comparison,
        'dominant_channels': dominant_channels,
        'c1664_inputs': {
            'pre_gate_dominant_counts': pre_counts,
            'post_gate_dominant_counts': post_counts,
            'concentrated_count': concentrated_count,
            'channel_verdict': channel_verdict,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't2_channel_decomposition.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\nT2 complete in {elapsed:.1f}s. Saved to {out_path}")


if __name__ == '__main__':
    main()
