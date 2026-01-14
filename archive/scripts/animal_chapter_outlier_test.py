"""
Animal Chapter Outlier Test

Puff Chapter 71 = "Küdreck" (cow dung) - ONLY animal-based chapter
Position: Last third (chapter 71 of 84)
Category: ANIMAL (unique in the corpus)

Animal distillation would differ from plant distillation:
- Different volatiles (not essential oils)
- Different decomposition hazards
- Possibly different fire requirements
- Unusual process structure

Look for structural outliers in Voynich's last third that might match.
"""

import json
from statistics import mean, stdev

with open('results/b_macro_scaffold_audit.json', 'r') as f:
    data = json.load(f)

folios = list(data['features'].keys())
n = len(folios)
third = n // 3

# Focus on last third (where Puff's animal chapter sits)
last_third = folios[2*third:]

print("="*70)
print("ANIMAL CHAPTER OUTLIER TEST")
print("="*70)
print(f"\nPuff Chapter 71: 'Kudreck' (cow dung)")
print(f"  - Position: Chapter 71 of 84 (last third)")
print(f"  - Category: ANIMAL (unique in corpus)")
print(f"  - Expected characteristics: structural outlier")

print(f"\nSearching Voynich last third ({len(last_third)} folios) for outliers...")

# Calculate global statistics for outlier detection
all_metrics = {
    'cei': [data['features'][f]['cei_total'] for f in folios],
    'hazard': [data['features'][f]['hazard_density'] for f in folios],
    'intervention': [data['features'][f]['intervention_frequency'] for f in folios],
    'near_miss': [data['features'][f]['near_miss_count'] for f in folios],
    'recovery': [data['features'][f]['recovery_ops_count'] for f in folios],
    'cycle': [data['features'][f]['mean_cycle_length'] for f in folios],
    'kernel_k': [data['features'][f]['kernel_dominance_k'] for f in folios],
}

# Calculate means and stdevs
stats = {}
for metric, values in all_metrics.items():
    stats[metric] = {'mean': mean(values), 'std': stdev(values)}

print("\n" + "-"*70)
print("OUTLIER DETECTION (>2 std from mean)")
print("-"*70)

# Find outliers in last third
def is_outlier(value, metric_stats, threshold=2.0):
    z = abs(value - metric_stats['mean']) / metric_stats['std']
    return z > threshold, z

outlier_scores = {}
for f in last_third:
    feat = data['features'][f]
    scores = {}
    outlier_count = 0

    # Map metric names to feature names
    metric_map = {
        'cei': 'cei_total',
        'hazard': 'hazard_density',
        'intervention': 'intervention_frequency',
        'near_miss': 'near_miss_count',
        'recovery': 'recovery_ops_count',
        'cycle': 'mean_cycle_length',
        'kernel_k': 'kernel_dominance_k'
    }

    for metric in all_metrics.keys():
        value = feat[metric_map[metric]]
        is_out, z = is_outlier(value, stats[metric])
        scores[metric] = {'value': value, 'z': z, 'outlier': is_out}
        if is_out:
            outlier_count += 1

    outlier_scores[f] = {'scores': scores, 'outlier_count': outlier_count}

# Sort by outlier count
ranked = sorted(outlier_scores.items(), key=lambda x: x[1]['outlier_count'], reverse=True)

print("\nFolios ranked by outlier count (last third only):")
print("-"*70)

for f, info in ranked[:10]:
    feat = data['features'][f]
    print(f"\n{f}: {info['outlier_count']} outlier metrics")
    print(f"  Regime: {feat['regime']}")
    print(f"  CEI: {feat['cei_total']:.3f} (z={info['scores']['cei']['z']:.2f})")
    print(f"  Hazard: {feat['hazard_density']:.3f} (z={info['scores']['hazard']['z']:.2f})")
    print(f"  Near-miss: {feat['near_miss_count']} (z={info['scores']['near_miss']['z']:.2f})")
    print(f"  Recovery: {feat['recovery_ops_count']} (z={info['scores']['recovery']['z']:.2f})")

    # Flag if multiple outliers
    if info['outlier_count'] >= 2:
        print(f"  *** CANDIDATE: Multiple outlier dimensions ***")

