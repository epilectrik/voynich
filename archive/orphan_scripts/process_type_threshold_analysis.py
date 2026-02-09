#!/usr/bin/env python3
"""
Analyze threshold sensitivity for process type discrimination.

Question: Is HIGH_K_LOW_H (k>35%, h<20%) a real category or just noise?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build paragraph data
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

# Collect paragraph kernel and role data
all_paragraphs = []

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = [t.word for line_num, tokens in p for t in tokens]
        if len(words) < 10:
            continue

        k = sum(w.count('k') for w in words)
        h = sum(w.count('h') for w in words)
        e = sum(w.count('e') for w in words)
        total_kernel = k + h + e

        if total_kernel < 10:
            continue

        k_pct = 100 * k / total_kernel
        h_pct = 100 * h / total_kernel
        e_pct = 100 * e / total_kernel

        n_tokens = len(words)
        fq_count = sum(1 for w in words if token_to_role.get(w) == 'FREQUENT_OPERATOR')
        fq_rate = fq_count / n_tokens

        all_paragraphs.append({
            'k_pct': k_pct,
            'h_pct': h_pct,
            'e_pct': e_pct,
            'fq_rate': fq_rate,
        })

print("="*70)
print("PROCESS TYPE THRESHOLD ANALYSIS")
print("="*70)

print(f"\nTotal paragraphs: {len(all_paragraphs)}")

# Analyze h distribution in k-rich paragraphs
k_rich = [p for p in all_paragraphs if p['k_pct'] > 35]
print(f"\nk-rich paragraphs (k>35%): {len(k_rich)}")

# h distribution in k-rich paragraphs
h_values = [p['h_pct'] for p in k_rich]
print(f"\nh% distribution in k-rich paragraphs:")
print(f"  Min: {min(h_values):.1f}")
print(f"  25th: {np.percentile(h_values, 25):.1f}")
print(f"  Median: {np.median(h_values):.1f}")
print(f"  75th: {np.percentile(h_values, 75):.1f}")
print(f"  Max: {max(h_values):.1f}")

# Test different h thresholds
print(f"\n{'='*70}")
print("FQ RATE BY h THRESHOLD (within k-rich paragraphs)")
print("="*70)

thresholds = [10, 15, 20, 25, 30]
print(f"\n{'h threshold':<15} {'Low-h count':<15} {'High-h count':<15} {'Low-h FQ':<15} {'High-h FQ':<15} {'p-value':<12}")
print("-"*90)

for thresh in thresholds:
    low_h = [p for p in k_rich if p['h_pct'] < thresh]
    high_h = [p for p in k_rich if p['h_pct'] >= thresh]

    if len(low_h) < 3 or len(high_h) < 3:
        continue

    low_h_fq = 100 * np.mean([p['fq_rate'] for p in low_h])
    high_h_fq = 100 * np.mean([p['fq_rate'] for p in high_h])

    u_stat, p_val = scipy_stats.mannwhitneyu(
        [p['fq_rate'] for p in low_h],
        [p['fq_rate'] for p in high_h],
        alternative='two-sided'
    )

    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    print(f"h<{thresh:<13} {len(low_h):<15} {len(high_h):<15} {low_h_fq:<15.1f} {high_h_fq:<15.1f} {p_val:<12.4f} {sig}")

# Correlation analysis
print(f"\n{'='*70}")
print("CORRELATION: h% vs FQ RATE (within k-rich paragraphs)")
print("="*70)

h_values = [p['h_pct'] for p in k_rich]
fq_values = [p['fq_rate'] for p in k_rich]

rho, p_val = scipy_stats.spearmanr(h_values, fq_values)
print(f"\nSpearman correlation: rho = {rho:.3f}, p = {p_val:.4f}")

if rho < -0.2 and p_val < 0.05:
    print("-> Significant NEGATIVE correlation: more h = less FQ")
    print("-> Supports hypothesis: phase monitoring reduces need for escape/recovery")
elif rho > 0.2 and p_val < 0.05:
    print("-> Significant POSITIVE correlation: more h = more FQ")
else:
    print("-> No significant correlation")

# What about ALL paragraphs (not just k-rich)?
print(f"\n{'='*70}")
print("CORRELATION: h% vs FQ RATE (ALL paragraphs)")
print("="*70)

h_all = [p['h_pct'] for p in all_paragraphs]
fq_all = [p['fq_rate'] for p in all_paragraphs]

rho, p_val = scipy_stats.spearmanr(h_all, fq_all)
print(f"\nSpearman correlation: rho = {rho:.3f}, p = {p_val:.6f}")

if rho < 0 and p_val < 0.001:
    print("-> Highly significant NEGATIVE correlation: more h = less FQ")
    print("-> Strongly supports: phase monitoring (distillation) reduces recovery need")

# k% vs FQ relationship
print(f"\n{'='*70}")
print("CORRELATION: k% vs FQ RATE (ALL paragraphs)")
print("="*70)

k_all = [p['k_pct'] for p in all_paragraphs]
rho, p_val = scipy_stats.spearmanr(k_all, fq_all)
print(f"\nSpearman correlation: rho = {rho:.3f}, p = {p_val:.6f}")

if rho > 0 and p_val < 0.001:
    print("-> Highly significant POSITIVE correlation: more k = more FQ")
    print("-> Supports: fire-heavy processes need more recovery capacity")

# e% vs FQ
print(f"\n{'='*70}")
print("CORRELATION: e% vs FQ RATE (ALL paragraphs)")
print("="*70)

e_all = [p['e_pct'] for p in all_paragraphs]
rho, p_val = scipy_stats.spearmanr(e_all, fq_all)
print(f"\nSpearman correlation: rho = {rho:.3f}, p = {p_val:.6f}")

# Summary
print(f"\n{'='*70}")
print("SUMMARY: KERNEL-FQ RELATIONSHIPS")
print("="*70)

print("""
If FQ (escape/recovery) correlates with kernel characters:

1. k% -> FQ (+): More fire = more recovery need
   - Consistent with k=ENERGY_MODULATOR, FQ=escape

2. h% -> FQ (-): More phase monitoring = less recovery need
   - Phase feedback (drip timing) prevents errors
   - DISTILLATION provides better control feedback

3. e% -> FQ (?): Equilibration relationship with recovery

INTERPRETATION:
- Distillation (high h) has BUILT-IN feedback (drip rate)
- Boiling/decoction (high k, low h) lacks this feedback
- Therefore boiling needs MORE escape/recovery capacity
""")
