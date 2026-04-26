"""
Phase 648 Step 1: Profile o-prefix usage per folio (no hypothesis, just data).

Goal: For each o-prefix (ok, ot, ol, or), identify which folios are
enriched, depleted, and average. Cross-reference with matched recipes
to see what kind of operational content each prefix concentrates on.

Output: phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json
"""
import sys
import json
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Per-folio counts for each o-prefix
folio_stats = defaultdict(lambda: {
    'total': 0,
    'ok': 0, 'ot': 0, 'ol': 0, 'or': 0,
})

for t in tx.currier_b():
    f = t.folio
    folio_stats[f]['total'] += 1
    w = t.word
    # Word starts with o + one of k/t/l/r — pure 2-char prefix
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k', 't', 'l', 'r'):
        folio_stats[f]['o' + w[1]] += 1

# Compute fractions
profile = {}
for f, s in folio_stats.items():
    if s['total'] < 30:
        continue  # filter tiny folios
    profile[f] = {
        'total': s['total'],
        'ok_frac': s['ok'] / s['total'],
        'ot_frac': s['ot'] / s['total'],
        'ol_frac': s['ol'] / s['total'],
        'or_frac': s['or'] / s['total'],
        'ok_n': s['ok'], 'ot_n': s['ot'],
        'ol_n': s['ol'], 'or_n': s['or'],
    }

# Aggregate stats
all_folios = list(profile.keys())
n_folios = len(all_folios)
print(f"Currier B folios profiled (>=30 tokens): {n_folios}")
print()

for prefix in ('ok', 'ot', 'ol', 'or'):
    fracs = [profile[f][f'{prefix}_frac'] for f in all_folios]
    mean_frac = sum(fracs) / len(fracs)
    sorted_folios = sorted(all_folios, key=lambda f: -profile[f][f'{prefix}_frac'])
    print(f"=== {prefix} ===")
    print(f"  Mean rate across folios: {mean_frac*100:.2f}%")
    print(f"  Top 8 enriched folios:")
    for f in sorted_folios[:8]:
        p = profile[f]
        print(f"    {f}: {p[f'{prefix}_frac']*100:5.2f}%  ({p[f'{prefix}_n']:3d}/{p['total']:4d})")
    print(f"  Bottom 5 (least enriched):")
    for f in sorted_folios[-5:]:
        p = profile[f]
        print(f"    {f}: {p[f'{prefix}_frac']*100:5.2f}%  ({p[f'{prefix}_n']:3d}/{p['total']:4d})")
    print()

# Pairwise correlation between fractions
import math
def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

prefixes = ('ok','ot','ol','or')
print("Pairwise correlation between o-prefix folio rates:")
print("        " + " ".join(f"{p:>7s}" for p in prefixes))
for p1 in prefixes:
    row = [f"{p1:>7s}"]
    for p2 in prefixes:
        if p1 == p2:
            row.append(f"{1.00:7.3f}")
        else:
            xs = [profile[f][f'{p1}_frac'] for f in all_folios]
            ys = [profile[f][f'{p2}_frac'] for f in all_folios]
            row.append(f"{pearson(xs,ys):7.3f}")
    print(" ".join(row))

print()
print("Interpretation key:")
print("  Strong negative correlation (< -0.3): orthogonal channels (different folios use them)")
print("  Near-zero correlation (-0.2 to +0.2): independent channels")
print("  Strong positive (> +0.3): channels co-vary (might share folio-level driver)")

# Save
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json', 'w') as f:
    json.dump(profile, f, indent=2)

print(f"\nSaved profile to phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json")