# Look for the MOST anomalous folio
print("\n" + "="*70)
print("STRONGEST OUTLIER CANDIDATE")
print("="*70)

if ranked[0][1]['outlier_count'] >= 2:
    top = ranked[0]
    f = top[0]
    feat = data['features'][f]

    print(f"\nFolio {f} shows {top[1]['outlier_count']} outlier dimensions")
    print(f"\nFull profile:")
    for metric, score in top[1]['scores'].items():
        flag = " <-- OUTLIER" if score['outlier'] else ""
        print(f"  {metric}: {score['value']:.3f} (z={score['z']:.2f}){flag}")

    print(f"\nInterpretation:")
    print(f"  Position in last third: YES (matches Puff Ch.71 position)")
    print(f"  Structural outlier: YES ({top[1]['outlier_count']} dimensions)")
    print(f"  Candidate for 'animal chapter' analog: POSSIBLE")
else:
    print("\nNo strong multi-dimensional outliers found in last third")

# Also check: what makes Chapter 71 (animal) different from Chapter 72 (fungus)?
# Both are anomalous categories but different types of anomaly
print("\n" + "="*70)
print("PUFF ANOMALOUS CHAPTERS IN LAST THIRD")
print("="*70)
print("""
From puff_83_chapters.json:
  Ch.71: Kudreck (cow dung) - ANIMAL - only animal chapter
  Ch.72: Schwammen (mushroom) - FUNGUS
  Ch.53: Pfifferling (pepper mushroom) - FUNGUS
  Ch.74: Rosen ol (rose oil) - OIL (not water)
  Ch.83: Kranwitber (juniper) - BERRY - external source, HAS METHOD
  Ch.84: Weyn gepranter (brandy) - SPIRIT - external source

If Voynich mirrors this, last third should have:
  - One major outlier (animal analog)
  - A few moderate outliers (fungus, oil, spirit analogs)
""")

# Count outliers by level
major_outliers = [f for f, info in outlier_scores.items() if info['outlier_count'] >= 3]
moderate_outliers = [f for f, info in outlier_scores.items() if info['outlier_count'] == 2]
minor_outliers = [f for f, info in outlier_scores.items() if info['outlier_count'] == 1]

print(f"Voynich last third outlier distribution:")
print(f"  Major outliers (3+ dimensions): {len(major_outliers)}")
print(f"  Moderate outliers (2 dimensions): {len(moderate_outliers)}")
print(f"  Minor outliers (1 dimension): {len(minor_outliers)}")
print(f"  No outliers: {len(last_third) - len(major_outliers) - len(moderate_outliers) - len(minor_outliers)}")

print(f"\nPuff last third anomalous chapters: ~6 (animal, 2x fungus, oil, berry, spirit)")
print(f"Voynich last third multi-dimensional outliers: {len(major_outliers) + len(moderate_outliers)}")

match = abs((len(major_outliers) + len(moderate_outliers)) - 6) <= 3
print(f"\nProportional match: {'YES' if match else 'NO'}")

# Save results
results = {
    "test": "Animal Chapter Outlier Detection",
    "puff_reference": {
        "chapter": 71,
        "name": "Kudreck (cow dung)",
        "category": "ANIMAL",
        "position": "last_third",
        "uniqueness": "only animal chapter in corpus"
    },
    "voynich_last_third": {
        "n_folios": len(last_third),
        "major_outliers": major_outliers,
        "moderate_outliers": moderate_outliers,
        "minor_outliers": minor_outliers
    },
    "top_candidates": [
        {"folio": f, "outlier_count": info['outlier_count'], "regime": data['features'][f]['regime']}
        for f, info in ranked[:5]
    ],
    "proportional_match": match
}

with open('results/animal_chapter_outlier_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to results/animal_chapter_outlier_test.json")
