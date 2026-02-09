"""
02_multidim_matching.py

Score all (Brunschwig material, A record) pairs using multi-dimensional matching.

Scoring dimensions:
1. REGIME match (0.3 weight) - expected REGIME from fire degree
2. Instruction pattern similarity (0.4 weight) - PREFIX profile cosine similarity
3. Uniqueness (0.2 weight) - penalty for many matches
4. PP convergence (0.1 weight) - B folio convergence strength
"""

import json
import math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

# Paths
results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("MULTI-DIMENSIONAL MATERIAL MATCHING")
print("="*70)

# Load Brunschwig signatures
with open(results_dir / "brunschwig_signatures.json", encoding='utf-8') as f:
    signatures_data = json.load(f)
signatures = signatures_data['signatures']

# Load A record profiles
with open(results_dir / "a_record_profiles.json", encoding='utf-8') as f:
    profiles_data = json.load(f)
profiles = profiles_data['profiles']

print(f"Loaded {len(signatures)} Brunschwig signatures")
print(f"Loaded {len(profiles)} A record profiles")

# Matching weights
WEIGHTS = {
    'regime': 0.30,
    'prefix_similarity': 0.40,
    'uniqueness': 0.15,
    'convergence': 0.15,
}

def cosine_similarity(vec1, vec2, keys):
    """Compute cosine similarity between two prefix profile vectors."""
    v1 = np.array([vec1.get(k, 0) for k in keys])
    v2 = np.array([vec2.get(k, 0) for k in keys])

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(v1, v2) / (norm1 * norm2))

def regime_score(expected_regime, profile_regime):
    """Score REGIME match (1.0 = exact, 0.5 = adjacent, 0.0 = distant)."""
    if expected_regime == profile_regime:
        return 1.0
    elif abs(expected_regime - profile_regime) == 1:
        return 0.5
    else:
        return 0.0

def compute_match_score(signature, profile):
    """Compute multi-dimensional match score."""

    # Dimension 1: REGIME match
    expected_regime = signature.get('expected_regime', 1)
    profile_regime = profile.get('regime_number', 0)
    r_score = regime_score(expected_regime, profile_regime)

    # Dimension 2: PREFIX profile similarity
    sig_prefix = signature.get('prefix_profile', {})
    prof_prefix = profile.get('normalized_prefix_profile', {})
    keys = ['qo', 'ch_sh', 'ok_ot', 'da', 'ol_or']
    p_score = cosine_similarity(sig_prefix, prof_prefix, keys)

    # Dimension 3: Uniqueness (will be filled later)
    u_score = 1.0  # Placeholder

    # Dimension 4: PP convergence strength
    n_convergent = profile.get('n_convergent_folios', 0)
    # Normalize: 0 folios = 0, 82 folios = 1.0
    c_score = min(n_convergent / 82.0, 1.0)

    # Weighted sum
    score = (
        WEIGHTS['regime'] * r_score +
        WEIGHTS['prefix_similarity'] * p_score +
        WEIGHTS['uniqueness'] * u_score +
        WEIGHTS['convergence'] * c_score
    )

    return {
        'total_score': score,
        'regime_score': r_score,
        'prefix_similarity': p_score,
        'uniqueness_score': u_score,
        'convergence_score': c_score,
    }

# Compute all match scores
print("\nComputing match scores...")

match_results = []
for sig in signatures:
    for profile in profiles:
        scores = compute_match_score(sig, profile)

        match_results.append({
            'recipe_id': sig['recipe_id'],
            'recipe_name': sig['name_english'],
            'material_class': sig['material_class'],
            'fire_degree': sig['fire_degree'],
            'expected_regime': sig['expected_regime'],
            'record_id': profile['record_id'],
            'ri_tokens': profile['ri_tokens'],
            'known_animal_ri': profile.get('known_animal_ri', []),
            'folio_unique_ri': profile.get('folio_unique_ri', []),
            'profile_regime': profile.get('primary_regime', 'UNKNOWN'),
            **scores,
        })

print(f"Computed {len(match_results)} match scores")

# Compute uniqueness penalty
# Count how many profiles each signature matches well (score > 0.6)
print("\nComputing uniqueness penalties...")
sig_high_matches = defaultdict(list)
for m in match_results:
    if m['total_score'] > 0.6:
        sig_high_matches[m['recipe_id']].append(m['record_id'])

