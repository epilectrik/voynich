"""
Post-Closure Characterization Phase: Run All Axes

Executes AXIS 1-4 and generates comprehensive summary report.
"""

import json
from pathlib import Path
from datetime import datetime

# Import axis modules
import axis1_entry_structure
import axis2_adjacency_navigation
import axis3_coverage_scheduling
import axis4_azc_interface


def generate_summary_report(all_results: dict) -> str:
    """Generate comprehensive summary report for all axes."""

    report = f"""
################################################################################
#                                                                              #
#           POST-CLOSURE CHARACTERIZATION PHASE - SUMMARY REPORT               #
#                                                                              #
################################################################################

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Phase: Post-Closure Characterization
Status: COMPLETE

================================================================================
PHASE GOAL (Reminder)
================================================================================

Characterize Currier A as a human-facing complexity-frontier registry:
- How discrimination coverage is maintained and navigated
- How entry structure, adjacency, and closure support cognition
- How these interact with AZC compatibility
- WITHOUT new grammars, semantics, or entry-level A-B mapping

CRITICAL: Current folio order is NOT authoritative (rebinding likely).

================================================================================
REBINDING SENSITIVITY SUMMARY
================================================================================

"""
    # Collect order sensitivity for all tests
    invariant_tests = []
    folio_local_tests = []
    latent_order_tests = []

    for axis_name, axis_results in all_results.items():
        for test_name, test_data in axis_results.items():
            sensitivity = test_data.get('order_sensitivity', 'UNKNOWN')
            test_label = f"{axis_name}/{test_name}: {test_data.get('verdict', 'N/A')}"

            if sensitivity == 'INVARIANT':
                invariant_tests.append(test_label)
            elif sensitivity == 'FOLIO_LOCAL_ORDER':
                folio_local_tests.append(test_label)
            elif sensitivity == 'LATENT_ORDER_DEPENDENT':
                latent_order_tests.append(test_label)

    report += f"""
INVARIANT (rebinding-safe): {len(invariant_tests)} tests
FOLIO_LOCAL_ORDER (within-folio sequence): {len(folio_local_tests)} tests
LATENT_ORDER_DEPENDENT (requires order recovery): {len(latent_order_tests)} tests

--------------------------------------------------------------------------------
INVARIANT FINDINGS (Safe under any rebinding)
--------------------------------------------------------------------------------
"""
    for t in invariant_tests:
        report += f"  - {t}\n"

    report += """
--------------------------------------------------------------------------------
FOLIO_LOCAL_ORDER FINDINGS (Assume within-folio sequence is original)
--------------------------------------------------------------------------------
"""
    for t in folio_local_tests:
        report += f"  - {t}\n"

    report += """
--------------------------------------------------------------------------------
LATENT_ORDER_DEPENDENT FINDINGS (Require external order validation)
--------------------------------------------------------------------------------
"""
    for t in latent_order_tests:
        report += f"  - {t}\n"

    # Axis-by-axis summary
    report += """

================================================================================
AXIS-BY-AXIS SUMMARY
================================================================================
"""

    axis_labels = {
        'axis1': 'AXIS 1: Entry Structure as Cognitive Interface',
        'axis2': 'AXIS 2: Adjacency as Discrimination Navigation',
        'axis3': 'AXIS 3: Coverage Control vs Temporal Scheduling',
        'axis4': 'AXIS 4: A <-> AZC Micro-Interface'
    }

    for axis_key, axis_title in axis_labels.items():
        if axis_key in all_results:
            report += f"\n{axis_title}\n"
            report += "-" * len(axis_title) + "\n\n"

            for test_name, test_data in all_results[axis_key].items():
                verdict = test_data.get('verdict', test_data.get('order_signal', 'N/A'))
                interp = test_data.get('interpretation', 'N/A')
                report += f"  {test_data.get('question', test_name)}\n"
                report += f"    Verdict: {verdict}\n"
                report += f"    Interpretation: {interp}\n\n"

    # Overall verdict
    report += """
================================================================================
OVERALL FINDINGS
================================================================================

"""
    # Count verdicts
    yes_count = 0
    weak_count = 0
    no_count = 0

    for axis_results in all_results.values():
        for test_data in axis_results.values():
            verdict = test_data.get('verdict', '')
            if verdict.startswith('YES'):
                yes_count += 1
            elif verdict.startswith('WEAK') or verdict == 'PARTIAL':
                weak_count += 1
            elif verdict in ['NO', 'NEUTRAL']:
                no_count += 1

    report += f"""
Positive findings (YES): {yes_count}
Weak/Partial findings: {weak_count}
Null findings (NO): {no_count}

"""

    if yes_count >= 5:
        overall = "STRONG CHARACTERIZATION"
        summary = """
Currier A shows clear cognitive interface properties:
- Entry structure supports human navigation
- Adjacency has measurable organizational function
- Coverage patterns are detectable order-independently
- A-AZC interface shows vocabulary-based coordination
"""
    elif yes_count + weak_count >= 5:
        overall = "MODERATE CHARACTERIZATION"
        summary = """
Currier A shows some cognitive interface properties:
- Some entry structure effects detected
- Adjacency function partially confirmed
- Mix of positive and null findings
"""
    else:
        overall = "MINIMAL CHARACTERIZATION"
        summary = """
Limited cognitive interface properties detected:
- Most effects are null or weak
- Currier A may be more uniform than expected
- Or: measurement granularity is insufficient
"""

    report += f"OVERALL VERDICT: {overall}\n"
    report += summary

    # What this does NOT change
    report += """
================================================================================
WHAT THIS DOES NOT CHANGE
================================================================================

The following Tier 0-2 constraints remain binding and unchanged:

ARCHITECTURE:
- C233 LINE_ATOMIC: Each line is an independent record
- C384 NO_A_B_COUPLING: No entry-level A->B correspondence
- C389 ADJACENCY_EXISTS: Adjacency structure is real
- C422 DA_ARTICULATION: DA marks internal punctuation

AZC:
- C319-C433: AZC grammar unchanged
- A->AZC activation rules unchanged

COVERAGE:
- C476 COVERAGE_OPTIMALITY: Coverage properties unchanged
- C478 TEMPORAL_SCHEDULING: Interpretation is order-dependent

CLOSURE:
- Closure mechanism is structural, not semantic
- Entry grammar (opener/content/closure) confirmed

================================================================================
EXIT CONDITIONS
================================================================================

This phase concludes when:
[X] All AXIS 1-4 questions answered or falsified
[X] Order-independent structure characterized
[ ] Remaining questions depend on external codicology (BLOCKED)
[ ] Further work would require reopening Tier 0-2 (STOP)

NEXT STEPS (if any):
- Order-dependent findings require external codicological validation
- No architectural changes warranted by these findings
- Phase moves to archival status

================================================================================
FILES GENERATED
================================================================================

- axis1_results.json, AXIS1_REPORT.md
- axis2_results.json, AXIS2_REPORT.md
- axis3_results.json, AXIS3_REPORT.md
- axis4_results.json, AXIS4_REPORT.md
- pcc_all_results.json (combined)
- PCC_SUMMARY_REPORT.md (this file)

################################################################################
#                           END OF PHASE REPORT                                #
################################################################################
"""

    return report


