#!/usr/bin/env python3
"""
Test 6: PP Gradient Analysis

Question: What continuous gradients describe PP variation across folios?

Uses PCA to identify principal gradients of variation, avoiding
the clustering approach that failed in A_PP_PROCEDURAL_MODES.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

# Role mapping
PREFIX_ROLES = {
    'ct': 'CROSS-REF', 'da': 'CLOSURE', 'do': 'CLOSURE',
    'ok': 'AUXILIARY', 'ol': 'LINK', 'or': 'LINK',
    'ot': 'OTHER', 'yk': 'OTHER', 'al': 'OTHER', 'ar': 'OTHER',
}

def get_role(prefix):
    if prefix in PREFIX_ROLES:
        return PREFIX_ROLES[prefix]
    if prefix and prefix.endswith('ch'):
        return 'GALLOWS-CH'
    if prefix and prefix.endswith('o') and len(prefix) == 2:
        return 'INPUT'
    return 'OTHER'

print("="*70)
print("TEST 6: PP GRADIENT ANALYSIS")
print("="*70)

# Build folio-level PP features
folio_data = defaultdict(lambda: {
    'pp_count': 0,
    'prefix_counts': Counter(),
    'middle_counts': Counter(),
    'role_counts': Counter(),
    'section': None,
})

for token in tx.currier_a():
    if '*' in token.word:
        continue

    try:
        m = morph.extract(token.word)
        if m.prefix not in RI_PREFIXES:
            folio_data[token.folio]['pp_count'] += 1
            if m.prefix:
                folio_data[token.folio]['prefix_counts'][m.prefix] += 1
                role = get_role(m.prefix)
                folio_data[token.folio]['role_counts'][role] += 1
            if m.middle:
                folio_data[token.folio]['middle_counts'][m.middle] += 1
        folio_data[token.folio]['section'] = token.section
    except:
        pass

# Filter to folios with sufficient data
MIN_PP = 30
folios = [f for f in folio_data if folio_data[f]['pp_count'] >= MIN_PP]
print(f"\nFolios with PP >= {MIN_PP}: {len(folios)}")

# Build feature matrix
roles = ['CROSS-REF', 'CLOSURE', 'AUXILIARY', 'LINK', 'GALLOWS-CH', 'INPUT', 'OTHER']

features = []
sections = []
for folio in folios:
    data = folio_data[folio]
    total = data['pp_count']

    # Role proportions
    role_vec = [data['role_counts'].get(r, 0) / total for r in roles]

    # MIDDLE diversity
    middle_diversity = len(data['middle_counts']) / total

    # Add features
    features.append(role_vec + [middle_diversity])
    sections.append(data['section'])

X = np.array(features)
feature_names = roles + ['MIDDLE_DIVERSITY']

print(f"Feature matrix shape: {X.shape}")

# =========================================================================
# PCA Analysis
# =========================================================================
print("\n" + "="*70)
print("PCA ANALYSIS")
print("="*70)

pca = PCA()
X_pca = pca.fit_transform(X)

print(f"\nVariance explained by each component:")
cumulative = 0
for i, var in enumerate(pca.explained_variance_ratio_):
    cumulative += var
    print(f"  PC{i+1}: {100*var:.1f}% (cumulative: {100*cumulative:.1f}%)")
    if cumulative > 0.95:
        break

# Loadings for top 3 PCs
print(f"\nPC Loadings (top 3 components):")
print(f"\n{'Feature':<18} {'PC1':<10} {'PC2':<10} {'PC3':<10}")
print("-"*50)

for i, name in enumerate(feature_names):
    pc1 = pca.components_[0, i]
    pc2 = pca.components_[1, i]
    pc3 = pca.components_[2, i] if len(pca.components_) > 2 else 0
    print(f"{name:<18} {pc1:>+.3f}{'':>5} {pc2:>+.3f}{'':>5} {pc3:>+.3f}")

# Interpret gradients
print("\nGradient interpretation:")
pc1_top = sorted(zip(feature_names, pca.components_[0]), key=lambda x: abs(x[1]), reverse=True)
pc2_top = sorted(zip(feature_names, pca.components_[1]), key=lambda x: abs(x[1]), reverse=True)

print(f"  PC1 ({100*pca.explained_variance_ratio_[0]:.1f}%): {pc1_top[0][0]} ({pc1_top[0][1]:+.3f}), {pc1_top[1][0]} ({pc1_top[1][1]:+.3f})")
print(f"  PC2 ({100*pca.explained_variance_ratio_[1]:.1f}%): {pc2_top[0][0]} ({pc2_top[0][1]:+.3f}), {pc2_top[1][0]} ({pc2_top[1][1]:+.3f})")

# =========================================================================
# Section correlation with gradients
# =========================================================================
print("\n" + "="*70)
print("SECTION CORRELATION WITH GRADIENTS")
print("="*70)

section_codes = {'H': 0, 'P': 1, 'T': 2}
section_numeric = [section_codes.get(s, -1) for s in sections]

# Only test H vs P (most common)
hp_mask = [s in ['H', 'P'] for s in sections]
hp_sections = [s for s, m in zip(sections, hp_mask) if m]
hp_pc1 = X_pca[hp_mask, 0]
hp_pc2 = X_pca[hp_mask, 1]

# T-tests: does PC separate sections?
h_pc1 = [v for v, s in zip(hp_pc1, hp_sections) if s == 'H']
p_pc1 = [v for v, s in zip(hp_pc1, hp_sections) if s == 'P']

if len(h_pc1) > 3 and len(p_pc1) > 3:
    t_stat, p_val = stats.ttest_ind(h_pc1, p_pc1)
    print(f"\nPC1 vs Section (H vs P):")
    print(f"  H mean: {np.mean(h_pc1):.3f}, P mean: {np.mean(p_pc1):.3f}")
    print(f"  t={t_stat:.2f}, p={p_val:.4f}")
    if p_val < 0.05:
        print("  ** PC1 significantly separates H and P sections **")

    h_pc2 = [v for v, s in zip(hp_pc2, hp_sections) if s == 'H']
    p_pc2 = [v for v, s in zip(hp_pc2, hp_sections) if s == 'P']

    t_stat2, p_val2 = stats.ttest_ind(h_pc2, p_pc2)
    print(f"\nPC2 vs Section (H vs P):")
    print(f"  H mean: {np.mean(h_pc2):.3f}, P mean: {np.mean(p_pc2):.3f}")
    print(f"  t={t_stat2:.2f}, p={p_val2:.4f}")
    if p_val2 < 0.05:
        print("  ** PC2 significantly separates H and P sections **")
else:
    p_val = 1.0
    p_val2 = 1.0

# =========================================================================
# Within-section variation
# =========================================================================
print("\n" + "="*70)
print("WITHIN-SECTION VARIATION")
print("="*70)

for section in ['H', 'P']:
    mask = [s == section for s in sections]
    if sum(mask) < 5:
        continue

    section_X = X_pca[mask]
    print(f"\nSection {section} (n={sum(mask)}):")
    print(f"  PC1 range: {section_X[:, 0].min():.3f} to {section_X[:, 0].max():.3f}")
    print(f"  PC1 std: {section_X[:, 0].std():.3f}")
    print(f"  PC2 std: {section_X[:, 1].std():.3f}")

    # Is within-section variation substantial?
    total_var = X_pca[:, 0].var()
    within_var = section_X[:, 0].var()
    print(f"  Within-section variance / total: {100*within_var/total_var:.1f}%")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: PP GRADIENT ANALYSIS")
print("="*70)

var_pc1 = pca.explained_variance_ratio_[0]
var_pc2 = pca.explained_variance_ratio_[1]

print(f"""
Principal gradients:
  PC1: {100*var_pc1:.1f}% variance - driven by {pc1_top[0][0]}
  PC2: {100*var_pc2:.1f}% variance - driven by {pc2_top[0][0]}

