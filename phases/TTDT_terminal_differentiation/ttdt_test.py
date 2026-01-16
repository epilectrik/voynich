#!/usr/bin/env python3
"""
Terminal Trajectory Differentiation Test (TTDT)

Question: Do Currier B folios define distinct terminal execution profiles
that cannot be reduced to REGIME, hazard level, or AZC legality alone?

Expert's prediction:
- ~83 stable clusters → B folios ARE outcome-typed, 83 is structurally forced
- ~4 clusters → B only encodes REGIME, hypothesis falsified
- ~10-20 clusters → Outcome types exist but not 1:1 with folios
- No stable clustering → 83 remains unexplained

Method:
1. Define terminal profile vector using B-internal metrics
2. Regress out REGIME to get residuals
3. Cluster the residual terminal profiles
4. Evaluate cluster count vs 83
"""

import json
import numpy as np
import warnings
from pathlib import Path
from collections import defaultdict
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans, AgglomerativeClustering

warnings.filterwarnings('ignore')

BASE_PATH = Path(__file__).parent.parent.parent
RESULTS_PATH = BASE_PATH / "results"
OUTPUT_FILE = RESULTS_PATH / "ttdt_results.json"


def load_control_signatures():
    """Load per-folio control signatures."""
    with open(RESULTS_PATH / "control_signatures.json") as f:
        data = json.load(f)
    return data["signatures"]


def load_regime_assignments():
    """Load REGIME assignments from proposed_folio_order.txt."""
    regime_map = {}
    with open(RESULTS_PATH / "proposed_folio_order.txt") as f:
        for line in f:
            line = line.strip()
            if '|' in line and 'REGIME' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    folio = parts[1]
                    regime = parts[2]
                    if regime.startswith('REGIME_'):
                        regime_map[folio] = regime
    return regime_map


def load_design_space_cartography():
    """Load additional metrics from b_design_space_cartography.json."""
    with open(RESULTS_PATH / "b_design_space_cartography.json") as f:
        data = json.load(f)
    # Extract per-folio data if available
    if "folios" in data:
        return data["folios"]
    return {}


def build_feature_matrix(signatures, regime_map):
    """Build the terminal profile feature matrix."""

    # Define which metrics to use
    numeric_features = [
        'mean_cycle_length',
        'cycle_regularity',
        'link_density',
        'kernel_contact_ratio',
        'hazard_density',
        'near_miss_count',
        'recovery_ops_count',
        'intervention_frequency',
        'intervention_diversity',
        'phase_ordering_rigidity',
        'kernel_distance_mean',
        'compression_ratio',
        'signature_sensitivity',
    ]

    # Collect data for B folios only
    folios = []
    features = []
    regimes = []
    terminal_states = []

    for folio, sig in signatures.items():
        # Skip non-B folios (those without regime assignment)
        if folio not in regime_map:
            continue

        # Extract numeric features
        row = []
        for feat in numeric_features:
            if feat in sig:
                val = sig[feat]
                if val is None:
                    val = 0.0
                row.append(float(val))
            else:
                row.append(0.0)

        # Terminal state as binary features
        terminal = sig.get('terminal_state', 'other')
        terminal_states.append(terminal)

        folios.append(folio)
        features.append(row)
        regimes.append(regime_map[folio])

    # Convert to arrays
    X = np.array(features)

    # Add terminal state dummy variables
    unique_terminals = list(set(terminal_states))
    terminal_dummies = np.zeros((len(terminal_states), len(unique_terminals)))
    for i, ts in enumerate(terminal_states):
        terminal_dummies[i, unique_terminals.index(ts)] = 1

    X = np.hstack([X, terminal_dummies])

    feature_names = numeric_features + [f'terminal_{t}' for t in unique_terminals]

    return X, folios, regimes, feature_names


def regress_out_regime(X, regimes):
    """Regress out REGIME to get residuals."""
    # One-hot encode regimes
    unique_regimes = sorted(set(regimes))
    regime_dummies = np.zeros((len(regimes), len(unique_regimes)))
    for i, r in enumerate(regimes):
        regime_dummies[i, unique_regimes.index(r)] = 1

    # Regress each feature on regime dummies
    residuals = np.zeros_like(X)
    for j in range(X.shape[1]):
        y = X[:, j]
        # Simple OLS: y = Xβ + ε
        # Residuals = y - X @ (X'X)^-1 X'y
        try:
            beta = np.linalg.lstsq(regime_dummies, y, rcond=None)[0]
            predicted = regime_dummies @ beta
            residuals[:, j] = y - predicted
        except:
            residuals[:, j] = y  # If regression fails, keep original

    return residuals, unique_regimes


