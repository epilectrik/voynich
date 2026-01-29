"""
Script 2: Morphological Subtype Prediction

For each heterogeneous class (k >= 2), tests whether morphological
features (PREFIX, MIDDLE, SUFFIX, ARTICULATOR) predict cluster membership.

Uses Adjusted Rand Index and chi-squared/Fisher's exact tests.

Expected constraint: C632 (Morphological Subtype Prediction)
Depends on: Script 1 results (intra_class_clustering.json)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import math
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
from scripts.voynich import Transcript, Morphology

# --- Data Loading ---
CLUSTERING_FILE = Path(__file__).parent.parent / 'results' / 'intra_class_clustering.json'
CLASS_MAP_FILE = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(CLUSTERING_FILE) as f:
    clustering = json.load(f)

with open(CLASS_MAP_FILE) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
class_to_tokens = {int(k): v for k, v in class_data['class_to_tokens'].items()}

morph = Morphology()
token_freqs = clustering.get('token_frequencies', {})


# --- Helper Functions ---

def compute_ari(labels_true, labels_pred):
    """Compute Adjusted Rand Index manually."""
    n = len(labels_true)
    if n < 2:
        return 0.0

    # Build contingency table
    classes_t = sorted(set(labels_true))
    classes_p = sorted(set(labels_pred))
    t_map = {c: i for i, c in enumerate(classes_t)}
    p_map = {c: i for i, c in enumerate(classes_p)}

    nij = np.zeros((len(classes_t), len(classes_p)), dtype=int)
    for lt, lp in zip(labels_true, labels_pred):
        nij[t_map[lt], p_map[lp]] += 1

    # Row and column sums
    a = nij.sum(axis=1)  # row sums
    b = nij.sum(axis=0)  # col sums

    # Compute combinations C(n, 2)
    def comb2(x):
        return x * (x - 1) / 2

    sum_nij_comb = sum(comb2(nij[i, j]) for i in range(nij.shape[0]) for j in range(nij.shape[1]))
    sum_a_comb = sum(comb2(ai) for ai in a)
    sum_b_comb = sum(comb2(bj) for bj in b)
    n_comb = comb2(n)

    if n_comb == 0:
        return 0.0

    expected = sum_a_comb * sum_b_comb / n_comb
    max_index = 0.5 * (sum_a_comb + sum_b_comb)
    denom = max_index - expected

    if denom == 0:
        return 1.0 if sum_nij_comb == expected else 0.0

    return (sum_nij_comb - expected) / denom


def fisher_exact_or_chi2(feature_labels, cluster_labels):
    """Test association between a categorical feature and cluster membership."""
    f_classes = sorted(set(feature_labels))
    c_classes = sorted(set(cluster_labels))

    if len(f_classes) < 2 or len(c_classes) < 2:
        return 1.0, 'DEGENERATE'

    # Build contingency table
    table = np.zeros((len(f_classes), len(c_classes)), dtype=int)
    f_map = {c: i for i, c in enumerate(f_classes)}
    c_map = {c: i for i, c in enumerate(c_classes)}

    for fl, cl in zip(feature_labels, cluster_labels):
        table[f_map[fl], c_map[cl]] += 1

    # Use Fisher's exact for 2x2, chi-squared otherwise
    if table.shape == (2, 2):
        _, p = stats.fisher_exact(table)
        return p, 'FISHER'
    else:
        # Chi-squared (if any expected < 5, note it)
        chi2, p, dof, expected = stats.chi2_contingency(table, correction=False)
        min_expected = expected.min()
        method = 'CHI2' if min_expected >= 5 else 'CHI2_LOW_EXPECTED'
        return p, method


# ============================================================
# Section 1: Morphological Feature Extraction
# ============================================================

print("=" * 60)
print("SECTION 1: Morphological Feature Extraction")
print("=" * 60)

token_morphology = {}  # token -> {prefix, middle, suffix, articulator, has_articulator, length}

for token in token_to_class:
    m = morph.extract(token)
    token_morphology[token] = {
        'prefix': m.prefix if m.prefix else 'NONE',
        'middle': m.middle if m.middle else 'NONE',
        'suffix': m.suffix if m.suffix else 'NONE',
        'articulator': m.articulator if m.articulator else 'NONE',
        'has_articulator': bool(m.articulator),
        'length': len(token)
    }

print(f"Extracted morphology for {len(token_morphology)} tokens")

# Summary of morphological features
prefix_dist = Counter(v['prefix'] for v in token_morphology.values())
middle_dist = Counter(v['middle'] for v in token_morphology.values())
suffix_dist = Counter(v['suffix'] for v in token_morphology.values())
art_dist = Counter(v['has_articulator'] for v in token_morphology.values())

print(f"Unique prefixes: {len(prefix_dist)}")
print(f"Unique middles: {len(middle_dist)}")
print(f"Unique suffixes: {len(suffix_dist)}")
print(f"Articulated tokens: {art_dist.get(True, 0)} / {len(token_morphology)}")

# ============================================================
# Section 2: Morphological Predictivity Test
# ============================================================

print("\n" + "=" * 60)
print("SECTION 2: Morphological Predictivity Test")
print("=" * 60)

per_class = clustering['per_class']
heterogeneous = [int(k) for k, v in per_class.items() if v['optimal_k'] > 1]
eligible_set = set()
for cls_id in heterogeneous:
    cm = per_class[str(cls_id)].get('cluster_members_eligible', {})
    for members in cm.values():
        eligible_set.update(members)

print(f"Heterogeneous classes: {heterogeneous}")
print(f"Total eligible tokens in heterogeneous classes: {len(eligible_set)}")

FEATURES = ['prefix', 'middle', 'suffix', 'articulator']
class_morph_results = {}

for cls_id in sorted(heterogeneous):
    cls_data = per_class[str(cls_id)]
    assignments = cls_data['cluster_assignments']
    eligible_members = cls_data.get('cluster_members_eligible', {})

    # Get eligible tokens and their clusters
    tokens_and_clusters = []
    for cluster_id, members in eligible_members.items():
        for token in members:
            tokens_and_clusters.append((token, int(cluster_id)))

    if len(tokens_and_clusters) < 2:
        print(f"\n  Class {cls_id}: too few eligible tokens for prediction test")
        continue

    tokens = [tc[0] for tc in tokens_and_clusters]
    cluster_labels = [tc[1] for tc in tokens_and_clusters]

    print(f"\n  Class {cls_id} ({cls_data['role']}, n={len(tokens)}, k={cls_data['optimal_k']}):")
    for cid, members in sorted(eligible_members.items()):
        print(f"    Cluster {cid}: {members}")

    feature_results = {}
    for feature in FEATURES:
        feature_labels = [token_morphology[t][feature] for t in tokens]

        # Skip if feature is degenerate (all same value)
        if len(set(feature_labels)) < 2:
            feature_results[feature] = {
                'ari': 0.0,
                'p_value': 1.0,
                'method': 'DEGENERATE',
                'partition': dict(Counter(feature_labels))
            }
            print(f"    {feature:12s}: ARI=0.000 (degenerate - all same)")
            continue

        ari = compute_ari(cluster_labels, feature_labels)
        p_val, method = fisher_exact_or_chi2(feature_labels, cluster_labels)

        feature_results[feature] = {
            'ari': round(ari, 4),
            'p_value': round(p_val, 6),
            'method': method,
            'partition': dict(Counter(feature_labels))
        }
        sig = '*' if p_val < 0.05 else ''
        print(f"    {feature:12s}: ARI={ari:.3f}, p={p_val:.4f} ({method}) {sig}")

    # Print morphological details
    print(f"    Token details:")
    for token, cluster in tokens_and_clusters:
        m = token_morphology[token]
        print(f"      {token:15s} -> cluster {cluster}  "
              f"pre={m['prefix']:6s} mid={m['middle']:6s} "
              f"suf={m['suffix']:6s} art={m['articulator']:4s}")

    # Identify best predictor
    best_feature = max(feature_results, key=lambda f: feature_results[f]['ari'])
    best_ari = feature_results[best_feature]['ari']
    best_p = feature_results[best_feature]['p_value']

    class_morph_results[cls_id] = {
        'n_tokens': len(tokens),
        'optimal_k': cls_data['optimal_k'],
        'role': cls_data['role'],
        'features': feature_results,
        'best_predictor': best_feature,
        'best_ari': best_ari,
        'best_p_value': best_p,
        'significant': best_p < 0.05
    }

    print(f"    BEST: {best_feature} (ARI={best_ari:.3f}, p={best_p:.4f})")

# ============================================================
# Section 3: Dominant Morphological Predictor
# ============================================================

print("\n" + "=" * 60)
print("SECTION 3: Dominant Morphological Predictor")
print("=" * 60)

if not class_morph_results:
    print("No heterogeneous classes with enough data for prediction test.")
else:
    # Which feature wins most often?
    predictor_wins = Counter()
    sig_predictors = Counter()
    ari_by_feature = defaultdict(list)

    for cls_id, result in class_morph_results.items():
        predictor_wins[result['best_predictor']] += 1
        if result['significant']:
            sig_predictors[result['best_predictor']] += 1
        for feature, fdata in result['features'].items():
            ari_by_feature[feature].append(fdata['ari'])

    print(f"Best predictor distribution (all classes):")
    for feat, count in predictor_wins.most_common():
        print(f"  {feat}: {count} classes")

    print(f"\nSignificant predictor distribution (p<0.05):")
    for feat, count in sig_predictors.most_common():
        print(f"  {feat}: {count} classes")
    if not sig_predictors:
        print("  (none)")

    print(f"\nMean ARI by feature across heterogeneous classes:")
    for feature in FEATURES:
        vals = ari_by_feature[feature]
        if vals:
            print(f"  {feature:12s}: mean={np.mean(vals):.3f}, "
                  f"max={np.max(vals):.3f}, n={len(vals)}")

    # How many classes have ARI > 0.3?
    strong_pred = sum(1 for r in class_morph_results.values() if r['best_ari'] > 0.3)
    any_pred = sum(1 for r in class_morph_results.values() if r['best_ari'] > 0.0)
    total = len(class_morph_results)

    print(f"\nClasses with strong prediction (ARI > 0.3): {strong_pred}/{total}")
    print(f"Classes with any prediction (ARI > 0.0): {any_pred}/{total}")

# ============================================================
# Section 4: Morphological Predictivity Summary
# ============================================================

print("\n" + "=" * 60)
print("SECTION 4: Morphological Predictivity Summary")
print("=" * 60)

if class_morph_results:
    n_total = len(class_morph_results)
    n_strong = sum(1 for r in class_morph_results.values() if r['best_ari'] > 0.3)
    n_sig = sum(1 for r in class_morph_results.values() if r['significant'])
    n_both = sum(1 for r in class_morph_results.values() if r['best_ari'] > 0.3 and r['significant'])

    print(f"Total heterogeneous classes analyzed: {n_total}")
    print(f"  Strong ARI (>0.3): {n_strong} ({100*n_strong/n_total:.0f}%)")
    print(f"  Significant (p<0.05): {n_sig} ({100*n_sig/n_total:.0f}%)")
    print(f"  Both strong + significant: {n_both} ({100*n_both/n_total:.0f}%)")

    # Per-class summary table
    print(f"\nPer-class summary:")
    print(f"  {'Class':>5s} {'Role':>20s} {'k':>2s} {'n':>3s} {'Best Feature':>12s} "
          f"{'ARI':>6s} {'p':>8s} {'Verdict':>12s}")
    print(f"  {'-----':>5s} {'----':>20s} {'--':>2s} {'---':>3s} {'------------':>12s} "
          f"{'------':>6s} {'--------':>8s} {'-------':>12s}")

    for cls_id in sorted(class_morph_results.keys()):
        r = class_morph_results[cls_id]
        if r['best_ari'] > 0.3 and r['significant']:
            verdict = 'PREDICTED'
        elif r['best_ari'] > 0.3:
            verdict = 'TREND'
        elif r['best_ari'] > 0.0:
            verdict = 'WEAK'
        else:
            verdict = 'OPAQUE'
        print(f"  {cls_id:5d} {r['role']:>20s} {r['optimal_k']:2d} {r['n_tokens']:3d} "
              f"{r['best_predictor']:>12s} {r['best_ari']:6.3f} {r['best_p_value']:8.4f} {verdict:>12s}")
else:
    print("No heterogeneous classes to summarize.")

# ============================================================
# Save Results
# ============================================================

output = {
    'metadata': {
        'phase': 'INTRA_CLASS_DIVERSITY',
        'script': 'morphology_subtype_prediction.py',
        'features_tested': FEATURES,
        'ari_strong_threshold': 0.3,
        'significance_threshold': 0.05
    },
    'summary': {
        'n_heterogeneous_analyzed': len(class_morph_results),
        'n_strong_ari': sum(1 for r in class_morph_results.values() if r['best_ari'] > 0.3),
        'n_significant': sum(1 for r in class_morph_results.values() if r['significant']),
        'n_both': sum(1 for r in class_morph_results.values()
                      if r['best_ari'] > 0.3 and r['significant']),
        'predictor_wins': dict(Counter(r['best_predictor'] for r in class_morph_results.values())),
        'mean_ari_by_feature': {
            feat: round(float(np.mean(ari_by_feature[feat])), 4) if ari_by_feature[feat] else None
            for feat in FEATURES
        } if class_morph_results else {}
    },
    'per_class': {
        str(cls_id): {
            'class_id': cls_id,
            **r,
        }
        for cls_id, r in class_morph_results.items()
    },
    'token_morphology': {
        t: m for t, m in token_morphology.items()
        if t in eligible_set
    }
}

out_file = RESULTS_DIR / 'morphology_subtype_prediction.json'
with open(out_file, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nResults saved to {out_file}")
print("DONE")
