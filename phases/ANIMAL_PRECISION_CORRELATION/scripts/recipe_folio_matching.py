#!/usr/bin/env python3
"""
Explore whether Brunschwig animal recipe structures could match
specific REGIME_4 folio profiles.

Recipe characteristics from Brunschwig:
- Küetreck (cow dung): 2-stage distillation, timing-specific, 9+ uses
- Hennen (chicken): 4 prep steps, 2-stage distillation, 1 use
- Kalbs blůt+lungen: Simple prep, 1-stage, 1 use
- Kalbs leber: Minimal prep, 1-stage, 1 use

Question: Do REGIME_4 folios show enough internal variation to
potentially distinguish recipe types?
"""

import json
import statistics
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load scaffold data
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json', 'r') as f:
    scaffold_data = json.load(f)

# REGIME_4 folios
regime4_folios = [
    "f26r", "f31v", "f34r", "f34v", "f39v", "f40r", "f40v", "f41r", "f41v",
    "f43r", "f43v", "f46v", "f50r", "f50v", "f55r", "f55v", "f57r", "f66v",
    "f85r1", "f85r2", "f86v6", "f94r", "f94v", "f95v1", "f95v2"
]

# Extract features for REGIME_4 folios
features_to_check = [
    'near_miss_count', 'recovery_ops_count', 'hazard_density',
    'intervention_frequency', 'mean_cycle_length', 'cycle_regularity',
    'cei_total', 'link_density'
]

print("=" * 70)
print("REGIME_4 FOLIO STRUCTURAL VARIATION")
print("=" * 70)
print()

# Collect data
r4_data = {}
for folio in regime4_folios:
    if folio in scaffold_data['features']:
        r4_data[folio] = scaffold_data['features'][folio]

print(f"REGIME_4 folios with data: {len(r4_data)}")
print()

# Analyze variation in each feature
print("-" * 70)
print("FEATURE VARIATION WITHIN REGIME_4")
print("-" * 70)
print()

feature_stats = {}
for feature in features_to_check:
    values = [r4_data[f].get(feature, 0) for f in r4_data]
    if values:
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        min_val = min(values)
        max_val = max(values)
        cv = std_val / mean_val if mean_val > 0 else 0
        feature_stats[feature] = {
            'mean': mean_val, 'std': std_val, 'min': min_val,
            'max': max_val, 'cv': cv
        }
        print(f"{feature:25s}: mean={mean_val:.2f}, std={std_val:.2f}, "
              f"range=[{min_val:.2f}-{max_val:.2f}], CV={cv:.2f}")

print()
print("-" * 70)
print("HIGHEST VARIATION FEATURES (potential discriminators)")
print("-" * 70)
print()

# Sort by coefficient of variation
sorted_features = sorted(feature_stats.items(), key=lambda x: x[1]['cv'], reverse=True)
for feature, stats in sorted_features[:5]:
    print(f"{feature}: CV={stats['cv']:.2f} (range {stats['min']:.2f}-{stats['max']:.2f})")

print()
print("-" * 70)
print("CLUSTERING ATTEMPT: Group REGIME_4 folios by profile")
print("-" * 70)
print()

# Use near_miss_count and recovery_ops_count as discriminators
# (These showed meaningful variation in our earlier tests)

# Create simple bins
low_recovery = []
high_recovery = []
low_near_miss = []
high_near_miss = []

median_recovery = statistics.median([r4_data[f]['recovery_ops_count'] for f in r4_data])
median_near_miss = statistics.median([r4_data[f]['near_miss_count'] for f in r4_data])

print(f"Median recovery_ops: {median_recovery}")
print(f"Median near_miss: {median_near_miss}")
print()

# Four-way classification
quadrants = {
    'low_recovery_low_escape': [],
    'low_recovery_high_escape': [],
    'high_recovery_low_escape': [],
    'high_recovery_high_escape': []
}

for folio in r4_data:
    rec = r4_data[folio]['recovery_ops_count']
    nm = r4_data[folio]['near_miss_count']

    if rec <= median_recovery and nm <= median_near_miss:
        quadrants['low_recovery_low_escape'].append(folio)
    elif rec <= median_recovery and nm > median_near_miss:
        quadrants['low_recovery_high_escape'].append(folio)
    elif rec > median_recovery and nm <= median_near_miss:
        quadrants['high_recovery_low_escape'].append(folio)
    else:
        quadrants['high_recovery_high_escape'].append(folio)

print("Folio clustering by recovery/escape profile:")
for quadrant, folios in quadrants.items():
    print(f"\n{quadrant}: {len(folios)} folios")
    for f in folios:
        rec = r4_data[f]['recovery_ops_count']
        nm = r4_data[f]['near_miss_count']
        haz = r4_data[f]['hazard_density']
        print(f"  {f}: recovery={rec}, near_miss={nm}, hazard={haz:.3f}")

print()
print("=" * 70)
print("POTENTIAL BRUNSCHWIG RECIPE -> PROFILE MAPPING")
print("=" * 70)
print()

print("""
Hypothesis (SPECULATIVE):

Recipe Complexity         | Expected REGIME_4 Profile
--------------------------|---------------------------
Simple (1-stage, 1 use)   | low_recovery, low_escape
  - Kalbs leber           | Straightforward procedure
  - Kalbs blut+lungen     | Minimal intervention needed
                          |
Complex (2-stage, multi)  | low_recovery, high_escape
  - Kuetreck              | Timing-critical (mid-May)
  - Hennen                | Multi-step prep needed
                          | Near-miss = narrow window
                          | Low recovery = precision req'd

This is TIER 4 speculation. We cannot prove which folio matches
which recipe because:
1. Animal-associated A tokens don't appear in B
2. C384 blocks A-B entry coupling
3. We're matching structural patterns, not vocabulary

The mapping would require external evidence (illustrations,
codicological analysis) to validate.
""")

# Save results
results = {
    'regime4_folio_count': len(r4_data),
    'feature_variation': feature_stats,
    'folio_clustering': {k: v for k, v in quadrants.items()},
    'folio_details': {
        folio: {
            'recovery_ops_count': r4_data[folio]['recovery_ops_count'],
            'near_miss_count': r4_data[folio]['near_miss_count'],
            'hazard_density': r4_data[folio]['hazard_density'],
            'cei_total': r4_data[folio]['cei_total']
        }
        for folio in r4_data
    }
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'recipe_folio_matching.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
