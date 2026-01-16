#!/usr/bin/env python3
"""
Terminal Trajectory Differentiation Test (TTDT) - v2

Question: Do Currier B folios define distinct terminal execution profiles
that cannot be reduced to REGIME alone?

Expert's prediction:
- ~83 stable clusters -> B folios ARE outcome-typed, 83 is structurally forced
- ~4 clusters -> B only encodes REGIME, hypothesis falsified
- ~10-20 clusters -> Outcome types exist but not 1:1 with folios
"""

import json
import numpy as np
import warnings
from pathlib import Path
from collections import defaultdict
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.cluster import KMeans

warnings.filterwarnings('ignore')

BASE_PATH = Path(__file__).parent.parent.parent
RESULTS_PATH = BASE_PATH / "results"
OUTPUT_FILE = RESULTS_PATH / "ttdt_results_v2.json"


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


def build_feature_matrix(signatures, regime_map):
    """Build the terminal profile feature matrix."""

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
    ]

    folios = []
    features = []
    regimes = []

    for folio, sig in signatures.items():
        if folio not in regime_map:
            continue

        row = []
        for feat in numeric_features:
            if feat in sig:
                val = sig[feat]
                if val is None:
                    val = 0.0
                row.append(float(val))
            else:
                row.append(0.0)

        # Terminal state as numeric
        terminal = sig.get('terminal_state', 'other')
        terminal_val = {'STATE-C': 2, 'initial': 1, 'other': 0}.get(terminal, 0)
        row.append(terminal_val)

        folios.append(folio)
        features.append(row)
        regimes.append(regime_map[folio])

    X = np.array(features)
    feature_names = numeric_features + ['terminal_state_numeric']

    return X, folios, regimes, feature_names


def regress_out_regime(X, regimes):
    """Regress out REGIME to get residuals."""
    unique_regimes = sorted(set(regimes))
    regime_dummies = np.zeros((len(regimes), len(unique_regimes)))
    for i, r in enumerate(regimes):
        regime_dummies[i, unique_regimes.index(r)] = 1

    residuals = np.zeros_like(X)
    for j in range(X.shape[1]):
        y = X[:, j]
        try:
            beta = np.linalg.lstsq(regime_dummies, y, rcond=None)[0]
            predicted = regime_dummies @ beta
            residuals[:, j] = y - predicted
        except:
            residuals[:, j] = y

    return residuals, unique_regimes


def evaluate_clustering(X, k_values):
    """Evaluate clustering at multiple k values."""

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Remove zero-variance columns
    variances = X_scaled.var(axis=0)
    valid_cols = variances > 1e-10
    X_valid = X_scaled[:, valid_cols]

    if X_valid.shape[1] < 2:
        return None

    results = {}
    for k in k_values:
        if k > len(X_valid) - 1:
            continue

        try:
            # K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels_kmeans = kmeans.fit_predict(X_valid)
            sil_kmeans = silhouette_score(X_valid, labels_kmeans)

            # Hierarchical clustering
            Z = linkage(X_valid, method='ward')
            labels_hier = fcluster(Z, k, criterion='maxclust')
            sil_hier = silhouette_score(X_valid, labels_hier)

            results[k] = {
                'kmeans_silhouette': float(sil_kmeans),
                'hierarchical_silhouette': float(sil_hier),
                'kmeans_inertia': float(kmeans.inertia_),
                'labels_kmeans': labels_kmeans.tolist(),
                'labels_hier': labels_hier.tolist()
            }
        except Exception as e:
            print(f"Warning: k={k} failed: {e}")
            continue

    return results


def compare_to_regime(X, regimes, folios):
    """Compare folio clustering to REGIME assignment."""

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    variances = X_scaled.var(axis=0)
    valid_cols = variances > 1e-10
    X_valid = X_scaled[:, valid_cols]

    # Create numeric REGIME labels
    unique_regimes = sorted(set(regimes))
    regime_labels = np.array([unique_regimes.index(r) for r in regimes])

    # Cluster at k=4 (number of regimes)
    kmeans_4 = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels_4 = kmeans_4.fit_predict(X_valid)

    # Measure how well clusters match regimes
    ari = adjusted_rand_score(regime_labels, cluster_labels_4)

    return {
        'adjusted_rand_index': float(ari),
        'interpretation': 'high' if ari > 0.5 else ('moderate' if ari > 0.2 else 'low')
    }


