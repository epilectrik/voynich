"""Phase 558 T4: Synthesis — Apply pass/fail criteria, generate verdict.

Input: t3_coherence_scoring.json
Output: t4_synthesis.json
"""
import json
import os
from pathlib import Path


def main():
    # Load T3 scoring
    t3_path = Path(__file__).parent.parent / 'results' / 't3_coherence_scoring.json'
    with open(t3_path) as f:
        t3 = json.load(f)

    # ════════════════════════════════════════════════════════════
    # Extract criterion results
    # ════════════════════════════════════════════════════════════

    c1 = t3.get('C1', {})
    c2 = t3.get('C2', {})
    c3 = t3.get('C3', {})
    c4 = t3.get('C4', {})
    c5 = t3.get('C5', {})

    c1_pass = c1.get('verdict') == 'PASS'
    c2_pass = c2.get('verdict') == 'PASS'
    c3_pass = c3.get('verdict') == 'PASS'
    c4_pass = c4.get('verdict') == 'PASS'

    c5a_pass = c5.get('c5a_viab_pass', False)
    c5b_pass = c5.get('c5b_error_pass', False)
    c5c_pass = c5.get('c5c_closure_pass', False)

    # ════════════════════════════════════════════════════════════
    # Apply pass criteria
    # ════════════════════════════════════════════════════════════

    # Overall PASS: C1 + C5a + C5c + at least 2 of {C2, C3, C4}
    soft_pass_count = sum([c2_pass, c3_pass, c4_pass])
    hard_requirements = c1_pass and c5a_pass and c5c_pass
    overall_pass = hard_requirements and soft_pass_count >= 2

    # ════════════════════════════════════════════════════════════
    # Failure conditions
    # ════════════════════════════════════════════════════════════

    failure_conditions = {}

    # FC1: Plant diverges → architecture wrong
    fc1 = not c1_pass
    failure_conditions['FC1'] = {
        'triggered': fc1,
        'desc': 'Plant diverges or leaves viable range',
        'viability': c1.get('viability', None),
    }

    # FC2: Token-shuffle EQUAL to full → positional grammar has no effect
    fc2 = not c5a_pass
    failure_conditions['FC2'] = {
        'triggered': fc2,
        'desc': 'Token-shuffle performs equal to full (positional grammar has no effect)',
        'details': c5.get('C5a_details', {}),
    }

    # FC3: Random tokens EQUAL to full → folio specificity has no effect
    fc3 = not c5c_pass
    failure_conditions['FC3'] = {
        'triggered': fc3,
        'desc': 'Random tokens perform equal to full (folio specificity has no effect)',
        'details': c5.get('C5c_details', {}),
    }

    # FC4: Line-shuffle dramatically destroys line-local safety
    fc4 = not c5b_pass
    failure_conditions['FC4'] = {
        'triggered': fc4,
        'desc': 'Line-shuffle destroys line-local safety metrics (lines are not safety-local)',
        'note': 'Modest global trajectory shift is acceptable, not a failure',
        'details': c5.get('C5b_details', {}),
    }

    # ════════════════════════════════════════════════════════════
    # Model comparison
    # ════════════════════════════════════════════════════════════

    model_comparison = t3.get('model_comparison', {})
    controller_comparison = t3.get('controller_comparison', {})

    # ════════════════════════════════════════════════════════════
    # Non-circularity audit
    # ════════════════════════════════════════════════════════════

    non_circularity = {
        'plant_ODE': 'NONE — thermodynamics (Phase 555-557)',
        'plant_parameters': 'NONE — REGIME_4 nominal (generic precision profile)',
        'P_controller': 'NONE — standard proportional control',
        'MPC_controller': 'NONE — standard predictive control',
        'supervisor_logic': 'NONE — supervisory control theory (permission intersection, guard evaluation)',
        'SUP_CLOSING_latch': 'NONE — standard safety shutdown pattern',
        'token_decomposition': 'ALL — f43v tokens via voynich.py',
        'weight_tables': 'INDIRECT — derived from Tier 2 constraints (C929, C1446, C1475-C1479, etc.)',
        'paragraph_structure': 'ALL — transcript paragraph annotations',
        'null_baselines': 'NONE — statistical shuffles',
        'verdict': 'Mapping rules are the critical interface. Two levels of indirection between tokens and plant actuation.'
    }

    # ════════════════════════════════════════════════════════════
    # Compile verdict
    # ════════════════════════════════════════════════════════════

    if overall_pass:
        verdict_text = "PASS"
        reason = f"C1={c1_pass}, C5a={c5a_pass}, C5c={c5c_pass} (all hard), " \
                 f"soft={soft_pass_count}/3 (C2={c2_pass}, C3={c3_pass}, C4={c4_pass})"
    else:
        verdict_text = "FAIL"
        failed_hard = []
        if not c1_pass:
            failed_hard.append("C1 (plant viability)")
        if not c5a_pass:
            failed_hard.append("C5a (token-shuffle degradation)")
        if not c5c_pass:
            failed_hard.append("C5c (random-token degradation)")
        if hard_requirements and soft_pass_count < 2:
            failed_hard.append(f"soft criteria ({soft_pass_count}/3, need 2)")

        triggered_fcs = [k for k, v in failure_conditions.items() if v['triggered']]
        reason = f"Failed: {', '.join(failed_hard)}. " \
                 f"Failure conditions triggered: {triggered_fcs}"

    output = {
        'verdict': {
            'verdict': verdict_text,
            'reason': reason,
            'overall_pass': overall_pass,
        },
        'criteria': {
            'C1': {'pass': c1_pass, 'details': c1},
            'C2': {'pass': c2_pass, 'details': c2},
            'C3': {'pass': c3_pass, 'details': c3},
            'C4': {'pass': c4_pass, 'details': c4},
            'C5': {
                'C5a_pass': c5a_pass,
                'C5b_pass': c5b_pass,
                'C5c_pass': c5c_pass,
                'details': c5,
            },
        },
        'failure_conditions': failure_conditions,
        'model_comparison': model_comparison,
        'controller_comparison': controller_comparison,
        'non_circularity': non_circularity,
        'paragraph_profiles': t3.get('paragraph_profiles', {}),
        'diagnostics': {
            'hard_requirements_met': hard_requirements,
            'soft_pass_count': soft_pass_count,
            'n_failure_conditions_triggered': sum(1 for v in failure_conditions.values() if v['triggered']),
        },
    }

    # Print summary
    print(f"=== PHASE 558 VERDICT: {verdict_text} ===")
    print(f"  Reason: {reason}")
    print()
    print("  Criteria:")
    print(f"    C1 (Execution Coherence):      {'PASS' if c1_pass else 'FAIL'}")
    print(f"    C2 (Safety Coherence):          {'PASS' if c2_pass else 'FAIL'}")
    print(f"    C3 (Paragraph Differentiation): {'PASS' if c3_pass else 'FAIL'}")
    print(f"    C4 (Token-Level Fit):           {'PASS' if c4_pass else 'FAIL'}")
    print(f"    C5a (Token-shuffle degrades):   {'PASS' if c5a_pass else 'FAIL'}")
    print(f"    C5b (Line-shuffle preserves):   {'PASS' if c5b_pass else 'FAIL'}")
    print(f"    C5c (Random-token degrades):    {'PASS' if c5c_pass else 'FAIL'}")
    print()
    print("  Failure conditions:")
    for k, v in failure_conditions.items():
        status = "TRIGGERED" if v['triggered'] else "clear"
        print(f"    {k}: {status} — {v['desc']}")
    print()
    print(f"  Non-circularity: Token decomposition=ALL, Weight tables=INDIRECT, rest=NONE")

    # Save
    out_path = Path(__file__).parent.parent / 'results' / 't4_synthesis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path) / 1024:.1f} KB")


if __name__ == '__main__':
    main()
