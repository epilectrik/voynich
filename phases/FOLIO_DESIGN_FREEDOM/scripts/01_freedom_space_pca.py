"""
Script 1: Freedom Space PCA
Question: What are the named dimensions of folio design freedom at atom resolution?

Builds section-residualized atom feature vectors per B folio, runs PCA,
names the resulting axes, and compares to prior category-level PCA (C1715, C1367).
"""

import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, pearsonr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS = Path(__file__).resolve().parent.parent / 'results'
RESULTS.mkdir(exist_ok=True)

# === Data Loading ===

tx = Transcript()
morph = Morphology()

HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
MOD_ATOMS = {'c', 'd', 'f', 'i', 'p', 's'}
TERM_ATOMS = {'h', 'l', 'm', 'n', 'r', 'y'}

def get_section(folio):
    """Map folio to section using standard Currier B section assignments."""
    # Standard mapping from constraint system
    bio_folios = {'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v',
                  'f79r', 'f79v', 'f80r', 'f80v', 'f81r', 'f81v', 'f82r', 'f82v',
                  'f83r', 'f83v', 'f84r', 'f84v'}
    stars_folios = {'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v',
                    'f106r', 'f106v', 'f107r', 'f107v', 'f108r', 'f108v',
                    'f109r', 'f109v', 'f110r', 'f110v', 'f111r', 'f111v',
                    'f112r', 'f112v', 'f113v', 'f114r', 'f114v', 'f115r', 'f115v', 'f116r'}
    cosmo_folios = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}
    # Everything else in B is Herbal
    if folio in bio_folios:
        return 'Bio'
    elif folio in stars_folios:
        return 'Stars'
    elif folio in cosmo_folios:
        return 'Cosmo'
    else:
        return 'Herbal'

# Collect token-level data
token_data = []
for tok in tx.currier_b():
    if '*' in tok.word or not tok.word.strip():
        continue
    m = morph.extract(tok.word)
    a = morph.atomize(tok.word)

    # HEAD classification
    atoms_list = a.atoms if a.atoms else []
    head = 'headless'
    if atoms_list and atoms_list[0][0] in HEAD_ATOMS:
        head = atoms_list[0][0]

    # Terminal atom
    term = None
    if atoms_list and atoms_list[-1][0] in TERM_ATOMS:
        term = atoms_list[-1][0]

    # Modifier atoms present
    mods_present = set()
    for atom_char, slot, _ in atoms_list:
        if atom_char in MOD_ATOMS:
            mods_present.add(atom_char)

    token_data.append({
        'folio': tok.folio,
        'word': tok.word,
        'prefix': m.prefix if m.prefix else 'BARE',
        'middle': m.middle,
        'suffix': m.suffix,
        'head': head,
        'term': term if term else 'bare',
        'mods': mods_present,
        'e_depth': a.e_depth if a else 0,
        'has_suffix': m.suffix is not None and m.suffix != '',
        'middle_len': len(m.middle) if m.middle else 0,
        'is_headless': a.is_headless if a else False,
    })

df = pd.DataFrame(token_data)
print(f"Total B tokens: {len(df)}")

# === Feature Extraction Per Folio ===

