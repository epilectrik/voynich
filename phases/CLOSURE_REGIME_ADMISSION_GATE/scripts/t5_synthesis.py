"""
T5: Integration + Report + Constraints
Phase 576 - CLOSURE_REGIME_ADMISSION_GATE

Synthesizes T0-T4 results into C1651-C1654 constraint verdicts and generates
REPORT_576.md. Includes config robustness reporting per expert guidance.
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

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
PHASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T5: Integration + Constraints")
    print("Phase 576 - CLOSURE_REGIME_ADMISSION_GATE")
    print("=" * 70)

    # ---- Load all prior results ----
    with open(os.path.join(RESULTS_DIR, 't0_corpus_classification.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_closure_admission_apparatus.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_admission_simulation.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_gate_anatomy.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_landscape_remap.json')) as f:
        t4 = json.load(f)

    best_config = t3['best_config_by_SSI']
    best_ssi = t3['best_SSI']
    configs = list(t3['ssi_results'].keys())
    regime_configs = [c for c in configs if c != 'CREDIT_ONLY']

    # ================================================================
    # C1651: Tiered Classification
    # ================================================================
    print("\n--- C1651: Tiered Classification ---")

    class_dist = t0['class_distribution']
    n_classified = t0['metadata'].get('n_lines_classified', 0)
    n_classes_populated = sum(1 for v in class_dist.values() if v.get('n_lines', 0) > 0)
    ambiguous_pct = class_dist.get('AUTH_AMBIGUOUS', {}).get('pct', 100)
    m1_agreement = t0.get('m1_agreement', {})
    m1_pct = m1_agreement.get('pct', 0)
    coverage_ok = n_classified >= 2300
    agreement_ok = m1_pct >= 90
    no_degenerate = n_classes_populated >= 5  # at least 5 of 6 populated
    ambiguous_ok = ambiguous_pct < 30

    if coverage_ok and agreement_ok and no_degenerate and ambiguous_ok:
        c1651_verdict = 'CLASSIFICATION_VALIDATED'
    elif coverage_ok and (agreement_ok or no_degenerate):
        c1651_verdict = 'CLASSIFICATION_PARTIAL'
    else:
        c1651_verdict = 'CLASSIFICATION_REJECTED'

    c1651_explanation = (
        f"Lines classified={n_classified} (>=2300: {coverage_ok}). "
        f"M1 agreement={m1_pct:.1f}% (>=90%: {agreement_ok}). "
        f"Classes populated={n_classes_populated}/6 (>=5: {no_degenerate}). "
        f"AUTH_AMBIGUOUS={ambiguous_pct:.1f}% (<30%: {ambiguous_ok})."
    )
    print(f"  {c1651_verdict}")
    print(f"  {c1651_explanation}")

    # ================================================================
    # C1652: Regime Admission Selectivity (DECISIVE)
    # ================================================================
    print("\n--- C1652: Regime Admission Selectivity ---")

    ssi_results = t3['ssi_results']
    rg_ssi = ssi_results.get('REGIME_GATED', {}).get('SSI', 0)
    co_ssi = ssi_results.get('CREDIT_ONLY', {}).get('SSI', 0)

    # Use A2 delta_advantage as primary regime-beats-credit metric
    # (SSI can be similar when fi_reduction is the same)
    ps_rg = t2.get('profile_summary', {}).get('REGIME_GATED', {}).get(
        'A2_SEALED_RECIRCULATION', {})
    ps_co = t2.get('profile_summary', {}).get('CREDIT_ONLY', {}).get(
        'A2_SEALED_RECIRCULATION', {})
    rg_a2_delta = ps_rg.get('mean_delta_advantage', 0)
    co_a2_delta = ps_co.get('mean_delta_advantage', 0)
    regime_beats_credit = rg_a2_delta > co_a2_delta

    if best_ssi >= 2.0 and regime_beats_credit:
        c1652_verdict = 'ADMISSION_SELECTIVE'
    elif best_ssi >= 1.0:
        c1652_verdict = 'ADMISSION_PARTIAL'
    else:
        c1652_verdict = 'ADMISSION_REJECTED'

    c1652_explanation = (
        f"Best config={best_config}, SSI={best_ssi:.4f} (>=2.0: {best_ssi >= 2.0}). "
        f"REGIME_GATED A2 delta={rg_a2_delta:.4f} > CREDIT_ONLY={co_a2_delta:.4f}: {regime_beats_credit}. "
        f"REGIME_GATED SSI={rg_ssi:.4f}, CREDIT_ONLY SSI={co_ssi:.4f}."
    )
    print(f"  {c1652_verdict}")
    print(f"  {c1652_explanation}")

    # ================================================================
    # C1653: Event-Band Discrimination
    # ================================================================
    print("\n--- C1653: Event-Band Discrimination ---")

    cm = t3['confusion_matrix'].get(best_config, {})
    tp = cm.get('TP', 0)
    tn = cm.get('TN', 0)
    fp = cm.get('FP', 0)
    fn = cm.get('FN', 0)
    n_cf = cm.get('n_counterfeitable', 0)
    n_res = cm.get('n_resistant', 0)

    tp_ok = tp >= 3
    tn_ok = tn >= 4

    # Weak CF suppression and strong preservation from T2 profile summary
    profile_summary = t2.get('profile_summary', {}).get(best_config, {})
    a2_ps = profile_summary.get('A2_SEALED_RECIRCULATION', {})

    # Strong-band preservation: compare baseline vs gated strong DYE directly
    best_ssi_data = ssi_results.get(best_config, {})
    baseline_strong_dye = best_ssi_data.get('baseline_strong_dye', 0)
    gated_strong_dye = best_ssi_data.get('gated_strong_dye', 0)
    if baseline_strong_dye > 0.001:
        strong_preserved_pct = (gated_strong_dye / baseline_strong_dye) * 100
    else:
        strong_preserved_pct = 100.0
    strong_ok = strong_preserved_pct >= 90

    # Weak CF suppression: null win reduction
    baseline_null_wins = best_ssi_data.get('baseline_null_wins', 0)
    gated_null_wins = best_ssi_data.get('gated_null_wins', 0)
    if baseline_null_wins > 0:
        weak_suppression_pct = (baseline_null_wins - gated_null_wins) / baseline_null_wins * 100
    else:
        weak_suppression_pct = 0.0
    weak_ok = weak_suppression_pct >= 20

    if tp_ok and tn_ok and strong_ok and weak_ok:
        c1653_verdict = 'DISCRIMINATION_VALIDATED'
    elif (tp_ok or tn_ok) and (strong_ok or weak_ok):
        c1653_verdict = 'DISCRIMINATION_PARTIAL'
    else:
        c1653_verdict = 'DISCRIMINATION_REJECTED'

    c1653_explanation = (
        f"TP={tp}/{n_cf} (>=3: {tp_ok}). TN={tn}/{n_res} (>=4: {tn_ok}). "
        f"FP={fp}, FN={fn}. "
        f"Strong preserved={strong_preserved_pct:.1f}% (>=90%: {strong_ok}). "
        f"Weak CF null suppression={weak_suppression_pct:.1f}% (>=20%: {weak_ok})."
    )
    print(f"  {c1653_verdict}")
    print(f"  {c1653_explanation}")

    # ================================================================
    # C1654: Landscape + CCS1
    # ================================================================
    print("\n--- C1654: Landscape + CCS1 ---")

    a2_pole = t4['a2_pole_analysis']
    n_forg_ungated = a2_pole['n_forgiving_ungated']
    n_forg_gated = a2_pole['n_forgiving_gated']
    pole_reduction = a2_pole['pole_reduction_pct']
    new_a1a3 = a2_pole['a1a3_new_forgiving']
    ccs1_reduction = t4.get('ccs1_reduction_pct', 0)

    forgiving_reduced = n_forg_gated < n_forg_ungated
    no_new_a1a3 = new_a1a3 == 0
    ccs1_ok = ccs1_reduction >= 10

    if forgiving_reduced and no_new_a1a3 and ccs1_ok:
        c1654_verdict = 'LANDSCAPE_IMPROVED'
    elif new_a1a3 > 0 or n_forg_gated > n_forg_ungated:
        c1654_verdict = 'LANDSCAPE_AGGRAVATED'
    else:
        c1654_verdict = 'LANDSCAPE_STABLE'

    c1654_explanation = (
        f"A2 FORGIVING: {n_forg_ungated}->{n_forg_gated} (reduced: {forgiving_reduced}). "
        f"Pole reduction={pole_reduction:.1f}%. "
        f"New A1/A3 FORGIVING={new_a1a3} (none: {no_new_a1a3}). "
        f"CCS1 reduction={ccs1_reduction:.1f}% (>=10%: {ccs1_ok})."
    )
    print(f"  {c1654_verdict}")
    print(f"  {c1654_explanation}")

    # ================================================================
    # Config Robustness Assessment (expert Issue 4)
    # ================================================================
    print("\n--- Config Robustness ---")

    robustness = t3['config_robustness']
    n_regime = robustness['n_regime_configs']
    n_ssi_above_1 = robustness['n_ssi_above_1']
    n_tn_ge_4 = robustness['n_tn_ge_4_of_5']
    n_beat_credit = robustness.get('n_beat_credit_only_a2_delta',
                                    robustness.get('n_beat_credit_only', 0))
    arch_robust = robustness['architecture_robust']
    qual_holds = robustness['qualitative_holds']

    # AMB_PESSIMISTIC comparison
    amb_comp = t3.get('amb_pessimistic_comparison', {})
    amb_pess_better = amb_comp.get('pessimistic_better', False)

    # Per-config SSI for report
    per_config_ssi = {}
    for c in configs:
        per_config_ssi[c] = ssi_results.get(c, {}).get('SSI', 0)

    # REGIME_GATED > CREDIT_ONLY across all regime configs?
    all_regime_beat_credit = n_beat_credit == n_regime

    if arch_robust and qual_holds:
        robustness_assessment = 'ARCHITECTURE_ROBUST'
    elif n_beat_credit >= 2:
        robustness_assessment = 'ARCHITECTURE_PARTIAL'
    else:
        robustness_assessment = 'RESULT_CONFIG_SPECIFIC'

    print(f"  SSI > 1.0: {n_ssi_above_1}/{n_regime}")
    print(f"  TN >= 4/5: {n_tn_ge_4}/{n_regime}")
    print(f"  Beat CREDIT_ONLY: {n_beat_credit}/{n_regime}")
    print(f"  Architecture robust: {arch_robust}")
    print(f"  AMB_PESSIMISTIC better: {amb_pess_better}")
    print(f"  Assessment: {robustness_assessment}")

    # ================================================================
    # Build constraints
    # ================================================================
    constraints = {
        'C1651': {
            'id': 'C1651',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'classification', 'tiered_classifier', 'closure'],
            'claim': f"Tiered classification verdict: {c1651_verdict}. {c1651_explanation}",
            'verdict': c1651_verdict,
            'evidence': {
                'source': 'Phase 576 T0 corpus classification',
                'n_classified': n_classified,
                'n_classes_populated': n_classes_populated,
                'ambiguous_pct': round(ambiguous_pct, 1),
                'm1_agreement_pct': round(m1_pct, 1),
            },
            'phase': 576,
        },
        'C1652': {
            'id': 'C1652',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'regime_admission', 'gate', 'SSI', 'decisive'],
            'claim': f"Regime admission selectivity verdict: {c1652_verdict}. {c1652_explanation}",
            'verdict': c1652_verdict,
            'evidence': {
                'source': 'Phase 576 T3 gate anatomy + SSI analysis',
                'best_config': best_config,
                'best_SSI': round(best_ssi, 4),
                'regime_gated_SSI': round(rg_ssi, 4),
                'credit_only_SSI': round(co_ssi, 4),
                'regime_beats_credit': regime_beats_credit,
            },
            'phase': 576,
        },
        'C1653': {
            'id': 'C1653',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'discrimination', 'event_band', 'confusion_matrix'],
            'claim': f"Event-band discrimination verdict: {c1653_verdict}. {c1653_explanation}",
            'verdict': c1653_verdict,
            'evidence': {
                'source': 'Phase 576 T3 confusion matrix + T2 band analysis',
                'best_config': best_config,
                'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
                'strong_preserved_pct': round(strong_preserved_pct, 1),
                'weak_suppression_pct': round(weak_suppression_pct, 1),
            },
            'phase': 576,
        },
        'C1654': {
            'id': 'C1654',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'landscape', 'CCS1', 'pole_reduction'],
            'claim': f"Landscape + CCS1 verdict: {c1654_verdict}. {c1654_explanation}",
            'verdict': c1654_verdict,
            'evidence': {
                'source': 'Phase 576 T4 landscape remapping',
                'n_forgiving_ungated': n_forg_ungated,
                'n_forgiving_gated': n_forg_gated,
                'pole_reduction_pct': round(pole_reduction, 1),
                'new_a1a3_forgiving': new_a1a3,
                'ccs1_reduction_pct': round(ccs1_reduction, 1),
            },
            'phase': 576,
        },
    }

    # ================================================================
    # Summary verdicts
    # ================================================================
    verdicts = {
        'tiered_classification': {
            'verdict': c1651_verdict,
            'explanation': c1651_explanation,
        },
        'regime_admission_selectivity': {
            'verdict': c1652_verdict,
            'explanation': c1652_explanation,
        },
        'event_band_discrimination': {
            'verdict': c1653_verdict,
            'explanation': c1653_explanation,
        },
        'landscape_ccs1': {
            'verdict': c1654_verdict,
            'explanation': c1654_explanation,
        },
    }

    all_validated = (
        c1651_verdict == 'CLASSIFICATION_VALIDATED' and
        c1652_verdict == 'ADMISSION_SELECTIVE' and
        c1653_verdict == 'DISCRIMINATION_VALIDATED' and
        c1654_verdict == 'LANDSCAPE_IMPROVED'
    )

    # ================================================================
    # Generate REPORT_576.md
    # ================================================================
    print("\n--- Generating REPORT_576.md ---")

    t1_verify = t1.get('verification', {})
    t2_meta = t2.get('metadata', {})

    report_lines = [
        "# Phase 576: CLOSURE REGIME ADMISSION GATE",
        "",
        "## Summary",
        "",
        "Closure regime admission gate that gates Layer 2 (whether `_apply_close_recovery` "
        "fires at all) based on packet legitimacy class, CTS band, and containment burden. "
        "Phase 575 proved that gating Layer 3 (Y-credit) after closure is already admitted is "
        "insufficient. Phase 576 gates Layer 2 (closure regime admission R1-R5). "
        "Four constraints (C1651-C1654) produced.",
        "",
        f"**Best gate configuration:** {best_config}",
        f"**SSI (Surgical Selectivity Index):** {best_ssi:.4f}",
        f"**Architecture robust:** {robustness_assessment}",
        "",
        "## Constraint Verdicts",
        "",
        "| ID | Subject | Verdict | Pass? |",
        "|------|---------|---------|-------|",
        f"| C1651 | Tiered Classification | {c1651_verdict} | {'YES' if c1651_verdict == 'CLASSIFICATION_VALIDATED' else 'PARTIAL/NO'} |",
        f"| C1652 | Regime Admission Selectivity | {c1652_verdict} | {'YES' if c1652_verdict == 'ADMISSION_SELECTIVE' else 'PARTIAL/NO'} |",
        f"| C1653 | Event-Band Discrimination | {c1653_verdict} | {'YES' if c1653_verdict == 'DISCRIMINATION_VALIDATED' else 'PARTIAL/NO'} |",
        f"| C1654 | Landscape + CCS1 | {c1654_verdict} | {'YES' if c1654_verdict == 'LANDSCAPE_IMPROVED' else 'PARTIAL/NO'} |",
        "",
        "## T0: Tiered Classification + Burden Calibration",
        "",
        f"- Lines classified: {n_classified}",
        f"- Classes populated: {n_classes_populated}/6",
        f"- AUTH_AMBIGUOUS: {ambiguous_pct:.1f}%",
        f"- M1 event agreement: {m1_pct:.1f}%",
        f"- Burden threshold: {t0.get('burden_calibration', {}).get('recommended_threshold', '?')}",
        "",
        "### Class Distribution",
        "",
        "| Class | Lines | % |",
        "|-------|-------|---|",
    ]
    for cls_name in ['AUTH_RESISTANT', 'AUTH_COUNTERFEITABLE', 'AUTH_THRESHOLD',
                     'AUTH_PROTECTIVE', 'AUTH_PRONE', 'AUTH_AMBIGUOUS']:
        cd = class_dist.get(cls_name, {})
        report_lines.append(
            f"| {cls_name} | {cd.get('n_lines', 0)} | {cd.get('pct', 0):.1f}% |"
        )

    report_lines.extend([
        "",
        "## T1: ClosureAdmissionApparatus Verification",
        "",
        f"- Identity check: {'PASS' if t1_verify.get('identity_check', {}).get('pass') else 'FAIL'}",
        f"- Full rejection check: {'PASS' if t1_verify.get('full_rejection_check', {}).get('pass') else 'FAIL'}",
        f"- Credit-only control: {'PASS' if t1_verify.get('credit_only_check', {}).get('pass') else 'FAIL'}",
        f"- Regime admission: {'PASS' if t1_verify.get('regime_check', {}).get('pass') else 'FAIL'}",
        f"- Admit vs credit: {'PASS' if t1_verify.get('admit_vs_credit', {}).get('pass') else 'FAIL'}",
        f"- Burden conditioning: {'PASS' if t1_verify.get('burden_conditioning', {}).get('pass') else 'FAIL'}",
        "",
        "## T2: Full Simulation",
        "",
        f"- Configurations: {t2_meta.get('n_configs', 5)}",
        f"- Total runs: {t2_meta.get('total_runs', '?')}",
        f"- Elapsed: {t2_meta.get('elapsed_seconds', '?')}s",
        "",
        "### Profile Summary (best config: {})".format(best_config),
        "",
    ])

    ps = t2.get('profile_summary', {}).get(best_config, {})
    for profile in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']:
        ps_data = ps.get(profile, {})
        report_lines.append(
            f"- **{profile}**: delta_adv={ps_data.get('mean_delta_advantage', 0):.4f}, "
            f"CCS1_red={ps_data.get('ccs1_reduction_pct', 0):.1f}%, "
            f"improved/degraded={ps_data.get('n_improved', 0)}/{ps_data.get('n_degraded', 0)}"
        )
    report_lines.append("")

    report_lines.extend([
        "## T3: Gate Anatomy + Config Robustness",
        "",
        f"- Best config SSI: {best_ssi:.4f}",
        "",
        "### SSI per Config",
        "",
        "| Config | SSI |",
        "|--------|-----|",
    ])
    for c in configs:
        s = per_config_ssi.get(c, 0)
        report_lines.append(f"| {c} | {s:.4f} |")

    report_lines.extend([
        "",
        f"### Confusion Matrix ({best_config})",
        "",
        f"- TP (CF correctly suppressed): {tp}/{n_cf}",
        f"- TN (RESISTANT correctly preserved): {tn}/{n_res}",
        f"- FP (RESISTANT incorrectly harmed): {fp}",
        f"- FN (CF incorrectly spared): {fn}",
        "",
        "### Config Robustness",
        "",
        f"- SSI > 1.0: {n_ssi_above_1}/{n_regime} regime configs",
        f"- TN >= 4/5: {n_tn_ge_4}/{n_regime} regime configs",
        f"- Beat CREDIT_ONLY: {n_beat_credit}/{n_regime} regime configs",
        f"- All regime beat CREDIT_ONLY: {all_regime_beat_credit}",
        f"- Architecture robust: {arch_robust}",
        f"- Assessment: **{robustness_assessment}**",
        "",
        "### AMB_PESSIMISTIC Comparison",
        "",
    ])
    if amb_comp:
        report_lines.extend([
            f"- AMB_PESSIMISTIC SSI: {amb_comp.get('amb_pessimistic_ssi', 0):.4f}",
            f"- REGIME_GATED SSI: {amb_comp.get('regime_gated_ssi', 0):.4f}",
            f"- Pessimistic better: {amb_pess_better}",
            f"- Interpretation: {amb_comp.get('interpretation', 'N/A')}",
        ])
    else:
        report_lines.append("- No AMB_PESSIMISTIC config found in results")

    report_lines.extend([
        "",
        "## T4: Landscape Remapping",
        "",
        f"- A2 FORGIVING: {n_forg_ungated} -> {n_forg_gated} "
        f"({pole_reduction:.1f}% reduction)",
        f"- New A1/A3 FORGIVING: {new_a1a3}",
        f"- CCS1 reduction: {ccs1_reduction:.1f}%",
        "",
        "### Transition Matrix",
        "",
        "| From \\ To | STABLE_AMPLIFIER | THRESHOLD_DEPENDENT | FORGIVING_RECIRCULATOR |",
        "|-----------|------------------|--------------------|-----------------------|",
    ])

    tm = t4['transition_matrix']
    for from_cls in ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']:
        row = tm.get(from_cls, {})
        report_lines.append(
            f"| {from_cls} | {row.get('STABLE_AMPLIFIER', 0)} | "
            f"{row.get('THRESHOLD_DEPENDENT', 0)} | "
            f"{row.get('FORGIVING_RECIRCULATOR', 0)} |"
        )

    report_lines.extend([
        "",
        "## Tier 3 Interpretation",
        "",
    ])

    if all_validated:
        report_lines.append(
            "> The closure regime admission gate validates the expert's core diagnosis: "
            "counterfeit closure must be blocked at the regime level (Layer 2), not the "
            "reward level (Layer 3). The tiered classifier (AUTH_RESISTANT through AUTH_AMBIGUOUS) "
            "discriminates legitimacy using morphological signatures, and the two-stage gate "
            "(admit_mult + credit_mult) gates both regime admission and yield credit. "
            "Resistant packets are admitted fully; counterfeitable packets with no real "
            "containment burden are rejected entirely (only base physics act). "
            f"The architecture is {robustness_assessment.lower().replace('_', ' ')}: "
            f"{n_beat_credit}/{n_regime} regime configs outperform the credit-only control. "
            "The forgiving pole of the A2 landscape shrinks because the gate discriminates "
            "what counts as genuine closure, not because parameters change."
        )
    else:
        failing = []
        if c1651_verdict != 'CLASSIFICATION_VALIDATED':
            failing.append(f"C1651={c1651_verdict}")
        if c1652_verdict != 'ADMISSION_SELECTIVE':
            failing.append(f"C1652={c1652_verdict}")
        if c1653_verdict != 'DISCRIMINATION_VALIDATED':
            failing.append(f"C1653={c1653_verdict}")
        if c1654_verdict != 'LANDSCAPE_IMPROVED':
            failing.append(f"C1654={c1654_verdict}")

        partial_count = sum(1 for v in [c1651_verdict, c1652_verdict, c1653_verdict, c1654_verdict]
                           if 'PARTIAL' in v or 'STABLE' in v)
        fail_count = sum(1 for v in [c1651_verdict, c1652_verdict, c1653_verdict, c1654_verdict]
                        if 'REJECTED' in v or 'AGGRAVATED' in v)

        report_lines.append(
            f"> Tier 3 interpretation NOT frozen. Non-validated constraints: {', '.join(failing)}. "
            f"The closure regime admission gate shows "
            f"{'partial' if partial_count > fail_count else 'insufficient'} effectiveness. "
            f"Architecture assessment: {robustness_assessment}. "
            f"{'The regime admission concept may be sound but tuning or architecture changes needed.' if partial_count >= 2 else 'Further investigation needed into whether the regime admission approach is viable.'}"
        )

    report_lines.extend(["", f"*Generated: {datetime.now(timezone.utc).isoformat()}*", ""])

    report_path = os.path.join(PHASE_DIR, 'REPORT_576.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"  Wrote {report_path}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '576',
            'script': 't5_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'verdicts': verdicts,
        'constraints': constraints,
        'all_validated': all_validated,
        'best_config': best_config,
        'best_SSI': round(best_ssi, 4),
        'config_robustness': {
            'assessment': robustness_assessment,
            'per_config_SSI': {c: round(v, 4) for c, v in per_config_ssi.items()},
            'n_regime_beat_credit': n_beat_credit,
            'amb_pessimistic_better': amb_pess_better,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
