"""
T2: Full Model Executor — 4 Models x 4 Folios
Phase 570b - DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR

Runs 4 comparison models across 4 selected pilot folios (16 total runs)
Models:
  M0  Generic baseline (current config, no F1-F5)
  M1  Folio-specific (F1-F5 applied via FolioSpecificApparatus)
  M2a Generic B10 (no close recovery)
  M2b Folio-specific B10 (F1-F5 applied, close recovery disabled)

All models use run_enhanced_event_trace() which automatically collects:
  - close_pre_state: state BEFORE first CLOSE token update
  - CLOSE-phase dV accumulator: line_close_dv_sum, line_close_token_count
  - Enhanced per_event_detail with full state vectors
  - line_states always collected (no flag needed)
"""

import json
import sys
import os
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
# Imports from T1 enhanced event trace (canonical source for 570b)
# ---------------------------------------------------------------------------
from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace,
    FolioSpecificApparatus,
    SELECTED_FOLIOS,
    sort_key,
    _aggregate_successes,
    assign_folio_profiles, compute_infra_scores,
    build_configured_apparatus, build_no_close_recovery_apparatus,
    PILOT_FOLIOS as ALL_PILOT_FOLIOS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_NAMES = ['M0', 'M1', 'M2a', 'M2b']

# ---------------------------------------------------------------------------
# Data loading (copied from 570a T3 load_data)
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
    section_thresholds = event_taxonomy['section_thresholds']
    print(f"    Event map entries: {len(event_map)}")

    print("  Loading T1 pilot selection (F1-F5 values)...")
    pilot_path = os.path.join(phases_dir, 'FOLIO_SPECIFIC_APPARATUS_PILOT',
                              'results', 't1_pilot_selection.json')
    with open(pilot_path, 'r', encoding='utf-8') as f:
        pilot_selection = json.load(f)
    folio_params = pilot_selection['folio_parameters']
    print(f"    Folio parameters: {len(folio_params)}")

    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (line_packets, cts_data, all_tokens, budgets, budget_path,
            event_map, section_thresholds, folio_params, regime_path)


# ---------------------------------------------------------------------------
# Apparatus builders for the 4 models
# ---------------------------------------------------------------------------
def build_m0_apparatus(profile, config_mode):
    """M0: Generic baseline (current config, no F1-F5)."""
    return build_configured_apparatus(profile, config_mode)


def build_m1_apparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5):
    """M1: Folio-specific (F1-F5 applied)."""
    return FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5)


def build_m2a_apparatus(profile, config_mode):
    """M2a: Generic B10 (no close recovery)."""
    return build_no_close_recovery_apparatus(profile, config_mode)


