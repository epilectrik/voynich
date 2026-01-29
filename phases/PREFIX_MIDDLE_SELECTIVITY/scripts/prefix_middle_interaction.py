#!/usr/bin/env python3
"""
PREFIX_MIDDLE_SELECTIVITY Phase - Script 2: PREFIX x MIDDLE Interaction

Tests 5-7: Measure PREFIX x MIDDLE interaction effect on successor class,
PREFIX role reclassification, and effective PREFIX x MIDDLE classification.

Dependencies:
  - prefix_middle_inventory.json (Script 1 output)
  - middle_classes_v2_backup.json (A_INTERNAL_STRATIFICATION)
  - pp_role_foundation.json (A_TO_B_ROLE_PROJECTION)
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - scripts/voynich.py (Transcript, Morphology)
"""

import json
import sys
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'

# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================

print("=" * 70)
print("PREFIX_MIDDLE_SELECTIVITY - Script 2: PREFIX x MIDDLE Interaction")
print("=" * 70)

# Load Script 1 results
with open(RESULTS_DIR / 'prefix_middle_inventory.json') as f:
    inv_results = json.load(f)

# Load PP set (404 MIDDLEs)
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])
print(f"\nPP MIDDLEs: {len(pp_set)}")

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_token_raw = json.load(f)
# Build token -> class mapping
# class_token_map.json has {"token_to_class": {token: class, ...}, ...}
if 'token_to_class' in class_token_raw:
    token_to_class = {tok: int(cls) for tok, cls in class_token_raw['token_to_class'].items()}
else:
    # Fallback: assume {class_str: [tokens]}
    token_to_class = {}
    for cls_str, tokens in class_token_raw.items():
        cls = int(cls_str)
        for tok in tokens:
            token_to_class[tok] = cls
print(f"Token-to-class map: {len(token_to_class)} tokens")

# Load EN class list for role classification
en_classes = set()
try:
    with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
        en_data = json.load(f)
    en_classes = set(en_data.get('definitive_en_classes', []))
    print(f"EN classes: {len(en_classes)}")
except FileNotFoundError:
    print("Warning: en_census.json not found, EN class identification limited")

# AX classes (from BCSC: classes 1-7 are AX per standard taxonomy)
# FQ classes: 13, 14 per BCSC
AX_CLASSES = set(range(1, 8))  # 1-7
FQ_CLASSES = {13, 14}
# INFRA classes: typically CC (8-12 range) but let's use the taxonomy
CC_CLASSES = set(range(8, 13))  # Core Control 8-12

tx = Transcript()
morph = Morphology()

# ============================================================
# BUILD SUCCESSOR PROFILES
# ============================================================

print("\nBuilding successor profiles per PREFIX x MIDDLE pair...")

b_lines = defaultdict(list)
for token in tx.currier_b():
    if token.word.strip() and '*' not in token.word:
        b_lines[(token.folio, token.line)].append(token.word)

pair_successor = defaultdict(Counter)    # (prefix, middle) -> Counter{next_class: count}
middle_successor = defaultdict(Counter)  # middle -> Counter{next_class: count}
prefix_successor = defaultdict(Counter)  # prefix -> Counter{next_class: count}
pair_class_membership = defaultdict(set) # (prefix, middle) -> set of classes this pair appears in
middle_class_membership = defaultdict(set)  # middle -> set of classes

for (folio, line), words in b_lines.items():
    for i in range(len(words)):
        m = morph.extract(words[i])
        if m.middle and m.middle in pp_set:
            prefix_key = m.prefix if m.prefix else 'NONE'
            # Record class membership of current token
            current_cls = token_to_class.get(words[i])
            if current_cls is not None:
                pair_class_membership[(prefix_key, m.middle)].add(current_cls)
                middle_class_membership[m.middle].add(current_cls)
            # Record successor class
            if i < len(words) - 1:
                next_cls = token_to_class.get(words[i + 1])
                if next_cls is not None:
                    pair_successor[(prefix_key, m.middle)][next_cls] += 1
                    middle_successor[m.middle][next_cls] += 1
                    prefix_successor[prefix_key][next_cls] += 1

print(f"PREFIX x MIDDLE pairs with successor data: {len(pair_successor)}")
print(f"MIDDLEs with successor data: {len(middle_successor)}")
print(f"PREFIXes with successor data: {len(prefix_successor)}")

