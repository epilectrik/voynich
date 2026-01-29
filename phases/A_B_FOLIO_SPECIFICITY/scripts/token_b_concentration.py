#!/usr/bin/env python3
"""
Whole-Token-to-B-Folio Concentration Analysis

Same as middle_b_concentration.py but using whole PP tokens (words)
instead of MIDDLEs. For each A folio's PP token vocabulary, measure
how concentrated those tokens are across B folios.
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
print("Whole-Token-to-B-Folio Concentration Analysis")
print("=" * 70)

# ============================================================
# Load data
# ============================================================
print("\n--- Loading data ---")

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# Build per-A-folio PP token sets (whole words)
print("Building A folio PP token sets...")
a_folios = sorted(analyzer.get_folios())
a_folio_tokens = {}  # A folio -> set of PP word forms

for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    tokens = set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                tokens.add(t.word)
    a_folio_tokens[fol] = tokens

print(f"  {len(a_folios)} A folios")
all_pp_tokens = set()
for s in a_folio_tokens.values():
    all_pp_tokens.update(s)
print(f"  {len(all_pp_tokens)} unique PP tokens across all A folios")

a_pool_sizes = [len(a_folio_tokens[f]) for f in a_folios]
print(f"  A token pool sizes: median={np.median(a_pool_sizes):.0f}, "
      f"mean={np.mean(a_pool_sizes):.1f}, min={np.min(a_pool_sizes)}, max={np.max(a_pool_sizes)}")

# Build per-B-folio token usage
print("Building B folio token usage...")
b_folio_tokens = defaultdict(set)  # B folio -> set of word types
b_token_to_folios = defaultdict(set)  # token -> set of B folios

for token in tx.currier_b():
    w = token.word
    b_folio_tokens[token.folio].add(w)
    b_token_to_folios[w].add(token.folio)

b_folios = sorted(b_folio_tokens.keys())
n_b = len(b_folios)
print(f"  {n_b} B folios")

all_b_tokens = set()
for s in b_folio_tokens.values():
    all_b_tokens.update(s)
print(f"  {len(all_b_tokens)} unique tokens in B")

shared_tokens = all_pp_tokens & all_b_tokens
print(f"  {len(shared_tokens)} shared (PP tokens that appear in B)")

# ============================================================
# T1: Per-token B-folio membership
# ============================================================
print("\n--- T1: Per-Token B-folio Membership ---")

tok_b_counts = []
for tok in sorted(shared_tokens):
    tok_b_counts.append(len(b_token_to_folios[tok]))

tok_b_counts = np.array(tok_b_counts)
print(f"Shared tokens: {len(tok_b_counts)}")
print(f"B folios per token:")
print(f"  Mean: {np.mean(tok_b_counts):.1f}")
print(f"  Median: {np.median(tok_b_counts):.0f}")
print(f"  Min: {np.min(tok_b_counts)}")
print(f"  Max: {np.max(tok_b_counts)}")
print(f"  Std: {np.std(tok_b_counts):.1f}")

print(f"  1 B folio only: {np.sum(tok_b_counts == 1)} ({np.sum(tok_b_counts == 1)/len(tok_b_counts)*100:.1f}%)")
print(f"  2-5 B folios: {np.sum((tok_b_counts >= 2) & (tok_b_counts <= 5))} ({np.sum((tok_b_counts >= 2) & (tok_b_counts <= 5))/len(tok_b_counts)*100:.1f}%)")
print(f"  6-20 B folios: {np.sum((tok_b_counts >= 6) & (tok_b_counts <= 20))} ({np.sum((tok_b_counts >= 6) & (tok_b_counts <= 20))/len(tok_b_counts)*100:.1f}%)")
print(f"  21-50 B folios: {np.sum((tok_b_counts >= 21) & (tok_b_counts <= 50))} ({np.sum((tok_b_counts >= 21) & (tok_b_counts <= 50))/len(tok_b_counts)*100:.1f}%)")
print(f"  51-82 B folios: {np.sum(tok_b_counts >= 51)} ({np.sum(tok_b_counts >= 51)/len(tok_b_counts)*100:.1f}%)")

# ============================================================
# T2: Per-A-folio token concentration across B folios
# ============================================================
print("\n--- T2: Per-A-folio Token Concentration ---")

b_folio_idx = {f: i for i, f in enumerate(b_folios)}

a_herfindahl = []
a_effective_b = []
a_top3_share = []
a_gini = []

for a_fol in a_folios:
    toks = a_folio_tokens[a_fol] & shared_tokens
    if not toks:
        a_herfindahl.append(1.0)
        a_effective_b.append(1)
        a_top3_share.append(1.0)
        a_gini.append(1.0)
        continue

    # Count how many of this A folio's tokens appear on each B folio
    b_hits = np.zeros(n_b)
    for tok in toks:
        for b_fol in b_token_to_folios[tok]:
            if b_fol in b_folio_idx:
                b_hits[b_folio_idx[b_fol]] += 1

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

    sorted_fracs = np.sort(fracs)[::-1]
    a_top3_share.append(np.sum(sorted_fracs[:3]))

    sorted_hits = np.sort(b_hits)
    n = len(sorted_hits)
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_hits) - (n + 1) * np.sum(sorted_hits)) / (n * np.sum(sorted_hits))
    a_gini.append(gini)

a_herfindahl = np.array(a_herfindahl)
a_effective_b = np.array(a_effective_b)
a_top3_share = np.array(a_top3_share)
a_gini = np.array(a_gini)

print(f"Herfindahl index per A folio:")
print(f"  Mean: {np.mean(a_herfindahl):.4f}")
print(f"  Median: {np.median(a_herfindahl):.4f}")
print(f"  (Uniform across {n_b} would give H={1/n_b:.4f})")

print(f"\nEffective number of B folios (1/H):")
print(f"  Mean: {np.mean(a_effective_b):.1f}")
print(f"  Median: {np.median(a_effective_b):.1f}")
print(f"  Min: {np.min(a_effective_b):.1f}")
print(f"  Max: {np.max(a_effective_b):.1f}")
print(f"  (Maximum possible: {n_b})")

print(f"\nTop-3 B folio share:")
print(f"  Mean: {np.mean(a_top3_share):.4f}")
print(f"  Median: {np.median(a_top3_share):.4f}")
print(f"  (Uniform: {3/n_b:.4f})")

print(f"\nGini coefficient:")
print(f"  Mean: {np.mean(a_gini):.4f}")
print(f"  Median: {np.median(a_gini):.4f}")

# ============================================================
# T3: Affinity matrix (token-level)
# ============================================================
print("\n--- T3: A-folio B-folio Token Affinity ---")

n_a = len(a_folios)
affinity = np.zeros((n_a, n_b))

for i, a_fol in enumerate(a_folios):
    toks = a_folio_tokens[a_fol] & shared_tokens
    if not toks:
        continue
    for j, b_fol in enumerate(b_folios):
        overlap = len(toks & b_folio_tokens[b_fol])
        affinity[i, j] = overlap / len(toks)

print(f"Token affinity matrix: {affinity.shape}")
print(f"  Mean: {np.mean(affinity):.4f}")
print(f"  Median: {np.median(affinity):.4f}")
print(f"  Min: {np.min(affinity):.4f}")
print(f"  Max: {np.max(affinity):.4f}")

# Per-A-folio best B
a_best = affinity.max(axis=1)
a_mean = affinity.mean(axis=1)
a_lift = a_best / np.where(a_mean > 0, a_mean, 1)

print(f"\nPer-A-folio:")
print(f"  Mean best affinity: {np.mean(a_best):.4f}")
print(f"  Mean of means: {np.mean(a_mean):.4f}")
print(f"  Mean lift: {np.mean(a_lift):.3f}x")
print(f"  Max lift: {np.max(a_lift):.3f}x")

# B folios with high overlap
a_b_above_25 = np.sum(affinity > 0.25, axis=1)
a_b_above_50 = np.sum(affinity > 0.50, axis=1)

print(f"\nB folios with >25% of A's tokens:")
print(f"  Mean: {np.mean(a_b_above_25):.1f}, Median: {np.median(a_b_above_25):.0f}")
print(f"B folios with >50% of A's tokens:")
print(f"  Mean: {np.mean(a_b_above_50):.1f}, Median: {np.median(a_b_above_50):.0f}")

# Variance decomposition
total_var = np.var(affinity)
var_by_a = np.var(affinity.mean(axis=1, keepdims=True))
var_by_b = np.var(affinity.mean(axis=0, keepdims=True))
residual_var = total_var - var_by_a - var_by_b

print(f"\nToken affinity variance decomposition:")
print(f"  Total: {total_var:.6f}")
print(f"  A folio: {var_by_a:.6f} ({var_by_a/total_var*100:.1f}%)")
print(f"  B folio: {var_by_b:.6f} ({var_by_b/total_var*100:.1f}%)")
print(f"  Residual: {residual_var:.6f} ({residual_var/total_var*100:.1f}%)")

# ============================================================
# T4: Permutation test
# ============================================================
print("\n--- T4: Permutation Test ---")

rng = np.random.RandomState(42)
shared_list = sorted(shared_tokens)
n_shared = len(shared_list)

# Pre-compute B-folio hit vectors per token
tok_b_vectors = {}
for tok in shared_list:
    vec = np.zeros(n_b)
    for b_fol in b_token_to_folios[tok]:
        if b_fol in b_folio_idx:
            vec[b_folio_idx[b_fol]] = 1
    tok_b_vectors[tok] = vec

obs_mean_eff_b = np.mean(a_effective_b)
obs_mean_herf = np.mean(a_herfindahl)

n_perm = 1000
null_mean_eff_b = []
a_shared_sizes = [len(a_folio_tokens[f] & shared_tokens) for f in a_folios]

for p in range(n_perm):
    perm_eff_b = []
    for pool_size in a_shared_sizes:
        if pool_size == 0:
            perm_eff_b.append(1)
            continue
        sample_idx = rng.choice(n_shared, size=min(pool_size, n_shared), replace=False)
        b_hits = np.zeros(n_b)
        for idx in sample_idx:
            b_hits += tok_b_vectors[shared_list[idx]]
        total = b_hits.sum()
        if total == 0:
            perm_eff_b.append(1)
            continue
        fracs = b_hits / total
        h = np.sum(fracs ** 2)
        perm_eff_b.append(1.0 / h)
    null_mean_eff_b.append(np.mean(perm_eff_b))

null_mean_eff_b = np.array(null_mean_eff_b)

# Correct interpretation:
# observed eff_b > null eff_b => observed is MORE diffuse
# observed eff_b < null eff_b => observed is MORE concentrated
p_more_diffuse = np.mean(null_mean_eff_b >= obs_mean_eff_b)  # null as diffuse or more
p_more_concentrated = np.mean(null_mean_eff_b <= obs_mean_eff_b)  # null as concentrated or more

print(f"Observed mean effective-B: {obs_mean_eff_b:.2f}")
print(f"Null mean effective-B: {np.mean(null_mean_eff_b):.2f} +/- {np.std(null_mean_eff_b):.2f}")
print(f"p(observed more diffuse than null): {p_more_diffuse:.4f}")
print(f"p(observed more concentrated than null): {p_more_concentrated:.4f}")

if obs_mean_eff_b < np.mean(null_mean_eff_b) and p_more_concentrated < 0.05:
    verdict = "CONCENTRATED"
    desc = "A folio tokens point to FEWER B folios than random"
elif obs_mean_eff_b > np.mean(null_mean_eff_b) and p_more_diffuse < 0.05:
    verdict = "DIFFUSE"
    desc = "A folio tokens spread across MORE B folios than random"
else:
    verdict = "RANDOM"
    desc = "A folio token distribution matches random draw"

print(f"\nVerdict: {verdict}")
print(f"  {desc}")

# ============================================================
# T5: Token narrowness distribution
# ============================================================
print("\n--- T5: Token Breadth in B ---")

singleton_b = np.sum(tok_b_counts == 1)
print(f"Shared tokens on exactly 1 B folio: {singleton_b} ({singleton_b/len(tok_b_counts)*100:.1f}%)")
print(f"Shared tokens on <= 3 B folios: {np.sum(tok_b_counts <= 3)} ({np.sum(tok_b_counts <= 3)/len(tok_b_counts)*100:.1f}%)")
print(f"Shared tokens on >= 41 B folios (50%+): {np.sum(tok_b_counts >= 41)} ({np.sum(tok_b_counts >= 41)/len(tok_b_counts)*100:.1f}%)")

# Per-A-folio: what fraction of its shared tokens are B-narrow (<=5)?
a_narrow_frac = []
for a_fol in a_folios:
    toks = a_folio_tokens[a_fol] & shared_tokens
    if not toks:
        a_narrow_frac.append(0)
        continue
    narrow = sum(1 for t in toks if len(b_token_to_folios[t]) <= 5)
    a_narrow_frac.append(narrow / len(toks))

print(f"\nPer-A-folio fraction of B-narrow tokens (<=5 B folios):")
print(f"  Mean: {np.mean(a_narrow_frac):.4f}")
print(f"  Median: {np.median(a_narrow_frac):.4f}")

# ============================================================
# Comparison: MIDDLE vs Token level
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON: MIDDLE vs WHOLE TOKEN")
print("=" * 70)

print(f"\n{'Metric':<45} {'MIDDLE':>10} {'TOKEN':>10}")
print("-" * 65)
print(f"{'Shared vocabulary size':<45} {'389':>10} {len(shared_tokens):>10}")
print(f"{'Median B folios per item':<45} {'3':>10} {np.median(tok_b_counts):.0f}{'':>4}")
print(f"{'Items on 1-5 B folios':<45} {'59.1%':>10} {np.sum(tok_b_counts <= 5)/len(tok_b_counts)*100:.1f}%{'':>4}")
print(f"{'Effective B folios per A folio':<45} {'79.2':>10} {np.mean(a_effective_b):.1f}{'':>4}")
print(f"{'Mean Gini':<45} {'0.106':>10} {np.mean(a_gini):.3f}{'':>4}")
print(f"{'Mean affinity':<45} {'0.554':>10} {np.mean(affinity):.3f}{'':>4}")
print(f"{'B folios >50% overlap':<45} {'51.7':>10} {np.mean(a_b_above_50):.1f}{'':>4}")
print(f"{'Variance: A folio explains':<45} {'25.4%':>10} {var_by_a/total_var*100:.1f}%{'':>4}")
print(f"{'Variance: B folio explains':<45} {'59.4%':>10} {var_by_b/total_var*100:.1f}%{'':>4}")
print(f"{'Permutation verdict':<45} {'DIFFUSE':>10} {verdict:>10}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\nAt whole-token level:")
print(f"  Shared tokens: {len(shared_tokens)}")
print(f"  Median B-folio breadth per token: {np.median(tok_b_counts):.0f}")
print(f"  Effective B folios per A folio: {np.mean(a_effective_b):.1f} / {n_b}")
print(f"  Mean token affinity: {np.mean(affinity):.4f}")
print(f"  Permutation: {verdict} ({desc})")

# Save results
results = {
    'metadata': {
        'phase': 'A_B_FOLIO_SPECIFICITY',
        'analysis': 'token_b_concentration',
        'timestamp': datetime.now().isoformat(),
        'n_a_folios': n_a,
        'n_b_folios': n_b,
        'n_shared_tokens': len(shared_tokens),
        'n_pp_tokens': len(all_pp_tokens),
        'n_b_tokens': len(all_b_tokens),
    },
    'T1_token_breadth': {
        'mean_b_folios_per_token': float(np.mean(tok_b_counts)),
        'median': float(np.median(tok_b_counts)),
        'min': int(np.min(tok_b_counts)),
        'max': int(np.max(tok_b_counts)),
        'pct_1_5': float(np.sum(tok_b_counts <= 5) / len(tok_b_counts) * 100),
        'pct_singleton': float(np.sum(tok_b_counts == 1) / len(tok_b_counts) * 100),
    },
    'T2_concentration': {
        'mean_herfindahl': float(np.mean(a_herfindahl)),
        'uniform_herfindahl': float(1 / n_b),
        'mean_effective_b': float(np.mean(a_effective_b)),
        'median_effective_b': float(np.median(a_effective_b)),
        'mean_gini': float(np.mean(a_gini)),
        'mean_top3_share': float(np.mean(a_top3_share)),
    },
    'T3_affinity': {
        'mean_affinity': float(np.mean(affinity)),
        'mean_best': float(np.mean(a_best)),
        'mean_lift': float(np.mean(a_lift)),
        'mean_b_above_25pct': float(np.mean(a_b_above_25)),
        'mean_b_above_50pct': float(np.mean(a_b_above_50)),
        'variance_by_a_pct': float(var_by_a / total_var * 100),
        'variance_by_b_pct': float(var_by_b / total_var * 100),
    },
    'T4_permutation': {
        'observed_mean_eff_b': float(obs_mean_eff_b),
        'null_mean_eff_b': float(np.mean(null_mean_eff_b)),
        'null_std': float(np.std(null_mean_eff_b)),
        'p_more_diffuse': float(p_more_diffuse),
        'p_more_concentrated': float(p_more_concentrated),
        'verdict': verdict,
    },
}

out_path = RESULTS_DIR / 'token_b_concentration.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {out_path}")
print("DONE")
