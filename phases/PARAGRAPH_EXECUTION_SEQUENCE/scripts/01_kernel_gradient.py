#!/usr/bin/env python3
"""
Test 1: Kernel Profile Gradient by Paragraph Ordinal

Question: Do kernel signatures (k%, h%, e%) vary systematically
by paragraph position within folios?

Hypothesis: If procedural sequence exists:
- Early paragraphs: Higher k (energy initialization)
- Middle paragraphs: Higher h (phase management)
- Late paragraphs: Higher e (stabilization)
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

# Path to raw transcript
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

def load_b_tokens_with_paragraphs():
    """Load Currier B tokens with paragraph identification."""
    tokens = []

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        current_para = {}  # folio -> current paragraph number

        for row in reader:
            # Filter to H transcriber only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            # Filter to Currier B (language == 'B')
            language = row.get('language', '').strip()
            if language != 'B':
                continue

            word = row.get('word', '').strip()
            if not word or '*' in word:  # Skip empty or uncertain
                continue

            folio = row.get('folio', '').strip()

            # Track paragraph boundaries using par_initial
            # par_initial has values 1, 2, 3... indicating position in paragraph
            # When it resets to 1, we're in a new paragraph
            par_initial_str = row.get('par_initial', '').strip()
            try:
                par_initial = int(par_initial_str)
            except (ValueError, TypeError):
                par_initial = 0

            # Detect paragraph boundary (par_initial == 1 means start of new paragraph)
            if folio not in current_para:
                current_para[folio] = 1
            elif par_initial == 1:
                current_para[folio] += 1

            tokens.append({
                'word': word,
                'folio': folio,
                'paragraph': current_para[folio]
            })

    return tokens

def compute_kernel_rates(tokens):
    """Compute k, h, e rates for a list of token dicts."""
    if not tokens:
        return {'k': 0, 'h': 0, 'e': 0, 'n': 0}

    k_count = sum(1 for t in tokens if 'k' in t['word'])
    h_count = sum(1 for t in tokens if 'h' in t['word'])
    e_count = sum(1 for t in tokens if 'e' in t['word'])
    n = len(tokens)

    return {
        'k': k_count / n,
        'h': h_count / n,
        'e': e_count / n,
        'n': n
    }

def main():
    print("=" * 60)
    print("Test 1: Kernel Profile Gradient by Paragraph Ordinal")
    print("=" * 60)

    # Load tokens with paragraph info
    all_tokens = load_b_tokens_with_paragraphs()
    print(f"\nTotal B tokens loaded: {len(all_tokens)}")

    # Collect tokens by folio and paragraph
    folio_paragraphs = defaultdict(lambda: defaultdict(list))

    for token in all_tokens:
        folio = token['folio']
        para = token['paragraph']
        folio_paragraphs[folio][para].append(token)

    print(f"Folios with paragraphs: {len(folio_paragraphs)}")

    # Compute kernel rates per paragraph
    paragraph_data = []

    for folio, paragraphs in folio_paragraphs.items():
        # Get paragraph ordinals (sorted)
        para_ids = sorted(paragraphs.keys())
        n_paras = len(para_ids)

        if n_paras < 2:
            continue  # Need at least 2 paragraphs for gradient

        for ordinal, para_id in enumerate(para_ids, 1):
            tokens = paragraphs[para_id]
            rates = compute_kernel_rates(tokens)

            # Normalized ordinal: 0 = first, 1 = last
            norm_ordinal = (ordinal - 1) / (n_paras - 1) if n_paras > 1 else 0.5

            paragraph_data.append({
                'folio': folio,
                'paragraph': para_id,
                'ordinal': ordinal,
                'norm_ordinal': norm_ordinal,
                'n_paragraphs': n_paras,
                'n_tokens': rates['n'],
                'k_rate': rates['k'],
                'h_rate': rates['h'],
                'e_rate': rates['e']
            })

    print(f"Paragraphs analyzed: {len(paragraph_data)}")

    # Extract arrays for correlation analysis
    norm_ordinals = np.array([p['norm_ordinal'] for p in paragraph_data])
    k_rates = np.array([p['k_rate'] for p in paragraph_data])
    h_rates = np.array([p['h_rate'] for p in paragraph_data])
    e_rates = np.array([p['e_rate'] for p in paragraph_data])

    # Correlation tests
    print("\n" + "-" * 40)
    print("Correlation: Normalized Ordinal vs Kernel Rates")
    print("-" * 40)

    results = {
        'n_folios': len(folio_paragraphs),
        'n_paragraphs': len(paragraph_data),
        'correlations': {},
        'ordinal_bins': {},
        'gradient_tests': {}
    }

    for kernel, rates in [('k', k_rates), ('h', h_rates), ('e', e_rates)]:
        r, p = stats.spearmanr(norm_ordinals, rates)
        results['correlations'][kernel] = {
            'spearman_r': float(r),
            'p_value': float(p),
            'significant': bool(p < 0.05),
            'direction': 'increasing' if r > 0 else 'decreasing'
        }
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {kernel}_rate: rho = {r:+.3f}, p = {p:.4f} {sig}")

    # Bin analysis: early (0-0.33), middle (0.33-0.67), late (0.67-1.0)
    print("\n" + "-" * 40)
    print("Bin Analysis: Early / Middle / Late Paragraphs")
    print("-" * 40)

    bins = {
        'early': [p for p in paragraph_data if p['norm_ordinal'] <= 0.33],
        'middle': [p for p in paragraph_data if 0.33 < p['norm_ordinal'] <= 0.67],
        'late': [p for p in paragraph_data if p['norm_ordinal'] > 0.67]
    }

    print(f"\n  Counts: early={len(bins['early'])}, middle={len(bins['middle'])}, late={len(bins['late'])}")

    for kernel in ['k', 'h', 'e']:
        rate_key = f'{kernel}_rate'
        bin_means = {}
        bin_arrays = {}

        for bin_name, paras in bins.items():
            rates = [p[rate_key] for p in paras]
            bin_means[bin_name] = np.mean(rates) if rates else 0
            bin_arrays[bin_name] = rates

        results['ordinal_bins'][kernel] = {
            'early_mean': float(bin_means['early']),
            'middle_mean': float(bin_means['middle']),
            'late_mean': float(bin_means['late'])
        }

        print(f"\n  {kernel}_rate by bin:")
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
            results['gradient_tests'][kernel] = {
                'kruskal_wallis_h': float(h_stat),
                'p_value': float(kw_p),
                'significant': bool(kw_p < 0.05)
            }
            sig = "***" if kw_p < 0.001 else "**" if kw_p < 0.01 else "*" if kw_p < 0.05 else ""
            print(f"    Kruskal-Wallis: H = {h_stat:.2f}, p = {kw_p:.4f} {sig}")

    # First vs Last paragraph direct comparison
    print("\n" + "-" * 40)
    print("First vs Last Paragraph Comparison")
    print("-" * 40)

    first_paras = [p for p in paragraph_data if p['ordinal'] == 1]
    last_paras = [p for p in paragraph_data if p['ordinal'] == p['n_paragraphs']]

    results['first_vs_last'] = {}

    for kernel in ['k', 'h', 'e']:
        rate_key = f'{kernel}_rate'
        first_rates = [p[rate_key] for p in first_paras]
        last_rates = [p[rate_key] for p in last_paras]

        u_stat, mw_p = stats.mannwhitneyu(first_rates, last_rates, alternative='two-sided')

        results['first_vs_last'][kernel] = {
            'first_mean': float(np.mean(first_rates)),
            'last_mean': float(np.mean(last_rates)),
            'mann_whitney_u': float(u_stat),
            'p_value': float(mw_p),
            'significant': bool(mw_p < 0.05)
        }

        sig = "***" if mw_p < 0.001 else "**" if mw_p < 0.01 else "*" if mw_p < 0.05 else ""
        delta = np.mean(last_rates) - np.mean(first_rates)
        print(f"  {kernel}_rate: first={np.mean(first_rates):.3f}, last={np.mean(last_rates):.3f}, "
              f"delta={delta:+.3f}, p={mw_p:.4f} {sig}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    significant_correlations = sum(1 for k in ['k', 'h', 'e']
                                   if results['correlations'][k]['significant'])
    significant_gradients = sum(1 for k in ['k', 'h', 'e']
                                if results['gradient_tests'].get(k, {}).get('significant', False))
    significant_contrasts = sum(1 for k in ['k', 'h', 'e']
                                if results['first_vs_last'][k]['significant'])

    total_significant = significant_correlations + significant_gradients + significant_contrasts

    results['verdict'] = {
        'significant_correlations': significant_correlations,
        'significant_gradients': significant_gradients,
        'significant_contrasts': significant_contrasts,
        'total_significant': total_significant,
        'max_possible': 9
    }

    if total_significant >= 6:
        verdict = "STRONG"
        interpretation = "Kernel profile varies systematically with paragraph ordinal"
    elif total_significant >= 3:
        verdict = "MODERATE"
        interpretation = "Partial kernel gradient exists"
    elif total_significant >= 1:
        verdict = "WEAK"
        interpretation = "Minimal kernel gradient"
    else:
        verdict = "NULL"
        interpretation = "No kernel gradient - paragraphs are kernel-independent"

    results['verdict']['level'] = verdict
    results['verdict']['interpretation'] = interpretation

    print(f"\n  Significant tests: {total_significant}/9")
    print(f"  Verdict: {verdict}")
    print(f"  Interpretation: {interpretation}")

    # Detailed pattern
    print("\n  Pattern detected:")
    for kernel in ['k', 'h', 'e']:
        corr = results['correlations'][kernel]
        if corr['significant']:
            print(f"    {kernel}: {corr['direction']} with ordinal (rho={corr['spearman_r']:+.3f})")

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / 'kernel_gradient.json'
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

if __name__ == '__main__':
    main()
