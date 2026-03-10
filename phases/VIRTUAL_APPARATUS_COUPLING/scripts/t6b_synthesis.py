"""
T6b: Phase 563b Synthesis — Aggregate T5b validation, produce verdict and report.

Phase 563b attempted three targeted refinements to the Phase 563 apparatus coupling:
  1. Routing as cumulative within-line bias (not punctual deflection)
  2. Plant oscillation recalibration (reduced decay, stronger cross-coupling)
  3. Headless as infrastructure parameterization (folio-level, not per-token)

Result: COUPLING_FAILED (3/9 pass, down from 5/9 in Phase 563).
No new constraints created. 563 constraints (C1581-C1587) remain valid.

Inputs:
  - t5b_plant_validation.json
  - t3b_coupled_traces.json
  - t4b_null_ablation_traces.json

Output:
  - t6b_synthesis.json
  - REPORT_563b.md
"""

import json
import os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')


def load_json(name):
    with open(os.path.join(RESULTS_DIR, name)) as f:
        return json.load(f)


def extract_key_metric(name, test):
    d = test['details']
    if name == 'P1_viable_envelope':
        return f"full>B2: {d['full_gt_B2']}/20, full>N1: {d['full_gt_N1']}/20"
    elif name == 'P2_packet_shape':
        return f"global KW sig: {d['global_n_sig']}/7 vars"
    elif name == 'P3_section_template':
        return f"KW sig: {d['n_sig']}/7 vars (5 sections, SECONDARY)"
    elif name == 'P3b_productive_diversity':
        return (f"nontrivial pass: {d['n_nontrivial_pass']}/20, "
                f"mean excursions: {d['mean_excursions']:.1f}, "
                f"mean bounded: {d['mean_bounded_excursions']:.1f}")
    elif name == 'P4_routing_consequence':
        correct = [rt for rt, info in d['route_details'].items() if info['correct']]
        return f"correct routes: {d['n_correct_routes']}/4 ({', '.join(correct) if correct else 'none'})"
    elif name == 'P5_headless_regime':
        p5a = d.get('P5a', {})
        p5b = d.get('P5b', {})
        return (f"P5a C_better={p5a.get('n_C_better', 0)}/20, "
                f"S_better={p5a.get('n_S_better', 0)}/20; "
                f"P5b C p={p5b.get('C_test', {}).get('p', 1.0):.3f}")
    elif name == 'P6_cts_closure':
        p6a = d.get('P6a', {})
        p6b = d.get('P6b', {})
        return (f"viab better: {p6a.get('n_viab_better', 0)}/20, "
                f"sep+: {p6b.get('n_separation_positive', 0)}/20")
    elif name == 'P7_null_destruction':
        nulls_d = d.get('per_null', {})
        destroyed = [k.split('_')[0] for k, v in nulls_d.items() if v.get('null_pass')]
        return f"{d.get('n_null_pass', 0)}/4 nulls destroyed ({', '.join(destroyed) if destroyed else 'none'})"
    elif name == 'P8_preferred_profile':
        return f"preferred best on >=1 metric: {d.get('n_preferred_best', 0)}/20"
    return ''


