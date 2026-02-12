#!/usr/bin/env python3
"""
Authoritative Regime Classification v2.

Replaces the broken median-split approach with proper data-driven GMM clustering
on 15 standardized per-folio features. Saves to data/regime_folio_mapping.json
as the single source of truth.

Source features:
  - folio_operational_profiles.json: kernel balance, control execution, thermochemical
  - folio_energy_frequent.json: energy/frequent operator rates
  - Transcript-derived: link_rate, vocab_richness, mean_line_length, qo_fraction, fq_rate
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

ROOT = Path(__file__).resolve().parents[3]
RESULTS_ROOT = ROOT / 'results'
BRUN_RESULTS = ROOT / 'phases' / 'BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS' / 'results'
OUTPUT_DIR = ROOT / 'data'


def load_operational_profiles():
    """Load 82-folio operational profiles (12 dimensions)."""
    path = RESULTS_ROOT / 'folio_operational_profiles.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {p['folio']: p for p in data['profiles']}


def load_energy_frequent():
    """Load energy/frequent rates per folio."""
    path = BRUN_RESULTS / 'folio_energy_frequent.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {d['folio']: d for d in data['folio_data']}


def compute_transcript_features():
    """Compute per-folio features from raw transcript."""
    tx = Transcript()
    morph = Morphology()

    # Known LINK tokens (monitoring operators) — the MIDDLE 'l' in bare form
    # FQ identification: the 4 most frequent instruction classes
    # We approximate FQ by morphological pattern: bare short tokens
    # that match known FQ patterns (daiin, ol, ar, or, al, etc.)
    FQ_TOKENS = {
        'daiin', 'ol', 'chedy', 'shedy', 'qokeedy', 'qokedy',
        'chey', 'shey', 'qokeey', 'okeedy', 'okeey',
    }

    folio_data = defaultdict(lambda: {
        'total': 0, 'link': 0, 'qo_en': 0, 'chsh_en': 0,
        'unique_middles': set(), 'lines': set(), 'fq': 0,
        'line_tokens': defaultdict(int),
    })

    # QO-leaning EN prefixes (k-initial MIDDLEs → QO per C649/C647)
    QO_PREFIXES = {'k', 'p', 't'}
    # CHSH-leaning EN prefixes (e/o-initial MIDDLEs → CHSH per C649/C647)
    CHSH_PREFIXES = {'e', 'o'}

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue

        f = token.folio
        fd = folio_data[f]
        fd['total'] += 1
        fd['lines'].add(token.line)
        fd['line_tokens'][token.line] += 1

        m = morph.extract(word)
        mid = m.middle or ''

        if mid:
            fd['unique_middles'].add(mid)

        # LINK detection: articulator 'y' or bare 'l' MIDDLE
        if mid == 'l' and not m.prefix and not m.suffix:
            fd['link'] += 1

        # Lane proxy from MIDDLE initial character (C647)
        if mid and len(mid) >= 1:
            initial = mid[0]
            if initial in QO_PREFIXES:
                fd['qo_en'] += 1
            elif initial in CHSH_PREFIXES:
                fd['chsh_en'] += 1

        # FQ detection (approximate)
        if word in FQ_TOKENS:
            fd['fq'] += 1

    result = {}
    for f, fd in folio_data.items():
        n = fd['total']
        if n < 30:
            continue
        n_lines = len(fd['lines'])
        en_total = fd['qo_en'] + fd['chsh_en']
        result[f] = {
            'link_rate': fd['link'] / n,
            'vocab_richness': len(fd['unique_middles']) / n,
            'mean_line_length': n / max(n_lines, 1),
            'qo_fraction': fd['qo_en'] / max(en_total, 1),
            'fq_rate': fd['fq'] / n,
        }

    return result


def main():
    print("=" * 70)
    print("AUTHORITATIVE REGIME CLASSIFICATION v2")
    print("=" * 70)

    # ---- Load data sources ----
    print("\n--- Loading data sources ---")
    op_profiles = load_operational_profiles()
    print(f"  Operational profiles: {len(op_profiles)} folios")

    ef_data = load_energy_frequent()
    print(f"  Energy-frequent: {len(ef_data)} folios")

    tx_features = compute_transcript_features()
    print(f"  Transcript features: {len(tx_features)} folios")

    # ---- Build unified feature matrix ----
    # Use folios present in all 3 sources
    common_folios = sorted(
        set(op_profiles.keys()) & set(ef_data.keys()) & set(tx_features.keys())
    )
    print(f"\n  Common folios: {len(common_folios)}")

    FEATURES = [
        # From operational profiles
        'k_ratio', 'h_ratio', 'e_ratio',
        'iteration_rate', 'checkpoint_rate', 'terminal_rate',
        'thermo_ke', 'thermo_kch',
        # From energy-frequent
        'energy_rate', 'frequent_rate',
        # From transcript
        'link_rate', 'vocab_richness', 'mean_line_length',
        'qo_fraction', 'fq_rate',
    ]

    n = len(common_folios)
    d = len(FEATURES)
    X = np.zeros((n, d))

    for i, folio in enumerate(common_folios):
        op = op_profiles[folio]
        ef = ef_data[folio]
        tf = tx_features[folio]

        row = [
            op['k_ratio'], op['h_ratio'], op['e_ratio'],
            op['iteration_rate'], op['checkpoint_rate'], op['terminal_rate'],
            op['thermo_ke'], op['thermo_kch'],
            ef['energy_rate'], ef['frequent_rate'],
            tf['link_rate'], tf['vocab_richness'], tf['mean_line_length'],
            tf['qo_fraction'], tf['fq_rate'],
        ]
        X[i] = row

    print(f"  Feature matrix: {X.shape}")

    # ---- Standardize ----
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ---- Feature summary ----
    print(f"\n--- Feature summary (raw) ---")
    for j, feat in enumerate(FEATURES):
        vals = X[:, j]
        print(f"  {feat:25s}: mean={vals.mean():.4f}  std={vals.std():.4f}  "
              f"min={vals.min():.4f}  max={vals.max():.4f}")

    # ---- PCA reduction ----
    # 15 features for 82 points is high-dimensional for full-covariance GMM.
    # Reduce to top 5 PCs (captures ~84% variance per BRUNSCHWIG analysis).
    from sklearn.decomposition import PCA
    from sklearn.mixture import GaussianMixture
    from sklearn.metrics import silhouette_score

    pca = PCA(n_components=5, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    cum_var = np.cumsum(pca.explained_variance_ratio_)

    print(f"\n--- PCA reduction ---")
    for pc_i, (var, cum) in enumerate(zip(pca.explained_variance_ratio_, cum_var)):
        print(f"  PC{pc_i+1}: {var:.3f} (cumulative: {cum:.3f})")
        # Show top 3 loadings
        loadings = pca.components_[pc_i]
        top_idx = np.argsort(np.abs(loadings))[::-1][:3]
        parts = [f"{FEATURES[j]}={loadings[j]:+.3f}" for j in top_idx]
        print(f"    Top loadings: {', '.join(parts)}")
    print(f"  Total variance captured: {cum_var[-1]:.3f}")

    # ---- GMM clustering on PCA space: test k=3,4,5 ----
    print(f"\n--- GMM model selection (PCA-reduced, diag covariance) ---")
    best_k = None
    best_bic = np.inf
    results_by_k = {}

    for k in [3, 4, 5, 6]:
        gmm = GaussianMixture(
            n_components=k, covariance_type='diag',
            n_init=10, max_iter=300, random_state=42,
        )
        labels = gmm.fit_predict(X_pca)
        bic = gmm.bic(X_pca)
        sil = silhouette_score(X_pca, labels)
        sizes = np.bincount(labels)

        results_by_k[k] = {
            'bic': bic, 'silhouette': sil, 'sizes': sizes.tolist(),
            'labels': labels, 'gmm': gmm,
        }

        print(f"  k={k}: BIC={bic:.1f}  silhouette={sil:.3f}  sizes={sizes.tolist()}")

        if bic < best_bic:
            best_bic = bic
            best_k = k

    print(f"\n  Best k by BIC: {best_k}")

    # Architecture expects 4 regimes. Use k=4 unless clearly wrong.
    use_k = 4
    bic_4 = results_by_k[4]['bic']
    bic_best = results_by_k[best_k]['bic']
    sil_4 = results_by_k[4]['silhouette']

    if best_k != 4:
        pct_diff = (bic_4 - bic_best) / abs(bic_best) * 100
        print(f"  k=4 BIC is {pct_diff:+.1f}% vs best (k={best_k})")
        if pct_diff > 10:
            print(f"  WARNING: k=4 substantially worse by BIC. Using k={best_k}.")
            use_k = best_k
        else:
            print(f"  Acceptable — using k=4 per architectural expectation.")

    chosen = results_by_k[use_k]
    labels = chosen['labels']
    gmm = chosen['gmm']
    sil = chosen['silhouette']
    print(f"\n  CHOSEN: k={use_k}, silhouette={sil:.3f}")

    # ---- Cluster centroids (in original scale) ----
    # GMM centroids are in PCA space; back-project to original feature space
    print(f"\n--- Cluster centroids (original scale) ---")
    centroids_pca = gmm.means_  # (k, 5)
    centroids_scaled = pca.inverse_transform(centroids_pca)  # (k, 15)
    centroids_raw = scaler.inverse_transform(centroids_scaled)  # (k, 15)

    cluster_profiles = {}
    for c in range(use_k):
        mask = labels == c
        n_c = mask.sum()
        # Use actual cluster means from raw data for accuracy
        actual_mean = X[mask].mean(axis=0)
        centroid = {FEATURES[j]: round(float(actual_mean[j]), 4) for j in range(d)}
        cluster_profiles[c] = {
            'size': int(n_c),
            'centroid': centroid,
            'folios': [common_folios[i] for i in range(n) if mask[i]],
        }
        print(f"\n  Cluster {c} (n={n_c}):")
        for feat in FEATURES:
            val = centroid[feat]
            overall_mean = float(X[:, FEATURES.index(feat)].mean())
            ratio = val / max(overall_mean, 1e-6)
            marker = ''
            if ratio > 1.3:
                marker = ' ▲'
            elif ratio < 0.7:
                marker = ' ▼'
            print(f"    {feat:25s}: {val:.4f}{marker}")

    # ---- Label clusters by properties ----
    # Strategy: use Hungarian algorithm to optimally match clusters to regimes
    # based on feature-profile scoring.
    print(f"\n--- Cluster labeling ---")

    # Standardize centroids for comparison (z-score relative to global means)
    global_means = X.mean(axis=0)
    global_stds = X.std(axis=0)

    # Score each cluster against each regime archetype
    # Archetypes defined by which features should be HIGH vs LOW
    regime_archetypes = {
        'REGIME_1': {  # Energy-intensive
            'high': ['energy_rate', 'k_ratio', 'qo_fraction', 'thermo_ke'],
            'low': ['e_ratio', 'terminal_rate', 'vocab_richness'],
        },
        'REGIME_2': {  # Balanced/default (largest, near-average)
            'high': ['frequent_rate'],
            'low': [],  # balanced = close to mean
        },
        'REGIME_3': {  # Stability-focused
            'high': ['e_ratio', 'link_rate', 'iteration_rate'],
            'low': ['k_ratio', 'energy_rate'],
        },
        'REGIME_4': {  # Precision
            'high': ['vocab_richness', 'checkpoint_rate', 'terminal_rate'],
            'low': ['frequent_rate', 'fq_rate', 'qo_fraction', 'k_ratio'],
        },
    }

    regimes_to_assign = list(regime_archetypes.keys())
    if use_k > 4:
        # Extra clusters get generic labels
        for i in range(use_k - 4):
            regimes_to_assign.append(f'REGIME_2_{chr(ord("a") + i)}')
            regime_archetypes[f'REGIME_2_{chr(ord("a") + i)}'] = {'high': [], 'low': []}

    # Build cost matrix (lower = better match)
    cost_matrix = np.zeros((use_k, len(regimes_to_assign)))
    for c in range(use_k):
        cent = cluster_profiles[c]['centroid']
        for r, regime in enumerate(regimes_to_assign):
            arch = regime_archetypes[regime]
            score = 0
            for feat in arch.get('high', []):
                if feat in cent:
                    z = (cent[feat] - global_means[FEATURES.index(feat)]) / max(global_stds[FEATURES.index(feat)], 1e-6)
                    score += z  # positive z = good match for 'high'
            for feat in arch.get('low', []):
                if feat in cent:
                    z = (cent[feat] - global_means[FEATURES.index(feat)]) / max(global_stds[FEATURES.index(feat)], 1e-6)
                    score -= z  # negative z = good match for 'low'
            cost_matrix[c, r] = -score  # negate for minimization

    from scipy.optimize import linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    label_map = {}
    for c, r in zip(row_ind, col_ind):
        regime = regimes_to_assign[r]
        label_map[c] = regime
        cent = cluster_profiles[c]['centroid']
        score = -cost_matrix[c, r]
        print(f"  Cluster {c} → {regime} (n={cluster_profiles[c]['size']}, match_score={score:.2f})")
        print(f"    k_ratio={cent['k_ratio']:.3f}  e_ratio={cent['e_ratio']:.3f}  "
              f"energy={cent['energy_rate']:.3f}  frequent={cent['frequent_rate']:.3f}  "
              f"vocab={cent['vocab_richness']:.3f}")

    # ---- Section cross-tabulation ----
    print(f"\n--- Section cross-tabulation ---")
    section_map = {}
    for folio, prof in op_profiles.items():
        cat = prof.get('material_category', 'UNKNOWN')
        section_map[folio] = cat

    regime_section = defaultdict(lambda: defaultdict(int))
    for i, folio in enumerate(common_folios):
        regime = label_map[labels[i]]
        section = section_map.get(folio, 'UNKNOWN')
        regime_section[regime][section] += 1

    sections = sorted(set(section_map.get(f, 'UNKNOWN') for f in common_folios))
    header = f"{'':15s}" + ''.join(f"{s:>10s}" for s in sections) + f"{'TOTAL':>8s}"
    print(f"  {header}")
    for regime in sorted(regime_section.keys()):
        row = f"  {regime:15s}"
        total = 0
        for section in sections:
            count = regime_section[regime][section]
            total += count
            row += f"{count:>10d}"
        row += f"{total:>8d}"
        print(row)

    # ---- Probabilities ----
    probs = gmm.predict_proba(X_pca)

    # ---- Build output ----
    regime_descriptions = {}
    for c in range(use_k):
        regime = label_map[c]
        cent = cluster_profiles[c]['centroid']

        # Generate description from centroid
        high_feats = []
        low_feats = []
        for feat in FEATURES:
            val = cent[feat]
            overall_mean = float(X[:, FEATURES.index(feat)].mean())
            if overall_mean > 0 and val / overall_mean > 1.3:
                high_feats.append(feat)
            elif overall_mean > 0 and val / overall_mean < 0.7:
                low_feats.append(feat)

        desc = f"High: {', '.join(high_feats) if high_feats else 'none'}. "
        desc += f"Low: {', '.join(low_feats) if low_feats else 'none'}."
        regime_descriptions[regime] = {
            'size': cluster_profiles[c]['size'],
            'description': desc,
            'high_features': high_feats,
            'low_features': low_feats,
            'centroid': cent,
        }

    regime_assignments = {}
    for i, folio in enumerate(common_folios):
        c = int(labels[i])
        regime = label_map[c]
        prob = float(probs[i, c])
        regime_assignments[folio] = {
            'regime': regime,
            'probability': round(prob, 4),
            'cluster_id': c,
        }

    output = {
        '_metadata': {
            'method': f'GMM k={use_k} on {d} standardized folio features',
            'source_features': FEATURES,
            'n_folios': n,
            'n_clusters': use_k,
            'silhouette': round(sil, 4),
            'bic': round(float(results_by_k[use_k]['bic']), 1),
            'bic_comparison': {
                str(k): round(float(results_by_k[k]['bic']), 1)
                for k in results_by_k
            },
            'silhouette_comparison': {
                str(k): round(float(results_by_k[k]['silhouette']), 4)
                for k in results_by_k
            },
            'source_files': [
                'results/folio_operational_profiles.json',
                'phases/BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS/results/folio_energy_frequent.json',
                'Transcript-derived (scripts/voynich.py)',
            ],
            'replaces': 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json',
            'warning': 'This is the authoritative regime mapping. Do not use other sources.',
        },
        'regime_assignments': regime_assignments,
        'regime_descriptions': regime_descriptions,
        'feature_means': {
            FEATURES[j]: round(float(X[:, j].mean()), 4) for j in range(d)
        },
        'feature_stds': {
            FEATURES[j]: round(float(X[:, j].std()), 4) for j in range(d)
        },
    }

    # ---- Save ----
    out_path = OUTPUT_DIR / 'regime_folio_mapping.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"REGIME CLASSIFICATION v2 COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Method: GMM k={use_k} on {d} features")
    print(f"  Silhouette: {sil:.3f}")
    print(f"  BIC: {results_by_k[use_k]['bic']:.1f}")
    print(f"  Saved: {out_path}")
    print(f"\n  Regime sizes:")
    for c in range(use_k):
        regime = label_map[c]
        n_c = cluster_profiles[c]['size']
        desc = regime_descriptions[regime]
        print(f"    {regime}: {n_c} folios — {desc['description']}")

    # ---- Confidence check ----
    all_probs = [regime_assignments[f]['probability'] for f in common_folios]
    print(f"\n  Assignment confidence:")
    print(f"    Mean: {np.mean(all_probs):.3f}")
    print(f"    Min:  {np.min(all_probs):.3f}")
    print(f"    <0.6: {sum(1 for p in all_probs if p < 0.6)} folios")
    print(f"    >0.9: {sum(1 for p in all_probs if p > 0.9)} folios")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
