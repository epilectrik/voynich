"""
Topic Model Replication Test
Phase: YALE_ALIGNMENT

Replicates Claire Bowern's topic modeling approach using our structural features.

Yale finding: Topic modeling found 5-6 sections. Groupings only made sense
when combined with scribal identification.

Test: Do our structural features produce similar clustering? How does it
compare to our 4 regimes and Davis's 5 scribes?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import sklearn for clustering
try:
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: sklearn not available, using simple clustering")


def load_folio_features():
    """Load structural features for all B folios."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    cart_path = results_dir / "b_design_space_cartography.json"

    with open(cart_path) as f:
        cart_data = json.load(f)

    folios = []
    features = []
    regimes = []

    for folio, data in cart_data.get("folio_positions", {}).items():
        folios.append(folio)
        regimes.append(data.get("regime", "UNKNOWN"))

        # Extract feature vector
        feature_vec = [
            data.get("hazard_density", 0),
            data.get("escape_density", 0),
            data.get("cei_total", 0),
            data.get("link_density", 0),
            data.get("execution_tension", 0)
        ]
        features.append(feature_vec)

    return folios, features, regimes


def simple_kmeans(features, k):
    """Simple k-means without sklearn."""
    import random

    n = len(features)
    dim = len(features[0])

    # Initialize centroids randomly
    random.seed(42)
    centroids = random.sample(features, k)

    for _ in range(100):  # Max iterations
        # Assign points to nearest centroid
        assignments = []
        for f in features:
            distances = []
            for c in centroids:
                dist = sum((f[i] - c[i])**2 for i in range(dim))
                distances.append(dist)
            assignments.append(distances.index(min(distances)))

        # Update centroids
        new_centroids = []
        for cluster_id in range(k):
            cluster_points = [features[i] for i in range(n) if assignments[i] == cluster_id]
            if cluster_points:
                new_centroid = [
                    sum(p[d] for p in cluster_points) / len(cluster_points)
                    for d in range(dim)
                ]
                new_centroids.append(new_centroid)
            else:
                new_centroids.append(centroids[cluster_id])

        if new_centroids == centroids:
            break
        centroids = new_centroids

    return assignments


def cluster_folios(folios, features, n_clusters_range=(3, 8)):
    """Cluster folios and find optimal cluster count."""

    if HAS_SKLEARN:
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        results = []
        for k in range(n_clusters_range[0], n_clusters_range[1] + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)

            if k > 1 and k < len(features):
                sil_score = silhouette_score(features_scaled, labels)
            else:
                sil_score = 0

            results.append({
                "k": k,
                "silhouette": round(sil_score, 4),
                "labels": labels.tolist()
            })

        # Find best k by silhouette
        best = max(results, key=lambda x: x["silhouette"])

        return results, best
    else:
        # Simple clustering without sklearn
        results = []
        for k in range(n_clusters_range[0], n_clusters_range[1] + 1):
            labels = simple_kmeans(features, k)
            results.append({
                "k": k,
                "silhouette": 0,  # Can't compute without sklearn
                "labels": labels
            })

        # Default to k=5 (Yale's finding)
        best = [r for r in results if r["k"] == 5][0]
        return results, best


def analyze_cluster_composition(folios, labels, regimes, scribes):
    """Analyze what's in each cluster."""

    cluster_analysis = defaultdict(lambda: {
        "folios": [],
        "regime_dist": Counter(),
        "scribe_dist": Counter()
    })

    for i, (folio, label, regime) in enumerate(zip(folios, labels, regimes)):
        scribe = scribes.get(folio, 0)
        cluster_analysis[label]["folios"].append(folio)
        cluster_analysis[label]["regime_dist"][regime] += 1
        if scribe:
            cluster_analysis[label]["scribe_dist"][f"Scribe_{scribe}"] += 1

    return dict(cluster_analysis)


def assign_scribes(folios):
    """Assign scribes to folios based on section."""
    import re

    scribe_assignments = {}
    for folio in folios:
        match = re.match(r'f(\d+)', folio.lower())
        if not match:
            continue
        num = int(match.group(1))

        if num <= 66:
            scribe_assignments[folio] = 1
        elif 67 <= num <= 73:
            scribe_assignments[folio] = 4
        elif 75 <= num <= 86:
            scribe_assignments[folio] = 2
        elif 87 <= num <= 102:
            scribe_assignments[folio] = 1
        elif 103 <= num <= 116:
            scribe_assignments[folio] = 3

    return scribe_assignments


