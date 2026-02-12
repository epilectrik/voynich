#!/usr/bin/env python3
"""
T6: C3-C4 Discriminant Anatomy
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

Two large populations (~351 vs ~362 MIDDLEs) are geometrically separable
with mutual exclusion z=-3.1, yet similar on known metrics. What separates
them? Train classifiers on diverse feature sets to find the hidden axis.

Stop rule: If no feature set reaches AUC > 0.70, separation is non-local.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, mannwhitneyu, entropy
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

QO_INITIALS = set('ktp')
CHSH_INITIALS = set('eo')
KERNEL_CHARS = set('keh')
VOWEL_CHARS = set('aeiouy')


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
    s = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            s.add(m.middle)
    return sorted(s)


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :], eigenvalues, eigenvectors


def build_features(all_middles, mid_to_idx, compat_matrix, embedding):
    """Build comprehensive feature matrix for C3-C4 discrimination."""
    tx = Transcript()
    morph = Morphology()
    n = len(all_middles)

    features = {}
    feature_names = []

    # ===== INTRINSIC CHARACTER FEATURES =====
    # Character unigram frequencies (relative within MIDDLE)
    all_chars = sorted(set(c for m in all_middles for c in m))
    for ch in all_chars:
        fname = f'char_{ch}'
        feature_names.append(fname)
        features[fname] = np.array([m.count(ch) / max(len(m), 1) for m in all_middles])

    # Character bigram presence
    all_bigrams = Counter()
    for m in all_middles:
        for i in range(len(m) - 1):
            all_bigrams[m[i:i+2]] += 1
    top_bigrams = [bg for bg, _ in all_bigrams.most_common(30)]
    for bg in top_bigrams:
        fname = f'bigram_{bg}'
        feature_names.append(fname)
        features[fname] = np.array([1 if bg in m else 0 for m in all_middles])

    # Length, kernel count, vowel ratio
    feature_names.append('length')
    features['length'] = np.array([len(m) for m in all_middles], dtype=float)

    feature_names.append('kernel_count')
    features['kernel_count'] = np.array([sum(1 for c in m if c in KERNEL_CHARS)
                                          for m in all_middles], dtype=float)

    feature_names.append('vowel_ratio')
    features['vowel_ratio'] = np.array([sum(1 for c in m if c in VOWEL_CHARS) / max(len(m), 1)
                                         for m in all_middles])

    # Initial and final character (encoded as one-hot for top chars)
    for ch in 'oekhtcdsairly':
        feature_names.append(f'initial_{ch}')
        features[f'initial_{ch}'] = np.array([1 if m[0] == ch else 0 for m in all_middles], dtype=float)
        feature_names.append(f'final_{ch}')
        features[f'final_{ch}'] = np.array([1 if m[-1] == ch else 0 for m in all_middles], dtype=float)

    # ===== FREQUENCY FEATURES =====
    a_counts = Counter()
    a_folio_sets = defaultdict(set)
    a_line_sets = defaultdict(set)
    a_prefix_counts = defaultdict(lambda: Counter())
    a_suffix_counts = defaultdict(lambda: Counter())
    a_section_counts = defaultdict(lambda: Counter())

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            mid = m.middle
            a_counts[mid] += 1
            a_folio_sets[mid].add(token.folio)
            a_line_sets[mid].add((token.folio, token.line))
            if m.prefix:
                a_prefix_counts[mid][m.prefix] += 1
            if m.suffix:
                a_suffix_counts[mid][m.suffix] += 1
            a_section_counts[mid][token.section] += 1

    feature_names.append('log_freq')
    features['log_freq'] = np.array([np.log1p(a_counts.get(m, 0)) for m in all_middles])

    feature_names.append('folio_count')
    features['folio_count'] = np.array([len(a_folio_sets.get(m, set())) for m in all_middles], dtype=float)

    # PREFIX diversity and entropy
    feature_names.append('prefix_diversity')
    prefix_div = []
    prefix_ent = []
    for m in all_middles:
        pc = a_prefix_counts.get(m, Counter())
        prefix_div.append(len(pc))
        if pc:
            total = sum(pc.values())
            probs = np.array([v / total for v in pc.values()])
            prefix_ent.append(float(entropy(probs)))
        else:
            prefix_ent.append(0.0)
    features['prefix_diversity'] = np.array(prefix_div, dtype=float)
    feature_names.append('prefix_entropy')
    features['prefix_entropy'] = np.array(prefix_ent)

    # Suffix diversity
    feature_names.append('suffix_diversity')
    features['suffix_diversity'] = np.array([len(a_suffix_counts.get(m, Counter()))
                                              for m in all_middles], dtype=float)

    # ===== B-SIDE CONTEXTUAL FEATURES =====
    b_counts = Counter()
    b_section_counts = defaultdict(lambda: Counter())
    b_predecessor = defaultdict(lambda: Counter())
    b_successor = defaultdict(lambda: Counter())
    b_line_positions = defaultdict(list)

    # Build B-side context
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            b_counts[m.middle] += 1
            b_section_counts[m.middle][token.section] += 1

    # Line-level co-occurrence for successor/predecessor (from A)
    line_tokens = defaultdict(list)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            line_tokens[(token.folio, token.line)].append(m.middle)

    for key, mids in line_tokens.items():
        for i in range(len(mids) - 1):
            if mids[i] in mid_to_idx and mids[i + 1] in mid_to_idx:
                b_successor[mids[i]][mids[i + 1]] += 1
                b_predecessor[mids[i + 1]][mids[i]] += 1

    feature_names.append('b_count')
    features['b_count'] = np.array([b_counts.get(m, 0) for m in all_middles], dtype=float)

    feature_names.append('in_b')
    features['in_b'] = np.array([1 if b_counts.get(m, 0) > 0 else 0
                                  for m in all_middles], dtype=float)

    # Successor/predecessor entropy
    succ_ent = []
    pred_ent = []
    succ_div = []
    for m in all_middles:
        sc = b_successor.get(m, Counter())
        pc = b_predecessor.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([v / total for v in sc.values()])
            succ_ent.append(float(entropy(probs)))
            succ_div.append(len(sc))
        else:
            succ_ent.append(0.0)
            succ_div.append(0)
        if pc:
            total = sum(pc.values())
            probs = np.array([v / total for v in pc.values()])
            pred_ent.append(float(entropy(probs)))
        else:
            pred_ent.append(0.0)

    feature_names.append('successor_entropy')
    features['successor_entropy'] = np.array(succ_ent)
    feature_names.append('predecessor_entropy')
    features['predecessor_entropy'] = np.array(pred_ent)
    feature_names.append('successor_diversity')
    features['successor_diversity'] = np.array(succ_div, dtype=float)

    # Section concentration (KL divergence from uniform)
    sections = ['B', 'C', 'F', 'H', 'S', 'T']
    uniform = np.ones(len(sections)) / len(sections)
    sec_kl = []
    for m in all_middles:
        sc = a_section_counts.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([sc.get(s, 0) / total for s in sections])
            probs = probs + 1e-10  # avoid log(0)
            probs = probs / probs.sum()
            sec_kl.append(float(entropy(probs, uniform)))
        else:
            sec_kl.append(0.0)
    feature_names.append('section_kl')
    features['section_kl'] = np.array(sec_kl)

    # ===== COMPATIBILITY GRAPH FEATURES =====
    # Degree (number of compatible MIDDLEs)
    degrees = compat_matrix.sum(axis=1)
    feature_names.append('compat_degree')
    features['compat_degree'] = degrees.astype(float)

    # Mean neighbor depth
    neighbor_depths = []
    norms = np.linalg.norm(embedding, axis=1)
    for i in range(n):
        neighbors = np.where(compat_matrix[i] > 0)[0]
        if len(neighbors) > 0:
            neighbor_depths.append(float(np.mean(norms[neighbors])))
        else:
            neighbor_depths.append(0.0)
    feature_names.append('mean_neighbor_depth')
    features['mean_neighbor_depth'] = np.array(neighbor_depths)

    # Compound status
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')
    feature_names.append('is_compound')
    features['is_compound'] = np.array([1 if mid_analyzer.is_compound(m) else 0
                                         for m in all_middles], dtype=float)

    # Residual norm (depth)
    feature_names.append('residual_norm')
    features['residual_norm'] = norms

    return features, feature_names


def main():
    print("=" * 60)
    print("T6: C3-C4 Discriminant Anatomy")
    print("=" * 60)

    # Load
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    embedding, eigenvalues, eigenvectors = build_residual_embedding(compat_matrix)

    # Reproduce GMM k=5 clustering
    print("\n[2] Reproducing GMM k=5 clustering...")
    gmm = GaussianMixture(n_components=5, random_state=42, n_init=3,
                           covariance_type='diag', max_iter=300)
    labels = gmm.fit_predict(embedding)

    c3_mask = labels == 3
    c4_mask = labels == 4
    c3c4_mask = c3_mask | c4_mask
    n_c3 = c3_mask.sum()
    n_c4 = c4_mask.sum()
    print(f"  C3: {n_c3}, C4: {n_c4}, total C3+C4: {c3c4_mask.sum()}")

    # Build features
    print("\n[3] Building feature matrix...")
    features, feature_names = build_features(all_middles, mid_to_idx, compat_matrix, embedding)

    # Restrict to C3 and C4
    X_full = np.column_stack([features[f][c3c4_mask] for f in feature_names])
    y = np.array([3 if labels[i] == 3 else 4 for i in range(len(all_middles)) if c3c4_mask[i]])
    print(f"  Feature matrix: {X_full.shape} ({len(feature_names)} features)")

    # Feature group definitions
    feature_groups = {
        'character_unigrams': [f for f in feature_names if f.startswith('char_')],
        'character_bigrams': [f for f in feature_names if f.startswith('bigram_')],
        'initial_final': [f for f in feature_names if f.startswith('initial_') or f.startswith('final_')],
        'morphological': ['length', 'kernel_count', 'vowel_ratio', 'is_compound'],
        'frequency': ['log_freq', 'folio_count', 'prefix_diversity', 'prefix_entropy',
                       'suffix_diversity'],
        'b_side_context': ['b_count', 'in_b', 'successor_entropy', 'predecessor_entropy',
                            'successor_diversity', 'section_kl'],
        'graph_topology': ['compat_degree', 'mean_neighbor_depth', 'residual_norm'],
    }

    # Test each feature group
    print("\n[4] Feature group discrimination (5-fold CV, Logistic Regression)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    chance = max(n_c3, n_c4) / (n_c3 + n_c4)
    print(f"  Chance level: {chance:.3f}")

    group_results = {}
    for group_name, group_features in feature_groups.items():
        feat_indices = [feature_names.index(f) for f in group_features if f in feature_names]
        if not feat_indices:
            continue
        X_group = X_full[:, feat_indices]

        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('lr', LogisticRegression(max_iter=1000, random_state=42))
        ])
        scores = cross_val_score(pipe, X_group, y, cv=cv, scoring='roc_auc')
        mean_auc = float(np.mean(scores))
        std_auc = float(np.std(scores))

        group_results[group_name] = {
            'auc': mean_auc,
            'std': std_auc,
            'n_features': len(feat_indices),
        }
        marker = " ***" if mean_auc >= 0.70 else ""
        print(f"  {group_name:>25s}: AUC={mean_auc:.3f}±{std_auc:.3f} "
              f"({len(feat_indices)} features){marker}")

    # Full model
    print("\n[5] Full model (all features)...")
    pipe_full = Pipeline([
        ('scaler', StandardScaler()),
        ('lr', LogisticRegression(max_iter=1000, random_state=42))
    ])
    scores_full = cross_val_score(pipe_full, X_full, y, cv=cv, scoring='roc_auc')
    full_auc = float(np.mean(scores_full))
    full_std = float(np.std(scores_full))
    print(f"  Full model AUC: {full_auc:.3f}±{full_std:.3f}")

    # Feature importance (fit on full data)
    print("\n[6] Feature importance (logistic regression coefficients)...")
    pipe_full.fit(X_full, y)
    coefs = pipe_full.named_steps['lr'].coef_[0]
    importance = list(zip(feature_names, coefs))
    importance.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"  Top 20 most discriminating features:")
    top_features = []
    for fname, coef in importance[:20]:
        direction = "→C4" if coef > 0 else "→C3"
        print(f"    {fname:>30s}: coef={coef:+.4f} ({direction})")
        top_features.append({'feature': fname, 'coef': float(coef)})

    # Univariate tests for top features
    print("\n[7] Univariate Mann-Whitney tests on top features...")
    univariate_results = []
    for fname, coef in importance[:15]:
        fidx = feature_names.index(fname)
        vals_c3 = X_full[y == 3, fidx]
        vals_c4 = X_full[y == 4, fidx]
        stat, p = mannwhitneyu(vals_c3, vals_c4, alternative='two-sided')
        mean_c3 = float(np.mean(vals_c3))
        mean_c4 = float(np.mean(vals_c4))
        univariate_results.append({
            'feature': fname,
            'mean_c3': mean_c3,
            'mean_c4': mean_c4,
            'diff': mean_c4 - mean_c3,
            'p': float(p),
        })
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
        print(f"    {fname:>30s}: C3={mean_c3:.4f} C4={mean_c4:.4f} diff={mean_c4-mean_c3:+.4f} "
              f"p={p:.2e} {sig}")

    # Example MIDDLEs from each side
    print("\n[8] Example MIDDLEs from C3 and C4...")
    c3_mids = [all_middles[i] for i in range(len(all_middles)) if labels[i] == 3]
    c4_mids = [all_middles[i] for i in range(len(all_middles)) if labels[i] == 4]

    # Sort by prediction confidence
    pipe_full.fit(X_full, y)
    probs = pipe_full.predict_proba(X_full)
    c3_indices_local = [i for i, yi in enumerate(y) if yi == 3]
    c4_indices_local = [i for i, yi in enumerate(y) if yi == 4]

    c3_conf = [(c3_indices_local[j], probs[c3_indices_local[j], 0])
               for j in range(len(c3_indices_local))]
    c3_conf.sort(key=lambda x: x[1], reverse=True)
    c4_conf = [(c4_indices_local[j], probs[c4_indices_local[j], 1])
               for j in range(len(c4_indices_local))]
    c4_conf.sort(key=lambda x: x[1], reverse=True)

    c3c4_global_indices = [i for i in range(len(all_middles)) if c3c4_mask[i]]

    print(f"  Most confident C3 MIDDLEs:")
    for idx, conf in c3_conf[:10]:
        gidx = c3c4_global_indices[idx]
        m = all_middles[gidx]
        print(f"    {m:>15s} (conf={conf:.3f})")

    print(f"  Most confident C4 MIDDLEs:")
    for idx, conf in c4_conf[:10]:
        gidx = c3c4_global_indices[idx]
        m = all_middles[gidx]
        print(f"    {m:>15s} (conf={conf:.3f})")

    # Verdict
    print("\n" + "=" * 60)
    best_group = max(group_results, key=lambda k: group_results[k]['auc'])
    best_group_auc = group_results[best_group]['auc']

    if full_auc >= 0.70:
        if best_group_auc >= 0.70:
            verdict = "INTERPRETABLE_AXIS"
            explanation = (
                f"Full AUC={full_auc:.3f}, best group '{best_group}' AUC={best_group_auc:.3f}. "
                f"C3-C4 separation has an interpretable feature-space axis."
            )
        else:
            verdict = "COMPOSITE_AXIS"
            explanation = (
                f"Full AUC={full_auc:.3f} but no single group exceeds 0.70 "
                f"(best: {best_group} at {best_group_auc:.3f}). "
                f"Separation requires combining multiple feature families."
            )
    else:
        verdict = "NON_LOCAL"
        explanation = (
            f"Full AUC={full_auc:.3f} < 0.70. "
            f"C3-C4 separation is non-local — encoded in high-order manifold curvature, "
            f"not reducible to interpretable feature combinations."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T6_c3c4_discriminant_anatomy',
        'n_c3': int(n_c3),
        'n_c4': int(n_c4),
        'chance_level': float(chance),
        'group_results': group_results,
        'full_model': {'auc': full_auc, 'std': full_std},
        'top_features': top_features,
        'univariate_tests': univariate_results,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't6_c3c4_discriminant_anatomy.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't6_c3c4_discriminant_anatomy.json'}")


if __name__ == '__main__':
    main()
