import json
from pathlib import Path

ROOT = Path("C:/git/voynich")

# Load both
print("=" * 60)
print("rosettes_annotated.json")
print("=" * 60)
d = json.load(open(ROOT / "data/rosettes_annotated.json", encoding="utf-8"))
print(f"Top-level type: {type(d).__name__}")
if isinstance(d, dict):
    print(f"Keys: {list(d.keys())}")
    for k in list(d.keys())[:10]:
        v = d[k]
        if isinstance(v, (list, dict)):
            print(f"  {k}: {type(v).__name__}, len={len(v)}")
            if isinstance(v, list) and v:
                print(f"    First item: {v[0]}")
        else:
            print(f"  {k}: {v}")

print("\n" + "=" * 60)
print("rosettes_unified.json")
print("=" * 60)
d2 = json.load(open(ROOT / "data/rosettes_unified.json", encoding="utf-8"))
print(f"Top-level type: {type(d2).__name__}")
if isinstance(d2, dict):
    print(f"Keys: {list(d2.keys())}")
    for k in list(d2.keys())[:10]:
        v = d2[k]
        if isinstance(v, (list, dict)):
            print(f"  {k}: {type(v).__name__}, len={len(v)}")
            if isinstance(v, list) and v:
                print(f"    First item: {v[0]}")
        else:
            print(f"  {k}: {v}")
