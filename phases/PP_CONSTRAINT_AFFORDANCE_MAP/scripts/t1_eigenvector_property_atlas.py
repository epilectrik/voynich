#!/usr/bin/env python3
"""
T1: Eigenvector Property Atlas
PP_CONSTRAINT_AFFORDANCE_MAP phase (Tier 4)

What do the top ~30 residual eigenvectors actually encode?
Correlate eigenvector loadings with known MIDDLE properties to build
an interpretive dictionary of the discrimination space axes.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import spearmanr, f_oneway

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99
N_EIGVECS = 29  # Eigenvectors 2-30 (indices 1-29 after sorting)

# Lane assignment from C649
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


def build_property_table(all_middles, mid_to_idx, hub_vec, residual_embedding):
    """Build comprehensive property table for all 972 MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    # Initialize properties
    props = {m: {} for m in all_middles}

    # --- Morphological properties ---
    for m in all_middles:
        props[m]['length'] = len(m)
        props[m]['initial_char'] = m[0] if m else '?'
        props[m]['contains_k'] = 1 if 'k' in m else 0
        props[m]['contains_e'] = 1 if 'e' in m else 0
        props[m]['contains_h'] = 1 if 'h' in m else 0
        # Kernel count
        props[m]['kernel_count'] = sum(1 for c in m if c in 'keh')

        # Lane assignment (C649)
        if m[0] in QO_INITIALS:
            props[m]['lane'] = 'QO'
            props[m]['lane_code'] = 1
        elif m[0] in CHSH_INITIALS:
            props[m]['lane'] = 'CHSH'
            props[m]['lane_code'] = -1
        else:
            props[m]['lane'] = 'OTHER'
            props[m]['lane_code'] = 0

    # --- Frequency properties from Currier A ---
    a_counts = Counter()
    a_folio_sets = defaultdict(set)
    a_prefix_sets = defaultdict(set)
    a_line_sets = defaultdict(set)
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m_result = morph.extract(word)
        if m_result.middle and m_result.middle in mid_to_idx:
            mid = m_result.middle
            a_counts[mid] += 1
            a_folio_sets[mid].add(token.folio)
            a_line_sets[mid].add((token.folio, token.line))
            if m_result.prefix:
                a_prefix_sets[mid].add(m_result.prefix)

    for m in all_middles:
        props[m]['a_token_count'] = a_counts.get(m, 0)
        props[m]['a_folio_count'] = len(a_folio_sets.get(m, set()))
        props[m]['a_line_count'] = len(a_line_sets.get(m, set()))
        props[m]['a_prefix_diversity'] = len(a_prefix_sets.get(m, set()))
        props[m]['log_freq'] = float(np.log1p(a_counts.get(m, 0)))

    # --- B-side properties ---
    b_counts = Counter()
    b_section_counts = defaultdict(lambda: Counter())
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m_result = morph.extract(word)
        if m_result.middle and m_result.middle in mid_to_idx:
            mid = m_result.middle
            b_counts[mid] += 1
            b_section_counts[mid][token.section] += 1

    for m in all_middles:
        props[m]['b_token_count'] = b_counts.get(m, 0)
        props[m]['in_b'] = 1 if b_counts.get(m, 0) > 0 else 0
        # Dominant B section
        if m in b_section_counts and b_section_counts[m]:
            dom_sec = b_section_counts[m].most_common(1)[0][0]
            props[m]['b_dominant_section'] = dom_sec
        else:
            props[m]['b_dominant_section'] = 'NONE'

    # --- Compound status ---
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('A')
    for m in all_middles:
        props[m]['is_compound'] = 1 if mid_analyzer.is_compound(m) else 0

    # --- Geometric properties ---
    for i, m in enumerate(all_middles):
        props[m]['hub_loading'] = float(hub_vec[i])
        props[m]['residual_norm'] = float(np.linalg.norm(residual_embedding[i]))

    return props


