#!/usr/bin/env python3
"""
T7: Contextual Eigenvector Annotation
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

T1 showed 27/29 eigenvectors are OPAQUE to intrinsic properties.
Now correlate eigenvector loadings with CONTEXTUAL features:
successor/predecessor profiles, prefix entropy, section KL,
constraint energy, hazard participation, depth gradients.

Goal: Are the hidden axes encoding contextual routing patterns
rather than material properties?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, entropy

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99
N_EIGVECS = 29


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


def main():
    print("=" * 60)
    print("T7: Contextual Eigenvector Annotation")
    print("=" * 60)

    # Load
    print("\n[1] Loading data...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    n = len(all_middles)

    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Build residual embedding
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    embedding = res_evecs * scaling[np.newaxis, :]
    norms = np.linalg.norm(embedding, axis=1)

    print(f"  {n} MIDDLEs, {N_EIGVECS} eigenvectors to annotate")

    # Build contextual features
    print("\n[2] Building contextual feature vectors...")
    tx = Transcript()
    morph = Morphology()

    # === A-side contextual features ===
    a_counts = Counter()
    a_folio_sets = defaultdict(set)
    a_prefix_counts = defaultdict(lambda: Counter())
    a_suffix_counts = defaultdict(lambda: Counter())
    a_section_counts = defaultdict(lambda: Counter())
    a_line_tokens = defaultdict(list)

    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            mid = m.middle
            a_counts[mid] += 1
            a_folio_sets[mid].add(token.folio)
            if m.prefix:
                a_prefix_counts[mid][m.prefix] += 1
            if m.suffix:
                a_suffix_counts[mid][m.suffix] += 1
            a_section_counts[mid][token.section] += 1
            a_line_tokens[(token.folio, token.line)].append(mid)

    # Successor/predecessor distributions from A
    successor_counts = defaultdict(lambda: Counter())
    predecessor_counts = defaultdict(lambda: Counter())
    for key, mids in a_line_tokens.items():
        for i in range(len(mids) - 1):
            successor_counts[mids[i]][mids[i + 1]] += 1
            predecessor_counts[mids[i + 1]][mids[i]] += 1

    # === B-side contextual features ===
    b_counts = Counter()
    b_section_counts = defaultdict(lambda: Counter())
    b_prefix_counts = defaultdict(lambda: Counter())
    b_line_tokens = defaultdict(list)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            mid = m.middle
            b_counts[mid] += 1
            b_section_counts[mid][token.section] += 1
            if m.prefix:
                b_prefix_counts[mid][m.prefix] += 1
            b_line_tokens[(token.folio, token.line)].append(mid)

    # B-side successor/predecessor
    b_successor_counts = defaultdict(lambda: Counter())
    b_predecessor_counts = defaultdict(lambda: Counter())
    for key, mids in b_line_tokens.items():
        for i in range(len(mids) - 1):
            b_successor_counts[mids[i]][mids[i + 1]] += 1
            b_predecessor_counts[mids[i + 1]][mids[i]] += 1

    # === Compute contextual property vectors ===
    ctx_features = {}
    ctx_names = []
    sections_list = ['B', 'C', 'F', 'H', 'S', 'T']
    uniform_sec = np.ones(len(sections_list)) / len(sections_list)

    # 1. Successor entropy (A)
    ctx_names.append('a_successor_entropy')
    vals = []
    for m in all_middles:
        sc = successor_counts.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([v / total for v in sc.values()])
            vals.append(float(entropy(probs)))
        else:
            vals.append(0.0)
    ctx_features['a_successor_entropy'] = np.array(vals)

    # 2. Predecessor entropy (A)
    ctx_names.append('a_predecessor_entropy')
    vals = []
    for m in all_middles:
        pc = predecessor_counts.get(m, Counter())
        if pc:
            total = sum(pc.values())
            probs = np.array([v / total for v in pc.values()])
            vals.append(float(entropy(probs)))
        else:
            vals.append(0.0)
    ctx_features['a_predecessor_entropy'] = np.array(vals)

    # 3. Successor diversity (number of unique successors)
    ctx_names.append('a_successor_diversity')
    ctx_features['a_successor_diversity'] = np.array([
        len(successor_counts.get(m, Counter())) for m in all_middles
    ], dtype=float)

    # 4. Predecessor diversity
    ctx_names.append('a_predecessor_diversity')
    ctx_features['a_predecessor_diversity'] = np.array([
        len(predecessor_counts.get(m, Counter())) for m in all_middles
    ], dtype=float)

    # 5. PREFIX entropy (A)
    ctx_names.append('a_prefix_entropy')
    vals = []
    for m in all_middles:
        pc = a_prefix_counts.get(m, Counter())
        if pc:
            total = sum(pc.values())
            probs = np.array([v / total for v in pc.values()])
            vals.append(float(entropy(probs)))
        else:
            vals.append(0.0)
    ctx_features['a_prefix_entropy'] = np.array(vals)

    # 6. PREFIX diversity
    ctx_names.append('a_prefix_diversity')
    ctx_features['a_prefix_diversity'] = np.array([
        len(a_prefix_counts.get(m, Counter())) for m in all_middles
    ], dtype=float)

    # 7. SUFFIX diversity
    ctx_names.append('a_suffix_diversity')
    ctx_features['a_suffix_diversity'] = np.array([
        len(a_suffix_counts.get(m, Counter())) for m in all_middles
    ], dtype=float)

    # 8. Section KL divergence from uniform (A)
    ctx_names.append('a_section_kl')
    vals = []
    for m in all_middles:
        sc = a_section_counts.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([sc.get(s, 0) / total for s in sections_list])
            probs = probs + 1e-10
            probs = probs / probs.sum()
            vals.append(float(entropy(probs, uniform_sec)))
        else:
            vals.append(0.0)
    ctx_features['a_section_kl'] = np.array(vals)

    # 9. Compatibility degree (from matrix)
    ctx_names.append('compat_degree')
    ctx_features['compat_degree'] = compat_matrix.sum(axis=1).astype(float)

    # 10. Residual norm (depth)
    ctx_names.append('residual_norm')
    ctx_features['residual_norm'] = norms

    # 11. Hub loading
    ctx_names.append('hub_loading')
    ctx_features['hub_loading'] = eigenvectors[:, 0].astype(float)

    # 12. Log frequency
    ctx_names.append('log_freq')
    ctx_features['log_freq'] = np.array([np.log1p(a_counts.get(m, 0)) for m in all_middles])

    # 13. B-side presence rate
    ctx_names.append('b_presence')
    ctx_features['b_presence'] = np.array([1 if b_counts.get(m, 0) > 0 else 0
                                            for m in all_middles], dtype=float)

    # 14. B successor entropy
    ctx_names.append('b_successor_entropy')
    vals = []
    for m in all_middles:
        sc = b_successor_counts.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([v / total for v in sc.values()])
            vals.append(float(entropy(probs)))
        else:
            vals.append(0.0)
    ctx_features['b_successor_entropy'] = np.array(vals)

    # 15. B section KL
    ctx_names.append('b_section_kl')
    b_sections = ['B', 'C', 'H', 'S', 'T']
    uniform_b = np.ones(len(b_sections)) / len(b_sections)
    vals = []
    for m in all_middles:
        sc = b_section_counts.get(m, Counter())
        if sc:
            total = sum(sc.values())
            probs = np.array([sc.get(s, 0) / total for s in b_sections])
            probs = probs + 1e-10
            probs = probs / probs.sum()
            vals.append(float(entropy(probs, uniform_b)))
        else:
            vals.append(0.0)
    ctx_features['b_section_kl'] = np.array(vals)

    # 16. Mean neighbor residual norm
    ctx_names.append('mean_neighbor_depth')
    vals = []
    for i in range(n):
        neighbors = np.where(compat_matrix[i] > 0)[0]
        if len(neighbors) > 0:
            vals.append(float(np.mean(norms[neighbors])))
        else:
            vals.append(0.0)
    ctx_features['mean_neighbor_depth'] = np.array(vals)

    # 17. Folio count
    ctx_names.append('folio_count')
    ctx_features['folio_count'] = np.array([
        len(a_folio_sets.get(m, set())) for m in all_middles
    ], dtype=float)

    print(f"  Built {len(ctx_names)} contextual features")

    # Correlate eigenvectors with contextual features
    print(f"\n[3] Correlating {N_EIGVECS} eigenvectors with {len(ctx_names)} contextual features...")

    correlation_atlas = {}  # eigvec -> {feature: rho}
    best_per_eigvec = {}

    for ev_idx in range(N_EIGVECS):
        ev_loadings = eigenvectors[:, ev_idx + 1]  # skip hub
        ev_key = f"eigvec_{ev_idx + 2}"

        correlations = {}
        for fname in ctx_names:
            rho, p = spearmanr(ev_loadings, ctx_features[fname])
            correlations[fname] = {'rho': float(rho), 'p': float(p)}

        correlation_atlas[ev_key] = correlations

        # Best correlation
        best_feat = max(ctx_names, key=lambda f: abs(correlations[f]['rho']))
        best_rho = correlations[best_feat]['rho']
        best_per_eigvec[ev_key] = {
            'best_feature': best_feat,
            'rho': float(best_rho),
            'p': float(correlations[best_feat]['p']),
            'eigenvalue': float(eigenvalues[ev_idx + 1]),
        }

    # Print atlas
    print(f"\n{'Eigvec':>10s} | {'λ':>6s} | {'Best Contextual Feature':>25s} | {'ρ':>7s} | {'p':>10s}")
    print("-" * 75)
    for ev_idx in range(N_EIGVECS):
        ev_key = f"eigvec_{ev_idx + 2}"
        info = best_per_eigvec[ev_key]
        marker = " ***" if abs(info['rho']) >= 0.20 else " **" if abs(info['rho']) >= 0.15 else ""
        print(f"  {ev_key:>8s} | {info['eigenvalue']:6.2f} | {info['best_feature']:>25s} | "
              f"{info['rho']:+.4f} | {info['p']:.2e}{marker}")

    # Summary: how many are now explained?
    print(f"\n[4] Summary: contextual vs intrinsic annotation...")
    n_strong_ctx = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.20)
    n_moderate_ctx = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.15)
    n_weak_ctx = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.10)

    print(f"  Contextual |ρ|≥0.20: {n_strong_ctx}/{N_EIGVECS}")
    print(f"  Contextual |ρ|≥0.15: {n_moderate_ctx}/{N_EIGVECS}")
    print(f"  Contextual |ρ|≥0.10: {n_weak_ctx}/{N_EIGVECS}")

    # Compare to T1 (intrinsic): 2 at ≥0.15
    print(f"\n  Comparison to T1 (intrinsic properties):")
    print(f"    T1 intrinsic |ρ|≥0.15: 2/{N_EIGVECS}")
    print(f"    T7 contextual |ρ|≥0.15: {n_moderate_ctx}/{N_EIGVECS}")
    print(f"    Improvement: {n_moderate_ctx - 2} additional eigenvectors explained")

    # Property dominance
    print(f"\n[5] Contextual property dominance...")
    prop_dominance = Counter()
    for ev_key, info in best_per_eigvec.items():
        if abs(info['rho']) >= 0.15:
            prop_dominance[info['best_feature']] += 1

    for prop, count in prop_dominance.most_common():
        print(f"    {prop:>25s}: dominates {count} eigenvectors")

    # Top-3 per eigenvector
    print(f"\n[6] Top-3 contextual correlations per eigenvector (first 15)...")
    multi_view = {}
    for ev_idx in range(min(15, N_EIGVECS)):
        ev_key = f"eigvec_{ev_idx + 2}"
        corrs = correlation_atlas[ev_key]
        ranked = sorted(ctx_names, key=lambda f: abs(corrs[f]['rho']), reverse=True)[:3]
        top3 = [(f, corrs[f]['rho']) for f in ranked]
        multi_view[ev_key] = [{'feature': f, 'rho': float(r)} for f, r in top3]
        top3_str = ', '.join(f"{f}={r:+.3f}" for f, r in top3)
        print(f"  {ev_key:>10s}: {top3_str}")

    # Verdict
    print("\n" + "=" * 60)

    if n_moderate_ctx >= 15:
        verdict = "CONTEXTUAL_ROUTING"
        explanation = (
            f"{n_moderate_ctx}/{N_EIGVECS} eigenvectors correlate with contextual features (|ρ|≥0.15). "
            f"The hidden axes primarily encode contextual routing patterns, not material properties."
        )
    elif n_moderate_ctx >= 8:
        verdict = "MIXED_ENCODING"
        explanation = (
            f"{n_moderate_ctx}/{N_EIGVECS} eigenvectors have contextual correlations (|ρ|≥0.15). "
            f"Some axes encode routing, others remain opaque — manifold has mixed structure."
        )
    elif n_moderate_ctx >= 4:
        verdict = "PARTIAL_CONTEXTUAL"
        explanation = (
            f"{n_moderate_ctx}/{N_EIGVECS} eigenvectors show contextual correlations. "
            f"Small improvement over intrinsic (T1: 2). Most axes remain structurally opaque."
        )
    else:
        verdict = "INTRINSIC_OPACITY"
        explanation = (
            f"Only {n_moderate_ctx}/{N_EIGVECS} contextual correlations at |ρ|≥0.15. "
            f"The eigenspace encodes neither intrinsic properties nor contextual routing — "
            f"it reflects irreducible manifold curvature."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T7_contextual_eigenvector_annotation',
        'n_middles': n,
        'n_eigvecs': N_EIGVECS,
        'n_contextual_features': len(ctx_names),
        'best_per_eigvec': best_per_eigvec,
        'multi_view_top15': multi_view,
        'property_dominance': dict(prop_dominance.most_common()),
        'strength_counts': {
            'strong_020': n_strong_ctx,
            'moderate_015': n_moderate_ctx,
            'weak_010': n_weak_ctx,
        },
        'comparison_to_t1': {
            't1_moderate': 2,
            't7_moderate': n_moderate_ctx,
            'improvement': n_moderate_ctx - 2,
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't7_contextual_eigenvector_annotation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't7_contextual_eigenvector_annotation.json'}")


if __name__ == '__main__':
    main()