def main():
    print("="*70)
    print("POST-CLOSURE CHARACTERIZATION PHASE")
    print("Running All Axes...")
    print("="*70)

    all_results = {}

    # Run AXIS 1
    print("\n" + "="*70)
    print("RUNNING AXIS 1...")
    print("="*70)
    all_results['axis1'] = axis1_entry_structure.main()

    # Run AXIS 2
    print("\n" + "="*70)
    print("RUNNING AXIS 2...")
    print("="*70)
    all_results['axis2'] = axis2_adjacency_navigation.main()

    # Run AXIS 3
    print("\n" + "="*70)
    print("RUNNING AXIS 3...")
    print("="*70)
    all_results['axis3'] = axis3_coverage_scheduling.main()

    # Run AXIS 4
    print("\n" + "="*70)
    print("RUNNING AXIS 4...")
    print("="*70)
    all_results['axis4'] = axis4_azc_interface.main()

    # Generate summary
    summary_report = generate_summary_report(all_results)
    print(summary_report)

    # Save combined results
    output_path = Path(__file__).parent / 'pcc_all_results.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nCombined results saved to: {output_path}")

    # Save summary report
    report_path = Path(__file__).parent / 'PCC_SUMMARY_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(summary_report)
    print(f"Summary report saved to: {report_path}")

    return all_results


if __name__ == '__main__':
    main()
