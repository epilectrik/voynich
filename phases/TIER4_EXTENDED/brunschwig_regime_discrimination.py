"""
Phase: Brunschwig Regime Discrimination Test
Tier 4 SPECULATIVE

QUESTION: Do Voynich regimes discriminate between Brunschwig fire degrees?

Test:
- REGIME_1 should match FIRST DEGREE (balneum marie - forgiving)
- REGIME_3 should match THIRD DEGREE (seething - intensive)
- REGIME_4 should match precision operations (not forbidden, but constrained)

If regimes discriminate correctly, this is procedural alignment at regime level.
"""

import json
from pathlib import Path
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# =============================================================================
# BRUNSCHWIG FIRE DEGREES - STRUCTURAL PREDICTIONS
# =============================================================================

FIRE_DEGREES = {
    "FIRST_DEGREE": {
        "name": "Balneum Marie (Water Bath)",
        "materials": "Flowers, delicate aromatics",
        "quote": "Water never boils, finger can bear it",
        "predictions": {
            "cei_max": 0.55,        # Low energy
            "escape_min": 0.15,     # HIGH forgiveness
            "hazard_max": 0.65,     # Moderate hazard
            "expected_regime": "REGIME_1"
        }
    },
    "SECOND_DEGREE": {
        "name": "Warm Fire",
        "materials": "Standard herbs",
        "quote": "Noticeably warm",
        "predictions": {
            "cei_range": (0.35, 0.50),
            "escape_range": (0.08, 0.15),
            "expected_regime": "REGIME_2"
        }
    },
    "THIRD_DEGREE": {
        "name": "Seething Fire",
        "materials": "Roots, bark, resins",
        "quote": "Almost seething, sustained intensive heat",
        "predictions": {
            "cei_min": 0.65,        # HIGH energy
            "escape_max": 0.20,     # Lower forgiveness (but not zero)
            "hazard_min": 0.55,     # Higher hazard
            "expected_regime": "REGIME_3"
        }
    },
    "FOURTH_DEGREE": {
        "name": "Destructive Fire (FORBIDDEN by Brunschwig)",
        "materials": "NONE - categorically prohibited",
        "quote": "Fourth degree should be avoided at all times...coerces nature",
        "voynich_interpretation": "REGIME_4 = precision-constrained, NOT forbidden",
        "predictions": {
            "escape_max": 0.12,     # LOWEST forgiveness (narrowest tolerance)
            "expected_regime": "REGIME_4"
        }
    }
}


def load_regime_profiles():
    """Load all B folios grouped by regime."""
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        data = json.load(f)

    regimes = {}
    for folio_name, profile in data.get('profiles', {}).items():
        if profile.get('system') != 'B':
            continue
        b_metrics = profile.get('b_metrics', {})
        regime = b_metrics.get('regime')
        if not regime:
            continue

        if regime not in regimes:
            regimes[regime] = []

        regimes[regime].append({
            'folio': folio_name,
            'cei': b_metrics.get('cei_total', 0),
            'escape': b_metrics.get('escape_density', 0),
            'hazard': b_metrics.get('hazard_density', 0),
            'recovery': b_metrics.get('recovery_ops_count', 0),
            'intervention': b_metrics.get('intervention_frequency', 0)
        })

    return regimes


def compute_regime_stats(folios):
    """Compute aggregate statistics for a regime."""
    if not folios:
        return {}

    return {
        'count': len(folios),
        'cei_mean': statistics.mean(f['cei'] for f in folios),
        'cei_std': statistics.stdev(f['cei'] for f in folios) if len(folios) > 1 else 0,
        'escape_mean': statistics.mean(f['escape'] for f in folios),
        'escape_std': statistics.stdev(f['escape'] for f in folios) if len(folios) > 1 else 0,
        'hazard_mean': statistics.mean(f['hazard'] for f in folios),
        'hazard_std': statistics.stdev(f['hazard'] for f in folios) if len(folios) > 1 else 0,
    }


