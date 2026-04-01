"""
Script 4: Operational Meaning Mapping
Question: Do design freedom choices map to interpretable operational differences?

Correlates atom-level freedom PCs with operational metrics (AXM dwell, hazard rate,
safety strategy, closure, paragraph architecture), builds "recipe cards" for
extreme folios, and tests against apparatus manifold.
"""

import sys, json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.stats import spearmanr, pearsonr, mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS = Path(__file__).resolve().parent.parent / 'results'

# === Load PCA Results ===

with open(RESULTS / '01_freedom_space_pca.json') as f:
    pca_results = json.load(f)

feature_df = pd.read_csv(RESULTS / '01_folio_atom_features.csv', index_col=0)
residual_df = pd.read_csv(RESULTS / '01_folio_atom_features_residualized.csv', index_col=0)

sections = pd.Series(pca_results['sections'])
folio_scores = pca_results['folio_scores']  # dict: folio -> [PC1, PC2, ...]
folios = list(feature_df.index)

print(f"Loaded {len(folios)} folios with PCA scores")

# === Compute Operational Metrics Per Folio ===

tx = Transcript()
morph = Morphology()

HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
TERM_ATOMS = {'h', 'l', 'm', 'n', 'r', 'y'}

# Pre-collect all tokens by folio for operational metrics
folio_tokens = {}
for tok in tx.currier_b():
    if '*' in tok.word or not tok.word.strip():
        continue
    if tok.folio not in folio_tokens:
        folio_tokens[tok.folio] = []
    folio_tokens[tok.folio].append(tok)

# Build operational metrics
op_metrics = {}
for folio in folios:
    if folio not in folio_tokens:
        continue
    tokens = folio_tokens[folio]
    n = len(tokens)
    if n < 30:
        continue

    metrics = {}

    # Parse all tokens
    parsed = []
    for tok in tokens:
        m = morph.extract(tok.word)
        a = morph.atomize(tok.word)
        atoms = a.atoms if a.atoms else []
        head = atoms[0][0] if atoms and atoms[0][0] in HEAD_ATOMS else 'headless'
        term = atoms[-1][0] if atoms and atoms[-1][0] in TERM_ATOMS else 'bare'
        parsed.append({
            'prefix': m.prefix or 'BARE',
            'middle': m.middle,
            'suffix': m.suffix or '',
            'head': head,
            'term': term,
            'e_depth': a.e_depth,
            'is_headless': a.is_headless,
            'line': tok.line,
        })

    pdf = pd.DataFrame(parsed)

    # Kernel ratios (C089, C103-C105)
    metrics['k_ratio'] = (pdf['head'] == 'k').mean()
    metrics['e_ratio'] = (pdf['head'] == 'e').mean()
    metrics['h_in_middle'] = sum(1 for t in tokens if 'h' in (morph.extract(t.word).middle or '')) / n

    # Safety metrics (C1457, C1732-C1733)
    metrics['ey_rate'] = ((pdf['head'] == 'e') & (pdf['term'] == 'y')).mean()
    metrics['ii_rate'] = sum(1 for t in tokens if 'ii' in (morph.extract(t.word).middle or '')) / n

    # Closure metrics (C1434-C1439)
    metrics['m_terminal_rate'] = (pdf['term'] == 'm').mean()

    # Checkpoint rate (n-terminal, C1482-C1484)
    metrics['n_terminal_rate'] = (pdf['term'] == 'n').mean()

    # Iteration (i-modifier)
    metrics['i_mod_rate'] = sum(1 for p in parsed if any(
        atom[0] == 'i' for atom in (morph.atomize(tokens[i].word).atoms or [])
        if atom[1] == 'MOD'
    ) for i, p in enumerate(parsed)) / n

    # Suffix rate
    metrics['suffix_rate'] = (pdf['suffix'] != '').mean()

    # E-depth (thermal gentleness, C1225)
    metrics['mean_e_depth'] = pdf['e_depth'].mean()

    # Headless rate (C1488-C1493)
    metrics['headless_rate'] = pdf['is_headless'].mean()

    # Thermal ratio (qo vs ch+sh)
    qo_count = (pdf['prefix'] == 'qo').sum()
    chsh_count = ((pdf['prefix'] == 'ch') | (pdf['prefix'] == 'sh')).sum()
    metrics['thermal_ratio'] = qo_count / max(qo_count + chsh_count, 1)

    # Sister pair ratios
    ch_count = (pdf['prefix'] == 'ch').sum()
    sh_count = (pdf['prefix'] == 'sh').sum()
    metrics['ch_sh_ratio'] = ch_count / max(ch_count + sh_count, 1)

    ok_count = (pdf['prefix'] == 'ok').sum()
    ot_count = (pdf['prefix'] == 'ot').sum()
    metrics['ok_ot_ratio'] = ok_count / max(ok_count + ot_count, 1)

    # Paragraph count
    lines = pdf['line'].unique()
    metrics['n_lines'] = len(lines)
    metrics['tokens_per_line'] = n / max(len(lines), 1)

    # Line length variance (C1425)
    line_lengths = pdf.groupby('line').size()
    metrics['line_length_cv'] = line_lengths.std() / max(line_lengths.mean(), 1) if len(line_lengths) > 1 else 0

    op_metrics[folio] = metrics

