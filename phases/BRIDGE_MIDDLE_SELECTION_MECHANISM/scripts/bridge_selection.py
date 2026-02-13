"""
Phase 331: BRIDGE_MIDDLE_SELECTION_MECHANISM
=============================================
What predicts which MIDDLEs bridge from A's discrimination manifold
into B's 49-class grammar? Only 85/972 (8.7%) cross over (C1011).

Tests whether bridging is explained by frequency/generality (boring)
or requires specific structural properties (revealing).
"""

import json
import sys
import time
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.stats import mannwhitneyu, fisher_exact, chi2_contingency
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore', category=UserWarning)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology


def load_all_data():
    """Load all precomputed data sources."""
    data = {}

    # 1. Affordance table (972 MIDDLEs with all behavioral signatures)
    with open(ROOT / 'data' / 'middle_affordance_table.json') as f:
        aff = json.load(f)
    data['affordance'] = aff

    # 2. Prefix promiscuity
    path = ROOT / 'phases' / 'PREFIX_MIDDLE_SELECTIVITY' / 'results' / 'prefix_middle_inventory.json'
    with open(path) as f:
        inv = json.load(f)
    data['prefix_inventory'] = inv.get('selectivity', {}).get('per_middle', {})

    # 3. Compatibility matrix for eigenvector computation
    data['compat_matrix'] = np.load(
        ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    )

    # 4. Token -> class mapping
    with open(ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        cm = json.load(f)
    data['token_to_class'] = {k: int(v) for k, v in cm['token_to_class'].items()}

    return data


def identify_bridge_middles(data):
    """Reconstruct the 85 bridge MIDDLEs (Phase 329 logic)."""
    tx = Transcript()
    morph = Morphology()
    token_to_class = data['token_to_class']

    # Get sorted A MIDDLEs (the 972 that define the discrimination manifold)
    a_middles_set = set()
    for token in tx.currier_a():
        word = token.word
        if not word.strip() or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            a_middles_set.add(m.middle)

    a_middles = sorted(a_middles_set)
    a_middles_lookup = set(a_middles)

    # Find which A MIDDLEs appear in B's classified tokens
    b_middle_classes = defaultdict(lambda: defaultdict(int))  # middle -> class -> count
    for token in tx.currier_b():
        word = token.word
        if not word.strip() or '*' in word:
            continue
        cls = token_to_class.get(word)
        if cls is None:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in a_middles_lookup:
            b_middle_classes[m.middle][cls] += 1

    # Bridge = A MIDDLE that appears in at least one B class
    bridge_set = set(b_middle_classes.keys())

    return a_middles, bridge_set, dict(b_middle_classes)


def compute_eigenvectors(compat_matrix):
    """Compute eigenvectors of compatibility matrix."""
    evals, evecs = np.linalg.eigh(compat_matrix.astype(np.float64))
    # Sort descending
    idx = np.argsort(-evals)
    evals = evals[idx]
    evecs = evecs[:, idx]
    return evals, evecs


def build_predictor_matrix(a_middles, bridge_set, data, evals, evecs):
    """Build feature matrix for all 972 MIDDLEs."""
    aff = data['affordance']['middles']
    prefix_inv = data['prefix_inventory']

    feature_names = [
        'compat_degree', 'token_frequency', 'radial_depth', 'length',
        'k_ratio', 'e_ratio', 'h_ratio', 'is_compound', 'qo_affinity',
        'regime_entropy', 'initial_rate', 'final_rate', 'folio_spread',
        'hub_loading', 'residual_norm', 'n_prefixes', 'affordance_bin',
    ]

    n = len(a_middles)
    X = np.full((n, len(feature_names)), np.nan)
    y = np.zeros(n, dtype=int)

    for i, mid in enumerate(a_middles):
        if mid in bridge_set:
            y[i] = 1

        entry = aff.get(mid)
        if entry is None:
            continue

        sig = entry.get('behavioral_signature', {})
        X[i, 0] = entry.get('compat_degree', np.nan)
        X[i, 1] = entry.get('token_frequency', np.nan)
        X[i, 2] = entry.get('radial_depth', np.nan)
        X[i, 3] = sig.get('length', np.nan)
        X[i, 4] = sig.get('k_ratio', np.nan)
        X[i, 5] = sig.get('e_ratio', np.nan)
        X[i, 6] = sig.get('h_ratio', np.nan)
        X[i, 7] = sig.get('is_compound', np.nan)
        X[i, 8] = sig.get('qo_affinity', np.nan)
        X[i, 9] = sig.get('regime_entropy', np.nan)
        X[i, 10] = sig.get('initial_rate', np.nan)
        X[i, 11] = sig.get('final_rate', np.nan)
        X[i, 12] = sig.get('folio_spread', np.nan)

        # Eigenvector features
        X[i, 13] = abs(evecs[i, 0])  # hub eigenmode loading (absolute)
        X[i, 14] = np.sqrt(np.sum(evecs[i, 1:101] ** 2))  # residual norm (top 100)

        # Prefix promiscuity
        pfx_data = prefix_inv.get(mid)
        X[i, 15] = pfx_data['n_prefixes'] if pfx_data else np.nan

        # Affordance bin
        X[i, 16] = entry.get('affordance_bin', np.nan)

    return X, y, feature_names


def run_t1(X, y, feature_names):
    """T1: Univariate Screening."""
    print("\n=== T1: Univariate Screening ===")

    n_features = len(feature_names)
    n_tests = n_features
    alpha = 0.05 / n_tests  # Bonferroni

    results = []
    bridge_idx = np.where(y == 1)[0]
    non_bridge_idx = np.where(y == 0)[0]

    for j, fname in enumerate(feature_names):
        col = X[:, j]
        valid = ~np.isnan(col)

        b_vals = col[valid & (y == 1)]
        nb_vals = col[valid & (y == 0)]

        if len(b_vals) < 5 or len(nb_vals) < 5:
            results.append({
                'feature': fname, 'n_bridge': len(b_vals), 'n_nonbridge': len(nb_vals),
                'test': 'SKIP', 'p': 1.0, 'significant': False,
            })
            continue

        if fname in ('affordance_bin',):
            # Categorical — use chi-square
            # Bin both into categories
            bins_b = b_vals.astype(int)
            bins_nb = nb_vals.astype(int)
            all_bins = sorted(set(bins_b) | set(bins_nb))
            table = np.zeros((2, len(all_bins)), dtype=int)
            for k, b in enumerate(all_bins):
                table[0, k] = np.sum(bins_b == b)
                table[1, k] = np.sum(bins_nb == b)
            if table.shape[1] > 1:
                chi2, p, _, _ = chi2_contingency(table)
                test_name = 'chi2'
            else:
                chi2, p = 0, 1.0
                test_name = 'chi2'
            effect = float(chi2)
            results.append({
                'feature': fname, 'test': test_name, 'statistic': float(chi2), 'p': float(p),
                'bridge_mean': float(np.mean(b_vals)), 'nonbridge_mean': float(np.mean(nb_vals)),
                'n_bridge': len(b_vals), 'n_nonbridge': len(nb_vals),
                'significant': p < alpha,
            })
        else:
            # Continuous — Mann-Whitney U
            u_stat, p = mannwhitneyu(b_vals, nb_vals, alternative='two-sided')
            # Rank-biserial correlation
            n1, n2 = len(b_vals), len(nb_vals)
            rbc = 1 - (2 * u_stat) / (n1 * n2)

            results.append({
                'feature': fname, 'test': 'mann_whitney',
                'U': float(u_stat), 'p': float(p), 'rank_biserial': float(rbc),
                'bridge_mean': float(np.mean(b_vals)), 'bridge_median': float(np.median(b_vals)),
                'nonbridge_mean': float(np.mean(nb_vals)), 'nonbridge_median': float(np.median(nb_vals)),
                'n_bridge': len(b_vals), 'n_nonbridge': len(nb_vals),
                'significant': p < alpha,
            })

    # Print summary
    sig_features = [r for r in results if r['significant']]
    print(f"  Bonferroni alpha: {alpha:.4f}")
    print(f"  Significant: {len(sig_features)}/{n_features}")
    for r in sorted(results, key=lambda x: x['p']):
        sig_mark = " ***" if r['significant'] else ""
        if 'bridge_mean' in r:
            print(f"    {r['feature']:>20}: bridge={r['bridge_mean']:.3f} nonbridge={r['nonbridge_mean']:.3f} p={r['p']:.2e}{sig_mark}")
        else:
            print(f"    {r['feature']:>20}: p={r['p']:.2e}{sig_mark}")

    return results


def run_t2(X, y, feature_names):
    """T2: Frequency Baseline — can frequency alone predict bridge status?"""
    print("\n=== T2: Frequency Baseline ===")

    freq_idx = feature_names.index('token_frequency')
    freq_col = X[:, freq_idx].reshape(-1, 1)
    valid = ~np.isnan(freq_col.ravel())

    X_freq = freq_col[valid]
    y_freq = y[valid]

    scaler = StandardScaler()
    X_freq_scaled = scaler.fit_transform(X_freq)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = LogisticRegression(max_iter=1000, random_state=42)

    probs = cross_val_predict(model, X_freq_scaled, y_freq, cv=cv, method='predict_proba')[:, 1]
    auc_freq = roc_auc_score(y_freq, probs)

    print(f"  Frequency-only AUC: {auc_freq:.3f}")

    return {
        'auc_frequency_only': float(auc_freq),
        'n_valid': int(valid.sum()),
        'n_bridge': int(y_freq.sum()),
    }


def run_t3(X, y, feature_names, t1_results):
    """T3: Multivariate Model — all significant predictors."""
    print("\n=== T3: Multivariate Model ===")

    # Use all continuous features (exclude affordance_bin which is categorical)
    continuous_features = [i for i, f in enumerate(feature_names) if f != 'affordance_bin']

    # Build valid mask (no NaN in any continuous feature)
    valid = np.ones(len(y), dtype=bool)
    for j in continuous_features:
        valid &= ~np.isnan(X[:, j])

    X_full = X[valid][:, continuous_features]
    y_full = y[valid]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_full)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = LogisticRegression(max_iter=1000, random_state=42, C=1.0)

    probs = cross_val_predict(model, X_scaled, y_full, cv=cv, method='predict_proba')[:, 1]
    auc_full = roc_auc_score(y_full, probs)

    # Permutation importance (1000 shuffles per feature)
    rng = np.random.default_rng(42)
    n_perm = 200  # Per feature, for speed
    importances = {}
    cont_names = [feature_names[i] for i in continuous_features]

    for feat_idx in range(X_scaled.shape[1]):
        perm_aucs = []
        for _ in range(n_perm):
            X_perm = X_scaled.copy()
            X_perm[:, feat_idx] = rng.permutation(X_perm[:, feat_idx])
            probs_perm = cross_val_predict(model, X_perm, y_full, cv=cv, method='predict_proba')[:, 1]
            perm_aucs.append(roc_auc_score(y_full, probs_perm))

        drop = auc_full - np.mean(perm_aucs)
        importances[cont_names[feat_idx]] = {
            'auc_drop': float(drop),
            'perm_mean': float(np.mean(perm_aucs)),
            'perm_std': float(np.std(perm_aucs)),
        }

    # Sort by importance
    sorted_imp = sorted(importances.items(), key=lambda x: -x[1]['auc_drop'])

    print(f"  Full model AUC: {auc_full:.3f}")
    print(f"  N valid: {valid.sum()} (bridges: {y_full.sum()})")
    print(f"  Feature importances (AUC drop):")
    for fname, imp in sorted_imp[:10]:
        print(f"    {fname:>20}: {imp['auc_drop']:+.4f}")

    # Fit final model for coefficients
    model.fit(X_scaled, y_full)
    coefficients = {cont_names[i]: float(model.coef_[0, i]) for i in range(len(cont_names))}

    return {
        'auc_full': float(auc_full),
        'n_valid': int(valid.sum()),
        'n_bridge': int(y_full.sum()),
        'n_features': len(continuous_features),
        'feature_importances': dict(sorted_imp),
        'coefficients': coefficients,
    }