def build_folio_features(group):
    """Build atom-resolution feature vector for one folio."""
    n = len(group)
    if n < 30:
        return None

    features = {}

    # HEAD fractions (6 values: a, e, o, k, t, headless)
    head_counts = group['head'].value_counts()
    for h in ['a', 'e', 'o', 'k', 't', 'headless']:
        features[f'head_{h}'] = head_counts.get(h, 0) / n

    # TERMINAL fractions (7 values: h, l, m, n, r, y, bare)
    term_counts = group['term'].value_counts()
    for t in ['h', 'l', 'm', 'n', 'r', 'y', 'bare']:
        features[f'term_{t}'] = term_counts.get(t, 0) / n

    # MODIFIER fractions (6 values: c, d, f, i, p, s — fraction of tokens containing each)
    for mod in ['c', 'd', 'f', 'i', 'p', 's']:
        features[f'mod_{mod}'] = group['mods'].apply(lambda ms: mod in ms).mean()

    # PREFIX fractions (top PREFIXes + grouped)
    pfx_counts = group['prefix'].value_counts()
    for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'BARE', 'or', 'po', 'pch', 'te', 'ct']:
        features[f'pfx_{pfx}'] = pfx_counts.get(pfx, 0) / n

    # Compound features
    features['suffix_rate'] = group['has_suffix'].mean()
    features['mean_middle_len'] = group['middle_len'].mean()
    features['e_depth_mean'] = group['e_depth'].mean()
    features['headless_rate'] = group['is_headless'].mean()

    # Derived ratios
    features['ey_rate'] = len(group[(group['head'] == 'e') & (group['term'] == 'y')]) / n
    features['k_head_rate'] = features['head_k']
    features['thermal_ratio'] = features['pfx_qo'] / max(features['pfx_ch'] + features['pfx_sh'], 0.001)
    features['sister_ch_sh'] = features['pfx_ch'] / max(features['pfx_ch'] + features['pfx_sh'], 0.001)
    features['sister_ok_ot'] = features['pfx_ok'] / max(features['pfx_ok'] + features['pfx_ot'], 0.001)

    return features

folio_features = {}
folio_sections = {}
for folio, group in df.groupby('folio'):
    section = get_section(folio)
    feat = build_folio_features(group)
    if feat is not None:
        folio_features[folio] = feat
        folio_sections[folio] = section

feature_df = pd.DataFrame(folio_features).T
feature_df['section'] = [folio_sections[f] for f in feature_df.index]

print(f"Folios with features: {len(feature_df)}")
print(f"Feature dimensions: {len(feature_df.columns) - 1}")
print(f"Sections: {feature_df['section'].value_counts().to_dict()}")

# === Section Residualization ===

numeric_cols = [c for c in feature_df.columns if c != 'section']
residual_df = feature_df[numeric_cols].copy()

# Subtract section mean from each feature
for section in feature_df['section'].unique():
    mask = feature_df['section'] == section
    section_mean = feature_df.loc[mask, numeric_cols].mean()
    residual_df.loc[mask] = feature_df.loc[mask, numeric_cols] - section_mean

print(f"\nSection residualization complete. Residual variance fraction:")
for col in numeric_cols[:5]:
    raw_var = feature_df[col].var()
    resid_var = residual_df[col].var()
    print(f"  {col}: {resid_var/max(raw_var, 1e-10):.3f}")

# === PCA on Residualized Features ===

# Drop near-zero-variance features
var_threshold = 1e-8
keep_cols = [c for c in numeric_cols if residual_df[c].var() > var_threshold]
print(f"\nFeatures after variance filter: {len(keep_cols)} / {len(numeric_cols)}")

