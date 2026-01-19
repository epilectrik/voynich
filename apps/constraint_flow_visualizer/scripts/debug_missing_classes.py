"""Debug the missing classes that block B folios."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "constraint_flow_visualizer"))

from core.data_loader import get_data_store

ds = get_data_store()

missing_classes = {36, 44, 46, 48}

print("=" * 60)
print("ANALYSIS OF MISSING CLASSES")
print("=" * 60)

for class_id in sorted(missing_classes):
    cls = ds.classes.get(class_id)
    print(f"\nClass {class_id}:")
    if cls:
        print(f"  Role: {cls.role}")
        print(f"  MIDDLEs: {cls.middles}")
        print(f"  Is kernel: {class_id in ds.kernel_classes}")
        print(f"  Is hazard: {class_id in ds.hazard_classes}")

        # Check MIDDLE folio spreads
        for m in cls.middles:
            spread = ds.middle_folio_spread.get(m, 0)
            print(f"    MIDDLE '{m}' spread: {spread} AZC folios")
    else:
        print("  NOT FOUND in data_store.classes")

# Check how many B folios require these classes
print("\n" + "=" * 60)
print("B FOLIO REQUIREMENTS FOR MISSING CLASSES")
print("=" * 60)

for class_id in sorted(missing_classes):
    count = sum(
        1 for folio, classes in ds.b_folio_class_footprints.items()
        if class_id in classes
    )
    print(f"Class {class_id}: required by {count}/{len(ds.b_folio_class_footprints)} B folios")

# Check if these classes are in kernel
print("\n" + "=" * 60)
print("KERNEL CLASS CHECK")
print("=" * 60)
print(f"Kernel classes ({len(ds.kernel_classes)}): {sorted(ds.kernel_classes)}")
print(f"Missing classes in kernel: {missing_classes & ds.kernel_classes}")
print(f"Missing classes NOT in kernel: {missing_classes - ds.kernel_classes}")
