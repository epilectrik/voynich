#!/usr/bin/env python3
"""
Test 2: Role Composition Gradient by Paragraph Ordinal

Question: Do role compositions (CC%, EN%, FL%, FQ%, AX%) vary
systematically by paragraph position within folios?

Hypothesis: If procedural sequence exists:
- Early: Higher CC (control setup), higher AX (scaffolding)
- Middle: Higher EN (energy operations)
- Late: Higher FL (flow/completion), higher FQ (error handling)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, RecordAnalyzer

# Role class mapping from BCSC (C583)
ROLE_CLASSES = {
    'CC': {10, 11, 12, 17},  # Core Control
    'EN': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},  # Energy
    'FL': {7, 30, 38, 40},  # Flow
    'FQ': {9, 13, 14, 23},  # Frequent
    'AX': {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}  # Auxiliary
}

def get_token_role(token_class):
    """Map token class to role."""
    if token_class is None:
        return None
    for role, classes in ROLE_CLASSES.items():
        if token_class in classes:
            return role
    return 'UN'  # Unclassified

def compute_role_rates(tokens, analyzer):
    """Compute role rates for a list of tokens."""
    if not tokens:
        return {role: 0.0 for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']}

    role_counts = defaultdict(int)
    total_classified = 0

    for token in tokens:
        # Get class from analyzer if possible
        try:
            word = token.word
            # Simple class lookup - use token's class if available
            token_class = getattr(token, 'token_class', None)
            if token_class:
                role = get_token_role(int(token_class))
            else:
                role = 'UN'
        except:
            role = 'UN'

        role_counts[role] += 1
        if role != 'UN':
            total_classified += 1

    n = len(tokens)
    rates = {}
    for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
        rates[role] = role_counts[role] / n if n > 0 else 0.0

    rates['n'] = n
    rates['classified_rate'] = total_classified / n if n > 0 else 0.0

    return rates

def main():
    print("=" * 60)
    print("Test 2: Role Composition Gradient by Paragraph Ordinal")
    print("=" * 60)

    tx = Transcript()
    analyzer = RecordAnalyzer()

    # Collect tokens by folio and paragraph
    folio_paragraphs = defaultdict(lambda: defaultdict(list))

    for token in tx.currier_b():
        folio = token.folio
        para = token.paragraph
        if para:
            folio_paragraphs[folio][para].append(token)

    print(f"\nFolios with paragraphs: {len(folio_paragraphs)}")

    # Compute role rates per paragraph
    paragraph_data = []

    for folio, paragraphs in folio_paragraphs.items():
        para_ids = sorted(paragraphs.keys())
        n_paras = len(para_ids)

        if n_paras < 2:
            continue

        for ordinal, para_id in enumerate(para_ids, 1):
            tokens = paragraphs[para_id]
            rates = compute_role_rates(tokens, analyzer)

            norm_ordinal = (ordinal - 1) / (n_paras - 1) if n_paras > 1 else 0.5

            entry = {
                'folio': folio,
                'paragraph': para_id,
                'ordinal': ordinal,
                'norm_ordinal': norm_ordinal,
                'n_paragraphs': n_paras,
                'n_tokens': rates['n'],
                'classified_rate': rates['classified_rate']
            }

            for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
                entry[f'{role}_rate'] = rates[role]

            paragraph_data.append(entry)

    print(f"Paragraphs analyzed: {len(paragraph_data)}")

    # Correlation analysis
    norm_ordinals = np.array([p['norm_ordinal'] for p in paragraph_data])

    results = {
        'n_paragraphs': len(paragraph_data),
        'correlations': {},
        'ordinal_bins': {},
        'gradient_tests': {},
        'first_vs_last': {}
    }

    print("\n" + "-" * 40)
    print("Correlation: Normalized Ordinal vs Role Rates")
    print("-" * 40)

    roles = ['CC', 'EN', 'FL', 'FQ', 'AX']

    for role in roles:
        rates = np.array([p[f'{role}_rate'] for p in paragraph_data])
        r, p = stats.spearmanr(norm_ordinals, rates)

        results['correlations'][role] = {
            'spearman_r': float(r),
            'p_value': float(p),
            'significant': p < 0.05,
            'direction': 'increasing' if r > 0 else 'decreasing'
        }

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {role}_rate: rho = {r:+.3f}, p = {p:.4f} {sig}")

    # Bin analysis
    print("\n" + "-" * 40)
    print("Bin Analysis: Early / Middle / Late Paragraphs")
    print("-" * 40)

    bins = {
        'early': [p for p in paragraph_data if p['norm_ordinal'] <= 0.33],
        'middle': [p for p in paragraph_data if 0.33 < p['norm_ordinal'] <= 0.67],
        'late': [p for p in paragraph_data if p['norm_ordinal'] > 0.67]
    }

    print(f"\n  Counts: early={len(bins['early'])}, middle={len(bins['middle'])}, late={len(bins['late'])}")

    for role in roles:
        rate_key = f'{role}_rate'
        bin_arrays = {}
        bin_means = {}

        for bin_name, paras in bins.items():
            rates = [p[rate_key] for p in paras]
            bin_means[bin_name] = np.mean(rates) if rates else 0
            bin_arrays[bin_name] = rates

        results['ordinal_bins'][role] = {
            'early_mean': float(bin_means['early']),
            'middle_mean': float(bin_means['middle']),
            'late_mean': float(bin_means['late'])
        }

        print(f"\n  {role}_rate by bin:")
        print(f"    Early:  {bin_means['early']:.3f}")
        print(f"    Middle: {bin_means['middle']:.3f}")
        print(f"    Late:   {bin_means['late']:.3f}")

        # Kruskal-Wallis test
        if all(len(bin_arrays[b]) > 0 for b in ['early', 'middle', 'late']):
            h_stat, kw_p = stats.kruskal(
                bin_arrays['early'],
                bin_arrays['middle'],
                bin_arrays['late']
            )
            results['gradient_tests'][role] = {
                'kruskal_wallis_h': float(h_stat),
                'p_value': float(kw_p),
                'significant': kw_p < 0.05
            }
            sig = "***" if kw_p < 0.001 else "**" if kw_p < 0.01 else "*" if kw_p < 0.05 else ""
            print(f"    Kruskal-Wallis: H = {h_stat:.2f}, p = {kw_p:.4f} {sig}")

    # First vs Last comparison
    print("\n" + "-" * 40)
    print("First vs Last Paragraph Comparison")
    print("-" * 40)

    first_paras = [p for p in paragraph_data if p['ordinal'] == 1]
    last_paras = [p for p in paragraph_data if p['ordinal'] == p['n_paragraphs']]

    for role in roles:
        rate_key = f'{role}_rate'
        first_rates = [p[rate_key] for p in first_paras]
        last_rates = [p[rate_key] for p in last_paras]

        u_stat, mw_p = stats.mannwhitneyu(first_rates, last_rates, alternative='two-sided')

        results['first_vs_last'][role] = {
            'first_mean': float(np.mean(first_rates)),
            'last_mean': float(np.mean(last_rates)),
            'mann_whitney_u': float(u_stat),
            'p_value': float(mw_p),
            'significant': mw_p < 0.05
        }

        sig = "***" if mw_p < 0.001 else "**" if mw_p < 0.01 else "*" if mw_p < 0.05 else ""
        delta = np.mean(last_rates) - np.mean(first_rates)
        print(f"  {role}_rate: first={np.mean(first_rates):.3f}, last={np.mean(last_rates):.3f}, "
              f"delta={delta:+.3f}, p={mw_p:.4f} {sig}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    significant_correlations = sum(1 for role in roles
                                   if results['correlations'][role]['significant'])
    significant_gradients = sum(1 for role in roles
                                if results['gradient_tests'].get(role, {}).get('significant', False))
    significant_contrasts = sum(1 for role in roles
                                if results['first_vs_last'][role]['significant'])

    total_significant = significant_correlations + significant_gradients + significant_contrasts
    max_possible = len(roles) * 3  # 5 roles × 3 test types

    results['verdict'] = {
        'significant_correlations': significant_correlations,
        'significant_gradients': significant_gradients,
        'significant_contrasts': significant_contrasts,
        'total_significant': total_significant,
        'max_possible': max_possible
    }

    if total_significant >= 9:
        verdict = "STRONG"
        interpretation = "Role composition varies systematically with paragraph ordinal"
    elif total_significant >= 5:
        verdict = "MODERATE"
        interpretation = "Partial role gradient exists"
    elif total_significant >= 2:
        verdict = "WEAK"
        interpretation = "Minimal role gradient"
    else:
        verdict = "NULL"
        interpretation = "No role gradient - paragraphs are role-independent"

    results['verdict']['level'] = verdict
    results['verdict']['interpretation'] = interpretation

    print(f"\n  Significant tests: {total_significant}/{max_possible}")
    print(f"  Verdict: {verdict}")
    print(f"  Interpretation: {interpretation}")

    # Detailed pattern
    print("\n  Pattern detected:")
    for role in roles:
        corr = results['correlations'][role]
        if corr['significant']:
            print(f"    {role}: {corr['direction']} with ordinal (rho={corr['spearman_r']:+.3f})")

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / 'role_gradient.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
