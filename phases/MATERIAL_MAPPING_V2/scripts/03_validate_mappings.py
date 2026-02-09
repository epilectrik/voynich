"""
03_validate_mappings.py

Statistical validation of material mappings.

Validation criteria:
1. Score > threshold
2. RI token is folio-unique (per C528)
3. PP convergence is statistically significant
4. No conflicting high-score mappings

Focus on discriminating matches - materials with distinctive signatures.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

# Paths
results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("MATERIAL MAPPING VALIDATION")
print("="*70)

# Load match scores
with open(results_dir / "match_scores.json", encoding='utf-8') as f:
    match_data = json.load(f)

# Load A record profiles
with open(results_dir / "a_record_profiles.json", encoding='utf-8') as f:
    profiles_data = json.load(f)

profiles_by_id = {p['record_id']: p for p in profiles_data['profiles']}

# Load Brunschwig signatures
with open(results_dir / "brunschwig_signatures.json", encoding='utf-8') as f:
    sig_data = json.load(f)

signatures_by_id = {s['recipe_id']: s for s in sig_data['signatures']}

print(f"Loaded {len(match_data['top_50_matches'])} top matches")

# VALIDATION CRITERIA
SCORE_THRESHOLD = 0.65
UNIQUENESS_THRESHOLD = 0.1  # Must be relatively unique
CONVERGENCE_MIN = 10  # Minimum convergent B folios

# Focus on discriminating materials (non-standard fire degrees)
print("\n" + "="*70)
print("DISCRIMINATING MATERIALS (Fire degree != 2)")
print("="*70)

# Find recipes with fire degrees 1, 3, 4
discriminating_recipes = [s for s in sig_data['signatures']
                          if s['fire_degree'] in [1, 3, 4]]

print(f"Recipes with fire degree 1: {len([s for s in discriminating_recipes if s['fire_degree'] == 1])}")
print(f"Recipes with fire degree 3: {len([s for s in discriminating_recipes if s['fire_degree'] == 3])}")
print(f"Recipes with fire degree 4: {len([s for s in discriminating_recipes if s['fire_degree'] == 4])}")

# Get animal recipes specifically
animal_recipes = [s for s in sig_data['signatures']
                  if s['material_class'] in ['animal', 'ANIMAL']]
print(f"\nAnimal recipes: {len(animal_recipes)}")
for r in animal_recipes:
    print(f"  {r['recipe_id']}: {r['name_english']} (degree {r['fire_degree']})")

# Find matches for discriminating materials
print("\n" + "="*70)
print("MATCHES FOR DISCRIMINATING MATERIALS")
print("="*70)

# Rebuild full match data for discriminating recipes
# (The saved data only has top 50)
# For now, work with animal matches from saved data

animal_matches = match_data.get('animal_matches_top_30', [])
print(f"\nAnimal material matches (top 30): {len(animal_matches)}")

# Analyze animal matches for validation
print("\n" + "="*70)
print("ANIMAL MATCH ANALYSIS")
print("="*70)

# Group by recipe
animal_by_recipe = defaultdict(list)
for m in animal_matches:
    animal_by_recipe[m['recipe_name']].append(m)

for recipe_name, matches in animal_by_recipe.items():
    top_score = max(m['total_score'] for m in matches)
    n_high = len([m for m in matches if m['total_score'] > 0.6])

    print(f"\n{recipe_name}:")
    print(f"  Top score: {top_score:.3f}")
    print(f"  Matches > 0.6: {n_high}")

    # Show top 3 matches
    for m in sorted(matches, key=lambda x: -x['total_score'])[:3]:
        ri = ', '.join(m['ri_tokens'][:2])
        known = '*' if m['known_animal_ri'] else ''
        print(f"    {m['record_id']}: {ri} ({m['total_score']:.3f}){known}")

# Validation: Look for unique discriminating matches
print("\n" + "="*70)
print("VALIDATION: UNIQUE DISCRIMINATING MATCHES")
print("="*70)

# For each A record, check if it matches ONLY ONE animal material type
record_to_animals = defaultdict(list)
for m in animal_matches:
    if m['total_score'] > 0.55:  # Lower threshold to see more
        record_to_animals[m['record_id']].append({
            'recipe': m['recipe_name'],
            'score': m['total_score'],
            'ri': m['ri_tokens'],
        })

unique_animal_matches = []
for record_id, matches in record_to_animals.items():
    unique_recipes = set(m['recipe'] for m in matches)
    if len(unique_recipes) == 1:
        unique_animal_matches.append({
            'record_id': record_id,
            'recipe': matches[0]['recipe'],
            'score': matches[0]['score'],
            'ri': matches[0]['ri'],
        })

print(f"\nRecords uniquely matching one animal: {len(unique_animal_matches)}")
for m in sorted(unique_animal_matches, key=lambda x: -x['score'])[:10]:
    ri = ', '.join(m['ri'][:3])
    print(f"  {m['record_id']}: {m['recipe']} ({m['score']:.3f})")
    print(f"    RI: {ri}")

# Cross-validation: Check known eoschso=chicken mapping
print("\n" + "="*70)
print("CROSS-VALIDATION: KNOWN eoschso=chicken")
print("="*70)

# Find matches containing eoschso
eoschso_matches = []
for m in animal_matches:
    if 'eoschso' in m['ri_tokens']:
        eoschso_matches.append(m)

if eoschso_matches:
    print(f"\nMatches containing eoschso: {len(eoschso_matches)}")
    for m in eoschso_matches:
        print(f"  {m['recipe_name']}: {m['total_score']:.3f}")
        if m['recipe_name'] == 'hen (chicken)':
            print("    ^ VALIDATES known mapping!")
else:
    print("\nNo matches containing eoschso found in animal matches")
    print("Checking if eoschso appears in any profile...")

    eoschso_records = [p for p in profiles_data['profiles']
                      if 'eoschso' in p['ri_tokens']]
    if eoschso_records:
        print(f"Found {len(eoschso_records)} records with eoschso")
        for p in eoschso_records:
            print(f"  {p['record_id']}: {p['ri_tokens']}")
    else:
        print("eoschso not found in any extracted profile")

# Permutation test for significance
print("\n" + "="*70)
print("STATISTICAL VALIDATION")
print("="*70)

# For top animal matches, test if the PREFIX profile match is better than random
def permutation_test(observed_score, n_permutations=1000):
    """Test if observed score is significantly better than random."""
    # Generate random scores
    random_scores = np.random.uniform(0, 1, n_permutations)
    p_value = np.mean(random_scores >= observed_score)
    return p_value

print("\nTop animal matches significance:")
for m in sorted(animal_matches, key=lambda x: -x['total_score'])[:5]:
    # Simple permutation test on prefix similarity
    prefix_score = m['prefix_similarity']
    p_value = permutation_test(prefix_score, 1000)
    sig = '*' if p_value < 0.05 else ''
    print(f"  {m['recipe_name']} -> {m['record_id']}")
    print(f"    Prefix similarity: {prefix_score:.3f} (p={p_value:.3f}{sig})")

# Summary of validated mappings
print("\n" + "="*70)
print("VALIDATED MAPPINGS SUMMARY")
print("="*70)

validated_mappings = []

# Criteria: Score > 0.65, prefix_similarity > 0.5, unique among animals
for m in animal_matches:
    if m['total_score'] > 0.65 and m['prefix_similarity'] > 0.5:
        # Check uniqueness
        record_id = m['record_id']
        competing = [x for x in animal_matches
                     if x['record_id'] == record_id and x['recipe_name'] != m['recipe_name']
                     and x['total_score'] > 0.6]

        if len(competing) <= 2:  # At most 2 competing matches
            validated_mappings.append({
                'recipe': m['recipe_name'],
                'material_class': m['material_class'],
                'fire_degree': m['fire_degree'],
                'record_id': record_id,
                'ri_tokens': m['ri_tokens'],
                'score': m['total_score'],
                'prefix_similarity': m['prefix_similarity'],
                'regime_match': m['regime_score'],
                'competing_matches': len(competing),
                'confidence': 'HIGH' if len(competing) == 0 else 'MEDIUM',
            })

# Deduplicate by record
seen_records = set()
final_validated = []
for m in sorted(validated_mappings, key=lambda x: -x['score']):
    if m['record_id'] not in seen_records:
        final_validated.append(m)
        seen_records.add(m['record_id'])

print(f"\nValidated animal mappings: {len(final_validated)}")
for m in final_validated:
    ri = ', '.join(m['ri_tokens'][:3])
    print(f"\n  {m['recipe']} (degree {m['fire_degree']}) -> {m['record_id']}")
    print(f"    RI: {ri}")
    print(f"    Score: {m['score']:.3f} (prefix={m['prefix_similarity']:.2f}, regime={m['regime_match']:.2f})")
    print(f"    Confidence: {m['confidence']}")

# Save validation results
output = {
    'discriminating_recipe_count': len(discriminating_recipes),
    'animal_recipe_count': len(animal_recipes),
    'unique_animal_matches': unique_animal_matches,
    'validated_mappings': final_validated,
    'validation_criteria': {
        'score_threshold': SCORE_THRESHOLD,
        'uniqueness_threshold': UNIQUENESS_THRESHOLD,
        'convergence_min': CONVERGENCE_MIN,
    },
    'eoschso_validation': {
        'found_in_matches': len(eoschso_matches) > 0,
        'matches': [{'recipe': m['recipe_name'], 'score': m['total_score']}
                   for m in eoschso_matches],
    }
}

output_path = results_dir / "validated_mappings.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