def find_optimal_clusters(X, max_k=100):
    """Find optimal number of clusters using silhouette and gap statistics."""

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Remove any columns with zero variance
    valid_cols = X_scaled.std(axis=0) > 1e-10
    X_scaled = X_scaled[:, valid_cols]

    if X_scaled.shape[1] < 2:
        return None, None, None

    results = {
        'k': [],
        'silhouette': [],
        'inertia': [],
    }

    max_k = min(max_k, X_scaled.shape[0] - 1)

    for k in range(2, max_k + 1):
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)

            sil = silhouette_score(X_scaled, labels)

            results['k'].append(k)
            results['silhouette'].append(sil)
            results['inertia'].append(kmeans.inertia_)
        except Exception as e:
            print(f"Warning: k={k} failed: {e}")
            continue

    # Find optimal k by silhouette
    if results['silhouette']:
        best_idx = np.argmax(results['silhouette'])
        optimal_k_silhouette = results['k'][best_idx]
    else:
        optimal_k_silhouette = None

    # Also do hierarchical clustering and find natural groupings
    try:
        Z = linkage(X_scaled, method='ward')
        # Cut at various heights to see cluster count
        hierarchical_results = {}
        for n_clusters in [4, 10, 20, 50, 83]:
            if n_clusters <= X_scaled.shape[0]:
                labels_hier = fcluster(Z, n_clusters, criterion='maxclust')
                sil_hier = silhouette_score(X_scaled, labels_hier)
                hierarchical_results[n_clusters] = sil_hier
    except:
        hierarchical_results = {}

    return results, optimal_k_silhouette, hierarchical_results


def stability_analysis(X, k, n_bootstrap=50):
    """Test cluster stability under bootstrap resampling."""

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    valid_cols = X_scaled.std(axis=0) > 1e-10
    X_scaled = X_scaled[:, valid_cols]

    if X_scaled.shape[1] < 2:
        return None

    base_kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    base_labels = base_kmeans.fit_predict(X_scaled)

    stability_scores = []

    for i in range(n_bootstrap):
        # Bootstrap sample
        indices = np.random.choice(len(X_scaled), len(X_scaled), replace=True)
        X_boot = X_scaled[indices]

        try:
            kmeans_boot = KMeans(n_clusters=k, random_state=i, n_init=10)
            labels_boot = kmeans_boot.fit_predict(X_boot)

            # Measure agreement via adjusted Rand index (approximated)
            sil_boot = silhouette_score(X_boot, labels_boot)
            stability_scores.append(sil_boot)
        except:
            continue

    if stability_scores:
        return {
            'mean_silhouette': np.mean(stability_scores),
            'std_silhouette': np.std(stability_scores),
            'n_bootstrap': len(stability_scores)
        }
    return None


