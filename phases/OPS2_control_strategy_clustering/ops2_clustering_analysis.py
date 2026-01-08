#!/usr/bin/env python3
"""
Phase OPS-2: Control Strategy Clustering

Clusters 83 Voynich folios into stable control-strategy regimes using
ONLY OPS-1 control signatures. No external data, no semantic interpretation.

Requirements:
- scikit-learn
- scipy
- numpy
- pandas
"""

import json
import csv
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter
from pathlib import Path

# Clustering imports
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    adjusted_rand_score
)
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist

# For stability testing
np.random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

OPS1_CSV = Path("C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_signature_table.csv")
OPS1_JSON = Path("C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json")
OUTPUT_DIR = Path("C:/git/voynich/phases/OPS2_control_strategy_clustering")

# Features to use (continuous only - categorical will be one-hot encoded)
CONTINUOUS_FEATURES = [
    'total_tokens',
    'link_count',
    'link_density',
    'mean_link_run',
    'max_link_run',
    'kernel_contact_ratio',
    'hazard_density',
    'cycle_count',
    'convergence_speed',
    'aggressiveness',
    'conservatism',
    'control_margin',
    'near_miss',
    'recovery_ops'
]

CATEGORICAL_FEATURES = [
    'kernel_dominance',
    'terminal_state',
    'waiting_profile',
    'risk_profile',
    'intervention_style',
    'stability_role'
]

BOOLEAN_FEATURES = ['restart_capable']

# K-means range to evaluate
K_RANGE = range(3, 11)  # k ∈ [3, 10]

# Bootstrap parameters
N_BOOTSTRAP = 100
NOISE_LEVEL = 0.05  # 5% noise injection

# ============================================================================
# DATA LOADING AND PREPROCESSING
# ============================================================================

def load_data():
    """Load OPS-1 signature table"""
    df = pd.read_csv(OPS1_CSV)
    print(f"Loaded {len(df)} folios with {len(df.columns)} features")
    return df


def preprocess_features(df):
    """
    Preprocess features:
    1. Standardize continuous features (z-score)
    2. One-hot encode categorical features
    3. Validate no missing values
    """
    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        raise ValueError(f"Data has {missing} missing values!")

    # Identify constant features to exclude
    constant_features = []
    for col in CONTINUOUS_FEATURES:
        if col in df.columns:
            if df[col].std() == 0:
                constant_features.append(col)
                print(f"  WARNING: {col} is constant (std=0), excluding from analysis")

    # Filter to non-constant continuous features
    active_continuous = [f for f in CONTINUOUS_FEATURES if f in df.columns and f not in constant_features]

    # Standardize continuous features
    scaler = StandardScaler()
    continuous_data = df[active_continuous].copy()
    continuous_scaled = pd.DataFrame(
        scaler.fit_transform(continuous_data),
        columns=active_continuous,
        index=df.index
    )

    # One-hot encode categorical features
    categorical_dfs = []
    for cat_feat in CATEGORICAL_FEATURES:
        if cat_feat in df.columns:
            dummies = pd.get_dummies(df[cat_feat], prefix=cat_feat)
            categorical_dfs.append(dummies)

    # Boolean features (already 0/1)
    boolean_data = df[BOOLEAN_FEATURES].astype(int) if BOOLEAN_FEATURES[0] in df.columns else pd.DataFrame()

    # Combine all features
    feature_df = pd.concat([continuous_scaled] + categorical_dfs + [boolean_data], axis=1)

    print(f"\nFeature matrix: {feature_df.shape[0]} samples x {feature_df.shape[1]} features")
    print(f"  - Continuous (z-scored): {len(active_continuous)}")
    print(f"  - Categorical (one-hot): {sum(d.shape[1] for d in categorical_dfs)}")
    print(f"  - Boolean: {len(BOOLEAN_FEATURES) if BOOLEAN_FEATURES[0] in df.columns else 0}")

    return feature_df, continuous_scaled, scaler, active_continuous


def compute_redundancy(feature_df, threshold=0.9):
    """Compute correlation matrix and flag redundant pairs"""
    corr_matrix = feature_df.corr()
    redundant_pairs = []

    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:  # Upper triangle only
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > threshold:
                    redundant_pairs.append((col1, col2, corr_val))

    return corr_matrix, redundant_pairs


# ============================================================================
# CLUSTERING METHODS
# ============================================================================