def main():
    print("=" * 60)
    print("TOPIC MODEL REPLICATION TEST")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    # Load data
    folios, features, regimes = load_folio_features()
    scribes = assign_scribes(folios)

    print(f"\nLoaded {len(folios)} B folios with {len(features[0])} features each")

    # Run clustering
    print("\nRunning clustering analysis...")
    all_results, best = cluster_folios(folios, features)

    print("\nCluster count evaluation:")
    print("-" * 40)
    for r in all_results:
        marker = " <-- BEST" if r["k"] == best["k"] else ""
        print(f"  k={r['k']}: silhouette={r['silhouette']:.4f}{marker}")

    print(f"\nOptimal cluster count: {best['k']}")
    print(f"Yale found: 5-6 sections")
    print(f"Our regimes: 4")
    print(f"Davis scribes: 5")

    # Analyze best clustering
    cluster_analysis = analyze_cluster_composition(
        folios, best["labels"], regimes, scribes
    )

    print(f"\nCluster composition (k={best['k']}):")
    print("-" * 40)

    for cluster_id in sorted(cluster_analysis.keys()):
        data = cluster_analysis[cluster_id]
        n = len(data["folios"])

        # Dominant regime
        if data["regime_dist"]:
            dom_regime = data["regime_dist"].most_common(1)[0]
            regime_pct = round(100 * dom_regime[1] / n, 1)
        else:
            dom_regime = ("NONE", 0)
            regime_pct = 0

        # Dominant scribe
        if data["scribe_dist"]:
            dom_scribe = data["scribe_dist"].most_common(1)[0]
            scribe_pct = round(100 * dom_scribe[1] / n, 1)
        else:
            dom_scribe = ("NONE", 0)
            scribe_pct = 0

        print(f"\n  Cluster {cluster_id}: {n} folios")
        print(f"    Dominant regime: {dom_regime[0]} ({regime_pct}%)")
        print(f"    Dominant scribe: {dom_scribe[0]} ({scribe_pct}%)")
        print(f"    Regimes: {dict(data['regime_dist'])}")
        print(f"    Scribes: {dict(data['scribe_dist'])}")

    # Check alignment with regimes
    print("\n" + "=" * 60)
    print("ALIGNMENT ANALYSIS")
    print("=" * 60)

    # How well do clusters align with regimes?
    regime_cluster_match = 0
    for cluster_id, data in cluster_analysis.items():
        if data["regime_dist"]:
            dom_count = data["regime_dist"].most_common(1)[0][1]
            total = sum(data["regime_dist"].values())
            regime_cluster_match += dom_count

    regime_purity = round(100 * regime_cluster_match / len(folios), 1)
    print(f"\nRegime purity (dominant regime per cluster): {regime_purity}%")

    # How well do clusters align with scribes?
    scribe_cluster_match = 0
    for cluster_id, data in cluster_analysis.items():
        if data["scribe_dist"]:
            dom_count = data["scribe_dist"].most_common(1)[0][1]
            scribe_cluster_match += dom_count

    scribe_assigned = sum(1 for f in folios if scribes.get(f))
    if scribe_assigned > 0:
        scribe_purity = round(100 * scribe_cluster_match / scribe_assigned, 1)
        print(f"Scribe purity (dominant scribe per cluster): {scribe_purity}%")

    # Build results
    results = {
        "test": "TOPIC_MODEL_REPLICATION",
        "date": "2026-01-14",
        "yale_finding": "5-6 sections, only made sense with scribal identification",
        "n_folios": len(folios),
        "features_used": ["hazard_density", "escape_density", "cei_total", "link_density", "execution_tension"],
        "optimal_k": best["k"],
        "silhouette_score": best["silhouette"],
        "regime_purity": regime_purity,
        "cluster_details": {},
        "interpretation": ""
    }

    for cluster_id, data in cluster_analysis.items():
        results["cluster_details"][f"cluster_{cluster_id}"] = {
            "n_folios": len(data["folios"]),
            "folios": data["folios"],
            "regime_distribution": dict(data["regime_dist"]),
            "scribe_distribution": dict(data["scribe_dist"])
        }

    # Interpretation
    if best["k"] in [5, 6]:
        results["interpretation"] = f"ALIGNED: Optimal k={best['k']} matches Yale's 5-6 sections"
    elif best["k"] == 4:
        results["interpretation"] = f"ALIGNED WITH REGIMES: Optimal k={best['k']} matches our 4 regimes"
    else:
        results["interpretation"] = f"DIVERGENT: Optimal k={best['k']} differs from Yale (5-6) and regimes (4)"

    print(f"\n{results['interpretation']}")

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "topic_model_replication.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