def run_t4(X, y, feature_names, data):
    """T4: Affordance Bin Enrichment."""
    print("\n=== T4: Affordance Bin Enrichment ===")

    bin_idx = feature_names.index('affordance_bin')
    bins = X[:, bin_idx]
    valid = ~np.isnan(bins)

    bins_v = bins[valid].astype(int)
    y_v = y[valid]

    unique_bins = sorted(set(bins_v))
    n_bridge_total = y_v.sum()
    n_total = len(y_v)
    base_rate = n_bridge_total / n_total

    # Per-bin enrichment
    bin_enrichment = {}
    for b in unique_bins:
        mask = bins_v == b
        n_bin = mask.sum()
        n_bridge_bin = (y_v[mask] == 1).sum()
        rate = n_bridge_bin / n_bin if n_bin > 0 else 0
        enrichment = rate / base_rate if base_rate > 0 else 0
        label = data['affordance']['_metadata']['affordance_bins'].get(str(b), {}).get('label', f'bin_{b}')
        bin_enrichment[int(b)] = {
            'label': label,
            'n_total': int(n_bin),
            'n_bridge': int(n_bridge_bin),
            'rate': float(rate),
            'enrichment': float(enrichment),
        }

    # Chi-square test
    table = np.zeros((2, len(unique_bins)), dtype=int)
    for k, b in enumerate(unique_bins):
        mask = bins_v == b
        table[0, k] = (y_v[mask] == 1).sum()
        table[1, k] = (y_v[mask] == 0).sum()

    chi2, p, dof, _ = chi2_contingency(table)

    # HUB_UNIVERSAL (bin 0) specific test
    hub_mask = bins_v == 0
    hub_table = np.array([
        [(y_v[hub_mask] == 1).sum(), (y_v[~hub_mask] == 1).sum()],
        [(y_v[hub_mask] == 0).sum(), (y_v[~hub_mask] == 0).sum()],
    ])
    _, p_hub = fisher_exact(hub_table)

    print(f"  Chi-square: {chi2:.1f}, p={p:.2e}")
    print(f"  HUB_UNIVERSAL (bin 0) Fisher p={p_hub:.2e}")
    print(f"  Per-bin enrichment:")
    for b in unique_bins:
        e = bin_enrichment[b]
        marker = " <--" if e['enrichment'] > 2.0 else ""
        print(f"    Bin {b} ({e['label']:>25}): {e['n_bridge']}/{e['n_total']} rate={e['rate']:.3f} enrichment={e['enrichment']:.2f}x{marker}")

    return {
        'chi2': float(chi2),
        'chi2_p': float(p),
        'chi2_dof': int(dof),
        'hub_fisher_p': float(p_hub),
        'base_rate': float(base_rate),
        'per_bin': bin_enrichment,
    }