X = residual_df[keep_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Handle NaN from zero-variance after scaling
X_scaled = np.nan_to_num(X_scaled, nan=0.0)

pca = PCA()
pca_scores = pca.fit_transform(X_scaled)

# Variance explained
cum_var = np.cumsum(pca.explained_variance_ratio_)
n_80 = np.searchsorted(cum_var, 0.80) + 1
n_90 = np.searchsorted(cum_var, 0.90) + 1

print(f"\nPCA Results:")
print(f"  PCs for 80% variance: {n_80}")
print(f"  PCs for 90% variance: {n_90}")
print(f"  Effective dimensionality (>1% each): {sum(pca.explained_variance_ratio_ > 0.01)}")

# Name PCs by top loadings
pc_names = {}
loadings = pd.DataFrame(pca.components_.T, index=keep_cols, columns=[f'PC{i+1}' for i in range(len(keep_cols))])

print(f"\nTop PCs with loadings:")
for i in range(min(8, len(pca.explained_variance_ratio_))):
    pc = f'PC{i+1}'
    var_pct = pca.explained_variance_ratio_[i] * 100
    top_pos = loadings[pc].nlargest(3)
    top_neg = loadings[pc].nsmallest(3)

    # Name by dominant contrast
    pos_name = top_pos.index[0]
    neg_name = top_neg.index[0]
    pc_names[pc] = f"{pos_name}(+) vs {neg_name}(-)"

    print(f"\n  {pc} ({var_pct:.1f}%): {pc_names[pc]}")
    print(f"    Positive: {', '.join(f'{k}={v:.3f}' for k, v in top_pos.items())}")
    print(f"    Negative: {', '.join(f'{k}={v:.3f}' for k, v in top_neg.items())}")

# === Compare to C1715 (category-level PCA) ===

# C1715 found: PC1 (32%) loads qo_frac(+0.326), headless_frac(-0.306), k_frac(+0.304)
# Check if our atom-level PC1 recovers this
print(f"\n=== Comparison to C1715 ===")
print(f"C1715: PC1 (32%) = qo(+0.326), headless(-0.306), k(+0.304)")
for i in range(min(3, len(pca.explained_variance_ratio_))):
    pc = f'PC{i+1}'
    var_pct = pca.explained_variance_ratio_[i] * 100
    qo_load = loadings.loc['pfx_qo', pc] if 'pfx_qo' in loadings.index else 0
    hl_load = loadings.loc['headless_rate', pc] if 'headless_rate' in loadings.index else 0
    k_load = loadings.loc['head_k', pc] if 'head_k' in loadings.index else 0
    print(f"  Our {pc} ({var_pct:.1f}%): qo={qo_load:.3f}, headless={hl_load:.3f}, k={k_load:.3f}")

# === REGIME Prediction Test ===

# Load REGIME assignments if available
try:
    regime_path = Path(__file__).resolve().parents[3] / 'results' / 'regime_assignments.json'
    if regime_path.exists():
        with open(regime_path) as f:
            regime_data = json.load(f)
        regime_map = {k: v for k, v in regime_data.items() if k in feature_df.index}

        if len(regime_map) > 20:
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.model_selection import LeaveOneOut

            common_folios = [f for f in feature_df.index if f in regime_map]
            X_regime = pca_scores[[list(feature_df.index).index(f) for f in common_folios]]
            y_regime = [regime_map[f] for f in common_folios]

            # LOO with increasing PC count
            print(f"\n=== REGIME Prediction (LOO, n={len(common_folios)}) ===")
            for n_pcs in [3, 5, 8, len(keep_cols)]:
                n_pcs = min(n_pcs, X_regime.shape[1])
                loo = LeaveOneOut()
                correct = 0
                for train_idx, test_idx in loo.split(X_regime):
                    knn = KNeighborsClassifier(n_neighbors=5)
                    knn.fit(X_regime[train_idx, :n_pcs], [y_regime[i] for i in train_idx])
                    pred = knn.predict(X_regime[test_idx, :n_pcs])
                    if pred[0] == y_regime[test_idx[0]]:
                        correct += 1
                acc = correct / len(common_folios)
                print(f"  {n_pcs} PCs: {acc:.3f} ({correct}/{len(common_folios)})")
    else:
        print("\nREGIME assignments not found — skipping prediction test")
except Exception as e:
    print(f"\nREGIME prediction failed: {e}")

# === Save Results ===

results = {
    'n_folios': len(feature_df),
    'n_features': len(keep_cols),
    'feature_names': keep_cols,
    'pca_variance_explained': pca.explained_variance_ratio_.tolist(),
    'pcs_for_80pct': int(n_80),
    'pcs_for_90pct': int(n_90),
    'effective_dimensionality': int(sum(pca.explained_variance_ratio_ > 0.01)),
    'pc_names': pc_names,
    'pc_loadings': {f'PC{i+1}': {k: float(v) for k, v in loadings[f'PC{i+1}'].items()}
                    for i in range(min(10, len(pca.explained_variance_ratio_)))},
    'folio_scores': {f: pca_scores[i, :10].tolist()
                     for i, f in enumerate(feature_df.index)},
    'sections': folio_sections,
}

with open(RESULTS / '01_freedom_space_pca.json', 'w') as f:
    json.dump(results, f, indent=2)

# Save the feature matrix for downstream scripts
feature_df.to_csv(RESULTS / '01_folio_atom_features.csv')
residual_df.to_csv(RESULTS / '01_folio_atom_features_residualized.csv')

print(f"\nResults saved to {RESULTS / '01_freedom_space_pca.json'}")
print("Done.")
