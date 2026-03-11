"""
T2: Strength-Gated Simulation (5 Configs)
Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE

Runs StrengthGatedApparatus across 76 folios under 5 gate configurations
with per-band, per-class×strength, and structural-zero tracking.

76 folios × 5 configs × (1 M1 + 5 M4f) = 2,280 event traces.
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace,
    sort_key,
    assign_folio_profiles, compute_infra_scores,
)
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
    build_demand_matched_assignments,
)
from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
    override_line_phases, build_demand_shuffled_phases, build_shuffled_event_map,
)

from phases.AUTHENTICITY_STRENGTH_REGIME_GATE.scripts.t1_strength_gated_apparatus import (
    create_strength_gated_apparatus,
    run_strength_gated_event_trace,
    build_strength_gate_configs,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

N_NULL_PERMS = 5


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T2: Strength-Gated Simulation (5 Configs)")
    print("Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE")
    print("=" * 70)

    # ---- Load all data ----
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

    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    # Load Phase 576 T0 corpus classification (frozen)
    print("  Loading Phase 576 T0 classification (frozen)...")
    p576_t0_path = os.path.join(PROJECT_ROOT,
        'phases/CLOSURE_REGIME_ADMISSION_GATE/results/t0_corpus_classification.json')
    with open(p576_t0_path) as f:
        p576_t0 = json.load(f)
    per_line_class = p576_t0['per_line_classification']
    burden_threshold = p576_t0['burden_calibration']['recommended_threshold']

    # Load Phase 577 T0 strength
    print("  Loading Phase 577 T0 strength...")
    with open(os.path.join(RESULTS_DIR, 't0_authenticity_strength_assembly.json')) as f:
        t0_strength = json.load(f)
    per_line_strength = t0_strength['per_line_strength']

    # Build structural zero set from T0 output
    structural_zero_cells = set()
    for sz in t0_strength.get('structural_zeros', []):
        parts = sz.split('+')
        if len(parts) == 2:
            structural_zero_cells.add((parts[0], parts[1]))
    print(f"  Structural zero cells: {len(structural_zero_cells)}")

    eligible_folios = t1_setup['eligible_folios']
    all_folios = t1_setup['all_folios']
    folio_configs = t1_setup['folio_configs']
    primary_runs = t2_runs['primary_runs']
    m0_line_states = t2_runs['m0_line_states']
    null_data = t3_nulls['m4f_demand_matched']

    print(f"  Eligible folios: {len(eligible_folios)}")
    print(f"  Burden threshold: {burden_threshold}")

    # Setup tokens
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(all_folios)

    eligible_set = set(eligible_folios)
    tokens_by_folio = {f: [] for f in eligible_set}
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # ================================================================
    # STEP 1: Compute baseline DYE from stored data
    # ================================================================
    print("\n--- Step 1: Baseline DYE ---")
    baseline = {}
    for folio in eligible_folios:
        fc = folio_configs[folio]
        m1_events = primary_runs[folio]['M1']['per_event_detail']
        selected_m1 = select_events(m1_events)
        m1_dye = compute_event_dye(selected_m1)

        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            matched = perm.get('matched_events', [])
            sel = select_events(matched)
            perm_dyes.append(compute_event_dye(sel))
        m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        baseline[folio] = {
            'm1_dye': m1_dye,
            'm4f_dye': m4f_dye,
            'advantage': m1_dye - m4f_dye,
            'profile': fc['profile'],
        }

    # ================================================================
    # STEP 2: Build gate configurations
    # ================================================================
    print("\n--- Step 2: Gate configurations ---")
    gate_configs = build_strength_gate_configs(burden_threshold)
    print(f"  Configs: {list(gate_configs.keys())}")

    # ================================================================
    # STEP 3: Run gated simulations
    # ================================================================
    per_config = {}
    admission_stats = {}
    sz_activations_per_config = {}
    total_runs = len(gate_configs) * len(eligible_folios) * (1 + N_NULL_PERMS)
    run_count = 0

    for config_name, config in gate_configs.items():
        print(f"\n--- Config: {config_name} ---")
        per_folio_results = {}
        config_admission = defaultdict(int)
        config_sz_total = 0

        for folio in eligible_folios:
            fc = folio_configs[folio]
            toks = tokens_by_folio[folio]
            if not toks:
                continue

            profile = fc['profile']
            config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

            f_params = {
                'config_mode': config_mode,
                'f1': fc['F1'], 'f2': fc['F2'], 'f3': fc['F3'],
                'f4_raw': fc['F4_raw'], 'f5': fc['F5'],
            }

            # --- M1 gated run ---
            app = create_strength_gated_apparatus(
                folio, profile, f_params, per_line_class,
                config['table'], config['burden_threshold'],
                per_line_strength)

            result = run_strength_gated_event_trace(
                app, toks, line_packets, cts_data, event_map)
            result.pop('line_states', None)
            m1_events = result['per_event_detail']
            selected_m1 = select_events(m1_events)
            gated_m1_dye = compute_event_dye(selected_m1)
            run_count += 1

            # Track admission stats
            for entry in app._admission_log:
                if entry['admit'] < 0.01:
                    config_admission['rejected'] += 1
                elif entry['admit'] < 0.99:
                    config_admission['partial'] += 1
                else:
                    config_admission['full'] += 1
                config_admission[f"class_{entry['class']}"] += 1

            # --- M4f gated runs ---
            line_states = m0_line_states[folio]
            close_indices = [i for i, ls in enumerate(line_states)
                             if ls['packet_phase'] == 'CLOSE']
            assignments = build_demand_matched_assignments(
                line_states, close_indices,
                n_permutations=N_NULL_PERMS, k_neighbors=5, seed=42)

            perm_dyes = []
            if assignments:
                for assignment in assignments:
                    shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
                    shuffled_lp = override_line_phases(line_packets, shuffled_phases)
                    shuffled_em = build_shuffled_event_map(event_map, shuffled_phases, line_packets)

                    null_app = create_strength_gated_apparatus(
                        folio, profile, f_params, per_line_class,
                        config['table'], config['burden_threshold'],
                        per_line_strength)

                    null_result = run_strength_gated_event_trace(
                        null_app, toks, shuffled_lp, cts_data, shuffled_em)
                    null_result.pop('line_states', None)
                    null_events = null_result['per_event_detail']
                    null_selected = select_events(null_events)
                    perm_dyes.append(compute_event_dye(null_selected))
                    run_count += 1

            gated_m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0
            gated_advantage = gated_m1_dye - gated_m4f_dye

            # --- Strength-band stratification (Phase 577 per-line bands) ---
            by_band = {'STRONG': [], 'MED': [], 'WEAK': []}
            by_class_strength = defaultdict(list)
            n_sz = 0

            for ev in selected_m1:
                lk = ev.get('line_key', '')
                strength_info = per_line_strength.get(lk, {})
                band = strength_info.get('strength_band', 'MED')
                cls_info = per_line_class.get(lk, {})
                cls = cls_info.get('class', 'AUTH_AMBIGUOUS')
                dye_val = ev.get('y_gain_event', 0) / max(ev.get('dv_magnitude_sum', 0.001), 0.001)

                by_band[band].append(dye_val)
                by_class_strength[f"{cls}+{band}"].append(dye_val)

                if (cls, band) in structural_zero_cells:
                    n_sz += 1

            config_sz_total += n_sz

            band_results = {}
            for band_name, dyes in by_band.items():
                band_results[band_name] = {
                    'n_events': len(dyes),
                    'gated_mean_dye': round(sum(dyes) / len(dyes), 6) if dyes else 0.0,
                }

            class_strength_results = {}
            for cell, dyes in by_class_strength.items():
                class_strength_results[cell] = {
                    'n_events': len(dyes),
                    'mean_dye': round(sum(dyes) / len(dyes), 6) if dyes else 0.0,
                }

            # --- Per-signature DYE ---
            by_sig = defaultdict(list)
            for ev in selected_m1:
                lk = ev.get('line_key', '')
                cls_info = per_line_class.get(lk, {})
                sig = cls_info.get('signature', 'unknown')
                dye_val = ev.get('y_gain_event', 0) / max(ev.get('dv_magnitude_sum', 0.001), 0.001)
                by_sig[sig].append(dye_val)

            sig_results = {}
            for sig, dyes in by_sig.items():
                sig_results[sig] = {
                    'n_events': len(dyes),
                    'mean_dye': round(sum(dyes) / len(dyes), 6) if dyes else 0.0,
                }

            bm = baseline[folio]
            per_folio_results[folio] = {
                'profile': profile,
                'gated_m1_dye': round(gated_m1_dye, 6),
                'gated_m4f_dye': round(gated_m4f_dye, 6),
                'gated_advantage': round(gated_advantage, 6),
                'baseline_m1_dye': round(bm['m1_dye'], 6),
                'baseline_m4f_dye': round(bm['m4f_dye'], 6),
                'baseline_advantage': round(bm['advantage'], 6),
                'delta_advantage': round(gated_advantage - bm['advantage'], 6),
                'by_band': band_results,
                'by_class_strength': class_strength_results,
                'by_signature': sig_results,
                'structural_zero_activations': n_sz,
            }

            if run_count % 100 == 0:
                elapsed = time.time() - t_start
                print(f"  [{run_count}/{total_runs}] runs, {elapsed:.0f}s elapsed...")

        per_config[config_name] = per_folio_results
        admission_stats[config_name] = dict(config_admission)
        sz_activations_per_config[config_name] = config_sz_total

    # ================================================================
    # STEP 4: Profile summaries
    # ================================================================
    print("\n--- Step 4: Profile summaries ---")
    profile_summary = {}

    for config_name, folio_results in per_config.items():
        profile_summary[config_name] = {}
        by_profile = defaultdict(list)
        for folio, r in folio_results.items():
            by_profile[r['profile']].append(r)

        for profile, results in sorted(by_profile.items()):
            n = len(results)
            mean_gated_adv = sum(r['gated_advantage'] for r in results) / n
            mean_baseline_adv = sum(r['baseline_advantage'] for r in results) / n
            mean_delta = sum(r['delta_advantage'] for r in results) / n

            baseline_m4f = sum(r['baseline_m4f_dye'] for r in results) / n
            gated_m4f = sum(r['gated_m4f_dye'] for r in results) / n
            ccs1_reduction_pct = 0.0
            if abs(baseline_m4f) > 0.001:
                ccs1_reduction_pct = (baseline_m4f - gated_m4f) / abs(baseline_m4f) * 100

            # Null win tracking
            n_null_wins_baseline = sum(1 for r in results if r['baseline_advantage'] < 0)
            n_null_wins_gated = sum(1 for r in results if r['gated_advantage'] < 0)

            # Band summary
            band_summary = {}
            for band_name in ['STRONG', 'MED', 'WEAK']:
                band_dyes = []
                for r in results:
                    bd = r['by_band'].get(band_name, {})
                    if bd.get('n_events', 0) > 0:
                        band_dyes.append(bd['gated_mean_dye'])
                band_summary[band_name] = {
                    'mean_gated_dye': round(sum(band_dyes) / len(band_dyes), 6) if band_dyes else 0.0,
                    'n_folios': len(band_dyes),
                }

            profile_summary[config_name][profile] = {
                'n_folios': n,
                'mean_gated_advantage': round(mean_gated_adv, 6),
                'mean_baseline_advantage': round(mean_baseline_adv, 6),
                'mean_delta_advantage': round(mean_delta, 6),
                'ccs1_reduction_pct': round(ccs1_reduction_pct, 2),
                'n_null_wins_baseline': n_null_wins_baseline,
                'n_null_wins_gated': n_null_wins_gated,
                'by_band': band_summary,
            }

            print(f"  {config_name} | {profile}: delta_adv={mean_delta:.4f}, "
                  f"CCS1_red={ccs1_reduction_pct:.1f}%, "
                  f"null_wins={n_null_wins_baseline}->{n_null_wins_gated}")

    # ================================================================
    # STEP 5: NO_STRENGTH vs CREDIT_ONLY_4D comparison
    # ================================================================
    print("\n--- Step 5: NO_STRENGTH vs CREDIT_ONLY_4D ---")
    control_comparison = {}
    if 'NO_STRENGTH' in per_config and 'CREDIT_ONLY_4D' in per_config:
        for folio in eligible_folios:
            ns = per_config['NO_STRENGTH'].get(folio, {})
            co = per_config['CREDIT_ONLY_4D'].get(folio, {})
            if ns and co:
                control_comparison[folio] = {
                    'profile': ns['profile'],
                    'no_strength_advantage': ns['gated_advantage'],
                    'credit_only_advantage': co['gated_advantage'],
                    'no_strength_better': ns['gated_advantage'] > co['gated_advantage'],
                }

        a2_compare = [v for v in control_comparison.values() if 'A2' in v['profile']]
        if a2_compare:
            n_ns_better = sum(1 for v in a2_compare if v['no_strength_better'])
            print(f"  A2 folios where NO_STRENGTH > CREDIT_ONLY_4D: {n_ns_better}/{len(a2_compare)}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '577',
            'script': 't2_strength_gated_simulation.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_folios': len(eligible_folios),
            'n_configs': len(gate_configs),
            'n_null_perms': N_NULL_PERMS,
            'total_runs': run_count,
        },
        'per_config': per_config,
        'profile_summary': profile_summary,
        'admission_stats': admission_stats,
        'structural_zero_activations': sz_activations_per_config,
        'no_strength_vs_credit_only': control_comparison,
    }

    out_path = os.path.join(RESULTS_DIR, 't2_strength_gated_simulation.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
