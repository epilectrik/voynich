#!/usr/bin/env python3
"""
bc_07_synthesis.py - Aggregate results and compute tier assessment

Combines results from H1-H4 and generates phase report.
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
PHASE_DIR = Path(__file__).parent


def load_result(filename):
    """Load a result file."""
    path = RESULTS_DIR / filename
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: Synthesis")
    print("=" * 70)
    print()

    # Load all hypothesis results
    h1_result = load_result("bc_freedom_correlation.json")
    h2_result = load_result("bc_scaffold_correlation.json")
    h3_result = load_result("bc_interaction_test.json")
    h4_result = load_result("bc_complementarity_ratio.json")

    # Check which tests ran
    hypothesis_results = []

    if h1_result:
        hypothesis_results.append({
            'hypothesis': 'H1',
            'name': 'Explanation vs Judgment Freedom',
            'prediction': 'Inverse correlation with freedom',
            'passed': h1_result['evaluation']['passed'],
            'key_metric': f"rho={h1_result['statistics']['spearman_rho']}"
        })
        print(f"H1: {'PASS' if h1_result['evaluation']['passed'] else 'FAIL'}")
    else:
        print("H1: NOT RUN")

    if h2_result:
        hypothesis_results.append({
            'hypothesis': 'H2',
            'name': 'Explanation vs Scaffold Rigidity',
            'prediction': 'UNIFORM < VARIED',
            'passed': h2_result['evaluation']['passed'],
            'key_metric': f"d={h2_result['statistics']['cohens_d']}"
        })
        print(f"H2: {'PASS' if h2_result['evaluation']['passed'] else 'FAIL'}")
    else:
        print("H2: NOT RUN")

    if h3_result:
        hypothesis_results.append({
            'hypothesis': 'H3',
            'name': 'Interaction > Main Effects',
            'prediction': 'Interaction adds variance',
            'passed': h3_result['evaluation']['passed'],
            'key_metric': f"dR2={h3_result['model_comparison']['delta_r2_interaction']}"
        })
        print(f"H3: {'PASS' if h3_result['evaluation']['passed'] else 'FAIL'}")
    else:
        print("H3: NOT RUN")

    if h4_result:
        hypothesis_results.append({
            'hypothesis': 'H4',
            'name': 'Complementarity Ratio',
            'prediction': 'Stable ratio across regimes',
            'passed': h4_result['evaluation']['passed'],
            'key_metric': f"cv={h4_result['ratio_statistics']['cv']}"
        })
        print(f"H4: {'PASS' if h4_result['evaluation']['passed'] else 'FAIL'}")
    else:
        print("H4: NOT RUN")

    # Count passes
    total_tests = len(hypothesis_results)
    total_passed = sum(1 for h in hypothesis_results if h['passed'])

    print(f"\nTotal: {total_passed}/{total_tests} passed")

    # Tier assessment
    print("\n" + "-" * 70)
    print("TIER ASSESSMENT")
    print("-" * 70)

    if total_passed == 4:
        tier = "TIER_2"
        confidence = "HIGH"
        rationale = "Strong complementarity: 4/4 hypotheses passed"
    elif total_passed == 3:
        tier = "TIER_3"
        confidence = "MODERATE"
        rationale = "Partial complementarity: 3/4 hypotheses passed"
    elif total_passed == 2:
        tier = "TIER_4"
        confidence = "LOW"
        rationale = "Weak signal: 2/4 hypotheses passed"
    elif total_passed == 1:
        tier = "TIER_4"
        confidence = "VERY_LOW"
        rationale = "Suggestive only: 1/4 hypotheses passed"
    else:
        tier = "FALSIFIED"
        confidence = "N/A"
        rationale = "No complementarity evidence: 0/4 hypotheses passed"

    print(f"\nTier: {tier}")
    print(f"Confidence: {confidence}")
    print(f"Rationale: {rationale}")

    # Key finding
    if total_passed >= 2:
        if h1_result and h1_result['evaluation']['passed']:
            key_finding = "Explanation density inversely correlates with judgment freedom."
        elif h2_result and h2_result['evaluation']['passed']:
            key_finding = "Scaffold rigidity predicts lower explanation density."
        elif h4_result and h4_result['evaluation']['passed']:
            key_finding = "Complementarity ratio shows stable partitioning."
        else:
            key_finding = "Interaction between freedom and pacing affects explanation density."
    else:
        key_finding = "No systematic explanation-enforcement complementarity detected."

    print(f"\nKey Finding: {key_finding}")

    # Save synthesis results
    synthesis = {
        'phase': 'BC_EXPLANATION_ENFORCEMENT',
        'timestamp': datetime.now().isoformat(),
        'hypothesis_results': hypothesis_results,
        'total_passed': total_passed,
        'total_tests': total_tests,
        'tier_assessment': {
            'tier': tier,
            'confidence': confidence,
            'rationale': rationale
        },
        'key_finding': key_finding
    }

    output_path = RESULTS_DIR / "bc_synthesis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(synthesis, f, indent=2)
    print(f"\nSynthesis saved to: {output_path}")

    # Generate report
    report = generate_report(synthesis, h1_result, h2_result, h3_result, h4_result)
    report_path = PHASE_DIR / "BC_EXPLANATION_ENFORCEMENT_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    return synthesis


def generate_report(synthesis, h1, h2, h3, h4):
    """Generate markdown report."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")

    report = f"""# BC_EXPLANATION_ENFORCEMENT Phase Report

**Generated:** {timestamp}
**Status:** COMPLETE

## Executive Summary

**Tier Assessment:** {synthesis['tier_assessment']['tier']}
**Confidence:** {synthesis['tier_assessment']['confidence']}
**Rationale:** {synthesis['tier_assessment']['rationale']}

> **Key Finding:** {synthesis['key_finding']}

---

## Hypothesis Results

**Passed:** {synthesis['total_passed']}/{synthesis['total_tests']}

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
"""

    for h in synthesis['hypothesis_results']:
        status = "**PASS**" if h['passed'] else "FAIL"
        report += f"| {h['hypothesis']} | {h['prediction'][:40]}... | {h['key_metric']} | {status} |\n"

    report += """
---

## Detailed Results

"""

    if h1:
        report += f"""### H1: Explanation vs Judgment Freedom

**Prediction:** Inverse correlation between explanation density and judgment freedom
**Threshold:** Spearman rho < -0.3, p < 0.05

**Results:**
- Spearman rho: {h1['statistics']['spearman_rho']}
- p-value: {h1['statistics']['p_value']}
- Direction: {h1['statistics']['direction']}
- **Verdict:** {'PASS' if h1['evaluation']['passed'] else 'FAIL'}

"""

    if h2:
        report += f"""### H2: Explanation vs Scaffold Rigidity

**Prediction:** UNIFORM scaffolds have lower explanation density than VARIED
**Threshold:** Mann-Whitney p < 0.05, effect size d > 0.3

**Results:**
- UNIFORM mean: {h2['descriptive']['uniform']['mean']} (n={h2['group_sizes']['uniform']})
- VARIED mean: {h2['descriptive']['varied']['mean']} (n={h2['group_sizes']['varied']})
- Cohen's d: {h2['statistics']['cohens_d']}
- p-value: {h2['statistics']['p_value']}
- **Verdict:** {'PASS' if h2['evaluation']['passed'] else 'FAIL'}

"""

    if h3:
        report += f"""### H3: Interaction > Main Effects

**Prediction:** Freedom x Pacing interaction explains more variance than main effects
**Threshold:** Delta R² > 0.05, p < 0.05

**Results:**
- R² (freedom only): {h3['model_comparison']['r2_freedom_only']}
- R² (pacing only): {h3['model_comparison']['r2_pacing_only']}
- R² (main effects): {h3['model_comparison']['r2_main_effects']}
- R² (with interaction): {h3['model_comparison']['r2_full_model']}
- Delta R²: {h3['model_comparison']['delta_r2_interaction']}
- p-value: {h3['statistics']['p_value']}
- **Verdict:** {'PASS' if h3['evaluation']['passed'] else 'FAIL'}

"""

    if h4:
        report += f"""### H4: Complementarity Ratio

**Prediction:** Explanation/constraint ratio should be stable across regimes
**Threshold:** Ratio CV < Density CV, homogeneous across regimes

**Results:**
- Density CV: {h4['comparison']['density_cv']}
- Ratio CV: {h4['comparison']['ratio_cv']}
- CV Reduction: {h4['comparison']['cv_reduction_pct']}%
- Bartlett p (homogeneity): {h4['statistics']['bartlett_p']}
- **Verdict:** {'PASS' if h4['evaluation']['passed'] else 'FAIL'}

"""

    report += """---

## Interpretation

"""

    if synthesis['total_passed'] >= 3:
        report += """This phase provides evidence for **explanation-enforcement complementarity**:
Where Voynich enforces more (high constraint), Brunschwig explains less.
Where Voynich enforces less (high freedom), Brunschwig explains more.

This supports the hypothesis that the two systems partition responsibility
between machine (enforcement) and human (pedagogy).
"""
    elif synthesis['total_passed'] >= 1:
        report += """This phase provides **partial evidence** for explanation-enforcement complementarity.
Some relationships between Brunschwig verbosity and Voynich constraint are detectable,
but the partitioning is not systematic across all measures.
"""
    else:
        report += """This phase **does not support** explanation-enforcement complementarity.
Brunschwig pedagogy does not systematically vary with Voynich constraint levels.
The relationship between the texts is curriculum-level, not interface-level.
"""

    report += """
---

## Constraint Compliance

| Constraint | How Respected |
|------------|---------------|
| C384 | No token-to-referent mapping; aggregate pedagogical behavior only |
| C430 | Family separation (Zodiac vs A/C) maintained |
| No semantic decoding | Testing explanation DENSITY, not meaning |

---

*Report generated by bc_07_synthesis.py*
"""

    return report


if __name__ == "__main__":
    main()
