#!/usr/bin/env python3
"""
T4: Morphological Derivation of Dimensionality
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Can we derive the effective dimensionality from the known morphological
composition rules (C267, C510-C513)?

If MIDDLEs are built from sub-components (C267: compositional morphology),
then compatibility should be determined by shared/conflicting sub-components.
The dimensionality of the discrimination space should equal the number of
independent binary features needed to encode all compatibility relations.

Key question: Is D ≈ 128 because there are ~128 independent morphological
features, or is it an artifact of the embedding method?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_matrix_and_middles():
    """Load compatibility matrix and rebuild MIDDLE list with morphology."""
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')

    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    middle_to_prefixes = defaultdict(set)
    middle_to_suffixes = defaultdict(set)

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
            if m.prefix:
                middle_to_prefixes[m.middle].add(m.prefix)
            if m.suffix:
                middle_to_suffixes[m.middle].add(m.suffix)

    all_middles = sorted(all_middles_set)
    return M, all_middles, middle_to_prefixes, middle_to_suffixes


def character_feature_encoding(all_middles):
    """Encode each MIDDLE as a binary feature vector based on character composition.

    Features:
    - Character presence (does MIDDLE contain 'a', 'e', 'o', etc.)
    - Character bigrams (does MIDDLE contain 'ch', 'sh', 'ai', etc.)
    - Character position (does MIDDLE start with 'e', end with 'd', etc.)
    - Length category
    """
    # Character features
    all_chars = sorted(set(c for m in all_middles for c in m))
    print(f"  Unique characters in MIDDLEs: {len(all_chars)}")
    print(f"  Characters: {''.join(all_chars)}")

    # Bigrams
    all_bigrams = set()
    for m in all_middles:
        for i in range(len(m) - 1):
            all_bigrams.add(m[i:i+2])
    all_bigrams = sorted(all_bigrams)
    print(f"  Unique bigrams: {len(all_bigrams)}")

    # Build feature matrix
    features = []
    feature_names = []

    # Character presence
    for c in all_chars:
        features.append([1 if c in m else 0 for m in all_middles])
        feature_names.append(f"has_{c}")

    # Bigram presence
    for bg in all_bigrams:
        features.append([1 if bg in m else 0 for m in all_middles])
        feature_names.append(f"has_{bg}")

    # Start/end character
    for c in all_chars:
        features.append([1 if m.startswith(c) else 0 for m in all_middles])
        feature_names.append(f"starts_{c}")
        features.append([1 if m.endswith(c) else 0 for m in all_middles])
        feature_names.append(f"ends_{c}")

    # Length features
    for length in range(1, 8):
        features.append([1 if len(m) == length else 0 for m in all_middles])
        feature_names.append(f"len_{length}")

    X = np.array(features).T  # n_middles × n_features
    print(f"  Total features: {X.shape[1]}")
    print(f"  Feature matrix shape: {X.shape}")

    # Remove constant columns
    col_var = X.var(axis=0)
    non_const = col_var > 0
    X = X[:, non_const]
    feature_names = [f for f, nc in zip(feature_names, non_const) if nc]
    print(f"  Non-constant features: {X.shape[1]}")

    return X, feature_names


def feature_based_compatibility_prediction(M, X):
    """How well can character features predict compatibility?

    If character features fully explain compatibility, then the
    dimensionality is bounded by the number of independent features.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    n = M.shape[0]
    upper_tri = np.triu_indices(n, k=1)
    y = M[upper_tri].astype(np.float64)

    # For each pair, feature = |x_i - x_j| (element-wise absolute difference)
    # or x_i * x_j (element-wise AND), or concatenated features
    print(f"\n  Building pair features...")

    # Sample balanced pairs (full matrix too large)
    pos_idx = np.where(y == 1)[0]
    neg_idx = np.where(y == 0)[0]
    n_sample = min(10000, len(pos_idx))

    np.random.seed(42)
    sample_pos = np.random.choice(pos_idx, n_sample, replace=False)
    sample_neg = np.random.choice(neg_idx, n_sample, replace=False)
    sample_idx = np.concatenate([sample_pos, sample_neg])
    np.random.shuffle(sample_idx)

    pairs_i = upper_tri[0][sample_idx]
    pairs_j = upper_tri[1][sample_idx]
    y_sample = y[sample_idx]

    # Feature: element-wise product (shared features)
    X_pairs = X[pairs_i] * X[pairs_j]

    # Train/test split
    n_train = int(0.8 * len(y_sample))
    X_train, X_test = X_pairs[:n_train], X_pairs[n_train:]
    y_train, y_test = y_sample[:n_train], y_sample[n_train:]

    # Logistic regression
    print(f"  Training logistic regression on {n_train} pairs...")
    lr = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    lr.fit(X_train, y_train)

    y_pred = lr.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred)
    accuracy = lr.score(X_test, y_test)

    print(f"  AUC: {auc:.4f}")
    print(f"  Accuracy: {accuracy:.4f}")

    # Feature importance (top coefficients)
    return {
        'auc': float(auc),
        'accuracy': float(accuracy),
        'n_features': int(X_pairs.shape[1]),
        'n_train': int(n_train),
        'n_test': int(len(y_test)),
    }


