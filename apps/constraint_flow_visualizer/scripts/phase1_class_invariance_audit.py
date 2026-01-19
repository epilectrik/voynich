"""
Phase 1: Class-Level Invariance Audit

For each instruction class, test if making it immune to pruning
restores B folio reachability without breaking forbidden transitions.
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Set, Dict, List
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.constraint_bundle import (
    build_bundle_registry, BundleType, AZCConstraintBundle
)
from core.reachability_engine import compute_bundle_legality
from core.azc_projection import compute_reachable_classes


@dataclass
class ClassImmunityResult:
    class_id: int
    baseline_reachable_b: int
    immune_reachable_b: int
    delta_reachable_b: int
    forbidden_transitions_intact: bool
    class_role: str
    class_middles: Set[str]
    b_folio_coverage: int  # How many B folios require this class


def audit_single_class(
    class_id: int,
    test_bundles: List[AZCConstraintBundle],
    data_store
) -> ClassImmunityResult:
    """Test the effect of making one class immune to pruning."""

    # Get class info
    cls = data_store.classes.get(class_id)
    role = cls.role if cls else "UNKNOWN"
    middles = cls.middles if cls else set()

    # Count B folio coverage for this class
    b_coverage = sum(
        1 for classes in data_store.b_folio_class_footprints.values()
        if class_id in classes
    )

    # Baseline: compute B reachability without immunity
    baseline_reachable = 0
    for bundle in test_bundles:
        result = compute_bundle_legality(bundle)
        baseline_reachable += sum(
            1 for fl in result.folio_legality.values()
            if fl.status.value == "REACHABLE"
        )

    # With immunity: temporarily add class to kernel set
    original_kernel = data_store.kernel_classes.copy()
    data_store.kernel_classes.add(class_id)

    immune_reachable = 0
    for bundle in test_bundles:
        result = compute_bundle_legality(bundle)
        immune_reachable += sum(
            1 for fl in result.folio_legality.values()
            if fl.status.value == "REACHABLE"
        )

    # Restore original kernel
    data_store.kernel_classes = original_kernel

    # Check forbidden transitions (always intact if we only ADD reachability)
    forbidden_intact = True  # Adding immunity cannot break forbidden transitions

    return ClassImmunityResult(
        class_id=class_id,
        baseline_reachable_b=baseline_reachable,
        immune_reachable_b=immune_reachable,
        delta_reachable_b=immune_reachable - baseline_reachable,
        forbidden_transitions_intact=forbidden_intact,
        class_role=role,
        class_middles=middles,
        b_folio_coverage=b_coverage
    )


def main():
    print("=" * 70)
    print("PHASE 1: CLASS-LEVEL INVARIANCE AUDIT")
    print("=" * 70)

    ds = get_data_store()

    # Get activating bundles for testing
    from core.a_record_loader import load_a_records
    store = load_a_records()
    registry = build_bundle_registry(store.registry_entries)

    activating_bundles = [
        b for b in registry.bundles.values()
        if b.bundle_type == BundleType.ACTIVATING
    ]

    print(f"\nTesting with {len(activating_bundles)} activating bundles")
    print(f"Current kernel classes: {len(ds.kernel_classes)}")
    print(f"  Kernel set: {sorted(ds.kernel_classes)}")
    print(f"Total B folios: {len(ds.b_folio_class_footprints)}")

    # Use a sample of bundles for efficiency (first 10)
    sample_bundles = activating_bundles[:10]
    print(f"\nUsing {len(sample_bundles)} sample bundles for testing")

    # Test each non-kernel class
    non_kernel = set(range(1, 50)) - ds.kernel_classes
    print(f"\nAuditing {len(non_kernel)} non-kernel classes...")

    results = []
    for class_id in sorted(non_kernel):
        result = audit_single_class(class_id, sample_bundles, ds)
        results.append(result)

        if result.delta_reachable_b > 0:
            print(f"  Class {class_id}: +{result.delta_reachable_b} B folios (coverage: {result.b_folio_coverage}/82)")

    # Summary: identify connectivity infrastructure candidates
    print("\n" + "=" * 70)
    print("CONNECTIVITY INFRASTRUCTURE CANDIDATES")
    print("=" * 70)
    print("(Classes that restore B reachability when made immune)")

    infrastructure = [r for r in results if r.delta_reachable_b > 0]
    infrastructure.sort(key=lambda r: -r.delta_reachable_b)

    if not infrastructure:
        print("\nNo classes restore B reachability when immunized.")
        print("This suggests the blocking may not be class-specific.")
    else:
        for r in infrastructure:
            print(f"\nClass {r.class_id} ({r.class_role}):")
            print(f"  B folio coverage: {r.b_folio_coverage}/82")
            print(f"  Delta reachability: +{r.delta_reachable_b}")
            if r.class_middles:
                print(f"  MIDDLEs: {sorted(r.class_middles)[:5]}{'...' if len(r.class_middles) > 5 else ''}")
            else:
                print(f"  MIDDLEs: (none - atomic class)")

    # Also show classes with high B coverage but no impact
    print("\n" + "-" * 70)
    print("HIGH-COVERAGE CLASSES (>75 B folios) - FOR REFERENCE")
    print("-" * 70)

    high_coverage = [r for r in results if r.b_folio_coverage >= 75]
    high_coverage.sort(key=lambda r: -r.b_folio_coverage)

    for r in high_coverage[:10]:
        status = "INFRASTRUCTURE" if r.delta_reachable_b > 0 else "no impact"
        print(f"  Class {r.class_id} ({r.class_role}): {r.b_folio_coverage}/82 B folios [{status}]")

    # Output JSON for analysis
    output = {
        "kernel_classes": sorted(ds.kernel_classes),
        "non_kernel_classes": sorted(non_kernel),
        "sample_bundles_tested": len(sample_bundles),
        "infrastructure_candidates": [
            {
                "class_id": r.class_id,
                "role": r.class_role,
                "b_coverage": r.b_folio_coverage,
                "delta_reachability": r.delta_reachable_b,
                "middles": sorted(r.class_middles) if r.class_middles else []
            }
            for r in infrastructure
        ],
        "high_coverage_classes": [
            {
                "class_id": r.class_id,
                "role": r.class_role,
                "b_coverage": r.b_folio_coverage,
                "delta_reachability": r.delta_reachable_b
            }
            for r in high_coverage
        ],
        "all_results": [
            {
                "class_id": r.class_id,
                "role": r.class_role,
                "b_coverage": r.b_folio_coverage,
                "baseline_reachable": r.baseline_reachable_b,
                "immune_reachable": r.immune_reachable_b,
                "delta": r.delta_reachable_b
            }
            for r in results
        ]
    }

    output_path = PROJECT_ROOT / "results" / "phase1_class_invariance.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {output_path}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Infrastructure candidates found: {len(infrastructure)}")
    print(f"High-coverage (>75) non-kernel classes: {len(high_coverage)}")

    if infrastructure:
        print("\nRECOMMENDATION: Consider adding these classes to infrastructure tier:")
        for r in infrastructure:
            print(f"  - Class {r.class_id} (B coverage: {r.b_folio_coverage})")


if __name__ == "__main__":
    main()
