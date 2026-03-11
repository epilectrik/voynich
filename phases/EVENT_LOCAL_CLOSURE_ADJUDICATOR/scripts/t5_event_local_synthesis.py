"""
T5: Integration + Constraints + Report
Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR

Constraints C1659-C1662:
  C1659: Event-Local Feature Coverage
  C1660: Event Legitimacy Gating (DECISIVE)
  C1661: Burden Resolution Discriminator
  C1662: Landscape Migration
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


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T5: Integration + Constraints")
    print("Phase 578 - EVENT_LOCAL_CLOSURE_ADJUDICATOR")
    print("=" * 70)

    # ---- Load all prior results ----
    with open(os.path.join(RESULTS_DIR, 't0_event_local_classification.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_event_local_apparatus.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_event_local_simulation.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_event_local_anatomy.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_event_local_landscape.json')) as f:
        t4 = json.load(f)

    best_config = t3['best_config']
    best_ssi = t3['best_SSI']
    best_a2_delta = t3['best_a2_delta']
    best_strong_pct = t3['best_strong_preserved_pct']
    configs = list(t3['config_comparison'].keys())

    # ================================================================
    # C1659: Event-Local Feature Coverage
    # ================================================================
    print("\n--- C1659: Event-Local Feature Coverage ---")

    n_events = t0['metadata']['n_events']
    n_total = t0['metadata']['n_total_lines']
    class_dist = t0['class_distribution']
    n_classes_populated = sum(1 for v in class_dist.values() if v > 0)
    n_classes_expected = 4  # AUTHENTIC, PARTIAL, COUNTERFEIT, INERT

    # Distribution profiled
    stats = t0['distribution_stats']['burden_frac_resolved']

    events_ok = n_events == 463
    total_ok = n_total == 2323
    # Allow 3+ classes (INERT may be 0)
    classes_ok = n_classes_populated >= 3

    if events_ok and total_ok and classes_ok:
        c1659_verdict = 'COVERAGE_VALIDATED'
    elif events_ok and total_ok:
        c1659_verdict = 'COVERAGE_PARTIAL'
    else:
        c1659_verdict = 'COVERAGE_REJECTED'

    c1659_explanation = (
        f"Events={n_events} (==463: {events_ok}). "
        f"Total lines={n_total} (==2323: {total_ok}). "
        f"Classes populated={n_classes_populated}/{n_classes_expected} (>=3: {classes_ok}). "
        f"Burden range=[{stats['min']:.4f}, {stats['max']:.4f}]."
    )
    print(f"  {c1659_verdict}")
    print(f"  {c1659_explanation}")

    # ================================================================
    # C1660: Event Legitimacy Gating (DECISIVE)
    # ================================================================
    print("\n--- C1660: Event Legitimacy Gating (DECISIVE) ---")

    c1660 = t3['c1660_decisive']
    c1660_verdict = c1660['verdict']

    lcc_delta = t3['config_comparison'].get('LINE_CLASS_CONTROL', {}).get('a2_delta', 0)
    lcc_null = t3['config_comparison'].get('LINE_CLASS_CONTROL', {}).get('null_wins_gated', 0)
    lcc_strong = t3['config_comparison'].get('LINE_CLASS_CONTROL', {}).get('strong_preserved_pct', 0)

    c1660_explanation = (
        f"Best config={best_config}. "
        f"A2 delta={best_a2_delta:.4f} vs LCC={lcc_delta:.4f}: "
        f"beats={best_a2_delta >= lcc_delta}. "
        f"Strong preserved={best_strong_pct:.1f}% (>=80%: {best_strong_pct >= 80}). "
        f"Null wins: LCC={lcc_null}, best={t3['config_comparison'].get(best_config, {}).get('null_wins_gated', 0)}."
    )
    print(f"  {c1660_verdict}")
    print(f"  {c1660_explanation}")

    # ================================================================
    # C1661: Burden Resolution Discriminator
    # ================================================================
    print("\n--- C1661: Burden Resolution Discriminator ---")

    c1661 = t3['c1661_discriminator']
    c1661_verdict = c1661['verdict']

    c1661_explanation = (
        f"AUTHENTIC mean DYE_adv={c1661['auth_mean_dye_adv']:.6f}, "
        f"COUNTERFEIT={c1661['cf_mean_dye_adv']:.6f}. "
        f"Direction (AUTH>CF): {c1661['direction_ok']}. "
        f"Cohen's d={c1661['cohens_d']:.4f} (>=0.3: {c1661['effect_size_ok']}). "
        f"n_auth={c1661['n_authentic']}, n_cf={c1661['n_counterfeit']}."
    )
    print(f"  {c1661_verdict}")
    print(f"  {c1661_explanation}")

    # ================================================================
    # C1662: Landscape Migration
    # ================================================================
    print("\n--- C1662: Landscape Migration ---")

    a2_pole = t4['a2_pole_analysis']
    n_forg_ungated = a2_pole['n_forgiving_ungated']
    n_forg_gated = a2_pole['n_forgiving_gated']
    pole_reduction = a2_pole['pole_reduction_pct']
    new_a1a3 = a2_pole['a1a3_new_forgiving']
    n_migrating = len(t4.get('migrating_folios', []))

    forgiving_reduced = n_forg_gated < n_forg_ungated
    no_regression = new_a1a3 == 0 and n_forg_gated <= n_forg_ungated

    if n_migrating >= 1 and no_regression:
        c1662_verdict = 'MIGRATION_DETECTED'
    elif new_a1a3 > 0 or n_forg_gated > n_forg_ungated:
        c1662_verdict = 'MIGRATION_REGRESSED'
    else:
        c1662_verdict = 'MIGRATION_ABSENT'

    c1662_explanation = (
        f"Migrating folios={n_migrating} (>=1: {n_migrating >= 1}). "
        f"A2 FORGIVING: {n_forg_ungated}->{n_forg_gated}. "
        f"Pole reduction={pole_reduction:.1f}%. "
        f"Regressed: {not no_regression}."
    )
    print(f"  {c1662_verdict}")
    print(f"  {c1662_explanation}")

    # ================================================================
    # Build constraints
    # ================================================================
    constraints = {
        'C1659': {
            'id': 'C1659',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'event_local', 'coverage', 'closure'],
            'claim': f"Event-local feature coverage verdict: {c1659_verdict}. {c1659_explanation}",
            'verdict': c1659_verdict,
            'evidence': {
                'source': 'Phase 578 T0 event-local classification',
                'n_events': n_events,
                'n_total_lines': n_total,
                'n_classes_populated': n_classes_populated,
                'class_distribution': class_dist,
            },
            'phase': 578,
        },
        'C1660': {
            'id': 'C1660',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'event_gating', 'decisive', 'closure'],
            'claim': f"Event legitimacy gating verdict: {c1660_verdict}. {c1660_explanation}",
            'verdict': c1660_verdict,
            'evidence': {
                'source': 'Phase 578 T3 event-local anatomy',
                'best_config': best_config,
                'best_a2_delta': round(best_a2_delta, 6),
                'lcc_a2_delta': round(lcc_delta, 6),
                'best_strong_preserved_pct': round(best_strong_pct, 1),
                'best_SSI': round(best_ssi, 4),
            },
            'phase': 578,
        },
        'C1661': {
            'id': 'C1661',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'burden_resolution', 'discriminator', 'closure'],
            'claim': f"Burden resolution discriminator verdict: {c1661_verdict}. {c1661_explanation}",
            'verdict': c1661_verdict,
            'evidence': {
                'source': 'Phase 578 T3 burden-DYE analysis',
                'auth_mean_dye_adv': c1661['auth_mean_dye_adv'],
                'cf_mean_dye_adv': c1661['cf_mean_dye_adv'],
                'cohens_d': c1661['cohens_d'],
                'direction_ok': c1661['direction_ok'],
                'effect_size_ok': c1661['effect_size_ok'],
            },
            'phase': 578,
        },
        'C1662': {
            'id': 'C1662',
            'tier': 2,
            'scope': 'B',
            'tags': ['apparatus', 'landscape', 'migration', 'closure'],
            'claim': f"Landscape migration verdict: {c1662_verdict}. {c1662_explanation}",
            'verdict': c1662_verdict,
            'evidence': {
                'source': 'Phase 578 T4 landscape remap',
                'n_forgiving_ungated': n_forg_ungated,
                'n_forgiving_gated': n_forg_gated,
                'pole_reduction_pct': round(pole_reduction, 1),
                'n_migrating': n_migrating,
                'a1a3_new_forgiving': new_a1a3,
            },
            'phase': 578,
        },
    }

    # ================================================================
    # Summary verdicts
    # ================================================================
    verdicts = {
        'event_local_coverage': {'verdict': c1659_verdict, 'explanation': c1659_explanation},
        'event_legitimacy_gating': {'verdict': c1660_verdict, 'explanation': c1660_explanation},
        'burden_resolution_discriminator': {'verdict': c1661_verdict, 'explanation': c1661_explanation},
        'landscape_migration': {'verdict': c1662_verdict, 'explanation': c1662_explanation},
    }

    all_validated = (
        c1659_verdict == 'COVERAGE_VALIDATED' and
        c1660_verdict == 'EVENT_GATING_VALIDATED' and
        c1661_verdict == 'DISCRIMINATOR_CONFIRMED' and
        c1662_verdict == 'MIGRATION_DETECTED'
    )

    # Config robustness
    robustness = t3.get('config_robustness', {})

    # Per-config SSI for report
    per_config_ssi = {}
    for c, data in t3['config_comparison'].items():
        per_config_ssi[c] = data.get('SSI', 0)

    # ================================================================
    # Generate REPORT_578.md
    # ================================================================
    print("\n--- Generating REPORT_578.md ---")

    t1_verify = t1.get('verification', {})
    t2_meta = t2.get('metadata', {})

    # Phase 576 comparison
    p576_comp = t3.get('p576_comparison', {})

    report_lines = [
        "# Phase 578: EVENT-LOCAL CLOSURE ADJUDICATOR",
        "",
        "## Summary",
        "",
        "Replaces Phase 576's line-level morphological classifier with an event-level "
        "execution+anatomy classifier. Phase 577 falsified line-level strength as the "
        "missing precision variable (21.6% surrogate agreement). The expert diagnosis: "
        "closure legitimacy is event-local, not line-local. The key discriminator is "
        "burden resolution — whether the CLOSE event actually reduced max(|C-0.5|, |X-0.5|) — "
        "combined with event-level packet strength signals from Phase 574.",
        "",
        f"**Best gate configuration:** {best_config}",
        f"**SSI:** {best_ssi:.4f}",
        f"**A2 delta advantage:** {best_a2_delta:.4f}",
        f"**Strong-band preserved:** {best_strong_pct:.1f}%",
        "",
        "## Constraint Verdicts",
        "",
        "| ID | Subject | Verdict |",
        "|----|---------|---------  |",
        f"| C1659 | Event-Local Feature Coverage | {c1659_verdict} |",
        f"| C1660 | Event Legitimacy Gating (decisive) | {c1660_verdict} |",
        f"| C1661 | Burden Resolution Discriminator | {c1661_verdict} |",
        f"| C1662 | Landscape Migration | {c1662_verdict} |",
        "",
        "## T0: Event-Local Classification",
        "",
        f"- Events classified: {n_events}",
        f"- Total lines: {n_total}",
        f"- Classes populated: {n_classes_populated}/4",
        "",
        "### Class Distribution",
        "",
        "| Class | Count | % |",
        "|-------|-------|---|",
    ]

    for cls_name in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT', 'INERT_PSEUDO']:
        count = class_dist.get(cls_name, 0)
        pct = 100.0 * count / n_events if n_events > 0 else 0
        report_lines.append(f"| {cls_name} | {count} | {pct:.1f}% |")

    report_lines.extend([
        "",
        "### Burden Resolution Distribution",
        "",
        f"- Min: {stats['min']:.4f}, Max: {stats['max']:.4f}",
        f"- p25: {stats['percentiles']['p25']}, p50: {stats['percentiles']['p50']}, p75: {stats['percentiles']['p75']}",
        "",
        "### Resolution Coherence",
        "",
    ])
    coherence = t3.get('coherence_analysis', {})
    for cls_name in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT']:
        coh = coherence.get(cls_name, {})
        report_lines.append(
            f"- **{cls_name}**: {coh.get('coherent_pct', 0):.1f}% coherent "
            f"({coh.get('coherent', 0)}/{coh.get('coherent', 0) + coh.get('incoherent', 0)})")

    report_lines.extend([
        "",
        "## T1: Apparatus Verification",
        "",
    ])
    for name, v in t1_verify.items():
        report_lines.append(f"- {name}: {'PASS' if v.get('pass') else 'FAIL'}")

    report_lines.extend([
        "",
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
            f"null_wins={ps_data.get('n_null_wins_baseline', 0)}->{ps_data.get('n_null_wins_gated', 0)}")

    report_lines.extend([
        "",
        "## T3: Gate Anatomy + Decisive Test",
        "",
        "### SSI per Config",
        "",
        "| Config | SSI | A2 delta | Strong% | Null wins |",
        "|--------|-----|----------|---------|-----------|",
    ])

    for c in configs:
        data = t3['config_comparison'].get(c, {})
        report_lines.append(
            f"| {c} | {data.get('SSI', 0):.4f} | {data.get('a2_delta', 0):.4f} | "
            f"{data.get('strong_preserved_pct', 0):.1f}% | "
            f"{data.get('null_wins_gated', 0)} |")

    report_lines.extend([
        "",
        f"### C1660 Decisive Test: {c1660_verdict}",
        "",
        f"- EVENT_CLASS_FULL beats LINE_CLASS_CONTROL: {c1660['ecf_beats_lcc_delta']}",
        f"- Strong >= 80%: {c1660['ecf_strong_ok']}",
        f"- Null wins <= LCC: {c1660['ecf_null_ok']}",
        "",
        f"### C1661 Burden-DYE Discriminator: {c1661_verdict}",
        "",
        f"- AUTHENTIC mean DYE_adv: {c1661['auth_mean_dye_adv']:.6f}",
        f"- COUNTERFEIT mean DYE_adv: {c1661['cf_mean_dye_adv']:.6f}",
        f"- Direction (AUTH > CF): {c1661['direction_ok']}",
        f"- Cohen's d: {c1661['cohens_d']:.4f} (>= 0.3: {c1661['effect_size_ok']})",
        "",
        "### Config Robustness",
        "",
        f"- Beat LINE_CLASS_CONTROL: {robustness.get('n_beat_lcc', 0)}/{robustness.get('n_event_configs', 0)}",
        f"- Beat CREDIT_ONLY_EVENT: {robustness.get('n_beat_credit', 0)}/{robustness.get('n_event_configs', 0)}",
        f"- Weak guardrail safe: {robustness.get('weak_guardrail_safe', False)}",
        f"- Architecture robust: {robustness.get('architecture_robust', False)}",
        "",
        "### Phase 576 Comparison",
        "",
        f"- Phase 576 best (AMB_PESSIMISTIC): A2 delta={p576_comp.get('p576_a2_delta', 0):.4f}",
        f"- Phase 578 best ({best_config}): A2 delta={p576_comp.get('p578_a2_delta', 0):.4f}",
        f"- Improvement: {p576_comp.get('improvement', 0):+.4f}",
        "",
        "## T4: Landscape + Migration",
        "",
        f"- A2 FORGIVING: {n_forg_ungated} -> {n_forg_gated} ({pole_reduction:.1f}% reduction)",
        f"- Migrating folios: {n_migrating}",
        f"- New A1/A3 FORGIVING: {new_a1a3}",
    ])

    # Phase 576 landscape comparison
    p576_lc = t4.get('p576_comparison', {})
    if p576_lc:
        report_lines.extend([
            "",
            f"- Phase 576 A2 FORGIVING gated: {p576_lc.get('p576_a2_forgiving_gated', '?')}",
            f"- Phase 578 A2 FORGIVING gated: {p576_lc.get('p578_a2_forgiving_gated', '?')}",
        ])

    report_lines.extend([
        "",
        "## Tier 3 Interpretation",
        "",
    ])

    if all_validated:
        report_lines.append(
            "> The event-local closure adjudicator validates the expert diagnosis: "
            "closure legitimacy is event-local, determined by whether the CLOSE event "
            "actually resolved containment burden. Burden resolution (burden_frac_resolved) "
            "discriminates DYE advantage with meaningful effect size. The 4-class event "
            "taxonomy (AUTHENTIC_RESOLVER, PARTIAL_RESOLVER, NONRESOLVING_COUNTERFEIT, "
            "INERT_PSEUDO) outperforms Phase 576's 6-class morphological taxonomy, "
            "achieving >= 80% strong-band preservation while maintaining or improving "
            "A2 delta advantage. The A2 forgiving pole begins to shrink."
        )
    else:
        failing = []
        if c1659_verdict != 'COVERAGE_VALIDATED':
            failing.append(f"C1659={c1659_verdict}")
        if c1660_verdict != 'EVENT_GATING_VALIDATED':
            failing.append(f"C1660={c1660_verdict}")
        if c1661_verdict != 'DISCRIMINATOR_CONFIRMED':
            failing.append(f"C1661={c1661_verdict}")
        if c1662_verdict != 'MIGRATION_DETECTED':
            failing.append(f"C1662={c1662_verdict}")

        report_lines.append(
            f"> Tier 3 interpretation NOT frozen. Non-validated: {', '.join(failing)}. "
            f"Strong-band preservation={best_strong_pct:.1f}% "
            f"(target >=80%, Phase 576 baseline={lcc_strong:.1f}%). "
            f"Further investigation needed."
        )

    report_lines.extend(["", f"*Generated: {datetime.now(timezone.utc).isoformat()}*", ""])

    report_path = os.path.join(PHASE_DIR, 'REPORT_578.md')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"  Wrote {report_path}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '578',
            'script': 't5_event_local_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'verdicts': verdicts,
        'constraints': constraints,
        'all_validated': all_validated,
        'best_config': best_config,
        'best_SSI': round(best_ssi, 4),
        'best_a2_delta': round(best_a2_delta, 6),
        'best_strong_preserved_pct': round(best_strong_pct, 1),
        'config_robustness': {
            'assessment': 'ARCHITECTURE_ROBUST' if robustness.get('architecture_robust') else 'SPECIFIC',
            'per_config_SSI': per_config_ssi,
            'n_beat_lcc': robustness.get('n_beat_lcc', 0),
            'n_beat_credit': robustness.get('n_beat_credit', 0),
        },
        'p576_comparison': p576_comp,
    }

    out_path = os.path.join(RESULTS_DIR, 't5_event_local_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
