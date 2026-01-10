#!/usr/bin/env python3
"""
P1: Folio Personality Clusters

If we cluster folios by ALL burden indices, what natural groupings emerge?

Questions:
1. Do folios cluster by system dominance?
2. Are there mixed-system anomalies?
3. Do natural clusters map to known categories (sections, quires)?

Output: results/folio_personality_clusters.json
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"

# Output
OUTPUT = RESULTS / "folio_personality_clusters.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_feature_matrix(unified):
    """
    Build feature matrix from unified profiles.
    Uses: ht_density, cognitive_burden, execution_tension (where available)
    """
    folios = []
    features = []

    for folio, profile in unified['profiles'].items():
        # Core features available for all folios
        ht_density = profile.get('ht_density', 0)
        ht_percentile = profile.get('ht_percentile', 50) / 100.0  # Normalize to 0-1

        # Burden indices
        burden = profile.get('burden_indices', {})
        cognitive_burden = burden.get('cognitive_burden', 0)

        # System indicator (one-hot)
        system = profile.get('system', 'UNKNOWN')
        is_A = 1 if system == 'A' else 0
        is_B = 1 if system == 'B' else 0
        is_AZC = 1 if system == 'AZC' else 0

        # HT status (ordinal)
        ht_status = profile.get('ht_status', 'NORMAL')
        ht_ordinal = 2 if ht_status == 'HOTSPOT' else 0 if ht_status == 'DESERT' else 1

        # For B folios, add execution metrics
        b_metrics = profile.get('b_metrics', {})
        execution_tension = burden.get('execution_tension')
        hazard_density = b_metrics.get('hazard_density', 0) if b_metrics else 0
        escape_density = b_metrics.get('qo_density', 0) if b_metrics else 0

        # Build feature vector (use 0 for missing values)
        feature_vec = [
            ht_density,
            cognitive_burden if cognitive_burden is not None else 0,
            execution_tension if execution_tension is not None else 0,
            is_A, is_B, is_AZC,
            ht_ordinal,
            hazard_density,
            escape_density
        ]

        folios.append(folio)
        features.append(feature_vec)

    return np.array(folios), np.array(features)


def find_optimal_k(X, max_k=10):
    """
    Find optimal number of clusters using silhouette score.
    """
    scores = []
    for k in range(2, min(max_k + 1, len(X))):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        scores.append((k, score))

    best_k = max(scores, key=lambda x: x[1])[0]
    return best_k, scores


def cluster_folios(folios, features, n_clusters=None):
    """
    Cluster folios using K-Means.
    """
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # Find optimal k if not specified
    if n_clusters is None:
        n_clusters, silhouette_scores = find_optimal_k(X_scaled)
    else:
        silhouette_scores = []

    # K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Also do hierarchical clustering for comparison
    linkage_matrix = linkage(X_scaled, method='ward')

    return {
        'labels': labels,
        'n_clusters': n_clusters,
        'silhouette_scores': silhouette_scores,
        'centers': kmeans.cluster_centers_,
        'linkage_matrix': linkage_matrix.tolist()
    }


def analyze_clusters(folios, labels, unified):
    """
    Analyze what defines each cluster.
    """
    n_clusters = max(labels) + 1
    clusters = defaultdict(list)

    for folio, label in zip(folios, labels):
        clusters[int(label)].append(folio)

    analysis = {}
    for cluster_id in range(n_clusters):
        cluster_folios = clusters[cluster_id]

        # Get profiles for this cluster
        profiles = [unified['profiles'][f] for f in cluster_folios]

        # System composition
        systems = Counter(p['system'] for p in profiles)

        # HT statistics
        ht_densities = [p['ht_density'] for p in profiles if p.get('ht_density') is not None]
        ht_statuses = Counter(p.get('ht_status', 'NORMAL') for p in profiles)

        # Burden indices (where available)
        cognitive_burdens = [p['burden_indices']['cognitive_burden'] for p in profiles
                           if p['burden_indices'].get('cognitive_burden') is not None]
        tensions = [p['burden_indices']['execution_tension'] for p in profiles
                   if p['burden_indices'].get('execution_tension') is not None]

        # Quire distribution
        quires = Counter(p.get('quire', 'UNKNOWN') for p in profiles)

        analysis[cluster_id] = {
            'n_folios': len(cluster_folios),
            'folios': sorted(cluster_folios),
            'systems': dict(systems),
            'dominant_system': systems.most_common(1)[0][0] if systems else 'UNKNOWN',
            'ht_stats': {
                'mean': round(float(np.mean(ht_densities)), 4) if ht_densities else None,
                'std': round(float(np.std(ht_densities)), 4) if ht_densities else None,
                'statuses': dict(ht_statuses)
            },
            'burden_stats': {
                'cognitive_mean': round(float(np.mean(cognitive_burdens)), 3) if cognitive_burdens else None,
                'tension_mean': round(float(np.mean(tensions)), 3) if tensions else None,
                'n_b_folios': len(tensions)
            },
            'quire_distribution': dict(quires)
        }

    return analysis


def identify_cluster_character(analysis):
    """
    Assign character labels to each cluster based on dominant features.
    """
    characters = {}

    for cluster_id, data in analysis.items():
        traits = []

        # System dominance
        dom_sys = data['dominant_system']
        sys_purity = data['systems'].get(dom_sys, 0) / data['n_folios']
        if sys_purity > 0.8:
            traits.append(f"{dom_sys}-pure")
        elif sys_purity > 0.5:
            traits.append(f"{dom_sys}-dominant")
        else:
            traits.append("mixed-system")

        # HT level
        ht_mean = data['ht_stats']['mean']
        if ht_mean and ht_mean > 0.18:
            traits.append("high-HT")
        elif ht_mean and ht_mean < 0.10:
            traits.append("low-HT")

        # Tension level (B only)
        tension = data['burden_stats']['tension_mean']
        if tension and tension > 0.5:
            traits.append("high-tension")
        elif tension and tension < -0.5:
            traits.append("low-tension")

        # Hotspot/desert presence
        hotspots = data['ht_stats']['statuses'].get('HOTSPOT', 0)
        deserts = data['ht_stats']['statuses'].get('DESERT', 0)
        if hotspots > 0:
            traits.append(f"{hotspots}-hotspots")
        if deserts > 0:
            traits.append(f"{deserts}-deserts")

        characters[cluster_id] = {
            'traits': traits,
            'label': " | ".join(traits) if traits else "uncharacterized"
        }

    return characters


def test_cluster_validity(folios, labels, unified):
    """
    Test if clusters are meaningful beyond random.
    """
    # Test: Do clusters separate systems?
    systems = [unified['profiles'][f]['system'] for f in folios]
    system_labels = {'A': 0, 'B': 1, 'AZC': 2}
    system_numeric = [system_labels.get(s, -1) for s in systems]

    # Chi-squared test
    contingency = np.zeros((max(labels) + 1, 3))
    for label, sys in zip(labels, system_numeric):
        if sys >= 0:
            contingency[label, sys] += 1

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    # Test: Do clusters separate HT levels?
    ht_values = [unified['profiles'][f].get('ht_density', 0) for f in folios]

    # Kruskal-Wallis for HT by cluster
    ht_by_cluster = defaultdict(list)
    for label, ht in zip(labels, ht_values):
        ht_by_cluster[int(label)].append(ht)

    ht_groups = [v for v in ht_by_cluster.values() if len(v) >= 3]
    if len(ht_groups) >= 2:
        h_stat, p_ht = stats.kruskal(*ht_groups)
    else:
        h_stat, p_ht = 0, 1.0

    return {
        'system_separation': {
            'chi2': round(float(chi2), 2),
            'p_value': round(float(p_value), 4),
            'significant': bool(p_value < 0.05)
        },
        'ht_separation': {
            'h_statistic': round(float(h_stat), 2),
            'p_value': round(float(p_ht), 4),
            'significant': bool(p_ht < 0.05)
        }
    }


def find_anomalous_folios(folios, labels, unified, analysis):
    """
    Find folios that are anomalous within their cluster.
    """
    anomalies = []

    for cluster_id, data in analysis.items():
        cluster_mask = labels == cluster_id
        cluster_folios = [f for f, m in zip(folios, cluster_mask) if m]

        dom_sys = data['dominant_system']

        # Find folios that don't match dominant system
        for folio in cluster_folios:
            profile = unified['profiles'][folio]
            if profile['system'] != dom_sys:
                anomalies.append({
                    'folio': folio,
                    'cluster': cluster_id,
                    'expected_system': dom_sys,
                    'actual_system': profile['system'],
                    'ht_density': profile.get('ht_density'),
                    'ht_status': profile.get('ht_status'),
                    'reason': f"{profile['system']} folio in {dom_sys}-dominant cluster"
                })

    return anomalies


def main():
    print("=" * 70)
    print("P1: Folio Personality Clusters")
    print("=" * 70)

    # Load data
    print("\n[1] Loading unified profiles...")
    unified = load_json(UNIFIED_PROFILES)
    print(f"    Total folios: {len(unified['profiles'])}")

    # Build feature matrix
    print("\n[2] Building feature matrix...")
    folios, features = build_feature_matrix(unified)
    print(f"    Features per folio: {features.shape[1]}")
    print(f"    Feature names: [ht_density, cognitive_burden, execution_tension,")
    print(f"                    is_A, is_B, is_AZC, ht_ordinal, hazard, escape]")

    # Cluster
    print("\n[3] Clustering folios...")
    clustering = cluster_folios(folios, features)
    n_clusters = clustering['n_clusters']
    labels = clustering['labels']
    print(f"    Optimal k: {n_clusters}")

    if clustering['silhouette_scores']:
        print(f"    Silhouette scores:")
        for k, score in clustering['silhouette_scores']:
            marker = " <- selected" if k == n_clusters else ""
            print(f"      k={k}: {score:.3f}{marker}")

    # Analyze clusters
    print("\n[4] Analyzing cluster composition...")
    analysis = analyze_clusters(folios, labels, unified)

    for cluster_id in sorted(analysis.keys()):
        data = analysis[cluster_id]
        print(f"\n    Cluster {cluster_id}: {data['n_folios']} folios")
        print(f"      Systems: {data['systems']}")
        print(f"      Dominant: {data['dominant_system']}")
        if data['ht_stats']['mean']:
            print(f"      HT: mean={data['ht_stats']['mean']:.3f}, statuses={data['ht_stats']['statuses']}")
        if data['burden_stats']['tension_mean']:
            print(f"      Tension: mean={data['burden_stats']['tension_mean']:.3f} (n={data['burden_stats']['n_b_folios']})")

    # Character labels
    print("\n[5] Assigning cluster characters...")
    characters = identify_cluster_character(analysis)

    for cluster_id in sorted(characters.keys()):
        print(f"    Cluster {cluster_id}: {characters[cluster_id]['label']}")

    # Validity tests
    print("\n[6] Testing cluster validity...")
    validity = test_cluster_validity(folios, labels, unified)

    sys_sep = validity['system_separation']
    print(f"    System separation: chi2={sys_sep['chi2']}, p={sys_sep['p_value']}")
    print(f"      {'*** SIGNIFICANT' if sys_sep['significant'] else 'Not significant'}")

    ht_sep = validity['ht_separation']
    print(f"    HT separation: H={ht_sep['h_statistic']}, p={ht_sep['p_value']}")
    print(f"      {'*** SIGNIFICANT' if ht_sep['significant'] else 'Not significant'}")

    # Find anomalies
    print("\n[7] Finding anomalous folios...")
    anomalies = find_anomalous_folios(folios, labels, unified, analysis)

    if anomalies:
        print(f"    Found {len(anomalies)} anomalies:")
        for a in anomalies[:10]:  # Show first 10
            print(f"      {a['folio']}: {a['reason']}")
    else:
        print("    No anomalies found")

    # Key findings
    print("\n[8] Key findings...")
    findings = []

    if validity['system_separation']['significant']:
        findings.append({
            'finding': 'Clusters separate by system',
            'chi2': sys_sep['chi2'],
            'p_value': sys_sep['p_value'],
            'interpretation': 'System identity drives clustering'
        })

    if validity['ht_separation']['significant']:
        findings.append({
            'finding': 'Clusters separate by HT level',
            'h_statistic': ht_sep['h_statistic'],
            'p_value': ht_sep['p_value'],
            'interpretation': 'HT density is a major clustering dimension'
        })

    if anomalies:
        findings.append({
            'finding': f'{len(anomalies)} cross-system anomalies',
            'interpretation': 'Some folios cluster by HT/burden rather than system'
        })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[9] Saving output...")

    output = {
        'metadata': {
            'analysis': 'P1 - Folio Personality Clusters',
            'description': 'Unsupervised clustering of folios by burden indices',
            'n_folios': len(folios),
            'n_features': features.shape[1],
            'n_clusters': n_clusters
        },
        'clustering': {
            'n_clusters': n_clusters,
            'silhouette_scores': clustering['silhouette_scores'],
            'labels': {str(f): int(l) for f, l in zip(folios, labels)}
        },
        'cluster_analysis': analysis,
        'cluster_characters': characters,
        'validity_tests': validity,
        'anomalies': anomalies,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("P1 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
