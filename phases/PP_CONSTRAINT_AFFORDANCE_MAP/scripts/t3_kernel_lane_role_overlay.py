#!/usr/bin/env python3
"""
T3: Kernel-Lane-Role Manifold Overlay
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

Map known categorical structure (kernel content, lane assignment,
compound status) onto the geometric manifold and test separability.
Can the manifold's geometry predict these categories?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter
from scipy.stats import spearmanr
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

QO_INITIALS = set('ktp')
CHSH_INITIALS = set('eo')


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    return sorted(all_middles_set)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :], eigenvalues


def main():
    print("=" * 60)
    print("T3: Kernel-Lane-Role Manifold Overlay")
    print("=" * 60)

    # Load
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    embedding, eigenvalues = build_residual_embedding(compat_matrix)
    print(f"  {len(all_middles)} MIDDLEs, embedding {embedding.shape}")

    # Build categorical overlays
    print("\n[2] Building categorical overlays...")

    # Lane overlay (C649)
    lane_labels = []
    for m in all_middles:
        if m[0] in QO_INITIALS:
            lane_labels.append('QO')
        elif m[0] in CHSH_INITIALS:
            lane_labels.append('CHSH')
        else:
            lane_labels.append('OTHER')
    lane_labels = np.array(lane_labels)
    print(f"  Lane: {Counter(lane_labels)}")

    # Kernel overlay
    kernel_labels = []
    for m in all_middles:
        has_k = 'k' in m
        has_e = 'e' in m
        has_h = 'h' in m
        n_kernel = sum([has_k, has_e, has_h])
        if n_kernel == 0:
            kernel_labels.append('NONE')
        elif n_kernel >= 2:
            kernel_labels.append('MULTI')
        elif has_k:
            kernel_labels.append('K')
        elif has_e:
            kernel_labels.append('E')
        else:
            kernel_labels.append('H')
    kernel_labels = np.array(kernel_labels)
    print(f"  Kernel: {Counter(kernel_labels)}")

    # Compound overlay
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')
    compound_labels = np.array([
        'COMPOUND' if mid_analyzer.is_compound(m) else 'BASE'
        for m in all_middles
    ])
    print(f"  Compound: {Counter(compound_labels)}")

    # Frequency tier overlay
    tx = Transcript()
    morph = Morphology()
    a_counts = Counter()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m_result = morph.extract(word)
        if m_result.middle and m_result.middle in mid_to_idx:
            a_counts[m_result.middle] += 1

    freq_labels = []
    for m in all_middles:
        c = a_counts.get(m, 0)
        if c >= 50:
            freq_labels.append('HIGH')
        elif c >= 10:
            freq_labels.append('MED')
        elif c >= 2:
            freq_labels.append('LOW')
        else:
            freq_labels.append('HAPAX')
    freq_labels = np.array(freq_labels)
    print(f"  Frequency: {Counter(freq_labels)}")

    # SVM separability testing
    print("\n[3] SVM separability testing (5-fold CV)...")

    overlays = {
        'lane': lane_labels,
        'kernel': kernel_labels,
        'compound': compound_labels,
        'frequency': freq_labels,
    }

    svm_results = {}
    for name, labels in overlays.items():
        # Only include classes with ≥10 members
        valid_classes = {c for c, n in Counter(labels).items() if n >= 10}
        mask = np.array([l in valid_classes for l in labels])
        X = embedding[mask]
        y = labels[mask]

        if len(set(y)) < 2:
            print(f"  {name}: Skipped (< 2 valid classes)")
            continue

        # Chance level
        chance = max(Counter(y).values()) / len(y)

        # Linear SVM with CV
        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('svm', LinearSVC(max_iter=5000, random_state=42, dual=True))
        ])
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(pipe, X, y, cv=cv, scoring='accuracy')

        mean_acc = float(np.mean(scores))
        std_acc = float(np.std(scores))
        lift = mean_acc / chance if chance > 0 else 0

        svm_results[name] = {
            'accuracy': mean_acc,
            'std': std_acc,
            'chance': float(chance),
            'lift': float(lift),
            'n_samples': int(mask.sum()),
            'n_classes': len(valid_classes),
        }

        print(f"  {name:>12s}: acc={mean_acc:.3f}±{std_acc:.3f} "
              f"(chance={chance:.3f}, lift={lift:.2f}x)")

    # Fisher criterion for each overlay
    print("\n[4] Fisher criterion (between/within scatter ratio)...")
    fisher_results = {}
    for name, labels in overlays.items():
        unique = sorted(set(labels))
        if len(unique) < 2:
            continue

        # Compute class centroids and scatters
        overall_mean = np.mean(embedding, axis=0)
        between_scatter = 0
        within_scatter = 0

        for cls in unique:
            mask = labels == cls
            n_cls = mask.sum()
            if n_cls < 2:
                continue
            cls_vecs = embedding[mask]
            cls_mean = np.mean(cls_vecs, axis=0)

            # Between-scatter: n * ||centroid - overall_mean||^2
            between_scatter += n_cls * np.sum((cls_mean - overall_mean) ** 2)

            # Within-scatter: sum of ||vec - centroid||^2
            within_scatter += np.sum((cls_vecs - cls_mean) ** 2)

        fisher = between_scatter / within_scatter if within_scatter > 0 else 0
        fisher_results[name] = float(fisher)
        print(f"  {name:>12s}: Fisher={fisher:.4f}")

    # Orthogonality: mutual information between overlay predictions
    print("\n[5] Overlay independence (Cramer's V between overlays)...")
    from scipy.stats import chi2_contingency
    independence = {}
    overlay_names = list(overlays.keys())
    for i, name_i in enumerate(overlay_names):
        for j, name_j in enumerate(overlay_names):
            if j <= i:
                continue
            # Contingency table
            labels_i = overlays[name_i]
            labels_j = overlays[name_j]
            ct = {}
            for li, lj in zip(labels_i, labels_j):
                ct.setdefault(li, Counter())[lj] += 1

            # Build matrix
            rows = sorted(ct.keys())
            cols = sorted(set(labels_j))
            table = np.array([[ct.get(r, {}).get(c, 0) for c in cols] for r in rows])

            if table.shape[0] < 2 or table.shape[1] < 2:
                continue

            chi2, p, dof, expected = chi2_contingency(table)
            n = table.sum()
            k_min = min(table.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * k_min)) if k_min > 0 and n > 0 else 0

            pair_key = f"{name_i}-{name_j}"
            independence[pair_key] = {
                'cramers_v': float(cramers_v),
                'chi2': float(chi2),
                'p': float(p),
            }
            print(f"  {pair_key:>25s}: V={cramers_v:.3f} (p={p:.2e})")

    # PCA projection for visualization summary
    print("\n[6] PCA projection (2D summary)...")
    pca = PCA(n_components=3)
    pca_coords = pca.fit_transform(embedding)
    var_explained = pca.explained_variance_ratio_
    print(f"  Variance explained by PC1-3: {var_explained[0]:.3f}, "
          f"{var_explained[1]:.3f}, {var_explained[2]:.3f} "
          f"(total={sum(var_explained[:3]):.3f})")

    # Per-overlay centroid spread in PCA space
    print("\n  Overlay centroid spread in PC1-2:")
    for name, labels in overlays.items():
        unique = sorted(set(labels))
        centroids = {}
        for cls in unique:
            mask = labels == cls
            if mask.sum() >= 5:
                centroids[cls] = pca_coords[mask, :2].mean(axis=0)
        if len(centroids) >= 2:
            pairs = [(a, b) for a in centroids for b in centroids if a < b]
            dists = [np.linalg.norm(centroids[a] - centroids[b]) for a, b in pairs]
            print(f"    {name:>12s}: mean centroid dist={np.mean(dists):.3f}, "
                  f"max={max(dists):.3f}")

    # Verdict
    print("\n" + "=" * 60)
    n_separable = sum(1 for r in svm_results.values() if r['accuracy'] >= 0.65)
    n_independent_pairs = sum(1 for v in independence.values() if v['cramers_v'] < 0.30)
    total_pairs = len(independence)

    if n_separable >= 2 and n_independent_pairs >= total_pairs * 0.3:
        verdict = "SEPARABLE_AXES"
        explanation = (
            f"{n_separable} overlays predictable at ≥65% accuracy, "
            f"{n_independent_pairs}/{total_pairs} overlay pairs have V<0.30 (partially independent). "
            f"The manifold encodes multiple separable constraint dimensions."
        )
    elif n_separable >= 1:
        verdict = "SINGLE_AXIS"
        explanation = (
            f"Only {n_separable} overlay(s) predictable at ≥65%. "
            f"The manifold is dominated by a single categorical dimension."
        )
    else:
        verdict = "NO_SEPARATION"
        explanation = (
            f"No overlays predictable at ≥65% accuracy. "
            f"Categorical structure does not map cleanly to the manifold geometry."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T3_kernel_lane_role_overlay',
        'n_middles': len(all_middles),
        'overlay_distributions': {name: dict(Counter(labels))
                                   for name, labels in overlays.items()},
        'svm_results': svm_results,
        'fisher_criteria': fisher_results,
        'independence': independence,
        'pca_variance': [float(v) for v in var_explained[:3]],
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't3_kernel_lane_role_overlay.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't3_kernel_lane_role_overlay.json'}")


if __name__ == '__main__':
    main()
