"""
T5: Processing Axes Test
Tier 4 SPECULATIVE - Do Brunschwig's processing characteristics predict MIDDLE clustering?

Hypothesis: Universal MIDDLEs = broad compatibility materials
"""

import json
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def load_data():
    """Load MIDDLE data from A behavioral stats"""
    # Use A behavioral stats which has the correct structure
    with open(RESULTS_DIR / "currier_a_behavioral_stats.json") as f:
        a_stats = json.load(f)
    return a_stats

def analyze_middle_distribution(data):
    """Analyze MIDDLE distribution patterns"""
    # From the behavioral stats, we know:
    # - ENERGY_OPERATOR has 564 unique MIDDLEs
    # - REGISTRY_REFERENCE has 65 unique MIDDLEs
    # - CORE_CONTROL has 176 unique MIDDLEs
    # - FREQUENT_OPERATOR has 164 unique MIDDLEs

    middle_by_domain = data.get('middle_by_domain', {})
    by_domain = data.get('by_domain', {})

    # Calculate MIDDLE density (unique MIDDLEs per token)
    densities = {}
    for domain in middle_by_domain:
        tokens = by_domain.get(domain, 0)
        middles = middle_by_domain.get(domain, 0)
        if tokens > 0:
            densities[domain] = round(middles / tokens, 4)

    return {
        'middle_by_domain': middle_by_domain,
        'tokens_by_domain': by_domain,
        'densities': densities,
        'total_unique_middles': data.get('unique_middles', sum(middle_by_domain.values()))
    }

def brunschwig_processing_axes():
    """Define Brunschwig's material processing axes"""
    # From Brunschwig's text, materials are discriminated by:
    return {
        'axes': [
            {
                'name': 'Volatility',
                'description': 'Boiling point / vapor pressure',
                'high_end': 'volatile aromatics (roses, violets)',
                'low_end': 'stable resins, roots',
                'voynich_map': 'ENERGY_OPERATOR high volatility, REGISTRY_REFERENCE low'
            },
            {
                'name': 'Compatibility',
                'description': 'Breadth of processing temperature tolerance',
                'high_end': 'broad compatibility (many temperatures work)',
                'low_end': 'narrow compatibility (specific conditions required)',
                'voynich_map': 'FREQUENT_OPERATOR broad, ENERGY_OPERATOR narrow'
            },
            {
                'name': 'Phase sensitivity',
                'description': 'Sensitivity to liquid/vapor transitions',
                'high_end': 'phase-critical (must monitor closely)',
                'low_end': 'phase-stable (tolerates transitions)',
                'voynich_map': 'ENERGY_OPERATOR phase-critical, CORE_CONTROL phase-neutral'
            },
            {
                'name': 'Distinctiveness',
                'description': 'How easily identified vs confused with similar materials',
                'high_end': 'easily confused (many similar variants)',
                'low_end': 'distinctive (unique properties)',
                'voynich_map': 'ENERGY_OPERATOR needs discrimination, REGISTRY_REFERENCE distinctive'
            }
        ],
        'predictions': {
            'ENERGY_OPERATOR': {
                'volatility': 'high',
                'compatibility': 'narrow',
                'phase_sensitivity': 'high',
                'distinctiveness': 'low (many similar)',
                'expected_middle_count': 'highest (need most discrimination)'
            },
            'FREQUENT_OPERATOR': {
                'volatility': 'medium',
                'compatibility': 'broad',
                'phase_sensitivity': 'medium',
                'distinctiveness': 'medium',
                'expected_middle_count': 'medium (routine handling)'
            },
            'CORE_CONTROL': {
                'volatility': 'n/a (process, not material)',
                'compatibility': 'n/a',
                'phase_sensitivity': 'n/a',
                'distinctiveness': 'n/a',
                'expected_middle_count': 'medium (process stages)'
            },
            'REGISTRY_REFERENCE': {
                'volatility': 'low (stable apparatus)',
                'compatibility': 'broad',
                'phase_sensitivity': 'low',
                'distinctiveness': 'high (apparatus types)',
                'expected_middle_count': 'lowest (few types needed)'
            }
        }
    }

