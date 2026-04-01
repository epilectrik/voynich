"""
s4_regime_atom_interaction.py
Test whether REGIME classification is decomposable to specific atom choices
or operates above atom level.

REGIME is defined by k_ratio quartiles (head_k column).
"""
import sys, os, json, warnings
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score, confusion_matrix
from scipy import stats as sp_stats

# ── Load data ───────────────────────────────────────────────────────────
features_df = pd.read_csv(
    'phases/FOLIO_DESIGN_FREEDOM/results/s1_folio_atom_features.csv', index_col=0
)

print(f"Loaded {len(features_df)} folios, {len(features_df.columns)} columns")
print(f"Sections: {features_df['section'].value_counts().to_dict()}")

# ── REGIME assignment via k_ratio quartiles ─────────────────────────────
features_df['REGIME'] = pd.qcut(
    features_df['head_k'], q=4, labels=['R1_lowK', 'R2', 'R3', 'R4_highK']
)
regime_counts = features_df['REGIME'].value_counts().sort_index()
print(f"\nREGIME counts (k quartiles):")
for r, c in regime_counts.items():
    print(f"  {r}: {c}")

# Feature columns (exclude token_count, section, REGIME)
atom_features = [c for c in features_df.columns
                 if c not in ('token_count', 'section', 'REGIME')]
print(f"\nAtom features for analysis: {len(atom_features)}")

results = {}

# ════════════════════════════════════════════════════════════════════════
# 1. Random Forest REGIME prediction (LOO-CV)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("1. RANDOM FOREST REGIME PREDICTION (LOO-CV)")
print("="*70)
print(f"   N={len(features_df)}, features={len(atom_features)}, classes=4")
print("   WARNING: N=82 with 30 features -- high overfitting risk.")
print("   LOO-CV gives honest out-of-sample estimate.")

X = features_df[atom_features].values
y = features_df['REGIME'].astype(str).values

loo = LeaveOneOut()
y_pred = np.empty(len(y), dtype=object)

for train_idx, test_idx in loo.split(X):
    rf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42, n_jobs=-1)
    rf.fit(X[train_idx], y[train_idx])
    y_pred[test_idx] = rf.predict(X[test_idx])

loo_accuracy = accuracy_score(y, y_pred)
cm = confusion_matrix(y, y_pred, labels=['R1_lowK', 'R2', 'R3', 'R4_highK'])

print(f"\n   LOO-CV Accuracy: {loo_accuracy:.4f}")
print(f"\n   Confusion matrix (rows=true, cols=pred):")
labels_short = ['R1', 'R2', 'R3', 'R4']
print(f"   {'':>6} {labels_short[0]:>6} {labels_short[1]:>6} {labels_short[2]:>6} {labels_short[3]:>6}")
for i, row in enumerate(cm):
    print(f"   {labels_short[i]:>6} {row[0]:>6} {row[1]:>6} {row[2]:>6} {row[3]:>6}")

# Permutation baseline
n_perm = 100
perm_accs = []
rng = np.random.RandomState(42)
for p in range(n_perm):
    y_shuf = rng.permutation(y)
    y_pred_shuf = np.empty(len(y), dtype=object)
    for train_idx, test_idx in loo.split(X):
        rf = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42, n_jobs=-1)
        rf.fit(X[train_idx], y_shuf[train_idx])
        y_pred_shuf[test_idx] = rf.predict(X[test_idx])
    perm_accs.append(accuracy_score(y_shuf, y_pred_shuf))
    if (p + 1) % 20 == 0:
        print(f"     Permutation {p+1}/{n_perm} done...")

perm_mean = np.mean(perm_accs)
perm_std = np.std(perm_accs)
p_value = np.mean([a >= loo_accuracy for a in perm_accs])

print(f"\n   Permutation baseline (100 shuffles):")
print(f"     Mean accuracy: {perm_mean:.4f} +/- {perm_std:.4f}")
print(f"     p-value (perm >= real): {p_value:.4f}")
print(f"     Lift over chance: {loo_accuracy - perm_mean:+.4f}")

# Feature importance from full model
rf_full = RandomForestClassifier(n_estimators=500, max_depth=3, random_state=42)
rf_full.fit(X, y)
importances = pd.Series(rf_full.feature_importances_, index=atom_features).sort_values(ascending=False)
print(f"\n   Top 10 feature importances (full model):")
for feat, imp in importances.head(10).items():
    print(f"     {feat:>20s}: {imp:.4f}")

