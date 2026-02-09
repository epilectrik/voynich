#!/usr/bin/env python3
"""
Test 1: Kernel k/h/e Profile by Prefix Family

Question: Do QO and CHSH tokens have different kernel distributions?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import Counter
import json

def main():
    tx = Transcript()
    morph = Morphology()

    # QO-family prefixes (o-initial prefixes that select QO lane)
    QO_PREFIXES = {'qo', 'ok', 'ot', 'o'}

    # CHSH-family prefixes
    CHSH_PREFIXES = {'ch', 'sh'}

    # Kernel characters
    KERNEL_CHARS = {'k', 'h', 'e'}

    qo_kernels = Counter()
    chsh_kernels = Counter()
    qo_total = 0
    chsh_total = 0

    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue

        m = morph.extract(token.word)
        if not m.prefix:
            continue

        # Count kernels in MIDDLE
        if not m.middle:
            continue

        kernels_in_middle = [c for c in m.middle if c in KERNEL_CHARS]

        if m.prefix in QO_PREFIXES:
            qo_total += 1
            for k in kernels_in_middle:
                qo_kernels[k] += 1
        elif m.prefix in CHSH_PREFIXES:
            chsh_total += 1
            for k in kernels_in_middle:
                chsh_kernels[k] += 1

    # Calculate percentages
    qo_kernel_total = sum(qo_kernels.values())
    chsh_kernel_total = sum(chsh_kernels.values())

    results = {
        'qo_tokens': qo_total,
        'chsh_tokens': chsh_total,
        'qo_kernel_total': qo_kernel_total,
        'chsh_kernel_total': chsh_kernel_total,
        'qo_kernel_dist': {
            'k': qo_kernels.get('k', 0),
            'h': qo_kernels.get('h', 0),
            'e': qo_kernels.get('e', 0),
        },
        'chsh_kernel_dist': {
            'k': chsh_kernels.get('k', 0),
            'h': chsh_kernels.get('h', 0),
            'e': chsh_kernels.get('e', 0),
        },
    }

    # Calculate percentages
    if qo_kernel_total > 0:
        results['qo_kernel_pct'] = {
            'k': round(100 * qo_kernels.get('k', 0) / qo_kernel_total, 1),
            'h': round(100 * qo_kernels.get('h', 0) / qo_kernel_total, 1),
            'e': round(100 * qo_kernels.get('e', 0) / qo_kernel_total, 1),
        }

    if chsh_kernel_total > 0:
        results['chsh_kernel_pct'] = {
            'k': round(100 * chsh_kernels.get('k', 0) / chsh_kernel_total, 1),
            'h': round(100 * chsh_kernels.get('h', 0) / chsh_kernel_total, 1),
            'e': round(100 * chsh_kernels.get('e', 0) / chsh_kernel_total, 1),
        }

    # Chi-square test
    from scipy.stats import chi2_contingency
    observed = [
        [qo_kernels.get('k', 0), qo_kernels.get('h', 0), qo_kernels.get('e', 0)],
        [chsh_kernels.get('k', 0), chsh_kernels.get('h', 0), chsh_kernels.get('e', 0)]
    ]
    chi2, p, dof, expected = chi2_contingency(observed)
    results['chi2'] = round(chi2, 2)
    results['p_value'] = p
    results['significant'] = p < 0.01

    # Print results
    print("=" * 60)
    print("TEST 1: KERNEL PROFILE BY PREFIX FAMILY")
    print("=" * 60)
    print()
    print(f"QO-family tokens (qo/ok/ot/o prefix): {qo_total}")
    print(f"CHSH-family tokens (ch/sh prefix): {chsh_total}")
    print()
    print("Kernel Distribution in MIDDLEs:")
    print("-" * 40)
    print(f"{'Family':<10} {'k (energy)':<15} {'h (hazard)':<15} {'e (escape)':<15}")
    print("-" * 40)

    qo_pct = results.get('qo_kernel_pct', {})
    chsh_pct = results.get('chsh_kernel_pct', {})

    print(f"{'QO':<10} {qo_pct.get('k', 0):>6.1f}% ({qo_kernels.get('k',0):>4})  {qo_pct.get('h', 0):>6.1f}% ({qo_kernels.get('h',0):>4})  {qo_pct.get('e', 0):>6.1f}% ({qo_kernels.get('e',0):>4})")
    print(f"{'CHSH':<10} {chsh_pct.get('k', 0):>6.1f}% ({chsh_kernels.get('k',0):>4})  {chsh_pct.get('h', 0):>6.1f}% ({chsh_kernels.get('h',0):>4})  {chsh_pct.get('e', 0):>6.1f}% ({chsh_kernels.get('e',0):>4})")
    print("-" * 40)
    print()
    print(f"Chi-square test: chi2={chi2:.2f}, p={p:.2e}")
    print(f"Significant difference (p<0.01): {results['significant']}")

    # Save results
    with open('C:/git/voynich/phases/QO_CHSH_DIFFERENTIATION/results/01_kernel_profile.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to results/01_kernel_profile.json")

if __name__ == '__main__':
    main()
