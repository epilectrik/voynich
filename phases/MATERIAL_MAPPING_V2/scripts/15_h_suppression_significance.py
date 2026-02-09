"""
15_h_suppression_significance.py

Test statistical significance of h-suppression in PRECISION PP vs baseline B.

Finding: PRECISION PP shows h=0.052 vs baseline h=0.097 (0.53x)
Question: Is this difference significant?

OPTIMIZED: Pre-compute per-MIDDLE stats, then sample from those.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("H-SUPPRESSION SIGNIFICANCE TEST")
print("="*70)

# Load PRECISION PP
with open(results_dir / "precision_analysis.json") as f:
    precision_data = json.load(f)

para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

# Get validated candidates
candidates = precision_data['precision_candidates']
validated = [c for c in candidates if c['kernels']['k'] + c['kernels']['e'] > 2 * c['kernels']['h']]

# Extract PP MIDDLEs
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

precision_pp = set()
for v in validated:
    para_id = v['para_id']
    tokens = para_tokens.get(para_id, [])
    for t in tokens:
        word = t.get('word', '')
        if not word or '*' in word:
            continue
        try:
            m = morph.extract(word)
            if m.middle and m.middle in pp_middles:
                precision_pp.add(m.middle)
        except:
            pass

print(f"PRECISION PP MIDDLEs: {len(precision_pp)}")

# Load B tokens and PRE-COMPUTE per-MIDDLE stats
print("\nPre-computing per-MIDDLE statistics...")
tx = Transcript()
b_tokens = list(tx.currier_b())

# Per-MIDDLE: count of tokens, count with h, count with k or e
middle_stats = defaultdict(lambda: {'total': 0, 'h': 0, 'ke': 0})

for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            middle_stats[m.middle]['total'] += 1
            if 'h' in m.middle:
                middle_stats[m.middle]['h'] += 1
            if 'k' in m.middle or 'e' in m.middle:
                middle_stats[m.middle]['ke'] += 1
    except:
        pass

print(f"Unique PP MIDDLEs in B: {len(middle_stats)}")

# Compute PRECISION h-rate by summing pre-computed stats
precision_h = sum(middle_stats[m]['h'] for m in precision_pp if m in middle_stats)
precision_total = sum(middle_stats[m]['total'] for m in precision_pp if m in middle_stats)
precision_ke = sum(middle_stats[m]['ke'] for m in precision_pp if m in middle_stats)

precision_h_rate = precision_h / precision_total if precision_total > 0 else 0
precision_ke_rate = precision_ke / precision_total if precision_total > 0 else 0

print(f"\nPRECISION PP in B: {precision_total} tokens")
print(f"  h_rate = {precision_h_rate:.4f}")
print(f"  k+e_rate = {precision_ke_rate:.4f}")

# Compute baseline
baseline_h = sum(s['h'] for s in middle_stats.values())
baseline_total = sum(s['total'] for s in middle_stats.values())
baseline_ke = sum(s['ke'] for s in middle_stats.values())

baseline_h_rate = baseline_h / baseline_total if baseline_total > 0 else 0
baseline_ke_rate = baseline_ke / baseline_total if baseline_total > 0 else 0

print(f"\nBaseline (all PP in B): {baseline_total} tokens")
print(f"  h_rate = {baseline_h_rate:.4f}")
print(f"  k+e_rate = {baseline_ke_rate:.4f}")

print(f"\nRatios:")
print(f"  h: {precision_h_rate / baseline_h_rate:.3f}x")
print(f"  k+e: {precision_ke_rate / baseline_ke_rate:.3f}x")

# Permutation test - OPTIMIZED: sample from pre-computed stats
print("\n" + "="*70)
print("PERMUTATION TEST (optimized)")
print("="*70)
print("H0: PRECISION PP has same h-rate as random PP sample of same size")

all_pp_list = list(middle_stats.keys())
n_sample = len([m for m in precision_pp if m in middle_stats])  # Only count those in B

n_permutations = 10000
perm_h_rates = []

for i in range(n_permutations):
    # Random sample of same size
    sample = random.sample(all_pp_list, min(n_sample, len(all_pp_list)))

    # Sum pre-computed stats
    sample_h = sum(middle_stats[m]['h'] for m in sample)
    sample_total = sum(middle_stats[m]['total'] for m in sample)

    if sample_total > 0:
        perm_h_rates.append(sample_h / sample_total)

# Compute p-value
n_lower = sum(1 for r in perm_h_rates if r <= precision_h_rate)
p_value = n_lower / len(perm_h_rates)

mean_perm = sum(perm_h_rates) / len(perm_h_rates)
std_perm = (sum((r - mean_perm)**2 for r in perm_h_rates) / len(perm_h_rates)) ** 0.5
effect_size = (mean_perm - precision_h_rate) / std_perm if std_perm > 0 else 0

print(f"\nPermutation results (n={n_permutations}):")
print(f"  Mean random h-rate: {mean_perm:.4f}")
print(f"  Std random h-rate: {std_perm:.4f}")
print(f"  PRECISION h-rate: {precision_h_rate:.4f}")
print(f"  p-value (one-tailed, lower): {p_value:.4f}")
print(f"  Effect size (Cohen's d): {effect_size:.2f}")

if p_value < 0.05:
    print(f"\n  *** SIGNIFICANT at p < 0.05 ***")
    print(f"  PRECISION PP has significantly LOWER h-rate than random PP")
elif p_value < 0.10:
    print(f"\n  Marginally significant (0.05 < p < 0.10)")
else:
    print(f"\n  NOT significant at p < 0.05")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

kernel_test = precision_ke_rate > 2 * precision_h_rate

print(f"""
H-SUPPRESSION:
  PRECISION: h = {precision_h_rate:.4f}
  Baseline:  h = {baseline_h_rate:.4f}
  Ratio: {precision_h_rate/baseline_h_rate:.2f}x ({(1-precision_h_rate/baseline_h_rate)*100:.0f}% reduction)
  p-value: {p_value:.4f}
  Effect size: {effect_size:.2f}
  Verdict: {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}

K+E RATE:
  PRECISION: k+e = {precision_ke_rate:.4f}
  Baseline:  k+e = {baseline_ke_rate:.4f}
  Ratio: {precision_ke_rate/baseline_ke_rate:.2f}x

KERNEL SIGNATURE (k+e > 2h):
  PRECISION: {precision_ke_rate:.4f} > 2 * {precision_h_rate:.4f} = {2*precision_h_rate:.4f}
  Test: {'PASS' if kernel_test else 'FAIL'}
""")

# Save results
results = {
    'precision_h_rate': precision_h_rate,
    'baseline_h_rate': baseline_h_rate,
    'h_ratio': precision_h_rate / baseline_h_rate if baseline_h_rate > 0 else 0,
    'p_value': p_value,
    'effect_size': effect_size,
    'significant': p_value < 0.05,
    'precision_ke_rate': precision_ke_rate,
    'baseline_ke_rate': baseline_ke_rate,
    'kernel_test_pass': kernel_test
}

with open(results_dir / "h_suppression_significance.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"Saved to h_suppression_significance.json")
