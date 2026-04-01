"""
s6_crib_decode_freedom_probe.py — Test whether 4 decoded recipe folios land in
freedom-space positions predicted by their Pseudo-Lull recipe content.

Decoded folios:
  f75r -> Ch19 aqua vitae (gentle distillation, balneum mariae, monitoring)
  f76r -> Ch20 rectification (repeated purification cycles, iterative)
  f77v -> furnace specification (equipment description, NOT a procedure)
  f84r -> Ch30 vegetable mercury (complex multi-step, product chain)

Freedom features tested (pure FREEDOM, section-independent):
  mod_c  (adjust)     — calibration/adjustment intensity
  term_h (transparent) — open monitoring
  mod_d  (mark)       — staging/marking
  mod_s  (sequence)   — sequential ordering

Run from repo root:
    python phases/FOLIO_DESIGN_FREEDOM/scripts/s6_crib_decode_freedom_probe.py
"""

import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

# ── Configuration ──────────────────────────────────────────────────────────
DECODED_FOLIOS = {
    'f75r': 'Ch19 aqua vitae (gentle distillation, balneum mariae)',
    'f76r': 'Ch20 rectification (repeated purification cycles)',
    'f77v': 'Furnace specification (equipment, NOT procedure)',
    'f84r': 'Ch30 vegetable mercury (complex multi-step preparation)',
}
FREEDOM_FEATURES = ['mod_c', 'term_h', 'mod_d', 'mod_s']
FREEDOM_GLOSSES = {
    'mod_c': 'adjust', 'term_h': 'transparent/monitor',
    'mod_d': 'mark/stage', 'mod_s': 'sequence',
}

# All feature columns for full profile comparison
HEAD_COLS = ['head_a', 'head_e', 'head_o', 'head_k', 'head_t', 'head_headless']
MOD_COLS = ['mod_p', 'mod_f', 'mod_i', 'mod_c', 'mod_d', 'mod_s']
TERM_COLS = ['term_y', 'term_n', 'term_l', 'term_r', 'term_m', 'term_h']
PFX_COLS = ['pfx_qo', 'pfx_ch', 'pfx_sh', 'pfx_ok', 'pfx_ot', 'pfx_da',
            'pfx_ol', 'pfx_ct', 'pfx_bare']
DERIVED_COLS = ['e_depth_mean', 'i_depth_mean', 'mean_atom_length']


