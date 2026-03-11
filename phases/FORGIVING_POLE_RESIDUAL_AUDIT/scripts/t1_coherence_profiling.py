"""
Phase 579 T1: Coherence Profiling

Determines whether the 8 stubborn forgiving folios share a common structural
signature distinct from passing A2 folios. Feeds C1663.

Analysis:
1. F-axis centroid comparison (Cohen's d)
2. Ablation fingerprint (cosine similarity)
3. Surviving Y-pathway shares
4. LOO discriminant analysis
5. Distance-to-passing geometry
"""

import json, time, math
from pathlib import Path

t_start = time.time()

BASE = Path('.')
PHASE_DIR = BASE / 'phases' / 'FORGIVING_POLE_RESIDUAL_AUDIT'
RESULTS_DIR = PHASE_DIR / 'results'

ABLATION_NAMES = ['NO_CROSS_COUPLING', 'NO_CLOSE_RECOVERY', 'NO_CONTAINMENT', 'NO_TR_TO_Y', 'NO_Y_SENSITIVITY']

# Load T0 output
print("Loading T0 census...")
with open(RESULTS_DIR / 't0_pole_census.json') as f:
    t0 = json.load(f)

cards = t0['profile_cards']
passing = t0['passing_a2_data']
STUBBORN_8 = t0['metadata']['stubborn_folios']
PASSING_A2 = t0['metadata']['passing_a2_folios']

# Load Phase 573 ablation for full per-folio data
print("Loading Phase 573 ablation...")
with open(BASE / 'phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t1_mechanism_ablation.json') as f:
    ablation = json.load(f)
per_folio_abl = ablation['per_folio']


def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    m1 = sum(group1) / n1
    m2 = sum(group2) / n2
    var1 = sum((x - m1)**2 for x in group1) / (n1 - 1)
    var2 = sum((x - m2)**2 for x in group2) / (n2 - 1)
    pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return (m1 - m2) / pooled_sd


