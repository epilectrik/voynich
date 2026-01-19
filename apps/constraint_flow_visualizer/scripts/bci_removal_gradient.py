"""
BCI Test 5: Removal Gradient (Perturbation Sensitivity)

Check if partial suppression has linear or nonlinear effects.
"""
import sys
import json
from pathlib import Path
import random

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.constraint_bundle import build_bundle_registry, BundleType
from core.reachability_engine import compute_bundle_legality

INFRASTRUCTURE_CLASSES = {44, 46}  # Focus on primary infrastructure

def main():
    print("=" * 70)
    print("BCI TEST 5: REMOVAL GRADIENT (PERTURBATION SENSITIVITY)")
    print("=" * 70)

    ds = get_data_store()

    # Get activating bundles
    from core.a_record_loader import load_a_records
    store = load_a_records()
    registry = build_bundle_registry(store.registry_entries)

    activating = [b for b in registry.bundles.values() if b.bundle_type == BundleType.ACTIVATING]
    sample_bundles = activating[:20]  # Sample for efficiency

    print(f"\nTesting with {len(sample_bundles)} sample bundles")
    print(f"Infrastructure classes: {sorted(INFRASTRUCTURE_CLASSES)}")

    # Baseline: full infrastructure available
    original_kernel = ds.kernel_classes.copy()

    # Test different suppression levels
    suppression_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
    results = []

    print("\n" + "-" * 70)
    print("SUPPRESSION GRADIENT TEST")
    print("-" * 70)

    # Set random seed for reproducibility
    random.seed(42)

    for level in suppression_levels:
        # Reset kernel
        ds.kernel_classes = original_kernel.copy()

        # Add infrastructure classes based on suppression level
        # level=0 means full suppression (no immunity)
        # level=1 means no suppression (full immunity)
        if level > 0:
            # Probabilistically add infrastructure to kernel
            for cls in INFRASTRUCTURE_CLASSES:
                if random.random() < level:
                    ds.kernel_classes.add(cls)

        # Compute reachability
        total_reachable = 0
        for bundle in sample_bundles:
            result = compute_bundle_legality(bundle)
            total_reachable += sum(
                1 for fl in result.folio_legality.values()
                if fl.status.value == "REACHABLE"
            )

        avg_reachable = total_reachable / len(sample_bundles)
        results.append({
            "suppression": 1 - level,  # Convert to suppression %
            "immunity": level,
            "avg_reachable_b": avg_reachable
        })

        print(f"\n  Immunity {level:.0%} (suppression {1-level:.0%}):")
        print(f"    Avg reachable B folios: {avg_reachable:.1f}")

    # Restore kernel
    ds.kernel_classes = original_kernel

    # Analyze linearity
    print("\n" + "-" * 70)
    print("LINEARITY ANALYSIS")
    print("-" * 70)

    # Compare actual vs linear expectation
    baseline = results[-1]["avg_reachable_b"]  # 100% immunity
    suppressed = results[0]["avg_reachable_b"]  # 0% immunity

    print(f"\nBaseline (full immunity): {baseline:.1f} B folios")
    print(f"Fully suppressed: {suppressed:.1f} B folios")

    for r in results[1:-1]:
        expected_linear = suppressed + r["immunity"] * (baseline - suppressed)
        actual = r["avg_reachable_b"]
        deviation = (actual - expected_linear) / expected_linear if expected_linear > 0 else 0

        print(f"\n  At {r['immunity']:.0%} immunity:")
        print(f"    Expected (linear): {expected_linear:.1f}")
        print(f"    Actual: {actual:.1f}")
        print(f"    Deviation: {deviation:+.1%}")

    # Interpretation
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)

    # Check for nonlinearity at 50%
    mid = results[2]  # 50% immunity
    expected_mid = suppressed + 0.5 * (baseline - suppressed)
    actual_mid = mid["avg_reachable_b"]

    if actual_mid < expected_mid * 0.8:
        print("\nNONLINEAR: Disproportionate impact at partial suppression")
        print("-> Small infrastructure loss causes outsized reachability loss")
        print("-> Threshold effect detected")
    elif actual_mid > expected_mid * 1.2:
        print("\nNONLINEAR: Resilient at partial suppression")
        print("-> Some redundancy in infrastructure")
    else:
        print("\nLINEAR: Proportional degradation")
        print("-> Infrastructure impact scales linearly with availability")

    # Save results
    output_path = PROJECT_ROOT / "results" / "bci_removal_gradient.json"
    output_path.write_text(json.dumps({
        "infrastructure_classes": sorted(INFRASTRUCTURE_CLASSES),
        "sample_size": len(sample_bundles),
        "results": results
    }, indent=2))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