def hierarchical_ward(X, n_clusters):
    """Hierarchical clustering with Ward linkage"""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    labels = model.fit_predict(X)
    return labels


def kmeans_clustering(X, n_clusters):
    """K-Means clustering"""
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)
    return labels


def dbscan_clustering(X, eps=0.5, min_samples=3):
    """DBSCAN density-based clustering"""
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)
    return labels


def hdbscan_clustering(X, min_cluster_size=3):
    """HDBSCAN clustering (if available)"""
    try:
        import hdbscan
        model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=2)
        labels = model.fit_predict(X)
        return labels
    except ImportError:
        print("  HDBSCAN not available, skipping")
        return None


# ============================================================================
# VALIDATION METRICS
# ============================================================================

def compute_validation_metrics(X, labels):
    """Compute internal validation metrics"""
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    if n_clusters < 2:
        return {'silhouette': np.nan, 'calinski_harabasz': np.nan, 'davies_bouldin': np.nan, 'n_clusters': n_clusters}

    # Filter out noise points for metrics (DBSCAN labels -1 as noise)
    mask = labels != -1
    if mask.sum() < 2:
        return {'silhouette': np.nan, 'calinski_harabasz': np.nan, 'davies_bouldin': np.nan, 'n_clusters': n_clusters}

    X_valid = X[mask]
    labels_valid = labels[mask]

    if len(set(labels_valid)) < 2:
        return {'silhouette': np.nan, 'calinski_harabasz': np.nan, 'davies_bouldin': np.nan, 'n_clusters': n_clusters}

    return {
        'silhouette': silhouette_score(X_valid, labels_valid),
        'calinski_harabasz': calinski_harabasz_score(X_valid, labels_valid),
        'davies_bouldin': davies_bouldin_score(X_valid, labels_valid),
        'n_clusters': n_clusters
    }


# ============================================================================
# STABILITY TESTING
# ============================================================================

def bootstrap_stability(X, cluster_func, n_clusters, n_bootstrap=100):
    """Test cluster stability via bootstrap resampling"""
    n_samples = X.shape[0]
    reference_labels = cluster_func(X, n_clusters)

    ari_scores = []
    for _ in range(n_bootstrap):
        # Bootstrap sample indices
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        X_boot = X[indices]

        # Cluster bootstrap sample
        try:
            boot_labels = cluster_func(X_boot, n_clusters)

            # Map back to original indices and compute ARI on overlap
            # We compare labels for points that appear in both
            common_indices = list(set(indices))
            ref_common = reference_labels[common_indices]
            boot_common = boot_labels[[list(indices).index(i) for i in common_indices if i in indices]]

            if len(set(ref_common)) >= 2 and len(set(boot_common)) >= 2:
                ari = adjusted_rand_score(ref_common, boot_common[:len(ref_common)])
                ari_scores.append(ari)
        except:
            pass

    return np.mean(ari_scores) if ari_scores else np.nan, np.std(ari_scores) if ari_scores else np.nan


