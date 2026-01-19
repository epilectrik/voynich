"""
BCI Test 1: REGIME Invariance

Check if infrastructure classes appear equally across all REGIMEs.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store

INFRASTRUCTURE_CLASSES = {44, 46, 42, 36}

def main():
    print("=" * 70)
    print("BCI TEST 1: REGIME INVARIANCE")
    print("=" * 70)

    ds = get_data_store()

    # Load REGIME assignments
    regime_path = PROJECT_ROOT / "results" / "regime_folio_mapping.json"
    if not regime_path.exists():
        print("ERROR: regime_folio_mapping.json not found")
        print("Need to run REGIME assignment phase first")
        return

    regime_data = json.loads(regime_path.read_text())

    # Build folio -> regime mapping
    folio_to_regime = {}
    for regime, folios in regime_data.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    print(f"\nLoaded {len(folio_to_regime)} folio REGIME assignments")

    # For each REGIME, compute infrastructure class presence
    regime_presence = defaultdict(lambda: defaultdict(int))
    regime_folio_count = defaultdict(int)

    for folio, classes in ds.b_folio_class_footprints.items():
        regime = folio_to_regime.get(folio, "UNKNOWN")
        regime_folio_count[regime] += 1

        for infra_class in INFRASTRUCTURE_CLASSES:
            if infra_class in classes:
                regime_presence[regime][infra_class] += 1

    # Report
    print("\n" + "-" * 70)
    print("INFRASTRUCTURE CLASS PRESENCE BY REGIME")
    print("-" * 70)

    for regime in sorted(regime_folio_count.keys()):
        total = regime_folio_count[regime]
        print(f"\n{regime} ({total} folios):")

        for infra_class in sorted(INFRASTRUCTURE_CLASSES):
            present = regime_presence[regime][infra_class]
            pct = 100 * present / total if total > 0 else 0
            print(f"  Class {infra_class}: {present}/{total} ({pct:.1f}%)")

    # Invariance test: check if presence rates are similar across REGIMEs
    print("\n" + "-" * 70)
    print("INVARIANCE ANALYSIS")
    print("-" * 70)

    for infra_class in sorted(INFRASTRUCTURE_CLASSES):
        rates = []
        for regime in sorted(regime_folio_count.keys()):
            if regime == "UNKNOWN":
                continue
            total = regime_folio_count[regime]
            present = regime_presence[regime][infra_class]
            rate = present / total if total > 0 else 0
            rates.append((regime, rate))

        if rates:
            min_rate = min(r[1] for r in rates)
            max_rate = max(r[1] for r in rates)
            spread = max_rate - min_rate

            print(f"\nClass {infra_class}:")
            print(f"  Min rate: {min_rate:.1%} ({[r[0] for r in rates if r[1] == min_rate]})")
            print(f"  Max rate: {max_rate:.1%} ({[r[0] for r in rates if r[1] == max_rate]})")
            print(f"  Spread: {spread:.1%}")

            if spread < 0.05:
                print(f"  VERDICT: REGIME-INVARIANT (spread < 5%)")
            else:
                print(f"  VERDICT: REGIME-SENSITIVE (spread >= 5%)")

    # Save results
    output = {
        "infrastructure_classes": sorted(INFRASTRUCTURE_CLASSES),
        "regime_presence": {k: dict(v) for k, v in regime_presence.items()},
        "regime_folio_count": dict(regime_folio_count)
    }

    output_path = PROJECT_ROOT / "results" / "bci_regime_invariance.json"
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