def main():
    t5b = load_json('t5b_plant_validation.json')
    t3b = load_json('t3b_coupled_traces.json')
    t4b = load_json('t4b_null_ablation_traces.json')

    tests = t5b['tests']
    verdict = t5b['verdict']
    n_pass = t5b['summary']['n_pass']
    n_fail = t5b['summary']['n_fail']
    n_tests = t5b['metadata']['n_tests']
    pilot_folios = t5b['metadata']['pilot_folios']

    # Summary table
    test_names = [
        'P1_viable_envelope', 'P2_packet_shape', 'P3_section_template',
        'P3b_productive_diversity', 'P4_routing_consequence', 'P5_headless_regime',
        'P6_cts_closure', 'P7_null_destruction', 'P8_preferred_profile'
    ]

    summary_table = {}
    for tn in test_names:
        t = tests[tn]
        summary_table[tn] = {
            'pass': t['pass'],
            'key_metric': extract_key_metric(tn, t),
        }

    # Composite metrics
    ref = t4b['reference']
    ref_viabs = [ref[f]['viability_fraction'] for f in pilot_folios if f in ref]
    ref_Ys = [ref[f]['Y_final'] for f in pilot_folios if f in ref]
    total_haz = sum(ref[f]['hazard_count'] for f in pilot_folios if f in ref)

    mean_viab = sum(ref_viabs) / len(ref_viabs) if ref_viabs else 0
    mean_Y = sum(ref_Ys) / len(ref_Ys) if ref_Ys else 0

    composite = {
        'mean_viability': round(mean_viab, 4),
        'mean_Y_final': round(mean_Y, 4),
        'total_hazard_events': total_haz,
        'n_folios_perfect_viab': sum(1 for v in ref_viabs if v >= 0.999),
        'n_folios': len(ref_viabs),
    }

    # 563 vs 563b comparison
    comparison_563_vs_563b = {
        'P1': {'563': 'PASS (5/7 B2, 7/7 N1)', '563b': f"FAIL ({tests['P1_viable_envelope']['details']['full_gt_B2']}/20 B2, {tests['P1_viable_envelope']['details']['full_gt_N1']}/20 N1)"},
        'P2': {'563': 'PASS (7/7 sig)', '563b': f"PASS ({tests['P2_packet_shape']['details']['global_n_sig']}/7 sig)"},
        'P3': {'563': 'FAIL (0/7 sig, N=7)', '563b': f"FAIL ({tests['P3_section_template']['details']['n_sig']}/7 sig, N=20, SECONDARY)"},
        'P3b': {'563': 'FAIL (excursions=1.3)', '563b': f"FAIL (excursions={tests['P3b_productive_diversity']['details']['mean_excursions']:.1f})"},
        'P4': {'563': 'FAIL (0/4)', '563b': f"FAIL ({tests['P4_routing_consequence']['details']['n_correct_routes']}/4, improved)"},
        'P5': {'563': 'FAIL (p>0.05, N=3v4)', '563b': 'FAIL (P5a 11/20 C, P5b p>0.05)'},
        'P6': {'563': 'PASS', '563b': 'PASS'},
        'P7': {'563': 'PASS (3/4)', '563b': f"FAIL ({tests['P7_null_destruction']['details']['n_null_pass']}/4)"},
        'P8': {'563': 'PASS (5/7)', '563b': f"PASS ({tests['P8_preferred_profile']['details']['n_preferred_best']}/20)"},
    }

    # Diagnostic: what changed direction
    regressions = []
    improvements = []
    for test_key, comp in comparison_563_vs_563b.items():
        if 'PASS' in comp['563'] and 'FAIL' in comp['563b']:
            regressions.append(test_key)
        elif 'FAIL' in comp['563'] and 'PASS' in comp['563b']:
            improvements.append(test_key)

    # No new constraints — COUPLING_FAILED
    constraints_note = (
        "COUPLING_FAILED verdict: no new constraints created. "
        "Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. "
        "The recalibration attempt is a documented negative result."
    )

    # Lessons learned
    lessons = [
        "Decay reduction (30-40% on T/X) did NOT produce oscillation. "
        "Mean excursions stayed at 1.3 (identical to 563). The monotonic drift is structural, "
        "not a matter of parameter magnitude — the update equation itself cannot produce oscillation "
        "under the current architecture.",

        "Routing accumulator improved P4 from 0/4 to 2/4. m→C is strongly significant "
        "(p~0, delta=+0.065) and h→TR passes (p=0.007). The cumulative approach is directionally "
        "correct but r→X and y→T remain undetectable. The routing effect is domain-modulated, "
        "not purely terminal-dependent.",

        "A2 profile is systematically hostile: f55r, f39v, f66r, f85r1, f86v5, f86v6 all show "
        "hazard exposure under their preferred A2 profile. A1 achieves perfect viability for all "
        "20 folios regardless of assignment. The A2/A3 profiles may have structural sensitivity "
        "misalignment with the supervisory signal distribution.",

        "P7 regressed from 3/4 to 2/4 null types passing. N3 (line shuffle) and N4 (within-line "
        "shuffle) both fail at the 14/20 threshold. The routing accumulator adds within-line "
        "structure that the original model lacked, making N4 more destructive — but the 14/20 "
        "threshold is harder to reach than 5/7.",

        "P2 packet shape is robust: 7/7 state variables significant in both 563 and 563b. "
        "This is the most stable result across configurations, confirming line-level SPEC/WORK/CLOSE "
        "as the primary grammar-to-apparatus coupling channel.",

        "Headless modulation at folio level (C1574 compliance) produces weak effects. "
        "P5a shows C_better for 11/20 but S_better for only 1/20. The modulation direction "
        "is inconsistent — higher headless rate should increase both C and S sensitivity, "
        "but the effect on S is inverted (lower S in full model vs B6). This suggests the "
        "headless modulation function needs retuning or the relationship is non-monotonic.",
    ]

    # Assemble output
    output = {
        'metadata': {
            'phase': '563b',
            'task': 'T6b_synthesis',
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'verdict': verdict,
            'n_tests_total': n_tests,
            'n_tests_pass': n_pass,
            'n_tests_fail': n_fail,
            'n_constraints_proposed': 0,
            'pilot_folios': pilot_folios,
        },
        'verdict_rationale': (
            f'COUPLING_FAILED: {n_pass}/{n_tests} tests pass (down from 5/9 in Phase 563). '
            f'The three targeted refinements (routing accumulator, decay reduction, headless '
            f'modulation) did not improve the overall coupling verdict. P4 improved from 0/4 to '
            f'2/4, but P1 and P7 regressed from PASS to FAIL. P3b excursions remained at 1.3 '
            f'(decay reduction had no effect on oscillation dynamics). P5 remains underpowered. '
            f'The recalibration is a documented negative result: parametric tuning of the current '
            f'architecture cannot produce the oscillatory dynamics required by P3b.'
        ),
        'comparison_563_vs_563b': comparison_563_vs_563b,
        'regressions': regressions,
        'improvements': improvements,
        'composite_metrics': composite,
        'summary_table': summary_table,
        'constraints_note': constraints_note,
        'lessons_learned': lessons,
    }

    out_path = os.path.join(RESULTS_DIR, 't6b_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f'T6b synthesis written to {out_path}')
    print(f'Verdict: {verdict} ({n_pass}/{n_tests} pass)')
    print(f'Regressions from 563: {regressions}')
    print(f'Improvements from 563: {improvements}')
    print(f'Constraints proposed: 0 (COUPLING_FAILED)')
    print(f'Composite: mean viability={composite["mean_viability"]}, '
          f'mean Y={composite["mean_Y_final"]}, '
          f'hazard events={composite["total_hazard_events"]}')

    # Write REPORT_563b.md
    write_report(output, tests, composite, comparison_563_vs_563b, lessons)


def write_report(output, tests, composite, comparison, lessons):
    report_path = os.path.join(PHASE_DIR, 'REPORT_563b.md')

    # Use UTF-8 encoding for report output
    lines = []
    lines.append("# Phase 563b: Routing Accumulation and Dynamic Recalibration")
    lines.append("")
    lines.append("**Phase:** 563b (recalibration of 563)")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Verdict:** {output['metadata']['verdict']} ({output['metadata']['n_tests_pass']}/{output['metadata']['n_tests_total']} tests pass)")
    lines.append("**New constraints:** None (negative result)")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("Phase 563b attempted three targeted refinements to the Phase 563 apparatus coupling:")
    lines.append("")
    lines.append("1. **Routing as cumulative within-line bias** -- routing accumulator with exponential decay (ROUTING_DECAY=0.7, ROUTING_GAIN=0.5), modulating sensitivity multiplicatively, reset at line boundaries (C1470)")
    lines.append("2. **Plant oscillation recalibration** -- decay reductions (30-40% on T/X) and cross-coupling strengthening (alpha_YX, alpha_FC) to encourage oscillation instead of monotonic drift")
    lines.append("3. **Headless as infrastructure parameterization** -- folio-level profile modulation (C/S sensitivity, C/S decay, alpha_XC) based on headless rate, plus halved per-token headless magnitudes (C1574)")
    lines.append("")
    lines.append("All three changes were run on an expanded 20-folio pilot set (up from 7 in Phase 563), covering 5 sections (B:4, H:7, S:5, T:2, C:2), 3 profiles, and HL rates 0.163-0.403.")
    lines.append("")
    lines.append("**Result: COUPLING_FAILED.** The recalibration made the overall verdict worse (3/9 pass, down from 5/9 in 563). P4 routing improved from 0/4 to 2/4, but P1 and P7 regressed from PASS to FAIL. The fundamental oscillation problem (P3b) was unaffected by decay reduction.")
    lines.append("")

    lines.append("## Results")
    lines.append("")
    lines.append("| Test | 563 | 563b | Key Finding |")
    lines.append("|------|-----|------|-------------|")
    for test_key in ['P1', 'P2', 'P3', 'P3b', 'P4', 'P5', 'P6', 'P7', 'P8']:
        c563 = comparison.get(test_key, {}).get('563', '?')
        c563b = comparison.get(test_key, {}).get('563b', '?')
        # Extract the pass/fail and metric
        test_name = {
            'P1': 'P1_viable_envelope', 'P2': 'P2_packet_shape',
            'P3': 'P3_section_template', 'P3b': 'P3b_productive_diversity',
            'P4': 'P4_routing_consequence', 'P5': 'P5_headless_regime',
            'P6': 'P6_cts_closure', 'P7': 'P7_null_destruction',
            'P8': 'P8_preferred_profile',
        }[test_key]
        metric = output['summary_table'][test_name]['key_metric']
        status = 'PASS' if tests[test_name]['pass'] else 'FAIL'
        secondary = ' (SEC)' if test_key == 'P3' else ''
        lines.append(f"| {test_key} | {c563.split('(')[0].strip()} | **{status}**{secondary} | {metric} |")
    lines.append("")

    lines.append("### Composite Metrics")
    lines.append("")
    lines.append("| Metric | 563 | 563b |")
    lines.append("|--------|-----|------|")
    lines.append(f"| Mean viability | 0.9616 | {composite['mean_viability']} |")
    lines.append(f"| Mean Y_final | 0.878 | {composite['mean_Y_final']:.3f} |")
    lines.append(f"| Total hazard events | 34 | {composite['total_hazard_events']} |")
    lines.append(f"| Folios with perfect viability | 4/7 | {composite['n_folios_perfect_viab']}/{composite['n_folios']} |")
    lines.append("")

    lines.append("## Analysis")
    lines.append("")

    lines.append("### Why the recalibration failed")
    lines.append("")
    lines.append("**P3b excursions (unchanged at 1.3):** The decay reduction hypothesis was that lower decay on T and X would allow these variables to excurse further from equilibrium before returning, producing oscillation. Instead, the plant simply enters a regime further from equilibrium and stays there. Mean nontrivial fraction is 0.96 (high -- the plant IS working) but excursion count remains ~1 (the plant never returns to baseline). This is a monotonic drift problem, not a parametric tuning problem. The update equation `V[n+1] = clamp(V[n] + dV + coupling - decay*(V[n]-0.5))` has no mechanism for reversal once cumulative dV pushes past the decay equilibrium zone.")
    lines.append("")
    lines.append("**P1 regression (12/20 vs 5/7):** Eight folios now have REF viability below B2 (folio-mean baseline). All are A2 or A3 preferred folios (f55r, f39v, f111r, f108v, f66r, f85r1, f86v5, f86v6). The recalibrated profiles have lower decay, meaning state variables drift further from equilibrium and more easily violate hazard boundaries. B2 (constant folio-mean contributions) trivially achieves viability=1.0 because the mean contribution doesn't push the plant far enough to violate boundaries. The full model's token-level variation, combined with lower decay, causes occasional hazard violations that the original profiles avoided.")
    lines.append("")
    lines.append("**P7 regression (2/4 vs 3/4):** N3 (line shuffle) now fails at 7/20 (was 3/7). N4 (within-line shuffle) now fails at 11/20 (was 5/7). The higher threshold (14/20 vs 5/7) is harder to reach, but the regression is real: with the routing accumulator adding within-line structure, shuffling within lines (N4) should be MORE destructive, not less. The issue is that the routing accumulator's effect is small (ROUTING_GAIN=0.5 * (mult-1.0) ~ 0.1-0.2) and gets overwhelmed by the dominant effect of token composition.")
    lines.append("")

    lines.append("### What improved")
    lines.append("")
    lines.append("**P4 routing (2/4 vs 0/4):** The cumulative between-subjects design detected two genuine routing effects:")
    lines.append("")
    p4d = tests['P4_routing_consequence']['details']['route_details']
    for rt, info in p4d.items():
        status = 'CORRECT' if info['correct'] else 'WRONG'
        lines.append(f"- **{rt}→{info['target_sv']}:** A_mean={info['group_a_mean']:.4f}, "
                      f"B_mean={info['group_b_mean']:.4f}, delta={info['delta']:+.4f}, "
                      f"p={info['p']:.5f} → {status}")
    lines.append("")
    lines.append("The m→C effect (delta=+0.065, p~0) is the strongest routing signal in the system. "
                  "The h→TR effect is significant but weaker. r→X shows directional correctness but "
                  "fails significance. y→T shows no effect. This suggests routing operates selectively: "
                  "containment-related routing (m, h) is detectable while transition/thermal routing "
                  "(r, y) is absorbed into broader domain dynamics.")
    lines.append("")

    lines.append("**P8 profile superiority (14/20 PASS):** Despite A2's hazard issues, "
                  "preferred profiles are still best on at least one metric (viability, hazard count, "
                  "or Y_final) for 14/20 folios. This passes the expanded threshold, confirming "
                  "that section-to-profile assignment captures real apparatus differentiation.")
    lines.append("")

    lines.append("### Stable results")
    lines.append("")
    lines.append("**P2 packet shape (7/7 in both):** Line packet phases produce strongly differentiated "
                  "plant states regardless of parameterization. This is the most robust coupling signal.")
    lines.append("")
    lines.append("**P6 CTS closure (PASS in both):** CTS adds genuine value (viability better for "
                  "14/20, C-separation positive for 15/20). This validates CTS as a permanent feature "
                  "of the trace-apparatus interface.")
    lines.append("")

    lines.append("## Lessons Learned")
    lines.append("")
    for i, lesson in enumerate(lessons, 1):
        lines.append(f"{i}. {lesson}")
        lines.append("")

    lines.append("## Constraints")
    lines.append("")
    lines.append("No new constraints created (COUPLING_FAILED verdict).")
    lines.append("")
    lines.append("Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. "
                  "The 563b recalibration is a documented negative result that does not invalidate "
                  "the original coupling findings.")
    lines.append("")

    lines.append("## Implications for Next Phase")
    lines.append("")
    lines.append("1. **Oscillation requires architectural change, not parametric tuning.** The update equation "
                  "`V[n+1] = clamp(V[n] + dV + coupling - decay*(V-0.5))` cannot produce reversal dynamics. "
                  "Consider: (a) feedback-dependent decay that increases when variables are far from equilibrium, "
                  "(b) state-dependent contribution gating, or (c) explicit return-to-equilibrium forces triggered "
                  "by line/paragraph boundaries.")
    lines.append("2. **Restore original 563 parameters.** The recalibrated profiles cause more hazard violations "
                  "without improving oscillation. Revert to 563 parameters for any future coupling work.")
    lines.append("3. **Routing accumulator is directionally correct for m→C and h→TR.** Keep the cumulative "
                  "routing design but investigate why r→X and y→T don't produce detectable effects.")
    lines.append("4. **A2 profile needs fundamental rethinking.** A2 creates systematic hazard exposure for "
                  "6/20 pilot folios. The sensitivity pattern (high C sensitivity=1.4) combined with the "
                  "supervisory signal distribution creates containment boundary violations. Consider: "
                  "(a) constraining A2 sensitivity range, (b) re-examining A2 assignment criteria, or "
                  "(c) accepting that A2 represents a genuinely dangerous operating regime that should "
                  "produce hazard exposure.")
    lines.append("5. **20-folio pilot set is adequate for most tests** but T and C sections (2 folios each) "
                  "are still underpowered for section-level analysis.")
    lines.append("")

    lines.append("## Scripts")
    lines.append("")
    lines.append("| Script | Purpose | Output |")
    lines.append("|--------|---------|--------|")
    lines.append("| t1b_apparatus_recalibration.py | Recalibrate 3 profiles, add headless modulation | t1b_apparatus_recalibrated.json |")
    lines.append("| t2b_unrouted_supervisory_interface.py | Remove baked-in routing, halve headless magnitudes | t2b_supervisory_interface_unrouted.json |")
    lines.append("| t3b_accumulated_trace_executor.py | Run 20 folios x 3 profiles with routing accumulator | t3b_coupled_traces.json |")
    lines.append("| t4b_null_and_ablation_executor.py | 6 baselines + 4 nulls x 50 perms = 4,140 runs | t4b_null_ablation_traces.json |")
    lines.append("| t5b_plant_behavior_validation.py | 9-test validation battery (8 tests + P3 secondary) | t5b_plant_validation.json |")
    lines.append("| t6b_synthesis.py | Aggregate results, comparison, report | t6b_synthesis.json |")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'REPORT_563b.md written to {report_path}')


if __name__ == '__main__':
    main()
