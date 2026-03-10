"""Phase 559 T4: Synthesis

Reads T2 and T3 results, applies the outcome classification from the plan,
generates t4_synthesis.json and REPORT.md.

Input: t2_supervisory_state_induction.json, t3_plant_coupling.json
Output: t4_synthesis.json, REPORT.md
"""
import json
from pathlib import Path
from datetime import datetime


def classify_phase_verdict(stage1_outcome, stage2_result):
    """Apply the plan's outcome classification table."""
    if stage1_outcome == 'FAIL':
        return 'FAIL'
    if stage1_outcome == 'MARGINAL':
        return 'MARGINAL'
    if stage1_outcome == 'PASS_WITH_CAVEAT':
        return 'PARTIAL_PASS'
    if stage1_outcome == 'STRONG_PASS':
        if stage2_result == 'STAGE_1_FAILED':
            return 'STAGE_1_PASS'
        if stage2_result and stage2_result.get('outcome') == 'PASS':
            return 'FULL_PASS'
        return 'STAGE_1_PASS'
    return 'UNKNOWN'


def generate_report(t2, t3, phase_verdict, out_path):
    """Generate REPORT.md from results."""
    eval_data = t2['evaluation']
    criteria = eval_data['criteria']
    fc = eval_data['failure_conditions']
    meta = t2['metadata']
    real = t2['real']['6state']['metrics']

    # Gather null JSD summaries
    null_summary = {}
    for nt, details in criteria['S1']['details'].items():
        null_summary[nt] = {
            'real_null_jsd': details['mean_real_null_jsd'],
            'null_null_jsd': details['mean_null_null_jsd'],
            'p': details['p_value'],
        }

    lines = []
    lines.append("# Phase 559: Compositional Supervisory State Induction")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Folio:** {meta['folio']}")
    lines.append(f"**Phase verdict:** {phase_verdict}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append("Test whether compositional pairwise features (PREFIX x HEAD, TERM x SUFFIX_HEAD,")
    lines.append("HEAD x TERM frame hazard, HEAD x MOD, zone context, cross-token routing, and")
    lines.append("meta-features) can induce supervisory states on a single folio (f43v) that are")
    lines.append("more structured than baselines and null models. This is the corrected successor")
    lines.append("to Phase 558 (SINGLE_FOLIO_EXECUTION_COHERENCE), which failed due to hand-authored")
    lines.append("evidence vectors.")
    lines.append("")
    lines.append("## 2. Method")
    lines.append("")
    lines.append("### Evidence Construction")
    lines.append("")
    lines.append("Seven weighted channels derive evidence from corpus-wide enrichment ratios:")
    lines.append("")
    lines.append("| Channel | Weight | Key | Source |")
    lines.append("|---------|--------|-----|--------|")
    for ch_name, weight in meta['channel_weights'].items():
        lines.append(f"| {ch_name} | {weight} | pairwise key | B-corpus enrichment |")
    lines.append("")
    lines.append("For each channel, the corpus-wide count of tokens matching each pairwise key")
    lines.append("is computed. Per-category enrichment ratios (vs corpus baseline) are converted")
    lines.append("to log2 evidence, mapped from 8 operational categories to 6 supervisory states,")
    lines.append("and softmax-normalized.")
    lines.append("")
    lines.append("### State Ontology")
    lines.append("")
    lines.append("| State | Category sources |")
    lines.append("|-------|-----------------|")
    for cat, state in meta['cat_to_state_mapping'].items():
        lines.append(f"| {state} | {cat} |")
    lines.append("")
    lines.append("### Partitions Tested")
    lines.append("")
    lines.append("- **Partition A:** 6-state hypothesis (SPEC, TWORK, OBS, CHK, TRANS, CLOSE)")
    lines.append("- **Partition B:** 4-state coarse (SPECIFY, OPERATE, TRANSITION, CLOSURE)")
    lines.append("- **Partition C:** Unsupervised k-means on one-hot feature matrix with PCA")
    lines.append("")
    lines.append("### Baselines")
    lines.append("")
    lines.append("- **HEAD-only:** State assignment using only the HEAD atom channel")
    lines.append("- **Zone-only:** State assignment using only the line-zone channel")
    lines.append("")
    lines.append("### Null Models (5 types x 50 seeds each)")
    lines.append("")
    lines.append("| Null type | Description |")
    lines.append("|-----------|-------------|")
    lines.append("| token_shuffle | Shuffle tokens within each line |")
    lines.append("| line_shuffle | Shuffle lines within each paragraph |")
    lines.append("| cross_paragraph | Shuffle lines across all paragraphs |")
    lines.append("| random_token | Replace each token with random B-corpus token |")
    lines.append("| head_matched | Replace each token with HEAD-matched random token |")
    lines.append("")
    lines.append("## 3. Results")
    lines.append("")
    lines.append("### 3.1 State Profile (6-state)")
    lines.append("")
    lines.append("| State | Fraction |")
    lines.append("|-------|----------|")
    for i, state in enumerate(meta['states_6']):
        lines.append(f"| {state} | {real['profile'][i]:.3f} |")
    lines.append("")
    lines.append(f"**Entropy:** {real['entropy']:.4f} bits")
    lines.append(f"**Zone alignment:** {real['zone_alignment']:.4f}")
    lines.append("")
    lines.append("### 3.2 Baseline Comparison")
    lines.append("")
    lines.append(f"| Model | Entropy |")
    lines.append(f"|-------|---------|")
    lines.append(f"| Full 7-channel | {criteria['S4']['real_entropy']:.4f} |")
    lines.append(f"| HEAD-only | {criteria['S4']['head_only_entropy']:.4f} |")
    lines.append(f"| Zone-only | {criteria['S4']['zone_only_entropy']:.4f} |")
    lines.append("")
    lines.append(f"**Gain vs HEAD-only:** {criteria['S4']['gain_vs_head']:+.1%}")
    lines.append(f"**Gain vs Zone-only:** {criteria['S4']['gain_vs_zone']:+.1%}")
    lines.append("")
    lines.append("The full model produces **higher** entropy than both baselines,")
    lines.append("indicating that the additional channels disperse rather than")
    lines.append("concentrate state assignments. HEAD atom alone is more informative.")
    lines.append("")
    lines.append("### 3.3 Null Model Comparisons")
    lines.append("")
    lines.append("| Null type | Real-Null JSD | Null-Null JSD | p-value |")
    lines.append("|-----------|--------------|--------------|---------|")
    for nt, ns in null_summary.items():
        lines.append(f"| {nt} | {ns['real_null_jsd']:.6f} | "
                     f"{ns['null_null_jsd']:.6f} | {ns['p']:.4f} |")
    lines.append("")
    lines.append("**Interpretation:** The real folio's state profile is indistinguishable")
    lines.append("from all five null types. Token shuffle and structural shuffles produce")
    lines.append("JSD values near zero, meaning the state assignments are entirely")
    lines.append("token-local with no sequential or positional structure contributing.")
    lines.append("")
    lines.append("### 3.4 Head-Matched Separation")
    lines.append("")
    lines.append(f"- Effect size: {criteria['S5']['effect_size']:.3f} "
                 f"(threshold: 1.5)")
    lines.append(f"- Real vs head-matched JSD: "
                 f"{criteria['S5']['mean_real_hm_jsd']:.6f}")
    lines.append("")
    lines.append("The full model barely distinguishes real f43v from HEAD-matched")
    lines.append("random tokens. The compositional features beyond HEAD add negligible")
    lines.append("discriminative power.")
    lines.append("")
    lines.append("### 3.5 Paragraph Differentiation")
    lines.append("")
    lines.append(f"Significant metrics (p<0.05): "
                 f"{criteria['S3']['significant_count']}/5")
    lines.append("")
    lines.append("| Metric | p-value |")
    lines.append("|--------|---------|")
    for metric, pval in criteria['S3']['details'].items():
        lines.append(f"| {metric} | {pval:.4f} |")
    lines.append("")
    lines.append("All paragraph differentiation p-values are 1.0, indicating the")
    lines.append("3 paragraphs of f43v are categorically undifferentiated under the")
    lines.append("induced states.")
    lines.append("")
    lines.append("### 3.6 Partition Comparison")
    lines.append("")
    s6 = criteria['S6']['details']
    lines.append(f"- 6-state mean separation JSD: {s6['6state_mean_separation_jsd']:.6f}")
    lines.append(f"- Unsupervised silhouette: {s6['unsupervised_real_silhouette']:.4f} "
                 f"(null mean: {s6['unsupervised_null_mean_silhouette']:.4f})")
    lines.append(f"- Unsupervised beats 6-state: {s6['unsupervised_beats_6state']}")
    lines.append(f"- 4-state entropy: {s6['4state_entropy']:.4f}")
    lines.append(f"- 6-state entropy: {s6['6state_entropy']:.4f}")
    lines.append("")
    lines.append("The unsupervised partition does NOT beat the 6-state partition (FC6")
    lines.append("not triggered), but this is cold comfort since neither partition")
    lines.append("demonstrates meaningful structure.")
    lines.append("")
    lines.append("### 3.7 Failure Conditions")
    lines.append("")
    lines.append("| Condition | Triggered | Detail |")
    lines.append("|-----------|-----------|--------|")
    for fc_name, fc_data in fc.items():
        triggered = 'YES' if fc_data['triggered'] else 'no'
        trigger_desc = fc_data['trigger']
        lines.append(f"| {fc_name} | {triggered} | {trigger_desc} |")
    lines.append("")
    lines.append("**FC4 triggered:** Full model entropy (2.328) exceeds HEAD-only (1.490).")
    lines.append("The compositional evidence accumulation adds noise, not signal.")
    lines.append("")
    lines.append("## 4. Stage 1 Criteria Summary")
    lines.append("")
    lines.append("| Criterion | Result | Detail |")
    lines.append("|-----------|--------|--------|")
    for s_name in ['S1', 'S2', 'S3', 'S4', 'S5']:
        c = criteria[s_name]
        result = 'PASS' if c['pass'] else 'FAIL'
        lines.append(f"| {s_name}: {c['criterion']} | {result} | "
                     f"threshold: {c['threshold']} |")
    lines.append(f"| S6: {criteria['S6']['criterion']} | diagnostic | "
                 f"6-state mean sep JSD = {s6['6state_mean_separation_jsd']:.6f} |")
    lines.append("")
    lines.append(f"**Stage 1 verdict:** {eval_data['verdict']}")
    lines.append("")
    lines.append("## 5. Stage 2: Plant Coupling")
    lines.append("")
    lines.append(f"**Status:** {t3.get('result', 'N/A')}")
    lines.append("")
    lines.append("Stage 1 failure blocks Stage 2. No plant coupling was performed.")
    lines.append("")
    lines.append(f"## 6. Phase Verdict: {phase_verdict}")
    lines.append("")
    lines.append("## 7. Interpretation")
    lines.append("")
    lines.append("### Why the compositional approach failed")
    lines.append("")
    lines.append("The core problem is that the 7-channel evidence accumulation produces a")
    lines.append("MORE uncertain (higher entropy) state assignment than using HEAD atom alone.")
    lines.append("This is the opposite of what would occur if the additional channels carried")
    lines.append("complementary information.")
    lines.append("")
    lines.append("**Diagnosis:** The 8-to-6 category mapping with softmax normalization")
    lines.append("spreads probability mass across states. When multiple channels contribute")
    lines.append("different evidence, they average out rather than reinforcing each other.")
    lines.append("HEAD atom alone is a strong enough signal (C1475: HEAD atoms define")
    lines.append("categorically distinct operational domains, V=0.511) that diluting it with")
    lines.append("weaker signals degrades the assignment.")
    lines.append("")
    lines.append("### What the baselines tell us")
    lines.append("")
    lines.append("HEAD-only entropy (1.490) is 36% lower than the full model (2.328).")
    lines.append("Zone-only entropy (1.451) is similar to HEAD-only. Both baselines produce")
    lines.append("sharper, more concentrated state assignments than the 7-channel model.")
    lines.append("This means the simplest possible atom-level feature already carries most")
    lines.append("of the category information, consistent with C1475 (HEAD is the primary")
    lines.append("domain selector).")
    lines.append("")
    lines.append("### What the null models tell us")
    lines.append("")
    lines.append("Token shuffle JSD near zero means that reordering tokens within lines")
    lines.append("does not change the state profile. This confirms that the induced states")
    lines.append("are entirely determined by token identity, not by position or sequence.")
    lines.append("This is expected given C1003 (pairwise compositionality) and C1429")
    lines.append("(cross-line category independence) -- there should be no sequential")
    lines.append("structure to detect.")
    lines.append("")
    lines.append("### Structural implications")
    lines.append("")
    lines.append("This result is consistent with the existing constraint system:")
    lines.append("")
    lines.append("- C1003: No three-way morphological synergy. Pairwise channels should")
    lines.append("  suffice, but weighted averaging of many pairwise signals can degrade.")
    lines.append("- C1475: HEAD atom is the PRIMARY domain selector. Adding secondary")
    lines.append("  signals dilutes rather than sharpens the assignment.")
    lines.append("- C1431-C1433: PREFIX explains 94.4% of theoretical AXM max variance.")
    lines.append("  The compositional details beyond PREFIX+HEAD are near-deterministic,")
    lines.append("  leaving little room for a supervisory layer to add.")
    lines.append("- C1429: Cross-line category independence. Lines are i.i.d. samples")
    lines.append("  from folio profile, so line-level state induction cannot find")
    lines.append("  sequential structure that does not exist.")
    lines.append("")
    lines.append("### What would need to change")
    lines.append("")
    lines.append("A supervisory state model would need to either:")
    lines.append("1. Operate at FOLIO level (comparing folios, not tokens within a folio)")
    lines.append("2. Use a non-weighted-average combination rule (e.g., max, argmax)")
    lines.append("3. Accept that HEAD alone is sufficient and build on it directly")
    lines.append("4. Find a different decomposition that does not dilute HEAD's signal")
    lines.append("")
    lines.append("## 8. Non-Circularity Audit")
    lines.append("")
    lines.append("| Component | Voynich Input | Verdict |")
    lines.append("|-----------|---------------|---------|")
    lines.append("| Evidence tables | Corpus-wide enrichment ratios | INDIRECT (no f43v-specific tuning) |")
    lines.append("| Channel weights | Proportional to measured MI | INDIRECT |")
    lines.append("| 6-state ontology | Model hypothesis | TESTED against alternatives |")
    lines.append("| Token decomposition | BFolioDecoder on f43v | DIRECT (unavoidable) |")
    lines.append("| Null baselines | Random permutation/sampling | NONE |")
    lines.append("| Thresholds | Pre-registered in plan | NONE |")
    lines.append("")
    lines.append("No circularity detected. The failure is genuine.")
    lines.append("")
    lines.append("## 9. Relationship to Phase 558")
    lines.append("")
    lines.append("Phase 558 failed due to hand-authored evidence vectors that were")
    lines.append("insufficiently grounded. Phase 559 corrected this by deriving all")
    lines.append("evidence from corpus-wide enrichment ratios. Despite this improvement,")
    lines.append("the fundamental problem remains: the token-level compositional features")
    lines.append("do not produce supervisory states more informative than the HEAD atom")
    lines.append("alone. Phase 558's failure was methodological; Phase 559's failure is")
    lines.append("substantive -- the signal is not there at this level of analysis.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Constraint implications:** No new constraints proposed. The negative")
    lines.append("result is consistent with existing Tier 2 constraints (C1003, C1475,")
    lines.append("C1429, C1431-C1433). The result strengthens the interpretation that")
    lines.append("HEAD atom is the primary (and near-sufficient) domain selector, and")
    lines.append("that within-folio token-level state induction cannot improve upon it.")

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    return lines


def main():
    print("=== Phase 559 T4: Synthesis ===")

    results_dir = Path(__file__).parent.parent / 'results'
    phase_dir = Path(__file__).parent.parent

    # Load T2
    t2_path = results_dir / 't2_supervisory_state_induction.json'
    with open(t2_path) as f:
        t2 = json.load(f)

    # Load T3
    t3_path = results_dir / 't3_plant_coupling.json'
    with open(t3_path) as f:
        t3 = json.load(f)

    stage1_outcome = t2['evaluation']['outcome']
    stage2_result = t3.get('result', 'N/A')

    print(f"  Stage 1 outcome: {stage1_outcome}")
    print(f"  Stage 2 result: {stage2_result}")

    phase_verdict = classify_phase_verdict(stage1_outcome, stage2_result)
    print(f"  Phase verdict: {phase_verdict}")

    # Generate REPORT.md
    report_path = phase_dir / 'REPORT.md'
    generate_report(t2, t3, phase_verdict, report_path)
    print(f"  Generated: {report_path}")

    # Save synthesis JSON
    output = {
        'metadata': {
            'phase': '559',
            'task': 'T4_synthesis',
            'folio': t2['metadata']['folio'],
            'timestamp': datetime.now().isoformat(),
        },
        'stage_1': {
            'outcome': stage1_outcome,
            'verdict': t2['evaluation']['verdict'],
            'criteria_passed': [
                s for s in ['S1', 'S2', 'S3', 'S4', 'S5']
                if t2['evaluation']['criteria'][s]['pass']
            ],
            'criteria_failed': [
                s for s in ['S1', 'S2', 'S3', 'S4', 'S5']
                if not t2['evaluation']['criteria'][s]['pass']
            ],
            'failure_conditions_triggered': [
                fc for fc, data in t2['evaluation']['failure_conditions'].items()
                if data['triggered']
            ],
            'key_numbers': {
                'full_entropy': t2['evaluation']['criteria']['S4']['real_entropy'],
                'head_only_entropy': t2['evaluation']['criteria']['S4']['head_only_entropy'],
                'zone_only_entropy': t2['evaluation']['criteria']['S4']['zone_only_entropy'],
                'head_matched_effect_size': t2['evaluation']['criteria']['S5']['effect_size'],
                'zone_alignment': t2['real']['6state']['metrics']['zone_alignment'],
            },
        },
        'stage_2': {
            'result': stage2_result,
        },
        'phase_verdict': phase_verdict,
        'constraints_proposed': [],
        'constraints_referenced': [
            'C1003', 'C1475', 'C1429', 'C1431', 'C1432', 'C1433',
            'C1566', 'C1563', 'C1411', 'C1415',
        ],
        'interpretation': (
            'Compositional pairwise evidence accumulation produces higher-entropy '
            '(less certain) state assignments than HEAD atom alone. The additional '
            'channels dilute rather than sharpen the signal. HEAD is the primary '
            'and near-sufficient domain selector (C1475). No supervisory state '
            'structure exists at the within-folio token level beyond what HEAD '
            'already provides.'
        ),
    }

    out_path = results_dir / 't4_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"  Saved: {out_path}")

    print(f"\n=== Phase 559 Complete: {phase_verdict} ===")


if __name__ == '__main__':
    main()
