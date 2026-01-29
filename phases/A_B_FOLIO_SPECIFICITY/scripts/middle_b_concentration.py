#!/usr/bin/env python3
"""
MIDDLE-to-B-Folio Concentration Analysis

For each A folio's PP MIDDLE pool, measure how concentrated those MIDDLEs
are across B folios. Are A folio MIDDLEs used by a few specific B programs
or spread across all of them?

Tests:
  T1: Per-MIDDLE B-folio membership (how many B folios use each MIDDLE?)
  T2: Per-A-folio MIDDLE concentration (do an A folio's MIDDLEs cluster
      into specific B folios?)
  T3: A-folio B-folio affinity (does each A folio have a "target" set of
      B folios that use most of its MIDDLEs?)
  T4: Permutation test (is concentration greater than expected from
      MIDDLE frequency alone?)
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
print("MIDDLE-to-B-Folio Concentration Analysis")
print("=" * 70)

# ============================================================
# Load data
# ============================================================
print("\n--- Loading data ---")

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

morph_cache = {}
def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

# Build per-A-folio PP MIDDLE pools
print("Building A folio PP pools...")
a_folios = sorted(analyzer.get_folios())
a_folio_mids = {}  # A folio -> set of PP MIDDLEs

for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    mids = set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
    a_folio_mids[fol] = mids

print(f"  {len(a_folios)} A folios")

# Build per-B-folio MIDDLE usage
print("Building B folio MIDDLE usage...")
b_folio_mids = defaultdict(set)  # B folio -> set of MIDDLEs used
b_mid_to_folios = defaultdict(set)  # MIDDLE -> set of B folios using it
b_mid_token_count = defaultdict(lambda: defaultdict(int))  # MIDDLE -> B folio -> count

for token in tx.currier_b():
    w = token.word
    m = get_morph(w)
    if m.middle:
        b_folio_mids[token.folio].add(m.middle)
        b_mid_to_folios[m.middle].add(token.folio)
        b_mid_token_count[m.middle][token.folio] += 1

b_folios = sorted(b_folio_mids.keys())
n_b = len(b_folios)
print(f"  {n_b} B folios")

all_b_mids = set()
for s in b_folio_mids.values():
    all_b_mids.update(s)
print(f"  {len(all_b_mids)} unique MIDDLEs in B")

# All PP MIDDLEs across A
all_pp_mids = set()
for s in a_folio_mids.values():
    all_pp_mids.update(s)
print(f"  {len(all_pp_mids)} unique PP MIDDLEs in A")

shared_mids = all_pp_mids & all_b_mids
print(f"  {len(shared_mids)} shared (PP MIDDLEs that appear in B)")

# ============================================================
# T1: Per-MIDDLE B-folio membership
# ============================================================
print("\n--- T1: Per-MIDDLE B-folio Membership ---")

# For shared MIDDLEs: how many B folios use each?
mid_b_counts = []
for mid in sorted(shared_mids):
    mid_b_counts.append(len(b_mid_to_folios[mid]))

mid_b_counts = np.array(mid_b_counts)
print(f"Shared MIDDLEs: {len(mid_b_counts)}")
print(f"B folios per MIDDLE:")
print(f"  Mean: {np.mean(mid_b_counts):.1f}")
print(f"  Median: {np.median(mid_b_counts):.0f}")
print(f"  Min: {np.min(mid_b_counts)}")
print(f"  Max: {np.max(mid_b_counts)}")
print(f"  Std: {np.std(mid_b_counts):.1f}")

# Distribution
print(f"  1-5 B folios: {np.sum(mid_b_counts <= 5)} ({np.sum(mid_b_counts <= 5)/len(mid_b_counts)*100:.1f}%)")
print(f"  6-20 B folios: {np.sum((mid_b_counts >= 6) & (mid_b_counts <= 20))} ({np.sum((mid_b_counts >= 6) & (mid_b_counts <= 20))/len(mid_b_counts)*100:.1f}%)")
print(f"  21-50 B folios: {np.sum((mid_b_counts >= 21) & (mid_b_counts <= 50))} ({np.sum((mid_b_counts >= 21) & (mid_b_counts <= 50))/len(mid_b_counts)*100:.1f}%)")
print(f"  51-82 B folios: {np.sum(mid_b_counts >= 51)} ({np.sum(mid_b_counts >= 51)/len(mid_b_counts)*100:.1f}%)")

# ============================================================
# T2: Per-A-folio MIDDLE concentration across B folios
# ============================================================
print("\n--- T2: Per-A-folio MIDDLE Concentration ---")

# For each A folio: its PP MIDDLEs -> which B folios use them?
# Measure: Herfindahl index of B-folio "hits" per A folio
# High Herfindahl = concentrated (few B folios get most hits)
# Low Herfindahl = diffuse (hits spread across many B folios)

b_folio_idx = {f: i for i, f in enumerate(b_folios)}

a_herfindahl = []
a_effective_b = []  # effective number of B folios (1/H)
a_top3_share = []   # fraction of total hits in top 3 B folios
a_gini = []

for a_fol in a_folios:
    mids = a_folio_mids[a_fol] & shared_mids
    if not mids:
        a_herfindahl.append(1.0)
        a_effective_b.append(1)
        a_top3_share.append(1.0)
        a_gini.append(1.0)
        continue

    # Count how many of this A folio's MIDDLEs appear on each B folio
    b_hits = np.zeros(n_b)
    for mid in mids:
        for b_fol in b_mid_to_folios[mid]:
            if b_fol in b_folio_idx:
                b_hits[b_folio_idx[b_fol]] += 1

    # Normalize to fractions
    total = b_hits.sum()
    if total == 0:
        a_herfindahl.append(1.0)
        a_effective_b.append(1)
        a_top3_share.append(1.0)
        a_gini.append(1.0)
        continue

    fracs = b_hits / total
    h = np.sum(fracs ** 2)
    a_herfindahl.append(h)
    a_effective_b.append(1.0 / h)

    # Top 3 share
    sorted_fracs = np.sort(fracs)[::-1]
    a_top3_share.append(np.sum(sorted_fracs[:3]))

    # Gini coefficient
    sorted_hits = np.sort(b_hits)
    n = len(sorted_hits)
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_hits) - (n + 1) * np.sum(sorted_hits)) / (n * np.sum(sorted_hits))
    a_gini.append(gini)

a_herfindahl = np.array(a_herfindahl)
a_effective_b = np.array(a_effective_b)
a_top3_share = np.array(a_top3_share)
a_gini = np.array(a_gini)

print(f"Herfindahl index (concentration) per A folio:")
print(f"  Mean: {np.mean(a_herfindahl):.4f}")
print(f"  Median: {np.median(a_herfindahl):.4f}")
print(f"  (Uniform across {n_b} B folios would give H={1/n_b:.4f})")

print(f"\nEffective number of B folios (1/H):")
print(f"  Mean: {np.mean(a_effective_b):.1f}")
print(f"  Median: {np.median(a_effective_b):.1f}")
print(f"  Min: {np.min(a_effective_b):.1f}")
print(f"  Max: {np.max(a_effective_b):.1f}")
print(f"  (Maximum possible: {n_b})")

print(f"\nTop-3 B folio share of MIDDLE hits:")
print(f"  Mean: {np.mean(a_top3_share):.4f}")
print(f"  Median: {np.median(a_top3_share):.4f}")
print(f"  (Uniform would give: {3/n_b:.4f})")

print(f"\nGini coefficient (inequality of B-folio hits):")
print(f"  Mean: {np.mean(a_gini):.4f}")
print(f"  Median: {np.median(a_gini):.4f}")
print(f"  (0 = perfectly equal, 1 = maximally concentrated)")

# ============================================================
# T3: A-folio affinity matrix (MIDDLE-level)
# ============================================================
print("\n--- T3: A-folio B-folio Affinity ---")

# Build affinity matrix: for each (A, B) pair, what fraction of A's PP MIDDLEs
# appear on B?
n_a = len(a_folios)
affinity = np.zeros((n_a, n_b))

for i, a_fol in enumerate(a_folios):
    mids = a_folio_mids[a_fol] & shared_mids
    if not mids:
        continue
    for j, b_fol in enumerate(b_folios):
        overlap = len(mids & b_folio_mids[b_fol])
        affinity[i, j] = overlap / len(mids)

print(f"Affinity matrix shape: {affinity.shape}")
print(f"  Mean affinity: {np.mean(affinity):.4f}")
print(f"  Median: {np.median(affinity):.4f}")
print(f"  Min: {np.min(affinity):.4f}")
print(f"  Max: {np.max(affinity):.4f}")

# Per-A-folio: best B folio affinity vs mean
a_best_affinity = affinity.max(axis=1)
a_mean_affinity = affinity.mean(axis=1)
a_affinity_lift = a_best_affinity / np.where(a_mean_affinity > 0, a_mean_affinity, 1)

print(f"\nPer-A-folio best B affinity:")
print(f"  Mean best: {np.mean(a_best_affinity):.4f}")
print(f"  Mean of means: {np.mean(a_mean_affinity):.4f}")
print(f"  Mean lift (best/mean): {np.mean(a_affinity_lift):.3f}x")
print(f"  Max lift: {np.max(a_affinity_lift):.3f}x")

# Per-A-folio: how many B folios have >50% of this A's MIDDLEs?
a_b_above_50 = np.sum(affinity > 0.5, axis=1)
a_b_above_75 = np.sum(affinity > 0.75, axis=1)
print(f"\nB folios with >50% of A's MIDDLEs:")
print(f"  Mean: {np.mean(a_b_above_50):.1f}")
print(f"  Median: {np.median(a_b_above_50):.0f}")
print(f"  Min: {np.min(a_b_above_50)}")
print(f"  Max: {np.max(a_b_above_50)}")

print(f"\nB folios with >75% of A's MIDDLEs:")
print(f"  Mean: {np.mean(a_b_above_75):.1f}")
print(f"  Median: {np.median(a_b_above_75):.0f}")
print(f"  Min: {np.min(a_b_above_75)}")
print(f"  Max: {np.max(a_b_above_75)}")

# Variance decomposition of affinity matrix
total_var = np.var(affinity)
row_means = affinity.mean(axis=1, keepdims=True)
var_by_a = np.var(row_means)
col_means = affinity.mean(axis=0, keepdims=True)
var_by_b = np.var(col_means)
residual_var = total_var - var_by_a - var_by_b

print(f"\nAffinity variance decomposition:")
print(f"  Total: {total_var:.6f}")
print(f"  A folio: {var_by_a:.6f} ({var_by_a/total_var*100:.1f}%)")
print(f"  B folio: {var_by_b:.6f} ({var_by_b/total_var*100:.1f}%)")
print(f"  Residual: {residual_var:.6f} ({residual_var/total_var*100:.1f}%)")

# ============================================================
# T4: Permutation test - is concentration greater than expected?
# ============================================================
print("\n--- T4: Permutation Test ---")

# Null: each A folio draws its MIDDLEs randomly from the shared pool.
# The B-folio distribution of those MIDDLEs would reflect overall MIDDLE
# frequency, not A-folio-specific targeting.

rng = np.random.RandomState(42)
shared_mids_list = sorted(shared_mids)
n_shared = len(shared_mids_list)

# Pre-compute: for each shared MIDDLE, its B-folio hit vector
mid_b_vectors = {}
for mid in shared_mids_list:
    vec = np.zeros(n_b)
    for b_fol in b_mid_to_folios[mid]:
        if b_fol in b_folio_idx:
            vec[b_folio_idx[b_fol]] = 1
    mid_b_vectors[mid] = vec

# Observed: mean effective-B across A folios
obs_mean_eff_b = np.mean(a_effective_b)
obs_mean_herf = np.mean(a_herfindahl)

# Null distribution: for each A folio, draw same number of MIDDLEs
# uniformly from shared pool, compute effective-B
n_perm = 1000
null_mean_eff_b = []
null_mean_herf = []

a_pool_sizes = [len(a_folio_mids[f] & shared_mids) for f in a_folios]

for p in range(n_perm):
    perm_eff_b = []
    perm_herf = []
    for pool_size in a_pool_sizes:
        if pool_size == 0:
            perm_eff_b.append(1)
            perm_herf.append(1.0)
            continue
        # Draw random MIDDLEs
        sample_idx = rng.choice(n_shared, size=min(pool_size, n_shared), replace=False)
        b_hits = np.zeros(n_b)
        for idx in sample_idx:
            b_hits += mid_b_vectors[shared_mids_list[idx]]
        total = b_hits.sum()
        if total == 0:
            perm_eff_b.append(1)
            perm_herf.append(1.0)
            continue
        fracs = b_hits / total
        h = np.sum(fracs ** 2)
        perm_herf.append(h)
        perm_eff_b.append(1.0 / h)
    null_mean_eff_b.append(np.mean(perm_eff_b))
    null_mean_herf.append(np.mean(perm_herf))

null_mean_eff_b = np.array(null_mean_eff_b)
null_mean_herf = np.array(null_mean_herf)

# Is observed MORE concentrated (lower effective-B) than null?
p_more_concentrated = np.mean(null_mean_eff_b >= obs_mean_eff_b)
# Is observed LESS concentrated (higher effective-B) than null?
p_less_concentrated = np.mean(null_mean_eff_b <= obs_mean_eff_b)

print(f"Observed mean effective-B: {obs_mean_eff_b:.2f}")
print(f"Null mean effective-B: {np.mean(null_mean_eff_b):.2f} +/- {np.std(null_mean_eff_b):.2f}")
print(f"p(more concentrated than null): {p_more_concentrated:.4f}")
print(f"p(less concentrated than null): {p_less_concentrated:.4f}")

print(f"\nObserved mean Herfindahl: {obs_mean_herf:.5f}")
print(f"Null mean Herfindahl: {np.mean(null_mean_herf):.5f} +/- {np.std(null_mean_herf):.5f}")

if p_more_concentrated < 0.05:
    conc_verdict = "CONCENTRATED"
    conc_desc = "A folio MIDDLEs are MORE concentrated in specific B folios than random"
elif p_less_concentrated < 0.05:
    conc_verdict = "DIFFUSE"
    conc_desc = "A folio MIDDLEs are MORE spread across B folios than random"
else:
    conc_verdict = "RANDOM"
    conc_desc = "A folio MIDDLE distribution across B folios matches random draw"

print(f"\nVerdict: {conc_verdict}")
print(f"  {conc_desc}")

# ============================================================
# T5: Individual MIDDLE breadth vs A-folio concentration
# ============================================================
print("\n--- T5: MIDDLE Breadth Distribution ---")

# Are most shared MIDDLEs narrow (few B folios) or broad (many)?
print(f"How broad are shared MIDDLEs in B?")
broad_mids = [mid for mid in shared_mids if len(b_mid_to_folios[mid]) >= n_b * 0.5]
narrow_mids = [mid for mid in shared_mids if len(b_mid_to_folios[mid]) <= 5]
print(f"  Broad (>= 50% of B folios): {len(broad_mids)} ({len(broad_mids)/len(shared_mids)*100:.1f}%)")
print(f"  Narrow (<= 5 B folios): {len(narrow_mids)} ({len(narrow_mids)/len(shared_mids)*100:.1f}%)")

# For each A folio: what fraction of its MIDDLEs are broad vs narrow?
a_broad_frac = []
a_narrow_frac = []
broad_set = set(broad_mids)
narrow_set = set(narrow_mids)
for a_fol in a_folios:
    mids = a_folio_mids[a_fol] & shared_mids
    if not mids:
        a_broad_frac.append(0)
        a_narrow_frac.append(0)
        continue
    a_broad_frac.append(len(mids & broad_set) / len(mids))
    a_narrow_frac.append(len(mids & narrow_set) / len(mids))

print(f"\nPer-A-folio composition:")
print(f"  Mean broad fraction: {np.mean(a_broad_frac):.4f}")
print(f"  Mean narrow fraction: {np.mean(a_narrow_frac):.4f}")

# Does narrow fraction predict concentration?
from scipy.stats import spearmanr
r_s, p_s = spearmanr(a_narrow_frac, a_herfindahl)
print(f"\nNarrow MIDDLE fraction vs Herfindahl:")
print(f"  Spearman rho={r_s:.4f}, p={p_s:.2e}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nShared MIDDLEs appear on median {np.median(mid_b_counts):.0f} B folios (of {n_b})")
print(f"A folio MIDDLEs reach effective {np.mean(a_effective_b):.1f} B folios (of {n_b})")
print(f"Mean affinity (fraction of A's MIDDLEs on each B folio): {np.mean(affinity):.4f}")
print(f"Concentration verdict: {conc_verdict}")
print(f"  {conc_desc}")

# ============================================================
# Save results
# ============================================================
results = {
    'metadata': {
        'phase': 'A_B_FOLIO_SPECIFICITY',
        'analysis': 'middle_b_concentration',
        'timestamp': datetime.now().isoformat(),
        'n_a_folios': n_a,
        'n_b_folios': n_b,
        'n_shared_middles': len(shared_mids),
        'n_pp_middles': len(all_pp_mids),
        'n_b_middles': len(all_b_mids),
    },
    'T1_middle_breadth': {
        'mean_b_folios_per_middle': float(np.mean(mid_b_counts)),
        'median': float(np.median(mid_b_counts)),
        'min': int(np.min(mid_b_counts)),
        'max': int(np.max(mid_b_counts)),
    },
    'T2_concentration': {
        'mean_herfindahl': float(np.mean(a_herfindahl)),
        'median_herfindahl': float(np.median(a_herfindahl)),
        'uniform_herfindahl': float(1 / n_b),
        'mean_effective_b': float(np.mean(a_effective_b)),
        'median_effective_b': float(np.median(a_effective_b)),
        'mean_top3_share': float(np.mean(a_top3_share)),
        'mean_gini': float(np.mean(a_gini)),
    },
    'T3_affinity': {
        'mean_affinity': float(np.mean(affinity)),
        'mean_best_affinity': float(np.mean(a_best_affinity)),
        'mean_lift': float(np.mean(a_affinity_lift)),
        'variance_by_a_pct': float(var_by_a / total_var * 100),
        'variance_by_b_pct': float(var_by_b / total_var * 100),
        'mean_b_above_50pct': float(np.mean(a_b_above_50)),
        'mean_b_above_75pct': float(np.mean(a_b_above_75)),
    },
    'T4_permutation': {
        'observed_mean_eff_b': float(obs_mean_eff_b),
        'null_mean_eff_b': float(np.mean(null_mean_eff_b)),
        'null_std_eff_b': float(np.std(null_mean_eff_b)),
        'p_more_concentrated': float(p_more_concentrated),
        'p_less_concentrated': float(p_less_concentrated),
        'verdict': conc_verdict,
    },
    'T5_breadth': {
        'n_broad': len(broad_mids),
        'n_narrow': len(narrow_mids),
        'narrow_vs_herf_rho': float(r_s),
        'narrow_vs_herf_p': float(p_s),
    },
}

out_path = RESULTS_DIR / 'middle_b_concentration.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {out_path}")
print("DONE")
