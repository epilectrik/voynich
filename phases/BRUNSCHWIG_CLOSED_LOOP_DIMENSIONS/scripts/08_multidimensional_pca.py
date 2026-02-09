#!/usr/bin/env python3
"""
Test 8: Multi-Dimensional Profile PCA

Determines how many independent dimensions describe the Voynich
control parameter space.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load class map
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map = json.load(f)

token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}
token_to_role = class_map.get('token_to_role', {})

# Key classes
LINK_CLASS = 29
FQ_CLASSES = {9, 13, 14, 23}
KERNEL_CHARS = {'k', 'h', 'e'}

# Build token sets
link_tokens = set(t for t, c in token_to_class.items() if c == LINK_CLASS)
fq_tokens = set(t for t, c in token_to_class.items() if c in FQ_CLASSES)

# Role token sets
role_tokens = defaultdict(set)
for token, role in token_to_role.items():
    role_tokens[role].add(token)

# Load REGIME mapping
with open(Path(__file__).parent.parent.parent.parent / 'results' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    regime_num = int(regime.replace('REGIME_', ''))
    for folio in folios:
        folio_regime[folio] = regime_num

# Load transcript
tx = Transcript()

print("="*70)
print("TEST 8: MULTI-DIMENSIONAL PCA")
print("="*70)

# Build line-grouped tokens for post-FQ analysis
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    key = (token.folio, token.line)
    line_tokens[key].append(token)

# Compute feature matrix per folio
folio_features = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio = token.folio
    word = token.word

    if folio not in folio_features:
        folio_features[folio] = {
            'total': 0,
            'link': 0,
            'fq': 0,
            'energy': 0,
            'frequent': 0,
            'flow': 0,
            'core': 0,
            'kernel_k': 0,
            'kernel_h': 0,
            'kernel_e': 0,
        }

    f = folio_features[folio]
    f['total'] += 1

    if word in link_tokens:
        f['link'] += 1
    if word in fq_tokens:
        f['fq'] += 1

    role = token_to_role.get(word)
    if role == 'ENERGY_OPERATOR':
        f['energy'] += 1
    elif role == 'FREQUENT_OPERATOR':
        f['frequent'] += 1
    elif role == 'FLOW_OPERATOR':
        f['flow'] += 1
    elif role == 'CORE_CONTROL':
        f['core'] += 1

    for c in word:
        if c == 'k':
            f['kernel_k'] += 1
        elif c == 'h':
            f['kernel_h'] += 1
        elif c == 'e':
            f['kernel_e'] += 1

# Add post-FQ h rate
def get_first_kernel(word):
    for c in word:
        if c in KERNEL_CHARS:
            return c
    return None

folio_post_fq = defaultdict(lambda: {'h': 0, 'total': 0})
for (folio, line), tokens in line_tokens.items():
    words = [t.word for t in tokens]
    for i, word in enumerate(words):
        cls = token_to_class.get(word)
        if cls in FQ_CLASSES and i + 1 < len(words):
            folio_post_fq[folio]['total'] += 1
            if get_first_kernel(words[i+1]) == 'h':
                folio_post_fq[folio]['h'] += 1

# Build normalized feature matrix
features_list = ['link', 'fq', 'energy', 'frequent', 'flow', 'core', 'kernel_k', 'kernel_h', 'kernel_e']
MIN_TOKENS = 100

data = []
folios = []

for folio in sorted(folio_features.keys()):
    f = folio_features[folio]
    if f['total'] < MIN_TOKENS:
        continue

    row = [f[feat] / f['total'] for feat in features_list]

    # Add post-FQ h rate
    pf = folio_post_fq[folio]
    post_fq_h = pf['h'] / pf['total'] if pf['total'] > 5 else 0
    row.append(post_fq_h)

    data.append(row)
    folios.append(folio)

features_list.append('post_fq_h')
X = np.array(data)

print(f"\nFolios analyzed: {len(folios)}")
print(f"Features: {len(features_list)}")
print(f"  {features_list}")

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA()
pca.fit(X_scaled)

# Variance explained
var_explained = pca.explained_variance_ratio_
cumulative_var = np.cumsum(var_explained)

print(f"\n{'='*70}")
print("PCA RESULTS")
print("="*70)

print(f"\nComponent   Variance%   Cumulative%")
print("-"*40)
for i, (v, c) in enumerate(zip(var_explained, cumulative_var)):
    marker = "*" if c <= 0.9 else ""
    print(f"  PC{i+1:2d}        {100*v:5.1f}%       {100*c:5.1f}%  {marker}")

# Determine dimensionality
n_components_90 = np.argmax(cumulative_var >= 0.90) + 1
n_components_80 = np.argmax(cumulative_var >= 0.80) + 1

print(f"\nComponents for 80% variance: {n_components_80}")
print(f"Components for 90% variance: {n_components_90}")

# Feature loadings for top components
print(f"\n{'='*70}")
print("FEATURE LOADINGS (Top 3 Components)")
print("="*70)

loadings = pca.components_

print(f"\n{'Feature':<15} {'PC1':>8} {'PC2':>8} {'PC3':>8}")
print("-"*45)
for i, feat in enumerate(features_list):
    print(f"  {feat:<13} {loadings[0,i]:+.3f}   {loadings[1,i]:+.3f}   {loadings[2,i]:+.3f}")

# Interpret components
print(f"\n{'='*70}")
print("COMPONENT INTERPRETATION")
print("="*70)

for pc_idx in range(min(3, len(features_list))):
    loadings_pc = loadings[pc_idx]
    top_pos = np.argsort(loadings_pc)[-3:][::-1]
    top_neg = np.argsort(loadings_pc)[:3]

    print(f"\nPC{pc_idx+1} ({100*var_explained[pc_idx]:.1f}% variance):")
    print(f"  Positive: {', '.join([f'{features_list[i]} ({loadings_pc[i]:+.2f})' for i in top_pos])}")
    print(f"  Negative: {', '.join([f'{features_list[i]} ({loadings_pc[i]:+.2f})' for i in top_neg])}")

# Compare to Brunschwig
print(f"\n{'='*70}")
print("COMPARISON TO BRUNSCHWIG")
print("="*70)
print(f"""
Brunschwig's parameter space: ~3 dimensions
  - Fire degree (1-4)
  - Material type (herb, root, flower, animal)
  - Method (balneum marie, direct fire, etc.)

