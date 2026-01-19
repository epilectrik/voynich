"""Debug B folio reachability for activating bundles."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store
from core.constraint_bundle import compute_compatible_folios
from core.azc_projection import compute_reachable_classes, ALL_ZONES

ds = get_data_store()

# Bundle {n}
azc_active = frozenset({'n'})
compatible = compute_compatible_folios(azc_active, ds)
print(f"Bundle {{n}} compatible AZC folios: {sorted(compatible)}")

# Effective vocabulary
effective_middles = set()
for folio_id in compatible:
    vocab = ds.azc_folio_middles.get(folio_id, set())
    effective_middles |= vocab
    print(f"  {folio_id} vocab size: {len(vocab)}")

print(f"\nEffective MIDDLEs ({len(effective_middles)}): {sorted(effective_middles)[:20]}...")

# Class reachability at zone C
zone_legal = set()
for m in effective_middles:
    legal_zones = ds.middle_zone_legality.get(m, ALL_ZONES)
    if 'C' in legal_zones:
        zone_legal.add(m)

print(f"\nZone-legal MIDDLEs at C: {len(zone_legal)}")

reachable = compute_reachable_classes(zone_legal, ds)
print(f"Reachable classes at C: {len(reachable)}")
print(f"  Classes: {sorted(reachable)}")
print(f"\nKernel classes: {len(ds.kernel_classes)}")
print(f"  Classes: {sorted(ds.kernel_classes)}")

# Check a B folio's requirements
print("\n" + "=" * 60)
print("B FOLIO REQUIREMENTS")
print("=" * 60)

for b_folio in ['f103r', 'f104r', 'f116r']:
    required = ds.b_folio_class_footprints.get(b_folio, set())
    missing = required - reachable
    print(f"\n{b_folio}:")
    print(f"  Required: {len(required)} classes -> {sorted(required)[:15]}...")
    print(f"  Missing: {len(missing)} -> {sorted(missing)[:10]}")

    if required <= reachable:
        print(f"  STATUS: REACHABLE")
    else:
        print(f"  STATUS: BLOCKED (missing {len(missing)} classes)")
