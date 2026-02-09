"""
11_precision_analysis.py

Deep analysis of PRECISION handling candidates (potential animals).

PRECISION pattern = ESCAPE + AUX dominant
Expected kernel signature: high k+e, low h (from BRSC)

This script:
1. Loads the 9 PRECISION candidates
2. Analyzes their kernel content (k, h, e operators)
3. Checks folio distribution
4. Compares against Brunschwig animal recipes
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("PRECISION HANDLING CANDIDATE ANALYSIS")
print("="*70)
print("Expected pattern: ESCAPE+AUX, kernel = high k+e, low h")
print()

# Load match results
with open(results_dir / "pp_brunschwig_match.json") as f:
    match_data = json.load(f)

# Load paragraph tokens
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

# Get PRECISION candidates
precision_candidates = match_data['precision_candidates']
print(f"PRECISION candidates: {len(precision_candidates)}")

# Get paragraph IDs
precision_para_ids = [c['para_id'] for c in precision_candidates]

# Kernel analysis
morph = Morphology()

def analyze_kernels(tokens):
    """Analyze kernel operators in a paragraph's PP tokens."""
    k_count = 0
    h_count = 0
    e_count = 0
    total = 0

    for t in tokens:
        word = t.get('word', '')
        if not word:
            continue
        try:
            m = morph.extract(word)
            middle = m.middle if m.middle else ''
            # Check for kernel operators in MIDDLE
            if 'k' in middle:
                k_count += 1
            if 'h' in middle:
                h_count += 1
            if 'e' in middle:
                e_count += 1
            total += 1
        except:
            pass

    if total == 0:
        return {'k': 0, 'h': 0, 'e': 0, 'total': 0}

    return {
        'k': k_count/total,
        'h': h_count/total,
        'e': e_count/total,
        'total': total,
        'k_raw': k_count,
        'h_raw': h_count,
        'e_raw': e_count
    }

# Analyze each PRECISION candidate
print("\n" + "="*70)
print("KERNEL ANALYSIS FOR PRECISION CANDIDATES")
print("="*70)

detailed_results = []

for cand in precision_candidates:
    para_id = cand['para_id']
    tokens = para_tokens.get(para_id, [])

    if not tokens:
        print(f"\n{para_id}: NO TOKENS FOUND")
        continue

    kernels = analyze_kernels(tokens)

    # Get folio info
    folios = set(t.get('folio', '') for t in tokens if t.get('folio'))
    lines = set(t.get('line', '') for t in tokens if t.get('line'))

    result = {
        'para_id': para_id,
        'initial_ri': cand['initial_ri'],
        'role_profile': cand['role_profile'],
        'match_score': cand['score'],
        'kernels': kernels,
        'folios': list(folios),
        'n_tokens': len(tokens),
        'n_lines': len(lines)
    }
    detailed_results.append(result)

    # Check if kernel pattern matches animal expectation (high k+e, low h)
    k_e_sum = kernels['k'] + kernels['e']
    h_val = kernels['h']
    is_animal_pattern = k_e_sum > h_val * 2  # k+e should dominate h

    print(f"\n{para_id}:")
    print(f"  Initial RI: {cand['initial_ri']}")
    print(f"  Folios: {list(folios)}")
    print(f"  Tokens: {len(tokens)}, Lines: {len(lines)}")
    print(f"  Kernel profile: k={kernels['k']:.2f}, h={kernels['h']:.2f}, e={kernels['e']:.2f}")
    print(f"  k+e={k_e_sum:.2f} vs h={h_val:.2f} -> Animal pattern: {is_animal_pattern}")
    print(f"  Role profile: ESCAPE={cand['role_profile'].get('ESCAPE', 0):.2f}, AUX={cand['role_profile'].get('AUX', 0):.2f}")

# Compare with non-PRECISION paragraphs
print("\n" + "="*70)
print("BASELINE COMPARISON (non-PRECISION paragraphs)")
print("="*70)

# Sample 10 non-PRECISION paragraphs
non_precision = [p for p in para_tokens.keys() if p not in precision_para_ids][:10]