def main():
    print("=" * 60)
    print("T1: Eigenvector Property Atlas")
    print("=" * 60)

    # Load data
    print("\n[1] Loading discrimination space...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    assert len(all_middles) == compat_matrix.shape[0], f"Mismatch: {len(all_middles)} vs {compat_matrix.shape[0]}"
    print(f"  {len(all_middles)} MIDDLEs, matrix {compat_matrix.shape}")

    # Eigendecomposition
    print("\n[2] Computing eigendecomposition...")
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    hub_vec = eigenvectors[:, 0]
    hub_val = eigenvalues[0]
    print(f"  Hub eigenvalue: {hub_val:.2f}")
    print(f"  Next 5: {eigenvalues[1:6].round(2)}")

    # Residual embedding
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    residual_embedding = res_evecs * scaling[np.newaxis, :]

    # Build property table
    print("\n[3] Building MIDDLE property table...")
    props = build_property_table(all_middles, mid_to_idx, hub_vec, residual_embedding)

    # Numeric properties to correlate
    numeric_props = [
        'length', 'contains_k', 'contains_e', 'contains_h', 'kernel_count',
        'lane_code', 'a_token_count', 'a_folio_count', 'a_line_count',
        'a_prefix_diversity', 'log_freq', 'b_token_count', 'in_b',
        'is_compound', 'hub_loading', 'residual_norm'
    ]

    # Categorical properties for ANOVA
    cat_props = ['lane', 'b_dominant_section', 'initial_char']

    # Build numeric arrays
    prop_arrays = {}
    for pname in numeric_props:
        prop_arrays[pname] = np.array([props[m][pname] for m in all_middles])

    cat_arrays = {}
    for pname in cat_props:
        cat_arrays[pname] = [props[m][pname] for m in all_middles]

    # Correlate eigenvectors with properties
    print("\n[4] Correlating eigenvectors 2-30 with properties...")
    n_eigvecs = min(N_EIGVECS, len(res_evals))

    correlation_matrix = {}  # eigvec_idx -> {prop: (rho, p)}
    best_per_eigvec = {}

    for ev_idx in range(n_eigvecs):
        ev_loadings = eigenvectors[:, ev_idx + 1]  # +1 because 0 is hub
        ev_key = f"eigvec_{ev_idx + 2}"  # Named eigvec_2 through eigvec_30

        correlations = {}
        for pname in numeric_props:
            rho, p = spearmanr(ev_loadings, prop_arrays[pname])
            correlations[pname] = {'rho': float(rho), 'p': float(p)}

        # ANOVA for categorical
        for pname in cat_props:
            categories = cat_arrays[pname]
            unique_cats = sorted(set(categories))
            if len(unique_cats) < 2:
                continue
            groups = []
            for cat in unique_cats:
                group = [ev_loadings[i] for i, c in enumerate(categories) if c == cat]
                if len(group) >= 5:
                    groups.append(group)
            if len(groups) >= 2:
                f_stat, p_val = f_oneway(*groups)
                correlations[f'anova_{pname}'] = {'F': float(f_stat), 'p': float(p_val)}

        correlation_matrix[ev_key] = correlations

        # Find best numeric correlation
        best_prop = max(numeric_props, key=lambda p: abs(correlations[p]['rho']))
        best_rho = correlations[best_prop]['rho']
        best_per_eigvec[ev_key] = {
            'best_property': best_prop,
            'rho': float(best_rho),
            'p': float(correlations[best_prop]['p']),
            'eigenvalue': float(eigenvalues[ev_idx + 1]),
        }

    # Print atlas
    print(f"\n{'Eigvec':>10s} | {'λ':>6s} | {'Best Property':>20s} | {'ρ':>7s} | {'p':>10s}")
    print("-" * 65)
    for ev_idx in range(n_eigvecs):
        ev_key = f"eigvec_{ev_idx + 2}"
        info = best_per_eigvec[ev_key]
        print(f"  {ev_key:>8s} | {info['eigenvalue']:6.2f} | {info['best_property']:>20s} | "
              f"{info['rho']:+.4f} | {info['p']:.2e}")

    # Property dominance: how many eigenvectors does each property dominate?
    print("\n[5] Property dominance summary...")
    prop_dominance = Counter()
    for ev_key, info in best_per_eigvec.items():
        if abs(info['rho']) >= 0.15:
            prop_dominance[info['best_property']] += 1

    print(f"  Properties dominating ≥1 eigenvector (|ρ|≥0.15):")
    for prop, count in prop_dominance.most_common():
        print(f"    {prop:>20s}: {count} eigenvectors")

    # Check how many eigenvectors have ANY strong correlation
    n_strong = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.20)
    n_moderate = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.15)
    n_weak = sum(1 for info in best_per_eigvec.values() if abs(info['rho']) >= 0.10)
    print(f"\n  Eigenvectors with |ρ|≥0.20: {n_strong}/{n_eigvecs}")
    print(f"  Eigenvectors with |ρ|≥0.15: {n_moderate}/{n_eigvecs}")
    print(f"  Eigenvectors with |ρ|≥0.10: {n_weak}/{n_eigvecs}")

    # Sanity check: hub should correlate with frequency
    print("\n[6] Sanity check: hub eigenvector vs frequency...")
    hub_rho, hub_p = spearmanr(hub_vec, prop_arrays['log_freq'])
    print(f"  Hub vs log_freq: ρ={hub_rho:.4f} (p={hub_p:.2e})")

    # Multi-property view: for each eigvec, show top 3 correlations
    print("\n[7] Top-3 correlations per eigenvector...")
    multi_view = {}
    for ev_idx in range(min(15, n_eigvecs)):
        ev_key = f"eigvec_{ev_idx + 2}"
        corrs = correlation_matrix[ev_key]
        numeric_corrs = [(p, corrs[p]['rho']) for p in numeric_props]
        numeric_corrs.sort(key=lambda x: abs(x[1]), reverse=True)
        top3 = numeric_corrs[:3]
        multi_view[ev_key] = [{'prop': p, 'rho': float(r)} for p, r in top3]
        top3_str = ', '.join(f"{p}={r:+.3f}" for p, r in top3)
        print(f"  {ev_key:>10s}: {top3_str}")

    # ANOVA results for categorical properties
    print("\n[8] Categorical property structure (ANOVA)...")
    for cat_prop in cat_props:
        anova_key = f'anova_{cat_prop}'
        sig_count = 0
        for ev_key in correlation_matrix:
            if anova_key in correlation_matrix[ev_key]:
                if correlation_matrix[ev_key][anova_key]['p'] < 0.001:
                    sig_count += 1
        print(f"  {cat_prop}: {sig_count}/{n_eigvecs} eigenvectors show significant (p<0.001) structure")

    # Verdict
    print("\n" + "=" * 60)
    n_unique_dominators = len(prop_dominance)

    if n_unique_dominators >= 5 and n_moderate >= 10:
        verdict = "FACTORED"
        explanation = (
            f"{n_unique_dominators} different properties dominate across {n_moderate} eigenvectors "
            f"(|ρ|≥0.15). The discrimination space has interpretable factored structure."
        )
    elif n_unique_dominators >= 3:
        verdict = "PARTIALLY_FACTORED"
        explanation = (
            f"{n_unique_dominators} properties dominate, but only {n_moderate} eigenvectors "
            f"have |ρ|≥0.15. Partial interpretability."
        )
    elif n_moderate >= 5 and n_unique_dominators <= 2:
        verdict = "ENTANGLED"
        explanation = (
            f"Only {n_unique_dominators} properties explain {n_moderate} eigenvectors. "
            f"Space is high-dimensional but property-simple."
        )
    else:
        verdict = "OPAQUE"
        explanation = (
            f"Only {n_moderate} eigenvectors have |ρ|≥0.15. "
            f"Known properties do not explain the spectral structure."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save results
    results = {
        'test': 'T1_eigenvector_property_atlas',
        'n_middles': len(all_middles),
        'n_eigvecs_analyzed': n_eigvecs,
        'hub_sanity': {'hub_vs_log_freq_rho': float(hub_rho), 'hub_eigenvalue': float(hub_val)},
        'best_per_eigvec': best_per_eigvec,
        'multi_view_top15': multi_view,
        'property_dominance': dict(prop_dominance.most_common()),
        'strength_counts': {
            'strong_020': n_strong,
            'moderate_015': n_moderate,
            'weak_010': n_weak,
        },
        'categorical_significance': {
            cat_prop: sum(1 for ev_key in correlation_matrix
                         if f'anova_{cat_prop}' in correlation_matrix[ev_key]
                         and correlation_matrix[ev_key][f'anova_{cat_prop}']['p'] < 0.001)
            for cat_prop in cat_props
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't1_eigenvector_property_atlas.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't1_eigenvector_property_atlas.json'}")


if __name__ == '__main__':
    main()