def independent_feature_count(X):
    """How many independent features are there?

    PCA on the binary feature matrix to find the effective rank.
    """
    from sklearn.decomposition import PCA

    # Center the features
    X_centered = X - X.mean(axis=0)

    # PCA
    n_components = min(X.shape)
    pca = PCA(n_components=n_components)
    pca.fit(X_centered)

    # Cumulative variance
    cumvar = np.cumsum(pca.explained_variance_ratio_)

    k_90 = np.searchsorted(cumvar, 0.90) + 1
    k_95 = np.searchsorted(cumvar, 0.95) + 1
    k_99 = np.searchsorted(cumvar, 0.99) + 1

    print(f"\n  PCA on feature matrix ({X.shape[0]}x{X.shape[1]}):")
    print(f"    K for 90% variance: {k_90}")
    print(f"    K for 95% variance: {k_95}")
    print(f"    K for 99% variance: {k_99}")

    # Effective rank via spectral entropy
    pos_var = pca.explained_variance_ratio_[pca.explained_variance_ratio_ > 0]
    spectral_entropy = -np.sum(pos_var * np.log(pos_var))
    effective_rank = np.exp(spectral_entropy)
    print(f"    Effective rank: {effective_rank:.1f}")

    return {
        'k_90': int(k_90),
        'k_95': int(k_95),
        'k_99': int(k_99),
        'effective_rank': float(effective_rank),
        'n_features_raw': int(X.shape[1]),
    }


def information_content_analysis(M, all_middles):
    """How many bits does the compatibility matrix encode?

    Entropy of each row tells us how much information that MIDDLE
    carries about its discrimination pattern.
    """
    n = M.shape[0]
    degrees = M.sum(axis=1) - 1  # exclude self

    # Per-row entropy (binary entropy of compatibility vector)
    row_entropies = []
    for i in range(n):
        row = M[i, :].copy()
        row[i] = 0  # exclude self
        p = row.sum() / (n - 1)
        if 0 < p < 1:
            h = -p * np.log2(p) - (1 - p) * np.log2(1 - p)
        else:
            h = 0
        row_entropies.append(h)

    row_entropies = np.array(row_entropies)

    print(f"\n  Per-row binary entropy:")
    print(f"    Mean: {row_entropies.mean():.4f} bits")
    print(f"    Range: {row_entropies.min():.4f} - {row_entropies.max():.4f}")

    # Total matrix entropy (assuming independence — upper bound)
    total_bits_upper = n * row_entropies.mean()
    print(f"    Total entropy (independence upper bound): {total_bits_upper:.1f} bits")

    # Joint entropy via SVD rank — the matrix can be described by
    # rank * n bits approximately
    eigs = np.load(RESULTS_DIR / 't1_eigenvalues.npy')
    pos_eigs = eigs[eigs > 1.0]
    approx_bits = len(pos_eigs) * np.log2(n)
    print(f"    Approx description length (rank × log2(n)): {approx_bits:.1f} bits")
    print(f"    This suggests ~{len(pos_eigs)} independent discrimination axes")

    # Mutual information between rows
    # Sample 1000 random pairs, compute MI
    np.random.seed(42)
    mi_samples = []
    for _ in range(1000):
        i, j = np.random.randint(0, n, 2)
        if i == j:
            continue
        ri = M[i, :].copy()
        rj = M[j, :].copy()
        ri[i], ri[j] = 0, 0
        rj[i], rj[j] = 0, 0
        # Compute MI
        n_pairs = n - 2
        p00 = np.sum((ri == 0) & (rj == 0)) / n_pairs
        p01 = np.sum((ri == 0) & (rj == 1)) / n_pairs
        p10 = np.sum((ri == 1) & (rj == 0)) / n_pairs
        p11 = np.sum((ri == 1) & (rj == 1)) / n_pairs
        pi = ri.sum() / n_pairs
        pj = rj.sum() / n_pairs
        mi = 0
        for pxy, px, py in [(p00, 1-pi, 1-pj), (p01, 1-pi, pj),
                             (p10, pi, 1-pj), (p11, pi, pj)]:
            if pxy > 0 and px > 0 and py > 0:
                mi += pxy * np.log2(pxy / (px * py))
        mi_samples.append(mi)

    mean_mi = np.mean(mi_samples)
    print(f"    Mean row-pair MI: {mean_mi:.4f} bits")
    print(f"    (Low MI = rows are largely independent = high dimensionality)")

    return {
        'mean_row_entropy': float(row_entropies.mean()),
        'total_entropy_upper': float(total_bits_upper),
        'approx_description_bits': float(approx_bits),
        'n_eigenvalues_gt1': int(len(pos_eigs)),
        'mean_row_pair_mi': float(mean_mi),
    }