def run_t5(X, y, feature_names, a_middles, bridge_set, b_middle_classes):
    """T5: Structural Profile of bridges."""
    print("\n=== T5: Structural Profile ===")

    bridge_idx = np.where(y == 1)[0]
    non_bridge_idx = np.where(y == 0)[0]

    profile = {}
    for j, fname in enumerate(feature_names):
        if fname == 'affordance_bin':
            continue
        col = X[:, j]
        b_vals = col[bridge_idx]
        nb_vals = col[non_bridge_idx]
        b_valid = b_vals[~np.isnan(b_vals)]
        nb_valid = nb_vals[~np.isnan(nb_vals)]

        if len(b_valid) > 0 and len(nb_valid) > 0:
            profile[fname] = {
                'bridge_mean': float(np.mean(b_valid)),
                'bridge_median': float(np.median(b_valid)),
                'nonbridge_mean': float(np.mean(nb_valid)),
                'nonbridge_median': float(np.median(nb_valid)),
                'ratio': float(np.mean(b_valid) / np.mean(nb_valid)) if np.mean(nb_valid) != 0 else float('inf'),
            }

    # Macro-state distribution (from Phase 329 data)
    MACRO_STATE_PARTITION = {
        'FL_HAZ': {7, 30}, 'FQ': {9, 13, 14, 23}, 'CC': {10, 11, 12},
        'AXm': {3, 5, 18, 19, 42, 45},
        'AXM': {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
        'FL_SAFE': {38, 40},
    }
    CLASS_TO_MACRO = {}
    for state, classes in MACRO_STATE_PARTITION.items():
        for c in classes:
            CLASS_TO_MACRO[c] = state

    macro_dist = defaultdict(int)
    for mid in bridge_set:
        if mid in b_middle_classes:
            # Find dominant class
            dom_cls = max(b_middle_classes[mid].items(), key=lambda x: x[1])[0]
            macro = CLASS_TO_MACRO.get(dom_cls, 'UNKNOWN')
            macro_dist[macro] += 1

    print(f"  Bridge population: {len(bridge_set)} MIDDLEs")
    print(f"  Macro-state distribution: {dict(macro_dist)}")
    print(f"  Key ratios (bridge/nonbridge):")
    for fname in ['compat_degree', 'token_frequency', 'length', 'folio_spread',
                   'hub_loading', 'residual_norm', 'n_prefixes']:
        if fname in profile:
            p = profile[fname]
            print(f"    {fname:>20}: {p['bridge_mean']:.2f} / {p['nonbridge_mean']:.2f} = {p['ratio']:.2f}x")

    # List the 85 bridge MIDDLEs
    bridge_list = sorted(bridge_set)

    return {
        'n_bridge': len(bridge_set),
        'n_nonbridge': len(a_middles) - len(bridge_set),
        'macro_state_distribution': dict(macro_dist),
        'feature_profiles': profile,
        'bridge_middles': bridge_list,
    }


def run_t6(t1, t2, t3, t4, t5):
    """T6: Synthesis."""
    print("\n=== T6: Synthesis ===")

    # P1: Bridge MIDDLEs have higher compat_degree
    cd = next((r for r in t1 if r['feature'] == 'compat_degree'), None)
    p1_pass = cd and cd['significant'] and cd['bridge_mean'] > cd['nonbridge_mean']
    print(f"  P1 (higher compat_degree): {'PASS' if p1_pass else 'FAIL'}")

    # P2: Bridge MIDDLEs are shorter
    ln = next((r for r in t1 if r['feature'] == 'length'), None)
    p2_pass = ln and ln['significant'] and ln['bridge_mean'] < ln['nonbridge_mean']
    print(f"  P2 (shorter length): {'PASS' if p2_pass else 'FAIL'}")

    # P3: Frequency alone does NOT explain (AUC_full - AUC_freq > 0.05)
    auc_diff = t3['auc_full'] - t2['auc_frequency_only']
    p3_pass = auc_diff > 0.05
    print(f"  P3 (structural > frequency, diff={auc_diff:.3f}): {'PASS' if p3_pass else 'FAIL'}")

    # P4: HUB_UNIVERSAL enriched > 2x
    hub_enrich = t4['per_bin'].get(0, {}).get('enrichment', 0)
    p4_pass = hub_enrich > 2.0 and t4['hub_fisher_p'] < 0.05
    print(f"  P4 (HUB_UNIVERSAL enrichment={hub_enrich:.2f}x, p={t4['hub_fisher_p']:.2e}): {'PASS' if p4_pass else 'FAIL'}")

    # P5: Higher folio_spread
    fs = next((r for r in t1 if r['feature'] == 'folio_spread'), None)
    p5_pass = fs and fs['significant'] and fs['bridge_mean'] > fs['nonbridge_mean']
    print(f"  P5 (higher folio_spread): {'PASS' if p5_pass else 'FAIL'}")

    # P6: Higher prefix promiscuity
    np_feat = next((r for r in t1 if r['feature'] == 'n_prefixes'), None)
    p6_pass = np_feat and np_feat['significant'] and np_feat['bridge_mean'] > np_feat['nonbridge_mean']
    print(f"  P6 (higher n_prefixes): {'PASS' if p6_pass else 'FAIL'}")

    predictions = {
        'P1_compat_degree': {'pass': p1_pass},
        'P2_shorter': {'pass': p2_pass},
        'P3_structural_beyond_freq': {'auc_diff': float(auc_diff), 'pass': p3_pass},
        'P4_hub_enrichment': {'enrichment': float(hub_enrich), 'pass': p4_pass},
        'P5_folio_spread': {'pass': p5_pass},
        'P6_prefix_promiscuity': {'pass': p6_pass},
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])

    # Verdict
    if n_pass >= 5 and t2['auc_frequency_only'] > 0.85 and not p3_pass:
        verdict = 'TOPOLOGICAL_SELECTION'
    elif p3_pass and 3 <= n_pass <= 4:
        verdict = 'STRUCTURAL_SELECTION'
    elif p3_pass and n_pass >= 5:
        verdict = 'COMPOSITE_SELECTION'
    elif n_pass >= 5 and not p3_pass:
        verdict = 'TOPOLOGICAL_SELECTION'
    elif n_pass <= 2:
        verdict = 'ARBITRARY_BRIDGE'
    else:
        # Default based on whether frequency suffices
        if t2['auc_frequency_only'] > 0.85:
            verdict = 'TOPOLOGICAL_SELECTION'
        elif p3_pass:
            verdict = 'STRUCTURAL_SELECTION'
        else:
            verdict = 'COMPOSITE_SELECTION'

    print(f"\n  Predictions: {n_pass}/6 passed")
    print(f"  Frequency-only AUC: {t2['auc_frequency_only']:.3f}")
    print(f"  Full model AUC: {t3['auc_full']:.3f}")
    print(f"\n  *** VERDICT: {verdict} ***")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': 6,
        'auc_frequency': t2['auc_frequency_only'],
        'auc_full': t3['auc_full'],
        'auc_diff': float(auc_diff),
        'verdict': verdict,
    }


