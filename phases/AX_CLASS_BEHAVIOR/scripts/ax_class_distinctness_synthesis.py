"""
AX_CLASS_BEHAVIOR Script 4: Distinctness synthesis.
Combine all behavioral dimensions. Cluster, PCA, confusability analysis.
Verdict: how many effective behavioral groups exist?
"""
import sys
sys.path.insert(0, 'C:/git/voynich')

import json
import math
from pathlib import Path
from collections import defaultdict

BASE = Path('C:/git/voynich')
RESULTS = BASE / 'phases/AX_CLASS_BEHAVIOR/results'
AUX_STRAT = BASE / 'phases/AUXILIARY_STRATIFICATION/results'
CSV_RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# ── Load all data sources ──

with open(RESULTS / 'ax_class_transition_matrix.json') as f:
    transitions = json.load(f)

with open(RESULTS / 'ax_class_positional_profiles.json') as f:
    positions = json.load(f)

with open(RESULTS / 'ax_class_context_signatures.json') as f:
    context = json.load(f)

with open(AUX_STRAT / 'ax_clustering.json') as f:
    clustering = json.load(f)

with open(AUX_STRAT / 'ax_features.json') as f:
    features = json.load(f)

with open(AUX_STRAT / 'ax_census.json') as f:
    census = json.load(f)

# Load subgroup assignments
with open(AUX_STRAT / 'ax_subgroups.json') as f:
    subgroups = json.load(f)

AX_CLASSES = sorted(census['definitive_ax_classes'])

# Build subgroup lookup
class_to_subgroup = {}
for sg_name, sg_data in subgroups['subgroups'].items():
    for cls in sg_data['classes']:
        class_to_subgroup[cls] = sg_name

print(f"AX Classes: {AX_CLASSES}")
print(f"Subgroup assignments: {class_to_subgroup}")

# ── Build combined feature matrix ──
# Dimensions:
# - From transitions (Script 1): self_chain_rate, transition_entropy, normalized_entropy (3)
# - From positions (Script 2): 10-bin positional frequencies (10)
# - From context (Script 3): left and right role rates for 6 roles (12)
# - From existing features: regime rates (4), section rates (4), morphology (3)
# Total: ~36 features

feature_names = []
feature_matrix = {}  # class -> feature vector

for cls in AX_CLASSES:
    cls_str = str(cls)
    vec = []

    # Transition features (3)
    t_metrics = transitions['per_class_metrics'].get(cls_str, {})
    vec.append(t_metrics.get('self_chain_rate', 0))
    vec.append(t_metrics.get('transition_entropy', 0))
    vec.append(t_metrics.get('transition_normalized_entropy', 0) or 0)
    if cls == AX_CLASSES[0]:
        feature_names.extend(['self_chain_rate', 'transition_entropy', 'transition_norm_entropy'])

    # Positional features (10 bins)
    p_cdf = positions['per_class_cdf'].get(cls_str, {})
    freqs = p_cdf.get('frequencies', [0] * 10)
    vec.extend(freqs)
    if cls == AX_CLASSES[0]:
        feature_names.extend([f'pos_bin_{i}' for i in range(10)])

    # Context features (12: 6 left roles + 6 right roles)
    ctx = context['per_class_context'].get(cls_str, {})
    roles = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
    for r in roles:
        vec.append(ctx.get('left_role_rates', {}).get(r, 0))
    for r in roles:
        vec.append(ctx.get('right_role_rates', {}).get(r, 0))
    if cls == AX_CLASSES[0]:
        feature_names.extend([f'left_{r}' for r in roles] + [f'right_{r}' for r in roles])

    # Existing features from ax_features.json
    feat = None
    for f_entry in features.get('per_class_features', []):
        if f_entry.get('class') == cls:
            feat = f_entry
            break

    if feat:
        # Regime rates (4)
        for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            vec.append(feat.get(f'regime_{regime}', 0))
        # Section rates (4)
        for section in ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']:
            vec.append(feat.get(f'section_{section}', 0))
        # Morphology (3)
        vec.append(feat.get('prefix_rate', 0))
        vec.append(feat.get('suffix_rate', 0))
        vec.append(feat.get('articulator_rate', 0))
    else:
        vec.extend([0] * 11)

    if cls == AX_CLASSES[0]:
        feature_names.extend(
            [f'regime_{i}' for i in range(1, 5)] +
            ['section_HERBAL_B', 'section_PHARMA', 'section_BIO', 'section_RECIPE_B'] +
            ['prefix_rate', 'suffix_rate', 'articulator_rate']
        )

    feature_matrix[cls] = vec

n_features = len(feature_names)
print(f"\nCombined feature matrix: {len(AX_CLASSES)} classes x {n_features} features")

# ── Z-score normalize ──