def test_degree_regime_alignment():
    """Test if regimes align with fire degrees."""
    regimes = load_regime_profiles()

    results = []

    # Test 1: REGIME_1 = First Degree (forgiving)
    r1_stats = compute_regime_stats(regimes.get('REGIME_1', []))
    first = FIRE_DEGREES['FIRST_DEGREE']['predictions']
    test1 = {
        'test': 'REGIME_1 = FIRST_DEGREE',
        'predictions': {
            'cei_max': first['cei_max'],
            'escape_min': first['escape_min'],
            'hazard_max': first['hazard_max']
        },
        'actual': {
            'cei_mean': r1_stats.get('cei_mean'),
            'escape_mean': r1_stats.get('escape_mean'),
            'hazard_mean': r1_stats.get('hazard_mean')
        },
        'checks': []
    }
    test1['checks'].append(('CEI <= max', r1_stats.get('cei_mean', 1) <= first['cei_max']))
    test1['checks'].append(('Escape >= min', r1_stats.get('escape_mean', 0) >= first['escape_min']))
    test1['checks'].append(('Hazard <= max', r1_stats.get('hazard_mean', 1) <= first['hazard_max']))
    test1['passed'] = all(c[1] for c in test1['checks'])
    results.append(test1)

    # Test 2: REGIME_3 = Third Degree (intensive)
    r3_stats = compute_regime_stats(regimes.get('REGIME_3', []))
    third = FIRE_DEGREES['THIRD_DEGREE']['predictions']
    test2 = {
        'test': 'REGIME_3 = THIRD_DEGREE',
        'predictions': {
            'cei_min': third['cei_min'],
            'escape_max': third['escape_max'],
            'hazard_min': third['hazard_min']
        },
        'actual': {
            'cei_mean': r3_stats.get('cei_mean'),
            'escape_mean': r3_stats.get('escape_mean'),
            'hazard_mean': r3_stats.get('hazard_mean')
        },
        'checks': []
    }
    test2['checks'].append(('CEI >= min', r3_stats.get('cei_mean', 0) >= third['cei_min']))
    test2['checks'].append(('Escape <= max', r3_stats.get('escape_mean', 1) <= third['escape_max']))
    test2['checks'].append(('Hazard >= min', r3_stats.get('hazard_mean', 0) >= third['hazard_min']))
    test2['passed'] = all(c[1] for c in test2['checks'])
    results.append(test2)

    # Test 3: REGIME_4 = Precision (narrowest tolerance)
    r4_stats = compute_regime_stats(regimes.get('REGIME_4', []))
    fourth = FIRE_DEGREES['FOURTH_DEGREE']['predictions']
    test3 = {
        'test': 'REGIME_4 = PRECISION (lowest escape)',
        'predictions': {
            'escape_max': fourth['escape_max'],
        },
        'actual': {
            'escape_mean': r4_stats.get('escape_mean'),
        },
        'checks': []
    }
    test3['checks'].append(('Escape <= max (narrowest)', r4_stats.get('escape_mean', 1) <= fourth['escape_max']))
    test3['passed'] = all(c[1] for c in test3['checks'])
    results.append(test3)

    # Test 4: REGIME_2 = Second Degree (baseline simple)
    r2_stats = compute_regime_stats(regimes.get('REGIME_2', []))
    second = FIRE_DEGREES['SECOND_DEGREE']['predictions']
    cei_min, cei_max = second['cei_range']
    escape_min, escape_max = second['escape_range']
    test4 = {
        'test': 'REGIME_2 = SECOND_DEGREE',
        'predictions': {
            'cei_range': second['cei_range'],
            'escape_range': second['escape_range'],
        },
        'actual': {
            'cei_mean': r2_stats.get('cei_mean'),
            'escape_mean': r2_stats.get('escape_mean'),
        },
        'checks': []
    }
    test4['checks'].append(('CEI in range', cei_min <= r2_stats.get('cei_mean', -1) <= cei_max))
    test4['checks'].append(('Escape in range', escape_min <= r2_stats.get('escape_mean', -1) <= escape_max))
    test4['passed'] = all(c[1] for c in test4['checks'])
    results.append(test4)

    # Test 5: Ordering (REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3 by CEI)
    cei_values = {
        'REGIME_1': r1_stats.get('cei_mean', 0),
        'REGIME_2': r2_stats.get('cei_mean', 0),
        'REGIME_3': r3_stats.get('cei_mean', 0),
        'REGIME_4': r4_stats.get('cei_mean', 0),
    }
    expected_order = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
    actual_order = sorted(cei_values.keys(), key=lambda r: cei_values[r])
    test5 = {
        'test': 'CEI ORDERING (energy escalation)',
        'predictions': {
            'expected_order': expected_order
        },
        'actual': {
            'actual_order': actual_order,
            'cei_values': cei_values
        },
        'checks': []
    }
    test5['checks'].append(('Order matches', actual_order == expected_order))
    test5['passed'] = all(c[1] for c in test5['checks'])
    results.append(test5)

    # Test 6: Escape ordering (REGIME_1 > REGIME_3 > REGIME_2 > REGIME_4)
    escape_values = {
        'REGIME_1': r1_stats.get('escape_mean', 0),
        'REGIME_2': r2_stats.get('escape_mean', 0),
        'REGIME_3': r3_stats.get('escape_mean', 0),
        'REGIME_4': r4_stats.get('escape_mean', 0),
    }
    # Forgiving -> Constrained
    # First degree most forgiving, Fourth most constrained
    expected_escape = ['REGIME_1', 'REGIME_3', 'REGIME_2', 'REGIME_4']
    actual_escape = sorted(escape_values.keys(), key=lambda r: -escape_values[r])
    test6 = {
        'test': 'ESCAPE ORDERING (forgiveness)',
        'predictions': {
            'expected_order': expected_escape
        },
        'actual': {
            'actual_order': actual_escape,
            'escape_values': escape_values
        },
        'checks': []
    }
    test6['checks'].append(('Order matches', actual_escape == expected_escape))
    test6['passed'] = all(c[1] for c in test6['checks'])
    results.append(test6)

    return results, regimes


