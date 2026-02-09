"""
03_paragraph_clustering.py - Paragraph type classification

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Test C: Can we cluster paragraphs by structure, and do clusters correlate with ordinal?

Question: Do natural paragraph clusters emerge, and do they align with position?

Method:
1. Feature vector per paragraph: role proportions, HT rate, length, FL distribution
2. Cluster with K-means (varying K)
3. Measure Adjusted Rand Index between cluster assignment and position bin

Null model: Permute position bins, compare ARI

Builds on C853: 5 existing clusters (single-line 9%, long-EN 10%, standard 81%)
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

GALLOWS = {'k', 't', 'p', 'f'}
FL_INITIAL = {'ar', 'r'}
FL_LATE = {'al', 'l', 'ol'}
FL_TERMINAL = {'aly', 'am', 'y'}

def has_gallows_initial(word):
    if not word or not word.strip():
        return False
    return word[0] in GALLOWS

def load_raw_data():
    data_path = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['transcriber'] == 'H' and row['language'] == 'B':
                folio = row['folio']
                line = row['line_number']
                word = row['word']
                if '*' in word:
                    continue
                folio_lines[folio][line].append(word)

    return folio_lines

def detect_paragraphs(folio_data):
    paragraphs = defaultdict(list)
    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].extend(tokens)

    return paragraphs

def extract_features(tokens, morph):
    """Extract feature vector for clustering."""
    if not tokens or len(tokens) < 2:
        return None

    n = len(tokens)

    # Basic
    token_count = n
    mean_length = np.mean([len(w) for w in tokens])

    # Gallows
    gallows_count = sum(1 for w in tokens if has_gallows_initial(w))
    gallows_rate = gallows_count / n

    # Morphological
    prefixes = Counter()
    suffixes = Counter()
    fl_counts = Counter()

    for word in tokens:
        m = morph.extract(word)
        if m:
            if m.prefix:
                prefixes[m.prefix] += 1
            if m.suffix:
                suffixes[m.suffix] += 1
                if m.suffix in FL_INITIAL:
                    fl_counts['INITIAL'] += 1
                elif m.suffix in FL_LATE:
                    fl_counts['LATE'] += 1
                elif m.suffix in FL_TERMINAL:
                    fl_counts['TERMINAL'] += 1

    # Common prefix rates
    ch_rate = prefixes.get('ch', 0) / n
    sh_rate = prefixes.get('sh', 0) / n
    qo_rate = prefixes.get('qo', 0) / n
    ot_rate = prefixes.get('ot', 0) / n

    # Suffix rates
    y_rate = suffixes.get('y', 0) / n
    r_rate = suffixes.get('r', 0) / n
    l_rate = suffixes.get('l', 0) / n

    # FL distribution
    fl_initial_rate = fl_counts.get('INITIAL', 0) / n
    fl_late_rate = fl_counts.get('LATE', 0) / n
    fl_terminal_rate = fl_counts.get('TERMINAL', 0) / n

    return np.array([
        token_count / 100,
        mean_length / 10,
        gallows_rate,
        ch_rate,
        sh_rate,
        qo_rate,
        ot_rate,
        y_rate,
        r_rate,
        l_rate,
        fl_initial_rate,
        fl_late_rate,
        fl_terminal_rate
    ])

def main():
    folio_data = load_raw_data()
    morph = Morphology()

    # Collect all paragraphs
    paragraphs = []
    for folio in sorted(folio_data.keys()):
        paras = detect_paragraphs(folio_data[folio])
        n_paras = len(paras)
        if n_paras < 2:
            continue

        for ordinal in sorted(paras.keys()):
            tokens = paras[ordinal]
            features = extract_features(tokens, morph)
            if features is None:
                continue

            rel_pos = (ordinal - 1) / (n_paras - 1) if n_paras > 1 else 0
            position_bin = 0 if rel_pos < 0.33 else (2 if rel_pos > 0.67 else 1)

            paragraphs.append({
                'folio': folio,
                'ordinal': ordinal,
                'position_bin': position_bin,  # 0=early, 1=middle, 2=late
                'features': features,
                'token_count': len(tokens)
            })

    print("=" * 70)
    print("TEST C: PARAGRAPH TYPE CLASSIFICATION")
    print("=" * 70)
    print(f"\nTotal paragraphs: {len(paragraphs)}")

    # Build feature matrix
    X = np.array([p['features'] for p in paragraphs])
    position_labels = np.array([p['position_bin'] for p in paragraphs])

    # Try different K values
    print(f"\n--- K-Means Clustering ---")

    results = {
        'n_paragraphs': len(paragraphs),
        'clustering': []
    }

    best_ari = -1
    best_k = 0

    for k in range(2, 8):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)

        silhouette = silhouette_score(X, cluster_labels)
        ari = adjusted_rand_score(position_labels, cluster_labels)

        # Null model: permute position labels
        null_aris = []
        for _ in range(100):
            perm_labels = np.random.permutation(position_labels)
            null_ari = adjusted_rand_score(perm_labels, cluster_labels)
            null_aris.append(null_ari)

        null_mean = np.mean(null_aris)
        null_std = np.std(null_aris)
        z_score = (ari - null_mean) / null_std if null_std > 0 else 0

        print(f"\nK={k}:")
        print(f"  Silhouette: {silhouette:.3f}")
        print(f"  ARI with position: {ari:.3f}")
        print(f"  Null ARI: {null_mean:.3f} (sd={null_std:.3f})")
        print(f"  Z-score: {z_score:.2f}")

        results['clustering'].append({
            'k': k,
            'silhouette': float(silhouette),
            'ari_with_position': float(ari),
            'null_ari_mean': float(null_mean),
            'null_ari_std': float(null_std),
            'z_score': float(z_score)
        })

        if ari > best_ari:
            best_ari = ari
            best_k = k

    # Analyze best clustering
    print(f"\n--- Best ARI: K={best_k} (ARI={best_ari:.3f}) ---")

    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    best_labels = kmeans.fit_predict(X)

    # Cluster composition by position
    print(f"\nCluster composition by position:")
    for c in range(best_k):
        cluster_mask = best_labels == c
        cluster_positions = position_labels[cluster_mask]

        early_pct = (cluster_positions == 0).sum() / len(cluster_positions) * 100
        mid_pct = (cluster_positions == 1).sum() / len(cluster_positions) * 100
        late_pct = (cluster_positions == 2).sum() / len(cluster_positions) * 100

        cluster_sizes = [p['token_count'] for i, p in enumerate(paragraphs) if best_labels[i] == c]
        mean_size = np.mean(cluster_sizes)

        print(f"  Cluster {c} (n={cluster_mask.sum()}, mean size={mean_size:.0f} tokens):")
        print(f"    Early: {early_pct:.0f}%, Middle: {mid_pct:.0f}%, Late: {late_pct:.0f}%")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if best_ari > 0.2:
        print(f"\nSTRONG CLUSTER-POSITION ALIGNMENT (ARI={best_ari:.2f}):")
        print("  Paragraph clusters correlate with ordinal position.")
        print("  Would challenge C857 - position IS structurally meaningful.")
    elif best_ari > 0.05:
        print(f"\nWEAK CLUSTER-POSITION ALIGNMENT (ARI={best_ari:.2f}):")
        print("  Some association between cluster and position.")
        print("  Consistent with existing constraints - weak but present.")
    else:
        print(f"\nNO CLUSTER-POSITION ALIGNMENT (ARI={best_ari:.2f}):")
        print("  Paragraph clusters independent of ordinal position.")
        print("  Strong support for C855 (PARALLEL_PROGRAMS).")

    # Save results
    results['summary'] = {
        'best_k': best_k,
        'best_ari': float(best_ari),
        'interpretation': 'strong' if best_ari > 0.2 else ('weak' if best_ari > 0.05 else 'none')
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/03_paragraph_clustering.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
