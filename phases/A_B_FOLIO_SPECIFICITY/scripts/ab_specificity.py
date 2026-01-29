#!/usr/bin/env python3
"""
A_B_FOLIO_SPECIFICITY - A-to-B Folio Coverage Analysis

For each of 114 A folios, compute its C502.a survivor set (which B tokens
it makes legal), then measure how well that survivor set covers each of
83 B folios' actual vocabulary.

Core question: Do A folios serve specific B folios (routing architecture)
or do all A folios cover all B folios roughly equally (flat relationship)?

Tests:
  T1: Coverage matrix statistics (114 x 83)
  T2: A-folio variance decomposition (how much does coverage vary by A folio?)
  T3: B-folio variance decomposition (how much does coverage vary by B folio?)
  T4: A-folio clustering (do A folios group by which B folios they serve?)
  T5: Best-match specificity (is each B folio's best A folio much better than average?)

Dependencies:
  - scripts/voynich.py (Transcript, Morphology, RecordAnalyzer)
  - phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json (RI/PP)

Output: results/ab_specificity.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("A_B_FOLIO_SPECIFICITY - A-to-B Folio Coverage Analysis")
print("=" * 70)

# ============================================================
# SECTION 1: Load & Pre-compute
# ============================================================
print("\n--- Section 1: Load & Pre-compute ---")

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

morph_cache = {}
def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

# ============================================================
# Build per-A-folio PP pools
# ============================================================
print("Building per-A-folio PP pools...")
a_folios = sorted(analyzer.get_folios())
a_folio_pp = {}  # folio -> (mids, prefs, sufs)

for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    mids, prefs, sufs = set(), set(), set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                m = get_morph(t.word)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
    a_folio_pp[fol] = (mids, prefs, sufs)

print(f"  {len(a_folios)} A folios processed")

# Summary stats for A PP pools
a_pool_sizes = [len(mids) for mids, _, _ in a_folio_pp.values()]
print(f"  A PP MIDDLE pool sizes: median={np.median(a_pool_sizes):.0f}, "
      f"mean={np.mean(a_pool_sizes):.1f}, min={np.min(a_pool_sizes)}, max={np.max(a_pool_sizes)}")

# ============================================================
# Build B token inventory with morphology
# ============================================================
print("\nBuilding B token inventory...")
b_tokens = {}  # word -> (prefix, middle, suffix)
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = get_morph(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)
print(f"  {len(b_tokens)} unique B token types with morphology")

# ============================================================
# Build per-B-folio token vocabularies
# ============================================================
print("Building per-B-folio token vocabularies...")
b_folio_vocab = defaultdict(set)  # folio -> set of word types
b_folio_token_counts = defaultdict(int)  # folio -> total token count

for token in tx.currier_b():
    w = token.word
    if w in b_tokens:  # only tokens with valid morphology
        b_folio_vocab[token.folio].add(w)
        b_folio_token_counts[token.folio] += 1

b_folios = sorted(b_folio_vocab.keys())
print(f"  {len(b_folios)} B folios")

b_vocab_sizes = [len(b_folio_vocab[f]) for f in b_folios]
print(f"  B folio vocab sizes: median={np.median(b_vocab_sizes):.0f}, "
      f"mean={np.mean(b_vocab_sizes):.1f}, min={np.min(b_vocab_sizes)}, max={np.max(b_vocab_sizes)}")

# ============================================================
# Compute per-A-folio legal B token sets (C502.a filtering)
# ============================================================
print("\nComputing per-A-folio legal B token sets...")
a_folio_legal = {}  # A folio -> set of legal B tokens

for fol in a_folios:
    mids, prefs, sufs = a_folio_pp[fol]
    shared_mids = mids & b_middles_set
    shared_prefs = prefs & b_prefixes_set
    shared_sufs = sufs & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            if (pref is None or pref in shared_prefs):
                if (suf is None or suf in shared_sufs):
                    legal.add(tok)
    a_folio_legal[fol] = legal

legal_sizes = [len(a_folio_legal[f]) for f in a_folios]
print(f"  Legal set sizes: median={np.median(legal_sizes):.0f}, "
      f"mean={np.mean(legal_sizes):.1f}, min={np.min(legal_sizes)}, max={np.max(legal_sizes)}")

# ============================================================
# SECTION 2: Build Coverage Matrix (114 x 83)
# ============================================================
print("\n--- Section 2: Coverage Matrix ---")

# coverage[i][j] = fraction of B folio j's vocabulary that is legal under A folio i
n_a = len(a_folios)
n_b = len(b_folios)
coverage = np.zeros((n_a, n_b))

for i, a_fol in enumerate(a_folios):
    legal = a_folio_legal[a_fol]
    for j, b_fol in enumerate(b_folios):
        vocab = b_folio_vocab[b_fol]
        if len(vocab) == 0:
            coverage[i, j] = 0.0
        else:
            coverage[i, j] = len(legal & vocab) / len(vocab)

print(f"Coverage matrix shape: {coverage.shape}")
print(f"  Overall mean coverage: {np.mean(coverage):.4f}")
print(f"  Overall median: {np.median(coverage):.4f}")
print(f"  Overall min: {np.min(coverage):.4f}")
print(f"  Overall max: {np.max(coverage):.4f}")
print(f"  Overall std: {np.std(coverage):.4f}")

# ============================================================
# T1: Coverage Matrix Statistics
# ============================================================
print("\n--- T1: Coverage Matrix Statistics ---")

# Per-A-folio: mean coverage across all B folios
a_mean_cov = coverage.mean(axis=1)
print(f"\nPer-A-folio mean coverage across B folios:")
print(f"  Mean of means: {np.mean(a_mean_cov):.4f}")
print(f"  Std of means: {np.std(a_mean_cov):.4f}")
print(f"  Min A folio mean: {a_folios[np.argmin(a_mean_cov)]} = {np.min(a_mean_cov):.4f}")
print(f"  Max A folio mean: {a_folios[np.argmax(a_mean_cov)]} = {np.max(a_mean_cov):.4f}")
print(f"  Range: {np.max(a_mean_cov) - np.min(a_mean_cov):.4f}")

# Per-B-folio: mean coverage across all A folios
b_mean_cov = coverage.mean(axis=0)
print(f"\nPer-B-folio mean coverage across A folios:")
print(f"  Mean of means: {np.mean(b_mean_cov):.4f}")
print(f"  Std of means: {np.std(b_mean_cov):.4f}")
print(f"  Min B folio mean: {b_folios[np.argmin(b_mean_cov)]} = {np.min(b_mean_cov):.4f}")
print(f"  Max B folio mean: {b_folios[np.argmax(b_mean_cov)]} = {np.max(b_mean_cov):.4f}")
print(f"  Range: {np.max(b_mean_cov) - np.min(b_mean_cov):.4f}")

# ============================================================
# T2: Variance Decomposition
# ============================================================
print("\n--- T2: Variance Decomposition ---")

total_var = np.var(coverage)
# Variance explained by A folio (row effect)
row_means = coverage.mean(axis=1, keepdims=True)
var_by_a = np.var(row_means)
# Variance explained by B folio (column effect)
col_means = coverage.mean(axis=0, keepdims=True)
var_by_b = np.var(col_means)
# Residual (interaction)
residual_var = total_var - var_by_a - var_by_b

print(f"Total variance: {total_var:.6f}")
print(f"Variance explained by A folio: {var_by_a:.6f} ({var_by_a / total_var * 100:.1f}%)")
print(f"Variance explained by B folio: {var_by_b:.6f} ({var_by_b / total_var * 100:.1f}%)")
print(f"Residual (interaction): {residual_var:.6f} ({residual_var / total_var * 100:.1f}%)")

# Key interpretation: if var_by_a >> var_by_b, A folios differ more than
# B folios in their coverage patterns -> different A folios make different
# amounts of B vocabulary legal. If var_by_b >> var_by_a, some B folios
# are inherently more accessible than others regardless of A folio.

# ============================================================
# T3: A-folio Specificity - Column Variance per A folio
# ============================================================
print("\n--- T3: A-folio Specificity (does each A folio serve some B folios better?) ---")

# For each A folio: variance across B folios
a_col_var = coverage.var(axis=1)  # per A folio, variance across B folios
print(f"Per-A-folio coverage variance across B folios:")
print(f"  Mean: {np.mean(a_col_var):.6f}")
print(f"  Std: {np.std(a_col_var):.6f}")

# If A folios are specific (routing), each A folio should have HIGH variance
# across B folios (some B folios well-covered, others poorly).
# If flat, variance should be LOW.

# Compare to null: if all A folios produced identical coverage profiles,
# the only variance would be from B folio characteristics.
# Null = variance of overall B column means
null_col_var = np.var(b_mean_cov)
print(f"Null (B-only) column variance: {null_col_var:.6f}")
print(f"Mean observed per-A variance: {np.mean(a_col_var):.6f}")
print(f"Ratio (observed / null): {np.mean(a_col_var) / null_col_var:.3f}x")

# If ratio ~ 1.0, A folios don't add specificity beyond B folio baseline
# If ratio >> 1.0, A folios are specific to certain B folios

# ============================================================
# T4: Correlation Structure - Do A folios cluster?
# ============================================================
print("\n--- T4: A-folio Clustering ---")

# Compute pairwise correlation between A folio coverage profiles
# (each A folio is a 83-dimensional vector of B-folio coverages)
# High correlation = two A folios cover the same B folios similarly
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import fcluster, linkage

# Z-score normalize each A folio's coverage profile to focus on relative pattern
a_profiles = coverage.copy()
for i in range(n_a):
    mu = a_profiles[i].mean()
    sd = a_profiles[i].std()
    if sd > 0:
        a_profiles[i] = (a_profiles[i] - mu) / sd
    else:
        a_profiles[i] = 0.0

# Correlation distance
corr_dists = pdist(a_profiles, metric='correlation')
mean_corr = 1.0 - np.mean(corr_dists)
print(f"Mean pairwise correlation between A folio profiles: {mean_corr:.4f}")
print(f"  (1.0 = identical profiles, 0.0 = uncorrelated, -1.0 = opposite)")

# If mean_corr ~ 1.0, all A folios produce nearly identical B coverage patterns -> flat
# If mean_corr < 0.7, there are distinct A folio "types" -> potential routing

# Hierarchical clustering
Z = linkage(corr_dists, method='ward')

# Test different cluster numbers
from scipy.stats import f_oneway

best_k = 1
best_f = 0
for k in [2, 3, 4, 5, 6, 8, 10]:
    labels = fcluster(Z, k, criterion='maxclust')
    # ANOVA: does cluster membership predict mean coverage?
    groups = [a_mean_cov[labels == c] for c in range(1, k + 1) if np.sum(labels == c) > 0]
    if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
        f_stat, p_val = f_oneway(*groups)
        if f_stat > best_f:
            best_f = f_stat
            best_k = k
        if k <= 6:
            print(f"  k={k}: F={f_stat:.2f}, p={p_val:.4f}, sizes={[len(g) for g in groups]}")

print(f"\n  Best k={best_k} (F={best_f:.2f})")

# Report cluster characteristics for k=best_k
if best_k > 1:
    labels = fcluster(Z, best_k, criterion='maxclust')
    for c in range(1, best_k + 1):
        mask = labels == c
        n_members = np.sum(mask)
        mean_cov_cluster = np.mean(a_mean_cov[mask])
        pool_sizes_cluster = np.array(a_pool_sizes)[mask]
        print(f"  Cluster {c}: n={n_members}, mean_cov={mean_cov_cluster:.4f}, "
              f"mean_pool={np.mean(pool_sizes_cluster):.1f}")

# ============================================================
# T5: Best-Match Specificity
# ============================================================
print("\n--- T5: Best-Match Specificity ---")

# For each B folio: which A folio gives best coverage? How much better than average?
best_a_per_b = []
for j in range(n_b):
    col = coverage[:, j]
    best_idx = np.argmax(col)
    best_cov = col[best_idx]
    mean_cov = col.mean()
    std_cov = col.std()
    best_a_per_b.append({
        'b_folio': b_folios[j],
        'best_a': a_folios[best_idx],
        'best_coverage': float(best_cov),
        'mean_coverage': float(mean_cov),
        'std_coverage': float(std_cov),
        'z_score': float((best_cov - mean_cov) / std_cov) if std_cov > 0 else 0.0,
        'lift': float(best_cov / mean_cov) if mean_cov > 0 else 0.0
    })

z_scores = [x['z_score'] for x in best_a_per_b]
lifts = [x['lift'] for x in best_a_per_b]
print(f"Best-match z-scores: mean={np.mean(z_scores):.3f}, max={np.max(z_scores):.3f}")
print(f"Best-match lifts: mean={np.mean(lifts):.3f}, max={np.max(lifts):.3f}")
print(f"  (lift = best_coverage / mean_coverage; >1.5 = strong specificity)")

# How many B folios have a strongly specific A folio?
n_specific = sum(1 for x in best_a_per_b if x['lift'] > 1.2)
print(f"B folios with lift > 1.2: {n_specific}/{n_b} ({n_specific/n_b*100:.1f}%)")
n_very_specific = sum(1 for x in best_a_per_b if x['lift'] > 1.5)
print(f"B folios with lift > 1.5: {n_very_specific}/{n_b} ({n_very_specific/n_b*100:.1f}%)")

# Reverse: for each A folio, which B folio is it best at?
best_b_per_a = []
for i in range(n_a):
    row = coverage[i, :]
    best_idx = np.argmax(row)
    best_cov = row[best_idx]
    mean_cov = row.mean()
    std_cov = row.std()
    best_b_per_a.append({
        'a_folio': a_folios[i],
        'best_b': b_folios[best_idx],
        'best_coverage': float(best_cov),
        'mean_coverage': float(mean_cov),
        'std_coverage': float(std_cov),
        'lift': float(best_cov / mean_cov) if mean_cov > 0 else 0.0
    })

a_lifts = [x['lift'] for x in best_b_per_a]
print(f"\nReverse: A folio best-B-match lifts:")
print(f"  Mean lift: {np.mean(a_lifts):.3f}")
print(f"  Max lift: {np.max(a_lifts):.3f}")

# ============================================================
# T6: Coverage Gap Analysis
# ============================================================
print("\n--- T6: Coverage Gap Analysis ---")

# How many B folios are poorly served (< 50% coverage) by the BEST A folio?
min_best = min(x['best_coverage'] for x in best_a_per_b)
print(f"Worst best-coverage: {min_best:.4f} ({best_a_per_b[np.argmin([x['best_coverage'] for x in best_a_per_b])]['b_folio']})")

# Coverage floor per B folio (worst A folio)
worst_per_b = coverage.min(axis=0)
print(f"Coverage floor (worst A folio per B folio): mean={np.mean(worst_per_b):.4f}, "
      f"min={np.min(worst_per_b):.4f}")

# Coverage ceiling per B folio (best A folio)
best_per_b = coverage.max(axis=0)
print(f"Coverage ceiling (best A folio per B folio): mean={np.mean(best_per_b):.4f}, "
      f"min={np.min(best_per_b):.4f}")

# Gap: best - worst
gap = best_per_b - worst_per_b
print(f"Coverage gap (ceiling - floor): mean={np.mean(gap):.4f}, max={np.max(gap):.4f}")
print(f"  (large gap = A folios are discriminating; small gap = flat)")

# ============================================================
# T7: Union Coverage - How many A folios needed?
# ============================================================
print("\n--- T7: Union Coverage ---")

# If we combine multiple A folios, how fast does coverage saturate?
# Greedy: pick A folio with highest marginal coverage gain at each step

for target_b_idx in range(0, n_b, max(1, n_b // 5)):  # sample 5 B folios
    vocab = b_folio_vocab[b_folios[target_b_idx]]
    remaining = set(vocab)
    used_a = []
    cov_trajectory = []

    available = list(range(n_a))
    while remaining and available:
        best_gain = -1
        best_a_idx = -1
        for a_idx in available:
            gain = len(a_folio_legal[a_folios[a_idx]] & remaining)
            if gain > best_gain:
                best_gain = gain
                best_a_idx = a_idx
        if best_gain == 0:
            break
        remaining -= a_folio_legal[a_folios[best_a_idx]]
        available.remove(best_a_idx)
        used_a.append(a_folios[best_a_idx])
        cov_trajectory.append(1.0 - len(remaining) / len(vocab))

    if cov_trajectory:
        # Find how many A folios to reach 90% and 95%
        n_90 = next((k + 1 for k, c in enumerate(cov_trajectory) if c >= 0.90), len(cov_trajectory))
        n_95 = next((k + 1 for k, c in enumerate(cov_trajectory) if c >= 0.95), len(cov_trajectory))
        n_99 = next((k + 1 for k, c in enumerate(cov_trajectory) if c >= 0.99), len(cov_trajectory))
        final = cov_trajectory[-1] if cov_trajectory else 0
        print(f"  B folio {b_folios[target_b_idx]}: "
              f"90%@{n_90}, 95%@{n_95}, 99%@{n_99}, "
              f"final={final:.4f} ({len(used_a)} A folios)")

# Full analysis: for EVERY B folio, how many A folios to reach 95%?
a_needed_95 = []
a_needed_100 = []
for b_fol in b_folios:
    vocab = b_folio_vocab[b_fol]
    remaining = set(vocab)
    available = list(range(n_a))
    n_used = 0
    reached_95 = False
    while remaining and available:
        best_gain = -1
        best_a_idx = -1
        for a_idx in available:
            gain = len(a_folio_legal[a_folios[a_idx]] & remaining)
            if gain > best_gain:
                best_gain = gain
                best_a_idx = a_idx
        if best_gain == 0:
            break
        remaining -= a_folio_legal[a_folios[best_a_idx]]
        available.remove(best_a_idx)
        n_used += 1
        if not reached_95 and (1.0 - len(remaining) / len(vocab)) >= 0.95:
            a_needed_95.append(n_used)
            reached_95 = True
    if not reached_95:
        a_needed_95.append(n_a + 1)  # never reached
    a_needed_100.append(n_used if not remaining else n_a + 1)

print(f"\nA folios needed to reach 95% coverage per B folio:")
print(f"  Median: {np.median(a_needed_95):.0f}")
print(f"  Mean: {np.mean(a_needed_95):.1f}")
print(f"  Min: {np.min(a_needed_95)}")
print(f"  Max: {np.max(a_needed_95)}")

print(f"\nA folios needed for 100% coverage per B folio:")
print(f"  Median: {np.median(a_needed_100):.0f}")
print(f"  Mean: {np.mean(a_needed_100):.1f}")
print(f"  Min: {np.min(a_needed_100)}")
print(f"  Max: {np.max(a_needed_100)}")

# ============================================================
# T8: Pool Size vs Coverage Correlation
# ============================================================
print("\n--- T8: Pool Size vs Coverage ---")

from scipy.stats import spearmanr, pearsonr

pool_sizes = np.array([len(a_folio_pp[f][0]) for f in a_folios])
mean_covs = a_mean_cov

r_s, p_s = spearmanr(pool_sizes, mean_covs)
r_p, p_p = pearsonr(pool_sizes, mean_covs)
print(f"A pool size vs mean B coverage:")
print(f"  Spearman rho={r_s:.4f}, p={p_s:.2e}")
print(f"  Pearson r={r_p:.4f}, p={p_p:.2e}")
print(f"  (strong positive = larger A pools cover more B vocabulary)")

# Also check: does pool size predict specificity (variance across B folios)?
r_s2, p_s2 = spearmanr(pool_sizes, a_col_var)
print(f"\nA pool size vs coverage variance:")
print(f"  Spearman rho={r_s2:.4f}, p={p_s2:.2e}")

# ============================================================
# T9: Shared vs Unique B Coverage
# ============================================================
print("\n--- T9: Shared vs Unique B Coverage ---")

# How many B tokens are legal under ALL A folios?
universal_legal = set(b_tokens.keys())
for fol in a_folios:
    universal_legal &= a_folio_legal[fol]
print(f"B tokens legal under ALL 114 A folios: {len(universal_legal)} "
      f"({len(universal_legal)/len(b_tokens)*100:.1f}%)")

# B tokens legal under NO A folio
never_legal = set(b_tokens.keys())
for fol in a_folios:
    never_legal -= a_folio_legal[fol]
print(f"B tokens legal under NO A folio: {len(never_legal)} "
      f"({len(never_legal)/len(b_tokens)*100:.1f}%)")

# B tokens legal under at least one A folio
any_legal = set()
for fol in a_folios:
    any_legal |= a_folio_legal[fol]
print(f"B tokens legal under >= 1 A folio: {len(any_legal)} "
      f"({len(any_legal)/len(b_tokens)*100:.1f}%)")

# Distribution: how many A folios make each B token legal?
b_token_a_count = defaultdict(int)
for fol in a_folios:
    for tok in a_folio_legal[fol]:
        b_token_a_count[tok] += 1

counts = np.array([b_token_a_count.get(tok, 0) for tok in b_tokens])
print(f"\nB token accessibility distribution:")
print(f"  Mean A folios: {np.mean(counts):.1f}")
print(f"  Median: {np.median(counts):.0f}")
q25, q75 = np.percentile(counts, [25, 75])
print(f"  Q25: {q25:.0f}, Q75: {q75:.0f}")
print(f"  Tokens accessible from 1-10 A folios: {np.sum((counts >= 1) & (counts <= 10))} "
      f"({np.sum((counts >= 1) & (counts <= 10))/len(counts)*100:.1f}%)")
print(f"  Tokens accessible from 11-50 A folios: {np.sum((counts >= 11) & (counts <= 50))} "
      f"({np.sum((counts >= 11) & (counts <= 50))/len(counts)*100:.1f}%)")
print(f"  Tokens accessible from 51-100 A folios: {np.sum((counts >= 51) & (counts <= 100))} "
      f"({np.sum((counts >= 51) & (counts <= 100))/len(counts)*100:.1f}%)")
print(f"  Tokens accessible from 101-114 A folios: {np.sum(counts >= 101)} "
      f"({np.sum(counts >= 101)/len(counts)*100:.1f}%)")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Determine verdict
if np.mean(a_col_var) / null_col_var < 1.1:
    specificity_verdict = "FLAT"
    specificity_desc = "A folios do not show specificity to particular B folios"
elif np.mean(a_col_var) / null_col_var < 1.5:
    specificity_verdict = "WEAK_SPECIFICITY"
    specificity_desc = "A folios show weak differentiation across B folios"
else:
    specificity_verdict = "ROUTING"
    specificity_desc = "A folios are specific to subsets of B folios (routing architecture)"

coverage_verdict = "HIGH" if np.mean(coverage) > 0.7 else "MODERATE" if np.mean(coverage) > 0.4 else "LOW"

print(f"\nSpecificity: {specificity_verdict} ({np.mean(a_col_var)/null_col_var:.3f}x null)")
print(f"  {specificity_desc}")
print(f"\nMean coverage: {np.mean(coverage):.4f} ({coverage_verdict})")
print(f"A-explained variance: {var_by_a/total_var*100:.1f}%")
print(f"B-explained variance: {var_by_b/total_var*100:.1f}%")
print(f"Mean A-folio pairwise profile correlation: {mean_corr:.4f}")
print(f"B tokens universally legal: {len(universal_legal)}/{len(b_tokens)} ({len(universal_legal)/len(b_tokens)*100:.1f}%)")
print(f"B tokens never legal: {len(never_legal)}/{len(b_tokens)} ({len(never_legal)/len(b_tokens)*100:.1f}%)")

# ============================================================
# Save Results
# ============================================================
results = {
    'metadata': {
        'phase': 'A_B_FOLIO_SPECIFICITY',
        'timestamp': datetime.now().isoformat(),
        'n_a_folios': n_a,
        'n_b_folios': n_b,
        'n_b_token_types': len(b_tokens),
        'seed': 42
    },
    'coverage_matrix': {
        'shape': [n_a, n_b],
        'mean': float(np.mean(coverage)),
        'median': float(np.median(coverage)),
        'std': float(np.std(coverage)),
        'min': float(np.min(coverage)),
        'max': float(np.max(coverage)),
    },
    'T1_statistics': {
        'a_mean_coverage_mean': float(np.mean(a_mean_cov)),
        'a_mean_coverage_std': float(np.std(a_mean_cov)),
        'a_mean_coverage_range': float(np.max(a_mean_cov) - np.min(a_mean_cov)),
        'b_mean_coverage_mean': float(np.mean(b_mean_cov)),
        'b_mean_coverage_std': float(np.std(b_mean_cov)),
        'b_mean_coverage_range': float(np.max(b_mean_cov) - np.min(b_mean_cov)),
    },
    'T2_variance_decomposition': {
        'total_variance': float(total_var),
        'variance_by_a': float(var_by_a),
        'variance_by_b': float(var_by_b),
        'residual_variance': float(residual_var),
        'pct_a': float(var_by_a / total_var * 100),
        'pct_b': float(var_by_b / total_var * 100),
        'pct_residual': float(residual_var / total_var * 100),
    },
    'T3_specificity': {
        'mean_a_col_var': float(np.mean(a_col_var)),
        'null_col_var': float(null_col_var),
        'specificity_ratio': float(np.mean(a_col_var) / null_col_var),
        'verdict': specificity_verdict,
    },
    'T4_clustering': {
        'mean_pairwise_correlation': float(mean_corr),
        'best_k': int(best_k),
        'best_f': float(best_f),
    },
    'T5_best_match': {
        'mean_z_score': float(np.mean(z_scores)),
        'max_z_score': float(np.max(z_scores)),
        'mean_lift': float(np.mean(lifts)),
        'max_lift': float(np.max(lifts)),
        'n_specific_1_2': n_specific,
        'n_very_specific_1_5': n_very_specific,
    },
    'T6_coverage_gap': {
        'mean_floor': float(np.mean(worst_per_b)),
        'mean_ceiling': float(np.mean(best_per_b)),
        'mean_gap': float(np.mean(gap)),
        'max_gap': float(np.max(gap)),
    },
    'T7_union_coverage': {
        'median_a_needed_95': float(np.median(a_needed_95)),
        'mean_a_needed_95': float(np.mean(a_needed_95)),
        'median_a_needed_100': float(np.median(a_needed_100)),
        'mean_a_needed_100': float(np.mean(a_needed_100)),
    },
    'T8_pool_size': {
        'pool_size_vs_coverage_rho': float(r_s),
        'pool_size_vs_coverage_p': float(p_s),
        'pool_size_vs_variance_rho': float(r_s2),
        'pool_size_vs_variance_p': float(p_s2),
    },
    'T9_shared_unique': {
        'universally_legal': len(universal_legal),
        'universally_legal_pct': float(len(universal_legal) / len(b_tokens) * 100),
        'never_legal': len(never_legal),
        'never_legal_pct': float(len(never_legal) / len(b_tokens) * 100),
        'any_legal': len(any_legal),
        'any_legal_pct': float(len(any_legal) / len(b_tokens) * 100),
        'accessibility_mean': float(np.mean(counts)),
        'accessibility_median': float(np.median(counts)),
    },
    'verdict': {
        'specificity': specificity_verdict,
        'coverage_level': coverage_verdict,
        'description': specificity_desc,
    },
    'a_folios': a_folios,
    'b_folios': b_folios,
}

out_path = RESULTS_DIR / 'ab_specificity.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {out_path}")
print("DONE")