def main():
    print("=" * 70)
    print("BRUNSCHWIG FIRE DEGREE - VOYNICH REGIME DISCRIMINATION TEST")
    print("=" * 70)

    print("\n--- Brunschwig's Four Degrees of Fire ---")
    for degree, info in FIRE_DEGREES.items():
        print(f"\n{degree}:")
        print(f"  Name: {info['name']}")
        print(f"  Materials: {info['materials']}")
        print(f"  Quote: \"{info['quote']}\"")

    results, regimes = test_degree_regime_alignment()

    print("\n" + "=" * 70)
    print("REGIME STATISTICS")
    print("=" * 70)

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        stats = compute_regime_stats(regimes.get(regime, []))
        print(f"\n{regime} (n={stats.get('count', 0)}):")
        print(f"  CEI:    {stats.get('cei_mean', 0):.3f} ± {stats.get('cei_std', 0):.3f}")
        print(f"  Escape: {stats.get('escape_mean', 0):.3f} ± {stats.get('escape_std', 0):.3f}")
        print(f"  Hazard: {stats.get('hazard_mean', 0):.3f} ± {stats.get('hazard_std', 0):.3f}")

    print("\n" + "=" * 70)
    print("DISCRIMINATION TESTS")
    print("=" * 70)

    passed = 0
    for r in results:
        print(f"\n{r['test']}:")
        for check_name, check_result in r['checks']:
            status = "PASS" if check_result else "FAIL"
            print(f"  {check_name}: {status}")
        overall = "PASS" if r['passed'] else "FAIL"
        print(f"  --> {overall}")
        if r['passed']:
            passed += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nTests Passed: {passed}/{len(results)}")

    if passed == len(results):
        verdict = "PERFECT_DISCRIMINATION"
        interpretation = """
All four Voynich regimes align with Brunschwig's four fire degrees:

| Voynich | Brunschwig | Meaning |
|---------|------------|---------|
| REGIME_2 | Second (warm) | Simple baseline procedures |
| REGIME_1 | First (balneum) | Forgiving volatile handling |
| REGIME_4 | Fourth* | Precision-constrained (NOT forbidden) |
| REGIME_3 | Third (seething) | Intensive multi-phase operations |

*REGIME_4 reinterpretation: Voynich provides the engineering alternative to
Brunschwig's moral prohibition. Same narrow tolerance, different framing.

THIS IS PROCEDURAL ALIGNMENT AT THE REGIME LEVEL.
"""
    elif passed >= 4:
        verdict = "STRONG_DISCRIMINATION"
        interpretation = f"""
{passed}/6 tests passed. Voynich regimes strongly discriminate between
Brunschwig fire degree profiles. Minor deviations may reflect:
- Voynich's engineering vs Brunschwig's pedagogical framing
- Different material distributions in each corpus
"""
    elif passed >= 2:
        verdict = "PARTIAL_DISCRIMINATION"
        interpretation = f"""
{passed}/6 tests passed. Some alignment between Voynich regimes and
Brunschwig fire degrees, but not complete correspondence.
"""
    else:
        verdict = "WEAK_DISCRIMINATION"
        interpretation = f"""
Only {passed}/6 tests passed. Voynich regimes do not clearly align with
Brunschwig's fire degree system.
"""

    print(f"\nVERDICT: {verdict}")
    print(interpretation)

    # Save results
    output = {
        "test": "BRUNSCHWIG_REGIME_DISCRIMINATION",
        "tier": 4,
        "status": "SPECULATIVE",
        "date": "2026-01-14",
        "tests_passed": passed,
        "tests_total": len(results),
        "regime_stats": {
            regime: compute_regime_stats(regimes.get(regime, []))
            for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
        },
        "test_results": [
            {
                'test': r['test'],
                'passed': r['passed'],
                'checks': r['checks']
            }
            for r in results
        ],
        "verdict": verdict
    }

    with open(RESULTS_DIR / "brunschwig_regime_discrimination.json", 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to results/brunschwig_regime_discrimination.json")


if __name__ == "__main__":
    main()