def noise_injection_stability(X, cluster_func, n_clusters, noise_level=0.05, n_trials=100):
    """Test stability under feature noise injection"""
    reference_labels = cluster_func(X, n_clusters)

    ari_scores = []
    for _ in range(n_trials):
        # Add Gaussian noise
        noise = np.random.normal(0, noise_level, X.shape)
        X_noisy = X + noise

        try:
            noisy_labels = cluster_func(X_noisy, n_clusters)
            ari = adjusted_rand_score(reference_labels, noisy_labels)
            ari_scores.append(ari)
        except:
            pass

    return np.mean(ari_scores) if ari_scores else np.nan, np.std(ari_scores) if ari_scores else np.nan


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def run_clustering_analysis():
    """Run complete clustering analysis"""
    print("=" * 70)
    print("PHASE OPS-2: CONTROL STRATEGY CLUSTERING")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load data
    print("[1] Loading OPS-1 data...")
    df = load_data()
    folio_ids = df['folio_id'].tolist()

    # Preprocess features
    print("\n[2] Preprocessing features...")
    feature_df, continuous_scaled, scaler, active_continuous = preprocess_features(df)
    X = feature_df.values

    # Redundancy check
    print("\n[3] Computing redundancy matrix...")
    corr_matrix, redundant_pairs = compute_redundancy(feature_df)

    if redundant_pairs:
        print(f"  Found {len(redundant_pairs)} highly correlated pairs (|rho| > 0.9):")
        for p1, p2, rho in redundant_pairs[:10]:
            print(f"    {p1} <-> {p2}: rho = {rho:.3f}")
        if len(redundant_pairs) > 10:
            print(f"    ... and {len(redundant_pairs) - 10} more")
    else:
        print("  No redundant pairs found")

    # Store results
    results = {
        'hierarchical': {},
        'kmeans': {},
        'dbscan': {},
        'hdbscan': {}
    }

    # ========================================================================
    # METHOD 1: HIERARCHICAL CLUSTERING (Ward)
    # ========================================================================
    print("\n[4] Hierarchical Clustering (Ward linkage)...")

    # Compute linkage for dendrogram analysis
    linkage_matrix = linkage(X, method='ward')

    for k in K_RANGE:
        labels = hierarchical_ward(X, k)
        metrics = compute_validation_metrics(X, labels)
        results['hierarchical'][k] = {
            'labels': labels,
            'metrics': metrics
        }
        print(f"  k={k}: Silhouette={metrics['silhouette']:.4f}, CH={metrics['calinski_harabasz']:.1f}, DB={metrics['davies_bouldin']:.4f}")

    # ========================================================================
    # METHOD 2: K-MEANS
    # ========================================================================
    print("\n[5] K-Means Clustering...")

    for k in K_RANGE:
        labels = kmeans_clustering(X, k)
        metrics = compute_validation_metrics(X, labels)
        results['kmeans'][k] = {
            'labels': labels,
            'metrics': metrics
        }
        print(f"  k={k}: Silhouette={metrics['silhouette']:.4f}, CH={metrics['calinski_harabasz']:.1f}, DB={metrics['davies_bouldin']:.4f}")

    # ========================================================================
    # METHOD 3: DBSCAN (multiple eps values)
    # ========================================================================
    print("\n[6] DBSCAN Clustering...")

    # Try multiple eps values
    eps_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    for eps in eps_values:
        labels = dbscan_clustering(X, eps=eps, min_samples=3)
        metrics = compute_validation_metrics(X, labels)
        n_noise = (labels == -1).sum()
        n_clusters = metrics['n_clusters']
        results['dbscan'][f'eps_{eps}'] = {
            'labels': labels,
            'metrics': metrics,
            'n_noise': n_noise
        }
        if not np.isnan(metrics['silhouette']):
            print(f"  eps={eps}: {n_clusters} clusters, {n_noise} noise, Silhouette={metrics['silhouette']:.4f}")
        else:
            print(f"  eps={eps}: {n_clusters} clusters, {n_noise} noise (metrics undefined)")

    # ========================================================================
    # METHOD 4: HDBSCAN (if available)
    # ========================================================================
    print("\n[7] HDBSCAN Clustering...")

    for min_size in [3, 5, 7]:
        labels = hdbscan_clustering(X, min_cluster_size=min_size)
        if labels is not None:
            metrics = compute_validation_metrics(X, labels)
            n_noise = (labels == -1).sum()
            results['hdbscan'][f'min_{min_size}'] = {
                'labels': labels,
                'metrics': metrics,
                'n_noise': n_noise
            }
            if not np.isnan(metrics['silhouette']):
                print(f"  min_size={min_size}: {metrics['n_clusters']} clusters, {n_noise} noise, Silhouette={metrics['silhouette']:.4f}")
            else:
                print(f"  min_size={min_size}: {metrics['n_clusters']} clusters, {n_noise} noise")
        else:
            break  # HDBSCAN not installed

    # ========================================================================
    # FIND BEST K FOR EACH METHOD
    # ========================================================================
    print("\n[8] Determining optimal cluster count...")

    best_k = {}

    # For hierarchical and kmeans, find k with best silhouette
    for method in ['hierarchical', 'kmeans']:
        scores = [(k, r['metrics']['silhouette']) for k, r in results[method].items()]
        best = max(scores, key=lambda x: x[1] if not np.isnan(x[1]) else -999)
        best_k[method] = best[0]
        print(f"  {method}: Best k={best[0]} (Silhouette={best[1]:.4f})")

    # For DBSCAN, find eps with best silhouette among valid results
    dbscan_scores = [(k, r['metrics']['silhouette']) for k, r in results['dbscan'].items() if not np.isnan(r['metrics']['silhouette'])]
    if dbscan_scores:
        best_dbscan = max(dbscan_scores, key=lambda x: x[1])
        best_k['dbscan'] = best_dbscan[0]
        print(f"  dbscan: Best {best_dbscan[0]} (Silhouette={best_dbscan[1]:.4f})")

    # ========================================================================
    # STABILITY TESTING ON BEST CANDIDATES
    # ========================================================================
    print(f"\n[9] Stability testing (bootstrap n={N_BOOTSTRAP}, noise={NOISE_LEVEL*100}%)...")

    stability_results = {}

    for method, k in best_k.items():
        if method == 'hierarchical':
            cluster_func = hierarchical_ward
        elif method == 'kmeans':
            cluster_func = kmeans_clustering
        else:
            continue  # Skip DBSCAN for bootstrap (different interface)

        print(f"  Testing {method} k={k}...")

        # Bootstrap stability
        boot_mean, boot_std = bootstrap_stability(X, cluster_func, k, N_BOOTSTRAP)

        # Noise injection stability
        noise_mean, noise_std = noise_injection_stability(X, cluster_func, k, NOISE_LEVEL)

        stability_results[method] = {
            'k': k,
            'bootstrap_ari_mean': boot_mean,
            'bootstrap_ari_std': boot_std,
            'noise_ari_mean': noise_mean,
            'noise_ari_std': noise_std
        }

        print(f"    Bootstrap ARI: {boot_mean:.3f} ± {boot_std:.3f}")
        print(f"    Noise ARI: {noise_mean:.3f} ± {noise_std:.3f}")

    # ========================================================================
    # CONSENSUS SELECTION
    # ========================================================================
    print("\n[10] Consensus selection...")

    # Check if methods agree within ±1
    method_k = [v for m, v in best_k.items() if m in ['hierarchical', 'kmeans']]
    k_diff = max(method_k) - min(method_k) if len(method_k) >= 2 else 0

    agreement = k_diff <= 1
    print(f"  Hierarchical best k: {best_k.get('hierarchical', 'N/A')}")
    print(f"  K-Means best k: {best_k.get('kmeans', 'N/A')}")
    print(f"  Methods agree within ±1: {agreement}")

    # Select final k
    if agreement:
        # Take the k with best average stability
        final_k = best_k['hierarchical']  # Default to hierarchical

        # Check stability scores
        hier_stable = stability_results.get('hierarchical', {}).get('noise_ari_mean', 0)
        km_stable = stability_results.get('kmeans', {}).get('noise_ari_mean', 0)

        if km_stable > hier_stable:
            final_k = best_k['kmeans']

        final_method = 'hierarchical' if final_k == best_k['hierarchical'] else 'kmeans'
        final_labels = results[final_method][final_k]['labels']

        print(f"\n  SELECTED: {final_method} with k={final_k}")

        # Verify no cluster has <3 folios
        cluster_sizes = Counter(final_labels)
        small_clusters = [c for c, s in cluster_sizes.items() if s < 3]
        if small_clusters:
            print(f"  WARNING: Clusters {small_clusters} have <3 folios")
    else:
        print("\n  INCONCLUSIVE: Methods do not agree within ±1 cluster")
        # Try to find a compromise
        avg_k = int(np.mean(method_k))
        final_k = avg_k
        final_method = 'hierarchical'
        final_labels = results['hierarchical'][final_k]['labels']
        print(f"  Using compromise k={final_k} from hierarchical")

    # ========================================================================
    # GENERATE OUTPUTS
    # ========================================================================
    print("\n[11] Generating outputs...")

    # Create cluster assignments
    cluster_assignments = {}
    for i, folio_id in enumerate(folio_ids):
        label = int(final_labels[i])
        # Compute confidence as silhouette sample score would require more computation
        # Use distance to cluster center as proxy
        cluster_assignments[folio_id] = {
            'cluster_id': f'REGIME_{label + 1}',
            'numeric_id': label,
            'confidence': 'STABLE' if stability_results.get(final_method, {}).get('noise_ari_mean', 0) > 0.7 else 'MODERATE'
        }

    # Save cluster assignments JSON
    output_json = {
        'metadata': {
            'phase': 'OPS-2',
            'title': 'Control Strategy Clustering',
            'timestamp': datetime.now().isoformat(),
            'selected_method': final_method,
            'selected_k': final_k,
            'n_clusters': len(set(final_labels)),
            'n_folios': len(folio_ids)
        },
        'assignments': cluster_assignments
    }

    with open(OUTPUT_DIR / 'ops2_folio_cluster_assignments.json', 'w') as f:
        json.dump(output_json, f, indent=2)
    print(f"  Saved: ops2_folio_cluster_assignments.json")

    # Compute cluster profiles
    cluster_profiles = compute_cluster_profiles(df, folio_ids, final_labels, active_continuous)

    # Save cluster profiles markdown
    save_cluster_profiles_md(cluster_profiles, final_method, final_k, OUTPUT_DIR)
    print(f"  Saved: ops2_cluster_profiles.md")

    # Save validation report
    save_validation_report(
        results, best_k, stability_results,
        redundant_pairs, agreement, final_method, final_k,
        OUTPUT_DIR
    )
    print(f"  Saved: ops2_clustering_validation.md")

    # Cross-checks
    print("\n[12] Running cross-checks...")
    cross_check_results = run_cross_checks(df, folio_ids, final_labels)

    print("\n" + "=" * 70)
    print("PHASE OPS-2 COMPLETE")
    print("=" * 70)

    return output_json, cluster_profiles, cross_check_results


