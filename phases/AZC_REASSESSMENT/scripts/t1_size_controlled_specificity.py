"""
T1: Size-Controlled Content Specificity

H0: After controlling pool size, A content has no predictive power for B folio match
H1: Content-specific PP composition predicts B match beyond size effects

Method: Partial correlation of PP Jaccard similarity with B coverage, controlling for pool size
Threshold: partial r > 0.15 and p < 0.01 to support H1
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=== T1: SIZE-CONTROLLED CONTENT SPECIFICITY ===\n")

# Build A folio PP pools
print("Building A folio data...")
a_folio_middles = {}
a_folio_tokens = {}

a_data = defaultdict(list)
for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    a_data[t.folio].append(w)

for fol in sorted(a_data.keys()):
    mids = set()
    tokens = set()
    for w in a_data[fol]:
        tokens.add(w)
        m = morph.extract(w)
        if m.middle:
            mids.add(m.middle)
    a_folio_middles[fol] = mids
    a_folio_tokens[fol] = tokens

# Collect B folio tokens and their MIDDLEs
b_folio_tokens = defaultdict(list)
b_folio_middles = {}
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    b_folio_tokens[t.folio].append(w)

for fol in b_folio_tokens:
    mids = set()
    for w in b_folio_tokens[fol]:
        m = morph.extract(w)
        if m.middle:
            mids.add(m.middle)
    b_folio_middles[fol] = mids

a_folios = sorted(a_folio_middles.keys())
b_folios = sorted(b_folio_tokens.keys())

print(f"  {len(a_folios)} A folios, {len(b_folios)} B folios")

# Compute coverage matrix (component-level for consistency with prior work)
print("\nComputing coverage matrix...")
b_folio_morphs = {}
for b_fol in b_folios:
    b_folio_morphs[b_fol] = [morph.extract(w) for w in b_folio_tokens[b_fol]]

# Build full component pools for A
a_folio_components = {}
for fol in a_folios:
    mids, prefs, sufs = set(), set(), set()
    for w in a_data[fol]:
        m = morph.extract(w)
        if m.middle:
            mids.add(m.middle)
            if m.prefix:
                prefs.add(m.prefix)
            if m.suffix:
                sufs.add(m.suffix)
    a_folio_components[fol] = (mids, prefs, sufs)

coverage = np.zeros((len(a_folios), len(b_folios)))
for i, a_fol in enumerate(a_folios):
    a_m, a_p, a_s = a_folio_components[a_fol]
    for j, b_fol in enumerate(b_folios):
        tokens = b_folio_tokens[b_fol]
        morphs = b_folio_morphs[b_fol]
        legal = 0
        for w, mo in zip(tokens, morphs):
            if mo.middle and mo.middle in a_m:
                if (not mo.prefix or mo.prefix in a_p):
                    if (not mo.suffix or mo.suffix in a_s):
                        legal += 1
        coverage[i, j] = legal / len(tokens) if tokens else 0

# Compute Jaccard similarity between each A folio pair's MIDDLE sets
print("Computing pairwise Jaccard similarities...")
n_a = len(a_folios)
jaccard_matrix = np.zeros((n_a, n_a))
for i in range(n_a):
    for j in range(n_a):
        set_i = a_folio_middles[a_folios[i]]
        set_j = a_folio_middles[a_folios[j]]
        if len(set_i | set_j) > 0:
            jaccard_matrix[i, j] = len(set_i & set_j) / len(set_i | set_j)
        else:
            jaccard_matrix[i, j] = 0

# Pool sizes
pool_sizes = np.array([len(a_folio_middles[f]) for f in a_folios])

# For each B folio, test whether content similarity (Jaccard) predicts coverage
# after controlling for pool size
print("\nTesting partial correlations for each B folio...")

partial_rs = []
partial_ps = []

for j, b_fol in enumerate(b_folios):
    cov_col = coverage[:, j]

    # For this B folio, compute:
    # - Correlation of (A pool size) with (A coverage of this B)
    # - Correlation of (A-A Jaccard to best-match) with (A coverage of this B), controlling for size

    # Find best-match A folio
    best_i = np.argmax(cov_col)

    # Jaccard similarity of each A folio to the best-match
    jaccard_to_best = jaccard_matrix[:, best_i]

    # Partial correlation: coverage ~ jaccard_to_best | pool_size
    # Using residual method

    # Regress coverage on pool_size
    slope_c, intercept_c, _, _, _ = stats.linregress(pool_sizes, cov_col)
    resid_cov = cov_col - (slope_c * pool_sizes + intercept_c)

    # Regress jaccard on pool_size
    slope_j, intercept_j, _, _, _ = stats.linregress(pool_sizes, jaccard_to_best)
    resid_jac = jaccard_to_best - (slope_j * pool_sizes + intercept_j)

    # Correlation of residuals
    r_partial, p_partial = stats.pearsonr(resid_cov, resid_jac)

    partial_rs.append(r_partial)
    partial_ps.append(p_partial)

partial_rs = np.array(partial_rs)
partial_ps = np.array(partial_ps)

# Summary statistics
print("\n=== RESULTS ===\n")

print(f"Partial correlation (coverage ~ Jaccard_to_best | pool_size):")
print(f"  Mean partial r: {np.mean(partial_rs):.4f}")
print(f"  Median partial r: {np.median(partial_rs):.4f}")
print(f"  Std partial r: {np.std(partial_rs):.4f}")
print(f"  Min partial r: {np.min(partial_rs):.4f}")
print(f"  Max partial r: {np.max(partial_rs):.4f}")

sig_count = np.sum((np.abs(partial_rs) > 0.15) & (partial_ps < 0.01))
print(f"\nB folios with |partial r| > 0.15 AND p < 0.01: {sig_count}/{len(b_folios)}")

# Also compute global partial correlation using all A-B pairs
print("\n--- Global Analysis ---")

# Flatten to all A-B pairs
all_coverages = coverage.flatten()
all_pool_sizes = np.tile(pool_sizes, len(b_folios))

# For global Jaccard, compute mean Jaccard to B folio's MIDDLE set
all_jaccards = []
for j, b_fol in enumerate(b_folios):
    b_mids = b_folio_middles[b_fol]
    for i, a_fol in enumerate(a_folios):
        a_mids = a_folio_middles[a_fol]
        if len(a_mids | b_mids) > 0:
            jac = len(a_mids & b_mids) / len(a_mids | b_mids)
        else:
            jac = 0
        all_jaccards.append(jac)

all_jaccards = np.array(all_jaccards)

# Raw correlations
r_size_cov, p_size_cov = stats.pearsonr(all_pool_sizes, all_coverages)
r_jac_cov, p_jac_cov = stats.pearsonr(all_jaccards, all_coverages)
r_size_jac, p_size_jac = stats.pearsonr(all_pool_sizes, all_jaccards)

print(f"Raw correlations (all A-B pairs, n={len(all_coverages)}):")
print(f"  Pool size vs coverage: r={r_size_cov:.4f}, p={p_size_cov:.2e}")
print(f"  A-B Jaccard vs coverage: r={r_jac_cov:.4f}, p={p_jac_cov:.2e}")
print(f"  Pool size vs A-B Jaccard: r={r_size_jac:.4f}, p={p_size_jac:.2e}")

# Partial correlation: coverage ~ Jaccard | pool_size (global)
slope_gc, intercept_gc, _, _, _ = stats.linregress(all_pool_sizes, all_coverages)
resid_cov_global = all_coverages - (slope_gc * all_pool_sizes + intercept_gc)

slope_gj, intercept_gj, _, _, _ = stats.linregress(all_pool_sizes, all_jaccards)
resid_jac_global = all_jaccards - (slope_gj * all_pool_sizes + intercept_gj)

r_partial_global, p_partial_global = stats.pearsonr(resid_cov_global, resid_jac_global)

print(f"\nGlobal partial correlation (coverage ~ A-B Jaccard | pool_size):")
print(f"  Partial r: {r_partial_global:.4f}")
print(f"  p-value: {p_partial_global:.2e}")

# Verdict
threshold_r = 0.15
threshold_p = 0.01

if r_partial_global > threshold_r and p_partial_global < threshold_p:
    verdict = "CONTENT_SIGNAL"
    explanation = f"Global partial r={r_partial_global:.3f} > 0.15 with p < 0.01: content predicts coverage beyond size"
elif r_partial_global > 0.05 and p_partial_global < 0.05:
    verdict = "WEAK_SIGNAL"
    explanation = f"Partial r={r_partial_global:.3f} shows weak content signal, not meeting threshold"
else:
    verdict = "NO_SIGNAL"
    explanation = f"Partial r={r_partial_global:.3f} shows no content signal beyond size"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Save results
results = {
    'test': 'T1_size_controlled_specificity',
    'per_b_folio': {
        'mean_partial_r': float(np.mean(partial_rs)),
        'median_partial_r': float(np.median(partial_rs)),
        'std_partial_r': float(np.std(partial_rs)),
        'significant_count': int(sig_count),
        'total_b_folios': len(b_folios),
    },
    'global': {
        'n_pairs': len(all_coverages),
        'raw_size_coverage_r': float(r_size_cov),
        'raw_jaccard_coverage_r': float(r_jac_cov),
        'raw_size_jaccard_r': float(r_size_jac),
        'partial_r': float(r_partial_global),
        'partial_p': float(p_partial_global),
    },
    'threshold': {
        'r': threshold_r,
        'p': threshold_p,
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't1_size_controlled_specificity.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
