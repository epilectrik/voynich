"""
T7: Zodiac vs A/C Family B Coverage

Question: Do the two AZC families (Zodiac vs A/C) serve different B folios?

Method:
1. Pool vocabulary within each AZC family
2. Compute B folio coverage by each family
3. Test: are some B folios preferentially served by Zodiac vs A/C?
4. Look for B folio clustering by AZC family affinity
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ZODIAC_FOLIOS = {
    'f72v3', 'f72v2', 'f72v1', 'f72r3', 'f72r2', 'f72r1',
    'f71v', 'f71r', 'f70v2', 'f70v1', 'f73v', 'f73r', 'f57v'
}

# Collect AZC vocabulary by family
print("Collecting AZC vocabulary by family...")

zodiac_middles = set()
ac_middles = set()

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    placement = getattr(token, 'placement', '')
    if placement.startswith('P'):
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    if token.folio in ZODIAC_FOLIOS:
        zodiac_middles.add(m.middle)
    else:
        ac_middles.add(m.middle)

print(f"Zodiac MIDDLEs: {len(zodiac_middles)}")
print(f"A/C MIDDLEs: {len(ac_middles)}")
print(f"Shared: {len(zodiac_middles & ac_middles)}")
print(f"Zodiac-only: {len(zodiac_middles - ac_middles)}")
print(f"A/C-only: {len(ac_middles - zodiac_middles)}")

# Collect B vocabulary by folio
print("\nCollecting B vocabulary...")
b_folio_middles = defaultdict(set)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if m.middle:
        b_folio_middles[token.folio].add(m.middle)

b_folios = sorted(b_folio_middles.keys())
print(f"B folios: {len(b_folios)}")

# Compute B folio coverage by each AZC family
print("\n" + "="*60)
print("B FOLIO COVERAGE BY AZC FAMILY")
print("="*60)

results = {
    'b_folio_stats': {},
    'summary': {},
}

zodiac_coverages = []
ac_coverages = []
coverage_ratios = []

for b_f in b_folios:
    b_vocab = b_folio_middles[b_f]

    # Coverage = fraction of B vocab found in AZC family
    zodiac_cov = len(b_vocab & zodiac_middles) / len(b_vocab) if b_vocab else 0
    ac_cov = len(b_vocab & ac_middles) / len(b_vocab) if b_vocab else 0

    # Ratio: zodiac/ac coverage (>1 = zodiac-preferred, <1 = ac-preferred)
    ratio = zodiac_cov / ac_cov if ac_cov > 0 else float('inf')

    results['b_folio_stats'][b_f] = {
        'vocab_size': len(b_vocab),
        'zodiac_coverage': float(zodiac_cov),
        'ac_coverage': float(ac_cov),
        'coverage_ratio': float(ratio) if ratio != float('inf') else None,
    }

    zodiac_coverages.append(zodiac_cov)
    ac_coverages.append(ac_cov)
    if ratio != float('inf'):
        coverage_ratios.append(ratio)

# Summary stats
print(f"\nOverall B coverage:")
print(f"  Zodiac family: mean={np.mean(zodiac_coverages):.3f} (std={np.std(zodiac_coverages):.3f})")
print(f"  A/C family:    mean={np.mean(ac_coverages):.3f} (std={np.std(ac_coverages):.3f})")

# Paired t-test: do the two families provide different coverage to the same B folios?
t_stat, t_p = stats.ttest_rel(zodiac_coverages, ac_coverages)
print(f"\nPaired t-test (same B folios): t={t_stat:.3f}, p={t_p:.4f}")

# Wilcoxon signed-rank test (non-parametric)
w_stat, w_p = stats.wilcoxon(zodiac_coverages, ac_coverages)
print(f"Wilcoxon signed-rank: W={w_stat:.0f}, p={w_p:.4f}")

# Correlation: does high Zodiac coverage imply high A/C coverage?
corr, corr_p = stats.pearsonr(zodiac_coverages, ac_coverages)
print(f"\nZodiac-A/C coverage correlation: r={corr:.3f}, p={corr_p:.4f}")

# Identify preference patterns
print("\n" + "="*60)
print("B FOLIO PREFERENCE PATTERNS")
print("="*60)

zodiac_preferred = [(b_f, r) for b_f, r in zip(b_folios, coverage_ratios) if r > 1.2]
ac_preferred = [(b_f, r) for b_f, r in zip(b_folios, coverage_ratios) if r < 0.8]
balanced = [(b_f, r) for b_f, r in zip(b_folios, coverage_ratios) if 0.8 <= r <= 1.2]

print(f"Zodiac-preferred (ratio > 1.2): {len(zodiac_preferred)} B folios")
print(f"A/C-preferred (ratio < 0.8): {len(ac_preferred)} B folios")
print(f"Balanced (0.8-1.2): {len(balanced)} B folios")

if zodiac_preferred:
    print(f"\nTop 5 Zodiac-preferred B folios:")
    for b_f, r in sorted(zodiac_preferred, key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {b_f}: ratio={r:.2f}")

if ac_preferred:
    print(f"\nTop 5 A/C-preferred B folios:")
    for b_f, r in sorted(ac_preferred, key=lambda x: x[1])[:5]:
        print(f"  {b_f}: ratio={r:.2f}")

# Coverage gap analysis: vocabulary available from one family but not the other
print("\n" + "="*60)
print("FAMILY-EXCLUSIVE VOCABULARY IMPACT")
print("="*60)

zodiac_only = zodiac_middles - ac_middles
ac_only = ac_middles - zodiac_middles

# How many B folios use zodiac-only vocabulary?
b_uses_zodiac_only = []
b_uses_ac_only = []

for b_f in b_folios:
    b_vocab = b_folio_middles[b_f]
    zodiac_only_used = len(b_vocab & zodiac_only)
    ac_only_used = len(b_vocab & ac_only)

    b_uses_zodiac_only.append(zodiac_only_used)
    b_uses_ac_only.append(ac_only_used)

print(f"B folios using Zodiac-only MIDDLEs: {sum(1 for x in b_uses_zodiac_only if x > 0)} ({100*sum(1 for x in b_uses_zodiac_only if x > 0)/len(b_folios):.1f}%)")
print(f"B folios using A/C-only MIDDLEs: {sum(1 for x in b_uses_ac_only if x > 0)} ({100*sum(1 for x in b_uses_ac_only if x > 0)/len(b_folios):.1f}%)")
print(f"Mean Zodiac-only MIDDLEs per B folio: {np.mean(b_uses_zodiac_only):.2f}")
print(f"Mean A/C-only MIDDLEs per B folio: {np.mean(b_uses_ac_only):.2f}")

# Chi-squared test: is family-exclusive vocabulary uniformly distributed across B folios?
# Contingency: (using_exclusive, not_using_exclusive) x (zodiac, ac)
zodiac_users = sum(1 for x in b_uses_zodiac_only if x > 0)
ac_users = sum(1 for x in b_uses_ac_only if x > 0)

contingency = [
    [zodiac_users, len(b_folios) - zodiac_users],
    [ac_users, len(b_folios) - ac_users],
]
chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-squared (family-exclusive usage): chi2={chi2:.2f}, p={chi_p:.4f}")

# Save results
results['summary'] = {
    'zodiac_middles': len(zodiac_middles),
    'ac_middles': len(ac_middles),
    'shared_middles': len(zodiac_middles & ac_middles),
    'zodiac_only': len(zodiac_only),
    'ac_only': len(ac_only),
    'zodiac_mean_coverage': float(np.mean(zodiac_coverages)),
    'ac_mean_coverage': float(np.mean(ac_coverages)),
    'paired_ttest_p': float(t_p),
    'wilcoxon_p': float(w_p),
    'coverage_correlation': float(corr),
    'zodiac_preferred_count': len(zodiac_preferred),
    'ac_preferred_count': len(ac_preferred),
    'balanced_count': len(balanced),
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if t_p < 0.01 and len(zodiac_preferred) > len(balanced) and len(ac_preferred) > len(balanced):
    verdict = "FAMILIES_SERVE_DIFFERENT_B"
    print("The two AZC families serve DIFFERENT B folio subsets")
elif corr > 0.8:
    verdict = "FAMILIES_REDUNDANT"
    print(f"The two AZC families provide REDUNDANT B coverage (r={corr:.3f})")
elif abs(np.mean(zodiac_coverages) - np.mean(ac_coverages)) < 0.05:
    verdict = "FAMILIES_EQUIVALENT"
    print("The two AZC families provide EQUIVALENT B coverage")
else:
    verdict = "WEAK_DIFFERENTIATION"
    print(f"Weak family differentiation in B coverage (p={t_p:.4f})")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't7_family_b_coverage.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")
