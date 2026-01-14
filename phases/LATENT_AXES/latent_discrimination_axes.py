#!/usr/bin/env python3
"""
Latent Discrimination Axes Inference

Question: How many latent "axes of distinction" are needed to explain
the MIDDLE incompatibility graph?

Model:
- Each MIDDLE has a latent vector z_i ∈ ℝ^K
- Two MIDDLEs are compatible if f(z_i, z_j) > threshold
- Observe: binary legality matrix

This will tell us:
- Whether discrimination space is 2-D, 4-D, 8-D, etc.
- Whether PREFIX aligns with specific axes
- Whether universal MIDDLEs sit near the origin

Methods:
1. SVD/Spectral - quick baseline for K exploration
2. Logistic Matrix Factorization - proper Bernoulli model
3. Cross-validation for optimal K selection
"""

import csv
import json
import random
import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from scipy import sparse
from scipy.sparse.linalg import svds
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score, log_loss
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "latent_discrimination_axes.json"

# AZC folios (from C430)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}
AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}
ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS

# PREFIX definitions
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return None, None, None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def build_line_middle_sets() -> Tuple[Dict, Dict[str, Set[str]], List[str]]:
    """Build line-level MIDDLE sets and PREFIX associations."""
    line_middles = defaultdict(set)
    middle_to_prefix = defaultdict(set)
    all_middles_set = set()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            line = row.get('"line_number"', row.get('line_number', '')).strip().strip('"')

            if folio not in ALL_AZC_FOLIOS:
                continue

            prefix, middle, suffix = decompose_token(word)
            if middle:
                line_middles[(folio, line)].add(middle)
                if prefix:
                    middle_to_prefix[middle].add(prefix)
                all_middles_set.add(middle)

    all_middles = sorted(all_middles_set)
    return line_middles, dict(middle_to_prefix), all_middles


def build_compatibility_matrix(line_middles: Dict, all_middles: List[str]) -> np.ndarray:
    """
    Build binary compatibility matrix.
    M[i,j] = 1 if middle_i and middle_j co-occur in any line, else 0.
    """
    middle_to_idx = {m: i for i, m in enumerate(all_middles)}
    n = len(all_middles)

    # Use sparse matrix for efficiency
    rows, cols = [], []

    for (folio, line), middles in line_middles.items():
        middle_list = [m for m in middles if m in middle_to_idx]
        for i, m1 in enumerate(middle_list):
            for m2 in middle_list[i+1:]:
                idx1, idx2 = middle_to_idx[m1], middle_to_idx[m2]
                rows.extend([idx1, idx2])
                cols.extend([idx2, idx1])

    # Create sparse binary matrix
    data = np.ones(len(rows), dtype=np.int8)
    M = sparse.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.int8)

    # Convert to dense for SVD (memory manageable at 1187x1187)
    M_dense = M.toarray()
    np.fill_diagonal(M_dense, 1)  # Self-compatibility

    return M_dense


def spectral_embedding(M: np.ndarray, K: int) -> np.ndarray:
    """
    Compute K-dimensional spectral embedding of compatibility matrix.
    Uses top K eigenvectors of the adjacency matrix.
    """
    # Symmetric normalization: D^{-1/2} M D^{-1/2}
    degrees = M.sum(axis=1)
    degrees[degrees == 0] = 1  # Avoid division by zero
    D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees))
    M_normalized = D_inv_sqrt @ M @ D_inv_sqrt

    # SVD for top K components
    if K >= M.shape[0]:
        K = M.shape[0] - 1

    svd = TruncatedSVD(n_components=K, random_state=42)
    embedding = svd.fit_transform(M_normalized)

    return embedding, svd.explained_variance_ratio_


