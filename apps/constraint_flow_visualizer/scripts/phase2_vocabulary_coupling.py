"""
Phase 2: AZC Vocabulary vs Class Membership Decoupling Test

Check if we're over-coupling vocabulary to class membership.
"""
import sys
from pathlib import Path
from collections import defaultdict
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.constraint_bundle import (
    build_bundle_registry, BundleType, compute_compatible_folios
)
from core.azc_projection import compute_reachable_classes, ALL_ZONES


def classify_middle(middle: str, ds) -> str:
    """Classify a MIDDLE by its vocabulary spread."""
    spread = ds.middle_folio_spread.get(middle, 0)
    if spread == 0:
        return "A_EXCLUSIVE"  # Not in any AZC folio
    elif spread <= 3:
        return "RESTRICTED"   # 1-3 folios
    else:
        return "UNIVERSAL"    # 4+ folios


def analyze_bundle_vocabulary_coupling(bundle, ds):
    """Analyze vocabulary coupling for a single bundle."""

    compatible_folios = list(bundle.compatible_folios)
    if not compatible_folios:
        return None

    # Pick first compatible folio for analysis
    folio = compatible_folios[0]
    folio_vocab = ds.azc_folio_middles.get(folio, set())

    # Get zone-legal MIDDLEs for zone C
    zone_legal = set()
    for m, zones in ds.middle_zone_legality.items():
        if 'C' in zones:
            zone_legal.add(m)

    # Effective vocabulary
    effective_vocab = zone_legal & folio_vocab

    # Compute reachable classes
    reachable = compute_reachable_classes(effective_vocab, ds)

    # Find missing classes (required by most B folios but not reachable)
    all_required = set()
    for classes in ds.b_folio_class_footprints.values():
        all_required |= classes

    missing = all_required - reachable - ds.kernel_classes

    # For each missing class, analyze its MIDDLE composition
    missing_analysis = {}
    for class_id in sorted(missing):
        cls = ds.classes.get(class_id)
        if not cls:
            continue

        # Classify each MIDDLE
        middle_types = defaultdict(list)
        for m in cls.middles:
            mtype = classify_middle(m, ds)
            middle_types[mtype].append(m)

        # Count B folio coverage
        b_coverage = sum(
            1 for classes in ds.b_folio_class_footprints.values()
            if class_id in classes
        )

        missing_analysis[class_id] = {
            "role": cls.role,
            "b_coverage": b_coverage,
            "total_middles": len(cls.middles),
            "universal": middle_types.get("UNIVERSAL", []),
            "restricted": middle_types.get("RESTRICTED", []),
            "a_exclusive": middle_types.get("A_EXCLUSIVE", []),
            "in_folio_vocab": list(cls.middles & folio_vocab)
        }

    return {
        "bundle_id": bundle.bundle_id,
        "compatible_folio": folio,
        "folio_vocab_size": len(folio_vocab),
        "zone_legal_size": len(zone_legal),
        "effective_vocab_size": len(effective_vocab),
        "reachable_classes": len(reachable),
        "missing_analysis": missing_analysis
    }


