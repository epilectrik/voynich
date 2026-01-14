"""
Folio Reordering Analysis
Phase: YALE_ALIGNMENT

Using our structural constraints to propose an original folio order:
- C161: Folio Ordering = Risk Gradient (rho=0.39)
- C325: Completion Gradient (rho=+0.24)
- C155: Piecewise-Sequential Geometry (PC1 rho=-0.624)

Method: Find ordering that maximizes structural gradients.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import random
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scipy.stats import spearmanr
import numpy as np


def load_folio_features():
    """Load structural features for all B folios."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    cart_path = results_dir / "b_design_space_cartography.json"

    with open(cart_path) as f:
        cart_data = json.load(f)

    folios = {}
    for folio, data in cart_data.get("folio_positions", {}).items():
        folios[folio] = {
            "hazard_density": data.get("hazard_density", 0),
            "escape_density": data.get("escape_density", 0),
            "cei_total": data.get("cei_total", 0),
            "link_density": data.get("link_density", 0),
            "execution_tension": data.get("execution_tension", 0),
            "regime": data.get("regime", "UNKNOWN")
        }

    return folios


def extract_folio_number(folio_name):
    """Extract numeric portion for sorting."""
    import re
    match = re.match(r'f(\d+)', folio_name.lower())
    if match:
        num = int(match.group(1))
        # Handle recto/verso
        if 'v' in folio_name.lower():
            return num + 0.5
        return num
    return 999


def calculate_gradient_score(order, features, metric='hazard_density'):
    """Calculate Spearman correlation for a given ordering."""
    values = [features[f][metric] for f in order]
    positions = list(range(len(order)))
    rho, p = spearmanr(positions, values)
    return rho if not np.isnan(rho) else 0


def calculate_combined_score(order, features):
    """Combined score: risk should increase, completion should increase."""
    # Risk gradient (hazard_density should increase)
    risk_rho = calculate_gradient_score(order, features, 'hazard_density')

    # Completion proxy: execution_tension (higher = more complete/resolved)
    completion_rho = calculate_gradient_score(order, features, 'execution_tension')

    # CEI gradient
    cei_rho = calculate_gradient_score(order, features, 'cei_total')

    # Combined: we want positive correlations (increasing with order)
    return risk_rho + completion_rho + cei_rho


def greedy_ordering(folios, features, metric='hazard_density', ascending=True):
    """Greedy algorithm: sort by metric."""
    sorted_folios = sorted(
        folios,
        key=lambda f: features[f][metric],
        reverse=not ascending
    )
    return sorted_folios


def simulated_annealing(folios, features, max_iter=50000, initial_temp=1.0, cooling_rate=0.9995):
    """Simulated annealing to find optimal ordering."""
    current_order = list(folios)
    random.shuffle(current_order)
    current_score = calculate_combined_score(current_order, features)

    best_order = current_order[:]
    best_score = current_score

    temp = initial_temp

    for i in range(max_iter):
        # Random swap
        new_order = current_order[:]
        i1, i2 = random.sample(range(len(new_order)), 2)
        new_order[i1], new_order[i2] = new_order[i2], new_order[i1]

        new_score = calculate_combined_score(new_order, features)

        # Accept if better, or with probability based on temperature
        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / temp):
            current_order = new_order
            current_score = new_score

            if current_score > best_score:
                best_order = current_order[:]
                best_score = current_score

        temp *= cooling_rate

        if i % 10000 == 0:
            print(f"  Iteration {i}: best_score={best_score:.4f}, temp={temp:.6f}")

    return best_order, best_score


def analyze_regime_blocks(order, features):
    """Analyze how regimes are distributed in the ordering."""
    regime_positions = defaultdict(list)
    for i, folio in enumerate(order):
        regime = features[folio]['regime']
        regime_positions[regime].append(i)

    blocks = {}
    for regime, positions in regime_positions.items():
        if positions:
            blocks[regime] = {
                'count': len(positions),
                'start': min(positions),
                'end': max(positions),
                'mean_position': sum(positions) / len(positions),
                'contiguous': max(positions) - min(positions) + 1 == len(positions)
            }

    return blocks


