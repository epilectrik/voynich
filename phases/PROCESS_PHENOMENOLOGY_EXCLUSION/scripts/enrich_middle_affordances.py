#!/usr/bin/env python3
"""
Enrich MIDDLE Affordance Table with Behavioral Signatures.

Computes a 17-dimensional behavioral feature vector per MIDDLE from:
  - Existing table (radial_depth, compat_degree, token_frequency)
  - Morphological analysis (length, k/e/h ratios, compound status)
  - Lane association (qo_affinity from kernel composition, C647/C649)
  - Regime enrichment (from authoritative regime_folio_mapping.json)
  - Positional tendency (initial/final rates)
  - Distribution breadth (folio_spread)

Then clusters in behavioral space and generates operational affordance profiles.

Tier 4 speculative. NOT semantic assignment.
"""

import sys
import json
import math
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / 'data'

N_B_FOLIOS = 82  # Total Currier B folios


def load_existing_table():
    """Load current middle_affordance_table.json."""
    path = DATA_DIR / 'middle_affordance_table.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_regime_mapping():
    """Load authoritative regime→folio mapping."""
    path = DATA_DIR / 'regime_folio_mapping.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Build folio→regime lookup
    return {
        folio: info['regime']
        for folio, info in data['regime_assignments'].items()
    }


def compute_kernel_ratios(middle):
    """Compute k/e/h character ratios for a MIDDLE string."""
    if not middle:
        return 0.0, 0.0, 0.0
    n = len(middle)
    k_count = middle.count('k')
    e_count = middle.count('e')
    h_count = middle.count('h')
    return k_count / n, e_count / n, h_count / n


def compute_qo_affinity(middle):
    """Compute QO affinity (0=CHSH, 1=QO, 0.5=neutral) from kernel content (C647)."""
    if not middle:
        return 0.5
    k_count = middle.count('k') + middle.count('t') + middle.count('p')
    e_count = middle.count('e') + middle.count('o')
    total = k_count + e_count
    if total == 0:
        return 0.5
    return k_count / total


def compute_transcript_features(folio_regime):
    """Compute per-MIDDLE features from B transcript."""
    tx = Transcript()
    morph = Morphology()

    mid_data = defaultdict(lambda: {
        'count': 0, 'folios': set(), 'initial': 0, 'final': 0,
        'regime_counts': defaultdict(int),
    })

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue

        m = morph.extract(word)
        mid = m.middle
        if not mid:
            continue

        folio = token.folio
        regime = folio_regime.get(folio, None)

        md = mid_data[mid]
        md['count'] += 1
        md['folios'].add(folio)

        # Position: use Token's line_initial/line_final booleans
        if token.line_initial:
            md['initial'] += 1
        if token.line_final:
            md['final'] += 1

        if regime:
            md['regime_counts'][regime] += 1

    return mid_data


def compute_regime_enrichment(mid_data, folio_regime):
    """Compute per-MIDDLE regime enrichment ratios."""
    # Total tokens per regime
    regime_totals = defaultdict(int)
    total_all = 0
    for mid, data in mid_data.items():
        for regime, count in data['regime_counts'].items():
            regime_totals[regime] += count
            total_all += count

    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    enrichments = {}

    for mid, data in mid_data.items():
        mid_total = data['count']
        if mid_total == 0:
            enrichments[mid] = {r: 1.0 for r in regimes}
            enrichments[mid]['entropy'] = math.log(4)
            continue

        mid_enrichment = {}
        probs = []
        for regime in regimes:
            obs = data['regime_counts'].get(regime, 0)
            regime_total = regime_totals.get(regime, 1)
            # Expected = mid_total * (regime_total / total_all)
            expected = mid_total * (regime_total / max(total_all, 1))
            if expected > 0:
                ratio = obs / expected
            else:
                ratio = 1.0
            mid_enrichment[regime] = round(ratio, 4)
            # For entropy
            p = obs / max(mid_total, 1)
            probs.append(p)

        # Shannon entropy
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log(p + 1e-10)
        mid_enrichment['entropy'] = round(entropy, 4)

        enrichments[mid] = mid_enrichment

    return enrichments


