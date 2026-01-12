#!/usr/bin/env python3
"""
Efficiency Regime Test: Synthesis of Results

Combines all test results and determines overall verdict according to
pre-declared interpretation matrix.

Interpretation Matrix:
| Test 2 | Test 1 | Test 4 | Test 3 | Verdict |
|--------|--------|--------|--------|---------|
| + | + | + | + | STRONGLY SUPPORTED |
| + | + | + | - | SUPPORTED (escape mechanism weaker) |
| + | + | - | + | ANOMALY (investigate universal behavior) |
| + | - | + | + | PARTIAL (discrimination only, not brittleness) |
| - | * | * | * | NOT SUPPORTED (stop) |
"""

import json
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent
RESULTS_DIR = BASE_PATH / "results"
OUTPUT_FILE = RESULTS_DIR / "efficiency_regime_synthesis.json"


def load_results():
    """Load all test results."""
    results = {}

    # Test 2: MIDDLE discrimination
    t2_path = RESULTS_DIR / "efficiency_regime_middle_discrimination.json"
    if t2_path.exists():
        with open(t2_path, 'r') as f:
            results['test_2'] = json.load(f)

    # Test 1: Residual brittleness
    t1_path = RESULTS_DIR / "efficiency_regime_residual_brittleness.json"
    if t1_path.exists():
        with open(t1_path, 'r') as f:
            results['test_1'] = json.load(f)

    # Test 4: Negative control
    t4_path = RESULTS_DIR / "efficiency_regime_negative_control.json"
    if t4_path.exists():
        with open(t4_path, 'r') as f:
            results['test_4'] = json.load(f)

    # Test 3: Family escape
    t3_path = RESULTS_DIR / "efficiency_regime_family_escape.json"
    if t3_path.exists():
        with open(t3_path, 'r') as f:
            results['test_3'] = json.load(f)

    return results


def interpret_test(test_name, result):
    """Interpret individual test result as +, -, or ~"""
    if test_name == 'test_2':
        verdict = result.get('verdict', {}).get('overall', '')
        if verdict == 'GRADIENT_SUPPORTED':
            return '+'
        elif verdict in ['WEAK_SUPPORT']:
            return '~'  # Partial
        else:
            return '-'

    elif test_name == 'test_1':
        verdict = result.get('verdict', {}).get('overall', '')
        if verdict == 'TEST_1_PASSED':
            return '+'
        elif verdict in ['TEST_1_FAILED', 'TEST_1_FAILED_PREFIX']:
            return '-'
        else:
            return '~'

    elif test_name == 'test_4':
        verdict = result.get('verdict', {}).get('overall', '')
        if verdict == 'NEGATIVE_CONTROL_PASSED':
            return '+'
        elif verdict == 'NEGATIVE_CONTROL_FAILED':
            return '-'
        else:
            return '~'

    elif test_name == 'test_3':
        verdict = result.get('verdict', {}).get('overall', '')
        if verdict == 'TEST_3_PASSED':
            return '+'
        elif verdict == 'TEST_3_PARTIAL':
            return '~'
        else:
            return '-'

    return '?'


def determine_overall_verdict(interpretations):
    """Apply the pre-declared interpretation matrix."""
    t2 = interpretations.get('test_2', '?')
    t1 = interpretations.get('test_1', '?')
    t4 = interpretations.get('test_4', '?')
    t3 = interpretations.get('test_3', '?')

    # Pre-declared stop condition: If Test 2 fails, stop
    if t2 == '-':
        return 'NOT_SUPPORTED', 'Test 2 failed - efficiency-regime hypothesis is NOT SUPPORTED'

    # Apply matrix
    if t2 == '+' and t1 == '+' and t4 == '+' and t3 == '+':
        return 'STRONGLY_SUPPORTED', 'All tests passed - strong evidence for efficiency regimes'

    if t2 == '+' and t1 == '+' and t4 == '+' and t3 in ['-', '~']:
        return 'SUPPORTED', 'Core tests passed - escape mechanism unclear but regime effect present'

    if t2 == '+' and t1 == '+' and t4 == '-':
        return 'ANOMALY', 'Core tests passed but negative control failed - investigate'

    if t2 == '+' and t1 == '-' and t4 == '+':
        return 'PARTIAL_DISCRIMINATION', 'Regime explains discrimination but not brittleness'

    if t2 == '~' and t1 == '-' and t4 == '+':
        return 'WEAK_PARTIAL', 'Weak discrimination evidence, no brittleness effect, but negative control passed'

    if t2 == '~' and t4 == '+':
        return 'PARTIAL_STRUCTURAL', 'Structural evidence present but behavioral predictions weak'

    # Default
    return 'INCONCLUSIVE', 'Mixed results - further investigation needed'


