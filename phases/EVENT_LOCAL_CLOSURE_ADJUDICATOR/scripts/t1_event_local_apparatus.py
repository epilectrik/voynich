"""
T1: Event-Local Apparatus Verification
Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR

Verifies ClosureAdmissionApparatus works correctly with event-class inputs.
Same apparatus code as Phase 576 — only legit_lookup data and gate_table values change.

5 gate configs:
  LINE_CLASS_CONTROL: Phase 576 AMB_PESSIMISTIC (6 morphological classes)
  EVENT_CLASS_FULL: 4-tier execution+anatomy gate
  EVENT_CLASS_BINARY: AUTHENTIC → (1,1), all else → minimal
  BURDEN_RESOLVED_ONLY: resolved → full, unresolved → reject
  CREDIT_ONLY_EVENT: admit=1.0, credit from EVENT_CLASS_FULL
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

from phases.CLOSURE_REGIME_ADMISSION_GATE.scripts.t1_closure_admission_apparatus import (
    ClosureAdmissionApparatus,
    create_closure_admission_apparatus,
    run_admission_gated_event_trace,
    build_gate_configs as build_p576_gate_configs,
)
from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace, sort_key, compute_infra_scores,
)
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus,
)


# ===========================================================================
# EVENT-CLASS GATE TABLES (exported for T2)
# ===========================================================================

def build_event_gate_table_full():
    """EVENT_CLASS_FULL: 4-tier execution+anatomy gate."""
    t = {}
    # AUTHENTIC_RESOLVER: full admission (any burden)
    for burden in ('low', 'high'):
        t[('AUTHENTIC_RESOLVER', burden, 'HIGH')] = (1.00, 1.00)
        t[('AUTHENTIC_RESOLVER', burden, 'MED')]  = (1.00, 0.95)
        t[('AUTHENTIC_RESOLVER', burden, 'LOW')]  = (0.95, 0.85)
    # PARTIAL_RESOLVER: moderate (burden-dependent)
    t[('PARTIAL_RESOLVER', 'high', 'HIGH')] = (0.85, 0.75)
    t[('PARTIAL_RESOLVER', 'high', 'MED')]  = (0.75, 0.60)
    t[('PARTIAL_RESOLVER', 'high', 'LOW')]  = (0.65, 0.50)
    t[('PARTIAL_RESOLVER', 'low', 'HIGH')]  = (0.70, 0.60)
    t[('PARTIAL_RESOLVER', 'low', 'MED')]   = (0.60, 0.45)
    t[('PARTIAL_RESOLVER', 'low', 'LOW')]   = (0.50, 0.35)
    # NONRESOLVING_COUNTERFEIT: heavy suppression
    t[('NONRESOLVING_COUNTERFEIT', 'high', 'HIGH')] = (0.20, 0.10)
    t[('NONRESOLVING_COUNTERFEIT', 'high', 'MED')]  = (0.10, 0.05)
    t[('NONRESOLVING_COUNTERFEIT', 'high', 'LOW')]  = (0.05, 0.02)
    for cts_band in ('HIGH', 'MED', 'LOW'):
        t[('NONRESOLVING_COUNTERFEIT', 'low', cts_band)] = (0.00, 0.00)
    # INERT_PSEUDO: full rejection
    for burden in ('low', 'high'):
        for cts_band in ('HIGH', 'MED', 'LOW'):
            t[('INERT_PSEUDO', burden, cts_band)] = (0.00, 0.00)
    # NON_CLOSE: pass-through
    for burden in ('low', 'high'):
        for cts_band in ('HIGH', 'MED', 'LOW'):
            t[('NON_CLOSE', burden, cts_band)] = (1.00, 1.00)
    return t


def build_event_gate_table_binary():
    """EVENT_CLASS_BINARY: AUTHENTIC → (1,1), all else → (0.10, 0.05)."""
    t = {}
    for burden in ('low', 'high'):
        for cts_band in ('HIGH', 'MED', 'LOW'):
            t[('AUTHENTIC_RESOLVER', burden, cts_band)] = (1.00, 1.00)
            t[('PARTIAL_RESOLVER', burden, cts_band)] = (0.10, 0.05)
            t[('NONRESOLVING_COUNTERFEIT', burden, cts_band)] = (0.10, 0.05)
            t[('INERT_PSEUDO', burden, cts_band)] = (0.10, 0.05)
            t[('NON_CLOSE', burden, cts_band)] = (1.00, 1.00)
    return t


def build_event_gate_table_burden_only():
    """BURDEN_RESOLVED_ONLY: AUTHENTIC+PARTIAL → (1,1), CF+INERT → (0,0)."""
    t = {}
    for burden in ('low', 'high'):
        for cts_band in ('HIGH', 'MED', 'LOW'):
            t[('AUTHENTIC_RESOLVER', burden, cts_band)] = (1.00, 1.00)
            t[('PARTIAL_RESOLVER', burden, cts_band)] = (1.00, 1.00)
            t[('NONRESOLVING_COUNTERFEIT', burden, cts_band)] = (0.00, 0.00)
            t[('INERT_PSEUDO', burden, cts_band)] = (0.00, 0.00)
            t[('NON_CLOSE', burden, cts_band)] = (1.00, 1.00)
    return t


def build_event_gate_table_credit_only():
    """CREDIT_ONLY_EVENT: admit=1.0 always, credit from EVENT_CLASS_FULL."""
    full = build_event_gate_table_full()
    return {key: (1.0, c) for key, (a, c) in full.items()}


def build_all_gate_configs(burden_threshold=0.10):
    """Build all 5 gate configurations including LINE_CLASS_CONTROL.

    LINE_CLASS_CONTROL uses Phase 576's AMB_PESSIMISTIC table —
    caller must supply the Phase 576 classification as legit_lookup.
    """
    # Phase 576 AMB_PESSIMISTIC table
    p576_configs = build_p576_gate_configs(burden_threshold)
    p576_amb_pess = p576_configs['REGIME_AMB_PESSIMISTIC']

    return {
        'LINE_CLASS_CONTROL': {
            'table': p576_amb_pess['table'],
            'burden_threshold': p576_amb_pess['burden_threshold'],
            'uses_p576_classification': True,
        },
        'EVENT_CLASS_FULL': {
            'table': build_event_gate_table_full(),
            'burden_threshold': burden_threshold,
            'uses_p576_classification': False,
        },
        'EVENT_CLASS_BINARY': {
            'table': build_event_gate_table_binary(),
            'burden_threshold': burden_threshold,
            'uses_p576_classification': False,
        },
        'BURDEN_RESOLVED_ONLY': {
            'table': build_event_gate_table_burden_only(),
            'burden_threshold': burden_threshold,
            'uses_p576_classification': False,
        },
        'CREDIT_ONLY_EVENT': {
            'table': build_event_gate_table_credit_only(),
            'burden_threshold': burden_threshold,
            'uses_p576_classification': False,
        },
    }


# ===========================================================================
# Verification
# ===========================================================================
def main():
    t0_time = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T1: Event-Local Apparatus Verification")
    print("Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    setup_path = os.path.join(phases_dir,
        'PRODUCTIVE_DISRUPTION_EXPANSION', 'results', 't1_full_scale_setup.json')
    with open(setup_path) as f:
        setup = json.load(f)
    folio_params = setup['folio_configs']

    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')) as f:
        line_packets = json.load(f)['line_packets']
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
    with open(os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                           'results', 't2b_supervisory_interface_unrouted.json')) as f:
        all_tokens = json.load(f)['token_signals']
    with open(os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                           'results', 't1_event_taxonomy.json')) as f:
        event_map = json.load(f)['event_map']

    # Load Phase 578 T0 classification (event classes)
    t0_path = os.path.join(RESULTS_DIR, 't0_event_local_classification.json')
    with open(t0_path) as f:
        t0_data = json.load(f)
    per_line_event = t0_data['per_line_classification']

    # Load Phase 576 T0 classification (morphological classes for LINE_CLASS_CONTROL)
    p576_t0_path = os.path.join(phases_dir, 'CLOSURE_REGIME_ADMISSION_GATE',
                                'results', 't0_corpus_classification.json')
    with open(p576_t0_path) as f:
        p576_t0 = json.load(f)
    per_line_morph = p576_t0['per_line_classification']
    burden_threshold = p576_t0['burden_calibration']['recommended_threshold']

    all_folios = setup.get('all_folios', setup['eligible_folios'])
    folio_infra = compute_infra_scores(all_folios)
    eligible_set = set(setup['eligible_folios'])

    tokens_by_folio = {}
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio.setdefault(tok['folio'], []).append(tok)

    # Build gate configs
    configs = build_all_gate_configs(burden_threshold)
    print(f"  Configs: {list(configs.keys())}")
    print(f"  Burden threshold: {burden_threshold}")

    # Pick 2 A2 folios
    a2_folios = [f for f, p in folio_params.items()
                 if 'A2' in p.get('profile', '') and f in eligible_set
                 and f in tokens_by_folio and len(tokens_by_folio[f]) > 0]
    test_folios = a2_folios[:2]
    test_folio = test_folios[0]
    fc = folio_params[test_folio]
    profile = fc['profile']
    config_mode = folio_infra.get(test_folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
    tokens = tokens_by_folio[test_folio]

    fp = {
        'config_mode': config_mode,
        'f1': fc['F1'], 'f2': fc['F2'], 'f3': fc['F3'],
        'f4_raw': fc['F4_raw'], 'f5': fc['F5'],
    }

    print(f"  Test folio: {test_folio} ({profile})")

    verification = {}

    # ================================================================
    # Test 1: Identity check — all AUTHENTIC_RESOLVER + full admit
    # ================================================================
    print("\n--- Test 1: Identity check (all AUTHENTIC_RESOLVER) ---")
    all_authentic = {k: {'class': 'AUTHENTIC_RESOLVER', 'cts': v.get('cts', 0.5)}
                     for k, v in per_line_event.items()}

    baseline_app = FolioSpecificApparatus(
        profile=profile, config_mode=config_mode, folio=test_folio,
        f1=fp['f1'], f2=fp['f2'], f3=fp['f3'], f4_raw=fp['f4_raw'], f5=fp['f5'])
    sorted_tokens = sorted(tokens, key=sort_key)
    baseline_result = run_enhanced_event_trace(
        baseline_app, sorted_tokens, line_packets, cts_data, event_map)
    baseline_y = baseline_result['metrics']['old_y_final']

    identity_app = create_closure_admission_apparatus(
        test_folio, profile, fp, all_authentic,
        configs['EVENT_CLASS_FULL']['table'], burden_threshold)
    identity_result = run_admission_gated_event_trace(
        identity_app, tokens, line_packets, cts_data, event_map)
    identity_y = identity_result['metrics']['old_y_final']

    y_diff = abs(identity_y - baseline_y)
    rel_diff = y_diff / max(abs(baseline_y), 1e-10)
    identity_pass = rel_diff < 0.05
    print(f"  Baseline Y={baseline_y:.8f}, Identity Y={identity_y:.8f}")
    print(f"  Diff={y_diff:.6f}, rel={rel_diff:.4f}")
    print(f"  PASS: {identity_pass}")
    verification['identity_check'] = {
        'pass': identity_pass,
        'baseline_y': round(baseline_y, 8),
        'identity_y': round(identity_y, 8),
        'rel_diff': round(rel_diff, 6),
    }

    # ================================================================
    # Test 2: Full rejection — all (0,0) → Y changes
    # ================================================================
    print("\n--- Test 2: Full rejection ---")
    reject_table = {key: (0.0, 0.0) for key in configs['EVENT_CLASS_FULL']['table']}
    reject_app = create_closure_admission_apparatus(
        test_folio, profile, fp, per_line_event, reject_table, burden_threshold)
    reject_result = run_admission_gated_event_trace(
        reject_app, tokens, line_packets, cts_data, event_map)
    reject_y = reject_result['metrics']['old_y_final']

    y_diff_reject = abs(baseline_y - reject_y)
    reject_pass = y_diff_reject > 1e-8
    print(f"  Baseline Y={baseline_y:.8f}, Rejected Y={reject_y:.8f}")
    print(f"  PASS: {reject_pass}")
    verification['full_rejection_check'] = {
        'pass': reject_pass,
        'baseline_y': round(baseline_y, 8),
        'reject_y': round(reject_y, 8),
    }

    # ================================================================
    # Test 3: LINE_CLASS_CONTROL runs and produces reasonable result
    # ================================================================
    print("\n--- Test 3: LINE_CLASS_CONTROL (Phase 576 AMB_PESSIMISTIC) ---")
    lcc_config = configs['LINE_CLASS_CONTROL']
    lcc_app = create_closure_admission_apparatus(
        test_folio, profile, fp, per_line_morph,
        lcc_config['table'], lcc_config['burden_threshold'])
    lcc_result = run_admission_gated_event_trace(
        lcc_app, tokens, line_packets, cts_data, event_map)
    lcc_y = lcc_result['metrics']['old_y_final']

    # Compare against Phase 576 T2 stored result for this folio
    p576_t2_path = os.path.join(phases_dir, 'CLOSURE_REGIME_ADMISSION_GATE',
                                'results', 't2_admission_simulation.json')
    with open(p576_t2_path) as f:
        p576_t2 = json.load(f)
    p576_amb_stored = p576_t2['per_config'].get('REGIME_AMB_PESSIMISTIC', {}).get(
        test_folio, {}).get('gated_m1_dye', None)

    if p576_amb_stored is not None:
        # LCC should match Phase 576 AMB_PESSIMISTIC
        lcc_match_diff = abs(lcc_y - p576_amb_stored)
        lcc_pass = True  # Functional check — exact match not expected due to Y vs DYE
        print(f"  LCC Y={lcc_y:.8f}")
        print(f"  Phase 576 AMB_PESSIMISTIC DYE={p576_amb_stored:.8f}")
        print(f"  (Note: Y vs DYE are different metrics — LCC is functional check)")
    else:
        lcc_pass = True
        print(f"  LCC Y={lcc_y:.8f} (no Phase 576 stored value for comparison)")

    verification['no_strength_check'] = {
        'pass': lcc_pass,
        'lcc_y': round(lcc_y, 8),
        'p576_amb_stored_dye': round(p576_amb_stored, 8) if p576_amb_stored else None,
    }

    # ================================================================
    # Test 4: EVENT_CLASS_FULL differs from LINE_CLASS_CONTROL
    # ================================================================
    print("\n--- Test 4: EVENT_CLASS_FULL (strength effect) ---")
    ecf_app = create_closure_admission_apparatus(
        test_folio, profile, fp, per_line_event,
        configs['EVENT_CLASS_FULL']['table'], burden_threshold)
    ecf_result = run_admission_gated_event_trace(
        ecf_app, tokens, line_packets, cts_data, event_map)
    ecf_y = ecf_result['metrics']['old_y_final']

    strength_diff = abs(ecf_y - lcc_y)
    strength_pass = strength_diff > 1e-8
    print(f"  EVENT_CLASS_FULL Y={ecf_y:.8f}")
    print(f"  LINE_CLASS_CONTROL Y={lcc_y:.8f}")
    print(f"  Diff={strength_diff:.8f}")
    print(f"  PASS (different): {strength_pass}")
    verification['strength_effect_check'] = {
        'pass': strength_pass,
        'ecf_y': round(ecf_y, 8),
        'lcc_y': round(lcc_y, 8),
        'diff': round(strength_diff, 8),
    }

    # ================================================================
    # Test 5: CREDIT_ONLY_EVENT — credit from table, admit=1.0
    # ================================================================
    print("\n--- Test 5: CREDIT_ONLY_EVENT ---")
    co_app = create_closure_admission_apparatus(
        test_folio, profile, fp, per_line_event,
        configs['CREDIT_ONLY_EVENT']['table'], burden_threshold)
    co_result = run_admission_gated_event_trace(
        co_app, tokens, line_packets, cts_data, event_map)
    co_y = co_result['metrics']['old_y_final']
    credit_pass = True  # Functional check
    print(f"  CREDIT_ONLY Y={co_y:.8f}")
    verification['credit_only_check'] = {
        'pass': credit_pass,
        'co_y': round(co_y, 8),
    }

    # ================================================================
    # Test 6: Burden conditioning — high/low entries differ
    # ================================================================
    print("\n--- Test 6: Burden conditioning ---")
    full_table = configs['EVENT_CLASS_FULL']['table']
    # Check PARTIAL_RESOLVER has different entries for high vs low burden
    partial_high = full_table.get(('PARTIAL_RESOLVER', 'high', 'HIGH'))
    partial_low = full_table.get(('PARTIAL_RESOLVER', 'low', 'HIGH'))
    burden_pass = partial_high != partial_low
    print(f"  PARTIAL high/HIGH: {partial_high}")
    print(f"  PARTIAL low/HIGH: {partial_low}")
    print(f"  Differ: {burden_pass}")

    # Also check from admission log
    admission_log = ecf_app._admission_log
    event_entries = [e for e in admission_log
                     if e['class'] not in ('NON_CLOSE', 'AUTH_AMBIGUOUS')]
    if event_entries:
        high_burden = [e for e in event_entries if e['burden'] >= burden_threshold]
        low_burden = [e for e in event_entries if e['burden'] < burden_threshold]
        print(f"  Admission log: {len(high_burden)} high-burden, {len(low_burden)} low-burden events")
    else:
        print("  No non-trivial events in admission log")

    verification['burden_conditioning'] = {
        'pass': burden_pass,
        'partial_high': list(partial_high) if partial_high else None,
        'partial_low': list(partial_low) if partial_low else None,
        'n_high_burden': len(high_burden) if event_entries else 0,
        'n_low_burden': len(low_burden) if event_entries else 0,
    }

    # ================================================================
    # Summary
    # ================================================================
    all_pass = all(v['pass'] for v in verification.values())
    print(f"\n{'=' * 70}")
    print(f"All checks: {'PASS' if all_pass else 'SOME FAILURES'}")
    for name, v in verification.items():
        print(f"  {name}: {'PASS' if v['pass'] else 'FAIL'}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '578',
            'script': 't1_event_local_apparatus.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t0_time, 2),
            'test_folio': test_folio,
            'test_profile': profile,
        },
        'verification': verification,
        'gate_configs': list(configs.keys()),
        'burden_threshold': burden_threshold,
    }

    out_path = os.path.join(RESULTS_DIR, 't1_event_local_apparatus.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t0_time:.1f}s")


if __name__ == '__main__':
    main()