op_df = pd.DataFrame(op_metrics).T
print(f"Operational metrics computed for {len(op_df)} folios")
print(f"Metrics: {list(op_df.columns)}")

# === Correlate PCs with Operational Metrics ===

print(f"\n=== PC-Operational Correlations ===")
print("(Only showing |rho| > 0.3 and p < 0.05)")

pc_correlations = {}
common_folios = [f for f in folios if f in op_df.index and f in folio_scores]

for pc_idx in range(min(6, len(pca_results['pca_variance_explained']))):
    pc_name = f'PC{pc_idx+1}'
    var_pct = pca_results['pca_variance_explained'][pc_idx] * 100
    pc_vals = [folio_scores[f][pc_idx] for f in common_folios]

    pc_correlations[pc_name] = {'variance_pct': var_pct, 'correlations': {}}
    sig_corrs = []

    for metric in op_df.columns:
        metric_vals = [op_df.loc[f, metric] for f in common_folios]
        rho, p = spearmanr(pc_vals, metric_vals)
        pc_correlations[pc_name]['correlations'][metric] = {'rho': float(rho), 'p': float(p)}
        if abs(rho) > 0.3 and p < 0.05:
            sig_corrs.append((metric, rho, p))

    if sig_corrs:
        sig_corrs.sort(key=lambda x: abs(x[1]), reverse=True)
        print(f"\n  {pc_name} ({var_pct:.1f}%):")
        for metric, rho, p in sig_corrs:
            print(f"    {metric}: rho={rho:+.3f}, p={p:.4f}")

# === Recipe Cards for Extreme Folios ===

print(f"\n=== Recipe Cards for Extreme Folios ===")

recipe_cards = {}
for pc_idx in range(min(4, len(pca_results['pca_variance_explained']))):
    pc_name = f'PC{pc_idx+1}'
    pc_vals = {f: folio_scores[f][pc_idx] for f in common_folios}

    sorted_folios = sorted(pc_vals, key=pc_vals.get)
    low_folio = sorted_folios[0]
    high_folio = sorted_folios[-1]

    card = {
        'high': {
            'folio': high_folio,
            'score': float(pc_vals[high_folio]),
            'section': sections[high_folio],
        },
        'low': {
            'folio': low_folio,
            'score': float(pc_vals[low_folio]),
            'section': sections[low_folio],
        },
    }

    # Add operational metrics for both extremes
    for endpoint in ['high', 'low']:
        f = card[endpoint]['folio']
        if f in op_df.index:
            card[endpoint]['metrics'] = {k: float(v) for k, v in op_df.loc[f].items()}

    recipe_cards[pc_name] = card

    print(f"\n  {pc_name}:")
    print(f"    HIGH: {high_folio} ({sections[high_folio]}, score={pc_vals[high_folio]:+.2f})")
    print(f"    LOW:  {low_folio} ({sections[low_folio]}, score={pc_vals[low_folio]:+.2f})")

    # Show biggest metric differences
    if high_folio in op_df.index and low_folio in op_df.index:
        diff = op_df.loc[high_folio] - op_df.loc[low_folio]
        top_diff = diff.abs().nlargest(3)
        print(f"    Biggest operational differences:")
        for metric in top_diff.index:
            print(f"      {metric}: {op_df.loc[high_folio, metric]:.4f} vs {op_df.loc[low_folio, metric]:.4f}")

