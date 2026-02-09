#!/usr/bin/env python3
"""
Test 3: Section QO:CHSH Absolute Ratio

Question: What's the base QO:CHSH ratio in each section?
          (We know oscillation rate varies, but what about absolute counts?)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
import json

def main():
    tx = Transcript()
    morph = Morphology()

    QO_PREFIXES = {'qo', 'ok', 'ot', 'o'}
    CHSH_PREFIXES = {'ch', 'sh'}

    section_qo = Counter()
    section_chsh = Counter()
    section_total = Counter()

    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue

        m = morph.extract(token.word)
        if not m.prefix:
            continue

        section = token.section
        section_total[section] += 1

        if m.prefix in QO_PREFIXES:
            section_qo[section] += 1
        elif m.prefix in CHSH_PREFIXES:
            section_chsh[section] += 1

    # Calculate ratios
    results = {
        'sections': {}
    }

    print("=" * 70)
    print("TEST 3: SECTION QO:CHSH RATIO")
    print("=" * 70)
    print()
    print(f"{'Section':<12} {'QO':<8} {'CHSH':<8} {'QO%':<8} {'CHSH%':<8} {'Ratio':<10}")
    print("-" * 70)

    sections = sorted(set(section_qo.keys()) | set(section_chsh.keys()))

    for section in sections:
        qo = section_qo.get(section, 0)
        chsh = section_chsh.get(section, 0)
        total = qo + chsh

        if total == 0:
            continue

        qo_pct = 100 * qo / total
        chsh_pct = 100 * chsh / total
        ratio = qo / chsh if chsh > 0 else float('inf')

        results['sections'][section] = {
            'qo': qo,
            'chsh': chsh,
            'qo_pct': round(qo_pct, 1),
            'chsh_pct': round(chsh_pct, 1),
            'ratio': round(ratio, 2) if ratio != float('inf') else 'inf'
        }

        print(f"{section:<12} {qo:<8} {chsh:<8} {qo_pct:<8.1f} {chsh_pct:<8.1f} {ratio:<10.2f}")

    print("-" * 70)

    # Global totals
    total_qo = sum(section_qo.values())
    total_chsh = sum(section_chsh.values())
    total = total_qo + total_chsh
    global_qo_pct = 100 * total_qo / total
    global_chsh_pct = 100 * total_chsh / total
    global_ratio = total_qo / total_chsh if total_chsh > 0 else float('inf')

    print(f"{'GLOBAL':<12} {total_qo:<8} {total_chsh:<8} {global_qo_pct:<8.1f} {global_chsh_pct:<8.1f} {global_ratio:<10.2f}")

    results['global'] = {
        'qo': total_qo,
        'chsh': total_chsh,
        'qo_pct': round(global_qo_pct, 1),
        'chsh_pct': round(global_chsh_pct, 1),
        'ratio': round(global_ratio, 2)
    }

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    # Find extremes
    max_qo_section = max(results['sections'].items(), key=lambda x: x[1]['qo_pct'])
    max_chsh_section = max(results['sections'].items(), key=lambda x: x[1]['chsh_pct'])

    print(f"Highest QO%: {max_qo_section[0]} ({max_qo_section[1]['qo_pct']}%)")
    print(f"Highest CHSH%: {max_chsh_section[0]} ({max_chsh_section[1]['chsh_pct']}%)")
    print()

    # Chi-square test for section independence
    from scipy.stats import chi2_contingency
    observed = []
    section_labels = []
    for section in sections:
        qo = section_qo.get(section, 0)
        chsh = section_chsh.get(section, 0)
        if qo + chsh >= 50:  # Only include sections with enough data
            observed.append([qo, chsh])
            section_labels.append(section)

    if len(observed) >= 2:
        chi2, p, dof, expected = chi2_contingency(observed)
        results['chi2'] = round(chi2, 2)
        results['p_value'] = p
        results['significant'] = p < 0.01
        print(f"Chi-square test (section x lane): chi2={chi2:.2f}, p={p:.2e}")
        print(f"Section affects QO:CHSH ratio: {results['significant']}")
    else:
        print("Not enough sections for chi-square test")

    # Save results
    import os
    os.makedirs('C:/git/voynich/phases/QO_CHSH_DIFFERENTIATION/results', exist_ok=True)
    with open('C:/git/voynich/phases/QO_CHSH_DIFFERENTIATION/results/03_section_ratio.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to results/03_section_ratio.json")

if __name__ == '__main__':
    main()