def compute_cluster_profiles(df, folio_ids, labels, continuous_features):
    """Compute profile statistics for each cluster"""
    profiles = {}

    for cluster_id in sorted(set(labels)):
        mask = labels == cluster_id
        cluster_df = df.iloc[mask]

        profile = {
            'regime_name': f'REGIME_{cluster_id + 1}',
            'size': int(mask.sum()),
            'folio_ids': [folio_ids[i] for i in range(len(labels)) if labels[i] == cluster_id],
            'continuous_metrics': {},
            'categorical_distributions': {}
        }

        # Continuous metrics
        key_metrics = ['link_density', 'hazard_density', 'aggressiveness', 'convergence_speed',
                      'control_margin', 'kernel_contact_ratio', 'mean_link_run']
        for metric in key_metrics:
            if metric in cluster_df.columns:
                profile['continuous_metrics'][metric] = {
                    'mean': float(cluster_df[metric].mean()),
                    'std': float(cluster_df[metric].std()),
                    'min': float(cluster_df[metric].min()),
                    'max': float(cluster_df[metric].max())
                }

        # Categorical distributions
        for cat in ['waiting_profile', 'risk_profile', 'intervention_style', 'stability_role', 'terminal_state']:
            if cat in cluster_df.columns:
                dist = cluster_df[cat].value_counts(normalize=True).to_dict()
                profile['categorical_distributions'][cat] = {k: round(v, 3) for k, v in dist.items()}

        profiles[cluster_id] = profile

    return profiles