def main():
    print("=" * 70)
    print("ENRICHING MIDDLE AFFORDANCE TABLE WITH BEHAVIORAL SIGNATURES")
    print("=" * 70)

    # ---- Load existing data ----
    print("\n--- Loading data ---")
    table = load_existing_table()
    existing_middles = table['middles']
    print(f"  Existing table: {len(existing_middles)} MIDDLEs")

    folio_regime = load_regime_mapping()
    print(f"  Regime mapping: {len(folio_regime)} folios")

    # ---- Build MiddleAnalyzer for compound detection ----
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')
    print(f"  MiddleAnalyzer: {mid_analyzer.summary()['core_count']} core MIDDLEs")

    # ---- Compute transcript features ----
    print("\n--- Computing transcript features ---")
    mid_data = compute_transcript_features(folio_regime)
    print(f"  MIDDLEs with transcript data: {len(mid_data)}")

    # ---- Compute regime enrichments ----
    print("  Computing regime enrichments...")
    enrichments = compute_regime_enrichment(mid_data, folio_regime)

    # ---- Build feature vectors ----
    print("\n--- Building feature vectors ---")

    middles = sorted(existing_middles.keys())
    n = len(middles)

    FEATURE_NAMES = [
        'radial_depth', 'compat_degree', 'token_frequency',
        'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound',
        'qo_affinity',
        'regime_1_enrichment', 'regime_2_enrichment',
        'regime_3_enrichment', 'regime_4_enrichment', 'regime_entropy',
        'initial_rate', 'final_rate', 'folio_spread',
    ]
    d = len(FEATURE_NAMES)

    X = np.zeros((n, d))
    for i, mid in enumerate(middles):
        entry = existing_middles[mid]
        td = mid_data.get(mid, None)
        enr = enrichments.get(mid, {r: 1.0 for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']})
        if 'entropy' not in enr:
            enr['entropy'] = math.log(4)

        count = entry['token_frequency']
        k_r, e_r, h_r = compute_kernel_ratios(mid)

        initial_rate = 0.0
        final_rate = 0.0
        folio_spread = 0.0
        if td and td['count'] > 0:
            initial_rate = td['initial'] / td['count']
            final_rate = td['final'] / td['count']
            folio_spread = len(td['folios']) / N_B_FOLIOS

        X[i] = [
            entry['radial_depth'],
            entry['compat_degree'],
            count,
            len(mid),
            k_r, e_r, h_r,
            1.0 if mid_analyzer.is_compound(mid) else 0.0,
            compute_qo_affinity(mid),
            enr.get('REGIME_1', 1.0),
            enr.get('REGIME_2', 1.0),
            enr.get('REGIME_3', 1.0),
            enr.get('REGIME_4', 1.0),
            enr.get('entropy', math.log(4)),
            initial_rate,
            final_rate,
            folio_spread,
        ]

    print(f"  Feature matrix: {X.shape}")

    # ---- Feature summary ----
    print(f"\n--- Feature summary ---")
    for j, feat in enumerate(FEATURE_NAMES):
        vals = X[:, j]
        print(f"  {feat:25s}: mean={vals.mean():.4f}  std={vals.std():.4f}  "
              f"min={vals.min():.4f}  max={vals.max():.4f}")

    # ---- Separate clustering set (freq >= 2) from hapax ----
    freq_mask = X[:, 2] >= 2  # token_frequency >= 2
    n_cluster = freq_mask.sum()
    n_hapax = n - n_cluster
    print(f"\n  Clustering set: {n_cluster} MIDDLEs (freq >= 2)")
    print(f"  Hapax set: {n_hapax} MIDDLEs (freq < 2, assigned to nearest)")

    X_cluster = X[freq_mask]

    # ---- Standardize ----
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_cluster_scaled = scaler.fit_transform(X_cluster)

    # ---- Silhouette analysis for k selection ----
    from sklearn.mixture import GaussianMixture
    from sklearn.metrics import silhouette_score

    print(f"\n--- Silhouette analysis ---")
    best_sil = -1
    best_k = 6
    results_by_k = {}

    for k in range(4, 13):
        gmm = GaussianMixture(
            n_components=k, covariance_type='diag',
            n_init=5, max_iter=300, random_state=42,
        )
        labels = gmm.fit_predict(X_cluster_scaled)

        # Check for degenerate clusters
        sizes = np.bincount(labels, minlength=k)
        if sizes.min() < 3:
            print(f"  k={k:2d}: SKIPPED (degenerate cluster, min_size={sizes.min()})")
            continue

        sil = silhouette_score(X_cluster_scaled, labels)
        bic = gmm.bic(X_cluster_scaled)

        results_by_k[k] = {
            'silhouette': sil, 'bic': bic, 'sizes': sizes.tolist(),
            'labels': labels, 'gmm': gmm,
        }

        marker = ''
        if sil > best_sil:
            best_sil = sil
            best_k = k
            marker = ' ← BEST'

        print(f"  k={k:2d}: silhouette={sil:.3f}  BIC={bic:.1f}  sizes={sizes.tolist()}{marker}")

    print(f"\n  Best k by silhouette: {best_k} (sil={best_sil:.3f})")

    chosen = results_by_k[best_k]
    labels_cluster = chosen['labels']
    gmm = chosen['gmm']
    sil = chosen['silhouette']

    # ---- Assign hapax MIDDLEs to nearest cluster ----
    X_all_scaled = scaler.transform(X)
    all_labels = np.zeros(n, dtype=int)

    # Set labels for clustered MIDDLEs
    cluster_indices = np.where(freq_mask)[0]
    for idx, label in zip(cluster_indices, labels_cluster):
        all_labels[idx] = label

    # Assign hapax to nearest cluster centroid
    hapax_indices = np.where(~freq_mask)[0]
    centroids = gmm.means_  # (k, d)
    for idx in hapax_indices:
        point = X_all_scaled[idx]
        dists = np.linalg.norm(centroids - point, axis=1)
        all_labels[idx] = np.argmin(dists)

    print(f"\n  All labels assigned: {np.bincount(all_labels, minlength=best_k).tolist()}")

    # ---- Compute cluster profiles ----
    print(f"\n--- Cluster profiles ---")

    cluster_profiles = {}
    for c in range(best_k):
        mask = all_labels == c
        n_c = mask.sum()
        mean_raw = X[mask].mean(axis=0)
        std_raw = X[mask].std(axis=0)

        centroid = {FEATURE_NAMES[j]: round(float(mean_raw[j]), 4) for j in range(d)}

        # Identify distinguishing features (> 0.5 std above/below global mean)
        global_mean = X.mean(axis=0)
        global_std = X.std(axis=0)
        high_feats = []
        low_feats = []
        for j, feat in enumerate(FEATURE_NAMES):
            z = (mean_raw[j] - global_mean[j]) / max(global_std[j], 1e-6)
            if z > 0.5:
                high_feats.append((feat, round(float(z), 2)))
            elif z < -0.5:
                low_feats.append((feat, round(float(z), 2)))

        # Top 5 examples by frequency
        cluster_middles = [middles[idx] for idx in range(n) if mask[idx]]
        examples = sorted(cluster_middles,
                          key=lambda m: existing_middles[m]['token_frequency'],
                          reverse=True)[:5]

        cluster_profiles[c] = {
            'size': int(n_c),
            'centroid': centroid,
            'high_features': high_feats,
            'low_features': low_feats,
            'top_examples': examples,
        }

        print(f"\n  Bin {c} (n={n_c}):")
        print(f"    HIGH: {', '.join(f'{f}({z:+.1f}σ)' for f, z in high_feats)}")
        print(f"    LOW:  {', '.join(f'{f}({z:+.1f}σ)' for f, z in low_feats)}")
        print(f"    Top:  {examples}")

    # ---- Generate affordance labels and profiles ----
    print(f"\n--- Generating affordance labels ---")

    # Label generation: pick the single most distinctive dimension for each bin,
    # then add at most one qualifier. Keep labels SHORT and physically meaningful.

    for c in range(best_k):
        cp = cluster_profiles[c]
        cent = cp['centroid']
        high = cp['high_features']
        low = cp['low_features']

        # Combine all distinguishing features, sorted by |z|
        all_feats = [(f, abs(z), 'HIGH' if z > 0 else 'LOW', z)
                     for f, z in high + low]
        all_feats.sort(key=lambda x: -x[1])

        # Primary distinction: the single most distinguishing feature
        primary = all_feats[0] if all_feats else ('none', 0, 'NONE', 0)

        # Generate label based on cluster character
        label = 'UNDIFFERENTIATED'
        profile = ''

        # Hub connectors: very high compat_degree + token_frequency + folio_spread
        if cent['compat_degree'] > 100 and cent['folio_spread'] > 0.5:
            label = 'HUB_UNIVERSAL'
            profile = (
                "Broadly compatible universal connectors. Short, high-frequency, "
                "present in nearly all folios. Structurally central in the constraint "
                "manifold. In distillation: generic operations used across all material "
                "types and processing modes."
            )
        # h-rich: phase management
        elif cent['h_ratio'] > 0.12:
            label = 'PHASE_SENSITIVE'
            profile = (
                "h-character enriched (phase manager, C647). Deep in constraint manifold, "
                "broadly distributed. In distillation: operations sensitive to phase "
                "boundaries — foam onset, condensation transitions, boiling regime shifts. "
                "Requires monitoring for phase-change events."
            )
        # e-rich: stability critical
        elif cent['e_ratio'] > 0.20:
            label = 'STABILITY_CRITICAL'
            profile = (
                "e-character enriched (stability anchor, C647). CHSH-lane leaning, "
                "moderate depth. In distillation: operations requiring careful thermal "
                "management — substrates that degrade if overheated, sensitive fractions "
                "needing gentle handling, or emulsion-prone mixtures."
            )
        # Strong regime specialization (low entropy)
        elif cent['regime_entropy'] < 0.8:
            # Which regime dominates?
            regime_vals = {
                'R1': cent['regime_1_enrichment'],
                'R2': cent['regime_2_enrichment'],
                'R3': cent['regime_3_enrichment'],
                'R4': cent['regime_4_enrichment'],
            }
            top_regime = max(regime_vals, key=regime_vals.get)
            regime_descriptions = {
                'R1': ('ENERGY_SPECIALIZED', 'energy-intensive operations'),
                'R2': ('ROUTINE_SPECIALIZED', 'routine/frequent operations'),
                'R3': ('SETTLING_SPECIALIZED', 'stability-focused settling operations'),
                'R4': ('PRECISION_SPECIALIZED', 'precision/constrained operations'),
            }
            label, regime_desc = regime_descriptions[top_regime]
            profile = (
                f"Strongly enriched in {top_regime} ({regime_desc}). "
                f"Low regime entropy indicates these MIDDLEs appear preferentially "
                f"in specific operational contexts rather than universally. "
                f"In distillation: material-specific or method-specific operations "
                f"tied to particular processing modes."
            )
        # Short, non-compound, positional
        elif cent['length'] < 3 and cent['is_compound'] < 0.3:
            if cent['final_rate'] > 0.1:
                label = 'FLOW_TERMINAL'
                profile = (
                    "Short, atomic (non-compound), line-final biased. "
                    "In distillation: flow state markers and line-terminating "
                    "operations — endpoint indicators, fraction boundaries, "
                    "completion signals."
                )
            else:
                label = 'ATOMIC_OPERATOR'
                profile = (
                    "Short, atomic (non-compound) MIDDLEs. Core operational "
                    "primitives in the instruction grammar. In distillation: "
                    "basic operational actions — single adjustments, checks, "
                    "or simple interventions."
                )
        # Compound, terminal
        elif cent['is_compound'] > 0.7 and cent['final_rate'] > 0.08:
            label = 'COMPOUND_TERMINAL'
            profile = (
                "Compound MIDDLEs with line-final tendency. Multi-atom "
                "specifications that close control blocks. In distillation: "
                "compound instructions specifying precise endpoint conditions "
                "or completion criteria for a processing step."
            )
        # Bulk undifferentiated (catch-all for the mega-cluster)
        elif cp['size'] > 200:
            label = 'BULK_OPERATIONAL'
            profile = (
                "The undifferentiated bulk of the MIDDLE inventory. Mostly hapax "
                "or low-frequency compound MIDDLEs. No single distinguishing "
                "behavioral feature. In distillation: the long tail of specific "
                "material-parameter combinations that appear once or rarely — "
                "consistent with one-time recipe specifications."
            )
        # Moderate regime enrichment
        elif any(z > 1.5 for _, z in high if 'regime' in _):
            regime_feats = [(f, z) for f, z in high if 'regime' in f]
            if regime_feats:
                top_r = max(regime_feats, key=lambda x: x[1])
                r_num = top_r[0].split('_')[1]
                label = f'R{r_num}_ENRICHED'
                profile = (
                    f"Moderately enriched in REGIME_{r_num}. Shows operational "
                    f"preference for specific processing contexts but not exclusively. "
                    f"In distillation: operations that occur more frequently under "
                    f"certain conditions but are not forbidden elsewhere."
                )
            else:
                label = 'MODERATE_SPECIALIZED'
                profile = "Moderate regime enrichment pattern."
        else:
            label = 'MIXED_OPERATIONAL'
            profile = (
                "Mixed behavioral profile without strong single-feature dominance. "
                "In distillation: versatile operations used across multiple contexts "
                "with moderate frequency."
            )

        cp['label'] = label
        cp['profile'] = profile

        print(f"  Bin {c}: {label} (n={cp['size']})")
        print(f"    {profile[:100]}...")

    # ---- Update table ----
    print(f"\n--- Updating table ---")

    for i, mid in enumerate(middles):
        c = int(all_labels[i])
        cp = cluster_profiles[c]

        # Build behavioral signature dict
        sig = {}
        for j, feat in enumerate(FEATURE_NAMES):
            # Skip features already in base table
            if feat in ('radial_depth', 'compat_degree', 'token_frequency'):
                continue
            sig[feat] = round(float(X[i, j]), 4)

        existing_middles[mid]['behavioral_signature'] = sig
        existing_middles[mid]['affordance_bin'] = c
        existing_middles[mid]['affordance_label'] = cp['label']
        existing_middles[mid]['affordance_profile'] = cp['profile']

    # ---- Update metadata ----
    table['_metadata']['affordance_bins'] = {
        str(c): {
            'label': cp['label'],
            'size': cp['size'],
            'centroid': cp['centroid'],
            'high_features': cp['high_features'],
            'low_features': cp['low_features'],
            'top_examples': cp['top_examples'],
            'profile': cp['profile'],
        }
        for c, cp in cluster_profiles.items()
    }

    table['_metadata']['behavioral_signature_method'] = (
        f"GMM k={best_k} on {d} standardized behavioral features "
        f"(silhouette={sil:.3f}). Hapax assigned to nearest centroid."
    )
    table['_metadata']['regime_source'] = 'data/regime_folio_mapping.json (v2, GMM k=4)'
    table['_metadata']['feature_descriptions'] = {
        'length': 'MIDDLE string length',
        'k_ratio': 'Fraction of characters that are k (energy modulator, C647)',
        'e_ratio': 'Fraction of characters that are e (stability anchor, C647)',
        'h_ratio': 'Fraction of characters that are h (phase manager, C647)',
        'is_compound': 'Contains core MIDDLEs as substrings (MiddleAnalyzer)',
        'qo_affinity': 'QO lane affinity (1=QO, 0=CHSH, 0.5=neutral) from kernel composition (C647)',
        'regime_1_enrichment': 'Observed/expected ratio in REGIME_1 (energy-intensive)',
        'regime_2_enrichment': 'Observed/expected ratio in REGIME_2 (k-dominant, frequent)',
        'regime_3_enrichment': 'Observed/expected ratio in REGIME_3 (h-rich, phase management)',
        'regime_4_enrichment': 'Observed/expected ratio in REGIME_4 (e-dominant, stability)',
        'regime_entropy': 'Shannon entropy of regime distribution (low = specialized)',
        'initial_rate': 'Fraction of tokens at line-initial position',
        'final_rate': 'Fraction of tokens at line-final position',
        'folio_spread': 'Distinct folios / 82 total B folios',
    }

    # ---- Save ----
    out_path = DATA_DIR / 'middle_affordance_table.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(table, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Cross-validation with existing 5-cluster assignment ----
    print(f"\n--- Cross-validation: new bins vs old clusters ---")
    from collections import Counter
    old_clusters = [existing_middles[m]['cluster_label'] for m in middles]
    new_bins = [int(all_labels[i]) for i in range(n)]

    cross = defaultdict(Counter)
    for old, new in zip(old_clusters, new_bins):
        cross[old][new] += 1

    for old_label in sorted(set(old_clusters)):
        counts = cross[old_label]
        total = sum(counts.values())
        dist = ', '.join(f"Bin{k}:{v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])[:3])
        print(f"  {old_label:25s} (n={total:3d}): {dist}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"MIDDLE AFFORDANCE TABLE ENRICHED")
    print(f"{'=' * 70}")
    print(f"  {n} MIDDLEs with behavioral signatures")
    print(f"  {best_k} affordance bins (silhouette={sil:.3f})")
    print(f"  {n_cluster} clustered + {n_hapax} hapax assigned")
    print(f"\n  Bin summary:")
    for c in range(best_k):
        cp = cluster_profiles[c]
        print(f"    Bin {c} ({cp['label']}): n={cp['size']}")
    print(f"\n  Saved: {out_path}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
