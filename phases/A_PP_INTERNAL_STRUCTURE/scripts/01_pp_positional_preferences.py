#!/usr/bin/env python3
"""
Test 1: PP Positional Preferences

Question: Do PP MIDDLEs have consistent within-line positional preferences?

Tests whether C234's "position-free" finding holds specifically for PP,
or whether PP has internal positional grammar.
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
GALLOWS = {'k', 't', 'p', 'f'}

# RI-associated prefixes (to identify PP vs RI)
RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

print("="*70)
print("TEST 1: PP POSITIONAL PREFERENCES")
print("="*70)

# Collect PP token positions within lines
pp_positions = defaultdict(list)  # MIDDLE -> list of normalized positions
prefix_positions = defaultdict(list)  # PREFIX -> list of positions

line_data = defaultdict(list)  # (folio, line) -> tokens

for token in tx.currier_a():
    if '*' in token.word:
        continue
    line_data[(token.folio, token.line)].append(token.word)

# Process each line
total_pp_tokens = 0
total_lines = 0

for (folio, line), tokens in line_data.items():
    if len(tokens) < 3:
        continue

    total_lines += 1

    # Identify PP tokens (non-RI)
    for i, token in enumerate(tokens):
        try:
            m = morph.extract(token)
            # PP = tokens without RI-associated prefix
            if m.prefix not in RI_PREFIXES:
                # Normalized position (0 = first, 1 = last)
                norm_pos = i / (len(tokens) - 1) if len(tokens) > 1 else 0.5

                if m.middle:
                    pp_positions[m.middle].append(norm_pos)
                if m.prefix:
                    prefix_positions[m.prefix].append(norm_pos)

                total_pp_tokens += 1
        except:
            pass

print(f"\nTotal A lines analyzed: {total_lines}")
print(f"Total PP tokens: {total_pp_tokens}")
print(f"Unique PP MIDDLEs: {len(pp_positions)}")
print(f"Unique PP PREFIXes: {len(prefix_positions)}")

# =========================================================================
# Analyze MIDDLE positional preferences
# =========================================================================
print("\n" + "="*70)
print("PP MIDDLE POSITIONAL PREFERENCES")
print("="*70)

# Filter to MIDDLEs with sufficient data
MIN_COUNT = 30
frequent_middles = {m: pos for m, pos in pp_positions.items() if len(pos) >= MIN_COUNT}

print(f"\nMIDDLEs with n >= {MIN_COUNT}: {len(frequent_middles)}")

# Compute statistics for each MIDDLE
middle_stats = []

for middle, positions in frequent_middles.items():
    mean_pos = np.mean(positions)
    std_pos = np.std(positions)
    n = len(positions)

    # Test against uniform distribution
    # Uniform on [0,1] has mean 0.5
    # One-sample t-test against 0.5
    t_stat, p_val = stats.ttest_1samp(positions, 0.5)

    # Also KS test against uniform
    ks_stat, ks_p = stats.kstest(positions, 'uniform')

    # Classify bias
    if p_val < 0.05:
        if mean_pos < 0.4:
            bias = 'EARLY'
        elif mean_pos > 0.6:
            bias = 'LATE'
        else:
            bias = 'MIDDLE'
    else:
        bias = 'NONE'

    middle_stats.append({
        'middle': middle,
        'n': n,
        'mean_pos': mean_pos,
        'std_pos': std_pos,
        't_stat': t_stat,
        'p_val': p_val,
        'ks_p': ks_p,
        'bias': bias,
    })

# Sort by absolute deviation from 0.5
middle_stats.sort(key=lambda x: abs(x['mean_pos'] - 0.5), reverse=True)

# Count biases
bias_counts = Counter(s['bias'] for s in middle_stats)
print(f"\nBias distribution:")
for bias, count in bias_counts.most_common():
    print(f"  {bias}: {count} ({100*count/len(middle_stats):.1f}%)")

# Show most biased MIDDLEs
print(f"\n{'MIDDLE':<12} {'N':<6} {'Mean Pos':<10} {'Bias':<8} {'P-val':<10}")
print("-"*50)

for s in middle_stats[:20]:
    sig = "***" if s['p_val'] < 0.001 else "**" if s['p_val'] < 0.01 else "*" if s['p_val'] < 0.05 else ""
    print(f"{s['middle']:<12} {s['n']:<6} {s['mean_pos']:<10.3f} {s['bias']:<8} {s['p_val']:<.4f}{sig}")

# =========================================================================
# Analyze PREFIX positional preferences
# =========================================================================
print("\n" + "="*70)
print("PP PREFIX POSITIONAL PREFERENCES")
print("="*70)

frequent_prefixes = {p: pos for p, pos in prefix_positions.items() if len(pos) >= MIN_COUNT}
print(f"\nPREFIXes with n >= {MIN_COUNT}: {len(frequent_prefixes)}")

prefix_stats = []

for prefix, positions in frequent_prefixes.items():
    mean_pos = np.mean(positions)
    std_pos = np.std(positions)
    n = len(positions)

    t_stat, p_val = stats.ttest_1samp(positions, 0.5)

    if p_val < 0.05:
        if mean_pos < 0.4:
            bias = 'EARLY'
        elif mean_pos > 0.6:
            bias = 'LATE'
        else:
            bias = 'MIDDLE'
    else:
        bias = 'NONE'

    prefix_stats.append({
        'prefix': prefix,
        'n': n,
        'mean_pos': mean_pos,
        'std_pos': std_pos,
        'p_val': p_val,
        'bias': bias,
    })

prefix_stats.sort(key=lambda x: abs(x['mean_pos'] - 0.5), reverse=True)

print(f"\n{'PREFIX':<10} {'N':<8} {'Mean Pos':<10} {'Bias':<8} {'P-val':<10}")
print("-"*50)

for s in prefix_stats[:15]:
    sig = "***" if s['p_val'] < 0.001 else "**" if s['p_val'] < 0.01 else "*" if s['p_val'] < 0.05 else ""
    print(f"{s['prefix']:<10} {s['n']:<8} {s['mean_pos']:<10.3f} {s['bias']:<8} {s['p_val']:<.4f}{sig}")

# =========================================================================
# Overall positional structure test
# =========================================================================
print("\n" + "="*70)
print("OVERALL POSITIONAL STRUCTURE")
print("="*70)

# Aggregate all PP positions
all_pp_positions = []
for positions in pp_positions.values():
    all_pp_positions.extend(positions)

all_pp_positions = np.array(all_pp_positions)

print(f"\nAll PP tokens: {len(all_pp_positions)}")
print(f"Mean position: {np.mean(all_pp_positions):.3f}")
print(f"Std position: {np.std(all_pp_positions):.3f}")

# Test against uniform
ks_stat, ks_p = stats.kstest(all_pp_positions, 'uniform')
print(f"\nKS test vs uniform: KS={ks_stat:.4f}, p={ks_p:.4f}")

if ks_p < 0.05:
    print("** PP positions are NOT uniformly distributed **")
else:
    print("PP positions appear uniformly distributed (position-free)")

# Position histogram
print("\nPosition distribution (deciles):")
hist, bins = np.histogram(all_pp_positions, bins=10, range=(0, 1))
for i, count in enumerate(hist):
    pct = 100 * count / len(all_pp_positions)
    bar = '#' * int(pct)
    print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}: {pct:>5.1f}% {bar}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: PP POSITIONAL PREFERENCES")
print("="*70)

n_significant_middle = sum(1 for s in middle_stats if s['p_val'] < 0.05)
n_significant_prefix = sum(1 for s in prefix_stats if s['p_val'] < 0.05)

print(f"""
MIDDLEs with significant position bias: {n_significant_middle}/{len(middle_stats)} ({100*n_significant_middle/len(middle_stats):.1f}%)
PREFIXes with significant position bias: {n_significant_prefix}/{len(prefix_stats)} ({100*n_significant_prefix/len(prefix_stats):.1f}%)

