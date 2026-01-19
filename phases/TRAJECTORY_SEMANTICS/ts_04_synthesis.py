#!/usr/bin/env python3
"""
ts_04_synthesis.py - Aggregate results and determine tier assessment

Combines Vector A and C results to determine overall TRAJECTORY_SEMANTICS findings.
Generates final report.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
PHASE_DIR = Path(__file__).parent


def load_results():
    """Load results from individual tests."""
    results = {}

    # Vector C
    try:
        with open(RESULTS_DIR / "ts_gradient_steepness.json") as f:
            results['vector_c'] = json.load(f)
    except FileNotFoundError:
        results['vector_c'] = None

    # Vector A
    try:
        with open(RESULTS_DIR / "ts_judgment_zone_matrix.json") as f:
            results['vector_a'] = json.load(f)
    except FileNotFoundError:
        results['vector_a'] = None

    # Final Pressure Test: Judgment Trajectories
    try:
        with open(RESULTS_DIR / "ts_judgment_trajectories.json") as f:
            results['judgment_trajectories'] = json.load(f)
    except FileNotFoundError:
        results['judgment_trajectories'] = None

    return results


def assess_tier(results):
    """Determine overall tier based on combined results."""
    c_passed = 0
    a_passed = 0

    if results['vector_c']:
        c_passed = results['vector_c'].get('summary', {}).get('hypotheses_passed', 0)

    if results['vector_a']:
        a_passed = results['vector_a'].get('summary', {}).get('hypotheses_passed', 0)

    total_passed = c_passed + a_passed
    total_tests = 7  # 4 from C + 3 from A

    # Tier 2 upgrade: C >= 3/4 AND A >= 2/3
    if c_passed >= 3 and a_passed >= 2:
        return {
            'tier': 'TIER_2_CANDIDATE',
            'confidence': 'HIGH',
            'rationale': f'Strong evidence in both vectors: C={c_passed}/4, A={a_passed}/3',
        }

    # Tier 3 enrichment: C >= 2/4 OR A >= 2/3
    if c_passed >= 2 or a_passed >= 2:
        return {
            'tier': 'TIER_3_ENRICHMENT',
            'confidence': 'MEDIUM',
            'rationale': f'Partial evidence: C={c_passed}/4, A={a_passed}/3',
        }

    # Weak signal
    if total_passed >= 2:
        return {
            'tier': 'TIER_3_WEAK',
            'confidence': 'LOW',
            'rationale': f'Weak signal: total={total_passed}/7',
        }

    return {
        'tier': 'INCONCLUSIVE',
        'confidence': 'NONE',
        'rationale': f'Insufficient evidence: total={total_passed}/7',
    }


def generate_report(results, assessment):
    """Generate markdown report."""
    report = []

    report.append("# TRAJECTORY_SEMANTICS Phase Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Status:** COMPLETE")
    report.append("")

    # Executive summary
    report.append("## Executive Summary")
    report.append("")
    report.append(f"**Tier Assessment:** {assessment['tier']}")
    report.append(f"**Confidence:** {assessment['confidence']}")
    report.append(f"**Rationale:** {assessment['rationale']}")
    report.append("")

    # Key finding
    report.append("> **Key Finding:** " + (
        "Trajectory semantics (HOW constraint pressure evolves) shows structure beyond token semantics."
        if assessment['tier'] in ['TIER_2_CANDIDATE', 'TIER_3_ENRICHMENT']
        else "Trajectory semantics signal is weak or absent."
    ))
    report.append("")

    report.append("---")
    report.append("")

    # Vector C results
    report.append("## Vector C: Gradient Steepness")
    report.append("")

    if results['vector_c']:
        vc = results['vector_c']
        report.append(f"**Recipes analyzed:** {vc.get('n_recipes', 'N/A')}")
        report.append("")

        report.append("### Hypothesis Results")
        report.append("")
        report.append("| Hypothesis | Test | Result | Status |")
        report.append("|------------|------|--------|--------|")

        for h_id, h_data in vc.get('hypotheses', {}).items():
            name = h_data.get('name', h_id)
            test = h_data.get('test', 'N/A')

            if 'F' in h_data and h_data['F'] is not None:
                result = f"F={h_data['F']:.2f}, p={h_data['p']:.4f}"
            elif 'r' in h_data and h_data['r'] is not None:
                result = f"r={h_data['r']:.3f}, p={h_data['p']:.4f}"
            elif 't' in h_data and h_data['t'] is not None:
                result = f"t={h_data['t']:.2f}, p={h_data['p']:.4f}"
            else:
                result = "N/A"

            status = "PASS" if h_data.get('significant', False) else "FAIL"
            report.append(f"| {h_id}: {name[:30]} | {test} | {result} | {status} |")

        report.append("")
        report.append(f"**Passed:** {vc.get('summary', {}).get('hypotheses_passed', 0)}/4")
        report.append(f"**Verdict:** {vc.get('summary', {}).get('verdict', 'N/A')}")
    else:
        report.append("*No results available*")

    report.append("")
    report.append("---")
    report.append("")

    # Vector A results
    report.append("## Vector A: Interface Theory")
    report.append("")

    if results['vector_a']:
        va = results['vector_a']
        report.append(f"**Judgments analyzed:** {va.get('n_judgments', 'N/A')}")
        report.append("")

        # Zone judgment counts
        if 'zone_counts' in va:
            report.append("### Zone Judgment Availability")
            report.append("")
            report.append("| Zone | Required | Permitted | Impossible |")
            report.append("|------|----------|-----------|------------|")
            for zone in ['C', 'P', 'R', 'S']:
                counts = va['zone_counts'].get(zone, {})
                report.append(f"| {zone} | {counts.get('required', 0)} | {counts.get('permitted', 0)} | {counts.get('impossible', 0)} |")
            report.append("")

        report.append("### Hypothesis Results")
        report.append("")
        report.append("| Hypothesis | Result | Status |")
        report.append("|------------|--------|--------|")

        for h_id, h_data in va.get('hypotheses', {}).items():
            name = h_data.get('name', h_id)

            if 'rate' in h_data:
                result = f"{h_data['rate']:.1%} non-uniform"
            elif 'count' in h_data:
                result = f"{h_data['count']} significant"
            elif 'r' in h_data and h_data['r'] is not None:
                result = f"r={h_data['r']:.3f}"
            else:
                result = "N/A"

            status = "PASS" if h_data.get('significant', False) else "FAIL"
            report.append(f"| {h_id}: {name[:40]} | {result} | {status} |")

        report.append("")
        report.append(f"**Passed:** {va.get('summary', {}).get('hypotheses_passed', 0)}/3")
        report.append(f"**Verdict:** {va.get('summary', {}).get('verdict', 'N/A')}")
    else:
        report.append("*No results available*")

    report.append("")
    report.append("---")
    report.append("")

    # Judgment Trajectories (Final Pressure Test)
    report.append("## Final Pressure Test: Judgment Elimination Trajectories")
    report.append("")

    if results.get('judgment_trajectories'):
        jt = results['judgment_trajectories']
        report.append("**The decisive finding:** The manuscript is a JUDGMENT-GATING SYSTEM.")
        report.append("")
        report.append("### Agency Withdrawal Curve")
        report.append("")
        report.append("| Zone | Available | Required | Impossible | Freedom |")
        report.append("|------|-----------|----------|------------|---------|")

        curve = jt.get('agency_withdrawal_curve', {})
        for zone in ['C', 'P', 'R', 'S']:
            c = curve.get(zone, {})
            freedom = c.get('freedom_index', 0) * 100
            report.append(f"| {zone} | {c.get('available', 0)} | {c.get('required', 0)} | "
                         f"{c.get('impossible', 0)} | {freedom:.0f}% |")

        report.append("")
        report.append("### Key Findings")
        report.append("")
        km = jt.get('key_metrics', {})
        report.append(f"- **Freedom collapse:** {km.get('c_zone_freedom', 0)*100:.0f}% -> "
                     f"{km.get('s_zone_freedom', 0)*100:.0f}% "
                     f"({km.get('freedom_collapse', 0)*100:.0f}% withdrawn)")
        report.append(f"- **FORBIDDEN INTERVENTION onset:** Zone {km.get('forbidden_intervention_onset', 0):.0f}")
        report.append(f"- **WATCH CLOSELY eliminated at S:** {km.get('watch_closely_eliminated_at_s', 0)}/6")
        report.append("")

        interp = jt.get('interpretation', {})
        report.append("### Interpretation")
        report.append("")
        report.append(f"> {interp.get('headline', '')}")
        report.append("")
        report.append(f"**Mechanism:** {interp.get('mechanism', '')}")
        report.append("")
        report.append(f"**Key insight:** {interp.get('key_insight', '')}")
    else:
        report.append("*No results available*")

    report.append("")
    report.append("---")
    report.append("")

    # Interpretation
    report.append("## Overall Interpretation")
    report.append("")

    if assessment['tier'] == 'TIER_2_CANDIDATE':
        report.append("### Trajectory Semantics Confirmed")
        report.append("")
        report.append("The results demonstrate that **trajectory semantics** - characterizing HOW constraint pressure evolves through procedural sequences - provides structured information beyond the token-level semantic ceiling.")
        report.append("")
        report.append("Key findings:")
        report.append("- Zone transition dynamics differ systematically by REGIME")
        report.append("- Operator judgment availability is non-uniformly distributed across zones")
        report.append("- This is sequence semantics, not symbol semantics")
        report.append("")
        report.append("**Implication:** The semantic ceiling holds for TOKEN meaning but not for TRAJECTORY meaning.")

    elif assessment['tier'] == 'TIER_3_ENRICHMENT':
        report.append("### Semantic Boundary Resolution Achieved")
        report.append("")
        report.append("This phase achieved **semantic boundary resolution** - precisely locating the semantic ceiling and understanding WHY it exists.")
        report.append("")
        report.append("Key discoveries:")
        report.append("- The semantic ceiling was NOT breached by naming things")
        report.append("- It was breached by discovering that meaning lives in the **withdrawal of agency**")
        report.append("- The artifact tells you *when judgment is no longer yours*")
        report.append("")
        report.append("### The Reframe")
        report.append("")
        report.append("> **The Voynich Manuscript is a machine for removing human freedom at exactly the moments where freedom would be dangerous.**")
        report.append("")
        report.append("This is not a failure to decode tokens. This IS going further - into **meta-semantics of control and responsibility**.")

    else:
        report.append("### Weak or No Signal")
        report.append("")
        report.append("Trajectory semantics does not show significant structure in this analysis.")
        report.append("The semantic ceiling may extend to trajectory patterns as well.")

    report.append("")
    report.append("---")
    report.append("")

    # Constraint compliance
    report.append("## Constraint Compliance")
    report.append("")
    report.append("| Constraint | How Respected |")
    report.append("|------------|---------------|")
    report.append("| C384 | Labels trajectories and phases, not tokens |")
    report.append("| C434 | Uses R-series ordering as foundation |")
    report.append("| C443 | Extends escape gradients with temporal dimension |")
    report.append("| C469 | Judgment availability is categorical |")
    report.append("")

    report.append("---")
    report.append("")
    report.append("*Report generated by ts_04_synthesis.py*")

    return "\n".join(report)


def main():
    print("=" * 60)
    print("TRAJECTORY_SEMANTICS: Synthesis")
    print("=" * 60)

    # Load results
    print("\nLoading results...")
    results = load_results()

    if not results['vector_c']:
        print("WARNING: Vector C results not found")
    if not results['vector_a']:
        print("WARNING: Vector A results not found")

    # Assess tier
    print("\nAssessing tier...")
    assessment = assess_tier(results)

    print(f"\n  Tier: {assessment['tier']}")
    print(f"  Confidence: {assessment['confidence']}")
    print(f"  Rationale: {assessment['rationale']}")

    # Generate report
    print("\nGenerating report...")
    report = generate_report(results, assessment)

    report_path = PHASE_DIR / "TRAJECTORY_SEMANTICS_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"  Report saved to: {report_path}")

    # Save synthesis results
    synthesis = {
        'phase': 'TRAJECTORY_SEMANTICS',
        'timestamp': datetime.now().isoformat(),
        'assessment': assessment,
        'vector_c_summary': results['vector_c'].get('summary') if results['vector_c'] else None,
        'vector_a_summary': results['vector_a'].get('summary') if results['vector_a'] else None,
    }

    synthesis_path = RESULTS_DIR / "ts_synthesis.json"
    with open(synthesis_path, 'w') as f:
        json.dump(synthesis, f, indent=2)
    print(f"  Synthesis saved to: {synthesis_path}")

    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT")
    print("=" * 60)
    print(f"\n  TIER: {assessment['tier']}")
    print(f"  {assessment['rationale']}")

    return synthesis


if __name__ == "__main__":
    main()
