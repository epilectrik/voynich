"""
Script 1: Intra-Class Clustering via Successor JS Divergence

For each of the 49 cosurvival classes, determines optimal number of
functional sub-types (k) by:
1. Building successor class distributions for each token type
2. Computing pairwise Jensen-Shannon divergence within each class
3. Hierarchical clustering with silhouette optimization (k=2..8)

Expected constraint: C631 (Intra-Class Clustering Census)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import math
import numpy as np
from collections import Counter, defaultdict
from scipy.spatial.distance import jensenshannon, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score
from scripts.voynich import Transcript

# --- Configuration ---
MIN_FREQ = 10          # Minimum token frequency for clustering eligibility
SILHOUETTE_THRESHOLD = 0.25  # Accept k>1 only above this
JSD_THRESHOLD_2TOKEN = 0.4   # For classes with exactly 2 eligible tokens
MAX_K = 8              # Maximum sub-types to test

# --- Data Loading ---
CLASS_MAP_FILE = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

with open(CLASS_MAP_FILE) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
class_to_tokens = {int(k): v for k, v in class_data['class_to_tokens'].items()}
class_to_role = {int(k): v for k, v in class_data['class_to_role'].items()}

tx = Transcript()
b_tokens = list(tx.currier_b())

# ============================================================
# Section 1: Token-Level Successor Profiles
# ============================================================

print("=" * 60)
print("SECTION 1: Token-Level Successor Profiles")
print("=" * 60)

# Count token frequencies
token_freq = Counter()
for t in b_tokens:
    if t.word.strip() and '*' not in t.word:
        token_freq[t.word] += 1

# Build successor class distributions
# Group tokens by (folio, line) for sequential bigrams
lines = defaultdict(list)
for t in b_tokens:
    if t.word.strip() and '*' not in t.word:
        lines[(t.folio, t.line)].append(t.word)

successor_counts = defaultdict(Counter)  # token -> {successor_class: count}
total_bigrams = 0

for (folio, line), words in lines.items():
    for i in range(len(words) - 1):
        src = words[i]
        tgt = words[i + 1]
        if tgt in token_to_class:
            tgt_class = token_to_class[tgt]
            successor_counts[src][tgt_class] += 1
            total_bigrams += 1

# All class IDs for building fixed-length vectors
all_classes = sorted(class_to_tokens.keys())
class_idx = {c: i for i, c in enumerate(all_classes)}
n_classes = len(all_classes)

# Build normalized successor profiles (only for tokens with freq >= MIN_FREQ)
successor_profiles = {}  # token -> numpy array of length n_classes
eligible_tokens = set()

for token, freq in token_freq.items():
    if freq >= MIN_FREQ and token in token_to_class:
        counts = successor_counts[token]
        total = sum(counts.values())
        if total > 0:
            vec = np.zeros(n_classes)
            for cls, cnt in counts.items():
                if cls in class_idx:
                    vec[class_idx[cls]] = cnt / total
            successor_profiles[token] = vec
            eligible_tokens.add(token)

print(f"Total B token types: {len(token_freq)}")
print(f"Token types with freq >= {MIN_FREQ}: {len(eligible_tokens)}")
print(f"Total bigrams: {total_bigrams}")

# Count eligible tokens per class
class_eligible = {}
for cls_id, members in class_to_tokens.items():
    eligible = [t for t in members if t in eligible_tokens]
    class_eligible[cls_id] = eligible

n_with_2plus = sum(1 for e in class_eligible.values() if len(e) >= 2)
n_with_3plus = sum(1 for e in class_eligible.values() if len(e) >= 3)
print(f"Classes with 2+ eligible tokens: {n_with_2plus}")
print(f"Classes with 3+ eligible tokens: {n_with_3plus}")

# ============================================================
# Section 2: Pairwise JS Divergence Matrix
# ============================================================

print("\n" + "=" * 60)
print("SECTION 2: Pairwise JS Divergence Matrix")
print("=" * 60)

class_jsd_matrices = {}  # cls_id -> {tokens: [...], matrix: condensed distance array, mean_jsd: float}

for cls_id in sorted(class_to_tokens.keys()):
    eligible = class_eligible[cls_id]
    if len(eligible) < 2:
        continue

    # Build pairwise JSD matrix
    n = len(eligible)
    condensed = []
    for i in range(n):
        for j in range(i + 1, n):
            p = successor_profiles[eligible[i]]
            q = successor_profiles[eligible[j]]
            # jensenshannon returns distance (sqrt of divergence)
            d = jensenshannon(p, q)
            if np.isnan(d):
                d = 1.0  # max distance if undefined
            condensed.append(d)

    condensed = np.array(condensed)
    mean_jsd = float(np.mean(condensed))

    class_jsd_matrices[cls_id] = {
        'tokens': eligible,
        'condensed': condensed,
        'mean_jsd': mean_jsd,
        'n_eligible': n
    }

    print(f"  Class {cls_id:2d} ({class_to_role.get(cls_id, '?'):20s}): "
          f"{n:2d} eligible, mean JSD={mean_jsd:.3f}")

# ============================================================
# Section 3: Hierarchical Clustering + Silhouette Optimization
# ============================================================

print("\n" + "=" * 60)
print("SECTION 3: Hierarchical Clustering + Silhouette")
print("=" * 60)

class_results = {}

for cls_id in sorted(class_to_tokens.keys()):
    members = class_to_tokens[cls_id]
    eligible = class_eligible[cls_id]
    role = class_to_role.get(cls_id, 'UNKNOWN')

    result = {
        'class_id': cls_id,
        'role': role,
        'n_tokens': len(members),
        'n_eligible': len(eligible),
        'optimal_k': 1,
        'silhouette_score': None,
        'mean_jsd': None,
        'cluster_assignments': {},
        'silhouette_scores': {},
        'method': None
    }

    if len(eligible) == 0:
        result['method'] = 'NO_ELIGIBLE'
        # Assign all members to cluster 0
        result['cluster_assignments'] = {t: 0 for t in members}
        class_results[cls_id] = result
        print(f"  Class {cls_id:2d}: k=1 (no eligible tokens)")
        continue

    if len(eligible) == 1:
        result['method'] = 'SINGLE_ELIGIBLE'
        result['cluster_assignments'] = {t: 0 for t in members}
        class_results[cls_id] = result
        print(f"  Class {cls_id:2d}: k=1 (1 eligible token)")
        continue

    jsd_data = class_jsd_matrices[cls_id]
    result['mean_jsd'] = jsd_data['mean_jsd']

    if len(eligible) == 2:
        # Simple threshold test for 2-token classes
        jsd_val = float(jsd_data['condensed'][0])
        result['method'] = 'THRESHOLD_2TOKEN'
        if jsd_val > JSD_THRESHOLD_2TOKEN:
            result['optimal_k'] = 2
            result['cluster_assignments'] = {eligible[0]: 0, eligible[1]: 1}
            # Assign ineligible tokens to cluster 0 (default)
            for t in members:
                if t not in result['cluster_assignments']:
                    result['cluster_assignments'][t] = 0
        else:
            result['optimal_k'] = 1
            result['cluster_assignments'] = {t: 0 for t in members}
        result['silhouette_score'] = jsd_val  # Store JSD as proxy
        print(f"  Class {cls_id:2d}: k={result['optimal_k']} "
              f"(2-token, JSD={jsd_val:.3f}, threshold={JSD_THRESHOLD_2TOKEN})")
        class_results[cls_id] = result
        continue

    # 3+ eligible tokens: hierarchical clustering with silhouette
    condensed = jsd_data['condensed']

    # Convert condensed to full distance matrix for silhouette
    full_matrix = squareform(condensed)

    # Linkage (UPGMA)
    Z = linkage(condensed, method='average')

    # Test k = 2 through min(n_eligible, MAX_K)
    max_test_k = min(len(eligible), MAX_K)
    silhouette_scores = {}
    best_k = 1
    best_sil = -1

    for k in range(2, max_test_k + 1):
        labels = fcluster(Z, t=k, criterion='maxclust')
        # Check we actually got k clusters
        n_unique = len(set(labels))
        if n_unique < 2:
            continue
        try:
            sil = silhouette_score(full_matrix, labels, metric='precomputed')
            silhouette_scores[k] = round(float(sil), 4)
            if sil > best_sil and sil >= SILHOUETTE_THRESHOLD:
                best_sil = sil
                best_k = k
        except Exception:
            continue

    result['silhouette_scores'] = silhouette_scores
    result['optimal_k'] = best_k
    result['method'] = 'HIERARCHICAL_SILHOUETTE'

    if best_k > 1:
        labels = fcluster(Z, t=best_k, criterion='maxclust')
        result['silhouette_score'] = round(best_sil, 4)
        # Map eligible tokens to clusters (0-indexed)
        for i, token in enumerate(eligible):
            result['cluster_assignments'][token] = int(labels[i]) - 1
        # Assign ineligible tokens: find nearest eligible neighbor
        for t in members:
            if t not in result['cluster_assignments']:
                if t in successor_profiles:
                    # Has profile but below freq threshold - find nearest eligible
                    min_dist = float('inf')
                    nearest_cluster = 0
                    for i, et in enumerate(eligible):
                        d = jensenshannon(successor_profiles[t], successor_profiles[et])
                        if not np.isnan(d) and d < min_dist:
                            min_dist = d
                            nearest_cluster = int(labels[i]) - 1
                    result['cluster_assignments'][t] = nearest_cluster
                else:
                    result['cluster_assignments'][t] = 0
    else:
        result['silhouette_score'] = max(silhouette_scores.values()) if silhouette_scores else None
        result['cluster_assignments'] = {t: 0 for t in members}

    # Compute within-cluster and between-cluster mean JSD
    if best_k > 1:
        within_jsds = []
        between_jsds = []
        for i in range(len(eligible)):
            for j in range(i + 1, len(eligible)):
                idx = i * len(eligible) - i * (i + 1) // 2 + j - i - 1
                d = float(condensed[idx])
                ci = result['cluster_assignments'][eligible[i]]
                cj = result['cluster_assignments'][eligible[j]]
                if ci == cj:
                    within_jsds.append(d)
                else:
                    between_jsds.append(d)
        result['mean_within_jsd'] = round(float(np.mean(within_jsds)), 4) if within_jsds else None
        result['mean_between_jsd'] = round(float(np.mean(between_jsds)), 4) if between_jsds else None
    else:
        result['mean_within_jsd'] = result['mean_jsd']
        result['mean_between_jsd'] = None

    sil_str = f"sil={result['silhouette_score']:.3f}" if result['silhouette_score'] is not None else "sil=N/A"
    print(f"  Class {cls_id:2d} ({role:20s}): k={best_k}, {sil_str}, "
          f"n_eligible={len(eligible)}, mean_jsd={jsd_data['mean_jsd']:.3f}")

    class_results[cls_id] = result

# ============================================================
# Section 4: Per-Class Summary
# ============================================================

print("\n" + "=" * 60)
print("SECTION 4: Per-Class Summary")
print("=" * 60)

# Aggregate statistics
k_distribution = Counter()
heterogeneous_classes = []
uniform_classes = []

for cls_id in sorted(class_results.keys()):
    r = class_results[cls_id]
    k_distribution[r['optimal_k']] += 1
    if r['optimal_k'] > 1:
        heterogeneous_classes.append(cls_id)
    else:
        uniform_classes.append(cls_id)

total_effective = sum(r['optimal_k'] for r in class_results.values())

print(f"\nTotal classes: {len(class_results)}")
print(f"Heterogeneous (k>1): {len(heterogeneous_classes)}")
print(f"Uniform (k=1): {len(uniform_classes)}")
print(f"Effective vocabulary size: {total_effective}")
print(f"\nk distribution:")
for k in sorted(k_distribution.keys()):
    print(f"  k={k}: {k_distribution[k]} classes")

print(f"\nHeterogeneous classes:")
for cls_id in heterogeneous_classes:
    r = class_results[cls_id]
    print(f"  Class {cls_id:2d} ({r['role']:20s}): k={r['optimal_k']}, "
          f"sil={r.get('silhouette_score', 'N/A')}, n_eligible={r['n_eligible']}")
    # Print cluster members
    clusters = defaultdict(list)
    for token, cluster in r['cluster_assignments'].items():
        if token in eligible_tokens:
            clusters[cluster].append(token)
    for c in sorted(clusters.keys()):
        members_str = ', '.join(sorted(clusters[c], key=lambda t: -token_freq.get(t, 0)))
        print(f"    Cluster {c}: [{members_str}]")

# Role-level summary
print(f"\nRole-level summary:")
role_stats = defaultdict(lambda: {'classes': 0, 'effective': 0, 'heterogeneous': 0})
for cls_id, r in class_results.items():
    role = r['role']
    role_stats[role]['classes'] += 1
    role_stats[role]['effective'] += r['optimal_k']
    if r['optimal_k'] > 1:
        role_stats[role]['heterogeneous'] += 1

for role in sorted(role_stats.keys()):
    s = role_stats[role]
    mean_k = s['effective'] / s['classes'] if s['classes'] > 0 else 0
    print(f"  {role:20s}: {s['classes']:2d} classes, {s['effective']:3d} effective, "
          f"{s['heterogeneous']:2d} heterogeneous, mean_k={mean_k:.2f}")

# Hazard comparison
hazard_classes = {7, 8, 9, 23, 30, 31}
hazard_ks = [class_results[c]['optimal_k'] for c in hazard_classes if c in class_results]
nonhazard_ks = [class_results[c]['optimal_k'] for c in class_results if c not in hazard_classes]
print(f"\nHazard classes mean k: {np.mean(hazard_ks):.2f} ({len(hazard_ks)} classes)")
print(f"Non-hazard classes mean k: {np.mean(nonhazard_ks):.2f} ({len(nonhazard_ks)} classes)")

# ============================================================
# Save Results
# ============================================================

output = {
    'metadata': {
        'phase': 'INTRA_CLASS_DIVERSITY',
        'script': 'intra_class_clustering.py',
        'min_freq_threshold': MIN_FREQ,
        'silhouette_threshold': SILHOUETTE_THRESHOLD,
        'jsd_threshold_2token': JSD_THRESHOLD_2TOKEN,
        'max_k': MAX_K,
        'total_b_token_types': len(token_freq),
        'eligible_token_types': len(eligible_tokens),
        'total_bigrams': total_bigrams
    },
    'summary': {
        'total_classes': len(class_results),
        'heterogeneous_count': len(heterogeneous_classes),
        'uniform_count': len(uniform_classes),
        'effective_vocabulary_size': total_effective,
        'k_distribution': {str(k): v for k, v in sorted(k_distribution.items())},
        'heterogeneous_class_ids': heterogeneous_classes,
        'uniform_class_ids': uniform_classes
    },
    'per_class': {}
}

for cls_id, r in class_results.items():
    entry = {
        'class_id': cls_id,
        'role': r['role'],
        'n_tokens': r['n_tokens'],
        'n_eligible': r['n_eligible'],
        'optimal_k': r['optimal_k'],
        'silhouette_score': r['silhouette_score'],
        'silhouette_scores': r.get('silhouette_scores', {}),
        'mean_jsd': r['mean_jsd'],
        'mean_within_jsd': r.get('mean_within_jsd'),
        'mean_between_jsd': r.get('mean_between_jsd'),
        'method': r['method'],
        'cluster_assignments': r['cluster_assignments']
    }
    # Add cluster member lists (eligible only) for easy reading
    if r['optimal_k'] > 1:
        clusters = defaultdict(list)
        for token, cluster in r['cluster_assignments'].items():
            if token in eligible_tokens:
                clusters[cluster].append(token)
        entry['cluster_members_eligible'] = {
            str(c): sorted(members, key=lambda t: -token_freq.get(t, 0))
            for c, members in sorted(clusters.items())
        }
    output['per_class'][str(cls_id)] = entry

# Token frequency map for downstream scripts
output['token_frequencies'] = {t: f for t, f in token_freq.most_common() if t in token_to_class}

out_file = RESULTS_DIR / 'intra_class_clustering.json'
with open(out_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {out_file}")
print("DONE")