Bias distribution (MIDDLEs):
  EARLY: {bias_counts.get('EARLY', 0)}
  MIDDLE: {bias_counts.get('MIDDLE', 0)}
  LATE: {bias_counts.get('LATE', 0)}
  NONE: {bias_counts.get('NONE', 0)}

Overall PP distribution: KS p={ks_p:.4f}
""")

# Determine verdict
if n_significant_middle / len(middle_stats) > 0.3 or ks_p < 0.001:
    verdict = "CONFIRMED"
    explanation = "PP has significant positional structure"
elif n_significant_middle / len(middle_stats) > 0.15 or ks_p < 0.05:
    verdict = "SUPPORT"
    explanation = "Some PP positional preferences exist"
else:
    verdict = "NOT SUPPORTED"
    explanation = "PP is largely position-free (confirms C234)"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'total_lines': total_lines,
    'total_pp_tokens': total_pp_tokens,
    'n_middles_tested': len(middle_stats),
    'n_middles_significant': n_significant_middle,
    'n_prefixes_tested': len(prefix_stats),
    'n_prefixes_significant': n_significant_prefix,
    'bias_counts': dict(bias_counts),
    'overall_ks_p': ks_p,
    'overall_mean_position': float(np.mean(all_pp_positions)),
    'top_biased_middles': [{'middle': s['middle'], 'mean_pos': s['mean_pos'], 'bias': s['bias'], 'p': s['p_val']}
                           for s in middle_stats[:10]],
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'pp_positional_preferences.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
