#!/usr/bin/env python3
"""
Phase 510: PARAGRAPH_PROGRAM_TYPING
Determine how many distinct paragraph program types exist in Currier B.

Extracts multi-dimensional feature vectors for each paragraph and applies
unsupervised clustering to identify structural program types.

Output: phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json
"""

import sys
import os
import json
import numpy as np
from collections import Counter, defaultdict

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.stats import chi2_contingency, f_oneway

# ============================================================
# ATOM-CATEGORY MAPPING (from C1250, C1195, C1388-C1392)
# ============================================================
# Each single-character atom maps to a primary operational category.
# These are used for plurality-vote category assignment of MIDDLEs.
ATOM_CATEGORY = {
    'k': 'THERMAL',       # C103: ENERGY_MODULATOR, kochen
    'e': 'THERMAL',       # C105: STABILITY_ANCHOR, erkalten (cooling)
    'h': 'MONITORING',    # C104: PHASE_MANAGER
    'd': 'CONTAINMENT',   # seal/make tight
    't': 'TRANSITION',    # transfer/drive
    'y': 'CONTAINMENT',   # end/close (closure family)
    'n': 'OPERATION',     # bind/connect
    'i': 'OPERATION',     # cycle/iterate
    'a': 'STAGING',       # into/intake
    'm': 'MARKING',       # batch-close marker (C1235)
    'l': 'FLOW',          # state/condition (C1385)
    'o': 'STAGING',       # arrange/ordnen (C1388)
    'r': 'FLOW',          # respond/mid (C1387)
    'c': 'MONITORING',    # main-loop modifier (C1389)
    'p': 'MARKING',       # marking/pause (C1390)
    's': 'STAGING',       # staging sequence (C1391)
    'f': 'MARKING',       # marking/flag (C1392)
    'q': 'THERMAL',       # part of qo prefix, but as atom in MIDDLE
    'g': 'OPERATION',     # rare
    'x': 'OPERATION',     # rare
}

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

# Prep PREFIXes (C933, C1221)
PREP_PREFIXES = {'pch', 'tch', 'dch', 'lch', 'te'}

# Terminal suffixes indicating Mode A (specification mode)
# From C1229, C1236: -edy, -dy, -ey, -eey, -y (terminal suffixes)
MODE_A_SUFFIXES = {'edy', 'dy', 'ey', 'eey', 'y', 'hy', 'ly', 'ry',
                   'chy', 'shy', 'ky', 'oky', 'oty'}


def assign_category(middle):
    """Assign operational category to a MIDDLE via atom plurality vote."""
    if not middle:
        return None
    votes = Counter()
    for ch in middle:
        cat = ATOM_CATEGORY.get(ch)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    return votes.most_common(1)[0][0]


def is_headless(middle):
    """Check if compound MIDDLE is headless (initial atom not in {a,e,o,k,t})."""
    if not middle or len(middle) < 2:
        return False
    return middle[0] not in {'a', 'e', 'o', 'k', 't'}


def get_suffix_mode(suffix, middle):
    """Determine suffix mode: A (terminal/specification) vs B (bare/continuation)."""
    if suffix and suffix in MODE_A_SUFFIXES:
        return 'A'
    if suffix:
        # Other suffixes like -aiin, -ain, -al, -ar, -or, -ol are checkpoint/mixed
        return 'A'
    # No suffix = bare = Mode B
    return 'B'