results['rf_loo'] = {
    'accuracy': float(loo_accuracy),
    'confusion_matrix': cm.tolist(),
    'perm_mean_accuracy': float(perm_mean),
    'perm_std': float(perm_std),
    'p_value': float(p_value),
    'top_importances': {k: float(v) for k, v in importances.head(10).items()},
    'n_folios': len(features_df),
    'n_features': len(atom_features),
    'overfitting_warning': 'N=82, 30 features, 4 classes -- LOO-CV is honest but RF may still capture noise'
}

# ════════════════════════════════════════════════════════════════════════
# 2. Per-atom REGIME effect (one-way ANOVA + within-Herbal partial)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("2. PER-ATOM REGIME EFFECT (one-way ANOVA eta-squared)")
print("="*70)


def eta_squared_oneway(values_by_group):
    """Compute eta-squared from one-way ANOVA groups."""
    groups = [np.array(g, dtype=float) for g in values_by_group if len(g) > 0]
    if len(groups) < 2:
        return 0.0, 1.0
    f_stat, p_val = sp_stats.f_oneway(*groups)
    if np.isnan(f_stat):
        return 0.0, 1.0
    # eta-squared = SS_between / SS_total
    grand_mean = np.concatenate(groups).mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
    ss_total = sum(np.sum((g - grand_mean)**2) for g in groups)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0.0
    return float(eta_sq), float(p_val)


# Identify the largest section for within-section analysis
section_sizes = features_df['section'].value_counts()
largest_section = section_sizes.index[0]
print(f"   Largest section: {largest_section} (n={section_sizes.iloc[0]})")
herbal_df = features_df[features_df['section'] == largest_section]
print(f"   REGIME distribution in {largest_section}:")
for r, c in herbal_df['REGIME'].value_counts().sort_index().items():
    print(f"     {r}: {c}")

# Load s2 for section eta-squared reference
s2_data = json.load(open('phases/FOLIO_DESIGN_FREEDOM/results/s2_freedom_constraint_partition.json'))

anova_results = {}
regime_labels = sorted(features_df['REGIME'].unique())

for feat in atom_features:
    # Overall REGIME eta-squared (one-way ANOVA, all folios)
    groups_regime = [features_df.loc[features_df['REGIME'] == r, feat].dropna().values
                     for r in regime_labels]
    regime_eta, regime_p = eta_squared_oneway(groups_regime)

    # Section eta-squared from s2 (already computed)
    section_eta = s2_data['features'].get(feat, {}).get('eta_sq', None)

    # Within-Herbal REGIME effect (partial, avoids section confounding)
    herbal_groups = [herbal_df.loc[herbal_df['REGIME'] == r, feat].dropna().values
                     for r in regime_labels]
    # Only compute if at least 2 groups have data
    nonempty = [g for g in herbal_groups if len(g) > 0]
    if len(nonempty) >= 2:
        herbal_regime_eta, herbal_regime_p = eta_squared_oneway(herbal_groups)
    else:
        herbal_regime_eta, herbal_regime_p = None, None

    anova_results[feat] = {
        'regime_eta_sq': regime_eta,
        'regime_p': regime_p,
        'section_eta_sq': section_eta,
        'herbal_regime_eta_sq': herbal_regime_eta,
        'herbal_regime_p': herbal_regime_p
    }

# Sort by REGIME eta-squared
sorted_by_regime = sorted(
    anova_results.items(),
    key=lambda x: x[1]['regime_eta_sq'], reverse=True
)

print(f"\n   {'Feature':>20s}  {'Sect eta2':>9s}  {'Reg eta2':>9s}  {'Reg p':>8s}  {'Herb eta2':>9s}  {'Herb p':>8s}")
print(f"   {'---'*25}")
for feat, r in sorted_by_regime:
    sect = f"{r['section_eta_sq']:.4f}" if r['section_eta_sq'] is not None else "     N/A"
    herb_e = f"{r['herbal_regime_eta_sq']:.4f}" if r['herbal_regime_eta_sq'] is not None else "     N/A"
    herb_p = f"{r['herbal_regime_p']:.4f}" if r['herbal_regime_p'] is not None else "     N/A"
    print(f"   {feat:>20s}  {sect:>9s}  {r['regime_eta_sq']:>9.4f}  {r['regime_p']:>8.4f}  {herb_e:>9s}  {herb_p:>8s}")

results['anova_regime_effects'] = anova_results

# ════════════════════════════════════════════════════════════════════════
# 3. Four-quadrant classification
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("3. FOUR-QUADRANT CLASSIFICATION")
print("="*70)
print(f"   section eta_sq > 0.15 = 'section effect'")
print(f"   within-{largest_section} REGIME eta_sq > 0.05 = 'regime effect'")

SECT_THRESH = 0.15
REG_THRESH = 0.05