def main():
    print("=" * 70)
    print("TERMINAL TRAJECTORY DIFFERENTIATION TEST (TTDT) - v2")
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

    regime_counts = defaultdict(int)
    for r in regimes:
        regime_counts[r] += 1
    print(f"\n  Regime distribution:")
    for r in sorted(regime_counts.keys()):
        print(f"    {r}: {regime_counts[r]} folios")

    # Key k values to test
    k_values = [2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 70, 80, 82]

    # Step 1: Cluster RAW features
    print("\n" + "-" * 70)
    print("STEP 1: Clustering RAW features")
    print("-" * 70)

    raw_results = evaluate_clustering(X, k_values)

    if raw_results:
        print("\n  k   | KMeans Sil | Hier Sil")
        print("  ----|------------|----------")
        for k in sorted(raw_results.keys()):
            r = raw_results[k]
            print(f"  {k:3d} |     {r['kmeans_silhouette']:.4f} |   {r['hierarchical_silhouette']:.4f}")

        # Find best k
        best_k_raw = max(raw_results.keys(), key=lambda k: raw_results[k]['kmeans_silhouette'])
        print(f"\n  Best k (raw): {best_k_raw} (silhouette: {raw_results[best_k_raw]['kmeans_silhouette']:.4f})")

    # Check REGIME match
    print("\n  Comparing k=4 clusters to REGIME assignments:")
    regime_match = compare_to_regime(X, regimes, folios)
    print(f"    Adjusted Rand Index: {regime_match['adjusted_rand_index']:.4f}")
    print(f"    Interpretation: {regime_match['interpretation']} match with REGIME")

    # Step 2: Regress out REGIME
    print("\n" + "-" * 70)
    print("STEP 2: Clustering RESIDUAL features (after regime removal)")
    print("-" * 70)

    residuals, unique_regimes = regress_out_regime(X, regimes)

    res_results = evaluate_clustering(residuals, k_values)

    if res_results:
        print("\n  k   | KMeans Sil | Hier Sil")
        print("  ----|------------|----------")
        for k in sorted(res_results.keys()):
            r = res_results[k]
            print(f"  {k:3d} |     {r['kmeans_silhouette']:.4f} |   {r['hierarchical_silhouette']:.4f}")

        best_k_res = max(res_results.keys(), key=lambda k: res_results[k]['kmeans_silhouette'])
        print(f"\n  Best k (residual): {best_k_res} (silhouette: {res_results[best_k_res]['kmeans_silhouette']:.4f})")

    # Step 3: Interpretation
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Key comparisons
    sil_at_4 = res_results.get(4, {}).get('kmeans_silhouette', 0)
    sil_at_10 = res_results.get(10, {}).get('kmeans_silhouette', 0)
    sil_at_20 = res_results.get(20, {}).get('kmeans_silhouette', 0)
    sil_at_82 = res_results.get(82, {}).get('kmeans_silhouette', 0)

    print(f"\n  Key silhouette scores (residuals):")
    print(f"    k=4:  {sil_at_4:.4f}  (REGIME count)")
    print(f"    k=10: {sil_at_10:.4f}")
    print(f"    k=20: {sil_at_20:.4f}")
    print(f"    k=82: {sil_at_82:.4f}  (near-folio count)")

    # Compute differentiation ratio
    if sil_at_4 > 0:
        diff_ratio = best_k_res / 4
    else:
        diff_ratio = None

    print(f"\n  Differentiation ratio (best_k / 4): {diff_ratio:.2f}" if diff_ratio else "")

    # Determine verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if best_k_res >= 60:
        verdict = "STRONG SUPPORT"
        explanation = f"Optimal clustering at k={best_k_res} suggests ~83 distinct terminal profiles"
    elif best_k_res >= 30:
        verdict = "MODERATE SUPPORT"
        explanation = f"Optimal clustering at k={best_k_res} suggests significant but not 1:1 differentiation"
    elif best_k_res >= 10:
        verdict = "WEAK/PARTIAL SUPPORT"
        explanation = f"Optimal clustering at k={best_k_res} suggests ~10-20 outcome families, not 83"
    elif best_k_res <= 6:
        verdict = "FALSIFIED"
        explanation = f"Optimal clustering at k={best_k_res} ~= REGIME count. B encodes REGIME, not outcomes"
    else:
        verdict = "INCONCLUSIVE"
        explanation = "Results do not clearly support either position"

    print(f"\n  {verdict}")
    print(f"  {explanation}")

    print(f"\n  Raw ARI with REGIME: {regime_match['adjusted_rand_index']:.4f}")
    if regime_match['adjusted_rand_index'] > 0.3:
        print("  -> Raw features are substantially explained by REGIME")
    elif regime_match['adjusted_rand_index'] > 0.1:
        print("  -> Raw features partially align with REGIME")
    else:
        print("  -> Raw features have structure beyond REGIME")

    # Implications for 83:83
    print("\n" + "-" * 70)
    print("IMPLICATIONS FOR 83:83 PUFF-VOYNICH CORRESPONDENCE")
    print("-" * 70)

    if best_k_res >= 60:
        implication = "B folios ARE outcome-typed. 83 is structurally forced by terminal differentiation."
    elif best_k_res >= 30:
        implication = "Partial outcome typing exists. 83 may be partitioned into ~30-40 outcome families."
    elif best_k_res >= 10:
        implication = "B has ~10-20 terminal profile families. 83 is organizational, not structural."
    else:
        implication = "B primarily encodes REGIME. 83:83 cannot be explained by outcome differentiation."

    print(f"\n  {implication}")

    # Save results
    results = {
        'test': 'TTDT_v2',
        'question': 'Do B folios define distinct terminal profiles beyond REGIME?',
        'data': {
            'n_folios': len(folios),
            'n_features': len(feature_names),
            'feature_names': feature_names,
            'regime_distribution': dict(regime_counts)
        },
        'raw_clustering': {
            'best_k': best_k_raw if raw_results else None,
            'best_silhouette': raw_results[best_k_raw]['kmeans_silhouette'] if raw_results else None,
            'regime_ari': regime_match['adjusted_rand_index'],
            'all_k': {str(k): v['kmeans_silhouette'] for k, v in raw_results.items()} if raw_results else {}
        },
        'residual_clustering': {
            'best_k': best_k_res if res_results else None,
            'best_silhouette': res_results[best_k_res]['kmeans_silhouette'] if res_results else None,
            'all_k': {str(k): v['kmeans_silhouette'] for k, v in res_results.items()} if res_results else {}
        },
        'verdict': verdict,
        'explanation': explanation,
        'implication_for_83': implication
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_FILE}")

    return results


if __name__ == '__main__':
    main()
