"""T5: Synthesis for Phase 580.

Write C1667-C1670, generate REPORT_580.md, freeze Tier-3 interpretation.
"""
import json, os
from datetime import datetime, timezone

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')


def main():
    # Load all previous results
    with open(os.path.join(RESULTS_DIR, 't0_feature_matrix_assembly.json')) as f:
        t0 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't1_manifold_embedding.json')) as f:
        t1 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_family_occupancy.json')) as f:
        t2 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't3_landscape_correspondence.json')) as f:
        t3 = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't4_accent_machine_fit.json')) as f:
        t4 = json.load(f)

    # Collect verdicts
    c1667 = t1['C1667']
    c1668 = t2['C1668']
    c1669 = t3['C1669']
    c1670 = t4['C1670']

    constraints = {
        'C1667': {
            'claim': (f"Response-surface manifold (Space A, 11 apparatus features) "
                      f"has effective rank {c1667['effective_rank_A']:.2f} and requires "
                      f"{c1667['pcs_for_80pct_A']} PCs for 80% variance."),
            'verdict': c1667['verdict'],
            'tier': 2,
            'scope': 'B_APPARATUS',
            'key_metrics': c1667['rationale']
        },
        'C1668': {
            'claim': (f"Apparatus families (A1={t2['metadata']['family_counts']['A1']}, "
                      f"A2={t2['metadata']['family_counts']['A2']}, "
                      f"A3={t2['metadata']['family_counts']['A3']}) show "
                      f"LOO accuracy {c1668['loo_accuracy']:.2f} and silhouette "
                      f"{c1668['silhouette']:.2f} in response-surface manifold."),
            'verdict': c1668['verdict'],
            'tier': 2,
            'scope': 'B_APPARATUS',
            'key_metrics': c1668['rationale']
        },
        'C1669': {
            'claim': (f"Landscape classes (SA/TD/FR) show "
                      f"{c1669['sig_PCs_A']} significant KW PCs in Space A with "
                      f"between/within ratio {c1669['bw_ratio_A']:.2f}."),
            'verdict': c1669['verdict'],
            'tier': 2,
            'scope': 'B_APPARATUS',
            'key_metrics': c1669['rationale']
        },
        'C1670': {
            'claim': (f"Folio accent vs manifold position: canonical r1="
                      f"{c1670['canonical_r1']:.3f}, max incremental R²="
                      f"{c1670['max_incremental_r2']:.3f}, max partial |r|="
                      f"{c1670['max_partial_corr']:.3f}."),
            'verdict': c1670['verdict'],
            'tier': 2,
            'scope': 'B_APPARATUS, ACCENT',
            'key_metrics': c1670['rationale']
        }
    }

    # Build Tier-3 interpretation freeze
    tier3_freeze = (
        "Currier B's productive closure advantage is broadly real but apparatus-conditioned. "
        "Regime-admission gating suppresses the main counterfeit-closure mechanism, especially "
        "in A2, but a residual forgiving pole remains. That pole is not a distinct hidden "
        "subfamily, not an opportunity artifact, and not recoverable by modest folio-specific "
        "retuning. It represents the forgiving edge of a continuous apparatus-response manifold, "
        "dominated by the same close-recovery channels that define A2 more generally. Folio "
        "accent and residual variance are therefore best understood as machine-fit positions on "
        "a real response surface, not as noise or decipherment failure."
    )

    # Generate REPORT_580.md
    report_lines = []
    report_lines.append("# Phase 580: Apparatus Response Manifold Synthesis")
    report_lines.append("")
    report_lines.append("## Executive Summary")
    report_lines.append("")
    report_lines.append(
        f"Two-space manifold analysis of 76 eligible Currier B folios across "
        f"3 apparatus families (A1=21, A2=18, A3=37). Space A (response surface, "
        f"11 features) captures what kind of apparatus each folio is; Space B "
        f"(realized performance, 4 features) captures how each folio actually performs."
    )
    report_lines.append("")

    # Verdicts summary
    report_lines.append("### Constraint Verdicts")
    report_lines.append("")
    report_lines.append("| ID | Track | Verdict |")
    report_lines.append("|----|-------|---------|")
    for cid, c in constraints.items():
        report_lines.append(f"| {cid} | {c['claim'][:60]}... | **{c['verdict']}** |")
    report_lines.append("")

    # Two-space design
    report_lines.append("## Two-Space Design Rationale")
    report_lines.append("")
    report_lines.append(
        "Per expert revision, we split features into two manifolds to avoid "
        "a self-repackaging PCA that rediscovers known verdict variables:"
    )
    report_lines.append("")
    report_lines.append(
        "- **Space A (Response Surface):** F1-F5 apparatus fits, 5 ablation deltas, "
        "mean_CTS. These describe *what kind of apparatus* a folio has."
    )
    report_lines.append(
        "- **Space B (Realized Performance):** DYE_advantage, CCS1, z_margin, PEF. "
        "These describe *how the folio actually performs*."
    )
    report_lines.append("")

    # Feature matrices and correlations
    report_lines.append("## Feature Matrices and Correlations")
    report_lines.append("")
    redundancy = t0['redundancy_report']
    report_lines.append(
        f"- Space A: {redundancy['space_A']['n_features']} features, "
        f"effective rank = {redundancy['space_A']['effective_rank']}"
    )
    report_lines.append(
        f"- Space B: {redundancy['space_B']['n_features']} features, "
        f"effective rank = {redundancy['space_B']['effective_rank']}"
    )
    report_lines.append("")
    high_A = t0['space_A']['high_correlations']
    if high_A:
        report_lines.append("High correlations (|r| > 0.7) in Space A:")
        report_lines.append("")
        for hc in high_A:
            report_lines.append(f"- {hc['feature_1']} ~ {hc['feature_2']}: r={hc['r']}")
        report_lines.append("")

    # Space A dimensionality
    sa = t1['space_A']
    report_lines.append("## Space A Dimensionality and PC Interpretation")
    report_lines.append("")
    report_lines.append(f"- Effective rank: {sa['effective_rank']:.2f}")
    report_lines.append(f"- PCs for 70%: {sa['pcs_for_70pct']}")
    report_lines.append(f"- PCs for 80%: {sa['pcs_for_80pct']}")
    report_lines.append(f"- PCs for 90%: {sa['pcs_for_90pct']}")
    report_lines.append(f"- Scree elbow: PC{sa['scree_elbow']}")
    report_lines.append("")
    report_lines.append("### PC Loadings (Space A)")
    report_lines.append("")
    for pc_name, tops in sa['loadings'].items():
        top_str = ', '.join(f"{t['feature']}({t['loading']:+.3f})" for t in tops[:4])
        report_lines.append(f"- **{pc_name}:** {top_str}")
    report_lines.append("")
    report_lines.append(f"**C1667: {c1667['verdict']}** -- {c1667['rationale']}")
    report_lines.append("")

    # Space B
    sb = t1['space_B']
    report_lines.append("## Space B Dimensionality")
    report_lines.append("")
    report_lines.append(f"- Effective rank: {sb['effective_rank']:.2f}")
    report_lines.append(f"- PCs for 80%: {sb['pcs_for_80pct']}")
    report_lines.append("")

    # Family geometry
    report_lines.append("## Family Geometry")
    report_lines.append("")
    fa = t2['space_A']
    report_lines.append(f"- LOO accuracy: {fa['loo_accuracy']:.2f}")
    report_lines.append(f"- Silhouette: {fa['silhouette']:.4f}")
    report_lines.append(f"- Permutation p: {fa['permutation_test']['p_value']:.4f}")
    report_lines.append(f"- Wrong centroid: {fa['wrong_centroid_count']}/{t2['metadata']['n_folios']}")
    report_lines.append("")
    report_lines.append("### Between-family distances")
    report_lines.append("")
    for k, v in fa['between_family_distances'].items():
        report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append("### Family elongation")
    report_lines.append("")
    for fam in ['A1', 'A2', 'A3']:
        e = fa['family_elongation'][fam]
        report_lines.append(f"- {fam}: ratio={e['ratio']:.2f}, direction={e['direction']}")
    report_lines.append(f"- Most elongated: **{fa['most_elongated_family']}**")
    report_lines.append("")
    report_lines.append("### A3 bridge analysis")
    report_lines.append("")
    b = fa['a3_bridge']
    report_lines.append(f"- Bridge fraction: {b['bridge_count']}/{b['n_a3']} ({b['bridge_fraction']:.2f})")
    report_lines.append(f"- Spanning ratio: {b['spanning_ratio']:.2f}")
    report_lines.append(f"- Mean dist to A1: {b['mean_dist_to_A1']:.4f}")
    report_lines.append(f"- Mean dist to A2: {b['mean_dist_to_A2']:.4f}")
    report_lines.append("")
    report_lines.append(f"**C1668: {c1668['verdict']}** -- {c1668['rationale']}")
    report_lines.append("")

    # Landscape correspondence
    report_lines.append("## Landscape Correspondence")
    report_lines.append("")
    la = t3['space_A']
    report_lines.append(f"### Space A")
    report_lines.append(f"- Significant KW PCs: {la['n_significant_PCs']}")
    report_lines.append(f"- Classification accuracy: {la['classification_accuracy']:.2f}")
    report_lines.append(f"- B/W ratio: {la['between_within_ratio']:.2f}")
    report_lines.append("")
    for pc, kw in la['kruskal_wallis_per_PC'].items():
        sig_str = " ***" if kw['significant_01'] else ""
        report_lines.append(f"- {pc}: H={kw['H']:.2f}, p={kw['p']:.4f}{sig_str}")
    report_lines.append("")
    lb = t3['space_B']
    report_lines.append(f"### Space B")
    report_lines.append(f"- Significant KW PCs: {lb['n_significant_PCs']}")
    report_lines.append(f"- Classification accuracy: {lb['classification_accuracy']:.2f}")
    report_lines.append(f"- B/W ratio: {lb['between_within_ratio']:.2f}")
    report_lines.append("")
    report_lines.append(f"### Cross-space comparison")
    comp = t3['cross_space_comparison']
    report_lines.append(f"- Better space for landscape: **{comp['better_space']}**")
    report_lines.append("")
    report_lines.append("### Cross-space correlations (|r| > 0.3)")
    report_lines.append("")
    for k, v in t3['cross_space_correlations'].items():
        if abs(v) > 0.3:
            report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append(f"**C1669: {c1669['verdict']}** -- {c1669['rationale']}")
    report_lines.append("")

    # Accent reinterpretation
    report_lines.append("## Accent Reinterpretation")
    report_lines.append("")
    report_lines.append(f"- Canonical correlations: {t4['canonical_correlations']}")
    report_lines.append(f"- Incremental R² for CCS1: {t4['incremental_r_squared']['CCS1']['incremental']:.4f}")
    report_lines.append(f"- Incremental R² for DYE: {t4['incremental_r_squared']['DYE_advantage']['incremental']:.4f}")
    report_lines.append(f"- Within-A2 R²: {t4['within_A2']['r_squared']:.4f}")
    report_lines.append("")
    report_lines.append("### Top Spearman correlations")
    report_lines.append("")
    sorted_spear = sorted(t4['spearman_accent_vs_manifold'].items(),
                          key=lambda x: abs(x[1]), reverse=True)
    for k, v in sorted_spear[:6]:
        report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append("### Forgiving-edge distance")
    report_lines.append("")
    for k, v in t4['forgiving_edge_distance']['accent_vs_FR_distance'].items():
        report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append("### Stubborn folios in manifold")
    report_lines.append("")
    report_lines.append("| Folio | Class | FR distance | PC scores |")
    report_lines.append("|-------|-------|-------------|-----------|")
    for f, data in t4['forgiving_edge_distance']['stubborn_folios'].items():
        scores_str = ', '.join(f"{pc}={s:.2f}" for pc, s in data['manifold_scores'].items())
        report_lines.append(
            f"| {f} | {data['endpoint_class']} | {data['fr_distance']:.3f} | {scores_str} |"
        )
    report_lines.append("")
    pb = t4['forgiving_edge_distance']['point_biserial_SE_vs_PA']
    if pb:
        report_lines.append("Point-biserial (SE=0 vs PA=1):")
        report_lines.append("")
        for k, v in pb.items():
            report_lines.append(f"- {k}: {v}")
        report_lines.append("")
    report_lines.append(f"**C1670: {c1670['verdict']}** -- {c1670['rationale']}")
    report_lines.append("")

    # Tier-3 interpretation freeze
    report_lines.append("## Tier-3 Interpretation Freeze")
    report_lines.append("")
    report_lines.append(f"> {tier3_freeze}")
    report_lines.append("")

    # Constraints table
    report_lines.append("## Constraints C1667-C1670")
    report_lines.append("")
    report_lines.append("| ID | Claim | Verdict | Tier | Scope |")
    report_lines.append("|----|-------|---------|------|-------|")
    for cid, c in constraints.items():
        report_lines.append(
            f"| {cid} | {c['claim']} | {c['verdict']} | {c['tier']} | {c['scope']} |"
        )
    report_lines.append("")

    report_text = '\n'.join(report_lines)

    # Write REPORT_580.md
    report_path = os.path.join(PHASE_DIR, 'REPORT_580.md')
    with open(report_path, 'w') as f:
        f.write(report_text)

    # Write synthesis JSON
    output = {
        'metadata': {
            'phase': '580',
            'script': 't5_synthesis.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': t0['metadata']['n_folios']
        },
        'constraints': constraints,
        'tier3_interpretation_freeze': tier3_freeze,
        'summary': {
            'space_A_effective_rank': t1['space_A']['effective_rank'],
            'space_A_pcs_80': t1['space_A']['pcs_for_80pct'],
            'space_B_effective_rank': t1['space_B']['effective_rank'],
            'loo_accuracy': t2['space_A']['loo_accuracy'],
            'silhouette': t2['space_A']['silhouette'],
            'landscape_sig_PCs_A': t3['space_A']['n_significant_PCs'],
            'landscape_bw_ratio_A': t3['space_A']['between_within_ratio'],
            'canonical_r1': t4['C1670']['canonical_r1'],
            'max_incr_r2': t4['C1670']['max_incremental_r2']
        }
    }

    out_path = os.path.join(RESULTS_DIR, 't5_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T5: Synthesis complete")
    print(f"  C1667: {c1667['verdict']}")
    print(f"  C1668: {c1668['verdict']}")
    print(f"  C1669: {c1669['verdict']}")
    print(f"  C1670: {c1670['verdict']}")
    print(f"  Report: {report_path}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
