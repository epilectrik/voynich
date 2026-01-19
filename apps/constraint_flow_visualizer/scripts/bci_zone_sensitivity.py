"""
BCI Test 4: AZC Zone Sensitivity

Check if infrastructure classes are equally present across C/P/R/S zones.
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
    print("BCI TEST 4: AZC ZONE SENSITIVITY")
    print("=" * 70)

    ds = get_data_store()

    # Get infrastructure class MIDDLEs
    infra_middles = set()
    for class_id in INFRASTRUCTURE_CLASSES:
        cls = ds.classes.get(class_id)
        if cls and cls.middles:
            infra_middles |= cls.middles

    print(f"\nInfrastructure MIDDLEs: {sorted(infra_middles)}")

    # Check zone legality for each MIDDLE
    print("\n" + "-" * 70)
    print("ZONE LEGALITY FOR INFRASTRUCTURE MIDDLEs")
    print("-" * 70)

    zone_presence = defaultdict(lambda: {"legal": 0, "total": 0})

    for middle in infra_middles:
        zones = ds.middle_zone_legality.get(middle, set())
        print(f"\n  {middle}: {sorted(zones) if zones else '(no data)'}")

        for zone in ['C', 'P', 'R', 'S']:
            zone_presence[zone]["total"] += 1
            if zone in zones:
                zone_presence[zone]["legal"] += 1

    # Summary by zone
    print("\n" + "-" * 70)
    print("ZONE PRESENCE RATES")
    print("-" * 70)

    for zone in ['C', 'P', 'R', 'S']:
        legal = zone_presence[zone]["legal"]
        total = zone_presence[zone]["total"]
        pct = 100 * legal / total if total > 0 else 0
        print(f"\n  Zone {zone}: {legal}/{total} MIDDLEs legal ({pct:.1f}%)")

    # Check for gradient
    print("\n" + "-" * 70)
    print("ZONE GRADIENT ANALYSIS")
    print("-" * 70)

    rates = []
    for zone in ['C', 'P', 'R', 'S']:
        legal = zone_presence[zone]["legal"]
        total = zone_presence[zone]["total"]
        rate = legal / total if total > 0 else 0
        rates.append((zone, rate))

    # Check if monotonically decreasing
    is_decreasing = all(rates[i][1] >= rates[i+1][1] for i in range(len(rates)-1))
    spread = rates[0][1] - rates[-1][1] if rates else 0

    print(f"\nC -> P -> R -> S: {[f'{z}={r:.1%}' for z, r in rates]}")
    print(f"Spread (C - S): {spread:.1%}")

    if spread < 0.1:
        print("\nVERDICT: ZONE-INVARIANT (spread < 10%)")
        print("-> Infrastructure available equally across all zones")
    elif is_decreasing:
        print("\nVERDICT: FOLLOWS ESCAPE GRADIENT")
        print("-> Infrastructure thins in later zones (matches C443)")
    else:
        print("\nVERDICT: COMPLEX ZONE PATTERN")
        print("-> Non-monotonic zone sensitivity")

    # Save results
    output_path = PROJECT_ROOT / "results" / "bci_zone_sensitivity.json"
    output_path.write_text(json.dumps({
        "infrastructure_classes": sorted(INFRASTRUCTURE_CLASSES),
        "infrastructure_middles": sorted(infra_middles),
        "zone_presence": {k: dict(v) for k, v in zone_presence.items()}
    }, indent=2))
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
