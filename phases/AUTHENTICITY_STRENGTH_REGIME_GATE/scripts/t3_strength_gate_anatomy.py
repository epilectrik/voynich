"""
T3: Strength Gate Anatomy — Strong-Band Rescue Analysis
Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE

The decisive test: does STRONG rescue preserve strong-band DYE without
weak-band relapse?

Per-signature battery, SSI, confusion matrix, strong-band preservation,
weak-band guardrail (hard), per-class rescue breakdown (expert Mod 3),
structural-zero activation tracking (expert Mod 4).
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
P576_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'CLOSURE_REGIME_ADMISSION_GATE', 'results')

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

RESCUE_CLASSES = ['AUTH_PROTECTIVE', 'AUTH_THRESHOLD', 'AUTH_AMBIGUOUS']


def _classify_sig(sig):
    if sig in KNOWN_RESISTANT_SIGS:
        return 'RESISTANT'
    elif sig in KNOWN_CF_SIGS:
        return 'COUNTERFEITABLE'
    return 'OTHER'


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T3: Strength Gate Anatomy — Strong-Band Rescue")
    print("Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")

    with open(os.path.join(RESULTS_DIR, 't0_authenticity_strength_assembly.json')) as f:
        t0 = json.load(f)
    per_line_strength = t0['per_line_strength']

    with open(os.path.join(P576_RESULTS, 't0_corpus_classification.json')) as f:
        p576_t0 = json.load(f)
    per_line_class = p576_t0['per_line_classification']

    with open(os.path.join(RESULTS_DIR, 't2_strength_gated_simulation.json')) as f:
        t2 = json.load(f)
    per_config = t2['per_config']
    profile_summary = t2['profile_summary']
    admission_stats = t2['admission_stats']
    t2_sz = t2.get('structural_zero_activations', {})

    # Phase 572 M1 runs (for baseline per-signature/band DYE)
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        setup = json.load(f)
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)
    primary_runs = t2_runs['primary_runs']
    eligible_folios = setup['eligible_folios']

    # Phase 576 T5 synthesis (for comparison)
    with open(os.path.join(P576_RESULTS, 't5_synthesis.json')) as f:
        p576_t5 = json.load(f)
    p576_best_config = p576_t5.get('best_config', '')

    # Phase 576 T2 (for A2 delta comparison)
    with open(os.path.join(P576_RESULTS, 't2_admission_simulation.json')) as f:
        p576_t2 = json.load(f)
    p576_ps = p576_t2.get('profile_summary', {}).get(p576_best_config, {})
    p576_a2_delta = p576_ps.get('A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)

    configs = list(per_config.keys())
    print(f"  Configs: {configs}")
    print(f"  Phase 576 best: {p576_best_config}, A2 delta={p576_a2_delta:.4f}")

    # ================================================================
    # Part 0: Baseline per-signature/band DYE from Phase 572
    # ================================================================
    print("\n--- Part 0: Baseline DYE from Phase 572 ---")
    baseline_sig_dyes = defaultdict(list)
    baseline_band_dyes = defaultdict(list)
    baseline_cs_dyes = defaultdict(list)

    for folio in eligible_folios:
        if folio not in primary_runs:
            continue
        m1_events = primary_runs[folio]['M1'].get('per_event_detail', [])
        selected = select_events(m1_events)
        for ev in selected:
            lk = ev.get('line_key', '')
            cls_info = per_line_class.get(lk, {})
            sig = cls_info.get('signature', 'unknown')
            cls = cls_info.get('class', 'AUTH_AMBIGUOUS')
            dv_sum = max(ev.get('dv_magnitude_sum', 0.001), 0.001)
            dye_val = ev.get('y_gain_event', 0) / dv_sum

            baseline_sig_dyes[sig].append(dye_val)

            strength_info = per_line_strength.get(lk, {})
            s_band = strength_info.get('strength_band', 'MED')
            baseline_band_dyes[s_band].append(dye_val)
            baseline_cs_dyes[f"{cls}+{s_band}"].append(dye_val)

    baseline_sig_means = {s: sum(d)/len(d) for s, d in baseline_sig_dyes.items() if d}
    baseline_band_means = {b: sum(d)/len(d) for b, d in baseline_band_dyes.items() if d}
    baseline_cs_means = {c: sum(d)/len(d) for c, d in baseline_cs_dyes.items() if d}

    print(f"  Baseline STRONG DYE: {baseline_band_means.get('STRONG', 0):.6f}")
    print(f"  Baseline MED DYE: {baseline_band_means.get('MED', 0):.6f}")
    print(f"  Baseline WEAK DYE: {baseline_band_means.get('WEAK', 0):.6f}")

    # ================================================================
    # Part 1: Per-signature battery
    # ================================================================
    print("\n--- Part 1: Per-signature battery ---")
    per_signature = {}

    for config_name in configs:
        folio_results = per_config[config_name]
        sig_gated_dyes = defaultdict(list)

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

            if sig_class == 'RESISTANT':
                correct = delta > -0.005
            elif sig_class == 'COUNTERFEITABLE':
                correct = delta < -0.005
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
    # Part 3: SSI + Strong-band preservation (PRIMARY METRIC)
    # ================================================================
    print("\n--- Part 3: SSI + Strong-band preservation ---")
    ssi_results = {}

    for config_name in configs:
        ps = profile_summary[config_name]
        a2 = ps.get('A2_SEALED_RECIRCULATION', {})

        baseline_null_wins = a2.get('n_null_wins_baseline', 0)
        gated_null_wins = a2.get('n_null_wins_gated', 0)
        fi_reduction = max(0, baseline_null_wins - gated_null_wins)

        a2_band = a2.get('by_band', {})
        gated_strong_dye = a2_band.get('STRONG', {}).get('mean_gated_dye', 0)
        baseline_strong_dye = baseline_band_means.get('STRONG', 0)
        strong_loss = max(0, baseline_strong_dye - gated_strong_dye)

        ssi = fi_reduction / max(strong_loss, 0.001)

        if abs(baseline_strong_dye) > 0.001:
            strong_preserved_pct = (gated_strong_dye / baseline_strong_dye) * 100
        else:
            strong_preserved_pct = 100.0

        ssi_results[config_name] = {
            'SSI': round(ssi, 4),
            'fi_reduction': fi_reduction,
            'strong_loss': round(strong_loss, 6),
            'baseline_null_wins': baseline_null_wins,
            'gated_null_wins': gated_null_wins,
            'baseline_strong_dye': round(baseline_strong_dye, 6),
            'gated_strong_dye': round(gated_strong_dye, 6),
            'strong_preserved_pct': round(strong_preserved_pct, 1),
        }
        print(f"  {config_name}: SSI={ssi:.4f}, strong_preserved={strong_preserved_pct:.1f}%, "
              f"FI_red={fi_reduction}")

    # ================================================================
    # Part 4: Weak-band relapse guardrail (HARD — expert Mod 2)
    # ================================================================
    print("\n--- Part 4: Weak-band relapse guardrail ---")
    weak_guardrail = {}

    ns_a2 = profile_summary.get('NO_STRENGTH', {}).get('A2_SEALED_RECIRCULATION', {})
    ns_null_wins = ns_a2.get('n_null_wins_gated', 0)

    for config_name in configs:
        ps = profile_summary[config_name]
        a2 = ps.get('A2_SEALED_RECIRCULATION', {})
        gated_null_wins = a2.get('n_null_wins_gated', 0)

        # Hard guardrail: null wins must not exceed NO_STRENGTH + 1
        weak_safe = gated_null_wins <= ns_null_wins + 1

        weak_guardrail[config_name] = {
            'gated_null_wins': gated_null_wins,
            'no_strength_null_wins': ns_null_wins,
            'weak_band_safe': weak_safe,
        }
        status = "SAFE" if weak_safe else "VIOLATED"
        print(f"  {config_name}: null_wins={gated_null_wins} (NO_STRENGTH={ns_null_wins}) [{status}]")

    # ================================================================
    # Part 5: Per-class rescue breakdown (expert Mod 3)
    # ================================================================
    print("\n--- Part 5: Per-class rescue breakdown ---")
    per_class_rescue = {}

    for config_name in configs:
        per_class_rescue[config_name] = {}
        folio_results = per_config[config_name]

        for rescue_cls in RESCUE_CLASSES:
            strong_dyes = []
            med_weak_dyes = []
            for folio, r in folio_results.items():
                by_cs = r.get('by_class_strength', {})
                strong_key = f"{rescue_cls}+STRONG"
                if strong_key in by_cs and by_cs[strong_key]['n_events'] > 0:
                    strong_dyes.append(by_cs[strong_key]['mean_dye'])
                for wm_key in [f"{rescue_cls}+MED", f"{rescue_cls}+WEAK"]:
                    if wm_key in by_cs and by_cs[wm_key]['n_events'] > 0:
                        med_weak_dyes.append(by_cs[wm_key]['mean_dye'])

            baseline_strong = baseline_cs_means.get(f"{rescue_cls}+STRONG", 0)
            baseline_med = baseline_cs_means.get(f"{rescue_cls}+MED", 0)

            mean_strong = sum(strong_dyes) / len(strong_dyes) if strong_dyes else 0
            mean_med_weak = sum(med_weak_dyes) / len(med_weak_dyes) if med_weak_dyes else 0

            per_class_rescue[config_name][rescue_cls] = {
                'n_strong_folios': len(strong_dyes),
                'mean_strong_gated_dye': round(mean_strong, 6),
                'baseline_strong_dye': round(baseline_strong, 6),
                'delta_strong': round(mean_strong - baseline_strong, 6),
                'n_med_weak_folios': len(med_weak_dyes),
                'mean_med_weak_gated_dye': round(mean_med_weak, 6),
                'baseline_med_dye': round(baseline_med, 6),
            }

        for cls in RESCUE_CLASSES:
            info = per_class_rescue[config_name][cls]
            print(f"  {config_name} | {cls}: STRONG delta={info['delta_strong']:.6f} "
                  f"(n={info['n_strong_folios']})")

    # ================================================================
    # Part 6: Cross-strength-class DYE
    # ================================================================
    print("\n--- Part 6: Cross-strength-class DYE ---")
    cross_class_strength = {}
    all_classes = ['AUTH_RESISTANT', 'AUTH_COUNTERFEITABLE', 'AUTH_THRESHOLD',
                   'AUTH_PROTECTIVE', 'AUTH_PRONE', 'AUTH_AMBIGUOUS']
    bands = ['STRONG', 'MED', 'WEAK']

    # Build structural zero set from T0
    structural_zero_cells = set()
    for sz in t0.get('structural_zeros', []):
        parts = sz.split('+')
        if len(parts) == 2:
            structural_zero_cells.add((parts[0], parts[1]))

    for config_name in configs:
        cross_class_strength[config_name] = {}
        folio_results = per_config[config_name]

        for cls in all_classes:
            for band in bands:
                cell = f"{cls}+{band}"
                cell_dyes = []
                for folio, r in folio_results.items():
                    by_cs = r.get('by_class_strength', {})
                    if cell in by_cs and by_cs[cell]['n_events'] > 0:
                        cell_dyes.append(by_cs[cell]['mean_dye'])

                if cell_dyes:
                    cross_class_strength[config_name][cell] = {
                        'n_folios': len(cell_dyes),
                        'mean_dye': round(sum(cell_dyes) / len(cell_dyes), 6),
                        'is_structural_zero': (cls, band) in structural_zero_cells,
                    }

    # ================================================================
    # Part 7: Structural-zero activation tracking (expert Mod 4)
    # ================================================================
    print("\n--- Part 7: Structural-zero activations ---")
    sz_report = {}
    for config_name in configs:
        n_sz = t2_sz.get(config_name, 0)
        sz_report[config_name] = {
            'n_activations': n_sz,
            'diagnostic': n_sz > 0,
        }
        status = "DIAGNOSTIC FLAG" if n_sz > 0 else "clean"
        print(f"  {config_name}: {n_sz} structural-zero activations [{status}]")

    # ================================================================
    # Part 8: Config robustness
    # ================================================================
    print("\n--- Part 8: Config robustness ---")
    strength_configs = [c for c in configs if c not in ('NO_STRENGTH', 'CREDIT_ONLY_4D')]

    ns_a2_delta = profile_summary.get('NO_STRENGTH', {}).get(
        'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
    co_a2_delta = profile_summary.get('CREDIT_ONLY_4D', {}).get(
        'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)

    n_beat_no_strength = sum(1 for c in strength_configs
                              if profile_summary.get(c, {}).get(
                                  'A2_SEALED_RECIRCULATION', {}).get(
                                  'mean_delta_advantage', 0) > ns_a2_delta)
    n_beat_credit_only = sum(1 for c in strength_configs
                              if profile_summary.get(c, {}).get(
                                  'A2_SEALED_RECIRCULATION', {}).get(
                                  'mean_delta_advantage', 0) > co_a2_delta)

    n_beat_p576 = sum(1 for c in configs
                      if profile_summary.get(c, {}).get(
                          'A2_SEALED_RECIRCULATION', {}).get(
                          'mean_delta_advantage', 0) > p576_a2_delta)

    config_robustness = {
        'n_strength_configs': len(strength_configs),
        'n_beat_no_strength': n_beat_no_strength,
        'n_beat_credit_only': n_beat_credit_only,
        'n_beat_phase_576': n_beat_p576,
        'p576_best_a2_delta': round(p576_a2_delta, 6),
        'architecture_robust': n_beat_no_strength >= 2 and n_beat_credit_only >= 2,
    }

    print(f"  Beat NO_STRENGTH: {n_beat_no_strength}/{len(strength_configs)}")
    print(f"  Beat CREDIT_ONLY_4D: {n_beat_credit_only}/{len(strength_configs)}")
    print(f"  Beat Phase 576 ({p576_best_config}): {n_beat_p576}/{len(configs)}")
    print(f"  Architecture robust: {config_robustness['architecture_robust']}")

    # ================================================================
    # Best config selection (filtered by weak guardrail)
    # ================================================================
    safe_configs = [c for c in configs if weak_guardrail.get(c, {}).get('weak_band_safe', False)]
    if safe_configs:
        best_config = max(safe_configs, key=lambda c:
            profile_summary.get(c, {}).get(
                'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', -999))
    else:
        best_config = max(configs, key=lambda c:
            profile_summary.get(c, {}).get(
                'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', -999))

    best_a2_delta = profile_summary.get(best_config, {}).get(
        'A2_SEALED_RECIRCULATION', {}).get('mean_delta_advantage', 0)
    best_ssi = ssi_results.get(best_config, {}).get('SSI', 0)
    best_strong_preserved = ssi_results.get(best_config, {}).get('strong_preserved_pct', 0)

    print(f"\n  Best config (safe): {best_config}")
    print(f"    A2 delta: {best_a2_delta:.4f}")
    print(f"    SSI: {best_ssi:.4f}")
    print(f"    Strong preserved: {best_strong_preserved:.1f}%")
    print(f"    vs Phase 576: {best_a2_delta:.4f} vs {p576_a2_delta:.4f}")

    per_config_ssi = {c: round(ssi_results.get(c, {}).get('SSI', 0), 4) for c in configs}

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '577',
            'script': 't3_strength_gate_anatomy.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'baseline_sig_means': {k: round(v, 6) for k, v in baseline_sig_means.items()},
        'baseline_band_means': {k: round(v, 6) for k, v in baseline_band_means.items()},
        'baseline_class_strength_means': {k: round(v, 6) for k, v in baseline_cs_means.items()},
        'per_signature': per_signature,
        'confusion_matrix': confusion_matrix,
        'ssi_results': ssi_results,
        'weak_guardrail': weak_guardrail,
        'per_class_rescue': per_class_rescue,
        'cross_class_strength': cross_class_strength,
        'structural_zero_report': sz_report,
        'config_robustness': config_robustness,
        'best_config_by_a2_delta': best_config,
        'best_a2_delta': round(best_a2_delta, 6),
        'best_SSI': round(best_ssi, 4),
        'best_strong_preserved_pct': round(best_strong_preserved, 1),
        'p576_comparison': {
            'p576_best_config': p576_best_config,
            'p576_a2_delta': round(p576_a2_delta, 6),
            'delta_improvement': round(best_a2_delta - p576_a2_delta, 6),
        },
        'per_config_SSI': per_config_ssi,
    }

    out_path = os.path.join(RESULTS_DIR, 't3_strength_gate_anatomy.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