def main():
    print("=" * 70)
    print("EFFICIENCY REGIME HYPOTHESIS: SYNTHESIS OF ALL TESTS")
    print("=" * 70)
    print()

    # Load results
    results = load_results()

    if not results:
        print("ERROR: No test results found")
        return

    # Interpret each test
    interpretations = {}
    for test_name, result in results.items():
        interp = interpret_test(test_name, result)
        interpretations[test_name] = interp

    # Display individual results
    print("INDIVIDUAL TEST RESULTS")
    print("-" * 70)

    test_names = {
        'test_2': 'MIDDLE Discrimination Pressure (CRITICAL)',
        'test_1': 'Residual Brittleness Analysis (PRIMARY)',
        'test_4': 'Universal MIDDLE Negative Control (CRITICAL)',
        'test_3': 'Family Escape Transfer (CONFIRMATORY)'
    }

    for test_id in ['test_2', 'test_1', 'test_4', 'test_3']:
        if test_id in results:
            result = results[test_id]
            verdict = result.get('verdict', {}).get('overall', 'UNKNOWN')
            interp = result.get('verdict', {}).get('interpretation', '')
            symbol = interpretations[test_id]

            print(f"\n{test_names[test_id]}:")
            print(f"   Verdict: {verdict}")
            print(f"   Interpretation: {interp}")
            print(f"   Matrix Entry: {symbol}")

    # Overall verdict
    print("\n" + "=" * 70)
    print("OVERALL VERDICT")
    print("=" * 70)

    overall, explanation = determine_overall_verdict(interpretations)

    print(f"\nMatrix entries: T2={interpretations.get('test_2','?')} T1={interpretations.get('test_1','?')} T4={interpretations.get('test_4','?')} T3={interpretations.get('test_3','?')}")
    print(f"\n>>> {overall} <<<")
    print(f"    {explanation}")

    # Action items
    print("\n" + "-" * 70)
    print("RECOMMENDED ACTIONS")
    print("-" * 70)

    if overall == 'NOT_SUPPORTED':
        print("- Update efficiency_regimes.md status to FALSIFIED")
        print("- Remove from INTERPRETATION_SUMMARY.md")
        print("- Document as negative result in CHANGELOG")
    elif overall in ['STRONGLY_SUPPORTED', 'SUPPORTED']:
        print("- Update efficiency_regimes.md with test citations")
        print("- Consider 'Validated Tier 3 Speculation' status")
        print("- Document in CHANGELOG")
    elif overall in ['PARTIAL_DISCRIMINATION', 'WEAK_PARTIAL', 'PARTIAL_STRUCTURAL']:
        print("- Update efficiency_regimes.md with partial support notes")
        print("- Document specific findings in CHANGELOG")
        print("- Consider refined hypothesis focusing on MIDDLE discrimination")
    else:
        print("- Document current findings")
        print("- May need additional investigation")

    # Save synthesis
    synthesis = {
        'hypothesis': 'Efficiency Regime Interpretation',
        'tests': {
            'test_2': {
                'name': 'MIDDLE Discrimination Pressure',
                'result': interpretations.get('test_2', '?'),
                'verdict': results.get('test_2', {}).get('verdict', {})
            },
            'test_1': {
                'name': 'Residual Brittleness Analysis',
                'result': interpretations.get('test_1', '?'),
                'verdict': results.get('test_1', {}).get('verdict', {})
            },
            'test_4': {
                'name': 'Universal MIDDLE Negative Control',
                'result': interpretations.get('test_4', '?'),
                'verdict': results.get('test_4', {}).get('verdict', {})
            },
            'test_3': {
                'name': 'Family Escape Transfer',
                'result': interpretations.get('test_3', '?'),
                'verdict': results.get('test_3', {}).get('verdict', {})
            }
        },
        'matrix': {
            'T2': interpretations.get('test_2', '?'),
            'T1': interpretations.get('test_1', '?'),
            'T4': interpretations.get('test_4', '?'),
            'T3': interpretations.get('test_3', '?')
        },
        'overall': {
            'verdict': overall,
            'explanation': explanation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(synthesis, f, indent=2)

    print(f"\n\nSynthesis saved to: {OUTPUT_FILE}")

    return synthesis


if __name__ == "__main__":
    main()