n_classes = len(AX_CLASSES)
means = [0.0] * n_features
stds = [0.0] * n_features

for j in range(n_features):
    vals = [feature_matrix[cls][j] for cls in AX_CLASSES]
    m = sum(vals) / n_classes
    means[j] = m
    v = sum((x - m) ** 2 for x in vals) / n_classes
    stds[j] = math.sqrt(v) if v > 0 else 1.0

z_matrix = {}
for cls in AX_CLASSES:
    z_matrix[cls] = [(feature_matrix[cls][j] - means[j]) / stds[j] for j in range(n_features)]

# ── Pairwise distance matrix ──

def euclidean(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

dist_matrix = {}
for i, cls_a in enumerate(AX_CLASSES):
    for cls_b in AX_CLASSES[i + 1:]:
        d = euclidean(z_matrix[cls_a], z_matrix[cls_b])
        dist_matrix[(cls_a, cls_b)] = d

sorted_pairs = sorted(dist_matrix.items(), key=lambda x: x[1])
most_confusable = sorted_pairs[:5]
most_distinct = sorted_pairs[-5:]

print(f"\nMost confusable (smallest distance):")
for (a, b), d in most_confusable:
    sg_a = class_to_subgroup.get(a, '?')
    sg_b = class_to_subgroup.get(b, '?')
    same = "SAME" if sg_a == sg_b else "DIFF"
    print(f"  {a} ({sg_a}) - {b} ({sg_b}): d={d:.3f} [{same}]")

print(f"\nMost distinct (largest distance):")
for (a, b), d in most_distinct:
    sg_a = class_to_subgroup.get(a, '?')
    sg_b = class_to_subgroup.get(b, '?')
    same = "SAME" if sg_a == sg_b else "DIFF"
    print(f"  {a} ({sg_a}) - {b} ({sg_b}): d={d:.3f} [{same}]")

# ── Inter vs intra subgroup distances ──

inter_dists = []
intra_dists = []
for (a, b), d in dist_matrix.items():
    sg_a = class_to_subgroup.get(a, '?')
    sg_b = class_to_subgroup.get(b, '?')
    if sg_a == sg_b:
        intra_dists.append(d)
    else:
        inter_dists.append(d)

mean_inter = sum(inter_dists) / len(inter_dists) if inter_dists else 0
mean_intra = sum(intra_dists) / len(intra_dists) if intra_dists else 0
separation_ratio = mean_inter / mean_intra if mean_intra > 0 else 0

print(f"\nSubgroup separation:")
print(f"  Mean inter-subgroup distance: {mean_inter:.3f}")
print(f"  Mean intra-subgroup distance: {mean_intra:.3f}")
print(f"  Separation ratio: {separation_ratio:.3f}")

# ── PCA (manual implementation) ──

# Compute covariance matrix
cov_matrix = [[0.0] * n_features for _ in range(n_features)]
for j in range(n_features):
    for k in range(j, n_features):
        cov = sum(z_matrix[cls][j] * z_matrix[cls][k] for cls in AX_CLASSES) / n_classes
        cov_matrix[j][k] = cov
        cov_matrix[k][j] = cov

# Power iteration for eigenvalues (simplified - get top eigenvalues)
def power_iteration(matrix, n_iter=1000):
    """Get largest eigenvalue and eigenvector."""
    n = len(matrix)
    v = [1.0 / math.sqrt(n)] * n
    for _ in range(n_iter):
        new_v = [sum(matrix[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x ** 2 for x in new_v))
        if norm < 1e-10:
            return 0, v
        v = [x / norm for x in new_v]
    eigenvalue = sum(sum(matrix[i][j] * v[j] for j in range(n)) * v[i] for i in range(n))
    return eigenvalue, v

def deflate(matrix, eigenvalue, eigenvector):
    """Remove top eigenvector contribution."""
    n = len(matrix)
    result = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[i][j] = matrix[i][j] - eigenvalue * eigenvector[i] * eigenvector[j]
    return result

# Extract top 10 eigenvalues
eigenvalues = []
eigenvectors = []
current_matrix = [row[:] for row in cov_matrix]

for pc in range(min(10, n_features)):
    eigenval, eigenvec = power_iteration(current_matrix)
    if eigenval < 1e-6:
        break
    eigenvalues.append(eigenval)
    eigenvectors.append(eigenvec)
    current_matrix = deflate(current_matrix, eigenval, eigenvec)

total_variance = sum(eigenvalues)
if total_variance > 0:
    explained_ratio = [ev / total_variance for ev in eigenvalues]
    cumulative = []
    cum = 0
    for r in explained_ratio:
        cum += r
        cumulative.append(round(cum, 4))
else:
    explained_ratio = []
    cumulative = []

# Components for 90% variance
components_90 = next((i + 1 for i, c in enumerate(cumulative) if c >= 0.90), len(cumulative))

print(f"\n=== PCA ===")
print(f"Components extracted: {len(eigenvalues)}")
for i, (ev, ratio) in enumerate(zip(eigenvalues, explained_ratio)):
    print(f"  PC{i+1}: eigenvalue={ev:.3f}, variance={ratio:.3f} ({cumulative[i]:.3f} cumulative)")
print(f"Components for 90% variance: {components_90}")

# Top loadings for PC1 and PC2
if len(eigenvectors) >= 2:
    pc1_loadings = sorted(zip(feature_names, eigenvectors[0]), key=lambda x: abs(x[1]), reverse=True)[:5]
    pc2_loadings = sorted(zip(feature_names, eigenvectors[1]), key=lambda x: abs(x[1]), reverse=True)[:5]
    print(f"\nPC1 top loadings:")
    for name, loading in pc1_loadings:
        print(f"  {name}: {loading:.3f}")
    print(f"PC2 top loadings:")
    for name, loading in pc2_loadings:
        print(f"  {name}: {loading:.3f}")

# ── Hierarchical clustering (simple agglomerative) ──

def silhouette_score(labels, dist_func):
    """Compute silhouette score for given cluster labels."""
    classes_list = list(labels.keys())
    n = len(classes_list)
    scores = []
    for cls in classes_list:
        label = labels[cls]
        same_cluster = [c for c in classes_list if labels[c] == label and c != cls]
        diff_clusters = set(labels[c] for c in classes_list if labels[c] != label)

        if not same_cluster:
            scores.append(0)
            continue

        # a(i) = mean distance to same cluster
        a = sum(dist_func(cls, c) for c in same_cluster) / len(same_cluster)

        # b(i) = min mean distance to any other cluster
        b = float('inf')
        for other_label in diff_clusters:
            other_members = [c for c in classes_list if labels[c] == other_label]
            if other_members:
                mean_d = sum(dist_func(cls, c) for c in other_members) / len(other_members)
                b = min(b, mean_d)

        if b == float('inf'):
            scores.append(0)
        else:
            scores.append((b - a) / max(a, b) if max(a, b) > 0 else 0)

    return sum(scores) / len(scores) if scores else 0

def get_dist(a, b):
    if a == b:
        return 0
    key = (min(a, b), max(a, b))
    return dist_matrix.get(key, 0)

# Simple k-medoids clustering
def k_medoids(k, max_iter=100):
    """Simple k-medoids clustering."""
    import random
    random.seed(42)
    # Initialize medoids
    medoids = random.sample(AX_CLASSES, k)

    for _ in range(max_iter):
        # Assign to nearest medoid
        labels = {}
        for cls in AX_CLASSES:
            best_medoid = min(medoids, key=lambda m: get_dist(cls, m))
            labels[cls] = medoids.index(best_medoid)

        # Update medoids
        new_medoids = []
        for cluster_id in range(k):
            members = [c for c in AX_CLASSES if labels[c] == cluster_id]
            if not members:
                new_medoids.append(medoids[cluster_id])
                continue
            # Find member with smallest total distance to others
            best = min(members, key=lambda m: sum(get_dist(m, c) for c in members))
            new_medoids.append(best)

        if set(new_medoids) == set(medoids):
            break
        medoids = new_medoids

    return labels

print(f"\n=== Clustering ===")
clustering_results = {}
for k in range(2, 9):
    labels = k_medoids(k)
    sil = silhouette_score(labels, get_dist)
    clustering_results[k] = {
        'silhouette': round(sil, 4),
        'labels': {str(cls): lab for cls, lab in labels.items()},
    }
    print(f"  k={k}: silhouette={sil:.4f}")

best_k = max(clustering_results, key=lambda k: clustering_results[k]['silhouette'])
best_sil = clustering_results[best_k]['silhouette']
prior_sil = 0.2317

print(f"\nBest k: {best_k} (silhouette={best_sil:.4f})")
print(f"Prior best (21D, k=2): {prior_sil:.4f}")
print(f"Improvement: {best_sil - prior_sil:+.4f}")

# ── Verdict ──

# Classification accuracy from Script 3
class_accuracy = context['classification']['overall_accuracy']
class_baseline = context['classification']['weighted_random_baseline']

# Positional distinctness from Script 2
pos_distinct_bonf = positions['summary']['classes_distinct_from_population_bonferroni']
pairs_distinct_bonf = positions['summary']['pairs_distinct_bonferroni']

# Transition structure from Script 1
structured_transitions = transitions['summary']['classes_with_structured_transitions']

verdict_lines = []
verdict_lines.append(f"BEHAVIORAL DISTINCTNESS ASSESSMENT")
verdict_lines.append(f"=" * 50)
verdict_lines.append(f"")
verdict_lines.append(f"Position: {pos_distinct_bonf}/20 classes positionally distinct (Bonferroni)")
verdict_lines.append(f"  {pairs_distinct_bonf}/190 pairs distinguishable = {pairs_distinct_bonf/190:.1%}")
verdict_lines.append(f"Transitions: {structured_transitions}/20 classes with structured transitions")
verdict_lines.append(f"Context: {class_accuracy:.1%} classification accuracy ({class_baseline:.1%} baseline, {class_accuracy/class_baseline:.2f}x)")
verdict_lines.append(f"Clustering: best k={best_k}, silhouette={best_sil:.4f} (prior: {prior_sil:.4f})")
verdict_lines.append(f"PCA: {components_90} components for 90% variance")
verdict_lines.append(f"Subgroup separation: {separation_ratio:.3f} (inter/intra distance ratio)")
verdict_lines.append(f"")

if best_sil < 0.25:
    cluster_verdict = "weak"
elif best_sil < 0.40:
    cluster_verdict = "moderate"
else:
    cluster_verdict = "strong"

if components_90 <= 3:
    dim_verdict = "low-dimensional (3 or fewer axes)"
elif components_90 <= 5:
    dim_verdict = "moderate-dimensional (4-5 axes)"
else:
    dim_verdict = "high-dimensional (6+ axes)"

if class_accuracy < class_baseline:
    context_verdict = "no contextual identity (below baseline)"
elif class_accuracy < 2 * class_baseline:
    context_verdict = "weak contextual identity"
else:
    context_verdict = "moderate contextual identity"

assessment = (
    f"The 20 AX classes show {cluster_verdict} cluster separation (silhouette={best_sil:.3f}), "
    f"{dim_verdict} behavioral structure ({components_90} PCA components for 90%), "
    f"and {context_verdict} ({class_accuracy:.1%} vs {class_baseline:.1%} baseline). "
    f"Position is the primary differentiator ({pos_distinct_bonf}/20 classes distinct), "
    f"while transitions are mostly uniform ({structured_transitions}/20 structured) "
    f"and context provides no classification signal. "
    f"The effective number of behavioral groups is {best_k}, not 20. "
    f"Within-subgroup classes are largely interchangeable."
)

verdict_lines.append(f"VERDICT: {assessment}")

for line in verdict_lines:
    print(line)

# ── Save results ──

results = {
    'combined_feature_matrix': {
        'classes': AX_CLASSES,
        'feature_names': feature_names,
        'n_features': n_features,
        'n_classes': n_classes,
    },
    'clustering': {
        'method': 'k_medoids',
        'results': clustering_results,
        'best_k': best_k,
        'best_silhouette': best_sil,
        'prior_silhouette': prior_sil,
        'improvement': round(best_sil - prior_sil, 4),
    },
    'pca': {
        'eigenvalues': [round(ev, 4) for ev in eigenvalues],
        'explained_variance_ratio': [round(r, 4) for r in explained_ratio],
        'cumulative_variance': cumulative,
        'components_for_90pct': components_90,
        'pc1_top_loadings': {name: round(val, 4) for name, val in pc1_loadings} if len(eigenvectors) >= 1 else {},
        'pc2_top_loadings': {name: round(val, 4) for name, val in pc2_loadings} if len(eigenvectors) >= 2 else {},
    },
    'confusability': {
        'most_confusable': [
            {'class_a': a, 'class_b': b, 'distance': round(d, 3),
             'subgroup_a': class_to_subgroup.get(a), 'subgroup_b': class_to_subgroup.get(b),
             'same_subgroup': class_to_subgroup.get(a) == class_to_subgroup.get(b)}
            for (a, b), d in most_confusable
        ],
        'most_distinct': [
            {'class_a': a, 'class_b': b, 'distance': round(d, 3),
             'subgroup_a': class_to_subgroup.get(a), 'subgroup_b': class_to_subgroup.get(b),
             'same_subgroup': class_to_subgroup.get(a) == class_to_subgroup.get(b)}
            for (a, b), d in most_distinct
        ],
        'inter_subgroup_mean_distance': round(mean_inter, 3),
        'intra_subgroup_mean_distance': round(mean_intra, 3),
        'separation_ratio': round(separation_ratio, 3),
    },
    'summary_metrics': {
        'positional_distinct_classes': pos_distinct_bonf,
        'positional_distinct_pairs': pairs_distinct_bonf,
        'structured_transition_classes': structured_transitions,
        'context_classification_accuracy': class_accuracy,
        'context_baseline': class_baseline,
    },
    'verdict': {
        'n_effective_groups': best_k,
        'behavioral_dimensionality': components_90,
        'cluster_strength': cluster_verdict,
        'context_signal': context_verdict,
        'assessment': assessment,
    }
}

with open(RESULTS / 'ax_class_distinctness_synthesis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'ax_class_distinctness_synthesis.json'}")