baseline_kernels = []
for para_id in non_precision:
    tokens = para_tokens[para_id]
    if tokens:
        k = analyze_kernels(tokens)
        baseline_kernels.append(k)

if baseline_kernels:
    avg_k = sum(b['k'] for b in baseline_kernels) / len(baseline_kernels)
    avg_h = sum(b['h'] for b in baseline_kernels) / len(baseline_kernels)
    avg_e = sum(b['e'] for b in baseline_kernels) / len(baseline_kernels)
    print(f"Baseline (n={len(baseline_kernels)}): k={avg_k:.2f}, h={avg_h:.2f}, e={avg_e:.2f}")
    print(f"Baseline k+e={avg_k+avg_e:.2f}")

# Precision average
if detailed_results:
    prec_avg_k = sum(d['kernels']['k'] for d in detailed_results) / len(detailed_results)
    prec_avg_h = sum(d['kernels']['h'] for d in detailed_results) / len(detailed_results)
    prec_avg_e = sum(d['kernels']['e'] for d in detailed_results) / len(detailed_results)
    print(f"PRECISION (n={len(detailed_results)}): k={prec_avg_k:.2f}, h={prec_avg_h:.2f}, e={prec_avg_e:.2f}")
    print(f"PRECISION k+e={prec_avg_k+prec_avg_e:.2f}")

# Folio distribution
print("\n" + "="*70)
print("FOLIO DISTRIBUTION OF PRECISION CANDIDATES")
print("="*70)

all_precision_folios = []
for r in detailed_results:
    all_precision_folios.extend(r['folios'])

folio_counts = Counter(all_precision_folios)
print(f"Total folios represented: {len(folio_counts)}")
for folio, count in folio_counts.most_common():
    print(f"  {folio}: {count} paragraphs")

# Cross-reference with Brunschwig animals
print("\n" + "="*70)
print("BRUNSCHWIG ANIMAL MATERIAL COMPARISON")
print("="*70)

# Load Brunschwig data
try:
    with open(Path(__file__).parent.parent.parent.parent / 'data' / 'brunschwig_curated_v3.json') as f:
        brunschwig = json.load(f)

    # Find animal recipes
    animal_recipes = []
    for recipe in brunschwig.get('recipes', []):
        category = recipe.get('category', '').lower()
        if 'animal' in category or any(x in recipe.get('ingredient', '').lower()
                                        for x in ['hen', 'chicken', 'ox', 'goat', 'blood']):
            animal_recipes.append(recipe)

    print(f"Brunschwig animal recipes found: {len(animal_recipes)}")
    for r in animal_recipes[:10]:
        print(f"  - {r.get('ingredient', 'unknown')}: degree {r.get('fire_degree', '?')}")

except FileNotFoundError:
    print("Brunschwig data not found")
except Exception as e:
    print(f"Error loading Brunschwig: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\n{len(detailed_results)} PRECISION paragraphs identified via PP pattern matching")
print("\nCandidate animal RI MIDDLEs:")
all_ri = []
for r in detailed_results:
    all_ri.extend(r['initial_ri'])
print(f"  {all_ri}")

print("\nTop candidates by match score:")
sorted_results = sorted(detailed_results, key=lambda x: -x['match_score'])
for r in sorted_results[:5]:
    ke = r['kernels']['k'] + r['kernels']['e']
    h = r['kernels']['h']
    print(f"  {r['para_id']}: {r['initial_ri']} (score={r['match_score']:.2f}, k+e={ke:.2f}, h={h:.2f})")

# Save detailed results
output = {
    'precision_candidates': detailed_results,
    'all_ri_middles': all_ri,
    'baseline_kernels': {
        'k': avg_k if baseline_kernels else 0,
        'h': avg_h if baseline_kernels else 0,
        'e': avg_e if baseline_kernels else 0
    },
    'precision_kernels': {
        'k': prec_avg_k if detailed_results else 0,
        'h': prec_avg_h if detailed_results else 0,
        'e': prec_avg_e if detailed_results else 0
    }
}

with open(results_dir / "precision_analysis.json", 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to precision_analysis.json")