def main():
    print("=" * 70)
    print("PHASE 2: AZC VOCABULARY vs CLASS MEMBERSHIP DECOUPLING")
    print("=" * 70)

    ds = get_data_store()

    # Get activating bundles
    from core.a_record_loader import load_a_records
    store = load_a_records()
    registry = build_bundle_registry(store.registry_entries)

    activating = [
        b for b in registry.bundles.values()
        if b.bundle_type == BundleType.ACTIVATING
    ]

    print(f"\nAnalyzing {len(activating)} activating bundles...")

    # Analyze each bundle (sample first 20)
    results = []
    for bundle in activating[:20]:
        analysis = analyze_bundle_vocabulary_coupling(bundle, ds)
        if analysis:
            results.append(analysis)

    # Aggregate missing class analysis
    print("\n" + "=" * 70)
    print("VOCABULARY COUPLING ANALYSIS")
    print("=" * 70)

    # Find classes that are consistently missing
    missing_counts = defaultdict(int)
    missing_info = {}

    for result in results:
        for class_id, info in result["missing_analysis"].items():
            missing_counts[class_id] += 1
            missing_info[class_id] = info

    print("\nClasses missing from multiple bundles:")
    for class_id, count in sorted(missing_counts.items(), key=lambda x: -x[1]):
        if count >= 3:  # Appears in 3+ bundle analyses
            info = missing_info[class_id]
            print(f"\n  Class {class_id} ({info['role']}): missing in {count}/{len(results)} bundles")
            print(f"    B coverage: {info['b_coverage']}/82")
            print(f"    Total MIDDLEs: {info['total_middles']}")
            print(f"    Universal: {info['universal']}")
            print(f"    Restricted: {info['restricted']}")
            print(f"    A-exclusive: {info['a_exclusive']}")
            print(f"    In folio vocab: {info['in_folio_vocab']}")

    # Key insight: vocabulary-independent classes
    print("\n" + "=" * 70)
    print("KEY INSIGHT: VOCABULARY-INDEPENDENT CLASSES")
    print("=" * 70)

    vocab_independent = []
    for class_id, info in missing_info.items():
        # Class is vocabulary-independent if:
        # 1. High B coverage (>90%)
        # 2. Has only universal MIDDLEs OR no AZC MIDDLEs at all
        if info["b_coverage"] >= 75:  # 75/82 = 91%
            universal_only = (
                len(info["universal"]) > 0 and
                len(info["restricted"]) == 0
            )
            no_azc_middles = len(info["in_folio_vocab"]) == 0

            if universal_only:
                vocab_independent.append(class_id)
                print(f"  Class {class_id}: VOCABULARY-INDEPENDENT (universal MIDDLEs only)")
            elif no_azc_middles and len(info["a_exclusive"]) > 0:
                vocab_independent.append(class_id)
                print(f"  Class {class_id}: VOCABULARY-INDEPENDENT (A-exclusive MIDDLEs)")

    # Detailed analysis of high-coverage missing classes
    print("\n" + "-" * 70)
    print("DETAILED ANALYSIS: HIGH-COVERAGE MISSING CLASSES")
    print("-" * 70)

    high_coverage_missing = [
        (cid, info) for cid, info in missing_info.items()
        if info["b_coverage"] >= 75
    ]
    high_coverage_missing.sort(key=lambda x: -x[1]["b_coverage"])

    for class_id, info in high_coverage_missing:
        print(f"\nClass {class_id} ({info['role']}):")
        print(f"  B folio coverage: {info['b_coverage']}/82")

        # MIDDLE breakdown
        total = info['total_middles']
        u = len(info['universal'])
        r = len(info['restricted'])
        a = len(info['a_exclusive'])

        print(f"  MIDDLE composition: {total} total")
        u_pct = 100*u/total if total > 0 else 0
        r_pct = 100*r/total if total > 0 else 0
        a_pct = 100*a/total if total > 0 else 0
        print(f"    Universal (4+ folios): {u} ({u_pct:.0f}%)")
        print(f"    Restricted (1-3 folios): {r} ({r_pct:.0f}%)")
        print(f"    A-exclusive (0 folios): {a} ({a_pct:.0f}%)")

        # Diagnosis
        if a == total:
            print(f"  DIAGNOSIS: All MIDDLEs are A-exclusive -> AZC cannot see this class")
        elif r > 0:
            print(f"  DIAGNOSIS: Has restricted MIDDLEs -> May be legitimately pruned")
        else:
            print(f"  DIAGNOSIS: Universal MIDDLEs -> Should not be pruned by AZC")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if vocab_independent:
        print(f"\n{len(vocab_independent)} vocabulary-independent classes identified:")
        print(f"  {sorted(vocab_independent)}")
        print("\nThese classes should be immune to AZC vocabulary pruning because:")
        print("  - They have only universal MIDDLEs (appear in 4+ AZC folios)")
        print("  - OR they have A-exclusive MIDDLEs (AZC has no visibility)")
    else:
        print("\nNo clear vocabulary-independent classes identified.")
        print("All high-coverage classes have restricted MIDDLEs that could be legitimately pruned.")

    # Save results
    output_path = PROJECT_ROOT / "results" / "phase2_vocabulary_coupling.json"
    output_path.write_text(json.dumps({
        "analyzed_bundles": len(results),
        "vocab_independent_candidates": sorted(vocab_independent),
        "missing_class_details": {
            str(k): v for k, v in missing_info.items()
        },
        "missing_counts": {str(k): v for k, v in missing_counts.items()},
        "bundle_analyses": results
    }, indent=2, default=str))
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
