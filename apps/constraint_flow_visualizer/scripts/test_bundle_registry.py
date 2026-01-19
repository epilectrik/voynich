"""
Test the new bundle registry system.

Verifies that the expert's recommended changes are working:
1. Bundle registry correctly collapses A records into bundles
2. LegalityProfile correctly shows zone survival
3. compute_bundle_legality correctly classifies B folios
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.a_record_loader import load_a_records
from core.constraint_bundle import (
    build_bundle_registry,
    compute_legality_profile,
    BundleType
)
from core.reachability_engine import compute_bundle_legality


def main():
    print("=" * 70)
    print("BUNDLE REGISTRY TEST")
    print("=" * 70)

    # Load A records
    print("\nLoading A records...")
    store = load_a_records()
    print(f"  Loaded {len(store.registry_entries)} A records")

    # Build bundle registry
    print("\nBuilding bundle registry...")
    registry = build_bundle_registry(store.registry_entries)
    print(f"  {registry.summary()}")

    # Statistics
    print("\n" + "-" * 70)
    print("BUNDLE STATISTICS")
    print("-" * 70)

    # Count by type
    type_counts = {bt: 0 for bt in BundleType}
    for bundle in registry.bundles.values():
        type_counts[bundle.bundle_type] += 1

    print("\nBundle type distribution:")
    for bt, count in type_counts.items():
        pct = 100 * count / registry.unique_bundle_count
        print(f"  {bt.value:12}: {count:4} bundles ({pct:.1f}%)")

    # Top bundles by record count
    print("\n" + "-" * 70)
    print("TOP BUNDLES BY RECORD COUNT")
    print("-" * 70)

    sorted_bundles = sorted(
        registry.bundle_to_records.items(),
        key=lambda x: -len(x[1])
    )

    for bundle_id, records in sorted_bundles[:10]:
        bundle = registry.bundles[bundle_id]
        profile = compute_legality_profile(bundle)
        print(f"\n{bundle_id}: {len(records)} records")
        print(f"  Type: {bundle.bundle_type.value}")
        print(f"  Compatible folios: {len(bundle.compatible_folios)}")
        print(f"  Execution mode: {profile.execution_mode}")
        print(f"  Zone survival: C={profile.survives_C}, P={profile.survives_P}, R={profile.survives_R}, S={profile.survives_S}")

    # Test B folio legality computation
    print("\n" + "-" * 70)
    print("B FOLIO LEGALITY TEST")
    print("-" * 70)

    # Test with a few different bundle types
    test_bundles = []

    # Get one of each type
    for bundle in registry.bundles.values():
        if bundle.bundle_type == BundleType.NEUTRAL and not any(
            b.bundle_type == BundleType.NEUTRAL for b in test_bundles
        ):
            test_bundles.append(bundle)
        elif bundle.bundle_type == BundleType.ACTIVATING and not any(
            b.bundle_type == BundleType.ACTIVATING for b in test_bundles
        ):
            test_bundles.append(bundle)
        elif bundle.bundle_type == BundleType.BLOCKED and not any(
            b.bundle_type == BundleType.BLOCKED for b in test_bundles
        ):
            test_bundles.append(bundle)

        if len(test_bundles) >= 3:
            break

    for bundle in test_bundles:
        print(f"\nBundle: {bundle.bundle_id} ({bundle.bundle_type.value})")

        result = compute_bundle_legality(bundle)
        print(f"  {result.summary()}")

        # Show sample B folios
        print("  Sample B folios:")
        for folio_id, fl in list(result.folio_legality.items())[:3]:
            print(f"    {fl.summary()}")

    # Verify C481 at bundle level
    print("\n" + "-" * 70)
    print("C481 VERIFICATION (Bundle-Level)")
    print("-" * 70)

    # Count unique folio signatures among activating bundles
    folio_sigs = {}
    for bundle in registry.bundles.values():
        if bundle.bundle_type == BundleType.ACTIVATING:
            sig = bundle.compatible_folios
            if sig not in folio_sigs:
                folio_sigs[sig] = []
            folio_sigs[sig].append(bundle.bundle_id)

    activating_count = sum(1 for b in registry.bundles.values()
                           if b.bundle_type == BundleType.ACTIVATING)

    print(f"\nActivating bundles: {activating_count}")
    print(f"Unique folio signatures: {len(folio_sigs)}")

    # Check for signature collisions
    collisions = {s: b for s, b in folio_sigs.items() if len(b) > 1}
    if collisions:
        print(f"Signature collisions: {len(collisions)}")
        print("\nCollision examples:")
        for sig, bundles in list(collisions.items())[:3]:
            print(f"  {len(sig)} folios -> {len(bundles)} bundles: {bundles[:3]}")
    else:
        print("No signature collisions - perfect 1:1 mapping!")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
