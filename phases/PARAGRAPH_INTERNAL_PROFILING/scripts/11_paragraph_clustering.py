"""
11_paragraph_clustering.py - Paragraph Clustering Analysis

Features for clustering:

A paragraphs:
- line_count, ri_rate, ri_initial_count, ri_final_count
- pp_compound_rate, has_linker (binary)
- folio_position (encoded), section (encoded)

B paragraphs:
- line_count, ht_rate, ht_delta
- is_gallows_initial, gallows_char (encoded)
- en_rate, fl_rate, fq_rate
- b_section (encoded)

Method:
1. Z-score normalize features
2. K-means with k = 2, 3, 4, 5
3. Silhouette score for optimal k
4. Report cluster centroids and assignments

Depends on: All previous scripts
"""

import json
import sys
from pathlib import Path
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def encode_categorical(value, categories):
    """One-hot encode a categorical variable."""
    return [1 if value == cat else 0 for cat in categories]

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    if not HAS_SKLEARN:
        print("scikit-learn not available. Skipping clustering analysis.")
        print("Install with: pip install scikit-learn")

        # Save placeholder results
        with open(results_dir / 'cluster_analysis.json', 'w') as f:
            json.dump({
                'status': 'skipped',
                'reason': 'scikit-learn not available'
            }, f, indent=2)
        return

    # Load profiles
    with open(results_dir / 'a_paragraph_profiles.json') as f:
        a_data = json.load(f)

    with open(results_dir / 'b_paragraph_profiles.json') as f:
        b_data = json.load(f)

    results = {
        'A': {},
        'B': {}
    }

    # === A PARAGRAPH CLUSTERING ===
    print("=== A PARAGRAPH CLUSTERING ===\n")

    a_profiles = a_data['profiles']

    # Build feature matrix
    a_features = []
    a_par_ids = []

    for p in a_profiles:
        if 'ri_profile' not in p or 'size' not in p:
            continue

        features = [
            p['size']['line_count'],
            p['size']['token_count'],
            p['ri_profile']['ri_rate'],
            p['ri_profile']['ri_initial_count'],
            p['ri_profile']['ri_final_count'],
            1 if p['ri_profile']['has_linker'] else 0
        ]

        # Encode folio_position
        pos_encoded = encode_categorical(p['folio_position'], ['first', 'middle', 'last', 'only'])
        features.extend(pos_encoded)

        # Encode section
        sec_encoded = encode_categorical(p.get('section', 'other'), ['H', 'P', 'T', 'other'])
        features.extend(sec_encoded)

        a_features.append(features)
        a_par_ids.append(p['par_id'])

    if len(a_features) < 10:
        print("Not enough A paragraphs for clustering")
    else:
        X_a = np.array(a_features)

        # Normalize
        scaler_a = StandardScaler()
        X_a_scaled = scaler_a.fit_transform(X_a)

        # Try different k values
        a_scores = {}
        for k in [2, 3, 4, 5]:
            if k >= len(a_features):
                continue
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_a_scaled)
            score = silhouette_score(X_a_scaled, labels)
            a_scores[k] = round(score, 3)
            print(f"  k={k}: silhouette={score:.3f}")

        # Best k
        best_k_a = max(a_scores, key=a_scores.get)
        print(f"\nBest k for A: {best_k_a} (silhouette={a_scores[best_k_a]})")

        # Final clustering
        kmeans_a = KMeans(n_clusters=best_k_a, random_state=42, n_init=10)
        a_labels = kmeans_a.fit_predict(X_a_scaled)

        # Cluster profiles
        a_cluster_profiles = {}
        for i in range(best_k_a):
            cluster_idx = [j for j, l in enumerate(a_labels) if l == i]
            cluster_pars = [a_profiles[a_par_ids.index(a_par_ids[j])] for j in cluster_idx]

            a_cluster_profiles[f'cluster_{i}'] = {
                'count': len(cluster_idx),
                'mean_lines': round(statistics.mean([p['size']['line_count'] for p in cluster_pars]), 2),
                'mean_ri_rate': round(statistics.mean([p['ri_profile']['ri_rate'] for p in cluster_pars]), 3),
                'linker_rate': round(sum(1 for p in cluster_pars if p['ri_profile']['has_linker']) / len(cluster_pars), 3)
            }

        results['A'] = {
            'silhouette_scores': a_scores,
            'best_k': best_k_a,
            'cluster_profiles': a_cluster_profiles
        }

        print("\nCluster profiles:")
        for name, profile in a_cluster_profiles.items():
            print(f"  {name}: n={profile['count']}, lines={profile['mean_lines']}, RI={profile['mean_ri_rate']}, linker={profile['linker_rate']}")

    # === B PARAGRAPH CLUSTERING ===
    print("\n=== B PARAGRAPH CLUSTERING ===\n")

    b_profiles = b_data['profiles']

    # Build feature matrix
    b_features = []
    b_par_ids = []

    for p in b_profiles:
        if 'ht_profile' not in p or 'size' not in p:
            continue

        features = [
            p['size']['line_count'],
            p['size']['token_count'],
            p['ht_profile']['ht_rate'],
            p['ht_profile']['ht_delta'],
            1 if p.get('initiation', {}).get('is_gallows_initial', False) else 0
        ]

        # Add role profile if available
        if 'role_profile' in p:
            features.extend([
                p['role_profile']['en_rate'],
                p['role_profile']['fl_rate'],
                p['role_profile']['fq_rate']
            ])
        else:
            features.extend([0, 0, 0])

        # Encode b_section
        sec_encoded = encode_categorical(p.get('b_section', 'other'),
                                         ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B', 'other'])
        features.extend(sec_encoded)

        # Encode gallows_char
        gchar = p.get('initiation', {}).get('gallows_char', None)
        gchar_encoded = encode_categorical(gchar, ['p', 't', 'k', 'f', None])
        features.extend(gchar_encoded)

        b_features.append(features)
        b_par_ids.append(p['par_id'])

    if len(b_features) < 10:
        print("Not enough B paragraphs for clustering")
    else:
        X_b = np.array(b_features)

        # Normalize
        scaler_b = StandardScaler()
        X_b_scaled = scaler_b.fit_transform(X_b)

        # Try different k values
        b_scores = {}
        for k in [2, 3, 4, 5]:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_b_scaled)
            score = silhouette_score(X_b_scaled, labels)
            b_scores[k] = round(score, 3)
            print(f"  k={k}: silhouette={score:.3f}")

        # Best k
        best_k_b = max(b_scores, key=b_scores.get)
        print(f"\nBest k for B: {best_k_b} (silhouette={b_scores[best_k_b]})")

        # Final clustering
        kmeans_b = KMeans(n_clusters=best_k_b, random_state=42, n_init=10)
        b_labels = kmeans_b.fit_predict(X_b_scaled)

        # Cluster profiles
        b_cluster_profiles = {}
        for i in range(best_k_b):
            cluster_idx = [j for j, l in enumerate(b_labels) if l == i]
            cluster_pars = [b_profiles[b_par_ids.index(b_par_ids[j])] for j in cluster_idx]

            # Get role stats if available
            en_rates = [p['role_profile']['en_rate'] for p in cluster_pars if 'role_profile' in p]
            fl_rates = [p['role_profile']['fl_rate'] for p in cluster_pars if 'role_profile' in p]

            b_cluster_profiles[f'cluster_{i}'] = {
                'count': len(cluster_idx),
                'mean_lines': round(statistics.mean([p['size']['line_count'] for p in cluster_pars]), 2),
                'mean_ht_delta': round(statistics.mean([p['ht_profile']['ht_delta'] for p in cluster_pars]), 3),
                'gallows_rate': round(sum(1 for p in cluster_pars if p.get('initiation', {}).get('is_gallows_initial', False)) / len(cluster_pars), 3),
                'mean_en_rate': round(statistics.mean(en_rates), 3) if en_rates else None,
                'mean_fl_rate': round(statistics.mean(fl_rates), 3) if fl_rates else None
            }

        results['B'] = {
            'silhouette_scores': b_scores,
            'best_k': best_k_b,
            'cluster_profiles': b_cluster_profiles
        }

        print("\nCluster profiles:")
        for name, profile in b_cluster_profiles.items():
            print(f"  {name}: n={profile['count']}, lines={profile['mean_lines']}, HT_delta={profile['mean_ht_delta']}, EN={profile['mean_en_rate']}")

    # Save
    with open(results_dir / 'cluster_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {results_dir}/cluster_analysis.json")

if __name__ == '__main__':
    main()
