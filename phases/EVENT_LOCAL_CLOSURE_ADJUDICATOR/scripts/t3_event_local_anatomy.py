"""
T3: Gate Anatomy + Decisive Test (C1660, C1661)
Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR

The decisive test: does event-class gating outperform line-class gating?

C1660: EVENT_CLASS_FULL A2 delta >= LINE_CLASS_CONTROL A2 delta
       AND strong_preserved_pct >= 80%
       AND null_wins_a2 <= LINE_CLASS_CONTROL null wins

C1661: Burden resolution discriminates DYE advantage
       AUTHENTIC_RESOLVER mean DYE_adv > NONRESOLVING_COUNTERFEIT (direction)
       Effect size (Cohen's d) >= 0.3
       COUNTERFEIT contributes disproportionately to A2 null CCS1
"""

import json
import sys
import os
import time
import math
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
)

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

# Ungated baseline strong-band DYE from Phase 572
BASELINE_STRONG_DYE = 0.190753


def cohens_d(group1, group2):
    """Compute Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    m1 = sum(group1) / n1
    m2 = sum(group2) / n2
    var1 = sum((x - m1) ** 2 for x in group1) / (n1 - 1)
    var2 = sum((x - m2) ** 2 for x in group2) / (n2 - 1)
    pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd < 1e-10:
        return 0.0
    return (m1 - m2) / pooled_sd


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T3: Gate Anatomy + Decisive Test")
    print("Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR")
    print("=" * 70)

    # ---- Load data ----
    with open(os.path.join(RESULTS_DIR, 't0_event_local_classification.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_event_local_simulation.json')) as f:
        t2 = json.load(f)

    per_line_event = t0['per_line_classification']
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

    # Load Phase 572 M1 runs for baseline per-band DYE
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        setup = json.load(f)
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)
    folio_configs = setup['folio_configs']
    primary_runs = t2_runs['primary_runs']
    eligible_folios = setup['eligible_folios']

    configs = list(per_config.keys())
    print(f"  Configs: {configs}")

    # ================================================================
    # Part 0: Baseline per-band DYE from Phase 572 (ungated)
    # ================================================================
    print("\n--- Part 0: Baseline per-band DYE ---")
    baseline_band_dyes = defaultdict(list)

    for folio in eligible_folios:
        if folio not in primary_runs:
            continue
        m1_events = primary_runs[folio]['M1'].get('per_event_detail', [])
        selected = select_events(m1_events)
        for ev in selected:
            lk = ev.get('line_key', '')
            ns = event_bands.get(lk, 0)
            if ns >= 3:
                band = 'STRONG'
            elif ns >= 1:
                band = 'MEDIUM'
            else:
                band = 'WEAK'
            dv_sum = max(ev.get('dv_magnitude_sum', 0.001), 0.001)
            dye_val = ev.get('y_gain_event', 0) / dv_sum
            baseline_band_dyes[band].append(dye_val)

    baseline_band_means = {}
    for band, dyes in baseline_band_dyes.items():
        baseline_band_means[band] = sum(dyes) / len(dyes) if dyes else 0.0

    print(f"  Baseline STRONG DYE: {baseline_band_means.get('STRONG', 0):.6f}")
    print(f"  Baseline MEDIUM DYE: {baseline_band_means.get('MEDIUM', 0):.6f}")
    print(f"  Baseline WEAK DYE: {baseline_band_means.get('WEAK', 0):.6f}")

    # ================================================================
    # Part 1: Per-config comparison table
    # ================================================================
    print("\n--- Part 1: Per-config comparison ---")
    config_comparison = {}

    for config_name in configs:
        ps = profile_summary[config_name]
        a2 = ps.get('A2_SEALED_RECIRCULATION', {})

        a2_delta = a2.get('mean_delta_advantage', 0)
        null_wins_baseline = a2.get('n_null_wins_baseline', 0)
        null_wins_gated = a2.get('n_null_wins_gated', 0)

        # Strong-band preservation
        a2_band = a2.get('by_band', {})
        gated_strong_dye = a2_band.get('STRONG', {}).get('mean_gated_dye', 0)
        baseline_strong = baseline_band_means.get('STRONG', BASELINE_STRONG_DYE)
        strong_preserved_pct = (gated_strong_dye / baseline_strong * 100) if baseline_strong > 0.001 else 100.0
        strong_loss = max(0, baseline_strong - gated_strong_dye)

        # SSI
        fi_reduction = max(0, null_wins_baseline - null_wins_gated)
        ssi = fi_reduction / max(strong_loss, 0.001)

        config_comparison[config_name] = {
            'a2_delta': round(a2_delta, 6),
            'null_wins_baseline': null_wins_baseline,
            'null_wins_gated': null_wins_gated,
            'fi_reduction': fi_reduction,
            'gated_strong_dye': round(gated_strong_dye, 6),
            'baseline_strong_dye': round(baseline_strong, 6),
            'strong_preserved_pct': round(strong_preserved_pct, 1),
            'strong_loss': round(strong_loss, 6),
            'SSI': round(ssi, 4),
        }

        print(f"  {config_name}: A2_delta={a2_delta:.4f}, "
              f"null_wins={null_wins_baseline}->{null_wins_gated}, "
              f"strong_preserved={strong_preserved_pct:.1f}%, "
              f"SSI={ssi:.4f}")

    # ================================================================
    # Part 2: C1660 — Event Legitimacy Gating (decisive)
    # ================================================================
    print("\n--- Part 2: C1660 Decisive Test ---")

    lcc = config_comparison.get('LINE_CLASS_CONTROL', {})
    ecf = config_comparison.get('EVENT_CLASS_FULL', {})

    # Criteria
    ecf_beats_lcc_delta = ecf.get('a2_delta', 0) >= lcc.get('a2_delta', 0)
    ecf_strong_ok = ecf.get('strong_preserved_pct', 0) >= 80.0
    ecf_null_ok = ecf.get('null_wins_gated', 99) <= lcc.get('null_wins_gated', 0)
    lcc_null_ok = ecf.get('null_wins_gated', 99) <= lcc.get('null_wins_gated', 0) + 1  # soft guardrail

    # Best event config
    event_configs = [c for c in configs if c not in ('LINE_CLASS_CONTROL', 'CREDIT_ONLY_EVENT')]
    best_event_config = max(event_configs, key=lambda c: config_comparison[c]['a2_delta'])
    best_event = config_comparison[best_event_config]

    best_beats_lcc = best_event['a2_delta'] >= lcc.get('a2_delta', 0)
    best_strong_ok = best_event['strong_preserved_pct'] >= 80.0

    print(f"  LINE_CLASS_CONTROL: A2_delta={lcc.get('a2_delta', 0):.4f}, "
          f"null_wins={lcc.get('null_wins_gated', 0)}, "
          f"strong%={lcc.get('strong_preserved_pct', 0):.1f}")
    print(f"  EVENT_CLASS_FULL: A2_delta={ecf.get('a2_delta', 0):.4f}, "
          f"null_wins={ecf.get('null_wins_gated', 0)}, "
          f"strong%={ecf.get('strong_preserved_pct', 0):.1f}")
    print(f"  Best event ({best_event_config}): A2_delta={best_event['a2_delta']:.4f}, "
          f"strong%={best_event['strong_preserved_pct']:.1f}")
    print(f"  ECF beats LCC (delta): {ecf_beats_lcc_delta}")
    print(f"  ECF strong >= 80%: {ecf_strong_ok}")
    print(f"  ECF null <= LCC null: {ecf_null_ok}")

    # C1660 verdict
    if ecf_beats_lcc_delta and ecf_strong_ok and ecf_null_ok:
        c1660_verdict = 'EVENT_GATING_VALIDATED'
    elif best_beats_lcc or ecf_beats_lcc_delta:
        c1660_verdict = 'EVENT_GATING_PARTIAL'
    else:
        c1660_verdict = 'EVENT_GATING_REJECTED'

    print(f"  C1660 verdict: {c1660_verdict}")

    # ================================================================
    # Part 3: C1661 — Burden Resolution Discriminator
    # ================================================================
    print("\n--- Part 3: C1661 Burden-DYE Discriminator ---")

    # Gather DYE_adv per event class from T0 data
    auth_dye_advs = []
    cf_dye_advs = []
    partial_dye_advs = []

    for lk, info in per_line_event.items():
        cls = info.get('class', '')
        dye_adv = info.get('DYE_adv_event', 0.0)
        if cls == 'AUTHENTIC_RESOLVER':
            auth_dye_advs.append(dye_adv)
        elif cls == 'NONRESOLVING_COUNTERFEIT':
            cf_dye_advs.append(dye_adv)
        elif cls == 'PARTIAL_RESOLVER':
            partial_dye_advs.append(dye_adv)

    # Direction test: AUTHENTIC mean > COUNTERFEIT mean
    auth_mean = sum(auth_dye_advs) / len(auth_dye_advs) if auth_dye_advs else 0
    cf_mean = sum(cf_dye_advs) / len(cf_dye_advs) if cf_dye_advs else 0
    direction_ok = auth_mean > cf_mean

    # Effect size: Cohen's d between AUTHENTIC and COUNTERFEIT
    d = cohens_d(auth_dye_advs, cf_dye_advs)
    effect_size_ok = abs(d) >= 0.3

    # Attribution: COUNTERFEIT null-win tendency
    # Under LINE_CLASS_CONTROL, check if COUNTERFEIT events have lower null-win rate
    # Use per-event-class data from T2 for LINE_CLASS_CONTROL
    lcc_folio_results = per_config.get('LINE_CLASS_CONTROL', {})
    ecf_folio_results = per_config.get('EVENT_CLASS_FULL', {})

    # A2 folios only
    a2_folios = [f for f in eligible_folios if 'A2' in folio_configs[f]['profile']]

    # Count null wins per event class contribution
    # (simplified: check if COUNTERFEIT events have disproportionate DYE under LCC)
    lcc_by_class_dye = defaultdict(list)
    ecf_by_class_dye = defaultdict(list)
    for folio in a2_folios:
        lcc_r = lcc_folio_results.get(folio, {})
        ecf_r = ecf_folio_results.get(folio, {})
        for cls_name, cls_data in lcc_r.get('by_event_class', {}).items():
            if cls_data.get('n_events', 0) > 0:
                lcc_by_class_dye[cls_name].append(cls_data['mean_dye'])
        for cls_name, cls_data in ecf_r.get('by_event_class', {}).items():
            if cls_data.get('n_events', 0) > 0:
                ecf_by_class_dye[cls_name].append(cls_data['mean_dye'])

    print(f"  AUTHENTIC mean DYE_adv: {auth_mean:.6f} (n={len(auth_dye_advs)})")
    print(f"  COUNTERFEIT mean DYE_adv: {cf_mean:.6f} (n={len(cf_dye_advs)})")
    print(f"  PARTIAL mean DYE_adv: {sum(partial_dye_advs)/max(1,len(partial_dye_advs)):.6f} (n={len(partial_dye_advs)})")
    print(f"  Direction (AUTH > CF): {direction_ok}")
    print(f"  Cohen's d: {d:.4f} (>= 0.3: {effect_size_ok})")

    # A2 per-class gated DYE (shows suppression effect)
    print(f"\n  A2 per-event-class gated DYE (LINE_CLASS_CONTROL):")
    for cls_name in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT']:
        vals = lcc_by_class_dye.get(cls_name, [])
        mean_v = sum(vals) / len(vals) if vals else 0
        print(f"    {cls_name}: {mean_v:.6f} (n_folios={len(vals)})")

    print(f"  A2 per-event-class gated DYE (EVENT_CLASS_FULL):")
    for cls_name in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT']:
        vals = ecf_by_class_dye.get(cls_name, [])
        mean_v = sum(vals) / len(vals) if vals else 0
        print(f"    {cls_name}: {mean_v:.6f} (n_folios={len(vals)})")

    # C1661 verdict
    if direction_ok and effect_size_ok:
        c1661_verdict = 'DISCRIMINATOR_CONFIRMED'
    elif direction_ok:
        c1661_verdict = 'DISCRIMINATOR_WEAK'
    else:
        c1661_verdict = 'DISCRIMINATOR_ABSENT'

    print(f"  C1661 verdict: {c1661_verdict}")

    # ================================================================
    # Part 4: Cross-reference event vs morphological classes
    # ================================================================
    print("\n--- Part 4: Event vs Morphological cross-reference ---")
    cross_ref = t0.get('cross_tabs', {}).get('class_vs_morph', {})
    for key in sorted(cross_ref.keys()):
        if cross_ref[key] > 0:
            print(f"  {key}: {cross_ref[key]}")

    # ================================================================
    # Part 5: Burden-direction coherence per class
    # ================================================================
    print("\n--- Part 5: Resolution coherence per class ---")
    coherence_data = t0.get('cross_tabs', {}).get('class_vs_coherence', {})
    coherence_analysis = {}
    for ecls in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT']:
        coh = coherence_data.get(f'{ecls}+coherent', 0)
        incoh = coherence_data.get(f'{ecls}+incoherent', 0)
        total = coh + incoh
        pct = 100.0 * coh / total if total > 0 else 0
        coherence_analysis[ecls] = {
            'coherent': coh,
            'incoherent': incoh,
            'coherent_pct': round(pct, 1),
        }
        print(f"  {ecls}: {pct:.1f}% coherent ({coh}/{total})")

    # ================================================================
    # Part 6: Config robustness
    # ================================================================
    print("\n--- Part 6: Config robustness ---")
    event_configs_list = [c for c in configs if c not in ('LINE_CLASS_CONTROL', 'CREDIT_ONLY_EVENT')]

    lcc_a2_delta = lcc.get('a2_delta', 0)
    co_a2_delta = config_comparison.get('CREDIT_ONLY_EVENT', {}).get('a2_delta', 0)

    n_beat_lcc = sum(1 for c in event_configs_list
                     if config_comparison[c]['a2_delta'] > lcc_a2_delta)
    n_beat_credit = sum(1 for c in event_configs_list
                        if config_comparison[c]['a2_delta'] > co_a2_delta)

    # Weak-band guardrail
    lcc_null_wins = lcc.get('null_wins_gated', 0)
    weak_guardrail_safe = all(
        config_comparison[c].get('null_wins_gated', 99) <= lcc_null_wins + 1
        for c in event_configs_list)

    config_robustness = {
        'n_event_configs': len(event_configs_list),
        'n_beat_lcc': n_beat_lcc,
        'n_beat_credit': n_beat_credit,
        'weak_guardrail_safe': weak_guardrail_safe,
        'architecture_robust': n_beat_lcc >= 2,
    }

    print(f"  Event configs: {len(event_configs_list)}")
    print(f"  Beat LINE_CLASS_CONTROL: {n_beat_lcc}/{len(event_configs_list)}")
    print(f"  Beat CREDIT_ONLY_EVENT: {n_beat_credit}/{len(event_configs_list)}")
    print(f"  Weak guardrail safe: {weak_guardrail_safe}")
    print(f"  Architecture robust: {config_robustness['architecture_robust']}")

    # Best config
    best_config = max(configs, key=lambda c: config_comparison[c]['a2_delta'])
    best_a2_delta = config_comparison[best_config]['a2_delta']
    best_ssi = config_comparison[best_config]['SSI']
    best_strong_pct = config_comparison[best_config]['strong_preserved_pct']

    print(f"\n  Best config: {best_config} (A2_delta={best_a2_delta:.4f}, "
          f"SSI={best_ssi:.4f}, strong%={best_strong_pct:.1f})")

    # Phase 576 comparison
    p576_a2_delta = lcc.get('a2_delta', 0)
    improvement = best_a2_delta - p576_a2_delta

    print(f"\n  Phase 576 (AMB_PESSIMISTIC) A2_delta: {p576_a2_delta:.4f}")
    print(f"  Phase 578 best A2_delta: {best_a2_delta:.4f}")
    print(f"  Improvement: {improvement:+.4f}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '578',
            'script': 't3_event_local_anatomy.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'baseline_band_means': {k: round(v, 6) for k, v in baseline_band_means.items()},
        'config_comparison': config_comparison,
        'c1660_decisive': {
            'ecf_beats_lcc_delta': ecf_beats_lcc_delta,
            'ecf_strong_ok': ecf_strong_ok,
            'ecf_null_ok': ecf_null_ok,
            'best_event_config': best_event_config,
            'best_beats_lcc': best_beats_lcc,
            'best_strong_ok': best_strong_ok,
            'verdict': c1660_verdict,
        },
        'c1661_discriminator': {
            'auth_mean_dye_adv': round(auth_mean, 6),
            'cf_mean_dye_adv': round(cf_mean, 6),
            'direction_ok': direction_ok,
            'cohens_d': round(d, 4),
            'effect_size_ok': effect_size_ok,
            'n_authentic': len(auth_dye_advs),
            'n_counterfeit': len(cf_dye_advs),
            'verdict': c1661_verdict,
        },
        'coherence_analysis': coherence_analysis,
        'a2_per_class_dye': {
            'lcc': {k: round(sum(v)/len(v), 6) if v else 0
                    for k, v in lcc_by_class_dye.items()},
            'ecf': {k: round(sum(v)/len(v), 6) if v else 0
                    for k, v in ecf_by_class_dye.items()},
        },
        'config_robustness': config_robustness,
        'best_config': best_config,
        'best_SSI': round(best_ssi, 4),
        'best_a2_delta': round(best_a2_delta, 6),
        'best_strong_preserved_pct': round(best_strong_pct, 1),
        'p576_comparison': {
            'p576_a2_delta': round(p576_a2_delta, 6),
            'p578_a2_delta': round(best_a2_delta, 6),
            'improvement': round(improvement, 6),
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't3_event_local_anatomy.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
