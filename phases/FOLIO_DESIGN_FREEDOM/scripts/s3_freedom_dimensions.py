"""
s3_freedom_dimensions.py — Interpret PCA freedom dimensions using atom glosses.

Takes the residualized folio-atom features from s1, reproduces PCA, and interprets
the top PCs using C1195 LOCKED-tier atom glosses. Identifies extreme folios,
correlates with operational profiles, and analyzes folio pair differences.

Run from repo root:
    python phases/FOLIO_DESIGN_FREEDOM/scripts/s3_freedom_dimensions.py
"""

import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# ── Atom glosses (C1195 LOCKED/SOLID tier) ──────────────────────────────────
ATOM_GLOSSES = {
    # HEAD atoms (LOCKED)
    'k': 'heat', 'e': 'cool', 'h': 'monitor', 'a': 'into/yield',
    'o': 'arrange', 'i': 'iterate/cycle', 'n': 'bind',
    # HEAD atoms (SOLID)
    't': 'transfer',
    # MOD atoms (LOCKED)
    # (same atoms appear as MOD)
    # TERM atoms (LOCKED)
    'y': 'end',
    # SOLID confidence
    'c': 'adjust', 'd': 'mark', 's': 'sequence', 'm': 'close/final',
    # Lower confidence
    'l': 'state', 'r': 'respond', 'p': 'flag', 'f': 'flag',
}

CONFIDENCE = {
    'k': 'LOCKED', 'e': 'LOCKED', 'h': 'LOCKED', 'y': 'LOCKED',
    'i': 'LOCKED', 'n': 'LOCKED', 'a': 'LOCKED', 'o': 'LOCKED',
    'c': 'SOLID', 'd': 'SOLID', 's': 'SOLID', 'm': 'SOLID',
    't': 'SOLID', 'l': 'LOW', 'r': 'LOW', 'p': 'LOW', 'f': 'LOW',
}

PREFIX_GLOSSES = {
    'qo': 'thermal-escape', 'ch': 'energy-op-primary', 'sh': 'energy-op-alt',
    'ok': 'frequent-op', 'ot': 'frequent-op-alt', 'da': 'infrastructure',
    'ct': 'registry-ref', 'ol': 'frequent-state', 'bare': 'no-prefix',
}

DERIVED_GLOSSES = {
    'e_depth_mean': 'cooling-depth (mean e-stacking)',
    'i_depth_mean': 'iteration-depth (mean i-stacking)',
    'mean_atom_length': 'instruction-complexity',
    'headless': 'headless (infrastructure token)',
}


def gloss_feature(feat: str) -> str:
    """Return human-readable gloss for a feature name like 'head_k' or 'pfx_qo'."""
    if feat in ('e_depth_mean', 'i_depth_mean', 'mean_atom_length'):
        return DERIVED_GLOSSES[feat]
    parts = feat.split('_', 1)
    if len(parts) != 2:
        return feat
    slot, atom = parts
    if slot == 'head' and atom == 'headless':
        return DERIVED_GLOSSES['headless']
    if slot == 'pfx':
        g = PREFIX_GLOSSES.get(atom, atom)
        return f"pfx:{g}"
    g = ATOM_GLOSSES.get(atom, atom)
    conf = CONFIDENCE.get(atom, '?')
    slot_label = {'head': 'HEAD', 'mod': 'MOD', 'term': 'TERM'}.get(slot, slot)
    return f"{slot_label}:{g} [{conf}]"


def interpret_pc(loadings: dict, pc_name: str) -> dict:
    """Given feature->loading dict, produce interpretation."""
    sorted_items = sorted(loadings.items(), key=lambda x: x[1], reverse=True)
    top_pos = [(f, v) for f, v in sorted_items[:3]]
    top_neg = [(f, v) for f, v in sorted_items[-3:][::-1]]  # most negative first

    pos_glosses = [(gloss_feature(f), v) for f, v in top_pos]
    neg_glosses = [(gloss_feature(f), v) for f, v in top_neg]

    return {
        'pc': pc_name,
        'top_positive': [{'feature': f, 'gloss': gloss_feature(f), 'loading': round(v, 4)}
                         for f, v in top_pos],
        'top_negative': [{'feature': f, 'gloss': gloss_feature(f), 'loading': round(v, 4)}
                         for f, v in top_neg],
        'pos_summary': ' + '.join(g for g, _ in pos_glosses),
        'neg_summary': ' + '.join(g for g, _ in neg_glosses),
    }


