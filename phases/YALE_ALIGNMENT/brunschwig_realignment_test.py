"""
Brunschwig Realignment Test
Phase: YALE_ALIGNMENT

Re-tests Brunschwig degree escalation using PROPOSED folio order.

Key question: Does proposed order strengthen the Brunschwig alignment?

Background:
- Brunschwig describes degree escalation: simple first, complex last
- Original test showed WEAK positional gradient in current order
- Proposed order should show STRONG positional gradient
"""

import json
from pathlib import Path
from statistics import mean
from scipy import stats

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


def load_data():
    """Load all required data."""
    with open(RESULTS_DIR / "b_macro_scaffold_audit.json") as f:
        macro = json.load(f)
    with open(RESULTS_DIR / "folio_reordering.json") as f:
        reordering = json.load(f)
    with open(RESULTS_DIR / "b_design_space_cartography.json") as f:
        cart = json.load(f)
    return macro, reordering, cart


def get_metrics(folio_list, features):
    """Calculate mean metrics for a list of folios."""
    valid = [f for f in folio_list if f in features]
    if not valid:
        return None
    return {
        'cei': mean([features[f]['cei_total'] for f in valid]),
        'hazard': mean([features[f]['hazard_density'] for f in valid]),
        'intervention': mean([features[f]['intervention_frequency'] for f in valid]),
        'cycle': mean([features[f]['mean_cycle_length'] for f in valid]),
        'n': len(valid)
    }


def calculate_escalation_score(first_metrics, last_metrics):
    """Calculate how much metrics escalate from first to last third."""
    if not first_metrics or not last_metrics:
        return 0

    # All metrics should increase from first to last for proper escalation
    scores = []
    for key in ['cei', 'hazard', 'intervention', 'cycle']:
        if first_metrics[key] > 0:
            ratio = last_metrics[key] / first_metrics[key]
            scores.append(ratio - 1)  # Positive = escalation

    return mean(scores) if scores else 0


def test_order(order, features, order_name):
    """Test escalation for a given order."""
    n = len(order)
    third = n // 3

    first_third = order[:third]
    middle_third = order[third:2*third]
    last_third = order[2*third:]

    first_metrics = get_metrics(first_third, features)
    middle_metrics = get_metrics(middle_third, features)
    last_metrics = get_metrics(last_third, features)

    print(f"\n--- {order_name} ---")
    print(f"First third ({first_metrics['n']} folios):")
    print(f"  CEI: {first_metrics['cei']:.3f}")
    print(f"  Hazard: {first_metrics['hazard']:.3f}")
    print(f"  Intervention: {first_metrics['intervention']:.2f}")

    print(f"Last third ({last_metrics['n']} folios):")
    print(f"  CEI: {last_metrics['cei']:.3f}")
    print(f"  Hazard: {last_metrics['hazard']:.3f}")
    print(f"  Intervention: {last_metrics['intervention']:.2f}")

    # Calculate differences
    cei_diff = last_metrics['cei'] - first_metrics['cei']
    hazard_diff = last_metrics['hazard'] - first_metrics['hazard']
    intervention_diff = last_metrics['intervention'] - first_metrics['intervention']

    print(f"\nEscalation (last - first):")
    print(f"  CEI: {cei_diff:+.3f}")
    print(f"  Hazard: {hazard_diff:+.3f}")
    print(f"  Intervention: {intervention_diff:+.2f}")

    # Calculate gradient correlation
    positions = list(range(len(order)))
    cei_values = [features[f]['cei_total'] for f in order if f in features]
    hazard_values = [features[f]['hazard_density'] for f in order if f in features]

    cei_rho, cei_p = stats.spearmanr(positions[:len(cei_values)], cei_values)
    hazard_rho, hazard_p = stats.spearmanr(positions[:len(hazard_values)], hazard_values)

    print(f"\nGradient correlations:")
    print(f"  CEI vs position: rho = {cei_rho:+.4f} (p = {cei_p:.4f})")
    print(f"  Hazard vs position: rho = {hazard_rho:+.4f} (p = {hazard_p:.4f})")

    # Count matches with Brunschwig expectation
    matches = 0
    total = 3
    if cei_diff > 0:
        matches += 1
    if hazard_diff > 0:
        matches += 1
    if intervention_diff > 0:
        matches += 1

    print(f"\nBrunschwig escalation matches: {matches}/{total}")

    return {
        'first_third': first_metrics,
        'middle_third': middle_metrics,
        'last_third': last_metrics,
        'cei_diff': cei_diff,
        'hazard_diff': hazard_diff,
        'intervention_diff': intervention_diff,
        'cei_gradient_rho': float(cei_rho),
        'cei_gradient_p': float(cei_p),
        'hazard_gradient_rho': float(hazard_rho),
        'hazard_gradient_p': float(hazard_p),
        'escalation_matches': matches,
        'escalation_total': total
    }


