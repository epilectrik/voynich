"""
T2: Full Gated Simulation with Event-Band Stratification
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Runs AuthenticatedRecoveryApparatus across 76 folios under 5 gate
configurations with mandatory STRONG/MEDIUM/WEAK band evaluation.
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

# Local imports
from phases.SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE.scripts.t1_authenticated_apparatus import (
    create_authenticated_apparatus,
    run_authenticated_event_trace,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')
P573_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES', 'results')

N_NULL_PERMS = 5


def classify_event_band(event):
    """Classify event into STRONG/MEDIUM/WEAK by n_strong_signals."""
    ns = event.get('n_strong_signals', 0)
    if ns >= 3:
        return 'STRONG'
    elif ns >= 1:
        return 'MEDIUM'
    return 'WEAK'


def load_all_data():
    """Load all required data for simulation."""
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
    lp_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')
    with open(lp_path) as f:
        lp_raw = json.load(f)
    line_packets = lp_raw['line_packets']

    print("  Loading CTS data...")
    cts_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path) as f:
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
    sup_path = os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                            'results', 't2b_supervisory_interface_unrouted.json')
    with open(sup_path) as f:
        sup_raw = json.load(f)
    all_tokens = sup_raw['token_signals']

    print("  Loading event taxonomy...")
    event_path = os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                              'results', 't1_event_taxonomy.json')
    with open(event_path) as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']

    print("  Loading Phase 574 T0 events (for band classification)...")
    t0_574_path = os.path.join(phases_dir,
        'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP', 'results',
        't0_event_feature_assembly.json')
    with open(t0_574_path) as f:
        t0_574 = json.load(f)

    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (t1_setup, t2_runs, t3_nulls,
            line_packets, cts_data, all_tokens, budget_path,
            event_map, regime_path, t0_574)


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T2: Full Gated Simulation with Event-Band Stratification")
    print("Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")
    (t1_setup, t2_runs, t3_nulls,
     line_packets, cts_data, all_tokens, budget_path,
     event_map, regime_path, t0_574) = load_all_data()

    eligible_folios = t1_setup['eligible_folios']
    all_folios = t1_setup['all_folios']
    folio_configs = t1_setup['folio_configs']
    primary_runs = t2_runs['primary_runs']
    m0_line_states = t2_runs['m0_line_states']
    null_data = t3_nulls['m4f_demand_matched']

    print(f"  Eligible folios: {len(eligible_folios)}")

    # ---- Load Phase 575 T0 ACS data ----
    print("\n--- Loading T0 ACS data ---")
    t0_path = os.path.join(RESULTS_DIR, 't0_acs_assembly.json')
    with open(t0_path) as f:
        t0_acs = json.load(f)

    acs_lookup = t0_acs['per_line_acs']
    empirical_thresholds = t0_acs['empirical_thresholds']

    # Build event-level band lookup from Phase 574 T0
    # {(folio, line_key): n_strong_signals}
    event_bands = {}
    for ev in t0_574['m1_events']:
        event_bands[ev['line_key']] = ev.get('n_strong_signals', 0)

    # ---- Setup tokens ----
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
            'section': fc['section'],
        }

    for profile in sorted(set(v['profile'] for v in baseline.values())):
        pf = [v for v in baseline.values() if v['profile'] == profile]
        n = len(pf)
        print(f"  {profile} (n={n}): adv={sum(v['advantage'] for v in pf)/n:.4f}")

    # ================================================================
    # STEP 2: Define gate configurations
    # ================================================================
    gate_configs = {}
    for level in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        gate_configs[level] = {
            'thresholds': empirical_thresholds[level],
            'cleanliness_penalty': 10.0,
        }
    # Penalty variants on MODERATE threshold
    gate_configs['MODERATE_LOWPEN'] = {
        'thresholds': empirical_thresholds['MODERATE'],
        'cleanliness_penalty': 5.0,
    }
    gate_configs['MODERATE_HIPEN'] = {
        'thresholds': empirical_thresholds['MODERATE'],
        'cleanliness_penalty': 15.0,
    }

    print(f"\n--- Gate configurations: {len(gate_configs)} ---")
    for name, cfg in gate_configs.items():
        print(f"  {name}: A2_thresh={cfg['thresholds'].get('A2', '?')}, penalty={cfg['cleanliness_penalty']}")

    # ================================================================
    # STEP 3: Run gated simulations
    # ================================================================
    per_config = {}
    total_runs = len(gate_configs) * len(eligible_folios) * (1 + N_NULL_PERMS)
    run_count = 0

    for config_name, config in gate_configs.items():
        print(f"\n--- Config: {config_name} ---")
        per_folio_results = {}

        for folio in eligible_folios:
            fc = folio_configs[folio]
            toks = tokens_by_folio[folio]
            if not toks:
                continue

            profile = fc['profile']
            config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')

            # Determine profile-specific threshold
            if 'A1' in profile:
                thresh = config['thresholds'].get('A1', 0.05)
            elif 'A2' in profile:
                thresh = config['thresholds'].get('A2', 0.35)
            else:
                thresh = config['thresholds'].get('A3', 0.10)

            f_params = {
                'config_mode': config_mode,
                'f1': fc['F1'], 'f2': fc['F2'], 'f3': fc['F3'],
                'f4_raw': fc['F4_raw'], 'f5': fc['F5'],
            }

            # --- M1 gated run ---
            app = create_authenticated_apparatus(
                folio, profile, f_params,
                acs_threshold=thresh,
                cleanliness_penalty=config['cleanliness_penalty'],
                acs_lookup=acs_lookup)

            result = run_authenticated_event_trace(
                app, toks, line_packets, cts_data, event_map)
            result.pop('line_states', None)
            m1_events = result['per_event_detail']
            selected_m1 = select_events(m1_events)
            gated_m1_dye = compute_event_dye(selected_m1)
            run_count += 1

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

                    null_app = create_authenticated_apparatus(
                        folio, profile, f_params,
                        acs_threshold=thresh,
                        cleanliness_penalty=config['cleanliness_penalty'],
                        acs_lookup=acs_lookup)

                    null_result = run_authenticated_event_trace(
                        null_app, toks, shuffled_lp, cts_data, shuffled_em)
                    null_result.pop('line_states', None)
                    null_events = null_result['per_event_detail']
                    null_selected = select_events(null_events)
                    perm_dyes.append(compute_event_dye(null_selected))
                    run_count += 1

            gated_m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0
            gated_advantage = gated_m1_dye - gated_m4f_dye

            # --- Event-band stratification ---
            by_band = {'STRONG': [], 'MEDIUM': [], 'WEAK': []}
            for ev in selected_m1:
                lk = ev.get('line_key', '')
                ns = event_bands.get(lk, 0)
                if ns >= 3:
                    band = 'STRONG'
                elif ns >= 1:
                    band = 'MEDIUM'
                else:
                    band = 'WEAK'
                dye = ev.get('y_gain_event', 0) / max(ev.get('dv_magnitude_sum', 0.001), 0.001)
                by_band[band].append(dye)

            band_results = {}
            bm = baseline[folio]
            for band_name, dyes in by_band.items():
                if dyes:
                    mean_dye = sum(dyes) / len(dyes)
                else:
                    mean_dye = 0.0
                band_results[band_name] = {
                    'n_events': len(dyes),
                    'gated_mean_dye': round(mean_dye, 6),
                }

            per_folio_results[folio] = {
                'profile': profile,
                'gated_m1_dye': round(gated_m1_dye, 6),
                'gated_m4f_dye': round(gated_m4f_dye, 6),
                'gated_advantage': round(gated_advantage, 6),
                'baseline_m1_dye': round(bm['m1_dye'], 6),
                'baseline_m4f_dye': round(bm['m4f_dye'], 6),
                'baseline_advantage': round(bm['advantage'], 6),
                'delta_m1_dye': round(gated_m1_dye - bm['m1_dye'], 6),
                'delta_m4f_dye': round(gated_m4f_dye - bm['m4f_dye'], 6),
                'delta_advantage': round(gated_advantage - bm['advantage'], 6),
                'by_band': band_results,
            }

            if run_count % 50 == 0:
                elapsed = time.time() - t_start
                print(f"  [{run_count}/{total_runs}] runs, {elapsed:.0f}s elapsed...")

        per_config[config_name] = per_folio_results

    # ================================================================
    # STEP 4: Profile summaries with band stratification
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
            mean_delta_m4f = sum(r['delta_m4f_dye'] for r in results) / n

            # CCS1 reduction percentage
            if abs(mean_baseline_adv) > 0.001:
                baseline_m4f = sum(r['baseline_m4f_dye'] for r in results) / n
                gated_m4f = sum(r['gated_m4f_dye'] for r in results) / n
                if abs(baseline_m4f) > 0.001:
                    ccs1_reduction_pct = (baseline_m4f - gated_m4f) / abs(baseline_m4f) * 100
                else:
                    ccs1_reduction_pct = 0.0
            else:
                ccs1_reduction_pct = 0.0

            # Per-band summary
            band_summary = {}
            for band_name in ['STRONG', 'MEDIUM', 'WEAK']:
                band_dyes = []
                for r in results:
                    bd = r['by_band'].get(band_name, {})
                    if bd.get('n_events', 0) > 0:
                        band_dyes.append(bd['gated_mean_dye'])
                band_summary[band_name] = {
                    'mean_gated_dye': round(sum(band_dyes) / len(band_dyes), 6) if band_dyes else 0.0,
                    'n_folios_with_events': len(band_dyes),
                }

            n_improved = sum(1 for r in results if r['delta_advantage'] > 0.001)
            n_degraded = sum(1 for r in results if r['delta_advantage'] < -0.001)

            profile_summary[config_name][profile] = {
                'n_folios': n,
                'mean_gated_advantage': round(mean_gated_adv, 6),
                'mean_baseline_advantage': round(mean_baseline_adv, 6),
                'mean_delta_advantage': round(mean_delta, 6),
                'mean_delta_m4f_dye': round(mean_delta_m4f, 6),
                'ccs1_reduction_pct': round(ccs1_reduction_pct, 2),
                'n_improved': n_improved,
                'n_degraded': n_degraded,
                'by_band': band_summary,
            }

            print(f"  {config_name} | {profile}: delta_adv={mean_delta:.4f}, "
                  f"CCS1_red={ccs1_reduction_pct:.1f}%, imp/deg={n_improved}/{n_degraded}")

    # ================================================================
    # Output
    # ================================================================
    # Serialize gate configs (remove complex thresholds for JSON)
    serializable_configs = {}
    for name, cfg in gate_configs.items():
        serializable_configs[name] = {
            'thresholds': cfg['thresholds'],
            'cleanliness_penalty': cfg['cleanliness_penalty'],
        }

    output = {
        'metadata': {
            'phase': '575',
            'script': 't2_gated_simulation.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_folios': len(eligible_folios),
            'n_configs': len(gate_configs),
            'n_null_perms': N_NULL_PERMS,
            'total_runs': run_count,
        },
        'gate_configs': serializable_configs,
        'per_config': per_config,
        'profile_summary': profile_summary,
    }

    out_path = os.path.join(RESULTS_DIR, 't2_gated_simulation.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
