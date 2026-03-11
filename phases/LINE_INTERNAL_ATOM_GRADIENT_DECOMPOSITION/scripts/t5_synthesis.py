"""T5: Synthesis for Phase 581.

Load T1-T4 results, write C1671-C1674, generate REPORT_581.md.
"""
import json, os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_atom_positional_gradients.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_q3q4_decomposition.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_hazard_atom_position.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_section_conditioned_gradients.json')) as f:
        t4 = json.load(f)

    constraints = {
        'C1671': t1['C1671'],
        'C1672': t2['C1672'],
        'C1673': t3['C1673'],
        'C1674': t4['C1674'],
    }

    # Write synthesis JSON
    synthesis = {
        'metadata': {
            'phase': '581',
            'script': 't5_synthesis.py',
            'n_tokens': t0['metadata']['n_tokens'],
            'n_lines': t0['metadata']['n_lines'],
        },
        'constraints': constraints,
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(synthesis, f, indent=2)

    # ---- Generate REPORT_581.md ----
    n = t0['metadata']['n_tokens']
    n_lines = t0['metadata']['n_lines']
    q_counts = t0['summary']['quintile_counts']

    # T1 data
    head_chi2 = t1['head_profiles']['chi_squared']
    head_p = t1['head_profiles']['p_value']
    term_chi2 = t1['terminal_profiles']['chi_squared']
    term_p = t1['terminal_profiles']['p_value']
    mod_chi2 = t1['modifier_profiles']['chi_squared']
    mod_p = t1['modifier_profiles']['p_value']
    min_cosine = t1['gradient_heterogeneity']['min_head_cosine']
    predictions = t1['predictions']
    pred_passed = t1['predictions_passed']
    carryover = t1['carryover_cross_reference']

    # T2 data
    q3q4 = t2['all_transitions']['Q3->Q4']
    q0q1 = t2['all_transitions']['Q0->Q1']
    q1q2 = t2['all_transitions']['Q1->Q2']
    q2q3 = t2['all_transitions']['Q2->Q3']
    cross_cos = t2['cross_transition_cosines']
    head_rate_changes = t2['rate_changes']['head_Q3_to_Q4']
    term_rate_changes = t2['rate_changes']['term_Q3_to_Q4']

    # T3 data
    interaction_chi2 = t3['interaction_test']['chi_squared']
    interaction_p = t3['interaction_test']['p_value']
    zone_pairs = t3['zone_specific_pairs']
    thermal = t3['thermal_cluster_comparison']
    zero_profiles = t3['zero_frame_profiles']

    # T4 data
    sections = t4['section_results']
    aggregate = t4['aggregate']

    report = []
    report.append("# Phase 581: Line-Internal Atom Gradient Decomposition")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append(f"Analyzed {n:,} Currier B tokens across {n_lines:,} lines to decompose "
                  "the validated three-zone line architecture (C1425-C1430) at individual "
                  "atom resolution. All four target constraints decided.")
    report.append("")
    report.append("| ID | Verdict | Key Metric |")
    report.append("|----|---------|------------|")
    for cid, cdata in constraints.items():
        report.append(f"| {cid} | {cdata['verdict']} | {cdata['rationale'][:80]} |")
    report.append("")

    # Data Quality
    report.append("## Data Assembly")
    report.append("")
    report.append(f"- **Tokens:** {n:,}")
    report.append(f"- **Lines:** {n_lines:,}")
    report.append(f"- **Quintile distribution:** {q_counts}")
    report.append(f"- **Quality:** {t0['quality']}")
    report.append("")

    # HEAD Profiles
    report.append("## HEAD Atom Positional Profiles")
    report.append("")
    report.append(f"Chi-squared: {head_chi2} (df={t1['head_profiles']['df']}, p={head_p})")
    report.append(f"Min pairwise cosine: {min_cosine}")
    report.append("")
    report.append("### Enrichment Table (rate / marginal)")
    report.append("")
    report.append("| HEAD | Q0 | Q1 | Q2 | Q3 | Q4 | Range |")
    report.append("|------|-----|-----|-----|-----|-----|-------|")
    head_enrich = t1['head_profiles']['enrichment']
    head_ranges = t1['head_profiles']['ranges']
    for h in ['e', 'k', 'a', 'o', 't', 'headless']:
        vals = [head_enrich[h][str(q)] for q in range(5)]
        report.append(f"| {h} | {vals[0]:.3f} | {vals[1]:.3f} | {vals[2]:.3f} | "
                      f"{vals[3]:.3f} | {vals[4]:.3f} | {head_ranges[h]:.4f} |")
    report.append("")

    # Headless internal
    report.append("### Headless Internal Split (Pseudo-HEAD)")
    report.append("")
    hl = t1['headless_internal']
    report.append(f"N headless: {hl['n_headless']}, chi2={hl['chi_squared']} "
                  f"(df={hl['df']}, p={hl['p_value']})")
    if hl['pseudo_heads']:
        report.append("")
        report.append("| Pseudo-HEAD | Q0 | Q1 | Q2 | Q3 | Q4 |")
        report.append("|-------------|-----|-----|-----|-----|-----|")
        for ph in hl['pseudo_heads'][:8]:
            vals = [hl['enrichment'][ph][str(q)] for q in range(5)]
            report.append(f"| {ph} | {vals[0]:.3f} | {vals[1]:.3f} | {vals[2]:.3f} | "
                          f"{vals[3]:.3f} | {vals[4]:.3f} |")
    report.append("")

    # TERMINAL Profiles
    report.append("## TERMINAL Atom Positional Profiles")
    report.append("")
    report.append(f"Chi-squared: {term_chi2} (df={t1['terminal_profiles']['df']}, p={term_p})")
    report.append("")
    report.append("| TERMINAL | Q0 | Q1 | Q2 | Q3 | Q4 | Range |")
    report.append("|----------|-----|-----|-----|-----|-----|-------|")
    term_enrich = t1['terminal_profiles']['enrichment']
    term_ranges = t1['terminal_profiles']['ranges']
    for t_atom in TERMINALS:
        vals = [term_enrich[t_atom][str(q)] for q in range(5)]
        report.append(f"| {t_atom} | {vals[0]:.3f} | {vals[1]:.3f} | {vals[2]:.3f} | "
                      f"{vals[3]:.3f} | {vals[4]:.3f} | {term_ranges[t_atom]:.4f} |")
    report.append("")

    # MODIFIER Profiles
    report.append("## MODIFIER Atom Positional Profiles")
    report.append("")
    report.append(f"Chi-squared: {mod_chi2} (df={t1['modifier_profiles']['df']}, p={mod_p})")
    report.append("")

    # Six Predictions
    report.append("## Six-Prediction Scorecard")
    report.append("")
    report.append(f"**Result: {pred_passed}/6 passed**")
    report.append("")
    report.append("| # | Prediction | Result | Key Value |")
    report.append("|---|-----------|--------|-----------|")
    for k, v in predictions.items():
        status = 'PASS' if v['pass'] else 'FAIL'
        # Get key metric
        key_vals = {k2: v2 for k2, v2 in v.items() if k2 not in ('test', 'pass')}
        key_str = ', '.join(f'{k2}={v2}' for k2, v2 in list(key_vals.items())[:2])
        report.append(f"| {k} | {v['test'][:60]} | {status} | {key_str} |")
    report.append("")

    # Q3->Q4 Decomposition
    report.append("## Q3->Q4 Atom Decomposition")
    report.append("")
    report.append("### Transition JSD Magnitudes")
    report.append("")
    report.append("| Transition | HEAD JSD | TERM JSD |")
    report.append("|------------|----------|----------|")
    for name in ['Q0->Q1', 'Q1->Q2', 'Q2->Q3', 'Q3->Q4']:
        tr = t2['all_transitions'][name]
        report.append(f"| {name} | {tr['head_total_jsd']:.6f} | {tr['term_total_jsd']:.6f} |")
    report.append("")

    report.append("### Q3->Q4 HEAD Contributors")
    report.append("")
    report.append(f"Top-2 share: {q3q4['head_top2_share']:.1%}, "
                  f"Gini: {q3q4['head_gini']}")
    report.append("")
    for atom, contrib in list(q3q4['head_contributions'].items())[:6]:
        share = contrib / q3q4['head_total_jsd'] * 100 if q3q4['head_total_jsd'] > 0 else 0
        report.append(f"- {atom}: {contrib:.6f} ({share:.1f}%)")
    report.append("")

    report.append("### Q3->Q4 TERMINAL Contributors")
    report.append("")
    report.append(f"Top-2 share: {q3q4['term_top2_share']:.1%}, "
                  f"Gini: {q3q4['term_gini']}")
    report.append("")
    for atom, contrib in list(q3q4['term_contributions'].items())[:7]:
        share = contrib / q3q4['term_total_jsd'] * 100 if q3q4['term_total_jsd'] > 0 else 0
        report.append(f"- {atom}: {contrib:.6f} ({share:.1f}%)")
    report.append("")

    report.append("### Cross-Transition Cosine Similarity")
    report.append("")
    for k, v in cross_cos.items():
        report.append(f"- {k}: {v}")
    report.append("")

    report.append("### HEAD Rate Changes (Q3 -> Q4)")
    report.append("")
    report.append("| Atom | Rate Q3 | Rate Q4 | Change | Rel Change |")
    report.append("|------|---------|---------|--------|------------|")
    for rc in head_rate_changes:
        report.append(f"| {rc['atom']} | {rc['rate_Q3']:.4f} | {rc['rate_Q4']:.4f} | "
                      f"{rc['abs_change']:+.4f} | {rc['rel_change']:+.2f} |")
    report.append("")

    report.append("### TERMINAL Rate Changes (Q3 -> Q4)")
    report.append("")
    report.append("| Atom | Rate Q3 | Rate Q4 | Change | Rel Change |")
    report.append("|------|---------|---------|--------|------------|")
    for rc in term_rate_changes:
        report.append(f"| {rc['atom']} | {rc['rate_Q3']:.4f} | {rc['rate_Q4']:.4f} | "
                      f"{rc['abs_change']:+.4f} | {rc['rel_change']:+.2f} |")
    report.append("")

    # Hazard x Atom x Position
    report.append("## Hazard x Atom x Position Interaction")
    report.append("")
    report.append(f"Interaction chi-squared: {interaction_chi2} "
                  f"(df={t3['interaction_test']['df']}, p={interaction_p})")
    report.append(f"Zone-specific pairs (enrichment > 1.5x): "
                  f"{t3['n_zone_specific_pairs']}")
    report.append("")
    if zone_pairs:
        report.append("| Hazard | HEAD | Zone | Enrichment | N |")
        report.append("|--------|------|------|------------|---|")
        for pair in zone_pairs[:10]:
            report.append(f"| {pair['hazard']} | {pair['head']} | {pair['zone']} | "
                          f"{pair['enrichment']:.3f}x | {pair['count']} |")
        report.append("")

    report.append("### Thermal Cluster: k vs t vs e Work-Zone Deployment")
    report.append("")
    tc = thermal['k_vs_t_vs_e']
    report.append(f"Interpretation: **{thermal['work_zone_interpretation']}**")
    report.append("")
    report.append("| HEAD | N | Mean Pos | SPEC | WORK | CLOSURE |")
    report.append("|------|---|----------|------|------|---------|")
    for h in ['k', 't', 'e']:
        if h in tc:
            d = tc[h]
            zf = d['zone_fractions']
            report.append(f"| {h} | {d['n']} | {d['mean_frac_pos']} | "
                          f"{zf['SPEC']:.3f} | {zf['WORK']:.3f} | {zf['CLOSURE']:.3f} |")
    report.append("")

    report.append("### ZERO-Frame Position Profiles")
    report.append("")
    if zero_profiles:
        report.append("| Frame | N | Mean Pos | SPEC Fraction |")
        report.append("|-------|---|----------|---------------|")
        for frame, prof in zero_profiles.items():
            report.append(f"| {frame} | {prof['n']} | {prof['mean_frac_pos']} | "
                          f"{prof['spec_fraction']:.3f} |")
    report.append("")

    # Section-Conditioned Gradients
    report.append("## Section-Conditioned Atom Gradients")
    report.append("")
    report.append(f"Qualifying sections (>= {t4['metadata']['min_section_tokens']} tokens): "
                  f"{t4['metadata']['qualifying_sections']}")
    report.append("")
    report.append("| Section | N | HEAD corr | TERM corr | Q3Q4 HEAD JSD | m surge |")
    report.append("|---------|---|-----------|-----------|---------------|---------|")
    for sec in sorted(sections.keys()):
        sr = sections[sec]
        gp = sr['gradient_preservation']
        report.append(f"| {sec} | {sr['n_tokens']} | {gp['head_correlation']:.4f} | "
                      f"{gp['term_correlation']:.4f} | "
                      f"{sr['q3q4_step']['head_jsd']:.6f} | "
                      f"{sr['m_terminal_surge']['m_surge']:+.4f} |")
    report.append("")
    report.append(f"Q3Q4 JSD ratio (max/min): {aggregate['q3q4_jsd_ratio']:.3f}")
    report.append("")

    # Carryover cross-reference
    report.append("## Carryover Class Cross-Reference")
    report.append("")
    report.append(f"Top-3 position-sensitive HEADs: {carryover['top3_positional_heads']}")
    report.append(f"Top-3 position-sensitive TERMs: {carryover['top3_positional_terms']}")
    report.append(f"Dominant carryover class: **{carryover['dominant_carryover']}** "
                  f"({carryover['dominant_fraction']:.0%})")
    report.append("")

    # Constraints
    report.append("## Constraints")
    report.append("")
    for cid, cdata in constraints.items():
        report.append(f"### {cid}: {cdata['verdict']}")
        report.append("")
        report.append(f"**Rationale:** {cdata['rationale']}")
        report.append("")

    report_text = '\n'.join(report)
    report_path = os.path.join(PHASE_DIR, 'REPORT_581.md')
    with open(report_path, 'w') as f:
        f.write(report_text)

    print("T5: Synthesis complete")
    print(f"  C1671: {constraints['C1671']['verdict']}")
    print(f"  C1672: {constraints['C1672']['verdict']}")
    print(f"  C1673: {constraints['C1673']['verdict']}")
    print(f"  C1674: {constraints['C1674']['verdict']}")
    print(f"  Report: {report_path}")
    print(f"  Output: {out_path}")


TERMINALS = ['bare', 'h', 'l', 'm', 'n', 'r', 'y']

if __name__ == '__main__':
    main()