if __name__ == '__main__':
    t0 = time.time()

    print("Phase 331: BRIDGE_MIDDLE_SELECTION_MECHANISM")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    data = load_all_data()

    # Identify bridge MIDDLEs
    print("Identifying bridge MIDDLEs...")
    a_middles, bridge_set, b_middle_classes = identify_bridge_middles(data)
    print(f"  A MIDDLEs: {len(a_middles)}, Bridges: {len(bridge_set)}")

    # Compute eigenvectors
    print("Computing eigenvectors...")
    evals, evecs = compute_eigenvectors(data['compat_matrix'])
    print(f"  Top eigenvalue: {evals[0]:.2f}, residual: {evals[1]:.2f}")

    # Build predictor matrix
    print("Building predictor matrix...")
    X, y, feature_names = build_predictor_matrix(a_middles, bridge_set, data, evals, evecs)
    print(f"  Shape: {X.shape}, Bridges: {y.sum()}")

    # Run tests
    t1 = run_t1(X, y, feature_names)
    t2 = run_t2(X, y, feature_names)
    t3 = run_t3(X, y, feature_names, t1)
    t4 = run_t4(X, y, feature_names, data)
    t5 = run_t5(X, y, feature_names, a_middles, bridge_set, b_middle_classes)
    t6 = run_t6(t1, t2, t3, t4, t5)

    elapsed = time.time() - t0

    # Save results
    results = {
        'phase': 'BRIDGE_MIDDLE_SELECTION_MECHANISM',
        'phase_number': 331,
        'question': 'What predicts which MIDDLEs bridge from A discrimination manifold into B 49-class grammar?',
        'n_a_middles': len(a_middles),
        'n_bridges': len(bridge_set),
        'bridge_rate': len(bridge_set) / len(a_middles),
        't1_univariate': t1,
        't2_frequency_baseline': t2,
        't3_multivariate': t3,
        't4_bin_enrichment': t4,
        't5_structural_profile': t5,
        't6_synthesis': t6,
        'elapsed_seconds': round(elapsed, 1),
    }

    def numpy_safe(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    out_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=numpy_safe)

    print(f"\nResults saved to {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")