# All classes observed
all_classes = sorted(set().union(*[set(c.keys()) for c in pair_successor.values()]))
n_classes = len(all_classes)
class_to_idx = {c: i for i, c in enumerate(all_classes)}
print(f"Distinct successor classes: {n_classes}")

# ============================================================
# HELPER: Build normalized distribution vector
# ============================================================

def to_dist(counter, class_list=all_classes):
    """Convert Counter to normalized probability vector."""
    total = sum(counter.values())
    if total == 0:
        return np.zeros(len(class_list))
    vec = np.array([counter.get(c, 0) for c in class_list], dtype=float)
    return vec / total

def jsd(p, q):
    """Jensen-Shannon Divergence between two distributions."""
    m = 0.5 * (p + q)
    # Add small epsilon to avoid log(0)
    eps = 1e-12
    kl_pm = np.sum(p * np.log2((p + eps) / (m + eps)))
    kl_qm = np.sum(q * np.log2((q + eps) / (m + eps)))
    return 0.5 * (kl_pm + kl_qm)

results = {}

# ============================================================
# SECTION 2: TEST 5 -- PREFIX x MIDDLE Interaction Effect
# ============================================================

print("\n" + "=" * 70)
print("TEST 5: PREFIX x MIDDLE Interaction Effect")
print("=" * 70)

MIN_PAIR_BIGRAMS = 10

# Find MIDDLEs with >=2 PREFIXes each having >=MIN_PAIR_BIGRAMS
testable_middles = {}
for mid in middle_successor:
    prefix_variants = {}
    for (pfx, m), counts in pair_successor.items():
        if m == mid and sum(counts.values()) >= MIN_PAIR_BIGRAMS:
            prefix_variants[pfx] = counts
    if len(prefix_variants) >= 2:
        testable_middles[mid] = prefix_variants

print(f"\nMIDDLEs with >=2 PREFIX variants (each >={MIN_PAIR_BIGRAMS} bigrams): {len(testable_middles)}")

# For each testable MIDDLE: compute within-MIDDLE between-PREFIX JSD
within_middle_jsds = []
middle_interaction_data = {}

for mid, variants in testable_middles.items():
    # Build distributions
    pfx_dists = {}
    for pfx, counts in variants.items():
        pfx_dists[pfx] = to_dist(counts)

    # Aggregate (MIDDLE-level)
    mid_dist = to_dist(middle_successor[mid])

    # Within-MIDDLE between-PREFIX JSD: pairwise between PREFIX variants
    pairwise_jsds = []
    for (p1, d1), (p2, d2) in combinations(pfx_dists.items(), 2):
        j = jsd(d1, d2)
        pairwise_jsds.append(j)

    mean_within = np.mean(pairwise_jsds) if pairwise_jsds else 0
    within_middle_jsds.append(mean_within)

    # JSD of each variant from the aggregate
    deviation_jsds = []
    for pfx, dist in pfx_dists.items():
        deviation_jsds.append(jsd(dist, mid_dist))

    middle_interaction_data[mid] = {
        'n_variants': len(variants),
        'prefixes': sorted(variants.keys()),
        'mean_within_jsd': round(float(mean_within), 4),
        'max_within_jsd': round(float(max(pairwise_jsds)), 4) if pairwise_jsds else 0,
        'mean_deviation_jsd': round(float(np.mean(deviation_jsds)), 4),
        'total_bigrams': sum(sum(c.values()) for c in variants.values()),
    }

if within_middle_jsds:
    mean_within_all = float(np.mean(within_middle_jsds))
    median_within_all = float(np.median(within_middle_jsds))
    max_within_all = float(max(within_middle_jsds))
else:
    mean_within_all = median_within_all = max_within_all = 0

# Reference: between-MIDDLE JSD from C657 (mean=0.537)
between_middle_ref = 0.537
effect_ratio = mean_within_all / between_middle_ref if between_middle_ref > 0 else 0

print(f"\nWithin-MIDDLE between-PREFIX JSD:")
print(f"  Mean:   {mean_within_all:.4f}")
print(f"  Median: {median_within_all:.4f}")
print(f"  Max:    {max_within_all:.4f}")
print(f"\nBetween-MIDDLE JSD reference (C657): {between_middle_ref:.3f}")
print(f"Effect ratio (within/between): {effect_ratio:.3f}")

if effect_ratio < 0.3:
    interaction_verdict = "PREFIX_MODULATES"
    print("Verdict: PREFIX modulates but does NOT transform behavior (ratio < 0.3)")