Section separation:
  PC1 separates H/P: p={p_val:.4f} {'(YES)' if p_val < 0.05 else '(NO)'}
  PC2 separates H/P: p={p_val2:.4f} {'(YES)' if p_val2 < 0.05 else '(NO)'}

Implication:
  PP variation is {'primarily section-driven' if p_val < 0.01 else 'partially section-driven' if p_val < 0.05 else 'not primarily section-driven'}
""")

# Determine verdict
if var_pc1 > 0.4 and p_val < 0.01:
    verdict = "CONFIRMED"
    explanation = "Clear gradient structure dominated by section difference"
elif var_pc1 > 0.3 or p_val < 0.05:
    verdict = "SUPPORT"
    explanation = "Gradient structure exists, partially section-related"
else:
    verdict = "NOT SUPPORTED"
    explanation = "No clear gradient structure in PP variation"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'n_folios': len(folios),
    'n_features': len(feature_names),
    'variance_explained': list(pca.explained_variance_ratio_[:5]),
    'pc1_loadings': {name: float(pca.components_[0, i]) for i, name in enumerate(feature_names)},
    'pc2_loadings': {name: float(pca.components_[1, i]) for i, name in enumerate(feature_names)},
    'section_separation_pc1_p': p_val,
    'section_separation_pc2_p': p_val2,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'pp_gradient_analysis.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
