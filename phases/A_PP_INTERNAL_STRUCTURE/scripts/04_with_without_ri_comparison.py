#!/usr/bin/env python3
"""
Test 4: WITH-RI vs WITHOUT-RI PP Comparison

Question: Does PP vocabulary differ between lines with RI and pure-PP lines?

C888 suggests WITHOUT-RI lines are cross-reference heavy (ct-enriched in H).
This test quantifies the PP vocabulary divergence.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

print("="*70)
print("TEST 4: WITH-RI vs WITHOUT-RI PP COMPARISON")
print("="*70)

# Collect data by line type
with_ri_pp = {'middles': Counter(), 'prefixes': Counter(), 'positions': [], 'n_lines': 0}
without_ri_pp = {'middles': Counter(), 'prefixes': Counter(), 'positions': [], 'n_lines': 0}

line_data = defaultdict(list)

for token in tx.currier_a():
    if '*' in token.word:
        continue
    line_data[(token.folio, token.line)].append(token.word)

for (folio, line), tokens in line_data.items():
    if len(tokens) < 2:
        continue

    # Classify line: does it have RI tokens?
    has_ri = False
    pp_tokens = []

    for i, token in enumerate(tokens):
        try:
            m = morph.extract(token)
            if m.prefix in RI_PREFIXES:
                has_ri = True
            else:
                # This is a PP token
                norm_pos = i / (len(tokens) - 1) if len(tokens) > 1 else 0.5
                pp_tokens.append((m.middle, m.prefix, norm_pos))
        except:
            pass

    # Collect PP data
    target = with_ri_pp if has_ri else without_ri_pp
    target['n_lines'] += 1

    for middle, prefix, pos in pp_tokens:
        if middle:
            target['middles'][middle] += 1
        if prefix:
            target['prefixes'][prefix] += 1
        target['positions'].append(pos)

print(f"\nLine counts:")
print(f"  WITH-RI lines: {with_ri_pp['n_lines']}")
print(f"  WITHOUT-RI lines: {without_ri_pp['n_lines']}")

# =========================================================================
# Compare PP MIDDLE vocabulary
# =========================================================================
print("\n" + "="*70)
print("PP MIDDLE VOCABULARY COMPARISON")
print("="*70)

with_ri_middles = set(m for m, c in with_ri_pp['middles'].items() if c >= 3)
without_ri_middles = set(m for m, c in without_ri_pp['middles'].items() if c >= 3)

shared = with_ri_middles & without_ri_middles
with_ri_only = with_ri_middles - without_ri_middles
without_ri_only = without_ri_middles - with_ri_middles

jaccard = len(shared) / len(with_ri_middles | without_ri_middles) if (with_ri_middles | without_ri_middles) else 0

print(f"\nMIDDLE vocabulary (count >= 3):")
print(f"  WITH-RI unique: {len(with_ri_middles)}")
print(f"  WITHOUT-RI unique: {len(without_ri_middles)}")
print(f"  Shared: {len(shared)}")
print(f"  Jaccard similarity: {jaccard:.3f}")

print(f"\nWITH-RI only MIDDLEs ({len(with_ri_only)}):")
top_with_ri_only = sorted([(m, with_ri_pp['middles'][m]) for m in with_ri_only], key=lambda x: -x[1])[:10]
for m, c in top_with_ri_only:
    print(f"  {m:<12} (n={c})")

print(f"\nWITHOUT-RI only MIDDLEs ({len(without_ri_only)}):")
top_without_ri_only = sorted([(m, without_ri_pp['middles'][m]) for m in without_ri_only], key=lambda x: -x[1])[:10]
for m, c in top_without_ri_only:
    print(f"  {m:<12} (n={c})")

# =========================================================================
# Compare PP PREFIX profiles
# =========================================================================
print("\n" + "="*70)
print("PP PREFIX PROFILE COMPARISON")
print("="*70)

with_ri_total = sum(with_ri_pp['prefixes'].values())
without_ri_total = sum(without_ri_pp['prefixes'].values())

# Get all prefixes
all_prefixes = set(with_ri_pp['prefixes'].keys()) | set(without_ri_pp['prefixes'].keys())

print(f"\n{'PREFIX':<10} {'WITH-RI %':<12} {'WITHOUT-RI %':<14} {'Ratio':<10}")
print("-"*50)

prefix_comparison = []
for prefix in sorted(all_prefixes):
    with_count = with_ri_pp['prefixes'].get(prefix, 0)
    without_count = without_ri_pp['prefixes'].get(prefix, 0)

    with_pct = 100 * with_count / with_ri_total if with_ri_total > 0 else 0
    without_pct = 100 * without_count / without_ri_total if without_ri_total > 0 else 0

    if with_pct > 0:
        ratio = without_pct / with_pct
    else:
        ratio = float('inf') if without_pct > 0 else 1.0

    if with_count + without_count >= 20:
        prefix_comparison.append({
            'prefix': prefix,
            'with_ri_pct': with_pct,
            'without_ri_pct': without_pct,
            'ratio': ratio,
        })
        print(f"{prefix:<10} {with_pct:<12.1f} {without_pct:<14.1f} {ratio:<10.2f}")

# Identify significantly different prefixes
print("\nPREFIXes enriched in WITHOUT-RI (ratio > 1.5):")
for p in sorted(prefix_comparison, key=lambda x: -x['ratio']):
    if p['ratio'] > 1.5 and p['ratio'] != float('inf'):
        print(f"  {p['prefix']}: {p['ratio']:.2f}x")

print("\nPREFIXes depleted in WITHOUT-RI (ratio < 0.67):")
for p in sorted(prefix_comparison, key=lambda x: x['ratio']):
    if p['ratio'] < 0.67:
        print(f"  {p['prefix']}: {p['ratio']:.2f}x")

# =========================================================================
# Compare PP positional distributions
# =========================================================================
print("\n" + "="*70)
print("PP POSITIONAL DISTRIBUTION COMPARISON")
print("="*70)

with_ri_pos = np.array(with_ri_pp['positions'])
without_ri_pos = np.array(without_ri_pp['positions'])

print(f"\nPosition statistics:")
print(f"  WITH-RI: mean={np.mean(with_ri_pos):.3f}, std={np.std(with_ri_pos):.3f}, n={len(with_ri_pos)}")
print(f"  WITHOUT-RI: mean={np.mean(without_ri_pos):.3f}, std={np.std(without_ri_pos):.3f}, n={len(without_ri_pos)}")

# Mann-Whitney test
u_stat, mw_p = stats.mannwhitneyu(with_ri_pos, without_ri_pos, alternative='two-sided')
print(f"\nMann-Whitney U test: U={u_stat:.0f}, p={mw_p:.4f}")

if mw_p < 0.05:
    if np.mean(with_ri_pos) < np.mean(without_ri_pos):
        print("** WITH-RI PP tends to appear EARLIER in lines")
    else:
        print("** WITHOUT-RI PP tends to appear EARLIER in lines")
else:
    print("No significant positional difference")

# =========================================================================
# Chi-square test for overall vocabulary difference
# =========================================================================
print("\n" + "="*70)
print("STATISTICAL TESTS")
print("="*70)

# Build contingency table for shared prefixes
shared_prefixes = set(with_ri_pp['prefixes'].keys()) & set(without_ri_pp['prefixes'].keys())
if len(shared_prefixes) >= 5:
    contingency = []
    for prefix in sorted(shared_prefixes):
        contingency.append([
            with_ri_pp['prefixes'][prefix],
            without_ri_pp['prefixes'][prefix]
        ])

    chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square (PREFIX distribution ~ line type):")
    print(f"  chi2={chi2:.2f}, df={dof}, p={chi_p:.6f}")

    if chi_p < 0.001:
        print("  *** Highly significant: WITH-RI and WITHOUT-RI have different PREFIX profiles")
    elif chi_p < 0.05:
        print("  * Significant: PREFIX profiles differ")
    else:
        print("  Not significant: PREFIX profiles are similar")
else:
    chi_p = 1.0

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: WITH-RI vs WITHOUT-RI PP COMPARISON")
print("="*70)

print(f"""
Vocabulary overlap:
  Jaccard (MIDDLEs): {jaccard:.3f}
  WITH-RI only: {len(with_ri_only)} MIDDLEs
  WITHOUT-RI only: {len(without_ri_only)} MIDDLEs

PREFIX profile difference:
  Chi-square p-value: {chi_p:.6f}

Positional difference:
  Mann-Whitney p-value: {mw_p:.4f}
""")

# Determine verdict
vocab_different = jaccard < 0.7 and (len(with_ri_only) > 10 or len(without_ri_only) > 10)
prefix_different = chi_p < 0.05
position_different = mw_p < 0.05

if vocab_different and prefix_different:
    verdict = "CONFIRMED"
    explanation = "WITH-RI and WITHOUT-RI lines have significantly different PP profiles"
elif prefix_different or vocab_different:
    verdict = "SUPPORT"
    explanation = "Some PP divergence between line types"
else:
    verdict = "NOT SUPPORTED"
    explanation = "PP is similar regardless of RI presence"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'with_ri_lines': with_ri_pp['n_lines'],
    'without_ri_lines': without_ri_pp['n_lines'],
    'jaccard_middles': jaccard,
    'with_ri_only_count': len(with_ri_only),
    'without_ri_only_count': len(without_ri_only),
    'chi_square_p': chi_p,
    'mann_whitney_p': mw_p,
    'prefix_comparison': prefix_comparison,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'with_without_ri_comparison.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