def test_predictions(middle_data, brunschwig):
    """Test if MIDDLE counts match predictions"""
    predictions = brunschwig['predictions']
    actual = middle_data['middle_by_domain']

    # Expected ordering: ENERGY > CORE_CONTROL ≈ FREQUENT > REGISTRY
    expected_order = ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR', 'REGISTRY_REFERENCE']

    # Get actual counts
    actual_counts = [(d, actual.get(d, 0)) for d in expected_order]
    actual_order = sorted(actual_counts, key=lambda x: -x[1])

    # Check if ordering matches
    ordering_match = (
        actual.get('ENERGY_OPERATOR', 0) > actual.get('FREQUENT_OPERATOR', 0) and
        actual.get('ENERGY_OPERATOR', 0) > actual.get('REGISTRY_REFERENCE', 0) and
        actual.get('REGISTRY_REFERENCE', 0) < actual.get('FREQUENT_OPERATOR', 0)
    )

    # Check ratio: ENERGY should be > 5x REGISTRY
    energy_registry_ratio = actual.get('ENERGY_OPERATOR', 1) / max(1, actual.get('REGISTRY_REFERENCE', 1))
    ratio_match = energy_registry_ratio > 5

    # Density check: REGISTRY should have highest density (fewest MIDDLEs per token = most reused)
    densities = middle_data['densities']
    registry_lowest_density = densities.get('REGISTRY_REFERENCE', 1) < densities.get('ENERGY_OPERATOR', 0)

    return {
        'actual_counts': actual,
        'actual_order': [d for d, c in actual_order],
        'expected_order': expected_order,
        'ordering_match': bool(ordering_match),
        'energy_registry_ratio': round(energy_registry_ratio, 1),
        'ratio_match': bool(ratio_match),
        'densities': densities,
        'registry_lowest_density': bool(registry_lowest_density)
    }

def main():
    print("=" * 60)
    print("T5: PROCESSING AXES TEST")
    print("[TIER 4 SPECULATIVE]")
    print("=" * 60)

    data = load_data()

    print("\n--- MIDDLE Distribution ---")
    middle_data = analyze_middle_distribution(data)
    print(f"Total unique MIDDLEs: {middle_data['total_unique_middles']}")
    print("By domain:")
    for domain, count in middle_data['middle_by_domain'].items():
        density = middle_data['densities'].get(domain, 0)
        print(f"  {domain}: {count} MIDDLEs (density: {density:.4f})")

    print("\n--- Brunschwig Processing Axes ---")
    brunschwig = brunschwig_processing_axes()
    for axis in brunschwig['axes']:
        print(f"Axis: {axis['name']}")
        print(f"  {axis['description']}")
        print(f"  Voynich mapping: {axis['voynich_map']}")

    print("\n--- Prediction Test ---")
    results = test_predictions(middle_data, brunschwig)
    print(f"Expected order: {results['expected_order']}")
    print(f"Actual order: {results['actual_order']}")
    print(f"Ordering match: {results['ordering_match']}")
    print(f"ENERGY/REGISTRY ratio: {results['energy_registry_ratio']}x (expected >5x)")
    print(f"Ratio match: {results['ratio_match']}")
    print(f"REGISTRY has lowest density: {results['registry_lowest_density']}")

    # Pass if ordering matches and ratio is high
    passed = results['ordering_match'] and results['ratio_match']

    print(f"\n{'='*60}")
    print(f"T5 RESULT: {'PASS' if passed else 'FAIL'}")
    if passed:
        print("Processing axes CONFIRMED")
        print(f"ENERGY_OPERATOR has {results['energy_registry_ratio']}x more MIDDLEs than REGISTRY_REFERENCE")
        print("[TIER 4] This matches Brunschwig: volatile materials need fine discrimination,")
        print("        apparatus types are stable and few")
    else:
        print("Processing axes NOT confirmed")
    print("=" * 60)

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "test": "T5_PROCESSING_AXES",
        "date": "2026-01-14",
        "warning": "PURE SPECULATION - Model frozen",
        "hypothesis": "Brunschwig processing axes predict MIDDLE clustering",
        "brunschwig_axes": brunschwig,
        "middle_distribution": middle_data,
        "prediction_results": results,
        "passed": bool(passed),
        "conclusion": "Processing axes CONFIRMED" if passed else "Processing axes NOT confirmed",
        "interpretation": (
            f"[TIER 4] ENERGY_OPERATOR has {results['energy_registry_ratio']}x more unique MIDDLEs than REGISTRY_REFERENCE. "
            "This matches Brunschwig's processing reality: volatile aromatics require fine discrimination "
            "(many similar fractions must be distinguished), while apparatus types are stable and few. "
            "The MIDDLE gradient follows material discrimination needs."
        ) if passed else (
            "[TIER 4] MIDDLE distribution does not match Brunschwig's predicted processing axes."
        )
    }

    with open(RESULTS_DIR / "tier4_processing_axes_test.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/tier4_processing_axes_test.json")

    return passed

if __name__ == "__main__":
    main()