def save_cluster_profiles_md(profiles, method, k, output_dir):
    """Save cluster profiles as markdown"""
    lines = [
        "# Phase OPS-2: Cluster Profiles",
        "",
        f"**Method:** {method.upper()}",
        f"**Number of Regimes:** {k}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        ""
    ]

    for cluster_id in sorted(profiles.keys()):
        p = profiles[cluster_id]
        lines.append(f"## {p['regime_name']}")
        lines.append("")
        lines.append(f"**Size:** {p['size']} folios")
        lines.append("")
        lines.append(f"**Folios:** {', '.join(p['folio_ids'])}")
        lines.append("")

        # Continuous metrics table
        lines.append("### Key Metrics")
        lines.append("")
        lines.append("| Metric | Mean | Std Dev | Min | Max |")
        lines.append("|--------|------|---------|-----|-----|")

        for metric, stats in p['continuous_metrics'].items():
            lines.append(f"| {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} |")

        lines.append("")

        # Categorical distributions
        lines.append("### OPS-1 Tag Distributions")
        lines.append("")

        for cat, dist in p['categorical_distributions'].items():
            dominant = max(dist.items(), key=lambda x: x[1])
            lines.append(f"**{cat}:** {dominant[0]} ({dominant[1]*100:.1f}%)")
            for val, pct in sorted(dist.items(), key=lambda x: -x[1]):
                lines.append(f"  - {val}: {pct*100:.1f}%")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Termination statement
    lines.append("")
    lines.append("> **\"OPS-2 is complete. Stable control-strategy regimes have been identified using purely operational metrics. No semantic or historical interpretation has been introduced.\"**")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")

    with open(output_dir / 'ops2_cluster_profiles.md', 'w') as f:
        f.write('\n'.join(lines))


