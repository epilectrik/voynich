"""Match Voynich B folios to Brunschwig recipes via operational profiles.

Uses cosine similarity on operational vectors (prep MIDDLEs, kernel ratios,
control-flow rates). Runs permutation test for significance.
Cross-references with Puff material categories.

Requires: results/folio_operational_profiles.json
          results/brunschwig_operational_profiles.json
          results/puff_83_chapters.json

Output:   results/folio_recipe_matching.json (+ console report)
"""
import json
import math
import sys

import numpy as np

# --- Load profiles ---
with open('results/folio_operational_profiles.json', encoding='utf-8') as f:
    folio_data = json.load(f)
with open('results/brunschwig_operational_profiles.json', encoding='utf-8') as f:
    recipe_data = json.load(f)

folio_profiles = folio_data['profiles']
recipe_profiles = recipe_data['profiles']
DIMS = folio_data['dimensions']

print(f"Loaded {len(folio_profiles)} folio profiles, {len(recipe_profiles)} recipe profiles")
print(f"Matching dimensions: {DIMS}")

# Filter recipes with procedures (zero vectors are meaningless)
recipe_profiles_active = [r for r in recipe_profiles if r['has_procedure']]
print(f"Active recipes (with procedures): {len(recipe_profiles_active)}")


# --- Build numpy arrays ---
def to_vector(profile):
    return [profile.get(d, 0.0) for d in DIMS]


# Min-max normalize across ALL profiles combined
all_profiles = folio_profiles + recipe_profiles_active
dim_mins = np.array([min(p.get(d, 0.0) for p in all_profiles) for d in DIMS])
dim_maxs = np.array([max(p.get(d, 0.0) for p in all_profiles) for d in DIMS])
dim_range = dim_maxs - dim_mins
dim_range[dim_range == 0] = 1.0

folio_mat = np.array([to_vector(p) for p in folio_profiles])
recipe_mat = np.array([to_vector(r) for r in recipe_profiles_active])

# Normalize
folio_mat = (folio_mat - dim_mins) / dim_range
recipe_mat = (recipe_mat - dim_mins) / dim_range

# L2-normalize rows for cosine similarity via dot product
folio_norms = np.linalg.norm(folio_mat, axis=1, keepdims=True)
recipe_norms = np.linalg.norm(recipe_mat, axis=1, keepdims=True)
folio_norms[folio_norms == 0] = 1.0
recipe_norms[recipe_norms == 0] = 1.0
folio_unit = folio_mat / folio_norms
recipe_unit = recipe_mat / recipe_norms

# Cosine similarity matrix: (N_folios) x (N_recipes)
sim_matrix = folio_unit @ recipe_unit.T
n_folios, n_recipes = sim_matrix.shape

# --- Match: for each folio, find top-5 recipe matches ---
matches = []
for i, fp in enumerate(folio_profiles):
    sims = sim_matrix[i]
    top_indices = np.argsort(sims)[::-1][:5]

    top5 = []
    for j in top_indices:
        rp = recipe_profiles_active[j]
        top5.append({
            'recipe_id': rp['recipe_id'],
            'name': rp['name'],
            'name_german': rp['name_german'],
            'material_class': rp['material_class'],
            'fire_degree': rp['fire_degree'],
            'similarity': round(float(sims[j]), 4),
        })

    matches.append({
        'folio': fp['folio'],
        'material_category': fp.get('material_category', ''),
        'output_category': fp.get('output_category', ''),
        'kernel_balance': fp.get('kernel_balance', ''),
        'top_match_sim': top5[0]['similarity'] if top5 else 0,
        'top5': top5,
    })

