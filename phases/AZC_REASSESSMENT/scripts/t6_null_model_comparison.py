"""
T6: Null Model Comparison

H0: Observed A->B matching is indistinguishable from random vocabulary sharing
H1: Observed matching shows structure beyond random character-level combination

Method: Generate synthetic A folios via random PP combination from observed
        character/morpheme distribution. Compare real vs synthetic A folios'
        ability to discriminate B folios.

Threshold: Real discrimination > 95th percentile of synthetic

This is the ultimate test: if randomly-assembled vocabulary pools work as well
as real A folios, then "routing" is just combinatorial overlap.
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
rng = np.random.RandomState(42)

print("=== T6: NULL MODEL COMPARISON ===\n")

# Build real A folio pools
print("Building real A folio pools...")
a_folio_components = {}
a_folio_section = {}

a_data = defaultdict(list)
for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    a_data[t.folio].append(w)
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

for fol in sorted(a_data.keys()):
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

a_folios = sorted(a_folio_components.keys())

# Collect all PP vocabulary (MIDDLEs shared between A and B)
all_a_middles = set()
all_a_prefixes = set()
all_a_suffixes = set()
for fol in a_folios:
    m, p, s = a_folio_components[fol]
    all_a_middles.update(m)
    all_a_prefixes.update(p)
    all_a_suffixes.update(s)

# Collect B vocabulary
b_folio_tokens = defaultdict(list)
b_folio_section = {}
all_b_middles = set()
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    b_folio_tokens[t.folio].append(w)
    if t.folio not in b_folio_section:
        b_folio_section[t.folio] = t.section
    m = morph.extract(w)
    if m.middle:
        all_b_middles.add(m.middle)

b_folios = sorted(b_folio_tokens.keys())

# Pre-compute B morphologies
b_folio_morphs = {}
for b_fol in b_folios:
    b_folio_morphs[b_fol] = [morph.extract(w) for w in b_folio_tokens[b_fol]]

pp_middles = list(all_a_middles & all_b_middles)
pp_prefixes = list(all_a_prefixes)
pp_suffixes = list(all_a_suffixes)

print(f"  {len(a_folios)} A folios, {len(b_folios)} B folios")
print(f"  PP vocabulary: {len(pp_middles)} MIDDLEs, {len(pp_prefixes)} prefixes, {len(pp_suffixes)} suffixes")

# Get real A folio pool size distribution
real_pool_sizes = [len(a_folio_components[f][0]) for f in a_folios]
print(f"  Real pool sizes: mean={np.mean(real_pool_sizes):.1f}, min={min(real_pool_sizes)}, max={max(real_pool_sizes)}")

def compute_coverage(a_pool, b_fol, b_folio_tokens, b_folio_morphs):
    """Compute coverage of B folio under A pool."""
    a_m, a_p, a_s = a_pool
    tokens = b_folio_tokens[b_fol]
    morphs = b_folio_morphs[b_fol]
    legal = 0
    for w, mo in zip(tokens, morphs):
        if mo.middle and mo.middle in a_m:
            if (not mo.prefix or mo.prefix in a_p):
                if (not mo.suffix or mo.suffix in a_s):
                    legal += 1
    return legal / len(tokens) if tokens else 0

def compute_discrimination(pools, b_folios, b_folio_tokens, b_folio_morphs):
    """Compute mean discrimination ratio across B folios."""
    n_pools = len(pools)
    n_b = len(b_folios)

    disc_ratios = []
    for j, b_fol in enumerate(b_folios):
        coverages = [compute_coverage(pool, b_fol, b_folio_tokens, b_folio_morphs) for pool in pools]
        coverages = np.array(coverages)

        if coverages.max() == 0:
            continue

        ranked = np.argsort(-coverages)
        best_cov = coverages[ranked[0]]
        second_cov = coverages[ranked[1]] if n_pools > 1 else 0

        disc = best_cov / second_cov if second_cov > 0 else 10  # cap at 10
        disc_ratios.append(min(disc, 10))

    return np.mean(disc_ratios) if disc_ratios else 0

# Compute real discrimination
print("\nComputing real A folio discrimination...")
real_pools = [a_folio_components[f] for f in a_folios]
real_disc = compute_discrimination(real_pools, b_folios, b_folio_tokens, b_folio_morphs)
print(f"  Real mean discrimination: {real_disc:.3f}")

# Generate synthetic A folios
print("\nGenerating synthetic A folios...")

n_synthetic_trials = 100
synthetic_discs = []

for trial in range(n_synthetic_trials):
    if trial % 20 == 0:
        print(f"  Trial {trial}/{n_synthetic_trials}...")

    # Create synthetic pools with same size distribution as real
    synthetic_pools = []
    for pool_size in real_pool_sizes:
        # Randomly sample MIDDLEs
        n_mids = pool_size
        n_prefs = min(pool_size // 2 + 1, len(pp_prefixes))
        n_sufs = min(pool_size // 3 + 1, len(pp_suffixes))

        sampled_mids = set(rng.choice(pp_middles, size=min(n_mids, len(pp_middles)), replace=False))
        sampled_prefs = set(rng.choice(pp_prefixes, size=min(n_prefs, len(pp_prefixes)), replace=False))
        sampled_sufs = set(rng.choice(pp_suffixes, size=min(n_sufs, len(pp_suffixes)), replace=False))

        synthetic_pools.append((sampled_mids, sampled_prefs, sampled_sufs))

    # Compute discrimination for synthetic pools
    synth_disc = compute_discrimination(synthetic_pools, b_folios, b_folio_tokens, b_folio_morphs)
    synthetic_discs.append(synth_disc)

synthetic_discs = np.array(synthetic_discs)

print(f"\nSynthetic discrimination distribution:")
print(f"  Mean: {synthetic_discs.mean():.3f}")
print(f"  Std: {synthetic_discs.std():.3f}")
print(f"  5th percentile: {np.percentile(synthetic_discs, 5):.3f}")
print(f"  95th percentile: {np.percentile(synthetic_discs, 95):.3f}")

# Compare real to synthetic
percentile_real = stats.percentileofscore(synthetic_discs, real_disc)
z_score = (real_disc - synthetic_discs.mean()) / synthetic_discs.std() if synthetic_discs.std() > 0 else 0

print(f"\n=== COMPARISON ===")
print(f"  Real discrimination: {real_disc:.3f}")
print(f"  Real percentile in synthetic: {percentile_real:.1f}%")
print(f"  z-score vs synthetic: {z_score:.2f}")

# Also test: unique best-matches
print("\nComputing unique best-match counts...")

def count_unique_matches(pools, b_folios, b_folio_tokens, b_folio_morphs):
    """Count unique pools that are best-match for some B folio."""
    best_match_indices = set()
    for j, b_fol in enumerate(b_folios):
        coverages = [compute_coverage(pool, b_fol, b_folio_tokens, b_folio_morphs) for pool in pools]
        if max(coverages) > 0:
            best_i = np.argmax(coverages)
            best_match_indices.add(best_i)
    return len(best_match_indices)

real_unique = count_unique_matches(real_pools, b_folios, b_folio_tokens, b_folio_morphs)
print(f"  Real unique best-matches: {real_unique}")

synthetic_uniques = []
for trial in range(min(50, n_synthetic_trials)):  # Fewer trials for this metric
    synthetic_pools = []
    for pool_size in real_pool_sizes:
        n_mids = pool_size
        n_prefs = min(pool_size // 2 + 1, len(pp_prefixes))
        n_sufs = min(pool_size // 3 + 1, len(pp_suffixes))

        sampled_mids = set(rng.choice(pp_middles, size=min(n_mids, len(pp_middles)), replace=False))
        sampled_prefs = set(rng.choice(pp_prefixes, size=min(n_prefs, len(pp_prefixes)), replace=False))
        sampled_sufs = set(rng.choice(pp_suffixes, size=min(n_sufs, len(pp_suffixes)), replace=False))

        synthetic_pools.append((sampled_mids, sampled_prefs, sampled_sufs))

    synth_unique = count_unique_matches(synthetic_pools, b_folios, b_folio_tokens, b_folio_morphs)
    synthetic_uniques.append(synth_unique)

synthetic_uniques = np.array(synthetic_uniques)
print(f"  Synthetic unique best-matches: mean={synthetic_uniques.mean():.1f}, std={synthetic_uniques.std():.1f}")

percentile_unique = stats.percentileofscore(synthetic_uniques, real_unique)
print(f"  Real unique percentile in synthetic: {percentile_unique:.1f}%")

# Verdict
threshold_percentile = 95

if percentile_real > threshold_percentile:
    verdict = "REAL_EXCEEDS_SYNTHETIC"
    explanation = f"Real disc ({real_disc:.3f}) > 95th percentile of synthetic: routing has structure beyond random"
elif percentile_real < 5:
    verdict = "REAL_BELOW_SYNTHETIC"
    explanation = f"Real disc ({real_disc:.3f}) < 5th percentile: real A folios are WORSE than random (unexpected)"
else:
    verdict = "INDISTINGUISHABLE"
    explanation = f"Real disc at {percentile_real:.0f}th percentile: indistinguishable from random vocabulary pools"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Additional interpretation
if verdict == "INDISTINGUISHABLE":
    print(f"\n  INTERPRETATION: Real A folios provide no more discriminative power than")
    print(f"  randomly-assembled vocabulary pools of the same size. This suggests")
    print(f"  'routing' is actually 'shared vocabulary with size effects' rather than")
    print(f"  'functional content-specific routing'.")

# Save results
results = {
    'test': 'T6_null_model_comparison',
    'n_a_folios': len(a_folios),
    'n_b_folios': len(b_folios),
    'pp_vocabulary': {
        'middles': len(pp_middles),
        'prefixes': len(pp_prefixes),
        'suffixes': len(pp_suffixes),
    },
    'real_discrimination': float(real_disc),
    'real_unique_matches': int(real_unique),
    'synthetic': {
        'n_trials': n_synthetic_trials,
        'disc_mean': float(synthetic_discs.mean()),
        'disc_std': float(synthetic_discs.std()),
        'disc_5th': float(np.percentile(synthetic_discs, 5)),
        'disc_95th': float(np.percentile(synthetic_discs, 95)),
        'unique_mean': float(synthetic_uniques.mean()),
        'unique_std': float(synthetic_uniques.std()),
    },
    'comparison': {
        'real_disc_percentile': float(percentile_real),
        'real_disc_z': float(z_score),
        'real_unique_percentile': float(percentile_unique),
    },
    'threshold_percentile': threshold_percentile,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't6_null_model_comparison.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