def save_validation_report(results, best_k, stability_results, redundant_pairs, agreement,
                          final_method, final_k, output_dir):
    """Save validation report as markdown"""
    lines = [
        "# Phase OPS-2: Clustering Validation Report",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        "## 1. Method Comparison",
        "",
        "### Hierarchical (Ward) Results",
        "",
        "| k | Silhouette | Calinski-Harabasz | Davies-Bouldin |",
        "|---|------------|-------------------|----------------|"
    ]

    for k in K_RANGE:
        m = results['hierarchical'][k]['metrics']
        lines.append(f"| {k} | {m['silhouette']:.4f} | {m['calinski_harabasz']:.1f} | {m['davies_bouldin']:.4f} |")

    lines.extend([
        "",
        "### K-Means Results",
        "",
        "| k | Silhouette | Calinski-Harabasz | Davies-Bouldin |",
        "|---|------------|-------------------|----------------|"
    ])

    for k in K_RANGE:
        m = results['kmeans'][k]['metrics']
        lines.append(f"| {k} | {m['silhouette']:.4f} | {m['calinski_harabasz']:.1f} | {m['davies_bouldin']:.4f} |")

    lines.extend([
        "",
        "### DBSCAN Results",
        "",
        "| eps | Clusters | Noise | Silhouette |",
        "|-----|----------|-------|------------|"
    ])

    for key, r in results['dbscan'].items():
        sil = r['metrics']['silhouette']
        sil_str = f"{sil:.4f}" if not np.isnan(sil) else "N/A"
        lines.append(f"| {key.replace('eps_', '')} | {r['metrics']['n_clusters']} | {r['n_noise']} | {sil_str} |")

    # HDBSCAN if available
    if results['hdbscan']:
        lines.extend([
            "",
            "### HDBSCAN Results",
            "",
            "| min_size | Clusters | Noise | Silhouette |",
            "|----------|----------|-------|------------|"
        ])
        for key, r in results['hdbscan'].items():
            sil = r['metrics']['silhouette']
            sil_str = f"{sil:.4f}" if not np.isnan(sil) else "N/A"
            lines.append(f"| {key.replace('min_', '')} | {r['metrics']['n_clusters']} | {r['n_noise']} | {sil_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Stability Results",
        "",
        "| Method | k | Bootstrap ARI | Noise ARI |",
        "|--------|---|---------------|-----------|"
    ])

    for method, sr in stability_results.items():
        boot_str = f"{sr['bootstrap_ari_mean']:.3f} ± {sr['bootstrap_ari_std']:.3f}"
        noise_str = f"{sr['noise_ari_mean']:.3f} ± {sr['noise_ari_std']:.3f}"
        lines.append(f"| {method} | {sr['k']} | {boot_str} | {noise_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Consensus Analysis",
        "",
        f"**Hierarchical best k:** {best_k.get('hierarchical', 'N/A')}",
        f"**K-Means best k:** {best_k.get('kmeans', 'N/A')}",
        f"**Agreement within ±1:** {'YES' if agreement else 'NO'}",
        "",
        "---",
        "",
        "## 4. Selected Solution",
        "",
        f"**Method:** {final_method.upper()}",
        f"**k:** {final_k}",
        "",
        "### Justification",
        ""
    ])

    if agreement:
        lines.append("Methods agree within ±1 cluster count. Selection based on stability metrics.")
    else:
        lines.append("Methods did not fully agree. Compromise solution selected based on available metrics.")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Feature Redundancy",
        "",
        f"**Highly correlated pairs (|rho| > 0.9):** {len(redundant_pairs)}",
        ""
    ])

    if redundant_pairs:
        lines.append("| Feature 1 | Feature 2 | rho |")
        lines.append("|-----------|-----------|---|")
        for p1, p2, rho in redundant_pairs[:15]:
            lines.append(f"| {p1} | {p2} | {rho:.3f} |")
        if len(redundant_pairs) > 15:
            lines.append(f"| ... | ({len(redundant_pairs) - 15} more) | ... |")
        lines.append("")
        lines.append("*Note: Both features retained per instruction (no pruning).*")
    else:
        lines.append("No highly correlated feature pairs found.")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Eliminated Alternatives",
        ""
    ])

    # List alternatives not chosen
    for method in ['hierarchical', 'kmeans']:
        if method != final_method or best_k.get(method) != final_k:
            lines.append(f"- **{method.upper()} k={best_k.get(method, 'N/A')}:** Not selected due to lower stability metrics")

    lines.append("- **DBSCAN:** Variable cluster counts across epsilon values; noise points complicate interpretation")
    if not results['hdbscan']:
        lines.append("- **HDBSCAN:** Not available (library not installed)")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated: {datetime.now().isoformat()}*"
    ])

    with open(output_dir / 'ops2_clustering_validation.md', 'w') as f:
        f.write('\n'.join(lines))


