"""
Phase 598b: Compute distributional properties of 1512 recipes.
These distributions drive the pre-registered predictions.
All numbers here come ONLY from the 1512 book.
"""

import json
from collections import Counter
from pathlib import Path

RECIPES = Path("phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/brunschwig_1512_recipes.json")

with open(RECIPES) as f:
    data = json.load(f)

# Filter to confirmed recipes in book content
recipes = [r for r in data['recipes']
           if r['classification'] == 'recipe'
           and r['book'] not in ('front_matter', 'back_matter')]

print(f"Confirmed recipes: {len(recipes)}")

# === Fire Degree Distribution ===
degrees = [r['fire_degree']['inferred_class'] for r in recipes]
total = len(degrees)
deg_counts = Counter(degrees)
print(f"\n=== Fire Degree Distribution ===")
for d in [1, 2, 3, 4, None]:
    n = deg_counts.get(d, 0)
    pct = 100 * n / total
    print(f"  Degree {d}: {n} ({pct:.1f}%)")

# Bin into gentle (1) vs elevated (2+3+4)
gentle = deg_counts.get(1, 0)
elevated = deg_counts.get(2, 0) + deg_counts.get(3, 0) + deg_counts.get(4, 0)
unspec = deg_counts.get(None, 0)
specified = gentle + elevated
print(f"\n  Gentle (d1): {gentle} ({100*gentle/specified:.1f}% of specified)")
print(f"  Elevated (d2+3+4): {elevated} ({100*elevated/specified:.1f}% of specified)")
print(f"  Unspecified: {unspec}")
print(f"  Gentle:Elevated ratio = {gentle/elevated:.1f}:1")

# === Method Distribution ===
print(f"\n=== Method Distribution ===")
method_counts = Counter()
for r in recipes:
    for m in r['methods']:
        method_counts[m] += 1
for m, c in method_counts.most_common():
    print(f"  {m}: {c} ({100*c/total:.1f}%)")

# === Method Complexity ===
method_complexities = [len(r['methods']) for r in recipes]
print(f"\n=== Method Complexity (methods per recipe) ===")
complexity_counts = Counter(method_complexities)
for c in sorted(complexity_counts):
    print(f"  {c} methods: {complexity_counts[c]} recipes")
avg_complexity = sum(method_complexities) / len(method_complexities)
print(f"  Mean: {avg_complexity:.2f}")

# Complexity by degree
print(f"\n=== Mean Method Complexity by Fire Degree ===")
for d in [1, 2, 3, None]:
    d_recipes = [r for r in recipes if r['fire_degree']['inferred_class'] == d]
    if d_recipes:
        mc = [len(r['methods']) for r in d_recipes]
        print(f"  Degree {d}: {sum(mc)/len(mc):.2f} methods/recipe (n={len(d_recipes)})")

# === Product Type by Degree ===
print(f"\n=== Product Type by Fire Degree ===")
for d in [1, 2, 3]:
    d_recipes = [r for r in recipes if r['fire_degree']['inferred_class'] == d]
    prods = Counter(r['primary_product'] for r in d_recipes)
    print(f"  Degree {d} (n={len(d_recipes)}): {dict(prods.most_common(5))}")

# === Distillation Step Depth ===
print(f"\n=== Distillation Step Depth ===")
distill_refs = [r['distillation_steps']['distill_references'] for r in recipes]
print(f"  Mean distill references: {sum(distill_refs)/len(distill_refs):.2f}")
print(f"  Max named distillation: max across recipes = {max(r['distillation_steps']['max_named'] for r in recipes)}")

# By degree
for d in [1, 2, 3]:
    d_recipes = [r for r in recipes if r['fire_degree']['inferred_class'] == d]
    if d_recipes:
        refs = [r['distillation_steps']['distill_references'] for r in d_recipes]
        named = [r['distillation_steps']['max_named'] for r in d_recipes]
        print(f"  Degree {d}: mean refs={sum(refs)/len(refs):.2f}, mean max_named={sum(named)/len(named):.2f}")

# === Key Ratios for Prediction Thresholds ===
print(f"\n=== KEY RATIOS FOR PREDICTION THRESHOLDS ===")
print(f"  Gentle fraction (of specified): {gentle/specified:.3f}")
print(f"  Elevated fraction (of specified): {elevated/specified:.3f}")
print(f"  Gentle:Elevated ratio: {gentle/elevated:.1f}:1")
print(f"  Balneum Mariae prevalence: {method_counts.get('balneum_mariae',0)/total:.3f}")
print(f"  Multi-method recipe fraction: {sum(1 for r in recipes if len(r['methods'])>=2)/total:.3f}")

# Book distribution for elevated recipes
print(f"\n=== Elevated Recipes by Book ===")
elevated_recipes = [r for r in recipes
                    if r['fire_degree']['inferred_class'] in (2, 3, 4)]
book_dist = Counter(r['book'] for r in elevated_recipes)
for b, c in book_dist.most_common():
    print(f"  {b}: {c}")

# Vessel distribution
print(f"\n=== Vessel Types ===")
vessel_counts = Counter()
for r in recipes:
    for v in r['vessels']:
        vessel_counts[v] += 1
for v, c in vessel_counts.most_common():
    print(f"  {v}: {c}")
