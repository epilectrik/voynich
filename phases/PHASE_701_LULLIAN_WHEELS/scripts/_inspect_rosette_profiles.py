import json
from pathlib import Path

ROOT = Path("C:/git/voynich")
d = json.load(open(ROOT / "data/rosettes_unified.json", encoding="utf-8"))

grid = d["rosette_grid"]

print("="*70)
print("ROSETTE COMBINED PROFILES")
print("="*70)
for pos, info in grid.items():
    profile = info.get("combined_profile", {})
    print(f"\n{pos} (type: {info.get('type','?')}, connects: {info.get('connects_to','?')}):")
    print(f"  n_tokens: {profile.get('n_tokens', '?')}")
    if isinstance(profile, dict):
        for k, v in profile.items():
            if isinstance(v, dict):
                print(f"  {k}: dict, len={len(v)}")
                if len(v) < 10:
                    for sk, sv in v.items():
                        print(f"    {sk}: {sv}")
            elif isinstance(v, list):
                print(f"  {k}: list, len={len(v)}, sample={v[:3]}")
            else:
                print(f"  {k}: {v}")

print("\n\n" + "="*70)
print("FUNCTIONAL PROFILES")
print("="*70)
print(json.dumps(d["functional_profiles"], indent=2)[:3000])
