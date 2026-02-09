#!/usr/bin/env python3
"""
Test if paragraphs show SEQUENTIAL pattern (early=energy, late=monitoring)
rather than alternating hysteresis
"""

import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

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

def get_kernel_stats(para):
    words = []
    for line_num, tokens in para:
        words.extend([t.word for t in tokens])

    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total = k + h + e

    qo = sum(1 for w in words if w.startswith('qo'))
    chsh = sum(1 for w in words if w.startswith('ch') or w.startswith('sh'))

    if total < 10:
        return None

    return {
        'k_pct': 100 * k / total,
        'h_pct': 100 * h / total,
        'e_pct': 100 * e / total,
        'qo': qo,
        'chsh': chsh,
        'qo_ratio': qo / (qo + chsh) if (qo + chsh) > 0 else 0.5,
        'tokens': len(words)
    }

# Aggregate by paragraph position (normalized 0-1 within each folio)
print("="*70)
print("PARAGRAPH POSITION vs KERNEL SIGNATURE")
print("="*70)

positions = []
k_pcts = []
h_pcts = []
qo_ratios = []

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    n_paras = len(paras)
    if n_paras < 3:
        continue

    for i, p in enumerate(paras):
        stats = get_kernel_stats(p)
        if stats is None:
            continue

        # Normalized position (0 = first, 1 = last)
        norm_pos = i / (n_paras - 1) if n_paras > 1 else 0.5

        positions.append(norm_pos)
        k_pcts.append(stats['k_pct'])
        h_pcts.append(stats['h_pct'])
        qo_ratios.append(stats['qo_ratio'])

positions = np.array(positions)
k_pcts = np.array(k_pcts)
h_pcts = np.array(h_pcts)
qo_ratios = np.array(qo_ratios)

# Correlations
rho_k, p_k = scipy_stats.spearmanr(positions, k_pcts)
rho_h, p_h = scipy_stats.spearmanr(positions, h_pcts)
rho_qo, p_qo = scipy_stats.spearmanr(positions, qo_ratios)

print(f"\nSpearman correlations (paragraph position 0->1):")
print(f"  k% vs position: rho={rho_k:.3f}, p={p_k:.2e}")
print(f"  h% vs position: rho={rho_h:.3f}, p={p_h:.2e}")
print(f"  qo_ratio vs position: rho={rho_qo:.3f}, p={p_qo:.2e}")

# Bin by position quartile
print(f"\n{'='*70}")
print("KERNEL SIGNATURE BY POSITION QUARTILE")
print("="*70)

quartiles = [0, 0.25, 0.5, 0.75, 1.01]
labels = ['Q1 (first)', 'Q2 (early-mid)', 'Q3 (late-mid)', 'Q4 (last)']

print(f"\n{'Quartile':<15} {'n':<6} {'k%':<8} {'h%':<8} {'e%':<8} {'qo_ratio':<10}")
print("-"*60)

for i in range(4):
    mask = (positions >= quartiles[i]) & (positions < quartiles[i+1])
    n = mask.sum()
    if n > 0:
        mean_k = k_pcts[mask].mean()
        mean_h = h_pcts[mask].mean()
        mean_e = 100 - mean_k - mean_h  # Approximate
        mean_qo = qo_ratios[mask].mean()
        print(f"{labels[i]:<15} {n:<6} {mean_k:<8.1f} {mean_h:<8.1f} {mean_e:<8.1f} {mean_qo:<10.3f}")

# Test for sequential pattern within individual folios
print(f"\n{'='*70}")
print("PER-FOLIO SEQUENTIAL PATTERN (k% early vs late)")
print("="*70)

folio_patterns = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    if len(paras) < 4:
        continue

    stats_list = [get_kernel_stats(p) for p in paras]
    stats_list = [s for s in stats_list if s is not None]

    if len(stats_list) < 4:
        continue

    # Compare first half vs second half
    mid = len(stats_list) // 2
    early = stats_list[:mid]
    late = stats_list[mid:]

    early_k = np.mean([s['k_pct'] for s in early])
    late_k = np.mean([s['k_pct'] for s in late])
    early_h = np.mean([s['h_pct'] for s in early])
    late_h = np.mean([s['h_pct'] for s in late])
    early_qo = np.mean([s['qo_ratio'] for s in early])
    late_qo = np.mean([s['qo_ratio'] for s in late])

    folio_patterns.append({
        'folio': folio,
        'n': len(stats_list),
        'early_k': early_k,
        'late_k': late_k,
        'k_delta': early_k - late_k,
        'early_h': early_h,
        'late_h': late_h,
        'h_delta': late_h - early_h,  # Expect positive if sequential
        'early_qo': early_qo,
        'late_qo': late_qo,
        'qo_delta': early_qo - late_qo  # Expect positive if sequential
    })

# Summary
k_deltas = [p['k_delta'] for p in folio_patterns]
h_deltas = [p['h_delta'] for p in folio_patterns]
qo_deltas = [p['qo_delta'] for p in folio_patterns]

print(f"\nEarly-vs-Late comparison across {len(folio_patterns)} folios:")
print(f"  k% (early - late): mean={np.mean(k_deltas):.1f}, median={np.median(k_deltas):.1f}")
print(f"  h% (late - early): mean={np.mean(h_deltas):.1f}, median={np.median(h_deltas):.1f}")
print(f"  qo_ratio (early - late): mean={np.mean(qo_deltas):.3f}, median={np.median(qo_deltas):.3f}")

# Count folios showing expected pattern
k_pattern = sum(1 for d in k_deltas if d > 0)  # Early k > late k
h_pattern = sum(1 for d in h_deltas if d > 0)  # Late h > early h
qo_pattern = sum(1 for d in qo_deltas if d > 0)  # Early qo > late qo

print(f"\nFolios showing expected sequential pattern:")
print(f"  k% higher early: {k_pattern}/{len(folio_patterns)} ({100*k_pattern/len(folio_patterns):.0f}%)")
print(f"  h% higher late: {h_pattern}/{len(folio_patterns)} ({100*h_pattern/len(folio_patterns):.0f}%)")
print(f"  qo_ratio higher early: {qo_pattern}/{len(folio_patterns)} ({100*qo_pattern/len(folio_patterns):.0f}%)")

# Binomial test
p_k = 1 - scipy_stats.binom.cdf(k_pattern-1, len(folio_patterns), 0.5)
p_h = 1 - scipy_stats.binom.cdf(h_pattern-1, len(folio_patterns), 0.5)
p_qo = 1 - scipy_stats.binom.cdf(qo_pattern-1, len(folio_patterns), 0.5)

print(f"\nBinomial test (vs 50% null):")
print(f"  k% higher early: p={p_k:.4f}")
print(f"  h% higher late: p={p_h:.4f}")
print(f"  qo_ratio higher early: p={p_qo:.4f}")

# Show strongest sequential folios
print(f"\n{'='*70}")
print("FOLIOS WITH STRONGEST SEQUENTIAL PATTERN (qo_delta)")
print("="*70)

folio_patterns.sort(key=lambda x: -x['qo_delta'])
print(f"\n{'Folio':<10} {'n':<5} {'early_qo':<10} {'late_qo':<10} {'delta':<10}")
print("-"*50)
for p in folio_patterns[:10]:
    print(f"{p['folio']:<10} {p['n']:<5} {p['early_qo']:<10.3f} {p['late_qo']:<10.3f} {p['qo_delta']:<10.3f}")
