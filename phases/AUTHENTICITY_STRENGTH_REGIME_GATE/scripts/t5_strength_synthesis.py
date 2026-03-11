"""
T5: Integration + Report + Constraints
Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE

Synthesizes T0-T4 results into C1655-C1658 constraint verdicts and generates
REPORT_577.md. C1656 is the decisive test.
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
    print("Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE")
    print("=" * 70)

    # ---- Load all prior results ----
    with open(os.path.join(RESULTS_DIR, 't0_authenticity_strength_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_strength_gated_apparatus.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_strength_gated_simulation.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_strength_gate_anatomy.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_strength_landscape_remap.json')) as f:
        t4 = json.load(f)

    best_config = t3['best_config_by_a2_delta']
    best_ssi = t3['best_SSI']
    best_a2_delta = t3['best_a2_delta']
    best_strong_preserved = t3['best_strong_preserved_pct']
    configs = list(t3['per_config_SSI'].keys())
    ssi_results = t3['ssi_results']
    per_config_ssi = t3['per_config_SSI']

    # ================================================================
    # C1655: Authenticity Strength Coverage
    # ================================================================
    print("\n--- C1655: Authenticity Strength Coverage ---")

    n_lines = t0['metadata']['n_lines']
    band_dist = t0['band_distribution']
    n_bands_populated = sum(1 for v in band_dist.values() if v > 0)
    structural_zeros = t0['structural_zeros']
    surrogate = t0.get('event_band_surrogate_validation', {})
    surrogate_agree = surrogate.get('agreement_pct', 0)

    coverage_ok = n_lines >= 2300
    bands_ok = n_bands_populated == 3
    zeros_documented = len(structural_zeros) >= 5

    if coverage_ok and bands_ok and zeros_documented:
        c1655_verdict = 'COVERAGE_VALIDATED'
    elif coverage_ok and bands_ok:
        c1655_verdict = 'COVERAGE_PARTIAL'
    else:
        c1655_verdict = 'COVERAGE_REJECTED'

    c1655_explanation = (
        f"Lines={n_lines} (>=2300: {coverage_ok}). "
        f"Bands populated={n_bands_populated}/3 (==3: {bands_ok}). "
        f"Structural zeros={len(structural_zeros)} (>=5: {zeros_documented}). "
        f"Surrogate agreement={surrogate_agree:.1f}%."
    )
    print(f"  {c1655_verdict}")
    print(f"  {c1655_explanation}")

    # ================================================================
    # C1656: Strong-Band Rescue (DECISIVE)
    # ================================================================
    print("\n--- C1656: Strong-Band Rescue ---")

    ssi_data = ssi_results.get(best_config, {})
    strong_preserved = ssi_data.get('strong_preserved_pct', 0)

    weak_guard = t3['weak_guardrail'].get(best_config, {})
    weak_safe = weak_guard.get('weak_band_safe', False)

    p576_comparison = t3.get('p576_comparison', {})
    p576_a2_delta = p576_comparison.get('p576_a2_delta', 0)
    a2_delta_meets_p576 = best_a2_delta >= p576_a2_delta

    strong_ok = strong_preserved >= 80
    strong_partial = strong_preserved >= 70

    if strong_ok and weak_safe and a2_delta_meets_p576:
        c1656_verdict = 'RESCUE_EFFECTIVE'
    elif strong_partial and weak_safe:
        c1656_verdict = 'RESCUE_PARTIAL'
    else:
        c1656_verdict = 'RESCUE_REJECTED'

    c1656_explanation = (
        f"Best config={best_config}. "
        f"Strong preserved={strong_preserved:.1f}% (>=80%: {strong_ok}). "
        f"Weak guardrail={'SAFE' if weak_safe else 'VIOLATED'}. "
        f"A2 delta={best_a2_delta:.4f} >= P576 {p576_a2_delta:.4f}: {a2_delta_meets_p576}."
    )
    print(f"  {c1656_verdict}")
    print(f"  {c1656_explanation}")

    # ================================================================
    # C1657: Configuration Robustness
    # ================================================================
    print("\n--- C1657: Configuration Robustness ---")

    robustness = t3['config_robustness']
    n_strength = robustness['n_strength_configs']
    n_beat_ns = robustness['n_beat_no_strength']
    n_beat_co = robustness['n_beat_credit_only']

    if n_beat_ns >= 3 and n_beat_co >= 3:
        c1657_verdict = 'ROBUST'
    elif n_beat_ns >= 2 and n_beat_co >= 2:
        c1657_verdict = 'PARTIAL'
    else:
        c1657_verdict = 'SPECIFIC'

    c1657_explanation = (
        f"Strength configs={n_strength}. "
        f"Beat NO_STRENGTH={n_beat_ns}/{n_strength} (>=3: {n_beat_ns >= 3}). "
        f"Beat CREDIT_ONLY_4D={n_beat_co}/{n_strength} (>=3: {n_beat_co >= 3}). "
        f"Architecture robust: {robustness['architecture_robust']}."
    )
    print(f"  {c1657_verdict}")
    print(f"  {c1657_explanation}")

    # ================================================================
    # C1658: Landscape Migration
    # ================================================================
    print("\n--- C1658: Landscape Migration ---")

    a2_pole = t4['a2_pole_analysis']
    n_forg_ungated = a2_pole['n_forgiving_ungated']
    n_forg_gated = a2_pole['n_forgiving_gated']
    pole_reduction = a2_pole['pole_reduction_pct']
    n_migrating = t4.get('n_migrating', 0)
    a1a3_new = a2_pole['a1a3_new_forgiving']

    regressed = n_forg_gated > n_forg_ungated or a1a3_new > 0

    if n_migrating >= 1 and not regressed:
        c1658_verdict = 'MIGRATION_DETECTED'
    elif regressed:
        c1658_verdict = 'MIGRATION_REGRESSED'
    else:
        c1658_verdict = 'MIGRATION_ABSENT'

    c1658_explanation = (
        f"Migrating folios={n_migrating} (>=1: {n_migrating >= 1}). "
        f"A2 FORGIVING: {n_forg_ungated}->{n_forg_gated}. "
        f"Pole reduction={pole_reduction:.1f}%. "
        f"Regressed: {regressed}."
    )
    print(f"  {c1658_verdict}")
    print(f"  {c1658_explanation}")

    # ================================================================
    # Build constraints
    # ================================================================
    constraints = {
        'C1655': {
            'id': 'C1655',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'strength', 'coverage', 'closure'],
            'claim': f"Authenticity strength coverage verdict: {c1655_verdict}. {c1655_explanation}",
            'verdict': c1655_verdict,
            'evidence': {
                'source': 'Phase 577 T0 authenticity strength assembly',
                'n_lines': n_lines,
                'n_bands_populated': n_bands_populated,
                'n_structural_zeros': len(structural_zeros),
                'surrogate_agreement_pct': round(surrogate_agree, 1),
            },
            'phase': 577,
        },
        'C1656': {
            'id': 'C1656',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'rescue', 'strength', 'decisive', 'closure'],
            'claim': f"Strong-band rescue verdict: {c1656_verdict}. {c1656_explanation}",
            'verdict': c1656_verdict,
            'evidence': {
                'source': 'Phase 577 T3 strength gate anatomy',
                'best_config': best_config,
                'strong_preserved_pct': round(strong_preserved, 1),
                'weak_guardrail_safe': weak_safe,
                'a2_delta': round(best_a2_delta, 6),
                'p576_a2_delta': round(p576_a2_delta, 6),
                'best_SSI': round(best_ssi, 4),
            },
            'phase': 577,
        },
        'C1657': {
            'id': 'C1657',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'robustness', 'configuration', 'closure'],
            'claim': f"Configuration robustness verdict: {c1657_verdict}. {c1657_explanation}",
            'verdict': c1657_verdict,
            'evidence': {
                'source': 'Phase 577 T3 config robustness',
                'n_strength_configs': n_strength,
                'n_beat_no_strength': n_beat_ns,
                'n_beat_credit_only': n_beat_co,
                'per_config_SSI': per_config_ssi,
            },
            'phase': 577,
        },
        'C1658': {
            'id': 'C1658',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'landscape', 'migration', 'closure'],
            'claim': f"Landscape migration verdict: {c1658_verdict}. {c1658_explanation}",
            'verdict': c1658_verdict,
            'evidence': {
                'source': 'Phase 577 T4 landscape remap',
                'n_forgiving_ungated': n_forg_ungated,
                'n_forgiving_gated': n_forg_gated,
                'pole_reduction_pct': round(pole_reduction, 1),
                'n_migrating': n_migrating,
                'a1a3_new_forgiving': a1a3_new,
            },
            'phase': 577,
        },
    }

    # ================================================================
    # Summary verdicts
    # ================================================================
    verdicts = {
        'authenticity_strength_coverage': {
            'verdict': c1655_verdict,
            'explanation': c1655_explanation,
        },
        'strong_band_rescue': {
            'verdict': c1656_verdict,
            'explanation': c1656_explanation,
        },
        'configuration_robustness': {
            'verdict': c1657_verdict,
            'explanation': c1657_explanation,
        },
        'landscape_migration': {
            'verdict': c1658_verdict,
            'explanation': c1658_explanation,
        },
    }

    all_validated = (
        c1655_verdict == 'COVERAGE_VALIDATED' and
        c1656_verdict == 'RESCUE_EFFECTIVE' and
        c1657_verdict == 'ROBUST' and
        c1658_verdict == 'MIGRATION_DETECTED'
    )

    # ================================================================
    # Generate REPORT_577.md
    # ================================================================
    print("\n--- Generating REPORT_577.md ---")

    t1_verify = t1.get('verification', {})
    t2_meta = t2.get('metadata', {})
    alignment = t0.get('alignment_comparison', {})

    report_lines = [
        "# Phase 577: AUTHENTICITY-STRENGTH REGIME GATE",
        "",
        "## Summary",
        "",
        "Adds closure authenticity strength as a 4th gate input to Phase 576's regime "
        "admission architecture. Phase 576 proved regime admission gating works "
        "(ARCHITECTURE_ROBUST) but strong-band DYE preservation was only 58.7% "
        "(target 90%). Phase 577 adds strength bands (STRONG/MED/WEAK) as a 4th "
        "gate dimension to rescue strong legitimate closure without weak-band relapse.",
        "",
        f"**Best gate configuration:** {best_config}",
        f"**SSI:** {best_ssi:.4f}",
        f"**Strong-band preserved:** {best_strong_preserved:.1f}%",
        f"**A2 delta advantage:** {best_a2_delta:.4f}",
        "",
        "## Constraint Verdicts",
        "",
        "| ID | Subject | Verdict |",
        "|----|---------|---------|",
        f"| C1655 | Authenticity Strength Coverage | {c1655_verdict} |",
        f"| C1656 | Strong-Band Rescue (decisive) | {c1656_verdict} |",
        f"| C1657 | Configuration Robustness | {c1657_verdict} |",
        f"| C1658 | Landscape Migration | {c1658_verdict} |",
        "",
        "## T0: Authenticity Strength Assembly",
        "",
        f"- Lines with strength: {n_lines}",
        f"- Bands: STRONG={band_dist.get('STRONG', 0)}, MED={band_dist.get('MED', 0)}, WEAK={band_dist.get('WEAK', 0)}",
        f"- Structural zeros: {len(structural_zeros)}",
        f"- Surrogate agreement (vs Phase 574 events): {surrogate_agree:.1f}%",
        "",
        "### Signal Alignment Changes from Phase 576",
        "",
        f"- Opaque (>=0.5 -> >0): {alignment.get('n_opaque_changed', '?')} lines changed",
        f"- Armed (proxy -> strict closure_armed): {alignment.get('n_armed_changed', '?')} lines changed",
        "",
        "## T1: Apparatus Verification",
        "",
    ]

    for test_name, test_data in t1_verify.items():
        status = "PASS" if test_data.get('pass') else "FAIL"
        report_lines.append(f"- {test_name}: {status}")
    report_lines.append("")

    report_lines.extend([
        "## T2: Full Simulation",
        "",
        f"- Configurations: {t2_meta.get('n_configs', 5)}",
        f"- Total runs: {t2_meta.get('total_runs', '?')}",
        f"- Elapsed: {t2_meta.get('elapsed_seconds', '?')}s",
        "",
        f"### Profile Summary (best: {best_config})",
        "",
    ])

    ps = t2.get('profile_summary', {}).get(best_config, {})
    for profile in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']:
        ps_data = ps.get(profile, {})
        report_lines.append(
            f"- **{profile}**: delta_adv={ps_data.get('mean_delta_advantage', 0):.4f}, "
            f"CCS1_red={ps_data.get('ccs1_reduction_pct', 0):.1f}%, "
            f"null_wins={ps_data.get('n_null_wins_baseline', 0)}->{ps_data.get('n_null_wins_gated', 0)}"
        )
    report_lines.append("")

    # T3 anatomy
    report_lines.extend([
        "## T3: Strength Gate Anatomy",
        "",
        "### SSI per Config",
        "",
        "| Config | SSI | Strong% | Weak Safe |",
        "|--------|-----|---------|-----------|",
    ])
    for c in configs:
        ssi_val = per_config_ssi.get(c, 0)
        sp = ssi_results.get(c, {}).get('strong_preserved_pct', 0)
        ws = t3['weak_guardrail'].get(c, {}).get('weak_band_safe', False)
        report_lines.append(f"| {c} | {ssi_val:.4f} | {sp:.1f}% | {'YES' if ws else 'NO'} |")

    # Per-class rescue
    report_lines.extend([
        "",
        "### Per-Class Rescue Breakdown",
        "",
    ])
    rescue_data = t3.get('per_class_rescue', {}).get(best_config, {})
    for cls in ['AUTH_PROTECTIVE', 'AUTH_THRESHOLD', 'AUTH_AMBIGUOUS']:
        info = rescue_data.get(cls, {})
        report_lines.append(
            f"- **{cls}**: STRONG delta={info.get('delta_strong', 0):.6f} "
            f"(n={info.get('n_strong_folios', 0)}), "
            f"gated={info.get('mean_strong_gated_dye', 0):.6f}, "
            f"baseline={info.get('baseline_strong_dye', 0):.6f}"
        )
    report_lines.append("")

    # Structural-zero activations
    sz_report_data = t3.get('structural_zero_report', {})
    total_sz = sum(v.get('n_activations', 0) for v in sz_report_data.values())
    report_lines.extend([
        "### Structural-Zero Activations",
        "",
        f"- Total across all configs: {total_sz}",
    ])
    for c in configs:
        n_sz = sz_report_data.get(c, {}).get('n_activations', 0)
        if n_sz > 0:
            report_lines.append(f"- {c}: {n_sz} (DIAGNOSTIC)")
    report_lines.append("")

    # Config robustness
    report_lines.extend([
        "### Config Robustness",
        "",
        f"- Beat NO_STRENGTH: {n_beat_ns}/{n_strength}",
        f"- Beat CREDIT_ONLY_4D: {n_beat_co}/{n_strength}",
        f"- Beat Phase 576: {robustness.get('n_beat_phase_576', 0)}/{len(configs)}",
        f"- Assessment: **{c1657_verdict}**",
        "",
    ])

    # Phase 576 comparison
    p576_comp = t3.get('p576_comparison', {})
    report_lines.extend([
        "### Phase 576 Comparison",
        "",
        f"- Phase 576 best ({p576_comp.get('p576_best_config', '')}): A2 delta={p576_a2_delta:.4f}",
        f"- Phase 577 best ({best_config}): A2 delta={best_a2_delta:.4f}",
        f"- Improvement: {best_a2_delta - p576_a2_delta:+.4f}",
        "",
    ])

    # T4 landscape
    report_lines.extend([
        "## T4: Landscape + Migration",
        "",
        f"- A2 FORGIVING: {n_forg_ungated} -> {n_forg_gated} ({pole_reduction:.1f}% reduction)",
        f"- Migrating folios: {n_migrating}",
        f"- New A1/A3 FORGIVING: {a1a3_new}",
        "",
    ])

    if n_migrating > 0:
        report_lines.append("### Migrating Folios")
        report_lines.append("")
        migration = t4.get('migration_report', {})
        for folio, info in sorted(migration.items()):
            if info.get('migrating'):
                report_lines.append(
                    f"- {folio}: deficit change={info['deficit_change_pct']:.1f}%, "
                    f"z={info['gated_z_margin']:.3f}"
                )
        report_lines.append("")

    # Tier 3 interpretation
    report_lines.extend([
        "## Tier 3 Interpretation",
        "",
    ])

    if all_validated:
        report_lines.append(
            "> Adding closure authenticity strength as a 4th gate dimension rescues "
            "strong-band DYE preservation while maintaining weak-band suppression. "
            f"The best configuration ({best_config}) preserves {best_strong_preserved:.1f}% "
            f"of strong-band DYE (up from Phase 576's 58.7%), with A2 delta advantage "
            f"of {best_a2_delta:.4f} (Phase 576: {p576_a2_delta:.4f}). "
            "The strength dimension resolves the classifier-resolution shortfall "
            "identified in Phase 576: strong legitimate closure on structurally "
            "mediocre-looking packets is now distinguished from counterfeit closure "
            "on similar packets."
        )
    else:
        failing = []
        if c1655_verdict != 'COVERAGE_VALIDATED':
            failing.append(f"C1655={c1655_verdict}")
        if c1656_verdict != 'RESCUE_EFFECTIVE':
            failing.append(f"C1656={c1656_verdict}")
        if c1657_verdict != 'ROBUST':
            failing.append(f"C1657={c1657_verdict}")
        if c1658_verdict != 'MIGRATION_DETECTED':
            failing.append(f"C1658={c1658_verdict}")

        report_lines.append(
            f"> Tier 3 interpretation NOT frozen. Non-validated: {', '.join(failing)}. "
            f"Strong-band preservation={best_strong_preserved:.1f}% "
            f"(target >=80%, Phase 576 baseline=58.7%). "
            f"{'The strength rescue approach shows promise but needs tuning.' if c1656_verdict == 'RESCUE_PARTIAL' else 'Further investigation needed.'}"
        )

    report_lines.extend(["", f"*Generated: {datetime.now(timezone.utc).isoformat()}*", ""])

    report_path = os.path.join(PHASE_DIR, 'REPORT_577.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"  Wrote {report_path}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '577',
            'script': 't5_strength_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'verdicts': verdicts,
        'constraints': constraints,
        'all_validated': all_validated,
        'best_config': best_config,
        'best_SSI': round(best_ssi, 4),
        'best_a2_delta': round(best_a2_delta, 6),
        'best_strong_preserved_pct': round(best_strong_preserved, 1),
        'config_robustness': {
            'assessment': c1657_verdict,
            'per_config_SSI': per_config_ssi,
            'n_beat_no_strength': n_beat_ns,
            'n_beat_credit_only': n_beat_co,
        },
        'p576_comparison': {
            'p576_best_config': p576_comp.get('p576_best_config', ''),
            'p576_a2_delta': round(p576_a2_delta, 6),
            'p577_a2_delta': round(best_a2_delta, 6),
            'improvement': round(best_a2_delta - p576_a2_delta, 6),
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't5_strength_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