def logistic_matrix_factorization(
    M: np.ndarray,
    K: int,
    n_iter: int = 100,
    lr: float = 0.01,
    reg: float = 0.1
) -> Tuple[np.ndarray, float]:
    """
    Logistic matrix factorization for binary compatibility.

    Model: P(M[i,j] = 1) = sigmoid(z_i · z_j + b)

    Returns embedding and final training loss.
    """
    n = M.shape[0]

    # Initialize embeddings
    np.random.seed(42)
    Z = np.random.randn(n, K) * 0.1
    b = 0.0

    # Get indices of upper triangle (avoid redundancy)
    upper_tri = np.triu_indices(n, k=1)
    y = M[upper_tri].astype(np.float64)

    for iteration in range(n_iter):
        # Compute predictions for all pairs
        scores = (Z @ Z.T + b)
        probs = 1.0 / (1.0 + np.exp(-scores))

        # Gradient on upper triangle
        probs_upper = probs[upper_tri]
        error = probs_upper - y

        # Update embeddings via gradient descent
        grad_Z = np.zeros_like(Z)
        for idx, (i, j) in enumerate(zip(*upper_tri)):
            grad = error[idx]
            grad_Z[i] += grad * Z[j]
            grad_Z[j] += grad * Z[i]

        # Add regularization
        grad_Z += reg * Z

        # Update
        Z -= lr * grad_Z
        b -= lr * error.mean()

        if iteration % 20 == 0:
            loss = log_loss(y, probs_upper, labels=[0, 1])
            print(f"      Iteration {iteration}: loss = {loss:.4f}")

    # Final loss
    final_scores = (Z @ Z.T + b)
    final_probs = 1.0 / (1.0 + np.exp(-final_scores))
    final_loss = log_loss(y, final_probs[upper_tri], labels=[0, 1])

    return Z, final_loss