def main():
    print("=" * 70)
    print("Phase 510: PARAGRAPH_PROGRAM_TYPING")
    print("=" * 70)

    # Load data
    tx = Transcript()
    morph = Morphology()
    tokens = list(tx.currier_b())
    print(f"Total Currier B tokens: {len(tokens)}")

    # Load REGIME mapping
    regime_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                               'data', 'regime_folio_mapping.json')
    with open(regime_path) as f:
        regime_data = json.load(f)
    regime_map = {k: v['regime'] for k, v in
                  regime_data['regime_assignments'].items()}

    # ============================================================
    # STEP 1: Build paragraphs from par_initial markers
    # ============================================================
    # Group tokens by folio, then split into paragraphs at par_initial markers
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t.folio].append(t)

    # Sort within each folio by line number
    for folio in folio_tokens:
        folio_tokens[folio].sort(key=lambda t: (t.line, 0))

    paragraphs = []  # list of dicts with folio, par_idx, tokens, lines
    for folio, toks in sorted(folio_tokens.items()):
        par_idx = 0
        current_par = []
        for t in toks:
            if t.par_initial and current_par:
                # End previous paragraph, start new one
                paragraphs.append({
                    'folio': folio,
                    'par_idx': par_idx,
                    'tokens': current_par,
                    'section': current_par[0].section,
                })
                par_idx += 1
                current_par = [t]
            else:
                current_par.append(t)
        # Last paragraph in folio
        if current_par:
            paragraphs.append({
                'folio': folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0].section,
            })

    print(f"Total paragraphs found: {len(paragraphs)}")

    # Count lines per paragraph
    for par in paragraphs:
        lines = set(t.line for t in par['tokens'])
        par['n_lines'] = len(lines)
        par['lines'] = sorted(lines)
        # Body lines = all lines except the first (header)
        par['body_lines'] = len(lines) - 1 if len(lines) > 1 else 0

    # Filter: only paragraphs with 3+ body lines
    MIN_BODY_LINES = 3
    filtered_pars = [p for p in paragraphs if p['body_lines'] >= MIN_BODY_LINES]
    print(f"Paragraphs with {MIN_BODY_LINES}+ body lines: {len(filtered_pars)}")
    print(f"  (excluded {len(paragraphs) - len(filtered_pars)} short paragraphs)")

    # ============================================================
    # STEP 2: Feature extraction
    # ============================================================
    print("\nExtracting features...")

    feature_names = (
        CATEGORIES +                    # 8 category fractions
        ['headless_frac',               # 1
         'mode_a_frac',                 # 1 suffix mode balance
         'prep_prefix_frac',            # 1
         'k_kernel', 'e_kernel', 'h_kernel',  # 3 kernel profile
         'body_line_count',             # 1
         'mean_middle_len',             # 1
         'headless_d_frac', 'headless_i_frac', 'headless_c_frac',  # 3
         'qo_frac', 'chsh_frac', 'bare_frac',  # 3 PREFIX channels
         'dy_frac',                     # 1
         ]
    )
    print(f"Feature dimensions: {len(feature_names)}")

    feature_matrix = []
    par_metadata = []  # Keep track of paragraph identity

    for par in filtered_pars:
        toks = par['tokens']
        n = len(toks)
        if n == 0:
            continue

        # Extract morphology for all tokens
        morphs = []
        for t in toks:
            w = t.word.strip()
            if not w or '*' in w:
                continue
            try:
                m = morph.extract(w)
                morphs.append(m)
            except Exception:
                continue

        if len(morphs) < 5:  # Need minimum tokens for meaningful features
            continue

        n_m = len(morphs)

        # --- Category profile (8 features) ---
        cat_counts = Counter()
        for m in morphs:
            cat = assign_category(m.middle)
            if cat:
                cat_counts[cat] += 1
        cat_total = sum(cat_counts.values()) or 1
        cat_fracs = [cat_counts.get(c, 0) / cat_total for c in CATEGORIES]

        # --- Headless fraction ---
        compounds = [m for m in morphs if m.middle and len(m.middle) >= 2]
        n_headless = sum(1 for m in compounds if is_headless(m.middle))
        headless_frac = n_headless / len(compounds) if compounds else 0.0

        # --- Suffix mode balance ---
        mode_a_count = 0
        for m in morphs:
            if get_suffix_mode(m.suffix, m.middle) == 'A':
                mode_a_count += 1
        mode_a_frac = mode_a_count / n_m

        # --- Prep PREFIX fraction ---
        prep_count = sum(1 for m in morphs if m.prefix and m.prefix in PREP_PREFIXES)
        prep_frac = prep_count / n_m

        # --- Kernel profile (k, e, h fractions) ---
        k_count = sum(1 for m in morphs if m.middle and 'k' in m.middle)
        e_count = sum(1 for m in morphs if m.middle and 'e' in m.middle)
        h_count = sum(1 for m in morphs if m.middle and 'h' in m.middle)
        k_frac = k_count / n_m
        e_frac = e_count / n_m
        h_frac = h_count / n_m

        # --- Body line count ---
        body_lines = par['body_lines']

        # --- Mean MIDDLE length ---
        mid_lens = [len(m.middle) for m in morphs if m.middle]
        mean_mid_len = np.mean(mid_lens) if mid_lens else 0.0

        # --- Headless initial atom profile ---
        headless_tokens = [m for m in compounds if is_headless(m.middle)]
        n_hl = len(headless_tokens) or 1
        hl_d = sum(1 for m in headless_tokens if m.middle[0] == 'd') / n_hl if headless_tokens else 0.0
        hl_i = sum(1 for m in headless_tokens if m.middle[0] == 'i') / n_hl if headless_tokens else 0.0
        hl_c = sum(1 for m in headless_tokens if m.middle[0] == 'c') / n_hl if headless_tokens else 0.0

        # --- PREFIX channel balance ---
        qo_count = sum(1 for m in morphs if m.prefix and m.prefix.startswith('qo'))
        chsh_count = sum(1 for m in morphs if m.prefix and
                         (m.prefix.startswith('ch') or m.prefix.startswith('sh')))
        bare_count = sum(1 for m in morphs if not m.prefix)
        qo_frac = qo_count / n_m
        chsh_frac = chsh_count / n_m
        bare_frac = bare_count / n_m

        # --- dy fraction ---
        dy_count = sum(1 for m in morphs if m.middle == 'dy')
        dy_frac = dy_count / n_m

        # Assemble feature vector
        fv = (cat_fracs +
              [headless_frac, mode_a_frac, prep_frac,
               k_frac, e_frac, h_frac,
               body_lines, mean_mid_len,
               hl_d, hl_i, hl_c,
               qo_frac, chsh_frac, bare_frac,
               dy_frac])

        feature_matrix.append(fv)
        par_metadata.append({
            'folio': par['folio'],
            'par_idx': par['par_idx'],
            'section': par['section'],
            'n_tokens': n_m,
            'n_lines': par['n_lines'],
            'body_lines': body_lines,
            'regime': regime_map.get(par['folio'], 'UNKNOWN'),
        })

    X = np.array(feature_matrix)
    print(f"Feature matrix shape: {X.shape}")
    print(f"Paragraphs in analysis: {X.shape[0]}")

    # Section distribution of analyzed paragraphs
    sec_dist = Counter(m['section'] for m in par_metadata)
    print(f"Section distribution: {dict(sec_dist)}")

    # ============================================================
    # STEP 3: Standardize features
    # ============================================================
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ============================================================
    # T1: Unsupervised Clustering
    # ============================================================
    print("\n" + "=" * 70)
    print("T1: UNSUPERVISED CLUSTERING")
    print("=" * 70)

    k_range = list(range(2, 9))
    silhouettes = {}
    inertias = {}
    best_k = None
    best_sil = -1

    for k in k_range:
        km = KMeans(n_clusters=k, n_init=50, random_state=42, max_iter=500)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        silhouettes[k] = sil
        inertias[k] = float(km.inertia_)
        sizes = Counter(labels)
        print(f"  k={k}: silhouette={sil:.4f}, inertia={km.inertia_:.1f}, "
              f"sizes={dict(sorted(sizes.items()))}")
        if sil > best_sil:
            best_sil = sil
            best_k = k

    print(f"\nBest k={best_k} with silhouette={best_sil:.4f}")

    # Fit best model
    km_best = KMeans(n_clusters=best_k, n_init=100, random_state=42, max_iter=500)
    best_labels = km_best.fit_predict(X_scaled)

    # Cluster centroids (in original feature space)
    centroids_scaled = km_best.cluster_centers_
    centroids_original = scaler.inverse_transform(centroids_scaled)

    cluster_sizes = Counter(best_labels)
    print(f"\nCluster sizes: {dict(sorted(cluster_sizes.items()))}")

    # Report centroids
    print(f"\nCluster centroids (original feature space):")
    for ci in range(best_k):
        print(f"\n  Cluster {ci} (n={cluster_sizes[ci]}):")
        for fi, fn in enumerate(feature_names):
            print(f"    {fn:25s}: {centroids_original[ci, fi]:.4f}")

    # ============================================================
    # T2: Cluster Interpretation
    # ============================================================
    print("\n" + "=" * 70)
    print("T2: CLUSTER INTERPRETATION")
    print("=" * 70)

    overall_means = X.mean(axis=0)
    overall_stds = X.std(axis=0)
    overall_stds[overall_stds == 0] = 1  # avoid division by zero

    cluster_descriptions = {}
    for ci in range(best_k):
        mask = best_labels == ci
        cluster_mean = X[mask].mean(axis=0)
        z_scores = (cluster_mean - overall_means) / overall_stds

        # Rank by absolute z-score
        ranked = sorted(enumerate(z_scores), key=lambda x: abs(x[1]), reverse=True)
        top3 = [(feature_names[idx], float(z)) for idx, z in ranked[:3]]
        enriched = [(feature_names[idx], float(z)) for idx, z in ranked if z > 0.5][:5]
        depleted = [(feature_names[idx], float(z)) for idx, z in ranked if z < -0.5][:5]

        desc = {
            'size': int(cluster_sizes[ci]),
            'top_3_discriminators': top3,
            'enriched': enriched,
            'depleted': depleted,
        }
        cluster_descriptions[ci] = desc

        print(f"\n  Cluster {ci} (n={cluster_sizes[ci]}):")
        print(f"    Top 3 discriminating features:")
        for fn, z in top3:
            direction = "HIGH" if z > 0 else "LOW"
            print(f"      {fn:25s}: z={z:+.3f} ({direction})")
        if enriched:
            print(f"    Enriched (z>0.5):")
            for fn, z in enriched:
                print(f"      {fn:25s}: z={z:+.3f}")
        if depleted:
            print(f"    Depleted (z<-0.5):")
            for fn, z in depleted:
                print(f"      {fn:25s}: z={z:+.3f}")

    # ============================================================
    # T3: Section Correspondence
    # ============================================================
    print("\n" + "=" * 70)
    print("T3: SECTION CORRESPONDENCE")
    print("=" * 70)

    # Map sections to interpretable names
    SECTION_NAMES = {
        'H': 'HERBAL', 'B': 'BIO', 'S': 'STARS_RECIPE',
        'C': 'COSMO', 'T': 'PHARMA'
    }

    sections = [SECTION_NAMES.get(par_metadata[i]['section'],
                                   par_metadata[i]['section'])
                for i in range(len(par_metadata))]
    unique_sections = sorted(set(sections))
    unique_clusters = list(range(best_k))

    # Build contingency table
    ct_section = np.zeros((len(unique_sections), best_k), dtype=int)
    for i in range(len(par_metadata)):
        si = unique_sections.index(sections[i])
        ct_section[si, best_labels[i]] += 1

    print(f"\n  Contingency table (Section x Cluster):")
    header = f"  {'Section':20s}" + "".join(f"  C{c}" for c in unique_clusters) + "  Total"
    print(header)
    for si, sec in enumerate(unique_sections):
        row = f"  {sec:20s}" + "".join(f"  {ct_section[si, c]:3d}" for c in unique_clusters)
        row += f"  {ct_section[si].sum():4d}"
        print(row)

    # Chi-squared test
    chi2, p_sec, dof, expected = chi2_contingency(ct_section)
    v_sec = np.sqrt(chi2 / (ct_section.sum() * (min(ct_section.shape) - 1)))
    print(f"\n  Chi-squared = {chi2:.2f}, p = {p_sec:.2e}, dof = {dof}")
    print(f"  Cramer's V = {v_sec:.4f}")
    if p_sec < 0.001:
        print("  => STRONG section-cluster correspondence")
    elif p_sec < 0.05:
        print("  => Significant section-cluster correspondence")
    else:
        print("  => No significant section-cluster correspondence")

    # ============================================================
    # T4: REGIME Correspondence
    # ============================================================
    print("\n" + "=" * 70)
    print("T4: REGIME CORRESPONDENCE")
    print("=" * 70)

    regimes = [par_metadata[i]['regime'] for i in range(len(par_metadata))]
    unique_regimes = sorted(set(regimes))

    ct_regime = np.zeros((len(unique_regimes), best_k), dtype=int)
    for i in range(len(par_metadata)):
        ri = unique_regimes.index(regimes[i])
        ct_regime[ri, best_labels[i]] += 1

    print(f"\n  Contingency table (REGIME x Cluster):")
    header = f"  {'REGIME':20s}" + "".join(f"  C{c}" for c in unique_clusters) + "  Total"
    print(header)
    for ri, reg in enumerate(unique_regimes):
        row = f"  {reg:20s}" + "".join(f"  {ct_regime[ri, c]:3d}" for c in unique_clusters)
        row += f"  {ct_regime[ri].sum():4d}"
        print(row)

    # Filter out UNKNOWN regime if present
    known_mask = np.array([r != 'UNKNOWN' for r in regimes])
    if not all(known_mask):
        ct_regime_known = ct_regime[[i for i, r in enumerate(unique_regimes) if r != 'UNKNOWN']]
        if ct_regime_known.shape[0] >= 2:
            chi2_r, p_reg, dof_r, _ = chi2_contingency(ct_regime_known)
            v_reg = np.sqrt(chi2_r / (ct_regime_known.sum() * (min(ct_regime_known.shape) - 1)))
        else:
            chi2_r, p_reg, dof_r, v_reg = 0, 1.0, 0, 0
    else:
        chi2_r, p_reg, dof_r, _ = chi2_contingency(ct_regime)
        v_reg = np.sqrt(chi2_r / (ct_regime.sum() * (min(ct_regime.shape) - 1)))

    print(f"\n  Chi-squared = {chi2_r:.2f}, p = {p_reg:.2e}, dof = {dof_r}")
    print(f"  Cramer's V = {v_reg:.4f}")
    if p_reg < 0.001:
        print("  => STRONG REGIME-cluster correspondence")
    elif p_reg < 0.05:
        print("  => Significant REGIME-cluster correspondence")
    else:
        print("  => No significant REGIME-cluster correspondence")

    # ============================================================
    # T5: Folio Distribution
    # ============================================================
    print("\n" + "=" * 70)
    print("T5: FOLIO DISTRIBUTION")
    print("=" * 70)

    folio_clusters = defaultdict(set)
    folio_par_counts = defaultdict(int)
    for i in range(len(par_metadata)):
        f = par_metadata[i]['folio']
        folio_clusters[f].add(int(best_labels[i]))
        folio_par_counts[f] += 1

    clusters_per_folio = [len(v) for v in folio_clusters.values()]
    mean_cpf = np.mean(clusters_per_folio)
    multi_type_folios = sum(1 for c in clusters_per_folio if c >= 2)
    total_folios = len(folio_clusters)

    print(f"  Total folios with analyzed paragraphs: {total_folios}")
    print(f"  Mean clusters per folio: {mean_cpf:.2f}")
    print(f"  Folios with 2+ cluster types: {multi_type_folios}/{total_folios} "
          f"({100*multi_type_folios/total_folios:.1f}%)")
    print(f"  Mono-type folios: {total_folios - multi_type_folios}/{total_folios} "
          f"({100*(total_folios-multi_type_folios)/total_folios:.1f}%)")

    # Distribution of cluster counts per folio
    cpf_dist = Counter(clusters_per_folio)
    print(f"  Distribution of clusters per folio:")
    for nc in sorted(cpf_dist.keys()):
        print(f"    {nc} cluster type(s): {cpf_dist[nc]} folios")

    # Show some examples
    print(f"\n  Multi-type folio examples:")
    for f in sorted(folio_clusters.keys()):
        if len(folio_clusters[f]) >= 2:
            print(f"    {f}: clusters {sorted(folio_clusters[f])}, "
                  f"{folio_par_counts[f]} paragraphs")
            if sum(1 for ff in sorted(folio_clusters.keys()) if len(folio_clusters[ff]) >= 2) > 15:
                break

    # ============================================================
    # T6: Feature Importance
    # ============================================================
    print("\n" + "=" * 70)
    print("T6: FEATURE IMPORTANCE")
    print("=" * 70)

    # Between-cluster variance / total variance for each feature
    total_var = X_scaled.var(axis=0)
    between_var = np.zeros(X_scaled.shape[1])
    overall_mean_s = X_scaled.mean(axis=0)
    for ci in range(best_k):
        mask = best_labels == ci
        ni = mask.sum()
        cluster_mean_s = X_scaled[mask].mean(axis=0)
        between_var += ni * (cluster_mean_s - overall_mean_s) ** 2
    between_var /= len(X_scaled)
    total_var[total_var == 0] = 1
    importance = between_var / total_var

    # Rank
    ranked_features = sorted(zip(feature_names, importance),
                             key=lambda x: x[1], reverse=True)
    print(f"\n  Feature importance (between-cluster / total variance):")
    for fn, imp in ranked_features:
        bar = '#' * int(imp * 50)
        print(f"    {fn:25s}: {imp:.4f}  {bar}")

    # ============================================================
    # T7: Stability Check
    # ============================================================
    print("\n" + "=" * 70)
    print("T7: STABILITY CHECK (100 runs)")
    print("=" * 70)

    n_stability_runs = 100
    all_labels = []
    for seed in range(n_stability_runs):
        km_s = KMeans(n_clusters=best_k, n_init=10, random_state=seed, max_iter=500)
        labels_s = km_s.fit_predict(X_scaled)
        all_labels.append(labels_s)

    # Compute pairwise ARI
    ari_values = []
    for i in range(0, n_stability_runs, 5):  # Sample pairs for efficiency
        for j in range(i + 1, min(i + 6, n_stability_runs)):
            ari = adjusted_rand_score(all_labels[i], all_labels[j])
            ari_values.append(ari)

    mean_ari = np.mean(ari_values)
    std_ari = np.std(ari_values)
    min_ari = np.min(ari_values)
    max_ari = np.max(ari_values)

    print(f"  Mean ARI: {mean_ari:.4f} +/- {std_ari:.4f}")
    print(f"  Range: [{min_ari:.4f}, {max_ari:.4f}]")
    if mean_ari > 0.8:
        print("  => HIGHLY STABLE clustering")
    elif mean_ari > 0.5:
        print("  => MODERATELY STABLE clustering")
    else:
        print("  => UNSTABLE clustering (sensitive to initialization)")

    # ============================================================
    # T8: Paragraph Length Association
    # ============================================================
    print("\n" + "=" * 70)
    print("T8: PARAGRAPH LENGTH ASSOCIATION")
    print("=" * 70)

    body_lengths = np.array([par_metadata[i]['body_lines']
                             for i in range(len(par_metadata))])

    groups = [body_lengths[best_labels == ci] for ci in range(best_k)]
    for ci in range(best_k):
        g = groups[ci]
        print(f"  Cluster {ci}: mean={g.mean():.2f}, "
              f"median={np.median(g):.1f}, std={g.std():.2f}, "
              f"range=[{g.min()}, {g.max()}]")

    if best_k >= 2 and all(len(g) >= 2 for g in groups):
        f_stat, p_anova = f_oneway(*groups)
        eta_sq = (f_stat * (best_k - 1)) / (f_stat * (best_k - 1) + len(body_lengths) - best_k)
        print(f"\n  ANOVA F = {f_stat:.2f}, p = {p_anova:.2e}")
        print(f"  Eta-squared = {eta_sq:.4f}")
        if p_anova < 0.001:
            print("  => STRONG length differentiation across clusters")
        elif p_anova < 0.05:
            print("  => Significant length differentiation")
        else:
            print("  => No significant length differentiation")
    else:
        f_stat, p_anova, eta_sq = 0, 1.0, 0

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Paragraphs analyzed: {X.shape[0]} (with {MIN_BODY_LINES}+ body lines)")
    print(f"  Feature dimensions: {len(feature_names)}")
    print(f"  Best k: {best_k} (silhouette={best_sil:.4f})")
    print(f"  Stability: ARI={mean_ari:.4f}")
    print(f"  Section correspondence: chi2={chi2:.2f}, V={v_sec:.4f}, p={p_sec:.2e}")
    print(f"  REGIME correspondence: chi2={chi2_r:.2f}, V={v_reg:.4f}, p={p_reg:.2e}")
    print(f"  Multi-type folios: {multi_type_folios}/{total_folios} ({100*multi_type_folios/total_folios:.1f}%)")
    print(f"  Length association: F={f_stat:.2f}, eta2={eta_sq:.4f}, p={p_anova:.2e}")

    # Interpretation
    if best_sil < 0.25:
        print(f"\n  INTERPRETATION: Weak clustering (sil={best_sil:.3f} < 0.25).")
        print(f"  Paragraph programs form a CONTINUOUS variation space,")
        print(f"  not discrete types. {best_k} clusters represent gradient")
        print(f"  zones along a continuum, not distinct program types.")
    elif best_sil < 0.50:
        print(f"\n  INTERPRETATION: Moderate clustering (sil={best_sil:.3f}).")
        print(f"  {best_k} program types are distinguishable but overlapping.")
    else:
        print(f"\n  INTERPRETATION: Strong clustering (sil={best_sil:.3f}).")
        print(f"  {best_k} distinct program types identified.")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    results = {
        'metadata': {
            'phase': 'PARAGRAPH_PROGRAM_TYPING (Phase 510)',
            'total_paragraphs': len(paragraphs),
            'analyzed_paragraphs': int(X.shape[0]),
            'min_body_lines': MIN_BODY_LINES,
            'feature_count': len(feature_names),
            'feature_names': feature_names,
        },
        'T1_clustering': {
            'silhouette_scores': {str(k): float(v) for k, v in silhouettes.items()},
            'inertias': {str(k): float(v) for k, v in inertias.items()},
            'best_k': best_k,
            'best_silhouette': float(best_sil),
            'cluster_sizes': {str(k): int(v) for k, v in sorted(cluster_sizes.items())},
            'centroids': {
                str(ci): {fn: float(centroids_original[ci, fi])
                          for fi, fn in enumerate(feature_names)}
                for ci in range(best_k)
            },
        },
        'T2_interpretation': {
            str(ci): {
                'size': cluster_descriptions[ci]['size'],
                'top_3_discriminators': [
                    {'feature': fn, 'z_score': float(z)}
                    for fn, z in cluster_descriptions[ci]['top_3_discriminators']
                ],
                'enriched': [
                    {'feature': fn, 'z_score': float(z)}
                    for fn, z in cluster_descriptions[ci]['enriched']
                ],
                'depleted': [
                    {'feature': fn, 'z_score': float(z)}
                    for fn, z in cluster_descriptions[ci]['depleted']
                ],
            }
            for ci in range(best_k)
        },
        'T3_section': {
            'contingency': {
                sec: {str(ci): int(ct_section[si, ci]) for ci in range(best_k)}
                for si, sec in enumerate(unique_sections)
            },
            'chi_squared': float(chi2),
            'p_value': float(p_sec),
            'dof': int(dof),
            'cramers_v': float(v_sec),
        },
        'T4_regime': {
            'contingency': {
                reg: {str(ci): int(ct_regime[ri, ci]) for ci in range(best_k)}
                for ri, reg in enumerate(unique_regimes)
            },
            'chi_squared': float(chi2_r),
            'p_value': float(p_reg),
            'cramers_v': float(v_reg),
        },
        'T5_folio': {
            'total_folios': total_folios,
            'mean_clusters_per_folio': float(mean_cpf),
            'multi_type_folios': multi_type_folios,
            'multi_type_fraction': float(multi_type_folios / total_folios),
            'clusters_per_folio_distribution': {
                str(k): int(v) for k, v in sorted(cpf_dist.items())
            },
        },
        'T6_feature_importance': {
            fn: float(imp) for fn, imp in ranked_features
        },
        'T7_stability': {
            'n_runs': n_stability_runs,
            'mean_ari': float(mean_ari),
            'std_ari': float(std_ari),
            'min_ari': float(min_ari),
            'max_ari': float(max_ari),
        },
        'T8_length': {
            'cluster_stats': {
                str(ci): {
                    'mean': float(groups[ci].mean()),
                    'median': float(np.median(groups[ci])),
                    'std': float(groups[ci].std()),
                    'min': int(groups[ci].min()),
                    'max': int(groups[ci].max()),
                }
                for ci in range(best_k)
            },
            'anova_f': float(f_stat),
            'anova_p': float(p_anova),
            'eta_squared': float(eta_sq),
        },
        'paragraph_labels': [
            {
                'folio': par_metadata[i]['folio'],
                'par_idx': par_metadata[i]['par_idx'],
                'section': par_metadata[i]['section'],
                'regime': par_metadata[i]['regime'],
                'cluster': int(best_labels[i]),
                'body_lines': par_metadata[i]['body_lines'],
                'n_tokens': par_metadata[i]['n_tokens'],
            }
            for i in range(len(par_metadata))
        ],
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                            'paragraph_program_typing.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