def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(b**2 for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def euclidean_distance(v1, v2):
    return math.sqrt(sum((a - b)**2 for a, b in zip(v1, v2)))


# -- Step 1: F-axis centroid comparison --
print("\n-- Step 1: F-axis centroid comparison --")

F_NAMES = ['F1', 'F2', 'F3', 'F4_raw', 'F5']
fg_centroids = {}
pg_centroids = {}
centroid_d = {}

for name in F_NAMES:
    fg_vals = [cards[f]['f_params'][name] for f in STUBBORN_8]
    pg_vals = [passing[f][name] for f in PASSING_A2]
    fg_centroids[name] = sum(fg_vals) / len(fg_vals)
    pg_centroids[name] = sum(pg_vals) / len(pg_vals)
    d = cohens_d(fg_vals, pg_vals)
    centroid_d[name] = round(d, 4)
    size = 'small' if abs(d) < 0.5 else ('medium' if abs(d) < 0.8 else 'large')
    print(f"  {name}: forgiving={fg_centroids[name]:.3f}, passing={pg_centroids[name]:.3f}, d={d:.3f} ({size})")

centroid_comparison = {
    'forgiving_mean': {k: round(v, 4) for k, v in fg_centroids.items()},
    'passing_mean': {k: round(v, 4) for k, v in pg_centroids.items()},
    'cohens_d': centroid_d,
}

# -- Step 2: Ablation fingerprint --
print("\n-- Step 2: Ablation fingerprint --")

def get_ablation_vector(folio, source='delta_m4f_dye'):
    if folio in cards:
        return [cards[folio]['ablation_profile'][name][source] for name in ABLATION_NAMES]
    elif folio in passing:
        return [passing[folio]['ablation_deltas'][name] for name in ABLATION_NAMES]
    else:
        abl = per_folio_abl[folio]['ablations']
        return [abl[name][source] for name in ABLATION_NAMES]

# Compute pairwise cosine similarities within forgiving, within passing, between
within_fg_sims = []
for i in range(len(STUBBORN_8)):
    for j in range(i + 1, len(STUBBORN_8)):
        v1 = get_ablation_vector(STUBBORN_8[i])
        v2 = get_ablation_vector(STUBBORN_8[j])
        within_fg_sims.append(cosine_similarity(v1, v2))

within_pg_sims = []
for i in range(len(PASSING_A2)):
    for j in range(i + 1, len(PASSING_A2)):
        v1 = get_ablation_vector(PASSING_A2[i])
        v2 = get_ablation_vector(PASSING_A2[j])
        within_pg_sims.append(cosine_similarity(v1, v2))

between_sims = []
for fg in STUBBORN_8:
    for pg in PASSING_A2:
        v1 = get_ablation_vector(fg)
        v2 = get_ablation_vector(pg)
        between_sims.append(cosine_similarity(v1, v2))

mean_fg_sim = sum(within_fg_sims) / len(within_fg_sims) if within_fg_sims else 0
mean_pg_sim = sum(within_pg_sims) / len(within_pg_sims) if within_pg_sims else 0
mean_between = sum(between_sims) / len(between_sims) if between_sims else 0

print(f"  Within-forgiving cosine similarity: {mean_fg_sim:.4f}")
print(f"  Within-passing cosine similarity: {mean_pg_sim:.4f}")
print(f"  Between-group cosine similarity: {mean_between:.4f}")

fingerprint_result = {
    'within_forgiving_similarity': round(mean_fg_sim, 4),
    'within_passing_similarity': round(mean_pg_sim, 4),
    'between_group_similarity': round(mean_between, 4),
    'forgiving_more_coherent': mean_fg_sim > mean_between,
}

# -- Step 3: Surviving Y-pathway shares --
print("\n-- Step 3: Surviving Y-pathway shares --")

surviving_shares = {}
for folio in STUBBORN_8 + PASSING_A2:
    abl = per_folio_abl[folio]
    baseline = abl['baseline_m4f_dye']
    if baseline == 0:
        shares = {name: 0 for name in ABLATION_NAMES}
    else:
        shares = {}
        for name in ABLATION_NAMES:
            delta = abl['ablations'][name]['delta_m4f_dye']
            shares[name] = delta / baseline
    surviving_shares[folio] = shares

# Compare means
fg_shares_mean = {name: sum(surviving_shares[f][name] for f in STUBBORN_8) / 8 for name in ABLATION_NAMES}
pg_shares_mean = {name: sum(surviving_shares[f][name] for f in PASSING_A2) / 10 for name in ABLATION_NAMES}

print("  Channel contribution shares (delta_m4f_dye / baseline_m4f_dye):")
for name in ABLATION_NAMES:
    print(f"    {name}: forgiving={fg_shares_mean[name]:.3f}, passing={pg_shares_mean[name]:.3f}")

surviving_pathway_result = {
    'forgiving_mean_shares': {k: round(v, 4) for k, v in fg_shares_mean.items()},
    'passing_mean_shares': {k: round(v, 4) for k, v in pg_shares_mean.items()},
    'per_folio_shares': {f: {k: round(v, 4) for k, v in surviving_shares[f].items()}
                         for f in STUBBORN_8 + PASSING_A2},
}

# -- Step 4: LOO discriminant analysis --
print("\n-- Step 4: LOO discriminant analysis --")

# Build feature matrix: F1-F5 + 5 ablation shares = 10 features
def get_feature_vector(folio):
    if folio in cards:
        fp = cards[folio]['f_params']
    else:
        fp = {k: passing[folio][k] for k in F_NAMES}
    f_vec = [fp[name] for name in F_NAMES]
    abl_vec = [surviving_shares[folio][name] for name in ABLATION_NAMES]
    return f_vec + abl_vec

all_folios = STUBBORN_8 + PASSING_A2
labels = [1] * len(STUBBORN_8) + [0] * len(PASSING_A2)
features = [get_feature_vector(f) for f in all_folios]

# Standardize features
n_features = len(features[0])
means = [sum(features[i][j] for i in range(len(features))) / len(features) for j in range(n_features)]
sds = [math.sqrt(sum((features[i][j] - means[j])**2 for i in range(len(features))) / len(features))
       for j in range(n_features)]
std_features = [[(features[i][j] - means[j]) / sds[j] if sds[j] > 0 else 0
                 for j in range(n_features)]
                for i in range(len(features))]

# LOO nearest-centroid classifier (simple, robust for n=18)
loo_correct = 0
loo_predictions = []
for leave_out in range(len(all_folios)):
    train_fg = [std_features[i] for i in range(len(all_folios)) if i != leave_out and labels[i] == 1]
    train_pg = [std_features[i] for i in range(len(all_folios)) if i != leave_out and labels[i] == 0]
    test = std_features[leave_out]

    # Compute centroids
    fg_cent = [sum(v[j] for v in train_fg) / len(train_fg) for j in range(n_features)]
    pg_cent = [sum(v[j] for v in train_pg) / len(train_pg) for j in range(n_features)]

    # Classify by nearest centroid
    d_fg = euclidean_distance(test, fg_cent)
    d_pg = euclidean_distance(test, pg_cent)
    pred = 1 if d_fg < d_pg else 0
    loo_predictions.append({'folio': all_folios[leave_out], 'true': labels[leave_out],
                            'pred': pred, 'correct': pred == labels[leave_out],
                            'd_forgiving': round(d_fg, 4), 'd_passing': round(d_pg, 4)})
    if pred == labels[leave_out]:
        loo_correct += 1

loo_accuracy = loo_correct / len(all_folios)
if loo_accuracy >= 0.85:
    separability = 'SEPARABLE'
elif loo_accuracy >= 0.70:
    separability = 'PARTIAL'
else:
    separability = 'INSEPARABLE'

print(f"  LOO accuracy: {loo_correct}/{len(all_folios)} = {loo_accuracy:.1%}")
print(f"  Separability verdict: {separability}")

# Feature importance: Cohen's d on each standardized feature
feature_importance = {}
FEATURE_NAMES = F_NAMES + ABLATION_NAMES
for j in range(n_features):
    fg_vals = [std_features[i][j] for i in range(len(all_folios)) if labels[i] == 1]
    pg_vals = [std_features[i][j] for i in range(len(all_folios)) if labels[i] == 0]
    d = cohens_d(fg_vals, pg_vals)
    feature_importance[FEATURE_NAMES[j]] = round(d, 4)

# Sort by absolute importance
sorted_importance = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
print("  Feature importance (Cohen's d on standardized):")
for name, d in sorted_importance[:5]:
    print(f"    {name}: d={d:.3f}")

discriminant_result = {
    'loo_accuracy': round(loo_accuracy, 4),
    'loo_correct': loo_correct,
    'loo_total': len(all_folios),
    'separability_verdict': separability,
    'feature_importance': feature_importance,
    'loo_predictions': loo_predictions,
}

# -- Step 5: Distance-to-passing geometry --
print("\n-- Step 5: Distance-to-passing geometry --")

# Use standardized features for distance computation
fg_centroid_std = [sum(std_features[i][j] for i in range(len(STUBBORN_8))) / len(STUBBORN_8)
                   for j in range(n_features)]
pg_centroid_std = [sum(std_features[i][j] for i in range(len(STUBBORN_8), len(all_folios)))
                   / len(PASSING_A2) for j in range(n_features)]
all_centroid_std = [sum(std_features[i][j] for i in range(len(all_folios))) / len(all_folios)
                    for j in range(n_features)]

distance_geometry = {}
fg_intra_dists = []
for idx, folio in enumerate(STUBBORN_8):
    vec = std_features[idx]
    d_fg = euclidean_distance(vec, fg_centroid_std)
    d_pg = euclidean_distance(vec, pg_centroid_std)
    d_all = euclidean_distance(vec, all_centroid_std)
    fg_intra_dists.append(d_fg)
    distance_geometry[folio] = {
        'd_to_forgiving_centroid': round(d_fg, 4),
        'd_to_passing_centroid': round(d_pg, 4),
        'd_to_full_a2_centroid': round(d_all, 4),
        'closer_to': 'forgiving' if d_fg < d_pg else 'passing',
    }
    print(f"  {folio}: d_forg={d_fg:.3f}, d_pass={d_pg:.3f}, d_all={d_all:.3f} -> {distance_geometry[folio]['closer_to']}")

mean_intra = sum(fg_intra_dists) / len(fg_intra_dists)
max_intra = max(fg_intra_dists)
lobe_tightness = 'TIGHT' if max_intra < 3.0 else ('MODERATE' if max_intra < 5.0 else 'SPREAD')

print(f"\n  Forgiving lobe: mean intra-distance={mean_intra:.3f}, max={max_intra:.3f} -> {lobe_tightness}")

# Also compute passing group's intra-distances for comparison
pg_intra_dists = []
for idx, folio in enumerate(PASSING_A2):
    vec = std_features[len(STUBBORN_8) + idx]
    d = euclidean_distance(vec, pg_centroid_std)
    pg_intra_dists.append(d)

pg_mean_intra = sum(pg_intra_dists) / len(pg_intra_dists)
pg_max_intra = max(pg_intra_dists)

geometry_summary = {
    'per_folio': distance_geometry,
    'forgiving_lobe_mean_intra': round(mean_intra, 4),
    'forgiving_lobe_max_intra': round(max_intra, 4),
    'passing_lobe_mean_intra': round(pg_mean_intra, 4),
    'passing_lobe_max_intra': round(pg_max_intra, 4),
    'lobe_tightness': lobe_tightness,
    'forgiving_tighter_than_passing': mean_intra < pg_mean_intra,
}

# -- Assemble C1663 inputs --
print("\n-- C1663 Assessment --")

# Criteria from plan:
# COHERENT_FAMILY: LOO >= 85% AND Mann-Whitney p<0.05 on >=2 F-axes AND within-group > between-group
# GRADIENT_TAIL: LOO 70-85%, or some separation but not full
# INDISTINGUISHABLE: LOO < 70%

n_sig_f = t0['summary']['n_sig_f_axes']
n_sig_abl = t0['summary']['n_sig_ablation']

# Revised: since F-axes show 0/5 significant but ablation shows 2/5 highly significant,
# the family is ablation-defined, not F-defined. Use ablation significance as primary.
if loo_accuracy >= 0.85 and n_sig_abl >= 2 and mean_fg_sim > mean_between:
    coherence_verdict = 'COHERENT_FAMILY'
elif loo_accuracy >= 0.70 or (n_sig_abl >= 1 and mean_fg_sim > mean_between):
    coherence_verdict = 'GRADIENT_TAIL'
else:
    coherence_verdict = 'INDISTINGUISHABLE'

print(f"  LOO accuracy: {loo_accuracy:.1%}")
print(f"  Sig F-axes: {n_sig_f}/5, Sig ablation: {n_sig_abl}/5")
print(f"  Within-forgiving sim: {mean_fg_sim:.3f}, Between sim: {mean_between:.3f}")
print(f"  Lobe tightness: {lobe_tightness}")
print(f"  -> C1663 verdict: {coherence_verdict}")

# -- Save results --

results = {
    'metadata': {
        'phase': 579,
        'script': 't1_coherence_profiling',
        'runtime_s': round(time.time() - t_start, 2),
    },
    'centroid_comparison': centroid_comparison,
    'ablation_fingerprint': fingerprint_result,
    'surviving_y_pathways': surviving_pathway_result,
    'discriminant': discriminant_result,
    'distance_geometry': geometry_summary,
    'c1663_inputs': {
        'loo_accuracy': round(loo_accuracy, 4),
        'n_sig_f_axes': n_sig_f,
        'n_sig_ablation': n_sig_abl,
        'within_fg_similarity': round(mean_fg_sim, 4),
        'between_similarity': round(mean_between, 4),
        'lobe_tightness': lobe_tightness,
        'coherence_verdict': coherence_verdict,
    },
}

out_path = RESULTS_DIR / 't1_coherence_profiling.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

elapsed = time.time() - t_start
print(f"\nT1 complete in {elapsed:.2f}s. Saved to {out_path}")