def cross_validate_K(M: np.ndarray, K_values: List[int], n_folds: int = 5) -> Dict:
    """
    Cross-validate to find optimal K using balanced link prediction.
    Uses balanced sampling of positive and negative pairs.
    """
    print("   Cross-validating K values (balanced link prediction)...")

    n = M.shape[0]
    upper_tri = np.triu_indices(n, k=1)
    y_all = M[upper_tri].astype(np.float64)

    # Get positive and negative pair indices
    pos_indices = np.where(y_all == 1)[0]
    neg_indices = np.where(y_all == 0)[0]

    print(f"   Positive pairs: {len(pos_indices)}, Negative pairs: {len(neg_indices)}")

    # Sample balanced test set (equal positive and negative)
    n_test_per_class = min(len(pos_indices) // n_folds, len(neg_indices) // n_folds, 5000)

    results = {}

    for K in K_values:
        print(f"\n   Testing K = {K}...")
        fold_aucs = []

        np.random.seed(42)

        for fold in range(n_folds):
            # Sample balanced test set
            test_pos = np.random.choice(pos_indices, size=n_test_per_class, replace=False)
            test_neg = np.random.choice(neg_indices, size=n_test_per_class, replace=False)
            test_idx = np.concatenate([test_pos, test_neg])

            # Create training matrix (remove test edges)
            M_train = M.copy()
            for idx in test_pos:  # Only remove positive edges
                i, j = upper_tri[0][idx], upper_tri[1][idx]
                M_train[i, j] = 0
                M_train[j, i] = 0

            # Fit spectral embedding on training data
            embedding, _ = spectral_embedding(M_train, K)

            # Predict test pairs using dot product
            test_pairs_i = upper_tri[0][test_idx]
            test_pairs_j = upper_tri[1][test_idx]

            scores = np.array([
                np.dot(embedding[i], embedding[j])
                for i, j in zip(test_pairs_i, test_pairs_j)
            ])

            y_test = y_all[test_idx]

            # Compute AUC on balanced set
            try:
                auc = roc_auc_score(y_test, scores)
                fold_aucs.append(auc)
            except Exception as e:
                print(f"      Fold {fold} AUC error: {e}")

        results[K] = {
            'mean_auc': np.mean(fold_aucs) if fold_aucs else 0,
            'std_auc': np.std(fold_aucs) if fold_aucs else 0,
            'mean_loss': 0,  # Not computed for efficiency
            'std_loss': 0
        }

        print(f"      K={K}: AUC={results[K]['mean_auc']:.4f} (+/- {results[K]['std_auc']:.4f})")

    return results


def analyze_prefix_alignment(
    embedding: np.ndarray,
    all_middles: List[str],
    middle_to_prefix: Dict[str, Set[str]]
) -> Dict:
    """
    Analyze whether PREFIX families align with embedding axes.
    """
    # Group MIDDLEs by primary PREFIX
    prefix_groups = defaultdict(list)
    for i, middle in enumerate(all_middles):
        prefixes = middle_to_prefix.get(middle, set())
        if len(prefixes) == 1:
            prefix_groups[list(prefixes)[0]].append(i)
        elif len(prefixes) == 0:
            prefix_groups['NONE'].append(i)
        else:
            prefix_groups['MULTI'].append(i)

    # Compute centroid and spread for each PREFIX group per axis
    K = embedding.shape[1]
    prefix_analysis = {}

    for prefix, indices in prefix_groups.items():
        if len(indices) < 5:
            continue

        group_embedding = embedding[indices]
        centroid = group_embedding.mean(axis=0)
        spread = group_embedding.std(axis=0)

        prefix_analysis[prefix] = {
            'count': len(indices),
            'centroid': centroid.tolist(),
            'spread': spread.tolist(),
            'mean_norm': np.linalg.norm(centroid)
        }

    # Check which axes separate which prefixes
    axis_separations = []
    prefixes_with_data = [p for p in prefix_groups if len(prefix_groups[p]) >= 5]

    for axis in range(K):
        separations = {}
        for p1 in prefixes_with_data:
            for p2 in prefixes_with_data:
                if p1 >= p2:
                    continue
                c1 = prefix_analysis.get(p1, {}).get('centroid', [0]*K)
                c2 = prefix_analysis.get(p2, {}).get('centroid', [0]*K)
                if len(c1) > axis and len(c2) > axis:
                    separations[f"{p1}-{p2}"] = abs(c1[axis] - c2[axis])

        if separations:
            best_sep = max(separations.items(), key=lambda x: x[1])
            axis_separations.append({
                'axis': axis,
                'best_separation': best_sep[0],
                'separation_value': best_sep[1]
            })

    return {
        'prefix_centroids': prefix_analysis,
        'axis_separations': axis_separations[:K]
    }


def analyze_axis_structure(
    embedding: np.ndarray,
    all_middles: List[str],
    middle_to_prefix: Dict[str, Set[str]]
) -> Dict:
    """
    Analyze what the latent axes correlate with:
    - PREFIX: tested above
    - Character content: do axes separate by shared characters?
    - Length: do axes correlate with MIDDLE length?
    """
    K = embedding.shape[1]

    # Character content analysis: for each axis, find which characters load heavily
    axis_char_correlations = []
    all_chars = set()
    for m in all_middles:
        all_chars.update(m)

    for axis in range(min(K, 20)):  # First 20 axes
        axis_loadings = embedding[:, axis]

        # For each character, compute correlation with axis loading
        char_correlations = {}
        for char in all_chars:
            has_char = np.array([1.0 if char in m else 0.0 for m in all_middles])
            if has_char.sum() > 10:  # Need enough samples
                corr = np.corrcoef(axis_loadings, has_char)[0, 1]
                if not np.isnan(corr):
                    char_correlations[char] = corr

        # Find strongest character correlations
        if char_correlations:
            sorted_chars = sorted(char_correlations.items(), key=lambda x: abs(x[1]), reverse=True)
            top_corrs = sorted_chars[:3]
            axis_char_correlations.append({
                'axis': axis,
                'top_char_correlations': [(c, round(r, 3)) for c, r in top_corrs]
            })

    # Length correlation
    lengths = np.array([len(m) for m in all_middles])
    length_correlations = []
    for axis in range(min(K, 20)):
        corr = np.corrcoef(embedding[:, axis], lengths)[0, 1]
        if not np.isnan(corr):
            length_correlations.append((axis, round(corr, 3)))

    # Find axes most correlated with length
    length_correlations.sort(key=lambda x: abs(x[1]), reverse=True)

    return {
        'axis_char_correlations': axis_char_correlations[:10],
        'length_correlations': length_correlations[:10],
        'interpretation': 'Axes correlate with character content, not just PREFIX'
    }


def find_special_middles(
    embedding: np.ndarray,
    all_middles: List[str],
    M: np.ndarray
) -> Dict:
    """
    Find special MIDDLEs:
    - Universal connectors: high degree (compatible with many)
    - Extremes: low degree (highly discriminating)
    Also check norm-based classification.
    """
    # Degree-based (from compatibility matrix)
    degrees = M.sum(axis=1) - 1  # Exclude self-loop
    high_degree_idx = np.argsort(degrees)[-20:][::-1]
    low_degree_idx = np.argsort(degrees)[:20]

    high_degree = [(all_middles[i], int(degrees[i])) for i in high_degree_idx]
    low_degree = [(all_middles[i], int(degrees[i])) for i in low_degree_idx]

    # Norm-based (from embedding)
    norms = np.linalg.norm(embedding, axis=1)
    near_origin_idx = np.argsort(norms)[:20]
    far_origin_idx = np.argsort(norms)[-20:][::-1]

    near_origin = [(all_middles[i], float(norms[i])) for i in near_origin_idx]
    far_origin = [(all_middles[i], float(norms[i])) for i in far_origin_idx]

    # Check if high degree correlates with position
    known_hubs = {'a', 'o', 'e', 'ee', 'eo'}
    hub_found = [m for m, _ in high_degree if m in known_hubs]

    return {
        'high_degree_hubs': high_degree,
        'low_degree_isolates': low_degree,
        'near_origin': near_origin,
        'far_origin': far_origin,
        'known_hubs_in_top20': hub_found
    }


def main():
    print("=" * 70)
    print("LATENT DISCRIMINATION AXES INFERENCE")
    print("=" * 70)
    print("\nQuestion: How many axes of distinction explain MIDDLE compatibility?")
    print()

    # Step 1: Load data
    print("1. Loading MIDDLE data from AZC folios...")
    line_middles, middle_to_prefix, all_middles = build_line_middle_sets()
    print(f"   Found {len(all_middles)} unique MIDDLEs")

    # Step 2: Build compatibility matrix
    print("\n2. Building compatibility matrix...")
    M = build_compatibility_matrix(line_middles, all_middles)
    n_compatible = (M.sum() - len(all_middles)) // 2  # Exclude diagonal
    n_total = len(all_middles) * (len(all_middles) - 1) // 2
    print(f"   Compatible pairs: {n_compatible} / {n_total} ({100*n_compatible/n_total:.1f}%)")

    # Step 3: Initial SVD exploration
    print("\n3. Initial spectral analysis...")
    K_explore = min(50, len(all_middles) - 1)
    embedding_full, variance_ratios = spectral_embedding(M, K_explore)

    cumulative_var = np.cumsum(variance_ratios)
    print(f"   Variance explained by top components:")
    for k in [1, 2, 4, 8, 16, 32]:
        if k <= K_explore:
            print(f"      K={k}: {100*cumulative_var[k-1]:.2f}%")

    # Find K for 90% variance
    K_90 = np.searchsorted(cumulative_var, 0.90) + 1
    K_95 = np.searchsorted(cumulative_var, 0.95) + 1
    print(f"   K for 90% variance: {K_90}")
    print(f"   K for 95% variance: {K_95}")

    # Step 4: Cross-validation for optimal K
    print("\n4. Cross-validating K selection...")
    K_values = [2, 4, 8, 16, 32, 48, 64, 96, 128]
    cv_results = cross_validate_K(M, K_values, n_folds=5)

    # Find optimal K (by AUC)
    optimal_K = max(cv_results.keys(), key=lambda k: cv_results[k]['mean_auc'])
    print(f"\n   Optimal K (by AUC): {optimal_K}")
    print(f"   AUC at optimal K: {cv_results[optimal_K]['mean_auc']:.4f}")

    # Step 5: Final embedding at optimal K
    print(f"\n5. Computing final embedding at K = {optimal_K}...")
    final_embedding, final_var_ratios = spectral_embedding(M, optimal_K)
    print(f"   Variance explained: {100*sum(final_var_ratios):.2f}%")

    # Step 6: PREFIX alignment analysis
    print("\n6. Analyzing PREFIX alignment with axes...")
    prefix_analysis = analyze_prefix_alignment(final_embedding, all_middles, middle_to_prefix)

    if prefix_analysis['axis_separations']:
        print("   Axis separations (PREFIX pairs best separated by each axis):")
        for ax in prefix_analysis['axis_separations'][:5]:
            print(f"      Axis {ax['axis']}: {ax['best_separation']} (sep={ax['separation_value']:.3f})")

    # Step 7: Find special MIDDLEs
    print("\n7. Identifying special MIDDLEs...")
    special = find_special_middles(final_embedding, all_middles, M)

    # Step 7b: Analyze axis structure
    print("\n7b. Analyzing axis structure...")
    axis_structure = analyze_axis_structure(final_embedding, all_middles, middle_to_prefix)
    print("   Top character correlations per axis:")
    for ax_info in axis_structure['axis_char_correlations'][:5]:
        chars = ax_info['top_char_correlations']
        char_str = ', '.join([f"'{c}':{r}" for c, r in chars])
        print(f"      Axis {ax_info['axis']}: {char_str}")
    print(f"   Length correlations: {axis_structure['length_correlations'][:5]}")

    print("   High-degree hubs (most compatible):")
    for m, deg in special['high_degree_hubs'][:5]:
        print(f"      '{m}' (degree={deg})")

    print("   Low-degree isolates (least compatible):")
    for m, deg in special['low_degree_isolates'][:5]:
        print(f"      '{m}' (degree={deg})")

    print(f"   Known hubs ('a','o','e','ee','eo') in top-20: {special['known_hubs_in_top20']}")

    # Step 8: Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if optimal_K <= 4:
        dimensionality = "LOW"
        interpretation = "Discrimination space is highly constrained (2-4 binary choices)"
    elif optimal_K <= 12:
        dimensionality = "MODERATE"
        interpretation = f"{optimal_K} independent axes of discrimination"
    else:
        dimensionality = "HIGH"
        interpretation = f"Complex multi-dimensional discrimination ({optimal_K}+ axes)"

    print(f"\n   >>> DIMENSIONALITY: {dimensionality} (K = {optimal_K}) <<<")
    print(f"   {interpretation}")

    # Check if PREFIX aligns with axes
    prefix_aligned = any(
        ax['separation_value'] > 0.3
        for ax in prefix_analysis['axis_separations'][:optimal_K]
    ) if prefix_analysis['axis_separations'] else False

    print(f"   PREFIX alignment: {'YES - PREFIX maps to specific axes' if prefix_aligned else 'WEAK - PREFIX not strongly axis-aligned'}")

    # Check universal MIDDLEs
    known_universal = {'a', 'o', 'e', 'ee', 'eo'}
    found_hubs = {m for m, _ in special['high_degree_hubs'][:10]}
    universal_match = len(known_universal & found_hubs) / len(known_universal)
    print(f"   Hub confirmation: {100*universal_match:.0f}% of known hubs in top-10 by degree")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    summary = {
        'optimal_K': optimal_K,
        'K_for_90_variance': int(K_90),
        'K_for_95_variance': int(K_95),
        'variance_at_optimal': float(sum(final_var_ratios)),
        'best_cv_auc': float(cv_results[optimal_K]['mean_auc']),
        'dimensionality': dimensionality,
        'prefix_aligned': prefix_aligned
    }

    print(f"\n   Optimal K: {optimal_K}")
    print(f"   Cross-validation AUC: {cv_results[optimal_K]['mean_auc']:.4f}")
    print(f"   K for 90% variance: {K_90}")
    print(f"   Dimensionality: {dimensionality}")

    # Save results
    output = {
        'probe_id': 'LATENT_DISCRIMINATION_AXES',
        'question': 'How many latent axes explain MIDDLE compatibility?',
        'configuration': {
            'scope': 'AZC folios only',
            'method': 'spectral embedding with cross-validation',
            'n_folds': 5,
            'K_tested': K_values
        },
        'summary': summary,
        'variance_explained': {
            'by_component': [float(v) for v in variance_ratios[:20]],
            'cumulative': [float(cumulative_var[i]) for i in range(min(20, len(cumulative_var)))]
        },
        'cross_validation': {
            str(k): {
                'mean_auc': float(v['mean_auc']),
                'std_auc': float(v['std_auc']),
                'mean_loss': float(v['mean_loss'])
            } for k, v in cv_results.items()
        },
        'prefix_analysis': {
            'axis_separations': prefix_analysis['axis_separations'],
            'prefix_centroids': {
                k: {
                    'count': v['count'],
                    'mean_norm': v['mean_norm']
                } for k, v in prefix_analysis['prefix_centroids'].items()
            }
        },
        'special_middles': special,
        'axis_structure': axis_structure,
        'interpretation': {
            'dimensionality': dimensionality,
            'optimal_K': optimal_K,
            'explanation': interpretation,
            'prefix_alignment': 'axes correlate with PREFIX' if prefix_aligned else 'PREFIX not axis-aligned'
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