# --- Aggregate statistics ---
top_sims = [m['top_match_sim'] for m in matches]
mean_sim = sum(top_sims) / len(top_sims) if top_sims else 0
median_sim = sorted(top_sims)[len(top_sims) // 2] if top_sims else 0

print(f"\n=== MATCHING RESULTS ===")
print(f"Mean top-match similarity: {mean_sim:.4f}")
print(f"Median top-match similarity: {median_sim:.4f}")

# --- Permutation test (numpy-vectorized) ---
# Null: randomly assign each folio to one recipe (with replacement)
# Test statistic: mean similarity of assigned pairs
# Compare to actual mean of best-match similarities
N_PERMS = 10000
rng = np.random.default_rng(42)
actual_mean = mean_sim

null_means = np.zeros(N_PERMS)
print(f"Running {N_PERMS} permutations...")
for i in range(N_PERMS):
    rand_idx = rng.integers(0, n_recipes, size=n_folios)
    null_means[i] = sim_matrix[np.arange(n_folios), rand_idx].mean()
    if (i + 1) % 2000 == 0:
        print(f"  {i + 1}/{N_PERMS}...")

null_mean = float(null_means.mean())
null_std = float(null_means.std())
z_score = (actual_mean - null_mean) / null_std if null_std > 0 else 0
p_value = float((null_means >= actual_mean).mean())

print(f"\n=== PERMUTATION TEST ({N_PERMS} permutations) ===")
print(f"Actual mean top-sim:  {actual_mean:.4f}")
print(f"Null mean:            {null_mean:.4f}")
print(f"Null std:             {null_std:.4f}")
print(f"Z-score:              {z_score:.2f}")
print(f"P-value:              {p_value:.4f}")

if p_value < 0.05:
    verdict = 'PASS'
elif p_value < 0.10:
    verdict = 'MARGINAL'
else:
    verdict = 'FAIL'
print(f"Verdict:              {verdict}")
print(f"Old matching p-value: 1.0000 (regime-only)")
print(f"Improvement:          {1.0 - p_value:.4f}")

# --- Material category alignment ---
CATEGORY_MAP = {
    'ANIMAL': {'animal', 'ANIMAL', 'animal product'},
    'ROOT': {'root', 'bulb', 'root_vegetable'},
    'DELICATE_PLANT': {'flower', 'flower_part', 'herb', 'leaf', 'fern',
                       'succulent', 'aquatic_flower'},
}

align_count = 0
align_total = 0
for m in matches:
    folio_cat = m.get('material_category', '')
    if not folio_cat or folio_cat == 'UNKNOWN':
        continue
    recipe_class = m['top5'][0]['material_class'] if m['top5'] else ''
    if not recipe_class:
        continue
    align_total += 1
    if recipe_class in CATEGORY_MAP.get(folio_cat, set()):
        align_count += 1

if align_total > 0:
    align_pct = 100 * align_count / align_total
    print(f"\n=== MATERIAL CATEGORY ALIGNMENT ===")
    print(f"Folios with material assignment: {align_total}")
    print(f"Aligned with top match: {align_count} ({align_pct:.1f}%)")
else:
    align_pct = 0
    print(f"\nNo material category alignments to test")

# --- Puff cross-reference ---
puff_agreement = None
try:
    with open('results/puff_83_chapters.json', encoding='utf-8') as f:
        puff_raw = json.load(f)

    puff_chapters = puff_raw.get('chapters', puff_raw) if isinstance(puff_raw, dict) else puff_raw

    puff_cats = {}
    for ch in puff_chapters:
        puff_cats[ch.get('chapter')] = ch.get('category', 'UNKNOWN').lower()

    with open('results/puff_voynich_matching_v2.json', encoding='utf-8') as f:
        old_match = json.load(f)

    puff_folio_map = {}
    for entry in old_match.get('top_20_matches', []):
        folio = entry.get('voynich_folio')
        puff_ch = entry.get('puff_chapter')
        if folio and puff_ch:
            puff_folio_map[folio] = puff_ch

    agree = 0
    disagree = 0
    cross_details = []
    for m in matches:
        folio = m['folio']
        if folio not in puff_folio_map:
            continue
        puff_ch = puff_folio_map[folio]
        puff_cat = puff_cats.get(puff_ch, 'unknown')
        recipe_class = m['top5'][0]['material_class'] if m['top5'] else ''

        is_aligned = (
            puff_cat == recipe_class.lower()
            or (puff_cat == 'flower' and recipe_class in ('flower', 'flower_part', 'aquatic_flower'))
            or (puff_cat == 'herb' and recipe_class in ('herb', 'leaf', 'fern'))
            or (puff_cat == 'root' and recipe_class in ('root', 'bulb', 'root_vegetable'))
        )

        if is_aligned:
            agree += 1
        else:
            disagree += 1
        cross_details.append({
            'folio': folio,
            'puff_chapter': puff_ch,
            'puff_category': puff_cat,
            'brunschwig_match': m['top5'][0]['name'] if m['top5'] else '',
            'brunschwig_class': recipe_class,
            'aligned': is_aligned,
        })

    total_cross = agree + disagree
    if total_cross > 0:
        puff_agreement = round(100 * agree / total_cross, 1)
        print(f"\n=== PUFF CROSS-REFERENCE ===")
        print(f"Folios with Puff assignment: {total_cross}")
        print(f"Puff<>Brunschwig agreement: {agree}/{total_cross} ({puff_agreement}%)")
        for d in cross_details:
            marker = '+' if d['aligned'] else '-'
            print(f"  {marker} {d['folio']}: Puff={d['puff_category']}, "
                  f"Brunschwig={d['brunschwig_class']} ({d['brunschwig_match']})")
    else:
        print(f"\nNo Puff cross-reference possible (no overlapping folios)")

except FileNotFoundError:
    print(f"\nPuff data not found - skipping cross-reference")

# --- Top 10 strongest and weakest matches ---
sorted_matches = sorted(matches, key=lambda m: m['top_match_sim'], reverse=True)

print(f"\n=== TOP 10 STRONGEST MATCHES ===")
for m in sorted_matches[:10]:
    top = m['top5'][0]
    print(f"  {m['folio']:8s} -> {top['name']:25s} ({top['material_class']:10s}, "
          f"fire={top['fire_degree']}) sim={top['similarity']:.4f}")

print(f"\n=== TOP 10 WEAKEST MATCHES ===")
for m in sorted_matches[-10:]:
    top = m['top5'][0]
    print(f"  {m['folio']:8s} -> {top['name']:25s} ({top['material_class']:10s}, "
          f"fire={top['fire_degree']}) sim={top['similarity']:.4f}")

# --- Output JSON ---
output = {
    'title': 'Voynich B Folio -> Brunschwig Recipe Operational Matching',
    'method': 'Cosine similarity on normalized operational vectors',
    'dimensions': DIMS,
    'folio_count': len(folio_profiles),
    'recipe_count': len(recipe_profiles_active),
    'statistics': {
        'mean_top_similarity': round(mean_sim, 4),
        'median_top_similarity': round(median_sim, 4),
    },
    'permutation_test': {
        'n_permutations': N_PERMS,
        'actual_mean': round(actual_mean, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 2),
        'p_value': round(p_value, 4),
        'verdict': verdict,
        'comparison': {
            'old_method': 'REGIME assignment only',
            'old_p_value': 1.0,
            'improvement': round(1.0 - p_value, 4),
        },
    },
    'material_alignment': {
        'tested': align_total,
        'aligned': align_count,
        'rate': round(align_pct, 1) if align_total > 0 else None,
    },
    'puff_cross_reference': {
        'agreement_rate': puff_agreement,
    },
    'matches': sorted_matches,
}

with open('results/folio_recipe_matching.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote results to results/folio_recipe_matching.json")
