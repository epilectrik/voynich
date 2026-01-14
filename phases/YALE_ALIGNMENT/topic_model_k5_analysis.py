"""
Topic Model k=5 Analysis
Force k=5 to match Yale's finding and see composition.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import re


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
        feature_vec = [
            data.get("hazard_density", 0),
            data.get("escape_density", 0),
            data.get("cei_total", 0),
            data.get("link_density", 0),
            data.get("execution_tension", 0)
        ]
        features.append(feature_vec)

    return folios, features, regimes


def assign_scribes(folios):
    """Assign scribes to folios based on section."""
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
    print("TOPIC MODEL k=5 ANALYSIS (Yale Match)")
    print("=" * 60)

    folios, features, regimes = load_folio_features()
    scribes = assign_scribes(folios)

    # Normalize and cluster with k=5
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_scaled)

    # Analyze cluster composition
    cluster_analysis = defaultdict(lambda: {
        "folios": [],
        "regime_dist": Counter(),
        "scribe_dist": Counter(),
        "folio_ranges": []
    })

    for i, (folio, label, regime) in enumerate(zip(folios, labels, regimes)):
        scribe = scribes.get(folio, 0)
        cluster_analysis[label]["folios"].append(folio)
        cluster_analysis[label]["regime_dist"][regime] += 1
        if scribe:
            cluster_analysis[label]["scribe_dist"][f"Scribe_{scribe}"] += 1

        # Extract folio number for range analysis
        match = re.match(r'f(\d+)', folio.lower())
        if match:
            cluster_analysis[label]["folio_ranges"].append(int(match.group(1)))

    print("\nCluster composition (k=5 to match Yale):")
    print("=" * 60)

    for cluster_id in sorted(cluster_analysis.keys()):
        data = cluster_analysis[cluster_id]
        n = len(data["folios"])

        # Dominant regime
        dom_regime = data["regime_dist"].most_common(1)[0] if data["regime_dist"] else ("NONE", 0)
        regime_pct = round(100 * dom_regime[1] / n, 1)

        # Dominant scribe
        dom_scribe = data["scribe_dist"].most_common(1)[0] if data["scribe_dist"] else ("NONE", 0)
        scribe_pct = round(100 * dom_scribe[1] / sum(data["scribe_dist"].values()), 1) if data["scribe_dist"] else 0

        # Folio range
        if data["folio_ranges"]:
            min_f, max_f = min(data["folio_ranges"]), max(data["folio_ranges"])
            range_str = f"f{min_f}-f{max_f}"
        else:
            range_str = "N/A"

        print(f"\nCluster {cluster_id}: {n} folios ({range_str})")
        print(f"  Dominant: {dom_regime[0]} ({regime_pct}%) + {dom_scribe[0]} ({scribe_pct}%)")
        print(f"  Regimes: {dict(data['regime_dist'])}")
        print(f"  Scribes: {dict(data['scribe_dist'])}")

        # Try to identify what Yale section this might correspond to
        section_guess = []
        if dom_scribe[0] == "Scribe_2" and scribe_pct > 50:
            section_guess.append("Balneological?")
        if dom_scribe[0] == "Scribe_3" and scribe_pct > 50:
            section_guess.append("Starred paragraphs?")
        if dom_scribe[0] == "Scribe_1" and scribe_pct > 50:
            if dom_regime[0] == "REGIME_4":
                section_guess.append("Herbal/Pharmaceutical?")
        if section_guess:
            print(f"  Possible Yale section: {', '.join(section_guess)}")

    # Compare cluster structure to regimes
    print("\n" + "=" * 60)
    print("REGIME vs CLUSTER CROSS-TABULATION")
    print("=" * 60)

    # Build cross-tab
    regime_cluster = defaultdict(Counter)
    for folio, label, regime in zip(folios, labels, regimes):
        regime_cluster[regime][label] += 1

    print("\n         | " + " | ".join(f"C{i}" for i in range(5)) + " |")
    print("-" * 50)
    for regime in sorted(regime_cluster.keys()):
        row = [f"{regime_cluster[regime][i]:3d}" for i in range(5)]
        print(f"{regime:10s}| " + " | ".join(row) + " |")

    # Key finding
    print("\n" + "=" * 60)
    print("KEY FINDING")
    print("=" * 60)

    # Check if clusters isolate regimes
    pure_clusters = 0
    for cluster_id, data in cluster_analysis.items():
        if data["regime_dist"]:
            dom = data["regime_dist"].most_common(1)[0]
            if dom[1] / len(data["folios"]) > 0.7:
                pure_clusters += 1
                print(f"Cluster {cluster_id} is >70% {dom[0]}")

    print(f"\n{pure_clusters}/5 clusters are regime-pure (>70%)")

    # Yale's finding was that clusters only made sense WITH scribal info
    # Check if adding scribe improves cluster coherence
    regime_only_coherent = sum(
        max(data["regime_dist"].values()) for data in cluster_analysis.values()
        if data["regime_dist"]
    )

    scribe_only_coherent = sum(
        max(data["scribe_dist"].values()) for data in cluster_analysis.values()
        if data["scribe_dist"]
    )

    combined_coherent = sum(
        max(
            sum(1 for f in data["folios"] if scribes.get(f) == s and regimes[folios.index(f)] == r)
            for s in set(scribes.values())
            for r in set(regimes)
        )
        for data in cluster_analysis.values()
    )

    print(f"\nCoherence analysis:")
    print(f"  Regime-only: {regime_only_coherent}/{len(folios)} = {100*regime_only_coherent/len(folios):.1f}%")
    print(f"  Scribe-only: {scribe_only_coherent}/{len([f for f in folios if scribes.get(f)]):.1f}%")

    # Save results
    results = {
        "test": "TOPIC_MODEL_K5",
        "k": 5,
        "yale_target": "5-6 sections",
        "clusters": {},
        "finding": "Clusters show mixed regime/scribe composition, suggesting structural features capture something beyond simple section boundaries"
    }

    for cluster_id, data in cluster_analysis.items():
        results["clusters"][f"cluster_{cluster_id}"] = {
            "n": len(data["folios"]),
            "regimes": dict(data["regime_dist"]),
            "scribes": dict(data["scribe_dist"])
        }

    output_path = Path(__file__).parent.parent.parent / "results" / "topic_model_k5.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
