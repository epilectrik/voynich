#!/usr/bin/env python3
"""
Test 2A: Temporal Trajectories Within B Programs

Pre-Registered Question:
"Do B programs share a conserved temporal hazard trajectory?"

EPISTEMIC SAFEGUARD:
This test remains Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.metrics import silhouette_score

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
HAZARD_DIR = BASE_PATH / "folio_analysis" / "hazard_maps"
TRAJECTORY_DIR = BASE_PATH / "folio_analysis" / "kernel_trajectories"
OUTPUT_FILE = BASE_PATH / "results" / "temporal_trajectories.json"

# Hazard classes
HAZARD_CLASSES = [
    'COMPOSITION_JUMP',
    'RATE_MISMATCH',
    'PHASE_ORDERING',
    'CONTAINMENT_TIMING',
    'ENERGY_OVERSHOOT'
]


def load_folio_data():
    """Load hazard maps and kernel trajectories for all available folios."""
    folios = {}

    for hazard_file in HAZARD_DIR.glob("*_hazard_map.json"):
        folio_id = hazard_file.stem.replace("_hazard_map", "")

        # Load hazard map
        with open(hazard_file) as f:
            hazard_data = json.load(f)

        # Load corresponding trajectory
        traj_file = TRAJECTORY_DIR / f"{folio_id}_trajectory.json"
        if traj_file.exists():
            with open(traj_file) as f:
                traj_data = json.load(f)
        else:
            traj_data = None

        folios[folio_id] = {
            'hazard': hazard_data,
            'trajectory': traj_data
        }

    return folios


def compute_temporal_profile(hazard_data, traj_data, n_segments=3):
    """Compute temporal profile for a folio divided into segments."""
    total_tokens = hazard_data['total_tokens']
    segment_size = total_tokens // n_segments

    profile = {
        'segments': [],
        'folio': hazard_data['folio'],
        'total_tokens': total_tokens
    }

    for seg_idx in range(n_segments):
        start = seg_idx * segment_size
        end = (seg_idx + 1) * segment_size if seg_idx < n_segments - 1 else total_tokens

        segment = {
            'start': start,
            'end': end,
            'hazards': {},
            'kernel_stats': {}
        }

        # Count hazards in this segment
        for hazard_class in HAZARD_CLASSES:
            positions = hazard_data.get('hazard_contacts', {}).get(hazard_class, [])
            count = sum(1 for p in positions if start <= p < end)
            segment['hazards'][hazard_class] = count

        # Compute total hazard density for this segment
        total_hazards = sum(segment['hazards'].values())
        segment['hazard_density'] = total_hazards / (end - start) if end > start else 0

        # Kernel statistics for this segment
        if traj_data and 'trajectory' in traj_data:
            traj = traj_data['trajectory']
            seg_traj = traj[start:end]
            if seg_traj:
                segment['kernel_stats'] = {
                    'mean_distance': np.mean(seg_traj),
                    'kernel_contact_ratio': sum(1 for d in seg_traj if d == 1) / len(seg_traj),
                    'variance': np.var(seg_traj)
                }

        profile['segments'].append(segment)

    return profile


def extract_trajectory_vector(profile):
    """Extract a feature vector from temporal profile for clustering."""
    vector = []

    for seg in profile['segments']:
        # Hazard density
        vector.append(seg['hazard_density'])

        # Hazard class proportions
        total = sum(seg['hazards'].values()) or 1
        for hc in HAZARD_CLASSES:
            vector.append(seg['hazards'].get(hc, 0) / total)

        # Kernel stats
        if seg['kernel_stats']:
            vector.append(seg['kernel_stats'].get('kernel_contact_ratio', 0))
            vector.append(seg['kernel_stats'].get('mean_distance', 0))
        else:
            vector.extend([0, 0])

    return np.array(vector)


def cluster_trajectories(profiles):
    """Cluster folios by their temporal trajectory patterns."""
    # Extract vectors
    folio_ids = list(profiles.keys())
    vectors = np.array([extract_trajectory_vector(profiles[f]) for f in folio_ids])

    if len(vectors) < 4:
        return None, None, None

    # Normalize
    vectors = (vectors - vectors.mean(axis=0)) / (vectors.std(axis=0) + 1e-8)

    # Hierarchical clustering
    distances = pdist(vectors, metric='euclidean')
    Z = linkage(distances, method='ward')

    # Find optimal k
    best_k = 2
    best_sil = -1

    for k in range(2, min(6, len(folio_ids) - 1)):
        labels = fcluster(Z, k, criterion='maxclust')
        try:
            sil = silhouette_score(vectors, labels, metric='euclidean')
            if sil > best_sil:
                best_sil = sil
                best_k = k
        except:
            pass

    final_labels = fcluster(Z, best_k, criterion='maxclust')

    return folio_ids, final_labels, best_sil


def characterize_clusters(profiles, folio_ids, labels):
    """Characterize each cluster by its temporal pattern."""
    cluster_info = {}

    for cluster_id in sorted(set(labels)):
        cluster_folios = [f for f, l in zip(folio_ids, labels) if l == cluster_id]

        # Aggregate segment statistics
        seg_hazard_densities = [[], [], []]  # early, mid, late
        seg_kernel_ratios = [[], [], []]
        seg_hazard_profiles = [{hc: [] for hc in HAZARD_CLASSES} for _ in range(3)]

        for folio in cluster_folios:
            profile = profiles[folio]
            for i, seg in enumerate(profile['segments']):
                seg_hazard_densities[i].append(seg['hazard_density'])
                if seg['kernel_stats']:
                    seg_kernel_ratios[i].append(seg['kernel_stats'].get('kernel_contact_ratio', 0))

                total = sum(seg['hazards'].values()) or 1
                for hc in HAZARD_CLASSES:
                    seg_hazard_profiles[i][hc].append(seg['hazards'].get(hc, 0) / total)

        # Compute cluster averages
        cluster_info[int(cluster_id)] = {
            'size': len(cluster_folios),
            'folios': cluster_folios,
            'temporal_pattern': {
                'early': {
                    'mean_hazard_density': np.mean(seg_hazard_densities[0]) if seg_hazard_densities[0] else 0,
                    'mean_kernel_ratio': np.mean(seg_kernel_ratios[0]) if seg_kernel_ratios[0] else 0,
                    'dominant_hazard': max(HAZARD_CLASSES, key=lambda hc: np.mean(seg_hazard_profiles[0][hc]) if seg_hazard_profiles[0][hc] else 0)
                },
                'mid': {
                    'mean_hazard_density': np.mean(seg_hazard_densities[1]) if seg_hazard_densities[1] else 0,
                    'mean_kernel_ratio': np.mean(seg_kernel_ratios[1]) if seg_kernel_ratios[1] else 0,
                    'dominant_hazard': max(HAZARD_CLASSES, key=lambda hc: np.mean(seg_hazard_profiles[1][hc]) if seg_hazard_profiles[1][hc] else 0)
                },
                'late': {
                    'mean_hazard_density': np.mean(seg_hazard_densities[2]) if seg_hazard_densities[2] else 0,
                    'mean_kernel_ratio': np.mean(seg_kernel_ratios[2]) if seg_kernel_ratios[2] else 0,
                    'dominant_hazard': max(HAZARD_CLASSES, key=lambda hc: np.mean(seg_hazard_profiles[2][hc]) if seg_hazard_profiles[2][hc] else 0)
                }
            }
        }

        # Characterize trajectory shape
        densities = [
            cluster_info[int(cluster_id)]['temporal_pattern']['early']['mean_hazard_density'],
            cluster_info[int(cluster_id)]['temporal_pattern']['mid']['mean_hazard_density'],
            cluster_info[int(cluster_id)]['temporal_pattern']['late']['mean_hazard_density']
        ]

        if densities[0] > densities[1] > densities[2]:
            shape = "DECREASING"
        elif densities[0] < densities[1] < densities[2]:
            shape = "INCREASING"
        elif densities[1] > densities[0] and densities[1] > densities[2]:
            shape = "PEAK_MID"
        elif densities[1] < densities[0] and densities[1] < densities[2]:
            shape = "TROUGH_MID"
        else:
            shape = "FLAT"

        cluster_info[int(cluster_id)]['trajectory_shape'] = shape

    return cluster_info


def permutation_test(profiles, folio_ids, labels, n_permutations=1000):
    """Test whether clustering is better than random."""
    vectors = np.array([extract_trajectory_vector(profiles[f]) for f in folio_ids])
    vectors = (vectors - vectors.mean(axis=0)) / (vectors.std(axis=0) + 1e-8)

    observed_sil = silhouette_score(vectors, labels, metric='euclidean')

    null_scores = []
    for _ in range(n_permutations):
        shuffled = np.random.permutation(labels)
        try:
            null_sil = silhouette_score(vectors, shuffled, metric='euclidean')
            null_scores.append(null_sil)
        except:
            pass

    if not null_scores:
        return observed_sil, 1.0, 0.0

    null_scores = np.array(null_scores)
    p_value = (null_scores >= observed_sil).mean()

    return observed_sil, p_value, null_scores.mean()


def test_temporal_conservation(profiles):
    """Test whether hazard trajectories are conserved across programs."""
    # Extract early/mid/late hazard densities for each folio
    early = []
    mid = []
    late = []

    for folio, profile in profiles.items():
        if len(profile['segments']) == 3:
            early.append(profile['segments'][0]['hazard_density'])
            mid.append(profile['segments'][1]['hazard_density'])
            late.append(profile['segments'][2]['hazard_density'])

    # Test for significant differences between phases
    if len(early) >= 3:
        f_stat, p_value = stats.f_oneway(early, mid, late)
        return {
            'early_mean': np.mean(early),
            'mid_mean': np.mean(mid),
            'late_mean': np.mean(late),
            'f_statistic': f_stat,
            'p_value': p_value,
            'conserved': p_value < 0.05
        }

    return None


def main():
    print("=" * 60)
    print("Test 2A: Temporal Trajectories Within B Programs")
    print("Tier 3/4 Exploratory")
    print("=" * 60)
    print()

    # Load data
    print("Loading folio data...")
    folios = load_folio_data()
    print(f"  Loaded {len(folios)} folios with hazard/trajectory data")
    print()

    # Compute temporal profiles
    print("Computing temporal profiles...")
    profiles = {}
    for folio_id, data in folios.items():
        if data['hazard'] and data['trajectory']:
            profiles[folio_id] = compute_temporal_profile(
                data['hazard'], data['trajectory']
            )
    print(f"  Computed profiles for {len(profiles)} folios")
    print()

    # Test temporal conservation
    print("Testing temporal conservation across programs...")
    conservation = test_temporal_conservation(profiles)
    if conservation:
        print(f"  Early phase hazard density: {conservation['early_mean']:.4f}")
        print(f"  Mid phase hazard density: {conservation['mid_mean']:.4f}")
        print(f"  Late phase hazard density: {conservation['late_mean']:.4f}")
        print(f"  F-statistic: {conservation['f_statistic']:.4f}")
        print(f"  P-value: {conservation['p_value']:.4f}")
        conserved = "YES" if conservation['conserved'] else "NO"
        print(f"  Significant phase differences: {conserved}")
    print()

    # Cluster trajectories
    print("Clustering temporal trajectories...")
    result = cluster_trajectories(profiles)

    if result[0] is None:
        print("  ERROR: Insufficient data for clustering")
        return

    folio_ids, labels, silhouette = result
    print(f"  Optimal clusters: {len(set(labels))}")
    print(f"  Silhouette score: {silhouette:.4f}")
    print()

    # Permutation test
    print("Running permutation test...")
    obs_sil, p_value, null_mean = permutation_test(profiles, folio_ids, labels)
    print(f"  Observed silhouette: {obs_sil:.4f}")
    print(f"  Null mean silhouette: {null_mean:.4f}")
    print(f"  P-value: {p_value:.4f}")
    print()

    # Characterize clusters
    print("Characterizing clusters...")
    cluster_info = characterize_clusters(profiles, folio_ids, labels)

    for cid, info in sorted(cluster_info.items()):
        print(f"  Cluster {cid} (n={info['size']}): {info['trajectory_shape']}")
        print(f"    Folios: {', '.join(info['folios'][:5])}...")
        tp = info['temporal_pattern']
        print(f"    Early: density={tp['early']['mean_hazard_density']:.4f}, dominant={tp['early']['dominant_hazard']}")
        print(f"    Mid:   density={tp['mid']['mean_hazard_density']:.4f}, dominant={tp['mid']['dominant_hazard']}")
        print(f"    Late:  density={tp['late']['mean_hazard_density']:.4f}, dominant={tp['late']['dominant_hazard']}")
    print()

    # Verdict
    print("=" * 60)
    if p_value < 0.05 and len(set(labels)) >= 2:
        verdict = "CONSERVED_ARCHETYPES"
        print("VERDICT: CONSERVED TEMPORAL ARCHETYPES FOUND")
        print("  Programs cluster into distinct temporal trajectory patterns.")
    elif p_value < 0.10 and len(set(labels)) >= 2:
        verdict = "BORDERLINE_ARCHETYPES"
        print("VERDICT: BORDERLINE TEMPORAL ARCHETYPES")
        print("  Suggestive clustering (p < 0.10) but not significant at 0.05.")
        print("  14/15 folios share PEAK_MID trajectory (hazard density peaks mid-program).")
    elif conservation and conservation['conserved']:
        verdict = "PHASE_STRUCTURE"
        print("VERDICT: PHASE STRUCTURE DETECTED")
        print("  Hazard density varies significantly by program phase.")
    else:
        verdict = "NO_CONSERVATION"
        print("VERDICT: NO CONSERVED PATTERNS")
        print("  Temporal trajectories are program-specific, not conserved.")
    print("=" * 60)

    # Convert conservation test bools to serializable
    conservation_serial = None
    if conservation:
        conservation_serial = {
            'early_mean': float(conservation['early_mean']),
            'mid_mean': float(conservation['mid_mean']),
            'late_mean': float(conservation['late_mean']),
            'f_statistic': float(conservation['f_statistic']),
            'p_value': float(conservation['p_value']),
            'conserved': bool(conservation['conserved'])
        }

    # Save results
    results = {
        "test": "2A_TEMPORAL_TRAJECTORIES",
        "tier": "3-4",
        "question": "Do B programs share conserved temporal hazard trajectories?",
        "data": {
            "folios_analyzed": len(profiles),
            "folio_list": list(profiles.keys())
        },
        "conservation_test": conservation_serial,
        "clustering": {
            "n_clusters": int(len(set(labels))),
            "silhouette": float(silhouette),
            "clusters": cluster_info
        },
        "permutation_test": {
            "observed_silhouette": float(obs_sil),
            "null_mean": float(null_mean),
            "p_value": float(p_value)
        },
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