elif effect_ratio < 0.7:
    interaction_verdict = "PREFIX_SIGNIFICANT"
    print("Verdict: PREFIX has significant but not dominant interaction effect (0.3-0.7)")
else:
    interaction_verdict = "PREFIX_TRANSFORMS"
    print("Verdict: PREFIX fundamentally transforms behavior (ratio >= 0.7)")

# Top interaction MIDDLEs (highest within-MIDDLE JSD)
top_interaction = sorted(middle_interaction_data.items(), key=lambda x: -x[1]['mean_within_jsd'])
print(f"\nTop 10 interaction MIDDLEs (highest within-MIDDLE between-PREFIX JSD):")
for mid, d in top_interaction[:10]:
    pfx_str = ', '.join(d['prefixes'][:4])
    print(f"  {mid:8s}: JSD={d['mean_within_jsd']:.3f}, max={d['max_within_jsd']:.3f}, "
          f"variants={d['n_variants']}, n={d['total_bigrams']}, pfx=[{pfx_str}]")

# Also compute: overall between-MIDDLE JSD for validation
# (Sample of pairwise JSD between different MIDDLEs)
mid_dists = {}
for mid in middle_successor:
    total = sum(middle_successor[mid].values())
    if total >= MIN_PAIR_BIGRAMS:
        mid_dists[mid] = to_dist(middle_successor[mid])

