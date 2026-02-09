"""
02_extended_pca.py - Extended PCA combining original + procedural features

Compares:
- Original 5D (from BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS)
- Extended with procedural features
- Tests if procedural features add independent variance
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("EXTENDED PCA: ORIGINAL + PROCEDURAL FEATURES")
print("="*70)

# ============================================================
# LOAD PROCEDURAL FEATURES
# ============================================================
print("\n--- Loading Procedural Features ---")

proc_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'procedural_features.json'
with open(proc_path, 'r', encoding='utf-8') as f:
    proc_data = json.load(f)

proc_features = proc_data['folio_features']
print(f"Loaded procedural features for {len(proc_features)} folios")

# ============================================================
# COMPUTE ORIGINAL FEATURES (from BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS)
# ============================================================
print("\n--- Computing Original Features ---")

# Role classification patterns (simplified from BCSC)
def classify_role(word, m):
    """Simplified role classification"""
    if not m or not m.middle:
        return 'OTHER'

    middle = m.middle
    prefix = m.prefix or ''

    # ENERGY: qo, ch, sh prefixed thermal operations
    if prefix in {'qo', 'ch', 'sh'}:
        return 'ENERGY'

    # FLOW: ol, or, al, ar prefixes
    if prefix in {'ol', 'or', 'al', 'ar'}:
        return 'FLOW'

    # CORE_CONTROL: specific patterns
    if 'aiin' in middle or 'ain' in middle:
        return 'CORE'

    # FREQUENT: high-frequency infrastructure
    if middle in {'d', 'y', 'dy', 'edy', 'ey'}:
        return 'FREQUENT'

    # AUXILIARY: scaffolding prefixes
    if prefix in {'ok', 'ot', 'od', 'os'}:
        return 'AUXILIARY'

    return 'OTHER'

def has_kernel(middle):
    """Check if MIDDLE contains kernel chars"""
    if not middle:
        return {'k': False, 'h': False, 'e': False}
    return {
        'k': 'k' in middle,
        'h': 'h' in middle or 'ch' in middle or 'sh' in middle,
        'e': 'e' in middle
    }

def is_link(word, m):
    """Check if token is LINK operator"""
    if not m or not m.middle:
        return False
    return m.middle in {'ck', 'cth', 'ckh'} or 'ck' in (m.middle or '')

def is_fq(word, m):
    """Check if token is FQ (frequent/escape)"""
    if not m:
        return False
    suffix = getattr(m, 'suffix', '')
    return suffix in {'y', 'dy', 'edy', 'ey', 'eey'}

# Compute original features per folio
original_features = {}

for folio in proc_features.keys():
    tokens = list(tx.currier_b())
    folio_tokens = [t for t in tokens if t.folio == folio]

    if len(folio_tokens) < 20:
        continue

    total = len(folio_tokens)

    # Role counts
    role_counts = defaultdict(int)
    kernel_counts = {'k': 0, 'h': 0, 'e': 0}
    link_count = 0
    fq_count = 0

    for t in folio_tokens:
        m = morph.extract(t.word)
        role = classify_role(t.word, m)
        role_counts[role] += 1

        if m and m.middle:
            kernels = has_kernel(m.middle)
            for k, v in kernels.items():
                if v:
                    kernel_counts[k] += 1

        if is_link(t.word, m):
            link_count += 1

        if is_fq(t.word, m):
            fq_count += 1

    original_features[folio] = {
        'ENERGY_rate': role_counts['ENERGY'] / total,
        'FLOW_rate': role_counts['FLOW'] / total,
        'CORE_rate': role_counts['CORE'] / total,
        'FREQUENT_rate': role_counts['FREQUENT'] / total,
        'AUXILIARY_rate': role_counts['AUXILIARY'] / total,
        'kernel_k': kernel_counts['k'] / total,
        'kernel_h': kernel_counts['h'] / total,
        'kernel_e': kernel_counts['e'] / total,
        'LINK_rate': link_count / total,
        'FQ_rate': fq_count / total
    }

print(f"Computed original features for {len(original_features)} folios")

# ============================================================
# BUILD COMBINED FEATURE MATRIX
# ============================================================
print("\n--- Building Combined Feature Matrix ---")

# Get common folios
common_folios = set(original_features.keys()) & set(proc_features.keys())
print(f"Common folios: {len(common_folios)}")

# Original feature names
orig_names = ['ENERGY_rate', 'FLOW_rate', 'CORE_rate', 'FREQUENT_rate', 'AUXILIARY_rate',
              'kernel_k', 'kernel_h', 'kernel_e', 'LINK_rate', 'FQ_rate']

# Procedural feature names
proc_names = ['prep_density', 'thermo_density', 'extended_density',
              'prep_thermo_ratio', 'ke_kch_ratio',
              'prep_mean_position', 'thermo_mean_position', 'extended_mean_position',
              'tier_spread', 'prep_diversity', 'qo_chsh_early_ratio', 'kernel_order_compliance']

# Build matrices
folios = sorted(common_folios)
X_orig = np.array([[original_features[f][feat] for feat in orig_names] for f in folios])
X_proc = np.array([[proc_features[f][feat] for feat in proc_names] for f in folios])
X_combined = np.hstack([X_orig, X_proc])

print(f"Original features shape: {X_orig.shape}")
print(f"Procedural features shape: {X_proc.shape}")
print(f"Combined features shape: {X_combined.shape}")

# ============================================================
# PCA ANALYSIS
# ============================================================
print("\n--- PCA Analysis ---")

# Standardize
scaler_orig = StandardScaler()
scaler_proc = StandardScaler()
scaler_comb = StandardScaler()

X_orig_scaled = scaler_orig.fit_transform(X_orig)
X_proc_scaled = scaler_proc.fit_transform(X_proc)
X_comb_scaled = scaler_comb.fit_transform(X_combined)

# PCA on original only
pca_orig = PCA()
pca_orig.fit(X_orig_scaled)

# PCA on procedural only
pca_proc = PCA()
pca_proc.fit(X_proc_scaled)

# PCA on combined
pca_comb = PCA()
pca_comb.fit(X_comb_scaled)

# ============================================================
# VARIANCE EXPLAINED COMPARISON
# ============================================================
print("\n--- Variance Explained Comparison ---")

def dims_for_variance(explained_ratio, threshold=0.80):
    """Find number of dimensions for threshold variance"""
    cumsum = np.cumsum(explained_ratio)
    return np.argmax(cumsum >= threshold) + 1

orig_dims_80 = dims_for_variance(pca_orig.explained_variance_ratio_, 0.80)
proc_dims_80 = dims_for_variance(pca_proc.explained_variance_ratio_, 0.80)
comb_dims_80 = dims_for_variance(pca_comb.explained_variance_ratio_, 0.80)

print(f"\nDimensions for 80% variance:")
print(f"  Original features only: {orig_dims_80}")
print(f"  Procedural features only: {proc_dims_80}")
print(f"  Combined features: {comb_dims_80}")

print(f"\nVariance explained by first 5 components:")
print(f"  Original: {100*np.sum(pca_orig.explained_variance_ratio_[:5]):.1f}%")
print(f"  Procedural: {100*np.sum(pca_proc.explained_variance_ratio_[:5]):.1f}%")
print(f"  Combined: {100*np.sum(pca_comb.explained_variance_ratio_[:5]):.1f}%")

# Detailed breakdown
print(f"\n{'PC':<5} {'Original':>10} {'Procedural':>12} {'Combined':>10}")
print("-" * 40)
for i in range(min(8, len(pca_comb.explained_variance_ratio_))):
    orig_var = pca_orig.explained_variance_ratio_[i] if i < len(pca_orig.explained_variance_ratio_) else 0
    proc_var = pca_proc.explained_variance_ratio_[i] if i < len(pca_proc.explained_variance_ratio_) else 0
    comb_var = pca_comb.explained_variance_ratio_[i]
    print(f"PC{i+1:<3} {100*orig_var:>9.1f}% {100*proc_var:>11.1f}% {100*comb_var:>9.1f}%")

# ============================================================
# INDEPENDENCE TEST
# ============================================================
print("\n--- Independence Test: Procedural vs Original PCs ---")

# Transform both to their PC spaces
orig_pcs = pca_orig.transform(X_orig_scaled)
proc_pcs = pca_proc.transform(X_proc_scaled)

# Correlate procedural PCs with original PCs
print(f"\nCorrelation matrix (Procedural PC rows, Original PC columns):")
print(f"         {'PC1':>8} {'PC2':>8} {'PC3':>8} {'PC4':>8} {'PC5':>8}")

max_corr_per_proc_pc = []
for i in range(min(5, proc_pcs.shape[1])):
    corrs = []
    for j in range(min(5, orig_pcs.shape[1])):
        r, _ = stats.pearsonr(proc_pcs[:, i], orig_pcs[:, j])
        corrs.append(r)
    max_corr_per_proc_pc.append(max(abs(c) for c in corrs))
    print(f"Proc PC{i+1} " + " ".join(f"{c:>8.3f}" for c in corrs))

print(f"\nMax |correlation| for each procedural PC:")
for i, mc in enumerate(max_corr_per_proc_pc):
    status = "INDEPENDENT" if mc < 0.3 else "CORRELATED" if mc < 0.5 else "REDUNDANT"
    print(f"  Proc PC{i+1}: {mc:.3f} ({status})")

# Count independent PCs
independent_pcs = sum(1 for mc in max_corr_per_proc_pc if mc < 0.3)
print(f"\nIndependent procedural PCs (|r| < 0.3): {independent_pcs}/{len(max_corr_per_proc_pc)}")

# ============================================================
# FEATURE LOADINGS ON NEW DIMENSIONS
# ============================================================
print("\n--- Feature Loadings on Combined PCs ---")

all_names = orig_names + proc_names
print(f"\nTop loadings on PC1-PC3 (combined):")

for pc_idx in range(3):
    loadings = pca_comb.components_[pc_idx]
    sorted_idx = np.argsort(np.abs(loadings))[::-1]
    print(f"\nPC{pc_idx+1} ({100*pca_comb.explained_variance_ratio_[pc_idx]:.1f}%):")
    for i in sorted_idx[:5]:
        print(f"  {all_names[i]:<25} {loadings[i]:>8.3f}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'PROCEDURAL_DIMENSION_EXTENSION',
    'test': 'extended_pca',
    'n_folios': len(folios),
    'n_features': {
        'original': len(orig_names),
        'procedural': len(proc_names),
        'combined': len(orig_names) + len(proc_names)
    },
    'dimensions_for_80pct': {
        'original': int(orig_dims_80),
        'procedural': int(proc_dims_80),
        'combined': int(comb_dims_80)
    },
    'variance_explained_5pc': {
        'original': float(np.sum(pca_orig.explained_variance_ratio_[:5])),
        'procedural': float(np.sum(pca_proc.explained_variance_ratio_[:5])),
        'combined': float(np.sum(pca_comb.explained_variance_ratio_[:5]))
    },
    'independence_test': {
        'max_correlations': [float(mc) for mc in max_corr_per_proc_pc],
        'independent_pcs': independent_pcs,
        'threshold': 0.3
    },
    'eigenvalues': {
        'original': [float(v) for v in pca_orig.explained_variance_[:8]],
        'procedural': [float(v) for v in pca_proc.explained_variance_[:8]],
        'combined': [float(v) for v in pca_comb.explained_variance_[:8]]
    },
    'variance_ratios': {
        'original': [float(v) for v in pca_orig.explained_variance_ratio_[:8]],
        'procedural': [float(v) for v in pca_proc.explained_variance_ratio_[:8]],
        'combined': [float(v) for v in pca_comb.explained_variance_ratio_[:8]]
    }
}

output_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'extended_pca.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: EXTENDED PCA")
print("="*70)

dimension_increase = comb_dims_80 - orig_dims_80

print(f"""
Do procedural features add independent dimensionality?

Dimensions for 80% variance:
  Original: {orig_dims_80}
  Combined: {comb_dims_80}
  Increase: {dimension_increase}

Independence test:
  Procedural PCs with |r| < 0.3 to all original PCs: {independent_pcs}

Verdict: {'STRONG - Procedural features add ' + str(dimension_increase) + ' independent dimension(s)' if dimension_increase > 0 and independent_pcs > 0 else 'WEAK - Procedural features largely redundant with original'}

{'The three-tier structure captures variance not explained by aggregate rate features.' if dimension_increase > 0 else 'The three-tier structure is a consequence of rate patterns, not independent encoding.'}
""")
