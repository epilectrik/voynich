"""
12_mode_clustering.py

Cluster FL MIDDLEs by their GMM component means to discover natural groupings.

Approach:
- Load 2-component GMM means from Test 07
- Hierarchical clustering on (low_mean, high_mean) pairs
- Cut dendrogram at largest gap to find natural k
- Report cluster membership and whether C777 gradient holds within each cluster
- Also fit 3-component GMMs for MIDDLEs that preferred 3, and cluster on 3 means
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist

# Load GMM results
results_dir = Path(__file__).resolve().parent.parent / "results"
with open(results_dir / "07_gaussian_mixture.json") as f:
    gmm_data = json.load(f)

# ============================================================
# Extract 2-component mode coordinates
# ============================================================
middles = []
low_means = []
high_means = []
stages = []
weights_low = []
weights_high = []

for mid, data in gmm_data['per_middle'].items():
    middles.append(mid)
    low_means.append(data['comp_means'][0])
    high_means.append(data['comp_means'][1])
    stages.append(data['stage'])
    weights_low.append(data['comp_weights'][0])
    weights_high.append(data['comp_weights'][1])

print(f"MIDDLEs for clustering: {len(middles)}")
print(f"\n{'MIDDLE':>6} {'Stage':>10} {'Low':>6} {'High':>6} {'wt_L':>6} {'wt_H':>6}")
print("-" * 50)
for i in range(len(middles)):
    print(f"{middles[i]:>6} {stages[i]:>10} {low_means[i]:>6.3f} {high_means[i]:>6.3f} "
          f"{weights_low[i]:>6.3f} {weights_high[i]:>6.3f}")

# ============================================================
# Hierarchical clustering on (low_mean, high_mean)
# ============================================================
X = np.array(list(zip(low_means, high_means)))

# Ward linkage
Z = linkage(X, method='ward')

# Find natural cut: look at merge distances
merge_distances = Z[:, 2]
gaps = np.diff(merge_distances)

print(f"\n{'='*60}")
print("MERGE DISTANCES (hierarchical clustering, Ward)")
for i in range(len(merge_distances)):
    n_clusters = len(middles) - i
    gap = gaps[i] if i < len(gaps) else 0
    marker = " <-- LARGEST GAP" if i < len(gaps) and gaps[i] == max(gaps) else ""
    print(f"  Merge {i+1}: distance={merge_distances[i]:.4f}, "
          f"clusters after={n_clusters-1}, gap_to_next={gap:.4f}{marker}")

# Cut at largest gap
best_gap_idx = np.argmax(gaps)
n_clusters_natural = len(middles) - best_gap_idx - 1
print(f"\nNatural number of clusters: {n_clusters_natural}")

# Also try k=2,3,4,5 and report
print(f"\n{'='*60}")
print("CLUSTER ASSIGNMENTS FOR DIFFERENT k")

cluster_results = {}
for k in range(2, min(7, len(middles))):
    labels = fcluster(Z, k, criterion='maxclust')

    clusters = defaultdict(list)
    for i, label in enumerate(labels):
        clusters[label].append({
            'middle': middles[i],
            'stage': stages[i],
            'low_mean': low_means[i],
            'high_mean': high_means[i],
            'wt_low': weights_low[i],
            'wt_high': weights_high[i],
        })

    print(f"\n--- k={k} ---")
    cluster_detail = {}
    for c in sorted(clusters.keys()):
        members = clusters[c]
        member_names = [m['middle'] for m in members]
        member_stages = [m['stage'] for m in members]
        avg_low = np.mean([m['low_mean'] for m in members])
        avg_high = np.mean([m['high_mean'] for m in members])
        avg_wt_low = np.mean([m['wt_low'] for m in members])

        # Check if C777 stage ordering holds within cluster
        # Sort members by their expected C777 position
        stage_order = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
        sorted_members = sorted(members, key=lambda m: stage_order[m['stage']])
        low_monotonic = all(sorted_members[i]['low_mean'] <= sorted_members[i+1]['low_mean'] + 0.05
                          for i in range(len(sorted_members)-1))
        high_monotonic = all(sorted_members[i]['high_mean'] <= sorted_members[i+1]['high_mean'] + 0.05
                           for i in range(len(sorted_members)-1))

        cluster_detail[str(c)] = {
            'members': member_names,
            'stages': member_stages,
            'avg_low_mean': round(float(avg_low), 3),
            'avg_high_mean': round(float(avg_high), 3),
            'avg_weight_low': round(float(avg_wt_low), 3),
            'low_monotonic': bool(low_monotonic),
            'high_monotonic': bool(high_monotonic),
        }

        mono_str = ""
        if low_monotonic:
            mono_str += " LOW-MONOTONIC"
        if high_monotonic:
            mono_str += " HIGH-MONOTONIC"

        print(f"  Cluster {c}: {member_names}")
        print(f"    stages: {member_stages}")
        print(f"    avg_low={avg_low:.3f}, avg_high={avg_high:.3f}, avg_wt_low={avg_wt_low:.2f}")
        print(f"    {mono_str if mono_str else '  (no monotonic gradient)'}")

    cluster_results[str(k)] = cluster_detail

# ============================================================
# Characterize the natural clustering
# ============================================================
print(f"\n{'='*60}")
print(f"NATURAL CLUSTERING ANALYSIS (k={n_clusters_natural})")

natural_labels = fcluster(Z, n_clusters_natural, criterion='maxclust')
natural_clusters = defaultdict(list)
for i, label in enumerate(natural_labels):
    natural_clusters[label].append(middles[i])

# Characterize each cluster
cluster_profiles = {}
for c in sorted(natural_clusters.keys()):
    members = natural_clusters[c]
    member_data = [(middles.index(m), m) for m in members]

    lows = [low_means[i] for i, _ in member_data]
    highs = [high_means[i] for i, _ in member_data]
    wts = [weights_low[i] for i, _ in member_data]
    stgs = [stages[i] for i, _ in member_data]

    # Characterize
    if np.mean(lows) < 0.05:
        low_type = "BOUNDARY_PINNED_ZERO"
    elif np.mean(lows) > 0.5:
        low_type = "HIGH_FLOOR"
    else:
        low_type = "INTERIOR"

    if np.mean(highs) > 0.95:
        high_type = "BOUNDARY_PINNED_ONE"
    elif np.mean(highs) < 0.7:
        high_type = "LOW_CEILING"
    else:
        high_type = "INTERIOR"

    profile = f"{low_type} / {high_type}"
    cluster_profiles[str(c)] = {
        'members': members,
        'stages': stgs,
        'low_range': [round(min(lows), 3), round(max(lows), 3)],
        'high_range': [round(min(highs), 3), round(max(highs), 3)],
        'avg_weight_low': round(float(np.mean(wts)), 3),
        'profile': profile,
    }

    print(f"\n  Cluster {c}: {members}")
    print(f"    Stages: {stgs}")
    print(f"    Low mode: [{min(lows):.3f} - {max(lows):.3f}] (avg={np.mean(lows):.3f})")
    print(f"    High mode: [{min(highs):.3f} - {max(highs):.3f}] (avg={np.mean(highs):.3f})")
    print(f"    Avg weight(low): {np.mean(wts):.3f}")
    print(f"    Profile: {profile}")

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"  Natural k = {n_clusters_natural}")
print(f"  Cluster profiles:")
for c, p in cluster_profiles.items():
    print(f"    {c}: {p['members']} — {p['profile']}")

result = {
    'n_middles': len(middles),
    'mode_coordinates': {
        middles[i]: {
            'low_mean': low_means[i],
            'high_mean': high_means[i],
            'weight_low': weights_low[i],
            'weight_high': weights_high[i],
            'stage': stages[i],
        }
        for i in range(len(middles))
    },
    'merge_distances': [round(float(d), 4) for d in merge_distances],
    'gaps': [round(float(g), 4) for g in gaps],
    'natural_k': int(n_clusters_natural),
    'cluster_assignments': cluster_results,
    'natural_cluster_profiles': cluster_profiles,
}

out_path = results_dir / "12_mode_clustering.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