def main():
    print("=" * 70)
    print("TERMINAL TRAJECTORY DIFFERENTIATION TEST (TTDT)")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    signatures = load_control_signatures()
    regime_map = load_regime_assignments()

    print(f"  Control signatures: {len(signatures)} folios")
    print(f"  Regime assignments: {len(regime_map)} folios")

    # Build feature matrix
    print("\nBuilding feature matrix...")
    X, folios, regimes, feature_names = build_feature_matrix(signatures, regime_map)

    print(f"  B folios: {len(folios)}")
    print(f"  Features: {len(feature_names)}")

    # Show regime distribution
    regime_counts = defaultdict(int)
    for r in regimes:
        regime_counts[r] += 1
    print(f"\n  Regime distribution:")
    for r in sorted(regime_counts.keys()):
        print(f"    {r}: {regime_counts[r]} folios")

    # Step 1: Cluster RAW features (before regime removal)
    print("\n" + "-" * 70)
    print("STEP 1: Clustering RAW features (before regime removal)")
    print("-" * 70)

    raw_results, raw_optimal_k, raw_hierarchical = find_optimal_clusters(X)

    if raw_optimal_k:
        print(f"\n  Optimal k (by silhouette): {raw_optimal_k}")
        print(f"  Best silhouette score: {max(raw_results['silhouette']):.4f}")

    if raw_hierarchical:
        print(f"\n  Hierarchical clustering silhouette scores:")
        for n_clust, sil in sorted(raw_hierarchical.items()):
            marker = " <--" if n_clust == 83 else ""
            print(f"    k={n_clust}: {sil:.4f}{marker}")

    # Step 2: Regress out REGIME
    print("\n" + "-" * 70)
    print("STEP 2: Regressing out REGIME")
    print("-" * 70)

    residuals, unique_regimes = regress_out_regime(X, regimes)

    print(f"\n  Regimes regressed: {unique_regimes}")
    print(f"  Residual variance explained by REGIME removed")

    # Step 3: Cluster RESIDUAL features
    print("\n" + "-" * 70)
    print("STEP 3: Clustering RESIDUAL features (after regime removal)")
    print("-" * 70)

    res_results, res_optimal_k, res_hierarchical = find_optimal_clusters(residuals)

    if res_optimal_k:
        print(f"\n  Optimal k (by silhouette): {res_optimal_k}")
        print(f"  Best silhouette score: {max(res_results['silhouette']):.4f}")

    if res_hierarchical:
        print(f"\n  Hierarchical clustering silhouette scores:")
        for n_clust, sil in sorted(res_hierarchical.items()):
            marker = " <--" if n_clust == 83 else ""
            print(f"    k={n_clust}: {sil:.4f}{marker}")

    # Step 4: Stability analysis at key cluster counts
    print("\n" + "-" * 70)
    print("STEP 4: Stability analysis")
    print("-" * 70)

    stability_results = {}
    for k in [4, 10, 20, 50, 83]:
        if k <= len(folios) - 1:
            print(f"\n  Testing stability at k={k}...")
            stab = stability_analysis(residuals, k, n_bootstrap=30)
            if stab:
                stability_results[k] = stab
                print(f"    Mean silhouette: {stab['mean_silhouette']:.4f} ± {stab['std_silhouette']:.4f}")

    # Step 5: Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Determine verdict based on results
    if res_optimal_k and res_results:
        best_sil = max(res_results['silhouette'])

        # Check if 83 clusters is meaningful
        sil_at_83 = res_hierarchical.get(83, 0) if res_hierarchical else 0
        sil_at_4 = res_hierarchical.get(4, 0) if res_hierarchical else 0

        print(f"\n  Key metrics:")
        print(f"    Optimal cluster count (silhouette): {res_optimal_k}")
        print(f"    Silhouette at k=4: {sil_at_4:.4f}")
        print(f"    Silhouette at k=83: {sil_at_83:.4f}")

        if res_optimal_k >= 70:
            verdict = "STRONG SUPPORT: ~83 natural clusters suggest B folios are outcome-typed"
            interpretation = "B folios define distinct terminal profiles beyond REGIME"
        elif res_optimal_k >= 40:
            verdict = "PARTIAL SUPPORT: Significant differentiation but not 1:1 with folios"
            interpretation = "Outcome types exist but some folios share profiles"
        elif res_optimal_k >= 15:
            verdict = "WEAK SUPPORT: Some structure beyond REGIME but limited"
            interpretation = "Folios cluster into ~10-20 outcome families"
        elif res_optimal_k <= 6:
            verdict = "FALSIFIED: Only ~4 clusters → REGIME dominates"
            interpretation = "B encodes REGIME only, not outcome differentiation"
        else:
            verdict = "INCONCLUSIVE: Need further analysis"
            interpretation = "Structure present but not clearly matching prediction"

        print(f"\n  VERDICT: {verdict}")
        print(f"  {interpretation}")

    # Save results
    results = {
        'test': 'TTDT',
        'question': 'Do B folios define distinct terminal profiles beyond REGIME?',
        'data': {
            'n_folios': len(folios),
            'n_features': len(feature_names),
            'feature_names': feature_names,
            'regime_distribution': dict(regime_counts)
        },
        'raw_clustering': {
            'optimal_k': raw_optimal_k,
            'best_silhouette': max(raw_results['silhouette']) if raw_results and raw_results['silhouette'] else None,
            'hierarchical': raw_hierarchical
        },
        'residual_clustering': {
            'optimal_k': res_optimal_k,
            'best_silhouette': max(res_results['silhouette']) if res_results and res_results['silhouette'] else None,
            'hierarchical': res_hierarchical
        },
        'stability': stability_results,
        'verdict': verdict if 'verdict' in dir() else 'INCONCLUSIVE',
        'interpretation': interpretation if 'interpretation' in dir() else 'Unable to determine'
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_FILE}")

    return results


if __name__ == '__main__':
    main()