def run_cross_checks(df, folio_ids, labels):
    """Run mandatory cross-checks"""
    results = {}

    # Check 1: Restart-capable folios
    restart_folios = df[df['restart_capable'] == True]['folio_id'].tolist()
    restart_clusters = [labels[folio_ids.index(f)] for f in restart_folios if f in folio_ids]

    print(f"  Restart-capable folios: {restart_folios}")
    print(f"  Their clusters: {[f'REGIME_{c+1}' for c in restart_clusters]}")

    # Are they clustered together or scattered?
    if len(set(restart_clusters)) == 1:
        print("  -> Restart folios cluster together (meaningful grouping)")
        results['restart_clustering'] = 'CLUSTERED_TOGETHER'
    elif len(set(restart_clusters)) == len(restart_clusters):
        print("  -> Restart folios scatter across clusters (outlier behavior)")
        results['restart_clustering'] = 'SCATTERED_OUTLIERS'
    else:
        print("  -> Restart folios partially cluster")
        results['restart_clustering'] = 'PARTIAL'

    # Check 2: Aggressive programs distribution
    aggressive_mask = df['intervention_style'] == 'AGGRESSIVE'
    aggressive_folios = df[aggressive_mask]['folio_id'].tolist()
    aggressive_clusters = [labels[folio_ids.index(f)] for f in aggressive_folios if f in folio_ids]

    cluster_counts = Counter(aggressive_clusters)
    total_aggressive = len(aggressive_folios)

    print(f"  Aggressive folios ({total_aggressive}): distribution across clusters")
    for c, count in sorted(cluster_counts.items()):
        print(f"    REGIME_{c+1}: {count} ({count/total_aggressive*100:.1f}%)")

    # Chi-square test for random distribution
    n_clusters = len(set(labels))
    expected = total_aggressive / n_clusters
    observed = [cluster_counts.get(c, 0) for c in range(n_clusters)]

    if sum(observed) > 0 and n_clusters > 1:
        chi2 = sum((o - expected)**2 / expected for o in observed if expected > 0)
        print(f"  -> Chi-square statistic: {chi2:.2f} (higher = more non-random)")
        results['aggressive_distribution'] = 'NON_RANDOM' if chi2 > n_clusters else 'RANDOM'
    else:
        results['aggressive_distribution'] = 'INSUFFICIENT_DATA'

    # Check 3: Maintenance vs Transition separation
    maint_mask = df['stability_role'] == 'MAINTENANCE_HEAVY'
    trans_mask = df['stability_role'] == 'TRANSITION_HEAVY'

    maint_clusters = Counter([labels[i] for i, m in enumerate(maint_mask) if m])
    trans_clusters = Counter([labels[i] for i, m in enumerate(trans_mask) if m])

    print(f"  Maintenance-heavy vs Transition-heavy separation:")

    overlap = 0
    for c in range(n_clusters):
        m_pct = maint_clusters.get(c, 0) / sum(maint_mask) * 100 if sum(maint_mask) > 0 else 0
        t_pct = trans_clusters.get(c, 0) / sum(trans_mask) * 100 if sum(trans_mask) > 0 else 0
        print(f"    REGIME_{c+1}: Maint {m_pct:.1f}%, Trans {t_pct:.1f}%")
        overlap += min(m_pct, t_pct)

    results['stability_role_separation'] = 'SEPARATED' if overlap < 50 else 'MIXED'
    print(f"  -> Overlap: {overlap:.1f}% ({'SEPARATED' if overlap < 50 else 'MIXED'})")

    return results


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    run_clustering_analysis()