def main():
    # ── Load s1 outputs ─────────────────────────────────────────────────────
    res_df = pd.read_csv('phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features_residualized.csv', index_col=0)
    with open('phases/FOLIO_DESIGN_FREEDOM/results/s1_variance_decomposition.json') as f:
        s1_results = json.load(f)

    print("=" * 80)
    print("S3: FREEDOM DIMENSION INTERPRETATION")
    print("=" * 80)

    folios = res_df.index.tolist()
    sections = res_df['section'].tolist() if 'section' in res_df.columns else ['?'] * len(folios)
    section_map = dict(zip(folios, sections))

    # Drop non-numeric columns for PCA
    numeric_cols = [c for c in res_df.columns if c not in ('section', 'token_count')]
    X = res_df[numeric_cols].values

    # ── Step 1: Reproduce PCA ───────────────────────────────────────────────
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    scaler = StandardScaler()
    X_z = scaler.fit_transform(X)

    n_components = min(5, X_z.shape[1], X_z.shape[0])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(X_z)  # (n_folios, 5)
    loadings = pca.components_       # (5, n_features)

    print(f"\nReproduced PCA on {X_z.shape[0]} folios x {X_z.shape[1]} features (z-scored)")
    print(f"Top 5 PCs explain {sum(pca.explained_variance_ratio_[:5])*100:.1f}% of variance")
    for i in range(n_components):
        print(f"  PC{i+1}: {pca.explained_variance_ratio_[i]*100:.1f}%")

    # ── Step 2: Name each PC ────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("STEP 2: PC INTERPRETATION VIA ATOM GLOSSES")
    print("=" * 80)

    pc_interpretations = []
    pc_labels = {}

    for i in range(n_components):
        loading_dict = {numeric_cols[j]: loadings[i, j] for j in range(len(numeric_cols))}
        interp = interpret_pc(loading_dict, f'PC{i+1}')

        # Propose label
        # Use the dominant polarity to name it
        pos_atoms = [x['gloss'] for x in interp['top_positive']]
        neg_atoms = [x['gloss'] for x in interp['top_negative']]

        # Simple heuristic labeling
        label = _propose_label(i, interp)
        interp['proposed_label'] = label
        pc_labels[f'PC{i+1}'] = label
        pc_interpretations.append(interp)

        print(f"\n--- PC{i+1} ({pca.explained_variance_ratio_[i]*100:.1f}%) — \"{label}\" ---")
        print(f"  Positive pole (high values):")
        for item in interp['top_positive']:
            print(f"    {item['feature']:20s}  {item['loading']:+.4f}  ({item['gloss']})")
        print(f"  Negative pole (low values):")
        for item in interp['top_negative']:
            print(f"    {item['feature']:20s}  {item['loading']:+.4f}  ({item['gloss']})")

    # ── Step 3: Extreme folios ──────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("STEP 3: EXTREME FOLIOS ON TOP 3 PCs")
    print("=" * 80)

    extreme_folios = {}
    for i in range(min(3, n_components)):
        pc_scores = scores[:, i]
        sorted_idx = np.argsort(pc_scores)

        high_3 = [(folios[j], section_map[folios[j]], round(float(pc_scores[j]), 3)) for j in sorted_idx[-3:][::-1]]
        low_3 = [(folios[j], section_map[folios[j]], round(float(pc_scores[j]), 3)) for j in sorted_idx[:3]]

        label = pc_labels[f'PC{i+1}']
        print(f"\n--- PC{i+1}: \"{label}\" ---")
        print(f"  Highest (positive pole):")
        for fol, sec, sc in high_3:
            print(f"    {fol:10s}  {sec:8s}  score={sc:+.3f}")
        print(f"  Lowest (negative pole):")
        for fol, sec, sc in low_3:
            print(f"    {fol:10s}  {sec:8s}  score={sc:+.3f}")

        extreme_folios[f'PC{i+1}'] = {
            'label': label,
            'high': [{'folio': f, 'section': s, 'score': sc} for f, s, sc in high_3],
            'low': [{'folio': f, 'section': s, 'score': sc} for f, s, sc in low_3],
        }

    # ── Step 4: Operational profile correlation ─────────────────────────────
    print("\n" + "=" * 80)
    print("STEP 4: PC-TO-OPERATIONAL CORRELATION")
    print("=" * 80)

    op_correlations = {}
    try:
        with open('results/folio_operational_profiles_v3.json') as f:
            op_data = json.load(f)

        op_metrics = ['k_ratio', 'h_ratio', 'e_ratio', 'iteration_rate',
                      'checkpoint_rate', 'terminal_rate',
                      'prep_te', 'prep_pch', 'thermo_ke', 'thermo_kch']

        # Build operational DF indexed by folio
        op_rows = {p['folio']: p for p in op_data['profiles']}
        op_df = pd.DataFrame(op_data['profiles']).set_index('folio')

        # Match folios
        common_folios = [f for f in folios if f in op_df.index]
        print(f"  Matched {len(common_folios)}/{len(folios)} folios with operational profiles")

        if len(common_folios) >= 10:
            # Get PC scores for common folios
            folio_to_idx = {f: i for i, f in enumerate(folios)}
            common_scores = np.array([scores[folio_to_idx[f]] for f in common_folios])

            available_metrics = [m for m in op_metrics if m in op_df.columns]

            print(f"\n  {'Metric':<20s}", end='')
            for i in range(n_components):
                print(f"  PC{i+1:d}(r)  ", end='')
            print()
            print("  " + "-" * (20 + n_components * 10))

            for metric in available_metrics:
                metric_vals = np.array([float(op_df.loc[f, metric]) for f in common_folios])
                # Skip if constant
                if np.std(metric_vals) < 1e-10:
                    continue

                row_data = {}
                print(f"  {metric:<20s}", end='')
                for i in range(n_components):
                    r, p = stats.pearsonr(common_scores[:, i], metric_vals)
                    sig = '*' if p < 0.05 else ' '
                    print(f"  {r:+.3f}{sig} ", end='')
                    row_data[f'PC{i+1}'] = {'r': round(float(r), 4), 'p': round(float(p), 4)}
                print()
                op_correlations[metric] = row_data

            print("\n  (* = p < 0.05)")

            # Highlight strongest correlations
            print("\n  Strongest PC-operational links:")
            for metric, pcs in op_correlations.items():
                for pc, vals in pcs.items():
                    if abs(vals['r']) >= 0.4:
                        sig = '***' if vals['p'] < 0.001 else '**' if vals['p'] < 0.01 else '*'
                        print(f"    {pc} <-> {metric}: r={vals['r']:+.4f} (p={vals['p']:.4f}) {sig}")
        else:
            print("  Insufficient folio overlap for correlation analysis")

    except FileNotFoundError:
        print("  WARNING: results/folio_operational_profiles_v3.json not found — skipping")
    except Exception as e:
        print(f"  WARNING: Error loading operational profiles: {e} — skipping")

    # ── Step 5: REGIME correlation ──────────────────────────────────────────
    print("\n" + "=" * 80)
    print("STEP 5: REGIME CORRELATION (k_ratio quartile)")
    print("=" * 80)

    regime_correlations = {}
    try:
        if 'op_df' in dir() and len(common_folios) >= 10:
            k_vals = np.array([float(op_df.loc[f, 'k_ratio']) for f in common_folios])
            # Quartile assignment: Q1=lowest k_ratio = REGIME 1, Q4=highest = REGIME 4
            quartiles = pd.qcut(k_vals, 4, labels=False) + 1  # 1-4

            print(f"  REGIME assignment by k_ratio quartile:")
            for r in range(1, 5):
                mask = quartiles == r
                k_range = k_vals[mask]
                print(f"    REGIME {r}: n={mask.sum()}, k_ratio=[{k_range.min():.3f}, {k_range.max():.3f}]")

            print(f"\n  {'PC':<6s}  {'r_spearman':>10s}  {'p':>8s}  Interpretation")
            print("  " + "-" * 50)

            for i in range(n_components):
                r, p = stats.spearmanr(common_scores[:, i], quartiles)
                label = pc_labels[f'PC{i+1}']
                sig = '*' if p < 0.05 else ' '
                strength = 'STRONG' if abs(r) > 0.5 else 'MODERATE' if abs(r) > 0.3 else 'WEAK'
                print(f"  PC{i+1:<3d}  {r:>+10.4f}  {p:>8.4f}  {strength} — {label}")
                regime_correlations[f'PC{i+1}'] = {
                    'r_spearman': round(float(r), 4),
                    'p': round(float(p), 4),
                    'strength': strength,
                }

            print(f"\n  Hypothesis: freedom PCs should be WEAKLY correlated with REGIME")
            print(f"  (since REGIME is section-controlled and features are residualized)")
            weak_count = sum(1 for v in regime_correlations.values() if v['strength'] == 'WEAK')
            total = len(regime_correlations)
            print(f"  Result: {weak_count}/{total} PCs are weakly correlated with REGIME")
            if weak_count >= total // 2:
                print(f"  => CONFIRMED: freedom dimensions are largely orthogonal to REGIME")
            else:
                print(f"  => PARTIAL: some freedom dimensions correlate with REGIME")
        else:
            print("  Skipped — operational profiles not available")
    except Exception as e:
        print(f"  Error in REGIME analysis: {e}")

    # ── Step 6: Folio pair analysis (Herbal only) ───────────────────────────
    print("\n" + "=" * 80)
    print("STEP 6: FOLIO PAIR ANALYSIS (Herbal section)")
    print("=" * 80)

    pair_analysis = {}
    herbal_folios = [f for f in folios if section_map[f] == 'Herbal']
    herbal_idx = [folios.index(f) for f in herbal_folios]
    herbal_scores = scores[herbal_idx]

    if len(herbal_folios) >= 6:
        # Euclidean distance on residualized features (not PC scores — use original z-scored)
        herbal_X = X_z[herbal_idx]
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(herbal_X, 'euclidean'))

        n_h = len(herbal_folios)
        pairs = []
        for i in range(n_h):
            for j in range(i + 1, n_h):
                pairs.append((i, j, dist_matrix[i, j]))

        pairs_sorted = sorted(pairs, key=lambda x: x[2])
        most_similar = pairs_sorted[:3]
        most_different = pairs_sorted[-3:][::-1]

        def analyze_pair(idx_a, idx_b, distance):
            fa, fb = herbal_folios[idx_a], herbal_folios[idx_b]
            # Which PCs drive the difference?
            diff_scores = herbal_scores[idx_a] - herbal_scores[idx_b]
            # Contribution of each PC to total Euclidean distance in PC space
            pc_contribs = {f'PC{i+1}': round(float(diff_scores[i] ** 2), 4) for i in range(n_components)}
            total_pc = sum(pc_contribs.values())
            pc_pcts = {k: round(v / total_pc * 100, 1) if total_pc > 0 else 0 for k, v in pc_contribs.items()}
            dominant_pc = max(pc_contribs, key=pc_contribs.get)

            return {
                'folio_a': fa, 'folio_b': fb,
                'distance': round(float(distance), 3),
                'pc_contributions_pct': pc_pcts,
                'dominant_pc': dominant_pc,
                'dominant_pc_label': pc_labels[dominant_pc],
                'score_a': {f'PC{i+1}': round(float(herbal_scores[idx_a, i]), 3) for i in range(n_components)},
                'score_b': {f'PC{i+1}': round(float(herbal_scores[idx_b, i]), 3) for i in range(n_components)},
            }

        print(f"\n  Herbal folios: {len(herbal_folios)}")

        print(f"\n  --- 3 Most Similar Herbal Pairs ---")
        similar_results = []
        for idx_a, idx_b, dist in most_similar:
            result = analyze_pair(idx_a, idx_b, dist)
            similar_results.append(result)
            print(f"\n  {result['folio_a']} vs {result['folio_b']} (dist={result['distance']:.3f})")
            print(f"    Dominant PC: {result['dominant_pc']} — \"{result['dominant_pc_label']}\"")
            for pc, pct in result['pc_contributions_pct'].items():
                bar = '#' * int(pct / 5)
                print(f"      {pc}: {pct:5.1f}% {bar}")

        print(f"\n  --- 3 Most Different Herbal Pairs ---")
        different_results = []
        for idx_a, idx_b, dist in most_different:
            result = analyze_pair(idx_a, idx_b, dist)
            different_results.append(result)
            print(f"\n  {result['folio_a']} vs {result['folio_b']} (dist={result['distance']:.3f})")
            print(f"    Dominant PC: {result['dominant_pc']} — \"{result['dominant_pc_label']}\"")
            for pc, pct in result['pc_contributions_pct'].items():
                bar = '#' * int(pct / 5)
                print(f"      {pc}: {pct:5.1f}% {bar}")

        pair_analysis = {
            'n_herbal_folios': len(herbal_folios),
            'most_similar': similar_results,
            'most_different': different_results,
        }
    else:
        print("  Insufficient Herbal folios for pair analysis")

    # ── Save JSON ───────────────────────────────────────────────────────────
    output = {
        'n_folios': len(folios),
        'n_features': len(numeric_cols),
        'n_pcs': n_components,
        'variance_explained': [round(float(v) * 100, 2) for v in pca.explained_variance_ratio_],
        'cumulative_variance': [round(float(sum(pca.explained_variance_ratio_[:i+1])) * 100, 2) for i in range(n_components)],
        'pc_interpretations': pc_interpretations,
        'pc_labels': pc_labels,
        'extreme_folios': extreme_folios,
        'operational_correlations': op_correlations,
        'regime_correlations': regime_correlations,
        'folio_pair_analysis': pair_analysis,
    }

    out_path = 'phases/FOLIO_DESIGN_FREEDOM/results/s3_freedom_dimensions.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n{'=' * 80}")
    print(f"Saved: {out_path}")
    print(f"{'=' * 80}")


