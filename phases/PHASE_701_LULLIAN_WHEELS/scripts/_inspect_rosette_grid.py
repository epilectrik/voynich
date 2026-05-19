import json
from pathlib import Path

ROOT = Path("C:/git/voynich")
d = json.load(open(ROOT / "data/rosettes_unified.json", encoding="utf-8"))

print("ROSETTE GRID:")
grid = d["rosette_grid"]
for pos, info in grid.items():
    print(f"\n  {pos}:")
    if isinstance(info, dict):
        for k, v in info.items():
            if isinstance(v, (list, dict)) and len(str(v)) > 200:
                print(f"    {k}: {type(v).__name__}, len={len(v)}")
            else:
                print(f"    {k}: {v}")
    else:
        print(f"    {info}")

print("\n\nREGION TO ROSETTE MAP:")
print(json.dumps(d["region_to_rosette_map"], indent=2)[:1500])

print("\n\nTOPOLOGY:")
print(json.dumps(d["topology"], indent=2)[:1500])

print("\n\nFUNCTIONAL PROFILES:")
print(json.dumps(d["functional_profiles"], indent=2)[:2000])