def main():
    # ── Load data ──────────────────────────────────────────────────────────
    features_df = pd.read_csv(
        'phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features.csv', index_col=0)

    print("=" * 80)
    print("S6: CRIB-DECODE FREEDOM PROBE")
    print("    Testing 4 decoded PL recipe folios against freedom-space predictions")
    print("=" * 80)

    # ── Verify section membership ──────────────────────────────────────────
    print("\n--- Section Verification ---")
    actual_section = None
    for folio in DECODED_FOLIOS:
        if folio not in features_df.index:
            print(f"  ERROR: {folio} not in feature matrix!")
            return
        sec = features_df.loc[folio, 'section']
        print(f"  {folio}: section={sec}")
        if actual_section is None:
            actual_section = sec
        elif sec != actual_section:
            print(f"  WARNING: mixed sections! {folio} is {sec}, expected {actual_section}")

    print(f"\n  All 4 folios are in section: {actual_section}")
    if actual_section != 'Herbal':
        print(f"  NOTE: Section is '{actual_section}', not 'Herbal'. Using '{actual_section}' as comparison group.")

    # Section peers for percentile/z-score computation
    section_df = features_df[features_df['section'] == actual_section].copy()
    n_section = len(section_df)
    print(f"  Section '{actual_section}' has {n_section} folios total")

    decoded_df = features_df.loc[list(DECODED_FOLIOS.keys())].copy()

    # ═══════════════════════════════════════════════════════════════════════
    # 1. FREEDOM FEATURE VALUES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. FREEDOM FEATURE VALUES (raw proportions)")
    print("=" * 80)
    print(f"\n  {'Folio':<8} {'mod_c':>8} {'term_h':>8} {'mod_d':>8} {'mod_s':>8}  Recipe")
    print(f"  {'':─<8} {'':─>8} {'':─>8} {'':─>8} {'':─>8}  {'':─<40}")
    for folio in DECODED_FOLIOS:
        row = features_df.loc[folio]
        print(f"  {folio:<8} {row['mod_c']:8.4f} {row['term_h']:8.4f} "
              f"{row['mod_d']:8.4f} {row['mod_s']:8.4f}  {DECODED_FOLIOS[folio][:50]}")

    # Section mean for reference
    sec_means = section_df[FREEDOM_FEATURES].mean()
    print(f"\n  {'MEAN':<8} {sec_means['mod_c']:8.4f} {sec_means['term_h']:8.4f} "
          f"{sec_means['mod_d']:8.4f} {sec_means['mod_s']:8.4f}  ({actual_section} average)")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. PERCENTILE RANKS within section
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print(f"2. PERCENTILE RANKS within {actual_section} (n={n_section})")
    print("=" * 80)

    percentiles = {}
    for folio in DECODED_FOLIOS:
        percentiles[folio] = {}
        for feat in FREEDOM_FEATURES:
            val = features_df.loc[folio, feat]
            pct = (section_df[feat] < val).sum() / n_section * 100
            percentiles[folio][feat] = round(pct, 1)

    print(f"\n  {'Folio':<8} {'mod_c':>10} {'term_h':>10} {'mod_d':>10} {'mod_s':>10}")
    for folio in DECODED_FOLIOS:
        p = percentiles[folio]
        markers = {f: '*' if p[f] >= 75 or p[f] <= 25 else '' for f in FREEDOM_FEATURES}
        print(f"  {folio:<8} {p['mod_c']:8.1f}%{markers['mod_c']:<1} "
              f"{p['term_h']:8.1f}%{markers['term_h']:<1} "
              f"{p['mod_d']:8.1f}%{markers['mod_d']:<1} "
              f"{p['mod_s']:8.1f}%{markers['mod_s']:<1}")
    print(f"\n  * = above 75th or below 25th percentile (notable)")

    # ═══════════════════════════════════════════════════════════════════════
    # 3. Z-SCORES relative to section mean
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print(f"3. Z-SCORES relative to {actual_section} mean")
    print("=" * 80)

    sec_stds = section_df[FREEDOM_FEATURES].std()
    zscores = {}
    for folio in DECODED_FOLIOS:
        zscores[folio] = {}
        for feat in FREEDOM_FEATURES:
            val = features_df.loc[folio, feat]
            z = (val - sec_means[feat]) / sec_stds[feat] if sec_stds[feat] > 0 else 0.0
            zscores[folio][feat] = round(z, 2)

    print(f"\n  {'Folio':<8} {'mod_c':>8} {'term_h':>8} {'mod_d':>8} {'mod_s':>8}")
    for folio in DECODED_FOLIOS:
        z = zscores[folio]
        print(f"  {folio:<8} {z['mod_c']:+8.2f} {z['term_h']:+8.2f} "
              f"{z['mod_d']:+8.2f} {z['mod_s']:+8.2f}")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. PREDICTION MATCHING
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("4. PREDICTION MATCHING")
    print("=" * 80)

    predictions = {}

    # f75r: expect HIGH mod_c (balneum mariae adjustment) and HIGH term_h (monitoring)
    p75 = percentiles['f75r']
    z75 = zscores['f75r']
    pred_75r = {
        'mod_c_elevated': p75['mod_c'] >= 60,
        'term_h_elevated': p75['term_h'] >= 60,
        'mod_c_pct': p75['mod_c'],
        'term_h_pct': p75['term_h'],
        'mod_c_z': z75['mod_c'],
        'term_h_z': z75['term_h'],
    }
    predictions['f75r'] = pred_75r
    match_75 = "MATCH" if pred_75r['mod_c_elevated'] or pred_75r['term_h_elevated'] else "MISS"
    print(f"\n  f75r (aqua vitae, gentle distillation, balneum mariae):")
    print(f"    Prediction: HIGH mod_c (adjustment) and/or HIGH term_h (monitoring)")
    print(f"    Result: mod_c at {p75['mod_c']:.0f}th pct (z={z75['mod_c']:+.2f}), "
          f"term_h at {p75['term_h']:.0f}th pct (z={z75['term_h']:+.2f})")
    print(f"    Verdict: {match_75}")

    # f76r: expect HIGH mod_d (staging between rectification cycles)
    p76 = percentiles['f76r']
    z76 = zscores['f76r']
    pred_76r = {
        'mod_d_elevated': p76['mod_d'] >= 60,
        'mod_s_moderate': 30 <= p76['mod_s'] <= 70,
        'mod_d_pct': p76['mod_d'],
        'mod_s_pct': p76['mod_s'],
        'mod_d_z': z76['mod_d'],
        'mod_s_z': z76['mod_s'],
    }
    predictions['f76r'] = pred_76r
    match_76 = "MATCH" if pred_76r['mod_d_elevated'] else "MISS"
    print(f"\n  f76r (rectification, repeated purification cycles):")
    print(f"    Prediction: HIGH mod_d (staging between cycles), moderate mod_s")
    print(f"    Result: mod_d at {p76['mod_d']:.0f}th pct (z={z76['mod_d']:+.2f}), "
          f"mod_s at {p76['mod_s']:.0f}th pct (z={z76['mod_s']:+.2f})")
    print(f"    Verdict: {match_76}")

    # f77v: should look DIFFERENT from the other 3 (equipment spec, not procedure)
    p77 = percentiles['f77v']
    z77 = zscores['f77v']
    # Compute Euclidean distance from each other decoded folio in freedom space
    freedom_vals = {f: [features_df.loc[f, feat] for feat in FREEDOM_FEATURES]
                    for f in DECODED_FOLIOS}
    f77v_vec = np.array(freedom_vals['f77v'])
    procedural = ['f75r', 'f76r', 'f84r']
    proc_vecs = np.array([freedom_vals[f] for f in procedural])
    proc_centroid = proc_vecs.mean(axis=0)
    dist_from_procedural = np.linalg.norm(f77v_vec - proc_centroid)

    # Also compute pairwise distances among the 3 procedural folios
    proc_dists = []
    for i in range(3):
        for j in range(i+1, 3):
            proc_dists.append(np.linalg.norm(proc_vecs[i] - proc_vecs[j]))
    mean_proc_dist = np.mean(proc_dists)

    pred_77v = {
        'dist_from_procedural': round(float(dist_from_procedural), 4),
        'mean_procedural_internal_dist': round(float(mean_proc_dist), 4),
        'is_outlier': dist_from_procedural > mean_proc_dist,
    }
    predictions['f77v'] = pred_77v
    match_77 = "MATCH" if pred_77v['is_outlier'] else "MISS"
    print(f"\n  f77v (furnace specification, equipment NOT procedure):")
    print(f"    Prediction: structurally DIFFERENT from the 3 procedure folios")
    print(f"    Result: distance from procedural centroid = {dist_from_procedural:.4f}")
    print(f"            mean internal distance among procedures = {mean_proc_dist:.4f}")
    print(f"            ratio = {dist_from_procedural/mean_proc_dist:.2f}x")
    print(f"    Verdict: {match_77}")

    # f84r: expect HIGH mod_s (sequential steps) and HIGH mod_d (staging)
    p84 = percentiles['f84r']
    z84 = zscores['f84r']
    pred_84r = {
        'mod_s_elevated': p84['mod_s'] >= 60,
        'mod_d_elevated': p84['mod_d'] >= 60,
        'mod_s_pct': p84['mod_s'],
        'mod_d_pct': p84['mod_d'],
        'mod_s_z': z84['mod_s'],
        'mod_d_z': z84['mod_d'],
    }
    predictions['f84r'] = pred_84r
    match_84 = "MATCH" if pred_84r['mod_s_elevated'] or pred_84r['mod_d_elevated'] else "MISS"
    print(f"\n  f84r (vegetable mercury, complex multi-step):")
    print(f"    Prediction: HIGH mod_s (sequence) and/or HIGH mod_d (staging)")
    print(f"    Result: mod_s at {p84['mod_s']:.0f}th pct (z={z84['mod_s']:+.2f}), "
          f"mod_d at {p84['mod_d']:.0f}th pct (z={z84['mod_d']:+.2f})")
    print(f"    Verdict: {match_84}")

    verdicts = [match_75, match_76, match_77, match_84]
    n_match = sum(1 for v in verdicts if v == "MATCH")
    print(f"\n  OVERALL: {n_match}/4 predictions match")

    # ═══════════════════════════════════════════════════════════════════════
    # 5. FREEDOM SPACE POSITIONS (PCA)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("5. FREEDOM SPACE POSITIONS (PCA on residualized features)")
    print("=" * 80)

    # Recompute PCA from residualized features (same as s3)
    res_df = pd.read_csv(
        'phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features_residualized.csv', index_col=0)

    # Drop non-numeric columns
    res_numeric = res_df.select_dtypes(include=[np.number])
    feat_cols = [c for c in res_numeric.columns if c != 'token_count']

    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    X = res_numeric[feat_cols].values
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=5)
    scores = pca.fit_transform(X_scaled)

    pc_labels = {
        0: "PC1: Yield vs Cooling",
        1: "PC2: Escape-iteration complexity",
        2: "PC3: Direct heat vs Modulated",
        3: "PC4: Infrastructure vs Cooling-state",
        4: "PC5: Operator-type selection",
    }

    # Map folio names to PC scores
    all_folios = res_df.index.tolist()
    folio_scores = {}
    for i, folio in enumerate(all_folios):
        folio_scores[folio] = scores[i]

    print(f"\n  {'Folio':<8} {'PC1':>8} {'PC2':>8} {'PC3':>8} {'PC4':>8} {'PC5':>8}")
    pca_positions = {}
    for folio in DECODED_FOLIOS:
        if folio in folio_scores:
            s = folio_scores[folio]
            print(f"  {folio:<8} {s[0]:+8.3f} {s[1]:+8.3f} {s[2]:+8.3f} "
                  f"{s[3]:+8.3f} {s[4]:+8.3f}")
            pca_positions[folio] = {f'PC{j+1}': round(float(s[j]), 4) for j in range(5)}

    # Spread analysis: pairwise distances in PC1-3 space
    decoded_scores = np.array([folio_scores[f][:3] for f in DECODED_FOLIOS])
    pairwise_pca = []
    folio_list = list(DECODED_FOLIOS.keys())
    for i in range(4):
        for j in range(i+1, 4):
            d = np.linalg.norm(decoded_scores[i] - decoded_scores[j])
            pairwise_pca.append((folio_list[i], folio_list[j], round(float(d), 3)))
    pairwise_pca.sort(key=lambda x: x[2], reverse=True)

    print(f"\n  Pairwise distances in PC1-PC3 space:")
    for f1, f2, d in pairwise_pca:
        print(f"    {f1}-{f2}: {d:.3f}")

    # Compare to average pairwise distance across ALL folios
    all_scores_3d = scores[:, :3]
    all_dists = []
    n_all = len(all_scores_3d)
    # O(n^2) but n=82, so 3321 pairs - fine
    for i in range(n_all):
        for j in range(i+1, n_all):
            all_dists.append(np.linalg.norm(all_scores_3d[i] - all_scores_3d[j]))
    mean_all_dist = np.mean(all_dists)
    mean_decoded_dist = np.mean([d for _, _, d in pairwise_pca])

    print(f"\n  Mean pairwise distance (decoded 4): {mean_decoded_dist:.3f}")
    print(f"  Mean pairwise distance (all folios): {mean_all_dist:.3f}")
    spread_ratio = mean_decoded_dist / mean_all_dist
    print(f"  Ratio: {spread_ratio:.2f}x")
    if spread_ratio > 1.2:
        print(f"  -> Decoded folios SPREAD across freedom space (diverse operations)")
    elif spread_ratio < 0.8:
        print(f"  -> Decoded folios CLUSTER in freedom space (similar operations)")
    else:
        print(f"  -> Decoded folios have TYPICAL spread")

    # ═══════════════════════════════════════════════════════════════════════
    # 6. ALL SECTION FOLIOS TABLE (with decoded highlighted)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print(f"6. ALL {actual_section.upper()} FOLIOS — FREEDOM FEATURES")
    print(f"   (* = decoded folio)")
    print("=" * 80)

    print(f"\n  {'Folio':<10} {'mod_c':>8} {'term_h':>8} {'mod_d':>8} {'mod_s':>8} {'tokens':>7}")
    print(f"  {'':─<10} {'':─>8} {'':─>8} {'':─>8} {'':─>8} {'':─>7}")

    for folio in sorted(section_df.index):
        row = section_df.loc[folio]
        marker = " *" if folio in DECODED_FOLIOS else "  "
        print(f"  {folio:<8}{marker} {row['mod_c']:8.4f} {row['term_h']:8.4f} "
              f"{row['mod_d']:8.4f} {row['mod_s']:8.4f} {row['token_count']:7.0f}")

    # Section stats
    print(f"\n  {'MEAN':<10} {sec_means['mod_c']:8.4f} {sec_means['term_h']:8.4f} "
          f"{sec_means['mod_d']:8.4f} {sec_means['mod_s']:8.4f}")
    sec_medians = section_df[FREEDOM_FEATURES].median()
    print(f"  {'MEDIAN':<10} {sec_medians['mod_c']:8.4f} {sec_medians['term_h']:8.4f} "
          f"{sec_medians['mod_d']:8.4f} {sec_medians['mod_s']:8.4f}")

    # ═══════════════════════════════════════════════════════════════════════
    # 7. E_DEPTH COMPARISON
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("7. E_DEPTH (cooling/gentle heat) COMPARISON")
    print("=" * 80)

    sec_e_mean = section_df['e_depth_mean'].mean()
    sec_e_std = section_df['e_depth_mean'].std()
    sec_i_mean = section_df['i_depth_mean'].mean()
    sec_i_std = section_df['i_depth_mean'].std()

    print(f"\n  {actual_section} e_depth: mean={sec_e_mean:.4f}, std={sec_e_std:.4f}")
    print(f"  {actual_section} i_depth: mean={sec_i_mean:.4f}, std={sec_i_std:.4f}")

    e_depth_data = {}
    print(f"\n  {'Folio':<8} {'e_depth':>8} {'e_z':>8} {'e_pct':>8} {'i_depth':>8} {'i_z':>8}  Recipe")
    for folio in DECODED_FOLIOS:
        e_val = features_df.loc[folio, 'e_depth_mean']
        i_val = features_df.loc[folio, 'i_depth_mean']
        e_z = (e_val - sec_e_mean) / sec_e_std if sec_e_std > 0 else 0
        i_z = (i_val - sec_i_mean) / sec_i_std if sec_i_std > 0 else 0
        e_pct = (section_df['e_depth_mean'] < e_val).sum() / n_section * 100
        e_depth_data[folio] = {
            'e_depth': round(float(e_val), 4),
            'e_z': round(float(e_z), 2),
            'e_pct': round(float(e_pct), 1),
            'i_depth': round(float(i_val), 4),
            'i_z': round(float(i_z), 2),
        }
        print(f"  {folio:<8} {e_val:8.4f} {e_z:+8.2f} {e_pct:7.1f}% {i_val:8.4f} {i_z:+8.2f}"
              f"  {DECODED_FOLIOS[folio][:45]}")

    print(f"\n  Predictions:")
    print(f"    f75r (balneum mariae): expect HIGH e_depth -> "
          f"{'MATCH' if e_depth_data['f75r']['e_pct'] >= 60 else 'MISS'} "
          f"({e_depth_data['f75r']['e_pct']:.0f}th pct)")
    print(f"    f77v (furnace spec):   expect DIFFERENT thermal profile -> "
          f"e_depth at {e_depth_data['f77v']['e_pct']:.0f}th pct")

    # ═══════════════════════════════════════════════════════════════════════
    # 8. FULL ATOM PROFILE COMPARISON
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("8. FULL ATOM PROFILES — side-by-side comparison")
    print("=" * 80)

    # Group by category
    categories = [
        ("HEAD atoms", HEAD_COLS),
        ("MOD atoms", MOD_COLS),
        ("TERM atoms", TERM_COLS),
        ("PREFIX distribution", PFX_COLS),
        ("DERIVED metrics", DERIVED_COLS),
    ]

    for cat_name, cols in categories:
        existing_cols = [c for c in cols if c in features_df.columns]
        if not existing_cols:
            continue
        print(f"\n  --- {cat_name} ---")
        header = f"  {'Feature':<20}"
        for folio in DECODED_FOLIOS:
            header += f" {folio:>8}"
        header += f" {'SecMean':>8}"
        print(header)

        sec_cat_means = section_df[existing_cols].mean()

        for col in existing_cols:
            row_str = f"  {col:<20}"
            vals = []
            for folio in DECODED_FOLIOS:
                v = features_df.loc[folio, col]
                vals.append(v)
                row_str += f" {v:8.4f}"
            row_str += f" {sec_cat_means[col]:8.4f}"

            # Flag if any decoded folio is notably high/low
            sec_col_std = section_df[col].std()
            sec_col_mean = sec_cat_means[col]
            flags = []
            for i, v in enumerate(vals):
                if sec_col_std > 0:
                    z = (v - sec_col_mean) / sec_col_std
                    if abs(z) > 1.5:
                        flags.append(f"{list(DECODED_FOLIOS.keys())[i]}:{z:+.1f}s")
            if flags:
                row_str += f"  [{', '.join(flags)}]"

            print(row_str)

    # ── What makes each folio operationally distinct? ──────────────────────
    print("\n  --- Distinctiveness Summary ---")
    all_profile_cols = HEAD_COLS + MOD_COLS + TERM_COLS + PFX_COLS + DERIVED_COLS
    existing_all = [c for c in all_profile_cols if c in features_df.columns]
    sec_all_means = section_df[existing_all].mean()
    sec_all_stds = section_df[existing_all].std()

    for folio, recipe in DECODED_FOLIOS.items():
        vals = features_df.loc[folio, existing_all]
        z_vals = ((vals - sec_all_means) / sec_all_stds).dropna()
        top_high = z_vals.nlargest(3)
        top_low = z_vals.nsmallest(3)
        print(f"\n  {folio} ({recipe[:50]}):")
        print(f"    Most elevated:  {', '.join(f'{c}(z={v:+.1f})' for c, v in top_high.items())}")
        print(f"    Most depressed: {', '.join(f'{c}(z={v:+.1f})' for c, v in top_low.items())}")

    # ═══════════════════════════════════════════════════════════════════════
    # STATISTICAL CAVEAT
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("STATISTICAL NOTE")
    print("=" * 80)
    print(f"  This analysis covers 4 folios — insufficient for formal hypothesis testing.")
    print(f"  Percentile ranks and z-scores are descriptive, not inferential.")
    print(f"  The predictions are directional (elevated/depressed), not point estimates.")
    print(f"  A 'MATCH' means the feature is in the predicted direction; it does not")
    print(f"  establish statistical significance. Treat as consistency check, not proof.")

    # ═══════════════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    results = {
        'decoded_folios': DECODED_FOLIOS,
        'section': actual_section,
        'n_section_folios': n_section,
        'freedom_features': FREEDOM_GLOSSES,
        'raw_values': {
            folio: {feat: round(float(features_df.loc[folio, feat]), 6)
                    for feat in FREEDOM_FEATURES}
            for folio in DECODED_FOLIOS
        },
        'section_means': {feat: round(float(sec_means[feat]), 6) for feat in FREEDOM_FEATURES},
        'percentile_ranks': percentiles,
        'z_scores': zscores,
        'predictions': {
            'f75r': {
                'prediction': 'HIGH mod_c and/or HIGH term_h',
                'verdict': match_75,
                **pred_75r,
            },
            'f76r': {
                'prediction': 'HIGH mod_d, moderate mod_s',
                'verdict': match_76,
                **pred_76r,
            },
            'f77v': {
                'prediction': 'structurally different from 3 procedure folios',
                'verdict': match_77,
                **pred_77v,
            },
            'f84r': {
                'prediction': 'HIGH mod_s and/or HIGH mod_d',
                'verdict': match_84,
                **pred_84r,
            },
        },
        'overall_match': f'{n_match}/4',
        'pca_positions': pca_positions,
        'pca_pairwise_distances': [
            {'pair': f'{f1}-{f2}', 'distance': d} for f1, f2, d in pairwise_pca
        ],
        'pca_spread': {
            'decoded_mean_dist': round(float(mean_decoded_dist), 4),
            'all_folios_mean_dist': round(float(mean_all_dist), 4),
            'ratio': round(float(spread_ratio), 3),
        },
        'e_depth': e_depth_data,
        'distinctiveness': {},
    }

    # Add distinctiveness to JSON
    for folio in DECODED_FOLIOS:
        vals = features_df.loc[folio, existing_all]
        z_vals = ((vals - sec_all_means) / sec_all_stds).dropna()
        top_high = z_vals.nlargest(3)
        top_low = z_vals.nsmallest(3)
        results['distinctiveness'][folio] = {
            'top_elevated': {c: round(float(v), 2) for c, v in top_high.items()},
            'top_depressed': {c: round(float(v), 2) for c, v in top_low.items()},
        }

    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.bool_, np.generic)):
            return obj.item()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    results = convert(results)

    out_path = 'phases/FOLIO_DESIGN_FREEDOM/results/s6_crib_decode_freedom_probe.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