# === Test: Does Freedom Space Predict Apparatus Distance? (C1380) ===

print(f"\n=== Apparatus Distance Prediction ===")

# Build pairwise distance in freedom PC space
from scipy.spatial.distance import pdist, squareform

pc_matrix = np.array([folio_scores[f][:6] for f in common_folios])
freedom_dist = squareform(pdist(pc_matrix, 'euclidean'))

# Build pairwise distance in operational metric space
op_matrix = op_df.loc[common_folios].values
op_dist = squareform(pdist(op_matrix, 'euclidean'))

# Mantel test (correlation of distance matrices)
upper_tri_mask = np.triu_indices(len(common_folios), k=1)
freedom_flat = freedom_dist[upper_tri_mask]
op_flat = op_dist[upper_tri_mask]

rho_mantel, p_mantel = spearmanr(freedom_flat, op_flat)
print(f"  Freedom-space vs operational distance: Mantel rho={rho_mantel:.3f}, p={p_mantel:.6f}")

# Permutation test for Mantel
n_perm = 999
rho_null = []
for _ in range(n_perm):
    perm_idx = np.random.permutation(len(common_folios))
    perm_dist = freedom_dist[np.ix_(perm_idx, perm_idx)]
    perm_flat = perm_dist[upper_tri_mask]
    rho_null.append(spearmanr(perm_flat, op_flat)[0])

p_perm = (sum(r >= rho_mantel for r in rho_null) + 1) / (n_perm + 1)
print(f"  Permutation p-value: {p_perm:.4f}")

# === Redundancy Check Against C1715 / C1367 ===

print(f"\n=== Novelty Assessment ===")
print("Comparing atom-level PCs to known category-level structures:")
print(f"  C1715: PC1=PREFIX/kernel (32%), PC2=suffix/complexity (17%)")
print(f"  C1367: Accent PC1=category composition, PC2=sequential complexity")

# Test: how much of operational variance do atom PCs capture vs category-level features?
# Use k_ratio, e_ratio, thermal_ratio as proxies for C1715 category features
category_proxies = ['k_ratio', 'e_ratio', 'thermal_ratio', 'ch_sh_ratio']
available_proxies = [c for c in category_proxies if c in op_df.columns]

if available_proxies:
    cat_matrix = op_df.loc[common_folios, available_proxies].values
    cat_dist = squareform(pdist(cat_matrix, 'euclidean'))
    cat_flat = cat_dist[upper_tri_mask]

    rho_cat, _ = spearmanr(cat_flat, op_flat)
    print(f"\n  Category-proxy vs operational distance: rho={rho_cat:.3f}")
    print(f"  Atom-level vs operational distance:     rho={rho_mantel:.3f}")
    print(f"  Atom advantage: {rho_mantel - rho_cat:+.3f}")

    # Partial correlation: atom PCs vs operational AFTER controlling category
    rho_partial_num = rho_mantel - rho_cat * spearmanr(freedom_flat, cat_flat)[0]
    print(f"  (Partial correlation estimate: {rho_partial_num:.3f})")

# === Save Results ===

results = {
    'n_folios': len(common_folios),
    'n_operational_metrics': len(op_df.columns),
    'metric_names': list(op_df.columns),
    'pc_correlations': pc_correlations,
    'recipe_cards': recipe_cards,
    'mantel_test': {
        'rho': float(rho_mantel),
        'p_parametric': float(p_mantel),
        'p_permutation': float(p_perm),
        'n_permutations': n_perm,
    },
    'operational_metrics': {f: {k: float(v) for k, v in row.items()} for f, row in op_df.iterrows()},
}

with open(RESULTS / '04_operational_meaning.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / '04_operational_meaning.json'}")
print("Done.")