if len(mid_dists) >= 2:
    # Sample up to 5000 pairs
    mid_list = list(mid_dists.keys())
    between_jsds = []
    n_pairs = min(5000, len(mid_list) * (len(mid_list) - 1) // 2)
    if n_pairs <= 5000:
        for m1, m2 in combinations(mid_list, 2):
            between_jsds.append(jsd(mid_dists[m1], mid_dists[m2]))
    else:
        rng = np.random.default_rng(42)
        indices = rng.choice(len(mid_list), size=(5000, 2), replace=True)
        for i, j in indices:
            if i != j:
                between_jsds.append(jsd(mid_dists[mid_list[i]], mid_dists[mid_list[j]]))

    computed_between = float(np.mean(between_jsds))
    print(f"\nComputed between-MIDDLE JSD (n={len(between_jsds)} pairs): {computed_between:.4f}")
    print(f"C657 reference: {between_middle_ref:.3f}")
else:
    computed_between = between_middle_ref

results['interaction'] = {
    'n_testable_middles': len(testable_middles),
    'min_pair_bigrams': MIN_PAIR_BIGRAMS,
    'within_middle_between_prefix_jsd': {
        'mean': round(mean_within_all, 4),
        'median': round(median_within_all, 4),
        'max': round(max_within_all, 4),
    },
    'between_middle_jsd_reference': between_middle_ref,
    'computed_between_middle_jsd': round(computed_between, 4),
    'effect_ratio': round(effect_ratio, 4),
    'verdict': interaction_verdict,
    'top_interaction_middles': {m: d for m, d in top_interaction[:20]},
    'per_middle': {m: d for m, d in sorted(middle_interaction_data.items(), key=lambda x: -x[1]['mean_within_jsd'])},
}

# ============================================================
# SECTION 3: TEST 6 -- PREFIX Role Reclassification
# ============================================================

print("\n" + "=" * 70)
print("TEST 6: PREFIX Role Reclassification")
print("=" * 70)

MIN_PAIR_TOKENS = 5

# EN-family prefixes (from C570)
EN_PREFIXES = {'ch', 'sh', 'qo'}
AX_PREFIXES = {'ok', 'ot', 'ct'}
INFRA_PREFIXES = {'da', 'do', 'sa', 'so'}

# For each MIDDLE: how many classes does it appear in?
# For each (PREFIX, MIDDLE): how many classes?
reduction_data = []
en_prefix_en_class = []
ax_prefix_ax_class = []
infra_prefix_infra_class = []

# Count tokens per (prefix, middle) pair from the actual B text
pair_token_counts = defaultdict(int)
for (folio, line), words in b_lines.items():
    for w in words:
        m = morph.extract(w)
        if m.middle and m.middle in pp_set:
            pfx = m.prefix if m.prefix else 'NONE'
            pair_token_counts[(pfx, m.middle)] += 1

for mid in middle_class_membership:
    mid_classes_set = middle_class_membership[mid]
    n_mid_classes = len(mid_classes_set)
    if n_mid_classes < 2:
        continue  # Can't reduce from 1

    for (pfx, m), cls_set in pair_class_membership.items():
        if m != mid:
            continue
        if pair_token_counts.get((pfx, mid), 0) < MIN_PAIR_TOKENS:
            continue

        n_pair_classes = len(cls_set)
        reduction = n_pair_classes / n_mid_classes
        reduction_data.append({
            'middle': mid,
            'prefix': pfx,
            'middle_classes': n_mid_classes,
            'pair_classes': n_pair_classes,
            'reduction': reduction,
        })

        # EN PREFIX -> EN class rate
        if pfx in EN_PREFIXES:
            en_in = len(cls_set & en_classes)
            en_rate = en_in / len(cls_set) if cls_set else 0
            en_prefix_en_class.append(en_rate)

        # AX PREFIX -> AX/FQ class rate
        if pfx in AX_PREFIXES:
            ax_fq_in = len(cls_set & (AX_CLASSES | FQ_CLASSES))
            ax_rate = ax_fq_in / len(cls_set) if cls_set else 0
            ax_prefix_ax_class.append(ax_rate)

        # INFRA PREFIX -> INFRA/CC class rate
        if pfx in INFRA_PREFIXES:
            infra_in = len(cls_set & CC_CLASSES)
            infra_rate = infra_in / len(cls_set) if cls_set else 0
            infra_prefix_infra_class.append(infra_rate)

if reduction_data:
    reductions = [d['reduction'] for d in reduction_data]
    mean_reduction = float(np.mean(reductions))
    median_reduction = float(np.median(reductions))
    print(f"\nClass reduction ratio (pair_classes / middle_classes):")
    print(f"  Mean:   {mean_reduction:.3f}")
    print(f"  Median: {median_reduction:.3f}")
    print(f"  Pairs analyzed: {len(reduction_data)}")

    # Distribution of reductions
    bins = {'0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0}
    for r in reductions:
        if r < 0.2:
            bins['0.0-0.2'] += 1
        elif r < 0.4:
            bins['0.2-0.4'] += 1
        elif r < 0.6:
            bins['0.4-0.6'] += 1
        elif r < 0.8:
            bins['0.6-0.8'] += 1
        else:
            bins['0.8-1.0'] += 1
    print(f"\n  Distribution:")
    for b, c in bins.items():
        print(f"    {b}: {c} ({100*c/len(reductions):.1f}%)")
else:
    mean_reduction = median_reduction = 0
    bins = {}
    print("\nNo reduction data (insufficient pairs)")

# Role specificity rates
if en_prefix_en_class:
    en_rate_mean = float(np.mean(en_prefix_en_class))
    print(f"\nEN PREFIX -> EN class rate: {en_rate_mean:.3f} ({len(en_prefix_en_class)} pairs)")
else:
    en_rate_mean = 0
    print(f"\nEN PREFIX -> EN class rate: no data")

if ax_prefix_ax_class:
    ax_rate_mean = float(np.mean(ax_prefix_ax_class))
    print(f"AX PREFIX -> AX/FQ class rate: {ax_rate_mean:.3f} ({len(ax_prefix_ax_class)} pairs)")
else:
    ax_rate_mean = 0
    print(f"AX PREFIX -> AX/FQ class rate: no data")

if infra_prefix_infra_class:
    infra_rate_mean = float(np.mean(infra_prefix_infra_class))
    print(f"INFRA PREFIX -> CC class rate: {infra_rate_mean:.3f} ({len(infra_prefix_infra_class)} pairs)")
else:
    infra_rate_mean = 0
    print(f"INFRA PREFIX -> CC class rate: no data")

# Best examples of role reclassification
if reduction_data:
    reduction_data.sort(key=lambda x: x['reduction'])
    print(f"\nMost role-narrowing pairs (lowest reduction ratio):")
    for d in reduction_data[:10]:
        print(f"  {d['prefix']:6s} + {d['middle']:8s}: {d['pair_classes']}/{d['middle_classes']} classes "
              f"(reduction={d['reduction']:.2f})")

results['role_reclassification'] = {
    'n_pairs_analyzed': len(reduction_data),
    'min_pair_tokens': MIN_PAIR_TOKENS,
    'mean_class_reduction': round(mean_reduction, 4),
    'median_class_reduction': round(median_reduction, 4),
    'reduction_distribution': bins,
    'en_prefix_en_class_rate': round(en_rate_mean, 4),
    'en_prefix_n_pairs': len(en_prefix_en_class),
    'ax_prefix_ax_class_rate': round(ax_rate_mean, 4),
    'ax_prefix_n_pairs': len(ax_prefix_ax_class),
    'infra_prefix_cc_class_rate': round(infra_rate_mean, 4),
    'infra_prefix_n_pairs': len(infra_prefix_infra_class),
    'top_narrowing': [d for d in reduction_data[:20]],
}

# ============================================================
# SECTION 4: TEST 7 -- Effective PREFIX x MIDDLE Classification
# ============================================================

print("\n" + "=" * 70)
print("TEST 7: Effective PREFIX x MIDDLE Classification")
print("=" * 70)

# Count all observed (PREFIX, MIDDLE) pairs
all_pairs = set(pair_successor.keys()) | set(pair_class_membership.keys())
observed_pairs = len(all_pairs)

# Filter to pairs with >=5 tokens
effective_pairs_set = {(pfx, mid) for (pfx, mid), n in pair_token_counts.items() if n >= 5}
effective_pairs = len(effective_pairs_set)

# Distinct PREFIXes and MIDDLEs in effective set
eff_prefixes = set(p for p, _ in effective_pairs_set)
eff_middles = set(m for _, m in effective_pairs_set)
theoretical_max = len(eff_prefixes) * len(eff_middles)

sparsity = 1.0 - (effective_pairs / theoretical_max) if theoretical_max > 0 else 0
expansion_factor = effective_pairs / 404 if 404 > 0 else 0

print(f"\nObserved (PREFIX, MIDDLE) pairs: {observed_pairs}")
print(f"Effective pairs (>=5 tokens): {effective_pairs}")
print(f"Effective PREFIXes: {len(eff_prefixes)}, Effective MIDDLEs: {len(eff_middles)}")
print(f"Theoretical max: {theoretical_max}")
print(f"Sparsity: {sparsity:.3f}")
print(f"Expansion factor (from 404 MIDDLEs): {expansion_factor:.2f}x")

# Clustering of (PREFIX, MIDDLE) pairs by behavioral profile
MIN_CLUSTER_BIGRAMS = 20

clusterable_pairs = {}
for (pfx, mid), counts in pair_successor.items():
    total = sum(counts.values())
    if total >= MIN_CLUSTER_BIGRAMS:
        clusterable_pairs[(pfx, mid)] = to_dist(counts)

n_clusterable = len(clusterable_pairs)
print(f"\nClusterable pairs (>={MIN_CLUSTER_BIGRAMS} bigrams): {n_clusterable}")

clustering_results = {}

if n_clusterable >= 10:
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import squareform
    from sklearn.metrics import silhouette_score

    pair_labels = sorted(clusterable_pairs.keys())
    pair_dists_list = [clusterable_pairs[p] for p in pair_labels]

    # Build JSD distance matrix
    n = len(pair_labels)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = jsd(pair_dists_list[i], pair_dists_list[j])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    condensed = squareform(dist_matrix)

    # Hierarchical clustering + silhouette sweep
    Z = linkage(condensed, method='average')
    max_k = min(20, n - 1)
    sil_scores = {}
    for k in range(2, max_k + 1):
        labels = fcluster(Z, t=k, criterion='maxclust')
        if len(set(labels)) < 2:
            continue
        sil = silhouette_score(dist_matrix, labels, metric='precomputed')
        sil_scores[k] = round(float(sil), 4)

    if sil_scores:
        best_k = max(sil_scores, key=sil_scores.get)
        best_sil = sil_scores[best_k]

        # Also find highest k above 0.25
        above_threshold = {k: s for k, s in sil_scores.items() if s >= 0.25}
        if above_threshold:
            optimal_k = max(above_threshold.keys())
            optimal_sil = sil_scores[optimal_k]
        else:
            optimal_k = best_k
            optimal_sil = best_sil

        print(f"\nClustering results:")
        print(f"  Best silhouette: k={best_k}, sil={best_sil:.4f}")
        print(f"  Optimal (highest k with sil>=0.25): k={optimal_k}, sil={optimal_sil:.4f}")
        print(f"  C657 MIDDLE-only comparison: max sil=0.237")

        # Compare to MIDDLE-only clustering
        if best_sil > 0.237:
            cluster_verdict = "PAIR_CLUSTERS_BETTER"
            print(f"  Verdict: PREFIX x MIDDLE pairs cluster BETTER than MIDDLEs alone")
        else:
            cluster_verdict = "NO_IMPROVEMENT"
            print(f"  Verdict: No improvement over MIDDLE-only clustering")

        # Silhouette for all k
        print(f"\n  Silhouette by k:")
        for k in sorted(sil_scores):
            marker = " <-- best" if k == best_k else (" <-- optimal" if k == optimal_k else "")
            print(f"    k={k:2d}: {sil_scores[k]:.4f}{marker}")

        # Characterize clusters at optimal k
        opt_labels = fcluster(Z, t=optimal_k, criterion='maxclust')
        cluster_profiles = defaultdict(list)
        for idx, (pair, label) in enumerate(zip(pair_labels, opt_labels)):
            cluster_profiles[int(label)].append(pair)

        print(f"\n  Cluster sizes at k={optimal_k}:")
        cluster_summaries = {}
        for cid in sorted(cluster_profiles):
            members = cluster_profiles[cid]
            prefixes_in = Counter(p for p, _ in members)
            middles_in = Counter(m for _, m in members)
            print(f"    Cluster {cid}: {len(members)} pairs, "
                  f"top PFX={prefixes_in.most_common(3)}, "
                  f"top MID={middles_in.most_common(3)}")
            cluster_summaries[cid] = {
                'size': len(members),
                'top_prefixes': dict(prefixes_in.most_common(5)),
                'top_middles': dict(middles_in.most_common(5)),
            }

        clustering_results = {
            'n_clusterable': n_clusterable,
            'best_k': best_k,
            'best_silhouette': best_sil,
            'optimal_k': optimal_k,
            'optimal_silhouette': optimal_sil,
            'c657_reference': 0.237,
            'verdict': cluster_verdict,
            'silhouette_scores': sil_scores,
            'cluster_summaries': cluster_summaries,
        }
    else:
        print("\nNo valid clustering found")
        clustering_results = {'n_clusterable': n_clusterable, 'verdict': 'NO_CLUSTERS'}
else:
    print(f"\nInsufficient pairs for clustering (need >=10, have {n_clusterable})")
    clustering_results = {'n_clusterable': n_clusterable, 'verdict': 'INSUFFICIENT_DATA'}

results['effective_classification'] = {
    'observed_pairs': observed_pairs,
    'effective_pairs': effective_pairs,
    'effective_prefixes': len(eff_prefixes),
    'effective_middles': len(eff_middles),
    'theoretical_max': theoretical_max,
    'sparsity': round(sparsity, 4),
    'expansion_factor': round(expansion_factor, 2),
    'clustering': clustering_results,
}

# ============================================================
# SECTION 5: SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY: PREFIX x MIDDLE Interaction")
print("=" * 70)

print(f"""
INTERACTION EFFECT (Test 5):
  Testable MIDDLEs: {len(testable_middles)}
  Within-MIDDLE between-PREFIX JSD: mean={mean_within_all:.4f}, median={median_within_all:.4f}
  Between-MIDDLE JSD reference (C657): {between_middle_ref:.3f}
  Computed between-MIDDLE JSD: {computed_between:.4f}
  Effect ratio: {effect_ratio:.3f}
  Verdict: {interaction_verdict}

ROLE RECLASSIFICATION (Test 6):
  Pairs analyzed: {len(reduction_data)}
  Mean class reduction: {mean_reduction:.3f}
  EN PREFIX -> EN class: {en_rate_mean:.3f} (n={len(en_prefix_en_class)})
  AX PREFIX -> AX/FQ class: {ax_rate_mean:.3f} (n={len(ax_prefix_ax_class)})
  INFRA PREFIX -> CC class: {infra_rate_mean:.3f} (n={len(infra_prefix_infra_class)})

EFFECTIVE CLASSIFICATION (Test 7):
  Observed pairs: {observed_pairs}
  Effective pairs (>=5 tokens): {effective_pairs}
  Expansion from 404: {expansion_factor:.2f}x
  Sparsity: {sparsity:.3f}
  Clustering: {clustering_results.get('verdict', 'N/A')}
  Best silhouette: {clustering_results.get('best_silhouette', 'N/A')} at k={clustering_results.get('best_k', 'N/A')}
""")

# Save results
output_path = RESULTS_DIR / 'prefix_middle_interaction.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"Results saved to {output_path}")