def run():
    print("=" * 70)
    print("T4: Morphological Derivation of Dimensionality")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    M, all_middles, middle_to_prefixes, middle_to_suffixes = load_matrix_and_middles()
    n = len(all_middles)
    print(f"  Matrix: {n}x{n}")
    print(f"  MIDDLEs: {n}")

    # Character feature encoding
    print("\n[1/4] Character feature encoding...")
    X, feature_names = character_feature_encoding(all_middles)

    # Independent feature count
    print("\n[2/4] Independent feature analysis...")
    independent_results = independent_feature_count(X)

    # Feature-based prediction
    print("\n[3/4] Feature-based compatibility prediction...")
    prediction_results = feature_based_compatibility_prediction(M, X)

    # Information content
    print("\n[4/4] Information content analysis...")
    info_results = information_content_analysis(M, all_middles)

    # Synthesis
    print(f"\n{'='*70}")
    print("MORPHOLOGICAL DERIVATION SUMMARY")
    print(f"{'='*70}")
    print(f"  Character features: {X.shape[1]} non-constant")
    print(f"  Independent features (PCA 95%): {independent_results['k_95']}")
    print(f"  Feature-based prediction AUC: {prediction_results['auc']:.4f}")
    print(f"  Eigenvalues > 1: {info_results['n_eigenvalues_gt1']}")
    print(f"  Mean row-pair MI: {info_results['mean_row_pair_mi']:.4f} bits")

    # Can character features explain compatibility?
    if prediction_results['auc'] > 0.95:
        feature_sufficiency = "SUFFICIENT"
    elif prediction_results['auc'] > 0.85:
        feature_sufficiency = "PARTIAL"
    else:
        feature_sufficiency = "INSUFFICIENT"

    print(f"\n  Character feature sufficiency: {feature_sufficiency}")

    # Does morphological derivation match spectral dimensionality?
    spectral_d = info_results['n_eigenvalues_gt1']
    morph_d = independent_results['k_95']
    ratio = spectral_d / morph_d if morph_d > 0 else float('inf')
    print(f"  Spectral D: {spectral_d}")
    print(f"  Morphological D (95%): {morph_d}")
    print(f"  Ratio: {ratio:.2f}")

    if 0.5 < ratio < 2.0:
        derivation = "CONSISTENT"
    elif ratio > 2.0:
        derivation = "SPECTRAL_EXCEEDS_MORPHOLOGICAL"
    else:
        derivation = "MORPHOLOGICAL_EXCEEDS_SPECTRAL"

    print(f"  Derivation verdict: {derivation}")

    results = {
        'test': 'T4_morphological_derivation',
        'n_middles': n,
        'n_features_raw': int(X.shape[1]),
        'independent_features': independent_results,
        'prediction': prediction_results,
        'information_content': info_results,
        'feature_sufficiency': feature_sufficiency,
        'derivation_verdict': derivation,
        'spectral_d': spectral_d,
        'morphological_d': morph_d,
    }

    with open(RESULTS_DIR / 't4_morphological_derivation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't4_morphological_derivation.json'}")


if __name__ == '__main__':
    run()