quadrant_map = {}
quadrant_counts = {'SECTION-CONSTRAINED': [], 'REGIME-CONSTRAINED': [],
                   'BOTH': [], 'NEITHER_FREEDOM': []}

for feat, r in anova_results.items():
    sect_eta = r['section_eta_sq']
    herb_eta = r['herbal_regime_eta_sq']

    # If herbal eta is not available, fall back to overall regime eta
    if herb_eta is None:
        herb_eta = r['regime_eta_sq']

    if sect_eta is None:
        sect_eta = 0.0

    sect_high = sect_eta > SECT_THRESH
    reg_high = herb_eta > REG_THRESH

    if sect_high and reg_high:
        q = 'BOTH'
    elif sect_high and not reg_high:
        q = 'SECTION-CONSTRAINED'
    elif not sect_high and reg_high:
        q = 'REGIME-CONSTRAINED'
    else:
        q = 'NEITHER_FREEDOM'

    quadrant_map[feat] = q
    quadrant_counts[q].append(feat)

print(f"\n   Classification results:")
for q_name in ['SECTION-CONSTRAINED', 'REGIME-CONSTRAINED', 'BOTH', 'NEITHER_FREEDOM']:
    feats = quadrant_counts[q_name]
    print(f"\n   {q_name} ({len(feats)}):")
    for f in feats:
        r = anova_results[f]
        sect = r['section_eta_sq'] if r['section_eta_sq'] is not None else 0.0
        herb = r['herbal_regime_eta_sq'] if r['herbal_regime_eta_sq'] is not None else r['regime_eta_sq']
        print(f"     {f:>20s}  sect={sect:.3f}  herbal_reg={herb:.3f}")

results['four_quadrant'] = {
    'thresholds': {'section_eta_sq': SECT_THRESH, 'herbal_regime_eta_sq': REG_THRESH},
    'classification': quadrant_map,
    'counts': {k: len(v) for k, v in quadrant_counts.items()},
    'members': {k: v for k, v in quadrant_counts.items()}
}

# ════════════════════════════════════════════════════════════════════════
# 4. Within-REGIME variance (CV)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("4. WITHIN-REGIME VARIANCE (CV by REGIME group)")
print("="*70)

within_cv = {}
for regime in sorted(features_df['REGIME'].unique()):
    group = features_df[features_df['REGIME'] == regime]
    cvs = {}
    for feat in atom_features:
        vals = group[feat].values
        mean_val = np.mean(vals)
        std_val = np.std(vals, ddof=1)
        cv = std_val / mean_val if mean_val > 0.001 else np.nan
        cvs[feat] = float(cv) if not np.isnan(cv) else None
    within_cv[str(regime)] = cvs

# Mean within-REGIME CV per atom
print(f"\n   Mean within-REGIME CV per atom (low = homogeneous within REGIME):")
mean_within_cv = {}
for feat in atom_features:
    vals = [within_cv[r][feat] for r in within_cv if within_cv[r][feat] is not None]
    mean_within_cv[feat] = np.mean(vals) if vals else None

sorted_cv = sorted(
    [(f, v) for f, v in mean_within_cv.items() if v is not None],
    key=lambda x: x[1]
)

print(f"   {'Feature':>20s}  {'MeanCV':>8s}  {'R1':>8s}  {'R2':>8s}  {'R3':>8s}  {'R4':>8s}  {'Interp':>20s}")
print(f"   {'---'*25}")
regimes_ordered = ['R1_lowK', 'R2', 'R3', 'R4_highK']
for feat, mcv in sorted_cv:
    r_cvs = [within_cv[r].get(feat) for r in regimes_ordered]
    r_strs = [f"{v:.3f}" if v is not None else "  N/A" for v in r_cvs]
    interp = "HOMOGENEOUS" if mcv < 0.3 else ("MODERATE" if mcv < 0.6 else "HETEROGENEOUS")
    print(f"   {feat:>20s}  {mcv:>8.3f}  {r_strs[0]:>8s}  {r_strs[1]:>8s}  {r_strs[2]:>8s}  {r_strs[3]:>8s}  {interp:>20s}")

results['within_regime_cv'] = {
    'per_regime': within_cv,
    'mean_across_regimes': {k: float(v) if v is not None else None for k, v in mean_within_cv.items()},
    'homogeneous_atoms': [f for f, v in sorted_cv if v is not None and v < 0.3],
    'heterogeneous_atoms': [f for f, v in sorted_cv if v is not None and v >= 0.6]
}

# ════════════════════════════════════════════════════════════════════════
# 5. Overlap with s2 partition
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("5. OVERLAP WITH s2 PARTITION (FREEDOM/CONSTRAINED/MIXED)")
print("="*70)

s2_partition = {feat: info['partition'] for feat, info in s2_data['features'].items()}