# Recompute scores with uniqueness
for m in match_results:
    n_matches = len(sig_high_matches.get(m['recipe_id'], []))
    if n_matches > 0:
        m['uniqueness_score'] = 1.0 / n_matches
    else:
        m['uniqueness_score'] = 1.0

    # Recompute total
    m['total_score'] = (
        WEIGHTS['regime'] * m['regime_score'] +
        WEIGHTS['prefix_similarity'] * m['prefix_similarity'] +
        WEIGHTS['uniqueness'] * m['uniqueness_score'] +
        WEIGHTS['convergence'] * m['convergence_score']
    )

# Sort by score
match_results.sort(key=lambda x: -x['total_score'])

# Filter to high-scoring matches
high_score_threshold = 0.7
high_matches = [m for m in match_results if m['total_score'] >= high_score_threshold]

print(f"\nMatches with score >= {high_score_threshold}: {len(high_matches)}")

# Show top matches
print("\n" + "="*70)
print("TOP 30 MATCHES")
print("="*70)

for i, m in enumerate(match_results[:30]):
    ri_display = ', '.join(m['ri_tokens'][:3])
    if len(m['ri_tokens']) > 3:
        ri_display += '...'

    known = ' [KNOWN ANIMAL]' if m['known_animal_ri'] else ''
    print(f"\n{i+1}. Score: {m['total_score']:.3f}{known}")
    print(f"   Material: {m['recipe_name']} ({m['material_class']}, degree {m['fire_degree']})")
    print(f"   A record: {m['record_id']} -> RI: {ri_display}")
    print(f"   Scores: regime={m['regime_score']:.2f}, prefix={m['prefix_similarity']:.2f}, "
          f"unique={m['uniqueness_score']:.2f}, conv={m['convergence_score']:.2f}")

# Focus on animal materials
print("\n" + "="*70)
print("ANIMAL MATERIAL MATCHES (Top by score)")
print("="*70)

animal_matches = [m for m in match_results if m['material_class'] == 'animal']
animal_matches.sort(key=lambda x: -x['total_score'])

for i, m in enumerate(animal_matches[:20]):
    ri_display = ', '.join(m['ri_tokens'][:3])
    known = ' [KNOWN]' if m['known_animal_ri'] else ''
    unique = ' [FOLIO-UNIQUE]' if m['folio_unique_ri'] else ''
    print(f"\n{i+1}. {m['recipe_name']} -> {m['record_id']}{known}{unique}")
    print(f"   Score: {m['total_score']:.3f} (regime={m['regime_score']:.2f}, "
          f"prefix={m['prefix_similarity']:.2f})")
    print(f"   RI tokens: {ri_display}")

# Match analysis: which records match multiple animals?
print("\n" + "="*70)
print("RECORDS MATCHING MULTIPLE ANIMAL RECIPES")
print("="*70)

record_animal_matches = defaultdict(list)
for m in animal_matches:
    if m['total_score'] > 0.6:
        record_animal_matches[m['record_id']].append({
            'recipe': m['recipe_name'],
            'score': m['total_score'],
        })

for record_id, matches in sorted(record_animal_matches.items(), key=lambda x: -len(x[1])):
    if len(matches) >= 2:
        print(f"\n{record_id}:")
        for match in sorted(matches, key=lambda x: -x['score']):
            print(f"  {match['recipe']}: {match['score']:.3f}")

# Best unique matches (record matches only one animal with high score)
print("\n" + "="*70)
print("UNIQUE ANIMAL MATCHES (record matches only 1 animal)")
print("="*70)

for record_id, matches in sorted(record_animal_matches.items(), key=lambda x: -x[1][0]['score'] if x[1] else 0):
    if len(matches) == 1 and matches[0]['score'] > 0.65:
        print(f"  {record_id} -> {matches[0]['recipe']} (score: {matches[0]['score']:.3f})")

# Summary by material class
print("\n" + "="*70)
print("TOP MATCH BY MATERIAL CLASS")
print("="*70)

material_best = {}
for m in match_results:
    key = m['material_class']
    if key not in material_best or m['total_score'] > material_best[key]['total_score']:
        material_best[key] = m

for mat_class in sorted(material_best.keys()):
    m = material_best[mat_class]
    ri_display = ', '.join(m['ri_tokens'][:2])
    print(f"  {mat_class:20} -> {m['record_id']:12} RI:{ri_display:20} score:{m['total_score']:.3f}")

# Save results
output = {
    'total_matches': len(match_results),
    'high_score_matches': len(high_matches),
    'weights': WEIGHTS,
    'threshold': high_score_threshold,
    'top_50_matches': match_results[:50],
    'animal_matches_top_30': animal_matches[:30],
    'material_class_best': material_best,
}

output_path = results_dir / "match_scores.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