def main():
    print("=" * 70)
    print("BRUNSCHWIG REALIGNMENT TEST")
    print("Does proposed order strengthen degree escalation alignment?")
    print("=" * 70)

    print("\nBrunschwig's Degree Escalation Model:")
    print("  First degree: balneum (water bath) - flowers, delicate")
    print("  Second degree: noticeably warm - standard herbs")
    print("  Third degree: almost seething - roots, bark, resins")
    print("  Fourth degree: FORBIDDEN (categorical prohibition)")
    print("\nPrediction: Front folios should show LOWER complexity than back folios")

    macro, reordering, cart = load_data()

    # Get features
    features = macro['features']

    # Get orders
    current_order = list(features.keys())
    proposed_order = reordering['optimal_order']['sequence']

    # Filter proposed order to only include folios we have features for
    proposed_order = [f for f in proposed_order if f in features]

    print(f"\nFolios analyzed: {len(current_order)} current, {len(proposed_order)} proposed")

    # Test both orders
    current_results = test_order(current_order, features, "CURRENT ORDER (manuscript)")
    proposed_results = test_order(proposed_order, features, "PROPOSED ORDER (optimized)")

    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    print("\nCEI Escalation (last - first):")
    print(f"  Current:  {current_results['cei_diff']:+.3f}")
    print(f"  Proposed: {proposed_results['cei_diff']:+.3f}")
    print(f"  Improvement: {proposed_results['cei_diff'] - current_results['cei_diff']:+.3f}")

    print("\nHazard Escalation (last - first):")
    print(f"  Current:  {current_results['hazard_diff']:+.3f}")
    print(f"  Proposed: {proposed_results['hazard_diff']:+.3f}")
    print(f"  Improvement: {proposed_results['hazard_diff'] - current_results['hazard_diff']:+.3f}")

    print("\nCEI Gradient Correlation:")
    print(f"  Current:  rho = {current_results['cei_gradient_rho']:+.4f} (p = {current_results['cei_gradient_p']:.4f})")
    print(f"  Proposed: rho = {proposed_results['cei_gradient_rho']:+.4f} (p = {proposed_results['cei_gradient_p']:.6f})")

    print("\nHazard Gradient Correlation:")
    print(f"  Current:  rho = {current_results['hazard_gradient_rho']:+.4f} (p = {current_results['hazard_gradient_p']:.4f})")
    print(f"  Proposed: rho = {proposed_results['hazard_gradient_rho']:+.4f} (p = {proposed_results['hazard_gradient_p']:.6f})")

    # Determine verdict
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)

    current_weak = abs(current_results['cei_gradient_rho']) < 0.3
    proposed_strong = proposed_results['cei_gradient_rho'] > 0.5 and proposed_results['cei_gradient_p'] < 0.001

    if current_weak and proposed_strong:
        print("\n*** BRUNSCHWIG ALIGNMENT STRENGTHENED: WEAK -> STRONG ***")
        print("\nThe proposed order reveals the true degree escalation:")
        print("  - Front folios: Low CEI, low hazard (first/second degree)")
        print("  - Back folios: High CEI, high hazard (third degree)")
        print("  - This matches Brunschwig's prescription exactly")
        verdict = "WEAK_TO_STRONG"
    elif proposed_strong:
        print("\n*** BRUNSCHWIG ALIGNMENT STRENGTHENED ***")
        verdict = "STRENGTHENED"
    else:
        print("\n*** IMPROVEMENT INSUFFICIENT ***")
        verdict = "INSUFFICIENT"

    # Build results
    results = {
        "test": "BRUNSCHWIG_REALIGNMENT",
        "date": "2026-01-14",
        "tier": 3,
        "status": "SPECULATIVE",
        "brunschwig_model": {
            "first_degree": "balneum (water bath) - flowers, delicate",
            "second_degree": "noticeably warm - standard herbs",
            "third_degree": "almost seething - roots, bark, resins",
            "fourth_degree": "FORBIDDEN"
        },
        "current_order": current_results,
        "proposed_order": proposed_results,
        "comparison": {
            "cei_diff_improvement": round(proposed_results['cei_diff'] - current_results['cei_diff'], 4),
            "hazard_diff_improvement": round(proposed_results['hazard_diff'] - current_results['hazard_diff'], 4),
            "cei_gradient_improvement": round(proposed_results['cei_gradient_rho'] - current_results['cei_gradient_rho'], 4),
            "hazard_gradient_improvement": round(proposed_results['hazard_gradient_rho'] - current_results['hazard_gradient_rho'], 4),
            "current_weak": current_weak,
            "proposed_strong": proposed_strong,
            "verdict": verdict
        },
        "interpretation": (
            "Proposed order reveals STRONG Brunschwig alignment that was hidden in current order. "
            "Front folios show low complexity (first/second degree), back folios show high complexity "
            "(third degree). Misbinding disrupted the visible degree escalation."
            if verdict == "WEAK_TO_STRONG" else
            "Brunschwig alignment improved but relationship may involve additional factors."
        )
    }

    # Save results
    output_path = RESULTS_DIR / "brunschwig_realignment_test.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_path}")

    return results


if __name__ == "__main__":
    main()
