"""
01_kernel_middle_correlation.py - MIDDLE distribution by kernel profile

Tests whether specific MIDDLEs correlate with kernel profiles:
- HIGH_K = energy-intensive operations (C893: 2x distillation rate)
- HIGH_H = phase monitoring
- HIGH_E = stability anchoring

If MIDDLEs cluster by kernel profile, they encode heat/energy requirements.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from scipy import stats
import json
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()

# Get Currier B tokens (where kernel analysis applies)
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# Build paragraph-level data
# Group tokens by folio + paragraph (using par_initial/par_final markers)
paragraphs = defaultdict(list)
current_para = 0
current_folio = None

for t in b_tokens:
    # Reset paragraph counter on new folio
    if t.folio != current_folio:
        current_folio = t.folio
        current_para = 0

    # New paragraph starts
    if t.par_initial:
        current_para += 1

    key = (t.folio, current_para)
    paragraphs[key].append(t)

print(f"Total paragraphs: {len(paragraphs)}")

# Compute kernel profile for each paragraph
def get_kernel(middle):
    """Extract kernel character from MIDDLE"""
    if not middle:
        return None
    # Kernel is typically first character if it's k, t, e, or h
    # But need to handle compound MIDDLEs
    for char in ['k', 't', 'e', 'h']:
        if char in middle:
            return char
    return None

paragraph_profiles = {}
for key, tokens in paragraphs.items():
    kernels = {'k': 0, 't': 0, 'e': 0, 'h': 0}
    total = 0
    for t in tokens:
        m = morph.extract(t.word)
        if m and m.middle:
            kernel = get_kernel(m.middle)
            if kernel:
                kernels[kernel] += 1
                total += 1

    if total >= 5:  # Minimum tokens for reliable profile
        # Compute proportions
        profile = {k: v/total for k, v in kernels.items()}

        # Classify paragraph
        # HIGH_K: k proportion > median
        # HIGH_H: h proportion > median
        # etc.
        paragraph_profiles[key] = {
            'kernels': kernels,
            'total': total,
            'profile': profile,
            'tokens': tokens
        }

print(f"Paragraphs with kernel profile: {len(paragraph_profiles)}")

# Compute median thresholds for classification
k_props = [p['profile']['k'] for p in paragraph_profiles.values()]
h_props = [p['profile']['h'] for p in paragraph_profiles.values()]
e_props = [p['profile']['e'] for p in paragraph_profiles.values()]

k_median = np.median(k_props)
h_median = np.median(h_props)
e_median = np.median(e_props)

print(f"\nKernel proportion medians:")
print(f"  k: {k_median:.3f}")
print(f"  h: {h_median:.3f}")
print(f"  e: {e_median:.3f}")

# Classify paragraphs
for key, data in paragraph_profiles.items():
    p = data['profile']
    data['HIGH_K'] = p['k'] > k_median
    data['HIGH_H'] = p['h'] > h_median
    data['HIGH_E'] = p['e'] > e_median

# Now compute MIDDLE distribution by kernel profile
# For each MIDDLE, count occurrences in HIGH_K vs LOW_K paragraphs

middle_by_kernel = defaultdict(lambda: {
    'HIGH_K': 0, 'LOW_K': 0,
    'HIGH_H': 0, 'LOW_H': 0,
    'HIGH_E': 0, 'LOW_E': 0,
    'total': 0
})

for key, data in paragraph_profiles.items():
    for t in data['tokens']:
        m = morph.extract(t.word)
        if m and m.middle:
            mid = m.middle
            middle_by_kernel[mid]['total'] += 1

            if data['HIGH_K']:
                middle_by_kernel[mid]['HIGH_K'] += 1
            else:
                middle_by_kernel[mid]['LOW_K'] += 1

            if data['HIGH_H']:
                middle_by_kernel[mid]['HIGH_H'] += 1
            else:
                middle_by_kernel[mid]['LOW_H'] += 1

            if data['HIGH_E']:
                middle_by_kernel[mid]['HIGH_E'] += 1
            else:
                middle_by_kernel[mid]['LOW_E'] += 1

# Filter to MIDDLEs with sufficient count
MIN_COUNT = 50
significant_middles = {k: v for k, v in middle_by_kernel.items() if v['total'] >= MIN_COUNT}
print(f"\nMIDDLEs with >= {MIN_COUNT} occurrences: {len(significant_middles)}")

# Compute enrichment ratios and chi-square tests
results = []

for mid, counts in significant_middles.items():
    total = counts['total']

    # K enrichment
    k_ratio = (counts['HIGH_K'] / total) / 0.5 if total > 0 else 1.0
    # Chi-square for K
    observed_k = [counts['HIGH_K'], counts['LOW_K']]
    expected_k = [total/2, total/2]
    if min(expected_k) >= 5:
        chi2_k, p_k = stats.chisquare(observed_k, expected_k)
    else:
        chi2_k, p_k = 0, 1.0

    # H enrichment
    h_ratio = (counts['HIGH_H'] / total) / 0.5 if total > 0 else 1.0
    observed_h = [counts['HIGH_H'], counts['LOW_H']]
    expected_h = [total/2, total/2]
    if min(expected_h) >= 5:
        chi2_h, p_h = stats.chisquare(observed_h, expected_h)
    else:
        chi2_h, p_h = 0, 1.0

    # E enrichment
    e_ratio = (counts['HIGH_E'] / total) / 0.5 if total > 0 else 1.0
    observed_e = [counts['HIGH_E'], counts['LOW_E']]
    expected_e = [total/2, total/2]
    if min(expected_e) >= 5:
        chi2_e, p_e = stats.chisquare(observed_e, expected_e)
    else:
        chi2_e, p_e = 0, 1.0

    results.append({
        'middle': mid,
        'total': total,
        'HIGH_K': counts['HIGH_K'],
        'HIGH_H': counts['HIGH_H'],
        'HIGH_E': counts['HIGH_E'],
        'k_ratio': k_ratio,
        'h_ratio': h_ratio,
        'e_ratio': e_ratio,
        'p_k': p_k,
        'p_h': p_h,
        'p_e': p_e
    })

# Sort by strongest signal
results.sort(key=lambda x: min(x['p_k'], x['p_h'], x['p_e']))

print("\n" + "="*80)
print("TOP 20 MIDDLEs BY KERNEL CORRELATION")
print("="*80)
print(f"{'MIDDLE':<12} {'N':>6} {'K_ratio':>8} {'p_k':>10} {'H_ratio':>8} {'p_h':>10} {'E_ratio':>8} {'p_e':>10}")
print("-"*80)

for r in results[:20]:
    print(f"{r['middle']:<12} {r['total']:>6} {r['k_ratio']:>8.2f} {r['p_k']:>10.4f} "
          f"{r['h_ratio']:>8.2f} {r['p_h']:>10.4f} {r['e_ratio']:>8.2f} {r['p_e']:>10.4f}")

# Find significantly enriched MIDDLEs (p < 0.01)
print("\n" + "="*80)
print("SIGNIFICANTLY K-ENRICHED MIDDLEs (p < 0.01, ratio > 1.2)")
print("="*80)
k_enriched = [r for r in results if r['p_k'] < 0.01 and r['k_ratio'] > 1.2]
k_enriched.sort(key=lambda x: -x['k_ratio'])
for r in k_enriched[:15]:
    print(f"  {r['middle']:<12} K_ratio={r['k_ratio']:.2f} (p={r['p_k']:.4f}, n={r['total']})")

print("\n" + "="*80)
print("SIGNIFICANTLY K-DEPLETED MIDDLEs (p < 0.01, ratio < 0.8)")
print("="*80)
k_depleted = [r for r in results if r['p_k'] < 0.01 and r['k_ratio'] < 0.8]
k_depleted.sort(key=lambda x: x['k_ratio'])
for r in k_depleted[:15]:
    print(f"  {r['middle']:<12} K_ratio={r['k_ratio']:.2f} (p={r['p_k']:.4f}, n={r['total']})")

print("\n" + "="*80)
print("SIGNIFICANTLY H-ENRICHED MIDDLEs (p < 0.01, ratio > 1.2)")
print("="*80)
h_enriched = [r for r in results if r['p_h'] < 0.01 and r['h_ratio'] > 1.2]
h_enriched.sort(key=lambda x: -x['h_ratio'])
for r in h_enriched[:15]:
    print(f"  {r['middle']:<12} H_ratio={r['h_ratio']:.2f} (p={r['p_h']:.4f}, n={r['total']})")

print("\n" + "="*80)
print("SIGNIFICANTLY E-ENRICHED MIDDLEs (p < 0.01, ratio > 1.2)")
print("="*80)
e_enriched = [r for r in results if r['p_e'] < 0.01 and r['e_ratio'] > 1.2]
e_enriched.sort(key=lambda x: -x['e_ratio'])
for r in e_enriched[:15]:
    print(f"  {r['middle']:<12} E_ratio={r['e_ratio']:.2f} (p={r['p_e']:.4f}, n={r['total']})")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
sig_k = len([r for r in results if r['p_k'] < 0.01])
sig_h = len([r for r in results if r['p_h'] < 0.01])
sig_e = len([r for r in results if r['p_e'] < 0.01])
print(f"MIDDLEs significantly correlated with K: {sig_k}/{len(results)} ({100*sig_k/len(results):.1f}%)")
print(f"MIDDLEs significantly correlated with H: {sig_h}/{len(results)} ({100*sig_h/len(results):.1f}%)")
print(f"MIDDLEs significantly correlated with E: {sig_e}/{len(results)} ({100*sig_e/len(results):.1f}%)")

# Save results
output = {
    'parameters': {
        'min_count': MIN_COUNT,
        'k_median': k_median,
        'h_median': h_median,
        'e_median': e_median,
        'total_paragraphs': len(paragraph_profiles),
        'total_middles_analyzed': len(results)
    },
    'summary': {
        'sig_k_count': sig_k,
        'sig_h_count': sig_h,
        'sig_e_count': sig_e
    },
    'k_enriched': [{'middle': r['middle'], 'ratio': r['k_ratio'], 'p': r['p_k'], 'n': r['total']}
                   for r in k_enriched],
    'k_depleted': [{'middle': r['middle'], 'ratio': r['k_ratio'], 'p': r['p_k'], 'n': r['total']}
                   for r in k_depleted],
    'h_enriched': [{'middle': r['middle'], 'ratio': r['h_ratio'], 'p': r['p_h'], 'n': r['total']}
                   for r in h_enriched],
    'e_enriched': [{'middle': r['middle'], 'ratio': r['e_ratio'], 'p': r['p_e'], 'n': r['total']}
                   for r in e_enriched],
    'all_results': results
}

with open('C:/git/voynich/phases/MIDDLE_SEMANTIC_MAPPING/results/kernel_middle_correlation.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nResults saved to kernel_middle_correlation.json")
