"""
Phase 3: Bundle-Level Minimal Execution Test

Check if every activating bundle has at least one minimal B execution path,
ignoring folio partitioning entirely.
"""
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.constraint_bundle import build_bundle_registry, BundleType
from core.azc_projection import compute_reachable_classes


def compute_minimal_grammar_coverage(reachable_classes: set, ds) -> dict:
    """
    Check if reachable classes cover minimal grammar requirements.

    Minimal requirements (from BCSC):
    - At least one CORE_CONTROL class
    - At least one ENERGY_OPERATOR class
    - Kernel operators must be reachable
    """
    # Get class roles
    core_control = set()
    energy_ops = set()
    auxiliary = set()

    for class_id in reachable_classes:
        cls = ds.classes.get(class_id)
        if not cls:
            continue
        role = (cls.role or "").upper()

        if "CORE" in role or "CONTROL" in role:
            core_control.add(class_id)
        if "ENERGY" in role or "OPERATOR" in role:
            energy_ops.add(class_id)
        if "AUXILIARY" in role:
            auxiliary.add(class_id)

    # Check kernel presence
    kernel_present = ds.kernel_classes <= reachable_classes

    return {
        "total_reachable": len(reachable_classes),
        "core_control_count": len(core_control),
        "core_control_ids": sorted(core_control),
        "energy_ops_count": len(energy_ops),
        "energy_ops_ids": sorted(energy_ops),
        "auxiliary_count": len(auxiliary),
        "kernel_complete": kernel_present,
        "kernel_missing": sorted(ds.kernel_classes - reachable_classes),
        "minimal_viable": (
            len(core_control) > 0 and
            len(energy_ops) > 0 and
            kernel_present
        )
    }


def test_bundle_minimal_path(bundle, ds) -> dict:
    """Test if a bundle admits minimal grammar coverage."""

    if not bundle.compatible_folios:
        return {"status": "NO_COMPATIBLE_FOLIOS"}

    # Compute effective vocabulary across ALL compatible folios
    all_effective_middles = set()
    for folio in bundle.compatible_folios:
        folio_vocab = ds.azc_folio_middles.get(folio, set())
        # Zone-legal at zone C (most permissive)
        for m in folio_vocab:
            zones = ds.middle_zone_legality.get(m, {'C', 'P', 'R', 'S'})
            if 'C' in zones:
                all_effective_middles.add(m)

    # Compute reachable classes from union of all folio vocabularies
    reachable = compute_reachable_classes(all_effective_middles, ds)

    # Check minimal grammar coverage
    coverage = compute_minimal_grammar_coverage(reachable, ds)

    return {
        "bundle_id": bundle.bundle_id,
        "compatible_folios": len(bundle.compatible_folios),
        "effective_middles": len(all_effective_middles),
        "reachable_classes": len(reachable),
        "reachable_class_ids": sorted(reachable),
        "coverage": coverage,
        "has_minimal_path": coverage["minimal_viable"]
    }


def main():
    print("=" * 70)
    print("PHASE 3: BUNDLE-LEVEL MINIMAL EXECUTION TEST")
    print("=" * 70)

    ds = get_data_store()

    print(f"\nKernel classes ({len(ds.kernel_classes)}): {sorted(ds.kernel_classes)}")

    # Get all activating bundles
    from core.a_record_loader import load_a_records
    store = load_a_records()
    registry = build_bundle_registry(store.registry_entries)

    activating = [
        b for b in registry.bundles.values()
        if b.bundle_type == BundleType.ACTIVATING
    ]

    print(f"\nTesting {len(activating)} activating bundles for minimal paths...")

    # Test each bundle
    with_path = 0
    without_path = 0
    results = []

    for bundle in activating:
        result = test_bundle_minimal_path(bundle, ds)
        results.append(result)

        if result.get("has_minimal_path"):
            with_path += 1
        else:
            without_path += 1

    # Summary
    print("\n" + "=" * 70)
    print("MINIMAL PATH SUMMARY")
    print("=" * 70)

    print(f"\nBundles WITH minimal path: {with_path}/{len(activating)} ({100*with_path/len(activating):.1f}%)")
    print(f"Bundles WITHOUT minimal path: {without_path}/{len(activating)} ({100*without_path/len(activating):.1f}%)")

    if without_path > 0:
        print("\n" + "-" * 70)
        print("BUNDLES WITHOUT MINIMAL PATH (first 10):")
        print("-" * 70)

        no_path = [r for r in results if not r.get("has_minimal_path")]
        for r in no_path[:10]:
            print(f"\n  {r['bundle_id']}:")
            print(f"    Compatible folios: {r['compatible_folios']}")
            print(f"    Effective MIDDLEs: {r['effective_middles']}")
            print(f"    Reachable classes: {r['reachable_classes']}")
            cov = r.get("coverage", {})
            print(f"    Core control: {cov.get('core_control_count', 0)} classes")
            print(f"    Energy ops: {cov.get('energy_ops_count', 0)} classes")
            print(f"    Kernel complete: {cov.get('kernel_complete')}")
            if cov.get('kernel_missing'):
                print(f"    Kernel missing: {cov.get('kernel_missing')}")

    # Analyze what's missing across all failing bundles
    if without_path > 0:
        print("\n" + "-" * 70)
        print("ANALYSIS: WHAT'S MISSING?")
        print("-" * 70)

        no_path_results = [r for r in results if not r.get("has_minimal_path")]

        # Check if kernel is the problem
        kernel_incomplete = sum(
            1 for r in no_path_results
            if not r.get("coverage", {}).get("kernel_complete", False)
        )
        print(f"\n  Bundles with incomplete kernel: {kernel_incomplete}/{len(no_path_results)}")

        # Check core control
        no_core = sum(
            1 for r in no_path_results
            if r.get("coverage", {}).get("core_control_count", 0) == 0
        )
        print(f"  Bundles with no CORE_CONTROL: {no_core}/{len(no_path_results)}")

        # Check energy ops
        no_energy = sum(
            1 for r in no_path_results
            if r.get("coverage", {}).get("energy_ops_count", 0) == 0
        )
        print(f"  Bundles with no ENERGY_OPERATOR: {no_energy}/{len(no_path_results)}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if without_path == 0:
        print("\nALL activating bundles have minimal paths!")
        print("-> B folios may be over-specified (folio footprints too strict)")
        print("-> The problem is in B folio requirements, not grammar coverage")
    else:
        pct_failing = 100 * without_path / len(activating)
        print(f"\n{without_path} bundles ({pct_failing:.1f}%) lack minimal paths")

        if kernel_incomplete > len(no_path_results) * 0.5:
            print("-> KERNEL IS THE ISSUE: AZC pruning is removing kernel classes")
            print("-> This should NOT happen if kernel is truly kernel")
        else:
            print("-> AZC pruning eliminated mandatory infrastructure")
            print("-> Need to identify and protect infrastructure classes")

    # Save results
    output_path = PROJECT_ROOT / "results" / "phase3_minimal_path.json"
    output_path.write_text(json.dumps({
        "total_activating": len(activating),
        "with_minimal_path": with_path,
        "without_minimal_path": without_path,
        "kernel_classes": sorted(ds.kernel_classes),
        "sample_results": results[:20],
        "failing_bundles": [r for r in results if not r.get("has_minimal_path")][:50]
    }, indent=2, default=str))
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
