#!/usr/bin/env python3
"""
Audit fire_degree assignments in brunschwig_curated_v2.json

Questions:
1. Is fire_degree correlated with the stated distillation method?
2. Are there any suspicious patterns (e.g., all same value after ID X)?
3. Can we verify against the source text?
"""

import json
from collections import Counter, defaultdict

with open('data/brunschwig_curated_v2.json', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']

print("="*70)
print("FIRE DEGREE AUDIT")
print("="*70)

# Check 1: Fire degree distribution by ID range
print("\n1. FIRE DEGREE BY ID RANGE")
print("-"*50)

ranges = [(1, 50), (51, 100), (101, 150), (151, 200), (201, 250)]
for start, end in ranges:
    subset = [r for r in recipes if start <= r['id'] <= end]
    fire_dist = Counter(r.get('fire_degree') for r in subset)
    print(f"  ID {start:3d}-{end:3d}: {dict(sorted(fire_dist.items()))}")

# Check 2: Fire degree by method
print("\n2. FIRE DEGREE BY DISTILLATION METHOD")
print("-"*50)

method_fire = defaultdict(list)
for r in recipes:
    method = r.get('method') or 'NONE'
    fire = r.get('fire_degree')
    method_fire[method].append(fire)

for method, fires in sorted(method_fire.items()):
    dist = Counter(fires)
    print(f"  {method[:30]:<30}: {dict(sorted(dist.items()))}")

# Check 3: Fire degree by material class
print("\n3. FIRE DEGREE BY MATERIAL CLASS")
print("-"*50)

class_fire = defaultdict(list)
for r in recipes:
    cls = r.get('material_class', 'UNKNOWN')
    fire = r.get('fire_degree')
    class_fire[cls].append(fire)

for cls, fires in sorted(class_fire.items(), key=lambda x: -len(x[1]))[:15]:
    dist = Counter(fires)
    mean = sum(f for f in fires if f) / len([f for f in fires if f]) if any(fires) else 0
    print(f"  {cls[:25]:<25}: n={len(fires):3d}, mean={mean:.2f}, dist={dict(sorted(dist.items()))}")

# Check 4: Look for suspicious patterns
print("\n4. SUSPICIOUS PATTERN CHECK")
print("-"*50)

# Check if fire_degree is constant after some ID
prev_fire = None
constant_start = None
for r in sorted(recipes, key=lambda x: x['id']):
    fire = r.get('fire_degree')
    if prev_fire is not None and fire == prev_fire:
        if constant_start is None:
            constant_start = r['id'] - 1
    else:
        if constant_start is not None:
            run_length = r['id'] - constant_start
            if run_length >= 10:
                print(f"  Constant fire={prev_fire} from ID {constant_start} to {r['id']-1} ({run_length} recipes)")
            constant_start = None
    prev_fire = fire

# Check 5: Sample recipes with fire_degree vs method mismatch
print("\n5. SAMPLE ENTRIES FOR MANUAL VERIFICATION")
print("-"*50)

# In Brunschwig, typical mapping:
# - balneum marie (water bath) = gentle = degree 1
# - per alembicum (standard) = moderate = degree 2
# - ash/sand bath = stronger = degree 3
# - direct fire / animal = degree 4

suspicious = []
for r in recipes:
    method = (r.get('method') or '').lower()
    fire = r.get('fire_degree')

    # Flag potential mismatches
    if 'balne' in method and fire and fire > 1:
        suspicious.append((r['id'], r['name_english'], fire, method, 'balneum should be 1'))
    if fire == 1 and 'alembic' in method and 'balne' not in method:
        suspicious.append((r['id'], r['name_english'], fire, method, 'alembicum usually 2+'))

print(f"  Found {len(suspicious)} potentially suspicious entries")
for s in suspicious[:10]:
    print(f"    ID {s[0]}: {s[1][:20]:<20} fire={s[2]}, method={s[3][:20]}, issue={s[4]}")

# Check 6: First 20 entries vs last 20 entries comparison
print("\n6. FIRST 20 vs LAST 20 ENTRIES")
print("-"*50)

first20 = recipes[:20]
last20 = recipes[-20:]

print("First 20:")
for r in first20:
    fire = r.get('fire_degree', '?')
    method = (r.get('method') or 'none')[:15]
    print(f"  ID {r['id']:3d}: {r['name_english'][:25]:<25} fire={fire}, method={method}")

print("\nLast 20:")
for r in last20:
    fire = r.get('fire_degree', '?')
    method = (r.get('method') or 'none')[:15]
    print(f"  ID {r['id']:3d}: {r['name_english'][:25]:<25} fire={fire}, method={method}")
