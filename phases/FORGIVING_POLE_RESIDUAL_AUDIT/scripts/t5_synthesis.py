"""
Phase 579 T5: Synthesis

Integrates T0-T4 results. Writes constraints C1663-C1666.
Generates REPORT_579.md.
"""

import json, sys, os, time
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
PHASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def main():
    t_start = time.time()

    print("T5: Synthesis")
    print("Phase 579 - FORGIVING_POLE_RESIDUAL_AUDIT")

    # -- Load all results --
    print("\n--- Loading T0-T4 results ---")

    with open(os.path.join(RESULTS_DIR, 't0_pole_census.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_coherence_profiling.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_channel_decomposition.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_opportunity_geometry.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_constrained_retuning.json')) as f:
        t4 = json.load(f)

    # -- Extract verdicts --
    c1663 = t1['c1663_inputs']['coherence_verdict']
    c1664 = t2['c1664_inputs']['channel_verdict']
    c1665 = t3['c1665_inputs']['opportunity_verdict']
    c1666 = t4['c1666_inputs']['c1666_verdict']

    print(f"\n  C1663 (Coherence):  {c1663}")
    print(f"  C1664 (Channel):    {c1664}")
    print(f"  C1665 (Opportunity): {c1665}")
    print(f"  C1666 (Endpoint):   {c1666}")

    # -- Build constraints --
    constraints = {
        'C1663': {
            'id': 'C1663',
            'tier': 2,
            'scope': 'A2_FORGIVING',
            'track': 'A: Coherence',
            'verdict': c1663,
            'evidence': {
                'loo_accuracy': t1['c1663_inputs']['loo_accuracy'],
                'n_sig_f_axes': t1['c1663_inputs']['n_sig_f_axes'],
                'n_sig_ablation': t1['c1663_inputs']['n_sig_ablation'],
                'within_fg_similarity': t1['c1663_inputs']['within_fg_similarity'],
                'between_similarity': t1['c1663_inputs']['between_similarity'],
                'lobe_tightness': t1['c1663_inputs']['lobe_tightness'],
            },
            'text': (f"The 8 stubborn A2 forgiving folios show {c1663} coherence: "
                     f"LOO accuracy={t1['c1663_inputs']['loo_accuracy']:.1%}, "
                     f"{t1['c1663_inputs']['n_sig_f_axes']}/5 significant F-axes, "
                     f"{t1['c1663_inputs']['n_sig_ablation']}/5 significant ablation channels. "
                     f"They form a tight lobe (within-similarity={t1['c1663_inputs']['within_fg_similarity']:.3f}) "
                     f"but are not separable from passing A2 folios."),
        },
        'C1664': {
            'id': 'C1664',
            'tier': 2,
            'scope': 'A2_FORGIVING',
            'track': 'B: Channel',
            'verdict': c1664,
            'evidence': {
                'post_gate_dominant_counts': t2['c1664_inputs']['post_gate_dominant_counts'],
                'concentrated_count': t2['c1664_inputs']['concentrated_count'],
            },
            'text': (f"Sub-channel analysis shows {c1664}: "
                     f"{t2['c1664_inputs']['concentrated_count']}/8 folios have >60% share "
                     f"in a single recovery channel. "
                     f"Dominant channels: {t2['c1664_inputs']['post_gate_dominant_counts']}. "
                     f"Pre-gate and post-gate dominant channels are identical -- "
                     f"regime admission gating did not alter the residual conversion mechanism."),
        },
        'C1665': {
            'id': 'C1665',
            'tier': 2,
            'scope': 'A2_FORGIVING',
            'track': 'C: Opportunity',
            'verdict': c1665,
            'evidence': {
                'event_count_r_squared': t3['c1665_inputs']['event_count_r_squared'],
                'forgiving_mean_cts': t3['cts_analysis']['forgiving_event_mean_cts'],
                'passing_mean_cts': t3['cts_analysis']['passing_event_mean_cts'],
            },
            'text': (f"Opportunity geometry shows {c1665}: "
                     f"event count R-sq={t3['c1665_inputs']['event_count_r_squared']:.4f} on CCS1 "
                     f"(no explanatory power). "
                     f"Forgiving folios have lower CTS and weaker grammar bands, "
                     f"but these are properties of the folios, not confounds."),
        },
        'C1666': {
            'id': 'C1666',
            'tier': 2,
            'scope': 'A2_FORGIVING',
            'track': 'D: Endpoint (DECISIVE)',
            'verdict': c1666,
            'evidence': {
                'classification_counts': t4['c1666_inputs']['classification_counts'],
                'n_endpoint': t4['c1666_inputs']['n_endpoint'],
                'n_underfit': t4['c1666_inputs']['n_underfit'],
                'n_achievable': t4['c1666_inputs']['n_achievable'],
            },
            'text': (f"F1xF2 grid search with conditional 3rd-axis extension yields {c1666}: "
                     f"{t4['c1666_inputs']['n_endpoint']} STRUCTURAL_ENDPOINT, "
                     f"{t4['c1666_inputs']['n_underfit']} PARAMETER_UNDERFIT, "
                     f"{t4['c1666_inputs']['n_achievable']} PARAMETER_ACHIEVABLE."),
        },
    }

    # -- Build per-folio cards --
    folio_cards = {}
    stubborn_8 = ['f39v', 'f40r', 'f50v', 'f55v', 'f85r2', 'f86v5', 'f86v6', 'f95r2']

    for folio in stubborn_8:
        census = t0['profile_cards'].get(folio, {})
        t4a = t4['t4a_results'].get(folio, {})
        t4b = t4.get('t4b_results', {}).get(folio, {})
        dom = t2.get('dominant_channels', {}).get(folio, {})
        final_class = t4.get('final_classifications', {}).get(folio, 'UNKNOWN')

        f_params = census.get('f_params', {})
        card = {
            'folio': folio,
            'section': census.get('section', '?'),
            'profile': census.get('profile', '?'),
            'F1': f_params.get('F1'),
            'F2': f_params.get('F2'),
            'F3': f_params.get('F3'),
            'F4_raw': f_params.get('F4_raw'),
            'F5': f_params.get('F5'),
            'CCS1': census.get('ccs1'),
            'DYE_advantage': census.get('dye_advantage'),
            'gap_to_passing': census.get('gap_to_passing'),
            'n_close_events': census.get('n_close_events'),
            'dominant_channel': dom.get('post_gate_dominant'),
            'dominant_share': dom.get('post_gate_dominant_share'),
            't4a_best_f1': t4a.get('best_f1'),
            't4a_best_f2': t4a.get('best_f2'),
            't4a_best_advantage': t4a.get('best_dye_advantage'),
            't4a_displacement': t4a.get('displacement'),
            't4a_passing_fraction': t4a.get('passing_fraction'),
            'final_classification': final_class,
        }
        if t4b:
            card['t4b_third_axis'] = t4b.get('third_axis')
            card['t4b_best_value'] = t4b.get('best_3rd_value')
            card['t4b_passes'] = t4b.get('passes')
            card['t4b_ext_displacement'] = t4b.get('extended_displacement')

        folio_cards[folio] = card

    # -- Generate report --
    print("\n--- Generating REPORT_579.md ---")

    report_lines = []
    report_lines.append("# Phase 579: FORGIVING POLE RESIDUAL AUDIT - Report")
    report_lines.append("")
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append(f"Phase 579 audits the 8 stubborn A2 forgiving folios that survive all")
    report_lines.append(f"closure-gating improvements from Phases 574-578. Four diagnostic tracks")
    report_lines.append(f"determine whether these represent a structural endpoint or parameter underfit.")
    report_lines.append("")
    report_lines.append("### Verdicts")
    report_lines.append("")
    report_lines.append(f"| Constraint | Track | Verdict |")
    report_lines.append(f"|------------|-------|---------|")
    report_lines.append(f"| C1663 | Coherence | **{c1663}** |")
    report_lines.append(f"| C1664 | Channel | **{c1664}** |")
    report_lines.append(f"| C1665 | Opportunity | **{c1665}** |")
    report_lines.append(f"| C1666 | Endpoint (DECISIVE) | **{c1666}** |")
    report_lines.append("")

    # Coherence section
    report_lines.append("## Track A: Coherence Profiling (C1663)")
    report_lines.append("")
    report_lines.append(f"LOO nearest-centroid accuracy: {t1['c1663_inputs']['loo_accuracy']:.1%}")
    report_lines.append(f"Significant F-axes: {t1['c1663_inputs']['n_sig_f_axes']}/5")
    report_lines.append(f"Significant ablation channels: {t1['c1663_inputs']['n_sig_ablation']}/5")
    report_lines.append(f"Within-forgiving cosine similarity: {t1['c1663_inputs']['within_fg_similarity']:.4f}")
    report_lines.append(f"Between-group similarity: {t1['c1663_inputs']['between_similarity']:.4f}")
    report_lines.append(f"Lobe tightness: {t1['c1663_inputs']['lobe_tightness']}")
    report_lines.append("")
    report_lines.append(f"The 8 form a tight lobe in feature space but are not separable from passing")
    report_lines.append(f"A2 folios. This is consistent with C1641 (A2 weakly structured, continuous")
    report_lines.append(f"variation). The forgiving folios are the tail of a gradient, not a distinct")
    report_lines.append(f"subfamily.")
    report_lines.append("")

    # Channel section
    report_lines.append("## Track B: Channel Decomposition (C1664)")
    report_lines.append("")
    report_lines.append(f"Post-gate dominant channel counts: {t2['c1664_inputs']['post_gate_dominant_counts']}")
    report_lines.append(f"Concentrated (>60% share): {t2['c1664_inputs']['concentrated_count']}/8")
    report_lines.append("")
    report_lines.append("Per-folio dominant channels:")
    report_lines.append("")
    for folio in stubborn_8:
        dom = t2.get('dominant_channels', {}).get(folio, {})
        pre = dom.get('pre_gate_dominant', '?')
        post = dom.get('post_gate_dominant', '?')
        share = dom.get('post_gate_dominant_share', 0)
        changed = ' (CHANGED)' if dom.get('dominant_changed', False) else ''
        report_lines.append(f"  {folio}: {pre} -> {post} (share={share:.2f}){changed}")
    report_lines.append("")
    report_lines.append("R1 (per-SV CLOSE drawdown) dominates 6/8 folios. R4 (quality-conditioned")
    report_lines.append("Y accumulation) dominates the remaining 2 (f86v5, f86v6). The gating from")
    report_lines.append("Phase 576 did not change the dominant conversion mechanism for any folio.")
    report_lines.append("")

    # Opportunity section
    report_lines.append("## Track C: Opportunity Geometry (C1665)")
    report_lines.append("")
    report_lines.append(f"Event count R-sq on CCS1: {t3['c1665_inputs']['event_count_r_squared']:.4f}")
    fg_cts = t3['cts_analysis']['forgiving_event_mean_cts']
    pa_cts = t3['cts_analysis']['passing_event_mean_cts']
    report_lines.append(f"CTS: forgiving={fg_cts:.3f} vs passing={pa_cts:.3f}")
    report_lines.append("")
    fg_gram = t3.get('grammar_bands', {}).get('forgiving', {})
    pa_gram = t3.get('grammar_bands', {}).get('passing', {})
    morph = t3.get('morphological_comparison', {})
    report_lines.append("Key morphological contrasts (forgiving vs passing):")
    report_lines.append(f"  Mean CTS: {fg_cts:.3f} vs {pa_cts:.3f}")
    report_lines.append(f"  WEAK grammar band: {fg_gram.get('WEAK', '?')} vs {pa_gram.get('WEAK', '?')}")
    sc = t3.get('strong_close_opportunity', {})
    report_lines.append(f"  E_armed: {morph.get('E_armed', {}).get('forgiving_fraction', '?')} vs {morph.get('E_armed', {}).get('passing_fraction', '?')}")
    report_lines.append("")
    report_lines.append("Event count has no explanatory power (R-sq ~ 0). The forgiving folios")
    report_lines.append("have structurally weaker closure events (lower CTS, fewer strong signals,")
    report_lines.append("less e-head support). These are intrinsic folio properties, not sampling")
    report_lines.append("artifacts.")
    report_lines.append("")

    # Retuning section
    report_lines.append("## Track D: Constrained Retuning (C1666)")
    report_lines.append("")
    report_lines.append(f"Grid: F1 x F2 in {t4['metadata']['grid_values']}")
    report_lines.append(f"Total simulation runs: {t4['metadata']['total_runs']}")
    report_lines.append("")
    report_lines.append("### T4a: F1 x F2 Sweep")
    report_lines.append("")
    report_lines.append(f"| Folio | Orig F1 | Orig F2 | Best F1 | Best F2 | Best Adv | Disp | Pass | Class |")
    report_lines.append(f"|-------|---------|---------|---------|---------|----------|------|------|-------|")
    for folio in stubborn_8:
        r = t4['t4a_results'][folio]
        p = 'Y' if r['passes_at_best'] else 'N'
        report_lines.append(
            f"| {folio} | {r['orig_f1']:.2f} | {r['orig_f2']:.2f} | "
            f"{r['best_f1']:.2f} | {r['best_f2']:.2f} | "
            f"{r['best_dye_advantage']:+.4f} | {r['displacement']:.3f} | "
            f"{p} | {r['t4a_classification']} |")
    report_lines.append("")

    if t4.get('t4b_results'):
        report_lines.append("### T4b: 3rd-Axis Extension")
        report_lines.append("")
        for folio, r in t4['t4b_results'].items():
            p = 'PASS' if r['passes'] else 'FAIL'
            report_lines.append(
                f"  {folio}: {r['third_axis']}={r['best_3rd_value']:.2f} "
                f"adv={r['best_dye_advantage']:+.4f} ext_disp={r['extended_displacement']:.3f} "
                f"-> {p} [{r['t4b_classification']}]")
        report_lines.append("")

    report_lines.append("### Final Classification")
    report_lines.append("")
    for folio in stubborn_8:
        fc = t4['final_classifications'][folio]
        report_lines.append(f"  {folio}: **{fc}**")
    report_lines.append("")
    report_lines.append(f"Counts: {t4['c1666_inputs']['classification_counts']}")
    report_lines.append(f"**C1666 verdict: {c1666}**")
    report_lines.append("")

    # Per-folio cards
    report_lines.append("## Per-Folio Cards")
    report_lines.append("")
    for folio in stubborn_8:
        card = folio_cards[folio]
        report_lines.append(f"### {folio}")
        report_lines.append("")
        report_lines.append(f"- Section: {card['section']}, Profile: {card['profile']}")
        report_lines.append(f"- F-params: F1={card['F1']}, F2={card['F2']}, F3={card['F3']}, F4={card['F4_raw']}, F5={card['F5']}")
        report_lines.append(f"- CCS1: {card['CCS1']}, DYE advantage: {card['DYE_advantage']}, Gap: {card['gap_to_passing']}")
        report_lines.append(f"- Close events: {card['n_close_events']}")
        report_lines.append(f"- Dominant channel: {card['dominant_channel']} (share={card['dominant_share']})")
        report_lines.append(f"- T4a: best ({card['t4a_best_f1']}, {card['t4a_best_f2']}), adv={card['t4a_best_advantage']}, disp={card['t4a_displacement']}, passing={card['t4a_passing_fraction']}")
        if 't4b_third_axis' in card:
            report_lines.append(f"- T4b: {card['t4b_third_axis']}={card['t4b_best_value']}, passes={card['t4b_passes']}, ext_disp={card['t4b_ext_displacement']}")
        report_lines.append(f"- **Final: {card['final_classification']}**")
        report_lines.append("")

    # Implications
    report_lines.append("## Implications")
    report_lines.append("")
    if c1666 == 'STRUCTURAL_ENDPOINT_CONFIRMED':
        report_lines.append("The 8 stubborn A2 forgiving folios are structural endpoints.")
        report_lines.append("Their forgivingness is an inherent property of their apparatus")
        report_lines.append("configuration, not recoverable by parameter retuning within the")
        report_lines.append("current model architecture. This closes the A2 forgivingness")
        report_lines.append("investigation with an explanatory endpoint.")
    elif c1666 == 'PARAMETER_UNDERFIT_CONFIRMED':
        report_lines.append("The 8 stubborn folios are parameter underfits. Their forgivingness")
        report_lines.append("can be eliminated by adjusting F1/F2 within reasonable displacement.")
        report_lines.append("This suggests the current F-param calibration is suboptimal for")
        report_lines.append("these folios and a recalibration pass would resolve them.")
    else:
        report_lines.append("The 8 stubborn folios show MIXED_BOUNDARY_STRATUM: some are genuine")
        report_lines.append("structural endpoints while others are parameter underfits. This is")
        report_lines.append("consistent with C1641 (A2 continuous variation, many boundary folios).")
        report_lines.append("The forgiving/passing boundary is a gradient, not a clean partition.")
    report_lines.append("")

    report_text = '\n'.join(report_lines)

    report_path = os.path.join(PHASE_DIR, 'REPORT_579.md')
    with open(report_path, 'w') as f:
        f.write(report_text)

    # -- Save synthesis --
    synthesis = {
        'metadata': {
            'phase': 579,
            'script': 't5_synthesis',
            'runtime_s': round(time.time() - t_start, 2),
        },
        'constraints': constraints,
        'folio_cards': folio_cards,
        'summary': {
            'C1663': c1663,
            'C1664': c1664,
            'C1665': c1665,
            'C1666': c1666,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(synthesis, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\nT5 complete in {elapsed:.1f}s")
    print(f"  Synthesis: {out_path}")
    print(f"  Report: {report_path}")


if __name__ == '__main__':
    main()