Voynich parameter space: {n_components_80} dimensions for 80%, {n_components_90} for 90%
  - PC1: {', '.join([features_list[i] for i in np.argsort(abs(loadings[0]))[-2:][::-1]])}
  - PC2: {', '.join([features_list[i] for i in np.argsort(abs(loadings[1]))[-2:][::-1]])}
  - PC3: {', '.join([features_list[i] for i in np.argsort(abs(loadings[2]))[-2:][::-1]])}
""")

# Verdict
if n_components_80 >= 4:
    verdict = "SUPPORT"
    print(f"** Voynich has MORE dimensions than Brunschwig's linear model **")
else:
    verdict = "PARTIAL"
    print(f"Dimensionality similar to Brunschwig")

# Save results
output = {
    'test': 'Multi-Dimensional PCA',
    'n_folios': len(folios),
    'n_features': len(features_list),
    'features': features_list,
    'variance_explained': [float(v) for v in var_explained],
    'cumulative_variance': [float(c) for c in cumulative_var],
    'n_components_80': int(n_components_80),
    'n_components_90': int(n_components_90),
    'loadings': {f'PC{i+1}': {feat: float(loadings[i, j]) for j, feat in enumerate(features_list)} for i in range(min(5, len(features_list)))},
    'verdict': verdict
}

output_path = results_dir / 'multidimensional_pca.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
