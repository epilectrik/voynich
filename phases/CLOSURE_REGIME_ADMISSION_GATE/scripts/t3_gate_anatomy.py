"""
T3: Signature Battery + Regime Admission Analysis + Config Robustness
Phase 576 - CLOSURE_REGIME_ADMISSION_GATE

Per-signature DYE drill-down, SSI, confusion matrix, regime admission vs
credit-only comparison, config robustness, burden conditioning analysis.

Baseline per-signature DYE is computed from Phase 572 M1 event data (ungated),
NOT approximated via uniform offset.
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

from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

# Signature classes from Phase 574 T3
KNOWN_RESISTANT_SIGS = {
    'armed+has_e_head_support+headless_involved',
    'armed+has_e_head_support+headless_involved+high_cts+high_opaque+m_terminal_present',
    'armed+has_e_head_support+headless_involved+high_cts+m_terminal_present',
    'has_e_head_support+headless_involved',
    'has_e_head_support+headless_involved+high_cts+m_terminal_present',
}

KNOWN_CF_SIGS = {
    'armed+has_e_head_support+headless_involved+high_opaque',
    'has_e_head_support',
    'has_e_head_support+headless_involved+high_opaque',
    'has_e_head_support+headless_involved+m_terminal_present',
    'headless_involved',
}


def _classify_sig(sig):
    """Classify a signature string."""
    if sig in KNOWN_RESISTANT_SIGS:
        return 'RESISTANT'
    elif sig in KNOWN_CF_SIGS:
        return 'COUNTERFEITABLE'
    return 'OTHER'


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T3: Signature Battery + Regime Admission Analysis")
    print("Phase 576 - CLOSURE_REGIME_ADMISSION_GATE")
    print("=" * 70)

    # ---- Load data ----
    with open(os.path.join(RESULTS_DIR, 't0_corpus_classification.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_admission_simulation.json')) as f:
        t2 = json.load(f)

    per_line_class = t0['per_line_classification']
    per_config = t2['per_config']
    profile_summary = t2['profile_summary']
    admission_stats = t2['admission_stats']

    # Load Phase 574 T0 for event bands
    p574_t0_path = os.path.join(PROJECT_ROOT,
        'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json')
    with open(p574_t0_path) as f:
        p574_t0 = json.load(f)
    event_bands = {}
    for ev in p574_t0['m1_events']:
        event_bands[ev['line_key']] = ev.get('n_strong_signals', 0)

    # Load Phase 572 setup + M1 runs (for baseline per-signature DYE)
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        setup = json.load(f)
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)
    folio_configs = setup['folio_configs']
    primary_runs = t2_runs['primary_runs']

    configs = list(per_config.keys())
    eligible_folios = setup['eligible_folios']
    print(f"  Configs: {configs}")

    # ================================================================
    # Part 0: Compute baseline (ungated) per-signature DYE from Phase 572
    # ================================================================
    print("\n--- Part 0: Baseline per-signature DYE from Phase 572 ---")
    baseline_sig_dyes = defaultdict(list)   # sig -> [dye values]
    baseline_band_dyes = defaultdict(list)  # band -> [dye values]

    for folio in eligible_folios:
        if folio not in primary_runs:
            continue
        m1_events = primary_runs[folio]['M1'].get('per_event_detail', [])
        selected = select_events(m1_events)
        for ev in selected:
            lk = ev.get('line_key', '')
            cls_info = per_line_class.get(lk, {})
            sig = cls_info.get('signature', 'unknown')
            dv_sum = max(ev.get('dv_magnitude_sum', 0.001), 0.001)
            dye_val = ev.get('y_gain_event', 0) / dv_sum

            baseline_sig_dyes[sig].append(dye_val)

            # Band classification
            ns = event_bands.get(lk, 0)
            if ns >= 3:
                band = 'STRONG'
            elif ns >= 1:
                band = 'MEDIUM'
            else:
                band = 'WEAK'
            baseline_band_dyes[band].append(dye_val)

    # Compute means
    baseline_sig_means = {}
    for sig, dyes in baseline_sig_dyes.items():
        baseline_sig_means[sig] = sum(dyes) / len(dyes) if dyes else 0.0

    baseline_band_means = {}
    for band, dyes in baseline_band_dyes.items():
        baseline_band_means[band] = sum(dyes) / len(dyes) if dyes else 0.0

    print(f"  Baseline signatures: {len(baseline_sig_means)}")
    print(f"  Baseline STRONG DYE: {baseline_band_means.get('STRONG', 0):.6f}")
    print(f"  Baseline WEAK DYE: {baseline_band_means.get('WEAK', 0):.6f}")

    # ================================================================
    # Part 1: Per-signature battery (all configs) — using true baseline
    # ================================================================
    print("\n--- Part 1: Per-signature battery ---")
    per_signature = {}

    for config_name in configs:
        folio_results = per_config[config_name]
        sig_gated_dyes = defaultdict(list)  # sig -> [gated DYE values across folios]

        for folio, r in folio_results.items():
            bsig = r.get('by_signature', {})
            for sig, data in bsig.items():
                if data['n_events'] > 0:
                    sig_gated_dyes[sig].append(data['mean_dye'])

        per_signature[config_name] = {}
        for sig, gated_dyes in sorted(sig_gated_dyes.items()):
            n = len(gated_dyes)
            mean_gated = sum(gated_dyes) / n if n > 0 else 0
            mean_baseline = baseline_sig_means.get(sig, mean_gated)
            delta = mean_gated - mean_baseline
            sig_class = _classify_sig(sig)

            # Correctly handled?
            if sig_class == 'RESISTANT':
                correct = delta > -0.005  # preserved
            elif sig_class == 'COUNTERFEITABLE':
                correct = delta < -0.005  # suppressed
            else:
                correct = None

            per_signature[config_name][sig] = {
                'n_folios': n,
                'mean_gated_dye': round(mean_gated, 6),
                'mean_baseline_dye': round(mean_baseline, 6),
                'delta': round(delta, 6),
                'class': sig_class,
                'correctly_handled': correct,
            }

    # ================================================================
    # Part 2: Confusion matrix per config
    # ================================================================
    print("\n--- Part 2: Confusion matrix ---")
    confusion_matrix = {}

    for config_name in configs:
        sigs = per_signature[config_name]
        tp = sum(1 for s in sigs.values() if s['class'] == 'COUNTERFEITABLE' and s['correctly_handled'] is True)
        tn = sum(1 for s in sigs.values() if s['class'] == 'RESISTANT' and s['correctly_handled'] is True)
        fp = sum(1 for s in sigs.values() if s['class'] == 'RESISTANT' and s['correctly_handled'] is False)
        fn = sum(1 for s in sigs.values() if s['class'] == 'COUNTERFEITABLE' and s['correctly_handled'] is False)
        n_cf = sum(1 for s in sigs.values() if s['class'] == 'COUNTERFEITABLE')
        n_res = sum(1 for s in sigs.values() if s['class'] == 'RESISTANT')

        confusion_matrix[config_name] = {
            'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
            'n_counterfeitable': n_cf, 'n_resistant': n_res,
        }
        print(f"  {config_name}: TP={tp}/{n_cf}, TN={tn}/{n_res}, FP={fp}, FN={fn}")

    # ================================================================
    # Part 3: SSI per config — using true baseline band DYE
    # ================================================================
    print("\n--- Part 3: SSI (Surgical Selectivity Index) ---")
    ssi_results = {}

    for config_name in configs:
        ps = profile_summary[config_name]
        a2 = ps.get('A2_SEALED_RECIRCULATION', {})

        baseline_null_wins = a2.get('n_null_wins_baseline', 0)
        gated_null_wins = a2.get('n_null_wins_gated', 0)
        fi_reduction = max(0, baseline_null_wins - gated_null_wins)

        # Strong-band preservation: compare baseline strong DYE vs gated strong DYE
        a2_band = a2.get('by_band', {})
        gated_strong_dye = a2_band.get('STRONG', {}).get('mean_gated_dye', 0)
        baseline_strong_dye = baseline_band_means.get('STRONG', 0)
        strong_loss = max(0, baseline_strong_dye - gated_strong_dye)

        ssi = fi_reduction / max(strong_loss, 0.001)

        ssi_results[config_name] = {
            'SSI': round(ssi, 4),
            'fi_reduction': fi_reduction,
            'strong_loss': round(strong_loss, 6),
            'baseline_null_wins': baseline_null_wins,
            'gated_null_wins': gated_null_wins,
            'baseline_strong_dye': round(baseline_strong_dye, 6),
            'gated_strong_dye': round(gated_strong_dye, 6),
        }
        print(f"  {config_name}: SSI={ssi:.4f}, FI_red={fi_reduction}, "
              f"strong_loss={strong_loss:.6f} (baseline={baseline_strong_dye:.6f}, gated={gated_strong_dye:.6f})")

    # ================================================================
    # Part 4: Regime admission effect (REGIME_GATED vs CREDIT_ONLY)
    # ================================================================
    print("\n--- Part 4: Regime vs Credit-only ---")
    regime_vs_credit = {}
    if 'REGIME_GATED' in per_config and 'CREDIT_ONLY' in per_config:
        rg_sigs = per_signature.get('REGIME_GATED', {})
        co_sigs = per_signature.get('CREDIT_ONLY', {})

        for sig in set(list(rg_sigs.keys()) + list(co_sigs.keys())):
            rg = rg_sigs.get(sig, {})
            co = co_sigs.get(sig, {})
            regime_vs_credit[sig] = {
                'regime_gated_dye': rg.get('mean_gated_dye', 0),
                'credit_only_dye': co.get('mean_gated_dye', 0),
                'regime_delta': rg.get('delta', 0),
                'credit_delta': co.get('delta', 0),
                'admit_effect': round(rg.get('delta', 0) - co.get('delta', 0), 6),
                'class': rg.get('class', co.get('class', 'OTHER')),
            }

        rg_ssi = ssi_results.get('REGIME_GATED', {}).get('SSI', 0)
        co_ssi = ssi_results.get('CREDIT_ONLY', {}).get('SSI', 0)

        # Also compare by A2 delta_advantage (more direct metric)
        rg_a2_delta = profile_summary.get('REGIME_GATED', {}).get(
            'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
        co_a2_delta = profile_summary.get('CREDIT_ONLY', {}).get(
            'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
        regime_a2_better = rg_a2_delta > co_a2_delta

        print(f"  REGIME_GATED SSI={rg_ssi:.4f}, CREDIT_ONLY SSI={co_ssi:.4f}")
        print(f"  REGIME_GATED A2 delta_adv={rg_a2_delta:.4f}, CREDIT_ONLY={co_a2_delta:.4f}")
        print(f"  Regime admission matters (SSI): {rg_ssi > co_ssi}")
        print(f"  Regime admission matters (A2 delta): {regime_a2_better}")

    # ================================================================
    # Part 5: Burden conditioning analysis
    # ================================================================
    print("\n--- Part 5: Burden conditioning ---")
    burden_analysis = {}
    for config_name in configs:
        stats = admission_stats.get(config_name, {})
        burden_analysis[config_name] = {
            'n_rejected': stats.get('rejected', 0),
            'n_partial': stats.get('partial', 0),
            'n_full': stats.get('full', 0),
        }
        print(f"  {config_name}: rejected={stats.get('rejected', 0)}, "
              f"partial={stats.get('partial', 0)}, full={stats.get('full', 0)}")

    # ================================================================
    # Part 6: Config robustness assessment
    # ================================================================
    print("\n--- Part 6: Config robustness ---")
    regime_configs = [c for c in configs if c != 'CREDIT_ONLY']

    n_ssi_above_1 = sum(1 for c in regime_configs if ssi_results.get(c, {}).get('SSI', 0) > 1.0)
    n_tn_ge_4 = sum(1 for c in regime_configs if confusion_matrix.get(c, {}).get('TN', 0) >= 4)

    co_ssi = ssi_results.get('CREDIT_ONLY', {}).get('SSI', 0)
    n_beat_credit_ssi = sum(1 for c in regime_configs
                            if ssi_results.get(c, {}).get('SSI', 0) > co_ssi)

    # Also check by A2 delta_advantage (more discriminating)
    co_a2_delta = profile_summary.get('CREDIT_ONLY', {}).get(
        'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
    n_beat_credit_a2 = sum(1 for c in regime_configs
                           if profile_summary.get(c, {}).get(
                               'A2_SEALED_RECIRCULATION', {}).get(
                               'mean_delta_advantage', 0) > co_a2_delta)

    config_robustness = {
        'n_regime_configs': len(regime_configs),
        'n_ssi_above_1': n_ssi_above_1,
        'n_tn_ge_4_of_5': n_tn_ge_4,
        'n_beat_credit_only_ssi': n_beat_credit_ssi,
        'n_beat_credit_only_a2_delta': n_beat_credit_a2,
        'architecture_robust': n_beat_credit_a2 >= 3,
        'qualitative_holds': n_ssi_above_1 >= 2 and n_tn_ge_4 >= 2,
    }

    print(f"  SSI > 1.0: {n_ssi_above_1}/{len(regime_configs)}")
    print(f"  TN >= 4/5: {n_tn_ge_4}/{len(regime_configs)}")
    print(f"  Beat CREDIT_ONLY (SSI): {n_beat_credit_ssi}/{len(regime_configs)}")
    print(f"  Beat CREDIT_ONLY (A2 delta): {n_beat_credit_a2}/{len(regime_configs)}")
    print(f"  Architecture robust: {config_robustness['architecture_robust']}")

    # ================================================================
    # Part 7: AMB_PESSIMISTIC vs REGIME_GATED
    # ================================================================
    print("\n--- Part 7: AMB_PESSIMISTIC vs REGIME_GATED ---")
    amb_pess_comparison = {}
    if 'REGIME_AMB_PESSIMISTIC' in ssi_results and 'REGIME_GATED' in ssi_results:
        ap_ssi = ssi_results['REGIME_AMB_PESSIMISTIC']['SSI']
        rg_ssi = ssi_results['REGIME_GATED']['SSI']
        ap_a2 = profile_summary.get('REGIME_AMB_PESSIMISTIC', {}).get(
            'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
        rg_a2 = profile_summary.get('REGIME_GATED', {}).get(
            'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
        pessimistic_better = ap_a2 > rg_a2
        amb_pess_comparison = {
            'amb_pessimistic_ssi': ap_ssi,
            'regime_gated_ssi': rg_ssi,
            'amb_pessimistic_a2_delta': round(ap_a2, 6),
            'regime_gated_a2_delta': round(rg_a2, 6),
            'pessimistic_better': pessimistic_better,
            'interpretation': ('Base AUTH_AMBIGUOUS too generous'
                              if pessimistic_better
                              else 'Base AUTH_AMBIGUOUS values adequate'),
        }
        print(f"  AMB_PESSIMISTIC A2 delta={ap_a2:.4f}, REGIME_GATED A2 delta={rg_a2:.4f}")
        print(f"  Pessimistic better: {pessimistic_better}")

    # ================================================================
    # Best config by A2 delta_advantage (more discriminating than SSI)
    # ================================================================
    best_config = max(configs, key=lambda c:
        profile_summary.get(c, {}).get(
            'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', -999))
    best_a2_delta = profile_summary.get(best_config, {}).get(
        'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
    best_ssi = ssi_results.get(best_config, {}).get('SSI', 0)
    print(f"\n  Best config by A2 delta: {best_config} (delta={best_a2_delta:.4f}, SSI={best_ssi:.4f})")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '576',
            'script': 't3_gate_anatomy.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'baseline_sig_means': {k: round(v, 6) for k, v in baseline_sig_means.items()},
        'baseline_band_means': {k: round(v, 6) for k, v in baseline_band_means.items()},
        'per_signature': per_signature,
        'confusion_matrix': confusion_matrix,
        'ssi_results': ssi_results,
        'regime_vs_credit_only': regime_vs_credit,
        'burden_analysis': burden_analysis,
        'config_robustness': config_robustness,
        'amb_pessimistic_comparison': amb_pess_comparison,
        'best_config_by_SSI': best_config,
        'best_SSI': best_ssi,
    }

    out_path = os.path.join(RESULTS_DIR, 't3_gate_anatomy.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