def _propose_label(pc_idx: int, interp: dict) -> str:
    """Propose an interpretive label for a PC based on its loadings."""
    pos = [x['feature'] for x in interp['top_positive']]
    neg = [x['feature'] for x in interp['top_negative']]
    all_feats = pos + neg

    # PC1: typically the biggest thermal contrast
    if pc_idx == 0:
        if 'head_a' in pos and 'head_e' in neg:
            return "Yield vs Cooling emphasis"
        if 'head_e' in neg or 'e_depth_mean' in neg:
            return "Dry-heat vs Cooling emphasis"
        return "Thermal polarity"

    if pc_idx == 1:
        if 'pfx_qo' in pos or 'mod_i' in pos:
            return "Escape-iteration complexity"
        return "Complexity axis"

    if pc_idx == 2:
        if 'head_k' in pos:
            return "Direct heat vs Modulated processing"
        return "Heat directness"

    if pc_idx == 3:
        if 'head_headless' in pos:
            return "Infrastructure density vs Cooling-state"
        return "Infrastructure vs specification"

    if pc_idx == 4:
        if 'pfx_ot' in pos or 'pfx_da' in neg:
            return "Operator-type selection"
        return "Operator preference axis"

    return f"Freedom dimension {pc_idx + 1}"


if __name__ == '__main__':
    main()