def main():
    print("=" * 60)
    print("FOLIO REORDERING ANALYSIS")
    print("Recovering Original Order from Structural Gradients")
    print("=" * 60)

    # Load data
    features = load_folio_features()
    folio_list = list(features.keys())

    print(f"\nLoaded {len(folio_list)} folios with structural features")

    # Current order (by folio number)
    current_order = sorted(folio_list, key=extract_folio_number)

    print("\n" + "-" * 60)
    print("CURRENT ORDER ANALYSIS")
    print("-" * 60)

    current_risk_rho = calculate_gradient_score(current_order, features, 'hazard_density')
    current_tension_rho = calculate_gradient_score(current_order, features, 'execution_tension')
    current_cei_rho = calculate_gradient_score(current_order, features, 'cei_total')
    current_combined = calculate_combined_score(current_order, features)

    print(f"\nCurrent order gradients:")
    print(f"  Risk (hazard_density):     rho = {current_risk_rho:.4f}")
    print(f"  Tension (execution):       rho = {current_tension_rho:.4f}")
    print(f"  CEI:                       rho = {current_cei_rho:.4f}")
    print(f"  Combined score:            {current_combined:.4f}")

    # Greedy orderings
    print("\n" + "-" * 60)
    print("GREEDY ORDERINGS")
    print("-" * 60)

    # Sort by risk ascending (low risk first)
    risk_order = greedy_ordering(folio_list, features, 'hazard_density', ascending=True)
    risk_combined = calculate_combined_score(risk_order, features)
    print(f"\nBy hazard_density (ascending): combined = {risk_combined:.4f}")

    # Sort by tension ascending
    tension_order = greedy_ordering(folio_list, features, 'execution_tension', ascending=True)
    tension_combined = calculate_combined_score(tension_order, features)
    print(f"By execution_tension (ascending): combined = {tension_combined:.4f}")

    # Sort by CEI ascending
    cei_order = greedy_ordering(folio_list, features, 'cei_total', ascending=True)
    cei_combined = calculate_combined_score(cei_order, features)
    print(f"By CEI (ascending): combined = {cei_combined:.4f}")

    # Simulated annealing
    print("\n" + "-" * 60)
    print("SIMULATED ANNEALING OPTIMIZATION")
    print("-" * 60)

    print("\nRunning simulated annealing (50k iterations)...")
    random.seed(42)
    optimal_order, optimal_score = simulated_annealing(folio_list, features)

    print(f"\nOptimal combined score: {optimal_score:.4f}")
    print(f"Improvement over current: {optimal_score - current_combined:.4f}")

    # Analyze optimal order
    opt_risk_rho = calculate_gradient_score(optimal_order, features, 'hazard_density')
    opt_tension_rho = calculate_gradient_score(optimal_order, features, 'execution_tension')
    opt_cei_rho = calculate_gradient_score(optimal_order, features, 'cei_total')

    print(f"\nOptimal order gradients:")
    print(f"  Risk (hazard_density):     rho = {opt_risk_rho:.4f} (was {current_risk_rho:.4f})")
    print(f"  Tension (execution):       rho = {opt_tension_rho:.4f} (was {current_tension_rho:.4f})")
    print(f"  CEI:                       rho = {opt_cei_rho:.4f} (was {current_cei_rho:.4f})")

    # Regime distribution in optimal order
    print("\n" + "-" * 60)
    print("REGIME DISTRIBUTION IN OPTIMAL ORDER")
    print("-" * 60)

    regime_blocks = analyze_regime_blocks(optimal_order, features)
    for regime in sorted(regime_blocks.keys()):
        block = regime_blocks[regime]
        contiguous = "CONTIGUOUS" if block['contiguous'] else "scattered"
        print(f"\n{regime}:")
        print(f"  Count: {block['count']}")
        print(f"  Positions: {block['start']} - {block['end']} ({contiguous})")
        print(f"  Mean position: {block['mean_position']:.1f}")

    # Compare orderings
    print("\n" + "-" * 60)
    print("ORDER COMPARISON (first 20 folios)")
    print("-" * 60)

    print("\nCurrent order:  ", " ".join(current_order[:20]))
    print("Optimal order:  ", " ".join(optimal_order[:20]))

    # Calculate displacement
    current_positions = {f: i for i, f in enumerate(current_order)}
    displacements = []
    for i, folio in enumerate(optimal_order):
        displacement = abs(i - current_positions[folio])
        displacements.append(displacement)

    avg_displacement = sum(displacements) / len(displacements)
    max_displacement = max(displacements)

    print(f"\nAverage displacement: {avg_displacement:.1f} positions")
    print(f"Maximum displacement: {max_displacement} positions")

    # Most displaced folios
    displacement_pairs = [(optimal_order[i], displacements[i]) for i in range(len(optimal_order))]
    displacement_pairs.sort(key=lambda x: x[1], reverse=True)

    print("\nMost displaced folios:")
    for folio, disp in displacement_pairs[:10]:
        curr_pos = current_positions[folio]
        opt_pos = optimal_order.index(folio)
        print(f"  {folio}: {curr_pos} -> {opt_pos} (displaced {disp})")

    # Build results
    results = {
        "test": "FOLIO_REORDERING",
        "date": "2026-01-14",
        "n_folios": len(folio_list),
        "current_order": {
            "risk_rho": round(current_risk_rho, 4),
            "tension_rho": round(current_tension_rho, 4),
            "cei_rho": round(current_cei_rho, 4),
            "combined": round(current_combined, 4)
        },
        "optimal_order": {
            "risk_rho": round(opt_risk_rho, 4),
            "tension_rho": round(opt_tension_rho, 4),
            "cei_rho": round(opt_cei_rho, 4),
            "combined": round(optimal_score, 4),
            "sequence": optimal_order
        },
        "improvement": round(optimal_score - current_combined, 4),
        "avg_displacement": round(avg_displacement, 2),
        "max_displacement": max_displacement,
        "most_displaced": [
            {"folio": f, "displacement": d} for f, d in displacement_pairs[:10]
        ],
        "regime_blocks": {
            regime: {
                "mean_position": round(block['mean_position'], 1),
                "contiguous": block['contiguous']
            }
            for regime, block in regime_blocks.items()
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "folio_reordering.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if optimal_score > current_combined:
        print(f"\nOptimal order improves gradient scores by {optimal_score - current_combined:.4f}")
        print("This suggests the current binding order is NOT optimal for the structural gradients.")
        print("\nInterpretation: The manuscript's current order has been disrupted.")
    else:
        print("\nCurrent order is already near-optimal for structural gradients.")
        print("This would suggest the current binding is close to original.")

    return results


if __name__ == "__main__":
    main()
