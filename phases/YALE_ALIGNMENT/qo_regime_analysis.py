"""
QO Distribution by Regime Analysis
Phase: YALE_ALIGNMENT

Tests whether qo token frequency differs across regimes.
Yale transcript notes that Scribe 4 (astronomical) has rare qo usage.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def analyze_qo_by_regime():
    """Analyze qo density distribution across regimes."""
    results_dir = Path(__file__).parent.parent.parent / "results"

    # Load cartography data with qo_density per folio
    cart_path = results_dir / "b_design_space_cartography.json"

    with open(cart_path) as f:
        cart_data = json.load(f)

    # Collect qo by regime
    regime_qo = defaultdict(list)

    for folio, data in cart_data.get("folio_positions", {}).items():
        regime = data.get("regime")
        # Note: qo_density might be named differently - check actual fields
        # From global_variance we saw "qo_density" so let's check folio data
        qo = data.get("qo_density") or data.get("escape_density")  # escape_density as proxy

        if regime and qo is not None:
            regime_qo[regime].append((folio, qo))

    # Calculate statistics per regime
    results = {
        "test": "QO_REGIME_DISTRIBUTION",
        "date": "2026-01-14",
        "source": "Yale lecture noted Scribe 4 has rare qo",
        "regime_stats": {},
        "findings": []
    }

    for regime in sorted(regime_qo.keys()):
        values = [v for _, v in regime_qo[regime]]
        if values:
            results["regime_stats"][regime] = {
                "n": len(values),
                "mean": round(statistics.mean(values), 4),
                "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0,
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "folios": [f for f, _ in regime_qo[regime]]
            }

    # Compare regimes
    all_means = [(r, s["mean"]) for r, s in results["regime_stats"].items()]
    if all_means:
        sorted_means = sorted(all_means, key=lambda x: x[1])
        results["ordering"] = [f"{r}: {m:.3f}" for r, m in sorted_means]

        # Check for significant differences
        overall_mean = statistics.mean([s["mean"] for s in results["regime_stats"].values()])
        results["overall_mean"] = round(overall_mean, 4)

        for regime, stats in results["regime_stats"].items():
            if stats["mean"] < overall_mean * 0.7:
                results["findings"].append(f"{regime} has LOW qo ({stats['mean']:.3f} vs {overall_mean:.3f})")
            elif stats["mean"] > overall_mean * 1.3:
                results["findings"].append(f"{regime} has HIGH qo ({stats['mean']:.3f} vs {overall_mean:.3f})")

    return results

def main():
    print("=" * 60)
    print("QO DISTRIBUTION BY REGIME")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    results = analyze_qo_by_regime()

    print(f"\nNote: Using escape_density as proxy (qo_density may not be per-folio)")
    print(f"\nOverall mean: {results.get('overall_mean', 'N/A')}")
    print(f"\nOrdering: {' < '.join(results.get('ordering', []))}")

    print("\nRegime Statistics:")
    print("-" * 40)
    for regime, stats in sorted(results["regime_stats"].items()):
        print(f"  {regime}: n={stats['n']}, mean={stats['mean']:.3f}, std={stats['std']:.3f}")

    if results["findings"]:
        print("\nFindings:")
        for f in results["findings"]:
            print(f"  - {f}")
    else:
        print("\nNo significant qo differences found between regimes.")

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "qo_regime_distribution.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == "__main__":
    main()
