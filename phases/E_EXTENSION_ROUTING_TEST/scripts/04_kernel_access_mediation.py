#!/usr/bin/env python3
"""
E_EXTENSION_ROUTING_TEST - Script 04: Kernel Access Mediation

Test whether e-extension in A vocabulary predicts kernel access patterns
in B (Tier B tests 5-6).

Per C765, AZC-mediated vocabulary has different kernel access than B-native.
Does e-extension correlate with these access patterns?

Also test: when e-heavy A MIDDLEs survive into B, where do they appear
in recovery sequences?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

def count_consecutive_e(s):
    """Count maximum consecutive e's."""
    max_consec = 0
    current = 0
    for c in s:
        if c == 'e':
            current += 1
            max_consec = max(max_consec, current)
        else:
            current = 0
    return max_consec

def main():
    print("=" * 70)
    print("KERNEL ACCESS MEDIATION TEST")
    print("Testing e-extension -> kernel access patterns")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # Build A MIDDLE inventory with e-metrics
    a_middles = defaultdict(lambda: {
        'occurrences': 0,
        'total_e': 0,
        'max_consec_e': 0,
        'folios': set()
    })

    print("\nBuilding A MIDDLE inventory...")
    for token in tx.currier_a():
        m = morph.extract(token.word)
        middle = m.middle if m.middle else ''
        if not middle:
            continue

        a_middles[middle]['occurrences'] += 1
        a_middles[middle]['total_e'] += token.word.count('e')
        a_middles[middle]['max_consec_e'] = max(
            a_middles[middle]['max_consec_e'],
            count_consecutive_e(token.word)
        )
        a_middles[middle]['folios'].add(token.folio)

    # Convert folio sets to counts
    for mid in a_middles:
        a_middles[mid]['n_folios'] = len(a_middles[mid]['folios'])
        a_middles[mid]['mean_e'] = a_middles[mid]['total_e'] / a_middles[mid]['occurrences']
        del a_middles[mid]['folios']

    # Build B MIDDLE inventory with kernel metrics
    b_middles = defaultdict(lambda: {
        'occurrences': 0,
        'kernel_tokens': 0,  # tokens containing k, h, or e
        'e_tokens': 0,
        'k_tokens': 0,
        'h_tokens': 0,
        'positions': [],  # line position (0=start, 1=end)
        'folios': set()
    })

    print("Building B MIDDLE inventory...")
    for token in tx.currier_b():
        m = morph.extract(token.word)
        middle = m.middle if m.middle else ''
        if not middle:
            continue

        b_middles[middle]['occurrences'] += 1
        b_middles[middle]['folios'].add(token.folio)

        # Kernel content
        word = token.word
        if any(c in word for c in ['e', 'k', 'h']):
            b_middles[middle]['kernel_tokens'] += 1
        if 'e' in word:
            b_middles[middle]['e_tokens'] += 1
        if 'k' in word:
            b_middles[middle]['k_tokens'] += 1
        if 'h' in word:
            b_middles[middle]['h_tokens'] += 1

        # Position in line
        try:
            pos = int(token.line_initial)
            final = int(token.line_final)
            total = pos + final - 1
            if total > 0:
                rel_pos = (pos - 1) / total
                b_middles[middle]['positions'].append(rel_pos)
        except (ValueError, TypeError):
            pass

    # Compute derived metrics for B
    for mid in b_middles:
        n = b_middles[mid]['occurrences']
        b_middles[mid]['n_folios'] = len(b_middles[mid]['folios'])
        b_middles[mid]['kernel_rate'] = b_middles[mid]['kernel_tokens'] / n if n > 0 else 0
        b_middles[mid]['e_rate'] = b_middles[mid]['e_tokens'] / n if n > 0 else 0
        b_middles[mid]['k_rate'] = b_middles[mid]['k_tokens'] / n if n > 0 else 0
        b_middles[mid]['h_rate'] = b_middles[mid]['h_tokens'] / n if n > 0 else 0
        b_middles[mid]['mean_position'] = np.mean(b_middles[mid]['positions']) if b_middles[mid]['positions'] else 0.5
        del b_middles[mid]['folios']
        del b_middles[mid]['positions']

    # Find shared MIDDLEs
    shared_middles = set(a_middles.keys()) & set(b_middles.keys())
    a_only = set(a_middles.keys()) - set(b_middles.keys())
    b_only = set(b_middles.keys()) - set(a_middles.keys())

    print(f"\nMIDDLE Overlap:")
    print(f"  Shared (A & B): {len(shared_middles)}")
    print(f"  A-only: {len(a_only)}")
    print(f"  B-only: {len(b_only)}")

    results = {
        'middle_overlap': {
            'shared': len(shared_middles),
            'a_only': len(a_only),
            'b_only': len(b_only)
        },
        'test_5_e_extension_kernel_access': {},
        'test_6_e_extension_position': {},
        'survival_analysis': {},
        'summary': {}
    }

    # ===========================================
    # TEST 5: A e-extension -> B kernel access
    # ===========================================
    print("\n" + "-" * 50)
    print("TEST 5: A e-extension -> B kernel access")
    print("-" * 50)

    # For shared MIDDLEs, correlate A's e-extension with B's kernel rate
    a_max_consec = []
    b_kernel_rates = []
    b_e_rates = []

    for mid in shared_middles:
        a_max_consec.append(a_middles[mid]['max_consec_e'])
        b_kernel_rates.append(b_middles[mid]['kernel_rate'])
        b_e_rates.append(b_middles[mid]['e_rate'])

    if len(a_max_consec) > 10:
        # A e-extension -> B kernel rate
        rho_kernel, p_kernel = stats.spearmanr(a_max_consec, b_kernel_rates)

        # A e-extension -> B e-rate specifically
        rho_e, p_e = stats.spearmanr(a_max_consec, b_e_rates)

        results['test_5_e_extension_kernel_access'] = {
            'n_shared_middles': len(shared_middles),
            'a_e_vs_b_kernel': {
                'spearman_rho': round(rho_kernel, 4),
                'p_value': round(p_kernel, 6),
                'significant': p_kernel < 0.05
            },
            'a_e_vs_b_e': {
                'spearman_rho': round(rho_e, 4),
                'p_value': round(p_e, 6),
                'significant': p_e < 0.05
            }
        }

        print(f"\nShared MIDDLEs analyzed: {len(shared_middles)}")
        print(f"\nA e-extension -> B kernel access rate:")
        print(f"  Spearman rho: {rho_kernel:.4f}")
        print(f"  p-value: {p_kernel:.6f}")
        print(f"  Significant: {p_kernel < 0.05}")

        print(f"\nA e-extension -> B e-character rate:")
        print(f"  Spearman rho: {rho_e:.4f}")
        print(f"  p-value: {p_e:.6f}")
        print(f"  Significant: {p_e < 0.05}")

        if p_e < 0.05 and rho_e > 0:
            print(f"  ** E-heavy A MIDDLEs have higher e-rate in B! **")
        elif p_e < 0.05 and rho_e < 0:
            print(f"  ** E-heavy A MIDDLEs have LOWER e-rate in B! **")

    # ===========================================
    # TEST 6: A e-extension -> B position
    # ===========================================
    print("\n" + "-" * 50)
    print("TEST 6: A e-extension -> B line position")
    print("-" * 50)

    # Do e-heavy MIDDLEs appear earlier/later in lines?
    b_positions = []
    for mid in shared_middles:
        a_max_consec_val = a_middles[mid]['max_consec_e']
        b_pos = b_middles[mid]['mean_position']
        a_max_consec.append(a_max_consec_val)
        b_positions.append(b_pos)

    # Rebuild lists (they got reused above)
    a_max_consec = [a_middles[mid]['max_consec_e'] for mid in shared_middles]
    b_positions = [b_middles[mid]['mean_position'] for mid in shared_middles]

    if len(a_max_consec) > 10:
        rho_pos, p_pos = stats.spearmanr(a_max_consec, b_positions)

        results['test_6_e_extension_position'] = {
            'spearman_rho': round(rho_pos, 4),
            'p_value': round(p_pos, 6),
            'significant': p_pos < 0.05,
            'direction': 'later' if rho_pos > 0 else 'earlier'
        }

        print(f"\nA e-extension -> B mean line position:")
        print(f"  Spearman rho: {rho_pos:.4f}")
        print(f"  p-value: {p_pos:.6f}")
        print(f"  Significant: {p_pos < 0.05}")

        if p_pos < 0.05:
            direction = "LATER (toward line end)" if rho_pos > 0 else "EARLIER (toward line start)"
            print(f"  ** E-heavy MIDDLEs appear {direction} in B lines **")
            print(f"  (Per C105, e is late in recovery - this {'aligns' if rho_pos > 0 else 'contradicts'})")

    # ===========================================
    # SURVIVAL ANALYSIS: Do high-e MIDDLEs survive?
    # ===========================================
    print("\n" + "-" * 50)
    print("SURVIVAL ANALYSIS: High-e MIDDLE propagation")
    print("-" * 50)

    # Compare survival rates by e-extension
    low_e_a = [m for m in a_middles if a_middles[m]['max_consec_e'] <= 1]
    mid_e_a = [m for m in a_middles if a_middles[m]['max_consec_e'] == 2]
    high_e_a = [m for m in a_middles if a_middles[m]['max_consec_e'] >= 3]

    low_e_survival = len([m for m in low_e_a if m in b_middles]) / len(low_e_a) if low_e_a else 0
    mid_e_survival = len([m for m in mid_e_a if m in b_middles]) / len(mid_e_a) if mid_e_a else 0
    high_e_survival = len([m for m in high_e_a if m in b_middles]) / len(high_e_a) if high_e_a else 0

    results['survival_analysis'] = {
        'low_e_count': len(low_e_a),
        'low_e_survival': round(low_e_survival, 4),
        'mid_e_count': len(mid_e_a),
        'mid_e_survival': round(mid_e_survival, 4),
        'high_e_count': len(high_e_a),
        'high_e_survival': round(high_e_survival, 4)
    }

    print(f"\nSurvival rate by A e-extension:")
    print(f"  Low (<=1 consec e): {len(low_e_a)} MIDDLEs, {low_e_survival:.1%} survive to B")
    print(f"  Mid (2 consec e):  {len(mid_e_a)} MIDDLEs, {mid_e_survival:.1%} survive to B")
    print(f"  High (>=3 consec e): {len(high_e_a)} MIDDLEs, {high_e_survival:.1%} survive to B")

    # Chi-square test for survival independence
    if high_e_a and low_e_a:
        # Contingency table: [survives, doesn't survive] x [low_e, high_e]
        low_survives = len([m for m in low_e_a if m in b_middles])
        low_dies = len(low_e_a) - low_survives
        high_survives = len([m for m in high_e_a if m in b_middles])
        high_dies = len(high_e_a) - high_survives

        contingency = [[low_survives, low_dies], [high_survives, high_dies]]

        if min(low_survives, low_dies, high_survives, high_dies) >= 5:
            chi2, p, dof, expected = stats.chi2_contingency(contingency)
            results['survival_analysis']['chi2_low_vs_high'] = {
                'chi2': round(chi2, 4),
                'p_value': round(p, 6),
                'significant': bool(p < 0.05)
            }

            print(f"\n  Chi-square (low vs high e survival): chi2={chi2:.4f}, p={p:.6f}")
            if p < 0.05:
                if high_e_survival > low_e_survival:
                    print(f"  ** High-e MIDDLEs survive MORE than low-e **")
                else:
                    print(f"  ** High-e MIDDLEs survive LESS than low-e **")

    # ===========================================
    # SUMMARY
    # ===========================================
    print("\n" + "=" * 70)
    print("TIER B TESTS 5-6 SUMMARY")
    print("=" * 70)

    test5_sig = results['test_5_e_extension_kernel_access'].get('a_e_vs_b_e', {}).get('significant', False)
    test6_sig = results['test_6_e_extension_position'].get('significant', False)
    survival_sig = results['survival_analysis'].get('chi2_low_vs_high', {}).get('significant', False)

    any_significant = test5_sig or test6_sig or survival_sig

    if any_significant:
        verdict = "MEDIATED EFFECTS FOUND - e-extension has indirect B consequences"
        findings = []
        if test5_sig:
            findings.append("A e-extension correlates with B e-rate")
        if test6_sig:
            findings.append("A e-extension correlates with B position")
        if survival_sig:
            findings.append("E-extension affects MIDDLE survival rate")
        verdict += f": {'; '.join(findings)}"
    else:
        verdict = "NO MEDIATED EFFECTS - e-extension doesn't predict B behavior through these paths"

    results['summary'] = {
        'test_5_significant': test5_sig,
        'test_6_significant': test6_sig,
        'survival_significant': survival_sig,
        'any_significant': any_significant,
        'verdict': verdict
    }

    print(f"\n  Test 5 (e -> kernel access) significant: {test5_sig}")
    print(f"  Test 6 (e -> position) significant: {test6_sig}")
    print(f"  Survival rate significant: {survival_sig}")
    print(f"\n  VERDICT: {verdict}")

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / '04_kernel_access_mediation.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