def build_m2b_apparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5):
    """M2b: Folio-specific B10 (F1-F5 applied, close recovery disabled)."""
    app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4_raw, f5)
    app.enable_close_recovery = False
    return app


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T2: Full Model Executor - 4 Models x 4 Folios")
    print("Phase 570b - DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data sources ---")
    (line_packets, cts_data, all_tokens, budgets, budget_path,
     event_map, section_thresholds, folio_params, regime_path) = load_data()

    # ---- Assign folio profiles and config modes ----
    print("\n--- Resolving folio profiles and config modes ---")
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(ALL_PILOT_FOLIOS)

    # Build profile/config map for selected folios
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
        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"F1={f_vals['f1']:.4f} F2={f_vals['f2']:.4f} "
              f"F3={f_vals['f3']:.4f} F4={f_vals['f4_raw']:.4f} "
              f"F5={f_vals['f5']:.4f}")

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

    # ================================================================
    # PRIMARY RUNS (16): 4 folios x 4 models
    # ================================================================
    print("\n--- Primary Runs (16) ---")
    primary_results = {}
    m0_line_states = {}
    run_count = 0

    for folio in SELECTED_FOLIOS:
        toks = tokens_by_folio[folio]
        if not toks:
            print(f"  SKIP {folio}: no tokens")
            continue

        fc = folio_config[folio]
        profile = fc['profile']
        config_mode = fc['config_mode']
        f1, f2, f3, f4_raw, f5 = (
            fc['f1'], fc['f2'], fc['f3'], fc['f4_raw'], fc['f5']
        )

        folio_results = {}

        # M0: Generic baseline (enhanced trace collects line_states automatically)
        app_m0 = build_m0_apparatus(profile, config_mode)
        result_m0 = run_enhanced_event_trace(app_m0, toks, line_packets, cts_data,
                                    event_map)
        m0_line_states[folio] = result_m0.pop('line_states', [])
        folio_results['M0'] = result_m0
        run_count += 1
        m = result_m0['metrics']
        n_ev = len(result_m0['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M0:  PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M1: Folio-specific
        app_m1 = build_m1_apparatus(profile, config_mode, folio,
                                    f1, f2, f3, f4_raw, f5)
        result_m1 = run_enhanced_event_trace(app_m1, toks, line_packets, cts_data, event_map)
        result_m1.pop('line_states', None)
        folio_results['M1'] = result_m1
        run_count += 1
        m = result_m1['metrics']
        n_ev = len(result_m1['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M1:  PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M2a: Generic B10
        app_m2a = build_m2a_apparatus(profile, config_mode)
        result_m2a = run_enhanced_event_trace(app_m2a, toks, line_packets, cts_data, event_map)
        result_m2a.pop('line_states', None)
        folio_results['M2a'] = result_m2a
        run_count += 1
        m = result_m2a['metrics']
        n_ev = len(result_m2a['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M2a: PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        # M2b: Folio-specific B10
        app_m2b = build_m2b_apparatus(profile, config_mode, folio,
                                      f1, f2, f3, f4_raw, f5)
        result_m2b = run_enhanced_event_trace(app_m2b, toks, line_packets, cts_data, event_map)
        result_m2b.pop('line_states', None)
        folio_results['M2b'] = result_m2b
        run_count += 1
        m = result_m2b['metrics']
        n_ev = len(result_m2b['per_event_detail'])
        print(f"  [{run_count:2d}/16] {folio} M2b: PCV={m['PCV']:.4f} WCU={m['WCU']:.4f} "
              f"UEB={m['UEB']:6.1f} CCY={m['CCY']:.4f} Yf={m['old_y_final']:.4f} "
              f"events={n_ev}")

        primary_results[folio] = folio_results

    t_primary = time.time()
    print(f"\n  Primary runs completed: {run_count} in {t_primary - t0:.1f}s")

    # ================================================================
    # Build output
    # ================================================================
    print("\n--- Writing output ---")

    output = {
        'metadata': {
            'phase': '570b',
            'script': 't2_full_model_executor.py',
            'total_runs': run_count,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'selected_folios': SELECTED_FOLIOS,
            'models': MODEL_NAMES,
        },
        'primary_runs': primary_results,
        'm0_line_states': m0_line_states,
    }

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 't2_full_model_runs.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = os.path.getsize(out_path)
    print(f"  Output: {out_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # ================================================================
    # Final comparison table
    # ================================================================
    t_final = time.time()
    print(f"\n{'=' * 70}")
    print("COMPARISON: M0 (generic) vs M1 (folio-specific)")
    print(f"{'=' * 70}")

    key_metrics = ['PCV', 'WCU', 'SAHB', 'UEB', 'CCY', 'QGY', 'WCP', 'EWP',
                   'REF_mean', 'SLR_mean', 'old_viability', 'old_y_final']

    print(f"\n  {'Folio':<8s} {'Metric':<16s} {'M0':>10s} {'M1':>10s} {'M2a':>10s} "
          f"{'M2b':>10s} {'M1-M0':>10s}")
    print(f"  {'-'*8} {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for folio in SELECTED_FOLIOS:
        if folio not in primary_results:
            continue
        fr = primary_results[folio]
        for mk in key_metrics:
            m0_val = fr['M0']['metrics'].get(mk, 0.0)
            m1_val = fr['M1']['metrics'].get(mk, 0.0)
            m2a_val = fr['M2a']['metrics'].get(mk, 0.0)
            m2b_val = fr['M2b']['metrics'].get(mk, 0.0)
            delta = m1_val - m0_val
            print(f"  {folio:<8s} {mk:<16s} {m0_val:10.4f} {m1_val:10.4f} "
                  f"{m2a_val:10.4f} {m2b_val:10.4f} {delta:+10.4f}")
        print()

    # ---- Event summary ----
    print(f"\n{'=' * 70}")
    print("EVENT SUMMARY: Per-folio event counts and EIR by model")
    print(f"{'=' * 70}")

    print(f"\n  {'Folio':<8s} {'Model':<6s} {'events':>7s} {'EIR':>7s} {'mean_ERM':>10s} "
          f"{'mean_ESQ':>10s} {'demanded':>8s}")
    for folio in SELECTED_FOLIOS:
        if folio not in primary_results:
            continue
        for model in MODEL_NAMES:
            fr = primary_results[folio][model]
            n_ev = len(fr['per_event_detail'])
            ebt = fr['events_by_type']
            e_any = ebt.get('E_any', {})
            eir = e_any.get('EIR', 0.0)
            erm = e_any.get('mean_ERM', 0.0)
            esq = e_any.get('mean_ESQ', 0.0)

            ebd = fr['events_by_demand']
            n_demanded = ebd.get('demanded', {}).get('count', 0)

            print(f"  {folio:<8s} {model:<6s} {n_ev:7d} {eir:7.4f} {erm:10.4f} "
                  f"{esq:10.4f} {n_demanded:8d}")
        print()

    # ---- M0 line states summary ----
    print(f"\n{'=' * 70}")
    print("M0 LINE STATES (for demand matching)")
    print(f"{'=' * 70}")
    for folio in SELECTED_FOLIOS:
        lines = m0_line_states.get(folio, [])
        n_close = sum(1 for ls in lines if ls['packet_phase'] == 'CLOSE')
        n_work = sum(1 for ls in lines if ls['packet_phase'] == 'WORK')
        print(f"  {folio}: {len(lines)} lines total, {n_work} WORK, {n_close} CLOSE")


    # ---- Enhanced state vector summary ----
    print(f"\n{'=' * 70}")
    print("ENHANCED STATE VECTORS: Per-event detail sample")
    print(f"{'=' * 70}")
    for folio in SELECTED_FOLIOS:
        if folio not in primary_results:
            continue
        details = primary_results[folio]['M0']['per_event_detail']
        if details:
            d = details[0]
            has_pre = 'close_pre_state' in d
            has_dv = 'dv_magnitude_sum' in d
            has_yg = 'y_gain_event' in d
            print(f"  {folio} M0: {len(details)} events, "
                  f"has_close_pre_state={has_pre}, "
                  f"has_dv_magnitude_sum={has_dv}, "
                  f"has_y_gain_event={has_yg}")
        else:
            print(f"  {folio} M0: 0 events")

    print(f"\n  Total time: {t_final - t0:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