print(f"\n   Cross-tabulation: s2 partition (rows) vs s4 quadrant (cols)")
print(f"   Expectation: s2-FREEDOM -> s4-NEITHER_FREEDOM")

s2_cats = ['CONSTRAINED', 'MIXED', 'FREEDOM']
s4_cats = ['SECTION-CONSTRAINED', 'REGIME-CONSTRAINED', 'BOTH', 'NEITHER_FREEDOM']

cross_tab = {s2: {s4: [] for s4 in s4_cats} for s2 in s2_cats}
for feat in atom_features:
    s2_cat = s2_partition.get(feat, 'UNKNOWN')
    s4_cat = quadrant_map.get(feat, 'ERROR')
    if s2_cat in cross_tab and s4_cat in cross_tab[s2_cat]:
        cross_tab[s2_cat][s4_cat].append(feat)

header = 's2\\s4'
print(f"\n   {header:>15s}", end='')
for s4 in s4_cats:
    print(f"  {s4[:12]:>12s}", end='')
print()
print(f"   {'---'*25}")

for s2 in s2_cats:
    print(f"   {s2:>15s}", end='')
    for s4 in s4_cats:
        n = len(cross_tab[s2][s4])
        print(f"  {n:>12d}", end='')
    print()

# Check the expectation
s2_freedom = [f for f, p in s2_partition.items() if p == 'FREEDOM']
s4_freedom = quadrant_counts['NEITHER_FREEDOM']
overlap = set(s2_freedom) & set(s4_freedom)
s2_only = set(s2_freedom) - set(s4_freedom)
s4_only = set(s4_freedom) - set(s2_freedom)

print(f"\n   s2-FREEDOM features: {s2_freedom}")
print(f"   s4-NEITHER features: {s4_freedom}")
print(f"   Overlap: {list(overlap)}")
print(f"   s2-FREEDOM but NOT s4-NEITHER: {list(s2_only)}")
print(f"   s4-NEITHER but NOT s2-FREEDOM: {list(s4_only)}")

agreement = len(overlap) / len(set(s2_freedom) | set(s4_freedom)) if (set(s2_freedom) | set(s4_freedom)) else 0
print(f"\n   Jaccard agreement (FREEDOM sets): {agreement:.3f}")

# Detailed cross-tab with feature names
cross_tab_names = {}
for s2 in s2_cats:
    for s4 in s4_cats:
        key = f"{s2}_x_{s4}"
        if cross_tab[s2][s4]:
            cross_tab_names[key] = cross_tab[s2][s4]

results['s2_overlap'] = {
    'cross_tab_counts': {s2: {s4: len(cross_tab[s2][s4]) for s4 in s4_cats} for s2 in s2_cats},
    'cross_tab_features': cross_tab_names,
    'freedom_jaccard': float(agreement),
    's2_freedom': s2_freedom,
    's4_neither': s4_freedom,
    'overlap': list(overlap),
    's2_only': list(s2_only),
    's4_only': list(s4_only)
}

# ════════════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

decomposable = loo_accuracy > perm_mean + 2 * perm_std
print(f"\n   RF LOO accuracy: {loo_accuracy:.3f} (chance: {perm_mean:.3f} +/- {perm_std:.3f})")
print(f"   REGIME is {'PARTIALLY' if decomposable else 'NOT'} decomposable to atoms")
print(f"     (accuracy {'>' if decomposable else '<='} chance + 2sigma)")

n_regime_driven = len(quadrant_counts['REGIME-CONSTRAINED']) + len(quadrant_counts['BOTH'])
n_section_only = len(quadrant_counts['SECTION-CONSTRAINED'])
n_free = len(quadrant_counts['NEITHER_FREEDOM'])
print(f"\n   Quadrant summary: {n_regime_driven} regime-driven, {n_section_only} section-only, {n_free} free")
print(f"   Most regime-driven atoms: {[f for f,_ in sorted_by_regime[:5]]}")
print(f"   Homogeneous within REGIME: {results['within_regime_cv']['homogeneous_atoms']}")
print(f"   Heterogeneous within REGIME: {results['within_regime_cv']['heterogeneous_atoms']}")

results['summary'] = {
    'regime_decomposable': bool(decomposable),
    'rf_accuracy': float(loo_accuracy),
    'chance_accuracy': float(perm_mean),
    'n_regime_driven': n_regime_driven,
    'n_section_only': n_section_only,
    'n_free': n_free,
    'freedom_set_jaccard': float(agreement)
}

# ── Save ────────────────────────────────────────────────────────────────
out_path = 'phases/FOLIO_DESIGN_FREEDOM/results/s4_regime_atom_interaction.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n   Saved: {out_path}")
